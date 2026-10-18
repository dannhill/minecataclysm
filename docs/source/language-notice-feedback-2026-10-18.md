# Language logic accepted; pause notice clarification

The sole human developer reported after `971579f`:

> va bene, ora la logica funziona, ma mi dice sempre "Riavvia start.sh per applicare.
> Italiano: WIP." anche se ho premuto poco prima su english(n.b. se il gioco è attualmente in inglese la scritta mi compare in inglese).

This accepts the repaired language-selection/persistence logic and closes the
renewed LANG-01.2 FAIL. The remaining observation concerns a fixed, ambiguous
notice. It does not request live translation of the active session.

Show the selected language for the next start immediately; when it matches the
session, show it as active without an unnecessary restart instruction. Qualify
the incomplete translation only when Italian is selected. Keep the notice in
the current session language until restart. The new notice has one deferred
personal readability recheck; no automated result constitutes human acceptance.
