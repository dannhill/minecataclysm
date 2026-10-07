# Ripresa della continuazione locale

Fonte: `Continuare_implementazione_RT02.txt`, fornito dall'utente il
2026-10-07 nella radice del progetto. Il file originale resta sul disco;
questa nota conserva le decisioni operative senza riscrivere il piano.
SHA-256 del file: `5022c72913193c6f075b464687289350e76b8bb1a968c30acfb1185dabbb51fc`.
L'indice recuperato è in `artifacts/conversation-recovery-20261007/index.json`.

- Messaggio utente 230, riga 15355: accettazione del test RT-02 dopo le
  correzioni del movimento/rebase; un microfreeze durante nuova esplorazione
  non impedisce la validazione per gli obiettivi del prototipo.
- Messaggio 339, riga 16999: dare precedenza al playable core rispetto ai
  veicoli. La priorità è già incorporata in `IMPLEMENTATION_PLAN.md`.
- Messaggi 379/381, righe 17626/17678: item singolo flottante e rotante,
  nessuna raccolta automatica; pile accessibili dalla GUI chest/container
  Mineclonia, azioni native CDDA e tempo fermo durante la selezione.
- Messaggio 581: per le pile è ammessa la presentazione iniziale con due o
  tre wielditem. Non serve attendere un nuovo modello di pila.
- Messaggi 689/738: mapping incrementale indipendente dallo sviluppo del
  gameplay. Solo i batch di produzione vengono importati; il fallback deve
  permettere di continuare senza completare la mappatura.
- Ultimi messaggi 754–756: CWM 2.4 introduce i guard della selezione PICKUP;
  il backend deve conservarli nella coda, rivalidarli all'esecuzione e
  assegnare `Character::pick_up()` con quantità zero, cioè l'intero stack.
  Il costruttore esplicito di `Command` era già presente alla ripresa.

La ripresa prosegue da questo ultimo passo. Non riapre le scelte del
controller né anticipa i veicoli. La validazione dell'interfaccia degli
oggetti rimane distinta dai test del backend. M5.5 resta il gate storico
FAILED, non viene ricertificato da questa continuazione.
