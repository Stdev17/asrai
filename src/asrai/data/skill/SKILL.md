---
name: asrai
description: First-pass art direction for game assets (2D raster, screenshots, SVG, 3D through rendered views). Use when reviewing generated or hand-made assets for readability, cohesion, hierarchy and colour; when a comment like "too dull" must become a measured, previewable change; or when an AD/TA judgment should be logged as a reusable precedent.
version: 0.1.0
---

# asrai — first-pass art direction

asrai records and reuses the judgments a human art director or technical artist makes. It never
replaces them. Four steps, always in this order: **measure** (deterministic numbers), **observe**
(qualified, number-free), **retrieve precedents**, **preview a recipe**. Direction may come from
looking; magnitude may only come from a measurement, a precedent or a human.

## Setup

```bash
uvx asrai doctor            # tool/package/corpus versions; --lock writes asrai.lock.json
                            # over MCP the same switch is doctor(write_lock=true)
uvx asrai mcp               # stdio MCP server (register it in your host; see README)
```

MCP tools: `vocab_search`, `vocab_get`, `measure`, `light_ledger`, `record`, `lint`, `doctor`. The
CLI has the same verbs (`asrai vocab search|get|category|categories|langs|translations`,
`asrai measure`, `asrai light-ledger`, `asrai record`, `asrai lint`, `asrai doctor`). Not yet available: precedent retrieval, previews,
apply, rasterize, render. Say so instead of improvising them.

## Vocabulary

Never paste the whole vocabulary into context. `vocab_search` (any language, compact rows) then
`vocab_get` for the one or two ids you will cite. Every observation and instruction cites term ids
from this vocabulary; the English bundle is the spec, locales only rename head terms.
`quantification.mode` tells you whether a number is even meaningful for a term:
`proxy_only | qualitative | relational | structural` terms never take `set` or delta operations.

## Evidence layers

| layer | what is looked at | may decide |
|---|---|---|
| L0 | source structure: SVG XML, mesh, prefab, palette entries | structural facts only (measurements) |
| L1 | one asset as rendered: sprite as-is, SVG rasterized, mesh rendered under a fixed profile | silhouette, value, colour, edge, per-asset readability |
| L2 | a composed frame: gameplay capture with `composed_of` | hierarchy, attention, cohesion across assets, clutter |

A screenshot is L2; a lone asset is L1. `perception.visual_hierarchy`, `perception.attention` and
`perception.style_coherence` are decided between elements of a frame: on a lone asset they are
`unknown` by construction. Precedents never cross layers.

## Judgment protocol

Gate order; if an earlier gate fails, later colour judgments are withheld:

1. `measure` at native, target and 64 px.
2. Grayscale study: does the value hierarchy read without hue?
3. Silhouette at 64 px: `shape.contour_economy`, `perception.silhouette_readability`.
4. Hierarchy and attention (L2 only).
5. Group cohesion: palette, value range, edge treatment against siblings.
6. Intentional contrast: does a faction / scene / state tag explain the difference? Then it is not a violation.
7. Density and noise: `perception.visual_clutter`, `shape.tertiary_detail`.
8. Colour last: `color.saturation`, `color.vibrance`, `color.hue`, `color.color_temperature`.

Qualified levels: `asserted` (backed by a measurement or agreed at all three scales),
`estimated` (model observation without measurement, or two scales agree), `unknown` (scales
disagree, no evidence region, or a pairwise verdict flipped when the order was swapped). `unknown`
never becomes a change; it becomes a measurement request or a question to a human.

Three axes, never summed: `direction_compliance`, `asset_cohesion`, `intentional_contrast`.
Each is `pass | warn | fail | unknown`.

Pairwise, not scores. Ask A vs B and B vs A; if the verdict flips, record `unknown`.

Bias guards: "too red" without a hue histogram is `estimated`; "too dark/bright" without a
luminance distribution is `estimated`; the size of a saturation or vibrance change is never yours
to choose.

## Surface pass (lighting)

"Is the lighting consistent?" is a question a vision model answers unreliably. "Does the bright side
of `pipe_left` face `e2`?" it answers reliably, given the picture with `pipe_left` and `e2` drawn on
it. `light_ledger` turns the first into the fewest of the second, from `surfaces.v1.json` (bundled
beside the vocabulary): ten surfaces an image's appearance decomposes into — `emissive`, `key`,
`diffuse`, `specular`, `light_color`, `cast_shadow`, `ambient`, `rim`, `atmosphere`, `albedo` — each
with one atomic question, the term id an answer is recorded under, and `decided_by`, which says who
owns it: `measurement` settles `diffuse` and `cast_shadow` outside the contested band, `evidence`
measures around `emissive`, `key`, `specular` and `light_color` and leaves the answer to you, and
`observer` means `ambient`, `rim`, `atmosphere` and `albedo` are yours alone, where `unknown` is the
honest default. Two calls, one form, no prose.

1. Subjects. A sprite: pass nothing, its own silhouette becomes the subject `asset`. A capture:
   `capture=capture.json` (its `composed_of` screen boxes; the reply's `capture` block says how many
   rows it declared, how many were measurable, and why any was skipped — read it before trusting an axis). A raw image: propose up to sixteen boxes yourself, the things that
   carry shading, as `subjects=[{"id": "pipe_left", "bbox": [x, y, w, h], "depth": 0}]`. Any subject may
   also carry `mask`, the path of an image whose alpha marks its pixels (canvas-sized or box-sized): a
   layer export. Without one, a box on a frame with no alpha measures whatever else is in it, which costs
   the shaded mass and the contour fit. Never derive a mask by segmenting the image; ask for the layer. `depth` is
   an optional layer index (nearest first, as an illustrator stacks layers), never a distance; it only
   widens the distance to a light on another layer. The ledger never segments a raw image itself.
2. Phase one: call `light_ledger` and look at `overlay`. `source` says whether the file is lossy, and
   `emitter_floor` which of the two floors bound: `relative` is a percentile and survives any colour
   space, `absolute` is a fixed level and is what decides in a night scene. Neither is asked of you, and
   a lossy source is reported, never corrected — ask for the original instead. White boxes are subjects, magenta boxes are
   proposed emitters (`e1` is the brightest; bright paint is proposed too, on purpose), the yellow
   arrow is where a subject's bright side points, the violet arrow where its shaded mass sits (it
   belongs opposite the yellow one), the cyan arrow is the contour fit (alpha masks
   only), the label at the tip names the emitter the subject should answer to and the angle to it,
   and the corner text is `key_fit`: the single light that best explains the frame, with the median
   residual in degrees and the share of subjects within tolerance. A `directional` best hypothesis
   with a low residual and no emitter near it means an off-screen or stylistic key.
3. Fill `form`. Its null fields are all you decide: `style.mode` (`physical`, `fake_lighting`,
   `engine_lit`), a kind for every proposed emitter (`paint` is a judgment and rejects it, voiding every
   pair with it; `unknown` is a hold, so the emitter is not confirmed but stays visible and holds
   `asset_cohesion` at `warn`, and a kind you leave null is read as `unknown`), optional `emitter_depth`, an answer for each listed pair (only the diffuse band the
   measurement could not decide), for each subject-scope surface the lists of subjects for which it
   is false or undecidable, and `global.key` and `global.atmosphere`. Every subject left out of both
   lists answers yes and is recorded as nothing, except `cast_shadow`, which the measurement owns: a
   subject left out falls through to it, and a subject you list overrides it. List one when you can see
   what pixels cannot, such as a missing contact shadow on the ground. `specular` and `light_color` are two of those lists,
   judged against the light the verdict names for each subject: the brightest region of a box always
   lies inside its bright side, so no measurement separates the two without a material mask.
   `questions` restates each null field as a sentence, and carries what the measurement already knows
   about it: an emitter's question says whether surfaces near it are brighter than surfaces farther
   out. Measured facts are not asked again.
4. Phase two: call `light_ledger` again with `answers=<the filled form>`. Handing the form back
   untouched is a valid call and the shortest path there is: it returns everything the measurement
   decides on its own (`diffuse` where the angle is outside the band, `cast_shadow`) and `unknown` for
   the rest, with no vocabulary asked of you. Fill a field only where you can improve on that. `cast_shadow` comes back
   with `shadow_opposition_deg` and `shadow_basis`: the angle by which a subject's shaded mass fails to
   sit opposite its lit side, on the same twenty and sixty degree bands. It needs no emitter, so it is
   the one surface that judges a lone sprite, and `unknown` there means too flat to place, never fine.
   It is read only on a file with alpha, which is what says which pixels are the subject: on a screenshot
   the bottom decile of a box is the ground, and a vignette or a sky gradient would make that ground a
   confident direction. A form carries `image_sha256`; phase two refuses one filled for another image,
   since emitter ids are ordinal and rebind when the pixels change.
   `verdict` gives per subject the expected key (lamp, sky and screen outrank neon and glow, then strength over distance), the
   `verdict_emitter` it was judged against (the emitter it points at counts when at least a quarter as
   strong), the residual in degrees, `agrees | disagrees | unknown` with its basis (`measurement` or
   `observer`), and the axis outcome. A pair the verdict needed but the form did not list is
   `unknown`: answer it and call again. Light colour is always yours: the hue numbers are hints, since
   a painted band inside a box looks like a cast to any measurement; `engine_lit` reports `baked | flat` instead,
   because painted shading on an engine-lit sprite double-lights. `verdict.emitters` answers the other
   direction for each confirmed light: `lights` when something points at it or its surroundings are
   brighter for it, `lights_nothing` when neither is true, `unreadable` when it has no readable
   neighbourhood and no subject near it — a sprite on transparency, a source at the border, or a frame
   whose darks are crushed into the bottom code values, where the codec moves a ring further than a light
   does — and `unclassified` for a blob you held. Either one holds `asset_cohesion` at `warn`: an axis
   does not pass on evidence it never had, and the honest answer must not be the one that clears a frame. A light the frame does not answer to is a decal, in any
   genre, and it is what `axes.asset_cohesion` fails on, together with a shaded mass that contradicts
   its own lit side; `axes` summarises that with
   `direction_compliance` and `intentional_contrast` for the frame. Under `fake_lighting` both land
   on `intentional_contrast`, because the style declared them.
5. Mirror check before recording a direction as `asserted`: phase one again with `mirror=true`; a
   bright side that does not mirror with the image is noise, and its subject is `unknown`.
6. Record: fill `record.observer.model` with your model id and pass `record` to `record`. Measured
   items are `asserted`, observer items `estimated`; notes name ids and carry no magnitude.

The ledger's `highlight` is the subject's brightest region: on a pipe with a bright painted band it
is the band, not a specular. The ledger cannot tell whether a proposed emitter emits — only what its
neighbourhood does, which is evidence and not the answer. Inside one box it cannot separate a cast
shadow from the form shadow, and it never sees a contact shadow that is absent from the ground; ambient,
atmosphere and albedo it does not measure at all. Those stay with the observer. A fix is a recipe (relighting is
not built), never an observation.

## Records

Everything is appended to `corpus/team/records.jsonl`; nothing is edited or deleted. Observation:

```json
{"kind": "observation", "asset_kind": "raster", "evidence_layer": "L1", "scale": "thumbnail",
 "asset_sha256": "<sha256 of the file, from measure>",
 "observer": {"mode": "host", "model": "<your model id>", "prompt_rev": "v1", "pinned": false},
 "context": {"asset_group": "enemies", "scene": "forest", "state": "idle", "generator": "sdxl"},
 "observations": [
   {"term_id": "perception.silhouette_readability", "level": "estimated", "region": "whole_image",
    "note": "body and weapon merge into one blob at this size"}]}
```

Notes carry no digits. `region` is `whole_image` or `[x, y, w, h]` at the observed scale. SVG and
mesh observations must name the `render_profile_id` they were rendered with.

Pairwise verdict (a human's taste choice or a model comparison):

```json
{"kind": "pairwise", "evidence_layer": "L1", "term_id": "color.saturation",
 "a": "<sha256 or record id>", "b": "<sha256 or record id>", "verdict": "prefer_a",
 "by": "human", "reason": "keeps the value structure"}
```

Model verdicts must set `order_checked: true`. An instruction (kind `instruction`, schema
`instruction.v2`) is linted before it is stored: `magnitude_basis` is one of
`none | example | precedent | measurement | human | llm`, and `llm` never reaches an applied state.

`lint` also refuses an instruction whose `context` does not pin what its own numbers mean. The rule
fires from the operation, the unit or the term, so it is invisible until it fails:

| when a change has | `context` must carry |
|---|---|
| any delta operation (`add_delta`, `multiply`, `relative_delta`, `percentage_point_delta`) | `baseline_ref` — the fixed thing the delta is measured from |
| `quantity.unit` of `px`, `px2` or `texel` | `image_ref` (or `grid_ref`) **and** `resolution` |
| `quantity.unit` of `svg_user_unit` | `viewBox` |
| `quantity.unit` of `frame` | `timebase.fps` (a positive number) **and** `timebase.clock` |
| `term_id: camera.fov` with `set` | `fov_axis ∈ vertical \| horizontal \| diagonal` **and** `projection: perspective` |
| `material.roughness`, `material.smoothness` or `material.metallic` with a direct operation | `shader_model` |

Two more live on the change itself: `define_metric` needs `metric`, and `set_sequence` needs a
non-empty `sequence` with no repeats. And on `execution`: `authorized` needs both `adapter` and
`binding_resolved`, and `status: applied` needs `run_ref`. A unit not in the registry, or one the
term's quantification profile does not admit, is refused whatever the context says.


## Do not

- Do not generate, inpaint or repaint. Do not give absolute aesthetic scores or sum axes.
- Do not invent magnitudes. Do not turn `unknown` into a change.
- Do not judge a screenshot as if it were one asset, or a lone asset for hierarchy.
- Do not modify input files; outputs are new files under `out/`.
- Do not paste the whole vocabulary or every record into context.
