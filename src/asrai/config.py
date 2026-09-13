"""Runtime configuration: `asrai.toml` in the project root, overlaid on defaults."""
from __future__ import annotations

import os
import tomllib
from pathlib import Path

DEFAULTS: dict[str, dict] = {
    "paths": {"team": "corpus/team", "out": "out", "inbox": "in"},
    # `host`: the agent hosting the MCP server observes; its model id is recorded, not pinned.
    # `api`: asrai calls a pinned vision model itself (not implemented yet; see docs/spec.md).
    "observer": {"mode": "host", "model": "unknown", "prompt_rev": "v1"},
}


def root() -> Path:
    return Path(os.environ.get("ASRAI_ROOT", Path.cwd())).resolve()


def load(project_root: Path | None = None) -> dict:
    base = project_root or root()
    cfg = {section: dict(values) for section, values in DEFAULTS.items()}
    path = base / "asrai.toml"
    if path.exists():
        for section, values in tomllib.loads(path.read_text("utf-8")).items():
            if isinstance(values, dict):
                cfg.setdefault(section, {}).update(values)
    cfg["_root"] = str(base)
    return cfg


def team_dir(cfg: dict) -> Path:
    return Path(cfg["_root"]) / cfg["paths"]["team"]
