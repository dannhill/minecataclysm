# Windows 11 distribution

Requested: one executable a nontechnical player double-clicks to start the same
integrated game as start.sh, without Bash/Python/WSL or development tools.
The installed runtime remains CDDA authority plus Luanti presentation, CWM 2.26.

Deliver a per-user, non-admin Windows x64 installer that bundles both executables,
DLL closure, CDDA data/catalogs, presentation game, engine assets/catalogs and
licenses. It creates a desktop/start-menu shortcut and launches the game after
installation. Program files and durable saves remain separate. Uninstall removes
the program, retaining the user's saves. The portable package uses the same layout.

The native Unicode GUI supervisor starts CDDA hidden, waits for an explicit
post-initialization readiness event, then launches the actual 3D client. It owns
both child processes in a job, requests native save/shutdown through an event
when presentation exits, and surfaces actionable startup/runtime/save errors
with a log folder. Defaults match the accepted continuous 4x product mode.
Durable state lives in LocalAppData/Minecataclysm; CLI --userdir isolates tests.
A per-user mutex prevents simultaneous use of the same canonical save directory.
No developer save or pre-generated private world is distributed.

Windows uses a bounded overlapped local named-pipe backend behind CwmTransport.
Framing, command IDs, revision/gap handling, budgets and resynchronization retain
the existing contract. Endpoints are random per session, reject remote clients
and restrict ACLs to the account/SYSTEM. Existing POSIX backend remains on Linux.
No Windows or Luanti structures enter the CWM wire model.

Cross-build from captured reconstructed forks using the pinned Luanti upstream's
LLVM-MinGW toolchain/dependency hashes. CDDA uses its existing internal Windows curses implementation; the CWM 24.3.25
FlatBuffers header SDK is explicitly configurable. Build/package tools and
source receipts preserve exact dependencies, hashes and reproducible commands.
Include licenses and a source identity/reproduction pointer with distributions.

Verification distinguishes cross-compilation, dependency closure, Wine execution
and native Windows 11 acceptance. Test private prefix/saves, initial world/start,
actual renderer IPC, quit/reload canonical persistence, language and Unicode/space
paths, bounded transport/reconnect and supervisor failure handling. Wine success
must not be represented as an actual Windows 11 hardware/driver playtest. Any
remaining personal Windows checks go into the manual backlog; existing PASS
entries and historical M5.5/SAVE-001 statuses remain scoped.
