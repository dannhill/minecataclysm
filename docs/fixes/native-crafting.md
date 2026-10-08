# Crafting guidato nativo — prima fetta

**K** apre il catalogo delle ricette conosciute e dei lavori incompleti. Ricerca,
pagine e lotto manuale 1–20 mostrano requisiti, utensili, competenze, libri,
aiutanti, disponibilita e durata stimata native. Il catalogo ferma il tempo e
non produce oggetti. Le icone riusano il mapping di presentazione esistente;
gli oggetti senza asset appropriato restano placeholder.

Seleziona una ricetta disponibile, poi **Scegli componenti e crea**. CDDA
propone le alternative e le fonti native (personaggio/vicinanze), quindi una
conferma esplicita con risultato, quantita e materiali. No/Cancel prima della
creazione non consumano i componenti. La selezione nativa distingue tipo,
quantita e fonte: scegliere una specifica istanza fra oggetti identici resta
un lavoro successivo. Oggetti preferiti, tipi attualmente equipaggiati e
contenitori liquidi pieni non sono consumati come componenti; la protezione
del tipo equipaggiato e conservativa e comprende anche copie non equipaggiate.

**ACT_CRAFT** e l'oggetto incompleto canonico CDDA possiedono materiali,
progresso, cariche degli utensili, fallimenti, pratica, competenze e risultati.
Luanti non crea gli oggetti ne aggiorna l'inventario in anticipo. La barra usa
il contatore nativo del lavoro, non una durata inventata dal renderer.
Il completamento e il salvataggio usano il formato CDDA originale.

**K o I** durante il lavoro fermano il tempo e offrono un'interruzione
esplicita. Interrompere conserva il lavoro incompleto; non rimborsa i materiali
gia incorporati. K lo mostra marcato **R**: puoi riprenderlo se raggiungibile
e se le condizioni native lo permettono, anche su una superficie vicina
visibile/accessibile. I materiali di riparazione mancanti e gli utensili del
lotto sono indicati nei dettagli. Il save con lavoro in corso riprende la vera
attivita nativa. In modalita ordinaria l'attivita procede senza il pacing RT;
pausa e interruzione interattive si provano con RT-02.

La prima fetta ammette risultati solidi senza sottoprodotti. Liquidi/gas,
sottoprodotti, pratica e costruzioni richiedono selettori dedicati: il catalogo
spiega il limite e il server lo ricontrolla anche sulla ripresa. Preferiti di
ricette, sottoricette collegate, lettura, smontaggio, accelerazione generale,
lavori nei veicoli e scelta della singola istanza restano nel piano.
Non viene dichiarato completo l'intero punto crafting/lettura/lavorazioni.

CWM **2.13** aggiunge query/catalogo, avvio con handle effimeri e interruzione
con token. Ogni comando ricontrolla la selezione all'ammissione e all'esecuzione;
ritrasmissioni non creano un secondo lavoro. Movimento e altre azioni durante
il crafting non vengono accodati. Reconnect/resync invalidano i vecchi handle.
Snapshot con attivita simultanee o contatori malformati richiedono resync.
Gli adattatori di scelta riusano le voci native del crafting, senza duplicarne
le regole nel client; le altre uilist terminali restano fuori da questa fetta.
La scena del renderer verifica bandages_makeshift senza utensili: non attesta
ogni ricetta, ogni utensile a cariche o ogni combinazione di contenitori.
Le regole restano native; queste combinazioni richiedono copertura dedicata.

## Prova rinviata

`./crafting-demo.sh --fresh` crea una copia isolata del save prodotto dal
lettore CDDA pristine. Nello zaino ci sono otto fogli di cotone e un preferito
protetto; a ovest, accanto al personaggio, un materiale alternativo. Cerca
**bandage** e scegli la ricetta senza utensile. Lotto 1 produce due bende,
lotto 2 quattro. Senza --fresh riprende il salvataggio della demo.
La stessa interfaccia K e disponibile nella partita normale da start.sh.

Le quattro nuove prove sono nel [backlog manuale](../validation/pending-manual.md),
insieme alle dodici precedenti: **16 PENDING**, nessuna richiesta di test ora
ne accettazione dedotta dall'automazione. Ricostruzione, build incrementali,
prove native e del renderer installato, identita e comandi sono riportati nel
[registro tecnico](native-crafting-evidence.json). M5.5 resta storico FAILED;
SAVE-001 completo ancora aperto.

Se la fixture locale manca, ricostruiscila con il lettore indipendente e la
ricetta di compilazione registrata nell'evidence; non usare mondi dell'utente:

```sh
artifacts/native-crafting-20261008/native-save-reader --create-crafting \
  --userdir artifacts/native-crafting-20261008/fixture/user \
  --datadir cdda/data --output artifacts/native-crafting-20261008/fixture/before.json
```

Verifiche mirate PASS: 84.101 asserzioni CDDA/83 casi; 308 test Luanti e
648 asserzioni Catch2/4 casi; protocollo 7/7; renderer installato 166 controlli
(crafting RT/save 27, ripresa 11, turni 19; medicazioni 35 + ripresa 14,
consumo 31, equipaggiamento 29). Le build sono incrementali su sorgenti
ricostruiti, con cache conservate; non sono build fredde indipendenti.

Artefatti: `artifacts/native-crafting-20261008`. La revisione AGY Gemini
3.8 Flash High ha completato un controllo limitato del validatore in 133 s;
ogni rilievo e stato ricontrollato. Il registro distingue suggerimenti adottati
e osservazioni errate; non e una certificazione architetturale.
