# Human testing and AI authorship

**The `PASS` entries in [pending-manual.md](docs/validation/pending-manual.md)
record tests actually performed by a human: this project's sole developer. They
are not results invented by an LLM, automated test results, or an agent's opinion
that a feature should work.** The developer plays the integrated game, reports
PASS/FAIL and comments, and directs subsequent changes.

**The developer also conducts extensive general playtesting beyond those
checklists.** This includes refining features that already pass their functional
checks, discovering useful new features, and evaluating whether the game loop,
mechanics and interfaces feel enjoyable, fluid and understandable to a person.
The developer is **not a UI/UX designer**; these are hands-on observations and
design decisions from the person developing and playing the game.

**This document was written by an LLM, following direct, explicit instructions
from that sole human developer on 2026-10-18.** The developer requested that this
authorship and the human origin of the testing be stated clearly. This is an
LLM-written account of the developer's instructions and reported experience,
not a separately authored human testimonial or an independent external review.

## What has been tested

Development uses extensive LLM-generated code under the human developer's
direction. The current development line includes features that the developer
has personally tested and marked `PASS` in the manual ledger, including core
interactions, inventory/equipment, consumption, treatment, crafting, ranged
combat, containers, dialogs and persistence within the tested scenarios.

The latest [seven core gates](docs/source/manual-core-gates-2026-10-18.md) were
all reported PASS by the developer. The same feedback identified additional
crafting, opening-control and lighting issues; passing a gate does not erase
those observations. General playtesting informs the roadmap even when a
checklist passes.

The ledger preserves chronology, untested cases, failures and deferred personal
rechecks. A PASS applies to the scenario and version actually played. Subsequent
code changes are checked automatically where possible, but new or changed
behavior still awaiting the developer's playtest stays `PENDING`. A dated PASS
must not be interpreted as a claim that the human has replayed every scenario
on every later commit, or that all planned game features are complete.

## Where to find the evidence

- **[Manual PASS/FAIL, comments and outstanding tests](docs/validation/pending-manual.md):**
  the human testing ledger. Historical delivery counts are dated snapshots.
- **[Implementation status](IMPLEMENTATION_STATUS.md):** what is implemented,
  what was verified automatically and what is still incomplete.
- **[Implementation plan](IMPLEMENTATION_PLAN.md):** accepted design decisions,
  remaining work and deferred graphical validation.
- **[Fix reports](docs/fixes/):** scoped engineering checks and artifact identities;
  automated checks are evidence separate from human acceptance.

Historical conformance findings remain visible: the M5.5 audit failed and the
full SAVE-001 gate is open. Human PASS entries and later scoped fixes do not
silently promote either global gate.
