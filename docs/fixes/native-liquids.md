# Native water sources and liquid pouring — 2026-10-23

Normal Linux **`./start.sh` now supports native water collection and pouring**.
Right-click an adjacent recognized source for the original native liquid menu:
collect into a carried container or drink, with native warnings and conditions.
In I select an owned liquid or its container and choose **Pour liquid...**.
`./liquids-demo.sh --fresh` provides an isolated pool, finite prepared source,
jerrycan and small bottles. Normal game sources retain their actual quality.

**Quantities, compatibility, capacity, seals, freezing and physiological effects
remain native.** A read-only source capability never calls map::water_from or
samples contamination. Explicit native examination can sample it before its
menu, as upstream does. Carried pouring can apply immediately and debit native
moves; the existing applied/time-remaining UI shows that uninterruptible cost.
Partial transfer is success and preserves the source remainder. No destination
or fake preselected amount is fabricated by the client.

Collection starts original ACT_FILL_LIQUID. I pauses and **Interrupt transfer**
uses native cancellation, retaining already transferred charges. Its semantic
state has a transient token and no invented percentage. Source/destination and
activity remain canonical through save/reload; reconnect does not start them
again. Ground directions disclose no terrain/furniture names. Source picking
checks at most the nine native nearby cells rather than scanning all water in
the cached world each render frame. [Detailed contract](../design/native-liquids.md).

CWM2.33 appends a liquid state, optional inventory metadata, typed cancellation
and POUR transfer action, retaining all eight old equipment action bits. Shared
view/item identities, command outcomes and connection fencing remain in use.
The local raw-water glyph now uses the attributed water icon instead of food
art; the previous clean-water correction and generated batch60 mappings remain.
The glyph is a type representation, not a detector of hidden poisoning.

## Verification

- **179 native cases / 73,677 assertions PASS** in the selected CWM, reading,
  disassembly, melee/ranged, NPC dialogue and mission suite. The six liquid cases
  cover 107 assertions: observational capability, native finite depletion and
  poison preservation, partial remainder/cost, cancellation/stale binding,
  seals/freezing/mixing and ground-choice privacy/full drain versus cancel.
- **309 client tests / 47 modules PASS**, plus 648 Catch assertions / four cases.
  Protocol **18/18**, language **9/9**, registry **3/3** PASS.
- **127 renderer/canonical checks PASS**: reconstructed collection
  38, actual fill restart
  12, installed collection
  38 and rest regression
  39. Actual start.sh input tests paused selection,
  interruption, capacity/remainder, old-POUR replay, incompatible containers,
  direct drinking, recovery, native fill restart and canonical completion.

The independent fixture/reader links only the **unmodified pinned CDDA core**.
Readback verifies ACT_FILL_LIQUID before restart, ACT_NULL after completion,
native inventory contents, unchanged position and an exact finite remainder of
28 charges (32 minus three filled and one drunk). Drinking produces 250ml in
native digestive state; the thirst number need not drop immediately. Images
were inspected by the LLM agent, not accepted by a human.
[Exact identities, commands, binary and log hashes](native-liquids-evidence.json).
Incremental captured reconstructions, not a cold build or whole upstream suite.

Investigation logs retain initial compilation fixes for native i_add's return
type and the engine's conflicting LIQUID_SOURCE name. A finite fixture was
initially frozen; a seal test used an insufficiently full bottle. The renderer
driver initially assumed instant thirst relief and a 20L jerrycan where the
native fixture has 10L. Corrected checks use actual digestive state and native
pocket capacity. No failed attempt is counted as final PASS. The final native
revision also removes ground-menu terrain disclosure and verifies both cancellation
and complete pouring with the native container retained.

## Installed build and remaining core

The verified Linux pair is installed in start.sh; its previous pair and receipt
are under `artifacts/native-liquids-20261023/`. **61 PENDING, no open manual
FAIL**: four new LIQ-01 checks in the [human ledger](../validation/pending-manual.md),
previous 57 unchanged. No human acceptance inferred from automated results.
The [human testing/authorship statement](../../HUMAN_TESTING.md) attributes earlier
manual PASS and general playtesting to the sole human developer. This delivery
report was written by an LLM following that developer's instructions.

The [minimum-core outlook](../progress/core-outlook-2026-10-23.md) records the
start-of-step estimate: approximately 94% (93–96%), excluding manual tests,
with roughly 2–5 substantial technical steps including uncertainty. Next:
essential sealed-container opening, liquid crafting/purification and native
item uses, then non-demo survival-loop, recovery/save and populated-performance
consolidation. Optional source handling does not solve mandatory crafting-output
recovery: liquid/gas results and byproducts remain gated. Vehicle tanks/fuel,
keg extraction, portable external-container pouring and arbitrary liquid amounts
remain separate. Native adjacent-keg filling remains an available destination.
Windows remains CWM2.26; historical M5.5 FAILED / full SAVE-001 OPEN are unchanged.
