# Known native mission journal — 2026-10-22

Linux **`./start.sh` supports the known mission journal: press J**. Active,
Completed and Failed tabs show only the avatar's native histories. Select a
row to inspect the objective, description when available, giver, deadline and
known destination in native global overmap coordinates, including Z. The
separate **Track this mission** button changes the native tracked selection.
Esc closes the journal and preserves an existing F7 pause.
`./journal-demo.sh --fresh` provides an isolated scene with prepared histories.

Browsing is read-only: it does not assign, complete, fail or reward missions,
evaluate goal conditions, sample randomness or invoke the general dynamic
tag parser. Unsupported dynamic details are explicitly marked unavailable;
missing descriptions and destinations have explicit empty states. This first
slice provides native goal categories and history states, without inventing
completion counters. Deadlines retain native watch/no-watch precision.
[Detailed contract](../design/native-journal.md).

Only a validated current active mission assigned to the avatar can be tracked.
The request checks view, connection and expected tracked selection. The shared
command ledger prevents a retry of an old selection from reverting a later
one. Tracking changes native UI metadata with no gameplay cost or time tick.
Disconnect/reset dismisses stale forms, requires authoritative recovery and
never replays tracking. Histories and selection persist in canonical CDDA
saves; menu/tab/pause state does not.

## Verification

- **170 native cases / 73,461 assertions PASS**: CWM, reading, disassembly,
  selected melee/ranged, NPC talk and native mission conditions. Focused
  journal/native mission coverage: **3 cases / 189 assertions PASS**.
  Queries preserve serialized player/missions, time, moves and RNG state;
  completion-condition callbacks are not evaluated. Watch and no-watch
  formatting, unsafe dynamic text, hidden missions, valid ID zero, stale
  selection and read-only completed/failed histories are covered.
- **309 client tests / 47 modules PASS**, plus 648 Catch assertions / 4 cases.
  Protocol **16/16**, launcher language **9/9**, registry **3/3** and the
  standalone journal presentation check PASS.
- **99 actual renderer/canonical checks PASS**: reconstructed journal 31,
  installed journal 31 and trade regression 37. Keyboard/mouse input through
  start.sh exercises
  the three tabs, time/position freeze, explicit selection, old-request replay,
  manual pause, connection replacement and fresh reopening. Independent
  pinned-core readback verifies saved selection, histories, assignment,
  unchanged position and no fabricated activity or newly created mission.
  The installed pair and the existing trade flow are checked separately;
  exact counts, screenshots and hashes are in the evidence.

[Exact source identities, commands, logs and binary hashes](native-journal-evidence.json).
Builds retain reconstruction caches; this is not a cold-build conformance audit.
Screenshots are inspected by the LLM agent, not counted as human acceptance.

The test-only fixture uses native saved-mission deserialization and assignment/
history APIs to prepare two active, one completed, one failed and one unaccepted
mission. This is not a claim that their quest lines were played to completion.
An early fixture lacked the native avatar-history event and legitimately
triggered CDDA's legacy-save migration, adding its faction-succession mission.
The fixture now records the event before preparing controlled histories;
production loading and journal membership were not filtered or changed to hide
that mission. Earlier fixture/API setup failures remain in local investigation
logs and are not counted as passing verification.

## Installed runtime and follow-up

The verified CWM2.30 Linux pair is installed in normal start.sh. Previous paired
binaries remain at `artifacts/native-journal-20261022/native-before-journal`
and `client-before-journal`. Developer worlds/preferences were not used.
Mapping batch60 is unchanged. The Windows installer remains its CWM2.26 snapshot.

**49 PENDING, no open manual FAIL**: four JOURNAL-01 checks added to the
[human ledger](../validation/pending-manual.md), previous 45 unchanged. No new
human PASS inferred and no manual gate required now. Next core slice:
individual companion commands/services. Full mission/mod/EOC lifecycle
coverage, safe recorded dynamic rewards and optional HUD/map navigation are
separate work. Historical **M5.5 FAILED** and full **SAVE-001 OPEN** are unchanged.
