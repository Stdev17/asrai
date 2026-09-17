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

**Within one layer, the later revision wins.** The order above ranks layers, not two statements of the
same rank, so a document that contradicts itself or a sibling has no resolution in it. Compare the
revisions that introduced the two statements and apply the later one. This settles ordinary drift
without an escalation. It does not settle a conflict where the later statement is outside its own
scope, where both arrived in one revision, or where the earlier one is the recorded human decision;
those still return to the human owner.

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

One more is advisory and deliberately outside that list, because it reports rather than decides:

```bash
uv run --no-sync python tools/check_claims_diff.py   # numbers added to prose that no claims row covers
```

The link and translation scripts check repository facts outside `pytest`. The wheel check exercises
the installed distribution in a fresh environment, without an editable checkout. CI runs these same
commands; its workflow and required-check setup are described in [`.github/README.md`](../.github/README.md).

### What the gate can check, and what it cannot

Every check above is deterministic: the same commit gives the same verdict on any machine. That is what
lets a check be *required* — one that sometimes blocks and sometimes does not is not a gate. Three
tiers, and a finding moves between them in one direction only, toward the first.

**Tier 1 — bound to a symbol. Blocking, and in place.** A number that lives in code and is restated
anywhere else is registered in [`../tests/claims.json`](../tests/claims.json). The suite evaluates the
live symbol, compares it to the row, and requires the row's exact wording in every file the row lists.
This is the only tier that is proof: it fails on the pull request that moves either side.

The rule this repository had covered a number that starts in prose. It also covers the other direction:
**a number baked into Python — a source constant, a test tolerance, a tool literal — that any document
or JSON canon also states is registered in the same change that writes the prose.** A test's own
tolerance is the easy one to miss, because nobody reads it as prose until a document quotes it. So is
anything under `src/asrai/data/stock/`, which sits in the **data** realm, whose writer the
[realm ledger](architecture.md) names as "the world".

**Tier 2 — found in a diff. Advisory, and built.** `claims.json` is a whitelist: nothing else looks
for a number no row claims, including the case where a row covers a value for some files and not for
the one it was just written into. [`../tools/check_claims_diff.py`](../tools/check_claims_diff.py) is
the net around it. It reads a diff's added lines, keeps the ones that are prose — markdown outside a
code fence, a Python comment or docstring, the stock files that carry prose — and reports a
numeral or a number-word no row covers for that file.

```bash
uv run --no-sync python tools/check_claims_diff.py                     # before committing
uv run --no-sync python tools/check_claims_diff.py origin/main...HEAD  # a pull request
```

It exits non-zero on a finding, which is what makes it worth running locally, and it is **not** in the
required set: the answer to a finding is to register the number or to say it is not a claim. It drops
the shapes that carry a numeral without claiming anything — an id in code voice, a date, a version, a
section or tier reference — and it is still the noisy tier, because a small number-word is ordinary
English. That is the trade a reporting check is allowed to make and a blocking one is not. In CI it
belongs in its own job, outside the names [`../.github/README.md`](../.github/README.md) lists as
required.

**Tier 3 — judged by a model. Advisory, and never required.** Whether a sentence still means what the
code does is semantic, and no pattern reaches it: a document stating a bound and a test admitting a
looser one are consistent as text and contradictory as a claim. A model reviewer reads that difference,
which is real value on the one pass where a claim is written. Two properties keep it out of the
required set, and neither is a matter of prompt quality.

- **It is not reproducible.** The same diff can return a different verdict on a rerun; model version,
  sampling and context all move it. A required check that goes red on an unchanged commit teaches the
  one habit a gate exists to prevent, which is re-running until green.
- **Its input is the contribution.** The DCO workflow's care — check out the trusted branch, fetch the
  pull request's objects without checking them out, never import, install or execute its files — exists
  because a pull request's contents are untrusted. A model reviewer must *read* those contents, so a
  pull request can address the reviewer directly. That is the same boundary in a softer form, and it is
  why the reviewer's output is a comment a human weighs rather than a check a merge waits on.

What narrows that second one is tier 2. `check_claims_diff.py --json` emits the flagged lines and
nothing else of the diff, so the text a model is shown is selected by a deterministic script rather
than by the contribution: a pull request cannot put a sentence in front of the reviewer by writing it
somewhere the scanner never looked. A reviewer adopted here runs on the pull request, is fed that
output and nothing else, and comments.

A model reviewer may therefore say what it suspects; a human registers what it found; the registration
is what the gate enforces on every later commit. Its value is the one pass, not standing between a
branch and `main`. If one is adopted here it enters as a non-required workflow with read-only
permission and no secret, like every other check, and this subsection is what it is held to.

### Which document rule each check covers

The `repository-operating` skill lists the rules about
operating documents that a machine could enforce, and deliberately keeps no count: how many instances
this repository has, and which of them are written, are facts about this repository. They are here.
The threshold for writing one is a **second real instance**; a check written for a single hypothetical
case is scaffolding.

| rule | checked by | instances here |
|---|---|---|
| every file in an enumerated directory appears in its index | `check_links.py` | one drift, in `docs/review/` |
| a write-policy glob agrees with the tool that applies it | `check_translations.py`, which scopes `i18n/<lang>/**` in code | two |
| a number stated in prose matches what computes it | tiers 1 and 2 above, which own this row | — |
| a naming decision cites a name resolving to more than one surface | not written | one: `ledger` in `conventions.md` §1a, fixed in place |
| a cross-boundary signature appears in two READMEs | not written | none; there is one level |
| a README names a node two hops away | not written | none |
| a no-authority realm cited as the reason for a rule | not written | not audited |
| a realm's stated command verifier does not run | not written | not audited; `support` declares no command of its own |
| a rule stated in two documents | not mechanisable | a review obligation |
| a document that is semantically stale | not mechanisable | what §5's stamp and a dated review exist for |

A row moving from **not written** to a script name is a change to this table in the same commit as the
script. A row whose count reaches two is the signal to write one, and the reason this table keeps counts
that look useless while they are one.

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
| something that landed and changes what a user or a contributor does | [`../CHANGELOG.md`](../CHANGELOG.md) | one hand-written line under `Unreleased`, newest first. A behaviour or policy change needs one; a status entry, a dated review and an internal refactor do not |
| a translation of a document | [`i18n/`](i18n/README.md) | stamped with the source commit |
| anything an agent needs before touching an asset | the bundled `SKILL.md` | never duplicated into `AGENTS.md` |
| how an agent operates the documents themselves | the `repository-operating` skill, named here and **not carried in this repository** | arrangement and ownership of documents, orthogonal to what they say; code policy stays in `conventions.md`. It is a convention this repository follows, held once per machine rather than copied per repository, because a copy per repository is how three of them drifted apart. A contributor without it is not blocked: what a contribution has to satisfy is in [`../CONTRIBUTING.md`](../CONTRIBUTING.md), this file and [`conventions.md`](conventions.md) |
| which realm a path belongs to, and what propagates between them | [`architecture.md`](architecture.md) | the realm ledger, level 0. Adding a realm needs a human scope decision |
| owner invariants and boundary signatures | the owning realm's own README — for the package core, [`../src/asrai/README.md`](../src/asrai/README.md) | verify against code and data flow when a boundary changes; conventions §0 governs scope |

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
| `review/<date>-*.md` | **never edited** after the commit that adds it. A later review supersedes an earlier one |
| `corpus/**/records.jsonl` | **append-only**, `supersedes` points at what a record replaces (`spec.md` invariant 6) |
| `spec.md`, `conventions.md` | edited, but a `[decided]` item needs a recorded reason and usually a test |
| `i18n/<lang>/**` | edited freely, except line 1, which is the stamp |
| `tests/fixtures/expected/` | **generated.** `tools/make_fixtures.py`, never by hand, never to quiet a red test |
| `src/asrai/data/stock/manifest.sha256.json` | **generated.** Refresh in the same commit as the data |
| a directory's own `README.md` | edited in the ordinary way. It is that directory's index or its policy, never an instance of the policy above |
| everything else | edited in the ordinary way |

A write policy targets a prefix its directory's own `README.md` cannot match — a date, a language
code. An unprefixed glob makes a maintained index formally unwritable, and a contributor then cannot
tell whether correcting it is permitted. `docs/review/README.md` and `docs/i18n/README.md` are
ordinary documents; [`check_translations.py`](../tools/check_translations.py) already scopes the
second one that way in code.

## 5. A rationale carries a stamp

Any document that explains *why* opens with one line:

```text
> YYYY-MM-DD · verified at `<short sha>` · <author>
```

The date is the day it was written. The sha is the commit its facts were checked against — not its own
commit, which does not exist yet when it is written and is recoverable from `git log` afterwards. For
reviews written before this rule, [`review/README.md`](review/README.md) carries the three values in its
index instead.

### Revision references

**Choose the kind of reference.** Navigation to the current rule keeps an ordinary relative link.
Evidence for a claim, copied text, a review or a decision pins the source actually read, using
`path@short` and a section when useful. A pin preserves that snapshot; it does not establish freshness
or give historical instructions authority over the current policy.

**Keep identity; shorten display.** Identity is the source repository, full commit OID and
repository-relative path at that commit. Name the repository for cross-repository citations. Retain
the full OID once in the existing source record or a commit-permalink target; without either, record
it once beside the document's sources. Repeated prose may use the compact display. Do not create a
second provenance index. A Markdown snapshot link targets the full-commit permalink, never `main` or
the current relative file; `path@short` by itself is a citation notation, not a filesystem path.

Use a **minimum of 7 hex characters** for display, generated by `git rev-parse --short=7` from the
verified commit. Keep any longer result Git needs for uniqueness; never slice the hash by hand.
Uniqueness is local and can change as objects arrive. An ambiguous prefix is recovered from the
retained full OID and displayed with a longer unique prefix. Missing history or a missing historical
path requires retrieval from the recorded repository/archive; otherwise mark the reference unresolved
and hold the dependent claim. Never substitute `HEAD`, guess a match or silently repin. Keep cited
history available to readers in retained repository history or an archive. A hash alone does not retain
its object.

**Resolve before relying on it.** In the source repository, set `ref_rev` to the cited prefix,
`ref_full` to the retained full OID, and `ref_path` to the path at that revision:

```bash
git rev-parse --verify --end-of-options "${ref_rev}^{commit}"
git rev-parse --short=7 --verify --end-of-options "${ref_full}^{commit}"
git show "${ref_full}:${ref_path}"
git diff "$ref_full" HEAD -- "$ref_path"
git diff --cached HEAD -- "$ref_path"
git diff -- "$ref_path"
```

Compare the first result with the retained `ref_full` before using the cited bytes. A prefix is not
an integrity or authorization check; security-sensitive verification uses the full expected OID from
a trusted source and the existing approval rules. Existing full hashes in machine records, manifests,
translation stamps and approval evidence stay full. Cited uncommitted bytes are explicitly `dirty` or
`uncommitted`, with an exact content digest and retrievable snapshot when needed; `HEAD` cannot pin them.

**Revalidate the dependent claim.** Before a pinned claim governs current work, inspect the cited
section and compare it with the current governing source, including staged and working-tree changes.
The diffs above are a starting point; a rename needs both historical and current paths. When editing a
source, search for its dependent citations and update or flag affected current claims in the same
change. Repin only after reviewing the changed content, never just to clear a stale marker. Frozen
reviews and append-only records keep their pins; a new entry supersedes them. Apply this to new or
substantively updated claims, without mechanically rewriting historical references.

This is a contributor procedure, not an automatic freshness gate. Git owns abbreviation and object
lookup ([`rev-parse`](https://git-scm.com/docs/git-rev-parse)); review owns whether a changed source
invalidates a claim. Compact display reduces repeated identifier text, but raw Markdown still contains
full link targets. Token savings and attention/quality effects need measurement on the actual context
and tokenizer; no improvement magnitude is asserted here.

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
2. Every number you added to prose is in `claims.json` — and so is every number you baked into
   Python that a document or a JSON canon also states (§1, tier 1).
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
