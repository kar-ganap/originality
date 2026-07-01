"""Tests for the Phase 2.3 subfield mechanism test (`subfield_divergence`).

Two testable cores (the streaming map builder is exercised on a synthetic
corpus; the regression is exercised against independent hand-computation):

  - ``extract_primary_subconcept`` / ``build_paper_subfield_map`` — assign each
    paper to its highest-scoring OpenAlex level-1 sub-concept (the interpretable
    subfield), mirroring ``extract_primary_field``.
  - ``subfield_regression`` — the pre-registered estimator: OLS of
    divergence-magnitude on canon-concentration controlling for log-size, with
    a permutation null on γ₁, a collinearity VIF, and a standardized γ₁.

The regression tests use EXACT planted designs (no noise) so the recovered
coefficients are deterministic:
  - a planted positive γ₁ is recovered exactly and is permutation-significant;
  - when divergence lies exactly in span{1, log_size}, γ₁ is exactly 0 for the
    observed fit AND every permutation → perm p == 1.0 (a clean null).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from whitespace2.subfield_divergence import (
    build_paper_subfield_map,
    extract_primary_subconcept,
    subfield_regression,
)

_CS_ID = "https://openalex.org/C41008148"        # level 0 (field root)
_PHYS_ID = "https://openalex.org/C121332964"      # level 0 (field root)
_ML = "https://openalex.org/C119857082"           # a level-1 CS sub-concept
_AI = "https://openalex.org/C154945302"           # another level-1 CS sub-concept
_QM = "https://openalex.org/C62520636"            # a level-1 physics sub-concept


def _concepts(*triples: tuple[str, int, float]) -> str:
    """Build a concepts_json string from (concept_id, level, score) triples."""
    return json.dumps(
        [{"id": cid, "level": lvl, "score": score} for cid, lvl, score in triples],
    )


# --------------------------------------------------------------------------
# extract_primary_subconcept
# --------------------------------------------------------------------------

def test_extract_primary_subconcept_picks_highest_level1() -> None:
    """The highest-scoring level-1 concept wins; level-0 roots and level-2+
    concepts are ignored."""
    # ML (0.6) beats AI (0.4); the level-0 CS root (0.9) is ignored.
    assert extract_primary_subconcept(
        _concepts((_CS_ID, 0, 0.9), (_ML, 1, 0.6), (_AI, 1, 0.4)),
    ) == _ML
    # A high-scoring level-2 concept does not qualify — only level 1.
    assert extract_primary_subconcept(
        _concepts((_ML, 1, 0.3), ("https://openalex.org/C999", 2, 0.95)),
    ) == _ML


def test_extract_primary_subconcept_ties_broken_by_id() -> None:
    """Equal top scores → the lexicographically smallest id (determinism)."""
    a, b = "https://openalex.org/C100", "https://openalex.org/C200"
    assert extract_primary_subconcept(_concepts((b, 1, 0.5), (a, 1, 0.5))) == a


def test_extract_primary_subconcept_exclude_ids() -> None:
    """An excluded level-1 id is skipped in favour of the next-best."""
    assert extract_primary_subconcept(
        _concepts((_ML, 1, 0.6), (_AI, 1, 0.4)),
        exclude_ids=frozenset({_ML}),
    ) == _AI


def test_extract_primary_subconcept_none_and_malformed() -> None:
    """No level-1 concept / malformed input → None."""
    assert extract_primary_subconcept(_concepts((_CS_ID, 0, 0.9))) is None
    assert extract_primary_subconcept("[]") is None
    assert extract_primary_subconcept("{not json") is None
    assert extract_primary_subconcept(None) is None  # type: ignore[arg-type]
    assert extract_primary_subconcept("") is None
    # a level-1 concept below min_score is rejected
    assert extract_primary_subconcept(
        _concepts((_ML, 1, 0.2)), min_score=0.3,
    ) is None


# --------------------------------------------------------------------------
# build_paper_subfield_map
# --------------------------------------------------------------------------

def test_build_paper_subfield_map(tmp_path: Path) -> None:
    """Stream a synthetic corpus → paper_id → 'field:concept' subfield key.

    Papers with no level-1 concept, or outside the field filter, are dropped
    (inner-join semantics, mirroring build_paper_field_map)."""
    corpus = pa.table({
        "id": [f"https://openalex.org/W{i}" for i in range(4)],
        "concepts_json": [
            _concepts((_CS_ID, 0, 0.6), (_ML, 1, 0.5)),      # cs → cs:ML
            _concepts((_PHYS_ID, 0, 0.7), (_QM, 1, 0.6)),    # physics → dropped (cs-only)
            _concepts((_CS_ID, 0, 0.6)),                     # cs but no level-1 → dropped
            _concepts((_CS_ID, 0, 0.5), (_AI, 1, 0.55)),     # cs → cs:AI
        ],
    })
    src = tmp_path / "corpus.parquet"
    pq.write_table(corpus, src)
    out = tmp_path / "subfield.parquet"

    stats = build_paper_subfield_map(src, out, field_filter="cs")
    tbl = pq.read_table(out).to_pandas()

    got = dict(zip(tbl["paper_id"], tbl["primary_field"], strict=True))
    assert got == {
        "https://openalex.org/W0": f"cs:{_ML}",
        "https://openalex.org/W3": f"cs:{_AI}",
    }
    assert stats["n_assigned"] == 2
    assert stats["n_papers"] == 4


def test_build_paper_subfield_map_both_fields(tmp_path: Path) -> None:
    """With no field filter, both fields' papers are kept, each keyed by its
    own field prefix."""
    corpus = pa.table({
        "id": ["https://openalex.org/W0", "https://openalex.org/W1"],
        "concepts_json": [
            _concepts((_CS_ID, 0, 0.6), (_ML, 1, 0.5)),
            _concepts((_PHYS_ID, 0, 0.7), (_QM, 1, 0.6)),
        ],
    })
    src = tmp_path / "corpus.parquet"
    pq.write_table(corpus, src)
    out = tmp_path / "subfield.parquet"
    build_paper_subfield_map(src, out, field_filter=None)
    tbl = pq.read_table(out).to_pandas()
    got = dict(zip(tbl["paper_id"], tbl["primary_field"], strict=True))
    assert got == {
        "https://openalex.org/W0": f"cs:{_ML}",
        "https://openalex.org/W1": f"physics:{_QM}",
    }


# --------------------------------------------------------------------------
# subfield_regression
# --------------------------------------------------------------------------

def test_subfield_regression_recovers_planted_gamma1() -> None:
    """An exact planted positive γ₁ is recovered and is permutation-significant."""
    rng = np.random.default_rng(0)
    n = 14
    canon = rng.uniform(0.3, 0.9, n)
    log_size = rng.uniform(3.0, 5.0, n)
    # Exact linear design: divergence = 0.5 + 1.5·canon + 0.3·log_size
    divergence = 0.5 + 1.5 * canon + 0.3 * log_size

    res = subfield_regression(canon, divergence, log_size, n_perm=2000, seed=1)
    assert abs(res["gamma1"] - 1.5) < 1e-9
    assert abs(res["beta_logsize"] - 0.3) < 1e-9
    assert res["gamma1_perm_pvalue"] < 0.05
    assert res["significant"] is True
    # standardized γ₁ = gamma1 · sd(canon)/sd(divergence)
    expect_std = 1.5 * float(np.std(canon, ddof=1)) / float(
        np.std(divergence, ddof=1))
    assert abs(res["gamma1_standardized"] - expect_std) < 1e-9


def test_subfield_regression_null_gamma1_is_exactly_zero() -> None:
    """When divergence lies exactly in span{1, log_size}, the partial γ₁ is 0
    for the observed fit AND every permutation → perm p == 1.0 (clean null).

    This holds regardless of canon's correlation with log_size, because
    divergence adds nothing beyond {1, log_size}: the unique LS solution puts
    canon's coefficient at exactly 0."""
    rng = np.random.default_rng(2)
    n = 12
    canon = rng.uniform(0.0, 1.0, n)          # arbitrary; correlated or not
    log_size = rng.uniform(2.0, 6.0, n)
    divergence = 2.0 + 0.4 * log_size          # no canon dependence, exact

    res = subfield_regression(canon, divergence, log_size, n_perm=1000, seed=3)
    assert abs(res["gamma1"]) < 1e-9
    assert res["gamma1_perm_pvalue"] == 1.0
    assert res["significant"] is False
    assert abs(res["gamma1_standardized"]) < 1e-9


def test_subfield_regression_vif_flags_collinearity() -> None:
    """VIF(canon, log_size) is large when canon ≈ log_size, ≈1 when orthogonal."""
    n = 20
    log_size = np.linspace(3.0, 5.0, n)
    # near-collinear canon → high VIF
    collinear = log_size * 0.1 + 1e-6 * np.arange(n)
    div = np.zeros(n)
    res_hi = subfield_regression(collinear, div, log_size, n_perm=200, seed=0)
    assert res_hi["vif_canon"] > 10.0

    # orthogonal canon (centered, dot-zero with centered log_size) → VIF ≈ 1
    # symmetric ± pattern is orthogonal to the antisymmetric centered ramp
    ortho = np.array([1.0, -1.0] * (n // 2))
    res_lo = subfield_regression(ortho, div, log_size, n_perm=200, seed=0)
    assert abs(res_lo["vif_canon"] - 1.0) < 0.05


def test_subfield_regression_field_fixed_effect() -> None:
    """A field fixed effect absorbs a field-level offset so γ₁ is recovered
    even when the two fields sit at different divergence levels."""
    rng = np.random.default_rng(4)
    n = 16
    canon = rng.uniform(0.3, 0.9, n)
    log_size = rng.uniform(3.0, 5.0, n)
    field = np.array(["cs"] * (n // 2) + ["physics"] * (n // 2))
    offset = np.where(field == "physics", 2.0, 0.0)   # field-level shift
    divergence = 0.5 + 1.2 * canon + 0.3 * log_size + offset

    res = subfield_regression(
        canon, divergence, log_size, field=field, n_perm=2000, seed=5)
    assert abs(res["gamma1"] - 1.2) < 1e-9
    assert res["n_subfields"] == n


def test_subfield_regression_degenerate_input() -> None:
    """Too few subfields → a non-significant, None-γ₁ verdict, not a crash."""
    res = subfield_regression([0.5, 0.6], [1.0, 2.0], [3.0, 4.0], n_perm=100)
    assert res["gamma1"] is None
    assert res["significant"] is False
