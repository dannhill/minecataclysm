#!/usr/bin/env python3
"""Continuous native authority, fractional stop, recovery and canonical persistence."""
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
    for name in ('workspace', 'fixture', 'decision-fixture', 'native-reader', 'artifacts'):
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
    from CDDA.CWM import ContinuousIntentRequest as Continuous
    from CDDA.CWM import MoveRequest, InteractRequest, Coord3i, AcknowledgeThreatRequest as Threat
    from CDDA.CWM import ResyncRequest, SnapshotAck, DecisionPrompt, DecisionResponse
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
            self.prompts = []
            self.auto_ack = True
            self.full_state_id = 0
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
                if self.auto_ack or msg.PayloadType() != Payload.Payload.WorldSnapshot:
                    self.wire.observe(self.sock, msg)
                if msg.PayloadType() == Payload.Payload.HelloResponse:
                    self.next_id = parse(msg, HelloResponse).NextCommandId()
                elif msg.PayloadType() == Payload.Payload.CommandAck:
                    a = parse(msg, CommandAck)
                    self.acks[a.CommandId()] = (a.Accepted(), (a.ErrorMessage() or b'').decode())
                elif msg.PayloadType() == Payload.Payload.WorldSnapshot:
                    w = parse(msg, WorldSnapshot)
                    self.wire.revision = w.WorldRevision()
                    if w.Full():
                        self.full_state_id = w.StateId()
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
                        realtime=clock.Realtime() if clock else False, continuous=clock.ContinuousMotion() if clock else False, actors=actors,
                        origin=[origin.X(), origin.Y(), origin.Z()], completed=w.CompletedCommandId())
                    self.completed.add(w.CompletedCommandId())
                    history.append(dict(wall=time.monotonic(), **self.state))
                    (out / 'history.json').write_text(json.dumps(history, indent=2) + '\n')
                elif msg.PayloadType() == Payload.Payload.DecisionPrompt:
                    prompt=parse(msg, DecisionPrompt)
                    self.prompts.append(dict(id=prompt.DecisionId(), text=prompt.Text().decode(),
                        choices=[prompt.Choices(i).decode() for i in range(prompt.ChoicesLength())]))

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
            self.acks.pop(ident, None)
            self.completed.discard(ident)
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

        def vector(self, x, y, accepted=True):
            return self.complete(self.send(Continuous, dict(X=x, Y=y)), accepted)

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
                x-self.state['origin'][0], y-self.state['origin'][1], int(self.pos()[2])))
            self.wire.send(self.sock, b, Payload.Payload.InteractRequest, InteractRequest.InteractRequestEnd(b))
            return self.complete(ident)


    import math
    def distance(a,b):
        return math.dist(a[:2],b[:2])
    def fractional(pos):
        return any(abs(v-round(v))>.005 for v in pos[:2])
    with tempfile.TemporaryDirectory(prefix='cwm-rt02-') as private:
        path=Path(private)/'cwm.sock'
        command=[str(ws/'cdda/build/src/cdda-server'),'--continuous','--userdir',str(user),
            '--datadir',str(ws/'cdda/data'),'--world','audit_fixture','--socket',str(path)]
        (out/'command.json').write_text(json.dumps(command,indent=2)+'\n')
        with (out/'server.log').open('w') as log:
            proc=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
            c=None
            try:
                deadline=time.monotonic()+85
                while not path.exists() and proc.poll() is None and time.monotonic()<deadline: time.sleep(.05)
                check('native_continuous_server_started',path.exists() and proc.poll() is None)
                c=Connection(path)
                check('native_continuous_negotiates_global_4x',c.state['continuous'] and c.state['realtime'] and c.state['scale']==4 and c.state['pause']==0)
                t=c.state['time']; c.observe(.8)
                check('idle_world_advances_at_global_4x',2<=c.state['time']-t<=4)
                c.vector(float('nan'),0,False); c.vector(float('inf'),0,False); c.vector(2,0,False)
                c.intent(3,False)
                c.complete(c.send(MoveRequest,dict(Direction=3)),False)
                initial=c.pos()[:]
                c.vector(-1,0); c.observe(.055); c.vector(0,0)
                stop=c.pos()[:]
                check('short_tap_moves_and_stops_inside_native_cell',.015<distance(stop,initial)<.45 and fractional(stop))
                c.observe(.5)
                check('release_preserves_fractional_position_without_queue',c.pos()==stop)
                start=stop[:]; c.vector(-.93,-.36); c.observe(.38); c.vector(0,0)
                oblique=c.pos()[:]
                dx,dy=oblique[0]-start[0],oblique[1]-start[1]
                check('arbitrary_direction_is_not_rounded_to_eight_octants',dx<-.3 and dy<-.1 and abs(dy/dx-.36/.93)<.06)
                check('movement_4x_has_native_distance_cadence',.7<distance(oblique,start)<1.9)
                # Direction changes every few milliseconds must not starve the sampler.
                start=c.pos()[:]
                for i in range(10):
                    c.vector(-.9,-.3 if i%2 else -.4); c.observe(.015)
                c.vector(0,0)
                check('frequent_heading_updates_keep_integrating_motion',distance(c.pos(),start)>.25)
                c.vector(-1,0); c.observe(.09); c.control(0)
                paused=c.pos()[:]; t=c.state['time']; c.observe(.7)
                check('pause_freezes_fractional_authority_and_calendar',c.pos()==paused and c.state['time']==t)
                c.vector(-1,0,False); c.control(1); c.observe(.4)
                check('resume_requires_new_intent',c.pos()==paused)
                c.vector(-1,0); c.observe(.11); c.control(3)
                menu=c.pos()[:]; t=c.state['time']; c.observe(.6)
                check('menu_freezes_fractional_position',c.pos()==menu and c.state['time']==t)
                c.control(4); c.observe(.3)
                check('menu_close_does_not_replay_input',c.pos()==menu)
                c.vector(0,0)
                duplicate=c.next_id-1
                c.control(0); frozen=c.pos()[:]
                c.complete(c.send(Continuous,dict(X=0,Y=0),duplicate))
                check('continuous_release_deduplicates',c.pos()==frozen)
                c.control(1)
                c.vector(-1,0); c.observe(.065); c.vector(0,0)
                old_identity=c.wire.identity; stopped=c.pos()[:]; t=c.state['time']
                c.sock.close(); c=None; time.sleep(.6)
                c=Connection(path)
                check('reconnect_retains_exact_subtile_position',distance(c.pos(),stopped)<1e-5 and c.pos()[2]==stopped[2])
                check('reconnect_drops_wall_debt_and_changes_connection',c.state['time']-t<=1 and c.wire.identity[:2]==old_identity[:2] and c.wire.identity[2]!=old_identity[2])
                c.observe(.3); check('reconnect_keeps_player_stopped',c.pos()==stopped)
                c.vector(-1,0); c.until(lambda: distance(c.pos(),stopped)>.05)
                c.auto_ack=False
                b=flatbuffers.Builder(64); ResyncRequest.ResyncRequestStart(b); ResyncRequest.ResyncRequestAddRequestId(b,77)
                c.wire.send(c.sock,b,Payload.Payload.ResyncRequest,ResyncRequest.ResyncRequestEnd(b))
                c.until(lambda: c.state['pause']&8)
                recovery,t=c.pos()[:],c.state['time']; c.observe(.6)
                check('resync_freezes_exact_fraction_until_full_ack',c.pos()==recovery and c.state['time']==t)
                b=flatbuffers.Builder(64); SnapshotAck.SnapshotAckStart(b); SnapshotAck.SnapshotAckAddStateId(b,c.full_state_id)
                c.wire.send(c.sock,b,Payload.Payload.SnapshotAck,SnapshotAck.SnapshotAckEnd(b)); c.auto_ack=True
                c.until(lambda: not c.state['pause']&8); c.observe(.3)
                check('resync_drops_pre_gap_direction',c.pos()==recovery)
                c.control(0); saved_position,saved_time=c.pos()[:],c.state['time']
            finally:
                if c:c.sock.close()
                proc.terminate()
                try:proc.wait(timeout=40)
                except subprocess.TimeoutExpired:proc.kill();proc.wait()
        check('continuous_native_shutdown_saves_cleanly',proc.returncode==0)
    with (out/'canonical.log').open('w') as log:
        result=subprocess.run([str(args.native_reader.resolve()),'--userdir',str(user),'--datadir',str(ws/'cdda/data'),
            '--output',str(out/'canonical.json')],stdout=log,stderr=subprocess.STDOUT,timeout=180)
    check('continuous_save_loads_with_pinned_pristine_cdda',result.returncode==0)
    native=json.loads((out/'canonical.json').read_text())
    state=native['player']['values']['cwm_motion_v1'].split()
    reconstructed=[int(state[0])+float(state[3]),int(state[1])+float(state[4]),int(state[2])]
    check('pristine_reader_preserves_native_anchor_offset_and_time',distance(reconstructed,saved_position)<1e-4 and reconstructed[2]==saved_position[2] and native['time']==saved_time)
    # Native upstream reserialization must preserve extension values.
    with (out/'native-resave.log').open('w') as log:
        result=subprocess.run([str(args.native_reader.resolve()),'--userdir',str(user),'--datadir',str(ws/'cdda/data'),
            '--resave','--output',str(out/'native-resave.json')],stdout=log,stderr=subprocess.STDOUT,timeout=180)
    check('pristine_native_resave_preserves_continuous_values',result.returncode==0 and json.loads((out/'native-resave.json').read_text())['player']['values']['cwm_motion_v1']==native['player']['values']['cwm_motion_v1'])
    with tempfile.TemporaryDirectory(prefix='cwm-rt02-reload-') as private,(out/'reload.log').open('w') as log:
        path=Path(private)/'cwm.sock'; proc=subprocess.Popen(command[:-1]+[str(path)],stdout=log,stderr=subprocess.STDOUT); c=None
        try:
            deadline=time.monotonic()+85
            while not path.exists() and proc.poll() is None and time.monotonic()<deadline:time.sleep(.05)
            check('canonical_continuous_reload_started',path.exists() and proc.poll() is None)
            c=Connection(path)
            check('reload_restores_fractional_position_after_upstream_resave',distance(c.pos(),saved_position)<1e-4 and c.pos()[2]==saved_position[2])
            check('reload_uses_global_4x_without_manual_pause',c.state['scale']==4 and not c.state['pause']&1)
        finally:
            if c:c.sock.close()
            proc.terminate()
            try:proc.wait(timeout=40)
            except subprocess.TimeoutExpired:proc.kill();proc.wait()
    check('reload_shutdown_clean',proc.returncode==0)
    print('continuous native checks:',len(checks),'PASS',flush=True)

if __name__=='__main__':main()
