# HUD a icone, sdraio X e lieve guado — 2026-10-08

Risponde al [riscontro e alla validazione](../source/hud-icon-feedback-2026-10-08.md).
I quattro adattamenti precedenti sono tutti PASS manuale. Il ritocco non
aggiunge un gate estetico; l’accettazione manuale non viene estesa implicitamente
al nuovo aspetto. [Stato del piano](../progress/2026-10-08.md).

## Comportamento

X predefinito, riconfigurabile, alterna sdraio/cammino. Ctrl/Shift mantengono
corsa/accovacciamento e le preferenze toggle. Le configurazioni che assegnano
esplicitamente un altro tasto conservano quella scelta. Launcher delle demo
e indicazioni nel client leggono/mostrano i comandi aggiornati.

HUD centrale sopra la barra dei posseduti: dolore (bendaggio) e sonno
(luna) nella prima fila; testa e torso con icone armatura e dieci cuori distinti
a sinistra; gocce sopra le cosciotte a destra; stamina sotto. Icone vuote scure,
piene colorate, nessun pannello nero né etichette permanenti. Tooltip e H
conservano le descrizioni. Dimensioni si riducono per finestre strette; texture/
widget vengono riusati. Posseduti ancora di sola lettura, nessuna selezione
o equipaggiamento gratuito. In pausa/menu/recovery restano le regole validate.
Diagnostica cammino/tempo/F3 conserva il comportamento attuale; la sua
opzione hotkey/menu è registrata nel piano per produzione, separata dagli
avvisi necessari di pausa/minaccia/decisione/disconnessione.

Proni in acqua bassa: compensazione di 0.22 nodi sul guado -0.30, dunque
occhi 0.08 nodi sotto lo sdraio asciutto. Altezza sopra il centro tile
0.745 contro 0.825 nodi. Ingresso/uscita usa lo smoothing già esistente;
nessuna modifica a posizione/collisioni/effetti o profondità CDDA. Immersione
profonda e relativa oscurità non sono ridisegnate da questo ritocco.

## Contratto dei bisogni

CWM 2.9 aggiunge `StatusValue.perceived_level`, -1 non disponibile o 0–10
livello ordinale del bisogno percepito: più icone è sempre una condizione
migliore (per fame: più sazio). CDDA decide il livello dalle **categorie**
della propria UI; Luanti non interpreta testi localizzati, colori o calorie.
Non è una percentuale fisiologica né una formula Minecraft.

| Barra | Categorie native → icone piene |
|---|---|
| Fame/sazietà | engorged/full/satisfied 10, blank 8, hungry 6, very hungry 4, famished 2, near starving 1, starving 0 |
| Idratazione | turgid 10, hydrated 9, slaked 8, neutra 7, thirsty 5, very thirsty 3, dehydrated 1, parched 0 |
| Riposo | normale 10, tired 6, dead tired 3, exhausted 0 |
| Comfort/dolore | nessuno 10, minimal 9, mild 8, moderate 7, distracting 6, distressing 5, unmanageable 4, intense 3, severe 0 |

Pieno/engorged non significa nutrizione ottimale: colori nativi e H preservano
l’avviso di eccesso. Idratazione usa `get_instant_thirst` (acqua nello stomaco
compresa). Dolore usa **perceived pain**, quindi gli antidolorifici influenzano
la barra senza divulgare dolore nascosto. Categorie senza descrizione neutra
sono note; il caso ERROR nativo fame è -1 con punto interrogativo, mai pieno
inventato. Valori fuori [-1,10] richiedono resync; fonti sane/affette/analgesia
e confini inclusivi/esclusivi sono verificati nei test nativi e protocollo.
Altri StatusValue conservano -1; salute/stamina usano ancora solo i cinque
segmenti del display nativo, distribuiti su dieci icone senza più precisione.
Salute vitale separata; malattie non mediate con HP. Non cambia la simulazione,
il formato del save o una soglia biologica. Entrambi i runtime sono 2.9.

Asset fame/cuori/armatura/stamina Mineclonia pinned; goccia/luna/bendaggio/
indisponibile sono originali CC0, SVG sorgenti e PNG con checksum/comando di
rasterizzazione in `game/mods/cdda_items/status_assets.json`.

## Verifica e consegna

Sorgente produzione `5c7a838`; successiva modifica soltanto alle attese del test
dolore e ai documenti/testi launcher, senza differenze di comportamento del
runtime. Ricostruzione incrementale con cache conservate, non build freddo.
Artifacts `artifacts/hud-icons-20261008/`; binari installati e rollback in
`installed-runtime.json` e `rollback/`. Reader di save nativo pristine pinned
2478ae876eb1439be387d0e117808d33c9d6afa4 riusato dalla consegna precedente,
con sorgente/build receipt in `artifacts/controls-hud-20261008/`.

Build entrambi componenti, protocollo 5/5 e Luanti 307 test/648 assertions
PASS. Suite CDDA finale **7.665 assertions/44 casi PASS**, con attese esplicite
sui confini delle categorie e analgesia. Sorgente finale dei test `241330c`.
GUI comandi/acqua/icone 32/32 sia ricostruita sia installata: X realmente
premuto, Ctrl/Shift, CLOSE simultaneo/ritardato, H acqua/pickup fermi, S,
resync, piccola discesa/risalita proni camminando fra acqua/pavimento e save
letto dal reader nativo. Scheda corporea in modalità ordinaria **19/19 PASS**,
inclusi scroll, pausa/reconnect, tutti i 12 HP esatti, posizione/tempo/stamina
nativi invariati. [Registro completo](icon-survival-hud-evidence.json) con
identità di sorgenti/binari, comandi, risultati e hash degli artefatti. Nessuna
certificazione completa M5.5/SAVE-001 viene dedotta da queste prove mirate.
