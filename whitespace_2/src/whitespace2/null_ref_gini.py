"""Matched null for `ref_gini`, WS2's reported canonical-concentration metric.

`reference_canonicity` counts, for each publication year, how often each *referenced work* appears
across that year's reference lists, and reports the Gini of those counts. The counter only ever sees
targets that were cited at least once, so `ref_gini` is a statistic about **repeat citations**: when
almost every cited work appears exactly once the Gini is near zero, and it rises as repeats
accumulate.

That makes it sample-size dependent in a way nothing in the pipeline subtracts. Drawing more edges
from a fixed pool produces more repeats by the birthday principle alone, so a corpus whose reference
lists lengthen will show a rising `ref_gini` with no change in how canonical anything is.

This module runs the matched null. It preserves, per year and exactly:

* the number of papers, and each paper's **observed reference count**;
* the pool of citable targets, sized so the *expected* number of distinct targets matches what was
  observed (`calibrate_pool_size`) — so the null is pinned by the data, with no free parameter;

and destroys only the thing at issue: any tendency for particular works to attract citations. Every
target in the null pool is equally attractive. Whatever trend survives is arithmetic.

:func:`replay_reference_canonicity` is the positive control. It reconstructs the committed series
from the source parquet — including the seeded per-year subsample that produced it — so that a
matching replay licenses the null. A null without a validated replay measures its own bugs.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt

from .canonical_metrics import gini

FloatArray = npt.NDArray[np.float64]

N_CAP = 5000
"""Per-(field, year) subsample used by `experiments/phase-2.2/compute_series.py`."""

SERIES_SEED = 46
"""`_SEED` in the generating script. The replay must consume the stream identically."""

FIELDS = ("cs", "physics")
YEARS = range(1970, 2025)


def calibrate_pool_size(n_edges: int, n_distinct: int) -> float:
    """Pool size `P` whose expected distinct-target count matches the observed one.

    Drawing `E` edges uniformly from `P` equally-attractive targets yields, in expectation,
    `P * (1 - (1 - 1/P)^E)` distinct targets. This inverts that for `P` by bisection.

    Pinning `P` to the data is what keeps the null honest: the null is not free to be more or less
    spread out than the corpus it is standing in for. When `n_distinct >= n_edges` every edge landed
    on a fresh target, which no finite pool reproduces in expectation, so the pool is treated as
    effectively unbounded and returned as `inf`.
    """
    if n_edges <= 0 or n_distinct <= 0:
        return float("inf")
    if n_distinct >= n_edges:
        return float("inf")

    def expected_distinct(pool: float) -> float:
        return pool * (1.0 - (1.0 - 1.0 / pool) ** n_edges)

    low, high = float(n_distinct), float(n_distinct)
    while expected_distinct(high) < n_distinct and high < 1e15:
        high *= 2.0
    for _ in range(200):
        mid = 0.5 * (low + high)
        if expected_distinct(mid) < n_distinct:
            low = mid
        else:
            high = mid
    return 0.5 * (low + high)


def simulate_year_gini(
    rng: np.random.Generator, reference_counts: Sequence[int], pool_size: float
) -> tuple[float, int, int]:
    """One null replicate of a single year. Returns `(ref_gini, n_edges, n_distinct)`.

    Only the year's **total** edge count matters here, because every target is equally attractive:
    under uniform attachment the multiplicity distribution depends on how many edges were drawn, not
    on how they were parcelled out across papers. So the year is simulated as one vectorized draw.

    That collapses a real distinction — a paper does not cite the same work twice, so draws are
    without replacement *within* a paper. At the calibrated pool sizes (order 1e5-1e6 against ~17
    references per paper) the chance of a within-paper collision is about `n^2 / 2P`, roughly 2e-4,
    so the two agree to far less than the null's own spread. :func:`simulate_year_gini_per_paper`
    implements the exact version and a test pins the two together rather than leaving the
    approximation asserted.
    """
    total = int(sum(c for c in reference_counts if c > 0))
    if total <= 0:
        return 0.0, 0, 0
    if not np.isfinite(pool_size):
        # Every edge lands on a fresh target: all multiplicities are 1, so the Gini is exactly 0.
        return 0.0, total, total

    pool = max(int(round(pool_size)), 1)
    multiplicities = np.bincount(rng.integers(0, pool, size=total))
    multiplicities = multiplicities[multiplicities > 0].astype(np.float64)
    return gini(multiplicities), total, int(multiplicities.size)


def simulate_year_gini_per_paper(
    rng: np.random.Generator, reference_counts: Sequence[int], pool_size: float
) -> tuple[float, int, int]:
    """Exact null: each paper draws its own references *without replacement*.

    Correct but slow — it exists so the vectorized path above can be checked against it rather than
    trusted. Repeats accumulate only across papers, as in the corpus.
    """
    counts = [c for c in reference_counts if c > 0]
    if not counts:
        return 0.0, 0, 0
    if not np.isfinite(pool_size):
        total = int(sum(counts))
        return 0.0, total, total

    pool = max(int(round(pool_size)), max(counts))
    tally: Counter[int] = Counter()
    for n_refs in counts:
        tally.update(rng.choice(pool, size=n_refs, replace=False).tolist())
    multiplicities = np.array(list(tally.values()), dtype=np.float64)
    return gini(multiplicities), int(multiplicities.sum()), int(multiplicities.size)


@dataclass(frozen=True)
class YearNull:
    """Observed year beside its matched null."""

    year: int
    n_papers: int
    n_ref_edges: int
    n_distinct_targets: int
    observed_gini: float
    pool_size: float
    null_mean: float
    null_band: tuple[float, float]

    @property
    def excess(self) -> float:
        return self.observed_gini - self.null_mean


@dataclass
class RefGiniNullStudy:
    """A field's observed `ref_gini` series against its matched null."""

    field: str
    years: list[YearNull] = dataclass_field(default_factory=list)
    replay_max_error: float = float("nan")
    n_replicates: int = 0
    null_slopes: list[float] = dataclass_field(default_factory=list)
    """One slope per replicate, each fitted to a complete synthetic series."""

    def observed(self) -> FloatArray:
        return np.array([y.observed_gini for y in self.years], dtype=np.float64)

    def null(self) -> FloatArray:
        return np.array([y.null_mean for y in self.years], dtype=np.float64)

    def year_array(self) -> FloatArray:
        return np.array([y.year for y in self.years], dtype=np.float64)

    def observed_slope(self) -> float:
        return slope(self.year_array(), self.observed())

    def excess_slope(self) -> float:
        """Trend in what the corpus does *above* the null — the concentration signal proper."""
        return slope(self.year_array(), self.observed() - self.null())

    def slope_p_value(self) -> float:
        """Two-sided empirical tail of the observed slope in the null's slope distribution."""
        if not self.null_slopes:
            return float("nan")
        draws = np.asarray(self.null_slopes, dtype=np.float64)
        upper = float((draws >= self.observed_slope()).mean())
        return 2.0 * min(upper, 1.0 - upper)

    def null_slope_band(self) -> tuple[float, float]:
        if not self.null_slopes:
            return (float("nan"), float("nan"))
        draws = np.asarray(self.null_slopes, dtype=np.float64)
        return (float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5)))


def slope(x: Sequence[float] | FloatArray, y: Sequence[float] | FloatArray) -> float:
    """Least-squares slope per year — the estimand the headline reports."""
    return float(np.polyfit(np.asarray(x, dtype=np.float64), np.asarray(y, dtype=np.float64), 1)[0])


def subsampled_reference_lists(
    metadata: Any, ref_map: dict[str, str], *, n_cap: int = N_CAP, seed: int = SERIES_SEED
) -> dict[str, list[tuple[int, list[list[str]]]]]:
    """Reproduce the generating script's per-(field, year) subsample.

    The script draws from one `default_rng(seed)` across both fields in order, touching it only for
    the year cap, so consuming the stream in the same order is what makes the replay exact.
    """
    rng = np.random.default_rng(seed)
    years_col = metadata["year"].to_numpy()
    field_col = metadata["field"].to_numpy()
    ids_col = metadata["paper_id"].to_numpy()

    result: dict[str, list[tuple[int, list[list[str]]]]] = {}
    for field_name in FIELDS:
        field_mask = field_col == field_name
        field_years = years_col[field_mask]
        field_ids = ids_col[field_mask]
        per_year: list[tuple[int, list[list[str]]]] = []
        for year in YEARS:
            year_mask = field_years == year
            n = int(year_mask.sum())
            if n == 0:
                continue
            indices = np.nonzero(year_mask)[0]
            if n > n_cap:
                indices = rng.choice(indices, size=n_cap, replace=False)
            refs = [
                list(json.loads(str(ref_map.get(field_ids[i], "[]")))) for i in indices
            ]
            per_year.append((int(year), refs))
        result[field_name] = per_year
    return result


def replay_reference_canonicity(
    per_year: Sequence[tuple[int, list[list[str]]]],
) -> list[dict[str, Any]]:
    """Recompute the committed `reference_canonicity` rows from the subsampled lists.

    Mirrors `canonical_metrics.reference_canonicity` for the fields the null needs, so a match
    against the committed artifact confirms the reconstruction end to end.
    """
    rows: list[dict[str, Any]] = []
    for year, reference_lists in per_year:
        counter: Counter[str] = Counter()
        for refs in reference_lists:
            counter.update(str(w) for w in refs)
        if not counter:
            continue
        counts = np.array(list(counter.values()), dtype=np.float64)
        rows.append(
            {
                "year": year,
                "n_papers": len(reference_lists),
                "n_ref_edges": int(counts.sum()),
                "n_distinct_targets": int(counts.size),
                "ref_gini": gini(counts),
            }
        )
    return rows


def run_field_study(
    per_year: Sequence[tuple[int, list[list[str]]]],
    committed: Sequence[dict[str, Any]],
    *,
    field_name: str,
    n_replicates: int = 200,
    seed: int = 20260722,
) -> RefGiniNullStudy:
    """Replay one field, then run the matched null for each of its years."""
    replayed = replay_reference_canonicity(per_year)
    committed_by_year = {int(r["year"]): r for r in committed}

    errors = [
        abs(row["ref_gini"] - committed_by_year[row["year"]]["ref_gini"])
        for row in replayed
        if row["year"] in committed_by_year
    ]

    study = RefGiniNullStudy(
        field=field_name,
        replay_max_error=max(errors) if errors else float("nan"),
        n_replicates=n_replicates,
    )

    rng = np.random.default_rng(seed)
    counts_by_year = {year: [len(refs) for refs in lists] for year, lists in per_year}
    per_year_draws: list[FloatArray] = []
    for row in replayed:
        pool = calibrate_pool_size(row["n_ref_edges"], row["n_distinct_targets"])
        draws = np.array(
            [
                simulate_year_gini(rng, counts_by_year[row["year"]], pool)[0]
                for _ in range(n_replicates)
            ],
            dtype=np.float64,
        )
        per_year_draws.append(draws)
        study.years.append(
            YearNull(
                year=row["year"],
                n_papers=row["n_papers"],
                n_ref_edges=row["n_ref_edges"],
                n_distinct_targets=row["n_distinct_targets"],
                observed_gini=row["ref_gini"],
                pool_size=pool,
                null_mean=float(draws.mean()),
                null_band=(
                    float(np.percentile(draws, 2.5)),
                    float(np.percentile(draws, 97.5)),
                ),
            )
        )

    # Each replicate index yields one complete synthetic series, so the observed slope can be placed
    # in a distribution of slopes rather than judged against per-year bands one at a time.
    if per_year_draws:
        matrix = np.vstack(per_year_draws)  # (n_years, n_replicates)
        years = study.year_array()
        study.null_slopes = [slope(years, matrix[:, r]) for r in range(matrix.shape[1])]
    return study


def load_series(path: Path) -> dict[str, list[dict[str, Any]]]:
    """The committed `reference_canonicity` rows per field."""
    payload = json.loads(path.read_text())
    return {
        name: value["canonical"]["reference_canonicity"]
        for name, value in payload["fields"].items()
    }
