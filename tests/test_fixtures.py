"""spec.md 14 conformance 1 and 12: measure is byte-stable on committed bytes, and the transports agree."""
import json
import subprocess
import sys
from pathlib import Path

import make_fixtures
import pytest

from asrai import measure

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.mark.parametrize("name", sorted(make_fixtures.BUILDERS), ids=lambda n: Path(n).stem)
def test_measure_matches_committed_fixture(name):
    """The documented byte-equality gate includes serialization, not just parsed numeric values."""
    want = (FIXTURES / "expected" / f"{Path(name).stem}.json").read_bytes()
    assert make_fixtures.expectation_json(name).encode("utf-8") == want, \
        f"measure drifted on {name}; if deliberate, rerun tools/make_fixtures.py and read the diff"


def test_cli_and_core_measure_identically():
    """The MCP tool is a one-line passthrough; the CLI is where serialization could disagree."""
    path = FIXTURES / "sprite_rgba.png"
    out = subprocess.run([sys.executable, "-m", "asrai.cli", "measure", str(path), "--target-width", "48"],
                         capture_output=True, text=True, check=True)
    assert json.loads(out.stdout) == measure.measure(path, 48)


def test_measure_reports_a_fully_transparent_asset_as_empty(tmp_path):
    """An export that dropped everything still has to measure, not divide by zero."""
    from PIL import Image
    Image.new("RGBA", (32, 32), (0, 0, 0, 0)).save(tmp_path / "void.png")
    native = measure.measure(tmp_path / "void.png")["scales"]["native"]
    assert native["empty"] is True and native["opaque_pixels"] == 0
    assert native["silhouette"] == {"mask_area_ratio": 0.0, "bbox": None, "bbox_fill_ratio": None, "components": 0}
