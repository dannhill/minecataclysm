# Native NPC trading — 2026-10-22

Linux **`./start.sh` supports native NPC trading**. Right-click a perceived,
non-hostile NPC, choose its native trade reply and edit the offer in the two
inventory panels. Select quantities, drag across panels or Shift-click to
toggle a whole stack. **Review and confirm** opens CDDA's confirmation. No
returns to the same editable offer; Cancel/Esc exits without an exchange.
`./trade-demo.sh --fresh` opens an isolated native trading scene.

Prices, credit/debt, willingness to buy/sell, ownership, containers, NPC pocket
capacity and the completed transfer use the native trade model and functions.
The client only proposes quantities. Native source fingerprints, quote and
connection identities prevent stale selection; the shared command ledger
prevents duplicate confirmed exchanges. The time stays paused while choosing.
Native shop restocking/drop-invalid-inventory occurs once on opening, as in
CDDA; cancelling does not undo these native opening effects.
[Detailed contract](../design/native-trade.md).

The native charge transfer previously consumed another same-type stack from
the giver's inventory. It now consumes the concrete selected item location.
The NPC pocket check now tests the offered charge quantity rather than the
whole unoffered stack. Native credit addition and whole-offer arithmetic use
wide intermediates and reject values outside native supported integer bounds.
No client economy, alternate inventory, new save format or invented trade cost
is introduced. The normal native chat action remains in effect at exit.

## Verification

- **167 native cases / 73,272 assertions PASS** across CWM, reading,
  disassembly, selected melee/ranged and upstream NPC talk. Focused trade
  coverage: **9 cases / 163 assertions PASS**, including four new cases for
  concrete charge sources, native confirmation/ownership/debt, read-only
  browsing, source changes/container overlap, offered capacity and credit math.
- **309 client tests / 47 modules PASS**, plus 648 Catch assertions / 4 cases.
  Protocol **15/15**, launcher language **9/9**, language registry **3/3** and
  the standalone trade view check PASS.
- **88 actual renderer/canonical checks PASS**: 33 trade checks against the
  reconstructed pair, 33 against the installed pair used by start.sh, and
  22 conversation regression checks. Actual mouse input exercises dragging,
  Shift-click, partial quantities, native No/Yes, cancellation and reconnect.
  Protocol probes on that connection exercise excess quantity, stale quote
  and a repeated accepted commit; only envelope sequences are adjusted for
  additional probe frames, never command identities or gameplay contents.

The unmodified pinned CDDA core independently creates and reloads the fixtures.
It confirms a 5-charge sale from the selected 30-charge stack, the other
20-charge stack untouched, one acquired bandage, native ownership, exact debt
and sold accounting, unchanged position and no fake activity. Replaying the
commit returns the cached native outcome. Screenshots were inspected by the
LLM agent, not counted as personal human acceptance.

[Exact source identities, hashes, commands and logs](native-trade-evidence.json).
Builds are incremental reconstructions with caches retained, not cold builds.
Investigation logs preserve the native test API setup errors, the confirmation
pause settlement repair, and the missing trade parser/drag routing caught by
the real renderer. Relay probe sequence/closure errors were in the harness;
final PASS follows their repair. No failed attempt is counted as a final PASS.

## Installed runtime and follow-up

CWM2.29 Linux native/client binaries are installed in normal start.sh. Previous
paired binaries are retained at `artifacts/native-trade-20261022/native-before-trade`
and `client-before-trade`; hashes are in the evidence. Developer worlds and
preferences were not used. Item mapping batch60 is unchanged; the Windows
installer remains its earlier CWM2.26 snapshot.

**45 PENDING, no open manual FAIL**: four new TRADE-01 cases in the
[human testing ledger](../validation/pending-manual.md), with the prior 41
unchanged. No new human PASS is inferred. Next core slice: native mission
journal and known objectives; specialised companion/services and broad mod/EOC
coverage remain open. Historical **M5.5 FAILED** and full **SAVE-001 OPEN**
remain unchanged.
