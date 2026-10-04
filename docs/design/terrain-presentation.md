# Terreno 3D: proposta prima delle feature che dipendono dalla geometria

Fonte: [seconda prova manuale](../source/manual-validation-2026-10-04.md).
Stato: punti 1 e 2 autorizzati dall'utente e realizzati nel
[prototipo di confronto](../prototypes/terrain-comparison.md). La
[prova manuale successiva](../source/terrain-feedback-2026-10-04.md) approva B
per materiali/vegetazione, ma trova troppo corta la distanza della nebbia.
B è ora attiva anche nel gioco normale: [implementazione e limiti](../fixes/exploration-apertures.md).
Distanza, alberi maturi, dettaglio superficiale e rilievo percorribile restano
da sviluppare. Le alternative e il contratto di memoria sono nella
[proposta su panorama e conoscenza](visibility-and-world-memory.md).
Il problema va definito adesso; il confronto giocabile appartiene alla fase 2,
prima di consolidare guida, combattimento e costruzioni. FND-02/03 restano le
prossime fondazioni da implementare.

Nel [riscontro dopo la riparazione](../source/exploration-validation-2026-10-04.md)
l'utente valida B nel mondo normale e nota molto meno la piattezza. Rilievo
e prototipi di dossi sono rinviati almeno fino a dettagli grafici sufficienti.
La voce facoltativa sul dettaglio superficiale sotto resta una possibilità
futura, non lavoro da introdurre nel prossimo task.

## Quanto dipende dal bridge corrente

Nel codice `c10633e`, `CwmMapExporter::export_block()` distingue materiali
generici usando flag e alcuni nomi di terreno. Erba e asfalto hanno categorie
dedicate; molti altri terreni ricadono in DIRT, i pavimenti in FLOOR e gli
ostacoli in categorie comuni. Non viene ancora esportata l'identità semantica
completa di terreno e arredo per scegliere un aspetto specifico.

`CddaBridge::place_cdda_tile()` rappresenta ogni livello con pavimento e due
celle superiori; `project_position()` assegna quota `z_level * 3`. Dentro uno
stesso livello il piano calpestabile ha quindi quota uniforme. Il mondo CDDA
possiede già livelli verticali: la pianura osservata non significa che scale,
tetti, aperture e sottosuolo siano privi di verticalità.

`get_node_for_material()` e `game/mods/cdda_nodes/init.lua` associano materiali
generici a pochi nodi/texture: amplificano la monotonia. Arricchire questa
traduzione può migliorare molto la scena, ma non genera colline percorribili.
La nebbia può nascondere la fine della proiezione; non risolve da sola la
geometria piatta.

## Confronto proposto

| Variante | Risultato e costo | Condizione |
|---|---|---|
| Presentazione più ricca | Nebbia del bordo, materiali fedeli, variazioni stabili, vegetazione e asset per famiglie di arredi/ostacoli. Intervento circoscritto. | Nessun nuovo percorso, riparo o ostacolo indipendente dalla simulazione. |
| Dettaglio superficiale | Piccole irregolarità decorative entro un limite da scegliere nella scena di prova. Più complesso per piedi, picking e silhouette. | Non introdurre una salita/discesa, alterare portata o nascondere aperture/pericoli. |
| Rilievo percorribile | Colline, avvallamenti e raccordi reali. Intervento architetturale e sui dati del mondo. | Quote autorevoli in CDDA integrato, condivise da attori, percorsi, interazioni e persistenza. |

La prima variante è stata provata e scelta per i materiali/vegetazione B.
La pianura cittadina/costiera è accettabile, quella naturale resta poco
credibile; campo visivo e alberi piccoli amplificano il problema. Sviluppare
prima panorama e vegetazione matura. Dettaglio superficiale opzionale in una
prova più ampia, senza test dedicato richiesto ora. Un gradino grafico di un
cubo può alterare piedi, visuale e copertura anche conservando la logica
piatta: non introdurlo come modifica innocua. Se servirà rilievo percorribile,
confrontarlo con il contratto sotto. Non attivare un mapgen autonomo Luanti
che inventi colline sopra la mappa CDDA.

## Contratto prima del rilievo percorribile

Verificare prima quali dislivelli/raccordi si possano esprimere con terrain e
livelli nativi del pin; documentare le estensioni necessarie senza imporre la
preservazione standalone. Il prototipo dovrà specificare:

- Quota della superficie e raccordi, distinte dai piani degli edifici. Fonte
  dei dati, generazione deterministica e trattamento dei mondi esistenti.
- Posizione/piedi degli attori, camera e conversione inversa del puntamento;
  porte, strade, ponti, acqua e scale devono raccordarsi senza compenetrazioni.
- Legalità e costo di movimento, pathfinding, cadute, percezione e tiro.
  Il rilievo visibile non deve inventare riparo o portata inesistenti in CDDA.
- Ruote, contatto e collisioni dei veicoli; costruzioni, scavi/demolizione e
  aggiornamenti del terreno. Nessuna deformazione solo grafica persistente.
- Dati semantici CWM, delta/rebase/reconnect e save/load canonici con eventuale
  versione/migrazione esplicita; nessun formato Luanti nel protocollo.

La possibilità di modificare CDDA per il prodotto è già autorizzata. B è
approvata per materiali/vegetazione; rilievo e suoi effetti sulle meccaniche
restano da discutere e provare. Worldgen e trattamento dei salvataggi esistenti
faranno parte di un'eventuale variante di rilievo scelta. Questa nota non
finalizza nebbia, distanza o nuova generazione al posto dell'utente.

## Scene e criteri di prova

Confrontare la stessa zona, luce e distanza di visualizzazione: strada con
edifici, campo aperto, bosco, margine d'acqua e scala/bordo. Varianti estetiche
devono essere stabili attraverso rebase e reload. Controllare anche nemici
vicini, porte/finestre e pericoli: la nebbia non deve cancellarli o mostrare
informazioni non disponibili. Distinguere bordo della proiezione, percezione
attuale e terreno ricordato; la fog visiva non definisce da sola la conoscenza.

Per un prototipo di rilievo aggiungere salita/discesa, tiro sopra un dosso,
percorso NPC, transizione strada/edificio e ruote. Misurare costo di meshing,
frame time e latenza d'azione. Esito richiesto: geometria leggibile e coerente,
senza regressioni a rebase/save/load, e confronto manuale dell'utente prima
di fissare la soluzione.

## Tempo e creature: segnalazioni separate

Il coordinator corrente aspetta comandi in `CwmServer::advance_turn()`;
le creature non avanzano mentre il giocatore aspetta l'input. È una fase
tecnica temporanea, non il default finale: la fase 2 prevede uno scheduler
CDDA unico, tempo reale con pausa e ritmo 1:1 regolabile.

Il bridge fissa i modelli al frame 0 con velocità di animazione 0; l'export
di mostri/NPC usa rotazione 0. Animazione, orientamento e attacchi distinguibili
restano lavoro di presentazione. La loro cronologia dovrà seguire il tempo
simulato e la pausa; non simulare l'AI autonomamente in Luanti.
