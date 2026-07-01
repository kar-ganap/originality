"""Unit tests for the Stage-2 semantic + canonical diversity metrics.

These are lifted into `src/` from Phase 0.1's
`experiments/phase-0.1/check5bd_convergence_stratification.py` (semantic)
and are new (canonical). Per `docs/desiderata.md` §8: semantic diversity
uses ≥2 metrics (effective dimensionality + mean pairwise cosine distance,
plus cluster entropy); canonical concentration uses ≥2 (citation Gini +
top-k share).
"""

from __future__ import annotations

import numpy as np

from whitespace2.canonical_metrics import gini, top_k_share
from whitespace2.semantic_metrics import (
    cluster_entropy,
    effective_dimensionality,
    mean_pairwise_cosine_distance,
)

# ---------- effective_dimensionality ----------


def test_effective_dimensionality_two_equal_axes() -> None:
    """4 points at (±1,0),(0,±1): covariance has two equal eigenvalues →
    participation ratio = 2.0 exactly."""
    v = np.array([[1.0, 0.0], [-1.0, 0.0], [0.0, 1.0], [0.0, -1.0]])
    assert abs(effective_dimensionality(v) - 2.0) < 1e-9


def test_effective_dimensionality_degenerate() -> None:
    """Identical vectors → zero variance → 0.0; <2 rows → 0.0."""
    assert effective_dimensionality(np.ones((5, 3))) == 0.0
    assert effective_dimensionality(np.ones((1, 3))) == 0.0
    # Rank-1 spread (all along one axis) → participation ratio 1.0
    v = np.array([[1.0, 0.0], [2.0, 0.0], [3.0, 0.0], [4.0, 0.0]])
    assert abs(effective_dimensionality(v) - 1.0) < 1e-9


# ---------- mean_pairwise_cosine_distance ----------


def test_mean_pairwise_cosine_distance_known() -> None:
    """Orthogonal → 1.0; identical → 0.0; antipodal → 2.0."""
    assert abs(mean_pairwise_cosine_distance(
        np.array([[1.0, 0.0], [0.0, 1.0]])) - 1.0) < 1e-9
    assert abs(mean_pairwise_cosine_distance(
        np.array([[1.0, 0.0], [1.0, 0.0]])) - 0.0) < 1e-9
    assert abs(mean_pairwise_cosine_distance(
        np.array([[1.0, 0.0], [-1.0, 0.0]])) - 2.0) < 1e-9


def test_mean_pairwise_cosine_distance_normalizes() -> None:
    """Un-normalized inputs are L2-normalized first (default)."""
    # (3,0) and (0,5) → normalize → (1,0),(0,1) → orthogonal → 1.0
    assert abs(mean_pairwise_cosine_distance(
        np.array([[3.0, 0.0], [0.0, 5.0]])) - 1.0) < 1e-9


def test_mean_pairwise_cosine_distance_subsample_deterministic() -> None:
    """max_sample subsamples deterministically (same seed → same value),
    and stays a sane cosine distance in [0, 2]."""
    rng = np.random.default_rng(0)
    v = rng.normal(size=(500, 16))
    a = mean_pairwise_cosine_distance(v, max_sample=100, seed=7)
    b = mean_pairwise_cosine_distance(v, max_sample=100, seed=7)
    assert a == b
    assert 0.0 <= a <= 2.0


# ---------- cluster_entropy ----------


def test_cluster_entropy_known() -> None:
    """Balanced 2-cluster: Shannon(ln2) + Miller-Madow (k-1)/(2n)."""
    # assignments [0,0,1,1], k=2, n=4 → ln2 + 1/8
    val = cluster_entropy(np.array([0, 0, 1, 1]), 2)
    assert abs(val - (0.6931 + 0.125)) < 1e-3
    # Single occupied cluster → 0 entropy, MM term 0
    assert cluster_entropy(np.array([0, 0, 0]), 1) == 0.0


# ---------- gini ----------


def test_gini_known() -> None:
    """gini([1,2,3,4]) = 0.25; equal values → 0."""
    assert abs(gini(np.array([1.0, 2.0, 3.0, 4.0])) - 0.25) < 1e-9
    assert gini(np.array([5.0, 5.0, 5.0])) == 0.0
    # Empty / all-zero → 0 (degenerate, no concentration)
    assert gini(np.array([0.0, 0.0, 0.0])) == 0.0


def test_gini_concentration_rises() -> None:
    """More concentrated citations → higher Gini (the canonical negative
    control's expected direction over time)."""
    spread = gini(np.array([10.0, 11.0, 9.0, 10.0]))
    concentrated = gini(np.array([0.0, 0.0, 1.0, 100.0]))
    assert concentrated > spread


# ---------- top_k_share ----------


def test_top_k_share_known() -> None:
    """Share of total held by the top k-fraction of items."""
    v = np.array([1.0, 1.0, 1.0, 7.0])  # total 10
    assert abs(top_k_share(v, 0.25) - 0.7) < 1e-9   # top 1 of 4 = 7/10
    assert abs(top_k_share(v, 0.5) - 0.8) < 1e-9    # top 2 = (7+1)/10
    assert top_k_share(np.array([0.0, 0.0]), 0.5) == 0.0  # degenerate
