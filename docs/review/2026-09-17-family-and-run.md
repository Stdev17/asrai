# The family and the run — 2026-09-17

> 2026-09-17 · verified at `bf4251a` · Claude Opus 5

For the package author, before the readability family exists. It settles what a surface family **is** in
asrai, who owns a run that consumes several of them, and which of today's single-family facts are
design rather than accident. It names no field as a shipped contract; those land with the
implementation and in `conventions.md` §1a. What it settles is the part that is expensive after a
second family exists and nearly free before: where the shared things live.

Two of its decisions are the author's, taken on 2026-09-17 and recorded here rather than derived:
**a family is a parameter, not a tool**, and **an owner that owns one run consumes the families**.
Everything below either supports those or works out what they cost.

## 1. The view, and what it measured

This is `spec-perturbation` mode 2. The sample is this repository at `a2ad5ae`; the view was written
before the reading and is one question:

> Which statement in these documents is true only because there is exactly one family?

Mode 1 was unavailable — there is no harness that accepts or rejects a second family, because the
second family is what would build it. Seven readings came back. Four are quoted here because they are
measurements rather than opinions; the other three are in §5 and §6 where they decide something.

**The tool surface fails on the second family.** The `tools/list` reply, which a host re-sends on every
turn, is 3,810 bytes — 896 tokens against a 1,000-token soft and 1,200-token hard cap (`spec.md` §6).
`light_ledger` is 1,350 of those bytes, 35.4% of the surface and the largest single entry. A second
family built as a second tool of the same shape puts the surface at 5,160 bytes, **1,214 tokens, over
the hard cap**, and the test that holds it fails. The cheap way to pass is to cut sixty bytes of prose,
which passes the test and leaves the actual duplication in place: all six of `light_ledger`'s
parameters — `path`, `subjects`, `capture`, `mirror`, `answers`, `profile`, 624 bytes of schema — are
family-agnostic, and every byte of them would be copied.

**Duplicate invention is already here, with one family.** `measure._components` and `light._label` are
the same 4-connected flood fill, written twice in pure Python with the same neighbour walk and the same
stack. One returns a count, the other a label array; the count is `labels.max()`. Neither module knows
the other exists. Whatever a second family costs, this was not caused by it.

**Most of `light.py` is not about light.** Split by vocabulary, of 1,028 lines roughly 196 carry no
lighting word at all — subject and box and depth and mask handling, the label and erode and dilate
primitives, the vector helpers, the whole profile rendering layer. Another ~230 are the two-phase
protocol written in lighting terms: issuing the form, validating answers, building the record,
sequencing the run. The genuinely lighting-local remainder is about 600. The split is crude, and the
conclusion survives being crude: the majority of the module is not the family.

**Every term the readability family would record is `proxy_only`.** `perception.readability`,
`silhouette_readability`, `icon_readability`, `scale_readability`, `material_readability` and
`shape.contour_economy` all are. Every term the lighting pass asserts is `measurable_with_context` or
`structural`. Invariant 3 keeps a `proxy_only` term from taking a `set` or a delta and `lint` enforces
it; nothing said the same on the observation side, so a `decided_by: measurement` surface could record
a proxy at `asserted` and claim evidence the vocabulary itself denies. Fixed at `233bde1`, on the
surface policy rather than on the record, because `spec.md` §7 gives an observer a second route to
`asserted` — the same answer at all three scales — which is open to any term and is not asrai's to
refuse. The same pass found that `surfaces.v1.json` had no machine verifier at all beyond its manifest
digest, in the one realm whose row requires one.

## 2. A family is data over a shared run

A **surface family** is a domain's worth of appearance questions: which surfaces exist, which tier
decides each, what the measurement computes, what the thresholds are, and what the findings are called.
The lighting family is the first. Readability is the second.

What a family is **not**, each ruled out by something above:

- not a tool. §3 and §4.
- not a mode. `physical | fake_lighting | engine_lit` are expectations *within* the lighting family and
  do not generalise; a mode changes what a verdict means, a family changes which questions exist.
- not a subsystem. A family owns thresholds and measurements, not a boundary; §7 is where that bill
  comes due.
- not a realm. Realms own classes of invariant, and two families own the same class.

The unit that does generalise is the **run**: one input, read once, judged by one or more families,
answered once, recorded once.

## 3. Why the run is an owner and not a facade

`conventions.md` §0 has the sentence that would reject this proposal:

> Grouping independent invariants under a facade does not reduce the owner count.

A module that calls `light`, then `readability`, then merges is exactly that facade, and it would buy
nothing. The run owner survives the test because it owns two invariants of its own, and neither of them
can be held by a family, because both are about what happens *between* families.

**One run reads its input once.** Every family in a run sees the same bytes, the same subject list and
the same `asset_sha256`. A family may not load the file, derive subjects, or decide what a subject is.
This is the invariant whose absence produced `_components` and `_label`: two modules needing the same
mask primitive, with no owner for it, each writing its own. It is also what stops two families
disagreeing about what `pipe_left` refers to — a disagreement that would be invisible in both records.

**The run owns family order and the withholding rule.** `spec.md` §7 states an eight-gate order in
which a failed gate withholds later colour judgments, and §7.1's surface pass appears in none of the
eight. That gap is harmless with one family and stops being harmless immediately: readability *is*
gate 3, named there by term id, so the second family lands inside an order the first one sits outside
of. Ordering is between families by construction, so no family can own it.

A third candidate collapses into the run owner rather than standing beside it. §5.

## 4. A family is a parameter, and the reason is who triggers it

The author's decision, and the reason is not the byte count:

> An end user does not order "check only this asset's readability". The model triggers some or all of
> them to test an asset.

That settles the shape. Two tools would have to carry, in descriptions paid for on every turn, the
conditions under which each applies — and those conditions are exactly what the model is choosing
anyway. One tool with a `families` parameter deletes the question. Since the model triggers *some or
all*, the parameter is a list and omitting it means every family; a scalar would make a model call the
tool N times to run everything.

The arithmetic agrees, which is confirmation rather than the argument. Against 3,810 bytes today:

| shape | surface | tokens | against the caps |
|---|---|---|---|
| a second `*_ledger` tool | 5,160 B | 1,214 | over the 1,200 hard cap |
| one tool, `families` parameter | ~4,040 B (estimated) | ~951 | under the 1,000 soft cap |

The second row is an estimate — a `families` enum at about 110 bytes and roughly 120 bytes of added
description — and it is the row that has to be measured when the tool is written, not assumed. The
first row is measured.

`conventions.md` §1a already holds the precedent for preferring a parameter on byte grounds: `vocab_get`
keeps three operations on one string parameter because splitting them measured 462 more bytes for
nothing the parameter cannot say. The same reasoning, and the same structural note applies — a model
cannot discover a family's existence from the type, so the enumeration has to be in the description.

## 5. What the run owner takes over

Five things are shared by construction. Each is shared because a second family needs the identical
thing, not a similar one.

1. **The subject primitive** — `{id, bbox, depth?, mask?}`. The only way to point at something inside an
   asset. Readability needs it at L2 for camera-scale reading and clutter, and for a silhouette inside
   a frame.
2. **Capture contract ingestion** — `composed_of` rows, the skipped-row report, box and depth and mask
   validation. A second implementation of this is a second definition of what a frame contains.
3. **The two-phase form/answers protocol**, including the `answers.image_sha256` stamp. The stamp exists
   because ids rebind when pixels change; that is true of every family's ids.
4. **The record builder** — `observation.v1` with its level assignment. Two builders means `asserted`
   means two things.
5. **The three axes** — `direction_compliance`, `asset_cohesion`, `intentional_contrast`. An axis
   re-derived per family is an axis with a different meaning per family, which is the failure this
   repository already fixed once on `asset_cohesion`.

And a sixth, which is why the rendering layer needs no owner of its own. The profile layer
(`sentences`, `for_reader`, and the helpers under them) presents a finished run to a human. Assembling
a family's execution steps on demand — so that `SKILL.md` carries asrai's epistemology and nothing
per-family, and the steps ride on a response the model already receives rather than on a surface billed
every turn — presents a run to a model. These are one job:

> **Every surface that presents a run to somebody belongs to the run owner, and none of them may move a
> verdict.**

That is `2026-09-17-profile-alignment.md`'s precedence rule generalised from readers to audiences, and
it keeps its verifier: for one asset and one set of answers, every profile and every presentation
produces a byte-identical verdict and record.

Two things deliberately do **not** move to the run owner. A family's measurements stay with the family,
because they are what the family is. And a family never reads another family's verdict: readability may
not explain a silhouette by citing the lighting family's finding. The gate order is the discipline —
gates run forward and a failure withholds what comes after; nothing later reinterprets what came before.

## 6. Where a family's data lives

**One policy file per family, in `src/asrai/data/stock/`.** No new realm.

The domains genuinely differ — lighting physics against perceptual reading — and the data realm is the
one the world contributes to, where a contributor should open one file that is theirs. `surfaces.v1.json`
is already titled for the lighting pass, which becomes honest rather than misleading. Claims do not
collide: `surfaces.count = 10` counts one file, and a sibling file is a separate claim with a separate
source, so there is no drift to resolve.

The file boundary is not what prevents duplicate invention. `_components` and `_label` are in separate
files and separate modules already. What prevents it is §3's first invariant, and the placement here is
decided on contribution ergonomics alone.

No new realm, and specifically not for the presentation layer. It has an invariant and a verifier, so it
qualifies as an owner, but its errors reach only what a human or a model reads and never a verdict or a
record — it has no outgoing arrow in the propagation graph. `cache` was already kept out of that graph
for the same shape of reason. The feature realm's invariant is "deterministic behaviour behind two
transports", and presentation is that. `profiles.v1.json` in data consumed by feature code is the
existing `surfaces.v1.json` arrangement, not a new one.

## 7. The node budget, and when it is spent

The feature realm's diagram has six nodes today. `conventions.md` §0 sets ten as the point at which the
proposed expansion pauses for a human scope review.

| | nodes |
|---|---|
| today: `config` `vocab` `measure` `records` `doctor` `light` | 6 |
| run owner + readability | 8 |
| a third family | 9 |
| a fourth family | 10 — §0 review |

The run owner buys exactly two more families. That is not a warning; it is a date. The question at ten
is not "is the drawing readable" but "is this one job", and §0 is explicit that deepening answers the
first and never the second. Recording it here means the next person meets a scheduled conversation
rather than a surprise.

## 8. What this does not decide

- **Which surfaces the readability family has**, what decides each, and what its thresholds are. Nothing
  here constrains that except §1's finding that its terms are `proxy_only`, which decides how findings
  are recorded and not what they are.
- **Whether readability needs subjects at L1.** `measure.v1` already computes, at a 64 px thumbnail
  scale, the silhouette mask area ratio, bbox, bbox fill ratio and component count, plus luminance
  percentiles, RMS contrast, edge density and an eight-colour palette. Much of the L1 half may be
  reading measurements that exist rather than taking new ones, which would put it in `measure.py` by the
  existing rule and not in a family module at all. Unmeasured.
- **The migration.** Whether `light.py` is split before the second family or as part of it, and whether
  `light_ledger` keeps its name once it takes a `families` parameter. A tool rename is a contract change
  under `conventions.md` §1 and needs its own row.
- **Whether the presentation layer becomes a module.** It is the run owner's job; whether it is the run
  owner's file is a legibility question to answer when it has two consumers.
- **The third family.** §7 says when that conversation happens, not how it goes.
- Nothing here validates the lighting thresholds, which remain unverified implementation policy
  (`2026-09-16-authority-and-release-gate.md`).

## 9. The ownership review of the slice that followed

Run with `domain-ownership-review` after the code was written and before it merged, against the two
rules §5 gives the run: *the input is read once*, and *subjects are derived once*. Three findings, all
closed in the same commit.

**A rule with no enforcer.** Both rules held only by the text of the code. No check would have gone red
if a family had called `measure.load` itself, and the mutation test confirmed it: adding one such call
to `light.py` left the suite green. The enforcer is now a source scan asserting that only `measure` and
`run` open an asset — a per-package test, so the second family inherits it without being named in it.

**A meaning changed under a mechanical move.** Extracting the run turned `_records(..., bool(capture))`
into `_records(..., read is not None)`. They differ when a caller passes `subjects` *and* `capture`,
which both transports accept: the observation record's `asset_kind` flips `screenshot` → `raster` and
its `evidence_layer` `L2` → `L1`. The new value was the correct one — `_subjects` never reads a capture
when subjects are given, so the old record claimed an evidence layer from a file nothing had opened —
but it arrived as an unannounced side effect of a rename, in a persisted record, with no test. The fix
is at the owner rather than at either expression: `_subjects` now refuses two sources of subjects, which
is what the MCP tool description had always published (`subjects: … or capture: … or neither`) and what
the code alone did not hold. The two expressions are then equal by construction.

**A second definition, in the commit that existed to end them.** `_depth` travelled into `run.py` with
the rest of the move and stayed there, dead, after the predicate was promoted to `measure.layer_index`
for the two owners that need it. §1's line — duplication waits for a primitive with no owner, not for a
second family — survives its own remedy being applied carelessly.

The review reached rung 2 for the run identity rule, which is what an `object` boundary needs: the
refusal of a sheet stamped with another run is observed after a real run, not from a call count.

What this says about the process: none of the three was visible from the diff of the slice, and all
three were visible from the rules the slice had written down one file earlier. The review is cheap only
when the invariants are already prose in the module that owns them.
