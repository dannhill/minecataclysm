# UX-05 — Scorciatoie native del crafting — 2026-10-14

Nel normale `start.sh`, K aggiunge All, Favorites, Recent e Unfinished.
La prima scheda segue il contesto CDDA: lavori incompleti accessibili, ricette
recenti note, preferite note, altrimenti catalogo. Ricerca e lotti restano
applicabili; i filtri precedono il limite di 256 risultati.

Un preferito della ricetta è metadata UI nativo, distinto dal preferito di
un componente fisico. Aggiungi/Rimuovi conserva il menu e attende la risposta
autorevole; non paga mosse, avvia attività né modifica la cronologia. Il comando
verifica identità, conoscenza/accesso e stato atteso, con la deduplicazione
ordinaria CWM. Le ultime 20 ricette avviate e i preferiti persistono nel normale
`uistate.json` CDDA, condiviso dai personaggi di quel mondo. Nessun nuovo campo
nel save del personaggio o inventario Luanti. “Più eseguite” resta separato:
i recenti nativi registrano avvii, non completamenti.

La ripresa verifica requisiti rimanenti, non richiede di nuovo i componenti
iniziali già consumati e non riconosce errori dal testo italiano. Fonti, utensili,
ingredienti protetti, conferma, costo e actor ACT_CRAFT restano CDDA.
[Design e limiti](../design/recipe-shortcuts.md), [protocollo 2.22](../../protocol/PROTOCOL.md).

Il nuovo test ha rilevato estrazioni casuali nella conoscenza dei preferiti.
Le fonti reali native mantengono accesso/proprietà/libri/helper senza generare
acqua o nuovi pseudo-utensili; la raccolta normale dei materiali conserva il
default. `item::select_itype_variant` evita estrazioni con liste vuote: la
selezione di varianti reali è invariata, ma la sequenza casuale successiva cambia
intenzionalmente eliminando quei draw. Nessun rollback RNG o override del seed.
Il test invarianti controlla mosse, calendario, RNG, actor e recenti, compresi
replay, view scaduta, stato atteso errato e ricetta dimenticata. Non certifica
ogni preview legacy che usa la cache dei materiali.

## Verifica e limiti

181 test CDDA / 186,030 assert; 309 test Luanti / 47 moduli più
648 assert Catch in 4 casi; 11 test del protocollo. Nel renderer finale:
42 controlli su runtime ricostruito, 42 sul percorso
installato e 14 dopo il riavvio: tutti PASS.

Build incrementali su sorgenti ricostruiti, non clean build. Renderer reale
Luanti in Xvfb/Mesa, input xdotool, relay IPC trasparente, fixture/save isolati
e lettore indipendente del core CDDA pinned. Controlli su preferiti gratuiti,
cronologia da avvio approvato, annullamento, lotto, pausa/interruzione/ripresa,
nessun movimento/avvio differito, riconnessione, risultati esattamente una volta,
componenti protetti e save canonico. Il successivo riavvio del percorso
installato verifica preferiti/recenti effettivamente salvati. Runtimes accoppiati
con copie di rollback; identità e hash nella
[ricevuta](recipe-shortcuts-evidence.json).

Conservati i fallimenti iniziali: loader JSON della fixture; mismatch tra tipi
string/translation delle schede client; consumo RNG nel controllo preferiti;
lettura parziale del JSON nativo senza dichiarare i membri volutamente omessi;
un refresh rifiutato per documentazione non ancora committata, seguito da un
vecchio binario nel comando diagnostico. Quest’ultimo non conta come prova del
fix. Tracing temporaneo rimosso. Fixture/harness corretti senza sopprimere assert
su costi, RNG, annullamento, risultati o persistence; le prove preliminari non
sostituiscono la verifica del runtime finale.

Backlog **24 PENDING + 1 FAIL manuale**: quattro nuove prove UX-05 rinviabili,
20 precedenti e FAIL lingua conservati; nessun PASS personale dedotto dai test
automatici. [Checklist](../validation/pending-manual.md). Nessun obbligo oggi.
Segue consolidamento core e debito visivo rig/UV/animazioni/audio. Frequenza,
sottoricette, risultati liquidi/gassosi/sottoprodotti e pratica restano follow-up.
Full SAVE-001 OPEN; M5.5 storico FAILED. Nessuna promozione del gate complessivo.
