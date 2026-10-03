#!/usr/bin/env python3
"""Render explicit BM01/BM02 CWM fixtures with the real, unmodified Luanti bridge.

These fixtures isolate presentation. They do not certify CDDA gameplay or its
input-to-visual latency. SDL swap timestamps are measured independently of HUD.
"""
import argparse
import json
import math
import os
from pathlib import Path
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time

def percentile(values, fraction):
    return sorted(values)[max(0, math.ceil(len(values)*fraction)-1)] if values else None

def run(ws, artifacts, probe_library, origin_x=0, origin_y=0):
    sys.path.insert(0, str(ws / "protocol/python"))
    import flatbuffers
    from CDDA.CWM import CwmMessage as Msg, Payload, HelloResponse as Hello
    from CDDA.CWM import WorldSnapshot as World, ChunkSnapshot as Chunk, CwmBlock as Block
    from CDDA.CWM import EntityState as Entity, Vec3f, Coord3i, EntityType
    from CDDA.CWM import CommandAck as Ack, MoveRequest as Move

    def envelope(builder, payload_type, offset, sequence):
        Msg.CwmMessageStart(builder)
        Msg.CwmMessageAddSequenceNumber(builder, sequence)
        Msg.CwmMessageAddWorldRevision(builder, sequence)
        Msg.CwmMessageAddPayloadType(builder, payload_type)
        Msg.CwmMessageAddPayload(builder, offset)
        builder.Finish(Msg.CwmMessageEnd(builder))
        return bytes(builder.Output())

    def hello(sequence):
        b=flatbuffers.Builder(256)
        name=b.CreateString("m55-presentation-fixture")
        Hello.HelloResponseStart(b)
        Hello.HelloResponseAddProtocolVersionMajor(b,1)
        Hello.HelloResponseAddProtocolVersionMinor(b,0)
        Hello.HelloResponseAddServerBuildId(b,name)
        Hello.HelloResponseAddAccepted(b,True)
        offset=Hello.HelloResponseEnd(b)
        return envelope(b,Payload.Payload.HelloResponse,offset,sequence)

    def snapshot(scenario, sequence, player=(8,8), chunks=True, omit_origin=False):
        b=flatbuffers.Builder(1024*1024)
        chunk_offsets=[]
        width=1 if scenario=="BM01" else 9
        levels=[0] if scenario=="BM01" else [0,1]
        if chunks:
            for z in levels:
                for cy in range(width):
                    for cx in range(width):
                        Chunk.ChunkSnapshotStartBlocksVector(b,256)
                        for index in range(255,-1,-1):
                            x,y=index%16,index//16
                            mat=4
                            if x in [0,15] or y in [0,15]:mat=3
                            if (x,y)==(15,7):mat=5
                            if (x,y)==(5,5):mat=9
                            Block.CreateCwmBlock(b,1 if mat==5 else 0,mat,15,0)
                        blocks=b.EndVector()
                        Chunk.ChunkSnapshotStart(b)
                        Chunk.ChunkSnapshotAddChunkX(b,cx)
                        Chunk.ChunkSnapshotAddChunkY(b,cy)
                        Chunk.ChunkSnapshotAddChunkZ(b,z)
                        Chunk.ChunkSnapshotAddSizeX(b,16)
                        Chunk.ChunkSnapshotAddSizeY(b,16)
                        Chunk.ChunkSnapshotAddSizeZ(b,1)
                        Chunk.ChunkSnapshotAddBlocks(b,blocks)
                        chunk_offsets.append(Chunk.ChunkSnapshotEnd(b))
        if chunks:
            World.WorldSnapshotStartChunksVector(b,len(chunk_offsets))
            for offset in reversed(chunk_offsets):b.PrependUOffsetTRelative(offset)
            chunks_vec=b.EndVector()
        else:chunks_vec=0
        offsets=[]
        count=2 if scenario=="BM01" else 150
        for i in range(count):
            name=b.CreateString("Player" if i==0 else "Zombie")
            archetype=b.CreateString("avatar" if i==0 else "mon_zombie")
            Entity.EntityStateStart(b)
            Entity.EntityStateAddId(b,1 if i==0 else 1000+i)
            Entity.EntityStateAddType(b,EntityType.EntityType.PLAYER if i==0 else EntityType.EntityType.MONSTER)
            Entity.EntityStateAddTypeId(b,archetype)
            Entity.EntityStateAddName(b,name)
            Entity.EntityStateAddHpPercent(b,100)
            pos=Vec3f.CreateVec3f(b,player[0] if i==0 else 10+(i%10),player[1] if i==0 else 10+(i//10),0)
            Entity.EntityStateAddPos(b,pos)
            offsets.append(Entity.EntityStateEnd(b))
        World.WorldSnapshotStartEntitiesVector(b,len(offsets))
        for offset in reversed(offsets):b.PrependUOffsetTRelative(offset)
        entities=b.EndVector()
        World.WorldSnapshotStart(b)
        World.WorldSnapshotAddWorldRevision(b,sequence)
        World.WorldSnapshotAddChunks(b,chunks_vec)
        World.WorldSnapshotAddEntities(b,entities)
        World.WorldSnapshotAddSimulationTimeSeconds(b,43200)
        if not omit_origin:
            origin=Coord3i.CreateCoord3i(b,origin_x,origin_y,-1)
            World.WorldSnapshotAddOrigin(b,origin)
        return envelope(b,Payload.Payload.WorldSnapshot,World.WorldSnapshotEnd(b),sequence)

    artifacts.mkdir(parents=True,exist_ok=True)
    results=[]
    game_link=ws/'luanti/games/cdda_voxel'
    if not game_link.exists():game_link.symlink_to(ws/'game',target_is_directory=True)
    for scenario in ["BM01","BM02"]:
        target=artifacts/scenario;target.mkdir(exist_ok=True)
        events=[];stop=threading.Event();inject_invalid=threading.Event();sequence=1
        with tempfile.TemporaryDirectory(prefix="m55-gui-") as temporary:
            directory=Path(temporary);sockpath=directory/'cwm.sock'
            server=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
            server.bind(str(sockpath));server.listen();server.settimeout(1)
            def serve():
                nonlocal sequence
                while not stop.is_set():
                    try:client,_=server.accept()
                    except socket.timeout:continue
                    except OSError:return
                    events.append({'kind':'connected','time_ns':time.monotonic_ns()})
                    try:
                        client.settimeout(1)
                        buf=b'';initialized=False
                        while not stop.is_set():
                            if initialized and inject_invalid.is_set():
                                inject_invalid.clear()
                                body=snapshot(scenario,sequence,chunks=False,omit_origin=True);sequence+=1
                                client.sendall(struct.pack('>I',len(body))+body)
                                events.append({'kind':'missing_origin_injected','time_ns':time.monotonic_ns()})
                            try:data=client.recv(65536)
                            except socket.timeout:continue
                            if not data:break
                            buf+=data
                            while len(buf)>=4 and len(buf)>=4+struct.unpack('>I',buf[:4])[0]:
                                n=struct.unpack('>I',buf[:4])[0];payload=buf[4:4+n];buf=buf[4+n:]
                                msg=Msg.CwmMessage.GetRootAsCwmMessage(payload,0)
                                kind=msg.PayloadType()
                                events.append({'kind':'input','payload_type':kind,'time_ns':time.monotonic_ns()})
                                if kind==Payload.Payload.HelloRequest:
                                    for body in [hello(sequence),snapshot(scenario,sequence+1)]:
                                        client.sendall(struct.pack('>I',len(body))+body)
                                    sequence+=2;initialized=True
                                    events.append({'kind':'initial_snapshot','time_ns':time.monotonic_ns(),'sequence':sequence-1})
                                elif kind==Payload.Payload.MoveRequest and initialized:
                                    request=Move.MoveRequest();request.Init(msg.Payload().Bytes,msg.Payload().Pos)
                                    b=flatbuffers.Builder(128)
                                    Ack.CommandAckStart(b)
                                    Ack.CommandAckAddCommandId(b,request.CommandId())
                                    Ack.CommandAckAddAccepted(b,True)
                                    offset=Ack.CommandAckEnd(b)
                                    body=envelope(b,Payload.Payload.CommandAck,offset,sequence);sequence+=1
                                    client.sendall(struct.pack('>I',len(body))+body)
                                    # Deliberately introduce a sequence gap: production must request resync.
                                    sequence+=1
                                    body=snapshot(scenario,sequence,player=(9,8),chunks=False);sequence+=1
                                    client.sendall(struct.pack('>I',len(body))+body)
                                    events.append({'kind':'sequence_gap_injected','time_ns':time.monotonic_ns()})
                    except Exception as error:events.append({'kind':'server_error','error':repr(error)})
                    finally:client.close()
            thread=threading.Thread(target=serve,daemon=True);thread.start()
            world=directory/'world';world.mkdir()
            (world/'world.mt').write_text('gameid = cdda_voxel\nbackend = sqlite3\nplayer_backend = sqlite3\nauth_backend = sqlite3\nload_mod_cdda_nodes = true\nload_mod_cdda_entities = true\n')
            cfg=target/'client.conf'
            cfg.write_text('name = audit\nenable_damage = false\nfullscreen = false\nscreen_w = 1024\nscreen_h = 768\nfps_max = 120\nfps_max_unfocused = 120\nvsync = false\nvideo_driver = opengl\nprofiler_print_interval = 1\ndebug_log_level = info\nenable_update_checker = false\nscreenshot_path = '+str(target)+'\n')
            env=os.environ.copy();env['LD_PRELOAD']=str(probe_library);env['M55_SOCKET_PATH']=str(sockpath);env['M55_FRAME_LOG']=str(target/'frames.ns')
            cmd=[str(ws/'luanti/bin/luanti'),'--go','--world',str(world),'--gameid','cdda_voxel','--config',str(cfg),'--logfile',str(target/'engine.log'),'--info']
            start=time.monotonic()
            resource_samples=[]
            with (target/'console.log').open('w') as log:
                proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,env=env)
                sampling_stop=threading.Event()
                def sample_resources():
                    while not sampling_stop.is_set():
                        try:
                            stats=Path(f'/proc/{proc.pid}/stat').read_text().rpartition(')')[2].split()
                            memory=Path(f'/proc/{proc.pid}/statm').read_text().split()
                            resource_samples.append({'time_ns':time.monotonic_ns(),
                                'cpu_seconds':(int(stats[11])+int(stats[12]))/os.sysconf('SC_CLK_TCK'),
                                'rss_bytes':int(memory[1])*os.sysconf('SC_PAGE_SIZE')})
                        except (OSError,ValueError,IndexError):return
                        sampling_stop.wait(.1)
                sampling=threading.Thread(target=sample_resources,daemon=True);sampling.start()
                window=None;old_window=None
                try:
                    old_window=subprocess.run(['xdotool','getactivewindow'],capture_output=True,text=True).stdout.strip()
                    for _ in range(50):
                        if proc.poll() is not None:break
                        lookup=subprocess.run(['xdotool','search','--onlyvisible','--pid',str(proc.pid)],capture_output=True,text=True)
                        if lookup.stdout.strip():window=lookup.stdout.strip().splitlines()[0];break
                        time.sleep(.2)
                    if window:
                        subprocess.run(['xdotool','windowactivate','--sync',window],capture_output=True,timeout=5)
                    for _ in range(150):
                        if any(e['kind']=='initial_snapshot' for e in events) or proc.poll() is not None:break
                        time.sleep(.1)
                    time.sleep(4)
                    if window:
                        # Look down into the transmitted room instead of
                        # treating a sky-facing screenshot as scene evidence.
                        subprocess.run(['xdotool','mousemove_relative','--','0','200'],capture_output=True)
                        time.sleep(1)
                        subprocess.run(['import','-window',window,str(target/'scene.png')],capture_output=True,timeout=15)
                        subprocess.run(['xdotool','keydown','--window',window,'w'],capture_output=True)
                        time.sleep(.4)
                        subprocess.run(['xdotool','keyup','--window',window,'w'],capture_output=True)
                        time.sleep(4)
                        subprocess.run(['import','-window',window,str(target/'after-gap.png')],capture_output=True,timeout=15)
                        subprocess.run(['xdotool','key','--window',window,'F3'],capture_output=True)
                        time.sleep(1)
                        subprocess.run(['import','-window',window,str(target/'after-f3.png')],capture_output=True,timeout=15)
                    time.sleep(4)
                    if scenario=='BM02' and any(e['kind']=='initial_snapshot' for e in events):
                        inject_invalid.set()
                        time.sleep(3)
                    alive_after_invalid=proc.poll() is None
                finally:
                    if proc.poll() is None:
                        proc.terminate()
                        try:proc.wait(timeout=10)
                        except subprocess.TimeoutExpired:proc.kill();proc.wait()
                    stop.set();server.close();thread.join(timeout=2)
                    sampling_stop.set();sampling.join(timeout=1)
                    if old_window:subprocess.run(['xdotool','windowactivate',old_window],capture_output=True)
                    shutil.copytree(world,target/'presentation-world',dirs_exist_ok=True)
            stamps=[int(x) for x in (target/'frames.ns').read_text().splitlines()] if (target/'frames.ns').exists() else []
            synced=next((e['time_ns'] for e in events if e['kind']=='initial_snapshot'),None)
            stamps=[x for x in stamps if synced and x>synced+3_000_000_000]
            times=[(b-a)/1e6 for a,b in zip(stamps,stamps[1:])]
            first_gap=next((e['time_ns'] for e in events if e['kind']=='sequence_gap_injected'),None)
            invalid_exercised=any(e['kind']=='missing_origin_injected' for e in events)
            resynced=any(e['kind']=='initial_snapshot' and e['time_ns']>first_gap for e in events) if first_gap else None
            outcome={'scenario':scenario,'fixture_entities':2 if scenario=='BM01' else 150,
                     'fixture_origin':[origin_x,origin_y,-1],
                     'fixture_chunks':1 if scenario=='BM01' else 162,'authoritative_cdda':False,
                     'connected':synced is not None,'duration_seconds':time.monotonic()-start,'exit_code':proc.returncode,
                     'measured_frames':len(times),'frame_time_p50_ms':percentile(times,.5),
                     'frame_time_p95_ms':percentile(times,.95),'frame_time_p99_ms':percentile(times,.99),
                     'measured_average_fps':1000*len(times)/sum(times) if times else None,
                     'sequence_gap_causes_resynchronization':resynced,
                     'semantic_invalid_snapshot_preserves_client':alive_after_invalid if invalid_exercised else None,
                     'rss_peak_bytes':max((s['rss_bytes'] for s in resource_samples),default=None),
                     'cpu_seconds':resource_samples[-1]['cpu_seconds'] if resource_samples else None,
                     'input_to_visual_p95_ms':None,'initial_projection_p95_ms':None,
                     'limitations':['Synthetic CWM presentation fixture; CDDA runtime is not exercised.',
                                    'Swap timestamps measure frame cadence, not confirmed mesh completion.',
                                    'Population is transmitted; entity meshes require separate visual verification.']}
            (target/'events.json').write_text(json.dumps(events,indent=2)+'\n')
            (target/'resources.json').write_text(json.dumps(resource_samples,indent=2)+'\n')
            (target/'result.json').write_text(json.dumps(outcome,indent=2)+'\n')
            results.append(outcome)
            print(json.dumps(outcome),flush=True)
    (artifacts/'results.json').write_text(json.dumps(results,indent=2)+'\n')
    return all(x['connected'] and x['measured_frames']>0 and x['sequence_gap_causes_resynchronization'] is True and
               x['semantic_invalid_snapshot_preserves_client'] is not False for x in results)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace',type=Path,required=True)
    parser.add_argument('--artifacts',type=Path,required=True)
    parser.add_argument('--probe-library',type=Path,required=True)
    parser.add_argument('--origin-x',type=int,default=0)
    parser.add_argument('--origin-y',type=int,default=0)
    args=parser.parse_args()
    sys.exit(0 if run(args.workspace.resolve(),args.artifacts.resolve(),args.probe_library.resolve(),args.origin_x,args.origin_y) else 1)
