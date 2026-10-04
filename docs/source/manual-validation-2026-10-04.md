# Riscontro manuale FND-01 — 2026-10-04

Fonte: prova dell'utente tramite `start.sh`, successiva al commit `661ac63`.

- Invisibilità generalizzata assente; movimento, muri/finestre, apertura porte
  e riconoscimento della minaccia accettati dall'utente.
- Save/load nella stessa posizione provato 2–3 volte e accettato. Persistenza
  manuale delle porte non provata: resta distinta dalle verifiche automatiche.
- Sfarfallio frequente durante movimento: cambiamento importante della scena
  per una frazione di secondo, correlato all'indicatore IPC da ~16 a 80–100+ ms.
  La convalida grafica resta aperta; le scene automatiche precedenti non
  esercitavano cambi di origine della reality bubble.
- Confine dell'area renderizzata simile a un'isola nel vuoto: richiesta una
  transizione di nebbia che non riveli terreno/conoscenza non disponibili.
- Richiesti comandi puntati espliciti OPEN e CLOSE, oltre all'apertura camminando.
- Il warning ripetuto è fastidioso ma accettato per ora, mantenendo safe mode.
- Chiusure esplorando un pozzo scuro e una zona urbana; ipotesi dell'utente:
  morte/collisioni da nemici non rappresentati. I log recenti mostrano invece
  un abort da `input_manager::get_input_event called in test mode`: morte
  nativa e richieste di conferma vanno discriminate, non presunte.

Priorità corrente: riprodurre/correggere il cambio di riferimento grafico,
rappresentare le creature percepite ed esporre le conferme native necessarie
a esplorazione/morte. Questo anticipa una parte di FND-04; non certifica il
lifecycle completo, il bestiario, SAVE-001 o il gate M5.5. Poi FND-02/03.

Nebbia del bordo e interazioni OPEN/CLOSE puntate restano esplicitamente nel
piano; nessuna variante definitiva di movimento/guida è stata scelta.
