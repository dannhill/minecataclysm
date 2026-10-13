# UX-04B — Structured native medical selection

The item-first route is explicit: I → real treatment item → Treat → native body
part → confirmation → paid ACT_FIRSTAID. CDDA owns selectable parts, treatment
powers, probabilities, biology, consumption, interruption and healing over time.
No automatic treatment selection or local healing is introduced.

Character::body_window supplies scoped semantic metadata alongside its existing
external choice. The metadata captures the native menu's exact allowed choices,
body IDs/names, descriptions of known wounds and treatment effects, and observable
health resolution. Disabled parts remain readable but cannot generate responses.
Native precision alone permits exact HP. PAIN_IMMUNE and broken/mending limbs use
qualitative state; the client never reconstructs HP from ASCII or translated text.

CWM 2.21 appends MedicalOption to DecisionPrompt. The native coordinator maps
metadata to each page's indices; navigation, safe cancellation and the original
selection mapping remain native. Generic confirmations retain the UX-04A panel.
The client draws anatomical armour proxies, ten hearts at the native resolution,
scrollable descriptions and explicit choices; existing decision/connection and
physical-key release guards remain. Unknown body IDs use neutral presentation.

The companion manual feedback fixes preserve the last acknowledged inventory
view while a zero-time layout query runs, increase destination hit areas to six
rows per page, use explicit language buttons, and export synchronous equipment
work progress from the existing coordinator clock. A native actor's move progress
still takes precedence. No activity, time, pocket, healing rule or save field is
invented for these UI changes.

Language changes still require a coordinated restart; live translation of both
processes and cached native text is deferred. Releasing RMB already ends the aim
gesture and new AIM requests; retaining earned recoil is a separate native rule.
Movement retains native accuracy costs. First-person aim pose/zoom, the body-first
H → filtered item route and richer anatomical artwork remain separate follow-ups.
Full SAVE-001 stays OPEN; the historical M5.5 audit is FAILED.
