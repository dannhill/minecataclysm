# Riscontro umano liquidi/sigilli e cursore — 2026-10-25

Fonte: messaggio diretto dell'unico sviluppatore umano nella conversazione.
Documento redatto da un LLM sul suo riscontro; questi PASS non provengono
né dai test automatici né da un playtest dell'agente.

> 1 PASS 2 PASS 3 PASS 4 PASS. Commenti generali: il pointer del mouse viene dislocato dopo aver premuto un'azione ogni tanto o sempre, e non è una sensazione carina o usuale. Dammi altri 4 test manuali da fare che siano più importanti possibili secondo gli stessi criteri di prima che non siano già stati fatti.

## Corrispondenza con i quattro test proposti

| Numero nella risposta umana | Scenario richiesto | Punto del backlog | Esito |
| --- | --- | --- | --- |
| 1 | Riempimento della tanica, pausa con I, interruzione con acqua già prelevata conservata | LIQ-01.1 | PASS |
| 2 | Travaso nella bottiglia piccola, limite di capacità, resto nella tanica e rifiuto del recipiente pieno | LIQ-01.2 | PASS |
| 3 | Quit durante il riempimento e riapertura della stessa demo senza --fresh, conservando lavoro e acqua già travasata | LIQ-01.4 | PASS |
| 4 | Cancel prima di aprire la bottiglia sigillata; poi Open, stessa acqua e Pour disponibile | SEAL-01.1 | PASS |

La copertura è quella delle istruzioni effettivamente proposte e provate.
Non si deducono prove personali di congelamento, miscela di liquidi incompatibili,
contenitori annidati o di ogni combinazione di salvataggio. Restano pendenti
LIQ-01.3 e SEAL-01.2–4. Il contatore passa da 65 a **61 PENDING**.
La segnalazione UX non revoca i quattro PASS funzionali.

## UX-CURSOR-01 — OPEN, da riprodurre e correggere

Il puntatore cambia posizione dopo un'azione; il developer non ha ancora
stabilito se accada sempre o solo a volte. Il comportamento è percepito come
innaturale e fastidioso. Non sono ancora accertati causa, menu esatti o frequenza.

Prima di ampliare ulteriormente i menu degli oggetti, verificare i passaggi
inventario → azione/scelta nativa → ritorno al menu. Conservare una posizione
coerente del cursore tra menu correlati, gestendo separatamente il puntamento
relativo della visuale e senza attivare involontariamente pulsanti/trascinamenti.
È una segnalazione aperta, non un nuovo test funzionale numerato da aggiungere
al contatore. Il runtime e i binari non cambiano in questo aggiornamento.

## Prossime quattro priorità, già pendenti

I nuovi numeri 1–4 del prossimo giro corrispondono, nell'ordine, a:

1. SEAL-01.3 — Lattina nello zaino: apertura e Cancel del travaso successivo.
2. REST-01.2 — Tentativo di dormire, annullamento e sonno effettivo.
3. REST-01.3 — Accelerazione del riposo, pausa e ritorno al ritmo normale.
4. DIS-01.3 — Interruzione/ripresa dello smontaggio e recupero dei materiali.

Sono quattro punti esistenti, non nuove voci aggiuntive. Le istruzioni sono
nel backlog; nessun PASS è dedotto dalla scelta delle priorità.
