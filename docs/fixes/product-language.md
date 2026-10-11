# LANG-01 — Lingua del prodotto

Consegna del 2026-10-12, CWM **2.18**. Il normale `./start.sh` usa
**English** come predefinito; **Italiano (WIP)** è selezionabile da Esc,
**Language / Lingua**. Esci e riavvia lo stesso launcher per applicare la
scelta a CDDA e Luanti. La scelta è presente anche nelle impostazioni del
menu principale. [Design e priorità delle preferenze](../design/product-language.md).
[Identità dei sorgenti ed evidenze](product-language-evidence.json).

## Comportamento e confini

La lingua di sistema e una vecchia impostazione globale `language` non
selezionano automaticamente italiano. Un cambio dal menu viene conservato
in `config/presentation-language.conf` nel userdir del prodotto. È metadato
di presentazione separato da `options.json` e dai salvataggi canonici.
`CDDA_LANGUAGE=it ./start.sh` è un override temporaneo; da solo non salva
una nuova preferenza. Valori espliciti diversi da en/it sono rifiutati prima
di creare il mondo. La sessione attuale conserva la lingua iniziale fino al
riavvio: il selettore non paga tempo né esegue o reinterpreta azioni native.

HUD, inventario, raccolta, corpo, crafting, quantità, azioni e indicazioni
d'integrazione usano il medesimo helper di presentazione. Nomi, descrizioni,
ricette e scelte native usano il traduttore CDDA e il suo catalogo italiano
catturato, compresi contesto e plurali. Anche il menu engine usa gettext.
Le traduzioni italiane mancanti conservano l'inglese: WIP è intenzionale,
non una promessa di traduzione integrale dei contenuti.

Le prime schermate italiane hanno rivelato icone generiche dipendenti da
categorie tradotte. I tre esportatori (inventario, proiezione degli oggetti posseduti,
slot rapidi) ora inviano l'ID nativo della categoria. Le etichette conosciute
sono localizzate soltanto per lettura/ricerca; l'arte usa ID stabili. Nessuna
modifica ai batch di mapping, ai type ID o alla struttura/versione CWM.

## Verifiche

Sorgenti ricostruiti e save/config isolati. CDDA è stato ricompilato con
LOCALIZE=ON e catalogo it_IT; Luanti ha una nuova build con gettext abilitato,
seguita da build incrementali per i ritocchi verificati. Non è un clean build
complessivo né una nuova certificazione M5.5.

- Launcher: **9 test** su precedenze, accordo dei processi, override,
  salvataggio atomico, ritorno all'inglese e opzioni native intatte.
- Protocollo: **10/10**, inclusi UTF-8/fallback e byte dei comandi invariati.
- Native: **173 casi / 185.813 asserzioni**; traduzioni non nascoste:
  **13 casi / 38.012 asserzioni**, inclusi cataloghi, contesto e plurali.
- Luanti: **308 test / 47 moduli**, più **648 asserzioni / 4 casi Catch**.
- Renderer reale sotto Xvfb: I/H/K, nomi di cappello/zaino, Annulla/Cancel,
  categorie stabili, pausa, cambio effettivo da Esc, preferenza al riavvio,
  ritorno inglese e save letto dal core nativo indipendente.

La ricevuta distingue le prove sui sorgenti ricostruiti da quelle sulla
coppia installata nel normale launcher e conserva gli screenshot. I check
canonici verificano quantità/identità, ruoli, oggetti immutati e posizione
al reload: sono compatibilità circoscritta, **non SAVE-001 completo**.
I tentativi iniziali falliti restano negli artefatti: file di configurazione
unit mancante e aspettativa del test che ometteva il prefisso nativo `++`.
Il test è stato corretto; i nomi nativi e i prefissi non sono stati alterati.

## Installazione e seguito

Entrambi i runtime localizzati e i due cataloghi italiani sono installati
insieme per il normale `start.sh`, con checksum e copie della coppia precedente
nell'artefatto di consegna. Il continuo **4×** accettato resta predefinito.
La ricevuta identifica le build, il compilatore gettext locale e il rollback;
nessun mondo o configurazione personale è stato usato per queste prove.

Il [backlog manuale](../validation/pending-manual.md) contiene **15 PENDING**:
i tredici precedenti e due nuovi punti per la lingua. Nessun PASS manuale
viene dedotto dalle prove automatiche e non serve testare oggi.
La mira RMB mantenuto/priorità contestuale è il prossimo passo, poi
contenitori esterni e raccolta quantitativa. Restano nel piano rig/UV,
animazioni, audio e dialoghi più ricchi. M5.5 rimane storico FAILED e
SAVE-001 resta OPEN.
