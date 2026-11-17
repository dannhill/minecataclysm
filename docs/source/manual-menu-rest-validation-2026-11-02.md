# Riscontro umano: menu e F8 — 2026-11-02

Fonte: messaggio diretto dell’unico sviluppatore umano; documento scritto da
un LLM sulle sue direttive, non risultato di test automatici.

La corrispondenza col giro di quattro prove proposto è:
1 → MENU-01.1; 2 → UF8-01.1; 3 → LIQ-01.3; 4 → SEAL-01.4.

- **MENU-01.1 PASS con segnalazione separata:** durante makeshift bandage K non
  mette in pausa; I e il pulsante Pause and inspect invece funzionano.
- **UF8-01.1 PASS funzionale con segnalazione separata:** una prova del sonno ha
  mostrato un messaggio riferito alla sincronizzazione CDDA. B non apriva più
  il riposo, mentre minimappa V e rotazione del mouse funzionavano. Un’altra
  prova non ha riprodotto il difetto. Testo preciso e determinismo non noti.
- LIQ-01.3 e SEAL-01.4 rimangono PENDING: il developer li farà in seguito.

Il PASS F8 copre i controlli proposti; non attribuisce una nuova validazione
save/load del sonno, che rimane nel già pendente REST-01.4. I PASS precedenti
sono conservati. 59 PENDING meno due =57; due ricontrolli delle correzioni,
KEY-K-01.1 e SYNC-01.1, riportano il totale a59 PENDING, senza trasformare i
PASS funzionali del developer in FAIL. I difetti K/SYNC restano distinti.

## Evidenza e limiti dell’indagine

Il percorso modale di lavoro gestiva I, F7 e F8 ma non la scorciatoia configurata
del crafting: K veniva intercettato dalla finestra senza aprire la consultazione.

Nei log della demo sonno `artifacts/runtime/20261102T150356Z-684359/cdda.log`
compare una chiusura trasporto di tipo6 (IoError); il salvataggio finale riesce.
Questo non identifica la causa iniziale né dimostra da solo che sia proprio
l’episodio descritto. I log precedenti del client non registravano il motivo
preciso del rifiuto di una proiezione o lo stato al momento della disconnessione.

L’implementazione aveva inoltre un rischio riproducibile di recupero infinito:
le transizioni Syncing/Resyncing azzeravano il timeout, anche senza installare
un mondo valido. Timer basati su dtime si fermavano nel menu pausa del motore.
Il nuovo watchdog usa tempo monotono reale, completa il tentativo solo su uno
stato autorevole installato e ritenta la connessione, senza inferire stato o
ripetere il comando di sonno. La regressione inietta risincronizzazioni invalide
mentre il menu pausa è aperto, poi consente un nuovo collegamento valido.
Questa correzione e la nuova diagnostica non provano la causa originaria rara.

Il working tree contieneva numerosi refactor locali precedenti al riscontro.
Le verifiche acquisiscono una fotografia Git privata di quel contenuto, senza
committare/pubblicare quei cambiamenti al posto del developer e senza usare i
suoi salvataggi di gioco. Le evidenze identificano fotografia, patch e binari.

Le correzioni locali e le prove automatiche successive sono descritte nella
[consegna del 2026-11-02](../fixes/manual-feedback-2026-11-02.md). Non costituiscono
un nuovo PASS umano per KEY-K-01.1 o SYNC-01.1.
