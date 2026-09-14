# CHECKPOINT

```text
phase: 1 (core and transports) — done, fixtures committed; 1b surface pass (surfaces.v1, light_ledger) — done
last_acceptance_passed: 58 tests on 3.14 (vocab search/get/locales, lint rules, light_ledger direction/emitters/key fit/form/answers/depth/modes/noise floor/mirror/capture/malformed/a light nothing answers to/a shadow on the wrong side/production perturbations/subject masks, surfaces map onto vocabulary and skill,
  measure determinism incl. 16-bit grey, record validation incl. layer rules, doctor lock/drift, MCP tools
  in-process and over stdio and inside their token budget, malformed-input refusal at both trust boundaries, six measure fixtures
  byte-equal, corpus validators inside pytest); validate_stock 21,675 checks; review_locales no defects
in_progress: nothing
next_slice: phase 2 — recipes, tool adapters, alpha policy, recipe hashes, preview/apply/diff (spec.md 8)
working_tree: main carries phase 1 (tag v0.1.0), AGENTS.md and the surface pass. Phase 2 starts in a separate
  git worktree, because this checkout is shared with another session.
design_lens: spec.md 1 now carries the three readers a feature must serve (no art training, an artist,
  an art director) and surfaces.v1 carries decided_by per surface (measurement 2, evidence 4, observer 4),
  so coverage is read from the data rather than argued in prose
pending_human:
  - six CI-gate questions, listed at the end of review/2026-09-15-ci-gate-discovery.md: whether a stale
    translation blocks, DCO or nothing, generated changelog or hand-written, who the second approver is
    at bus factor 1, whether contributed images need a provenance field, whether a held pull request is
    a state this project wants
  - review docs/spec.md and the artist brief
  - decide observer.mode default and embedding egress (spec.md 10)
  - confirm Blender/Inkscape versions on team machines (none installed on the dev machine)
  - light_ledger proposes emitters from luminance alone: bright paint is proposed too, by design (the
    emissive question rejects it); the highlight of a subject with a bright painted band is that band
  - spill reads the neighbourhood, so a real lamp mounted on a dark wall beside a lit floor can read
    negative; it is one of two tests (the other is receivers) and both must be empty before a light is
    called one the frame does not answer to
  - cast_shadow measures where a subject's shaded mass sits against its lit side, which needs no emitter
    and judges a lone sprite; inside one box it cannot separate cast from form shadow, it is read only
    on a file with alpha (which is what says which pixels are the subject), and a subject too flat for
    either mass to carry a direction is unknown, never yes
  - a flattened preview of a transparent sprite (the checkerboard baked into the pixels) is not the
    asset: measure reports alpha_present false and light_ledger proposes the checkerboard as emitters.
    Ask for the PNG with its alpha
audit (2026-09-14, every README and doc read against the code and the schemas):
  - fixed, silent: a capture.json row without a usable screen_bbox was skipped without a word (four
    declared, one measured, no warning), and rows past the sixteen-subject cap were dropped the same
    way. Phase one now returns `capture` with declared, measured and every skipped row with its reason
  - fixed, silent: an emitter answered `unknown` was treated as a rejection, so on one decoy scene
    naming e1 a lamp read fail while "I cannot tell" read pass and dropped the row entirely. unknown is
    a hold: it keeps a row as `unclassified` and holds asset_cohesion at warn. paint still rejects,
    because that is a judgment. The sibling verdict `unknown` became `unreadable`
  - fixed, leaked at a boundary: subjects[].mask was reachable from neither the CLI (--subject took a
    bbox only) nor the MCP description, two commits after it shipped. The CLI form is now
    ID=X,Y,W,H[,depth][@mask.png] and the tool description names mask
  - fixed, leaked at a boundary: lint requires nine conditional context keys (baseline_ref, image_ref /
    grid_ref + resolution, viewBox, timebase.fps + clock, fov_axis + projection, shader_model, and
    metric / sequence on the change). None was named in spec.md, SKILL.md or the tool schema, so they
    were discoverable only by failing. SKILL.md now carries the table and a test derives the key list
    from vocab.py, so it cannot go stale
  - fixed, drifted: "twelve locale bundles" in three files against eleven; per-file test counts in
    tests/README summing to 36 against a suite of 51; spec.md 6 listing six tools against seven.
    tests/claims.json now registers 14 numbers with what computes each and the wording that carries it
  - fixed, unchecked: manifest.sha256.json had drifted on validation_report.json with nothing to catch
    it; a test now compares every digest
  - moved out of the contract: the embedding price table (spec.md 10) and the pre-implementation
    playbook (repository root) are dated reviews. AGENTS.md now holds the asrai section spec.md 12
    reserves instead of unrelated web-research notes
  - English is canonical everywhere except review/, whose never-edited rule outranks it. The two
    READMEs inside the wheel were Korean, including the one asking eleven language communities for
    translations; both are English now
mcp_surface (decided 2026-09-14): the eight-tool cap was never a host limit and had no measurement behind
  it, so the bound is now bytes. The tools/list reply as compact JSON is 3,620 bytes — about 850 tokens at
  4.25 bytes per token, o200k_base — under a hard cap of 1,200 tokens and warned above 1,000 by
  tests/test_asrai.py. It measured 4,108 bytes (968 tokens) before the descriptions were cut, light_ledger's
  alone 38.5% of it; what left the descriptions is in SKILL.md, which is read once. The vocab_get overload
  survives on the same budget (docs/conventions.md 1a, structural notes)
known_limits:
  - the byte-equal fixture gate is decoder-bound, and flat.jpg is the exposed one: perturbing its decode
    by +/-1 on 0.1% of subpixels moves 2 of its 78 committed numbers (1% moves 10), landing on
    percentiles, which jump a whole quantisation step. Arithmetic is not the risk -- the tightest of the
    304 rounded values sits 9.8e-07 from a rounding boundary against float noise near 1e-16 -- but PNG
    decoding is exact by definition and JPEG's is not, and pillow>=12,<13 lets the bundled decoder move.
    A dependency patch release can turn a green change red under a message blaming the author
  - measure refuses above 12 Mpx (~4 GB peak at ~320 B/px): a 4K capture fits, 8K does not
  - 16-bit colour PNGs are measured at 8-bit precision; 16-bit grey is rescaled correctly
  - a heavy vignette (0.55) bends a sprite's shaded mass by about 20 deg, out of the band the
    measurement settles and into the one the observer is asked. Light ones (0.15) cost under 9 deg
  - a vignette also dims an emitter near the frame border below the proposal floor, which is global
    (0.6 x the 99th percentile): a neon sign at the edge of a graded screenshot is not proposed at all
  - at most the eight brightest blobs are proposed and at most sixteen subjects measured; a frame with
    a dozen neon signs is read through its eight strongest
  - the absolute emitter floor (EMITTER_MIN_Y 0.30 linear) is the one constant in the pass that a
    transfer function moves. On the pixel-art night reference it is the binding one and the relative
    floor sits at 0.298, so the two nearly tie; a darker frame would be chosen by an absolute level.
    Reported as emitter_floor.basis rather than corrected
colour_space (answered 2026-09-14, no input field added):
  - every rank-based measurement is invariant to a monotone transfer by construction: bright side, shaded
    mass and key fit are percentile centroids, and the emitter relative floor is a percentile. Measured:
    8 emitters x 3 references x {shipped, gamma 2.2, gamma 1/2.2}, masks pinned, and the rank share of
    each spill ring was identical to two decimals while the luminance difference swung 10-20x
  - the difference form still held its sign on all 18 real rows; it flipped only when the file's tonal
    range was destroyed (sRGB read as linear, then JPEG), which SPILL_MIN_Y refuses. A mid-rank form was
    tried and rejected: it reads 1.00 on the bloomed synthetic where the difference form correctly reads
    lights_nothing, because both ring forms include subjects and not only ground
  - SPILL_MIN_Y verified against the night reference: all 8 emitters measurable (p50 Y 0.015, gains
    +0.013..+0.075), so the guard does not silence dark genres
perturbations_run (2026-09-14, synthetic disc scene, both alpha and bbox subjects):
  - injected: URP bloom, vignette (0.1..0.7), sRGB-as-linear both ways, JPEG q60, film grain, matte-line
    fringing, atlas extrude writing opaque padding, and the stacks a real hand-over combines
  - held: bright_side (under 1 deg across every perturbation and stack), contour_fit (under 4 deg, and
    r2 reports the silhouette that is not one form), bloom at every radius and gain (it widens the
    emitter mask symmetrically, so the spill sign survives), atlas padding (a phantom emitter, correctly
    proposed and rejectable; the silhouette box grows by the padding)
  - moved, and fixed: a vignette of a tenth fabricated a shaded mass on a bbox subject (alpha now
    required); a vignette over 0.4 and a crushed export made spill unmeasurable and the axis read pass
    (an unchecked light now holds it at warn); sRGB-as-linear plus JPEG flipped the spill sign positive
    around a decal (both rings must now clear the bottom 3% of the 8-bit range); the ordinal emitter ids
    rebound under a strong vignette, so a filled sheet answered about other blobs (the form is stamped)
repo_docs: every tracked directory carries a README (src/asrai, data, data/skill, data/stock,
  data/stock/examples, data/stock/locales, tests, tests/fixtures, tools, docs, docs/review), plus
  CONTRIBUTING.md and a repository map in the root README. Mermaid is used for the four structural
  diagrams (package dependencies, test gate, document authority, repository map) so they diff as text.
  docs/README.md carries the authority order: spec.md wins, conventions binds new code, CHECKPOINT is a
  snapshot, review/ is historical and never edited. A link checker over every relative markdown link
  runs by hand (see the CONTRIBUTING checklist); it found and fixed four docs/reviews -> docs/review
  typos left from before the folder was renamed
ci_gate (discovery 2026-09-15, nothing decided): review/2026-09-15-ci-gate-discovery.md. There is no
  .github/ at all. Measured that day: 21 commits by 1 author; CHECKPOINT.md in 12 of the last 12 commits
  and spec.md in 10, at 8.1 files per commit, so two concurrent pull requests collide with near-certainty
  on a status file that is rewritten rather than appended; the suite is 58 tests in 2.5 s, so CI minutes
  bound nothing; the declared floor 3.11 was run and passes. The precedents say the gate should check
  provenance and conformance (Getty AAT requires a source for a term, Google Fonts blocks on FAIL and
  lets WARN through) and should never check merit, and that projects lose artists on the reply rather
  than the standard (Godot proposal 779, the Krita artist-programmer thread). The missing piece that
  maps onto this codebase: `unknown` is a hold everywhere in the data model and a pull request has no
  equivalent -- merged or closed, nothing held
next_command: uv run pytest
art_basis: the surface pass's eight published sources and the estimator noise floor moved to
  review/2026-09-15-art-direction-rationale.md on 2026-09-15, with what each was adopted for and
  what was deliberately not taken. A citation is not a status
```
