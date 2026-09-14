# `src/asrai/data/` — what ships inside the wheel

Everything here is data, not code, and it is installed with the package so `uvx asrai` works with no
network and no corpus checkout.

| directory | what it is | consumed by |
|---|---|---|
| [`skill/`](skill/) | `SKILL.md`, the agent-facing instruction bundle | copied into a host by the user; `asrai skill-path` prints its location |
| [`stock/`](stock/) | vocabulary v2, its schemas, the surface pass definition, locales, illustrative instructions, the integrity manifest | `vocab.py`, `light.py`, `records.py` |

Two rules hold across both:

1. **Zero taste in stock.** Nothing here states a preference. The vocabulary defines what a term means
   and how it may be quantified; it never says what is good. Preference lives in a team's records.
2. **Data is versioned by its own `schema_version`**, never by the package version. `vocab.v2.json`,
   `surfaces.v1.json` and `instruction.v2.schema.json` each carry one, and a reader checks it.

`stock/manifest.sha256.json` records the digest of each stock file. Nothing in the code reads it at
runtime — it is bookkeeping for review, so that a change to a shipped corpus file is visible in the
diff as a digest change and not only as a wall of JSON. Refresh it in the same commit that changes the
file.
