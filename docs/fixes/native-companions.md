# Individual companion orders and rules — 2026-10-22

Linux **`./start.sh` supports a dedicated local-ally panel**. Right-click a
perceived ally and choose the first **Companion orders and rules** response.
Guard this position / Follow me use the native NPC order functions. Combat
and Behavior pages expose all 18 native follower rules; additional pages expose
native engagement, aiming and CBM reserve/recharge preferences. Base settings,
effective settings and temporary overrides are displayed separately. Changing
a base rule never silently clears an overriding order.
`./companions-demo.sh --fresh` provides an isolated ally scene.

Only a local, visible, living ally who can communicate is eligible. Eligibility
is rechecked after each choice. The shortcut is absent in radio, stranger,
sleep and blocked native conversation topics. Local guard/follow cannot
release camp or expedition assignments. The panel grants no recruitment,
skills, equipment, healing or power. The native conversation's normal avatar
exit cost and NPC-side setter/weapon-selection costs are retained.
[Detailed contract](../design/native-companions.md).

The existing native decision/connection identities own every selection.
Reading and pagination do not apply dialogue entry effects again or change
rules. Esc/disconnect safely leaves the conversation; accepted changes remain
canonical and are never replayed. Explicit Back returns to the current native
friend/guard topic. The compact layout uses Mineclonia presentation assets;
only a semantic control-panel flag is appended to ConversationInfo in CWM2.31.
There is no client AI model, parallel NPC inventory or new save format.

## Verification

- **171 native cases / 73,526 assertions PASS** across CWM, reading,
  disassembly, selected melee/ranged, NPC dialogue and mission conditions.
  The new companion case checks all 18 rule IDs, observational browsing,
  unchanged panel-time/RNG/moves/position, native base vs effective overrides,
  native guard/follow, camp protection, stranger, sleeping/deaf and lost-vision
  rejection. Assertions are inside the action boundary: the normal subsequent
  native world phase legitimately advances NPC AI and turn credit.
- **309 client tests / 47 modules PASS**, plus 648 Catch assertions / 4 cases.
  Protocol **16/16**, launcher language **9/9**, registry **3/3** and the
  standalone companion view check PASS.
- **89 actual renderer/canonical checks PASS**: reconstructed companion 29,
  installed companion 29 and journal regression 31. Keyboard/mouse input
  through start.sh exercises paused
  browsing, explicit base/override edits, old-decision replay, policy selection,
  native return topic, actual guard/follow movement, reconnect and canonical
  readback. The installed pair and the existing journal are checked separately;
  exact counts, images, commands and hashes are in the evidence.

The reader is linked to the unmodified pinned native core, never production
fork objects. It creates an ally through native follow/assignment APIs and
independently reloads the resulting canonical save, checking exact native rule
bits, override enable/value, engagement, aim, power preferences, assignment
and absence of a fabricated player activity. Screenshots were inspected by
the LLM agent; no personal human acceptance is inferred.

[Exact identities and evidence](native-companions-evidence.json). Builds are
incremental captured reconstructions with retained caches, not cold builds.
Earlier investigation logs retain include/API build errors and test-only
boundary/relay/reach mistakes. The initial purity test incorrectly compared
RNG/moves after the ordinary native AI phase; the corrected test measures the
panel itself. A relay helper shadowed Python's select module; later the GUI
test attempted to talk beyond the normal unarmed four-tile pointing reach.
The final test approaches via real native movement rather than changing range.
No failed attempt is counted as a final PASS.

## Installed runtime and next core slice

The verified Linux CWM2.31 pair is installed in start.sh, with the previous
pair retained as `artifacts/native-companions-20261022/native-before-companions`
and `client-before-companions`. Developer worlds/preferences were not used.
Mapping batch60 is unchanged; Windows remains the CWM2.26 installer snapshot.

**53 PENDING, no open manual FAIL**: four COMP-01 tests added to the
[human ledger](../validation/pending-manual.md), previous 49 unchanged. No manual
gate required now. The [core outlook](../progress/core-outlook-2026-10-22.md)
remains approximately **90–95%, reference 92%, excluding personal tests**.
Next essential slice: native sleep/rest and waiting; then missing essential
liquid/item uses and consolidated non-demo/regression/performance coverage.
Training, copied/pickup rules, radio/group orders, complex services and camps
are separate work. Historical **M5.5 FAILED** and full **SAVE-001 OPEN** remain
unchanged.
