# Native single-item disassembly

CWM 2.27 exposes Disassemble / Resume disassembly in I for an exact owned,
accessible native item. CDDA owns eligibility, tools, light, confirmations,
ACT_DISASSEMBLE, workbench/exertion modifiers, recovery rolls, tool charges,
practice and component placement. The adapter calls Character::disassemble
with its real item_location; it neither removes the item nor creates yields.

The native actor replaces the original with an in-progress `disassembly` item.
Its item_counter (0–10,000,000) is progress; player_activity.moves_left is not
its progress clock. A const activity-actor accessor projects the exact native
actor target, including a workbench target outside the carried inventory.
The actor remains in the canonical save. Session tokens are ephemeral.

I pauses work; Close resumes, Interrupt calls native cancel_activity without
refund. The interrupted object retains its native counter. Select that object
in I and Resume disassembly to continue. A workbench/ground object must first
be collected through the existing native pickup interface; this first slice
starts/resumes owned objects, not arbitrary remote map or vehicle items.
Native placement prompts use the existing crafting-choice adapter.

Favorite, worn and ownership warnings and QUERY_DISASSEMBLE keep their native
meaning. A declined confirmation leaves the original untouched. Stale views,
changed items, busy/paused actions and repeated command IDs use the existing
validation and at-most-once ledger. A typed cancel can only cancel the matching
ACT_DISASSEMBLE generation. Reconnect publishes current state without replay.

Inspection exports native recipe duration as an estimate and unfinished
progress, not guaranteed yield or a client timer. Concrete reachable tools and
owned pseudo-tools are checked with Character::can_disassemble. Inspection
excludes generated environmental pseudo-items (including randomized map water)
so it does not advance RNG/cache generated resources. Environmental-only
pseudo-tool availability is a follow-up; execution still rechecks CDDA's full
crafting inventory. The interface never promises recovery success.

Initial boundaries: one non-charge-counted solid item, or its single-item
unfinished disassembly; empty contents; solid recovered components. Charged
stacks, liquid/gas recovery, sealed technical contents and recursive/bulk
smashing/salvage remain explicit follow-ups. Zero-duration native recipes keep
zero duration. No rate multiplier is added; current global 4x applies uniformly.
The quickbar's automatic default does not select a destructive disassembly.
Books retain Skim/Read alongside a separate Disassemble action.

`./disassembly-demo.sh --fresh` uses an isolated pristine-core fixture with
faux-fur foot wraps, lamp and backpack. Their native 90-second recipe recovers
two faux-fur patchwork sheets, placed nearby. The default 4x means roughly
20–25 real seconds under favorable conditions; native modifiers may differ.
The fixture deliberately needs no cutting tool. Ordinary start.sh has the same
inventory action; no demonstration items are added to the player's world.

Human checks are DIS-01 in the existing manual ledger. Automated scoped
verification does not close historical M5.5 FAILED or full SAVE-001 OPEN.
