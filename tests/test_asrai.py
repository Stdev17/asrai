import asyncio
import json
import subprocess
import sys
import warnings

import numpy as np
import pytest
from PIL import Image, ImageDraw

# The words a document may spell a number with live with the scanner that looks for them, so the
# anchor check below and the net around it cannot come to know different words.
from check_claims_diff import NUMBER_WORDS, numerals

from asrai import config, doctor, measure, records, vocab

SHA = "a" * 64
OBSERVER = {"mode": "host", "model": "test-model", "prompt_rev": "v1"}


def sprite(path):
    img = Image.new("RGBA", (96, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((16, 8, 80, 56), fill=(220, 40, 40, 255))
    d.rectangle((40, 40, 56, 60), fill=(40, 40, 200, 255))
    img.save(path)
    return path


def test_search_get_and_locales():
    ids = [e["id"] for e in vocab.search("silhouette")["entries"]]
    assert "shape.silhouette" in ids[:3]
    ko = [e["id"] for e in vocab.search("실루엣", lang="ko")["entries"]]
    assert "shape.silhouette" in ko
    row = vocab.get("shape.silhouette", lang="ja", full=False)
    assert row["lang"] == "ja" and row["label_en"] == "silhouette" and row["label"] != "silhouette"
    full = vocab.get("color.saturation")
    assert "note" in full["quantification"] and full["localized"]["lang"] == "en"
    assert {"id", "label", "entry_count"} <= set(vocab.categories()[0])
    assert any(l["locale"] == "ko" for l in vocab.langs())
    with pytest.raises(ValueError):
        vocab.get("no.such_term")


def test_lint_rules():
    example = json.loads((vocab.DATA / "examples" / "body_width.json").read_text("utf-8"))
    assert vocab.lint_instruction(example) == []
    bad = json.loads(json.dumps(example))
    bad["changes"][0] = {"term_id": "perception.readability", "operation": "relative_delta",
                         "quantity": {"value": 20, "unit": "percent_relative"}, "property_binding": None,
                         "magnitude_basis": "example"}
    assert any("not a direct numeric property" in e for e in vocab.lint_instruction(bad))
    applied = json.loads(json.dumps(example))
    applied["status"] = "applied"
    applied["changes"][0]["magnitude_basis"] = "llm"
    errors = vocab.lint_instruction(applied)
    assert any("model-invented magnitude" in e for e in errors) and any("run_ref" in e for e in errors)


def test_measure_sprite_is_deterministic(tmp_path):
    path = sprite(tmp_path / "s.png")
    a = measure.measure(path)
    b = measure.measure(path)
    assert a == b
    assert (a["bit_depth"], a["color_type"], a["precision"]) == (8, "rgba", "8bit")
    assert 0.3 < a["alpha"]["coverage"] < 0.6 and a["alpha"]["binary"] is True
    native = a["scales"]["native"]
    assert native["silhouette"]["bbox"] == [16, 8, 65, 53] and native["silhouette"]["components"] == 1
    assert native["palette"][0]["rgb"] == "#dc2828" and native["palette"][0]["share"] > 0.7
    assert native["hue_bins_30deg"] is not None and abs(sum(native["hue_bins_30deg"]) - 1) < 0.01
    small = a["scales"]["thumbnail"]
    assert (small["width"], small["height"], small["resample"]) == (64, 43, "box")
    assert small["silhouette"]["components"] == 1
    t = measure.measure(path, target_width=48)["scales"]["target"]
    assert (t["width"], t["target_width"], t["resample"]) == (48, 48, "box")


def test_measure_screenshot_and_16bit_gray(tmp_path):
    ramp = np.tile(np.linspace(0, 255, 320, dtype=np.uint8), (180, 1))
    Image.fromarray(np.stack([ramp, ramp, ramp], -1), "RGB").save(tmp_path / "shot.png")
    shot = measure.measure(tmp_path / "shot.png")
    assert shot["alpha"] is None and shot["scales"]["native"]["silhouette"] is None
    assert shot["scales"]["native"]["chromatic_ratio"] == 0 and shot["scales"]["native"]["hue_bins_30deg"] is None
    gray16 = np.tile(np.linspace(0, 65535, 128, dtype=np.uint16), (32, 1))
    Image.fromarray(gray16).save(tmp_path / "g16.png")
    g = measure.measure(tmp_path / "g16.png")
    assert (g["bit_depth"], g["color_type"]) == (16, "gray")
    assert 0.1 < g["scales"]["native"]["luminance"]["p50"] < 0.9  # not clipped to white


def test_records_validation_and_append(tmp_path):
    log = tmp_path / "records.jsonl"
    base = {"kind": "observation", "asset_kind": "raster", "evidence_layer": "L1", "scale": "thumbnail",
            "asset_sha256": SHA, "observer": OBSERVER, "observations": [
                {"term_id": "perception.silhouette_readability", "level": "estimated", "note": "one blob"}]}
    stored = records.append(base, log)
    assert stored["id"].startswith("observation_") and stored["schema_version"] == "observation.v1"
    assert len(records.read(log)) == 1
    with pytest.raises(ValueError, match="must not contain numbers"):
        records.append(base | {"observations": [{"term_id": "color.saturation", "level": "estimated", "note": "about 5% too much"}]}, log)
    records.append(base | {"observations": [{"term_id": "lighting.form_shadow", "level": "estimated",
                                             "note": "bright side of pipe_2 faces e1 rather than e2"}]}, log)  # ids may end in digits
    with pytest.raises(ValueError, match="must not contain numbers"):
        records.append(base | {"observations": [{"term_id": "lighting.form_shadow", "level": "estimated", "note": "reads at 1080p"}]}, log)
    with pytest.raises(ValueError, match="can only be unknown"):
        records.append(base | {"observations": [{"term_id": "perception.visual_hierarchy", "level": "asserted", "note": "reads first"}]}, log)
    with pytest.raises(ValueError, match="must be L2"):
        records.append(base | {"asset_kind": "screenshot"}, log)
    with pytest.raises(ValueError, match="render_profile_id"):
        records.append(base | {"asset_kind": "svg"}, log)
    # a required field is a string, and a null is not a shorter one: `str(None)` is the string `None`,
    # so the check that catches an empty model used to pass the value the ledger actually builds
    for model in (None, "", "  ", 7):
        with pytest.raises(ValueError, match="observer.model required"):
            records.append(base | {"observer": OBSERVER | {"model": model}}, log)
    # the run's judgment travels with what it observed: all three axes or none, since a subset would
    # let a reader take a missing axis for one that passed
    records.append(base | {"axes": {a: "pass" for a in records.AXES}}, log)
    for axes in ({}, {"direction_compliance": "pass"}, dict.fromkeys(records.AXES, "pass") | {"extra": "pass"},
                 dict.fromkeys(records.AXES, "maybe"), "pass"):
        with pytest.raises(ValueError, match="axes|axis"):
            records.append(base | {"axes": axes}, log)
    pair = {"kind": "pairwise", "evidence_layer": "L1", "term_id": "color.saturation", "a": SHA, "b": "b" * 64,
            "verdict": "prefer_a", "by": "model"}
    with pytest.raises(ValueError, match="order_checked"):
        records.append(pair, log)
    records.append(pair | {"by": "human"}, log)
    with pytest.raises(ValueError, match="a must reference"):
        records.append(pair | {"by": "human", "a": None}, log)      # the same hole, on the other side
    for bad in (None, "x", 7):      # what a model sends when a run had nothing to record
        with pytest.raises(ValueError, match="must be a JSON object"):
            records.append(bad, log)
    assert len(records.read(log)) == 4


def test_doctor_counts_the_records_that_name_no_observer(tmp_path):
    """`observer.mode: host` means the agent hosting the server observed, and asrai cannot know which
    model that is. The run signs a record with the configured default and SKILL.md asks the model to
    put its own id there; a model that skips that step says so nowhere, and a corpus nobody attributed
    reads like a corpus nobody looked at.

    Counting is all asrai can do, and it is a report and not a gate -- `unknown` is honest, only
    uninformative, and refusing the record would lose an observation to save an attribution. It is out
    of the lock on purpose: a corpus grows, and a pinned view that moved with it would report drift
    every time somebody recorded something."""
    cfg = config.load(tmp_path)
    log = config.team_dir(cfg) / "records.jsonl"
    base = {"kind": "observation", "asset_kind": "raster", "evidence_layer": "L1", "scale": "native",
            "asset_sha256": SHA, "observer": config.DEFAULTS["observer"], "observations": [
                {"term_id": "lighting.form_shadow", "level": "estimated", "note": "the ball reads flat"}]}
    records.append(base, log)                                       # what the run signs, unreplaced
    records.append(base | {"observer": OBSERVER}, log)              # what a model that read step six sends
    records.append(base | {"observer": config.DEFAULTS["observer"]}, log)
    assert doctor.run(cfg)["observed"] == {"observations": 3, "observer_unnamed": 2}
    assert "observed" not in doctor.pinned_view(doctor.snapshot(cfg))


def test_doctor_lock_and_drift(tmp_path):
    cfg = config.load(tmp_path)
    assert doctor.run(cfg)["status"] == "unlocked"
    assert doctor.run(cfg, write_lock=True)["status"] == "locked"
    assert doctor.run(cfg)["status"] == "match"
    lock = json.loads((tmp_path / doctor.LOCK).read_text("utf-8"))
    lock["packages"]["numpy"] = "0"
    (tmp_path / doctor.LOCK).write_text(json.dumps(lock), "utf-8")
    report = doctor.run(cfg)
    assert report["status"] == "drift" and report["drift"][0]["key"] == "packages.numpy"


def test_mcp_tools_in_process_and_over_stdio():
    from asrai.server import server
    names = {t.name for t in asyncio.run(server.list_tools())}
    assert names == {"vocab_search", "vocab_get", "measure", "light_ledger", "record", "lint", "doctor"}
    schema = next(t for t in asyncio.run(server.list_tools()) if t.name == "light_ledger").input_schema
    assert schema["properties"]["subjects"]["anyOf"][0]["type"] == "array" and "answers" in schema["properties"]
    msgs = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                                                                    "clientInfo": {"name": "test", "version": "0"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "vocab_get", "arguments": {"lookup": "shape.silhouette", "full": False}}},
    ]
    proc = subprocess.Popen([sys.executable, "-m", "asrai.cli", "mcp"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, text=True)
    replies = {}
    try:
        for m in msgs:
            proc.stdin.write(json.dumps(m) + "\n")
        proc.stdin.flush()
        while 3 not in replies:  # keep stdin open until the last reply lands; EOF would shut the server down
            line = proc.stdout.readline()
            if not line:
                break
            r = json.loads(line)
            if "id" in r:
                replies[r["id"]] = r
    finally:
        proc.stdin.close()
        proc.wait(timeout=30)
    assert {t["name"] for t in replies[2]["result"]["tools"]} == names
    assert "shape.silhouette" in json.dumps(replies[3]["result"])


SOFT_CAP_TOKENS, HARD_CAP_TOKENS = 1000, 1200   # docs/spec.md 6: a warning, then a failure
BYTES_PER_TOKEN = 4.25                          # o200k_base over this surface as compact JSON, measured 2026-09-14


def tool_surface_bytes() -> int:
    """The tools/list reply a host re-sends the model on every turn: name, description and input schema per
    tool, as compact JSON. Hosts render it differently, so this is the reproducible proxy, not one host's bill."""
    from asrai.server import server
    return sum(len(json.dumps({"name": t.name, "description": t.description, "inputSchema": t.input_schema},
                              separators=(",", ":"))) for t in asyncio.run(server.list_tools()))


def test_the_tool_surface_stays_inside_its_token_budget():
    """"Never more than eight tools" had no measurement behind it, and no host caps at eight. What a tool
    costs is its schema on every turn, so the budget is in bytes: light_ledger alone was 38 per cent of it.
    Trim a description before raising a cap; the detail belongs in SKILL.md, which is read once."""
    tokens = tool_surface_bytes() / BYTES_PER_TOKEN
    assert tokens <= HARD_CAP_TOKENS, f"tool surface at {tokens:.0f} tokens: cut description prose, do not raise the cap"
    if tokens > SOFT_CAP_TOKENS:
        warnings.warn(f"tool surface at {tokens:.0f} tokens, over the {SOFT_CAP_TOKENS}-token soft cap", stacklevel=1)


def test_measure_bounds_the_work_it_accepts(tmp_path):
    path = sprite(tmp_path / "s.png")
    with pytest.raises(ValueError, match="Mpx"):          # 4x4 upscaled to 50000 wide is 800 GB of float64
        measure.measure(path, target_width=50_000)
    with pytest.raises(ValueError, match="target_width"):
        measure.measure(path, target_width=0)
    assert measure.measure(path, target_width=192)["scales"]["target"]["width"] == 192
    big = tmp_path / "big.png"
    Image.new("L", (4000, 4000)).save(big)                # 16 Mpx: refused on the header, before decode
    with pytest.raises(ValueError, match="Mpx"):
        measure.measure(big)


def test_malformed_host_input_lints_instead_of_raising():
    """Every shape here is one a model plausibly sends. None may escape as an exception."""
    good = {"term_id": "color.saturation", "operation": "set"}
    for bad in ([],
                {"changes": "increase the saturation"},
                {"changes": ["increase the saturation"]},
                {"changes": {"term_id": "color.saturation"}},
                {"changes": [good | {"quantity": "a lot"}]},
                {"context": "the hero sprite", "changes": [good]},
                {"context": {"timebase": "12fps"}, "changes": [good | {"quantity": {"unit": "frame", "value": 8}}]},
                {"execution": []}):
        errors = vocab.lint_instruction(bad)
        assert isinstance(errors, list) and errors, bad


def test_malformed_record_validates_instead_of_raising():
    base = {"kind": "observation", "evidence_layer": "L1", "asset_kind": "raster", "scale": "native",
            "asset_sha256": SHA, "observer": OBSERVER}
    for bad in ([],
                "observation",
                {"kind": ["observation"]},
                base | {"observer": "me"},
                base | {"observations": ["reads as one blob"]},
                base | {"observations": [{"term_id": "shape.silhouette", "level": "estimated"}, 7]}):
        errors = records.validate(bad)
        assert isinstance(errors, list) and errors, bad



def test_the_claims_scanner_finds_a_magnitude_and_not_a_reference():
    """`tools/check_claims_diff.py` is the net around `claims.json` (runbook §1, tier 2). It has to read
    the magnitude a sentence states and leave the shapes that carry a numeral without claiming anything:
    an id, a date, a version, a section reference. And a number-word inside an ordinary string literal is
    data — the map of number-words is itself a dict of number-words, and a scanner that read its own
    values as prose would report every one of them."""
    from pathlib import Path

    import check_claims_diff as scanner

    def found(text):
        return {value for value, _ in scanner.numbers(text)}

    assert found("stays under four degrees (bright side)") == {4}
    assert found("the emitter it points at when that one is at least a quarter as strong") == {0.25}
    assert found("measures 0.37 of shaded strength on a box") == {0.37}
    assert found("the surface measures 3,843 bytes and is held under 1,200 tokens") == {3843, 1200}
    # the two directions are one definition: every spelling the claims test looks for is a spelling the
    # scanner reads back as that number, so neither tier has a form the other cannot see
    assert scanner.numerals(1200) == ("1200", "1,200") and scanner.numerals(7) == ("7",)
    for value in (7, 475, 1200, 3843, 0.25):
        assert all(found(spelling) == {value} for spelling in scanner.numerals(value)), value
    assert found("`measure.v1` on 2026-09-17, Python 3.14, runbook §1, tier 2, tiers 1 and 2, e2 at L1") == set()
    assert found("spec.md section 7.1 and §7.1 both point at the surface pass") == set()
    # a numbered item inside a comment carries two markers, and stripping only the outer one leaves the
    # inner looking like a magnitude. The item number is not a claim at either depth
    assert found("# 1. a directory carries its own README") == set()
    assert found("1. a directory carries its own README") == set()
    assert found("# 4. two lists, and 12 of them are drawn") == {2, 12}
    src = (Path(__file__).resolve().parent.parent / "tools" / "check_claims_diff.py").read_text("utf-8")
    lines = src.splitlines()
    code = next(i for i, line in enumerate(lines, 1) if line.startswith("NUMBER_WORDS = {"))
    prose = next(i for i, line in enumerate(lines, 1) if "Tier 2 of the gate" in line)
    kept = {n for n, _ in scanner.prose_only("tools/check_claims_diff.py", [(code, ""), (prose, "")])}
    assert kept == {prose}, kept


def test_every_number_the_documents_claim_is_the_number_the_repository_has():
    """Prose counts drift silently: "twelve locale bundles" outlived the twelfth bundle in three files at
    once, and the per-file test counts in tests/README summed to thirty-six against a suite of fifty-one.
    tests/claims.json registers each number with what computes it and the exact wording that carries it,
    so a value that moves, or a document that keeps the old one, fails here instead of misleading a reader.
    A translation under docs/i18n/ is held to the same number as the English file it mirrors."""
    import asyncio
    import json
    from pathlib import Path
    import test_light
    from asrai import light, measure, run, vocab
    from asrai.server import server

    root = Path(__file__).resolve().parent.parent
    data = vocab.DATA
    truth = {
        "vocab.terms": lambda: len(vocab.index()),
        "vocab.categories": lambda: len(vocab.categories()),
        "vocab.languages": lambda: len(vocab.locale_codes()),
        "locales.bundles": lambda: len(list((data / "locales").glob("*.json"))),
        "mcp.tools": lambda: len(asyncio.run(server.list_tools())),
        "package.modules": lambda: len(list((root / "src" / "asrai").glob("*.py"))),
        "package.core_modules": lambda: len([f for f in (root / "src" / "asrai").glob("*.py")
                                            if f.name not in ("cli.py", "server.py")]),
        "surfaces.count": lambda: len(light.surfaces()["surfaces"]),
        "light.subjects_max": lambda: run.SUBJECTS_MAX,
        "light.emitters_max": lambda: light.EMITTERS_MAX,
        "light.key_tolerance_deg": lambda: light.KEY_TOLERANCE_DEG,
        "light.disagree_deg": lambda: light.DISAGREE_DEG,
        "light.pointed_min_proxy": lambda: light.POINTED_MIN_PROXY,
        "light.spill_near_radii": lambda: light.SPILL_NEAR,
        "light.spill_far_inner_radii": lambda: light.SPILL_FAR[0],
        "light.spill_far_outer_radii": lambda: light.SPILL_FAR[1],
        # a conformance bound is a decision, so its truth is the constant the sweep is held to
        "light.bright_side_noise_deg": lambda: test_light.BRIGHT_SIDE_NOISE_DEG,
        "light.contour_fit_noise_deg": lambda: test_light.CONTOUR_FIT_NOISE_DEG,
        "measure.max_megapixels": lambda: measure.MAX_PIXELS // 1_000_000,
        "fixtures.images": lambda: len([p for p in (root / "tests" / "fixtures").iterdir()
                                        if p.suffix in (".png", ".jpg")]),
        "instruction.examples": lambda: len(list((data / "examples").glob("*.json"))),
        "mcp.surface_bytes": tool_surface_bytes,
        "mcp.soft_cap_tokens": lambda: SOFT_CAP_TOKENS,
        "mcp.hard_cap_tokens": lambda: HARD_CAP_TOKENS,
        "mcp.bytes_per_token": lambda: BYTES_PER_TOKEN,
        # Human revision-reference request, 2026-09-17; this is a display minimum, not identity.
        "references.abbrev_min": lambda: 7,
        # Human scope decision, 2026-09-16; conventions §0 distinguishes review from diagram fit.
        "architecture.owner_review_at": lambda: 10,
        "architecture.diagram_node_limit": lambda: 10,
    }
    claims = json.loads((root / "tests" / "claims.json").read_text("utf-8"))["claims"]
    assert {c["id"] for c in claims} == set(truth), "claims.json and this test disagree on what is registered"

    wrong, absent, unanchored, untranslated = [], [], [], []
    for c in claims:
        value = truth[c["id"]]()
        if value != c["value"]:
            wrong.append(f"{c['id']}: claims.json says {c['value']}, {c['truth']} gives {value}")
            continue
        word = NUMBER_WORDS.get(value, "")
        for path, phrase in c["claimed_in"].items():
            # the wording has to carry the number itself, or a claim could be met by unrelated prose
            if not any(n in phrase for n in numerals(value)) and (not word or word not in phrase.lower()):
                unanchored.append(f"{c['id']} -> {path}: {phrase!r} does not contain {value}")
            elif phrase not in (root / path).read_text("utf-8"):
                absent.append(f"{c['id']} -> {path}: {phrase!r}")
            # a translation of a document that states a number states the same number. It is found from
            # the English row, so no translator edits claims.json; the numeral is what is required,
            # which is why docs/i18n/README.md asks for numerals even where English spells a count out.
            # For a one-digit value this net is weak -- a stray 6 passes it -- and the strong check
            # stays on the English source above.
            for mirror in sorted((root / "docs" / "i18n").glob(f"*/{path}")):
                if not any(n in mirror.read_text("utf-8") for n in numerals(value)):
                    untranslated.append(f"{c['id']} -> {mirror.relative_to(root)}: no {value}")
    assert not wrong, wrong
    assert not unanchored, unanchored
    assert not absent, absent
    assert not untranslated, untranslated


def test_every_index_names_what_the_repository_has():
    """A directory README is where a contributor looks to find out what already exists, and until now
    nothing checked one against its directory. `claims.json` holds the numbers the documents state and
    `check_links.py` holds the links between them; the gap between those two is a list that has quietly
    stopped listing everything. `test_profile.py` was in neither the table nor the graph of
    tests/README for three days, and `tools/hooks/` was named in no index at all.

    The cost is not cosmetic. An index that undercounts sends the next contributor to write a second
    copy of something that is already here, which is a defect this repository has paid for in code:
    one flood fill, written once in `light` and once in `measure`, because no page said the first one
    existed.

    Four mechanical claims. Every tracked directory is documented. Every table that lists files lists
    all of them. Every public name a table advertises is one its module defines. And a drawing that
    names a set of files names the same set as the table beside it."""
    import ast
    import re
    from pathlib import Path, PurePosixPath

    root = Path(__file__).resolve().parent.parent

    def read(doc: str) -> str:
        return (root / doc).read_text("utf-8")

    # 1. a directory carries its own README, or the one above it names it as a path: `hooks/`, never
    # the bare word inside a sentence about hooks. A passing mention must not stand in for an entry
    tracked = subprocess.run(["git", "-C", str(root), "ls-files"], capture_output=True,
                             text=True, check=True).stdout.split()
    undocumented = []
    for d in sorted({PurePosixPath(f).parent for f in tracked if "/" in f}):
        if (root / d / "README.md").exists():
            continue
        above = root / d.parent / "README.md"
        if above.exists() and re.search(rf"\b{re.escape(d.name)}/", above.read_text("utf-8")):
            continue
        undocumented.append(str(d))

    # 2. a listed file. The row anchor is `| `name` |` at the start of a line, so prose naming a file
    # can neither satisfy a row nor break one. tools/README.md names its scripts in running text
    # instead, which is why that one is asked in one direction: every tool is named, and a name is not
    # held to being a tool
    indexes = (
        ("src/asrai/README.md", r"^\| `([a-z_]+\.py)` \|", "src/asrai", "*.py", True),
        ("tests/README.md", r"^\| `(test_\w+\.py)` \|", "tests", "test_*.py", True),
        ("tools/README.md", r"`(\w+\.py)`", "tools", "*.py", False),
    )
    unlisted, phantom = [], []
    for doc, anchor, folder, glob, both in indexes:
        named = set(re.findall(anchor, read(doc), re.M))
        have = {p.name for p in (root / folder).glob(glob)}
        unlisted += [f"{doc} does not name {n}" for n in sorted(have - named)]
        if both:
            phantom += [f"{doc} names {n}, which {folder}/ does not have" for n in sorted(named - have)]

    # 3. the public surface a table advertises. This is the row that goes stale in the same commit that
    # moves a function out of a module, and the one a reader trusts most: it is read as the module's API
    package = read("src/asrai/README.md")
    for mod in sorted(p.name for p in (root / "src" / "asrai").glob("*.py")):
        cell = re.search(rf"^\| `{re.escape(mod)}` \|[^|]*\|([^|]*)\|", package, re.M)
        if cell is None:
            continue                          # an unlisted module is already an entry in `unlisted`
        public = set()
        for node in ast.parse((root / "src" / "asrai" / mod).read_text("utf-8")).body:
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and not node.name.startswith("_"):
                public.add(node.name)
            bound = (node.targets if isinstance(node, ast.Assign)
                     else [node.target] if isinstance(node, ast.AnnAssign) else [])
            public |= {t.id for t in bound if isinstance(t, ast.Name) and t.id.isupper()}
        phantom += [f"src/asrai/README.md says {mod} exposes {n}, which it does not define"
                    for n in sorted(set(re.findall(r"`(\w+)`", cell.group(1))) - public)]

    # 4. two lists spelled a second time. The MCP table mirrors the tools `server.py` decorates and the
    # tests diagram mirrors the table under it; a second spelling is a second thing to forget
    tools = set(re.findall(r"@_guard\ndef (\w+)\(", read("src/asrai/server.py")))
    mirrored = set(re.findall(r"^\| `(\w+)` \| `asrai", package, re.M))
    drawn = set(re.findall(r"\[(test_\w+)\]", read("tests/README.md")))
    suite = {p.stem for p in (root / "tests").glob("test_*.py")}

    assert not undocumented, f"no README, and the one above does not name it: {undocumented}"
    assert not unlisted, unlisted
    assert not phantom, phantom
    assert tools == mirrored, f"the MCP tool table and server.py disagree: {sorted(tools ^ mirrored)}"
    assert drawn == suite, f"the tests diagram and the test files disagree: {sorted(drawn ^ suite)}"
