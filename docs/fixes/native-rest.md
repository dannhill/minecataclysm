# Native rest, sleep and waiting — 2026-10-23

Normal Linux **`./start.sh` now supports B**, configurable as
`keymap_cdda_rest`. Try to sleep / Wait or catch your breath call the original
CDDA actions and their native menus: confirmation, optional save, active-item
warnings, watch/heartbeat durations, alarm choices, terrain/vehicle restrictions
and character-specific rules remain native. `./rest-demo.sh --fresh` opens an
isolated tired character on a bed, without a watch or nearby hostiles.

Waiting, trying to fall asleep and actual sleep are distinct. B can interrupt
native interruptible wait/try activities. Actual sleep has no free forced-wake
button: alarms, disturbances, needs, damage and narcosis follow CDDA. I/Esc
pauses the real-time world; held movement, posture, aim and quick-use cannot
replace sleep or replay afterwards. The HUD shows the actual phase and only a
finite native wait counter has a percentage. Its key hint follows the configured
rest binding. B no longer collides with the upstream default hotbar-previous
binding; that optional binding remains configurable.

Long rest can run with a 64x pacing multiplier after eight simulated seconds;
short waits remain normal. B switches normal/fast speed. **Every native turn
still executes**, including AI, effects, needs and alarms; actual throughput is
limited by simulation cost. Pause, recovery and return to normal drop excess
pacing credit rather than creating catch-up bursts. Accelerated unsolicited
state publication is limited to ten per wall second; decisions, completions,
phase changes and full recovery bypass that limit.

CWM2.32 appends a rest request and semantic rest state, sharing the command
ledger and native choice IDs. Stale generations are rejected. A request arriving
during recovery receives an explicit rejection rather than silently remaining
pending. Unpaid native actions cannot be replaced by sleep. Accepted command
replay returns the cached outcome without opening the old menu. Canonical
activities, effects, posture and alarms remain native save data. Menu pause,
transient generation IDs and acceleration preference are not saved.
[Detailed contract](../design/native-rest.md).

## Verification

- **173 native cases / 73,570 assertions PASS** in the selected CWM, reading,
  disassembly, melee/ranged, NPC dialogue and mission regression suite. The two
  rest cases cover 44 assertions: observational cancellation, distinct phases,
  native interruption, pacing warmup, real effect-expiry wake-up and narcosis.
- **309 client tests / 47 modules PASS**, plus 648 Catch assertions / four cases.
  Protocol **17/17**, language **9/9**, registry **3/3** PASS.
- **129 actual renderer/canonical checks PASS**: reconstructed rest
  39, reloaded sleep 22,
  installed rest 39 and companion regression
  29. Actual start.sh keyboard/mouse input
  checks native confirmations, short waits, I pause, interruption, command
  replay, actual sleep, blocked movement/posture, acceleration, reconnection,
  canonical readback and restart without a new sleep command.

An independent reader links only the **unmodified pinned CDDA core**. It creates
an awake tired fixture, then reloads the resulting saves to verify a positive
native sleep effect, ACT_NULL (not invented sleeping work), prone posture and
unchanged position. Screenshots were inspected by the LLM agent; they are not
personal human acceptance. [Exact source, commands, binary and log hashes](native-rest-evidence.json).
These are incremental captured reconstructions, not a cold-build audit or the
entire upstream test suite.

Investigation logs retain an initial expression/include compilation fix, a
wrong data-directory test invocation, refresh refusal while docs were dirty,
the original B/hotbar collision and posture request flooding during sleep.
The renderer driver also needed to wait for the full-state acknowledgement
and recovery pause before sending fresh input. Final runs use those fences;
failed attempts are not counted as passing evidence. The final client also
corrects the rest-specific Esc hint and uses the configured rest key.

## Installation and next step

The verified Linux pair is installed in start.sh. Its previous paired binaries
remain under `artifacts/native-rest-20261023/` with an installation receipt.
**57 PENDING, no open manual FAIL**: four REST-01 checks added to the
[human ledger](../validation/pending-manual.md), prior 53 unchanged. No human
PASS inferred from automation. The ledger's earlier PASS records and broader
playtesting belong to the sole human developer; [authorship/provenance](../../HUMAN_TESTING.md).
This delivery report is written by an LLM following the developer's instructions.

Next core slice: essential liquid sources/transfers and missing item uses,
then consolidated non-demo survival loops and populated performance checks.
General activity acceleration, every alarm/trait/disturbance combination and
advanced NPC services/camps remain separate. Ordinary real-time start.sh was
verified; the unpaced comparison bootstrap still waits for a queued gameplay
action before servicing a rest menu, and is not certified for this feature.
Mapping batch60 is unchanged;
Windows remains the earlier CWM2.26 installer. Historical M5.5 FAILED and full
SAVE-001 OPEN remain unchanged.
