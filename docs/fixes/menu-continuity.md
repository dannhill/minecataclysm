# Continuous action menus — 2026-10-26

The paired Linux CWM2.37 runtimes keep related screens within the same live
modal in normal start.sh. Inventory/external storage → native choices → work
→ result/inventory, and crafting → confirmation → progress/cancellation → K,
replace content without an intervening world-only frame. This follows the
[developer's direct feedback](../source/modal-continuity-feedback-2026-10-26.md).

The original code closed the form to release Menu pause, sent the selected
operation and reopened inventory after native completion. The new action view
separates those states. Its input is fenced while the native command executes;
actual decisions retain their authoritative identity and explicit cancellation.
Native time, activities, debt, output and costs are unchanged.

**Pause and inspect / I** stops the same clock, including inspection before
an equipment ACK arrives. Atomic wear/takeoff remains applied and cannot be
undone. Genuine activities retain their existing native interruption controls.
**Return to game / Esc** explicitly leaves and opts out of automatic return;
it does not refund an admitted operation. F7 and F8 remain available in the
action view; pausing preserves its return target, changing speed while paused
does not advance work. Ordinary browsing still freezes time. Reconnect/death
invalidate the local view/return intent without replaying an operation.

The view model and shared-theme renderer remain separate from native command
routing, so later visual redesign does not require gameplay changes.
[Detailed contract](../design/menu-continuity.md).

## Verification

Captured incremental builds and isolated saves/configuration were used. Native
regression selects the existing CWM/reading/disassembly/melee/ranged/NPC/mission
suite, rather than the entire upstream suite or a cold conformance audit.
Client unit tests, the protocol/presentation SDK and shared-language checks run
against captured sources. The version changes to 2.37 because the native
crafting completion guarantee now uses InventoryWorkState; no schema offsets or
canonical saves change, but an older server must not satisfy this negotiation.

Actual Xvfb/Mesa Luanti renderer tests record modal count at every sampled
camera frame. They check continuity through seal choices/cancellation, external
pouring, consumption and cancellation, paid clothing, crafting choices/work/
interruption/completion, and manual pause with speed changes. Delayed ACK,
unchanged native debt, explicit exit, reconnect and independent pinned-CDDA
canonical readback verify the functional limits. Installed checks use the same
matching binaries. [Source, commands, counts and SHA-256 evidence](menu-continuity-evidence.json).
Screenshots were inspected by the LLM agent, not accepted by a human.

Exploratory runs retain two wrong-equipment-fixture failures (the food scene
has no hat) and one real F7 interception regression in the new work modal.
The latter was fixed by routing configured pause/speed shortcuts through the
modal with physical key-repeat fencing. Failed attempts are excluded from
passing verification totals.

## Human validation and next work

The human developer confirmed **FB-01.1/2 PASS** after the CWM2.36 startup fix;
previous FB-01.3/4 remain PASS. This separate presentation follow-up adds only
MENU-01.1: **59 PENDING, no open manual FAIL**, with UF8-01.1 still pending.
The prior results are retained; automated checks do not supply personal PASS.
[Manual ledger](../validation/pending-manual.md) · [human testing and LLM authorship](../../HUMAN_TESTING.md).
This report was written by an LLM following the sole developer's direct instructions.

Next core work remains essential native item uses, safe liquid outputs and
purification, then non-demo survival-loop/recovery/performance consolidation.
Mapping batch60, the Windows CWM2.26 installer, historical M5.5 FAILED and full
SAVE-001 OPEN remain unchanged by this scoped presentation repair.
