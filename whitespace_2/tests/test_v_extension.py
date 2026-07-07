"""Phase 2.4 — data-spine correctness (parse + in-sample forward-citation inversion)."""

from __future__ import annotations

import json

import numpy as np

from whitespace2.v_extension import (
    forward_uptake,
    parse_authorships,
    parse_references,
    top_subfield,
)


def test_parse_authorships() -> None:
    js = json.dumps([
        {"author": {"id": "https://openalex.org/A1", "orcid": "x"}, "countries": ["US"]},
        {"author": {"id": "https://openalex.org/A2", "orcid": None}, "countries": ["GB"]},
        {"author": {"id": "https://openalex.org/A3"}, "countries": []},
    ])
    team, aids, n_orcid, country = parse_authorships(js)
    assert team == 3
    assert aids == ["https://openalex.org/A1", "https://openalex.org/A2", "https://openalex.org/A3"]
    assert n_orcid == 1
    assert country == "US"          # first non-empty country
    assert parse_authorships("") == (0, [], 0, None)
    assert parse_authorships("[]") == (0, [], 0, None)


def test_top_subfield() -> None:
    js = json.dumps([
        {"display_name": "Broad", "level": 0, "score": 0.9},
        {"display_name": "Machine learning", "level": 1, "score": 0.4},
        {"display_name": "Deep learning", "level": 1, "score": 0.7},   # top level-1
        {"display_name": "Narrow", "level": 2, "score": 0.99},
    ])
    assert top_subfield(js, level=1) == "Deep learning"
    assert top_subfield("[]") is None


def test_parse_references() -> None:
    assert parse_references(json.dumps(["https://openalex.org/W1", "https://openalex.org/W2"])) == \
        ["https://openalex.org/W1", "https://openalex.org/W2"]
    assert parse_references("[]") == []


def test_forward_uptake() -> None:
    # 4 papers; edges = who-cites-whom (in-sample). Windowed forward uptake.
    ids = ["A", "B", "C", "D"]
    years = [2000, 2002, 2004, 2010]
    refs = [
        [],                 # A cites nothing
        ["A"],              # B(2002) cites A(2000): within 5y -> counts for A
        ["A", "B"],         # C(2004) cites A(2000) [4y, counts] and B(2002) [2y, counts]
        ["A", "Z"],         # D(2010) cites A(2000) [10y > 5, NOT counted] and Z (out-of-sample)
    ]
    up = forward_uptake(ids, years, refs, window=5)
    # A: cited by B(2002,2y ok), C(2004,4y ok), D(2010,10y no) -> 2
    # B: cited by C(2004,2y ok) -> 1 ; C,D: 0
    assert list(up) == [2, 1, 0, 0]
    # widen window to 10 -> D's citation of A now counts
    assert list(forward_uptake(ids, years, refs, window=10)) == [3, 1, 0, 0]


def test_forward_uptake_ignores_out_of_sample() -> None:
    # references to ids not in the paper set are ignored (in-sample graph only)
    up = forward_uptake(["A"], [2000], [["A"]], window=5)  # self-ref edge, in-sample
    assert up[0] == 1
    up2 = forward_uptake(["A"], [2000], [["QQ"]], window=5)  # ref out of sample
    assert up2[0] == 0
    assert isinstance(up2, np.ndarray)
