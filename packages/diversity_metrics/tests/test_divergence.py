"""Tests for the trend / divergence statistics (lifted from WS2 test_divergence.py).

Covers the three lifted estimators: ols_trend, permutation_slope_test, and
standardized_effect. (The WS2 divergence_test / residual_trend orchestration was
not graduated, so their tests are not ported.)
"""

from __future__ import annotations

from diversity_metrics.divergence import (
    ols_trend,
    permutation_slope_test,
    standardized_effect,
)


def test_ols_trend_clean_line() -> None:
    """y = 2x + 1 → slope 2, highly significant, direction up."""
    x = list(range(11))
    y = [2 * xi + 1 for xi in x]
    t = ols_trend(x, y)
    assert abs(t["slope"] - 2.0) < 1e-9
    assert t["pvalue"] < 1e-6
    assert t["significant"] is True
    assert t["direction"] == "up"
    assert abs(t["r_squared"] - 1.0) < 1e-9


def test_ols_trend_flat_and_degenerate() -> None:
    """Constant series → not significant, flat; n<3 → flat/degenerate."""
    flat = ols_trend(list(range(11)), [5.0] * 11)
    assert flat["significant"] is False
    assert flat["direction"] == "flat"
    deg = ols_trend([1, 2], [3.0, 4.0])
    assert deg["n"] == 2
    assert deg["significant"] is False
    assert deg["direction"] == "flat"


def test_permutation_slope_test_clean_vs_flat() -> None:
    """A clean monotone line beats every shuffle (perm p ≈ 1/(n+1) < 0.01);
    a flat/near-flat series does not."""
    x = list(range(55))
    up = permutation_slope_test(x, [2.0 * i for i in x], n_perm=2000, seed=1)
    assert up["significant"] is True
    assert up["perm_pvalue"] < 0.01
    flat = permutation_slope_test(x, [5.0] * 55, n_perm=2000, seed=1)
    assert flat["significant"] is False
    deg = permutation_slope_test([1, 2], [3.0, 4.0], n_perm=100)
    assert deg["significant"] is False and deg["n"] == 2


def test_standardized_effect_ramp() -> None:
    """A clean linear ramp spans ~sqrt(12) ≈ 3.46 SDs total; sign tracks slope."""
    x = list(range(55))
    up = standardized_effect(x, [0.01 * i for i in x])
    # discrete n=55 ramp spans ~3.37 SDs (→ sqrt(12) ≈ 3.46 in the continuous limit)
    assert 3.3 < up["total_change_sd"] < 3.5
    assert up["slope_sd_per_year"] > 0
    down = standardized_effect(x, [1.0 - 0.01 * i for i in x])
    assert down["total_change_sd"] < -3.0
    const = standardized_effect(x, [7.0] * 55)
    assert const["total_change_sd"] == 0.0
