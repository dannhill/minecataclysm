# Validazione manuale del ciclo di vita degli attori — 2026-10-04

Fonte: riscontro dell'utente dopo la consegna
[FND-04 identità/ciclo di vita](../fixes/fnd04-actor-lifecycle.md), report
`933de02`, sorgenti di accettazione `cedb871` e demo diurna `124702d`.
L'utente dichiara: «validati tutti e 3 i punti da me».
La validazione identifica la consegna associata, non un checksum o una
sessione specifica forniti dall'utente.

Sono accettati:

1. Presenze coerenti, senza duplicati o mesh sul piano sbagliato, dopo
   avvicinamento e salita/discesa sulla scala della demo.
2. Presenze/posizioni coerenti dopo il viaggio lungo il corridoio e il ritorno
   nell'area degli attori.
3. Presenze/posizioni coerenti dopo uscita e rilancio vicino agli attori.

Queste prove bastano per accettare il passo circoscritto. Non occorre ripetere
la checklist. FND-04 completo, SAVE-001 e il gate M5.5 mantengono i propri
limiti ed esiti; animazioni e tempo reale non sono certificati da questi test.

## Segnalazione fuori dal percorso

L'utente riferisce di essersi buttato oltre la strada nel «fiume di mattoni»:
lo schermo è diventato completamente nero e ha dovuto chiudere il gioco.
Non considera il caso prioritario e chiede se occorra rientrare nella demo.

Registrare il caso come blocco visivo/esplorativo da riprodurre. Non è ancora
accertato se si tratti di immersione, caduta, cambio piano, luce o proiezione.
Non attestare un crash, una morte o una correzione senza evidenza. Conservare
la sessione demo; non serve un nuovo test manuale ora. L'eventuale uso di
`actor-demo.sh --fresh` crea un'altra copia senza cancellare quella precedente.

## Seguito proposto

Primo prototipo circoscritto dello scheduler in tempo reale della fase 2:
avanzamento nativo CDDA anche a personaggio fermo, rapporto predefinito 1:1,
velocità globale coerente, pausa esplicita/menu e autopausa su nuova minaccia
percepita. Partire dalla griglia nativa interpolata esistente; il confronto
con offset continuo autorevole resta un prototipo successivo, senza scegliere
ora il controller finale. Le attività lunghe accelerate restano nello scope
della fase 2, con interruzioni native.

Verificare tempo/effetti nativi, movimento senza accumuli o raffiche,
disconnessione/resync, salvataggio/caricamento e renderer reale. Quando questa
prima scena sarà giocabile, ricordare all'utente il confronto su scale a gradini
e a pioli automatiche/continue prima di finalizzare il controller.
Luce, campi/HUD, percezione leggibile, animazioni e gli altri criteri FND-04
restano aperti. Questa registrazione propone il seguito; non lo implementa.
