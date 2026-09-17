"""Stock vocabulary v2: lookup, search and instruction lint.

The English bundle is the only spec (units, operations, quantification, guidance).
`locales/<code>.json` own the head-term label and spoken description per language.
Nothing here executes a graphics tool; a passing lint is not permission to apply.
"""
from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path
from typing import Any

DATA = Path(__file__).resolve().parent / "data" / "stock"
LANG_ALIASES = {
    "zh": "zh-Hans", "zh-cn": "zh-Hans", "zh-sg": "zh-Hans", "zh-tw": "zh-Hant", "zh-hk": "zh-Hant",
    "id": "ms", "in": "ms", "ms-my": "ms", "id-id": "ms", "ko-kr": "ko", "ja-jp": "ja", "en-us": "en",
    "en-gb": "en", "pt-br": "pt", "pt-pt": "pt", "es-es": "es", "es-419": "es", "th-th": "th",
}
# Numeric ops whose magnitude is meaningless without a fixed reference state.
DELTA_OPS = ("relative_delta", "multiply", "add_delta", "percentage_point_delta")
DIRECT_OPS = ("set",) + DELTA_OPS
# the three operations whose unit the operation itself fixes, and the unit each one fixes it to.
# Keyed on `object` because the operation is read from a model-supplied document: a lookup with
# whatever arrived there answers nothing, which is the answer, rather than raising here.
UNIT_FOR_OP: dict[object, str] = {"relative_delta": "percent_relative", "multiply": "factor",
                                  "percentage_point_delta": "percentage_point"}
# Material scalars whose number only means something inside a declared shader model.
MATERIAL_SCALARS = ("material.roughness", "material.smoothness", "material.metallic")


def _load(path: Path) -> Any:
    def reject(token: str) -> None:
        raise ValueError(f"Non-JSON numeric literal: {token}")
    with path.open(encoding="utf-8") as handle:
        return json.load(handle, parse_constant=reject)


@lru_cache(maxsize=1)
def pack() -> dict[str, Any]:
    return _load(DATA / "vocab.v2.json")


@lru_cache(maxsize=1)
def index() -> dict[str, dict[str, Any]]:
    return {e["id"]: e for e in pack()["entries"]}


def locale_codes() -> list[str]:
    """`en` is the base bundle itself; every other language is an overlay file."""
    return sorted({"en", *(p.stem for p in (DATA / "locales").glob("*.json"))})


def resolve_lang(code: str) -> str:
    folded = LANG_ALIASES.get(code.casefold(), code).casefold()
    for name in locale_codes():
        if name.casefold() == folded:
            return name
    raise ValueError(f"Unknown language {code!r}. Available: {', '.join(locale_codes())} (or 'all')")


@lru_cache(maxsize=None)
def locale(code: str) -> dict[str, dict[str, Any]]:
    if code == "en":
        return {e["id"]: {"label": e["label"], "description": e["description"]} for e in pack()["entries"]}
    return _load(DATA / "locales" / f"{code}.json")["terms"]


def localize(entry: dict, terms: dict, code: str) -> dict:
    """Head-term view in one language. Specs are never translated."""
    row = terms.get(entry["id"], {})
    out = {"lang": code, "label": row.get("label", entry["label"]),
           "description": row.get("description", entry["description"])}
    if row.get("aliases"):
        out["aliases"] = row["aliases"]
    return out


def expand(entry: dict) -> dict:
    """Entries store profile_id only; the shared note lives in the registry."""
    q = entry["quantification"]
    return entry | {"quantification": q | {"note": pack()["quantification_profiles"][q["profile_id"]]["note"]}}


def compact(entry: dict, terms: dict, code: str) -> dict:
    loc = localize(entry, terms, code)
    return {"id": entry["id"], "category": entry["category"], "label_en": entry["label"], "label": loc["label"],
            "kind": entry["kind"], "description": loc["description"], "lang": code,
            "quantification_mode": entry["quantification"]["mode"]}


def _haystack(entry: dict, terms: dict) -> tuple[list[str], str]:
    row = terms.get(entry["id"], {})
    names = [a["text"] for a in entry["aliases"]] + ([row["label"]] if "label" in row else []) + list(row.get("aliases", []))
    return [x.casefold() for x in names], (row.get("description") or "").casefold()


def _codes(lang: str) -> tuple[list[str], str]:
    if lang.casefold() == "all":
        codes = locale_codes()
        return codes, ("en" if "en" in codes else codes[0])
    code = resolve_lang(lang)
    return [code], code


def categories() -> list[dict]:
    return pack()["categories"]


def category(cat_id: str, lang: str = "en", full: bool = False) -> list[dict]:
    if cat_id not in {c["id"] for c in categories()}:
        raise ValueError(f"Unknown category: {cat_id}")
    _, code = _codes(lang)
    terms = locale(code)
    rows = [e for e in pack()["entries"] if e["category"] == cat_id]
    return [expand(e) | {"localized": localize(e, terms, code)} for e in rows] if full else [compact(e, terms, code) for e in rows]


def get(term_id: str, lang: str = "en", full: bool = True) -> dict:
    if term_id not in index():
        raise ValueError(f"Unknown term id: {term_id}")
    _, code = _codes(lang)
    entry = index()[term_id]
    if not full:
        return compact(entry, locale(code), code)
    return expand(entry) | {"localized": localize(entry, locale(code), code)}


def translations(term_id: str) -> dict:
    entry = get(term_id)
    return {"id": entry["id"], "category": entry["category"], "kind": entry["kind"], "label_en": entry["label"],
            "quantification_mode": entry["quantification"]["mode"], "spec_language": "en",
            "translations": {code: localize(entry, locale(code), code) for code in locale_codes()}}


def search(query: str, lang: str = "en", category_id: str | None = None, limit: int = 12, full: bool = False) -> dict:
    """Score 100 for an exact alias or id, 50 for a partial alias, 10 for a description hit."""
    if not 1 <= limit <= 500:
        raise ValueError("limit must be between 1 and 500")
    text = query.casefold().strip()
    if not text:
        raise ValueError("Search text must not be empty")
    codes, default = _codes(lang)
    loaded = {code: locale(code) for code in codes}
    scored = []
    for e in pack()["entries"]:
        if category_id and e["category"] != category_id:
            continue
        best, hit = 0, default
        for code in codes:
            names, desc = _haystack(e, loaded[code])
            score = 100 if text in names or text == e["id"] else 50 if any(text in x for x in names) else 10 if text in desc else 0
            if score > best:
                best, hit = score, code
        if best:
            scored.append((best, e["id"], e, hit))
    scored.sort(key=lambda row: (-row[0], row[1]))
    chosen = scored[:limit]
    rows = [expand(e) | {"localized": localize(e, loaded[hit], hit)} for _, _, e, hit in chosen] if full else \
           [compact(e, loaded[hit], hit) for _, _, e, hit in chosen]
    return {"query": query, "lang": lang, "match_count": len(scored), "returned": len(chosen), "entries": rows}


def scalar_change(baseline: float, operation: str, value: float) -> float:
    """Illustrative numeric semantics; never reads or changes an asset."""
    if not all(isinstance(n, (int, float)) and not isinstance(n, bool) and math.isfinite(n) for n in (baseline, value)):
        raise ValueError("Finite numbers required")
    if operation == "set":
        return value
    if operation == "add_delta":
        return baseline + value
    if operation == "multiply":
        return baseline * value
    if operation == "relative_delta":
        return baseline * (1 + value / 100)
    if operation == "percentage_point_delta":
        return baseline + value / 100
    raise ValueError(f"Unsupported scalar operation: {operation}")


def _obj(value: Any, label: str, errors: list[str]) -> dict:
    """Host input is arbitrary JSON: a wrong-shaped field is a lint error, never a traceback."""
    if value is None or isinstance(value, dict):
        return value or {}
    errors.append(f"{label} must be an object")
    return {}


def lint_instruction(request: dict[str, Any]) -> list[str]:
    """Representative semantic checks on an instruction.v2 document. Passing is not permission to execute."""
    if not isinstance(request, dict):
        return ["instruction must be a JSON object"]

    p = pack()
    idx = index()
    errors: list[str] = []
    context = _obj(request.get("context"), "context", errors)
    applied = request.get("status") == "applied"
    changes = request.get("changes", [])
    if not isinstance(changes, list):
        return errors + ["changes must be an array of change objects"]

    for i, change in enumerate(changes):
        prefix = f"changes[{i}]"
        if not isinstance(change, dict):
            errors.append(f"{prefix}: must be an object")
            continue
        tid = change.get("term_id")
        if tid not in idx:
            errors.append(f"{prefix}: unknown term_id {tid!r}")
            continue
        q = idx[tid]["quantification"]
        op = change.get("operation")
        if op not in p["operation_registry"]:
            errors.append(f"{prefix}: unknown operation {op!r}")
            continue
        if op not in q["allowed_operations"]:
            errors.append(f"{prefix}: operation {op!r} not allowed by this term profile")
        basis = change.get("magnitude_basis")
        if applied and basis == "llm":
            errors.append(f"{prefix}: a model-invented magnitude must not reach an applied instruction")
        quantity = _obj(change.get("quantity"), f"{prefix}: quantity", errors)
        if quantity and basis in (None, "none"):
            errors.append(f"{prefix}: a quantity requires a magnitude_basis")
        if op in DELTA_OPS and not context.get("baseline_ref"):
            errors.append(f"{prefix}: fixed baseline_ref required")
        if q["mode"] in ("proxy_only", "qualitative", "undefined") and op in DIRECT_OPS:
            errors.append(f"{prefix}: perceptual term is not a direct numeric property")
        if op == "define_metric" and not change.get("metric"):
            errors.append(f"{prefix}: explicit metric definition required")
        if quantity:
            unit = quantity.get("unit")
            if unit not in p["unit_registry"]:
                errors.append(f"{prefix}: unknown or ambiguous unit {unit!r}")
            elif op not in UNIT_FOR_OP and unit not in q["allowed_units"]:
                errors.append(f"{prefix}: unit {unit!r} is not admitted by profile {q['profile_id']}")
            expected = UNIT_FOR_OP.get(op)
            if expected and unit != expected:
                errors.append(f"{prefix}: {op} requires {expected}")
            if unit in ("px", "px2", "texel"):
                if not context.get("image_ref", context.get("grid_ref")) or not context.get("resolution"):
                    errors.append(f"{prefix}: named image/grid and resolution required")
            if unit == "svg_user_unit" and "viewBox" not in context:
                errors.append(f"{prefix}: SVG viewBox required")
            if unit == "frame":
                tb = _obj(context.get("timebase"), f"{prefix}: context.timebase", errors)
                fps = tb.get("fps")
                if not isinstance(fps, (int, float)) or isinstance(fps, bool) or fps <= 0 or not tb.get("clock"):
                    errors.append(f"{prefix}: positive timebase.fps and clock required")
            val = quantity.get("value")
            values = val if isinstance(val, list) else [val]
            if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
                errors.append(f"{prefix}: quantity must contain finite numbers")
        if tid == "camera.fov" and op == "set":
            if context.get("fov_axis") not in ("vertical", "horizontal", "diagonal"):
                errors.append(f"{prefix}: FOV axis required")
            if context.get("projection") != "perspective":
                errors.append(f"{prefix}: FOV request requires explicit perspective projection")
        if tid in MATERIAL_SCALARS and op in DIRECT_OPS and not context.get("shader_model"):
            errors.append(f"{prefix}: shader_model required")
        if op == "set_sequence":
            seq = change.get("sequence", [])
            if not seq or len(seq) != len(set(seq)):
                errors.append(f"{prefix}: nonempty unique ordered stage list required")
    ex = _obj(request.get("execution"), "execution", errors)
    if ex.get("authorized") and not (ex.get("adapter") and ex.get("binding_resolved")):
        errors.append("execution: authorization requires a bound adapter and a resolved binding")
    if applied and not ex.get("run_ref"):
        errors.append("execution: an applied instruction must carry a run_ref")
    return errors


def langs() -> list[dict]:
    keys = ("locale", "language_label_en", "language_label_native", "covers", "term_count", "translation_basis")
    base = {"locale": "en", "language_label_en": "English", "language_label_native": "English", "covers": ["en"],
            "term_count": len(index()), "translation_basis": "base_bundle_is_the_spec"}
    return [base] + [{k: v for k, v in _load(DATA / "locales" / f"{code}.json").items() if k in keys}
                     for code in locale_codes() if code != "en"]
