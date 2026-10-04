#!/usr/bin/env python3
"""Actual 3D client: arbitrary direction, fractional stop, pause and performance."""
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
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ('workspace', 'fixture', 'native-reader', 'artifacts'):
        parser.add_argument('--'+key, type=Path, required=True)
    args = parser.parse_args()
    ws, out = args.workspace.resolve(), args.artifacts.resolve()
    out.mkdir(parents=True, exist_ok=False)
    user = out/'user'
    shutil.copytree(args.fixture.resolve(), user)
    (user/'config/options.json').write_text(json.dumps([
        {'name':'SAFEMODE','value':'false'}, {'name':'AUTOSAFEMODE','value':'false'},
        {'name':'AUTOSAVE','value':'false'}]))
    camera, actors = out/'camera.csv', out/'actors.csv'
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    config = out/'client.conf'
    config.write_text(f'screen_w = 1280\nscreen_h = 800\nfullscreen = false\nfps_max = 60\nfps_max_unfocused = 60\n'
        f'vsync = false\nenable_clouds = false\nport = {port}\n'
        f'keymap_jump = KEY_SPACE\nkeymap_sneak = KEY_LSHIFT\n'
        f'cwm_trace_file = {camera}\ncwm_entity_trace_file = {actors}\n')
    env = dict(os.environ, CDDA_CONTINUOUS='1', CDDA_REALTIME='1', CDDA_USERDIR=str(user), CDDA_WORLD='audit_fixture',
        CDDA_CHARACTER='Audit Survivor', LUANTI_WORLD=str(out/'world'), LUANTI_CONFIG=str(config),
        LOG_DIR=str(out/'logs'), CDDA_BIN=str(ws/'cdda/build/src/cdda-server'), LUANTI_BIN=str(ws/'luanti/bin/luanti'))
    env.pop('CDDA_TERRAIN_DEMO', None)
    old_window = subprocess.run(['xdotool','getactivewindow'],capture_output=True,text=True).stdout.strip()
    checks = {}
    def check(name, ok):
        checks[name] = bool(ok)
        (out/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
        print(name, 'PASS' if ok else 'FAIL', flush=True)
        if not ok:
            raise AssertionError(name)
    def rows(path):
        if not path.exists():
            return []
        with path.open() as stream:
            return [r for r in csv.DictReader(stream) if None not in r.values()]
    def latest():
        data = rows(camera)
        return data[-1] if data else {}
    def roster():
        data = rows(actors)
        if not data:
            return {}
        stamp = data[-1]['time_ns']
        return {int(r['id']):r for r in data if r['time_ns']==stamp}
    def until(predicate, timeout=15):
        deadline = time.monotonic()+timeout
        while time.monotonic()<deadline and proc.poll() is None:
            row = latest()
            if row and predicate(row):
                return row
            time.sleep(.03)
        if window:
            subprocess.run(['import','-window',window,str(out/'timeout.png')],timeout=10)
        raise RuntimeError('Real-time GUI condition timed out; inspect traces and logs')
    def xdo(*argv):
        subprocess.run(['xdotool',*argv],check=True,capture_output=True,timeout=8)
    def tap(key):
        xdo('keydown','--window',window,key)
        time.sleep(.12)
        xdo('keyup','--window',window,key)
        time.sleep(.15)
    def target(row):
        return tuple(float(row['target_'+k]) for k in ('x','y','z'))
    def pose(data):
        return {i:tuple(float(r['current_'+k]) for k in ('x','y','z')) for i,r in data.items()}
    def native_time(row):
        return int(row['simulation_time'])
    window = None
    with (out/'launcher.log').open('w') as log:
        proc = subprocess.Popen([str(ws/'start.sh'),'--go','--name','realtime_gui_tester','--info'],
            env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        try:
            import math
            initial = until(lambda r:r['input_ready']=='1' and r['continuous_motion']=='1' and r['pause_reasons']=='0',85)
            initial_target=target(initial)
            descendants=[proc.pid]
            for pid in descendants:
                try:
                    descendants.extend(map(int,Path(f'/proc/{pid}/task/{pid}/children').read_text().split()))
                    if Path(f'/proc/{pid}/comm').read_text().strip()!='luanti':continue
                except (FileNotFoundError,ProcessLookupError):continue
                found=subprocess.run(['xdotool','search','--onlyvisible','--pid',str(pid)],capture_output=True,text=True)
                if found.stdout.strip():window=found.stdout.splitlines()[0]
            check('actual_continuous_start_window',bool(window))
            xdo('windowactivate','--sync',window); time.sleep(.8)
            check('actual_gui_default_global_4x',latest()['time_scale']=='4')
            start_time=native_time(latest()); time.sleep(.8)
            check('real_gui_idle_world_clock_advances_4x',2<=native_time(latest())-start_time<=4)
            before=target(latest())
            xdo('keydown','--window',window,'a'); time.sleep(.065); xdo('keyup','--window',window,'a')
            until(lambda r:r['intent_x']=='0' and r['intent_y']=='0'); time.sleep(.25)
            stopped=target(latest())
            check('real_short_tap_stops_inside_tile',.015<math.dist(stopped,before)<.5 and any(abs(v-round(v))>.01 for v in stopped))
            time.sleep(.4)
            check('real_release_has_no_queued_tile_step',target(latest())==stopped)
            before=stopped
            xdo('mousemove_relative','--sync','--','73','0'); time.sleep(.15)
            xdo('keydown','--window',window,'w'); time.sleep(.65); xdo('keyup','--window',window,'w')
            until(lambda r:r['intent_x']=='0' and r['intent_y']=='0'); time.sleep(.25)
            after=target(latest()); dx,dz=after[0]-before[0],after[2]-before[2]
            ratio=abs(dx/dz) if abs(dz)>1e-5 else 0
            check('real_camera_yaw_produces_arbitrary_confirmed_direction',abs(dx)>.03 and abs(dz)>.03 and abs(ratio-1)>.05)
            check('real_4x_continuous_pace_is_usable',1.1<math.dist(after,before)<3.5)
            subprocess.run(['import','-window',window,str(out/'continuous.png')],check=True,timeout=10)
            xdo('keydown','--window',window,'a'); time.sleep(.16)
            tap('F7'); until(lambda r:r['pause_reasons']=='1'); time.sleep(.1)
            paused=target(latest()); paused_time=native_time(latest()); cam=tuple(float(latest()['camera_'+k]) for k in ('x','y','z'))
            time.sleep(.6)
            check('actual_pause_freezes_confirmed_position_and_clock',target(latest())==paused and native_time(latest())==paused_time)
            check('actual_pause_freezes_camera_interpolation',tuple(float(latest()['camera_'+k]) for k in ('x','y','z'))==cam)
            tap('F7'); until(lambda r:r['pause_reasons']=='0'); time.sleep(.35)
            check('held_key_does_not_resume_after_pause',target(latest())==paused)
            xdo('keyup','--window',window,'a'); time.sleep(.2)
            xdo('keydown','--window',window,'a'); time.sleep(.16); xdo('keyup','--window',window,'a'); time.sleep(.2)
            check('fresh_press_resumes_continuous_motion',math.dist(target(latest()),paused)>.05)
            tap('Escape'); until(lambda r:r['pause_reasons']=='2'); time.sleep(.1)
            menu=target(latest()); menu_time=native_time(latest()); time.sleep(.4)
            check('actual_menu_freezes_fractional_authority',target(latest())==menu and native_time(latest())==menu_time)
            tap('Escape'); until(lambda r:r['pause_reasons']=='0')
            tap('F7'); until(lambda r:r['pause_reasons']=='1'); time.sleep(.15)
            final=latest(); saved_target=target(final); saved_time=native_time(final)
            subprocess.run(['import','-window',window,str(out/'paused.png')],check=True,timeout=10)
        finally:
            if window:
                for key in ('w','a','s','d','F7','Escape'):subprocess.run(['xdotool','keyup','--window',window,key],capture_output=True)
            os.killpg(proc.pid,signal.SIGTERM)
            try:proc.wait(timeout=50)
            except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
            if old_window:subprocess.run(['xdotool','windowactivate',old_window],capture_output=True)
    check('actual_client_and_server_shutdown_clean',proc.returncode in (0,143,-15))
    data=rows(camera)
    stamps=[int(r['time_ns']) for r in data]
    intervals=[(b-a)/1e9 for a,b in zip(stamps,stamps[1:]) if 0<(b-a)/1e9<.2]
    intervals.sort(); median=intervals[len(intervals)//2]
    check('continuous_actual_frame_rate_stays_interactive',1/median>35)
    (out/'performance.json').write_text(json.dumps(dict(frames=len(data),median_fps=1/median,
        max_ipc_latency_ms=None),indent=2)+'\n')
    with (out/'canonical.log').open('w') as log:
        res=subprocess.run([str(args.native_reader.resolve()),'--userdir',str(user),'--datadir',str(ws/'cdda/data'),
            '--output',str(out/'canonical.json')],stdout=log,stderr=subprocess.STDOUT,timeout=180)
    check('actual_3d_save_is_native_readable',res.returncode==0)
    native=json.loads((out/'canonical.json').read_text()); state=native['player']['values']['cwm_motion_v1'].split()
    pos=[int(state[0])+float(state[3]),int(state[1])+float(state[4]),int(state[2])]
    # Scene origin is fixed at initial projection; trace targets are already
    # absolute in that scene. Recover native coordinates from initial anchor.
    native_scene=[pos[0]-60+initial_target[0],pos[2]*3,-(pos[1]-60)+initial_target[2]]
    check('actual_visual_target_matches_saved_native_offset',math.dist(native_scene,saved_target)<1e-3 and native['time']==saved_time)
    print('continuous actual GUI checks:',len(checks),'PASS',flush=True)

if __name__=='__main__':main()
