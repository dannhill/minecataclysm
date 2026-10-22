# Native NPC conversation boundary

Right-click a perceived, non-hostile NPC to start a conversation. Friendly
movement contact remains movement contact; it does not silently choose a
conversation. Targeting is a presentation ray, but admission and execution
both resolve the canonical NPC ID, same Z, native visibility and the native
`game::chat` range of two submaps. Native speech restrictions still apply.
Hostile actors retain the existing combat controls.

The owner thread calls `avatar::talk_to`. Native `dialogue::opt` generates the
challenge, response text, trial chances, consequences and topic entry effects
once. The external branch replaces terminal input, retaining native response
resolution, mission selection, training selection, trial rolls, opinion and
effect application. It also exposes the native Look at, Size up stats, Assess
personality, Check opinion and Yell topic actions. Conversation completion pays
the same 100 native moves as `game::chat`; there is no client-side timer or
social simulation. Conversation state is not serialized by Luanti.

The pinned native `avatar::talk_to` had two consecutive calls to `get_topics`,
which invokes mission talk callbacks. The duplicate is removed. Native stack
backtracking now tests for an empty stack before reading its last topic, and
the dialogue history highlight count is initialized before its first increment.

CWM 2.28 appends TalkRequest (target entity ID, command ID) and optional native
conversation metadata to DecisionPrompt. Existing session identity, sequence,
command ledger, decision ID and connection checks remain in force. Pagination
maps to the same already-generated responses; it does not ask CDDA to evaluate
the topic again. Protocol validation bounds speaker/topic/history, rejects
conflicting medical metadata and requires an explicit safe final exit.

While a decision is open, the native simulation clock is paused. Response
buttons and number keys select exactly one native answer. Esc and connection
loss select an additional **Leave conversation** action with no reply effects;
they never infer that the last or sole native reply is harmless. Native entry
effects and the fact that the player has met the NPC can already have occurred.
They are canonical, not rolled back by closing the presentation. Leaving still
pays the normal chat action cost. Recovery does not reopen or reissue a talk
command. A new conversation after recovery re-evaluates native conditions.

The graphical view includes a scrollable native transcript and complete
scrollable reply text, including native trial/consequence formatting. A wire
view retains the newest complete transcript messages within 256 KiB and
explicitly signals when older text is omitted. It is not a persistent journal.
Native strings use CDDA translation; integration labels use the extensible
product language registry. New text may still fall back to English in Italian
WIP. Open native choices are not replayed to change language.

## Services and follow-ups

This slice connects native conversations, not every NPC-related subsystem.
Static native service menus use the existing external-choice provider with
enabled entries and exact native return values. Informational popups use
external choices. Callback-dependent menus, text entry and native inventory
selectors explicitly cancel where their dedicated presentation is missing.
The original CWM2.28 delivery cancelled trading before restocking or transfer.
CWM2.29 supersedes that boundary with the dedicated [native trade interface](native-trade.md),
using native quotes, prices, ownership, credit, capacity and confirmation.

Mission dialogue effects continue in CDDA, but this delivery does not certify
all mission scripts, map selectors, surgery, camp management or training
activities. [Individual companion orders/rules](native-companions.md) now add a
dedicated local-ally panel; complex service interfaces remain separate roadmap
work. Opening a conversation is not evidence that an
arbitrary EOC-driven NPC service is fully usable in 3D.

`./conversation-demo.sh --fresh` uses an isolated pristine-core fixture with
one NPC directly ahead, native neutral topics and an ordinary canonical save.
It does not add or reposition NPCs in the developer's world. Relaunch without
`--fresh` to reuse that demo. NPC-01 in the shared manual ledger records human
acceptance separately from automated tests. Historical M5.5 FAILED and full
SAVE-001 OPEN remain unchanged.
