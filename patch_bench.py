import re

with open("tests/benchmark_test.py", "r") as f:
    text = f.read()

# Add Heartbeat imports
text = text.replace("from CDDA.CWM.MoveRequest import MoveRequestStart, MoveRequestAddCommandId, MoveRequestAddDirection, MoveRequestEnd", "from CDDA.CWM.MoveRequest import MoveRequestStart, MoveRequestAddCommandId, MoveRequestAddDirection, MoveRequestEnd\nfrom CDDA.CWM.Heartbeat import HeartbeatStart, HeartbeatAddClientTime, HeartbeatEnd\nfrom CDDA.CWM.HeartbeatAck import HeartbeatAck")

loop_code_old = """
        print("[Step 4] Running BM01/BM02: 100 turns IPC latency test...")
        num_turns = 100
        latencies = []
        for i in range(num_turns):
            cmd_id = 200 + i
            builder2 = flatbuffers.Builder(1024)
            MoveRequestStart(builder2)
            MoveRequestAddCommandId(builder2, cmd_id)
            MoveRequestAddDirection(builder2, MoveDirection.NONE)
            move_offset = MoveRequestEnd(builder2)

            CwmMessageStart(builder2)
            CwmMessageAddSequenceNumber(builder2, 2 + i)
            CwmMessageAddWorldRevision(builder2, world_rev)
            CwmMessageAddPayloadType(builder2, Payload.MoveRequest)
            CwmMessageAddPayload(builder2, move_offset)
            msg2 = CwmMessageEnd(builder2)
            builder2.Finish(msg2)

            t0 = time.perf_counter()
            send_framed_msg(client_sock, builder2.Output())

            ack_bytes = recv_framed_msg(client_sock)
            ack_msg = CwmMessage.GetRootAsCwmMessage(ack_bytes, 0)
            
            # Followed by snapshot/delta
            snap2_bytes = recv_framed_msg(client_sock)
            snap2_msg = CwmMessage.GetRootAsCwmMessage(snap2_bytes, 0)
            world_rev = snap2_msg.WorldRevision()
            
            t1 = time.perf_counter()
            latency_ms = (t1 - t0) * 1000.0
            latencies.append(latency_ms)
"""

loop_code_new = """
        print("[Step 4] Running BM01/BM02: 100 Heartbeats IPC latency test...")
        num_turns = 100
        latencies = []
        for i in range(num_turns):
            builder2 = flatbuffers.Builder(1024)
            HeartbeatStart(builder2)
            HeartbeatAddClientTime(builder2, 0)
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
"""

text = text.replace(loop_code_old.strip(), loop_code_new.strip())
text = text.replace("Completed 100 turns.", "Completed 100 heartbeats.")

with open("tests/benchmark_test.py", "w") as f:
    f.write(text)
