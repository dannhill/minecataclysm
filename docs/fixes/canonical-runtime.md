# FND-01 — Avvio, caricamento e ciclo nativo

Implementazione completata con verifica mirata PASS. Il gate M5.5 storico
rimane FAILED; questa riparazione non certifica SAVE-001 completo, protocollo,
proiezione di tutte le entità o tutte le interazioni.

Sorgenti verificati: commit `f3cea9c8502a0caac938a9b4047540e4a2a31b02`,
branch `fix/canonical-runtime`. Comandi, identità, hash e risultati sono in
[canonical-runtime-evidence.json](canonical-runtime-evidence.json).

## Comportamento

Un mondo esistente carica il personaggio salvato attraverso `game::setup()` e
`game::load(save_t)`. Conserva identità, inventario, coordinate, calendario e
stato canonico del mondo. Se ci sono più salvataggi, richiede una selezione
esplicita; non crea silenziosamente un altro Survivor. Una nuova partita usa
`avatar::create()` e `game::start_game()`, senza impostare artificialmente l'ora.
La creazione esplicita controlla che l'identificatore non esista già.

I nuovi mondi leggono il preset `dev:default` dal file CDDA nativo e filtrano
gli ID non disponibili come fa il gestore nativo delle mod. Sul pin corrente:
`dda`, `no_npc_food`, `personal_portal_storms`, `no_fungal_growth`. Il riferimento
obsoleto `No_Rail_Stations` viene scartato. Un preset personale dello standalone
non sostituisce quello approvato per il prodotto; i mondi esistenti conservano
le proprie mod e opzioni.

Il runtime pubblica prima lo stato caricato e attende un'azione ammessa prima
del bootstrap della simulazione. Questo conserva l'ora iniziale anche quando
il personaggio salvato ha zero punti movimento o un debito residuo. Handshake
e richieste non supportate non avviano quel bootstrap.

Successivamente usa il ciclo esterno nativo. `do_turn_with_action()` fornisce
le intenzioni nello stesso punto in cui `do_turn()` chiama `handle_action()`;
condivide il resto dell'implementazione, senza copiarne le fasi. L'override
dell'input è locale alla chiamata e viene ripristinato anche dopo eccezioni.
Il thread autorevole esegue eventi temporizzati, missioni, corpo, meteo,
attività, cadute, veicoli, campi, oggetti, esplosioni, suoni, IA e NPC secondo
l'ordine nativo. I turni necessari a pagare il debito di un'azione continuano
anche senza un nuovo comando.

Lo stato dopo il preambolo viene pubblicato prima di attendere l'input. Gli
esiti arrivano dopo gli aggiornamenti nativi pertinenti: prima di un'eventuale
seconda azione nello stesso turno, oppure dopo la coda completa del turno.
Non si fa avanzare un nuovo turno per una richiesta rifiutata mentre il
runtime è in attesa dell'input. La simulazione dovuta ad azioni già ammesse,
attività o debito salvato può comunque produrre minacce che bloccano un'intenzione.

WAIT usa `avatar::pause()`; movimento e apertura automatica delle porte usano
`avatar_action::move()`. OPEN/CLOSE sono limitati ai bersagli adiacenti e ai
metodi nativi per le porte di terreno. Le altre interazioni restano incomplete.
Sono rimossi lo zombie generato dall'handshake e il fuoco sintetico di USE.

La modalità sicura resta attiva. Il client presenta il blocco nativo e permette
di riconoscere la minaccia con Aux1, predefinito E e riassegnabile nelle opzioni
Luanti. Una pressione prolungata non riconosce automaticamente minacce nuove.
L'azione condivide la logica nativa IGNORE_ENEMY, non costa movimento o tempo e
non disabilita safe mode. Il protocollo aggiunge un flag di stato e una richiesta
semantica; il minor 1 non attesta conformità completa alla specifica v1.1.

SIGINT/SIGTERM salvano prima del cleanup nativo che svuota i buffer delle mappe.
Il main evita un secondo salvataggio dopo il cleanup. Il lifecycle completo
di morte, le decisioni native bloccanti e la loro GUI rimangono in FND-04/M7.

## Verifica

Tutti i mondi/configurazioni/socket delle prove sono isolati. Non sono stati
usati i salvataggi reali dell'utente. I binari verificati sono installati nelle
posizioni utilizzate da `start.sh`.

| Prova | Esito |
|---|---|
| CDDA nativo: catalogo/proiezione, corpo/campi/IA, debito, safe mode, attività | 7 casi, 3.376 asserzioni PASS |
| Caricamento, azioni, save/restart, selezione personaggi e preset | 40 controlli PASS |
| Luanti reale → CDDA → lettore nativo indipendente | 11 controlli PASS |
| Launcher e mondo reale isolato, inclusa stabilità della camera | 8 controlli PASS |
| Regressioni grafiche/input a diversi limiti FPS e risposta ritardata | 48 controlli PASS |
| Luanti nativo sul binario finale | 303/303 PASS |
| Protocollo, build Debug ricostruita | 2/2 PASS |

Il lettore indipendente è collegato al core upstream pinned del precedente
audit, senza oggetti del fork di produzione. Il nuovo flag test-only `--resave`
permette un controllo nativo load/save/load. Il riavvio del runtime concorda con
quel controllo per ora, posizione, terreno/arredi, mostri, NPC e veicoli.
NPC `on_load()` esegue aggiornamenti fisiologici differiti: compararli al JSON
prima del caricamento impone un'aspettativa errata. Il comportamento del pin,
incluse le sue peculiarità nel bookkeeping di `last_updated`, non è stato
modificato per far passare le prove.

I gruppi di mostri possono comparire durante il preambolo nativo. La prova
dell'handshake confronta due handshake sullo stesso stato; il salvataggio
confronta i mostri con l'ultimo stato autorevole. La prova degli NPC verifica
la persistenza nativa: l'exporter CWM non li presenta ancora.

La build CDDA usa oggetti del precedente audit soltanto quando dipendenze di
progetto e flag coincidono; ricompila i file e le dipendenze cambiati. Il receipt
registra 590 oggetti riutilizzati e 5 esclusi al primo passaggio. Si tratta di
una build incrementale verificata, non di una certificazione cold-cache.
Una ricostruzione finale separata verifica tutte le sorgenti contro l'inventario.

## Uso e limiti

`./start.sh` riprende l'unico personaggio presente. Con più personaggi:

```sh
CDDA_CHARACTER='<ID mostrato dal server>' ./start.sh
```

Il backend offre `--character`, `--new-character` e `--headless-ticks 0` per
selezione, creazione esplicita e caricamento/salvataggio senza turni.

Lo scheduler attuale è ancora comandato dalle azioni. Tempo reale 1:1, pausa
globale/menu, attività accelerate e confronto dei due prototipi di movimento
restano nella fase 2 del piano approvato. Non viene scelta la variante continua.

Restano FND-02/03 per framing, backpressure, versioni/sessioni, deduplicazione,
reconnect/resync; FND-04 per entità, percezione/HUD, interazioni e lifecycle;
FND-05 per SAVE-001 esteso, performance e certificazione. Il prossimo task
prioritario è FND-02. Le vecchie evidenze di conformance fallita sono conservate.
