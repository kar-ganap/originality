"""Tests for the concentration measures — canon-share (out-edge) and cohort in-degree (in-edge).

Both are built to `docs/concentration-measures.md`; the characterization tests here are the ones
`ref_gini` never had, encoding each requirement the old metric failed.
"""

from __future__ import annotations

import numpy as np
import pytest

from whitespace2.canon_share import (
    build_canon_series,
    parse_work_id,
    top_k_ids,
)
from whitespace2.canon_share import (
    entropy_deficit as canon_entropy_deficit,
)
from whitespace2.cohort_concentration import (
    cohort_concentration,
    entropy_deficit,
    top_decile_share,
    volume_controlled_gini,
)

# --- canon_share (out-edge) ------------------------------------------------------------------


def test_parse_work_id_strips_the_openalex_prefix() -> None:
    assert parse_work_id("https://openalex.org/W4406718614") == 4406718614
    assert parse_work_id("W123") == 123


def test_top_k_ids_is_deterministic_under_ties() -> None:
    from collections import Counter

    counter = Counter({1: 5, 2: 5, 3: 5, 4: 1})
    # three-way tie at 5; the id tiebreak keeps the smallest ids, deterministically.
    assert top_k_ids(counter, 2) == {1, 2}


def test_canon_share_does_not_move_when_the_corpus_merely_grows() -> None:
    """R2, the defect that killed ref_gini: a fixed canon share must not drift with edge count.

    Every year cites the same fixed set of works in the same proportion; later years simply have
    more papers. canon_share must stay flat where ref_gini rose.
    """
    canon_targets = list(range(1, 51))
    other = 10_000
    per_year = []
    for i, year in enumerate(range(1990, 2010)):
        n_papers = 100 * (i + 1)  # corpus grows every year
        lists = []
        for p in range(n_papers):
            # half the references hit the fixed canon, half hit unique fresh works — a constant mix
            fresh = [other + year * 1000 + p * 10 + j for j in range(5)]
            lists.append(canon_targets[:5] + fresh)
        per_year.append((year, lists))

    study = build_canon_series(per_year, k=50, field_name="synthetic", min_edges=50)
    shares = study.share_array()
    assert shares.size > 5
    # flat: max deviation from the mean share is tiny despite the corpus growing 20x
    assert float(np.ptp(shares)) < 0.05


def test_canon_entropy_deficit_is_zero_for_even_and_positive_for_peaked() -> None:
    assert canon_entropy_deficit([5, 5, 5, 5], k=4) == pytest.approx(0.0, abs=1e-9)
    assert canon_entropy_deficit([100, 1, 1, 1], k=4) > 0.4


# --- cohort in-degree (in-edge) --------------------------------------------------------------


def test_top_decile_share_even_vs_concentrated() -> None:
    even = np.ones(100, dtype=np.int64)
    assert top_decile_share(even) == pytest.approx(0.10, abs=1e-9)
    concentrated = np.array([1000] * 10 + [0] * 90, dtype=np.int64)
    assert top_decile_share(concentrated) == pytest.approx(1.0)


def test_cohort_entropy_deficit_scale_and_spread() -> None:
    assert entropy_deficit(np.ones(50, dtype=np.int64)) == pytest.approx(0.0, abs=1e-9)
    peaked = np.array([500] + [1] * 49, dtype=np.int64)
    assert entropy_deficit(peaked) > 0.5


def test_uncited_papers_count_toward_concentration() -> None:
    """A cohort where citations pile onto a few papers is more concentrated than an even one.

    The never-cited papers belong in the cohort; dropping them would understate concentration.
    """
    from whitespace2.canonical_metrics import gini

    even = np.array([2] * 50, dtype=np.int64)
    piled = np.array([100] + [0] * 49, dtype=np.int64)
    assert gini(piled.astype(float)) > gini(even.astype(float))


def test_cohort_concentration_excludes_censored_years() -> None:
    """R4: a cohort younger than the window would be censored, so it must not appear."""
    years = np.array([2000] * 300 + [2023] * 300, dtype=np.int64)
    indeg = np.concatenate([np.arange(300), np.arange(300)]).astype(np.int64)
    fields = np.array(["cs"] * 600, dtype=object)
    rows = cohort_concentration(
        years, indeg, fields, field_name="cs", last_complete_year=2024, window=5, min_papers=200
    )
    present = {r.year for r in rows}
    assert 2000 in present
    assert 2023 not in present  # 2023 + 5 = 2028 > 2024, censored


def test_matched_null_is_below_a_real_concentration_and_tracks_volume() -> None:
    """The null keeps cohort size and citation volume, removes concentration.

    A concentrated cohort must sit above its null; a random-volume cohort must sit near it.
    """
    years = np.array([2000] * 400, dtype=np.int64)
    fields = np.array(["cs"] * 400, dtype=object)
    concentrated = np.array([200] * 20 + [0] * 380, dtype=np.int64)
    rows = cohort_concentration(
        years, concentrated, fields, field_name="cs", last_complete_year=2024, window=5,
        min_papers=200, n_replicates=100,
    )
    assert rows[0].gini > rows[0].null_gini + 0.2  # real concentration is well above the null

    # A cohort whose citations are themselves thrown at random must sit *near* its null — the null
    # is random allocation, not perfect evenness, so it carries the ~0.25 Gini that random volume
    # forces. This is the whole point: the null absorbs volume-driven inequality so the excess is
    # concentration proper.
    random_even = np.random.default_rng(0).multinomial(2000, np.full(400, 1 / 400))
    rows_even = cohort_concentration(
        years, random_even.astype(np.int64), fields, field_name="cs",
        last_complete_year=2024, window=5, min_papers=200, n_replicates=100,
    )
    assert abs(rows_even[0].excess_gini) < 0.05  # random volume ≈ its matched null


def test_volume_control_removes_the_density_confound() -> None:
    """Two cohorts with the SAME concentration shape but different citation density.

    Raw Gini would call the sparse one more concentrated purely because it has more zeros. Thinning
    both to a common rate must bring their Ginis together — isolating shape from density.
    """
    rng = np.random.default_rng(0)
    shape = np.array([50, 30, 20, 10] + [1] * 96, dtype=np.float64)
    shape = shape / shape.sum()
    dense = rng.multinomial(4000, shape)  # 40 citations/paper
    sparse = rng.multinomial(200, shape)  # 2 citations/paper, same shape

    from whitespace2.canonical_metrics import gini

    raw_gap = abs(gini(dense.astype(float)) - gini(sparse.astype(float)))
    controlled_gap = abs(
        volume_controlled_gini(rng, dense, rate=2.0, n_replicates=200)
        - volume_controlled_gini(rng, sparse, rate=2.0, n_replicates=200)
    )
    # Equalizing density more than halves the spurious gap. It does not fully close it: thinning to
    # a low rate leaves shape-dependent sampling noise, which is why the control reduces rather than
    # erases a density-driven trend and must be read alongside the raw series, not instead of it.
    assert controlled_gap < 0.5 * raw_gap
