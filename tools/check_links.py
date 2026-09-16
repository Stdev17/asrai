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

It also checks the other direction. A directory whose README enumerates its contents has an index that
can fall behind the directory, and the failure is silent in the same way: three reviews sat unlisted
for a day, reachable only from whichever document happened to cite them. Broken links are documents
pointing at nothing; an unindexed file is a document nothing points at, and one walk finds both.
"""

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
SKIP = {".venv", ".git", "node_modules", "__pycache__", "out"}
# Directories whose README enumerates what lives in them, so a new file has to be listed to be read.
# Only docs/review/ does today; add a row when a second index appears, not before.
INDEXED = {"docs/review": "README.md"}


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

    unindexed = []
    for folder, index in sorted(INDEXED.items()):
        listing = (ROOT / folder / index).read_text("utf-8")
        for md in sorted((ROOT / folder).glob("*.md")):
            if md.name != index and md.name not in listing:
                unindexed.append(f"{folder}/{md.name} is not named in {folder}/{index}")

    for line in broken:
        print(f"broken  {line}", file=sys.stderr)
    for line in unindexed:
        print(f"unindexed  {line}", file=sys.stderr)
    print(f"{len(broken)} broken relative links, {len(unindexed)} unindexed files")
    return 1 if broken or unindexed else 0


if __name__ == "__main__":
    sys.exit(main())
