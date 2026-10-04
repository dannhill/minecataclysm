# Piano completo CDDA–Luanti

Piano corrente, aggiornato con i 15 questionari del 2026-10-04.
Le [decisioni dettagliate](docs/source/feature-decisions-2026-10-04.md) e il loro
[registro strutturato](docs/source/feature-decisions-2026-10-04.json) integrano
specifica v1.0, emendamenti v1.1 e direttiva di scope del 2026-10-03.
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
| FND-02 | Framing e code limitati; EOF, input malformato e client lento non bloccano o terminano il runtime. | PLANNED |
| FND-03 | Negoziazione, identità di sessione, deduplicazione, revisioni, sequenze, reconnect/resync e abilitazione dell'input su stato completo. | PLANNED |
| FND-04 | Entità reali persistenti, picking, verticalità, campi, luce/percezione e HUD autorevoli; lifecycle e threading verificati. | IN PROGRESS: geometria/input, rebase, creature base e decisioni native; copertura incompleta |
| FND-05 | SAVE-001 completo, test discovery, licenze/media e benchmark popolati riproducibili; nuova certificazione M5.5 soltanto dopo le evidenze. | PLANNED |

FND-01 applica il preset CDDA raccomandato ai nuovi mondi e conserva mod/opzioni
dei mondi esistenti. Selezione esplicita se esistono più personaggi; niente
sovrascrittura silenziosa. Il ciclo comandato dalle azioni è un passaggio
tecnico verso il tempo reale approvato, non il comportamento finale del prodotto.
Implementazione ed evidenze in [FND-01](docs/fixes/canonical-runtime.md).
Il [riscontro manuale](docs/source/manual-validation-2026-10-04.md) accetta
movimento, strutture, apertura porte, safe mode e riavvio, ma lascia aperta
la stabilità grafica durante i cambi di origine della reality bubble.
Prima di proseguire FND-02: riparazione mirata di rebase, creature visibili e
conferme native esplorazione/morte, come anticipo parziale di FND-04.
La [riparazione](docs/fixes/rebase-and-threat-presentation.md) ha prove mirate
PASS; resta da confermare manualmente la scena che sfarfallava.
FND-04 comprende anche OPEN/CLOSE puntati senza attraversamento; la fase 2
comprende una nebbia del confine della proiezione che non sveli terreno ignoto.

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
- Portata e ostacoli coerenti con geometria visibile; inizialmente esigere
  legalità nativa e coerenza geometrica. Estensioni ulteriori documentate.
- Percezione CDDA indipendente dal cono camera; indizi periferici/sonori con
  conoscenza e incertezza native. Luce e sensi speciali coerenti.

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
