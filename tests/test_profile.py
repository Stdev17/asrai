"""The overlay is a cache over the record corpus: derived, deletable, and never a source."""
import json

import pytest

from asrai import profile, records

OBS = {"kind": "observation", "asset_kind": "raster", "evidence_layer": "L1", "scale": "native",
       "asset_sha256": "a" * 64, "observer": {"mode": "host", "model": "m", "prompt_rev": "v1"},
       "observations": [{"term_id": "lighting.cast_shadow", "level": "estimated", "region": [0, 0, 4, 4],
                         "note": "asset: cast shadow missing or inconsistent"}]}


def test_the_overlay_is_what_the_corpus_demonstrates_and_absence_is_not_a_finding(tmp_path):
    """Every row comes from a record, so a term nobody has written about is simply missing rather than
    marked clean. That distinction is the one this repository keeps getting wrong, so the file says it
    in its own `unobserved` field instead of leaving a reader to infer it."""
    assert profile.project(tmp_path)["scopes"] == {}          # no corpus at all is not an error
    records.append(OBS, tmp_path / "records.jsonl")
    scopes = profile.project(tmp_path)["scopes"]

    # one observation lands on the term and on the category it belongs to, and on nothing else
    assert set(scopes) == {"term:lighting.cast_shadow", "category:lighting"}
    assert scopes["term:lighting.cast_shadow"]["state"] == "used"
    assert scopes["term:lighting.cast_shadow"]["evidence"] == [records.read(tmp_path / "records.jsonl")[0]["id"]]
    assert "nobody has looked is not the same as nothing is there" in profile.project(tmp_path)["unobserved"]

    # a record that replaces another is judgment over that scope, not only vocabulary
    records.append(OBS | {"supersedes": "observation_x"}, tmp_path / "records.jsonl")
    assert profile.project(tmp_path)["scopes"]["term:lighting.cast_shadow"]["state"] == "overrode"


def test_the_cache_follows_its_source_and_deleting_it_loses_nothing(tmp_path):
    """The one rule the cache realm owns about itself. An append moves the source, so the next read
    reprojects; deleting the cache changes no answer, only the time it took. A cache that survived a
    source it no longer matches would be a second source, which is what `docs/architecture.md` forbids."""
    records.append(OBS, tmp_path / "records.jsonl")
    first = profile.overlay(tmp_path)
    assert (tmp_path / profile.CACHE).exists()
    assert profile.overlay(tmp_path)["at"] == first["at"]     # unchanged source: the cache answers

    records.append(OBS, tmp_path / "records.jsonl")
    assert profile.overlay(tmp_path)["source_bytes"] > first["source_bytes"]

    keep = profile.overlay(tmp_path)
    (tmp_path / profile.CACHE).unlink()
    assert profile.overlay(tmp_path)["scopes"] == keep["scopes"]          # deletion loses only time

    (tmp_path / profile.CACHE).write_text("not json at all", "utf-8")
    assert profile.overlay(tmp_path)["scopes"] == keep["scopes"]          # a broken cache is a cold one


def test_a_term_the_vocabulary_no_longer_ships_is_dropped_not_guessed(tmp_path):
    """Records outlive a vocabulary revision, and the overlay is an annotation on the vocabulary that
    ships now. A scope for a term that is gone would be one nothing could ever be said about."""
    records.append(OBS, tmp_path / "records.jsonl")
    line = (tmp_path / "records.jsonl").read_text("utf-8").replace("lighting.cast_shadow", "lighting.retired")
    (tmp_path / "records.jsonl").write_text(line, "utf-8")
    assert profile.project(tmp_path)["scopes"] == {}
