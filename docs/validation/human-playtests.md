# Human playtest results

**The project’s sole human developer played and reported every manual PASS in this index.** An LLM compiled this page from the developer’s direct instructions and reports. The developer also playtests beyond the checklist to refine mechanics, find useful additions, and judge whether the game feels enjoyable and fluid. They are not a UI/UX designer. [Authorship statement](../../HUMAN_TESTING.md)

Updated **2026-11-17**. **21 manual checks are still pending**, including three on real Windows 11 hardware. A PASS applies to the scenario and build played. See the [full ledger](pending-manual.md) for steps, dates, comments and earlier failures, and the [implementation status](../../IMPLEMENTATION_STATUS.md) for automated verification.

## Recorded manual results

The numbers in the result column are the numbered cases in the detailed ledger. “Partial” means the developer reported observations for only part of that case.

| Area | Human result | What was played |
| --- | --- | --- |
| Pickup | 1–4 PASS | Ground items, pickup outcomes, pause and persistence |
| Body and survival HUD | 1–4 PASS | Survival cues, body detail, inspection pause and return |
| Pointed melee | 1–4 PASS | Direct attacks, valid targets, movement separation and pause |
| Running and posture | 1–4 PASS | Movement modes, prone and exhausted running |
| Controls and presentation | 1–4 PASS | Held controls, HUD and water presentation in the tested scenes |
| Inventory and equipment | 1–4 PASS | Hand, worn items, stowing and possession |
| Food and drink | 1–4 PASS | Native choice, consumption, time and effects |
| First aid | 1–4 PASS | Body-part choice, treatment, abort and native effects |
| Guided crafting | 1–4 PASS | Recipe selection, requirements, progress and incomplete work |
| Ranged combat | 1–4 PASS | Aim, fire, reload and state in the tested scenes |
| Quantities and owned containers | 1–4 PASS | Partial quantities, drop and transfer; nested ammo deposit covered by the later UX-03 recheck |
| UI and item mapping rechecks | 1–4 PASS | Item icons, color markup and relevant menu feedback |
| UX-01 inventory layout | 1–4 PASS | Navigation, search and inventory actions |
| UX-02 consecutive actions | 1–4 PASS | Ordinary work and return to inventory. Three exception scenarios are pending |
| UX-03 drag-and-drop hotbar | 1–4 PASS | Assignment, swapping, removal and visual feedback |
| UX-03D hand and worn items | 1–2 PASS | Hand display, worn items and container navigation |
| UX-03 targeted rechecks | 1–3 PASS | Search behavior, visual pause, quantities and errors |
| LANG-01 language preference | 1–2 PASS | English/Italian selection and restart behavior at that stage. The wording regression passed its follow-up |
| AIM-01 held right-click aim | 1–3 PASS | Aiming, context priorities and pause |
| EXT-01 external containers | 1–4 PASS | Storage access, partial pickup and pause. Point 4 passed the follow-up |
| UX-04A native prompts and work feedback | 1–4 PASS | Decisions and visible work progression |
| October 13 feedback rechecks | 1–3 PASS | Later playtests resolved the initial wear/take-off pause failure |
| UX-04B structured medical panel | 1–4 PASS | Anatomy, confirmation, expected effects and persistence |
| UX-05 recipe shortcuts | 1–4 PASS | Favorites, recent starts, actual incomplete work and the tested reload scenarios |
| INT-01 interaction gestures | 1–3 PASS | Doors/windows, Shift-click transfer and dropping outside the window |
| Loose objects and stacks | 1–3 PASS | Direct single-item and stack pickup, with a separate multi-item case |
| Humanoid models | 3 PASS | Player model in third person and inventory preview. NPC and zombie appearance pending |
| Movement animation | 2 PASS | Animations stop when the game is paused. Direction changes and player/actor reappearance pending |
| Core feedback | 4, 9 PASS. 2 partial | Held object in first person and immersion cue. A hit on the zombie produced a red flash. Eight feedback checks remain in total |
| Rechecks after the seven core gates | 1–3 PASS | Search and cursor stability, recipe/batch result, windows and curtains. Gradual darkness is pending |
| READ-01 native books | 1–4 PASS | Identifying a book, studying, pausing and loading |
| LANG-01 language label | PASS | Confirmation wording reflects the selected language |
| LANG-02 live language change | 1–2 PASS | Menus and native prompts change language without restart. Ongoing work and persistence were also checked |
| DIS-01 disassembly | 1–4 PASS | Consultation, work and pause, interruption and reload |
| NPC-01 conversation | 1–4 PASS | Pointing and entering, paused browsing, responses and reload |
| TRADE-01 barter | 1, 2, 4 PASS. 3 partial | Cancel, partial exchange and persistence. The remaining refusal scenarios have been prepared for the next playtest |
| JOURNAL-01 mission journal | 2–4 PASS | Explicit tracking, read-only history and save/reload. Contents and empty state are pending |
| COMP-01 companion orders | 1–4 PASS | Panel access, follow/guard, rule precedence and persistence |
| REST-01 native rest | 1–4 PASS | Wait, pause and interrupt, sleep, speed and persistence. A synchronization failure passed the later human retry |
| LIQ-01 native liquids | 1–4 PASS | Source, transfer, consumption and persistence in the tested cases. Ground spill feedback remains open |
| SEAL-01 sealed containers | 1–4 PASS | Opening, access, stashed can and saved seal state |
| FB-01 follow-up | 1–4 PASS | Cursor, can recovery, earlier rest-speed controls and night sky. Cursor result also covers UX-CURSOR-01 |
| UF8-01 contextual speed | PASS | One F8 control manages rate and restores the awake rate |
| MENU-01 menu continuity | PASS | Related screens replace one another during native work |
| KEY-K-01 crafting inspection | PASS | K pauses the active craft for inspection like I |
| SYNC-01 recovery during rest | PASS | Human follow-up after a sleep connection issue |
| READ-FB-01 native distraction | PASS | Continuing after the cold prompt stays interactive. An additional injury prompt was observed |
| WORK-FB-01 work progress | PASS | Reopen and resume the progress panel during reading and drinking |

The developer also playtested earlier world and movement work, including [terrain and apertures](../fixes/exploration-apertures.md), [vertical travel](../fixes/fnd04-vertical-navigation.md), [actor lifecycle](../fixes/fnd04-actor-lifecycle.md), and the [first continuous movement prototype](../prototypes/rt02-continuous.md). The October 18 [seven core checks](../source/manual-core-gates-2026-10-18.md) were reported as PASS, with separate bug and usability notes.

## Pending manual checks

| Count | Remaining coverage |
| ---: | --- |
| 3 | Work UI when a native warning takes over, the player dies, or the connection is lost |
| 2 | NPC and zombie models |
| 2 | Actor movement and player pose or reappearance |
| 8 | Attack and damage feedback, audio, canids, spiders, ground birds, low light, and diagnostics |
| 1 | Gradual darkness at a light boundary |
| 3 | Installer, first run and save, and update/uninstall on a real Windows 11 PC |
| 1 | Trade refusals, including insufficient credit |
| 1 | Mission journal contents and the empty state |
| **21** | **Total** |

Feedback and defects may remain open after the related scenario passes. Recent examples include intermittent movement delay after recovering breath, the first-person Glock placeholder and recoil cue, and requests to improve dialog scrolling and J/K menu closure. The [latest human feedback](../source/manual-priority-tests-2026-11-17-followup.md) records the observations. Some steps in the detailed ledger refer to local test worlds or logs under `artifacts/`. The public Git history includes the reports and source manifests.

The historical M5.5 conformance audit failed. Full SAVE-001 remains open. See the [audit findings](../audits/M5.5.md) for the scope of those gates.
