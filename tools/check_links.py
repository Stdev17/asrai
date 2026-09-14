#!/usr/bin/env python3
"""Resolve every relative markdown link in the repository and name the ones that go nowhere.

Renaming a directory is the cheap part; the links into it rot silently, and a reader who follows one
concludes the document is abandoned. This found four `docs/reviews/` -> `docs/review/` typos left from
before that folder was renamed. Anchors are ignored: only the file part is resolved.

A link that climbs above the repository root is broken even when it resolves on this machine. One
review linked to `../../../asrai/docs/spec.md`, which walks out of the checkout and back in through a
directory that happens to be named `asrai` — fine here, dead in a worktree and in anyone else's clone.
The walk is normalised lexically, so a path that leaves and returns is caught along with one that
simply leaves.
"""

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
SKIP = {".venv", ".git", "node_modules", "__pycache__", "out"}


def main() -> int:
    broken = []
    for md in sorted(ROOT.rglob("*.md")):
        if SKIP & set(md.parts):
            continue
        for match in LINK.finditer(md.read_text("utf-8")):
            target = match.group(1).split("#")[0].strip()
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            walk = os.path.normpath(os.path.join(md.parent.relative_to(ROOT).as_posix(), target))
            if walk.startswith(".."):
                broken.append(f"{md.relative_to(ROOT)} -> {target} (climbs above the repository root)")
            elif not (ROOT / walk).exists():
                broken.append(f"{md.relative_to(ROOT)} -> {target}")

    for line in broken:
        print(f"broken  {line}", file=sys.stderr)
    print(f"{len(broken)} broken relative links")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
