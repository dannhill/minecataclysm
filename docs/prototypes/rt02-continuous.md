# RT-02 — native continuous movement prototype

Status: implementation under verification; manual comparison pending.
User authorization: “Procedi”, after selection of global 4x on RT-01.

CDDA integrates normalized direction on its authoritative timeline, retains
subtile XY in canonical Creature values and debits native movement/stamina
proportionally. Native crossings still execute terrain, trap, water, sound and
safety effects; only their already-paid walk/swim debit is suppressed. Doors,
attacks, restraints and vertical actions retain their separate native costs.
Luanti sends direction and interpolates confirmed small updates; it never
supplies a position or commits gameplay physics.

`./continuous-demo.sh --fresh` creates a separate persistent copy of the native
RT-01 fixture. Default rate: global 4x, F7 pause and F8 speed. WASD follows exact
camera yaw, stops inside a cell and normalizes diagonals. `realtime-demo.sh`
remains the grid comparison (select 4x with F8).

The fixture contains stairs ahead and a ladder immediately right of spawn.
Space/Shift+Space still use one native vertical connection per press. Automatic
stair/ladder traversal is unresolved; compare the existing transition before
choosing its replacement. Mounted/grabbed/vehicle movement is outside this
prototype. Restrained/stunned movement keeps native discrete status attempts.
Perception, AI and combat retain tile anchors; continuous combat and vehicles
are later work. This slice does not certify the historical M5.5 gate.

Verification evidence will be recorded here after reconstructed-source tests
and actual 3D-client checks complete. No existing user world is used.
