# Validazioni manuali del playable core

Ultimo riscontro umano (2026-10-26): **FB-01.1 e FB-01.2 PASS**, confermati
anche dopo la nuova segnalazione sui passaggi dei menu. Chiusi entrambi i FAIL
di avvio. **59 PENDING, nessun FAIL aperto**: i precedenti 58 invariati più
MENU-01.1 per la nuova continuità delle schermate. UF8-01.1 rimane pendente.
[Fonte e direttiva](../source/modal-continuity-feedback-2026-10-26.md).
Le sezioni datate sotto conservano la cronologia dei conteggi.

Ultimo riscontro (2026-10-25, successivo a CWM2.35): **FB-01.3 e .4 PASS**;
**FB-01.1 e .2 FAIL di avvio della demo**, quindi le prove funzionali non sono
state raggiunte. Il PASS 3 include una richiesta esplicita di sostituire il
moltiplicatore separato con l'unico controllo F8. [Fonte e diagnosi](../source/unified-f8-feedback-2026-10-25.md).
**58 PENDING +2 FAIL di avvio**: 57 altri punti ancora pendenti più il nuovo
UF8-01.1 per il design modificato. Le verifiche automatiche non chiudono i
FAIL personali; riprovare 1 e 2 dopo il fix dell'avvio, senza accettarli d'ufficio.

Il fix CWM2.36 è installato in start.sh: nome demo valido `recovery_demo`,
un solo F8 con scala contestuale. [Consegna e prove automatiche](../fixes/unified-f8.md).
Rilanciare `./liquid-recovery-demo.sh --fresh` per FB-01.1/.2 e
`./rest-demo.sh --fresh` per UF8-01.1. Non occorre ripetere il cielo FB-01.4.


Secondo riscontro umano del 2026-10-25: **SEAL-01.3, REST-01.2, REST-01.3 e
DIS-01.3 PASS** nei quattro scenari proposti. Il backlog scende da 61 a 57;
quattro nuovi ricontrolli FB-01 delle modifiche successive lo portano a
**61 PENDING**. [Riscontro e direttive](../source/manual-rest-recovery-feedback-2026-10-25.md).
I PASS non attestano automaticamente i nuovi livelli di accelerazione, la
correzione del cursore/skybox o il recupero della lattina: questi hanno test propri.


Riscontro umano del 2026-10-25: **61 PENDING**, nessun nuovo FAIL funzionale.
L'unico sviluppatore ha validato **LIQ-01.1, LIQ-01.2, LIQ-01.4 e SEAL-01.1**
nei quattro scenari proposti. [Riscontro e corrispondenza esatta](../source/manual-liquids-seals-feedback-2026-10-25.md).
La segnalazione **UX-CURSOR-01 è OPEN**: il puntatore si sposta dopo alcune
azioni; causa e frequenza da accertare. Non revoca i quattro PASS e non aggiunge
un test numerato al contatore. Le consegne datate sotto mantengono i conti storici.

Prossimo giro di quattro prove, tutte già pendenti e senza duplicare quelle
eseguite: **1 → SEAL-01.3; 2 → REST-01.2; 3 → REST-01.3; 4 → DIS-01.3**.


Apertura sigilli (2026-10-23): **65 PENDING, nessun FAIL manuale aperto**.
I precedenti 61 punti restano invariati; quattro nuove prove SEAL-01 sono
rinviabili. Nessun PASS umano viene dedotto dalle verifiche automatiche.

Fonti d’acqua e travasi (2026-10-23): **61 PENDING, nessun FAIL manuale aperto**.
I precedenti 57 punti restano invariati; quattro nuove prove LIQ-01 sono
rinviabili. Nessun PASS umano viene dedotto dalle verifiche automatiche.

Riposo, sonno e attesa (2026-10-23): **57 PENDING, nessun FAIL manuale aperto**.
I precedenti 53 punti restano invariati; quattro nuove prove REST-01 sono
rinviabili. Nessun PASS umano viene dedotto dalle verifiche automatiche.

Compagni individuali (2026-10-22): **53 PENDING, nessun FAIL manuale aperto**.
I precedenti 49 punti restano invariati; quattro nuove prove COMP-01 sono
rinviabili. Nessun PASS personale viene dedotto dalle prove automatiche.

Diario missioni note (2026-10-22): **49 PENDING, nessun FAIL manuale aperto**.
I precedenti 45 punti restano invariati; quattro nuove prove JOURNAL-01 sono
rinviabili. Le verifiche automatiche non costituiscono un PASS umano.

Commercio NPC (2026-10-22): **45 PENDING, nessun FAIL manuale aperto**.
I precedenti 41 punti restano invariati; quattro nuove prove TRADE-01 sono
rinviabili. Le verifiche automatiche e le immagini ispezionate dall'agente
non costituiscono un PASS umano. La vecchia limitazione trade di NPC-01 è
superata da questa consegna, senza accettare automaticamente i suoi test.

Conversazioni NPC (2026-10-22): **41 PENDING, nessun FAIL manuale aperto**.
I precedenti 37 punti rimangono invariati; quattro nuove prove NPC-01 sono
rinviabili. Le prove automatiche non sono un'accettazione umana. Il chiarimento
NPC precedente in fondo al file descrive la versione prima di questa consegna.

Smontaggio nativo (2026-10-22): **37 PENDING, nessun FAIL manuale aperto**.
I precedenti 33 punti sono invariati; si aggiungono quattro prove DIS-01
rinviabili. Nessun PASS umano viene dedotto dalle verifiche automatiche.

Distribuzione Windows 11 (2026-10-21): **33 PENDING, nessun FAIL manuale
aperto**. I precedenti 30 punti rimangono invariati; si aggiungono tre prove
WIN-01 su un PC Windows reale. Cross-compilazione e prove Wine sono automatiche
e non costituiscono un PASS personale Windows. Le prove sono rinviabili per
lo sviluppo delle feature successive.

Ultimo riscontro: **30 PENDING, nessun FAIL manuale aperto**. La conferma
«ok funziona perfettamente» accetta l'avviso LANG-01 dopo `a0bbf43`: il suo
ricontrollo non è più pendente. I precedenti 28 restano invariati; due nuove
prove rinviabili LANG-02 riguardano il successivo cambio lingua a caldo.
[Provenienza umana e nuova richiesta](../source/live-language-feedback-2026-10-18.md).
Nessun PASS personale della nuova implementazione dedotto dall'automazione.

Ultimo riscontro: **29 PENDING, nessun FAIL manuale aperto**. La conferma umana
«ora la logica funziona» accetta il fix LANG-01.2; i precedenti 28 punti restano
invariati. Un solo nuovo ricontrollo rinviabile riguarda la dicitura della lingua
selezionata, in fondo al file. [Riscontro](../source/language-notice-feedback-2026-10-18.md).

Nuovo riscontro dopo `91393f7`: **28 PENDING + 1 FAIL manuale aperto**.
**LANG-01.2 riaperto:** English dal menu Esc chiude il menu e al riavvio
resta Italiano. I PASS della versione precedente sono storici; il fix richiede
un ricontrollo personale, non un PASS dedotto dalle prove automatiche.
[Riscontro originale](../source/language-regression-2026-10-18.md).

Stato dopo la lettura nativa: **28 PENDING, nessun FAIL manuale aperto**.
Quattro nuove prove rinviabili di lettura sono in fondo; i precedenti 24 punti
restano invariati. Nessun PASS personale viene dedotto dai test automatici.
I sette gate T1–T7 già provati dall'unico sviluppatore restano accettati.

Stato corrente dopo i sette gate personali del 2026-10-18: **24 PENDING, nessun FAIL manuale aperto**.
T1–T7 sono **PASS riferiti dall'unico sviluppatore umano**; i bug e i commenti
non sono stati cancellati dai PASS. Il vecchio FAIL Indossa/Togli è superato.
[Provenienza e riscontro](../source/manual-core-gates-2026-10-18.md),
[dichiarazione pubblica di test umani e redazione LLM](../../HUMAN_TESTING.md).
Tolti otto punti pendenti coperti dai gate e aggiunti quattro ricontrolli mirati
in fondo; pila conteggiata, recenza/rifiuto, eccezioni UX-02 e altre prove
non eseguite restano pendenti. Nessun obbligo di prove oggi.

Stato corrente dopo i dieci seguiti core del 2026-10-18: **28 PENDING + 1 FAIL manuale**.
Dieci nuove prove rinviabili sono in fondo: feedback, famiglie, ambiente e F3.
Prima di questa consegna erano **18 PENDING + 1 FAIL manuale**.
I tre passi autorizzati consecutivamente aggiungono nove prove rinviabili in
fondo al file: raccolta sfusa, materiali/avatar, animazioni. Nessun gate oggi.
Al secondo riscontro del 2026-10-18 erano **9 PENDING + 1 FAIL manuale**.
Acquisiti 13 nuovi PASS: EXT4, dialoghi UX-04A 1–4, ricontrolli 1 e 3,
LANG-01.2, scheda medica UX-04B 1–4 e UX-05.1. Il ricontrollo Indossa/Togli
resta FAIL per la pausa con I; l'utente ha scelto la semantica nativa atomica,
senza annullamento del singolo capo. Le prove non eseguite restano pendenti.
[Riscontro e decisione](../source/manual-validation-followup-2026-10-18.md).
I contatori e i paragrafi dei riscontri precedenti sotto sono storici.
Acquisiti **12 nuovi PASS**: UI/mapping 4, hotbar 4, mano/contenitori 2,
lingua 1 e mira 1. I 13 punti non provati rimangono; aggiunte 3 prove mirate
ai commenti e 4 alla scheda medica. LANG-01 punto 2 conserva il FAIL finché
l’utente non accetta il ricontrollo. Nessun PASS è dedotto dai fix automatici.
[Riscontro e commenti integrali](../source/manual-ui-feedback-2026-10-13.md).
Tutti i PASS precedenti restano accettati. Nessun obbligo di prove oggi.
I contatori nelle descrizioni delle consegne precedenti sono storici.

Il [riscontro precedente ed errata corrige](../source/core-ux-validation-2026-10-09.md)
accetta 1–4 di tiro/ricarica, quantità/trasferimenti, UX-01 e UX-02 (16 PASS),
oltre ai precedenti 16 di inventario, consumo, medicazioni e crafting.
I PASS UX-02 attestano il flusso ordinario osservato: non morte/IPC/decisioni
non provati. Il deposito delle munizioni annidate nel sacchetto segnalato
prima è compreso nel nuovo Ricontrollo UX-03 3 PASS; ciò non chiude gli altri
ricontrolli storici. Le checklist sotto conservano versioni e cronologia.

L'utente il 2026-10-08 ha eseguito e approvato tutti i quattro punti di
ciascuna delle quattro checklist. Il [riscontro](../source/playable-core-feedback-2026-10-08.md)
supera i rinvii precedenti. Le checklist sotto conservano i comandi della
versione provata (R/X/P); le nuove preferenze Ctrl/Shift sono un adattamento
successivo e avranno una verifica separata.

## Raccolta — VALIDATA: 1–4 PASS

Dalla directory del progetto: `./pickup-demo.sh --fresh`. Copia isolata,
movimento continuo 4x; davanti alla partenza, guardando in basso, sasso e
7 munizioni 9mm. Non serve ripetere la validazione RT-02 già accettata.

1. Tasto destro sulla pila: GUI chest Mineclonia, tooltip delle munizioni e
   tempo fermo. Esc chiude senza raccogliere.
2. Riapri e trascina le munizioni dal pannello superiore a uno slot inferiore
   vuoto: GUI chiusa, attività nativa, solo il sasso rimane a terra.
3. Esci e rilancia `./pickup-demo.sh` senza `--fresh`: solo il sasso rimane.
   Tasto destro sul sasso: raccolta diretta, nessuna GUI, nessun residuo.
4. Esci e rientra: gli oggetti raccolti non ricompaiono.

Il pannello inferiore è ancora di sola lettura, anche per indossati,
impugnati e contenuti annidati; le icone generiche sono fallback. Dettagli e
verifica automatizzata: [ground-items-ui.md](../fixes/ground-items-ui.md).

## HUD e scheda corporea — VALIDATA: 1–4 PASS

Feature indipendente dalla raccolta: `./body-demo.sh --fresh`. Personaggio
assetato/stanco, testa e braccio sinistro feriti; nessun pickup necessario.

1. Controlla il pannello in basso a sinistra: stamina e salute di testa/torso,
   con i bisogni percepiti. Non devono esserci i cuori/hotbar fittizi di Luanti.
2. Premi **H**: la scheda mostra parti del corpo e bisogni, incluse le ferite
   iniziali. Attendi e prova WASD: tempo/personaggio restano fermi.
   **Esc** o **Torna al gioco** chiude e riprende la modalità precedente.
3. Metti in pausa con **F7**, apri H e richiudi: il gioco deve restare in pausa
   finché premi di nuovo F7. Consultare la scheda H non cura né raccoglie oggetti.
4. Esci e rilancia `./body-demo.sh` senza `--fresh`: posizione e condizioni
   sono quelle del save CDDA; la scheda torna consultabile.

Entrambe le demo conservano sessioni separate dai salvataggi normali.
Entrambe le checklist sono ora accettate dall'utente.

## Corpo a corpo puntato — VALIDATA: 1–4 PASS

Feature indipendente dalle altre due: `./combat-demo.sh --fresh`. Mazza già
impugnata e zombie ostile subito davanti, immobilizzato solo nella scena di
prova. **E** riconosce la minaccia; **F7** mette in pausa/riprende.

1. Punta lo zombie: nome e suggerimento di attacco; clic sinistro per un colpo.
   Tieni poi premuto: un solo attacco, senza raffica. Ripeti con nuovi clic.
   Se la mazza lo respinge, riavvicinati: i colpi fuori portata sono rifiutati.
2. Metti in pausa con F7 e clicca: niente attacco. Riprendi: nessun colpo
   ritardato dal clic fatto durante la pausa. Il mirino nel vuoto non attacca.
3. Uccidi il bersaglio con nuovi clic: modello rimosso, cadavere nativo a terra.
   Nessun movimento verso il bersaglio causato dal clic.
4. Esci e rilancia `./combat-demo.sh` senza `--fresh`: bersaglio morto/cadavere
   coerenti con il save. Questa prova non richiede raccolta né scheda H.

Checklist accettata dall'utente, compreso il mancato avvicinamento automatico.

## Corsa e posture native — VALIDATA: 1–4 PASS

Quarta feature indipendente: `./posture-demo.sh --fresh`, copia isolata con
area iniziale priva di bersagli predisposti e senza raccolta obbligatoria;
movimento continuo 4x già approvato. Gli spawn fissi nella bolla iniziale sono
rimossi dalla sola fixture; esplorare oltre può incontrare creature native.

1. Premi **R**: pannello «Corsa», WASD più veloce e consumo maggiore di stamina.
   Ripremi R: «Cammino». Tenere R premuto non deve alternare ripetutamente.
2. Premi **X**: «Accovacciato», visuale più bassa e movimento più lento.
   Ripremi X per rialzarti; **P** dà «A terra», visuale ancora più bassa e
   strisciamento più lento. Ripremi P per camminare. Shift resta modificatore
   per chiusura porte/finestre e discesa, senza cambiare postura.
3. **F7**, poi R/X/P: niente cambio durante la pausa e niente comando ritardato
   alla ripresa. Le nuove posture non devono spostarti/teletrasportarti.
4. Lasciati accovacciato o a terra, esci e rilancia `./posture-demo.sh` senza
   `--fresh`: postura e posizione conservate. Se corri fino a esaurire la
   stamina, CDDA deve interrompere la corsa; non puoi forzare R mentre affannato.

Altezze di visuale sono un primo adattamento 3D; le animazioni del corpo/rig
in terza persona verranno completate separatamente. Tutte e quattro le prove hanno accettazione manuale esplicita.


## Adattamenti comandi e presentazione — VALIDATA: 1–4 PASS

Le quattro checklist sopra sono già accettate. Anche le quattro modifiche
successive sono state approvate esplicitamente dall’utente: `./controls-demo.sh --fresh`
(copia isolata con acqua bassa alla partenza e sasso davanti).

1. **Ctrl sinistro** tenuto: corsa; rilascio: cammino. **Shift** tenuto:
   accovacciato; rilascio: cammino. **P** resta toggle. In pausa F7 i tasti
   non devono produrre cambi ritardati. Le preferenze `cwm_run_toggle` e
   `cwm_crouch_toggle` nelle impostazioni consentono il comportamento toggle.
   Shift+tasto destro e Shift+Spazio conservano chiusura e discesa native.
2. **H**: bisogni/parti leggibili con icone; premere S più volte non seleziona
   Sete/Sonno. Il sasso e l'acqua restano fermi durante la pausa e riprendono
   alla chiusura. La pausa F7 resta attiva dopo aver richiuso H.
3. **P nell'acqua bassa**: la visuale resta sopra la superficie, senza il
   vuoto nella metà inferiore; P per rialzarsi. Questa prova non comprende
   ancora la presentazione completa dell'immersione profonda.
4. HUD: cuori separati testa/torso, icone stamina, fame descritta da CDDA,
   oggetti posseduti visibili nella barra. La barra è ancora una vista:
   numeri/rotella non equipaggiano quegli oggetti. Il toggle sdraio persiste
   nel save. Il rifiuto della corsa deve avere una spiegazione comprensibile.


## Ultimo ritocco HUD/acqua — nessun nuovo gate manuale

Su richiesta successiva: X predefinito per sdraiarsi, lieve discesa della
visuale proni in acqua bassa, HUD di icone senza pannello nero. La checklist
precedente conserva P e il vecchio HUD come descrizione della versione
validata. L’utente richiede di proseguire dopo questo ritocco senza attendere
un’ulteriore validazione estetica. Non si deduce un PASS manuale del nuovo HUD.
Eventuali osservazioni potranno essere raccolte durante le prossime feature.

## Inventario ed equipaggiamento — VALIDATA: 1–4 PASS

Accettata dall'utente il 2026-10-09; restano i bug descritti nel riscontro corrente.
Avvio dalla directory del progetto: `./equipment-demo.sh --fresh`.
Copia isolata: mazza impugnata, zaino indossato; cappello, bandana e due
sassi nelle tasche. `I` apre l'inventario anche nel gioco normale.

1. **I**: griglia, nomi al passaggio del mouse, filtri e ricerca, dettaglio
   dell'oggetto selezionato con provenienza/tasche/capacita. Tempo fermo,
   WASD non muove; Esc chiude senza equipaggiare. Le icone generiche sono
   fallback di presentazione, non oggetti diversi da quelli CDDA.
2. Seleziona cappello: **Indossa**, poi riapri I e **Togli**. Seleziona
   mazza: **Riponi** e scegli la destinazione nativa con il numero mostrato;
   prova anche **Annulla**. Poi **Impugna** un sasso: solo quello diventa
   impugnato. I vincoli e i tempi restano nativi; nessuno switch rapido gratis.
3. Con F7 in pausa, prova un'azione: non deve partire ne venire eseguita
   quando riprendi. Chiudere I non deve togliere la pausa F7. Per togliere
   lo zaino senza lasciarlo a terra, riponi prima l'oggetto impugnato:
   CDDA puo impugnare lo zaino completo; **Indossa** lo rimette con i contenuti.
   Se manca spazio e hai gia qualcosa in mano, CDDA puo lasciare lo zaino
   a terra con i contenuti: e comportamento nativo, non una cancellazione.
4. Lascia cappello indossato e un sasso impugnato; esci e rilancia
   `./equipment-demo.sh` senza `--fresh`. Controlla equipaggiamento e
   contenuti: nessuna perdita, duplicazione o ricomparsa delle vecchie copie.

Quantita parziali, trasferimenti mirati tra tasche/contenitori, apertura di
tasche sigillate e hotbar interattiva vengono dopo: non sono implementati
in questa prima fetta. [Dettagli e verifica tecnica](../fixes/native-equipment.md).


## Cibo e bevande nativi — VALIDATA: 1–4 PASS

Accettata dall’utente il 2026-10-09 insieme alla checklist inventario.
Avvio isolato: `./consumption-demo.sh --fresh`. Zaino gia fornito dal core
nativo con due mele fresche, una marcia, una bottiglia con quattro porzioni
d'acqua pulita e un sasso. La stessa funzione e disponibile con I nel gioco.

1. **I**, scegli una mela fresca: dettagli e **Mangia**; scegli l'acqua nella
   bottiglia: **Bevi**. Il sasso non deve offrire Consuma. Consultare i dettagli del menu mantiene
   tempo/personaggio fermi (non si tratta della lettura di libri). Mangia/Bevi chiudono il menu e avviano un consumo
   con indicazione di progresso; una sola porzione si toglie alla fine.
2. Durante una mela premi **I**: il progresso si ferma col menu; **Interrompi
   consumo** torna al gioco, conservando la porzione non ancora consumata.
   Avvia poi nuovamente Mangia e lascia terminare. La durata della nuova
   richiesta segue il comportamento CDDA del pin, senza rimborso del tempo
   gia trascorso. I bisogni si aggiornano attraverso digestione nativa, non
   con una cura istantanea inventata dalla GUI.
3. Seleziona la mela marcia: avviso nel dettaglio, conferma nativa dopo
   Mangia. Scegli **No** con il numero mostrato: mela conservata, nessuna
   attivita bloccata. Con **F7** in pausa, prova Mangia/Bevi: niente comando
   ritardato dopo la ripresa; chiudere I conserva la pausa F7.
4. Bevi una porzione e mangiane una, esci e riavvia `./consumption-demo.sh`
   senza --fresh: bottiglia/quantita e bisogni restano coerenti, senza
   duplicazioni. Puoi anche uscire durante un consumo: il save mantiene
   l'attivita nativa; al rientro il tempo riprende da quel lavoro residuo.

Farmaci/medicazioni, bere da fontane, aprire tasche sigillate, scegliere
quantita e travasare richiedono le prossime fette. Le icone mancanti restano
fallback con nomi CDDA. [Dettagli tecnici](../fixes/native-consumption.md).


## Medicazioni native — VALIDATA: 1–4 PASS

Inventario/consumo e queste medicazioni sono accettati il 2026-10-09. Avvio isolato:
`./medicine-demo.sh --fresh`. Braccio sinistro e torso feriti; nello zaino
ci sono tre bende, una salvietta disinfettante e una benda sporca. Non serve
raccogliere o mangiare nulla. La funzione e disponibile anche con **I** nel gioco.

1. **I**, scegli una benda e **Medica...**: CDDA propone le parti trattabili
   con salute ed effetti conoscibili. Scegli usando il numero mostrato, poi
   conferma. Annulla una volta la scelta e una volta la conferma: nessuna
   benda consumata. La benda sporca e il sasso non offrono Medica.
2. Avvia la benda sul braccio sinistro. Il trattamento mostra progresso;
   **I** lo ferma e **Interrompi trattamento** conserva la benda inutilizzata.
   Una nuova richiesta segue la ripresa nativa, senza rimborso del tempo.
   Movimento o altre azioni non devono partire in ritardo dopo la cura.
3. Lascia terminare la benda; usa la salvietta sul torso. **H** mostra
   bendaggio e disinfezione sulle parti scelte. Una benda/salvietta viene
   consumata al completamento. Non aspettarti cuori recuperati subito:
   questi oggetti favoriscono la guarigione nel tempo. In pausa **F7** il
   clic Medica non deve diventare un comando differito alla ripresa.
4. Esci e riavvia `./medicine-demo.sh` senza --fresh: oggetti e condizioni
   restano coerenti. Prova anche a uscire durante una medicazione: al
   rientro riprende il lavoro residuo e consuma il trattamento una sola volta.

Questa fetta copre gli oggetti esterni non commestibili con attore heal:
bende, salviette e analoghi. Farmaci ingeribili, antisettici liquidi, cura di
NPC, chirurgia e avvio parte→oggetto dalla scheda H restano successivi.
[Dettagli tecnici](../fixes/native-medicine.md). Checklist 1–4 accettata dall’utente il 2026-10-09; nuove correzioni da ricontrollare.


## Crafting guidato — VALIDATA: 1–4 PASS

Dalla directory del progetto: `./crafting-demo.sh --fresh`. Scena e salvataggio
isolati; K apre il catalogo CDDA. Non serve completare le altre checklist.

1. K: ricerca `bandage`, seleziona la ricetta senza utensile e leggi
   materiali, luce/competenze, fonti e durata. Lotto 1–20 aggiorna i requisiti.
   Il tempo resta fermo nella GUI; Esc esce senza creare né consumare materiali.
2. Avvia lotto 1: scegli materiale/fonte con i numeri della decisione nativa.
   Rifiuta la conferma finale e verifica che non compaiano lavori/risultati;
   ripeti confermando. Il foglio preferito non deve essere consumato.
3. Avvia lotto 2, apri K o I durante il progresso, attendi e verifica la pausa;
   interrompi. K mostra il lavoro incompleto marcato R, da riprendere senza
   ricomprare i componenti. Al termine controlla in I le quattro bende prodotte.
4. Avvia un altro lotto 2 e chiudi il gioco mentre il lavoro è in corso (K per
   fermare il tempo prima di uscire). Rilancia `./crafting-demo.sh` senza --fresh:
   riprende il lavoro salvato e lo completa una sola volta. Se cambi stanza/
   materiali, una ricetta senza requisiti deve spiegare perché non è avviabile.

Checklist 1–4 accettata dall’utente il 2026-10-09; il badge R segnalato
ha un ricontrollo separato. Questa prima fetta
non include ricette liquide, sottoprodotti, pratica, preferiti di ricette,
collegamenti di sottoricette, selezione della singola istanza fra oggetti
identici né accelerazione automatica delle attività lunghe: restano nel piano.

## Tiro, mira e ricarica — VALIDATA: 1–4 PASS

Avvio isolato: `./ranged-demo.sh --fresh`. Pistola già impugnata con tre
colpi; trenta munizioni 9mm nello zaino, variante FMJ compatibile e munizioni
incompatibili. Zombie immobilizzato davanti a quattro caselle, cane amico
sulla destra. Nessuna raccolta/equipaggiamento obbligatorio.
**E** riconosce la minaccia iniziale e riprende dopo l'autopausa.

1. Punta lo zombie: nome dell'arma, colpi e rinculo. Tieni **F**: il rinculo
   diminuisce pagando tempo nativo; rilascia F e **clic sinistro** per sparare.
   Tieni il mouse: un solo colpo, nessuna raffica automatica. Clic nel vuoto
   o sul cane non spara. Il tiro non avvicina il personaggio al bersaglio.
2. **F7** in pausa, poi F/clic/R: nessuna azione né miglioramento gratuito
   della mira. Rilascia i tasti e riprendi: nessun comando ritardato. Aprire
   **H** o **I** mantiene tempo e mira fermi, chiudere conserva la pausa F7.
3. **R**: scelta nativa di munizioni e conferma. Annulla la scelta e rifiuta
   una conferma: nessuna munizione trasferita. Conferma poi 9mm; **I** durante
   il progresso ferma il tempo. **Interrompi ricarica** conserva i colpi;
   ripeti e lascia completare. Movimento/tiro non devono partire in ritardo.
4. Esci e rilancia senza --fresh: arma e munizioni persistono senza duplicati.
   Prova anche a uscire durante una ricarica (I per fermare il tempo prima
   dell'uscita): al rientro il lavoro nativo residuo completa una sola volta.

Questa prima fetta copre armi da fuoco impugnate e modalità balistica corrente,
bersagli ostili percepiti e ricarica nativa. Mirino libero, tiro deliberato su
neutrali, archi/carica-e-spara, armi montate/veicoli e cambio modalità restano
nel piano. Accettata dall'utente il 2026-10-09; nuvole, arma/audio e feedback
del rinculo restano segnalazioni aperte. RMB mantenuto è la nuova richiesta,
non il comportamento di F descritto dalla versione validata qui sopra.


## Quantita, deposito e contenitori posseduti — VALIDATA: 1–4 PASS, con riserva sul deposito annidato

Avvio isolato: `./transfer-demo.sh --fresh`. Trenta munizioni 9mm, sacchetto
vuoto, bottiglia vuota, mazza e sasso gia nello zaino. Non serve raccogliere,
combattere o completare altre checklist. Nel gioco normale: **I → Quantita e
trasferimenti**. Questa fetta permette destinazioni possedute e terra sotto
il personaggio; contenitori esterni e scelta della singola tasca vengono dopo.

1. Apri I e **Quantita e trasferimenti**: pannello sinistro degli oggetti,
   destro dei contenitori. Scegli munizioni, sacchetto, quantita 7. Attendi o
   premi WASD: tempo/posizione restano fermi. Prova 31, zero o testo non numerico:
   niente trasferimento. Esc chiude senza spostare oggetti.
2. Conferma 7 nel sacchetto: menu chiuso, lavoro nativo e tempo pagato.
   **I** durante il lavoro ferma il progresso; **Interrompi trasferimento**
   conserva le munizioni non ancora spostate. Ripeti e lascia completare:
   7 nel sacchetto e 23 nella tasca precedente. Riapri I per la provenienza.
   Prova mazza → bottiglia: rifiuto nativo, nessun oggetto perso.
3. Seleziona le munizioni dentro il sacchetto, quantita 3, **Deposita a terra**:
   3 sotto il personaggio, 4 nel sacchetto, 23 altrove nello zaino. Deposita poi
   il sacchetto intero: rimane a terra con le 4 munizioni dentro. Gli oggetti
   indossati richiedono prima Togli; liquidi/sigilli richiedono altre interazioni.
   Con **F7** in pausa un clic di trasferimento non deve partire alla ripresa.
4. Esci e rilancia senza --fresh: quantita e contenuti persistono senza copie
   aggiuntive. Prova anche a uscire durante l'inserimento di 7 munizioni
   (I per fermare il tempo prima di uscire): il lavoro nativo salvato riprende
   e sposta le 7 una sola volta. Per rifare la scena usa --fresh, che crea
   una nuova copia isolata e conserva le sessioni demo precedenti.

L'utente dichiara 1–4 PASS il 2026-10-09, ma non è riuscito a depositare le
munizioni direttamente dal sacchetto: quel sottocaso resta da ricontrollare.
Quantità sovrapposta, tag hint ed errori poco visibili rimangono bug aperti.
[Dettagli tecnici](../fixes/native-transfer.md).


## Ricontrolli mirati del riscontro UI e mapping — 1–4 PASS manuali (2026-10-13)

I 16 PASS precedenti restano acquisiti. Non occorre ripeterli né fare queste
prove oggi. La revisione completa dell'interfaccia è pianificata: il layout
attuale resta provvisorio.

1. **Tag colore**: `./equipment-demo.sh --fresh`, I → mazza → Riponi:
   nome dello zaino leggibile, senza `<color_...>`/`</color>`. Stesso controllo
   quando appare una conferma nel consumo. Simboli `++` e testo conservati.
2. **Recupero depositati**: I → Quantità e trasferimenti → deposita un
   piccolo oggetto; tasto destro lo raccoglie se entra nelle tasche.
   Prova anche una mazza/zaino che non entra: compare una spiegazione e
   scelta esplicita Impugna/Annulla (se impugnabile). Annulla conserva
   l'oggetto; Impugna lo recupera con i costi nativi. Uno zaino recuperato
   mantiene i suoi contenuti. Esci/rientra: nessuna copia o perdita.
3. **Badge crafting**: interrompi un lavoro in `./crafting-demo.sh --fresh`;
   K mostra R interamente dentro lo slot. Clic sul badge seleziona il lavoro,
   non lo avvia senza il pulsante Riprendi.

4. **Mapping aggiornato**: nella demo consumo la mela deve avere la sua
   icona, l’acqua pulita una goccia (non una mela) e la mela marcia una tinta
   diversa più un segnale `!`, mantenendo nome/stato nativi; nella demo crafting le bende improvvisate usano il proxy di cuoio
   scelto nel batch. Tooltip/nome devono indicare sempre il vero oggetto CDDA.
   Zaino e mazza possono ancora usare il fallback: non tutti i record hanno
   un asset pronto. Nessun cambiamento atteso a quantità, tempi o salvataggi.

Le revisioni successive UX-02–05 avranno checklist proprie alla consegna.


## UX-01 — Nuovo inventario Mineclonia — VALIDATA: 1–4 PASS

Il nuovo layout è disponibile anche con **I** nel gioco normale. Tutti i
quattro test accettati con errata corrige del 2026-10-09. La ricerca su
richiesta descritta sotto è storica: l'utente ora la vuole visibile ma senza
focus, attivata su clic e disattivata cliccando altrove. Modifica pianificata.

1. `./equipment-demo.sh --fresh`: **I** mostra griglia 9×3, mano vera,
   indossati e fila inferiore distinta. La ricerca non è attiva all'apertura:
   clic **Cerca...**, digita `cap`, poi **Cerca**/Invio. Primo **Esc** lascia
   la ricerca mantenendo inventario/tempo fermi; secondo Esc torna al gioco.
   Non equipaggi niente con un semplice clic sulle icone.
2. Seleziona lo zaino: scheda breve leggibile, **Tasche e dettagli...** apre
   capacità, contenuti e costi nella zona scorrevole; **Meno dettagli** riduce.
   Prova Tutti/Equipaggiati/Contenitori e selezione da mano/indossati/barra.
   Tooltip distinguono icone di categoria e mapping/proxy, col nome CDDA vero.
   I contenuti dello zaino rimangono nell'inventario anche quando lo impugni:
   la provenienza dice **In mano > zaino > tasca**. Non sono copie aggiuntive.
3. `./equipment-demo.sh --pages --fresh`: scena isolata di stress con 52
   oggetti e 12 indossati (strati predisposti dalla fixture debug, non
   ottenuti eludendo le normali regole Indossa). Usa entrambe le coppie di
   frecce, seleziona un oggetto di pagina 2, chiudi/riapri I e **Aggiorna**.
   Pagina/filtro/ricerca restano; la selezione viene azzerata nelle nuove viste
   per non riusare ID scaduti. Cerca `bandana` e controlla nomi e leggibilità.
4. Nella demo normale seleziona cappello → **Indossa**, poi **Togli**;
   mazza → **Riponi** (anche Annulla), sasso → **Impugna**. I pulsanti restano
   nel pannello a destra e i vincoli nativi valgono sempre. **F7** blocca le
   azioni senza eseguirle alla ripresa. Esci/rientra: equipaggiamento e
   contenuti conservati. La barra inferiore seleziona soltanto: switch rapido
   è ancora un passo successivo; il ritorno automatico è ora coperto da UX-02.

La sagoma non riproduce ancora i vestiti reali e l'elenco degli indossati
non è ancora raggruppato per parte del corpo. Le coperture/impedimenti
richiedono dati CWM tipizzati; non vengono dedotti dal nome dei vestiti.


## UX-02 — Azioni consecutive con costi nativi — VALIDATA: 1–4 PASS dichiarati, eccezioni separate

Accettazione del flusso ordinario dichiarata dall'utente il 2026-10-09.
Morte/IPC/schermate native non effettivamente provati: vedere prove separate
sotto. Una singola azione esplicita lascia scorrere il mondo, poi riapre la
vista dell'inventario. Pagina/filtro/ricerca restano; oggetto e destinazione
vanno riselezionati perché le vecchie identità native sono scadute.

1. `./equipment-demo.sh --fresh`: I → Cerca `cap` → seleziona cappello →
   **Indossa**. Durante il lavoro appare un indicatore compatto; al termine
   I torna automaticamente, mantenendo la ricerca. Seleziona di nuovo il
   cappello → **Togli**; poi un sasso → **Impugna**, scegliendo esplicitamente
   come riporre la mazza nel dialogo nativo. Tutte e tre le azioni devono
   finire davvero prima del ritorno; consultare I continua a fermare il tempo.
2. `./consumption-demo.sh --fresh`: mangia una mela. L'indicatore mostra
   progresso e il mondo continua. **I** durante il pasto mette in pausa;
   **Interrompi** segue la cancellazione nativa, conserva il cibo non ancora
   consumato e torna a I dopo il costo già pagato. Ripeti lasciando finire:
   una sola porzione consumata e ritorno automatico. Prova l'acqua e annulla
   l'avviso della mela marcia: nessuna scelta automatica né oggetto consumato.
3. `./transfer-demo.sh --fresh`: I → **Quantità e trasferimenti**, deposita
   poche munizioni oppure inseriscile nella borsa. Alla fine deve tornare
   questo pannello, con quantità/contenuti reali aggiornati e selezioni
   azzerate. Nella demo equipaggiamento puoi usare F8 per rallentare a 0,5×:
   **Esc durante il lavoro** lascia il mondo aperto senza annullare l'azione;
   F7 blocca il tempo e, dopo la ripresa, non forza I. Le minacce e le
   decisioni native hanno precedenza sull'inventario.
4. Esci/rientra dalla demo senza `--fresh`: arma, vestiti, cibo e trasferimenti
   completati rimangono nel save nativo. Se esci mentre un'attività lunga è
   ferma in I, il lavoro resta nativo e può riprendere: nessuna duplicazione,
   nessun ritorno automatico a una vecchia selezione della sessione precedente.
   In caso di morte o perdita/recupero IPC, la vecchia intenzione di ritorno
   viene scartata; le schermate native restano prioritarie.

## UX-02 — Eccezioni non provate — PENDING (3), rinviabili

Nessun obbligo di eseguirle oggi; non ripetere i flussi ordinari già accettati.
L'agente deve predisporre scene/istruzioni controllate prima di proporre prove
di errore: non chiedere di terminare processi della partita personale.

1. **Minaccia e decisione nativa**: durante un lavoro, un avviso o una domanda
   CDDA ha precedenza sul ritorno a I. Il menu non risponde da solo né riparte
   senza la scelta esplicita; la minaccia mantiene la pausa prevista.
2. **Morte**: nella demo di combattimento isolata, morte durante il lavoro
   mostra la UI nativa; il vecchio inventario non riappare sopra la morte.
3. **IPC**: nella fixture di recupero isolata, perdita e ripristino della
   connessione non riaprono una vecchia selezione e non duplicano il lavoro.
   Nessun input di gioco parte mentre manca lo stato autorevole completo.


## UX-03 — Hotbar con drag-and-drop — 1–4 PASS manuali (2026-10-13)

Il precedente punto **1 FAIL di ergonomia** riguarda la versione a pulsanti
CWM 2.17, conservata nel [riscontro](../source/ux03-drag-feedback-2026-10-09.md)
e nel [report storico](../fixes/interactive-quickbar.md). UX-03D/CWM 2.18
rimuove quei due pulsanti e riscrive soltanto la prova 1. **2–4 sono ancora
non testati**; la disposizione della griglia viene ora compresa nella prova 4.

Disponibile con I anche nel normale `./start.sh`: movimento continuo 4×
predefinito. `./equipment-demo.sh --fresh` crea una copia isolata con mazza,
zaino, cappello e sassi. Gli slot inizialmente vuoti sono riferimenti rapidi,
non tasche nuove. Non occorre ripetere i PASS inventario/equipaggiamento.

1. **Trascina, scambia, rimuovi**: I non deve mostrare Assegna/Svuota.
   Trascina mazza, cappello e un sasso dalla griglia negli slot 1, 2, 3:
   le istanze assegnate lasciano la griglia principale, senza copie o perdita.
   Trascina 2 su 3: i riferimenti devono scambiarsi; ripeti per ripristinarli.
   Trascina la mazza dallo slot 1 su una casella vuota della griglia:
   scompare solo il riferimento rapido, la mazza resta in mano/posseduta.
   Prova Esc durante un gesto e rilascio fuori dal menu: nessun deposito.
   Un clic breve continua a selezionare/aprire i dettagli.
   Fuori da I, icone coerenti con l'inventario; selezione **oro**, mano reale
   **azzurra**. L'oggetto in mano compare anche nel riquadro separato a destra
   quando non è assegnato a uno slot.(commento manuale da me: quando faccio drag and 
   drop l'interfaccia si chiude e si apre velocemente in modo fastidioso, io 
   toglierei questa cosa.)
2. **Seleziona e usa**: rotella oppure 1–9 selezionano senza equipaggiare.
   **3, poi G** richiedono Impugna del sasso; scegli esplicitamente dove
   riporre la mazza. **2, poi G** indossano il cappello, un nuovo G lo toglie.
   Tempo/costi sono nativi; G dal mondo non forza il ritorno automatico a I.
   In I puoi scegliere le altre azioni con i pulsanti del dettaglio.(commento manuale
   dopo testing: quando tolgo o indosso qualcosa mi dice "in progress" e mi fa
   attendere ma non mi dice il progresso attuale. Non so se è intended, ma prima
   mi ricordo che la percentuale di progresso era presente. Devo ancora capire 
   cosa ha senso)
3. **Pausa, lavoro e perdita**: F7 → G non usa né accoda; riprendendo non
   parte un'azione ritardata. G durante un'attività non accoda altre azioni.
   Deposita un oggetto assegnato usando I → Quantità e trasferimenti: il
   riferimento scompare; raccoglierlo di nuovo non lo riassegna da solo.
   Nella demo consumo puoi assegnare una mela: G mangia la precisa mela
   scelta; quando consumata, il riferimento non passa a una mela omonima.(commento
   manuale dopo il testing: la mela mangiata con G funziona e ho notato che qui
   la percentuale di progresso è corretta e funzionante mentre prima non era così
   per il wearing, forse è solo nel consumption demo che funziona e nelle altre no?
   da indagare. EDIT: no, il progress bar e percentage nel wearing non funziona
   neanche in consumption demo)
4. **Persistenza**: lascia cappello/sasso assegnati e almeno uno indossato o
   impugnato; esci e rilancia `./equipment-demo.sh` senza `--fresh`. I e HUD
   devono conservare gli stessi oggetti, non i primi della nuova lista.
   Prima di uscire riordina anche due oggetti non assegnati nella griglia:
   trascina uno su un altro per inserirlo prima; su uno spazio vuoto lo porti
   alla fine. Al riavvio l'ordine resta. Non è una griglia con buchi salvati,
   né uno spostamento fra tasche. Rimozione/riassegnazione rimangono coerenti,
   senza duplicazioni.

## UX-03D — Mano, indossati e contenitori — 1–2 PASS manuali (2026-10-13)

1. **Equipaggiamento col gesto**: `./equipment-demo.sh --fresh`, I.
   Trascina il cappello dalla griglia in uno spazio Indossati, poi dal
   pannello Indossati a una casella vuota della griglia: Indossa/Togli nativi,
   tempo che scorre durante l'azione e ritorno a I soltanto dopo il costo.
   Trascina la mazza dal riquadro In mano alla griglia; prova Annulla sulla
   scelta CDDA, poi ripeti scegliendo dove riporla. Trascina un sasso in mano.
   In F7 il gesto fisico è rifiutato senza esecuzione ritardata alla ripresa.
   Riordinare/assegnare riferimenti rimane una scelta grafica gratuita.
2. **Contenitori e Terra**: `./transfer-demo.sh --fresh`, I → Quantità e
   trasferimenti. Seleziona le 30 munizioni, imposta 7 e trascinale sulla
   riga del sacchetto: al termine 7 dentro, 23 nella sorgente originale.
   Seleziona la voce delle munizioni annidate (non il sacchetto), imposta 3
   e trascina su **Terra**: 4 restano dentro. Trascinare poi il sacchetto su
   Terra deve depositarlo con il contenuto. La mazza sulla bottiglia mostra
   un rifiuto evidente e conserva la mazza. Fuori dal menu/Esc annullano;
   deposito solo sulla zona esplicita Terra. Nel pannello principale puoi
   trascinare un oggetto trasferibile sull'icona di un contenitore, senza
   aprire questa sottovista; per quantità precise usa il pannello avanzato.
   Le destinazioni evidenziate restano soggette alla verifica di capacità CDDA.
   (commento manuale dopo test: io metterei i rettangoli dei container in quantità
   e trasferimenti più grandi per il drag and drop, per il resto tutto bene per ora)

## Ricontrolli UX-03 — VALIDATA: 1–3 PASS

Accettati dall’utente nel riscontro più recente. Conservati sotto per
cronologia; non serve ripeterli per il solo FAIL ergonomico della hotbar.

1. **Ricerca**: I mostra da subito il campo vuoto. Digitare prima di cliccarlo
   non scrive nel campo. Clic sinistro sul campo abilita digitazione e cambia
   colore del testo; Cerca/Invio filtra. Clic su uno slot o sullo sfondo lascia
   il focus: altri tasti non si aggiungono alla ricerca. Esc mentre scrivi
   lascia prima il campo; un nuovo Esc chiude I.
2. **Nuvole e pausa**: in una scena con cielo visibile e nuvole abilitate,
   controlla che nuvole, acqua e oggetti rotanti si fermino in F7 e in H/I;
   alla ripresa tornano a muoversi. Non serve attendere meteo diverso.
3. **Quantità ed errori**: `./transfer-demo.sh --fresh`, I → Quantità e
   trasferimenti: etichetta Quantità e frecce pagina non si sovrappongono.
   Inserire la mazza nella bottiglia deve lasciare il rifiuto ben visibile,
   conservando la mazza. Per depositare munizioni dal sacchetto, seleziona
   **la voce delle munizioni nella lista di sinistra**, verifica il percorso
   della sorgente nei dettagli, inserisci quantità positiva e premi Deposita.
   Selezionare il sacchetto deposita invece il contenitore con i contenuti.

Le verifiche automatiche su renderer e core di riferimento sono registrate
nel [report UX-03](../fixes/interactive-quickbar.md); non costituiscono PASS
manuali. La lingua ha ora la checklist separata sotto; mira RMB, UV/rig,
animazioni e suoni restano nel piano.

## LANG-01 — Lingua del prodotto — 1–2 PASS; logica riconfermata dopo `971579f`

Disponibile dal normale `./start.sh`; non serve fare queste prove oggi.
I PASS precedenti rimangono accettati. Le prove automatiche delle due lingue
non attestano la tua accettazione della leggibilità e del menu.
[Comportamento e impostazioni](../design/product-language.md).

1. **Inglese predefinito**: senza una preferenza di prodotto già scelta,
   `./start.sh` apre in inglese, indipendentemente dalla lingua del sistema.
   Controlla I, H e K: etichette inglesi, nomi/descrizioni nativi inglesi e
   ricerca funzionante. Per una scelta nativa annullabile puoi usare la
   demo isolata di equipaggiamento: Riponi della mazza, poi Cancel.
   Se hai già scelto italiano, Esc → Language → English, esci e riavvia.
2. **Italiano WIP e ritorno**: Esc → Language / Lingua → Italiano (WIP).
   La partita corrente mantiene la lingua iniziale. Esci e riavvia lo
   stesso `start.sh` o la stessa demo senza `--fresh`: I/H/K usano italiano,
   con fallback inglese per testi nativi non ancora tradotti. Nella demo,
   il cappello e lo zaino hanno nomi italiani, e Riponi offre Annulla.
   Riporta il selettore su English e riavvia: la scelta persiste e anche
   i testi nativi tornano inglesi. Il cambio lingua non riordina né duplica
   gli oggetti e non cancella i salvataggi. Non serve ripetere i vecchi
   test di persistenza o tutte le azioni inventario già validate.(commenti manuali
   dopo testing: ma non si potrebbe fare che quando si cambia la lingua il 
   restart non sia necessario?)
   (commenti manuali fatti dopo i test: dopo aver impostato italiano e riavviato
   viene cambiato in italiano, ma poi nel menu a tendina se ripremo sulla freccetta
   e seleziono inglese non me lo cambia e se riavvio il gioco rimane in italiano)

**Riparazione del FAIL LANG-01.2, poi accettata dall'utente:** gli overlay del renderer vengono
ora nascosti per tutti i menu modali, incluso Esc. Il filtro del buio non deve
intercettare il clic su English e convertirlo in una chiusura. Ricontrolla il
punto 2 anche in un interno buio: clic su English, menu ancora aperto/tempo
fermo, poi uscita e riavvio con lingua inglese. Dopo `971579f` l'utente conferma
«ora la logica funziona»: il FAIL è chiuso per questo riscontro umano.
La nota fissa poco chiara ha un ricontrollo distinto in fondo; non occorre
ripetere tutti gli altri test.

## AIM-01 — Mira con destro mantenuto — VALIDATA: 1–3 PASS (2026-10-18)

Questa checklist conserva il binding della versione accettata. Il nuovo RMB
per aprire e chiudere è nel ricontrollo INT-01 sotto e sostituisce Shift+RMB.

Non serve fare queste prove oggi. [Regole e priorità](../design/held-mouse-aim.md).
La demo isolata è `./ranged-demo.sh --fresh`; il comportamento è disponibile
anche da `./start.sh` con un'arma da fuoco realmente impugnata. Rilascia i tasti
prima di riprendere da una pausa di minaccia. F resta una scorciatoia alternativa.

1. **Mira e sparo**: punta lo zombie della demo e tieni il destro. Il suggerimento
   mostra In mira/Aiming e il rinculo nativo diminuisce pagando tempo. Clicca
   sinistro continuando a tenere il destro: parte un solo tiro per clic, e poi
   la mira riprende senza dover ripremere F/destro. Tenere il sinistro non crea
   raffiche nuove. Rilascia il destro: non arrivano altri passi di miglioramento.
   La precisione già pagata può restare finché non ti muovi/fai altro. R ricarica
   con scelte e costi nativi; dopo il lavoro rilascia e ripremi destro per mirare.
   (commenti manuali dopo aver testato: io farei che lasciando il tasto destro
   la mira sparisce proprio, non che è un tasto toggle, ma possiamo discuterne,
   tu che ne pensi? quali sarebbero le ripercussioni a livello di design? inoltre
   mentre si tiene il tasto mira premuto ci si può muovere? Nel caso, ha senso
   permettere di muovere mentre si tiene mirato?)
2. **Interazioni**: nella partita normale o demo di controlli, RMB apre porte e
   finestre; Shift+RMB le chiude (per una finestra aperta punta il davanzale).
   RMB sugli oggetti a terra raccoglie/apre la raccolta; tenere quel clic non
   trasforma l'interazione in mira spostando il puntamento. Con arma da fuoco,
   un ostile direttamente nel mirino ha priorità di mira. Shift per accovacciarti
   non impedisce di mirare all'ostile. I vecchi PASS di apertura/raccolta restano
   accettati: questa è una prova dell'ergonomia dopo il nuovo binding.
3. **Pausa e bersagli**: tenendo destro, apri H/I o usa F7, poi chiudi/riprendi
   continuando a tenerlo: nessuna mira/sparo nascosto; rilascia e ripremi per
   ripartire. In pausa il rinculo non migliora e le munizioni non calano.
   Puntare il cane amico o il vuoto non genera passi di mira pagati né colpi.
   Il controllo automatico include reconnect; non devi interrompere IPC a mano.


## EXT-01 — Contenitori esterni e raccolta parziale — VALIDATA: 1–4 PASS (2026-10-18)

Prova isolata: `./storage-demo.sh --fresh`. Le partite normali aperte con
`./start.sh` ricevono la stessa interazione. Senza `--fresh` la demo riapre
il proprio salvataggio e non usa la tua partita. Gli armadietti usano per ora
una cassa come modello proxy; il contenuto e le regole sono quelli CDDA.

1. **Aprire e leggere.** Punta l'armadietto con munizioni/zaino vicino allo
   spawn e premi RMB: due griglie a nove colonne, contenuto esterno e tuo
   inventario. Il contenuto del mobile non gira fuori come drop. Anche
   l'armadietto vuoto è interattivo. Leggere lascia tempo e personaggio fermi;
   gli oggetti sfusi continuano a comparire come drop.
2. **Quantità e deposito.** Clic sulla pila di 30 munizioni, Quantity=7,
   trascina nella zona Collect here del tuo pannello o in una sua casella
   vuota. Dopo il costo nativo ritorna il menu con 23 rimaste fuori. Deposita
   alcune munizioni nella zona Deposit here del pannello esterno: finiscono
   nel mobile puntato, non sotto il personaggio. Nessuna duplicazione.
3. **Tasche reali e rifiuti.** Trascina munizioni sull'icona dello zaino a
   terra: sono contenute nelle sue tasche. Raccogli il sasso annidato senza
   raccogliere lo zaino. La mazza nella bottiglia deve fallire conservando gli
   oggetti e mostrando la ragione; una quantità eccessiva e la cassa sigillata
   non devono aggirare le regole. L'apertura dei sigilli arriverà separatamente.
4. **Pausa e persistenza.** F7 impedisce nuove raccolte/trasferimenti: dopo
   il rilascio della pausa il tentativo rifiutato non si esegue da solo.
   Esegui raccolta/deposito validi, chiudi, riavvia la stessa demo senza
   `--fresh`: quantità, contenuti annidati e posizione devono essere mantenuti.

Questa checklist non richiede prove oggi. Nessun PASS è dedotto dai test
automatici; tutti i PASS già dichiarati nelle sezioni precedenti rimangono.


## UX-04A — Dialoghi nativi e feedback del lavoro — VALIDATA: 1–4 PASS (2026-10-18)

Le interfacce sono disponibili nel normale `./start.sh`. Per prove isolate usa
`./consumption-demo.sh --fresh` e `./medicine-demo.sh --fresh`: non aprono la
tua partita. I dialoghi conservano scelte e testo CDDA; le icone anatomiche e
la scheda medica strutturata sono ora disponibili in UX-04B; la checklist originale rimane da provare.

1. **Conferma leggibile.** Nella demo consumo scegli la mela marcia: pannello
   chiaro, testo/colori/scorrimento e pulsanti leggibili, senza tag grezzi o
   overlay di debug sul testo. Mouse e numeri 1–9 scelgono; Invio da solo non
   approva. No oppure Esc devono conservare il cibo e tornare all'inventario.
2. **Due domande consecutive.** Nella demo medicina scegli una benda e una
   parte del corpo. Tenere premuto il numero usato per scegliere la parte non
   deve confermare anche la domanda successiva: serve rilascio e nuova
   pressione. Esc sul selettore o sulla conferma annulla secondo CDDA, senza
   consumo/cura. Il testo completo di una scelta lunga resta nel tooltip.
3. **Consulta, riprendi, interrompi.** Approva esplicitamente una medicazione:
   il pannello temporaneo indica operazione/oggetto e progresso nativo quando
   disponibile. I consulta e mette in pausa; chiudere I riprende il lavoro.
   Interrompi annulla l'actor, conservando i costi già pagati. Nessuna cura o
   consumo mentre leggi il dialogo; il lavoro finito non viene presentato come
   un successo inventato dal client.
4. **Ripetizioni e lingua.** Ripeti conferme/annullamenti con clic rapidi:
   nessuna doppia azione o risposta applicata alla domanda sbagliata. Prova
   English e, quando vuoi, Italiano WIP riavviando dal menu delle impostazioni:
   la semantica di Esc e delle scelte resta uguale, anche con etichette tradotte.

I vecchi PASS rimangono. Le eccezioni UX-02 morte/IPC non provate restano nelle
loro sezioni: queste prove e l'automazione non deducono la tua accettazione.


## Ricontrolli commenti del 2026-10-13 — VALIDATA: 1–3 PASS (2026-10-18)

1. **DND senza vista vuota:** equipment-demo --fresh, I; riordina griglia,
   assegna/scambia/svuota hotbar. Durante l’attesa della risposta la griglia
   resta visibile, poi si aggiorna senza mostrare il pannello vuoto di lettura.
   Le azioni fisiche mantengono invece i costi nativi e la pausa/ritorno.
2. **Indossa/Togli — PASS personale T1, supera il FAIL:** in
   `./equipment-demo.sh --fresh`, indossa e togli un capo. Il cambiamento è
   immediato; il pannello indica il tempo nativo restante in secondi di gioco,
   senza una barra di vestizione o pulsante Interrompi. Premi I anche subito
   dopo la scelta: deve aprirsi e mettere in pausa il tempo residuo; il capo
   risulta già indossato/tolto. Chiudi: riprende lo stesso costo senza annullare
   il cambio né riavviarlo. Per renderlo più osservabile puoi ridurre la velocità
   con F8 prima di aprire I. Nessun ritardo finto. La mancanza di annullamento
   è ora voluta: decisione esplicita dell'utente dopo verifica del codice nativo.
   Le vere attività (medicazione/crafting ecc.) conservano invece Interrompi.
3. **Destinazioni più grandi:** Quantità e trasferimenti mostra sei contenitori
   per pagina con righe più alte. DND e clic selezionano la destinazione giusta;
   se ce ne sono di più, le frecce permettono di raggiungerli. Capacità e quantità
   conservano la validazione CDDA.

**LANG-01 punto 2 — PASS ricevuto il 2026-10-18:** accettato il ritorno a
English con i pulsanti espliciti e riavvio. Il FAIL precedente è storico;
non è una nuova prova pendente. Cambio a caldo rinviato.

## UX-04B — Scheda medica strutturata — VALIDATA: 1–4 PASS (2026-10-18)

Prova isolata: `./medicine-demo.sh --fresh`; disponibile anche in start.sh.

1. **Parti e cuori:** I → benda → Medica/Treat mostra icone anatomiche proxy,
   cuori e descrizioni leggibili. Le parti sane/non pertinenti sono consultabili
   ma non selezionabili per quell’oggetto. Nessuna cura mentre leggi.
2. **Scelta esplicita:** scegli con mouse una parte ferita; la conferma riguarda
   quella parte e quella precisa benda. No/Esc conservano oggetto e stato;
   tenere un numero premuto non approva la domanda successiva.
3. **Effetti conoscibili:** confronta benda e salvietta. Bandaggio/disinfezione,
   benefici e limiti sono quelli nativi; nessuna promessa di HP immediati.
   Scorrimento permette di leggere tutte le parti/descrizioni. Le parti con
   salute non conoscibile o fratture mantengono una descrizione qualitativa.
4. **Lavoro e persistenza:** approva una medicazione; I pausa, chiudi per
   riprendere, controlla il risultato con H. Salva/riapri la demo senza --fresh:
   oggetti e condizione persistono senza doppia cura. Italiano WIP può avere
   descrizioni inglesi dove manca la traduzione, ma stessi cuori e scelte.


## UX-05 — 1, 3 e ripresa/persistenza 4 PASS; 2 PENDING (2026-10-18)

Disponibile nel normale `./start.sh`; scena isolata `./crafting-demo.sh --fresh`.

1. **Preferite senza lavoro:** K, cerca bandage, scegli la ricetta senza utensile
   e Aggiungi ricetta preferita. K resta aperto, appare l’asterisco; Preferite
   mostra quella ricetta. Rimuovila: non deve più comparire in quella scheda.
   Segnare/selezionare/leggere non consuma materiali né avvia attività; il tempo
   resta in pausa. Il preferito della ricetta è distinto dai componenti protetti.
2. **Recenti reali:** scegli componenti/fonti e rispondi No: la ricetta non entra
   nei Recenti. Approva poi un lavoro: Recenti la mostra senza dover cercare.
   Riaprendo K la scheda iniziale segue dati nativi: prima incompleti accessibili,
   poi recenti/preferite, altrimenti Tutte. I recenti indicano avvii, non completamenti.
   Una ricetta recente con materiali mancanti mostra il limite e non diventa gratis.
3. **Incompleti — PASS personale T2:** avvia un lotto 2, apri K, interrompi e scegli il lavoro R
   nella scheda Incompleti. La ripresa conserva il progresso e chiede solo
   requisiti/ricambi nativi necessari; non riavvia un secondo lavoro né crea
   risultati duplicati. Prova in inglese: nessun controllo dipende dal testo italiano.
4. **Persistenza/ripresa — PASS personale T3 per lo scenario provato:** lascia la ricetta preferita e un avvio recente,
   esci e rilancia la demo senza --fresh. Schede, ricerca, lotti e marker devono
   restare leggibili e preferiti/recenti devono persistere. English e Italiano WIP
   devono conservare significato delle schede. Riavvio/ripresa non contano come
   nuovi completamenti; un elenco Più eseguite non è ancora presente.

Il riscontro T3 accetta salvataggio/ripresa del lavoro; non estende da solo la
copertura a tutte le lingue e ai metadati preferiti/recenti. Alla riapertura I
non viene ripristinato: l'actor è canonico, il menu e la pausa sono transitori.
T2 resta PASS con bug del falso crafting della categoria bandages: ricontrollo
separato in fondo, senza attribuire il PASS a quella voce.

Le vecchie validazioni restano accettate. Un playtest mirato del core è consigliato
al consolidamento delle interfacce, ma queste prove possono ancora essere rinviate.

## INT-01 — Gesti — 1–3 PASS personali T4/T5/T6 (2026-10-18)

1. **Porte e finestre:** RMB apre quelle chiuse e chiude quelle aperte, senza
   Shift; tieni il clic: un solo cambio. Prova anche accovacciato. Avvicinati
   molto all’anta/varco e apri: devi poter arretrare e passare. Una chiusura che
   investirebbe il corpo deve essere rifiutata chiedendo di allontanarti.
   La compenetrazione riferita durante apertura resta da ricontrollare nella
   struttura originale: la guardia automatica prova il caso di chiusura sul corpo.
2. **Shift-clic:** in `./storage-demo.sh --fresh`, Shift-clic sull’oggetto esterno
   raccoglie; su quello tuo deposita nel mobile, pagando il costo CDDA. Quantità
   selezionata rispettata, altrimenti pila intera. Nella vista dei contenitori
   posseduti scegli prima la destinazione a destra, poi Shift-clic a sinistra;
   senza destinazione appare un messaggio. Tasca piena/sigilli restano vincolanti.
3. **Rilascio fuori dalla finestra:** trascina un oggetto vero da I/trasferimenti,
   anche dalla hotbar o dal pannello esterno, oltre il bordo della finestra:
   viene depositato a terra ai tuoi piedi, con costo/quantità nativi. Contenuti
   esterni parziali lasciano il resto nella sorgente. Esc durante il drag annulla;
   rilasciare sullo sfondo dentro il menu non deposita. In pausa nessun deposito
   né raccolta deve partire dopo la ripresa. Worn/liquidi/proprietà/sigilli
   conservano i rifiuti nativi, senza togliere vestiti o rubare implicitamente.

**EXT4 — PASS ricevuto il 2026-10-18:** accettata l'assenza di raccolta
rinviata dopo F7. Non duplicare questo punto nei contatori. Il commento UX
sul menu 9×3 per oggetti sfusi è nel seguito; non revoca il PASS funzionale.

## Raccolta sfusa diretta — 1 e 3 PASS personali T5; 2 PENDING

1. **Un oggetto:** nella partita o `./storage-demo.sh --fresh`, deposita un
   oggetto da solo ai piedi del personaggio, chiudi I e punta il drop. RMB lo
   raccoglie senza aprire il menu 9×3. Anche un singolo sasso è raccolta diretta.
2. **Una pila:** deposita solo alcune munizioni (es. 7) su una casella vuota.
   RMB raccoglie tutta quella pila senza menu, rispettando spazio/costo CDDA.
   Niente duplicazioni o perdita del resto rimasto nell'inventario.
3. **Pausa e contenitori:** F7, prova RMB sul drop, riprendi senza cliccare:
   non parte una vecchia raccolta. Un nuovo clic funziona. Mobili, zaini a terra
   e più oggetti insieme mantengono il menu con quantità e contenuti nativi.

## Modelli e materiali umanoidi — PENDING (3), rinviabili

1. **NPC:** osserva l'NPC dello spawn da vicino, davanti e dietro. Pelle,
   volto, torso e arti devono appartenere a un omino voxel riconoscibile, senza
   la pelle ripetuta sui volumi dell'armatura. Aspetto generico: non rappresenta
   ancora esattamente vestiti, mutazioni o anatomia CDDA.
2. **Zombie:** osserva uno zombie comune. Volto e vestiti devono essere
   riconoscibili, senza texture spalmata sul guscio dell'armatura. La bassa
   risoluzione pixel art è quella degli asset Mineclonia; non è un pack HD.
3. **Terza persona:** premi C per vedere il personaggio dietro/davanti, poi
   torna alla prima persona. Deve esserci un modello voxel, non una sagoma 2D
   verde; piedi e altezza devono risultare plausibili. I conserva l'anteprima.

## Orientamento e animazioni di movimento — 2 PASS personale T7; 1 e 3 PENDING

1. **Movimento:** osserva zombie/NPC che camminano e cambiano direzione.
   Gli arti si animano e il modello segue la direzione degli spostamenti;
   quando si ferma passa alla posa idle. Non è una nuova AI. I cubi delle
   famiglie senza rig rimangono placeholder. Attacchi/reazioni richiedono
   eventi nativi dedicati e non fanno parte di questa animazione locomotoria.
2. **Tempo:** apri I/H o F7 mentre una creatura è in movimento: la posa deve
   congelarsi insieme al mondo. Chiudendo/riprendendo non recupera animazioni
   saltate. F8 scala anche le animazioni, senza cambiamenti alla velocità nativa.
3. **Giocatore e riapparizioni:** C, cammina/fermati, poi prova accovacciato,
   corsa e sdraio. La posa segue lo stato confermato e si ferma nei menu.
   Creature che diventano visibili o tornano dopo il caricamento non devono
   percorrere una vecchia traiettoria invisibile o lasciare doppi modelli.

## Feedback del core — dieci passi — PENDING (10), rinviabili

Nessun obbligo adesso. Avvio normale `./start.sh`; per una scena già pronta
puoi usare `./combat-demo.sh --fresh` o `./ranged-demo.sh --fresh`. Aspetto dei
vestiti e timbri audio sono ancora provvisori; bestiario completo non dichiarato.

1. **Attacchi:** osserva un attacco tuo in terza persona (C) e uno zombie che
   attacca davvero. Deve partire un gesto breve anche quando manca; non deve
   attaccare solo perché vicino. F7/I fermano la posa insieme alla simulazione.
2. **Danni:** un colpo effettivo produce una breve reazione/tinta sul bersaglio;
   se vieni ferito compare una tinta lieve sullo schermo, senza scuotere la
   camera né spostarti. Un colpo mancato non deve simulare un danno riuscito.
3. **Audio:** con volume attivo prova sparo, colpi e rumori di lavoro/movimento.
   Devono arrivare suoni e didascalie quando CDDA li rende udibili. Giudica anche
   il volume: il colpo d'arma usa ancora un timbro provvisorio. Niente ripetizione
   dei vecchi suoni dopo pausa/reconnect. La sordità nativa resta vincolante.
4. **Prima persona:** impugna/disimpugna un oggetto e una pistola. Deve vedersi
   l'oggetto effettivo, usando l'icona estrusa come proxy, indipendente dallo slot
   rapido selezionato. Destro mantenuto alza la posa, sparare dà un breve rinculo
   visivo dell'oggetto; non deve sembrare il pugno/mining di Minecraft. Non è una
   nuova regola di mira o un modello 3D definitivo di tutte le armi.
5. **Canidi:** quando incontri cane/lupo/coyote nella partita, controlla modello
   a quattro zampe, scala, pelle e ciclo di cammino; in pausa rimane fermo.
   Forme mutate/zombie non incluse conservano il fallback. Prova rinviabile fino
   a un incontro naturale, senza dover modificare il salvataggio per trovarli.
6. **Ragni:** quando incontri un ragno supportato controlla zampe, scala piccola
   o grande e cammino. Il proxy non deve comparire per una specie sconosciuta,
   né rivelare ragni che CDDA non percepisce. Anche questa prova può attendere.
7. **Uccelli terrestri:** gallina/gallo cedrone e pulcini supportati hanno un
   modello piccolo riconoscibile e si animano sul movimento confermato. Non si
   dichiara ancora volo o sagoma specifica di ogni uccello. Rinviabile all'incontro.
8. **Oscurità:** in una stanza buia compare un segnale «Low light» e una lieve
   velatura; uscendo alla luce si toglie. Nessuna creatura nascosta deve diventare
   visibile. È un'indicazione della luce nativa, non il futuro panorama/nebbia.
9. **Immersione:** quando CDDA conferma che sei sott'acqua compare una tinta blu
   e l'indicazione «Underwater». Emergere li rimuove. Non promette visibilità
   dove CDDA non esporta terreno; il messaggio deve rendere comprensibile anche
   una zona completamente buia. Niente ossigeno/danno inventato dal client.
10. **Diagnostica:** all'avvio niente grandi pannelli tecnici persistenti. Il
    tasto debug (default F3, riconfigurabile) li mostra/nasconde. Pausa, perdita
    connessione, minaccia, scelte native e lavoro devono restare comprensibili
    anche a diagnostica spenta. Le vecchie configurazioni possono avere F5.


## Ricontrolli dopo i sette gate — PENDING (4), rinviabili

I sette gate sono accettati; questi sono ricontrolli di modifiche successive,
non PASS dedotti dalle prove automatiche. Disponibili anche in `./start.sh`.

1. **Catalogo e ricerca dinamica:** `./crafting-demo.sh --fresh`, K, Tutte.
   L'avviso dei troppi risultati resta nel margine inferiore e non copre le
   schede. Scrivi lentamente `band`: risultati aggiornati senza Invio, campo
   sempre modificabile. Inserisci/cancella un carattere nel mezzo: cursore e
   ricerca non saltano alla fine. Lo stesso filtro dinamico è disponibile in I.
2. **Ricette vere e lotto:** cerca `bandage`: la categoria navigazionale senza
   risultato non è più avviabile. Seleziona `makeshift bandage` senza utensile,
   cambia lotto a 2 o 4: la selezione resta, requisiti/durata si aggiornano e
   puoi creare senza riselezionare. Con i materiali della demo un lotto 4 dà
   otto makeshift bandages, dopo il lavoro nativo; nessun esito fantasma a 0%.
   La vera `bandages` richiede materiali sanitari, nastro e disinfettante.
3. **Vano e chiusura esplicita:** punta una finestra chiusa e usa RMB. Senza
   abbassare la mira al davanzale, RMB deve richiedere la chiusura del vetro
   aperto. **O** richiede soltanto CLOSE, anche per tirare le tende di una
   finestra già chiusa; RMB le riapre dal lato consentito da CDDA. O è
   riconfigurabile con `keymap_cdda_close`; Shift non serve. Stato, lato interno,
   costo e rifiuto sul corpo restano nativi. Porte semplici conservano il toggle.
4. **Buio graduale:** attraversa più volte una soglia luce/ombra nel mondo.
   La tinta entra/esce progressivamente, senza un salto a ogni soglia; la
   velocità F8 non deve accelerare l'adattamento visivo. Il tetto può ancora
   causare poca luce secondo CDDA: questa modifica non cambia chi puoi vedere
   e non aggiunge ancora illuminazione 3D laterale. Valuta il comfort visivo.


## READ-01 — Libri cartacei e studio nativo — PENDING (4), rinviabili

Disponibile in `./start.sh` con libri realmente posseduti. Scena separata:
`./reading-demo.sh --fresh`. Nello zaino ci sono un breve libro di svago sui
gatti non identificato e una rivista sulle armi già identificata. La lampada
atomica assicura luce nella scena. Rilancia senza `--fresh` per riprendere il
save della demo. Questa prima fetta esclude e-reader, libri con usi speciali e
hint del guidebook; il menu ne indica il limite. Nessun gate personale oggi.

1. **Sfogliare e conoscere:** I, seleziona il libro non identificato. Leggere
   i dettagli deve mantenere tempo fermo e non rivelare gratis il contenuto.
   Premi **Skim book / Sfoglia libro**: il lavoro richiede tempo; solo al
   termine il libro diventa noto e il pulsante cambia in **Read / Leggi**.
   Nome, icona e istruzioni devono essere comprensibili; la scelta non deve
   far sparire il libro o produrne uno nuovo.
2. **Studiare davvero:** seleziona la rivista nota, Leggi. Nella scelta nativa
   puoi annullare, leggere una volta oppure fino al livello teorico successivo.
   Annulla una volta: nessun capitolo completato o esperienza gratuita. Poi
   scegli un capitolo e completalo: nei dettagli cresce la progressione teorica
   nativa. La durata dipende dal lettore: circa sette minuti CDDA,
   circa 100–105 secondi a 4x nella scena;
   questa consegna non introduce ancora un'accelerazione dedicata alle attività.
3. **Pausa e ripresa:** avvia lo studio, premi I e attendi: progresso e mondo
   restano fermi. Chiudi per riprendere, poi riapri e usa **Interrupt reading /
   Interrompi lettura**. Non si assegna un capitolo completo per un'interruzione.
   Leggendo di nuovo lo stesso libro con lo stesso modo, CDDA riprende il lavoro
   eleggibile già pagato, senza ricominciare da zero. F7 non deve accodare un
   vecchio clic di lettura da eseguire alla ripresa.
4. **Save/load del capitolo:** esci con studio in corso e I aperto. Rilancia la
   demo senza `--fresh`: il vero capitolo riparte dal progresso salvato, non
   duplica libri o esperienza. Come per il crafting, I e la sua pausa non sono
   persistiti; puoi premere I di nuovo per fermarti. Prova anche i testi in
   Italiano WIP dopo il riavvio con la lingua scelta; manca ancora la traduzione
   di alcune descrizioni native. Valuta leggibilità del pannello e del pulsante
   Leggi senza sovrapposizioni con Interrompi.


## LANG-01 — Dicitura della lingua selezionata — PASS (1), 2026-10-18

L’unico sviluppatore conferma «ok funziona perfettamente» dopo `a0bbf43`.
[Provenienza](../source/live-language-feedback-2026-10-18.md). Il testo del test
seguente documenta la versione accettata; il cambio a caldo successivo ha le
proprie prove LANG-02 e non eredita questo PASS.

1. Nel menu Esc, scegli English: compare **Prossimo avvio: English** se la
   sessione è italiana, oppure **Active: English** se è già inglese. La nota
   sulla traduzione italiana incompleta non compare con English selezionato.
   Scegli Italiano: il testo indica **Italiano (WIP)** e la sua incompletezza.
   Torna a English senza chiudere il menu: la dicitura si aggiorna e il tempo
   rimane fermo. Il testo segue sempre la lingua della sessione fino al riavvio.
   Questo è solo un controllo di chiarezza; la logica è già accettata dall'utente.


## LANG-02 — Cambio lingua senza riavvio — PENDING (2), rinviabile

1. In `./start.sh`, Esc → Italiano, poi English, ripetendo anche rapidamente.
   La partita e il menu restano aperti, il tempo fermo. Il menu Esc cambia
   subito lingua e indica quella attiva; WIP/incompletezza compaiono solo per
   Italiano. Chiudi Esc e controlla I/H/K: etichette e nomi nativi cambiano,
   oggetti/equipaggiamento e icone restano corretti. Una successiva domanda
   nativa usa la nuova lingua; annullare resta possibile senza eseguire l'azione.
   Descrizioni non tradotte possono restare inglesi con Italiano WIP.
2. Con un lavoro lungo in corso, apri Esc, cambia lingua e attendi: il lavoro
   resta fermo. Riprendi e verifica che continui dallo stesso punto senza
   duplicazioni o riavvii. Esci normalmente e rilancia: la lingua scelta è
   conservata. Le domande native già aperte conservano il testo originale fino
   alla risposta; non devono ripresentarsi o applicare effetti due volte.


## WIN-01 — Pacchetto Windows 11 x64 — PENDING (3), rinviabile

1. **Installazione e primo avvio:** copia `Minecataclysm-Windows11-Setup.exe`
   su un PC Windows 11 x64, preferibilmente senza strumenti di sviluppo. Doppio
   clic: installazione per il tuo utente, icona sul desktop e avvio automatico
   della partita 3D. Il primo mondo può richiedere qualche minuto. Nessun Bash,
   Python o WSL richiesto. Prova anche un account/percorso con spazi e lettere
   accentate. L'eseguibile non ha una firma del produttore.
2. **Partita e riapertura:** movimento continuo 4x, mouse, I/H/K, pausa F7/Esc,
   icone, grafica e suoni sul tuo hardware. Esc → Italiano/English cambia lingua
   senza riavviare e resta in pausa. Muoviti, modifica una porta o finestra,
   esci normalmente e aspetta la chiusura del salvataggio; doppio clic sull'icona
   del desktop. Posizione, oggetti, stato del mondo e lingua restano coerenti.
3. **Aggiornamento e disinstallazione:** chiudi il gioco, riesegui l'installer e
   riapri dall'icona: il salvataggio precedente è ancora disponibile. Disinstalla
   da Windows e verifica che `%LOCALAPPDATA%\Minecataclysm` conservi salvataggi
   e log. Reinstalla e controlla che la stessa partita si carichi. Non cancellare
   quella cartella per disinstallare il programma.


## DIS-01 — Smontaggio nativo — 3 PASS umano; 1, 2, 4 PENDING (2026-10-25)

`./disassembly-demo.sh --fresh` crea una copia isolata: fasce per piedi in
pelliccia sintetica, lampada e zaino. Stesse azioni nel normale `./start.sh`
con oggetti smontabili realmente posseduti. Non occorre fare queste prove ora.

1. **PENDING — Consulta e annulla.** I → seleziona le fasce → Smonta / Disassemble.
   Durante la consultazione il tempo resta fermo. Rifiuta la conferma nativa:
   oggetto ancora presente, nessun componente prodotto. F7 deve impedire
   l'avvio, senza eseguirlo dopo la ripresa.
2. **PENDING — Lavoro e pausa.** Conferma lo smontaggio: compare il progresso.
   Apri I durante il lavoro: progresso e mondo fermi. Chiudi I: riprende.
   Non è un'azione istantanea: il tempo e i requisiti sono quelli di CDDA.
3. **PASS umano 2026-10-25 — Interrompi e riprendi.** I → Interrompi smontaggio. Rimane un
   oggetto di smontaggio incompleto. Selezionalo → Riprendi smontaggio:
   conserva il progresso già fatto. A fine lavoro appaiono nelle vicinanze
   due pezze di pelliccia sintetica; il vecchio oggetto non deve duplicarsi.
4. **PENDING — Salva e ricarica.** In una nuova demo avvia lo smontaggio e
   chiudi il gioco durante il lavoro. Rilancia senza `--fresh`: riprende il
   lavoro nativo, con progresso conservato e un solo risultato. Il menu I
   non viene salvato come pausa, coerentemente con lettura e crafting.

Questa fetta non include pile di munizioni, liquidi o smontaggio ricorsivo.
Se CDDA posa l'incompleto su un banco o a terra, raccoglilo prima di riprenderlo
con I. Durata e recupero dipendono dalle condizioni native; la demo usa una
ricetta senza utensili aggiuntivi e senza rischio di recupero da difficoltà.

## Chiarimento NPC precedente — snapshot bab8fe2, prima di NPC-01

Questa nota descriveva la build precedente ed è superata dalla consegna NPC-01
qui sotto. In quel momento non c’era un nuovo test personale: **le conversazioni con gli NPC non sono
ancora collegate alla GUI**. Non esiste un tasto funzionante per iniziarle.
Il controllo nel runtime (`cwm_server.cpp`, movimento verso un NPC amichevole)
restituisce esplicitamente “NPC interaction UI is not implemented yet”.
Le precedenti prove PASS dei “dialoghi nativi” riguardano conferme e scelte di
oggetti/attività, non conversazioni, missioni o commercio. Questi ultimi
restano nella Fase 4.6 della roadmap e richiederanno una consegna distinta.


## NPC-01 — Conversazioni native con gli NPC — 4 PENDING

`./conversation-demo.sh --fresh`: un NPC si trova direttamente davanti al
personaggio, a pochi passi. La stessa interazione vale nel normale `./start.sh`.
Questi controlli si possono fare insieme al resto del backlog, senza urgenza.

1. **PENDING — Puntamento e ingresso.** Punta al corpo dell'NPC: compare l'hint
   per parlare. Premi il tasto destro: si apre la conversazione con il suo nome
   e le risposte native. Non devi urtarlo né camminargli addosso. Con un'arma
   in mano il destro sull'NPC non ostile continua a servire per parlargli.
2. **PENDING — Lettura e tempo fermo.** Lascia aperta la conversazione: il
   mondo rimane fermo. Leggi il testo corrente e lo storico; scorri le risposte
   e, quando presente, usa Next page / Previous page. Le opzioni non devono
   sparire e sfogliare non deve cambiare la battuta corrente o far passare tempo.
3. **PENDING — Risposta, dettagli e uscita.** Scegli una domanda innocua
   (per esempio “What are you doing?” nella demo), leggi la risposta e torna
   indietro. Prova una voce di osservazione/opinione e poi Esc / Leave
   conversation. Il gioco riprende senza scegliere una risposta nativa al tuo
   posto. Se provi il commercio, per ora deve apparire l'avviso di funzione
   rinviata: nessuno scambio, nessun blocco su terminale. Non è un trade completo.
4. **PENDING — Salvataggio e rientro.** Parla, esci, chiudi il gioco e riapri
   senza `--fresh`: stesso personaggio, NPC e mondo. Le conseguenze native
   effettivamente ottenute restano salvate. La finestra della conversazione non
   viene salvata come pausa; una nuova conversazione richiede un nuovo destro.
   Una semplice ispezione non deve regalare oggetti né completare missioni.

Le risposte con prove sociali e avvisi di ostilità sono native: possono fallire
per statistiche e condizioni del personaggio. Non occorre riuscire in una prova
per validare l'interfaccia. Scambi, diario missioni e servizi NPC complessi
restano fette successive; non si deduce che siano implementati da questi PASS.


## TRADE-01 — Scambio NPC nativo — 4 PENDING

`./trade-demo.sh --fresh` crea una sessione isolata: NPC direttamente davanti,
benda e lampada in vendita, due pile di munizioni da 20 e 30 e credito nativo
iniziale. Funziona anche nella partita normale da `./start.sh`, con NPC nativi
non ostili percepiti. Non usare i tuoi save ordinari per le prove distruttive.

1. **PENDING** — Destro sull'NPC, scegli la risposta per commerciare. Due
   pannelli con icone, nomi/tooltip, quantità e saldo; tempo fermo. Seleziona
   qualcosa, poi **Cancel trade** o **Esc**: nessun trasferimento o debito variato.
   Riapri e verifica che l'offerta non sia già selezionata.
2. **PENDING** — Richiedi la benda e offri 5 munizioni dalla pila da 30,
   trascinandola nell'altro pannello o usando quantità/**Update offer**.
   **Review and confirm**: prima rispondi **No**, l'offerta rimane modificabile;
   poi **Sì**. Benda ricevuta una volta, pila da 20 intatta, pila da 30 ridotta
   a 25 e saldo aggiornato. Shift-clic propone/rimuove l'intera pila; la
   selezione da sola non trasferisce nulla.
3. **PENDING** — Prova quantità oltre il disponibile e, quando il credito non
   basta, una richiesta troppo costosa: motivo visibile, nessuno scambio. Selezionare
   contenitore e suo contenuto insieme deve essere rifiutato. Esc da un'offerta
   e No dalla conferma non devono bloccare il gioco. F7 già attivo non deve
   accodare una conversazione/scambio da eseguire appena riprende il tempo.
4. **PENDING** — Dopo uno scambio esci e riapri `./trade-demo.sh` senza
   `--fresh`: oggetti, quantità e debito persistono, nessuna copia aggiuntiva.
   Riaprire e annullare altre offerte non ripete lo scambio precedente.

L'apertura usa il restock/riordino nativo del venditore: annullare evita lo
scambio, non annulla questi effetti nativi di apertura. La prima fetta non
certifica tutti i mercanti/mod/EOC o servizi speciali. I PASS NPC precedenti
restano distinti dalle nuove prove TRADE-01. Nessun gate manuale richiesto oggi.


## JOURNAL-01 — Diario delle missioni note — 4 PENDING

`./journal-demo.sh --fresh`: sessione isolata con due missioni attive, una
completata, una fallita e una proposta NPC non ancora accettata. Il diario si
apre con **J** anche nella normale partita di `./start.sh`. La demo ha un NPC
davanti e nessun orologio: le scadenze attive hanno precisione approssimata.

1. **PENDING** — Premi J. Leggi Attive/Completate/Fallite, descrizioni e
   obiettivi; il tempo e il personaggio restano fermi. La missione proposta
   dall'NPC e non accettata non deve comparire. In una partita senza missioni
   note il diario deve mostrare uno stato vuoto comprensibile.
2. **PENDING** — Nella scheda Active seleziona Find Flag e premi **Track this
   mission**; poi prova l'altra missione attiva. Il contrassegno segue la
   selezione esplicita. Consultare un'altra voce non deve cambiare la missione
   seguita, assegnare premi o completarla. La destinazione di Find Flag mostra
   coordinate native, incluso Z; la missione senza destinazione non ne inventa
   una. Le coordinate sono celle della mappa globale CDDA, non blocchi Luanti.
3. **PENDING** — Le schede Completed/Failed sono consultabili senza pulsanti
   per completare, riattivare o seguire quelle missioni. Controlla la scadenza
   approssimata in assenza di orologio. Esc chiude il diario; se prima avevi
   attivato F7, dopo la chiusura il gioco deve rimanere in pausa fino a F7.
4. **PENDING** — Segui Find Flag, chiudi e riavvia `./journal-demo.sh` senza
   `--fresh`: missioni, stati e selezione persistono. Il diario non si riapre
   automaticamente e la pausa del suo menu non è salvata. Facoltativamente
   accetta una nuova missione parlando all'NPC e riapri J: deve comparire solo
   dopo l'accettazione nativa.

La lettura non valuta condizioni di completamento e non esegue gli script:
non promette percentuali o ricompense simulate. Dettagli dinamici non sicuri
mostrano un avviso esplicito. Indicazioni HUD/mappa 3D e compatibilità con ogni
missione mod/EOC rimangono attività separate; nessun gate manuale richiesto ora.


## COMP-01 — Ordini e regole individuali dei compagni — 4 PENDING

`./companions-demo.sh --fresh` apre una sessione isolata con un alleato davanti.
Nella partita normale usa un compagno effettivamente alleato, non uno sconosciuto.
Il pannello è la prima voce **Companion orders and rules** nel dialogo amico.
Non è un nuovo comando per reclutare né un controllo a distanza degli NPC.

1. **PENDING — Accesso e consultazione.** Destro sull'alleato, apri il pannello,
   visita Combat rules / Behavior rules, eventuali Next page / Previous page,
   politiche di combattimento, mira e bionica. Sono visibili solo impostazioni
   dell'alleato scelto. Il mondo resta fermo mentre leggi; Esc esce dal dialogo.
   Su uno sconosciuto non deve comparire il pannello per comandarlo.
2. **PENDING — Guardia e seguito.** Guard this position, esci e allontanati
   qualche passo: il compagno mantiene il comportamento di guardia CDDA.
   Parlaci di nuovo, Follow me, esci e cammina: l'AI nativa riprende a seguirti.
   Back to conversation torna al dialogo amico/guardia appropriato. Non deve
   reclutare NPC, teletrasportarli o cambiare assegnazioni di accampamenti.
3. **PENDING — Regola e ordine temporaneo.** Nella demo Use firearms parte
   con Base On ma Override Off. Modificare la base non cancella l'override:
   Effective resta Off fino a Use base rule (remove override). Prova una regola
   di comportamento e una politica di mira. Modifiche esplicite sul solo alleato;
   consultare non deve concedere energia, abilità, cure o oggetti.
4. **PENDING — Persistenza.** Modifica una regola e un override, esci e chiudi;
   riapri `./companions-demo.sh` senza --fresh. Stesso alleato, ordini e regole
   conservati. Il pannello non si riapre e la sua pausa non è salvata. Le azioni
   già accettate rimangono native, non vengono ripetute alla riapertura.

Addestramento, filtri testuali di raccolta, copia delle regole da altri NPC,
radio/comandi di gruppo e servizi/accampamenti complessi restano fette separate.
Non è richiesto nessun gate manuale adesso; i precedenti PASS restano storici.


## REST-01 — Riposo, sonno e attesa nativi — 2, 3 PASS umani; 1, 4 PENDING (2026-10-25)

**B** nella partita normale apre il menu di riposo; il tasto è configurabile.
`./rest-demo.sh --fresh` prepara una sessione isolata con personaggio stanco,
letto, stamina bassa, senza orologio o ostili vicini. Non modifica i tuoi mondi.

1. **PENDING — Attesa e pausa.** B → Wait or catch your breath; prova l'attesa
   breve e quella per riprendere fiato. Il tempo scorre, I/Esc lo ferma mentre
   leggi. B → Interrupt rest interrompe l'attesa. Annullare il primo menu non
   deve avviare attività; tenere premuto movimento durante l'attesa non deve
   accodare passi da eseguire dopo.
2. **PASS umano 2026-10-25 — Tentativo e sonno effettivo.** B → Try to sleep: No lascia svegli;
   Yes usa il tentativo nativo. Puoi interrompere il tentativo, non forzare
   gratuitamente il risveglio durante il sonno effettivo. Nella demo sul letto
   il personaggio è abbastanza stanco da addormentarsi. Controlla il messaggio
   Sleeping anche quando non vedi il mondo. Nessuna percentuale inventata
   del sonno; se possiedi una sveglia, conserva le scelte di allarme native.
3. **PASS umano 2026-10-25 — Velocità e risveglio.** Le attese brevi restano a velocità normale.
   Sonno/attese lunghe possono accelerare dopo qualche secondo simulato; B →
   Continue at normal speed rallenta, Fast-forward long rest riaccelera.
   I/Esc continua a fermare il mondo. Controlla che il ritorno al gioco dopo
   un risveglio nativo non provochi una raffica di passi/tempo arretrato.
   Rumori, danni e sveglie restano nativi; niente cure o stamina istantanee.
4. **PENDING — Persistenza.** Esci durante sonno/attesa; riapri la stessa demo
   senza --fresh. La vera attività o l'effetto sonno prosegue dal salvataggio,
   senza un nuovo comando di avvio. Il menu e la sua pausa non vengono salvati;
   consulta B/I anche dopo il caricamento. Posizione e bisogni restano nativi.

Queste sono nuove prove personali rinviabili, non un gate richiesto adesso.
Il riposo non completa i servizi avanzati NPC o l'accelerazione di ogni attività.


## LIQ-01 — Fonti d’acqua e travasi nativi — 1, 2, 4 PASS umani; 3 PENDING (2026-10-25)

`./liquids-demo.sh --fresh`: sessione isolata con tanica impugnata, zaino,
bottiglie piccole vuote, una pozza adiacente e un cubo di legno vicino che
rappresenta un gabinetto con scorta finita preparata per la prova. Guarda la
fonte da vicino: l’hint dice Liquid source; destro apre le scelte native.
Nella partita normale qualità e scorte sono quelle reali del mondo CDDA.

1. **PASS umano 2026-10-25 — Fonte e interruzione.** Destro sulla pozza → Pour into a container
   → tanica. I deve fermare il riempimento; Interrupt transfer deve interromperlo
   conservando l’acqua già prelevata. Annullare il menu della fonte non riempie
   oggetti. Nessuna percentuale finta per questa attività nativa.
2. **PASS umano 2026-10-25 — Travaso e capacità.** In I seleziona la tanica o il suo liquido e
   premi Pour liquid... → Pour into a container → bottiglia piccola. La bottiglia
   si riempie entro la capacità nativa e il resto rimane nella tanica. Un travaso
   già applicato può mostrare tempo da pagare senza essere annullabile. Oggetti
   pieni, liquidi incompatibili, sigilli e liquidi congelati non vanno aggirati.
3. **PENDING — Scorta finita e consumo.** Destro sul cubo vicino: il menu nativo
   identifica la fonte. Riempi un’altra bottiglia e/o scegli Consume it: la scorta
   deve diminuire, senza diventare infinita. Il liquido mantiene il tipo nativo.
   Bere segue la fisiologia CDDA: la sete può migliorare dopo l’assorbimento,
   non necessariamente all’istante. L’acqua della partita normale può essere
   pericolosa; questa interfaccia non la purifica.
4. **PASS umano 2026-10-25 — Persistenza.** Avvia un riempimento lungo, apri I per fermarlo e
   chiudi il gioco. Riapri la stessa demo senza --fresh: riprende il riempimento
   nativo, non un nuovo comando. Quantità già versate, resto e scorta finita
   persistono. Il menu/pausa non viene salvato. Interrompi o lascia finire e
   verifica ancora l’inventario.

Il riscontro del 2026-10-25 accetta riempimento/pausa/interruzione, travaso con
capacità e resto conservati e la persistenza nel caso proposto. Congelamento,
miscele incompatibili e annullamento del primo menu non sono automaticamente
provati personalmente da quei PASS. LIQ-01.3 resta pendente. Crafting dei liquidi,
purificazione e serbatoi veicoli restano fette distinte; l'apertura sigilli ha
la propria sezione seguente.


## SEAL-01 — Apertura tasche sigillate — 1, 3 PASS umani; 2, 4 PENDING (2026-10-25)

`./seals-demo.sh --fresh`: scena isolata con bottiglia sigillata in mano,
zaino, bottiglia per condimenti sigillata e lattina sigillata. La funzione è
anche nella partita normale con `./start.sh`; non richiede un mondo nuovo.

1. **PASS umano 2026-10-25 — Apertura e annullamento.** I → bottiglia in mano → Open sealed
   pocket... → Cancel: rimane sigillata. Ripeti confermando Open: sigillo rotto,
   stessa acqua e quantità, Pour liquid... disponibile dopo aggiornamento.
   Nessun tempo di apertura inventato; bere/travasare conserva i costi nativi.
2. **PENDING — Accesso.** Non puoi consumare o trasferire direttamente il liquido
   attraverso un sigillo. Apri il contenitore prima; dopo l’apertura torna
   accessibile tramite le interfacce native. In contenitori annidati sigillati
   apri prima quello esterno. Leggere l’inventario non deve aprire nulla.
3. **PASS umano 2026-10-25 — Lattina nello zaino.** Aprila esplicitamente: perde la chiusura
   stagna; la gestione nativa propone cosa fare col liquido. Annullando quel
   travaso successivo può posare la lattina aperta a terra per non versarla.
   Il primo Cancel non rompe il sigillo; il Cancel dopo apertura non lo ricrea.
4. **PENDING — Persistenza.** Apri la bottiglia in mano, lascia sigillata quella
   per condimenti. Esci e riapri la demo senza --fresh: entrambi gli stati e
   i contenuti restano corretti. Nessun comando ripetuto al caricamento.

Nessun gate personale richiesto ora. Aperture mediante utensili/trasformazioni,
usi speciali degli oggetti e crafting/purificazione liquidi restano separati.


## UX-CURSOR-01 — PASS umano 2026-10-26 tramite FB-01.1

Segnalazione umana del 2026-10-25, [testo originale e contesto](../source/manual-liquids-seals-feedback-2026-10-25.md).
Dopo aver premuto un'azione il cursore viene dislocato, con frequenza ancora
incerta. Da riprodurre nei passaggi inventario/scelte native/ritorno al menu;
rendere coerente la posizione tra menu correlati senza interferire col controllo
della visuale. L'intervento CWM2.35 conserva la posizione normalizzata tra menu;
la verifica automatica passa e il ricontrollo personale è FB-01.1. La descrizione
sopra conserva il riscontro originario. Il conteggio di 61 include i nuovi FB-01;
i PASS funzionali precedenti restano validi.


## FB-01 — 4 PASS umani (3, 4 il 2026-10-25; 1, 2 il 2026-10-26)

Quattro nuovi casi riferiti alle correzioni successive, non ripetizioni dei
quattro PASS precedenti. Proporli dopo la consegna verificata degli interventi.

1. **PASS umano 2026-10-26 — Cursore e conferme (precedente FAIL di avvio chiuso).** `./liquid-recovery-demo.sh --fresh`:
   I → bottiglia impugnata → Open sealed pocket..., prima Cancel, poi conferma
   e ritorna al menu. Tieni la lattina per la prova 2. Il cursore deve mantenere una
   posizione coerente nei passaggi, senza saltare al centro dopo ogni azione.
   Prova anche una conferma Yes/No dal riposo B: etichette senza punto fermo
   finale; domande, puntini di sospensione e testo narrativo restano sensati.
2. **PASS umano 2026-10-26 — Recupero della lattina (precedente FAIL di avvio chiuso).** Nella stessa demo apri la lattina nello
   zaino e annulla il travaso, lasciandola a terra. Destro sul drop apre la vista
   esterna; seleziona lattina → Pour liquid... → Pour into a container → glass
   bottle vuota preparata nella demo. Dopo il travaso, raccogli la lattina vuota
   trascinandola verso il pannello del tuo inventario. Acqua nella bottiglia,
   lattina recuperabile, nessuna perdita/duplicazione. Una lattina piena aperta
   rimane soggetta alle regole native: il gesto non la rende stagna.
3. **PASS funzionale 2026-10-25 — Ritmo del riposo esplicito (design CWM2.35 poi superato).** `./rest-demo.sh --fresh`, B → Try to
   sleep → Yes. Leggi fase, NORMAL/FAST REST e velocità F8 × moltiplicatore =
   obiettivo. B permette normale e x64/x256/x1024; prova x1024 e normale,
   chiudi il menu B con Keep resting, cambia F8 e verifica che la formula si aggiorni. I/Esc ferma comunque il
   tempo. Il throughput effettivo dipende dalla simulazione; valuta se la
   durata reale è ora accettabile. Dopo il riposo niente accelerazione residua.
4. **PASS umano 2026-10-25 — Cielo notturno.** `./night-demo.sh --fresh`: guarda verso l'alto
   attraverso l'apertura sopra il personaggio. Cielo notturno coerente col
   terreno scuro, senza fondo azzurro diurno. F7/Esc e attendi alcuni secondi:
   il cielo non deve ritornare diurno. Confronta col giorno in una demo diurna
   o nella partita normale; la pausa non deve far avanzare sole/luna.


## UF8-01 — Unica velocità F8 contestuale — 1 PENDING

La precedente prova FB-01.3 resta PASS della vecchia funzione, accompagnata
alla richiesta di semplificarla. Questo è il ricontrollo della nuova funzione.

1. **PENDING — Un solo F8, pause e ritorno al gioco.** `./rest-demo.sh --fresh`:
   prima di dormire scegli con F8 una velocità ordinaria riconoscibile, per
   esempio 2x. B → Try to sleep → Yes. Appena compare il sonno, F8 cicla sulla
   scala ampliata 1/4/64/256/1024/4096x; seleziona 1x per leggere con calma,
   poi un valore alto. L'HUD mostra un solo numero e un colore/etichetta
   distinti, senza prodotti tra due moltiplicatori. B non offre velocità.
   I/Esc ferma il tempo. Al risveglio o all'interruzione di un'attesa lunga
   torna la precedente velocità da svegli (2x nell'esempio), senza raffiche
   arretrate. Salva/riapri durante il sonno: continua l'attività nativa, non
   parte un nuovo tentativo; la velocità selezionata è una preferenza transitoria.


## MENU-01 — Continuità delle schermate e lavoro nativo — 1 PENDING

1. **PENDING — Nessun ritorno momentaneo al gioco tra menu correlati.**
   `./liquid-recovery-demo.sh --fresh`: I → lattina → Open sealed pocket →
   conferma → Cancel del travaso; l'interfaccia passa direttamente tra scelte
   native, attesa e inventario, senza un fotogramma del solo gioco. Ripeti
   un'azione indossa/togli e l'interruzione di un'attività da I/K: il lavoro
   conserva i costi CDDA mentre la finestra rimane visibile. Pause and inspect
   (anche I) ferma il tempo senza annullare il lavoro; Return to game/Esc esce
   volontariamente. F7 ferma/riprende l’azione nella finestra e F8 cambia
   l’unica velocità senza far avanzare il tempo quando è in pausa. Nessun
   comando duplicato e cursore coerente. I PASS FB-01
   rimangono validi; questo è un ricontrollo della nuova presentazione.
