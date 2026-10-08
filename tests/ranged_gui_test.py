#!/usr/bin/env python3
"""Exercise native aiming, shooting and reload in the actual Luanti renderer.

Requires an independently created --create-ranged fixture, X11, xdotool,
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
        env.pop('CDDA_CONTINUOUS', None)
        env.pop('CDDA_REALTIME', None)
    # A byte-transparent local relay lets the real client lose IPC while a
    # selection is queued under manual pause. Gameplay still runs in CDDA.
    scratch = tempfile.TemporaryDirectory(prefix='cwm-ranged-gui-')
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
            relay_errors.append(str(error))
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
        proc = subprocess.Popen([str(ws / 'start.sh'), '--go', '--name', 'body_tester', '--info'],
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
            def messages(kind, client=False):
                import struct
                buf=(out/('client-wire.bin' if client else 'server-wire.bin')).read_bytes();offset=0;found=[]
                while offset+4<=len(buf):
                    n=struct.unpack('>I',buf[offset:offset+4])[0];offset+=4
                    if offset+n>len(buf):break
                    message=CwmMessage.GetRootAs(buf[offset:offset+n]);offset+=n
                    if message.PayloadType()==kind:found.append(message)
                return found
            def prompt():
                from CDDA.CWM.DecisionPrompt import DecisionPrompt
                m=messages(Payload.DecisionPrompt)[-1];p=DecisionPrompt();p.Init(m.Payload().Bytes,m.Payload().Pos)
                return p.DecisionId(),p.Text().decode(),[p.Choices(n).decode() for n in range(p.ChoicesLength())]
            def begin_reload(cancel=False, decline=False):
                tap('r');wait(lambda r:int(r['pending_decision'])>0)
                ident,text,labels=prompt()
                check('native_reload_choices_exclude_incompatible_ammo','Choose ammunition' in text and len(labels)==3 and labels[-1]=='Cancel' and not any('38' in x for x in labels))
                shot('ammo-choices.png')
                # The default 9mm stack is natively labeled without FMJ. Selection uses native order.
                index=next(i for i,label in enumerate(labels[:-1]) if 'FMJ' not in label)
                tap(str(len(labels)) if cancel else str(index+1))
                if cancel:
                    wait(lambda r:int(r['pending_decision'])==0 and int(r['pending_move'])==0);return
                wait(lambda r:int(r['pending_decision'])>0 and int(r['pending_decision'])!=ident)
                ident,text,labels=prompt();check('native_reload_confirmation','Reload' in text and labels==['Yes','No'])
                shot('reload-confirmation.png');tap('2' if decline else '1')
                wait(lambda r:int(r['pending_decision'])==0 and int(r['pending_move'])==0)
            def open_inventory():
                tap('i');wait(lambda r:int(r['equipment_form'])==1 and int(r['inventory_view'])>0)
            def cancel_reload():
                shot('reload-paused.png')
                from PIL import Image
                width,height=Image.open(out/'reload-paused.png').size;unit=height*.075
                x=(width-16*unit)/2+11.75*unit;y=(height-11*unit)/2+2.2*unit
                xdo('mousemove','--window',window,str(round(x)),str(round(y)));xdo('click','1')
                wait(lambda r:int(r['equipment_form'])==0 and int(r['reload_token'])==0 and int(r['pending_move'])==0)
            if args.resume_only:
                if args.resume_active:
                    wait(lambda r:int(r['reload_token'])>0)
                    check('canonical_reload_resumes_saved_progress',0<int(latest()['reload_remaining'])<=int(latest()['reload_total']))
                    wait(lambda r:int(r['reload_token'])==0,timeout=25)
                    check('saved_reload_completes_without_new_command',int(latest()['reload_sent'])==0 and int(latest()['weapon_ammo'])==15)
                else:
                    check('completed_reload_stays_completed',int(latest()['reload_token'])==0 and int(latest()['weapon_ammo'])==15)
                shot('reloaded.png')
            else:
                wait(lambda r:int(r['weapon_token'])>0)
                check('native_loaded_weapon_visible',int(latest()['weapon_ammo'])==3)
                turn(0,-8);wait(lambda r:int(r['combat_hover'])>0)
                target=latest()['combat_hover'];initial=latest();shot('pointed-target.png')
                if not args.action_driven:
                    tap('F7');wait(lambda r:int(r['pause_reasons'])==1)
                    frozen=latest();xdo('keydown','f');xdo('click','1');tap('r');time.sleep(.7);xdo('keyup','f')
                    check('manual_pause_blocks_aim_fire_reload_and_time',all(latest()[k]==frozen[k] for k in ('aim_sent','fire_sent','reload_sent','weapon_ammo','weapon_recoil','simulation_time')))
                    tap('F7');wait(lambda r:int(r['pause_reasons'])==0);time.sleep(.3)
                    check('paused_keys_not_replayed',latest()['fire_sent']==frozen['fire_sent'] and latest()['reload_sent']==frozen['reload_sent'])
                tap('h');wait(lambda r:int(r['body_form'])==1);frozen=latest()
                xdo('keydown','f');time.sleep(.6);xdo('keyup','f')
                check('reading_does_not_aim_for_free',all(latest()[k]==frozen[k] for k in ('aim_sent','weapon_recoil','simulation_time')))
                tap('Escape');wait(lambda r:int(r['body_form'])==0)
                turn(0,-8);wait(lambda r:r['combat_hover']==target)
                recoil=float(latest()['weapon_recoil']);sent=int(latest()['aim_sent']);native_time=latest()['simulation_time']
                xdo('keydown','f');wait(lambda r:int(r['aim_sent'])>=sent+2);time.sleep(.4);xdo('keyup','f')
                wait(lambda r:int(r['pending_move'])==0)
                check('held_aim_uses_native_paid_steps',float(latest()['weapon_recoil'])<recoil and latest()['simulation_time']!=native_time and int(latest()['weapon_ammo'])==3)
                shot('aimed.png');before=latest();sent=int(before['fire_sent'])
                xdo('mousedown','1');wait(lambda r:int(r['fire_sent'])==sent+1);time.sleep(.8);xdo('mouseup','1');wait(lambda r:int(r['pending_move'])==0)
                check('held_mouse_fires_exactly_once',int(latest()['fire_sent'])==sent+1 and int(latest()['weapon_ammo'])==2)
                check('native_shot_acknowledged',int(latest()['attack_result'])==1 and latest()['attack_target']==target)
                check('shot_does_not_move_player',all(abs(float(latest()[k])-float(before[k]))<.02 for k in ('target_x','target_y','target_z')))
                # Native ballistic hit/miss is authoritative; deterministic skill-rich fixture checks real damage.
                check('native_target_takes_damage',int(latest()['attack_target_hp'])<100)
                turn(180,0);wait(lambda r:int(r['combat_hover'])==0);sent=latest()['fire_sent'];xdo('click','1');time.sleep(.3)
                check('empty_reticle_sends_no_shot',latest()['fire_sent']==sent)
                turn(-27,-8);wait(lambda r:int(r['combat_hover'])>0);neutral=latest()['combat_hover'];sent=latest()['fire_sent'];xdo('click','1');time.sleep(.3)
                check('friendly_creature_not_accepted_as_ranged_target',neutral!=target and latest()['fire_sent']==sent)
                turn(0,-8);wait(lambda r:r['combat_hover']==target)
                begin_reload(cancel=True);check('cancel_ammo_choice_keeps_rounds',int(latest()['weapon_ammo'])==2 and int(latest()['reload_token'])==0)
                begin_reload(decline=True);check('decline_reload_keeps_rounds',int(latest()['weapon_ammo'])==2 and int(latest()['reload_token'])==0)
                begin_reload()
                if not args.action_driven:
                    wait(lambda r:int(r['reload_token'])>0);token=latest()['reload_token'];before=latest()
                    xdo('keydown','w');xdo('keydown','f');xdo('click','1');time.sleep(.3);xdo('keyup','w');xdo('keyup','f')
                    check('reload_blocks_movement_aim_and_fire',all(latest()[k]==before[k] for k in ('target_x','target_z','aim_sent','fire_sent')))
                    open_inventory();frozen=latest()['reload_remaining'];time.sleep(.6)
                    check('inventory_freezes_native_reload',latest()['reload_remaining']==frozen and int(latest()['weapon_ammo'])==2)
                    cancel_reload();check('cancel_native_reload_preserves_rounds',int(latest()['weapon_ammo'])==2)
                    connection=latest()['connection_id'];old_weapon=latest()['weapon_token'];sent=latest()['fire_sent'];drop.set()
                    wait(lambda r:r['connection_id']!=connection and int(r['input_ready'])==1,timeout=20)
                    check('reconnect_discards_old_weapon_handle_without_replaying_fire',latest()['weapon_token']!=old_weapon and latest()['fire_sent']==sent and int(latest()['weapon_ammo'])==2)
                    begin_reload();wait(lambda r:int(r['reload_token'])>0)
                    check('new_reload_has_fresh_activity_token',latest()['reload_token']!=token)
                    if args.save_active:
                        open_inventory();check('shutdown_keeps_native_reload_activity',int(latest()['reload_token'])>0 and int(latest()['weapon_ammo'])==2)
                        shot('save-active-reload.png')
                if not args.save_active:
                    wait(lambda r:int(r['reload_token'])==0,timeout=25)
                    check('native_reload_transfers_ammo_once',int(latest()['weapon_ammo'])==15)
                    shot('reload-complete.png')
                check('actual_runtime_survives_native_ranged_combat',proc.poll() is None)
        finally:
            shutting_down.set() # Resets caused by our SIGTERM are expected only after this boundary.
            subprocess.run(['xdotool', 'keyup', 'w', 'f'], capture_output=True)
            subprocess.run(['xdotool', 'mouseup', '1'], capture_output=True)
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
    check('ranged_save_readable_by_pristine_native_core', result.returncode == 0)
    native=json.loads(output.read_text())
    def live_items(value):
        if isinstance(value,dict):
            if 'typeid' in value:yield value
            for key,child in value.items():
                if key not in ('components','comps_used'):yield from live_items(child)
        elif isinstance(value,list):
            for child in value:yield from live_items(child)
    items=list(live_items(native['player']))
    guns=[it for it in items if it.get('item_vars',{}).get('uid')=='ranged-gun']
    check('native_gun_instance_persists_once',len(guns)==1)
    # Loaded and loose rounds are separate canonical objects, including nested magazine pockets.
    rounds=sum(it.get('charges',0) for it in items if it['typeid']=='9mm')
    check('canonical_ammunition_conserved_except_one_fired_round',rounds==32)
    for uid,total in [('ranged-other',20),('ranged-wrong',10)]:
        matches=[it for it in items if it.get('item_vars',{}).get('uid')==uid]
        check(uid+'_untouched',len(matches)==1 and matches[0]['charges']==total)
    activity=native['player']['activity']
    if args.save_active:
        check('canonical_save_contains_native_reload_actor',activity['type']=='ACT_RELOAD' and activity['moves_left']>0)
    else:
        check('completed_reload_has_no_pending_activity',activity['type']=='ACT_NULL')
    check('canonical_ranged_save_has_no_luanti_inventory',not any('luanti' in key.lower() for key in native['player']))
    (out/'summary.json').write_text(json.dumps(dict(checks=checks,native_save=str(output)),indent=2)+'\n')


if __name__ == '__main__':
    main()
