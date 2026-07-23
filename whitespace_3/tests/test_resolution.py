"""Tests for the resolution-map noise-floor diagnostics (design §3, pre-reg locked 2026-07-22).

These are the spec-independent primitives: they know nothing about the diagnostic grid, the SESOI
values, or the model. They implement the classification rule and the variance decomposition, and are
tested against known-answer synthetic inputs before ever touching `channel.run`.
"""

from __future__ import annotations

import numpy as np
import pytest

from whitespace3.resolution import (
    classify,
    crossover_exists,
    mean_ci,
    seed_cv,
    variance_decompose,
)

# --- seed_cv ---------------------------------------------------------------------------------


def test_seed_cv_is_zero_for_a_deterministic_output() -> None:
    assert seed_cv(np.full(30, 1.0 + 5.0)) == pytest.approx(0.0, abs=1e-15)


def test_seed_cv_matches_std_over_mean() -> None:
    values = np.array([2.0, 4.0, 6.0])
    assert seed_cv(values) == pytest.approx(float(np.std(values)) / float(np.mean(values)))


def test_seed_cv_handles_zero_mean_without_dividing_by_zero() -> None:
    # centered noise: mean ~0. CV is undefined; the function must return inf, not raise.
    assert np.isinf(seed_cv(np.array([-1.0, 1.0, -1.0, 1.0])))


# --- classify (the 4-way rule) ---------------------------------------------------------------


def test_deterministic_flat_when_no_lever_response() -> None:
    # zero seed spread AND the effect is below the meaningful floor.
    assert classify(effect=0.0, ci_lo=0.0, ci_hi=0.0, sesoi=0.1, seed_cv_level=0.0) == \
        "deterministic-flat"


def test_deterministic_clock_when_response_is_large_but_noiseless() -> None:
    # C = 1 + t: no seed spread, but a real nonzero response to the lever.
    assert classify(effect=1.0, ci_lo=1.0, ci_hi=1.0, sesoi=0.1, seed_cv_level=0.0) == \
        "deterministic-clock"


def test_stochastic_with_signal_needs_ci_excluding_zero_and_effect_above_sesoi() -> None:
    assert classify(effect=-0.3, ci_lo=-0.4, ci_hi=-0.2, sesoi=0.1, seed_cv_level=0.2) == \
        "stochastic-with-signal"


def test_stochastic_noise_dominated_when_ci_includes_zero() -> None:
    assert classify(effect=-0.3, ci_lo=-0.5, ci_hi=0.1, sesoi=0.1, seed_cv_level=0.2) == \
        "stochastic-noise-dominated"


def test_stochastic_noise_dominated_when_effect_below_sesoi_even_if_ci_excludes_zero() -> None:
    # a CI can exclude zero for a trivially small effect; that is not usable.
    assert classify(effect=-0.02, ci_lo=-0.03, ci_hi=-0.01, sesoi=0.1, seed_cv_level=0.2) == \
        "stochastic-noise-dominated"


def test_determinism_takes_priority_over_the_ci_test() -> None:
    # even with a degenerate CI excluding zero, near-zero seed spread means deterministic.
    assert classify(effect=1.0, ci_lo=0.9, ci_hi=1.1, sesoi=0.1, seed_cv_level=1e-9) == \
        "deterministic-clock"


# --- mean_ci ---------------------------------------------------------------------------------


def test_mean_ci_brackets_the_mean_and_narrows_with_n() -> None:
    rng = np.random.default_rng(0)
    small = mean_ci(rng.normal(0.0, 1.0, size=10), seed=0)
    large = mean_ci(rng.normal(0.0, 1.0, size=1000), seed=0)
    assert small[0] < 0.0 < small[1]
    assert (large[1] - large[0]) < (small[1] - small[0])  # more seeds → tighter CI


# --- crossover_exists (E4 internal-relevance standard) ---------------------------------------


def test_crossover_exists_on_a_ci_separated_sign_flip() -> None:
    # (point, ci_lo, ci_hi) in ascending-λ order: reliably + then reliably -.
    slopes = [(0.05, 0.02, 0.08), (-0.04, -0.07, -0.01)]
    assert crossover_exists(slopes) is True


def test_no_crossover_when_signs_never_flip() -> None:
    slopes = [(0.05, 0.02, 0.08), (0.03, 0.01, 0.06)]  # positive throughout
    assert crossover_exists(slopes) is False


def test_no_crossover_in_the_wrong_direction() -> None:
    # reliably - then reliably +: a flip, but not WS3's V→C direction.
    slopes = [(-0.05, -0.08, -0.02), (0.04, 0.01, 0.07)]
    assert crossover_exists(slopes) is False


def test_ci_including_zero_does_not_count_as_a_determined_sign() -> None:
    # the middle point straddles zero (mush) — the flip must be carried by CI-separated points.
    slopes = [(0.05, 0.02, 0.08), (-0.01, -0.05, 0.03), (-0.04, -0.09, -0.01)]
    assert crossover_exists(slopes) is True  # +ve at λ0, straddle at λ1, -ve at λ2 → still a flip


def test_all_straddling_zero_is_not_a_crossover() -> None:
    slopes = [(0.02, -0.03, 0.07), (-0.02, -0.07, 0.03)]  # both CIs include 0
    assert crossover_exists(slopes) is False


# --- variance_decompose ----------------------------------------------------------------------


def test_variance_decompose_recovers_a_known_split() -> None:
    """Synthetic nested data: known between-seed vs within-seed(graph) variance."""
    rng = np.random.default_rng(0)
    n_seeds, n_graph = 40, 40
    seed_effects = rng.normal(0.0, 3.0, size=n_seeds)          # between-seed sd = 3
    data = seed_effects[:, None] + rng.normal(0.0, 1.0, size=(n_seeds, n_graph))  # within sd = 1
    frac = variance_decompose(data)
    # between-seed variance 9, within 1 → seed fraction ~0.9. Tolerance for finite sampling.
    assert frac["seed_fraction"] == pytest.approx(0.9, abs=0.08)
    assert frac["graph_fraction"] == pytest.approx(0.1, abs=0.08)
    assert frac["seed_fraction"] + frac["graph_fraction"] == pytest.approx(1.0)
