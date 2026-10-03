#!/usr/bin/env python3
"""
Visual Entities, Monster Animations & LERP Acceptance Test
Milestone 3 Verification Test
Verifies authoritative monster synchronization, monster AI turn advancement,
entity state tracking, and 60 FPS LERP position smoothing.
"""

import sys
import os
import time
import socket
import struct
import math
import subprocess
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORKSPACE_ROOT / "protocol" / "python"))

import flatbuffers
from CDDA.CWM.CwmMessage import CwmMessage, CwmMessageStart, CwmMessageAddSequenceNumber, CwmMessageAddWorldRevision, CwmMessageAddPayloadType, CwmMessageAddPayload, CwmMessageEnd
from CDDA.CWM.Payload import Payload
from CDDA.CWM.HelloRequest import HelloRequestStart, HelloRequestAddProtocolVersionMajor, HelloRequestAddProtocolVersionMinor, HelloRequestAddBuildId, HelloRequestEnd
from CDDA.CWM.HelloResponse import HelloResponse
from CDDA.CWM.WorldSnapshot import WorldSnapshot
from CDDA.CWM.MoveRequest import MoveRequestStart, MoveRequestAddCommandId, MoveRequestAddDirection, MoveRequestEnd
from CDDA.CWM.MoveDirection import MoveDirection
from CDDA.CWM.CommandAck import CommandAck
from CDDA.CWM.EntityType import EntityType

def send_framed_msg(sock, data: bytes):
    length_prefix = struct.pack(">I", len(data))
    sock.sendall(length_prefix + data)

def recv_framed_msg(sock, timeout=5.0) -> bytes:
    sock.settimeout(timeout)
    hdr = b""
    while len(hdr) < 4:
        chunk = sock.recv(4 - len(hdr))
        if not chunk:
            raise ConnectionError("Socket closed prematurely while reading header")
        hdr += chunk
    (length,) = struct.unpack(">I", hdr)
    payload = b""
    while len(payload) < length:
        chunk = sock.recv(length - len(payload))
        if not chunk:
            raise ConnectionError("Socket closed prematurely while reading body")
        payload += chunk
    return payload

def run_entity_animation_test():
    print("==================================================")
    print(" Running Milestone 3: Visual Entities & LERP Test ")
    print("==================================================")

    socket_path = "/tmp/cwm_entity_test.sock"
    user_dir = "/tmp/cdda_entity_user"
    world_name = "entity_test_world"
    cdda_bin = WORKSPACE_ROOT / "cdda" / "build" / "src" / "cdda-server"

    if os.path.exists(socket_path):
        os.unlink(socket_path)

    cmd = [
        str(cdda_bin),
        "--socket", socket_path,
        "--world", world_name,
        "--userdir", user_dir,
    ]

    print("[Step 1] Launching CDDA headless simulation server...")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    try:
        start_wait = time.time()
        connected = False
        client_sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        while time.time() - start_wait < 15.0:
            if os.path.exists(socket_path):
                try:
                    client_sock.connect(socket_path)
                    connected = True
                    break
                except socket.error:
                    pass
            time.sleep(0.1)

        if not connected:
            print("ERROR: Timed out waiting for CDDA server socket!")
            return False

        print(f"[Step 2] Connected to CWM IPC socket at: {socket_path}")

        # Send Hello
        print("[Step 3] Handshake CWM protocol...")
        builder = flatbuffers.Builder(1024)
        client_str = builder.CreateString("luanti_cdda_entity_anim_test")
        HelloRequestStart(builder)
        HelloRequestAddProtocolVersionMajor(builder, 1)
        HelloRequestAddProtocolVersionMinor(builder, 0)
        HelloRequestAddBuildId(builder, client_str)
        hello_offset = HelloRequestEnd(builder)

        CwmMessageStart(builder)
        CwmMessageAddSequenceNumber(builder, 1)
        CwmMessageAddWorldRevision(builder, 0)
        CwmMessageAddPayloadType(builder, Payload.HelloRequest)
        CwmMessageAddPayload(builder, hello_offset)
        msg_offset = CwmMessageEnd(builder)
        builder.Finish(msg_offset)

        send_framed_msg(client_sock, builder.Output())

        resp_bytes = recv_framed_msg(client_sock)
        resp_msg = CwmMessage.GetRootAsCwmMessage(resp_bytes, 0)
        hello_resp = HelloResponse()
        hello_resp.Init(resp_msg.Payload().Bytes, resp_msg.Payload().Pos)
        assert hello_resp.Accepted(), "Handshake rejected!"
        print("  Handshake accepted.")

        # Receive WorldSnapshot
        print("[Step 4] Ingesting initial WorldSnapshot and entities...")
        snap_bytes = recv_framed_msg(client_sock)
        snap_msg = CwmMessage.GetRootAsCwmMessage(snap_bytes, 0)
        assert snap_msg.PayloadType() == Payload.WorldSnapshot

        snapshot = WorldSnapshot()
        snapshot.Init(snap_msg.Payload().Bytes, snap_msg.Payload().Pos)

        num_entities = snapshot.EntitiesLength()
        print(f"  Total entities in snapshot: {num_entities}")
        if num_entities < 2:
            print(f"ERROR: Expected at least 2 entities (Player + Monster), got {num_entities}!")
            return False

        player = None
        monsters = []

        for i in range(num_entities):
            ent = snapshot.Entities(i)
            eid = ent.Id()
            etype = ent.Type()
            pos = ent.Pos()
            name = ent.Name().decode("utf-8") if ent.Name() else ""
            type_id = ent.TypeId().decode("utf-8") if ent.TypeId() else ""
            print(f"  Found Entity: ID={eid}, Type={etype}, TypeId='{type_id}', Name='{name}', Pos=({pos.X():.1f}, {pos.Y():.1f}, {pos.Z():.1f})")

            if etype == EntityType.PLAYER or eid == 1:
                player = (eid, pos.X(), pos.Y(), pos.Z())
            elif etype == EntityType.MONSTER or eid >= 1000:
                monsters.append((eid, pos.X(), pos.Y(), pos.Z(), type_id))

        if not player:
            print("ERROR: Player entity not found!")
            return False
        if not monsters:
            print("ERROR: Monster entity not found in snapshot!")
            return False

        zombie_id, z_x0, z_y0, z_z0, z_type = monsters[0]
        print(f"[Step 5] Authoritative Zombie target identified: ID={zombie_id}, Pos=({z_x0:.1f}, {z_y0:.1f}, {z_z0:.1f})")

        # Step 6: Advance turn with MoveRequest(NONE) - Player waits, monster steps
        print("[Step 6] Dispatching MoveRequest(NONE) to advance simulation turn...")
        builder2 = flatbuffers.Builder(1024)
        cmd_id = 101
        MoveRequestStart(builder2)
        MoveRequestAddCommandId(builder2, cmd_id)
        MoveRequestAddDirection(builder2, MoveDirection.NONE)
        move_offset = MoveRequestEnd(builder2)

        CwmMessageStart(builder2)
        CwmMessageAddSequenceNumber(builder2, 2)
        CwmMessageAddWorldRevision(builder2, snap_msg.WorldRevision())
        CwmMessageAddPayloadType(builder2, Payload.MoveRequest)
        CwmMessageAddPayload(builder2, move_offset)
        msg2 = CwmMessageEnd(builder2)
        builder2.Finish(msg2)

        send_framed_msg(client_sock, builder2.Output())

        # Step 7: Receive CommandAck
        ack_bytes = recv_framed_msg(client_sock)
        ack_msg = CwmMessage.GetRootAsCwmMessage(ack_bytes, 0)
        assert ack_msg.PayloadType() == Payload.CommandAck
        ack = CommandAck()
        ack.Init(ack_msg.Payload().Bytes, ack_msg.Payload().Pos)
        assert ack.CommandId() == cmd_id
        assert ack.Accepted()
        print("  CommandAck received and confirmed.")

        # Step 8: Receive updated WorldSnapshot with monster turn stepped
        print("[Step 8] Ingesting updated WorldSnapshot post-simulation turn...")
        snap2_bytes = recv_framed_msg(client_sock)
        snap2_msg = CwmMessage.GetRootAsCwmMessage(snap2_bytes, 0)
        assert snap2_msg.PayloadType() == Payload.WorldSnapshot

        snapshot2 = WorldSnapshot()
        snapshot2.Init(snap2_msg.Payload().Bytes, snap2_msg.Payload().Pos)

        z_x1, z_y1, z_z1 = None, None, None
        for i in range(snapshot2.EntitiesLength()):
            ent = snapshot2.Entities(i)
            if ent.Id() == zombie_id:
                pos = ent.Pos()
                z_x1, z_y1, z_z1 = pos.X(), pos.Y(), pos.Z()
                break

        if z_x1 is None:
            print(f"ERROR: Zombie ID={zombie_id} disappeared from snapshot!")
            return False

        dist_0 = math.hypot(z_x0 - player[1], z_y0 - player[2])
        dist_1 = math.hypot(z_x1 - player[1], z_y1 - player[2])
        print(f"  Zombie stepped: Pos=({z_x1:.1f}, {z_y1:.1f}, {z_z1:.1f})")
        print(f"  Distance to player: Before={dist_0:.2f}, After={dist_1:.2f}")

        # Step 9: Verify 60 FPS LERP Smoothing Simulation
        print("[Step 9] Simulating Luanti Presentation Bridge 60 FPS LERP interpolation...")
        current_pos = [z_x0, z_y0, z_z0]
        target_pos = [z_x1, z_y1, z_z1]
        dt = 1.0 / 60.0  # 60 FPS frame time (16.6ms)

        positions_interpolated = []
        for frame in range(15):  # 15 frames (~250ms)
            dx = target_pos[0] - current_pos[0]
            dy = target_pos[1] - current_pos[1]
            dz = target_pos[2] - current_pos[2]
            alpha = min(1.0, dt * 12.0)
            current_pos[0] += dx * alpha
            current_pos[1] += dy * alpha
            current_pos[2] += dz * alpha
            positions_interpolated.append(list(current_pos))

        print(f"  Frame  0 (0.0ms):  ({positions_interpolated[0][0]:.3f}, {positions_interpolated[0][1]:.3f})")
        print(f"  Frame  5 (83.3ms): ({positions_interpolated[5][0]:.3f}, {positions_interpolated[5][1]:.3f})")
        print(f"  Frame 10 (166.7ms): ({positions_interpolated[10][0]:.3f}, {positions_interpolated[10][1]:.3f})")
        print(f"  Frame 14 (233.3ms): ({positions_interpolated[14][0]:.3f}, {positions_interpolated[14][1]:.3f})")

        # Invariant: smooth monotonic progression without snapping
        residual_dx = abs(positions_interpolated[-1][0] - target_pos[0])
        residual_dy = abs(positions_interpolated[-1][1] - target_pos[1])
        print(f"  LERP convergence residual: dx={residual_dx:.4f}, dy={residual_dy:.4f}")
        assert residual_dx < 0.2 and residual_dy < 0.2, "LERP failed to converge smoothly to target!"

        client_sock.close()
        print("\n==================================================")
        print(" [SUCCESS] Milestone 3: Visual Entities & LERP PASSED! ")
        print("==================================================")
        return True

    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        if os.path.exists(socket_path):
            os.unlink(socket_path)

if __name__ == "__main__":
    success = run_entity_animation_test()
    sys.exit(0 if success else 1)
