"""Tests for the `ref_gini` null, including the metric characterization WS2 never ran."""

from __future__ import annotations

import numpy as np
import pytest

from whitespace2.canonical_metrics import gini
from whitespace2.null_ref_gini import (
    calibrate_pool_size,
    replay_reference_canonicity,
    simulate_year_gini,
    simulate_year_gini_per_paper,
    slope,
)

# --- metric characterization: what does ref_gini do when nothing is canonical? ---------------


def test_gini_is_zero_when_every_work_is_cited_exactly_once() -> None:
    """The regime the 1970s corpus is in: 1,904 edges over 1,880 targets."""
    assert gini(np.ones(1880)) == pytest.approx(0.0, abs=1e-12)


def test_ref_gini_rises_with_edge_count_alone_under_uniform_attachment() -> None:
    """The confound, stated as a test.

    Nothing here is canonical — every target is equally attractive and the pool is fixed. Drawing
    more edges still drives the Gini up, because repeats accumulate by the birthday principle.
    """
    rng = np.random.default_rng(0)
    pool = 50_000.0
    ginis = [
        float(np.mean([simulate_year_gini(rng, [edges], pool)[0] for _ in range(20)]))
        for edges in (2_000, 10_000, 40_000, 80_000)
    ]
    assert ginis == sorted(ginis), "uniform attachment must still produce a rising Gini"
    assert ginis[-1] > 3 * ginis[0]


def test_observed_ref_gini_magnitudes_are_the_singleton_regime_not_a_canon() -> None:
    """Anchor the scale, so `ref_gini` rising 0.013 to 0.060 cannot be read as a canon forming.

    Real citation distributions are heavy-tailed and land near Gini 0.8-0.99 — which is where this
    study's *other* canonical metric, the age-restricted citation Gini, actually sits (0.81-0.95).
    The observed `ref_gini` range is two regimes away, and is what a corpus of near-singletons
    produces.
    """
    zipf = np.arange(1, 20_001, dtype=np.float64) ** -1.0
    assert gini(zipf / zipf.min()) > 0.80, "a real citation distribution is highly unequal"

    observed_regime = np.array([1.0] * 79_000 + [2.0] * 800 + [3.0] * 80 + [10.0] * 9)
    assert gini(observed_regime) < 0.05, "the observed range is the near-all-singletons regime"


# --- the pool calibration --------------------------------------------------------------------


def test_pool_calibration_recovers_the_expected_distinct_count() -> None:
    for n_edges, n_distinct in ((85_135, 79_889), (1_904, 1_880), (34_218, 31_503)):
        pool = calibrate_pool_size(n_edges, n_distinct)
        expected = pool * (1.0 - (1.0 - 1.0 / pool) ** n_edges)
        assert expected == pytest.approx(float(n_distinct), rel=1e-6)


def test_pool_is_unbounded_when_no_edge_repeats() -> None:
    assert calibrate_pool_size(100, 100) == float("inf")
    assert simulate_year_gini(np.random.default_rng(0), [100], float("inf"))[0] == 0.0


# --- the vectorized path must match the exact one ---------------------------------------------


def test_vectorized_null_matches_the_exact_per_paper_null() -> None:
    """The fast path treats a year as one draw; the exact path draws per paper without replacement.

    At realistic pool sizes these must agree well inside the null's own spread, or the speedup is
    buying a different model.
    """
    counts = [17] * 400
    pool = calibrate_pool_size(sum(counts), int(sum(counts) * 0.94))
    fast = [simulate_year_gini(np.random.default_rng(s), counts, pool)[0] for s in range(30)]
    exact = [
        simulate_year_gini_per_paper(np.random.default_rng(s), counts, pool)[0] for s in range(30)
    ]
    tolerance = 0.25 * float(np.std(exact))
    assert float(np.mean(fast)) == pytest.approx(float(np.mean(exact)), abs=tolerance)


# --- the replay ------------------------------------------------------------------------------


def test_replay_counts_targets_across_papers_within_a_year() -> None:
    per_year = [(1990, [["a", "b"], ["b", "c"], ["b"]])]
    rows = replay_reference_canonicity(per_year)
    assert len(rows) == 1
    assert rows[0]["n_ref_edges"] == 5
    assert rows[0]["n_distinct_targets"] == 3
    assert rows[0]["ref_gini"] == pytest.approx(gini(np.array([1.0, 3.0, 1.0])))


def test_replay_skips_years_with_no_reference_edges() -> None:
    assert replay_reference_canonicity([(1971, [[], []])]) == []


def test_slope_matches_a_known_line() -> None:
    assert slope([0.0, 1.0, 2.0, 3.0], [1.0, 3.0, 5.0, 7.0]) == pytest.approx(2.0)
