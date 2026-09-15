"""Require a valid DCO signoff on commits introduced by a change."""

import os
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GRANDFATHER = "1ecfc08af7d1b9c6d009e80341638d97020ec815"
SIGNOFF = re.compile(
    r"Signed-off-by:\s*[^<>\s](?:[^<>]*[^<>\s])?\s+<[^<>\s@]+@[^<>\s@]+>",
    re.IGNORECASE,
)


class DCOError(RuntimeError):
    pass


def _git(repo, *args, input_text=None):
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        input=input_text,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        raise DCOError(result.stderr.strip() or "git command failed")
    return result.stdout


def _commit(repo, ref):
    try:
        return _git(
            repo,
            "rev-parse",
            "--verify",
            "--end-of-options",
            f"{ref}^{{commit}}",
        ).strip()
    except DCOError as error:
        raise DCOError(f"invalid or unavailable commit {ref!r}: {error}") from error


def check(repo, base, head, grandfather=GRANDFATHER):
    repo = Path(repo)
    if _git(repo, "rev-parse", "--is-shallow-repository").strip() == "true":
        raise DCOError("full git history is required")

    base = _commit(repo, base)
    head = _commit(repo, head)
    grandfather = _commit(repo, grandfather)
    commits = _git(
        repo,
        "rev-list",
        f"{base}..{head}",
        "--not",
        grandfather,
    ).splitlines()

    unsigned = []
    for commit in commits:
        message = _git(repo, "show", "-s", "--format=%B", commit)
        trailers = _git(repo, "interpret-trailers", "--parse", input_text=message)
        if not any(SIGNOFF.fullmatch(line) for line in trailers.splitlines()):
            unsigned.append(commit)

    if unsigned:
        raise DCOError("missing valid Signed-off-by trailer: " + ", ".join(unsigned))


def main():
    try:
        base = os.environ["DCO_BASE_SHA"]
        head = os.environ["DCO_HEAD_SHA"]
        check(ROOT, base, head)
    except KeyError as error:
        print(f"DCO check failed: missing environment variable {error.args[0]}", file=sys.stderr)
        return 1
    except DCOError as error:
        print(f"DCO check failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
