# `tools/` — repository scripts

None of these ships in the wheel; each is run with `uv run python tools/<name>.py`. The table is the count.

| script | what it does | when to run it |
|---|---|---|
| `validate_stock.py` | validates vocabulary v2 and the illustrative instructions — roughly 21,700 checks | runs inside `pytest`; standalone when you want the full report rather than pass/fail |
| `review_locales.py` | mechanically reviews the eleven locale bundles and flags what a human still has to confirm | after touching any `locales/*.json` |
| `make_fixtures.py` | creates the six measure fixtures once, and regenerates their expected JSON on demand | only for a deliberate change to what `measure` reports — see [tests/fixtures/](../tests/fixtures/README.md) |
| `check_links.py` | resolves every relative markdown link and names the ones that go nowhere | before a pull request, and after renaming anything |
| `check_translations.py` | says how far each document under [`docs/i18n/`](../docs/i18n/README.md) has drifted from the English it was made from | before a pull request, and after editing a translated document |
| `check_dco.py` | requires a valid signoff trailer on new commits, using `DCO_BASE_SHA` and `DCO_HEAD_SHA`; pre-adoption history is exempt | pull requests; tested with real temporary git histories inside pytest |
| `commit_check.py` | checks commit structure, asrai owners, changed numeric literals and conditional trailers; missing Git evidence fails | installed hooks, `--rev`, `--range`, or `--selftest`; see [runbook §7](../docs/runbook.md#7-landing-a-change) |
| `check_wheel.py` | builds a wheel, exports hashed runtime requirements, installs them into a temporary environment, checks installed CLI/MCP/data and immutable input bytes, and writes `dist/repro/` | before landing or releasing; choose a new `--out` directory for repeat runs |

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
