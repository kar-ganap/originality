"""Coverage-closing tests for the resolution-map diagnostics (companion to test_resolution.py).

The existing suite exercises the happy paths; this file locks the branches, equality boundaries,
and NaN-robustness the coverage audit found unexercised. Every assertion here encodes the behavior
required by `docs/resolution-map-phase3-prereg.md` (the "4-way classification rule", the
"E4 internal standard", and "E5"). Pure known-answer inputs only — no `channel.run`, no I/O,
no randomness beyond a pinned seed.
"""

from __future__ import annotations

import numpy as np
import pytest

from whitespace3.resolution import (
    DETERMINISM_TOL,
    classify,
    crossover_exists,
    mean_ci,
    seed_cv,
    variance_decompose,
)

# --- seed_cv: single element, negative mean, NaN robustness ----------------------------------


def test_seed_cv_single_element_is_zero() -> None:
    # One seed has no spread; CV is 0/|x|, defined and non-inf (mean is not ~0).
    assert seed_cv(np.array([5.0])) == 0.0


def test_seed_cv_uses_absolute_mean_so_negative_mean_gives_positive_cv() -> None:
    # CV must divide by |mean|; a sign-flipped input must give the identical (positive) CV.
    neg = seed_cv(np.array([-2.0, -4.0, -6.0]))
    pos = seed_cv(np.array([2.0, 4.0, 6.0]))
    assert neg == pytest.approx(pos)
    assert neg > 0.0


def test_seed_cv_propagates_nan_rather_than_returning_a_finite_number() -> None:
    # A leaked NaN must poison the output (nan), not silently produce a wrong finite CV or raise.
    assert np.isnan(seed_cv(np.array([1.0, np.nan, 3.0])))


# --- mean_ci: <2 guard, size-2 boundary, spread monotonicity, NaN robustness ------------------


def test_mean_ci_returns_nan_pair_for_fewer_than_two_values() -> None:
    # The size<2 guard: both an empty and a single-value input return (nan, nan) without computing.
    empty_lo, empty_hi = mean_ci(np.array([]))
    single_lo, single_hi = mean_ci(np.array([7.0]))
    assert np.isnan(empty_lo) and np.isnan(empty_hi)
    assert np.isnan(single_lo) and np.isnan(single_hi)


def test_mean_ci_computes_finite_bounds_at_the_two_value_boundary() -> None:
    # size == 2 is the first input that clears the guard; it must return finite bounds, not nan.
    lo, hi = mean_ci(np.array([1.0, 3.0]), seed=0)
    assert np.isfinite(lo) and np.isfinite(hi)
    assert lo == pytest.approx(1.0)
    assert hi == pytest.approx(3.0)


def test_mean_ci_wider_spread_gives_a_wider_interval() -> None:
    # Same n and seed, only the dispersion differs: more spread must widen the bootstrap CI.
    tight = mean_ci(np.array([0.9, 1.0, 1.1, 1.0, 0.95, 1.05]), seed=0)
    broad = mean_ci(np.array([-3.0, 5.0, -2.0, 4.0, -1.0, 3.0]), seed=0)
    assert (broad[1] - broad[0]) > (tight[1] - tight[0])


def test_mean_ci_propagates_nan_into_the_interval() -> None:
    # A NaN in the sample poisons resampled means; both bounds must come back nan, not finite.
    lo, hi = mean_ci(np.array([1.0, np.nan, 3.0, 2.0]), seed=0)
    assert np.isnan(lo) and np.isnan(hi)


# --- classify: equality boundaries and the det_tol parameter ---------------------------------


def test_classify_effect_exactly_at_sesoi_is_clock_when_deterministic() -> None:
    # |effect| == sesoi satisfies the ">= SESOI" clock condition (pre-reg rule 2, boundary).
    assert (
        classify(effect=0.1, ci_lo=0.1, ci_hi=0.1, sesoi=0.1, seed_cv_level=0.0)
        == "deterministic-clock"
    )


def test_classify_effect_exactly_at_sesoi_is_with_signal_when_stochastic() -> None:
    # |effect| == sesoi satisfies C2 (">= SESOI"); with a CI excluding zero this is USABLE (rule 3).
    assert (
        classify(effect=0.1, ci_lo=0.05, ci_hi=0.15, sesoi=0.1, seed_cv_level=0.2)
        == "stochastic-with-signal"
    )


def test_classify_ci_endpoint_touching_zero_does_not_count_as_excluding_zero() -> None:
    # A CI whose endpoint is exactly 0 does not strictly exclude 0 → noise-dominated, both sides.
    from_below = classify(effect=0.3, ci_lo=0.0, ci_hi=0.6, sesoi=0.1, seed_cv_level=0.2)
    from_above = classify(effect=-0.3, ci_lo=-0.6, ci_hi=0.0, sesoi=0.1, seed_cv_level=0.2)
    assert from_below == "stochastic-noise-dominated"
    assert from_above == "stochastic-noise-dominated"


def test_classify_seed_cv_exactly_at_det_tol_is_stochastic_not_deterministic() -> None:
    # Determinism is seed-CV < det_tol (strict); at exactly det_tol the output is stochastic.
    assert (
        classify(
            effect=1.0, ci_lo=0.9, ci_hi=1.1, sesoi=0.1, seed_cv_level=DETERMINISM_TOL
        )
        == "stochastic-with-signal"
    )


def test_classify_honors_an_explicit_det_tol_override() -> None:
    # A level of 5e-3 is deterministic only under the loosened tol; the parameter must be respected.
    assert (
        classify(effect=1.0, ci_lo=0.9, ci_hi=1.1, sesoi=0.1, seed_cv_level=5e-3, det_tol=1e-2)
        == "deterministic-clock"
    )


def test_classify_deterministic_flat_for_a_nonzero_but_subthreshold_effect() -> None:
    # Flat needs only |effect| < sesoi, not effect == 0: a small nonzero response is still flat.
    assert (
        classify(effect=0.05, ci_lo=0.04, ci_hi=0.06, sesoi=0.1, seed_cv_level=0.0)
        == "deterministic-flat"
    )


def test_classify_with_signal_for_a_ci_entirely_above_zero() -> None:
    # The excludes-zero test must fire for a wholly-positive CI too, not only wholly-negative ones.
    assert (
        classify(effect=0.3, ci_lo=0.1, ci_hi=0.5, sesoi=0.1, seed_cv_level=0.2)
        == "stochastic-with-signal"
    )


# --- crossover_exists: empty, single, straddle handling, touching-zero boundaries ------------


def test_crossover_empty_sequence_is_false() -> None:
    assert crossover_exists([]) is False


def test_crossover_single_point_is_never_a_crossover() -> None:
    # One λ cannot contain a V→C flip regardless of its sign.
    assert crossover_exists([(0.05, 0.02, 0.08)]) is False
    assert crossover_exists([(-0.05, -0.08, -0.02)]) is False
    assert crossover_exists([(0.0, -0.05, 0.05)]) is False


def test_crossover_straddle_between_same_sign_points_is_not_a_flip() -> None:
    # +ve, straddle, +ve: no reliably-C-favouring point ever appears → no crossover.
    slopes = [(0.05, 0.02, 0.08), (0.0, -0.03, 0.03), (0.03, 0.01, 0.06)]
    assert crossover_exists(slopes) is False


def test_crossover_v_favouring_carries_across_multiple_straddling_points() -> None:
    # The V-favouring flag persists through several mush points until a reliably-C-favouring one.
    slopes = [(0.05, 0.02, 0.08), (0.0, -0.03, 0.03), (0.0, -0.02, 0.04), (-0.04, -0.09, -0.01)]
    assert crossover_exists(slopes) is True


def test_crossover_detected_when_flip_is_embedded_in_a_longer_sequence() -> None:
    # -ve first (no V seen yet, ignored), then +ve, then -ve → a valid V→C flip.
    slopes = [(-0.05, -0.08, -0.02), (0.04, 0.01, 0.07), (-0.04, -0.09, -0.01)]
    assert crossover_exists(slopes) is True


def test_crossover_true_on_the_first_flip_even_with_several_flips() -> None:
    # + - + -: the first reliable V→C transition already establishes a crossover.
    slopes = [(0.05, 0.02, 0.08), (-0.04, -0.07, -0.01), (0.03, 0.01, 0.06), (-0.02, -0.05, -0.01)]
    assert crossover_exists(slopes) is True


def test_crossover_ci_lo_touching_zero_is_not_reliably_v_favouring() -> None:
    # "Entirely above 0" is strict: ci_lo == 0 is not V-favouring, so no later flip counts.
    slopes = [(0.05, 0.0, 0.10), (-0.04, -0.09, -0.01)]
    assert crossover_exists(slopes) is False


def test_crossover_ci_hi_touching_zero_is_not_reliably_c_favouring() -> None:
    # "Entirely below 0" is strict: ci_hi == 0 is not C-favouring, so no flip is registered.
    slopes = [(0.05, 0.02, 0.08), (-0.04, -0.09, 0.0)]
    assert crossover_exists(slopes) is False


# --- variance_decompose: pure splits, degenerate total, and the ValueError guards ------------


def test_variance_decompose_attributes_all_variance_to_seeds_when_rows_are_flat() -> None:
    # Each row is constant (zero within-seed variance); differing row means → all variance is seed.
    frac = variance_decompose(np.array([[1.0, 1.0], [5.0, 5.0], [9.0, 9.0]]))
    assert frac["seed_fraction"] == pytest.approx(1.0)
    assert frac["graph_fraction"] == pytest.approx(0.0)
    assert frac["seed_fraction"] + frac["graph_fraction"] == pytest.approx(1.0)


def test_variance_decompose_attributes_all_variance_to_graph_when_row_means_match() -> None:
    # Rows are permutations sharing a mean → zero between-seed variance; all variance is within.
    frac = variance_decompose(np.array([[1.0, 3.0], [3.0, 1.0]]))
    assert frac["seed_fraction"] == pytest.approx(0.0)
    assert frac["graph_fraction"] == pytest.approx(1.0)
    assert frac["seed_fraction"] + frac["graph_fraction"] == pytest.approx(1.0)


def test_variance_decompose_returns_zero_fractions_when_total_variance_is_zero() -> None:
    # All-identical data: between == within == 0. The guard returns zeros, not a 0/0 nan.
    frac = variance_decompose(np.full((5, 4), 3.0))
    assert frac == {"seed_fraction": 0.0, "graph_fraction": 0.0}


def test_variance_decompose_rejects_one_dimensional_input() -> None:
    with pytest.raises(ValueError, match="draws per seed"):
        variance_decompose(np.array([1.0, 2.0, 3.0]))


def test_variance_decompose_rejects_a_single_draw_per_seed() -> None:
    # shape (n, 1): 2-D but only one graph draw, so the decomposition is undefined.
    with pytest.raises(ValueError, match="draws per seed"):
        variance_decompose(np.array([[1.0], [2.0], [3.0]]))


def test_variance_decompose_rejects_more_than_two_dimensions() -> None:
    with pytest.raises(ValueError, match="draws per seed"):
        variance_decompose(np.zeros((2, 2, 2)))
