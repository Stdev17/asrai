# Shape, and what the gates consume — 2026-09-20

> 2026-09-20 · verified at `1958079` · Claude Opus 5

For the package author, choosing the second family. It **supersedes**
[`2026-09-20-readability-before-colour.md`](2026-09-20-readability-before-colour.md), written earlier
the same day, on three of its nine sections: the family is `shape` and not `readability`, the node
budget correction in its §2 was itself wrong, and the questions its §8 left to a human were asked in
the wrong units. Its §1, §5 and §7 survive and are carried forward here.

Three decisions, all the author's:

1. **A family is a supplier to the eight gates, not a layer.** The run runs the gates; a family
   supplies what one consumes.
2. **`shape` is next**, because it supplies the most gates from the fewest categories and needs
   nothing the run does not already have.
3. **`reading` is not an owner**, so the realm is at seven nodes and the budget of
   [`2026-09-17-family-and-run.md`](2026-09-17-family-and-run.md) §7 stands as first forecast.

## 1. A family is not a layer

`records.LAYERS` is a property of the **asset** — L0 source structure, L1 rendered asset, L2 composed
frame — and `run._record` settles it with `"L2" if capture else "L1"`. The lighting family runs at both
and owns neither. So the earlier document's instinct to arrange families into layers was reading a
field that describes the input as if it described the code.

What families are ordered by is `spec.md` §7, and the ordering is consumption:

| gate | supplied by |
|---|---|
| 1 measure at three scales | **the run.** `measure` takes the numbers, `open_run` holds the ladder |
| 2 grayscale study | shape |
| 3 silhouette at 64 px | shape |
| 4 hierarchy and attention (L2 only) | composition |
| 5 group cohesion | composition |
| 6 intentional contrast | **nobody.** It is one of `records.AXES`, a verdict the run reduces, and its own parenthesis says context tags explain the difference — context belongs to the record |
| 7 density and noise | shape |
| 8 colour last | colour |

## 2. The count that orders the additions

Two numbers per family. **Gates supplied** is how much of the run's order it pays for. **Categories
drawn from** is how question-shaped it is: a family whose terms come from one category has a boundary
the vocabulary draws for it, and one that borrows from seven has a boundary somebody has to keep
drawing by hand. `light`'s figures are measured off `surfaces.v1.json`; the other three are counted
off the vocabulary and are estimates until a policy file exists.

| family | gates | categories | measurable terms available | needs |
|---|---|---|---|---|
| **shape** | 3 of 8 (2, 3, 7) | 4 | 21 in `shape`, 2 usable in `value` | nothing new |
| **colour** | 1 of 8 (8) | 1 | 12 in `color` | the gate that withholds it to have run |
| **composition** | 2 of 8 (4, 5) | 5 | 6 + 7 relational | L2: a capture, several subjects, and the terms `records.L2_ONLY` refuses at L1 |
| `light` (built) | **0 of 8** | **7** | 9 in `lighting` and 13 borrowed | — |

`light` claims twenty-five terms across seven categories — `lighting` 12, `material` 6, `value` 2,
`color` 2, `space` 1, `vfx` 1, `perception` 1 — and pays for none of the eight gates. That is not a
defect, it is the measurement of what `2026-09-18-the-run-answers-once.md` §5 already recorded in
words: lighting sits outside the gate order because it is the one family defined by **a question**
rather than by what it measures. It is also why the second family was hard to place from lighting's
shape: there was nothing in the built family to generalise from.

Shape inverts both numbers. Colour has the cleanest boundary of the three and still cannot go first,
because it is the gate everything else withholds. Composition has the widest spread and is the only one
that needs machinery the run does not have.

## 3. `reading` is not an owner

`src/asrai/README.md` claimed an invariant for it — *judgment outranks expression*. That sentence is
`2026-09-17-family-and-run.md` §5's rule about the **run**, and what holds it is `run.ledger`: it takes
`findings` out of the family's return and hands over those alone, so there is no verdict inside
`reading` to move. The module is what the invariant is **about**, not what enforces it.

The repository had already written the rule this falls under, one module earlier: `profile` is a module
and owns nothing because *it projects a cache*. `reading` projects a run's findings under a reader
profile. **A projection owns nothing.** The file stays — a renderer living inside a family would be a
renderer with a branch per family — and it leaves the owner graph, as `profile` and the transports
already had.

So the realm is at seven drawn owners and the forecast stands as written:

| | nodes |
|---|---|
| today: `config` `vocab` `measure` `records` `doctor` `light` `run` | 7 |
| + shape | 8 |
| + colour | 9 |
| + composition | **10 — §0 review** |

The earlier document's §2 claimed this fell due one family early. It does not. The error was counting a
projection as an owner, and the scope review lands on composition — the family that needs L2 anyway,
which is the right place for the conversation about whether this is still one job.

## 4. The shape family

Seven surfaces, in gate order, in the idiom of `surfaces.v1.json`. Every scope is `global`: the
per-element half is gates 4 and 5, and `records.L2_ONLY` already refuses those terms at L1. Shape is
therefore the family that proves `ctx["subjects"]` is a run's offer and not a family's obligation.

`terms[0]` is the term the measurement is entitled to assert, not a summary of the surface —
`tests/test_corpus.py` has required since `233bde1` that a `measurement` surface lead with a term the
vocabulary does not call `proxy_only`, `qualitative` or `relational`, and its comment names this family
as who it is waiting for. All three `measurement` surfaces below lead with a measurable term.

| id | gate | decided_by | terms[0] | mode | what decides it |
|---|---|---|---|---|---|
| `value_bands` | 2 | `measurement` | `value.three_value` | integer | how many separated luminance bands the asset resolves into at 64 px |
| `value_separation` | 2 | `evidence` | `value.value_contrast` | proxy | the p10–p90 luminance spread and `rms_contrast`; the observer reads them and decides |
| `silhouette` | 3 | `measurement` | `shape.silhouette` | mask | whether there is a mask to read at all — the alpha channel, or failing that the answer `value_separation` gave |
| `occupancy` | 3 | `measurement` | `composition.screen_occupancy` | number | `bbox_fill_ratio` and `mask_area_ratio`; `composition.negative_space` and `positive_space` after it |
| `survival` | 3 | `evidence` | `perception.silhouette_readability` | proxy | `silhouette.components`, `bbox_fill_ratio` and `mask_area_ratio`, native against 64 px; `perception.scale_readability` after it |
| `detail_economy` | 7 | `evidence` | `shape.tertiary_detail` | number | `edge_density` native against 64 px: detail that does not survive the reduction was not paying for itself. `shape.contour_economy` and `perception.visual_clutter` after it |
| `icon` | 3 | `observer` | `perception.icon_readability` | proxy | nothing. No measurement recognises a thing, and `unknown` is the honest default |

`shape.proportion` is measurable and is deliberately absent: its `required_context` is `numerator`,
`denominator` and `baseline_for_delta`, and no baseline exists until a precedent corpus does. It is the
first term to add once §6 has run.

**One withholding is real today**, and it needs no cross-family machinery: an asset with alpha has its
silhouette in the alpha channel and `silhouette` is measured whatever the values do; an asset without
alpha has no silhouette except the one the values separate, so a failed `value_separation` makes
`silhouette` `unknown` and never `no`. That is gate 2 gating gate 3 on a field `ctx` already carries,
and the fixtures split both ways — `sprite_rgba.png`, `antialiased_rgba.png` and `indexed_alpha.png`
carry alpha, `screenshot_rgb.png`, `flat.jpg` and `gray16.png` do not.

The scale ladder belongs to `open_run`, not to the family: gate 1 is *measure at three scales*, before
any gate a family owns, and `measure.stats(rgba, alpha_present)` is already public and already takes an
array. Numbers stay `measure`'s, the ladder becomes the run's, the family holds its thresholds and
nothing else. (This is the earlier document's §5, unchanged.)

## 5. What shape asserts, and what it only concludes

`perception` has twenty-three terms and **none is measurable** — seventeen `proxy_only`, six
`qualitative`. That is the whole reason this family is not called readability: a family named for that
category could never assert anything from it. Readability is not a family and not a layer. It is the
column every family writes its conclusion in.

| family | asserts from | concludes in `perception.*` |
|---|---|---|
| shape | `shape`, `value.three_value`, `composition.screen_occupancy` | `silhouette_readability`, `scale_readability`, `icon_readability`, `visual_clutter`, `figure_ground` |
| colour | `color` | `perceived_color` is colour's own; little else |
| composition | `composition`, `value.contrast_hierarchy` | `visual_hierarchy`, `attention`, `style_coherence`, `perceptual_grouping`, `visual_saliency` |
| light | `lighting`, `material` | `material_readability` |

`spec.md` §7's rule then places every row: a measurement of a proxy is recorded under the term that was
actually measured, or under the proxy at `estimated`. Shape can do the first, which is what the earlier
document got right and then filed under the wrong family name.

## 6. Thresholds come from references, not from a survey

The earlier document's §8 asked a human *how many bands is three* and what value of `rms_contrast` is
too little. Neither is answerable. The first presumes the artist sets the luminance threshold that
separates two bands, which is the tool's unit and not theirs; the second asks for a cutoff on the
standard deviation of luminance with no reference to be short of.

`spec.md` §7 already prescribes the answerable form — *pairwise, both orders, no scores* — and
`records.pairwise.v1` is already built for it. `surfaces.v1.json` states the policy in one line:
**team precedent replaces these numbers.** So the two questions become one request:

> At the size it ships at: assets you would send out as they are, and assets you would send back.

Arbitrary cutoffs go in first, the corpus fits them, and the claims get trimmed against it. The
posterise question is answerable the same way and needs no number at all — show the asset reduced to
three luminance levels and ask whether it still reads as the same image.

## 7. The axes reduction is a rule, not a question

The earlier document left `{unknown, pass}` to a human. It is not an art question and a survey cannot
reach it. `spec.md` §7 already has the constraint — *`unknown` never becomes a change* — which makes
`unknown` an absence rather than a verdict, and the rule follows:

> An axis is the worst verdict among the families that judged it. A family that could not judge
> contributes nothing, not `unknown`. When no family judged it, the axis is `unknown`.

Monotone, no human input, and `run._backed` still holds: the family that warned owns the observation
behind it.

## 8. Motion is a second kind of run, not an eleventh owner

`motion` has forty-three terms and eighteen measurable ones, and they are the juice vocabulary
outright: `anticipation`, `overshoot`, `settle`, `follow_through`, `drag`, `afterimage`,
`squash_stretch`, `contact`, `residual_motion`, `delayed_follower`, `temporal_overlap`, `timing`,
`spacing`. Thirteen of the eighteen are denominated in `s`, `ms` or `frame`.

Which is the obstacle. `open_run` reads **one file** and `run_sha256` is taken over its bytes, the
mirror flag and the subjects. A time axis is not a family's to add: it is a second kind of run, and
every rule the run owns — the input read once, subjects derived once, one identity a form is stamped
with — would have to be restated over a sequence first. It supplies none of the eight gates, which are
all still-image.

There is also a ruling only the author can make. `spec.md` §1 puts *animation judgment* among the
non-goals, and immediately says a rendered view of a mesh is in scope while the mesh's construction is
not. Juice is the rendered result over time, so the same sentence reads both ways. **That is a real
question for a human, unlike the two in §6**, and answering it is the precondition for the motion work
rather than a consequence of it.

## 9. What this does not decide

- **The thresholds**, until §6's corpus exists. They arrive as unverified implementation policy under
  the rule [`2026-09-16-authority-and-release-gate.md`](2026-09-16-authority-and-release-gate.md) set
  for the lighting cutoffs.
- **The style exemption.** The vocabulary has no term for a deliberately limited value range — no
  notan, no low-key, no limited palette — and the stock corpus is vendored, so inventing one is not
  asrai's. Until an upstream term exists the exemption has to key on the asset group's declared
  context, which is weaker than `lighting.fake_lighting` and is the author's call. A fog tile and a
  background flat fail gate 2 by design.
- **Whether `light.py` is split before shape or as part of it.** Shape needs the two-phase protocol and
  none of the lighting. Whether that is a shared helper, a copy or a split is unmeasured.
- **The tool surface.** `2026-09-17-family-and-run.md` §1 measured a second family built as a second
  tool at 1,214 tokens, over the 1,200 hard cap of `spec.md` §6. Shape arrives as a row in
  `run.ledger`, so the cap holds — but `light_ledger` returning a shape verdict says something false,
  and the rename is a contract change under `conventions.md` §1 needing its own row.
- **Two defects the second family exposes**, carried forward from the earlier document's §7 unchanged:
  `run._record` hardcodes `"scale": "native"` at [`../../src/asrai/run.py:205`](../../src/asrai/run.py),
  and `required_context` is enforced nowhere in `src/asrai/` although three of the terms in §4 name
  `resolution` in theirs.
