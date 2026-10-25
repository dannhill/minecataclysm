# Riscontro umano riposo, lattina e smontaggio — 2026-10-25

Fonte: messaggio diretto dell'unico sviluppatore umano. Questo documento è
redatto da un LLM sul suo riscontro; i PASS non provengono dall'automazione.

| Numero proposto | Punto del backlog | Riscontro |
| --- | --- | --- |
| 1 | SEAL-01.3 — apertura lattina nello zaino e annullamento del travaso | PASS, con limite di recupero riferito |
| 2 | REST-01.2 — tentativo e sonno effettivo | PASS, con commenti sul ritmo e sulla sua chiarezza |
| 3 | REST-01.3 — accelerazione, pausa e risveglio | PASS |
| 4 | DIS-01.3 — interruzione e ripresa dello smontaggio | PASS |

Sono quattro prove già pendenti: 61 → **57 PENDING**, prima dei ricontrolli
separati delle modifiche successive. I PASS restano validi per i casi provati;
non attestano i nuovi livelli di velocità, il recupero dalla lattina o il cielo.

## Commenti e direttive

- La lattina perde il sigillo e cade a terra. Tentare di rimetterla nello
  zaino dà il rifiuto per contenitori aperti/liquidi; anche svuotare un altro
  contenitore non rende chiaro come trasferirvi il contenuto. La posa a terra
  dopo Cancel è nativa; il percorso d'interazione con il liquido a terra manca.
- Non è chiaro quando il sonno sia accelerato né come si rapporti alla velocità
  F8. La durata reale del sonno è percepita come eccessiva: richiesta una modalità
  di accelerazione superiore, conservando la simulazione nativa.
- Le scelte/conferme hanno punteggiatura incoerente: preferenza esplicita per
  etichette senza punto fermo finale. Non modificare gli ID o il significato
  delle scelte; conservare narrativa e punteggiatura semanticamente necessaria.
- Rendere facile cambiare l'aspetto delle interfacce in futuro: separazione
  di dati/logica/input e rendering/tema, con rework mirato se necessario.
- Bug: ambiente notturno molto scuro ma cielo/skybox ancora azzurro e luminoso.
- Successive precisazioni: fornire altri quattro test prioritari **dopo aver
  completato gli interventi**, non interrompere il lavoro per proporli prima.

Il salto del puntatore è la precedente segnalazione UX-CURSOR-01; la sua
correzione e la nuova resa restano ricontrolli distinti dai quattro PASS.
