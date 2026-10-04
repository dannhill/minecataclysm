#!/usr/bin/env python3
"""Native real-time authority, pacing, pause, threat, recovery and canonical save.

Runs the reconstructed server with copies of a pristine-created fixture. No GUI
claim: realtime_gui_test.py independently exercises the installed presentation.
"""
import argparse
import json
from pathlib import Path
import select
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
    from CDDA.CWM import CwmMessage, Payload, HelloRequest, HelloResponse, WorldSnapshot, CommandAck
    from CDDA.CWM import SimulationControlRequest as Control, MovementIntentRequest as Intent
    from CDDA.CWM import MoveRequest, InteractRequest, Coord3i, AcknowledgeThreatRequest as Threat
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
            self.wire = NativeWire(91)
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock.connect(str(path))
            self.buffer = b''
            self.state = None
            self.acks = {}
            self.completed = set()
            b = flatbuffers.Builder(64)
            HelloRequest.HelloRequestStart(b)
            self.wire.hello_fields(b)
            self.wire.send(self.sock, b, Payload.Payload.HelloRequest, HelloRequest.HelloRequestEnd(b))
            self.until(lambda: self.state is not None and not self.state['pause'] & 8)

        def pump(self, wait=.05):
            if select.select([self.sock], [], [], max(0, wait))[0]:
                data = self.sock.recv(1 << 20)
                if not data:
                    raise EOFError('Native connection closed')
                self.buffer += data
            while len(self.buffer) >= 4:
                size = struct.unpack('>I', self.buffer[:4])[0]
                if not 0 < size <= 16 * 1024 * 1024:
                    raise ValueError('Invalid frame size')
                if len(self.buffer) < size + 4:
                    break
                msg = CwmMessage.CwmMessage.GetRootAsCwmMessage(self.buffer[4:size+4])
                self.buffer = self.buffer[size+4:]
                self.wire.observe(self.sock, msg)
                if msg.PayloadType() == Payload.Payload.HelloResponse:
                    self.next_id = parse(msg, HelloResponse).NextCommandId()
                elif msg.PayloadType() == Payload.Payload.CommandAck:
                    a = parse(msg, CommandAck)
                    self.acks[a.CommandId()] = (a.Accepted(), (a.ErrorMessage() or b'').decode())
                elif msg.PayloadType() == Payload.Payload.WorldSnapshot:
                    w = parse(msg, WorldSnapshot)
                    origin = w.Origin()
                    actors = {}
                    for i in range(w.EntitiesLength()):
                        a = w.Entities(i)
                        actors[a.Id()] = dict(id=a.Id(), name=(a.Name() or b'').decode(), kind=a.Type(),
                            pos=[origin.X()+a.Pos().X(), origin.Y()+a.Pos().Y(), a.Pos().Z()],
                            motion=a.MotionSeconds(), perceived=a.Perceived())
                    clock = w.Clock()
                    self.state = dict(time=w.SimulationTimeSeconds(), revision=w.WorldRevision(),
                        pause=clock.PauseReasons() if clock else 0, scale=clock.TimeScale() if clock else 1,
                        realtime=clock.Realtime() if clock else False, actors=actors,
                        origin=[origin.X(), origin.Y(), origin.Z()], completed=w.CompletedCommandId())
                    self.completed.add(w.CompletedCommandId())
                    history.append(dict(wall=time.monotonic(), **self.state))
                    (out / 'history.json').write_text(json.dumps(history, indent=2) + '\n')
                elif msg.PayloadType() == Payload.Payload.DecisionPrompt:
                    raise AssertionError('Unexpected decision in real-time scene')

        def until(self, predicate, timeout=15):
            deadline = time.monotonic() + timeout
            while not predicate():
                if time.monotonic() > deadline:
                    raise TimeoutError('Native state condition timed out')
                self.pump(.05)
            return self.state

        def observe(self, duration):
            deadline = time.monotonic() + duration
            while time.monotonic() < deadline:
                self.pump(min(.05, deadline-time.monotonic()))
            return self.state

        def send(self, module, fields, ident=None):
            name = module.__name__.split('.')[-1]
            if ident is None:
                ident = self.next_id
                self.next_id += 1
            b = flatbuffers.Builder(128)
            getattr(module, name+'Start')(b)
            getattr(module, name+'AddCommandId')(b, ident)
            for key, value in fields.items():
                getattr(module, name+'Add'+key)(b, value)
            self.wire.send(self.sock, b, getattr(Payload.Payload, name), getattr(module, name+'End')(b))
            return ident

        def complete(self, ident, accepted=True):
            self.until(lambda: ident in self.acks and ident in self.completed)
            check('command_' + str(ident) + '_accepted_' + str(accepted), self.acks[ident][0] == accepted)
            return ident

        def control(self, action, scale=1, accepted=True):
            return self.complete(self.send(Control, dict(Action=action, TimeScale=scale)), accepted)

        def intent(self, direction, accepted=True):
            return self.complete(self.send(Intent, dict(Direction=direction)), accepted)

        def pos(self):
            return self.state['actors'][1]['pos']

        def interact(self, x, y, action):
            ident = self.next_id
            self.next_id += 1
            b = flatbuffers.Builder(128)
            InteractRequest.InteractRequestStart(b)
            InteractRequest.InteractRequestAddCommandId(b, ident)
            InteractRequest.InteractRequestAddAction(b, action)
            InteractRequest.InteractRequestAddTargetCoord(b, Coord3i.CreateCoord3i(b,
                x-self.state['origin'][0], y-self.state['origin'][1], self.pos()[2]))
            self.wire.send(self.sock, b, Payload.Payload.InteractRequest, InteractRequest.InteractRequestEnd(b))
            return self.complete(ident)

    with tempfile.TemporaryDirectory(prefix='cwm-rt01-') as private:
        path = Path(private) / 'cwm.sock'
        command = [str(ws / 'cdda/build/src/cdda-server'), '--realtime', '--userdir', str(user),
                   '--datadir', str(ws / 'cdda/data'), '--world', 'audit_fixture', '--socket', str(path)]
        (out / 'command.json').write_text(json.dumps(command, indent=2) + '\n')
        with (out / 'server.log').open('w') as log:
            proc = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT)
            c = None
            try:
                deadline = time.monotonic()+85
                while not path.exists() and proc.poll() is None and time.monotonic()<deadline:
                    time.sleep(.05)
                check('native_server_started', path.exists() and proc.poll() is None)
                time.sleep(2.4)  # No client must not advance the native world.
                c = Connection(path)
                check('realtime_negotiated_1x_without_initial_threat', c.state['realtime'] and c.state['scale']==1 and c.state['pause']==0)
                check('unconnected_startup_does_not_simulate_wall_time', 43200 <= c.state['time'] <= 43201)
                start_time = c.state['time']
                start_actors = {k:v['pos'][:] for k,v in c.state['actors'].items()}
                c.observe(3.2)
                check('idle_default_native_clock_is_1_to_1', 2 <= c.state['time']-start_time <= 4)
                check('native_ai_moves_without_player_input', any(k != 1 and v['pos'] != start_actors.get(k) for k,v in c.state['actors'].items()))
                check('idle_does_not_move_player', c.pos()==[60,60,0])
                c.control(0)
                frozen = (c.state['time'], {k:v['pos'][:] for k,v in c.state['actors'].items()})
                c.observe(1.5)
                check('manual_pause_freezes_native_calendar_and_actors', frozen == (c.state['time'], {k:v['pos'][:] for k,v in c.state['actors'].items()}))
                c.intent(3, False)
                c.control(2, 0, False)
                c.control(2, float('nan'), False)
                c.control(2, 4)
                check('speed_changes_do_not_unpause_or_advance_world', c.state['pause']==1 and c.state['time']==frozen[0])
                c.control(1)
                t = c.state['time']
                c.observe(2.1)
                check('global_4x_scales_native_clock', 6 <= c.state['time']-t <= 9)
                c.control(2, 1)
                c.control(3)
                t = c.state['time']
                c.observe(1.2)
                check('menu_pause_freezes_native_time', c.state['pause']==2 and c.state['time']==t)
                c.control(4)
                c.intent(99, False)
                # Held direction into open corridor; native cost/speed sets cadence.
                c.intent(7)
                c.observe(2.2)
                c.intent(0)
                stopped = c.pos()[:]
                check('held_intent_has_bounded_native_cadence', 57 <= stopped[0] <= 59 and stopped[1:] == [60,0])
                c.observe(1.4)
                check('released_intent_leaves_no_step_queue', c.pos()==stopped)
                # Drain pending explicit requests with correlated negative results.
                c.intent(7)
                c.until(lambda: c.pos() != stopped)
                pending = c.send(MoveRequest, dict(Direction=3))
                pause = c.send(Control, dict(Action=0))
                c.until(lambda: pending in c.acks and pause in c.acks)
                check('pause_acknowledges_cancelled_queued_action', not c.acks[pending][0] and c.acks[pause][0])
                c.observe(.1)
                stopped = c.pos()[:]
                c.control(1)
                c.observe(1.3)
                check('resume_does_not_replay_held_or_cancelled_input', c.pos()==stopped)
                # Pausing while a move interpolates must not create free credit on release.
                c.intent(0)
                duplicate = c.next_id-1
                c.control(0)
                t = c.state['time']
                c.complete(c.send(Intent, dict(Direction=0), duplicate))
                check('duplicate_intent_deduplicates', c.state['time']==t and c.pos()==stopped)
                c.control(1)
                old_identity = c.wire.identity
                c.intent(7)
                c.observe(.3)
                c.sock.close()
                c = None
                time.sleep(1.3)
                c = Connection(path)
                check('reconnect_changes_connection_only', c.wire.identity[:2]==old_identity[:2] and c.wire.identity[2]!=old_identity[2])
                stopped = c.pos()[:]
                t = c.state['time']
                c.observe(.3)
                check('disconnect_loses_wall_debt_and_held_intent', c.pos()==stopped and c.state['time']-t<=1)
                # Approach the closed room from the safe corridor.
                c.control(2,4)
                c.intent(3)
                c.until(lambda: c.pos()[0]>=73)
                c.intent(0)
                check('native_room_approach_stops_outside_closed_door', c.pos()==[73,60,0])
                c.interact(74,60,0)
                c.until(lambda: bool(c.state['pause'] & 4))
                check('new_native_perceived_hostile_autopauses', any(a['name']=='Realtime Threat' and a['perceived'] for a in c.state['actors'].values()))
                t = c.state['time']
                pos = c.pos()[:]
                c.observe(1.2)
                check('threat_pause_freezes_native_time_and_player', c.state['time']==t and c.pos()==pos)
                c.complete(c.send(Threat, {}))
                c.observe(.7)
                check('acknowledgement_resumes_without_repeating_same_threat', c.state['pause']==0 and c.state['time']>t and c.pos()==pos)
                c.control(0)
                saved_position, saved_time = c.pos()[:], c.state['time']
            finally:
                if c:
                    c.sock.close()
                proc.terminate()
                try:
                    proc.wait(timeout=40)
                except subprocess.TimeoutExpired:
                    proc.kill(); proc.wait()
        check('native_shutdown_saves_cleanly', proc.returncode==0)
    with (out / 'canonical.log').open('w') as log:
        result = subprocess.run([str(args.native_reader.resolve()), '--userdir', str(user),
            '--datadir', str(ws / 'cdda/data'), '--output', str(out/'canonical.json')],
            stdout=log, stderr=subprocess.STDOUT, timeout=180)
    check('realtime_save_is_pristine_native_readable', result.returncode==0)
    native = json.loads((out/'canonical.json').read_text())
    check('native_save_preserves_clock_and_position', native['player_abs']==saved_position and native['time']==saved_time)
    with tempfile.TemporaryDirectory(prefix='cwm-rt01-reload-') as private, (out/'reload.log').open('w') as log:
        path = Path(private)/'cwm.sock'
        reload_command = command[:-1]+[str(path)]
        proc = subprocess.Popen(reload_command, stdout=log, stderr=subprocess.STDOUT)
        c = None
        try:
            deadline=time.monotonic()+85
            while not path.exists() and proc.poll() is None and time.monotonic()<deadline:
                time.sleep(.05)
            check('realtime_canonical_reload_started', path.exists() and proc.poll() is None)
            c=Connection(path)
            check('reload_keeps_canonical_position_and_clock',c.pos()==saved_position and saved_time<=c.state['time']<=saved_time+1)
            check('clock_controller_settings_are_volatile', c.state['scale']==1 and not c.state['pause']&1)
        finally:
            if c:
                c.sock.close()
            proc.terminate()
            try:
                proc.wait(timeout=40)
            except subprocess.TimeoutExpired:
                proc.kill(); proc.wait()
    check('reloaded_native_shutdown_is_clean', proc.returncode==0)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
