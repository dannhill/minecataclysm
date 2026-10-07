# Ground items: ripresa e backend PICKUP

Documento storico del backend 2.4. La successiva GUI e la consegna 2.5
sono registrate in [ground-items-ui.md](ground-items-ui.md).

Verifica circoscritta completata il 2026-10-07. Prosegue il passo finale
della [continuazione recuperata](../source/continuation-2026-10-07.md), senza
modificare l'ordine del piano. Identità sorgenti verificata:
`299a594da7ead1082feec132c6246f932ce5c1f7`, con patch e inventari completi
in `baseline/`. M5.5 rimane FAILED.

## Comportamento

CWM 2.4 conserva nella coda il tile assoluto e il guard della selezione:
indice nello stack, type ID, charges e count-by-charges. All'esecuzione,
CDDA rivalida portata, presenza e guard prima di assegnare l'attività nativa
di pickup. Cambi di origine della reality bubble non cambiano il bersaglio.
Una richiesta diventata obsoleta viene rifiutata senza trasferire oggetti.

Il guard completo partecipa anche alla deduplicazione: riutilizzare lo
stesso command ID per un'altra selezione chiude la connessione; ripetere
la stessa richiesta non trasferisce due volte l'oggetto. Quantità zero
significa l'intero stack selezionato. L'ACK positivo conferma l'assegnazione
dell'attività, non il completamento del trasferimento. Tasche, capacità,
costi e completamento restano nativi.

I binding Python sono aggiornati insieme a quelli C++; i peer di prova
negoziano 2.4. Entrambi i runtime sono installati nelle posizioni usate da
`start.sh`. Il precedente client è conservato nel rollback degli artefatti;
il server in quella posizione risultava assente prima dell'installazione.

## Mapping già disponibile

Importati esclusivamente i nove `batch-XXXX-output.json` di produzione:
360 record, 88 definizioni di presentazione utilizzabili, 25 corrispondenze
che richiedono ancora fallback e 247 `NO_GOOD_MATCH`; 18 texture estratte.
Il batch 8 conteneva virgolette non escape in un marcatore di citazione:
corretto solo il formato JSON, conservando tutte le scelte. L'originale
e la ricevuta della correzione sono negli artefatti.

Il sync è idempotente e mantiene le attribuzioni dei media. La provenienza
e i checksum dei nove output sono in
`game/mods/cdda_items/mapping_provenance.json`. I nomi visuali derivano
deterministicamente dal type ID; la mappatura può continuare senza rebuild
e senza bloccare lo sviluppo del gameplay. I proxy procedurali usano per
ora il visuale di base, senza generare nuove varianti.

## Evidenza

Artefatti: `artifacts/playable-core-pickup-20261007/`.

- Ricostruzione incrementale con cache e replay indipendente delle patch:
  PASS, incluse verifiche di contenuto/mode degli inventari.
- Build CDDA server/test, Luanti e protocollo: PASS.
- Protocollo: 5/5 test PASS.
- Luanti: 305 test PASS e 648 asserzioni Catch2 PASS.
- CDDA, filtro `[cwm],[diving],[pickup]`, seed 42: 6.945 asserzioni,
  28 casi PASS. Include selezione valida, indice obsoleto, sostituzione del
  tipo, cariche mutate, bersaglio fuori portata, rebase e deduplicazione.
- Processo CDDA reale in modalità continuous: 15 controlli PASS.
  Il menu ferma il tempo; una richiesta durante il menu non trasferisce
  gratuitamente l'oggetto. Dopo la chiusura, l'attività raccoglie solo la
  pila scelta; il replay non la duplica.
- Lettura del save con helper linkato al core CDDA originale pin
  `2478ae876eb1439be387d0e117808d33c9d6afa4`: una sola pila con tutte e
  sette le munizioni nell'inventario; il sasso non selezionato rimane a
  terra; nessuna copia delle munizioni rimane sulla mappa.
- Avvio grafico reale su Pop!_OS, finestra Luanti e proiezione CDDA:
  6 controlli PASS, con screenshot e mondo isolato. Dopo l'installazione,
  gli stessi 6 controlli passano anche usando i binari ordinari del progetto
  da `start.sh`, nuovamente con salvataggi isolati.

Comandi principali dalla ricostruzione `artifacts/fnd03-session/workspace`:

```sh
cmake -S cdda -B cdda/build
cmake --build cdda/build --target cdda-server cata_test --parallel 2
cmake --build luanti/build --target luanti --parallel 2
cmake -S protocol -B protocol/build
cmake --build protocol/build --parallel 2
ctest --test-dir protocol/build --output-on-failure
```

Il runner nativo va eseguito dalla directory `workspace/cdda`, con
`--user-dir` assoluto e isolato. `tests/pickup_runtime_test.py` conserva
comandi e controlli riproducibili; la ricevuta di build dell'helper originale
è `native-save-reader-v3.build.json`. I primi tentativi della fixture sono
conservati come superati: usavano impropriamente il vecchio campo charges
dei fiammiferi, che CDDA migra nel contenitore interno al load. La fixture
finale usa autentiche munizioni count-by-charges.

## Confine della verifica

Questa è la chiusura del backend richiesto alla fine della continuazione.
La GUI chest/container e il collegamento del puntamento alla richiesta
PICKUP sono il passo successivo già approvato; non sono dichiarati
implementati. Non serve ripetere i test manuali di RT-02 per validare questo
backend. L'avvio grafico verifica caricamento e integrazione, non completa
la validazione visiva delle pile o dell'interfaccia di raccolta.

Il guard attuale non è un ID persistente dell'istanza: non distingue due
oggetti con lo stesso tipo/cariche ma contenuti o condizioni diversi.
Le scelte native speciali per oggetti problematici o furto devono essere
collegate all'interfaccia prima di dichiarare completa la raccolta di ogni
categoria. Nessun inventario Luanti autorevole è stato introdotto.
