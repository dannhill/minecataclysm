#!/usr/bin/env python3
"""Native ledge cancellation and death cleanup, on disposable oracle fixtures."""
import argparse
import json
from pathlib import Path
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('workspace', 'native-reader', 'artifacts'):
        parser.add_argument('--'+name, type=Path, required=True)
    args = parser.parse_args()
    ws, reader, out = args.workspace.resolve(), args.native_reader.resolve(), args.artifacts.resolve()
    out.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(ws/'protocol/python'))
    import flatbuffers
    from session_wire import NativeWire
    wire = NativeWire()
    from CDDA.CWM import CwmMessage as Msg, Payload, HelloRequest as Hello, MoveRequest as Move
    from CDDA.CWM import DecisionPrompt as Prompt, DecisionResponse as Response, WorldSnapshot as World
    checks, events, commands = {}, [], []

    def check(name, value):
        checks[name] = bool(value)
        (out/'checks.json').write_text(json.dumps(checks, indent=2)+'\n')
        print(name, 'PASS' if value else 'FAIL', flush=True)

    def message(kind, build):
        b = flatbuffers.Builder(256); value = build(b)
        return wire.finish(b,kind,value)

    def hello(b):
        Hello.HelloRequestStart(b); wire.hello_fields(b)
        return Hello.HelloRequestEnd(b)

    def move(b, direction):
        Move.MoveRequestStart(b); Move.MoveRequestAddCommandId(b,44); Move.MoveRequestAddDirection(b,direction)
        return Move.MoveRequestEnd(b)

    def answer(b, decision, choice):
        Response.DecisionResponseStart(b); Response.DecisionResponseAddDecisionId(b,decision)
        Response.DecisionResponseAddChoice(b,choice); return Response.DecisionResponseEnd(b)

    def send(c, body): c.sendall(struct.pack('>I',len(body))+body)

    def read(c):
        def exact(n):
            data = b''
            while len(data) < n:
                part = c.recv(n-len(data))
                if not part: raise EOFError()
                data += part
            return data
        size = struct.unpack('>I',exact(4))[0]
        if size > 16*1024*1024: raise ValueError('oversized server frame')
        return wire.observe(c,Msg.CwmMessage.GetRootAsCwmMessage(exact(size),0))

    base = out/'fixture'
    command = [str(reader),'--userdir',str(base),'--datadir',str(ws/'cdda/data'),
               '--create-ledge','--output',str(out/'fixture.json')]
    commands.append(command)
    with (out/'fixture.log').open('w') as log:
        result = subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=180)
    if result.returncode: raise RuntimeError('native fixture creation failed')
    check('independent_native_fixture', True)

    for case in ('ledge_cancel','death_keep','death_query','death_watch','death_reset','death_delete'):
        user = out/case/'user'; user.parent.mkdir(parents=True,exist_ok=True); shutil.copytree(base,user)
        dead = case.startswith('death')
        save = next((user/'save/audit_fixture').glob('*.sav'))
        header, body = save.read_text().split('\n',1); data = json.loads(body)
        if dead: data['player']['body']['torso']['hp_cur'] = 0
        save.write_text(header+'\n'+json.dumps(data))
        config = user/'config'; config.mkdir(exist_ok=True)
        (config/'options.json').write_text(json.dumps([
            {'name':'DEATHCAM','value':'always' if case=='death_watch' else 'never'},
            {'name':'SAFEMODE','value':'false'}, {'name':'AUTOSAFEMODE','value':'false'}]))
        options_path = user/'save/audit_fixture/worldoptions.json'
        options = json.loads(options_path.read_text())
        for option in options:
            if option['name']=='WORLD_END': option['value'] = case[6:] if case in ('death_query','death_reset','death_delete') else 'keep'
        options_path.write_text(json.dumps(options))
        prompts, latest, proc = [], None, None
        with tempfile.TemporaryDirectory(prefix='cwm-decision-') as temp, (user.parent/'server.log').open('w') as log:
            path = Path(temp)/'cwm.sock'
            command = [str(ws/'cdda/build/src/cdda-server'),'--userdir',str(user),
                       '--datadir',str(ws/'cdda/data'),'--world','audit_fixture','--socket',str(path)]
            commands.append(command); proc = subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT)
            try:
                deadline = time.monotonic()+60
                while time.monotonic()<deadline and not path.exists() and proc.poll() is None: time.sleep(.05)
                with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as c:
                    c.connect(str(path)); c.settimeout(15)
                    send(c,message(Payload.Payload.HelloRequest,hello))
                    while True:
                        msg = read(c)
                        if msg.PayloadType()==Payload.Payload.WorldSnapshot:
                            s = World.WorldSnapshot();s.Init(msg.Payload().Bytes,msg.Payload().Pos)
                            latest = {'time':s.SimulationTimeSeconds(),
                                      'position':[s.Entities(0).Pos().X()+s.Origin().X(),
                                                  s.Entities(0).Pos().Y()+s.Origin().Y(),s.Entities(0).Pos().Z()]}
                            break
                    send(c,message(Payload.Payload.MoveRequest,lambda b:move(b,0 if dead else 1)))
                    for _ in range(50):
                        try: msg = read(c)
                        except EOFError: break
                        if msg.PayloadType()==Payload.Payload.WorldSnapshot:
                            s = World.WorldSnapshot();s.Init(msg.Payload().Bytes,msg.Payload().Pos)
                            latest = {'time':s.SimulationTimeSeconds(),
                                      'position':[s.Entities(0).Pos().X()+s.Origin().X(),
                                                  s.Entities(0).Pos().Y()+s.Origin().Y(),s.Entities(0).Pos().Z()]}
                        if msg.PayloadType()!=Payload.Payload.DecisionPrompt: continue
                        p = Prompt.DecisionPrompt();p.Init(msg.Payload().Bytes,msg.Payload().Pos)
                        text = p.Text().decode(); choices = [p.Choices(i).decode() for i in range(p.ChoicesLength())]
                        prompts.append(text); events.append({'case':case,'text':text,'choices':choices,'state':latest})
                        if not dead:
                            check('ledge_has_explicit_native_menu', 'ledge' in text.lower() and 'Cancel' in choices)
                            send(c,message(Payload.Payload.DecisionResponse,lambda b:answer(b,p.DecisionId()+900,0)))
                            send(c,message(Payload.Payload.DecisionResponse,lambda b:answer(b,p.DecisionId(),65000)))
                            time.sleep(.3)
                            check('invalid_decision_does_not_abort_runtime',proc.poll() is None)
                            choice = choices.index('Cancel')
                        elif 'World policy' in text: choice = choices.index('Keep world')
                        elif text.startswith('Deathcam:'): choice = choices.index('Finish deathcam')
                        else: choice = len(choices)-1
                        send(c,message(Payload.Payload.DecisionResponse,lambda b:answer(b,p.DecisionId(),choice)))
                        if not dead:
                            # Allow native action result to settle, then save cleanly.
                            time.sleep(.3); proc.terminate(); break
                proc.wait(timeout=30)
                check(case+'_clean_exit',proc.returncode==0)
            finally:
                if proc.poll() is None:
                    proc.terminate()
                    try:proc.wait(timeout=10)
                    except subprocess.TimeoutExpired:proc.kill();proc.wait()
        text = (user.parent/'server.log').read_text()
        check(case+'_no_terminal_input_abort','input_manager::get_input_event' not in text and 'terminate called' not in text)
        if dead:
            check(case+'_death_notice','has died' in ' '.join(prompts))
            check(case+'_native_cleanup_completed','Native character death lifecycle completed.' in text)
            check(case+'_save_moved_to_native_graveyard',not list((user/'save/audit_fixture').glob('*.sav')) and bool(list((user/'graveyard').rglob('*.sav'))))
            if case=='death_delete':check('native_delete_world_policy',not (user/'save/audit_fixture').exists())
            else:check(case+'_world_retained',(user/'save/audit_fixture/worldoptions.json').exists())
            if case=='death_reset':check('native_reset_world_policy',not list((user/'save/audit_fixture/maps').rglob('*.map')))
            if case=='death_query':check('native_world_end_question_exposed',any('World policy' in p for p in prompts))
            if case=='death_watch':check('native_deathcam_question_exposed',any('Deathcam:' in p for p in prompts))
        else:
            command = [str(reader),'--userdir',str(user),'--datadir',str(ws/'cdda/data'),'--output',str(out/'ledge-after.json')]
            commands.append(command)
            with (out/'ledge-native-read.log').open('w') as log:
                result = subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=180)
            check('ledge_cancel_native_save_readable',result.returncode==0)
            if result.returncode==0:
                state=json.loads((out/'ledge-after.json').read_text())
                check('ledge_cancel_preserves_native_position',state['player_abs']==[60,60,0])
    (out/'events.json').write_text(json.dumps(events,indent=2)+'\n')
    (out/'commands.json').write_text(json.dumps(commands,indent=2)+'\n')
    return 0 if all(checks.values()) else 1


if __name__=='__main__':sys.exit(main())
