# Inventario, hotbar e dialoghi nativi — proposta di attuazione

Riscontro: [16 PASS e richieste del 2026-10-09](../source/inventory-ui-feedback-2026-10-09.md).
Stato: **pianificato**, salvo le tre correzioni mirate documentate separatamente.
L'interfaccia attuale non è la versione definitiva. Nessuna approvazione
estetica della nuova proposta viene dedotta dai PASS delle meccaniche.

## Studio dei sorgenti e vincoli effettivi

| Sorgente letto | Comportamento riscontrato | Conseguenza per la UI |
|---|---|---|
| `mineclonia/mods/HUD/mcl_inventory/survival.lua`, `build_page` e `main_page_static` | Inventario 9×3, hotbar 9×1, silhouette/armatura, tasca secondaria e guida; slot e sfondo condivisi. | Riutilizzare proporzioni, asset, slot e gerarchia visiva familiari. |
| `luanti/src/cdda/equipment_inventory.h`, `equipmentForm`/`transferForm` | Griglia 6×6, ricerca sempre visibile, textarea con tutto il dettaglio; fonti/tasche native già disponibili. | Separare informazioni essenziali, dettagli avanzati e gestione tasche; ricerca chiusa per default. |
| `cdda/src/cwm/cwm_inventory.h`, `InventorySelection` | Identità effimere, antenati, ruolo indossato/impugnato e accesso rivalidati; tutti i contenuti posseduti sono visitati. | Una borsa in mano non nasconde i contenuti. Mostrare il percorso reale; la griglia non crea capacità. |
| `luanti/src/cdda/cdda_bridge.cpp`, `equipmentInventoryFields`/`flush_equipment` | L'azione chiude I e attende la rimozione di MENU_OPEN prima dell'esecuzione nativa. | Tenere semplicemente la finestra modale aperta bloccherebbe il lavoro. Serve uno stato di esecuzione distinto dalla consultazione. |
| `luanti/src/client/game.cpp`, aggiornamento CWM; `gui/guiFormSpecMenu.cpp`, eventi mouse/tastiera | Il conteggio dei menu governa MENU_OPEN. Le liste native Luanti generano IMoveAction; i pulsanti immagine inviano campi formspec. | Scorciatoie CWM richiedono un percorso esplicito per l'identità sotto il mouse. Non riattivare i trasferimenti autorevoli Mineclonia. |
| `cdda/src/pickup.cpp`, `pick_one_up` | Se non entra nelle tasche, il pickup può terminare senza raccolta. | Spiegare il rifiuto; eventuale impugnatura è una scelta esplicita con validazione/costi nativi. |
| `cdda/src/cwm/cwm_server.cpp`, `ask_decision`; `do_turn` provider esterno | Decisioni temporaneamente rappresentate da testo/scelte numerate; world e input sospesi, annullamento finale sicuro. | Nuova veste grafica senza approvazioni automatiche. Metadati tipizzati per scelte mediche/oggetti, senza dedurre gameplay dal testo. |
| `cdda/src/recipe_dictionary.cpp`, `recipe_subset::recent`/`favorite`; `craft_command.cpp` | Recenti/preferiti nativi esistono; il comando registra fino a 20 ricette recenti dopo l'avvio del lavoro, non dopo la sola ricerca. | Esporre prima Recenti/Preferiti. Per “più eseguiti” definire conteggio dei completamenti, non delle aperture o dei tentativi. |

La prova del renderer con i precedenti nove batch mostrava molte icone identiche: il fallback attuale
`game/mods/cdda_items/textures/cdda_items_fallback.png` è una texture grigia
di pietra, non un simbolo neutro di oggetto sconosciuto. Il mapping generato di quella versione
non conteneva mazza/zaino/benda della fixture; nei log viene effettivamente
caricato `cdda_items:fallback_generic`. UX-01 deve distinguere almeno categorie
con asset appropriati, conservando nomi e fallback espliciti. Non è stato
riscontrato un nuovo errore di caricamento delle texture in queste prove.
La successiva sincronizzazione richiesta dall’utente importa i 27 batch
attuali: 1.080 record e 396 rappresentazioni attive. La benda improvvisata
ora usa il proxy di cuoio del batch; le modifiche procedurali raccomandate
non sono applicate da questo import. Zaino e mazza restano fallback per
assenza di match/asset supportato, rispettivamente.

Mineclonia contribuisce il linguaggio grafico, non la sua simulazione: non
si importano crafting 2×2, inventario a capacità fissa, drag-and-drop locale,
armature limitate a un pezzo per slot o equipaggiamento senza costo.

## UX-01 — Inventario familiare e dettagli progressivi (prossimo passo)

- Finestra compatta: personaggio/equipaggiamento in alto, griglia **9×3** in
  basso, fila rapida **9×1** distinta. Asset di slot/sfondo già disponibili.
  Oltre 27 oggetti: frecce/pagine, indicatore del totale e categoria. I 27
  riquadri sono una pagina, non un limite di possesso.
- Ricerca nascosta dietro lente/Cerca: clic apre e mette a fuoco il campo;
  Esc prima lascia la ricerca e poi chiude I. Nessun focus tastiera rubato
  all'apertura. Filtri compatti: Tutti, Equipaggiati, Contenitori.
- Slot della mano chiaramente evidenziato con l'oggetto **davvero impugnato**.
  Vestiti per zona del corpo, con conteggio e apertura degli strati multipli;
  niente falsa equivalenza “testa = un solo casco”.
- Verificare il mapping delle icone CDDA agli asset estratti: distinguere
  icone reali, placeholder di categoria e fallback generico, con nomi sempre
  disponibili. Non presentare un cubo generico come modello definitivo.
- Selezione apre una scheda breve: icona/nome, quantità, ruolo, sorgente,
  massa/volume e azioni consentite. Stato con colore e simbolo + testo,
  mai solo colore. Dettagli espandibili per lunghezza, costo d'accesso,
  impedimento e tasche; unità leggibili, testo tecnico non nella vista base.
- Contenitori: riepilogo spazio/peso utilizzati, poi espansione di tasche e
  contenuti. Non duplicare contenitori e figli negli aggregati; né far
  credere che due icone equivalgano a due copie dello stesso oggetto.
- Conservare pagina/filtro/ricerca/selezione tra azioni; al cambio di vista
  rivalidare l'identità. Non riutilizzare ID di vecchia query/reconnect.
- Scorciatoie indicate nel tooltip e riconfigurabili. Preferenza sul clic
  sinistro chiesta all'utente: selezione + azioni esplicite oppure toggle
  impugna/riponi. “Impugna” e “Indossa” restano distinguibili; consumare e
  depositare non sono effetti di un clic esplorativo.

Verifica: inventario oltre una pagina, zaino indossato/impugnato/depositato,
strati multipli, oggetti annidati, identità invalidata, tooltip/ricerca/focus,
nessuna mutazione o avanzamento del tempo per la sola consultazione.
Serve prova grafica dell'utente alla consegna; gli attuali 16 PASS non la coprono.

## UX-02 — Azioni consecutive con costi reali

Flusso proposto: **consulta in pausa → conferma una sola azione → pannello
compatto non modale durante il lavoro → ritorno alla stessa vista al termine**.
Il mondo e le creature avanzano mentre si indossa, ripone, mangia o trasferisce.
Non serve ripremere I per la successiva azione; nessun batch invisibile.

Il pannello durante il lavoro mostra operazione, progresso quando esiste e
interruzione. Esc permette di tornare al mondo senza riapertura automatica;
I apre una consultazione e mette in pausa come oggi. Minaccia, decisione,
morte, disconnessione e pausa manuale hanno precedenza sulla riapertura.
Annullare la scelta prima dell'avvio non consuma l'oggetto; interrompere
conserva i costi già pagati secondo l'actor nativo.

Condizione tecnica: per azioni brevi senza ACT_* non basta il primo ACK.
Verificare la fase in cui il costo/debito nativo è davvero processato; esporre
un segnale semantico di completamento se necessario. Riapplicare MENU_OPEN
prima di quel punto congelerebbe il debito e renderebbe il cambio abusabile.
Una GUI modale mantenuta aperta senza questo adattamento fermerebbe l'actor.

Verifica: più azioni successive, costo/calendario nativo, minaccia durante
lavoro, cancel, reconnect, uscita e save/load. Non aggiungere ritardi inventati
alla modalità scandita dalle azioni solo per ottenere un'animazione.

## UX-03 — Hotbar interattiva

Nove riferimenti rapidi, non nove nuove tasche. Rotella/numeri selezionano
un riferimento; **selezione grafica** e **oggetto impugnato** hanno indicatori
diversi. Selezionare non altera CDDA. L'azione pertinente (Impugna, Usa,
Mangia/Bevi, Indossa, Riponi) invia il comando nativo e paga l'accesso reale.

Possibile equip automatico su cambio slot è un'opzione da confrontare, non
un cambio istantaneo: una sola intenzione, niente coda di cambi durante il
lavoro. Non assegnare il clic destro contemporaneamente a consumare e aprire
una porta senza una priorità esplicita. Pulsante/shortcut di uso riconfigurabile
prima del confronto. I riferimenti si invalidano quando l'oggetto è perso,
consumato o depositato; non riassegnare silenziosamente a un oggetto omonimo.
Per persistenti assegnazioni servono identificatori canonici o metadati UI
separati e validati al load: gli ID CWM della vista non sono persistenti.

Verifica: selezione contro mano reale, consumabili/vestiti/arma, perdita del
riferimento, costi, busy/pause, nessun replay, salvataggio e riconnessione.

## UX-04 — Conferme visive, poi scheda medica

Componente coerente con inventario: titolo corto, icona, motivo, effetti
conoscibili, pulsanti espliciti Conferma/Annulla, scorrimento e focus sicuro.
Rischi importanti (cibo marcio, danni agli oggetti in acqua, parti ferite,
componenti protetti) rimangono decisioni native; scelte ordinarie ridondanti
possono essere raggruppate solo conservando esattamente le decisioni del core.
Le scelte numerate restano shortcut, non l'unico sistema di input.

Adattare prima Yes/No e destinazioni d'oggetti, poi medicina: sagoma/icone di
parti del corpo, cuori proporzionali alla salute osservabile, benefici/rischi
conoscibili, selezione esplicita della parte. Utilizzare lo stato nativo
strutturato collegato alla decisione: non analizzare le barrette ASCII per
inventare HP o possibilità di trattamento. Annullamento sicuro, nessun auto-OK
al timeout/disconnect e nessuna cura mentre si consulta la scheda.

Le sole rimozioni dei tag colore consegnate adesso **non** costituiscono
questa revisione dei dialoghi, né sostituiscono i futuri colori semantici.

## UX-05 — Ricette recenti, preferite e frequenti

K apre prima Lavori incompleti / Recenti / Preferiti, oltre al catalogo;
ricerca opzionale. Riutilizzare i 20 recenti nativi e i preferiti, filtrando
sempre per conoscenza/ammissibilità attuale. Ricetta recente non significa
attualmente eseguibile: mostrare materiali mancanti e luce/strumenti.

“Più eseguiti” deve contare i completamenti effettivi una volta ciascuno,
separare ripresa da nuovo lavoro e chiarire lotto vs numero di oggetti.
Definire persistenza compatibile o metadati UI separati prima di aggiungere
il contatore; non imporre campi obbligatori al salvataggio CDDA canonico.
I recenti nativi sono ricette avviate; non etichettarli come completamenti.

Verifica: niente conteggi per ricerca/annullamento, riprese e load non
raddoppiano il risultato, ricetta diventata indisponibile resta spiegata.

## Sequenza successiva e backlog

1. Correzioni mirate → ricontrolli nel backlog, nessun test obbligatorio oggi.
2. UX-01, poi UX-02: leggibilità e azioni consecutive prima di aggiungere
   altra complessità all'inventario attuale.
3. UX-04 con UI medica e UX-05; UX-03 come fetta nativa distinta con i costi
   verificati, dopo stabilità della gestione delle azioni.
4. Contenitori esterni vicini e raccolta con quantità selezionate restano
   essenziali, usando poi questi componenti. La roadmap M6/M7 e le fondazioni
   non vengono sostituite da un progetto separato di UI.

Per ogni fetta consegnata aggiungere solo le nuove prove necessarie a
[validazioni manuali](../validation/pending-manual.md), mantenendo separati
PASS precedenti, evidenza automatica e nuove scelte estetiche ancora da provare.
