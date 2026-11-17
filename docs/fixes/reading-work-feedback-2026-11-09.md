# Lettura: avvisi nativi e pannello di progresso — 2026-11-09

Documento scritto da un LLM su direttive dirette dell'unico sviluppatore umano.
I quattro PASS del [riscontro](../source/manual-reading-feedback-2026-11-09.md)
restano risultati di playtest umani. Le verifiche delle correzioni descritte
qui sono automatiche; non sostituiscono i due ricontrolli personali.

## Correzioni

Una domanda nativa sopraggiunta durante un lavoro invalida ora la cache della
schermata di progresso. Dopo la risposta, la finestra torna al lavoro anche
se il contenuto del progresso non è cambiato. Prima poteva rimanere una
finestra di attesa obsoleta che veniva trattata come consultazione in pausa.

I continua ad aprire l'inventario in pausa. Chiudendolo durante un'attività,
si torna allo stesso pannello di progresso dell'avvio. Esc/Return to game
nasconde il pannello senza annullare il lavoro; I e ancora I lo riaprono.
Il bridge usa l'attività/tempo nativo già osservato, senza inviare un nuovo
comando di lettura o consumo. Anche le attività caricate da un salvataggio
possono usare questo percorso senza inventare un'identità di comando.

Il pannello mostra lo stesso titolo, libro e progressione teorica prima e
dopo la consultazione; l'overlay precedente non si sovrappone al pannello
modale. Il passaggio dalla consultazione al progresso conserva la stessa
finestra, evitando un frame intermedio di gameplay.

Le modifiche di produzione sono nel bridge C++ Luanti e nella chiusura delle
formspec. Nessuna modifica alle regole o ai sorgenti nativi CDDA in questo
intervento. No continua una volta, Ignore segue la logica nativa per quella
distrazione; non si sopprimono gli avvisi e non si risponde automaticamente.
Pausa, costi e salvataggio canonico restano nativi. Protocollo CWM2.37 invariato.

## Verifica

Il difetto della domanda di congelamento è riprodotto con i binari precedenti
in `artifacts/reading-feedback-20261109/before-fix/`: dopo No la lettura rimane
attiva ma ferma con Menu pause, una finestra presente e nessuna decisione
pendente. La prova termina con exit1. Si usa esclusivamente una copia isolata
del salvataggio della fixture, mai una partita del developer.

La regressione finale attiva la stessa domanda mediante temperatura corporea
canonica di test: 1800 unità legacy, 30,6 °C, sotto la soglia nativa di 31 °C.
Sceglie No, risponde alla successiva domanda con Ignore e gestisce esplicitamente
un ulteriore avviso nativo di danno se compare. Controlla che la lettura avanzi,
che I la fermi, che la chiusura di I riusi lo stesso pannello senza frame di
gameplay e che Esc → I → I lo riapra senza inviare una nuova lettura.

La prova di consumo controlla lo stesso ciclo per una bevuta a 0,5x con F8,
poi ripristina 4x e verifica quantità, costo, annullamento, rifiuti e recovery.
La lettura ordinaria viene anche salvata in corso e ricaricata, con rilettura
canonica tramite il reader collegato al core CDDA pinned non modificato.

PASS: unità client **309 test /47 moduli**, più **648 asserzioni /4 casi**;
SDK **21 test**. **163 controlli renderer/canonici** in sei esecuzioni:
freddo 19/18 e consumo 43/43 su ricostruzione/binari installati, lettura
ordinaria con salvataggio27 e ricaricamento13. La differenza nel freddo è il
controllo opzionale dell'ulteriore avviso nativo di danno. Tutti i driver hanno
exit code0 registrato; non sono 163 scenari indipendenti.

Build incrementale da fotografia privata
`804628bb9fd689f5e647cb0cff6f409e0576ee22`, preservando i refactor locali già
presenti. I driver finali, affinati per gestire anche i successivi avvisi nativi
della fixture, sono identificati separatamente tramite checksum. La fotografia
di build rimane immutabile. Nessun commit/push del working tree del developer.

Prove, conteggi effettivi, ricevute e hash dei binari sono nel
[registro delle evidenze](reading-work-feedback-2026-11-09-evidence.json).
La build non è una nuova verifica da zero o una certificazione del gioco completo.

## Installazione e backlog

Il client verificato è installato in `luanti/bin/luanti`, usato dal normale
`start.sh`. Il client precedente è conservato negli artifact. Il server nativo
ha lo stesso hash della coppia precedente e di quello usato nelle prove.
La sostituzione è atomica: i processi di gioco già aperti continuano a usare
il loro binario precedente; chiudere e rilanciare applica il nuovo client.

TRADE-01.4, READ-01.3, READ-01.4 e SEAL-01.2 restano PASS umani. I precedenti
punti pendenti sono47; READ-FB-01.1 e WORK-FB-01.1 danno **49 PENDING**.
I due ricontrolli si possono rinviare. LIQ-FB-01 OPEN, mapping batch60,
Windows CWM2.26 e gate storico M5.5 FAILED / SAVE-001 OPEN restano separati.
