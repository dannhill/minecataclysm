# Native NPC conversations — 2026-10-22

The later [CWM2.29 native trading delivery](native-trade.md) supersedes this
report's trade boundary and installed runtime. The checks below describe the
conversation delivery's exact historical source.

Normal Linux **`./start.sh` now supports talking to NPCs**: point at a
perceived, non-hostile character and **right-click**. The same control works
with a weapon held. Walking into a friendly NPC does not start a conversation.
`./conversation-demo.sh --fresh` opens an isolated scene with an NPC ahead.

The interface shows the current native line, scrollable transcript, complete
responses, native social trial percentages and consequence colors. Numbered
buttons/keys select a response; long lists have presentation-only pagination.
Native observation, evaluation, personality, opinion and yell actions are also
available. CDDA retains topic conditions, entry effects, mission/training
selection, trial rolls and consequences. The native clock is paused while
choosing, and finishing pays the ordinary `game::chat` 100-move cost.

Esc chooses an additional **Leave conversation** action, rather than assuming
that a native goodbye or sole reply is harmless. Connection loss/replacement
settles an unanswered choice through that safe exit. A valid answer received
before disconnection remains accepted once. Reconnection never restarts talk
automatically. Meeting the NPC and entry effects already applied remain native
state; leaving is not a rollback. [Detailed contract](../design/native-conversation.md).

CWM **2.28** appends typed TalkRequest and optional conversation metadata on
DecisionPrompt. The server revalidates canonical identity, native perception,
same Z and chat range at admission and execution. The existing command ledger
and decision/connection identities prevent replay. Pagination uses the existing
generated options, without running topic effects or social rolls again.

The pinned native source contained duplicate `get_topics` calls, including
mission talk callbacks. This duplication is removed; stack backtracking checks
for an empty stack and the history highlight count starts initialized.

## Scoped verification

- **163 native cases / 73,220 assertions PASS**, including CWM, reading,
  disassembly, selected melee/ranged and upstream NPC talk coverage. Four
  focused conversation cases pass **56 assertions**: native history, social
  trial/effect/opinion application, entry count, safe exit, service menu values,
  trade cancellation, target revalidation, command deduplication and connection
  replacement before/after an accepted response.
- **309 client tests / 47 modules PASS**, plus 648 Catch assertions in four
  cases. The standalone decision view/input contract passes as well.
  Protocol **14/14**, language **9/9**, extensible registry **3/3 PASS**.
- **44 renderer/canonical checks PASS**: 22 against the reconstructed runtime
  pair and 22 repeated against the actual installed `start.sh` pair. These use
  the real renderer, mouse targeting, mouse scrolling to an offscreen response,
  keyboard choices, pause, trade boundary, disconnect/recovery and active quit.

An unmodified pinned-CDDA core independently creates and reloads the fixtures.
Readback confirms the same canonical NPC ID, native known-to-player state and
settled talk attitude, unchanged player position and no fake conversation
activity or Luanti persistence. Screenshots were inspected by the agent;
this is distinct from the developer's personal acceptance.

[Exact sources, commands, hashes, logs and limitations](native-conversation-evidence.json).
Builds are incremental captured reconstructions, not cold builds. Source and
mode inventories are checked; SDK changes rebuilt native dependencies. Later
repairs rebuilt the affected native/client objects and test units.

Investigation logs remain separate from final PASS: initial fixture access to
a private field, a strict compiler warning and two native test setup assumptions
were corrected. An initially passing GUI script missed an invalid scrollbar;
screenshot inspection found it, and final coverage includes actual mouse
scroll/selection and real formspec parser validation.

## Installation and remaining work

The verified Linux pair is installed in normal `./start.sh`. Paired rollback
copies are `artifacts/native-conversation-20261022/native-before-conversation`
and `client-before-conversation` (previous CWM2.27). Developer saves and
preferences were not used for verification. Item mapping batch60 is unchanged.

**Dedicated NPC trading remains the next core slice.** Current trade choices
show an explicit notice and cancel before restocking, item migration or an
exchange. Static service menus and informational popups have external adapters;
text entry, callback menus and inventory selectors without a dedicated view
cancel. This does not certify every mission/EOC, camp, surgery, map selector,
training activity or companion interface. The transcript wire view retains
newest complete messages within 256 KiB, with an explicit omission notice.

**41 PENDING, no open manual FAIL**: four NPC-01 checks added to the previous
37 unchanged in [the shared human testing ledger](../validation/pending-manual.md).
No new human PASS is inferred from automation. Historical **M5.5 FAILED** and
full **SAVE-001 OPEN** remain unchanged. The existing Windows installer remains
the earlier **CWM2.26 snapshot**; this delivery updates Linux only.
