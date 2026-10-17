#!/usr/bin/env python3
"""Exercise the external storage, partial collection and container transfer in the actual Luanti renderer.

Requires an independently created --create-external fixture, X11, xdotool,
ImageMagick and Pillow. Never opens an existing user world.
"""
import argparse
import csv
import json
import math
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('workspace', 'fixture', 'native-reader', 'artifacts'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--action-driven', action='store_true', help='Verify ordinary start.sh mode without the real-time scheduler')
    parser.add_argument('--resume-only', action='store_true')
    parser.add_argument('--feedback', action='store_true')
    parser.add_argument('--automatic-return', action='store_true', help='Verify UX-02 returns to the transfer panel')
    parser.add_argument('--save-active', action='store_true')
    args = parser.parse_args()
    ws, out = args.workspace.resolve(), args.artifacts.resolve()
    out.mkdir(parents=True, exist_ok=False)
    user = out / 'user'
    shutil.copytree(args.fixture.resolve(), user)
    (user / 'config/options.json').write_text(json.dumps([
        {'name': 'SAFEMODE', 'value': 'false'}, {'name': 'AUTOSAFEMODE', 'value': 'false'},
        {'name': 'AUTOSAVE', 'value': 'false'}]))
    checks = {}
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
    if args.action_driven:
        env['CDDA_CONTINUOUS'] = '0'
        env.pop('CDDA_REALTIME', None)
    # A byte-transparent local relay lets the real client lose IPC while a
    # selection is queued under manual pause. Gameplay still runs in CDDA.
    scratch = tempfile.TemporaryDirectory(prefix='cwm-body-gui-')
    relay_path = Path(scratch.name) / 'relay.sock'
    native_path = out / 'native-socket'
    stop, drop = threading.Event(), threading.Event()
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
                    while not stop.is_set():
                        if drop.is_set():
                            drop.clear()
                            break
                        readable, _, _ = select.select([client_socket, server_socket], [], [], .03)
                        closed = False
                        for source in readable:
                            data = source.recv(1 << 20)
                            if not data:
                                closed = True
                                break
                            with (out / ('client-wire.bin' if source is client_socket else 'server-wire.bin')).open('ab') as capture:
                                capture.write(data)
                            (server_socket if source is client_socket else client_socket).sendall(data)
                        if closed:
                            break
        except Exception as error:
            if not stop.is_set(): relay_errors.append(str(error))
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
    def turn(yaw_target, pitch_target=0):
        for _ in range(25):
            r = latest()
            yaw = math.degrees(math.atan2(-float(r['dir_x']), float(r['dir_z'])))
            pitch = math.degrees(math.asin(max(-1, min(1, float(r['dir_y'])))))
            dyaw = (yaw_target - yaw + 180) % 360 - 180
            dpitch = pitch_target - pitch
            if max(abs(dyaw), abs(dpitch)) < 1:
                break
            xdo('mousemove_relative', '--', str(max(-130, min(130, round(-dyaw / .2)))),
                str(max(-130, min(130, round(-dpitch / .2)))))
            time.sleep(.12)
        time.sleep(.4)
    window = None
    with (out / 'launcher.log').open('w') as log:
        proc = subprocess.Popen([str(ws / 'start.sh'), '--go', '--name', 'body_tester', '--port', str(port), '--info'],
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
            time.sleep(.1 if args.resume_only else 1)
            wait(lambda r: int(r['input_ready']) == 1 and int(r['pause_reasons']) == 0)
            sys.path.insert(0, str(ws / 'protocol/python'))
            from CDDA.CWM.CwmMessage import CwmMessage
            from CDDA.CWM.Payload import Payload
            from CDDA.CWM.InventoryView import InventoryView
            def views():
                import struct
                buf = (out / 'server-wire.bin').read_bytes(); offset = 0; found = []
                while offset + 4 <= len(buf):
                    n = struct.unpack('>I', buf[offset:offset+4])[0]; offset += 4
                    if offset+n > len(buf): break
                    msg = CwmMessage.GetRootAs(buf[offset:offset+n]); offset += n
                    if msg.PayloadType() == Payload.InventoryView:
                        v = InventoryView(); v.Init(msg.Payload().Bytes,msg.Payload().Pos)
                        if v.ViewId(): found.append(v)
                return found
            def cancel_choice():
                import struct
                from CDDA.CWM.DecisionPrompt import DecisionPrompt
                buf = (out / 'server-wire.bin').read_bytes(); offset = 0; options = []
                while offset + 4 <= len(buf):
                    n = struct.unpack('>I',buf[offset:offset+4])[0]; offset += 4
                    if offset + n > len(buf): break
                    msg = CwmMessage.GetRootAs(buf[offset:offset+n]); offset += n
                    if msg.PayloadType() == Payload.DecisionPrompt:
                        prompt = DecisionPrompt();prompt.Init(msg.Payload().Bytes,msg.Payload().Pos)
                        options = [prompt.Choices(i).decode() for i in range(prompt.ChoicesLength())]
                assert options and options[-1] == 'Cancel' and len(options) <= 9, options
                return str(len(options))
            def open_inventory():
                if int(latest().get('inventory_return',0)) and int(latest()['transfer_token'])==0:
                    wait(lambda r:int(r['equipment_form'])==1 and int(r['inventory_view'])>0)
                elif int(latest()['equipment_form'])==1 and int(latest()['inventory_view'])==0:
                    wait(lambda r:int(r['inventory_view'])>0)
                if int(latest()['equipment_form']) == 1 and int(latest()['inventory_view']) > 0:
                    return views()[-1]
                tap('i')
                wait(lambda r: int(r['equipment_form']) == 1 and int(r['inventory_view']) > 0)
                return views()[-1]
            turn(-90, -8)
            wait(lambda r:int(r['ground_hover'])==1)
            xdo('click','3')
            wait(lambda r:int(r['equipment_form'])==1 and int(r['inventory_view'])>0)
            view=views()[-1];shot('storage.png')
            check('storage_contents_have_no_rotating_drop_nodes',int(latest()['ground_target_visual_nodes'])==0)

            from formspec_geometry import geometry
            origin_x,origin_y,unit=geometry(out/'storage.png',22,9)
            def entries(v):return [v.Entries(n) for n in range(v.EntriesLength())]
            def find(v,kind,external,parent=None):
                return next(e for e in entries(v) if e.TypeId().decode()==kind and e.External()==external and (parent is None or e.ParentId()==parent))
            def point(e,v):
                pane=[x for x in entries(v) if x.External()==e.External()];index=next(n for n,x in enumerate(pane) if x.Id()==e.Id())
                assert index<27
                return (.5 if e.External() else 11.5)+(index%9)*1.12+.525,2+(index//9)*1.15+.525
            def mouse(x,y):xdo('mousemove','--window',window,str(round(origin_x+x*unit)),str(round(origin_y+y*unit)))
            def click(x,y):
                xdo('windowactivate','--sync',window);time.sleep(.05);mouse(x,y);xdo('click','1');time.sleep(.2)
            def select_item(e,v):click(*point(e,v));wait(lambda r:int(r['equipment_selected'])==e.Id())
            def amount(value):click(12.4,7.25);xdo('key','ctrl+a');xdo('type','--clearmodifiers',str(value));time.sleep(.15)
            def drag(e,v,target,expect_sent=True):
                sent=int(latest()['transfers_sent']);source=point(e,v);mouse(*source);xdo('mousedown','1');time.sleep(.15)
                for n in range(1,9):mouse(source[0]+(target[0]-source[0])*n/8,source[1]+(target[1]-source[1])*n/8);time.sleep(.05)
                xdo('mouseup','1');time.sleep(.3)
                if expect_sent:wait(lambda r:int(r['transfers_sent'])==sent+1)
                return sent
            def finish():
                wait(lambda r:int(r['pending_move'])==0 and int(r['transfer_token'])==0 and int(r['equipment_form'])==1 and int(r['inventory_view'])>0,timeout=25)
                time.sleep(.5) # State trace precedes installation of the corresponding formspec.
                return views()[-1]
            if args.resume_only:
                check('reloaded_external_menu_keeps_owned_twenty_two_rounds',sum(e.Charges() for e in entries(view) if not e.External() and e.TypeId().decode()=='9mm')==22)
                check('reloaded_external_menu_keeps_twenty_eight_rounds_outside',sum(e.Charges() for e in entries(view) if e.External() and e.TypeId().decode()=='9mm')==(23 if args.feedback else 28))
                pack=find(view,'backpack_hiking',True)
                check('reloaded_external_backpack_retains_two_nested_rounds',find(view,'9mm',True,pack.Id()).Charges()==2)
                check('reloaded_nested_rock_stays_owned',bool(find(view,'rock',False)))
                check('restart_does_not_replay_transfers',int(latest()['transfers_sent'])==0)
                shot('storage-reloaded.png');tap('Escape')
            else:
                check('external_two_panes_use_native_furniture_and_nested_pockets',bool(view.ExternalCoord()) and bool(view.ExternalLabel()) and find(view,'9mm',True).Charges()==30 and bool(find(view,'rock',True).ParentId()))
                stopped=latest()['simulation_time'];position=tuple(latest()[k] for k in ('target_x','target_y','target_z'))
                xdo('keydown','w');time.sleep(.6);xdo('keyup','w')
                check('storage_menu_pauses_native_time_and_movement',latest()['simulation_time']==stopped and tuple(latest()[k] for k in ('target_x','target_y','target_z'))==position)
                ammo=find(view,'9mm',True);select_item(ammo,view);amount(31);sent=drag(ammo,view,(16.5,5.95),False)
                check('invalid_partial_quantity_is_local_rejection_only',int(latest()['transfers_sent'])==sent and int(latest()['equipment_form'])==1)
                amount(7);shot('selected-seven.png');drag(ammo,view,(16.5,5.95));view=finish()
                check('partial_native_pickup_leaves_twenty_three_external',find(view,'9mm',True,0).Charges()==23)
                check('partial_native_pickup_adds_exact_seven_owned',sum(e.Charges() for e in entries(view) if not e.External() and e.TypeId().decode()=='9mm')==27)
                check('paid_pickup_returns_to_external_menu',int(latest()['external_form'])==1 and int(latest()['native_work_settled'])==1)
                ammo=find(view,'9mm',False);select_item(ammo,view);amount(3);drag(ammo,view,(5.5,5.95));view=finish()
                check('deposit_uses_selected_furniture_not_avatar_tile',sum(e.Charges() for e in entries(view) if e.External() and e.TypeId().decode()=='9mm')==26)
                ammo=find(view,'9mm',False);pack=find(view,'backpack_hiking',True);select_item(ammo,view);amount(2);drag(ammo,view,point(pack,view));view=finish()
                pack=find(view,'backpack_hiking',True)
                check('external_container_insert_retains_native_parent_and_two_rounds',find(view,'9mm',True,pack.Id()).Charges()==2)
                rock=find(view,'rock',True);select_item(rock,view);amount(1);drag(rock,view,(16.5,5.95));view=finish()
                check('nested_external_pickup_removes_contents_without_collecting_container',bool(find(view,'rock',False)) and bool(find(view,'backpack_hiking',True)) and not any(e.External() and e.TypeId().decode()=='rock' for e in entries(view)))
                bat=find(view,'bat',False);bottle=find(view,'bottle_plastic',False);select_item(bat,view);drag(bat,view,point(bottle,view));view=finish()
                check('native_capacity_rejection_reopens_without_losing_bat',bool(find(view,'bat',False)) and int(latest()['external_form'])==1)
                shot('capacity-error.png')
                if args.feedback:
                    def shift_move(e,v):
                        sent=int(latest()['transfers_sent']);mouse(*point(e,v));xdo('keydown','Shift_L');time.sleep(.08)
                        xdo('click','1');xdo('keyup','Shift_L');wait(lambda r:int(r['transfers_sent'])==sent+1)
                        return finish()
                    ammo=find(view,'9mm',True,0);select_item(ammo,view);amount(4);view=shift_move(ammo,view)
                    check('shift_click_collects_selected_quantity',sum(e.Charges() for e in entries(view) if not e.External() and e.TypeId().decode()=='9mm')==26)
                    ammo=find(view,'9mm',False);select_item(ammo,view);amount(4);view=shift_move(ammo,view)
                    check('shift_click_deposits_to_opposite_pane',find(view,'9mm',True,0).Charges()==26)
                    rock=find(view,'rock',False);select_item(rock,view);drag(rock,view,(-1,4));view=finish()
                    check('owned_outside_drag_drops_without_depositing_in_storage',not any(e.TypeId().decode()=='rock' for e in entries(view)))
                    tap('Escape');wait(lambda r:int(r['equipment_form'])==0)
                    turn(0,88);wait(lambda r:int(r['ground_hover'])==1 and int(r['ground_target_items'])==1)
                    tap('F7');wait(lambda r:int(r['pause_reasons'])==1)
                    xdo('click','3');time.sleep(.6)
                    check('paused_loose_pickup_is_rejected_without_queue',int(latest()['queued_pickup'])==0 and int(latest()['pending_move'])==0 and int(latest()['ground_target_items'])==1)
                    tap('F7');wait(lambda r:int(r['pause_reasons'])==0);time.sleep(.8)
                    check('unpause_does_not_collect_previous_loose_click',int(latest()['ground_target_items'])==1 and int(latest()['queued_pickup'])==0)
                    xdo('click','3');wait(lambda r:int(r['ground_target_items'])==0 and int(r['pending_move'])==0)
                    check('fresh_unpaused_click_collects_loose_item',True)
                    turn(-90,-8);wait(lambda r:int(r['ground_hover'])==1);xdo('click','3')
                    wait(lambda r:int(r['equipment_form'])==1 and int(r['inventory_view'])>0);view=views()[-1];time.sleep(.5)
                    ammo=find(view,'9mm',True,0);select_item(ammo,view);amount(5);drag(ammo,view,(-1,4));view=finish()
                    check('external_outside_drop_keeps_unmoved_twenty_one',find(view,'9mm',True,0).Charges()==21)
                    shot('outside-drag-ground-drop.png')
                tap('Escape');wait(lambda r:int(r['equipment_form'])==0)
                tap('F7');wait(lambda r:int(r['pause_reasons'])==1)
                xdo('click','3');wait(lambda r:int(r['equipment_form'])==1 and int(r['inventory_view'])>0);view=views()[-1]
                ammo=find(view,'9mm',True,0);select_item(ammo,view);amount(1);sent=drag(ammo,view,(16.5,5.95),False)
                check('manual_pause_never_queues_collection',int(latest()['transfers_sent'])==sent and int(latest()['equipment_form'])==1)
                tap('Escape');wait(lambda r:int(r['equipment_form'])==0 and int(r['pause_reasons'])==1)
                tap('F7');wait(lambda r:int(r['pause_reasons'])==0)
                check('resuming_never_replays_paused_drag',int(latest()['transfers_sent'])==sent)
                xdo('click','3');wait(lambda r:int(r['equipment_form'])==1 and int(r['inventory_view'])>0)
                connection=latest()['connection_id'];drop.set()
                wait(lambda r:r['connection_id']!=connection and int(r['input_ready'])==1 and int(r['equipment_form'])==0,timeout=25)
                check('recovery_discards_external_selection_and_does_not_replay',int(latest()['transfers_sent'])==sent)
                xdo('click','3');wait(lambda r:int(r['equipment_form'])==1 and int(r['inventory_view'])>0);view=views()[-1]
                pack=find(view,'backpack_hiking',True)
                check('resync_keeps_external_nested_contents',find(view,'9mm',True,pack.Id()).Charges()==2)
                tap('Escape');wait(lambda r:int(r['equipment_form'])==0)
                turn(90,-8);wait(lambda r:int(r['ground_hover'])==1);xdo('click','3');wait(lambda r:int(r['equipment_form'])==1 and int(r['inventory_view'])>0);view=views()[-1]
                check('empty_storage_is_interactive',bool(view.ExternalCoord()) and not any(e.External() for e in entries(view)))
                tap('Escape');wait(lambda r:int(r['equipment_form'])==0)
                turn(0,-50);wait(lambda r:int(r['ground_hover'])==1);xdo('click','3');wait(lambda r:int(r['equipment_form'])==1 and int(r['inventory_view'])==0)
                check('sealed_storage_exposes_no_item_view',int(latest()['external_entries'])==0)
                shot('sealed-storage.png');tap('Escape')
                check('actual_runtime_survives',proc.poll() is None)
        finally:
            stop.set()  # Declared shutdown: native peers may reset while closing.
            subprocess.run(['xdotool', 'keyup', 'w'], capture_output=True)
            stop.set()
            if proc.poll() is None:
                os.killpg(proc.pid, signal.SIGTERM)
                try:
                    proc.wait(timeout=45)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait()
            stop.set()
            relay_thread.join(timeout=3)
            listener.close()
            (out / 'relay-errors.json').write_text(json.dumps(relay_errors))
            scratch.cleanup()
            if old_window:
                subprocess.run(['xdotool', 'windowactivate', old_window], capture_output=True)
    check('byte_relay_completed_without_errors', not relay_errors)
    output = out / 'native.json'
    with (out / 'native.log').open('w') as log:
        result = subprocess.run([str(args.native_reader.resolve()), '--userdir', str(user),
            '--datadir', str(ws / 'cdda/data'), '--output', str(output)], stdout=log, stderr=subprocess.STDOUT, timeout=180)
    check('transfer_save_readable_by_pristine_native_core',result.returncode==0)
    native=json.loads(output.read_text())
    def items(value):
        found=[]
        if isinstance(value,dict):
            if 'typeid' in value:found.append(value)
            for child in value.values():found.extend(items(child))
        elif isinstance(value,list):
            for child in value:found.extend(items(child))
        return found
    owned=items(native['player']);ground=items(native['ground_items'])
    check('canonical_total_ammo_conserved',sum(i.get('charges',0) for i in owned+ground if i['typeid']=='9mm')==50)
    for uid in ['external-ground-pack','external-nested-rock','external-owned-bottle','external-owned-bat','external-sealed-rock']:
        check('canonical_identity_once_'+uid,sum(i.get('item_vars',{}).get('uid')==uid for i in owned+ground)==1)
    if args.feedback:
        ground_tile=next(t for t in native['ground_items'] if isinstance(t,dict) and 'position' in t) if False else None
        check('canonical_external_drag_conserves_total_charges',sum(i.get('charges',0) for i in ground if i['typeid']=='9mm')==28)
    check('canonical_owned_ammo_twenty_two' ,sum(i.get('charges',0) for i in owned if i['typeid']=='9mm')==22)
    pack=next(i for i in ground if i.get('item_vars',{}).get('uid')=='external-ground-pack')
    check('canonical_external_pack_keeps_two_rounds',sum(i.get('charges',0) for i in items(pack) if i['typeid']=='9mm')==2)
    check('canonical_nested_rock_is_owned',any(i.get('item_vars',{}).get('uid')=='external-nested-rock' for i in owned))
    check('canonical_position_unchanged',native['player_abs']==[60,60,0])
    (out/'summary.json').write_text(json.dumps(dict(checks=checks,native_save=str(output)),indent=2)+'\n')

if __name__=='__main__':main()
