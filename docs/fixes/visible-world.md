# Invisible world: startup and projection repair

The reported trigger was running `start.sh` and entering a world, with all
blocks invisible. The invoked CDDA binary predates the audit bootstrap fixes
and was reproduced exiting with SIGSEGV (-11) in an isolated user directory.
The script opened Luanti anyway. The clean corrected server built during the
audit had remained in the audit workspace rather than the invoked path.

Even with a running server, camera/entities added absolute origin and a Z
offset while terrain used local XY / absolute levels. Delayed Luanti singlenode
block packets also replaced projected terrain with air. Node/media receipt
alone did not guarantee that texture initialization and mesh startup completed.

## Changes

- Refresh the actual `cdda/build/src/cdda-server` and `luanti/bin/luanti`
  executables. The CDDA binary exactly matches the clean audit build. New
  Luanti is rebuilt from the patched source with native unit tests enabled.
- Wait for the private socket and post-initialization readiness message before
  opening the client. Startup failure stops launch and preserves its exit code.
  Resource paths work from any current directory; both owned processes are
  stopped on exit. Logs go under `artifacts/runtime/`.
- Open `cdda_voxel` directly using a dedicated disposable presentation world
  in `worlds/cdda-presentation`. CDDA data defaults to `user/cdda`. Existing
  `~/.minetest/worlds` and legacy `/tmp/cdda_cwm_bench_user` are not modified.
  `CDDA_USERDIR`, `CDDA_WORLD`, `LUANTI_WORLD`, `LUANTI_CONFIG`, binary paths and
  `LOG_DIR` remain configurable through environment variables.
- Connect after `LC_Ready` and only when CDDA node definitions exist. A
  configured `cwm_socket_path` replaces the launcher's shared test socket.
- Use local XY and absolute CDDA levels for all projection positions. Origin
  changes reset interpolation into the new local bubble. Authoritative CWM
  coordinates and CDDA gameplay are not modified.
- Keep projected block nodes in a bridge-owned cache, reapply them after native
  block deserialization, invalidate the block's cached air flag and then use
  the native mesh queue/ack path. Full terrain replaces stale projected areas.
- Reject snapshots without origin and skip missing entity/vehicle positions.
  Clear bridge-owned connection, GUI and scene state on shutdown.
- Disable Luanti's movement anticheat for this presentation game: CDDA owns
  player positioning. The launcher's local server binds loopback.

## Verification

Evidence is under `artifacts/visibility-fix/`; the committed
[evidence index](visible-world-evidence.json) records source/binary identities,
commands, outcomes and artifact hashes. The frozen audit workspace was
restored, including the byte-identical original Luanti executable.

The actual CDDA/Luanti launch is tested with isolated worlds and captured
screenshots. A deliberately failing backend verifies that Luanti is not
opened and exit 23 is preserved. The real rendering regression transmits
one-room and two-level scenes with origin `(84000, -42000, -1)`, exercises
delayed native air-block updates, and checks textured geometry before and
after movement. It does not certify dense entity meshes or benchmark latency.
Native Luanti tests pass 302/302 against the installed new executable.
The real launch/failure checks pass 6/6; the distant-origin visibility checks
pass 10/10. Small and two-level scenes both retain visible textured terrain
after native cache updates, and missing-origin input no longer crashes the
client. [Actual CDDA scene](../../artifacts/visibility-fix/startup-final/actual-scene.png)
and [small-room capture](../../artifacts/visibility-fix/render-distant/BM01/scene.png)
provide the visual evidence.

The first native smoke harness read an action-only engine logfile for INFO
messages, and therefore reported false negatives while its console and
screenshots already showed visible terrain. That artifact is retained;
the final harness explicitly records INFO logs. The initial client link error
(ODR use of `MapBlock::nodecount`) is also retained; the rebuilt value argument
fixes it. Remaining gap-recovery failures are preserved in the rendering
results, rather than treated as part of visibility acceptance.

```sh
./start.sh

python3 tests/visible_world_test.py --workspace . --artifacts artifacts/visibility-repeat/render --probe-library artifacts/m5.5/20261003-takeover/evidence/conformance/frameprobe.so
python3 tests/startup_visibility_test.py --workspace . --artifacts artifacts/visibility-repeat/startup
```

The graphical tests require X11, xdotool, ImageMagick and Python FlatBuffers.
The probe library can be built from `tests/takeover_frame_probe.c` using
`cc -shared -fPIC tests/takeover_frame_probe.c -ldl -o /tmp/frameprobe.so`.

This is a scoped visibility repair. Canonical existing-character loading,
complete scheduling/action validation, protocol deduplication/resync, entity
meshes and full threading/performance acceptance still require the M5.5
remediation plan. The gate remains FAILED.
