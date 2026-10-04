# Riscontro manuale RT-01 — 2026-10-04

Fonte: messaggio dell'utente dopo la consegna del primo prototipo dello
[scheduler in tempo reale](../prototypes/rt01-real-time.md), report `6e96ff3`.
Il riferimento identifica la consegna associata: l'utente non fornisce
checksum dei binari o identificativo della sessione provata.

> Valido tutto però per dio è troppo lenta la velocità base. Inoltre pensavo che si era detto che il movimento non sarebbe più stato a griglia discreta bensì continuo. Parliamone un attimo.

La checklist consegnata è accettata per lo scheduler e le funzionalità
circoscritte della demo. Non occorre ripeterla. Il ritmo base 1× è giudicato
troppo lento e non va trattato come scelta finale accettata del prodotto.

L'utente chiede di chiarire il controller continuo già previsto. RT-01 usa
ancora otto direzioni native e interpolazione: non implementa l'offset
continuo autorevole, l'arresto dentro una casella o orientamenti arbitrari.
La variante continua del piano resta da realizzare e confrontare; questa
validazione non la certifica e non sceglie la griglia come controller finale.

Il rapporto 1:1 resta il baseline tecnico misurato. Il ritmo del prodotto
deve essere discusso e ricalibrato. Accelerazione globale e modifica dei
soli costi/velocità di locomozione hanno effetti differenti: la prima accelera
anche AI, attacchi e attività; la seconda richiede adattamento e verifica
espliciti dei rapporti fra attori e delle meccaniche native. Nessun nuovo
default, moltiplicatore o bilanciamento è approvato da questo messaggio.

Segue il dialogo su velocità e controller. Sono ancora da confrontare anche
le scale a gradini e a pioli automatiche/continue. Gli esiti e i limiti di
fase 2, FND-04 e M5.5 restano distinti dalla validazione di questa demo.

## Preferenza di ritmo dopo il chiarimento

Alla domanda su quale velocità provata con F8 sia più vicina a quella
desiderata, l'utente risponde:

> tra quelle disponibili quella che mi piace di più è x4.

Usare **4× globale come ritmo di riferimento del prossimo prototipo continuo**.
È la modalità effettivamente provata: accelera anche gli altri attori e i
sistemi nativi, conservando i rapporti fra costi e velocità. Non interpretarla
come richiesta di quadruplicare soltanto la locomozione del giocatore.

Il default installato di RT-01 rimane 1×, selezionabile fino a 4× con F8;
questo aggiornamento registra la preferenza e non modifica i binari.
Restano da confrontare il controller continuo e il ritmo con combattimento,
posture e attività più complete prima di fissare il bilanciamento finale.
