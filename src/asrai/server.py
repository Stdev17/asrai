"""MCP transport: the same core as the CLI, exposed as tools over stdio."""
from __future__ import annotations

import functools
from pathlib import Path

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from . import config, doctor as doctor_mod, light, measure as measure_mod, records, vocab

INSTRUCTIONS = (
    "First-pass art direction for game assets. Order of work: vocab_search then vocab_get for exact term ids; "
    "measure before observing; record observations with qualified levels and no numbers; lint an instruction "
    "before proposing it. Direction may be observed; magnitude only comes from measurements, precedents or a human."
)
server = MCPServer("asrai", instructions=INSTRUCTIONS)
CORE_ERRORS = (OSError, ValueError, KeyError, TypeError)


def _guard(fn):
    """Core errors become tool errors the host can read, not server tracebacks."""
    @functools.wraps(fn)  # keeps the signature the MCP schema is generated from
    def run(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except CORE_ERRORS as exc:
            raise ToolError(str(exc)) from exc
    return run


@server.tool()
@_guard
def vocab_search(query: str, lang: str = "en", category: str | None = None, limit: int = 12, full: bool = False) -> dict:
    """Search the stock vocabulary by label, alias (any language) or description.
    full=true returns the whole spec per hit; the default returns id, label, kind and description only."""
    return vocab.search(query, lang, category, limit, full)


@server.tool()
@_guard
def vocab_get(lookup: str, lang: str = "en", full: bool = True) -> dict:
    """Look up one term, or browse. lookup takes an exact term id ("shape.silhouette"), the literal
    "categories" to list every category, or "category:<id>" ("category:vector") to list one category.
    full=true returns the whole spec; false returns id, label, kind and description only."""
    if lookup == "categories":
        return {"categories": vocab.categories()}
    if lookup.startswith("category:"):
        return {"entries": vocab.category(lookup.split(":", 1)[1], lang, full)}
    return vocab.get(lookup, lang, full)


@server.tool()
@_guard
def measure(path: str, target_width: int | None = None) -> dict:
    """Deterministic measurements of a raster (PNG/JPG/WebP) at native, target and 64px scales. Never modifies the file."""
    return measure_mod.measure(Path(path), target_width)


@server.tool()
@_guard
def light_ledger(path: str, subjects: list[dict] | None = None, capture: str | None = None, mirror: bool = False,
                 answers: dict | None = None) -> dict:
    """Lighting pass over a raster, in two phases. Phase one (no answers): proposed emitters, where each subject's
    shading points, a key-light fit, an overlay PNG under out/ with every id drawn on it, and `form`, the typed
    answer sheet whose null fields are all an observer decides. Phase two: pass the filled form as `answers` for
    `verdict` and an observation `record`; handing it back unfilled is valid and returns what the measurement alone
    decides. subjects: [{"id": "pipe_left", "bbox": [x, y, w, h], "depth": 0, "mask": "layers/pipe.png"}], at most
    16 — bbox in pixels; depth an optional layer index (0 nearest), never a distance; mask an optional image whose
    alpha marks the subject's pixels, canvas- or box-sized: a layer export, never a segmentation. capture: a
    capture.json whose composed_of boxes become the subjects. Vectors are [dx, dy], y down. mirror=true measures
    the mirrored image. The bundled SKILL.md carries the rest; this schema is re-sent every turn."""
    cfg = config.load()
    return light.ledger(Path(path), subjects, capture, Path(cfg["_root"]) / cfg["paths"]["out"], mirror, answers)


@server.tool()
@_guard
def record(record: dict) -> dict:
    """Append one validated record (kind: observation | pairwise | instruction) to the team log. Returns it with id."""
    cfg = config.load()
    return records.append(record, config.team_dir(cfg) / "records.jsonl")


@server.tool()
@_guard
def lint(instruction: dict) -> dict:
    """Lint an instruction.v2 document against the vocabulary. Passing is not permission to apply."""
    errors = vocab.lint_instruction(instruction)
    return {"valid": not errors, "errors": errors}


@server.tool()
@_guard
def doctor(write_lock: bool = False) -> dict:
    """Report tool, package and corpus versions, and drift against asrai.lock.json.
    write_lock=true overwrites that file with this environment instead of reporting drift."""
    return doctor_mod.run(config.load(), write_lock)


def main() -> None:
    server.run(transport="stdio")
