# Language preference regression after native reading

The sole human developer reported, after delivery `91393f7`:

> non mi fa impostare la lingua inglese su ./start.sh, quando premo mi si chiude il menu di esc e se riavvio il gioco rimane in italiano.

This reopens LANG-01.2 as a human FAIL for the current build. Earlier reported
PASS entries remain historical acceptance of the versions actually played.
Automated reproduction or a later fix does not constitute a new human PASS.
The previous 28 PENDING checks are unchanged.

The authorized repair is selecting/persisting English through the normal pause
menu and supervised launcher. The accepted restart requirement remains; this
report does not request live translation of an active session. Native options,
worlds and canonical saves must not be rewritten to change language.
