#!/usr/bin/env python3
"""SAVE-001 attempt through the actual Luanti client, with a passive CWM proxy."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import select
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time


def run(ws, reader, probe, out):
    out.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(ws/'protocol/python'))
    from CDDA.CWM import CwmMessage, Payload, WorldSnapshot, EntityType, CommandAck, MoveRequest
    events = []
    stop = threading.Event()
    checks = []

    def check(name, ok, **detail):
        entry = {'name': name, 'status': 'PASS' if ok else 'FAIL', **detail}
        checks.append(entry)
        (out/'checks.json').write_text(json.dumps(checks, indent=2)+'\n')
        print(json.dumps(entry), flush=True)

    def native(user, filename, create=False, character=None):
        if character:
            # The pristine public world loader selects the first player save.
            # Select one player in a disposable copy; preserve every original.
            selected_user=out/(filename+'.reader-user')
            shutil.copytree(user,selected_user,dirs_exist_ok=True)
            for save in (selected_user/'save/audit_fixture').glob('*.sav'):
                text=save.read_text()
                state=json.loads(text[text.index('{'):])
                if state.get('player',{}).get('name') != character:
                    save.unlink()
            user=selected_user
        args = [str(reader), '--userdir', str(user), '--datadir', str(ws/'cdda/data'),
                '--output', str(out/filename)]
        if create: args.append('--create')
        if character: args += ['--expect-character', character]
        with (out/(filename+'.log')).open('w') as log:
            result = subprocess.run(args, stdout=log, stderr=subprocess.STDOUT, timeout=180)
        check('native_'+filename, result.returncode == 0, command=args, exit_code=result.returncode)
        return json.loads((out/filename).read_text()) if result.returncode == 0 else None

    with tempfile.TemporaryDirectory(prefix='m55-save-') as temporary:
        directory = Path(temporary)
        user = directory/'user'
        baseline = native(user, 'before.json', create=True)
        if baseline is None: return False
        backend = directory/'backend.sock'
        frontend = directory/'frontend.sock'
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        listener.bind(str(frontend)); listener.listen(); listener.settimeout(.5)

        def proxy():
            try:
                while not stop.is_set():
                    try: client, _ = listener.accept(); break
                    except socket.timeout: continue
                else: return
                server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                server.connect(str(backend))
                sockets = [client, server]
                buffers = {client: b'', server: b''}
                with client, server, (out/'client.wire').open('wb') as cfile, (out/'server.wire').open('wb') as sfile:
                    while not stop.is_set():
                        ready, _, _ = select.select(sockets, [], [], .2)
                        for source in ready:
                            data = source.recv(65536)
                            if not data: return
                            destination = server if source is client else client
                            destination.sendall(data)
                            (cfile if source is client else sfile).write(data)
                            buffers[source] += data
                            buf = buffers[source]
                            while len(buf) >= 4:
                                size = struct.unpack('>I', buf[:4])[0]
                                if size > 16*1024*1024: raise ValueError('oversized proxy frame')
                                if len(buf) < 4+size: break
                                payload, buf = buf[4:4+size], buf[4+size:]
                                msg = CwmMessage.CwmMessage.GetRootAsCwmMessage(payload, 0)
                                event = {'direction': 'client' if source is client else 'server',
                                         'payload_type': msg.PayloadType(), 'time_ns': time.monotonic_ns(),
                                         'sequence': msg.SequenceNumber(), 'revision': msg.WorldRevision()}
                                if msg.PayloadType() == Payload.Payload.WorldSnapshot:
                                    snap = WorldSnapshot.WorldSnapshot()
                                    snap.Init(msg.Payload().Bytes, msg.Payload().Pos)
                                    for i in range(snap.EntitiesLength()):
                                        who = snap.Entities(i)
                                        if who.Type() == EntityType.EntityType.PLAYER:
                                            event['player'] = {'name': who.Name().decode(),
                                                'position': [who.Pos().X()+snap.Origin().X(),
                                                             who.Pos().Y()+snap.Origin().Y(), who.Pos().Z()],
                                                'time': snap.SimulationTimeSeconds()}
                                if msg.PayloadType() == Payload.Payload.CommandAck:
                                    ack = CommandAck.CommandAck(); ack.Init(msg.Payload().Bytes, msg.Payload().Pos)
                                    event.update(command_id=ack.CommandId(), accepted=ack.Accepted())
                                if msg.PayloadType() == Payload.Payload.MoveRequest:
                                    request = MoveRequest.MoveRequest(); request.Init(msg.Payload().Bytes, msg.Payload().Pos)
                                    event['command_id'] = request.CommandId()
                                events.append(event)
                            buffers[source] = buf
            except Exception as error:
                events.append({'error': repr(error)})

        server_cmd = ['stdbuf', '-oL', '-eL', str(ws/'cdda/build/src/cdda-server'), '--socket', str(backend),
                      '--userdir', str(user), '--datadir', str(ws/'cdda/data'), '--world', 'audit_fixture']
        (out/'commands.json').write_text(json.dumps({'server': server_cmd}, indent=2)+'\n')
        with (out/'server.log').open('w') as slog:
            server = subprocess.Popen(server_cmd, stdout=slog, stderr=subprocess.STDOUT)
            gui = None; thread = None; old_window = None
            try:
                deadline = time.monotonic()+120
                while not backend.exists() and server.poll() is None and time.monotonic() < deadline: time.sleep(.1)
                check('headless_ready', backend.exists() and server.poll() is None, exit_code=server.poll())
                if not backend.exists(): return False
                thread = threading.Thread(target=proxy, daemon=True); thread.start()
                world = directory/'presentation'; world.mkdir()
                (world/'world.mt').write_text('gameid = cdda_voxel\nbackend = sqlite3\nplayer_backend = sqlite3\nauth_backend = sqlite3\n')
                cfg = out/'client.conf'
                cfg.write_text('name = audit\nscreen_w = 1024\nscreen_h = 768\nfps_max = 60\nvsync = false\nenable_update_checker = false\nkeymap_aux1 = KEY_KEY_E\n')
                game_link = ws/'luanti/games/cdda_voxel'
                if not game_link.exists(): game_link.symlink_to(ws/'game', target_is_directory=True)
                env = os.environ.copy(); env.update(LD_PRELOAD=str(probe), M55_SOCKET_PATH=str(frontend), M55_FRAME_LOG=str(out/'frames.ns'))
                gui_cmd = [str(ws/'luanti/bin/luanti'), '--go', '--gameid', 'cdda_voxel', '--world', str(world),
                           '--config', str(cfg), '--logfile', str(out/'engine.log')]
                with (out/'client.log').open('w') as glog:
                    gui = subprocess.Popen(gui_cmd, stdout=glog, stderr=subprocess.STDOUT, env=env)
                    old_window = subprocess.run(['xdotool', 'getactivewindow'], capture_output=True, text=True).stdout.strip()
                    window = None
                    for _ in range(200):
                        if gui.poll() is not None: break
                        result = subprocess.run(['xdotool', 'search', '--onlyvisible', '--pid', str(gui.pid)], capture_output=True, text=True)
                        if result.stdout.strip(): window = result.stdout.strip().splitlines()[0]
                        if window and any('player' in e for e in events): break
                        time.sleep(.1)
                    if window and gui.poll() is None:
                        subprocess.run(['xdotool', 'windowactivate', '--sync', window], capture_output=True, timeout=5)
                        time.sleep(4)
                        subprocess.run(['xdotool', 'keydown', '--window', window, 'w'], capture_output=True)
                        time.sleep(.5)
                        subprocess.run(['xdotool', 'keyup', '--window', window, 'w'], capture_output=True)
                        # Full native turns can detect a threat and stop input.
                        # Exercise the actual explicit-resume binding before
                        # measuring accepted movement; never disable safe mode.
                        time.sleep(.3)
                        subprocess.run(['xdotool', 'keydown', '--window', window, 'e'], capture_output=True)
                        time.sleep(.15)
                        subprocess.run(['xdotool', 'keyup', '--window', window, 'e'], capture_output=True)
                        time.sleep(.3)
                        subprocess.run(['xdotool', 'keydown', '--window', window, 'w'], capture_output=True)
                        time.sleep(.6)
                        subprocess.run(['xdotool', 'keyup', '--window', window, 'w'], capture_output=True)
                        time.sleep(4)
                        subprocess.run(['import', '-window', window, str(out/'scene.png')], capture_output=True, timeout=15)
                    gui.terminate(); gui.wait(timeout=15)
                check('actual_3d_client_received_state', any('player' in e for e in events))
                sent = sum(e.get('direction') == 'client' and e.get('payload_type') == Payload.Payload.MoveRequest for e in events)
                accepted = sum(e.get('payload_type') == Payload.Payload.CommandAck and e.get('accepted', False) for e in events)
                check('actual_3d_movement_attempted', sent > 0, sent=sent, accepted=accepted)
                move_ids = {e.get('command_id') for e in events if e.get('direction') == 'client'
                            and e.get('payload_type') == Payload.Payload.MoveRequest}
                # Requests are decoded below into command IDs, avoiding the
                # acknowledgement of a free threat-resume counting as movement.
                accepted_moves = sum(e.get('command_id') in move_ids and e.get('accepted', False)
                                     for e in events if e.get('payload_type') == Payload.Payload.CommandAck)
                check('actual_3d_movement_accepted', accepted_moves > 0, accepted_moves=accepted_moves)
            finally:
                if gui and gui.poll() is None: gui.kill(); gui.wait()
                if server.poll() is None:
                    server.terminate()
                    try: server.wait(timeout=20)
                    except subprocess.TimeoutExpired: server.kill(); server.wait()
                stop.set(); listener.close()
                if thread: thread.join(timeout=2)
                if old_window: subprocess.run(['xdotool', 'windowactivate', old_window], capture_output=True)
                (out/'events.json').write_text(json.dumps(events, indent=2)+'\n')
                shutil.copytree(user, out/'user-state', dirs_exist_ok=True)
                check('graceful_canonical_save', server.returncode == 0 and 'Final save: SUCCESS' in (out/'server.log').read_text(), exit_code=server.returncode)
        snapshots = [e['player'] for e in events if 'player' in e]
        if not snapshots: return False
        initial, final = snapshots[0], snapshots[-1]
        check('existing_avatar_preserved', initial['name'] == baseline['player']['name'], expected=baseline['player']['name'], observed=initial['name'])
        loaded = native(user, 'after.json', character=final['name'])
        if loaded:
            check('saved_position_matches_authority', loaded['player_abs'] == final['position'], expected=final['position'], observed=loaded['player_abs'])
            check('saved_time_matches_authority', loaded['time'] == final['time'], expected=final['time'], observed=loaded['time'])
            check('fixture_time_is_preserved_on_load', initial['time'] == baseline['time'], expected=baseline['time'], observed=initial['time'])
        (out/'scope.json').write_text(json.dumps({'status': 'FAILED' if any(c['status'] == 'FAIL' for c in checks) else 'INCOMPLETE',
            'save001_complete': False, 'reason': 'Existing-avatar/time preconditions and observed position/time are checked. Full inventory, world and entity semantic equivalence remains required before certification.',
            'binaries': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in [reader, ws/'cdda/build/src/cdda-server', ws/'luanti/bin/luanti']}}, indent=2)+'\n')
    return all(c['status'] == 'PASS' for c in checks)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ['workspace', 'native-reader', 'probe-library', 'artifacts']:
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    sys.exit(0 if run(args.workspace.resolve(), args.native_reader.resolve(), args.probe_library.resolve(), args.artifacts.resolve()) else 1)
