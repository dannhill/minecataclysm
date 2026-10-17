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
import struct


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('workspace', 'fixture', 'native-reader', 'artifacts'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--action-driven', action='store_true', help='Verify ordinary start.sh mode without the real-time scheduler')
    parser.add_argument('--resume-only', action='store_true')
    parser.add_argument('--drag-equipment', action='store_true')
    parser.add_argument('--sequential', action='store_true', help='Exercise UX-02 paid completion and automatic return')
    parser.add_argument('--native-equipment-time', action='store_true', help='Atomic clothing, inspection during delayed ACK, frozen/resumed native debit')
    parser.add_argument('--quickbar', action='store_true', help='Verify UX-03 shortcuts, focus, native costs, pause and persistence')
    parser.add_argument('--quickbar-resume', action='store_true', help='Verify the saved UX-03 shortcut identities after actual reload')
    parser.add_argument('--presentation-only', action='store_true', help='Exercise paging, layering and search without gameplay mutations')
    parser.add_argument('--language-smoke', choices=('en', 'it'), help='Check native localization and capture the real translated renderer')
    parser.add_argument('--language-menu-change', choices=('en', 'it'), help='Change the actual pause-menu language preference before exiting')
    parser.add_argument('--use-saved-language', action='store_true', help='Verify launcher preference resolution without a language environment override')
    args = parser.parse_args()
    ws, out = args.workspace.resolve(), args.artifacts.resolve()
    sys.path.insert(0, str(ws / 'tools'))
    out.mkdir(parents=True, exist_ok=False)
    user = out / 'user'
    shutil.copytree(args.fixture.resolve(), user)
    native_options = user / 'config/options.json'
    native_options.write_text(json.dumps([
        {'name': 'SAFEMODE', 'value': 'false'}, {'name': 'AUTOSAFEMODE', 'value': 'false'},
        {'name': 'AUTOSAVE', 'value': 'false'}] +
        ([{'name': 'USE_LANG', 'value': 'it_IT'}] if args.language_smoke else [])))
    native_options_before = native_options.read_bytes()
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
    env.pop('CDDA_LANGUAGE', None)
    if args.language_smoke and not args.use_saved_language:
        env['CDDA_LANGUAGE'] = args.language_smoke
    if args.quickbar or args.quickbar_resume:
        env.pop('CDDA_CONTINUOUS', None) # Verify the actual launcher default, not a demo override.
    if args.action_driven:
        env['CDDA_CONTINUOUS'] = '0'
        env.pop('CDDA_REALTIME', None)
    # A byte-transparent local relay lets the real client lose IPC while a
    # selection is queued under manual pause. Gameplay still runs in CDDA.
    scratch = tempfile.TemporaryDirectory(prefix='cwm-body-gui-')
    relay_path = Path(scratch.name) / 'relay.sock'
    native_path = out / 'native-socket'
    stop, drop = threading.Event(), threading.Event()
    hold_server = threading.Event()
    hold_equipment_reply = threading.Event()
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
                    delayed_server = bytearray()
                    client_frames = bytearray()
                    while not stop.is_set():
                        if drop.is_set():
                            drop.clear()
                            break
                        if delayed_server and not hold_server.is_set():
                            client_socket.sendall(delayed_server)
                            delayed_server.clear()
                        readable, _, _ = select.select([client_socket, server_socket], [], [], .03)
                        closed = False
                        for source in readable:
                            data = source.recv(1 << 20)
                            if not data:
                                closed = True
                                break
                            with (out / ('client-wire.bin' if source is client_socket else 'server-wire.bin')).open('ab') as capture:
                                capture.write(data)
                            if source is client_socket:
                                client_frames.extend(data)
                                while len(client_frames)>=4:
                                    size=struct.unpack('>I',client_frames[:4])[0]
                                    if len(client_frames)<size+4:break
                                    if hold_equipment_reply.is_set() and CwmMessage.GetRootAs(client_frames[4:size+4]).PayloadType()==Payload.EquipmentRequest:
                                        hold_server.set();hold_equipment_reply.clear()
                                    del client_frames[:size+4]
                            if source is server_socket and (hold_server.is_set() or delayed_server):
                                delayed_server.extend(data)
                            else:
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
        f"Path({str(out / 'actual-client-config-path')!r}).write_text(str(p))\n" +
        f"p.write_text(s+'\\ncwm_socket_path = {relay_path}\\n')\n" +
        f"Path({str(out / 'relay-client.conf')!r}).write_text(p.read_text())\n" +
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
                from CDDA.CWM.DecisionPrompt import DecisionPrompt
                buf = (out / 'server-wire.bin').read_bytes(); offset = 0; options = []
                while offset + 4 <= len(buf):
                    n = struct.unpack('>I',buf[offset:offset+4])[0]; offset += 4
                    if offset + n > len(buf): break
                    msg = CwmMessage.GetRootAs(buf[offset:offset+n]); offset += n
                    if msg.PayloadType() == Payload.DecisionPrompt:
                        prompt = DecisionPrompt();prompt.Init(msg.Payload().Bytes,msg.Payload().Pos)
                        options = [prompt.Choices(i).decode() for i in range(prompt.ChoicesLength())]
                assert options and options[-1] == ('Annulla' if args.language_smoke == 'it' else 'Cancel') and len(options) <= 9, options
                return str(len(options))
            def open_inventory():
                if int(latest()['equipment_form']) == 1 and int(latest()['inventory_view']) > 0:
                    time.sleep(.4); xdo('windowactivate','--sync',window)
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
                if e.QuickSlot():
                    click(1.025+(e.QuickSlot()-1)*1.15,10.025)
                else:
                    visible=[view.Entries(n) for n in range(view.EntriesLength()) if not view.Entries(n).QuickSlot()]
                    visible.sort(key=lambda x:x.UiOrder() or 4096+x.Id())
                    index=next(n for n,x in enumerate(visible) if x.Id()==e.Id())
                    click(1.025 + (index % 9)*1.15, 5.975 + ((index % 27) // 9)*1.15)
                wait(lambda r: int(r['equipment_selected']) == e.Id())
            def drag(source,target,cancel=False,screenshot=None):
                def move(xy):
                    xdo('mousemove','--window',window,str(round(origin_x+xy[0]*unit)),str(round(origin_y+xy[1]*unit)))
                move(source);xdo('mousedown','1');time.sleep(.15)
                for n in range(1,8):
                    move((source[0]+(target[0]-source[0])*n/7,source[1]+(target[1]-source[1])*n/7));time.sleep(.04)
                if screenshot:shot(screenshot)
                if cancel:tap('Escape')
                xdo('mouseup','1');time.sleep(.4)
            def cell(e):
                if e.QuickSlot():return (1.025+(e.QuickSlot()-1)*1.15,10.025)
                visible=[view.Entries(n) for n in range(view.EntriesLength()) if not view.Entries(n).QuickSlot()]
                visible.sort(key=lambda x:x.UiOrder() or 4096+x.Id())
                index=next(n for n,x in enumerate(visible) if x.Id()==e.Id())
                return (1.025+(index%9)*1.15,5.975+((index%27)//9)*1.15)
            def action(number):
                sent = int(latest()['equipment_sent'])
                click(12.325 + (number % 2)*2.2, 8.15 + (number // 2)*.75)
                wait(lambda r: int(r['equipment_sent']) == sent+1)
                # Esc now answers the native modal. Never use it as an implicit
                # opt-out while a question is opening; inspect real settlement.
                wait(lambda r: int(r['equipment_form']) == 0 or
                     (int(r['native_work_settled']) == 1 and int(r['pending_move']) == 0))
            def finish_action():
                wait(lambda r: int(r['pending_move']) == 0 and (int(r['pause_reasons']) == 0 or
                     (int(r['equipment_form']) == 1 and int(r['native_work_settled']) == 1)))
            def item(v, name):
                return next(e for e in entries(v) if e.TypeId().decode() == name)
            if args.language_smoke:
                language = args.language_smoke
                from CDDA.CWM.WorldSnapshot import WorldSnapshot
                buf=(out/'server-wire.bin').read_bytes();offset=0;status=None
                while offset+4<=len(buf):
                    size=struct.unpack('>I',buf[offset:offset+4])[0];offset+=4
                    if offset+size>len(buf):break
                    msg=CwmMessage.GetRootAs(buf[offset:offset+size]);offset+=size
                    if msg.PayloadType()==Payload.WorldSnapshot:
                        state=WorldSnapshot();state.Init(msg.Payload().Bytes,msg.Payload().Pos)
                        if state.AvatarStatus():status=state.AvatarStatus()
                check('integration_status_labels_use_selected_language', status is not None and
                      next(status.Needs(n).Label().decode() for n in range(status.NeedsLength())
                           if status.Needs(n).Id()==b'thirst') == ('Sete' if language=='it' else 'Thirst'))
                check('native_item_name_uses_selected_catalog', item(view,'hat_ball').Name().decode() ==
                      '++\u00a0' + ('cappello da baseball' if language == 'it' else 'baseball cap'))
                check('native_nested_backpack_name_uses_selected_catalog', item(view,'backpack_hiking').Name().decode().startswith(
                      '++\u00a0' + ('zaino da escursione' if language == 'it' else 'hiking backpack') + ' > '))
                check('native_category_ids_are_language_independent',
                      item(view,'hat_ball').Category()==b'clothing' and
                      item(view,'backpack_hiking').Category()==b'clothing' and
                      item(view,'bat').Category()==b'weapons')
                select_item(item(view,'hat_ball')); shot('translated-item-details.png')
                click(9.5,4.95);xdo('key','Home');xdo('key','Down');xdo('key','Down');xdo('key','Return');time.sleep(.3)
                click(1.025,5.975)
                wait(lambda r:int(r['equipment_selected'])==item(view,'backpack_hiking').Id())
                check('translated_filter_resolves_semantic_container_selection',True)
                click(9.5,4.95);xdo('key','Home');xdo('key','Return');time.sleep(.3)
                # Match field values produced by the actual launcher, not the test base config.
                translated_config = (out / 'relay-client.conf').read_text()
                check('actual_launcher_selects_same_language_in_renderer',
                      f'\ncwm_language = {language}\nlanguage = {language}\n' in translated_config)
                frozen = latest()['simulation_time']
                time.sleep(.4)
                check('localized_inventory_remains_read_only_and_paused', latest()['simulation_time'] == frozen)
                tap('Escape');wait(lambda r:int(r['equipment_form'])==0)
                tap('h');wait(lambda r:int(r['body_form'])==1);shot('translated-body.png')
                tap('Escape');wait(lambda r:int(r['body_form'])==0)
                tap('k');wait(lambda r:int(r['crafting_form'])==1 and int(r['crafting_view'])>0)
                shot('translated-crafting.png')
                tap('Escape');wait(lambda r:int(r['crafting_form'])==0)
                view=open_inventory();select_item(item(view,'bat'));action(1)
                wait(lambda r:int(r['pending_decision'])>0);shot('translated-native-choice.png')
                choice = cancel_choice()
                check('native_decision_cancel_uses_selected_catalog', True)
                tap(choice);finish_action()
                view=open_inventory()
                check('localized_native_cancel_preserves_wielded_item', item(view,'bat').Wielded())
                tap('Escape');wait(lambda r:int(r['equipment_form'])==0)
                if args.language_menu_change:
                    tap('Escape');wait(lambda r:int(r['pause_reasons'])==2)
                    paused_time=latest()['simulation_time']
                    shot('pause-language-selector.png')
                    # Fixed-size v1 pause form on the controlled 96-DPI display.
                    xdo('mousemove','--window',window,'875', '365' if args.language_menu_change == 'it' else '320');xdo('click','1');time.sleep(.4)
                    from product_language import configured_language
                    actual_config = Path((out / 'actual-client-config-path').read_text())
                    check('real_pause_menu_updates_product_preference',
                          configured_language(actual_config)==args.language_menu_change)
                    check('language_preference_is_free_and_keeps_simulation_paused',
                          latest()['simulation_time']==paused_time)
                    shot('pause-language-selected.png')
                    tap('Escape');wait(lambda r:int(r['pause_reasons'])==0)
                    view=open_inventory()
                    check('menu_change_keeps_current_native_language_until_restart',
                          item(view,'hat_ball').Name().decode() == '++\u00a0' + ('cappello da baseball' if language == 'it' else 'baseball cap'))
                    tap('Escape');wait(lambda r:int(r['equipment_form'])==0)
            elif args.quickbar or args.quickbar_resume:
                from CDDA.CWM.WorldSnapshot import WorldSnapshot
                def states():
                    buf=(out/'server-wire.bin').read_bytes();offset=0;found=[]
                    while offset+4<=len(buf):
                        n=struct.unpack('>I',buf[offset:offset+4])[0];offset+=4
                        if offset+n>len(buf):break
                        msg=CwmMessage.GetRootAs(buf[offset:offset+n]);offset+=n
                        if msg.PayloadType()==Payload.WorldSnapshot:
                            s=WorldSnapshot();s.Init(msg.Payload().Bytes,msg.Payload().Pos);found.append(s)
                    return found
                def slot(n):
                    return states()[-1].QuickSlots(n-1)
                def bind(type_id,n):
                    nonlocal view
                    chosen=item(view,type_id)
                    old=int(latest()['quick_bind_command']);old_view=latest()['inventory_view']
                    drag(cell(chosen),(1.025+(n-1)*1.15,10.025))
                    wait(lambda r:int(r['quick_bind_command'])>old)
                    wait(lambda r:int(r['pending_move'])==0 and int(r['inventory_view'])>0 and r['inventory_view']!=old_view)
                    view=views()[-1]
                    check('slot_'+str(n)+'_references_exact_native_'+type_id,slot(n).TypeId()==type_id.encode() and len(slot(n).BindingId())==32)
                check('normal_launcher_defaults_to_continuous_4x',int(latest()['continuous_motion'])==1 and float(latest()['time_scale'])==4)
                if args.quickbar:
                    check('fresh_quickbar_has_no_implicit_first_nine_items',int(latest()['quick_count'])==0)
                    # A visible field must not capture keyboard input before a click.
                    xdo('type','--clearmodifiers','cap');click(6.5,4.95)
                    select_item(item(view,'rock'))
                    check('search_initially_visible_without_keyboard_focus',True)
                    click(2,4.95);xdo('type','--clearmodifiers','cap');click(6.5,4.95)
                    click(1.025,5.975);wait(lambda r:int(r['equipment_selected'])==item(view,'hat_ball').Id())
                    check('click_focus_enables_search',True)
                    # Clicking elsewhere must blur even on a non-input background.
                    click(10.8,4.2);xdo('type','--clearmodifiers','zzzz');click(6.5,4.95)
                    click(1.025,5.975);wait(lambda r:int(r['equipment_selected'])==item(view,'hat_ball').Id())
                    check('background_click_disables_search_keyboard_input',True)
                    click(7.7,4.95)
                    paused=latest()['simulation_time']
                    old=latest()['inventory_view']
                    rock=item(view,'rock');bat=item(view,'bat')
                    drag(cell(rock),cell(bat),cancel=True)
                    check('escape_cancels_drag_without_closing_or_mutating',latest()['inventory_view']==old and int(latest()['equipment_form'])==1 and int(latest()['pending_move'])==0)
                    sent=latest()['transfers_sent'];equipped=latest()['equipment_sent']
                    drag(cell(rock),(-.5,-.5),cancel=True)
                    check('escape_cancels_outside_drag_without_ground_drop',latest()['inventory_view']==old and latest()['transfers_sent']==sent and latest()['equipment_sent']==equipped and latest()['simulation_time']==paused)
                    old_view=latest()['inventory_view']; layout_start=len(rows())
                    drag(cell(rock),cell(bat),screenshot='drag-ghost-and-target.png')
                    wait(lambda r:int(r['pending_move'])==0 and int(r['inventory_view'])>0 and r['inventory_view']!=old_view)
                    view=views()[-1]
                    check('layout_query_keeps_previous_grid_visible',all(int(r['equipment_form'])==1 and int(r['inventory_view'])>0 for r in rows()[layout_start:]))
                    check('drag_grid_order_is_persistent_native_ui_metadata',item(view,'rock').UiOrder()<item(view,'bat').UiOrder() and latest()['simulation_time']==paused)
                    bind('bat',1);bind('hat_ball',2);bind('rock',3)
                    check('assignment_preserves_native_time_and_hand',latest()['simulation_time']==paused and slot(1).Wielded() and not slot(3).Wielded())
                    old_view=latest()['inventory_view'];a=slot(2).BindingId();b=slot(3).BindingId()
                    drag((2.175,10.025),(3.325,10.025))
                    wait(lambda r:int(r['pending_move'])==0 and int(r['inventory_view'])>0 and r['inventory_view']!=old_view)
                    view=views()[-1]
                    check('drag_occupied_hotbar_swaps_both_exact_instances_atomically',slot(2).BindingId()==b and slot(3).BindingId()==a)
                    old_view=latest()['inventory_view'];drag((2.175,10.025),(3.325,10.025))
                    wait(lambda r:int(r['pending_move'])==0 and int(r['inventory_view'])>0 and r['inventory_view']!=old_view)
                    view=views()[-1]
                    shot('assigned-quickbar.png')
                    # Clear a bookmark, preserving its real item and the real hand.
                    old_view=latest()['inventory_view'];drag((1.025,10.025),(10.225,8.275))
                    wait(lambda r:int(r['pending_move'])==0 and r['inventory_view']!=old_view and int(r['inventory_view'])>0)
                    view=views()[-1]
                    check('clear_removes_reference_without_removing_item',not slot(1).BindingId() and item(view,'bat').Wielded() and int(latest()['quick_count'])==2)
                    tap('Escape');wait(lambda r:int(r['equipment_form'])==0)
                    before=latest()['quick_use_sent'];tap('3');time.sleep(.5)
                    check('slot_selection_does_not_equip_or_use',latest()['quick_use_sent']==before and int(latest()['quick_wielded'])==0)
                    tap('g');wait(lambda r:int(r['pending_decision'])>0)
                    check('quick_wield_retains_native_disposal_choice',int(latest()['equipment_form'])==0)
                    tap('1') # Explicit native Store in inventory, no production auto-confirm.
                    wait(lambda r:int(r['native_work_settled'])==1 and int(r['pending_move'])==0,timeout=25)
                    check('quick_wield_preserves_binding_and_pays_native_time',slot(3).Wielded() and int(latest()['quick_wielded'])==3 and int(latest()['simulation_time'])>int(paused))
                    # Deliver number and use in the same frame: use the new slot.
                    xdo('keydown','2','g');time.sleep(.2);xdo('keyup','2','g')
                    wait(lambda r:int(r['native_work_settled'])==1 and int(r['pending_move'])==0 and slot(2).Worn(),timeout=25)
                    check('quick_clothing_uses_native_wear',slot(2).Worn())
                    work=[state.InventoryWork() for state in states() if state.InventoryWork() and state.InventoryWork().TotalTimeMs()]
                    check('synchronous_equipment_exports_native_pacing_progress',bool(work) and all(0<=w.RemainingTimeMs()<=w.TotalTimeMs() for w in work) and any(not w.Settled() and w.RemainingTimeMs()>0 for w in work))
                    check('same_frame_slot_and_use_targets_new_selection',int(latest()['quick_slot'])==2 and slot(2).Worn())
                    check('world_quick_use_does_not_force_inventory',int(latest()['equipment_form'])==0)
                    tap('F7');wait(lambda r:int(r['pause_reasons'])&1)
                    sent=latest()['quick_use_sent'];paused=latest()['simulation_time'];tap('g');time.sleep(.5)
                    check('paused_quick_use_is_not_sent',latest()['quick_use_sent']==sent and latest()['simulation_time']==paused)
                    tap('F7');wait(lambda r:int(r['pause_reasons'])==0);time.sleep(.6)
                    check('paused_quick_key_does_not_replay_on_resume',latest()['quick_use_sent']==sent and slot(2).Worn())
                    tap('3');shot('hud-selected-hand.png')
                    connection=latest()['connection_id'];drop.set()
                    wait(lambda r:r['connection_id']!=connection and int(r['input_ready'])==1,timeout=25)
                    check('reconnect_restores_native_shortcut_identities',slot(2).Worn() and slot(3).Wielded() and int(latest()['quick_count'])==2)
                else:
                    check('actual_reload_restores_bookmarks_not_inventory_order',not slot(1).BindingId() and slot(2).TypeId()==b'hat_ball' and slot(2).Worn() and slot(3).TypeId()==b'rock' and slot(3).Wielded())
                    check('reloaded_items_use_exact_saved_binding_ids',item(view,'hat_ball').QuickSlot()==2 and item(view,'rock').QuickSlot()==3)
                    check('actual_reload_retains_grid_order_on_exact_instances',0<item(view,'rock').UiOrder()<item(view,'bat').UiOrder())
                    shot('reloaded-shortcuts.png');tap('Escape');wait(lambda r:int(r['equipment_form'])==0)
                view=open_inventory();check('quickbar_changes_leave_native_contents_intact',view.EntriesLength()==6 and item(view,'backpack_hiking').Worn())
                # Stop in read-only I before closing the isolated runtime.
            elif args.drag_equipment:
                paused=latest()['simulation_time']
                def paid_drag(source,target,decision=False):
                    nonlocal view
                    previous=latest()['inventory_view'];sent=int(latest()['equipment_sent'])
                    drag(source,target)
                    wait(lambda r:int(r['equipment_sent'])==sent+1)
                    if decision:
                        wait(lambda r:int(r['pending_decision'])>0);tap('1')
                    wait(lambda r:int(r['equipment_form'])==1 and int(r['inventory_view'])>0 and r['inventory_view']!=previous and int(r['native_work_settled'])==1,timeout=25)
                    shot('drag-paid-return.png');view=views()[-1]
                paid_drag(cell(item(view,'hat_ball')),(6.425,2.575))
                check('drag_into_wear_area_runs_native_wear',item(view,'hat_ball').Worn())
                worn=[e for e in entries(view) if e.Worn()]
                index=next(n for n,e in enumerate(worn) if e.TypeId()==b'hat_ball')
                paid_drag((5.225+(index%5)*1.2,2.575+(index//5)*1.15),(10.225,8.275))
                check('drag_worn_to_grid_runs_native_takeoff',not item(view,'hat_ball').Worn())
                paid_drag((1.025,2.575),(10.225,8.275),decision=True)
                check('drag_hand_to_grid_runs_native_stow',not any(view.Entries(n).Wielded() for n in range(view.EntriesLength())))
                paid_drag(cell(item(view,'rock')),(1.025,2.575))
                check('drag_into_hand_runs_native_wield',item(view,'rock').Wielded())
                check('physical_drags_pay_native_time',int(latest()['simulation_time'])>int(paused))
                shot('drag-final-equipment.png')
            elif args.native_equipment_time:
                from CDDA.CWM.WorldSnapshot import WorldSnapshot
                from CDDA.CWM.Payload import Payload
                from CDDA.CWM.CwmMessage import CwmMessage
                def snapshots():
                    buf=(out/'server-wire.bin').read_bytes();offset=0;states=[]
                    while offset+4<=len(buf):
                        size=struct.unpack('>I',buf[offset:offset+4])[0];offset+=4
                        if offset+size>len(buf):break
                        msg=CwmMessage.GetRootAs(buf[offset:offset+size]);offset+=size
                        if msg.PayloadType()==Payload.WorldSnapshot:
                            state=WorldSnapshot();state.Init(msg.Payload().Bytes,msg.Payload().Pos);states.append(state)
                    return states
                tap('Escape');wait(lambda r:int(r['equipment_form'])==0)
                tap('F8');wait(lambda r:float(r['time_scale'])==.5)
                view=open_inventory()
                for number, worn in ((2,True),(3,False)):
                    # Delay bytes only, with unchanged order/contents. The real
                    # server can apply the garment while its ACK is in flight.
                    select_item(item(view,'hat_ball'));sent=int(latest()['equipment_sent'])
                    hold_equipment_reply.set()
                    click(12.325+(number%2)*2.2,8.15+(number//2)*.75)
                    wait(lambda r:int(r['equipment_sent'])==sent+1 and int(r['pending_move'])>0)
                    command=int(latest()['inventory_work_command'])
                    tap('i')
                    check('inspection_opens_before_ack_'+str(number),int(latest()['equipment_form'])==1 and int(latest()['pending_move'])==command)
                    hold_server.clear()
                    wait(lambda r:int(r['pending_move'])==0 and int(r['inventory_view'])>0 and int(r['pause_reasons'])&2)
                    view=views()[-1];frozen=latest()
                    check('garment_applied_atomically_'+str(number),item(view,'hat_ball').Worn()==worn)
                    check('native_debit_not_an_activity_'+str(number),int(frozen['native_work_command'])==command and int(frozen['native_work_settled'])==0 and int(frozen['native_work_remaining_ms'])>0 and int(frozen['consumption_token'])==0)
                    time.sleep(1.2)
                    check('inspection_freezes_time_and_debit_'+str(number),latest()['simulation_time']==frozen['simulation_time'] and latest()['native_work_remaining_ms']==frozen['native_work_remaining_ms'])
                    shot('atomic-inspect-'+str(number)+'.png')
                    tap('Escape');wait(lambda r:int(r['equipment_form'])==0 and int(r['pause_reasons'])==0)
                    wait(lambda r:int(r['native_work_remaining_ms'])<int(frozen['native_work_remaining_ms']))
                    check('close_resumes_same_debit_and_panel_'+str(number),int(latest()['native_work_command'])==command and int(latest()['inventory_work_command'])==command and int(latest()['inventory_work_visible'])==1)
                    check('no_fractional_clothing_progress_bar_'+str(number),int(latest()['work_progress_visible'])==0)
                    shot('atomic-time-'+str(number)+'.png')
                    wait(lambda r:int(r['native_work_settled'])==1,timeout=35)
                    check('inspection_does_not_force_return_'+str(number),int(latest()['equipment_form'])==0)
                    view=open_inventory()
                    check('paid_state_still_has_expected_garment_'+str(number),item(view,'hat_ball').Worn()==worn)
                    paid_states=[s for s in snapshots() if s.InventoryWork() and s.InventoryWork().CommandId()==command]
                    check('native_wire_debit_monotonic_'+str(number),all(b.InventoryWork().RemainingTimeMs()<=a.InventoryWork().RemainingTimeMs() for a,b in zip(paid_states,paid_states[1:])) and any(s.InventoryWork().Settled() for s in paid_states))
                # Leave the same canonical end condition as the standard suite.
                select_item(item(view,'rock'));action(0)
                wait(lambda r:int(r['pending_decision'])>0);tap('1') # Explicit native store of the bat.
                finish_action()
                view=open_inventory();check('next_equipment_action_uses_fresh_inventory',item(view,'rock').Wielded())
                tap('Escape');wait(lambda r:int(r['equipment_form'])==0)
            elif args.sequential:
                from CDDA.CWM.WorldSnapshot import WorldSnapshot
                from CDDA.CWM.SimulationControlRequest import SimulationControlRequest
                from CDDA.CWM.EquipmentRequest import EquipmentRequest
                def packets(filename):
                    buf=(out/filename).read_bytes();offset=0;found=[]
                    while offset+4<=len(buf):
                        n=struct.unpack('>I',buf[offset:offset+4])[0];offset+=4
                        if offset+n>len(buf):break
                        msg=CwmMessage.GetRootAs(buf[offset:offset+n]);offset+=n;found.append(msg)
                    return found
                def paid_return(number):
                    sent=int(latest()['equipment_sent']);old_view=latest()['inventory_view']
                    click(12.325+(number%2)*2.2,8.15+(number//2)*.75)
                    wait(lambda r:int(r['equipment_sent'])==sent+1)
                    if number==0:
                        wait(lambda r:int(r['pending_decision'])>0)
                        check('native_stow_choice_precedes_return',int(latest()['equipment_form'])==0)
                        tap('1') # Fixture explicitly chooses native Store in inventory.
                    wait(lambda r:int(r['equipment_form'])==1 and int(r['inventory_view'])>0 and r['inventory_view']!=old_view,timeout=25)
                    check('automatic_return_'+str(sent),int(latest()['native_work_settled'])==1 and int(latest()['equipment_selected'])==0)
                    return views()[-1]
                start_time=int(latest()['simulation_time'])
                # Select a native filtered item; keep the optional search open across work.
                click(4.9,4.95);xdo('type','--clearmodifiers','cap');click(6.5,4.95)
                hat=item(view,'hat_ball');click(1.025,5.975);wait(lambda r:int(r['equipment_selected'])==hat.Id())
                view=paid_return(2);check('wear_completes_before_return',item(view,'hat_ball').Worn())
                check('return_preserves_search_view',int(latest()['equipment_search_open'])==1)
                shot('automatic-return-search.png')
                click(1.025,5.975);wait(lambda r:int(r['equipment_selected'])==item(view,'hat_ball').Id())
                view=paid_return(3);check('takeoff_completes_before_return',not item(view,'hat_ball').Worn())
                check('sequential_operations_advance_native_time',int(latest()['simulation_time'])>start_time)
                # Leave nested search, clear its applied filter, then act on a distinct object.
                click(7.7,4.95)
                select_item(item(view,'rock'));view=paid_return(0)
                check('third_operation_uses_fresh_native_binding',item(view,'rock').Wielded())
                shot('automatic-return-grid.png')
                if not args.action_driven:
                    tap('Escape');wait(lambda r:int(r['equipment_form'])==0)
                    tap('F8');wait(lambda r:float(r['time_scale'])==.5)
                    view=open_inventory()
                    # Esc affects UI return only; the already-paid/native mutation survives.
                    select_item(item(view,'hat_ball'));sent=int(latest()['equipment_sent'])
                    click(12.325,8.9);wait(lambda r:int(r['equipment_sent'])==sent+1)
                    tap('Escape');wait(lambda r:int(r['equipment_form'])==0 and int(r['inventory_work_command'])==0)
                    wait(lambda r:int(r['native_work_settled'])==1,timeout=25)
                    check('escape_opts_out_without_reopening',int(latest()['equipment_form'])==0)
                    view=open_inventory();check('escape_does_not_undo_native_wear',item(view,'hat_ball').Worn())
                    # Manual pause must suppress automatic return after a paid short action.
                    select_item(item(view,'hat_ball'));sent=int(latest()['equipment_sent'])
                    click(14.525,8.9);wait(lambda r:int(r['equipment_sent'])==sent+1)
                    wait(lambda r:int(r['pending_move'])==0 and int(r['native_work_command'])==int(r['inventory_work_command']))
                    tap('F7');wait(lambda r:int(r['pause_reasons'])&1)
                    paused=latest()['simulation_time'];time.sleep(.8)
                    check('manual_pause_takes_precedence',latest()['simulation_time']==paused and int(latest()['equipment_form'])==0)
                    tap('F7');wait(lambda r:int(r['pause_reasons'])==0)
                    wait(lambda r:int(r['native_work_settled'])==1,timeout=25)
                    check('manual_resume_does_not_force_inventory',int(latest()['equipment_form'])==0)
                    # Actual connection loss during pending return must drop its stale intent.
                    view=open_inventory();select_item(item(view,'hat_ball'));sent=int(latest()['equipment_sent']);connection_id=latest()['connection_id']
                    click(12.325,8.9);wait(lambda r:int(r['equipment_sent'])==sent+1)
                    wait(lambda r:int(r['pending_move'])==0 and int(r['native_work_command'])==int(r['inventory_work_command']))
                    check('disconnect_is_after_native_mutation_before_paid_return',int(latest()['native_work_settled'])==0)
                    drop.set()
                    wait(lambda r:r['connection_id']!=connection_id and int(r['input_ready'])==1,timeout=25)
                    check('reconnect_discards_pending_return',int(latest()['equipment_form'])==0 and int(latest()['inventory_work_command'])==0)
                    view=open_inventory();check('reconnect_retains_canonical_equipment',item(view,'rock').Wielded() and item(view,'hat_ball').Worn())
                tap('Escape');wait(lambda r:int(r['equipment_form'])==0)
                server_packets=packets('server-wire.bin');client_packets=packets('client-wire.bin')
                paid={};early=set();operations=[];opens=[];first_return={};active_operation=0
                for msg in server_packets:
                    if msg.PayloadType()!=Payload.WorldSnapshot:continue
                    state=WorldSnapshot();state.Init(msg.Payload().Bytes,msg.Payload().Pos);work=state.InventoryWork()
                    if work:
                        if work.Settled():paid.setdefault(work.CommandId(),state.WorldRevision())
                        else:early.add(work.CommandId())
                for msg in client_packets:
                    if msg.PayloadType()==Payload.EquipmentRequest:
                        req=EquipmentRequest();req.Init(msg.Payload().Bytes,msg.Payload().Pos);operations.append(req.CommandId());active_operation=req.CommandId()
                    if msg.PayloadType()==Payload.SimulationControlRequest:
                        req=SimulationControlRequest();req.Init(msg.Payload().Bytes,msg.Payload().Pos)
                        if req.Action()==3:
                            opens.append(msg.WorldRevision())
                            if active_operation:first_return.setdefault(active_operation,msg.WorldRevision())
                if args.action_driven:
                    check('each_native_operation_has_settled_state',all(id in paid for id in operations[:3]))
                else:
                    check('actual_wire_separates_ack_from_paid_completion',all(id in early and id in paid for id in operations[:3]))
                    check('all_three_returns_reference_paid_authoritative_revision',all(first_return.get(id,0)>=paid[id] for id in operations[:3]))
                    work_rows=[r for r in rows() if int(r.get('inventory_work_visible',0))]
                    check('work_panel_is_visible_without_modal_pause',any(int(r['pause_reasons'])==0 and int(r['equipment_form'])==0 for r in work_rows))
            elif args.presentation_only:
                es = entries(view)
                image = Image.open(out / 'inventory.png').convert('RGB')
                region = image.crop((round(origin_x+2.05*unit),round(origin_y+1.55*unit),round(origin_x+4.35*unit),round(origin_y+4.45*unit)))
                check('model_preview_has_visible_skin_not_untextured_armor',sum(max(rgb)-min(rgb)>20 for rgb in region.getdata())>300)
                check('native_fixture_exceeds_grid_and_worn_pages',len(es)>27 and sum(e.Worn() for e in es)>10)
                paused=latest();sent=paused['equipment_sent']
                click(10.35,9.2);select_item(es[27]);shot('page-two.png')
                check('page_two_selects_exact_native_identity', int(latest()['equipment_selected'])==es[27].Id())
                click(1.025,10.025);wait(lambda r:int(r['quick_slot'])==1)
                check('empty_quick_row_does_not_reassign_inventory_items',latest()['equipment_sent']==sent and int(latest()['quick_count'])==0 and int(latest()['equipment_selected'])==es[27].Id())
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
                click(2,4.95);tap('Escape');time.sleep(.3)
                check('first_escape_returns_to_grid_with_pause',int(latest()['equipment_form'])==1 and latest()['simulation_time']==paused['simulation_time'])
                click(7.7,4.95) # Remove the applied search; reset page.
                pack=next(e for e in es if e.TypeId()==b'backpack_hiking')
                select_item(pack);shot('compact-container.png');click(13.4,7.45);shot('expanded-container.png')
                check('details_do_not_execute_native_actions',latest()['equipment_sent']==sent)
                click(9.5,4.95);xdo('key','Home');xdo('key','Down');xdo('key','Down');xdo('key','Return');time.sleep(.3)
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
    before = json.loads((args.fixture.parent / ('native.json' if args.resume_only or args.quickbar_resume else 'before.json')).read_text())
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
    check('canonical_save_records_expected_weapon', native['player']['weapon']['typeid'] == ('bat' if args.presentation_only or args.language_smoke else 'rock'))
    check('canonical_save_records_backpack_worn', any(i['typeid'] == 'backpack_hiking' for i in native['player']['worn']['worn']))
    if args.presentation_only or args.language_smoke:
        check('readonly_inventory_preserves_canonical_items',native['player']['worn']==before['player']['worn'] and native['player']['weapon']==before['player']['weapon'])
    if args.language_smoke:
        check('presentation_language_does_not_rewrite_native_options', native_options.read_bytes() == native_options_before)
        if args.language_menu_change:
            from product_language import configured_language
            check('normal_launcher_persists_actual_menu_change',
                  configured_language(user / 'config/presentation-language.conf') == args.language_menu_change)
    if args.resume_only:
        check('actual_reload_preserves_canonical_position', native['player_abs'] == before['player_abs'])
        if args.action_driven:
            check('readonly_reload_inventory_consumes_no_native_time', native['time'] == before['time'])
    if args.quickbar or args.quickbar_resume:
        found={}
        def identities(value):
            if isinstance(value,dict):
                token=value.get('item_vars',{}).get('cwm_quick_identity')
                if token: found.setdefault(token,[]).append(value.get('typeid'))
                for child in value.values():identities(child)
            elif isinstance(value,list):
                for child in value:identities(child)
        identities(native['player'])
        def slot_values(value):
            result={}
            if isinstance(value,dict):
                for key,child in value.items():
                    if key.startswith('cwm_quick_slot_'):result[key]=child
                    result.update(slot_values(child))
            elif isinstance(value,list):
                for child in value:result.update(slot_values(child))
            return result
        bookmarks=slot_values(native['player'])
        check('pristine_core_retains_optional_bookmarks_and_exact_item_metadata',len(bookmarks)==2 and found.get(bookmarks.get('cwm_quick_slot_2'))==['hat_ball'] and found.get(bookmarks.get('cwm_quick_slot_3'))==['rock'])
        positions={}
        def layout(value):
            if isinstance(value,dict):
                rank=value.get('item_vars',{}).get('cwm_inventory_position')
                # Fixture uid identifies the exact instance; two native rocks
                # deliberately have different positions and must not overwrite
                # each other in a dictionary keyed by item type.
                if rank is not None:positions[value.get('item_vars',{}).get('uid')]=int(float(rank))
                for child in value.values():layout(child)
            elif isinstance(value,list):
                for child in value:layout(child)
        layout(native['player'])
        check('pristine_core_retains_optional_grid_order',0<positions.get('equipment-rock-0',0)<positions.get('equipment-bat',0)<positions.get('equipment-rock-1',0))
    (out / 'summary.json').write_text(json.dumps(dict(checks=checks, native_save=str(output)), indent=2)+'\n')


if __name__ == '__main__':
    main()
