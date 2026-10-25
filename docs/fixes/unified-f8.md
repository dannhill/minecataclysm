# Single contextual F8 and recovery-demo startup — 2026-10-25

Linux `start.sh` now uses the paired CWM2.36 runtimes. The
[developer's human feedback](../source/unified-f8-feedback-2026-10-25.md)
accepted FB-01.3/4, reported that the recovery demo could not start, and
requested a single time-speed feature.

The recovery demo passed `liquid_recovery_demo`, 20 bytes, while Luanti permits
19. Native CDDA loaded successfully but the client rejected the name before
gameplay. It now uses `recovery_demo`. Prior renderer tests replaced the alias
with their own valid test name and missed this real entry-point defect. The
new regression runs `liquid-recovery-demo.sh --fresh` without that override;
three launcher tests also compare its argument with the actual engine limit.
Private test session namespaces leave the developer's demo pointer/world alone.

F8 is the sole absolute pacing control:

| Context | F8 cycle |
| --- | --- |
| Awake / short wait | 0.5, 1, 2, 4x |
| Sleep attempt, sleep, long wait | 1, 4, 64, 256, 1024, 4096x |

Long rest initially uses 1024x, the previous default's effective target. It
remembers its last contextual rate while the server runs. Leaving it restores
the previous awake rate. B only manages native rest/interruption; the separate
multiplier and warmup are removed. The HUD shows one target and an amber
REST FAST-FORWARD label above 4x. Simulation load can limit actual throughput.
Native turns, AI, effects, needs, alarms, sleep duration and waking still run
normally. Pause/context change/deceleration drop unused fast tick credit;
native work/action debt remains. [Detailed contract](../design/unified-f8.md).

## Verification and installation

- **185 native cases /73,766 assertions PASS** in the selected CWM, reading,
  disassembly, melee/ranged, NPC dialogue and mission suite; the focused native
  menu/context case passes **14 assertions**.
- **309 client tests /47 modules PASS**, plus **648 Catch assertions /4 cases**.
  Protocol **20**, launcher **3**, language **9**, registry **3** PASS.
- **119 renderer/canonical checks PASS**: reconstructed public demo 20, rest
  46, night 9, installed public demo 20, installed sleeping-save restart 24.
  Actual renderer tests exercise the public recovery script, cursor continuity,
  pouring and empty-can pickup, both F8 contexts and every cycle value, awake
  restoration, pause, reconnect, night sky and canonical sleeping-save restart.
  An independent reader linked to unmodified pinned CDDA reloads the resulting
  saves; no private user world is opened. Source and binary identities,
  per-scenario check counts and log hashes are in the
  [evidence receipt](unified-f8-evidence.json).

Builds are incremental captured reconstructions with isolated configuration,
not cold-build conformance or the entire upstream suite. Native/client binaries
are copied as a matching pair after successful reconstruction checks, verifying
the previous installed hashes and preserving both old executables. Installed
verification repeats the actual public entry point and loads the sleeping save.
Screenshots were inspected by the LLM agent, not accepted by a human.

The first revised rest GUI driver attempted another menu before a native paid
turn settled at the deliberately slower awake 2x. Native rejection was correct:
the test now waits for simulated time to settle instead of a fixed 0.3 seconds.
That failed driver run remains in artifacts and is excluded from PASS totals.
No production gameplay was changed to bypass the debt check.

## Human ledger and next work

Subsequent human retry, 2026-10-26: **FB-01.1/2 PASS**, confirming both repairs
and closing the startup failures below. UF8-01.1 remains pending. A separate
[menu-transition report](../source/modal-continuity-feedback-2026-10-26.md)
requests continuous presentation; the delivery-time counts below are historical.


FB-01.3/4 remain human PASS of the previous build. FB-01.1/2 remain startup
FAIL until the developer retries the repaired demo. UF8-01.1 covers the revised
F8 design: **58 PENDING +2 startup FAIL**, 60 points awaiting personal acceptance.
Automated success does not close personal tests.
[Manual ledger](../validation/pending-manual.md) · [testing/authorship](../../HUMAN_TESTING.md).
This report is written by an LLM following the sole developer's direct instructions.

Next core work remains essential native item uses, safe liquid outputs and
purification, then non-demo survival-loop/recovery/performance consolidation.
Mapping batch60 is unchanged. Windows remains CWM2.26; historical M5.5 FAILED
and full SAVE-001 OPEN are unchanged by this scoped repair.
