#!/usr/bin/env python3
"""Resolve every relative markdown link in the repository and name the ones that go nowhere.

Renaming a directory is the cheap part; the links into it rot silently, and a reader who follows one
concludes the document is abandoned. This found four `docs/reviews/` -> `docs/review/` typos left from
before that folder was renamed. Anchors are ignored: only the file part is resolved.
"""

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
            if not (md.parent / target).resolve().exists():
                broken.append(f"{md.relative_to(ROOT)} -> {target}")

    for line in broken:
        print(f"broken  {line}", file=sys.stderr)
    print(f"{len(broken)} broken relative links")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
