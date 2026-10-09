# UX-03D — Inventario con trascinamento

Consegna del 2026-10-09, CWM **2.18**, disponibile con I dal normale
`./start.sh` e dalle demo isolate. Sostituisce il flusso Assegna/Svuota
rifiutato dall'utente. Accettazione del nuovo gesto **PENDING**, separata
dalle prove automatiche. [Identità ed evidenze](inventory-drag-and-drop-evidence.json).

## Comportamento

Clic breve seleziona; movimento oltre 6 pixel avvia il drag, con icona al
cursore e destinazione verde/rossa secondo l'ammissibilità già conoscibile.
CDDA verifica comunque capacità e condizioni finali. Esc durante il gesto,
rilascio fuori dal menu e rigenerazione della vista lo annullano. Deposito
soltanto sull'area esplicita **Terra**, senza drop accidentale fuori dalla GUI.

| Gesto | Operazione |
|---|---|
| Griglia → slot rapido | Assegna l'istanza; scompare dalla griglia principale. |
| Slot rapido → altro slot | Sposta o scambia entrambi i riferimenti atomicamente. |
| Slot rapido → griglia | Toglie il riferimento, conservando oggetto e ruolo reale. |
| Griglia → altro oggetto non contenitore / spazio vuoto | Inserisce prima / porta alla fine nell'ordine grafico. |
| Oggetto → In mano / Indossati | Impugna / Indossa con costi e scelte CDDA. |
| In mano / Indossati → griglia | Riponi / Togli con costo e vincoli CDDA. |
| Oggetto → icona/riga contenitore posseduto | Inserimento nativo nel contenitore. |
| Oggetto → Terra | Deposito nativo alla posizione del personaggio. |

La sottovista **Quantità e trasferimenti** conserva tutte le sorgenti,
compresi contenuti annidati e oggetti assegnati. Seleziona la pila, imposta
la quantità e trascinala sulla riga del contenitore o su Terra. Senza una
quantità esplicita per quella sorgente, il gesto usa l'intera disponibilità.
Un contenitore depositato mantiene i suoi contenuti; non confonderlo con la
voce del singolo oggetto contenuto. Per trasferire un indossato non ammesso
come sorgente, prima Togli: nessuna azione nascosta o sigillo aperto implicitamente.

Mano/indossati descrivono ruoli dello stesso oggetto; non sono copie o tasche
aggiuntive. Le pagine degli indossati conservano tutti gli strati esportati.
La griglia è un ordine compatto: caselle vuote non rappresentano buchi salvati
né capacità fisica. I pulsanti di dettaglio rimangono per azioni come
Mangia/Medica che non hanno una destinazione naturale. Rotella/1–9 e G
conservano la selezione separata dall'uso nativo. La raccolta già consegnata
mantiene il suo controller specchio; il nuovo controller opera solo su I.

## Autorità e persistenza

Le zone formspec e le coordinate del puntatore restano locali a Luanti.
Il bridge risolve una vista corrente e invia intenzioni CWM semantiche:
QuickbarBind/Swap, InventoryArrange, Equipment o ItemTransfer; non esegue
IMoveAction gameplay e non modifica ottimisticamente contenuti/ruoli.

Lo swap verifica entrambi i token attesi sul thread proprietario nativo;
una discordanza rifiuta tutta l'operazione. Riordino e riferimenti non
pagano tempo perché sono solo disposizione UI. Le operazioni fisiche usano
i rami nativi esistenti: decisioni, accesso alle tasche, quantità, capacità,
costi, cancellazione e attività. UX-02 riapre il menu dopo il costo pagato,
mai alla sola ricezione del primo risultato. F7/lavoro/recovery non accodano
input fisici per una ripresa successiva.

`item_vars.cwm_inventory_position` conserva il rango opzionale 1–2048 sulla
vera istanza; valori assenti/malformati esportano zero. Nessun ID effimero
entra nel save. Copie/spostamenti nativi conservano il rango; stacking
integrato ignora questa chiave UI, split la mantiene solo sull'originale.
Il reader nativo indipendente conferma ordine distinto dei due sassi,
identità, quantità e ruoli; il reload reale verifica le stesse istanze.
Questo è un riscontro di compatibilità circoscritto: SAVE-001 completo resta
OPEN, M5.5 rimane storico FAILED.

## Verifica e limiti

Build incrementali sui sorgenti ricostruiti, senza dichiarare un clean build.
Native: **173 casi / 185.813 asserzioni**; protocollo **10/10**; Luanti
**308 test**, più **648 asserzioni / 4 casi**. Renderer reale sotto Xvfb
privato: hotbar/riordino, annullamento, mano/indossati, quantità/righe
contenitore/Terra, costi/decisioni/pausa, capacità, riconnessione, consumo e
salvataggi. Prove dei runtime installati e reload usano il normale launcher
con default continuo 4× e soltanto copie isolate, mai mondi personali.
Le icone contenitore della griglia condividono il percorso verificato delle
righe nella sottovista: questa destinazione è anche nella nuova prova manuale.

Entrambi i runtime 2.18 sono installati insieme, con checksum e copie di
rollback della precedente coppia 2.17. Le ricevute conservano anche tentativi
falliti: generazione senza mutatori, avvio del test nella directory sbagliata,
reset del display virtuale e due fixture che confondevano ordine/identità.
Non sono riscritti come prove passate.

[Backlog manuale](../validation/pending-manual.md): **13 PENDING**, inclusi
ricontrollo del vecchio FAIL e due nuovi punti per equipaggiamento/contenitori.
I tre ricontrolli UX-03 già accettati restano PASS. Non serve testarli oggi.
Lingua inglese/italiano WIP e mira RMB seguono; contenitori esterni,
quantità selezionate nel pickup, tasche manuali, sigilli/liquidi e batch moves
richiedono fette dedicate. Rig/UV, animazioni/audio e dialoghi ricchi restano
nel piano, senza essere dichiarati risolti da questo intervento.
