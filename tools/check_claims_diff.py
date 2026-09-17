"""Tier 2 of the gate (`docs/runbook.md` §1): a number added to prose that no `claims.json` row covers.

Advisory, and never a required check. It reports and does not decide: the answer to a finding is to
register the number or to say it is not a claim. `claims.json` is a whitelist — nothing else looks for
a number no row claims — and this is the net around it, including the case a row covers a value for
some files but not the one it was just written into.

It is also what bounds a model reviewer downstream. `--json` emits the flagged lines and nothing else
of the diff, so what a model is shown is chosen here, deterministically, rather than by the
contribution: a pull request cannot put text in front of the reviewer by writing it somewhere the
scanner never looked.

    python tools/check_claims_diff.py                     # working tree against HEAD, before committing
    python tools/check_claims_diff.py origin/main...HEAD  # a pull request
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLAIMS = ROOT / "tests" / "claims.json"

# The word a document may spell a number with. `tests/test_asrai.py` anchors its rows on the same map,
# so a word this repository writes and a word the scanner knows cannot drift apart.
NUMBER_WORDS = {0.25: "quarter", 2: "two", 4: "four", 6: "six", 7: "seven", 8: "eight", 9: "nine",
                10: "ten", 11: "eleven", 12: "twelve", 16: "sixteen", 20: "twenty", 22: "twenty-two",
                60: "sixty"}
WORD_VALUE = {w: v for v, w in NUMBER_WORDS.items()}

# CHECKPOINT.md is append-only, so an old entry is a frozen observation and no claim may anchor there;
# review/ and experiments/ are frozen for the same reason. i18n mirrors are held to the English row.
SKIP_FILES = ("docs/CHECKPOINT.md", "tests/claims.json")
SKIP_DIRS = ("docs/review/", "docs/i18n/", "docs/experiments/", "tests/fixtures/")
STOCK_PROSE = ("src/asrai/data/stock/surfaces.v1.json", "src/asrai/data/stock/profiles.v1.json")

FENCE = re.compile(r"^\s*```")
DROP = (re.compile(r"`[^`]*`"),                       # an id in code voice is a reference, not a claim
        re.compile(r"\]\([^)]*\)|https?://\S+"),      # link targets and urls
        re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),         # dates
        re.compile(r"\bv?\d+(?:\.\d+){2,}\b|\bv\d+(?:\.\d+)+\b|\bPython \d+(?:\.\d+)*"),
        re.compile(r"\.v\d+\b|\b[A-Za-z]+\d+\b|\b[0-9a-f]{7,}\b|#\d+|\b\d+-bit\b"),
        re.compile(r"§\s*\d+|\b(?:tiers?|sections?|steps?|phases?|rounds?|invariants?|items?|figures?"
                   r"|tables?)\s+(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten)"
                   r"(?:\s*(?:,|and)\s*(?:\d+|one|two|three|four|five|six|seven|eight|nine|ten))*\b", re.I),
        re.compile(r"^\s*(?:[-*+]|\d+[.)]|#{1,6})\s+"))
NUMERAL = re.compile(r"\b\d{1,3}(?:,\d{3})+\b|\b\d+(?:\.\d+)?\b")   # a separator is punctuation


def scanned(path: str) -> bool:
    if path in SKIP_FILES or any(path.startswith(d) for d in SKIP_DIRS):
        return False
    return path.endswith((".md", ".py")) or path in STOCK_PROSE


def added(rev: str | None) -> dict[str, list[tuple[int, str]]]:
    """Added lines per file, with their line numbers in the new file. `--unified=0`: no context rows."""
    out = subprocess.run(["git", "diff", "--unified=0", "--no-color", rev or "HEAD"],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout
    files: dict[str, list[tuple[int, str]]] = {}
    path, line = None, 0
    for row in out.splitlines():
        if row.startswith("+++ "):
            path = row[6:] if row.startswith("+++ b/") else None
        elif row.startswith("@@"):
            hunk = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)", row)
            line = int(hunk.group(1)) if hunk else 0
        elif path and row.startswith("+"):
            files.setdefault(path, []).append((line, row[1:]))
            line += 1
    return files


def prose_only(path: str, rows: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """Python prose is what its comments and strings say, not the lines they sit on: a dict of constants
    holds a string and is still code, and code is tier 1's business."""
    if not path.endswith(".py"):
        return rows
    file = ROOT / path
    if not file.exists():
        return []
    said: dict[int, list[str]] = {}
    try:
        with file.open("rb") as handle:
            for tok in tokenize.tokenize(handle.readline):
                if tok.type == tokenize.COMMENT or (tok.type == tokenize.STRING
                                                    and tok.string.lstrip("rbfuRBFU")[:3] in ('"""', "'''")):
                    for i, piece in enumerate(tok.string.splitlines()):
                        said.setdefault(tok.start[0] + i, []).append(piece)
    except (tokenize.TokenError, SyntaxError):
        return rows                       # unparsable head: report everything rather than nothing
    return [(n, " ".join(said[n])) for n, _ in rows if n in said]


def numerals(value) -> tuple[str, ...]:
    """Every way prose writes this magnitude as a numeral: bare, and with a thousands separator.

    The writing direction. `NUMERAL` above is the reading one, and the two have to agree: a spelling one
    of them knows and the other does not is a number that passes whichever tier happens to be asked.
    They are one definition here, in the module both tiers already import `NUMBER_WORDS` from, because
    three answers to one question is how a number gets around all of them."""
    plain = str(value)
    return (plain,) if not isinstance(value, int) or abs(value) < 1000 else (plain, f"{value:,}")


def numbers(text: str):
    """Every magnitude a sentence carries, after the shapes that are never claims are removed."""
    for pattern in DROP:
        text = pattern.sub(" ", text)
    for hit in NUMERAL.finditer(text):
        raw = hit.group(0)
        plain = raw.replace(",", "")        # a thousands separator is punctuation, not a second magnitude
        yield (float(plain) if "." in plain else int(plain)), raw
    for word, value in WORD_VALUE.items():
        if re.search(rf"\b{re.escape(word)}\b", text, re.I):
            yield value, word


def scan(rev: str | None) -> list[dict]:
    rows = json.loads(CLAIMS.read_text("utf-8"))["claims"]
    findings, said = [], set()
    for path, lines in sorted(added(rev).items()):
        if not scanned(path):
            continue
        fenced = False
        for number, text in prose_only(path, lines):
            if FENCE.match(text):
                fenced = not fenced
            if fenced or FENCE.match(text):
                continue
            for value, token in numbers(text):
                covered = [c for c in rows if c["value"] == value]
                if any(path in c["claimed_in"] for c in covered):
                    continue
                seen = (path, number, value)
                if seen in said:
                    continue
                said.add(seen)
                findings.append({"path": path, "line": number, "value": value, "token": token,
                                 "text": text.strip()[:120],
                                 "rows": [c["id"] for c in covered]})
    return findings


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("rev", nargs="?", help="a git range; default is the working tree against HEAD")
    ap.add_argument("--json", action="store_true", help="the findings only, for a downstream reviewer")
    args = ap.parse_args(argv)
    findings = scan(args.rev)
    if args.json:
        print(json.dumps(findings, ensure_ascii=False, indent=2))
        return 1 if findings else 0
    if not findings:
        print("no unregistered number added to prose")
        return 0
    print(f"{len(findings)} number(s) added to prose that tests/claims.json does not cover for that file.")
    print("Advisory: register the number, or say in review why it is not a claim.\n")
    for f in findings:
        where = f" (registered for other files as {', '.join(f['rows'])})" if f["rows"] else ""
        print(f"  {f['path']}:{f['line']}  {f['value']}  as {f['token']!r}{where}")
        print(f"    | {f['text']}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
