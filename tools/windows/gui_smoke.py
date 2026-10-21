#!/usr/bin/env python3
"""Exercise the shipped native supervisor and actual Windows renderer under Wine.

Invoke through wine_run.py, using a private prefix/display and fresh artifact dir.
"""
import argparse,csv,json,math,os,subprocess,time
from pathlib import Path

def windows(path):return 'Z:'+str(path.resolve()).replace('/','\\')

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--payload',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    payload=args.payload.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    user=out/'Player saves 試験';user.mkdir();trace=out/'camera.csv';checks={};window=None;proc=None
    def check(name,ok):
        checks[name]=bool(ok);(out/'checks.json').write_text(json.dumps(checks,indent=2)+'\n');print(name,'PASS' if ok else 'FAIL',flush=True)
        if not ok:raise AssertionError(name)
    def shot(name):subprocess.run(['import','-window',window if window else 'root',str(out/(name+'.png'))],check=True,timeout=20)
    def latest():
        if not trace.exists():return {}
        with trace.open() as stream:rows=[r for r in csv.DictReader(stream) if None not in r.values()]
        return rows[-1] if rows else {}
    def wait(predicate,timeout=20):
        end=time.monotonic()+timeout
        while time.monotonic()<end:
            r=latest()
            if r and predicate(r):return r
            if proc.poll() is not None:break
            time.sleep(.1)
        shot('timeout');raise RuntimeError('Windows game condition timed out; inspect logs/trace')
    def xdo(*args):return subprocess.run(['xdotool',*args],check=True,capture_output=True,text=True,timeout=10).stdout.strip()
    def tap(key):xdo('key','--clearmodifiers',key);time.sleep(.2)
    def position(row):return tuple(float(row['target_'+k]) for k in ('x','y','z'))
    def focus():xdo('windowfocus','--sync',window)
    def launch():
        nonlocal proc,window
        trace.unlink(missing_ok=True)
        with (user/'client.conf').open('a') as config:config.write('\nscreen_w = 1280\nscreen_h = 800\nfullscreen = false\nvsync = false\nfps_max = 30\nfps_max_unfocused = 30\ncwm_trace_file = '+windows(trace)+'\n')
        proc=subprocess.Popen(['wine',str(payload/'Minecataclysm.exe'),'--userdir',windows(user)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        row=wait(lambda r:r['input_ready']=='1' and int(r['revision'])>0,330)
        found=xdo('search','--onlyvisible','--name','Luanti|Minetest')
        window=found.splitlines()[-1];focus();return row
    def quit_game():
        # Standard Windows close request, delivered through the X11/Wine window.
        focus();tap('alt+F4');proc.wait(timeout=90)
        check('supervisor_clean_exit_'+str(len(checks)),proc.returncode==0)
        logs=sorted((user/'logs').glob('*/cdda.log'),key=lambda p:p.stat().st_mtime)
        check('native_final_save_'+str(len(checks)),'Final save: SUCCESS' in logs[-1].read_text(errors='replace'))
    try:
        first=launch();check('shipped_renderer_named_pipe_authoritative_world',first['ipc_connected']=='1' and first['continuous_motion']=='1' and first['time_scale']=='4')
        check('unicode_and_space_paths',bool(list((user/'cdda/save').glob('*/worldoptions.json'))))
        wait(lambda r:r['pause_reasons']=='0');time.sleep(1)
        before=position(latest())
        for key in ('w','d'):
            xdo('keydown',key);time.sleep(.25);xdo('keyup',key);time.sleep(.2)
        wait(lambda r:r['intent_x']=='0' and r['intent_y']=='0')
        check('windows_keys_produce_confirmed_continuous_motion',math.dist(position(latest()),before)>.015)
        shot('world')
        tap('i');wait(lambda r:r['equipment_form']=='1');time.sleep(.3);paused=latest();time.sleep(.6)
        check('inventory_freezes_native_time',latest()['simulation_time']==paused['simulation_time']);shot('inventory')
        tap('Escape');wait(lambda r:r['equipment_form']=='0');tap('h');wait(lambda r:r['body_form']=='1');shot('body');tap('Escape');wait(lambda r:r['body_form']=='0')
        tap('k');wait(lambda r:r['crafting_form']=='1');shot('crafting');tap('Escape');wait(lambda r:r['crafting_form']=='0')
        tap('Escape');wait(lambda r:r['pause_reasons']=='2');shot('language-before');paused=latest()['simulation_time']
        xdo('mousemove','--window',window,'875','365');xdo('click','1');time.sleep(1)
        check('live_italian_while_paused','cwm_language = it' in (user/'client.conf').read_text() and latest()['simulation_time']==paused and latest()['pause_reasons']=='2');shot('language-italian')
        tap('Escape');wait(lambda r:r['pause_reasons']=='0');tap('F7');wait(lambda r:r['pause_reasons']=='1');saved=latest();shot('saved')
        (out/'expected-pose.json').write_text(json.dumps(dict(position=position(saved),time=saved['simulation_time']))+'\n')
        quit_game();check('language_persisted_by_supervisor','cwm_language = it' in (user/'presentation-language.conf').read_text())
        restored=launch();tap('F7') if latest()['pause_reasons']=='0' else None;wait(lambda r:r['pause_reasons']!='0')
        check('canonical_position_restored',math.dist(position(saved),position(restored))<.001)
        check('native_items_and_status_restored',restored['owned_items']==saved['owned_items'] and restored['status_head']==saved['status_head']);shot('restored');quit_game()
    finally:
        if proc and proc.poll() is None:
            shot('failure');proc.terminate()
            try:proc.wait(timeout=5)
            except subprocess.TimeoutExpired:proc.kill();proc.wait()
    return 0
if __name__=='__main__':raise SystemExit(main())
