# Readability before colour — 2026-09-20

> 2026-09-20 · verified at `a607d22` · Claude Opus 5

For the package author, before the second family exists. It answers the first two bullets of
[`2026-09-17-family-and-run.md`](2026-09-17-family-and-run.md) §8 — *which surfaces the readability
family has* and *whether it needs subjects at L1* — corrects the node budget that review's §7 forecast,
and settles which family comes next and why it is not shape.

The decision is the author's and is one sentence: **readability is the second family, it takes no
subjects, and the `value` terms of the grayscale gate belong to it rather than to a colour family.**
What follows is what the vocabulary and `measure.v1` already decide about that, and the four things it
leaves to a human.

## 1. There is no shape gate

`spec.md` §7 orders the gates: 1 measure at three scales → 2 grayscale study → 3 silhouette at 64 px →
4 hierarchy and attention (L2 only) → 5 group cohesion → 6 intentional contrast → 7 density and noise →
8 colour last. Shape is not one of them. The silhouette enters at gate 3 as a readability question, and
gates 2, 3 and 7 are the whole of what a first pass over a lone asset can decide.

The vocabulary draws the same line one level down, and it is sharper than the gate order:

| term | mode | who owns it |
|---|---|---|
| `shape.silhouette` | `measurable_with_context` (`shape_or_mask`, px) | a measurement |
| `shape.primary_form` | `measurable_with_context` (ratio) | a measurement |
| `perception.silhouette_readability` | `proxy_only` | a judgment |
| `perception.scale_readability` | `proxy_only` | a judgment |
| `shape.contour_economy` | `proxy_only` | a judgment |

**The silhouette is measurable; whether it reads is not.** So there is no shape family to build: there
is a shape measurement, three quarters of which `measure.v1` already computes, and a readability
judgment over it. Building shape first would be building `measure.py` under another name and then
taking `shape.contour_economy` back off it when readability arrived, because readability is where that
term's `comparison_condition` comes from.

The run's own unbuilt machinery points the same way. Axes reduction across families, gate order, gate
withholding and a run with no family are each an identity function or an unreachable branch while one
family exists; `CHECKPOINT.md` and `2026-09-17-family-and-run.md` §8 both name readability as what makes
them testable. Lighting cannot: it sits outside the eight gates
([`2026-09-18-the-run-answers-once.md`](2026-09-18-the-run-answers-once.md) §5).

## 2. The budget was spent one family early

`2026-09-17-family-and-run.md` §7 forecast the feature realm's node count. `reading.py` is not in that
forecast — it was decided three days later, by
[`2026-09-20-one-run-one-voice.md`](2026-09-20-one-run-one-voice.md) — and it is a drawn owner. The
table as it now stands, counted off the graph in [`../../src/asrai/README.md`](../../src/asrai/README.md):

| | nodes | §7 forecast |
|---|---|---|
| today: `config` `vocab` `measure` `records` `doctor` `light` `run` `reading` | 8 | 7 |
| + readability | 9 | 8 |
| + a third family | **10 — §0 review** | 9 |

The scheduled conversation §7 promised arrives **one family earlier than it said**: at the family after
readability, not at the fourth. `conventions.md` §0 is explicit that the question at ten is not whether
the drawing is readable but whether this is one job, so a colour family is the point at which that is
asked — which is the same boundary §5 of this document reaches from the other side.

This paragraph is the correction. `2026-09-17-family-and-run.md` §7 is not edited; a review never is.

## 3. What readability may assert: two terms out of eleven

`spec.md` §7: *a measurement never asserts a term the vocabulary calls `proxy_only`, `qualitative`,
`relational` or `structural`*, and the same rule says where such a measurement goes instead — under the
term that was actually measured, or under the proxy at `estimated`. Against the eleven terms this family
would touch:

- **assertable, measured:** `value.three_value` (`measurable_with_context`, integer, `count`, no
  perceptual review) and `shape.silhouette` (`measurable_with_context`, `shape_or_mask`, px, no
  perceptual review).
- **`estimated` at best:** `perception.readability`, `perception.silhouette_readability`,
  `perception.scale_readability`, `perception.icon_readability`, `shape.contour_economy`,
  `value.value`, `value.value_contrast`, `value.tone_affinity` — all `proxy_only`.
- **not this family's, and not this layer's:** `value.contrast_hierarchy` is `relational` and its
  `required_context` is `targets`, plural. Two targets is gate 4, hierarchy and attention, which
  `spec.md` §7 marks L2 only. It is not gate 2 material and readability does not claim it at L1.

Three terms are already claimed by the lighting family's `surfaces.v1.json` and readability may not
record them: `value.highlight` (surface `specular`), `value.shadow` (`cast_shadow`) and
`perception.material_readability` (`albedo`). That is the right split and not an accident of order — a
highlight is a lighting event on one subject, a three-value study is a property of the whole frame.
**The `value` category does not belong to one family; it splits by what the term is about.**

So the family's shape is the mirror image of lighting's. Lighting is mostly measured with an observer
margin; readability is mostly observed with a measured floor, because two of the eleven terms can carry
`asserted` and every sentence it says about reading is `estimated` by construction. §4 counts both.

## 4. Six surfaces, and the test that already picks their first term

`tests/test_corpus.py` has held this since `233bde1`: a surface whose `decided_by` is `measurement` must
have a `terms[0]` the vocabulary does not call `proxy_only`, `qualitative` or `relational`. Its comment
names who it is waiting for — *every term the readability family would record is proxy_only, so this is
the guard that meets it first*. It does meet it: a five-surface draft of this section put
`perception.silhouette_readability` first under a measured surface and was red before a line of it
existed.

So `terms[0]` is not a summary of the surface, it is **the term the measurement is entitled to assert**,
and §3's line falls out of it: where something is measured the measured term leads, and the judgment
over it is a separate surface that the observer decides. In gate order, in the idiom of
`surfaces.v1.json`. Every scope is `global`: see §5.

| id | gate | decided_by | terms[0] | what the ledger puts under it |
|---|---|---|---|---|
| `value_bands` | 2 | `measurement` | `value.three_value` | separated luminance bands at 64 px, from `luminance.p10/p50/p90` and `palette`. A count, which is the one thing about value the vocabulary lets a measurement assert |
| `value_separation` | 2 | `evidence` | `value.value_contrast` | `luminance.rms_contrast` and the p10–p90 spread at 64 px; the observer reads them and decides. `value.tone_affinity` second |
| `silhouette` | 3 | `measurement` | `shape.silhouette` | whether this asset has a silhouette the pass can measure at all: the alpha channel, or failing that the answer `value_separation` gave. See §6 |
| `silhouette_survival` | 3 | `evidence` | `perception.silhouette_readability` | `silhouette.components`, `bbox_fill_ratio` and `mask_area_ratio`, native against 64 px; `perception.scale_readability` second. `unknown` wherever `silhouette` is not `yes` |
| `contour_economy` | 3, 7 | `evidence` | `shape.contour_economy` | `edge_density` native against 64 px: detail that does not survive the reduction was not paying for itself, which is gate 7 read on the same number |
| `icon` | 3 | `observer` | `perception.icon_readability` | nothing. No measurement recognises a thing, and `unknown` is the honest default |

Two surfaces measure and four do not, which is the mirror image of lighting: of its ten surfaces six
carry something measured — two `measurement` and four `evidence` — and only four are the observer's
alone. Readability inverts that ratio, and §3 says why. Every proxy row it writes is `estimated` by
construction; the two measured rows are what make those legible in a corpus, under `spec.md` §7's own
rule that a measurement of a proxy is recorded under the term that was actually measured.

`perception.readability` is the roll-up on the verdict and not a surface: it is what the other five
conclude, and a surface that asked it directly would be asking the observer to do the pass's job in one
question — the failure mode `spec.md` §7.1 opens by naming for lighting.

## 5. No subjects, and the ladder belongs to the run

**Readability at L1 takes no subjects.** Everything in §4 is asset-scope. The per-element half — does
*this* element read against *that* one — is gates 4 and 5, both L2, and `records.L2_ONLY` already
refuses `perception.visual_hierarchy` and `perception.attention` at L1. So readability is the first
family to prove that `ctx["subjects"]` is a run's offer and not a family's obligation, which is a
structural test of the boundary `2026-09-17-family-and-run.md` §5 drew, and one that one family cannot
run.

§8 of that review asked whether the L1 half therefore belongs in `measure.py` and not in a family at
all. It does not, and the answer splits three ways:

- **The numbers are `measure`'s.** `measure.stats(rgba, alpha_present)` is public, takes an array, and
  already returns every input §4 names, at a 64 px thumbnail.
- **The ladder is the run's.** Gate 1 is *measure at three scales*, before any gate a family owns, and
  `open_run` is where the input is read once. The scale ladder belongs in `ctx` beside `subjects` and
  `masks`: readability reads it, lighting ignores it, colour later reads the same dict, and no family
  decodes the file twice or reaches for `measure._resize`, which is private. `light` already imports
  `measure._r` and `SILHOUETTE_ALPHA` across that line and [`../../src/asrai/README.md`](../../src/asrai/README.md)
  records it as a defect; a second family repeating it would make it a pattern.
- **The thresholds are the family's,** and they are all it holds. That is why `readability.py` is one
  node and a thin one.

## 6. Where the withholding is real today

`spec.md` §7 says a failed gate withholds later **colour** judgments. With no colour family there is
nothing to withhold, and building the cross-family machinery now would be building an unreachable
branch — the thing §1 just argued against.

One withholding is real today, and it falls out of a field `ctx` already carries:

> **Without alpha, gate 2 gates gate 3.** A file with alpha has its silhouette in the alpha channel and
> `silhouette_survival` is measured whatever the values do. A file without alpha has no silhouette
> except the one the values separate, so when `value_separation` fails there, the silhouette answer is
> `unknown` and never `no` — the same rule `surfaces.v1.json` states for a subject the measurement
> cannot place.

The fixtures already split both ways: `sprite_rgba.png`, `antialiased_rgba.png` and
`indexed_alpha.png` carry alpha; `screenshot_rgb.png`, `flat.jpg` and `gray16.png` do not. So the rule
is testable on the day it is written, which is the only reason to write it before colour exists.

## 7. What the second family exposes in the run

Measured against `a607d22`, none of it fixed here.

- **`run._record` hardcodes `"scale": "native"`** ([`../../src/asrai/run.py:205`](../../src/asrai/run.py)),
  and `scale` is a property of the record, not of an observation. Readability's findings are about the
  64 px thumbnail. It survives only because every region in §4 is `whole_image`, which is scale-free —
  `records` calls a region "[x, y, w, h] in pixels of the observed scale", so `whole_image` is the one
  region that does not lie. The first family with a per-region finding at a reduced scale does not
  survive it. What scale a finding is *about* goes in `context`, where the vocabulary already asks for
  it: `shape.silhouette` requires `resolution` and every proxy term requires `comparison_condition`.
- **`required_context` is enforced nowhere in `src/asrai/`.** Readability is the first family whose
  terms require fields no code supplies or checks. It owes a test — the policy file declares the context
  keys each surface supplies, and the test compares them against `terms[0]`'s `required_context` in the
  vocabulary — and not a runtime gate. That is the same shape as the verifier `surfaces.v1.json` gained
  at `233bde1`, for the same reason.
- **The axes reduction gets its first real case, and it is not obvious.** Readability leaves
  `direction_compliance` `unknown` at L1: an asset with no brief has no direction to comply with.
  Lighting may return `pass` on the same run. The run then has to reduce `{unknown, pass}` to one axis
  value, and `spec.md` §7's only rule here — *`unknown` never becomes a change* — constrains what the
  result may cause and not what it is. Whether a run where one family looked and the other could not is
  `pass` or `unknown` is a human decision, and it is the first question the reduction must answer.
- **The tool surface.** `2026-09-17-family-and-run.md` §1 measured a second family built as a second
  tool at 1,214 tokens, over the 1,200 hard cap of `spec.md` §6. Readability arrives as a row in
  `run.ledger`, so the cap holds — but a tool named `light_ledger` returning a readability verdict says
  something false. The rename is a contract change under `conventions.md` §1 and still needs its own
  row. §8 of that review left it open and this document does not close it.

## 8. What this does not decide

- **The thresholds.** How many bands is three, what `rms_contrast` is too little, how much
  `edge_density` may vanish between scales. None of these is in the vocabulary and none is measured
  here. They arrive as unverified implementation policy under the rule
  [`2026-09-16-authority-and-release-gate.md`](2026-09-16-authority-and-release-gate.md) already set for
  the lighting cutoffs, or they arrive from a team's precedent.
- **The style exemption.** Lighting's keys on a term, `lighting.fake_lighting`, that declares the style.
  The vocabulary has no term for a deliberately limited value range — no notan, no low-key, no limited
  palette — and the stock corpus is vendored, so inventing one is not asrai's to do. Until an upstream
  term exists the exemption has to key on the asset group's declared context, which is a weaker thing
  and the author's call, not this document's. A fog tile and a background flat fail gate 2 by design.
- **Whether `light.py` is split before readability or as part of it.** §1 of that review measured that
  roughly 196 of its then 1,028 lines carried no lighting word and another ~230 were the two-phase
  protocol written in lighting terms. It is 862 lines now, the presentation layer having left it. Readability needs the protocol and not the lighting. Whether that is a
  shared helper, a copy, or a split is a migration decision with its own cost, unmeasured here.
- **The colour family.** §2 says when that conversation happens — at node ten, with `conventions.md` §0
  in the room. Not how it goes.
