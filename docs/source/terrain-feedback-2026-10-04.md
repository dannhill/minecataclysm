# Prova manuale del terreno e segnalazioni — 2026-10-04

Fonte: riscontro dell'utente dopo il confronto A/B introdotto dal codice
`3a830d8`, documentato in `57cbda6`. La preferenza estetica è una decisione;
le anomalie riportate sono segnalazioni, non riproduzioni automatiche. Il
messaggio non identifica una sessione precisa per ciascun episodio: non
attribuire tutti i casi alla fixture o al mondo normale senza verificarlo.

## Decisioni e richieste effettive

- **B approvata come direzione per materiali e vegetazione.** A è percepita
  come artificiale e povera; B come naturale e più varia. Questo non approva
  ogni placeholder geometrico di B e non certifica il renderer completo.
- **Nebbia attuale non approvata come soluzione definitiva.** Riduce pop-in
  e sensazione di isola nel vuoto, ma la distanza visiva è troppo restrittiva.
  L'utente chiede di discutere ora e conservare le alternative nel piano.
- Opzione proposta 1: distanza maggiore per strutture già osservate,
  congelate all'ultima osservazione, senza creature lontane; valutare come
  attenuare la comparsa delle creature quando diventano percepite.
- Opzione proposta 2: aumentare la scala grafica delle caselle; dubbio su
  proporzioni e beneficio reale.
- Opzione proposta 3: rendere graficamente visibili elementi oltre la
  percezione, mantenendo limiti o penalità di gameplay. L'utente è poco
  propenso: rischio di snaturamento e ribilanciamento non necessario.
- Richieste altre proposte. Nessuna delle opzioni sulla distanza è stata
  selezionata definitivamente dall'utente.
- Pianura uniforme accettabile in città e sulla costa; poco credibile nei
  campi/boschi. Piccoli dislivelli estetici sono una possibilità, **non una
  priorità**. Facoltativo includerli in una futura prova più ampia, senza una
  sessione di validazione dedicata soltanto a essi.
- Campo visivo breve, edifici bassi e mancanza di alberi medi/alti contribuiscono
  alla sensazione di piattezza. La resa del bosco resta da sviluppare.

## Difetti segnalati e indagine iniziale

| Segnalazione | Riscontro nei sorgenti / limite dell'indagine | Lavoro richiesto |
|---|---|---|
| Finestre assenti, ma richiesta nativa di attraversamento | L'export classifica WINDOW_OPEN quando `movecost > 0`. Esistono varianti JSON con vetro ancora chiuso e costo positivo: attraversabilità e stato del vetro non sono equivalenti. Non identificata la variante incontrata dall'utente. | Derivare identità, stato e passaggio dalle definizioni native risolte; distinguere vetro, tende, telaio, danni e rinforzi. |
| Alcune porte mostrano stato opposto | La classificazione usa TFLAG_DOOR e il terreno destinazione di `close`, senza coprire tutte le famiglie. Alcune porte native chiuse/locked non hanno quel flag. Non riprodotta l'esatta inversione riportata. | Matrice sulle varianti native, collegamenti open/close, locked/broken e aggiornamento atomico delle due metà; includere osservazione da entrambi i lati e reload. |
| Due blocchi di vetro scompaiono quando la finestra si apre | Confermato direttamente in `place_cdda_tile`: lower e upper usano lo stesso materiale; WINDOW_OPEN è aria. | Per finestre ordinarie: davanzale/parete inferiore permanente e vetro superiore apribile. Conservare famiglie diverse, ad esempio vetrate intere; raccordare camera, piedi e attraversamento/vault nativo. |
| Cubi lignei attraversabili, anche fuori dagli edifici | Gli arredi hanno una resa generica; CDDA decide impedimenti e costi, e la fisica Luanti non governa il movimento CWM. Non identificati gli oggetti specifici. | Asset distinguibili per arredi/vegetazione e indicazione della categoria percepibile. Non aggiungere collisioni Luanti per rendere solidi placeholder che CDDA consente di attraversare. |
| Chiusura brusca entrando in uno stagno | Un log della demo contiene un abort da input terminale; l'ingresso in acqua profonda può usare un `uilist` non adattato. Associazione al passo nello stagno plausibile, non dimostrata. | Priorità alta: riprodurre in fixture isolata acqua profonda con/senza oggetti vulnerabili; adattare la conferma nativa, conservando effetti/costi e annullamento. |
| Camminata apparentemente sulla superficie del mare | Il materiale WATER non distingue profondità/postura nella presentazione. La riva della fixture usa `t_water_sh`, che si può guadare; il nuoto profondo esiste nella logica nativa. | Distinguere guado, nuoto, immersione e livelli del liquido; altezza visiva coerente con lo stato autorevole. L'effetto grafico non è un risultato finale accettato. |
| Secondo piano visibile, scale non trovate | L'export corrente tratta terreni con nome contenente `stairs` come FLOOR; non presenta una scala riconoscibile. Non provato che l'edificio specifico avesse una scala raggiungibile. | Esportare connessioni verticali native e renderle leggibili, verificando destinazione/GOES_UP/GOES_DOWN. Non inventare scale o teletrasporti per edifici che non li possiedono. |

Le precedenti prove positive su movimento, rebase, zombie visibili e morte da
combattimento restano evidenza nei casi provati. Il nuovo riscontro riapre la
copertura delle varianti di aperture e dell'esplorazione acquatica; non va
descritto come convalida generale delle strutture o di tutti i menu nativi.

## Log letti, senza modificare i mondi

`artifacts/terrain-prototype/plays/run-inDyCv/logs/cdda.log` termina con:

```text
terminate called after throwing an instance of 'std::runtime_error'
  what():  input_manager::get_input_event called in test mode
```

Il log Luanti della stessa sessione riporta SIGTERM/shutdown alle 13:11:38;
il launcher arresta il client quando il processo CDDA termina. Questo è un
abort concreto, non una morte attestata. Il log non conserva l'azione e gli
oggetti che hanno aperto il menu: la causa precisa richiede riproduzione.
La sessione successiva `run-rU7lUX` termina invece con save nativo SUCCESS.

| Artefatto locale, ignorato da git | Byte | SHA-256 |
|---|---:|---|
| `run-inDyCv/logs/cdda.log` | 785 | `9986de6e7336712d51363693484cf007a8b8a4e91801d995327cc29994c01958` |
| `run-inDyCv/logs/luanti.log` | 370671 | `3aa4e39c8201690373155403d123f498b45ca0aa0abad7624ea88885b52a0530` |
| `run-rU7lUX/logs/cdda.log` | 750 | `c2456f8d19b561570750b5fbb371e5b6ced5750d43cc0042faf7994416d38963` |

Entrambi i log Luanti contengono anche warning ripetuti `moved too fast` del
server di presentazione. Non dimostrano una regressione della camera, ma
restano da indagare per evitare controlli/pollution dei log su coordinate
governate da CDDA. Non assumere che il vecchio test di movimento copra ogni
zona esplorata ora.

La [discussione progettuale](../design/visibility-and-world-memory.md) integra
questo riscontro nel [piano completo](../../IMPLEMENTATION_PLAN.md).
In questo aggiornamento sono cambiati soltanto documenti: B resta disponibile
nella demo; `start.sh` non è ancora stato promosso alla nuova resa. Nessun
nuovo rilievo, cache di memoria o comportamento dell'acqua è stato implementato.

Aggiornamento successivo: la [riparazione esplorativa](../fixes/exploration-apertures.md)
implementa B nel gioco normale, le correzioni mirate di aperture/acqua e
OPEN/CLOSE puntati. Il paragrafo precedente descrive lo stato al momento
della registrazione del riscontro, non quello successivo alla riparazione.
