"""MCP transport: the same core as the CLI, exposed as tools over stdio."""
from __future__ import annotations

import functools
import inspect
from pathlib import Path

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

from . import config, doctor as doctor_mod, measure as measure_mod, profile as profile_mod, records, run as run_mod, vocab

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
    run.__doc__ = inspect.cleandoc(fn.__doc__ or "")   # the docstring is the description: indentation is not sent
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
    """Look up one term by exact id ("shape.silhouette"), or browse: lookup="categories" lists every category and
    "category:<id>" ("category:vector") lists one. full=false returns id, label, kind and description only."""
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
                 answers: dict | None = None, profile: str | None = None) -> dict:
    """Lighting pass, two phases. Without answers: proposed emitters, each subject's shading direction, a key-light
    fit, an overlay PNG under out/ with every id drawn on it, and `form`, the typed answer sheet. With the filled
    form as answers: `verdict` and a `record`, null when nothing was observed; an unfilled form
    returns what the measurement alone decides.
    subjects: at most 16 of {"id", "bbox": [x, y, w, h] px, "depth"?: layer index, "mask"?: alpha image}; or
    capture: a capture.json; or neither, for a sprite with alpha. mirror=true measures the mirrored image.
    profile: untrained | artist | art_director also says the verdict for that reader under `sentences`.
    SKILL.md carries the rest."""
    cfg = config.load()
    # the overlay is read here, not in the run: a renderer that knew about team directories would
    # be a renderer that could be asked to decide something
    seen = profile_mod.overlay(config.team_dir(cfg))["scopes"] if profile else None
    return run_mod.ledger(Path(path), subjects, capture, Path(cfg["_root"]) / cfg["paths"]["out"],
                          mirror, answers, cfg["observer"], profile, seen)


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
