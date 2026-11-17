# Core minimo giocabile e verificato — stima 2026-11-15

Stima ingegneristica dell'LLM richiesta direttamente dall'unico sviluppatore,
basata su roadmap, contratti e sorgenti correnti e sui suoi risultati manuali.
Non è una nuova esecuzione dell'audit, una certificazione o un PASS umano.

## Traguardo e percentuali

Per il core minimo Linux con verifica finale inclusa: **85–90%**, quindi
**10–15% residuo** come stima di avanzamento. La presenza delle funzioni del
core resta stimata intorno al **95%**, nel precedente intervallo93–96% che
escludeva il collaudo umano. Le due percentuali hanno un denominatore diverso;
non derivano dal numero di checklist, righe o asserzioni e non predicono una
riduzione proporzionale del tempo residuo. Non aumentare il core a ogni PASS.

Il traguardo è il ciclo esplorazione → risorse → equipaggiamento → bisogni,
acqua/riposo/cure → lavoro/crafting/lettura → combattimento → salvataggio,
caricamento e recupero, utilizzabile nella normale partita3D. Conservare il
perimetro minimo: veicoli completi, accampamenti, tutti i servizi/mod/EOC,
ogni bionica/mutazione e grafica definitiva rimangono fuori da questo traguardo.

Il 100% richiede funzioni essenziali completate, nessun blocco noto del ciclo
minimo, prove automatiche riproducibili della build effettiva, verifica completa
di preservazione del salvataggio/ripristino e prove finali in mondi normali con
carico reale. Le accettazioni umane delle funzioni esistenti non sostituiscono
le verifiche tecniche di conformità. M5.5 storico FAILED / SAVE-001 completo
OPEN non vengono promossi dai PASS locali raccolti successivamente.

## Lavoro ancora necessario

1. Usi nativi essenziali degli oggetti non esposti dall'interfaccia; distinguere
   quelli necessari al ciclo minimo dal catalogo completo degli usi CDDA.
   L'enum EquipmentAction corrente espone otto azioni specializzate, senza una
   generica attivazione completa degli oggetti.
2. Risultati liquidi delle ricette/purificazione con gestione obbligatoria sicura
   su annullamento, disconnessione e shutdown. Il controllo corrente in
   `cwm_crafting.h` rifiuta ancora risultati liquidi/gassosi; la raccolta e il
   travaso opzionale esistenti non chiudono quel percorso.
3. Chiudere LIQ-FB-01 nel loop acqua, predisporre i casi negativi mancanti e
   consolidare le transizioni di attività/menu/decisione. NPC-SCROLL-01 resta
   una miglioria UX; non far crescere indefinitamente il minimo per rifiniture.
4. Verifica finale di salvataggi/ripristino, perdita di connessione e prestazioni
   in mondo popolato, poi playtest del ciclo completo fuori dalle sole demo.

Budget indicativo: **4–7 interventi tecnici sostanziali**, comprensivi delle
verifiche di integrazione, e **2–4 cicli di riscontro/fix** in base ai difetti
emersi. Sono unità di lavoro, non promesse di un messaggio ciascuna o scadenze.
Un difetto strutturale nel gate dei salvataggi può allargare questo intervallo.

## Quanto collaudo umano resta

Il backlog corrente è **39 PENDING**, compresi i quattro appena proposti.
Di questi,15 sono nei gruppi modelli/animazioni/feedback (3+2+10),3 sono Windows,
21 negli altri gruppi. Sono una classificazione dei temi, non una certificazione
che i15 siano tutti cosmetici o rinviabili: audio, danni e visibilità possono
comunque rivelare blocchi. Non equiparare39 casi a39 feature mancanti.

Assumendo **5–10 minuti per caso**, senza nuovi difetti o difficoltà a riprodurre
il trigger:39×5–10 =195–390 minuti, cioè **3h15–6h30** per l'intera checklist
esistente. Il caso non riprodotto non va forzato o convertito in PASS. Correzioni,
nuove verifiche e preparazione delle scene negative sono tempo aggiuntivo.

Per il collaudo finale proporre inoltre **due sessioni da30–60 minuti** nel
gioco normale, con un ciclo di sopravvivenza e salvataggio/caricamento, senza
espandere il minimo. Esaurire tutte le39 prove e fare quelle sessioni vale
circa **4h15–8h30 di tempo umano**, alle ipotesi indicate, non di sviluppo.
Il sottoinsieme indispensabile alla chiusura del core va scelto per rischio;
il resto rimane documentato senza accettazioni implicite.

Windows richiede anche un pacchetto aggiornato alla funzionalità Linux e le
tre prove dedicate già comprese nel conteggio39: il vecchio installer CWM2.26
non è una verifica della build Linux CWM2.37 attuale. La percentuale85–90%
si riferisce al core Linux, senza dedurne lo stato del pacchetto Windows.

Il lavoro successivo deve tornare alle omissioni funzionali essenziali,
alternando gruppi di2–4 verifiche mirate e implementazione; svuotare il backlog
da solo non implementa le due famiglie funzionali ancora mancanti.

Fonti: [stato](../../IMPLEMENTATION_STATUS.md), [piano](../../IMPLEMENTATION_PLAN.md),
[backlog](../validation/pending-manual.md), [contratto liquidi](../design/native-liquids.md),
[precedente stima funzionale](core-outlook-2026-10-23.md).
