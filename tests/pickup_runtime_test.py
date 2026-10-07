#!/usr/bin/env python3
"""Real native pickup, pause, replay and pristine-CDDA save verification.

No renderer is involved; UI selection remains a separate implementation slice.
All worlds are created by the independently linked native fixture reader.
"""
import argparse
import json
from pathlib import Path
import select
import socket
import struct
import subprocess
import sys
import tempfile
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('workspace', 'native-reader', 'artifacts'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    ws, reader, out = args.workspace.resolve(), args.native_reader.resolve(), args.artifacts.resolve()
    out.mkdir(parents=True, exist_ok=False)
    user = out / 'user'
    checks = {}

    def check(name, ok):
        checks[name] = bool(ok)
        (out / 'checks.json').write_text(json.dumps(checks, indent=2) + '\n')
        print(name, 'PASS' if ok else 'FAIL', flush=True)
        if not ok:
            raise AssertionError(name)

    def native(label, create=False):
        command = [str(reader), '--userdir', str(user), '--datadir', str(ws / 'cdda/data'),
                   '--output', str(out / (label + '.json'))]
        if create:
            command.append('--create-pickup')
        with (out / (label + '.log')).open('w') as log:
            result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=180)
        check('pristine_reader_' + label, result.returncode == 0)
        return json.loads((out / (label + '.json')).read_text())

    before = native('before', True)
    (user / 'config/options.json').write_text(json.dumps([
        {'name': 'SAFEMODE', 'value': 'false'}, {'name': 'AUTOSAFEMODE', 'value': 'false'},
        {'name': 'AUTOSAVE', 'value': 'false'}]))
    sys.path.insert(0, str(ws / 'protocol/python'))
    import flatbuffers
    from session_wire import NativeWire
    from CDDA.CWM import CwmMessage, Payload, HelloRequest, WorldSnapshot, CommandAck
    from CDDA.CWM import InteractRequest as Interact, Coord3i
    from CDDA.CWM import SimulationControlRequest as Control

    wire = NativeWire(713)
    state, piles, acknowledgements = {}, {}, {}
    pending = b''
    next_id = 1

    def pump(wait=.05):
        nonlocal pending
        if select.select([peer], [], [], wait)[0]:
            data = peer.recv(1 << 20)
            if not data:
                raise EOFError('Native peer closed')
            pending += data
        while len(pending) >= 4:
            size = struct.unpack('>I', pending[:4])[0]
            assert 0 < size <= 16 * 1024 * 1024
            if len(pending) < size + 4:
                break
            msg = CwmMessage.CwmMessage.GetRootAsCwmMessage(pending[4:4+size], 0)
            pending = pending[4+size:]
            wire.observe(peer, msg)
            if msg.PayloadType() == Payload.Payload.CommandAck:
                ack = CommandAck.CommandAck()
                ack.Init(msg.Payload().Bytes, msg.Payload().Pos)
                acknowledgements[ack.CommandId()] = ack.Accepted()
            elif msg.PayloadType() == Payload.Payload.WorldSnapshot:
                world = WorldSnapshot.WorldSnapshot()
                world.Init(msg.Payload().Bytes, msg.Payload().Pos)
                origin = world.Origin()
                state.update(time=world.SimulationTimeSeconds(), completed=world.CompletedCommandId(),
                             origin=(origin.X(), origin.Y()), pause=world.Clock().PauseReasons())
                if world.Full():
                    piles.clear()
                for i in range(world.GroundItemTilesLength()):
                    tile = world.GroundItemTiles(i)
                    coord = tile.Coord()
                    absolute = (coord.X()+origin.X(), coord.Y()+origin.Y(), coord.Z())
                    piles[absolute] = [dict(index=tile.Items(j).StackIndex(),
                        type=tile.Items(j).TypeId().decode(), charges=tile.Items(j).Charges(),
                        counted=tile.Items(j).CountByCharges()) for j in range(tile.ItemsLength())]

    def until(predicate, timeout=20):
        deadline = time.monotonic()+timeout
        while not predicate():
            if time.monotonic() > deadline:
                raise TimeoutError('Native pickup condition timed out')
            pump()

    def send(module, build, ident=None):
        nonlocal next_id
        if ident is None:
            ident = next_id
            next_id += 1
        acknowledgements.pop(ident, None)
        name = module.__name__.split('.')[-1]
        b = flatbuffers.Builder(256)
        build(b, ident, name)
        wire.send(peer, b, getattr(Payload.Payload, name), getattr(module, name+'End')(b))
        until(lambda: ident in acknowledgements and state.get('completed') == ident)
        return ident, acknowledgements[ident]

    def control(action):
        def build(b, ident, name):
            Control.SimulationControlRequestStart(b)
            Control.SimulationControlRequestAddCommandId(b, ident)
            Control.SimulationControlRequestAddAction(b, action)
        return send(Control, build)

    def pickup(target, selected, ident=None):
        def build(b, cid, name):
            type_id = b.CreateString(selected['type'])
            Interact.InteractRequestStart(b)
            Interact.InteractRequestAddCommandId(b, cid)
            Interact.InteractRequestAddAction(b, 3)
            Interact.InteractRequestAddPickupStackIndex(b, selected['index'])
            Interact.InteractRequestAddPickupTypeId(b, type_id)
            Interact.InteractRequestAddPickupCharges(b, selected['charges'])
            Interact.InteractRequestAddPickupCountByCharges(b, selected['counted'])
            Interact.InteractRequestAddTargetCoord(b, Coord3i.CreateCoord3i(b,
                target[0]-state['origin'][0], target[1]-state['origin'][1], target[2]))
        return send(Interact, build, ident)

    with tempfile.TemporaryDirectory(prefix='cwm-pickup-') as scratch:
        path = Path(scratch) / 'cwm.sock'
        command = [str(ws / 'cdda/build/src/cdda-server'), '--continuous', '--userdir', str(user),
                   '--datadir', str(ws / 'cdda/data'), '--world', 'audit_fixture', '--socket', str(path)]
        (out / 'server-command.json').write_text(json.dumps(command, indent=2)+'\n')
        with (out / 'server.log').open('w') as log:
            proc = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
            peer = None
            try:
                deadline = time.monotonic()+85
                while not path.exists() and proc.poll() is None and time.monotonic()<deadline:
                    time.sleep(.05)
                check('server_ready', path.exists() and proc.poll() is None)
                peer = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                peer.connect(str(path))
                b = flatbuffers.Builder(64)
                HelloRequest.HelloRequestStart(b)
                wire.hello_fields(b)
                wire.send(peer, b, Payload.Payload.HelloRequest, HelloRequest.HelloRequestEnd(b))
                until(lambda: state and not state['pause'] & 8)
                x, y, z = before['player_abs']
                target = (x, y-1, z)
                items = piles[target]
                (out / 'initial-selection.json').write_text(json.dumps(
                    dict(target=target, items=items), indent=2)+'\n')
                selected = next(i for i in items if i['type'] == 'matches')
                check('native_projection_contains_guarded_stack', selected['charges'] == 7)
                control(3)  # MENU_OPEN freezes selection time.
                frozen = state['time']
                for _ in range(6):
                    pump(.05)
                check('menu_pauses_native_time', state['time'] == frozen)
                check('pickup_is_not_a_free_transfer_while_menu_is_open', not pickup(target, selected)[1])
                control(4)  # MENU_CLOSE before paying the native activity cost.
                changed = dict(selected, charges=selected['charges']+1)
                check('wrong_guard_rejected_by_native_executor', not pickup(target, changed)[1])
                ident, accepted = pickup(target, selected)
                check('native_pickup_activity_assigned', accepted)
                until(lambda: {i['type'] for i in piles.get(target, [])} == {'rock'})
                check('only_selected_stack_removed_from_projection', True)
                check('completed_command_replay_is_deduplicated', pickup(target, selected, ident)[1])
                control(0)  # PAUSE for a deterministic save/reader boundary.
            finally:
                proc.terminate()
                try:
                    proc.wait(timeout=60)
                except subprocess.TimeoutExpired:
                    proc.kill()
                    proc.wait()
                if peer:
                    peer.close()
        check('native_shutdown_saved', proc.returncode == 0)

    saved = native('after')
    def marked(value, uid):
        if isinstance(value, dict):
            return ([value] if value.get('item_vars', {}).get('uid') == uid else []) + [
                item for child in value.values() for item in marked(child, uid)]
        if isinstance(value, list):
            return [item for child in value for item in marked(child, uid)]
        return []
    selected = marked(saved['player'], 'pickup-selected')
    check('canonical_inventory_contains_one_selected_stack', len(selected) == 1)
    check('canonical_inventory_preserves_all_seven_charges', selected[0]['charges'] == 7)
    check('canonical_ground_preserves_unselected_item', len(marked(saved['ground_items'], 'pickup-untouched')) == 1)
    check('canonical_ground_has_no_duplicate_selected_item', not marked(saved['ground_items'], 'pickup-selected'))


if __name__ == '__main__':
    main()
