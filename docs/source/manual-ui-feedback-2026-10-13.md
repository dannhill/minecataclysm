# Riscontro manuale UI — 2026-10-13

Fonte: modifiche dirette dell’utente al backlog, preservate integralmente sotto.
12 nuovi PASS: UI/mapping 4, hotbar DND 4, mano/contenitori 2, lingua 1,
mira RMB 1. Lingua 2 FAIL: ritorno italiano → inglese non persistente.
13 punti non provati rimangono PENDING; nessun PASS automatico.

Richieste/commenti: evitare la vista vuota fra layout DND e risposta; mostrare
il pagamento temporale nativo per Indossa/Togli; destinazioni contenitore più
grandi; valutare cambio lingua senza restart e distinguere gesto di mira da
precisione CDDA già pagata, inclusa compatibilità col movimento.

Il restart resta necessario in questa fetta: entrambi i processi caricano cataloghi
ed etichette native all’avvio. Cambio a caldo è separato dalla correzione della
preferenza. RMB è già mantenuto, non toggle; al rilascio termina il gesto e non
arrivano nuovi passi AIM. Non si azzera la precisione già pagata; il movimento
conserva la penalità nativa. Un’eventuale postura/zoom di mira sarà visiva e
mostrata solo mentre il tasto è mantenuto. Nessuna nuova regola di tiro approvata.

```diff
diff --git a/docs/validation/pending-manual.md b/docs/validation/pending-manual.md
index 458bdf6..4c9e0e8 100644
--- a/docs/validation/pending-manual.md
+++ b/docs/validation/pending-manual.md
@@ -319,7 +319,7 @@ Quantità sovrapposta, tag hint ed errori poco visibili rimangono bug aperti.
 [Dettagli tecnici](../fixes/native-transfer.md).
 
 
-## Ricontrolli mirati del riscontro UI e mapping — PENDING (4), quando puoi
+## Ricontrolli mirati del riscontro UI e mapping — PASS(manually modified from PENDING to PASS) (4), quando puoi
 
 I 16 PASS precedenti restano acquisiti. Non occorre ripeterli né fare queste
 prove oggi. La revisione completa dell'interfaccia è pianificata: il layout
@@ -434,7 +434,8 @@ di errore: non chiedere di terminare processi della partita personale.
    Nessun input di gioco parte mentre manca lo stato autorevole completo.
 
 
-## UX-03 — Hotbar con drag-and-drop — 1 RICONTROLLO PENDING; 2–4 PENDING
+## UX-03 — Hotbar con drag-and-drop — PASS(modificato manualmente da me, controlla
+vari commenti manuali che ho inserito, ma in complessiva è PASS)
 
 Il precedente punto **1 FAIL di ergonomia** riguarda la versione a pulsanti
 CWM 2.17, conservata nel [riscontro](../source/ux03-drag-feedback-2026-10-09.md)
@@ -457,18 +458,29 @@ non tasche nuove. Non occorre ripetere i PASS inventario/equipaggiamento.
    Un clic breve continua a selezionare/aprire i dettagli.
    Fuori da I, icone coerenti con l'inventario; selezione **oro**, mano reale
    **azzurra**. L'oggetto in mano compare anche nel riquadro separato a destra
-   quando non è assegnato a uno slot.
+   quando non è assegnato a uno slot.(commento manuale da me: quando faccio drag and 
+   drop l'interfaccia si chiude e si apre velocemente in modo fastidioso, io 
+   toglierei questa cosa.)
 2. **Seleziona e usa**: rotella oppure 1–9 selezionano senza equipaggiare.
    **3, poi G** richiedono Impugna del sasso; scegli esplicitamente dove
    riporre la mazza. **2, poi G** indossano il cappello, un nuovo G lo toglie.
    Tempo/costi sono nativi; G dal mondo non forza il ritorno automatico a I.
-   In I puoi scegliere le altre azioni con i pulsanti del dettaglio.
+   In I puoi scegliere le altre azioni con i pulsanti del dettaglio.(commento manuale
+   dopo testing: quando tolgo o indosso qualcosa mi dice "in progress" e mi fa
+   attendere ma non mi dice il progresso attuale. Non so se è intended, ma prima
+   mi ricordo che la percentuale di progresso era presente. Devo ancora capire 
+   cosa ha senso)
 3. **Pausa, lavoro e perdita**: F7 → G non usa né accoda; riprendendo non
    parte un'azione ritardata. G durante un'attività non accoda altre azioni.
    Deposita un oggetto assegnato usando I → Quantità e trasferimenti: il
    riferimento scompare; raccoglierlo di nuovo non lo riassegna da solo.
    Nella demo consumo puoi assegnare una mela: G mangia la precisa mela
-   scelta; quando consumata, il riferimento non passa a una mela omonima.
+   scelta; quando consumata, il riferimento non passa a una mela omonima.(commento
+   manuale dopo il testing: la mela mangiata con G funziona e ho notato che qui
+   la percentuale di progresso è corretta e funzionante mentre prima non era così
+   per il wearing, forse è solo nel consumption demo che funziona e nelle altre no?
+   da indagare. EDIT: no, il progress bar e percentage nel wearing non funziona
+   neanche in consumption demo)
 4. **Persistenza**: lascia cappello/sasso assegnati e almeno uno indossato o
    impugnato; esci e rilancia `./equipment-demo.sh` senza `--fresh`. I e HUD
    devono conservare gli stessi oggetti, non i primi della nuova lista.
@@ -478,7 +490,8 @@ non tasche nuove. Non occorre ripetere i PASS inventario/equipaggiamento.
    né uno spostamento fra tasche. Rimozione/riassegnazione rimangono coerenti,
    senza duplicazioni.
 
-## UX-03D — Mano, indossati e contenitori — PENDING (2), rinviabili
+## UX-03D — Mano, indossati e contenitori — PASS(modificato manualmente da me
+dopo i test), rinviabili
 
 1. **Equipaggiamento col gesto**: `./equipment-demo.sh --fresh`, I.
    Trascina il cappello dalla griglia in uno spazio Indossati, poi dal
@@ -499,6 +512,8 @@ non tasche nuove. Non occorre ripetere i PASS inventario/equipaggiamento.
    trascinare un oggetto trasferibile sull'icona di un contenitore, senza
    aprire questa sottovista; per quantità precise usa il pannello avanzato.
    Le destinazioni evidenziate restano soggette alla verifica di capacità CDDA.
+   (commento manuale dopo test: io metterei i rettangoli dei container in quantità
+   e trasferimenti più grandi per il drag and drop, per il resto tutto bene per ora)
 
 ## Ricontrolli UX-03 — VALIDATA: 1–3 PASS
 
@@ -526,7 +541,7 @@ nel [report UX-03](../fixes/interactive-quickbar.md); non costituiscono PASS
 manuali. La lingua ha ora la checklist separata sotto; mira RMB, UV/rig,
 animazioni e suoni restano nel piano.
 
-## LANG-01 — Lingua del prodotto — PENDING (2), rinviabili
+## LANG-01 — Lingua del prodotto — 1 PASS e 2 FAIL(modificato manualmente dopo test), rinviabili
 
 Disponibile dal normale `./start.sh`; non serve fare queste prove oggi.
 I PASS precedenti rimangono accettati. Le prove automatiche delle due lingue
@@ -547,9 +562,15 @@ non attestano la tua accettazione della leggibilità e del menu.
    Riporta il selettore su English e riavvia: la scelta persiste e anche
    i testi nativi tornano inglesi. Il cambio lingua non riordina né duplica
    gli oggetti e non cancella i salvataggi. Non serve ripetere i vecchi
-   test di persistenza o tutte le azioni inventario già validate.
+   test di persistenza o tutte le azioni inventario già validate.(commenti manuali
+   dopo testing: ma non si potrebbe fare che quando si cambia la lingua il 
+   restart non sia necessario?)
+   (commenti manuali fatti dopo i test: dopo aver impostato italiano e riavviato
+   viene cambiato in italiano, ma poi nel menu a tendina se ripremo sulla freccetta
+   e seleziono inglese non me lo cambia e se riavvio il gioco rimane in italiano)
 
-## AIM-01 — Mira con destro mantenuto — PENDING (3), rinviabili
+## AIM-01 — Mira con destro mantenuto — 1 PASS 2-3 NON ANCORA TESTATI(modificato
+a mano dopo aver effettuato i test), rinviabili
 
 Non serve fare queste prove oggi. [Regole e priorità](../design/held-mouse-aim.md).
 La demo isolata è `./ranged-demo.sh --fresh`; il comportamento è disponibile
@@ -563,6 +584,11 @@ prima di riprendere da una pausa di minaccia. F resta una scorciatoia alternativ
    raffiche nuove. Rilascia il destro: non arrivano altri passi di miglioramento.
    La precisione già pagata può restare finché non ti muovi/fai altro. R ricarica
    con scelte e costi nativi; dopo il lavoro rilascia e ripremi destro per mirare.
+   (commenti manuali dopo aver testato: io farei che lasciando il tasto destro
+   la mira sparisce proprio, non che è un tasto toggle, ma possiamo discuterne,
+   tu che ne pensi? quali sarebbero le ripercussioni a livello di design? inoltre
+   mentre si tiene il tasto mira premuto ci si può muovere? Nel caso, ha senso
+   permettere di muovere mentre si tiene mirato?)
 2. **Interazioni**: nella partita normale o demo di controlli, RMB apre porte e
    finestre; Shift+RMB le chiude (per una finestra aperta punta il davanzale).
    RMB sugli oggetti a terra raccoglie/apre la raccolta; tenere quel clic non
```
