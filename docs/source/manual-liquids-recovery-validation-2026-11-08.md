# Riscontro umano: recupero, K e liquidi — 2026-11-08

Documento scritto da un LLM su direttive e risultati comunicati direttamente
dall'unico sviluppatore umano. Questi PASS sono playtest umani; non derivano
dalle prove automatiche dell'agente.

Il giro proposto e accettato corrisponde a:

1. **SYNC-01.1 PASS** — sonno e consultazione dopo il fix del recupero.
2. **KEY-K-01.1 PASS** — K apre il crafting in pausa durante il lavoro.
3. **LIQ-01.3 PASS con commenti separati** — fonte finita e consumo.
4. **SEAL-01.4 PASS** — persistenza degli stati aperto/sigillato e dei contenuti.

Il developer non precisa se nel primo test sia ricomparso un vero guasto di
sincronizzazione. Il PASS chiude il ricontrollo personale proposto; non prova
la causa dell'episodio originale né una riproduzione manuale di quella fault.
REST-01.4, persistenza del sonno, rimane separato e pendente.

Backlog: **59 meno quattro =55 PENDING**. Nessun PASS precedente revocato e
nessun ulteriore test aggiunto per i commenti di questo giro.

## LIQ-FB-01 — Segnalazioni sui liquidi, OPEN

Il developer osserva che il trasferimento in un contenitore è istantaneo.
Dopo aver versato acqua per terra, un nuovo clic produce il messaggio
«no native liquid activity started» senza effetto evidente. L'acqua appare
come un drop di acqua sporca non interagibile col destro. Il comportamento si
ripete versando da un contenitore impugnato. Non è documentata una quantità
persa o duplicata, né una modifica indebita del tipo di liquido: non dedurle.

Il contratto esistente ammette travasi da contenitore applicati immediatamente
con debito di mosse nativo, distinti dall'attività ACT_FILL_LIQUID. Non aggiungere
una durata cancellabile fittizia. La sola apparenza istantanea non dimostra
che il tempo non venga addebitato.

Il ramo EXAMINE in `cdda/src/cwm/cwm_server.cpp` determina l'accettazione con
`bool(u.activity)`: un'operazione senza attività può ricevere la diagnostica
generica anche se ha avuto effetti immediati. Le fonti riconosciute da
`liquid_source_kind` sono handler di terreno/arredo; un liquido versato come
item a terra non diventa automaticamente una fonte riconosciuta. La gestione
dei liquidi selezionati richiede inoltre un parent container. Questi limiti
vanno confrontati con la gestione nativa dei liquidi versati prima di decidere
se aggiungere recupero oppure una spiegazione grafica dell'acqua versata.
Non classificare il comportamento come voluto o già corretto dal solo PASS.

Il seguito deve distinguere esito applicato, annullamento e fallimento senza
usare la sola presenza di un'attività; chiarire anche presentazione e possibili
azioni sull'acqua a terra. Nessuna modifica di codice, regola o build in questo
aggiornamento documentale.

## Prossimo giro prioritario, ancora PENDING

1. **REST-01.4** — salvare durante il sonno e ricaricare senza riavviarlo.
2. **DIS-01.4** — salvare lo smontaggio in corso, conservando progresso e risultato unico.
3. **READ-01.2** — completare un capitolo con progressione teorica reale; annullamento senza premio.
4. **TRADE-01.2** — offerta parziale, No e poi conferma, quantità e saldo nativi.

I quattro punti sono già nel backlog; questo elenco non li duplica e non
anticipa la loro accettazione. I test del nuovo giro non sono eseguiti qui.

## Secondo riscontro umano: quattro ulteriori PASS

Al giro sopra il developer risponde direttamente «1 PASS 2 PASS 3 PASS 4 PASS»:

1. **REST-01.4 PASS** — salvataggio durante il sonno e proseguimento dopo il caricamento.
2. **DIS-01.4 PASS** — progresso dello smontaggio conservato, completamento senza duplicazioni.
3. **READ-01.2 PASS** — annullamento senza premio e capitolo con progressione teorica.
4. **TRADE-01.2 PASS** — offerta parziale, rifiuto e conferma con quantità e saldo corretti.

Questo secondo messaggio è un risultato di playtest umano, non una deduzione
da prove automatiche. Non aggiunge commenti o nuovi difetti. **55 meno quattro
=51 PENDING**. I PASS precedenti e LIQ-FB-01 OPEN restano invariati.

La copertura segue le quattro istruzioni effettivamente proposte: non accetta
automaticamente gli altri test READ-01, TRADE-01, DIS-01 o NPC-01. In particolare
il PASS dello scambio non è una nuova prova del suo salvataggio/ricaricamento;
il PASS del capitolo non verifica da solo interruzione o persistenza della lettura.
Nessuna modifica di codice, build, protocollo o percentuale core da questo
aggiornamento documentale.

## Terzo giro proposto, ancora da eseguire

Alla domanda del developer se ci siano altri test, le prossime quattro prove
selezionate tra le 51 già pendenti sono:

1. **TRADE-01.4** — ricaricare lo scambio appena accettato senza `--fresh`,
   verificando quantità/saldo e assenza di un secondo scambio automatico.
2. **READ-01.3** — pausa, interruzione e ripresa dello stesso capitolo;
   conservare il lavoro pagato senza esperienza gratuita per l'interruzione.
3. **READ-01.4** — proseguire la prova precedente con salvataggio durante la
   lettura e riavvio senza `--fresh`, senza duplicare libro o esperienza.
4. **SEAL-01.2** — acqua inaccessibile attraverso il sigillo; consultare non
   lo apre, apertura esplicita abilita le azioni consentite dalle regole native.

Sono proposte di test, non risultati. Il contatore resta 51; nessun nuovo
test o obbligo di completare tutto il backlog prima di proseguire lo sviluppo.
