# Rest, slow rates and repeated synchronization failure — 2026-11-15

This report is written by an LLM from the sole developer's direct feedback and
local source/runtime investigation. The three PASS results and REST-01.1 FAIL
below are human results. Automated checks are agent-run evidence, not human
acceptance or a whole-game certification.

The developer reports repeatable wait/breath failures at0.5x/1x/2x, apparently
absent at4x, with I pause/resume and B interruption working. Accept direct
loose-stack pickup2, JOURNAL-01.2 and DIS-01.2 as human PASS. The ledger now has
**35 PENDING +1 FAIL =36 unresolved cases**; no new manual test is added.

## Captured cause and minimal repair

The real runtime logs reject a structurally received WorldSnapshot with
valid_world=0, then reject full recovery states repeatedly. A private copy of
`artifacts/rest-demo/session-h6sd_sq6/user` reproduces the initial full-state
failure on the previously installed native/client pair. The native canonical
save contains an ACT_WAIT_STAMINA and16 monsters, including creatures outside
perception. The first snapshot has17 actors and the contextual rest rate1024x.
Each nonplayer actor has motion_seconds=1/1024=0.0009765625; the established
protocol minimum is0.01. The unchanged validator rejects that field.

Ordinary rate selection and the contextual long-rest rate are alternatives,
not multiplied speeds. Correlation with the selected ordinary rate alone does
not explain every possible sync failure. The captured failure specifically
proves an accelerated-rest projection defect once other creatures are loaded;
empty-creature fixture success did not exercise it.

`cwm_map_exporter.cpp` now clamps only the nonplayer visual interpolation
duration to the existing0.01–60-second wire limits. Native turns, positions,
speed selection, visibility, protocol validation and canonical saves are
unchanged. Both full recovery and ordinary deltas use the same correction.
The client binary is unchanged from the verified Nov9 delivery.

The new native regression exports player/NPC/monster rosters as full state,
live delta and recovery at all ordinary rates and all contextual rest rates,
checking semantic validity and absence of native position/time/stamina mutation.
The renderer driver adds `--rate-check` for real waits, cancellation, I pause,
manual-pause reconnect, completion and contextual breath recovery. It explicitly
loads Audit Survivor; an accidentally generated world is not fixture evidence.

## Delivered verification

Runtime source capture: `aaa88d1eed4b6edf59816779f4f98782e60120a3`, private
snapshot in `artifacts/rest-rate-feedback-20261115/source-final`. The capture
includes pre-existing local changes; root branch/HEAD are untouched. Component
sources were refreshed into owned reconstructions with inventory/pin/blob
checks. Builds are incremental with retained caches, not a cold audit.

- Native selected suite: **186 cases,74,099 assertions PASS**.
- Protocol SDK: **21 tests PASS**, wire remainsCWM2.37.
- Actual renderer/canonical checks: **130 checks in6 runs PASS**. Four rates
  0.5/1/2/4, the copied failed save, and a final run on the installed pair.
- Each run saves through native CDDA and is read back with the independent
  pinned-core reader. Position and expected completed native activity checked.
- Three simulated seconds measured from unpaused renderer traces take
  5.9967/2.9755/1.5329/0.7499 real seconds at0.5/1/2/4 respectively; the nominal
  values are6/3/1.5/0.75. These samples establish the exercised rate behavior,
  not a general performance guarantee.
- The copied failed save now exports all17 actors, completes breath recovery,
  reconnects under manual pause and never replays the loaded rest command.
  All post-fix captured projections pass the unchanged semantic validator.

The verified native binary was installed atomically for normal `start.sh` and
all demos. Its previous version is retained under the artifact directory.
Close/relaunch an already running game to use the new executable. Exact binary,
source, test, capture and reader hashes are in the
[evidence record](rest-rate-feedback-2026-11-15-evidence.json).

## Human gate and remaining scope

REST-01.1 stays **FAIL awaiting human retry**. Previous PASS scenarios remain
accepted within their tested scope. The next checks are ordered by shared
foundations: **REST-01.1 → JOURNAL-01.3 → NPC-01.2 → LANG-02.1**.
[Detailed instructions and stop conditions](../source/manual-priority-tests-2026-11-15.md#quattro-controlli-in-ordine-di-dipendenza).
Do not spend downstream testing effort while its prerequisite is failing.

No original developer world was modified; all game/readback runs use isolated
copies. Early harness attempts with the wrong fixture parent or a too-short
transient observation are excluded and retained in the evidence. This scoped
repair does not close historical M5.5 FAILED, full SAVE-001 OPEN, LIQ-FB-01 or
other pending feature work. The older Windows package is not rebuilt here.
