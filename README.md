# Minecataclysm

**Human-tested, AI-assisted development:** every manual `PASS` in
[the testing ledger](docs/validation/pending-manual.md) was reported by the
project's **sole human developer**, who also conducts extensive general
playtesting to refine gameplay, fluidity and interfaces. The developer is not
a UI/UX designer. **This notice and the [full testing/authorship statement](HUMAN_TESTING.md)
were written by an LLM on the developer's direct, explicit instructions.**
Automated verification and pending personal rechecks are recorded separately.

[Human testing and AI authorship](HUMAN_TESTING.md) ·
[Current implementation](IMPLEMENTATION_STATUS.md) ·
[Full plan](IMPLEMENTATION_PLAN.md) ·
[Manual PASS/FAIL and outstanding tests](docs/validation/pending-manual.md)

Windows 11 x64: the local installer is generated as
`dist/windows11/Minecataclysm-Windows11-Setup.exe` (not tracked in Git).
[Delivery and verification](docs/releases/windows11-2026-10-21.md) ·
[Windows build instructions](tools/windows/README.md). Real Windows hardware
acceptance is recorded separately from automated Wine verification.

Current Linux slice: [playtest recovery/presentation fixes](docs/fixes/playtest-feedback-2026-10-25.md)
in `./start.sh`: clearer/faster native rest with x64/x256/x1024, ground-container
pouring and empty-can pickup, stable menu pointer, consistent confirmations,
a shared skin/model boundary and a native night sky. `./liquid-recovery-demo.sh --fresh`, `./rest-demo.sh --fresh`, `./night-demo.sh --fresh` provide isolated
scenes. Linux uses CWM2.35; the Windows installer remains CWM2.26.

Previous Linux slice: [native sealed-pocket opening](docs/fixes/native-seals.md)
in `./start.sh`. I → owned sealed container → **Open sealed pocket...**.
Native preservation/spill rules and costs apply; Cancel before opening keeps
the seal intact. `./seals-demo.sh --fresh` opens the isolated test scene.
Both Linux runtimes use CWM2.34; the Windows installer remains CWM2.26.

Previous Linux slice: [native water sources and liquid pouring](docs/fixes/native-liquids.md)
in `./start.sh`. Right-click a recognized nearby source to collect/drink;
I → selected liquid/container → **Pour liquid...**. Capacity, quality, remainder,
freezing and costs are native. I pauses and interrupts real filling; canonical
fill work survives reload. `./liquids-demo.sh --fresh` opens the isolated scene.

[Native rest, sleep and waiting](docs/fixes/native-rest.md) remains available:
**B** opens its native context; `./rest-demo.sh --fresh` opens the isolated bed scene.

[Individual companion orders/rules](docs/fixes/native-companions.md) remain
available: right-click a local ally and choose **Companion orders and rules**.
`./companions-demo.sh --fresh` opens the isolated ally scene.
[Minimum-core outlook](docs/progress/core-outlook-2026-10-23.md): the estimate before
this water slice was approximately **94% (93–96%)**, excluding pending personal
tests. Essential item uses, safe liquid crafting/purification and
non-demo survival-loop/performance/recovery consolidation remain. This is an
engineering estimate, not completion of the full approved game.

[Known mission journal](docs/fixes/native-journal.md) remains available in
`./start.sh`. **Press J** for native Active / Completed / Failed histories,
known objectives, destinations and deadlines. **Track this mission** changes
the native tracked mission explicitly; browsing never accepts or completes one.
`./journal-demo.sh --fresh` opens an isolated scene with prepared mission histories.
[Native NPC trading](docs/fixes/native-trade.md) remains available: right-click
a perceived non-hostile NPC and choose its native trade reply.
[Native conversations](docs/fixes/native-conversation.md) and
[item disassembly](docs/fixes/native-disassembly.md) remain available.
Human rechecks are recorded separately in the ledger. Linux uses paired
CWM2.33 runtimes; the Windows installer remains its earlier CWM2.26 snapshot.

This project aims to merge the 2D turn based videogame Cataclysm Dark Days Ahead(CDDA) with the 3D voxel real time game Mineclonia(as the name suggests, an open source minecraft clone) with the goal to provide CDDA with a 3D voxel engine.
FAQ
A: Why did you choose to make this?
B: I really love CDDA and I think it deserves more recognition, and I think that with with a 3D voxel interface that is very familiar to the public it will be easier for casual gamers to hop into the game
A: Is this yet another AI generated slop game?
B: It indeed relies on heavy use of agentic AI and web chat AI, but I am making sure I guide the design choices, I understand the software architecture, and in general assure the quality of the products.
WIP
