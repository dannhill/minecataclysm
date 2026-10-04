# FND-04 — Connessioni verticali native

**Implementato con verifica mirata PASS e binari installati.** Task circoscritto
alle connessioni verticali e ai comandi salita/discesa. Sorgenti `7a72692`,
branch `fix/fnd04-vertical-navigation`; checksum, ambiente e risultati nel
[registro delle evidenze](fnd04-vertical-navigation-evidence.json).
L'utente [accetta i quattro test manuali e la transizione visiva](../source/vertical-validation-2026-10-04.md).
La salita/discesa automatica e continua di scale e scale a pioli sarà rivalutata
con l'utente quando il prototipo di tempo reale sarà giocabile. FND-04 completo,
SAVE-001 e M5.5 non sono certificati da questo passo.

## Comportamento

Le scale native hanno un ingresso a gradini; le scale a pioli hanno montanti
e traversi; gli ingressi verso il basso sono incassati nel pavimento. Sono
geometrie compatte di presentazione. Il cambio di piano rimane un'azione
contestuale CDDA, anziché una scala fisica di Luanti attraversabile liberamente.
Il futuro confronto del controller sceglierà l'attraversamento definitivo.

- **Salto** (predefinito Spazio): salita nativa, oppure risalita/emersione in acqua.
- **Furtivo + Salto** (Maiusc + Spazio): discesa nativa, oppure immersione.
- Un passaggio per pressione: tenere premuto non fa attraversare tutti i piani.
- L'indicazione contestuale compare sulla casella di collegamento. I comandi
  usano le azioni rimappabili dell'engine; nessun salto fisico o volo Luanti.

CDDA sceglie l'arrivo anche quando le due estremità delle scale non coincidono
in XY. La funzione `game::vertical_move` conserva costi, stamina, effetti,
followers, ostacoli, map shift e immersione. Immergersi/emergere alla superficie
può modificare soltanto lo stato sott'acqua, senza cambiare Z: è comportamento
nativo. Il client attende l'esito e lo stato autorevole prima di riprendere.

Arrampicata libera, selezione della direzione su bordi e controlli verticali
dei veicoli richiedono altri adattamenti e sono esplicitamente rifiutati qui.
Una corda CLIMBABLE non viene promossa artificialmente a GOES_UP. Rampe di
movimento nativo orizzontale e voli non fanno parte di questa verifica.

## Prova manuale

```bash
./vertical-demo.sh
```

La fixture è generata con il core CDDA pinned indipendente. Il comando crea
una copia sotto `artifacts/vertical-demo/session-*` e usa `start.sh` con i
binari installati. Non usa i salvataggi della partita normale. Rilanciare
riprende la stessa prova; `--fresh` crea un'altra copia conservando le precedenti.

Dal centro iniziale, con orientamento verso nord:

1. Scala davanti: raggiungila, premi Spazio, poi Maiusc + Spazio per tornare.
   Verifica riconoscibilità, cambio piano e assenza di blocchi/sfarfallio.
2. Scala verso sud: Maiusc + Spazio entra nella cantina; Spazio torna su.
3. Scala a pioli verso est: tieni Spazio premuto circa due secondi. Deve
   salire di un solo piano. Rilascia e ripremi per il piano successivo.
4. Esci su un piano diverso da zero e rilancia la demo: deve mantenere il piano
   e permettere il ritorno. Sui pavimenti ordinari Spazio non fa volare.

Facoltativo: due caselle a est c'è acqua profonda. Maiusc + Spazio immerge,
un'altra pressione scende nel volume; Spazio risale ed emerge. La resa buia
dell'acqua resta il problema di percezione già registrato, non un fix di questo task.
La scala otto caselle a est e una a nord prova l'arrivo nativo sfalsato.

I medesimi comandi funzionano nella partita normale tramite `./start.sh`.
Non serve ripetere le prove FND-03 già accettate. Le porte invertite di alcuni
edifici e il perno di un'anta doppia restano segnalazioni a priorità bassa.

## Riproduzione della fixture

Se gli artifact locali mancano, costruire il lettore di prova sul core pristine
pinned come descritto nell'audit, poi generare una directory nuova:

```bash
python3 tools/build_native_save_reader.py --pristine-cdda <core-pristine-compilato> \
  --workspace <sorgenti-ricostruiti> --output artifacts/fnd04-vertical/native-save-reader --strip-debug
artifacts/fnd04-vertical/native-save-reader --create-vertical \
  --userdir artifacts/fnd04-vertical/fixture-user --datadir <sorgenti-ricostruiti>/cdda/data \
  --output artifacts/fnd04-vertical/fixture-baseline.json
```

Non rigenerare sopra una directory di salvataggi esistente.

## Evidenze e limiti

- CDDA: 16 casi e 6.645 assertion pertinenti PASS. Il catalogo di terreno
  conserva GOES_UP/DOWN/DIFFICULT_Z; una corda CLIMBABLE non diventa una scala.
- Protocollo: quattro eseguibili PASS. Luanti: 304 test in 47 moduli e
  648 assertion in quattro casi Catch PASS.
- Runtime CDDA reale: 70 controlli PASS. Comprendono direzioni invalide senza
  costo, salita/discesa, immersione/emersione anche senza cambio Z, scala a
  pioli, arrivo sfalsato, replay dello stesso comando e reconnect. Il core
  pinned indipendente rilegge salvataggi a Z=-1 e Z=1.
- `start.sh` e client grafico reale: 17 controlli PASS. Camera ai piani
  positivi/negativi, tasto tenuto, pressione nuova, rimappatura, riavvio a Z=2,
  OPEN/CLOSE a Z=1 e persistenza canonica. Il picking supera anche il rebase
  nativo: target locale `(61,71,1)` corrisponde alla porta assoluta `(61,59,1)`.
  Screenshot della geometria e delle aperture ispezionati.
- Regressioni: 21 controlli di sessione, 42 acqua/aperture e 48 di
  movimento/camera PASS. Quelli di pacing usano autorità CWM sintetica e
  renderer reale; i limiti FPS 30/60/120 non garantiscono quel throughput.
- Demo installata: quattro controlli di startup/proiezione/isolamento PASS.

Build incrementali nel workspace ricostruito `artifacts/fnd03-session/workspace`,
aggiornato da Git e dai file catturati; **non cold-cache**. Tutti i 237 blob/modi
Git della radice e 20.189 file dei fork corrispondono alla sorgente della prova.
Una verifica indipendente riproduce le patch complete da file originali pinned
in directory temporanee e confronta tutti gli altri blob Git: include anche
i file esclusi da `git archive` tramite export-ignore. Non usa le working copy
modificate per costruire il risultato. Il lettore canonico è collegato al core
pristine pinned; soltanto il helper di prova viene ricompilato, senza sezioni debug.

L'archivio originale FND-03 resta in
`artifacts/fnd03-session/final-reconstruction.tar.gz`. I suoi due runtime
precedenti sono conservati e verificati negli archivi rollback sotto
`artifacts/fnd04-vertical/`; il workspace compilato ora contiene questo task.
Nessun mondo/configurazione della partita normale è usato o cancellato.

Durante lo sviluppo sono state corrette assunzioni dei harness: enum del wire
signed a 8 bit; corda nativa priva di GOES_UP; domanda d'acqua senza oggetti
vulnerabili; confronto del calendario dopo il prelude nativo. Quest'ultimo può
avanzare il calendario dopo lo stato di esito di un'azione: un heartbeat delimita
il punto di attesa stabile prima di misurare l'assenza di costo del replay.
I tentativi falliti restano negli artifact; non sono attestati come PASS.

Restano aperti controller/scheduler finali, arrampicata e rampe complete,
identità persistenti di tutte le entità, campi/HUD/luce locale/percezione,
panorama/nebbia e gli altri criteri di FND-04. La geometria delle connessioni è
provvisoria; nessuna nuova collisione o inferenza del client determina l'arrivo.

Il confronto pixel della porta certifica il cambio di geometria; la fixture
usa una porta isolata, senza muri adiacenti, che riceve l'orientamento
predefinito. Guardandola da est/ovest, l'anta aperta è frontale e quella chiusa
di taglio. È un limite dell'orientamento/presentazione della fixture, non una
verifica dell'allineamento di tutte le porte ai loro varchi. La segnalazione
sugli edifici di pietra resta senza una riproduzione identificata; controllare
le connessioni dei muri è una pista per l'audit futuro delle aperture.

Comandi delle prove mirate, con directory output nuove:

```bash
python3 tools/takeover_baseline.py check
python3 tools/verify_captured_sources.py --workspace <workspace> --receipt <output>/sources.json
cmake --build <workspace>/cdda/build --target cdda-server cata_test --parallel 1
cmake --build <workspace>/luanti/build --target luanti --parallel 1
python3 <workspace>/tests/vertical_runtime_test.py --workspace <workspace> \
  --fixture artifacts/fnd04-vertical/fixture-user \
  --native-reader artifacts/fnd04-vertical/native-save-reader --artifacts <output>/native
DISPLAY=:1 python3 <workspace>/tests/vertical_gui_test.py --workspace <workspace> \
  --fixture artifacts/fnd04-vertical/fixture-user \
  --native-reader artifacts/fnd04-vertical/native-save-reader --artifacts <output>/gui
```
