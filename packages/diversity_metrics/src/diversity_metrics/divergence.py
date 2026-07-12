# Lifted verbatim from whitespace_2/src/whitespace2/divergence.py (Originality WS2) — behaviour-preserving copy.
"""Trend / divergence statistics on per-year series.

  - ``ols_trend`` — OLS of ``values ~ years`` with two-tailed slope significance.
  - ``permutation_slope_test`` — year-label permutation test on the OLS slope.
  - ``standardized_effect`` — slope as a standardized effect size.
"""

from __future__ import annotations

from typing import Any

import numpy as np


def ols_trend(
    years: Any,
    values: Any,
    *,
    alpha: float = 0.05,
) -> dict[str, Any]:
    """OLS of ``values ~ years``; two-tailed significance on the slope.

    Returns ``{slope, intercept, pvalue, stderr, r_squared, n, significant,
    direction}``. ``direction`` ∈ {"up","down","flat"}. Degenerate input
    (n<3 or zero year-variance) → ``significant=False``, ``direction="flat"``,
    ``pvalue=None``.
    """
    from scipy.stats import linregress

    x = np.asarray(years, dtype=np.float64)
    y = np.asarray(values, dtype=np.float64)
    mask = ~(np.isnan(x) | np.isnan(y))
    x, y = x[mask], y[mask]
    n = int(x.size)
    if n < 3 or float(np.ptp(x)) == 0.0:
        return {"slope": None, "intercept": None, "pvalue": None,
                "stderr": None, "r_squared": None, "n": n,
                "significant": False, "direction": "flat"}

    res = linregress(x, y)
    slope = float(res.slope)
    pvalue = float(res.pvalue)
    significant = np.isfinite(pvalue) and pvalue < alpha
    if not significant or slope == 0.0:
        direction = "flat" if slope == 0.0 else ("down" if slope < 0 else "up")
    else:
        direction = "down" if slope < 0 else "up"
    return {
        "slope": slope,
        "intercept": float(res.intercept),
        "pvalue": pvalue,
        "stderr": float(res.stderr),
        "r_squared": float(res.rvalue) ** 2,
        "n": n,
        "significant": bool(significant),
        "direction": direction,
    }


def permutation_slope_test(
    years: Any,
    values: Any,
    *,
    n_perm: int = 10_000,
    seed: int = 0,
    alpha: float = 0.01,
) -> dict[str, Any]:
    """Year-label permutation test on the OLS slope (PA-2 decision gate).

    Shuffles the year labels ``n_perm`` times, recomputes the slope each time
    → the null distribution of "a slope from noise alone in THIS data". The
    two-tailed permutation p-value is the fraction of permuted slopes at least
    as extreme (in ``|·|``) as the observed (add-one smoothed). ``significant``
    iff ``perm_pvalue < alpha`` — ``alpha=0.01`` is the pre-registered 99.5/0.5
    percentile gate. Unit-safe: imports none of the CD-critique's σ units.

    Degenerate input (n<3 or zero year-variance) → ``significant=False``.
    """
    x = np.asarray(years, dtype=np.float64)
    y = np.asarray(values, dtype=np.float64)
    mask = ~(np.isnan(x) | np.isnan(y))
    x, y = x[mask], y[mask]
    n = int(x.size)
    if n < 3 or float(np.ptp(x)) == 0.0:
        return {"slope": None, "perm_pvalue": None, "n": n,
                "n_perm": n_perm, "alpha": alpha, "significant": False}
    xc = x - x.mean()
    varx = float((xc**2).sum())
    obs = float((xc * (y - y.mean())).sum() / varx)
    rng = np.random.default_rng(seed)
    idx = np.argsort(rng.random((n_perm, n)), axis=1)   # random permutations
    yp = y[idx]                                          # (n_perm, n)
    yp_c = yp - yp.mean(axis=1, keepdims=True)
    perm_slopes = (yp_c @ xc) / varx                    # (n_perm,)
    exceed = int(np.sum(np.abs(perm_slopes) >= abs(obs)))
    perm_p = (1 + exceed) / (n_perm + 1)
    return {"slope": obs, "perm_pvalue": float(perm_p), "n": n,
            "n_perm": n_perm, "alpha": alpha,
            "significant": bool(perm_p < alpha)}


def standardized_effect(years: Any, values: Any) -> dict[str, Any]:
    """Slope as a standardized effect (PA-2 effect-size floor).

    Returns ``slope_sd_per_year`` (= slope / sd(values)) and
    ``total_change_sd`` (= slope × year-range / sd(values)) — the fitted change
    over the window in units of the series' own SD. The PA-2 floor rejects a
    permutation-significant slope whose ``|total_change_sd| < ~0.1σ`` (the
    CD-critique "treat below ~0.1σ as noise" line); ``~1σ`` marks a
    "substantial" divergence. A clean linear ramp has ``|total_change_sd|`` ≈
    ``sqrt(12)`` ≈ 3.46 (its full rise spans ~3.46 SDs).

    Degenerate input → ``None``; zero-variance series → 0.0.
    """
    x = np.asarray(years, dtype=np.float64)
    y = np.asarray(values, dtype=np.float64)
    mask = ~(np.isnan(x) | np.isnan(y))
    x, y = x[mask], y[mask]
    n = int(x.size)
    if n < 3 or float(np.ptp(x)) == 0.0:
        return {"slope": None, "sd": None, "slope_sd_per_year": None,
                "total_change_sd": None, "n": n}
    xc = x - x.mean()
    slope = float((xc * (y - y.mean())).sum() / (xc**2).sum())
    sd = float(np.std(y, ddof=1))
    if sd == 0.0:
        return {"slope": slope, "sd": 0.0, "slope_sd_per_year": 0.0,
                "total_change_sd": 0.0, "n": n}
    yr = float(x.max() - x.min())
    return {"slope": slope, "sd": sd, "slope_sd_per_year": slope / sd,
            "total_change_sd": slope * yr / sd, "n": n}
