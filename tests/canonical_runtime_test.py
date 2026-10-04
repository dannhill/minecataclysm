#!/usr/bin/env python3
"""Canonical startup/actions/restart regressions, using disposable native saves.

The reader must be linked to the independent pinned upstream core. This suite
does not certify all SAVE-001 categories or transport/session conformance.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import shutil
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
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    ws, reader, out = args.workspace.resolve(), args.native_reader.resolve(), args.artifacts.resolve()
    out.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(ws/'protocol/python'))
    import flatbuffers
    from CDDA.CWM import (CwmMessage, Payload, HelloRequest, MoveRequest, InteractRequest,
                         Coord3i, AcknowledgeThreatRequest, CommandAck, WorldSnapshot, EntityType)
    checks, commands = [], []

    def check(name, ok, **detail):
        entry = dict(name=name, status='PASS' if ok else 'FAIL', **detail)
        checks.append(entry)
        (out/'checks.json').write_text(json.dumps(checks, indent=2)+'\n')
        print(json.dumps(entry), flush=True)
        return ok

    def record_command(command):
        commands.append(command)
        (out/'commands.json').write_text(json.dumps(commands, indent=2)+'\n')

    def native(user, label, create=False, resave=False):
        command = [str(reader), '--userdir', str(user), '--datadir', str(ws/'cdda/data'),
                   '--output', str(out/(label+'.json'))]
        if create: command.append('--create')
        if resave: command.append('--resave')
        record_command(command)
        with (out/(label+'.log')).open('w') as log:
            proc = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=180)
        if not check('native_'+label, proc.returncode == 0, exit_code=proc.returncode):
            raise RuntimeError('Independent native reader failed: '+label)
        return json.loads((out/(label+'.json')).read_text())

    def server_args(user, sock, world='audit_fixture', extra=()):
        return [str(ws/'cdda/build/src/cdda-server'), '--userdir', str(user),
                '--datadir', str(ws/'cdda/data'), '--world', world, '--socket', str(sock), *extra]

    def run_headless(user, label, world='audit_fixture', extra=(), expected=0):
        command = server_args(user, user.parent/(label+'.sock'), world, extra)
        record_command(command)
        with (out/(label+'.log')).open('w') as log:
            proc = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=180)
        check(label, proc.returncode == expected, exit_code=proc.returncode, expected=expected)
        return proc.returncode

    def message(kind, build):
        builder = flatbuffers.Builder(256)
        payload = build(builder)
        CwmMessage.CwmMessageStart(builder)
        CwmMessage.CwmMessageAddPayloadType(builder, kind)
        CwmMessage.CwmMessageAddPayload(builder, payload)
        builder.Finish(CwmMessage.CwmMessageEnd(builder))
        return bytes(builder.Output())

    def hello():
        def build(b):
            HelloRequest.HelloRequestStart(b)
            HelloRequest.HelloRequestAddProtocolVersionMajor(b, 1)
            HelloRequest.HelloRequestAddProtocolVersionMinor(b, 1)
            return HelloRequest.HelloRequestEnd(b)
        return message(Payload.Payload.HelloRequest, build)

    def move(command, direction):
        def build(b):
            MoveRequest.MoveRequestStart(b)
            MoveRequest.MoveRequestAddCommandId(b, command)
            MoveRequest.MoveRequestAddDirection(b, direction)
            return MoveRequest.MoveRequestEnd(b)
        return message(Payload.Payload.MoveRequest, build)

    def interact(command, coord, action):
        def build(b):
            InteractRequest.InteractRequestStart(b)
            InteractRequest.InteractRequestAddCommandId(b, command)
            InteractRequest.InteractRequestAddAction(b, action)
            InteractRequest.InteractRequestAddTargetCoord(b, Coord3i.CreateCoord3i(b, *coord))
            return InteractRequest.InteractRequestEnd(b)
        return message(Payload.Payload.InteractRequest, build)

    def acknowledge(command):
        def build(b):
            AcknowledgeThreatRequest.AcknowledgeThreatRequestStart(b)
            AcknowledgeThreatRequest.AcknowledgeThreatRequestAddCommandId(b, command)
            return AcknowledgeThreatRequest.AcknowledgeThreatRequestEnd(b)
        return message(Payload.Payload.AcknowledgeThreatRequest, build)

    def read(client):
        def exact(n):
            result = bytearray()
            while len(result) < n:
                data = client.recv(n-len(result))
                if not data: raise EOFError('Backend disconnected')
                result.extend(data)
            return bytes(result)
        size = struct.unpack('>I', exact(4))[0]
        if size > 16*1024*1024: raise ValueError('Oversized server frame')
        return CwmMessage.CwmMessage.GetRootAsCwmMessage(exact(size), 0)

    def state(msg):
        snap = WorldSnapshot.WorldSnapshot()
        snap.Init(msg.Payload().Bytes, msg.Payload().Pos)
        who = next(snap.Entities(i) for i in range(snap.EntitiesLength())
                   if snap.Entities(i).Type() == EntityType.EntityType.PLAYER)
        return dict(name=who.Name().decode(), time=snap.SimulationTimeSeconds(),
                    position=[who.Pos().X()+snap.Origin().X(), who.Pos().Y()+snap.Origin().Y(), who.Pos().Z()],
                    local=[int(who.Pos().X()), int(who.Pos().Y()), int(who.Pos().Z())],
                    revision=msg.WorldRevision(), safety_stop=snap.SafetyStop(),
                    monsters=sum(snap.Entities(i).Type() == EntityType.EntityType.MONSTER
                                 for i in range(snap.EntitiesLength())),
                    npcs=sum(snap.Entities(i).Type() == EntityType.EntityType.NPC
                             for i in range(snap.EntitiesLength())), vehicles=snap.VehiclesLength())

    def send(client, payload): client.sendall(struct.pack('>I', len(payload))+payload)

    def transact(client, payload, command):
        send(client, payload)
        ack = None
        for _ in range(100):
            msg = read(client)
            if msg.PayloadType() == Payload.Payload.CommandAck:
                candidate = CommandAck.CommandAck()
                candidate.Init(msg.Payload().Bytes, msg.Payload().Pos)
                if candidate.CommandId() == command: ack = candidate
            elif ack is not None and msg.PayloadType() == Payload.Payload.WorldSnapshot:
                latest = state(msg)
                # Native next-turn setup can publish an unsolicited state
                # immediately after the action result. Retain that state too.
                deadline = time.monotonic()+2
                while time.monotonic() < deadline and select.select([client], [], [], .2)[0]:
                    following = read(client)
                    if following.PayloadType() == Payload.Payload.WorldSnapshot:
                        latest = state(following)
                return ack.Accepted(), latest
        raise RuntimeError('Missing matching ACK/state')

    with tempfile.TemporaryDirectory(prefix='canonical-runtime-') as temporary:
        scratch = Path(temporary)
        user = scratch/'user'
        native(user, 'fixture', create=True)
        control = native(user, 'control')
        run_headless(user, 'zero_turn_load', extra=('--headless-ticks', '0'))
        zero = native(user, 'zero')
        for category in ('time', 'player_abs', 'terrain_and_furniture', 'monsters', 'npcs', 'vehicles'):
            check('zero_turn_preserves_'+category, zero[category] == control[category])
        check('zero_turn_preserves_inventory', all(zero['player'].get(k) == control['player'].get(k)
              for k in control['player'] if any(t in k for t in ('inv', 'worn', 'weapon'))))
        sock = scratch/'live.sock'
        command = server_args(user, sock)
        record_command(command)
        with (out/'live.log').open('w') as log:
            proc = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.settimeout(12)
            try:
                deadline = time.monotonic()+120
                while time.monotonic() < deadline and proc.poll() is None:
                    try: client.connect(str(sock)); break
                    except (FileNotFoundError, ConnectionRefusedError): time.sleep(.1)
                else: raise RuntimeError('Backend failed to start')
                send(client, hello())
                while True:
                    msg = read(client)
                    if msg.PayloadType() == Payload.Payload.WorldSnapshot:
                        current = state(msg); break
                initial = current.copy()
                check('live_restores_identity_position_time', current['name'] == control['player']['name']
                      and current['position'] == control['player_abs'] and current['time'] == control['time'], state=current)
                # The native startup prelude may spawn reality-bubble groups.
                # A repeated protocol handshake itself must change no actors.
                send(client, hello())
                while True:
                    msg = read(client)
                    if msg.PayloadType() == Payload.Payload.WorldSnapshot:
                        after_hello = state(msg); break
                check('handshake_does_not_spawn_monster', after_hello['monsters'] == current['monsters'])
                current = after_hello
                for cid, payload in ((1, move(1, 127)), (2, interact(2, (1, 1, 0), 7)),
                                     (3, interact(3, tuple(current['local']), 7))):
                    accepted, after = transact(client, payload, cid)
                    check('rejected_action_'+str(cid)+'_preserves_authority', not accepted
                          and all(after[k] == current[k] for k in ('time', 'position', 'revision')),
                          accepted=accepted, before=current, after=after)
                    current = after
                cid = 10
                actions = []
                for direction in (0, 0, 0, 3, 3, 3):
                    accepted = False
                    for _ in range(3):
                        if current['safety_stop']:
                            cid += 1
                            ok, resumed = transact(client, acknowledge(cid), cid)
                            check('threat_resume_'+str(cid)+'_is_free', ok and not resumed['safety_stop']
                                  and resumed['time'] == current['time'] and resumed['position'] == current['position'])
                            current = resumed
                        cid += 1
                        accepted, current = transact(client, move(cid, direction), cid)
                        if accepted: break
                    actions.append(dict(direction=direction, accepted=accepted, state=current.copy()))
                check('wait_and_native_movement_are_accepted', all(a['accepted'] for a in actions), actions=actions)
                check('live_calendar_advances', current['time'] > initial['time'])
                check('door_bump_then_step_changes_position', current['position'] != initial['position'])
                final = current.copy()
                proc.terminate()
                proc.wait(timeout=20)
                check('shutdown_saves_before_native_cleanup', proc.returncode == 0
                      and 'Final save: SUCCESS' in (out/'live.log').read_text())
            finally:
                client.close()
                if proc.poll() is None:
                    proc.terminate()
                    try: proc.wait(timeout=20)
                    except subprocess.TimeoutExpired: proc.kill(); proc.wait()
        saved = native(user, 'saved')
        check('native_reader_restores_last_authoritative_position_time', saved['player_abs'] == final['position']
              and saved['time'] == final['time'], expected=final, actual_position=saved['player_abs'], actual_time=saved['time'])
        check('live_save_keeps_inventory', all(saved['player'].get(k) == control['player'].get(k)
              for k in ('inv', 'worn', 'weapon')))
        # The fixture starts on a native horde-spawn boundary. Compare with
        # the last authoritative state, including newly spawned actors.
        check('live_save_keeps_exported_actor_counts', len(saved['monsters']) == final['monsters']
              and len(saved['vehicles']) == final['vehicles'],
              expected={k:final[k] for k in ('monsters', 'vehicles')},
              observed={k:len(saved[k]) for k in ('monsters', 'vehicles')})
        native_npc_ids = [n['id'] for n in saved['npcs']]
        check('live_save_keeps_native_npc_identity', all(native_npc_ids.count(n['id']) == 1
              for n in control['npcs']), npc_ids=native_npc_ids,
              limitation='NPC presentation is still unimplemented; this checks native persistence only.')
        native_restart = scratch/'native-restart'; shutil.copytree(user, native_restart)
        native(native_restart, 'native_restart_resave', resave=True)
        expected_restart = native(native_restart, 'native_restart_expected')
        run_headless(user, 'restart_zero_turn', extra=('--headless-ticks', '0'))
        restarted = native(user, 'restarted')
        comparisons = {k: expected_restart[k] == restarted[k]
                       for k in ('time', 'player_abs', 'terrain_and_furniture', 'monsters', 'npcs', 'vehicles')}
        check('restart_matches_independent_native_load_save_cycle', all(comparisons.values()), comparisons=comparisons,
              native_npc_load_catchup='Compared to the independent native lifecycle, not raw pre-load NPC caches.')
        multi = scratch/'multi'; shutil.copytree(user, multi)
        original_saves = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in (multi/'save/audit_fixture').glob('*.sav')}
        run_headless(multi, 'new_character_is_explicit', extra=('--new-character', '--character', 'Second Survivor', '--headless-ticks', '0'))
        run_headless(multi, 'multiple_saves_require_selection', extra=('--headless-ticks', '0'), expected=2)
        check('new_character_does_not_overwrite_old_save', all(hashlib.sha256((multi/'save/audit_fixture'/name).read_bytes()).hexdigest() == digest
              for name, digest in original_saves.items()))
        first_id = base64.b64decode(next(iter(original_saves)).removesuffix('.sav')).decode()
        run_headless(multi, 'explicit_saved_character_selection', extra=('--character', first_id, '--headless-ticks', '0'))
        run_headless(multi, 'unknown_character_is_rejected', extra=('--character', 'missing', '--headless-ticks', '0'), expected=2)
        run_headless(multi, 'colliding_character_is_rejected', extra=('--new-character', '--character', control['player']['name'], '--headless-ticks', '0'), expected=2)
        fresh = scratch/'fresh'
        (fresh/'config').mkdir(parents=True)
        # A standalone user's custom default cannot replace the product's
        # approved developer-recommended preset for new worlds.
        (fresh/'config/user-default-mods.json').write_text(json.dumps(
            [dict(type='MOD_INFO', id='user:default', dependencies=['dda'])]))
        run_headless(fresh, 'new_world_recommended_profile', world='profile', extra=('--headless-ticks', '0'))
        mods = json.loads((fresh/'save/profile/mods.json').read_text())
        check('new_world_loads_valid_native_recommended_mods', mods == ['dda', 'no_npc_food', 'personal_portal_storms', 'no_fungal_growth'], mods=mods)
        check('existing_world_keeps_native_mod_profile', json.loads((user/'save/audit_fixture/mods.json').read_text()) == ['dda'])
        shutil.copytree(user, out/'saved-fixture', dirs_exist_ok=True)
    return 0 if all(c['status'] == 'PASS' for c in checks) else 1


if __name__ == '__main__':
    sys.exit(main())
