"""Light ledger: where each subject's shading points, which proposed emitter it agrees with, a key-light
fit, the typed form an observer fills, and, once filled, per-subject verdicts and an observation record.

Everything is 2-D and in image coordinates (x right, y down): a vector [-0.7, -0.7] points to the
upper-left. The image-plane direction from a subject to an emitter does not depend on depth (a 3-D line
projects to the line through the two projected points), so "which side faces the lamp" is exact without
it. Depth, when given, is an ordinal layer index (0 nearest), never a distance: it widens the falloff
distance to a light on another layer, which decides which light a subject should answer to.

Two direction estimates per subject:

- bright side: centroid of the subject's top-decile luminance minus the subject centroid. Reads flat
  and cel shading, where a Lambertian fit does not. Under 4 degrees of error on synthetic discs.
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
import math
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
BRIGHT_PERCENTILE = 90      # the bright side is the top decile of a subject's luminance
HIGHLIGHT_PERCENTILE = 98
MIN_PIXELS = 16             # fewer shaded pixels than this and a subject has no direction
CONTOUR_MIN = 16            # contour samples needed for a least-squares direction
# Existing cutoffs are unverified implementation policy, not measured art-direction limits.
# Synthetic estimator accuracy does not establish when an artist considers lighting inconsistent.
# Retained for compatibility pending human validation; docs/review/2026-09-16-authority-and-release-gate.md.
# Between the two cutoffs the measurement does not decide and the observer is asked.
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
SPILL_MIN_Y = 8 / 255 / 12.92   # ... and so is a neighbourhood crushed into the bottom 3% of the 8-bit
                            # range (sRGB's linear segment). There a ring mean is a handful of code values
                            # and the codec moves it further than any light does: an export written in the
                            # wrong colour space and sent through JPEG read +0.002 of spill, six standard
                            # errors of it, around a decal that lights nothing at all
PAIR_SURFACES = ("diffuse",)                   # the only surface asked per (subject, emitter)
EMITTER_KINDS = ("lamp", "neon", "sky", "screen", "glow", "paint", "unknown")
EMITTER_RANK = {"lamp": 0, "sky": 0, "screen": 0}     # designed sources outrank decorative ones (neon, glow, proposed: 1)
POINTED_MIN_PROXY = 0.25    # a subject may answer to the emitter it points at when that one is at least this
                            # fraction as strong as its expected key; the proxy under-reads clipped lamp heads
REJECTED_KINDS = ("paint",)   # a judgment: the blob does not emit, so its pairs are void
HELD_KINDS = ("unknown",)     # not a judgment: the observer could not say. Held, never rejected,
UNCONFIRMED = REJECTED_KINDS + HELD_KINDS   # because an axis does not pass on evidence nobody gave
                            # moves a spill ring further than a light does, and undoing it would need the
                            # encoder's tables. The answer to a lossy source is to ask for the original
MODES = ("physical", "fake_lighting", "engine_lit")
ANSWER_VALUES = ("yes", "no", "unknown")
EMITTER_COLOR, REJECTED_COLOR, SUBJECT_COLOR = (255, 0, 255), (120, 120, 120), (255, 255, 255)
BRIGHT_COLOR, FIT_COLOR, SHADOW_COLOR = (255, 220, 0), (0, 255, 255), (170, 90, 255)


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
    if min(float(Y[near].mean()), float(Y[far].mean())) < SPILL_MIN_Y:
        return None                                  # both rings are black: there is nothing to compare
    hue = _hue(_hex(rgb[mask].mean(0)))

    def pull(m: np.ndarray) -> float | None:
        h = measure.hsl(rgb[m])[0]
        h = h[~np.isnan(h)]
        return None if hue is None or not len(h) else float(np.mean(np.abs((h - hue + 180) % 360 - 180)))

    near_hue, far_hue = pull(near), pull(far)
    return {"luminance_gain": _r(float(Y[near].mean() - Y[far].mean())),
            "hue_pull_deg": None if near_hue is None or far_hue is None else _r(far_hue - near_hue),
            "ring_px": [int(near.sum()), int(far.sum())]}


def _emitters(rgb: np.ndarray, Y: np.ndarray, opaque: np.ndarray) -> tuple[list[dict], np.ndarray, dict]:
    """The brightest blobs, brightest first, a label plane (pixel value i belongs to emitter e<i>), and
    which of the two floors bound. The relative floor is a percentile and so survives any transfer
    function; the absolute one does not, and in a night scene it is the one that decides. Reporting
    which bound answers the first question a contributor asks: why was this blob not proposed?"""
    H, W = Y.shape
    if not opaque.any():
        return [], np.zeros((H, W), dtype=np.int16), {"value": None, "basis": "none"}
    rel = EMITTER_FRACTION * float(np.percentile(Y[opaque], EMITTER_PERCENTILE))
    floor = max(EMITTER_MIN_Y, rel)
    used = {"value": _r(floor), "basis": "absolute" if EMITTER_MIN_Y > rel else "relative",
            "absolute": EMITTER_MIN_Y, "relative": _r(rel)}
    emit = opaque & (Y >= floor)
    scale = min(1.0, LABEL_LONG_SIDE / max(H, W))
    small = emit
    if scale < 1:
        size = (max(1, round(W * scale)), max(1, round(H * scale)))
        small = np.asarray(Image.fromarray(emit.astype(np.uint8) * 255, "L").resize(size, Image.Resampling.BOX)) >= 128
    labels = measure.label(small)
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
    return rows, ids, used


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
             confirmed: set[int] | None, mask: np.ndarray | None = None) -> dict:
    x, y, w, h = sub["bbox"]
    a = rgba[y:y + h, x:x + w, 3]
    silhouette = alpha and bool((a < SILHOUETTE_ALPHA).any())
    body = mask if mask is not None else (a >= SILHOUETTE_ALPHA) if silhouette else np.ones((h, w), dtype=bool)
    # the subject's pixels are known when a mask says so, or when the file's alpha does -- either by
    # cutting the ground out of the box, or, for a box wholly inside a silhouette, by there being none
    known, outlined = mask is not None or alpha, mask is not None or silhouette
    ids = emit_ids[y:y + h, x:x + w] * body
    shade = body.copy()
    for k in np.unique(ids[ids > 0]):
        blob = ids == k
        # before answers: a ring on a pipe leaves, a lit cap stays; after: exactly the confirmed emitters leave
        if (k in confirmed) if confirmed is not None else (blob.sum() < EMITTER_MAX_SHARE * body.sum()):
            shade &= ~blob
    row = {"id": sub["id"], "bbox": sub["bbox"], "depth": sub["depth"],
           "mask": "given" if mask is not None else "alpha" if silhouette else "bbox",
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
    # Only where the file carries alpha: without it the bottom decile of a box is the ground behind the
    # subject, and any frame-wide gradient turns that ground into a confident direction. A vignette under
    # the default post-process volume of a URP project, below what anyone would call a defect, put a
    # confident shaded mass on a ball whose shading it never touched and pointed it near the lit side: an
    # asserted yes about the background. Alpha says which pixels are the subject, or, on a box wholly
    # inside a silhouette, that none of them are ground. What that gradient measured is a frozen
    # observation and is in docs/CHECKPOINT.md; a number here would be one nothing recomputes.
    bright = np.array(row["bright_side"]["vector"])
    lo = shade & (Ys <= np.percentile(v, SHADOW_PERCENTILE))
    ly, lx = np.nonzero(lo)
    sd = np.array([lx.mean() + x - cx, ly.mean() + y - cy])
    # strength as for the bright side: a box over a uniform ground has its darkest pixels all round it,
    # so the offset is noise that normalising would turn into a confident diagonal
    if known and np.linalg.norm(bright) > 0 and np.linalg.norm(sd) > 0:
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
    if outlined:
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


def _form(subjects: list[dict], emitters: list[dict], agreement: list[dict], run: str) -> tuple[dict, list[dict]]:
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
    form = {"schema_version": ANSWERS, "run_sha256": run, "style": {"mode": None}, "emitters": {e["id"]: None for e in emitters},
            "emitter_depth": {}, "pairs": pairs,
            "subjects": {s["id"]: None for s in _subject_surfaces()},
            "global": {"key": None, "atmosphere": None}}
    return form, questions


def _answers(a, emitters: list[dict], subjects: list[dict], run: str) -> dict:
    """The filled form, checked at the trust boundary. Unfilled fields count as unknown."""
    if not isinstance(a, dict):
        raise ValueError("answers must be the form returned by light_ledger, filled in")
    # every answer is addressed to an id, and an id belongs to the run that assigned it: emitter ids are
    # ordinal over the pixels this run measured, and a subject id is whatever named the box. So the sheet
    # is stamped with the run rather than the file. The same bytes with other boxes, or mirrored, are
    # other ids -- and mirroring is the one operation here that reorders emitters on purpose, which a
    # file digest cannot see. A hand-written sheet may omit the stamp.
    if a.get("run_sha256") not in (None, run):
        raise ValueError("answers were filled for a different run: the sheet's ids were assigned over "
                         "this file's pixels, with that run's subjects and mirror, so run phase one "
                         "again with the arguments you mean to answer for")
    style = a.get("style") or {}
    if not isinstance(style, dict):     # the type is checked before the value is read: `or {}` keeps a
        raise ValueError(f"style must be an object; style.mode is one of {MODES}")   # truthy list intact
    mode = style.get("mode") or "physical"
    if mode not in MODES:
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
    if not isinstance(pairs, list):    # the type before the value, as every sibling above does it:
        raise ValueError("pairs must be a list of "                 # enumerate(5) raises in Python's
                         f"{{subject, emitter, surface \u2208 {PAIR_SURFACES}, answer \u2208 {ANSWER_VALUES}}}")
    for i, p in enumerate(pairs):                                   # words, not the contract's
        if not isinstance(p, dict) or p.get("subject") not in sids or p.get("emitter") not in eids \
                or p.get("surface") not in PAIR_SURFACES or p.get("answer") not in ANSWER_VALUES + (None,):
            raise ValueError(f"pairs[{i}] must be {{subject, emitter, surface ∈ {PAIR_SURFACES}, answer ∈ {ANSWER_VALUES}}}")
    subj = a.get("subjects") or {}
    if not isinstance(subj, dict):
        raise ValueError("subjects must map a surface id to {no: [ids], unknown: [ids]}")
    for sid, lists in subj.items():
        if sid not in {s["id"] for s in _subject_surfaces()} or not (lists is None or isinstance(lists, dict)
                and all(isinstance(lists.get(k, []), list) and not set(lists.get(k, [])) - sids for k in ("no", "unknown"))):
            raise ValueError(f"subjects.{sid} must be null, or {{no: [subject ids], unknown: [subject ids]}}")
    glob = a.get("global") or {}
    if not isinstance(glob, dict) or any(v not in ANSWER_VALUES + (None,) for v in glob.values()):
        raise ValueError(f"global.key and global.atmosphere must be one of {ANSWER_VALUES}")
    return {"mode": mode, "kinds": {e["id"]: kinds.get(e["id"]) for e in emitters},
            "emitter_depth": {k: measure.layer_index(v, f"emitter_depth.{k}") for k, v in depth.items()},
            "pairs": {(p["subject"], p["emitter"], p["surface"]): p.get("answer") or "unknown" for p in pairs},
            "subjects": {s["id"]: None if subj.get(s["id"]) is None else
                         {"no": set(subj[s["id"]].get("no", [])), "unknown": set(subj[s["id"]].get("unknown", []))}
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


def _emitter_verdicts(emitters: list[dict], held: list[dict]) -> list[dict]:
    """A light the frame does not answer to: nothing points at it and nothing near it is brighter for
    it. Both tests are a sign or a count, so no invented magnitude decides a light source.

    A blob the observer left unclassified is neither answer. It is a hold, so it keeps its row and its
    measured spill: dropping it would let the one honest answer be the one that hides a decal."""
    rows = []
    for e in emitters:
        sp, seen = e.get("spill"), e.get("receivers") or 0
        lights = seen > 0 or bool(sp and sp["luminance_gain"] > 0)
        rows.append({"id": e["id"], "kind": e["kind"], "receivers": seen, "spill": sp,
                     "verdict": "lights" if lights else "lights_nothing" if sp else "unreadable"})
    rows += [{"id": e["id"], "kind": e["kind"], "receivers": None, "spill": e.get("spill"),
              "verdict": "unclassified"} for e in held]
    return rows


def _verdict(subjects: list[dict], emitters: list[dict], held: list[dict], agreement: list[dict],
             key_fit: dict | None, ans: dict) -> dict:
    mode = ans["mode"]
    ranks = _ranks(emitters)
    directional = next((h for h in (key_fit or {}).get("hypotheses", []) if h["hypothesis"] == "directional"), None)
    rows = []
    for s in subjects:
        v = {"id": s["id"], "mode": mode, "expected_key": None, "pointed_at": None, "verdict_emitter": None,
             "residual_deg": None, "diffuse": "unknown", "basis": "none", "specular": "unknown", "light_color": "unknown",
             "axis": None}
        for surf in _subject_surfaces():
            # a surface nobody wrote on is unanswered, not agreed. Only a list the observer actually
            # filled in can leave a subject at yes; null is the whole ask, so null stays unknown.
            lists = ans["subjects"][surf["id"]]
            v[surf["id"]] = ("unknown" if lists is None or s["id"] in lists["unknown"]
                             else "no" if s["id"] in lists["no"] else "yes")
        if not s["bright_side"]:
            rows.append(v | {"axis": "unknown"})
            continue
        measured = _shadow_measured(s)
        v["shadow_opposition_deg"] = s["shadow"]["opposition_deg"] if measured else None
        shadow = ans["subjects"]["cast_shadow"]
        listed = shadow is not None and s["id"] in shadow["no"] | shadow["unknown"]
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
    emits = _emitter_verdicts(emitters, held)
    # a declared light the frame ignores is the elements disagreeing with each other, not with a brief;
    # under a declared stylistic key it is the style, so it lands on intentional_contrast instead
    dark = [e for e in emits if e["verdict"] == "lights_nothing"]
    # a confirmed light whose neighbourhood could not be read is not a light that passed: bloom, a
    # vignette or any exposure lift raises the emitter floor until the rings have no ground left, and
    # the frame then reports no dark emitter because it measured none. That is warn, never pass.
    # ... and so is a blob nobody classified: unknown is a hold, not a finding of "not a light"
    unchecked = [e for e in emits if e["verdict"] in ("unreadable", "unclassified")]
    shadows = [r for r in rows if r.get("shadow_basis") == "measurement"]
    crossed = [r["id"] for r in shadows if r["cast_shadow"] == "no"]
    fake = mode == "fake_lighting"
    cohesion = "unknown"
    if not fake:
        cohesion = ("fail" if dark or crossed else
                    "warn" if unchecked else
                    "pass" if shadows or any(e["verdict"] == "lights" for e in emits) else "unknown")
    # a declared stylistic key that nothing could be fitted to is unmeasured, not failing: without a
    # directional hypothesis and without a dark or crossed finding, the frame gave nothing to judge,
    # and warning there is the verdict saying more than the measurement did
    contrast = "unknown"
    if fake:
        contrast = ("pass" if directional["within_tolerance"] >= 0.5 and not dark and not crossed else "warn") \
            if directional else "warn" if dark or crossed else "unknown"
    frame = {"direction_compliance": "fail" if "fail" in axes else "warn" if "warn" in axes
             else "pass" if "pass" in axes else "unknown",
             "intentional_contrast": contrast, "asset_cohesion": cohesion}
    return {"mode": mode, "key": {"answer": ans["global"]["key"], "best": (key_fit or {}).get("best")},
            "atmosphere": ans["global"]["atmosphere"], "emitters": emits, "subjects": rows, "axes": frame}


def _observations(verdict: dict, emitters: list[dict], subjects: list[dict], ans: dict) -> list[dict]:
    """What this family observed, as `observation.v1` items: measured ones asserted, observer ones
    estimated. Notes cite ids (e2, pipe_left) and never a magnitude.

    The items and not the record. Which asset they are about, which layer the evidence is, and who
    observed are facts about the run, and a second family answering them again is two records that
    disagree about one asset -- so the run assembles the record and this returns its own half."""
    items = []
    term = {s["id"]: s["terms"][0] for s in surfaces()["surfaces"]}
    boxes = {s["id"]: s["bbox"] for s in subjects}
    dark = {e["id"] for e in verdict["emitters"] if e["verdict"] == "lights_nothing"}
    for e in emitters:
        # the kind the pass settled, not the raw answer: a blob nobody answered for and one answered
        # `unknown` are the same fact -- nobody decided -- and the verdict already warns on both. It
        # recorded only the second, so a run could warn a reader and leave the corpus silent
        kind, held = e["kind"], e["kind"] in HELD_KINDS
        items.append({"term_id": term["emissive"], "level": "unknown" if held else "estimated",
                      "region": e["bbox"],
                      "note": f"{e['id']} was left unclassified, so nothing is judged against it" if held
                      else f"{e['id']} is bright paint, not a source" if kind in REJECTED_KINDS
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
            elif v[surf["id"]] == "unknown" and sid in (ans["subjects"][surf["id"]] or {}).get("unknown", ()):
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
    return items


# Eight points, clockwise from +x. Image coordinates, so +y is down and `[-0.7, -0.7]` is upper left,
# exactly as surfaces.v1.json states it. The label is a coarser projection of a measured unit vector,
# the same move `_direction` makes on an angle; it introduces no magnitude the measurement did not have.
FACINGS = ("right", "lower right", "down", "lower left", "left", "upper left", "up", "upper right")


def _facing(vec) -> str:
    return FACINGS[int((math.degrees(math.atan2(vec[1], vec[0])) % 360 + 22.5) % 360 // 45)]


def _findings(result: dict) -> list[dict]:
    """What this pass found, one row per finding, in the shape every family reports in.

    A row is a sentence and the four things a reader profile may do to it: withhold it when a
    measurement settled it on its own, name the surfaces it points at, say what decided it, attach the
    angle a contested one turned on. The family writes the sentence, because only the family knows what
    a lighting finding is. It never decides who hears one -- `reading` does that, for every family at
    once, which is what keeps a run from speaking in as many voices as it has families.

    Surfaces travel as `{label, term}` beside a `say` that ends at its colon, rather than joined into
    it. Whether a term id may be said belongs to the reader and to the corpus, and a sentence handed
    over with the ids already baked in could not be unsaid for the reader who has no vocabulary.
    """
    verdict = result["verdict"]
    boxes = {s["id"]: s["bbox"] for s in result["subjects"]}
    out: list[dict] = []

    def row(say: str, terms: list[dict] | None = None, settled: bool = False,
            basis: str | None = None, evidence: float | None = None) -> None:
        out.append({"say": say, "terms": terms or [], "settled": settled,
                    "basis": basis, "evidence": evidence})

    for v in verdict["subjects"]:
        sid = v["id"]
        where = "%s (box %d,%d to %d,%d)" % (sid, *boxes[sid])
        lit = next((s["bright_side"] for s in result["subjects"] if s["id"] == sid), None)
        facing = _facing(lit["vector"]) if lit else None
        # `settled` is the measurement deciding alone, which is the one thing a profile may silence.
        # The contested band below is never marked settled: it is what that silence exists to leave
        settled = v["basis"] == "measurement"
        if v["diffuse"] == "disagrees":
            row(f"The lit side of {where} faces {facing}, which is not where the light it should "
                f"answer to ({v['expected_key']}) is.",
                settled=settled, basis=v["basis"], evidence=v["residual_deg"])
        elif v["diffuse"] == "agrees" and facing:
            row(f"The lit side of {where} faces {facing}, and that agrees with "
                f"{v['verdict_emitter']}.", settled=settled, basis=v["basis"], evidence=v["residual_deg"])
        elif v["diffuse"] == "unknown" and v["expected_key"]:
            # the contested band itself: the measurement placed the lit side and declined to rule on
            # it, and nobody answered. Saying nothing here is the defect this whole file keeps having
            row(f"The lit side of {where} faces {facing}, and whether that answers to "
                f"{v['expected_key']} is undecided — too far off to pass and too close to fail, "
                f"and nobody has ruled.", basis=v["basis"], evidence=v["residual_deg"])
        if v.get("cast_shadow") == "no":
            row(f"The shaded part of {where} is not opposite its lit side, so its shadow and its "
                f"light disagree.", settled=v.get("shadow_basis") == "measurement",
                basis=v.get("shadow_basis"), evidence=v.get("shadow_opposition_deg"))
        wrong = _surfaces_at(v, "no", skip="cast_shadow")
        if wrong:
            row(f"On {where}, these are missing or inconsistent with the rest of the frame:",
                terms=wrong, basis="observer")
        # two different kinds of not-knowing, and collapsing them is the defect this file has had three
        # times: the measurement failing to read a shaded mass is not the observer declining to look
        if v.get("cast_shadow") == "unknown" and v.get("shadow_basis") == "none":
            row(f"The shaded part of {where} was too faint to measure, so nothing here can say "
                f"which way its shadow falls.")
        unseen = _surfaces_at(v, "unknown", skip="cast_shadow" if v.get("shadow_basis") == "none" else None)
        if unseen:
            row(f"Nobody has decided these on {where}, which is not the same as fine — it means "
                f"no one has looked:", terms=unseen)
    # `unclassified` and `unreadable` are not the same hold and must not be said as one: the first is
    # nobody having judged the blob, the second a confirmed light whose surroundings could not be read
    held = [e["id"] for e in verdict["emitters"] if e["verdict"] == "unclassified"]
    if held:
        row(f"{_join(held)} {'is a bright area' if len(held) == 1 else 'are bright areas'} nobody "
            f"has said is a light or not, so nothing in the frame was judged against "
            f"{'it' if len(held) == 1 else 'them'}.")
    blind = [e["id"] for e in verdict["emitters"] if e["verdict"] == "unreadable"]
    if blind:
        row(f"{_join(blind)} {'is a light' if len(blind) == 1 else 'are lights'}, but the area "
            f"around {'it' if len(blind) == 1 else 'them'} is too bright to read, so nothing could "
            f"be checked against {'it' if len(blind) == 1 else 'them'}.")
    dark = [e["id"] for e in verdict["emitters"] if e["verdict"] == "lights_nothing"]
    if dark:
        row(f"{_join(dark)} {'is a light' if len(dark) == 1 else 'are lights'} that nothing in the "
            f"frame takes {'its' if len(dark) == 1 else 'their'} light from.")
    return out


def _join(items: list[str]) -> str:
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def _surfaces_at(v: dict, value: str, skip: str | None = None) -> list[dict]:
    """The surfaces of one subject at one verdict value, each with the term that names it.

    Both halves travel and the reader decides which of them is said, because the choice turns on who
    is listening and on what this team has written -- neither of which this family knows. Deciding it
    here would put the reader's affair inside the finding, where no profile could reach it."""
    out = []
    for k in _subject_surfaces():
        if v[k["id"]] != value or k["id"] == skip:
            continue
        surf = _surface(k["id"])
        out.append({"label": surf["label"].lower(), "term": surf["terms"][0]})
    return out


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
    # the size asked for, not the one read back: without FreeType `load_default` answers a bitmap
    # font that carries no `size`, and the overlay is the one surface a reviewer actually looks at
    pt = max(10, long // 70)
    font = ImageFont.load_default(size=pt)

    def label(xy, text, color):
        d.text(xy, text, fill=color, font=font, stroke_width=lw, stroke_fill=(0, 0, 0))

    for e in emitters:
        x, y, w, h = e["bbox"]
        color = REJECTED_COLOR if e["kind"] in REJECTED_KINDS else EMITTER_COLOR   # a hold stays proposed
        d.rectangle([x, y, x + w - 1, y + h - 1], outline=color, width=lw)
        label((x, max(0, y - pt - 2)), e["id"], color)
    for s in subjects:
        x, y, w, h = s["bbox"]
        d.rectangle([x, y, x + w - 1, y + h - 1], outline=SUBJECT_COLOR, width=lw)
        label((x + lw + 1, y + lw + 1), s["id"], SUBJECT_COLOR)
        if not s["bright_side"]:
            continue
        length = max(3 * pt, 0.6 * np.sqrt(s["pixels"] / np.pi))
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


def pass_(ctx: dict, out_dir: Path | None = None, answers: dict | None = None) -> dict:
    """The lighting family's half of one run. `run.open_run` owns the asset, the subjects and the run
    identity; everything here is a question about light.

    Phase one (no answers): emitters, per-subject direction, agreement, key fit, form, questions, overlay.
    Phase two (answers): the same over confirmed emitters, plus verdict and an observation record.
    Handing the form back unfilled is a valid phase two: it returns everything the measurement decides
    and nothing else.

    It takes a run and never a path, which is the whole of the dependency rule: a family cannot read the
    file, choose the subjects or decide what run it is in, so two families in one run cannot disagree
    about any of the three."""
    rgba, meta, subs = ctx["rgba"], ctx["meta"], ctx["subjects"]
    alpha, W, H = ctx["alpha"], ctx["width"], ctx["height"]
    masks, run, read = ctx["masks"], ctx["run"], ctx["capture"]
    opaque = rgba[..., 3] > 0 if alpha else np.ones((H, W), dtype=bool)
    rgb = rgba[..., :3].astype(np.float64) / 255.0
    Y = measure.luminance(rgb)
    emitters, emit_ids, floor = _emitters(rgb, Y, opaque)
    ans = _answers(answers, emitters, subs, run) if answers is not None else None
    confirmed = None
    if ans:
        for e in emitters:
            e["kind"] = ans["kinds"][e["id"]] or "unknown"
            e["depth"] = ans["emitter_depth"].get(e["id"])
        confirmed = {i for i, e in enumerate(emitters, 1) if e["kind"] not in UNCONFIRMED}
    rows = [_subject(s, rgba, Y, alpha, emit_ids, confirmed, masks.get(s["id"])) for s in subs]
    live = [e for e in emitters if confirmed is None or e["kind"] not in UNCONFIRMED]
    held = [e for e in emitters if confirmed is not None and e["kind"] in HELD_KINDS]
    agreement = _agreement(rows, live, max(W, H))
    for e in live:
        e["receivers"] = sum(1 for a in agreement if a["emitter"] == e["id"]
                             and a["angle_deg"] is not None and a["angle_deg"] <= KEY_TOLERANCE_DEG)
    key_fit = _key_fit(rows, live, agreement)
    out = {"schema_version": SCHEMA} | ctx["envelope"] | {
           "emitter_floor": floor, "emitters": emitters, "subjects": rows, "agreement": agreement, "key_fit": key_fit, "overlay": None}
    if read is not None:
        out["capture"] = read
    if ans:
        verdict = _verdict(rows, live, held, agreement, key_fit, ans)
        out |= {"verdict": verdict, "observations": _observations(verdict, emitters, rows, ans),
                "context": {"lighting_mode": ans["mode"]}}
        out["findings"] = _findings(out)
    else:
        out["form"], out["questions"] = _form(rows, live, agreement, run)
    if out_dir is not None:
        file = Path(out_dir) / meta["sha256"][:12] / f"light_ledger.{run[:6]}{'.answered' if ans else ''}{'.mirror' if ctx['mirrored'] else ''}.png"
        _overlay(rgba, emitters, rows, agreement, key_fit, file)
        out["overlay"] = str(file)
    return out
