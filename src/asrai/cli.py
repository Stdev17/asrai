"""CLI transport over the same core as the MCP server. Every command prints one JSON document."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__, config, doctor, measure, records, vocab

SKILL = Path(__file__).resolve().parent / "data" / "skill" / "SKILL.md"


def _emit(obj) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False))


def _read_json(arg: str):
    return json.load(sys.stdin) if arg == "-" else json.loads(Path(arg).read_text("utf-8"))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="asrai", description=__doc__)
    p.add_argument("--version", action="version", version=__version__)
    sub = p.add_subparsers(dest="command", required=True)
    v = sub.add_parser("vocab", help="stock vocabulary lookup")
    vs = v.add_subparsers(dest="vocab_command", required=True)
    s = vs.add_parser("search", help="search labels, aliases (any language) and descriptions")
    s.add_argument("text"); s.add_argument("--lang", default="en"); s.add_argument("--category")
    s.add_argument("--limit", type=int, default=12); s.add_argument("--full", action="store_true")
    g = vs.add_parser("get", help="one term by exact id")
    g.add_argument("id"); g.add_argument("--lang", default="en"); g.add_argument("--compact", action="store_true")
    c = vs.add_parser("category", help="list one category")
    c.add_argument("id"); c.add_argument("--lang", default="en"); c.add_argument("--full", action="store_true")
    vs.add_parser("categories", help="list categories and counts")
    vs.add_parser("langs", help="list head-term languages")
    t = vs.add_parser("translations", help="one term in every language"); t.add_argument("id")
    m = sub.add_parser("measure", help="deterministic measurements of an image")
    m.add_argument("path"); m.add_argument("--target-width", type=int)
    r = sub.add_parser("record", help="append a validated record to the team log")
    r.add_argument("file", help="JSON file, or - for stdin")
    l = sub.add_parser("lint", help="lint an instruction.v2 JSON document"); l.add_argument("file")
    d = sub.add_parser("doctor", help="environment report; --lock writes asrai.lock.json"); d.add_argument("--lock", action="store_true")
    sub.add_parser("mcp", help="run the MCP server over stdio")
    sub.add_parser("skill-path", help="print the path of the bundled SKILL.md")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "vocab":
            vc = args.vocab_command
            if vc == "search":
                _emit(vocab.search(args.text, args.lang, args.category, args.limit, args.full))
            elif vc == "get":
                _emit(vocab.get(args.id, args.lang, full=not args.compact))
            elif vc == "category":
                _emit(vocab.category(args.id, args.lang, args.full))
            elif vc == "categories":
                _emit(vocab.categories())
            elif vc == "langs":
                _emit(vocab.langs())
            else:
                _emit(vocab.translations(args.id))
        elif args.command == "measure":
            _emit(measure.measure(Path(args.path), args.target_width))
        elif args.command == "record":
            cfg = config.load()
            _emit(records.append(_read_json(args.file), config.team_dir(cfg) / "records.jsonl"))
        elif args.command == "lint":
            errors = vocab.lint_instruction(_read_json(args.file))
            _emit({"valid": not errors, "errors": errors})
            return 1 if errors else 0
        elif args.command == "doctor":
            _emit(doctor.run(config.load(), write_lock=args.lock))
        elif args.command == "mcp":
            from .server import main as serve
            serve()
        else:
            print(SKILL)
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
