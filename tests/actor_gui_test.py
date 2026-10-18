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
    parser.add_argument('--feedback',action='store_true')
    args = parser.parse_args()
    ws, out = args.workspace.resolve(), args.artifacts.resolve()
    out.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(ws / 'protocol/python'))
    import flatbuffers
    from session_wire import AuthorityWire
    from CDDA.CWM import CwmMessage, Payload, HelloResponse, ResyncRequest
    from CDDA.CWM import WorldSnapshot as World, ChunkSnapshot as Chunk, CwmBlock as Block
    from CDDA.CWM import EntityState as Entity, Vec3f, Coord3i
    from CDDA.CWM import SimulationState, PresentationEvent as Cue, GroundItemState as Item, RangedWeaponState as Gun
    monster_id, npc_id = (1 << 62) | 2, (1 << 63) | 3
    actors = [{'id':monster_id, 'kind':2, 'type':'mon_zombie', 'pos':[8,8,0], 'seen':True},
              {'id':npc_id, 'kind':1, 'type':'npc', 'pos':[6,8,0], 'seen':True}]
    commands, receipts = queue.Queue(), queue.Queue()
    stop, errors, checks = threading.Event(), [], {}
    trace, camera = out / 'actors.csv', out / 'camera.csv'
    origin = [0,0]
    pending_cues=[]; environment=[False,0]; wield=[False]; cue_serial=[0]
    clock = [0,1.0] # Authoritative pause reasons / global time scale.
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
            if actor['id']==1: Entity.EntityStateAddStateFlags(b,environment[1])
            Entity.EntityStateAddPos(b,Vec3f.CreateVec3f(b,actor['pos'][0]-origin[0],actor['pos'][1]-origin[1],actor['pos'][2]))
            states.append(Entity.EntityStateEnd(b))
        World.WorldSnapshotStartEntitiesVector(b,len(states))
        for state in reversed(states): b.PrependUOffsetTRelative(state)
        roster=b.EndVector(); empty=wire.empty_vectors(b)
        SimulationState.SimulationStateStart(b)
        SimulationState.SimulationStateAddRealtime(b,True)
        SimulationState.SimulationStateAddPauseReasons(b,clock[0])
        SimulationState.SimulationStateAddTimeScale(b,clock[1])
        state_clock=SimulationState.SimulationStateEnd(b)
        cue_offsets=[]
        if not full:
            for kind,actor,description,category,volume in pending_cues:
                cue_serial[0]+=1
                description=b.CreateString(description); category=b.CreateString(category)
                Cue.PresentationEventStart(b); Cue.PresentationEventAddId(b,cue_serial[0])
                Cue.PresentationEventAddKind(b,kind); Cue.PresentationEventAddActor(b,actor)
                Cue.PresentationEventAddDescription(b,description); Cue.PresentationEventAddSoundCategory(b,category)
                Cue.PresentationEventAddHeardVolume(b,volume); cue_offsets.append(Cue.PresentationEventEnd(b))
        pending_cues.clear()
        World.WorldSnapshotStartPresentationEventsVector(b,len(cue_offsets))
        for cue in reversed(cue_offsets): b.PrependUOffsetTRelative(cue)
        cues=b.EndVector(); owned=0; gun=0
        if wield[0]:
            item_type=b.CreateString('glock_19'); name=b.CreateString('Glock 19'); category=b.CreateString('guns')
            Item.GroundItemStateStart(b); Item.GroundItemStateAddTypeId(b,item_type)
            Item.GroundItemStateAddName(b,name); Item.GroundItemStateAddCategory(b,category)
            Item.GroundItemStateAddWielded(b,True); item=Item.GroundItemStateEnd(b)
            World.WorldSnapshotStartOwnedItemsVector(b,1);b.PrependUOffsetTRelative(item);owned=b.EndVector()
            reason=b.CreateString(''); Gun.RangedWeaponStateStart(b);Gun.RangedWeaponStateAddToken(b,1)
            Gun.RangedWeaponStateAddName(b,name);Gun.RangedWeaponStateAddReason(b,reason)
            Gun.RangedWeaponStateAddAmmo(b,10);Gun.RangedWeaponStateAddRange(b,10);gun=Gun.RangedWeaponStateEnd(b)
        World.WorldSnapshotStart(b); wire.world_fields(b,full,empty)
        World.WorldSnapshotAddPresentationEvents(b,cues);World.WorldSnapshotAddLowLight(b,environment[0])
        if owned: World.WorldSnapshotAddOwnedItems(b,owned);World.WorldSnapshotAddRangedWeapon(b,gun)
        World.WorldSnapshotAddClock(b,state_clock)
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
                            if action=='clock': clock[:]=value
                            if action=='cues': pending_cues.extend(value)
                            if action=='environment': environment[:]=value
                            if action=='wield': wield[0]=value
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
                focus='windowfocus' if os.environ.get('CWM_GUI_NO_WM')=='1' else 'windowactivate'
                subprocess.run(['xdotool',focus,'--sync',window],check=True,capture_output=True)
                if args.feedback:
                    def camera_latest():
                        values=rows(camera)
                        return values[-1] if values else {}
                    def screen(name):
                        subprocess.run(['import','-window',window,str(out/name)],check=True)
                    check('diagnostics_default_off',camera_latest()['diagnostics']=='0')
                    subprocess.run(['xdotool','key','--window',window,'F3'],check=True);time.sleep(.2)
                    check('rebindable_debug_action_enables_diagnostics',camera_latest()['diagnostics']=='1')
                    screen('diagnostics-on.png')
                    subprocess.run(['xdotool','key','--window',window,'F3'],check=True);time.sleep(.2)
                    check('debug_action_disables_diagnostics_again',camera_latest()['diagnostics']=='0')
                    rev=update('cues',[(0,monster_id,'','',0)])
                    strike=until(lambda d:int(d[1]['revision'])==rev and float(d[monster_id]['attack_seconds'])>0)
                    check('native_attack_cue_selects_actual_punch_frames',50<=float(strike[monster_id]['model_frame'])<=59)
                    screen('attack.png')
                    # An event already in progress must freeze with simulation pause.
                    rev=update('clock',[2,1.0]);paused=until(lambda d:int(d[1]['revision'])==rev)
                    time.sleep(.35);frozen=until(lambda d:int(d[1]['revision'])==rev)
                    check('pause_freezes_native_attack_pose',paused[monster_id]['model_frame']==frozen[monster_id]['model_frame'])
                    update('clock',[0,1.0]);time.sleep(.6)
                    rev=update('cues',[(1,monster_id,'','',0),(1,1,'','',0)])
                    hurt=until(lambda d:int(d[1]['revision'])==rev and float(d[monster_id]['hurt_seconds'])>0)
                    check('native_damage_cue_tints_actual_skin', 'colorize' in hurt[monster_id]['material1'])
                    check('player_injury_has_explicit_native_cue',float(hurt[1]['hurt_seconds'])>0)
                    screen('hurt.png');time.sleep(.45)
                    cleared=until(lambda d:float(d[monster_id]['hurt_seconds'])==0)
                    check('injury_tint_clears_without_changing_target',cleared[monster_id]['material1'].endswith('zombie.png'))
                    rev=update('cues',[(4,0,'East: bang','gunfire',50)])
                    until(lambda d:int(d[1]['revision'])==rev);time.sleep(.15)
                    check('heard_sound_reaches_audio_manager',int(camera_latest()['sounds_dispatched'])>=1)
                    screen('sound-caption.png')
                    rev=update('environment',[True,0]);until(lambda d:int(d[1]['revision'])==rev);time.sleep(.1)
                    check('native_low_light_reaches_presentation',camera_latest()['low_light']=='1');screen('darkness.png')
                    # UNDERWATER from the shared semantic flag, not a Luanti water node.
                    from pathlib import Path as _Path
                    import re as _re
                    semantics=(ws/'protocol/include/cwm/tile_semantics.hpp').read_text()
                    shift=int(_re.search(r'UNDERWATER\s*=\s*1u?\s*<<\s*(\d+)',semantics)[1])
                    rev=update('environment',[False,1<<shift]);until(lambda d:int(d[1]['revision'])==rev);time.sleep(.1)
                    check('native_underwater_state_reaches_presentation',camera_latest()['underwater']=='1');screen('underwater.png')
                    update('environment',[False,0]);rev=update('wield',True)
                    until(lambda d:int(d[1]['revision'])==rev);time.sleep(.2)
                    check('actual_native_hand_resolves_first_person_texture',bool(camera_latest()['wield_texture']))
                    screen('held-firearm.png')
                    rev=update('cues',[(3,1,'','',0)])
                    until(lambda d:int(d[1]['revision'])==rev and float(d[1]['attack_seconds'])>.35)
                    check('native_shot_drives_visual_kick',float(camera_latest()['shot_kick'])>0)
                    update('wield',False);time.sleep(.6)
                    original=[dict(a) for a in actors]
                    for family,kind,skin,height in [('canine','mon_wolf','mobs_mc_wolf.png',8.4),('spider','mon_spider_web','mobs_mc_spider.png',7),('bird','mon_chicken','mobs_mc_chicken.png',5)]:
                        rev=update('actors',[dict(original[0],type=kind),original[1]])
                        family_scene=until(lambda d:int(d[1]['revision'])==rev and d[monster_id]['material0'].endswith(skin))
                        check(family+'_uses_real_pinned_mesh_and_skin',int(family_scene[monster_id]['node_materials'])>0 and abs(float(family_scene[monster_id]['model_height'])-height)<.1)
                        screen(family+'.png')
                        moved=[dict(a,pos=[a['pos'][0]+1,a['pos'][1],a['pos'][2]]) for a in actors]
                        rev=update('actors',moved)
                        family_walk=until(lambda d:int(d[1]['revision'])==rev and float(d[monster_id]['model_frame'])>0)
                        check(family+'_cycles_on_authoritative_motion',float(family_walk[monster_id]['model_frame'])>0)
                    update('actors',original);time.sleep(.5)
                    initial=until(lambda d:d[monster_id]['material1'].endswith('zombie.png'))
                generations={i:initial[i]['node_generation'] for i in (monster_id,npc_id)}
                check('real_zombie_and_npc_meshes_created', initial[1]['scene_actors']=='2')
                check('zombie_skin_does_not_cover_armour_geometry',initial[monster_id]['material0'].endswith('blank.png') and initial[monster_id]['material1'].endswith('zombie.png'))
                # This pinned B3D exposes two rendered materials; Mineclonia's
                # Lua player definition also declares an unused third texture.
                check('npc_skin_and_empty_overlays_use_separate_materials',int(initial[npc_id]['node_materials'])==2 and initial[npc_id]['material0'].endswith('mcl_skins_character_1.png') and initial[npc_id]['material1'].endswith('blank.png'))
                check('integrated_avatar_is_voxel_mesh',int(initial[1]['node_materials'])==2 and float(initial[1]['model_frame'])>=0 and initial[1]['material0'].endswith('mcl_skins_character_1.png') and initial[1]['material1'].endswith('blank.png'))
                check('avatar_and_npc_use_humanoid_world_scale',all(14<float(initial[i]['model_height'])<22 for i in (1,npc_id)))
                idle_frame=float(initial[monster_id]['model_frame']);time.sleep(.65)
                idle=until(lambda data:data[1]['ready']=='1')
                check('idle_cycle_changes_actual_mesh_frame',abs(float(idle[monster_id]['model_frame'])-idle_frame)>.2)
                rev=update('clock',[2,1.0]);paused=until(lambda data:int(data[1]['revision'])==rev)
                frozen_frames={i:row['model_frame'] for i,row in paused.items()}
                time.sleep(.7)
                frozen=until(lambda data:int(data[1]['revision'])==rev)
                check('pause_freezes_avatar_and_creature_frames',all(frozen[i]['model_frame']==frozen_frames[i] for i in frozen_frames))
                rev=update('clock',[0,2.0]);fast=until(lambda data:int(data[1]['revision'])==rev)
                time.sleep(.7);later=until(lambda data:int(data[1]['revision'])==rev)
                seconds=(int(later[monster_id]['time_ns'])-int(fast[monster_id]['time_ns']))/1e9
                frames=(float(later[monster_id]['model_frame'])-float(fast[monster_id]['model_frame']))%10
                check('idle_cycle_obeys_authoritative_time_scale',seconds>.4 and abs(frames/seconds-4)<.8)
                for view in ('avatar-back.png','avatar-front.png'):
                    subprocess.run(['xdotool','key','--window',window,'c'],check=True)
                    time.sleep(.3);subprocess.run(['import','-window',window,str(out/view)],check=True)
                subprocess.run(['xdotool','key','--window',window,'c'],check=True);time.sleep(.3)
                subprocess.run(['import','-window',window,str(out/'initial.png')],check=True)
                moved=[dict(a,pos=[a['pos'][0]+1,a['pos'][1],a['pos'][2]]) for a in actors]
                rev=update('actors',moved)
                settled=until(lambda data: int(data[1]['revision'])==rev and coords(data[monster_id],'current')==coords(data[monster_id],'target'))
                check('motion_preserves_owned_nodes', all(settled[i]['node_generation']==generations[i] for i in generations))
                movement=[r for r in rows(trace) if int(r['id'])==monster_id and int(r['revision'])==rev]
                check('perceived_motion_interpolates_confirmed_positions', any(coords(r,'current')!=coords(r,'target') for r in movement))
                check('confirmed_motion_uses_walk_cycle',any(0<=float(r['model_frame'])<40 for r in movement))
                check('walking_faces_confirmed_motion',abs(float(settled[monster_id]['model_yaw'])-90)<.1)
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
