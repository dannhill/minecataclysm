# Oggetti a terra: puntamento e GUI Mineclonia

Aggiornamento successivo 2026-10-08: l'utente valida tutti i quattro punti
della checklist di questa fetta. I riferimenti a prove pending/rinviate sotto
conservano il contesto della consegna originale. I nuovi comandi/HUD sono in
[controlli e presentazione](controls-and-survival-presentation.md).


Segue il [backend PICKUP](ground-items-pickup.md) e le direttive della
[continuazione recuperata](../source/continuation-2026-10-07.md).
Sorgenti della consegna: `5b8c5b44ae9d6851b8f425152832eed4c944a1b9`.
Patch complete e inventari dei fork sono in `baseline/manifest.json`.
Verifica automatizzata circoscritta PASS e binari installati il 2026-10-08.
La validazione visiva dell'utente resta da ottenere. M5.5 resta FAILED;
questa verifica riguarda soltanto la raccolta e la sua presentazione.

## Comportamento implementato

Guarda un oggetto a terra entro la portata nativa, sullo stesso piano:
il tasto destro raccoglie un singolo oggetto; una pila apre la GUI della
chest Mineclonia. Non viene effettuata raccolta automatica. Il raggio si
ferma alla prima superficie puntata, evitando selezioni attraverso i muri.
Maiusc + tasto destro conserva la chiusura di porte/finestre.

La GUI riprende dimensioni, spaziatura, slot e media della chest:
27 slot sopra e 36 sotto. Il pannello superiore mostra il tile CDDA;
quello inferiore mostra gli oggetti posseduti, indossati, impugnati e annidati
nei contenitori. I pannelli hanno pagine aggiuntive quando necessario.
Il nome e le cariche effettive sono nel tooltip; le icone non ancora mappate
usano il fallback. I nove batch di mapping restano un'attività indipendente.
Provenienza/checksum dei quattro media della GUI sono in
`game/mods/cdda_items/container_assets.json`, con le attribuzioni conservate.

Nella modalità continua, aprire la GUI mette in pausa la simulazione.
Esc chiude senza raccogliere. Trascinare uno slot superiore in quello
inferiore seleziona **l'intera pila nativa**, chiude la GUI e riprende il tempo
per pagare l'attività CDDA. La pausa manuale F7 rimane rispettata: una raccolta
selezionata aspetta la ripresa. La selezione conserva il bersaglio assoluto
e il guard originale; il server verifica nuovamente indice, tipo, cariche,
count-by-charges e portata. Un ACK positivo assegna l'attività e non garantisce
che un oggetto sia già nell'inventario.

Gli inventari della formspec sono specchi locali di sola presentazione.
Il client intercetta il trascinamento prima dell'invio al server Luanti
e prima della sua applicazione ottimistica. La GUI non può spostare,
consumare o duplicare autonomamente gli oggetti. Disconnect/reset/resync
chiudono il pannello e annullano selezioni non ancora inviate.
CWM passa a **2.5** per la proiezione `owned_items`; i due runtime vanno
ricompilati insieme. Il save rimane quello nativo CDDA.

Le scelte sul furto conservano le politiche native Yes/Always/Never/No.
Per un secchio pieno è disponibile la scelta nativa di impugnarlo, compresa
la disposizione dell'oggetto già in mano. L'annullamento è l'ultima scelta
nei menu esterni: il provider CWM lo usa se perde la connessione, senza
impugnare, gettare oggetti o ricordare una preferenza di furto automaticamente.
Il versamento non viene proposto: entra nel selettore nativo dei liquidi,
che deve ancora ricevere la propria interfaccia esterna.

## Confine del prototipo

Il pannello inferiore è una vista appiattita di sola lettura: non è ancora
l'interfaccia completa per indossare, togliere, gettare, riorganizzare tasche
o contenitori. Ogni raccolta seleziona una sola pila intera e chiude la GUI;
quantità parziali e raccolta multipla appartengono alla successiva interfaccia.
Il guard non identifica univocamente due istanze con tipo/cariche uguali
ma condizioni o contenuti differenti: il limite del backend è conservato.
Il feedback delle attività che non riescono per capacità e altri motivi nativi
va completato con il futuro canale dei messaggi CDDA; l'ACK non è una ricevuta
di trasferimento. I test di questa fase non certificano ogni categoria di item.

La proiezione dei possedimenti viene esportata interamente a ogni stato;
la fixture è piccola. Non è una misura delle prestazioni di un inventario enorme.
Le pagine sono implementate ma non ancora validate manualmente su una grande pila.
Le icone della fixture per sasso/munizioni/zaino sono ancora generiche.
Nessuna nuova immagine o mappatura AI è stata generata.

## Prova manuale

Dalla directory del progetto:

```sh
./pickup-demo.sh --fresh
```

La prova usa una copia isolata della fixture nativa e movimento continuo 4x.
Guarda in basso, subito davanti alla partenza: ci sono un sasso e 7 munizioni
9mm. I tuoi salvataggi ordinari non vengono aperti. Senza `--fresh` riprendi
l'ultima prova; `--fresh` ne crea un'altra senza cancellare quelle precedenti.

1. Apri la pila col tasto destro; controlla layout e tooltip delle munizioni.
   Attendi qualche secondo: il tempo deve rimanere fermo. Esc non raccoglie nulla.
2. Riapri e trascina le munizioni dal pannello superiore a uno slot inferiore
   vuoto. La GUI si chiude e il tempo riprende; a terra deve restare il sasso.
3. Chiudi il gioco e rilancia `./pickup-demo.sh`: deve rimanere soltanto il sasso.
   Raccoglilo direttamente col tasto destro: nessuna GUI e nessun oggetto residuo.
4. Esci e rientra ancora: gli oggetti raccolti non devono ricomparire.

La validazione visiva dell'utente è ancora da ottenere, esplicitamente
rinviata il 2026-10-08. La [checklist persistente](../validation/pending-manual.md)
sarà riproposta insieme al prossimo HUD/scheda corporea indipendente dalla
raccolta. L'inventario/equipaggiamento interattivo viene dopo; non serve
ripetere la validazione RT-02 già accettata.

## Evidenze della consegna

La [ricevuta completa](ground-items-ui-evidence.json) identifica sorgenti,
binari, ambiente, checksum dei log/screenshot e limiti della verifica.

- Replay indipendente delle patch e ricostruzione incrementale: PASS.
- Protocollo: 5/5 PASS, incluse selezioni semanticamente invalide.
- CDDA: 7.032 asserzioni in 31 casi PASS, filtro `[cwm],[diving],[pickup]`,
  seed 42. Include raccolta/rivalidazione/dedup, possedimenti annidati,
  politiche di furto, secchio pieno e annullamento dei menu con peer perso.
- Luanti: 305 test e 648 asserzioni Catch2 PASS.
- Avvio grafico reale con i binari installati e `start.sh`: **15/15 PASS**
  in modalità ordinaria e **18/18 PASS** in modalità continua 4x.
- Nella casella selezionata: due oggetti prima, solo il sasso dopo il
  trasferimento delle munizioni, zero dopo la raccolta diretta. Il test
  controlla sia la proiezione semantica sia i nodi effettivi della scena.
- Il lettore linkato al core CDDA originale verifica entrambi i save:
  una pila con tutte e sette le munizioni e il sasso nei possedimenti,
  senza duplicati a terra.
- Perdita dell'IPC mentre una selezione aspetta la ripresa dalla pausa
  manuale: la selezione si annulla, la GUI resta chiusa e non viene
  eseguita automaticamente dopo la riconnessione.

Il primo tentativo nella modalità ordinaria usava il conteggio globale
degli oggetti come se la percezione del mondo fosse immutabile. Il primo
turno aggiorna legittimamente anche altri tile: l'asserzione è stata
sostituita con controlli sulla casella selezionata, incluso il type ID
rimasto e i suoi nodi renderizzati. Il tentativo fallito è conservato.

Il client finale aggiunge soltanto telemetria rispetto al primo giro di
verifica installato. Il server CDDA è il medesimo binario verificato al
commit `2931190c32d3465be735f804843339f458075128`: gli inventari dei sorgenti
CDDA e tutti gli input non documentali del protocollo sono identici alla
consegna finale; l'equivalenza è registrata nella ricevuta d'installazione.
I due binari precedenti sono conservati nel rollback degli artefatti.

## Riproduzione della verifica

Artefatti: `artifacts/playable-core-item-ui-20261008/`.
La ricostruzione incrementale conserva le cache di build e controlla ogni
file/mode dei fork e del repository radice. Il replay delle patch è indipendente.
Non è stata eseguita una nuova build completamente da zero.

Dalla ricostruzione `artifacts/fnd03-session/workspace`:

```sh
cmake --build cdda/build --target cdda-server cata_test --parallel 2
cmake --build luanti/build --target luanti --parallel 2
ctest --test-dir protocol/build --output-on-failure
```

Il test CDDA va avviato dalla sottodirectory `cdda`, usando un nuovo percorso
assoluto per `--user-dir`:

```sh
build/tests/cata_test '[cwm],[diving],[pickup]' --rng-seed 42 --user-dir=/absolute/isolated-user
```

La fixture è prodotta da `tests/takeover_save_reader.cpp`, già compilato contro
il core originale pin `2478ae876eb1439be387d0e117808d33c9d6afa4`:

```sh
artifacts/playable-core-pickup-20261007/native-save-reader-v3 \
  --userdir artifacts/playable-core-item-ui-20261008/fixture/user \
  --datadir cdda/data \
  --output artifacts/playable-core-item-ui-20261008/fixture/before.json --create-pickup
```

Per la prova grafica, usare directory di artefatti nuove e percorsi assoluti:

```sh
python3 tests/pickup_gui_test.py --workspace /absolute/reconstructed-workspace \
  --fixture /absolute/fixture/user --native-reader /absolute/native-save-reader-v3 \
  --artifacts /absolute/new-gui-artifacts
```

Aggiungere `--action-driven` per verificare anche la modalità ordinaria.
Il test usa davvero `start.sh`, la finestra Luanti, mouse/trascinamento e save
nativo. Un relay locale trasparente interrompe l'IPC per la prova della selezione
in attesa; non simula CDDA. Screenshot e trace vengono conservati.
Richiede X11, xdotool, ImageMagick e Pillow. Su questo desktop DISPLAY è `:1`.

## Gemini come assistente secondario

`agy` elenca `gemini-3.8-flash-high`. È stato tentato un esame circoscritto
in modalità plan, con `--dangerously-skip-permissions`, sui soli file copiati
in `artifacts/playable-core-item-ui-20261008/gemini-review/`.
Il comando è andato in timeout dopo 120 secondi senza produrre un rapporto
utilizzabile. Prompt e log sono conservati; nessuna sua conclusione è stata
usata come evidenza o per implementare le modifiche. Il controllo dei sorgenti
è stato effettuato direttamente.
