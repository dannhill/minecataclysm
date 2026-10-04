# CWM: required contract and observed implementation

Normative sources: [v1.0](../docs/source/architecture-v1.0.md) and
[v1.1 amendments](../docs/source/amendments-v1.1.md). This document records the
captured implementation; it does not approve its gaps. The executable schema
is [cwm.fbs](cwm.fbs). Audit findings and evidence are in
[M5.5](../docs/audits/M5.5.md).

This document retains takeover-baseline coverage below. Subsequent scoped
repairs are recorded in their evidence: native canonical turns/loading,
stable presentation through rebases, perceived creature models and native
decisions. The current terrain comparison uses minor 3; its appended material
catalog is described below. Negotiation/session/recovery conformance remains
unverified.

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

## Takeover-baseline message coverage (historical)

| Payload | CDDA server | Luanti bridge |
| --- | --- | --- |
| HelloRequest / HelloResponse | Accepts every major version; handshake can spawn a zombie | Sends hello; reports acceptance, but marks connected before validation |
| Heartbeat / HeartbeatAck | Replies | No periodic RTT measurement |
| WorldSnapshot | Full terrain on connection/rebase; changed tiles and positions after movement | Applies terrain before visual targets; preserves unchanged terrain |
| ChunkSnapshot | Embedded in WorldSnapshot | Embedded ingestion only |
| TileDelta | Open/close interaction | Applies and requests native mesh updates |
| EntityState / EntityRemoved | Entity states embedded; removal not emitted | Embedded states stored; standalone updates/removal not handled |
| VehicleState | Embedded state, zero velocity | Stores transforms; creates empty scene nodes |
| FieldState | Embedded on snapshots that include chunks | Ignored |
| MoveRequest | Horizontal movement and NONE/wait | WASD hook sends horizontal commands |
| InteractRequest | OPEN, CLOSE and synthetic USE/fire | Public method exists; no gameplay input caller |
| AttackRequest | Not handled | Not sent |
| CommandAck | Replies to implemented requests | Movement waits for matching ACK and subsequent authoritative snapshot |
| TimeEvent | Defined, not emitted | Ignored |

`ResyncRequest`, `WorldReset`, session/player/connection identities, stable
archetype identifiers and spawn events required by v1.1 are absent. The union
cannot express those operations without a schema extension.

## Coordinates and material interpretation

Chunks are 16×16×1, indexed `x` fastest, then `y`, then `z`. The server exports
9×9 chunks at each of the player's three Z levels (243 chunks), despite the
comment and historical test expecting 8×8×3. Horizontal extent is 144 tiles,
larger than the current 132-tile reality bubble. Out-of-bounds cells are explicitly
air; the exporter checks `map::inbounds` before reading terrain/furniture.

`origin.x/y` equals the absolute submap origin times 12. Entity positions and
chunk cells are local in X/Y; their Z value is a CDDA level. `origin.z` is
currently the player's level minus one. The current bridge anchors presentation
at the first snapshot's origin: local XY plus current origin minus initial
origin. Terrain, camera, vehicles, actors and inverse interaction transforms
share this frame. Rebases preserve interpolation and unchanged overlapping
meshes. The incompatible pre-repair transforms remain
documented in the frozen M5.5 audit.

Presentation maps stable scene XY and native Z to `(X,3z,-Y)` in signed 16-bit coordinates, with
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
| 10 / 11 | open / boarded window |
| 12 / 13 | generic solid obstacle / glass wall |
| 14 / 15 | water surface / low traversable obstacle |
| 16 / 17 / 18 | sand / traversable shrub / blocking tree |
| 19 / 20 | sidewalk / long grass |

Minor 3 appends these five terrain categories, retaining the 8-byte CwmBlock
layout. Movement/obstruction flags remain native. The isolated A/B comparison
can select richer textures/vegetation; ordinary presentation maps the appended
IDs back to the earlier generic materials. Fog and visual variants are client
configuration, not gameplay state or new wire data. See the
[prototype evidence](../docs/prototypes/terrain-comparison.md).

The exporter uses loaded CDDA terrain flags, open/close links and movement
costs for structural geometry. Text matching remains only for floor/ground
texture selection. `state_flags` bit 0 identifies doors, bit 1 records
`map::impassable_ter_furn`, bit 2 adds furniture over the terrain and bit 3
requests tall furniture. `orientation` 0/1 describes east-west/north-south wall
alignment inferred from adjacent CDDA wall connections. No native node IDs
are transmitted. Furniture, unfamiliar solid terrain and passable damaged
walls no longer disappear into floor textures. Material/geometry remains an
approximation: fences/rocks and baseline trees share an obstacle placeholder, furniture
uses wooden boxes and stairs/roof surfaces are not detailed meshes.

`WorldSnapshot.tiles` is an appended FlatBuffers vector of `TileDelta`. An
end-of-action comparison of the complete projected semantic tiles emits only
changed cells, including auto-opened doors and furniture modified by actors.
The renderer applies this batch before updating entity targets. A rebase or
invalidated export cache requires full chunks. Both project runtime binaries
must be rebuilt together to render the new materials/batched changes.

Player wire ID is always 1. Cached runtime export uses monotonic monster IDs
from 1000, associated with native weak ownership, and a separate NPC namespace
containing the canonical NPC ID. Actor `perceived` controls rendered visibility;
unperceived records are still sent. Monster IDs do not persist across runtime
restart; vehicle IDs remain process memory addresses. This is not a complete
persisted identity/session registry.

## Required ordering and recovery

The required lifecycle is: negotiate compatible protocol and identities,
receive a complete snapshot, apply ordered atomic turn batches, then accept
input. Sequence gaps, incompatible revisions, reconnect and world reset must
freeze input and obtain a fresh authoritative snapshot. Commands need stable
IDs and bounded deduplication scoped to the session; receiving the same command
must not repeat gameplay.

Currently the server allocates some sequence numbers without emitting a
message; neither side validates ordering. The client stores every incoming
world revision without checking monotonicity. Movement now has a tile batch
inside its result snapshot, but a general revision/recovery contract and
deduplication are absent. Full terrain ingestion replaces the
terrain cache and clears absent projected blocks; native Luanti air blocks
cannot overwrite it. Shutdown clears bridge-owned visual state. Removal of
absent actors within complete rosters is implemented; complete vehicle
lifecycle and reconnect recovery remain uncertified.

## Framing and scheduling defects retained for remediation

The takeover probes reproduce loss of a final frame when EOF/HUP arrives,
uncaught exceptions on oversized incoming frames, and synchronous sends that
block for about 100 ms under backpressure. Receive staging has no bounded
per-frame/per-update work budget. A closed or slow peer must be isolated from
simulation, render responsiveness and canonical save safety.

See `tests/takeover_transport.cpp`, `tests/takeover_runtime.py` and
`tests/takeover_render.py`. Failing probes are deliberately retained.
