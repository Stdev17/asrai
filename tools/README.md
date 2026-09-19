# `tools/` — repository scripts

None of these ships in the wheel; each is run with `uv run python tools/<name>.py`. The table is the count.

| script | what it does | when to run it |
|---|---|---|
| `validate_stock.py` | validates vocabulary v2 and the illustrative instructions — roughly 21,700 checks | runs inside `pytest`; standalone when you want the full report rather than pass/fail |
| `review_locales.py` | mechanically reviews the eleven locale bundles and flags what a human still has to confirm | after touching any `locales/*.json` |
| `make_fixtures.py` | creates the six measure fixtures once, and regenerates their expected JSON on demand | only for a deliberate change to what `measure` reports — see [tests/fixtures/](../tests/fixtures/README.md) |
| `check_links.py` | resolves every relative markdown link and names the ones that go nowhere, then names any file an enumerating README has stopped listing | before a pull request, and after renaming or adding anything |
| `check_translations.py` | says how far each document under [`docs/i18n/`](../docs/i18n/README.md) has drifted from the English it was made from | before a pull request, and after editing a translated document |
| `check_claims_diff.py` | reads a diff's added prose and reports a number no `claims.json` row covers for that file; `--json` is what bounds a model reviewer's input | before committing, and on a pull request as a check that is not required — [runbook §1](../docs/runbook.md#1-the-gate) |
| `check_dco.py` | requires a valid signoff trailer on new commits, using `DCO_BASE_SHA` and `DCO_HEAD_SHA`; pre-adoption history is exempt | pull requests; tested with real temporary git histories inside pytest |
| `commit_check.py` | checks commit structure, asrai owners, changed numeric literals and conditional trailers; missing Git evidence fails | installed hooks, `--rev`, `--range`, or `--selftest`; see [runbook §7](../docs/runbook.md#7-landing-a-change) |
| `check_wheel.py` | builds a wheel, exports hashed runtime requirements, installs them into a temporary environment, checks installed CLI/MCP/data and immutable input bytes, and writes `dist/repro/` | before landing or releasing; choose a new `--out` directory for repeat runs |

`hooks/` holds the two Git hooks themselves — `commit-msg` and `reference-transaction` — which is why
they carry no `.py` and are not in the table above. They are shell entry points that call
`commit_check.py`, installed by pointing Git at this directory:

```bash
git config core.hooksPath tools/hooks
```

`reference-transaction` is what makes the check survive an amend, a rebase and a worktree, since those
move a ref without writing a commit message; [runbook §7](../docs/runbook.md#7-landing-a-change) is the
procedure and `test_commit_check.py` exercises both against real repositories.

`make_fixtures.py` writes fixtures; `check_wheel.py` creates temporary environments and a generated
install bundle, refusing an existing output directory. `commit_check.py --selftest` creates disposable
Git repositories; its normal checks and the other scripts are read-only.

`validate_stock.py` and `review_locales.py` are also called from the test suite, so the gate stays a
single command. Keeping them as scripts as well is deliberate: the standalone run prints the whole
report, which is what you want when you are changing the corpus rather than checking that it still
passes. Link and translation checks run separately for repository facts. The wheel check is its own
executable integration proof, including an actual stdio MCP call from outside the editable checkout;
its bundle is derived from `uv.lock`, never maintained separately. See the
[runbook](../docs/runbook.md#9-install-the-environment-a-release-was-checked-with) for installation.
