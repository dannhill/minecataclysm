# Validazioni manuali da riproporre

L'utente il 2026-10-08 ha chiesto di rinviare ancora entrambe le prove
(raccolta e HUD/scheda corporea) e proseguire autonomamente con un'altra
feature essenziale ortogonale. **Rinviata non significa approvata.**
Riproporre tutte le checklist alla prossima consegna, senza bloccare lo
sviluppo autorizzato né anticipare l'inventario interattivo.

## Raccolta — IN ATTESA

Dalla directory del progetto: `./pickup-demo.sh --fresh`. Copia isolata,
movimento continuo 4x; davanti alla partenza, guardando in basso, sasso e
7 munizioni 9mm. Non serve ripetere la validazione RT-02 già accettata.

1. Tasto destro sulla pila: GUI chest Mineclonia, tooltip delle munizioni e
   tempo fermo. Esc chiude senza raccogliere.
2. Riapri e trascina le munizioni dal pannello superiore a uno slot inferiore
   vuoto: GUI chiusa, attività nativa, solo il sasso rimane a terra.
3. Esci e rilancia `./pickup-demo.sh` senza `--fresh`: solo il sasso rimane.
   Tasto destro sul sasso: raccolta diretta, nessuna GUI, nessun residuo.
4. Esci e rientra: gli oggetti raccolti non ricompaiono.

Il pannello inferiore è ancora di sola lettura, anche per indossati,
impugnati e contenuti annidati; le icone generiche sono fallback. Dettagli e
verifica automatizzata: [ground-items-ui.md](../fixes/ground-items-ui.md).

## HUD e scheda corporea — IN ATTESA

Feature indipendente dalla raccolta: `./body-demo.sh --fresh`. Personaggio
assetato/stanco, testa e braccio sinistro feriti; nessun pickup necessario.

1. Controlla il pannello in basso a sinistra: stamina e salute di testa/torso,
   con i bisogni percepiti. Non devono esserci i cuori/hotbar fittizi di Luanti.
2. Premi **H**: la scheda mostra parti del corpo e bisogni, incluse le ferite
   iniziali. Attendi e prova WASD: tempo/personaggio restano fermi.
   **Esc** o **Torna al gioco** chiude e riprende la modalità precedente.
3. Metti in pausa con **F7**, apri H e richiudi: il gioco deve restare in pausa
   finché premi di nuovo F7. La lettura non deve curare o raccogliere oggetti.
4. Esci e rilancia `./body-demo.sh` senza `--fresh`: posizione e condizioni
   sono quelle del save CDDA; la scheda torna consultabile.

Entrambe le demo conservano sessioni separate dai salvataggi normali.
Queste checklist si ripropongono alla fine dell'implementazione; nessuna
approvazione manuale è stata ricevuta per raccolta o HUD/scheda.
