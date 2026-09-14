# `tools/` — repository scripts

Three scripts. None of them ships in the wheel; all three are run with `uv run python tools/<name>.py`.

| script | what it does | when to run it |
|---|---|---|
| `validate_stock.py` | validates vocabulary v2 and the illustrative instructions — roughly 21,700 checks | runs inside `pytest`; standalone when you want the full report rather than pass/fail |
| `review_locales.py` | mechanically reviews the twelve locale bundles and flags what a human still has to confirm | after touching any `locales/*.json` |
| `make_fixtures.py` | creates the six measure fixtures once, and regenerates their expected JSON on demand | only for a deliberate change to what `measure` reports — see [tests/fixtures/](../tests/fixtures/README.md) |

`validate_stock.py` and `review_locales.py` are read-only. `make_fixtures.py` writes, and is the only
script here that does.

The first two are also called from the test suite, so the gate stays a single command. Keeping them as
scripts as well is deliberate: the standalone run prints the whole report, which is what you want when
you are changing the corpus rather than checking that it still passes.
