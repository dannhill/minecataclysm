# Riscontro umano: recupero e continuità dei menu — 2026-10-26

Fonte: messaggi diretti dell'unico sviluppatore umano. Documento redatto da
un LLM sulle sue direttive; non è una verifica automatica.

«1 PASS e 2 PASS» conferma FB-01.1 (cursore/conferme) e FB-01.2 (recupero
della lattina) dopo la correzione dell'avvio CWM2.36. La successiva precisazione
conferma espressamente che le validazioni rimangono valide.
I due FAIL di avvio sono quindi chiusi; i 58 PENDING non cambiano.
UF8-01.1 non è stata validata da questo messaggio.

Nuova segnalazione: quando si cancella un'azione o si attraversano schermate
correlate, il menu si chiude, appare brevemente il gioco, poi un altro menu si
riapre. Il developer richiede di mantenere visibile l'interfaccia e sostituirne
la schermata; consente che il tempo necessario all'azione avanzi col menu
visibile. Non richiede di rendere gratuite azioni/cancellazioni o rimborsarle.

Implementazione da verificare: separare presenza della finestra e pausa del
coordinatore, conservare una vista modale di attesa/progresso durante l'azione,
passare direttamente a conferme/risultati/inventario/crafting. Pausa ordinaria,
sicurezza, costi, interruzioni e salvataggi rimangono autorevoli CDDA. Uscire
volontariamente verso il mondo rimane un gesto distinto.
Un nuovo ricontrollo MENU-01.1 porta il backlog a 59 PENDING, nessun FAIL aperto;
non revoca i PASS esistenti e non accetta automaticamente la nuova presentazione.
