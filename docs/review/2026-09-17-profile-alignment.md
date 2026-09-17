# Profile alignment and persona construction — 2026-09-17

> 2026-09-17 · verified at `d5b9b8f` · Claude Opus 5

For the package author, before any profile code exists. It settles what a profile is in asrai, what it
may and may not touch, where its ledger lives and when it is injected, and on what terms a persona may
be built at all. It decides no field names as shipped contracts; those land with the implementation and
in `conventions.md` §1a. What it does decide is the one thing that is expensive to change later: the
direction of authority between a measurement and a reader.

## 1. The persona is the audience, not the model

A profile in asrai models **the person receiving the output**. It is not a costume the model wears.

The distinction is not pedantic; the two have different mechanisms and opposite evidence. A model given
a self-concept — "you are an expert art director" — shifts into instruction-following and measurably
loses factual discrimination. [PRISM](https://arxiv.org/html/2603.18507v1) measured MMLU falling from
71.6% to 68.0% under a long expert persona, math dropping 8.50 to 8.00 and coding 7.40 to 6.75 on 7B
models, with one math problem falling from 9/10 to 1.5/10; the longer the persona, the worse the damage.
Their fix is a gate that routes roughly 6% of knowledge queries to the persona and 73–78% of safety
queries. That is a real result about a real hazard, and it is a hazard asrai does not currently have.
It is recorded here so that if anyone later proposes giving asrai a voice — a bundled `SKILL.md`
persona, an art-director register for the MCP tools — the price of that specific thing is already on
the table and does not have to be rediscovered.

An audience model runs the other way. Nothing about the model's self-concept changes; what changes is
which rendering of an already-computed verdict the reader is handed.

**The precedence rule comes from a working system.** The author's Hermes agent profile reproduces a
character's register through a `voice_card`, and when accurate information has to be conveyed, the
expression layer recedes. That is not a prohibition on expression. It is an ordering:

> Judgment outranks expression. Where they conflict, expression yields.

This is `runbook.md` §1 applied to a new pair, and it is verifiable rather than declared: for one asset
and one set of answers, **every profile must produce a byte-identical `verdict` and `record`**, with
only the rendering differing. One equality test is the whole gate.

Two consequences follow, and the second is the one that constrains the design.

- **"The model must apply a profile" is not an invariant.** No profile is the default. A profile is an
  optional projection onto output that is already complete without it, which is what makes the on/off
  switch coherent: "off" is the full default surface, not a model that has stopped being anyone.
- **A profile is a realm without authority.** It has no invariant of its own to defend, only a
  rendering to select. In the ledger's terms its verifier is the equality test above, and it may never
  be cited as the reason a verdict says what it says.

The three profiles already exist. `spec.md` §1 names three readers as `[decided]` — no art training,
an artist, an art director — with a column headed *what asrai owes them*. That table is an audience
model written eleven days before this review, and the profile system's whole job is to make its third
column operational. Nothing here defines a new reader; a `profiles` file points at that table and
holds only the rendering consequence, so the reader stays owned in one place.

## 2. What the practice has already paid for

Persona construction has thirty years of accumulated receipts. Read as gains, costs, delayed failures
and free leverage, they decompose cleanly.

**What it gets you.** Alan Cooper's original argument is the one nobody has successfully disputed: a
named persona stops the *elastic user*, the imaginary person a team stretches to justify whatever it
already wanted to build. [Proto-personas](https://www.senseandrespond.co/blog/proto-personas) add a
second gain that is purely about the team — they make implicit assumptions explicit and arguable, which
is a different good from being accurate. Our own persona tour is the local instance: three projections
of one repository found three nearly disjoint defect sets, and none of the three would have surfaced
the others.

**What it costs.** [NN/g's three types](https://www.nngroup.com/articles/persona-types/) are a price
list, and the useful part is that each tier buys a *different claim*, not more of the same claim.

| type | evidence | cost | may claim | may not claim |
|---|---|---|---|---|
| proto / lightweight | no new research; team assumptions | a 2–4 hour workshop | shared direction; assumptions made explicit | accuracy about real users |
| qualitative | 5–30 interviews, coded to saturation | moderate, parallelisable | motivations, expectations, the *why* | what share of the population each covers |
| statistical | qualitative pass **plus** 100+ (ideally 500+) survey and clustering | high; needs statistical expertise | population proportions; outliers not overweighted | more design utility than the qualitative tier — NN/g's own verdict is "cracking a walnut using a hydraulic press" |

The third row is the important one. Paying the largest price does not buy a better persona; it buys a
*proportion*, and only a team that needs proportions should pay it.

**The delayed failure modes.** These are delayed precisely because a persona works fine until someone
acts on it as though it were a measurement.

1. **It cannot be falsified.** [Chapman and Milham
   (2006)](https://journals.sagepub.com/doi/10.1177/154193120605000503) is the sharpest critique the
   field has: personas cannot be adequately verified or falsified and therefore have no demonstrable
   validity, and the practical consequence is political — a persona becomes a way to settle a question
   that data should have settled.
2. **The composite describes nobody, and does so faster than anyone expects.** [Chapman, Love, Milham,
   ElRif and Alford
   (2008)](https://quantuxbook.com/papers/REPRINT-HFES08-chapman-love-milham-elrif-alford.pdf) built a
   formal model and tested it against six survey datasets from N=268 to N=10,307 plus two simulated
   sets, generating 10,000 random persona-like descriptions per dataset. Expected prevalence falls
   rapidly as attributes are added. Their recommendation is to assess a persona's prevalence
   empirically before assuming it describes a group of people at all. The operational reading is
   blunt: **every attribute you add is a cost paid in prevalence**, so a persona should be as short as
   it can be and still be useful. This review did not obtain the per-attribute figures; the paper
   holds them and a reader acting on the magnitude should go and get them.
3. **A proto-persona becomes an echo chamber.** NN/g names it directly: with no research behind it,
   the artefact can simply amplify the team's existing wrong assumptions, and the team then concludes
   that personas are worthless rather than that this one was unvalidated.
4. **Fluency buys trust that validity has not earned.** The LLM-era failure mode reported across the
   [synthetic-users critique](https://dl.acm.org/doi/10.1145/3745900.3746108) is *convincing mimicry*:
   synthetic output is trusted because it is articulate, opening a gap between perceived and actual
   reliability, with reported tendencies to flatten identity groups and describe users in a uniformly
   positive light. This repository already has a name for that defect. `conventions.md` and the
   repository-operating skill both say that a claim nothing computes is prose, and that prose reading
   as measured is the failure already fixed twice here. A generated persona is the same defect wearing
   a face.

**The free leverage.** Two moves cost nothing and are worth taking every time.

- **Microsoft's [Persona Spectrum](https://inclusive.microsoft.design/articles/inclusive-101-guidebook)
  turns one persona into three by varying only how the constraint was arrived at** — permanent,
  temporary, situational. Their own worked example: one-handed use covers roughly 26,000 people with
  arm amputations, about 13 million with a temporary injury and around 8 million in a situational
  bind, so the same design reaches on the order of 21 million. This is evidence perturbation under a
  different name: hold the constraint fixed, vary the evidence that produces it, and read what the new
  view exposes. It is the strongest external precedent for the method proposed in §4.
- **Subtracting attributes is free and improves prevalence**, per failure mode 2. The only persona
  discipline that costs nothing is keeping it short.

## 3. Why the evidence-perturbation view survives the field's own critique

Chapman and Milham's objection is fatal to a persona that claims to describe people: there is no
observation that would disconfirm it.

A persona built as a projection makes a different claim, and the difference is what saves it. It does
not assert *this person exists*. It asserts **this path through this artefact reaches, or fails to
reach, this thing** — and that is checkable by walking the path.

Our own tour is the demonstration. Nobody was recruited. One sample, this repository, was projected
through three evidence tuples: what is reachable by a reader with no art vocabulary, by a technical
artist, by a contributor who does not read English. Each projection returned a falsifiable claim, and
each was then falsified or confirmed by running it. The unfilled form returning `yes` on five surfaces
was a prediction of the first projection, and `git` now holds its correction. The `--compact` blur came
out of the second, the translation drift out of the third.

This is `spec-perturbation` mode 2 exactly as the skill defines it: the sample is fixed, the evidence
tuple is perturbed, and the cost is a projection rather than a new probe. The persona is what that
projection looks like when it is given a face so a human can reason with it.

The discipline that keeps it honest is one field. A projection must stay **false-detectable as a
projection** — never silently promoted to evidence about real humans. That is the same rule as
`basis: stereotype` in §4's ledger and the same rule as the repository-operating skill's requirement
that a declared absence of authority stay false-detectable. Failure mode 4 is what happens when it is
dropped, and the drop is always silent, because a fluent persona reads exactly like a researched one.

## 4. The three schemas

Sketches, not contracts. Names are argued in `conventions.md` §1a when they ship.

**A — stock profiles, the stereotype layer.** Three rows, and every rendering axis falls out of
`spec.md` §1's third column rather than being invented here. The file cites that table; it never
restates it.

| axis | no art training | artist | art director | the clause it serves |
|---|---|---|---|---|
| `vocabulary` | avoid | assume | assume | "without vocabulary" |
| `basis` | on request | always | on request | "the basis of every claim" |
| `settled_rows` | sentence | show | silence | "silence on what the measurement can settle" |
| `contested_band` | hide | show | hand over | "handed over with its evidence attached" |
| `unknown_reads_as` | hold | hold | hold | "`unknown` must never read as fine" |

Five axes, closed enums, no narrative sentence anywhere. Failure mode 2 says keep it short; PRISM says
a long persona is also the expensive one. Both point the same way, which is why the shortness is easy
to hold.

**B — the overlay ledger, the adaptive layer.** The classical decomposition
([Brusilovsky and Millán](https://link.springer.com/chapter/10.1007/978-3-540-72079-9_1)) is that a
stereotype seeds an overlay, evidence updates the overlay, and the overlay overrides the stereotype.
asrai can adopt it directly because the domain model already exists: 475 terms in 22 categories, with
`confusable_with` on 47 of them and `quantification.mode` in 8 values.

A row, keyed by scope rather than by person:

```text
scope    category:lighting | term:lighting.rim_light
state    stereotype | seen | used | overrode
basis    stereotype | observed | declared
evidence <record id | run id>        required unless basis is stereotype
at       ISO 8601
by       <profile id>
```

Three properties earn their place.

- **`state` names an observed event, never a state of knowledge.** "Knows" is not observable; "used
  this term in an answer" and "overrode a verdict on this scope" are. This is the discipline that
  keeps asrai from inventing a magnitude, applied to a second quantity.
- **Most rows are derived, not authored.** `records.jsonl` already carries `observer`, `term_id` and
  `level`, and `spec.md` §1 already keeps the director's override as precedent. The overlay is a
  materialised view over that corpus, so it is recomputable and never needs repair — the explicit
  write path exists for what the corpus cannot see, and is marked `declared` so the difference stays
  visible.
- **It is language-invariant.** Scopes are term ids, so a Korean contributor's ledger and an English
  contributor's ledger are the same artefact under the same schema. No prose in any language ever
  enters it. This is what keeps the 2026-09-17 translation-scope decision in `docs/i18n/README.md`
  from having to reach the profile system at all.

The write surface is two verbs, and the first refuses a row whose basis claims observation without
evidence, at the same trust boundary `record` already defends.

**C — the projection record, for `persona-build`.** The output of building a persona is not the
persona. It is the derivation, and this is the field that carries §3's discipline:

```text
artifact      what was projected (repo@rev, corpus, spec)
held          what was held fixed
varied        which evidence tuple was perturbed   <- the persona is this, anthropomorphised
licensed      what this view may claim: reachable / not reachable on this path
not_licensed  what it may not: real preference, frequency, satisfaction, population share
found         what only this projection exposed
```

`not_licensed` is the load-bearing field. It is also what makes the skill cheap to re-run: with
`varied` written down, the same projection against a later revision says what was repaired without
re-synthesising anything, which is where the token saving actually comes from. The reproducibility and
the economy are the same property.

One thing `persona-build` must not do is the last step of the published pipelines. The
[agentic-persona work](https://arxiv.org/html/2603.21846) clusters expert feedback and then has an LLM
synthesise a narrative profile at 40% / 25% thresholds. That narrative is exactly the long persona of
failure mode 2 and of PRISM's worst case. Cluster, threshold and record the derivation; emit the short
typed profile of schema A, not a biography.

## 5. Where the ledger is injected

`platform.claude.com`'s caching contract: render order is tools → system → messages, at most four
`cache_control` breakpoints, and matching is on the exact prefix, so one changed byte at position N
invalidates every breakpoint at or after N. Reordering to put volatile content first does not help,
because everything before a breakpoint must still be byte-identical.

The placement follows once the actual volatility of each half is measured rather than assumed.

| | changes | placement |
|---|---|---|
| stock profile (schema A) | between sessions | system, before a breakpoint; cached |
| overlay (schema B) | **within a session: not at all** | after the last breakpoint, injected once |
| which scope is active | every turn | not injected; derived from the query |

The middle row is the correction this review exists partly to record. A first pass assumed the overlay
was continuously self-editing, which is Letta's model —
[memory blocks](https://www.letta.com/blog/memory-blocks/) are pinned to the context window and the
agent rewrites them with tools as it learns. That model is right for an open domain and wrong here,
for two reasons. A person's demonstrated vocabulary does not meaningfully change inside one session:
someone who used a term correctly at turn 3 is the same reader at turn 40. And fast adaptation is a
known harm in its own right — [Lavie and
Meyer](http://www.cs.tufts.edu/~jacob/250aui/AdaptiveBenefits_Lavie_IJoHCI10.pdf) and the adaptive-menu
literature record that frequency-reordered interfaces reduced performance and disoriented users, while
slow-paced adaptation helped.

So `note()` appends to disk; it does not mutate context. A write takes effect at the next session or at
an explicit profile switch, which is a rare, human-initiated event — the event the hook was always
described as firing on. Nothing invalidates mid-session, and a profile switch costs the messages
segment only.

There is one genuinely per-turn variable, which scope is under discussion, and it is not part of the
profile. It is the query, derivable from what is being asked, and it stays out of the injected block.
This is the useful residue of [ExPerT's](https://arxiv.org/pdf/2607.01242) finding that expertise is
domain-local and a single global profile under-serves it; the answer is that the overlay is keyed by
scope, not that it must be recomputed continuously.

## 6. What this does not decide

- No field name is a contract. Schemas A, B and C are sketches; `conventions.md` §1a takes them when
  they ship, with rejected alternatives.
- The equality test of §1 is specified and not written. Until it exists, "expression yields" is a
  claim, not a gate — and claiming a gate that does not exist is the defect this repository names in
  its own skill.
- Whether the verdict gains a `basis` on the four subject surfaces that lack one — `specular`,
  `ambient`, `rim`, `albedo` — is a separate question the artist profile exposed and does not answer.
  It is an implementation gap independent of profiles.
- Nothing here licenses generating a persona of a real contributor, or storing anything about an
  identified person. The ledger's scopes are term ids and its states are events on this repository's
  own artefacts.
- The prevalence figures behind failure mode 2 were not obtained. The direction is established and the
  magnitude is not, which matters if anyone proposes a schema A with more than a handful of axes.
