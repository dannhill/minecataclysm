#!/usr/bin/env python3
"""Exercise the native quantities, drop and container transfer in the actual Luanti renderer.

Requires an independently created --create-transfer fixture, X11, xdotool,
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
    args = parser.parse_args()
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
        env.pop('CDDA_CONTINUOUS', None)
        env.pop('CDDA_REALTIME', None)
    # A byte-transparent local relay lets the real client lose IPC while a
    # selection is queued under manual pause. Gameplay still runs in CDDA.
    scratch = tempfile.TemporaryDirectory(prefix='cwm-body-gui-')
    relay_path = Path(scratch.name) / 'relay.sock'
    native_path = out / 'native-socket'
    stop, drop = threading.Event(), threading.Event()
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
            time.sleep(.1 if args.resume_only else 1)
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
                assert options and options[-1] == 'Cancel' and len(options) <= 9, options
                return str(len(options))
            def open_inventory():
                if int(latest()['equipment_form']) == 1 and int(latest()['inventory_view']) > 0:
                    return views()[-1]
                tap('i')
                wait(lambda r: int(r['equipment_form']) == 1 and int(r['inventory_view']) > 0)
                return views()[-1]
            view = open_inventory()
            shot('inventory.png')
            from PIL import Image
            width, height = Image.open(out / 'inventory.png').size
            from formspec_geometry import geometry
            origin_x, origin_y, unit = geometry(out / 'inventory.png')
            def click(x, y):
                xdo('mousemove','--window',window,str(round(origin_x+x*unit)),str(round(origin_y+y*unit)))
                xdo('click','1'); time.sleep(.18)
            def entries(v): return [v.Entries(n) for n in range(v.EntriesLength())]
            def item(v, name, parent=None):
                return next(e for e in entries(v) if e.TypeId().decode() == name and (parent is None or e.ParentId() == parent))
            def transfer_panel():
                click(13.5,.5);wait(lambda r:int(r['transfer_form'])==1)
            def select_item(e):
                index=e.Id()-1
                click(1.025+(index%6)*1.18,3.2+(index//6)*1.0)
                wait(lambda r:int(r['equipment_selected'])==e.Id())
            def destination(v,e):
                containers=[x for x in entries(v) if x.Container()]
                index=next(n for n,x in enumerate(containers) if x.Id()==e.Id())
                assert index<12
                click(11.75,2.8+index*.42)
            def quantity(value):
                click(1.2,9.97);xdo('key','ctrl+a');xdo('type','--clearmodifiers',str(value));time.sleep(.15)
            def action(insert):
                sent=int(latest()['transfers_sent'])
                click(11.75 if insert else 4.65,9.97)
                wait(lambda r:int(r['transfers_sent'])==sent+1)
                tap('Escape')  # Opt out of return for this explicit-I mechanism suite.
                wait(lambda r:int(r['equipment_form'])==0)
            def finish():wait(lambda r:int(r['pending_move'])==0 and int(r['transfer_token'])==0,timeout=20)
            if args.resume_only:
                wait(lambda r:int(r['transfer_token'])>0)
                check('saved_native_insert_resumes_without_new_request',int(latest()['transfers_sent'])==0)
                before_work=int(latest()['transfer_remaining']);time.sleep(.8)
                check('resumed_transfer_pauses_in_inventory',int(latest()['transfer_remaining'])==before_work)
                tap('Escape');finish();view=open_inventory();bag=item(view,'bag_plastic')
                check('saved_insert_completes_once_in_actual_renderer',item(view,'9mm',bag.Id()).Charges()==7)
                check('saved_insert_leaves_exact_remainder',sum(e.Charges() for e in entries(view) if e.TypeId().decode()=='9mm' and e.ParentId()!=bag.Id())==23)
                tap('Escape')
            else:
                check('fixture_supplies_native_ammo_and_container',item(view,'9mm').Charges()==30 and bool(item(view,'bag_plastic').ParentId()))
                stopped=latest()['simulation_time'];position=tuple(latest()[k] for k in ('target_x','target_y','target_z'))
                xdo('keydown','w');time.sleep(.6);xdo('keyup','w')
                check('reading_and_movement_in_menu_change_no_time_or_position',latest()['simulation_time']==stopped and tuple(latest()[k] for k in ('target_x','target_y','target_z'))==position)
                transfer_panel();select_item(item(view,'9mm'));destination(view,item(view,'bag_plastic'));quantity(31)
                sent=latest()['transfers_sent'];click(11.75,9.97)
                check('excess_quantity_remains_in_menu_without_command',latest()['transfers_sent']==sent and int(latest()['equipment_form'])==1)
                quantity(7);shot('transfer-selected.png')
                if args.action_driven:
                    # The ordinary native loop can finish five seconds of work
                    # between two GUI frames; it has no wall-clock pacing.
                    tap('Escape');view=open_inventory()
                    check('ordinary_escape_changes_no_ammunition',item(view,'9mm').Charges()==30)
                else:
                    action(True);wait(lambda r:int(r['transfer_token'])>0)
                    check('insert_uses_paid_native_activity',int(latest()['transfer_total'])>0 and int(latest()['transfer_remaining'])>0)
                    view=open_inventory();remaining=int(latest()['transfer_remaining']);stopped=latest()['simulation_time'];time.sleep(.8)
                    check('menu_freezes_native_work_and_time',int(latest()['transfer_remaining'])==remaining and latest()['simulation_time']==stopped)
                    shot('transfer-paused.png')
                    if args.save_active:
                        check('saved_work_has_not_moved_ammo_early',item(view,'9mm').Charges()==30)
                        check('actual_runtime_survives',proc.poll() is None)
                    else:
                        cancelled=int(latest()['cancel_consumption_sent']);click(13.4,10.35)
                        wait(lambda r:int(r['equipment_form'])==0 and int(r['cancel_consumption_sent'])==cancelled+1)
                        finish();view=open_inventory();check('native_cancel_keeps_all_thirty_rounds',item(view,'9mm').Charges()==30)
                if not args.save_active:
                    transfer_panel();select_item(item(view,'9mm'));destination(view,item(view,'bag_plastic'));quantity(7);action(True);finish()
                    view=open_inventory();bag=item(view,'bag_plastic');nested=item(view,'9mm',bag.Id())
                    check('native_transfer_splits_exact_seven',nested.Charges()==7)
                    check('native_transfer_leaves_twenty_three',sum(e.Charges() for e in entries(view) if e.TypeId().decode()=='9mm' and e.ParentId()!=bag.Id())==23)
                    check('native_provenance_identifies_destination',nested.PocketIndex()>=0)
                    transfer_panel();select_item(nested);quantity(3);action(False);finish()
                    view=open_inventory();bag=item(view,'bag_plastic')
                    check('partial_drop_preserves_four_in_nested_container',item(view,'9mm',bag.Id()).Charges()==4)
                    transfer_panel();select_item(bag);quantity(1);action(False);finish();view=open_inventory()
                    check('loaded_container_dropped_as_one_native_object',not any(e.TypeId().decode()=='bag_plastic' for e in entries(view)))
                    check('only_twenty_three_rounds_remain_owned',sum(e.Charges() for e in entries(view) if e.TypeId().decode()=='9mm')==23)
                    transfer_panel();select_item(item(view,'bat'));destination(view,item(view,'bottle_plastic'));action(True);finish();view=open_inventory()
                    check('native_size_rejection_preserves_bat',bool(item(view,'bat')))
                    tap('Escape');wait(lambda r:int(r['equipment_form'])==0)
                    if not args.action_driven:
                        tap('F7');wait(lambda r:int(r['pause_reasons'])==1);view=open_inventory()
                        transfer_panel();select_item(item(view,'9mm'));quantity(1)
                        sent=latest()['transfers_sent'];stopped=latest()['simulation_time'];click(4.65,9.97)
                        check('manual_pause_blocks_transfer_without_queuing',latest()['transfers_sent']==sent and int(latest()['equipment_form'])==1)
                        tap('Escape');wait(lambda r:int(r['equipment_form'])==0 and int(r['pause_reasons'])==1)
                        check('closing_transfer_menu_preserves_manual_pause',latest()['simulation_time']==stopped)
                        tap('F7');wait(lambda r:int(r['pause_reasons'])==0)
                        check('resume_does_not_replay_rejected_transfer',latest()['transfers_sent']==sent)
                    view=open_inventory();connection_id=latest()['connection_id'];sent=latest()['transfers_sent'];drop.set()
                    wait(lambda r:r['connection_id']!=connection_id and int(r['input_ready'])==1 and int(r['equipment_form'])==0,timeout=20)
                    check('reconnect_closes_stale_item_handles',True);check('reconnect_replays_no_transfer',latest()['transfers_sent']==sent)
                    view=open_inventory();check('resync_restores_native_twenty_three_rounds',item(view,'9mm').Charges()==23)
                    tap('Escape');check('actual_runtime_survives',proc.poll() is None)
        finally:
            stop.set()  # Declared shutdown: native peers may reset while closing.
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
            scratch.cleanup()
            if old_window:
                subprocess.run(['xdotool', 'windowactivate', old_window], capture_output=True)
    check('byte_relay_completed_without_errors', not relay_errors)
    output = out / 'native.json'
    with (out / 'native.log').open('w') as log:
        result = subprocess.run([str(args.native_reader.resolve()), '--userdir', str(user),
            '--datadir', str(ws / 'cdda/data'), '--output', str(output)], stdout=log, stderr=subprocess.STDOUT, timeout=180)
    check('transfer_save_readable_by_pristine_native_core',result.returncode==0)
    native=json.loads(output.read_text())
    def items(value):
        found=[]
        if isinstance(value,dict):
            if 'typeid' in value:found.append(value)
            for child in value.values():found.extend(items(child))
        elif isinstance(value,list):
            for child in value:found.extend(items(child))
        return found
    owned=items(native['player']);ground=items(native['ground_items'])
    check('canonical_total_ammo_conserved',sum(i.get('charges',0) for i in owned+ground if i['typeid']=='9mm')==30)
    check('canonical_bag_exists_once',sum(i.get('item_vars',{}).get('uid')=='transfer-bag' for i in owned+ground)==1)
    check('canonical_bat_and_bottle_survive',all(sum(i.get('item_vars',{}).get('uid')==uid for i in owned+ground)==1 for uid in ['transfer-bat','transfer-bottle']))
    if args.save_active:
        check('canonical_activity_is_native_insert',native['player']['activity']['type']=='ACT_INSERT_ITEM')
        check('canonical_saved_insert_contains_native_item_locations',bool(native['player']['activity']['actor']))
    elif args.resume_only:
        check('canonical_resumed_insert_is_complete',native['player']['activity']['type']=='ACT_NULL')
        check('canonical_saved_container_has_seven_rounds',sum(i.get('charges',0) for i in items(next(i for i in owned if i.get('item_vars',{}).get('uid')=='transfer-bag')) if i['typeid']=='9mm')==7)
    else:
        check('canonical_owned_ammo_is_twenty_three',sum(i.get('charges',0) for i in owned if i['typeid']=='9mm')==23)
        bag=next(i for i in ground if i.get('item_vars',{}).get('uid')=='transfer-bag')
        check('canonical_dropped_container_keeps_four_rounds',sum(i.get('charges',0) for i in items(bag) if i['typeid']=='9mm')==4)
        check('canonical_ground_receives_three_loose_rounds',sum(i.get('charges',0) for i in ground if i['typeid']=='9mm')==7)
    check('canonical_position_unchanged',native['player_abs']==[60,60,0])
    if args.action_driven: check('ordinary_transfers_pay_native_simulation_time',native['time']>json.loads((args.fixture.parent/'before.json').read_text())['time'])
    (out / 'summary.json').write_text(json.dumps(dict(checks=checks, native_save=str(output)), indent=2)+'\n')


if __name__ == '__main__':
    main()
