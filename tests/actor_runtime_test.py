#!/usr/bin/env python3
"""Native actor identity through multi-Z, bubble offload, reconnect and pristine resave."""
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
    for key in ('workspace', 'fixture', 'native-reader', 'artifacts'):
        parser.add_argument('--' + key, type=Path, required=True)
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
    from CDDA.CWM import CwmMessage, HelloRequest, HelloResponse, WorldSnapshot, Payload
    from CDDA.CWM import MoveRequest, CommandAck, Heartbeat
    checks, history = {}, []

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
            self.wire = NativeWire(81)
            self.c = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.c.settimeout(30)
            self.c.connect(str(path))
            self.actors = {}
            b = flatbuffers.Builder(64)
            HelloRequest.HelloRequestStart(b)
            self.wire.hello_fields(b)
            self.wire.send(self.c, b, Payload.Payload.HelloRequest, HelloRequest.HelloRequestEnd(b))
            self.next_id = parse(self.read(), HelloResponse).NextCommandId()
            self.read()  # ordered reset
            self.snapshot(self.read())
            self.settle()

        def read(self):
            def exact(size):
                data = b''
                while len(data) < size:
                    part = self.c.recv(size - len(data))
                    if not part:
                        raise EOFError()
                    data += part
                return data
            size = struct.unpack('>I', exact(4))[0]
            if not 0 < size <= 16 * 1024 * 1024:
                raise ValueError('Invalid frame size')
            return self.wire.observe(self.c, CwmMessage.CwmMessage.GetRootAsCwmMessage(exact(size)))

        def snapshot(self, msg):
            world = parse(msg, WorldSnapshot)
            origin = world.Origin()
            self.origin = [origin.X(), origin.Y(), origin.Z()]
            self.actors = {}
            for i in range(world.EntitiesLength()):
                actor = world.Entities(i)
                ident = actor.Id()
                if ident in self.actors:
                    raise AssertionError('Duplicate authoritative actor ID')
                self.actors[ident] = dict(id=ident, kind=actor.Type(),
                    type=(actor.TypeId() or b'').decode(), name=(actor.Name() or b'').decode(),
                    position=[origin.X()+actor.Pos().X(), origin.Y()+actor.Pos().Y(), actor.Pos().Z()],
                    perceived=actor.Perceived(), hp=actor.HpPercent())
            self.player = self.actors[1]['position']
            history.append(dict(revision=world.WorldRevision(), origin=self.origin, actors=list(self.actors.values()),
                spawned=[world.Spawned(i).State().Id() for i in range(world.SpawnedLength())],
                removed=[world.Removed(i).Id() for i in range(world.RemovedLength())]))
            return world

        def settle(self):
            b = flatbuffers.Builder(64)
            Heartbeat.HeartbeatStart(b)
            self.wire.send(self.c, b, Payload.Payload.Heartbeat, Heartbeat.HeartbeatEnd(b))
            while True:
                msg = self.read()
                if msg.PayloadType() == Payload.Payload.WorldSnapshot:
                    self.snapshot(msg)
                if msg.PayloadType() == Payload.Payload.HeartbeatAck:
                    return

        def move(self, direction):
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
                    raise AssertionError('Unexpected native decision in harmless fixture')
                if msg.PayloadType() == Payload.Payload.CommandAck:
                    candidate = parse(msg, CommandAck)
                    if candidate.CommandId() == ident:
                        ack = candidate
                if msg.PayloadType() == Payload.Payload.WorldSnapshot:
                    world = self.snapshot(msg)
                    if ack is not None and world.CompletedCommandId() == ident:
                        if not ack.Accepted():
                            raise AssertionError('Native movement rejected')
                        return

    expected = {}
    def identities(c):
        return {a['type']: a['id'] for a in c.actors.values() if a['kind'] != 0}

    def reader(label, resave=False):
        command = [str(args.native_reader.resolve()), '--userdir', str(user), '--datadir', str(ws / 'cdda/data'),
                   '--output', str(out / (label + '.json'))]
        if resave:
            command.append('--resave')
        with (out / (label + '.log')).open('w') as log:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=180)
        check(label + '_pristine_load', result.returncode == 0)
        return json.loads((out / (label + '.json')).read_text())

    with tempfile.TemporaryDirectory(prefix='cwm-actors-') as private:
        path = Path(private) / 'cwm.sock'
        command = [str(ws / 'cdda/build/src/cdda-server'), '--userdir', str(user), '--datadir', str(ws / 'cdda/data'),
                   '--world', 'audit_fixture', '--socket', str(path)]
        (out / 'command.json').write_text(json.dumps(command, indent=2) + '\n')

        def run(label, action):
            with (out / (label + '.log')).open('w') as log:
                proc = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
                c = None
                try:
                    deadline = time.monotonic() + 85
                    while not path.exists() and proc.poll() is None and time.monotonic() < deadline:
                        time.sleep(.05)
                    check(label + '_started', path.exists() and proc.poll() is None)
                    c = Connection(path)
                    action(c)
                    check(label + '_survives', proc.poll() is None)
                finally:
                    if c:
                        c.c.close()
                    proc.terminate()
                    try:
                        proc.wait(timeout=40)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        proc.wait()
                    (out / 'history.json').write_text(json.dumps(history, indent=2) + '\n')
                check(label + '_clean_exit', proc.returncode == 0)

        def depart(c):
            expected.update(identities(c))
            check('native_fixture_has_zombie_dog_and_npc', set(expected) == {'mon_zombie', 'mon_dog', 'npc'})
            check('persistent_namespaces_are_distinct', expected['mon_zombie'] >> 62 == 1 and
                  expected['mon_dog'] >> 62 == 1 and expected['npc'] >> 63 == 1)
            c.move(1)
            c.move(9)
            check('native_upper_floor_reached', c.player == [60,59,1])
            c.move(10)
            c.move(5)
            check('ids_survive_floor_roundtrip', identities(c) == expected)
            old_identity = c.wire.identity
            c.c.close()
            time.sleep(.15)
            resumed = Connection(path)
            try:
                check('same_runtime_reconnect_keeps_actor_ids', identities(resumed) == expected)
                check('reconnect_changes_only_connection_identity', resumed.wire.identity[:2] == old_identity[:2] and
                      resumed.wire.identity[2] != old_identity[2])
                for x in range(61,141):
                    resumed.move(3)
                    check('east_native_position_' + str(x), resumed.player == [x,60,0])
                check('actual_bubble_origin_changed', resumed.origin[0] > 63)
                check('departure_removes_original_actors', not set(expected.values()) & set(resumed.actors))
            finally:
                resumed.c.close()
        run('depart', depart)
        state = reader('offloaded-native-save', True)
        check('far_position_is_canonical', state['player_abs'] == [140,60,0])

        def return_home(c):
            check('far_restart_does_not_resurrect_nearby_actors', not set(expected.values()) & set(c.actors))
            for x in range(139,59,-1):
                c.move(7)
                check('west_native_position_' + str(x), c.player == [x,60,0])
            check('canonical_offload_reload_keeps_original_ids', identities(c) == expected)
        run('return', return_home)
        state = reader('home-native-resave', True)
        check('native_monster_values_preserve_wire_identity',
              {(1 << 62) | int(a['values']['cwm_monster_id']) for a in state['monsters']} ==
              {expected['mon_zombie'], expected['mon_dog']})
        check('native_npc_id_preserved', {(1 << 63) | a['id'] for a in state['npcs']} == {expected['npc']})
        run('after-pristine-writer', lambda c: check('pristine_writer_roundtrip_keeps_actor_ids', identities(c) == expected))
    check('spawn_removal_batches_cover_bubble_departure_return',
          set(expected.values()) <= {i for state in history for i in state['removed']} and
          set(expected.values()) <= {i for state in history for i in state['spawned']})
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
