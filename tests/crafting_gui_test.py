#!/usr/bin/env python3
"""Exercise native crafting in the actual Luanti renderer.

Requires an independently created --create-crafting fixture, X11, xdotool,
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
    parser.add_argument('--recipe-shortcuts', action='store_true')
    parser.add_argument('--catalog-feedback', action='store_true')
    parser.add_argument('--modal-continuity', action='store_true')
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
    scratch = tempfile.TemporaryDirectory(prefix='cwm-crafting-gui-')
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
            from CDDA.CWM.CraftingView import CraftingView
            def messages(kind):
                import struct
                buf=(out/'server-wire.bin').read_bytes();offset=0;found=[]
                while offset+4<=len(buf):
                    n=struct.unpack('>I',buf[offset:offset+4])[0];offset+=4
                    if offset+n>len(buf):break
                    message=CwmMessage.GetRootAs(buf[offset:offset+n]);offset+=n
                    if message.PayloadType()==kind:found.append(message)
                return found
            def catalog():
                found=[]
                for message in messages(Payload.CraftingView):
                    v=CraftingView();v.Init(message.Payload().Bytes,message.Payload().Pos)
                    if v.ViewId():found.append(v)
                return found[-1]
            def entries(v):return [v.Entries(n) for n in range(v.EntriesLength())]
            def open_crafting():
                if int(latest()['crafting_form'])!=1:tap('i' if int(latest().get('action_menu',0)) else 'k')
                wait(lambda r:int(r['crafting_form'])==1 and int(r['crafting_view'])>0 and int(r['pause_reasons'])&2)
                return catalog()
            view=open_crafting();check('native_crafting_catalog_opened',True);shot('catalog.png')
            from PIL import Image
            from formspec_geometry import geometry
            origin_x,origin_y,unit=geometry(out/'catalog.png')
            def click(x,y):
                xdo('mousemove','--window',window,str(round(origin_x+x*unit)),str(round(origin_y+y*unit)))
                xdo('click','1');time.sleep(.3)
            def search(text='bandage'):
                old=latest()['crafting_view'];click(2,1.3)
                xdo('key','ctrl+a');xdo('key','BackSpace');xdo('type','--clearmodifiers',text);click(6.9,1.325)
                wait(lambda r:int(r['crafting_view'])>0 and r['crafting_view']!=old)
                return catalog()
            def tab(index):
                if catalog().Filter()==index:return catalog()
                old=latest()['crafting_view'];click(1.35+index*1.85,2.2)
                wait(lambda r:int(r['crafting_view'])>0 and r['crafting_view']!=old)
                v=catalog();check('native_filter_'+str(index),v.Filter()==index);return v
            def favorite_recipe(v,desired):
                selected=next(e for e in entries(v) if e.RecipeId()==b'bandages_makeshift' and not e.Resume());select_recipe(v)
                old=latest()['crafting_view'];frozen=latest()['simulation_time'];work=latest()['crafting_sent']
                click(11.5,10.1)
                wait(lambda r:int(r['crafting_view'])>0 and r['crafting_view']!=old)
                v=catalog();check('favorite_free_keeps_time_work_and_menu_'+str(desired),latest()['simulation_time']==frozen and latest()['crafting_sent']==work and int(latest()['crafting_form'])==1)
                check('favorite_result_'+str(desired),all(e.Favorite()==desired for e in entries(v) if e.RecipeId()==b'bandages_makeshift'))
                return v
            def select_recipe(v,resume=False):
                e=next(e for e in entries(v) if e.RecipeId()==b'bandages_makeshift' and e.Resume()==resume)
                index=e.Id()-1;click(1.025+(index%6)*1.18,3.225+(index//6)*1.12)
                wait(lambda r:int(r['crafting_selected'])==e.Id());return e
            def start():
                sent=int(latest()['crafting_sent']);click(11.5,9.325)
                wait(lambda r:int(r['crafting_form'])==0 and int(r['crafting_sent'])==sent+1)
            def prompt():
                from CDDA.CWM.DecisionPrompt import DecisionPrompt
                message=messages(Payload.DecisionPrompt)[-1]
                p=DecisionPrompt();p.Init(message.Payload().Bytes,message.Payload().Pos)
                return p.DecisionId(),p.Text().decode(),[p.Choices(n).decode() for n in range(p.ChoicesLength())]
            def choose(approve=True):
                for _ in range(12):
                    wait(lambda r:int(r['pending_decision'])>0)
                    identifier,text,options=prompt()
                    if 'Consume these components' in text:
                        check('native_confirmation_names_recipe_components_and_quantity','cotton' in text.lower() and 'bandage' in text.lower() and options==['Yes','No'])
                        shot('component-confirmation.png');tap('1' if approve else '2')
                        wait(lambda r:int(r['pending_move'])==0 and int(r['pending_decision'])==0)
                        return
                    # Native component alternatives/source choices. Never synthesize a material choice.
                    check('native_component_sources_exposed',any('nearby' in label or 'on person' in label for label in options))
                    shot('component-sources.png')
                    index=next((i for i,label in enumerate(options) if 'on person' in label),0)
                    tap(str(index+1));wait(lambda r:int(r['pending_decision'])!=identifier)
                raise RuntimeError('Unexpected native crafting decision loop')
            def set_batch(number):
                old=latest()['crafting_view'];click(9,1.325)
                xdo('key','Home')
                if number>1:xdo('key',*(['Down']*(number-1)))
                xdo('key','Return')
                wait(lambda r:int(r['crafting_view'])>0 and r['crafting_view']!=old)
                return catalog()
            if args.catalog_feedback:
                view=tab(0)
                check('navigation_categories_are_not_craftable_rows',all(not e.RecipeId().startswith(b'nested_') for e in entries(view)))
                frozen=latest()['simulation_time'];sent=latest()['crafting_sent']
                click(2,1.3)
                text=''
                for character in 'band':
                    old=latest()['crafting_view'];text+=character
                    xdo('type','--clearmodifiers',character)
                    wait(lambda r:int(r['crafting_view'])>0 and r['crafting_view']!=old)
                    view=catalog()
                    check('live_partial_search_'+text,bool(entries(view)) and all(text in (e.Name().decode()+' '+e.RecipeId().decode()).lower() for e in entries(view)))
                old=latest()['crafting_view']
                xdo('key','Home','Right','Right');xdo('type','X')
                wait(lambda r:int(r['crafting_view'])>0 and r['crafting_view']!=old)
                check('live_edit_keeps_middle_caret',catalog().EntriesLength()==0)
                old=latest()['crafting_view'];xdo('key','BackSpace')
                wait(lambda r:int(r['crafting_view'])>0 and r['crafting_view']!=old)
                check('live_delete_restores_partial_results',bool(entries(catalog())))
                check('live_search_does_not_advance_or_start_work',latest()['simulation_time']==frozen and latest()['crafting_sent']==sent)
                view=search();select_recipe(view)
                view=set_batch(2)
                selected=next(e for e in entries(view) if e.RecipeId()==b'bandages_makeshift' and not e.Resume())
                check('batch_refresh_rebinds_selected_recipe',int(latest()['crafting_selected'])==selected.Id() and view.Batch()==2)
                shot('live-search-selected-batch.png')
                view=set_batch(1)
                check('batch_one_keeps_selected_recipe',int(latest()['crafting_selected'])==next(e.Id() for e in entries(view) if e.RecipeId()==b'bandages_makeshift' and not e.Resume()))
            if args.recipe_shortcuts and args.resume_only:
                view=tab(1);check('favorite_survives_native_save_and_reload',any(e.RecipeId()==b'bandages_makeshift' and e.Favorite() for e in entries(view)))
                view=tab(2);check('recent_survives_native_save_and_reload',any(e.RecipeId()==b'bandages_makeshift' and e.RecentRank()==1 for e in entries(view)))
                shot('reloaded-native-shortcuts.png');tap('Escape');wait(lambda r:int(r['crafting_form'])==0)
            elif args.resume_only:
                saved=json.loads((args.fixture.parent/'native.json').read_text())
                if args.resume_active:
                    check('canonical_craft_resumes_saved_progress',int(latest()['crafting_token'])>0 and int(latest()['crafting_progress'])>0)
                    frozen=latest()['crafting_progress'];time.sleep(.7)
                    check('reload_menu_freezes_native_craft',latest()['crafting_progress']==frozen)
                    tap('Escape');wait(lambda r:int(r['crafting_form'])==0)
                    wait(lambda r:int(r['crafting_token'])==0,timeout=30)
                    check('resumed_craft_finishes_with_no_extra_command',int(latest()['crafting_sent'])==0)
                else:
                    check('finished_craft_reload_has_no_activity',int(latest()['crafting_token'])==0)
                    tap('Escape');wait(lambda r:int(r['crafting_form'])==0)
                shot('reloaded.png')
            else:
                before_time=latest()['simulation_time'];time.sleep(.7)
                check('catalog_pauses_native_time',latest()['simulation_time']==before_time)
                if args.recipe_shortcuts:
                    view=tab(2);check('fresh_recent_has_no_synthetic_history',view.EntriesLength()==0)
                    view=tab(1);check('fresh_favorites_has_no_implicit_selection',view.EntriesLength()==0)
                    view=tab(0);view=search();view=favorite_recipe(view,True)
                    view=tab(1);check('favorites_only_include_native_marked_recipes',view.EntriesLength()>0 and all(e.Favorite() for e in entries(view)));shot('favorite-recipes.png')
                    view=favorite_recipe(view,False);check('removing_last_favorite_yields_empty_view',view.EntriesLength()==0)
                    view=tab(0);view=search();view=favorite_recipe(view,True)
                    view=tab(2);check('favoriting_does_not_create_recent_work',view.EntriesLength()==0)
                    view=tab(0)
                view=search();e=select_recipe(view)
                check('native_requirements_duration_and_available_recipe',not e.Reason() and e.ExpectedMoves()>0 and b'cotton' in e.Requirements().lower())
                shot('recipe-details.png')
                modal_start=len(rows());start();choose(approve=False)
                view=open_crafting()
                check('declined_confirm_has_no_craft_activity',int(latest()['crafting_token'])==0)
                if args.modal_continuity:
                    span=rows()[modal_start:]
                    check('declining_components_returns_directly_to_catalog',len(span)>5 and all(int(r['modal_count'])>0 for r in span))
                if args.recipe_shortcuts:
                    view=open_crafting();view=tab(2);check('declined_craft_never_enters_recent',view.EntriesLength()==0);tap('Escape');wait(lambda r:int(r['crafting_form'])==0)
                view=open_crafting();view=search();select_recipe(view);modal_start=len(rows());start();choose(approve=True)
                wait(lambda r:int(r['crafting_token'])==0,timeout=20)
                check('first_native_craft_completes',True)
                view=open_crafting()
                if args.modal_continuity:
                    span=rows()[modal_start:]
                    check('native_craft_confirmation_work_and_result_keep_modal',len(span)>5 and all(int(r['modal_count'])>0 for r in span))
                if args.recipe_shortcuts:
                    view=tab(2);check('started_craft_enters_native_recent_without_search',any(e.RecipeId()==b'bandages_makeshift' and e.RecentRank()==1 for e in entries(view)));shot('recent-recipes.png');view=tab(0)
                view=search();view=set_batch(2);e=select_recipe(view)
                check('batch_query_updates_native_duration',view.Batch()==2 and e.ExpectedMoves()>=3200)
                start();choose(approve=True)
                if not args.action_driven:
                    r=wait(lambda r:int(r['crafting_token'])>0 and 0<int(r['crafting_progress'])<10000000);token=r['crafting_token']
                    check('native_craft_counter_is_not_meal_or_firstaid_timer',0<int(r['crafting_progress'])<10000000 and int(r['consumption_token'])==0 and int(r['first_aid_token'])==0)
                    xdo('keydown','w');time.sleep(.45);xdo('keyup','w')
                    check('crafting_does_not_queue_held_movement',latest()['target_x']==r['target_x'] and latest()['target_z']==r['target_z'])
                    view=open_crafting();frozen=latest()['crafting_progress'];time.sleep(.7)
                    check('menu_freezes_native_craft_counter',latest()['crafting_progress']==frozen)
                    shot('crafting-paused.png');modal_start=len(rows());sent_before_cancel=latest()['crafting_sent'];click(11.5,2.2)
                    wait(lambda r:int(r['crafting_token'])==0 and int(r['pending_move'])==0)
                    view=open_crafting();view=search();e=select_recipe(view,True)
                    if args.modal_continuity:
                        span=rows()[modal_start:]
                        check('craft_interruption_keeps_modal_and_native_incomplete',len(span)>5 and all(int(r['modal_count'])>0 for r in span))
                    # MENU_CLOSE permits native time before the typed cancel is
                    # admitted. A final paid turn may advance the real craft;
                    # cancelling must retain that work, never restore the UI's
                    # previously paused counter or start a new craft.
                    check('interrupted_work_is_native_resumable_item',e.Resume() and int(frozen)<=e.Progress()<10000000)
                    check('interruption_retains_native_progress_without_new_craft',latest()['crafting_sent']==sent_before_cancel)
                    shot('incomplete-work.png')
                    sent = latest()['crafting_sent']; index = e.Id() - 1
                    click(.5+(index%6)*1.18+.825,2.7+(index//6)*1.12+.225)
                    check('resume_badge_selects_without_starting_work',latest()['crafting_sent']==sent and int(latest()['crafting_selected'])==e.Id() and int(latest()['crafting_form'])==1)
                    start()
                    # Wielded craft resumes without a material/confirmation prompt.
                    wait(lambda r:int(r['pending_move'])==0)
                    check('resumed_work_has_fresh_token',latest()['crafting_token']!=token)
                wait(lambda r:int(r['crafting_token'])==0,timeout=30)
                check('batch_native_craft_completes',True)
                view=open_crafting();view=search();select_recipe(view)
                if not args.action_driven:
                    tap('Escape');wait(lambda r:int(r['crafting_form'])==0)
                    tap('F7');wait(lambda r:int(r['pause_reasons'])==1)
                    view=open_crafting();view=search();select_recipe(view);sent=latest()['crafting_sent'];click(11.5,9.325);time.sleep(.5)
                    check('manually_paused_start_is_not_queued',latest()['crafting_sent']==sent and int(latest()['crafting_form'])==1)
                    tap('Escape');wait(lambda r:int(r['crafting_form'])==0);tap('F7');wait(lambda r:int(r['pause_reasons'])==0)
                    view=open_crafting()
                connection=latest()['connection_id'];sent=latest()['crafting_sent'];drop.set()
                wait(lambda r:r['connection_id']!=connection and int(r['input_ready'])==1 and int(r['crafting_form'])==0,timeout=20)
                check('recovery_discards_old_recipe_selection',latest()['crafting_sent']==sent)
                view=open_crafting();view=search();check('recovery_restores_available_recipe',not next(e for e in entries(view) if e.RecipeId()==b'bandages_makeshift' and not e.Resume()).Reason())
                if args.save_active:
                    view=set_batch(2);select_recipe(view);start();choose(approve=True)
                    wait(lambda r:int(r['crafting_token'])>0);view=open_crafting();shot('save-active-craft.png')
                    check('shutdown_keeps_native_incomplete_work',0<int(latest()['crafting_progress'])<10000000)
                else:
                    tap('Escape');wait(lambda r:int(r['crafting_form'])==0)
                check('actual_runtime_survives_native_crafting',proc.poll() is None)
        finally:
            shutting_down.set() # Resets caused by our SIGTERM are expected only after this boundary.
            subprocess.run(['xdotool', 'keyup', 'w'], capture_output=True)
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
    check('crafting_save_readable_by_pristine_native_core', result.returncode == 0)
    native=json.loads(output.read_text())
    def live_items(value):
        # Components of a craft/result are consumed provenance, not additional live objects.
        if isinstance(value,dict):
            if 'typeid' in value: yield value
            for key,child in value.items():
                if key not in ('components','comps_used'): yield from live_items(child)
        elif isinstance(value,list):
            for child in value:yield from live_items(child)
    items=list(live_items(native['player']))
    favorite=[it for it in items if it.get('item_vars',{}).get('uid')=='crafting-favorite']
    check('favorite_component_preserved_by_native_save',len(favorite)==1 and favorite[0].get('is_favorite',False))
    crafts=[it for it in items if it['typeid']=='craft']
    bandages=[it for it in items if it['typeid']=='bandages_makeshift']
    # First craft produces 2, batch 2 produces 4; optional saved second batch adds 4 on resume.
    count=sum(it.get('charges',1) if it.get('charges',0)>0 else 1 for it in bandages)
    check('native_results_created_exactly_once',count==(10 if args.resume_active else 6))
    activity=native['player']['activity']
    if args.save_active:
        check('canonical_save_contains_native_craft_actor',activity['type']=='ACT_CRAFT' and len(crafts)==1)
        check('canonical_incomplete_work_keeps_counter_and_recipe',0<crafts[0]['item_counter']<10000000)
    else:
        check('completed_work_removes_native_craft_item',activity['type']=='ACT_NULL' and not crafts)
    check('canonical_crafting_save_has_no_luanti_inventory',not any('luanti' in key.lower() for key in native['player']))
    if args.recipe_shortcuts:
        state=json.loads((user/'save/audit_fixture/uistate.json').read_text())
        check('native_uistate_persists_favorite_recipe','bandages_makeshift' in state['favorite_recipes'])
        check('native_uistate_has_unique_native_recency',state['recent_recipes'][-1]=='bandages_makeshift' and state['recent_recipes'].count('bandages_makeshift')==1 and len(state['recent_recipes'])<=20)
    (out/'summary.json').write_text(json.dumps(dict(checks=checks,native_save=str(output)),indent=2)+'\n')


if __name__ == '__main__':
    main()
