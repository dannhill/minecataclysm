#!/usr/bin/env python3
"""
Vertical Slice Automated Acceptance Test
Milestone 1 Verification Test
Verifies end-to-end IPC communication between CDDA Headless Server
and CWM Client (Luanti presentation model).
"""

import sys
import os
import time
import socket
import struct
import subprocess
from pathlib import Path

# Add FlatBuffers python bindings
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
from CDDA.CWM.InteractRequest import InteractRequestStart, InteractRequestAddCommandId, InteractRequestAddTargetCoord, InteractRequestAddAction, InteractRequestEnd
from CDDA.CWM.InteractAction import InteractAction
from CDDA.CWM.Coord3i import CreateCoord3i
from CDDA.CWM.TileDelta import TileDelta

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

def run_vertical_slice_test():
    print("==================================================")
    print(" Running Milestone 1: Vertical Slice Acceptance   ")
    print("==================================================")

    socket_path = "/tmp/cwm_vs_test.sock"
    user_dir = "/tmp/cdda_vs_user"
    world_name = "vertical_slice_world"
    cdda_bin = WORKSPACE_ROOT / "cdda" / "build" / "src" / "cdda-server"

    if os.path.exists(socket_path):
        os.unlink(socket_path)

    cmd = [
        str(cdda_bin),
        "--socket", socket_path,
        "--world", world_name,
        "--userdir", user_dir,
    ]

    print(f"[Step 1] Starting CDDA headless server...")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    try:
        # Wait for socket to become ready
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

        # Step 3: Send HelloRequest
        print("[Step 3] Sending CWM HelloRequest handshake...")
        builder = flatbuffers.Builder(1024)
        client_str = builder.CreateString("luanti_cdda_client_5.10.0")
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

        # Step 4: Receive HelloResponse
        print("[Step 4] Awaiting HelloResponse...")
        resp_bytes = recv_framed_msg(client_sock)
        resp_msg = CwmMessage.GetRootAsCwmMessage(resp_bytes, 0)
        if resp_msg.PayloadType() != Payload.HelloResponse:
            print(f"ERROR: Expected HelloResponse, got payload type {resp_msg.PayloadType()}")
            return False

        hello_resp = HelloResponse()
        hello_resp.Init(resp_msg.Payload().Bytes, resp_msg.Payload().Pos)
        if not hello_resp.Accepted():
            print("ERROR: HelloRequest was rejected by server!")
            return False
        server_build = hello_resp.ServerBuildId().decode("utf-8") if hello_resp.ServerBuildId() else "unknown"
        print(f"  Handshake accepted by CDDA! Server build: {server_build}")

        # Step 5: Receive Initial WorldSnapshot
        print("[Step 5] Awaiting initial WorldSnapshot...")
        snap_bytes = recv_framed_msg(client_sock)
        snap_msg = CwmMessage.GetRootAsCwmMessage(snap_bytes, 0)
        if snap_msg.PayloadType() != Payload.WorldSnapshot:
            print(f"ERROR: Expected WorldSnapshot, got payload type {snap_msg.PayloadType()}")
            return False

        snapshot = WorldSnapshot()
        snapshot.Init(snap_msg.Payload().Bytes, snap_msg.Payload().Pos)

        num_chunks = snapshot.ChunksLength()
        num_entities = snapshot.EntitiesLength()
        print(f"  Received WorldSnapshot: {num_chunks} chunks loaded, {num_entities} entities present.")

        if num_chunks == 0:
            print("ERROR: Snapshot contains 0 chunks!")
            return False
        if num_entities == 0:
            print("ERROR: Snapshot contains 0 entities (missing player)!")
            return False

        player_ent = snapshot.Entities(0)
        p_id = player_ent.Id()
        p_x = player_ent.Pos().X()
        p_y = player_ent.Pos().Y()
        p_z = player_ent.Pos().Z()
        p_name = player_ent.Name().decode("utf-8") if player_ent.Name() else ""
        print(f"  Player entity verified: ID={p_id}, Name='{p_name}', Position=({p_x:.1f}, {p_y:.1f}, {p_z:.1f})")

        # Step 6: Send MoveRequest (EAST)
        print("[Step 6] Dispatching MoveRequest (EAST)...")
        builder2 = flatbuffers.Builder(1024)
        cmd_id = 42
        MoveRequestStart(builder2)
        MoveRequestAddCommandId(builder2, cmd_id)
        MoveRequestAddDirection(builder2, MoveDirection.EAST)
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
        print("[Step 7] Awaiting CommandAck for move...")
        ack_bytes = recv_framed_msg(client_sock)
        ack_msg = CwmMessage.GetRootAsCwmMessage(ack_bytes, 0)
        if ack_msg.PayloadType() != Payload.CommandAck:
            print(f"ERROR: Expected CommandAck, got {ack_msg.PayloadType()}")
            return False

        ack = CommandAck()
        ack.Init(ack_msg.Payload().Bytes, ack_msg.Payload().Pos)
        print(f"  CommandAck received: CommandId={ack.CommandId()}, Accepted={ack.Accepted()}")
        if ack.CommandId() != cmd_id:
            print(f"ERROR: CommandId mismatch: expected {cmd_id}, got {ack.CommandId()}")
            return False

        # Step 8: Receive updated WorldSnapshot with player moved
        print("[Step 8] Awaiting updated WorldSnapshot...")
        snap2_bytes = recv_framed_msg(client_sock)
        snap2_msg = CwmMessage.GetRootAsCwmMessage(snap2_bytes, 0)
        if snap2_msg.PayloadType() != Payload.WorldSnapshot:
            print(f"ERROR: Expected WorldSnapshot, got {snap2_msg.PayloadType()}")
            return False

        snapshot2 = WorldSnapshot()
        snapshot2.Init(snap2_msg.Payload().Bytes, snap2_msg.Payload().Pos)
        player_ent2 = snapshot2.Entities(0)
        p_x2 = player_ent2.Pos().X()
        p_y2 = player_ent2.Pos().Y()
        print(f"  Updated player position: ({p_x2:.1f}, {p_y2:.1f}, {player_ent2.Pos().Z():.1f})")

        # Step 9: Send InteractRequest (OPEN door at adjacent position)
        print("[Step 9] Dispatching InteractRequest (OPEN)...")
        builder3 = flatbuffers.Builder(1024)
        interact_cmd_id = 43
        InteractRequestStart(builder3)
        InteractRequestAddCommandId(builder3, interact_cmd_id)
        coord_offset = CreateCoord3i(builder3, int(p_x2) + 1, int(p_y2), int(player_ent2.Pos().Z()))
        InteractRequestAddTargetCoord(builder3, coord_offset)
        InteractRequestAddAction(builder3, InteractAction.OPEN)
        interact_offset = InteractRequestEnd(builder3)

        CwmMessageStart(builder3)
        CwmMessageAddSequenceNumber(builder3, 3)
        CwmMessageAddWorldRevision(builder3, snap2_msg.WorldRevision())
        CwmMessageAddPayloadType(builder3, Payload.InteractRequest)
        CwmMessageAddPayload(builder3, interact_offset)
        msg3 = CwmMessageEnd(builder3)
        builder3.Finish(msg3)

        send_framed_msg(client_sock, builder3.Output())

        # Step 10: Receive Interact CommandAck
        print("[Step 10] Awaiting Interact CommandAck...")
        ack2_bytes = recv_framed_msg(client_sock)
        ack2_msg = CwmMessage.GetRootAsCwmMessage(ack2_bytes, 0)
        if ack2_msg.PayloadType() != Payload.CommandAck:
            print(f"ERROR: Expected CommandAck for interact, got {ack2_msg.PayloadType()}")
            return False
        ack2 = CommandAck()
        ack2.Init(ack2_msg.Payload().Bytes, ack2_msg.Payload().Pos)
        print(f"  Interact CommandAck received: CommandId={ack2.CommandId()}, Accepted={ack2.Accepted()}")

        client_sock.close()
        print("\n[SUCCESS] Milestone 1: Vertical Slice Acceptance Test PASSED!")
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
    success = run_vertical_slice_test()
    sys.exit(0 if success else 1)
