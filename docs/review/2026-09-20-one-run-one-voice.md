# One run, one voice — 2026-09-20

> 2026-09-20 · verified at `008eadc` · Claude Opus 5

For the package author, after the axes reached the record and before a second family exists. It closes
the first bullet of [`2026-09-18-the-run-answers-once.md`](2026-09-18-the-run-answers-once.md) §6 —
*whether the presentation layer moves with the rest* — and the file question that
[`2026-09-17-family-and-run.md`](2026-09-17-family-and-run.md) §8 left open behind it.

The decision is the author's and is one sentence: **the presentation layer is the run's output stage,
and it assembles typed data. No owner speaks in its own voice.** What follows is what that costs, what
it would have been without the second half of the sentence, and what it does not buy.

## 1. Why the file move alone would have been a lie

`light.sentences` read `v["diffuse"]`, `v["cast_shadow"]`, `v["expected_key"]`, `s["bright_side"]`.
Moved into `run.py` unchanged, it would have been the lighting family's renderer under the run owner's
name — and the run owner's file would have learned what a shaded mass is. The rule
`2026-09-17-family-and-run.md` §5 states is about *who may address an audience*, and a renderer that
knows one family's fields cannot serve a second one without growing a branch per family. A branch per
family is every owner speaking in its own voice again, with one import statement hiding it.

So the boundary had to be somewhere the second family will not move: **a family reports findings, and
the run's output stage renders them.** That is testable today with one family, because the test is not
what the sentences say but which module is allowed to know.

## 2. The seam

A finding is a sentence and the four things a reader profile may do to it, which are exactly the four
axes `profiles.v1.json` already had:

```json
{"say": "...", "terms": [{"label": "ambient", "term": "lighting.ambient"}],
 "settled": false, "basis": "observer", "evidence": null}
```

- `settled` — a measurement decided this alone, so `settled: silence` may withhold it. The contested
  band is never marked settled: it is what that silence exists to leave behind.
- `terms` — the surfaces the line points at, carried beside the sentence rather than joined into it,
  because whether a term id may be said belongs to the reader (`vocabulary`) and to the corpus
  (`profile.overlay`). A sentence handed over with the ids baked in could not be unsaid for the reader
  who has no vocabulary to use one. Such a `say` ends at its colon and the reader completes it.
- `basis` and `evidence` — who decided, and the angle a contested line turned on. Both are suffixes,
  so neither can change the sentence carrying it.

`findings` never leaves `run.ledger`: the family returns them inside its pass, the run removes them and
hands them to `reading`. A reply carrying both them and the sentences built from them would say one
thing twice under two names, with nothing to stop the two from drifting apart.

## 3. What it proved

Every reading this package can produce, before and after, over every fixture, every form state
(unfilled, all lamps, all paint), all three profiles, with and without an overlay, plus phase one:
**one hundred and twenty-six readings and one hundred and sixty-two sentences, byte for byte
identical.** Expression did not move, which is the invariant the whole layer exists under.

Five mutations, each red:

| delete | what goes red |
|---|---|
| a transport's import of the run, replaced by a family's | the transport asks a family, not the run |
| `reading`'s family-free import list | the presentation layer knows which family spoke |
| `light`'s family-free import list | a family reaches for its own reader |
| the `settled: silence` check | the art director hears what a measurement settled |
| `pop` on `findings` | the plumbing ships on the wire |

The first three are a structural test over the import graph, which is the only kind that survives a
contributor who does not read this document. The rule it enforces is one line: a transport and the
presentation layer may not name a family, and a family may not name the reader.

One tier-2 advisory stands and is deliberately not registered: the `light.py` row of
[`src/asrai/README.md`](../../src/asrai/README.md) says *two-phase ledger*, which is the name
[`spec.md`](../spec.md) §7.1 gives the protocol and not a magnitude anybody chose. The row was touched
because that module's public surface shrank; the term in it did not move. Everything else the scanner
flagged was an English count that earned nothing, and those were reworded rather than registered — the
owner tally in the package README most of all, since a number that goes stale the next time an owner
arrives is worse than no number.

## 4. Two things deleted, for one reason

`for_reader` existed so that `None` meant one thing in both transports. Neither transport applies a
profile any more — `ledger` does, once — so the reason dissolved with the move and the wrapper went
with it. `conventions.md` §1a keeps the row: a rejected-name table that drops its entry when the name
is retired loses the reasoning that decided it.

`_profile(None)` fell back to `untrained`, so `None` meant *no reading* at one layer and *the plain
reading* at another. That is §1's second failure mode — two meanings under one word — and it was
reachable only from a test. `sentences` now requires a profile and `ledger` decides whether to ask.

## 5. What this does not decide

- **The model-facing half.** `2026-09-17-family-and-run.md` §5 gives the run owner two audiences: a
  reader, and a model that would be handed a family's execution steps on the response it already
  receives. Only the first exists. The second is what would prove the seam carries more than one
  audience, and building it now would be a second consumer invented to justify the first.
- **Family order and the reduction across families.** Unchanged from
  `2026-09-18-the-run-answers-once.md` §5: one family, so ordering is unobservable and a reduction is
  the identity function. Abstention still has to be told apart from `unknown` before either lands.
- **Whether a finding should carry its subject id.** It does not today, because `say` already names
  the subject and nothing groups or orders findings. The first consumer that needs to sort them is the
  one that decides the field, not this document.
- **The lighting thresholds**, which remain unverified implementation policy
  (`2026-09-16-authority-and-release-gate.md`).
