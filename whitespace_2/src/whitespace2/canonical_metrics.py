"""Canonical-concentration metrics for the Stage-2 divergence test.

Per ``docs/desiderata.md`` §8, canonical concentration uses ≥2 metrics.
These operate on a cell's citation counts (``cited_by_count``, present in
the §0 corpus) — no embeddings needed. In the pre-registered divergence
test (phase-0.2-plan.md "Test I") canonical concentration is the
**negative control**: it should RISE over time; if it stays flat the
analysis substrate is broken.

  - ``gini`` — Gini coefficient of the citation distribution.
  - ``top_k_share`` — fraction of total citations held by the top
    ``k_frac`` of works.

(The reference-list Spearman-top-N / Chu-Evans canonicity metric is a
Stage-2 addition — it needs ``referenced_works`` overlap across years —
and is not implemented here.)
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
