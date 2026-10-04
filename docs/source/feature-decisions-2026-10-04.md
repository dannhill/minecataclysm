# Decisioni approvate dai 15 questionari

Fonte: risposte e precisazioni dell'utente nella conversazione Codex del
2026-10-04, dopo lettura dei sorgenti locali dei tre progetti. Integrano la
specifica precedente e prevalgono sulle ipotesi modificate. Il [registro JSON](feature-decisions-2026-10-04.json)
conserva i dettagli raccolti; il [piano completo](../../IMPLEMENTATION_PLAN.md)
definisce dipendenze e verifiche. Sono direttive, non attestazioni di feature
già implementate.

## 1. Fondazioni

Meccaniche CDDA profonde, default guidati, gestione ripetitiva automatizzabile
e controllo manuale/dettagli progressivi fino a esperienza vicina alla nativa.
CDDA integrato autorevole; estensioni spaziali autorizzate, documentate, testate
e provabili personalmente dall'utente. Prototipi griglia interpolata e tile +
offset continuo CDDA; orientamento naturale, arresto interno e costi accumulati
per la variante ibrida. La scelta definitiva dipende dal confronto giocabile.
Portata, ostacoli e geometria visibile devono essere coerenti.

## 2. Comandi e asse verticale

Azione rapida, ruota compatta a posizioni stabili, elenco completo, shortcut
riassegnabili. Walk/run/crouch/prone diretti, corpo/camera corrispondenti;
velocità/rumore/fatica CDDA integrato, adattamenti espliciti consentiti.
Scale fluide, climb/vault contestuali, nuoto/immersione. Salti nativi contestuali
e abilità acquisite inclusi; costo effettivo di `iexamine::ledge` da verificare
perché non direttamente addebitato nel ramo di successo. Salto fisico libero
universale non richiesto.

## 3. Inventario

Vista unificata icone/categorie/ricerca e sorgente reale, vista avanzata delle
tasche annidate. Selezione automatica nativa delle tasche con controllo manuale.
Conservare massa/volume/lunghezza/rigidità/liquidi e costi d'accesso.
Trasferimenti a due pannelli: quantità scelte in pausa, poi attività native
temporizzate e interrompibili.

## 4. Corpo, vestiti, medicina

Sopravvivenza completa: calorie/digestione/vitamine, sete/sonno/stanchezza,
stamina, temperatura/bagnato, morale/dolore e condizioni. HUD essenziale e
dettagli secondo conoscenza. Vestiti/equipaggiamento riconoscibili inizialmente
per categoria/colore; statistiche, strati e impedimenti specifici restano completi.
Medicina: parte → scelta esplicita di oggetto reale → conferma; anche oggetto →
parte disponibile. Filtrare oggetti pertinenti e spiegare effetti conoscibili;
nessuna selezione automatica del trattamento o piano automatico di cura.

## 5. Crafting e attività

Catalogo visivo delle ricette note, libri/aiutanti e requisiti nativi. Mostrare
materiali mancanti e sottoricette conosciute collegate; giocatore avvia ogni
lavoro, batch/preferiti disponibili. Confermare componenti concreti e fonti;
alternative modificabili, preferiti/equipaggiati protetti dalla selezione automatica.
Attività lunghe accelerate automaticamente, progresso e stop/rallentamento;
pausa sulle distrazioni native rilevanti. Il mondo CDDA continua a essere simulato.

## 6. Combattimento

Melee puntando/attaccando; difese passive, arti marziali e movimento nativi.
Nessuna nuova parata/capriola universale. Mira assistita predefinita e mirino
libero configurabile nella prima versione completa, stessi costi/precisione,
rinculo/dispersione/traiettoria/danni autorevoli. Nuova minaccia percepita:
autopausa, poi ripresa in tempo reale con pausa manuale. Combattimento opzionale
scandito dalle azioni richiesto se ragionevole da implementare: fattibilità da
verificare nel prototipo. Scegliere in pausa non migliora la mira gratuitamente.

## 7. Percezione e mappe

Percezione CDDA indipendente dal cono camera; indizi contestualizzati fuori
inquadratura. Ribilanciamento per nuovo campo visivo rinviato. Audio direzionale
e descrizioni/segnali discreti opzionali con incertezza e udito nativi.
Mappe locale/generale, annotazioni, percorsi e minimappa opzionale; quella
grafica è già abilitata nel preset CDDA pinned. La mappa locale dedicata adatta
la vista dall'alto, senza nuovo oggetto obbligatorio. Distinguere informazioni
percepite, terreno ricordato e overmap scoperta.

## 8. Creature e cadaveri

Varietà del bestiario base, modelli condivisi per famiglie/taglie/varianti
riconoscibili; asset individuali affinati dopo. AI, atteggiamenti, evoluzione,
special attack e preavvisi CDDA. Cadaveri, revival, pulp, butcher/dissect,
strumenti/rischi/prodotti/tempi nativi. Manuale predefinito, automatismi opzionali.

## 9. NPC e accampamenti

Dialoghi in pausa con testo completo, cronologia, prove/conseguenze; refresh
non riapplica effetti d'ingresso. Scambi a due pannelli con offerta complessiva
confermata, prezzi/credito/proprietà/contenitori/capacità nativi, effetto unico.
Compagni: comandi rapidi, profili leggibili e regole individuali complete,
condizioni di comunicazione native. Diario/target e indicazioni HUD facoltative
solo verso destinazioni note. CDDA ha già diario e direzione sulla minimappa:
HUD 3D è adattamento; precisione del tempo residuo conserva requisito orologio.
Accampamenti inclusi: pannello di risorse/ampliamenti/incarichi/spedizioni,
astrazioni native degli NPC lontani.

## 10. Base, costruzioni, impianti

Strutture CDDA in 3D con anteprima/validazione, progetti multi-casella e stime
dei materiali, lavoro progressivo/interrompibile. Zone di smistamento/farm/build
visibili, lavoro effettivo di personaggio/NPC. Apparecchi/reti elettriche nativi
con UI di dispositivo/connessioni, nascondendo il riuso interno di vehicle.

## 11. Veicoli

Prototipi guida nativa interpolata e continua autorevole CDDA; scelta utente
dopo prova di manovre/collisioni/abilità. Officina con puntamento e vista a
strati, componenti sovrapposti e tempi/requisiti nativi. Copertura terra → acqua
→ volo, tutte le categorie previste.

## 12. Creazione e progressione

Percorso guidato/preset e editor completo nativo. Pratica/teoria/competenze,
libri/addestramento conservati. Mutazioni e bionica complete, con costi/rischi,
chirurgia/energia/attivazioni, taglia/sensi e compatibilità corpo/vestiti.
Capacità passive/attive leggibili, shortcut; geometria/camera coerenti con
effetti fisici, dettaglio estetico progressivo.

## 13. Attività e fenomeni

Farm/harvest, pesca/foraging, cura animali/mungitura/tosatura/cavalcature,
cucina/conservazione, trappole/scasso/demolizione nativi tramite interfacce comuni.
Fuoco/fumo/gas/campi rappresentati secondo stato e conoscenza. Liquidi:
fonti/contenitori/travasi/carburanti/nuoto/fenomeni nativi con aspetto 3D,
nessuna nuova fluidodinamica voxel. Computer: pannello leggibile delle funzioni,
prove/tempi/conseguenze nativi, nessun nuovo minigioco di riflessi.

## 14. Preset e salvataggi

Nuovi mondi con preset raccomandato valido locale, mod/opzioni esplicite e
configurazione avanzata; mondi esistenti conservati. Il preset distribuito usa
dda/no_npc_food/personal_portal_storms/no_fungal_growth, con ID legacy/invalidi
risolti dal loader nativo. Questo prevale sull'ipotesi generica precedente di
bisogni NPC sempre attivi. Grandi mod dopo il base, verificate separatamente;
preservare EOC/spell generici, usati anche da bionica e mutazioni.
Quick save/load/autosave, morte definitiva e gestione mondo configurabile
nativi, politica dichiarata alla creazione (WORLD_END pinned default reset).
Nessun nuovo recupero post-morte richiesto.

## 15. Ritmo normale

Default 1 secondo reale = 1 secondo simulato, velocità globale regolabile
applicata a tutti i sistemi, incluse micce/nemici/veicoli/attività. Pausa e
accelerazione delle attività come sopra. Animazioni/esiti/coordinate devono
riferirsi alla stessa cronologia.

## Integrazione successiva: terreno e distanza

Il successivo [riscontro sul terreno](terrain-feedback-2026-10-04.md) integra
queste decisioni: B approvata come direzione dei materiali/vegetazione;
distanza/nebbia non finalizzate, alternative conservate nella
[proposta di panorama ricordato](../design/visibility-and-world-memory.md).
Piccoli dislivelli facoltativi e non prioritari, senza test dedicato richiesto.
Non modifica le scelte di autorità, percezione o tempo sopra.

## Sorgenti esaminate

CDDA: `do_turn`, `calendar`, `avatar_action`, `game`, `creature`, tasche e item
location, corpo/vestiti/iuse, crafting/attività, ranged/melee, sounds/overmap,
monster/monmove/monexamine/mattack, npctalk/npctrade/faction_camp, construction/
clzones/veh_appliance, vehicle_move/veh_interact, skill/mutation/bionics,
computer_session/handle_liquid e relative definizioni JSON.
Luanti: bridge C++, movimento/physics, picking e formspec GUI.
Mineclonia: inventory/craftguide/player animations/armor/mobs/villager,
mappe/weather/farming. Asset e presentazione riutilizzabili; backend gameplay
autonomi da adattare o eliminare secondo scope.
