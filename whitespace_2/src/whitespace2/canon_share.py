"""Concentration measures built to the spec in `docs/concentration-measures.md`.

`ref_gini` failed because it moved when the corpus grew. The measure here removes that by
construction rather than by correction: the canon is a **fixed-size** set of `K` works, defined only
from the past, and the statistic is a share of the year's own edges.

    canon_share_K(t) = (year-t reference edges landing in C_t) / (all year-t reference edges)

where `C_t` is the top-`K` targets by citations received from papers published strictly before `t`.
Because `K` never grows and the denominator is the year's own edge count, a longer reference list
cannot inflate the number — which is exactly what `ref_gini` could not survive.

Definitions are frozen in the spec before measuring; see that document for the requirement each
design choice answers.
"""

from __future__ import annotations

import heapq
import json
from collections import Counter
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from typing import Any

import numpy as np
import numpy.typing as npt

FloatArray = npt.NDArray[np.float64]

CANON_SIZES = (100, 1_000, 10_000)
"""Reported at every `K`; a canon claim must not hinge on the cutoff."""


def parse_work_id(work_id: str) -> int:
    """`https://openalex.org/W4406718614` -> `4406718614`.

    Interning 6.5M OpenAlex URLs as Python strings costs over a gigabyte; the numeric suffix is a
    lossless key and keeps the cumulative counter in integer space.
    """
    tail = work_id.rsplit("/", 1)[-1]
    return int(tail[1:]) if tail[:1] in {"W", "w"} else int(tail)


def iter_reference_ids(payload: Any) -> Iterator[int]:
    """Reference ids from one stored `referenced_works_json` cell."""
    if not payload:
        return
    for work_id in json.loads(str(payload)):
        try:
            yield parse_work_id(str(work_id))
        except ValueError:  # a malformed id is dropped, never silently counted as a target
            continue


def top_k_ids(counter: Counter[int], k: int) -> set[int]:
    """The `k` most-cited ids, ties broken by id so the canon is deterministic."""
    if not counter:
        return set()
    return {
        work_id
        for work_id, _ in heapq.nlargest(k, counter.items(), key=lambda kv: (kv[1], -kv[0]))
    }


def entropy_deficit(counts: Sequence[int] | FloatArray, k: int) -> float:
    """`1 - H/log(k)` over canon-directed edges: how unevenly attention sits *within* the canon.

    Zero when the canon's `k` slots share attention evenly, approaching one as it collapses onto a
    few. Normalizing by `log(k)` rather than by the number of *occupied* slots is deliberate: an
    occupied-slot denominator would shrink as concentration rose and partly cancel the signal.
    """
    values = np.asarray(counts, dtype=np.float64)
    values = values[values > 0]
    if values.size == 0 or k <= 1:
        return 0.0
    p = values / values.sum()
    return float(1.0 - (-(p * np.log(p)).sum()) / np.log(k))


@dataclass(frozen=True)
class YearCanon:
    """One year's canon-share measurement beside its matched null."""

    year: int
    k: int
    n_papers: int
    n_edges: int
    n_prior_targets: int
    canon_share: float
    entropy_deficit: float
    null_share: float

    @property
    def excess(self) -> float:
        return self.canon_share - self.null_share


@dataclass
class CanonStudy:
    """A field's canon-share series at one `K`."""

    field: str
    k: int
    years: list[YearCanon] = dataclass_field(default_factory=list)

    def year_array(self) -> FloatArray:
        return np.array([y.year for y in self.years], dtype=np.float64)

    def share_array(self) -> FloatArray:
        return np.array([y.canon_share for y in self.years], dtype=np.float64)

    def null_array(self) -> FloatArray:
        return np.array([y.null_share for y in self.years], dtype=np.float64)

    def deficit_array(self) -> FloatArray:
        return np.array([y.entropy_deficit for y in self.years], dtype=np.float64)


def slope(x: Sequence[float] | FloatArray, y: Sequence[float] | FloatArray) -> float:
    return float(np.polyfit(np.asarray(x, dtype=np.float64), np.asarray(y, dtype=np.float64), 1)[0])


def build_canon_series(
    per_year: Iterable[tuple[int, list[list[int]]]],
    *,
    k: int,
    field_name: str,
    min_edges: int = 200,
    canon_per_year: Sequence[tuple[int, list[list[int]]]] | None = None,
) -> CanonStudy:
    """Walk years in ascending order, measuring each against the canon its predecessors built.

    The cumulative counter is updated *after* each year is measured, so no year's canon is ever
    informed by its own edges.

    `canon_per_year` lets the canon accumulate from a different (fuller) history than the cohort
    being measured. The subsample-invariance check needs exactly that: thinning the measured cohort
    *and* the canon at once would vary two things and answer neither.
    """
    study = CanonStudy(field=field_name, k=k)
    cumulative: Counter[int] = Counter()
    canon_edges = (
        {year: [w for refs in lists for w in refs] for year, lists in canon_per_year}
        if canon_per_year is not None
        else None
    )

    for year, reference_lists in per_year:
        edges = [work_id for refs in reference_lists for work_id in refs]
        if len(edges) >= min_edges and len(cumulative) >= k:
            canon = top_k_ids(cumulative, k)
            hits = Counter(w for w in edges if w in canon)
            n_hits = int(sum(hits.values()))
            study.years.append(
                YearCanon(
                    year=year,
                    k=k,
                    n_papers=len(reference_lists),
                    n_edges=len(edges),
                    n_prior_targets=len(cumulative),
                    canon_share=n_hits / len(edges),
                    entropy_deficit=entropy_deficit(list(hits.values()), k),
                    # No-preference null: every previously-seen target equally likely, so the canon
                    # is reached at exactly its share of the prior universe.
                    null_share=k / len(cumulative),
                )
            )
        cumulative.update(edges if canon_edges is None else canon_edges.get(year, []))

    return study


def subsample_invariance(
    per_year: Sequence[tuple[int, list[list[int]]]],
    *,
    k: int,
    field_name: str,
    n_papers: int = 500,
    seed: int = 20260722,
) -> tuple[CanonStudy, CanonStudy]:
    """Battery item 1 (R3): the same series on all papers and on a fixed-size cohort per year.

    The canon itself is always built from the full history — only the *measured* cohort is thinned,
    which is what isolates cohort size from canon formation.
    """
    rng = np.random.default_rng(seed)
    full = build_canon_series(per_year, k=k, field_name=field_name)

    thinned: list[tuple[int, list[list[int]]]] = []
    for year, reference_lists in per_year:
        if len(reference_lists) > n_papers:
            picks = rng.choice(len(reference_lists), size=n_papers, replace=False)
            thinned.append((year, [reference_lists[i] for i in picks]))
        else:
            thinned.append((year, reference_lists))
    thinned_study = build_canon_series(
        thinned,
        k=k,
        field_name=f"{field_name}-sub{n_papers}",
        canon_per_year=list(per_year),  # canon from the full history; only the cohort is thinned
    )
    return full, thinned_study
