---
name: persona-build
description: Use before shipping something a stranger has to land on cold, or when a team is about to argue about "the user" - spec-perturbation mode 2 over an artifact you already have, producing end-user personas as falsifiable projections rather than descriptions of people.
---

# persona-build

spec-perturbation **mode 2**: the sample is an artifact that already exists — a repository, a product,
a contract — and the projection is what that artifact affords along one path through it. A persona here
is that projection with a face on it, so a human can reason with it.

**A persona is the audience, not a costume.** It models who receives the output. It is never a
self-concept handed to a model, which is a different mechanism with a measured cost: an expert persona
raises instruction-following and lowers factual accuracy, worst when it is longest. If someone wants
the model to *sound* like someone, that is a separate decision with its own price and this skill does
not cover it.

## Why not just describe your users

The field's sharpest objection is that a persona cannot be verified or falsified, so it has no
demonstrable validity and becomes a way to settle by politics what data should have settled
(Chapman & Milham 2006). The second objection is quantitative: expected prevalence falls rapidly as
attributes accumulate, so a composite with enough fields describes nobody
(Chapman, Love, Milham, ElRif & Alford 2008).

A projection escapes the first because it makes a different claim. It does not assert *this person
exists*. It asserts **this path through this artifact reaches, or fails to reach, this thing** — and
a path can be walked, so the claim can be wrong in a way somebody notices.

It does not escape the second. Every attribute still costs, so the deliverable is short by
construction.

## The move

1. **Fix the sample.** One artifact, at one revision. Write down which.
2. **Choose what to hold and what to vary.** The varied dimension is the persona. Vary one thing:
   what the arriver already knows, what they can read, what they came to do, what they are allowed to
   touch.
3. **Walk each path for real.** Run the commands. Read what comes back. A projection that was reasoned
   about rather than executed is a description, and descriptions are what this skill exists to replace.
4. **Record what only that path exposed.** If two personas find the same set, one of them was not a
   different view.
5. **Write the projection record, not the persona.** The record is the reusable artifact; the persona
   is its readable surface.

**The spectrum trick is free.** Microsoft's persona spectrum varies how a constraint was arrived at —
permanent, temporary, situational — and turns one persona into three at no extra research cost, while
enormously widening who the finding covers. Ask it of every constraint you name: who else arrives here
by a different road?

## The record

One per projection. Six fields, and the fourth and fifth are the ones that keep it honest.

```text
artifact      what was projected, pinned: repo@rev, a corpus, a document at a revision
held          what was held fixed across every persona in the set
varied        the dimension perturbed - this, anthropomorphised, is the persona
licensed      what this view may claim: reachable / not reachable on this path
not_licensed  what it may not: real preference, frequency, satisfaction, population share
found         what only this projection exposed, each item pointing at the run that found it
```

`not_licensed` is load-bearing. A projection is evidence about an artifact and never about people, and
the drop from one to the other is always silent, because a fluent persona reads exactly like a
researched one. That is the live failure mode: synthetic-user output is trusted *because* it is
articulate, which opens a gap between how reliable it reads and how reliable it is. Name the gap in the
artifact itself, where the next reader cannot miss it.

`varied` is what makes the set cheap to re-run. With it written down, the same projection against a
later revision says what was repaired without re-deriving anything, and that is where the saving is:
reproducibility and economy are the same property here.

## What it costs, by tier

Know which one you are buying. Each tier buys a *different claim*, not more of the same one.

| tier | evidence | buys | cannot claim |
|---|---|---|---|
| projection (this skill) | an artifact you already have | what a path affords; findings that can be walked | anything about real people |
| qualitative | 5–30 interviews to saturation | motivations, expectations, the why | what share of anyone each covers |
| statistical | the qualitative pass **plus** a large survey and clustering | population proportions | more design utility than the tier below it |

The bottom row is the trap. Paying the most does not buy a better persona; it buys a proportion, and
only someone who needs a proportion should pay for it.

## Failure modes

- **Echo chamber.** With no artifact under it, the set amplifies what the team already believed. The
  fix is step 3: the artifact talks back, or you did not run one.
- **Promotion.** A projection quietly becomes "our users want X". `not_licensed` exists to make that a
  visible edit rather than a drift.
- **Attribute creep.** Each field added shrinks who the row describes. If a persona needs a
  biography, it has stopped being a view.
- **Convergent sets.** Three personas returning one finding set means one dimension varied, not three.
  Re-cut `varied` before trusting the coverage.
- **Rendering as judgment.** When a persona drives what a system *says*, expression must yield to
  judgment: the underlying finding is identical for every persona, and only the saying differs. If a
  persona can change a verdict, it has stopped being an audience.

## When not to use this

When the question is about people rather than about an artifact — what they would pay, which they
prefer, how often they do it — no projection answers it and this skill will produce a confident
answer anyway. Go and ask someone. Mode 2 exhausts one sample; it does not replace a second.
