# Combattimento corpo a corpo puntato

Prima fetta del combattimento previsto dal playable core: clic sinistro su una
creatura percepita, ostile e adiacente. Un nuovo clic per ogni attacco; il mouse
premuto non ripete colpi. CDDA usa arma impugnata o mani nude, difese passive,
arti marziali, danni, pratica, stamina e costo nativi. Luanti punta i modelli e
presenta l'esito, senza applicare danni propri.

È indipendente dalle prove ancora rinviate di raccolta e scheda corporea.
`./combat-demo.sh --fresh` usa una copia isolata creata dal core pinned originale:
mazza già impugnata e zombie ostile subito davanti, con immobilizzazione nativa
solo nella fixture. E riconosce la minaccia; F7 pausa/riprende. Nessun attacco
viene accodato durante pausa, menu o recupero della connessione.
La tecnica BRUTAL della mazza può respingere il bersaglio: riavvicinarsi
prima del colpo successivo. Anche questo effetto è nativo.
Senza `--fresh` riprende la stessa sessione canonica CDDA.

CWM 2.7 abilita AttackRequest con identità canonica del bersaglio, inclusa nella
deduplicazione. Ammissione ed esecuzione ricontrollano identità, percezione,
ostilità, stesso Z, adiacenza e percorso nativo. Se il bersaglio cambia o si
allontana, nessuna sostituzione per coordinate. Il puntamento considera solo
nodi attore visibili e si arresta alla prima superficie di terreno selezionata.
Una creatura non ostile davanti a un nemico non viene saltata dal puntamento.
La conferma nativa di un'arma molto lenta usa le decisioni del coordinator;
perdita del client equivale a No. Non cambia la formula del combattimento.

La percezione resta quella nativa: `Creature::sees()` percepisce sempre un
mostro adiacente sullo stesso livello, e `map::clear_path()` esclude il punto
finale. Questi controlli non equivalgono a un raycast 3D: è il puntamento del
client a fermarsi alla geometria visibile, mentre CDDA decide la portata.
Il clic non invia un comando di camminata; eventuali spostamenti delle
tecniche di combattimento rimangono risolti da CDDA.

Limiti: niente attacco deliberato a neutrali/amici, reach attack o armi da fuoco
in questa fetta. Animazioni dei mob, equipaggiamento visibile e feedback di
impatto restano nel piano. La mano è ancora una presentazione generica,
non il modello della mazza impugnata. Il gesto della mano è cosmetico; la geometria Luanti
non decide distanza o esito nativo. L'attacco puntato evita il rerouting casuale
del movimento stordito; le penalità native del combattimento restano applicate.
M5.5 resta FAILED e SAVE-001 completo resta aperto.

Validazione manuale **IN ATTESA**, insieme alle altre due feature:
[checklist cumulativa](../validation/pending-manual.md). L'utente ha chiesto
esplicitamente il secondo rinvio di entrambe e sviluppo autonomo di questa
feature; nessuna accettazione manuale è stata inferita.

## Verifica della consegna

Runtime compilati da sorgenti ricostruiti al commit
`d0b180718b8b1867e0427296ca2c35c2c374bc54`; harness finale di melee al commit
`ebc5788`. Quest'ultimo cambia solo test/checklist/documentazione. Patch e
inventari completi in `baseline/manifest.json`; riproduzione indipendente PASS.
Compilazione incrementale con cache mantenute, non build completa a freddo.
Coppia CWM 2.7 installata atomicamente per file, identica SHA256 ai build;
rollback della coppia 2.6 conservato. Prove/checksum nella
[ricevuta](pointed-melee-evidence.json), artefatti in
`artifacts/playable-core-melee-20261008/`.

- CDDA: **7.297 asserzioni in 38 casi PASS**, filtro `[cwm],[diving],[pickup]`,
  seed 42. Guardie al momento di esecuzione, pet/amici, NPC nemici/neutrali,
  duplicati pendenti/completati, conflitto di identità, cancellazione e pausa.
- Confronto diretto con attacco originale per bump, stessa fixture e RNG:
  HP del bersaglio, mosse, stamina e stato RNG identici.
- Conferma dell'arma lenta: Yes/Ignore/No e perdita del peer PASS. Il periodo
  nativo di Ignore è rispettato; lo stato precedente non viene falsamente
  azzerato dall'helper di setup dei test.
- Protocollo **5/5 PASS**; Luanti **306 test e 648 asserzioni Catch2 PASS**.
- GUI reale tramite `start.sh`, runtime installati: **21/21** in modalità
  ordinaria, **23/23** in continuo 4x. Puntamento effettivo del modello,
  singolo colpo per pressione, niente attacco nel vuoto/in pausa, recupero
  senza replay, contraccolpo e rifiuto fuori portata, riavvicinamento nativo.
- Morte rimuove la scena; il core CDDA pinned originale rilegge il save,
  riconoscendo lo specifico cadavere `Bersaglio melee` e l'arma ancora impugnata.
  Posizione finale del personaggio e tempo pagato sono nativi.
- Regressione GUI della scheda corporea: **19/19 PASS**, incluso HP esatto
  invariato per tutte le 12 parti. Regressione della raccolta: **18/18 PASS**.

I primi tentativi falliti sono conservati negli artefatti: correzioni alle
assunzioni della prova (miss, credito frazionario, percezione adiacente,
setup/cooldown e contraccolpo), non eliminazione delle regole native.
L'ispezione delle immagini conferma modello puntabile e rimozione dopo morte;
questo controllo dell'agente non sostituisce la valutazione visiva dell'utente.
