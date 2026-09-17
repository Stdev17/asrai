"""Environment report and version lock: what this machine would measure and render with."""
from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
from importlib.metadata import PackageNotFoundError, version as dist_version
from pathlib import Path

from . import __version__, config, records, vocab

TOOLS = {"imagemagick": ("ASRAI_MAGICK", "magick", ["-version"]),
         "inkscape": ("ASRAI_INKSCAPE", "inkscape", ["--version"]),
         "blender": ("ASRAI_BLENDER", "blender", ["--version"])}
LOCK = "asrai.lock.json"
PROBE_TIMEOUT_S = 30   # a --version probe that hangs this long is a broken install, not a slow one


def tool_version(env: str, default: str, args: list[str]) -> dict:
    exe = os.environ.get(env) or shutil.which(default)
    if not exe:
        return {"found": False, "version": None, "path": None}
    try:
        out = subprocess.run([exe, *args], capture_output=True, text=True, timeout=PROBE_TIMEOUT_S)
    except (OSError, subprocess.SubprocessError) as exc:
        return {"found": False, "version": None, "path": exe, "error": str(exc)}
    lines = (out.stdout or out.stderr).strip().splitlines()
    return {"found": True, "version": lines[0] if lines else "", "path": exe}


def snapshot(cfg: dict) -> dict:
    def dist(name: str) -> str | None:
        try:
            return dist_version(name)
        except PackageNotFoundError:
            return None
    return {"asrai": __version__, "python": platform.python_version(), "platform": platform.platform(),
            "packages": {n: dist(n) for n in ("pillow", "numpy", "mcp")},
            "tools": {name: tool_version(*spec) for name, spec in TOOLS.items()},
            "corpus": {"schema_version": vocab.pack()["schema_version"], "entry_count": len(vocab.index()),
                       "vocab_sha256": records.sha256_file(vocab.DATA / "vocab.v2.json")},
            "observer": cfg["observer"]}


def observed(cfg: dict) -> dict:
    """What the team's own records say about who observed them.

    `observer.model` is the host model's id. asrai cannot know it -- `observer.mode: host` means the
    agent hosting the server is the observer -- so the run signs a record with the configured default
    and `SKILL.md` asks the model to replace it with its own. A model that does not is silent about it,
    and a corpus where nobody filled it in reads exactly like one where nobody looked.

    Counting is the only thing asrai can do about that, and it is a report rather than a gate: the
    value is honest, it is just uninformative, and refusing a record over it would lose the
    observation to save the attribution. It stays out of `pinned_view` because a corpus grows and a
    lock must not drift every time somebody records something."""
    rows = [r for r in records.read(config.team_dir(cfg) / "records.jsonl") if r.get("kind") == "observation"]
    blank = [r for r in rows if str((r.get("observer") or {}).get("model", "")).strip() in ("", "unknown")]
    return {"observations": len(rows), "observer_unnamed": len(blank)}


def pinned_view(snap: dict) -> dict:
    """What a team pins. `platform` is left out: teammates on other operating systems must not drift."""
    return {"asrai": snap["asrai"], "python": snap["python"], "packages": snap["packages"],
            "tools": {k: v["version"] for k, v in snap["tools"].items()},
            "corpus": snap["corpus"], "observer": snap["observer"]}


def _diff(a: dict, b: dict, prefix: str = "") -> list[dict]:
    out = []
    for key in sorted(set(a) | set(b)):
        x, y = a.get(key), b.get(key)
        if isinstance(x, dict) and isinstance(y, dict):
            out += _diff(x, y, f"{prefix}{key}.")
        elif x != y:
            out.append({"key": f"{prefix}{key}", "locked": x, "current": y})
    return out


def run(cfg: dict, write_lock: bool = False) -> dict:
    snap = snapshot(cfg)
    view = pinned_view(snap)
    path = Path(cfg["_root"]) / LOCK
    if write_lock:
        path.write_text(json.dumps(view, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return {"status": "locked", "lock": str(path), "drift": [], "environment": snap,
                "observed": observed(cfg)}
    if not path.exists():
        return {"status": "unlocked", "lock": None, "drift": [], "environment": snap,
                "observed": observed(cfg)}
    drift = _diff(json.loads(path.read_text("utf-8")), view)
    return {"status": "drift" if drift else "match", "lock": str(path), "drift": drift,
            "environment": snap, "observed": observed(cfg)}
