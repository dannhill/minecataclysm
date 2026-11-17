# Riscontro umano: pannelli, scambi e lotto crafting — 2026-11-11

Documento scritto da un LLM sulle direttive e sui risultati comunicati
direttamente dall'unico sviluppatore umano. Le accettazioni riportate sono
playtest umani, distinte dalle prove automatiche precedenti.

Il developer risponde al giro prioritario proposto il 2026-11-09:

1. **READ-FB-01.1 NON RIPRODOTTO**. Rimane PENDING per la conferma personale
   della risposta alla distrazione; non è un FAIL e non viene convertito in PASS.
   La regressione automatica del difetto precedente conserva la propria evidenza.
2. **WORK-FB-01.1 PASS** — pannello coerente e riapribile per lettura/bevuta.
3. **TRADE-01.3 PASS parziale** — accettati i controlli effettivamente proposti
   e provati, con esclusione esplicita della richiesta oltre il credito.
   Il developer non ha provato quest'ultima parte e chiede cosa significhi il
   credito; la parte finanziaria rimane PENDING. Il caso contenitore+contenuto
   della checklist estesa non era nel prompt ricevuto e non viene dedotto da
   questa risposta.
4. **Ricontrolli dopo i sette gate, punto2 PASS** — il developer conferma
   esplicitamente otto makeshift bandages al termine e chiede di ricordare lo
   scopo della prova. Nessuna nuova anomalia di crafting segnalata.

Sono chiusi completamente due punti: **49 meno due =47 PENDING**. Il caso
non riprodotto e il test finanziario incompleto mantengono i rispettivi punti
pendenti; nessun nuovo test o FAIL aggiunto. LIQ-FB-01 resta OPEN.

## Credito: spiegazione verificata nel codice

`trade_ui` parte da `NPC.op_of_u.owed - service_cost` e calcola il saldo finale
aggiungendo il valore offerto dal giocatore e sottraendo quello richiesto.
Saldo positivo: l'NPC deve valore al giocatore; negativo: il giocatore deve
valore all'NPC. `npc_will_accept_trade` verifica saldo+max_credit_extended>=0
per gli scambi ordinari. Gli alleati con scambio libero seguono il caso nativo
senza debito. Il credito è contabilità con quel singolo NPC, non un nuovo
portafoglio introdotto dall'integrazione.

Il campo **Credit limit** mostra quanto debito verso di lui l'NPC è disposto
ad accettare; il saldo già a favore del giocatore è distinto. Esempio didattico:
saldo iniziale +20, offerta5, richiesta30 dà -5. Con limite10 è ammissibile;
una richiesta40 darebbe -15 e richiederebbe un'offerta maggiore.

La fixture `--create-trade` assegna deliberatamente `owed=100000` centesimi,
cioè $1000 di saldo favorevole, e trust20. Serve a rendere fattibile il test
positivo dello scambio. Non è una fixture deterministica per superare il
credito con gli oggetti disponibili. Non chiedere di insistere sulla stessa
demo: prima di riproporre la parte finanziaria preparare e verificare una
scena con saldo/limite e merce tali da attivare sicuramente il rifiuto.

## Crafting: perché il test era importante

Nel riscontro del 2026-10-18 la voce percepita come bandage spariva dopo un
progresso0% senza produrre nulla, anche in lotto4. L'indagine trovò
`nested_bandages`: una categoria di navigazione nativa scambiata dall'export
per una ricetta eseguibile. La correzione esclude quelle categorie dall'avvio.
L'utente aveva inoltre segnalato la perdita della selezione al cambio lotto.

Il ricontrollo verifica tre cose: avvio delle sole ricette effettive; cambio
lotto con selezione/requisiti/durata coerenti; produzione reale al termine,
non soltanto un ACK o una barra che scompare. La ricetta senza utensile
`bandages_makeshift` ha `result_mult=2` in
`cdda/data/json/recipes/other/medical.json`: lotto4 esegue quattro lavorazioni,
quindi4×2=8 bende. Il risultato esplicitamente osservato è quello atteso.

Questo aggiornamento registra risultati e chiarimenti; non modifica runtime,
build o regole native. Il seguito della roadmap resta il completamento delle
funzioni essenziali del core e del loop liquidi, con i controlli personali
residui in backlog; nessun obbligo di esaurirli prima di proseguire.

## Quattro ulteriori controlli richiesti dal developer

Alla richiesta successiva di altri quattro controlli importanti, la selezione
tra quelli già pendenti è:

1. **LANG-02.2** — cambiare lingua con una lettura in corso, verificando pausa,
   prosecuzione senza riavvio/duplicazione e preferenza conservata al riavvio.
   Nel flusso attuale Esc nasconde il pannello del lavoro e un secondo Esc
   apre il menu di pausa da cui cambiare lingua.
2. **DIS-01.1** — annullare lo smontaggio senza consumare l'oggetto/produrre
   componenti; con F7 attivo nessun avvio accodato per la ripresa.
3. **JOURNAL-01.4** — selezionare esplicitamente Find Flag, salvare e riaprire
   journal-demo senza `--fresh`, conservando missioni/stati/selezione.
4. **COMP-01.2** — ordine Guard this position e poi Follow me; osservare l'AI
   nativa solo dopo aver lasciato la conversazione, senza teletrasporti.

Queste sono istruzioni, non risultati. Le quattro fixture e gli script pubblici
esistono; nessuna modifica a runtime o fixture in questa selezione. Totale
47 PENDING invariato. Il credito e il caso non riprodotto non vengono riproposti
senza prima predisporre una prova deterministica quando necessaria.

## Secondo riscontro: lingua, smontaggio, missioni e compagni

Il developer risponde al giro appena descritto «1 PASS 2 PASS 3 PASS ... 4 PASS»:

1. **LANG-02.2 PASS** — cambio lingua durante il lavoro, pausa/prosecuzione e
   preferenza conservata al riavvio nel percorso proposto.
2. **DIS-01.1 PASS** — annullamento senza consumo e nessun lavoro accodato
   sotto pausa manuale.
3. **JOURNAL-01.4 PASS** — missione seguita e storia conservate al caricamento.
4. **COMP-01.2 PASS** — guardia e ritorno al seguito nativo dell'alleato.

I quattro risultati sono playtest umani dichiarati dall'unico sviluppatore;
non sono deduzioni dalle prove automatiche. **47 meno quattro =43 PENDING**.
Non vengono accettati per estensione gli altri casi degli stessi moduli.
READ-FB-01.1 non riprodotto, TRADE-01.3 parziale e LIQ-FB-01 OPEN restano invariati.
Nessuna modifica a codice, build o protocollo e nessun nuovo test aggiunto.

Il developer domanda se il tracker delle missioni sia una nuova meccanica.
Verificato anche nei sorgenti upstream pinned non modificati:
`src/mission_ui.cpp` seleziona la missione tramite `avatar::set_active_mission`;
`avatar.cpp` possiede la selezione, e il salvataggio canonico serializza
`active_mission` insieme alle liste delle missioni. Quindi diario, stati e
missione seguita sono funzioni native CDDA. L'integrazione aggiunge la GUI
Luanti su J, il pulsante Track this mission e i messaggi CWM che invocano lo
stesso setter dopo validazione. La lettura del diario non assegna/completa
missioni o eroga ricompense; un waypoint sull'HUD3D rimane una presentazione
separata e non è introdotto dal semplice tracciamento nel diario.
