#!/usr/bin/env python3
"""Black-box authority, ordering, idempotency, framing and SAVE-001 takeover probes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import struct
import subprocess
import sys
import tempfile
import time

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace',type=Path,required=True)
    parser.add_argument('--native-reader',type=Path,required=True)
    parser.add_argument('--artifacts',type=Path,required=True)
    args=parser.parse_args()
    ws=args.workspace.resolve();out=args.artifacts.resolve();out.mkdir(parents=True,exist_ok=True)
    sys.path.insert(0,str(ws/'protocol/python'))
    import flatbuffers
    from CDDA.CWM import CwmMessage as Msg, Payload, HelloRequest as Hello, HelloResponse
    from CDDA.CWM import WorldSnapshot, MoveRequest as Move, MoveDirection, CommandAck
    from CDDA.CWM import InteractRequest as Interact, InteractAction, Coord3i, Heartbeat
    checks=[]
    def record(name,ok,**evidence):
        entry={'name':name,'status':'PASS' if ok else 'FAIL',**evidence};checks.append(entry)
        print(json.dumps(entry),flush=True)
        (out/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    def body(module,message):
        value=getattr(module,module.__name__.split('.')[-1])()
        value.Init(message.Payload().Bytes,message.Payload().Pos)
        return value
    def message(kind,build):
        builder=flatbuffers.Builder(256);offset=build(builder)
        Msg.CwmMessageStart(builder)
        Msg.CwmMessageAddSequenceNumber(builder,1)
        Msg.CwmMessageAddPayloadType(builder,kind)
        Msg.CwmMessageAddPayload(builder,offset)
        builder.Finish(Msg.CwmMessageEnd(builder));return bytes(builder.Output())
    def hello(major=1):
        def build(b):
            name=b.CreateString('m55-audit')
            Hello.HelloRequestStart(b);Hello.HelloRequestAddProtocolVersionMajor(b,major)
            Hello.HelloRequestAddBuildId(b,name);return Hello.HelloRequestEnd(b)
        return message(Payload.Payload.HelloRequest,build)
    def move(command=42):
        def build(b):
            Move.MoveRequestStart(b);Move.MoveRequestAddCommandId(b,command)
            Move.MoveRequestAddDirection(b,MoveDirection.MoveDirection.NONE)
            return Move.MoveRequestEnd(b)
        return message(Payload.Payload.MoveRequest,build)
    def use(command,target):
        def build(b):
            Interact.InteractRequestStart(b);Interact.InteractRequestAddCommandId(b,command)
            Interact.InteractRequestAddAction(b,InteractAction.InteractAction.USE)
            coord=Coord3i.CreateCoord3i(b,*target);Interact.InteractRequestAddTargetCoord(b,coord)
            return Interact.InteractRequestEnd(b)
        return message(Payload.Payload.InteractRequest,build)
    def receive(client,timeout=3):
        client.settimeout(timeout)
        def exact(n):
            data=b''
            while len(data)<n:
                chunk=client.recv(n-len(data))
                if not chunk:raise ConnectionError('EOF')
                data+=chunk
            return data
        n=struct.unpack('>I',exact(4))[0]
        if n>16*1024*1024:raise ValueError('oversized server frame')
        data=exact(n);return Msg.CwmMessage.GetRootAsCwmMessage(data,0)
    def send(client,data):client.sendall(struct.pack('>I',len(data))+data)
    def until(client,kind):
        for _ in range(12):
            msg=receive(client)
            if msg.PayloadType()==kind:return msg
        raise RuntimeError('Expected message type not received')

    with tempfile.TemporaryDirectory(prefix='m55-runtime-') as temporary:
        tmp=Path(temporary);user=tmp/'user';sock=tmp/'ipc.sock'
        reader=args.native_reader.resolve()
        fixture=out/'native-fixture.json';loaded=out/'native-loaded.json'
        cmd=[str(reader),'--create','--userdir',str(user),'--datadir',str(ws/'cdda/data'),'--output',str(fixture)]
        with (out/'native-fixture.log').open('w') as log:
            result=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,timeout=180)
        record('native_fixture_creation',result.returncode==0,exit_code=result.returncode)
        if result.returncode:
            shutil.copytree(user,out/'user-state',dirs_exist_ok=True)
            return 1
        cmd=[str(reader),'--userdir',str(user),'--datadir',str(ws/'cdda/data'),'--output',str(loaded)]
        with (out/'native-load.log').open('w') as log:
            result=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,timeout=180)
        record('native_canonical_loader',result.returncode==0,exit_code=result.returncode)
        if result.returncode:
            shutil.copytree(user,out/'user-state',dirs_exist_ok=True)
            return 1
        before=json.loads(fixture.read_text());after=json.loads(loaded.read_text())
        keys=['time','player_abs','terrain_and_furniture']
        # Full avatar serializers contain load-time caches; compare explicit semantic fields.
        inventory_keys=[key for key in before['player'] if any(x in key for x in ['inv','worn','weapon'])]
        equal={key:before[key]==after[key] for key in keys}
        equal['inventory']=all(before['player'].get(k)==after['player'].get(k) for k in inventory_keys)
        equal['monsters']=before['monsters']==after['monsters']
        equal['npcs']=before['npcs']==after['npcs']
        equal['vehicles']=before['vehicles']==after['vehicles']
        record('native_control_roundtrip',all(equal.values()),comparisons=equal,
               categories={'monsters':len(after['monsters']),'npcs':len(after['npcs']),'vehicles':len(after['vehicles'])},
               limitation='Control validates the native oracle only; it does not certify integration SAVE-001.')
        baseline_name=after['player'].get('name')
        log=(out/'cdda-server.log').open('w')
        cmd=['stdbuf','-oL','-eL',str(ws/'cdda/build/src/cdda-server'),'--socket',str(sock),'--world','audit_fixture',
             '--userdir',str(user),'--datadir',str(ws/'cdda/data')]
        server_command=list(cmd)
        proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        client=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
        start=time.monotonic()
        try:
            connected=False
            while time.monotonic()-start<120 and proc.poll() is None:
                try:client.connect(str(sock));connected=True;break
                except (FileNotFoundError,ConnectionRefusedError):time.sleep(.1)
            record('headless_boot',connected,exit_code=proc.poll(),seconds=time.monotonic()-start)
            if not connected:return 1
            # A connection without a handshake must not receive authoritative state.
            prehandshake=None
            try:prehandshake=receive(client,timeout=.5)
            except socket.timeout:pass
            record('no_snapshot_before_handshake',prehandshake is None,
                   observed_payload=prehandshake.PayloadType() if prehandshake else None)
            send(client,hello(65535))
            response=body(HelloResponse,until(client,Payload.Payload.HelloResponse))
            record('unsupported_major_rejected',not response.Accepted(),accepted=response.Accepted())
            snap_msg=until(client,Payload.Payload.WorldSnapshot);snap=body(WorldSnapshot,snap_msg)
            player=snap.Entities(0)
            actual_name=player.Name().decode() if player.Name() else None
            record('saved_avatar_is_loaded',actual_name==baseline_name,
                   native_saved_name=baseline_name,cwm_name=actual_name,
                   native_position=after['player_abs'],cwm_local_position=[player.Pos().X(),player.Pos().Y(),player.Pos().Z()],
                   snapshot_time=snap.SimulationTimeSeconds(),native_time=after['time'])
            # Same command_id twice must cause one action, with a stable acknowledgement.
            observations=[]
            for _ in range(2):
                send(client,move(4242))
                ack=body(CommandAck,until(client,Payload.Payload.CommandAck))
                updated=until(client,Payload.Payload.WorldSnapshot);state=body(WorldSnapshot,updated)
                observations.append({'accepted':ack.Accepted(),'revision':updated.WorldRevision(),'time':state.SimulationTimeSeconds()})
            record('command_idempotency',observations[0]==observations[1],observations=observations)
            record('wait_advances_authoritative_time',observations[-1]['time']>snap.SimulationTimeSeconds(),
                   initial=snap.SimulationTimeSeconds(),after=observations[-1]['time'])
            send(client,use(4243,(1,1,int(player.Pos().Z()))))
            ack=body(CommandAck,until(client,Payload.Payload.CommandAck))
            record('distant_use_is_validated',not ack.Accepted(),accepted=ack.Accepted(),target=[1,1,int(player.Pos().Z())])
            if ack.Accepted():until(client,Payload.Payload.WorldSnapshot)
            # Preserve the unmodified fuzzer result, separately from the stronger framing check.
            cmd=[sys.executable,str(ws/'tools/cdda_fuzzer.py'),'--socket',str(sock),'--iterations','500']
            with (out/'legacy-fuzzer.log').open('w') as fuzzlog:
                result=subprocess.run(cmd,stdout=fuzzlog,stderr=subprocess.STDOUT,timeout=180)
            record('legacy_fuzzer_process_result',result.returncode==0,exit_code=result.returncode,
                   limitation='Legacy fuzzer closes immediately and does not prove server-side decoding.')
            client.close()
            # Keep the peer open so oversized data actually reaches FrameDecoder.
            strict=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);strict.connect(str(sock))
            strict.sendall(struct.pack('>I',16*1024*1024+1))
            time.sleep(.3)
            alive=proc.poll() is None
            record('oversized_frame_preserves_server',alive,exit_code=proc.poll())
            strict.close()
        except Exception as error:
            record('runtime_probe_execution',False,error=repr(error),server_exit_code=proc.poll())
        finally:
            client.close()
            if proc.poll() is None:
                proc.terminate()
                try:proc.wait(timeout=15)
                except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
            log.close()
            shutil.copytree(user,out/'user-state',dirs_exist_ok=True)
            (out/'server-result.json').write_text(json.dumps({'command':server_command,'exit_code':proc.returncode,
                 'binary_sha256':hashlib.sha256((ws/'cdda/build/src/cdda-server').read_bytes()).hexdigest()},indent=2)+'\n')
    return 0 if all(x['status']=='PASS' for x in checks) else 1

if __name__=='__main__':sys.exit(main())
