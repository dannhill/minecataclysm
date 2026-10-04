# RT-01 — Primo prototipo dello scheduler in tempo reale

Autorizzazione: «Procedi pure», dopo la validazione del ciclo di vita di
creature/NPC e la proposta del primo passo della fase 2. La scelta finale del
controller resta subordinata al confronto giocabile previsto nel
[piano completo](../../IMPLEMENTATION_PLAN.md).

## Prova locale

```bash
./realtime-demo.sh --fresh
```

La demo copia una fixture canonica in `artifacts/realtime-demo/session-*`.
Rilanciando senza `--fresh` riprende la stessa copia; le copie precedenti sono
conservate. Non usa la partita normale né cambia la sessione di `actor-demo.sh`
con il caso di schermo nero segnalato dall'utente.

- Resta fermo qualche secondo all'inizio: il cane e il compagno eseguono la
  propria AI nativa. Dopo averti raggiunto possono fermarsi normalmente.
- Tieni premuto WASD, poi rilascialo. Confronta 1×, 2× e 4× con F8;
  il ciclo completo è 1 → 2 → 4 → 0,5 → 1. Cambia la velocità del mondo intero.
- F7 mette in pausa/riprende; anche il menu Esc ferma CDDA. Dopo una pausa,
  rilascia e ripremi WASD: il movimento precedente non riparte da solo.
- Dalla partenza, percorri la strada verso destra fino alla piccola stanza
  chiusa con pareti di mattoni. Apri la porta, oppure cammina verso di essa:
  una nuova minaccia percepita attiva l'autopausa. E riconosce e riprende.
  Lo zombie di questa stanza è legato per rendere sicura la prova.
- Scala a gradini davanti alla partenza; scala a pioli subito a destra.
  Spazio sale, Maiusc+Spazio scende, una volta per pressione. Prova anche
  quit/load: posizione, piano e modifiche al mondo rimangono canonici.

**Promemoria richiesto dall'utente:** ora che lo scheduler è giocabile,
rivalutare insieme l'attraversamento automatico e continuo sia delle scale a
gradini sia delle scale a pioli, prima di scegliere il controller definitivo.
Qui sono ancora connessioni native contestuali. L'altro prototipo, con offset
continuo autorevole CDDA, resta da implementare e confrontare.

`start.sh`, `actor-demo.sh` e `vertical-demo.sh` mantengono il comportamento
scandito dalle azioni. L'opt-in tecnico per una sessione normale è
`CDDA_REALTIME=1 ./start.sh`; per il confronto iniziale usare la demo isolata.
I due binari verificati sono installati; anche l’avvio di `realtime-demo.sh`
è verificato sul client grafico reale. L'utente
[accetta la checklist manuale](../source/rt01-validation-2026-10-04.md), ma
giudica il ritmo base 1× troppo lento e chiede chiarimenti sul controller
continuo previsto. Lo scheduler è accettato per questa prova; velocità e
controller finali restano da scegliere.

## Contratto implementato

Un solo coordinatore, nel processo CDDA e sul thread della simulazione, usa
l'orologio monotono per ammettere le fasi native di `do_turn()`. Default:
un secondo reale per secondo simulato. Nessun calendario, costo di azione,
AI o salvataggio autorevole è implementato in Luanti.

Il budget `moves`, la velocità, i debiti delle azioni costose, la generazione
di nuovi punti, gli eventi, il corpo, campi, oggetti, veicoli, creature e NPC
restano nella sequenza nativa. Da fermo il coordinatore esegue l'attesa nativa
al confine del tick. Con un'intenzione mantenuta può chiudere la fase delle
azioni conservando il credito nativo inutilizzato: un attore veloce non viene
ridotto artificialmente a una sola azione per tick.

Il prossimo input viene temporizzato sul costo effettivo `moves` prima/dopo
l'azione e sulla velocità nativa corrente. Un'intenzione mantenuta è una
richiesta idempotente di direzione, non una coda di passi. I passi successivi
sono azioni native interne. I comandi puntuali, comprese le transizioni
verticali, mantengono esiti correlati e deduplicazione. Pausa, decisione,
disconnessione o risincronizzazione scartano l'intenzione; i comandi puntuali
annullati ricevono un esito negativo invece di lasciare il client in attesa.

L'accelerazione è globale, da 0,25× a 4× sul protocollo. Pausa manuale,
menu, minaccia, recupero della connessione e decisione sono motivi distinti,
combinabili: chiudere un menu non annulla una pausa manuale. La ripresa non
recupera il tempo trascorso in pausa. Sospensioni/stalli lunghi perdono tempo
reale invece di generare raffiche di tick arretrati; il delta per campione è
limitato a 250 ms. Non è una garanzia di 1:1 sotto carico arbitrario.

L'autopausa confronta identità native di ostili percepiti tramite `avatar::sees`
e atteggiamenti nativi, anche se SAFEMODE è disabilitato. Non usa il cono della
camera né avvisa per attori non percepiti. E usa anche il riconoscimento nativo
delle minacce. La percezione viene rivalutata ai confini di azione/tick:
questa prova non certifica un'interruzione prima di ogni attacco interno
alla fase AI, né il combattimento completo della fase 2.

La griglia nativa resta autorevole. Luanti interpola fino ai target confermati
con durate pubblicate dal coordinatore; scala le durate senza saltare la
frazione già interpolata e ferma l'interpolazione degli attori e della camera
in pausa. La ricomparsa di attori non percepiti e il recupero completo conservano
il comportamento già verificato: nessuna animazione di un percorso non osservato.

Il calendario viene incrementato nel prelude nativo; la fase del mondo viene
eseguita al confine temporizzato. Gli stati dopo un'azione possono precedere
la fase AI del tick. Misurazioni e HUD sono quindi quantizzati, non descrivono
una simulazione fisica continua né garantiscono un'unica fotografia di fine
turno. `motion_seconds` è una durata di presentazione, non una nuova autorità.

Il salvataggio resta quello CDDA. Velocità del prototipo, intenzione mantenuta
e stato dei tasti/pausa sono volatili: dopo un riavvio la velocità torna a 1×;
una minaccia già presente può essere nuovamente riconosciuta dal nuovo runtime.

## Sorgente e verifica

Implementazione e test sono sul branch `prototype/rt01-scheduler`. Sorgente
verificata e checksum sono nel [registro delle prove](rt01-real-time-evidence.json).
Il workspace `artifacts/fnd03-session/workspace` è una ricostruzione aggiornata
da commit e patch complete, con verifica di tutti i blob/modi. Le build sono
**incrementali con cache conservate**, non build pulite. Una verifica separata
riproduce le patch sui file pinned originali e confronta gli altri blob.

Ambiente: Pop!_OS 22.04 LTS, GCC 11.4.0, FlatBuffers 24.3.25, display `:1`.
La scena grafica RT-01 osserva una mediana di circa 59,7 FPS su 1.591 frame
con limite 60; non è una certificazione sotto carico arbitrario.

Copertura mirata:

- Protocollo: cinque programmi CTest, inclusi orologio deterministico e
  risincronizzazione per velocità/durate non finite o maschere sconosciute.
- CDDA: 20 casi e 6.710 asserzioni `[cwm],[diving]`; il nuovo caso verifica
  conservazione del credito e isolamento dell'hook di confine turno.
- Luanti: 304 controlli in 47 moduli, più 648 asserzioni in quattro casi.
- Server nativo: 78 controlli registrati, idle 1:1, AI senza input, accelerazione, pause combinate,
  input annullato, replay, disconnessione, full-state non confermato,
  scale e pioli, autopausa, decisione d'acqua e riavvio canonico.
- Client grafico effettivo tramite `start.sh`: 20 controlli, idle/AI, pacing a 2×,
  assenza di raffiche, rilascio, F7/F8/E, menu, autopausa, mesh e salvataggio.
- Regressioni della modalità scandita dalle azioni: 363 controlli fra sessioni, multi-Z/acqua,
  identità/offload/salvataggi, ciclo di vita delle mesh, trasporto avverso e
  movimento/camera a diversi limiti FPS.

Le prove copiano fixture e configurazioni in directory nuove. Il lettore
canonico è collegato al core CDDA pristine pinned; i fork di produzione non
creano la fixture né interpretano la prova di compatibilità.
I tentativi iniziali restano negli artifact: corretti accessor del binding,
barriera ACK del replay, coordinate intere, enum OPEN e prefisso del nome
visualizzato. L'avvicinamento alla porta nel test usa un'azione puntuale per
l'ultima casella: tenere la direzione può già aprirla automaticamente.
Il primo smoke del launcher cercava una vecchia stringa di log: corretto
per il messaggio di installazione attuale e ripetuto, con ispezione delle
schermate attivo/pausa. Quei tentativi non sono conteggiati come prove complete riuscite.

Comandi riproducibili, usando directory output nuove:

```bash
python3 tools/takeover_baseline.py check
python3 tools/verify_captured_sources.py --workspace <workspace> --receipt <output>/sources.json
cmake --build <workspace>/protocol/build --parallel 2
ctest --test-dir <workspace>/protocol/build --output-on-failure
cmake --build <workspace>/cdda/build --target cdda-server cata_test --parallel 2
cmake --build <workspace>/luanti/build --target luanti --parallel 2
python3 tools/build_native_save_reader.py --pristine-cdda <core-pristine-compilato> \
  --workspace <workspace> --output <output>/native-save-reader --strip-debug
<output>/native-save-reader --create-realtime --userdir <fixture-rt> \
  --datadir <workspace>/cdda/data --output <output>/demo-fixture-baseline.json
<output>/native-save-reader --create-exploration --userdir <fixture-acqua> \
  --datadir <workspace>/cdda/data --output <output>/water-baseline.json
python3 <workspace>/tests/realtime_runtime_test.py --workspace <workspace> \
  --fixture <fixture-rt> --decision-fixture <fixture-acqua> \
  --native-reader <output>/native-save-reader --artifacts <output>/native
DISPLAY=:1 python3 <workspace>/tests/realtime_gui_test.py --workspace <workspace> \
  --fixture <fixture-rt> --native-reader <output>/native-save-reader --artifacts <output>/gui
```

RT-01 non chiude tutta la fase 2, FND-04, FND-05 o M5.5. Restano controller
continuo, posture/orientamento/animazioni, combattimento e attività completi,
percezione/luce/nebbia/panorama, UI di inventario/crafting/NPC e le rispettive
prove del piano. La presentazione dei veicoli e l'avatar ausiliario Luanti
restano debito dei loro task. Porte invertite, perni e schermo nero fuori dalla
demo precedente non sono dichiarati corretti da questo prototipo.
