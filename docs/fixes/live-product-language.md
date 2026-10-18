# Live product language and extensible locale registry

The sole human developer accepted the previous notice and requested language
changes without restarting the game, then explicitly required an architecture
that makes additional languages easy to add. [Directives](../source/live-language-feedback-2026-10-18.md).

Esc now applies the selected language to the running native runtime and client.
A correlated presentation request is acknowledged by CDDA before client text,
engine gettext and the stored preference change. CDDA invalidates translation
caches and republishes labels without a turn or canonical option/save write.
The whole pause form regenerates on its next draw, retaining pause and buttons.
A native decision already open is never replayed to translate its entry effects;
new questions use the selected language after the current decision is answered.

The [shared registry](../../localization/languages.json) owns language codes,
endonyms, native/engine locale mappings, catalogs and completeness. Generated
C++ metadata, main-menu labels and setting choices come from that registry;
Esc derives its choices from it and can scroll. New integration languages use
JSON catalogs with English per-message fallback. Existing inline Italian strings
are a compatibility fallback; new languages require no third C++ argument or
wire enum. [Adding a language](../../localization/README.md),
[complete contract](../design/product-language.md).

CWM **2.26** requires the two rebuilt runtimes together. Both are installed in
the normal `start.sh` paths, with hash-checked rollback copies in
`artifacts/live-language-20261018/`. An existing process needs one quit/relaunch
to load this delivery; subsequent language changes do not require a restart.
The installation leaves the developer's worlds/preferences and mapping batch60
untouched. A menu preference persists on orderly launcher exit.

Scoped PASS: **114 native cases / 65,738 assertions**, plus an isolated native
language case with 14 assertions; **309 client tests / 47 modules**, 648 Catch
assertions / 4 cases; **13 protocol**, **9 launcher** and **3 registry tests**.
The registry tests generate/compile a temporary third locale, including catalog
fallback and menu/setting metadata; they do not enable or visually certify a
third game language. **99 renderer/canonical checks** cover both language
directions in reconstructed runtimes and an installed `start.sh` run. Checks
include repeated choices, preserved pause and item roles, translated subsequent
native questions, the same session/connection, untouched native options and
independent pinned-core readback of isolated saves. Agent screenshot inspection
is separate from human validation.

[Exact evidence](live-product-language-evidence.json) records distinct client,
native and test-fixture source identities, incremental reconstruction/build logs,
binaries/catalogs and failed investigation attempts. Initial fixture assumptions
about worn/random cap variants were corrected, preserving native item behavior.
These are incremental builds with retained caches; full SAVE-001 remains OPEN
and historical M5.5 FAILED. Previously recorded optional statistical failures
are not certified by this scoped regression selection.

The previous notice's personal check is now PASS. Two new deferred LANG-02
checks bring the [manual ledger](../validation/pending-manual.md) to **30 PENDING,
no open manual FAIL**, with the previous 28 unchanged. No new personal gate is
required today; native disassembly remains the next functional core slice.
