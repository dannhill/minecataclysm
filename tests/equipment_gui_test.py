#!/usr/bin/env python3
"""Exercise the native inventory and equipment in the actual Luanti renderer.

Requires an independently created --create-equipment fixture, X11, xdotool,
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
    parser.add_argument('--presentation-only', action='store_true', help='Exercise paging, layering and search without gameplay mutations')
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
                assert options and options[-1] == 'Cancel' and len(options) <= 9, options
                return str(len(options))
            def open_inventory():
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
                wait(lambda r: int(r['equipment_form']) == 0 and int(r['equipment_sent']) == sent+1)
            def finish_action():
                wait(lambda r: int(r['pending_move']) == 0 and int(r['pause_reasons']) == 0)
            def item(v, name):
                return next(e for e in entries(v) if e.TypeId().decode() == name)
            if args.presentation_only:
                es = entries(view)
                check('native_fixture_exceeds_grid_and_worn_pages',len(es)>27 and sum(e.Worn() for e in es)>10)
                paused=latest();sent=paused['equipment_sent']
                click(10.35,9.2);select_item(es[27]);shot('page-two.png')
                check('page_two_selects_exact_native_identity', int(latest()['equipment_selected'])==es[27].Id())
                click(1.025,10.025);wait(lambda r:int(r['equipment_selected'])==es[0].Id())
                check('quick_row_only_selects_existing_identity',latest()['equipment_sent']==sent)
                click(10.45,1.6)
                layer=[e for e in es if e.Worn()][10]
                click(5.225,2.575);wait(lambda r:int(r['equipment_selected'])==layer.Id())
                check('layer_beyond_ten_slots_is_accessible', True);shot('layer-page-two.png')
                # Native IDs are reset on every fresh query, while the viewport is retained.
                old_view=latest()['inventory_view'];click(12.35,1.25)
                wait(lambda r:r['inventory_view']!=old_view and int(r['inventory_view'])>0)
                check('refresh_invalidates_selection',int(latest()['equipment_selected'])==0)
                select_item(es[27]);shot('refresh-page-two.png')
                tap('Escape');wait(lambda r:int(r['equipment_form'])==0)
                view=open_inventory();es=entries(view)
                select_item(es[27]);check('reopening_preserves_page_with_fresh_handles',int(latest()['equipment_selected'])==es[27].Id())
                # Search focuses only after the explicit opening click.
                click(4.9,4.95);xdo('type','--clearmodifiers','bandana');click(6.5,4.95)
                filtered=[e for e in es if b'bandana' in e.Name().lower()]
                click(1.025,5.975);wait(lambda r:int(r['equipment_selected'])==filtered[0].Id())
                check('explicit_search_focus_selects_native_filtered_item',True);shot('optional-search.png')
                tap('Escape');time.sleep(.3)
                check('first_escape_returns_to_grid_with_pause',int(latest()['equipment_form'])==1 and latest()['simulation_time']==paused['simulation_time'])
                click(8.5,4.95) # Remove the applied search; reset page.
                pack=next(e for e in es if e.TypeId()==b'backpack_hiking')
                select_item(pack);shot('compact-container.png');click(13.4,7.45);shot('expanded-container.png')
                check('details_do_not_execute_native_actions',latest()['equipment_sent']==sent)
                click(1.5,4.95);xdo('key','Home');xdo('key','Down');xdo('key','Down');xdo('key','Return');time.sleep(.3)
                click(1.025,5.975);wait(lambda r:int(r['equipment_selected'])==pack.Id())
                shot('container-filter.png');check('container_filter_keeps_native_container_identity',True)
                click(13.5,.5);wait(lambda r:int(r['transfer_form'])==1);click(9.7,.5);wait(lambda r:int(r['transfer_form'])==0)
                tap('Escape');wait(lambda r:int(r['equipment_form'])==0)
                view=open_inventory();click(1.025,5.975);wait(lambda r:int(r['equipment_selected'])==pack.Id())
                check('reopen_preserves_filter',True)
                tap('Escape');wait(lambda r:int(r['equipment_form'])==0)
                check('browse_never_issues_equipment_command',latest()['equipment_sent']==sent)
            elif args.resume_only:
                check('actual_reload_keeps_native_weapon_and_backpack', item(view,'rock').Wielded() and item(view,'backpack_hiking').Worn())
                check('actual_reload_keeps_nested_contents_once', view.EntriesLength() == 6 and item(view,'hat_ball').ParentId() > 0)
                tap('Escape');wait(lambda r: int(r['equipment_form']) == 0)
            else:
                opened = latest()
                check('nested_objects_and_pockets_are_native', view.PocketsLength() > 0 and item(view,'hat_ball').ParentId() > 0)
                check('two_identical_items_have_distinct_selection_ids', len({e.Id() for e in entries(view) if e.TypeId() == b'rock'}) == 2)
                time.sleep(1)
                xdo('keydown','w');time.sleep(.4);xdo('keyup','w');time.sleep(.3)
                check('inventory_reading_freezes_native_time', latest()['simulation_time'] == opened['simulation_time'])
                check('inventory_reading_does_not_move_player', latest()['target_x'] == opened['target_x'] and latest()['target_z'] == opened['target_z'])
                check('survival_hud_hidden_behind_inventory', int(latest()['survival_visible']) == 0)
                check('inventory_freezes_presentation_animation', latest()['visual_animation_time'] == opened['visual_animation_time'] and float(latest()['visual_animation_delta']) == 0)
                click(4.9,4.95);time.sleep(.2);xdo('key','ctrl+a');xdo('key','BackSpace'); xdo('type','--delay','80','cap'); time.sleep(.4); click(6.5,4.95); shot('search-filter.png')
                cap = item(view,'hat_ball'); click(1.025,5.975)
                wait(lambda r: int(r['equipment_selected']) == cap.Id())
                check('search_preserves_native_item_selection', True)
                click(2.2,4.95);xdo('key','ctrl+a');xdo('key','BackSpace');click(6.5,4.95)
                tap('Escape');time.sleep(.3)
                check('escape_leaves_search_keeps_inventory_paused', int(latest()['equipment_form']) == 1 and int(latest()['pause_reasons']) == 2)
                select_item(item(view,'hat_ball'));shot('hat-details.png')
                action(2);finish_action()
                view = open_inventory()
                check('wear_cap_native_result_visible', item(view,'hat_ball').Worn() and not item(view,'hat_ball').ParentId())
                select_item(item(view,'hat_ball'));action(3);finish_action()
                view = open_inventory()
                check('takeoff_cap_returns_to_native_pocket', not item(view,'hat_ball').Worn() and item(view,'hat_ball').ParentId() > 0)
                select_item(item(view,'bat'));action(1)
                wait(lambda r: int(r['pending_decision']) > 0)
                shot('native-stow-choice.png')
                tap(cancel_choice());finish_action()
                view = open_inventory()
                check('native_stow_cancel_keeps_weapon_wielded', item(view,'bat').Wielded())
                select_item(item(view,'bat'));action(1)
                wait(lambda r: int(r['pending_decision']) > 0)
                tap('1');finish_action()
                view = open_inventory()
                check('native_stow_keeps_bat_owned_without_wielding', not item(view,'bat').Wielded())
                select_item(item(view,'rock'));action(0);finish_action()
                view = open_inventory()
                check('wield_uses_selected_native_item', item(view,'rock').Wielded())
                select_item(item(view,'rock'));action(1)
                wait(lambda r: int(r['pending_decision']) > 0);tap('1');finish_action()
                view = open_inventory()
                select_item(item(view,'backpack_hiking'));action(3);finish_action()
                view = open_inventory()
                check('taking_off_loaded_backpack_retains_all_contents', item(view,'backpack_hiking').Wielded() and not item(view,'backpack_hiking').Worn() and view.EntriesLength() == 6 and item(view,'hat_ball').ParentId() > 0)
                select_item(item(view,'backpack_hiking'));action(2);finish_action()
                view = open_inventory()
                check('wearing_loaded_backpack_retains_all_contents', item(view,'backpack_hiking').Worn() and view.EntriesLength() == 6)
                select_item(item(view,'rock'));action(0);finish_action()
                view = open_inventory()
                tap('Escape');wait(lambda r: int(r['equipment_form']) == 0)
                check('escape_closes_inventory', True)
                if not args.action_driven:
                    tap('F7');wait(lambda r: int(r['pause_reasons']) == 1)
                    view = open_inventory();select_item(item(view,'hat_ball'))
                    sent = latest()['equipment_sent'];stopped = latest()['simulation_time']
                    click(12.325,8.9);time.sleep(.5)
                    check('manual_pause_blocks_equipment_without_queuing', latest()['equipment_sent'] == sent and int(latest()['equipment_form']) == 1)
                    tap('Escape');wait(lambda r: int(r['equipment_form']) == 0 and int(r['pause_reasons']) == 1)
                    check('closing_inventory_preserves_manual_pause', latest()['simulation_time'] == stopped)
                    tap('F7');wait(lambda r: int(r['pause_reasons']) == 0)
                    check('unpause_does_not_execute_rejected_click', latest()['equipment_sent'] == sent)
                view = open_inventory()
                connection_id = latest()['connection_id'];sent = latest()['equipment_sent']
                drop.set()
                wait(lambda r: r['connection_id'] != connection_id and int(r['input_ready']) == 1 and int(r['equipment_form']) == 0, timeout=20)
                check('real_reconnect_closes_stale_inventory', True)
                check('reconnect_never_replays_unsent_equipment', latest()['equipment_sent'] == sent)
                view = open_inventory()
                check('resync_restores_native_equipment', item(view,'rock').Wielded() and item(view,'backpack_hiking').Worn())
                tap('Escape');wait(lambda r: int(r['equipment_form']) == 0)
                check('actual_runtime_survives', proc.poll() is None)
        finally:
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
    check('equipment_save_readable_by_pristine_native_core', result.returncode == 0)
    native = json.loads(output.read_text())
    before = json.loads((args.fixture.parent / ('native.json' if args.resume_only else 'before.json')).read_text())
    def uid_counts(value, counts=None):
        counts = {} if counts is None else counts
        if isinstance(value, dict):
            uid = value.get('item_vars', {}).get('uid')
            if uid and uid.startswith('equipment-'): counts[uid] = counts.get(uid,0)+1
            for child in value.values(): uid_counts(child,counts)
        elif isinstance(value,list):
            for child in value: uid_counts(child,counts)
        return counts
    check('canonical_save_has_each_fixture_item_once', uid_counts(native['player']) == uid_counts(before['player']) and len(uid_counts(native['player'])) == (51 if args.presentation_only else 5))
    check('canonical_save_records_selected_rock_as_weapon', native['player']['weapon']['typeid'] == ('bat' if args.presentation_only else 'rock'))
    check('canonical_save_records_backpack_worn', any(i['typeid'] == 'backpack_hiking' for i in native['player']['worn']['worn']))
    if args.presentation_only:
        check('readonly_inventory_preserves_canonical_items',native['player']['worn']==before['player']['worn'] and native['player']['weapon']==before['player']['weapon'])
    if args.resume_only:
        check('actual_reload_preserves_canonical_position', native['player_abs'] == before['player_abs'])
        if args.action_driven:
            check('readonly_reload_inventory_consumes_no_native_time', native['time'] == before['time'])
    (out / 'summary.json').write_text(json.dumps(dict(checks=checks, native_save=str(output)), indent=2)+'\n')


if __name__ == '__main__':
    main()
