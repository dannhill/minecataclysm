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

Limiti: niente attacco deliberato a neutrali/amici, reach attack o armi da fuoco
in questa fetta. Animazioni dei mob, equipaggiamento visibile e feedback di
impatto restano nel piano. Il gesto della mano è cosmetico; la geometria Luanti
non decide distanza o esito nativo. L'attacco puntato evita il rerouting casuale
del movimento stordito; le penalità native del combattimento restano applicate.
M5.5 resta FAILED e SAVE-001 completo resta aperto.

Validazione manuale IN ATTESA, insieme alle altre due feature:
[checklist cumulativa](../validation/pending-manual.md). Verifiche automatiche
in corso contro sorgenti ricostruiti; prove/identità finali saranno registrate
alla consegna, senza assumere alcuna approvazione dell'utente.
