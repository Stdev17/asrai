"""What a team's records demonstrate about the vocabulary they work in, as a cache over those records.

A reader profile (`profiles.v1.json`) is a stereotype: three readers, fixed, knowing nothing about
anyone. This is the overlay over it, in the classical sense — an annotation on the domain model, which
here is the shipped vocabulary, saying where evidence exists that differs from the stereotype's prior.
`docs/review/2026-09-17-profile-alignment.md` is the design and the reasoning.

Three things about it are load-bearing and none of them is an implementation detail.

**It is derived, so it is a cache and not a source.** Every row comes from `records.jsonl`, which is
append-only and is the truth. Nothing is written here that could not be computed again, which is what
lets the `cache` realm own no invariant (`docs/architecture.md`): a wrong row is deleted, not repaired,
and a maintainer asked to repair one has found a bug in this projection. An earlier draft had an
explicit write verb for the agent to call; it was dropped when the evidence turned out to be in the
corpus already, since a cache that accepts writes is a source wearing a cache's name.

**It says what a corpus demonstrates, never what a person knows.** An observation record names an
observer's mode and model, not a human, so there is nobody here to profile and the review forbids
putting one here. A term this team's records use constantly is a term this team has; that is a fact
about the corpus, and it is the fact adaptation needs.

**Absence means no evidence, never a finding.** A scope nobody has written about is missing from
`scopes`, and a reader of this file falls back to the stereotype — which is a prior, not a pass. That
is why `unobserved` says so in the file itself rather than in a comment somebody has to find."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from . import records, vocab

OVERLAY = "profile_overlay.v1"
CACHE = "profile.overlay.json"
# `used`: the corpus wrote an observation under this scope, so the vocabulary is live in it.
# `overrode`: a record superseded another over this scope, which is judgment and not only vocabulary.
# Nothing writes `supersedes` yet (`case.v2` is planned, spec.md 4), so `overrode` is reachable by
# contract and unreached in practice. It is derived rather than deferred because the field is already
# promised by invariant 6 and a reader of this file must not have to ask which states can occur.
STATES = ("used", "overrode")


def _scopes(rows: list[dict]) -> dict:
    index = vocab.index()
    out: dict[str, dict] = {}
    for rec in rows:
        if rec.get("kind") != "observation":
            continue
        state = "overrode" if rec.get("supersedes") else "used"
        for item in rec.get("observations") or []:
            term = index.get(item.get("term_id"))
            if term is None:
                continue                      # a term the shipped vocabulary no longer carries
            for scope in (f"term:{term['id']}", f"category:{term['category']}"):
                row = out.setdefault(scope, {"state": "used", "evidence": [], "at": None})
                if state == "overrode":
                    row["state"] = "overrode"
                if rec.get("id") and rec["id"] not in row["evidence"]:
                    row["evidence"].append(rec["id"])
                row["at"] = max(row["at"] or "", rec.get("created_at") or "") or None
    return dict(sorted(out.items()))


def project(team: Path) -> dict:
    """Read the corpus and return the overlay. This is the whole computation; everything else is cost."""
    source = Path(team) / "records.jsonl"
    return {"schema_version": OVERLAY, "source": source.name,
            "source_bytes": source.stat().st_size if source.exists() else 0,
            "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "scopes": _scopes(records.read(source)),
            "unobserved": "A scope absent from `scopes` has no evidence in this corpus at all. Read it "
                          "as the reader profile's prior and never as a finding: nobody has looked is "
                          "not the same as nothing is there."}


def overlay(team: Path, refresh: bool = False) -> dict:
    """The overlay, from the cache beside the records when it still matches them.

    `records.jsonl` is append-only (spec.md invariant 6), so its size is enough to say whether the
    cache is behind it: an append always grows the file, and a same-size file is the same file. A
    digest would be sounder against a corpus that broke that invariant, and would cost a full read on
    every call, which is the cost this cache exists to avoid. If the two ever disagree the answer is to
    delete the cache, which is the only repair a cache has."""
    team = Path(team)
    path, source = team / CACHE, team / "records.jsonl"
    size = source.stat().st_size if source.exists() else 0
    if not refresh and path.exists():
        try:
            held = json.loads(path.read_text("utf-8"))
            if held.get("schema_version") == OVERLAY and held.get("source_bytes") == size:
                return held
        except (ValueError, OSError):
            pass                              # an unreadable cache is a cold cache, never an error
    fresh = project(team)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(fresh, indent=2, ensure_ascii=False) + "\n", "utf-8")
    return fresh


def digest(team: Path) -> str:
    """The projection's own sha256, for a caller that needs to know whether it moved between sessions."""
    o = project(team)
    return hashlib.sha256(json.dumps(o["scopes"], sort_keys=True).encode()).hexdigest()
