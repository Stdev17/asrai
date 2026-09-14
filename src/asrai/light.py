"""Light ledger: where each subject's shading points, which proposed emitter it agrees with, a key-light
fit, the typed form an observer fills, and, once filled, per-subject verdicts and an observation record.

Everything is 2-D and in image coordinates (x right, y down): a vector [-0.7, -0.7] points to the
upper-left. The image-plane direction from a subject to an emitter does not depend on depth (a 3-D line
projects to the line through the two projected points), so "which side faces the lamp" is exact without
it. Depth, when given, is an ordinal layer index (0 nearest), never a distance: it widens the falloff
distance to a light on another layer, which decides which light a subject should answer to.

Two direction estimates per subject:

- bright side: centroid of the subject's top-decile luminance minus the subject centroid. Reads flat
  and cel shading, where a Lambertian fit does not. Under 3 degrees of error on synthetic discs.
- contour fit: Johnson & Farid (2005). Along the occluding contour the surface normal lies in the
  image plane, so luminance against the contour normal is a linear least squares for the light
  direction, and r2 says whether the surface shades like a Lambertian form at all. Alpha masks only:
  a bounding box has no contour of its own. Under 8 degrees of error on synthetic discs.

A candidate emitter is also measured against its own neighbourhood: a light in a rendered frame
leaves the surfaces near it brighter than the ones farther out and pulled toward its hue, while a
bright decal pasted onto a surface leaves neither. That spill, and the count of subjects whose
shading points at the candidate, decide whether a confirmed light is one the frame answers to.

Two phases in one tool. Without `answers`: emitters are proposed (the brightest blobs; bright paint
qualifies and the observer rejects it), subjects are measured, the key light is fitted, and a form is
returned whose null fields are the only things the observer must fill. With `answers`: confirmed
emitters leave the shading, every surface the measurement can decide is decided, and per-subject
verdicts plus an observation record come back. Inputs are never written; the only output is the
overlay under out/.
"""
from __future__ import annotations

import functools
import hashlib
import json
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import measure, vocab
from .measure import SILHOUETTE_ALPHA, _r

SCHEMA = "light_ledger.v1"
ANSWERS = "light_answers.v1"
SURFACES = vocab.DATA / "surfaces.v1.json"
LABEL_LONG_SIDE = 256       # emitter blobs are labelled on a downscaled mask (pure-python flood fill)
EMITTER_MIN_Y = 0.30        # linear luminance floor (sRGB ~0.58): a dark scene must not promote mid-tones
EMITTER_PERCENTILE = 99     # ... and a candidate is at least EMITTER_FRACTION as bright as the image's
EMITTER_FRACTION = 0.6      # brightest percent, so a second, dimmer source is still proposed
EMITTER_MIN_AREA = 4        # labelled pixels; smaller is a stray highlight
EMITTER_MAX_SHARE = 0.25    # a proposed emitter covering more of a subject than this is the subject's own
                            # lit surface (a lone sprite has no lamp), so it stays in the shading
EMITTERS_MAX = 8            # brightest first, ids e1..e8
SUBJECTS_MAX = 16
BRIGHT_PERCENTILE = 90      # the bright side is the top decile of a subject's luminance
HIGHLIGHT_PERCENTILE = 98
MIN_PIXELS = 16             # fewer shaded pixels than this and a subject has no direction
CONTOUR_MIN = 16            # contour samples needed for a least-squares direction
# Agreement thresholds. Estimator noise on synthetic discs is under 3 deg (bright side) and 8 deg
# (contour fit); hand-drawn scenes hold their key to roughly 10 deg; suspicion starts near 18 deg
# (cosine 0.95). Between the two thresholds the measurement does not decide and the observer is asked.
KEY_TOLERANCE_DEG = 20
DISAGREE_DEG = 60
DEPTH_STEP = 0.25           # one layer of depth adds this fraction of the long side to the falloff distance
SHADOW_PERCENTILE = 10      # the shaded mass is the bottom decile, as the bright side is the top
SHADED_STRENGTH = 0.15      # a bright side stronger than this carries directional shading: painted-in on an
                            # engine-lit sprite, and the condition for its shaded mass to mean anything
                            # (a flat sprite measures 0; a shaded disc 0.3 to 0.65)
SPILL_NEAR = 2.0            # rings at two core radii out against rings at four to eight: a source lifts
SPILL_FAR = (4.0, 8.0)      # and tints its neighbourhood, a decal does not. Sign only, no magnitude.
SPILL_MIN_PX = 32           # either ring smaller than this (a lone sprite, a source at the border) is unmeasured
PAIR_SURFACES = ("diffuse",)                   # the only surface asked per (subject, emitter)
EMITTER_KINDS = ("lamp", "neon", "sky", "screen", "glow", "paint", "unknown")
EMITTER_RANK = {"lamp": 0, "sky": 0, "screen": 0}     # designed sources outrank decorative ones (neon, glow, proposed: 1)
POINTED_MIN_PROXY = 0.25    # a subject may answer to the emitter it points at when that one is at least this
                            # fraction as strong as its expected key; the proxy under-reads clipped lamp heads
REJECTED_KINDS = ("paint", "unknown")
MODES = ("physical", "fake_lighting", "engine_lit")
ANSWER_VALUES = ("yes", "no", "unknown")
EMITTER_COLOR, REJECTED_COLOR, SUBJECT_COLOR = (255, 0, 255), (120, 120, 120), (255, 255, 255)
BRIGHT_COLOR, FIT_COLOR, SHADOW_COLOR = (255, 220, 0), (0, 255, 255), (170, 90, 255)
SPACE = re.compile(r"\s+")


@functools.cache
def surfaces() -> dict:
    return json.loads(SURFACES.read_text("utf-8"))


def _surface(sid: str) -> dict:
    return next(s for s in surfaces()["surfaces"] if s["id"] == sid)


def _subject_surfaces() -> list[dict]:
    return [s for s in surfaces()["surfaces"] if s["scope"] == "subject"]


def _unit(v) -> list[float]:
    v = np.asarray(v, dtype=np.float64)
    n = float(np.linalg.norm(v))
    return [0.0, 0.0] if n < 1e-9 else [round(float(v[0] / n), 3), round(float(v[1] / n), 3)]


def _angle(a, b) -> float:
    return float(np.degrees(np.arccos(np.clip(np.dot(a, b), -1, 1))))


def _hex(rgb01) -> str:
    return "#%02x%02x%02x" % tuple(int(round(float(c) * 255)) for c in rgb01)


def _hue(hex_rgb: str) -> float | None:
    rgb = np.array([int(hex_rgb[i:i + 2], 16) / 255 for i in (1, 3, 5)]).reshape(1, 3)
    h = measure.hsl(rgb)[0][0]
    return None if np.isnan(h) else float(h)


def _erode(mask: np.ndarray) -> np.ndarray:
    p = np.pad(mask, 1, constant_values=False)
    return mask & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]


def _dilate(mask: np.ndarray, r: float) -> np.ndarray:
    """Grow a mask by r pixels. BoxBlur carries running sums, so a large radius costs no more."""
    if r < 1:
        return mask
    return np.asarray(Image.fromarray(mask.astype(np.uint8) * 255, "L").filter(ImageFilter.BoxBlur(int(r)))) > 0


def _spill(mask: np.ndarray, bright: np.ndarray, opaque: np.ndarray, Y: np.ndarray, rgb: np.ndarray) -> dict | None:
    """What the neighbourhood of a candidate emitter does. Rings are taken outside every bright pixel,
    so a second source next door cannot stand in for the spill. Evidence for the emissive question,
    never a verdict on its own: a lamp mounted on a dark wall beside a lit floor reads negative."""
    r = max(2.0, float(np.sqrt(int(mask.sum()) / np.pi)))
    long = float(max(Y.shape))
    ground = opaque & ~bright
    near = _dilate(mask, min(SPILL_NEAR * r, long)) & ground
    far = (_dilate(mask, min(SPILL_FAR[1] * r, long)) & ~_dilate(mask, min(SPILL_FAR[0] * r, long))) & ground
    if int(near.sum()) < SPILL_MIN_PX or int(far.sum()) < SPILL_MIN_PX:
        return None
    hue = _hue(_hex(rgb[mask].mean(0)))

    def pull(m: np.ndarray) -> float | None:
        h = measure.hsl(rgb[m])[0]
        h = h[~np.isnan(h)]
        return None if hue is None or not len(h) else float(np.mean(np.abs((h - hue + 180) % 360 - 180)))

    near_hue, far_hue = pull(near), pull(far)
    return {"luminance_gain": _r(float(Y[near].mean() - Y[far].mean())),
            "hue_pull_deg": None if near_hue is None or far_hue is None else _r(far_hue - near_hue),
            "ring_px": [int(near.sum()), int(far.sum())]}


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
    """The brightest blobs, brightest first, and a label plane: pixel value i belongs to emitter e<i>."""
    H, W = Y.shape
    if not opaque.any():
        return [], np.zeros((H, W), dtype=np.int16)
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
    rows, ids = [], np.zeros(emit.shape, dtype=np.int16)
    for i, (_, area, _, native) in enumerate(blobs[:EMITTERS_MAX], 1):
        ids[native] = i
        ys, xs = np.nonzero(native)
        rows.append({"id": f"e{i}", "kind": "proposed",
                     "bbox": [int(xs.min()), int(ys.min()), int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)],
                     "centroid": [_r(xs.mean()), _r(ys.mean())], "area_px": area, "area_ratio": _r(area / (H * W)),
                     "rgb": _hex(rgb[native].mean(0)), "luminance": _r(Y[native].mean()), "depth": None,
                     "spill": _spill(native, emit, opaque, Y, rgb), "receivers": None})
    return rows, ids


def _box(value) -> list[int] | None:
    if not isinstance(value, list) or len(value) != 4:
        return None
    out = []
    for v in value:
        if isinstance(v, bool) or not isinstance(v, (int, float)) or v < 0 or float(v) != int(v):
            return None
        out.append(int(v))
    return out


def _depth(value, where: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0 or float(value) != int(value):
        raise ValueError(f"{where}: depth is a layer index, a whole number with 0 nearest the camera")
    return int(value)


def _silhouette_subject(rgba: np.ndarray) -> list[dict] | None:
    """A lone sprite is its own subject. Without this a file handed over with no boxes and no capture
    measures nothing at all, which is the one case a first reviewer reaches for first."""
    ys, xs = np.nonzero(rgba[..., 3] >= SILHOUETTE_ALPHA)
    if not len(xs):
        return None
    return [{"id": "asset", "bbox": [int(xs.min()), int(ys.min()),
                                     int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)]}]


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
            found.append({"id": sid if seen[sid] == 1 else f"{sid}_{seen[sid]}", "bbox": box, "depth": c.get("depth")})
        subjects = sorted(found, key=lambda s: -(s["bbox"][2] * s["bbox"][3]))[:SUBJECTS_MAX]
    if not subjects:
        return []
    if not isinstance(subjects, list) or len(subjects) > SUBJECTS_MAX:
        raise ValueError(f"subjects must be a list of at most {SUBJECTS_MAX} {{id, bbox, depth?}} objects")
    out, seen = [], set()
    for i, s in enumerate(subjects):
        box = _box(s.get("bbox")) if isinstance(s, dict) else None
        if box is None:
            raise ValueError(f"subjects[{i}] must be {{id, bbox: [x, y, w, h]}} with whole pixels of the image")
        sid = SPACE.sub("_", str(s.get("id") or f"s{i + 1}").strip())
        if sid in seen:
            raise ValueError(f"duplicate subject id {sid!r}")
        seen.add(sid)
        x, y, w, h = box
        x0, y0, x1, y1 = min(x, W), min(y, H), min(x + w, W), min(y + h, H)
        if x1 - x0 < 1 or y1 - y0 < 1:
            raise ValueError(f"subjects[{i}] {sid!r} lies outside the {W}x{H} image")
        out.append({"id": sid, "bbox": [x0, y0, x1 - x0, y1 - y0], "depth": _depth(s.get("depth"), f"subjects[{i}]")})
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


def _subject(sub: dict, rgba: np.ndarray, Y: np.ndarray, alpha: bool, emit_ids: np.ndarray,
             confirmed: set[int] | None) -> dict:
    x, y, w, h = sub["bbox"]
    a = rgba[y:y + h, x:x + w, 3]
    silhouette = alpha and bool((a < SILHOUETTE_ALPHA).any())
    body = (a >= SILHOUETTE_ALPHA) if silhouette else np.ones((h, w), dtype=bool)
    ids = emit_ids[y:y + h, x:x + w] * body
    shade = body.copy()
    for k in np.unique(ids[ids > 0]):
        blob = ids == k
        # before answers: a ring on a pipe leaves, a lit cap stays; after: exactly the confirmed emitters leave
        if (k in confirmed) if confirmed is not None else (blob.sum() < EMITTER_MAX_SHARE * body.sum()):
            shade &= ~blob
    row = {"id": sub["id"], "bbox": sub["bbox"], "depth": sub["depth"], "mask": "alpha" if silhouette else "bbox",
           "pixels": int(shade.sum()), "centroid": None, "body_rgb": None, "bright_side": None, "shadow": None,
           "contour_fit": None, "highlight": None}
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
    # the shaded mass must sit opposite the lit side, whatever lights the subject: no emitter is needed,
    # so a lone sprite is judged on this alone. Form shadow and cast shadow are not separable inside one box.
    bright = np.array(row["bright_side"]["vector"])
    lo = shade & (Ys <= np.percentile(v, SHADOW_PERCENTILE))
    ly, lx = np.nonzero(lo)
    sd = np.array([lx.mean() + x - cx, ly.mean() + y - cy])
    # strength as for the bright side: a box over a uniform ground has its darkest pixels all round it,
    # so the offset is noise that normalising would turn into a confident diagonal
    if np.linalg.norm(bright) > 0 and np.linalg.norm(sd) > 0:
        row["shadow"] = {"vector": _unit(sd), "strength": _r(min(1.0, float(np.linalg.norm(sd)) / radius)),
                         "opposition_deg": _r(_angle(_unit(sd), -bright))}
    hi = shade & (Ys >= np.percentile(v, HIGHLIGHT_PERCENTILE))
    hy, hx = np.nonzero(hi)
    px = rgba[y:y + h, x:x + w, :3].astype(np.float64) / 255
    row["body_rgb"] = _hex(np.median(px[shade], axis=0))
    hue_hi, hue_body = _hue(_hex(px[hi].mean(0))), _hue(row["body_rgb"])
    # a highlight whose hue is the body's own hue carries no light colour: it is brighter paint
    shift = None if hue_hi is None or hue_body is None else _r(abs((hue_hi - hue_body + 180) % 360 - 180))
    row["highlight"] = {"centroid": [_r(hx.mean() + x), _r(hy.mean() + y)], "rgb": _hex(px[hi].mean(0)),
                        "luminance": _r(Ys[hi].mean()), "hue_shift_from_body_deg": shift}
    if silhouette:
        row["contour_fit"] = _contour_fit(body, Ys)
    return row


def _agreement(subjects: list[dict], emitters: list[dict], long: int) -> list[dict]:
    """One row per (subject, emitter): expected direction, distance, angle to the bright side, hue
    difference, and an irradiance proxy (luminance x area / distance^2, depth layers widening the
    distance) normalised so the emitter a subject should answer to reads 1.0."""
    rows = []
    for s in subjects:
        if not s["bright_side"]:
            continue
        bs, c = np.array(s["bright_side"]["vector"]), np.array(s["centroid"])
        hh = _hue(s["highlight"]["rgb"])
        mine = []
        for e in emitters:
            d = np.array(e["centroid"]) - c
            dist = float(np.linalg.norm(d))
            if dist < 1e-9:
                continue
            dz = None if s["depth"] is None or e["depth"] is None else abs(s["depth"] - e["depth"])
            proxy = e["luminance"] * e["area_px"] / max(dist ** 2 + ((dz or 0) * DEPTH_STEP * long) ** 2, 1.0)
            eh = _hue(e["rgb"])
            mine.append({"subject": s["id"], "emitter": e["id"], "expected": _unit(d), "distance_px": _r(dist),
                         "depth_delta": dz, "angle_deg": _r(_angle(bs, d / dist)) if np.linalg.norm(bs) else None,
                         "hue_delta_deg": None if hh is None or eh is None else _r(abs((hh - eh + 180) % 360 - 180)),
                         "irradiance_proxy": proxy})
        top = max((m["irradiance_proxy"] for m in mine), default=0.0) or 1.0
        for m in mine:
            m["irradiance_proxy"] = _r(m["irradiance_proxy"] / top)
        rows += mine
    return rows


def _expected(agreement: list[dict], sid: str, ranks: dict) -> dict | None:
    """The emitter a subject should answer to: designed sources first, then the strongest proxy."""
    mine = [a for a in agreement if a["subject"] == sid]
    return max(mine, key=lambda a: (-ranks.get(a["emitter"], 1), a["irradiance_proxy"])) if mine else None


def _ranks(emitters: list[dict]) -> dict:
    return {e["id"]: EMITTER_RANK.get(e["kind"], 1) for e in emitters}


def _pointed(agreement: list[dict], sid: str) -> dict | None:
    mine = [a for a in agreement if a["subject"] == sid and a["angle_deg"] is not None]
    return min(mine, key=lambda a: a["angle_deg"]) if mine else None


def _key_fit(subjects: list[dict], emitters: list[dict], agreement: list[dict]) -> dict | None:
    """Which single light explains the frame: one directional hypothesis (the mean bright side, an
    off-screen or stylistic key) and one point hypothesis per emitter. Residuals are per subject, in
    degrees; the best hypothesis has the lowest median."""
    vs = {s["id"]: np.array(s["bright_side"]["vector"]) for s in subjects
          if s["bright_side"] and s["bright_side"]["strength"] > 0}
    if not vs:
        return None

    def summary(res: list[float]) -> dict:
        r = np.array(res)
        return {"median_deg": _r(np.median(r)), "max_deg": _r(r.max()),
                "within_tolerance": _r((r <= KEY_TOLERANCE_DEG).mean()), "subjects": len(r)}

    hyps = []
    mean = np.mean(list(vs.values()), axis=0)
    if np.linalg.norm(mean) > 1e-9:
        d = mean / np.linalg.norm(mean)
        # one subject fits its own mean with no residual: kept for fake_lighting, never chosen as best
        hyps.append({"hypothesis": "directional", "direction": _unit(d), "degenerate": len(vs) < 2}
                    | summary([_angle(v, d) for v in vs.values()]))
    for e in emitters:
        res = [a["angle_deg"] for a in agreement if a["emitter"] == e["id"] and a["angle_deg"] is not None]
        if res:
            hyps.append({"hypothesis": e["id"], "degenerate": False} | summary(res))
    best = min(hyps, key=lambda h: (h["degenerate"], h["median_deg"], -h["within_tolerance"]))
    return {"tolerance_deg": KEY_TOLERANCE_DEG, "best": best["hypothesis"], "hypotheses": hyps}


def _form(subjects: list[dict], emitters: list[dict], agreement: list[dict]) -> tuple[dict, list[dict]]:
    """The typed answer sheet: null is what the observer fills; everything the measurement decided is
    absent. Pair questions exist only for the emitter a subject should answer to and the one it points
    at, and only in the band where the angle or hue does not decide."""
    pairs, questions = [], []
    ranks = _ranks(emitters)
    q = {s["id"]: s["question"] for s in surfaces()["surfaces"]}
    for e in emitters:
        sp = e.get("spill")
        hint = "" if not sp else (" Surfaces near it are %s than surfaces farther out (luminance_gain %+g)."
                                  % ("brighter" if sp["luminance_gain"] > 0 else "no brighter", sp["luminance_gain"]))
        questions.append({"path": f"emitters.{e['id']}", "question": q["emissive"].format(emitter=e["id"])
                          + f" Answer with one of {EMITTER_KINDS}; paint means rejected." + hint})
    for s in subjects:
        exp, pt = _expected(agreement, s["id"], ranks), _pointed(agreement, s["id"])
        if not exp:
            continue
        for a in dict.fromkeys((exp["emitter"], pt["emitter"] if pt else exp["emitter"])):
            row = next(r for r in agreement if r["subject"] == s["id"] and r["emitter"] == a)
            if row["angle_deg"] is not None and KEY_TOLERANCE_DEG < row["angle_deg"] < DISAGREE_DEG:
                pairs.append({"subject": s["id"], "emitter": a, "surface": "diffuse", "angle_deg": row["angle_deg"], "answer": None})
    for i, p in enumerate(pairs):
        questions.append({"path": f"pairs[{i}].answer", "question": q[p["surface"]].format(subject=p["subject"], emitter=p["emitter"])})
    for s in _subject_surfaces():
        extra = ""
        if s["id"] == "cast_shadow":
            open_ids = [r["id"] for r in subjects if _shadow_measured(r)
                        and KEY_TOLERANCE_DEG < r["shadow"]["opposition_deg"] < DISAGREE_DEG]
            extra = (" The shaded mass is measured against the lit side; it left %s undecided." % ", ".join(open_ids)
                     if open_ids else " The shaded mass is measured against the lit side wherever a subject"
                     " carries shading; a subject listed here overrides that.")
        questions.append({"path": f"subjects.{s['id']}", "question": "For which subjects is this false, and for which "
                          "can it not be decided? " + s["question"].replace("{subject}", "<subject>") + extra})
    questions += [{"path": "global.key", "question": q["key"] + " key_fit names the best hypothesis and its residual."},
                  {"path": "global.atmosphere", "question": q["atmosphere"]},
                  {"path": "style.mode", "question": f"One of {MODES}: physical lights, a fixed stylistic key "
                   "(lighting.fake_lighting), or sprites the engine will light (no shading may be painted in)."}]
    form = {"schema_version": ANSWERS, "style": {"mode": None}, "emitters": {e["id"]: None for e in emitters},
            "emitter_depth": {}, "pairs": pairs,
            "subjects": {s["id"]: {"no": [], "unknown": []} for s in _subject_surfaces()},
            "global": {"key": None, "atmosphere": None}}
    return form, questions


def _answers(a, emitters: list[dict], subjects: list[dict]) -> dict:
    """The filled form, checked at the trust boundary. Unfilled fields count as unknown."""
    if not isinstance(a, dict):
        raise ValueError("answers must be the form returned by light_ledger, filled in")
    style = a.get("style") or {}
    mode = style.get("mode") or "physical"
    if not isinstance(style, dict) or mode not in MODES:
        raise ValueError(f"style.mode must be one of {MODES}")
    kinds = a.get("emitters") or {}
    eids = {e["id"] for e in emitters}
    if not isinstance(kinds, dict) or any(k not in eids for k in kinds) or any(v not in EMITTER_KINDS + (None,) for v in kinds.values()):
        raise ValueError(f"emitters must map proposed emitter ids to one of {EMITTER_KINDS}")
    depth = a.get("emitter_depth") or {}
    if not isinstance(depth, dict) or any(k not in eids for k in depth):
        raise ValueError("emitter_depth must map proposed emitter ids to layer indexes")
    pairs = a.get("pairs") or []
    sids = {s["id"] for s in subjects}
    for i, p in enumerate(pairs):
        if not isinstance(p, dict) or p.get("subject") not in sids or p.get("emitter") not in eids \
                or p.get("surface") not in PAIR_SURFACES or p.get("answer") not in ANSWER_VALUES + (None,):
            raise ValueError(f"pairs[{i}] must be {{subject, emitter, surface ∈ {PAIR_SURFACES}, answer ∈ {ANSWER_VALUES}}}")
    subj = a.get("subjects") or {}
    if not isinstance(subj, dict):
        raise ValueError("subjects must map a surface id to {no: [ids], unknown: [ids]}")
    for sid, lists in subj.items():
        if sid not in {s["id"] for s in _subject_surfaces()} or not isinstance(lists, dict) \
                or any(not isinstance(lists.get(k, []), list) or set(lists.get(k, [])) - sids for k in ("no", "unknown")):
            raise ValueError(f"subjects.{sid} must be {{no: [subject ids], unknown: [subject ids]}}")
    glob = a.get("global") or {}
    if not isinstance(glob, dict) or any(v not in ANSWER_VALUES + (None,) for v in glob.values()):
        raise ValueError(f"global.key and global.atmosphere must be one of {ANSWER_VALUES}")
    return {"mode": mode, "kinds": {e["id"]: kinds.get(e["id"]) for e in emitters},
            "emitter_depth": {k: _depth(v, f"emitter_depth.{k}") for k, v in depth.items()},
            "pairs": {(p["subject"], p["emitter"], p["surface"]): p.get("answer") or "unknown" for p in pairs},
            "subjects": {s["id"]: {"no": set(subj.get(s["id"], {}).get("no", [])), "unknown": set(subj.get(s["id"], {}).get("unknown", []))}
                         for s in _subject_surfaces()},
            "global": {"key": glob.get("key") or "unknown", "atmosphere": glob.get("atmosphere") or "unknown"}}


def _shadow_measured(s: dict) -> bool:
    """Both masses have to carry a direction before the angle between them says anything."""
    return bool(s["shadow"] and s["bright_side"] and min(s["bright_side"]["strength"],
                                                         s["shadow"]["strength"]) > SHADED_STRENGTH)


def _direction(angle: float | None, answer: str | None) -> tuple[str, str]:
    """(verdict, basis): the measurement decides outside the contested band, the observer inside it."""
    if angle is None:
        return "unknown", "none"
    if angle <= KEY_TOLERANCE_DEG:
        return "agrees", "measurement"
    if angle >= DISAGREE_DEG:
        return "disagrees", "measurement"
    return {"yes": "agrees", "no": "disagrees"}.get(answer or "", "unknown"), "observer"


def _emitter_verdicts(emitters: list[dict]) -> list[dict]:
    """A light the frame does not answer to: nothing points at it and nothing near it is brighter for
    it. Both tests are a sign or a count, so no invented magnitude decides a light source."""
    rows = []
    for e in emitters:
        sp, seen = e.get("spill"), e.get("receivers") or 0
        lights = seen > 0 or bool(sp and sp["luminance_gain"] > 0)
        rows.append({"id": e["id"], "kind": e["kind"], "receivers": seen, "spill": sp,
                     "verdict": "lights" if lights else "lights_nothing" if sp else "unknown"})
    return rows


def _verdict(subjects: list[dict], emitters: list[dict], agreement: list[dict], key_fit: dict | None, ans: dict) -> dict:
    mode = ans["mode"]
    ranks = _ranks(emitters)
    directional = next((h for h in (key_fit or {}).get("hypotheses", []) if h["hypothesis"] == "directional"), None)
    rows = []
    for s in subjects:
        v = {"id": s["id"], "mode": mode, "expected_key": None, "pointed_at": None, "verdict_emitter": None,
             "residual_deg": None, "diffuse": "unknown", "basis": "none", "specular": "unknown", "light_color": "unknown",
             "axis": None}
        for surf in _subject_surfaces():
            lists = ans["subjects"][surf["id"]]
            v[surf["id"]] = "no" if s["id"] in lists["no"] else "unknown" if s["id"] in lists["unknown"] else "yes"
        if not s["bright_side"]:
            rows.append(v | {"axis": "unknown"})
            continue
        measured = _shadow_measured(s)
        v["shadow_opposition_deg"] = s["shadow"]["opposition_deg"] if measured else None
        listed = s["id"] in ans["subjects"]["cast_shadow"]["no"] | ans["subjects"]["cast_shadow"]["unknown"]
        if not listed and mode != "engine_lit":
            # this surface is the one the measurement owns, so silence here is not the usual yes: a
            # subject too flat to place its shaded mass, and unlisted, is undecided rather than fine
            decided, basis = _direction(s["shadow"]["opposition_deg"] if measured else None, None)
            v["cast_shadow"] = {"agrees": "yes", "disagrees": "no"}.get(decided, "unknown")
            v["shadow_basis"] = basis if measured else "none"
        exp, pt = _expected(agreement, s["id"], ranks), _pointed(agreement, s["id"])
        v["pointed_at"] = pt["emitter"] if pt else None
        if mode == "engine_lit":
            baked = s["bright_side"]["strength"] > SHADED_STRENGTH
            v |= {"diffuse": "baked" if baked else "flat", "basis": "measurement", "axis": "warn" if baked else "pass"}
        elif mode == "fake_lighting":
            if directional:
                res = _angle(np.array(s["bright_side"]["vector"]), np.array(directional["direction"]))
                v["expected_key"], v["residual_deg"] = "directional", _r(res)
                v["diffuse"], v["basis"] = _direction(res, None if res >= DISAGREE_DEG or res <= KEY_TOLERANCE_DEG else "unknown")
            v["axis"] = {"agrees": "pass", "disagrees": "fail"}.get(v["diffuse"], "unknown")
        elif exp:
            target = exp
            if pt and pt["emitter"] != exp["emitter"] and ranks[pt["emitter"]] <= ranks[exp["emitter"]] \
                    and pt["irradiance_proxy"] >= POINTED_MIN_PROXY * exp["irradiance_proxy"]:
                target = pt                              # answers to a strong-enough source it faces
            v["expected_key"], v["verdict_emitter"], v["residual_deg"] = exp["emitter"], target["emitter"], target["angle_deg"]
            v["diffuse"], v["basis"] = _direction(target["angle_deg"], ans["pairs"].get((s["id"], target["emitter"], "diffuse")))
            v["color_basis"] = "observer"
            v["axis"] = {"agrees": "pass", "disagrees": "fail"}.get(v["diffuse"], "unknown")
        else:
            v["axis"] = "unknown"      # no confirmed emitter to answer to
        rows.append(v)
    axes = [r["axis"] for r in rows]
    emits = _emitter_verdicts(emitters)
    # a declared light the frame ignores is the elements disagreeing with each other, not with a brief;
    # under a declared stylistic key it is the style, so it lands on intentional_contrast instead
    dark = [e for e in emits if e["verdict"] == "lights_nothing"]
    shadows = [r for r in rows if r.get("shadow_basis") == "measurement"]
    crossed = [r["id"] for r in shadows if r["cast_shadow"] == "no"]
    fake = mode == "fake_lighting"
    cohesion = "unknown"
    if not fake:
        cohesion = ("fail" if dark or crossed else
                    "pass" if shadows or any(e["verdict"] == "lights" for e in emits) else "unknown")
    frame = {"direction_compliance": "fail" if "fail" in axes else "warn" if "warn" in axes
             else "pass" if "pass" in axes else "unknown",
             "intentional_contrast": ("pass" if directional and directional["within_tolerance"] >= 0.5
                                      and not dark and not crossed else "warn") if fake else "unknown",
             "asset_cohesion": cohesion}
    return {"mode": mode, "key": {"answer": ans["global"]["key"], "best": (key_fit or {}).get("best")},
            "atmosphere": ans["global"]["atmosphere"], "emitters": emits, "subjects": rows, "axes": frame}


def _records(verdict: dict, emitters: list[dict], subjects: list[dict], ans: dict, sha: str, capture: bool) -> dict:
    """One observation record from the verdict: measured items are asserted, observer items estimated.
    Notes cite ids (e2, pipe_left) and never a magnitude."""
    items = []
    term = {s["id"]: s["terms"][0] for s in surfaces()["surfaces"]}
    boxes = {s["id"]: s["bbox"] for s in subjects}
    dark = {e["id"] for e in verdict["emitters"] if e["verdict"] == "lights_nothing"}
    for e in emitters:
        kind = ans["kinds"].get(e["id"])
        if kind:
            items.append({"term_id": term["emissive"], "level": "estimated", "region": e["bbox"],
                          "note": f"{e['id']} is bright paint, not a source" if kind in REJECTED_KINDS
                          else f"{e['id']} reads as {kind} and nothing in the frame takes its light" if e["id"] in dark
                          else f"{e['id']} confirmed as {kind}"})
    for v in verdict["subjects"]:
        sid, box = v["id"], boxes[v["id"]]
        level = {"measurement": "asserted", "observer": "estimated"}.get(v["basis"], "unknown")
        if v["mode"] == "engine_lit" and v["diffuse"] != "unknown":
            items.append({"term_id": "lighting.fake_lighting", "level": "asserted", "region": box,
                          "note": f"{sid} carries painted directional shading that the engine will light again"
                          if v["diffuse"] == "baked" else f"{sid} is flat and leaves shading to the engine"})
        against = v.get("verdict_emitter") or v["expected_key"]
        if v["diffuse"] == "agrees":
            items.append({"term_id": term["diffuse"], "level": level, "region": box,
                          "note": f"bright side of {sid} faces {against}, its expected key" if against == v["expected_key"]
                          else f"bright side of {sid} faces {against}, a source strong enough to light it"})
        elif v["diffuse"] == "disagrees":
            items.append({"term_id": term["diffuse"], "level": level, "region": box,
                          "note": f"bright side of {sid} faces {v['pointed_at'] or 'nothing'} rather than {against}, its expected key"})
        elif v["expected_key"]:
            items.append({"term_id": term["diffuse"], "level": "unknown", "region": box,
                          "note": f"bright side of {sid} against {against} could not be decided"})
        # every subject surface is one list; only the two that judge a subject against the light it
        # answers to name that light, and silence stays silence: nothing is recorded for a plain yes
        named = {} if v["mode"] != "physical" or not against else {
            "specular": f"highlight on {sid} does not follow {against}",
            "light_color": f"lit surfaces of {sid} do not take the colour of {against}"}
        levels = {}
        if v.get("shadow_basis") == "measurement":
            named["cast_shadow"] = f"the shaded mass of {sid} does not sit opposite its lit side"
            levels["cast_shadow"] = "asserted"
        for surf in _subject_surfaces():
            if v[surf["id"]] == "no":
                items.append({"term_id": surf["terms"][0], "level": levels.get(surf["id"], "estimated"), "region": box,
                              "note": named.get(surf["id"], f"{sid}: {surf['label'].lower()} missing or inconsistent")})
            elif v[surf["id"]] == "unknown" and sid in ans["subjects"][surf["id"]]["unknown"]:
                items.append({"term_id": surf["terms"][0], "level": "unknown", "region": box, "note": f"{sid}: {surf['label'].lower()} undecided"})
    key = verdict["key"]
    if key["answer"] != "unknown":
        items.append({"term_id": term["key"], "level": "estimated", "region": "whole_image",
                      "note": f"one key light explains the frame, best hypothesis {key['best']}" if key["answer"] == "yes"
                      else f"no single light explains the frame; best hypothesis {key['best']}"})
    if verdict["atmosphere"] != "unknown":
        items.append({"term_id": term["atmosphere"], "level": "estimated", "region": "whole_image",
                      "note": "farther subjects lose contrast and saturation" if verdict["atmosphere"] == "yes"
                      else "depth does not soften contrast or saturation"})
    return {"kind": "observation", "asset_kind": "screenshot" if capture else "raster", "evidence_layer": "L2" if capture else "L1",
            "scale": "native", "asset_sha256": sha, "observer": {"mode": "host", "model": None, "prompt_rev": "v1"},
            "context": {"lighting_mode": ans["mode"]}, "observations": items}


def _arrow(d: ImageDraw.ImageDraw, start, vec, length: float, color, lw: int) -> tuple[float, float]:
    x0, y0 = start
    dx, dy = vec
    x1, y1 = x0 + dx * length, y0 + dy * length
    d.line([(x0, y0), (x1, y1)], fill=color, width=lw)
    for s in (1, -1):                                  # head: two strokes swept back from the tip
        ang = np.arctan2(dy, dx) + s * np.radians(150)
        d.line([(x1, y1), (x1 + np.cos(ang) * length * 0.3, y1 + np.sin(ang) * length * 0.3)], fill=color, width=lw)
    return x1, y1


def _overlay(rgba: np.ndarray, emitters: list[dict], subjects: list[dict], agreement: list[dict],
             key_fit: dict | None, path: Path) -> None:
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
        color = REJECTED_COLOR if e["kind"] in REJECTED_KINDS else EMITTER_COLOR
        d.rectangle([x, y, x + w - 1, y + h - 1], outline=color, width=lw)
        label((x, max(0, y - font.size - 2)), e["id"], color)
    for s in subjects:
        x, y, w, h = s["bbox"]
        d.rectangle([x, y, x + w - 1, y + h - 1], outline=SUBJECT_COLOR, width=lw)
        label((x + lw + 1, y + lw + 1), s["id"], SUBJECT_COLOR)
        if not s["bright_side"]:
            continue
        length = max(3 * font.size, 0.6 * np.sqrt(s["pixels"] / np.pi))
        tip = _arrow(d, s["centroid"], s["bright_side"]["vector"], length, BRIGHT_COLOR, lw)
        if _shadow_measured(s):            # where the shaded mass sits: it belongs opposite the yellow arrow
            _arrow(d, s["centroid"], s["shadow"]["vector"], 0.7 * length, SHADOW_COLOR, lw)
        if s["contour_fit"]:
            _arrow(d, s["centroid"], s["contour_fit"]["vector"], 0.8 * length, FIT_COLOR, lw)
        exp = _expected(agreement, s["id"], _ranks(emitters))
        if exp and exp["angle_deg"] is not None:
            label(tip, f"{exp['emitter']} {exp['angle_deg']:.0f}°", BRIGHT_COLOR)
    if key_fit:
        best = next(h for h in key_fit["hypotheses"] if h["hypothesis"] == key_fit["best"])
        label((lw + 2, lw + 2), f"key {best['hypothesis']} median {best['median_deg']:.0f}° "
              f"within {KEY_TOLERANCE_DEG}°: {best['within_tolerance']:.0%}", BRIGHT_COLOR)
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def ledger(path: Path, subjects: list[dict] | None = None, capture: str | None = None,
           out_dir: Path | None = None, mirror: bool = False, answers: dict | None = None) -> dict:
    """Phase one (no answers): emitters, per-subject direction, agreement, key fit, form, questions, overlay.
    Phase two (answers): the same over confirmed emitters, plus verdict and an observation record.
    With no subjects and no capture, a file with alpha is its own subject. Handing the form back
    unfilled is a valid phase two: it returns everything the measurement decides and nothing else."""
    path = Path(path)
    rgba, meta = measure.load(path)
    alpha = meta["alpha_present"]
    H, W = rgba.shape[:2]
    if subjects is None and not capture and alpha:
        subjects = _silhouette_subject(rgba)
    subs = _subjects(subjects, capture, W, H)
    if mirror:
        rgba = np.ascontiguousarray(rgba[:, ::-1])
        subs = [s | {"bbox": [W - s["bbox"][0] - s["bbox"][2], *s["bbox"][1:]]} for s in subs]
    opaque = rgba[..., 3] > 0 if alpha else np.ones((H, W), dtype=bool)
    rgb = rgba[..., :3].astype(np.float64) / 255.0
    Y = measure.luminance(rgb)
    emitters, emit_ids = _emitters(rgb, Y, opaque)
    ans = _answers(answers, emitters, subs) if answers is not None else None
    confirmed = None
    if ans:
        for e in emitters:
            e["kind"] = ans["kinds"][e["id"]] or "unknown"
            e["depth"] = ans["emitter_depth"].get(e["id"])
        confirmed = {i for i, e in enumerate(emitters, 1) if e["kind"] not in REJECTED_KINDS}
    rows = [_subject(s, rgba, Y, alpha, emit_ids, confirmed) for s in subs]
    live = [e for e in emitters if confirmed is None or e["kind"] not in REJECTED_KINDS]
    agreement = _agreement(rows, live, max(W, H))
    for e in live:
        e["receivers"] = sum(1 for a in agreement if a["emitter"] == e["id"]
                             and a["angle_deg"] is not None and a["angle_deg"] <= KEY_TOLERANCE_DEG)
    key_fit = _key_fit(rows, live, agreement)
    out = {"schema_version": SCHEMA, "path": str(path), "sha256": meta["sha256"], "width": W, "height": H,
           "mirrored": bool(mirror), "coordinates": "image pixels, x right, y down; vectors are [dx, dy]; depth is a layer index, 0 nearest",
           "emitters": emitters, "subjects": rows, "agreement": agreement, "key_fit": key_fit, "overlay": None}
    if ans:
        verdict = _verdict(rows, live, agreement, key_fit, ans)
        out |= {"verdict": verdict, "record": _records(verdict, emitters, rows, ans, meta["sha256"], bool(capture))}
    else:
        out["form"], out["questions"] = _form(rows, live, agreement)
    if out_dir is not None:
        tag = hashlib.sha256(json.dumps([s["bbox"] for s in subs]).encode()).hexdigest()[:6]
        file = Path(out_dir) / meta["sha256"][:12] / f"light_ledger.{tag}{'.answered' if ans else ''}{'.mirror' if mirror else ''}.png"
        _overlay(rgba, emitters, rows, agreement, key_fit, file)
        out["overlay"] = str(file)
    return out
