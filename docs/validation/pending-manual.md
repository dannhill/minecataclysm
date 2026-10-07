# Validazioni manuali da riproporre

L'utente il 2026-10-08 non può provare il gioco e chiede di rinviare la
validazione della raccolta, proseguendo autonomamente con una feature
essenziale indipendente. **Rinviata non significa approvata.** Riproporre
questa checklist alla consegna del successivo HUD/scheda corporea, insieme
alla sua checklist. L'inventario interattivo non è anticipato da questa scelta.

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

## HUD e scheda corporea — IN IMPLEMENTAZIONE

Feature indipendente dalla raccolta. Checklist e comando isolato saranno
aggiunti alla consegna; non è richiesta una prova durante l'implementazione.
