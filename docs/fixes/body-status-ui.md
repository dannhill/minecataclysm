# HUD di sopravvivenza e scheda corporea

Slice essenziale del playable core, indipendente dalla nuova GUI di raccolta.
L'utente il 2026-10-08 autorizza questa prosecuzione autonoma e rinvia il test
della raccolta. Entrambe le [checklist](../validation/pending-manual.md) restano
in attesa: nessuna accettazione manuale è dedotta dai test automatizzati.

## Comportamento

Il pannello in basso a sinistra mostra stamina, salute di testa/torso e i
bisogni segnalati da CDDA. **H** apre una scheda di sola lettura con tutte
le parti principali del corpo, salute e temperatura, oltre a fame, sete,
sonno, dolore percepito, affaticamento, temperatura generale e morale.
I due elenchi scorrono se necessario. **Esc** o **Torna al gioco** chiude.
Il tasto è configurabile con `keymap_cdda_body` (default `KEY_KEY_H`).

La scheda mette in pausa il tempo nativo nella modalità continua e rispetta
la pausa manuale F7 alla chiusura. Nessuna azione CDDA è assegnata per leggere
la scheda; niente cure, equipaggiamento o trasferimenti impliciti. In modalità
scandita dalle azioni non fa avanzare il tempo. Una perdita IPC/reset/resync
chiude la scheda: occorre riaprirla dopo lo stato completo confermato.
Il HUD segnala esplicitamente uno stato non sincronizzato/non disponibile.
I cuori, la barra d'ossigeno e la hotbar del server Luanti locale vengono
esclusi quando il bridge possiede il personaggio: non rappresentano CDDA.

## Origine e conoscenza

`CwmMapExporter::export_avatar_status()` consulta le funzioni native in
`cdda/src/display.cpp` e `output.cpp`. Le barre corporee seguono quelle di
`Character::extended_description()` in `character.cpp`: nessun valore esatto
di HP viene esportato dalla nuova scheda. Il dolore usa la variante Character
di `display::pain_text_color()`, inclusi analgesia e precisione dopo visita
nativa; fame e sete usano le rispettive percezioni, non formule Luanti.
Una descrizione nativa vuota resta vuota nel protocollo; la scheda la mostra
come `-`, spiegandone il significato. Etichette in italiano e valori nella
lingua configurata di CDDA possono coesistere; localizzazione completa rinviata.

CWM **2.6** aggiunge `avatar_status` a ogni pubblicazione, sia completa sia
incrementale. Le stringhe/liste sono limitate e gli ID unici; uno stato
malformato non entra nel renderer. I due runtime devono usare la stessa
versione. Colori nativi tradotti in una palette leggibile di presentazione;
nessuna regola di salute o progressione viene duplicata nel client.

## Confine

È il primo HUD/scheda corporea, non l'intera medicina. Diagramma anatomico
grafico, condizioni/ferite con dettagli clinici, trattamenti espliciti con
oggetti reali, vestiti/impedimenti, nutrienti, bagnato e grafici avanzati
restano nel piano. Non vengono rivelate malattie nascoste o vitamine.
La scheda fotografa l'ultimo stato confermato all'apertura; la pausa nativa
deve essere ricevuta dal coordinator. Non è una fonte autonoma di save.
La grande varietà di anatomie e le risoluzioni molto piccole richiedono
ulteriore validazione visiva. M5.5 resta FAILED; SAVE-001 completo resta aperto.

## Prova manuale

`./body-demo.sh --fresh` usa una copia isolata creata dal core CDDA pinned
originale: ferite a testa/braccio sinistro, sete, stanchezza, stamina ridotta,
nessuna pila a terra o creatura ostile. Movimento continuo 4x.
Senza `--fresh` riprende la stessa sessione, senza cancellare le precedenti.
Il HUD/scheda è disponibile anche in `start.sh` e `pickup-demo.sh`.
Le quattro prove sono nella [checklist congiunta](../validation/pending-manual.md).

## Verifica in corso

Artefatti: `artifacts/playable-core-body-ui-20261008/`. Test nativi della
proiezione e dell'analgesia, test di rifiuto/resync di stato malformato, prova
GUI reale su fixture indipendente in modalità ordinaria e continua, controllo
save con lettore linkato al core pristine. Esiti, sorgenti e binari saranno
registrati alla conclusione della verifica.
