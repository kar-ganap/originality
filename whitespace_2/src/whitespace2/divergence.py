"""The pre-registered demographic-vs-semantic divergence test (Test I).

Implements the headline statistic locked in `docs/phases/phase-0.2-plan.md`
"Test I" (to be consolidated into the Stage 2 plan per desideratum §5):

  OLS regression of the (semantic plurality / demographic plurality) ratio
  on year shows a **negative slope significant at p<0.05 two-tailed** across
  BOTH primary semantic metrics (cluster entropy + effective dimensionality),
  with **directional agreement** on the secondary (mean pairwise cosine).

  - Fail (a successful NULL): both plurality series rise in tandem → the
    ratio has no significant negative trend → Claim #13 disconfirmed.
  - Negative control: canonical concentration (citation Gini / top-k share)
    should RISE over time. If it is flat, the analysis substrate is broken.

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
        ratio_trends[metric] = ols_trend(
            years_arr[kept], ratios, alpha=alpha,
        )

    def _neg_sig(m: str) -> bool:
        t = ratio_trends.get(m, {})
        return bool(t.get("significant")) and t.get("direction") == "down"

    def _neg_dir(m: str) -> bool:
        return ratio_trends.get(m, {}).get("direction") == "down"

    primary_both = all(_neg_sig(m) for m in primary_metrics)
    secondary_agree = all(_neg_dir(m) for m in secondary_metrics)
    divergence_confirmed = primary_both and secondary_agree

    negative_control: dict[str, Any] | None = None
    substrate_ok = True
    if canonical is not None:
        negative_control = ols_trend(years, canonical, alpha=alpha)
        # Substrate is sound iff canonical concentration is rising
        # (significant positive slope).
        substrate_ok = bool(
            negative_control["significant"]
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
