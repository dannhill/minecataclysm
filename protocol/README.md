# CDDA–Mineclonia Common World Model (CWM) Protocol

This package defines the standalone, binary IPC protocol between:
- **Cataclysm: Dark Days Ahead (CDDA)** — The Authoritative Simulation Engine
- **Luanti / Mineclonia** — The 3D Presentation & Voxel Rendering Runtime

## Specifications
- **Format**: FlatBuffers binary serialization (`cwm.fbs`)
- **Transport**: Unix Domain Sockets (`AF_UNIX`) on POSIX, TCP loopback fallback
- **Framing**: 4-byte big-endian length-prefixed stream framing
- **License**: Apache-2.0

## Directory Layout
- `cwm.fbs`: Authoritative schema definition
- `include/cwm/`: Generated C++ headers, message builders, frame encoder/decoder, IPC transport
- `python/`: Generated Python bindings for testing, simulation tools, and fuzzers
- `tests/`: Automated unit test suite verifying serialization and IPC socket transport
