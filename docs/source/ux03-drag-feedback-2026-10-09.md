# Riscontro UX-03 e richiesta drag-and-drop — 2026-10-09

Fonte: messaggio dell'utente successivo alla consegna CWM 2.17.

> Ricontrolli UX-03: 1 PASS 2 PASS 3 PASS; UX-03 — Hotbar assegnabile e persistente: 1 FAIL (non mi piace: devi rimuovere tasti "assegna slot" e "svuota slot" e metti tutto il menu, tutte le parti del menu come drag and drop). Il resto non ho ancora testato, ma puoi tenerti questo e nel frattempo pensare al prossimo step e mantenere il backlog con i soliti elementi.

## Esito registrato

- Ricontrolli UX-03: ricerca/focus, nuvole/pausa, quantità/errori **1–3 PASS**.
  Il PASS del terzo punto comprende la checklist proposta, senza dedurre un
  PASS delle vecchie prove UI/mapping o eccezioni UX-02.
- Hotbar assegnabile/persistente: **1 FAIL di ergonomia**. Non è una
  segnalazione di corruzione o mancata persistenza: il flusso a pulsanti è
  rifiutato. Non ridurre la richiesta al solo trascinamento della hotbar.
- Hotbar **2–4 PENDING**, non ancora provati; nessuna accettazione inferita
  dalle prove automatiche della consegna precedente.
- Restano i quattro vecchi ricontrolli UI/mapping e le tre eccezioni UX-02.
  Totale aperto: **11 punti = 10 PENDING + 1 FAIL**.

## Nuova direttiva

Rimuovere i pulsanti Assegna/Svuota nella prossima revisione; trascinamento
degli oggetti in tutte le parti dell'inventario e nelle sottoviste: griglia,
hotbar, mano, indossati, contenitori/trasferimenti e raccolta. Ricerca,
filtri, dettagli e conferme rimangono controlli appropriati alle loro funzioni.
Azioni fisiche continuano a pagare costi e validazioni nativi; spostare la
presentazione o un collegamento rapido non crea un trasferimento gratuito.

Il [piano basato sui sorgenti](../design/inventory-drag-and-drop.md) precede
lingua/mira nella sequenza operativa. Questa turnazione registra il riscontro
e prepara quel piano: **nessun runtime modificato e nessun drag-and-drop
nuovo dichiarato implementato**. Le nuove prove verranno proposte nel backlog
alla consegna; non occorre ripetere ora i tre PASS appena acquisiti.
