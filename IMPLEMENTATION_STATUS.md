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

Manual feedback accepted movement, structures, door opening, safe mode and
position reload, but reported remaining camera flicker and terminal-input
aborts. A [scoped repair](docs/fixes/rebase-and-threat-presentation.md) now
keeps scene coordinates stable through CDDA rebases, renders perceived
creatures/NPCs, and exposes supported native ledge/death decisions. Its tests
have now been followed by the user's manual acceptance of absent/imperceptible
flicker, visible zombies and combat death without a crash. Manual ledge/pit
reproduction is still pending. Creature animations/heading and real-time
scheduling are not implemented; action-driven time is temporary. Border fog
and full entity/lifecycle conformance remain pending. Desktop pointed
OPEN/CLOSE is now implemented in the scoped exploration repair below.
The user also reported flat, monotonous ground; a
[terrain proposal](docs/design/terrain-presentation.md) records the design
questions for phase 2. The user then requested points 1/2: an
[isolated playable comparison](docs/prototypes/terrain-comparison.md) now
provides A/B materials/vegetation and independent border fog via
`terrain-demo.sh`. The later exploration repair promotes the chosen B style
to ordinary `start.sh`, independently of the demo fixture.
Real-time scheduling and terrain relief
are not part of this prototype.

Subsequent [manual terrain feedback](docs/source/terrain-feedback-2026-10-04.md)
**accepts B as the materials/vegetation direction**. Ordinary `start.sh` now
uses B. The current short border fog is not
accepted as the final solution. The
[distance/memory proposal](docs/design/visibility-and-world-memory.md) records
the user's alternatives and recommends a larger static remembered panorama
with bounded rendering and no extra creature knowledge. No distant memory,
new perception filter, larger view distance or relief has been implemented.
The current terrain export is not filtered by perception; the actor renderer
uses native `sees`. These must not be described as the same fog-of-war system.

The same feedback reports missing windows, inconsistent door states,
double-height disappearing window glass, generic traversable wooden objects,
apparent water-surface walking and unclear access to an upper floor. These
reopen variant/geometry coverage within FND-04 rather than invalidate all
earlier scoped tests. A demo-session CDDA log contains a terminal-input abort;
deep-water item warnings were using an unadapted native menu. An independent
canonical fixture reproduces its terminal-input abort with the previous
installed server; the [scoped exploration repair](docs/fixes/exploration-apertures.md)
routes that warning and the low-oxygen warning through native external
decisions, preserves water/item
effects, distinguishes aperture variants and retains the window sill. Native
state cues lower the first-person camera for wading/swimming and raise the
feet for window passage. Right-click opens; Sneak + right-click closes an
adjacent pointed opening, including by pointing at the remaining sill/floor.
The exact pond save reported by the user has not been reproduced. Full
underwater/vertical input, furniture assets and upper-floor navigation remain
incomplete. Historical M5.5 and SAVE-001 outcomes remain unchanged.

The subsequent [manual exploration validation](docs/source/exploration-validation-2026-10-04.md)
accepts pointed OPEN/CLOSE on doors/windows, B in normal play, shallow/deep
water entry/exit and the native vulnerable-item confirmation. Position and
modified aperture states survive quit/load, including departure beyond the
rendered area and return. This does not certify distant visual memory.
The user also accepts readable/moving placeholder creatures. Remaining visual
issues are dark-room NPC pop-in without corresponding local darkness,
black underwater presentation and the unsoftened projection border. Window
sill targeting works but its final ergonomics remain open. These are recorded
for FND-04/phase 2; flatness/relief is deferred until sufficient visual detail.
No further repeated manual checklist is needed before FND-02/03 work.

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
batched end-of-action tile changes, scoped window/door geometry repairs, exclusive
CWM player positioning and frame-independent bounded movement input. See
[the scoped repair](docs/fixes/projection-and-movement.md) for evidence and limits.
Later manual feedback above identifies aperture variants outside that evidence.

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
