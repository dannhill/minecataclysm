#!/usr/bin/env python3
"""Exercise real actor pointing and CDDA melee without pickup/body-sheet dependencies.

Requires an independently created --create-combat fixture, X11, xdotool,
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
                      f'port = {port}\ncwm_trace_file = {trace}\ncwm_entity_trace_file = {out / "actors.csv"}\n')
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
    scratch = tempfile.TemporaryDirectory(prefix='cwm-melee-gui-')
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
        proc = subprocess.Popen([str(ws / 'start.sh'), '--go', '--name', 'melee_tester', '--info'],
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
            if not args.action_driven and int(latest()['pause_reasons']) & 4:
                tap('e')  # existing native threat acknowledgement, not manual pause
            wait(lambda r: int(r['pause_reasons']) == 0)
            turn(0, -12)
            wait(lambda r: int(r['combat_hover']) > 1)
            target = latest()['combat_hover']
            before = json.loads((args.fixture.resolve().parent / 'before.json').read_text())
            initial = latest()
            check('actual_native_target_pointed', int(target) >> 62 == 1)
            check('demo_weapon_pre_equipped_without_pickup', 'bat' in str(before['player']['weapon']))
            shot('pointed-target.png')
            def click():
                xdo('click', '1')
                time.sleep(.35)
            if not args.action_driven:
                tap('F7')
                wait(lambda r: int(r['pause_reasons']) & 1)
                paused = latest()
                click()
                time.sleep(.6)
                check('pause_blocks_attack_and_native_time', latest()['attacks_sent'] == paused['attacks_sent'] and latest()['simulation_time'] == paused['simulation_time'])
                tap('F7')
                wait(lambda r: int(r['pause_reasons']) == 0)
                time.sleep(.5)
                check('paused_click_not_replayed_on_resume', latest()['attacks_sent'] == paused['attacks_sent'])
            turn(180, 0)
            wait(lambda r: int(r['combat_hover']) == 0)
            sent = latest()['attacks_sent']
            click()
            check('empty_pointing_sends_no_attack', latest()['attacks_sent'] == sent)
            turn(0, -12)
            wait(lambda r: r['combat_hover'] == target)
            xdo('mousedown', '1')
            wait(lambda r: int(r['attacks_sent']) == int(sent) + 1)
            time.sleep(.9)
            xdo('mouseup', '1')
            wait(lambda r: int(r['pending_move']) == 0)
            check('held_mouse_sends_exactly_one_attack', int(latest()['attacks_sent']) == int(sent) + 1)
            check('request_targets_the_actual_pointed_identity', latest()['attack_target'] == target)
            check('actual_native_attack_acknowledged_including_a_miss', int(latest()['attack_result']) == 1)
            shot('after-native-strike.png')
            connection_id = latest()['connection_id']
            drop.set()
            wait(lambda r: r['connection_id'] != connection_id and int(r['input_ready']) == 1, timeout=20)
            wait(lambda r: int(r['pause_reasons']) == 0)
            check('full_recovery_does_not_repeat_attack', int(latest()['attacks_sent']) == int(sent) + 1)
            def target_pose():
                with (out / 'actors.csv').open() as stream:
                    records = [r for r in csv.DictReader(stream) if r['id'] == target]
                return records[-1]
            clicks_moved_player = False
            out_of_reach_checked = False
            # Native bat BRUTAL can knock the target back. Follow with native
            # movement, never inferring a hit or weakening native range checks.
            for _ in range(20):
                if int(latest()['attack_target_hp']) < 0:
                    break
                actor, r = target_pose(), latest()
                dx, dz = float(actor['target_x']) - float(r['target_x']), float(actor['target_z']) - float(r['target_z'])
                yaw = math.degrees(math.atan2(-dx, dz))
                turn(yaw, -25)
                wait(lambda r: r['combat_hover'] == target)
                native_distance = max(abs(round(float(actor['target_x'])) - round(float(r['target_x']))),
                                      abs(round(float(actor['target_z'])) - round(float(r['target_z']))))
                if native_distance > 1:
                    if not out_of_reach_checked:
                        hp = latest()['attack_target_hp']
                        previous = int(latest()['attacks_sent'])
                        click()
                        wait(lambda r: int(r['attacks_sent']) > previous and int(r['pending_move']) == 0)
                        check('native_knockback_target_cannot_be_hit_at_range', int(latest()['attack_result']) == 0 and latest()['attack_target_hp'] == hp)
                        out_of_reach_checked = True
                    for _ in range(15):
                        r, actor = latest(), target_pose()
                        gap = max(abs(round(float(actor['target_x'])) - round(float(r['target_x']))),
                                  abs(round(float(actor['target_z'])) - round(float(r['target_z']))))
                        if gap <= 1:
                            break
                        if args.action_driven:
                            tap('w')
                        else:
                            xdo('keydown', 'w'); time.sleep(.075); xdo('keyup', 'w'); time.sleep(.4)
                    check('native_movement_reaches_knocked_back_target', gap <= 1)
                    actor, r = target_pose(), latest()
                    dx, dz = float(actor['target_x']) - float(r['target_x']), float(actor['target_z']) - float(r['target_z'])
                    turn(math.degrees(math.atan2(-dx, dz)), -25)
                    wait(lambda r: r['combat_hover'] == target)
                before_click = latest()
                previous = int(before_click['attacks_sent'])
                click()
                wait(lambda r: int(r['attacks_sent']) > previous and int(r['pending_move']) == 0)
                after_click = latest()
                clicks_moved_player |= any(abs(float(after_click[k]) - float(before_click[k])) > .02
                                          for k in ('target_x','target_y','target_z'))
            check('pointed_attacks_do_not_move_player', not clicks_moved_player)
            final_position = [float(latest()[k]) for k in ('target_x','target_y','target_z')]
            check('native_death_removes_target', int(latest()['attack_target_hp']) == -1)
            time.sleep(.4)
            sent = latest()['attacks_sent']
            click()
            check('dead_target_cannot_be_attacked_again', latest()['attacks_sent'] == sent)
            shot('native-corpse.png')
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
            scratch.cleanup()
            if old_window:
                subprocess.run(['xdotool', 'windowactivate', old_window], capture_output=True)
    check('byte_relay_completed_without_errors', not relay_errors)
    output = out / 'native.json'
    with (out / 'native.log').open('w') as log:
        result = subprocess.run([str(args.native_reader.resolve()), '--userdir', str(user),
            '--datadir', str(ws / 'cdda/data'), '--output', str(output)], stdout=log, stderr=subprocess.STDOUT, timeout=180)
    check('combat_save_readable_by_pristine_native_core', result.returncode == 0)
    after = json.loads(output.read_text())
    check('native_monster_death_persisted', not any(m['typeid'] == 'mon_zombie' for m in after['monsters']))
    check('specific_native_corpse_created_at_target', any(
        any(it.get('typeid') == 'corpse' and
            it.get('corpse') == 'mon_zombie' and it.get('name') == 'Bersaglio melee'
            for it in tile['items']) for tile in after['ground_items']))
    check('native_save_preserves_final_authoritative_anchor', after['player_abs'] == [round(final_position[0]), -round(final_position[2]), round(final_position[1] / 3)])
    check('native_time_paid_for_combat', after['time'] > before['time'])
    check('weapon_remains_native_and_equipped', 'bat' in str(after['player']['weapon']))
    (out / 'summary.json').write_text(json.dumps(dict(checks=checks, baseline=str(args.fixture.resolve().parent/'before.json'), native_save=str(output)), indent=2)+'\n')


if __name__ == '__main__':
    main()
