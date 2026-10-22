# Native disassembly — 2026-10-22

I now offers **Disassemble** for an accessible owned single item, and
**Resume disassembly** for its native unfinished object. CDDA owns the action,
confirmations, requirements, time, workbench/exertion modifiers, interruption,
recovery rolls, consumed tools and component placement. Nothing is deleted or
created by Luanti. Books retain separate Read/Skim and Disassemble actions.
[Bounded contract](../design/native-disassembly.md).

I pauses the real actor; Close resumes. Interrupt leaves the native unfinished
item with its counter; choosing Resume continues paid progress. Closing I to
submit the ordinary cancel can allow one more native tick before cancellation;
the assertion is no reset/refund, not an unchanged earlier inspection counter.
Native placement can use a workbench or the ground. Collect an interrupted
object there before resuming it through I in this first owned-item slice.

CWM **2.27** adds the eighth equipment action/reason, disassembly information,
the exact native actor's work-item counter and typed cancellation. Session/view
identities and the command ledger reject stale, changed, paused and duplicate
requests. Reconnect and save/load expose existing work without issuing it again.
No canonical save fields or separate Luanti disassembly persistence were added.

A native const activity accessor exposes the exact actor target. Its counter,
not player_activity.moves_left, is authoritative for ACT_DISASSEMBLE. Inspection
uses concrete reachable tools without generating randomized environmental water.
A further RNG probe caught temporary item construction in upstream disassembly
requirement filtering. That type-level filter now reads the type flag directly;
a data-wide test compares default-instance flags and every resulting component
list, and checks RNG preservation. Existing stored component-instance flags
continue through the original native recovery path.

## Scoped verification

- Native regression: **120 cases / 72,540 assertions PASS**, including CWM,
  reading, selected melee/ranged and upstream disassembly coverage. Focused new
  disassembly coverage: **5 cases / 6,800 assertions PASS**, including dry/water
  inspection purity, confirmations, native yields, typed/stale/duplicate cancel,
  native resume and a data-wide component-filter comparison.
- Client: **309 tests / 47 modules PASS**, plus **648 Catch assertions / 4 cases**.
  Inventory checks include separate reading/disassembly actions and interrupt
  precedence. Protocol: **14/14 PASS**, including malformed metadata, bounds,
  exclusivity and typed requests. Language **9/9**, extensible registry **3/3**.
- **48 renderer/canonical checks PASS**: 24 start/inspect/decline/pause/cancel/
  resume/reconnect/active-save checks; 12 loaded-completion checks; 12 checks
  repeated with the actual installed start.sh runtime pair.

The pristine pinned-CDDA reader creates the scene and independently loads both
partial and completed saves. Readback finds exactly one unfinished item with
its saved counter and ACT_DISASSEMBLE, no early components, then completion
without another start request and two recovered faux-fur sheets on the ground.
Position stays unchanged; the original does not duplicate alongside the work.
Agent inspection of renderer screenshots is separate from human acceptance.

[Exact sources, checksums, commands, logs and limitations](native-disassembly-evidence.json).
These are incremental captured reconstructions, not cold builds. The const
header change rebuilt dependent native core/test units. The later type-filter
repair rebuilt native requirements and the affected integration units. A final
complete target build passes; the client binary is retained after verifying
its source inventory and shared SDK bytes are unchanged by that native-only fix.
The reconstruction refresher now preserves identical root-file timestamps;
source content/mode validation remains mandatory.

Investigation failures are retained separately: private actor access was
replaced before build verification; an overstrict graphical cancel assertion
was corrected for paid native ticks; the RNG test exposed and drove the filter
repair; its extra test was corrected to use public recipe.is_reversible().
No earlier failing attempt is counted as final PASS.

## Installation and personal backlog

The exact verified **Linux runtime pair is installed in normal `./start.sh`**.
Rollback copies remain under `artifacts/native-disassembly-20261022/` as
`native-before-disassembly` and `client-before-disassembly`; restore them
together for the previous CWM2.26 pair. Preferences and developer saves were
not used or edited by verification. Mapping batch60 is unchanged.

`./disassembly-demo.sh --fresh` creates an isolated copy with faux-fur foot
wraps, lamp and backpack. Select the wraps in I, choose Disassemble and confirm.
Their native recipe needs no extra tool; its components appear nearby.
Relaunch without --fresh to retain that demo's canonical save. If recreating
its fixture, use the pristine reader recipe in the evidence receipt with
`--create-disassembly`, never a player world.

**37 PENDING, no open manual FAIL**: four new DIS-01 checks and the previous 33
unchanged in [the shared manual ledger](../validation/pending-manual.md).
No new personal test is required today; none is inferred from automation.
Existing manual PASS entries remain the sole human developer's reports under
[the public testing/authorship statement](../../HUMAN_TESTING.md).

**NPC conversations are not implemented.** There is no working talk control.
The native coordinator explicitly rejects friendly-NPC bump dialogue, and the
continuous controller does not invoke it. Previous native-dialog PASS entries
cover activity confirmations/choices, not conversations, trade or missions.
A dedicated conversation slice is the next core candidate; those social loops
must remain open until actually integrated and verified.

This delivery supports one empty, non-charge-counted solid item or its single
unfinished disassembly, with solid recovery. Charged stacks, liquid/gas recovery,
recursive/bulk operations and environmental-only pseudo-tools remain follow-ups.
Historical **M5.5 FAILED**, full **SAVE-001 OPEN**, and five historical optional
statistical melee failures remain unchanged. No complete milestone is certified.

The Windows installer delivered on 2026-10-21 remains its verified **CWM2.26
snapshot**; it has not been replaced with an untested build. This feature is in
Linux/start.sh. Future Windows packaging derives the protocol version from the
captured header instead of a hardcoded literal.
