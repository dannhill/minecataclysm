# Engineering instructions

This workspace integrates CDDA, Luanti and selected Mineclonia presentation content.
Read `ARCHITECTURE.md`, `IMPLEMENTATION_STATUS.md`, `docs/invariants.md`, and the
original specification, amendments and current user scope directive in
`docs/source/` before changing behavior.
Read `IMPLEMENTATION_PLAN.md` and accepted decisions in
`docs/source/feature-decisions-2026-10-04.md` before choosing product behavior.
Prototype decisions that require the user's playable comparison must not be
silently finalized by an agent.

- CDDA owns gameplay, simulation time and canonical persistence. Luanti owns presentation only.
- The integrated product is the target. Unused upstream code, internal APIs
  and standalone functionality may be removed or substantially changed when
  beneficial. Do not preserve standalone behavior for its own sake; see
  `docs/source/project-scope-2026-10-03.md`.
- Keep CWM independent of Luanti structures and the underlying transport.
- Product text defaults to English; Italian WIP is the other supported choice.
  Follow `docs/design/product-language.md`: native text uses CDDA's translator,
  integration UI uses the shared presentation helper. Never translate wire/type
  identifiers or infer gameplay rules from translated labels. Language changes
  use the acknowledged presentation request, without restarting gameplay,
  replaying open native decisions, or rewriting native options/saves.
  Language definitions/catalogs live in `localization/`; regenerate shared
  metadata with `tools/generate_product_languages.py`. Add future languages
  through that registry/catalog path, not bilingual enums or menu branches.
- Keep UI view data/identities and native command routing separate from rendering
  and styling. Reuse the shared presentation theme; future visual redesigns
  must not require gameplay/protocol rewrites. Confirmation action labels omit
  terminal full stops; retain wire choices, semantic punctuation and narrative.
- Time speed uses the single contextual F8 control. Rest can extend its range;
  never reintroduce an independent sleep multiplier or a second speed menu.
- A missing delta requires a full authoritative resynchronization; never infer missing state.
- Preserve the upstream pins and complete patches in `baseline/manifest.json`.
  The ignored fork directories are working copies, not root-repository source history.
  Any later fork change must update its captured patch and source inventory.
- Original roadmap M0–M9 applies: M5 is interaction; M6 is vehicles.
- A milestone is VERIFIED only with an exact source identity, environment,
  reproducible commands and substantive passing evidence. Passing a Python CWM
  client does not verify the Luanti renderer.
- The M5.5 takeover is complete and FAILED. Its tag/report are historical
  evidence. Scope subsequent functional fixes to the user's request, record
  the new source identity and verification, and preserve remaining failing
  conformance probes. Do not promote the whole gate from a scoped repair.
- Run tests against reconstructed sources with isolated saves/configuration.
  Never use or delete the user's existing worlds or shared benchmark save directories.
- Do not execute `test_worldgen.py`, `patch_*`, or `fix_file.py` as tests: they
  modify production sources. Their presence is historical evidence.
- Keep one writer per working tree. Do not push, publish or contact others as
  part of this local audit.

Use `python3 tools/takeover_baseline.py check` to verify that the fork sources
still match the captured baseline. Audit artifacts are ignored; committed
reports identify their location and checksums.
