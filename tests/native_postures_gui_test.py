#!/usr/bin/env python3
"""Exercise independent native postures, camera and canonical persistence.

Requires an independently created --create-posture fixture, X11, xdotool,
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
                      'keymap_cdda_run = KEY_KEY_R\nkeymap_cdda_crouch = KEY_KEY_X\n'
                      'keymap_cdda_prone = KEY_KEY_P\ncwm_run_toggle = true\ncwm_crouch_toggle = true\n'
                      f'port = {port}\ncwm_trace_file = {trace}\ncwm_entity_trace_file = {out / "actors.csv"}\n')
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
    scratch = tempfile.TemporaryDirectory(prefix='cwm-posture-gui-')
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
                            with (out / ('client-wire.bin' if source is client_socket else 'server-wire.bin')).open('ab') as wire_log:
                                wire_log.write(data)
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
        proc = subprocess.Popen([str(ws / 'start.sh'), '--go', '--name', 'posture_tester', '--info'],
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
            wait(lambda r: int(r['input_ready']) == 1)
            wait(lambda r: int(r['pause_reasons']) == 0)
            mask = 128 | 256 | 512
            def mode(): return int(latest()['player_state_flags']) & mask
            def choose_mode(key, expected):
                tap(key)
                wait(lambda r: (int(r['player_state_flags']) & mask) == expected and int(r['pending_move']) == 0)
            if args.resume_only:
                check('saved_prone_restored_on_actual_reload', mode() == 512)
                wait(lambda r: abs(float(r['player_eye_offset']) + 1.3) < .025)
                shot('prone-reloaded.png')
            else:
                check('starts_native_walking', mode() == 0)
                position = [latest()[k] for k in ('target_x', 'target_y', 'target_z')]
                choose_mode('r', 128)
                # Canonical fixture contains inherited move debt (-12). The
                # first admitted command starts the native turn prelude and
                # settles it. Further free mode changes must add no turns.
                initial_time = latest()['simulation_time']
                shot('running.png')
                choose_mode('r', 0)
                xdo('keydown', '--window', window, 'x')
                wait(lambda r: (int(r['player_state_flags']) & mask) == 256)
                held_start = int(latest()['time_ns'])
                time.sleep(.8)
                xdo('keyup', '--window', window, 'x')
                held_rows = [r for r in rows() if int(r['time_ns']) >= held_start]
                check('held_crouch_key_does_not_toggle_back', mode() == 256 and
                      all(int(r['player_state_flags']) & mask == 256 for r in held_rows))
                wait(lambda r: abs(float(r['player_eye_offset']) + .7) < .025)
                shot('crouched.png')
                choose_mode('p', 512)
                wait(lambda r: abs(float(r['player_eye_offset']) + 1.3) < .025)
                shot('prone.png')
                check('all_mode_changes_preserve_native_coordinates', position == [latest()[k] for k in ('target_x', 'target_y', 'target_z')])
                if args.action_driven:
                    check('mode_selection_consumes_no_native_time', latest()['simulation_time'] == initial_time)
                else:
                    tap('F7'); wait(lambda r: int(r['pause_reasons']) & 1)
                    paused = latest()
                    for key in ('r', 'x', 'p'): tap(key)
                    check('pause_blocks_all_posture_commands', mode() == 512 and latest()['simulation_time'] == paused['simulation_time'])
                    tap('F7'); wait(lambda r: int(r['pause_reasons']) == 0)
                    time.sleep(.5)
                    check('paused_keys_not_replayed', mode() == 512)
                choose_mode('p', 0)
                distances = {}
                if not args.action_driven:
                    for name, key, flags in [('walk', None, 0), ('run','r',128), ('crouch','x',256), ('prone','p',512)]:
                        if key: choose_mode(key, flags)
                        wait(lambda r: int(r['pending_move']) == 0)
                        before_move = latest()
                        xdo('keydown', 'w'); time.sleep(.45); xdo('keyup', 'w')
                        wait(lambda r: abs(float(r['intent_x'])) + abs(float(r['intent_y'])) < 1e-6)
                        time.sleep(.2)
                        after_move = latest()
                        distances[name] = math.hypot(float(after_move['target_x']) - float(before_move['target_x']),
                                                    float(after_move['target_z']) - float(before_move['target_z']))
                    (out / 'distances.json').write_text(json.dumps(distances, indent=2) + '\n')
                    check('actual_continuous_run_faster_than_walk', distances['run'] > distances['walk'] * 1.3)
                    check('actual_crouch_slower_than_walk', .2 < distances['crouch'] < distances['walk'] * .8)
                    check('actual_prone_slower_than_crouch', .05 < distances['prone'] < distances['crouch'] * .8)
                else:
                    choose_mode('p', 512)
                connection_id = latest()['connection_id']
                drop.set()
                wait(lambda r: r['connection_id'] != connection_id and int(r['input_ready']) == 1, timeout=20)
                wait(lambda r: int(r['pause_reasons']) == 0)
                check('actual_full_recovery_preserves_native_posture', mode() == 512)
                shot('after-recovery.png')
            final_row = latest()
            final_position = [float(final_row[k]) for k in ('target_x','target_y','target_z')]
            scene_origin = [int(final_row[k]) for k in ('scene_origin_x', 'scene_origin_y')]
            check('actual_runtime_survives', proc.poll() is None)
        finally:
            subprocess.run(['xdotool', 'mouseup', '1'], capture_output=True)
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
            (out / "relay-errors.json").write_text(json.dumps(relay_errors))
            scratch.cleanup()
            if old_window:
                subprocess.run(['xdotool', 'windowactivate', old_window], capture_output=True)
    check('byte_relay_completed_without_errors', not relay_errors)
    output = out / 'native.json'
    with (out / 'native.log').open('w') as log:
        result = subprocess.run([str(args.native_reader.resolve()), '--userdir', str(user),
            '--datadir', str(ws / 'cdda/data'), '--output', str(output)], stdout=log, stderr=subprocess.STDOUT, timeout=180)
    check('save_readable_by_pristine_native_core', result.returncode == 0)
    after = json.loads(output.read_text())
    check('prone_is_canonical_native_save_field', after['player']['move_mode'] == 'prone')
    check('canonical_native_anchor_preserved', after['player_abs'] == [scene_origin[0] + round(final_position[0]), scene_origin[1] - round(final_position[2]), round(final_position[1] / 3)])
    check('no_pickup_body_sheet_or_melee_needed', all(int(r['attacks_sent']) == 0 and
          int(r['ground_container']) == 0 and int(r['body_form']) == 0 and
          int(r['queued_pickup']) == 0 for r in rows()))
    (out / 'summary.json').write_text(json.dumps(dict(checks=checks, fixture=str(args.fixture.resolve()), native_save=str(output)), indent=2)+'\n')


if __name__ == '__main__':
    main()
