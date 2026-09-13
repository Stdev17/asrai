import asyncio
import json
import subprocess
import sys

import numpy as np
import pytest
from PIL import Image, ImageDraw

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
    with pytest.raises(ValueError, match="can only be unknown"):
        records.append(base | {"observations": [{"term_id": "perception.visual_hierarchy", "level": "asserted", "note": "reads first"}]}, log)
    with pytest.raises(ValueError, match="must be L2"):
        records.append(base | {"asset_kind": "screenshot"}, log)
    with pytest.raises(ValueError, match="render_profile_id"):
        records.append(base | {"asset_kind": "svg"}, log)
    pair = {"kind": "pairwise", "evidence_layer": "L1", "term_id": "color.saturation", "a": SHA, "b": "b" * 64,
            "verdict": "prefer_a", "by": "model"}
    with pytest.raises(ValueError, match="order_checked"):
        records.append(pair, log)
    records.append(pair | {"by": "human"}, log)
    assert len(records.read(log)) == 2


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
    assert names == {"vocab_search", "vocab_get", "measure", "record", "lint", "doctor"}
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
