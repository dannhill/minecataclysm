# Selected language in the pause notice

The sole human developer confirmed that language-selection/persistence now works,
then reported that the fixed “Restart start.sh / Italian: WIP” note was misleading
after choosing English. [Human confirmation](../source/language-notice-feedback-2026-10-18.md).
That acceptance closes the previous LANG-01.2 FAIL; it does not personally validate
this subsequent wording change.

The pause form source now observes the selected product-language setting. It
refreshes its presentation only when that selection changes, using the existing
safe next-frame formspec refresh. A matching language says **Active: English**
or **Attiva: Italiano (WIP)**. A different selection says **Next start / Prossimo
avvio** and names the selected language, with a restart instruction. The separate
incomplete-translation note appears only for Italian. Notice wording remains in
the session language until a supervised restart. The menu stays open and native
time remains paused; no live translator, protocol or native-save change is added.

After the first functional pass, agent inspection found an unnecessary scrollbar.
The final notice is shorter with a larger text area; two additional focused GUI
runs recheck the final layout and modal controls, without repeating unchanged
native canonical checks.

The exact verified client is installed in the normal start.sh path; an existing
process must be closed/relaunched to load that binary. The previous client is
retained in `artifacts/language-notice-20261018/client-before-notice`. The native
runtime, CWM 2.25, language persistence helper and item mapping are unchanged.
This follow-up does not rewrite the developer's language preference or native
options/worlds.

Scoped PASS: 309 client tests / 47 modules, 648 Catch assertions / 4 cases,
9 language tests, **56 functional renderer/canonical checks**, then **42 focused
final GUI checks**. Both startup languages cover
selection, an immediately different rendered notice, return to the original
active notice, another selection using the regenerated buttons, preserved pause,
unchanged current-session native text and persisted final choice. Screenshots
were also inspected by the agent; this is not human acceptance. A pristine
pinned-CDDA reader loads both isolated output saves and verifies possessions and
unchanged native options. Reconstructed incremental Release/LTO builds retain
caches; no cold-build or new global certification is claimed. The installed copy
is hash-checked against the tested executable; no extra installed renderer run
was needed for this presentation-only follow-up.

[Exact evidence, source and binary identities](language-selection-notice-evidence.json).
The [manual ledger](../validation/pending-manual.md) has **29 PENDING, no open
manual FAIL**: the previous 28 unchanged plus one optional notice-readability
recheck. Full SAVE-001 remains OPEN and historical M5.5 FAILED. Native disassembly
remains the next functional core slice.
