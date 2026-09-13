"""The vocabulary ships inside the wheel, so its validators belong in the suite, not in a README step."""
import json
from copy import deepcopy

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
