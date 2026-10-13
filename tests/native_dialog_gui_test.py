#!/usr/bin/env python3
"""Exercise graphical native decisions, held-key safety and paid-work feedback in the actual Luanti renderer.

Requires an independently created --create-medicine fixture, X11, xdotool,
ImageMagick and Pillow. Never opens an existing user world.
"""
import argparse
import csv
import json
import math
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import time
import select
import tempfile
import threading
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('workspace', 'fixture', 'native-reader', 'artifacts'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--action-driven', action='store_true', help='Verify ordinary start.sh mode without the real-time scheduler')
    parser.add_argument('--resume-only', action='store_true')
    parser.add_argument('--save-active', action='store_true')
    parser.add_argument('--resume-active', action='store_true')
    args = parser.parse_args()
    if args.resume_active: args.resume_only = True
    ws, out = args.workspace.resolve(), args.artifacts.resolve()
    out.mkdir(parents=True, exist_ok=False)
    user = out / 'user'
    shutil.copytree(args.fixture.resolve(), user)
    (user / 'config/options.json').write_text(json.dumps([
        {'name': 'SAFEMODE', 'value': 'false'}, {'name': 'AUTOSAFEMODE', 'value': 'false'},
        {'name': 'AUTOSAVE', 'value': 'false'}]))
    checks = {}
    def check(name, ok):
        checks[name] = bool(ok)
        (out / 'checks.json').write_text(json.dumps(checks, indent=2) + '\n')
        print(name, 'PASS' if ok else 'FAIL', flush=True)
        if not ok:
            raise AssertionError(name)

    old_window = subprocess.run(['xdotool', 'getactivewindow'], capture_output=True, text=True).stdout.strip()
    folder = out
    trace = out / 'camera.csv'
    with socket.socket() as temporary:
        temporary.bind(('127.0.0.1', 0))
        port = temporary.getsockname()[1]
    config = out / 'client.conf'
    config.write_text('screen_w = 1280\nscreen_h = 800\nfullscreen = false\nfps_max = 60\n'
                      'vsync = false\nenable_clouds = false\ngui_scaling = 1\n'
                      f'port = {port}\ncwm_trace_file = {trace}\n')
    env = dict(os.environ, CDDA_USERDIR=str(user), CDDA_WORLD='audit_fixture',
               LUANTI_WORLD=str(out / 'luanti'), LUANTI_CONFIG=str(config),
               LOG_DIR=str(out / 'logs'), CDDA_BIN=str(ws / 'cdda/build/src/cdda-server'),
               LUANTI_BIN=str(ws / 'luanti/bin/luanti'), CDDA_CONTINUOUS='1')
    env.pop('CDDA_TERRAIN_DEMO', None)
    if args.action_driven:
        env['CDDA_CONTINUOUS'] = '0'
        env.pop('CDDA_REALTIME', None)
    # A byte-transparent local relay lets the real client lose IPC while a
    # selection is queued under manual pause. Gameplay still runs in CDDA.
    scratch = tempfile.TemporaryDirectory(prefix='cwm-body-gui-')
    relay_path = Path(scratch.name) / 'relay.sock'
    native_path = out / 'native-socket'
    stop, drop = threading.Event(), threading.Event()
    shutting_down = threading.Event()
    expected_shutdown_errors = []
    relay_errors = []
    listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    listener.bind(str(relay_path)); listener.listen(1); listener.settimeout(.1)
    def relay():
        try:
            while not stop.is_set():
                try:
                    client_socket, _ = listener.accept()
                except socket.timeout:
                    continue
                with client_socket, socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server_socket:
                    server_socket.connect(native_path.read_text().strip())
                    while not stop.is_set():
                        if drop.is_set():
                            drop.clear()
                            break
                        readable, _, _ = select.select([client_socket, server_socket], [], [], .03)
                        closed = False
                        for source in readable:
                            data = source.recv(1 << 20)
                            if not data:
                                closed = True
                                break
                            with (out / ('client-wire.bin' if source is client_socket else 'server-wire.bin')).open('ab') as capture:
                                capture.write(data)
                            (server_socket if source is client_socket else client_socket).sendall(data)
                        if closed:
                            break
        except (ConnectionResetError, BrokenPipeError) as error:
            if shutting_down.is_set(): expected_shutdown_errors.append(str(error))
            else: relay_errors.append(str(error))
        except Exception as error:
            if not stop.is_set(): relay_errors.append(str(error))
    relay_thread = threading.Thread(target=relay, daemon=True)
    relay_thread.start()
    wrapper = out / 'client-relay.py'
    wrapper.write_text("#!/usr/bin/env python3\nimport os,sys,re\nfrom pathlib import Path\n" +
        "args=sys.argv[1:]\ni=args.index('--config')+1\np=Path(args[i])\ns=p.read_text()\n" +
        f"Path({str(native_path)!r}).write_text(re.findall(r'^cwm_socket_path = (.+)$',s,re.M)[-1])\n" +
        f"p=Path({str(out / 'relay-client.conf')!r})\n" +
        f"p.write_text(s+'\\ncwm_socket_path = {relay_path}\\n')\nargs[i]=str(p)\n" +
        f"os.execv({str(ws / 'luanti/bin/luanti')!r},[{str(ws / 'luanti/bin/luanti')!r},*args])\n")
    wrapper.chmod(0o755)
    env['LUANTI_BIN'] = str(wrapper)
    def rows():
        if not trace.exists():
            return []
        with trace.open() as stream:
            return [r for r in csv.DictReader(stream) if r.get('scene_origin_y') is not None]
    def latest():
        return rows()[-1]
    def wait(predicate, timeout=12):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline and proc.poll() is None:
            data = rows()
            if data and predicate(data[-1]):
                return data[-1]
            time.sleep(.05)
        raise RuntimeError('GUI condition not reached; inspect trace/logs')
    def xdo(*argv):
        if os.environ.get('CWM_GUI_NO_WM') == '1' and argv[0] == 'windowactivate':
            argv = ('windowfocus', *argv[1:])
        subprocess.run(['xdotool', *argv], check=True, capture_output=True, timeout=5)
    def tap(key, sneak=False):
        if sneak:
            xdo('keydown', 'Shift_L')
            time.sleep(.12)
        xdo('keydown', '--window', window, key)
        time.sleep(.12)
        xdo('keyup', '--window', window, key)
        if sneak:
            time.sleep(.12)
            xdo('keyup', 'Shift_L')
        time.sleep(.3)
    def shot(name):
        time.sleep(.6)  # Allow actual asynchronous mesh installation.
        subprocess.run(['import', '-window', window, str(folder / name)], check=True, timeout=10)
    def turn(yaw_target, pitch_target=0):
        for _ in range(25):
            r = latest()
            yaw = math.degrees(math.atan2(-float(r['dir_x']), float(r['dir_z'])))
            pitch = math.degrees(math.asin(max(-1, min(1, float(r['dir_y'])))))
            dyaw = (yaw_target - yaw + 180) % 360 - 180
            dpitch = pitch_target - pitch
            if max(abs(dyaw), abs(dpitch)) < 1:
                break
            xdo('mousemove_relative', '--', str(max(-130, min(130, round(-dyaw / .2)))),
                str(max(-130, min(130, round(-dpitch / .2)))))
            time.sleep(.12)
        time.sleep(.4)
    window = None
    with (out / 'launcher.log').open('w') as log:
        proc = subprocess.Popen([str(ws / 'start.sh'), '--go', '--name', 'body_tester', '--port', str(port), '--info'],
                                env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            deadline = time.monotonic() + 85
            while time.monotonic() < deadline and proc.poll() is None:
                descendants = [proc.pid]
                for pid in descendants:
                    try:
                        descendants.extend(map(int, Path(f'/proc/{pid}/task/{pid}/children').read_text().split()))
                        if Path(f'/proc/{pid}/comm').read_text().strip() != 'luanti':
                            continue
                    except (FileNotFoundError, ProcessLookupError):
                        continue
                    found = subprocess.run(['xdotool', 'search', '--onlyvisible', '--pid', str(pid)], capture_output=True, text=True)
                    if found.stdout.strip():
                        window = found.stdout.splitlines()[0]
                if window and len(rows()) > 20:
                    break
                time.sleep(.2)
            check('actual_start_ready', bool(window) and len(rows()) > 20)
            xdo('windowactivate', '--sync', window)
            time.sleep(1)
            wait(lambda r: int(r['input_ready']) == 1 and int(r['pause_reasons']) == 0)
            sys.path.insert(0, str(ws / 'protocol/python'))
            from CDDA.CWM.CwmMessage import CwmMessage
            from CDDA.CWM.Payload import Payload
            from CDDA.CWM.InventoryView import InventoryView
            def views():
                import struct
                buf = (out / 'server-wire.bin').read_bytes(); offset = 0; found = []
                while offset + 4 <= len(buf):
                    n = struct.unpack('>I', buf[offset:offset+4])[0]; offset += 4
                    if offset+n > len(buf): break
                    msg = CwmMessage.GetRootAs(buf[offset:offset+n]); offset += n
                    if msg.PayloadType() == Payload.InventoryView:
                        v = InventoryView(); v.Init(msg.Payload().Bytes,msg.Payload().Pos)
                        if v.ViewId(): found.append(v)
                return found
            def cancel_choice():
                import struct
                from CDDA.CWM.DecisionPrompt import DecisionPrompt
                buf = (out / 'server-wire.bin').read_bytes(); offset = 0; options = []
                while offset + 4 <= len(buf):
                    n = struct.unpack('>I',buf[offset:offset+4])[0]; offset += 4
                    if offset + n > len(buf): break
                    msg = CwmMessage.GetRootAs(buf[offset:offset+n]); offset += n
                    if msg.PayloadType() == Payload.DecisionPrompt:
                        prompt = DecisionPrompt();prompt.Init(msg.Payload().Bytes,msg.Payload().Pos)
                        options = [prompt.Choices(i).decode() for i in range(prompt.ChoicesLength())]
                assert options and options[-1] in ('Cancel','No') and len(options) <= 9, options
                return str(len(options))
            def open_inventory():
                if int(latest().get('inventory_return',0)) and int(latest()['first_aid_token'])==0:
                    wait(lambda r:int(r['equipment_form'])==1 and int(r['inventory_view'])>0)
                elif int(latest()['equipment_form'])==1 and int(latest()['inventory_view'])==0:
                    wait(lambda r:int(r['inventory_view'])>0)
                if int(latest()['equipment_form']) == 1 and int(latest()['inventory_view']) > 0:
                    return views()[-1]
                tap('i')
                wait(lambda r: int(r['equipment_form']) == 1 and int(r['inventory_view']) > 0)
                return views()[-1]
            view = open_inventory()
            check('native_inventory_opened', True)
            shot('inventory.png')
            from PIL import Image
            width, height = Image.open(out / 'inventory.png').size
            from formspec_geometry import geometry
            origin_x, origin_y, unit = geometry(out / 'inventory.png')
            def click(x, y):
                xdo('mousemove','--window',window,str(round(origin_x+x*unit)),str(round(origin_y+y*unit)))
                xdo('click','1'); time.sleep(.3)
            def entries(v):
                return [v.Entries(n) for n in range(v.EntriesLength())]
            def select_item(e):
                index = e.Id() - 1
                click(1.025 + (index % 9)*1.15, 5.975 + ((index % 27) // 9)*1.15)
                wait(lambda r: int(r['equipment_selected']) == e.Id())
            def action(number):
                sent = int(latest()['equipment_sent'])
                click(12.325 + (number % 2)*2.2, 8.15 + (number // 2)*.75)
                wait(lambda r: int(r['equipment_sent']) == sent+1)
                wait(lambda r: int(r['equipment_form']) == 0)
            def finish_action():
                wait(lambda r: int(r['pending_move']) == 0 and (int(r['pause_reasons']) == 0 or (int(r['equipment_form']) == 1 and int(r['native_work_settled']) == 1)))
            def item(v, name):
                return next(e for e in entries(v) if e.TypeId().decode() == name)
            def food(v):
                return next(e for e in entries(v) if e.TypeId() == b'apple' and not e.ConsumeWarning())
            def rotten(v):
                return next(e for e in entries(v) if e.TypeId() == b'apple' and e.ConsumeWarning())
            def prompts():
                import struct
                from CDDA.CWM.DecisionPrompt import DecisionPrompt
                buf = (out / 'server-wire.bin').read_bytes(); offset = 0; found = []
                while offset + 4 <= len(buf):
                    n = struct.unpack('>I',buf[offset:offset+4])[0];offset += 4
                    if offset+n>len(buf):break
                    message = CwmMessage.GetRootAs(buf[offset:offset+n]);offset += n
                    if message.PayloadType()==Payload.DecisionPrompt:
                        prompt=DecisionPrompt();prompt.Init(message.Payload().Bytes,message.Payload().Pos)
                        found.append((prompt.DecisionId(),prompt.Text().decode(),[prompt.Choices(i).decode() for i in range(prompt.ChoicesLength())],prompt))
                return found
            def bandages(v):return [e for e in entries(v) if e.TypeId()==b'bandages']
            def ready_inventory():
                wait(lambda r:int(r['pending_move'])==0 and int(r['equipment_form'])==1 and int(r['inventory_view'])>0,timeout=25)
                time.sleep(.55);return views()[-1]
            def begin(v):
                select_item(bandages(v)[0]);action(5);wait(lambda r:int(r['pending_decision'])>0)
                time.sleep(.3);return prompts()[-1]
            def dialog_click(index,name='dialog-click.png'):
                shot(name)
                dx,dy,du=geometry(out/name,16,12)
                xdo('windowactivate','--sync',window)
                xdo('mousemove','--window',window,str(round(dx+(3.2 if prompts()[-1][3].MedicalLength() else 7)*du)),str(round(dy+((3.1+next(n for n in range(prompts()[-1][3].MedicalLength()) if prompts()[-1][3].Medical(n).Choice()==index)*2.8+.35) if prompts()[-1][3].MedicalLength() else (6+index*.85+.36))*du)))
                xdo('click','1');time.sleep(.3)
            check('fixture_supplies_three_native_bandages',len(bandages(view))==3)
            xdo('keydown','1')
            first=begin(view);shot('native-body-choices.png')
            typed=first[3];parts=[typed.Medical(n) for n in range(typed.MedicalLength())]
            check('typed_medical_disclosure_has_stable_body_ids_and_no_exact_self_hp',len(parts)==6 and len({p.BodyId() for p in parts})==6 and all(p.HpCurrent()==-1 and p.HpMax()==-1 for p in parts))
            check('native_wounded_parts_selectable_healthy_parts_readonly',any(p.BodyId()==b'arm_l' and p.Choice()>=0 and 0<=p.HealthQuarters()<=20 for p in parts) and any(p.Choice()==-1 for p in parts))
            check('native_descriptions_preserve_known_effects',all(p.Description() for p in parts))
            identifier=first[0];stopped=latest()['simulation_time'];position=tuple(latest()[k] for k in ('target_x','target_y','target_z'))
            xdo('keydown','1');time.sleep(.6)
            check('number_held_before_dialog_does_not_choose',int(latest()['pending_decision'])==identifier and int(latest()['decision_waiting'])==0)
            tap('Return');xdo('keydown','w');time.sleep(.6);xdo('keyup','w')
            check('enter_does_not_approve_and_menu_keeps_time_position_frozen',int(latest()['pending_decision'])==identifier and latest()['simulation_time']==stopped and tuple(latest()[k] for k in ('target_x','target_y','target_z'))==position)
            xdo('keyup','1');xdo('keydown','1')
            wait(lambda r:int(r['pending_decision'])>0 and int(r['pending_decision'])!=identifier)
            second=prompts()[-1];identifier=second[0]
            xdo('keydown','1');time.sleep(.65)
            check('held_answer_never_confirms_the_next_native_question',int(latest()['pending_decision'])==identifier and int(latest()['first_aid_token'])==0)
            xdo('keyup','1');dialog_click(1,'native-confirmation.png');view=ready_inventory()
            check('mouse_decline_preserves_all_bandages_and_returns_inventory',len(bandages(view))==3 and int(latest()['first_aid_token'])==0)
            first=begin(view);tap('Escape');view=ready_inventory()
            check('escape_uses_native_body_chooser_cancel',len(bandages(view))==3 and int(latest()['first_aid_token'])==0)
            first=begin(view);identifier=first[0];dialog_click(0,'mouse-body-choice.png')
            wait(lambda r:int(r['pending_decision'])>0 and int(r['pending_decision'])!=identifier)
            tap('Escape');view=ready_inventory()
            check('escape_declines_native_confirmation_without_treatment',len(bandages(view))==3 and int(latest()['first_aid_token'])==0)
            first=begin(view);identifier=first[0];tap('1')
            wait(lambda r:int(r['pending_decision'])>0 and int(r['pending_decision'])!=identifier)
            dialog_click(0,'approve-native-confirmation.png')
            wait(lambda r:int(r['first_aid_token'])>0)
            check('explicit_mouse_approval_starts_native_firstaid',int(latest()['first_aid_total'])>0)
            shot('work-progress.png');tap('i')
            view=ready_inventory();remaining=latest()['first_aid_remaining'];stopped=latest()['simulation_time'];time.sleep(.6)
            check('inspection_pauses_work_without_consuming_bandage',latest()['first_aid_remaining']==remaining and latest()['simulation_time']==stopped and len(bandages(view))==3)
            shot('inspection-paused.png');tap('Escape')
            wait(lambda r:int(r['equipment_form'])==0)
            wait(lambda r:int(r['first_aid_token'])==0 and int(r['pending_move'])==0,timeout=35)
            # Manual inspection dismisses the automatic return, but not the actor.
            view=open_inventory();check('closing_inspection_resumes_and_consumes_exactly_one_bandage',len(bandages(view))==2)
            tap('Escape');wait(lambda r:int(r['equipment_form'])==0)
            view=open_inventory();first=begin(view);connection=latest()['connection_id'];drop.set()
            wait(lambda r:r['connection_id']!=connection and int(r['input_ready'])==1 and int(r['pending_decision'])==0,timeout=25)
            view=open_inventory();check('lost_peer_cancels_native_choice_without_approval_or_replay',len(bandages(view))==2 and int(latest()['first_aid_token'])==0)
            tap('Escape');check('actual_runtime_survives_native_dialogs',proc.poll() is None)
        finally:
            shutting_down.set() # Resets caused by our SIGTERM are expected only after this boundary.
            subprocess.run(['xdotool', 'keyup', 'w'], capture_output=True)
            stop.set()
            if proc.poll() is None:
                os.killpg(proc.pid, signal.SIGTERM)
                try:
                    proc.wait(timeout=45)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait()
            stop.set()
            relay_thread.join(timeout=3)
            listener.close()
            (out / 'relay-errors.json').write_text(json.dumps(relay_errors))
            (out / 'expected-shutdown-errors.json').write_text(json.dumps(expected_shutdown_errors))
            scratch.cleanup()
            if old_window:
                subprocess.run(['xdotool', 'windowactivate', old_window], capture_output=True)
    check('byte_relay_completed_without_errors', not relay_errors)
    output = out / 'native.json'
    with (out / 'native.log').open('w') as log:
        result = subprocess.run([str(args.native_reader.resolve()), '--userdir', str(user),
            '--datadir', str(ws / 'cdda/data'), '--output', str(output)], stdout=log, stderr=subprocess.STDOUT, timeout=180)
    check('medicine_save_readable_by_pristine_native_core', result.returncode == 0)
    native = json.loads(output.read_text())
    before = json.loads((args.fixture.parent / ('native.json' if args.resume_only else 'before.json')).read_text())
    def items(value):
        found=[]
        if isinstance(value,dict):
            if value.get('item_vars',{}).get('uid','').startswith('medicine-'):found.append(value)
            for child in value.values():found.extend(items(child))
        elif isinstance(value,list):
            for child in value:found.extend(items(child))
        return found
    saved=items(native['player']);counts={}
    for e in saved:
        uid=e['item_vars']['uid'];counts[uid]=counts.get(uid,0)+1
    check('canonical_medicine_items_never_duplicated',bool(saved) and all(n==1 for n in counts.values()))
    check('canonical_consumed_bandage_count',sum(e['typeid']=='bandages' for e in saved)==(1 if args.resume_active else 2))
    check('canonical_dirty_bandage_never_used','medicine-dirty' in counts)
    check('canonical_unused_wipe_preserved','medicine-wipe' in counts)
    check('canonical_position_unchanged_by_treatment',native['player_abs']==before['player_abs'])
    effects=native['player']['effects']
    check('canonical_bandaging_applied_to_exactly_one_native_body_part',len(effects.get('bandaged',{}))==1)
    check('canonical_dialog_reading_did_not_disinfect','disinfected' not in effects)
    (out/'summary.json').write_text(json.dumps(dict(checks=checks,native_save=str(output)),indent=2)+'\n')

if __name__=='__main__':main()
