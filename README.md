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

Current Linux slice: [native NPC conversations](docs/fixes/native-conversation.md)
are available in `./start.sh`: point at a perceived, non-hostile NPC and
**right-click**. Native choices pause time, with current text, transcript and
social trials. `./conversation-demo.sh --fresh` opens an isolated NPC scene.
Dedicated NPC trading remains planned; its current option explicitly cancels.
[Native item disassembly](docs/fixes/native-disassembly.md), including resume
and canonical persistence, remains available. Human rechecks are separately
pending in the ledger. The Windows installer above remains its previous
CWM2.26 snapshot; this delivery updates Linux to CWM2.28.

This project aims to merge the 2D turn based videogame Cataclysm Dark Days Ahead(CDDA) with the 3D voxel real time game Mineclonia(as the name suggests, an open source minecraft clone) with the goal to provide CDDA with a 3D voxel engine.
FAQ
A: Why did you choose to make this?
B: I really love CDDA and I think it deserves more recognition, and I think that with with a 3D voxel interface that is very familiar to the public it will be easier for casual gamers to hop into the game
A: Is this yet another AI generated slop game?
B: It indeed relies on heavy use of agentic AI and web chat AI, but I am making sure I guide the design choices, I understand the software architecture, and in general assure the quality of the products.
WIP
