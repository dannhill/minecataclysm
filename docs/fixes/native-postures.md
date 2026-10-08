# Corsa e posture native

Aggiornamento successivo 2026-10-08: l'utente valida tutti i quattro punti
della checklist di questa fetta. I riferimenti a prove pending/rinviate sotto
conservano il contesto della consegna originale. I nuovi comandi/HUD sono in
[controlli e presentazione](controls-and-survival-presentation.md).


Quarta fetta essenziale indipendente dalle tre validazioni manuali rinviate.
R alterna corsa/cammino; X accovacciato/cammino; P a terra/cammino. Le shortcut
sono configurabili via keymap_cdda_run/crouch/prone. Shift conserva le azioni
chiudi/scendi. Luanti non moltiplica velocità, stamina o rumore: il controller
continuo usa già run_cost/burn_move_stamina/footstep_sound di CDDA.

Il comando CWM 2.8 è deduplicato e validato prima dell'accodamento e durante
l'esecuzione; non è accettato in pausa/menu/recupero. Il setter nativo conserva
costo nullo, invalida percezione, gestisce hauling e recoil. Offset e credito
subtile pagati non vengono azzerati. La transizione di esaurimento corsa è la
stessa funzione nativa ora condivisa dal movimento a caselle e frazionario,
che impedisce velocità di corsa aggiuntiva dopo stamina esaurita dentro un tile.

La proiezione usa flag semantici esclusivi. La camera in prima persona si
abbassa di 0,7 unità accovacciata e 1,3 a terra, con transizione cosmetica;
coordinate autorevoli e collisioni non cambiano. Nuoto e immersione conservano
l'altezza dedicata; attraversare un davanzale conserva il profilo precedente.
Il pannello mostra esclusivamente la modalità confermata dal server.

Limiti: rig/animazioni in terza persona, shortcut nel menu grafico completo
ed esposizione delle modalità aggiunte da mod restano successive. Non chiude
il piano di interazioni né certifica M5.5/SAVE-001. Le altezze saranno affinabili
al test utente. Checklist [salvata](../validation/pending-manual.md), IN ATTESA.

La demo è prodotta dal semantic reader collegato al core CDDA pinned originale,
con `--create-posture`. Densità zero non elimina gli spawn fissi di mapgen:
la sola fixture li cancella nella bolla iniziale con `map::clear_spawns()`.
Il mondo continua ad avere spawn nativi fuori da quella zona. Nessuna delle
interfacce da validare è necessaria per provare o conservare le posture.

In modalità ordinaria scandita dalle azioni, il primo comando ammesso dopo
il load avvia il prelude nativo e salda l'eventuale debito di mosse del save:
la fixture originale contiene -12 mosse. Questo può avanzare un turno anche
se il setter di postura è gratuito. I cambi successivi non avanzano il tempo;
la prova nativa diretta conferma costo nullo del setter e offset invariati.

## Verifica della consegna

Sorgente nativo compilato al commit `a4060a4`; albero CDDA invariato nei commit
successivi. Client con legenda definitiva al commit `e83b20e`; harness finale
`a9fe12d`. Patch complete e inventari in baseline; ricostruzione e replay
indipendente PASS. Compilazione incrementale, non build a freddo. Binari
installati identici SHA256 ai build; rollback 2.7 conservato negli artefatti.
La [ricevuta](native-postures-evidence.json) conserva hash, comandi, sorgenti
pinned, prove e tentativi precedenti. Artefatti:
`artifacts/playable-core-postures-20261008/`.

- CDDA: 7.448 asserzioni/43 casi PASS, `[cwm],[diving],[pickup]`, seed 42.
  Setter/offset/credito/RNG senza mutazioni extra, disponibilità verificata
  all'ammissione e riesecuzione, dupliche senza recoil ripetuto, costi/rumore
  nativi, esaurimento dentro un tile e flag contraddittori rifiutati.
- Protocollo 5/5 PASS, incluso resync prima di applicare posture contraddittorie.
- Luanti installato: 306 test e 648 asserzioni Catch2 PASS.
- GUI installata tramite start.sh: 16 controlli continui, 12 ordinari, 8 di
  rientro effettivo nel save. Pausa, pressione singola senza autorepeat,
  postura/camera, reconnect, posizione assoluta e campo move_mode canonico.
  Distanze nella prova continua: cammino 1,775, corsa 3,368, accovacciato 0,842,
  a terra 0,277 caselle, con la stessa pressione WASD di circa 0,45 s a 4x.
  Sono misure di questa prova, non nuovi moltiplicatori o benchmark generali.
- Regressioni reali: scheda corporea 19/19, raccolta 18/18, melee 21/21,
  con lettura del save da core pinned originale. I casi nativi di portata
  restano nel filtro completo; questa esecuzione GUI melee non ha attivato
  il ramo facoltativo di knockback/fuori portata del test precedente.

Le immagini della legenda finale sono state ispezionate: il pannello non si
sovrappone più al debug. L'errore iniziale di autorepeat è corretto nel client;
gli altri fallimenti erano assunzioni/strumentazione dei test e sono conservati
nella ricevuta. Le verifiche automatiche non sostituiscono le quattro prove
manuali rinviate dall'utente.
