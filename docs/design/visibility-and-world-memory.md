# Distanza visiva, memoria e paesaggio 3D

Fonte: [prova manuale e preferenze](../source/terrain-feedback-2026-10-04.md).
Analisi sul codice `3a830d8`, con i pin e le patch conservati nel baseline.
**B è approvata per la direzione dei materiali/vegetazione.** La soluzione
per distanza, nebbia, alberi e rilievo qui descritta è una raccomandazione da
prototipare; non un'approvazione dell'utente né una feature implementata.
La [riparazione successiva](../fixes/exploration-apertures.md) promuove soltanto
i materiali/vegetazione B al gioco normale e corregge aperture/acqua;
non implementa il panorama distante qui proposto.

## I tre limiti oggi sono diversi

1. **Proiezione disponibile.** `export_world_snapshot` invia 9 × 9 chunk di
   16 × 16 celle per ciascuno dei livelli z−1/z/z+1. Copre quindi un quadrato
   nominale di 144 celle, con AIR fuori dalla mappa nativa locale di 132 × 132.
   Un full snapshot rimuove dalla scena ciò che non fa più parte della
   proiezione. Non c'è un panorama persistente delle zone lasciate indietro.
2. **Nebbia grafica del prototipo.** `terrainFogDistance` impone un massimo
   di 40 celle, ridotto prima del bordo più vicino; `drawScene` inizia la
   sfumatura al 45% della distanza finale. Con il massimo di 40, comincia
   dunque a circa 18 celle. È una scelta conservativa della demo, non un
   raggio di vista imposto da CDDA. Togliere la fog lascia visibili i confini
   della proiezione; aumentare soltanto il parametro non crea il terreno mancante.
3. **Conoscenza/percezione.** Le creature vengono visualizzate attraverso
   `avatar::sees`. L'export del terreno, invece, legge attualmente tutti i tile
   inbounds, senza un filtro equivalente di visibilità o memoria. La fog non
   certifica né implementa correttamente la conoscenza del personaggio.

Allargare il panorama e correggere la conoscenza sono lavori collegati ma
distinti. Conservare ciecamente tutti i voxel ricevuti oggi non produrrebbe
una memoria fedele: conserverebbe anche parti mai osservate, inclusi interni.
La nuova soluzione deve far dipendere il dato dal sapere CDDA, non dal fatto
che il renderer lo abbia ricevuto.

## Alternative discusse

| Opzione | Beneficio | Limite e raccomandazione |
|---|---|---|
| 1. Strutture ricordate a distanza maggiore, senza creature lontane | Orizzonte e punti di riferimento conservati, senza aumentare il raggio di simulazione degli attori. | Raccomandata come base. Memoria per casella effettivamente osservata, non edificio intero marcato visto. Stati congelati; un incendio/demolizione/apertura non osservati non aggiornano il ricordo. Distanza finita e budget di mesh. |
| 2. Scala grafica maggiore per casella | Può migliorare dimensioni di stanze, porte e sensazione del passo. | Da rinviare come scelta di proporzioni. Non aggiunge conoscenza né caselle visibili; con una scala uniforme molte proporzioni angolari restano simili. Camera, creature, velocità grafica, picking, multi-Z e veicoli devono usare lo stesso contratto. |
| 3. Mostrare elementi non percepiti, poi applicare limiti/penalità | Panorama più libero e creature sempre visibili. | Non raccomandata per il problema attuale; l'utente è già poco propenso. Sapere dov'è un nemico è un vantaggio anche senza poterlo colpire: una penalità di mira non elimina l'informazione aggiuntiva. Richiederebbe una distinta decisione di gameplay. |
| 4. Presentazione a distanza variabile: dettaglio osservato vicino, memoria statica lontana, sagome da overmap nota ancora oltre | Migliora skyline e continuità contenendo il costo, con haze leggero soltanto presso il limite effettivo. | Proposta complementare alla 1. L'overmap conosciuta autorizza una categoria/località, non la pianta esatta di una casa. Sagome indicative esplicite, oppure nessuna sagoma se la conoscenza nativa non basta. Non generare dettagli reali di zone inesplorate per riempire il panorama. |

Raccomandazione: **1 + la parte compatibile di 4**, mantenendo per ora la
scala e la percezione di gameplay native. La fog può essere tenue nel campo
vicino e sfumare più lontano verso il limite della conoscenza disponibile.
Non serve scegliere tra una nebbia a 40 celle e assenza totale di transizione.
Meteo, notte e sensi possono richiedere una resa diversa: il panorama ricordato
non deve apparire come un mondo attualmente illuminato o osservabile.

Un primo confronto può regolare l'inizio/fine della nebbia entro la proiezione
disponibile. Serve a giudicare la resa, non risolve persistenza del panorama,
zone inesplorate o percezione; non va consegnato come soluzione completa.
Non aumentare direttamente MAPSIZE per questo scopo: una reality bubble più
grande comporta anche lavoro di simulazione, mentre qui serve prima separare
la distanza di presentazione da quella del mondo attivo.

## Memoria: infrastruttura esistente e lavoro mancante

CDDA ha già `avatar::player_map_memory`, con regioni persistenti di
`memorized_tile`: ID di terreno, decorazione, rotazioni/subtile e simbolo.
`game::save` e caricamento includono la memoria. È una base pertinente alla
proposta 1, ma non contiene già un modello 3D completo, timestamp di ogni
osservazione o stato di tutte le aperture, luci, oggetti e livelli sovrapposti.

Nel pin esaminato le chiamate che memorizzano gli ID di terreno/decorazione
sono nel renderer `cata_tiles`; la variante ASCII memorizza simboli in `map`.
Il runtime CWM usa `test_mode`, senza collegare l'export a quelle chiamate.
Occorre quindi verificare e, dove necessario, rendere la registrazione delle
osservazioni indipendente dal disegno nativo. **Non assumere che la memoria
grafica sia già popolata solo perché il save nativo esiste.** Conservare i
vecchi ricordi importabili, senza ricostruirli leggendo il terreno corrente
invisibile. Simboli legacy ambigui non autorizzano geometria dettagliata.

L'overmap ha celle di 24 × 24 caselle locali e informazioni di scoperta.
Scoprire una località sulla mappa non equivale a visitarne il cortile o
conoscere i piani. Anche una sagoma lontana deve usare soltanto attributi
conoscibili, evitando forma reale del tetto, loot, creature o stato corrente
dedotti da submap non osservate.

## Contratto proposto per il panorama

- **Osservato adesso:** terreno e attori autorizzati dai predicati nativi,
  rispettando luce, occlusione, sensi, livello e conoscenza delle singole
  componenti. Una finestra non rivela automaticamente tutto l'edificio.
- **Ricordato:** ultima osservazione statica, con provenienza e generazione
  di memoria CDDA. Non replica creature, loot, veicoli mobili, luci accese,
  fuoco o altri eventi correnti non percepiti. Eventuali ricordi nativi di
  elementi mobili non vanno disegnati come attori presenti. Una porta può
  restare graficamente aperta nel ricordo finché non viene osservata di nuovo.
- **Conosciuto soltanto sulla overmap:** categoria/sagoma indicativa, senza
  collisione, picking operativo o accesso a interni. Tenerla distinta dalla
  geometria ricordata esatta; una sagoma non diventa fonte di conoscenza nativa.
- **Ignoto:** nessun edificio o nemico reale esportato. Cielo/sfondo e
  transizione atmosferica possono dare continuità senza fingere terreno noto.
- Nessun input usa una cache lontana come autorità. Quando si entra in una
  zona, movimento/interazione richiedono lo stato CDDA corrente; i dati
  ricordati non autorizzano attraversamenti o tiri attraverso porte cambiate.
- Una cache Luanti resta eliminabile. La fonte persistente della conoscenza
  è CDDA; prima di scegliere nuovi campi o storage verificare estensione
  compatibile della memoria e lettura nativa del save. Non fissare un nuovo
  formato canonico soltanto per velocizzare il renderer.
- CWM distingue semanticamente osservazione/memoria e identità/versione del
  mondo/personaggio. Non trasporta MapNode o mesh. Gap di sequenza/reconnect
  richiedono ricostruzione dalla fonte autorevole; un vecchio ricordo non può
  essere presentato come sostituto di un delta mancante.
- Buffer del panorama limitati, caricamento anticipato delle zone **note**,
  livello di dettaglio ridotto in distanza e soglie diverse di ingresso/uscita
  per evitare continua comparsa/scomparsa. Misurare rete, meshing, memoria,
  frame time e latenza di input. Nessuna simulazione Luanti di entità lontane.

## Comparsa delle creature

La proposta di una transizione più dolce è da provare. Non mostrare anticipi,
ombre, suoni o sagome di creature non percepite per evitare un pop-in: sarebbero
informazione aggiuntiva. Il ramo `perceived` attuale è una base, non certifica
già la rappresentazione corretta di ogni senso speciale.

Una breve comparsa grafica **dopo** la percezione può attenuare il salto, ma
HUD, autopausa, collisione e attacco devono reagire subito allo stato nativo.
Vietare ritardi che rendano invisibile un attaccante già vicino; uscita dalla
percezione senza posizioni fantasma aggiornate. Provare soglie oscillanti,
angoli di muri, notte, velocità alte, sensi speciali e variazioni di latenza.
Orientamento, animazioni e occlusione corretti aiutano la leggibilità, ma non
eliminano da soli il problema delle soglie informative.

## Piattezza, alberi e aperture

La B attuale mostra un albero con un blocco di tronco e uno di chioma sopra il
pavimento: non è una conversione definitiva dell'altezza di un albero maturo.
Una priorità estetica più utile dei dossi casuali è una vegetazione con taglie,
tronchi, chiome e distribuzione riconoscibili, più un panorama abbastanza
ampio da mostrarla. Altezza grafica e quote dei piani vanno disaccoppiate con
cautela: chiome non devono cancellare tetti, ostruire un percorso superiore
legale o diventare riparo contro proiettili che CDDA non riconosce.

Il piano inferiore permanente delle finestre ordinarie è una proposta sensata:
parete/davanzale sotto, vetro o apertura sopra. Non basta scambiare un blocco,
perché il movimento attuale mantiene una quota visiva costante. La resa deve
mostrare il passaggio/vault quando la logica lo consente, anziché far passare
il corpo nel davanzale. Telaio, tende, barre e vetro rotto sono stati separati;
le vetrate a tutta altezza richiedono un'altra famiglia. Scale riconoscibili
devono derivare dalle connessioni native, non dal desiderio di salire a un
piano visibile.

Un dislivello di un cubo mantenendo CDDA perfettamente piatto non è soltanto
texture: può mostrare piedi sospesi, corpo dentro il terreno, falsa copertura,
tiro/picking incongruenti e problemi con veicoli o raccordi alle porte.
Non introdurlo al volo come soluzione definitiva. Prima provare dettagli
superficiali piccoli e decorativi, stabili sulle coordinate assolute, lontani
da strade, aperture, acqua e pericoli, senza cambiare percorsi o regole.
Ampiezza da scegliere nella scena, non già approvata. Se serve un vero gradino
percorribile, seguire il [contratto di rilievo](terrain-presentation.md) con
quote/regole autorevoli CDDA. Nessun test separato dei dossi richiesto ora.

## Ordine di lavoro e criteri di consegna

| Passo | Dipendenze / esito verificabile |
|---|---|
| Correzioni esplorative in FND-04 | Prima di nuove prove estese: riprodurre e risolvere abort acqua/menu; verificare famiglie di porte/finestre, distinzione guado/nuoto, scale e arredi leggibili. Conservare rebase e movimento già validati. |
| Promozione della resa B | Separare la selezione dello stile dalla fixture demo; materiali/vegetazione B disponibili nel gioco normale con fallback semantico. Non trasferire al mondo normale lo spawn disabilitato, il seed, il meteo o le restrizioni della fixture. |
| Fondazioni FND-02/03 | Framing/limiti, sessioni, revisioni, reconnect e resync prima di certificare una cache distribuita più ampia. Le diagnosi estetiche non completano queste fondazioni. |
| Percezione e registrazione nativa | Fixture giorno/notte, interno/esterno e multi-Z; definire cosa è osservabile e cosa viene memorato, inclusi termini delle connessioni mai visti. Prova su mondo nuovo e memoria nativa importata. |
| Panorama ricordato limitato | Un'area già osservata rimane visibile dopo uscita dalla bubble; nessun aggiornamento da modifiche occulte. Restart e cache Luanti eliminata ricostruiscono lo stesso ricordo dal save CDDA. |
| Distanza/LOD e fog più lontana | Stessa scena/ora, zona nota e ignota, skyline e bordi; variare separatamente distanza e haze. Misure su renderer reale e confronto manuale nell'ambito della fase 2. Nessuna distanza promessa prima di misurare. |
| Alberi e dettaglio naturale | Taglie/chiome coerenti, confini multi-Z e raccordi. Eventuale dettaglio superficiale incluso nel confronto generale, se utile; rilievo percorribile resta decisione distinta. |

Prove essenziali del panorama: porta modificata fuori vista conserva il vecchio
ricordo; nuova osservazione lo aggiorna; finestre/interiori mai visti restano
ignoti; creatura oltre percezione non compare; uscita/rientro dalla bubble non
produce flash; save/load/reconnect non inventano dati; rimozione della cache
Luanti non elimina conoscenza canonica. Includere occlusione, buio, sensi e
memorie parziali. Il successo della B estetica non è evidenza di queste prove.

## Sorgenti consultate

- [Export semantico e snapshot CDDA](../../cdda/src/cwm/cwm_map_exporter.cpp):
  classificazione, bounds e `sees` degli attori.
- [Bridge Luanti](../../luanti/src/cdda/cdda_bridge.cpp): `place_cdda_tile`,
  sostituzione della proiezione e `terrainFogDistance`.
- [Disegno della fog](../../luanti/src/client/game.cpp): `Game::drawScene`.
- [Memoria nativa](../../cdda/src/map_memory.h),
  [avatar](../../cdda/src/avatar.cpp), [tile renderer](../../cdda/src/cata_tiles.cpp),
  [map ASCII](../../cdda/src/map.cpp) e [save/load](../../cdda/src/game.cpp).
- [Overmap](../../cdda/src/overmapbuffer.h) e
  [scale delle coordinate](../../cdda/src/coordinates.h).
- [Movimento/acqua](../../cdda/src/avatar_action.cpp),
  [runtime headless](../../cdda/src/cwm/cwm_main.cpp),
  [finestre native](../../cdda/data/json/furniture_and_terrain/terrain-windows.json),
  [porte](../../cdda/data/json/furniture_and_terrain/terrain-doors.json) e
  [liquidi](../../cdda/data/json/furniture_and_terrain/terrain-liquids.json).

Questa revisione documenta feedback e progetto. Non cambia codice, binari,
salvataggi o la distanza visiva attuale. FND-04 completo, SAVE-001 e il gate
M5.5 restano aperti; il gate storico resta FAILED.
