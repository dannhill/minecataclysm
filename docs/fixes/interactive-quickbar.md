# UX-03 — Hotbar interattiva e ritocchi mirati

Consegna del 2026-10-09, CWM **2.17**. Accettazione grafica dell'utente
**PENDING**, separata dalle verifiche automatiche. M5.5 resta storico FAILED;
SAVE-001 completo resta OPEN. **Riscontro successivo:** Ricontrolli UX-03
1–3 PASS; hotbar 1 FAIL ergonomico, 2–4 non provati. La richiesta
[drag-and-drop completo](../design/inventory-drag-and-drop.md) sostituirà il
flusso Assegna/Svuota; non è ancora implementata. Il contatore 14 sotto e le
ricevute descrivono la consegna, il backlog attuale ha 11 elementi aperti.
Identità sorgenti, binari, comandi, ambiente e
ricevute: [evidenze esatte](interactive-quickbar-evidence.json).

## Comportamento disponibile

In I: scegli un oggetto nella griglia, uno dei nove slot inferiori e
**Assegna allo slot N**. **Svuota slot** elimina solo il riferimento.
I nove slot non sono nuove tasche e non copiano i primi nove oggetti della
lista. Non cambiano capacità, contenuti o oggetto in mano. Assegnazione e
rimozione non fanno avanzare il tempo nativo.

Fuori da I: rotella/1–9 selezionano; **G** richiede l'azione nativa pertinente.
Per indossati: Togli; altrimenti la prima azione disponibile fra Mangia/Bevi,
Indossa, Medica, Impugna, Riponi, Togli. I conserva i pulsanti espliciti per
scegliere un'azione diversa. G è riconfigurabile nelle impostazioni.
L'accesso alle tasche, decisioni sulla destinazione, rischi del consumo e
costi/attività restano CDDA. Un'operazione dalla hotbar non forza I a riaprirsi.
Pausa/lavoro in corso non accodano G per una ripresa successiva.

Lo slot selezionato è oro; il vero oggetto in mano è azzurro e compare anche
nel riquadro separato a destra quando non è assegnato. Icone HUD e I hanno
lo stesso mapping/fallback di categoria. Non viene introdotto un modello 3D
dell'arma o degli abiti reali da questa modifica.

Ricerca visibile all'apertura, senza catturare la tastiera: clic per scrivere,
clic altrove per uscire dal campo; Esc lascia prima un campo focalizzato,
poi chiude I. Il focus modifica il colore del testo. Quantità ha un'etichetta
separata dalle frecce pagina; gli errori nativi restano in una fascia evidente.
I suggerimenti contestuali rimuovono tag colore terminali, conservando il testo.
Il lavoro Indossa/Togli include il nome dell'oggetto quando disponibile.

`water_clean` usa una piccola override locale con la goccia già presente nel
progetto; i **27 batch generati non sono modificati**. Il deterioramento
esportato nativamente aggiunge fondo colorato/segno `!` all'icona, anche negli
slot rapidi. La decorazione della griglia è sotto il pulsante, così l'oggetto
marcio resta selezionabile. Le nuvole usano il clock visivo già condiviso da
acqua e oggetti: non avanzano durante la pausa autorevole.

`./start.sh` avvia normalmente il continuo **4×** accettato. Per confronti:
`CDDA_CONTINUOUS=0 ./start.sh` seleziona il ciclo comandato dalle azioni;
`CDDA_REALTIME=1 ./start.sh` conserva il vecchio prototipo a griglia scandita.
Launcher demo/driver storici dichiarano esplicitamente la modalità voluta.
La verifica usa esclusivamente copie isolate, mai i mondi personali.

## Identità, costi e persistenza

`Hotbar` nel core risolve soltanto istanze davvero possedute. Un token opaco
univoco di 32 caratteri esadecimali usa la sorgente d'identità CWM, senza
consumare RNG gameplay. Avatar `values` e item `item_vars` nativi conservano
rispettivamente slot/token come metadati opzionali. Nessun campo obbligatorio
nuovo, cache Luanti o ID effimero di query entra nella persistenza autorevole.
Il reader CDDA di riferimento conserva quei campi e conferma contenuti/ruoli.

Wield/wear possono copiare/spostare oggetti nativi: il token segue l'istanza.
Il key UI è ignorato dal controllo di stacking integrato. Lo split mantiene
il token sulla porzione originale e lo toglie da quella nuova. Se un merge
consuma l'istanza referenziata, il riferimento può invalidarsi; non si sceglie
un'altra pila per tipo/nome. Perdita, consumo, proprietà ambigua o scansione
incompleta invalidano il collegamento; riacquisire non lo ricrea.
Questo non certifica tutti i casi SAVE-001 né identica logica di restacking
nel gioco upstream, che non conosce la nuova chiave UI riservata.

Binding: vista/oggetto correnti e token precedente atteso impediscono che
un vecchio comando sovrascriva una nuova assegnazione. Use: slot/token esatti
sono rivalidati sia all'ammissione sia all'esecuzione. Le sei azioni usano gli
stessi rami nativi dell'inventario; `InventoryWorkState` distingue il primo
risultato dal completamento pagato. Ledger limita duplicazioni/replay. La scansione posseduti è limitata a
8.192 voci e non viene fatta quando tutti gli slot sono vuoti; la baseline
prestazionale dei grandi inventari resta nel task di performance dedicato.
Il client processa selezione prima di G nello stesso fotogramma; i numeri
rimangono riservati alle decisioni native quando una decisione è aperta.

## Verifica e limiti

Build incrementali dopo refresh completo delle sorgenti ricostruite; non
una nuova clean build/conformance gate. Protocollo 10/10; native suite
171 casi e 185.788 asserzioni; client 308 test più 648 asserzioni/4 casi.
**77 controlli sul binario finale** (consumo e hotbar/save/reload installati),
più **97** sulla stessa logica prima della sola correzione dello strato
decorativo: la ricevuta distingue hash e fasi.
Prove Xvfb nel renderer reale: assegnazione/rimozione, focus, selezione vs
mano, costi/scelte, pausa/no replay, riconnessione, reload delle identità;
regressioni azioni consecutive, consumo e trasferimenti, incluse quantità
parziali annidate/rifiuti nativi. Letture indipendenti dei save completano
le ricevute, senza sostituire l'accettazione estetica dell'utente.

Le prove hanno trovato e corretto autofocus iniziale, tooltip con separatore
formspec non escapato e decorazione marcio che bloccava i clic. Due test
nativi iniziali confondevano rock charge-merge con due istanze: fixture
corretta con due cappelli non fusi, mantenendo gli assert sull'identità.
Tentativi falliti e motivi restano distinti dalle ricevute finali.

Coppia precedente conservata in `artifacts/ux03-quickbar-20261009/`;
la ricevuta d'installazione registra entrambi i vecchi e nuovi hash.
[Prove manuali rinviabili](../validation/pending-manual.md): **14 PENDING**,
senza chiedere di ripetere i PASS precedenti. L'estetica pausa nuvole richiede
ancora osservazione manuale con nuvole abilitate; i driver di queste prove
usano cielo senza nuvole per evitare rumore visivo.

Rimangono inglese predefinito/italiano WIP, RMB mantenuto per mira, arma
visibile/rinculo, rig/UV/animazioni/audio, dialoghi ricchi, recenti crafting,
raggruppamento anatomico e continuità della selezione tra query. Contenitori
esterni/raccolta quantitativa restano la prossima estensione essenziale
all'inventario. Nessun PASS viene attribuito a queste parti.
