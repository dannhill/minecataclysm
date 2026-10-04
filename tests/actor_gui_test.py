#!/usr/bin/env python3
"""Actual Luanti scene lifecycle under controlled CWM visibility, rebases and recovery.

The peer is synthetic. Native identity/save/offload semantics are covered by
actor_runtime_test.py; this test observes real scene nodes and interpolation.
"""
import argparse
import csv
import json
import os
from pathlib import Path
import queue
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('workspace', 'artifacts'):
        parser.add_argument('--' + key, type=Path, required=True)
    args = parser.parse_args()
    ws, out = args.workspace.resolve(), args.artifacts.resolve()
    out.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(ws / 'protocol/python'))
    import flatbuffers
    from session_wire import AuthorityWire
    from CDDA.CWM import CwmMessage, Payload, HelloResponse, ResyncRequest
    from CDDA.CWM import WorldSnapshot as World, ChunkSnapshot as Chunk, CwmBlock as Block
    from CDDA.CWM import EntityState as Entity, Vec3f, Coord3i
    monster_id, npc_id = (1 << 62) | 2, (1 << 63) | 3
    actors = [{'id':monster_id, 'kind':2, 'type':'mon_zombie', 'pos':[8,8,0], 'seen':True},
              {'id':npc_id, 'kind':1, 'type':'npc', 'pos':[6,8,0], 'seen':True}]
    commands, receipts = queue.Queue(), queue.Queue()
    stop, errors, checks = threading.Event(), [], {}
    trace, camera = out / 'actors.csv', out / 'camera.csv'
    origin = [0,0]
    old_window = subprocess.run(['xdotool','getactivewindow'],capture_output=True,text=True).stdout.strip()

    def check(name, ok):
        checks[name] = bool(ok)
        (out / 'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
        print(name, 'PASS' if ok else 'FAIL', flush=True)
        if not ok:
            raise AssertionError(name)

    def rows(path):
        if not path.exists():
            return []
        with path.open() as stream:
            return [row for row in csv.DictReader(stream) if None not in row.values()]

    def latest():
        data = rows(trace)
        if not data:
            return {}
        stamp = data[-1]['time_ns']
        return {int(row['id']):row for row in data if row['time_ns'] == stamp}

    def until(predicate, timeout=15):
        deadline = time.monotonic()+timeout
        while time.monotonic()<deadline and proc.poll() is None:
            data = latest()
            if data and predicate(data):
                return data
            time.sleep(.025)
        raise RuntimeError('Actor scene condition timed out; inspect traces and engine log')

    def coords(row, prefix):
        return tuple(float(row[prefix+'_'+axis]) for axis in ('x','y','z'))

    def update(action, value=None):
        commands.put((action,value))
        revision = receipts.get(timeout=15)
        if isinstance(revision, BaseException):
            raise revision
        return revision

    def frame(data):
        return struct.pack('>I',len(data))+data

    def snapshot(wire, full=False, bad_kind=False):
        b = flatbuffers.Builder(8192)
        chunks = 0
        if full:
            parts=[]
            for cx in (-1,0,1):
                Chunk.ChunkSnapshotStartBlocksVector(b,256)
                for _ in range(256):
                    Block.CreateCwmBlock(b,0,4,15,0)
                blocks=b.EndVector()
                Chunk.ChunkSnapshotStart(b)
                Chunk.ChunkSnapshotAddChunkX(b,cx)
                Chunk.ChunkSnapshotAddSizeX(b,16); Chunk.ChunkSnapshotAddSizeY(b,16)
                Chunk.ChunkSnapshotAddSizeZ(b,1); Chunk.ChunkSnapshotAddBlocks(b,blocks)
                parts.append(Chunk.ChunkSnapshotEnd(b))
            World.WorldSnapshotStartChunksVector(b,len(parts))
            for part in reversed(parts): b.PrependUOffsetTRelative(part)
            chunks=b.EndVector()
        states=[]
        for actor in [{'id':1,'kind':0,'type':'avatar','pos':[8,12,0],'seen':True}, *actors]:
            type_name=b.CreateString(actor['type'])
            Entity.EntityStateStart(b)
            Entity.EntityStateAddId(b,actor['id'])
            kind=1 if bad_kind and actor['id']==monster_id else actor['kind']
            Entity.EntityStateAddType(b,kind)
            Entity.EntityStateAddTypeId(b,type_name)
            Entity.EntityStateAddHpPercent(b,100)
            Entity.EntityStateAddPerceived(b,actor['seen'])
            Entity.EntityStateAddPos(b,Vec3f.CreateVec3f(b,actor['pos'][0]-origin[0],actor['pos'][1]-origin[1],actor['pos'][2]))
            states.append(Entity.EntityStateEnd(b))
        World.WorldSnapshotStartEntitiesVector(b,len(states))
        for state in reversed(states): b.PrependUOffsetTRelative(state)
        roster=b.EndVector(); empty=wire.empty_vectors(b)
        World.WorldSnapshotStart(b); wire.world_fields(b,full,empty)
        World.WorldSnapshotAddEntities(b,roster)
        World.WorldSnapshotAddOrigin(b,Coord3i.CreateCoord3i(b,84000+origin[0],-42000+origin[1],-1))
        if full: World.WorldSnapshotAddChunks(b,chunks)
        return wire.finish(b,Payload.Payload.WorldSnapshot,World.WorldSnapshotEnd(b))

    with tempfile.TemporaryDirectory(prefix='cwm-actor-gui-') as private:
        path=Path(private)/'cwm.sock'
        listener=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
        listener.bind(str(path)); listener.listen(1); listener.settimeout(.2)
        def serve():
            nonlocal actors
            connection_index=0
            last_revision=0
            try:
                while not stop.is_set():
                    try: c,_=listener.accept()
                    except socket.timeout: continue
                    connection_index+=1
                    with c:
                        c.settimeout(15)
                        def exact(size):
                            data=b''
                            while len(data)<size:
                                part=c.recv(size-len(data))
                                if not part: raise EOFError()
                                data+=part
                            return data
                        size=struct.unpack('>I',exact(4))[0]
                        msg=CwmMessage.CwmMessage.GetRootAsCwmMessage(exact(size))
                        if msg.PayloadType()!=Payload.Payload.HelloRequest: raise ValueError('Missing Hello')
                        wire=AuthorityWire(connection=connection_index,session=88 if connection_index<3 else 99)
                        wire.revision=last_revision if connection_index<3 else 0
                        b=flatbuffers.Builder(128); HelloResponse.HelloResponseStart(b)
                        HelloResponse.HelloResponseAddAccepted(b,True); wire.hello_fields(b)
                        c.sendall(frame(wire.finish(b,Payload.Payload.HelloResponse,HelloResponse.HelloResponseEnd(b)))+
                                  frame(wire.reset())+frame(snapshot(wire,True)))
                        c.settimeout(.02); buffer=b''; recovery=None
                        while not stop.is_set():
                            if recovery and time.monotonic()>=recovery[0]:
                                c.sendall(frame(wire.reset(recovery[1]))+frame(snapshot(wire,True)))
                                recovery=None
                            try: data=c.recv(65536)
                            except socket.timeout: data=None
                            if data==b'': break
                            if data:
                                buffer+=data
                                while len(buffer)>=4:
                                    size=struct.unpack('>I',buffer[:4])[0]
                                    if len(buffer)<size+4: break
                                    msg=CwmMessage.CwmMessage.GetRootAsCwmMessage(buffer[4:size+4]); buffer=buffer[size+4:]
                                    if msg.PayloadType()==Payload.Payload.ResyncRequest:
                                        value=ResyncRequest.ResyncRequest(); value.Init(msg.Payload().Bytes,msg.Payload().Pos)
                                        recovery=(time.monotonic()+.65,value.RequestId())
                            try: action,value=commands.get_nowait()
                            except queue.Empty: continue
                            if action=='disconnect':
                                receipts.put(wire.revision); break
                            if action=='actors': actors=value
                            if action=='rebase': origin[:]=value
                            c.sendall(frame(snapshot(wire, action=='rebase', action=='bad-kind')))
                            receipts.put(wire.revision)
                        last_revision=wire.revision
            except Exception as error:
                if not stop.is_set(): errors.append(repr(error)); receipts.put(error)
        thread=threading.Thread(target=serve,daemon=True); thread.start()
        world=out/'world'; world.mkdir()
        (world/'world.mt').write_text('gameid = cdda_voxel\nbackend = sqlite3\nplayer_backend = sqlite3\nauth_backend = sqlite3\n')
        with socket.socket() as port_socket:
            port_socket.bind(('127.0.0.1',0)); port=port_socket.getsockname()[1]
        config=out/'client.conf'
        config.write_text(f'screen_w = 1024\nscreen_h = 768\nfullscreen = false\nfps_max = 60\nfps_max_unfocused = 60\n'
            f'vsync = false\nenable_clouds = false\nenable_update_checker = false\n'
            f'cwm_socket_path = {path}\ncwm_trace_file = {camera}\ncwm_entity_trace_file = {trace}\nport = {port}\n')
        link=ws/'luanti/games/cdda_voxel'
        if not link.exists(): link.parent.mkdir(parents=True,exist_ok=True); link.symlink_to(ws/'game')
        command=[str(ws/'luanti/bin/luanti'),'--go','--world',str(world),'--gameid','cdda_voxel','--config',str(config),
                 '--name','actor_tester','--info','--logfile',str(out/'engine.log')]
        (out/'command.json').write_text(json.dumps(command,indent=2)+'\n')
        with (out/'console.log').open('w') as log:
            proc=subprocess.Popen(command,cwd=ws/'luanti',stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            try:
                initial=until(lambda data: monster_id in data and npc_id in data and
                    all(data[i]['node_visible']=='1' for i in (monster_id,npc_id)),85)
                found=subprocess.run(['xdotool','search','--onlyvisible','--pid',str(proc.pid)],capture_output=True,text=True)
                window=found.stdout.splitlines()[0]
                subprocess.run(['xdotool','windowactivate','--sync',window],check=True,capture_output=True)
                generations={i:initial[i]['node_generation'] for i in (monster_id,npc_id)}
                check('real_zombie_and_npc_meshes_created', initial[1]['scene_actors']=='2')
                subprocess.run(['import','-window',window,str(out/'initial.png')],check=True)
                moved=[dict(a,pos=[a['pos'][0]+1,a['pos'][1],a['pos'][2]]) for a in actors]
                rev=update('actors',moved)
                settled=until(lambda data: int(data[1]['revision'])==rev and coords(data[monster_id],'current')==coords(data[monster_id],'target'))
                check('motion_preserves_owned_nodes', all(settled[i]['node_generation']==generations[i] for i in generations))
                movement=[r for r in rows(trace) if int(r['id'])==monster_id and int(r['revision'])==rev]
                check('perceived_motion_interpolates_confirmed_positions', any(coords(r,'current')!=coords(r,'target') for r in movement))
                target=coords(settled[monster_id],'target')
                rev=update('rebase',[12,0])
                rebased=until(lambda data: int(data[1]['revision'])==rev)
                check('origin_rebase_preserves_actor_scene_position',coords(rebased[monster_id],'target')==target and
                      rebased[monster_id]['node_generation']==generations[monster_id])
                hidden=[dict(a,seen=False,pos=[14,7,0]) for a in actors]
                rev=update('actors',hidden)
                concealed=until(lambda data: int(data[1]['revision'])==rev and data[1]['visible_actors']=='0')
                check('native_unperceived_state_hides_all_actor_nodes',concealed[1]['scene_actors']=='2')
                revealed=[dict(a,seen=True,pos=[7 if a['kind']==2 else 5,7,0]) for a in actors]
                rev=update('actors',revealed)
                seen=until(lambda data: int(data[1]['revision'])==rev and data[1]['visible_actors']=='2')
                first=[r for r in rows(trace) if int(r['id'])==monster_id and int(r['revision'])==rev][0]
                check('reappearance_does_not_animate_unseen_path',coords(first,'current')==coords(first,'target'))
                check('visibility_toggle_reuses_single_mesh',seen[monster_id]['node_generation']==generations[monster_id])
                evolved=[dict(a,type='mon_zombie_brute') if a['kind']==2 else a for a in actors]
                rev=update('actors',evolved)
                changed=until(lambda data: int(data[1]['revision'])==rev and data[monster_id]['node_generation']!=generations[monster_id])
                check('archetype_change_replaces_mesh_without_orphan',changed[1]['scene_actors']=='2')
                trusted=rev
                update('bad-kind')
                frozen=until(lambda data: data[1]['ready']=='0')
                check('kind_alias_is_rejected_before_scene_mutation',int(frozen[1]['revision'])==trusted and frozen[monster_id]['type']=='monster')
                recovered=until(lambda data: data[1]['ready']=='1' and int(data[1]['revision'])>trusted)
                check('correlated_full_resync_restores_actor_roster',recovered[1]['scene_actors']=='2')
                old_connection=recovered[1]['connection_id']; old_session=recovered[1]['session_id']
                update('disconnect')
                disconnected=until(lambda data: data[1]['ready']=='0' and data[1]['visible_actors']=='0')
                check('transport_loss_hides_creatures',disconnected[1]['scene_actors']=='2')
                reconnected=until(lambda data: data[1]['ready']=='1' and data[1]['connection_id']!=old_connection)
                check('same_session_reconnect_does_not_duplicate_meshes',reconnected[1]['scene_actors']=='2' and reconnected[1]['session_id']==old_session)
                update('disconnect')
                fresh=until(lambda data: data[1]['ready']=='1' and data[1]['session_id']!=old_session)
                check('new_session_discards_old_scene_nodes',fresh[1]['scene_actors']=='2')
                rev=update('actors',[])
                removed=until(lambda data: int(data[1]['revision'])==rev and len(data)==1)
                check('despawn_removes_actual_irrlicht_nodes',removed[1]['scene_actors']=='0')
                subprocess.run(['import','-window',window,str(out/'removed.png')],check=True)
                return_actors=[dict(a) for a in evolved]
                rev=update('actors',return_actors)
                returned=until(lambda data: int(data[1]['revision'])==rev and data[1]['visible_actors']=='2')
                check('returning_persistent_ids_create_one_mesh_each',returned[1]['scene_actors']=='2')
                subprocess.run(['import','-window',window,str(out/'returned.png')],check=True)
            finally:
                stop.set(); listener.close()
                if proc.poll() is None:
                    proc.terminate()
                    try: proc.wait(timeout=15)
                    except subprocess.TimeoutExpired: proc.kill(); proc.wait()
                thread.join(timeout=3)
                if old_window: subprocess.run(['xdotool','windowactivate',old_window],capture_output=True)
    check('graphical_client_clean_exit',proc.returncode==0)
    check('controlled_peer_has_no_errors',not errors)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
