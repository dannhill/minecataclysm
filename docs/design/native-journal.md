# Known native mission journal

J opens the paused journal in normal Linux start.sh. Active, completed and
failed tabs project only the avatar's native history lists. Reading/selecting
a row does not assign, complete, fail, process or reward a mission. A separate
Track this mission button invokes `avatar::set_active_mission` after current
view, membership, assignment, in-progress status and expected tracked-mission
validation. This is native UI metadata with no action, move cost or game tick.
The existing bounded command ledger prevents old retries from changing a later
selection. Completed/failed/unaccepted/other-player missions cannot be tracked.

Native names, descriptions, goal categories, known quest giver, deadlines and
explicit mission target are shown. The target is exactly the coordinate already
shown by CDDA's mission journal, in global overmap cells, including Z. No giver
position fallback, terrain lookup/generation, hidden world mission registry,
creature telemetry, fog reveal or automatic routing is used. This slice adds
no minimap/HUD waypoint; that remains an optional presentation follow-up.

Remaining time copies native watch/no-watch formatting. Completed entries omit
remaining time as in the native screen. Goals are descriptive categories and
native history states, not a simulated completion percentage. A condition can
run arbitrary native logic: journal queries never call `is_complete`, mission
processing, dialogue effects or the general tag/snippet parser. Static player/
giver name tokens are safe substitutions; unsupported dynamic tokens (including
potentially random reward expressions) get an explicit unavailable detail
marker. Long text has an explicit limited flag and UTF-8-safe bounds. Native
mission acceptance, objectives, rewards and failure behavior remain untouched.

CWM2.30 appends MissionQueryRequest, MissionView and MissionTrackRequest. A query
ID correlates read-only views; a session view ID and canonical native mission ID
(including valid zero) identify selection. Track carries expected tracked ID,
with -1 as absence. No Luanti types enter the protocol. At most 2048 entries are
exported with explicit truncation. Native modal decisions/trades block the
journal. Other queries do not create views of unaccepted missions.

J menus pause existing work; Escape/Inventory-close resumes the previous clock
mode. An explicit F7 pause remains set. The client fences callbacks by view and
connection; disconnect/reset dismisses the journal without replay. Recovery
requires full authoritative state and explicit reopening. Only native history
and active selection are persisted in ordinary CDDA saves, not form/tab/menu
pause state. A reload may resume ordinary native activity as elsewhere.

J takes precedence over the engine's unrelated J fast-move shortcut while CDDA
owns the player. `keymap_cdda_journal` is configurable; other product controls
are unchanged. English is default, Italian is WIP. New labels use shared
catalog helpers; native mission translations remain native, with no bilingual
protocol enum or new language branch.

`./journal-demo.sh --fresh` uses an independent pinned-core fixture: two active
missions, one completed, one failed, one unaccepted NPC proposal, no watch.
It uses native saved-mission deserialization and native history/assignment APIs
to prepare controlled histories; it is not a claim that those quest lines were
played to completion. The developer's worlds are never used. Reuse without
--fresh to test canonical persistence. See JOURNAL-01 in the manual ledger.

Follow-ups: full mission/mod/EOC lifecycle acceptance, safe recorded dynamic
reward text, optional known-target HUD navigation, and companion/service UIs.
Historical M5.5 FAILED and full SAVE-001 OPEN remain unchanged.
