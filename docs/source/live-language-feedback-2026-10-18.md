# Human acceptance and request for live language switching

After `a0bbf43`, the sole human developer wrote:

> ok funziona perfettamente. Ma non si può fare sì che il restart del gioco non sia necessario per cambiare la lingua?

The first sentence accepts the selected-language notice, closing its one deferred
readability check. The second requests removing the supervised-restart constraint.
This supersedes that product constraint in AGENTS/design; it does not authorize
replaying gameplay or native decisions to obtain translated labels. The new live
behavior has separate automated evidence and deferred personal checks. This
record is written by an LLM from the developer's direct message, not a human test
report for the subsequent implementation.
