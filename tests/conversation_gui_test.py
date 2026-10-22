#!/usr/bin/env python3
"""Exercise native NPC conversations in the actual Luanti renderer.

Requires an independently created --create-conversation fixture, X11, xdotool,
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
    args = parser.parse_args()
    ws, out = args.workspace.resolve(), args.artifacts.resolve()
    out.mkdir(parents=True, exist_ok=False)
    user = out / 'user'
    shutil.copytree(args.fixture.resolve(), user)
    (user / 'config/options.json').write_text(json.dumps([
        {'name': 'SAFEMODE', 'value': 'false'}, {'name': 'AUTOSAFEMODE', 'value': 'false'},
        {'name': 'AUTOSAVE', 'value': 'false'}, {'name': 'QUERY_DISASSEMBLE', 'value': 'true'}]))
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
    # A byte-transparent local relay lets the real client lose IPC while a
    # selection is queued under manual pause. Gameplay still runs in CDDA.
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
            p=talk(); npc=p.Conversation().NpcId()
            check('right_click_targets_native_npc_identity',npc>>63==1 and p.Conversation().Speaker()==b'Conversation NPC')
            check('native_topic_and_full_text_are_exported',p.Conversation().Topic()==b'TALK_STRANGER_NEUTRAL' and b'Hello there.' in p.Conversation().History())
            check('safe_leave_is_distinct_from_native_responses',labels(p)[-1]=='Leave conversation' and p.CancelChoice()==p.ChoicesLength()-1)
            shot('native-conversation.png')
            frozen=latest()['simulation_time'];time.sleep(1)
            check('conversation_pauses_native_time',latest()['simulation_time']==frozen and int(latest()['pause_reasons'])&16)
            # Root dialogue has many native options. Presentation pagination
            # must keep the same topic/history without running native effects.
            seen=[];history=p.Conversation().History();page_count=0
            if 'Next page' in labels(p):
                from formspec_geometry import geometry
                ox,oy,unit=geometry(out/'native-conversation.png',height=12)
                old=latest()['pending_decision'];first=labels(p)
                # Reach an offscreen response through the real scroll widget,
                # then select its numbered button with the mouse.
                xdo('mousemove','--window',window,str(round(ox+12*unit)),str(round(oy+6*unit)))
                xdo('click','--repeat','24','--delay','40','5');time.sleep(.3)
                shot('scrolled-native-replies.png')
                n=first.index('Next page');maximum=max(1,len(first)*23-76)
                y=2.3+n*2.3-maximum*.1+.35
                xdo('mousemove','--window',window,str(round(ox+10.15*unit)),str(round(oy+y*unit)))
                xdo('click','1');wait(lambda r:r['pending_decision']!=old)
                p=prompt();seen+=first;page_count=1
                check('offscreen_response_is_reachable_by_mouse_scroll',p.Conversation().History()==history)
            while True:
                options=labels(p);seen+=options;page_count+=1
                if 'Next page' not in options: break
                choose(options.index('Next page'));p=prompt()
                check('pagination_preserves_generated_topic_'+str(page_count),p.Conversation().History()==history and p.Conversation().NpcId()==npc and latest()['simulation_time']==frozen)
            check('native_choices_are_not_lost_to_pagination',page_count>=2 and len(seen)>9)
            leave()
            check('leave_returns_to_live_game',proc.poll() is None and int(latest()['input_ready'])==1)
            # Native trade is explicitly declined before a terminal UI or any
            # transfer. The conversation can continue after that native cancel.
            p=talk()
            while True:
                options=labels(p)
                selected=next((n for n,t in enumerate(options) if 'trade' in t.lower()),None)
                if selected is not None:break
                if 'Next page' not in options:raise AssertionError('No native trade response')
                choose(options.index('Next page'));p=prompt()
            choose(selected);p=prompt()
            check('unsupported_trade_is_explicit_and_nonblocking',p.Conversation() is None and b'No trade was made' in p.Text())
            shot('trade-boundary.png');choose(p.CancelChoice())
            wait(lambda r:int(r['pending_decision'])==0 and int(r['pending_move'])==0)
            check('native_trade_branch_returns_safely',proc.poll() is None)
            # A dropped connection safely leaves; recovery never chooses a
            # native reply or automatically starts the conversation again.
            p=talk();connection=latest()['connection_id'];sent=len(messages(Payload.TalkRequest,'client'));drop.set()
            wait(lambda r:r['connection_id']!=connection and int(r['input_ready'])==1 and int(r['pending_decision'])==0 and int(r['pending_move'])==0,timeout=25)
            check('disconnect_safely_leaves_without_replaying_talk',proc.poll() is None and len(messages(Payload.TalkRequest,'client'))==sent)
            shot('reconnected.png')
            tap('F7');wait(lambda r:int(r['pause_reasons'])==1)
            turn(0,-9);wait(lambda r:int(r['combat_hover'])==npc)
            xdo('click','3');time.sleep(.5)
            check('manual_pause_does_not_queue_talk',int(latest()['pending_decision'])==0 and int(latest()['pending_move'])==0)
            tap('F7');wait(lambda r:int(r['pause_reasons'])==0)
            time.sleep(.4)
            check('resume_does_not_replay_rejected_talk',int(latest()['pending_decision'])==0)
            p=talk();check('conversation_can_be_started_after_recovery',p.Conversation().NpcId()==npc)
            shot('save-during-conversation.png')
            final=latest()
            (out/'final-trace.json').write_text(json.dumps(final,indent=2)+'\n')
        finally:
            shutting_down.set()
            if proc.poll() is None:
                os.killpg(proc.pid,signal.SIGTERM)
                try:proc.wait(timeout=45)
                except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
            stop.set();relay_thread.join(timeout=3);listener.close();scratch.cleanup()
            (out/'relay-errors.json').write_text(json.dumps(relay_errors))
            if old_window:subprocess.run(['xdotool','windowactivate',old_window],capture_output=True)
    check('byte_relay_completed_without_errors',not relay_errors)
    logs='\n'.join(p.read_text(errors='replace') for p in (out/'logs').rglob('*.log'))
    check('conversation_widgets_are_accepted_by_real_formspec_parser','Invalid scrollbar element' not in logs)
    output=out/'native.json'
    with (out/'native.log').open('w') as log:
        result=subprocess.run([str(args.native_reader.resolve()),'--userdir',str(user),'--datadir',str(ws/'cdda/data'),'--output',str(output)],stdout=log,stderr=subprocess.STDOUT,timeout=180)
    check('conversation_save_readable_by_independent_pinned_core',result.returncode==0)
    native=json.loads(output.read_text());player=native['player']
    npcs=[n for n in native['npcs'] if n.get('name')=='Conversation NPC']
    check('same_canonical_npc_survives_save',len(npcs)==1 and npcs[0]['id']==(npc & ((1<<63)-1)))
    check('native_conversation_marks_npc_known',npcs[0]['known_to_u'])
    check('native_talk_attitude_is_settled',npcs[0]['attitude']==0)
    check('canonical_position_unchanged',native['player_abs']==[60,60,0])
    check('no_conversation_activity_or_fake_inventory',player['activity']['type']=='ACT_NULL' and not any('luanti' in k.lower() for k in player))
    (out/'summary.json').write_text(json.dumps({'checks':checks,'native_save':str(output)},indent=2)+'\n')


if __name__=='__main__':main()
