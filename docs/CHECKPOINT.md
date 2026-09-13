# CHECKPOINT

```text
phase: 1 (core and transports) — done, fixtures committed
last_acceptance_passed: 29 tests on 3.14 and on the 3.11 floor (vocab search/get/locales, lint rules,
  measure determinism incl. 16-bit grey, record validation incl. layer rules, doctor lock/drift, MCP tools
  in-process and over stdio, malformed-input refusal at both trust boundaries, six measure fixtures
  byte-equal, corpus validators inside pytest); validate_stock 21,675 checks; review_locales no defects
in_progress: nothing
next_slice: phase 2 — recipes, tool adapters, alpha policy, recipe hashes, preview/apply/diff (spec.md 8)
working_tree: main carries this commit. Phase 2 starts in a separate git worktree, because this checkout
  is shared with another session. Branch from this commit, do not continue on main.
pending_human:
  - review docs/spec.md and the artist brief
  - decide observer.mode default and embedding egress (spec.md 10)
  - confirm Blender/Inkscape versions on team machines (none installed on the dev machine)
  - decide the vocab_get overload: three operations on one string parameter, capped by the eight-tool
    budget (docs/conventions.md 1a, structural notes)
  - AGENTS.md is untracked and currently holds unrelated web-research notes; spec.md 12 reserves that
    filename for the asrai skill section on Codex and OpenCode
known_limits:
  - measure refuses above 12 Mpx (~4 GB peak at ~320 B/px): a 4K capture fits, 8K does not
  - 16-bit colour PNGs are measured at 8-bit precision; 16-bit grey is rescaled correctly
next_command: uv run pytest
```
