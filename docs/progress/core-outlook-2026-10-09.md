# Stato e stima del lavoro restante — 2026-10-09

Recap richiesto prima di ripartire, successivo alla validazione manuale di
tiro, trasferimenti, UX-01 e UX-02. [Riscontro e limiti](../source/core-ux-validation-2026-10-09.md).
Sorgente di produzione invariata rispetto a `048ca366ee9a2ee888b69a6d3c5b098517a4f67d`;
CWM 2.16 e coppia runtime già installata. I bug nuovi non sono ancora corretti.

Questo recap conserva lo stato **precedente alla consegna UX-03**. La hotbar,
le correzioni mirate e il default continuo 4× sono ora disponibili in CWM 2.17;
[stato corrente](../../IMPLEMENTATION_STATUS.md) e
[consegna UX-03](../fixes/interactive-quickbar.md) descrivono evidenze e limiti.
Non si ricalibrano le percentuali solo per un task: la prossima rivalutazione
seguirà contenitori esterni e i riscontri manuali rimasti.

## Come leggere le stime

Stime ingegneristiche di lavoro, non percentuali misurate di codice o test.
Le feature già presenti nel core CDDA non sono automaticamente accessibili
nella versione 3D. La percentuale considera integrazione, UI, grafica e
verifica delle parti necessarie. Non usare M5/9 come misura dell'avanzamento:
sono state anticipate molte fette M7 mentre M6/veicoli è ancora aperta.

Un ciclo significa una fetta circoscritta implementata, ricostruita,
verificata e installata, con eventuali test dell'utente nel backlog.
Può richiedere più turni; un messaggio «continua» non garantisce un ciclo.
Non stimare ore o token con precisione senza misure dei futuri task.
Gli intervalli comprendono correzioni e integrazione; vanno ricalibrati dopo
hotbar/contenitori esterni, poi dopo il primo veicolo guidabile.

| Traguardo | Stima attuale | Lavoro restante indicativo |
|---|---|---|
| Core minimo giocabile autonomamente: esplorare, raccogliere, equipaggiarsi, combattere, sopravvivere, curarsi e produrre; controlli comprensibili e avvio normale coerente | **75–85%**, riferimento 80% | **8–14 cicli** sostanziali |
| Intero ambito base approvato nei 15 questionari, incluse famiglie di meccaniche e adattamenti 3D | **20–30%**, riferimento 25% | **60–120+ cicli**, forte incertezza |

Le stime non sono additive: il core è contenuto nel prodotto completo.
Grandi mod future, multiplayer e modelli individuali per ogni oggetto/creatura
non sono inclusi nell'intervallo del base. Il prodotto completo include una
presentazione riconoscibile per famiglie e tutte le meccaniche approvate;
non equivale a perfezione artistica né a tutte le future versioni di CDDA.

## Già utilizzabile

Startup/load canonico, IPC/sessione/resync, terreno B e strutture,
apertura/chiusura, connessioni verticali, acqua con decisioni native;
movimento continuo CDDA a 4× quando abilitato, corsa/posture/pausa;
creature con identità e persistenza, raccolta, HUD e scheda corporea;
inventario/equipaggiamento, cibo/bevande, medicazioni, crafting guidato;
melee, armi da fuoco/mira/ricarica; quantità/drop/trasferimenti posseduti;
layout UX-01 e ritorno dopo costi nativi UX-02. Queste fette non chiudono
ogni famiglia di meccaniche; audio, rig e alcuni placeholder sono incompleti.
Sincronizzati 27 batch: 1.080 record, 396 rappresentazioni runtime, 89 texture.

## Core: pacchetti rimanenti

1. UX-03: hotbar assegnabile/rimuovibile, icone HUD e mano autorevole,
   focus ricerca aggiornato, quantità/errori leggibili e acqua pulita corretta.
2. Contenitori esterni e raccolta di quantità selezionate, sorgenti annidate
   chiaramente navigabili; poi fonti di liquidi e travasi essenziali.
3. UX-04: conferme leggibili e scelta medica visiva. UX-05: recenti/preferiti
   nativi per crafting. Lettura e strumenti/usi essenziali ancora mancanti.
4. Attività lunghe: accelerazione generale, stop e interruzioni con mondo
   simulato e costi preservati; feedback Indossa/Togli comprensibile.
5. Mira su RMB mantenuto, arma visibile, rinculo leggibile; personaggio 3D,
   UV/animazioni di base e primi suoni collegati a esiti autorevoli.
6. Percezione/panorama: distanza, nebbia, buio e immersione leggibili senza
   rivelare creature o terreno ignoti. Dossi naturali restano rinviati.
7. Inglese predefinito e italiano WIP coerenti; consegna normale tramite
   start.sh, default continuo 4× esplicito e vecchie modalità selezionabili.
8. Consolidamento: regressioni del normale ciclo su mondo non-demo,
   casi eccezionali UX-02, salvataggi e ripresa, prestazioni con popolazioni
   reali. Full SAVE-001 e certificazione M5.5 rimangono gate separati aperti.

I pacchetti possono richiedere più cicli o accorparsi se i cambiamenti sono
piccoli. Core minimo non richiede subito veicoli, commercio o accampamenti.

## Dopo il core: ambito completo

- M6 veicoli: identità/parti, geometria, guida e collisioni autorevoli,
  prototipo da confrontare; officina, passeggeri/cargo/danni, acqua e volo.
- M7 interazioni estese: arrampicata/salti e scale continue da rivalutare;
  tasche/sigilli/liquidi, farmaci e medicina avanzata; crafting/lettura/
  smontaggio completi, armi/mode/reach/bersagli neutrali.
- Mappe e memoria, missioni/diario, dialoghi/scambi, compagni e regole,
  accampamenti/spedizioni; costruzioni, zone, coltivazione e reti elettriche.
- Creazione personaggio/mondo guidata e avanzata; abilità/proficienze,
  mutazioni/bionica e capacità attive con corpo/equipaggiamento coerenti.
- Bestiario e cadaveri/revival/macellazione, animali/pesca/foraging,
  trappole/scasso/demolizione, fuoco/fumo/gas/campi, computer e fenomeni.
- M8/M9: benchmark popolati, ottimizzazione misurata, conformance completa,
  contenuti/licenze, diagnostica opzionale e packaging Linux/Windows.

## Prossima consegna

UX-03 e correzioni correlate, installate e provate attraverso start.sh su
salvataggi isolati. Il prossimo intervento non promette di correggere nello
stesso ciclo anche tutto l'audio, il rig e il panorama. Le rispettive prove
manuali verranno aggiunte solo quando quelle funzionalità saranno consegnate.
