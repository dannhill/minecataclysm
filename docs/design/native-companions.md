# Individual native companion orders and rules

A perceived local ally offers **Companion orders and rules** from its normal
native friend/guard conversation root. The entry is absent on strangers,
hostiles, radio conversations and native blocked speech/sleep topics. The
server revalidates alliance, life, same Z, native sensory range/visibility,
hearing and speech before every panel action. No new omniscient NPC browser
or remote command channel is introduced.

The panel provides local Guard this position / Follow me and all 18 native
boolean follower rules, native engagement and aiming policies, native CBM
reserve/recharge preferences and temporary per-rule overrides. Guard/follow
use talk_function::assign_guard/stop_guard. Camp/expedition assignments cannot
be changed through this shortcut. The panel does not recruit strangers, grant
knowledge of hidden skills, heal, generate items or supply power.

Base settings use native talker setters (including range cache invalidation
and native weapon reselection/costs). Override operations use native follower
rule APIs. Base, effective and temporary values are distinct: changing a base
rule never silently removes an overriding order. Clearing one override or
clearing all overrides is explicit. AI, execution of orders and persistence
remain entirely CDDA, including native limits and possible AI failures.

The panel is a native conversation subflow with existing decision IDs,
connection fencing and safe last-choice exit. CWM2.31 appends only a semantic
companion_controls flag to ConversationInfo; no new rule mutation request,
client AI model, saved UI or transport/engine type is added. The flag selects
a compact control layout with native labels and a scrollable description.
Pagination is over already-created choices. Reading/paging does not re-run
native topic speaker effects, roll trials or mutate rules.

Normal chat admission and its native 100-avatar-move exit cost remain shared.
Rule/order effects occur on an explicit decision; reading does not advance
simulation time. Native NPC-side costs, including weapon reselection, are
preserved rather than called free. Esc/disconnect safely leaves the whole
conversation; accepted changes are not rolled back or replayed. An explicit
Back returns to the current native friend/guard root. Only actual native NPC
rules, attitude and assignments are saved, not panel/tab/menu pause state.

The native conversation still exposes ordinary offers, recruitment trials,
training and special services. This slice does not certify their whole
lifecycle or add training progress, pickup-filter text entry, copied rules,
camp/spedition UI, radio orders or mass shouting. Those remain separate work.
Historical M5.5 FAILED and full SAVE-001 OPEN remain unchanged.
