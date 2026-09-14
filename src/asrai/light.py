"""Light ledger: where each subject's shading points, which proposed emitter it agrees with, the
atomic questions that follow (surfaces.v1), and an overlay that shows all of it.

Everything is 2-D and in image coordinates (x right, y down): a vector [-0.7, -0.7] points to the
upper-left. Two estimates per subject:

- bright side: centroid of the subject's top-decile luminance minus the subject centroid. Reads
  flat and cel shading, where a Lambertian fit does not.
- contour fit: Johnson & Farid (2005). Along the occluding contour the surface normal lies in the
  image plane, so luminance against the contour normal is a linear least squares for the light
  direction, and r2 says whether the surface shades like a Lambertian form at all. Alpha masks
  only: a bounding box has no contour of its own.

Emitters are proposed from luminance alone: the brightest things in the image, which is what a
light source is and what bright paint under one also is. They stay `proposed` until an observer
confirms them. Inputs are never written; the only output is the overlay under out/.
"""
from __future__ import annotations

import functools
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import measure, vocab
from .measure import SILHOUETTE_ALPHA, _r

SCHEMA = "light_ledger.v1"
SURFACES = vocab.DATA / "surfaces.v1.json"
LABEL_LONG_SIDE = 256       # emitter blobs are labelled on a downscaled mask (pure-python flood fill)
EMITTER_MIN_Y = 0.30        # linear luminance floor (sRGB ~0.58): a dark scene must not promote mid-tones
EMITTER_PERCENTILE = 99     # ... and a candidate is at least EMITTER_FRACTION as bright as the image's
EMITTER_FRACTION = 0.6      # brightest percent, so a second, dimmer source is still proposed
EMITTER_MIN_AREA = 4        # labelled pixels; smaller is a stray highlight
EMITTERS_MAX = 8            # brightest first, ids e1..e8
SUBJECTS_MAX = 16
BRIGHT_PERCENTILE = 90      # the bright side is the top decile of a subject's luminance
HIGHLIGHT_PERCENTILE = 98
MIN_PIXELS = 16             # fewer shaded pixels than this and a subject has no direction
CONTOUR_MIN = 16            # contour samples needed for a least-squares direction
EMITTER_COLOR, SUBJECT_COLOR = (255, 0, 255), (255, 255, 255)
BRIGHT_COLOR, FIT_COLOR = (255, 220, 0), (0, 255, 255)


@functools.cache
def surfaces() -> dict:
    return json.loads(SURFACES.read_text("utf-8"))


def _unit(v) -> list[float]:
    v = np.asarray(v, dtype=np.float64)
    n = float(np.linalg.norm(v))
    return [0.0, 0.0] if n < 1e-9 else [round(float(v[0] / n), 3), round(float(v[1] / n), 3)]


def _hex(rgb01) -> str:
    return "#%02x%02x%02x" % tuple(int(round(float(c) * 255)) for c in rgb01)


def _hue(rgb01) -> float | None:
    h = measure.hsl(np.asarray(rgb01, dtype=np.float64).reshape(1, 3))[0][0]
    return None if np.isnan(h) else float(h)


def _erode(mask: np.ndarray) -> np.ndarray:
    p = np.pad(mask, 1, constant_values=False)
    return mask & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]


def _label(mask: np.ndarray) -> np.ndarray:
    """4-connected labels, 0 is background. Pure python: callers keep the mask small."""
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


def _emitters(rgb: np.ndarray, Y: np.ndarray, opaque: np.ndarray) -> tuple[list[dict], np.ndarray]:
    """The brightest blobs, brightest first, with the native mask they cover."""
    H, W = Y.shape
    if not opaque.any():
        return [], np.zeros((H, W), dtype=bool)
    floor = max(EMITTER_MIN_Y, EMITTER_FRACTION * float(np.percentile(Y[opaque], EMITTER_PERCENTILE)))
    emit = opaque & (Y >= floor)
    scale = min(1.0, LABEL_LONG_SIDE / max(H, W))
    small = emit
    if scale < 1:
        size = (max(1, round(W * scale)), max(1, round(H * scale)))
        small = np.asarray(Image.fromarray(emit.astype(np.uint8) * 255, "L").resize(size, Image.Resampling.BOX)) >= 128
    labels = _label(small)
    sh, sw = small.shape
    up = labels[np.minimum(np.arange(H) * sh // H, sh - 1)][:, np.minimum(np.arange(W) * sw // W, sw - 1)]
    blobs = []
    for k in range(1, int(labels.max()) + 1):
        if int((labels == k).sum()) < EMITTER_MIN_AREA:
            continue
        native = (up == k) & emit
        if native.any():
            blobs.append((float(Y[native].mean()), int(native.sum()), k, native))
    blobs.sort(key=lambda t: (-t[0], -t[1], t[2]))
    rows, keep = [], np.zeros_like(emit)
    for i, (_, area, _, native) in enumerate(blobs[:EMITTERS_MAX], 1):
        keep |= native
        ys, xs = np.nonzero(native)
        rows.append({"id": f"e{i}", "kind": "proposed",
                     "bbox": [int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)],
                     "centroid": [_r(xs.mean()), _r(ys.mean())], "area_ratio": _r(area / (H * W)),
                     "rgb": _hex(rgb[native].mean(0)), "luminance": _r(Y[native].mean())})
    return rows, keep


def _box(value) -> list[int] | None:
    if not isinstance(value, list) or len(value) != 4:
        return None
    out = []
    for v in value:
        if isinstance(v, bool) or not isinstance(v, (int, float)) or v < 0 or float(v) != int(v):
            return None
        out.append(int(v))
    return out


def _subjects(subjects, capture, W: int, H: int) -> list[dict]:
    """Model-supplied boxes, or the capture contract's screen boxes. Clipped to the image, ids unique."""
    if subjects is None and capture:
        doc = json.loads(Path(capture).read_text("utf-8"))
        rows = doc.get("composed_of") if isinstance(doc, dict) else None
        if not isinstance(rows, list):
            raise ValueError("capture must be a capture.json with a composed_of list")
        found, seen = [], {}
        for c in rows:
            box = _box(c.get("screen_bbox")) if isinstance(c, dict) else None
            if box is None:
                continue
            sid = str(c.get("game_object") or c.get("sprite") or str(c.get("asset_sha256", ""))[:12] or "subject")
            seen[sid] = seen.get(sid, 0) + 1
            found.append({"id": sid if seen[sid] == 1 else f"{sid}_{seen[sid]}", "bbox": box})
        subjects = sorted(found, key=lambda s: -(s["bbox"][2] * s["bbox"][3]))[:SUBJECTS_MAX]
    if not subjects:
        return []
    if not isinstance(subjects, list) or len(subjects) > SUBJECTS_MAX:
        raise ValueError(f"subjects must be a list of at most {SUBJECTS_MAX} {{id, bbox}} objects")
    out, seen = [], set()
    for i, s in enumerate(subjects):
        box = _box(s.get("bbox")) if isinstance(s, dict) else None
        if box is None:
            raise ValueError(f"subjects[{i}] must be {{id, bbox: [x, y, w, h]}} with whole pixels of the image")
        sid = str(s.get("id") or f"s{i + 1}")
        if sid in seen:
            raise ValueError(f"duplicate subject id {sid!r}")
        seen.add(sid)
        x, y, w, h = box
        x0, y0, x1, y1 = min(x, W), min(y, H), min(x + w, W), min(y + h, H)
        if x1 - x0 < 1 or y1 - y0 < 1:
            raise ValueError(f"subjects[{i}] {sid!r} lies outside the {W}x{H} image")
        out.append({"id": sid, "bbox": [x0, y0, x1 - x0, y1 - y0]})
    return out


def _contour_fit(mask: np.ndarray, Y: np.ndarray) -> dict | None:
    """Johnson & Farid 2005: I = rho * (N . L) + ambient is linear in (Lx, Ly, ambient) along the
    occluding contour, where N is the contour normal. Sampled two pixels in, past the anti-aliased edge."""
    blur = np.asarray(Image.fromarray(mask.astype(np.uint8) * 255, "L").filter(ImageFilter.BoxBlur(2)),
                      dtype=np.float64) / 255
    gy, gx = np.gradient(blur)
    e1 = _erode(mask)
    ring = e1 & ~_erode(e1)
    n = np.stack([-gx[ring], -gy[ring]], 1)      # outward: the mask falls off outward
    norm = np.linalg.norm(n, axis=1)
    ok = norm > 1e-6
    if int(ok.sum()) < CONTOUR_MIN:
        return None
    n = n[ok] / norm[ok, None]
    I = Y[ring][ok]
    A = np.column_stack([n, np.ones(len(n))])
    coef, *_ = np.linalg.lstsq(A, I, rcond=None)
    ss = float(((I - I.mean()) ** 2).sum())
    r2 = 1 - float(((I - A @ coef) ** 2).sum()) / ss if ss > 1e-12 else 0.0
    return {"vector": _unit(coef[:2]), "r2": _r(max(0.0, r2))}


def _subject(sub: dict, rgba: np.ndarray, Y: np.ndarray, alpha: bool, emit: np.ndarray) -> dict:
    x, y, w, h = sub["bbox"]
    a = rgba[y:y + h, x:x + w, 3]
    silhouette = alpha and bool((a < SILHOUETTE_ALPHA).any())
    body = (a >= SILHOUETTE_ALPHA) if silhouette else np.ones((h, w), dtype=bool)
    shade = body & ~emit[y:y + h, x:x + w]
    row = {"id": sub["id"], "bbox": sub["bbox"], "mask": "alpha" if silhouette else "bbox",
           "pixels": int(shade.sum()), "centroid": None, "bright_side": None, "contour_fit": None, "highlight": None}
    if row["pixels"] < MIN_PIXELS:
        return row
    ys, xs = np.nonzero(shade)
    cx, cy = xs.mean() + x, ys.mean() + y
    row["centroid"] = [_r(cx), _r(cy)]
    Ys = Y[y:y + h, x:x + w]
    v = Ys[shade]
    top = shade & (Ys >= np.percentile(v, BRIGHT_PERCENTILE))
    ty, tx = np.nonzero(top)
    d = np.array([tx.mean() + x - cx, ty.mean() + y - cy])
    radius = np.sqrt(row["pixels"] / np.pi)
    row["bright_side"] = {"vector": _unit(d), "strength": _r(min(1.0, float(np.linalg.norm(d)) / radius))}
    hi = shade & (Ys >= np.percentile(v, HIGHLIGHT_PERCENTILE))
    hy, hx = np.nonzero(hi)
    rgb = rgba[y:y + h, x:x + w, :3].astype(np.float64)[hi].mean(0) / 255
    row["highlight"] = {"centroid": [_r(hx.mean() + x), _r(hy.mean() + y)], "rgb": _hex(rgb), "luminance": _r(Ys[hi].mean())}
    if silhouette:
        row["contour_fit"] = _contour_fit(body, Ys)
    return row


def _agreement(subjects: list[dict], emitters: list[dict]) -> list[dict]:
    rows = []
    for s in subjects:
        if not s["bright_side"]:
            continue
        bs, c = np.array(s["bright_side"]["vector"]), np.array(s["centroid"])
        hh = _hue(tuple(int(s["highlight"]["rgb"][i:i + 2], 16) / 255 for i in (1, 3, 5)))
        for e in emitters:
            d = np.array(e["centroid"]) - c
            if np.linalg.norm(d) < 1e-9:
                continue
            expected = d / np.linalg.norm(d)
            angle = None if not np.linalg.norm(bs) else _r(np.degrees(np.arccos(np.clip(bs @ expected, -1, 1))))
            eh = _hue(tuple(int(e["rgb"][i:i + 2], 16) / 255 for i in (1, 3, 5)))
            delta = None if hh is None or eh is None else _r(abs((hh - eh + 180) % 360 - 180))
            rows.append({"subject": s["id"], "emitter": e["id"], "expected": _unit(d),
                         "distance_px": _r(np.linalg.norm(d)), "angle_deg": angle, "hue_delta_deg": delta})
    return rows


def _global(subjects: list[dict]) -> dict | None:
    vs = [(np.array(s["bright_side"]["vector"]), s["bright_side"]["strength"])
          for s in subjects if s["bright_side"] and s["bright_side"]["strength"] > 0]
    if not vs:
        return None
    R = sum(v * w for v, w in vs) / sum(w for _, w in vs)    # mean of unit vectors: |R| is 1 when all agree
    return {"key_direction": _unit(R), "alignment": _r(np.linalg.norm(R)), "subjects": len(vs)}


def _questions(subjects: list[dict], emitters: list[dict], agreement: list[dict], best: dict) -> list[dict]:
    """surfaces.v1 instantiated: per emitter, per subject, once, or per pair against the emitter the
    shading points at, the nearest emitter and the brightest one."""
    brightest = emitters[0]["id"] if emitters else None
    nearest: dict[str, tuple[str, float]] = {}
    for a in agreement:
        if a["subject"] not in nearest or a["distance_px"] < nearest[a["subject"]][1]:
            nearest[a["subject"]] = (a["emitter"], a["distance_px"])
    qs = []
    for s in surfaces()["surfaces"]:
        base = {"surface": s["id"], "term_id": s["terms"][0]}
        if s["scope"] == "global":
            qs.append(base | {"question": s["question"]})
        elif s["scope"] == "emitter":
            qs += [base | {"emitter": e["id"], "question": s["question"].format(emitter=e["id"])} for e in emitters]
        elif s["scope"] == "subject":
            qs += [base | {"subject": t["id"], "region": t["bbox"], "question": s["question"].format(subject=t["id"])}
                   for t in subjects]
        else:
            for t in subjects:
                if not t["bright_side"]:
                    continue
                cands = []
                for e in ((best.get(t["id"]) or (None,))[0], (nearest.get(t["id"]) or (None,))[0], brightest):
                    if e and e not in cands:
                        cands.append(e)
                qs += [base | {"subject": t["id"], "region": t["bbox"], "emitter": e,
                               "question": s["question"].format(subject=t["id"], emitter=e)} for e in cands]
    return qs


def _arrow(d: ImageDraw.ImageDraw, start, vec, length: float, color, lw: int) -> tuple[float, float]:
    x0, y0 = start
    dx, dy = vec
    x1, y1 = x0 + dx * length, y0 + dy * length
    d.line([(x0, y0), (x1, y1)], fill=color, width=lw)
    for s in (1, -1):                                  # head: two strokes swept back from the tip
        ang = np.arctan2(dy, dx) + s * np.radians(150)
        d.line([(x1, y1), (x1 + np.cos(ang) * length * 0.3, y1 + np.sin(ang) * length * 0.3)], fill=color, width=lw)
    return x1, y1


def _overlay(rgba: np.ndarray, emitters: list[dict], subjects: list[dict], best: dict, path: Path) -> None:
    img = Image.fromarray(rgba, "RGBA")
    img = Image.alpha_composite(Image.new("RGBA", img.size, (64, 64, 64, 255)), img).convert("RGB")
    d = ImageDraw.Draw(img)
    long = max(img.size)
    lw = max(1, round(long / 600))
    font = ImageFont.load_default(size=max(10, long // 70))

    def label(xy, text, color):
        d.text(xy, text, fill=color, font=font, stroke_width=lw, stroke_fill=(0, 0, 0))

    for e in emitters:
        x, y, w, h = e["bbox"]
        d.rectangle([x, y, x + w - 1, y + h - 1], outline=EMITTER_COLOR, width=lw)
        label((x, max(0, y - font.size - 2)), e["id"], EMITTER_COLOR)
    for s in subjects:
        x, y, w, h = s["bbox"]
        d.rectangle([x, y, x + w - 1, y + h - 1], outline=SUBJECT_COLOR, width=lw)
        label((x + lw + 1, y + lw + 1), s["id"], SUBJECT_COLOR)
        if not s["bright_side"]:
            continue
        length = max(3 * font.size, 0.6 * np.sqrt(s["pixels"] / np.pi))
        tip = _arrow(d, s["centroid"], s["bright_side"]["vector"], length, BRIGHT_COLOR, lw)
        if s["contour_fit"]:
            _arrow(d, s["centroid"], s["contour_fit"]["vector"], 0.8 * length, FIT_COLOR, lw)
        if s["id"] in best:
            label(tip, f"{best[s['id']][0]} {best[s['id']][1]:.0f}°", BRIGHT_COLOR)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def ledger(path: Path, subjects: list[dict] | None = None, capture: str | None = None,
           out_dir: Path | None = None, mirror: bool = False) -> dict:
    """Emitters, per-subject shading direction, agreement angles, instantiated questions, overlay path."""
    path = Path(path)
    rgba, meta = measure.load(path)
    alpha = meta["alpha_present"]
    H, W = rgba.shape[:2]
    subs = _subjects(subjects, capture, W, H)
    if mirror:
        rgba = np.ascontiguousarray(rgba[:, ::-1])
        subs = [{"id": s["id"], "bbox": [W - s["bbox"][0] - s["bbox"][2], *s["bbox"][1:]]} for s in subs]
    opaque = rgba[..., 3] > 0 if alpha else np.ones((H, W), dtype=bool)
    rgb = rgba[..., :3].astype(np.float64) / 255.0
    Y = measure.luminance(rgb)
    emitters, emit = _emitters(rgb, Y, opaque)
    rows = [_subject(s, rgba, Y, alpha, emit) for s in subs]
    agreement = _agreement(rows, emitters)
    best: dict[str, tuple[str, float]] = {}
    for a in agreement:
        if a["angle_deg"] is not None and (a["subject"] not in best or a["angle_deg"] < best[a["subject"]][1]):
            best[a["subject"]] = (a["emitter"], a["angle_deg"])
    out = {"schema_version": SCHEMA, "path": str(path), "sha256": meta["sha256"], "width": W, "height": H,
           "mirrored": bool(mirror), "coordinates": "image pixels, x right, y down; vectors are [dx, dy]",
           "emitters": emitters, "subjects": rows, "agreement": agreement, "global": _global(rows),
           "questions": _questions(rows, emitters, agreement, best), "overlay": None}
    if out_dir is not None:
        tag = hashlib.sha256(json.dumps([s["bbox"] for s in subs]).encode()).hexdigest()[:6]
        file = Path(out_dir) / meta["sha256"][:12] / f"light_ledger.{tag}{'.mirror' if mirror else ''}.png"
        _overlay(rgba, emitters, rows, best, file)
        out["overlay"] = str(file)
    return out
