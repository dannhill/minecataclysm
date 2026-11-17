# Quattro controlli prioritari proposti — 2026-11-15

Documento scritto da un LLM sulla richiesta diretta dell'unico sviluppatore
umano di altri quattro test prioritari. Sono istruzioni ancora da eseguire,
non risultati né PASS dedotti da prove automatiche.

La corrispondenza del nuovo giro è:

1. **COMP-01.3** — `./companions-demo.sh --fresh`; destro sull'alleato →
   Companion orders and rules → Combat rules → Use firearms. La fixture parte
   da Base On / Temporary override Off / Effective Off. Disabilitare e poi
   riabilitare la base: l'override resta Off e l'effettivo resta Off. Use base
   rule (remove override) rimuove l'override ed Effective passa a On. Verificare
   anche il cambio esplicito di una regola di comportamento e politica di mira;
   vale solo per l'alleato, senza effetti gratuiti su inventario/abilità/energia.
2. **COMP-01.4** — nella stessa demo, impostare Use firearms con Disable base
   rule e Temporarily enable: Base Off / Override On / Effective On, diversi
   dai valori iniziali. Annotare la regola/politica eventualmente cambiata.
   Uscire normalmente, riaprire `./companions-demo.sh` senza `--fresh` e
   controllare stesso alleato e valori conservati. Nessuna riapertura automatica
   del pannello o ripetizione degli ordini; guardia/seguito già provati restano
   un test distinto. La scelta inversa alla fixture evita un falso PASS da reset.
3. **NPC-01.3** — `./conversation-demo.sh --fresh`; avvicinarsi all'NPC davanti,
   destro, domanda innocua disponibile, lettura della risposta e dello storico,
   ritorno al menu, osservazione/opinione quando presente, poi Leave conversation
   o Esc. La partita riprende; nessuna risposta viene scelta al posto del
   giocatore e non rimane una finestra bloccata. Il commercio è già implementato
   e ha i suoi test: rimossa dalla checklist la vecchia aspettativa superata
   dell'avviso di trade rinviato, senza modificare il runtime.
4. **READ-01.1** — `./reading-demo.sh --fresh`; selezionare in I il libro sui
   gatti non identificato. Consultare i dettagli mantiene la pausa e non lo
   identifica. Skim book richiede il lavoro nativo; completato lo sfoglio,
   il libro risulta identificato e il comando diventa Read. Stesso libro,
   nessuna perdita o copia, niente identificazione gratuita dalla consultazione.

Script pubblici e fixture dei tre tipi di demo verificati presenti; etichette
degli ordini e stato iniziale confrontati con `cwm_companions.h` e la creazione
indipendente della fixture. Nessun comando è eseguito nelle partite del developer.

La selezione copre precedenza degli ordini, persistenza di stato non predefinito,
dialoghi ordinari e acquisizione della conoscenza dei libri. Nessun nuovo test
aggiunto: **43 PENDING** invariato. Il credito e il caso di freddo non riprodotto
restano distinti; nessuna modifica di codice/build da questa proposta.

## Riscontro umano del giro

Il developer risponde direttamente «1 PASS 2 PASS 3 PASS ... 4 PASS»:

1. **COMP-01.3 PASS** — precedenza della regola temporanea e cambi espliciti.
2. **COMP-01.4 PASS** — persistenza dei valori modificati dell'alleato.
3. **NPC-01.3 PASS con richiesta UX separata** — risposte, navigazione e uscita.
4. **READ-01.1 PASS** — identificazione dopo lo sfoglio nativo del libro.

Sono risultati di playtest umani dell'unico sviluppatore, non inferenze dai
test automatici. **43 meno quattro =39 PENDING**, nessun nuovo test o FAIL.
Gli altri casi degli stessi moduli non vengono accettati per estensione.

**NPC-SCROLL-01 TODO:** dopo la scelta di un'opzione di dialogo, scorrere
automaticamente lo storico fino all'ultima interazione, rendendo visibile la
nuova battuta. Questo è un intervento UX richiesto, distinto dal PASS funzionale
NPC-01.3; non è implementato da questo aggiornamento documentale e non aggiunge
un test manuale al contatore. Conservare la consultazione dello storico mentre
si legge; far seguire il fondo quando arriva la nuova interazione scelta.

## Prossimi quattro controlli richiesti

1. **REST-01.1** — nella demo riposo provare attesa breve/recupero fiato,
   consultazione in pausa, interruzione e assenza di passi accodati. Il tempo
   usa sempre l'unico F8; non provare un risveglio gratuito dal sonno effettivo.
2. **Raccolta sfusa diretta, punto2** — transfer-demo con30 munizioni: depositarne
   7 su una casella vuota, attendere il deposito, chiudere il menu e raccogliere
   quella singola pila col destro, senza menu9×3. Controllare23 rimaste dopo il
   deposito e30 complessive dopo la raccolta, senza copie o perdite.
3. **JOURNAL-01.2** — alternare esplicitamente Track this mission tra le due
   missioni attive; consultare l'altra senza premere Track non cambia la scelta,
   non completa missioni e non assegna premi. Coordinate note native, inclusoZ,
   soltanto dove esiste una destinazione, senza fallback inventato.
4. **DIS-01.2** — avviare realmente lo smontaggio delle fasce nella demo; I
   ferma progresso/mondo, chiudere I riprende. È lavoro nativo temporizzato,
   distinto dal rifiuto della conferma già accettato in DIS-01.1.

Sono quattro casi già pendenti. Nessuna nuova esecuzione o accettazione in
questa selezione: totale39 invariato, codice/build invariati. Gli script e
le fixture dei quattro tipi di demo risultano presenti.

## Secondo riscontro umano e cambio di priorità

Fonte: unico sviluppatore, messaggio del2026-11-15. REST-01.1 FAIL:
ripetuti «CDDA state not synchronized» / Connect/Synchronizing durante attesa
e Catch your breath a0.5x,1x,2x; a4x non osservato. I ferma tempo e progresso,
chiudendolo riprende; B/Interrupt rest interrompe correttamente. Questi sottocasi
non bastano a chiudere il FAIL complessivo. Raccolta sfusa punto2, JOURNAL-01.2,
DIS-01.2 PASS umani. Restano35 PENDING +1 FAIL,36 punti aperti complessivi.

Nuova direttiva: proporre le prove in ordine di dipendenza, così una modifica
alle fondamenta emersa dopo non costringa a rifare le prove delle feature.
Prima correggere/ricontrollare il difetto del tempo e della sincronizzazione;
non usare4x come soluzione del guasto. I PASS precedenti restano evidenza degli
scenari effettivamente provati, senza accettare automaticamente i nuovi fix.

## Quattro controlli in ordine di dipendenza

Una priorità per dipendenze: prima tempo/stato autorevole; poi proprietà delle
pause; poi decisioni native; infine traduzione di quelle interfacce. Il primo è
il solo ricontrollo necessario di un FAIL dopo la sua correzione; gli altri sono
punti già pendenti. Nessun nuovo test è aggiunto al contatore. Non garantisce
assenza assoluta di regressioni future, ma evita di costruire accettazioni a
valle di un guasto già noto. I test automatici restano separati dai PASS umani.

1. **REST-01.1 — Tempo e sincronizzazione.** Dopo aver chiuso e rilanciato il
   gioco aggiornato, `./rest-demo.sh --fresh`. Con F8 selezionare0.5x **prima**
   di B → Wait or catch your breath → Wait20 heartbeats. Lasciare finire una
   breve attesa a0.5x,1x,2x,4x:20 secondi simulati richiedono circa40/20/10/5
   secondi reali, oltre a menu e costi nativi; i menu aperti non vanno contati.
   Nessun CDDA state not synchronized / Connect/Synchronizing persistente.
   Su una delle attese provare I, aspettare5 secondi, chiudere: tempo/progresso
   fermi e poi ripresa. Avviarne un'altra e interromperla con B → Interrupt rest.
   Provare Catch your breath con stamina mancante, eventualmente in una nuova
   demo fresca: è un riposo lungo e può usare la diversa gamma contestuale di
   F8, poi deve ripristinare la velocità ordinaria scelta. Non serve riprovare
   morte, sonno completo o tutti gli altri save/load già accettati.
   **Se fallisce fermare i controlli2–4:** sono costruiti sulla stessa connessione
   e sullo stesso orologio e il loro esito sarebbe meno attendibile.
2. **JOURNAL-01.3 — Proprietà della pausa e consultazione senza effetti.**
   `./journal-demo.sh --fresh`, F7 per attivare la pausa manuale, poi J.
   Sfogliare Completed/Failed: niente comandi per completarle, riattivarle o
   seguirle. Controllare la scadenza approssimata senza orologio. Esc chiude J;
   attendere5 secondi: il gioco deve rimanere fermo finché si preme di nuovo F7.
   Serve a verificare che chiudere una finestra non tolga una pausa di altra
   origine, una proprietà condivisa dai menu delle feature successive.
3. **NPC-01.2 — Consultazione di una decisione nativa.**
   `./conversation-demo.sh --fresh`, destro sull'NPC davanti, senza urtarlo.
   Lasciare il dialogo aperto5 secondi, leggere e scorrere storico/risposte,
   usare Next/Previous page quando presenti. Nessun tempo trascorso, opzione
   persa o risposta scelta solo per aver sfogliato. Uscire con Esc/Leave.
   Dopo il controllo della pausa delle query, questo verifica la distinta
   proprietà del menu nativo su cui si appoggiano scambi e servizi NPC.
4. **LANG-02.1 — Traduzione senza riavvii o azioni implicite.**
   Nel normale `./start.sh`, oppure `./equipment-demo.sh --fresh` per la stessa
   integrazione in una scena isolata, Esc → Italiano → English, due volte
   anche rapidamente. Menu e partita restano aperti/fermi; la lingua cambia
   subito, WIP compare soltanto per Italiano. Chiudere Esc e controllare I/H/K:
   testi nella lingua scelta, icone/oggetti invariati. Nella demo aprire Riponi
   della mazza e annullare la domanda: nuova lingua, nessun trasferimento.
   Lasciare English. Lo si fa dopo il flusso nativo, così si distingue un
   difetto della traduzione da un difetto di base del menu o dell'azione.

Se2 o3 falliscono sulla pausa o sul controllo delle scelte, fermare i controlli
a valle e riferire il punto preciso. Un difetto solo estetico va annotato senza
trasformarlo automaticamente in un FAIL dell'autorità o del tempo.

La correzione automatizzata è stata installata dopo la riproduzione su una copia
del salvataggio fallito: durata di interpolazione delle creature fuori dai limiti
nel riposo accelerato. [Consegna ed evidenze](../fixes/rest-rate-feedback-2026-11-15.md).
Riprovare il punto1 con una nuova esecuzione del gioco; il FAIL umano resta aperto.
