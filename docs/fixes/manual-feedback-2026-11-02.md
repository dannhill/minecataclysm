# Seguito dei playtest: K e recupero sincronizzazione — 2026-11-02

Documento scritto da un LLM sulle direttive dirette dell'unico sviluppatore
umano. I PASS MENU-01.1 e UF8-01.1 sono dichiarazioni del developer; le prove
automatiche sotto sono distinte e non sostituiscono la sua accettazione.
[Riscontro originale e copertura](../source/manual-menu-rest-validation-2026-11-02.md).

## Correzioni installate

Nel menu del lavoro nativo il tasto configurato del crafting, normalmente K,
ora apre il catalogo e mette in pausa il crafting, attraverso il percorso di
ispezione già usato da I e dal pulsante Pause and inspect. La gestione resta
limitata al lavoro del crafting; identità, costi, interruzione e ripresa rimangono
nativi. Nessuna riapertura del menu mediante un frame intermedio di gameplay.

La sincronizzazione ora ha un limite di cinque secondi monotoni senza un mondo
autorevole installato. I cambi Syncing/Resyncing non rinnovano quel limite e la
pausa del motore non lo ferma. Alla scadenza il client chiude la connessione e
ritenta dopo due secondi reali, installando una proiezione completa prima di
riabilitare i comandi. Il watchdog non misura il ping e non interrompe una
connessione pronta solo perché la simulazione avanza lentamente.

Il recupero conserva il sonno canonico senza reinviare la richiesta di dormire.
Nuovi messaggi di log riportano motivo di chiusura, stato, sequenza, revisione
e metadati della prima proiezione rifiutata. Non inventano dati mancanti né
modificano i tempi o il formato dei salvataggi CDDA. Wire CWM2.37 invariato da
queste correzioni locali.

## Episodio intermittente: causa ancora non dimostrata

Nel log locale `artifacts/runtime/20261102T150356Z-684359/` è presente una
chiusura trasporto con motivo 6, IoError, e il salvataggio canonico ha avuto
successo. Mancano dettagli per collegare con certezza quella chiusura al
messaggio visto dal developer o per attribuire una causa iniziale.

Dal codice risultavano invece due difetti verificabili del recupero: il timer
era azzerato da ogni cambio di stato e dipendeva da dtime, fermo sotto la pausa
Esc. La regressione automatica riproduce questi difetti con proiezioni invalide
durante il sonno; non pretende di riprodurre la causa originaria del playtest.

## Verifica e identità

Fotografia privata verificata:
`artifacts/manual-feedback-20261102/source`, commit
`e1875ce701a71dca841ef6279733ea934e43180a`. Include i refactor già presenti
all'inizio della sessione, separati dal delta di questa correzione. Branch,
indice e HEAD del repository di lavoro sono rimasti invariati. Nessun commit
o push di quei refactor come se fossero parte di questo intervento.

Le due ricostruzioni sono state aggiornate dalla fotografia, confrontando file
e inventari dei fork, poi compilate con cache conservate. Prima dell'aggiornamento
era stata trovata metadata baseline obsoleta nelle cache: i byte dei fork
corrispondevano esattamente alla baseline preesistente acquisita all'ingresso.
La vecchia metadata è conservata e la riparazione è documentata. Non è una
build da zero né un audit completo di tutte le funzioni.

| Prova automatica | Risultato |
| --- | --- |
| Suite nativa selezionata | 185 casi, 73.766 asserzioni PASS |
| Unità Luanti | 309 test/47 moduli e 648 asserzioni/4 casi PASS |
| SDK/presentazione | 21 test PASS, incluso watchdog con tempo controllato |
| GUI crafting con K | 30 controlli PASS su ricostruzione, 30 su binari installati |
| GUI sonno e proiezioni invalide | 28 controlli PASS su ricostruzione, 28 su binari installati |

Ogni prova di sincronizzazione consegna 34 snapshot con un bit di pausa
sconosciuto, conservando il flusso originale CDDA separatamente. Con Esc in
pausa, il watchdog scade dopo cinque secondi reali e il client si ricollega;
il tempo nativo rimane fermo, il personaggio rimane addormentato e una nuova B
funziona senza riavviare il sonno. I test successivi coprono F8, ispezione,
riconnessione e rilettura del salvataggio mediante un core CDDA pinned non
modificato. La corruzione è esclusivamente nel relay della prova.

Totale: **116 controlli renderer/canonici**, due scenari ripetuti sui due
ambienti, non 116 scenari indipendenti. Tutti i driver hanno exit code 0
registrato. Screenshot crafting-paused e sleep-reconnected dei binari
installati ispezionati dall'LLM. Nessuna nuova validazione umana implicita.

Il client compilato e il server verificato sono installati nei percorsi usati
da `start.sh`; la coppia precedente è conservata negli artifact. Salvataggi e
configurazioni delle prove sono isolati dai mondi del developer.
Comandi riproducibili, hash, ricevute delle ricostruzioni e binari sono nel
[registro delle evidenze](manual-feedback-2026-11-02-evidence.json).

## Backlog e limiti

MENU-01.1 e UF8-01.1 restano PASS umani. I nuovi KEY-K-01.1 e SYNC-01.1 sono
PENDING, senza obbligo di eseguirli subito. LIQ-01.3 e SEAL-01.4 non sono stati
provati in questo giro; REST-01.4 rimane separato. Totale **59 PENDING**, nessun
nuovo FAIL manuale. [Checklist](../validation/pending-manual.md).

Mapping batch60, build Windows CWM2.26 e gate storico M5.5 FAILED / SAVE-001
OPEN restano invariati. Queste prove non certificano il gioco completo o la
causa iniziale dell'errore intermittente. Prossima fetta core invariata: usi
nativi essenziali e output liquidi/purificazione sicuri, poi consolidamento
del loop in mondi normali.
