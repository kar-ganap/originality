"""Tests for the novelty metrics (lifted from WS2 test_v_extension.py).

Covers reference_atypicality, cd_index (dense), and cd_index_csr (sparse). The
WS2 data-spine helpers (parse_*, forward_uptake, off_canon_share,
persistence_weight, panel_year_test) were not graduated, so their tests are not
ported.
"""

from __future__ import annotations

import numpy as np

from diversity_metrics.novelty import cd_index, reference_atypicality
from diversity_metrics.novelty_sparse import cd_index_csr


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


def test_cd_index_csr_window_and_floor() -> None:
    # focal 1 (yr 2001) is cited by 2,3,4,5 (yrs 2002,2005,2010,2003).
    graph = [[], [0], [1], [1], [1], [1, 0]]
    ip, ix = _to_csr(graph)
    year = np.array([2000, 2001, 2002, 2005, 2010, 2003], dtype=np.int32)
    base = cd_index_csr(ip, ix, min_citers=3)
    wide = cd_index_csr(ip, ix, min_citers=3, year=year, window=100)
    assert np.allclose(base[1], wide[1])          # huge window ⇒ identical to un-windowed
    narrow = cd_index_csr(ip, ix, min_citers=3, year=year, window=2)
    assert np.isnan(narrow[1])                    # only 2 citers within 2 yrs of 2001 (<min_citers)
    floored = cd_index_csr(ip, ix, min_citers=3, year=year, year_min=2004)
    assert np.isnan(floored[1])                   # only 2 citers with yr≥2004 (<min_citers)
