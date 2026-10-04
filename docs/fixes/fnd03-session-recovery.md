# FND-03 — Sessioni e recupero coerente

**Implementato con verifica mirata PASS.** CDDA e Luanti richiedono CWM 2.0;
`start.sh` e gli alias compilati usano i nuovi eseguibili verificati. Un comando
duplicato ha un solo effetto. Una sequenza incompleta o uno stato invalido
blocca l'input e richiede uno snapshot autorevole prima di riprendere.

Sorgenti della verifica: commit `74b7a40`, branch `fix/fnd03-session-recovery`.
I pin, patch complete e inventari dei fork sono in `baseline/manifest.json`;
checksum, ambiente, comandi, risultati e binari installati sono nel
[registro delle evidenze](fnd03-session-recovery-evidence.json).

Aggiornamento successivo: il [task verticale FND-04](fnd04-vertical-navigation.md)
riusa il workspace compilato di questo task e installa nuovi runtime. Per
riprodurre esattamente FND-03 usare il commit sopra e l'archivio originale
`artifacts/fnd03-session/final-reconstruction.tar.gz`; i runtime FND-03 sono
conservati con checksum negli archivi rollback di `artifacts/fnd04-vertical/`.
I log e gli esiti FND-03 restano evidenza storica, non una nuova certificazione.

## Contratto implementato

Prima di Hello compatibile il server non invia gameplay e non esegue comandi.
La versione incompatibile riceve un rifiuto seguito dalla chiusura. Hello
accettato assegna sessione del runtime, identità del personaggio canonico e
identità della connessione. Il client conserva la propria identità tra i
riavvii del collegamento. Nessun fallback permissivo verso CWM 1.

WorldReset precede lo stato iniziale completo. Solo l'ACK dello snapshot
installato permette al server di accettare input; anche Luanti verifica la
propria readiness. Ogni messaggio successivo deve avere identità corrette e
sequenza contigua nella propria direzione. Le sequenze contano messaggi
accodati, indipendentemente dai turni o dalle revisioni del mondo.

WorldSnapshot distingue full e batch incrementale, specificando revisione
base, ID dello stato, correlazione del resync e comando completato. Il client
verifica struttura semantica e revisione prima di modificare la proiezione.
Terreno e roster completi di attori/veicoli sono applicati sul thread principale;
il mutex della proiezione copre l'intero batch rispetto ai worker delle mesh.
Un full elimina gli elementi assenti. Spawn/despawn sono incorporati nel batch;
non esistono aggiornamenti autonomi che aggirino la readiness.

Una perdita, inversione o incoerenza ferma i nuovi comandi. Il client conserva
l'ultimo stato fidato, scarta la coda non affidabile e chiede un singolo resync
correlato. Il reset corrispondente stabilisce una nuova barriera di sequenza;
lo stato completo seguente deve corrispondere alla richiesta. Dopo l'installazione
si invia SnapshotAck. Il prompt nativo ancora pendente viene riproposto dopo
questa conferma sulla stessa connessione. Se il trasporto cade senza una
risposta valida, resta la scelta sicura nativa.

Il registro CDDA contiene al massimo 1.024 comandi, con ID monotono per
sessione/personaggio, autore e firma della richiesta. Un duplicato pendente
non entra due volte in coda. Uno completato restituisce l'esito e la revisione
originali insieme a uno stato completo attuale. Una firma/autore diversa per
lo stesso ID chiude il peer; un ID vecchio evinto viene rifiutato e mai
rieseguito. I comandi non eseguiti cancellati alla disconnessione conservano
un risultato negativo. Un'azione nativa già iniziata può terminare e registra
l'esito anche se il client è andato via.

Dopo reconnect nessun comando incerto viene ritentato automaticamente. La
sessione nuova invalida le identità precedenti e azzera cache, oggetti visivi
e origine della scena. I salvataggi rimangono esclusivamente CDDA e non
contengono il registro di protocollo. Il comportamento comandato dalle azioni
resta quello transitorio previsto dal piano; questo task non implementa lo scheduler.

CwmTransport/CwmListener e framing non dipendono da POSIX. I runtime usano
l'interfaccia; Unix rimane il backend di produzione. Un backend in memoria
verifica lo stesso controller di sessione. Socket privati 0600, directory 0700,
assenza di fallback condivisi e mancato unlink di socket altrui evitano due
supervisori concorrenti. Launcher e coordinator eseguono il solo `start.sh`.
Il [contratto completo](../../protocol/PROTOCOL.md) conserva limiti e semantica EOF.

## Verifica e riproduzione

Build da sorgenti ricostruiti in `artifacts/fnd03-session/workspace`, con riuso
incrementale di oggetti FND-02 soltanto se flag e tutte le dipendenze coincidono.
**Non sono build cold-cache.** Gli inventari dei fork e il contenuto/modo Git
della radice vengono ricontrollati dopo gli aggiornamenti finali. Una seconda
ricostruzione dal commit del report è archiviata in
`artifacts/fnd03-session/final-reconstruction.tar.gz`: 20.189 file dei fork
ricontrollati dopo la compressione; checksum nel registro. La copia espansa
temporanea è rimossa per contenere il consumo di disco. I mondi di
prova sono copie isolate; nessun salvataggio utente è usato o eliminato.
Il lettore dei salvataggi è collegato al core CDDA pinned indipendente.

- Protocollo: quattro eseguibili PASS; 15 casi sessione e 13 casi trasporto
  anche con ASan/UBSan. Inclusi gap, riordino, revisione base errata, full
  malformato, cache limitata e conservazione del socket di un altro supervisore.
- CDDA reale: 21 controlli di sessione e 29 di peer avversi PASS. Negoziazione,
  comando pre-ACK, duplicato pendente/completato/dopo reconnect, firma in
  conflitto, ID vecchi e persistenza dopo riavvio verificati.
- Luanti reale: 21 controlli PASS su frammentazione, gap, full incompleto,
  input tenuto durante recupero, rimozione di attori/veicoli, nuova sessione,
  EOF, errori e flusso di dati. Nessun avanzamento della revisione dai heartbeat.
  Durante il flusso: 13 frame, intervallo massimo circa 19,7 ms, massimo letto
  256 KiB per aggiornamento.
- Test nativi pertinenti: 15 casi/3.584 assertion PASS. Luanti: 304 test in
  47 moduli e 648 assertion in quattro casi Catch PASS.
- Regressioni: 48 controlli input/camera, 15 rebase, 42 acqua/aperture,
  40 lifecycle delle decisioni native e 21 su `start.sh` con GUI reale PASS.
  Il core indipendente conferma posizione, effetti sugli oggetti e stato
  delle finestre nei casi provati. Sei controlli sugli alias del supervisore PASS.

Comandi principali dalla radice; utilizzare directory output nuove:

```bash
python3 tools/takeover_baseline.py check
python3 tools/takeover_baseline.py reconstruct --destination <workspace-nuovo>
cmake --build <workspace>/cdda/build --target cdda-server cata_test --parallel 1
cmake --build <workspace>/luanti/build --target luanti --parallel 1
ctest --test-dir <workspace>/protocol/build --output-on-failure
python3 tests/session_runtime_test.py --workspace <workspace> \
  --fixture artifacts/exploration-fix/fixture-user --artifacts <output-nuovo>
DISPLAY=:1 python3 tests/transport_gui_test.py --workspace <workspace> \
  --artifacts <output-nuovo>
python3 tests/exploration_runtime_test.py --workspace <workspace> \
  --fixture artifacts/exploration-fix/fixture-user \
  --native-reader artifacts/exploration-fix/native-save-reader --artifacts <output-nuovo>
```

## Limiti e prossimo passo

**M5.5 storico resta FAILED; SAVE-001 completo resta incompleto.** Le prove
mirate non certificano l'intera simulazione o tutti i payload futuri. I probe
storici CWM 1 rimangono evidenza del takeover; i casi indirizzati sono verificati
con fixture CWM 2, senza indebolire le condizioni per accettare gameplay.
La saturazione delle code è testata a livello trasporto; il vecchio flusso di
Hello ripetuti è ora, correttamente, una violazione di sessione.

Rimangono FND-04/05: registry persistente completo delle entità, ID dei veicoli
ancora legati al runtime, copertura dei campi, validazione semantica/range completa,
large-coordinate policy, luce/percezione, verticalità, HUD e verifica threading
più ampia. I componenti placeholder dei veicoli sono aggiornati dal roster e
non costituiscono M6; riuso delle scene/benchmark popolati restano da completare.
I budget I/O non limitano il tempo massimo di ingestione di un full molto grande.

Il prossimo passo di fondazione è completare FND-04 mantenendo le validazioni
manuali accettate. Tempo reale, ergonomia dell'apertura, oscurità/immersione,
nebbia e panorama ricordato restano nelle fasi previste. Il rilievo rimane
rinviato secondo la decisione dell'utente. Nessuna nuova scelta grafica è
finalizzata da questo intervento.
