# CWM: required contract and observed implementation

Normative sources: [v1.0](../docs/source/architecture-v1.0.md) and
[v1.1 amendments](../docs/source/amendments-v1.1.md). This document records the
captured implementation; it does not approve its gaps. The executable schema
is [cwm.fbs](cwm.fbs). Audit findings and evidence are in
[M5.5](../docs/audits/M5.5.md).

The current runtime requires **CWM 2.18**. This breaks the old negotiation
contract; schema fields and union members are appended without changing the
existing FlatBuffers offsets. Both executables must be rebuilt together.
The historical coverage table below is retained as audit evidence.

CWM 2.18 appends `QuickbarSwapRequest` (43), `InventoryArrangeRequest` (44)
and `InventoryEntry.ui_order`. Swap compares both exact expected bindings
and changes the two slots atomically on the native owner thread; a stale
source or destination rejects the whole operation. An empty target means
move, not duplicate. Arrangement validates the current owned-item view and
every binding, then inserts the source before another current item (zero
means end). Both requests have bounded ledger signatures/at-most-once results;
they change UI metadata only, without movement, activity or time costs.

Optional native item `item_vars.cwm_inventory_position` holds a positive
integer rank up to 2048. Missing/malformed ranks export zero. It follows the
actual native instance through moves/copies and save/load, not ephemeral
query IDs. Native stacking ignores this reserved UI key; splitting retains
it only on the original portion. The rank is a compact visual order, not
an extra pocket, capacity limit or persistent empty-slot coordinate.

Drag input stays inside Luanti's GUI. The bridge resolves current view/item
identities and sends these semantic requests or existing EquipmentRequest /
ItemTransferRequest. No widget name, pixel rectangle, GUI event or Luanti
inventory mutation is introduced into the wire contract. Native equipment
and transfer requests continue to pay CDDA costs and retain its choices.
[Implementation and evidence](../docs/fixes/inventory-drag-and-drop.md).

CWM 2.17 appends `QuickbarBindRequest` (41), `QuickbarUseRequest` (42),
`WorldSnapshot.quick_slots`, `InventoryEntry.quick_slot/rotten` and owned-item
category/wielded/rotten presentation fields. Category strings in inventory,
owned-item metadata and quick slots carry native item-category IDs (not translated
labels); renderers may localize their display. This clarification keeps icons
stable across language choices without changing the schema.
Nine quick slots are references
to actual owned items, not additional storage. Binding uses a current inventory
view/item plus the expected previous binding; clearing requires zero view/item.
It changes optional UI metadata only, without native move costs or time advance.
Each binding has a unique 32-character lowercase hexadecimal identity, exported
with the item's native action eligibility, worn/wielded and spoilage state.
Queries retain ephemeral IDs; those IDs are never saved as shortcuts.

Use requests carry slot, exact binding and an EquipmentAction. Admission and
execution resolve the same actually-owned native instance and validate the
action; rebound/lost/ambiguous identities reject rather than select a namesake.
The existing native equipment/consume/treatment branches and InventoryWorkState
own costs and completion. Paused/busy uses do not queue for later replay.
Both messages have bounded ledger signatures and at-most-once outcomes.
Snapshot validators reject malformed slot count/order, duplicate or invalid
identities, forbidden action bits and contradictory item roles.

Bindings persist as optional native avatar `values` (`cwm_quick_slot_1`–`_9`)
and item `item_vars` (`cwm_quick_identity`). No mandatory save field or
Luanti structure is added. Integrated native stacking ignores this reserved UI
key; splitting keeps it on the original portion and clears it on the new one.
Loss/consumption/merge ambiguity clears a reference instead of guessing a
replacement. The scoped pristine reader retains these optional keys; this is
not full SAVE-001 certification or proof of upstream gameplay parity.
[Implementation and evidence](../docs/fixes/interactive-quickbar.md).

CWM 2.16 appends WorldSnapshot.inventory_work (InventoryWorkState): a nonzero
command identity and native settled flag. completed_command_id still identifies
the first result publication, not paid completion. Inventory execution and valid
native interruption replace the work identity; busy rejections do not replace
an active operation. Settled requires no native actor, positive recovered native
move credit and, in real time, a paid coordinator deadline. Native ACT_* move
debits are observed on the owning thread and paced on the same clock, including
the final partial turn and interruption; no inventory UI duration is invented.
Disconnect/reset clears this ephemeral correlation, never the canonical actor.
All new identity fields are semantically validated before projection.

CWM 2.15 appends ItemTransferRequest (39), CancelItemTransferRequest (40),
InventoryEntry.transfer_reason/container and WorldSnapshot.item_transfer;
CancelReloadRequest retains union 38. Transfers bind a current owned-item
view, source/destination native safe item_locations and a positive exact
quantity (one instance for non-charge items). DROP selects ground at the
query's canonical avatar tile, explicitly excluding automatic vehicle cargo;
INSERT selects an owned real container, with native pocket selection.
Admission/execution revalidate identities, ancestry, quantities, canonical
position, activity/pause and native direct/ancestor capacities. Worn sources,
liquids/gases, technical/sealed ancestry and spillable full containers need
dedicated interactions. A destination with sealed CONTAINER pockets is rejected;
this UI never authorizes implicit unsealing. Cycles and no-op insertion into
an immediate parent are rejected. The ledger signature includes all request
fields; refresh/recovery invalidates ephemeral selections.

ACT_DROP / ACT_INSERT_ITEM remain canonical native actors with their original
access/transfer costs and save data. ItemTransferState is exclusive with the
other exported activities: nonzero token, nonnegative total/remaining bounded
by total; INSERT needs positive total, DROP may export zero total/remaining
because native dropping has no fixed-duration progress. No invented percentage
is shown for such work. CancelItemTransferRequest requires the exact active
interruptible native transfer token, and cannot queue behind another activity.
I freezes work and lets the player cancel through native cancel_activity.
The first slice covers owned container destinations and current-tile ground;
external containers, manual per-pocket placement, seals and fluids are later.

CWM 2.14 appends RangedRequest (union 37), CancelReloadRequest (38),
WorldSnapshot.ranged_weapon and WorldSnapshot.reload. CancelCraftingRequest
retains union 36. Weapon tokens identify the actual wielded native item and
current mode; replacement, mode changes and connection recovery invalidate
them. AIM/FIRE carry an existing perceived hostile entity ID; RELOAD has no
target. No client coordinates, hit claims, recoil, damage or ammunition edits
are accepted. Native checks run at admission and execution. AIM spends native
move credit through the same aiming function as target_ui; FIRE uses native
fire_gun, recoil/dispersion/projectiles/damage/charges. The real-time adapter
holds paid aim between inputs by spending idle credit without improving it;
movement, other actions, invalid targets/weapons and recovery end that hold.
Manual/menu pause never gives free aim improvement. The first slice excludes
free reticle/neutral targets, reload-and-shoot and mounted/vehicle weapons.

RELOAD invokes reload_wielded, native ammo options and explicit confirmation.
Only accessible unsealed container ancestry is offered by the external
selector; quantities, reload targets and costs are native. ACT_RELOAD owns
remaining work and final charge transfer. ReloadState uses ephemeral token
and native positive total_moves / bounded remaining_moves, exclusive with
consumption, first aid and crafting. CancelReloadRequest requires the exact
interruptible ACT_RELOAD token and has its own ledger signature. Native save
data contains the original reload actor and item_locations, no CWM token.
Read-only weapon state carries bounded name/reason, nonnegative ammo/range
and finite native recoil; malformed states require authoritative resync.

CWM 2.13 appends the crafting catalog/query/start/cancel messages and native
work progress. Queries disclose known recipes and requirements without
charging time; view-local handles invalidate after refresh/recovery. Native
component/source choices and confirmation precede ACT_CRAFT; interrupted work
remains a canonical craft item resumable from owned or accessible nearby
surfaces. Recipe scope and exact evidence: [crafting](../docs/fixes/native-crafting.md).

CWM 2.12 adds TREAT=5, six action reasons and `WorldSnapshot.first_aid`.
TREAT selects an accessible owned non-comestible item with native heal use.
Filthy, broken, incompatible, underwater/mounted and insufficient-charge
cases are rejected by CDDA; constraints are checked again when executed.
The native body_window constructs available parts, health display and treatment
descriptions. Its external adapter sends enabled choices plus Cancel through
DecisionPrompt; the native mapping validates the selected index. An explicit
Yes/No confirmation names the actual item and selected body part before
heal_actor assigns canonical ACT_FIRSTAID. No CWM body-part healing arithmetic,
health mutation or patient/inventory authority is introduced in Luanti.
Native use_item handles access; firstaid_activity_actor owns effects, practice,
proficiencies and single-use/charge removal at completion. The exact native
obtained item_location replaces the actor target, as in native consume finish.
Oral/COMESTIBLE medications, liquid antiseptics and other patients are outside
this first treatment slice and are explicitly unavailable here.

FirstAidState has the same bounded native work semantics as ConsumptionState;
the two cannot coexist in a snapshot. CancelFirstAidRequest has its own payload
and ledger signature and must match both token and ACT_FIRSTAID. Tokens change
on activity kind/start and are not canonical save fields. A consumption cancel
cannot stop a treatment with a matching token. All gameplay commands revalidate
native busy state at admission and execution; queued actions cannot replace a
newly started activity. Native cancel preserves spent work/backlog rules.
Canonical first aid saves retain target, patient/body part and remaining work.
BodyPartStatus.conditions appends bounded known wound/treatment names disclosed
by the native body UI (bandaged/disinfected/bleed/bite/infected/mending), without
exporting arbitrary hidden effects or exact timers. H presents those names.

CWM 2.11 appends CONSUME=4 to EquipmentAction, native `consume_moves`,
`consume_label` and the first read-only `consume_warning` to InventoryEntry.
All five reasons are required, matching the enabled action mask. CONSUME
is limited to owned FOOD/DRINK, accessible unsealed container pockets, native
can_eat availability and foods whose use action needs no separate interface
(PETFOOD is exempt like native eat). MED/tools and other special uses are
blocked. Soft warnings remain enabled: the native actor asks the full set of
warnings interactively before starting. Declining schedules no work and
consumes no serving. Native avatar_action::eat assigns ACT_CONSUME with empty
terminal-menu continuation; completion is entirely the native actor's job.
Native eat does not charge obtain_cost separately: access_moves is descriptive,
not a cost added by the bridge. Quantities, digestion, ownership confirmation
and container removal/preservation remain native.

WorldSnapshot.consumption replaces the optional native progress: an ephemeral
activity token, positive total_moves, 0 <= remaining_moves <= total_moves.
It is absent when no active positive-work consumption exists. Client validation
rejects malformed progress via resync. This is native work, not a wall-time
ETA; pause/speed changes need no local inference. Tokens are renewed on each
CWM start, including restarting the same item, and after native load in a new
server. They are not saved. No other consumption initiator is exposed in this
slice. CancelConsumptionRequest(command_id, activity_token) goes through the
session/sequence guards and at-most-once ledger, then cancels the matching
interruptible native activity immediately at the coordinator boundary, never
behind its busy action queue. Manual/threat/decision/recovery pauses reject it;
the UI removes the menu pause before sending, as with other owned actions.
Stale/zero/different tokens cannot cancel a later meal. Native cancellation
preserves already spent time and native backlog rules. In this pinned native
actor, a newly requested consume restarts its duration; the bridge does not
patch that behavior. A canonical load retains in-flight native actor work.
Ordinary mode uses the same native activity but completes it without real-time
pacing, so the interactive progress/cancel experience is primarily RT-02.
CommandAck for CONSUME means activity start accepted, not food already eaten.

CWM 2.10 appends `InventoryQueryRequest(query_id)`, `InventoryView` and
`EquipmentRequest(command_id, view_id, item_id, action)`. Query IDs correlate
read-only replies separately from the action ledger. A query does not consume
moves, advance the native calendar or invent a gameplay activity. Queries are
rate-limited to one per 100 ms; successful queries replace one bounded server
selection cache. Error replies have view_id 0, empty lists and a reason.

Views contain at most 2,048 entries, 8,192 pockets and 32 ancestry levels, with
an explicit truncation flag. Entry IDs are contiguous view-local handles, not
persistent item IDs. Parent precedes child; parent/pocket links, action bits
and five reasons are validated before rendering. Technical contents use
pocket_index -1 and cannot bypass their native interaction. Pockets report
native volume/weight capacities, remaining space, length/access constraints,
sealed/rigid/watertight flags. Negative remaining capacity is permitted for
native overstuffing. None of these fields changes canonical saves.

WIELD/STOW/WEAR/TAKEOFF revalidate native safe item_locations, ownership,
ancestor chain, type, charges, equipment role and native availability at both
admission and execution. Refresh/resync/disconnect invalidate old handles;
execution invalidates sibling handles before mutation or player choice.
Command dedup binds view, item and action. Completion uses CommandAck and the
existing authoritative state completion flow; the renderer never changes
local inventories optimistically. Native wield/obtain, unwield/disposal,
wear and takeoff pay native costs and use existing decision prompts.
TAKEOFF can natively drop a loaded container when no storage is available;
its contents remain inside. Cancellation is preserved. Sealed/technical
contents, partial quantities, arbitrary transfers and liquid destination
selection require later interaction slices. Both executables require 2.12.

CWM 2.9 appends `StatusValue.perceived_level`: -1 unavailable, otherwise
an ordinal 0–10 well-being level, higher is better. CDDA quantizes only the
same native player-facing hunger effects, instant-thirst descriptor ranges,
fatigue categories and perceived-pain categories used by its native UI.
No raw calories, vitamins, hidden pain or diagnoses are exported. It is not
a linear biological percentage, a Minecraft hunger rule or a death threshold.
Hunger full/engorged/satisfied share a full bar; native color/description still
warn about overeating. Missing native hunger category is unavailable, never
assumed full. Empty known neutral descriptions remain known. Health/stamina
retain their five-segment text resolution; this field is -1 for other values.
Out-of-range levels invalidate state and cause resynchronization. Both
executables require matching 2.9; language/localized text is not parsed by the
renderer to determine fill. No gameplay command or save field is added.

CWM 2.8 appends `MovementModeRequest(command_id, mode)` for WALK/RUN/CROUCH/PRONE.
The native coordinator checks bounds, readiness/pause and native availability,
then queues the same native mode setter used by CDDA keyboard controls.
Execution rechecks availability and pause. Native mode selection is free;
no artificial movement/time/stamina cost or displacement is introduced.
Mode participates in command deduplication. Player state bits 7/8/9 describe
RUNNING/CROUCHING/PRONE; absence means standing/walking. Conflicting bits,
or posture bits on non-player entities, invalidate a snapshot and require
resynchronization. The client changes camera height only after native state.
Native movement-mode multipliers, stamina, noise and canonical `move_mode`
persistence remain authoritative. Matching 2.8 executables are required.

CWM 2.7 enables the existing `AttackRequest(command_id, target_entity_id)`
for adjacent pointed melee against perceived hostile monsters/NPCs. The
`HOSTILE_TO_PLAYER` actor state bit (6) comes from native attitude and is
published only when perceived. No client damage/weapon formulas are added.
Identity participates in deduplication; admission and execution both resolve
current native identity, hostility, visibility, same-level adjacency and
clear path. Paused/recovering clients cannot queue attacks for later.
Native melee owns damage, defenses, stamina, proficiency and action cost.
No hostile-target fallback by coordinates; no ranged, reach or friendly attack
in this slice. The long-attack warning uses coordinator decisions with No
last, so losing the peer cancels. Both executables require matching 2.7.

CWM 2.3 appends authoritative ground-item tile lists to `WorldSnapshot`.
Empty lists in incremental updates remove the previous pile; full state
replaces the cache. CWM 2.4 appends selection guards to `InteractRequest` for
`PICKUP`: stack index, type ID, charges and count-by-charges. The server stores
an absolute target at admission and checks reach and the selected native map
item again at execution. A stale selection is rejected. A valid selection
assigns CDDA's native pickup activity for the entire selected stack; its ACK
means activity assignment, not completed transfer. Native capacity, pocket
selection, action costs and activity completion remain authoritative.
Pickup guards participate in command deduplication.

CWM 2.5 appends `owned_items` to `WorldSnapshot`: a complete read-only
projection of native possessions, including worn, wielded and nested items.
Indices describe presentation order and are not inventory mutation handles.
A present vector replaces the possession projection; an absent vector clears
it on a full snapshot and preserves it on a delta. Native export currently
publishes the complete vector with each state. Item lists require contiguous
indices and bounded, nonempty type/name strings. Ground tiles additionally
require unique, bounded local coordinates. Both lists are limited to 8,192
entries; ground-tile vectors are limited to 65,536 entries.

The ground container uses Mineclonia's formspec layout, slot textures and
Luanti inventory widgets. Its detached lists are client-only immutable
mirrors. Moving a displayed ground stack into the possession panel queues a
native PICKUP and closes the menu before executing it. No inventory action is
sent to the Luanti server or applied optimistically. Each widget represents
one complete native stack; native charges are shown in its tooltip. Partial
quantities, dropping and equipment rearrangement are not implemented here.
Disconnect/reset/resync cancels unsent selections and closes this form.
These fields and widgets do not create a Luanti-owned gameplay inventory.

CWM 2.6 appends `avatar_status`: complete native player-facing stamina,
needs and main body-part descriptions, including native health bars and
perceived temperature. IDs are semantic; colors are native palette names.
No raw numeric HP/pain fields, calorie/vitamin values or hidden diagnoses
are exposed. A native description may include a perceived pain number when
the native examination effect authorizes that precision.
Empty native descriptions remain empty. A present status replaces the view;
an absent one clears it on a full snapshot and preserves it on a delta.
The exporter includes it in every state. Read-only UI queries do not run a
native action, consume moves or alter inventory. Status tables have bounded
strings (IDs 128, labels 256, text 2048, palette 64 bytes), unique needs/part
IDs, at most 32 needs and 64 parts; NUL strings and missing fields are invalid.
Malformed status follows normal freeze/resynchronization before ingestion.
The body sheet uses the existing native menu pause and is closed on IPC loss,
reset or resynchronization. Local Luanti HP/breath/hotbar are suppressed while
the bridge owns the player; they are not authoritative survival indicators.

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

Chunks follow CDDA's native 12×12 submap geometry and are indexed `x` fastest,
then `y`, then `z`. The server exports 11×11 chunks at each of the player's
three Z levels (363 chunks), covering the native 132×132 reality bubble exactly.
Ordinary XY bubble shifts are exported incrementally; full chunk snapshots remain
for initial synchronization, recovery, and incompatible cache changes.

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

## CWM 2.2 — Optional real-time prototype

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


## Continuous prototype (2.2)

`SimulationState.continuous_motion` advertises the opt-in native controller.
`ContinuousIntentRequest` carries an idempotent command ID and native XY
floats, never a position. Finite directions of length at most sqrt(2) are
normalized; zero releases. Invalid/paused intents are rejected. Grid held
intent and horizontal MoveRequest are rejected in this mode. Vertical and
interaction requests continue through native actions. Player Vec3f contains
native tile plus the server's paid, saved offset. The initial rate is global
4x; the same clock advances every gameplay system.

Continuous offset, fractional debit credit and stamina remainder are stored
in canonical CDDA Creature values. Native tile-based perception, AI and combat
still use the anchor. This is a spatial prototype, not a claim that every CDDA
system now uses continuous distances. An anchor mismatch after an external
teleport resets offsets but retains already-paid rounding credit.


## External storage (2.19)

`InventoryQueryRequest.external_coord` optionally selects an absolute native
CDDA tile. The server requires same-Z adjacency, perception and native item
accessibility. The resulting InventoryView combines owned and external entries,
marks external ancestry explicitly, and supplies the native site label and
volume capacity/free space. An ordinary query still exports possessions only.
External rows have no owned equipment actions, quick slots or grid order.

All handles are ephemeral. Query binds the avatar origin, site terrain/furniture
IDs, safe native item_locations, type/charges and parent chains. Both admission
and native execution revalidate them. A changed position/site/selection, sealed
pocket or inaccessible tile rejects; no search for a replacement by type/name.

ItemTransferAction appends TAKE_EXTERNAL=2 and DEPOSIT_EXTERNAL=3. Quantity is
positive, at most the current native charges, or one for non-counted items.
TAKE_EXTERNAL starts native ACT_PICKUP and carries no destination handle.
DEPOSIT_EXTERNAL starts native ACT_DROP with the queried tile offset and
force_ground; capacity is checked at admission/execution. INSERT=1 also accepts
accessible external item containers, subject to native size/capacity/ancestry
and ownership restrictions. External equipment/drop/arrange shortcuts reject.
Native theft/capacity decisions remain part of pickup; direct insert cannot
bypass ownership or open sealed pockets. Work pause/cancel/completion follows
the existing paid inventory-work lifecycle. ACT_PICKUP exports transfer state
with unknown total (zero), as native drop already permits.

GroundItemTileState appends storage/label; visible native CONTAINER furniture
exports a site even when empty. Contents require native perception,
could_see_items and accessible_items. GroundItemState appends container to allow
opening a ground backpack rather than immediately collecting it. STORAGE bit 7
is presentation semantics only. Storage sites suppress rotating item visuals;
loose ground items retain them. Deltas clear vanished sites and resync installs
a new complete projection. All fields use CDDA coordinates/identities; no
Luanti inventory or type is serialized. Exact 2.19 negotiation is required.

Vehicle cargo, liquid transfer and explicit per-pocket placement are outside
this slice. Native actor persistence stays canonical. During an activity CDDA
may apply its own overflow/drop policy if the destination changes; the client
requeries the actual result instead of assuming a committed destination.


## Graphical native decisions (2.20)

DecisionPrompt appends `cancel_choice:int32=-1`. CDDA advertises the existing
safe fallback index; -1 disables client cancellation. Native paged choices keep
their original mapping. Cancel never depends on translated labels or the client
assuming that the last choice is safe. Choice count remains 1–9; IDs are nonzero,
text/labels are bounded to 16384 bytes and labels are nonempty and NUL-free.
Invalid prompts initiate authoritative resynchronization. Exact 2.20 negotiation
is required; response and canonical-save formats are unchanged.

The modal renderer binds decision ID and connection identity, accepts one
explicit response and waits for native settlement/new prompt. In real-time mode
settlement observes PauseReason::Decision (16), not Recovery (8). Native lookup,
pagination, costs and fallback on lost peer remain server-owned. Physical held
keys do not answer a later prompt; graphical reading/cancellation does not infer
health, consequences or successful inventory work from text/initial ACKs.
