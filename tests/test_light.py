"""light_ledger: a Lambertian disc lit from the upper-left must point there, agree with the lamp
placed there, disagree with the decoy, and mirror with the image."""
import json

import numpy as np
import pytest
from PIL import Image

from asrai import light

LIGHT = np.array([-0.5, -0.5, np.sqrt(0.5)])           # unit: towards the upper-left, out of the image
BALL = [{"id": "ball", "bbox": [50, 30, 80, 80]}]
UPPER_LEFT = np.array([-1.0, -1.0]) / np.sqrt(2)


def scene(path):
    W, H = 160, 120
    img = np.zeros((H, W, 4), np.uint8)
    yy, xx = np.mgrid[:H, :W]
    nx, ny = (xx - 90) / 36, (yy - 70) / 36
    inside = nx ** 2 + ny ** 2 <= 1
    nz = np.sqrt(np.clip(1 - nx ** 2 - ny ** 2, 0, 1))
    shade = 0.08 + 0.45 * np.clip(nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2], 0, 1)
    srgb = np.where(shade <= 0.0031308, shade * 12.92, 1.055 * shade ** (1 / 2.4) - 0.055)
    for c, k in enumerate((1.0, 0.92, 0.80)):            # a warm grey ball
        img[..., c] = np.where(inside, srgb * k * 255, 0).round()
    img[..., 3] = np.where(inside, 255, 0)
    img[(xx - 18) ** 2 + (yy - 14) ** 2 <= 36] = (255, 255, 240, 255)     # white lamp, upper-left
    img[(xx - 150) ** 2 + (yy - 110) ** 2 <= 25] = (0, 255, 255, 255)     # cyan decoy, lower-right
    Image.fromarray(img, "RGBA").save(path)
    return path


def test_direction_emitters_fit_and_questions(tmp_path):
    led = light.ledger(scene(tmp_path / "s.png"), BALL, out_dir=tmp_path / "out")
    assert led == light.ledger(tmp_path / "s.png", BALL, out_dir=tmp_path / "out")
    ball = led["subjects"][0]
    assert ball["mask"] == "alpha" and np.dot(ball["bright_side"]["vector"], UPPER_LEFT) > 0.9
    assert ball["contour_fit"]["r2"] > 0.5 and np.dot(ball["contour_fit"]["vector"], UPPER_LEFT) > 0.9
    assert len(led["emitters"]) == 2 and led["emitters"][0]["id"] == "e1"
    lamp, decoy = led["emitters"]                        # brightest first: the white lamp, then cyan
    assert np.hypot(*(np.array(lamp["centroid"]) - (18, 14))) < 2 and np.hypot(*(np.array(decoy["centroid"]) - (150, 110))) < 2
    by = {a["emitter"]: a for a in led["agreement"]}
    assert by[decoy["id"]]["distance_px"] < by[lamp["id"]]["distance_px"]   # nearer, yet not what the shading points at
    assert by[lamp["id"]]["angle_deg"] < 20 and by[decoy["id"]]["angle_deg"] > 120
    assert by[lamp["id"]]["hue_delta_deg"] is None and by[decoy["id"]]["hue_delta_deg"] > 90
    assert led["global"]["alignment"] > 0.99 and np.dot(led["global"]["key_direction"], UPPER_LEFT) > 0.9
    assert Image.open(led["overlay"]).size == (160, 120)
    surfaces = [q["surface"] for q in led["questions"]]
    assert surfaces[:2] == ["emissive", "emissive"] and surfaces.count("diffuse") == 2   # lamp: pointed at and brightest; decoy: nearest
    pair = next(q for q in led["questions"] if q["surface"] == "diffuse")
    assert pair["term_id"] == "lighting.form_shadow" and pair["region"] == [50, 30, 80, 80]
    assert "ball" in pair["question"] and pair["emitter"] in pair["question"]


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
    assert led["subjects"] == [] and led["global"] is None and led["overlay"] is None
    assert [e["kind"] for e in led["emitters"]] == ["proposed"]
    assert {q["surface"] for q in led["questions"]} == {"emissive", "key", "atmosphere"}


def test_capture_boxes_become_subjects(tmp_path):
    p = scene(tmp_path / "frame.png")
    cap = tmp_path / "capture.json"
    cap.write_text(json.dumps({"composed_of": [{"game_object": "Ball", "screen_bbox": [50, 30, 80, 80]},
                                               {"game_object": "Ball", "screen_bbox": [0, 0, 8, 8]},
                                               {"game_object": "Ghost"}]}), "utf-8")
    assert [s["id"] for s in light.ledger(p, capture=str(cap))["subjects"]] == ["Ball", "Ball_2"]


def test_malformed_subjects_raise_value_error(tmp_path):
    p = scene(tmp_path / "s.png")
    for bad in ("ball", [{"id": "b"}], [{"id": "b", "bbox": [0, 0, 0, 5]}], [{"id": "b", "bbox": [1.5, 0, 5, 5]}],
                [{"id": "b", "bbox": [500, 500, 5, 5]}], [{"id": "b", "bbox": [0, 0, 5, 5]}] * 2, [7]):
        with pytest.raises(ValueError):
            light.ledger(p, bad)
