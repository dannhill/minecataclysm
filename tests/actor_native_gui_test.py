#!/usr/bin/env python3
"""Real start.sh, native actor perception/multi-Z and canonical reload in isolated saves."""
import argparse
import csv
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import time


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for key in ('workspace','fixture','native-reader','artifacts'):
        parser.add_argument('--'+key,type=Path,required=True)
    args=parser.parse_args()
    ws,out=args.workspace.resolve(),args.artifacts.resolve()
    out.mkdir(parents=True,exist_ok=False)
    user=out/'user'; shutil.copytree(args.fixture.resolve(),user)
    (user/'config/options.json').write_text(json.dumps([
        {'name':'SAFEMODE','value':'false'},{'name':'AUTOSAFEMODE','value':'false'},
        {'name':'AUTOSAVE','value':'false'}]))
    checks={}; expected=set()
    old_window=subprocess.run(['xdotool','getactivewindow'],capture_output=True,text=True).stdout.strip()
    def check(name,ok):
        checks[name]=bool(ok); (out/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
        print(name,'PASS' if ok else 'FAIL',flush=True)
        if not ok: raise AssertionError(name)
    def read(path):
        if not path.exists(): return []
        with path.open() as stream:
            return [row for row in csv.DictReader(stream) if None not in row.values()]
    for run in ('initial','reload'):
        folder=out/run; folder.mkdir()
        camera,actors=folder/'camera.csv',folder/'actors.csv'
        with socket.socket() as temporary:
            temporary.bind(('127.0.0.1',0)); port=temporary.getsockname()[1]
        config=folder/'client.conf'
        config.write_text(f'screen_w = 1024\nscreen_h = 768\nfullscreen = false\nfps_max = 60\nfps_max_unfocused = 60\n'
            f'keymap_jump = KEY_SPACE\nkeymap_sneak = KEY_LSHIFT\nvsync = false\nenable_clouds = false\n'
            f'port = {port}\ncwm_trace_file = {camera}\ncwm_entity_trace_file = {actors}\n')
        env=dict(os.environ,CDDA_USERDIR=str(user),CDDA_WORLD='audit_fixture',CDDA_CHARACTER='Audit Survivor',
            LUANTI_WORLD=str(folder/'world'),LUANTI_CONFIG=str(config),LOG_DIR=str(folder/'logs'),
            CDDA_BIN=str(ws/'cdda/build/src/cdda-server'),LUANTI_BIN=str(ws/'luanti/bin/luanti'))
        env.pop('CDDA_TERRAIN_DEMO',None)
        def latest():
            data=read(actors)
            if not data: return {}
            stamp=data[-1]['time_ns']
            return {int(row['id']):row for row in data if row['time_ns']==stamp}
        def until(predicate,timeout=15):
            deadline=time.monotonic()+timeout
            while time.monotonic()<deadline and proc.poll() is None:
                data=latest()
                if data and predicate(data): return data
                time.sleep(.03)
            raise RuntimeError('Native GUI actor condition timed out; inspect traces and logs')
        def xdo(*argv):
            subprocess.run(['xdotool',*argv],check=True,capture_output=True,timeout=8)
        def tap(key,sneak=False):
            if sneak: xdo('keydown','Shift_L'); time.sleep(.1)
            xdo('keydown','--window',window,key); time.sleep(.12); xdo('keyup','--window',window,key)
            if sneak: xdo('keyup','Shift_L')
            time.sleep(.3)
        def arrived(x,y,z):
            return until(lambda data: [float(data[1]['target_'+k]) for k in ('x','y','z')]==[x,y,z])
        with (folder/'launcher.log').open('w') as log:
            proc=subprocess.Popen([str(ws/'start.sh'),'--go','--name','actor_native_tester','--info'],
                env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            try:
                state=until(lambda data: len(data)>=4 and data[1]['ready']=='1',85)
                if run=='initial':
                    player=state[1]
                    px,py,pz=[float(player['target_'+k]) for k in ('x','y','z')]
                    # Native mapgen can contain legitimate static animal spawns
                    # even at density zero. Select our fixed fixture actors by
                    # kind and relative position, rather than forbidding others.
                    wanted={('monster',px+3,py,pz+2),('monster',px+5,py,pz+2),('npc',px,py,pz-4)}
                    expected={ident for ident,row in state.items() if
                        (row['type'],*[float(row['target_'+k]) for k in ('x','y','z')]) in wanted}
                ids=set(state)&expected
                check(run+'_actual_native_actor_roster',ids==expected and len(ids)==3)
                check(run+'_wire_ids_use_persistent_namespaces',sum(i>>62==1 for i in ids)==2 and sum(i>>63==1 for i in ids)==1)
                npc_id=next(i for i in ids if i>>63==1)
                descendants=[proc.pid]; window=None
                for pid in descendants:
                    try:
                        descendants.extend(map(int,Path(f'/proc/{pid}/task/{pid}/children').read_text().split()))
                        if Path(f'/proc/{pid}/comm').read_text().strip()!='luanti': continue
                    except (FileNotFoundError,ProcessLookupError): continue
                    found=subprocess.run(['xdotool','search','--onlyvisible','--pid',str(pid)],capture_output=True,text=True)
                    if found.stdout.strip(): window=found.stdout.splitlines()[0]
                check(run+'_actual_start_window',bool(window))
                xdo('windowactivate','--sync',window); time.sleep(.8)
                if run=='initial':
                    start=state[1]
                    x,y,z=[float(start['target_'+k]) for k in ('x','y','z')]
                    for offset in (1,2,3): tap('s'); arrived(x,y,z-offset)
                    npc_seen=until(lambda data: npc_id in data and data[npc_id]['perceived']=='1' and data[npc_id]['node_visible']=='1')
                    check('native_perceived_npc_has_real_mesh',int(npc_seen[npc_id]['node_generation'])>0)
                    subprocess.run(['import','-window',window,str(folder/'npc.png')],check=True)
                    for offset in (2,1,0): tap('w'); arrived(x,y,z-offset)
                    tap('w'); arrived(x,y,z+1)
                    tap('space'); arrived(x,y+3,z+1)
                    tap('space',True); arrived(x,y,z+1)
                    tap('s'); returned=arrived(x,y,z)
                    check('native_floor_roundtrip_retains_actor_ids',expected<=set(returned))
                else:
                    check('native_gui_reload_has_no_orphan_meshes',int(state[1]['scene_actors'])<=len(state)-1)
                samples=read(actors)
                check(run+'_mesh_visibility_respects_native_perception',all(
                    row['node_visible']=='0' or (row['perceived']=='1' and row['ready']=='1') for row in samples))
            finally:
                if proc.poll() is None:
                    os.killpg(proc.pid,signal.SIGTERM)
                    try: proc.wait(timeout=40)
                    except subprocess.TimeoutExpired: os.killpg(proc.pid,signal.SIGKILL); proc.wait()
                if old_window: subprocess.run(['xdotool','windowactivate',old_window],capture_output=True)
        check(run+'_supervisor_shutdown',proc.returncode==143)
    command=[str(args.native_reader.resolve()),'--userdir',str(user),'--datadir',str(ws/'cdda/data'),
        '--output',str(out/'canonical.json')]
    with (out/'canonical.log').open('w') as log:
        result=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=180)
    check('actual_gui_save_is_pristine_readable',result.returncode==0)
    native=json.loads((out/'canonical.json').read_text())
    ids={(1<<62)|int(a['values']['cwm_monster_id']) for a in native['monsters'] if 'Lifecycle' in a['unique_name']}
    ids|={(1<<63)|a['id'] for a in native['npcs'] if a['name']=='Lifecycle NPC'}
    check('actual_gui_save_preserves_all_three_native_actor_ids',ids==expected)
    return 0


if __name__=='__main__':
    raise SystemExit(main())
