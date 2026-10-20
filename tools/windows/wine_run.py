#!/usr/bin/env python3
"""Run a Windows verification command in an isolated Wine prefix/X display."""
import argparse,fcntl,os,subprocess
from pathlib import Path

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prefix',type=Path,required=True);p.add_argument('--log',type=Path,required=True);p.add_argument('--timeout',type=int,default=180);p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
 a.log.parent.mkdir(parents=True,exist_ok=True)
 r,w=os.pipe();high=fcntl.fcntl(w,fcntl.F_DUPFD,64);os.close(w);w=high
 with a.log.with_suffix('.xvfb.log').open('w') as xvlog:
  display=subprocess.Popen(['Xvfb','-displayfd',str(w),'-screen','0','1280x800x24','-nolisten','tcp','-noreset','-dpi','96'],pass_fds=(w,),stdout=xvlog,stderr=subprocess.STDOUT)
  os.close(w)
  with os.fdopen(r) as ready:number=ready.readline().strip()
  if not number:raise RuntimeError('Private X display did not start')
  env=dict(os.environ,DISPLAY=':'+number,WINEPREFIX=str(a.prefix.resolve()),WINEARCH='win64',WINEDEBUG='-all',WINEDLLOVERRIDES='mscoree,mshtml,winemenubuilder.exe,winegstreamer=',LIBGL_ALWAYS_SOFTWARE='1',ALSOFT_DRIVERS='null');env.pop('XAUTHORITY',None);env.pop('WAYLAND_DISPLAY',None);env['XDG_SESSION_TYPE']='x11'
  try:
   with a.log.open('w') as log:result=subprocess.run(a.command,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=a.timeout)
  finally:
   subprocess.run(['wineserver','-k'],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=10)
   display.terminate();display.wait(timeout=10)
 return result.returncode
if __name__=='__main__':raise SystemExit(main())
