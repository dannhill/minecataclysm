# Sette gate personali del core — 2026-10-18

Fonte: riscontro diretto dell'unico sviluppatore umano nella conversazione.
Documento redatto da un LLM su quel riscontro, non da un test automatico.
L'utente autorizza a proseguire, rimandando i nuovi ricontrolli al backlog.

| Gate proposto | Riscontro umano | Collegamento al backlog |
| --- | --- | --- |
| T1 Indossa/Togli: pausa del debito nativo con I | PASS | Ricontrollo commenti 2026-10-13, punto 2; supera il FAIL |
| T2 Crafting: pausa, interruzione, incompleti/ripresa | PASS con bug collaterali | UX-05.3 |
| T3 Persistenza e ripresa del lavoro dopo quit/load | PASS | UX-05.4 per lo scenario provato |
| T4 Shift-clic e quantità | PASS | INT-01.2 |
| T5 Drop fuori finestra, raccolta diretta, nessun clic differito dalla pausa | PASS | INT-01.3; raccolta sfusa 1 e 3 |
| T6 Aperture e assenza di incastro nel caso provato | PASS con riserva su finestre/tende | INT-01.1; nuovo ricontrollo separato |
| T7 Il mondo/animazioni si fermano con F7/I/H | PASS | Animazioni di movimento.2 |

I sette gate non sono sette checklist complete aggiuntive. Non si deduce un
PASS per prove non comprese: per esempio la pila conteggiata della raccolta
sfusa e il rifiuto/recenza del crafting restano da provare separatamente.
L'accettazione del salvataggio riguarda lo scenario eseguito; non certifica
ogni combinazione di lingua, preferiti/recenti o il gate SAVE-001 completo.

## Bug e richieste associati

- Nel crafting l'avviso `Too many results: narrow the search` si sovrappone
  alle schede All/Favorites/Recent/Unfinished.
- Nella `crafting-demo --fresh`, la voce percepita come bandage, anche lotto
  quattro, mostra solo 0%, sparisce in meno di un secondo e non produce bende
  né un errore chiaro. Makeshift bandage funziona bene. Pausa/interruzione
  funzionano e il gate T2 resta PASS.
- Richiesta ricerca dinamica a ogni carattere, senza Invio; il cambio lotto
  deve conservare la ricetta selezionata.
- Dopo quit con I aperto/tempo fermo, il caricamento riapre il mondo senza
  inventario e riprende il lavoro. L'utente domanda se sia voluto: il costo/
  actor persistono nel save CDDA; il menu e la pausa di ispezione sono stato
  transitorio del client. Non introdurre un annullamento o cambiare il costo.
  Una ripresa inizialmente in pausa è una futura decisione di presentazione.
- Toggle non sufficiente per finestre e tapparelle/tende: richiesta di un
  comando tastiera di sola chiusura, esplicitamente diverso da Shift+RMB.
- Il segnale di poca luce migliora la percezione ma è troppo repentino;
  sotto una copertura aperta lateralmente il buio logico sembra incoerente.
  Rendere graduale la presentazione senza attribuire al renderer una nuova
  autorità sulla visibilità. Illuminazione 3D più completa resta nel piano.

## Indagine sul crafting

Nei recenti delle demo locali, consultati senza modificarne i salvataggi,
compare `nested_bandages`. Il dato nativo `nested_category` è navigazione,
senza oggetto prodotto, e il catalogo CWM lo trattava come lavoro eseguibile.
La correzione esclude le categorie e conserva le ricette effettive; non
modifica tempi, materiali o moltiplicatori delle bende native.

La demo fornisce fogli di cotone per makeshift bandage; la vera ricetta
`bandages` richiede anche materiali sanitari, nastro e disinfettante. I test
automatici devono distinguere esplicitamente categoria, materiali mancanti
e produzione reale di una o quattro lavorazioni.
