# FND-02: trasporto limitato e errori di connessione contenuti

Il collegamento CDDA–Luanti ora conserva i frame completi prima di EOF,
contiene gli errori di framing e gestisce i lettori lenti con code limitate.
Branch `fix/fnd02-transport`; sorgenti eseguibili al commit
`f616b723e3ddcd0357fff35a04a45e59a0c5be34`. Identità, comandi, ambiente e
risultati nel [registro delle evidenze](fnd02-transport-evidence.json).

## Comportamento

Prima della modifica, il probe storico riproduce tre difetti: perdita del
frame finale, abort su prefisso troppo grande e attesa di circa 101 ms quando
il destinatario non legge. Lo stesso probe, senza modifiche alle asserzioni,
ora passa con ASan/UBSan. L'invio al peer lento accoda il messaggio senza
attendere la disponibilità del socket.

`send_message` significa accettazione nella coda FIFO, non consegna. Il pump
legge e scrive senza attesa nei due runtime: massimo 256 KiB per direzione,
64 tentativi di syscall per direzione e 8 messaggi consegnati per aggiornamento.
Il budget di consegna è 1 MiB, con eccezione per un singolo primo frame legale
più grande. La coda mantiene offset e ordine quando una scrittura è parziale.
I limiti sono configurabili tramite `IpcLimits`, con tetto assoluto del payload
16 MiB, staging di ingresso 16 MiB + 4 e uscita 32 MiB/128 frame.

Il prefisso viene validato prima del corpo. Il decoder conserva un cursore
anziché spostare la coda dopo ogni estrazione e limita anche la crescita della
sua allocazione. Framing invalido e FlatBuffers strutturalmente invalido
chiudono la connessione interessata. Un frame incompleto alla chiusura viene
classificato come troncato dopo i frame completi precedenti. Le eccezioni di
framing non escono dal trasporto verso il ciclo di simulazione/rendering.

Una coda piena chiude la connessione: non scarta delta lasciando il client
apparentemente sincronizzato. Una nuova connessione riceve lo snapshot completo
previsto dal ciclo esistente. I comandi nativi ancora in coda vengono cancellati
alla disconnessione; una risposta valida alla decisione nativa già in corso
può essere consumata prima di EOF. Le prove distinguono questo caso dalla
chiusura senza risposta, che conserva la scelta sicura.

Il server respinge un secondo peer finché il primo è vivo. Luanti usa connect
non bloccante e un solo timer di tentativo del bridge. La prova grafica ha
rilevato che il ciclo Game ricreava il bridge a ogni perdita di connessione,
cancellando proiezione e traccia: ora l'inizializzazione avviene una volta per
Client. Durante l'interruzione l'input resta disabilitato, gli attori vengono
nascosti e la proiezione statica viene conservata.

Il [contratto osservato](../../protocol/PROTOCOL.md) descrive limiti, EOF e
semantica di accodamento. La traccia diagnostica opzionale misura code,
byte/frame consegnati e tentativi I/O per aggiornamento.

## Evidenza e riproduzione

Prove e mondi sono isolati in `artifacts/fnd02-transport/`; nessuna partita
utente è stata usata. Le patch integrali dei fork e gli inventari sono
catturati in `baseline/`. Il workspace compilato è ricostruito dai pin e dalle
patch; prima della compilazione finale, l'esportazione della radice viene
aggiornata dal commit e il file Game dal fork catturato. Il controllo successivo
confronta inventari dei fork e contenuto/modo dei 217 file della radice.
Una seconda ricostruzione integrale del commit in `final-reconstruction/`
verifica che l'esportazione sia riproducibile senza il working tree originario.

Le build riusano oggetti del precedente workspace verificato solo quando
flag e tutte le dipendenze coincidono: **build incrementali, non cold-cache**.
La ricerca del `flags.make` del target ora copre anche gli oggetti CMake in
sottodirectory; una prova distinta verifica che dipendenze o flag modificati
continuino a impedire il riuso. I receipt conservano ogni oggetto accettato o
rifiutato. Il lettore dei salvataggi resta collegato al core pinned indipendente.

Verifiche principali:

- Probe storico ASan/UBSan: 5 controlli PASS.
- Nuova suite trasporto ASan/UBSan: 12 casi PASS, compreso un payload legale
  di 16 MiB, output parziale/FIFO, saturazione, EOF con molte consegne,
  troncamenti, half-close e budget sotto flusso continuo.
- Tre eseguibili di test del protocollo PASS; test nativi pertinenti
  `[cwm],[diving]` PASS e unit test Luanti PASS.
- Peer avversi su CDDA reale: errori di framing/FlatBuffers, seconda connessione,
  lettura ritardata e saturazione non terminano il processo. La lettura nativa
  indipendente conferma posizione/effetto sull'oggetto della risposta finale
  all'avviso d'acqua; i peer precedenti non muovono l'avatar né avanzano revisione.
- Luanti reale: 13 controlli PASS su frammentazione, flusso di circa 2,6 MiB,
  stato finale prima di EOF, frame malformati e tentativi successivi. Durante
  il flusso vengono osservati 13 frame grafici, intervallo massimo circa
  19,1 ms e budget letto massimo esattamente 256 KiB.
- Regressioni su input/camera, acqua/aperture e decisioni native: risultati
  e binari esatti nel registro. `start.sh` usa i due eseguibili verificati.

Comandi dalla radice; il registro conserva anche configurazione e cwd:

```bash
python3 tools/takeover_baseline.py check
python3 tools/takeover_baseline.py reconstruct --destination <directory-nuova>
cmake --build <workspace>/cdda/build --target cdda-server cata_test --parallel 1
cmake --build <workspace>/luanti/build --target luanti --parallel 1
ctest --test-dir <workspace>/protocol/build --output-on-failure
python3 tests/transport_runtime_test.py --workspace <workspace> \
  --fixture artifacts/exploration-fix/fixture-user \
  --native-reader artifacts/exploration-fix/native-save-reader --artifacts <output-nuovo>
python3 tests/transport_gui_test.py --workspace <workspace> --artifacts <output-nuovo>
```

## Confini della verifica

**FND-02 implementato con verifica mirata PASS. M5.5 storico resta FAILED;
SAVE-001 completo resta incompleto.** Il recupero dalla perdita di connessione
qui provato non certifica negoziazione, sequenze contigue, deduplicazione,
identità o reset del mondo: sono FND-03. I probe storici relativi a questi
problemi restano conservati. POSIX è ancora l'unico backend.

I budget limitano lavoro I/O, staging e consegne; non garantiscono il tempo
massimo di esportazione/ingestione di uno snapshot legale molto grande.
Il flusso grafico sintetico non sostituisce BM01/BM02 popolati. Validazione
semantica completa, luminosità locale, immersione, confine con nebbia e panorama
ricordato restano nei task già pianificati. Rilievo/flatness resta rinviato come
richiesto dall'utente. Non serve ripetere la checklist manuale già accettata
per iniziare FND-03.
