"""In-edge concentration: how unequally citations land *within* a publication cohort.

This is the construct WS2 set out to measure and never measured cleanly.
`age_restricted_concentration` took the Gini of **all-time** `cited_by_count` with only a
minimum-age filter, so a 1970 cohort had
55 years to accrue and a 2010 cohort 14 — the trend confounds concentration with accrual time, the
same defect that made the CD-index reverse under a fixed window (WS3 bridge C-2c).

The fix is a **fixed forward-citation window**: every paper is scored on citations received within
`[t, t+W]`, so every cohort gets the same accrual opportunity, and only cohorts with `t + W ≤`
the last complete citer year are used (no censoring). Then concentration is measured *across the
cohort's papers*, on three functional forms (spec `docs/concentration-measures.md`, R8):

* `gini` of the per-paper windowed in-degree (zeros included — uncited papers belong to the cohort);
* `top_decile_share` — the fraction of the cohort's citations held by its top 10% of papers;
* `entropy_deficit` — `1 − H/log(n)` over the per-paper citation shares.

Every function here is pure and graph-source-agnostic: it takes per-paper `(year, indegree, field)`
arrays. Local in-sample `uptake_W` and the 24M in-population in-degree run the identical code, which
is what lets the measure be validated locally before it is trusted on the population. The one thing
the caller must supply correctly is the in-degree itself — see the runner for the graph it used.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from dataclasses import field as dataclass_field

import numpy as np
import numpy.typing as npt

from .canonical_metrics import gini

FloatArray = npt.NDArray[np.float64]
IntArray = npt.NDArray[np.int64]

CANON_DECILE = 0.10


def top_decile_share(indegree: Sequence[int] | IntArray, frac: float = CANON_DECILE) -> float:
    """Share of a cohort's citations held by its most-cited `frac` of papers.

    Ranks by in-degree and sums the citations of the top `frac` of *papers* (not of citations), so a
    cohort where a few works dominate scores high and an even cohort scores near `frac`. Uncited
    papers stay in the denominator of the paper count, which is why a growing tail of never-cited
    work pushes this up — that is concentration, correctly.
    """
    values = np.sort(np.asarray(indegree, dtype=np.float64))[::-1]
    total = values.sum()
    if total <= 0 or values.size == 0:
        return 0.0
    n_top = max(1, int(round(frac * values.size)))
    return float(values[:n_top].sum() / total)


def entropy_deficit(indegree: Sequence[int] | IntArray) -> float:
    """`1 − H/log(n)` over per-paper citation shares — 0 when citations are spread evenly.

    Normalized by `log(n)` over the full cohort size `n`, so cohorts of different sizes are
    comparable and a cohort that concentrates its citations onto fewer papers scores higher.
    """
    values = np.asarray(indegree, dtype=np.float64)
    n = values.size
    total = values.sum()
    if n <= 1 or total <= 0:
        return 0.0
    p = values[values > 0] / total
    return float(1.0 - (-(p * np.log(p)).sum()) / np.log(n))


@dataclass(frozen=True)
class CohortRow:
    """One publication cohort's citation concentration beside its matched null."""

    year: int
    field: str
    n_papers: int
    n_citations: int
    gini: float
    top_decile_share: float
    entropy_deficit: float
    null_gini: float
    null_gini_band: tuple[float, float]

    @property
    def excess_gini(self) -> float:
        return self.gini - self.null_gini


def _null_gini_distribution(
    rng: np.random.Generator, n_papers: int, n_citations: int, n_replicates: int
) -> FloatArray:
    """Gini of `n_citations` spread multinomially-uniform over `n_papers`.

    The matched null: same cohort size, same citation volume, concentration removed. Whatever Gini
    this leaves is what cohort size and citation count force arithmetically — the birthday-style
    inequality that `ref_gini` mistook for a canon.
    """
    if n_papers <= 1 or n_citations <= 0:
        return np.zeros(n_replicates, dtype=np.float64)
    draws = rng.multinomial(n_citations, np.full(n_papers, 1.0 / n_papers), size=n_replicates)
    return np.array([gini(row.astype(np.float64)) for row in draws], dtype=np.float64)


def cohort_concentration(
    years: Sequence[int] | IntArray,
    indegree: Sequence[int] | IntArray,
    fields: Sequence[str],
    *,
    field_name: str,
    min_papers: int = 200,
    last_complete_year: int,
    window: int,
    n_replicates: int = 200,
    seed: int = 20260722,
) -> list[CohortRow]:
    """Per-cohort citation concentration for one field, matched null included.

    Only cohorts with `year + window ≤ last_complete_year` are returned: a shorter forward window
    would censor recent cohorts and manufacture exactly the accrual trend this measure exists to
    avoid.
    """
    year_arr = np.asarray(years, dtype=np.int64)
    indeg_arr = np.asarray(indegree, dtype=np.int64)
    field_arr = np.asarray(fields, dtype=object)
    rng = np.random.default_rng(seed)

    rows: list[CohortRow] = []
    in_field = field_arr == field_name
    for year in range(int(year_arr.min()), last_complete_year - window + 1):
        cohort = in_field & (year_arr == year)
        n = int(cohort.sum())
        if n < min_papers:
            continue
        cites = indeg_arr[cohort]
        total = int(cites.sum())
        null_draws = _null_gini_distribution(rng, n, total, n_replicates)
        rows.append(
            CohortRow(
                year=year,
                field=field_name,
                n_papers=n,
                n_citations=total,
                gini=gini(cites.astype(np.float64)),
                top_decile_share=top_decile_share(cites),
                entropy_deficit=entropy_deficit(cites),
                null_gini=float(null_draws.mean()),
                null_gini_band=(
                    float(np.percentile(null_draws, 2.5)),
                    float(np.percentile(null_draws, 97.5)),
                ),
            )
        )
    return rows


def volume_controlled_gini(
    rng: np.random.Generator,
    indegree: Sequence[int] | IntArray,
    rate: float,
    *,
    n_replicates: int = 200,
) -> float:
    """Gini of a cohort thinned to a common citations-per-paper `rate`, averaged over replicates.

    Gini of a raw count vector depends on its mean: a cohort with few citations per paper is
    mechanically more unequal (more zeros) than a citation-rich one, so a bare Gini trend confounds
    concentration with citation *density*. Subtracting a matched null does **not** fix this — the
    null's own Gini falls as density rises, so observed-minus-null tracks density instead.

    The clean control holds density fixed. Each cohort is thinned to `round(rate * n_papers)`
    citations, drawn multinomially in proportion to the observed in-degree, so every cohort carries
    the same citations-per-paper and only the *shape* of its distribution can move the Gini. `rate`
    must be ≤ every cohort's own rate (pick the series minimum) so every cohort can be down-thinned
    rather than invented.
    """
    values = np.asarray(indegree, dtype=np.float64)
    n = values.size
    total = values.sum()
    budget = int(round(rate * n))
    if n == 0 or total <= 0 or budget <= 0:
        return 0.0
    probabilities = values / total
    draws = rng.multinomial(budget, probabilities, size=n_replicates)
    return float(np.mean([gini(row.astype(np.float64)) for row in draws]))


@dataclass
class FieldConcentration:
    """A field's cohort-concentration series at one window."""

    field: str
    window: int
    rows: list[CohortRow] = dataclass_field(default_factory=list)

    def years(self) -> FloatArray:
        return np.array([r.year for r in self.rows], dtype=np.float64)

    def series(self, attr: str) -> FloatArray:
        return np.array([getattr(r, attr) for r in self.rows], dtype=np.float64)

    def slope(self, attr: str) -> float:
        if len(self.rows) < 2:
            return float("nan")
        return float(np.polyfit(self.years(), self.series(attr), 1)[0])
