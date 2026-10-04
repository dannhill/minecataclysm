# Validazione manuale delle connessioni verticali — 2026-10-04

Fonte: riscontro dell'utente nella conversazione Codex dopo il task
[FND-04 sulle connessioni verticali](../fixes/fnd04-vertical-navigation.md),
sorgenti `7a72692` e report `d9aef42`. L'utente dichiara di aver eseguito
tutti e quattro i test proposti nella demo e che funzionano egregiamente.
Il riscontro non contiene un checksum dei binari o l'identificativo della
sessione; questi riferimenti identificano la consegna associata.

Sono accettati:

1. Salita e discesa sulla scala, con collegamento fra piani riconoscibile e
   transizione visiva soddisfacente.
2. Discesa in cantina e ritorno.
3. Scala a pioli: un solo piano tenendo premuto il comando; una nuova
   pressione permette il passaggio successivo.
4. Uscita e riavvio su un piano diverso da zero, mantenimento del piano e
   possibilità di ritorno, secondo la checklist consegnata.

Queste prove bastano per accettare il passo circoscritto; non occorre
ripeterle o aggiungere altre prove manuali prima di proporre il seguito.
Il riscontro non aggiunge una verifica manuale dell'acqua o della scala
con arrivo sfalsato, che erano facoltative. FND-04 completo, SAVE-001 e il
gate M5.5 conservano gli esiti e i limiti già documentati.

## Promemoria per il prototipo in tempo reale

La transizione attuale è accettata come soluzione provvisoria. L'utente
preferirebbe che scale a gradini e scale a pioli si percorressero in modo
automatico e continuo nel gioco in tempo reale, e chiede di riparlarne
dopo l'implementazione di quel motore.

Quando il primo prototipo di scheduler in tempo reale sarà giocabile,
ricordare esplicitamente all'utente questa preferenza e includere scale
a gradini e a pioli nella prova, prima di scegliere il controller definitivo.
Confrontare la soluzione attuale con l'attraversamento continuo/automatico;
la preferenza non finalizza ora un nuovo comportamento. Costi, tempo,
stamina, legalità e destinazione restano autorevoli in CDDA.

## Seguito proposto

Raccomandazione: completare un passo FND-04 dedicato all'identità e al ciclo
di vita delle creature/NPC, verificando movimento, cambio origine/piano,
uscita e rientro nell'area, morte/rimozione, riconnessione e caricamento
canonico. Serve una base affidabile per il successivo prototipo di tempo
reale; non include ora dialoghi, commercio o animazioni complete.

L'utente chiede la proposta e deciderà poi se continuare. Questo riscontro
registra l'accettazione della consegna e il promemoria; non avvia il prossimo
task di implementazione.
