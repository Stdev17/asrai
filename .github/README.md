# GitHub checks

[`workflows/ci.yml`](workflows/ci.yml) runs on pull requests, pushes to `main`, and manual dispatches.
The `Checks` matrix installs the locked environment on Python 3.11 and 3.14, then runs the suite,
link and translation checks, and the wheel installation smoke test. Each matrix entry uploads its own
`asrai-repro-python-<version>` bundle from `dist/repro/`.

Pull requests also run the separate `DCO` workflow against the event's exact base and head commit
SHAs. `pull_request_target` loads that workflow and `tools/check_dco.py` from the trusted default
branch. It checks out only that branch, fetches the pull request's Git objects without checking them
out, and never imports, installs, or executes pull-request files. Commits at or before the fixed
grandfather commit are excluded. The workflow has read-only repository permission, persists no
checkout credential, and does not reference or pass repository secrets.

What a required check may be, and why a model reviewer is not one, is
[`runbook.md` §1](../docs/runbook.md#1-the-gate). `tools/check_claims_diff.py` is advisory by that rule:
if it is wired here it gets its own job, outside the required names below, and a model reviewer reading
its `--json` output is a comment and never a check.

The stable required-check names are:

- `Checks (Python 3.11)`
- `Checks (Python 3.14)`
- `DCO`

Repository files cannot activate a GitHub ruleset or branch protection. The trusted DCO workflow and
checker must first land on the default branch through explicit review and local validation; they
cannot protect their own bootstrap change. After that landing, a repository administrator must run
signed and unsigned pull-request cases, confirm the three check names above, and require them in the
remote settings. The workflows do not publish packages.
