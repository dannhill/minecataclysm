# CDDA–Mineclonia Common World Model (CWM) Protocol

This package defines the standalone, binary IPC protocol between:
- **Cataclysm: Dark Days Ahead (CDDA)** — The Authoritative Simulation Engine
- **Luanti / Mineclonia** — The 3D Presentation & Voxel Rendering Runtime

## Specifications
- **Format**: FlatBuffers binary serialization (`cwm.fbs`)
- **Transport**: Unix Domain Sockets (`AF_UNIX`) on POSIX, TCP loopback fallback
- **Framing**: 4-byte big-endian length-prefixed stream framing
- **License**: Apache-2.0

Minor version 1 adds `WorldSnapshot.safety_stop` and the appended
`AcknowledgeThreatRequest`. Acknowledgement invokes CDDA's native ignore-enemy
action; it does not disable safe mode or advance simulation time. The bridge
shows a warning and uses the configurable Luanti Aux1 binding (default E).
Version negotiation, deduplication and recovery remain FND-03 work.

The current schema minor is 2. `EntityState.perceived` carries CDDA sensory
visibility; the renderer must hide unperceived creatures. Snapshot entity
lists replace the tracked roster, including removal. Monster IDs are stable
within a running coordinator through weak native ownership; persistence of
protocol identities across server restarts remains future work.

`DecisionPrompt` / `DecisionResponse` carry a pending native question and an
explicit numbered selection. The coordinator validates the decision ID and
choice range; waiting for a response does not advance simulation. This covers
yes/no, supported ledge choices and death/world-end decisions. It is not the
complete dialog/inventory/activity coordinator or a recovery certification.

## Directory Layout
- `cwm.fbs`: Authoritative schema definition
- `include/cwm/`: Generated C++ headers, message builders, frame encoder/decoder, IPC transport
- `python/`: Generated Python bindings for testing, simulation tools, and fuzzers
- `tests/`: Automated unit test suite verifying serialization and IPC socket transport
