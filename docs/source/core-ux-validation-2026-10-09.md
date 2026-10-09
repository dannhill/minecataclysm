# Validazioni e nuove richieste dopo UX-02 — 2026-10-09

Fonte: due messaggi dell'utente nella conversazione corrente, compresa
l'errata corrige successiva. Nessuna correzione di produzione viene attestata
da questo registro.

## Accettazioni e limiti

- Tiro/mira/ricarica: 1–4 PASS. Rinculo numerico osservato, feedback visivo
  ancora poco comprensibile.
- Quantità/deposito/contenitori posseduti: 1–4 PASS dichiarati. L'utente non
  è riuscito a depositare direttamente le munizioni contenute nel sacchetto:
  resta una verifica mirata di accessibilità, non un PASS di quel sottocaso.
- UX-01: tutti e quattro i test PASS. L'errata corrige sostituisce la dicitura
  ambigua «1 PASS 2 3 5» del messaggio precedente.
- UX-02: tutti e quattro i test PASS dichiarati. Morte, perdita/recupero IPC
  e schermate native non sono stati effettivamente provati/comprensi; non
  dedurre accettazione di quei sottocasi. Minacce/decisioni vengono mantenute
  nelle prove eccezionali separate, senza chiedere di rifare il flusso normale.
- I quattro ricontrolli mirati UI/mapping non hanno un nuovo PASS complessivo.
  L'acqua pulita ha un'icona errata; i tag negli hint restano visibili.

## Richieste autorizzate

- Hotbar HUD con icone corrette e indicatore dell'oggetto realmente impugnato;
  riferimenti assegnabili/rimuovibili, distinti dall'inventario completo.
  Rotella/numeri selezionano; azioni ed eventuale equipaggiamento pagano CDDA.
- Ricerca visibile fin dall'apertura ma senza focus: clic sinistro abilita
  digitazione e cambia colore; clic altrove toglie focus. Questa richiesta
  sostituisce il precedente default di ricerca nascosta su richiesta.
- Mira mantenendo il tasto destro, anche dopo un tiro; esplicitare la priorità
  con aperture, raccolta e uso degli oggetti. Nessuna mira gratuita in pausa.
- Fermare anche le nuvole in pausa. Presentare arma in mano e rinculo in modo
  leggibile; audio per tiro, ricarica e creature, senza simulazione parallela.
- Correggere sovrapposizione Quantità/frecce, tag colore negli hint e risposte
  native negative poco visibili («item is too big»).
- Correggere solamente la mappatura di `water_clean`, senza riscrivere il
  mapping generale. Distinguere mela marcia con un segnale grafico derivato
  dallo stato nativo, senza classificazione mediante nome localizzato.
- Verificare vestiti mancanti nella equipment-demo. Il save isolato originale
  contiene solo `backpack_hiking` tra gli indossati: pantaloni/maglietta/scarpe
  non sono nascosti dalla GUI in quella fixture. Rendere la demo più chiara.
- Riparare sagoma 2D verde in terza persona C, UV/texture dei personaggi e
  animazioni movimento/attacco/idle; conservare percezione e cronologia CDDA.
- Rendere più evidente l'operazione durante Indossa/Togli. I consulta e
  sospende il lavoro; chiudere I lo fa riprendere. Solo Interrompi cancella
  l'actor. Riaprire I manualmente scarta l'intenzione di ritorno automatico:
  comportamento corrente, da spiegare meglio nell'interfaccia.
- Prodotto in inglese per default; selezione lingua inglese / italiano (WIP).
  Localizzare coerentemente UI, testo nativo e nuove funzionalità; italiano
  incompleto con fallback esplicito. Non basta cambiare le etichette del menu.
- Ogni consegna deve essere disponibile anche attraverso `start.sh`, non
  soltanto nelle demo. Verificare il default continuo 4×: attualmente il
  launcher abilita `--continuous` solo con `CDDA_CONTINUOUS=1`.

## Priorità immediata

Prima di ripartire l'utente chiede recap, stime e prossimo passo. In questa
turnazione aggiornare registri/piano/backlog, senza presentare i difetti come
già corretti. Prossima fetta: UX-03 hotbar gestibile, con correzioni UI correlate,
icona acqua mirata e integrazione nel normale avvio. Lingua, mira, animazioni,
audio e robustezza rimangono task espliciti nella stima del core.
