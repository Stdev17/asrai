#!/usr/bin/env python3
"""Report how far each translated document has drifted from the English it was made from.

Every file under docs/i18n/<lang>/ carries a stamp on line 1 naming its source and the source's
commit at translation time. This script compares that commit with the source's latest one.

A missing, malformed or impossible stamp is an error and exits non-zero: it means the file cannot
be checked at all, which is worse than being out of date. Staleness is reported and never fails:
decided 2026-09-15, a stale translation does not block a merge, and a language is held to a named
owner instead (docs/i18n/README.md). The commit subjects are printed with the count so that owner
can tell a typo from a promise.
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
I18N = ROOT / "docs" / "i18n"
# A translated contract is a second source of truth: when the two disagree, work stops to find out
# which one the code obeys. docs/i18n/README.md and docs/README.md carry the same rule in prose.
NEVER_TRANSLATED = ("docs/spec.md", "docs/conventions.md", "src/asrai/data/skill/SKILL.md", "docs/review/")
STAMP = re.compile(r"^<!-- translation-of: (\S+)@([0-9a-f]{7,40}) -->\s*$")


def git(*args: str) -> str:
    done = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)
    return done.stdout.rstrip() if done.returncode == 0 else ""  # rstrip only: the log format leads with two spaces


def main() -> int:
    errors, stale, ok = [], [], []
    for path in sorted(I18N.rglob("*.md")):
        if path.parent == I18N:
            continue  # docs/i18n/README.md states the rule; it translates nothing
        here = path.relative_to(ROOT).as_posix()
        first = path.read_text(encoding="utf-8").split("\n", 1)[0]
        stamp = STAMP.match(first)
        if not stamp:
            errors.append(f"{here}: line 1 is not a `<!-- translation-of: PATH@SHA -->` stamp")
            continue
        source, sha = stamp.group(1), stamp.group(2)
        if not (ROOT / source).exists():
            errors.append(f"{here}: source {source} does not exist")
            continue
        if source.startswith(NEVER_TRANSLATED):
            errors.append(f"{here}: {source} may never be translated (docs/i18n/README.md)")
            continue
        if not git("rev-parse", "--quiet", "--verify", f"{sha}^{{commit}}"):
            errors.append(f"{here}: {sha} is not a commit in this repository")
            continue
        latest = git("log", "-1", "--format=%H", "--", source)
        if latest.startswith(sha):
            ok.append(f"{here} <- {source}@{sha[:7]}")
            continue
        since = git("log", "--format=  %h %s", f"{sha}..HEAD", "--", source).splitlines()
        plural = "commit" if len(since) == 1 else "commits"
        stale.append(f"{here}: {source} moved {len(since)} {plural} since {sha[:7]}")
        stale.extend(since)

    for line in ok:
        print(f"ok     {line}")
    for line in stale:
        print(f"stale  {line}" if not line.startswith("  ") else line)
    for line in errors:
        print(f"error  {line}", file=sys.stderr)

    print(f"\n{len(ok)} current, {sum(1 for s in stale if not s.startswith('  '))} stale, {len(errors)} broken")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
