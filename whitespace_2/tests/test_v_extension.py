"""Phase 2.4 — data-spine correctness (parse + in-sample forward-citation inversion)."""

from __future__ import annotations

import json

import numpy as np

from whitespace2.v_extension import (
    cd_index,
    cd_index_csr,
    forward_uptake,
    off_canon_share,
    panel_year_test,
    parse_authorships,
    parse_references,
    persistence_weight,
    reference_atypicality,
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


def test_off_canon_share() -> None:
    # head A..E cited 10x each (2000); tail F0..F19 cited 1x each (2000); 25 distinct.
    years = [2000] * 10 + [2000] * 20 + [2001, 2001, 2001]
    refs = (
        [["A", "B", "C", "D", "E"]] * 10
        + [[f"F{i}"] for i in range(20)]
        + [["A", "F0"], ["A", "B"], ["F1", "F2"]]
    )
    off = off_canon_share(years, refs, alpha=0.2)  # top-20% of 25 = top 5 = the head {A..E}
    assert off[-3] == 0.5   # [A,F0]: A canon, F0 off
    assert off[-2] == 0.0   # [A,B]: both canon
    assert off[-1] == 1.0   # [F1,F2]: both off (a percentile threshold would call these canon)
    assert np.isnan(off_canon_share([2000], [[]], alpha=0.05)[0])   # no refs -> NaN
    # tolerates ndarray refs (a parquet reload yields arrays, not lists)
    arr_refs = [np.array(["A", "B"]), np.array([], dtype=object)]
    res = off_canon_share([2000, 2000], arr_refs, alpha=0.5)
    assert not np.isnan(res[0]) and np.isnan(res[1])


def test_persistence_weight() -> None:
    s = persistence_weight(uptake=[0, 2, 10, 0], field=["cs"] * 4, year=[2000, 2000, 2000, 2001])
    # cell (cs,2000): u=[0,2,10], mean ubar=4 -> s = 0, 2/6, 10/14
    assert s[0] == 0.0
    assert abs(s[1] - 2 / 6) < 1e-9
    assert abs(s[2] - 10 / 14) < 1e-9
    assert s[3] == 0.0        # cell (cs,2001): u=[0], ubar=0 -> 0/0 handled as 0


def test_panel_year_test() -> None:
    rng = np.random.default_rng(0)
    n = 2000
    year = rng.integers(1970, 2020, n).astype(float)
    ctrl = rng.normal(0, 1, n)                      # a confound correlated with the outcome
    field = np.where(rng.random(n) < 0.5, "cs", "physics")
    fe = np.where(field == "cs", 0.0, 0.3)          # field fixed effect
    y = -0.01 * (year - 1970) + 0.5 * ctrl + fe + rng.normal(0, 0.1, n)
    res = panel_year_test(y, year, field, controls=[ctrl], n_perm=500, seed=1)
    assert res["year_coef"] < 0                     # recovers the negative year slope
    assert abs(res["year_coef"] - (-0.01)) < 0.003  # ≈ −0.01 net of ctrl + field-FE
    assert res["perm_pvalue"] < 0.01                # permutation-significant
    assert res["abs_change"] < 0                    # material negative change over the span
    # year-shuffle placebo: the trend must vanish
    yshuf = rng.permutation(year)
    res0 = panel_year_test(y, yshuf, field, controls=[ctrl], n_perm=500, seed=2)
    assert res0["perm_pvalue"] > 0.05


def test_reference_atypicality() -> None:
    # C,D always co-cited (conventional); A,B each common but co-cited only once (atypical)
    refs = [["C", "D"]] * 50 + [["A"]] * 30 + [["B"]] * 30 + [["A", "B"]]
    med, p10 = reference_atypicality(refs, d_min=20, min_pairs=1)
    assert med[0] > 0        # [C,D]: co-cited far more than expected -> conventional (high z)
    assert med[-1] < 0       # [A,B]: never co-cited before -> atypical (negative z)
    assert med[0] > med[-1]
    assert np.isnan(med[50])  # single-ref paper [A] -> no pairs -> NaN


def test_cd_index() -> None:
    # vendored from WS3 @ 282e09f: element 1 (cites root 0) cited by 3 papers ignoring its ref
    # (disruptive) + 1 citing both (consolidating) -> CD > 0.
    disruptive = [[], [0], [1], [1], [1], [1, 0]]
    cd = cd_index(disruptive, min_citers=3)
    assert cd[1] > 0
    assert np.isnan(cd[0])       # root: no references -> NaN
    # reverse: 3 consolidating citers + 1 disruptive -> CD < 0.
    consolidating = [[], [0], [1, 0], [1, 0], [1, 0], [1]]
    assert cd_index(consolidating, min_citers=3)[1] < 0
    # focals subset: same arithmetic on the FULL graph, others NaN (data-scaling path).
    sub = cd_index(disruptive, min_citers=3, focals=[1])
    assert sub[1] == cd[1] and np.isnan(sub[0]) and np.isnan(sub[2])


def _to_csr(prereqs: list[list[int]]) -> tuple[np.ndarray, np.ndarray]:
    indptr = np.zeros(len(prereqs) + 1, dtype=np.int64)
    for i, p in enumerate(prereqs):
        indptr[i + 1] = indptr[i] + len(p)
    indices = np.array([x for p in prereqs for x in p], dtype=np.int32)
    return indptr, indices


def test_cd_index_csr_matches_dense() -> None:
    # the CSR/scipy engine (24M-scale path) must equal the list-of-lists cd_index bit-for-bit.
    for graph in ([[], [0], [1], [1], [1], [1, 0]],
                  [[], [0], [1, 0], [1, 0], [1, 0], [1]]):
        ip, ix = _to_csr(graph)
        a = cd_index(graph, min_citers=3)
        b = cd_index_csr(ip, ix, min_citers=3)
        m = ~np.isnan(a)
        assert np.allclose(a[m], b[m]) and bool(np.isnan(b[~m]).all())
