# Indossa/Togli: tempo nativo e consultazione — 2026-10-18

La [decisione esplicita](../source/manual-validation-followup-2026-10-18.md)
conserva la semantica CDDA del singolo capo: applicazione atomica e costo in
mosse, senza introdurre una vestizione parziale annullabile. Il
[design](../design/native-equipment-time.md) distingue questa operazione dalle
vere attività native. Protocollo CWM **2.23**, gameplay e salvataggi invariati.

## Correzione

Il client rifiutava I mentre il comando era in volo. Inoltre aprire/chiudere
I cancellava il tracciamento del costo già applicato, facendo sparire il
feedback alla ripresa. Il runtime precedente riproduce il primo difetto con
una risposta dell'equipaggiamento ritardata da un relay byte-trasparente.

- I apre e richiede subito MENU_OPEN anche durante la risposta di quel comando.
  La query di sola lettura attende l'esito, evitando l'inventario precedente al
  cambio. Se l'azione non era ancora eseguita può essere rifiutata dalla pausa
  nativa; non viene dichiarata applicata per il solo fatto di averla inviata.
- Il pannello mostra operazione/oggetto, applicazione avvenuta e secondi di
  gioco residui esportati dal coordinatore. Nessuna percentuale o barra di
  vestizione. Un eventuale esito negativo resta distinto da un cambio applicato.
- Consultare conserva il costo residuo: il capo risulta già cambiato, il tempo
  si ferma e chiudere riprende lo stesso debito. Non rimborsa mosse e non annulla
  il capo. La consultazione manuale disattiva il ritorno automatico; Esc fuori
  dal menu continua a nascondere il solo pannello.
- Barra e Interrompi restano per gli actor reali: medicina, crafting, consumo,
  ricarica e trasferimenti. Non viene inventato un token per i vestiti.

## Verifica

Build incrementale da ricostruzione con inventari verificati, non clean build.
309 test client / 47 moduli e 648 assert Catch / 4 casi PASS. **115 controlli grafici/canonici PASS**: 28 vestiti ricostruiti, 33 medicina,
26 sequenze/pausa/recovery e 28 sul runtime installato nel normale `start.sh`.
Renderer reale, input xdotool su Xvfb/Mesa privato, relay byte-trasparente e
salvataggi isolati. Il core pinned indipendente rilegge i salvataggi.
[Ricevuta riproducibile](native-equipment-time-evidence.json): comandi, source
identity, hash e rollback. Nessun binario CDDA sostituito con codice nuovo.

Il core CDDA, i suoi costi e il suo binario non vengono modificati. Nessuna
ricertificazione dell'intero SAVE-001 (OPEN) o del gate M5.5 storico (FAILED).
Mapping batch60 invariato. Nessun salvataggio personale usato.

## Riscontro personale

Registrati 13 nuovi PASS; backlog **9 PENDING + 1 FAIL manuale**. Resta il
ricontrollo Indossa/Togli, ora con aspettativa fedele al nativo e senza richiesta
di annullamento. I PASS personali non derivano dalle prove automatiche.
[Checklist rinviabile](../validation/pending-manual.md).
La raccolta diretta degli oggetti sfusi resta un seguito UX separato.
