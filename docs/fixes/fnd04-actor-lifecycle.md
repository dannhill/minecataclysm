# FND-04 — Identità e ciclo di vita di creature/NPC

Passo circoscritto autorizzato dopo la
[validazione delle connessioni verticali](../source/vertical-validation-2026-10-04.md).
Sorgenti di accettazione `cedb871`, branch `fix/fnd04-actor-lifecycle`.
Variante diurna della demo in `124702d`, senza ulteriori modifiche ai sorgenti
di produzione.
Evidenze, checksum e comandi nel
[registro strutturato](fnd04-actor-lifecycle-evidence.json).
FND-04 completo, SAVE-001 e il gate M5.5 non sono certificati da questo passo.

## Correzione

Prima, l'identità dei mostri apparteneva alla cache di proiezione e cambiava
al riavvio o quando l'oggetto nativo era scaricato e ricostruito. Ora appartiene
alla creatura nativa: `values.cwm_monster_id` conserva un identificativo allocato
dal contatore canonico condiviso di personaggi/NPC. Il wire usa un namespace
distinto da NPC e player; non invia indirizzi di processo.

Il core pinned già legge e riscrive `Creature::values`: nessuna modifica del
formato o dei serializer di salvataggio. Il primo export di una creatura legacy
inizializza il metadato e avanza il contatore delle identità. Non consuma RNG,
tempo o mosse, né cambia HP o AI. Il contatore conserva il limite nativo di un
intero positivo. Una copia simultanea con metadato duplicato riceve un nuovo ID;
il primo attore nell'elenco nativo conserva quello precedente. Non si inferisce
identità da tipo, nome o posizione. NPC e avatar mantengono i loro ID canonici.

Il client usa l'elenco autorevole completo per creare/aggiornare/rimuovere le
entità. Alla perdita di percezione o connessione le mesh diventano invisibili.
Alla nuova percezione e dopo uno snapshot di recupero la posizione è quella
appena confermata: nessuna animazione del tragitto non osservato. Il movimento
percepito ordinario e il rebase del terreno mantengono l'interpolazione.
L'evoluzione del tipo sostituisce la mesh conservando l'identità. Il protocollo
rifiuta kind illegali/incoerenti, rotazioni non finite e metadati di spawn/rimozione
duplicati o contraddittori prima di modificare la scena. Limiti e lookup indicizzato
contengono il lavoro di validazione; il roster resta la fonte di verità.

La diagnostica facoltativa `cwm_entity_trace_file` registra ogni frame: ID,
percezione, posizione visuale/autorevole, generazione del nodo e visibilità.
Conta anche i nodi effettivamente presenti nella scena Irrlicht, per verificare
rimozioni e assenza di mesh residue. È disabilitata nel gioco normale.

## Prova manuale

```bash
./actor-demo.sh
```

La demo copia una variante all'aperto in luce diurna nativa, creata dal core
pinned indipendente con `--create-actor-demo`, sotto
`artifacts/actor-demo/session-*`; rilanciarla riprende il salvataggio.
`--fresh` crea un'altra copia conservando la precedente. Non usa mondi o
configurazioni della partita normale.

I tre attori della prova sono zombie/cane verso nord-est e NPC verso sud:
sono innocui e immobili per questa fixture. La variante coperta dei test
automatici resta separata ed esercita anche la percezione limitata dalla luce.
Possono comparire altri animali provenienti
dagli spawn statici nativi: densità zero non elimina tutti gli spawn già generati.
La scena serve a verificare sincronizzazione, non animazioni o qualità dei modelli.

1. Avvicinati ai tre attori, sali sulla scala a nord e torna giù: niente copie,
   mesh rimaste sul piano sbagliato o spostamenti anomali delle creature.
2. Percorri circa 80 caselle nel corridoio verso est e torna: ritrova i tre
   attori coerenti dopo l'uscita e il rientro nell'area simulata.
3. Esci vicino agli attori e rilancia la demo: posizione e presenze coerenti,
   senza duplicati. Le correzioni sono disponibili anche in `./start.sh`.

L'utente [accetta tutti e tre i controlli](../source/actor-lifecycle-validation-2026-10-04.md).
Non occorre ripetere la checklist. Il nuovo schermo nero fuori dal percorso
della demo è registrato separatamente, resta da riprodurre e non è attestato
come risolto; conservare la sessione per l'eventuale investigazione.

## Verifica e riproduzione

Workspace verificato: `artifacts/fnd03-session/workspace`, aggiornato dai
commit e dalle patch/inventari completi, conservando le cache. Sono build
incrementali; non si attesta una nuova build da cache vuota. Il controllo
indipendente riproduce le patch dai commit upstream pinned e confronta tutti
i file. I runtime della consegna precedente sono conservati e verificati in
`artifacts/fnd04-actors/*-vertical-rollback.gz`.

Verifiche mirate:

- CDDA: 19 casi, 6701 asserzioni `[cwm],[diving]`, inclusi serializzazione,
  copia simultanea, movimento, cambio Z, evoluzione, morte/rimozione e NPC.
- Protocollo: quattro eseguibili; backend in memoria e controlli avversi sul
  ciclo di vita, alias di tipo e resync.
- Luanti: 304 test in 47 moduli e 648 asserzioni in quattro casi Catch.
- Runtime nativo: 186 controlli, viaggio di 80 caselle in entrambe le direzioni,
  offload/reload effettivo, connessione nuova nello stesso runtime, riavvii e
  lettura/riscrittura con core pristine. Verifica anche la coerenza dei metadati
  incrementali; gli snapshot completi sostituiscono il roster senza richiedere
  eventi di spawn/rimozione ridondanti.
- Renderer reale con peer controllato: 17 controlli sui nodi effettivi,
  interpolazione, percezione, rebase, cambio modello, resync e reconnect.
  Il peer è sintetico; non certifica la semantica della simulazione.
- Prodotto combinato via `start.sh`: 15 controlli su mesh dell'NPC percepito,
  roundtrip verticale, riavvio, rispetto della percezione e salvataggio letto
  dal core pristine; gli attori della fixture sono distinti dagli animali nativi.
  La variante diurna ha una prova combinata separata.
- Regressione verticale nativa: 70 controlli; sessione nativa: 21 controlli;
  trasporto avverso nel renderer reale: 21 controlli.
- Movimento/camera: 48 controlli a limiti di 30/60/120 FPS e risposta ritardata;
  il limite di 120 non equivale a throughput osservato di 120 FPS.
- Variante diurna: altri 15 controlli combinati e 8 controlli sul launcher
  installato, con ispezione visiva della scena e lettura canonica del salvataggio.
  I binari verificati sono installati per `start.sh` e `actor-demo.sh`;
  checksum, rollback e smoke test sono nel registro strutturato.

```bash
python3 tools/takeover_baseline.py check
python3 tools/verify_captured_sources.py --workspace <workspace> --receipt <output>/sources.json
cmake --build <workspace>/cdda/build --target cdda-server cata_test --parallel 2
cmake --build <workspace>/luanti/build --target luanti --parallel 2
python3 tools/build_native_save_reader.py --pristine-cdda <core-pristine-compilato> \
  --workspace <workspace> --output <output>/native-save-reader --strip-debug
<output>/native-save-reader --create-actors --userdir <nuova-fixture> \
  --datadir <workspace>/cdda/data --output <output>/fixture-baseline.json
python3 <workspace>/tests/actor_runtime_test.py --workspace <workspace> \
  --fixture <nuova-fixture> --native-reader <output>/native-save-reader --artifacts <output>/native
DISPLAY=:1 python3 <workspace>/tests/actor_gui_test.py --workspace <workspace> --artifacts <output>/gui
DISPLAY=:1 python3 <workspace>/tests/actor_native_gui_test.py --workspace <workspace> \
  --fixture <nuova-fixture> --native-reader <output>/native-save-reader --artifacts <output>/native-gui
<output>/native-save-reader --create-actor-demo --userdir <nuova-fixture-demo> \
  --datadir <workspace>/cdda/data --output <output>/demo-fixture-baseline.json
```

Non rigenerare fixture o test sopra salvataggi esistenti. I tentativi iniziali
restano negli artifact: API JSON del test corretta, spawn statici distinti dagli
attori bersaglio, raccolta della diagnostica spostata sul callback di ogni frame,
metadati incrementali distinti dai roster completi. Non sono attestati come PASS.

## Limiti e seguito

Restano da implementare animazioni/orientamento completi, scheduler in tempo
reale, luce locale/percezione leggibile, campi/HUD e gli altri criteri FND-04.
I veicoli usano ancora ID da indirizzi di processo e restano nel loro task.
Il roster trasmette tuttora anche attori non percepiti, che il renderer nasconde;
questo passo non introduce un nuovo filtro informativo del wire. Non certifica
il bestiario completo, revival/cadaveri, dialoghi/scambi o il threading globale.
Il server Luanti segnala ancora correzioni del proprio avatar ausiliario
(`moved too fast`); i controlli CWM di coordinate e camera passano. La rimozione
del controller ausiliario resta nel lavoro sul controller della fase 2.
Le porte invertite e i perni delle ante doppie restano segnalazioni a bassa priorità.

Il passo prepara il prototipo di tempo reale della fase 2. Alla sua prima prova
giocabile, ricordare all'utente di rivalutare l'attraversamento continuo/automatico
di scale a gradini e a pioli, come già richiesto. La scelta del controller resta
subordinata al confronto giocabile.
