# CDDA–Luanti integration: normative architecture

The original specification v1.0 and amendments v1.1, preserved verbatim in
`docs/source/`, define the intended behavior. The approved agy plan is retained
as historical evidence and does not replace the original M0–M9 roadmap.
The [current user scope directive](docs/source/project-scope-2026-10-03.md)
removes standalone preservation as a product constraint. Upstream internals
and unused functionality can be changed or removed to serve the integration.
Pinned upstream builds/tests are reference evidence, not a requirement to
retain unrelated standalone functionality in the product.

The [complete current plan](IMPLEMENTATION_PLAN.md) and
[accepted feature decisions](docs/source/feature-decisions-2026-10-04.md)
define the product adaptations: real time with pause, guided deep interfaces,
native recommended content defaults and playable spatial/controller prototypes.
Explicit tested spatial extensions inside integrated CDDA are authorized;
the user selects movement/driving after playing the comparison scenes.

CDDA is the sole simulation, gameplay, temporal and persistence authority.
Its internal CWM coordinator validates inputs and exports immutable snapshots
and end-of-turn delta batches. CWM describes semantic state, independent of the
transport and presentation engine. Luanti's native C++ bridge renders that
projection, interpolates visual positions and captures commands. Mineclonia
supplies selected textures/models/node definitions. The start.sh supervisor owns process and private-socket lifecycle; compiled
launcher/coordinator aliases exec it without governing gameplay.

The canonical save is CDDA's save. A Luanti world is a disposable presentation
cache. On reconnect or a missing delta the client must obtain an authoritative
snapshot before resuming. Session/player/connection identity, command
deduplication, message sequences and world revisions have distinct meanings.
CWM 2.0 implements this boundary through CwmTransport/CwmListener: exact
version negotiation, canonical player identity, fresh runtime/connection IDs,
bounded command outcomes, contiguous per-direction emitted messages and
correlated reset/full-state acknowledgement. Old wire clients are incompatible.

CDDA `(x,y,z_level)` coordinates are semantic. Scale, floor height and eye
height belong to presentation configuration. Changes of reality-bubble origin
must preserve consistent terrain/entity/interaction positions.

Pinned source identities and complete local modifications are recorded in
`baseline/manifest.json`. Reconstruction checks every source file's content and
mode before compilation. The root CMake currently discovers CDDA/Luanti but
does not build them; they require explicit component builds.

See `protocol/PROTOCOL.md` for observed wire behavior, `docs/invariants.md` for
the acceptance invariants, and `docs/audits/M5.5.md` for implementation findings.
Observed behavior must be reported separately from these requirements.
