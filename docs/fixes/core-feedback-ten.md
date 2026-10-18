# Ten consecutive core feedback steps — 2026-10-18

The ten scoped roadmap slices in the [contract](../design/core-feedback-ten-steps.md)
are implemented and installed in ordinary `./start.sh`, using **CWM 2.24**.
These are core consolidation slices, not ten completed M0–M9 milestones.

1. Native character/monster melee and fired shots trigger short attack poses,
   including native misses. Unsupported special attacks do not invent poses.
2. Actual damage through the native damage path triggers a brief skin/pose
   reaction or player tint. No camera shake, knockback or hit-point inference.
3. The native hearing path publishes sounds after attenuation, deafness, sleep
   and NPC gates. The client dispatches audio and readable captions without
   revealing exact locations or identities of unseen sources. OpenAL is now
   enabled: the previous client was compiled with `ENABLE_SOUND=OFF`.
4. The real native wielded object is rendered in first person using its mapped
   icon/category art as an extruded proxy. The firearm pose follows held aim
   and native shot events, instead of displaying a mining/punch gesture.
5. Explicit dog/wolf/coyote archetypes use the pinned wolf rig and cycles.
6. Explicit small/large spiders use the pinned spider rig and cycles.
7. Chicken/grouse and supported chicks use the pinned ground-bird rig/cycles.
8. Native ambient illumination supplies a subtle low-light cue and explanation.
9. Native underwater state supplies a blue tint and explicit immersion cue.
10. Large diagnostic panels default off. The rebindable debug action (default
    F3; old personal configurations may retain F5) toggles them. The default fog
    toggle moves to F5. Pause/recovery, threat, decisions and work remain visible.

Events are bounded to 128 per publication, collected on the simulation thread,
not saved, and drained once. Full/recovery state contains no transient events.
Cue IDs are deduplicated within a native session even across a full resync.
Presentation phases freeze/scale with the existing native visual clock. No new
AI, time costs, save state, local gameplay authority or visibility rules.

## Verification and reproducibility

Exact source/build/runtime identities, commands, logs and screenshots are in
[the evidence receipt](core-feedback-ten-evidence.json). Artifacts are under
`artifacts/core-feedback-20261018/`; isolated native saves and private X displays
were used throughout. Production builds were incremental reconstructions,
retaining caches; enabling audio rebuilt a substantial part of the client.
This is not a cold clean-build certification.

The passing scope is 98 native cases / 65,402 assertions; 309 client tests /
47 modules plus 648 Catch assertions / 4 cases; 12 protocol tests; 9 language
checks and 6 launcher checks. There are 231 renderer/canonical checks across six
runs (46 + 24 + 43 reconstructed; 47 + 28 + 43 installed).

The receipt distinguishes reconstructed and installed runs. Actual native
melee/ranged tests verify actor identity, damage, move costs, pauses, reconnect,
reloading and canonical saves with the separate pristine native reader. The
controlled renderer verifies actual mesh materials/frames/bounds, visibility,
three families, native cues, wielded visuals, darkness/immersion, pause and
resync. Its synthetic water flag is a presentation check, not a swimming test.
Audio dispatch and assets are automatic evidence; timbre/loudness/comfort remain
manual acceptance. Test audio uses OpenAL's null driver on private displays.

There are **28 PENDING + 1 manual FAIL** in the [personal backlog](../validation/pending-manual.md).
Ten new entries are deferred. Earlier PASS stay accepted; the equipment-pause
manual FAIL is not cleared by passing installed regressions.

## Failures retained and investigation

- The first native invocation used the wrong custom CLI spelling; native
  `--user-dir=<path>` requires `=`, while Catch's RNG seed uses a separate value.
  One case-list invocation also used the wrong data working directory. Logs
  are retained, and these commands are not counted as passing verification.
- The visibility fixture initially assumed blindness concealed an adjacent
  actor; the native implementation can still perceive it. The fixture now
  requires actual native non-perception and refreshes sight caches after
  changing vision, as upstream vision tests do, to avoid test-order dependence.
- The expanded opt-in statistical melee suite crashed in its own unarmed INFO
  diagnostic by dereferencing an absent weapon. Only that diagnostic was fixed;
  statistical assertions and gameplay were unchanged.
- After that repair the expanded suite had **5 failing cases / 11 assertions**.
  All five case names reproduce as failing against the previous independent
  `artifacts/fnd02-transport/workspace` executable (equipped sections used for
  the first two to avoid its unpatched null diagnostic). These tests calculate
  hit/dodge rolls directly, without invoking the new presentation hooks.
  Their old numeric expectations remain unresolved; the expanded suite is
  explicitly not declared passing and no balance change was made to satisfy it.
- The renderer found an actual F3/fog binding conflict; bindings and priority
  were corrected. Animated bird bounding boxes change during walking, so the
  scale probe now allows bounded cycle variation instead of requiring a rigid
  rest-pose height. Material, frame and movement assertions remain active.
- An installed held-aim test sampled its baseline before the renderer observed
  the physical release. The trace shows the last paid aim was sent before
  `aim_held` became false. It now waits for that observed edge and settled work,
  then enforces no further aiming. The failed attempt is retained.
- Supervisor stubs first used a project-root expectation inconsistent with the
  compiled aliases. Using their actual configured root passes all six checks;
  no production launcher check was relaxed.

## Remaining scope

Art is generic and provisional. This does not claim exact clothing/anatomy,
all creatures, all special attacks, all damage mechanisms, flying birds,
third-person firearm attachments, complete audio/SFX or spatialized hidden
sound sources. Reload and other SFX-only paths still need a native hearing-aware
presentation slice; short one-shot tails are not paused mid-sample. Darkness
and immersion cues do not solve the wider horizon/fog-of-war prototype or expose
unexported terrain. The flatness/controller/driving choices stay deferred.

The next functional core slice is native reading/disassembly and related item
work interfaces, using existing activity/decision/pause foundations. More
bestiary/weapon assets and SFX can extend these explicit presentation seams.
Full **SAVE-001 remains OPEN** and historical **M5.5 remains FAILED**. No milestone
or personal validation is promoted by these scoped checks. Item mapping batch60
is unchanged.

## Audio build dependencies

Configure the production client with `-DENABLE_SOUND=ON`, OpenAL, Ogg and
Vorbis development headers, retaining the existing gettext/build options.
This machine already has the runtime libraries. To avoid system changes, the
build extracted `libopenal-dev`, `libogg-dev`, and `libvorbis-dev` locally with
`apt-get download`/`dpkg-deb -x`; exact package files/hashes and CMake paths are
recorded in the receipt. No sudo or system package installation was used.
Media files are unchanged pinned Mineclonia assets; checksums, source paths and
upstream attribution notices accompany `game/mods/cdda_entities/presentation-assets.json`.
