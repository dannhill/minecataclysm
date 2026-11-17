# Riscontro umano: lettura, pannelli e persistenza — 2026-11-09

Documento scritto da un LLM sulle direttive e sui risultati comunicati
direttamente dall'unico sviluppatore umano. I quattro PASS sono playtest
umani, distinti dalle successive prove automatiche e dalle correzioni.

La risposta «1 PASS 2 PASS ... 3 PASS 4 PASS» corrisponde al giro proposto:

1. **TRADE-01.4 PASS** — persistenza dello scambio già eseguito.
2. **READ-01.3 PASS con segnalazioni separate** — pausa/interruzione/ripresa.
3. **READ-01.4 PASS** — persistenza della lettura in corso.
4. **SEAL-01.2 PASS** — accesso ai liquidi dopo apertura del sigillo.

Non estendere questi risultati agli altri test degli stessi moduli. Il totale
dei test precedenti ancora pendenti scende da **51 a47**.

## Segnalazioni separate

- **READ-FB-01:** compare «You are freezing. Stop reading? (Case sensitive)»;
  scegliendo di continuare, il pannello rimane bloccato e non è possibile
  aprire o chiudere altre schermate. La lettura ordinaria mantiene il PASS.
- **WORK-FB-01:** il pannello iniziale della lettura differisce da quello
  ottenuto dopo I e ancora I, pur svolgendo la stessa funzione. Dopo Esc per
  nascondere il progresso manca una via chiara/funzionante per riaprirlo.
  Il developer segnala quest'ultimo problema anche bevendo.

Il freddo, i rischi e le decisioni devono rimanere nativi; non eliminare
l'avvertimento o scegliere automaticamente la risposta per evitare il blocco.
La finestra di progresso deve essere coerente prima/dopo la consultazione,
riapribile senza reinviare l'azione e senza un frame involontario di gameplay.

## Diagnosi riprodotta prima del fix

`artifacts/reading-feedback-20261109/before-fix/` usa i binari installati
precedenti, una copia isolata del salvataggio della fixture e temperature
corporee di test impostate per attivare l'autentico avviso CDDA. Il flusso
e il salvataggio del developer non sono modificati.

Dopo la risposta No il client ha `pending_decision=0`, lettura ancora attiva,
`pause_reasons=2` (Menu), `action_menu=1` e una finestra ancora presente. La
prova non raggiunge la successiva decisione e termina con exit code1.
La cache del progresso rimaneva valida quando la domanda nativa lo sostituiva:
al ritorno non veniva necessariamente ridisegnato il pannello; il menu rimasto
veniva trattato come una consultazione e teneva fermo il tempo.

L'uscita da I conservava inoltre soltanto il vecchio overlay non modale, invece
del pannello usato all'avvio. Esc poteva disarmarne la visualizzazione senza
un percorso che la ripristinasse all'uscita dalla consultazione.

Due ricontrolli personali delle correzioni sono separati dai quattro PASS:
READ-FB-01.1 e WORK-FB-01.1. Il totale con questi due nuovi punti è **49 PENDING**;
nessuna loro accettazione viene dedotta dalle prove automatiche.

Le correzioni locali sono installate e verificate separatamente nella
[consegna del 2026-11-09](../fixes/reading-work-feedback-2026-11-09.md).
I due ricontrolli personali restano rinviabili; gli avvisi restano nativi.

## Prossimo giro prioritario proposto

Alla domanda successiva sulle quattro prove più importanti, la corrispondenza
è registrata per non confondere risposte numerate e casi del backlog:

1. **READ-FB-01.1** — risposta alla distrazione nativa nella lettura; No continua
   una volta, Ignore segue le regole native. Se il difetto/avviso non ricompare,
   dichiarare «non riprodotto», senza richiedere un'esposizione volontaria al freddo.
2. **WORK-FB-01.1** — stesso pannello prima/dopo I e riapertura dopo Esc → I → I,
   sia durante la lettura sia durante una bevuta rallentata con l'unico F8.
3. **TRADE-01.3** — quantità non disponibile, offerta troppo costosa quando
   possibile, rifiuti comprensibili senza scambio e assenza di comandi accodati in pausa.
4. **Ricontrolli dopo i sette gate, punto2** — categoria non avviabile, lotto
   modificabile senza perdere selezione, quattro lotti che producono otto
   makeshift bandages dopo il costo nativo, senza risultati fantasma a0%.

Tutti già pendenti, nessun nuovo test né nuova accettazione. Totale49 invariato.
