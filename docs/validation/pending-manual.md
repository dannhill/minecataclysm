# Validazioni manuali del playable core

L'utente il 2026-10-08 ha eseguito e approvato tutti i quattro punti di
ciascuna delle quattro checklist. Il [riscontro](../source/playable-core-feedback-2026-10-08.md)
supera i rinvii precedenti. Le checklist sotto conservano i comandi della
versione provata (R/X/P); le nuove preferenze Ctrl/Shift sono un adattamento
successivo e avranno una verifica separata.

## Raccolta — VALIDATA: 1–4 PASS

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

## HUD e scheda corporea — VALIDATA: 1–4 PASS

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
Entrambe le checklist sono ora accettate dall'utente.

## Corpo a corpo puntato — VALIDATA: 1–4 PASS

Feature indipendente dalle altre due: `./combat-demo.sh --fresh`. Mazza già
impugnata e zombie ostile subito davanti, immobilizzato solo nella scena di
prova. **E** riconosce la minaccia; **F7** mette in pausa/riprende.

1. Punta lo zombie: nome e suggerimento di attacco; clic sinistro per un colpo.
   Tieni poi premuto: un solo attacco, senza raffica. Ripeti con nuovi clic.
   Se la mazza lo respinge, riavvicinati: i colpi fuori portata sono rifiutati.
2. Metti in pausa con F7 e clicca: niente attacco. Riprendi: nessun colpo
   ritardato dal clic fatto durante la pausa. Il mirino nel vuoto non attacca.
3. Uccidi il bersaglio con nuovi clic: modello rimosso, cadavere nativo a terra.
   Nessun movimento verso il bersaglio causato dal clic.
4. Esci e rilancia `./combat-demo.sh` senza `--fresh`: bersaglio morto/cadavere
   coerenti con il save. Questa prova non richiede raccolta né scheda H.

Checklist accettata dall'utente, compreso il mancato avvicinamento automatico.

## Corsa e posture native — VALIDATA: 1–4 PASS

Quarta feature indipendente: `./posture-demo.sh --fresh`, copia isolata con
area iniziale priva di bersagli predisposti e senza raccolta obbligatoria;
movimento continuo 4x già approvato. Gli spawn fissi nella bolla iniziale sono
rimossi dalla sola fixture; esplorare oltre può incontrare creature native.

1. Premi **R**: pannello «Corsa», WASD più veloce e consumo maggiore di stamina.
   Ripremi R: «Cammino». Tenere R premuto non deve alternare ripetutamente.
2. Premi **X**: «Accovacciato», visuale più bassa e movimento più lento.
   Ripremi X per rialzarti; **P** dà «A terra», visuale ancora più bassa e
   strisciamento più lento. Ripremi P per camminare. Shift resta modificatore
   per chiusura porte/finestre e discesa, senza cambiare postura.
3. **F7**, poi R/X/P: niente cambio durante la pausa e niente comando ritardato
   alla ripresa. Le nuove posture non devono spostarti/teletrasportarti.
4. Lasciati accovacciato o a terra, esci e rilancia `./posture-demo.sh` senza
   `--fresh`: postura e posizione conservate. Se corri fino a esaurire la
   stamina, CDDA deve interrompere la corsa; non puoi forzare R mentre affannato.

Altezze di visuale sono un primo adattamento 3D; le animazioni del corpo/rig
in terza persona verranno completate separatamente. Tutte e quattro le prove hanno accettazione manuale esplicita.


## Adattamenti comandi e presentazione — VALIDATA: 1–4 PASS

Le quattro checklist sopra sono già accettate. Anche le quattro modifiche
successive sono state approvate esplicitamente dall’utente: `./controls-demo.sh --fresh`
(copia isolata con acqua bassa alla partenza e sasso davanti).

1. **Ctrl sinistro** tenuto: corsa; rilascio: cammino. **Shift** tenuto:
   accovacciato; rilascio: cammino. **P** resta toggle. In pausa F7 i tasti
   non devono produrre cambi ritardati. Le preferenze `cwm_run_toggle` e
   `cwm_crouch_toggle` nelle impostazioni consentono il comportamento toggle.
   Shift+tasto destro e Shift+Spazio conservano chiusura e discesa native.
2. **H**: bisogni/parti leggibili con icone; premere S più volte non seleziona
   Sete/Sonno. Il sasso e l'acqua restano fermi durante la pausa e riprendono
   alla chiusura. La pausa F7 resta attiva dopo aver richiuso H.
3. **P nell'acqua bassa**: la visuale resta sopra la superficie, senza il
   vuoto nella metà inferiore; P per rialzarsi. Questa prova non comprende
   ancora la presentazione completa dell'immersione profonda.
4. HUD: cuori separati testa/torso, icone stamina, fame descritta da CDDA,
   oggetti posseduti visibili nella barra. La barra è ancora una vista:
   numeri/rotella non equipaggiano quegli oggetti. Il toggle sdraio persiste
   nel save. Il rifiuto della corsa deve avere una spiegazione comprensibile.


## Ultimo ritocco HUD/acqua — nessun nuovo gate manuale

Su richiesta successiva: X predefinito per sdraiarsi, lieve discesa della
visuale proni in acqua bassa, HUD di icone senza pannello nero. La checklist
precedente conserva P e il vecchio HUD come descrizione della versione
validata. L’utente richiede di proseguire dopo questo ritocco senza attendere
un’ulteriore validazione estetica. Non si deduce un PASS manuale del nuovo HUD.
Eventuali osservazioni potranno essere raccolte durante le prossime feature.

## Inventario ed equipaggiamento — DA PROVARE, rinviato su richiesta

L'utente non puo testare ora (2026-10-08); queste prove restano pendenti.
Non costituiscono un blocco tecnico per la consegna di questa fetta.
Avvio dalla directory del progetto: `./equipment-demo.sh --fresh`.
Copia isolata: mazza impugnata, zaino indossato; cappello, bandana e due
sassi nelle tasche. `I` apre l'inventario anche nel gioco normale.

1. **I**: griglia, nomi al passaggio del mouse, filtri e ricerca, dettaglio
   dell'oggetto selezionato con provenienza/tasche/capacita. Tempo fermo,
   WASD non muove; Esc chiude senza equipaggiare. Le icone generiche sono
   fallback di presentazione, non oggetti diversi da quelli CDDA.
2. Seleziona cappello: **Indossa**, poi riapri I e **Togli**. Seleziona
   mazza: **Riponi** e scegli la destinazione nativa con il numero mostrato;
   prova anche **Annulla**. Poi **Impugna** un sasso: solo quello diventa
   impugnato. I vincoli e i tempi restano nativi; nessuno switch rapido gratis.
3. Con F7 in pausa, prova un'azione: non deve partire ne venire eseguita
   quando riprendi. Chiudere I non deve togliere la pausa F7. Per togliere
   lo zaino senza lasciarlo a terra, riponi prima l'oggetto impugnato:
   CDDA puo impugnare lo zaino completo; **Indossa** lo rimette con i contenuti.
   Se manca spazio e hai gia qualcosa in mano, CDDA puo lasciare lo zaino
   a terra con i contenuti: e comportamento nativo, non una cancellazione.
4. Lascia cappello indossato e un sasso impugnato; esci e rilancia
   `./equipment-demo.sh` senza `--fresh`. Controlla equipaggiamento e
   contenuti: nessuna perdita, duplicazione o ricomparsa delle vecchie copie.

Quantita parziali, trasferimenti mirati tra tasche/contenitori, apertura di
tasche sigillate e hotbar interattiva vengono dopo: non sono implementati
in questa prima fetta. [Dettagli e verifica tecnica](../fixes/native-equipment.md).


## Cibo e bevande nativi — DA PROVARE, rinviato su richiesta

La checklist inventario/equipaggiamento sopra rimane pendente. Non si
trasformano le verifiche automatiche in accettazione grafica dell'utente.
Avvio isolato: `./consumption-demo.sh --fresh`. Zaino gia fornito dal core
nativo con due mele fresche, una marcia, una bottiglia con quattro porzioni
d'acqua pulita e un sasso. La stessa funzione e disponibile con I nel gioco.

1. **I**, scegli una mela fresca: dettagli e **Mangia**; scegli l'acqua nella
   bottiglia: **Bevi**. Il sasso non deve offrire Consuma. Leggere mantiene
   tempo/personaggio fermi. Mangia/Bevi chiudono il menu e avviano un consumo
   con indicazione di progresso; una sola porzione si toglie alla fine.
2. Durante una mela premi **I**: il progresso si ferma col menu; **Interrompi
   consumo** torna al gioco, conservando la porzione non ancora consumata.
   Avvia poi nuovamente Mangia e lascia terminare. La durata della nuova
   richiesta segue il comportamento CDDA del pin, senza rimborso del tempo
   gia trascorso. I bisogni si aggiornano attraverso digestione nativa, non
   con una cura istantanea inventata dalla GUI.
3. Seleziona la mela marcia: avviso nel dettaglio, conferma nativa dopo
   Mangia. Scegli **No** con il numero mostrato: mela conservata, nessuna
   attivita bloccata. Con **F7** in pausa, prova Mangia/Bevi: niente comando
   ritardato dopo la ripresa; chiudere I conserva la pausa F7.
4. Bevi una porzione e mangiane una, esci e riavvia `./consumption-demo.sh`
   senza --fresh: bottiglia/quantita e bisogni restano coerenti, senza
   duplicazioni. Puoi anche uscire durante un consumo: il save mantiene
   l'attivita nativa; al rientro il tempo riprende da quel lavoro residuo.

Farmaci/medicazioni, bere da fontane, aprire tasche sigillate, scegliere
quantita e travasare richiedono le prossime fette. Le icone mancanti restano
fallback con nomi CDDA. [Dettagli tecnici](../fixes/native-consumption.md).
