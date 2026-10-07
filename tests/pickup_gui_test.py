#!/usr/bin/env python3
"""Exercise the real Mineclonia-style pickup formspec and native saved items.

Requires an independently created --create-pickup fixture, X11, xdotool,
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('workspace', 'fixture', 'native-reader', 'artifacts'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--action-driven', action='store_true', help='Verify ordinary start.sh mode without the real-time scheduler')
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
    scratch = tempfile.TemporaryDirectory(prefix='cwm-pickup-gui-')
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
        proc = subprocess.Popen([str(ws / 'start.sh'), '--go', '--name', 'pickup_tester', '--info'],
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
            initial = latest()
            tiles, nodes, owned = [int(initial[k]) for k in ('ground_tiles', 'ground_visual_nodes', 'owned_items')]
            check('ground_items_are_rendered', nodes >= 2)
            time.sleep(.8)
            check('idle_does_not_auto_pickup', int(latest()['owned_items']) == owned and int(latest()['ground_visual_nodes']) == nodes)
            turn(0, -52)
            wait(lambda r: int(r['ground_hover']) == 1)
            shot('pointed-pile.png')
            xdo('click', '3')
            wait(lambda r: int(r['ground_container']) == 1 and (args.action_driven or int(r['pause_reasons']) & 2))
            frozen = int(latest()['simulation_time'])
            shot('container-open.png')
            time.sleep(1)
            check('container_freezes_native_time', int(latest()['simulation_time']) == frozen)
            tap('Escape')
            wait(lambda r: int(r['ground_container']) == 0 and int(r['pause_reasons']) == 0)
            check('escape_does_not_transfer_items', int(latest()['owned_items']) == owned and int(latest()['ground_visual_nodes']) == nodes)
            wait(lambda r: int(r['ground_hover']) == 1)
            if not args.action_driven:
                tap('F7')
                wait(lambda r: int(r['pause_reasons']) & 1)
            xdo('click', '3')
            wait(lambda r: int(r['ground_container']) == 1 and (args.action_driven or int(r['pause_reasons']) & 2))
            shot('container-reopened.png')
            # Locate actual repeated slot interiors in the screenshot. This
            # follows rendered geometry even when the desktop DPI changes.
            from PIL import Image
            import statistics
            image = Image.open(out / 'container-reopened.png').convert('RGB')
            geometry = None
            for y in range(40, image.height // 2):
                runs, beginning = [], None
                for x in range(image.width):
                    gray = image.getpixel((x, y)) == (157, 157, 157)
                    if gray and beginning is None:
                        beginning = x
                    if beginning is not None and (not gray or x == image.width-1):
                        if 20 <= x - beginning <= 150:
                            runs.append((beginning, x))
                        beginning = None
                if len(runs) >= 7:
                    centers = [(a+b)/2 for a,b in runs]
                    widths = [b-a for a,b in runs]
                    step = statistics.median(b-a for a,b in zip(centers, centers[1:]))
                    if max(widths)-min(widths) < 3 and max(abs(b-a-step) for a,b in zip(centers,centers[1:])) < 3:
                        unit = step / 1.25
                        geometry = (centers[-1] - 7*step, y + statistics.median(widths)/2, unit, step)
                        break
            check('actual_chest_slots_detected', geometry is not None)
            x, y, unit, step = geometry
            # Move the second ground stack (7x 9mm) to an empty owned slot.
            (out / 'slot-geometry.json').write_text(json.dumps(geometry))
            xdo('mousemove', '--window', window, str(round(x)), str(round(y)))
            xdo('mousedown', '1')
            time.sleep(.2)
            xdo('mousemove', '--window', window, str(round(x+7*step)), str(round(y+4.35*unit)))
            time.sleep(.2)
            xdo('mouseup', '1')
            if not args.action_driven:
                wait(lambda r: int(r['ground_container']) == 0 and int(r['queued_pickup']) == 1)
                check('manual_pause_keeps_pickup_queued_without_free_transfer', int(latest()['owned_items']) == owned)
                old_connection = latest()['connection_id']
                drop.set()
                wait(lambda r: r['connection_id'] != old_connection and int(r['input_ready']) == 1, timeout=25)
                check('reconnect_cancels_unsent_selection_and_container', int(latest()['queued_pickup']) == 0 and int(latest()['ground_container']) == 0)
                if int(latest()['pause_reasons']) & 1:
                    tap('F7')
                wait(lambda r: int(r['pause_reasons']) == 0)
                time.sleep(.5)
                check('reconnect_does_not_replay_stale_selection', int(latest()['owned_items']) == owned and int(latest()['ground_visual_nodes']) == nodes)
                turn(0, -52)
                wait(lambda r: int(r['ground_hover']) == 1)
                xdo('click', '3')
                wait(lambda r: int(r['ground_container']) == 1 and (args.action_driven or int(r['pause_reasons']) & 2))
                xdo('mousemove', '--window', window, str(round(x)), str(round(y)))
                shot('native-stack-tooltip.png')
                xdo('mousedown', '1')
                time.sleep(.2)
                xdo('mousemove', '--window', window, str(round(x+7*step)), str(round(y+4.35*unit)))
                time.sleep(.2)
                xdo('mouseup', '1')
            wait(lambda r: int(r['ground_container']) == 0 and int(r['owned_items']) == owned+1 and int(r['pending_move']) == 0)
            check('only_selected_stack_transferred', int(latest()['ground_visual_nodes']) == nodes-1 and int(latest()['ground_tiles']) == tiles)
            shot('single-item-left.png')
            turn(0, -52)
            wait(lambda r: int(r['ground_hover']) == 1)
            xdo('click', '3')
            wait(lambda r: int(r['owned_items']) == owned+2 and int(r['pending_move']) == 0)
            check('single_item_uses_direct_pickup_without_container', int(latest()['ground_container']) == 0)
            check('emptied_ground_tile_removes_visual', int(latest()['ground_visual_nodes']) == nodes-2 and int(latest()['ground_tiles']) == tiles-1)
            shot('empty-ground.png')
            if not args.action_driven:
                tap('F7')
                wait(lambda r: int(r['pause_reasons']) & 1)
            check('actual_runtime_survives', proc.poll() is None)
        finally:
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
            scratch.cleanup()
            if old_window:
                subprocess.run(['xdotool', 'windowactivate', old_window], capture_output=True)
    check('byte_relay_completed_without_errors', not relay_errors)
    output = out / 'native.json'
    with (out / 'native.log').open('w') as log:
        result = subprocess.run([str(args.native_reader.resolve()), '--userdir', str(user),
            '--datadir', str(ws / 'cdda/data'), '--output', str(output)], stdout=log, stderr=subprocess.STDOUT, timeout=180)
    check('gui_save_readable_by_independent_native_core', result.returncode == 0)
    state = json.loads(output.read_text())
    def marked(value, uid):
        if isinstance(value, dict):
            return ([value] if value.get('item_vars', {}).get('uid') == uid else []) + [
                item for child in value.values() for item in marked(child, uid)]
        if isinstance(value, list):
            return [item for child in value for item in marked(child, uid)]
        return []
    ammo = marked(state['player'], 'pickup-selected')
    check('native_inventory_preserves_selected_seven_charge_stack', len(ammo) == 1 and ammo[0]['charges'] == 7)
    check('native_inventory_contains_directly_picked_single_item', len(marked(state['player'], 'pickup-untouched')) == 1)
    check('no_native_ground_duplicates', not marked(state['ground_items'], 'pickup-selected') and not marked(state['ground_items'], 'pickup-untouched'))


if __name__ == '__main__':
    main()
