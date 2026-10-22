#!/usr/bin/env python3
"""Exercise the native individual companion controls in the actual Luanti renderer.

Requires an independently created --create-companions fixture, X11, xdotool,
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
                # An unarmed pointing ray has the product's normal four-tile
                # reach. Approach a guard through real native movement first.
                for _ in range(14):
                    turn(0,-9)
                    if int(latest()['combat_hover'])>>63==1:break
                    xdo('keydown','--window',window,'w');time.sleep(.12);xdo('keyup','--window',window,'w');time.sleep(.2)
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


            from CDDA.CWM.DecisionResponse import DecisionResponse
            from formspec_geometry import geometry
            def pick(text,part=False,mouse=False):
                for _ in range(10):
                    p=prompt();ls=labels(p)
                    found=[n for n,label in enumerate(ls) if (text in label if part else label==text)]
                    if found:
                        n=found[0];old=latest()['pending_decision']
                        if mouse:
                            shot('companion-click-layout.png');ox,oy,unit=geometry(out/'companion-click-layout.png',height=12)
                            xdo('mousemove','--window',window,str(round(ox+10.5*unit)),str(round(oy+(2.69+n*.91)*unit)));xdo('click','1')
                            wait(lambda r:r['pending_decision']!=old)
                        else:choose(n)
                        return prompt()
                    if 'Next page' not in ls:raise AssertionError('Choice unavailable: '+text+' / '+repr(ls))
                    choose(ls.index('Next page'))
                raise AssertionError('Pagination did not terminate')
            def control():
                talk();p=pick('Companion orders and rules')
                check('native_panel_context_is_typed',bool(p.Conversation() and p.Conversation().CompanionControls()))
                return p
            def body():return prompt().Text().decode()
            def npc_pos():
                for msg in reversed(messages(Payload.WorldSnapshot)):
                    state=WorldSnapshot();state.Init(msg.Payload().Bytes,msg.Payload().Pos)
                    for i in range(state.EntitiesLength()):
                        e=state.Entities(i)
                        if e.Name()==b'Companion NPC':return (e.Pos().X(),e.Pos().Y(),e.Pos().Z())
                raise AssertionError('Native perceived companion missing')
            p=control();shot('companion-home.png');frozen=latest()['simulation_time'];start=(latest()['target_x'],latest()['target_z'])
            time.sleep(.5);tap('w')
            check('browsing_freezes_native_time_and_player',latest()['simulation_time']==frozen and (latest()['target_x'],latest()['target_z'])==start)
            pick('Combat rules',mouse=True);shot('companion-combat.png')
            pick('Use firearms:',part=True);shot('companion-override.png')
            check('base_and_effective_override_are_distinct','Base rule: On' in body() and 'Effective rule: Off' in body() and 'Temporary override: Off' in body())
            pick('Disable base rule');old_reply=messages(Payload.DecisionResponse,'client')[-1]
            pick('Enable base rule');current=latest()['pending_decision']
            check('base_change_does_not_clear_temporary_order','Base rule: On' in body() and 'Effective rule: Off' in body())
            data=bytes(old_reply._tab.Bytes);injections.put(struct.pack('>I',len(data))+data);time.sleep(.6)
            check('stale_decision_does_not_repeat_old_rule_change',latest()['pending_decision']==current and 'Base rule: On' in body())
            pick('Use base rule (remove override)')
            check('explicit_override_removal_restores_base','Effective rule: On' in body() and 'Temporary override: None' in body())
            pick('Disable base rule');pick('Back');pick('Back')
            pick('Behavior rules');pick('Bash obstacles:',part=True);pick('Enable base rule');pick('Temporarily disable')
            check('individual_behavior_override_is_explicit','Base rule: On' in body() and 'Effective rule: Off' in body())
            shot('companion-behavior.png');pick('Back');pick('Back')
            pick('Engagement policy');pick('All enemies');check('native_engagement_choice_marked','* All enemies' in labels(prompt()));pick('Back')
            pick('Aiming policy');pick('Shoot only when precisely aimed');check('native_aim_choice_marked','* Shoot only when precisely aimed' in labels(prompt()));pick('Back')
            pick('Bionic power policy');pick('Power reserved for defense');pick('Reserve 25%');pick('Back')
            pick('Recharge threshold');pick('Recharge below 75%');pick('Back');pick('Back')
            check('editing_decisions_keep_native_clock_frozen',latest()['simulation_time']==frozen)
            pick('Guard this position');check('native_guard_order_changes_current_status','Guarding position' in body())
            shot('companion-guard.png');p=pick('Back to conversation')
            check('explicit_back_returns_to_native_guard_topic',not p.Conversation().CompanionControls() and any('come with me' in label for label in labels(p)))
            pick('Companion orders and rules');tap('Escape');wait(lambda r:int(r['pending_decision'])==0 and int(r['pending_move'])==0)
            check('safe_leave_returns_live_controls',int(latest()['pause_reasons'])==0)
            guard=npc_pos()
            xdo('keydown','--window',window,'s');time.sleep(.75);xdo('keyup','--window',window,'s');time.sleep(.6)
            check('guarded_companion_does_not_follow_player_step_for_step',npc_pos()==guard and (latest()['target_x'],latest()['target_z'])!=start)
            p=control();pick('Follow me');check('native_follow_order_changes_current_status','Following you' in body());tap('Escape')
            wait(lambda r:int(r['pending_decision'])==0 and int(r['pending_move'])==0)
            xdo('keydown','--window',window,'s');time.sleep(.9);xdo('keyup','--window',window,'s');time.sleep(2)
            check('companion_ai_moves_after_follow_resumes',npc_pos()!=guard)
            p=control();shot('companion-following.png');sent=len(messages(Payload.TalkRequest,'client'));connection=latest()['connection_id'];drop.set()
            wait(lambda r:r['connection_id']!=connection and int(r['input_ready'])==1 and int(r['pending_move'])==0,timeout=25)
            shot('companion-reconnected.png')
            try:geometry(out/'companion-reconnected.png',height=12);stale=True
            except AssertionError:stale=False
            check('reconnect_dismisses_old_companion_panel',not stale)
            check('reconnect_does_not_replay_talk_or_orders',len(messages(Payload.TalkRequest,'client'))==sent)
            p=control();pick('Behavior rules');pick('Bash obstacles:',part=True)
            check('fresh_connection_projects_current_canonical_rule','Base rule: On' in body() and 'Effective rule: Off' in body())
            tap('Escape');wait(lambda r:int(r['pending_decision'])==0 and int(r['pending_move'])==0)
            shot('companion-return-to-game.png');(out/'final-trace.json').write_text(json.dumps(latest(),indent=2)+'\n')
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
    check('companion_widgets_are_accepted_by_actual_parser','Invalid formspec' not in logs)
    output=out/'native.json'
    with (out/'native.log').open('w') as log:
        result=subprocess.run([str(args.native_reader.resolve()),'--userdir',str(user),'--datadir',str(ws/'cdda/data'),'--output',str(output)],stdout=log,stderr=subprocess.STDOUT,timeout=180)
    check('companion_save_readable_by_independent_pinned_core',result.returncode==0)
    native=json.loads(output.read_text());people=[n for n in native['npcs'] if n['name']=='Companion NPC']
    check('same_canonical_companion_survives',len(people)==1)
    n=people[0];rules=n['rules']
    check('canonical_individual_base_rules_persist',not rules['rule_use_guns'] and rules['rule_allow_bash'])
    check('canonical_temporary_override_persists',rules['override_enable_allow_bash'] and not rules['override_allow_bash'] and not rules['override_enable_use_guns'])
    check('canonical_native_policies_persist',rules['engagement']==4 and rules['aim']==3 and rules['cbm_reserve']==25 and rules['cbm_recharge']==75)
    check('native_follow_assignment_persists',n['attitude']==3 and n['mission']==0 and n['assigned_camp'] is None)
    check('companion_panel_does_not_create_player_activity',native['player']['activity']['type']=='ACT_NULL')
    (out/'summary.json').write_text(json.dumps({'checks':checks,'native_save':str(output),'companion':'Companion NPC'},indent=2)+'\n')

if __name__=='__main__':main()
