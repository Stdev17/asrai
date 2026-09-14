# Runbook — the operating procedures

Steps, not reasons. The reasons are in [`../CONTRIBUTING.md`](../CONTRIBUTING.md) and the contract is
[`spec.md`](spec.md); when this file disagrees with either of them, they win and this file is wrong.

If you are an agent asked to give someone a tour of this repository, this page and
[`README.md`](README.md) are the two to read: between them they answer where a thing goes, what may not
be created, and what has to be true before a change lands.

## 1. The gate

```bash
uv run pytest                          # the one gate: code, shipped corpus, fixture byte-equality
uv run python tools/check_links.py          # before a pull request
uv run python tools/check_translations.py   # before a pull request
```

The two `check_*` scripts are not inside `pytest` and are not expected to be: they check facts about
this repository, not behaviour of the package a user installs.

## 2. Where a thing gets written

| you have | it goes | and it is |
|---|---|---|
| a promise about what the tools do | [`spec.md`](spec.md) | the contract. `[decided]` items need a reason recorded before they change |
| a name, and the alternatives you rejected | [`conventions.md`](conventions.md) §1a | binding on new code |
| a number stated in prose | [`../tests/claims.json`](../tests/claims.json) | checked by the suite, in every file that states it |
| what is true now, what landed, what is limited | [`CHECKPOINT.md`](CHECKPOINT.md) | a new entry on top. Never edit an entry |
| why a hard-to-reverse decision was made | [`review/`](review/README.md) | a dated file, never edited afterwards |
| a procedure someone will repeat | this file | steps only |
| how to make a change that will be accepted | [`../CONTRIBUTING.md`](../CONTRIBUTING.md) | process |
| a translation of a document | [`i18n/`](i18n/README.md) | stamped with the source commit |
| anything an agent needs before touching an asset | the bundled `SKILL.md` | never duplicated into `AGENTS.md` |

## 3. What never to create

**Do not add a plan, a progress note, a summary, a task list or a second checkpoint as a tracked file.**
Not at the repository root, not under `docs/`, not in a worktree — a worktree's files arrive in the pull
request like any other. A reviewer, and a CI gate, cannot tell an agent's working note from a
documentation contribution, and every review meets one.

Where the note goes instead:

- **scratch that nobody else needs** — outside the repository, or under a name `.gitignore` already
  covers: `*.scratch.md`, or anything in `scratch/`
- **what landed, and what is true now** — a new `CHECKPOINT.md` entry
- **why a decision was made** — a dated file in `review/`

## 4. How each file may be written

| file or directory | write policy |
|---|---|
| `CHECKPOINT.md` | **append-only.** Add an entry on top; never edit or remove one below it |
| `review/*.md` | **never edited** after the commit that adds it. A later review supersedes an earlier one |
| `corpus/**/records.jsonl` | **append-only**, `supersedes` points at what a record replaces (`spec.md` invariant 6) |
| `spec.md`, `conventions.md` | edited, but a `[decided]` item needs a recorded reason and usually a test |
| `i18n/**` | edited freely, except line 1, which is the stamp |
| `tests/fixtures/expected/` | **generated.** `tools/make_fixtures.py`, never by hand, never to quiet a red test |
| `src/asrai/data/stock/manifest.sha256.json` | **generated.** Refresh in the same commit as the data |
| everything else | edited in the ordinary way |

## 5. A rationale carries a stamp

Any document that explains *why* opens with one line:

```text
> YYYY-MM-DD · verified at `<short sha>` · <author>
```

The date is the day it was written. The sha is the commit its facts were checked against — not its own
commit, which does not exist yet when it is written and is recoverable from `git log` afterwards. For
reviews written before this rule, [`review/README.md`](review/README.md) carries the three values in its
index instead.

## 6. The five changes people actually make

**Add a vocabulary term.** Edit `vocab.v2.json`, add the head term to every `locales/*.json`, refresh the
manifest, then `tools/validate_stock.py` and `tools/review_locales.py`. Set `quantification.mode`
honestly — `proxy_only`, `qualitative`, `relational` and `structural` can never take `set` or a delta.
A term that says what is *good* does not belong in stock; it belongs in your team's records.

**Add a surface.** `surfaces.v1.json` first — id, `scope`, `decided_by`, one atomic question, the ledger
fields, the vocabulary terms it records under — then the code, then `SKILL.md`.

**Add a measurement.** Deterministic and asset-wide goes in `measure.py`; anything needing a subject, an
emitter or an observer goes in `light.py`. If `measure`'s output changes, the regenerated fixture diff
goes in the same commit.

**Add or update a translation.** Copy the source, put the stamp on line 1 with the source's current
commit (`git log -1 --format=%H -- <path>`), write numbers as numerals, then
`tools/check_translations.py`. Never translate `spec.md`, `conventions.md`, `SKILL.md` or `review/`.
If the same commit also changes the source, the stamp cannot name it — that commit does not exist yet.
Stamp the source's previous commit, land both, and re-stamp in a follow-up, which the checker will ask
for until you do.

**Add an image.** Say where it came from and under what licence, in the README of the directory it lands
in. An image whose origin cannot be stated does not go in.

## 7. Landing a change

1. `uv run pytest`, `check_links.py`, `check_translations.py` all clean.
2. Every number you added to prose is in `claims.json`.
3. Anything an agent can now do is described in `SKILL.md`.
4. A new public name has its rejected alternative written down in `conventions.md` §1a.
5. A new `CHECKPOINT.md` entry on top, stamped, restating the volatile lists.
6. Commits split by meaning, each one green on its own.

## 8. Pull request states

- **open** — being read.
- **held** — the machine cannot settle it and no one has yet. It stays open with the reason named. A
  hold is not a rejection, the same way `unknown` is not a verdict.
- **closed** — it will not land in this form. The close says where the idea *can* live: a team's own
  records, a team surfaces file, a later phase.
