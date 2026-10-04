#!/usr/bin/env python3
"""Real Luanti renderer under fragmented frames, a data flood, final EOF and malformed peers."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import queue
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('workspace', 'artifacts'): parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args(); ws, out = args.workspace.resolve(), args.artifacts.resolve()
    out.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(ws/'protocol/python'))
    import flatbuffers
    from CDDA.CWM import CwmMessage as Msg, Payload, HelloResponse as Hello, HeartbeatAck as Beat
    from CDDA.CWM import WorldSnapshot as World, ChunkSnapshot as Chunk, CwmBlock as Block
    from CDDA.CWM import EntityState as Entity, Vec3f, Coord3i
    commands = queue.Queue(); errors = []; stop = threading.Event(); checks = {}
    trace = out/'camera.csv'; binary = ws/'luanti/bin/luanti'
    (out/'identity.json').write_text(json.dumps(dict(binary=str(binary), sha256=hashlib.sha256(binary.read_bytes()).hexdigest()), indent=2)+'\n')
    def check(name, ok):
        checks[name] = bool(ok); (out/'checks.json').write_text(json.dumps(checks, indent=2)+'\n')
        print(name, 'PASS' if ok else 'FAIL', flush=True)
        if not ok: raise AssertionError(name)
    def envelope(b, kind, value, revision):
        Msg.CwmMessageStart(b); Msg.CwmMessageAddSequenceNumber(b, revision)
        Msg.CwmMessageAddWorldRevision(b, revision); Msg.CwmMessageAddPayloadType(b, kind); Msg.CwmMessageAddPayload(b, value)
        b.Finish(Msg.CwmMessageEnd(b)); return bytes(b.Output())
    def hello():
        b = flatbuffers.Builder(128); Hello.HelloResponseStart(b); Hello.HelloResponseAddAccepted(b, True)
        return envelope(b, Payload.Payload.HelloResponse, Hello.HelloResponseEnd(b), 1)
    def snapshot(revision, full=False):
        b = flatbuffers.Builder(4096); chunks = 0
        if full:
            Chunk.ChunkSnapshotStartBlocksVector(b, 256)
            for i in range(255, -1, -1):
                x, y = i%16, i//16; wall = x in (0, 15) or y in (0, 15)
                Block.CreateCwmBlock(b, 2 if wall else 0, 3 if wall else 4, 15, 0)
            blocks = b.EndVector()
            Chunk.ChunkSnapshotStart(b); Chunk.ChunkSnapshotAddSizeX(b, 16); Chunk.ChunkSnapshotAddSizeY(b, 16)
            Chunk.ChunkSnapshotAddSizeZ(b, 1); Chunk.ChunkSnapshotAddBlocks(b, blocks)
            chunk = Chunk.ChunkSnapshotEnd(b)
            World.WorldSnapshotStartChunksVector(b, 1); b.PrependUOffsetTRelative(chunk); chunks = b.EndVector()
        Entity.EntityStateStart(b); Entity.EntityStateAddId(b, 1)
        Entity.EntityStateAddPos(b, Vec3f.CreateVec3f(b, 8, 12, 0)); entity = Entity.EntityStateEnd(b)
        World.WorldSnapshotStartEntitiesVector(b, 1); b.PrependUOffsetTRelative(entity); entities = b.EndVector()
        World.WorldSnapshotStart(b); World.WorldSnapshotAddOrigin(b, Coord3i.CreateCoord3i(b, 0, 0, 0))
        World.WorldSnapshotAddEntities(b, entities)
        if full: World.WorldSnapshotAddChunks(b, chunks)
        return envelope(b, Payload.Payload.WorldSnapshot, World.WorldSnapshotEnd(b), revision)
    def beat(revision):
        b = flatbuffers.Builder(128); Beat.HeartbeatAckStart(b)
        return envelope(b, Payload.Payload.HeartbeatAck, Beat.HeartbeatAckEnd(b), revision)
    def frame(body): return struct.pack('>I', len(body))+body
    def rows():
        if not trace.exists(): return []
        with trace.open() as f: return [row for row in csv.DictReader(f) if row.get('ipc_write_calls') is not None]
    def until(predicate, timeout=20):
        deadline = time.monotonic()+timeout
        while time.monotonic() < deadline and proc.poll() is None:
            data = rows()
            if data and predicate(data[-1]): return data[-1]
            time.sleep(.05)
        found = subprocess.run(['xdotool', 'search', '--onlyvisible', '--pid', str(proc.pid)], capture_output=True, text=True)
        if found.stdout.strip():
            subprocess.run(['import', '-window', found.stdout.splitlines()[0], str(out/'timeout.png')], timeout=10)
        raise RuntimeError(f'Renderer condition timed out (exit={proc.poll()}); inspect trace, task-window screenshot and engine log')
    link = ws/'luanti/games/cdda_voxel'
    if not link.exists(): link.parent.mkdir(parents=True, exist_ok=True); link.symlink_to(ws/'game', target_is_directory=True)
    with tempfile.TemporaryDirectory(prefix='cwm-gui-adverse-') as temporary:
        scratch = Path(temporary); path = scratch/'cwm.sock'
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); listener.bind(str(path)); listener.listen(4); listener.settimeout(.2)
        def serve():
            connection_index = 0
            try:
                while not stop.is_set():
                    try: c, _ = listener.accept()
                    except socket.timeout: continue
                    connection_index += 1
                    with c:
                        c.settimeout(10)
                        # Read the real bridge's queued Hello, including fragmentation.
                        def exact(n):
                            data = b''
                            while len(data) < n:
                                part = c.recv(n-len(data))
                                if not part: raise EOFError()
                                data += part
                            return data
                        size = struct.unpack('>I', exact(4))[0]; msg = Msg.CwmMessage.GetRootAsCwmMessage(exact(size), 0)
                        if msg.PayloadType() != Payload.Payload.HelloRequest: raise ValueError('Missing real Hello')
                        wire = frame(hello())+frame(snapshot(connection_index*1000, True))
                        c.sendall(wire[:2]); time.sleep(.02); c.sendall(wire[2:7]); time.sleep(.02); c.sendall(wire[7:])
                        while not stop.is_set():
                            try: action = commands.get(timeout=.1)
                            except queue.Empty: continue
                            if action == 'flood':
                                # Valid FlatBuffers followed by allowed trailing padding.
                                c.sendall(b''.join(frame(beat(1100+i)+bytes(65536)) for i in range(40)))
                            elif action == 'final':
                                c.sendall(frame(snapshot(1500))); break
                            elif action == 'oversize':
                                c.sendall(struct.pack('>I', 16*1024*1024+1)); break
                            elif action == 'malformed':
                                c.sendall(struct.pack('>I', 8)+b'garbage!'); break
            except (OSError, EOFError, ValueError) as error:
                if not stop.is_set(): errors.append(repr(error))
        thread = threading.Thread(target=serve, daemon=True); thread.start()
        world = scratch/'world'; world.mkdir()
        (world/'world.mt').write_text('gameid = cdda_voxel\nbackend = sqlite3\nplayer_backend = sqlite3\nauth_backend = sqlite3\n')
        port = socket.socket(); port.bind(('127.0.0.1', 0)); port_number = port.getsockname()[1]; port.close()
        config = scratch/'client.conf'
        config.write_text(f'fullscreen = false\nscreen_w = 1024\nscreen_h = 768\nfps_max = 60\nfps_max_unfocused = 60\n'
            f'vsync = false\nenable_damage = false\nenable_update_checker = false\nenable_clouds = false\ndebug_log_level = info\n'
            f'cwm_socket_path = {path}\ncwm_trace_file = {trace}\nport = {port_number}\n')
        old_window = subprocess.run(['xdotool', 'getactivewindow'], capture_output=True, text=True).stdout.strip()
        window = None
        with (out/'console.log').open('w') as log:
            command = [str(binary), '--go', '--world', str(world), '--gameid', 'cdda_voxel', '--config', str(config),
                       '--name', 'transport_tester', '--info', '--logfile', str(out/'engine.log')]
            (out/'command.json').write_text(json.dumps(dict(argv=command, cwd=str(ws/'luanti'), display=os.environ.get('DISPLAY')), indent=2)+'\n')
            proc = subprocess.Popen(command, cwd=ws/'luanti', stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            try:
                until(lambda r: int(r['revision']) == 1000, 80)
                found = subprocess.run(['xdotool', 'search', '--onlyvisible', '--pid', str(proc.pid)], capture_output=True, text=True)
                window = found.stdout.strip().splitlines()[0]
                subprocess.run(['xdotool', 'windowactivate', '--sync', window], check=True, capture_output=True)
                time.sleep(2)
                check('real_client_applied_fragmented_initial_state', int(rows()[-1]['revision']) == 1000)
                subprocess.run(['import', '-window', window, str(out/'before.png')], check=True, timeout=10)
                flood_start = time.monotonic(); commands.put('flood')
                until(lambda r: int(r['revision']) == 1139)
                flood_end = time.monotonic()
                commands.put('final'); until(lambda r: int(r['revision']) == 1500 and int(r['ipc_connected']) == 0)
                check('final_complete_state_applied_before_disconnect', int(rows()[-1]['revision']) == 1500)
                check('renderer_alive_after_eof', proc.poll() is None)
                until(lambda r: int(r['revision']) == 2000 and int(r['ipc_connected']) == 1)
                check('fresh_connection_after_orderly_close', True)
                commands.put('oversize'); until(lambda r: int(r['ipc_connected']) == 0)
                check('renderer_survives_oversized_prefix', proc.poll() is None)
                until(lambda r: int(r['revision']) == 3000 and int(r['ipc_connected']) == 1)
                commands.put('malformed'); until(lambda r: int(r['ipc_connected']) == 0)
                check('renderer_survives_invalid_flatbuffer', proc.poll() is None)
                until(lambda r: int(r['revision']) == 4000 and int(r['ipc_connected']) == 1)
                check('client_usable_after_repeated_transport_failure', True)
                subprocess.run(['import', '-window', window, str(out/'after.png')], check=True, timeout=10)
            finally:
                if proc.poll() is None:
                    proc.terminate()
                    try: proc.wait(timeout=10)
                    except subprocess.TimeoutExpired: proc.kill(); proc.wait()
                stop.set(); listener.close(); thread.join(timeout=2)
                if old_window: subprocess.run(['xdotool', 'windowactivate', old_window], capture_output=True)
    data = rows()
    check('renderer_clean_exit', proc.returncode == 0)
    check('adverse_authority_no_fixture_errors', not errors)
    check('real_frame_input_and_output_caps', all(int(r['ipc_input']) <= 16*1024*1024+4 and int(r['ipc_output']) <= 32*1024*1024 for r in data))
    check('real_frame_io_and_dispatch_budgets', all(int(r['ipc_read_bytes']) <= 256*1024 and
        int(r['ipc_write_bytes']) <= 256*1024 and int(r['ipc_frames']) <= 8 and
        int(r['ipc_read_calls']) <= 64 and int(r['ipc_write_calls']) <= 64 for r in data))
    check('flood_exercised_read_budget', max(int(r['ipc_read_bytes']) for r in data) == 256*1024)
    flood = [int(r['time_ns'])/1e9 for r in data if flood_start < int(r['time_ns'])/1e9 < flood_end]
    gaps = [b-a for a, b in zip(flood, flood[1:])]
    check('renderer_kept_frames_during_flood', len(flood) >= 5 and max(gaps, default=1) < .2)
    (out/'observations.json').write_text(json.dumps(dict(errors=errors, trace_rows=len(data), flood_frames=len(flood),
        max_flood_frame_gap_ms=max(gaps, default=0)*1000, peak_read_bytes=max(int(r['ipc_read_bytes']) for r in data)), indent=2)+'\n')
    return 0

if __name__ == '__main__': sys.exit(main())
