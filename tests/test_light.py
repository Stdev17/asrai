"""light_ledger: a Lambertian disc lit from the upper-left must point there, answer to the lamp placed
there, reject the decoy, mirror with the image, and turn a filled form into verdicts and a record."""
import json

import numpy as np
import pytest
from PIL import Image

from asrai import light, records

BALL = [{"id": "ball", "bbox": [50, 30, 80, 80]}]
UPPER_LEFT = np.array([-1.0, -1.0]) / np.sqrt(2)


def disc(ang_deg, alpha=True, cel=False, flat=False):
    """A 36 px disc at (90, 70) lit from `ang_deg` in the image plane (y down), a white lamp at the
    upper-left and a small cyan decoy at the lower-right; the decoy is nearer, the lamp stronger."""
    W, H = 160, 120
    yy, xx = np.mgrid[:H, :W]
    L = np.array([np.cos(np.radians(ang_deg)) * 0.7071, np.sin(np.radians(ang_deg)) * 0.7071, 0.7071])
    nx, ny = (xx - 90) / 36, (yy - 70) / 36
    inside = nx ** 2 + ny ** 2 <= 1
    nz = np.sqrt(np.clip(1 - nx ** 2 - ny ** 2, 0, 1))
    ndl = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    shade = np.full(ndl.shape, 0.3) if flat else np.where(ndl > 0.45, 0.5, 0.12) if cel else 0.08 + 0.45 * ndl
    srgb = np.where(shade <= 0.0031308, shade * 12.92, 1.055 * shade ** (1 / 2.4) - 0.055)
    rgb = np.zeros((H, W, 3), np.uint8)
    for c, k in enumerate((1.0, 0.92, 0.80)):                       # a warm grey ball on a dark ground
        rgb[..., c] = np.where(inside, srgb * k * 255, 30 if c < 2 else 40).round()
    lamp, decoy = (xx - 18) ** 2 + (yy - 14) ** 2 <= 36, (xx - 150) ** 2 + (yy - 110) ** 2 <= 16
    rgb[lamp], rgb[decoy] = (255, 255, 240), (0, 255, 255)
    if not alpha:
        return Image.fromarray(rgb, "RGB")
    return Image.fromarray(np.dstack([rgb, np.where(inside | lamp | decoy, 255, 0).astype(np.uint8)]), "RGBA")


def scene(path, **kw):
    disc(225, **kw).save(path)
    return path


def test_direction_emitters_fit_key_and_form(tmp_path):
    led = light.ledger(scene(tmp_path / "s.png"), BALL, out_dir=tmp_path / "out")
    assert led == light.ledger(tmp_path / "s.png", BALL, out_dir=tmp_path / "out")
    ball = led["subjects"][0]
    assert ball["mask"] == "alpha" and np.dot(ball["bright_side"]["vector"], UPPER_LEFT) > 0.99
    assert ball["contour_fit"]["r2"] > 0.5 and np.dot(ball["contour_fit"]["vector"], UPPER_LEFT) > 0.99
    lamp, decoy = led["emitters"]                                   # brightest first
    assert lamp["id"] == "e1" and np.hypot(*(np.array(lamp["centroid"]) - (18, 14))) < 2
    assert np.hypot(*(np.array(decoy["centroid"]) - (150, 110))) < 2
    by = {a["emitter"]: a for a in led["agreement"]}
    assert by["e1"]["angle_deg"] < 10 and by["e2"]["angle_deg"] > 120
    assert by["e1"]["irradiance_proxy"] == 1.0 > by["e2"]["irradiance_proxy"]
    assert by["e2"]["distance_px"] < by["e1"]["distance_px"]         # nearer, yet weaker and not pointed at
    assert by["e1"]["hue_delta_deg"] is None and by["e2"]["hue_delta_deg"] > 90
    fit = led["key_fit"]
    assert fit["best"] == "e1" and {h["hypothesis"] for h in fit["hypotheses"]} == {"directional", "e1", "e2"}
    assert next(h for h in fit["hypotheses"] if h["hypothesis"] == "e1")["median_deg"] < 10
    assert (lamp["receivers"], decoy["receivers"]) == (1, 0)
    assert lamp["spill"] is decoy["spill"] is None            # a sprite on transparency has no neighbourhood
    form = led["form"]
    assert form["emitters"] == {"e1": None, "e2": None} and form["style"]["mode"] is None
    assert form["pairs"] == []                                # the measurement decided every pair it lists
    assert {q["path"].split(".")[0].split("[")[0] for q in led["questions"]} == {"emitters", "subjects", "global", "style"}
    assert Image.open(led["overlay"]).size == (160, 120)


def test_answers_phase_gives_verdict_and_record(tmp_path):
    p = scene(tmp_path / "s.png")
    form = light.ledger(p, BALL)["form"]
    form["style"]["mode"] = "physical"
    form["emitters"] = {"e1": "lamp", "e2": "paint"}
    form["subjects"]["cast_shadow"]["no"] = ["ball"]
    form["subjects"]["light_color"]["unknown"] = ["ball"]
    form["global"] = {"key": "yes", "atmosphere": "unknown"}
    led = light.ledger(p, BALL, answers=form, out_dir=tmp_path / "out")
    assert [e["kind"] for e in led["emitters"]] == ["lamp", "paint"]
    assert {a["emitter"] for a in led["agreement"]} == {"e1"}       # the rejected decoy voids its pairs
    v = led["verdict"]["subjects"][0]
    assert (v["expected_key"], v["diffuse"], v["basis"], v["axis"]) == ("e1", "agrees", "measurement", "pass")
    assert (v["specular"], v["cast_shadow"], v["ambient"], v["light_color"], v["color_basis"]) == ("yes", "no", "yes", "unknown", "observer")
    assert led["verdict"]["emitters"] == [{"id": "e1", "kind": "lamp", "receivers": 1, "spill": None, "verdict": "lights"}]
    assert led["verdict"]["axes"]["asset_cohesion"] == "pass"
    assert led["subjects"][0]["highlight"]["hue_shift_from_body_deg"] < 30      # brighter paint, no cast
    assert led["verdict"]["axes"]["direction_compliance"] == "pass" and led["overlay"].endswith(".answered.png")
    rec = led["record"]
    assert rec["observer"]["model"] is None and rec["evidence_layer"] == "L1"
    rec["observer"]["model"] = "test-model"
    assert records.validate(rec) == []
    by_term = {}
    for item in rec["observations"]:
        by_term.setdefault(item["term_id"], []).append(item)
    assert [i["note"][-8:] for i in by_term["material.emission"]] == [" as lamp", "a source"]
    assert by_term["lighting.form_shadow"][0]["level"] == "asserted" and "e1" in by_term["lighting.form_shadow"][0]["note"]
    assert by_term["lighting.cast_shadow"][0]["level"] == "estimated" and by_term["lighting.light_direction"][0]["region"] == "whole_image"
    assert by_term["color.light_color"][0]["level"] == "unknown"          # listed undecided; a plain yes records nothing
    assert "value.highlight" not in by_term


def test_a_confirmed_light_the_frame_does_not_answer_to(tmp_path):
    """Lit from the lower-right, the ball answers to the decoy and ignores the lamp, and nothing near
    the lamp is brighter for it: a source the frame does not respond to, whatever its genre."""
    p = tmp_path / "s.png"
    disc(45, alpha=False).save(p)
    led = light.ledger(p, BALL)
    by_id = {e["id"]: e for e in led["emitters"]}
    assert by_id["e1"]["receivers"] == 0 and by_id["e1"]["spill"]["luminance_gain"] <= 0
    assert by_id["e2"]["receivers"] == 1                       # the decoy, and e3 is the ball's own lit cap
    assert "no brighter" in next(q["question"] for q in led["questions"] if q["path"] == "emitters.e1")
    form = led["form"] | {"emitters": {"e1": "lamp", "e2": "neon", "e3": "paint"}}
    led = light.ledger(p, BALL, answers=form)
    assert [(e["id"], e["verdict"]) for e in led["verdict"]["emitters"]] == [("e1", "lights_nothing"), ("e2", "lights")]
    assert led["verdict"]["axes"] == {"direction_compliance": "fail", "intentional_contrast": "unknown", "asset_cohesion": "fail"}
    notes = [i["note"] for i in led["record"]["observations"] if i["term_id"] == "material.emission"]
    assert notes == ["e1 reads as lamp and nothing in the frame takes its light", "e2 confirmed as neon",
                     "e3 is bright paint, not a source"]
    fake = light.ledger(p, BALL, answers=form | {"style": {"mode": "fake_lighting"}})["verdict"]["axes"]
    assert (fake["asset_cohesion"], fake["intentional_contrast"]) == ("unknown", "warn")   # the style owns it


def test_a_shadow_painted_on_the_wrong_side(tmp_path):
    """A lone sprite, no light to answer to: the lit side points upper-left, so the shaded mass must
    sit lower-right. Painted upper-right instead, it fails on its own, with nothing else to compare."""
    img = np.array(disc(225))
    yy, xx = np.mgrid[:120, :160]
    img[((xx - 18) ** 2 + (yy - 14) ** 2 <= 36) | ((xx - 150) ** 2 + (yy - 110) ** 2 <= 16)] = 0   # lamps away
    img[((xx - 108) ** 2 + (yy - 52) ** 2 <= 144) & (img[..., 3] > 0), :3] = 10
    p = tmp_path / "s.png"
    Image.fromarray(img, "RGBA").save(p)
    led = light.ledger(p, BALL)
    sub = led["subjects"][0]
    assert np.dot(sub["bright_side"]["vector"], UPPER_LEFT) > 0.9
    assert 60 < sub["shadow"]["opposition_deg"] < 130
    assert "ball" not in next(q["question"] for q in led["questions"] if q["path"] == "subjects.cast_shadow")
    form = led["form"] | {"emitters": {e["id"]: "paint" for e in led["emitters"]}}
    v = light.ledger(p, BALL, answers=form)
    row = v["verdict"]["subjects"][0]
    assert (row["cast_shadow"], row["shadow_basis"]) == ("no", "measurement")
    assert v["verdict"]["axes"] == {"direction_compliance": "unknown", "intentional_contrast": "unknown",
                                   "asset_cohesion": "fail"}          # nothing else in the frame can speak
    shadow = [i for i in v["record"]["observations"] if i["term_id"] == "lighting.cast_shadow"]
    assert [(i["level"], i["note"]) for i in shadow] == [("asserted", "the shaded mass of ball does not sit opposite its lit side")]
    listed = light.ledger(p, BALL, answers=form | {"subjects": {"cast_shadow": {"unknown": ["ball"]}}})
    assert listed["verdict"]["subjects"][0]["cast_shadow"] == "unknown"       # the observer overrides


def test_depth_layers_change_the_expected_key(tmp_path):
    """Pushing the lamp three layers back makes the nearer decoy the light to answer to."""
    p = scene(tmp_path / "s.png")
    form = light.ledger(p, [BALL[0] | {"depth": 0}])["form"]
    form["emitters"], form["emitter_depth"] = {"e1": "lamp", "e2": "lamp"}, {"e1": 3}
    v = light.ledger(p, [BALL[0] | {"depth": 0}], answers=form)["verdict"]["subjects"][0]
    assert (v["expected_key"], v["pointed_at"], v["verdict_emitter"], v["diffuse"]) == ("e2", "e1", "e1", "agrees")   # still strong enough
    form["emitter_depth"] = {"e1": 6}
    v = light.ledger(p, [BALL[0] | {"depth": 0}], answers=form)["verdict"]["subjects"][0]
    assert (v["expected_key"], v["verdict_emitter"], v["diffuse"], v["axis"]) == ("e2", "e2", "disagrees", "fail")
    form["emitters"] = {"e1": "lamp", "e2": "neon"}                  # a designed source outranks a decorative one
    v = light.ledger(p, [BALL[0] | {"depth": 0}], answers=form)["verdict"]["subjects"][0]
    assert (v["expected_key"], v["diffuse"]) == ("e1", "agrees")


def test_fake_and_engine_lit_modes(tmp_path):
    p = scene(tmp_path / "s.png")
    base = light.ledger(p, BALL)["form"]
    fake = light.ledger(p, BALL, answers=base | {"style": {"mode": "fake_lighting"}})["verdict"]
    assert (fake["subjects"][0]["expected_key"], fake["subjects"][0]["diffuse"]) == ("directional", "agrees")
    assert fake["axes"]["intentional_contrast"] == "pass"
    engine = light.ledger(p, BALL, answers=base | {"style": {"mode": "engine_lit"}})["verdict"]["subjects"][0]
    assert (engine["diffuse"], engine["axis"]) == ("baked", "warn")
    scene(tmp_path / "flat.png", flat=True)
    flat = light.ledger(tmp_path / "flat.png", BALL, answers=base | {"style": {"mode": "engine_lit"}})
    assert (flat["verdict"]["subjects"][0]["diffuse"], flat["verdict"]["axes"]["direction_compliance"]) == ("flat", "pass")


@pytest.mark.parametrize("alpha,cel", [(True, False), (False, False), (True, True), (False, True)],
                         ids=["lambert-alpha", "lambert-rect", "cel-alpha", "cel-rect"])
def test_estimator_noise_floor_on_every_direction(tmp_path, alpha, cel):
    """Both estimators stay well inside the thresholds the ledger reasons with (surfaces.v1 thresholds)."""
    for ang in range(0, 360, 45):
        disc(ang, alpha=alpha, cel=cel).save(tmp_path / "d.png")
        s = light.ledger(tmp_path / "d.png", [{"id": "d", "bbox": [54, 34, 72, 72]}])["subjects"][0]
        truth = np.array([np.cos(np.radians(ang)), np.sin(np.radians(ang))])
        assert light._angle(s["bright_side"]["vector"], truth) < 5, (ang, s["bright_side"])
        assert light._shadow_measured(s) == alpha, (ang, s["shadow"])   # a box on a uniform ground has no
        if alpha:                                                       # shaded mass of its own to place
            assert s["shadow"]["opposition_deg"] < 10, (ang, s["shadow"])
        if alpha:
            assert s["contour_fit"]["r2"] > 0.5 and light._angle(s["contour_fit"]["vector"], truth) < 10, (ang, s["contour_fit"])


def test_mirror_flips_x_only(tmp_path):
    p = scene(tmp_path / "s.png")
    a = light.ledger(p, BALL)["subjects"][0]["bright_side"]["vector"]
    m = light.ledger(p, BALL, mirror=True)
    b = m["subjects"][0]["bright_side"]["vector"]
    assert m["mirrored"] and abs(a[0] + b[0]) < 0.05 and abs(a[1] - b[1]) < 0.05
    assert m["subjects"][0]["bbox"] == [30, 30, 80, 80]


def test_no_alpha_and_no_subjects(tmp_path):
    img = np.full((60, 90, 3), 40, np.uint8)
    img[10:20, 60:75] = 255
    Image.fromarray(img, "RGB").save(tmp_path / "f.png")
    led = light.ledger(tmp_path / "f.png")
    assert led["subjects"] == [] and led["key_fit"] is None and led["overlay"] is None
    assert [e["kind"] for e in led["emitters"]] == ["proposed"] and led["form"]["pairs"] == []


def test_capture_boxes_become_subjects(tmp_path):
    p = scene(tmp_path / "frame.png")
    cap = tmp_path / "capture.json"
    cap.write_text(json.dumps({"composed_of": [{"game_object": "Ball", "screen_bbox": [50, 30, 80, 80], "depth": 2},
                                               {"game_object": "Ball", "screen_bbox": [0, 0, 8, 8]},
                                               {"game_object": "Ghost"}]}), "utf-8")
    subs = light.ledger(p, capture=str(cap))["subjects"]
    assert [(s["id"], s["depth"]) for s in subs] == [("Ball", 2), ("Ball_2", None)]


def test_malformed_input_raises_value_error(tmp_path):
    p = scene(tmp_path / "s.png")
    for bad in ("ball", [{"id": "b"}], [{"id": "b", "bbox": [0, 0, 0, 5]}], [{"id": "b", "bbox": [1.5, 0, 5, 5]}],
                [{"id": "b", "bbox": [500, 500, 5, 5]}], [{"id": "b", "bbox": [0, 0, 5, 5]}] * 2, [7],
                [{"id": "b", "bbox": [0, 0, 5, 5], "depth": -1}]):
        with pytest.raises(ValueError):
            light.ledger(p, bad)
    for bad in ("yes", {"emitters": {"zz": "lamp"}}, {"emitters": {"e1": "sun"}}, {"style": {"mode": "magic"}},
                {"pairs": [{"subject": "ball", "emitter": "e1", "surface": "diffuse", "answer": "maybe"}]},
                {"subjects": {"cast_shadow": {"no": ["ghost"]}}}, {"global": {"key": "yes!"}}, {"emitter_depth": {"e1": 1.5}}):
        with pytest.raises(ValueError):
            light.ledger(p, BALL, answers=bad)
