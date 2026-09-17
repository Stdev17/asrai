"""CLI transport over the same core as the MCP server. Every command prints one JSON document."""
from __future__ import annotations

import argparse
import json
import sys
from typing import Any
from pathlib import Path

from . import __version__, config, doctor, light, measure, profile, records, run as run_mod, vocab

SKILL = Path(__file__).resolve().parent / "data" / "skill" / "SKILL.md"


def _emit(obj) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False))


def _read_json(arg: str):
    return json.load(sys.stdin) if arg == "-" else json.loads(Path(arg).read_text("utf-8"))


SUBJECT_FORM = "ID=X,Y,W,H[,depth][@mask.png]"


def _subject(arg: str) -> dict:
    """The whole subject contract of spec.md 7.1, so the CLI can say everything the MCP tool can."""
    sid, _, rest = arg.partition("=")
    box, _, mask = rest.partition("@")
    try:
        nums = [int(v) for v in box.split(",")]
    except ValueError:
        nums = []
    if len(nums) not in (4, 5):
        raise ValueError(f"--subject wants {SUBJECT_FORM} in pixels, got {arg!r}")
    out: dict[str, Any] = {"id": sid, "bbox": nums[:4]}
    if len(nums) == 5:
        out["depth"] = nums[4]
    if mask:
        out["mask"] = mask
    return out


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
    g.add_argument("id"); g.add_argument("--lang", default="en")
    g.add_argument("--full", action=argparse.BooleanOptionalAction, default=True)   # one word on every surface
    c = vs.add_parser("category", help="list one category")
    c.add_argument("id"); c.add_argument("--lang", default="en"); c.add_argument("--full", action="store_true")
    vs.add_parser("categories", help="list categories and counts")
    vs.add_parser("langs", help="list head-term languages")
    t = vs.add_parser("translations", help="one term in every language"); t.add_argument("id")
    m = sub.add_parser("measure", help="deterministic measurements of an image")
    m.add_argument("path"); m.add_argument("--target-width", type=int)
    lg = sub.add_parser("light-ledger", help="lighting pass: shading direction per subject against proposed emitters; overlay under out/")
    lg.add_argument("path")
    lg.add_argument("--subject", action="append", metavar=SUBJECT_FORM,
                    help="repeatable; pixels of the image, an optional layer index (0 nearest), and an "
                         "optional mask image whose alpha marks the subject's pixels (a layer export)")
    lg.add_argument("--capture", help="capture.json whose composed_of screen boxes become the subjects")
    lg.add_argument("--mirror", action="store_true", help="measure the horizontally mirrored image")
    lg.add_argument("--profile", choices=[p["id"] for p in light.profiles()["profiles"]],
                    help="also say the verdict for one reader, under `sentences`; omit for the result alone")
    lg.add_argument("--answers", help="the filled form (JSON file, or - for stdin): returns verdict and record")
    lg.add_argument("--out", help="overlay directory (default: paths.out from asrai.toml)")
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
                _emit(vocab.get(args.id, args.lang, full=args.full))
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
        elif args.command == "light-ledger":
            cfg = config.load()
            subjects = [_subject(s) for s in args.subject] if args.subject else None
            out = Path(args.out) if args.out else Path(cfg["_root"]) / cfg["paths"]["out"]
            answers = _read_json(args.answers) if args.answers else None
            # the profile never reaches `ledger`: it selects a reading of a finished result, and the
            # overlay is read here rather than there so `light` stays free of team directories
            seen = profile.overlay(config.team_dir(cfg))["scopes"] if args.profile else None
            _emit(light.for_reader(run_mod.ledger(Path(args.path), subjects, args.capture, out,
                                                args.mirror, answers, cfg["observer"]), args.profile, seen))
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
