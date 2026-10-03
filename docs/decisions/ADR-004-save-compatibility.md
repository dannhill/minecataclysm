# ADR-004: canonical saves and semantic compatibility

Status: ACCEPTED (original specification §37–38, §67; amendments §18–19).

SAVE-001 requires create/play through the 3D integration/save/shutdown/load
with standard upstream-compatible CDDA from the same pinned commit. Compare
position, inventory, terrain, furniture, monsters, NPCs, vehicles, time and
relevant world state semantically. Do not require byte-identical save files.
Do not compare against moving upstream master.

The external native fixture/reader links pristine upstream gameplay code and
uses canonical public load/serialization APIs. Its CMake target is test
infrastructure, not a production save-format modification. A direct native
fixture roundtrip validates the oracle, not the integration's SAVE-001.

The existing save_compat_test.py only checks files and exit codes; retain that
result as smoke-test evidence and report the stronger semantic test separately.

The [2026-10-03 user directive](../source/project-scope-2026-10-03.md) removes
standalone usability as a product constraint. Native pinned-CDDA loading is
an audit oracle for inherited saves, not a requirement to preserve its UI or
unrelated vanilla functionality. Any later intentional save-format evolution
must still preserve authoritative state with an explicit migration and tests.
