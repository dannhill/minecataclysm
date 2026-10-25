# Presentation and recovery follow-up — 2026-10-25

Scope follows the sole developer's human [feedback](../source/manual-rest-recovery-feedback-2026-10-25.md)
and the earlier pointer report. CDDA remains gameplay/time/save authority.

## Rest pacing and its presentation

Global F8 speed remains 0.25–4. Long rest adds a native coordinator preference:
normal (multiplier 1), x64, x256 (default), or x1024. The rest menu B offers
explicit selections. After the existing eight native-second warmup, the target
rate is **F8 global speed × rest multiplier**; for example 4 × 256 = 1024 game
seconds per real second as a target. Actual throughput is limited by executing
the native simulation, not guaranteed by the selected number. Sleep length,
needs, disturbances, alarms and waking remain native; calendar time is never
assigned forward and AI/effects/turn phases are not skipped.

The old coordinator discarded accrued clock credit after each lagged tick,
which unnecessarily limited deliberate acceleration. Fast rest now retains at
most 32 ticks of credit. Each credit requires an actual native world tick.
Normal play keeps its previous stall policy; pause/wake remove unused rest
credit. Move/work debt remains payable. Short waits stay unaccelerated.
The HUD distinguishes NORMAL REST, warmup and FAST REST, shows the F8/factor/
target calculation and the load limitation. Pausing still freezes all work.
CWM2.35 appends RestState.speed_multiplier; valid values are 1/64/256/1024.
An accelerated state cannot claim multiplier 1. Preferences remain transient,
separate from canonical effects/activities; recovery never starts sleep again.

## Open ground-container recovery

After opening a stashed soda can, native contents_change_handler can set it on
the floor when the player cancels further liquid handling. It stays open and
cannot be put back in a backpack full of liquid without native spill handling.
The new route is right-click ground container → select it → Pour liquid... →
a compatible carried container. Once empty the can uses ordinary pickup.
`./liquid-recovery-demo.sh --fresh` provides the sealed can and an empty glass
bottle. Pour is also available on selected owned liquids in that external view.

The existing POUR command retains zero quantity/destination and shared command
identity. External view/range/Z/perception/ownership/type/ancestor/charges/seal
bindings are checked before native handling. The selector still chooses only
compatible accessible carried destinations. Original handle_liquid_from_container
owns compatibility, transfer, 100-move debit where applicable, partial remainder,
contents changes and child removal when drained. Native collection of the empty
can has its own activity/cost. No generic INSERT bypass for full open containers,
no vehicle tanks or unrestricted external looting is introduced.

## Pointer and confirmation rendering

CWM forms retain a normalized presentation-only pointer position on menu events
and submissions. A recreated CWM menu disables relative look and restores that
position. Ordinary look input is still recentered while controlling the world;
restoring a position sends no click, answer, drag or native command. Form IDs,
views/generations, input fencing and cached decisions remain authoritative.

Confirmation choice labels remove terminal full stops and trailing whitespace;
questions, ellipses, internal decimals and UTF-8 remain. Confirmation body text
can remove a terminal stop while preserving native colour markup. Dialogue
narrative/history is not rewritten. The wire labels and numeric choice IDs are
unchanged, including native Yes./No. strings. This is rendering, not a semantic
answer parser.

## Future visual replacement

Inventory/transfer/crafting/trade/journal already use explicit read-only view
models and command handlers. DecisionModel now contains the native question,
choices and identity/input validation independently from DecisionDialog's
formspec renderer. PresentationTheme/presentationPanel provide shared panel,
text and button styling to those modals. Future artwork/layout can replace the
renderer/theme without changing native commands, CWM IDs or time costs. This is
a scoped separation, not a completed visual redesign of every HUD/body panel.

## Native sky clock

Luanti previously started its visual world at noon. The bridge now projects
native simulation_time_seconds modulo 86400 into visual time-of-day, with
local time speed zero. The renderer applies that clock every frame, including
pauses; legacy Luanti TimeOfDay packets are ignored while the native bridge owns
the player, preventing transient day-sky resets and spurious day-count changes.
Native per-tile light and perception are unchanged. The visual sky uses Luanti's
sun/moon/colour model; seasonal astronomy and weather matching remain separate.
`./night-demo.sh --fresh` gives a canonical midnight scene with an opening above
the player for direct sky inspection. Menu/pause state is not saved as gameplay.

Automated native/SDK/client/renderer and independent canonical readback evidence
is required before installation. Four personal FB-01 checks remain separate;
the four human PASS results preceding these changes are retained. Windows
remains the earlier CWM2.26 snapshot, mapping batch60 is unchanged, and scoped
repairs do not promote historical M5.5 FAILED / full SAVE-001 OPEN.
