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

## Smontaggio nativo e chiarimento NPC — 2026-10-22

Fetta implementata: smontaggio di singoli oggetti posseduti tramite la vera
ACT_DISASSEMBLE, progresso dell'incompleto, conferme, pausa, interruzione,
ripresa e persistenza canonica. [Contratto](docs/design/native-disassembly.md).
[Consegna verificata](docs/fixes/native-disassembly.md): 120 casi nativi,
309 client, 14 protocollo e 48 controlli grafici/canonici PASS. Coppia CWM2.27
installata nel normale start.sh Linux; nessuna certificazione globale.
Quattro prove DIS-01 rinviate nel
backlog, precedenti 33 invariati; nessuna accettazione umana inferita.
Pile, liquidi e operazioni ricorsive restano separati. Il pacchetto Windows
consegnato il 21 ottobre rimane una fotografia CWM2.26 fino a un nuovo rebuild.

Chiarimento richiesto dall'utente: gli NPC sono visualizzati, ma i dialoghi
NPC non sono implementati; il runtime rifiuta esplicitamente l'interazione.
I PASS dei “dialoghi nativi” precedenti sono conferme di attività, non
conversazioni. Dialoghi, missioni e commercio restano Fase4.6: questa lacuna
non va conteggiata come core già giocabile. Dopo lo smontaggio, valutare una
fetta dedicata di conversazione NPC prima di dichiarare completo il ciclo
sociale; non dedurre il completamento dalla sola presenza del modello NPC.

## Cambio lingua a caldo — 2026-10-18

L'utente accetta l'avviso precedente e chiede di eliminare il riavvio.
[Direttiva](docs/source/live-language-feedback-2026-10-18.md). Il vincolo LANG-01
è superato: selezione Esc con richiesta di presentazione correlata e conferma
nativa, invalidazione dei traduttori CDDA/gettext, refresh del menu e dei testi
esportati. Niente turno, ripetizione delle scelte, nuova attività o scrittura
alle opzioni/save canonici. Le decisioni aperte mantengono il testo fino alla
risposta. CWM2.26 richiede i due eseguibili abbinati. [Contratto corrente](docs/design/product-language.md).

Il precedente ricontrollo della dicitura è PASS personale; due nuove prove
LANG-02 rinviabili portano il backlog a **30 PENDING, nessun FAIL manuale aperto**.
I precedenti 28 restano invariati. Non serve un gate personale oggi; la prossima
fetta funzionale rimane lo smontaggio nativo. SAVE-001 OPEN e M5.5 FAILED invariati.
I requisiti di riavvio nelle consegne storiche sotto descrivono quelle versioni.

## Lettura cartacea e studio nativo — 2026-10-18

Prossimo passo funzionale eseguito senza un nuovo gate manuale: I permette di
sfogliare i veri libri posseduti e studiare quelli noti, con lettore, luce,
costi di accesso, durata, esperienza teorica e scelte di CDDA. Nessuna conoscenza
gratis consultando il menu. I ferma il capitolo; Interrompi usa la cancellazione
e la ripresa native. Il save conserva ACT_READ e le conoscenze, non la pausa del
menu. Riconnessione e caricamento riprendono lo stato autorevole senza duplicare
la richiesta. [Contratto](docs/design/native-reading.md),
[consegna e verifiche](docs/fixes/native-reading.md).

CWM 2.25 richiede i due eseguibili abbinati; i libri con usi speciali, guidebook
ed e-reader restano esplicitamente fuori da questa prima fetta. Nessun nuovo
moltiplicatore per accelerare lo studio. `./reading-demo.sh --fresh` crea una
sessione separata. **28 PENDING, nessun FAIL manuale aperto**: quattro nuove prove
READ-01 rinviabili, precedenti 24 invariati. Nessun PASS umano dedotto dalle
prove automatiche. Prossimo passo funzionale: smontaggio/lavorazioni native,
riusando attività, requisiti, scelte, interruzione e save. SAVE-001 OPEN e
M5.5 FAILED rimangono invariati; nessuna promozione a M6.

## Sette gate umani e consolidamento del crafting — 2026-10-18

T1–T7 PASS personali, con i bug e commenti conservati nel
[riscontro](docs/source/manual-core-gates-2026-10-18.md). Il FAIL della pausa
Indossa/Togli è superato. **24 PENDING, nessun FAIL manuale aperto**: otto
punti preesistenti accettati e quattro ricontrolli delle modifiche successive.
I PASS hanno origine umana; automazione e nuove modifiche non li estendono
automaticamente. [Dichiarazione pubblica richiesta dallo sviluppatore](HUMAN_TESTING.md).

Prima della lettura/smontaggio, correggere le regressioni emerse nei gate:
categorie native erroneamente eseguibili, avviso sovrapposto, ricerca dinamica
in K/I, selezione stabile al cambio lotto, puntamento del vano finestra e O
di sola chiusura/tende. Rendere graduale la tinta di poca luce, senza cambiare
il modello nativo. [Verifica ricostruita e installazione](docs/fixes/core-gates-crafting.md):
100 casi nativi / 65.437 assert, 309 client, 12 protocollo e 253 controlli GUI/canonici
PASS. I ricontrolli personali restano pendenti; segue il push richiesto.

Il menu e la pausa di ispezione non sono persistiti nel save: il lavoro nativo
si riprende al caricamento. Una futura ripresa inizialmente in pausa è una
decisione di presentazione distinta, senza annullare l'actor o il suo costo.
Luce laterale più credibile, panorami/nebbia e scale real-time restano separati.
Prossima espansione funzionale: lettura nativa, poi smontaggio/lavorazioni,
riusando attività, scelte, pausa e persistenza già esistenti.

## Dieci passi consecutivi del core — 2026-10-18

Richiesta esplicita: dieci passi autonomi, prove personali rinviate. Il
[contratto operativo](docs/design/core-feedback-ten-steps.md) segue il debito di
presentazione già pianificato: (1) attacchi nativi, (2) reazioni ai danni,
(3) suoni effettivamente uditi e didascalie, (4) oggetto reale in prima persona
con posa di mira/sparo, (5) canidi, (6) ragni, (7) piccoli uccelli terrestri,
(8) oscurità, (9) immersione, (10) diagnostica opzionale. I modelli restano proxy
espliciti di famiglie selezionate, non copertura completa del bestiario.

CWM 2.24 raccoglie eventi effimeri filtrati dentro CDDA e li pubblica nei batch:
nessuna inferenza di attacco/danno nel client, nessuna nuova autorità o save.
[Implementazione e installazione](docs/fixes/core-feedback-ten.md) verificate in
modo mirato: 98 casi nativi / 65.402 assert, 309 test client, 12 test protocollo
e 231 controlli GUI/canonici tra ricostruzione e `start.sh` installato. Restano
cinque casi statistici opzionali fallenti, riprodotti nell'eseguibile precedente;
non dichiarare PASS la suite estesa. Backlog **28 PENDING + 1 FAIL manuale**, senza
gate oggi. Prossima fetta funzionale: lettura/smontaggio e lavorazioni native.
Non finalizzare nebbia/panorama, controller o M6; SAVE-001 OPEN, M5.5 FAILED.

## Tre passi consecutivi del core — 2026-10-18

Dopo Indossa/Togli l'utente autorizza altri tre o quattro passi senza attendere
prove personali. Scelti e implementati questi tre elementi già nel piano:

1. Raccolta diretta di un singolo stack sfuso, anche conteggiato: RMB richiede
   il pickup nativo completo senza menu 9×3. Mobili, contenitori e più oggetti
   conservano la selezione delle quantità; nessuna raccolta automatica/in pausa.
2. Materiali umanoidi e avatar voxel: pelle separata dalle superfici armatura
   vuote, filtro pixel art, terza persona con rig Mineclonia e scala/piedi coerenti.
   È un aspetto generico, non la ricostruzione completa dei vestiti/anatomie CDDA.
3. Posa idle/cammino, orientamento sul movimento confermato e postura del
   giocatore sulla stessa cronologia visiva scalata/ferma. Nessun recupero di
   traiettorie nascoste, nuova AI o movimento autorevole nel renderer.

[Contratto](docs/design/core-presentation-followups.md). Nove prove aggiunte al
[backlog](docs/validation/pending-manual.md): **18 PENDING + 1 FAIL manuale**,
incluso il ricontrollo della pausa Indossa/Togli. Nessun gate personale oggi.
Le animazioni d'attacco/reazione aspettano eventi nativi dedicati; non dedurle
da distanza o perdita HP. Audio, posa dell'arma e famiglie del bestiario restano
i prossimi elementi di presentazione, prima di espandere veicoli/M6.

## Indossa/Togli — semantica nativa e pausa — 2026-10-18

L'utente sceglie esplicitamente la [soluzione fedele al codice nativo](docs/source/manual-validation-followup-2026-10-18.md):
il singolo capo cambia immediatamente e addebita mosse; non si introduce una
vestizione parziale annullabile. Distinguere il tempo CDDA residuo dal progresso
di un actor: secondi di gioco e stato applicato per il primo, barra/Interrompi
solo per vere attività. I deve mettere in pausa anche durante la risposta in
volo; consultazione aggiornata dopo l'esito e chiusura riprendono lo stesso costo.
Errori restano errori, senza dichiarare applicato un cambio rifiutato.
[Design](docs/design/native-equipment-time.md).

Il nuovo riscontro aggiunge 13 PASS personali e lascia **9 PENDING + 1 FAIL**:
ricontrollo pausa Indossa/Togli. La richiesta di annullamento del singolo capo
è superata dalla decisione nativa, senza cancellare il FAIL sulla pausa.
UX-05 2–4, gesti INT-01 1–3 ed eccezioni UX-02 restano pendenti. Il commento
sulla raccolta diretta degli oggetti sfusi è un seguito UX separato; poi
consolidamento core e debito rig/UV/animazioni/audio. Nessun gate personale oggi.
I conteggi nelle sezioni delle precedenti consegne sotto sono storici.

## INT-01 — Riscontro manuale e gesti — 2026-10-18

[Riscontro](docs/source/manual-interaction-feedback-2026-10-18.md): AIM1–3 PASS;
EXT1–3 PASS, EXT4 FAIL solo per raccolta differita dalla pausa. Cinque nuovi PASS.
Priorità a rifiuto/scarto della raccolta in pausa, RMB toggle porte/finestre,
Shift-clic verso altro pannello/destinazione scelta e rilascio esterno = terra.
Gesti reali producono azioni native con quantità/costi/accesso; split parziale
esterno conserva resto e identità rapida. Chiusura sul corpo continuo rifiutata
all’ammissione e all’esecuzione; il caso riportato durante apertura della
struttura originale resta un ricontrollo personale, non una riproduzione certa.
[Design](docs/design/interaction-feedback.md), CWM2.23. Backlog **21 PENDING +
2 FAIL manuali** (lingua ed EXT4): tre nuove prove dei gesti, senza obbligo oggi.
Rilascio mira/azzeramento precisione ancora da decidere: nessuna modifica a
recoil o costo; la presentazione futura di arma abbassata può essere distinta.
Dopo questi fix riprende consolidamento core/rig/UV/animazioni/audio; gate
storici e salvataggi personali restano separati.

## Riscontro del playable core — 2026-10-08

Tutte le prove manuali raccolta/corpo/melee/posture sono PASS. Il
[riscontro corrente](docs/source/playable-core-feedback-2026-10-08.md) aggiunge
Ctrl/Shift tenuti premuti, toggle configurabile, animazioni ferme in pausa,
camera sicura in acqua bassa e HUD con asset Mineclonia. Barra oggetti visibile
di sola lettura; equipaggiamento rapido richiede una fetta nativa dedicata.
Salute vitale e malattie restano distinte; media HP non finalizzata.

Il [secondo riscontro](docs/source/hud-icon-feedback-2026-10-08.md) valida
anche i quattro adattamenti e richiede l’ultimo ritocco: X predefinito per
sdraiarsi; lieve discesa proni nell’acqua; HUD centrale a icone (più = meglio),
senza sfondo nero. Barre dei bisogni sono categorie percepite native, non
nuove regole biologiche. H conserva i dettagli. Dopo questo ritocco proseguire
senza nuovo gate estetico. Il [resoconto corrente](docs/progress/2026-10-08.md)
separa le fetta giocabili dalle parti ancora pianificate.

## Nuovo riscontro UX-03 — drag-and-drop completo

[Riscontro registrato](docs/source/ux03-drag-feedback-2026-10-09.md):
Ricontrolli UX-03 **1–3 PASS**; hotbar **1 FAIL** per ergonomia,
**2–4 non provati**. Il backlog alla ricezione era **11 aperti: 10 PENDING + 1 FAIL**.
I contatori sotto descrivono le consegne precedenti.

**UX-03D consegnata**, prima di lingua/mira: rimossi Assegna/Svuota e
adattare a drag-and-drop griglia, hotbar, mano, indossati e sottoviste dei
contenitori, conservando raccolta e costi nativi. Il gesto su mano/vestiti/
contenitori richiede un'azione CDDA; disposizione grafica/riferimenti non
creano tasche nuove. Scambio slot coerente, quantità esplicite, annullamento
ed errori leggibili; nessuna identità dedotta dal nome e nessuna mutazione
Luanti di gameplay. [Piano operativo dai sorgenti](docs/design/inventory-drag-and-drop.md).
Ora CWM **2.18**, con entrambi i runtime installati nel normale start.sh.
Il riordino usa ranghi compatti opzionali sugli oggetti nativi, non capacità
o tasche nuove; una casella vuota porta l'oggetto alla fine, senza buchi
persistenti. Scambio hotbar atomico con verifica di entrambe le identità.
[Consegna ed evidenze](docs/fixes/inventory-drag-and-drop.md).
Il backlog alla consegna UX-03D era **13 PENDING**: ricontrollo DND di 1,
hotbar 2–4, due nuove prove mano/indossati e contenitori, sette precedenti.
M5.5/SAVE-001 restano separati.

## LANG-01 — Lingua del prodotto — 2026-10-12

Consegnata nel normale `start.sh`: **English** predefinito, **Italiano (WIP)**
selezionabile da Esc e dalle impostazioni. Riavvio supervisionato per allineare
Luanti, testo d'integrazione e traduzioni native CDDA. La preferenza di
presentazione è separata da opzioni native e save canonici; il cambio non
esegue azioni, non altera costi e non riscrive le regole. Identificatori nativi
restano stabili, compresi quelli delle categorie usati dalle icone; mapping
batch invariato. Fallback inglese per traduzioni italiane mancanti.
[Design](docs/design/product-language.md) e [consegna/evidenze](docs/fixes/product-language.md).
Backlog corrente **15 PENDING**, aggiungendo soltanto due prove di lingua;
nessun nuovo gate manuale oggi e nessun PASS dedotto dai test automatici.

La fetta successiva è ora consegnata sotto; i quindici punti sopra descrivono
il backlog alla consegna LANG-01.

## AIM-01 — Destro mantenuto e priorità contestuali — 2026-10-12

Mira assistita con RMB mantenuto, F alternativo; sparo singolo per clic sinistro,
ripresa della mira dopo il tiro se RMB resta premuto. Porte/finestre e raccolta
conservano le interazioni contestuali; un gesto di apertura/raccolta non diventa
mira cambiando puntamento. Shift+RMB chiude; Shift per accovacciarsi non blocca
la mira su un ostile puntato. Un clic rapidissimo resta un'interazione.

Un solo sparo/R esplicito può attendere la fine del passo AIM già in corso,
con identità e deadline stretti; nessuna coda dietro movimento, altri colpi,
lavori o menu. Pausa/menu/recovery richiedono rilascio e nuova pressione;
cancellano anche quel differimento. Il rinculo e i costi restano CDDA, così
come il mantenimento nativo della precisione già pagata. Nessuna mira gratuita,
nuova regola simulativa, modifica schema o deduzione dal nome dell'oggetto.
[Design](docs/design/held-mouse-aim.md) e [consegna](docs/fixes/held-mouse-aim.md).
Disponibile nel normale start.sh, CWM **2.18**. Backlog alla consegna **18 PENDING**:
tre nuovi punti per RMB, quindici precedenti invariati. Non serve testarli oggi.

L'intervento annunciato a questa consegna è completato nella sezione seguente.
Rig/UV/animazioni, audio e le altre macrofeature restano nel piano sottostante.

## EXT-01 — Contenitori esterni e raccolta parziale — 2026-10-12

Consegnato nel normale `start.sh`, CWM **2.19**, mantenendo tempo continuo 4x e
lingua del prodotto. I mobili con semantica nativa CONTAINER (armadietti,
casse, ecc.) aprono due griglie a nove colonne, anche se vuoti. Il contenuto
non compare più come drop rotanti; gli oggetti sfusi restano drop. Anche zaini
a terra, pile multiple e oggetti a cariche aprono la stessa vista quantitativa.
I modelli di cassa sono proxy provvisori per i vari mobili, non un mapping
finale né l'importazione di meccaniche Mineclonia.

DND fra zone di raccolta/deposito o su vere icone di contenitori; clic sulla
pila + Quantity per trasferimenti parziali. Pickup/drop/insert nativi gestiscono
costi, furto, capacità, tasche, salvataggi e ritorno al menu dopo il pagamento.
Raggio, percezione, sigilli, identità, genitori, quantità e tipo di mobile sono
ricontrollati all'ammissione e all'esecuzione. Nessuna inferenza da etichette,
mutazione d'inventario Luanti o deduzione del risultato durante il lavoro.

[Consegna](docs/fixes/external-storage.md), [protocollo](protocol/PROTOCOL.md),
[prova isolata](storage-demo.sh). Quattro nuovi test nel backlog portano il totale
a **22 PENDING**; gli altri diciotto e tutti i PASS precedenti rimangono.
Nessun nuovo gate manuale oggi. Cargo veicoli, travaso liquidi, apertura dei
sigilli, selezione della singola tasca e trasferimenti in batch sono rinviati;
M5.5 FAILED e SAVE-001 OPEN restano separati dalla verifica della feature.

L'intervento annunciato qui è consegnato nella sezione seguente.

## UX-04A — Dialoghi nativi e feedback del lavoro — 2026-10-12

Consegnati in `start.sh`, CWM **2.20**. Il testo numerato sovrapposto al mondo
è sostituito da un pannello coerente con l'inventario: lettura/scelte scorrevoli,
colori nativi sanificati, pulsanti e scorciatoie 1–9. Etichette su una riga e
contenuto completo nel tooltip; debug nascosto durante la decisione. Esc usa
l'indice di annullamento esportato da CDDA, senza deduzioni da traduzioni;
Invio non sceglie tramite il focus e un tasto tenuto non risponde alla domanda
successiva. Ogni risposta è legata a domanda/connessione e viene inviata una
sola volta; il pannello attende il risultato nativo o la domanda successiva.

Il lavoro temporaneo mostra operazione/oggetto e progresso nativo disponibile;
I significa consulta/pausa, Chiudi riprende, Interrompi annulla secondo l'actor.
Il ritorno all'inventario segue ancora completamento e costo nativi, con feedback
leggibile. Nessun nuovo costo/durata, conferma automatica, regola o campo nel save.
[Design](docs/design/native-decision-panels.md), [report](docs/fixes/native-decision-panels.md).
Quattro nuove prove portano il backlog a **26 PENDING**, mantenendo i 22
precedenti e tutti i PASS. Nessun gate manuale oggi.

**Intervento successivo annunciato allora: UX-04B, scheda medica strutturata**. Esporre
identità delle parti, salute osservabile e benefici/rischi conoscibili associati
alla scelta; icone anatomiche/cuori e selezione esplicita di oggetto/parte.
Non ricavare statistiche da barrette ASCII o dal testo tradotto. La presente
fetta aggiorna la veste e gli input, lasciando le descrizioni mediche native.
UX-05 recenti/preferiti, rig/UV/animazioni/audio e macrofeature restano nel piano.
Le eccezioni UX-02 morte/IPC non provate restano nel backlog; M5.5/SAVE-001 separati.

## Riscontro manuale e UX-04B — 2026-10-13

[Riscontro integrale](docs/source/manual-ui-feedback-2026-10-13.md): acquisiti
12 nuovi PASS, un FAIL lingua e 13 prove non eseguite. Riparazioni mirate:
ultima griglia mantenuta durante query di layout, destinazioni a sei righe più
alte, progresso Indossa/Togli dal clock autorevole già esistente, scelta lingua
con pulsanti espliciti e restart coordinato. Il FAIL resta tale fino al ricontrollo
manuale; niente accettazione implicita. Cambio lingua a caldo è un follow-up.

UX-04B usa dati semantici del menu medico nativo: item reale → parte → conferma,
icone/cuori alla risoluzione osservabile, parti disabilitate leggibili, effetti e
limiti nativi. Nessuna statistica ricostruita dal testo. Parte → item filtrati
resta un’estensione successiva del medesimo flusso, insieme agli asset anatomici.
CWM 2.21, installato in start.sh; [design](docs/design/structured-medical-selection.md)
e [consegna/evidenze](docs/fixes/structured-medical-selection.md).

Sincronizzati [batch Sol 28–60](docs/fixes/item-mapping-2026-10-13.md): 2.400
oggetti totali, 972 rappresentazioni supportate. Nuovo backlog **20 PENDING +
1 FAIL manuale**: 13 invariati, 3 ricontrolli commenti e 4 medici. Prossima fetta:
**UX-05 ricette recenti/preferite**. Un playtest mirato è consigliato al consolidamento
core dopo UX-05; nessun nuovo gate personale oggi. Per RMB il rilascio già termina
il gesto di mira: non azzerare la precisione pagata; postura/zoom visivi separati,
movimento e penalità nativi. SAVE-001 OPEN e storico M5.5 FAILED restano separati.

## UX-05 — Scorciatoie native del crafting — 2026-10-14

K: Tutte/Preferite/Recenti/Incompleti, con apertura prioritaria a incompleti
accessibili, recenti noti, preferite note e infine catalogo. Filtri prima del limite
256, ricerca/lotti conservati. Stato della ricetta e ammissibilità restano CDDA.
Preferiti e ultime 20 ricette avviate usano uistate.json nativo (condiviso dal mondo),
con setter esplicito, handle verificati, dedup e zero costo/avvio in pausa.
Ingredienti preferiti/protetti sono distinti. Ripresa per requisiti rimanenti,
senza interpretazione di errori italiani. CWM2.22; [design](docs/design/recipe-shortcuts.md).
Il controllo RNG nuovo ha richiesto di evitare estrazioni per insiemi di varianti
vuoti: nessuna variante reale o probabilità nuova. La conoscenza per i preferiti
usa fonti reali native senza generare acqua/pseudo-utensili né estrarre semi
casuali; regole di accesso/proprietà e percorso normale di crafting conservati. Sequenza casuale successiva
modificata eliminando quelle estrazioni inutili; verifica ed evidenze separate.

“Più eseguite” richiede conteggi di completamenti effettivi e persistenza definita:
non ricavarlo dai recenti avviati. Rimane follow-up, insieme a sottoricette e
risultati/liquidi/pratica. Backlog **24 PENDING + 1 FAIL manuale**, quattro prove
nuove, vecchi PASS invariati. Nessun gate personale oggi. Segue consolidamento
core e debito visivo rig/UV/animazioni/audio, conservando FND-05/SAVE-001/M5.5
separati. Confronti di nuovi controlli spaziali richiedono ancora la prova utente.

## Riscontro inventario/interfacce — 2026-10-09

Il [riscontro successivo con errata corrige](docs/source/core-ux-validation-2026-10-09.md)
accetta anche tiro/ricarica, trasferimenti, UX-01 e UX-02: quattro punti per
checklist. Eccezioni UX-02 non provate e deposito annidato non riuscito
restano espliciti; il backlog alla ricezione era **7 PENDING**, diventati **14**
con i ricontrolli UX-03 e UI aggiunti alla consegna precedente. Le descrizioni della
consegna sotto conservano la cronologia e i vecchi conteggi.
UX-03 consegnata (CWM 2.17): hotbar assegnabile/rimuovibile con icone HUD corrette,
mano evidenziata, ricerca **visibile ma senza focus**, quantità/errori
leggibili e correzione del solo `water_clean`. Mapping generato invariato.
Rotella/numeri selezionano, G invia l’azione nativa con costi; collegamenti
canonici opzionali persistono senza usare ID effimeri. [Consegna/evidenze](docs/fixes/interactive-quickbar.md).
Nuvole col clock visivo in pausa e nomi oggetto nel lavoro Indossa/Togli
sono inclusi nei ritocchi. Restano mira RMB mantenuto, arma/rinculo,
rig/UV/animazioni, audio autorevole e feedback completo delle operazioni.
Lingua del prodotto: inglese di default, italiano (WIP) selezionabile con
fallback; applicarla anche al testo nativo e alle nuove UI. Ogni consegna
deve essere installata nel normale `start.sh`, con verifica su save isolati;
il continuo 4× accettato è ora predefinito, conservando opzioni
per confronti tecnici (`CDDA_CONTINUOUS=0`, oppure `CDDA_REALTIME=1`).
[Recap e stime per traguardo](docs/progress/core-outlook-2026-10-09.md).

Cronologia precedente alla nuova accettazione:

L'utente accetta 16 punti inventario/equipaggiamento, consumo, medicazioni e
crafting; restano tiro/ricarica e quantità/contenitori. I bug e le richieste
sono nel [riscontro](docs/source/inventory-ui-feedback-2026-10-09.md).
Il [piano UI basato sui sorgenti](docs/design/inventory-and-native-dialogs.md)
prioritizza: layout Mineclonia 9×3 con ricerca su richiesta, dettagli
progressivi e strati; azioni consecutive con tempo nativo e ritorno alla stessa
vista; conferme visive/medicina; ricette recenti/preferite/frequenti; hotbar
interattiva con selezione distinta dalla mano reale. Sono task UX-01–05. Il layout UX-01 è ora consegnato, ma non ancora graficamente approvato;
UX-02 è implementato: azioni consecutive, indicatore non modale e ritorno
solo dopo il costo nativo pagato (CWM 2.16). Accettazione grafica pendente
nel backlog, ora 20 punti. Prossimo passo UX-03, hotbar interattiva; contenitori esterni e raccolta quantitativa
restano essenziali e riusano questi componenti. Costi/decisioni/capacità
rimangono nativi. Le nuove prove manuali saranno aggiunte alla consegna.
Su ulteriore richiesta sono sincronizzati i **27 batch di produzione** attuali:
1.080 record, 396 rappresentazioni runtime e 89 texture attribuite. Il
[report mapping](docs/fixes/item-mapping-2026-10-09.md) distingue proxy pronti,
asset non supportati, no-match e varianti procedurali ancora da realizzare.
La mappatura resta una corsia indipendente dal gameplay; i nuovi test mirati
UI/mapping sono nel consueto backlog (12 pendenti dopo i 16 PASS).

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
scambi e luce locale restano nei task previsti. L'utente
[accetta tutti e tre i controlli manuali](docs/source/actor-lifecycle-validation-2026-10-04.md).
Non serve ripeterli. Il caso di schermo nero fuori dal percorso della demo
resta da riprodurre, conservando la sessione; non riapre questi tre controlli.
Il seguito autorizzato è il [primo prototipo dello scheduler della fase 2](docs/prototypes/rt01-real-time.md):
tick nativi temporizzati, idle, velocità globale, pause/menu/minacce e input
mantenuto senza coda di passi. `realtime-demo.sh` offre la prova isolata.
L'utente [accetta la checklist manuale dello scheduler](docs/source/rt01-validation-2026-10-04.md),
ma giudica il ritmo base 1× troppo lento e chiede il controller continuo già
previsto. Il baseline tecnico a griglia è storico; RT-02 con offset continuo autorevole,
arresto dentro una casella e direzione arbitraria è implementato e accettato
nella [continuazione recuperata](docs/source/continuation-2026-10-07.md).
Fra le velocità provate, l'utente preferisce 4×: usarlo come ritmo globale
di riferimento del prossimo prototipo continuo. Controller e bilanciamento
finali restano da confrontare; la fase 2 non è chiusa.
Gli altri criteri FND-04 restano aperti.

## Fase 2 — Prototipo di tempo, movimento e percezione

Dipende da FND-01–03 e dalla proiezione sufficiente alla scena di confronto.

- Scheduler unico CDDA: default 1:1 e velocità globale regolabile, pausa
  esplicita/menu, attività lunghe accelerate, interruzioni native rilevanti.
  Il rapporto 1:1 è il baseline RT-01 verificato; l'utente preferisce 4×
  fra i ritmi provati. Il prototipo continuo RT-02, ora implementato e accettato, usa 4× globale come
  riferimento, mantenendo la regolazione. Il bilanciamento finale richiede
  anche il confronto di combattimento, posture e attività.
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

## Priorità operativa — playable core

Prima di espandere M6/veicoli, anticipare il minimo necessario dei punti 1–5
della Fase 4 per ottenere un ciclo giocabile: interazioni, inventario/equipaggiamento,
corpo/HUD, crafting/medicina essenziali e combattimento. M6 resta definita invariata
qui sotto, ma viene ripresa dopo questo playable core minimo.

Per gli item a terra, un singolo oggetto usa la normale rappresentazione Mineclonia
dell'item flottante/rotante, ma senza pickup automatico: l'interazione esplicita
avvia la corrispondente azione nativa CDDA. Più item sulla stessa casella sono
presentati come una pila generica; interagirvi apre la stessa GUI Mineclonia usata
per chest/container, popolata però dagli item realmente presenti sul tile CDDA.
Spostamenti, pickup e altre operazioni della GUI sono tradotti nelle corrispondenti
azioni CDDA e mai applicati a un inventario Luanti autonomo. La simulazione resta
in pausa mentre la GUI è aperta. La presentazione passa automaticamente fra
nessun item, item singolo e pila in base allo stato autorevole corrente.

Avanzamento locale 2026-10-08: raccolta/pila con GUI Mineclonia,
HUD/scheda corporea e [melee puntato](docs/fixes/pointed-melee.md) implementati;
le prove furono inizialmente rinviate; ora tutte e quattro sono validate
nel [riscontro corrente](docs/source/playable-core-feedback-2026-10-08.md).
La quarta fetta essenziale ortogonale sono le
[corsa/posture native](docs/fixes/native-postures.md), già previste nelle
fondazioni/comandi: inizialmente R/X/P toggle, ora Ctrl/Shift mantenuti e
sdraio toggle (ora X predefinito) secondo le direttive successive;
velocità/stamina/rumore CDDA, visuale 3D corrispondente e save canonico.
Non richiede nessuna delle tre interfacce da validare. Rig/animazioni in terza
persona restano successivi. Melee resta il primo combattimento, non chiusura
dell'intero punto 5: ranged, reach, feedback avanzati e attacco deliberato a
neutrali restano nel piano. Tutte e quattro le
[checklist](docs/validation/pending-manual.md) originali sono PASS;
anche i quattro adattamenti successivi sono PASS; il ritocco estetico non aggiunge un gate;
verifiche automatiche e accettazione visiva sono distinte. Il calendario
approvato e i nove batch di mapping restano invariati.

Prima fetta implementata 2026-10-08: **inventario/equipaggiamento nativo**,
I per query di oggetti/tasche con provenienza e capacita; Impugna/Riponi/
Indossa/Togli attraverso item_location, vincoli e costi CDDA, scelte native,
nessuna mutazione ottimistica o hotbar gratuita. Checklist manuale rinviata
nel file abituale per indisponibilita dell'utente, senza dichiararla PASS.
Quantita/drop/trasferimenti mirati e apertura tasche sigillate restano fette
successive.

Successiva fetta implementata 2026-10-08: **cibo/bevande nativi**, I con
Mangia/Bevi, avvisi CDDA e ACT_CONSUME, durata/progresso autorevoli e
interruzione esplicita, nessuna fame/sete o quantita modificate dal client.
Salvataggio canonico anche con consumo in corso; movimento/azioni non
accodati mentre si consuma. Farmaci/uso speciale, sigilli e travasi restano
fuori da questa fetta. [Dettagli](docs/fixes/native-consumption.md).
Quattro nuovi test grafici rinviati si aggiungono ai quattro inventario nel
[backlog manuale](docs/validation/pending-manual.md); nessun PASS dedotto.
Successiva fetta implementata 2026-10-08: **medicazioni esterne native**,
I con Medica..., scelta di parte tramite le voci native e conferma, ACT_FIRSTAID
con costo/progresso/stop e rimozione finale dell'oggetto, salvataggio del lavoro
residuo. H mostra condizioni di ferita/trattamento conoscibili; niente cura
locale o automatica. [Dettagli](docs/fixes/native-medicine.md). Farmaci orali,
antisettici liquidi, avvio parte→oggetto da H, NPC/chirurgia sono fette successive.
Quattro nuovi punti nel backlog, allora 12 manuali pendenti, senza gate immediato.
Successiva fetta implementata 2026-10-08: **crafting guidato nativo**, K con
ricette note/libri/aiutanti, ricerca e lotto manuale 1–20, requisiti e durata,
scelte native di componenti/fonti e conferma. ACT_CRAFT e oggetto incompleto
canonico possiedono progresso, costi, fallimenti, pratica e risultati; K/I
permettono pausa/interruzione e K riprende lavori propri o su superficie
vicina accessibile. Protezione di preferiti/tipi equipaggiati/contenitori
liquidi pieni, handle effimeri invalidati al reconnect e dedup dei comandi.
[Dettagli e limiti](docs/fixes/native-crafting.md). CWM 2.13, due runtime
ricostruiti installati; quattro nuovi test nel backlog, **16 PENDING**.
Ricette liquide/gassose, sottoprodotti/pratica/costruzioni, preferiti ricette,
sottoricette, selezione singola istanza, lavori nei veicoli, lettura/smontaggio
e accelerazione generale restano fette successive: il punto 4 non e completo.
Successiva fetta implementata 2026-10-08: **tiro, mira e ricarica nativi**.
F tenuto paga la mira CDDA, clic sinistro esegue un tiro/raffica della modalità
corrente, R propone munizioni e conferma native prima di ACT_RELOAD. I ferma
il tempo e interrompe; save in corso riprende il lavoro canonico e trasferisce
le munizioni una sola volta. Conservazione della mira pagata fra input real time,
nessun miglioramento durante pausa/menu, input occupati non accodati, token
rinnovati al reconnect. Corrette ricorsione della cache visiva nativa e portata
di puntamento limitata alla mano Luanti. CWM 2.14, verifica mirata e due runtime
installati; [limiti/evidenze](docs/fixes/native-ranged.md). Quattro nuovi test
manuali rinviati nel backlog, **20 PENDING**. Il punto combattimento non è
completo: mirino libero configurabile, neutrali, archi/RAS, armi montate/veicoli,
cambio modalità, munizioni parziali e presentazione delle armi restano previsti.
Successiva fetta implementata 2026-10-09: **quantita, deposito e contenitori
posseduti**, I → Quantita e trasferimenti con sorgente/contenitore, quantità
parziali e terra alla casella corrente. ACT_DROP/ACT_INSERT_ITEM originali
pagano costi/accesso, conservano contenuti e progresso; I interrompe e un lavoro
canonico salvato riprende una sola volta. Handles/quantita/ancestry/posizione/
capienza e pausa rivalidati; nessun sigillo aperto implicitamente o inventario
Luanti autorevole. CWM 2.15, [limiti e prove](docs/fixes/native-transfer.md);
quattro nuovi manuali nel backlog, **24 PENDING**, senza dedurre PASS.
Questa fetta non completa l'inventario profondo: contenitori esterni/cargo,
quantita di raccolta, scelta della singola tasca, liquidi/sigilli e trasferimenti
multipli restano successivi. La precedente priorità contenitori esterni/raccolta
quantitativa è aggiornata dal riscontro UI del 2026-10-09: prima UX-01/02, poi
accesso ai contenitori esterni e quantità. Attivita estese restano
nella sequenza; nessuna validazione grafica pendente e promossa a PASS.


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

## Presentazione di produzione — promemoria esplicito

Gli overlay «cammino», «tempo reale», «CDDA–Mineclonia / F3», metriche e
istruzioni di debug diventano opzionali con una hotkey riconfigurabile e
impostazione nel menu. Default prodotto senza pannelli diagnostici persistenti;
le demo tecniche possono abilitarli. Distinguere questa diagnostica dagli
indicatori minimi di pausa, perdita di connessione, minaccia e decisioni native:
questi devono restare comprensibili anche con debug disattivato. Pianificato,
non incluso nell’ultimo ritocco HUD. Non riaprire altre iterazioni estetiche
prima della prossima feature essenziale del playable core.

## Fase 5 — M8/M9 e contenuti successivi

Anticipazione richiesta il 2026-10-21: installer nativo Windows 11 x64 con
avvio automatico, librerie/risorse incluse e salvataggi separati.
[Consegna e prove](docs/releases/windows11-2026-10-21.md): verifiche automatiche
Wine; tre controlli WIN-01 su hardware reale restano nel backlog. Questa fetta
non completa M9 né i gate generali di prestazioni, recovery e SAVE-001.

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
