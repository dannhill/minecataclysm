# Native rest, sleep and waiting

B (keymap_cdda_rest) opens a native paused rest menu in normal start.sh. Idle
choices call the original avatar_action::sleep/wait menus, not copied sleep
logic. Confirmation, active-item warnings, optional save, comfort/mutations,
watch/heartbeat durations, alarms and vehicle/deep-water restrictions stay
native. Opening sleep may stop an active musical instrument before its native
confirmation, as upstream does; cancel does not undo native opening effects.

Waiting, trying to fall asleep and sleeping are distinct projected phases.
Only native interruptible wait/try activities offer Interrupt rest, calling
cancel_activity and native actor cancellation. Actual sleep offers no forced
wake: native alarms, needs, noise, damage and wake_up/narcosis rules own it.
No healing, stamina refill, successful sleep or wake time is invented. Attempt
and sleep have no fabricated percentage/countdown. Finite ordinary wait may
show its actual native counter percentage.

The CWM2.32 RestRequest opens this context, bound to the last projected rest
generation (zero idle). It uses the shared command ledger and existing native
decision IDs. A pending request is serviced only inside the external-choice
scope, including while activities/sleep omit the normal player-input callback.
Pause, recovery and connection loss reject pending requests; accepted outcomes
are cached without reopening old menus. Busy unrelated activities and unpaid
move/time debt cannot be replaced by sleeping. Gameplay/held movement is blocked
while asleep; held direction needs release before reuse after rest.

The coordinator uses the [single contextual F8 rate](unified-f8.md): ordinary
play cycles 0.5/1/2/4x; attempts, actual sleep and long waits cycle
1/4/64/256/1024/4096x, defaulting to 1024x. These are absolute alternatives,
never multiplied by an awake rate. B only manages native rest choices and
interruption; there is no second speed menu or warmup. Short waits keep the
awake rate. Leaving long rest restores the previous awake preference.
Every native turn, effect, AI update,
need, sound and alarm still executes; calendar time is never assigned forward.
The clock retains at most 32 native ticks of deliberate rest credit, bounds
wall stalls and drops unused acceleration budget when paused
or returning to normal play. This is rest-specific, not global long-activity
acceleration. Visible new threats pause aware waiting/attempts through the
existing safety path; sleep retains native sensory limits and disturbances.

During accelerated rest, unsolicited projections are limited to ten per wall
second. Full recovery, decisions, command results and phase changes bypass the
limit. Projection-cache comparisons span the last emitted canonical state;
revision/sequence validation and full resync are unchanged. Publication rate
never changes native turns or creates inferred client state.

RestState carries a transient token, phase, interruptibility, acceleration and
honest finite-wait progress. Canonical activities, effects, alarms and posture
are saved only by CDDA. Menu pause, generation IDs and acceleration preference
are not canonical save fields. Save/reload/reconnect preserves real work/sleep
without issuing another start command. Normal UI gives a readable sleep/rest
status even when native sleep removes visual perception.
As of CWM2.36 the deprecated wire multiplier is always 1; clock state carries
the effective rate and explicit PLAY/REST context.

English remains default, Italian WIP uses shared catalog fallback. Windows
installer remains its earlier snapshot until a dedicated rebuild. Historical
M5.5 FAILED and full SAVE-001 OPEN remain independent unresolved gates.
