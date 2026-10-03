# Required invariants

Normative requirements from the takeover directive. Audit outcomes are in
`audits/M5.5.md`; this list must not be weakened to match existing code.

## INV-001

CDDA is the sole gameplay authority.

Evidence required: Trace every input/state mutation and compare turn advancement with upstream rules.

## INV-002

Luanti never commits gameplay state independently.

Evidence required: Inspect connected/disconnected input, local server mutations and persistence/cache boundaries.

## INV-003

CDDA save format remains canonical.

Evidence required: Native pinned-CDDA semantic reader and standard-client load after integration actions.

## INV-004

CWM does not expose Luanti-specific data structures.

Evidence required: Schema/types contain no MapNode, content_t, param1/param2 or engine pointers.

## INV-005

Visual interpolation never modifies authoritative coordinates.

Evidence required: LERP remains in bridge visual state; origin/height transformations remain consistent.

## INV-006

Mineclonia contributes presentation content only.

Evidence required: Loaded cdda_voxel Lua modules and extracted assets contain no gameplay systems.

## INV-007

CWM protocol is transport-independent.

Evidence required: Verify CwmTransport boundary and that framing/schema do not depend on backend APIs.

## INV-008

A lost delta causes resynchronization rather than client-side inference.

Evidence required: Inject a sequence gap into the real bridge and require snapshot-based recovery.
