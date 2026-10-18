# Native paper books and study

I now offers **Skim book / Read** for owned ordinary paper books, including
accessible nested books. The same feature is installed in ordinary `start.sh`;
`./reading-demo.sh --fresh` creates an isolated demonstration session.
[Design](../design/native-reading.md), [exact evidence](native-reading-evidence.json).

The native item location pays its obtain/access cost, then `avatar::read` owns
reader selection, vision/literacy/morale conditions, helpers, time, chapter
marking, enjoyment and theoretical skill experience. Unknown books are identified
only after the native skim completes. Inspecting details gives no identification,
experience, clock advance or RNG consumption. Known skill books keep the actual
Read once / Read until a level / Cancel choices. The scoped external-menu adapter
preserves native return values and participant information; other menus are
unchanged.

I pauses the real ACT_READ actor. Close resumes it; Interrupt reading invokes
native cancellation/backlog rules, without assigning a completed chapter or
refunding paid time. Re-reading an eligible same book/mode resumes native work.
Read-only metadata includes the reader-adjusted skim/chapter duration and known
skill progression. The demo magazine takes 39,900 native moves for its generated
character, rather than a fixed 42,000; the integration does not change that rate.
No dedicated study fast-forward was added.

The work panel and contextual hint distinguish reading/skimming from eating.
Progress is exported native moves, including after load/reconnect without a new
initiating command. Paused, stale and retransmitted input cannot create another
chapter. Canonical native ACT_READ, targets, knowledge and experience survive
quit/load. An open I menu and its pause remain transient, matching the accepted
current crafting/load behavior; loading resumes the saved work.

CWM **2.25** appends READ=6, BookInfo, ReadingState and CancelReadingRequest.
Inventory reason vectors contain seven entries. Validation covers malformed
metadata, text bounds, native-player presence and conflicting activity states.
Both executables require the same exact protocol version. No engine-specific
wire structures or new canonical reading-save fields were introduced.
Special-use books, guidebook hints and e-readers remain explicitly unsupported
by this first slice, pending their own interfaces.

## Scoped verification

- Native: **113 cases / 65,724 assertions PASS**, including the existing native
  reading tests and the integration/activity/combat regression filter. The focused
  integration subset is **4 cases / 114 assertions**.
- Luanti: **309 tests / 47 modules**, plus **648 Catch assertions / 4 cases PASS**.
- Protocol **13/13**, language **9/9**, reconstructed launcher aliases **6/6 PASS**.
- **84 actual renderer/canonical checks PASS**: 27 skim/study/pause/interrupt/
  reconnect/active-save, 13 reload/completed-chapter/experience, 31 inventory and
  faithful clothing-debit regressions, 13 final installed-start.sh reload checks.

The pristine pinned-CDDA reader creates the fixture and independently loads the
produced saves. It verifies exact book preservation, native identification,
ACT_READ and partial counters before completion, and actual theoretical
experience after the loaded chapter completes without reissuing Read. The
fixture and outputs are isolated copies, never the developer's worlds. These
checks are scoped evidence, not full SAVE-001 certification.

Sources are captured in the baseline and built incrementally in owned
reconstructions with caches retained; these are not cold builds. The final
context-label fix changes client presentation only; final client unit tests and
the installed renderer were rechecked. Earlier functional GUI runs used the
preceding client with identical reading behavior; both binary identities are
recorded per run. Actual renderer screenshots were inspected by the agent;
this is separate from the developer's personal acceptance. OpenAL uses its null
backend for automated runs, so listening comfort is not claimed.

The normal runtime pair is CWM 2.25. Previous executables remain under
`artifacts/native-reading-20261018/native-previous-runtime` and
`client-previous-runtime`; restore them together for CWM 2.24 rollback. The
intermediate 2.25 client is also retained. Source commits, binary hashes, build
receipts, command recipes, artifact identities and exact check names are in
[the evidence receipt](native-reading-evidence.json).

Initial investigations are preserved locally: private actor access was replaced
with the public native activity progress API before the final build; old protocol
fixtures were corrected for seven reasons and an actual native player; a GUI
constant was replaced by the native character-adjusted duration. A subsequent
actual-renderer inspection found an old Consumption hint during reading; it was
fixed and the client rebuilt/rechecked. No native time was changed to satisfy a
test. Those earlier failed runs are not counted as final PASS.

## Personal validation and remaining scope

The [manual ledger](../validation/pending-manual.md) has **28 PENDING, no open
manual FAIL**: four new READ-01 checks and the previous 24 unchanged. No personal
test blocks this delivery; none is inferred from automation. Existing PASS entries
remain the sole human developer's reports, as explained in
[the public authorship/testing statement](../../HUMAN_TESTING.md).

Item mapping remains batch60. The five historical opt-in statistical melee
failures are still excluded from the active filter, not repaired or promoted.
Full SAVE-001 remains OPEN and historical M5.5 FAILED. Next functional slice:
native disassembly/related item work using the established activity, choice,
interruption and persistence boundaries; no advancement to M6 is claimed.

If the local fixture is absent, build the independent reader with the recipe in
the receipt, then create an isolated fixture (never point this at a user world):

```sh
artifacts/native-reading-20261018/native-save-reader --create-reading \
  --userdir artifacts/native-reading-20261018/fixture/user \
  --datadir cdda/data --output artifacts/native-reading-20261018/fixture/before.json
```
