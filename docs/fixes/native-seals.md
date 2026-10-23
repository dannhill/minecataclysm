# Native sealed pocket opening — 2026-10-23

Normal Linux **`./start.sh` now exposes Open sealed pocket...** in I when an
owned container has a sealed native CONTAINER pocket. Choose the pocket to
open or Cancel. Opening an outer sealed container is required before its nested
pockets. `./seals-demo.sh --fresh` provides three isolated sealed containers.

The explicit operation is an integration adaptation of the native
`contents_change_handler` prefix used by CDDA item actions. **Pinned CDDA has
no separate pocket-opening activity or extra opening move charge.** This
interface adds neither. Native retrieval, eating and pouring keep their own
costs. Tool-dependent item transformations remain separate; this does not
promise every sealed item can be opened without its required tool.

Native code owns seal changes, preservation multipliers, restacking, spilling
and placement on the ground. First Cancel leaves the seal intact. Cancelling a
later liquid-handling choice cannot restore a broken seal: CDDA may place the
open container on the ground while keeping its contents. Opening alone neither consumes nor fabricates contents; further liquid
choices retain their native effects. No automatic resealing is exposed.

CWM2.34 appends optional SealInfo and OPEN_SEAL=5, keeping the eight old
EquipmentAction bits and all previous field/union offsets. Existing inventory
identity, position/ancestor checks, pause/work admission and command ledger
remain. Pocket seal state is now part of the binding. The client queues the
operation after menu pause closes and refreshes the authoritative inventory;
Pour replaces Open once the selected pocket no longer needs opening.
[Detailed contract](../design/native-seals.md).

## Verification

- **183 native cases / 73,740 assertions PASS** in the selected CWM, reading,
  disassembly, melee/ranged, dialogue and mission suite; four new seal cases /
  63 assertions cover cancellation, costs/RNG, stale identities and seal state,
  nested barriers and the actual native spill/drop policy.
- Client **309 tests / 47 modules**, 648 Catch assertions / four cases PASS.
  Protocol **19**, launcher language **9**, registry **3** PASS.
- **111 renderer/canonical checks PASS**: reconstructed opening
  29, real saved-state restart
  15, installed opening
  29 and installed liquids regression
  38. The real client issues commands,
  cancels/opens, repeats accepted command packets and replaces the connection.
  Independent pinned-CDDA readback preserves distinct open/sealed states,
  carried quantities and the open can on the floor with its remaining liquid.
- Incremental captured source builds, isolated canonical saves/configuration;
  actual Luanti renderer under private Xvfb/Mesa, representative screenshots
  inspected by the LLM. Automated verification is **not human acceptance**.

Exact commits, fork inventories, binary/log/readback hashes and commands:
[native-seals-evidence.json](native-seals-evidence.json). Production source
capture `cc0d295966b16472bbbfef1cb1674d280aa1445e`, renderer harness `6f2361e35dfa0546d752cc718cb5e6823fbde2d8`. Both
normal Linux runtimes installed together; previous binaries retained in
`artifacts/native-seals-20261023/`. No user's existing save was opened.

## Deferred acceptance and next scope

**65 PENDING**, no open manual FAIL: prior 61 unchanged plus four SEAL-01
checks in [the manual ledger](../validation/pending-manual.md). No new human
PASS has been inferred. English defaults and the extensible language registry
remain; Italian WIP text is included. Generated mapping batch60 is unchanged.

Next bounded work: essential item activation, safe liquid-output recovery and
purification/crafting, then consolidated non-demo survival-loop, persistence,
recovery and populated performance. External portable-container opening, all
NPC services/camps/vehicles and final artwork do not become core prerequisites.
The Windows installer remains CWM2.26. Historical M5.5 FAILED and full SAVE-001
OPEN are unchanged; this scoped delivery does not certify those broad gates.

This report was written by an LLM acting on the sole developer's instructions.
Manual PASS/FAIL and general playtest feedback belong to that human developer;
see [the authorship/testing notice](../../HUMAN_TESTING.md).
