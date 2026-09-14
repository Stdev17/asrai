# `src/asrai/data/skill/` — the bundled skill

One file: `SKILL.md`. It is what an agent reads before it touches an asset, and it is copied into the
host rather than imported — `asrai skill-path` prints where it lives.

```bash
cp "$(uvx asrai skill-path)" .claude/skills/asrai/SKILL.md   # Claude Code
```

Codex CLI and OpenCode read `AGENTS.md` instead; Hermes Agent reads `~/.hermes/skills/asrai/SKILL.md`.
The install table is in the [root README](../../../../README.md).

## The rule: no spec loss

**Anything the MCP tools can do must be described here.** A capability that exists in `server.py` and
not in `SKILL.md` is invisible: the agent never calls it, and the feature is shipped dead. The corpus
test `test_surfaces_map_onto_the_vocabulary_and_the_skill` enforces the surface half of this
mechanically — every surface id in `surfaces.v1.json` must appear in `SKILL.md` — but the rest is a
review obligation.

So a change to a tool's behaviour is not finished until this file says so. In practice that means
three files move together: the module, `SKILL.md`, and whichever contract in [`docs/`](../../../../docs/)
owns the promise.

## What it is not

Not a prompt, and not documentation for a person. It is the agent's operating procedure: gate order,
qualified levels, what may be asserted and what must stay `unknown`, and the four things it must never
do. Prose that does not change what the agent does belongs in `docs/`.
