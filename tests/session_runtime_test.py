#!/usr/bin/env python3
"""Session/at-most-once behavior against real CDDA, on an independent save copy."""
import argparse, hashlib, json, shutil, socket, struct, subprocess, sys, tempfile, time
from pathlib import Path

def main():
    p=argparse.ArgumentParser()
    for name in ('workspace','fixture','artifacts'): p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args(); ws=args.workspace.resolve(); out=args.artifacts.resolve(); out.mkdir(parents=True)
    sys.path.insert(0,str(ws/'protocol/python'))
    import flatbuffers
    from session_wire import NativeWire
    from CDDA.CWM import CwmMessage as Msg, Payload, HelloRequest, HelloResponse, MoveRequest, WorldSnapshot, CommandAck, ResyncRequest, WorldReset
    checks={}; events=[]
    def check(name,value):
        checks[name]=bool(value); (out/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
        print(name,'PASS' if value else 'FAIL',flush=True)
        if not value: raise AssertionError(name)
    def parse(msg,module):
        obj=getattr(module,module.__name__.split('.')[-1])(); obj.Init(msg.Payload().Bytes,msg.Payload().Pos); return obj
    def raw_read(c):
        def exact(n):
            result=b''
            while len(result)<n:
                body=c.recv(n-len(result))
                if not body: raise EOFError()
                result+=body
            return result
        return Msg.CwmMessage.GetRootAsCwmMessage(exact(struct.unpack('>I',exact(4))[0]),0)
    def send(c,wire,kind,build):
        b=flatbuffers.Builder(128); payload=build(b); wire.send(c,b,kind,payload)
    def hello(b,wire,major=2):
        HelloRequest.HelloRequestStart(b); wire.hello_fields(b)
        HelloRequest.HelloRequestAddProtocolVersionMajor(b,major); return HelloRequest.HelloRequestEnd(b)
    def move(b,ident,direction):
        MoveRequest.MoveRequestStart(b); MoveRequest.MoveRequestAddCommandId(b,ident)
        MoveRequest.MoveRequestAddDirection(b,direction); return MoveRequest.MoveRequestEnd(b)
    def eof(c):
        try:
            while c.recv(65536): pass
        except ConnectionResetError: pass
    def position(msg):
        w=parse(msg,WorldSnapshot); a=next(w.Entities(i) for i in range(w.EntitiesLength()) if w.Entities(i).Id()==1)
        return [w.Origin().X()+a.Pos().X(),w.Origin().Y()+a.Pos().Y(),a.Pos().Z()]
    user=out/'user'; shutil.copytree(args.fixture.resolve(),user)
    config=user/'config'; config.mkdir(exist_ok=True)
    (config/'options.json').write_text(json.dumps([{'name':n,'value':'false'} for n in ('SAFEMODE','AUTOSAFEMODE','AUTOSAVE')]))
    binary=ws/'cdda/build/src/cdda-server'
    (out/'identity.json').write_text(json.dumps({'binary':str(binary),'sha256':hashlib.sha256(binary.read_bytes()).hexdigest()},indent=2)+'\n')
    with tempfile.TemporaryDirectory(prefix='cwm-session-') as temp:
        path=Path(temp)/'cwm.sock'
        command=[str(binary),'--userdir',str(user),'--datadir',str(ws/'cdda/data'),'--world','audit_fixture','--socket',str(path)]
        (out/'command.json').write_text(json.dumps(command,indent=2)+'\n')
        def start(label):
            log=(out/(label+'.log')).open('w'); proc=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
            end=time.monotonic()+80
            while not path.exists() and proc.poll() is None and time.monotonic()<end: time.sleep(.05)
            check(label+'_started',path.exists() and proc.poll() is None)
            return proc,log
        def connect():
            c=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM); c.settimeout(15); c.connect(str(path)); return c
        def initialize(c,wire,ack=True):
            send(c,wire,Payload.Payload.HelloRequest,lambda b:hello(b,wire))
            h=raw_read(c); response=parse(h,HelloResponse)
            check('accepted_version_and_identity',response.Accepted() and response.ProtocolVersionMajor()==2 and all((h.SessionId(),h.PlayerId(),h.ConnectionId())))
            wire.observe(c,h)
            reset=raw_read(c); full=raw_read(c)
            check('ordered_reset_then_full',reset.SequenceNumber()==2 and reset.PayloadType()==Payload.Payload.WorldReset and full.SequenceNumber()==3 and parse(full,WorldSnapshot).Full())
            if ack: wire.observe(c,full)
            return full,response.NextCommandId()
        def result(c,wire,ident):
            ack=None
            for _ in range(50):
                msg=wire.observe(c,raw_read(c))
                if msg.PayloadType()==Payload.Payload.CommandAck:
                    candidate=parse(msg,CommandAck)
                    if candidate.CommandId()==ident: ack=candidate
                if msg.PayloadType()==Payload.Payload.WorldSnapshot and parse(msg,WorldSnapshot).CompletedCommandId()==ident and ack is not None:
                    events.append({'id':ident,'accepted':ack.Accepted(),'revision':ack.ResultRevision(),'position':position(msg)})
                    return ack,msg
            raise AssertionError('No matching command state')
        proc,log=start('first')
        try:
            with connect() as c:
                c.settimeout(.15)
                try: c.recv(1); silent=False
                except socket.timeout: silent=True
                check('no_state_before_hello',silent); c.settimeout(15)
                wire=NativeWire(); send(c,wire,Payload.Payload.MoveRequest,lambda b:move(b,1,5))
                msg=raw_read(c); check('prehello_command_rejected',not parse(msg,HelloResponse).Accepted()); eof(c)
            time.sleep(.1)
            with connect() as c:
                wire=NativeWire(); send(c,wire,Payload.Payload.HelloRequest,lambda b:hello(b,wire,99))
                msg=raw_read(c); check('unsupported_version_rejected',not parse(msg,HelloResponse).Accepted()); eof(c)
            time.sleep(.1)
            with connect() as c:
                wire=NativeWire(77); initial,floor=initialize(c,wire,False); first_identity=wire.identity
                send(c,wire,Payload.Payload.MoveRequest,lambda b:move(b,1,5))
                c.settimeout(.2)
                try: raw_read(c); blocked=False
                except socket.timeout: blocked=True
                check('command_blocked_until_snapshot_ack',blocked); c.settimeout(15); wire.observe(c,initial)
                ident=max(7,floor)
                send(c,wire,Payload.Payload.MoveRequest,lambda b:move(b,ident,5))
                send(c,wire,Payload.Payload.MoveRequest,lambda b:move(b,ident,5))
                ack,world=result(c,wire,ident)
                check('queued_duplicate_executes_once',ack.Accepted() and position(world)==[60,61,0])
                original_revision=ack.ResultRevision()
                send(c,wire,Payload.Payload.MoveRequest,lambda b:move(b,ident,5))
                ack,world=result(c,wire,ident)
                check('completed_duplicate_replays_original_result',position(world)==[60,61,0] and ack.ResultRevision()==original_revision and parse(world,WorldSnapshot).Full())
                def resync(b):
                    ResyncRequest.ResyncRequestStart(b); ResyncRequest.ResyncRequestAddRequestId(b,91); return ResyncRequest.ResyncRequestEnd(b)
                send(c,wire,Payload.Payload.ResyncRequest,resync)
                reset=raw_read(c); world=wire.observe(c,raw_read(c))
                check('resync_correlated_full_state',parse(reset,WorldReset).RequestId()==91 and parse(world,WorldSnapshot).ResyncId()==91 and parse(world,WorldSnapshot).Full() and position(world)==[60,61,0])
            time.sleep(.15)
            with connect() as c:
                wire=NativeWire(77); world,floor=initialize(c,wire)
                check('reconnect_same_session_new_connection_and_floor',wire.identity[:2]==first_identity[:2] and wire.identity[2]!=first_identity[2] and floor>ident)
                send(c,wire,Payload.Payload.MoveRequest,lambda b:move(b,ident,5)); ack,world=result(c,wire,ident)
                check('duplicate_after_reconnect_has_no_second_effect',position(world)==[60,61,0] and ack.ResultRevision()==original_revision)
                send(c,wire,Payload.Payload.MoveRequest,lambda b:move(b,ident,3)); eof(c)
                check('conflicting_duplicate_disconnects_without_effect',proc.poll() is None)
            time.sleep(.15)
            with connect() as c:
                wire=NativeWire(78); world,floor=initialize(c,wire)
                check('conflict_did_not_move_character',position(world)==[60,61,0])
                wire.identity=first_identity
                send(c,wire,Payload.Payload.MoveRequest,lambda b:move(b,floor,3)); eof(c)
                check('stale_connection_identity_rejected',proc.poll() is None)
            time.sleep(.15)
            with connect() as c:
                wire=NativeWire(79); world,floor=initialize(c,wire)
                check('stale_command_had_no_gameplay_effect',position(world)==[60,61,0])
            proc.terminate(); proc.wait(timeout=40); check('canonical_shutdown',proc.returncode==0)
        finally:
            if proc.poll() is None: proc.terminate(); proc.wait(timeout=40)
            log.close()
        proc,log=start('restart')
        try:
            with connect() as c:
                wire=NativeWire(77); world,floor=initialize(c,wire)
                check('new_server_has_new_session_identity',wire.identity[0]!=first_identity[0])
                check('canonical_restart_preserves_position',position(world)==[60,61,0])
                wire.identity=first_identity
                send(c,wire,Payload.Payload.MoveRequest,lambda b:move(b,ident,3)); eof(c)
                check('old_session_command_cannot_mutate_new_server',proc.poll() is None)
        finally:
            if proc.poll() is None: proc.terminate(); proc.wait(timeout=40)
            log.close()
    (out/'events.json').write_text(json.dumps(events,indent=2)+'\n')
    return 0
if __name__=='__main__': sys.exit(main())
