# Playtest feedback follow-up — 2026-10-25

Historical CWM2.35 delivery. The later [single contextual F8 and launcher
repair](unified-f8.md) supersedes its independent rest multiplier/B speed menu
and fixes the public recovery-demo alias. The original evidence below remains.

Normal Linux **start.sh now uses CWM2.35** with the following scoped repairs:

- Native long rest offers x64/x256/x1024 (default x256) in B and normal speed.
  The HUD distinguishes warmup/normal/fast and shows F8 × rest factor = target.
  Deliberate fast rest retains at most 32 native-tick credits instead of losing
  accrued budget after each lagged tick. Every tick, need, AI phase and waking
  rule remains native; actual throughput depends on the world/CPU.
- Open cans set on the floor after native cancelled spill handling can now be
  selected in the external view and drained via Pour liquid... into an owned
  compatible container. The empty can is then an ordinary pickup. Range,
  perception, ownership, seals, phases, capacities and real costs remain native.
- CWM menu transitions retain normalized pointer position. Confirmation labels
  remove terminal full stops/trailing whitespace while native wire choices,
  numeric IDs, questions, ellipses and narrative remain semantically unchanged.
- DecisionModel now holds question/choice identity independently from the
  DecisionDialog renderer. Inventory, transfers, crafting, trade, journal and
  decisions share a panel/button theme entry point for future visual replacement.
- Sky follows the native clock rather than fixed presentation noon, including
  during pauses. Legacy TimeOfDay packets cannot overwrite it. Native terrain
  illumination/perception remains unchanged. The midnight scene shows stars
  and a dark sky, verified by rendered pixels and screenshot inspection.

[Detailed contract](../design/playtest-feedback-2026-10-25.md).
`./liquid-recovery-demo.sh --fresh` includes the can and an empty glass bottle;
`./night-demo.sh --fresh` provides a native midnight scene with an opening above
its player. Normal `./rest-demo.sh --fresh` keeps the native sleep fixture.

## Verification

**185 native cases /73,766 assertions PASS** in the selected CWM, reading,
melee/ranged, disassembly, dialogue and mission suite. The two new focused cases
pass **26 assertions**, covering native rest preferences without unpaid game
changes and pouring from a real open ground can with native debit and contents.
Protocol **20**, client **309 tests /47 modules** plus **648 Catch assertions /
four cases**, language **9** and registry **3** PASS.

**138 real-renderer/canonical checks PASS** across reconstructed recovery,
rest and midnight plus all three installed-pair runs. They cover pointer
continuity, real liquid transfer/empty-can pickup, actual sleep, explicit
factors, pause/reconnect, rejection of legacy sky-clock rewrites and independent
pinned-core canonical readback. Final installed screenshots are checked by the
LLM; these automated runs are not personal acceptance by the developer.

[Exact evidence](playtest-feedback-2026-10-25-evidence.json) records capture
commits, source inventories, binaries, logs, command lines and excluded setup/
pre-fix failures. Native capture `47f4227226e25f89f1469daa21bb217b35b807ca`; final client
capture `b112e6865dbc96a0a10184f5627b9cf9ebfe1364`. Incremental captured builds, isolated
saves/configuration, actual Luanti under private Xvfb/Mesa. Previous normal
Linux binaries are retained in `artifacts/playtest-feedback-20261025/`.
The developer's existing worlds were never opened by verification.

## Human feedback and remaining work

The developer's **SEAL-01.3, REST-01.2, REST-01.3 and DIS-01.3 PASS** are
recorded from the [human message](../source/manual-rest-recovery-feedback-2026-10-25.md).
61 previous pending checks minus those four =57; four new FB-01 checks for
these repairs make **61 PENDING**. Earlier liquid/seal PASS results remain.
No human acceptance of the repairs is inferred from automated results.

Next core implementation remains essential item uses and safe mandatory liquid
output/purification, then non-demo loop/recovery/save/performance consolidation.
This is no complete UI redesign, universal liquid handling, vehicle delivery or
cold conformance audit. Mapping batch60 and the Windows CWM2.26 snapshot are
unchanged. Historical M5.5 FAILED / full SAVE-001 OPEN remain unchanged.

This report was written by an LLM following the sole developer's instructions;
manual PASS/FAIL and general playtests belong to that human developer.
See [the testing/authorship statement](../../HUMAN_TESTING.md).
