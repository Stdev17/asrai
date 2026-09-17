"""One run: one input read once, one set of subjects, one identity every family answers to.

A surface family owns questions about appearance -- which surfaces exist, what decides each, what the
thresholds are. It does not own the asset. This module does, and the split is what keeps two families
from disagreeing about the thing they are both looking at.

Three facts belong to the run and to no family, which is why they are here and not in `light`.

**The input is read once.** One decode, one array, one set of boxes, handed to every family in the run.
A family that loaded the file itself could measure a different thing under the same subject id, and
nothing in either record would say so.

**Subjects are derived once.** A box, a layer mask, a capture contract row, or -- for a file with alpha
and nothing else -- the silhouette itself. `SUBJECTS_MAX` bounds the work here rather than per family,
because the bound is on what a reviewer can be shown, not on what one pass can measure.

**A run has an identity.** `run_sha256` is taken over the bytes, the mirror flag and the subjects, and
it is what a typed answer sheet is stamped with: ids are assigned over the pixels *this* run measured,
so the same file with other boxes, or mirrored, is a different run and a sheet filled for one is
refused by the other. A file digest cannot see that, which is why the run carries its own.

The dependency runs one way: this module calls a family, a family never calls this one. A family
receives a run and returns its half of the ledger.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import numpy as np

from . import config, light, measure, records
from .measure import SILHOUETTE_ALPHA

SUBJECTS_MAX = 16            # the most a reviewer is shown at once, largest box first
SPACE = re.compile(r"\s+")
LOSSY_FORMATS = ("JPEG", "JPEG2000", "WEBP")   # reported, never corrected: ringing around a bright blob
COORDINATES = ("image pixels, x right, y down; vectors are [dx, dy]; "
               "depth is a layer index, 0 nearest")


def _box(value) -> list[int] | None:
    if not isinstance(value, list) or len(value) != 4:
        return None
    out = []
    for v in value:
        if isinstance(v, bool) or not isinstance(v, (int, float)) or v < 0 or float(v) != int(v):
            return None
        out.append(int(v))
    return out

def _silhouette_subject(rgba: np.ndarray) -> list[dict] | None:
    """A lone sprite is its own subject. Without this a file handed over with no boxes and no capture
    measures nothing at all, which is the one case a first reviewer reaches for first."""
    ys, xs = np.nonzero(rgba[..., 3] >= SILHOUETTE_ALPHA)
    if not len(xs):
        return None
    return [{"id": "asset", "mask": None, "bbox": [int(xs.min()), int(ys.min()),
                                                   int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)]}]

def _mask(path: str, box: list[int], W: int, H: int, sid: str) -> np.ndarray:
    """Which pixels of the image are this subject, as the alpha of a layer export.

    A box is the cheapest way to point at a thing and the most expensive to measure: whatever else sits
    in it is measured as if it were the subject. That is what stops albedo and ambient from separating a
    dark strap inside a shirt, and what stops the shaded mass from being read on a screenshot at all. A
    mask ends both, and it costs an artist nothing they do not already have: hand-drawn work is layered,
    and "export layers" writes exactly this file. The game still ships one flattened sprite; only the
    package carries the layers.

    Canvas-sized (what a layer export gives) or box-sized, so neither side has to crop."""
    rgba, meta = measure.load(Path(path))
    if not meta["alpha_present"]:
        raise ValueError(f"subjects {sid!r}: mask {path} has no alpha channel, and the mask is its alpha")
    x, y, w, h = box
    if (meta["width"], meta["height"]) == (W, H):
        a = rgba[y:y + h, x:x + w, 3]
    elif (meta["width"], meta["height"]) == (w, h):
        a = rgba[..., 3]
    else:
        raise ValueError(f"subjects {sid!r}: mask {path} is {meta['width']}x{meta['height']}; expected the "
                         f"image ({W}x{H}) or the subject's box ({w}x{h})")
    m = a >= SILHOUETTE_ALPHA
    if not m.any():
        raise ValueError(f"subjects {sid!r}: mask {path} is empty inside the subject's box")
    return m

def _subjects(subjects, capture, W: int, H: int) -> tuple[list[dict], dict | None]:
    """Model-supplied boxes, or the capture contract's screen boxes. Clipped to the image, ids unique.

    A composed_of row the contract cannot read is skipped, and every skip is reported back: a capture
    whose rows half parse (an engine script writing `bbox` where the contract says `screen_bbox`) would
    otherwise measure a quarter of the frame and let the axes speak as if that quarter were the frame."""
    if subjects is not None and capture:
        raise ValueError("subjects and capture both say what the subjects are: pass one. A capture's "
                         "composed_of rows are read only when no subjects are given, so passing both "
                         "measures the boxes and files the evidence as if the capture had been read")
    read = None
    if subjects is None and capture:
        doc = json.loads(Path(capture).read_text("utf-8"))
        rows = doc.get("composed_of") if isinstance(doc, dict) else None
        if not isinstance(rows, list):
            raise ValueError("capture must be a capture.json with a composed_of list")
        found, skipped = [], []
        times: dict[str, int] = {}
        for i, c in enumerate(rows):
            box = _box(c.get("screen_bbox")) if isinstance(c, dict) else None
            sid = str((isinstance(c, dict) and (c.get("game_object") or c.get("sprite")
                       or str(c.get("asset_sha256", ""))[:12])) or "subject")
            if box is None:
                skipped.append({"row": i, "id": sid,
                                "reason": "no screen_bbox [x, y, w, h] of whole pixels"})
                continue
            times[sid] = times.get(sid, 0) + 1
            found.append({"id": sid if times[sid] == 1 else f"{sid}_{times[sid]}", "bbox": box,
                          "depth": c.get("depth"), "mask": c.get("mask")})
        found.sort(key=lambda s: -(s["bbox"][2] * s["bbox"][3]))
        skipped += [{"row": None, "id": s["id"], "reason": f"over the {SUBJECTS_MAX}-subject limit, smallest first"}
                    for s in found[SUBJECTS_MAX:]]
        subjects = found[:SUBJECTS_MAX]
        read = {"path": str(capture), "declared": len(rows), "measured": len(subjects), "skipped": skipped}
    if not subjects:
        return [], read
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
        mask = s.get("mask")
        if mask is not None and not isinstance(mask, str):
            raise ValueError(f"subjects[{i}] {sid!r}: mask is the path of an image whose alpha marks the subject")
        out.append({"id": sid, "bbox": [x0, y0, x1 - x0, y1 - y0], "mask": mask,
                    "depth": measure.layer_index(s.get("depth"), f"subjects[{i}]")})
    return out, read

def open_run(path: Path, subjects: list[dict] | None = None, capture: str | None = None,
             mirror: bool = False) -> dict:
    """Read the asset once and settle what every family in this run will be looking at."""
    path = Path(path)
    rgba, meta = measure.load(path)
    alpha = meta["alpha_present"]
    H, W = rgba.shape[:2]
    if subjects is None and not capture and alpha:
        subjects = _silhouette_subject(rgba)
    subs, read = _subjects(subjects, capture, W, H)
    # what assigned the ids a sheet answers to: these bytes, these subjects, this mirror. Taken before
    # the flip, so a box that mirrors onto itself still tells the runs apart.
    run = hashlib.sha256(json.dumps([meta["sha256"], bool(mirror), subs], sort_keys=True).encode()).hexdigest()
    masks = {s["id"]: _mask(s["mask"], s["bbox"], W, H, s["id"]) for s in subs if s.get("mask")}
    if mirror:
        rgba = np.ascontiguousarray(rgba[:, ::-1])
        subs = [s | {"bbox": [W - s["bbox"][0] - s["bbox"][2], *s["bbox"][1:]]} for s in subs]
        masks = {k: np.ascontiguousarray(v[:, ::-1]) for k, v in masks.items()}
    return {"path": path, "rgba": rgba, "meta": meta, "alpha": alpha, "width": W, "height": H,
            "mirrored": bool(mirror), "run": run, "subjects": subs, "masks": masks, "capture": read,
            # the fields a run owns, travelling with it so a family repeats them rather than
            # restating them: a family that imported this module to ask for them would invert the
            # one dependency that keeps two families from disagreeing about one asset
            "envelope": {"path": str(path), "sha256": meta["sha256"], "width": W, "height": H,
                         "mirrored": bool(mirror), "coordinates": COORDINATES,
                         "source": {"format": meta["format"],
                                    "lossy": meta["format"] in LOSSY_FORMATS}}}


def _record(ctx: dict, observations: list[dict], context: dict, observer: dict | None,
            axes: dict) -> dict | None:
    """One record of what this run's families observed, or nothing when they observed nothing.

    Which asset, at which evidence layer and scale, and who observed, are the run's to answer and not a
    family's. Two families answering them apart is two records disagreeing about one asset, and
    `asserted` then means two things. The observer is the configured one: `spec.md` section 4 requires
    it, `config` is the only thing that holds it, and a family inventing one is how a null reached the
    corpus under a field the schema calls required.

    The three axes travel with it. They are the judgment the run reached, `spec.md` section 7.1 draws
    an arrow from them into the record, and until now they were computed, read aloud to whoever asked
    for a profile, and dropped -- so the corpus held what was observed and never what was concluded from
    it. The copy here and the one under `verdict` are the same values by construction; this is the one
    that survives the reply.

    Nothing observed is `None`, never a record with an empty list. A corpus that may not be edited is
    worse off holding a row that observed nothing, and what nobody decided is said to the reader
    instead. `None` rather than no key at all, because an omitted field reads as a clean one.

    The validation is this run's trust boundary in the outgoing direction. Everything guarded so far
    guards what a model sends in; nothing guarded what the package hands out, so the tool told to store
    a record was the first thing to look at one."""
    if not observations:
        return None
    capture = ctx["capture"] is not None
    record = {"kind": "observation", "asset_kind": "screenshot" if capture else "raster",
              "evidence_layer": "L2" if capture else "L1", "scale": "native",
              "asset_sha256": ctx["meta"]["sha256"], "context": context, "observations": observations,
              "axes": axes,
              "observer": dict(observer or config.DEFAULTS["observer"])}
    errors = records.validate(record)
    if errors:
        raise ValueError("this run built a record its own schema rejects, which is a defect in asrai and "
                         "not in what was answered: " + "; ".join(errors))
    return record


LOUD = ("warn", "fail")


def _backed(axes: dict, record: dict | None) -> None:
    """An axis that warns or fails is backed by something in the record.

    A `pass` needs no backing -- a pass is the absence of a finding -- but a run may not tell a reader
    that something is wrong and leave the corpus silent about it. Silence is the failure mode this
    repository has now fixed three times in the reader layer, and the record is where it costs most: a
    reading is read once, and the corpus is what everything after it is built on.

    The family supplies the observation and the run holds the rule, so a second family inherits it
    without being named in it. A violation is a defect in asrai and not in what was answered, which is
    why it raises rather than being reported as a finding about the asset."""
    loud = sorted(axis for axis, value in axes.items() if value in LOUD)
    if loud and not (record and record["observations"]):
        raise ValueError(f"this run says {', '.join(loud)} and records nothing, which is a defect in asrai: "
                         "the family that judged it owes an observation for what it found")


def ledger(path: Path, subjects: list[dict] | None = None, capture: str | None = None,
           out_dir: Path | None = None, mirror: bool = False, answers: dict | None = None,
           observer: dict | None = None) -> dict:
    """One run, judged by the families it asks, and recorded once. Today it asks one, and the ordering
    rule it will need is already written down: families run in the gate order of `spec.md` section 7 and
    never read each other's verdicts. A second family arrives as a row here, not as a second tool.

    A family returns the observations it made; the record they go in is assembled here, so that what a
    run says and what it stores cannot be two different things."""
    ctx = open_run(path, subjects, capture, mirror)
    out = light.pass_(ctx, out_dir, answers)
    if "observations" in out:
        axes = out["verdict"]["axes"]
        out["record"] = _record(ctx, out.pop("observations"), out.pop("context"), observer, axes)
        _backed(axes, out["record"])
    return out
