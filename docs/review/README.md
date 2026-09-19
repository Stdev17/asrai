# `docs/review/` — dated reviews

Decision records. Each one is a snapshot of what was known and decided on a day, written for a named
reader, and **never edited afterwards**: if a decision changes, a later document supersedes it and the
old one stays as it was. That is the same rule the record corpus follows (spec.md invariant 6), applied
to prose.

| document | for whom | what it settles |
|---|---|---|
| [`2026-09-13-art-direction-skill-scenario-review.md`](2026-09-13-art-direction-skill-scenario-review.md) | the package author, pre-implementation | the design review the whole package was built from. The reasoning behind the playbook below lives here |
| [`2026-09-13-art-direction-skill-playbook.md`](2026-09-13-art-direction-skill-playbook.md) | a team routinising first-pass art direction | the procedure written before implementation. Its revision 2 records the eight points on which `spec.md` supersedes it, so read the spec first and this for the reasoning. It sat at the repository root until the documentation pass; nothing in it changed but its own two links |
| [`2026-09-13-art-direction-artist-brief.md`](2026-09-13-art-direction-artist-brief.md) | an artist, not a programmer or TA | a fifteen-minute brief; its last two tables ask the artist to mark **need / do not need / want**, which is how the feature list gets grounded in someone's actual work |
| [`2026-09-13-asrai-zium-dagga-operating-outlook.md`](2026-09-13-asrai-zium-dagga-operating-outlook.md) | the package author as game designer | an outlook review against the implementation as it then stood. Its recommendations are proposals, not approved revisions of spec.md |
| [`2026-09-13-embedding-provider-survey.md`](2026-09-13-embedding-provider-survey.md) | the package author, choosing a default | the two multimodal embedding models reachable through OpenRouter, their prices and token figures, and the 768-dimension decision. The prices live here rather than in `spec.md` §10 because a vendor's price list is not a contract asrai can keep |
| [`2026-09-15-ci-gate-discovery.md`](2026-09-15-ci-gate-discovery.md) `@da6def4` | the package author, before writing `.github/` | what an open-source CI gate is made of, what the precedents did with it, and the culture gap between a programmer's gate and an artist's contribution. Decides nothing; it names two defects to fix before CI exists and six questions only a human can answer |
| [`2026-09-15-art-direction-rationale.md`](2026-09-15-art-direction-rationale.md) `@aa46ada` | a reader a year from now, asking why the design says what it says | where every art claim in the design came from — published work, industry practice, measured here, or a person's choice — and the three that came from nowhere. The surface pass's eight sources and the estimator noise floor live here now, having been extracted from `CHECKPOINT.md` |
| [`2026-09-16-authority-and-release-gate.md`](2026-09-16-authority-and-release-gate.md) `@ea6ae95` | contributors and future maintainers | that human-maintained documents outrank a generated spec, which outranks code; that the lighting cutoffs remain unverified policy; and what the first release gate actually installs. Supersedes this index's earlier description of `CHECKPOINT.md` as rewritten |
| [`2026-09-16-commit-policy.md`](2026-09-16-commit-policy.md) `@78266a1` | the author, adopting a supplied policy | the typed subject, the `Owners`/`Fixes`/`Values`/`Deviation`/`Source` trailers and the two hooks, with the byte provenance of the supplied files. Written after the stamp rule and carrying no stamp; its three values are in the table below |
| [`2026-09-16-owner-boundaries.md`](2026-09-16-owner-boundaries.md) `@efe9802` | the author, adapting another repository's conventions | decomposition by owned invariant, the signature-only graph, and the human scope decision that a crowded diagram is a boundary review rather than permission to become a tool system |
| [`2026-09-17-profile-alignment.md`](2026-09-17-profile-alignment.md) `@de47ef8` | the package author, before any profile code exists | that a profile models the reader rather than the model, that judgment outranks expression with a byte-equality test as the gate, where the profile ledger lives and when it is injected, and on what terms a persona may be built. Decomposes thirty years of persona practice into what it gets you, what it costs, what fails late and what is free |
| [`2026-09-17-family-and-run.md`](2026-09-17-family-and-run.md) `@1e8a782` | the package author, before the readability family exists | that a surface family is data over a shared run rather than a tool, that an owner of one run consumes the families and owns both reading the input once and ordering them, and that every surface presenting a run — to a reader or to a model — belongs to that owner and may not move a verdict. Measures what a second family costs at `a2ad5ae`: the tool surface goes over its hard cap, and one flood fill is already written twice |
| [`2026-09-18-the-run-answers-once.md`](2026-09-18-the-run-answers-once.md) | the package author, after the run owner exists and before it judges anything | that a run answers once — the verdict, the record and every reading say the same thing, and what a run hands out is valid before it leaves — and that the record builder and the three axes are the run's on that rule. Measures at `9ea08f1` the flow `spec.md` §7.1 calls valid: on every fixture the record the ledger returns is rejected by the tool that stores it, a run warns a reader and tells the corpus nothing, and the required `observer.model` check lets a null through where it catches an empty string |
| [`2026-09-20-one-run-one-voice.md`](2026-09-20-one-run-one-voice.md) | the package author, after the axes reached the record | that the presentation layer is the run's output stage and assembles typed data, so that a family reports findings and never a voice. Settles the file question `2026-09-17-family-and-run.md` §8 left open: it is a module, because a renderer living inside a family is a renderer with a branch per family. Measures the move at `008eadc` — every reading over every fixture, form state, profile and overlay, byte for byte identical — and names the five deletions that turn it red |
| [`2026-09-20-readability-before-colour.md`](2026-09-20-readability-before-colour.md) | the package author, choosing the second family | that readability is next and shape is not a family at all — the vocabulary calls a silhouette measurable and its readability `proxy_only`, so shape is a measurement `measure.v1` mostly already takes and readability is the judgment over it. Answers the first two bullets of `2026-09-17-family-and-run.md` §8 with five surfaces, no subjects and a scale ladder that belongs to the run, and corrects that review's §7 budget: `reading` took node eight, so the scope review of `conventions.md` §0 falls due one family earlier than forecast |

## Naming and the stamp

`YYYY-MM-DD-<topic>.md`. The date is the day it was written, not the day a decision took effect.

Since 2026-09-15 every review opens with a stamp naming the day, the revision its facts were checked
against, and the author:

```text
> 2026-09-15 · verified at `cdf7802` · Shelby Yoon
```

A reader can then tell how old the reasoning is without running `git log`, which is the whole point:
these files are never edited, so the only thing that can go stale is the reader's assumption about when
they were true. The five written before the rule carry no stamp and are not edited to add one. One later review
missed the rule and cannot be corrected in place either, because a review is never edited. Their
provenance is here instead:

| document | written | added to the repository | author |
|---|---|---|---|
| `2026-09-13-art-direction-skill-scenario-review.md` | 2026-09-13 | `91a4bc7` | Shelby Yoon |
| `2026-09-13-art-direction-artist-brief.md` | 2026-09-13 | `91a4bc7` | Shelby Yoon |
| `2026-09-13-asrai-zium-dagga-operating-outlook.md` | 2026-09-13 | `91a4bc7` | Shelby Yoon |
| `2026-09-13-art-direction-skill-playbook.md` | 2026-09-13 | `18752ef`, moved here from the repository root | Shelby Yoon |
| `2026-09-13-embedding-provider-survey.md` | 2026-09-14 | `18752ef`, extracted from `spec.md` §10 | Shelby Yoon |
| `2026-09-16-commit-policy.md` | 2026-09-16 | `78266a1` | Codex |

## When to add one

Write a review when a decision is **hard to reverse and the reasoning will not survive in a diff**: a
boundary, an axis, an evidence rule, a refusal. Small rejected alternatives do not need a document —
they belong in the table in [`../conventions.md`](../conventions.md) §1a, which is where a contributor
looks for "why is this field named that".

A review is not a status update. [`CHECKPOINT.md`](../CHECKPOINT.md) is for status; it is append-only
and these are frozen, which are different rules for different reasons. The sentence this paragraph
used to end with called that file rewritten, which it stopped being on 2026-09-15.
