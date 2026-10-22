#!/usr/bin/env python3
"""Exercise the native rest, wait and sleep in the actual Luanti renderer.

Requires an independently created --create-rest fixture, X11, xdotool,
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
import queue
import struct


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('workspace', 'fixture', 'native-reader', 'artifacts'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--reload-sleep', action='store_true')
    args = parser.parse_args()
    ws, out = args.workspace.resolve(), args.artifacts.resolve()
    sys.path.insert(0,str(ws/'protocol/python'))
    from CDDA.CWM.CwmMessage import CwmMessage
    out.mkdir(parents=True, exist_ok=False)
    user = out / 'user'
    shutil.copytree(args.fixture.resolve(), user)
    (user / 'config/options.json').write_text(json.dumps([
        {'name': 'SAFEMODE', 'value': 'false'}, {'name': 'AUTOSAFEMODE', 'value': 'false'},
        {'name': 'AUTOSAVE', 'value': 'false'}, {'name': 'QUERY_DISASSEMBLE', 'value': 'true'}]))
    checks = {}
    injections=queue.Queue()
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
    # A local relay records real renderer traffic and injects explicit protocol
    # probes. It renumbers client envelope sequences for the additional frames;
    # command/quote identity and payload bytes remain unchanged.
    scratch = tempfile.TemporaryDirectory(prefix='cwm-conversation-gui-')
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
                    native_sequence=0;client_buffer=bytearray()
                    def forward_client(packet):
                        nonlocal native_sequence
                        body=bytearray(packet[4:]);message=CwmMessage.GetRootAs(body)
                        native_sequence+=1
                        offset=message._tab.Offset(4)
                        if not offset:raise AssertionError('Client sequence must be explicit')
                        struct.pack_into('<Q',body,message._tab.Pos+offset,native_sequence)
                        frame=struct.pack('>I',len(body))+body
                        with (out/'client-wire.bin').open('ab') as capture:capture.write(frame)
                        server_socket.sendall(frame)
                    while not stop.is_set():
                        if drop.is_set():
                            drop.clear()
                            break
                        while not injections.empty():forward_client(injections.get_nowait())
                        readable, _, _ = select.select([client_socket, server_socket], [], [], .03)
                        closed=False
                        for source in readable:
                            data=source.recv(1<<20)
                            if not data:closed=True;break
                            if source is client_socket:
                                client_buffer.extend(data)
                                while len(client_buffer)>=4:
                                    size=struct.unpack('>I',client_buffer[:4])[0]
                                    if len(client_buffer)<size+4:break
                                    forward_client(bytes(client_buffer[:size+4]));del client_buffer[:size+4]
                            else:
                                with (out/'server-wire.bin').open('ab') as capture:capture.write(data)
                                client_socket.sendall(data)
                        if closed:break
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
        # Xvfb without a WM has no _NET_ACTIVE_WINDOW support. Direct focus
        # is sufficient for the real client on this isolated display.
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
        proc = subprocess.Popen([str(ws / 'start.sh'), '--go', '--name', 'conversation_tester', '--port', str(port), '--info'],
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
            from CDDA.CWM.DecisionPrompt import DecisionPrompt
            from CDDA.CWM.WorldSnapshot import WorldSnapshot
            def messages(kind,direction="server"):
                import struct
                buf=(out/(direction+'-wire.bin')).read_bytes();offset=0;found=[]
                while offset+4<=len(buf):
                    n=struct.unpack('>I',buf[offset:offset+4])[0];offset+=4
                    if offset+n>len(buf):break
                    msg=CwmMessage.GetRootAs(buf[offset:offset+n]);offset+=n
                    if msg.PayloadType()==kind:found.append(msg)
                return found
            def prompt():
                msg=messages(Payload.DecisionPrompt)[-1]
                p=DecisionPrompt();p.Init(msg.Payload().Bytes,msg.Payload().Pos)
                return p
            def labels(p): return [p.Choices(n).decode() for n in range(p.ChoicesLength())]
            def talk():
                turn(0,-9)
                wait(lambda r: int(r['combat_hover'])>>63==1)
                xdo('click','3')
                wait(lambda r:int(r['pending_decision'])>0)
                return prompt()
            def choose(n):
                old=latest()['pending_decision'];tap(str(n+1))
                wait(lambda r:r['pending_decision']!=old)
            def leave():
                tap('Escape')
                wait(lambda r:int(r['pending_decision'])==0 and int(r['pending_move'])==0)


            from CDDA.CWM.CommandAck import CommandAck
            from CDDA.CWM.RestRequest import RestRequest
            def pick(part):
                values=labels(prompt());matches=[n for n,v in enumerate(values) if part in v]
                check('menu_has_'+part.replace(' ','_')+'_'+str(len(checks)),len(matches)==1)
                choose(matches[0])
            def rest_menu():
                tap('b');wait(lambda r:int(r['pending_decision'])>0)
                return labels(prompt())
            def idle():
                wait(lambda r:int(r['pending_move'])==0 and int(r['pending_decision'])==0)
            def phase():return int(latest()['rest_phase'])
            def position():return (latest()['target_x'],latest()['target_z'])
            def paused_reading():
                tap('i');wait(lambda r:int(r['pause_reasons'])&2)
                frozen=latest()['simulation_time'];pos=position();time.sleep(.7)
                check('inventory_freezes_rest_clock_'+str(len(checks)),latest()['simulation_time']==frozen and position()==pos)
                tap('Escape');wait(lambda r:int(r['pause_reasons'])==0)
            if not args.reload_sleep:
                check('fixture_starts_awake',phase()==-1)
                values=rest_menu();check('rest_offers_native_sleep_and_wait',any('Try to sleep' in x for x in values) and any('Wait or catch' in x for x in values))
                frozen=latest()['simulation_time'];time.sleep(.5)
                check('rest_menu_pauses_world',latest()['simulation_time']==frozen)
                leave();check('cancel_rest_keeps_avatar_awake',phase()==-1)
                rest_menu();pick('Wait or catch your breath');pick('Wait 20 heartbeats')
                wait(lambda r:int(r['rest_phase'])==0);idle()
                check('short_native_wait_stays_unaccelerated',int(latest()['rest_accelerated'])==0)
                paused_reading();rest_menu();pick('Interrupt rest');idle();wait(lambda r:int(r['rest_phase'])==-1)
                check('native_wait_cancels_through_rest_menu',phase()==-1)
                command=messages(Payload.RestRequest,'client')[-1];request=RestRequest();request.Init(command.Payload().Bytes,command.Payload().Pos)
                def acks():
                    result=[]
                    for msg in messages(Payload.CommandAck):
                        a=CommandAck();a.Init(msg.Payload().Bytes,msg.Payload().Pos)
                        if a.CommandId()==request.CommandId():result.append(a)
                    return result
                count=len(acks());data=bytes(command._tab.Bytes);injections.put(struct.pack('>I',len(data))+data)
                deadline=time.monotonic()+10
                while len(acks())<=count and time.monotonic()<deadline:time.sleep(.05)
                check('rest_replay_returns_cached_outcome_without_restart',len(acks())>count and acks()[-1].Accepted() and phase()==-1 and int(latest()['pending_decision'])==0)
                rest_menu();pick('Try to sleep');pick('No.');idle()
                check('native_sleep_decline_stays_awake',phase()==-1)
                rest_menu();pick('Try to sleep');pick('Yes.');idle()
                wait(lambda r:int(r['rest_phase'])==2,timeout=25)
                check('native_sleep_attempt_reaches_actual_sleep',phase()==2)
            else:
                wait(lambda r:int(r['rest_phase'])==2)
                check('canonical_reload_restores_sleep_without_start_command',not messages(Payload.RestRequest,'client'))
            values=rest_menu();check('actual_sleep_has_no_forced_wake_override',not any('Interrupt rest' in x for x in values))
            pick('Continue at normal speed');idle()
            check('normal_speed_rest_can_be_selected',int(latest()['rest_accelerated'])==0)
            pos=position();xdo('keydown','--window',window,'w');time.sleep(.7);xdo('keyup','--window',window,'w');time.sleep(.3)
            check('sleep_blocks_held_movement',phase()==2 and position()==pos)
            paused_reading();shot('sleeping.png')
            rest_menu();pick('Fast-forward long rest');idle()
            wait(lambda r:int(r['rest_accelerated'])==1,timeout=15)
            start=float(latest()['simulation_time']);time.sleep(.8);advanced=float(latest()['simulation_time'])-start
            check('long_rest_advances_native_turns_faster_than_normal',advanced>12)
            rest_menu();pick('Continue at normal speed');idle()
            check('return_to_normal_clears_rest_acceleration',int(latest()['rest_accelerated'])==0)
            paused_reading()
            values=rest_menu();connection=latest()['connection_id'];sent=len(messages(Payload.RestRequest,'client'));drop.set()
            wait(lambda r:r['connection_id']!=connection and int(r['input_ready'])==1 and int(r['pending_move'])==0 and int(r['pending_decision'])==0,timeout=25)
            check('reconnect_preserves_sleep_without_replaying_rest_command',phase()==2 and len(messages(Payload.RestRequest,'client'))==sent)
            values=rest_menu();check('reopened_rest_uses_actual_sleep_state',not any('Interrupt rest' in x for x in values))
            pick('Keep resting');idle();shot('sleep-reconnected.png')
            final=latest();(out/'final-trace.json').write_text(json.dumps(final,indent=2)+'\n')
        finally:
            shutting_down.set()
            if proc.poll() is None:
                os.killpg(proc.pid,signal.SIGTERM)
                try:proc.wait(timeout=45)
                except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
            stop.set();relay_thread.join(timeout=3);listener.close();scratch.cleanup()
            (out/'relay-errors.json').write_text(json.dumps(relay_errors))
            if old_window:subprocess.run(['xdotool','windowactivate',old_window],capture_output=True)
    check('relay_completed_without_errors',not relay_errors)
    logs='\n'.join(p.read_text(errors='replace') for p in (out/'logs').rglob('*.log'))
    check('rest_dialogs_accepted_by_actual_renderer','Invalid formspec' not in logs)
    output=out/'native.json'
    with (out/'native.log').open('w') as log:
        result=subprocess.run([str(args.native_reader.resolve()),'--userdir',str(user),'--datadir',str(ws/'cdda/data'),'--output',str(output)],stdout=log,stderr=subprocess.STDOUT,timeout=180)
    check('rest_save_readable_by_independent_pinned_core',result.returncode==0)
    native=json.loads(output.read_text());player=native['player']
    check('canonical_native_position_preserved',native['player_abs']==[60,60,0])
    check('actual_sleep_is_an_effect_not_an_invented_activity',player['activity']['type']=='ACT_NULL' and 'sleep' in player['effects'])
    check('native_sleep_preserves_prone_posture',player['move_mode']=='prone')
    (out/'summary.json').write_text(json.dumps({'checks':checks,'native_save':str(output)},indent=2)+'\n')

if __name__=='__main__':main()
