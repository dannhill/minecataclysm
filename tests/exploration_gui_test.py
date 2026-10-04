#!/usr/bin/env python3
"""Exercise native water choices and pointed apertures through start.sh and real Luanti."""
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('workspace', 'fixture', 'native-reader', 'artifacts'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    ws, out = args.workspace.resolve(), args.artifacts.resolve()
    out.mkdir(parents=True, exist_ok=True)
    user = out / 'user'
    shutil.copytree(args.fixture.resolve(), user)
    config = user / 'config'
    config.mkdir(exist_ok=True)
    (config / 'options.json').write_text(json.dumps([
        {'name': 'SAFEMODE', 'value': 'false'},
        {'name': 'AUTOSAFEMODE', 'value': 'false'},
        {'name': 'AUTOSAVE', 'value': 'false'}]))
    trace = out / 'camera.csv'
    port_socket = socket.socket()
    port_socket.bind(('127.0.0.1', 0))
    port = port_socket.getsockname()[1]
    port_socket.close()
    client_config = out / 'client.conf'
    client_config.write_text(f"screen_w = 1024\nscreen_h = 768\nfullscreen = false\n"
                            f"fps_max = 60\nvsync = false\nenable_clouds = false\n"
                            f"port = {port}\ncwm_trace_file = {trace}\n")
    env = dict(os.environ, CDDA_USERDIR=str(user), CDDA_WORLD='audit_fixture',
               LUANTI_WORLD=str(out / 'luanti'), LUANTI_CONFIG=str(client_config),
               LOG_DIR=str(out / 'logs'), CDDA_BIN=str(ws / 'cdda/build/src/cdda-server'),
               LUANTI_BIN=str(ws / 'luanti/bin/luanti'))
    env.pop('CDDA_TERRAIN_DEMO', None)
    checks = {}
    def check(name, ok):
        checks[name] = bool(ok)
        (out / 'checks.json').write_text(json.dumps(checks, indent=2) + '\n')
        print(name, 'PASS' if ok else 'FAIL', flush=True)
        if not ok:
            raise AssertionError(name)
    def rows():
        if not trace.exists():
            return []
        with trace.open() as stream:
            return [r for r in csv.DictReader(stream) if r.get('terrain_fog') is not None]
    def latest():
        return rows()[-1]
    def wait(predicate, timeout=10):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline and proc.poll() is None:
            data = rows()
            if data and predicate(data[-1]):
                return data[-1]
            time.sleep(.05)
        raise RuntimeError('condition not reached; inspect trace and logs')
    old_window = subprocess.run(['xdotool', 'getactivewindow'], capture_output=True, text=True).stdout.strip()
    window = None
    with (out / 'launcher.log').open('w') as log:
        proc = subprocess.Popen([str(ws / 'start.sh'), '--go', '--name', 'exploration_tester', '--info'],
                                env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            deadline = time.monotonic() + 80
            while time.monotonic() < deadline and proc.poll() is None:
                descendants = [proc.pid]
                for pid in descendants:
                    try:
                        descendants.extend(map(int, Path(f'/proc/{pid}/task/{pid}/children').read_text().split()))
                        if Path(f'/proc/{pid}/comm').read_text().strip() != 'luanti':
                            continue
                    except FileNotFoundError:
                        continue
                    found = subprocess.run(['xdotool', 'search', '--onlyvisible', '--pid', str(pid)], capture_output=True, text=True)
                    if found.stdout.strip():
                        window = found.stdout.splitlines()[0]
                if window and len(rows()) > 20:
                    break
                time.sleep(.2)
            check('actual_normal_start_client_ready', bool(window) and len(rows()) > 20)
            def xdo(*argv):
                subprocess.run(['xdotool', *argv], check=True, capture_output=True, timeout=5)
            def tap(key):
                xdo('keydown', '--window', window, key)
                time.sleep(.08)
                xdo('keyup', '--window', window, key)
            def shot(name):
                subprocess.run(['import', '-window', window, str(out / name)], check=True, timeout=10)
            def turn(yaw_target, pitch_target=0):
                for _ in range(20):
                    r = latest()
                    yaw = math.degrees(math.atan2(-float(r['dir_x']), float(r['dir_z'])))
                    pitch = math.degrees(math.asin(max(-1, min(1, float(r['dir_y'])))))
                    dyaw = (yaw_target - yaw + 180) % 360 - 180
                    dpitch = pitch_target - pitch
                    if max(abs(dyaw), abs(dpitch)) < 1:
                        break
                    dx = max(-130, min(130, round(-dyaw / .2)))
                    dy = max(-130, min(130, round(-dpitch / .2)))
                    xdo('mousemove_relative', '--', str(dx), str(dy))
                    time.sleep(.12)
                time.sleep(.4)
            xdo('windowactivate', '--sync', window)
            time.sleep(2)
            start = latest()
            x, z, y = [float(start[k]) for k in ('target_x', 'target_z', 'camera_y')]
            check('approved_B_in_normal_start', start['terrain_style'] == '1')
            check('comparison_fog_not_forced_into_normal_start', start['terrain_fog'] == '0')
            turn(0)
            tap('w')
            wait(lambda r: int(r['pending_move']) != 0)
            time.sleep(1)
            shot('water-warning.png')
            check('warning_waits_without_moving', float(latest()['target_z']) == z)
            tap('2')
            wait(lambda r: int(r['pending_move']) == 0)
            check('water_cancel_keeps_position', float(latest()['target_z']) == z)
            tap('w')
            wait(lambda r: int(r['pending_move']) != 0)
            time.sleep(.5)
            tap('1')
            wait(lambda r: float(r['target_z']) == z + 1 and int(r['pending_move']) == 0)
            time.sleep(1)
            shot('swimming.png')
            check('swimming_camera_enters_water', float(latest()['camera_y']) < y - 8)
            tap('s')
            wait(lambda r: float(r['target_z']) == z and int(r['pending_move']) == 0)
            time.sleep(1)
            check('camera_returns_to_ground_height', abs(float(latest()['camera_y']) - y) < .02)
            turn(90)
            shot('window-closed.png')
            revision = int(latest()['revision'])
            xdo('click', '--window', window, '3')
            wait(lambda r: int(r['revision']) > revision and int(r['pending_move']) == 0)
            time.sleep(1)
            shot('window-open.png')
            check('pointed_open_keeps_position', float(latest()['target_x']) == x and float(latest()['target_z']) == z)
            # The open pane is air: aim at its persistent sill to close it.
            turn(90, -45)
            shot('window-sill-target.png')
            revision = int(latest()['revision'])
            xdo('keydown', '--window', window, 'Shift_L')
            time.sleep(.12)  # Keep the modifier down across client input frames.
            xdo('click', '--window', window, '3')
            time.sleep(.12)
            xdo('keyup', '--window', window, 'Shift_L')
            wait(lambda r: int(r['revision']) > revision and int(r['pending_move']) == 0)
            time.sleep(1)
            turn(90)
            shot('window-reclosed.png')
            check('pointed_close_keeps_position', float(latest()['target_x']) == x and float(latest()['target_z']) == z)
            check('native_runtime_survives_actual_gui_choices', proc.poll() is None)
            from PIL import Image, ImageChops
            def foreground(name):
                return Image.open(out / name).convert('RGB').crop((330, 330, 700, 620))
            closed, opened, reclosed = map(foreground, ['window-closed.png', 'window-open.png', 'window-reclosed.png'])
            def changed(a, b):
                return sum(max(pixel) > 25 for pixel in ImageChops.difference(a, b).getdata())
            check('native_open_changes_visible_pane', changed(closed, opened) > 100)
            check('native_close_restores_visible_pane', changed(opened, reclosed) > 100)
        finally:
            if window:
                for key in ('w', 's', 'Shift_L', '1', '2'):
                    subprocess.run(['xdotool', 'keyup', '--window', window, key], capture_output=True)
            if proc.poll() is None:
                os.killpg(proc.pid, signal.SIGTERM)
                try:
                    proc.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait()
            if old_window:
                subprocess.run(['xdotool', 'windowactivate', old_window], capture_output=True)
    command = [str(args.native_reader.resolve()), '--userdir', str(user), '--datadir', str(ws / 'cdda/data'),
               '--output', str(out / 'native.json')]
    with (out / 'native.log').open('w') as log:
        readback = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=120)
    check('actual_gui_save_readable_by_independent_core', readback.returncode == 0)
    state = json.loads((out / 'native.json').read_text())
    check('actual_gui_native_position_preserved', state['player_abs'] == [60, 60, 0])
    check('actual_gui_water_damaged_native_item', 'ITEM_BROKEN' in state['player']['weapon'].get('item_tags', []))
    terrain = {tuple(t[:3]): t[3] for t in state['terrain_and_furniture']}
    check('actual_gui_window_close_persisted', terrain[(59, 60, 0)] == 't_window_no_curtains')
    log = (out / 'logs/cdda.log').read_text()
    check('normal_world_loaded_without_demo_fixture', 'Terrain comparison ready' not in log and 'Loading existing world' in log)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
