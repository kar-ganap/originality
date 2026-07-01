"""Tests for the pre-registered divergence estimator (Test I).

Synthetic per-year series exercise the OLS trend test and the full
divergence decision rule (both primary semantic metrics show a
negative-significant semantic/demographic ratio slope + directional 3rd;
canonical concentration as a rising negative control).
"""

from __future__ import annotations

from whitespace2.divergence import divergence_test, ols_trend

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
