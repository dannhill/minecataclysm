# UX-04B e riscontro manuale — consegna del 2026-10-13

Installato nel normale `start.sh`, CWM 2.21, mantenendo movimento continuo 4x.
Il [riscontro originale](../source/manual-ui-feedback-2026-10-13.md) accetta
12 nuovi punti e segnala un FAIL lingua. Non si trasformano le riparazioni in
PASS personali: backlog 20 PENDING + 1 FAIL manuale, tutti rinviabili.

## Comportamento

I → oggetto reale → Treat/Medica apre una scelta strutturata delle parti:
icone anatomiche proxy, cuori alla risoluzione nativa, spiegazioni CDDA di ferite,
benefici e limiti. Parti non pertinenti restano leggibili ma non cliccabili.
Salute sconosciuta/fratture/mending restano qualitative; HP esatti solo dove il
menu nativo consente precisione. Scelte e conferma sono esplicite, senza cura
in lettura, automatismi di trattamento o parsing delle barrette ASCII.
Identità della domanda/connessione, rilascio dei tasti, annullamento e perdita
IPC conservano i vincoli UX-04A. [Design](../design/structured-medical-selection.md).

Il layout DND mantiene l’ultima griglia durante la query, senza pannello vuoto
intermedio. Le azioni fisiche continuano a richiedere lavoro nativo e ritorno
pagato. Indossa/Togli mostrano il pagamento temporale già gestito dal clock CDDA:
non viene creata una finta attività né allungata un’azione breve. Consumo/cura/
crafting mantengono il progresso del proprio actor. Le destinazioni possedute
hanno righe più alte e sei contenitori per pagina.

Il menu Esc ora offre due pulsanti espliciti per la lingua. English → Italiano
→ English viene verificato con menu reali, preferenza persistente e riavvii dei
due processi. Il selettore a tendina del menu pausa viene sostituito: nessuna
deduzione di gameplay da etichette tradotte. Il restart resta necessario; il
cambio a caldo di cataloghi e testi nativi memorizzati è un follow-up.

[Mapping aggiornato](item-mapping-2026-10-13.md): 60 batch, 2.400 record, 972
rappresentazioni supportate e 146 texture con fonte/hash. Gli output originali,
l’override locale water_clean e la logica di gameplay rimangono distinti.

## Verifica e limiti

Build incrementali da copie ricostruite e controllate; nessuna clean build o
certificazione complessiva. 179 test CDDA / 185.997 assert, 309 test Luanti /
47 moduli più 648 assert Catch in 4 casi, 11 test protocollo, helper di
presentazione e 9 verifiche della lingua/launcher. Prove nel renderer reale,
wire trasparente, mondi/configurazioni isolati e lettore indipendente del core
CDDA pinned. Ricevuta completa con identità, hash, comandi e conteggi grafici:
[structured-medical-selection-evidence.json](structured-medical-selection-evidence.json).

Le prove mediche controllano selezione/lettura, tasti tenuti, No/Esc, approvazione
esplicita, pausa/ripresa, esattamente una benda consumata e una parte bendata,
nessun disinfettante usato, nessun replay su perdita IPC e save canonico leggibile.
Hotbar: griglia sempre disponibile durante query di layout, progresso nativo
sincrono, equipaggiamento/costi, nessun replay da pausa, riconnessione e riferimenti
canonici persistenti. Lingua: entrambi i cambi dal menu reale e successivo avvio
in inglese, senza riscrivere opzioni native o duplicare gli oggetti.

Fallimenti di preparazione conservati negli artifact: file unit.conf mancante;
nuovo test medico inizialmente senza credito di movimento; vecchio harness
premendo Esc annullava la domanda e attendeva erroneamente nessun menu dopo il
ritorno automatico. Corretti configurazione/fixture/harness, conservando gli
assert su risultati, annullamento e costo autorevoli. Nessuna regola clinica
modificata per far passare i test.

Icone anatomiche restano proxy Mineclonia; il percorso H → parte → oggetti
filtrati è un’estensione successiva. AIM-01 rimane gesto mantenuto: rilascio
termina nuovi passi di mira, senza azzerare la precisione già pagata; movimento
mantiene costi/penalità nativi. Pose/zoom restano presentazione futura. UX-05
recenti/preferiti è la prossima fetta. SAVE-001 completo OPEN; M5.5 storico FAILED.
