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
it. `light_ledger` turns the first question into a list of the second, from `surfaces.v1.json`
(bundled beside the vocabulary): ten surfaces an image's appearance decomposes into, in pass order,
each with one atomic question and the term id an answer is recorded under.

1. Subjects. A capture: `capture=capture.json` (its `composed_of` screen boxes). A sprite: one
   subject over the whole file. A raw image: propose up to sixteen boxes yourself, the things that
   carry shading, as `subjects=[{"id": "pipe_left", "bbox": [x, y, w, h]}]`. The ledger never
   segments a raw image on its own.
2. Call `light_ledger` and look at `overlay`: white boxes are subjects, magenta boxes are proposed
   emitters (`e1` is the brightest), the yellow arrow is where a subject's bright side points, the cyan
   arrow is the contour fit (alpha masks only), and the label at the arrow tip names the emitter the
   shading points at and the angle to it. `agreement` also carries the distance to each emitter, and
   pair questions are asked against the emitter the shading points at, the nearest one and `e1`.
3. Answer `questions` in order with yes, no or unknown and one line each. `emissive` comes first
   because bright paint is the usual false positive and every later pair question is about an emitter.
4. Levels. A surface with ledger fields (`emissive`, `key`, `diffuse`, `specular`, `light_color`,
   `rim`) is `asserted` when the field decides it: `angle_deg` near zero agrees, near a half turn
   disagrees, a small `hue_delta_deg` means the highlight carries the emitter's colour. The ledger's
   `highlight` is the subject's brightest region: on a pipe with a bright painted band it is the band,
   so a `specular` answer whose highlight colour is the subject's own paint stays `estimated`. A
   surface with no field (`cast_shadow`, `ambient`, `atmosphere`, `albedo`) is `estimated` at best.
5. Mirror check before any direction claim is recorded as `asserted`: call again with `mirror=true`
   and answer again. A claim that does not mirror with the image is `unknown`.
6. Record one observation item per answer: `term_id` and `region` from the question, a note that
   names the subject and emitter ids and carries no digits. If the asset group's context declares
   `lighting.fake_lighting` (a fixed stylistic light, common in pixel art), a disagreement is
   `intentional_contrast`, not `direction_compliance`.

The ledger cannot tell depth (a source in front of the subject and one behind it give the same
two-dimensional direction), whether a proposed emitter emits, or anything about cast shadows. Those
stay with the observer. A fix is a recipe (relighting is not built), never an observation.

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

## Do not

- Do not generate, inpaint or repaint. Do not give absolute aesthetic scores or sum axes.
- Do not invent magnitudes. Do not turn `unknown` into a change.
- Do not judge a screenshot as if it were one asset, or a lone asset for hierarchy.
- Do not modify input files; outputs are new files under `out/`.
- Do not paste the whole vocabulary or every record into context.
