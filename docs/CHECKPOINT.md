# CHECKPOINT

```text
phase: 1 (core and transports) — done, fixtures committed; 1b surface pass (surfaces.v1, light_ledger) — done
last_acceptance_passed: 51 tests on 3.14 (vocab search/get/locales, lint rules, light_ledger direction/emitters/key fit/form/answers/depth/modes/noise floor/mirror/capture/malformed/a light nothing answers to/a shadow on the wrong side/production perturbations/subject masks, surfaces map onto vocabulary and skill,
  measure determinism incl. 16-bit grey, record validation incl. layer rules, doctor lock/drift, MCP tools
  in-process and over stdio, malformed-input refusal at both trust boundaries, six measure fixtures
  byte-equal, corpus validators inside pytest); validate_stock 21,675 checks; review_locales no defects
in_progress: nothing
next_slice: phase 2 — recipes, tool adapters, alpha policy, recipe hashes, preview/apply/diff (spec.md 8)
working_tree: main carries phase 1 (tag v0.1.0), AGENTS.md and the surface pass. Phase 2 starts in a separate
  git worktree, because this checkout is shared with another session.
design_lens: spec.md 1 now carries the three readers a feature must serve (no art training, an artist,
  an art director) and surfaces.v1 carries decided_by per surface (measurement 2, evidence 4, observer 4),
  so coverage is read from the data rather than argued in prose
pending_human:
  - review docs/spec.md and the artist brief
  - decide observer.mode default and embedding egress (spec.md 10)
  - confirm Blender/Inkscape versions on team machines (none installed on the dev machine)
  - decide the vocab_get overload: three operations on one string parameter, capped by the eight-tool
    budget (docs/conventions.md 1a, structural notes)
  - AGENTS.md is committed and still holds only web-research notes; spec.md 12 reserves that filename
    for the asrai skill section on Codex and OpenCode
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
known_limits:
  - measure refuses above 12 Mpx (~4 GB peak at ~320 B/px): a 4K capture fits, 8K does not
  - 16-bit colour PNGs are measured at 8-bit precision; 16-bit grey is rescaled correctly
  - a heavy vignette (0.55) bends a sprite's shaded mass by about 20 deg, out of the band the
    measurement settles and into the one the observer is asked. Light ones (0.15) cost under 9 deg
  - a vignette also dims an emitter near the frame border below the proposal floor, which is global
    (0.6 x the 99th percentile): a neon sign at the edge of a graded screenshot is not proposed at all
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
next_command: uv run pytest
sources (surface pass, 7.1; verified 2026-09-14 against arXiv/OpenReview pages):
  - Cho et al., Davidsonian Scene Graph, ICLR 2024, arXiv:2310.18235. Adopted: atomic questions from
    typed data, a fixed order, and the dependency rule (a parent answered no counts its children as no,
    unasked: rejected emitters void their pairs). Not adopted: the averaged accuracy score (asrai keeps
    three axes and never sums) and the VQA-model answering (host mode answers; api mode is planned).
  - Yang et al., Set-of-Mark Prompting, 2023, arXiv:2310.11441. Adopted: ids drawn on the image so the
    observer refers to e2 and pipe_left. Not adopted: SEEM/SAM segmentation; subjects come from the
    capture contract, a sprite's alpha, or the observer's boxes.
  - Johnson & Farid, Exposing digital forgeries by detecting inconsistencies in lighting, ACM Multimedia
    and Security Workshop 2005. Adopted: light direction from luminance along the occluding contour
    (contour_fit). Not adopted: their 3-D spherical-harmonics extension (Kee & Farid 2010).
  - Sarkar et al., Shadows Don't Lie and Lines Can't Bend, CVPR 2024, arXiv:2311.17138. Evidence that
    generated images fail object-shadow and perspective consistency; motivates cast_shadow as a
    surface. Their shadow classifier is not adopted (observation-only today).
  - Giroux, Hilliard, Hold-Geoffroy, Vazquez-Corral, Lalonde, Shedding Light, SIGGRAPH Asia 2026,
    arXiv:2609.10787. Lighting direction, colour and radiance distribution measured from inpainted
    probes against ground-truth light probes: the same three axes as key/diffuse, light_color and the
    irradiance proxy. A probe object in an engine capture is a planned measurement.
  - Maruani et al., Illustrator's Depth, arXiv:2511.17454 (rev. 2026-03). Depth as a layer index for
    illustrations: the model behind `depth` being an ordinal layer, never a distance.
  - Yang et al., Depth Anything V2, NeurIPS 2024, arXiv:2406.09414 (25M to 1.3B params). A planned,
    optional adapter for virtual depth on raw images; not a dependency.
  - Zhang, Rao, Agrawala, IC-Light, ICLR 2025 (OpenReview u1cQYxRI1H). Relighting as a future recipe,
    never an observation.
  - Community practice: Sprite Lamp / SpriteIlluminator / Sprite DLight normal maps with Unity URP
    Light2D. The `engine_lit` mode: painted directional shading double-lights a normal-mapped sprite.
noise_floor: bright side under 3 deg and contour fit under 8 deg on synthetic Lambertian and cel discs,
  alpha or rectangle masks, eight directions (tests/test_light.py); thresholds 20/60 deg sit above it
```
