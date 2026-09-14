# `docs/review/` — dated reviews

Decision records. Each one is a snapshot of what was known and decided on a day, written for a named
reader, and **never edited afterwards**: if a decision changes, a later document supersedes it and the
old one stays as it was. That is the same rule the record corpus follows (spec.md invariant 6), applied
to prose.

| document | for whom | what it settles |
|---|---|---|
| `2026-09-13-art-direction-skill-scenario-review.md` | the package author, pre-implementation | the design review the whole package was built from. The reasoning behind `ART_DIRECTION_SKILL_PLAYBOOK.md` lives here |
| `2026-09-13-art-direction-artist-brief.md` | an artist, not a programmer or TA | a fifteen-minute brief; its last two tables ask the artist to mark **need / do not need / want**, which is how the feature list gets grounded in someone's actual work |
| `2026-09-13-asrai-zium-dagga-operating-outlook.md` | the package author as game designer | an outlook review against the implementation as it then stood. Its recommendations are proposals, not approved revisions of spec.md |

## Naming

`YYYY-MM-DD-<topic>.md`. The date is the day it was written, not the day a decision took effect.

## When to add one

Write a review when a decision is **hard to reverse and the reasoning will not survive in a diff**: a
boundary, an axis, an evidence rule, a refusal. Small rejected alternatives do not need a document —
they belong in the table in [`../conventions.md`](../conventions.md) §1a, which is where a contributor
looks for "why is this field named that".

A review is not a status update. `CHECKPOINT.md` is for status, and it is rewritten; these are not.
