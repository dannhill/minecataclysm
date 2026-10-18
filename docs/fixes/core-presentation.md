# Tre passi del core: raccolta, modelli, movimento — 2026-10-18

L'utente ha autorizzato tre o quattro passi consecutivi dopo la correzione
Indossa/Togli, senza attendere prove personali. Implementati i tre elementi
già pianificati nel [contratto](../design/core-presentation-followups.md).
CWM **2.23 invariato**; il core e il binario CDDA restano quelli precedenti.

## Comportamento

1. **Raccolta sfusa diretta.** RMB su un singolo stack non contenitore richiede
   direttamente PICKUP, anche per sassi e munizioni conteggiate. Tipo, indice,
   cariche attese, accesso, capacità e costo vengono rivalidati da CDDA.
   Raccoglie tutta la pila puntata; quantità parziali restano nell'interfaccia
   di mobili/contenitori/gruppi. In pausa nessuna selezione si accoda al resume.
2. **Materiali e avatar.** Il bridge non dipinge più la pelle sulle superfici
   di armatura vuote. Zombie: primo materiale vuoto, secondo pelle. Umano:
   primo pelle, secondo vuoto; il rig pinned espone due materiali renderizzati,
   benché la definizione Lua Mineclonia dichiari anche una terza texture.
   Riutilizzati rig e immagini già estratti, con filtro nearest per la pixel art.
   Nel runtime integrato il giocatore usa il modello voxel, anziché lo sprite
   Luanti predefinito; scala e piedi seguono la proiezione umanoide.
3. **Cammino e orientamento.** Cicli idle/cammino presi dai rig pinned, direzione
   dagli spostamenti confermati. Il giocatore ha anche pose crouch/run/prone
   secondo i flag nativi. L'avanzamento dei frame usa una sola volta per update
   il tempo visivo scalato; Irrlicht e l'animazione basata sui tasti locali non
   lo fanno avanzare autonomamente. Menu, pausa e recovery congelano la posa.
   Riapparizioni/reconnect non ripercorrono intervalli non percepiti.

Geometria, pose e rotazione modificano soltanto nodi di presentazione: nessuna
coordinata, collisione, AI, spesa di mosse o proprietà CDDA cambia nel client.
Visibilità e identità restano quelle autorevoli. La riparazione del tempo dei
vestiti resta distinta e conserva la semantica nativa atomica.

## Verifica

Build incrementale Release/LTO da sorgenti ricostruiti e inventari verificati,
non clean build. 309 test client / 47 moduli e 648 assert Catch / 4 casi PASS.
**195 controlli grafici/canonici PASS**: 26 renderer controllato ricostruito,
15 scena nativa percezione/scale/reload, 50 raccolta/trasferimenti ricostruiti,
26 renderer installato, 50 raccolta/trasferimenti installati e 28 regressioni
Indossa/Togli sul normale `start.sh`. Materiali reali, avatar, frame fermi/scalati,
orientamento, lifecycle/resync, quantità e salvataggi verificati.
[Ricevuta riproducibile](core-presentation-evidence.json): comandi, source identity,
hash, immagini e coppia runtime di rollback. Client installato; CDDA invariato.

Il renderer controllato usa un peer sintetico per posizioni/clock/percezione;
non prova la AI CDDA. La scena nativa percezione/scale dichiara esplicitamente
la modalità storica a passi interi. La raccolta e i ricontrolli dei vestiti
usano invece il normale movimento continuo real time e il launcher reale.
Tutte le fixture e i salvataggi sono isolati. Il reader indipendente del
core pinned verifica lo stato canonico, senza promuovere l'intero SAVE-001.

## Limiti e seguito

I modelli umani sono proxy generici: vestiti, mutazioni, specie/taglie e
anatomia completi non sono ancora ricostruiti graficamente. Le altre famiglie
senza rig mantengono il cubo placeholder. Attacchi/reazioni aspettano eventi
nativi dedicati; non vengono inventati dalla vicinanza o dal calo degli HP.
Audio e posa delle armi restano i prossimi elementi di presentazione.

Nove prove nuove nel [backlog](../validation/pending-manual.md): **18 PENDING +
1 FAIL manuale** complessivi. Nessun test personale obbligatorio oggi e nessun
PASS dedotto dall'automazione. Mapping Sol batch60 invariato; nessun salvataggio
personale usato. Full SAVE-001 OPEN; M5.5 storico FAILED.
