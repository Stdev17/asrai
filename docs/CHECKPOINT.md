# CHECKPOINT

```text
phase: 1 (core and transports) — done, fixtures committed; 1b surface pass (surfaces.v1, light_ledger) — done
last_acceptance_passed: 35 tests on 3.14 (vocab search/get/locales, lint rules, light_ledger direction/emitters/fit/mirror/capture/malformed, surfaces map onto vocabulary and skill,
  measure determinism incl. 16-bit grey, record validation incl. layer rules, doctor lock/drift, MCP tools
  in-process and over stdio, malformed-input refusal at both trust boundaries, six measure fixtures
  byte-equal, corpus validators inside pytest); validate_stock 21,675 checks; review_locales no defects
in_progress: nothing
next_slice: phase 2 — recipes, tool adapters, alpha policy, recipe hashes, preview/apply/diff (spec.md 8)
working_tree: main carries phase 1 (tag v0.1.0), AGENTS.md and the surface pass. Phase 2 starts in a separate
  git worktree, because this checkout is shared with another session.
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
known_limits:
  - measure refuses above 12 Mpx (~4 GB peak at ~320 B/px): a 4K capture fits, 8K does not
  - 16-bit colour PNGs are measured at 8-bit precision; 16-bit grey is rescaled correctly
next_command: uv run pytest
```
