# CWM: required contract and observed implementation

Normative sources: [v1.0](../docs/source/architecture-v1.0.md) and
[v1.1 amendments](../docs/source/amendments-v1.1.md). This document records the
captured implementation; it does not approve its gaps. The executable schema
is [cwm.fbs](cwm.fbs). Audit findings and evidence are in
[M5.5](../docs/audits/M5.5.md).

This document retains takeover-baseline coverage below. Subsequent scoped
repairs are recorded in their evidence: native canonical turns/loading,
stable presentation through rebases, perceived creature models and native
decisions. The current implementation uses minor 4: minor 3 appended the terrain
catalog, minor 4 appends actor state cues. Negotiation/session/recovery conformance remains
unverified.

## Wire format

Each message is a four-byte unsigned big-endian length followed by one
nonempty FlatBuffers `CwmMessage`. The absolute size limit is 16 MiB; a
connection can configure a smaller limit through `IpcLimits`. There is no
FlatBuffers file identifier, compression, checksum, authentication or session
identifier. The schema carries sequence number, world revision, timestamp and
a typed union payload. C++ and Python bindings regenerate identically with
flatc 24.3.25.

`MessageVerifier` validates FlatBuffers structure. It does not establish
semantic validity. The bridge rejects a snapshot without `origin` and skips
entities/vehicles/components lacking `pos`/`pivot`/`offset`. Vector
length/dimension consistency, enum ranges and finite/in-range coordinates
still require comprehensive validation at the boundary.

The schema contains no Luanti `MapNode` or `content_t`. Framing currently
includes POSIX `arpa/inet.h`, and endpoints directly use `IpcConnection`.
Only Unix-domain socket connection/listening is implemented; an alternate
backend and the required transport abstraction remain absent.

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
hardcoded voxel scale and baseline eye height. Inverse picking uses floor division
of node Y by three, so both aperture halves and negative Z levels belong to
the correct native floor. Native actor cues adjust presentation posture only.
A configurable, shared transform and
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
can select richer textures/vegetation; ordinary presentation now uses the
approved B style (`cdda_terrain_enriched = true`). Only comparison mode retains
the extra semantic cache needed for live A/B switches. Fog and visual variants are client
configuration, not gameplay state or new wire data. See the
[prototype evidence](../docs/prototypes/terrain-comparison.md).

The exporter uses loaded CDDA terrain flags, open/close links and movement
costs for structural geometry. Door/gate family names supplement missing native
DOOR flags on linked transitions; two empty-curtain IDs supplement missing
WINDOW flags. Names also select floor/ground textures. Closed/open state follows
native transitions, independently of DOOR flags or passability alone. Open but
blocking trailer doors retain a visible threshold. Window states retain a
lower wall/sill; only the upper pane changes. `CwmBlock.state_flags` bit 0 identifies doors, bit 1 records
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

Minor 4 appends `EntityState.state_flags:uint32=0` after `perceived`, leaving
older fields unchanged. Actor bits are WINDOW_PASSAGE (1), WADING (2),
SWIMMING (4) and UNDERWATER (8). CDDA derives them from native terrain/avatar
state, excluding vehicle-supported water tiles. Luanti smoothly adjusts feet
and first-person eye height; authoritative positions, action costs and time do
not change. They are distinct from the tile obstruction flags above. See the
[exploration repair](../docs/fixes/exploration-apertures.md) for evidence/limits.

Desktop picking sends native OPEN/CLOSE through the existing coordinator:
right-click opens, Sneak + right-click closes; an empty pane/door can be targeted
through its remaining sill/floor. Actions share the movement ACK/state gate;
Luanti dig/place callbacks do not modify the projection. No full interaction
query, inventory or vertical-control interface is certified by this wiring.

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

## Bounded transport after FND-02

The historical takeover reproduced lost final frames, uncaught oversized-frame
exceptions and approximately 100-ms synchronous sends under backpressure.
[FND-02](../docs/fixes/fnd02-transport.md) repairs that transport behavior;
the original behavioral probe is retained unchanged and now passes.

`send_message` accepts a frame into a bounded FIFO; success does **not** mean
delivery. `poll_and_receive` pumps both directions. CDDA and Luanti call it
with zero timeout. Partial writes retain the head offset; EAGAIN returns to
the runtime without waiting or dropping queued frames. Each connection defaults
to the following limits, configurable through `IpcLimits`:

| Resource/work per connection | Default |
| --- | --- |
| Payload | 16 MiB absolute ceiling |
| Pending input staging | 16 MiB + 4 bytes |
| Retained output frames | 32 MiB and 128 frames |
| Read/write per pump | 256 KiB each |
| Delivered frames per pump | 8 |
| Delivered payload per pump | 1 MiB; one legal larger first frame may be delivered |
| recv/send attempts per pump | 64 each, including EINTR |

Read the leading four-byte prefix and validate it before staging its body.
The decoder uses a cursor and bounded growth/occasional compaction. Zero or
oversized lengths, structurally invalid FlatBuffers and output overflow close
the offending connection. Truncated input closes after delivering preceding
complete frames. Queue overflow disconnects rather than dropping a delta while
keeping the client apparently synchronized. A fresh connection receives a
full authoritative snapshot under the existing lifecycle; full negotiation,
gap detection, deduplication and recovery correctness remain FND-03.

POLLHUP/ERR does not precede readable bytes: recv establishes EOF. Complete
buffered frames drain across successive bounded pumps. A **false** return may
still accompany final complete frames; both runtime adapters consume these
before disabling the connection. CDDA cancels movement/interactions still in
its command queue when the connection departs. A complete valid response to
the currently pending native decision can be consumed before EOF; absent
responses retain the safe native default. No unexecuted command crosses into
a replacement connection.

Additional connections are rejected while the current one is live. The
visual thread uses nonblocking connect without waiting; the bridge owns its
retry timer and is initialized once per Luanti Client. Disconnect disables
command readiness and hides actors while retaining the static projection.
Unix socket path lengths and fd flags are checked. There is still no alternate
transport backend or negotiated session/world reset contract.

These are byte/frame/syscall budgets, not a general wall-clock bound on native
snapshot generation or renderer ingestion of a legal 16-MiB frame. Benchmarks
and further semantic vector/coordinate validation remain FND-04/05.
Tests cover the actual socket layer plus adverse peers in real native and
graphical runtimes. The optional camera trace records connection status,
queue sizes and per-pump counters. Historical broader session failures in
`tests/takeover_runtime.py` and `tests/takeover_render.py` remain separate debt.
