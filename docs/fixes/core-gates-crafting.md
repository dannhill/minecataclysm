# Core gate feedback: crafting, opening controls and gradual darkness

The sole human developer reported **T1–T7 PASS**, alongside concrete bugs and
comfort feedback. These are personal observations, not agent-inferred acceptance.
[Original feedback and scope](../source/manual-core-gates-2026-10-18.md),
[public human-testing/authorship statement](../../HUMAN_TESTING.md).

## Result

The normal `start.sh` runtime now excludes native navigation categories from
executable recipes, updates searches while typing, retains the selected recipe
when changing a batch, and puts the catalog-limit warning below the grid.
The native recipe and activity rules remain unchanged. Inventory I also filters
as characters change; clicking the search field is still required.

The no-result bandage was `nested_bandages`, a native `nested_category`,
mistakenly exported as a craft. Its description groups other recipes; it has
no result. Native `crafting_gui.cpp` handles these as navigation. The flattened
CWM catalog now lists actual known children, rejects categories on validation
and favorite changes, and refuses continuation of such unsupported old work.
It does not delete saved history/items or change recipes to make the demo pass.
Real `bandages` require sanitary components, tape and disinfectant; the demo's
cotton sheets support `bandages_makeshift`. Tests cover missing materials and
actual real-bandage production for batches 1 and 4, not only an accepted ACK.

Live crafting queries have a 120 ms typing debounce, remain read-only and keep
MENU_OPEN. A newer edit waits for the outstanding query; its intermediate reply
is not installed as matching the new text. Craft starts cannot use the old handles
while searching. When a batch/favorite refresh returns, selection is rebound
by recipe plus new/resume role only if unambiguous, then uses the new view ID.
Several unfinished works for the same recipe are never silently conflated.
The actual search widget survives same-form regeneration, retaining focus,
caret and text selection. Non-integrated forms keep their previous behavior.

**O** (`keymap_cdda_close`) explicitly requests native CLOSE. Plain RMB still
toggles the authoritative projected state. An already closed domestic window
can support both OPEN (glass) and CLOSE (draw curtains), so both inputs are
needed. Native side/range/body/cost rules apply. The ray now intersects the
semantic opening volume, limited by the existing scene occlusion ray, allowing
selection of an open window's empty upper pane without aiming down at its sill.
O never falls back to OPEN; Shift remains posture input.

The low-light tint approaches the native target exponentially over wall time
(0.45 s time constant) instead of switching at a snapshot. It is independent
of F8, retains a bounded subtle maximum and decays on leaving darkness. The
label says “Low ambient light”; the cue is not a new visibility calculation.
Native roof/ambient lighting, including visually odd open-sided roofs, remains
unchanged. Three-dimensional lateral lighting is still a separate design issue.

Quit/load preserves the canonical native work, not an open inventory/menu pause.
The current load behavior therefore resumes the activity. A future initially
paused load is recorded separately; this fix neither cancels the saved actor
nor changes its time cost.

## Verification and installation

Both production components were built incrementally from captured reconstructed
sources. CWM **2.24 unchanged**, client audio remains enabled. Previous root
executables are retained in `artifacts/catalog-feedback-20261018` for rollback.
Exact sources, binaries, commands, checks and logs are recorded in
[the evidence receipt](core-gates-crafting-evidence.json).

Native tests: **100 cases / 65,437 assertions PASS**, including crafting-category
exclusion and actual medical-bandage batches. Luanti: **309 tests / 47 modules**
plus **648 Catch assertions / 4 cases PASS**. Protocol: **12/12 PASS** after
reconfiguring the test cache to include presentation-event coverage. Language:
**9/9 PASS**. Reconstructed launcher/coordinator aliases: **6/6 PASS**.

**253 actual GUI/canonical checks PASS** across reconstructed runs and the
installed ordinary `start.sh`. The tests exercise live partial searches, middle edits, batch selection,
native components/progress/interruption/resume/results and independent canonical
readback; empty-pane RMB and O CLOSE with persisted window state; the native
equipment debit/pause; and the gradual low-light renderer under controlled CWM
state. The controlled peer verifies presentation, not native lighting physics.
Audio uses an OpenAL null backend; listening comfort still needs human playtest.
Reconstructed builds retain caches and are not independent cold builds.

During test preparation, the initial real-bandage test did not enter its action
callback because fixture move credit was not initialized. It now explicitly
initializes credit and requires that the callback ran. A GUI port collision and
an empty `xdotool key` call at batch 1 were test-harness defects, corrected before
final runs. Earlier launcher binaries were configured for another checkout;
fresh aliases targeting the reconstructed checkout pass. Those initial logs
remain in the local artifact directory; none are counted as final PASS.

The five previously recorded opt-in statistical melee failures are outside the
active test filter and were not repaired or promoted by this delivery. Full
SAVE-001 remains OPEN and historical M5.5 FAILED. Item mapping stays at batch60.

The [manual ledger](../validation/pending-manual.md) now has **24 PENDING, no
open manual FAIL**. Four new rechecks are deferred; a new automated PASS is not
the developer's personal acceptance. Next functional roadmap slice remains
native reading, followed by disassembly/related item work.
