# Ten consecutive core presentation steps — 2026-10-18

Authorized by the user's request for ten roadmap steps without another personal
gate. These extend the existing core consolidation, before vehicles/M6.

1. Perceived native melee/fire attacks animate the actor, including misses.
2. Native inflicted damage produces a short visible reaction; the player's
   injury cue does not infer attacker identity. No camera shake or forced aim.
3. Native *heard* sounds become audio and readable captions. Hearing, sleep,
   deafness and weather attenuation stay native. An unseen sound discloses no
   position, creature ID or type beyond CDDA's own directional description.
4. The actual wielded object appears in first person; a firearm uses a held
   aim/recoil pose rather than a mining/punch animation. No aim-rule changes.
5. Canine family proxy using the pinned Mineclonia wolf model/material/cycles.
6. Spider family proxy using the pinned Mineclonia spider model/material/cycles.
7. Small ground bird proxy using the pinned chicken model/material/cycles.
   Only explicitly supported native IDs map to these generic appearances.
8. A darkness cue uses native illumination at the player; it explains limited
   perception without revealing hidden actors or changing visibility.
9. An underwater tint/label uses native underwater state, without revealing
   unloaded terrain, changing swimming or adding a separate oxygen mechanic.
10. Persistent diagnostic panels default off; the existing rebindable F3/debug
    action toggles them. Pause, recovery, threat, decisions and work stay visible.

Events are bounded transient presentation data collected in native actions and
published in the existing snapshot batch, never socket writes in gameplay code.
They have monotonic IDs, are not saved, and are not replayed across resync. No
damage/attack inference from proximity or health differences. Unsupported special
attacks and creature shapes retain their current fallback rather than claiming
complete bestiary coverage. New manual checks remain PENDING in the shared file.

Verification: reconstructed native/client builds, event visibility/hearing and
batch lifecycle checks, protocol rejection/recovery tests, actual-renderer
material/cycle/cue checks and installed-runtime smoke tests in isolated worlds.
Audio output dispatch can be verified automatically; perceived loudness/timbre
and visual comfort remain personal tests. Full SAVE-001 remains OPEN and the
historical M5.5 remains FAILED.
