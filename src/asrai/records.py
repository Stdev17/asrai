"""Append-only JSONL records. No deletion, no in-place edits: only new records and `supersedes`."""
from __future__ import annotations

import hashlib
import json
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path

from . import vocab

LAYERS = ("L0", "L1", "L2")            # source structure / rendered asset / composed frame
LEVELS = ("asserted", "estimated", "unknown")
SCALES = ("native", "target", "thumbnail")   # the keys of measure.v1 `scales`
VERDICTS = ("prefer_a", "prefer_b", "equal", "unknown")
ASSET_KINDS = ("raster", "screenshot", "svg", "mesh")
SCHEMAS = {"observation": "observation.v1", "pairwise": "pairwise.v1", "instruction": "instruction.v2"}
# Reading order and coherence exist only between elements of one frame: never asserted on a lone asset.
L2_ONLY = frozenset(t for t in ("perception.visual_hierarchy", "perception.attention", "perception.style_coherence")
                    if t in vocab.index())
DIGIT = re.compile(r"(?<![A-Za-z_])\d")   # a digit inside an id (e2, pipe_2) is a name; a bare digit is a magnitude
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def canonical_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def sha256_file(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def new_id(prefix: str) -> str:
    return f"{prefix}_{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}_{secrets.token_hex(3)}"


def validate(record: dict) -> list[str]:
    if not isinstance(record, dict):
        return ["record must be a JSON object"]
    kind = record.get("kind")
    if not isinstance(kind, str) or kind not in SCHEMAS:
        return [f"unknown record kind {kind!r}; expected one of {sorted(SCHEMAS)}"]
    errors = []
    if record.get("evidence_layer") not in LAYERS:
        errors.append(f"evidence_layer must be one of {LAYERS}")
    if kind == "observation":
        errors += _validate_observation(record)
    elif kind == "pairwise":
        errors += _validate_pairwise(record)
    else:
        errors += vocab.lint_instruction(record)
    return errors


def _missing(value) -> bool:
    """A required field is a non-empty string, and this is the test for one. It used to be
    `str(value).strip()`, and `str(None)` is the string `None`: an empty value was caught and a null
    was not, so a null passed every check that calls its field required and reached the corpus."""
    return not isinstance(value, str) or not value.strip()


def _validate_observation(r: dict) -> list[str]:
    e = []
    if not HEX64.match(str(r.get("asset_sha256", ""))):
        e.append("asset_sha256 must be the 64-hex sha256 of the observed file")
    kind = r.get("asset_kind")
    if kind not in ASSET_KINDS:
        e.append(f"asset_kind must be one of {ASSET_KINDS}")
    layer = r.get("evidence_layer")
    if kind == "screenshot" and layer != "L2":
        e.append("a screenshot is a composed frame: evidence_layer must be L2")
    if kind in ("raster", "svg", "mesh") and layer != "L1":
        e.append("a single asset is observed through its render: evidence_layer must be L1")
    if kind in ("svg", "mesh") and not r.get("render_profile_id"):
        e.append("svg/mesh observations need render_profile_id (the render is the evidence, not the source)")
    if r.get("scale") not in SCALES:
        e.append(f"scale must be one of {SCALES}")
    obs = r.get("observer") or {}
    if not isinstance(obs, dict):
        return e + ["observer must be an object with mode, model and prompt_rev"]
    if obs.get("mode") not in ("host", "api"):
        e.append("observer.mode must be host or api")
    for key in ("model", "prompt_rev"):
        if _missing(obs.get(key)):
            e.append(f"observer.{key} required")
    items = r.get("observations")
    if not isinstance(items, list) or not items:
        e.append("observations must be a non-empty list")
        return e
    for i, o in enumerate(items):
        p = f"observations[{i}]"
        if not isinstance(o, dict):
            e.append(f"{p}: must be an object with term_id, level and note")
            continue
        tid = o.get("term_id")
        if tid not in vocab.index():
            e.append(f"{p}: unknown term_id {tid!r}")
        elif tid in L2_ONLY and layer == "L1" and o.get("level") != "unknown":
            e.append(f"{p}: {tid} is decided between elements of a frame; at L1 it can only be unknown")
        if o.get("level") not in LEVELS:
            e.append(f"{p}: level must be one of {LEVELS}")
        region = o.get("region", "whole_image")
        if region != "whole_image" and not (isinstance(region, list) and len(region) == 4
                                            and all(isinstance(v, int) and v >= 0 for v in region)):
            e.append(f"{p}: region must be 'whole_image' or [x, y, w, h] in pixels of the observed scale")
        if DIGIT.search(str(o.get("note", ""))):
            e.append(f"{p}: note must not contain numbers (ids like e2 are fine); magnitudes come from measurements or precedents")
    return e


def _validate_pairwise(r: dict) -> list[str]:
    e = []
    if r.get("term_id") not in vocab.index():
        e.append(f"unknown term_id {r.get('term_id')!r}")
    for side in ("a", "b"):
        if _missing(r.get(side)):
            e.append(f"{side} must reference an asset sha256, a record id or a case id")
    if r.get("verdict") not in VERDICTS:
        e.append(f"verdict must be one of {VERDICTS}")
    if r.get("by") not in ("human", "model"):
        e.append("by must be human or model")
    if r.get("by") == "model" and r.get("order_checked") is not True:
        e.append("model verdicts must set order_checked: true (A/B and B/A both asked; a flip means unknown)")
    if DIGIT.search(str(r.get("reason", ""))):
        e.append("reason must not contain numbers")
    return e


def append(record: dict, path: Path) -> dict:
    if not isinstance(record, dict):
        # `dict(record)` below raises first and says `'NoneType' object is not iterable`, which reaches
        # a model as the tool's error. The module already has the readable sentence for this case.
        raise ValueError("; ".join(validate(record)))
    rec = dict(record)
    rec.setdefault("id", new_id(str(rec.get("kind", "rec"))))
    rec.setdefault("created_at", datetime.now(timezone.utc).isoformat(timespec="seconds"))
    rec.setdefault("schema_version", SCHEMAS.get(rec.get("kind"), ""))
    errors = validate(rec)
    if errors:
        raise ValueError("; ".join(errors))
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(canonical_json(rec) + "\n")
    return rec


def read(path: Path) -> list[dict]:
    path = Path(path)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text("utf-8").splitlines() if line.strip()]
