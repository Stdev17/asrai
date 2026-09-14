# asrai

First-pass art direction for game assets: deterministic **measurement**, qualified **observation**,
precedent retrieval, previewable **recipes**. It records the judgments a human art director or
technical artist makes; it never replaces them, and it never invents a magnitude.

Codex CLI and OpenCode read this file where Claude Code reads a skills directory. It is a pointer, not
a copy: the operating procedure is the bundled `SKILL.md`, and duplicating it here would give an agent
two versions to drift between.

## Register the server

```bash
codex mcp add asrai -- uvx asrai mcp      # Codex CLI
```

OpenCode, in `opencode.json`:

```json
{"mcp": {"asrai": {"type": "local", "command": ["uvx", "asrai", "mcp"], "enabled": true}}}
```

## Read the skill before touching an asset

```bash
uvx asrai skill-path      # prints the bundled SKILL.md; read that file, then work
```

It carries the gate order, the evidence layers, the qualified levels, the surface pass, the record
shapes, and the four things never to do. Everything below is only what you need before you open it.

## The four rules that hold whatever the task

1. **Direction may be observed; magnitude may not.** A number comes from a measurement, a precedent or
   a human. A model-proposed one is stored as `magnitude_basis: llm` and can never reach `apply`.
2. **`unknown` is a hold, not a verdict.** It never becomes a change, and no axis passes on evidence it
   was not given. Ask for a measurement or a human instead.
3. **Input bytes are immutable.** Every output is a new file under `out/`. Records are appended, never
   edited.
4. **Never paste the whole vocabulary into context.** `vocab_search`, then `vocab_get` for the one or
   two ids you will cite.

Not built yet: precedent retrieval, previews, `apply`, rasterize, render. Say so rather than improvising
them — `docs/spec.md` is the contract and marks what is `[built]`.

## Never create a status document

Do not add a plan, a progress note, a summary, a task list or a second checkpoint as a tracked file —
not at the root, not under `docs/`, and not in a worktree, whose files arrive in the pull request like
any other. Neither a reviewer nor a CI gate can tell an agent's working note from a documentation
contribution, and every review meets one. Scratch goes outside the repository or under a name
`.gitignore` already covers (`*.scratch.md`, `scratch/`); what landed goes in a new `CHECKPOINT.md`
entry; why it was decided goes in a dated file under `docs/review/`.

## Contributing to this repository

[`docs/runbook.md`](docs/runbook.md) is the procedures — where a thing gets written, how each file may
be written, the five changes people actually make. [`CONTRIBUTING.md`](CONTRIBUTING.md) is why, and
[`docs/README.md`](docs/README.md) says which document outranks which. One gate: `uv run pytest`.
