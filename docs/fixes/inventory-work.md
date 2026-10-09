# UX-02 — Azioni consecutive e completamento nativo

Implementazione del 2026-10-09 per il prossimo passo autorizzato. Dopo una
singola azione da I il menu lascia scorrere il mondo; un indicatore compatto
mostra operazione/progresso nativo e I torna alla vista precedente al termine.
Le azioni restano una per volta e richiedono una scelta esplicita.

## Comportamento e limiti

Valido per Impugna/Riponi/Indossa/Togli, Mangia/Bevi/Medica e i trasferimenti
posseduti. Pagina, filtro, ricerca aperta/applicata, dettagli e tipo di pannello
rimangono. Una query nuova azzera oggetto/destinazione/quantità: identità stabili
tra query restano da implementare, senza selezionare oggetti omonimi a intuito.
Il ritorno non trasferisce automaticamente altri oggetti e non è un batch.

Durante il lavoro il pannello è non modale e non prende focus/input. I apre
la consultazione e mette in pausa come prima; Interrompi cancella il vero
actor nativo e conserva i costi già spesi. Esc lascia il mondo aperto e rinuncia
al ritorno automatico, senza annullare né rimborsare l'azione. Prima della
spedizione rinuncia anche alla scelta ancora in coda. F7/minacce sopprimono
il ritorno; decisioni native lo sospendono. Morte/disconnessione/resync scartano
l'intenzione locale, senza cancellare il lavoro canonico salvato.

Il progresso percentuale esiste solo se l'actor dichiara un totale positivo;
il deposito senza durata fissa resta “in corso”. Nessun conto alla rovescia
inventato dal client. Il crafting da K e la ricarica avviata nel mondo
conservano il loro flusso; Interrompi da I può tornare a I dopo il cancel.

## Confine autorevole

CWM 2.16 aggiunge `WorldSnapshot.inventory_work`: command_id nonzero e settled.
`completed_command_id` continua a significare primo risultato pubblicato,
che può arrivare prima che i costi siano pagati. Non si riapre al solo ACK.

Le azioni brevi consumano i moves nativi e il coordinatore ne paga la durata.
I due cicli canonici `u.activity.do_turn` notificano l’addebito effettivo sulla
stessa thread; il clock paga anche la frazione finale dell'attività. Il provider
è scoped e viene ripristinato dopo ogni turno, come azione/scelte/world gate.
Settled richiede actor concluso/interrotto, moves positivi dopo eventuale
recupero del debito e deadline pagata in RT. In modalità a turni vale il credito
nativo senza aggiungere ritardi grafici. Cancel conserva il deadline già
addebitato; reset/reconnect azzerano solo la correlazione, non il save.
La morte è esportata con hp_percent=0 per il player, prima indicato sempre 100.
Nessun campo Luanti nel protocollo e nessuna serializzazione canonica nuova.

## Evidenza e prove rinviate

Le verifiche riproducibili e gli hash saranno registrati nel receipt
[inventory-work-evidence.json](inventory-work-evidence.json). Build sui sorgenti
ricostruiti con cache, non clean build fredda. Artefatti locali:
`artifacts/ux02-inventory-work-20261009/`. I tentativi GUI preliminari sono
conservati separatamente: driver con ripressione I concorrente al ritorno e
scelta nativa per riporre la mazza non gestita. La seconda prova ha inoltre
intercettato il collegamento Esc mancante nel dispatch dei tasti, corretto
e soggetto a nuova prova prima della consegna. Non sono risultati PASS.

Quattro nuove prove [manuali](../validation/pending-manual.md), totale
20 PENDING, senza obbligo di eseguirle ora. Nessuna accettazione grafica dedotta.
M5.5 resta FAILED storico e SAVE-001 completo OPEN. Prossimo task UX-03:
hotbar interattiva con selezione distinta dalla mano e costi nativi.
