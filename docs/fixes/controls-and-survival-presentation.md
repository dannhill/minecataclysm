# Comandi familiari e presentazione della sopravvivenza

Risponde al [riscontro](../source/playable-core-feedback-2026-10-08.md): le quattro
feature precedenti hanno accettazione manuale completa. Le nuove modifiche
sono verificate separatamente, senza ripetere come pending quelle accettate.

## Comportamento

Ctrl sinistro mantenuto richiede RUN nativo; Shift mantenuto richiede CROUCH;
il rilascio ritorna alla postura latched (normalmente cammino). P alterna
prone/cammino. Se si tiene Ctrl+Shift, accovacciarsi ha precedenza; rilasciare
Shift ripristina la corsa finché Ctrl rimane premuto. P interrompe le posture
mantenute; occorre rilasciare/ripremere quei tasti per riattivarle. Se si tiene
Ctrl partendo proni, il rilascio torna proni: non cancella il toggle P.
Richieste native, ACK e world result confermati governano la postura effettiva;
nessuna velocità/collisione/HP è calcolata da Luanti. Un rilascio mentre il
comando precedente è in corso aggiorna l'intenzione, non accoda due azioni.
Esaurimento/rifiuto RUN richiede un nuovo press, senza retry continuo.
Menu/pausa/recovery consumano i press senza riproporli. Il rilascio di una
postura mantenuta ripristina il cammino alla ripresa; P canonico resta nel save.

Shift conserva chiusura porte/finestre e discesa. Azioni contestuali vengono
processate prima delle nuove richieste gratuite di postura, così una pressione
simultanea non occupa lo slot del clic/Spazio con un cambio di postura.
Se OPEN/CLOSE incontra solo il roundtrip di una postura, si conserva al massimo
un clic per un secondo: portata/stato rivalidati da CDDA, annullamento su
menu/pausa/recovery/disconnessione. Il debounce delle interazioni già presente
(200 ms) resta applicato. Altre azioni non vengono accodate da questa regola.
I tasti sono configurabili (`keymap_cdda_run/crouch/prone/body`), le etichette
leggono la configurazione. `cwm_run_toggle` e `cwm_crouch_toggle` sono bool,
default false, nel catalogo impostazioni Luanti. Per il launcher si possono
salvare in `~/.minetest/minetest.conf` o nel file fornito da `LUANTI_CONFIG`:

```ini
cwm_run_toggle = true
cwm_crouch_toggle = true
```

## Pausa e visuale

Un orologio di presentazione cumulativo governa le texture animate dei nodi,
i timer/delta shader e i pickup. Pausa nativa, menu (anche modalità comandata
dalle azioni), decisioni e resync fermano la fase; alla ripresa niente catch-up.
Nel continuo segue la scala globale nativa. L'interpolazione delle entità/
veicoli si ferma nei medesimi casi. Coordinate/costi restano CDDA.
Nell'acqua bassa il guado non abbassa due volte gli occhi del personaggio
prono: altezza risultante uguale allo sdraio sul pavimento (0.825 blocchi sopra
il centro tile). Nuoto/immersione profondi conservano la presentazione precedente;
la loro leggibilità resta lavoro futuro, non coperta da questo fix.

La scheda H usa elenchi di label scorrevoli, senza tabelle selezionabili:
S non avvia più la ricerca alternata Sete/Sonno. Il rifiuto RUN spiega che
occorre riprendere fiato o controllare le condizioni delle gambe.

## HUD e oggetti

Asset Mineclonia originali: cuori, icone armatura per le parti, icone exhaustion
per stamina e cibo per fame. H mostra tutte le parti e temperature; HUD mostra
separatamente testa/torso vitali, stamina e bisogni. Cinque icone sono i cinque
segmenti del display CDDA: pipe piena, slash metà, colon frazione minima,
dashes vuoti. Non si ricostruiscono gli HP esatti da questa quantizzazione.
Malattie/condizioni non vengono mescolate con la salute; una media degli arti
potrebbe nascondere una ferita mortale alla testa/torso. È una raccomandazione
esplicita, non l'approvazione dedotta della formula proposta dall'utente.
L'elenco completo delle malattie/effect e le interazioni mediche restano
pianificati; questa fetta non ne implementa la UI completa.
Fame resta la descrizione percepita, anche `-` quando non esiste un'indicazione;
non si inventa un'equivalenza calorie → cosce di pollo Minecraft.

La barra in basso mostra i primi nove oggetti dell'export posseduti nativo
(anche equipaggiati/annidati), icone registrate e fallback, con conteggio del
resto. È una vista, senza selezione/equipaggiamento tramite numeri/rotella.
Il prossimo equipaggiamento rapido deve usare item location/tasche e costi
nativi; non è implementato implicitamente dalla hotbar locale.
Le immagini GUI vengono riusate, non allocate ogni frame. Durante la perdita
IPC le icone si nascondono e il pannello segnala lo stato non sincronizzato.
Provenienza e checksum in `game/mods/cdda_items/status_assets.json`, notifiche
media nella stessa mod. Nessun gameplay Lua Mineclonia aggiunto.

## Prova manuale

`./controls-demo.sh --fresh`: scena privata con acqua bassa allo spawn,
sasso davanti e finestra a destra. Non modifica i mondi normali.
[Checklist breve salvata](../validation/pending-manual.md).

## Evidenze

Artifacts: `artifacts/controls-hud-20261008/`. Identità sorgenti, comandi,
binari e risultati nel registro `controls-and-survival-presentation-evidence.json`.
I controlli sono mirati: nessuna certificazione globale M5.5/SAVE-001.
