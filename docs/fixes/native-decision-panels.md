# UX-04A — Native decisions and work feedback

Installed in ordinary `start.sh`, CWM 2.20. Generic native confirmations and
choosers use a Mineclonia-style modal with scrollable text/choices, safe native
colour markup, full-label tooltips, clickable buttons and physical 1–9 shortcuts.
Esc uses CDDA's advertised safe cancellation index. Enter does not select the
focused child. Physical key state is recorded before menus consume it, so a held
answer cannot approve the next question or a prompt restored after recovery.
Exact decision/connection binding and a submitted state prevent duplicate or
stale responses; a waiting panel persists until native settlement/new prompt.

Native inventory work keeps its paid-completion gate and gains a clear temporary
panel/progress bar. I inspects and pauses; closing resumes; Interrupt cancels
through the native actor. Returned inventory says native work ended without
inferring successful gameplay from an ACK. Debug overlays no longer obscure
questions. Protocol validation bounds IDs, choices, text and cancellation index.
No native save format, medical outcome, cost or duration was changed.

[Design](../design/native-decision-panels.md), [receipt](native-decision-panels-evidence.json),
[deferred user tests](../validation/pending-manual.md). Manual backlog: 26 PENDING;
previous PASS retained. Generic medical choices keep native text and ASCII
information. Anatomical icons/hearts/known effects need native structured
metadata in UX-04B, the next slice. M5.5 remains FAILED and full SAVE-001 OPEN.

Verification uses owned reconstructed sources/build caches, isolated copied
worlds, the actual renderer and independent pristine-core canonical readback.
Native suite: 178 cases / 185963 assertions, seed 42; Luanti: 309 tests / 47
modules and 648 Catch assertions / four cases; protocol: eleven tests. The
presentation probe covers held/released keys, stale binding, safe markup,
cancellation metadata and waiting. Graphic cases exercise Enter, held numbers
across native questions, mouse approval/decline, Esc, pause/resume during
first aid, exact consumption and lost-peer cancellation. Receipts retain source
identities, commands, hashes, installed runtimes/catalogs, rollback and failed
attempts. These are scoped checks, not a clean-build or whole conformance gate.

Actual graphics/canonical checks pass on reconstructed and installed runtimes:
23 each for native dialogs/medication, plus 37 installed consumption regression
checks. They preserve one native bandaging effect, exact remaining medicine,
water/food quantities and canonical digestion. The English-default regression
expectation and stale synthetic-click timing were repaired in the test harness;
no assertion about native cost, pause, identity or conservation was dropped.
