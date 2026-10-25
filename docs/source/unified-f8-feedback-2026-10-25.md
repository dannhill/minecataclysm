# Riscontro: avvio demo e unico controllo F8 — 2026-10-25

Fonte: messaggio diretto dell'unico sviluppatore umano; testo redatto da un
LLM sulle sue direttive. I risultati seguenti non sono test automatici.

- **FB-01.1 e FB-01.2 FAIL di avvio**: `./liquid-recovery-demo.sh --fresh`
  termina dopo «CDDA ready. Opening the CDDA Voxel presentation world».
  Le due prove sulle interfacce/recupero non sono state raggiunte.
- **FB-01.3 PASS funzionale**, ma il developer richiede di cambiare il design:
  niente secondo speedup del sonno moltiplicato per F8. Un'unica funzione F8,
  con valori più alti nel sonno e indicazione visiva distinta della modalità.
- **FB-01.4 PASS** per cielo notturno e pausa.

La build precedente era CWM2.35 (`a5114e8`). 61 PENDING meno i quattro punti
classificati =57 PENDING +2 FAIL di avvio. La successiva UF8-01.1 è una nuova
prova della revisione richiesta: **58 PENDING +2 FAIL di avvio** (60 non ancora
accettati). I FAIL originari rimangono fino al ricontrollo personale, anche
quando la correzione automatica passa. Il vecchio PASS 3 non accetta il nuovo
controllo F8 automaticamente.

## Causa dell'avvio, accertata dal codice

Il launcher della demo passava `--name liquid_recovery_demo`, lungo 20 byte.
Luanti pinned (`src/player.h`, `client/clientlauncher.cpp`) ammette al massimo
PLAYERNAME_SIZE-1, cioè 19 byte, e rifiuta il nome prima del gioco. I log
forniti mostrano il server nativo correttamente caricato, ma nessuna connessione
CWM del client. Il messaggio specifico del nome non compariva in quei log.

La correzione usa `recovery_demo`. I precedenti test del renderer avviavano
start.sh con `conversation_tester`: non provavano l'alias dello script pubblico.
La regressione ora esegue lo script pubblico senza sovrascriverne il nome,
con sessioni in uno spazio di verifica distinto dal last-session umano.

## Decisione approvata

F8 modifica una sola velocità assoluta del coordinatore CDDA. Il sonno/tentativo
 e l'attesa lunga usano la scala F8 ampliata; B resta un menu di riposo e
interruzione senza moltiplicatori o velocità indipendenti. Il cambio di contesto
mostra colore/etichetta distinti; al termine viene ripristinata la precedente
velocità da svegli. Tutti i turni/effetti/AI restano nativi; nessun salto del
calendario, nessuna attività riavviata da un cambio di velocità.
