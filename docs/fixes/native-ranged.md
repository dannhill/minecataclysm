# Tiro, mira e ricarica nativi — prima fetta

Da provare quando disponibile: `./ranged-demo.sh --fresh`. Scena isolata con
Glock già impugnata, tre colpi e munizioni nello zaino; zombie davanti e cane
amico a destra. E riconosce la minaccia iniziale. F mantenuto mira, clic
sinistro spara una volta, R ricarica. I consente pausa e interruzione; F7
resta pausa manuale. Rilascia F prima di sparare: gli input occupati non
accodano colpi per il futuro. Disponibile anche nella partita normale con
un'arma da fuoco impugnata.

Il bersaglio è l'identità della creatura ostile realmente percepita. Il client
non invia posizione, portata, danni, colpi rimasti né una dichiarazione di hit.
Il raggio di puntamento usa la portata nativa dell'arma, con limite di
traversal alla bolla e intersezione con gli ostacoli visuali: la portata della
mano Luanti non restringe più il tiro. CDDA rivalida arma, modalità, bersaglio, portata, percezione, disponibilità
nativa, attività e pausa all'ammissione e prima dell'esecuzione. La modalità
balistica corrente determina tiro singolo/raffica e costi. Tenere il mouse
non genera altri comandi; mira tenuta campiona soltanto dopo l'esito e stato
autorevoli del passo precedente. Le armi non balistiche non diventano melee
per errore quando la modalità cambia.

La penalità di rotazione e la riduzione di rinculo sono estratte dalle
funzioni native usate dal target UI; ogni miglioramento paga move credit.
Il suggerimento espone rinculo nativo, non una probabilità di colpire inventata.
Tra comandi real time la mira già pagata resta mantenuta finché arma/bersaglio
sono validi: consuma credito di attesa senza migliorare il rinculo. Movimento,
altre azioni e recovery terminano questo mantenimento. Il generic WAIT nativo
invece azzera la mira; usarlo qui rendeva impossibile sparare dopo aver mirato.
Il tiro usa fire_gun: dispersione, proiettile, terreno/creature intercettate,
danni, inceppamenti, calore, cariche, skill e tempo restano nativi.

La verifica nel renderer ha esposto una ricorsione nel pin originale:
rebuild_aim_cache → calc_steadiness → sees → cant_see → rebuild_aim_cache.
La cache viene resa non ricorsiva durante la valutazione della percezione
fisica e poi sostituita dal cono finale; il bersaglio assoluto viene convertito
in coordinate locali prima della steadiness. Il test controlla bersaglio
visibile e visione lontana dietro il giocatore ancora ristretta. Dopo mira e
tiro il cache dirty viene aggiornato. Il core pristine del lettore di save
rimane originale: la riparazione non modifica formato o serializzazione.

R usa reload_wielded, list_ammo e reload_option nativi. Il selettore esterno
mostra solo munizioni accessibili tramite tasche CONTAINER non sigillate,
con quantità/costi nativi; conserva alternative e Annulla. Munizioni di tipo
diverso possono essere escluse dalla lista con un caricatore già parzialmente
carico: è il vincolo nativo, non un filtro cosmetico. Conferma esplicita prima
di ACT_RELOAD. Il lavoro e il trasferimento finale appartengono all'attore
canonico, con riferimenti a arma/caricatore e munizioni reali. Annullamento
prima dell'avvio e interruzione durante il lavoro non trasferiscono cariche;
nessun rimborso del tempo già speso. Salvataggio/caricamento continua il lavoro
nativo residuo. I progressi ricarica/consumo/medicazioni/craft sono esclusivi.

CWM 2.14 appende le nuove strutture e conserva le vecchie numerazioni.
Handle dell'arma effimeri, rinnovati al cambio item/modalità e al reconnect;
la cancellazione richiede token e ACT_RELOAD corretti. Ledger e snapshot
proteggono da ritrasmissione e comandi durante pausa/attività. Progresso e
stato dell'arma malformati richiedono resync; nessuna inferenza del client.

## Limiti e prossime fette

Mira assistita su ostili percepiti e armi da fuoco impugnate. Mirino libero
configurabile resta previsto nella prima versione completa; tiro deliberato
su neutrali, arco/carica-e-spara, armi montate/veicoli, cambio modalità e
ricarica di oggetti non impugnati sono successivi. Il selettore usa la quantità
nativa proposta, senza slider parziale in questa fetta. L'ACT_AIM terminale
non è portato integralmente: mantenimento e token CWM sono effimeri, non
nuovi campi di save. Rig/modelli dell'arma, tracce/suoni/animazioni e feedback
balistico completo richiedono un passaggio di presentazione separato.

Le quattro prove manuali sono PENDING nel backlog abituale, ora 20 punti.
La verifica automatizzata non equivale all'accettazione dell'utente. M5.5
resta storico FAILED; SAVE-001 e conformance completi rimangono aperti.

## Verifica mirata e riproduzione

PASS: CDDA 86.045 asserzioni / 107 casi (CWM, acqua/pickup/crafting, ricariche
native, copertura balistica e accuratezza di tiratori competenti/esperti);
Luanti 308 test e 648 asserzioni Catch2 / 4 casi; protocollo 8/8.

Renderer reale: gui-range 31, gui-installed 31, gui-installed-resume 11, gui-ordinary 24, crafting-regression 25, medicine-regression 33, equipment-regression 29 verifiche PASS per esecuzione; 184 occorrenze complessive.
Il lettore del core pristine conferma un solo gun, munizioni 33 iniziali
meno un colpo sparato = 32, variante/incompatibili intatte e posizione
canonica invariata. Il save attivo contiene ACT_RELOAD/attore/riferimenti
item_location nativi e lavoro residuo; il renderer installato lo completa
senza nuova richiesta, caricatore a 15 e fonte a 17. I token non sono campi
di salvataggio. Le schermate catturate sono state ispezionate per arma/rinculo,
scelta munizioni e Interrompi ricarica; restano placeholder e debug già pianificati.

Sorgenti ricostruite da pin/patch/inventari, compilazione incrementale con
cache conservate. Identità runtime, commit di produzione, lettore pristine,
comandi e checksum di log/save/screenshot: [evidenza completa](native-ranged-evidence.json).
Gli eseguibili precedenti 2.13 sono conservati in artifacts/native-ranged-20261008
come rollback; i due installati coincidono con i binari ricostruiti verificati.

Riproduci `python3 tools/takeover_baseline.py check`, refresh/replay delle
sorgenti con gli script tools e ricevute del report, build esplicito dei tre
componenti; i comandi esatti delle sette sessioni GUI e dei test nativi sono
nel JSON. Servono X11 :1, xdotool/ImageMagick/Pillow e le fixture isolate
generate dal lettore native-save-reader: `--create-ranged` per questa demo.
La ricevuta reader-build.json conserva i tre argv di compilazione/link/strip
contro il core originale; non si usa una suite Python come prova del renderer.

I tentativi iniziali falliti e lo stack del crash sono conservati negli
artifacts; non vengono conteggiati come PASS. La correzione è verificata dalle
sole esecuzioni riuscite elencate sopra. Le copie dei save di test restano
isolate e nessun mondo dell'utente è stato usato o modificato.
