#!/usr/bin/env python3
"""Actual start.sh/CDDA/Luanti: idle AI, paced input, pause, speed, menu and save.

All configuration, worlds, diagnostics and screenshots are private to this run.
Threat/recovery protocol boundaries are independently covered by the native test.
"""
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
    env = dict(os.environ, CDDA_REALTIME='1', CDDA_USERDIR=str(user), CDDA_WORLD='audit_fixture',
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
            initial = until(lambda r:r['input_ready']=='1' and r['realtime']=='1' and r['pause_reasons']=='0',85)
            first = roster()
            initial_target = target(initial)
            descendants = [proc.pid]
            for pid in descendants:
                try:
                    descendants.extend(map(int,Path(f'/proc/{pid}/task/{pid}/children').read_text().split()))
                    if Path(f'/proc/{pid}/comm').read_text().strip()!='luanti':
                        continue
                except (FileNotFoundError,ProcessLookupError):
                    continue
                found = subprocess.run(['xdotool','search','--onlyvisible','--pid',str(pid)],capture_output=True,text=True)
                if found.stdout.strip():
                    window=found.stdout.splitlines()[0]
            check('actual_start_window', bool(window))
            xdo('windowactivate','--sync',window)
            time.sleep(3.2)
            idle = latest()
            check('idle_real_gui_clock_advances_1_to_1',2<=native_time(idle)-native_time(initial)<=5)
            check('idle_player_stays_authoritative',target(idle)==initial_target)
            all_actors = rows(actors)
            check('actual_native_ai_changes_real_scene_target', any(
                int(r['id'])!=1 and int(r['id']) in first and
                any(r['target_'+k]!=first[int(r['id'])]['target_'+k] for k in ('x','y','z')) for r in all_actors))
            # Walk backwards along the safe road; pause while the key is held.
            xdo('keydown','--window',window,'s')
            until(lambda r:target(r)!=initial_target)
            tap('F7')
            paused = until(lambda r:int(r['pause_reasons'])&1)
            time.sleep(.2)
            frozen = latest()
            frozen_pose = pose(roster())
            time.sleep(1.2)
            check('manual_pause_freezes_calendar_camera_and_actor_interpolation',
                native_time(latest())==native_time(frozen) and target(latest())==target(frozen) and pose(roster())==frozen_pose and
                all(abs(float(latest()['camera_'+k])-float(frozen['camera_'+k]))<.001 for k in ('x','y','z')))
            tap('F8')
            until(lambda r:float(r['time_scale'])==2 and int(r['pause_reasons'])&1)
            tap('F7')
            resumed = until(lambda r:r['pause_reasons']=='0')
            time.sleep(1.1)
            check('resume_requires_release_of_previously_held_key',target(latest())==target(frozen))
            xdo('keyup','--window',window,'s')
            time.sleep(.15)
            xdo('keydown','--window',window,'s')
            start = latest()
            time.sleep(2.2)
            xdo('keyup','--window',window,'s')
            time.sleep(.15)
            stop = latest()
            distance = sum(abs(a-b) for a,b in zip(target(start),target(stop)))
            check('held_input_at_2x_has_bounded_native_pacing', 2<=distance<=6)
            times = []
            old = target(start)
            for r in rows(camera):
                if int(r['time_ns'])<int(start['time_ns']) or int(r['time_ns'])>int(stop['time_ns']):
                    continue
                if target(r)!=old:
                    times.append(int(r['time_ns'])/1e9)
                    old=target(r)
            check('held_steps_do_not_arrive_as_catchup_burst',len(times)>=2 and all(b-a>.12 for a,b in zip(times,times[1:])))
            time.sleep(1.1)
            check('release_does_not_queue_extra_steps',target(latest())==target(stop))
            t = native_time(latest())
            time.sleep(2.1)
            check('speed_control_scales_same_native_clock',3<=native_time(latest())-t<=5)
            tap('Escape')
            menu = until(lambda r:int(r['pause_reasons'])&2)
            time.sleep(1.2)
            check('actual_escape_menu_pauses_native_clock',native_time(latest())==native_time(menu))
            tap('Escape')
            until(lambda r:r['pause_reasons']=='0')
            tap('F7')
            paused=until(lambda r:int(r['pause_reasons'])&1)
            subprocess.run(['import','-window',window,str(out/'paused.png')],check=True,timeout=10)
            saved_time = native_time(paused)
            saved_target = target(paused)
            samples = rows(actors)
            check('actual_mesh_visibility_respects_native_perception',all(r['node_visible']=='0' or (r['perceived']=='1' and r['ready']=='1') for r in samples))
            check('real_scene_has_no_unowned_actor_nodes',all(int(r['scene_actors'])<=int(latest()['entity_cache'])-1 for r in roster().values()))
        finally:
            if window:
                for key in ('s','w','F7','F8','Escape'):
                    subprocess.run(['xdotool','keyup','--window',window,key],capture_output=True)
            if proc.poll() is None:
                os.killpg(proc.pid,signal.SIGTERM)
                try:
                    proc.wait(timeout=40)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid,signal.SIGKILL); proc.wait()
            if old_window:
                subprocess.run(['xdotool','windowactivate',old_window],capture_output=True)
    check('supervisor_shutdown',proc.returncode==143)
    with (out/'canonical.log').open('w') as log:
        result = subprocess.run([str(args.native_reader.resolve()),'--userdir',str(user),
            '--datadir',str(ws/'cdda/data'),'--output',str(out/'canonical.json')],
            stdout=log,stderr=subprocess.STDOUT,timeout=180)
    check('actual_gui_realtime_save_is_pristine_readable', result.returncode==0)
    native=json.loads((out/'canonical.json').read_text())
    check('actual_gui_save_keeps_native_clock',native['time']==saved_time)
    # Camera coordinates are presentation; compare the native saved absolute tile
    # against the recorded bridge origin/axis transform, without trusting it as a save.
    final=latest()
    check('actual_gui_save_keeps_authoritative_position',
        native['player_abs']==[int(saved_target[0]+float(final['scene_origin_x'])),
            int(-saved_target[2]+float(final['scene_origin_y'])),int(saved_target[1]/3)])
    return 0


if __name__=='__main__':
    raise SystemExit(main())
