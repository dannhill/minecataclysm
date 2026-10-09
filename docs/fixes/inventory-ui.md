# UX-01 — Inventario con layout Mineclonia

Fetta di presentazione del 2026-10-09, richiesta con «Continua al prossimo
passo». La griglia usa il linguaggio visivo di Mineclonia; oggetti, capacità,
costi, attività e salvataggio restano CDDA. CWM rimane **2.15**.

## Comportamento consegnato

**I**: mano realmente impugnata evidenziata, sagoma di riferimento, tutti gli
indossati in un elenco paginato; griglia **9×3** con conteggio/pagine e fila
inferiore **9×1** distinta. I riquadri sono viste di identità native, non
slot Luanti né capacità aggiuntiva. L'elenco conserva anche i contenuti dei
contenitori impugnati; provenienza indica radice indossata/in mano, contenitore
e tasca. Icone ripetute in mano/indossati/griglia/barra selezionano lo stesso
oggetto, senza creare copie. Non c'è ancora switch rapido.

Ricerca nascosta all'apertura, anche se si conserva la ricerca applicata:
**Cerca...** apre e mette a fuoco il campo, Cerca/Invio applica; **Esc** lascia
la ricerca senza chiudere I o rilasciare la pausa. Un secondo Esc chiude.
Filtri Tutti/Equipaggiati/Contenitori. Pagina, filtro e ricerca restano nella
sessione; nuove query e reconnect azzerano la selezione, senza indovinare
l'identità tra oggetti omonimi. Aggiorna limita la pagina al risultato nuovo.

Scheda breve con nome, ruolo, categoria, quantità, massa/volume e provenienza.
**Tasche e dettagli...** espande costi, lunghezza, tasche e contenuti nel pannello
scorrevole; ogni tasca mostra capacità residue native, senza sommare una seconda
volta i figli al peso del contenitore. Il riepilogo totale arriva direttamente
da CDDA. Azioni disponibili come pulsanti; indisponibili grigie con motivo
nativo al passaggio del mouse. Un semplice clic sulle icone seleziona.

Mapping/proxy dei 27 batch invariato. Quando manca la rappresentazione,
immagini di categoria da asset già estratti; categorie sconosciute mostrano
`?`. Tooltip dichiarano categoria/segnaposto oppure mapping che può essere
proxy. Il nome CDDA rimane leggibile: un'icona di spada per WEAPONS non
trasforma una mazza in spada. Nessuna nuova texture o meccanica Mineclonia.

La scena dell'anteprima GUI esclude la nebbia del mondo e assegna una
texture trasparente al secondo materiale Armor del modello, che prima
copriva la pelle con una sagoma grigia. La camera e la nebbia del mondo
non cambiano. L'anteprima è statica durante la consultazione.

## Confini della fetta e seguito

UX-01 non è accettato graficamente dall'utente: quattro prove nuove nel
[backlog](../validation/pending-manual.md), totale **16 PENDING**. Non richieste
oggi e non bloccano il seguito autorizzato. Le vecchie checklist PASS attestano
le precedenti meccaniche, non questo layout.

Il protocollo attuale non esporta coperture/impedimento dei singoli vestiti.
Gli indossati sono tutti accessibili, ma non ancora raggruppati per parte
anatomica; la sagoma non rappresenta l'abbigliamento reale. Serve un export
semantico tipizzato, riusabile con medicina/corpo. Non dedurre coperture dal
nome degli oggetti. Questo requisito resta nel piano UX-01.

Identità stabile tra azioni e scorciatoie configurabili sugli oggetti restano
nelle fette successive; non riusare ID numerici di una vista precedente.
Il menu continua a chiudersi per eseguire un'azione con i tempi nativi.
**Prossimo task UX-02**: ritorno automatico alla consultazione solo dopo il
pagamento effettivo dell'azione, rispettando minacce, decisioni, morte, pausa
manuale e reconnect. Hotbar interattiva, conferme tipizzate e cronologia ricette
seguono il [piano UI](../design/inventory-and-native-dialogs.md).

## Verifica riproducibile

Fonte ed esatti risultati nel [receipt](inventory-ui-evidence.json).
**PASS**: Luanti 308 test / 47 moduli, più 648 asserzioni Catch2 / 4 casi;
ricostruzione indipendente delle sorgenti; 206 controlli in sette sessioni
GUI con ricarica dei save nel core pristine. Di questi, **112 in quattro
sessioni** usano l'hash del binario finale (paging, tiro, trasferimenti e
intera regressione equipaggiamento dopo installazione); 94 in tre sessioni
precedenti verificano equipaggiamento/consumo/medicina prima degli ultimi
ritocchi grafici. Il receipt distingue sorgenti e hash senza presentarli
come un'unica suite del binario finale.

Binario Luanti installato: `c04505366583fb7075a426eb01ea4e4fecd0e8a5e534624976bba2c7267cf1c9`.
CDDA resta `bf1898dbd1ec43072506962c46cb575443583a9d95fcc861d6cc308add7721d8`.
Rollback Luanti: `artifacts/ux01-inventory-20261009/luanti-previous-runtime`.
[Anteprima dal runtime installato](../../artifacts/ux01-inventory-20261009/equipment-installed/inventory.png).
Artefatti locali: `artifacts/ux01-inventory-20261009/`.
Ricostruzione incrementale con cache, non clean build fredda. Pin CDDA/Luanti/
Mineclonia invariati; cattura completa in `baseline/manifest.json`.

```
python3 tools/takeover_baseline.py check
python3 tools/refresh_verification_workspace.py \
  --workspace artifacts/fnd03-session/workspace \
  --receipt artifacts/ux01-inventory-20261009/refresh-provenance.json
# Nella workspace ricostruita, DOPO il completamento del refresh:
cmake --build luanti/build -j3
# Dalla sua directory luanti:
bin/luanti --run-unittests
```

GUI reale su display Xvfb privati 1280×800, Mesa/llvmpipe, input xdotool,
wire relay trasparente e screenshot. Porte esplicite diverse per ogni scena;
nessun salvataggio/configurazione dell'utente. Driver in `tests/`, wrapper
`run-gui.py` nell'artefatto. La fixture di paging è prodotta dal core CDDA
pristine con `tests/takeover_save_reader.cpp --create-inventory-pages`:
52 oggetti e 12 indossati; gli 11 strati di bandana sono una predisposizione
debug, non un aggiramento del comando Indossa. Compilazione/link del reader
contro core originale nel receipt `reader-build.json`. Ricarica nativa dopo
ogni sessione per verificare quantità, contenuti, arma e vestiti canonicali.

Le prove coprono apertura/ricerca/Esc, filtri/pagine, molteplici indossati,
consultazione senza comandi né avanzamento, native azioni e invalidazione su
reconnect. Test positivi separati dai tentativi preliminari conservati:
conflitto di porta dei primi due test simultanei, firma errata nella sola
fixture, membro materiale GUI non supportato intercettato dal compilatore,
coordinata obsoleta del pulsante Annulla nel driver trasferimenti,
e build sovrapposta a un refresh. Quest'ultima è stata esclusa e
sostituita da build dopo refresh completo con verifica delle stringhe/asset
e della resa effettiva del nuovo binario. Nessuno di questi tentativi vale
come PASS della versione finale.

M5.5 resta **FAILED** storico; SAVE-001 completo **OPEN**. Il controllo dei
save di queste fixture non ricertifica l'intero progetto.
