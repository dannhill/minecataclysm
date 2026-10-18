# Implementation status

Current scoped delivery: **native atomic equipment time**, CWM **2.23 unchanged**,
installed in ordinary `start.sh`, with the previous runtime pair retained.
Wear/takeoff keep native atomic garment changes and move costs. I pauses even
with the equipment result in flight; the read-only query follows settlement.
Closing inspection resumes the same native debt and preserves feedback, with
remaining game seconds instead of a fractional clothing progress bar. Native
actor interruption remains available for treatment/crafting/transfers/etc.
No clothing cancellation or new gameplay/save rule is introduced.
[Design](docs/design/native-equipment-time.md), [evidence](docs/fixes/native-equipment-time.md).

Scoped verification: 309 client tests / 47 modules, 648 Catch assertions / 4 cases,
115 renderer/canonical checks including installed `start.sh`, delayed reply,
frozen/resumed debt, treatment interruption, automatic return and reconnect.
Incremental reconstructed client build; native runtime unchanged. Full SAVE-001
OPEN; historical M5.5 FAILED; mapping batch60 unchanged.

Recorded 13 new personal PASS; backlog **9 PENDING + 1 manual FAIL** (I pause
clothing recheck). Cancellation of a single garment is superseded by the explicit
native-semantics decision. No acceptance inferred from automation.
[Backlog](docs/validation/pending-manual.md). The user authorizes the next three
roadmap slices consecutively: loose pickup UX, humanoid materials/rig, then
movement orientation/animations. Manual checks remain deferred.

Previous scoped delivery: **INT-01 interaction feedback**, CWM **2.23**, installed
in ordinary `start.sh` with paired rollback runtimes. RMB toggles projected
openings using their last authoritative state; Shift is posture only. Shift-click
moves to the opposite external pane or the selected owned container. Dropping
outside an inventory/transfer formspec requests native ground DROP; Esc and
background inside still cancel. Actual quantities, roles, costs, seals, capacity
and ownership remain CDDA. No local inventory edits or automatic undress/theft.

Paused loose pickup is rejected and unsent selections are discarded, so RESUME
never executes the old click. External partial DROP uses native item::split,
conserving the remainder and its shortcut identity. Continuous CLOSE refuses a
tile intersecting the native body at admission and execution. The reported jam
while *opening* the original world door remains a manual recheck: the concrete
reproduced/guarded case is close-through-body, not a certified mesh fix.
Aim release semantics are unchanged and pending discussion: stop paid AIM input,
retain earned precision under the integrated native policy, no forced recoil reset.
[Design](docs/design/interaction-feedback.md), [delivery](docs/fixes/interaction-feedback.md).

Manual feedback: AIM1–3 PASS, EXT1–3 PASS, EXT4 FAIL only for paused deferred
pickup. Five new PASS; backlog **21 PENDING + 2 manual FAIL** (language and EXT4),
including three new gesture checks. All prior PASS retained. No manual testing
required today; automatic checks do not constitute personal acceptance.
[Backlog](docs/validation/pending-manual.md).

Scoped verification: 183 native cases / 186,099 assertions; 309 client tests /
47 modules plus 648 Catch assertions / 4 cases; 11 protocol tests. Actual renderer
and independent canonical readers cover toggled windows, paid shortcut transfers,
partial outside drops, pause/resume, recovery and canonical state. Incremental
reconstructed builds, not a clean build. Batch60 mapping unchanged; full SAVE-001
OPEN and historical M5.5 FAILED. Next: core consolidation and rig/UV/animation/audio.

Previous scoped delivery: **UX-05 native recipe shortcuts**, CWM **2.22**,
installed in ordinary `start.sh`, with paired rollback runtimes retained.
K has All/Favorites/Recent/Unfinished; opening prioritizes reachable unfinished
work, known recent recipes, known favorites, then All. Native filtering precedes
the 256-row limit, and search/batches stay in scope. Recipe favorites are native
UI metadata, distinct from protected component items; setting them keeps K open,
without moves, activity, clock/RNG change or artificial recency. Present knowledge,
view identity and expected state are revalidated, with at-most-once settlement.

Favorites and unique last-20 started recipes use canonical world `uistate.json`,
shared by its characters; no new character-save schema or client persistence.
Recent means started, not completed. English-safe native continuation checks
remaining requirements, preserving prior components and progress. Frequent,
subrecipes, liquid/gas/byproduct results and practice remain separate.
[Design](docs/design/recipe-shortcuts.md),
[delivery and evidence](docs/fixes/recipe-shortcuts.md).

Scoped verification: **181 native cases / 186,030 assertions**; **309 client
cases / 47 modules**, plus **648 Catch assertions / 4 cases**; **11 protocol tests**.
Actual renderer: **42 reconstructed + 42 installed + 14 reload checks**, all PASS,
with isolated saves and independent pinned native reader. Builds are incremental,
not cold clean builds. Empty-variant selection avoids meaningless RNG draws;
this intentionally changes subsequent random-stream order. Favorite knowledge
uses real native sources without generating water/pseudo-tools. The favorite RNG
invariant does not certify every legacy material-cache preview.

Backlog **24 PENDING + 1 manual FAIL**: four new recipe checks plus twenty previous;
manual PASS retained and LANG-01.2 FAIL awaits the user's recheck. No user testing
required today, and automation never implies personal acceptance.
[Deferred checklist](docs/validation/pending-manual.md).
Mapping remains through Sol batch60 (2,400 records / 972 supported visuals / 146
textures); unchanged in this delivery. Next: focused core consolidation and
rig/UV/animation/audio presentation debt. New spatial-control prototypes still
need the user's playable comparison. Full SAVE-001 OPEN; historical M5.5 FAILED.

Previous scoped delivery: **UX-04B structured medical selection and manual feedback**,
CWM **2.21**, installed in ordinary `start.sh`, paired rollback runtimes retained.
Item-first native treatment selection now exports observable body identities,
health resolution and known treatment descriptions. Anatomical armour proxies,
hearts and readable disabled parts replace flattened ASCII choice labels. Exact
HP only in native precise mode; unknown/broken/mending health stays qualitative.
Native choice mapping, explicit confirmation, ACT_FIRSTAID, paid costs,
interruption and canonical persistence remain unchanged. No client healing.

The user's [file feedback](docs/source/manual-ui-feedback-2026-10-13.md) adds
**12 manual PASS**, leaves **13 untested points**, and records **LANG-01.2 FAIL**.
Fixes retain the last accepted grid during layout queries, enlarge container
hit targets to six rows per page, and show synchronous equipment pacing from
the native coordinator clock. Esc language controls are explicit buttons;
restart still required. Original PASS retained; the language FAIL awaits the
user's recheck even after scoped automated verification. Backlog **20 PENDING +
1 manual FAIL** includes three feedback rechecks and four medical checks.
No user testing required today; no acceptance is inferred from automation.

Mapping synchronized through **Sol batch 60**: 2,400 items, 972 supported visual
registrations, 146 textures with attribution/hash; unsupported/no-match fallback
and local water_clean override retained. No Mineclonia gameplay imported.
[Delivery/evidence](docs/fixes/structured-medical-selection.md),
[mapping](docs/fixes/item-mapping-2026-10-13.md),
[backlog](docs/validation/pending-manual.md).

At UX-04B delivery, the next slice was UX-05 (now delivered above). Body-first H → filtered
medical items, refined anatomical art, live language change and first-person aim
pose/zoom remain follow-ups. RMB release already ends the gesture; earned native
precision is not reset. Movement retains native accuracy costs. Full SAVE-001
remains OPEN; historical M5.5 remains FAILED. Incremental scoped verification
never promotes the whole gate.

Previous scoped delivery: **UX-04A native decision panels and work feedback**,
CWM **2.20**, installed in ordinary `start.sh` with paired rollback copies.
Native questions now use a Mineclonia-style modal: readable colour-safe text,
scrolling, full-label tooltips, clickable choices and physical 1–9 shortcuts.
Esc selects the cancellation index advertised by CDDA; labels are not parsed
for gameplay or cancellation. Enter cannot choose via accidental widget focus.
Held keys cannot answer a later prompt. Handlers bind exact decision/connection;
one response enters waiting until native settlement/new prompt. Debug overlays
are hidden while choosing. Native costs, pagination, lost-peer fallback and
canonical save behavior remain server-owned.

The temporary work panel has clearer inspect/pause instructions and a native
progress bar when total work is known. Closing inspection resumes the actor;
Interrupt cancels it. Returned inventory reports work completion without claiming
success from an initial ACK. [Design](docs/design/native-decision-panels.md) and
[scoped verification](docs/fixes/native-decision-panels.md).

At UX-04A delivery, backlog **26 PENDING**: four new dialog/work checks plus twenty-two unchanged.
No user testing is required today; no acceptance is inferred from automation.
The next slice announced then was **UX-04B structured medical selection**, with native
body-part identities, observable health and known treatment effects; do not
infer these from ASCII bars or labels. The generic medical selector remains
native text in this slice. Existing UX-02 death/IPC manual exceptions remain
separate. Full SAVE-001 is OPEN; historical M5.5 is FAILED.

Previous scoped delivery: **EXT-01 external storage and partial collection**,
CWM **2.19**, installed in ordinary `start.sh` with paired runtime rollback.
RMB on nearby visible native storage opens two Mineclonia-style nine-column
panes; empty storage is interactive. Ground backpacks, counted stacks and
multi-item piles use the same interface. Loose ordinary items retain direct
pickup and rotating visuals; furniture contents no longer rotate outside.
Drag between receiving areas or onto real container items. Selecting a stack
and editing Quantity supports partial collection/deposit. CDDA's pickup/drop/
insert actors own pockets, size/capacity/theft, cost, outcome and persistence;
paid completion returns to the same external menu. Sealed/distant/changed
sites, stale identity/parents/charges and external equipment shortcuts reject.
No local inventory, teleport or optimistic transfer is committed.
[Behavior and scoped evidence](docs/fixes/external-storage.md).

At EXT-01 delivery, backlog **22 PENDING**: eighteen unchanged plus four storage checks. Previous
manual PASS remain accepted; automation does not imply user acceptance.
No user testing is required today. `./storage-demo.sh --fresh` opens an isolated
scene; without `--fresh` it resumes that demo save. Furniture chest meshes are
provisional presentation proxies. Cargo, pouring, opening seals and explicit
single-pocket placement remain separate. Next: richer native dialogs and
visible operation feedback, retaining rig/UV/animation/audio and other core
features in the plan. Full SAVE-001 remains OPEN; historical M5.5 remains FAILED.

Previous scoped delivery: **AIM-01 held right-mouse aim**, CWM **2.18**.
RMB holds assisted native aim; F remains a keyboard fallback. Context RMB
opens/collects and Shift+RMB closes nearby projected openings, with gestures
classified once. Firearm + pointed perceived hostile wins over a context behind
it; crouch does not steal aim. LMB still fires once per press, then held RMB
resumes paid aim. Only one explicit shot/R may finish the current in-flight AIM
step; menus/pause/recovery, changed target/weapon and timeout discard it.
No shot waits behind movement, other fire or activities. Release stops new aim
improvement, retaining the existing native policy for already-paid recoil.
Both processes keep CDDA authority/costs; no new protocol/save fields or native
simulation changes. The verified client is installed in ordinary `start.sh`,
with previous-client rollback; localized native runtime/catalogs are unchanged.
[Behavior and scoped verification](docs/fixes/held-mouse-aim.md).

At AIM-01 delivery, backlog **18 PENDING**: the previous fifteen plus three RMB checks. Existing
manual PASS remain accepted; no acceptance is inferred from renderer automation.
No user testing was required then. External containers and selected-quantity
collection are now delivered above; richer native dialogs/feedback follow.
Rig/UV/animations, audio and the existing UX-02 exceptions remain scheduled.
Full SAVE-001 stays OPEN and M5.5 remains historical FAILED.

Previous scoped delivery: **LANG-01 product language**, CWM **2.18**.
English defaults independently of the system locale and legacy engine settings;
Italiano (WIP) is selectable from Esc → Language/Lingua, applied to both processes
through a restart. Actual menu preferences are separate from native options and
canonical saves. Native gettext and a shared UI helper provide English fallback;
category IDs keep generic art stable. Both runtimes and Italian catalogs were
installed with rollback copies, preserving continuous **4x**. Its delivery had
**15 PENDING**, before the three AIM-01 checks. [Report](docs/fixes/product-language.md).

Previous scoped delivery: **UX-03D inventory drag-and-drop**, CWM **2.18**.
Assign/Clear buttons are removed. Grid, quick slots, hand, worn-item pages,
owned-container icons/rows and explicit Ground zone use semantic drag input.
Short click still selects; Esc/outside release cancels. Quick-slot swaps are
atomic and grid ordering persists on actual native items as optional UI metadata.
Equipment/transfers execute paid native actions and decisions, then return after
authoritative completion. Its delivery had **13 PENDING**, before LANG-01's
additional checks. [Report and scoped receipts](docs/fixes/inventory-drag-and-drop.md).

Previous scoped delivery (2026-10-09): **UX-03 interactive persistent hotbar**,
CWM **2.17**. Nine explicitly assigned/removable references are independent of
inventory ordering/capacity. Wheel/numbers select without equipping; **G** requests
the eligible native operation and pays access/work costs. Actual hand and selected
slot have different HUD markers; unassigned wielded items remain visible separately.
Native optional UI metadata preserves exact-instance bindings through wield/wear,
save/load and reconnect, without saving ephemeral inventory-query IDs. Lost,
consumed or ambiguous references clear instead of following a namesake.
[Report and receipts](docs/fixes/interactive-quickbar.md).

Targeted repairs: visible initially unfocused search, click-to-focus/blur,
quantity layout, prominent native rejection, contextual color-tag sanitation,
water_clean-only icon override and native spoilage cue. Generated item batches
are unchanged. Clouds share the paused visual clock. Normal start.sh defaults to
the accepted continuous **4x** mode; explicit ordinary/comparison options remain.
The earlier 2.17 delivery installed both runtimes with previous-pair copies;
its installed save/reload checks and exact hashes remain in historical receipts.
Real wielded rig/UV/animations, audio and richer native dialogs remain scheduled;
product language and held RMB aim are delivered in later scoped slices.

Earlier manual acceptance: ranged/reload, owned transfers, UX-01 and ordinary
UX-02 each four PASS, with the errata preserved. Death/IPC/native decisions were
not actually tested, and nested ammunition deposit was not performed/understood.
Automatic transfer checks demonstrated partial nested deposit; the latest
focused UX-03 point 3 is now accepted. Preserve the earlier qualification
as history, not as a new failure. [Earlier feedback](docs/source/core-ux-validation-2026-10-09.md).
The delivery initially had **14 PENDING**. The latest feedback above
accepts three focused rechecks and rejects hotbar point 1; remaining
points are retained without inferring acceptance. No testing is required now.
[Backlog](docs/validation/pending-manual.md).

UX-02 paid completion/automatic return remains available, verified in equipment,
consumption and transfer regressions. G from the world does not force I open.
I during a native activity is consultation/pause; closing it resumes the actor,
whereas Interrompi requests native cancellation. The original equipment fixture
wears only a backpack; it does not contain an unseen full outfit.
Body-region clothing/encumbrance, persistent selection across queries and
nearby external containers/selected-quantity collection still need dedicated
semantic interfaces. Inventory drag-and-drop, language and held RMB aim are delivered;
external containers remain the next essential inventory extension.
The broader M5.5 gate remains historical FAILED and full SAVE-001 stays OPEN.

Previous scoped follow-up (2026-10-09): inventory feedback fixes and synchronization
of all **27 production item batches**. Native capacity pickup now explains a
rejection and offers explicitly validated native wielding/Cancel; auto-pickup
never changes equipment. Decision prompts/choices strip terminal color tags
without losing symbols/text. Craft resume R stays inside its slot and only
selects, without starting work. CWM stays 2.15; canonical save rules unchanged.
User accepted **16 manual points** (equipment, consumption, medicine, crafting).
Ranged/reload and transfer checklists remain pending; four focused UI/mapping
rechecks bring the usual backlog to **12**, no tests required from the user today.
Both reconstructed runtimes are installed with rollback copies. Scope/evidence:
[inventory feedback](docs/fixes/inventory-feedback-2026-10-09.md).
Mapping: 1,080 records, 396 runtime representations, 89 attributed textures;
105 selected but unsupported assets and 579 no-match records use fallback.
[Mapping report](docs/fixes/item-mapping-2026-10-09.md). Procedural variants
recommended in batches are not implemented by synchronization.
The UX-01 layout above supersedes that delivery’s next-step recommendation.
Remaining steps: sequential paid native actions, improved confirmations,
recipe history and interactive hotbar. [Detailed source-based plan](docs/design/inventory-and-native-dialogs.md).
The broader M5.5 gate remains historical FAILED and full SAVE-001 stays OPEN.

The transfer delivery below is historical; its 24-pending counter describes
acceptance before the latest user feedback, superseded by the current backlog.

Current delivery: [native quantities, drop and owned-container transfers](docs/fixes/native-transfer.md),
CWM 2.15. I → Quantita e trasferimenti offers a read-only pair of panels,
positive partial charge quantities, current-tile ground deposit and an explicitly
selected owned native container. ACT_DROP/ACT_INSERT_ITEM own access, costs,
removal and work; I pauses/cancels. Native identities/ancestry, quantities,
position, capacities and pause/busy state are revalidated at admission/execution.
No optimistic inventory edits, implicit unsealing or delayed paused inputs.
Canonical saved insert work resumes and transfers once in the actual renderer;
a dropped loaded bag retains its contents, confirmed by pristine core reader.
Scoped native PASS: 16,659 assertions / 113 cases (CWM, pickup, pocket, reload,
diving); Luanti 308 tests plus 648 assertions / 4 cases; protocol 9/9.
Both reconstructed runtimes installed with the previous 2.14 pair retained.
[Exact receipts](docs/fixes/native-transfer-evidence.json) record 145 checks
in six renderer sessions and independent save checks; manual acceptance is deferred, four new points bring the usual
backlog to **24 PENDING**. External containers/cargo, manual per-pocket placement,
fluid transfers/seals and batch moves remain later slices. Next essential slice:
nearby external containers and selected-quantity collection using these interfaces.
M5.5 remains historical FAILED; full SAVE-001 remains OPEN.

The CWM 2.14 delivery below is historical, superseded by the current 2.15;
its original scoped identities and evidence remain preserved.

Current delivery: [native aiming, shooting and reload](docs/fixes/native-ranged.md),
CWM 2.14; both reconstructed runtimes installed together. F held aims using
native move credit, LMB fires once with native ballistics, R uses native ammo
choices/confirmation and canonical ACT_RELOAD. I pauses/interrupts reload;
manual/menu pause grants no free aim and busy inputs do not replay later.
Paid aim remains steady between real-time inputs without automatic improvement;
movement/other actions/recovery end it. Native aim-cache perception recursion
and absolute/local target confusion are repaired; the presentation ray uses
native weapon range rather than Luanti hand reach. Only perceived hostile
identities and the actual wielded ballistic mode are admitted and revalidated.
Scoped native PASS: 86,045 assertions / 107 cases including native reload,
coverage and shooter-accuracy checks; Luanti 308 tests plus 648 assertions /
4 cases; protocol 8/8. Actual-renderer and pristine canonical-save evidence:
[exact receipts](docs/fixes/native-ranged-evidence.json). Native saved reload
resumes and transfers ammunition once, including actual installed runtimes.
Four new ranged points bring [the usual manual backlog](docs/validation/pending-manual.md)
to **20 PENDING**; automatic checks never imply user acceptance. Free reticle,
neutral targets, bows/RAS, mounted/vehicle weapons, mode selection, arbitrary
reload quantities/items and complete weapon animation/feedback remain later
slices. Next essential slice: deep inventory quantities/drop/transfers and
external containers. M5.5 remains historical FAILED; full SAVE-001 is open.

The CWM 2.13 delivery below is historical, superseded by current 2.14;
its original scoped identities and evidence remain preserved.

Current delivery: [guided native crafting](docs/fixes/native-crafting.md),
CWM 2.13; both reconstructed runtimes installed together. K opens known recipes,
native book/helper knowledge, requirements, search and manual batches 1–20.
Native component/source choices and an explicit summary precede creation;
favored/equipped types and nonempty liquid containers are protected components.
ACT_CRAFT and the canonical work item own costs/progress/failures/results.
K/I pause and interrupt; K resumes owned or accessible nearby surface work.
Canonical in-flight work reloads in the actual renderer and completes once;
an independent pristine core confirms exact results and the protected favorite.
Scoped PASS: CDDA 84,101 assertions/83 cases; Luanti 308 tests plus 648 Catch2
assertions/4 cases; protocol 7/7. Installed renderer crafting: 27 RT/save,
11 in-flight reload and 19 ordinary-mode checks; medicine 35 + 14 reload,
consumption 31 and equipment 29 regression checks, 166 total. Exact
source/binary identities and receipts: [evidence](docs/fixes/native-crafting-evidence.json).
Four new crafting points bring [the manual backlog](docs/validation/pending-manual.md)
to 16 PENDING. No automatic result implies user acceptance. Liquid/gas and
byproduct recipes, practice/buildings, recipe favorites/subrecipes, per-instance
components, vehicle work, reading/disassembly and general acceleration remain
later slices; the entire crafting/reading roadmap point is not complete.
Next essential slice: native ranged combat/aiming/reload. Deep inventory and
extended jobs stay scheduled. M5.5 remains historical FAILED; full SAVE-001 open.

The CWM 2.12 delivery below is historical, superseded by the current 2.13
runtime; its identities and scoped evidence remain preserved.

Current delivery: [native wound treatments](docs/fixes/native-medicine.md),
CWM 2.12; reconstructed runtimes installed together. I offers Medica... for
owned external heal items, native body-part selection and explicit confirmation.
Canonical ACT_FIRSTAID owns time/proficiencies, effects and final item removal;
I permits pause/interruption and H displays known wound/treatment names.
Native saved in-flight first aid resumes through the actual renderer and
completes once, confirmed by the independent pristine core.
Scoped PASS: CDDA 8,131 assertions/55 cases; Luanti 308 tests and 648 Catch2
assertions/4 cases; protocol 6/6; installed renderer 35 treatment, 14 native
in-flight reload, 25 ordinary-mode, 31 consumption and 29 equipment regression
checks (134 total). [Exact evidence](docs/fixes/native-medicine-evidence.json).
Four new manual points bring [the backlog](docs/validation/pending-manual.md)
to 12 PENDING; automatic evidence does not imply user acceptance. Oral/liquid
medication, other patients/surgery and part-to-item initiation are later slices.
Next: guided crafting. M5.5 remains historical FAILED; full SAVE-001 is open.

The CWM 2.11 delivery below is historical, superseded by the current 2.12
runtime; its binary identities and evidence remain preserved.


Current delivery: [native food/drink consumption](docs/fixes/native-consumption.md),
CWM 2.11; reconstructed runtimes installed together. I offers Mangia/Bevi
for owned accessible FOOD/DRINK, native duration and warnings. ACT_CONSUME
owns serving removal, containers, digestion and effects. Progress is native
work; I offers explicit interruption while busy, with stale-token and
at-most-once guards. Manual/menu/threat pause and reconnect remain coherent;
movement/gameplay requests made during consumption are not deferred.
Canonical in-flight actor work is saved/read by the independent pristine core
and resumed by the actual renderer. Scoped PASS: CDDA 7,939 assertions/52
cases, Luanti 308 individual tests and 648 Catch2 assertions, protocol 6/6;
renderer 33 reconstructed, 33 installed, 14 in-flight reload, 22 ordinary,
and 29 equipment regression checks.
[Exact evidence and reproduction](docs/fixes/native-consumption-evidence.json).
Manual acceptance remains PENDING: four new consumption checks join the four
inventory checks in [the usual backlog](docs/validation/pending-manual.md).
MED/special-use items, seals, liquid transfer and arbitrary quantities remain
later slices. Next: medicine for an explicitly selected object/body part,
then crafting. M5.5 remains historical FAILED; full SAVE-001 is still open.

The CWM 2.10 delivery below is historical; its binaries and evidence are
preserved separately from the current 2.11 runtime.

Current delivery: [native inventory/equipment](docs/fixes/native-equipment.md),
CWM 2.10; both reconstructed runtimes installed. I opens native owned objects,
search/filters, pocket provenance and capacities. Wield/stow/wear/takeoff use
native item_locations, action costs and disposal choices; no optimistic
inventory mutation or free hotbar equipment. Refresh/reconnect/resync discard
stale handles. Native takeoff can drop a loaded bag when storage is unavailable,
with its contents preserved; the UI explains this possibility.
Scoped verification PASS: CDDA 7,824 assertions/49 cases; Luanti 308 tests
and 648 Catch2 assertions; protocol 6/6. Actual renderer: reconstructed and
installed real-time 29/29 each, installed ordinary mode 26/26, actual native
reload 11/11 including unchanged position and time for read-only inventory.
The independent pristine-core reader confirms each fixture item exactly once.
Exact identities and reproducible commands: [evidence](docs/fixes/native-equipment-evidence.json).
Manual acceptance is PENDING: user cannot test now; four checks saved in
[the usual checklist](docs/validation/pending-manual.md). Prior accepted
features remain accepted. Quantities, targeted pocket/external-container
transfers, sealed/technical contents and timed quick equipment remain later
slices. Next essential step is consumption/medical basics, then crafting.
M5.5 remains historical FAILED; full SAVE-001 is still open.

The CWM 2.9 presentation delivery below is historical, superseded by the
2.10 runtime above; its evidence preserves the corresponding old binaries.

Current delivery: [compact icon HUD / shallow prone dip / X](docs/fixes/icon-survival-hud.md),
CWM 2.9. All four familiar-control/pause/camera adaptations have explicit user
PASS (in addition to the original four feature checklists). The last requested
HUD polish must not add another manual gate. X is the configurable default
prone toggle; the shallow prone camera dips 0.08 nodes. Centered ten-icon rows
show native perceived hunger, hydration, rest and comfort, separate vital
head/torso hearts, stamina and read-only possessions, without the old survival
background or permanent labels. H keeps detailed native descriptions. Gameplay
rules and canonical save fields are unchanged. Debug overlay hotkey/settings
are recorded for production, not implemented in this slice.
Current verification PASS: CDDA 7,665 assertions/44 cases, Luanti 307 tests
and 648 Catch2 assertions, protocol 5/5; reconstructed and installed controls/
water GUI 32/32 each, ordinary-mode body GUI 19/19 including exact native HP
and position/time/stamina preservation. Source/runtime identities and scope
are in the [evidence](docs/fixes/icon-survival-hud-evidence.json).
[Current plan summary](docs/progress/2026-10-08.md): inventory/equipment, then
consumption/medical essentials and crafting before vehicles. M5.5 remains
historical FAILED and full SAVE-001 remains open.

The following CWM 2.8 delivery paragraphs are historical, superseded by the
2.9 presentation slice above; their runtime hashes belong to their own evidence.

User validation on 2026-10-08: pickup, body HUD/sheet, pointed melee and
native run/postures all four checklist items PASS each. [Feedback](docs/source/playable-core-feedback-2026-10-08.md)
authorizes familiar hold controls and visual pause/camera fixes. Earlier
pending entries below describe their delivery dates, not current acceptance.


The [familiar controls and survival presentation](docs/fixes/controls-and-survival-presentation.md)
are implemented and the verified Luanti runtime is installed (CWM 2.8 remains
unchanged). Left Ctrl/Shift hold native run/crouch, optional toggle preferences,
P latched prone. Native contextual modifiers remain functional; a bounded
opening click survives only its posture roundtrip and is cancelled on pause/
recovery. Native display segments use Mineclonia hearts/armor/stamina icons;
owned items have a read-only strip. H freezes pickup/node/shader animations,
S no longer selects table rows, prone shallow-water camera stays above the
surface, and unavailable running has a readable explanation.
CDDA 7,448 assertions/43 cases; Luanti 307 tests/648 Catch2 assertions; protocol
5/5 PASS. Installed controls GUI: 27 held, 22 toggle, 24 ordinary-mode checks;
actual reload 8; body regression 19 (all 12 native HP unchanged), pickup 18, vertical 17 and
melee 23 (including native knockback) PASS.
An additional 15-check actual Ctrl+W/Shift+W movement test confirms native
speed hierarchy. A subsequent body scroll-only polish has 21 reconstructed
and installed GUI checks and unchanged 307/648 engine results; its binary identity is
recorded separately from the preceding control runs.
Source identities, remaining scope and results are in the [evidence](docs/fixes/controls-and-survival-presentation-evidence.json).
The [four-point adaptation checklist](docs/validation/pending-manual.md) was
subsequently manually accepted in full. Full diseases/medical UI, quantitative hunger redesign and
native timed quick equipment switching remain future work. No full M5.5 or
SAVE-001 certification is claimed.

Earlier delivery entries below retain historical controls, protocol versions
and pending states; subsequent explicit user validation supersedes those.

The fourth independent [native running/posture slice](docs/fixes/native-postures.md)
is implemented and CWM 2.8 runtimes installed. R toggles run/walk, X crouch/walk,
P prone/walk; native speed, stamina, noise, exhaustion and canonical mode
remain authoritative. First-person camera follows confirmed posture. Scoped
verification PASS: CDDA 7,448 assertions/43 cases; protocol 5/5; Luanti 306
individual tests/648 Catch2 assertions. Installed posture GUI: 16 continuous,
12 ordinary-mode and 8 actual save-reload checks. Body regression 19, pickup 18,
melee 21 checks pass. Native save reading uses pinned pristine CDDA. Evidence
and exact source identities are [recorded](docs/fixes/native-postures-evidence.json).
The user explicitly requested a third deferral and autonomous work on another
essential independent feature. All four [manual checklists](docs/validation/pending-manual.md)
were subsequently explicitly validated. Third-person rigs/animations remain future work; no full
M5.5/SAVE-001 certification or manual acceptance is claimed.

Earlier delivery entries below retain historical protocol versions and test
counts; current installed runtime evidence is the CWM 2.8 slice above.

The independent [pointed melee slice](docs/fixes/pointed-melee.md) is implemented
and both CWM 2.7 runtimes installed. Left click targets perceived adjacent
hostiles; CDDA owns weapon rules, passive defenses, damage, practice, stamina
and cost. Native tests: 7,297 assertions/38 cases; protocol: 5/5; Luanti:
306 tests/648 assertions. Installed melee GUI: 21 ordinary-mode and 23 continuous
4x checks, including native knockback, range rejection, recovery and pristine
canonical corpse reading. Body GUI regression: 19 checks; pickup: 18 checks. The user explicitly deferred both
previous manual validations again and authorized this essential independent
feature autonomously. All three [manual checklists](docs/validation/pending-manual.md)
remain pending. No full combat, M5.5 or SAVE-001 certification is claimed.

The recovered local continuation now has the ground-item PICKUP backend
and its [Mineclonia container/pointer interface](docs/fixes/ground-items-ui.md)
implemented. Scoped automated verification PASS; both runtimes are installed. Native CDDA
checks pass with 7,032 assertions, Luanti with 305 tests, and installed GUI
runs with 15 ordinary-mode and 18 continuous-mode checks. User visual
validation of this interface is pending and explicitly deferred by the user
on 2026-10-08. The [saved manual checklist](docs/validation/pending-manual.md)
must be delivered together with the next independent feature.
CWM 2.5 adds read-only native possessions to guarded, deduplicated pickup.
Nine production mapping batches remain an independent lane. The lower panel
is read-only. The independent survival HUD/read-only body status is implemented below;
interactive inventory/equipment follows later.
The independent [survival HUD/body sheet](docs/fixes/body-status-ui.md) is now
implemented with scoped automated verification PASS and installed CWM 2.6 runtimes.
H opens a read-only native sheet with menu pause; local Luanti HP/breath/hotbar
are suppressed. Native CDDA: 7,049 assertions in 32 cases; Luanti: 306 tests;
protocol: 5/5; installed body GUI: 16 ordinary-mode and 18 continuous-mode
checks, plus exact native HP comparison for all 12 parts. Pickup regression:
18/18 with the new installed runtimes. Both manual checklists remain pending;
no new manual acceptance or full M5.5/SAVE-001 certification is claimed.
Historical backend evidence is
[retained](docs/fixes/ground-items-pickup.md).

The [complete implementation plan](IMPLEMENTATION_PLAN.md) now incorporates
all 15 source-grounded feature questionnaires. Detailed accepted decisions
are in [the product directive](docs/source/feature-decisions-2026-10-04.md).
FND-01 (canonical startup/loading and shared native turns) is implemented with
scoped verification PASS; see [the repair](docs/fixes/canonical-runtime.md).
Existing-avatar/time preconditions now pass through the actual 3D client.
Full SAVE-001 remains incomplete; the failed M5.5 gate has not been recertified.
FND-02 (bounded framing, queues and nonblocking I/O) is implemented with
scoped verification PASS; see [the transport repair](docs/fixes/fnd02-transport.md).
Final complete frames survive EOF, malformed framing/FlatBuffers close the
offending connection, and slow readers cannot cause peer-dependent send waits.
The real renderer and isolated native saves are included in verification.
FND-03 (negotiation, identities, deduplication, sequencing and coherent recovery)
is implemented with scoped verification PASS; see [the session repair](docs/fixes/fnd03-session-recovery.md).
CWM 2.0 gates input on installed full state, deduplicates commands across
connections, and freezes/resynchronizes the actual renderer after gaps or
invalid updates. Both runtime binaries and compiled launcher aliases are installed.
The user [accepts the FND-03 manual checklist](docs/source/fnd03-manual-validation-2026-10-04.md)
and authorizes continuation. Visual state inversion on some stone-building
doors and the center hinge on one double-door leaf remain low-priority reports;
neither is claimed fixed or reproduced. A [scoped FND-04 slice](docs/fixes/fnd04-vertical-navigation.md)
now implements recognizable native vertical connections and authoritative
up/down input, with scoped verification PASS and installed runtimes. Jump
ascends; Sneak + Jump descends, once per press. Stairfinding, underwater
transitions and save/load on other floors remain native. `vertical-demo.sh`
provides a persistent isolated manual fixture; the user
[accepts all four manual checks and the visual transition](docs/source/vertical-validation-2026-10-04.md).
No additional manual checks are needed to accept this slice. Revisit automatic,
continuous traversal of stairs and ladders with the user when the first real-time
scheduler prototype is playable, before choosing the final controller.
Full FND-04 and M5.5 are not recertified.
The next authorized [actor lifecycle slice](docs/fixes/fnd04-actor-lifecycle.md)
persists monster identity in native Creature metadata using the native world
character-ID allocator; NPCs retain their canonical IDs. Motion, multi-Z,
bubble departure/return, reconnect, native save/reload and pristine writer
roundtrips have scoped coverage. The real renderer removes owned scene nodes,
replaces changed archetype meshes and snaps re-perceived/recovered actors to
their confirmed position without animating unseen motion. Invalid actor-kind
aliases and contradictory lifecycle metadata are rejected before ingestion.
`actor-demo.sh` provides the persistent isolated manual fixture. This does not
implement animations, real-time scheduling, local light or full FND-04 conformance.
The user [accepts all three actor lifecycle manual checks](docs/source/actor-lifecycle-validation-2026-10-04.md).
No repeat checklist is needed. Black-screen loss of context after leaving the
demo road is reported separately, not yet reproduced; preserve that demo save.
The authorized [RT-01 real-time prototype](docs/prototypes/rt01-real-time.md)
implements paced native turns, idle AI, global speed, manual/menu/threat/recovery
pauses and held movement intent. `realtime-demo.sh` offers the isolated manual
scene; ordinary `start.sh` remains action-driven unless explicitly opted in.
Scoped verification is recorded in its evidence. The user
[accepts the scoped manual checklist](docs/source/rt01-validation-2026-10-04.md),
but rejects the base 1x pace as too slow and asks about the planned continuous
controller. The subsequent local continuation implemented the RT-02 native
continuous offset at the user's preferred global 4x pace. Its motion/rebase
manual test was accepted in the [recovered continuation](docs/source/continuation-2026-10-07.md).
RT-01 is historical baseline evidence; do not repeat its accepted scheduler
checklist or treat RT-02 as still unimplemented. Final balance and automatic
continuous stairs/ladders remain separate decisions.
Automatic continuous stairs/ladders must now be revisited with the user before
choosing the final controller. Other phase-2/FND-04 criteria remain open.
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
underwater/vertical input, furniture assets and upper-floor navigation were
incomplete at that repair. The later vertical slice above covers native
connections and immersion controls; free climbing, vertical vehicles,
underwater perception and complete furniture assets remain pending.
Historical M5.5 and SAVE-001 outcomes remain unchanged.

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
The accepted manual cases do not need another gate before FND-04 work.

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
