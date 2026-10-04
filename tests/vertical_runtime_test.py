#!/usr/bin/env python3
"""Native multi-Z transitions, command replay and canonical reload in isolated saves."""
import argparse
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
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    ws, out = args.workspace.resolve(), args.artifacts.resolve()
    out.mkdir(parents=True, exist_ok=False)
    user = out / 'user'
    shutil.copytree(args.fixture.resolve(), user)
    (user / 'config/options.json').write_text(json.dumps([
        {'name': 'SAFEMODE', 'value': 'false'}, {'name': 'AUTOSAFEMODE', 'value': 'false'},
        {'name': 'AUTOSAVE', 'value': 'false'}]))
    sys.path.insert(0, str(ws / 'protocol/python'))
    import flatbuffers
    from session_wire import NativeWire
    from CDDA.CWM import CwmMessage, HelloRequest, HelloResponse, MoveRequest
    from CDDA.CWM import Payload, CommandAck, WorldSnapshot, DecisionPrompt, DecisionResponse
    checks, events = {}, []

    def check(name, ok):
        checks[name] = bool(ok)
        (out / 'checks.json').write_text(json.dumps(checks, indent=2) + '\n')
        print(name, 'PASS' if ok else 'FAIL', flush=True)
        if not ok:
            raise AssertionError(name)

    def parse(msg, module):
        value = getattr(module, module.__name__.split('.')[-1])()
        value.Init(msg.Payload().Bytes, msg.Payload().Pos)
        return value

    class Connection:
        def __init__(self, path):
            self.wire = NativeWire(71)
            self.c = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.c.settimeout(20)
            self.c.connect(str(path))
            b = flatbuffers.Builder(64)
            HelloRequest.HelloRequestStart(b)
            self.wire.hello_fields(b)
            self.wire.send(self.c, b, Payload.Payload.HelloRequest, HelloRequest.HelloRequestEnd(b))
            hello = parse(self.read(), HelloResponse)
            self.next_id = hello.NextCommandId()
            self.state = {}
            self.read()  # ordered WorldReset, covered independently by FND-03
            self.snapshot(self.read())

        def close(self):
            self.c.close()

        def read(self):
            def exact(n):
                data = b''
                while len(data) < n:
                    chunk = self.c.recv(n - len(data))
                    if not chunk:
                        raise EOFError()
                    data += chunk
                return data
            n = struct.unpack('>I', exact(4))[0]
            if n > 16 * 1024 * 1024:
                raise ValueError('oversized native frame')
            return self.wire.observe(self.c, CwmMessage.CwmMessage.GetRootAsCwmMessage(exact(n)))

        def snapshot(self, msg):
            world = parse(msg, WorldSnapshot)
            origin = world.Origin()
            for i in range(world.EntitiesLength()):
                actor = world.Entities(i)
                if actor.Id() == 1:
                    self.state = dict(position=[origin.X() + actor.Pos().X(), origin.Y() + actor.Pos().Y(), actor.Pos().Z()],
                                      flags=actor.StateFlags(), time=world.SimulationTimeSeconds(),
                                      full=world.Full(), revision=world.WorldRevision())
            return world

        def move(self, direction, ident=None):
            if ident is None:
                ident = self.next_id
                self.next_id += 1
            b = flatbuffers.Builder(64)
            MoveRequest.MoveRequestStart(b)
            MoveRequest.MoveRequestAddCommandId(b, ident)
            MoveRequest.MoveRequestAddDirection(b, direction)
            self.wire.send(self.c, b, Payload.Payload.MoveRequest, MoveRequest.MoveRequestEnd(b))
            ack = None
            while True:
                msg = self.read()
                if msg.PayloadType() == Payload.Payload.DecisionPrompt:
                    prompt = parse(msg, DecisionPrompt)
                    # Only the existing native vulnerable-item water question
                    # is expected in this fixture; don't auto-accept other risks.
                    check('water_question_is_native', b'waterproof' in prompt.Text())
                    b = flatbuffers.Builder(64)
                    DecisionResponse.DecisionResponseStart(b)
                    DecisionResponse.DecisionResponseAddDecisionId(b, prompt.DecisionId())
                    DecisionResponse.DecisionResponseAddChoice(b, 0)
                    self.wire.send(self.c, b, Payload.Payload.DecisionResponse, DecisionResponse.DecisionResponseEnd(b))
                if msg.PayloadType() == Payload.Payload.CommandAck:
                    candidate = parse(msg, CommandAck)
                    if candidate.CommandId() == ident:
                        ack = candidate
                if msg.PayloadType() == Payload.Payload.WorldSnapshot:
                    world = self.snapshot(msg)
                    if ack is not None and world.CompletedCommandId() == ident:
                        events.append(dict(id=ident, direction=direction, accepted=ack.Accepted(), **self.state))
                        (out / 'events.json').write_text(json.dumps(events, indent=2) + '\n')
                        return ack, ident

    def expect(c, name, direction, position, accepted=True, flags=None, ident=None):
        ack, ident = c.move(direction, ident)
        check(name, ack.Accepted() == accepted and c.state['position'] == position)
        if flags is not None:
            check(name + '_native_cue', c.state['flags'] & flags == flags)
        return ident

    def native_read(label, expected):
        output = out / (label + '.json')
        command = [str(args.native_reader.resolve()), '--userdir', str(user), '--datadir', str(ws / 'cdda/data'),
                   '--output', str(output)]
        with (out / (label + '.log')).open('w') as log:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=180)
        check(label + '_canonical_readable', result.returncode == 0)
        state = json.loads(output.read_text())
        check(label + '_canonical_position', state['player_abs'] == expected)
        return state

    with tempfile.TemporaryDirectory(prefix='cwm-vertical-') as private:
        path = Path(private) / 'cwm.sock'
        command = [str(ws / 'cdda/build/src/cdda-server'), '--userdir', str(user),
                   '--datadir', str(ws / 'cdda/data'), '--world', 'audit_fixture', '--socket', str(path)]
        (out / 'command.json').write_text(json.dumps(command, indent=2) + '\n')
        def run(label, actions):
            with (out / (label + '.log')).open('w') as log:
                proc = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
                c = None
                try:
                    deadline = time.monotonic() + 80
                    while not path.exists() and proc.poll() is None and time.monotonic() < deadline:
                        time.sleep(.05)
                    check(label + '_started', path.exists() and proc.poll() is None)
                    c = Connection(path)
                    actions(c, path)
                    check(label + '_survives', proc.poll() is None)
                finally:
                    if c:
                        c.close()
                    proc.terminate()
                    try:
                        proc.wait(timeout=35)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        proc.wait()
                check(label + '_clean_shutdown', proc.returncode == 0)

        def stairs(c, path):
            check('inherited_position', c.state['position'] == [60, 60, 0])
            before = c.state['time']
            expect(c, 'up_without_connection_rejected', 9, [60, 60, 0], False)
            expect(c, 'down_without_connection_rejected', 10, [60, 60, 0], False)
            expect(c, 'unknown_direction_rejected', 255, [60, 60, 0], False)
            check('rejected_directions_spend_no_time', c.state['time'] == before)
            expect(c, 'step_on_upstairs', 1, [60, 59, 0], flags=16)
            before = c.state['time']
            ident = expect(c, 'native_ascend', 9, [60, 59, 1], flags=32)
            check('ascend_native_time_and_full_reprojection', c.state['time'] > before and c.state['full'])
            stamp = c.state['time']
            expect(c, 'duplicate_ascend_has_one_effect', 9, [60, 59, 1], ident=ident)
            check('duplicate_does_not_spend_time', c.state['time'] == stamp)
            c.close()
            time.sleep(.15)
            resumed = Connection(path)
            try:
                expect(resumed, 'duplicate_after_reconnect_has_one_effect', 9, [60, 59, 1], ident=ident)
                check('reconnect_duplicate_does_not_spend_time', resumed.state['time'] == stamp)
                expect(resumed, 'native_descend', 10, [60, 59, 0], flags=16)
                expect(resumed, 'return_from_upstairs', 5, [60, 60, 0])
                expect(resumed, 'step_on_downstairs', 5, [60, 61, 0], flags=32)
                expect(resumed, 'native_basement', 10, [60, 61, -1], flags=16)
            finally:
                resumed.close()
        run('stairs', stairs)
        native_read('basement-save', [60, 61, -1])

        def ladder_water(c, path):
            check('negative_z_reloaded', c.state['position'] == [60, 61, -1])
            expect(c, 'return_from_basement', 9, [60, 61, 0])
            expect(c, 'ground_center', 1, [60, 60, 0])
            expect(c, 'ladder_entry', 3, [61, 60, 0], flags=16)
            expect(c, 'ladder_first_floor', 9, [61, 60, 1], flags=48)
            expect(c, 'ladder_second_floor', 9, [61, 60, 2], flags=32)
            expect(c, 'ladder_return_first', 10, [61, 60, 1])
            expect(c, 'ladder_return_ground', 10, [61, 60, 0])
            expect(c, 'native_deep_water', 3, [62, 60, 0], flags=4)
            expect(c, 'dive_keeps_z', 10, [62, 60, 0], flags=8)
            expect(c, 'swim_below_surface', 10, [62, 60, -1], flags=8)
            expect(c, 'swim_to_surface_tile', 9, [62, 60, 0], flags=8)
            expect(c, 'surface_keeps_z', 9, [62, 60, 0], flags=4)
            check('surface_clears_underwater', not c.state['flags'] & 8)
            expect(c, 'leave_water', 7, [61, 60, 0])
            # Native stairfinding permits an offset upper endpoint. Don't force
            # identical XY or invent a client-owned connection.
            for x in range(62, 69):
                expect(c, 'offset_route_' + str(x), 3, [x, 60, 0])
            expect(c, 'offset_entry', 1, [68, 59, 0])
            expect(c, 'native_offset_stairfinding', 9, [70, 59, 1])
        run('ladder-water-offset', ladder_water)
        state = native_read('upper-save', [70, 59, 1])
        terrain = {tuple(t[:3]): t[3] for t in state['terrain_and_furniture']}
        check('native_endpoints_preserved', terrain[(68, 59, 0)] == 't_stairs_up' and
              terrain[(70, 59, 1)] == 't_stairs_down')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
