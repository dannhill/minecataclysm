#!/usr/bin/env python3
"""Exercise the native sealed pocket opening in the actual Luanti renderer.

Requires an independently created --create-seals fixture, X11, xdotool,
ImageMagick and Pillow. Never opens an existing user world.
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
import select
import tempfile
import threading
import sys
import queue
import struct


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('workspace', 'fixture', 'native-reader', 'artifacts'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--reload-opening', action='store_true')
    args = parser.parse_args()
    ws, out = args.workspace.resolve(), args.artifacts.resolve()
    sys.path.insert(0,str(ws/'protocol/python'))
    from CDDA.CWM.CwmMessage import CwmMessage
    out.mkdir(parents=True, exist_ok=False)
    user = out / 'user'
    shutil.copytree(args.fixture.resolve(), user)
    (user / 'config/options.json').write_text(json.dumps([
        {'name': 'SAFEMODE', 'value': 'false'}, {'name': 'AUTOSAFEMODE', 'value': 'false'},
        {'name': 'AUTOSAVE', 'value': 'false'}, {'name': 'QUERY_DISASSEMBLE', 'value': 'true'}]))
    checks = {}
    injections=queue.Queue()
    def check(name, ok):
        checks[name] = bool(ok)
        (out / 'checks.json').write_text(json.dumps(checks, indent=2) + '\n')
        print(name, 'PASS' if ok else 'FAIL', flush=True)
        if not ok:
            raise AssertionError(name)

    old_window = subprocess.run(['xdotool', 'getactivewindow'], capture_output=True, text=True).stdout.strip()
    folder = out
    trace = out / 'camera.csv'
    with socket.socket() as temporary:
        temporary.bind(('127.0.0.1', 0))
        port = temporary.getsockname()[1]
    config = out / 'client.conf'
    config.write_text('screen_w = 1280\nscreen_h = 800\nfullscreen = false\nfps_max = 60\n'
                      'vsync = false\nenable_clouds = false\ngui_scaling = 1\n'
                      f'port = {port}\ncwm_trace_file = {trace}\n')
    env = dict(os.environ, CDDA_USERDIR=str(user), CDDA_WORLD='audit_fixture',
               LUANTI_WORLD=str(out / 'luanti'), LUANTI_CONFIG=str(config),
               LOG_DIR=str(out / 'logs'), CDDA_BIN=str(ws / 'cdda/build/src/cdda-server'),
               LUANTI_BIN=str(ws / 'luanti/bin/luanti'), CDDA_CONTINUOUS='1')
    env.pop('CDDA_TERRAIN_DEMO', None)
    # A local relay records real renderer traffic and injects explicit protocol
    # probes. It renumbers client envelope sequences for the additional frames;
    # command/quote identity and payload bytes remain unchanged.
    scratch = tempfile.TemporaryDirectory(prefix='cwm-conversation-gui-')
    relay_path = Path(scratch.name) / 'relay.sock'
    native_path = out / 'native-socket'
    stop, drop = threading.Event(), threading.Event()
    shutting_down = threading.Event()
    expected_shutdown_errors = []
    relay_errors = []
    listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    listener.bind(str(relay_path)); listener.listen(1); listener.settimeout(.1)
    def relay():
        try:
            while not stop.is_set():
                try:
                    client_socket, _ = listener.accept()
                except socket.timeout:
                    continue
                with client_socket, socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server_socket:
                    server_socket.connect(native_path.read_text().strip())
                    native_sequence=0;client_buffer=bytearray()
                    def forward_client(packet):
                        nonlocal native_sequence
                        body=bytearray(packet[4:]);message=CwmMessage.GetRootAs(body)
                        native_sequence+=1
                        offset=message._tab.Offset(4)
                        if not offset:raise AssertionError('Client sequence must be explicit')
                        struct.pack_into('<Q',body,message._tab.Pos+offset,native_sequence)
                        frame=struct.pack('>I',len(body))+body
                        with (out/'client-wire.bin').open('ab') as capture:capture.write(frame)
                        server_socket.sendall(frame)
                    while not stop.is_set():
                        if drop.is_set():
                            drop.clear()
                            break
                        while not injections.empty():forward_client(injections.get_nowait())
                        readable, _, _ = select.select([client_socket, server_socket], [], [], .03)
                        closed=False
                        for source in readable:
                            data=source.recv(1<<20)
                            if not data:closed=True;break
                            if source is client_socket:
                                client_buffer.extend(data)
                                while len(client_buffer)>=4:
                                    size=struct.unpack('>I',client_buffer[:4])[0]
                                    if len(client_buffer)<size+4:break
                                    forward_client(bytes(client_buffer[:size+4]));del client_buffer[:size+4]
                            else:
                                with (out/'server-wire.bin').open('ab') as capture:capture.write(data)
                                client_socket.sendall(data)
                        if closed:break
        except (ConnectionResetError, BrokenPipeError) as error:
            if shutting_down.is_set(): expected_shutdown_errors.append(str(error))
            else: relay_errors.append(str(error))
        except Exception as error:
            relay_errors.append(str(error))
    relay_thread = threading.Thread(target=relay, daemon=True)
    relay_thread.start()
    wrapper = out / 'client-relay.py'
    wrapper.write_text("#!/usr/bin/env python3\nimport os,sys,re\nfrom pathlib import Path\n" +
        "args=sys.argv[1:]\ni=args.index('--config')+1\np=Path(args[i])\ns=p.read_text()\n" +
        f"Path({str(native_path)!r}).write_text(re.findall(r'^cwm_socket_path = (.+)$',s,re.M)[-1])\n" +
        f"p=Path({str(out / 'relay-client.conf')!r})\n" +
        f"p.write_text(s+'\\ncwm_socket_path = {relay_path}\\n')\nargs[i]=str(p)\n" +
        f"os.execv({str(ws / 'luanti/bin/luanti')!r},[{str(ws / 'luanti/bin/luanti')!r},*args])\n")
    wrapper.chmod(0o755)
    env['LUANTI_BIN'] = str(wrapper)
    def rows():
        if not trace.exists():
            return []
        with trace.open() as stream:
            return [r for r in csv.DictReader(stream) if r.get('scene_origin_y') is not None]
    def latest():
        return rows()[-1]
    def wait(predicate, timeout=12):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline and proc.poll() is None:
            data = rows()
            if data and predicate(data[-1]):
                return data[-1]
            time.sleep(.05)
        raise RuntimeError('GUI condition not reached; inspect trace/logs')
    def xdo(*argv):
        # Xvfb without a WM has no _NET_ACTIVE_WINDOW support. Direct focus
        # is sufficient for the real client on this isolated display.
        if os.environ.get('CWM_GUI_NO_WM') == '1' and argv[0] == 'windowactivate':
            argv = ('windowfocus', *argv[1:])
        subprocess.run(['xdotool', *argv], check=True, capture_output=True, timeout=5)
    def tap(key, sneak=False):
        if sneak:
            xdo('keydown', 'Shift_L')
            time.sleep(.12)
        xdo('keydown', '--window', window, key)
        time.sleep(.12)
        xdo('keyup', '--window', window, key)
        if sneak:
            time.sleep(.12)
            xdo('keyup', 'Shift_L')
        time.sleep(.3)
    def shot(name):
        time.sleep(.6)  # Allow actual asynchronous mesh installation.
        subprocess.run(['import', '-window', window, str(folder / name)], check=True, timeout=10)
    window = None
    with (out / 'launcher.log').open('w') as log:
        proc = subprocess.Popen([str(ws / 'start.sh'), '--go', '--name', 'conversation_tester', '--port', str(port), '--info'],
                                env=env, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            deadline = time.monotonic() + 85
            while time.monotonic() < deadline and proc.poll() is None:
                descendants = [proc.pid]
                for pid in descendants:
                    try:
                        descendants.extend(map(int, Path(f'/proc/{pid}/task/{pid}/children').read_text().split()))
                        if Path(f'/proc/{pid}/comm').read_text().strip() != 'luanti':
                            continue
                    except (FileNotFoundError, ProcessLookupError):
                        continue
                    found = subprocess.run(['xdotool', 'search', '--onlyvisible', '--pid', str(pid)], capture_output=True, text=True)
                    if found.stdout.strip():
                        window = found.stdout.splitlines()[0]
                if window and len(rows()) > 20:
                    break
                time.sleep(.2)
            check('actual_start_ready', bool(window) and len(rows()) > 20)
            xdo('windowactivate', '--sync', window)
            time.sleep(1)
            wait(lambda r: int(r['input_ready']) == 1 and int(r['pause_reasons']) == 0)
            sys.path.insert(0, str(ws / 'protocol/python'))
            from CDDA.CWM.CwmMessage import CwmMessage
            from CDDA.CWM.Payload import Payload
            from CDDA.CWM.InventoryView import InventoryView
            from CDDA.CWM.DecisionPrompt import DecisionPrompt
            from CDDA.CWM.WorldSnapshot import WorldSnapshot
            def messages(kind,direction="server"):
                import struct
                buf=(out/(direction+'-wire.bin')).read_bytes();offset=0;found=[]
                while offset+4<=len(buf):
                    n=struct.unpack('>I',buf[offset:offset+4])[0];offset+=4
                    if offset+n>len(buf):break
                    msg=CwmMessage.GetRootAs(buf[offset:offset+n]);offset+=n
                    if msg.PayloadType()==kind:found.append(msg)
                return found
            def prompt():
                msg=messages(Payload.DecisionPrompt)[-1]
                p=DecisionPrompt();p.Init(msg.Payload().Bytes,msg.Payload().Pos)
                return p
            def labels(p): return [p.Choices(n).decode() for n in range(p.ChoicesLength())]
            def choose(n):
                old=latest()['pending_decision'];tap(str(n+1))
                wait(lambda r:r['pending_decision']!=old)
            from CDDA.CWM.CommandAck import CommandAck
            from CDDA.CWM.ItemTransferRequest import ItemTransferRequest
            from formspec_geometry import geometry
            def idle():wait(lambda r:int(r['pending_move'])==0 and int(r['pending_decision'])==0)
            def ready():wait(lambda r:int(r['input_ready'])==1 and int(r['pending_move'])==0 and int(r['pending_decision'])==0 and int(r['pause_reasons'])==0)
            def view():
                for msg in reversed(messages(Payload.InventoryView)):
                    v=InventoryView();v.Init(msg.Payload().Bytes,msg.Payload().Pos)
                    if v.ViewId():return v
                raise RuntimeError('Missing native inventory view')
            def entries(v):return [v.Entries(n) for n in range(v.EntriesLength())]
            def open_inventory():
                if int(latest()['equipment_form'])!=1:tap('i')
                wait(lambda r:int(r['equipment_form'])==1 and int(r['inventory_view'])>0 and int(r['pause_reasons'])&2)
                shot('inventory.png');return view()
            def click(x,y):
                ox,oy,unit=geometry(out/'inventory.png')
                xdo('mousemove','--window',window,str(round(ox+x*unit)),str(round(oy+y*unit)));xdo('click','1');time.sleep(.3)
            def water_in(v,kind):
                parents=[e.Id() for e in entries(v) if e.TypeId().decode()==kind]
                return sum(e.Charges() for e in entries(v) if e.ParentId() in parents and e.TypeId().decode() in ('water','water_clean'))
            def close_inventory():tap('Escape');wait(lambda r:int(r['equipment_form'])==0);ready()
            def sealed(v,kind):
                owner=next(e for e in entries(v) if e.TypeId().decode()==kind)
                return any(v.Pockets(n).Sealed() for n in range(v.PocketsLength()) if v.Pockets(n).OwnerId()==owner.Id())
            def select_item(kind):
                v=view();item=next(e for e in entries(v) if e.TypeId().decode()==kind)
                values=sorted([e for e in entries(v) if not e.QuickSlot()],key=lambda e:e.UiOrder() or 4096+e.Id())
                index=next(n for n,e in enumerate(values) if e.Id()==item.Id())
                click(.5+(index%9)*1.15+.525,5.45+(index//9)*1.15+.525)
                wait(lambda row:int(row['equipment_selected'])==item.Id());return item
            def refresh():
                old=latest()['inventory_view'];shot('inventory.png');click(12.35,1.25)
                wait(lambda row:row['inventory_view']!=old);return view()
            def open_seal(kind):
                item=select_item(kind);check('sealed_metadata_'+kind+'_'+str(len(checks)),item.Seal() is not None and not item.Seal().Reason())
                shot('selected-'+kind+'.png');click(13.4,10.4);wait(lambda row:int(row['pending_decision'])>0)
                return item
            if not args.reload_opening:
                v=open_inventory();check('all_fixture_containers_start_sealed',all(sealed(v,k) for k in ('bottle_plastic','condiment_bottle_sealed','can_drink')))
                frozen=latest()['simulation_time'];time.sleep(.7)
                check('inventory_inspection_does_not_open_or_advance',latest()['simulation_time']==frozen and sealed(view(),'bottle_plastic'))
                open_seal('bottle_plastic');check('opening_has_explicit_warning_and_cancel','Preservation' in prompt().Text().decode() and labels(prompt())[-1]=='Cancel')
                shot('opening-confirmation.png');choose(len(labels(prompt()))-1);idle();v=open_inventory()
                check('cancel_keeps_native_seal_and_quantity',sealed(v,'bottle_plastic') and water_in(v,'bottle_plastic')==2)
                open_seal('bottle_plastic');choose(0);idle();v=open_inventory()
                check('opening_breaks_only_selected_seal',not sealed(v,'bottle_plastic') and sealed(v,'condiment_bottle_sealed') and sealed(v,'can_drink'))
                check('opening_preserves_type_and_charges',water_in(v,'bottle_plastic')==2)
                opened=next(e for e in entries(v) if e.TypeId()==b'bottle_plastic')
                check('fresh_view_replaces_opening_with_pouring',opened.Seal() is None and opened.Liquid() is not None and not opened.Liquid().Reason())
                command=messages(Payload.ItemTransferRequest,'client')[-1];request=ItemTransferRequest();request.Init(command.Payload().Bytes,command.Payload().Pos)
                check('opening_request_is_semantic_and_has_no_quantity',request.Action()==5 and not request.Quantity() and not request.DestinationId())
                def acks():
                    result=[]
                    for msg in messages(Payload.CommandAck):
                        ack=CommandAck();ack.Init(msg.Payload().Bytes,msg.Payload().Pos)
                        if ack.CommandId()==request.CommandId():result.append(ack)
                    return result
                count=len(acks());snapshots=len(messages(Payload.SnapshotAck,'client'));data=bytes(command._tab.Bytes);injections.put(struct.pack('>I',len(data))+data)
                deadline=time.monotonic()+12
                while (len(acks())<=count or len(messages(Payload.SnapshotAck,'client'))<=snapshots) and time.monotonic()<deadline:time.sleep(.05)
                check('opening_replay_returns_cached_success',len(acks())>count and acks()[-1].Accepted())
                wait(lambda row:int(row['input_ready'])==1 and int(row['pending_move'])==0)
                if int(latest()['equipment_form'])==1:refresh()
                v=open_inventory();check('opening_replay_does_not_touch_other_seals',not sealed(v,'bottle_plastic') and sealed(v,'condiment_bottle_sealed') and water_in(v,'bottle_plastic')==2)
                open_seal('can_drink');choose(0);wait(lambda row:int(row['pending_decision'])>0)
                check('open_stashed_can_uses_native_spill_choices',any('Pour' in v for v in labels(prompt())))
                shot('native-open-can-liquid-choices.png')
                choose(len(labels(prompt()))-1);idle();v=open_inventory()
                check('cancelled_spill_sets_open_can_on_ground',not any(e.TypeId()==b'can_drink' for e in entries(v)))
                check('other_liquids_are_unchanged',water_in(v,'bottle_plastic')==2 and water_in(v,'condiment_bottle_sealed')==2)
                close_inventory();ready();connection=latest()['connection_id'];sent=len(messages(Payload.ItemTransferRequest,'client'));drop.set()
                wait(lambda row:row['connection_id']!=connection and int(row['input_ready'])==1,timeout=25)
                check('reconnect_does_not_issue_another_opening',len(messages(Payload.ItemTransferRequest,'client'))==sent)
                v=open_inventory();check('reconnect_preserves_open_and_closed_states',not sealed(v,'bottle_plastic') and sealed(v,'condiment_bottle_sealed'))
                shot('final-open-and-sealed.png')
            else:
                check('reload_does_not_issue_open_commands',not messages(Payload.ItemTransferRequest,'client'))
                v=open_inventory();check('reloaded_native_seals_are_distinct',not sealed(v,'bottle_plastic') and sealed(v,'condiment_bottle_sealed'))
                check('reloaded_native_liquids_unchanged',water_in(v,'bottle_plastic')==2 and water_in(v,'condiment_bottle_sealed')==2)
                check('reloaded_can_remains_on_ground',not any(e.TypeId()==b'can_drink' for e in entries(v)))
                shot('reloaded-seals.png')
            final=latest();(out/'final-trace.json').write_text(json.dumps(final,indent=2)+'\n')
        finally:
            shutting_down.set()
            if proc.poll() is None:
                os.killpg(proc.pid,signal.SIGTERM)
                try:proc.wait(timeout=45)
                except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
            stop.set();relay_thread.join(timeout=3);listener.close();scratch.cleanup()
            (out/'relay-errors.json').write_text(json.dumps(relay_errors))
            if old_window:subprocess.run(['xdotool','windowactivate',old_window],capture_output=True)
    check('relay_completed_without_errors',not relay_errors)
    logs='\n'.join(p.read_text(errors='replace') for p in (out/'logs').rglob('*.log'))
    check('seal_dialogs_accepted_by_actual_renderer','Invalid formspec' not in logs)
    output=out/'native.json'
    with (out/'native.log').open('w') as log:
        result=subprocess.run([str(args.native_reader.resolve()),'--userdir',str(user),'--datadir',str(ws/'cdda/data'),'--output',str(output)],stdout=log,stderr=subprocess.STDOUT,timeout=180)
    check('seal_save_readable_by_independent_pinned_core',result.returncode==0)
    native=json.loads(output.read_text());player=native['player']
    check('canonical_native_position_preserved',native['player_abs']==[60,60,0])
    check('opening_has_no_fabricated_native_activity',player['activity']['type']=='ACT_NULL')
    def items(value):
        if isinstance(value,dict):
            if 'typeid' in value:yield value
            for child in value.values():yield from items(child)
        elif isinstance(value,list):
            for child in value:yield from items(child)
    containers={it['typeid']:it for it in items(player) if it['typeid'] in ('bottle_plastic','condiment_bottle_sealed','can_drink')}
    def native_sealed(it):return any(p['_sealed'] for p in it['contents']['contents'])
    check('canonical_bottle_is_open',not native_sealed(containers['bottle_plastic']))
    check('canonical_unselected_condiment_remains_sealed',native_sealed(containers['condiment_bottle_sealed']))
    check('canonical_carried_water_quantity_preserved',sum(it.get('charges',0) for it in items(player) if it['typeid']=='water_clean')==4)
    ground=[it for row in native['ground_items'] for it in items(row['items'])]
    can=next((it for it in ground if it['typeid']=='can_drink'),None)
    check('canonical_can_is_open_on_ground',can is not None and not native_sealed(can))
    check('canonical_water_not_duplicated_or_lost',sum(it.get('charges',0) for it in ground if it['typeid']=='water_clean')==1)
    (out/'summary.json').write_text(json.dumps({'checks':checks,'native_save':str(output)},indent=2)+'\n')

if __name__=='__main__':main()
