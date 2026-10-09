# Riscontro inventario, correzioni e mapping — 2026-10-09

L'utente accetta **16 punti manuali**: inventario/equipaggiamento, consumo,
medicazioni e crafting, tutti 1–4 PASS. Tiro/ricarica e quantità/contenitori
restano pendenti. Nuovi ricontrolli solo per le correzioni: **12 punti** totali
nel [backlog](../validation/pending-manual.md), senza chiedere test oggi.

## Correzioni consegnate

- DecisionPrompt: il bridge rimuove tag terminali `<color_...>`/`</color>` da
  testo e scelte, conservando simboli `++`, caratteri Unicode e parentesi
  letterali. Il nome dello zaino è leggibile nella scelta Riponi.
- Crafting: badge R inset nel riquadro; clic seleziona la ricetta, senza
  avviare il lavoro. Il relativo test usa il pulsante Riprendi per l'azione.
- Recupero: CDDA può rifiutare silenziosamente un pickup senza spazio nelle
  tasche. Per una raccolta manuale l'UI esterna ora spiega il rifiuto e offre
  **Wield/Cancel** se il core permette l'impugnatura. La scelta usa lo stesso
  ramo nativo del pickup problematico: validazione, eventuale gestione della
  mano occupata, costi e rimozione dell'originale rimangono CDDA.
  Annullare conserva l'oggetto; lo zaino recuperato conserva i contenuti.
  Auto-pickup non propone scelte né equipaggia autonomamente.
- Con spazio disponibile continua la raccolta nativa ordinaria, senza popup
  aggiuntivi. Il messaggio di selezione non equivaleva a raccolta completata.
  La segnalazione dell'utente non è riprodotta in ogni variante del suo save:
  la causa verificata/fissata è il rifiuto per capacità, non ogni possibile
  problema di raccolta.

Lo zaino impugnato rimane posseduto, così come i contenuti: devono comparire
nella vista unificata con la sorgente reale. Non è un bug. “Leggere” nelle
checklist significava consultare I/H, non leggere libri; testo corretto.

CWM rimane **2.15**, nessun cambiamento di schema o regole di salvataggio.
I runtime ricostruiti sono installati nella coppia usata da `start.sh`;
backup dei precedenti in `artifacts/inventory-feedback-20261009`.

## Mapping e piano UI

[Importati tutti i 27 batch di produzione](item-mapping-2026-10-09.md): 1.080
record, 396 rappresentazioni supportate, 89 texture con fonte/hash e licenze.
105 associazioni con asset non supportato e 579 senza match restano fallback.
Le varianti procedurali raccomandate non sono realizzate da questo import.
Il renderer mostra i nuovi proxy nelle ricette, senza modificare gli oggetti
nativi. Input/output Sol originali sono conservati.

Il [piano basato sui sorgenti](../design/inventory-and-native-dialogs.md)
propone UX-01 (layout Mineclonia 9×3, ricerca opzionale, dettagli/strati), poi
UX-02 (azioni consecutive pagando i costi e tornando alla stessa vista),
conferme visive/medicina, ricette recenti/preferite/frequenti e hotbar
interattiva. Il layout attuale rimane provvisorio: queste revisioni **non**
sono già implementate o approvate esteticamente. Il clic sinistro ha una
preferenza opzionale pendente; la proposta di base seleziona, le scorciatoie
agiscono. La scelta della rotella non equivale a impugnatura gratuita.

## Evidenza mirata

Identità, hash, ambiente, log, installazione e proiezioni native indipendenti
sono nel [registro](inventory-feedback-evidence.json). Sorgenti production:
`8001dea`, `1e145d3`; test e fixture aggiornati in `2b5ed40`; mapping `1817918`.
Harness per display isolato/focus/DPI e progresso in `a0d058c`, `be05b00`,
`f52c6dd`. Le copie ricostruite conservano i pin e patch integrali del baseline.

- Native: **8.576 assert / 65 casi**, tag `[cwm],[pickup]`, seed 42. Inclusi
  recupero con scelta/cancel, zaino pieno e sette munizioni conservate,
  costi pagati e auto-pickup che non cambia equipaggiamento.
- Luanti: **308 test / 47 moduli**, più **648 assert / 4 casi**.
- Protocollo: **9/9**. Nessuna nuova versione richiesta per le modifiche.
- **112 controlli in 6 sessioni del renderer reale**: recupero senza tasche
  (anche runtime installati), equipaggiamento/scelte native, crafting/badge,
  crafting con la registry nuova e raccolta con tasche disponibili anche
  nella modalità ordinaria. Salvataggi riletti dal core CDDA originale.
- Ultime due sessioni su Xvfb con OpenGL/llvmpipe, senza interferire col
  desktop. Posizioni del mouse ricavate dal frame effettivamente renderizzato,
  non da una supposizione sul DPI. Nessuna sostituzione del client con stub.
- Registry: 396 definizioni/riferimenti univoci, nessun callback gameplay;
  27 output validati, 89 asset confrontati con upstream, sync idempotente.

Esempi di comandi (dalla ricostruzione dove indicato):

```sh
# cwd artifacts/fnd03-session/workspace
cmake --build cdda/build --target cdda-server cata_test -j3
cmake --build luanti/build -j3
ctest --test-dir build/protocol --output-on-failure
# cwd .../cdda; usare un user-dir isolato
build/tests/cata_test '[cwm],[pickup]' --rng-seed 42 --user-dir=<isolato>
# cwd .../luanti
bin/luanti --run-unittests
```

Comandi completi dei due renderer isolati nel receipt locale
`delivery-isolated-renderer-runs.json`; fixture create dal lettore nativo
indipendente, comprese `--create-recovery`, `--create-transfer` e crafting.
Receipts di refresh/replay, build, screenshot, trace e wire in
`artifacts/inventory-feedback-20261009`.

Tentativi esplorativi falliti conservati ed esclusi dal PASS: fixture con
spazio disponibile erroneamente usata per attendere un popup; callback di
test senza credito iniziale; focus desktop perso; clic sintetici con DPI
errato; lettura del progresso nell'istante di ammissione prima del primo tick.
Il rifiuto del vecchio runtime senza tasche è una riproduzione negativa
attesa, con oggetto a terra e nessuna decisione, non una verifica positiva.
M5.5 storico rimane FAILED; SAVE-001 completo OPEN.
