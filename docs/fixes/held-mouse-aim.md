# AIM-01 — Mira tenendo premuto il destro

Consegna del 2026-10-12, CWM **2.18**, installata nel normale `./start.sh`.
Con un'arma da fuoco impugnata, RMB mantenuto mira all'ostile percepito puntato;
clic sinistro spara una volta. Tenendo ancora il destro, la mira riprende dopo
il tiro. F resta un'alternativa da tenere premuta, R ricarica nativamente.
[Design](../design/held-mouse-aim.md) e [ricevute](held-mouse-aim-evidence.json).

RMB su una porta/finestra vicina apre; Shift+RMB chiude. Per una finestra aperta
si punta il davanzale, come prima. RMB sugli oggetti a terra conserva raccolta
singola/lista e consultazione durante pausa. Il gesto viene classificato alla
pressione: tenere un clic contestuale e cambiare inquadratura non avvia mira.
Con arma da fuoco, un ostile puntato ha priorità; accovacciarsi con Shift non
impedisce di mirare. Clic su pareti/pavimenti ordinari non invia OPEN inutile.
Il cache di aperture usa materiali CWM e coordinate stabili, non nomi dei nodi.
CDDA rivalida comunque stato, distanza, percezione e costi.

## Comandi e interruzioni

Il nuovo controllo risolve il clic perso durante AIM: un solo sparo/R esplicito
può attendere la fine del passo AIM già in corso, al massimo un secondo, con
identità di arma/bersaglio vincolate. Non accoda colpi dietro movimento, altri
colpi o lavori. Cancellano quel differimento pausa, menu, recovery, cambio
arma/bersaglio, nuovo contesto e timeout. Il client non inventa hit o anticipa
munizioni/danni. Tenere LMB non crea un trigger automatico.

Rilasciare RMB ferma nuovi passi di miglioramento. Il mantenimento nativo della
precisione già pagata resta quello precedente; non viene aggiunto un reset
artificiale del rinculo. Menu, F7, attività e reconnect richiedono rilascio e
nuova pressione per riprendere la mira. Il suggerimento espone RMB/F, Aiming /
In mira e rinculo CDDA; `aim_held` e `ranged_deferred` sono solo trace locali.

## Evidenze e limiti

Client ricompilato incrementalmente da sorgenti ricostruiti. **309 test Luanti /
47 moduli**, più **648 asserzioni / 4 casi Catch**; protocollo **10/10**.
Native, Mineclonia, cataloghi, launcher e schema non cambiano. La ricevuta riusa
le identità e le prove native della consegna LANG-01, senza chiamarle una nuova
build o nuova esecuzione della suite CDDA.

Renderer reale, Xvfb privato, input fisici xdotool, relay CWM senza mutazioni,
fixture e configurazioni isolate. Mira/sparo include una risposta IPC trattenuta:
un clic attende il passo AIM, poi aprire H cancella l'intenzione senza sparare
né consumare munizioni. Si verificano ripresa dopo tiro, rilascio, pausa/menu,
reconnect, neutralità, vuoto, ricarica e costi nativi. Lettore del core pinned
pristine: arma unica, munizioni conservate tranne un colpo reale, altre pile
intatte e attività canonica conclusa. La stessa suite gira anche sulla coppia
installata, attraverso start.sh.

Regressioni complete: finestre aperte/chiuse e Shift simultaneo/risposta di
postura ritardata, camera acqua/posture/pausa; raccolta selezionata e singola,
pausa, reconnect e assenza di duplicati nel save. Screenshot e check sono nella
ricevuta. Restano conservati i tentativi dell'harness falliti per window manager
assente, porta condivisa e lettura frammentata del numero del display virtuale;
non sono fallimenti di gameplay riclassificati come PASS.

Il client precedente è copiato per rollback; native e cataloghi mantengono gli
stessi checksum. Il continuo 4× resta predefinito. Non vengono usati mondi o
configurazioni personali. Queste prove sono compatibilità circoscritta: full
SAVE-001 resta OPEN, M5.5 storico FAILED.

[Backlog manuale](../validation/pending-manual.md): **18 PENDING**, aggiungendo
soltanto tre prove RMB ai quindici precedenti. Nessun nuovo PASS manuale dedotto
e nessuna prova richiesta oggi. Prossimo passo essenziale: contenitori esterni
e raccolta quantitativa, poi feedback/dialoghi. Mirino libero, bersagli neutrali,
archi, armi montate, rig/UV, animazioni e audio restano fette successive; questa
consegna non promette zoom o una nuova rappresentazione dell'arma.
