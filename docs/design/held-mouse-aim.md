# Held right-mouse aim and context priority

Scope: the accepted assisted aim on perceived hostile creatures with a native
wielded firearm. RMB is the main held input; F remains a keyboard fallback.
No new hit probability, weapon mode, zoom, free-reticle shot or perception rule.
CDDA still owns recoil, turning penalty, move costs, projectiles and damage.

## Gesture routing

Classify each physical RMB press once. With a firearm and a perceived hostile
under the reticle, hold to request native paid AIM steps. Empty reticle may
start an aim gesture, but no AIM is sent until an eligible creature is pointed.
Neutral creatures never become hostile targets through this input.

Without that pointed ranged target, a nearby projected door/window or reachable
ground stack wins. RMB opens/collects; Shift+RMB closes a pointed opening.
The opening cache uses CWM material and stable scene coordinates, including
pane/sill and negative Z floors. It is eligibility for input routing only;
CDDA revalidates range/state and pays the actual action. Ordinary wall/floor
clicks no longer send meaningless OPEN requests. Crouching with Shift does not
prevent aim when the reticle points at the hostile rather than an opening.

A context gesture remains context until RMB release, even if the scene/camera
changes. Holding an opening/collection click never becomes paid aim. A short
press and release received in one frame must still deliver the context click.
Explicit context input takes priority over a simultaneous F hold.

## Timing and interruption

Aim repeats only when the previous command has its authoritative outcome/state;
there is no backlog of aim steps. Release stops generating AIM. Existing native
recoil already paid for remains maintained by the native idle policy until
movement/another native action/recovery, without further improvement. Releasing
RMB does not invent a recoil reset or a gameplay command.

LMB fires once per physical press. While RMB remains held, paid AIM resumes
following the shot. A single explicit fire click or R press may wait for the
currently in-flight AIM step only, bounded to one second, with the same weapon
and (for fire) target identity. No shot waits behind movement, another shot,
reload/activity or a menu. Aim generation yields to this explicit intention.
Native validation is repeated when actually sent; it is not an optimistic hit.
Pause/menu/recovery, context click, changed weapon/target and timeout discard it.
This bounded completion replaces the previous lost-click behavior during AIM;
it does not make held LMB an automatic trigger.

Menus, manual/threat pause, loss of focus, activities and reconnect disarm held
inputs. Release and press again to resume; no hidden fire/aim is queued for
unpause. Read-only ground consultation remains accessible under manual pause;
its existing native guards still prohibit free pickup/open/close. R disarms the hold while native reload/choices execute. Hint text names
RMB/F and marks the held aim intent; recoil remains the native number.
`aim_held` in the diagnostic trace is local input intent, not simulated state.

## Verification and follow-up

Tests must exercise actual renderer input and native command outcomes/costs,
not just the gesture classifier. Include shoot while holding RMB, resume after
shot, release, menu/pause/reconnect, neutral/empty reticle and reload; regress
Shift+RMB window closure and pickup. Canonical save readback is scoped evidence,
not full SAVE-001. The usual manual backlog retains prior untested features.

Separate later work: free reticle, neutral targeting confirmation, bows,
mounted/vehicle weapons, ballistic feedback, real wielded models/animations,
audio, richer dialogs. External containers remain the next essential inventory
extension; this input slice does not require pending DND/language manual PASS.
