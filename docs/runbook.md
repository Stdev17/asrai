# Runbook — the operating procedures

The operating procedures and the judgment hierarchy. Contribution policy is in
[`../CONTRIBUTING.md`](../CONTRIBUTING.md); the implementation contract is [`spec.md`](spec.md).

If you are an agent asked to give someone a tour of this repository, this page and
[`README.md`](README.md) are the two to read: between them they answer where a thing goes, what may not
be created, and what has to be true before a change lands.

## 1. The gate

### Judgment hierarchy — before changing anything

Apply the following order within the scope of the decision:

1. **The responsible human's explicit decisions and instructions.** Preserve their source and scope.
2. **Human-maintained documents:** intent, invariants, acceptance criteria and operating policy.
   This runbook and `CONTRIBUTING.md` carry that policy; a recorded human decision governs its subject.
3. **Derived specifications:** AI-generated specs, schemas and agent instructions. A generated spec is
   an implementation artifact. It ranks above executable code because changes propagate through it to
   code, tests and callers; its filename or a `[decided]` label does not grant it human authority.
4. **Executable implementation and tests.** They must satisfy the governing documents. If code and
   the governing document disagree, the code is incorrectly implemented; do not rewrite the document
   merely to make the existing code pass.

Human adoption is a decision with a source, not an inference from prose style, a commit author, a file
extension or an agent having written the file. A human can adopt a generated proposal; until then it
cannot override human-maintained intent. When ownership or adoption is materially unclear, hold the
affected judgment and identify the human who can settle it.

For a conflict, read the exact governing source, identify the defect at the lower layer, and propagate
the correction through spec/schema/skill, code and tests. Verify those dependants together. If the
governing document is itself inconsistent, record the conflict and return it to its human owner.
Measurements and test results are evidence about behavior, not authority to change the objective.
`CHECKPOINT.md` records verified state; dated reviews record historical reasoning. Neither silently
overrides a current human decision. The rationale is in
[`review/2026-09-16-authority-and-release-gate.md`](review/2026-09-16-authority-and-release-gate.md).

### Run the checks

```bash
uv sync --locked
uv run --no-sync pytest                           # behavior, corpus and fixture byte-equality
uv run --no-sync python tools/check_links.py
uv run --no-sync python tools/check_translations.py
uv run --no-sync python tools/check_wheel.py       # fresh install, CLI/MCP and the install bundle
```

The link and translation scripts check repository facts outside `pytest`. The wheel check exercises
the installed distribution in a fresh environment, without an editable checkout. CI runs these same
commands; its workflow and required-check setup are described in [`.github/README.md`](../.github/README.md).

## 2. Where a thing gets written

| you have | it goes | and it is |
|---|---|---|
| a promise about what the tools do | [`spec.md`](spec.md) | the derived implementation contract, governed by the hierarchy above. `[decided]` items need a reason recorded before they change |
| a name, and the alternatives you rejected | [`conventions.md`](conventions.md) §1a | binding on new code |
| a number stated in prose | [`../tests/claims.json`](../tests/claims.json) | checked by the suite, in every file that states it |
| what is true now, what landed, what is limited | [`CHECKPOINT.md`](CHECKPOINT.md) | a new entry on top. Never edit an entry |
| why a hard-to-reverse decision was made | [`review/`](review/README.md) | a dated file, never edited afterwards |
| an operating policy or a procedure someone will repeat | this file | human-maintained policy and its steps |
| how to make a change that will be accepted | [`../CONTRIBUTING.md`](../CONTRIBUTING.md) | process |
| a translation of a document | [`i18n/`](i18n/README.md) | stamped with the source commit |
| anything an agent needs before touching an asset | the bundled `SKILL.md` | never duplicated into `AGENTS.md` |
| how an agent develops this repository | [development skill](../.agents/skills/asrai-development/SKILL.md) | applies this runbook and conventions; separate from the bundled asset workflow |
| owner invariants and boundary signatures | [`architecture.md`](architecture.md) | verify against code and data flow when a boundary changes; conventions §0 governs scope |

## 3. What never to create

**Do not add a plan, a progress note, a summary, a task list or a second checkpoint as a tracked file.**
Not at the repository root, not under `docs/`, not in a worktree — a worktree's files arrive in the pull
request like any other. A reviewer, and a CI gate, cannot tell an agent's working note from a
documentation contribution, and every review meets one.

Where the note goes instead:

- **scratch that nobody else needs** — outside the repository, or under a name `.gitignore` already
  covers: `*.scratch.md`, anything in `scratch/`, or an experiment record under `docs/experiments/`
  (evidence kept beside the code — a run's diffs, a measurement — never tracked)
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
for until you do. A new language lands with a named owner in `docs/i18n/README.md`, who answers for
its staleness; without one it is not accepted. Staleness itself never blocks a merge.

**Add an image.** Say where it came from and under what licence, in the README of the directory it lands
in. An image whose origin cannot be stated does not go in.

## 7. Landing a change

1. Locked sync, `pytest`, `check_links.py`, `check_translations.py` and `check_wheel.py` all clean.
2. Every number you added to prose is in `claims.json`.
3. Asset capabilities are described in the bundled `SKILL.md`; repository development procedures
   belong in the development skill and its governing documents.
4. A new public name has its rejected alternative written down in `conventions.md` §1a.
5. A new `CHECKPOINT.md` entry on top, stamped, restating the volatile lists.
6. Commits split by meaning, each one green on its own, and each message naming every owner its diff
   touches using [conventions.md §5](conventions.md#5-commits). The checker prints the format on failure.
   A file the message cannot account for goes in its own commit or stays out.
7. `git commit -s`. Every commit carries a `Signed-off-by` line — the Developer Certificate of Origin,
   adopted 2026-09-15. Commits before that day carry none and are not rewritten.

### Install and check commit policy

After cloning, with Python available as `python3`:

```bash
git config --local core.hooksPath tools/hooks
uv run --no-sync python tools/commit_check.py --selftest
```

Both tracked hook files must be executable. Inspect an existing `core.hooksPath` before replacing it;
preserve any unrelated hooks. A new clone needs this explicit local installation. The hooks resolve
the checker in the current worktree. If other worktrees have not adopted these files, enable Git's
`extensions.worktreeConfig` and set `core.hooksPath` with `--worktree` only in the adopted worktree.

Use ordinary `git commit -s` and `git commit --amend -s`. The message hook checks structure; the
reference-transaction hook checks the completed commit against its first parent before Git moves
the branch. Rejected transactions leave the branch unchanged; the index and message remain available
for correction. No empty-index heuristic or special amend command is needed. Both hooks and the
same history checks are exercised in disposable repositories by the package suite.

To inspect an existing commit or the exact change under review:

```bash
uv run --no-sync python tools/commit_check.py --rev HEAD
uv run --no-sync python tools/commit_check.py --range <base>..<head>
```

Use resolved base/head revisions for the review; unavailable revisions fail. The positional message
file mode checks only the staged diff; use `--rev HEAD --msg <file>` to preflight a message-only
amend. The local hooks do not activate a remote gate, and the existing DCO workflow checks DCO only.
Review checks authority, causal `Fixes`, numeric evidence outside automatic coverage, and copy
provenance as well as the executable range result. See the
[adoption rationale](review/2026-09-16-commit-policy.md).

## 8. Pull request states

- **open** — being read.
- **held** — the machine cannot settle it and no one has yet. It stays open with the reason named. A
  hold is not a rejection, the same way `unknown` is not a verdict.
- **closed** — it will not land in this form. The close says where the idea *can* live: a team's own
  records, a team surfaces file, a later phase.

## 9. Install the environment a release was checked with

`uvx asrai==<version>` selects the package version; it does not install this repository's `uv.lock`.
For a reproducible dependency set, distribute the successful CI job's `dist/repro/` bundle together:
the wheel, `requirements.txt`, `python-version.txt` and `environment.json`. Attach that exact bundle
to the corresponding release. Until a release has that attachment, use the artifact of its successful
CI run; a locally built bundle is only local verification.

With [uv installed](https://docs.astral.sh/uv/getting-started/installation/), unpack the bundle into a
stable directory and run there. On macOS/Linux:

```bash
uv venv --python "$(cat python-version.txt)" .venv
uv pip sync --python .venv/bin/python --require-hashes --only-binary :all: --strict requirements.txt
.venv/bin/asrai --version
```

On Windows PowerShell:

```powershell
uv venv --python (Get-Content python-version.txt) .venv
uv pip sync --python .venv/Scripts/python.exe --require-hashes --only-binary :all: --strict requirements.txt
.venv/Scripts/asrai.exe --version
```

Register the absolute path of that environment's `asrai` executable with `mcp` as its argument in the
host, so an unrelated `uvx` environment cannot be selected. Keep the host's working directory (or
`ASRAI_ROOT`) at the user's asset project; the install directory is not the team corpus.
Run that same executable's `doctor --lock` from the asset project to record its actual environment.
The doctor lock reports drift; automatic strict refusal remains unimplemented.

The requirements file is generated from `uv.lock` with runtime dependencies only, then extended with
the built wheel's hash. Never maintain it by hand or separately from its wheel. Hashes constrain the
downloaded artifacts; they do not attest a publisher's identity. Obtain the bundle through the trusted
project release or CI run. If a compatible wheel is unavailable, installation fails instead of silently
building native dependencies from source.

The bundle fixes the package, dependency versions and the selected Python patch version. OS/CPU-specific
wheels and system libraries can still differ. `environment.json` records the tested platform and JPEG
decoder, the source revision and whether it was dirty. Exact fixture values remain the gate on each
tested environment; do not claim arbitrary-machine byte identity. A decoder difference needs a
reproducible report and a human decision about the contract, not an invented tolerance or regenerated
expectations. A container pinned by image digest is an option if identical system libraries become a
requirement; it is not part of this initial install path.

To update, install the next verified bundle in a new directory, compare measurements, then change the
host registration. Retain the previous directory for rollback. The bundle contains no team records.
