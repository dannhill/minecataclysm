# Single contextual time speed — CWM2.36

The sole developer requested [one speed feature](../source/unified-f8-feedback-2026-10-25.md)
after accepting the old sleep function. F8 now selects the single absolute
native coordinator target, measured in simulated seconds per real second.

| Native context | F8 cycle | Initial preference |
| --- | --- | --- |
| Ordinary play, including short waits | 0.5, 1, 2, 4x | 4x in normal start.sh |
| Trying to sleep, sleeping, waits of at least 30,000 moves | 1, 4, 64, 256, 1024, 4096x | 1024x |

The last rate in each context is remembered only by the running coordinator.
Entering long rest selects its alternative rate; leaving it restores the
previous awake rate. These values never multiply. Reload reconstructs the
canonical native rest state, not menu pause or saved speed preferences.
There is no eight-second warmup or second B speed selection. B retains native
sleep/wait/interrupt choices; actual sleep has no invented forced-wake action.

The rest HUD labels the one selected rate as F8 REST FAST-FORWARD above 4x,
in amber, or F8 TIME SPEED at lower rates. The number is a target rather than
guaranteed throughput. Simulation cost can limit it. I/Esc still pauses the
same clock and all native work; creature movement and action authority stay
with CDDA.

Every native turn executes. Deliberate accelerated rest retains at most 32
native tick credits; normal play keeps its stall-discard policy. Pausing,
changing context or decelerating drops unused accelerated credit without
refunding paid or unpaid action/work debt. Native AI, effects, needs, alarms
and waking are never skipped. Unsolicited accelerated-rest publication remains
bounded to ten per wall second; recovery, decisions, completion and phase
changes bypass that limit.

The protocol appends PLAY/REST context to clock state and speed requests.
Stale context requests and unknown values are rejected. The ledger includes
context in command identity, and validation restricts rates by context. The
legacy multiplier field is retained for FlatBuffers offsets but emits and
validates only 1. No renderer types or new canonical save fields are added.

The public recovery demo also uses the valid 13-byte alias `recovery_demo`.
The previous `liquid_recovery_demo` exceeded Luanti's 19-byte player-name limit
and prevented its window from starting. Automated renderer validation must
exercise `liquid-recovery-demo.sh --fresh` without overriding that name.
An isolated test namespace under artifacts keeps the developer's demo session
pointer and canonical saves untouched.

Personal FB-01.3/4 remain PASS of the reviewed build. FB-01.1/2 remain recorded
as startup failures until the developer retries them; revised F8 behavior has
its own UF8-01.1 check in the [manual ledger](../validation/pending-manual.md).
Automated verification never supplies human acceptance.


Subsequent human retry (2026-10-26) confirmed FB-01.1/2 PASS and closed their
startup failures. The [new menu directive](../source/modal-continuity-feedback-2026-10-26.md)
retains those validations; UF8-01.1 is still a separate pending check.
