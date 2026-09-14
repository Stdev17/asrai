# Contributing to asrai

asrai records the judgments a human art director or technical artist makes, so they can be retrieved
and re-applied. It never replaces the judgment, and it never invents a magnitude. Almost every rule
below is that sentence, applied somewhere specific.

## Setup

```bash
uv sync
uv run pytest -q          # the single gate: code, shipped corpus, and fixture byte-equality
```

There is one gate and that is it. The corpus validators run inside pytest rather than beside it, so a
change to the shipped vocabulary fails the same command a change to a module does.

## The five rules that will actually bite you

The full list is [docs/spec.md](docs/spec.md) §2 (invariants 1–14). These are the ones a change trips
over in practice:

1. **A number comes from a measurement, a precedent, or a human — never from a model and never from
   what the code currently prints.** If you add a threshold, the comment beside it names what measured
   it. "It looked right on my test image" is not a basis; measuring that image and saying so is.
2. **Silence is not agreement.** A measurement that could not be taken returns `unknown`, and an axis
   never reads `pass` on evidence it does not have. This is the single most common defect in this
   codebase's history — it has been fixed twice, at two different levels.
3. **Input bytes are immutable.** Every output is a new file under `out/`. Nothing in `measure.py` or
   `light.py` writes to a path it was given.
4. **Nothing is deleted or edited in place in the record corpus.** Records are appended; `supersedes`
   points at what a record replaces.
5. **Zero taste in stock.** The shipped vocabulary says what a term means and how it may be quantified.
   It never says what is good. Preference lives in a team's own records.

## What moves together

A change is not finished when the code passes. These travel in one commit:

```mermaid
flowchart TD
    CODE[module] --> TEST[test] --> SKILL[SKILL.md] --> CONTRACT[spec or conventions]
    DATA[stock data] --> MANIFEST[manifest.sha256]
    CONTRACT --> CKPT[CHECKPOINT]
```

- **module → test.** Non-trivial logic leaves one runnable check behind. Name it as a sentence about
  behaviour, and put the reason in the docstring.
- **module → `SKILL.md`.** No spec loss: a capability the tools have and the skill does not describe is
  shipped dead, because the agent never calls it. See [the skill README](src/asrai/data/skill/README.md).
- **a tool description → the budget.** A description is re-sent to the model on every turn; `SKILL.md` is
  read once. Keep the description to what picks the tool and shapes the call, and put the rest in the
  skill: the test warns above 1,000 tokens and fails above 1,200.
- **behaviour → contract.** A promise belongs in `spec.md`; a naming decision and its rejected
  alternatives belong in `conventions.md` §1a. Write the rejected alternative down — it is the cheapest
  thing in this repository and it stops the same argument recurring.
- **stock data → `manifest.sha256.json`.** Refresh the digest in the same commit; a test now fails if
  you forget.
- **a number in prose → `tests/claims.json`.** Any count a document states — terms, locales, tools,
  fixtures, a threshold — is registered there with what computes it and the wording that carries it.
- **a number in English prose → every translation of that document.** `docs/i18n/` mirrors a
  document, and the suite requires the same numeral in the mirror. Prose may lag behind its source and
  `tools/check_translations.py` says by how much; a number may not.
- **anything landing → `CHECKPOINT.md`.** Keep `last_acceptance_passed` truthful.

## The three changes people actually make

**Adding a vocabulary term.** Edit `src/asrai/data/stock/vocab.v2.json`, add the head term to each
`locales/*.json`, refresh the manifest, then `uv run python tools/validate_stock.py` and
`tools/review_locales.py`. Set `quantification.mode` honestly: `proxy_only`, `qualitative`,
`relational` and `structural` can never take `set` or a delta, and `lint` will enforce that forever.

**Adding a surface to the lighting pass.** `surfaces.v1.json` first — id, `scope`, `decided_by`, one
atomic question, the ledger fields, and the vocabulary terms it records under. `decided_by` is the
honest part: `measurement` means a field settles it, `evidence` means the ledger measures *around* it
and a human answers, `observer` means nothing is measured and `unknown` is the default. The corpus test
checks that `ledger` is non-empty exactly for the non-observer tiers, and that the surface is named in
`SKILL.md`.

**Adding a measurement.** Deterministic and asset-wide goes in `measure.py`; anything needing a
subject, an emitter or an observer goes in `light.py`. If it changes what `measure` reports, the
fixture diff belongs in the same commit — see [tests/fixtures](tests/fixtures/README.md), and read that
file before regenerating anything.

## Before you open a pull request

- `uv run pytest -q` is green.
- `uv run python tools/check_links.py` and `uv run python tools/check_translations.py` are clean.
  Neither runs inside pytest: a link and a translation are repository facts, not package behaviour,
  and the gate stays one command about the code.
- Any new number names what measured it.
- Any new failure mode returns `unknown` rather than a default.
- The skill describes anything new an agent can now do.
- A rejected alternative for any new public name is written down.
- If you found a defect in a real asset, the regression test keeps the *real* magnitude. A perturbation
  at an invented strength proves nothing; the vignette that broke the shaded mass was 0.10, and it
  mattered precisely because that is invisible.

## What not to add

No plan files, progress notes, summaries, task lists or second checkpoints. They are indistinguishable
from a documentation contribution at review time, and a worktree does not hide them — a pull request
shows everything. Scratch goes outside the repository or under `*.scratch.md`; status goes in a
`CHECKPOINT.md` entry; reasoning goes in a dated `docs/review/` file. [`docs/runbook.md`](docs/runbook.md)
§3 is the full rule.

## Scope

Say no to: absolute aesthetic scores, summing the three axes, generating or repainting pixels, and any
correction that guesses at what a codec or an engine did. A lossy source is reported, not deringed; a
colour space is measured around, not declared. The answer to a degraded input is to ask for the
original.
