# CWM: required contract and observed implementation

Normative sources: [v1.0](../docs/source/architecture-v1.0.md) and
[v1.1 amendments](../docs/source/amendments-v1.1.md). This document records the
captured implementation; it does not approve its gaps. The executable schema
is [cwm.fbs](cwm.fbs). Audit findings and evidence are in
[M5.5](../docs/audits/M5.5.md).

The current runtime requires **CWM 2.1**. This breaks the old negotiation
contract; schema fields and union members are appended without changing the
existing FlatBuffers offsets. Both executables must be rebuilt together.
The historical coverage table below is retained as audit evidence.

## Wire format

Each message is a four-byte unsigned big-endian length followed by one
nonempty FlatBuffers `CwmMessage`. The absolute size limit is 16 MiB; a
connection can configure a smaller limit through `IpcLimits`. No file
identifier, compression, checksum or authentication is added. The envelope
carries sequence number, world revision, timestamp, typed union payload and
explicit session/player/connection IDs. Bindings use flatc 24.3.25.

`MessageVerifier` checks structure. `ClientSession` validates ordering and
snapshot completeness before ingestion: required origin/player/rosters,
finite positions, bounded vectors, exact chunk dimensions/block counts and
consistent spawn/removal references. This is not complete semantic validation
of every enum, coordinate transform, field or interaction; see FND-04.

CWM contains no Luanti structures. `CwmTransport`/`CwmListener` are independent
of OS and framing; endpoints use those interfaces, with POSIX instantiated
only at the backend factory. Framing encodes big-endian bytes without POSIX
headers. Unix sockets are the sole production backend. The in-memory test
backend exercises the same client session controller without descriptors.

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

That table describes the frozen takeover, not the current payload contract.
CWM 2 adds `ResyncRequest`, `WorldReset`, `SnapshotAck`, `EntitySpawned`,
envelope identities and explicit full/incremental state metadata.

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
requests tall furniture. Bits 4/5/6 record native GOES_UP, GOES_DOWN and
DIFFICULT_Z (terrain or furniture). Water can carry GOES_UP too: that bit
does not imply a staircase. `orientation` 0/1 describes east-west/north-south wall
alignment inferred from adjacent CDDA wall connections. No native node IDs
are transmitted. Furniture, unfamiliar solid terrain and passable damaged
walls no longer disappear into floor textures. Material/geometry remains an
approximation: fences/rocks and baseline trees share an obstacle placeholder, furniture
uses wooden boxes. Vertical connections have compact stair/ladder entry
geometry; they are not full physical flights. Roof surfaces remain simplified.

`WorldSnapshot.tiles` is an appended FlatBuffers vector of `TileDelta`. An
end-of-action comparison of the complete projected semantic tiles emits only
changed cells, including auto-opened doors and furniture modified by actors.
The renderer applies this batch before updating entity targets. A rebase or
invalidated export cache requires full chunks. Both project runtime binaries
must be rebuilt together to render the new materials/batched changes.

Player wire ID is always 1. Monster wire ID is `(1 << 62) | native_id`; NPC
wire ID is `(1 << 63) | canonical_npc_id`. Missing/invalid monster metadata is
initialized using the native world character-ID allocator, already shared by
avatars/NPCs. Decimal `native_id` is stored in `Creature::values["cwm_monster_id"]`,
which the pinned native reader/writer preserves. No save serializer or wire layout
changes. Allocation consumes native IDs but no gameplay RNG, moves or time.
The allocator retains its native positive-int range; the 64-bit wire namespaces
do not enlarge that allocator. Simultaneously loaded copies with the same metadata
are given distinct IDs; the first native roster occurrence retains the existing
ID. Normal overmap offload/reload and runtime restart preserve the sole owner's ID.

Actor `perceived` controls rendered visibility; unperceived records are still
sent. A newly perceived actor or recovery snapshot establishes its current
position immediately, rather than interpolating an unobserved interval.
Ordinary perceived motion and terrain rebases retain visual interpolation.
Complete rosters govern scene creation/removal. Announced spawn states must
agree with their roster entries; duplicate spawn/removal metadata, invalid actor
kinds, nonfinite rotation and changing kind under a currently installed ID cause
resynchronization before ingestion. Lifecycle vectors and actor rosters are
bounded; spawn validation uses indexed lookup. Archetype evolution within MONSTER
can replace a mesh while preserving identity. Vehicle IDs remain process memory
addresses, pending the separate vehicle work. See the
[actor lifecycle evidence](../docs/fixes/fnd04-actor-lifecycle.md).

Minor 4 appends `EntityState.state_flags:uint32=0` after `perceived`, leaving
older fields unchanged. Actor bits are WINDOW_PASSAGE (1), WADING (2),
SWIMMING (4) and UNDERWATER (8). CDDA derives them from native terrain/avatar
state, excluding vehicle-supported water tiles. Luanti smoothly adjusts feet
and first-person eye height; authoritative positions, action costs and time do
not change. They are distinct from the tile obstruction flags above. See the
[exploration repair](../docs/fixes/exploration-apertures.md) for evidence/limits.

Within CWM 2.0, actor bits 4/5 indicate ON_UP_CONNECTION/ON_DOWN_CONNECTION
on non-water native terrain. They are contextual hints, not a promise that a
blocked connection can be used. Existing MoveDirection UP (9) and DOWN (10)
invoke native `game::vertical_move` through the same command ledger and
ACK/state gate as horizontal movement. Costs, underwater state, stairfinding,
offset destinations, followers and canonical saves remain CDDA-owned.
Only native connections and underwater transitions are supported in this
slice; free climbing/ledge direction selection and vertical vehicle controls
are explicitly rejected, rather than invoking an unadapted terminal selector.
Desktop Jump selects UP; Sneak + Jump selects DOWN, once per fresh press.
These use the remappable engine actions. No Luanti jump/fly movement is enabled.

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

The implemented lifecycle is Disconnected → HelloSent → Accepted → Syncing
→ Running. Sequence/revision/semantic failure enters Resyncing and disables
input. A lost transport returns to Disconnected with one retry timer. Five
seconds without completing negotiation/full sync causes disconnect; native
player decision prompts do not time out.

1. Client Hello has sequence 1, zero envelope identities and a nonzero client
   ID retained across reconnects. Exact major/minor 2.0 is required. The server
   sends no gameplay state before accepting Hello. Rejection is sent and the
   connection closed; there is no permissive legacy fallback.
2. Accepted HelloResponse is sequence 1 and carries a fresh server-runtime
   session ID, native canonical avatar ID, new connection ID and command-ID
   floor. Initial WorldReset(request=0) precedes a full WorldSnapshot.
3. Client installs the complete state on the presentation thread, then sends
   SnapshotAck(state_id). Only that matching acknowledgement enables server
   command acceptance. Input is also gated by client readiness and player state.
4. Each subsequent message matches all three IDs and a contiguous sequence
   in its direction. Counters count messages successfully queued, independently
   of simulation revisions, and restart per connection. WorldSnapshot carries
   full, base_revision, state_id, resync_id and completed_command_id. A running
   update requires base_revision equal to the installed revision; revision
   never decreases. Chunks indicate full replacement, not an inferred delta.
5. Terrain changes and complete actor/vehicle rosters are one atomic message;
   full replacement removes absent terrain, actors and vehicle components.
   Spawn/removal lists are embedded in that batch. Separate TileDelta or actor
   messages cannot bypass the state gate. Dynamic-field rendering remains
   absent and is not certified by this lifecycle.
6. On a gap, reorder or invalid state the client retains its last trusted
   projection, freezes new commands and sends one correlated ResyncRequest.
   Untrusted tail messages are discarded. A matching WorldReset establishes
   the new sequence barrier; the next contiguous full state must match the
   request. State ACK completes recovery. Pending native prompts are replayed
   after state ACK on the same connection. No missing state is inferred.
7. Reconnect to the same session installs a fresh full state with a new
   connection ID. A different session/player discards old caches, visual
   objects and scene origin before ingestion. No uncertain command is
   automatically resent. Full authoritative state resolves its actual effect.

The server has a bounded 1,024-entry at-most-once command ledger. IDs are
monotonic across a server session/player, with client ownership and canonical
request signature. A pending duplicate is not queued again. A completed
duplicate returns the original outcome/result revision and a fresh full state.
Reusing an ID with different semantics/author closes the offender. IDs evicted
below the high-water mark are rejected as expired, never executed again.
Queued actions canceled on disconnect retain a negative outcome. A native
action already in progress may complete and records its result even without
an active client. The ledger is volatile: fresh session identity invalidates
old commands after a server restart. Session/connection identities and command
ledger state are not persisted; native actor identity metadata is canonical as
described above.

The client releases a movement/interaction only after the matching CommandAck
and WorldSnapshot.completed_command_id, with sufficient result revision.
Unrelated heartbeat/state traffic cannot unlock it. WorldReset cancels uncertain
local pending input; recovery never synthesizes or retries gameplay commands.

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
negotiated full authoritative snapshot under the CWM 2 lifecycle above.

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
Unix socket path lengths and fd flags are checked. Socket creation uses mode
0600 and never unlinks another process’s bound path. All launch entry points
exec the single start.sh supervisor; shared fallback socket paths are removed.

These are byte/frame/syscall budgets, not a general wall-clock bound on native
snapshot generation or renderer ingestion of a legal 16-MiB frame. Benchmarks
and further semantic vector/coordinate validation remain FND-04/05.
Tests cover the actual socket layer plus adverse peers in real native and
graphical runtimes. The optional camera trace records connection status,
queue sizes, per-pump counters, session IDs, readiness, received sequence and
resync count. The original takeover probes remain frozen evidence; CWM 2
fixtures test the new contract with substantive native and graphical cases.

## CWM 2.1 — Optional real-time prototype

`SimulationControlRequest` and `MovementIntentRequest` append command payloads.
Both use the existing command ledger and exact version negotiation. A held
intent sets direction 0–8; 0 releases, vertical movement remains a punctual
`MoveRequest`. Accepted intent updates have one effect; native repeated steps
are internal actions, not repeated execution of the request ID.

`WorldSnapshot.clock` is absent in action-driven mode. In real-time mode its
scale is finite in [0.25,4]. Pause bits are Manual=1, Menu=2, Threat=4,
Recovery=8, Decision=16. Unknown bits or invalid scales require recovery.
`SimulationControl` is PAUSE=0, RESUME=1, SET_SPEED=2, MENU_OPEN=3, MENU_CLOSE=4.
Controls change the coordinator, not native movement costs or save serialization.

`EntityState.motion_seconds` is finite in [0.01,60], default 0.2 seconds for
action-driven presentation. The coordinator publishes effective action duration
for the avatar and a native tick duration for other actors. This does not expose
sub-tick AI trajectories. Lifecycle metadata must agree with roster durations.

Pauses drop held intent and acknowledge cancelled queued actions negatively.
A missing delta still requires correlated reset/full-state installation; the
world does not progress while waiting for its ACK. The calendar, native action
and post-player world phases remain distinct; an action result can precede that
tick's AI phase. See [RT-01](../docs/prototypes/rt01-real-time.md) for quantization,
stall policy, evidence and remaining controller decisions.
