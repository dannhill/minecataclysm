# Rebase, creature e decisioni native — riparazione mirata

Codice: `c10633e6afb838a7e2f6114fedf95067c4f854c7`, branch
`fix/rebase-and-threat-presentation`. Fonte del task: il
[riscontro manuale](../source/manual-validation-2026-10-04.md).
Identità, comandi, binari e artefatti sono nel
[registro di verifica](rebase-and-threat-evidence.json).
Questa riparazione anticipa parte di FND-04; M5.5 resta FAILED.

## Sfarfallio

Il bridge usava coordinate locali della reality bubble. Al cambio di origine
spostava subito la camera di 12 caselle e riscriveva tutte le mappe locali;
il meshing asincrono mostrava per un intervallo la vecchia geometria dalla
nuova posizione. Il nuovo test riproduce sul client reale due cambi di origine
in movimento e uno da fermo: il vecchio binario fallisce tre controlli di camera.

La presentazione ora conserva l'origine della prima snapshot come riferimento.
Camera, terreno, creature, veicoli e conversione inversa delle interazioni
applicano insieme la differenza rispetto a quell'origine. CDDA conserva le
proprie coordinate e autorità. Il rebase non interrompe l'interpolazione.
Le snapshot complete vengono confrontate in questo riferimento: il bridge
aggiorna o rimuove soltanto i blocchi cambiati, conservando le mesh sovrapposte.
I modelli delle creature seguono anche l'offset grafico interno della camera Luanti.

L'indicatore prima chiamato IPC Latency misurava l'attesa del risultato di
un'azione, comprendendo simulazione, trasporto e ingestione dello stato. Ora
si chiama Action result; projection misura separatamente l'ingestione della
snapshot, non il meshing asincrono o il rendering completo. Non è una misura
di ping puro. I ritardi di trasporto/backpressure restano lavoro FND-02.

## Creature

Le registrazioni Lua esistevano, ma il bridge non istanziava le creature nella
scena. Ora crea modelli zombie e NPC dagli asset già estratti; gli altri tipi
usano un segnaposto magenta. Non ci sono AI, collisioni o spawn Luanti aggiuntivi.
Posizione e presenza provengono da CDDA. La rimozione dalla roster elimina
il modello; `perceived`, calcolato con i sensi CDDA, ne determina la visibilità,
indipendentemente dal cono della camera. I tipi cambiati sostituiscono il modello.

Gli ID dei mostri prima dipendevano dall'ordine dell'elenco e cambiavano quando
un altro mostro spariva. Il coordinator ora usa identità monotone associate
all'ownership nativa debole. Durano nel processo, non nel salvataggio CWM o
attraverso un riavvio. Gli NPC usano il proprio identificatore canonico in un
namespace distinto. La snapshot resta una roster completa: il flusso contiene
anche gli attori non percepiti e non è una certificazione del filtraggio del
protocollo. Il client li nasconde; privacy/registry/sessioni completi restano aperti.

## Conferme, bordi e morte

I log dell'utente mostrano aborti da input terminale in test mode, non una
chiusura pulita per morte. Sono distinti i percorsi di ledge e morte:

- Le domande native sì/no usano un provider di scelta, locale alla chiamata
  del ciclo nativo e ripristinato anche dopo eccezioni.
- Il menu del bordo conserva le opzioni native disponibili di salita/discesa,
  salto e caduta, con annullamento. Peek down e examine from above richiedono
  ancora la propria camera/interfaccia; non vengono sostituiti da una caduta.
- CWM pubblica testo, scelte e decision ID; il client risponde con una scelta
  numerata. Il server controlla ID e range e sospende la progressione simulativa
  finché riceve la risposta. Liste lunghe vengono paginate.
- I numeri sono gestiti prima della hotbar e del movimento. Un numero tenuto
  premuto non conferma una successiva domanda. Il movimento resta bloccato
  durante la scelta.
- La morte mostra un avviso e la politica del mondo, poi usa eventi, corpse,
  diario, salvataggi del mondo, graveyard e reset/delete/keep nativi. Deathcam
  conserva l'opzione nativa, con avanzamento a passi e uscita esplicita.
- Le schermate terminali di epitafio/epiloghi vengono omesse; le ultime parole
  sono vuote, non inventate. La GUI completa di fine partita resta M7.
- Chiudere il client davanti a una conferma pericolosa sceglie No/Cancel;
  davanti alla domanda di world-end conserva il mondo. La morte già avvenuta
  mantiene la politica nativa configurata. Non viene introdotto un recupero.
- L'interazione camminando contro un NPC non ostile viene rifiutata mentre
  la GUI del dialogo non è disponibile, anziché aprire un menu terminale.

Il minor dello schema è 2. La negoziazione non è ancora verificata: servono i
due binari aggiornati insieme. Altre interazioni/modalità terminali non sono
certificate da questa copertura.

## Verifica e limiti

Prove su sorgenti ricostruiti e salvataggi isolati; nessun mondo dell'utente
usato o modificato dai test. Il lettore indipendente usa il core pinned
upstream, con un nuovo parametro solo di fixture per costruire un bordo.
La fixture usa una variante nativa di open air che conserva l'apertura dopo
`add_roofs()`, invece di modificare il loader per adattarlo alla prova.

| Prova | Esito |
|---|---|
| CDDA nativo: fasi, scelte/RAII, sensi e identità dopo rimozione | 9 casi, 3.396 asserzioni PASS |
| Luanti nativo finale | 303/303 PASS |
| Rebase reale: due in movimento, uno da fermo, risposta ritardata | 15/15 PASS |
| Creature, percezione/despawn, modelli e numeri tenuti premuti | 18/18 PASS |
| Regressioni visive/input, diversi FPS e risposta di 650 ms | 48/48 PASS |
| Bordo, salvataggio dopo annullamento, morte e world policies | 40/40 PASS |
| Caricamento, save/restart e compatibilità canonica mirata | 40/40 PASS |
| Launcher reale con movimento e cache nativa | 8/8 PASS |
| Luanti reale → CDDA → lettore nativo indipendente | 11/11 PASS |
| Protocollo Debug | 2/2 PASS |

La regressione canonica 40/40 è stata eseguita prima degli ultimi ritocchi
all'input numerico, ai testi/paginazione delle scelte e agli ID senza cache;
non certifica il binario finale. Lifecycle nativo, launcher e salvataggio dal
client 3D sono stati verificati di nuovo sui binari finali.

La prova della scena di rebase non riproduce ogni edificio o percorso reale:
il [secondo riscontro manuale](../source/manual-validation-2026-10-04.md)
accetta per ora sfarfallio assente/impercettibile, zombie visibili e morte
da zombie senza crash. Il pozzo/bordo non è stato riprovato manualmente.
Questa conferma successiva integra il registro di verifica automatico, che
conserva il contesto originale precedente alla prova dell'utente. I test
grafici usano una sorgente CWM controllata; native CDDA e launcher reale hanno
prove separate. Le identità dei fork nel workspace compilato corrispondono
all'inventario finale; una ricostruzione separata conferma la riproducibilità.
Build incrementali con riuso verificato delle dipendenze, non cold-cache.

Restano il confine della proiezione con nebbia, OPEN/CLOSE puntati, bestiario
completo, percezione/HUD/campi/verticalità estesi e tutte le interfacce M7.
Il riferimento grafico fisso usa ancora coordinate nodo a 16 bit: viaggio
molto lungo e riallineamento del renderer devono essere verificati nei
benchmark successivi. Tempo reale/prototipi di movimento e guida restano nel
piano approvato; nessuna scelta definitiva è stata fatta.
FND-02/03 e SAVE-001 completo non sono certificati da questi risultati.
