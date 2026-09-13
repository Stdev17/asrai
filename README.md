# asrai

First-pass art direction for game assets, for teams without a GPU. asrai records the judgments a human
art director or technical artist makes, so they can be retrieved and re-applied: deterministic
**measurement**, qualified **observation**, **precedent** retrieval, previewable **recipes**. It never
replaces the judgment and never invents a magnitude.

It ships as one Python package with a CLI and a stdio MCP server, plus a bundled `SKILL.md`, and works
in Claude Code, Codex CLI, OpenCode and Hermes Agent. The full contract is in [docs/spec.md](docs/spec.md).

## Status (0.1)

Built and tested: stock vocabulary v2 (475 terms, 12 languages), `measure` (Pillow + numpy),
append-only records with layer rules, instruction lint, `doctor` with a version lock, CLI and MCP.
Not built yet: recipes and previews, precedent retrieval, ingest and promotion, the pairwise bootstrap,
Blender rendering. The skill says so; agents should not improvise those steps.

## Install and register

```bash
uvx asrai doctor           # environment report; add --lock to write asrai.lock.json
uvx asrai skill-path       # where the bundled SKILL.md is
```

| host | MCP server | skill |
|---|---|---|
| Claude Code | `claude mcp add asrai -- uvx asrai mcp` | `cp "$(uvx asrai skill-path)" .claude/skills/asrai/SKILL.md` |
| Codex CLI | `codex mcp add asrai -- uvx asrai mcp` | add a section to `AGENTS.md` |
| OpenCode | in `opencode.json`: `"mcp": {"asrai": {"type": "local", "command": ["uvx", "asrai", "mcp"], "enabled": true}}` | add a section to `AGENTS.md` |
| Hermes Agent | in `~/.hermes/config.yaml`: `mcp_servers: {asrai: {command: uvx, args: [asrai, mcp]}}` | `~/.hermes/skills/asrai/SKILL.md` |

## Use

```bash
asrai vocab search "silhouette" --limit 5          # any language: --lang ko "실루엣"
asrai vocab get shape.silhouette --lang ja --compact  # MCP: vocab_get(lookup=, full=false)
asrai measure sprites/orc_idle.png --target-width 96
asrai lint instruction.json
asrai record observation.json                       # appends to corpus/team/records.jsonl
asrai doctor --lock
```

MCP tools: `vocab_search`, `vocab_get`, `measure`, `record`, `lint`, `doctor`. Every verb prints or
returns one JSON document; nothing modifies an input file.

## Develop

```bash
uv sync
uv run pytest -q
uv run python tools/validate_stock.py   # also runs inside pytest; standalone for the full report
uv run python tools/review_locales.py   # flags translations a human still has to confirm
uv run python tools/make_fixtures.py    # rewrite tests/fixtures/expected/ after a deliberate change
```

`uv run pytest` is the single gate: it covers the code, the shipped vocabulary, and byte-equality of
`measure` against the committed fixtures. Conventions for changes are in [docs/conventions.md](docs/conventions.md).

Layout: `src/asrai/` core (`vocab`, `measure`, `records`, `doctor`, `config`, `cli`, `server`),
`src/asrai/data/stock/` the vocabulary and locales (contributions welcome: `locales/README.md`),
`src/asrai/data/skill/SKILL.md`, `tools/` validators, `docs/spec.md` the contract, `docs/CHECKPOINT.md`.

The stock vocabulary is derived from an origin corpus with the learning layer removed; every entry keeps
`origin.entry_sha256`. Translations are LLM-drafted counterparts flagged for human confirmation.

MIT license.
