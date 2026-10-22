#!/usr/bin/env python3
"""Exercise the native mission journal in the actual Luanti renderer.

Requires an independently created --create-journal fixture, X11, xdotool,
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


            from CDDA.CWM.MissionView import MissionView
            from CDDA.CWM.MissionTrackRequest import MissionTrackRequest
            from CDDA.CWM.CommandAck import CommandAck
            from formspec_geometry import geometry
            def wait_wire(kind,count,timeout=12):
                deadline=time.monotonic()+timeout
                while time.monotonic()<deadline:
                    if len(messages(kind))>count:return
                    if proc.poll() is not None:break
                    time.sleep(.05)
                raise RuntimeError('Missing wire message '+str(kind))
            def view():
                msg=messages(Payload.MissionView)[-1];v=MissionView();v.Init(msg.Payload().Bytes,msg.Payload().Pos);return v
            def open_journal():
                count=len(messages(Payload.MissionView));tap('j');wait_wire(Payload.MissionView,count);wait(lambda r:int(r['pause_reasons'])&2)
                shot('journal-active.png');return view()
            def click(x,y):
                ox,oy,unit=geometry(out/'journal-active.png',height=12)
                xdo('mousemove','--window',window,str(round(ox+x*unit)),str(round(oy+y*unit)));xdo('click','1');time.sleep(.25)
            def refresh():
                count=len(messages(Payload.MissionView));click(5.5,11.2);wait_wire(Payload.MissionView,count);return view()
            def track(index):
                click(3,2.77+index*.84);count=len(messages(Payload.MissionView));click(13,11.2);wait_wire(Payload.MissionView,count);return view()
            v=open_journal();known=[v.Entries(n) for n in range(v.EntriesLength())]
            check('only_four_known_native_missions',len(known)==4)
            check('native_histories_are_partitioned', [e.State() for e in known]==[0,0,1,2])
            first,second=known[:2];first_id=first.Id();second_id=second.Id()
            check('canonical_native_mission_ids_are_distinct',first_id>=0 and second_id!=first_id)
            check('native_tracked_mission_exported',v.TrackedId()==second_id and second.Tracked())
            check('known_target_includes_native_vertical_coordinate',first.Target() is not None and first.Target().Z()==-1)
            check('unset_target_has_no_invented_location',second.Target() is None and not second.TargetText())
            check('native_deadline_and_remaining_are_visible',bool(second.Deadline()) and bool(second.Remaining()))
            check('no_unaccepted_inhaler_mission_disclosed',not any(b'Inhaler' in e.Title() for e in known))
            frozen=latest()['simulation_time'];time.sleep(.6);tap('w');
            check('browsing_keeps_time_and_position_frozen',latest()['simulation_time']==frozen and latest()['target_x']=='60' and latest()['target_z']=='-60')
            for tab in (1,2,0):click(.5+tab*3.4+1.4,1.75);shot('journal-tab-'+str(tab)+'.png')
            check('browsing_does_not_send_tracking_or_gameplay_commands',not messages(Payload.MissionTrackRequest,'client') and not messages(Payload.TalkRequest,'client'))
            v=track(0);check('explicit_track_updates_native_mission',v.TrackedId()==first_id)
            first_command=messages(Payload.MissionTrackRequest,'client')[-1];r=MissionTrackRequest();r.Init(first_command.Payload().Bytes,first_command.Payload().Pos);first_command_id=r.CommandId()
            check('tracking_keeps_clock_paused',latest()['simulation_time']==frozen)
            shot('journal-tracked.png')
            v=track(1);check('another_explicit_selection_changes_native_tracking',v.TrackedId()==second_id)
            def acks(command):
                values=[]
                for msg in messages(Payload.CommandAck):
                    a=CommandAck();a.Init(msg.Payload().Bytes,msg.Payload().Pos)
                    if a.CommandId()==command:values.append(a)
                return values
            before=len(acks(first_command_id));data=bytes(first_command._tab.Bytes);injections.put(struct.pack('>I',len(data))+data)
            deadline=time.monotonic()+8
            while len(acks(first_command_id))<=before and time.monotonic()<deadline:time.sleep(.05)
            check('replayed_selection_returns_cached_outcome',len(acks(first_command_id))>before and acks(first_command_id)[-1].Accepted())
            v=refresh();check('replay_does_not_restore_an_old_tracked_mission',v.TrackedId()==second_id)
            v=track(0);check('final_native_selection_is_first_mission',v.TrackedId()==first_id)
            tap('Escape');wait(lambda r:int(r['pause_reasons'])==0)
            tap('F7');wait(lambda r:int(r['pause_reasons'])==1);paused=latest()['simulation_time']
            v=open_journal();tap('Escape');wait(lambda r:int(r['pause_reasons'])==1)
            check('journal_close_preserves_explicit_manual_pause',latest()['simulation_time']==paused)
            tap('F7');wait(lambda r:int(r['pause_reasons'])==0)
            v=open_journal();sent=len(messages(Payload.MissionTrackRequest,'client'));connection=latest()['connection_id'];drop.set()
            wait(lambda r:r['connection_id']!=connection and int(r['input_ready'])==1 and int(r['pending_move'])==0,timeout=25)
            shot('journal-reconnected.png')
            try:geometry(out/'journal-reconnected.png',height=12);stale=True
            except AssertionError:stale=False
            check('connection_replacement_dismisses_stale_journal',not stale)
            check('connection_replacement_never_replays_selection',len(messages(Payload.MissionTrackRequest,'client'))==sent)
            v=open_journal();check('reopened_journal_uses_new_connection_and_canonical_tracking',v.TrackedId()==first_id and messages(Payload.MissionView)[-1].ConnectionId()==int(latest()['connection_id']))
            tap('Escape');wait(lambda r:int(r['pause_reasons'])==0)
            shot('journal-return-to-game.png');final=latest();(out/'final-trace.json').write_text(json.dumps(final,indent=2)+'\n')
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
    check('journal_widgets_are_accepted_by_actual_formspec_parser','Invalid scrollbar element' not in logs and 'Invalid formspec' not in logs)
    output=out/'native.json'
    with (out/'native.log').open('w') as log:
        result=subprocess.run([str(args.native_reader.resolve()),'--userdir',str(user),'--datadir',str(ws/'cdda/data'),'--output',str(output)],stdout=log,stderr=subprocess.STDOUT,timeout=180)
    check('journal_save_readable_by_independent_pinned_core',result.returncode==0)
    native=json.loads(output.read_text());player=native['player'];missions=native['missions']
    check('canonical_native_tracked_mission_persisted',player['active_mission']==first_id)
    check('canonical_history_lists_preserved',len(player['active_missions'])==2 and len(player['completed_missions'])==1 and len(player['failed_missions'])==1)
    check('no_new_missions_created_by_browsing',len(missions)==5)
    byid={m['uid']:m for m in missions}
    check('canonical_active_mission_stays_in_progress',byid[first_id]['status']=='in_progress' and byid[second_id]['status']=='in_progress')
    check('unaccepted_mission_stays_unassigned',any(m['status']=='yet_to_start' and m['player_id']==-1 for m in missions))
    check('canonical_native_position_preserved',native['player_abs']==[60,60,0])
    check('journal_does_not_create_a_native_activity',player['activity']['type']=='ACT_NULL')
    (out/'summary.json').write_text(json.dumps({'checks':checks,'native_save':str(output),'tracked':first_id},indent=2)+'\n')

if __name__=='__main__':main()
