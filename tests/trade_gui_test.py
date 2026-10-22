#!/usr/bin/env python3
"""Exercise native NPC trading in the actual Luanti renderer.

Requires an independently created --create-trade fixture, X11, xdotool,
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
import queue
import struct


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('workspace', 'fixture', 'native-reader', 'artifacts'):
        parser.add_argument('--' + name, type=Path, required=True)
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
            def talk():
                turn(0,-9)
                wait(lambda r: int(r['combat_hover'])>>63==1)
                xdo('click','3')
                wait(lambda r:int(r['pending_decision'])>0)
                return prompt()
            def choose(n):
                old=latest()['pending_decision'];tap(str(n+1))
                wait(lambda r:r['pending_decision']!=old)
            def leave():
                tap('Escape')
                wait(lambda r:int(r['pending_decision'])==0 and int(r['pending_move'])==0)

            from CDDA.CWM.TradeView import TradeView
            from CDDA.CWM.TradeClosed import TradeClosed
            from CDDA.CWM.CommandAck import CommandAck
            from formspec_geometry import geometry
            def trade_view():
                msg=messages(Payload.TradeView)[-1];v=TradeView();v.Init(msg.Payload().Bytes,msg.Payload().Pos);return v
            def wait_wire(kind,count,timeout=12):
                deadline=time.monotonic()+timeout
                while time.monotonic()<deadline:
                    if len(messages(kind))>count:return
                    if proc.poll() is not None:break
                    time.sleep(.05)
                raise RuntimeError('Wire packet not reached: '+str(kind))
            def open_trade():
                p=talk()
                while True:
                    choices=labels(p);n=next((n for n,t in enumerate(choices) if 'trade' in t.lower()),None)
                    if n is not None:break
                    if 'Next page' not in choices:raise AssertionError('No trade choice')
                    choose(choices.index('Next page'));p=prompt()
                count=len(messages(Payload.TradeView));tap(str(n+1));wait_wire(Payload.TradeView,count)
                wait(lambda r:int(r['pending_decision'])==0);time.sleep(.5)
                shot('trade-open.png')
                return trade_view()
            def click(x,y):
                ox,oy,unit=geometry(out/'trade-open.png',width=22,height=12)
                xdo('mousemove','--window',window,str(round(ox+x*unit)),str(round(oy+y*unit)));xdo('click','1');time.sleep(.25)
            def entry(v,itype,trader,skip=0):
                found=[v.Entries(n) for n in range(v.EntriesLength()) if v.Entries(n).TypeId()==itype.encode() and v.Entries(n).Trader()==trader]
                return found[skip]
            def select_item(v,e,shift=False):
                entries=[v.Entries(n) for n in range(v.EntriesLength()) if v.Entries(n).Trader()==e.Trader()]
                n=next(n for n,r in enumerate(entries) if r.Id()==e.Id())
                if n>=27:raise AssertionError('Fixture entry outside first page')
                x=.5 if e.Trader() else 11.5
                if shift:xdo('keydown','Shift_L')
                click(x+(n%9)*1.12+.5,2.2+(n//9)*1.15+.5)
                if shift:xdo('keyup','Shift_L')
            def offer(v,e,quantity,drag=False):
                select_item(v,e);click(12.2,8.65)
                xdo('key','--clearmodifiers','ctrl+a');xdo('type','--clearmodifiers',str(quantity));time.sleep(.15)
                count=len(messages(Payload.TradeView))
                if drag:
                    entries=[v.Entries(n) for n in range(v.EntriesLength()) if v.Entries(n).Trader()==e.Trader()]
                    n=next(n for n,r in enumerate(entries) if r.Id()==e.Id())
                    ox,oy,unit=geometry(out/'trade-open.png',width=22,height=12);x=.5 if e.Trader() else 11.5
                    xdo('mousemove','--window',window,str(round(ox+(x+(n%9)*1.12+.5)*unit)),str(round(oy+(2.2+(n//9)*1.15+.5)*unit)))
                    xdo('mousedown','1');time.sleep(.15)
                    xdo('mousemove','--window',window,str(round(ox+(16.5 if e.Trader() else 5.5)*unit)),str(round(oy+6.05*unit)));time.sleep(.25);xdo('mouseup','1')
                else:click(17,8.65)
                wait_wire(Payload.TradeView,count);return trade_view()
            def settle():
                time.sleep(.3)
                if int(latest()['pending_decision']):tap('Escape')
                wait(lambda r:int(r['pending_decision'])==0 and int(r['pending_move'])==0 and int(r['pause_reasons'])==0)
            v=open_trade();npc=v.NpcId()
            check('native_two_panel_quote',v.TradeId()>0 and v.QuoteId()>0 and npc>>63==1 and v.EntriesLength()>0)
            frozen=latest()['simulation_time'];time.sleep(.7)
            check('native_clock_paused_during_quote',latest()['simulation_time']==frozen and int(latest()['pause_reasons'])&16)
            bandage=entry(v,'bandages',True)
            for expected in (1,0):
                count=len(messages(Payload.TradeView));select_item(v,bandage,shift=True);wait_wire(Payload.TradeView,count);v=trade_view()
                check('shift_click_toggles_offer_'+str(expected),v.Entries(bandage.Id()-1).Selected()==expected and latest()['simulation_time']==frozen)
            v=offer(v,bandage,1)
            check('proposal_updates_native_quote_without_running_clock',v.TheirValue()>0 and latest()['simulation_time']==frozen and v.Entries(bandage.Id()-1).Selected()==1)
            check('native_price_and_balance_exported',v.Balance()==100000-v.TheirValue() and v.RememberedBalance()==v.Balance() and v.CanConfirm())
            # Send invalid proposals through the same byte relay/session.
            # They are protocol probes, not alternate gameplay simulation.
            def invalid_offer(quantity,quote):
                import flatbuffers,struct
                from CDDA.CWM import TradeOfferRequest as O,CwmMessage as E
                b=flatbuffers.Builder(256);O.Start(b);O.AddRequestId(b,900000);O.AddTradeId(b,v.TradeId());O.AddQuoteId(b,quote);O.AddEntryId(b,bandage.Id());O.AddQuantity(b,quantity);payload=O.End(b)
                E.Start(b);E.AddSequenceNumber(b,1);E.AddWorldRevision(b,int(latest()['revision']));E.AddPayloadType(b,Payload.TradeOfferRequest);E.AddPayload(b,payload);E.AddSessionId(b,int(latest()['session_id']));E.AddPlayerId(b,int(latest()['player_id']));E.AddConnectionId(b,int(latest()['connection_id']));b.Finish(E.End(b))
                count=len(messages(Payload.TradeView));data=bytes(b.Output());injections.put(struct.pack('>I',len(data))+data);wait_wire(Payload.TradeView,count)
                return trade_view()
            rejected=invalid_offer(bandage.Available()+1,v.QuoteId())
            check('excess_quantity_rejects_without_editing_offer',rejected.QuoteId()==v.QuoteId() and rejected.Entries(bandage.Id()-1).Selected()==1 and bool(rejected.Error()))
            rejected=invalid_offer(0,v.QuoteId()-1)
            check('stale_quote_rejects_without_editing_offer',rejected.QuoteId()==v.QuoteId() and rejected.Entries(bandage.Id()-1).Selected()==1 and bool(rejected.Error()))
            count=len(messages(Payload.TradeClosed));click(2.5,11.4);wait_wire(Payload.TradeClosed,count);settle()
            check('cancel_offer_returns_to_game_without_confirmation',proc.poll() is None)
            v=open_trade();bandage=entry(v,'bandages',True)
            check('cancel_preserves_stock_and_credit',bandage.Available()==1 and bandage.Selected()==0 and v.Balance()==100000)
            v=offer(v,bandage,1)
            count=len(messages(Payload.DecisionPrompt));click(19.5,11.4);wait_wire(Payload.DecisionPrompt,count)
            p=prompt();check('whole_offer_has_native_confirmation',p.Conversation() is None and p.ChoicesLength()==2)
            shot('native-trade-confirm.png');tap(str(p.CancelChoice()+1));wait(lambda r:int(r['pending_decision'])==0);time.sleep(.5)
            check('decline_keeps_offer_editable',trade_view().TradeId()==v.TradeId())
            shot('trade-declined.png')
            # Offer five charges from the second same-type stack, using actual
            # drag across panels. It must not consume the first stack.
            v=trade_view();ammo=entry(v,'9mm',False,1);selected_available=ammo.Available()
            check('same_type_charge_stacks_are_distinct',selected_available==30 and entry(v,'9mm',False,0).Available()==20)
            v=offer(v,ammo,5,drag=True)
            check('drag_sets_partial_native_offer',v.Entries(ammo.Id()-1).Selected()==5 and v.YourValue()>0)
            expected_owed=v.RememberedBalance();expected_sold=v.YourValue()
            check('bilateral_balance_comes_from_native_prices',v.Balance()==100000+v.YourValue()-v.TheirValue())
            shot('bilateral-offer.png')
            count=len(messages(Payload.DecisionPrompt));closed=len(messages(Payload.TradeClosed));click(19.5,11.4);wait_wire(Payload.DecisionPrompt,count)
            tap('1');wait_wire(Payload.TradeClosed,closed);settle()
            commits=messages(Payload.TradeCommitRequest,'client');commit=commits[-1]
            from CDDA.CWM.TradeCommitRequest import TradeCommitRequest
            c=TradeCommitRequest();c.Init(commit.Payload().Bytes,commit.Payload().Pos);command=c.CommandId()
            def matching_acks():
                found=[]
                for msg in messages(Payload.CommandAck):
                    a=CommandAck();a.Init(msg.Payload().Bytes,msg.Payload().Pos)
                    if a.CommandId()==command:found.append(a)
                return found
            check('commit_acknowledged_after_native_transfer',matching_acks() and matching_acks()[-1].Accepted())
            # Replay exactly the accepted command on the same connection.
            before=len(matching_acks());payload=bytes(commit._tab.Bytes);injections.put(struct.pack('>I',len(payload))+payload)
            deadline=time.monotonic()+8
            while len(matching_acks())<=before and time.monotonic()<deadline:time.sleep(.05)
            check('replayed_commit_returns_cached_ack',len(matching_acks())>before and matching_acks()[-1].Accepted())
            v=open_trade()
            check('accepted_exchange_removed_stock_once',not any(v.Entries(n).TypeId()==b'bandages' and v.Entries(n).Trader() for n in range(v.EntriesLength())))
            check('accepted_exchange_keeps_exact_source_remainder',entry(v,'9mm',False,0).Available()==20 and entry(v,'9mm',False,1).Available()==25)
            check('native_credit_updated_once',v.Balance()==expected_owed)
            connection=latest()['connection_id'];sent=len(messages(Payload.TradeCommitRequest,'client'));drop.set()
            wait(lambda r:r['connection_id']!=connection and int(r['input_ready'])==1 and int(r['pending_decision'])==0 and int(r['pending_move'])==0,timeout=25)
            check('reconnect_cancels_quote_without_replaying_commit',len(messages(Payload.TradeCommitRequest,'client'))==sent)
            check('replacement_connection_never_inherits_old_quote',not any(m.ConnectionId()==int(latest()['connection_id']) for m in messages(Payload.TradeView)))
            shot('trade-recovery-before-input.png')
            try:
                geometry(out/'trade-recovery-before-input.png',width=22,height=12)
                stale_modal=True
            except AssertionError:
                stale_modal=False
            check('reconnect_dismisses_modal_before_any_input',not stale_modal)
            tap('i');wait(lambda r:int(r['equipment_form'])==1)
            check('reconnect_closes_old_trade_and_allows_inventory',int(latest()['equipment_form'])==1)
            tap('Escape');wait(lambda r:int(r['equipment_form'])==0 and int(r['pause_reasons'])==0)
            check('recovered_inventory_returns_to_live_controls',int(latest()['input_ready'])==1)
            shot('trade-reconnected.png')
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

    check('byte_relay_completed_without_errors',not relay_errors)
    logs='\n'.join(p.read_text(errors='replace') for p in (out/'logs').rglob('*.log'))
    check('native_trade_widgets_accepted_by_actual_parser','Invalid scrollbar element' not in logs and 'Invalid formspec' not in logs and 'Unknown DrawSpec: type=cwm_' not in logs)
    output=out/'native.json'
    with (out/'native.log').open('w') as log:
        result=subprocess.run([str(args.native_reader.resolve()),'--userdir',str(user),'--datadir',str(ws/'cdda/data'),'--output',str(output)],stdout=log,stderr=subprocess.STDOUT,timeout=180)
    check('trade_save_readable_by_independent_pinned_core',result.returncode==0)
    native=json.loads(output.read_text());player=native['player'];np=[n for n in native['npcs'] if n.get('name')=='Conversation NPC']
    def flatten(value):
        if isinstance(value,dict):
            yield value
            for v in value.values():yield from flatten(v)
        elif isinstance(value,list):
            for v in value:yield from flatten(v)
    def tagged(value,uid):return [i for i in flatten(value) if i.get('item_vars',{}).get('uid')==uid]
    check('canonical_npc_survives',len(np)==1 and np[0]['id']==(npc&((1<<63)-1)))
    check('canonical_debt_and_sold_once',np[0]['op_of_u']['owed']==expected_owed and np[0]['op_of_u']['sold']==expected_sold)
    first=tagged(player,'trade-player-ammo-a');second=tagged(player,'trade-player-ammo-b');sold=tagged(np,'trade-player-ammo-b');bought=tagged(player,'trade-npc-bandage')
    check('canonical_first_same_type_stack_untouched',len(first)==1 and first[0]['charges']==20)
    check('canonical_selected_stack_partial_sale',len(second)==1 and second[0]['charges']==25 and len(sold)==1 and sold[0]['charges']==5)
    check('canonical_bandage_moves_once',len(bought)==1 and not tagged(np,'trade-npc-bandage'))
    check('canonical_owners_follow_exchange',bought[0].get('owner')==second[0].get('owner') and sold[0].get('owner')!=second[0].get('owner'))
    check('canonical_position_unchanged',native['player_abs']==[60,60,0])
    check('no_fake_activity_or_inventory',player['activity']['type']=='ACT_NULL' and not any('luanti' in k.lower() for k in player))
    (out/'summary.json').write_text(json.dumps({'checks':checks,'native_save':str(output),'expected_owed':expected_owed,'expected_sold':expected_sold},indent=2)+'\n')

if __name__=='__main__':main()
