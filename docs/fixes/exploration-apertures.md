# Riparazione esplorativa: acqua, aperture e terreno B

Richiesta: procedere con le correzioni segnalate nella
[prova del terreno](../source/terrain-feedback-2026-10-04.md), prima delle
fondazioni di trasporto FND-02/03. Branch `fix/exploration-apertures`.
Sorgenti, binari, comandi e risultati sono nel
[registro delle evidenze](exploration-apertures-evidence.json).

## Comportamento implementato

Il server installato precedente abortisce entrando nella fixture d'acqua
profonda con un oggetto esposto vulnerabile: il menu degli oggetti richiedeva
input da terminale in modalità headless. La nuova versione presenta la stessa
lista nativa di oggetti dissolti, distrutti o bagnati tramite decisione CWM.
No, disconnessione o arresto durante la scelta non autorizzano l'ingresso.
Yes esegue il nuoto e gli effetti sugli oggetti originali CDDA. Anche l'avviso
di mancanza d'ossigeno usa una decisione esterna. Non è stata ricostruita la
partita esatta del laghetto segnalato dall'utente: è verificata questa causa
concreta di abort, non una diagnosi di ogni possibile uscita nell'acqua.

Le aperture derivano stato visivo e attraversabilità separatamente dai dati
CDDA. Una porta aperta può conservare il flag DOOR; una finestra chiusa
rinforzata può avere costo di movimento positivo e una transizione OPEN.
Questi casi non vengono più confusi con chiuso/aperto rispettivamente.
Sono riconosciute anche le varianti di tende su finestre vuote prive di WINDOW.
Il catalogo nativo e le transizioni reali di famiglie porte/finestre sono
coperti dai test. Nel pin la porta interna del rimorchio è aperta ma ha
`move_cost=0`: resta un ostacolo visibile sulla soglia, senza cambiare la regola
CDDA o far sembrare libero un passaggio bloccato.

La finestra ordinaria ha parete/davanzale sotto e vetro sopra. OPEN toglie solo
il vetro; CLOSE lo ripristina. La camera segue indicazioni native di passaggio
finestra, guado, nuoto e immersione. Gli offset sono interpolati soltanto nella
presentazione; coordinate Z, costi e orologio CDDA rimangono invariati. Non è
un'animazione completa del corpo o un nuovo sistema di arrampicata.

Il puntamento usa tutti e tre i nodi del piano corretto, anche ai livelli Z
negativi. Clic destro invia OPEN; il comando Sneak tenuto premuto, normalmente
Shift sinistro, più clic destro invia CLOSE. Per chiudere un'apertura vuota
si punta il davanzale o il pavimento della sua casella. La validazione richiede
adiacenza e stesso piano in CDDA, che paga il costo dell'azione. Gli input
aspettano ACK e stato autorevole; i callback Luanti di scavo/posa non modificano
la proiezione. La barra Luanti non diventa un inventario CDDA con questa modifica.
La configurazione del gioco esclude il controllo Luanti della velocità di
movimento, che altrimenti segnalava `moved too fast` sulle posizioni governate
da CDDA; conserva gli altri controlli di scavo/interazione.

I materiali/vegetazione **B**, approvati dall'utente, sono attivi in `start.sh`.
Lo stile è separato dalla fixture del confronto: non importa seed, spawn
disabilitati, meteo o nebbia corta nella partita normale. La cache aggiuntiva
per F7 resta riservata alla demo. La distanza, il panorama ricordato, gli
alberi maturi e il rilievo conservano le
[decisioni ancora aperte](../design/visibility-and-world-memory.md).

## Verifica e riproduzione

Tutti i mondi/config delle prove sono isolati in `artifacts/exploration-fix/`.
La fixture nasce da un lettore collegato al core CDDA pinned indipendente,
con acqua profonda a nord, bassa a sud, finestra a ovest e porta a est.
Il test modifica copie della fixture; il salvataggio dell'utente non è usato.

Le sorgenti sono ricostruite dai pin e dalle patch integrali e confrontate con
gli inventari catturati. Le build riusano oggetti verificati attraverso le
dipendenze del precedente confronto: **build incrementali, non cold-cache**.
Il registro identifica il workspace compilato, una ricostruzione indipendente
ulteriore, receipt del lettore e hash degli eseguibili installati.

Comandi principali, dalla radice del progetto:

```bash
python3 tools/takeover_baseline.py check
python3 tools/takeover_baseline.py reconstruct --destination <directory-nuova>
cmake --build artifacts/exploration-fix/workspace/cdda/build --target cdda-server cata_test --parallel 2
cmake --build artifacts/exploration-fix/workspace/luanti/build --target luanti --parallel 2
```

I comandi completi delle prove sono nel registro. La suite nativa acqua
verifica effetti, posizione assoluta dopo un rebase e costo del movimento:
un ACK positivo dopo No significa azione gestita e non prova uno spostamento.
Il client di test legge continuamente i frame, come il bridge; tolleranza
dei client lenti resta FND-02, senza nascondere i probe di trasporto falliti.

Le prove grafiche usano Luanti reale e `start.sh` normale, con il server
nativo: scelta No/Yes, nuoto/guado, passaggio sul davanzale, OPEN/CLOSE senza
spostamento, cambio del vetro e lettura indipendente del save. Le regressioni
di pacing/rebase usano un'autorità CWM sintetica e sono evidenze del renderer,
distinte dalle prove di gameplay CDDA. Il confronto A/B usa la fixture nativa.

| Prova | Esito |
|---|---|
| Riproduzione dell'abort sul server precedente | PASS, fixture indipendente |
| CDDA nativo `[cwm],[diving]` | 15 casi / 3.584 asserzioni PASS |
| Luanti nativo | 304/304 PASS |
| Protocollo Debug | 2/2 PASS |
| Acqua, aperture e salvataggio tramite IPC nativo | 42/42 PASS |
| `start.sh` normale con server nativo e GUI reale | 21/21 PASS |
| Pacing, vetro e risultato ritardato nel renderer | 48/48 PASS |
| Rebase nel renderer | 15/15 PASS |
| Confronto terreno nativo | 14/14 PASS |

I due binari verificati sono installati atomicamente nei percorsi di `start.sh`,
con copie precedenti e receipt conservati negli artifact.

## Prova manuale con `start.sh`

1. Cercare porte e finestre diverse: stato visibile coerente prima/dopo il
   passaggio, osservando anche dall'altro lato.
2. Puntare una porta/finestra vicina: clic destro per aprire, Shift sinistro
   tenuto premuto + clic destro per chiudere. Da aperta puntare anche in basso
   sul davanzale/pavimento. Non dovrebbe servire attraversarla.
3. Verificare che sotto la finestra resti la parete; attraversandola, la
   camera deve superare il davanzale e tornare all'altezza normale dopo.
4. Provare una riva e acqua bassa/profonda: annullare l'avviso quando presente,
   poi confermare. Controllare visuale di guado/nuoto, ritorno a terra e assenza
   dell'interruzione `shutting down`. La conferma può danneggiare oggetti
   secondo le regole native; la lista nell'avviso serve a scegliere.
5. Chiudere un'apertura, uscire e rientrare: verificare stato e posizione.
   Osservare B anche fuori dalla demo e segnalare eventuali nuovi salti grafici.

## Limiti e prossimo lavoro

Restano placeholder per arredi e varianti dettagliate di aperture; il davanzale
generico in mattoni non identifica ogni materiale originale. Finestre a tutta
altezza, inferriate, tende e vetro danneggiato richiedono asset/semantica più
specifici. Alcuni oggetti restano attraversabili perché lo sono in CDDA: non
sono state aggiunte collisioni Luanti per renderli artificialmente solidi.

Immersione/emersione comandate, accesso verticale completo, animazioni del
corpo e creature, scheduler in tempo reale, panorama distante e rilievo non
sono completati. Gli avvisi temporanei usano numeri; liste lunghe possono
superare lo spazio della GUI attuale e richiedono il futuro pannello completo.
Questa verifica non certifica tutte le condizioni d'acqua, equipaggiamento,
veicoli o ogni variante grafica del catalogo.

Il prossimo task di fondazione rimane **FND-02**, seguito da FND-03; panorama
ricordato e nebbia più distante vengono dopo il contratto di recovery.
**M5.5 storico resta FAILED; SAVE-001 completo resta incompleto.** Le prove
mirate di questa riparazione non ricertificano l'intero progetto.
