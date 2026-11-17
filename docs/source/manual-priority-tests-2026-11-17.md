# Riscontro umano e prossimo giro per dipendenze — 2026-11-17

Documento scritto da un LLM dalle direttive e dai risultati forniti direttamente
dall'unico sviluppatore umano. I PASS sotto sono suoi playtest, non esiti di
automazione eseguita dall'agente. Questo turno aggiorna documentazione e
priorità; non modifica codice, binari, salvataggi o launcher.

## Risultati accettati

1. REST-01.1 PASS: chiuso il FAIL del2026-11-15 dopo la correzione della
   proiezione delle creature in riposo accelerato. Commento REST-FB-02 separato.
2. JOURNAL-01.3 PASS: consultazione degli stati e pausa manuale conservata.
3. NPC-01.2 PASS: lettura/sfoglio della conversazione senza avanzamento.
4. LANG-02.1 PASS: cambio lingua corrente senza riavvio e senza azioni implicite.

Da35 PENDING +1 FAIL a **32 PENDING**, nessun FAIL aperto nelle checklist
correnti. Tre casi pendenti e il FAIL chiusi; nessun nuovo caso aggiunto.
Decomposizione:7 casi espliciti residui (NPC1/4, TRADE1/3, JOURNAL1, COMP1,
READ-FB1) e25 casi storici (eccezioni UX-02 3, UX-05 1, modelli3, movimento2,
feedback10, ricontrolli dopo i sette gate3, Windows3). I commenti OPEN e i gate
architetturali storici restano distinti dal conteggio dei punti manuali.

## Osservazioni sul recupero del fiato e sulle scorciatoie

**REST-FB-02 OPEN:** recupero quasi istantaneo dopo Catch your breath partendo
da1x; personaggio immobile per qualche secondo dopo. La lettura del codice
conferma che la scelta nativa crea ACT_WAIT_STAMINA con90000 moves_total
(`handle_action.cpp`). RestTracker::speed_context la tratta come riposo lungo:
il clock sceglie la preferenza REST, inizialmente1024x, ricordando la precedente
velocità PLAY. È la singola velocità contestuale autorizzata, non un nuovo
moltiplicatore. Se1x indicava già REST1x durante l'attività, il recupero
quasi istantaneo non è spiegato da questo cambio di contesto.

L'attività termina nativamente al raggiungimento della stamina richiesta
(`activity_handlers::wait_stamina_do_turn/finish`). Il ponte blocca il movimento
con attività/pausa e richiede il rilascio di un intento tenuto durante il blocco;
il server conserva inoltre il debito di tempo delle azioni. Queste sono piste,
non la dimostrazione della causa dei secondi di immobilità riportati. Le tracce
delle quattro regressioni Nov15 mostrano input_ready subito dopo la fine del
recupero accelerato, ma il driver non prova a camminare subito: non escludono il
sintomo. Registrarlo separatamente, senza inventare un cooldown nativo o
revocare il PASS umano. Prima di un nuovo ricontrollo preparare una misura
controllata di fase, velocità effettiva, debito, pausa e intento/rilascio WASD.

**MENU-TOGGLE-01 TODO/proposta:** adottare J per aprire/chiudere il diario e K
per aprire/chiudere il crafting, come I. Attualmente Game::processKeyInput apre
J/K; il gestore modale di GUIFormSpecMenu gestisce genericamente Esc/I per la
chiusura. La differenza osservata è coerente col codice. La futura modifica
deve rispettare il focus della ricerca (digitare k non chiude), tasti
riconfigurati e singole pressioni anziché auto-repeat. Riutilizzare il percorso
di chiusura con pause native/manuali/minaccia, progressi e decisioni intatti.
Durante un lavoro K mantiene l'ispezione e il ritorno al progresso nativo.
È una raccomandazione richiesta dal developer, non una modifica già consegnata.

## I prossimi quattro punti, tutti già pendenti

Le fondamenta di tempo, pausa, decisioni native e lingua hanno ora il PASS
umano. Proseguire con ingresso contestuale, annullamento senza effetti,
consultazione dei sottopannelli e persistenza dopo un flusso stabile. Non si
propone nuovamente il credito senza una scena deterministica né il freddo
non riprodotto contando su un incontro casuale.

1. **NPC-01.1 — Puntamento, ingresso e oggetto impugnato.**
   `./conversation-demo.sh --fresh`: NPC direttamente davanti, pochi passi.
   Puntare al corpo, verificare l'hint e usare RMB: nome e risposte corretti,
   senza urtarlo o camminargli addosso. Uscire, impugnare il sasso disponibile
   tramite I → sasso → Wield, poi riprovare il destro sullo stesso NPC non ostile:
   deve parlare, senza attaccarlo. È il prerequisito comune per i pannelli2/3;
   se fallisce la selezione/il comando del destro, fermare i controlli dipendenti.
2. **TRADE-01.1 — Offerta annullata senza trasferimenti.**
   `./trade-demo.sh --fresh`: parlare all'NPC → risposta per commerciare.
   Due pannelli con icone, nomi/tooltip, quantità e saldo; tempo fermo.
   Annotare saldo/quantità dopo l'apertura; selezionare la benda o alcune
   munizioni, poi Cancel trade o Esc, senza confermare lo scambio. Riaprire:
   offerta vuota, inventari e saldo non modificati dall'annullamento. Non serve
   ripetere lo scambio effettivo/persistenza già PASS né superare il credito.
   L'apertura può effettuare il restock/riordino nativo del venditore: non è un
   trasferimento al giocatore da annullare retroattivamente.
3. **COMP-01.1 — Consultazione e limiti dei comandi ai compagni.**
   `./companions-demo.sh --fresh`: destro sull'alleato → Companion orders and
   rules. Visitare Combat/Behavior rules, pagine e politiche di mira/bionica
   quando disponibili, senza cambiarle. Impostazioni del solo alleato scelto,
   tempo fermo e nessuna cura/oggetto/energia/abilità concessa dalla lettura.
   Esc per uscire. Per la parte sconosciuto, usare l'NPC non alleato del test1:
   Companion orders and rules non deve essere disponibile. Non occorre
   ripetere modifiche di regole, guardia/seguito o persistenza già PASS.
4. **NPC-01.4 — Persistenza della conversazione senza riprodurre azioni.**
   Tornare a `./conversation-demo.sh` **senza --fresh**, sulla sessione del
   test1. Parlare, fare una domanda innocua, uscire con Leave/Esc e chiudere
   normalmente il gioco. Riaprire ancora senza --fresh: stesso personaggio,
   NPC e mondo. Dialogo non riaperto automaticamente, tempo non bloccato dal
   vecchio menu; un nuovo destro riapre una conversazione utilizzabile. Nessun
   oggetto/premio o missione ottenuto per aver salvato/letto; eventuali effetti
   realmente scelti conservano esclusivamente la persistenza nativa.

Verificati presenti gli script pubblici e le relative fixture utente/baseline;
la fixture conversazione contiene un sasso utilizzabile per l'impugnatura.
Nessun mondo del developer viene aperto per preparare questa proposta. Un FAIL
su un componente condiviso rinvia i controlli che dipendono da quel componente;
un appunto estetico resta distinto da perdita di stato o esecuzione di azioni.
