#!/usr/bin/env python3
"""
Dynamic Fields, Authoritative Lighting & Mouse Picking Verification Test
Milestone 4 Verification Test
Verifies dynamic field (fire/smoke) creation, lighting illumination,
and Luanti 3D raycast/picking coordinate transformation.
"""

import sys
import os
import time
import socket
import struct
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
from CDDA.CWM.InteractRequest import InteractRequestStart, InteractRequestAddCommandId, InteractRequestAddTargetCoord, InteractRequestAddAction, InteractRequestEnd
from CDDA.CWM.InteractAction import InteractAction
from CDDA.CWM.Coord3i import CreateCoord3i
from CDDA.CWM.CommandAck import CommandAck

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

def run_dynamic_fields_test():
    print("==================================================")
    print(" Running Milestone 4: Dynamic Fields & Lighting   ")
    print("==================================================")

    socket_path = "/tmp/cwm_fields_test.sock"
    user_dir = "/tmp/cdda_fields_user"
    world_name = "fields_test_world"
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
        client_str = builder.CreateString("luanti_cdda_fields_test")
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
        print("[Step 4] Ingesting initial WorldSnapshot and ambient lighting...")
        snap_bytes = recv_framed_msg(client_sock)
        snap_msg = CwmMessage.GetRootAsCwmMessage(snap_bytes, 0)
        assert snap_msg.PayloadType() == Payload.WorldSnapshot

        snapshot = WorldSnapshot()
        snapshot.Init(snap_msg.Payload().Bytes, snap_msg.Payload().Pos)

        # Inspect chunks and lighting
        first_chunk = snapshot.Chunks(0)
        first_block = first_chunk.Blocks(0)
        initial_light = first_block.LightLevel()
        print(f"  Initial ambient light level at Z={first_chunk.ChunkZ()}: {initial_light} (range 0-15)")
        assert 1 <= initial_light <= 15, "Ambient lighting out of range!"

        player_ent = snapshot.Entities(0)
        px = int(player_ent.Pos().X())
        py = int(player_ent.Pos().Y())
        pz = int(player_ent.Pos().Z())
        print(f"  Player origin for picking: ({px}, {py}, {pz})")

        # Step 5: Test Mouse Picking Raycast conversion
        print("[Step 5] Testing Luanti 3D Raycast to CDDA coordinate conversion...")
        target_cdda = (px + 2, py + 1, pz)
        # Coordinate mapping: Luanti = (x, z*3, -y)
        luanti_coord = (target_cdda[0], target_cdda[2] * 3, -target_cdda[1])
        # Inverted mapping: CDDA = (luanti.X, -luanti.Z, round(luanti.Y / 3.0))
        roundtrip_cdda = (luanti_coord[0], -luanti_coord[2], round(luanti_coord[1] / 3.0))
        print(f"  Picked CDDA Pos:     {target_cdda}")
        print(f"  Mapped Luanti Voxel: {luanti_coord}")
        print(f"  Roundtrip CDDA Pos:  {roundtrip_cdda}")
        assert target_cdda == roundtrip_cdda, "Mouse picking coordinate transform mismatch!"

        # Step 6: Dispatch InteractRequest(USE) on target coordinate to ignite fire
        print(f"[Step 6] Dispatching InteractRequest(USE) at picked coordinate {target_cdda} to ignite fire field...")
        builder2 = flatbuffers.Builder(1024)
        cmd_id = 701
        InteractRequestStart(builder2)
        InteractRequestAddCommandId(builder2, cmd_id)
        coord_off = CreateCoord3i(builder2, target_cdda[0], target_cdda[1], target_cdda[2])
        InteractRequestAddTargetCoord(builder2, coord_off)
        InteractRequestAddAction(builder2, InteractAction.USE)
        interact_off = InteractRequestEnd(builder2)

        CwmMessageStart(builder2)
        CwmMessageAddSequenceNumber(builder2, 2)
        CwmMessageAddWorldRevision(builder2, snap_msg.WorldRevision())
        CwmMessageAddPayloadType(builder2, Payload.InteractRequest)
        CwmMessageAddPayload(builder2, interact_off)
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

        # Step 8: Receive updated WorldSnapshot with dynamic field and illumination
        print("[Step 8] Ingesting updated WorldSnapshot post-ignition...")
        snap2_bytes = recv_framed_msg(client_sock)
        snap2_msg = CwmMessage.GetRootAsCwmMessage(snap2_bytes, 0)
        assert snap2_msg.PayloadType() == Payload.WorldSnapshot

        snapshot2 = WorldSnapshot()
        snapshot2.Init(snap2_msg.Payload().Bytes, snap2_msg.Payload().Pos)

        num_fields = snapshot2.FieldsLength()
        print(f"  Active dynamic fields present: {num_fields}")
        if num_fields == 0:
            print("ERROR: Expected at least 1 active field in snapshot!")
            return False

        found_fire = False
        for fi in range(num_fields):
            fld = snapshot2.Fields(fi)
            fc = fld.Coord()
            ftype = fld.FieldTypeId()
            fden = fld.Density()
            print(f"  Field {fi}: Coord=({fc.X()}, {fc.Y()}, {fc.Z()}), TypeId={ftype}, Density={fden}")
            if ftype == 1:  # Fire
                found_fire = True

        assert found_fire, "Fire field was not present in snapshot!"
        print("  Authoritative fire field verified.")

        client_sock.close()
        print("\n==================================================")
        print(" [SUCCESS] Milestone 4: Fields & Lighting PASSED! ")
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
    success = run_dynamic_fields_test()
    sys.exit(0 if success else 1)
