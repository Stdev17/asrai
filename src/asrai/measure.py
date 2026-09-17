"""Deterministic V0 measurements with Pillow and numpy. Same bytes in, same JSON out. Never writes."""
from __future__ import annotations

import hashlib
import io
from pathlib import Path

import numpy as np
from PIL import Image

SCHEMA = "measure.v1"
THUMBNAIL_LONG_SIDE = 64     # silhouette reads at icon size: the gate in spec.md 7 step 3
SILHOUETTE_ALPHA = 128       # after a box downscale edge pixels are partial; >=128 keeps the body only
CHROMA_MIN_S = 0.10          # below this HSL saturation a pixel carries no usable hue
CHROMA_MIN_L = 0.05          # near-black and near-white hue is numerically unstable: a few
CHROMA_MAX_L = 0.95          # codes of noise swing it across the wheel, so both ends are cut
PALETTE_K = 8
PALETTE_SAMPLE = 1_000_000   # deterministic stride sample above this many opaque pixels
COMPONENT_MAX = 128 * 128    # connected components only on small masks (pure-python flood fill)
# stats() peaks near 320 bytes per pixel (float64 sRGB->linear over the whole plane), so a pixel
# count is a memory budget: 12 Mpx is roughly 4 GB. A 4K capture (8.3 Mpx) fits; 8K does not.
# Both the decoded source and any target rescale are checked, because target_width is model-supplied.
# ponytail: float32 and linearising only the opaque pixels would cut this ~4x if 8K ever matters.
MAX_PIXELS = 12_000_000
COLOR_TYPES = {0: "gray", 2: "rgb", 3: "indexed", 4: "gray_alpha", 6: "rgba"}
LUMA = np.array([0.2126, 0.7152, 0.0722])   # Rec. 709 luma weights, applied to linear light
SIXTEEN_BIT = ("I;16", "I;16B", "I;16L", "I;16N", "I")


def _r(x) -> float:
    return round(float(x), 4)


def _pct(v: np.ndarray) -> dict:
    return {"p10": _r(np.percentile(v, 10)), "p50": _r(np.percentile(v, 50)),
            "p90": _r(np.percentile(v, 90)), "mean": _r(v.mean())}


def _png_header(data: bytes) -> tuple[int, int] | None:
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        return None
    return data[24], data[25]  # bit depth, colour type


def _check_size(w: int, h: int, what: str) -> None:
    if w * h > MAX_PIXELS:
        raise ValueError(f"{what} is {w}x{h} = {w * h / 1e6:.1f} Mpx; measure is bounded at "
                         f"{MAX_PIXELS // 1_000_000} Mpx. Downscale first.")


def load(path: Path) -> tuple[np.ndarray, dict]:
    data = path.read_bytes()
    try:
        img = Image.open(io.BytesIO(data))
    except Image.DecompressionBombError as exc:  # Pillow raises this off Exception, not OSError
        raise ValueError(str(exc)) from exc
    _check_size(img.width, img.height, "source image")  # header only: refuse before load() decodes
    img.load()
    hdr = _png_header(data)
    alpha_present = img.mode in ("RGBA", "LA", "PA") or "transparency" in img.info
    meta = {"format": img.format, "mode": img.mode, "width": img.width, "height": img.height,
            "bit_depth": hdr[0] if hdr else 8,
            "color_type": COLOR_TYPES.get(hdr[1], str(hdr[1])) if hdr else img.mode.lower(),
            "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
            "alpha_present": bool(alpha_present),
            # Pillow decodes 16-bit colour PNGs to 8 bits; every number below is 8-bit precision.
            "precision": "8bit"}
    if img.mode in SIXTEEN_BIT:  # convert() would clip 16-bit grey to white; rescale explicitly
        maxval = 65535 if meta["bit_depth"] == 16 else max(1, int(np.asarray(img).max()))
        gray = (np.asarray(img, dtype=np.float64) / maxval * 255).round().astype(np.uint8)
        img = Image.fromarray(gray, "L")
    return np.asarray(img.convert("RGBA"), dtype=np.uint8), meta


def _resize(rgba: np.ndarray, size: tuple[int, int], method) -> np.ndarray:
    return np.asarray(Image.fromarray(rgba, "RGBA").resize(size, method), dtype=np.uint8)


def _palette(rgb_u8: np.ndarray) -> list[dict]:
    n = len(rgb_u8)
    if n > PALETTE_SAMPLE:
        rgb_u8 = rgb_u8[:: -(-n // PALETTE_SAMPLE)]
    strip = Image.fromarray(np.ascontiguousarray(rgb_u8).reshape(1, -1, 3), "RGB")
    q = strip.quantize(colors=PALETTE_K, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    pal = q.getpalette()
    counts = q.getcolors(256) or []
    total = sum(c for c, _ in counts) or 1
    rows = sorted(((c / total, tuple(pal[3 * i:3 * i + 3])) for c, i in counts), key=lambda t: (-t[0], t[1]))
    return [{"rgb": "#%02x%02x%02x" % rgb, "share": _r(s)} for s, rgb in rows]


def _edge_density(Yf: np.ndarray, opaque: np.ndarray) -> float | None:
    gx = np.abs(np.diff(Yf, axis=1))
    ox = opaque[:, 1:] & opaque[:, :-1]
    gy = np.abs(np.diff(Yf, axis=0))
    oy = opaque[1:, :] & opaque[:-1, :]
    k = int(ox.sum() + oy.sum())
    return _r((gx[ox].sum() + gy[oy].sum()) / k) if k else None


def label(mask: np.ndarray) -> np.ndarray:
    """4-connected labels, 0 is background, components numbered 1..n in raster order.

    Pure python, so a caller keeps the mask small: COMPONENT_MAX bounds the one call here, and the
    surface pass labels a downscaled copy. Public because it is the only traversal of a mask in this
    package and a second private copy is how the two drifted apart before."""
    labels = np.zeros(mask.shape, dtype=np.int32)
    h, w = mask.shape
    n = 0
    for y0, x0 in zip(*np.nonzero(mask)):
        if labels[y0, x0]:
            continue
        n += 1
        labels[y0, x0] = n
        stack = [(int(y0), int(x0))]
        while stack:
            y, x = stack.pop()
            for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not labels[ny, nx]:
                    labels[ny, nx] = n
                    stack.append((ny, nx))
    return labels


def _components(mask: np.ndarray) -> int:
    return int(label(mask).max())          # the count is the labelling's own maximum


def _silhouette(a: np.ndarray) -> dict:
    mask = a >= SILHOUETTE_ALPHA
    h, w = mask.shape
    area = int(mask.sum())
    if area == 0:
        return {"mask_area_ratio": 0.0, "bbox": None, "bbox_fill_ratio": None, "components": 0}
    ys, xs = np.nonzero(mask)
    x0, x1, y0, y1 = int(xs.min()), int(xs.max()) + 1, int(ys.min()), int(ys.max()) + 1
    return {"mask_area_ratio": _r(area / (h * w)), "bbox": [x0, y0, x1 - x0, y1 - y0],
            "bbox_fill_ratio": _r(area / ((x1 - x0) * (y1 - y0))),
            "components": _components(mask) if mask.size <= COMPONENT_MAX else None}


def _alpha(a: np.ndarray) -> dict:
    return {"coverage": _r((a > 0).mean()), "binary": bool(np.isin(a, (0, 255)).all()),
            "partial_ratio": _r(((a > 0) & (a < 255)).mean())}


def luminance(rgb: np.ndarray) -> np.ndarray:
    """Rec. 709 luma of sRGB-encoded float RGB in [0, 1], taken on linear light."""
    # sRGB electro-optical transfer function (IEC 61966-2-1). The coefficients are the standard's
    # own and stay inline: naming each one hides the formula a reader would otherwise recognise.
    lin = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    return lin @ LUMA


def hsl(rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """HSL of float RGB in [0, 1] over the last axis. Hue is in degrees, nan where no usable hue."""
    mx, mn = rgb.max(-1), rgb.min(-1)
    d, L = mx - mn, (mx + mn) / 2
    denom = 1 - np.abs(2 * L - 1)
    S = np.where(d < 1e-9, 0.0, d / np.where(denom < 1e-9, 1.0, denom))
    dd = np.maximum(d, 1e-9)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    H = np.where(mx == r, ((g - b) / dd) % 6, np.where(mx == g, (b - r) / dd + 2, (r - g) / dd + 4)) * 60
    chroma = (S > CHROMA_MIN_S) & (L > CHROMA_MIN_L) & (L < CHROMA_MAX_L)
    return np.where(chroma, H, np.nan), S, L


def stats(rgba: np.ndarray, alpha_present: bool) -> dict:
    h, w = rgba.shape[:2]
    a = rgba[..., 3]
    opaque = (a > 0) if alpha_present else np.ones((h, w), dtype=bool)
    n = int(opaque.sum())
    out: dict = {"width": w, "height": h, "opaque_pixels": n}
    if n == 0:
        return out | {"empty": True, "silhouette": _silhouette(a) if alpha_present else None}
    rgb = rgba[..., :3].astype(np.float64) / 255.0
    Yf = luminance(rgb)
    px, Y = rgb[opaque], Yf[opaque]
    H, S, L = hsl(px)
    out["luminance"] = _pct(Y) | {"rms_contrast": _r(Y.std())}
    out["lightness"] = _pct(L)
    out["saturation"] = _pct(S)
    chroma = ~np.isnan(H)
    out["chromatic_ratio"] = _r(chroma.mean())
    if chroma.any():
        hist, _ = np.histogram(H[chroma], bins=12, range=(0, 360))
        out["hue_bins_30deg"] = [_r(x) for x in hist / hist.sum()]
    else:
        out["hue_bins_30deg"] = None
    out["palette"] = _palette(rgba[opaque][:, :3])
    out["edge_density"] = _edge_density(Yf, opaque)
    out["silhouette"] = _silhouette(a) if alpha_present else None
    return out


def measure(path: Path, target_width: int | None = None) -> dict:
    """Measurements at native scale, at `target_width` (display size) and at 64 px long side."""
    path = Path(path)
    if target_width is not None and target_width < 1:
        raise ValueError(f"target_width must be a positive pixel width, got {target_width}")
    rgba, meta = load(path)
    alpha = meta.pop("alpha_present")
    w, h = meta["width"], meta["height"]
    native = stats(rgba, alpha) | {"resample": None}
    scales = {"native": native}
    if target_width and target_width != w:
        size = (int(target_width), max(1, round(h * target_width / w)))
        _check_size(*size, "target scale")
        method = Image.Resampling.NEAREST if target_width > w else Image.Resampling.BOX
        scales["target"] = stats(_resize(rgba, size, method), alpha) | {"resample": method.name.lower(),
                                                                          "target_width": int(target_width)}
    elif target_width:
        scales["target"] = native | {"target_width": int(target_width)}
    long_side = max(w, h)
    if long_side > THUMBNAIL_LONG_SIDE:
        s = THUMBNAIL_LONG_SIDE / long_side
        size = (max(1, round(w * s)), max(1, round(h * s)))
        scales["thumbnail"] = stats(_resize(rgba, size, Image.Resampling.BOX), alpha) | {"resample": "box"}
    else:
        scales["thumbnail"] = native
    return {"schema_version": SCHEMA, "path": str(path), **meta,
            "alpha": _alpha(rgba[..., 3]) if alpha else None, "scales": scales}
