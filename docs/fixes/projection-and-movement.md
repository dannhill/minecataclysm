# Structural projection and movement repair

Scope: the user's reports of inconsistent walls/windows, invisible building
obstacles, camera flicker and irregular held-key movement. CDDA world generation
and canonical movement rules remain the source of the world and action results.

The old exporter classified unfamiliar impassable terrain as dirt, ignored most
furniture, replaced floors with selected furniture and classified open windows
as glass. Substring `air` also matched stairs. All opening orientations were zero.
Movement actions could open doors without exporting the changed tile. These
errors made visual obstacles disagree with CDDA's actual terrain/furniture.

The exporter now reads the loaded terrain flags, movement costs and door links.
Every impassable terrain gets visible structural geometry; passable damaged
walls get a low obstacle, open windows get an aperture and boarded windows get
wood. Furniture overlays its floor and records whether it blocks movement.
Out-of-bubble cells are explicitly air. The native catalog tests compare these
properties to the actual loaded CDDA registry and canonical movement routines.

The server compares semantic tiles at the end of an action, after actor/field
processing. Changed tiles are batched in the appended `WorldSnapshot.tiles`
field and applied before player targets. An unchanged action does not resend
243 terrain chunks; a rebase still requires full terrain. Snapshot and standalone
tile export share one classifier. Window headroom reaches eye height and the
two door halves occupy independent cells, with a consistently oriented image.

Native Luanti physics and native teleport packets no longer change a CWM-owned
player, including during reconnect. Mouse look remains active. Native node
prediction/add/remove cannot change the authoritative projection. A shared
lock protects projection writes, native air-block deserialization/restoration
and the mesh worker's capture of node data; workers mesh private copies after
releasing it. This closes the identified projection/capture race, not every
possible threading issue in the complete upstream engines.

Mesh results also use one FIFO completion queue. The old separate normal/urgent
result queues could deliver a newer urgent projection followed by an older
normal mesh for the same block, erasing visible geometry despite correct node
data. The work queue still prioritizes urgent jobs and permits only one job per
position in flight; each worker publishes before marking that position done.
The focused native `testMeshResultOrder` protects the actual completion API.

Input uses `steady_clock`, a 200 ms repeat interval and at most one outstanding
move. Its matching ACK alone does not unlock another command: the authoritative
result snapshot must arrive too. A slow response cannot build a held-key backlog
or a catch-up burst. Player presentation interpolates linearly over a step,
instead of frame-dependent exponential easing. It never predicts a CDDA move.
Slow simulation, blocked moves and door-opening actions can still cause a
legitimate pause; the client does not invent movement to hide one.

## Verification

Commands, exact source/binary identities and artifact hashes are recorded in
[`projection-and-movement-evidence.json`](projection-and-movement-evidence.json).
Artifacts are isolated beneath
`artifacts/projection-movement/`. Existing user saves are not used by these tests.

```sh
cmake --build luanti/build --target luanti --parallel 2
luanti/bin/luanti --run-unittests
cmake --build protocol/build --parallel 2
ctest --test-dir protocol/build --output-on-failure
# Native CDDA build with BUILD_TESTING=ON; run from its source directory:
build/tests/cata_test '[cwm]' --rng-seed 42 --user-dir=/tmp/cwm-native-test
python3 tests/presentation_regression.py --workspace . --artifacts /tmp/cwm-render-test
python3 tests/startup_visibility_test.py --workspace . --artifacts /tmp/cwm-launch-test --movement
```

The graphical fixture exercises actual WASD capture/camera, rejected commands,
a 650 ms delayed authoritative result, release, both window views and an open
window. It measures camera coordinates and request timestamps, independent of
the legacy HUD's fixed FPS field. FPS settings are limits, not evidence that
120 FPS was achieved. CDDA catalog/action tests and the real isolated launch
provide separate evidence for the production exporter/runtime.

Final results: native CDDA 3/3 cases, 3,339 assertions; Luanti 303/303 native
tests including mesh result ordering; protocol Debug 2/2; real renderer/input
48/48 checks across four scenarios; actual launcher/world 8/8 checks. The
camera has zero stationary/settled position variation in these fixtures.
Measured moving speed has a median of approximately five tiles/second at
actual frame rates near 30 and 60 FPS; the 120 FPS limit achieved about 60 FPS.
A delayed result introduces one pause and no queued burst. Both window faces
are captured, and a one-tile batched update removes glass without full terrain.
The frozen audit workspace, including its binaries, was restored; a fresh
final reconstruction verifies every fork source against the committed inventory.

Geometry is still approximate: trees/fences/rocks use a solid placeholder,
furniture uses wooden boxes and climbable/damaged walls use low obstacles.
Detailed stairs, roof shapes, vehicle/entity meshes, canonical inherited-avatar
loading, the complete turn scheduler and protocol resynchronization remain in
the failed M5.5 remediation scope. This repair does not certify the whole gate.
