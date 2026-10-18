# Pause-menu language selection in darkness

The human developer reported that English closes Esc and the next start.sh
still uses Italian. The current installed runtime reproduced that exact failure.
[Human report](../source/language-regression-2026-10-18.md),
[exact verification and installation](pause-language-menu-evidence.json).

The cause was presentation hit testing, not native language persistence. The
fullscreen low-light tint is a disabled root-level Irrlicht widget. Disabled
widgets still participate in getElementFromPoint; reused menus could remain
behind it. The bridge hid it for its own inventory/body/crafting/decision forms,
but did not recognize the engine pause menu. An intercepted click was remapped
by GUIModalMenu::remapClickOutside to Escape. The language callback received no
button, and the unchanged preference correctly remained Italian. The diagnostic
captured only quit with low_light=1/low_light_blend=1; its temporary input logging
was removed before the final build.

The game now passes the actual menu-manager state into bridge overlay rendering.
While any modal menu is open, all passive bridge GUI widgets and HUD icons are
hidden; their ordinary native-derived visibility returns on close. This covers
engine menus too and prevents tint or another passive overlay stealing a button.
Native illumination, perception, time, gameplay and language-selection rules are
unchanged. English/Italian clicks stay in the menu with time frozen, write the
normal supervised configuration, and apply to both components after restart.

Scoped checks PASS: 309 client tests / 47 modules and 648 Catch assertions / 4
cases; 9 language-resolution/launcher tests; **75 renderer/canonical checks**.
The renderer checks cover Italian → English and English → Italian under actual
native low light, hidden HUD, a still-open pause menu, frozen time, unchanged
current-session translation, saved preference, unchanged native options and
exact native possessions. The installed ordinary start.sh then loads the actual
saved English preference without CDDA_LANGUAGE, exports English native names
and dialog choices, and accepts a further Italian choice. A pristine pinned-CDDA
reader independently loads all three isolated output saves. No user world was
used for these tests.

The client was captured and built incrementally in an owned reconstruction,
with Release/LTO/audio enabled and retained caches; this is not a cold build.
Only the verified client was installed; CWM 2.25 and the native executable/data
are unchanged. Its previous executable is retained as
`artifacts/language-menu-20261018/client-before-fix`. Artifacts, sources, build,
commands, screenshots, binary hashes and initial failures are in the receipt.

The developer explicitly wants English. After verifying the installed restart,
the normal `user/cdda/config/presentation-language.conf` was set to English
using the existing atomic presentation helper, with its previous preference
backed up in the artifact folder. Native options were checked unchanged. No
canonical world/save was rewritten for this setting. An already running client
keeps its startup language: exit completely and relaunch `./start.sh`.

Manual status: **28 PENDING + 1 human FAIL**, LANG-01.2 reopened for the new
regression. The scoped repair is automatically verified; that does not turn it
into a human PASS. The [ledger](../validation/pending-manual.md) requests only
this focused personal recheck; older human PASS entries remain historical.
Full SAVE-001 stays OPEN and historical M5.5 FAILED. This UI repair adds no new
feature or protocol milestone and does not recertify unrelated components.
