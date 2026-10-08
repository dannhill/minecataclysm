# Inventario ed equipaggiamento nativo — prima fetta

`I` apre l'inventario CDDA nel client Luanti. Griglia e pannello usano gli
asset Mineclonia; nomi, categorie, quantita, provenienza, peso/volume e tasche
vengono dagli oggetti effettivamente posseduti. Ricerca, filtri e paginazione
sono presentazione. Seleziona un'icona per dettagli e azioni disponibili.
Le icone non ancora mappate usano il fallback esistente, con nome nativo.

Impugna/Riponi/Indossa/Togli passano dal coordinator CDDA alle stesse API
native delle azioni da tastiera. Consultare e cercare non consuma mosse o
tempo; il menu ferma simulazione e animazioni. Un'azione chiude il menu,
attende la rimozione della sola pausa menu e paga il costo nativo. Pausa
manuale/minaccia o riconnessione cancellano una scelta ancora non inviata.
Le richieste inviate hanno deduplicazione e completamento autorevole.

Riporre o cambiare arma conserva la scelta nativa di destinazione/cancellazione,
mostrata dal pannello decisioni esistente con conferma numerica. Togliere uno
zaino non ne cancella il contenuto: CDDA lo ripone, impugna oppure lascia a
terra se non ha spazio. La GUI segnala questa possibilita nel tooltip Togli.
Per provare rimozione/reindosso senza lasciarlo a terra, riponi prima l'arma.
Nessuna selezione della hotbar o inventario Luanti cambia equipaggiamento.

## Autorita e limiti

CWM 2.10 aggiunge una query di sola lettura e handle effimeri per le azioni.
Il server conserva native safe item_locations, non UUID persistenti. Oggetto,
proprieta rilevanti, ruolo e catena dei contenitori vengono riverificati sia
all'ammissione sia all'esecuzione. Refresh, resync e disconnect invalidano
la vista; un'azione invalida gli altri handle prima della mutazione/scelta.
La query e limitata e rate-limited. Il client valida struttura e collegamenti
prima di renderizzarla. [Contratto preciso](../../protocol/PROTOCOL.md).

Questa fetta comprende gli oggetti posseduti e l'equipaggiamento. Non chiude
l'intero inventario: trasferimenti mirati, quantita parziali, drop generale,
apertura di tasche sigillate, contenuti tecnici/ammo, liquidi e hotbar
interattiva restano nel piano. Le azioni non disponibili hanno il motivo
nativo; non si aggirano i vincoli. I salvataggi restano canonici CDDA.

## Verifica e riproduzione

Le [evidenze](native-equipment-evidence.json) riportano commit, alberi,
eseguibili, fixture indipendente, comandi e risultati. Build incrementali
su sorgenti ricostruiti dai pin/patch; nessun cold build o gate globale
M5.5/SAVE-001 viene dichiarato. I test usano copie isolate, mai i save utente.

Il lettore/creatore di fixture e collegato al core CDDA pristine del pin.
I test nativi controllano costi, replay, selezioni mutate, annullamento,
carichi annidati e zaino lasciato a terra completo. Il test del renderer reale
controlla menu/ricerca, quattro azioni, pausa, decisioni, reconnect e lettura
indipendente del save, con screenshot e cattura del protocollo.

Prova manuale rinviata su richiesta, senza dedurne un PASS:
[`pending-manual.md`](../validation/pending-manual.md), ultima checklist.
`./equipment-demo.sh --fresh` prepara una copia della fixture con mazza,
zaino, cappello, bandana e due sassi; senza `--fresh` riprende il save demo.
Nel gioco normale basta `I`. Le prove precedenti restano accettate.
