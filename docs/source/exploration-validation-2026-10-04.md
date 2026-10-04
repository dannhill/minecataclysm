# Validazione manuale dopo la riparazione esplorativa — 2026-10-04

Fonte: riscontro dell'utente nella conversazione Codex, dopo l'installazione
documentata in [riparazione esplorativa](../fixes/exploration-apertures.md).
Riferimento distribuito: codice `2a01800`, report `f0873d5`; identità dei
binari nel [registro](../fixes/exploration-apertures-evidence.json).
Il riscontro riguarda `start.sh` normale; non identifica la sessione o ogni
variante incontrata. Le prove manuali restano distinte dalla certificazione
completa e dalle verifiche automatiche.

## Funzionalità accettate

- Clic destro OPEN e Shift + clic destro CLOSE su porte e finestre funzionano.
  Puntamento basso sul davanzale compreso e accettato funzionalmente;
  ergonomia definitiva ancora da valutare.
- Terreno B nella partita normale validato.
- Creature con cubo viola leggibili e movimento accettato. Aspetto placeholder;
  non una convalida del bestiario o delle animazioni complete.
- Acqua bassa isolata: ingresso senza problemi e senza popup nel caso provato.
- Acqua più profonda: avviso di danno allo smartphone e conferma comprensibili;
  ingresso e spostamento in acqua, poi ritorno sul terreno, senza interruzione.
  Non riferita una verifica dell'effettivo danno all'oggetto nel save.
- Posizione del personaggio dopo quit/load validata più volte.
- Stato di apertura/chiusura di porte e finestre modificato dal giocatore
  conservato dopo quit/load.
- Dopo allontanamento fino alla scomparsa della proiezione grafica, quit/load
  e ritorno, le aperture mantengono lo stato modificato. È persistenza e
  riproiezione; non certifica memoria grafica distante o uscita delle submap
  dalla simulazione nativa.

## Osservazioni da conservare

**Oscurità negli interni.** L'NPC nella stanza dello spawn scompare oltre circa
tre caselle. L'utente ha ricondotto il fenomeno all'assenza di luce quando
porte e finestre sono chiuse. La presentazione non rende abbastanza chiaro
il buio: comparsa/scomparsa sembra arbitraria. Nessuna riproduzione della
specifica stanza è stata eseguita in questo aggiornamento.
Nei sorgenti correnti NPC/mostri usano `avatar::sees`, ma i tile ricevono una
luce naturale semplificata per livello Z, anziché la luce locale con occlusione
e sorgenti. Discrepanza da affrontare in FND-04/fase 2, conservando i limiti
nativi della percezione. Non è un'urgenza richiesta ora.

**Immersione.** L'immagine diventa nera; ingresso e uscita funzionano, ma manca
una percezione visiva riconoscibile dell'essere sott'acqua. Registrato per
presentazione del volume/superficie, camera, tinta/attenuazione e indizi guidati
dallo stato nativo. Non attribuita la causa esatta del nero, né autorizzata
visibilità aggiuntiva per correggerlo. Priorità successiva, insieme alla
leggibilità di luce/percezione.

**Confine grafico.** Assenza di nebbia ancora giudicata molto sgradevole.
Confermata la necessità del lavoro su panorama/memoria e transizione del bordo.
Non scelta una nuova distanza o un'alternativa definitiva di
[panorama](../design/visibility-and-world-memory.md).

**Piattezza.** Con B è molto meno evidente. L'utente chiede di rinviare il
problema del rilievo almeno fino a dettagli grafici sufficienti. Nessun
prototipo di dossi o nuova worldgen ora.

## Raccomandazione per il seguito

Correzioni accettate nei casi provati. Proseguire con FND-02 (trasporto robusto
e lavoro limitato), poi FND-03 (sessioni, deduplicazione e resync), prima della
cache del panorama. Successivamente confrontare panorama/nebbia e leggibilità
della percezione, includendo interno buio e immersione nella prova più ampia.
Nessun altro ciclo obbligatorio della stessa checklist richiesto all'utente.

Proposta ergonomica dell'agente, non una scelta già approvata: puntamento
semantico dell'intera apertura anche quando il vetro è assente, evidenziazione
del telaio/area e azione disponibile esplicita. Occlusione e portata native,
scelta stabile fra aperture vicine e validazione CDDA; nessuna collisione
artificiale o interazione attraverso muri.

FND-04 completo, SAVE-001 e il gate M5.5 restano distinti da questa accettazione.
