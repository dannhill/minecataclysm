# Current user directive: integrated product scope

Source: explicit user clarification in the current Codex conversation,
2026-10-03. This supplements the recovered agy conversation and takes
precedence where standalone-preservation requirements conflict.

> aggiungo una precisazione che puoi tranquillamente aggiungere al piano in corso d'opera. Non è assolutamente necessario preservare il codice di luanti o di mineclonia o di cdda che serve per utilizzi esterni rispetti a questo progetto a cui stiamo lavorando insieme. Ovvero, se per motivi di efficienza, efficacia, feature necessarie ecc... è più conveniente rimuovere della logica(o stravolgerla) che renderebbe i singoli progetti standalone inutilizzabili con lo scopo di efficientare o aiutare il progetto collettivo allora non esitare a rimuoverli. Tutto qua. Continua pure col tuo lavoro.

Engineering consequences:

- The integrated CDDA–Luanti presentation project is the product.
- Standalone usability, unused upstream features and upstream internal APIs
  are not release constraints. Remove or substantially change them when that
  improves the integrated product.
- Retain pinned upstream sources and native checks as useful audit/reference
  evidence, without treating every upstream feature or test as a product goal.
- Gameplay authority, canonical persistence and ordering/recovery invariants
  remain requirements. This code-scope permission does not establish that an
  unverified save migration or simulation change is correct.
- Complete the takeover audit, then plan targeted remediation and the next
  original-roadmap milestone around the integrated product. No wholesale
  preservation effort is required for unrelated standalone functionality.
