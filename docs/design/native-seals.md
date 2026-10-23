# Native sealed pocket opening

I → selected owned container → Open sealed pocket... explicitly selects a
sealed CONTAINER pocket (bounded 256 choices, native decision paging) or Cancel.
An enclosing sealed/technical pocket must be opened first. Requests retain the
inventory view/item identity, position, charge and ancestor guards; pocket seal
state is now part of the binding. Work/sleep/pause admission remains native.

This is a presentation adaptation: pinned CDDA has no separate stand-alone
opening activity or opening cost for pocket seals. Native item-use/consume/
retrieval paths break seals via contents_change_handler; this interface exposes
that same prefix, without inventing a timer or a move charge. Retrieval,
consumption and subsequent liquid handling still charge their own native costs.
Item-use transformations requiring tools are a distinct, deferred mechanism.

The native contents handler owns unsealing, restacking, ancestor invalidation,
open-container spilling and ground placement on cancelled liquid handling.
Confirmation Cancel occurs before mutation; cancelling a later spill choice
cannot restore a seal already broken. Contents are not moved/consumed by opening
itself. Sealed preservation multipliers change as defined by CDDA. Pocket seals
are not automatically resealable via this interface. Saves remain canonical.

CWM2.34 appends InventoryEntry.seal (SealInfo.reason) and OPEN_SEAL=5 on the
existing transfer request, with quantity/destination both zero. The 8-bit
EquipmentAction mask is unchanged. Handles are cleared before native choices;
the shared command ledger prevents replay. External portable containers are
not included. The open-seal button takes precedence over Pour for sealed items;
a fresh authoritative view restores Pour after opening.

Reconstructed native/client/SDK builds and actual renderer/canonical tests are
required before installation. Personal tests remain PENDING in the manual ledger.
Windows remains CWM2.26. Historical M5.5 FAILED / full SAVE-001 OPEN unchanged.
