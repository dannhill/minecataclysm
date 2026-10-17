#!/usr/bin/env python3
"""Exercise familiar hold controls, shallow-water camera and frozen presentation.

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
import struct
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('workspace', 'fixture', 'native-reader', 'artifacts'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--action-driven', action='store_true', help='Verify ordinary start.sh mode without the real-time scheduler')
    parser.add_argument('--resume-only', action='store_true')
    parser.add_argument('--toggle-controls', action='store_true')
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
                      f'cwm_run_toggle = {str(args.toggle_controls).lower()}\ncwm_crouch_toggle = {str(args.toggle_controls).lower()}\n'
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
    scratch = tempfile.TemporaryDirectory(prefix='cwm-posture-gui-')
    relay_path = Path(scratch.name) / 'relay.sock'
    native_path = out / 'native-socket'
    stop, drop = threading.Event(), threading.Event()
    slow_posture_reply = threading.Event()
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
                            if source is server_socket and slow_posture_reply.is_set():
                                slow_posture_reply.clear()
                                time.sleep(.35)
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
    sys.path.insert(0,str(ws / 'protocol/python'))
    from CDDA.CWM import CwmMessage, Payload, InteractRequest, CommandAck
    def wire_messages(filename):
        raw = (out / filename).read_bytes()
        offset = 0
        while offset + 4 <= len(raw):
            size = struct.unpack_from('>I',raw,offset)[0]
            offset += 4
            if offset + size > len(raw): break
            yield CwmMessage.CwmMessage.GetRootAs(raw[offset:offset+size],0)
            offset += size
    def accepted_action(action):
        commands = set()
        for msg in wire_messages('client-wire.bin'):
            if msg.PayloadType() == Payload.Payload.InteractRequest:
                request = InteractRequest.InteractRequest()
                request.Init(msg.Payload().Bytes,msg.Payload().Pos)
                if request.Action() == action: commands.add(request.CommandId())
        accepted = set()
        for msg in wire_messages('server-wire.bin'):
            if msg.PayloadType() == Payload.Payload.CommandAck:
                ack = CommandAck.CommandAck()
                ack.Init(msg.Payload().Bytes,msg.Payload().Pos)
                if ack.CommandId() in commands and ack.Accepted(): accepted.add(ack.CommandId())
        return len(accepted)
    window = None
    with (out / 'launcher.log').open('w') as log:
        proc = subprocess.Popen([str(ws / 'start.sh'), '--go', '--name', 'posture_tester', '--port', str(port), '--info'],
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
                wait(lambda r: abs(float(r['player_eye_offset']) + (1.08 if int(r['player_state_flags']) & 2 else 1.3)) < .025)
                shot('prone-reloaded.png')
            else:
                check('starts_native_walking_in_shallow_water', mode() == 0 and int(latest()['player_state_flags']) & 2)
                position = [latest()[k] for k in ('target_x','target_y','target_z')]
                check('native_perceived_gauges_ingested', [int(latest()[k]) for k in
                    ('status_hunger_level','status_thirst_level','status_fatigue_level','status_pain_level')] == [8,3,6,8])
                check('compact_icon_hud_is_rendered', int(latest()['hud_images_active']) > 90)
                shot('compact-hud.png')
                if args.toggle_controls:
                    for key, expected in [('Control_L',128),('Control_L',0),('Shift_L',256),('Shift_L',0)]:
                        choose_mode(key,expected)
                    check('configurable_toggle_ctrl_shift', mode() == 0)
                else:
                    for key, flag in [('Control_L',128),('Shift_L',256)]:
                        xdo('keydown',key)
                        wait(lambda r: int(r['player_state_flags']) & mask == flag and int(r['pending_move']) == 0)
                        held_start = int(latest()['time_ns'])
                        time.sleep(.8)
                        check(key + '_physical_hold_no_autorepeat', all(int(r['player_state_flags']) & mask == flag for r in rows() if int(r['time_ns']) >= held_start))
                        shot('held-' + key + '.png')
                        xdo('keyup',key)
                        wait(lambda r: int(r['player_state_flags']) & mask == 0 and int(r['pending_move']) == 0)
                        check(key + '_release_restores_walk', True)
                    xdo('keydown','Control_L')
                    wait(lambda r: int(r['player_state_flags']) & mask == 128)
                    xdo('keydown','Shift_L')
                    wait(lambda r: int(r['player_state_flags']) & mask == 256)
                    xdo('keyup','Shift_L')
                    wait(lambda r: int(r['player_state_flags']) & mask == 128)
                    xdo('keyup','Control_L')
                    wait(lambda r: int(r['player_state_flags']) & mask == 0)
                    check('crouch_priority_and_return_to_held_run', True)
                turn(-90,-50)
                xdo('click','3')
                wait(lambda r: accepted_action(1) and int(r['pending_move']) == 0)
                check('pointed_window_open_native_ack',True)
                time.sleep(.25)  # Existing interaction debounce is 200 ms.
                xdo('click','3')
                wait(lambda r: accepted_action(2) and int(r['pending_move']) == 0)
                check('plain_rmb_closes_authoritatively_open_window',True)
                time.sleep(.25)  # Respect the existing native-input debounce before the next click.
                if not args.toggle_controls:
                    wait(lambda r: int(r['player_state_flags']) & mask == 0 and int(r['pending_move']) == 0)
                    xdo('click','3')
                    wait(lambda r: accepted_action(1) == 2 and int(r['pending_move']) == 0)
                    time.sleep(.25)
                    slow_posture_reply.set()
                    xdo('keydown','Shift_L')
                    time.sleep(.1)
                    xdo('click','3')
                    time.sleep(.5)
                    xdo('keyup','Shift_L')
                    wait(lambda r: int(r['pending_move']) == 0 and int(r['player_state_flags']) & mask == 0)
                    wait(lambda r: accepted_action(2) == 2)
                    check('delayed_modifier_reply_does_not_swallow_close', accepted_action(1) == 2 and accepted_action(2) == 2)

                if args.toggle_controls:
                    # The modifier press also latched crouch in toggle mode.
                    if mode() == 256: choose_mode('Shift_L',0)
                else:
                    wait(lambda r: int(r['player_state_flags']) & mask == 0)
                choose_mode('x',512)
                wait(lambda r: abs(float(r['player_eye_offset']) + 1.08) < .025)
                wait(lambda r: float(r['camera_y']) - float(r['target_y']) * 10 > 7.)
                check('prone_wading_eye_above_surface', float(latest()['camera_y']) - float(latest()['target_y']) * 10 > 7.)
                turn(0,-15)
                shot('prone-shallow-water.png')
                check('posture_changes_preserve_native_coordinates', position == [latest()[k] for k in ('target_x','target_y','target_z')])
                animated = latest()
                time.sleep(.5)
                check('presentation_clock_and_pickups_advance_when_active', float(latest()['visual_animation_time']) > float(animated['visual_animation_time']) and latest()['ground_item_rotation'] != animated['ground_item_rotation'])
                tap('h')
                wait(lambda r: int(r['body_form']) == 1 and float(r['visual_animation_delta']) == 0)
                paused = latest()
                shot('body-before-s.png')
                for _ in range(4): tap('s')
                shot('body-after-s.png')
                check('H_freezes_native_time_water_and_pickups', latest()['simulation_time'] == paused['simulation_time'] and latest()['visual_animation_time'] == paused['visual_animation_time'] and latest()['ground_item_rotation'] == paused['ground_item_rotation'])
                # Compare the actual readonly sheet; ignore renderer metrics outside it.
                from PIL import Image, ImageChops
                before = Image.open(out / 'body-before-s.png').convert('RGB')
                after_image = Image.open(out / 'body-after-s.png').convert('RGB')
                # The central content region contains needs and body, no debug HUD.
                box = (400,260,850,570)
                check('S_does_not_change_sheet_selection', ImageChops.difference(before.crop(box),after_image.crop(box)).getbbox() is None)
                tap('Escape'); wait(lambda r: int(r['body_form']) == 0)
                wait(lambda r: float(r['visual_animation_time']) > float(paused['visual_animation_time']))
                check('visual_clock_resumes_without_catchup', float(latest()['visual_animation_time']) - float(paused['visual_animation_time']) < 3.)
                if not args.action_driven:
                    tap('F7'); wait(lambda r: int(r['pause_reasons']) & 1 and float(r['visual_animation_delta']) == 0)
                    frozen = latest()
                    turn(135,-15)
                    shot('water-paused-before.png')
                    time.sleep(.7)
                    shot('water-paused-after.png')
                    water_before = Image.open(out / 'water-paused-before.png').convert('RGB')
                    water_after = Image.open(out / 'water-paused-after.png').convert('RGB')
                    water_box = (880,350,1100,580)
                    check('rendered_water_pixels_frozen_in_manual_pause', ImageChops.difference(water_before.crop(water_box),water_after.crop(water_box)).getbbox() is None)
                    for key in ('Control_L','Shift_L','x'): tap(key)
                    check('paused_controls_and_animation_remain_stopped', mode() == 512 and latest()['visual_animation_time'] == frozen['visual_animation_time'])
                    tap('F7'); wait(lambda r: int(r['pause_reasons']) == 0)
                    time.sleep(.3)
                    check('paused_controls_not_replayed',mode() == 512)
                connection_id = latest()['connection_id']
                drop.set()
                wait(lambda r: r['connection_id'] != connection_id and int(r['input_ready']) == 1,timeout=20)
                wait(lambda r: int(r['pause_reasons']) == 0)
                check('recovery_preserves_native_prone',mode() == 512)
                if not args.action_driven and not args.toggle_controls:
                    # The independent native fixture has floor immediately west.
                    # Exercise the actual transition in both directions, not just
                    # compare two preset heights or assert a camera formula.
                    water = latest()
                    water_height = float(water['camera_y']) - float(water['target_y']) * 10
                    water_x = float(water['target_x'])
                    turn(90,0)
                    xdo('keydown','w')
                    try:
                        wait(lambda r: not int(r['player_state_flags']) & 2 and float(r['target_x']) < water_x - .5)
                    finally:
                        xdo('keyup','w')
                    wait(lambda r: abs(float(r['player_eye_offset']) + 1.3) < .01)
                    time.sleep(.4)
                    land = latest()
                    land_height = float(land['camera_y']) - float(land['target_y']) * 10
                    check('prone_water_exit_has_small_visual_step', .65 < land_height - water_height < .95)
                    shot('prone-floor.png')
                    turn(-90,0)
                    xdo('keydown','w')
                    try:
                        wait(lambda r: int(r['player_state_flags']) & 2 and float(r['target_x']) > water_x - .4)
                    finally:
                        xdo('keyup','w')
                    wait(lambda r: abs(float(r['player_eye_offset']) + 1.08) < .01)
                    time.sleep(.4)
                    entered = latest()
                    water_again = float(entered['camera_y']) - float(entered['target_y']) * 10
                    check('prone_water_entry_has_small_visual_step', .65 < land_height - water_again < .95)
                    check('small_water_dip_never_exposes_underside', 7.2 < water_again < 7.7)
                    shot('prone-water-return.png')
                shot('final-hud.png')
            final_row = latest()
            final_position = [float(final_row[k]) for k in ('target_x','target_y','target_z')]
            scene_origin = [int(final_row[k]) for k in ('scene_origin_x', 'scene_origin_y')]
            check('actual_runtime_survives', proc.poll() is None)
        finally:
            if window and proc.poll() is None:
                shot('last-frame.png')
            subprocess.run(['xdotool', 'mouseup', '1'], capture_output=True)
            subprocess.run(['xdotool', 'keyup', 'w', 'Control_L', 'Shift_L', 'x'], capture_output=True)
            stop.set()  # Explicit test shutdown; preserve all earlier relay failures.
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
    if not args.resume_only:
        check('pointed_window_closed_in_canonical_save', [61,60,0,'t_window_no_curtains','f_null'] in after['terrain_and_furniture'])
    check('canonical_native_anchor_preserved', after['player_abs'] == [scene_origin[0] + round(final_position[0]), scene_origin[1] - round(final_position[2]), round(final_position[1] / 3)])
    check('visual_sheet_does_not_pickup_or_attack', all(int(r['attacks_sent']) == 0 and int(r['queued_pickup']) == 0 for r in rows()))
    (out / 'summary.json').write_text(json.dumps(dict(checks=checks, fixture=str(args.fixture.resolve()), native_save=str(output)), indent=2)+'\n')


if __name__ == '__main__':
    main()
