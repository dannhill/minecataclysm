# Quantità, deposito e contenitori posseduti

Prima fetta dell'inventario profondo, disponibile con **I → Quantità e
trasferimenti**. Il pannello sinistro mostra gli oggetti posseduti; il destro
permette di scegliere un contenitore reale. Quantità positive esplicite:
cariche parziali per oggetti conteggiati, una singola istanza altrimenti.
**Deposita a terra** sceglie esplicitamente il suolo della casella del personaggio,
anche se esiste cargo di un veicolo. **Trasferisci nel contenitore** usa le
tasche CONTAINER selezionate dal codice nativo del contenitore scelto.

La GUI sceglie in pausa e chiude per agire. ACT_DROP e ACT_INSERT_ITEM sono
attori CDDA originali: rimozione, quantità, accesso, ingombro e costi di
trasferimento rimangono nativi. Per il deposito CDDA non fornisce una durata
totale: viene mostrato un lavoro attivo senza inventare una percentuale. Per
l'inserimento si mostra il costo e il lavoro residuo nativi. **I** ferma
il tempo; **Interrompi trasferimento** invoca cancel_activity nativo.
Non vengono modificati inventari o cariche nel client Luanti. Nel fallback
scandito dalle azioni, senza scheduler real time, il loop nativo puo completare
il lavoro fra due frame grafici: paga comunque il tempo simulato. Le prove
di pausa/interruzione durante il progresso usano la modalita RT della demo.

CWM 2.15 conserva union 38 e appende ItemTransferRequest 39 e
CancelItemTransferRequest 40; aggiunge metadati di sola lettura all'InventoryEntry
e lo stato opzionale ItemTransferState allo snapshot. Il ledger include
vista, identità dell'oggetto, quantità, destinazione e azione. Handle effimeri
vincolati a safe item_location; quantità, ruolo e catena dei contenitori,
posizione canonica, attività e pausa vengono rivalidati all'ammissione e
all'esecuzione. Destinazione, capienza diretta e capacità degli antenati vengono
controllate da CDDA. Self-containment/cicli, noop nello stesso contenitore,
cariche e identità mutate non vengono accettati. Refresh/reconnect/resync
invalidano le selezioni; comandi durante pausa/attività non sono differiti.

Il salvataggio usa gli attori e item_location canonici: nessun handle CWM è
persistito. Il contenitore depositato conserva il suo contenuto. La quantità
scelta non è una promessa client: l'esito e la provenienza si leggono dalla
nuova vista autorevole. I rifiuti nativi restano nel messaggio di risultato.

## Limiti espliciti

Destinazioni di questa fetta: contenitori posseduti e suolo della casella
corrente. Contenitori esterni, cargo, selezione puntuale della singola tasca,
trasferimenti multipli in un lotto e drag/drop avanzato sono successivi.
Gli oggetti indossati richiedono prima Togli; can_drop/can_unwield restano
vincolanti. Liquidi, gas, contenuti tecnici, tasche sigillate e contenitori
aperti pieni richiedono interazioni dedicate. Non si aprono sigilli
implicitamente. Il native insert actor può conservare il suo costo per
l'intera pila di origine anche quando viene scelta una quantità parziale:
non lo si sostituisce con un tempo più favorevole inventato dalla GUI.
Il controllo conservativo degli antenati usa le stesse API del native actor;
riordini molto stretti in un contenitore quasi pieno possono richiedere un
passaggio intermedio. La scelta manuale del contenitore non implementa
ancora tutte le impostazioni/favoriti delle singole tasche.

## Verifica

[Evidenze scoped e comandi riproducibili](native-transfer-evidence.json).
CDDA: **16.659 asserzioni / 113 casi**, incluse tasche, raccolta, ricarica,
acqua e CWM. Luanti: **308 test / 47 moduli**, più **648 asserzioni / 4 casi**
Catch2. Protocollo: **9/9**. Sei sessioni del renderer reale, **145 controlli
riusciti**: trasferimento RT salvato (16), ripresa (13), runtime installati
(30), fallback scandito dalle azioni (26), equipaggiamento (29) e tiro/ricarica
(31). Tutti i save vengono riletti dal core pristine dello stesso pin CDDA.

La fixture ha 30 munizioni. L'inserimento di 7 conserva 23 alla fonte;
3 depositate lasciano 4 nel sacchetto. Depositare il sacchetto conserva le 4
al suo interno, con 3 cariche sciolte e 23 possedute: totale 30, nessuna
istanza del contenitore o degli altri oggetti duplicata. Il save attivo
contiene ACT_INSERT_ITEM originale, riferimento item_location e quantità 7,
500 mosse totali / 300 residue nella prova; il riavvio riprende senza nuova
richiesta e completa una sola volta. Le schermate del pannello di selezione
e di Interrompi trasferimento sono state ispezionate; le icone senza mapping
mantengono il fallback esistente e l'accettazione grafica resta dell'utente.

Identità complete di sorgenti/pin/patch, eseguibili, lettore pristine, comandi,
log, save e screenshot sono nel JSON. La precedente coppia 2.14 è conservata
in artifacts/native-transfer-20261009 come rollback. Gli eseguibili installati
coincidono con quelli ricostruiti e verificati. Gli esperimenti iniziali non
sono conteggiati come PASS: fixture di test/working directory corrette,
shutdown esplicito del relay di prova distinto dagli errori attivi, e test
ordinary distinto dalla visibilità del progresso scandito nel tempo reale.
Non è stato necessario cambiare gli attori originali di drop/insert.

Riproduzione: script di baseline, refresh della ricostruzione e replay dei pin;
build/test espliciti e argv esatti nel report. Il lettore standalone richiede
il core pristine del pin e il helper tests/takeover_save_reader.cpp: la ricevuta
reader-build.json conserva compile/link/strip e digest. La fixture si genera
con --create-transfer; GUI con tests/transfer_gui_test.py, fixture isolata,
X11 :1, xdotool/ImageMagick/Pillow e native-save-reader. Nessun save utente è
stato aperto o modificato.

Build incrementali su sorgenti ricostruiti da pin e patch, cache conservate;
nessun cold build, nessuna promozione del M5.5 storico FAILED o del SAVE-001
completo ancora OPEN. Fixture e lettore semantico collegati al core pristine
CDDA originale, salvataggi e configurazioni isolati. I test manuali restano
[nel backlog](../validation/pending-manual.md), quattro nuovi punti,
**24 PENDING** totali; nessun PASS dell'utente viene dedotto.

`./transfer-demo.sh --fresh` apre una nuova copia della fixture verificata,
con 30 munizioni 9mm, sacchetto, bottiglia, mazza e sasso nello zaino.
Senza --fresh riprende l'ultima sessione della sola demo.
