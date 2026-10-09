# UX-03D — Inventario con drag-and-drop completo

Stato: **IMPLEMENTED / accettazione manuale PENDING**, CWM **2.18**.
Successivo al [FAIL ergonomico UX-03](../source/ux03-drag-feedback-2026-10-09.md),
rimuove Assegna/Svuota e copre griglia, hotbar, mano, indossati, contenitori
posseduti e Terra; conserva la raccolta già consegnata. Entrambi i runtime
sono installati per il normale start.sh. [Report ed evidenze](../fixes/inventory-drag-and-drop.md).
Lingua/mira seguono questa consegna; non vengono implicitamente incluse.

## Base letta prima della revisione

| Sorgente | Situazione attuale | Conseguenza |
|---|---|---|
| `luanti/src/cdda/equipment_inventory.h`, `equipmentForm` | Mano, indossati, griglia e hotbar sono image/item buttons; Assegna/Svuota inviano campi formspec. | Servono sorgenti/destinazioni di drag per ciascuna sezione, senza perdere clic di selezione e dettaglio. |
| Stesso file, `transferForm` | Oggetti a sinistra, contenitori di destinazione come righe/pulsanti, quantità separata, Deposita/Trasferisci. | Le righe dei contenitori devono essere destinazioni di rilascio; integrare quantità e area Terra nel gesto. |
| `luanti/src/gui/guiFormSpecMenu.cpp` | Trascinamento nativo sulle liste genera IMoveAction e include logica locale di pile/swap. | Riutilizzare il gesto/feedback visivo, instradando il caso CWM verso comandi semantici, senza applicare mutazioni Luanti al gameplay. |
| `luanti/src/cdda/cdda_bridge.cpp`, `populate_mirror`/`container_form` | Raccolta già usa liste specchio; owned items e sorgenti a terra vengono pubblicati dal core. | Conservare il pickup funzionante; non confondere indice della lista specchio, ID di query e identità persistente. |
| Stesso file, `equipmentInventoryFields`/`flush_equipment` | EquipmentRequest/ItemTransferRequest vengono eseguiti dopo la chiusura della consultazione; UX-02 aspetta il costo pagato prima di riaprire. | Il rilascio sostituisce la scelta a pulsanti, non il modello di tempo e lavoro. |
| `cdda/src/cwm/cwm_inventory.h`, `action_error`/`validate_transfer` | Capacità, antenati, quantità, cicli, posizione e sigilli sono rivalidati; non tutte le sorgenti consentono ogni trasferimento. | Feedback di ammissibilità e rifiuti nativi; niente takeoff/unseal impliciti per far funzionare un gesto. |
| `cdda/src/cwm/cwm_hotbar.h`, `bind`/`resolve` | Identità persistente per un oggetto preciso e confronto del precedente binding; un bind sposta il riferimento, non esegue uno swap atomico fra due slot. | Riutilizzare l'identità; per swap di due riferimenti serve un'operazione atomica con entrambe le aspettative, non due comandi indipendenti. |

## Gesti e significato delle destinazioni

| Sorgente → destinazione | Risultato previsto |
|---|---|
| Griglia → hotbar | Assegnare l'oggetto preciso allo slot senza equipaggiare o cambiare tasca. |
| Hotbar → griglia | Rimuovere il collegamento, conservando l'oggetto e il suo ruolo fisico. |
| Hotbar → altro slot rapido | Spostamento; se entrambi occupati, scambio atomico dei due riferimenti. |
| Griglia/hotbar → mano | Richiesta Impugna con accesso, scelta nativa sulla mano occupata e costi CDDA. |
| Oggetto → zona Indossati | Richiesta Indossa quando nativamente disponibile; mantenere tutti gli strati, senza un falso limite a una maglia/casco. |
| Mano/indossato → griglia | Riponi/Togli nativo; la destinazione grafica non garantisce spazio fisico e non sopprime una scelta nativa necessaria. |
| Oggetto → icona/riga di contenitore | ItemTransferRequest INSERT con istanza e quantità; il core sceglie una tasca valida. Mostrare il percorso effettivo. |
| Oggetto → area esplicita Terra | ItemTransferRequest DROP alla posizione nativa del personaggio; distinguere dal solo svuotamento di un riferimento rapido. |
| Terra → inventario | Pickup nativo già esistente; quantità selezionata richiede estensione dedicata dove il contratto corrente non la supporta. |
| Griglia → spazio vuoto della griglia | Disposizione visiva, senza dichiarare che l'oggetto è stato spostato in una tasca CDDA diversa. |

La hotbar è una parte della disposizione principale: un oggetto assegnato
non deve occupare anche un secondo slot nella griglia principale. Mano e
indossati descrivono ruoli reali, con riferimenti riconoscibili alla stessa
istanza. La vista avanzata delle sorgenti resta completa, inclusi contenuti
annidati: non nasconderli quando una borsa è impugnata.

La disposizione ora persiste come `item_vars.cwm_inventory_position` sulla
reale istanza CDDA: query effimere non vengono salvate. I ranghi interi 1–2048
sono compatti; un drop su oggetto non contenitore inserisce prima, uno su
spazio vuoto sposta alla fine. Non si salvano buchi o coordinate di caselle.
Wield/wear/copie native conservano il metadato; lo stacking integrato lo ignora
e lo split lo mantiene solo sulla porzione originale. Identità/tasche reali
vengono verificate prima di aggiornare tutti i ranghi. Due oggetti omonimi
mantengono ordini distinti; un cambio di nome/tipo non è una ricerca d'identità.
Il reader nativo indipendente e il reload reale verificano la continuità.

## Interazione e validazioni

- Clic breve seleziona/apre dettagli; movimento oltre una soglia avvia il
  drag. Icona al cursore e evidenziazione della destinazione valida/invalida,
  con motivo testuale quando disponibile. Decorazioni non intercettano clic.
- Rilascio su zona senza azione, fuori dal menu o Esc durante drag annulla
  il gesto. Nessun deposito accidentale trascinando fuori dalla finestra.
- Per pile: trascinamento normale dell'intera quantità disponibile;
  selezione esplicita della quantità parziale prima dell'invio, riusando la
  funzione nativa già presente. Conservare accesso a quantità precisa senza
  supporre stack_max o frazionamenti arbitrari Mineclonia.
- Quando necessario Togli prima di un trasferimento, presentare il motivo
  e consentire i due gesti espliciti, pagando entrambe le azioni. Non
  concatenare attività nascoste per soddisfare una destinazione.
- Trascinare su se stessi non fa nulla; cicli, sigilli, liquidi/travasi e
  capacità seguono i limiti nativi. Il drag non implementa da solo sigilli,
  tasche manuali o contenitori esterni ancora assenti.
- Il gesto conserva sessione, vista, istanza e aspettativa del destinatario.
  Refresh/cambio pagina/filtro/chiusura/decisione/recovery invalidano un drag
  pendente. Dopo costo nativo, UX-02 torna alla vista aggiornata senza ID stantii.
- Ghost del cursore soltanto visivo: contenuti, ruoli e quantità cambiano
  alla conferma autorevole. Il protocollo contiene intenzioni semantiche,
  non coordinate pixel, nomi widget o strutture inventario Luanti.
- Sostituire Assegna/Svuota con i gesti, mantenendo ricerca, pagine, dettagli,
  annullamento e azioni senza destinazione naturale (mangia/medica) accessibili.
  Un rilascio non può significare contemporaneamente assegnare, indossare e
  consumare: la destinazione decide, le scelte native rimangono esplicite.

## Consegna e backlog

Controller CWM locale con soglia di 6 pixel e cancellazione alla rigenerazione
della GUI. Il gesto invia al bridge vista e nomi locali delle zone; il bridge
li risolve in identità native correnti. Sul filo: QuickbarBind/Swap,
InventoryArrange, Equipment o ItemTransfer. Nessun IMoveAction gameplay.
Swap confronta entrambi i token attesi e cambia i due slot atomicamente;
riordino e riferimenti sono metadati gratuiti, azioni fisiche restano CDDA.

Renderer verificato con gesti reali per riordino, hotbar, mano/indossati,
righe contenitore, Terra e quantità parziali; Esc/rilascio esterno, conferme,
costi/pausa, rifiuto per capacità, recovery e salvataggi. Le destinazioni
sulle icone dei contenitori del pannello principale condividono il percorso
semantico verificato e sono incluse nel nuovo ricontrollo manuale. La raccolta
mantiene il controller specchio preesistente; quello nuovo è limitato alla
formspec CWM_EQUIPMENT. [Ricevute riproducibili](../fixes/inventory-drag-and-drop-evidence.json).

Il backlog ha **13 PENDING**: ricontrollo drag di hotbar 1 (precedente FAIL
conservato come storia), hotbar 2–4 ancora non provati, due nuove prove per
mano/indossati e contenitori, sette vecchi punti. Ricontrolli UX-03 1–3 restano
PASS. Nessuna prova viene richiesta ora. Contenitori esterni, sigilli/fluidi,
quantità selezionate del pickup e batch moves richiedono interfacce dedicate.
