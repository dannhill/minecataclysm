# FND-04 — Connessioni verticali native

Task circoscritto alle connessioni verticali e ai comandi salita/discesa.
Verifica in corso; questo documento verrà completato con sorgenti e risultati.
FND-04 completo, SAVE-001 e M5.5 restano separati.

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
