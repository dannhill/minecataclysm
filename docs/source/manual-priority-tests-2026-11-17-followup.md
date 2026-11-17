# Secondo riscontro e istruzioni operative — 2026-11-17

Documento scritto da un LLM dai risultati e dalle direttive dell'unico
sviluppatore umano. Fonte diretta: «1 PASS 2 PASS 3 non ho francamente capito
qual è il test [...] 4 PASS». I PASS sono playtest umani, non deduzioni da test
automatici. Il developer chiede spiegazioni più chiare anche in futuro.

## Risultati

- NPC-01.1 PASS: ingresso dal corpo dell'NPC, anche con oggetto impugnato.
- TRADE-01.1 PASS: consultazione/annullamento e offerta non ripresentata.
- COMP-01.1 non eseguito per istruzioni poco chiare: resta PENDING, non FAIL.
- NPC-01.4 PASS: salvataggio/rientro della conversazione senza replay.

**29 PENDING =32 meno tre**, nessun nuovo caso o FAIL. Restano4 casi espliciti
(COMP1, JOURNAL1, residuo TRADE3 e READ-FB1) e25 storici. REST-FB-02 OPEN,
MENU-TOGGLE-01 TODO/proposta e i gate architetturali restano separati.

Le nuove istruzioni distinguono apertura di una categoria, consultazione di
un valore e comando che lo modifica. Evitano formule come «nessuna energia
gratis» senza una misura osservabile. La preferenza del developer è registrata
anche in AGENTS.md per conservarla oltre la conversazione.

## Nuovo gruppo: primo punto rispiegato e tre prove ancora pendenti

Ordine: permessi/consultazione dei compagni, ricerca condivisa, recenza legata
all'avvio nativo, infine modello del giocatore. Nessuno è già PASS. I punti2/3
si svolgono nella stessa demo di crafting per ridurre ripartenze e lavoro.
I casi di credito insufficiente e distrazione da freddo richiedono ancora una
scena personale controllata prima di essere riproposti. Per JOURNAL-01.1 manca
una scena sicuramente vuota: la fixture conversazione ha liste vuote nel
baseline ma il più recente salvataggio reale contiene una missione. Non dire
al developer che quella scena deve mostrare zero senza verificarne il caricamento.

### 1 — COMP-01.1: leggere una regola senza cambiarla

**Scopo:** verificare che un clic per aprire i dettagli non sia trattato come
un comando per cambiare il comportamento del compagno.

**Avvio:** `./companions-demo.sh --fresh`.

1. Punta all'omino davanti e fai clic destro. Scegli **Companion orders and rules**.
2. Scegli **Combat rules**, poi **Use firearms**. Questo apre i dettagli; non
   premere Enable, Disable o Temporarily. Annota i tre valori. Nella scena nuova
   sono **Base rule On / Temporary override Off / Effective rule Off**: non è
   un errore, il valore temporaneo prevale sulla regola base.
3. Premi **Back**, riapri **Use firearms**: devono esserci gli stessi tre valori.
4. Torna al menu principale con Back. Apri **Behavior rules** e una voce per
   leggerne i dettagli, poi torna indietro senza premere comandi di modifica.
   Apri **Aiming policy**: l'asterisco indica la scelta attuale; non cliccare
   un'altra scelta. Apri **Bionic power policy**, poi i due sottopannelli:
   guarda l'opzione marcata e torna indietro senza selezionarne una nuova.
5. Usa **Leave conversation** o Esc. Riapri il dialogo e i dettagli di Use
   firearms: i valori devono essere rimasti quelli iniziali, senza finestre bloccate.
6. Chiudi la demo. Avvia `./conversation-demo.sh --fresh` e parla all'omino:
   questo NPC è uno sconosciuto, non il compagno. La voce **Companion orders
   and rules** non deve esserci. Non serve reclutarlo o fargli cambiare stato.

**PASS:** puoi entrare/uscire dai pannelli, la sola lettura non cambia le
impostazioni, i comandi ai compagni non sono offerti allo sconosciuto.
**Non serve:** far combattere l'NPC, verificare la sua mira o ripetere guardia/
seguito, modifica regole e loro persistenza già validati.

### 2 — Ricontrolli dopo i sette gate, punto1: ricerca mentre scrivi

**Scopo:** verificare che cercare una ricetta non richieda Invio e non sposti
il cursore, un comportamento usato anche da altre interfacce.

**Avvio:** `./crafting-demo.sh --fresh`, premi K e scegli **All / Tutte**.

1. Senza filtro, guarda l'avviso **Too many results: narrow the search** quando
   presente: deve restare separato dai pulsanti All/Favourites/Recent/Unfinished.
2. Clicca nella ricerca e scrivi lentamente **band**, una lettera alla volta,
   senza Invio. I risultati devono aggiornarsi da soli.
3. Porta il cursore subito dopo la **a** di band e scrivi **x**: deve risultare
   **baxnd**. Premi Backspace: torna **band**, senza perdere il focus o portare
   il cursore in fondo. Se il filtro non trova ricette è un esito normale.
4. Chiudi K con Esc, poi premi I e prova lo stesso inserimento/cancellazione a metà di una ricerca.
   Non occorre raccogliere, depositare o creare oggetti per questa prova.

**PASS:** risultati aggiornati senza Invio, cursore/focus stabili, avviso che
non copre le schede. Se questo fallisce, riferisci il punto preciso prima del
punto3: un difetto della ricerca può rendere meno affidabile anche quel flusso.

### 3 — UX-05.2: Recenti registra un avvio, non una selezione annullata

**Scopo:** verificare che la lista Recenti corrisponda ai lavori avviati.

**Avvio:** continua la stessa demo del punto2. Se non l'hai ancora avviata,
usa `./crafting-demo.sh --fresh`. Non usare --fresh fra le due metà di questo test.

1. In K cerca **makeshift bandage**. Se ci sono più varianti, scegli quella
   senza utensile. Imposta **Batch 1** e premi il comando di creazione.
2. Dopo l'eventuale scelta del materiale, alla domanda **Consume these components
   and start crafting?** scegli **No**. Riapri K e clicca **Recent**: quella
   ricetta non deve essere comparsa. Una scena fresca parte con Recenti vuoto.
3. Cerca di nuovo la stessa ricetta, avviala e stavolta rispondi **Yes** alla
   stessa domanda. Lascia finire il lavoro; non occorre ottenere otto bende:
   qui Batch1 produce due bende con la ricetta senza utensile.
4. Riapri K. Senza incompleti pendenti deve proporti i Recenti; se stai
   cambiando filtro manualmente clicca **Recent**. La ricetta deve esserci e
   devi poterla selezionare senza riscrivere il nome.
5. Seleziona quella ricetta e imposta **Batch 20**: la scena non ha venti pezzi
   di tessuto. Deve indicare il requisito mancante o impedire l'avvio. Il fatto
   che sia nei Recenti non deve renderla creabile senza materiali. Riporta Batch1.

**PASS:** No non aggiunge la ricetta, Yes con avvio la aggiunge; la voce recente
conserva i requisiti. La lista registra avvii, non un contatore di completamenti.

### 4 — Modelli e materiali umanoidi, punto3: corpo 3D del giocatore

**Scopo:** verificare che le due visuali esterne e l'anteprima mostrino un
personaggio 3D utilizzabile, dopo la sostituzione della vecchia sagoma verde.

**Avvio:** `./equipment-demo.sh --fresh`.

1. Premi C una volta: devi vedere il personaggio da dietro. Cammina qualche
   passo e gira la visuale per guardare torso, braccia, gambe e piedi.
2. Premi C una seconda volta: devi vedere il personaggio da davanti.
3. Premi C una terza volta: torni alla prima persona, senza un corpo piatto
   o una sagoma verde rimasta davanti alla camera.
4. Apri I e guarda l'anteprima del personaggio: anche lì deve esserci il modello
   voxel. Non si richiede che riproduca già ogni indumento CDDA.

**PASS:** corpo con volume in entrambe le visuali esterne e nell'anteprima;
piedi sul pavimento, corpo non sospeso o sepolto nel terreno; ritorno alla
prima persona corretto. Questo non valida ancora animazioni di attacco/posa.

## Verifiche di preparazione e limiti

Etichette e percorsi dei compagni verificati in cwm_companions.h, inclusa la
priorità Base On / Override Off della scena. La conferma e l'aggiornamento
Recenti sono in craft_command.cpp: la conferma precede il salvataggio della
recenza. La ricetta bandages_makeshift senza utensile richiede un tessuto e
produce due bende; la fixture ha meno di20 tessuti e Recenti inizialmente
vuoto. Script e fixture esistono. Nessuna partita viene avviata/modificata
per registrare questo riscontro; nessuna modifica a produzione o binari.

## Terzo riscontro e quattro prove successive

Il developer ha assegnato PASS ai quattro punti del giro precedente.
Il punto 1 chiude COMP-01.1. Ha aperto i pannelli aggiuntivi e ha chiesto quale
testo leggere. Bastava verificare che le schermate si aprissero e che tornare
indietro lasciasse le scelte come prima. Nei pannelli con un asterisco,
quello indica l'opzione attiva. Il punto 2 chiude il ricontrollo della ricerca
e del cursore. L'aggiornamento in tempo reale gli era già familiare. L'operazione
distintiva era inserire e cancellare a metà parola. Il punto 3 chiude UX-05.2
e il punto 4 chiude il modello 3D del giocatore e la sua anteprima.

**25 prove pendenti dopo i quattro PASS umani.** Per il prossimo giro i
primi due punti riguardano il recupero da un blocco e un comando di esplorazione.
Gli altri due controllano come il mondo comunica immersione e oggetto impugnato.
Tutte e quattro le prove erano già nel registro.

1. **Rispondere all'avviso di freddo durante la lettura (READ-FB-01.1)**

   Avvia `./artifacts/manual-checks-20261117/launch.sh cold`. Premi I appena
   entri, scegli la rivista **Recoil**, poi **Read → Read once**. Alla domanda
   **You are freezing. Stop reading?** scegli **No**. Se ritorna la stessa
   domanda, scegli **Ignore this distraction and continue**. Se compare un
   nuovo avviso di ferita puoi usare lo stesso comando anche lì. Quando il
   pannello della lettura ricompare, verifica che la barra avanzi. Premi I,
   poi premi ancora I per tornare al progresso. Il punto passa se dopo le
   risposte il pannello avanza e I continua a funzionare. Se la domanda di
   freddo non compare, segna «avviso assente».

2. **Chiudere il vetro e tirare le tende (ricontrollo 3)**

   Avvia `./artifacts/manual-checks-20261117/launch.sh window`. Rimani dove
   parti. Guarda circa 90° a destra verso la finestra vicina e punta il vetro.
   Destro apre il vetro. Aspetta il cambio, tieni il mirino alla stessa altezza
   e fai di nuovo destro sul vano vuoto. Il vetro deve richiudersi anche con
   il mirino sopra il davanzale. Riapri col destro, poi premi **O** e aspetta
   che il vetro si richiuda. Premi **O** ancora. Le tende devono coprire la
   finestra. Un destro dall'interno deve scostarle. Lascia finire ogni azione
   prima di premere di nuovo.

3. **Segnale a schermo durante l'immersione (feedback 9)**

   Avvia `./vertical-demo.sh --fresh`. Dalla partenza, con la visuale rivolta
   verso la scala che sale, premi **D** due volte separate. La prima casella
   è la scala a pioli e la seconda è l'acqua. Accetta l'eventuale domanda
   nativa d'ingresso. In acqua premi **Maiusc sinistro + Spazio** una volta
   per immergerti, poi **Spazio** per riemergere. Il punto passa se in
   immersione compaiono una tinta blu e **Underwater / Sott'acqua** in alto,
   e se entrambi spariscono quando torni in superficie. Se l'avviso d'ingresso
   copre la scritta in alto, aspetta che il messaggio di ingresso svanisca. Premi A per tornare
   alla casella della scala a pioli.

4. **Oggetto impugnato in prima persona (feedback 4)**

   Avvia `./equipment-demo.sh --fresh`. La mazza è già in mano e deve
   comparire in basso a destra. Cambia slot con la rotella. Finché la mazza
   resta nella casella **In hand / In mano** di I deve restare anche nella
   visuale. Seleziona la mazza in I, scegli **Stow / Riponi**, conferma la
   destinazione e aspetta che l'azione finisca. La mazza deve sparire dalla
   visuale. Avvia poi `./ranged-demo.sh --fresh`. La Glock è già impugnata.
   Se all'inizio c'è l'avviso di minaccia, premi E. Punta lo zombie davanti
   e tieni premuto il destro. Guarda se la pistola si alza. Rilascia e fai un
   clic sinistro. Al colpo l'oggetto deve dare un breve scatto. La forma
   semplificata dell'oggetto è quella prevista da questa versione.

Il launcher locale delle prime due prove copia ogni volta la fixture in una
nuova cartella sotto `artifacts/manual-checks-20261117/`. La copia fredda usa
la stessa temperatura del test automatico della lettura. La copia finestra
sostituisce nel salvataggio di prova il vetro senza tende con quello domestico
alla stessa posizione. Entrambe usano il runtime normale tramite `start.sh`.

## Quarto riscontro e prossimo giro

L'unico sviluppatore ha assegnato PASS a READ-FB-01.1, chiusura vetro/tende
(ricontrollo 3), immersione (feedback 9) e oggetto impugnato (feedback 4).
**21 punti pendenti dopo questi quattro PASS umani.** In lettura ha visto
anche un avviso di ferita. La scena fredda può produrre una seconda domanda
nativa distinta da quella sul congelamento. In combattimento ha confermato
il lampo rosso sullo zombie colpito. Il punto 2 del feedback danni resta aperto
per il lato giocatore. Lo scatto della Glock si vede poco e ha l'aspetto di
una spada. Il client ripiega sulla texture della spada per le categorie
`weapons` e `guns` quando manca un'immagine associata all'oggetto. La resa
dello scatto è calcolata separatamente nella camera. Tenere il riscontro
per il seguito su grafica e rinculo visivo.

Il gesto **destro mantenuto per mirare, sinistro per sparare** è il controllo
3D scelto per l'integrazione. Nel CDDA originale, **F** apre la modalità di
puntamento. Lì si può mirare con **.** e sparare con **F/Invio**, o usare
le scorciatoie di mira e sparo. L'arco di Mineclonia parte al rilascio del
destro. Qui si può cliccare sinistro tenendo ancora destro. Se si rilascia
prima, si interrompe il miglioramento della mira e si può ancora sparare
con la mira già acquisita se il bersaglio e lo stato restano validi. Calcolo
di mira, costi e colpo rimangono di CDDA.
[Binding CDDA](../../cdda/data/raw/keybindings.json) ·
[Gestione dei tasti nell'integrazione](../design/held-mouse-aim.md) ·
[Arco Mineclonia](../../mineclonia/mods/ITEMS/mcl_bows/bow.lua)

1. **Verificare il rifiuto di un'offerta fuori credito (TRADE-01.3)**

   Avvia `./artifacts/manual-checks-20261117/launch.sh credit`. Parla con
   l'NPC davanti col destro e scegli l'opzione di scambio. Verifica **Credit
   limit $0.00**. Nel riquadro del mercante fai **Maiusc + clic sinistro**
   sulla benda per richiederla. Lascia vuota la tua offerta. Il saldo deve
   diventare negativo, comparire l'avviso di credito e sparire **Review
   and confirm**. Poi, nel riquadro **Your inventory** a destra, fai
   **Maiusc + clic sinistro** sul tuo zaino e dopo sulla pila da **30 colpi**.
   La pila è nello zaino. Il menu deve tenere selezionato lo zaino, lasciare
   la pila a **0/30** e dire che puoi offrire il contenitore o il contenuto.
   Premi
   **Cancel trade** e riapri lo scambio. La benda è ancora del mercante,
   l'offerta è vuota e il saldo è tornato a zero. La prova della quantità
   fuori limite conserva il precedente riscontro già registrato.

2. **Distinguere le missioni note dalle proposte (JOURNAL-01.1)**

   Avvia `./journal-demo.sh --fresh` e premi **J**. Aspettati **Active (2)**,
   **Completed (1)** e **Failed (1)**. Clicca **Find Flag** e controlla che a
   destra si vedano descrizione e obiettivo. **Find Inhaler** è ancora una
   proposta e deve restare fuori da tutte le schede. Chiudi la demo e
   avvia `./artifacts/manual-checks-20261117/launch.sh journal-empty`.
   Premi **J**. Tutte e tre le schede devono segnare **0** e ciascuna deve
   mostrare **No known missions in this category**. Esc chiude entrambi i
   diari, rimettendo a disposizione i controlli.

3. **Controllare il modello dello zombie (modelli umanoidi, punto 2)**

   Avvia `./ranged-demo.sh --fresh`. Guarda lo zombie già davanti. Se c'è
   l'avviso di minaccia, premi E, poi spostati un poco a lato per vederlo di
   sbieco. Da davanti devono distinguersi volto e vestiti. Di lato le texture
   devono restare sui pezzi giusti del corpo, specialmente testa e torso.
   La pixel art può rimanere a bassa risoluzione. Puoi tenere aperta la demo
   per il punto successivo.

4. **Sentire spari, colpi e passi (feedback 3)**

   Attiva l'audio nelle impostazioni e usa la stessa `./ranged-demo.sh`.
   Punta lo zombie, mira tenendo destro e spara una volta col sinistro.
   Verifica che allo sparo corrispondano un suono e una didascalia in alto.
   Dopo che il suono è finito, attiva F7, aspetta e ripremi F7. Lo sparo
   precedente non deve ripartire. In `./combat-demo.sh --fresh`, premi E
   se la minaccia ha messo in pausa, colpisci lo zombie davanti con la
   mazza e fai qualche passo. Controlla se senti il colpo e i passi e se
   il loro volume si distingue da quello dello sparo. Annota separatamente
   suoni assenti, didascalie assenti e volume scomodo.

Il launcher locale usa copie di prova. La variante credito conserva stock e
posizione, ma parte da saldo e credito zero. Il diario vuoto conserva la
proposta non assegnata e parte senza missioni note o tracciate. I riscontri
automatici sulla preparazione restano negli artifact locali.
