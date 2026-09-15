#!/usr/bin/env python3
"""Create the measure fixtures once, and regenerate their expected JSON on demand.

The images are committed bytes, not regenerated: measure records the file's sha256, so a
re-encode under a different Pillow would change every expectation for no real reason. An
existing image is left alone; delete it deliberately if it must change.

The expectations *are* derived, and rewriting them is how an intentional change to measure
is recorded. `--check` rewrites nothing and reports what drifted.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from asrai import measure

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "tests" / "fixtures"
# Each entry is one decode or scaling branch of measure; the value is its target_width, if any.
TARGET_WIDTH = {"sprite_rgba.png": 48, "screenshot_rgb.png": None, "gray16.png": None,
                "indexed_alpha.png": 32, "antialiased_rgba.png": None, "flat.jpg": 24}


def sprite_rgba() -> Image.Image:
    """Binary alpha, two colours, one connected component: the ordinary sprite case."""
    img = Image.new("RGBA", (96, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((16, 8, 80, 56), fill=(220, 40, 40, 255))
    d.rectangle((40, 40, 56, 60), fill=(40, 40, 200, 255))
    return img


def screenshot_rgb() -> Image.Image:
    """No alpha plane at all: silhouette is None and a grey ramp has no usable hue."""
    ramp = np.tile(np.linspace(0, 255, 320, dtype=np.uint8), (180, 1))
    return Image.fromarray(np.stack([ramp, ramp, ramp], -1), "RGB")


def gray16() -> Image.Image:
    """16-bit grey: convert() would clip it to white, so load() rescales explicitly."""
    return Image.fromarray(np.tile(np.linspace(0, 65535, 128, dtype=np.uint16), (32, 1)))


def indexed_alpha() -> Image.Image:
    """Palette PNG whose transparency lives in img.info, not in an alpha channel."""
    a = np.zeros((64, 64), dtype=np.uint8)
    a[8:56, 8:56] = 1
    a[20:44, 20:44] = 2
    img = Image.fromarray(a, "P")
    img.putpalette([0, 0, 0] + [30, 160, 90] + [240, 210, 60] + [0, 0, 0] * 253)
    img.info["transparency"] = 0
    return img


def antialiased_rgba() -> Image.Image:
    """Partial alpha on the edge: alpha.binary is false and partial_ratio is above zero."""
    big = Image.new("RGBA", (320, 320), (0, 0, 0, 0))
    ImageDraw.Draw(big).ellipse((16, 16, 304, 304), fill=(60, 90, 200, 255))
    return big.resize((80, 80), Image.Resampling.BOX)


def flat_jpg() -> Image.Image:
    """Not a PNG: there is no IHDR, so bit depth and colour type fall back to the mode."""
    x = np.linspace(0, 1, 64)
    rgb = np.stack([np.tile(x, (48, 1)) * 255, np.full((48, 64), 120.0), np.tile(1 - x, (48, 1)) * 255], -1)
    return Image.fromarray(rgb.astype(np.uint8), "RGB")


BUILDERS = {"sprite_rgba.png": sprite_rgba, "screenshot_rgb.png": screenshot_rgb, "gray16.png": gray16,
            "indexed_alpha.png": indexed_alpha, "antialiased_rgba.png": antialiased_rgba, "flat.jpg": flat_jpg}


def expectation(name: str) -> dict:
    """`path` is absolute and machine-specific, so the fixture stores the file name instead."""
    return measure.measure(DIR / name, TARGET_WIDTH[name]) | {"path": name}


def expectation_json(name: str) -> str:
    """Use the committed format for both fixture generation and the byte-equality gate."""
    return json.dumps(expectation(name), ensure_ascii=False, indent=2, allow_nan=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Report drift; write nothing.")
    args = parser.parse_args()
    (DIR / "expected").mkdir(parents=True, exist_ok=True)

    created, drifted = [], []
    for name, build in BUILDERS.items():
        path = DIR / name
        if not path.exists():
            build().save(path)
            created.append(name)

        want = expectation_json(name)
        target = DIR / "expected" / f"{Path(name).stem}.json"
        if target.exists() and target.read_text("utf-8") == want:
            continue
        drifted.append(name)
        if not args.check:
            target.write_text(want, encoding="utf-8")

    print(json.dumps({"fixtures": len(BUILDERS), "images_created": created,
                      "expectations_drifted" if args.check else "expectations_written": drifted}, indent=2))
    return 1 if args.check and drifted else 0


if __name__ == "__main__":
    raise SystemExit(main())
