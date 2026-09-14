# `tools/` — repository scripts

None of these ships in the wheel; each is run with `uv run python tools/<name>.py`. The table is the count.

| script | what it does | when to run it |
|---|---|---|
| `validate_stock.py` | validates vocabulary v2 and the illustrative instructions — roughly 21,700 checks | runs inside `pytest`; standalone when you want the full report rather than pass/fail |
| `review_locales.py` | mechanically reviews the eleven locale bundles and flags what a human still has to confirm | after touching any `locales/*.json` |
| `make_fixtures.py` | creates the six measure fixtures once, and regenerates their expected JSON on demand | only for a deliberate change to what `measure` reports — see [tests/fixtures/](../tests/fixtures/README.md) |
| `check_links.py` | resolves every relative markdown link and names the ones that go nowhere | before a pull request, and after renaming anything |

`make_fixtures.py` is the only script here that writes; the other three are read-only.

`validate_stock.py` and `review_locales.py` are also called from the test suite, so the gate stays a
single command. Keeping them as scripts as well is deliberate: the standalone run prints the whole
report, which is what you want when you are changing the corpus rather than checking that it still
passes. `check_links.py` is not in the suite, because what it checks is a fact about this repository rather
than behaviour of the package a user installs.
