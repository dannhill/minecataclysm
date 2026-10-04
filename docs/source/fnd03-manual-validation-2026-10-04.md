# Validazione manuale FND-03 — 2026-10-04

Fonte: riscontro dell'utente nella conversazione Codex dopo il task
[FND-03](../fixes/fnd03-session-recovery.md), sorgenti `74b7a40` e report
`fd50215`. L'utente scrive «Valido tutto» e autorizza il passo successivo.
Questa accettazione riguarda la checklist manuale proposta; non certifica
il gate M5.5 completo, SAVE-001 o tutte le varianti del mondo.

Restano due segnalazioni, entrambe a priorità molto bassa:

- In alcuni edifici, in particolare strutture di pietra, lo stato grafico
  aperto/chiuso di alcune porte è invertito rispetto allo stato logico.
  La segnalazione era già presente; la copertura delle famiglie native è
  incompleta. Non sono identificati gli ID di terreno o un salvataggio
  riproducibile, e non si attesta qui una causa né una correzione.
- Nelle porte doppie di alcune case di mattoni una delle ante aperte ha il
  perno al centro del varco anziché vicino al muro. Priorità ancora inferiore.
  La geometria corrente usa un solo lato di perno; occorre verificare
  adiacenza/orientamento prima di scegliere l'anta speculare.

Proseguire FND-04 senza ripetere le prove già accettate. Conservare questi
casi nella copertura futura delle aperture; nessuna collisione o autorità
indipendente di Luanti per correggerne la presentazione.
