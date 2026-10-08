# Medicazioni native — prima fetta

**I → oggetto reale → Medica... → parte corporea → conferma** avvia una
medicazione CDDA. Il selettore mostra solo le parti ammesse dal body_window
nativo, con salute ed effetti conoscibili. Cancel/No conservano l'oggetto.
La scelta usa i numeri mostrati; testi CDDA e nomi possono essere in inglese.

La fetta copre gli oggetti non commestibili con uso heal: bende, salviette,
stracci antisettici e analoghi. Oggetti sporchi, rotti, incompatibili o senza
cariche e uso sott'acqua/in sella sono rifiutati. Farmaci ingeribili e
antisettici liquidi richiedono un'interfaccia successiva; non vengono
instradati nel consumo FOOD/DRINK. Parte→oggetto dalla scheda H, cura di NPC,
chirurgia, dettagli completi delle malattie e accelerazione automatica delle
attivita lunghe restano nel piano.

**CDDA possiede la cura.** Avatar_action::use_item gestisce accesso e oggetto;
heal_actor conserva condizioni native e riduzioni di durata per wound care.
Il solo selettore terminale body_window ha un adattatore alle scelte esterne:
usa le stesse voci native gia costruite, senza duplicare la logica di cura.
Una conferma esplicita precede ACT_FIRSTAID. Il target conserva la vera
item_location, incluse tasche annidate. Firstaid_activity_actor applica
bendaggio/disinfezione, sanguinamento e altri effetti previsti dall'oggetto,
pratica e consumo al termine. Una benda non deve ripristinare cuori subito:
nel pin favorisce la guarigione nel tempo.

Luanti mostra il lavoro residuo nativo. **I** ferma il tempo e offre
**Interrompi trattamento**, poi Character::cancel_activity applica i suoi
vincoli/backlog senza rimborso. Non vengono accodati movimento o azioni durante
la cura; anche un comando gia in coda ricontrolla se e iniziata un'attivita.
**H** mostra i nomi nativi delle condizioni di ferita e dei trattamenti sulle
parti interessate, senza pubblicare tutte le malattie nascoste o timer esatti.

CWM **2.12** aggiunge TREAT=5, la sesta ragione per azione, FirstAidState,
CancelFirstAidRequest e le condizioni conoscibili della parte. Token/progresso
sono effimeri; nessun nuovo formato save. Snapshot con cura e consumo insieme,
progresso malformato e cancellazione di tipo/token errati sono rifiutati.
I due runtime sono aggiornati insieme. In modalita ordinaria CDDA completa
l'attivita senza il pacing reale; progresso/stop interattivo si provano in RT-02.

## Prova e validazione

`./medicine-demo.sh --fresh` crea una copia della scena salvata dal lettore
CDDA pristine: braccio sinistro/torso feriti, tre bende, una salvietta, una
benda sporca e un sasso. Nessun pickup/cibo necessario; le due checklist
precedenti restano indipendenti. Senza --fresh riprende il save della demo.
La stessa interfaccia e disponibile da I nella partita normale.

Le quattro prove utente sono nel [backlog manuale](../validation/pending-manual.md).
**Dodici punti pendenti**, quattro per inventario, consumo e medicazioni;
nessuna accettazione dedotta dai test. Il prossimo passo essenziale e il
crafting guidato. M5.5 resta storico FAILED e SAVE-001 completo ancora aperto.

Verifiche PASS: 8.131 asserzioni CDDA/55 casi, 308 test Luanti + 648
asserzioni Catch2, protocollo 6/6 e 134 controlli nel renderer installato
(medicazione, ripresa, turni, regressioni consumo/equipaggiamento).
Verifiche, sorgenti/binary esatti, limiti e comandi riproducibili sono nel
[registro tecnico](native-medicine-evidence.json). Artefatti isolati:
`artifacts/native-medicine-20261008`. La revisione read-only AGY
Gemini 3.8 Flash High e arrivata al limite CLI di 180 s senza conclusione
utilizzabile; il log parziale non e trattato come revisione approvata.
