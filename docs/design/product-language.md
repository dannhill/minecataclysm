# Product language

English is the product default, independent of the operating-system locale
and an old global Luanti `language` preference. Supported product choices are
**English** and **Italiano (WIP)**. Italian is incomplete; missing native
translations use their original English text.

## Player setting and restart

The normal `./start.sh` opens the world directly. Press **Esc**, click
**English** or **Italiano (WIP)** on the right, then exit the game and launch `start.sh`
again. The current session retains its startup language: changing a preference
does not reinterpret an open native decision or restart an activity.
Selecting a language keeps the pause menu open and the simulation paused.
Passive bridge HUD/tint widgets are hidden while any modal menu is open,
including engine menus. Disabled Irrlicht widgets still participate in hit
testing; a fullscreen darkness/underwater tint must never intercept these clicks.
The main-menu Settings → Accessibility selector exposes the same two choices
when Luanti is opened through its main menu.

`cwm_language` is the product preference. The supervised launcher passes it
as `--language en|it` to CDDA and sets both `cwm_language` and engine `language`
in the temporary client configuration. After the client exits, an actual menu
change is stored atomically in
`$CDDA_USERDIR/config/presentation-language.conf`. This is presentation metadata,
separate from native `options.json` and canonical world/character saves.

Resolution order: explicit `CDDA_LANGUAGE`, saved presentation preference,
`cwm_language` in `LUANTI_CONFIG` (or the ordinary Minetest config), then `en`.
`CDDA_LANGUAGE=it ./start.sh` is a temporary override; an unchanged override is
not persisted. Unsupported explicit values fail before world creation.

## Text sources and boundaries

Integration UI strings use `protocol/include/cwm/product_language.hpp`:
`tr` returns UTF-8 literals, `text` an owning string and `wide` UTF-8 converted
to an owning wide string. English comes first; an absent/empty Italian string
falls back to English. The preference is set once during process startup.
Use `.c_str()` for APIs accepting pointers, including wide printf arguments.

Native item/recipe names, descriptions, conditions and decisions use CDDA's
existing translation manager, plural/context handling and pinned `it_IT.po`.
CDDA selects `en` or `it_IT` before loading static data. `CDDA_LOCALE_DIR`
selects the compiled catalog path without modifying native filesystem/save
paths. The selection overrides native USE_LANG only in process memory.
Luanti's engine menus use its existing gettext catalog.

Operation IDs, type IDs, instance identities and enum values remain unchanged.
Language selection itself adds no wire field or protocol revision; see
[the protocol contract](../../protocol/PROTOCOL.md) for the current paired version.
Never choose gameplay behavior, mappings or item identity from translated names.
Category metadata carries native category IDs in inventory, owned-item projection
and quick slots. Generic art uses those IDs, independent of language; labels
are translated only for display/search. Unknown IDs use a neutral fallback.
Native item type mappings remain the primary icon source; batches are unchanged.

## Build and verification

CDDA must be built with `LOCALIZE=ON`, `LANGUAGES=it_IT`; build its `locale`
target as well as `cdda-server` and `cata_test`. The native catalog is
`cdda/lang/mo/it_IT/LC_MESSAGES/cataclysm-dda.mo`.
Luanti requires gettext enabled and `GETTEXT_MSGFMT` available; its translations
target produces `luanti/locale/it/LC_MESSAGES/luanti.mo` for RUN_IN_PLACE.
Catalogs are generated from the captured upstream sources, not hand translated
item lists. Install catalogs together with the verified runtimes.

`tests/product_language_test.py` checks precedence and launcher agreement using
isolated child stubs, including menu-change persistence and untouched native
options. Protocol tests check unchanged semantic command bytes and UTF-8/fallback.
`tests/equipment_gui_test.py --language-smoke en|it` uses the real renderer,
native item names/decisions and an independent save reader, with screenshots
for inventory, body, crafting and native choices. These scopes are distinct:
launcher stubs do not certify native localization or rendered text.

The scoped delivery report records exact sources, commands, binaries, generated
catalog hashes and limits. Full SAVE-001 and M5.5 are not recertified by language
checks. Future feature UI must follow these same language boundaries.

UX-04B (2026-10-13) replaces the pause dropdown with explicit language buttons.
The user's renewed Italian → English FAIL after `91393f7` stays in manual review;
[the overlay repair](../fixes/pause-language-menu.md) has scoped automated
menu/restart evidence, which does not constitute personal acceptance. Live language switching is
deferred; all clinical and decision text remains in the startup language.
