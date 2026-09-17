"""The vocabulary ships inside the wheel, so its validators belong in the suite, not in a README step."""
import json
from copy import deepcopy
from pathlib import Path

import pytest
import review_locales
import validate_stock

from asrai import vocab


def test_stock_corpus_validates():
    report = validate_stock.validate(vocab.DATA)          # raises with the reason on any failure
    assert report["status"] == "passed"
    assert report["json_schema"] == "passed_draft_2020_12"
    assert report["entry_count"] == len(vocab.index()) == 475
    assert (report["numeric_test_count"], report["negative_lint_test_count"]) == (8, 9)


def test_locales_carry_no_hard_defect():
    base = {e["id"]: e for e in vocab.pack()["entries"]}
    defects = []
    for path in sorted((vocab.DATA / "locales").glob("*.json")):
        doc = json.loads(path.read_text("utf-8"))         # in memory: only main() writes flags back
        _, errors = review_locales.review_locale(doc["locale"], doc["terms"], base)
        defects += errors
    assert defects == []


@pytest.mark.parametrize("path", sorted((vocab.DATA / "examples").glob("*.json")), ids=lambda p: p.stem)
def test_shipped_lint_agrees_with_the_vendored_validator(path):
    """Two implementations of one rule set: vocab.lint_instruction and the standalone copy in tools/."""
    doc = json.loads(path.read_text("utf-8"))
    assert vocab.lint_instruction(doc) == validate_stock.lint_instruction(doc, vocab.pack()) == []


def test_lint_implementations_agree_on_rejections():
    """Drop one context key at a time. A fixture list would rot; the shipped examples cannot."""
    pack = vocab.pack()
    checked = 0
    for path in sorted((vocab.DATA / "examples").glob("*.json")):
        doc = json.loads(path.read_text("utf-8"))
        for key in doc.get("context", {}):
            bad = deepcopy(doc)
            del bad["context"][key]
            assert vocab.lint_instruction(bad) == validate_stock.lint_instruction(bad, pack), f"{path.stem}/{key}"
            checked += 1
    assert checked > 20, f"only {checked} rejection paths exercised"


def test_surfaces_map_onto_the_vocabulary_and_the_skill():
    doc = json.loads((vocab.DATA / "surfaces.v1.json").read_text("utf-8"))
    skill = (vocab.DATA.parent / "skill" / "SKILL.md").read_text("utf-8")
    ids = [s["id"] for s in doc["surfaces"]]
    assert len(ids) == len(set(ids)) == 10
    for s in doc["surfaces"]:
        assert s["terms"] and all(t in vocab.index() for t in s["terms"]), s["id"]
        assert s["scope"] in doc["scopes"], s["id"]
        assert ("{subject}" in s["question"]) == (s["scope"] in ("subject", "pair")), s["id"]
        assert ("{emitter}" in s["question"]) == (s["scope"] in ("emitter", "pair")), s["id"]
        assert all(f.split("[")[0].split(".")[0] in ("emitters", "subjects", "agreement", "key_fit") for f in s["ledger"]), s["id"]
        assert f"`{s['id']}`" in skill, s["id"]         # the skill walks the same list, by id
        assert s["decided_by"] in doc["decided_by"], s["id"]
        # a surface that claims a ledger field must be one the measurement reaches, and the reverse
        assert bool(s["ledger"]) == (s["decided_by"] != "observer"), s["id"]
    assert doc["style_exemption"]["term"] in vocab.index()


def test_every_profile_answers_every_axis_and_no_axis_answers_itself():
    """A profile is a view over a verdict, so the file that defines one has to be as strict as the
    verdict is. Two rules, and both are this repository's own defects turned into checks.

    A profile declares every axis. An absent field would default silently, which is the failure this
    codebase has now fixed at an axis, a measurement, an answer contract and a rendered line.

    No axis holds one value across every profile. A constant is not a choice; it is an invariant
    wearing a field, and every field a persona carries is paid for in how few readers it describes
    (Chapman, Love, Milham, ElRif and Alford 2008, cited in the 2026-09-17 review). `unknown` reads as
    a hold for all three readers, which is why it is prose in this file and not a column."""
    doc = json.loads((vocab.DATA / "profiles.v1.json").read_text("utf-8"))
    spec = (Path(__file__).resolve().parent.parent / "docs" / "spec.md").read_text("utf-8")
    ids = [p["id"] for p in doc["profiles"]]
    assert len(ids) == len(set(ids)) and ids
    for row in doc["profiles"]:
        for axis, meta in doc["axes"].items():
            assert row.get(axis) in meta["values"], f"{row['id']}.{axis}"
        assert row["owes"].startswith("docs/spec.md#")
        assert "## 1. Purpose and non-goals" in spec          # the anchor the row points at
    for axis in doc["axes"]:
        assert len({row[axis] for row in doc["profiles"]}) > 1, f"{axis} is constant: an invariant, not an axis"


def test_the_skill_names_every_context_key_lint_requires():
    """lint refuses an instruction for a missing `context` key, and the model that wrote it sees only
    SKILL.md and a tool description with no declared properties. A requirement named nowhere is one a
    caller can find only by failing, so every key the linter reaches for must appear in the skill."""
    import re
    from pathlib import Path
    source = Path(vocab.__file__).read_text("utf-8")
    keys = set(re.findall(r'context\.get\("([A-Za-z_]+)"', source))
    keys |= set(re.findall(r'"([A-Za-z_]+)" not in context', source))
    keys |= set(re.findall(r'tb\.get\("([A-Za-z_]+)"\)', source)) | {"fps"}
    skill = (vocab.DATA.parent / "skill" / "SKILL.md").read_text("utf-8")
    assert keys, "the extraction found no context keys; the linter was probably restructured"
    assert sorted(k for k in keys if k not in skill) == []


def test_the_skill_names_every_tool_the_server_exposes():
    """No spec loss, mechanised for the tool list: a capability in server.py that SKILL.md does not
    describe is shipped dead, because the agent reading the skill never learns to call it."""
    import asyncio
    from asrai.server import server
    skill = (vocab.DATA.parent / "skill" / "SKILL.md").read_text("utf-8")
    names = sorted(t.name for t in asyncio.run(server.list_tools()))
    assert [n for n in names if f"`{n}`" not in skill] == []


def test_the_stock_manifest_matches_the_files_it_records():
    """CONTRIBUTING asks for the digest in the same commit as the data, and nothing enforced it: the
    entry for validation_report.json was found stale during a documentation pass, with no way to say
    when it had drifted. A digest nobody checks records nothing."""
    import hashlib
    import json
    manifest = json.loads((vocab.DATA / "manifest.sha256.json").read_text("utf-8"))
    wrong = {name: "missing" for name in manifest["files"] if not (vocab.DATA / name).exists()}
    wrong |= {name: "stale" for name, digest in manifest["files"].items()
              if (vocab.DATA / name).exists()
              and hashlib.sha256((vocab.DATA / name).read_bytes()).hexdigest() != digest}
    assert wrong == {}, wrong
    assert manifest["file_count"] == len(manifest["files"])
