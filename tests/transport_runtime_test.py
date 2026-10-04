#!/usr/bin/env python3
"""Adverse CWM peers against real CDDA; isolated native fixture and independent reload."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('workspace', 'fixture', 'native-reader', 'artifacts'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    ws, out, native = args.workspace.resolve(), args.artifacts.resolve(), args.native_reader.resolve()
    out.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(ws/'protocol/python'))
    import flatbuffers
    from session_wire import NativeWire
    wire = NativeWire()
    from CDDA.CWM import CwmMessage as Msg, Payload, HelloRequest as Hello, Heartbeat
    from CDDA.CWM import MoveRequest as Move, DecisionPrompt as Prompt, DecisionResponse as Response
    from CDDA.CWM import WorldSnapshot as World
    checks, observations, commands = {}, [], []
    binary = ws/'cdda/build/src/cdda-server'
    identity = dict(binary=str(binary), sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),
                    native_reader=str(native), native_reader_sha256=hashlib.sha256(native.read_bytes()).hexdigest())
    (out/'identity.json').write_text(json.dumps(identity, indent=2)+'\n')
    def check(name, ok):
        checks[name] = bool(ok)
        (out/'checks.json').write_text(json.dumps(checks, indent=2)+'\n')
        print(name, 'PASS' if ok else 'FAIL', flush=True)
        if not ok: raise AssertionError(name)
    def message(kind, build):
        b = flatbuffers.Builder(256); value = build(b)
        body = wire.finish(b,kind,value)
        return struct.pack('>I',len(body))+body
    def hello(b):
        Hello.HelloRequestStart(b); wire.hello_fields(b); return Hello.HelloRequestEnd(b)
    def greeting(): return message(Payload.Payload.HelloRequest, hello)
    def read(c):
        def exact(n):
            data = b''
            while len(data) < n:
                part = c.recv(n-len(data))
                if not part: raise EOFError()
                data += part
            return data
        size = struct.unpack('>I', exact(4))[0]
        if not 0 < size <= 16*1024*1024: raise ValueError('Invalid CWM length')
        return wire.observe(c,Msg.CwmMessage.GetRootAsCwmMessage(exact(size), 0))
    def state(msg):
        world = World.WorldSnapshot(); world.Init(msg.Payload().Bytes, msg.Payload().Pos)
        origin = world.Origin()
        player = next(world.Entities(i) for i in range(world.EntitiesLength()) if world.Entities(i).Id() == 1)
        return [player.Pos().X()+origin.X(), player.Pos().Y()+origin.Y(), player.Pos().Z()]
    user = out/'user'; shutil.copytree(args.fixture.resolve(), user)
    config = user/'config'; config.mkdir(exist_ok=True)
    (config/'options.json').write_text(json.dumps([{'name': key, 'value': 'false'}
        for key in ('SAFEMODE', 'AUTOSAFEMODE', 'AUTOSAVE')]))
    with tempfile.TemporaryDirectory(prefix='cwm-adverse-') as temp, (out/'server.log').open('w') as log:
        path = Path(temp)/'cwm.sock'
        command = [str(binary), '--userdir', str(user), '--datadir', str(ws/'cdda/data'),
                   '--world', 'audit_fixture', '--socket', str(path)]
        commands.append(command)
        proc = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
        def connect():
            c = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); c.settimeout(15); c.connect(str(path)); return c
        def initialized(c, label, fragmented=False):
            if fragmented:
                for byte in greeting(): c.sendall(bytes([byte]))
            else: c.sendall(greeting())
            accepted = full = False; pos = None; revision = None
            for _ in range(20):
                msg = read(c)
                if msg.PayloadType() == Payload.Payload.HelloResponse: accepted = True
                if msg.PayloadType() == Payload.Payload.WorldSnapshot:
                    world = World.WorldSnapshot(); world.Init(msg.Payload().Bytes, msg.Payload().Pos)
                    if world.ChunksLength(): full = True; pos = state(msg); revision = msg.WorldRevision()
                if accepted and full: break
            check(label+'_full_authoritative_snapshot', accepted and full and pos == [60, 60, 0])
            observations.append(dict(label=label, position=pos, revision=revision))
        def eof(c):
            # Include any already-queued valid bytes before the terminal event.
            total = 0
            while True:
                try: data = c.recv(65536)
                except ConnectionResetError: return total
                if not data: return total
                total += len(data)
        try:
            deadline = time.monotonic()+60
            while not path.exists() and proc.poll() is None and time.monotonic() < deadline: time.sleep(.05)
            check('native_runtime_started', path.exists() and proc.poll() is None)
            with connect() as c:
                initialized(c, 'fragmented_hello', True)
                with connect() as extra:
                    eof(extra); check('second_peer_rejected', True)
                def heartbeat(b):
                    Heartbeat.HeartbeatStart(b); return Heartbeat.HeartbeatEnd(b)
                c.sendall(message(Payload.Payload.Heartbeat, heartbeat))
                alive = False
                for _ in range(10):
                    if read(c).PayloadType() == Payload.Payload.HeartbeatAck: alive = True; break
                check('original_client_survives_extra_peer', alive)
            time.sleep(.05)
            for label, wire in [('oversize', struct.pack('>I', 16*1024*1024+1)),
                                ('zero', struct.pack('>I', 0)),
                                ('invalid_flatbuffer', struct.pack('>I', 8)+b'garbage!')]:
                with connect() as c:
                    initialized(c, label+'_before')
                    c.sendall(wire); eof(c)
                check(label+'_peer_closed_runtime_alive', proc.poll() is None)
                with connect() as c: initialized(c, label+'_after')
                time.sleep(.05)
            for label, wire in [('partial_header', b'\x00\x00'),
                                ('partial_body', struct.pack('>I', 256)+b'partial')]:
                with connect() as c:
                    initialized(c, label+'_before'); c.sendall(wire); c.shutdown(socket.SHUT_WR); eof(c)
                check(label+'_runtime_survives', proc.poll() is None)
                with connect() as c: initialized(c, label+'_after')
                time.sleep(.05)
            with connect() as c:
                c.sendall(greeting()); time.sleep(.5)  # Deliberately exceed the old 100-ms timeout.
                hello_seen = snapshot_seen = False
                for _ in range(10):
                    msg = read(c)
                    hello_seen |= msg.PayloadType() == Payload.Payload.HelloResponse
                    snapshot_seen |= msg.PayloadType() == Payload.Payload.WorldSnapshot
                    if hello_seen and snapshot_seen: break
                check('slow_reader_resumes_same_connection', hello_seen and snapshot_seen)
            time.sleep(.05)
            with connect() as c:
                c.sendall(greeting()*400)  # Repeated Hello is now a session violation; queue saturation is tested at transport level.
                time.sleep(2)
                discarded = eof(c)
                observations.append(dict(label='repeated_hello', received_bytes=discarded))
                check('repeated_hello_closes_peer_without_process_loss', proc.poll() is None)
            with connect() as c:
                initialized(c, 'after_repeated_hello')
                def move(b):
                    Move.MoveRequestStart(b); Move.MoveRequestAddCommandId(b, 99)
                    Move.MoveRequestAddDirection(b, 1); return Move.MoveRequestEnd(b)
                c.sendall(message(Payload.Payload.MoveRequest, move))
                for _ in range(20):
                    msg = read(c)
                    if msg.PayloadType() == Payload.Payload.DecisionPrompt:
                        prompt = Prompt.DecisionPrompt(); prompt.Init(msg.Payload().Bytes, msg.Payload().Pos); break
                else: raise AssertionError('No native water prompt')
                check('native_water_prompt_survives_transport_errors', 'matchbook' in prompt.Text().decode())
                def response(b):
                    Response.DecisionResponseStart(b); Response.DecisionResponseAddDecisionId(b, prompt.DecisionId())
                    Response.DecisionResponseAddChoice(b, 0); return Response.DecisionResponseEnd(b)
                c.sendall(message(Payload.Payload.DecisionResponse, response))
                c.shutdown(socket.SHUT_WR); eof(c)  # Final complete response must be consumed before EOF.
            time.sleep(.2)
            check('native_process_alive_after_final_response_and_close', proc.poll() is None)
            proc.terminate(); proc.wait(timeout=30)
            check('canonical_shutdown_after_adverse_peers', proc.returncode == 0)
        finally:
            if proc.poll() is None:
                proc.terminate()
                try: proc.wait(timeout=10)
                except subprocess.TimeoutExpired: proc.kill(); proc.wait()
    command = [str(native), '--userdir', str(user), '--datadir', str(ws/'cdda/data'), '--output', str(out/'native-after.json')]
    commands.append(command)
    with (out/'native-after.log').open('w') as log:
        result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=120)
    check('independent_native_reload', result.returncode == 0)
    canonical = json.loads((out/'native-after.json').read_text())
    check('final_response_effect_persisted', canonical['player_abs'] == [60, 59, 0] and
          'ITEM_BROKEN' in canonical['player']['weapon'].get('item_tags', []))
    positions = [entry['position'] for entry in observations if 'position' in entry]
    check('adverse_peers_did_not_move_avatar', all(pos == [60, 60, 0] for pos in positions))
    revisions = [entry['revision'] for entry in observations if 'revision' in entry]
    check('adverse_peers_did_not_advance_simulation_revision', len(set(revisions)) == 1)
    (out/'observations.json').write_text(json.dumps(observations, indent=2)+'\n')
    (out/'commands.json').write_text(json.dumps(commands, indent=2)+'\n')
    return 0

if __name__ == '__main__': sys.exit(main())
