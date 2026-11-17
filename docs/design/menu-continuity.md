# Continuous action menus

The developer accepted FB-01.1/2 and separately requested that related screens
replace one another without a brief return to gameplay.
[Human directive](../source/modal-continuity-feedback-2026-10-26.md).

A visible modal and native menu pause are separate states. Selecting an action
from I, external storage or K arms a presentation return target and replaces
the same live form with a waiting/progress view. Only that explicitly selected
native operation releases Menu pause while the window stays present. Native
decisions, manual/safety/recovery pause and canonical work remain authoritative.
No input, action cost, interruption or refund is inferred from elapsed UI time.

Native choices replace the action view in place. Responses wait behind the same
modal until the next choice or authoritative result. Completed work returns
directly to a refreshed inventory or crafting view, with Menu pause reinstated
before browsing. Search/batch context and native selection binding rules remain.
CWM handlers fence command, decision, connection and local action-view generations;
stale buttons cannot resubmit an old command. Input remains captured by the modal.

The action view offers **Pause and inspect**, also I. Inventory inspection can
pause while its ACK is still in flight; queries wait for the authoritative result.
Actual activities can then be interrupted through their existing native controls.
Atomic clothing mutations are already applied and cannot be undone; inspection
pauses their remaining native time rather than inventing a cancellable actor.
**Return to game** / Esc explicitly leaves and disarms automatic return, keeping
already admitted native work/debt. Before admission it may discard the unsent
selection, as the previous UI dismissal did. This explicit exit is distinct from
an involuntary flash between related screens.
The configured F7 pause and F8 speed shortcuts remain active in the action
view, with physical key-repeat fencing. Pausing there preserves its return
target; resuming completes the same native work and returns directly to the
originating menu. Changing speed while paused does not advance work.

Crafting joins the existing native observational InventoryWorkState identity.
This reports completion after native activity and remaining coordinator debt;
it does not change crafting choices, output, work, timing or save data. No CWM
fields or offsets change, but **CWM2.37** requires this completion guarantee:
both executables must match, rather than accept an older server that could
leave the new crafting return waiting for an absent identity.

Renderer changes reuse GUIFormSpecMenu rather than quit/create it between views.
Each replacement sets the appropriate close/input policy; a native decision's
non-closable flag must not leak into the following ordinary inventory. The
ActionMenuView is read-only and its renderer uses the shared theme, allowing
later styling changes independently of native command routing.

Recovery/death invalidates the transient return/action view. Reconnect still
requires an authoritative full snapshot and never replays a selected action.
Canonical saves own native activities/effects/items, not open windows or return
intent. The trace appends actual modal count and action-view state, so renderer
tests can check every sampled frame between related screens. Automated results
are separate from MENU-01.1 personal acceptance in the manual ledger.

## Reading/work follow-up — 2026-11-09

A spontaneous native decision also replaces the progress view. Its arrival
invalidates the cached progress rendering: after an answer, the same progress
text must still replace the submitted-decision view. Retaining a live modal
must never retain an obsolete waiting screen or turn it into a Menu pause.
The native No, Ignore and Stop choices keep their distinct CDDA semantics.

Closing inventory/crafting inspection while authoritative work is active now
returns to the same ActionMenu presentation used at its start. The bridge
observes the current activity or outstanding native work identity; it never
issues another start command. This also applies after Esc/Return to game hid
the panel and to canonical loaded activities without a transient start ID.
I opens paused inspection; closing it reopens progress. Esc/Return to game
can hide that panel again without cancelling work. Existing native pauses,
debt and cancellation rules remain. Explicit exit still disarms automatic
return until the player inspects and reopens the panel.

The reading title and theoretical-progress text come from the authoritative
reading projection in both cases. The legacy HUD progress overlay is hidden
while the ActionMenu is visible. Window replacement reuses the live modal,
including the inspection-to-work transition, without a gameplay flash.
