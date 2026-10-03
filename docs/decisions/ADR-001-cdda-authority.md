# ADR-001: CDDA owns gameplay and time

Status: ACCEPTED (original specification §5, §30, §32–35; amendments §4, §24–25).

CDDA validates and executes gameplay through its canonical rules. CWM inputs
are requests, not client-authored state. Luanti may interpolate visuals and
raycast targets; those operations cannot mutate authoritative coordinates,
health, inventory, terrain or time. The standalone launcher has no gameplay
role. Reconnecting must not add creatures or replay already executed commands.

The present handwritten turn loop, synthetic USE/fire action and incomplete
input checks require conformance review. Process separation alone does not
prove equivalent CDDA gameplay.
