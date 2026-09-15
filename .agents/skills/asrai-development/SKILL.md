---
name: asrai-development
description: Use when changing or reviewing asrai code, contracts, owner boundaries, or contributor tooling in this repository.
---

# Develop asrai

Read [runbook](../../../docs/runbook.md) for authority and landing checks,
[conventions](../../../docs/conventions.md) for code policy, and
[architecture](../../../docs/architecture.md) for the current owner graph.
This develops the repository; asset work uses the separate
[bundled skill](../../../src/asrai/data/skill/SKILL.md).

## Before editing

- Trace the requested behavior from CLI/MCP through its owner and every caller. Name the invariant,
  allowed write set and executable acceptance evidence. Check the current checkpoint and exact source.
- Apply the runbook's hierarchy. Conflicting code is defective; generated instructions cannot overrule
  human-maintained policy. Preserve unknowns and return contradictory requirements to their human owner.
- For a boundary change, draw the proposed owner graph before implementation. Use actual cross-owner
  signatures; expose data contracts, shared constants and private imports. Count independent invariants,
  including deterministic policy, rather than files, tool names or commit-owner path buckets.

## Keep the job small

At **10 or more responsibility owners**, review whether the single product skill has acquired another
job, even if its graph fits. Follow conventions §0 for the separate diagram-fit condition. A new box,
subgraph, facade or larger imported cap cannot erase an independent responsibility. Present the
invariants and scope decision to the human before adding that responsibility; do not split the product
automatically. Helpers and data-only records do not become owners merely to tidy the diagram.

## Make the change

- Put rules in the responsible core owner; keep CLI/MCP as transports. Prefer an existing function or
  a direct call. A new public surface must justify its dependency in the graph.
- Review names from the caller's name, type and description alone. Preserve working names; make
  changed meaning explicit in the contract and keep old records readable. Keep units, coordinate
  frames and magnitude provenance visible. A named threshold needs its derivation.
- Stop at a write-set wall and report the required file and reason. Do not bridge it with copied
  constants, hidden state or a broadened return. A deviation requires sourced authority.
- Run the smallest proof that would fail if the change were wrong, then the runbook's landing checks.
  Update the graph with boundary changes. Append a checkpoint and use the existing commit hook schema,
  including copy provenance; a passing hook does not establish source identity.
