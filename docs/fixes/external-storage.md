# EXT-01 — External storage and partial collection

Implementation under verification, CWM 2.19. Root source and complete fork
patches are captured before builds. Final receipts follow after isolated tests.

RMB on a nearby native CONTAINER furniture opens two nine-column grids.
Ground backpacks, counted stacks and multi-item piles open the same view.
Single ordinary loose items retain immediate pickup. Storage contents have no
rotating drops. Static chest art is a proxy for native furniture, including
lockers; native passability remains authoritative.

Drag external → owned receiving area to collect, owned → external receiving
area to deposit, or onto an actual container item to insert. Select a stack and
set Quantity before dragging it for a partial transfer. No local slot move is
committed. CDDA pickup/drop/insert actors pay costs, choose native pockets,
handle capacity/theft and persist canonical activity/state. Menu returns only
after native completion and paid clock credit.

Views bind absolute adjacent coordinates, avatar origin, terrain/furniture
identity, safe item_locations, parent chains and quantity/type state. Admission
and execution revalidate. Sealed, unperceived, distant and changed sites reject;
external entries cannot be equipped or arranged as owned items. Contents on
hidden/sealed tiles are excluded from ground exports.

Vehicle cargo, pouring, explicit per-pocket placement, opening seals and
multi-item batch transfer remain deferred. Native DROP retains its overflow
policy if the destination changes during the activity; actual outcome is
requeried, never inferred by the client. Full SAVE-001 remains OPEN and the
historical M5.5 conformance gate remains FAILED.

Manual checks are deferred in `docs/validation/pending-manual.md`.
