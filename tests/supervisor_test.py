#!/usr/bin/env python3
"""Verify every compiled alias executes the configured supervisor in isolation."""
import argparse
import json
import os
from pathlib import Path
import subprocess

SERVER = '''#!/usr/bin/env python3
import json,os,signal,socket,sys,time
from pathlib import Path
args=sys.argv[1:]; path=args[args.index('--socket')+1]
s=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM); s.bind(path); s.listen(1)
Path(os.environ['TEST_REPORT']+'-server.json').write_text(json.dumps(dict(args=args,socket=path,mode=os.stat(Path(path).parent).st_mode & 0o777)))
signal.signal(signal.SIGTERM,lambda *_:sys.exit(0))
print('CWM IPC server listening on: '+path,flush=True)
while True: time.sleep(.1)
'''
CLIENT = '''#!/usr/bin/env python3
import json,os,sys
from pathlib import Path
args=sys.argv[1:]; config=Path(args[args.index('--config')+1]).read_text()
Path(os.environ['TEST_REPORT']+'-client.json').write_text(json.dumps(dict(args=args,config=config)))
'''

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('project-root','launcher-build','coordinator-build','artifacts'):
        p.add_argument('--'+name,type=Path,required=True)
    args=p.parse_args(); out=args.artifacts.resolve(); out.mkdir(parents=True,exist_ok=False)
    checks={}
    custom=out/'custom'; custom.mkdir()
    script=custom/'start.sh'
    script.write_text('#!/usr/bin/env python3\nimport json,os,sys\nprint(json.dumps(dict(argv=sys.argv[1:],marker=os.environ.get("CDDA_WORLD"))))\nsys.exit(23)\n')
    script.chmod(0o700)
    server=out/'server.py'; server.write_text(SERVER); server.chmod(0o700)
    client=out/'client.py'; client.write_text(CLIENT); client.chmod(0o700)
    (out/'base.conf').write_text('enable_update_checker = false\n')
    for component,target in [('launcher','cwm-launcher'),('launcher','cwm-coordinator'),('coordinator','cwm-coordinator')]:
        build=args.launcher_build if component=='launcher' else args.coordinator_build
        binary=build.resolve()/target; name=component+'-'+target
        result=subprocess.run([str(binary),'--name','name with spaces'],env=dict(os.environ,CWM_PROJECT_ROOT=str(custom),CDDA_WORLD='isolated_probe'),capture_output=True,text=True,timeout=10)
        record=json.loads(result.stdout)
        checks[name+':arguments_and_status']=result.returncode==23 and record['argv']==['--name','name with spaces'] and record['marker']=='isolated_probe'
        report=out/name
        env=dict(os.environ,CDDA_BIN=str(server),LUANTI_BIN=str(client),CDDA_USERDIR=str(out/'user'),CDDA_WORLD='isolated_probe',LUANTI_WORLD=str(out/'world'),LUANTI_CONFIG=str(out/'base.conf'),LOG_DIR=str(out/(name+'-logs')),TEST_REPORT=str(report))
        env.pop('CWM_PROJECT_ROOT',None)
        result=subprocess.run([str(binary),'--name','probe_tester'],env=env,capture_output=True,text=True,timeout=20)
        a=json.loads(Path(str(report)+'-server.json').read_text()); b=json.loads(Path(str(report)+'-client.json').read_text())
        checks[name+':configured_supervisor']=result.returncode==0 and str(args.project_root.resolve()/'cdda/data') in a['args'] and 'cwm_socket_path = '+a['socket'] in b['config'] and a['mode']==0o700 and not Path(a['socket']).parent.exists()
    (out/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    for name,ok in checks.items(): print(name,'PASS' if ok else 'FAIL',flush=True)
    return 0 if all(checks.values()) else 1
if __name__=='__main__': raise SystemExit(main())
