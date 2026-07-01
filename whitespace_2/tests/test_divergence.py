"""Tests for the pre-registered divergence estimator (Test I).

Synthetic per-year series exercise the OLS trend test and the full
divergence decision rule (both primary semantic metrics show a
negative-significant semantic/demographic ratio slope + directional 3rd;
canonical concentration as a rising negative control).
"""

from __future__ import annotations

from whitespace2.divergence import (
    divergence_test,
    ols_trend,
    permutation_slope_test,
    residual_trend,
    standardized_effect,
)

_YEARS = list(range(1970, 2025))  # 55 points
_N = len(_YEARS)


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


def _rising_demographic() -> list[float]:
    return [0.30 + 0.004 * i for i in range(_N)]  # 0.30 → 0.516


def test_divergence_confirmed() -> None:
    """Semantic falling while demographic rises → ratio falls → both
    primaries negative-significant + 3rd directional → divergence; canonical
    rising → substrate ok."""
    dem = _rising_demographic()
    semantic = {
        "cluster_entropy": [5.0 - 0.015 * i for i in range(_N)],
        "effective_dimensionality": [200.0 - 1.5 * i for i in range(_N)],
        "mean_pairwise_cosine": [0.50 - 0.0015 * i for i in range(_N)],
    }
    canonical = [0.40 + 0.003 * i for i in range(_N)]  # rising
    res = divergence_test(_YEARS, dem, semantic, canonical)

    assert res["primary_both_neg_significant"] is True
    assert res["secondary_directional_agreement"] is True
    assert res["divergence_confirmed"] is True
    assert res["substrate_ok"] is True
    assert res["verdict"] == "divergence"
    # every ratio trend is a significant decline
    for m in ["cluster_entropy", "effective_dimensionality"]:
        assert res["ratio_trends"][m]["direction"] == "down"
        assert res["ratio_trends"][m]["significant"] is True


def test_divergence_null_tandem() -> None:
    """Semantic proportional to demographic → ratio constant → no negative
    trend → successful null (Claim #13 disconfirmed on this synthetic)."""
    dem = _rising_demographic()
    semantic = {  # each = const × demographic → ratio exactly flat
        "cluster_entropy": [15.0 * d for d in dem],
        "effective_dimensionality": [500.0 * d for d in dem],
        "mean_pairwise_cosine": [1.2 * d for d in dem],
    }
    canonical = [0.40 + 0.003 * i for i in range(_N)]  # rising (substrate ok)
    res = divergence_test(_YEARS, dem, semantic, canonical)

    assert res["divergence_confirmed"] is False
    assert res["substrate_ok"] is True
    assert res["verdict"] == "null_tandem"


def test_divergence_substrate_broken() -> None:
    """Even with a semantic decline, a FLAT canonical negative control means
    the analysis substrate is broken — verdict overrides to substrate_broken."""
    dem = _rising_demographic()
    semantic = {
        "cluster_entropy": [5.0 - 0.015 * i for i in range(_N)],
        "effective_dimensionality": [200.0 - 1.5 * i for i in range(_N)],
        "mean_pairwise_cosine": [0.50 - 0.0015 * i for i in range(_N)],
    }
    canonical = [0.40] * _N  # flat → substrate broken
    res = divergence_test(_YEARS, dem, semantic, canonical)

    assert res["substrate_ok"] is False
    assert res["verdict"] == "substrate_broken"


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


def test_divergence_effect_floor_gates_confirmation() -> None:
    """PA-2: a permutation-significant, downward ratio is NOT confirmed if its
    total standardized change is below the effect floor. Same synthetic as the
    confirmed case (~3.46σ change) is rejected under a 5σ floor, accepted at 0.1σ."""
    dem = _rising_demographic()
    semantic = {
        "cluster_entropy": [5.0 - 0.015 * i for i in range(_N)],
        "effective_dimensionality": [200.0 - 1.5 * i for i in range(_N)],
        "mean_pairwise_cosine": [0.50 - 0.0015 * i for i in range(_N)],
    }
    canonical = [0.40 + 0.003 * i for i in range(_N)]
    hi = divergence_test(_YEARS, dem, semantic, canonical,
                         n_perm=2000, effect_floor=5.0)
    assert hi["divergence_confirmed"] is False   # ~3.46σ < 5σ floor
    lo = divergence_test(_YEARS, dem, semantic, canonical,
                         n_perm=2000, effect_floor=0.1)
    assert lo["divergence_confirmed"] is True
    # the effect size is surfaced per ratio metric
    eff = lo["ratio_trends"]["cluster_entropy"]["effect"]["total_change_sd"]
    assert eff is not None and eff < 0


def test_residual_trend_recovers_year_effect() -> None:
    """A genuine year effect (control independent of year) is recovered + sig."""
    import numpy as np
    rng = np.random.default_rng(0)
    x = np.arange(55.0)
    ctrl = rng.normal(size=55)          # independent of year
    y = 2.0 * x + 0.1 * rng.normal(size=55)
    r = residual_trend(x, y, [ctrl], n_perm=2000, seed=1)
    assert abs(r["year_coef"] - 2.0) < 0.1
    assert r["significant"] is True
    assert r["year_vif"] < 2.0          # control ⊥ year → low collinearity


def test_residual_trend_year_effect_vanishes_after_control() -> None:
    """When the trend is entirely explained by a control, the partial year
    coefficient collapses to ~0 (not significant) — the WS-F question."""
    import numpy as np
    rng = np.random.default_rng(2)
    x = np.arange(55.0)
    ctrl = x + 3.0 * rng.normal(size=55)      # correlated w/ year, not identical
    y = 5.0 * ctrl + 0.01 * rng.normal(size=55)   # y driven entirely by ctrl
    r = residual_trend(x, y, [ctrl], n_perm=2000, seed=1)
    assert abs(r["year_coef"]) < 0.5
    assert r["significant"] is False


def test_residual_trend_flags_collinearity() -> None:
    """Perfectly collinear control (= year) → huge VIF (year effect unreliable)."""
    import numpy as np
    x = np.arange(55.0)
    r = residual_trend(x, 2.0 * x, [x], n_perm=200, seed=1)
    assert r["year_vif"] > 100.0


def test_divergence_handles_zero_demographic() -> None:
    """Years with zero demographic plurality are dropped from the ratio
    (no divide-by-zero); the test still runs on the remaining years."""
    dem = [0.0] + _rising_demographic()[1:]  # first year degenerate
    semantic = {
        "cluster_entropy": [5.0 - 0.015 * i for i in range(_N)],
        "effective_dimensionality": [200.0 - 1.5 * i for i in range(_N)],
        "mean_pairwise_cosine": [0.50 - 0.0015 * i for i in range(_N)],
    }
    res = divergence_test(_YEARS, dem, semantic)
    # cluster_entropy ratio computed on 54 (not 55) years
    assert res["ratio_trends"]["cluster_entropy"]["n"] == _N - 1
