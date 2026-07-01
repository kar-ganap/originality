"""The pre-registered demographic-vs-semantic divergence test (Test I).

Implements the headline statistic locked in `docs/phases/phase-2.0-plan.md` §5
(amended Phase 2.2 PA-2):

  OLS slope of the (semantic plurality / demographic plurality) ratio on year,
  with significance from a **year-label permutation null** (observed slope
  beyond the 99.5/0.5 percentile) AND an **effect-size floor** (total
  standardized change ≥ ~0.1σ) — NOT a bare p<0.05. Divergence is CONFIRMED iff
  BOTH primary semantic ratios (cluster entropy + effective dimensionality)
  clear that gate downward, with **directional agreement** on the secondary
  (mean pairwise cosine).

  - Fail (a successful NULL): both plurality series rise in tandem → the
    ratio has no material negative trend → Claim #13 disconfirmed.
  - Negative control: canonical concentration (Chu-Evans reference canonicity
    primary; age-restricted citation Gini/top-k secondary) should RISE over
    time (permutation-significant). If flat, the analysis substrate is broken.

This module only runs the statistic on per-year series; computing those
series (demographic from the Phase-1.3 coverage pipeline, semantic from
`semantic_metrics`, canonical from `canonical_metrics`) is the caller's job.
"""

from __future__ import annotations

from typing import Any

import numpy as np

_PRIMARY = ("cluster_entropy", "effective_dimensionality")
_SECONDARY = ("mean_pairwise_cosine",)


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


def _ratio(numerator: Any, denominator: Any) -> tuple[list[float], list[int]]:
    """Elementwise num/den, dropping positions where den ≤ 0 or is NaN.

    Returns (ratios, kept_indices)."""
    num = np.asarray(numerator, dtype=np.float64)
    den = np.asarray(denominator, dtype=np.float64)
    ratios: list[float] = []
    kept: list[int] = []
    for i in range(num.size):
        if den[i] > 0 and not (np.isnan(num[i]) or np.isnan(den[i])):
            ratios.append(float(num[i] / den[i]))
            kept.append(i)
    return ratios, kept


def divergence_test(
    years: Any,
    demographic: Any,
    semantic: dict[str, Any],
    canonical: Any | None = None,
    *,
    primary_metrics: tuple[str, ...] = _PRIMARY,
    secondary_metrics: tuple[str, ...] = _SECONDARY,
    alpha: float = 0.05,
    n_perm: int = 10_000,
    perm_seed: int = 0,
    perm_alpha: float = 0.01,
    effect_floor: float = 0.1,
) -> dict[str, Any]:
    """Run the pre-registered divergence test on per-year series.

    Args:
      years: per-year x-axis.
      demographic: demographic plurality per year (denominator).
      semantic: ``{metric_name: per-year semantic plurality}``; must
        include the ``primary_metrics`` and ``secondary_metrics``.
      canonical: canonical concentration per year (negative control).

    Returns a verdict dict:
      - ``ratio_trends``: per-metric ``ols_trend`` on (semantic/demographic).
      - ``primary_both_neg_significant``: both primaries negative + p<alpha.
      - ``secondary_directional_agreement``: all secondaries slope < 0.
      - ``divergence_confirmed``: primary AND secondary conditions met.
      - ``negative_control``: ``ols_trend`` on canonical (expected: up).
      - ``substrate_ok``: canonical slope > 0 (rising) — else substrate broken.
      - ``verdict``: "divergence" | "null_tandem" | "substrate_broken".
    """
    years_arr = np.asarray(years, dtype=np.float64)

    ratio_trends: dict[str, dict[str, Any]] = {}
    for metric, series in semantic.items():
        ratios, kept = _ratio(series, demographic)
        yk = years_arr[kept]
        t = ols_trend(yk, ratios, alpha=alpha)
        t["permutation"] = permutation_slope_test(
            yk, ratios, n_perm=n_perm, seed=perm_seed, alpha=perm_alpha,
        )
        t["effect"] = standardized_effect(yk, ratios)
        ratio_trends[metric] = t

    def _neg_sig(m: str) -> bool:
        # PA-2: negative slope that clears the permutation null AND the
        # ~0.1σ total-effect floor (not a bare p<0.05).
        t = ratio_trends.get(m, {})
        tcs = t.get("effect", {}).get("total_change_sd")
        return (
            bool(t.get("permutation", {}).get("significant"))
            and t.get("direction") == "down"
            and tcs is not None and abs(tcs) >= effect_floor
        )

    def _neg_dir(m: str) -> bool:
        return ratio_trends.get(m, {}).get("direction") == "down"

    primary_both = all(_neg_sig(m) for m in primary_metrics)
    secondary_agree = all(_neg_dir(m) for m in secondary_metrics)
    divergence_confirmed = primary_both and secondary_agree

    negative_control: dict[str, Any] | None = None
    substrate_ok = True
    if canonical is not None:
        negative_control = ols_trend(years, canonical, alpha=alpha)
        negative_control["permutation"] = permutation_slope_test(
            years, canonical, n_perm=n_perm, seed=perm_seed, alpha=perm_alpha,
        )
        # Substrate is sound iff canonical concentration is RISING and clears
        # the permutation null (PA-2 significance for the negative control too).
        substrate_ok = bool(
            negative_control["permutation"]["significant"]
            and negative_control["direction"] == "up",
        )

    if canonical is not None and not substrate_ok:
        verdict = "substrate_broken"
    elif divergence_confirmed:
        verdict = "divergence"
    else:
        verdict = "null_tandem"

    return {
        "alpha": alpha,
        "ratio_trends": ratio_trends,
        "primary_both_neg_significant": primary_both,
        "secondary_directional_agreement": secondary_agree,
        "divergence_confirmed": divergence_confirmed,
        "negative_control": negative_control,
        "substrate_ok": substrate_ok,
        "verdict": verdict,
    }
