#!/usr/bin/env python3
"""
CDDA CWM Protocol Fuzzer
Per Specification Section 66 (Fuzz testing):
Tests truncated messages, invalid frames, garbage payloads, and socket edge cases.
"""

import socket
import struct
import random
import time
import argparse
import sys

def run_fuzzer(socket_path: str, iterations: int = 500):
    print(f"==================================================")
    print(f" Starting CWM Protocol Fuzzer: {socket_path}     ")
    print(f" Running {iterations} fuzzing test iterations...  ")
    print(f"==================================================")

    passed = 0
    crashes = 0

    for i in range(iterations):
        try:
            s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            s.settimeout(1.0)
            s.connect(socket_path)

            case_type = i % 5

            if case_type == 0:
                # Random garbage bytes
                garbage = bytearray(random.getrandbits(8) for _ in range(random.randint(10, 2048)))
                frame = struct.pack(">I", len(garbage)) + garbage
                s.sendall(frame)

            elif case_type == 1:
                # Truncated length header
                s.sendall(b"\x00\x00")

            elif case_type == 2:
                # Length header claiming 1000 bytes, but sending only 10
                s.sendall(struct.pack(">I", 1000) + b"shortdata")

            elif case_type == 3:
                # Oversized frame exceeding 16 MB limit (should trigger instant rejection)
                s.sendall(struct.pack(">I", 32 * 1024 * 1024) + b"\x00\x01\x02\x03")

            elif case_type == 4:
                # Truncated FlatBuffer with valid length header
                fake_fb = b"\x04\x00\x00\x00\x00\x00\x00\x00\xFF\xFF"
                s.sendall(struct.pack(">I", len(fake_fb)) + fake_fb)

            s.close()
            passed += 1

        except (ConnectionRefusedError, FileNotFoundError):
            print(f"ERROR: Server unreachable or crashed at iteration {i}!")
            crashes += 1
            break
        except Exception:
            # Expected socket reset / disconnect from server
            passed += 1

        if (i + 1) % 100 == 0:
            print(f"  Progress: {i + 1}/{iterations} test cases executed.")

    print(f"\nFuzzing completed: {passed} cases handled safely, {crashes} server crashes.")
    return crashes == 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CWM Protocol Fuzzer")
    parser.add_argument("--socket", type=str, default="/tmp/cdda_cwm.sock")
    parser.add_argument("--iterations", type=int, default=500)
    args = parser.parse_args()

    success = run_fuzzer(args.socket, args.iterations)
    sys.exit(0 if success else 1)
