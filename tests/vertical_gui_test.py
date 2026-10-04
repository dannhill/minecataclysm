#!/usr/bin/env python3
"""Real start.sh input, multi-Z camera, upper-floor picking and remapping."""
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
    for case in ('default', 'remapped'):
        folder = out / case
        folder.mkdir()
        trace = folder / 'camera.csv'
        with socket.socket() as temporary:
            temporary.bind(('127.0.0.1', 0))
            port = temporary.getsockname()[1]
        config = folder / 'client.conf'
        config.write_text('screen_w = 1024\nscreen_h = 768\nfullscreen = false\nfps_max = 60\n'
                          'vsync = false\nenable_clouds = false\n'
                          f'port = {port}\ncwm_trace_file = {trace}\n' +
                          ('keymap_jump = KEY_KEY_R\n' if case == 'remapped' else ''))
        env = dict(os.environ, CDDA_USERDIR=str(user), CDDA_WORLD='audit_fixture',
                   LUANTI_WORLD=str(folder / 'luanti'), LUANTI_CONFIG=str(config),
                   LOG_DIR=str(folder / 'logs'), CDDA_BIN=str(ws / 'cdda/build/src/cdda-server'),
                   LUANTI_BIN=str(ws / 'luanti/bin/luanti'))
        env.pop('CDDA_TERRAIN_DEMO', None)
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
        def arrived(x, y, z):
            return wait(lambda r: [float(r[k]) for k in ('target_x', 'target_y', 'target_z')] ==
                        [x, y, z] and int(r['pending_move']) == 0)
        window = None
        with (folder / 'launcher.log').open('w') as log:
            proc = subprocess.Popen([str(ws / 'start.sh'), '--go', '--name', 'vertical_tester', '--info'],
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
                check(case + '_actual_start_ready', bool(window) and len(rows()) > 20)
                xdo('windowactivate', '--sync', window)
                time.sleep(1)
                if case == 'default':
                    start = latest()
                    x, z, camera_y = [float(start[k]) for k in ('target_x', 'target_z', 'camera_y')]
                    turn(0, -25)
                    shot('stairs-entry.png')
                    tap('space')
                    time.sleep(.8)
                    check('jump_on_plain_floor_keeps_authoritative_position', float(latest()['target_y']) == 0)
                    turn(0)
                    tap('w')
                    arrived(x, 0, z + 1)
                    tap('space')
                    arrived(x, 3, z + 1)
                    time.sleep(.7)
                    check('native_upper_floor_camera_height', abs(float(latest()['camera_y']) - camera_y - 30) < .1)
                    shot('upper-floor.png')
                    turn(-90)
                    revision = int(latest()['revision'])
                    xdo('click', '3')
                    wait(lambda r: int(r['revision']) > revision and int(r['pending_move']) == 0)
                    shot('upper-door-open.png')
                    check('upper_floor_picking_keeps_position', float(latest()['target_y']) == 3)
                    revision = int(latest()['revision'])
                    xdo('keydown', 'Shift_L')
                    time.sleep(.12)
                    xdo('click', '3')
                    time.sleep(.12)
                    xdo('keyup', 'Shift_L')
                    wait(lambda r: int(r['revision']) > revision and int(r['pending_move']) == 0)
                    shot('upper-door-closed.png')
                    tap('space', sneak=True)
                    arrived(x, 0, z + 1)
                    turn(0)
                    tap('s')
                    arrived(x, 0, z)
                    tap('s')
                    arrived(x, 0, z - 1)
                    tap('space', sneak=True)
                    arrived(x, -3, z - 1)
                    time.sleep(.7)
                    check('native_basement_camera_height', abs(float(latest()['camera_y']) - camera_y + 30) < .1)
                    shot('basement.png')
                    tap('space')
                    arrived(x, 0, z - 1)
                    tap('w')
                    arrived(x, 0, z)
                    turn(-90)
                    tap('w')
                    arrived(x + 1, 0, z)
                    xdo('keydown', '--window', window, 'space')
                    arrived(x + 1, 3, z)
                    time.sleep(2)
                    check('held_jump_does_not_chain_floors', float(latest()['target_y']) == 3)
                    xdo('keyup', '--window', window, 'space')
                    time.sleep(.2)
                    tap('space')
                    arrived(x + 1, 6, z)
                    check('fresh_press_reaches_second_ladder_floor', float(latest()['target_y']) == 6)
                    shot('ladder-second-floor.png')
                else:
                    check('positive_native_z_reloaded_in_real_client', float(latest()['target_y']) == 6)
                    tap('space', sneak=True)
                    time.sleep(.6)
                    check('old_binding_no_longer_moves_player', float(latest()['target_y']) == 6)
                    tap('r', sneak=True)
                    wait(lambda r: float(r['target_y']) == 3 and int(r['pending_move']) == 0)
                    check('remapped_jump_descends_through_native_action', float(latest()['target_y']) == 3)
                    shot('remapped-first-floor.png')
                check(case + '_no_runtime_abort', proc.poll() is None)
            finally:
                subprocess.run(['xdotool', 'keyup', 'Shift_L'], capture_output=True)
                if window:
                    for key in ('space', 'r', 'w', 's'):
                        subprocess.run(['xdotool', 'keyup', '--window', window, key], capture_output=True)
                if proc.poll() is None:
                    os.killpg(proc.pid, signal.SIGTERM)
                    try:
                        proc.wait(timeout=35)
                    except subprocess.TimeoutExpired:
                        os.killpg(proc.pid, signal.SIGKILL)
                        proc.wait()
                if old_window:
                    subprocess.run(['xdotool', 'windowactivate', old_window], capture_output=True)
    output = out / 'native.json'
    with (out / 'native.log').open('w') as log:
        result = subprocess.run([str(args.native_reader.resolve()), '--userdir', str(user),
            '--datadir', str(ws / 'cdda/data'), '--output', str(output)], stdout=log, stderr=subprocess.STDOUT, timeout=180)
    check('actual_gui_save_readable_by_independent_core', result.returncode == 0)
    state = json.loads(output.read_text())
    check('actual_gui_positive_z_canonical_position', state['player_abs'] == [61, 60, 1])
    terrain = {tuple(t[:3]): t[3] for t in state['terrain_and_furniture']}
    check('upper_floor_pointed_close_persisted_natively', terrain[(61, 59, 1)] == 't_door_c')
    from PIL import Image, ImageChops
    opened = Image.open(out / 'default/upper-door-open.png').convert('RGB').crop((330, 330, 700, 620))
    closed = Image.open(out / 'default/upper-door-closed.png').convert('RGB').crop((330, 330, 700, 620))
    check('upper_floor_open_close_visible_in_actual_renderer',
          sum(max(p) > 25 for p in ImageChops.difference(opened, closed).getdata()) > 100)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
