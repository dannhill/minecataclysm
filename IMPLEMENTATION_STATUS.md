# Implementation status

The [complete implementation plan](IMPLEMENTATION_PLAN.md) now incorporates
all 15 source-grounded feature questionnaires. Detailed accepted decisions
are in [the product directive](docs/source/feature-decisions-2026-10-04.md).
FND-01 (canonical startup/loading and shared native turns) is implemented with
scoped verification PASS; see [the repair](docs/fixes/canonical-runtime.md).
Existing-avatar/time preconditions now pass through the actual 3D client.
Full SAVE-001 remains incomplete; the failed M5.5 gate has not been recertified.
FND-02 is next.
Product decisions and planned prototypes do not certify implementation.

**M5.5 takeover audit: COMPLETE. Architectural conformance gate: FAILED.**
The findings are documented in [the audit](docs/audits/M5.5.md), with
[persistent evidence](docs/audits/M5.5-evidence.json) and a
[prioritized remediation / M6 plan](docs/audits/M5.5-remediation.md).

Post-audit visibility repair: `start.sh` now waits for the real CDDA process,
uses a private configured socket, opens the CDDA presentation game directly
and preserves failure status. The actual invoked binaries have been refreshed.
Terrain, camera and vehicles share local XY / absolute Z coordinates; cached
Luanti air blocks cannot erase the CDDA projection. Full terrain replaces old
projected blocks, and bridge shutdown clears owned state. Missing origins are
safely rejected. See [the scoped repair evidence](docs/fixes/visible-world.md).
The original failed M5.5 gate and remaining findings are not recertified.

Post-audit structural/movement repair: semantic CDDA terrain/furniture export,
batched end-of-action tile changes, consistent window/door geometry, exclusive
CWM player positioning and frame-independent bounded movement input. See
[the scoped repair](docs/fixes/projection-and-movement.md) for evidence and limits.

The frozen claimed-M5 baseline is `1c37927`, tagged
`pre-takeover-m5-claimed`. The audit is on `audit/m5-conformance`; the scoped
visibility repair is on `fix/visible-world-startup`. During the audit only two production
changes were made to enable verification: trap-registry/map initialization
(`53ec1d4`) and the native `main` declaration (`6f0d415`). Complete fork patches,
upstream pins and source identities are in `baseline/manifest.json`.

The following results/findings describe the historical audit baseline.
Later scoped repairs above supersede their addressed failures without
recertifying the remaining gate.

Clean component builds pass. Protocol tests pass 2/2; Luanti native tests pass
302/302; CDDA's native default suite passes 1,067/1,068 cases; Mineclonia's
upstream CI lint command passes for 461 Lua files. Root CTest discovers zero
tests. The final legacy integration run passes 3/6 scripts with timing and
message-order assumptions explained in the audit.

Product blockers include lost inherited avatar/time, an incomplete simulation
turn loop, unchecked actions, process aborts on oversized frames, missing
command deduplication/resynchronization and an actual bridge crash on an absent
snapshot origin. Spatial projection, entity instantiation, interaction wiring,
lifecycle/threading and full performance acceptance are incomplete.

SAVE-001 fails. The clean native oracle restores its control fixture; the actual
3D attempt sends three accepted moves and produces a natively readable save,
but replaces the original avatar and resets its calendar. Full semantic
preservation is not certified.

Original M0–M9 applies: M5 is interaction, M6 is vehicles. The recovered agy
plan used compressed milestone labels and its claims are historical evidence.
M0–M5 remain IN PROGRESS under the original acceptance criteria; M6–M9 remain
PLANNED. No historical milestone is promoted to VERIFIED.

The [current scope directive](docs/source/project-scope-2026-10-03.md) gives
the integrated product priority. Unused CDDA/Luanti/Mineclonia logic, internal
APIs and standalone capabilities may be removed or substantially transformed
when beneficial. Authoritative gameplay, canonical persistence and recovery
invariants remain requirements.
