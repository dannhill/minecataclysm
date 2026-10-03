/plan implementa questo: "# CDDA–Mineclonia Integration
## Software Architecture & Engineering Specification
### Versione 1.0 — Architectural Baseline

---

## 0. Documento

### 0.1 Scopo

Questo documento definisce l'architettura software, il modello dati, il protocollo di integrazione, la strategia di build, il piano di test, i requisiti prestazionali e la roadmap implementativa del progetto:

> trasformare Cataclysm: Dark Days Ahead (CDDA) in un gioco con rappresentazione 3D voxel/3D elaborata basata sull'ecosistema Luanti + Mineclonia.

Il progetto mantiene CDDA come:

- simulation authority;
- gameplay authority;
- persistence authority;
- temporal authority.

Luanti viene utilizzato come:

- runtime grafico;
- motore di rendering 3D;
- chunk/mesh manager;
- sistema di rendering delle entità;
- audio/video presentation layer;
- acquisizione input.

Mineclonia viene utilizzato selettivamente come:

- fonte di contenuti voxel;
- palette e definizioni visuali;
- texture;
- modelli;
- animazioni;
- eventuale codice Lua riutilizzabile esclusivamente dove utile alla presentazione.

La gameplay logic Minecraft-like di Mineclonia non costituisce parte del gameplay finale.

---

# 1. Obiettivi

## 1.1 Obiettivo primario

Produrre un client 3D capace di rappresentare in tempo reale lo stato simulativo autentico di CDDA senza alterarne le regole fondamentali.

Il giocatore deve poter utilizzare il mondo 3D come interfaccia primaria mantenendo:

- regole di movimento CDDA;
- combattimento CDDA;
- IA CDDA;
- inventario CDDA;
- crafting CDDA;
- veicoli CDDA;
- campi ed effetti CDDA;
- meteo CDDA;
- salvataggi CDDA.

## 1.2 Obiettivi secondari

Il sistema deve inoltre:

1. supportare esplorazione 3D;
2. supportare più z-level;
3. rappresentare entità animate;
4. rappresentare veicoli;
5. rappresentare effetti dinamici;
6. mantenere la compatibilità dei salvataggi;
7. permettere aggiornamenti indipendenti dei fork;
8. mantenere un confine netto tra simulazione e presentazione.

## 1.3 Non-obiettivi

Non rientrano nel progetto iniziale:

- ricreare il gameplay Minecraft;
- mantenere crafting Mineclonia;
- mantenere hunger Mineclonia;
- mantenere farming Mineclonia;
- mantenere IA mob Mineclonia;
- utilizzare la fisica player di Luanti come autorità;
- utilizzare la persistenza mondo nativa di Luanti;
- trasformare CDDA in un gioco realmente free-movement;
- riscrivere la simulazione CDDA in Lua.

---

# 2. Progetti upstream

## 2.1 Cataclysm: Dark Days Ahead

Repository ufficiale:

    github.com/CleverRaven/Cataclysm-DDA

Ruolo:

    Simulation authority

Licenza dichiarata dal progetto:

    CC BY-SA 3.0

Nota:

    CDDA contiene anche componenti di terze parti con licenze proprie.
    Nessun audit di licenza deve assumere automaticamente che ogni file del
    repository possieda la medesima licenza.

---

## 2.2 Luanti

Repository ufficiale:

    github.com/luanti-org/luanti

Ruolo:

    3D voxel engine / client runtime

Licenza principale:

    LGPL-2.1-or-later

Architettura:

    C++ engine
    + server/client runtime
    + Lua API
    + rendering/meshing
    + content system

---

## 2.3 Mineclonia

Upstream canonico:

    codeberg.org/mineclonia/mineclonia

Mirror GitHub disponibile per comodità:

    github.com/mark-wiemer/mineclonia

Ruolo:

    content/game layer di Luanti
    fonte di modelli, texture, definizioni e componenti visuali

Licenza del codice:

    GPLv3-or-later

Media:

    licenze miste secondo LEGAL.md e file/mod interessati.

IMPORTANTE:

    Il mirror GitHub non deve essere trattato automaticamente come
    upstream canonico. La baseline deve essere determinata dal commit
    effettivamente utilizzato nel progetto.

---

# 3. Decisione architetturale

## 3.1 Full source merge

Stato:

    NO-GO come baseline di engineering.

Motivazione:

    CDDA utilizza CC BY-SA 3.0 per il progetto principale.
    Mineclonia utilizza GPLv3-or-later per il codice.

    Creative Commons dichiara GPLv3 compatibile come licenza di
    destinazione per adattamenti CC BY-SA 4.0, ma non identifica GPLv3
    come licenza compatibile con CC BY-SA 3.0.

Conseguenza:

    il progetto non assume la possibilità di trasformare CDDA + Mineclonia
    in un unico programma distribuito sotto un regime licenziario unico.

Questa decisione è una decisione conservativa di ingegneria, non un parere
legale definitivo.

Qualunque futura riapertura del Full Merge richiede una specifica
license review formale.

---

# 4. Architettura selezionata

## 4.1 Modello generale

Il sistema è composto da due processi principali e tre componenti logici.

    PROCESSO A
    ┌─────────────────────────────────┐
    │ CDDA                             │
    │                                 │
    │ Simulation Core                 │
    │ Reality Bubble                  │
    │ Gameplay                        │
    │ AI                              │
    │ Combat                          │
    │ Vehicles                        │
    │ Weather                         │
    │ Save/Load                       │
    │                                 │
    │ CWM Exporter / Input Receiver   │
    └──────────────┬──────────────────┘
                   │
                   │ CWM protocol
                   │ FlatBuffers
                   │
                   ▼
    PROCESSO B
    ┌─────────────────────────────────┐
    │ Luanti                          │
    │                                 │
    │ C++ CWM Bridge                  │
    │ ClientMap                       │
    │ Meshing                         │
    │ Rendering                       │
    │ Audio                           │
    │ Entity Presentation             │
    │                                 │
    │ Mineclonia Content              │
    └─────────────────────────────────┘

Componenti logici:

    1. CDDA Simulation Authority
    2. Common World Model / Integration Coordinator
    3. Luanti Presentation Runtime

Il Coordinator è inizialmente un modulo logico integrato nel processo CDDA,
non necessariamente un terzo processo.

---

# 5. Principio fondamentale: simulation authority

CDDA è l'unica autorità per:

- posizione reale delle creature;
- movimento;
- collisioni gameplay;
- combattimento;
- danno;
- HP;
- stamina;
- inventario;
- crafting;
- fame;
- sete;
- temperature;
- campi;
- fuoco;
- IA;
- NPC;
- veicoli;
- meteo;
- tempo simulato;
- visibilità gameplay;
- persistenza.

Luanti non può autonomamente correggere o sostituire uno stato proveniente
da CDDA.

Regola:

    Luanti presentation != simulation authority

---

# 6. Luanti come presentation authority

Luanti è autorità esclusivamente per:

- camera;
- rendering;
- mesh generation;
- animation presentation;
- interpolazione;
- particelle puramente estetiche;
- post-processing;
- audio spaziale;
- LOD;
- frustum culling;
- effetti grafici.

Esempio:

    CDDA:
        zombie position = (100, 200, 0)

    Luanti:
        interp position = (100.43, 200.21, 1.0 visual units)

La posizione visuale intermedia non modifica la posizione simulativa.

---

# 7. Mineclonia come content source

Mineclonia non viene eseguito come gameplay Minecraft completo.

I sistemi devono essere classificati:

## 7.1 Riutilizzabili

- node definitions;
- texture definitions;
- texture packs;
- modelli;
- skeleton;
- animation metadata;
- materiali;
- effetti visivi;
- eventuali utility Lua non gameplay.

## 7.2 Da eliminare/disabilitare

- crafting Mineclonia;
- hunger Mineclonia;
- farming Mineclonia;
- Mineclonia weather simulation;
- Mineclonia mob AI;
- Mineclonia mob spawning;
- Mineclonia world generation;
- Mineclonia persistence;
- Mineclonia player physics;
- Mineclonia survival rules.

## 7.3 Da riscrivere

- CDDA entity presentation;
- CDDA vehicle presentation;
- CDDA input mapping;
- CDDA world injection;
- CDDA lighting/visibility bridge;
- CDDA interaction layer.

---

# 8. Common World Model

## 8.1 Principio

CDDA e Luanti non devono conoscersi direttamente.

Il modello intermedio è:

    CDDA state
        ↓
    Common World Model
        ↓
    Luanti representation

Il CWM deve essere indipendente da:

- MapBlock;
- content_id;
- param1;
- param2;
- SAO;
- specifiche classi Luanti.

Tali strutture appartengono al translator verso Luanti.

---

# 9. CWM — categorie semantiche

Il CWM deve distinguere almeno:

    Block
    Surface
    Furniture
    Entity
    Vehicle
    Item
    Field
    Light
    Weather
    Effect
    WorldEvent
    InputCommand
    TimeState

---

# 10. CWM coordinate model

## 10.1 Coordinate logiche

CDDA utilizza:

    (x, y, z_level)

dove:

    x = coordinata orizzontale
    y = coordinata orizzontale
    z = z-level discreto

## 10.2 Coordinate visuali

Luanti utilizza:

    (X, Y, Z)

Il mapping esatto tra z-level e altezza visuale NON deve essere hard-coded
nel protocollo.

Definire:

    world_scale_xy
    floor_height
    entity_eye_height
    voxel_height

come parametri di configurazione del presentation layer.

Esempio:

    X = x * scale_xy
    Z = y * scale_xy
    Y = z_level * floor_height + local_offset

La scelta iniziale può essere:

    scale_xy   = 1.0
    floor_height = 3.0

ma il valore 3.0 è una scelta grafica, non una proprietà semantica di CDDA.

---

# 11. CWM block representation

Esempio concettuale:

    CwmBlock {
        material_id
        geometry_type
        surface_flags
        transparency
        light_level
        orientation
        state_flags
    }

Il translator Luanti converte:

    CwmBlock
        →
    MapNode / node definition / mesh

---

# 12. Terrain mapping

## 12.1 Terrain

CDDA:

    ter_id

CWM:

    MaterialDefinition

Luanti:

    node/content definition

Non trasmettere ogni volta il nome testuale "t_wall".
Utilizzare ID numerici ottenuti tramite una manifest condivisa.

---

# 13. Furniture mapping

Furniture statico:

    CWM Prop
        ↓
    Luanti node/nodebox/static mesh

Furniture con comportamento visuale:

    CWM InteractiveProp
        ↓
    Luanti entity / animated presentation

La logica comportamentale rimane in CDDA.

---

# 14. Entity mapping

CDDA entity:

    authoritative entity ID
    entity type
    logical position
    state
    orientation
    animation hint

Luanti:

    visual entity
    3D model
    skeleton
    animation state

Esempio:

    CDDA:
        entity_id = 9321
        type = MONSTER
        monster_id = mon_zombie
        position = (100, 200, 0)

    CWM:
        EntitySnapshot

    Luanti:
        cdda_client:mon_zombie

Il client non deve conoscere:

- HP esatto;
- AI state;
- internal attack logic;
- pathfinding;
- biological stats;

salvo quando tali informazioni servono esplicitamente alla presentazione.

---

# 15. Entity interpolation

## 15.1 Regola iniziale

Usare interpolazione lineare tra stati confermati.

    State A
       ↓
    confirmed State B
       ↓
    interpolation

Non utilizzare inizialmente predizione fisica complessa.

## 15.2 Future enhancement

Solo dopo la stabilizzazione:

- spline;
- dead reckoning;
- local prediction;
- animation blending.

---

# 16. Vehicle representation

I veicoli non devono essere convertiti in semplici voxel statici.

Modello:

    Vehicle
       ├── root transform
       ├── chassis
       ├── wheels
       ├── doors
       ├── windows
       ├── equipment
       ├── turrets
       └── visual components

CDDA resta autorità su:

- posizione;
- velocità;
- direzione;
- componenti;
- collisione;
- danno;
- occupanti.

Luanti determina soltanto la rappresentazione visuale.

---

# 17. Fields and effects

CDDA:

    field_entry

CWM:

    FieldState

Luanti:

    particle emitter
    light source
    smoke/fire material
    post-processing effect

Principio:

    gameplay effect ≠ rendering effect

Una particella client non deve modificare la simulazione.

---

# 18. Visibility and lighting

CDDA continua a determinare:

- line of sight;
- conosciuto/sconosciuto;
- fog of war;
- condizioni di visibilità gameplay.

Luanti determina:

- illuminazione visiva;
- ombre;
- bloom;
- atmosfera;
- fog estetico.

Il renderer deve poter ricevere una mask o un insieme di visibility states
dal CWM.

---

# 19. Luanti Integration Layer

## 19.1 C++ bridge

Il bridge principale deve essere implementato nell'engine C++ di Luanti.

Non affidarsi a:

    Lua + socket
    Lua + FFI

come percorso critico del rendering.

Motivazioni:

- accesso diretto al client engine;
- accesso a ClientMap;
- accesso a entity/scene systems;
- nessuna dipendenza dal sandbox Lua per IPC;
- meno allocazioni;
- controllo migliore del threading;
- migliore integrazione con il meshing.

Lua/Mineclonia resta utilizzabile per configurazione e content logic.

---

# 20. Engine-side responsibilities

Il C++ bridge Luanti deve implementare:

- CWM protocol client;
- snapshot ingestion;
- delta ingestion;
- entity synchronization;
- chunk injection;
- entity presentation;
- input extraction;
- command generation;
- connection management;
- resynchronization;
- client-side interpolation.

---

# 21. Protocollo

Nome:

    CDDA CWM Protocol

Transport:

    Unix Domain Socket su POSIX
    loopback TCP su Windows

Fallback futuro:

    named pipe Windows nativo

Non usare networking pubblico per la versione single-player.

---

# 22. Protocol stages

## 22.1 Handshake

Client:

    HELLO(protocol_version, build_id)

Server:

    HELLO_ACK(protocol_version, server_build_id)

## 22.2 Snapshot

Server:

    WORLD_SNAPSHOT

contenente:

- origin;
- dimensions;
- chunk set;
- entities;
- environment;
- time state.

## 22.3 Delta stream

Server:

    TILE_DELTA
    ENTITY_DELTA
    VEHICLE_DELTA
    FIELD_DELTA
    EFFECT_EVENT
    TIME_EVENT

## 22.4 Client input

Client:

    MOVE_REQUEST
    INTERACT_REQUEST
    ATTACK_REQUEST
    INVENTORY_REQUEST
    UI_COMMAND

---

# 23. Message identity

Ogni comando client deve possedere:

    command_id

Ogni messaggio di stato deve possedere:

    world_revision
    sequence_number

Questo consente:

- deduplicazione;
- ordering;
- debugging;
- recovery;
- resync.

---

# 24. Snapshot vs Delta

## Snapshot

Utilizzato:

- all'avvio;
- dopo reconnect;
- dopo perdita di sincronizzazione;
- quando il giocatore cambia area in maniera significativa.

Formato:

    ChunkSnapshot

## Delta

Utilizzato nel gioco normale.

Esempi:

    TileDelta
    EntityMoved
    EntitySpawned
    EntityRemoved
    VehicleDelta
    FieldDelta

Non inviare un intero chunk quando è cambiata una singola tile.

---

# 25. FlatBuffers

FlatBuffers è il formato binario principale candidato.

Motivazioni:

- schema esplicito;
- versionabilità;
- accesso strutturato ai dati serializzati;
- buona integrazione C++;
- payload compatti;
- adatto a snapshot e delta.

MA:

    "zero-copy" deve essere inteso come accesso senza
    deserializzazione completa lato consumer.

Non assumere zero-copy end-to-end fra:

    CDDA memory
    kernel
    socket
    Luanti
    mesh
    GPU.

La necessità effettiva di FlatBuffers deve essere confermata con benchmark.

---

# 26. Protocol schema iniziale

Esempio:

    namespace CDDA.CWM;

    enum EntityType : byte {
        PLAYER,
        NPC,
        MONSTER,
        VEHICLE,
        ITEM,
        EFFECT
    }

    struct Vec3f {
        x: float;
        y: float;
        z: float;
    }

    struct Coord3 {
        x: int32;
        y: int32;
        z: int32;
    }

    table TileDelta {
        revision: ulong;
        coord: Coord3;
        material_id: ushort;
        state: uint;
    }

    table ChunkSnapshot {
        chunk_x: int32;
        chunk_y: int32;
        chunk_z: int32;
        blocks: [ushort];
    }

    table EntityState {
        id: ulong;
        type: EntityType;
        position: Vec3f;
        rotation: float;
        animation: ushort;
    }

    table MoveRequest {
        command_id: ulong;
        direction: byte;
    }

    table Message {
        sequence: ulong;
        revision: ulong;
        payload: Payload;
    }

    union Payload {
        ChunkSnapshot,
        TileDelta,
        EntityState,
        MoveRequest
    }

Questo schema è illustrativo e non è ancora ABI definitivo.

---

# 27. Protocol versioning

Ogni protocollo deve avere:

    major
    minor

Regole:

    major incompatibile
    minor compatibile quando possibile

Il client deve rifiutare una versione major sconosciuta.

---

# 28. Heartbeat

Heartbeat iniziale:

    10 Hz

Timeout iniziale:

    2–3 secondi

I valori definitivi devono essere benchmarkati.

Heartbeat non deve essere utilizzato per sincronizzare la simulazione.

---

# 29. Recovery

In caso di disconnessione:

    freeze presentation

mostrare:

    "Simulation link lost"

Alla riconnessione:

    HELLO
      ↓
    WORLD_SNAPSHOT
      ↓
    RESUME

Non tentare di ricostruire lo stato mediante una sequenza potenzialmente
incompleta di delta.

---

# 30. Time model

CDDA mantiene:

    simulation time

Luanti mantiene:

    presentation time

Il rendering deve poter funzionare a:

    60+ FPS

indipendentemente dal numero di aggiornamenti simulativi effettivamente
prodotti da CDDA.

Il frame rate non costituisce la frequenza della simulazione.

---

# 31. Time dilation

Durante:

- sonno;
- lettura;
- attività lunghe;
- attese estese;

CDDA può avanzare rapidamente nella simulazione.

Il protocollo deve quindi supportare:

    TIME_JUMP
    TIME_ACCELERATION
    SIMULATION_BUSY

Il client può:

- animare il cielo;
- accelerare effetti;
- sospendere animazioni non necessarie;
- bloccare input non compatibili.

Non deve però inventare gameplay durante il salto temporale.

---

# 32. Input architecture

Flusso:

    user input
        ↓
    Luanti client
        ↓
    CWM command
        ↓
    CDDA
        ↓
    action validation
        ↓
    simulation result
        ↓
    world delta
        ↓
    visual update

---

# 33. Movement

W/A/S/D non modificano direttamente la posizione simulativa.

Esempio:

    W
     ↓
    MOVE_REQUEST(NORTH)
     ↓
    CDDA validates
     ↓
    accepted/rejected
     ↓
    EntityMoved
     ↓
    animation

Questo preserva l'autorità CDDA.

---

# 34. Mouse picking

Il client identifica:

    visual coordinate

Il CWM converte:

    visual coordinate
        ↓
    CDDA tile coordinate

L'interazione finale è sempre validata da CDDA.

---

# 35. Collision system

Il client non deve diventare authoritative.

Luanti può:

- calcolare raycast visuale;
- identificare target;
- calcolare camera obstruction;
- effettuare collision checks grafici opzionali.

CDDA decide:

- se un movimento è valido;
- se una porta può essere aperta;
- se un colpo colpisce;
- se un proiettile impatta;
- se un attore può attraversare una posizione.

---

# 36. UI architecture

Due livelli:

## 36.1 HUD 3D

Implementato dal client.

Esempi:

- barra stamina;
- HP;
- temperatura;
- status;
- quick actions.

## 36.2 UI complessa

Nella prima fase non riscrivere tutti i menu CDDA.

Usare una UI overlay dedicata.

Priorità:

    P0:
        input
        targeting
        movement
        combat
        inventory basics

    P1:
        crafting
        vehicle interface
        medical UI

    P2:
        complete redesign
        native 3D interfaces

---

# 37. Save/Load

CDDA è l'unica persistence authority.

Luanti non deve mantenere il mondo come savegame.

Il mondo Luanti è:

    derived state
    cache
    presentation state

All'avvio:

    CDDA load
       ↓
    snapshot
       ↓
    Luanti rebuild

Alla chiusura:

    Luanti discards visual world

    CDDA saves canonical world

---

# 38. Save compatibility requirement

Requirement:

    SAVE-001

Un mondo modificato tramite il client 3D deve poter essere caricato
dal fork CDDA standard senza il client 3D.

Target successivo:

    SAVE-002

Il save modificato tramite il client 3D deve poter essere aperto
anche dall'upstream CDDA compatibile con la baseline utilizzata.

Questo deve essere verificato con test automatici.

---

# 39. World streaming

La Reality Bubble non deve essere confusa con:

- area renderizzata;
- area visualizzata;
- area trasferita;
- area meshed.

Definire separatamente:

    CDDA active simulation area
    CWM streaming area
    Luanti loaded chunk area
    camera-visible area

---

# 40. CDDA baseline geometry

CDDA attualmente definisce:

    MAPSIZE = 11
    SEEX = 12
    SEEY = 12

con una Reality Bubble di circa 60 tile di raggio secondo i commenti
del codice corrente.

Il renderer non deve assumere una dimensione immutabile:
la baseline esatta deve essere letta dal commit scelto.

---

# 41. Luanti MapBlock

Luanti usa MapBlock:

    16 × 16 × 16 MapNodes

Questo è un dettaglio dell'implementazione Luanti, non del CWM.

Il CWM può utilizzare qualsiasi chunk dimensione interna.

Translator:

    CWM chunk
        ↓
    Luanti MapBlock

---

# 42. Chunk cache

Il client manterrà:

    current chunks
    neighboring chunks
    dirty chunks
    mesh state

Stati possibili:

    EMPTY
    RECEIVED
    DIRTY
    MESHING
    READY
    EVICTED

---

# 43. Meshing

Il sistema deve preferire:

    greedy meshing / engine-native meshing

per:

- muri;
- pavimenti;
- terreno;
- superfici ripetitive.

Mesh custom per:

- furniture;
- veicoli;
- ringhiere;
- oggetti;
- strutture complesse.

---

# 44. Verticality

La relazione:

    1 z-level CDDA = N visual units

è configurabile.

Baseline iniziale consigliata:

    floor_height = 3.0

ma non deve essere incorporata nello schema CWM.

---

# 45. Z-level rendering

Il renderer deve supportare:

- piano attivo;
- piani superiori;
- piani inferiori;
- aperture;
- scale;
- sotterranei;
- soffitti;
- occlusion.

Test obbligatori:

    open building
    closed building
    basement
    multi-floor building
    stairwell
    rooftop
    shaft

---

# 46. Lighting

CDDA lighting semantics:

    authoritative for gameplay/visibility

Luanti lighting:

    authoritative for visual appearance

Non utilizzare il solo sistema di illuminazione grafico Luanti per decidere
se un mostro esiste o meno dal punto di vista del gameplay.

---

# 47. Asset pipeline

Ogni asset deve possedere:

    asset_id
    source_project
    source_path
    source_commit
    author
    license
    modification_status

Esempio:

    asset_id:
        cdda_vehicle_ambulance

    source:
        CDDA

    commit:
        <SHA>

    license:
        CC BY-SA 3.0

---

# 48. Asset manifest

File:

    assets-manifest.json

Campi minimi:

    id
    source
    source_commit
    original_path
    license
    author
    derivative_of
    transformed
    destination

La build CI deve poter verificare che ogni asset distribuito possieda una
provenienza identificabile.

---

# 49. Asset licensing rule

Mai assumere:

    "licenza del progetto = licenza di ogni asset"

Ogni asset deve essere verificato contro:

- license file;
- LEGAL.md;
- README;
- directory-level license;
- copyright header;
- upstream provenance.

---

# 50. Repository structure

Struttura di sviluppo:

    cdda-mineclonia/
    ├── cdda/
    ├── luanti/
    ├── mineclonia/
    ├── protocol/
    │   ├── cwm.fbs
    │   ├── README.md
    │   └── LICENSE
    ├── coordinator/
    ├── tools/
    ├── tests/
    ├── docs/
    └── packaging/

La directory `protocol/` è indipendente dai due fork.

---

# 51. CDDA fork policy

Modifiche preferite:

    additive bridge code

Esempio:

    src/cwm/

Evitare, quando possibile:

    modifiche invasive alla simulation core

La patch CDDA deve essere strutturata in modo da permettere:

    upstream update
        ↓
    rebase
        ↓
    bridge patch reapply

---

# 52. Luanti fork policy

Il fork Luanti deve contenere:

    src/cdda/

o equivalente modulo isolato.

Funzioni principali:

    protocol client
    world injection
    entity synchronization
    input extraction
    rendering bridge

Evitare modifiche arbitrarie al core dell'engine.

---

# 53. Mineclonia fork policy

Il progetto Mineclonia può essere vendorizzato o forkato separatamente.

Le modifiche dovrebbero essere limitate a:

- estrazione di content;
- adattamento asset;
- rimozione gameplay;
- visual presentation;
- API visuali.

Non rendere il gameplay Minecraft dipendenza del sistema.

---

# 54. Build system

Non imporre uno standard C++ unico a tutti i progetti.

Baseline:

    CDDA:
        C++17
        upstream-native build

    Luanti:
        upstream-native build configuration

    Coordinator / CWM utilities:
        C++20

Il root build system può orchestrare i tre sottoprogetti senza modificare
artificialmente gli standard richiesti dai rispettivi upstream.

---

# 55. Dependency policy

Le dipendenze devono rimanere associate al sottosistema che le richiede.

Esempio:

    CDDA:
        SDL3 (se necessaria)
        zlib
        gettext
        ecc.

    Luanti:
        IrrlichtMt
        LuaJIT
        SQLite
        OpenGL
        OpenAL
        ecc.

    Integration:
        FlatBuffers

Evitare di trasformare tutte le dipendenze in un unico global dependency set
senza necessità.

---

# 56. Headless CDDA

Questa è una milestone tecnica reale, non una semplice build flag.

Obiettivo:

    CDDA starts without:
        SDL UI
        curses UI
        normal renderer
        interactive frontend

ma mantiene:

        simulation
        world loading
        input command system
        save/load
        logs

Acceptance criteria:

    A CDDA world starts successfully.
    Canonical state loads.
    No graphical window is created.
    No curses UI is required.
    Simulation can advance.
    Input commands can be supplied programmatically.
    Save succeeds.

---

# 57. CDDA integration API

API concettuale minima:

    initialize_world()
    get_world_snapshot()
    get_chunk()
    get_entity_snapshot()
    submit_command()
    submit_input()
    get_world_revision()
    save_world()
    shutdown()

Non esporre direttamente strutture interne CDDA al client.

---

# 58. Protocol command set

Versione iniziale:

    MOVE
    INTERACT
    ATTACK
    PICKUP
    DROP
    USE
    OPEN
    CLOSE
    EXAMINE
    INVENTORY_ACTION
    UI_ACTION
    CAMERA_HINT

La command authority rimane CDDA.

---

# 59. World events

Il server deve poter pubblicare:

    TILE_CHANGED
    TERRAIN_CHANGED
    FURNITURE_CHANGED
    ENTITY_SPAWNED
    ENTITY_MOVED
    ENTITY_REMOVED
    VEHICLE_CHANGED
    FIELD_CHANGED
    FIRE_CHANGED
    WEATHER_CHANGED
    TIME_CHANGED
    EFFECT_TRIGGER
    WORLD_REVISION

---

# 60. Threading model

CDDA:

    authoritative simulation thread model
    secondo quanto previsto upstream

Coordinator/CWM export:

    minimizzare lock
    minimizzare accessi concorrenti alla map

Luanti:

    rispettare il threading model dell'engine

Mai introdurre un renderer thread che acceda direttamente a strutture CDDA
interne non thread-safe.

La comunicazione deve avvenire tramite snapshot/delta immutabili.

---

# 61. Snapshot strategy

Quando serve leggere CDDA:

    simulation state
        ↓
    export snapshot
        ↓
    release simulation structures
        ↓
    serialize
        ↓
    send

Evita:

    renderer
        ↓
    direct concurrent access
        ↓
    CDDA map internals

---

# 62. Performance targets

Questi sono TARGET iniziali, non garanzie.

## Client

    target:
        60 FPS

    warning:
        < 50 FPS sustained

    failure:
        < 30 FPS sustained in baseline scenario

## Input-to-visual

Target:

    P95 < 50 ms

Il benchmark iniziale può puntare a valori inferiori, ma non assumerli
come garantiti.

## World initial projection

Target:

    P95 < 5 s

per la baseline hardware definita dal benchmark.

---

# 63. Benchmark machine

Ogni release benchmark deve dichiarare:

    CPU
    GPU
    RAM
    OS
    resolution
    driver
    build type
    compiler
    CDDA commit
    Luanti commit
    Mineclonia commit

---

# 64. Benchmark scenarios

## BM01 — Small Room

    1 player
    1 zombie
    1 door
    1 furniture

## BM02 — Dense Urban

    150 entities
    multi-floor building
    many walls/furniture

## BM03 — Horde

    1000 entities

## BM04 — Fire

    300+ field cells
    smoke
    dynamic lights

## BM05 — Vehicle

    large vehicle
    movement
    camera tracking

## BM06 — Multi-Z

    5+ simultaneously represented levels

---

# 65. Metrics

Registrare almeno:

    FPS
    frame time
    P50
    P95
    P99
    simulation step time
    IPC latency
    bytes/sec
    snapshots/sec
    deltas/sec
    dirty chunks
    mesh generation time
    GPU time
    RAM
    VRAM
    allocation rate
    dropped commands

---

# 66. Testing strategy

## Unit tests

Testare:

- coordinate conversion;
- CWM serialization;
- CWM deserialization;
- ID mapping;
- revision ordering;
- command IDs;
- protocol versioning.

## Integration tests

Testare:

    CDDA → CWM → Luanti

e:

    Luanti input → CWM → CDDA

## Regression tests

Eseguire test suite CDDA upstream.

## Fuzz testing

Fuzzare:

    malformed FlatBuffers
    truncated messages
    invalid coordinates
    invalid entity IDs
    overflow values
    unknown message types
    duplicate sequence IDs

---

# 67. Save/load tests

Test:

    create
    save
    shutdown
    restart
    load
    compare

Confrontare:

    terrain
    entities
    vehicles
    inventory
    world state
    time

Il renderer non deve introdurre stato persistente che cambi il risultato.

---

# 68. Failure tests

Simulare:

    CDDA crash
    Luanti crash
    socket close
    partial packet
    delayed packet
    duplicated packet
    corrupted packet
    client restart
    server restart

---

# 69. Observability

## CDDA

Log:

    simulation
    command
    save
    export
    protocol

## Coordinator/CWM

Log:

    sequence
    revision
    message size
    latency
    queue depth
    dropped/invalid messages

## Luanti

Log:

    chunk updates
    entity updates
    mesh timings
    render timings
    connection state

---

# 70. Debug overlay

Hotkey iniziale:

    F3

Visualizzare:

    simulation revision
    protocol version
    current CDDA coordinate
    current visual coordinate
    FPS
    frame time
    chunks loaded
    chunks dirty
    entities
    RX KB/s
    TX KB/s
    protocol latency
    queue depth
    simulation tick status

---

# 71. Logging correlation

Ogni sessione deve avere:

    session_id

Ogni message:

    sequence_id

Ogni state:

    world_revision

Questo permette di ricostruire un bug end-to-end.

---

# 72. Security

Il sistema è single-player e locale.

Policy:

    no public network bind

Usare:

    Unix Domain Socket
    oppure 127.0.0.1

Permessi restrittivi per file/socket.

Validare sempre:

    length
    range
    entity ID
    coordinate
    enum
    revision
    sequence

Mai fidarsi del client.

---

# 73. Licensing architecture

Il prodotto distribuito mantiene separati:

    CDDA fork
    Luanti fork
    Mineclonia content
    protocol
    launcher

Ogni componente deve mantenere:

    LICENSE
    NOTICE
    source attribution
    provenance

Il launcher non incorpora codice del core se non necessario.

---

# 74. Protocol license

Il protocollo CWM deve essere un componente indipendente.

Esempio consigliato:

    Apache-2.0

oppure altra licenza permissiva scelta esplicitamente.

Il protocollo non deve copiare strutture interne CDDA o Mineclonia.

---

# 75. Distribution structure

    /CDDA-Voxel/
    ├── bin/
    │   ├── cdda-server
    │   ├── luanti-client
    │   └── launcher
    │
    ├── cdda/
    │   ├── data/
    │   └── licenses/
    │
    ├── luanti/
    │   ├── game/
    │   ├── mods/
    │   └── licenses/
    │
    ├── protocol/
    │   └── schema/
    │
    ├── assets/
    │   └── manifest/
    │
    ├── licenses/
    │   ├── CDDA/
    │   ├── Luanti/
    │   ├── Mineclonia/
    │   └── third-party/
    │
    └── user/
        ├── saves/
        ├── config/
        └── logs/

---

# 76. Upstream strategy

Ogni fork mantiene:

    upstream remote
    integration remote

Branch:

    upstream-tracking
    integration
    experimental

Le patch di integrazione devono essere isolate.

Preferire:

    new files
    adapters
    interfaces
    exporters

rispetto a:

    invasive changes to simulation core

---

# 77. Upstream update policy

Ogni aggiornamento upstream deve produrre:

    updated commit manifest
    license re-audit
    build validation
    protocol compatibility check
    save/load regression
    rendering regression

Non aggiornare contemporaneamente CDDA e Luanti senza poter
attribuire eventuali regressioni.

---

# 78. Milestone 0 — Baseline

Obiettivo:

    compilare senza modifiche:

        CDDA
        Luanti
        Mineclonia

Acceptance:

    upstream tests pass
    exact commit recorded
    toolchain recorded
    reproducible build achieved

---

# 79. Milestone 0.5 — Headless CDDA

Obiettivo:

    ottenere una sessione CDDA senza UI grafica.

Acceptance:

    world loads
    simulation advances
    save works
    no graphics window
    programmatic command input works

Questo milestone deve essere completato prima della parte 3D.

---

# 80. Milestone 1 — Vertical Slice

Scena:

    1 room
    1 floor
    1 wall
    1 door
    1 item
    1 zombie
    1 player

Flusso completo:

    CDDA
      ↓
    CWM
      ↓
    Luanti
      ↓
    rendering
      ↓
    input
      ↓
    CDDA

Acceptance:

    player can move
    zombie moves
    attack works
    door interaction works
    visual state matches authoritative state

Questo è il principale architectural proof-of-concept.

---

# 81. Milestone 2 — Terrain projection

Implementare:

    floor
    wall
    furniture
    doors
    windows
    stairs
    roofs
    open air

Acceptance:

    multi-room building rendered correctly

---

# 82. Milestone 3 — Entities

Implementare:

    player
    zombie
    animal
    NPC

Features:

    spawn
    despawn
    movement
    animation
    interpolation

---

# 83. Milestone 4 — Dynamic world

Implementare:

    destruction
    construction
    doors
    furniture changes
    fields
    fire
    smoke
    lighting reactions

---

# 84. Milestone 5 — Interaction

Implementare:

    mouse picking
    keyboard movement
    inspect
    pickup
    attack
    interact

---

# 85. Milestone 6 — Vehicles

Implementare:

    vehicle mesh
    vehicle transform
    movement
    occupants
    doors
    wheels
    destruction presentation

I veicoli devono essere trattati come subsystem separato.

---

# 86. Milestone 7 — Full game loop

Implementare progressivamente:

    inventory
    crafting
    medical
    vehicle management
    base interaction
    NPC management

La UI può inizialmente essere overlay.

---

# 87. Milestone 8 — Performance

Profilare:

    simulation
    protocol
    translation
    chunk update
    meshing
    entity rendering
    GPU

Ottimizzare solo sulla base dei benchmark.

---

# 88. Milestone 9 — Packaging

Produrre:

    Windows build
    Linux build

Test su macchina pulita.

Verificare:

    launch
    licenses
    assets
    save
    update
    crash recovery

---

# 89. Risk register

## R1 — Licensing

Probabilità:

    alta

Impatto:

    critico

Mitigazione:

    Path B
    provenance manifest
    legal review prima della distribuzione

## R2 — Headless CDDA

Probabilità:

    alta

Impatto:

    alto

Mitigazione:

    Milestone 0.5 dedicata

## R3 — Luanti client integration

Probabilità:

    media

Impatto:

    alto

Mitigazione:

    C++ bridge

## R4 — Spatial mismatch

Probabilità:

    alta

Impatto:

    alto

Mitigazione:

    CWM astratto
    floor_height configurabile

## R5 — Vehicle rendering

Probabilità:

    alta

Impatto:

    alto

Mitigazione:

    subsystem dedicato

## R6 — Performance

Probabilità:

    media

Impatto:

    alto

Mitigazione:

    benchmark vertical slice
    profiling

## R7 — Upstream divergence

Probabilità:

    alta

Impatto:

    alto

Mitigazione:

    patch isolation

## R8 — Asset license error

Probabilità:

    media

Impatto:

    critico

Mitigazione:

    asset manifest + CI validation

---

# 90. Decisione tecnica finale

## PRIMARY

    CDDA authoritative simulation
        +
    specialized Luanti client
        +
    selected Mineclonia content
        +
    C++ CWM bridge
        +
    FlatBuffers state protocol
        +
    independent persistence

## NOT PRIMARY

    monolithic CDDA + Luanti merge

## NOT PRIMARY

    Lua-only IPC bridge

## NOT PRIMARY

    Mineclonia gameplay inside final simulation

---

# 91. Success criterion

Il progetto è tecnicamente riuscito quando:

1. CDDA esegue la simulazione senza interfaccia grafica.
2. Luanti visualizza la Reality Bubble tramite CWM.
3. Il giocatore può controllare CDDA dalla visuale 3D.
4. Tutte le decisioni di gameplay vengono effettuate da CDDA.
5. La visualizzazione rimane fluida indipendentemente dal ritmo dei turni.
6. I salvataggi rimangono proprietà di CDDA.
7. Il sistema può essere avviato e chiuso senza corrompere i save.
8. Gli asset utilizzati possiedono provenienza e licenza verificabili.
9. Il protocollo è versionato.
10. Il progetto supera i benchmark e i test definiti.

---

# 92. Repository references

## CDDA

CleverRaven / Cataclysm-DDA

    github.com/CleverRaven/Cataclysm-DDA

## Luanti

luanti-org / luanti

    github.com/luanti-org/luanti

## Mineclonia — GitHub mirror

mark-wiemer / mineclonia

    github.com/mark-wiemer/mineclonia

NOTA:

    Mineclonia indica Codeberg come repository canonico upstream.
    Il mirror GitHub deve essere usato solo quando il commit è stato
    verificato contro l'upstream canonico.

## Mineclonia mirror alternativo

    github.com/ZenonSeth/mineclonia-mirror

---

# 93. Primary external references

CDDA:
    repository
    LICENSE.txt
    map_scale_constants.h
    CMakeLists.txt
    TILESET.md

Luanti:
    repository
    engine structure documentation
    client/server architecture
    client-side mod documentation

Mineclonia:
    README.md
    LEGAL.md
    CONTRIBUTING.md

Licensing:
    Creative Commons BY-SA 3.0 Legal Code
    Creative Commons Compatible Licenses
    GNU GPL FAQ

---

# 94. Final implementation order

L'ordine raccomandato è:

    1. pin dei commit
    2. license/provenance audit
    3. clean build CDDA
    4. clean build Luanti
    5. clean build Mineclonia
    6. headless CDDA proof
    7. protocol standalone
    8. CWM data model
    9. Luanti C++ bridge
    10. one-room vertical slice
    11. terrain
    12. entities
    13. interaction
    14. dynamic fields
    15. vehicles
    16. UI
    17. performance
    18. packaging
    19. upstream maintenance automation

---

# 95. Architectural principle in one sentence

    CDDA simula il mondo.
    CWM descrive il mondo.
    Luanti lo rende visibile.
    Mineclonia fornisce contenuti visuali selezionati.
    Nessun componente visuale diventa autorità sul gameplay."
