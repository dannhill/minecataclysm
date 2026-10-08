# Corsa e posture native

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
