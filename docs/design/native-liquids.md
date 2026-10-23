# Native water sources and carried-liquid pouring

Normal start.sh uses recognized native water_source / finite_water_source
examine handlers. Right-clicking a perceived adjacent source sends the existing
semantic EXAMINE command; admission and execution recheck source, range, Z and
perception. The tile capability is read-only: it never calls map::water_from,
creates water or samples hidden contamination. Explicit native examination may
sample water before its menu, as the original handler does, even on cancel.

The original native liquid menu handles direct consumption and container choice.
Its external container selector exposes accessible carried item_locations and
calls native remaining-capacity/compatibility predicates. Sealed/technical
pockets are not bypassed. Choices are bounded to 256 compatible containers and
paged through existing native decision IDs; final Cancel is safe on disconnect.
Adjacent keg destinations use the original native logic. Vehicle tank selection
is deferred. Ground pouring uses an external direction menu, then the original
native destination checks and transfer routine. No curses selector is entered.

I adds Pour liquid... on a real owned liquid or a container holding it. CWM2.33
appends optional LiquidInfo and ItemTransferAction.POUR (4), without widening
the old 8-bit equipment-action mask. POUR requires quantity=0/destination=0:
it opens the native whole-stack/capacity-limited handler, not a fabricated
quantity operation. Multiple direct contents require an explicit liquid choice.
Existing inventory view, item identity, pocket ancestry, generation and command
ledger checks remain. Full/changed/invalid destinations use native rules.
Partial pouring counts as success and preserves the source remainder; only a
fully drained selected liquid is removed through native item_location methods.

Source collection runs original ACT_FILL_LIQUID. LiquidTransferState carries
only its transient token: the native legacy activity has no finite move-total
percentage. I pauses/inspects and Interrupt transfer sends a typed, generation-
checked CancelLiquidTransferRequest. Already transferred charges remain real.
Carried-container pouring may instead apply immediately and debit native moves;
the existing applied/time-remaining UI owns that uninterruptible paid interval.
There is no fake cancellable animation for an already applied pour.

Canonical activities, source stacks, destination contents, quality, temperature,
seals and item locations remain CDDA save data. Loading an in-progress fill
continues the original activity; reconnect never issues another source command.
The source, finite depletion and carried remainder are never stored in Luanti.
Native drinking reaches stomach/gut physiology first; the thirst number need
not fall instantly. Frozen items remain frozen and cannot become free liquid.

Only raw water's local presentation glyph is corrected in addition to the
existing water_clean override. It does not change generated mapping batches,
types, quality or safety: untreated water's glyph is not a poison detector.
English remains default; missing Italian WIP text uses the shared fallback.

This slice does not enable liquid/gas crafting results or universal item use.
Mandatory native output handling requires a separate safe recovery/shutdown
path before liquid recipes/purification can be enabled. Opening sealed pockets,
vehicle fuel/tanks, external portable-container pouring and arbitrary quantity
selection remain separate. Normal real-time start.sh is the target. Windows
installer remains CWM2.26; historical M5.5 FAILED / full SAVE-001 OPEN remain.
