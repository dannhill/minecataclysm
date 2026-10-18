#!/usr/bin/env python3
"""Exercise native paper-book reading in the actual Luanti renderer.

Requires an independently created --create-reading fixture, X11, xdotool,
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
    # A byte-transparent local relay lets the real client lose IPC while a
    # selection is queued under manual pause. Gameplay still runs in CDDA.
    scratch = tempfile.TemporaryDirectory(prefix='cwm-reading-gui-')
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
        proc = subprocess.Popen([str(ws / 'start.sh'), '--go', '--name', 'reading_tester', '--port', str(port), '--info'],
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
            def messages(kind):
                import struct
                buf=(out/'server-wire.bin').read_bytes();offset=0;found=[]
                while offset+4<=len(buf):
                    n=struct.unpack('>I',buf[offset:offset+4])[0];offset+=4
                    if offset+n>len(buf):break
                    msg=CwmMessage.GetRootAs(buf[offset:offset+n]);offset+=n
                    if msg.PayloadType()==kind:found.append(msg)
                return found
            def view():
                for msg in reversed(messages(Payload.InventoryView)):
                    v=InventoryView();v.Init(msg.Payload().Bytes,msg.Payload().Pos)
                    if v.ViewId()==int(latest()['inventory_view']):return v
                raise RuntimeError('No matching inventory view')
            def inventory():
                if not int(latest()['equipment_form']):tap('i')
                wait(lambda r:int(r['equipment_form'])==1 and int(r['inventory_view'])>0 and int(r['pending_move'])==0)
                return view()
            inventory();shot('inventory.png')
            from formspec_geometry import geometry
            ox,oy,unit=geometry(out/'inventory.png')
            def click(x,y):
                xdo('mousemove','--window',window,str(round(ox+x*unit)),str(round(oy+y*unit)))
                xdo('click','1');time.sleep(.3)
            def entries(v):return [v.Entries(n) for n in range(v.EntriesLength())]
            def item(v,kind):return next(e for e in entries(v) if e.TypeId()==kind.encode())
            def select_book(kind):
                v=inventory();book=item(v,kind)
                visible=[e for e in entries(v) if not e.QuickSlot()]
                visible.sort(key=lambda e:e.UiOrder() or 4096+e.Id())
                index=next(n for n,e in enumerate(visible) if e.Id()==book.Id())
                click(1.025+(index%9)*1.15,5.975+(index//9)*1.15)
                wait(lambda r:int(r['equipment_selected'])==book.Id())
                return book
            def start():
                sent=int(latest()['equipment_sent']);click(13.4,10.4)
                wait(lambda r:int(r['equipment_form'])==0 and int(r['equipment_sent'])==sent+1)
            def choice(index):
                wait(lambda r:int(r['pending_decision'])>0)
                msg=messages(Payload.DecisionPrompt)[-1]
                p=DecisionPrompt();p.Init(msg.Payload().Bytes,msg.Payload().Pos)
                options=[p.Choices(n).decode() for n in range(p.ChoicesLength())]
                check('native_study_choices_are_exposed','Read once' in options[0] and options[-1]=='Cancel' and len(options)>=3)
                shot('native-study-choices.png');tap(str((len(options)-1 if index<0 else index)+1))
                wait(lambda r:int(r['pending_decision'])==0 and int(r['pending_move'])==0)
            if args.resume_only:
                check('canonical_loaded_actor_is_native_reading',int(latest()['reading_token'])>0 and int(latest()['reading_remaining'])<int(latest()['reading_total']))
                remaining=latest()['reading_remaining'];clock=latest()['simulation_time'];time.sleep(.7)
                check('inspection_freezes_loaded_native_reading',latest()['reading_remaining']==remaining and latest()['simulation_time']==clock)
                tap('Escape');wait(lambda r:int(r['equipment_form'])==0)
                wait(lambda r:int(r['reading_token'])==0,timeout=180)
                check('loaded_reading_completes_without_reissuing_read',int(latest()['equipment_sent'])==0)
                book=select_book('mag_guns')
                check('book_remains_known_after_native_reload',book.Book().Identified())
                shot('completed-native-reading.png')
            else:
                unknown=select_book('book_fict_soft_satire_cats')
                check('inspection_discloses_unidentified_book_without_free_knowledge',unknown.Book() is not None and not unknown.Book().Identified() and unknown.Actions()&64)
                check('unidentified_book_has_no_skill_summary',b'theory' not in unknown.Book().Summary())
                frozen=latest()['simulation_time'];time.sleep(.7)
                check('book_inspection_is_paused_and_does_not_start_actor',latest()['simulation_time']==frozen and int(latest()['reading_token'])==0)
                shot('unidentified-book.png')
                tap('Escape');wait(lambda r:int(r['equipment_form'])==0)
                tap('F7');wait(lambda r:int(r['pause_reasons'])==1)
                select_book('book_fict_soft_satire_cats');sent=latest()['equipment_sent']
                click(13.4,10.4)
                check('manual_pause_does_not_queue_read',latest()['equipment_sent']==sent and int(latest()['equipment_form'])==1)
                tap('Escape');wait(lambda r:int(r['equipment_form'])==0)
                tap('F7');wait(lambda r:int(r['pause_reasons'])==0);time.sleep(.4)
                check('unpause_does_not_replay_rejected_read',latest()['equipment_sent']==sent and int(latest()['reading_token'])==0)
                select_book('book_fict_soft_satire_cats');start()
                wait(lambda r:int(r['reading_token'])>0)
                check('skim_is_actual_native_work',int(latest()['reading_total'])>0 and int(latest()['reading_skimming'])==1)
                wait(lambda r:int(r['reading_token'])==0 and int(r['equipment_form'])==1 and int(r['inventory_view'])>0,timeout=30)
                check('completed_native_skim_identifies_book',item(view(),'book_fict_soft_satire_cats').Book().Identified())
                book=select_book('mag_guns');check('known_book_exposes_native_theory',book.Book().Identified() and b'theory' in book.Book().Summary())
                start();choice(-1)
                wait(lambda r:int(r['equipment_form'])==1 and int(r['inventory_view'])>0)
                check('cancelled_study_creates_no_actor',int(latest()['reading_token'])==0)
                select_book('mag_guns');start();choice(0)
                wait(lambda r:int(r['reading_token'])>0 and 0<int(r['reading_remaining'])<int(r['reading_total']))
                token=latest()['reading_token'];total=int(latest()['reading_total'])
                check('known_chapter_uses_native_duration',total>=42000)
                inventory();remaining=int(latest()['reading_remaining']);clock=latest()['simulation_time'];time.sleep(.8)
                check('I_freezes_native_chapter_and_time',int(latest()['reading_remaining'])==remaining and latest()['simulation_time']==clock)
                shot('reading-paused.png');click(13.4,10.35)
                wait(lambda r:int(r['reading_token'])==0 and int(r['equipment_form'])==1 and int(r['inventory_view'])>0)
                check('interrupt_reading_keeps_book',item(view(),'mag_guns').Book().Identified())
                select_book('mag_guns');start();choice(0)
                wait(lambda r:int(r['reading_token'])>0 and int(r['pending_move'])==0)
                check('native_resume_keeps_paid_chapter_progress',0<int(latest()['reading_remaining'])<=remaining and latest()['reading_token']!=token)
                connection=latest()['connection_id'];sent=latest()['equipment_sent'];drop.set()
                wait(lambda r:r['connection_id']!=connection and int(r['input_ready'])==1 and int(r['reading_token'])>0,timeout=20)
                check('reconnect_retains_native_reading_without_replay',latest()['equipment_sent']==sent and 0<int(latest()['reading_remaining'])<total)
                if args.save_active:
                    inventory();check('quit_will_preserve_partial_native_chapter',0<int(latest()['reading_remaining'])<total)
                    shot('save-active-reading.png')
                else:
                    wait(lambda r:int(r['reading_token'])==0,timeout=180)
                    select_book('mag_guns');shot('completed-native-reading.png')
                check('actual_runtime_survives_native_reading',proc.poll() is None)
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
    output=out/'native.json'
    with (out/'native.log').open('w') as log:
        result=subprocess.run([str(args.native_reader.resolve()),'--userdir',str(user),'--datadir',str(ws/'cdda/data'),'--output',str(output)],stdout=log,stderr=subprocess.STDOUT,timeout=180)
    check('reading_save_readable_by_independent_pinned_core',result.returncode==0)
    native=json.loads(output.read_text());player=native['player']
    def items(value):
        if isinstance(value,dict):
            if 'typeid' in value:yield value
            for key,child in value.items():
                if key not in ('components','comps_used'):yield from items(child)
        elif isinstance(value,list):
            for child in value:yield from items(child)
    carried=list(items(player));books=[x for x in carried if x.get('item_vars',{}).get('uid') in ('reading-unknown','reading-skill')]
    check('canonical_books_are_preserved_exactly_once',len(books)==2 and len({x['item_vars']['uid'] for x in books})==2)
    check('native_skim_knowledge_is_canonical','book_fict_soft_satire_cats' in player['items_identified'])
    skill=player['skills']['gun']
    if args.save_active:
        check('canonical_save_contains_native_read_actor',player['activity']['type']=='ACT_READ')
        check('saved_progress_matches_frozen_trace',player['activity']['moves_left']==int(final['reading_remaining']) and 0<player['activity']['moves_left']<player['activity']['moves_total'])
        check('incomplete_chapter_does_not_grant_early_experience',skill['knowledgeExperience']==0 and skill['knowledgeLevel']==0)
    else:
        check('canonical_reading_actor_finishes',player['activity']['type']=='ACT_NULL')
        check('completed_native_chapter_grants_theoretical_experience',skill['knowledgeExperience']>0 or skill['knowledgeLevel']>0)
    check('canonical_position_unchanged',native['player_abs']==[60,60,0])
    check('no_luanti_reading_persistence',not any('luanti' in k.lower() for k in player))
    (out/'summary.json').write_text(json.dumps({'checks':checks,'native_save':str(output)},indent=2)+'\n')


if __name__=='__main__':main()
