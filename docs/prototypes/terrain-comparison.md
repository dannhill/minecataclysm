# Confronto giocabile del terreno

Prototipo richiesto dall'utente: punti 1 e 2 della proposta sul terreno.
Confronta presentazione attuale e materiali/vegetazione più distinti, con
nebbia regolabile separatamente. La prova successiva approva B per
materiali/vegetazione; la soluzione finale della distanza/nebbia resta aperta.

## Avvio e confronto

Dalla directory del progetto:

```bash
./terrain-demo.sh
```

| Comando | Effetto |
|---|---|
| F7 | Alterna A (materiali attuali) e B (materiali e vegetazione più distinti), nella stessa posizione. |
| F8 | Alterna nebbia ON/OFF, indipendentemente dalla variante. |
| WASD + mouse | Movimento nativo CDDA e visuale in prima persona. |
| Esc | Menu di pausa/uscita Luanti. |

La partenza è B con nebbia ON. Per un confronto completo, restare nello stesso
punto e provare A senza nebbia, B senza nebbia e B con nebbia. Aspettare circa
un secondo dopo F7 perché il meshing completi il cambio. Cambiare resa non
manda un comando di gameplay, non consuma tempo e non sposta il personaggio.

Al centro ci sono percorsi chiari verso quattro zone: bosco a nord-ovest,
campo a nord-est, strada/casa a sud-ovest, sabbia/acqua a sud-est. Alla partenza
si guarda a nord: bosco a sinistra e campo a destra; girandosi di mezzo giro,
casa a destra e riva a sinistra. Camminare nelle zone per valutarle anche da
vicino. Casa, finestre e porta sono terrain nativi, non scenografia separata.

Ogni avvio crea un nuovo mondo in
`artifacts/terrain-prototype/plays/run-*/`. I salvataggi e log della demo restano
lì; il mondo normale e il suo personaggio non vengono caricati. Per ripetere
il confronto dal centro basta rilanciare lo script. Dopo l'approvazione manuale,
`start.sh` usa anch'esso B, tramite la [riparazione esplorativa](../fixes/exploration-apertures.md).
La fixture, gli spawn disabilitati e la nebbia corta restano specifici della demo.

## Riscontro della prova manuale

L'utente ha scelto B per materiali/vegetazione: resa più naturale e varia.
La fog riduce pop-in e isola nel vuoto, ma la distanza è troppo corta per
essere la soluzione definitiva. Pianura cittadina/costiera accettabile;
bosco/campo, alberi e panorama restano da migliorare. Non sono stati scelti
nuova scala, rilievo o visibilità aggiuntiva delle creature.

La [segnalazione completa](../source/terrain-feedback-2026-10-04.md) registra
anche finestre/porte incoerenti, acqua, arredi e accesso ai piani. Una sessione
della demo contiene un abort da input terminale: le evidenze sotto sul
confronto non certificano tutti i percorsi esplorativi o varianti native.
La [proposta sulla distanza](../design/visibility-and-world-memory.md) distingue
percezione, memoria e confine grafico. Promozione B e correzioni sono descritte
nella riparazione successiva; le evidenze sotto identificano il prototipo originale.

## Criteri usati per la prova

- Sensazione del paesaggio: resta troppo piatto anche con la vegetazione?
- Distinzione di erba, terra, sabbia, asfalto, marciapiede e acqua.
- Nebbia: attenua il confine senza disturbare la lettura dei dintorni?
- Bosco/campo rispetto alla strada e all'interno dell'edificio.
- Pacing del cambio A/B, frame rate e presenza di eventuali nuovi salti grafici.

Sono utili preferenze separate per materiali, vegetazione e nebbia. Questa
scena non propone ancora colline o piccole ondulazioni decorative. Il tempo
resta comandato dalle azioni; animazioni/orientamento dei mob non cambiano.

## Implementazione e limiti

`cdda-server --terrain-demo` costruisce la fixture attraverso map, terrain,
weather e save nativi, soltanto in un nuovo mondo `terrain_comparison`.
Una seconda creazione nello stesso mondo viene rifiutata. Gli spawn vengono
disabilitati soltanto nella fixture, per osservare il paesaggio senza combattere.
La superficie mantiene le quote e i costi nativi: sabbia, erba lunga, arbusti
e acqua possono rallentare diversamente il passo.

CWM minor 3 aggiunge cinque categorie semantiche al catalogo numerico, senza
strutture Luanti: sabbia, arbusto, albero, marciapiede, erba lunga. La variante
A le traduce nelle precedenti categorie generiche; B usa asset del pin
Mineclonia. Le variazioni di erba/terra dipendono dalle coordinate assolute
CDDA, quindi un rebase non cambia casualmente le texture.

Il client conserva la proiezione semantica per ricostruire A/B, aggiorna i
blocchi cambiati sotto il lock di proiezione e conserva camera/entità. Questa
cache aggiuntiva e i suoi bounds esistono soltanto nella modalità confronto.
Gli alberi sono una rappresentazione stilizzata di tronco/chioma, entro le
celle del renderer corrente; non un modello definitivo del bosco.

La nebbia sfuma linearmente verso il colore del cielo. La distanza massima è
40 caselle e viene ridotta prima del bordo della superficie proiettata;
il calcolo dei bounds avviene agli aggiornamenti, non scandendo i tile a ogni
frame. È una nebbia del confine: la proiezione corrente non ha ancora il
filtraggio completo della conoscenza/percezione del terreno. Non certifica
una fog of war sensoriale, né la lettura di nemici e pericoli in ogni scenario.

L'acqua usa una texture animata, senza una simulazione fluida Luanti. Le
texture aggiunte sono copie dei file pinned; provenienza/hash e i notice
upstream sono in `game/mods/cdda_nodes/terrain-assets.json` e `media-notices/`.
L'audit completo delle licenze resta FND-05.

## Evidenze

Risultati, comandi, sorgenti e hash sono nel
[registro](terrain-comparison-evidence.json). Prove su sorgenti ricostruiti,
mondi isolati e client Luanti reale. Build incrementali con riuso verificato
delle dipendenze, non cold-cache.

| Prova | Esito |
|---|---|
| Demo reale: A/B, fog, quattro zone, camera/revisione e movimento | 14/14 PASS |
| Rebase sul renderer reale | 15/15 PASS |
| Movimento, finestre, FPS e risposta ritardata | 48/48 PASS |
| Fixture solo in nuovi mondi, rifiuto e preservazione dei save | 4/4 PASS |
| CDDA nativo `[cwm]` | 10 casi / 3.410 asserzioni PASS |
| Luanti nativo | 303/303 PASS |
| Protocollo Debug | 2/2 PASS |
| Lettura nativa indipendente del save della demo | PASS, scope mirato |

I binari di `start.sh` e della demo corrispondono a quelli verificati e sono
stati installati atomicamente. Queste verifiche attestano il funzionamento
del confronto; non scelgono l'estetica per l'utente e non promuovono il gate
M5.5 storico, che resta FAILED. FND-02/03, SAVE-001 completo e il resto della
fase 2 restano aperti.
