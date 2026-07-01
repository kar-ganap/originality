"""Unit tests for the Stage-2 semantic + canonical diversity metrics.

These are lifted into `src/` from Phase 0.1's
`experiments/phase-0.1/check5bd_convergence_stratification.py` (semantic)
and are new (canonical). Per `docs/desiderata.md` §8: semantic diversity
uses ≥2 metrics (effective dimensionality + mean pairwise cosine distance,
plus cluster entropy); canonical concentration uses ≥2 (citation Gini +
top-k share).
"""

from __future__ import annotations

import numpy as np

from whitespace2.canonical_metrics import (
    age_restricted_concentration,
    gini,
    reference_canonicity,
    top_k_share,
)
from whitespace2.semantic_metrics import (
    cluster_entropy,
    effective_dimensionality,
    mean_pairwise_cosine_distance,
)

# ---------- effective_dimensionality ----------


def test_effective_dimensionality_two_equal_axes() -> None:
    """4 points at (±1,0),(0,±1): covariance has two equal eigenvalues →
    participation ratio = 2.0 exactly."""
    v = np.array([[1.0, 0.0], [-1.0, 0.0], [0.0, 1.0], [0.0, -1.0]])
    assert abs(effective_dimensionality(v) - 2.0) < 1e-9


def test_effective_dimensionality_degenerate() -> None:
    """Identical vectors → zero variance → 0.0; <2 rows → 0.0."""
    assert effective_dimensionality(np.ones((5, 3))) == 0.0
    assert effective_dimensionality(np.ones((1, 3))) == 0.0
    # Rank-1 spread (all along one axis) → participation ratio 1.0
    v = np.array([[1.0, 0.0], [2.0, 0.0], [3.0, 0.0], [4.0, 0.0]])
    assert abs(effective_dimensionality(v) - 1.0) < 1e-9


# ---------- mean_pairwise_cosine_distance ----------


def test_mean_pairwise_cosine_distance_known() -> None:
    """Orthogonal → 1.0; identical → 0.0; antipodal → 2.0."""
    assert abs(mean_pairwise_cosine_distance(
        np.array([[1.0, 0.0], [0.0, 1.0]])) - 1.0) < 1e-9
    assert abs(mean_pairwise_cosine_distance(
        np.array([[1.0, 0.0], [1.0, 0.0]])) - 0.0) < 1e-9
    assert abs(mean_pairwise_cosine_distance(
        np.array([[1.0, 0.0], [-1.0, 0.0]])) - 2.0) < 1e-9


def test_mean_pairwise_cosine_distance_normalizes() -> None:
    """Un-normalized inputs are L2-normalized first (default)."""
    # (3,0) and (0,5) → normalize → (1,0),(0,1) → orthogonal → 1.0
    assert abs(mean_pairwise_cosine_distance(
        np.array([[3.0, 0.0], [0.0, 5.0]])) - 1.0) < 1e-9


def test_mean_pairwise_cosine_distance_subsample_deterministic() -> None:
    """max_sample subsamples deterministically (same seed → same value),
    and stays a sane cosine distance in [0, 2]."""
    rng = np.random.default_rng(0)
    v = rng.normal(size=(500, 16))
    a = mean_pairwise_cosine_distance(v, max_sample=100, seed=7)
    b = mean_pairwise_cosine_distance(v, max_sample=100, seed=7)
    assert a == b
    assert 0.0 <= a <= 2.0


# ---------- cluster_entropy ----------


def test_cluster_entropy_known() -> None:
    """Balanced 2-cluster: Shannon(ln2) + Miller-Madow (k-1)/(2n)."""
    # assignments [0,0,1,1], k=2, n=4 → ln2 + 1/8
    val = cluster_entropy(np.array([0, 0, 1, 1]), 2)
    assert abs(val - (0.6931 + 0.125)) < 1e-3
    # Single occupied cluster → 0 entropy, MM term 0
    assert cluster_entropy(np.array([0, 0, 0]), 1) == 0.0


# ---------- gini ----------


def test_gini_known() -> None:
    """gini([1,2,3,4]) = 0.25; equal values → 0."""
    assert abs(gini(np.array([1.0, 2.0, 3.0, 4.0])) - 0.25) < 1e-9
    assert gini(np.array([5.0, 5.0, 5.0])) == 0.0
    # Empty / all-zero → 0 (degenerate, no concentration)
    assert gini(np.array([0.0, 0.0, 0.0])) == 0.0


def test_gini_concentration_rises() -> None:
    """More concentrated citations → higher Gini (the canonical negative
    control's expected direction over time)."""
    spread = gini(np.array([10.0, 11.0, 9.0, 10.0]))
    concentrated = gini(np.array([0.0, 0.0, 1.0, 100.0]))
    assert concentrated > spread


# ---------- top_k_share ----------


def test_top_k_share_known() -> None:
    """Share of total held by the top k-fraction of items."""
    v = np.array([1.0, 1.0, 1.0, 7.0])  # total 10
    assert abs(top_k_share(v, 0.25) - 0.7) < 1e-9   # top 1 of 4 = 7/10
    assert abs(top_k_share(v, 0.5) - 0.8) < 1e-9    # top 2 = (7+1)/10
    assert top_k_share(np.array([0.0, 0.0]), 0.5) == 0.0  # degenerate


# ---------- age_restricted_concentration (WS3 — citation-age-robust) ----------


def test_age_restricted_drops_immature_years() -> None:
    """snapshot 2026, min_age 5 → only publication years ≤ 2021 retained."""
    years = np.array([2018, 2019, 2020, 2021, 2022, 2023, 2024])
    cites = np.array([10, 20, 30, 40, 50, 60, 70])
    rows = age_restricted_concentration(
        years, cites, snapshot_year=2026, min_age=5,
    )
    got_years = [r["year"] for r in rows]
    assert got_years == [2018, 2019, 2020, 2021]  # 2022-2024 are < 5 yr old


def test_age_restricted_matches_base_metrics() -> None:
    """Each retained year's gini / top_k_share equals the base metric on its counts."""
    years = np.array([2000, 2000, 2000, 2000, 2010, 2010])
    cites = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 5.0])
    rows = age_restricted_concentration(
        years, cites, snapshot_year=2026, min_age=5, k_frac=0.5,
    )
    by_year = {r["year"]: r for r in rows}
    assert abs(by_year[2000]["gini"] - gini(np.array([1, 2, 3, 4]))) < 1e-12
    assert by_year[2000]["n"] == 4
    assert abs(
        by_year[2000]["top_k_share"] - top_k_share(np.array([1, 2, 3, 4]), 0.5)
    ) < 1e-12
    assert by_year[2010]["gini"] == 0.0  # equal citations → no concentration


def test_age_restricted_min_papers_filter() -> None:
    """Years thinner than min_papers are skipped (Gini on a handful is noise)."""
    years = np.array([2000, 2000, 2005])  # 2005 has a single paper
    cites = np.array([3.0, 7.0, 9.0])
    rows = age_restricted_concentration(
        years, cites, snapshot_year=2026, min_age=5, min_papers=2,
    )
    assert [r["year"] for r in rows] == [2000]


def test_age_restricted_empty_when_all_immature() -> None:
    """No year old enough → empty (caller must not interpret an empty control)."""
    years = np.array([2023, 2024, 2025])
    cites = np.array([1, 2, 3])
    rows = age_restricted_concentration(
        years, cites, snapshot_year=2026, min_age=5,
    )
    assert rows == []


def test_age_restriction_excludes_zero_inflated_recent() -> None:
    """The fix: zero-inflated recent years (Gini→0 by accrual) are dropped,
    so the retained series carries the real concentration signal (pilot #1)."""
    # 2024 papers all uncited (age 2 → excluded); 2000 papers concentrated.
    years = np.array([2024] * 5 + [2000] * 5)
    cites = np.array([0, 0, 0, 0, 0] + [0, 0, 0, 1, 100])
    rows = age_restricted_concentration(
        years, cites, snapshot_year=2026, min_age=5,
    )
    assert [r["year"] for r in rows] == [2000]
    assert rows[0]["gini"] > 0.5  # concentrated, not the spurious 0.0


def test_age_restricted_sorted_and_handles_nan_years() -> None:
    """Rows are year-sorted; non-finite years are ignored."""
    years = np.array([2010.0, 2000.0, np.nan, 2005.0])
    cites = np.array([4.0, 1.0, 9.0, 2.0])
    rows = age_restricted_concentration(
        years, cites, snapshot_year=2026, min_age=5,
    )
    assert [r["year"] for r in rows] == [2000, 2005, 2010]


# ---------- reference_canonicity (WS-A — Chu-Evans primary canonical, PA-1) ----------


def test_reference_canonicity_concentration_matches_base() -> None:
    """Per-year reference-target concentration == gini/top_k on the freq counts.

    Year 2000: W1 referenced 3×, W2 2×, W3 1× → counts {3,2,1}."""
    years = np.array([2000, 2000, 2000])
    refs = [["W1", "W2", "W3"], ["W1", "W2"], ["W1"]]  # W1:3 W2:2 W3:1
    rows = reference_canonicity(years, refs, top_n=50, deltas=(5,), k_frac=0.5)
    r = rows[0]
    counts = np.array([3.0, 2.0, 1.0])
    assert r["year"] == 2000
    assert r["n_papers"] == 3
    assert r["n_ref_edges"] == 6
    assert r["n_distinct_targets"] == 3
    assert abs(r["ref_gini"] - gini(counts)) < 1e-12
    assert abs(r["ref_top_k_share"] - top_k_share(counts, 0.5)) < 1e-12


def test_reference_canonicity_no_age_restriction() -> None:
    """Unlike citation Gini, recent years get a concentration value (a
    reference list is fixed at publication → no accrual confound)."""
    years = np.array([2000, 2000, 2024, 2024])
    refs = [["W1", "W2"], ["W1"], ["W9", "W8"], ["W9"]]
    rows = reference_canonicity(years, refs, deltas=(5,))
    got = {r["year"] for r in rows}
    assert 2024 in got  # the recent year is NOT dropped
    assert 2000 in got


def test_reference_canonicity_counts_all_targets() -> None:
    """Targets are counted over ALL cited works, incl. cross-field/external
    ids not otherwise in the corpus (PA-1: the canon a field draws on)."""
    years = np.array([2000, 2000])
    refs = [["W_ext_math", "W1"], ["W_ext_math"]]  # external id referenced 2×
    rows = reference_canonicity(years, refs, k_frac=0.5)
    r = rows[0]
    assert r["n_distinct_targets"] == 2  # W_ext_math + W1 both counted
    assert r["n_ref_edges"] == 3


def test_reference_canonicity_stability_high_vs_low() -> None:
    """A canon stable across Δ=5 → Spearman ≈ 1; a fully-turned-over canon →
    lower (negative) Spearman."""
    # Stable: 2000 and 2005 share the same top ranking (W1>W2>W3).
    stable_years = np.array([2000]*6 + [2005]*6)
    stable_refs = (
        [["W1", "W2", "W3"], ["W1", "W2"], ["W1"], ["W1"], ["W2"], ["W3"]]
        + [["W1", "W2", "W3"], ["W1", "W2"], ["W1"], ["W1"], ["W2"], ["W3"]]
    )
    srows = {r["year"]: r for r in
             reference_canonicity(stable_years, stable_refs, top_n=50, deltas=(5,))}
    assert abs(srows[2000]["canon_spearman_d5"] - 1.0) < 1e-9

    # Turnover: 2000's canon is {W1,W2}; 2005's is disjoint {W3,W4}.
    turn_years = np.array([2000, 2000, 2000, 2005, 2005, 2005])
    turn_refs = [["W1", "W2"], ["W1"], ["W1", "W2"],
                 ["W3", "W4"], ["W3"], ["W3", "W4"]]
    trows = {r["year"]: r for r in
             reference_canonicity(turn_years, turn_refs, top_n=50, deltas=(5,))}
    assert trows[2000]["canon_spearman_d5"] < srows[2000]["canon_spearman_d5"]
    assert trows[2000]["canon_spearman_d5"] < 0.0  # anti-correlated canons


def test_reference_canonicity_delta_columns_and_edges() -> None:
    """Δ=5 and Δ=1 columns both produced; years without a t+Δ partner → None."""
    years = np.array([2000]*2 + [2001]*2 + [2005]*2)
    refs = [["W1"], ["W1", "W2"]] * 3
    rows = {r["year"]: r for r in
            reference_canonicity(years, refs, deltas=(5, 1))}
    # 2000 has both a +1 (2001) and a +5 (2005) partner.
    assert rows[2000]["canon_spearman_d1"] is not None
    assert rows[2000]["canon_spearman_d5"] is not None
    # 2001 has no +5 (2006 absent) and no +1 (2002 absent).
    assert rows[2001]["canon_spearman_d5"] is None
    assert rows[2001]["canon_spearman_d1"] is None
    # 2005 has neither partner.
    assert rows[2005]["canon_spearman_d5"] is None


def test_reference_canonicity_excludes_zero_reference_years() -> None:
    """A year whose papers carry no references is excluded (PA-3 degenerate)."""
    years = np.array([2000, 2000, 2010, 2010])
    refs = [["W1"], ["W1", "W2"], [], []]  # 2010 papers have empty ref lists
    rows = reference_canonicity(years, refs, deltas=(5,))
    got = {r["year"] for r in rows}
    assert got == {2000}  # 2010 dropped (no reference edges)


def test_reference_canonicity_min_papers_and_sorted() -> None:
    """min_papers filters thin years; rows are year-sorted; None refs safe."""
    years = np.array([2010, 2000, 2000])
    refs = [["W5"], ["W1"], None]  # 2010 has 1 paper; None ref list tolerated
    rows = reference_canonicity(years, refs, deltas=(5,), min_papers=2)
    assert [r["year"] for r in rows] == [2000]  # 2010 (1 paper) filtered out
