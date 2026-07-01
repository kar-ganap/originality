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
  - ``age_restricted_concentration`` — the two above per publication year,
    but **only on years whose papers are ≥ ``min_age`` years old** at the
    snapshot. This is the citation-age-robust negative control (Phase-1.4
    pilot finding #1): raw citation Gini per publication year is
    accrual-confounded — recent papers are zero-inflated (a 2024 paper has
    ~0 citations), so their Gini artificially collapses and drags the
    "concentration rises over time" control negative. Gini is
    scale-invariant, so per-cohort rescaling is a no-op; ``counts_by_year``
    (needed for a fixed N-year window) is not in the corpus and doesn't
    reach back to 1970, so a fixed-window metric is unreconstructable for
    old papers. The tractable control is therefore **age restriction** —
    drop the immature recent years, report the trend on mature years, and
    sweep ``min_age`` (the N-floor) for sensitivity.

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


def age_restricted_concentration(
    publication_years: Any,
    cited_by_counts: Any,
    *,
    snapshot_year: int,
    min_age: int,
    k_frac: float = 0.1,
    min_papers: int = 1,
) -> list[dict[str, Any]]:
    """Per-year citation concentration on papers ≥ ``min_age`` years old.

    For each publication year ``Y`` with ``snapshot_year − Y ≥ min_age``
    (i.e. ``Y ≤ snapshot_year − min_age``) and at least ``min_papers``
    papers, computes :func:`gini` and :func:`top_k_share` over that year's
    total ``cited_by_count``. Immature recent years (age ``< min_age``) are
    dropped — their citation distributions are zero-inflated and their Gini
    artificially collapses (pilot finding #1), which would otherwise drag the
    "concentration rises over time" negative control negative.

    ``publication_years`` / ``cited_by_counts`` are parallel arrays over
    papers; non-finite years are ignored. Returns a list of
    ``{"year", "n", "gini", "top_k_share"}`` rows sorted ascending by year
    (empty if no year is old enough — the caller must NOT interpret an empty
    control). Sweep ``min_age`` (e.g. 3 / 5 / 10) for the N-sensitivity the
    control requires: a residual accrual gradient remains across the retained
    years (mature years still differ in accrual), so the control's job is the
    directional claim — concentration rises across the mature decades — not a
    point estimate at any single ``min_age``.
    """
    years = np.asarray(publication_years, dtype=np.float64)
    cites = np.asarray(cited_by_counts, dtype=np.float64)
    max_year = snapshot_year - min_age

    rows: list[dict[str, Any]] = []
    finite = np.isfinite(years)
    eligible = np.unique(years[finite & (years <= max_year)])
    for y in eligible:
        mask = years == y
        c = cites[mask]
        if c.size < min_papers:
            continue
        rows.append({
            "year": int(y),
            "n": int(c.size),
            "gini": gini(c),
            "top_k_share": top_k_share(c, k_frac),
        })
    return rows
