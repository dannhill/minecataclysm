#!/usr/bin/env python3
"""Exercise real Luanti input/camera with isolated, controlled CWM responses.

CDDA semantics are checked separately by the native [cwm] tests. This fixture
checks frame-rate independence, rejected actions, delayed results, release,
stationary camera stability and actual rendering from either side of a window.
"""
import argparse
import csv
import json
import math
import os
from pathlib import Path
import socket
import struct
import statistics
import subprocess
import sys
import tempfile
import threading
import time


def run(ws, out, fps, delayed=False, rebases=False, threats=False):
    link = ws / "luanti/games/cdda_voxel"
    if not link.exists():
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(ws / "game", target_is_directory=True)
    sys.path.insert(0, str(ws / "protocol/python"))
    import flatbuffers
    from CDDA.CWM import CwmMessage as Msg, Payload, HelloResponse as Hello
    from CDDA.CWM import WorldSnapshot as World, ChunkSnapshot as Chunk, CwmBlock as Block
    from CDDA.CWM import EntityState as Entity, Vec3f, Coord3i, CommandAck as Ack, MoveRequest as Move
    from CDDA.CWM import TileDelta as Tile
    from CDDA.CWM import DecisionPrompt as Prompt, DecisionResponse as Response

    sequence = 0
    player = [8, 24]
    events = []
    error = []
    stop = threading.Event()
    synchronized = threading.Event()
    geometry = threading.Event()
    outside = threading.Event()
    window_open = threading.Event()
    force_rebase = threading.Event()
    origin_offset = [0, 0]
    creature_mode = [0]
    prompt_requested = threading.Event()

    def envelope(b, kind, value):
        nonlocal sequence
        sequence += 1
        Msg.CwmMessageStart(b)
        Msg.CwmMessageAddSequenceNumber(b, sequence)
        Msg.CwmMessageAddWorldRevision(b, sequence)
        Msg.CwmMessageAddPayloadType(b, kind)
        Msg.CwmMessageAddPayload(b, value)
        b.Finish(Msg.CwmMessageEnd(b))
        return bytes(b.Output())

    def hello():
        b = flatbuffers.Builder(128)
        Hello.HelloResponseStart(b)
        Hello.HelloResponseAddAccepted(b, True)
        return envelope(b, Payload.Payload.HelloResponse, Hello.HelloResponseEnd(b))

    def ack(command, accepted):
        b = flatbuffers.Builder(128)
        Ack.CommandAckStart(b)
        Ack.CommandAckAddCommandId(b, command)
        Ack.CommandAckAddAccepted(b, accepted)
        return envelope(b, Payload.Payload.CommandAck, Ack.CommandAckEnd(b))

    def prompt(decision_id=77):
        b = flatbuffers.Builder(256)
        text = b.CreateString('Native decision fixture: choose Keep world.')
        options = [b.CreateString(s) for s in ('Reset world', 'Delete world', 'Keep world')]
        Prompt.DecisionPromptStartChoicesVector(b, len(options))
        for option in reversed(options): b.PrependUOffsetTRelative(option)
        choices = b.EndVector()
        Prompt.DecisionPromptStart(b)
        Prompt.DecisionPromptAddDecisionId(b, decision_id)
        Prompt.DecisionPromptAddText(b, text)
        Prompt.DecisionPromptAddChoices(b, choices)
        return envelope(b, Payload.Payload.DecisionPrompt, Prompt.DecisionPromptEnd(b))

    def snapshot(full=False, window_delta=False):
        b = flatbuffers.Builder(32768)
        offsets = []
        if full:
            for cy in range(4 if rebases else 2):
                for cx in range(4 if rebases else 2):
                    Chunk.ChunkSnapshotStartBlocksVector(b, 256)
                    for i in range(255, -1, -1):
                        x, y = cx * 16 + i % 16 + origin_offset[0], cy * 16 + i // 16 + origin_offset[1]
                        material, flags, orientation = 4, 0, 0
                        if x in (0, 31) or y in (0, 31): material, flags = 3, 2
                        if geometry.is_set():
                            if y == 16: material, flags = 3, 2
                            if (x, y) == (8, 16): material, flags = (10, 0) if window_open.is_set() else (7, 2)
                            if (x, y) == (6, 16): material, flags = 11, 2
                            if (x, y) == (10, 16): material, flags = 5, 3
                            if (x, y) == (6, 18): flags = 14  # blocking tall furniture, with floor
                            if (x, y) == (10, 18): material, flags = 12, 2
                        Block.CreateCwmBlock(b, flags, material, 15, orientation)
                    blocks = b.EndVector()
                    Chunk.ChunkSnapshotStart(b)
                    Chunk.ChunkSnapshotAddChunkX(b, cx)
                    Chunk.ChunkSnapshotAddChunkY(b, cy)
                    Chunk.ChunkSnapshotAddChunkZ(b, 0)
                    Chunk.ChunkSnapshotAddSizeX(b, 16)
                    Chunk.ChunkSnapshotAddSizeY(b, 16)
                    Chunk.ChunkSnapshotAddSizeZ(b, 1)
                    Chunk.ChunkSnapshotAddBlocks(b, blocks)
                    offsets.append(Chunk.ChunkSnapshotEnd(b))
            World.WorldSnapshotStartChunksVector(b, len(offsets))
            for offset in reversed(offsets): b.PrependUOffsetTRelative(offset)
            chunks = b.EndVector()
        else: chunks = 0
        Entity.EntityStateStart(b)
        Entity.EntityStateAddId(b, 1)
        Entity.EntityStateAddPos(b, Vec3f.CreateVec3f(b, player[0]-origin_offset[0], player[1]-origin_offset[1], 0))
        entity = Entity.EntityStateEnd(b)
        actors = [entity]
        if creature_mode[0] in (1,2,3):
            for eid, kind, typename, x in [(1000,2,'mon_zombie',8), (1001,2,'mon_dog',10), (1002,1,'npc',6)]:
                type_id = b.CreateString(typename)
                Entity.EntityStateStart(b)
                Entity.EntityStateAddId(b,eid)
                Entity.EntityStateAddType(b,kind)
                Entity.EntityStateAddTypeId(b,type_id)
                Entity.EntityStateAddPerceived(b,creature_mode[0] != 2)
                Entity.EntityStateAddPos(b,Vec3f.CreateVec3f(b,x,player[1]-4,0))
                actors.append(Entity.EntityStateEnd(b))
        World.WorldSnapshotStartEntitiesVector(b, len(actors))
        for actor in reversed(actors): b.PrependUOffsetTRelative(actor)
        entities = b.EndVector()
        tiles = 0
        if window_delta:
            Tile.TileDeltaStart(b)
            Tile.TileDeltaAddCoord(b, Coord3i.CreateCoord3i(b, 8, 16, 0))
            Tile.TileDeltaAddBlock(b, Block.CreateCwmBlock(b, 0, 10, 15, 0))
            delta = Tile.TileDeltaEnd(b)
            World.WorldSnapshotStartTilesVector(b, 1)
            b.PrependUOffsetTRelative(delta)
            tiles = b.EndVector()
        World.WorldSnapshotStart(b)
        World.WorldSnapshotAddEntities(b, entities)
        World.WorldSnapshotAddChunks(b, chunks)
        World.WorldSnapshotAddTiles(b, tiles)
        World.WorldSnapshotAddOrigin(b, Coord3i.CreateCoord3i(b, 84000+origin_offset[0], -42000+origin_offset[1], -1))
        return envelope(b, Payload.Payload.WorldSnapshot, World.WorldSnapshotEnd(b))

    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="cwm-pacing-") as temp:
        scratch = Path(temp)
        path = scratch / "cwm.sock"
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(str(path)); server.listen(1); server.settimeout(.2)

        def serve():
            try:
                connection = None
                while not stop.is_set() and connection is None:
                    try: connection, _ = server.accept()
                    except socket.timeout: pass
                if connection is None: return
                with connection:
                    connection.settimeout(.01)
                    def send(body): connection.sendall(struct.pack(">I", len(body)) + body)
                    buffer = b""
                    pending = None
                    geometry_sent = outside_sent = opened_sent = False
                    last_creatures = 0
                    prompt_sent = False
                    while not stop.is_set():
                        now = time.monotonic()
                        if pending and now >= pending[0]:
                            _, command, accepted, full = pending
                            if accepted: player[1] -= 1
                            send(snapshot(full))
                            events.append({"kind": "result", "command": command, "time": now, "player": player[:]})
                            pending = None
                        if geometry.is_set() and not geometry_sent:
                            player[:] = [8, 20]; send(snapshot(True)); geometry_sent = True
                        if outside.is_set() and not outside_sent:
                            player[:] = [8, 12]; send(snapshot()); outside_sent = True
                        if window_open.is_set() and not opened_sent:
                            send(snapshot(window_delta=True)); opened_sent = True
                            events.append({"kind": "window_delta", "tiles": 1, "chunks": 0, "time": now})
                        if force_rebase.is_set():
                            force_rebase.clear()
                            origin_offset[1] = 0
                            send(snapshot(True))
                            events.append({"kind": "stationary_rebase", "time": now})
                        if creature_mode[0] != last_creatures:
                            last_creatures = creature_mode[0]
                            send(snapshot())
                        if prompt_requested.is_set() and not prompt_sent:
                            send(prompt()); prompt_sent = True
                        try: data = connection.recv(65536)
                        except socket.timeout: continue
                        if not data: break
                        buffer += data
                        while len(buffer) >= 4:
                            size = struct.unpack(">I", buffer[:4])[0]
                            if len(buffer) < size + 4: break
                            msg = Msg.CwmMessage.GetRootAsCwmMessage(buffer[4:size+4], 0)
                            buffer = buffer[size+4:]
                            if msg.PayloadType() == Payload.Payload.HelloRequest:
                                send(hello()); send(snapshot(True)); synchronized.set()
                            elif msg.PayloadType() == Payload.Payload.MoveRequest:
                                req = Move.MoveRequest(); req.Init(msg.Payload().Bytes, msg.Payload().Pos)
                                n = sum(e["kind"] == "request" for e in events) + 1
                                accepted = n != 6  # reject one action, keep the camera still
                                events.append({"kind": "request", "command": req.CommandId(), "time": time.monotonic(),
                                               "overlap": pending is not None, "accepted": accepted})
                                send(ack(req.CommandId(), accepted))
                                full = rebases and n in (5, 10)
                                if full:
                                    origin_offset[1] = -12 if n == 5 else -24
                                    events.append({"kind": "moving_rebase", "time": time.monotonic()})
                                pending = (time.monotonic() + (.12 if full else .65 if delayed and n == 3 else .01), req.CommandId(), accepted, full)
                            elif msg.PayloadType() == Payload.Payload.DecisionResponse:
                                response = Response.DecisionResponse()
                                response.Init(msg.Payload().Bytes,msg.Payload().Pos)
                                events.append({'kind':'decision','id':response.DecisionId(),'choice':response.Choice()})
                                if response.DecisionId()==77: send(prompt(78))
            except (OSError, ValueError) as exc:
                if not stop.is_set(): error.append(repr(exc))

        thread = threading.Thread(target=serve, daemon=True); thread.start()
        world = scratch / "world"; world.mkdir()
        (world / "world.mt").write_text("gameid = cdda_voxel\nbackend = sqlite3\nplayer_backend = sqlite3\nauth_backend = sqlite3\n")
        config = scratch / "client.conf"
        config.write_text(f"fullscreen = false\nscreen_w = 1024\nscreen_h = 768\nfps_max = {fps}\n"
                          f"fps_max_unfocused = {fps}\nvsync = false\nenable_damage = false\n"
                          f"enable_update_checker = false\ndebug_log_level = info\nmouse_sensitivity = 0.2\n"
                          f"cwm_socket_path = {path}\ncwm_trace_file = {out / 'camera.csv'}\n"
                          "bind_address = 127.0.0.1\nanticheat_flags = digging,interaction\n")
        old_window = subprocess.run(["xdotool", "getactivewindow"], capture_output=True, text=True).stdout.strip()
        with (out / "console.log").open("w") as log:
            proc = subprocess.Popen([str(ws / "luanti/bin/luanti"), "--go", "--world", str(world),
                                     "--gameid", "cdda_voxel", "--config", str(config), "--name", "regression",
                                     "--logfile", str(out / "engine.log")], cwd=ws / "luanti", stdout=log,
                                    stderr=subprocess.STDOUT, start_new_session=True)
            window = None
            try:
                deadline = time.monotonic() + 30
                while time.monotonic() < deadline and proc.poll() is None:
                    found = subprocess.run(["xdotool", "search", "--onlyvisible", "--pid", str(proc.pid)], capture_output=True, text=True)
                    if found.stdout.strip(): window = found.stdout.strip().splitlines()[0]
                    if window and synchronized.is_set(): break
                    time.sleep(.1)
                if not window or not synchronized.is_set(): raise RuntimeError("Luanti fixture did not initialize")
                def xdo(*args): subprocess.run(["xdotool", *args], check=True, timeout=5, capture_output=True)
                def screenshot(name): subprocess.run(["import", "-window", window, str(out / name)], check=True, timeout=10)
                xdo("windowactivate", "--sync", window)
                time.sleep(2)
                stationary_start = time.monotonic()
                time.sleep(.7)
                stationary_end = time.monotonic()
                press = time.monotonic(); xdo("keydown", "--window", window, "w")
                time.sleep(3.2)
                xdo("keyup", "--window", window, "w"); release = time.monotonic()
                time.sleep(1)
                stopped = time.monotonic(); time.sleep(.7); stopped_end = time.monotonic()
                if rebases:
                    screenshot('rebase-before.png')
                    rebase_start = time.monotonic()
                    force_rebase.set(); time.sleep(1.0)
                    rebase_end = time.monotonic()
                    screenshot('rebase-after.png')
                if threats:
                    creature_mode[0] = 1; time.sleep(1); screenshot('creatures-visible.png')
                    creature_mode[0] = 2; time.sleep(.5); screenshot('creatures-unperceived.png')
                    creature_mode[0] = 3; time.sleep(.5); screenshot('creatures-restored.png')
                    creature_mode[0] = 4; time.sleep(.5); screenshot('creatures-removed.png')
                    prompt_requested.set(); time.sleep(.5); screenshot('native-decision.png')
                    xdo('keydown','--window',window,'w'); time.sleep(.4)
                    xdo('keyup','--window',window,'w')
                    xdo('keydown','--window',window,'3'); time.sleep(.5)
                    held_decision_count = sum(e['kind']=='decision' for e in events)
                    xdo('keyup','--window',window,'3'); time.sleep(.1)
                    xdo('key','--window',window,'3'); time.sleep(.5)
                if fps == 60 and not delayed and not rebases and not threats:
                    geometry.set(); time.sleep(2)
                    screenshot("window-inside.png")
                    screenshot("window-inside-later.png")
                    outside.set(); time.sleep(.5)
                    # 0.2 degrees/pixel. Use small relative increments so the
                    # cursor warp cannot clip a long motion at the X11 edge.
                    for _ in range(10): xdo("mousemove_relative", "--", "90", "0"); time.sleep(.05)
                    time.sleep(.5); screenshot("window-outside.png")
                    directions = list(csv.DictReader((out / "camera.csv").open()))
                    camera_turned = bool(directions) and float(directions[-1]["dir_z"]) < -.9
                    window_open.set(); time.sleep(2); screenshot("window-open.png")
            finally:
                if window: subprocess.run(["xdotool", "keyup", "--window", window, "w"], capture_output=True)
                if proc.poll() is None:
                    proc.terminate()
                    try: proc.wait(timeout=10)
                    except subprocess.TimeoutExpired: proc.kill(); proc.wait()
                stop.set(); server.close(); thread.join(timeout=2)
                if old_window: subprocess.run(["xdotool", "windowactivate", old_window], capture_output=True)

    rows = list(csv.DictReader((out / "camera.csv").open()))
    for row in rows:
        for key in row: row[key] = float(row[key])
    requests = [e for e in events if e["kind"] == "request"]
    intervals = [b["time"]-a["time"] for a, b in zip(requests, requests[1:])]
    def span(start, end, axis):
        values = [r[axis] for r in rows if start < r["time_ns"]/1e9 < end]
        return max(values)-min(values) if values else math.inf
    idle_span = max(span(stationary_start, stationary_end, axis) for axis in ("camera_x", "camera_y", "camera_z"))
    stopped_span = max(span(stopped, stopped_end, axis) for axis in ("camera_x", "camera_y", "camera_z"))
    movement_rows = [r for r in rows if press+.1 < r["time_ns"]/1e9 < release]
    backwards = sum(b["camera_z"] < a["camera_z"]-.001 for a, b in zip(movement_rows, movement_rows[1:]))
    vertical_span = max(r["camera_y"] for r in movement_rows)-min(r["camera_y"] for r in movement_rows)
    checks = {
        "runtime_clean_exit": proc.returncode == 0,
        "no_server_error": not error,
        "no_outstanding_command_overlap": not any(e["overlap"] for e in requests),
        "no_catchup_bursts": bool(intervals) and min(intervals) >= .18,
        "held_key_rate": 13 <= len(requests) <= 17 if delayed else 15 <= len(requests) <= 17,
        "no_commands_after_release": not any(e["time"] > release+.08 for e in requests),
        "stationary_camera_stable": idle_span < .001,
        "released_camera_stable": stopped_span < .001,
        "camera_never_reverses": backwards == 0,
        "camera_height_stable": vertical_span < .001,
        "rejected_action_exercised": any(not e["accepted"] for e in requests),
    }
    if rebases:
        checks['two_moving_bubble_rebases_exercised'] = sum(e['kind'] == 'moving_rebase' for e in events) == 2
        checks['stationary_bubble_rebase_does_not_move_camera'] = max(span(rebase_start, rebase_end, axis) for axis in ('camera_x','camera_y','camera_z')) < .001
        checks['moving_bubble_rebase_has_no_camera_teleport'] = all(abs(b['camera_z']-a['camera_z']) < 5 for a,b in zip(movement_rows,movement_rows[1:]))
        before,after = [subprocess.check_output(['convert',str(out/s),'-crop','400x160+300+500','+repage','-depth','8','RGB:-']) for s in ('rebase-before.png','rebase-after.png')]
        checks['stationary_rebase_preserves_visible_terrain'] = sum(abs(a-b)>5 for a,b in zip(before,after)) < 60
    if threats:
        def body_pixels(name):
            return subprocess.check_output(['convert',str(out/name),'-crop','500x180+260+480','+repage','-depth','8','RGB:-'])
        on,off,restored,removed = [body_pixels(s) for s in ('creatures-visible.png','creatures-unperceived.png','creatures-restored.png','creatures-removed.png')]
        def changed(a,b): return sum(max(abs(x-y) for x,y in zip(a[i:i+3],b[i:i+3])) > 25 for i in range(0,len(a),3))
        console = (out/'console.log').read_text() + (out/'engine.log').read_text()
        checks['zombie_npc_and_generic_creature_models_created'] = all('Visual creature '+str(i) in console for i in (1000,1001,1002))
        checks['perceived_creatures_are_rendered'] = changed(on,off) > 300
        checks['perception_loss_hides_creatures_and_recovery_restores_them'] = changed(restored,off) > 300 and changed(on,restored) < 100
        checks['removed_creatures_leave_no_ghost_models'] = changed(off,removed) < 100
        checks['native_decision_number_reaches_authority'] = any(e['kind']=='decision' and e['id']==77 and e['choice']==2 for e in events)
        checks['held_number_does_not_answer_a_following_decision'] = held_decision_count==1 and sum(e['kind']=='decision' and e['id']==78 for e in events)==1
        checks['no_missing_creature_assets'] = 'Mesh not found:' not in console
    if fps == 60 and not delayed and not rebases and not threats:
        checks["mouse_look_and_opposite_side_exercised"] = camera_turned
        def crop(name):
            # Exclude sky/clouds; the frame texture is off-white, not pure white.
            return subprocess.check_output(["convert", str(out/name), "-crop", "400x210+300+340",
                                            "+repage", "-depth", "8", "RGB:-"])
        inside, exterior, opened = [crop(name) for name in ["window-inside.png", "window-outside.png", "window-open.png"]]
        def white_pixels(data):
            return sum(min(data[i:i+3]) > 200 for i in range(0, len(data), 3))
        checks["glass_frame_visible_on_both_sides"] = min(white_pixels(inside), white_pixels(exterior)) > 40
        checks["open_window_removes_glass"] = white_pixels(exterior) > white_pixels(opened) + 40
        checks["batched_tile_update_without_full_resend"] = any(e["kind"] == "window_delta" for e in events)
    frame_seconds = [(b["time_ns"]-a["time_ns"])/1e9 for a, b in zip(rows, rows[1:])]
    result = {"fps_limit": fps, "delayed_result": delayed, "checks": checks,
              "requests": len(requests), "intervals_seconds": intervals, "stationary_span": idle_span,
              "stopped_span": stopped_span, "vertical_span": vertical_span, "backwards_frames": backwards,
              "frames": len(rows), "measured_median_fps": 1/statistics.median(frame_seconds),
              "server_errors": error, "limitations": "Synthetic CWM authority; native CDDA semantics tested separately. FPS setting is a limit, not guaranteed achieved throughput."}
    (out / "events.json").write_text(json.dumps(events, indent=2)+"\n")
    (out / "result.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result), flush=True)
    return all(checks.values())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--rebase-only", action='store_true')
    parser.add_argument("--threats-only", action='store_true')
    args = parser.parse_args()
    if args.rebase_only:
        sys.exit(0 if run(args.workspace.resolve(), args.artifacts.resolve(), 60, rebases=True) else 1)
    if args.threats_only:
        sys.exit(0 if run(args.workspace.resolve(), args.artifacts.resolve(), 60, threats=True) else 1)
    outcomes = [run(args.workspace.resolve(), args.artifacts.resolve()/f"fps-{fps}", fps) for fps in (30, 60, 120)]
    outcomes.append(run(args.workspace.resolve(), args.artifacts.resolve()/"delayed", 60, True))
    sys.exit(0 if all(outcomes) else 1)
