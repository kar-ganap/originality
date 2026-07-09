# Lifted verbatim from whitespace_2/src/whitespace2/canonical_metrics.py (Originality WS2) — behaviour-preserving copy.
"""Concentration metrics for a non-negative distribution (e.g. per-work citation
counts): the Gini coefficient and the top-``k`` share.
"""

from __future__ import annotations

from typing import Any

import numpy as np


def gini(values: Any) -> float:
    """Gini coefficient of a non-negative distribution.

    ``0`` = perfect equality (all works cited equally), ``→1`` = maximal
    concentration (one work holds all citations). Returns 0.0 on empty or
    all-zero input (no concentration defined).
    """
    v = np.asarray(values, dtype=np.float64)
    v = v[~np.isnan(v)]
    n = v.size
    if n == 0:
        return 0.0
    total = float(v.sum())
    if total <= 0.0:
        return 0.0
    # Mean absolute difference / (2 * mean) via the sorted-rank formula:
    #   G = (2·Σ i·x_(i)) / (n·Σx) − (n+1)/n   for x sorted ascending.
    x = np.sort(v)
    idx = np.arange(1, n + 1, dtype=np.float64)
    return float((2.0 * float((idx * x).sum())) / (n * total) - (n + 1) / n)


def top_k_share(values: Any, k_frac: float) -> float:
    """Fraction of the total held by the top ``k_frac`` of items.

    e.g. ``k_frac=0.1`` → share of citations captured by the most-cited
    10% of works. ``k`` is ``ceil(k_frac · N)`` (at least 1). Returns 0.0
    on empty or all-zero input.
    """
    v = np.asarray(values, dtype=np.float64)
    v = v[~np.isnan(v)]
    n = v.size
    if n == 0:
        return 0.0
    total = float(v.sum())
    if total <= 0.0:
        return 0.0
    k = max(1, int(np.ceil(k_frac * n)))
    top = np.sort(v)[::-1][:k]
    return float(top.sum() / total)
