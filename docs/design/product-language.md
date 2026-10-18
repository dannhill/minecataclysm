# Product language

English is the default, independent of OS locale and old global Luanti language
settings. Supported choices: **English**, **Italiano (WIP)**. Missing Italian
translations retain the English source. Stable type/item/category/operation IDs
are never translated or inferred from labels.

## Live change during play

In `./start.sh`, Esc → English / Italiano changes the active session without
restarting either process. The native CWM coordinator accepts a registered-code presentation
request on its owner thread, calls CDDA's `set_language` to invalidate translation
caches, then acknowledges the active language and refreshes native projection
labels. The client activates its shared translator and engine gettext only after
the matching acknowledgement. The existing next-frame formspec refresh rebuilds
the whole pause menu, without destroying it during a click callback. The notice
says Active and names the acknowledged language; Italian alone has the incomplete
translation note. While awaiting a reply it says Applying. Repeated clicks retain
the latest requested choice; only one request is in flight.

This supersedes the original supervised-restart rule following the
[developer's request](../source/live-language-feedback-2026-10-18.md). It changes
presentation, without turns, motion, unpaid aim, activity restarts or canonical
options/save writes. The native language-option value itself remains untouched;
only the translation manager changes. CDDA names use native plural/context
handling. Existing narrative messages are historical text, not actions to replay.
An already open native decision retains its original text until answered. The
client defers its language request while a decision is open; the server also
rejects requests during that state. Entry effects and answers must execute once.
Subsequent decisions use the new language.

CWM 2.26 adds correlated LanguageRequest/LanguageState messages, independent of
gameplay command IDs. Reconnect resynchronizes authoritative state first, then
reapplies the presentation preference, without recreating native actions. Sequence
gaps continue to require full authoritative resynchronization. Unsupported codes
are rejected. Both runtimes must be installed together.

The Linux engine refreshes GNU gettext's message catalog on its UI thread by
invalidating LC_MESSAGES after updating LANGUAGE; numeric/time locale is retained.
Integration forms and HUD use `protocol/include/cwm/product_language.hpp`.
Native item/recipe/status/decision text comes from CDDA's translation manager and
captured it_IT catalog. Engine menus use the engine gettext catalog. Old recorded
messages, proper names and untranslated WIP content are not rewritten.
Passive HUD/tints stay hidden while any modal menu is open, including Esc.
Disabled Irrlicht widgets can still hit-test; a fullscreen tint must not intercept
menu clicks.

## Preference and startup

`cwm_language` is presentation metadata. After a native acknowledgement it and
engine `language` are updated in the launcher's private client configuration.
On exit the supervisor atomically persists an actual menu change in
`$CDDA_USERDIR/config/presentation-language.conf`, separate from `options.json`
and canonical saves. A crash before orderly exit can lose an unsaved preference.

Startup resolution: explicit CDDA_LANGUAGE, saved presentation preference,
cwm_language in LUANTI_CONFIG/ordinary config, then en. An unchanged explicit
`CDDA_LANGUAGE=it ./start.sh` override is temporary. Unsupported explicit values
fail before world creation. The launcher passes en/it to native startup and both
client language settings. The main-menu Accessibility selector chooses the next
session's startup preference; the in-session Esc selector applies live.

## Build and verification

CDDA needs LOCALIZE=ON, LANGUAGES=it_IT and the locale target. Its catalog is
`cdda/lang/mo/it_IT/LC_MESSAGES/cataclysm-dda.mo`; CDDA_LOCALE_DIR may select it
without changing native save paths. Luanti needs gettext and its translations
target, producing `luanti/locale/it/LC_MESSAGES/luanti.mo` in RUN_IN_PLACE.

Launcher tests cover precedence/persistence, override and unchanged native
options. Protocol tests validate correlated, bounded replies while preserving
command IDs/revisions. Native tests exercise actual language admission, cached
item names, blocked decisions and retained activity/moves/time/position/options.
Renderer tests switch both ways in the same connection, repeat selections,
inspect inventory/body/crafting and new native questions, preserve menu pause,
and verify isolated native saves with the independent pinned-core reader.
Automated evidence is distinct from human acceptance; deferred personal checks
remain in the manual ledger. Incremental reconstruction and scoped readback are
not a cold build or full SAVE-001/M5.5 certification.

## Adding languages

The shared registry is [localization/languages.json](../../localization/languages.json).
It owns code, endonym, native/engine locale mapping, catalog and WIP status.
Integration catalogs are UTF-8 JSON maps from English message to translation;
missing/empty entries fall back to English. Existing inline Italian pairs are a
migration fallback, not an extra parameter required for new languages.
`tools/generate_product_languages.py` generates C++ metadata/catalogs, main-menu
labels and the setting's supported codes. Esc derives its scrollable choices
from that registry. The launcher resolves the engine locale from metadata;
CDDA uses the corresponding native locale. Adding a registry/catalog entry and
building the corresponding upstream catalogs requires no new wire enum, language
branch or protocol revision. See [translator instructions](../../localization/README.md).
