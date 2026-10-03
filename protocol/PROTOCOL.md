# CWM: required contract and observed implementation

Normative sources: [v1.0](../docs/source/architecture-v1.0.md) and
[v1.1 amendments](../docs/source/amendments-v1.1.md). This document records the
captured implementation; it does not approve its gaps. The executable schema
is [cwm.fbs](cwm.fbs). Audit findings and evidence are in
[M5.5](../docs/audits/M5.5.md).

## Wire format

Each message is a four-byte unsigned big-endian length followed by one
FlatBuffers `CwmMessage`. The current size limit is 16 MiB. There is no
FlatBuffers file identifier, compression, checksum, authentication or session
identifier. The schema carries sequence number, world revision, timestamp and
a typed union payload. C++ and Python bindings regenerate identically with
flatc 24.3.25.

`MessageVerifier` validates FlatBuffers structure. It does not establish
semantic validity: optional `origin`, entity `pos`, vehicle `pivot` and
component `offset` can be absent while the bridge dereferences them. Vector
length/dimension consistency, enum ranges and coordinate bounds also require
validation at the boundary.

The schema contains no Luanti `MapNode` or `content_t`. Framing currently
includes POSIX `arpa/inet.h`, and endpoints directly use `IpcConnection`.
Only Unix-domain socket connection/listening is implemented; TCP headers and
comments do not provide a TCP backend or the required transport abstraction.

## Observed message coverage

| Payload | CDDA server | Luanti bridge |
| --- | --- | --- |
| HelloRequest / HelloResponse | Accepts every major version; handshake can spawn a zombie | Sends hello; reports acceptance, but marks connected before validation |
| Heartbeat / HeartbeatAck | Replies | No periodic RTT measurement |
| WorldSnapshot | Sends immediately after connection, on hello and after movement | Projects chunks, stores visual targets; treats partial snapshots as full messages |
| ChunkSnapshot | Embedded in WorldSnapshot | Embedded ingestion only |
| TileDelta | Open/close interaction | Applies and requests native mesh updates |
| EntityState / EntityRemoved | Entity states embedded; removal not emitted | Embedded states stored; standalone updates/removal not handled |
| VehicleState | Embedded state, zero velocity | Stores transforms; creates empty scene nodes |
| FieldState | Embedded on snapshots that include chunks | Ignored |
| MoveRequest | Horizontal movement and NONE/wait | WASD hook sends horizontal commands |
| InteractRequest | OPEN, CLOSE and synthetic USE/fire | Public method exists; no gameplay input caller |
| AttackRequest | Not handled | Not sent |
| CommandAck | Replies to implemented requests | Received without reconciliation |
| TimeEvent | Defined, not emitted | Ignored |

`ResyncRequest`, `WorldReset`, session/player/connection identities, stable
archetype identifiers and spawn events required by v1.1 are absent. The union
cannot express those operations without a schema extension.

## Coordinates and material interpretation

Chunks are 16×16×1, indexed `x` fastest, then `y`, then `z`. The server exports
9×9 chunks at each of the player's three Z levels (243 chunks), despite the
comment and historical test expecting 8×8×3. Horizontal extent is 144 tiles,
larger than the current 132-tile reality bubble; bounds need an explicit rule.

`origin.x/y` equals the absolute submap origin times 12. Entity positions and
chunk cells are local in X/Y; their Z value is a CDDA level. `origin.z` is
currently the player's level minus one. Luanti adds horizontal origin to
entities/vehicles but ignores it for terrain and tile deltas. It also subtracts
origin.z for entities while terrain uses `level * 3`. These incompatible
interpretations are implementation defects, not alternate valid conventions.

Presentation maps `(x,y,z)` to `(x,3z,-y)` in signed 16-bit coordinates, with
hardcoded voxel scale and eye height. A configurable, shared transform and
explicit large-coordinate policy remain required.

| Material ID | Current interpretation |
| --- | --- |
| 0 | air |
| 1 | dirt |
| 2 | grass |
| 3 | brick wall |
| 4 | wooden floor |
| 5 / 6 | closed / open wooden door |
| 7 | window |
| 8 | pavement |
| 9 | wooden furniture |

The exporter reduces terrain/furniture through string matching and sets only
bit 0 of `state_flags` for door-like terrain. These mappings do not yet cover
all required semantic terrain, layered furniture, stairs or roof shapes.

Player wire ID is always 1. Monster IDs are reassigned from 1000 on every
export. Vehicle IDs are process memory addresses. NPCs are not exported.
These values must not be treated as stable persisted identities.

## Required ordering and recovery

The required lifecycle is: negotiate compatible protocol and identities,
receive a complete snapshot, apply ordered atomic turn batches, then accept
input. Sequence gaps, incompatible revisions, reconnect and world reset must
freeze input and obtain a fresh authoritative snapshot. Commands need stable
IDs and bounded deduplication scoped to the session; receiving the same command
must not repeat gameplay.

Currently the server allocates some sequence numbers without emitting a
message; neither side validates ordering. The client stores every incoming
world revision without checking monotonicity and retains visual maps across
reconnect. There is no delta batch boundary, recovery request or deduplication.
Full snapshot ingestion does not remove absent entities/vehicles or clear old
terrain.

## Framing and scheduling defects retained for remediation

The takeover probes reproduce loss of a final frame when EOF/HUP arrives,
uncaught exceptions on oversized incoming frames, and synchronous sends that
block for about 100 ms under backpressure. Receive staging has no bounded
per-frame/per-update work budget. A closed or slow peer must be isolated from
simulation, render responsiveness and canonical save safety.

See `tests/takeover_transport.cpp`, `tests/takeover_runtime.py` and
`tests/takeover_render.py`. Failing probes are deliberately retained.
