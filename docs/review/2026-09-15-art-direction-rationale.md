# Where the art claims in this design came from, and the three that came from nowhere

> 2026-09-15 · verified at `cdf7802` · Shelby Yoon

**For a reader a year from now** who asks why the key-light tolerance is twenty degrees, why these ten
surfaces and not twelve, and why the shipped vocabulary refuses to say what is good. Until today those
answers lived in four places, one of which was a status file that is rewritten on every change. This
collects them, and separates what has a basis from what only has a habit.

It settles nothing on its own. Where it finds a claim with no recorded basis it says so and leaves the
repair to a person; inventing a citation would be the exact failure the whole design exists to prevent.

## 1. The five ways a claim got in

| basis | what it means | where it is recorded |
|---|---|---|
| published work | a paper or a standard, adopted for one named mechanism, with the parts deliberately not adopted written down | §2 below |
| industry practice | how the trade and its tools already behave, followed rather than reinvented | §3 |
| measured here | a number this repository produced by running the code on images, with what produced it | §4 |
| a person decided | an invariant the author chose. Legitimate — invariant 1 admits a human as a source — but it has to say who and when | §5 |
| **nothing** | stated as fact, with no source anywhere | **§6** |

The last row is the reason this document exists.

## 2. Published work

Eight sources, verified 2026-09-14 against their arXiv or OpenReview pages. Each was adopted for one
mechanism; what was *not* taken matters as much, because it is where this design deliberately differs.

- **Cho et al., Davidsonian Scene Graph, ICLR 2024, arXiv:2310.18235.** Adopted: atomic questions
  generated from typed data, asked in a fixed order, and the dependency rule — a parent answered no
  counts its children as no, unasked, which is why a rejected emitter voids its pairs. Not adopted:
  the averaged accuracy score, because asrai keeps three axes and never sums them, and the VQA model
  answering its own questions.
- **Yang et al., Set-of-Mark Prompting, arXiv:2310.11441.** Adopted: identifiers drawn onto the image
  so an observer can say `e2` and `pipe_left` instead of describing a position. Not adopted: SEEM or
  SAM segmentation — subjects come from the capture contract, a sprite's alpha, or the observer's own
  boxes.
- **Johnson & Farid, *Exposing digital forgeries by detecting inconsistencies in lighting*, ACM MM&Sec
  2005.** Adopted: light direction estimated from luminance along the occluding contour, which is
  `contour_fit`. Not adopted: the 3-D spherical-harmonics extension (Kee & Farid 2010).
- **Sarkar et al., *Shadows Don't Lie and Lines Can't Bend*, CVPR 2024, arXiv:2311.17138.** Evidence
  that generated images fail object-shadow and perspective consistency, which is why `cast_shadow` is a
  surface at all. Their shadow classifier is not adopted; this is observation only.
- **Giroux et al., *Shedding Light*, SIGGRAPH Asia 2026, arXiv:2609.10787.** Lighting direction, colour
  and radiance measured against ground-truth probes: the same three quantities as `key`, `light_color`
  and the irradiance proxy. A probe object in an engine capture is a planned measurement, not a built
  one.
- **Maruani et al., *Illustrator's Depth*, arXiv:2511.17454.** The model behind `depth` being an ordinal
  layer index and never a distance.
- **Yang et al., Depth Anything V2, NeurIPS 2024, arXiv:2406.09414.** A planned optional adapter for
  virtual depth on raw images. Deliberately not a dependency.
- **Zhang, Rao & Agrawala, IC-Light, ICLR 2025 (OpenReview u1cQYxRI1H).** Relighting as a future
  recipe, never an observation.

These moved here from `CHECKPOINT.md`, where they had been sitting in a file whose own README calls it a
snapshot that is rewritten. A citation is not a status.

## 3. Industry practice

- **Sprite Lamp, SpriteIlluminator and Sprite DLight normal maps under Unity URP `Light2D`.** This is
  where the `engine_lit` mode comes from: painted directional shading double-lights a normal-mapped
  sprite, and the pass has to be able to say which of the two it is looking at.
- **The tool's own spelling wins.** `locales/README.md` rule 2: where a language's Illustrator, Blender
  or Unity has a word for something, the locale bundle uses that word rather than a better translation.
  A vocabulary that argues with the software on the artist's screen is a vocabulary they will not use.
- **`PBR`, `UV` and `LOD` staying untranslated** in non-Latin scripts, for the same reason.

## 4. Measured here

Every one of these was produced by running this code and is reproducible from the repository.

- **Estimator noise floor.** Under 3 degrees for bright side and under 8 for contour fit, on synthetic
  Lambertian and cel discs, alpha or rectangle masks, across eight directions (`tests/test_light.py`).
  This is what the agreement thresholds are supposed to sit above.
- **Colour-space invariance.** 8 emitters x 3 references x {shipped, gamma 2.2, gamma 1/2.2}, masks
  pinned: the rank share of each spill ring was identical to two decimals while the luminance
  difference swung ten to twenty times. Rank-based measurement is invariant to a monotone transfer by
  construction, and this is the check that it actually is.
- **Perturbation response.** A vignette at 0.55 bends a sprite's shaded mass by about 20 degrees; at
  0.15 it costs under 9. Bright side held under 1 degree across every perturbation and stack; contour
  fit under 4.
- **`SPILL_MIN_Y` against a real night reference.** All 8 emitters remained measurable at p50 luminance
  0.015, so the guard does not silence dark genres.
- **The emitter floor is a near-tie on real pixel art.** The absolute floor 0.30 binds where the
  relative one sits at 0.298, which is why `emitter_floor.basis` is reported rather than corrected.

## 5. What a person decided

These are choices, not findings, and invariant 1 allows a human to be the source. What was missing
until now is the second half of that rule: who, and when.

| decision | who and when |
|---|---|
| three axes, never summed into a score | the author, before implementation (`review/2026-09-13-art-direction-skill-scenario-review.md`) |
| zero taste in stock; preference lives in a team's records | same |
| direction may be observed, magnitude may not be invented | same; it is invariant 1 |
| `unknown` is a hold, not a verdict | the author, 2026-09-14, after a decoy scene passed by answering "I cannot tell" |
| the three readers a feature must serve — no art training, an artist, an art director | the author, 2026-09-14 |
| English canonical, other languages as aliases | the author, round 1 |
| the emitter constants: floor 0.30, fraction 0.6, max share 0.25, min area 4 | the author, with a reason beside each in `light.py` and no measurement behind any |
| the spill geometry: rings at 2 core radii against 4 to 8 | same |

The last two rows are legitimate under invariant 1 and still worth naming, because a reader cannot tell
a measured constant from a chosen one by looking at it.

## 6. The three with no basis at all

**A. Sixty degrees.** `DISAGREE_DEG = 60` is the threshold beyond which the measurement declares two
lights to be in disagreement rather than asking the observer. The comment above it grounds *twenty* and
says nothing about sixty. `spec.md` §7 and `SKILL.md` both restate it as a band. Nothing anywhere says
what sixty is, and it is the threshold that decides when a human stops being asked.

**B. "Hand-drawn scenes hold their key to roughly 10 degrees."** This sentence sits in the comment that
justifies `KEY_TOLERANCE_DEG`, between two numbers that were measured. It is a claim about how artists
actually work, it is load-bearing for twenty degrees, and nothing names what measured it or who
observed it. It is the same shape of defect as "never more than eight tools", which was removed on
2026-09-14 for exactly this reason.

**C. Why these ten surfaces.** `surfaces.v1.json` records `decided_by` for each — two by measurement,
four by evidence, four by observer — so coverage is readable from the data. Nothing records why the
list is these ten. Three of the four observer surfaces (`ambient`, `rim`, `albedo`) measure nothing at
all today, which makes the question sharper, not softer: they are there because someone thought an art
director asks about them.

### Not defects, but worth reading in the same breath

The shipped vocabulary already discloses its own limits, and is the model the rest of this should copy.
Its `known_limits` say that removing the learning layer "is not evidence that what remains is an
industry-standard set; it is the v1 corpus minus its practice exercises", and that descriptions and
guidance "are not verified against any external primary source." That is honest, and it is why the 22
categories are not in the list above: the corpus does not claim what it cannot show.

One thing it does claim uniformly, though. All 475 entries carry the identical provenance triple —
`term_basis: attested_in_in_scope_source` on every single one, with no source named for any individual
term. That field records a policy, not evidence, and a reader could easily mistake it for the second.

## 7. What would fix each

- **Sixty degrees**: either a measurement (at what separation do two observers stop calling it the same
  key?) or an honest demotion to a chosen constant with a name and a date beside it.
- **The ten-degree claim**: it can be measured, on the real references this repository already has.
  Until it is, it should say who asserted it.
- **The ten surfaces**: one paragraph in a review saying what an art director is asked about and why
  the list stops there. The artist brief already asks that question of a real artist; its answers are
  the natural source.
- **Per-term provenance**: when stock contributions open, the Getty Art & Architecture Thesaurus shape
  is the one to copy — term, language, **source of the term**, scope note, with authoritative sources
  cited per record rather than per corpus. That is the same rule as invariant 1, pointed at vocabulary
  instead of numbers, and it is a rule a technical artist can satisfy without writing code. See
  `2026-09-15-ci-gate-discovery.md` §2.
