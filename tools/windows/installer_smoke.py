#!/usr/bin/env python3
"""Private Wine check: install, auto-launch, shortcut, save retention, uninstall.

Requires an isolated prefix with no existing Minecataclysm user/install data.
"""
import argparse,csv,hashlib,json,os,subprocess,time
from pathlib import Path
from gui_smoke import windows

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--installer',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    checks={};trace=out/'camera.csv';window=None
    def check(name,ok):
        checks[name]=bool(ok);(out/'checks.json').write_text(json.dumps(checks,indent=2)+'\n');print(name,'PASS' if ok else 'FAIL',flush=True)
        if not ok:raise AssertionError(name)
    def wine(*args,timeout=60):return subprocess.run(['wine',*map(str,args)],text=True,capture_output=True,timeout=timeout)
    def winvar(name):return wine('cmd','/c','echo %'+name+'%').stdout.strip()
    def host(path):return Path(subprocess.check_output(['winepath','-u',path],text=True).strip())
    local=host(winvar('LOCALAPPDATA'));profile=host(winvar('USERPROFILE'));user=local/'Minecataclysm';install=local/'Programs/Minecataclysm';shortcut=profile/'Desktop/Minecataclysm.lnk'
    prefix=Path(os.environ['WINEPREFIX']).resolve()
    check('all_installer_paths_are_private',all(p.resolve().is_relative_to(prefix) for p in (user,install,shortcut)))
    check('clean_private_prefix_no_existing_game',not user.exists() and not install.exists())
    user.mkdir();(user/'client.conf').write_text('screen_w = 1280\nscreen_h = 800\nfullscreen = false\nfps_max = 30\nfps_max_unfocused = 30\ncwm_trace_file = '+windows(trace)+'\n')
    def latest():
        if not trace.exists():return {}
        with trace.open() as f:rows=[r for r in csv.DictReader(f) if None not in r.values()]
        return rows[-1] if rows else {}
    def wait(fn,timeout=300):
        end=time.monotonic()+timeout
        while time.monotonic()<end:
            if fn():return
            time.sleep(.2)
        subprocess.run(['import','-window','root',str(out/'timeout.png')],timeout=20);raise RuntimeError('Installer/game condition timed out')
    def active():return latest().get('input_ready')=='1'
    def find_window():
        nonlocal window
        window=subprocess.check_output(['xdotool','search','--onlyvisible','--name','Luanti|Minetest'],text=True).splitlines()[-1]
        subprocess.run(['xdotool','windowfocus','--sync',window],check=True)
    def close_game(label):
        find_window();subprocess.run(['import','-window',window,str(out/(label+'.png'))],check=True,timeout=20)
        subprocess.run(['xdotool','key','--clearmodifiers','alt+F4'],check=True)
        current=max((user/'logs').glob('*/cdda.log'),key=lambda p:p.stat().st_mtime)
        wait(lambda:'Final save: SUCCESS' in current.read_text(errors='replace'),90)
        time.sleep(1)
    def launch_installer(silent=True):
        trace.unlink(missing_ok=True)
        result=wine(a.installer.resolve(),*(['/S'] if silent else []),timeout=150)
        (out/('installer-'+str(len(checks))+'.log')).write_text(result.stdout+result.stderr)
        check('installer_exit_'+str(len(checks)),result.returncode==0)
        wait(active)
    uninstall_key='HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Minecataclysm'
    launch_installer(silent=False);check('default_per_user_payload_and_desktop_shortcut',(install/'Minecataclysm.exe').is_file() and shortcut.is_file())
    check('uninstall_entry',wine('reg','query',uninstall_key,'/v','DisplayName').returncode==0)
    close_game('installed-world')
    native_log=max((user/'logs').glob('*/cdda.log'),key=lambda p:p.stat().st_mtime)
    check('installed_native_canonical_save','Final save: SUCCESS' in native_log.read_text(errors='replace'))
    trace.unlink(missing_ok=True)
    reopen=subprocess.Popen(['wine','start','/wait',windows(shortcut)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    wait(active);close_game('desktop-reopen');reopen.wait(timeout=90)
    logs=sorted((user/'logs').glob('*/cdda.log'),key=lambda p:p.stat().st_mtime)
    check('desktop_shortcut_reloads_same_native_character','Restored character:' in logs[-1].read_text(errors='replace'))
    # Re-run setup with the game closed, then stop the automatic launch.
    launch_installer();close_game('updated-world');time.sleep(2)
    saves={str(p.relative_to(user)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (user/'cdda/save').rglob('*.sav')}
    check('canonical_save_exists_before_uninstall',bool(saves))
    result=wine(install/'Uninstall.exe','/S',timeout=90);check('uninstaller_exit',result.returncode==0)
    wait(lambda:not (install/'Minecataclysm.exe').exists(),30)
    check('uninstall_removes_program_and_shortcuts',not shortcut.exists() and not (install/'runtime').exists())
    after={str(p.relative_to(user)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (user/'cdda/save').rglob('*.sav')}
    check('uninstall_preserves_canonical_save_bytes',after==saves)
    launch_installer();close_game('reinstalled-world');logs=sorted((user/'logs').glob('*/cdda.log'),key=lambda p:p.stat().st_mtime)
    check('reinstall_restores_existing_world','Restored character:' in logs[-1].read_text(errors='replace'))
    return 0
if __name__=='__main__':raise SystemExit(main())
