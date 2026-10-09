# Sincronizzazione dei batch oggetti — 2026-10-09

Richiesta esplicita dell’utente: importare gli ultimi output Sol. Sono presenti
**27** batch consecutivi `batch-0001-output.json`–`batch-0027-output.json` in
`artifacts/item-mapping/sol-pass1-batches`, 40 record ciascuno. Gli input e gli
output originali non sono modificati. Pilot/test/repliche non vengono importati.

Comando: `python3 tools/sync_item_mapping.py` dalla radice del progetto.

| Misura | Prima | Dopo |
|---|---:|---:|
| Batch di produzione | 9 | 27 |
| Record | 360 | 1.080 |
| Rappresentazioni supportate nel runtime | 88 | 396 |
| Associazioni con asset non supportato, fallback | 25 | 105 |
| Nessun match adatto, fallback | 247 | 579 |
| Asset texture distinti con fonte/hash | 18 | 89 |

Validazione di tutti i record: quantità/ordine/ID corrispondenti agli input,
nessun ID duplicato, scelta appartenente ai candidati, NO_GOOD_MATCH senza
scelta, decisione/confidenza/tipi coerenti. Le 89 texture sono confrontate
tramite SHA-256 con i sorgenti Mineclonia del pin corrente. Licenze/attribuzioni
accompagnano gli asset. Seconda generazione identica byte per byte.

396 definizioni di presentazione in `game/mods/cdda_items/generated_mapping.lua`;
manifest asset e hash degli output in `generated_assets.tsv` e
`mapping_provenance.json`. Master completo/rapporto restano nell’area mapping
come in precedenza. Le raccomandazioni di varianti procedurali non sono
implementate da questo import: il runtime usa l'immagine proxy supportata.
Associazioni a nodi senza icona supportata conservano il fallback. Nessun
comportamento Mineclonia, oggetto CDDA o quantità viene importato/alterato.

Evidenze riproducibili locali in `artifacts/inventory-feedback-20261009`:
`mapping-validation.json`, `mapping-sync.log`, `mapping-idempotence.json`;
le verifiche grafiche con la nuova registry sono riassunte nel report dei fix
UI della stessa consegna. Nuovo ricontrollo facoltativo nel consueto backlog.
