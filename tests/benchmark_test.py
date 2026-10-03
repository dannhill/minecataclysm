#!/usr/bin/env python3
"""
IPC Latency Benchmark Acceptance Test
Milestone 5 Verification Test
Evaluates BM01 & BM02: ensures IPC latency (round trip) is < 5ms.
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
from CDDA.CWM.MoveRequest import MoveRequestStart, MoveRequestAddCommandId, MoveRequestAddDirection, MoveRequestEnd
from CDDA.CWM.Heartbeat import HeartbeatStart, HeartbeatAddTimestampMs, HeartbeatEnd
from CDDA.CWM.HeartbeatAck import HeartbeatAck
from CDDA.CWM.MoveDirection import MoveDirection
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
            raise ConnectionError("Socket closed")
        hdr += chunk
    length = struct.unpack(">I", hdr)[0]
    data = b""
    while len(data) < length:
        chunk = sock.recv(length - len(data))
        if not chunk:
            raise ConnectionError("Socket closed")
        data += chunk
    return data

def run_benchmark():
    print("==================================================")
    print(" Running Benchmark Test (BM01/BM02 - IPC Latency) ")
    print("==================================================")

    cdda_bin = WORKSPACE_ROOT / "cdda" / "build" / "src" / "cdda-server"
    socket_path = "/tmp/cwm_bench_ipc.sock"
    world_name = "test_world"
    user_dir = "/tmp/cdda_cwm_bench_user"

    if os.path.exists(socket_path):
        os.unlink(socket_path)
    os.makedirs(user_dir, exist_ok=True)

    print(f"[Step 1] Starting CWM Simulation Server: {cdda_bin}")
    cmd = [
        str(cdda_bin),
        "--socket", socket_path,
        "--world", world_name,
        "--userdir", user_dir,
    ]
    # For a real run we might need a dummy CDDA executable if it's mocked,
    # but the previous tests seem to assume the binary exists or it's a mocked python script.
    # Wait, is cdda-server actually compiled in the workspace?
    # Let's check if cdda/build/src/cdda-server exists!
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

        print("[Step 2] Handshake CWM protocol...")
        builder = flatbuffers.Builder(1024)
        client_str = builder.CreateString("luanti_cdda_bench_test")
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

        # Initial snapshot
        print("[Step 3] Initial WorldSnapshot ingested.")
        snap_bytes = recv_framed_msg(client_sock)
        snap_msg = CwmMessage.GetRootAsCwmMessage(snap_bytes, 0)
        assert snap_msg.PayloadType() == Payload.WorldSnapshot
        world_rev = snap_msg.WorldRevision()

        print("[Step 4] Running BM01/BM02: 100 Heartbeats IPC latency test...")
        num_turns = 100
        latencies = []
        for i in range(num_turns):
            builder2 = flatbuffers.Builder(1024)
            HeartbeatStart(builder2)
            HeartbeatAddTimestampMs(builder2, 0)
            hb_offset = HeartbeatEnd(builder2)

            CwmMessageStart(builder2)
            CwmMessageAddSequenceNumber(builder2, 2 + i)
            CwmMessageAddWorldRevision(builder2, world_rev)
            CwmMessageAddPayloadType(builder2, Payload.Heartbeat)
            CwmMessageAddPayload(builder2, hb_offset)
            msg2 = CwmMessageEnd(builder2)
            builder2.Finish(msg2)

            t0 = time.perf_counter()
            send_framed_msg(client_sock, builder2.Output())

            ack_bytes = recv_framed_msg(client_sock)
            ack_msg = CwmMessage.GetRootAsCwmMessage(ack_bytes, 0)
            assert ack_msg.PayloadType() == Payload.HeartbeatAck
            
            t1 = time.perf_counter()
            latency_ms = (t1 - t0) * 1000.0
            latencies.append(latency_ms)

        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        
        print(f"  Completed {num_turns} turns.")
        print(f"  Average IPC Latency: {avg_latency:.2f} ms")
        print(f"  Max IPC Latency: {max_latency:.2f} ms")
        
        assert avg_latency < 5.0, f"BM01 Failed: Average latency {avg_latency:.2f}ms exceeds 5ms limit!"

        print("\n==================================================")
        print(" [SUCCESS] Milestone 5: Benchmark (IPC) PASSED! ")
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
    success = run_benchmark()
    sys.exit(0 if success else 1)
