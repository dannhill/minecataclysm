#!/usr/bin/env python3
"""Native water/aperture regressions in copies of an independent canonical fixture."""
import argparse
import json
from pathlib import Path
import resource
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
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--binary', type=Path)
    parser.add_argument('--expect-abort', action='store_true')
    args = parser.parse_args()
    ws, out = args.workspace.resolve(), args.artifacts.resolve()
    out.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(ws / 'protocol/python'))
    import flatbuffers
    from CDDA.CWM import CwmMessage as Msg, Payload, HelloRequest as Hello
    from CDDA.CWM import MoveRequest as Move, InteractRequest as Interact, Coord3i
    from CDDA.CWM import WorldSnapshot as World, CommandAck as Ack
    from CDDA.CWM import DecisionPrompt as Prompt, DecisionResponse as Response
    checks, events = {}, []

    def check(name, ok):
        checks[name] = bool(ok)
        (out / 'checks.json').write_text(json.dumps(checks, indent=2) + '\n')
        print(name, 'PASS' if ok else 'FAIL', flush=True)
        if not ok:
            raise AssertionError(name)

    def message(kind, build):
        b = flatbuffers.Builder(256)
        payload = build(b)
        Msg.CwmMessageStart(b)
        Msg.CwmMessageAddPayloadType(b, kind)
        Msg.CwmMessageAddPayload(b, payload)
        b.Finish(Msg.CwmMessageEnd(b))
        return bytes(b.Output())

    def read(c):
        def exact(n):
            data = b''
            while len(data) < n:
                part = c.recv(n - len(data))
                if not part:
                    raise EOFError()
                data += part
            return data
        size = struct.unpack('>I', exact(4))[0]
        if size > 16 * 1024 * 1024:
            raise ValueError('oversized frame')
        return Msg.CwmMessage.GetRootAsCwmMessage(exact(size), 0)

    def send(c, kind, build):
        data = message(kind, build)
        c.sendall(struct.pack('>I', len(data)) + data)

    def hello(b):
        Hello.HelloRequestStart(b)
        Hello.HelloRequestAddProtocolVersionMajor(b, 1)
        Hello.HelloRequestAddProtocolVersionMinor(b, 4)
        return Hello.HelloRequestEnd(b)

    def response(b, ident, choice):
        Response.DecisionResponseStart(b)
        Response.DecisionResponseAddDecisionId(b, ident)
        Response.DecisionResponseAddChoice(b, choice)
        return Response.DecisionResponseEnd(b)

    def move(b, ident, direction):
        Move.MoveRequestStart(b)
        Move.MoveRequestAddCommandId(b, ident)
        Move.MoveRequestAddDirection(b, direction)
        return Move.MoveRequestEnd(b)

    def interact(b, ident, target, verb):
        Interact.InteractRequestStart(b)
        Interact.InteractRequestAddCommandId(b, ident)
        Interact.InteractRequestAddAction(b, verb)
        Interact.InteractRequestAddTargetCoord(b, Coord3i.CreateCoord3i(b, *target))
        return Interact.InteractRequestEnd(b)

    for case in (('before',) if args.expect_abort else ('cancel', 'confirm', 'disconnect')):
        root = out / case
        user = root / 'user'
        root.mkdir()
        shutil.copytree(args.fixture.resolve(), user)
        config = user / 'config'
        config.mkdir(exist_ok=True)
        (config / 'options.json').write_text(json.dumps([
            {'name': 'SAFEMODE', 'value': 'false'},
            {'name': 'AUTOSAFEMODE', 'value': 'false'},
            {'name': 'AUTOSAVE', 'value': 'false'}]))
        tiles, state = {}, {}

        def snapshot(msg):
            world = World.WorldSnapshot()
            world.Init(msg.Payload().Bytes, msg.Payload().Pos)
            for i in range(world.ChunksLength()):
                chunk = world.Chunks(i)
                for j in range(chunk.BlocksLength()):
                    block = chunk.Blocks(j)
                    tiles[(chunk.ChunkX() * 16 + j % 16,
                           chunk.ChunkY() * 16 + j // 16, chunk.ChunkZ())] = block.MaterialId()
            for i in range(world.TilesLength()):
                delta = world.Tiles(i)
                tiles[(delta.Coord().X(), delta.Coord().Y(), delta.Coord().Z())] = delta.Block().MaterialId()
            for i in range(world.EntitiesLength()):
                actor = world.Entities(i)
                if actor.Id() == 1:
                    state.update(position=[actor.Pos().X(), actor.Pos().Y(), actor.Pos().Z()],
                                 flags=actor.StateFlags(), time=world.SimulationTimeSeconds())
            events.append({'case': case, 'state': state.copy()})

        def result(c, ident):
            accepted = None
            for _ in range(100):
                msg = read(c)
                if msg.PayloadType() == Payload.Payload.CommandAck:
                    ack = Ack.CommandAck()
                    ack.Init(msg.Payload().Bytes, msg.Payload().Pos)
                    if ack.CommandId() == ident:
                        accepted = ack.Accepted()
                elif msg.PayloadType() == Payload.Payload.WorldSnapshot:
                    snapshot(msg)
                    if accepted is not None:
                        return accepted
            raise RuntimeError('missing action result')

        with tempfile.TemporaryDirectory(prefix='cwm-water-') as temp, (root / 'server.log').open('w') as log:
            path = Path(temp) / 'cwm.sock'
            cmd = [str((args.binary or ws / 'cdda/build/src/cdda-server').resolve()),
                   '--userdir', str(user), '--datadir', str(ws / 'cdda/data'),
                   '--world', 'audit_fixture', '--socket', str(path)]
            def no_core():
                resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
            proc = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, preexec_fn=no_core)
            try:
                deadline = time.monotonic() + 60
                while not path.exists() and proc.poll() is None and time.monotonic() < deadline:
                    time.sleep(.05)
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as c:
                    c.connect(str(path))
                    c.settimeout(15)
                    send(c, Payload.Payload.HelloRequest, hello)
                    while True:
                        msg = read(c)
                        if msg.PayloadType() == Payload.Payload.WorldSnapshot:
                            snapshot(msg)
                            break
                    start = state['position'][:]
                    send(c, Payload.Payload.MoveRequest, lambda b: move(b, 1, 1))
                    if args.expect_abort:
                        try:
                            while True:
                                read(c)
                        except EOFError:
                            pass
                        proc.wait(timeout=15)
                        check('old_binary_reproduces_water_terminal_abort', proc.returncode != 0 and
                              'input_manager::get_input_event called in test mode' in (root / 'server.log').read_text())
                        continue
                    while True:
                        msg = read(c)
                        if msg.PayloadType() == Payload.Payload.WorldSnapshot:
                            snapshot(msg)
                        if msg.PayloadType() == Payload.Payload.DecisionPrompt:
                            prompt = Prompt.DecisionPrompt()
                            prompt.Init(msg.Payload().Bytes, msg.Payload().Pos)
                            break
                    text = prompt.Text().decode()
                    choices = [prompt.Choices(i).decode() for i in range(prompt.ChoicesLength())]
                    check(case + '_native_item_warning', 'matchbook' in text and 'waterproof' in text)
                    check(case + '_safe_cancel_choice', choices[-1] == 'No')
                    check(case + '_no_move_before_confirmation', state['position'] == start)
                    if case == 'disconnect':
                        pass  # Native coordinator must decline when this connection closes.
                    else:
                        send(c, Payload.Payload.DecisionResponse,
                             lambda b: response(b, prompt.DecisionId(), 0 if case == 'confirm' else 1))
                        accepted = result(c, 1)
                        # Native move() handles a declined deep-water choice by
                        # returning true. Verify effects, never infer a step from ACK.
                        check(case + '_native_action_result', accepted)
                        expected = [start[0], start[1] - 1, start[2]] if case == 'confirm' else start
                        check(case + '_native_position', state['position'] == expected)
                        if case == 'confirm':
                            check('swimming_cue_with_native_z_unchanged', state['flags'] & 4 and state['position'][2] == start[2])
                            send(c, Payload.Payload.MoveRequest, lambda b: move(b, 2, 5))
                            check('return_from_swimming', result(c, 2) and state['position'] == start)
                        target = [int(start[0] - 1), int(start[1]), int(start[2])]
                        for ident, verb, material in [(3, 1, 10), (4, 2, 7)]:
                            send(c, Payload.Payload.InteractRequest, lambda b: interact(b, ident, target, verb))
                            check(case + '_window_' + str(verb), result(c, ident) and tiles[tuple(target)] == material)
                            check(case + '_pointed_action_keeps_position_' + str(verb), state['position'] == start)
                        send(c, Payload.Payload.MoveRequest, lambda b: move(b, 5, 5))
                        check(case + '_shallow_water_wading', result(c, 5) and state['flags'] & 2)
                        send(c, Payload.Payload.MoveRequest, lambda b: move(b, 6, 1))
                        check(case + '_return_from_wading', result(c, 6) and state['position'] == start)
                time.sleep(.2)
                proc.terminate()
                proc.wait(timeout=30)
                check(case + '_clean_shutdown', proc.returncode == 0)
            finally:
                if proc.poll() is None:
                    proc.terminate()
                    try:
                        proc.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        proc.wait()
        if not args.expect_abort:
            cmd = [str(args.native_reader.resolve()), '--userdir', str(user),
                   '--datadir', str(ws / 'cdda/data'), '--output', str(root / 'native.json')]
            with (root / 'native.log').open('w') as log:
                readback = subprocess.run(cmd, stdout=log, stderr=subprocess.STDOUT, timeout=120)
            check(case + '_canonical_save_readable', readback.returncode == 0)
            native = json.loads((root / 'native.json').read_text())
            check(case + '_canonical_position_preserved', native['player_abs'] == [60, 60, 0])
            weapon = native['player']['weapon']
            check(case + '_native_water_item_effect', ('ITEM_BROKEN' in weapon.get('item_tags', [])) == (case == 'confirm'))
            check(case + '_no_terminal_abort', 'input_manager::get_input_event' not in (root / 'server.log').read_text())
    (out / 'events.json').write_text(json.dumps(events, indent=2) + '\n')
    return 0 if all(checks.values()) else 1


if __name__ == '__main__':
    sys.exit(main())
