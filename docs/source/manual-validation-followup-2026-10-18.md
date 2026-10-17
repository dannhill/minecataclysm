# Riscontro manuale successivo e decisione sui vestiti — 2026-10-18

Fonte: conversazione dell'utente dopo la consegna INT-01. Integra, senza
sostituirlo, `manual-interaction-feedback-2026-10-18.md`.

- EXT-01: punto 4 PASS, inclusa assenza della raccolta differita dalla pausa.
  Commento: per un oggetto sfuso il menu 9×3 è scomodo; preferita la raccolta
  diretta. I contenitori e le pile con quantità richiedono valutazione distinta.
- UX-04A, Dialoghi nativi e feedback del lavoro: punti 1–4 PASS.
- Ricontrolli dei commenti 2026-10-13: 1 PASS, 2 FAIL, 3 PASS.
  Il punto 2 segnala che I non mette in pausa il costo temporale di
  indossamento/rimozione e manca un pulsante per interrompere.
- LANG-01: punto 2 PASS (il punto 1 era già PASS).
- UX-04B, Scheda medica strutturata: punti 1–4 PASS.
- UX-05: punto 1 PASS; punti 2–4 non ancora provati.

Sono 13 nuovi PASS. Prima di nuove prove il backlog passa da 21 PENDING +
2 FAIL a **9 PENDING + 1 FAIL**. I PASS personali non derivano da automazione.

Prima di implementare un'interruzione dei vestiti l'utente ha precisato:

> Fermo, prima controlla qual è il comportamento nativo di cdda. Se richiede
> tempo e anche lì è interrompibile fallo, altrimenti parliamone.

Esaminato il pinned locale: il singolo capo viene applicato atomicamente e
addebita mosse; ACT_WEAR non introduce una vestizione frazionaria per capo.
È stata proposta la conservazione di queste regole, distinguendo il tempo
residuo da un'attività annullabile e correggendo separatamente la pausa con I.
Risposta esplicita dell'utente:

> Facciamo la soluzione fedele al comportamento nativo.

Il ricontrollo 2 conserva il FAIL sulla pausa finché provato personalmente;
la richiesta di annullamento del singolo capo è superata da questa decisione.
Non si aggiunge un nuovo conteggio per lo stesso ricontrollo. La raccolta
diretta degli oggetti sfusi resta un seguito UX da affrontare separatamente.
