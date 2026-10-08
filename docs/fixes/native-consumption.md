# Cibo e bevande nativi — prima fetta

`I` permette di selezionare cibo o acqua posseduti e scegliere **Mangia** o
**Bevi**. Nome, provenienza, porzioni, durata e disponibilita vengono da CDDA.
Il dettaglio mostra il primo avviso conoscibile; dopo il clic l'attivita nativa
chiede tutte le conferme applicabili, per esempio per cibo marcio. **No**
conserva l'oggetto e non avvia lavoro. I nomi/avvisi nativi possono essere in
inglese; le icone non ancora mappate usano il fallback esistente.

Il consumo avviene attraverso avatar_action::eat e consume_activity_actor,
non con modifiche locali a fame/sete o all'inventario Luanti. Una porzione
viene tolta dal percorso consume(item_location) alla fine dell'attivita.
Bottiglie e contenuti residui rimangono nativi, come digestione, effetti,
utensili necessari, vincoli corporei e conferma di proprieta. La durata
riportata e lavoro CDDA in mosse; non e una promessa di secondi reali. Il
ritmo segue il tempo RT-02 scelto, 4x di riferimento, con pause e minacce.

Una scritta segnala il progresso autorevole. **I** durante un pasto ferma il
lavoro e offre **Interrompi consumo**. La richiesta chiude il menu e usa
Character::cancel_activity al confine del coordinator, senza attendere che
l'attivita finisca e senza rimborsare tempo. Le porzioni non ancora consumate
restano nell'inventario. In questo pin l'attore nativo confronta anche
l'indirizzo di consume_item in can_resume_with_internal: una nuova richiesta
dello stesso oggetto riparte con la durata completa. Non si modifica quella
regola in questa fetta. Salvataggio/caricamento di un'attivita gia avviata
conserva invece il lavoro residuo tramite serializzazione nativa dell'attore.

Movimento/posture e altri comandi di gioco non vengono accodati durante il
consumo: interrompi prima. Menu, scheda e controlli temporali restano leggibili.
Un tasto tenuto durante il pasto deve essere rilasciato prima di riprendere
il movimento. La pausa F7 non viene rimossa chiudendo I; i clic durante
pausa manuale/minaccia non diventano azioni ritardate. In modalita ordinaria
il consumo usa la stessa attivita senza pacing reale e termina rapidamente;
progresso/interruzione giocabili sono soprattutto un'esperienza RT-02.

## Confine e invarianti

CWM 2.11 aggiunge un quinto comando alla selezione di oggetti posseduti,
durata/etichetta/avviso nativi e progresso opzionale nelle pubblicazioni.
La query rimane di sola lettura e limitata. Selezione, proprieta/possesso,
catena delle tasche, tipo, cariche e ruolo vengono riverificati all'ammissione
ed esecuzione. Il cliente attende ACK e stato autorevole, senza applicare
consumi ottimistici. L'ACK di Mangia/Bevi indica l'avvio, non il pasto concluso.

L'interruzione usa un token effimero dell'attivita, mai un nuovo campo save
canonico. Ha le stesse identita di sessione/connessione, sequenze e ledger
at-most-once degli altri comandi. Ogni avvio dalla GUI rinnova il token,
anche per lo stesso alimento; token scaduti o diversi non interrompono il
pasto successivo. Le pubblicazioni riportano lavoro totale/residuo CDDA;
valori malformati provocano resync. [Contratto](../../protocol/PROTOCOL.md).

La voce Accesso nativo descrive obtain_cost: il percorso eat del pin non lo
addebita separatamente. Il bridge non aggiunge un costo artificiale. Questa
fetta comprende FOOD/DRINK accessibili in tasche CONTAINER non sigillate.
MED, strumenti medici, contenuti tecnici e alimenti con use_action speciale
richiedono un'interazione dedicata e sono bloccati; PETFOOD segue l'eccezione
nativa di eat. Aprire sigilli, travasare/riempire, bere da fontane, consumare
quantita scelte, medicina per parte e progresso generale restano nel piano.

## Verifica e riproduzione

[Evidenza e identita](native-consumption-evidence.json). Build incrementali
su ricostruzione da pin e patch completi; nessun cold build, nuovo gate M5.5
o certificazione SAVE-001 completa viene dichiarato. Il lettore/creatore di
fixture e collegato al core pristine CDDA, senza bridge. Salvataggi e config
di tutti i test sono copie isolate, mai quelli dell'utente.

I test nativi verificano assegnazione e durata, digestione/porzione, acqua
annidata/bottiglia, cariche mutate, annullamento immediato/dedup, token scaduto
e azioni bloccate durante il consumo, oltre alle regressioni CWM/acqua/pickup.
Protocollo e Luanti verificano bounds/resync, etichette ed escaping. Il driver
`tests/consumption_gui_test.py` usa il vero renderer, input X11, relay senza
mutazioni, screenshot e lettura indipendente del save; comprende avvisi,
pausa, progresso, interruzione, riconnessione e caricamento dell'attivita.

Risultati finali tutti PASS: CDDA 7.939 asserzioni / 52 casi; Luanti 308
verifiche individuali e 648 asserzioni Catch2; protocollo 6/6. Renderer consumo:
33 verifiche su ricostruito, 33 su installato, 14 di rientro nel pasto gia in
corso, 22 in modalita ordinaria. Regressione inventario/equipaggiamento:
29 verifiche sul runtime installato. Al rientro il residuo nativo viene
consumato e il lettore pristine conferma ACT_NULL e zero mele fresche residue.

`./consumption-demo.sh --fresh` crea una sessione isolata; senza --fresh la
riprende. La fixture fornisce zaino, due mele fresche, una marcia, una bottiglia
da due litri con quattro porzioni d'acqua pulita e un sasso. Gli alimenti sono
inizializzati con temperatura nativa di 20 C: il congelamento normale del
mondo non viene aggirato dal gameplay. Resta pendente l'accettazione grafica
utente, insieme ai quattro test inventario gia rinviati:
[backlog manuale](../validation/pending-manual.md). Prossima fetta: medicina
minima con selezione esplicita di oggetto e parte del corpo, poi crafting.
