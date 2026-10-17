# INT-01 — Riscontro manuale e gesti — 2026-10-18

Installato nel normale `start.sh`, CWM **2.23**, con copie della coppia precedente.
Il [riscontro](../source/manual-interaction-feedback-2026-10-18.md) accetta AIM1–3
ed EXT1–3; EXT4 resta FAIL soltanto per la raccolta differita dalla pausa.
Cinque nuovi PASS rispetto al backlog precedente. Stato corrente: **21 PENDING +
2 FAIL manuali**, lingua ed EXT4; tre nuove prove dei gesti rinviabili.
Nessun PASS personale dedotto dalle riparazioni automatiche.

## Modifiche

- RMB apre/chiude secondo l’ultimo stato CDDA della porta/finestra, senza Shift;
  un clic tenuto rimane una sola interazione e non diventa mira. Shift conserva
  l’accovacciamento. Range, stato, addebito e rifiuti restano nativi.
- Shift-clic trasferisce verso il pannello opposto nella vista esterna. Nella
  vista dei contenitori posseduti usa la destinazione selezionata; senza scelta
  mostra un motivo. Quantità selezionata rispettata, altrimenti pila intera.
- Trascinamento di un vero oggetto fuori dai bordi del menu: DROP ai piedi del
  personaggio tramite ACT_DROP, da inventario/trasferimenti/contenuti esterni.
  Esc durante drag annulla; sfondo interno annulla. Hotbar risolve l’istanza
  reale. Nessun inventario locale o concatenazione automatica di Togli/Travaso/
  furto: capacità, sigilli, tipo e proprietà continuano a limitare il gesto.
- Il clic di raccolta sfusa in pausa viene rifiutato subito; pause successive
  scartano selezioni non inviate. Riprendere non esegue un vecchio clic.
- Il deposito parziale di una pila esterna ora usa `item::split`: sposta la
  quantità richiesta e lascia il resto al suo posto, con identità rapida sul
  resto soltanto. Corretto il ramo nativo che sottraeva la quantità dalla copia
  e rimuoveva l’intera sorgente. Accesso e costo restano nell’actor nativo.

Il controllo di chiusura considera il corpo continuo, non solo la casella
centrale, sia all’ammissione sia all’esecuzione. Una chiusura che lo interseca
viene rifiutata senza spostarlo o addebitare mosse. Il renderer disabilita già
la fisica locale Luanti e l’anta aperta non ha collisione fisica. Questo prova
un percorso concreto di intrappolamento durante chiusura; **il caso riferito
aprendo la porta della struttura originale non è stato riprodotto esattamente**.
Rimane nel ricontrollo personale INT-01.1, senza dichiararlo risolto per deduzione.
[Design](../design/interaction-feedback.md).

Mira invariata: il rilascio termina nuovi passi di AIM; precisione già pagata
conservata secondo la policy nativa integrata. `ranged.cpp` distingue QUIT
dall’esplicito `action_drop_aim`, che imposta MAX_RECOIL. Collegare il rilascio
a quest’ultima cambierebbe il gameplay ed è ancora una decisione aperta.
Una futura animazione di arma abbassata può essere indipendente dal rinculo.

## Verifica e limiti

183 casi CDDA / **186.099 assert**, 309 test Luanti / 47 moduli più 648 assert
Catch in 4 casi; 11 test del protocollo. Build incrementali da copie ricostruite
con inventari verificati, non cold clean build. Renderer Luanti reale con input
xdotool su Xvfb/Mesa privato, relay byte-trasparente e fixture/save isolati;
lettore indipendente del core CDDA pinned. Ricevuta con comandi, source identity,
hash dei runtime installati/rollback, conteggi grafici e artifact:
[interaction-feedback-evidence.json](interaction-feedback-evidence.json).

Controlli grafici: RMB senza Shift, postura/pausa/reconnect; Shift-clic con
quantità fra pannelli e in un contenitore posseduto; drop esterno e contenitore
carico; nessuna raccolta sfusa al resume, nuovo clic valido; rifiuti di capacità,
interruzione, fonti sigillate/vuote, recupero e salvataggi. Le prove canonicali
conservano 50 munizioni nella scena esterna e 30 in quella dei contenitori
posseduti, le identità degli oggetti e le quantità annidate esatte.

Conservati i tentativi falliti: argomento Catch `--rng-seed42` scritto male;
nuova fixture porta senza peer IPC, quindi rifiutata da Recovery; secondo clic
sulla finestra durante il debounce di 200ms; pitch rivolto in alto; lettura del
vecchio target cliccato invece del nuovo hover; sasso conteggiato usato per
provare il percorso sfuso; clic prima dell’installazione della formspec ritornata;
reset del relay durante SIGTERM scambiato per errore vivo. Corretti fixture e
harness, preservando recovery, debounce, controlli di rete durante il gioco,
assert su costi/quantità/risultati e rifiuti; nessun vecchio FAIL conta come PASS.
La ricevuta precedente UX-05 corregge soltanto la spaziatura del comando seed.

[Checklist rinviabile](../validation/pending-manual.md). Mapping batch60 invariato;
nessun salvataggio personale usato. Full SAVE-001 OPEN; M5.5 storico FAILED.
Segue il consolidamento core e il debito rig/UV/animazioni/audio previsto.
