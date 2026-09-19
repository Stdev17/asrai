"""Every surface that presents a run, and none of them may move a verdict.

A family answers what it measured. It does not decide who hears that answer or in which words, because
a family choosing for itself is a run speaking in as many voices as it has families about one asset --
and a reader cannot tell a voice apart from a finding. `2026-09-17-family-and-run.md` section 5 states
the rule for readers and generalises it to audiences; this module is where it holds, and it is the run
owner's because presenting a run is not a question about light.

**A reading is a projection of findings, never a source of them.** What arrives here is already
decided: one row per finding, each a sentence and everything a reader profile may do to it.
Nothing here can add a finding, drop one no profile asked to drop, or change what any of them says is
true. That is structural rather than a rule someone has to remember -- there is no verdict in this
module to move, and `run.ledger` is the only caller that has one.

**The profile decides who hears what, and it is the only thing that does.** Withhold what a
measurement settled, name a surface's term or leave it plain, say what decided a line, attach the
angle a contested one turned on. `profiles.v1.json` holds those axes and `docs/spec.md` section 1
holds the three readers they serve.

**A term a team has written about is a term that team has.** The overlay (`profile.py`) overrides
`vocabulary: avoid` and only that axis, so a corpus can widen a reader's vocabulary and can never
decide what to suppress or what to enrich: neither is in the evidence it was derived from.

Silence is the failure mode all of this exists to prevent. A surface nobody answered is said out loud
under every profile, because an omitted line reads as a clean one -- the defect this repository has now
fixed three times. The art director's `settled: silence` is not that: it drops findings a measurement
decided, which stay in the observation record and are read there.
"""
from __future__ import annotations

import functools
import json

from . import vocab

PROFILES = vocab.DATA / "profiles.v1.json"
UNJUDGED = ("Nothing has been judged yet. This is the measurement half; the form it returned has to be "
            "answered before anything here can pass or fail.")


@functools.cache
def profiles() -> dict:
    return json.loads(PROFILES.read_text("utf-8"))


def _profile(pid: str) -> dict:
    row = next((p for p in profiles()["profiles"] if p["id"] == pid), None)
    if row is None:
        raise ValueError(f"unknown profile {pid!r}; one of {[p['id'] for p in profiles()['profiles']]}")
    return row


def sentences(findings: list[dict] | None, profile: str, overlay: dict | None = None) -> list[str]:
    """Say one run's findings to one reader, one line per finding.

    `findings` is `None` when no family reached a verdict, which is phase one and not an empty
    reading: the form has to come back before anything here can pass or fail, and saying nothing at
    all would read as a clean frame. An empty list is the other case and says nothing, correctly --
    a family that judged and found nothing has nothing to say.

    A finding's `say` is the whole sentence, except when it carries `terms`: then it ends at its colon
    and is completed here, because which surfaces may be named out loud is the reader's affair and the
    corpus's. A sentence handed over with the ids already baked in could not be unsaid for the reader
    who has no vocabulary to use one."""
    p = _profile(profile)
    if findings is None:
        return [UNJUDGED]
    seen = set(overlay or ())
    out = []
    for f in findings:
        if f["settled"] and p["settled"] == "silence":
            continue
        line = f["say"]
        if f["terms"]:
            # several surface labels contain their own "and", so these lists are joined on semicolons
            line += " " + "; ".join(_named(t, p, seen) for t in f["terms"]) + "."
        out.append(line + _said(p, f["basis"], f["evidence"]))
    return out


def _named(term: dict, p: dict, seen: set) -> str:
    """One surface, with the term that names it when this reader may read one.

    A term this corpus has written about is what this team says out loud, so naming it is the local
    idiom rather than jargon, and the hundreds of terms nobody here has ever used stay out of a
    sentence meant to be acted on. A reader who needs the canonical term goes and asks an artist,
    which is a cheaper escape than a renderer guessing which words are safe."""
    named = p["vocabulary"] != "avoid" or f"term:{term['term']}" in seen
    return f"{term['label']} ({term['term']})" if named else term["label"]


def _said(p: dict, basis: str | None, evidence: float | None) -> str:
    """What a line adds beyond the finding: who decided it, or the angle the contested band turned on.
    Both are suffixes, so neither can change the sentence that carries them."""
    if p["basis"] == "show" and basis in ("measurement", "observer"):
        return f" ({basis})"
    if p["contested"] == "hand_over" and evidence is not None:
        return f" ({evidence:g} degrees)"
    return ""
