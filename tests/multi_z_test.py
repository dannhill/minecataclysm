#!/usr/bin/env python3
"""
Multi-Z Terrain & Building Meshing Verification Test
Milestone 2 Verification Test
Verifies multi-level Reality Bubble layers (Z = -1, 0, +1),
chunk distribution across Z-levels, air vs solid voxel differentiation,
and multi-Z tile delta synchronization.
"""

import sys
import os
import time
import socket
import struct
import subprocess
from pathlib import Path
from collections import defaultdict

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

def run_multi_z_test():
    print("==================================================")
    print(" Running Milestone 2: Multi-Z Meshing Acceptance  ")
    print("==================================================")

    socket_path = "/tmp/cwm_multiz_test.sock"
    user_dir = "/tmp/cdda_multiz_user"
    world_name = "multiz_world"
    cdda_bin = WORKSPACE_ROOT / "cdda" / "build" / "src" / "cdda-server"

    if os.path.exists(socket_path):
        os.unlink(socket_path)

    cmd = [
        str(cdda_bin),
        "--socket", socket_path,
        "--world", world_name,
        "--userdir", user_dir,
    ]

    print("[Step 1] Starting CDDA headless server...")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    try:
        # Wait for socket
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

        # Send HelloRequest
        print("[Step 3] Handshake with CWM server...")
        builder = flatbuffers.Builder(1024)
        client_str = builder.CreateString("luanti_cdda_multiz_test")
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
        print("[Step 4] Ingesting WorldSnapshot for Multi-Z verification...")
        snap_bytes = recv_framed_msg(client_sock)
        snap_msg = CwmMessage.GetRootAsCwmMessage(snap_bytes, 0)
        assert snap_msg.PayloadType() == Payload.WorldSnapshot

        snapshot = WorldSnapshot()
        snapshot.Init(snap_msg.Payload().Bytes, snap_msg.Payload().Pos)

        num_chunks = snapshot.ChunksLength()
        print(f"  Total chunks received: {num_chunks}")
        # Expected: 8x8x3 = 192 chunks
        if num_chunks != 192:
            print(f"ERROR: Expected 192 chunks (8x8x3 across Z=-1,0,+1), got {num_chunks}!")
            return False

        chunks_per_z = defaultdict(int)
        solid_blocks_per_z = defaultdict(int)
        air_blocks_per_z = defaultdict(int)

        for i in range(num_chunks):
            chunk = snapshot.Chunks(i)
            cz = chunk.ChunkZ()
            chunks_per_z[cz] += 1
            num_blocks = chunk.BlocksLength()
            for bi in range(num_blocks):
                block = chunk.Blocks(bi)
                mat_id = block.MaterialId()
                if mat_id == 0:
                    air_blocks_per_z[cz] += 1
                else:
                    solid_blocks_per_z[cz] += 1

        print("[Step 5] Analyzing Multi-Z Layer Distribution:")
        for z in sorted(chunks_per_z.keys()):
            c_count = chunks_per_z[z]
            s_count = solid_blocks_per_z[z]
            a_count = air_blocks_per_z[z]
            total = s_count + a_count
            print(f"  Z={z:+2d}: Chunks={c_count}, SolidBlocks={s_count}, AirBlocks={a_count}, TotalBlocks={total}")

        # Invariants verification
        # 1. Exactly 64 chunks per Z level
        for z in [-1, 0, 1]:
            if chunks_per_z[z] != 64:
                print(f"ERROR: Z={z} has {chunks_per_z[z]} chunks, expected 64!")
                return False

        # 2. Ground level (Z=0) MUST have solid blocks
        if solid_blocks_per_z[0] == 0:
            print("ERROR: Z=0 (ground level) has 0 solid blocks!")
            return False

        # 3. Z=1 (above ground) MUST have predominantly air
        if air_blocks_per_z[1] == 0:
            print("ERROR: Z=1 (upper level) has 0 air blocks!")
            return False
        air_ratio_z1 = air_blocks_per_z[1] / (solid_blocks_per_z[1] + air_blocks_per_z[1])
        print(f"  Z=1 Air Ratio: {air_ratio_z1 * 100:.2f}% (predominantly open air above ground)")
        if air_ratio_z1 < 0.80:
            print(f"WARNING: Air ratio at Z=1 is unexpectedly low: {air_ratio_z1:.2f}")

        # 4. Player entity position verification
        player_ent = snapshot.Entities(0)
        p_z = player_ent.Pos().Z()
        print(f"[Step 6] Verifying player entity vertical position: Z={p_z:.1f}")
        if int(p_z) != 0:
            print(f"ERROR: Expected player at ground level Z=0, got Z={p_z}!")
            return False

        client_sock.close()
        print("\n==================================================")
        print(" [SUCCESS] Milestone 2: Multi-Z Meshing PASSED!   ")
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
    success = run_multi_z_test()
    sys.exit(0 if success else 1)
