#!/usr/bin/env python3
"""Exercise the native survival HUD/body sheet independently of ground pickup.

Requires an independently created --create-body fixture, X11, xdotool,
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
        env['CDDA_CONTINUOUS'] = '0'
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
            initial = latest()
            check('native_status_ingested_and_hud_visible', int(initial['status_available']) == 1 and int(initial['survival_visible']) == 1)
            before = json.loads((args.fixture.resolve().parent / 'before.json').read_text())
            native_parts = {p['id']: p for p in before['visible_status']['parts']}
            check('wounded_head_and_arm_match_pristine_native_ui', initial['status_head'] == native_parts['head']['health']['text'] and initial['status_arm_l'] == native_parts['arm_l']['health']['text'])
            if args.action_driven:
                check('native_stamina_matches_without_local_estimate', initial['status_stamina'] == before['visible_status']['stamina']['text'])
            else:
                time.sleep(1)
                check('idle_native_time_advances', int(latest()['simulation_time']) > int(initial['simulation_time']))
            shot('survival-hud.png')
            tap('h')
            wait(lambda r: int(r['body_form']) == 1 and (args.action_driven or int(r['pause_reasons']) & 2))
            opened = latest()
            shot('native-body-sheet.png')
            # Native six main parts exceed the viewport only slightly. Scroll
            # far down twice: the second pass must stay at the content bottom.
            from PIL import Image, ImageChops
            xdo('mousemove','--window',window,'840','360')
            xdo('click','--repeat','12','--delay','20','5')
            shot('body-scroll-bottom.png')
            xdo('click','--repeat','12','--delay','20','5')
            shot('body-scroll-bottom-again.png')
            first = Image.open(out / 'body-scroll-bottom.png').convert('RGB')
            second = Image.open(out / 'body-scroll-bottom-again.png').convert('RGB')
            box = (705,220,950,500)
            check('body_scroll_stops_at_content_bottom', ImageChops.difference(first.crop(box),second.crop(box)).getbbox() is None)
            # The clipped torso temperature remains present, rather than an
            # empty pane at maximum scroll. Require visible text/icon pixels.
            pane = second.crop(box)
            check('body_scroll_keeps_last_parts_visible', sum(1 for rgb in pane.getdata() if min(rgb) > 110) > 150)
            xdo('mousemove','--window',window,'683','349')
            time.sleep(2)
            xdo('keydown', 'w')
            time.sleep(.4)
            xdo('keyup', 'w')
            time.sleep(.4)
            r = latest()
            check('body_sheet_pauses_native_time', r['simulation_time'] == opened['simulation_time'])
            check('read_only_sheet_does_not_move_or_transfer_items', r['target_x'] == opened['target_x'] and r['target_z'] == opened['target_z'] and r['owned_items'] == opened['owned_items'])
            check('survival_hud_hidden_behind_sheet', int(r['survival_visible']) == 0)
            tap('Escape')
            wait(lambda r: int(r['body_form']) == 0 and int(r['survival_visible']) == 1 and (args.action_driven or int(r['pause_reasons']) == 0))
            check('escape_returns_to_hud_and_restores_time_mode', True)
            if not args.action_driven:
                resumed = latest()
                wait(lambda r: int(r['simulation_time']) > int(resumed['simulation_time']))
                check('native_clock_resumes_after_sheet', True)
                tap('F7')
                wait(lambda r: int(r['pause_reasons']) & 1)
                stopped_time = latest()['simulation_time']
                tap('h')
                wait(lambda r: int(r['body_form']) == 1 and int(r['pause_reasons']) == 3)
                tap('Escape')
                wait(lambda r: int(r['body_form']) == 0 and int(r['pause_reasons']) == 1)
                time.sleep(1)
                check('closing_sheet_preserves_manual_pause', latest()['simulation_time'] == stopped_time)
            tap('h')
            wait(lambda r: int(r['body_form']) == 1)
            connection_id = latest()['connection_id']
            drop.set()
            wait(lambda r: r['connection_id'] != connection_id and int(r['input_ready']) == 1 and int(r['body_form']) == 0, timeout=20)
            check('real_ipc_reconnect_closes_stale_body_sheet', True)
            check('recovered_full_snapshot_restores_native_health', latest()['status_head'] == native_parts['head']['health']['text'] and int(latest()['status_available']) == 1)
            if not args.action_driven:
                wait(lambda r: int(r['pause_reasons']) == 1)
                check('manual_pause_survives_body_sheet_reconnect', True)
            shot('recovered-hud.png')
            check('actual_runtime_survives', proc.poll() is None)
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
            scratch.cleanup()
            if old_window:
                subprocess.run(['xdotool', 'windowactivate', old_window], capture_output=True)
    check('byte_relay_completed_without_errors', not relay_errors)
    output = out / 'native.json'
    with (out / 'native.log').open('w') as log:
        result = subprocess.run([str(args.native_reader.resolve()), '--userdir', str(user),
            '--datadir', str(ws / 'cdda/data'), '--output', str(output)], stdout=log, stderr=subprocess.STDOUT, timeout=180)
    check('body_demo_save_readable_by_pristine_native_core', result.returncode == 0)
    after = json.loads(output.read_text())
    after_parts = {p['id']: p for p in after['visible_status']['parts']}
    check('native_health_preserved_without_gui_healing', after_parts['head']['health']['text'] == native_parts['head']['health']['text'] and after_parts['arm_l']['health']['text'] == native_parts['arm_l']['health']['text'])
    def hp_values(state):
        return {id: (part['hp_cur'], part['hp_max']) for id, part in state['player']['body'].items()}
    check('exact_native_hp_unchanged_for_every_body_part', hp_values(after) == hp_values(before))
    check('read_only_gui_preserves_native_position', after['player_abs'] == before['player_abs'])
    if args.action_driven:
        check('read_only_gui_preserves_native_time_and_stamina', after['time'] == before['time'] and after['visible_status']['stamina'] == before['visible_status']['stamina'])
    (out / 'summary.json').write_text(json.dumps(dict(checks=checks, baseline=str(args.fixture.resolve().parent/'before.json'), native_save=str(output)), indent=2)+'\n')


if __name__ == '__main__':
    main()
