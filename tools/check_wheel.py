#!/usr/bin/env python3
"""Build a hash-locked install bundle and exercise its installed CLI and MCP away from the checkout.

The export is a release artifact derived from uv.lock, never a second maintained lockfile.
An existing output directory is refused so a checked bundle cannot be silently replaced.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent


def installed_check() -> dict:
    """Catch missing wheel data, an editable source leak, or a transport that cannot serve real calls."""
    import asrai
    from asrai import config, doctor, vocab
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from PIL import Image, features

    assert Path(asrai.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()), asrai.__file__
    executable = Path(sys.executable).parent / ("asrai.exe" if os.name == "nt" else "asrai")
    with tempfile.TemporaryDirectory(prefix="asrai-user-") as directory:
        work = Path(directory)
        env = dict(os.environ, ASRAI_ROOT=str(work))
        env.pop("PYTHONPATH", None)

        def cli(*args: str) -> str:
            return subprocess.check_output([str(executable), *args], cwd=work, env=env,
                                           text=True, encoding="utf-8", timeout=30)

        skill = Path(cli("skill-path").strip())
        assert skill.resolve().is_relative_to(Path(sys.prefix).resolve()) and skill.is_file(), skill
        assert "## Judgment protocol" in skill.read_text("utf-8"), skill
        manifest = json.loads((vocab.DATA / "manifest.sha256.json").read_text("utf-8"))
        for name, digest in manifest["files"].items():
            assert hashlib.sha256((vocab.DATA / name).read_bytes()).hexdigest() == digest, name
        for code in vocab.locale_codes():
            vocab.locale(code)
        term = json.loads(cli("vocab", "get", "shape.silhouette", "--no-full"))
        assert term["id"] == "shape.silhouette", term

        asset = work / "sprite.png"
        Image.new("RGBA", (8, 8), (255, 0, 0, 255)).save(asset)
        before = asset.read_bytes()
        measured = json.loads(cli("measure", str(asset)))
        assert measured["sha256"] == hashlib.sha256(before).hexdigest(), measured

        async def mcp_check() -> None:
            params = StdioServerParameters(command=str(executable), args=["mcp"], cwd=work,
                                           env={"ASRAI_ROOT": str(work)})
            async with stdio_client(params) as (reader, writer):
                async with ClientSession(reader, writer, read_timeout_seconds=30) as session:
                    await session.initialize()
                    names = {tool.name for tool in (await session.list_tools()).tools}
                    assert names == {"vocab_search", "vocab_get", "measure", "light_ledger",
                                     "record", "lint", "doctor"}, names
                    result = await session.call_tool("measure", {"path": str(asset)})
                    assert not result.is_error, result
                    payload = json.loads(next(c.text for c in result.content if c.type == "text"))
                    assert payload == measured, payload

        asyncio.run(asyncio.wait_for(mcp_check(), timeout=45))
        assert asset.read_bytes() == before, "installed commands modified their input"
        return {"environment": doctor.snapshot(config.load(work)),
                "codecs": {"jpeg": features.version_codec("jpg"),
                           "libjpeg_turbo": features.version_feature("libjpeg_turbo")}}


def build_bundle(out: Path) -> None:
    if out.exists():
        raise FileExistsError(f"{out} already exists; choose a new --out directory")
    with tempfile.TemporaryDirectory(prefix="asrai-wheel-") as directory:
        work = Path(directory)
        bundle = work / "bundle"
        subprocess.run(["uv", "build", "--wheel", "--out-dir", str(bundle)], cwd=ROOT, check=True)
        wheels = list(bundle.glob("*.whl"))
        if len(wheels) != 1:
            raise ValueError(f"expected one built wheel, got {wheels}")
        wheel = wheels[0]
        requirements = bundle / "requirements.txt"
        subprocess.run(["uv", "export", "--locked", "--no-dev", "--no-emit-project",
                        "--no-header", "--output-file", str(requirements)], cwd=ROOT,
                       stdout=subprocess.DEVNULL, check=True)
        digest = hashlib.sha256(wheel.read_bytes()).hexdigest()
        with requirements.open("a", encoding="utf-8") as stream:
            stream.write(f"\n./{wheel.name} --hash=sha256:{digest}\n")
        (bundle / "python-version.txt").write_text(platform.python_version() + "\n", "utf-8")

        venv = work / "venv"
        subprocess.run(["uv", "venv", "--python", sys.executable, str(venv)], check=True)
        python = venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        subprocess.run(["uv", "pip", "sync", "--python", str(python), "--require-hashes",
                        "--only-binary", ":all:", "--strict", "requirements.txt"],
                       cwd=bundle, check=True)
        # -I prevents PYTHONPATH and the repository from rescuing an incomplete wheel.
        report = json.loads(subprocess.check_output(
            [str(python), "-I", str(Path(__file__).resolve()), "--installed"],
            cwd=work, text=True, encoding="utf-8", timeout=120))
        report.update({"wheel_sha256": digest,
                       "uv_lock_sha256": hashlib.sha256((ROOT / "uv.lock").read_bytes()).hexdigest(),
                       "source_revision": subprocess.check_output(
                           ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                       "source_dirty": bool(subprocess.check_output(
                           ["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()),
                       "uv": subprocess.check_output(["uv", "--version"], text=True).strip()})
        (bundle / "environment.json").write_text(json.dumps(report, indent=2) + "\n", "utf-8")
        shutil.copytree(bundle, out)
    print(f"wheel install, CLI, MCP, bundled data and input preservation passed: {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "dist" / "repro")
    parser.add_argument("--installed", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.installed:
        print(json.dumps(installed_check()))
    else:
        build_bundle(args.out.resolve())
