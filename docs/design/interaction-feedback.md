# INT-01 — Interaction feedback, 2026-10-18

RMB toggles the last authoritative door/window state, including the sill of an
open window; Shift is now posture only. One classified press, one context action;
held context cannot become aim. CDDA revalidates the explicit OPEN or CLOSE,
range/state and native cost. A native fractional-body guard refuses closure
through the avatar's circle before admission and again before execution.
Luanti physics is already disabled for CWM-owned avatars and open door nodeboxes
are nonwalkable. This fixes a demonstrated close-through-body path; the reported
jam while opening a particular world structure still needs the user's recheck.
Do not claim a reproduced mesh collision or teleport the avatar away.

Shift-click in external storage sends PICKUP or DEPOSIT to the opposite panel.
In owned-container transfers the explicit selected destination is used; missing
destination shows a reason. Existing selected quantity applies; unselected stacks
move all. Ordinary inventory short clicks keep selection. Press/release and view
identity prevent a regenerated menu from completing a stale gesture.

Dragging a real item outside the formspec bounds requests DROP at the avatar's
native tile. Background inside still cancels; Esc during drag cancels, including
release outside afterward. This includes actual quickbar references (drop the
item), hand, owned containers and external contents. Worn items, liquids/open
buckets, seals, cycles, ownership and capacity retain native restrictions. Recipe
icons and other hypothetical results are not real physical-item drag sources.
No automatic undress, stealing, pouring, free move or optimistic inventory edit.
CWM2.23 extends existing DROP source eligibility rather than inventing a client
inventory. Native ACT_DROP handles both own and external items; the existing
external partial-charge bug in obtain_activity_items is corrected to keep the
remainder in place and drop exactly the requested portion.

Paused loose pickup formerly remained queued until RESUME, unlike the guarded
storage transfer path. Reject at selection and cancel unsent pickup on manual
pause or a new non-menu pause. Consultation stays possible. Physical actions
never wait behind pause; a new gesture after resume is required.

Aim semantics remain pending discussion: ranged.cpp QUIT aborts the targeting
UI while action_drop_aim explicitly resets recoil to MAX_RECOIL. The integrated
held gesture stops sending AIM at release, retaining already-paid precision
under its idle policy. Releasing RMB does not implicitly invoke drop-aim.
An ADS/weapon-lowering presentation can later follow release independently;
changing precision retention is a gameplay decision, not a visual toggle.
Native movement continues to apply its accuracy cost. No new aim rule here.
