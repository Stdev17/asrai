# `docs/review/` — dated reviews

Decision records. Each one is a snapshot of what was known and decided on a day, written for a named
reader, and **never edited afterwards**: if a decision changes, a later document supersedes it and the
old one stays as it was. That is the same rule the record corpus follows (spec.md invariant 6), applied
to prose.

| document | for whom | what it settles |
|---|---|---|
| `2026-09-13-art-direction-skill-scenario-review.md` | the package author, pre-implementation | the design review the whole package was built from. The reasoning behind the playbook below lives here |
| `2026-09-13-art-direction-skill-playbook.md` | a team routinising first-pass art direction | the procedure written before implementation. Its revision 2 records the eight points on which `spec.md` supersedes it, so read the spec first and this for the reasoning. It sat at the repository root until the documentation pass; nothing in it changed but its own two links |
| `2026-09-13-art-direction-artist-brief.md` | an artist, not a programmer or TA | a fifteen-minute brief; its last two tables ask the artist to mark **need / do not need / want**, which is how the feature list gets grounded in someone's actual work |
| `2026-09-13-asrai-zium-dagga-operating-outlook.md` | the package author as game designer | an outlook review against the implementation as it then stood. Its recommendations are proposals, not approved revisions of spec.md |
| `2026-09-13-embedding-provider-survey.md` | the package author, choosing a default | the two multimodal embedding models reachable through OpenRouter, their prices and token figures, and the 768-dimension decision. The prices live here rather than in `spec.md` §10 because a vendor's price list is not a contract asrai can keep |
| `2026-09-15-art-direction-rationale.md` | a reader a year from now, asking why the design says what it says | where every art claim in the design came from — published work, industry practice, measured here, or a person's choice — and the three that came from nowhere. The surface pass's eight sources and the estimator noise floor live here now, having been extracted from `CHECKPOINT.md` |

## Naming and the stamp

`YYYY-MM-DD-<topic>.md`. The date is the day it was written, not the day a decision took effect.

Since 2026-09-15 every review opens with a stamp naming the day, the revision its facts were checked
against, and the author:

```text
> 2026-09-15 · verified at `cdf7802` · Shelby Yoon
```

A reader can then tell how old the reasoning is without running `git log`, which is the whole point:
these files are never edited, so the only thing that can go stale is the reader's assumption about when
they were true. The five written before the rule carry no stamp and are not edited to add one — their
provenance is here instead:

| document | written | added to the repository | author |
|---|---|---|---|
| `2026-09-13-art-direction-skill-scenario-review.md` | 2026-09-13 | `91a4bc7` | Shelby Yoon |
| `2026-09-13-art-direction-artist-brief.md` | 2026-09-13 | `91a4bc7` | Shelby Yoon |
| `2026-09-13-asrai-zium-dagga-operating-outlook.md` | 2026-09-13 | `91a4bc7` | Shelby Yoon |
| `2026-09-13-art-direction-skill-playbook.md` | 2026-09-13 | `18752ef`, moved here from the repository root | Shelby Yoon |
| `2026-09-13-embedding-provider-survey.md` | 2026-09-14 | `18752ef`, extracted from `spec.md` §10 | Shelby Yoon |

## When to add one

Write a review when a decision is **hard to reverse and the reasoning will not survive in a diff**: a
boundary, an axis, an evidence rule, a refusal. Small rejected alternatives do not need a document —
they belong in the table in [`../conventions.md`](../conventions.md) §1a, which is where a contributor
looks for "why is this field named that".

A review is not a status update. `CHECKPOINT.md` is for status, and it is rewritten; these are not.
