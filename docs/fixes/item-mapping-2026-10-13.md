# Sincronizzazione batch oggetti — 2026-10-13

Importati gli output di produzione Sol 28–60 senza modificare input/output
originali, pilot o repliche. Il registro ora contiene 60 batch consecutivi,
2.400 ID univoci, 972 rappresentazioni supportate, 274 match con fallback e
1.154 NO_GOOD_MATCH; 146 texture distinte con fonte e SHA-256.
La consegna precedente conteneva 27 batch, 1.080 record e 396 rappresentazioni.

Comando: `python3 tools/sync_item_mapping.py`. Verificati input/output, ordine,
candidati, conflitti, confidenza/tipi, tutte le texture rispetto al pin Mineclonia,
hash di ogni output e seconda generazione identica. Licenze/attribuzioni copiate
accanto ai media. Evidenze: `artifacts/medical-20261013/mapping-validation.json`.
Il renderer carica le nuove definizioni nel normale start.sh; nessuna meccanica
Mineclonia viene importata. Varianti procedurali consigliate dai batch restano
raccomandazioni; match non supportati conservano il fallback. Il override locale
water_clean resta separato e precede il fallback grafico.
