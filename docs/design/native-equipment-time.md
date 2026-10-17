# Native equipment time and inspection

Decision: the user explicitly chose native clothing semantics on 2026-10-18,
after asking to inspect CDDA before adding interruption.

At pinned CDDA `2478ae876eb1439be387d0e117808d33c9d6afa4`, ordinary Wear
calls `Character::wear`/`outfit::wear_item`: apply the garment and subtract
`item_wear_cost`. Take off calls `takeoff(location.obtain(u))`: obtain charges
native handling/removal cost, then removes the garment atomically. These are
not partially completed, cancellable single-garment actors. ACT_WEAR can
process a selection across turns, but each garment still uses atomic
`wear_item`; stopping remaining work does not undo garments already applied.

Keep those native operations, costs, outcomes and canonical saves unchanged.
The existing CWM InventoryWorkState reports coordinator time debt, not an
ongoing dressing activity. Show remaining **game seconds** and that the action
is already applied/cannot be undone. Reserve percentage/progress bars and
Interrupt for actual native activities that expose an activity token.

I must open inspection and send MENU_OPEN even if the equipment result has
not reached the client. Defer the read-only inventory query until that command
settles, so the view cannot retain the pre-action garment. A command not yet
executed can be rejected by the existing native pause policy. Never report it
as applied merely because it was sent. Preserve work tracking across inspection;
close resumes the same native debt. Manual inspection suppresses automatic
return, and Esc outside the menu only hides feedback. Pause freezes time; it
does not refund moves or reverse a committed garment. Native actor cancellation,
recovery and stale-command rejection retain their existing semantics.

No protocol, save schema, simulation duration or gameplay rule changes.
Verify real renderer input with a delayed equipment reply, atomic garment
state, frozen/resumed authoritative time debt and canonical item conservation;
also recheck actual treatment interruption. Personal acceptance stays deferred.
