"""light_ledger: a Lambertian disc lit from the upper-left must point there, answer to the lamp placed
there, reject the decoy, mirror with the image, and turn a filled form into verdicts and a record."""
import json

import numpy as np
import pytest
from PIL import Image

from asrai import config, light, records, run

# The bound the estimators are held to. Registered in claims.json and stated in docs/spec.md,
# surfaces.v1.json and light.py's own docstring: moving any one of them fails the suite.
BRIGHT_SIDE_NOISE_DEG = 4
CONTOUR_FIT_NOISE_DEG = 8
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
    led = run.ledger(scene(tmp_path / "s.png"), BALL, out_dir=tmp_path / "out")
    assert led == run.ledger(tmp_path / "s.png", BALL, out_dir=tmp_path / "out")
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
    form = run.ledger(p, BALL)["form"]
    form["style"]["mode"] = "physical"
    form["emitters"] = {"e1": "lamp", "e2": "paint"}
    form["subjects"]["cast_shadow"] = {"no": ["ball"]}
    form["subjects"]["light_color"] = {"unknown": ["ball"]}
    form["subjects"]["specular"] = {"no": [], "unknown": []}     # looked at, nothing to except
    form["global"] = {"key": "yes", "atmosphere": "unknown"}
    led = run.ledger(p, BALL, answers=form, out_dir=tmp_path / "out")
    assert [e["kind"] for e in led["emitters"]] == ["lamp", "paint"]
    assert {a["emitter"] for a in led["agreement"]} == {"e1"}       # the rejected decoy voids its pairs
    v = led["verdict"]["subjects"][0]
    assert (v["expected_key"], v["diffuse"], v["basis"], v["axis"]) == ("e1", "agrees", "measurement", "pass")
    # ambient is neither: the form came back without a word on it, so it is unanswered, not agreed
    assert (v["specular"], v["cast_shadow"], v["ambient"], v["light_color"], v["color_basis"]) == ("yes", "no", "unknown", "unknown", "observer")
    assert led["verdict"]["emitters"] == [{"id": "e1", "kind": "lamp", "receivers": 1, "spill": None, "verdict": "lights"}]
    assert led["verdict"]["axes"]["asset_cohesion"] == "pass"
    assert led["subjects"][0]["highlight"]["hue_shift_from_body_deg"] < 30      # brighter paint, no cast
    assert led["verdict"]["axes"]["direction_compliance"] == "pass" and led["overlay"].endswith(".answered.png")
    rec = led["record"]
    # the run signs what it hands out, with the configured observer and not one a family invented, and
    # it is valid before it leaves: the tool told to store it is never the first thing to look at it
    assert rec["observer"] == config.DEFAULTS["observer"] and rec["evidence_layer"] == "L1"
    assert records.validate(rec) == []
    mine = {"mode": "api", "model": "test-model", "prompt_rev": "v2"}
    assert run.ledger(p, BALL, answers=form, observer=mine)["record"]["observer"] == mine
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
    led = run.ledger(p, BALL)
    by_id = {e["id"]: e for e in led["emitters"]}
    assert by_id["e1"]["receivers"] == 0 and by_id["e1"]["spill"]["luminance_gain"] <= 0
    assert by_id["e2"]["receivers"] == 1                       # the decoy, and e3 is the ball's own lit cap
    assert "no brighter" in next(q["question"] for q in led["questions"] if q["path"] == "emitters.e1")
    form = led["form"] | {"emitters": {"e1": "lamp", "e2": "neon", "e3": "paint"}}
    led = run.ledger(p, BALL, answers=form)
    assert [(e["id"], e["verdict"]) for e in led["verdict"]["emitters"]] == [("e1", "lights_nothing"), ("e2", "lights")]
    assert led["verdict"]["axes"] == {"direction_compliance": "fail", "intentional_contrast": "unknown", "asset_cohesion": "fail"}
    notes = [i["note"] for i in led["record"]["observations"] if i["term_id"] == "material.emission"]
    assert notes == ["e1 reads as lamp and nothing in the frame takes its light", "e2 confirmed as neon",
                     "e3 is bright paint, not a source"]
    fake = run.ledger(p, BALL, answers=form | {"style": {"mode": "fake_lighting"}})["verdict"]["axes"]
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
    led = run.ledger(p, BALL)
    sub = led["subjects"][0]
    assert np.dot(sub["bright_side"]["vector"], UPPER_LEFT) > 0.9
    assert 60 < sub["shadow"]["opposition_deg"] < 130
    assert "ball" not in next(q["question"] for q in led["questions"] if q["path"] == "subjects.cast_shadow")
    form = led["form"] | {"emitters": {e["id"]: "paint" for e in led["emitters"]}}
    v = run.ledger(p, BALL, answers=form)
    row = v["verdict"]["subjects"][0]
    assert (row["cast_shadow"], row["shadow_basis"]) == ("no", "measurement")
    assert v["verdict"]["axes"] == {"direction_compliance": "unknown", "intentional_contrast": "unknown",
                                   "asset_cohesion": "fail"}          # nothing else in the frame can speak
    shadow = [i for i in v["record"]["observations"] if i["term_id"] == "lighting.cast_shadow"]
    assert [(i["level"], i["note"]) for i in shadow] == [("asserted", "the shaded mass of ball does not sit opposite its lit side")]
    listed = run.ledger(p, BALL, answers=form | {"subjects": {"cast_shadow": {"unknown": ["ball"]}}})
    assert listed["verdict"]["subjects"][0]["cast_shadow"] == "unknown"       # the observer overrides


def test_depth_layers_change_the_expected_key(tmp_path):
    """Pushing the lamp three layers back makes the nearer decoy the light to answer to."""
    p = scene(tmp_path / "s.png")
    form = run.ledger(p, [BALL[0] | {"depth": 0}])["form"]
    form["emitters"], form["emitter_depth"] = {"e1": "lamp", "e2": "lamp"}, {"e1": 3}
    v = run.ledger(p, [BALL[0] | {"depth": 0}], answers=form)["verdict"]["subjects"][0]
    assert (v["expected_key"], v["pointed_at"], v["verdict_emitter"], v["diffuse"]) == ("e2", "e1", "e1", "agrees")   # still strong enough
    form["emitter_depth"] = {"e1": 6}
    v = run.ledger(p, [BALL[0] | {"depth": 0}], answers=form)["verdict"]["subjects"][0]
    assert (v["expected_key"], v["verdict_emitter"], v["diffuse"], v["axis"]) == ("e2", "e2", "disagrees", "fail")
    form["emitters"] = {"e1": "lamp", "e2": "neon"}                  # a designed source outranks a decorative one
    v = run.ledger(p, [BALL[0] | {"depth": 0}], answers=form)["verdict"]["subjects"][0]
    assert (v["expected_key"], v["diffuse"]) == ("e1", "agrees")


def test_fake_and_engine_lit_modes(tmp_path):
    p = scene(tmp_path / "s.png")
    base = run.ledger(p, BALL)["form"]
    fake = run.ledger(p, BALL, answers=base | {"style": {"mode": "fake_lighting"}})["verdict"]
    assert (fake["subjects"][0]["expected_key"], fake["subjects"][0]["diffuse"]) == ("directional", "agrees")
    assert fake["axes"]["intentional_contrast"] == "pass"
    engine = run.ledger(p, BALL, answers=base | {"style": {"mode": "engine_lit"}})["verdict"]["subjects"][0]
    assert (engine["diffuse"], engine["axis"]) == ("baked", "warn")
    scene(tmp_path / "flat.png", flat=True)
    # its own form: a flat disc proposes a different emitter set, and a form is filled for one image
    flat_form = run.ledger(tmp_path / "flat.png", BALL)["form"]
    flat = run.ledger(tmp_path / "flat.png", BALL, answers=flat_form | {"style": {"mode": "engine_lit"}})
    assert (flat["verdict"]["subjects"][0]["diffuse"], flat["verdict"]["axes"]["direction_compliance"]) == ("flat", "pass")


@pytest.mark.parametrize("alpha,cel", [(True, False), (False, False), (True, True), (False, True)],
                         ids=["lambert-alpha", "lambert-rect", "cel-alpha", "cel-rect"])
def test_estimator_noise_floor_on_every_direction(tmp_path, alpha, cel):
    """Both estimators stay well inside the thresholds the ledger reasons with (surfaces.v1 thresholds)."""
    for ang in range(0, 360, 45):
        disc(ang, alpha=alpha, cel=cel).save(tmp_path / "d.png")
        s = run.ledger(tmp_path / "d.png", [{"id": "d", "bbox": [54, 34, 72, 72]}])["subjects"][0]
        truth = np.array([np.cos(np.radians(ang)), np.sin(np.radians(ang))])
        assert light._angle(s["bright_side"]["vector"], truth) < BRIGHT_SIDE_NOISE_DEG, (ang, s["bright_side"])
        assert light._shadow_measured(s) == alpha, (ang, s["shadow"])   # a box on a uniform ground has no
        if alpha:                                                       # shaded mass of its own to place
            assert s["shadow"]["opposition_deg"] < 10, (ang, s["shadow"])
        if alpha:
            assert s["contour_fit"]["r2"] > 0.5 and light._angle(s["contour_fit"]["vector"], truth) < CONTOUR_FIT_NOISE_DEG, (ang, s["contour_fit"])


def test_mirror_flips_x_only(tmp_path):
    p = scene(tmp_path / "s.png")
    a = run.ledger(p, BALL)["subjects"][0]["bright_side"]["vector"]
    m = run.ledger(p, BALL, mirror=True)
    b = m["subjects"][0]["bright_side"]["vector"]
    assert m["mirrored"] and abs(a[0] + b[0]) < 0.05 and abs(a[1] - b[1]) < 0.05
    assert m["subjects"][0]["bbox"] == [30, 30, 80, 80]


def test_a_lone_sprite_is_its_own_subject_and_an_unfilled_form_is_a_verdict(tmp_path):
    """The first reviewer's path: hand over one file, hand the form back untouched, read what the
    measurement alone decided. No boxes, no emitter kinds, no vocabulary."""
    p = scene(tmp_path / "s.png")
    led = run.ledger(p)
    asset = led["subjects"][0]
    assert [s["id"] for s in led["subjects"]] == ["asset"] and asset["mask"] == "alpha"
    assert asset["bbox"] == [12, 8, 143, 107]                  # the whole silhouette: disc, lamp and decoy
    v = run.ledger(p, answers=led["form"])["verdict"]        # returned unfilled
    # nobody said what the two bright blobs are, so they are held, not dropped: the measurement still
    # answers on its own, and the axis says which half of the frame nobody looked at
    assert v["mode"] == "physical"
    assert [(e["id"], e["verdict"]) for e in v["emitters"]] == [("e1", "unclassified"), ("e2", "unclassified")]
    row = v["subjects"][0]
    assert (row["diffuse"], row["cast_shadow"], row["shadow_basis"]) == ("unknown", "yes", "measurement")
    assert v["axes"] == {"direction_compliance": "unknown", "intentional_contrast": "unknown",
                         "asset_cohesion": "warn"}
    assert run.ledger(p, answers={})["verdict"] == v          # an empty object says the same thing


def test_an_unanswered_surface_is_unknown_and_an_answered_one_excepts_only_what_it_lists(tmp_path):
    """Silence is not agreement, at the answer contract itself. Every subject surface is issued null;
    a surface the observer never wrote on cannot put a subject at `yes`, and one they did write on
    answers for every subject it does not except. This shipped the other way round: the form came with
    two empty exception lists per surface and the verdict fell through to `yes`, so the reviewer above
    -- who is told to hand the form back untouched -- was handed a pass on five surfaces nobody looked
    at. The surface the measurement owns still decides itself, filled or not."""
    p = scene(tmp_path / "s.png")
    led = run.ledger(p)
    assert led["form"]["subjects"] == dict.fromkeys(
        ("specular", "light_color", "cast_shadow", "ambient", "rim", "albedo"))
    row = run.ledger(p, answers=led["form"])["verdict"]["subjects"][0]
    assert [row[s] for s in ("specular", "light_color", "ambient", "rim", "albedo")] == ["unknown"] * 5
    assert (row["cast_shadow"], row["shadow_basis"]) == ("yes", "measurement")

    answered = led["form"] | {"subjects": {"rim": {"no": [], "unknown": []}, "ambient": {"no": ["asset"]}}}
    row = run.ledger(p, answers=answered)["verdict"]["subjects"][0]
    assert (row["rim"], row["ambient"], row["albedo"]) == ("yes", "no", "unknown")


def test_the_reader_with_no_training_gets_a_sentence_and_the_verdict_does_not_move(tmp_path):
    """spec.md section 1 owes reader one an id, a box, a direction, in a sentence, and requires that
    `unknown` never read as fine. It also fixes the direction of authority: expression is a projection
    of a verdict, so producing it may not change one. That is structural here — `sentences` takes the
    finished result and returns strings — and this pins it, because the cheap way to add a profile
    later is to thread it into `ledger`, which is exactly what must not happen."""
    disc(45).save(tmp_path / "u.png")                     # lit from the lower right, lamp at the upper left
    form = run.ledger(tmp_path / "u.png", BALL)["form"]
    form["emitters"] = {"e1": "lamp", "e2": "paint"}
    out = run.ledger(tmp_path / "u.png", BALL, answers=form, out_dir=tmp_path / "o")
    before = json.dumps(out["verdict"], sort_keys=True)
    said = light.sentences(out)
    assert json.dumps(out["verdict"], sort_keys=True) == before      # expression yields: it reads, never writes

    disagreement = next(s for s in said if "lit side" in s)
    assert "ball" in disagreement and "50,30 to 80,80" in disagreement and "lower right" in disagreement
    hold = next(s for s in said if "Nobody has decided" in s)
    assert "not the same as fine" in hold                            # silence is not agreement, said out loud

    # no vocabulary and no evidence word reaches this reader: they have neither
    text = " ".join(said)
    assert not any(i["term_id"] in text for i in out["record"]["observations"])
    assert not any(w in text for w in ("asserted", "estimated", "unknown", "observer", "measurement"))

    # a confirmed light whose surroundings could not be read is not an unclassified blob, and an
    # unfilled form is not a measurement that failed. Collapsing either pair is the defect this file
    # has now carried three times
    assert next(s for s in said if s.startswith("e1")).endswith("too bright to read, so nothing could be checked against it.")
    lone = run.ledger(scene(tmp_path / "s.png", flat=True))   # no shading to place a shaded mass by
    flat = light.sentences(run.ledger(tmp_path / "s.png", answers=lone["form"]))
    assert any("too faint to measure" in s for s in flat) and any("no one has looked" in s for s in flat)

    # phase one has no verdict to project, and an empty reading would read as a clean one
    assert light.sentences(lone) == ["Nothing has been judged yet. This is the measurement half; the "
                                     "form it returned has to be answered before anything here can pass or fail."]
    assert "sentences" not in light.for_reader(lone, None)           # no profile is the default
    assert light.for_reader(out, "artist")["verdict"] is out["verdict"]   # the same object, unwrapped
    with pytest.raises(ValueError, match="unknown profile"):
        light.sentences(out, "art director")


def test_three_profiles_say_one_verdict_three_ways_and_none_of_them_moves_it(tmp_path):
    """The gate the 2026-09-17 review specifies: a profile is a view, so one asset and one set of
    answers must produce the same verdict under every profile. What differs is the saying. The scene is
    in the contested band deliberately, because that is where all four axes have something to do."""
    disc(180).save(tmp_path / "a.png")                    # 37.9 degrees off: too far to pass, too close to fail
    form = run.ledger(tmp_path / "a.png", BALL)["form"]
    form["emitters"] = {"e1": "lamp", "e2": "paint"}
    form["subjects"] = {"ambient": {"no": ["ball"]}}
    out = run.ledger(tmp_path / "a.png", BALL, answers=form, out_dir=tmp_path / "o")

    frozen = json.dumps(out["verdict"], sort_keys=True), json.dumps(out["record"], sort_keys=True)
    said = {p["id"]: light.sentences(out, p["id"]) for p in light.profiles()["profiles"]}
    assert (json.dumps(out["verdict"], sort_keys=True), json.dumps(out["record"], sort_keys=True)) == frozen
    assert len({tuple(v) for v in said.values()}) == 3          # three readings, and they are not the same

    band = {k: next(s for s in v if "lit side" in s) for k, v in said.items()}
    assert "(observer)" in band["artist"] and "37.875 degrees" in band["art_director"]
    assert "(" not in band["untrained"].removeprefix("The lit side of ball (box 50,30 to 80,80)")
    assert all("nobody has ruled" in s for s in band.values())  # the band is named to every reader

    # `assume` lets a line carry the term id; `avoid` may not, because that reader cannot use one
    wrong = {k: next(s for s in v if "missing or inconsistent" in s) for k, v in said.items()}
    assert "lighting.ambient" in wrong["artist"] and "lighting.ambient" not in wrong["untrained"]

    # silence on what the measurement settled, for the one reader spec section 1 owes it to
    disc(225).save(tmp_path / "b.png")                    # dead on: the measurement decides alone
    f2 = run.ledger(tmp_path / "b.png", BALL)["form"]
    f2["emitters"] = {"e1": "lamp", "e2": "paint"}
    settled = run.ledger(tmp_path / "b.png", BALL, answers=f2, out_dir=tmp_path / "o2")
    assert any("agrees with e1" in s for s in light.sentences(settled, "untrained"))
    assert not any("agrees with e1" in s for s in light.sentences(settled, "art_director"))
    assert any("no one has looked" in s for s in light.sentences(settled, "art_director"))


def test_the_corpus_overrides_the_profile_on_vocabulary_and_on_nothing_else(tmp_path):
    """The overlay is the adaptive half: a term this corpus has written about is what this team says
    out loud, so it reaches even the reader the profile tells us has no vocabulary. The hundreds nobody
    here has used stay out, and a reader who needs the canonical term asks an artist.

    It overrides that one axis. The evidence is which terms a corpus wrote; what to suppress and what
    to enrich are not in it, and reading them out of it would be an inference the evidence never made."""
    disc(180).save(tmp_path / "a.png")
    form = run.ledger(tmp_path / "a.png", BALL)["form"]
    form["emitters"] = {"e1": "lamp", "e2": "paint"}
    form["subjects"] = {"ambient": {"no": ["ball"]}}
    out = run.ledger(tmp_path / "a.png", BALL, answers=form, out_dir=tmp_path / "o")

    plain = next(s for s in light.sentences(out, "untrained") if "missing or inconsistent" in s)
    assert "lighting.ambient" not in plain                     # nobody here has used it

    seen = {"term:lighting.ambient": {"state": "used", "evidence": ["observation_x"], "at": None}}
    named = light.sentences(out, "untrained", seen)
    assert "lighting.ambient" in next(s for s in named if "missing or inconsistent" in s)
    # a term the corpus has not written about is still plain, in the same sentence-set
    assert "value.highlight" not in " ".join(named)

    # the other three axes do not move: the art director still loses what the measurement settled and
    # still receives the angle, whatever the corpus happens to have written about
    band = next(s for s in light.sentences(out, "art_director", seen) if "lit side" in s)
    assert "37.875 degrees" in band and "(observer)" not in band
    assert light.sentences(out, "artist", seen) == light.sentences(out, "artist")   # already `assume`

    assert json.dumps(out["verdict"], sort_keys=True) == json.dumps(
        light.for_reader(out, "untrained", seen)["verdict"], sort_keys=True)


def test_no_alpha_and_no_subjects(tmp_path):
    img = np.full((60, 90, 3), 40, np.uint8)
    img[10:20, 60:75] = 255
    Image.fromarray(img, "RGB").save(tmp_path / "f.png")
    led = run.ledger(tmp_path / "f.png")
    assert led["subjects"] == [] and led["key_fit"] is None and led["overlay"] is None
    assert [e["kind"] for e in led["emitters"]] == ["proposed"] and led["form"]["pairs"] == []


def test_capture_boxes_become_subjects(tmp_path):
    p = scene(tmp_path / "frame.png")
    cap = tmp_path / "capture.json"
    cap.write_text(json.dumps({"composed_of": [{"game_object": "Ball", "screen_bbox": [50, 30, 80, 80], "depth": 2},
                                               {"game_object": "Ball", "screen_bbox": [0, 0, 8, 8]},
                                               {"game_object": "Ghost"}]}), "utf-8")
    subs = run.ledger(p, capture=str(cap))["subjects"]
    assert [(s["id"], s["depth"]) for s in subs] == [("Ball", 2), ("Ball_2", None)]


def test_a_capture_says_what_it_could_not_read(tmp_path):
    """A Unity script that writes `bbox` where the contract says `screen_bbox` used to cost three of four
    subjects in silence, and the axes then spoke for a quarter of the frame as if it were the frame."""
    p = tmp_path / "s.png"
    disc(45, alpha=False).save(p)
    cap = tmp_path / "capture.json"
    cap.write_text(json.dumps({"engine": "unity", "composed_of": [
        {"game_object": "Hero", "screen_bbox": [50, 30, 80, 80]},
        {"game_object": "Crate", "bbox": [10, 10, 20, 20]},
        {"game_object": "Lamp", "screen_bbox": [5, 5, -4, 9]},
        {"game_object": "Barrel"}]}), "utf-8")
    led = run.ledger(p, None, str(cap))
    assert [s["id"] for s in led["subjects"]] == ["Hero"]
    assert (led["capture"]["declared"], led["capture"]["measured"]) == (4, 1), led["capture"]
    assert [s["id"] for s in led["capture"]["skipped"]] == ["Crate", "Lamp", "Barrel"], led["capture"]


def test_malformed_input_raises_value_error(tmp_path):
    p = scene(tmp_path / "s.png")
    for bad in ("ball", [{"id": "b"}], [{"id": "b", "bbox": [0, 0, 0, 5]}], [{"id": "b", "bbox": [1.5, 0, 5, 5]}],
                [{"id": "b", "bbox": [500, 500, 5, 5]}], [{"id": "b", "bbox": [0, 0, 5, 5]}] * 2, [7],
                [{"id": "b", "bbox": [0, 0, 5, 5], "depth": -1}]):
        with pytest.raises(ValueError):
            run.ledger(p, bad)
    for bad in ("yes", {"emitters": {"zz": "lamp"}}, {"emitters": {"e1": "sun"}}, {"style": {"mode": "magic"}},
                {"style": ["physical"]},   # a wrong type, not a wrong value: the check precedes the read
                {"pairs": [{"subject": "ball", "emitter": "e1", "surface": "diffuse", "answer": "maybe"}]},
                {"subjects": {"cast_shadow": {"no": ["ghost"]}}}, {"global": {"key": "yes!"}}, {"emitter_depth": {"e1": 1.5}}):
        with pytest.raises(ValueError):
            run.ledger(p, BALL, answers=bad)


# --- perturbations reported from production pipelines -------------------------------------------
# Each is a defect that ships, not a stress test: the default URP post-process volume carries bloom
# and a vignette, assets come back from chat and trackers re-encoded, and an export written in the
# wrong colour space crushes its own shadows. Every one of these used to move a slot.

def _vignette(a, k=0.15):
    """The default post-process volume: the frame corners darken. A tenth of it is invisible to an eye."""
    H, W = a.shape[:2]
    yy, xx = np.mgrid[:H, :W]
    r = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2)) / np.sqrt(2)
    f = (1 - k * r ** 2)[..., None]
    return np.dstack([a[..., :3] * f, a[..., 3:]]) if a.shape[2] == 4 else a * f


def _crushed(a):
    """An sRGB export sampled as linear, then handed over through a tracker: the ground lands on the
    bottom few code values and the codec's ringing around a bright decal outweighs any real spill."""
    import io
    x = np.dstack([a[..., :3] ** 2.2, a[..., 3:]]) if a.shape[2] == 4 else a ** 2.2
    buf = io.BytesIO()
    Image.fromarray((np.clip(x[..., :3], 0, 1) * 255).round().astype(np.uint8), "RGB").save(buf, "JPEG", quality=60)
    return np.asarray(Image.open(buf).convert("RGB")).astype(np.float64) / 255


def _write(path, fn, alpha=True):
    a = np.asarray(disc(225, alpha=alpha)).astype(np.float64) / 255
    out = np.clip(fn(a) * 255, 0, 255).round().astype(np.uint8)
    Image.fromarray(out, "RGBA" if out.shape[2] == 4 else "RGB").save(path)
    return path


def test_a_vignette_is_not_a_shaded_mass(tmp_path):
    """The bottom decile of a box in a file without alpha is the ground behind the subject, and any
    frame-wide gradient turns that ground into a confident direction. A vignette nobody would call a
    defect used to put a confident shaded mass on a ball it never touched, pointing near its lit side:
    an asserted yes about the background. Alpha says which pixels are the subject; nothing else does.
    What it measured is in docs/CHECKPOINT.md; no number here is asserted by anything below."""
    for k in (0.0, 0.15, 0.55):
        flat = run.ledger(_write(tmp_path / f"r{k}.png", lambda a: _vignette(a, k), alpha=False), BALL)["subjects"][0]
        assert flat["mask"] == "bbox" and flat["shadow"] is None, (k, flat["shadow"])
        # under alpha the same gradient only bends the shaded mass: a heavy vignette costs 19 deg, which
        # leaves the band the measurement settles and hands the subject to the observer, never to a no
        sprite = run.ledger(_write(tmp_path / f"a{k}.png", lambda a: _vignette(a, k)))["subjects"][0]
        opp = sprite["shadow"]["opposition_deg"]
        assert light._shadow_measured(sprite) and opp < light.DISAGREE_DEG, (k, sprite["shadow"])
        assert (opp <= light.KEY_TOLERANCE_DEG) == (k < 0.5), (k, opp)


def test_a_light_nobody_could_check_never_passes_for_cohesion(tmp_path):
    """A confirmed light whose neighbourhood cannot be read is not a light that passed. Two ways to lose
    it: a crushed export, and a sprite on transparency that has no neighbourhood at all. Either way the
    frame reports no dark emitter because it measured none, which is warn and never pass."""
    for name, fn, alpha, subs in (("crushed", _crushed, False, BALL), ("sprite", lambda a: a, True, None)):
        p = _write(tmp_path / f"{name}.png", fn, alpha=alpha)
        form = run.ledger(p, subs)["form"]
        form["style"]["mode"] = "physical"
        form["emitters"] = {e["id"]: "neon" for e in run.ledger(p, subs)["emitters"]}
        v = run.ledger(p, subs, answers=form)["verdict"]
        assert any(e["verdict"] == "unreadable" and not e["spill"] for e in v["emitters"]), (name, v["emitters"])
        assert v["axes"]["asset_cohesion"] == "warn", (name, v["axes"])


def test_a_hold_is_not_a_rejection(tmp_path):
    """An observer who cannot classify a blob must not thereby clear the frame. Same pixels as the decoy
    scene, one answer apart: calling e1 a lamp exposes a source nothing in the frame takes light from,
    so "I cannot tell" was the one answer that made it disappear. unknown is a hold, not a finding."""
    p = tmp_path / "s.png"
    disc(45, alpha=False).save(p)
    seen = {}
    for kind in ("lamp", "unknown"):
        form = run.ledger(p, BALL)["form"] | {"emitters": {"e1": kind, "e2": "neon", "e3": "paint"}}
        v = run.ledger(p, BALL, answers=form)["verdict"]
        seen[kind] = (v["axes"]["asset_cohesion"], {e["id"]: e["verdict"] for e in v["emitters"]})
    assert seen["lamp"] == ("fail", {"e1": "lights_nothing", "e2": "lights"}), seen
    assert seen["unknown"][1] == {"e2": "lights", "e1": "unclassified"}, seen   # held, not dropped
    assert seen["unknown"][0] == "warn", seen                                   # and it never reaches pass


def test_a_form_belongs_to_the_run_it_was_filled_for(tmp_path):
    """Every answer is addressed to an id, and an id belongs to the run that assigned it. Emitter ids are
    ordinal by brightness, so under a vignette the lamp stopped being e1 and a sheet answered for one
    export silently re-bound to other blobs. The file's digest alone did not cover the other ways a
    run rebinds them: the same bytes measured with other boxes answered about pixels nobody had looked
    at, and `mirror` -- the one operation here that reorders emitters on purpose -- was invisible to it."""
    p, q = scene(tmp_path / "s.png"), _write(tmp_path / "v.png", _vignette, alpha=False)
    form = run.ledger(p, BALL)["form"]
    assert form["run_sha256"] == run.ledger(p, BALL)["form"]["run_sha256"]   # same arguments, same run
    assert run.ledger(p, BALL, answers=form)["verdict"]["mode"] == "physical"
    elsewhere = [{"id": "ball", "bbox": [0, 0, 30, 30]}]                       # the id stays, the pixels move
    for path, subjects, mirror in ((q, BALL, False), (p, elsewhere, False), (p, BALL, True)):
        with pytest.raises(ValueError, match="different run"):
            run.ledger(path, subjects, mirror=mirror, answers=form)
    form.pop("run_sha256")                        # a hand-written sheet may omit it
    assert run.ledger(q, BALL, answers=form)["verdict"]["mode"] == "physical"


def test_the_run_owns_the_record_and_writes_none_when_nothing_was_observed(tmp_path):
    """A record says which asset, at which evidence layer and scale, and who observed. All four are
    facts about the run, so the run assembles it and validates it before it leaves -- the tool told to
    store a record is not the first thing to look at one.

    A run that observed nothing writes no record. An append-only corpus is worse off holding a row that
    observed nothing, and `None` says so where an absent key would read as a clean one. An unfilled form
    is that run today: nothing is confirmed as a light, so there is nothing for a subject to be right or
    wrong about, and the axes say `unknown`.

    `asset_cohesion` is `warn` here and nothing backs it in the record, because nobody classified the
    lamp. That is the finding the next slice closes; this one only stops an invalid record leaving."""
    import asrai
    from pathlib import Path as P
    p = scene(tmp_path / "s.png", flat=True)
    out = run.ledger(p, BALL, answers=run.ledger(p, BALL)["form"])
    assert out["record"] is None                      # the key is there; what is absent is the record
    assert "observations" not in out and "context" not in out    # the family's half, consumed by the run

    # nothing but config and records knows what an observer is made of, so no family can write one:
    # a null under a required field reached the corpus the last time one did
    pkg = P(asrai.__file__).parent
    named = sorted(m.name for m in pkg.glob("*.py") if "prompt_rev" in m.read_text("utf-8"))
    assert named == ["config.py", "records.py"], named


def test_only_the_run_owner_opens_the_asset_and_only_one_source_names_the_subjects(tmp_path):
    """The run owns the asset so that two families cannot disagree about it, and neither half of that
    holds by itself. A family that opened the file would measure its own pixels under this run's subject
    ids; a caller who named the subjects twice would have one source measured and the other filed as the
    evidence layer. Both were held only by the text of the code until this ran."""
    import asrai
    from pathlib import Path
    pkg = Path(asrai.__file__).parent
    opens = sorted(m.name for m in pkg.glob("*.py")
                   if "measure.load(" in m.read_text("utf-8") or "Image.open(" in m.read_text("utf-8"))
    assert opens == ["measure.py", "run.py"], opens   # measure decodes, run decides when; no family does

    p = scene(tmp_path / "s.png")
    cap = tmp_path / "capture.json"
    cap.write_text(json.dumps({"composed_of": [{"game_object": "ball", "screen_bbox": [40, 40, 40, 40]}]}), "utf-8")
    assert run.ledger(p, capture=str(cap))["subjects"][0]["id"] == "ball"     # one source: read
    with pytest.raises(ValueError, match="both say what the subjects are"):
        run.ledger(p, BALL, capture=str(cap))


def _disc_mask(path, size, origin=(0, 0)):
    """A layer export: the disc's own pixels, alpha 255, everything else transparent."""
    W, H = size
    ox, oy = origin
    yy, xx = np.mgrid[:H, :W]
    inside = ((xx + ox - 90) / 36) ** 2 + ((yy + oy - 70) / 36) ** 2 <= 1
    rgba = np.zeros((H, W, 4), np.uint8)
    rgba[..., 3] = np.where(inside, 255, 0)
    Image.fromarray(rgba, "RGBA").save(path)
    return str(path)


def test_a_subject_mask_gives_a_box_the_pixels_it_is_made_of(tmp_path):
    """A box is the cheapest way to point at a thing and the most expensive to measure: whatever else is
    in it is measured as the subject. On a file without alpha that costs the shaded mass and the contour
    fit entirely. A layer export -- which a hand-drawn package already has, and which no segmentation can
    recover, since a rock and the sand under one warm light share their chroma -- gives them back."""
    p = scene(tmp_path / "s.png", alpha=False)
    bare = run.ledger(p, BALL)["subjects"][0]
    assert (bare["mask"], bare["shadow"], bare["contour_fit"]) == ("bbox", None, None)

    for tag, size, origin in (("canvas", (160, 120), (0, 0)), ("box", (80, 80), (50, 30))):
        m = _disc_mask(tmp_path / f"{tag}.png", size, origin)
        s = run.ledger(p, [{"id": "ball", "bbox": [50, 30, 80, 80], "mask": m}])["subjects"][0]
        assert s["mask"] == "given" and s["pixels"] < bare["pixels"], (tag, s["pixels"])
        assert np.dot(s["bright_side"]["vector"], UPPER_LEFT) > 0.99, (tag, s["bright_side"])
        assert light._shadow_measured(s) and s["shadow"]["opposition_deg"] < 10, (tag, s["shadow"])
        assert s["contour_fit"]["r2"] > 0.5 and np.dot(s["contour_fit"]["vector"], UPPER_LEFT) > 0.98


def test_a_mask_is_checked_at_the_boundary(tmp_path):
    p = scene(tmp_path / "s.png", alpha=False)
    def box(**kw):
        return run.ledger(p, [{"id": "ball", "bbox": [50, 30, 80, 80]} | kw])
    Image.fromarray(np.zeros((120, 160, 3), np.uint8), "RGB").save(tmp_path / "opaque.png")
    with pytest.raises(ValueError, match="no alpha"):
        box(mask=str(tmp_path / "opaque.png"))
    with pytest.raises(ValueError, match="expected the image"):
        box(mask=_disc_mask(tmp_path / "wrong.png", (99, 99)))
    with pytest.raises(ValueError, match="empty inside"):
        box(mask=_disc_mask(tmp_path / "empty.png", (160, 120), (900, 900)))
    with pytest.raises(ValueError, match="path of an image"):
        box(mask=7)


def test_the_ledger_says_which_floor_bound_and_whether_the_source_is_lossy(tmp_path):
    """The relative floor is a percentile and survives any transfer function; the absolute one does not,
    and in a night scene it is the one that decides. Both are reported rather than asked for."""
    p = scene(tmp_path / "s.png")
    led = run.ledger(p, BALL)
    assert led["source"] == {"format": "PNG", "lossy": False}
    f = led["emitter_floor"]
    assert f["basis"] in ("absolute", "relative") and f["value"] == max(f["absolute"], f["relative"])
    Image.open(p).convert("RGB").save(tmp_path / "s.jpg", quality=90)
    assert run.ledger(tmp_path / "s.jpg", BALL)["source"] == {"format": "JPEG", "lossy": True}
