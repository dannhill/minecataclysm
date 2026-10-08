#!/usr/bin/env python3
"""Exercise the native food and drink in the actual Luanti renderer.

Requires an independently created --create-consumption fixture, X11, xdotool,
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
                assert options and options[-1] in ('Cancel','No') and len(options) <= 9, options
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
            unit = height * .075
            origin_x, origin_y = (width - 16 * unit) / 2, (height - 11 * unit) / 2
            def click(x, y):
                xdo('mousemove','--window',window,str(round(origin_x+x*unit)),str(round(origin_y+y*unit)))
                xdo('click','1'); time.sleep(.3)
            def entries(v):
                return [v.Entries(n) for n in range(v.EntriesLength())]
            def select_item(e):
                index = e.Id() - 1
                click(1.025 + (index % 6)*1.18, 3.225 + (index // 6)*1.12)
                wait(lambda r: int(r['equipment_selected']) == e.Id())
            def action(number):
                sent = int(latest()['equipment_sent'])
                click(9.7 + (number % 2)*3.8, 8.275 + (number // 2)*.85)
                wait(lambda r: int(r['equipment_form']) == 0 and int(r['equipment_sent']) == sent+1)
            def finish_action():
                wait(lambda r: int(r['pending_move']) == 0 and int(r['pause_reasons']) == 0)
            def item(v, name):
                return next(e for e in entries(v) if e.TypeId().decode() == name)
            def food(v):
                return next(e for e in entries(v) if e.TypeId() == b'apple' and not e.ConsumeWarning())
            def rotten(v):
                return next(e for e in entries(v) if e.TypeId() == b'apple' and e.ConsumeWarning())
            if args.resume_only:
                check('reload_keeps_water_in_original_container', item(view,'water_clean').Charges() == 3 and item(view,'water_clean').ParentId() == item(view,'bottle_twoliter').Id())
                check('reload_keeps_rotten_apple_and_rock', rotten(view) is not None and item(view,'rock') is not None)
                tap('Escape');wait(lambda r: int(r['equipment_form']) == 0)
            else:
                check('food_and_drink_native_actions_and_duration', food(view).Actions() & 16 and food(view).ConsumeMoves() > 0 and item(view,'water_clean').ConsumeLabel() == b'Bevi')
                check('liquid_nested_in_native_bottle', item(view,'water_clean').ParentId() == item(view,'bottle_twoliter').Id())
                check('non_food_cannot_be_consumed', not item(view,'rock').Actions() & 16)
                check('rotten_food_has_native_warning_without_consumption', bool(rotten(view).ConsumeWarning()) and rotten(view).Actions() & 16)
                first = food(view)
                fresh_id, fresh_charges = first.Id(), first.Charges()
                stopped = latest()['simulation_time'];time.sleep(.7)
                check('inventory_query_remains_readonly_and_paused', latest()['simulation_time'] == stopped)
                select_item(first);shot('food-detail.png')
                action(4);finish_action()
                if not args.action_driven:
                    wait(lambda r: int(r['consumption_token']) > 0)
                    progress = latest();token = progress['consumption_token']
                    check('native_progress_announced_before_serving_removed', int(progress['consumption_total']) == first.ConsumeMoves() and int(progress['consumption_remaining']) > 0)
                    time.sleep(.5);wait(lambda r: int(r['consumption_remaining']) < int(progress['consumption_remaining']))
                    view = open_inventory();selected = view.Entries(fresh_id-1)
                    check('started_meal_keeps_item_until_native_finish', selected.TypeId() == b'apple' and selected.Charges() == fresh_charges)
                    frozen = latest()['consumption_remaining'];time.sleep(.7)
                    check('menu_freezes_native_consumption_progress', latest()['consumption_remaining'] == frozen)
                    shot('cancel-consumption.png')
                    click(11.5,2.2)
                    wait(lambda r: int(r['cancel_consumption_sent']) == 1 and int(r['equipment_form']) == 0)
                    finish_action();wait(lambda r: int(r['consumption_token']) == 0)
                    check('cancel_reaches_busy_actor_immediately', True)
                    view = open_inventory()
                    check('cancel_preserves_food_and_quantity', view.Entries(fresh_id-1).Charges() == fresh_charges)
                    select_item(food(view));action(4);finish_action()
                    wait(lambda r: int(r['consumption_token']) > 0)
                    check('resumed_meal_has_new_cancellation_token', latest()['consumption_token'] != token)
                wait(lambda r: int(r['consumption_token']) == 0,timeout=30)
                view = open_inventory()
                fresh_now = sum(max(1,e.Charges()) for e in entries(view) if e.TypeId() == b'apple' and not e.ConsumeWarning())
                check('meal_consumes_exactly_one_native_serving', fresh_now == 1)
                select_item(item(view,'water_clean'));action(4);finish_action()
                wait(lambda r: int(r['consumption_token']) == 0,timeout=20)
                view = open_inventory()
                check('drink_consumes_one_charge_not_bottle', item(view,'water_clean').Charges() == 3 and item(view,'bottle_twoliter') is not None)
                selected = rotten(view);select_item(selected);shot('rotten-warning.png')
                action(4);wait(lambda r: int(r['pending_decision']) > 0)
                shot('native-food-warning.png');tap(cancel_choice());finish_action()
                view = open_inventory()
                check('declining_native_warning_preserves_rotten_food', rotten(view).Charges() == selected.Charges())
                check('declining_native_warning_clears_activity', int(latest()['consumption_token']) == 0)
                tap('Escape');wait(lambda r: int(r['equipment_form']) == 0)
                if not args.action_driven:
                    tap('F7');wait(lambda r: int(r['pause_reasons']) == 1)
                    view = open_inventory();select_item(food(view));sent = latest()['equipment_sent']
                    click(9.7,9.975);time.sleep(.5)
                    check('paused_consume_click_not_queued', latest()['equipment_sent'] == sent and int(latest()['equipment_form']) == 1)
                    tap('Escape');wait(lambda r: int(r['equipment_form']) == 0 and int(r['pause_reasons']) == 1)
                    tap('F7');wait(lambda r: int(r['pause_reasons']) == 0)
                    check('unpause_does_not_execute_rejected_consume', latest()['equipment_sent'] == sent and int(latest()['consumption_token']) == 0)
                view = open_inventory();connection_id = latest()['connection_id'];sent = latest()['equipment_sent']
                drop.set()
                wait(lambda r: r['connection_id'] != connection_id and int(r['input_ready']) == 1 and int(r['equipment_form']) == 0,timeout=20)
                check('real_reconnect_invalidates_old_consumption_selection', latest()['equipment_sent'] == sent)
                view = open_inventory()
                check('resync_restores_actual_remaining_water', item(view,'water_clean').Charges() == 3)
                tap('Escape');wait(lambda r: int(r['equipment_form']) == 0)
                check('actual_runtime_survives_consumption', proc.poll() is None)
        finally:
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
            scratch.cleanup()
            if old_window:
                subprocess.run(['xdotool', 'windowactivate', old_window], capture_output=True)
    check('byte_relay_completed_without_errors', not relay_errors)
    output = out / 'native.json'
    with (out / 'native.log').open('w') as log:
        result = subprocess.run([str(args.native_reader.resolve()), '--userdir', str(user),
            '--datadir', str(ws / 'cdda/data'), '--output', str(output)], stdout=log, stderr=subprocess.STDOUT, timeout=180)
    check('consumption_save_readable_by_pristine_native_core', result.returncode == 0)
    native = json.loads(output.read_text())
    before = json.loads((args.fixture.parent / ('native.json' if args.resume_only else 'before.json')).read_text())
    def items(value):
        found=[]
        if isinstance(value,dict):
            if value.get('item_vars',{}).get('uid','').startswith('consumption-'):found.append(value)
            for child in value.values():found.extend(items(child))
        elif isinstance(value,list):
            for child in value:found.extend(items(child))
        return found
    saved = items(native['player'])
    uid_counts={}
    for e in saved:
        uid=e['item_vars']['uid'];uid_counts[uid]=uid_counts.get(uid,0)+1
    check('canonical_consumption_items_never_duplicated', bool(saved) and all(n==1 for n in uid_counts.values()))
    check('canonical_water_has_three_native_charges', next(e for e in saved if e['typeid']=='water_clean')['charges']==3)
    check('canonical_bottle_and_rock_remain_owned', 'consumption-bottle' in uid_counts and 'consumption-rock' in uid_counts)
    check('canonical_rotten_apple_was_not_consumed', 'consumption-rotten' in uid_counts)
    check('canonical_food_contains_exactly_one_remaining_fresh_serving', sum(max(1,e.get('charges',1)) for e in saved if e['typeid']=='apple' and e['item_vars']['uid'] != 'consumption-rotten')==1)
    if args.resume_only:
        check('actual_reload_preserves_canonical_position', native['player_abs'] == before['player_abs'])
        if args.action_driven:
            check('readonly_reload_inventory_consumes_no_native_time', native['time'] == before['time'])
    else:
        check('native_digestion_received_food_and_water', native['player']['stomach']['last_ate'] > before['player']['stomach']['last_ate'])
    (out / 'summary.json').write_text(json.dumps(dict(checks=checks, native_save=str(output)), indent=2)+'\n')


if __name__ == '__main__':
    main()
