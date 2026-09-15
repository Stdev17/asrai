#!/usr/bin/env python3
"""Check commit policy using only the standard library. See docs/conventions.md §5.

MSGFILE checks the staged diff. --message checks syntax for commit-msg;
--transaction checks actual commits before Git updates local refs.
--rev SHA [--msg FILE] and --range BASE..HEAD check existing commits.
--selftest runs the same disposable-history checks as pytest, without pytest.
"""
import argparse
import ast
import json
import pathlib
import re
import runpy
import subprocess
import sys
import tempfile
import tomllib

SCHEMA = """\
commit message schema (docs/conventions.md §5):

  type(scope): why-subject       feat fix docs chore refactor test perf build ci revert style
                                scope is an owner; 50 chars target, 72 hard; no final period
  <blank line>
  body explaining why
  <blank line>
  Owners: a, b                   exactly every owner touched
  Fixes: <sha>                   required on fix; a real commit affecting a touched file
  Values: name old->new; ...     required on changed numbers; see automatic coverage below
  Deviation: what — why — authority   cite the existing human approval, never self-authorize
  Source: <repo> <rev>           on a copy; commit SHA, provenance reviewed by a human
  Signed-off-by: Name <email>   required separately by the DCO gate

owners: runtime=src/asrai (except data)  stock=src/asrai/data/stock
  skill=src/asrai/data/skill  tests=tests  ci=.github  process=tools,.claude,.agents,
  AGENTS.md,CLAUDE.md,.mcp.json,.gitignore  docs=docs,README.md,CONTRIBUTING.md,CHANGELOG.md
  package=pyproject.toml,uv.lock,LICENSE  root=anything else

Automatic Values coverage: changed module-level Python literal assignments, numeric leaves in
JSON/JSONL/TOML; names may be qualified as path:name. Added/deleted fields, computed values,
prose, versions and other formats require author/reviewer judgment. Tests still gate behavior.
Source syntax is checked; copying and approval provenance cannot be inferred from a diff.
"""

OWNER_PREFIXES = [
    ("src/asrai/data/stock", "stock"), ("src/asrai/data/skill", "skill"),
    ("src/asrai", "runtime"), ("tests", "tests"), (".github", "ci"),
    ("tools", "process"), (".claude", "process"), (".agents", "process"), ("docs", "docs"),
]
ROOT_FILES = {
    **dict.fromkeys(("AGENTS.md", "CLAUDE.md", ".mcp.json", ".gitignore"), "process"),
    **dict.fromkeys(("README.md", "CONTRIBUTING.md", "CHANGELOG.md"), "docs"),
    **dict.fromkeys(("pyproject.toml", "uv.lock", "LICENSE"), "package"),
}
OWNER_NAMES = {name for _, name in OWNER_PREFIXES} | set(ROOT_FILES.values()) | {"root"}
TYPES = {"feat", "fix", "docs", "chore", "refactor", "test", "perf", "build", "ci", "revert", "style"}
KNOWN_TRAILERS = {"owners", "fixes", "values", "deviation", "source", "spec", "co-authored-by", "signed-off-by", "refs"}
SHA = re.compile(r"[0-9a-f]{7,64}")
AUTHORITY = re.compile(r"\b(fallback|graceful|defensive|best-effort|compatib\w*|intelligent|robust|workaround)\b", re.I)
BUNDLING = re.compile(r"\balso\b|\bwhile (?:i'm|we're|i am|we are) (?:here|at it)\b", re.I)


def owner(path):
    if path in ROOT_FILES:
        return ROOT_FILES[path]
    for prefix, name in OWNER_PREFIXES:
        if path == prefix or path.startswith(prefix + "/"):
            return name
    return "root"


def git(*args, text=None):
    result = subprocess.run(["git", *args], capture_output=True, text=True, encoding="utf-8", input=text)
    if result.returncode:
        raise ValueError(f"git {' '.join(args)}: {result.stderr.strip() or 'failed'}")
    return result.stdout


def commit(ref):
    return git("rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}").strip()


class Diff:
    """Stable blob ids from the index or a commit's first-parent diff, including root commits."""
    def __init__(self, rev=None):
        if rev and git("rev-parse", "--is-shallow-repository").strip() == "true":
            raise ValueError("full git history is required to compare a commit with its parent")
        args = (["diff-tree", "--root", "--diff-merges=first-parent", "-r", "--no-commit-id", commit(rev)]
                if rev else ["diff", "--cached"])
        raw = git(*args, "--raw", "-z", "--no-abbrev", "--no-renames", "--").split("\0")
        self.blobs = {}
        for metadata, path in zip(raw[0:-1:2], raw[1:-1:2]):
            _, _, old, new, _ = metadata.split()
            self.blobs[path] = (old, new)
        self.files = list(self.blobs)

    def content(self, blob):
        return "" if set(blob) == {"0"} else git("cat-file", "blob", blob)


def numeric_values(path, text):
    """Literal quantities only. Meaning and unmodelled formats remain review obligations."""
    if not text:
        return {}
    values = {}

    def collect(value, key):
        if type(value) in (int, float):
            values[key] = str(value)
        elif isinstance(value, dict):
            for name, child in value.items():
                collect(child, f"{key}.{name}" if key else name)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                collect(child, f"{key}[{index}]")

    suffix = pathlib.Path(path).suffix
    if suffix == ".py":
        # Module bindings have stable names; local assignments and expressions need review.
        for node in ast.parse(text, filename=path).body:
            if isinstance(node, (ast.Assign, ast.AnnAssign)) and node.value is not None:
                try:
                    value = ast.literal_eval(node.value)
                except (ValueError, TypeError):
                    continue
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    if isinstance(target, ast.Name):
                        collect(value, target.id)
    elif suffix == ".json":
        collect(json.loads(text), "")
    elif suffix == ".jsonl":
        for index, line in enumerate(text.splitlines()):
            if line.strip():
                collect(json.loads(line), str(index))
    elif suffix == ".toml" or path == "uv.lock":
        collect(tomllib.loads(text), "")
    return values


def changed_values(diff):
    for path, (before, after) in diff.blobs.items():
        if pathlib.Path(path).suffix not in {".py", ".json", ".jsonl", ".toml"} and path != "uv.lock":
            continue
        old = numeric_values(path, diff.content(before))
        new = numeric_values(path, diff.content(after))
        for key in old.keys() & new.keys():
            if old[key] != new[key]:
                yield path, key, old[key], new[key]


def parse_message(text):
    lines = [l.rstrip() for l in text.splitlines() if not l.startswith("#")]
    while lines and not lines[-1]:
        lines.pop()
    subject = lines[0] if lines else ""
    rest = lines[1:]
    paragraphs, cur = [], []
    for l in rest:
        if l.strip():
            cur.append(l)
        elif cur:
            paragraphs.append(cur); cur = []
    if cur:
        paragraphs.append(cur)
    trailers = {}
    last = None
    if paragraphs and all(re.match(r"^[A-Za-z-]+: \S", l) or l.startswith(" ") for l in paragraphs[-1]):
        for l in paragraphs.pop():
            if re.match(r"^[A-Za-z-]+: ", l):
                k, v = l.split(": ", 1)
                key = k.strip().lower()
                if key in trailers and key not in {"signed-off-by", "co-authored-by"}:
                    raise ValueError(f"duplicate trailer: {k}")
                trailers[key] = v.strip()
                last = key
            elif last:
                trailers[last] += " " + l.strip()
    body = "\n".join("\n".join(p) for p in paragraphs)
    blank_after_subject = len(lines) < 2 or not lines[1].strip()
    return subject, body, trailers, blank_after_subject


def check(message, diff=None):
    fails, warns = [], []
    subject, body, trailers, blank = parse_message(message)
    # subject
    if len(subject) > 72:
        fails.append(f"subject is {len(subject)} chars; 72 is the hard limit")
    elif len(subject) > 50:
        warns.append(f"subject is {len(subject)} chars; 50 is the target")
    if subject.endswith("."):
        fails.append("subject ends with a period")
    m = re.match(r"^(\w+)\(([^)]+)\)!?: (\S.*)$", subject)
    typ = scope = None
    if not m:
        fails.append("subject is not `type(scope): description`")
    else:
        typ, scope = m.group(1), m.group(2)
        if typ not in TYPES:
            fails.append(f"type `{typ}` is not one of {' '.join(sorted(TYPES))}")
        if scope and scope not in OWNER_NAMES:
            fails.append(f"scope `{scope}` is not an owner")
    if not blank:
        fails.append("no blank line after the subject")
    if not body.strip():
        fails.append("no body: say why")
    # Owners are syntactic at commit-msg time and exact once Git creates the commit.
    declared = {o.strip() for o in trailers.get("owners", "").split(",") if o.strip()}
    if not declared:
        fails.append("no Owners trailer: name every owner touched")
    for name in sorted(declared - OWNER_NAMES):
        fails.append(f"Owners names `{name}`, not an owner")
    if diff is not None:
        touched = {owner(p) for p in diff.files}
        if declared - touched:
            fails.append(f"Owners lists {', '.join(sorted(declared - touched))}: not in the diff")
        if touched - declared:
            fails.append(f"Owners misses {', '.join(sorted(touched - declared))}: in the diff")
    if scope and declared and scope not in declared:
        fails.append(f"scope `{scope}` is not in Owners")
    if typ == "fix" and "fixes" not in trailers:
        fails.append("type fix without Fixes: <sha>")
    if "fixes" in trailers:
        value = trailers["fixes"]
        if not SHA.fullmatch(value):
            fails.append("Fixes must name a commit SHA")
        else:
            planted = Diff(commit(value))
            if diff is not None and not set(planted.files) & set(diff.files):
                fails.append(f"Fixes: {value} touches no file this diff touches")
    declared_values = set()
    if "values" in trailers:
        for entry in trailers["values"].split(";"):
            match = re.fullmatch(r"\s*(\S+)\s+(\S+)->(\S+)\s*", entry)
            if not match:
                fails.append("Values must be name old->new; ...")
            else:
                declared_values.add(match.groups())
    if diff is not None:
        for path, key, old, new in changed_values(diff):
            if not {(key, old, new), (f"{path}:{key}", old, new)} & declared_values:
                fails.append(f"{path}: {key} {old}->{new} not in Values")
    if AUTHORITY.search(body) and "deviation" not in trailers:
        fails.append("body names an exception with no Deviation: what — why — authority")
    if "deviation" in trailers:
        parts = trailers["deviation"].split(" — ")
        if len(parts) != 3 or not all(p.strip() for p in parts):
            fails.append("Deviation must be what — why — authority (an existing approval)")
    if "source" in trailers and not re.fullmatch(r"\S+ [0-9a-f]{7,64}", trailers["source"]):
        fails.append("Source must be <repo> <rev>, with a commit SHA")
    elif "source" in trailers:
        warns.append("Source syntax checked; review the source revision, paths and adaptations")
    if BUNDLING.search(body):
        warns.append(f"body says `{BUNDLING.search(body).group(0)}`: bundling? split, or name the owner")
    for k in trailers:
        if k not in KNOWN_TRAILERS:
            warns.append(f"unknown trailer `{k}`")
    return fails, warns


def report(label, fails, warns, full=True):
    verdict = "FAIL" if fails else "PASS"
    print(f"{label}: {verdict}")
    for f in fails:
        print(f"  fail: {f}")
    for w in warns:
        print(f"  warn: {w}")
    if fails and full:
        print("\n" + SCHEMA)
    return not fails


def check_revisions(revisions, message=None):
    ok = True
    for rev in revisions:
        msg = message if message is not None else git("show", "-s", "--format=%B", rev)
        ok = report(rev[:12], *check(msg, Diff(rev))) and ok
    return ok


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--rev")
    group.add_argument("--range", dest="revision_range")
    group.add_argument("--message", action="store_true")
    group.add_argument("--transaction", action="store_true")
    group.add_argument("--selftest", action="store_true")
    parser.add_argument("--msg", type=pathlib.Path)
    parser.add_argument("file", nargs="?", type=pathlib.Path)
    args = parser.parse_args(argv)
    if args.msg and not args.rev:
        parser.error("--msg requires --rev")
    if args.file and (args.rev or args.revision_range or args.transaction or args.selftest):
        parser.error("unexpected message file")
    try:
        if args.selftest:
            tests = runpy.run_path(str(pathlib.Path(__file__).resolve().parents[1] / "tests/test_commit_check.py"))
            for name, test in tests.items():
                if name.startswith("test_"):
                    with tempfile.TemporaryDirectory(prefix="asrai-commit-") as directory:
                        test(pathlib.Path(directory))
                    print(f"PASS {name}")
            return 0
        if args.transaction:
            tips = set()
            for line in sys.stdin:
                old, new, ref = line.split()
                if ref != "HEAD" and not ref.startswith("refs/heads/"):
                    continue
                for value in (old, new):
                    if value.startswith("ref:"):
                        git("check-ref-format", value[4:])
                    elif not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value):
                        raise ValueError("invalid reference transaction object id")
                if not new.startswith("ref:") and set(new) != {"0"}:
                    tips.add(commit(new))
            revisions = git("rev-list", "--reverse", *sorted(tips), "--not", "--all").splitlines() if tips else []
            return 0 if check_revisions(revisions) else 1
        if args.revision_range:
            parts = args.revision_range.split("..")
            if len(parts) != 2 or not all(parts) or any(p.startswith(".") for p in parts):
                raise ValueError("--range requires BASE..HEAD")
            base, head = map(commit, parts)
            revisions = git("rev-list", "--reverse", f"{base}..{head}").splitlines()
            if not revisions:
                print("PASS: valid range contains no commits")
            return 0 if check_revisions(revisions) else 1
        if args.rev:
            msg = args.msg.read_text("utf-8") if args.msg else None
            return 0 if check_revisions([commit(args.rev)], msg) else 1
        if not args.file:
            parser.error("a message file or check mode is required")
        diff = None if args.message else Diff()
        return 0 if report("commit message", *check(args.file.read_text("utf-8"), diff)) else 1
    except (ValueError, OSError, SyntaxError) as error:
        report("commit policy", [str(error)], [])
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
