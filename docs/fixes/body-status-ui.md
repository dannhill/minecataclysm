# HUD di sopravvivenza e scheda corporea

Slice essenziale del playable core, indipendente dalla nuova GUI di raccolta.
L'utente il 2026-10-08 autorizza questa prosecuzione autonoma e rinvia il test
della raccolta. Entrambe le [checklist](../validation/pending-manual.md) restano
in attesa: nessuna accettazione manuale è dedotta dai test automatizzati.

## Comportamento

Il pannello in basso a sinistra mostra stamina, salute di testa/torso e i
bisogni segnalati da CDDA. **H** apre una scheda di sola lettura con tutte
le parti principali del corpo, salute e temperatura, oltre a fame, sete,
sonno, dolore percepito, affaticamento, temperatura generale e morale.
I due elenchi scorrono se necessario. **Esc** o **Torna al gioco** chiude.
Il tasto è configurabile con `keymap_cdda_body` (default `KEY_KEY_H`).

La scheda mette in pausa il tempo nativo nella modalità continua e rispetta
la pausa manuale F7 alla chiusura. Nessuna azione CDDA è assegnata per leggere
la scheda; niente cure, equipaggiamento o trasferimenti impliciti. In modalità
scandita dalle azioni non fa avanzare il tempo. Una perdita IPC/reset/resync
chiude la scheda: occorre riaprirla dopo lo stato completo confermato.
Il HUD segnala esplicitamente uno stato non sincronizzato/non disponibile.
I cuori, la barra d'ossigeno e la hotbar del server Luanti locale vengono
esclusi quando il bridge possiede il personaggio: non rappresentano CDDA.

## Origine e conoscenza

`CwmMapExporter::export_avatar_status()` consulta le funzioni native in
`cdda/src/display.cpp` e `output.cpp`. Le barre corporee seguono quelle di
`Character::extended_description()` in `character.cpp`: nessun valore esatto
di HP viene esportato dalla nuova scheda. Il dolore usa la variante Character
di `display::pain_text_color()`, inclusi analgesia e precisione dopo visita
nativa; fame e sete usano le rispettive percezioni, non formule Luanti.
Una descrizione nativa vuota resta vuota nel protocollo; la scheda la mostra
come `-`, spiegandone il significato. Etichette in italiano e valori nella
lingua configurata di CDDA possono coesistere; localizzazione completa rinviata.

CWM **2.6** aggiunge `avatar_status` a ogni pubblicazione, sia completa sia
incrementale. Le stringhe/liste sono limitate e gli ID unici; uno stato
malformato non entra nel renderer. I due runtime devono usare la stessa
versione. Colori nativi tradotti in una palette leggibile di presentazione;
nessuna regola di salute o progressione viene duplicata nel client.

## Confine

È il primo HUD/scheda corporea, non l'intera medicina. Diagramma anatomico
grafico, condizioni/ferite con dettagli clinici, trattamenti espliciti con
oggetti reali, vestiti/impedimenti, nutrienti, bagnato e grafici avanzati
restano nel piano. Non vengono rivelate malattie nascoste o vitamine.
La scheda fotografa l'ultimo stato confermato all'apertura; la pausa nativa
deve essere ricevuta dal coordinator. Non è una fonte autonoma di save.
La grande varietà di anatomie e le risoluzioni molto piccole richiedono
ulteriore validazione visiva. M5.5 resta FAILED; SAVE-001 completo resta aperto.

## Prova manuale

`./body-demo.sh --fresh` usa una copia isolata creata dal core CDDA pinned
originale: ferite a testa/braccio sinistro, sete, stanchezza, stamina ridotta,
nessuna pila a terra o creatura ostile. Movimento continuo 4x.
Senza `--fresh` riprende la stessa sessione, senza cancellare le precedenti.
Il HUD/scheda è disponibile anche in `start.sh` e `pickup-demo.sh`.
Le quattro prove sono nella [checklist congiunta](../validation/pending-manual.md).

## Verifica della consegna

Sorgenti di produzione: `1a40905822300bb04a4abf583d63cadccaa6ae97`.
Patch/inventari completi in `baseline/manifest.json`; riproduzione indipendente
e confronto dei working fork PASS. Compilazione incrementale da sorgenti
ricostruiti con cache mantenute, non una nuova compilazione completa a freddo.
La [ricevuta](body-status-ui-evidence.json) contiene checksum, identità e limiti.
Artefatti: `artifacts/playable-core-body-ui-20261008/`.

- CDDA: **7.049 asserzioni / 32 casi PASS**, filtro `[cwm],[diving],[pickup]`,
  seed 42. Nuova proiezione corporea pura e analgesia comprese.
- Protocollo: **5/5 PASS**, inclusi rifiuto/resync prima dell'ingestione di
  descrizioni mancanti, duplicate, NUL, liste eccessive o parti malformate.
- Luanti finale: **306 test e 648 asserzioni Catch2 PASS**. Comprende escape
  di stringhe native che potrebbero altrimenti inserire elementi nella formspec.
- GUI reale con `start.sh` e binari **installati**: **16/16** in modalità
  ordinaria e **18/18** in continua 4x. Salute concorde con core originale,
  HUD visibile, sheet in pausa, WASD senza effetto in menu, Esc, pausa manuale
  conservata, perdita IPC reale e nuova proiezione completa.
- Due save letti dal core CDDA originale: posizione e salute conservate;
  in modalità ordinaria anche tempo/stamina invariati. Un confronto aggiuntivo
  degli stessi save conferma **HP correnti e massimi esatti di tutte le 12
  parti** invariati, oltre alle barre percepite. È salvato separatamente in
  `additional-native-hp-checks.json`; il test riproducibile ora include
  direttamente questa asserzione, oltre alle 16/18 del giro installato.
- Regressione della raccolta con i nuovi binari: **18/18 PASS**, GUI chest,
  raccolta della pila scelta e del singolo sasso, annullamento dopo reconnect,
  save originale senza duplicati. Questo non sostituisce il test visivo utente.

L'ispezione degli screenshot reali ha portato a un pannello di fondo pieno
e a barre con cinque posizioni (`[|||..]`). La GUI finale è stata ricontrollata
e ritestata dopo questa modifica. Sono conservati anche gli screenshot
del primo giro. Verifica automatizzata circoscritta PASS; **validazione
manuale in attesa**, come esplicitamente richiesto dall'utente.

Il server è compilato al commit `2c1dd1d`: il suo inventario CDDA e tutti gli
input non documentali del protocollo sono identici a quelli di `1a40905`.
Il client finale è compilato da `1a40905`; l'equivalenza e i checksum dei
binari installati sono in `installed-runtime.json`. Il rollback conserva i
due binari CWM 2.5 precedenti, senza modificare salvataggi utente.

## Riproduzione

Il core pristine di riferimento è CDDA `2478ae876eb1439be387d0e117808d33c9d6afa4`.
`tests/takeover_save_reader.cpp --create-body` viene linkato ai suoi object
file, senza exporter/server CWM; comandi, sorgente e SHA del lettore sono in
`native-reader-build-final.json`. La fixture ne conserva `before.json` e il
save nativo. La prima fixture mancava dell'effetto nativo della fame: la
versione finale lo inizializza con `update_stomach(turn,turn)`, senza tempo
trascorso, e conserva il primo tentativo in `fixture-pre-hunger/`.

```sh
python3 tools/refresh_verification_workspace.py --workspace artifacts/fnd03-session/workspace --receipt artifacts/nuova-verifica/refresh.json
cmake --build artifacts/fnd03-session/workspace/cdda/build --target cdda-server cata_test --parallel 2
cmake --build artifacts/fnd03-session/workspace/luanti/build --target luanti --parallel 2
python3 tests/body_status_gui_test.py --workspace artifacts/fnd03-session/workspace --fixture artifacts/playable-core-body-ui-20261008/fixture/user --native-reader artifacts/playable-core-body-ui-20261008/native-save-reader --artifacts artifacts/nuova-verifica/gui-body
```

La directory di output della GUI deve essere nuova. Aggiungi `--action-driven`
per la modalità ordinaria. Serve X11 con xdotool, ImageMagick e Pillow.
Le prove clonano il save e usano configurazioni isolate; un relay trasparente
consente la perdita IPC reale, senza simulazione finta. Nessun codice di
produzione viene riscritto dal test.
