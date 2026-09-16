# Architecture — realms

The repository's level 0. A **realm** is a boundary that owns a class of invariant, and this page is
asrai's ledger of them: what each one owns, how far its errors travel, who may write it, and what
checks it. [Conventions §0](conventions.md#0-owner-boundaries) governs decomposition, the
[runbook](runbook.md#1-the-gate) governs authority, and the
[repository-operating skill](../.agents/skills/repository-operating/SKILL.md) defines what a realm is
and how this ledger is maintained.

Nothing here draws a realm's interior. Each realm's own document does, one level down, so no drawing on
this page grows as a realm does.

## Propagation

Arrows point the way an error travels: a defect in the tail reaches the head. `support` is the sink —
it carries other realms' evidence and nothing depends on it, which is why it owns no invariant of its
own. Labels name what actually crosses.

```mermaid
flowchart TB
    SPEC["spec<br/>docs/, AGENTS.md,<br/>CONTRIBUTING.md, SKILL.md"]
    DATA["data<br/>src/asrai/data/stock/"]
    FEATURE["feature<br/>src/asrai/"]
    SUPPORT["support<br/>tests/, tools/,<br/>.github/, docs/review/"]

    SPEC -->|"invariants 1–14<br/>owner boundaries<br/>naming and records"| FEATURE
    SPEC -->|"vocab and instruction<br/>schemas, quantification<br/>modes"| DATA
    SPEC -->|"landing checks<br/>write policies<br/>claims"| SUPPORT
    DATA -->|"term ids<br/>surfaces.v1 policy<br/>the stock path"| FEATURE
    DATA -->|"manifest digests<br/>locale coverage"| SUPPORT
    FEATURE -->|"measure.v1 values<br/>fixture bytes"| SUPPORT
```

## The ledger

| realm | extent | invariant it owns | who writes it | verified by | interior drawn in |
|---|---|---|---|---|---|
| **spec** | `docs/`, `AGENTS.md`, `CONTRIBUTING.md`, the bundled `SKILL.md` | what the repository promises and how it is governed | maintainer | review, [`claims.json`](../tests/claims.json), `check_links.py` | [`docs/README.md`](README.md) |
| **data** | [`src/asrai/data/stock/`](../src/asrai/data/stock/README.md) | the vocabulary means what it says in every language it ships | **the world** | `validate_stock.py`, `review_locales.py`, `manifest.sha256.json` | [`stock/README.md`](../src/asrai/data/stock/README.md) |
| **feature** | the rest of `src/asrai/` | deterministic behaviour behind two transports | maintainer | `pytest`, committed fixtures | [`src/asrai/README.md`](../src/asrai/README.md) |
| **support** | `tests/`, `tools/`, `.github/`, `docs/review/`, packaging | none of its own; it carries another realm's evidence | maintainer | the realm it serves | each directory's own README |

**Derivation and repair.** spec and feature are authored. data is **projected**: the stock vocabulary
comes from an origin corpus with the learning layer removed, and every entry keeps
`origin.entry_sha256`, so a correction is re-taken from that canon rather than edited here. support is
mixed, and [runbook §4](runbook.md#4-how-each-file-may-be-written) names each generated file —
`manifest.sha256.json` and `tests/fixtures/expected/` are regenerated, never hand-edited to quiet a
red test. When `corpus/packs/` lands (`spec.md` §5), it enters as a fifth realm whose writers this
repository cannot ask for a fix: its exit is **supersede**, since a team canonical already outranks a
pack by contract.

The bundled `SKILL.md` ships under `src/` and is spec: propagation decides a realm, never location.
`docs/review/` is support for the same reason — a frozen review is evidence about a decision, not the
decision's current statement, which lives in the realm the decision governs.

**data is the centre of gravity.** Every other realm is maintainable by one technical artist; the
vocabulary is not, because its correctness in twelve languages needs contributors this repository does
not employ. That is why the data realm is the one where duplication is permitted — the locale bundles
restate every head term by design — and the only one where a machine, not a reviewer, is what holds the
copies equal.

## Where the physical layout lives

[`README.md`](../README.md) draws the directory tree for someone traversing the checkout, and each
directory's README says what lives there. That map is navigation; this page is responsibility. A
directory can move without changing a realm, and two directories can share one.

The adaptation this ledger's owner rules came from is recorded in
[`review/2026-09-16-owner-boundaries.md`](review/2026-09-16-owner-boundaries.md).
