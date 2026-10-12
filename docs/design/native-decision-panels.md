# UX-04A — Native choice panels and operation feedback

User requests readable clickable confirmations, native choices, clear work
feedback and continued deferred manual checks. This slice replaces the static
numbered text overlay with a Mineclonia-style panel: native text with safe colour
markup, scrollable reading/choice areas, full-label tooltips, mouse buttons,
physical 1–9 shortcuts and explicit native Esc cancellation.

CWM 2.20 appends DecisionPrompt.cancel_choice (default -1). CDDA exposes its
existing safe last-option fallback, including native paged lists. Luanti never
infers cancellation, medicine or danger from translated labels. Generic
panels preserve ASCII/body-choice information as native text; typed medical
body icons/hearts/known effects remain UX-04B, not claimed delivered here.

Every handler binds the current native decision and connection. Only one
response is sent; the panel remains in a waiting state until a native state
clears Decision or supplies the next prompt. Menus/read-only inspection do
not approve, heal, consume or improve aim. Return never silently confirms.
A physical key latch is observed before menus consume input, preserving release
requirements across consecutive prompts, menu generations and reconnection.
Esc selects only the advertised native cancellation index. Missing or invalid
metadata never causes a guessed choice. Lost peer/resync discards the panel;
CDDA retains its existing fallback policy.

Native inventory work retains its paid-completion gate. The temporary panel
shows operation/item, native progress only when available, and clearly labels
I as inspect/pause. Closing inspection resumes work; Interrupt cancels through
the native actor. Returning inventory reports that native work ended, without
claiming a successful item move or heal from an initial ACK. Capacity/rule
rejections remain visible in the inventory.

No new gameplay, duration, auto-confirmation, native save field, audio event or
medical inference is introduced. English defaults; Italian WIP uses the shared
presentation helper/native gettext. Test actual renderer and canonical saves;
keep manual acceptance and full SAVE-001/M5.5 separate.
