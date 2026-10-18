# Adding a product language

`languages.json` is the shared registry for the launcher, native runtime and
3D client. Currently enabled content: English and Italian WIP. It is not a
two-language limit; language requests use registered string codes on the wire.

1. Add an entry with a unique product code (for example `fr-CA`), endonym,
   `native_locale` matching CDDA, `engine_locale` matching Luanti,
   `incomplete` boolean and a catalog filename relative to this directory.
2. Add the UTF-8 JSON catalog: English message → translated message. Preserve
   formatting placeholders. Missing/empty messages fall back to English.
   Existing Italian inline messages remain a compatibility fallback; a new
   language uses its catalog, without adding parameters to C++ call sites.
3. Run `python3 tools/generate_product_languages.py`. It updates the shared C++
   metadata/catalog header, engine setting codes and main-menu labels. Esc
   builds its language buttons directly from the registry, scrolling when needed.
4. Build CDDA's corresponding upstream catalog (`LOCALIZE=ON`, add the locale
   to `LANGUAGES` and build `locale`) and Luanti's translations target. The
   integration catalog translates integration UI; it does not replace native
   CDDA item/recipe/decision or engine gettext translations.
5. Capture changed forks with `tools/takeover_baseline.py capture`, rebuild both
   paired runtimes from captured sources, then verify both directions in-game.

`python3 tools/generate_product_languages.py --check` detects stale generated
files. `tests/product_language_registry_test.py` generates and compiles a third
locale in a temporary tree, checks its translation/fallback, locale mappings and
menu/setting inclusion, without enabling that incomplete example in the game.

Keep English as the fallback. Only UI labels are translated: wire/type/item IDs,
canonical saves and native gameplay rules are unchanged. Upstream missing
translations may retain English, so keep incomplete languages marked WIP.
