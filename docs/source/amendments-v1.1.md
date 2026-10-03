Ho letto il piano e ti chiedo di emendarlo includendo le seguenti modifiche: "```markdown
# CDDA–Mineclonia Integration
## Architectural Plan Amendments — v1.1

Questo documento elenca esclusivamente le modifiche da applicare
all'Implementation Plan v1.0. Non sostituisce la specifica principale:
la integra e ne corregge i punti emersi durante la revisione architetturale.

---

# 1. PROCESS B — Luanti Presentation Runtime

## 1.1 Nuova definizione

PROCESS B deve essere descritto come:

    LUANTI PRESENTATION PROCESS

e non semplicemente come "Luanti Client".

Il processo può contenere il runtime Luanti necessario a caricare
`cdda_voxel`, registrare contenuti e fornire il normale ambiente client/server
interno di Luanti.

La distinzione fondamentale è:

    Luanti runtime
        ≠
    gameplay authority

CDDA rimane l'unica autorità sul gameplay.

## 1.2 Struttura logica

    PROCESS B
    ┌─────────────────────────────────────────┐
    │ Luanti Presentation Process             │
    │                                         │
    │  Local Luanti game/content environment  │
    │    - cdda_voxel                         │
    │    - node definitions                   │
    │    - visual entities                    │
    │    - Mineclonia selected content        │
    │    - NO gameplay authority              │
    │                                         │
    │  C++ CWM Bridge                         │
    │    - protocol client                    │
    │    - snapshot/delta ingestion           │
    │    - entity synchronization             │
    │    - input capture                      │
    │                                         │
    │  Luanti Client                          │
    │    - ClientMap                          │
    │    - mesh pipeline                      │
    │    - rendering                          │
    │    - camera                              │
    │    - visual entities                    │
    └─────────────────────────────────────────┘

Le normali mod Lua non devono essere assunte come principale meccanismo
di IPC o rendering client-side.

Il percorso IPC critico deve essere implementato nel C++ engine bridge.

---

# 2. Coordinator vs Launcher

Il piano deve distinguere due concetti.

## 2.1 CWM Integration Coordinator

Componente logico responsabile di:

- conversione CDDA → CWM;
- conversione input → CDDA commands;
- gestione delle revisioni;
- batching degli eventi;
- protocollo;
- resync.

Il Coordinator può risiedere nel processo CDDA.

## 2.2 Launcher

Processo/programa separato opzionale responsabile di:

- avvio CDDA;
- avvio Luanti;
- configurazione;
- shutdown;
- lifecycle supervision;
- raccolta exit status.

Il Launcher NON deve essere parte del runtime CWM.

Struttura consigliata:

    cdda/
        src/cwm/

    luanti/
        src/cdda/

    protocol/

    launcher/
        launcher_main.cpp

---

# 3. Transport Abstraction

Il protocollo CWM non deve conoscere il tipo di trasporto.

Definire:

    CwmTransport

con implementazioni:

    LocalTransport
        POSIX:
            Unix Domain Socket

        Windows:
            loopback TCP
            oppure Named Pipe come implementazione futura

    NetworkTransport
        TCP / eventuale QUIC futuro

Single-player iniziale:

    LocalTransport

Multiplayer futuro:

    NetworkTransport

Il protocollo CWM deve rimanere identico indipendentemente dal transport.

---

# 4. Multiplayer-readiness

Il progetto resta single-player nella prima implementazione, ma il protocollo
deve evitare assunzioni strutturali che impediscano un futuro multiplayer.

## 4.1 Session identity

Ogni connessione deve essere concettualmente associabile a:

    session_id
    player_id
    connection_id

Anche in single-player:

    session_id = 1
    player_id = 1

## 4.2 Input ownership

Ogni comando client deve poter identificare il proprio autore.

Esempio:

    MoveRequest {
        session_id
        command_id
        direction
    }

## 4.3 Server authority

In un futuro multiplayer:

    CDDA Server
        |
        +-- Player 1
        +-- Player 2
        +-- Player N

Ogni Luanti client è esclusivamente una presentation endpoint.

NON creare una seconda gameplay authority in Luanti.

## 4.4 Per-client state projection

Il server deve poter, in futuro, inviare ad ogni client soltanto la porzione
di stato necessaria.

L'attuale single-player può continuare a inviare l'intera projection.

---

# 5. CWM Protocol — State Synchronization Model

Il protocollo deve essere denominato:

    CWM State Synchronization Protocol

e non semplicemente "RPC protocol".

Il protocollo contiene:

- snapshots;
- deltas;
- events;
- commands;
- acknowledgements;
- heartbeats;
- resynchronization messages.

---

# 6. Protocol Framing

FlatBuffers definisce il payload ma non il framing dello stream.

Ogni messaggio sul transport deve essere:

    [uint32 payload_size]
    [FlatBuffer payload]

Regole:

- integer encoding documentato;
- payload size validato prima dell'allocazione;
- maximum payload size configurabile;
- FlatBuffer verificato prima dell'accesso ai campi;
- messaggi troncati rifiutati;
- payload oltre il limite rifiutati.

Questo requisito è obbligatorio per il fuzzing.

---

# 7. Connection State Machine

Il protocollo deve formalizzare:

    DISCONNECTED
        ↓
    CONNECTING
        ↓
    HELLO_SENT
        ↓
    ACCEPTED
        ↓
    SYNCING
        ↓
    RUNNING
        ↓
    RESYNCING
        ↓
    RUNNING

Errore:

    RUNNING
        ↓
    CONNECTION_LOST
        ↓
    RECONNECTING

Il client non deve tentare di ricostruire lo stato mediante delta incompleti.

Dopo una perdita di sincronizzazione:

    HELLO
      ↓
    WORLD_SNAPSHOT
      ↓
    RUNNING

---

# 8. Snapshot vs Delta

Formalizzare la differenza.

## 8.1 Snapshot

Usato per:

- connessione iniziale;
- reconnect;
- resynchronization;
- world reset;
- grandi cambiamenti di area.

Tipi:

    WorldSnapshot
    ChunkSnapshot

## 8.2 Delta

Usato durante il gameplay normale.

Tipi:

    TileDelta
    EntityMoved
    EntitySpawned
    EntityRemoved
    VehicleDelta
    FieldDelta
    EffectEvent
    TimeEvent

Regola:

    una singola mutazione non deve causare automaticamente la
    trasmissione dell'intero chunk.

---

# 9. World Revision e Message Sequence

Definire semanticamente:

    sequence_number
        ordine totale dei messaggi sul transport

    world_revision
        versione dello stato simulativo CDDA

Esempio:

    world_revision = 42
    sequence = 800
    sequence = 801
    sequence = 802

Se il client rileva:

    800
    802

può richiedere resync perché manca 801.

`world_revision` non deve essere usato come sostituto del sequence number.

---

# 10. Nuovi messaggi CWM

Aggiungere almeno:

    EntitySpawned
    EntityRemoved
    ResyncRequest
    WorldReset

Opzionalmente:

    Heartbeat
    HeartbeatAck
    Error
    Disconnect

---

# 11. Entity Protocol Optimization

Evitare stringhe ripetute nei messaggi runtime.

Sostituire:

    type_id: string

con:

    entity_type: enum
    archetype_id: uint16

Esempio:

    archetype_id = 1001
        → mon_zombie

Il mapping è definito nella manifest/registry.

Le stringhe possono essere utilizzate nei file statici di configurazione,
ma non devono essere necessarie per i delta ad alta frequenza.

---

# 12. ChunkSnapshot

Definire formalmente il layout lineare dei blocchi:

    index =
        x + size_x * (y + size_y * z)

Invariant:

    blocks.size == size_x * size_y * size_z

Il significato degli assi deve essere esplicitamente definito dal protocollo.

---

# 13. CWM Independence

`CwmBlock` non deve utilizzare direttamente concetti nativi Luanti come:

- `content_t`;
- `MapNode`;
- `param1`;
- `param2`;
- `MapBlock`.

Utilizzare concetti astratti:

    material_id
    state_flags
    lighting
    orientation
    geometry

Solo il translator Luanti esegue:

    CWM
      ↓
    Luanti content/node representation

Lo schema CWM deve poter essere implementato da un renderer diverso
da Luanti senza modificarne la semantica.

---

# 14. CDDA Event Export

Il CWM exporter non deve inviare direttamente dati sul socket da metodi
interni ad alta frequenza come `map::set()`.

Pattern obbligatorio:

    simulation mutation
        ↓
    local mutation/event collection
        ↓
    end-of-step / end-of-turn batch
        ↓
    immutable CWM delta
        ↓
    FlatBuffers
        ↓
    transport

Questo evita che il networking entri direttamente nella critical path
della simulazione.

---

# 15. Batching

Una simulazione che modifica molte tile deve produrre un singolo batch
quando possibile.

Esempio:

    explosion
        ↓
    3000 tile changes
        ↓
    one WorldDelta

e non:

    3000 socket writes

Il batch size massimo deve essere configurabile.

---

# 16. Headless CDDA

La modalità headless non deve essere considerata una semplice flag già
esistente.

Deve essere una vera milestone tecnica.

Obiettivi:

- nessuna SDL initialization;
- nessuna curses UI;
- nessun renderer;
- world load;
- world creation;
- simulation advancement;
- programmatic input;
- save/load;
- logging.

Acceptance criteria:

    CDDA boots headless
    loads/creates world
    advances simulation
    receives command
    saves
    exits cleanly

Qualsiasi flag come:

    -DNO_SDL
    -DIPC_SERVER

deve essere verificato contro il build system del commit baseline,
non assunto preventivamente.

---

# 17. Milestone Status Semantics

Usare esclusivamente:

    PLANNED
    IN PROGRESS
    VERIFIED

Non usare `COMPLETED` come sinonimo di "specificato".

Un milestone è `VERIFIED` solo se esistono:

- commit;
- command riproducibile;
- test output;
- ambiente;
- risultato verificabile.

Esempio:

    M1 — VERIFIED

    commit:
        abcdef...

    command:
        python3 tests/vertical_slice_test.py

    result:
        PASS

---

# 18. SAVE-001

La verifica deve controllare equivalenza semantica, non uguaglianza
byte-for-byte dei file.

Test:

    same pinned CDDA commit

    create world
    play through 3D client
    save
    close

    load with clean upstream-compatible CDDA

Verify:

    player position
    inventory
    terrain
    furniture
    monsters
    NPCs
    vehicles
    time
    relevant world state

Il requisito è:

    canonical semantic state preserved

non:

    save files byte-identical

---

# 19. Save baseline

Il test deve usare esattamente il commit CDDA baseline utilizzato
dal progetto.

Non confrontare automaticamente con `master` corrente.

---

# 20. Luanti Mesh Pipeline

Sostituire la formulazione:

    "greedy voxel meshing, LOD"

con:

    "Luanti-native mesh update pipeline"

Obiettivi V1:

- sfruttare il meshing esistente;
- minimizzare dirty chunk rebuild;
- evitare mesh generation duplicata;
- usare LOD soltanto se dimostrato necessario dai benchmark.

LOD è una fase di ottimizzazione, non requisito fondamentale del vertical slice.

---

# 21. Luanti C++ Bridge

Il bridge C++ deve assumere la responsabilità di:

- CWM transport;
- message validation;
- snapshot ingestion;
- delta ingestion;
- world projection;
- entity synchronization;
- input capture;
- command generation;
- interpolation;
- debug metrics.

La Lua layer non deve essere il percorso critico dell'IPC.

---

# 22. Mineclonia Content Layer

Mineclonia viene trattata come:

    content source

non come:

    gameplay subsystem

Riutilizzare selettivamente:

- textures;
- node definitions;
- models;
- animation data;
- visual metadata.

Rimuovere/non includere:

- hunger;
- crafting;
- farming;
- mob AI;
- mob spawning;
- world generation;
- survival rules;
- Mineclonia persistence.

---

# 23. Vertical Slice

Il vertical slice deve rimanere estremamente piccolo.

Scena minima:

    1 room
    1 floor
    1 wall
    1 door
    1 item
    1 player
    1 zombie

Flusso:

    CDDA
      ↓
    CWM snapshot
      ↓
    Luanti rendering
      ↓
    user input
      ↓
    CWM command
      ↓
    CDDA
      ↓
    authoritative result
      ↓
    visual interpolation

Success criteria:

- rendering corretto;
- movement;
- zombie movement;
- attack;
- door interaction;
- save/load.

---

# 24. Input Idempotency

Ogni command deve contenere:

    command_id

La risposta deve contenere lo stesso:

    command_id

Questo consente:

- deduplicazione;
- retry;
- debugging;
- handling di reconnect.

---

# 25. Multiplayer-ready Input

Anche in single-player il command model deve essere compatibile con:

    session_id
    player_id
    command_id

Non implementare il multiplayer nella V1.

Implementare invece un protocollo che non lo renda impossibile.

---

# 26. Transport Evolution

V1:

    single player
    local transport

Future:

    multiplayer
    network transport

Il codice applicativo non deve assumere:

    localhost
    one client
    one player

Queste sono proprietà del deployment iniziale, non del protocollo.

---

# 27. Future Multiplayer Topology

Architettura futura:

    ┌─────────────────────┐
    │      CDDA Server    │
    │                     │
    │ simulation authority│
    └──────┬─────┬───────┘
           │     │
         CWM     CWM
           │     │
           ▼     ▼
       Luanti   Luanti
       Client   Client

Non introdurre:

    CDDA server
        ↓
    Luanti server
        ↓
    clients

come doppia authority.

---

# 28. Per-client projection

Per il single-player:

    full relevant world projection

Per il futuro multiplayer:

    server
      ↓
    visibility/filtering
      ↓
    per-client CWM stream

Questo deve essere tenuto compatibile con il protocollo, senza
implementare il filtraggio completo nella V1.

---

# 29. Runtime Architecture Summary

## Single-player V1

    [Launcher]
        │
        ├──────► [CDDA]
        │           │
        │           │ CWM
        │           ▼
        └──────► [Luanti]
                    │
                    ▼
               [Player]

## Future multiplayer

    [CDDA Dedicated Server]
          │       │       │
         CWM     CWM     CWM
          │       │       │
          ▼       ▼       ▼
       Client   Client   Client

---

# 30. Updated Repository Structure

    cdda-mineclonia/
    ├── cdda/
    │   └── src/cwm/
    ├── luanti/
    │   └── src/cdda/
    ├── mineclonia/
    ├── game/
    │   └── mods/
    │       ├── cdda_nodes/
    │       └── cdda_entities/
    ├── protocol/
    │   ├── cwm.fbs
    │   ├── include/
    │   ├── src/
    │   └── tests/
    ├── launcher/
    │   └── launcher_main.cpp
    ├── tools/
    └── tests/

`protocol/` è indipendente da CDDA e Mineclonia.

`launcher/` non implementa la sincronizzazione runtime.

---

# 31. Updated Priority Order

Implementazione consigliata:

    P0  Pin exact commits
    P1  Clean build CDDA
    P2  Clean build Luanti
    P3  Mineclonia content extraction
    P4  Headless CDDA
    P5  CWM protocol
    P6  Luanti C++ bridge
    P7  Vertical slice
    P8  SAVE-001
    P9  Terrain / multi-Z
    P10 Entities
    P11 Input / interaction
    P12 Dynamic fields
    P13 Vehicles
    P14 UI
    P15 Performance
    P16 Packaging

La verifica SAVE-001 deve avvenire presto e non essere lasciata alla fase
finale di packaging.

---

# 32. Acceptance Criteria per l'architettura

L'architettura è considerata validata quando:

    1. CDDA esegue headless.
    2. Luanti riceve un WorldSnapshot.
    3. Una scena 3D viene costruita.
    4. Input viene inviato a CDDA.
    5. CDDA decide l'azione.
    6. Luanti rappresenta il risultato.
    7. Entity interpolation funziona.
    8. Save/load rimane semanticamente compatibile.
    9. Protocol sequence/revision sono verificabili.
    10. Reconnect/resync funziona.
    11. Il protocollo non dipende dal transport.
    12. Il protocollo non assume un solo client.
    13. Il gameplay Mineclonia non esercita alcuna autorità.
    14. Il renderer non accede direttamente a strutture CDDA non thread-safe.

---

# 33. Final Architectural Principle

La specifica deve essere riassunta dal seguente principio:

    CDDA simula.

    CWM descrive e sincronizza lo stato.

    Luanti presenta.

    Mineclonia fornisce contenuti visuali selezionati.

    Il Launcher orchestra i processi ma non governa il gameplay.

    Il transport è sostituibile.

    Il protocollo è progettato per funzionare prima in single-player
    e potenzialmente in multiplayer senza cambiare il modello di authority.

    Nessun client visuale può diventare fonte autorevole della simulazione.
```"
