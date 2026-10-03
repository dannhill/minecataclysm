# Engineering instructions

This workspace integrates CDDA, Luanti and selected Mineclonia presentation content.
Read `ARCHITECTURE.md`, `IMPLEMENTATION_STATUS.md`, `docs/invariants.md`, and the
original specification and amendments in `docs/source/` before changing behavior.

- CDDA owns gameplay, simulation time and canonical persistence. Luanti owns presentation only.
- Keep CWM independent of Luanti structures and the underlying transport.
- A missing delta requires a full authoritative resynchronization; never infer missing state.
- Preserve the upstream pins and complete patches in `baseline/manifest.json`.
  The ignored fork directories are working copies, not root-repository source history.
  Any later fork change must update its captured patch and source inventory.
- Original roadmap M0–M9 applies: M5 is interaction; M6 is vehicles.
- A milestone is VERIFIED only with an exact source identity, environment,
  reproducible commands and substantive passing evidence. Passing a Python CWM
  client does not verify the Luanti renderer.
- During the M5.5 takeover, production changes are limited to those strictly
  required to run verification. Record them separately; leave functional fixes
  for the remediation plan. Preserve failing conformance probes.
- Run tests against reconstructed sources with isolated saves/configuration.
  Never use or delete the user's existing worlds or shared benchmark save directories.
- Do not execute `test_worldgen.py`, `patch_*`, or `fix_file.py` as tests: they
  modify production sources. Their presence is historical evidence.
- Keep one writer per working tree. Do not push, publish or contact others as
  part of this local audit.

Use `python3 tools/takeover_baseline.py check` to verify that the fork sources
still match the captured baseline. Audit artifacts are ignored; committed
reports identify their location and checksums.
