# Piano completo CDDA–Luanti

Piano corrente, aggiornato con i 15 questionari del 2026-10-04.
Le [decisioni dettagliate](docs/source/feature-decisions-2026-10-04.md) e il loro
[registro strutturato](docs/source/feature-decisions-2026-10-04.json) integrano
specifica v1.0, emendamenti v1.1 e direttiva di scope del 2026-10-03.
Il successivo [riscontro sul terreno](docs/source/terrain-feedback-2026-10-04.md)
approva i materiali/vegetazione B, riapre alcuni casi esplorativi e richiede
un panorama più ampio; nebbia, memoria distante e rilievo restano da scegliere.
Lo [stato implementato](IMPLEMENTATION_STATUS.md) e le evidenze restano separati
dagli obiettivi. La roadmap originale M0–M9 conserva i propri significati.

## Prodotto e autorità

Profondità CDDA completa, interfacce guidate e dettagli manuali progressivi.
CDDA integrato possiede gameplay, spazio autorevole, tempo e salvataggi; Luanti
presenta e raccoglie intenzioni; Mineclonia fornisce asset di presentazione.
Gli upstream possono essere cambiati per servire il prodotto collettivo.
Estensioni spaziali autorizzate, con differenze documentate, test pertinenti e
prove giocabili dell'utente. L'interpolazione non anticipa lo stato autorevole.

## Fase 1 — Fondazioni prima delle nuove feature

Seguire il [piano di remediation](docs/audits/M5.5-remediation.md), conservando
le riparazioni già completate a visibilità, strutture e movimento.

| Task | Risultato verificabile | Stato |
|---|---|---|
| FND-01 | Distinguere nuova partita e caricamento; mantenere identità, inventario, posizione, orologio e mondo. Comandi e verifiche headless usano il ciclo nativo completo. | IMPLEMENTED — verifica mirata PASS; SAVE-001 completo in FND-05 |
| FND-02 | Framing e code limitati; EOF, framing/FlatBuffers strutturalmente invalidi e client lento sono contenuti. I/O non bloccante e lavoro limitato per aggiornamento. | IMPLEMENTED — verifica mirata PASS; [evidenze](docs/fixes/fnd02-transport.md) |
| FND-03 | Negoziazione, identità di sessione, deduplicazione, revisioni, sequenze, reconnect/resync e abilitazione dell'input su stato completo. | IMPLEMENTED — verifica mirata PASS; [evidenze](docs/fixes/fnd03-session-recovery.md) |
| FND-04 | Entità reali persistenti, picking, verticalità, campi, luce/percezione e HUD autorevoli; lifecycle e threading verificati. | IN PROGRESS: rebase, creature base, decisioni native, OPEN/CLOSE, aperture/acqua, [connessioni verticali native](docs/fixes/fnd04-vertical-navigation.md) e [identità/ciclo di vita degli attori](docs/fixes/fnd04-actor-lifecycle.md) implementati con verifica mirata; copertura incompleta |
| FND-05 | SAVE-001 completo, test discovery, licenze/media e benchmark popolati riproducibili; nuova certificazione M5.5 soltanto dopo le evidenze. | PLANNED |

FND-01 applica il preset CDDA raccomandato ai nuovi mondi e conserva mod/opzioni
dei mondi esistenti. Selezione esplicita se esistono più personaggi; niente
sovrascrittura silenziosa. Il ciclo comandato dalle azioni è un passaggio
tecnico verso il tempo reale approvato, non il comportamento finale del prodotto.
Implementazione ed evidenze in [FND-01](docs/fixes/canonical-runtime.md).
Il [riscontro manuale](docs/source/manual-validation-2026-10-04.md) accetta
movimento, strutture, apertura porte, safe mode e riavvio. Dopo la
[riparazione](docs/fixes/rebase-and-threat-presentation.md), accetta anche
sfarfallio assente/impercettibile, zombie visibili e morte da zombie senza
crash. Il pozzo/bordo resta da riprovare manualmente. Questa riparazione
anticipa parte di FND-04; animazioni/orientamento e copertura completa restano
aperti. FND-02 e FND-03 sono implementati con verifica mirata; il prossimo
task di fondazione è completare FND-04. Il nuovo abort nell'acqua e le varianti
di porte/finestre segnalate nel [riscontro sul terreno](docs/source/terrain-feedback-2026-10-04.md)
sono stati affrontati nella [riparazione esplorativa](docs/fixes/exploration-apertures.md):
avviso degli oggetti vulnerabili tramite UI esterna, stati derivati dalle
transizioni native, davanzale persistente e OPEN/CLOSE puntati. Restano i
limiti e la nuova verifica manuale indicati nel report.
La [validazione manuale successiva](docs/source/exploration-validation-2026-10-04.md)
accetta OPEN/CLOSE puntati, B normale, ingresso/uscita nell'acqua e avviso degli
oggetti vulnerabili. Posizione e stati delle aperture persistono anche dopo
allontanamento oltre la proiezione, quit/load e ritorno. Nei casi provati la
riparazione è accettata; non serve ripetere la stessa checklist prima di
FND-03, ora verificato. Puntamento sul davanzale funzionale, ergonomia ancora da valutare:
proposta di selezione dell'intera apertura con evidenziazione/azione esplicita,
occlusione e portata native, senza collisioni aggiunte.
L'accettazione delle strutture nei casi precedenti non copre queste anomalie.
FND-04 ora include OPEN/CLOSE puntati senza attraversamento; la fase 2
comprende una nebbia del confine della proiezione che non sveli terreno ignoto.
Su richiesta dell'utente, il [confronto del terreno](docs/prototypes/terrain-comparison.md)
è stato anticipato come prototipo isolato: A/B nella stessa scena nativa e
nebbia ON/OFF separata, tramite `terrain-demo.sh`. L'utente ha approvato B
per materiali/vegetazione; B è ora attiva nel gioco normale, separando stile e
fixture e conservando le opzioni native del mondo caricato. La nebbia attuale
non è approvata come soluzione definitiva. La
[proposta su distanza e memoria](docs/design/visibility-and-world-memory.md)
conserva le alternative e raccomanda panorama statico ricordato, dettaglio
ridotto lontano e haze al confine effettivo. La raccomandazione non è ancora
una scelta dell'utente né un'implementazione; la fase 2 resta aperta.

FND-04 deve inoltre distinguere stato del vetro/telaio/davanzale e
attraversabilità nativa, coprire famiglie open/closed/locked/broken delle
porte, adattare i menu nativi di ingresso in acqua e presentare guado/nuoto,
arredi e connessioni verticali riconoscibili. Non correggere placeholder
aggiungendo collisioni o scale indipendenti da CDDA. Riproduzione isolata e
verifica della causa precedono l'attestazione di ogni fix.

FND-03 usa CWM 2.0: Hello compatibile prima dello stato, identità distinte,
sequenze per connessione, registro limitato dei comandi e resync completo
con conferma dello snapshot. `start.sh` è l'unico supervisore, anche per gli
alias compilati. Le regressioni includono il client grafico reale, salvataggi
isolati, input/camera e menu nativi. Non occorre ripetere le validazioni
manuali già accettate; M5.5 completo rimane FAILED e SAVE-001 resta in FND-05.
I dettagli e i binari installati sono nel [report FND-03](docs/fixes/fnd03-session-recovery.md).

L'utente [valida la checklist FND-03](docs/source/fnd03-manual-validation-2026-10-04.md)
e autorizza il seguito. Restano a priorità bassa porte con stato visivo
invertito, soprattutto in strutture di pietra, e il perno centrale di un'anta
nelle porte doppie. Il [passo sulle connessioni verticali](docs/fixes/fnd04-vertical-navigation.md)
è implementato e verificato: scale/scale a pioli riconoscibili, salita/discesa
contestuali native e immersione/emersione, un passaggio per pressione.
`vertical-demo.sh` offre la prova isolata, riprendibile dopo quit/load;
l'utente [accetta tutti e quattro i test e la transizione visiva](docs/source/vertical-validation-2026-10-04.md).
Non servono altre prove manuali per accettare questo passo. Non finalizza
il controller continuo né lo scheduler della fase 2 e non chiude l'intero FND-04.

Il seguito autorizzato consolida [creature e NPC](docs/fixes/fnd04-actor-lifecycle.md):
identità canoniche, ingresso/uscita dall'area simulata, riconnessione, salvataggio
e caricamento, cambio di modello e rimozione effettiva delle mesh. `actor-demo.sh`
offre una prova isolata riprendibile. La visibilità resta CDDA; alla ricomparsa
non si anima il percorso non osservato. Animazioni, AI in tempo reale, dialoghi,
scambi e luce locale restano nei task previsti. La prova manuale di questa nuova
consegna resta da svolgere; quelle precedenti rimangono accettate.

## Fase 2 — Prototipo di tempo, movimento e percezione

Dipende da FND-01–03 e dalla proiezione sufficiente alla scena di confronto.

- Scheduler unico CDDA: default 1:1 e velocità globale regolabile, pausa
  esplicita/menu, attività lunghe accelerate, interruzioni native rilevanti.
- Autopausa su nuova minaccia percepita; ripresa in tempo reale. Verificare
  fattibilità del combattimento opzionale scandito dalle azioni sullo stesso
  scheduler. La pausa di scelta non migliora gratuitamente la mira.
- Due prototipi: griglia nativa interpolata e tile + offset continuo autorevole
  CDDA, con orientamento naturale, arresto interno e accumulo dei costi senza
  riaddebitare il passo al confine o alterare arbitrariamente il calendario.
- Confrontare walk/run/crouch/prone, diagonali, porte/finestre/muri, strettoie,
  scale/bordi, arrampicata/salti, acqua e taglie differenti. Investigare il costo
  effettivo del salto `iexamine::ledge` prima di adattarlo.
- Quando il primo prototipo di scheduler in tempo reale sarà giocabile,
  ricordare all'utente di rivalutare la salita/discesa automatica e continua
  sia delle scale a gradini sia delle scale a pioli. Includerle nella prova
  prima di scegliere il controller definitivo: la transizione attuale è
  accettata provvisoriamente, la preferenza per il tempo reale è da confrontare.
  Riferimento: [validazione e promemoria](docs/source/vertical-validation-2026-10-04.md).
- Portata e ostacoli coerenti con geometria visibile; inizialmente esigere
  legalità nativa e coerenza geometrica. Estensioni ulteriori documentate.
- Percezione CDDA indipendente dal cono camera; indizi periferici/sonori con
  conoscenza e incertezza native. Luce e sensi speciali coerenti.
  Coprire il caso manuale dell'NPC visibile solo da vicino in una stanza
  chiusa/buia: luce locale e sorgenti/occlusione CDDA devono rendere leggibile
  la perdita di percezione, oltre alla luce naturale semplificata per piano.
  Per l'immersione, confrontare superficie/volume, camera e tinta/attenuazione
  riconoscibili anziché nero privo di contesto. Entrambi registrati per la
  prova più ampia, conservando la visibilità autorevole degli attori.
- Separare distanza di presentazione, realtà simulata e conoscenza. Il
  [contratto proposto](docs/design/visibility-and-world-memory.md) distingue
  terreno osservato, memoria statica e overmap nota. Verificare/popolare la
  memoria nativa anche in headless; non conservare come ricordo tutti i tile
  del bridge corrente, che include terreno non filtrato dalla percezione.
  Prototipare panorama ricordato con cache limitate, dettaglio ridotto,
  restart/reconnect e assenza di aggiornamenti occulti. Nessuna creatura
  lontana resa visibile per attenuare il pop-in; eventuale breve transizione
  dopo percezione non ritarda avvisi/attacchi. Fog e distanza sono controlli
  distinti da confrontare, con prestazioni misurate e scelta manuale finale.
- Terreno: definire ora il contratto e confrontare in questa fase una scena
  più ricca (nebbia del bordo, materiali, vegetazione) con le necessità di
  rilievo giocabile, prima di consolidare veicoli/combattimento/costruzioni.
  Materiali/vegetazione B sono scelti come direzione; distanza/nebbia, alberi
  maturi e rilievo restano da sviluppare secondo la
  [proposta aggiornata](docs/design/terrain-presentation.md). Pianura cittadina
  e costiera accettabile; dettaglio naturale e skyline da migliorare.
  Piccole irregolarità facoltative in una prova più ampia, senza test manuale
  dedicato; nessun gradino di un cubo soltanto grafico assunto innocuo.
  Il successivo riscontro trova la piattezza molto meno evidente con B:
  rinviare rilievo e prototipi di dossi fino a dettagli grafici sufficienti;
  rivalutare allora la necessità, senza una nuova worldgen nel prossimo task.
  Rilievi percorribili richiedono quote e regole autorevoli CDDA, non colline
  autonome Luanti. Nessuna nuova generazione del mondo è stata scelta.
- Animazione e orientamento delle creature coerenti con stato, movimento e
  cronologia simulata; pose leggibili anche in pausa. La visibilità base già
  validata non certifica animazioni, AI in tempo reale o bestiario completo.

Consegna: scene ripetibili, controlli selezionabili, misure di pacing/latency,
differenze da CDDA pinned e prova dell'utente. La scelta finale del movimento
dipende da quella prova e non può essere decisa silenziosamente dall'agente.

## Fase 3 — M6, veicoli

Conformance prima del rilascio delle nuove feature. IDs semantici stabili di
mezzo/parti, trasformazioni, geometria, passeggeri, porte, ruote, danni, despawn
e save/load. Comandi attraverso il coordinator comune e risultati atomici.

Confrontare guida nativa interpolata e continua autorevole CDDA in scene di
svolta, retromarcia, collisione, aderenza e abilità. L'utente sceglie dopo prova.
Officina con puntamento e vista a strati dei componenti sovrapposti, requisiti
e lavori temporizzati. Ordine: terra, acqua, volo; tutte le categorie previste,
certificazione separata per quelle effettivamente verificate.

## Fase 4 — M7, interfacce e ciclo completo

Ordine per dipendenze:

1. Interazioni: azione rapida, ruota stabile, lista completa, shortcut; query
   CDDA di disponibilità, requisiti, costo ed esito.
2. Inventario/abbigliamento: categorie/ricerca, tasche avanzate, doppio pannello,
   quantità e accesso, attività interrompibili e regole native.
3. Corpo/medicina: HUD essenziale e dettagli, diagramma corporeo, selezione
   esplicita di oggetto/parte e spiegazioni conoscibili.
4. Crafting/lettura/lavorazioni: ricette note, componenti concreti confermati,
   fonti/utensili, sottoricette collegate, batch manuali e progresso.
5. Combattimento: melee puntato, difese native, mira assistita predefinita e
   mirino libero configurabile sullo stesso sistema balistico CDDA.
6. Mappe/missioni/NPC: mappe note/minimappa, diario, dialoghi completi e prove,
   commercio, compagni con profili e tutte le regole individuali.
7. Base: anteprime, progetti multi-casella, zone con lavoro effettivo, reti
   energetiche e gestione accampamenti/spedizioni/ampliamenti.
8. Creazione/progressione: percorso guidato ed editor completo, abilità e
   competenze, mutazioni/bionica complete e corpo coerente.

CWM richiede query/comandi semantici per item location, inventari, bersagli,
attività, corpo, ricette, dialoghi/scambi, NPC/zone/costruzioni, abilità e tempo.
La GUI non modifica gli inventari Luanti. Le query non riapplicano effetti;
conferme identificano il contesto e producono un unico risultato anche dopo
ritrasmissione. Le scelte native bloccanti su terminale diventano decisioni
esplicite coordinator/UI, mantenendo validazione e risoluzione in CDDA.

Bestiario base ampio con modelli per famiglie e varianti distinguibili;
vestiti/equipaggiamento riconoscibili per categoria inizialmente. Coltivazione,
animali, pesca, cibo, cadaveri, scasso, trappole, campi, liquidi e terminali
usano le interfacce comuni mantenendo regole, requisiti e tempi nativi.

## Fase 5 — M8/M9 e contenuti successivi

Misurare sim, code/delta, meshing, entità visibili, input-to-visual e risorse
nelle scene BM01–BM06. Ottimizzare colli misurati, verificare regressioni.
Packaging Linux/Windows, licenze, avvio, aggiornamenti, save/crash recovery su
ambiente pulito. Grandi mod selezionate dopo il gioco base, con matrice delle
capacità e prove specifiche: caricare JSON da solo non certifica compatibilità.
Preservare infrastruttura EOC/spell, usata anche da mutazioni e bionica native.

## Confini e verifica

Esclusi dalle scelte attuali: costruzione arbitraria per singolo cubo, nuova
fluidodinamica voxel, nuova schivata/parata universale, produzione automatica
delle sottoricette e recupero aggiuntivo post-morte. Save/morte/world-end seguono
opzioni native rese esplicite alla creazione. Single-player iniziale, protocollo
predisposto al futuro multiplayer previsto dalla specifica.

Ogni task registra sorgenti ricostruibili, test pertinenti, risultati e limiti.
Test su salvataggi isolati, confronto di effetti/costi autorevoli oltre agli ACK.
Verificare restart/reconnect, interruzioni, informazioni nascoste, contenitori
annidati, frame rate e refresh/ritrasmissioni delle schermate. Il M5.5 storico
resta FAILED finché un nuovo audit completo non soddisfa tutti gli invarianti.
