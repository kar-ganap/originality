"""Semantic-diversity metrics for the Stage-2 divergence test.

Lifted verbatim (behaviour-preserving) from Phase 0.1's
``experiments/phase-0.1/check5bd_convergence_stratification.py`` so the
Stage-1 → Stage-2 substrate stays numerically consistent with the Phase
0.1 convergence work. Per ``docs/desiderata.md`` §8, semantic diversity
uses ≥2 metrics; the plan-at-a-glance §5 stack is:

  - ``effective_dimensionality`` — PCA participation ratio (primary B)
  - ``mean_pairwise_cosine_distance`` — bootstrap-subsampled (secondary)
  - ``cluster_entropy`` — Shannon over K-means assignments, Miller-Madow
    corrected (primary A; §11 temporally-stratified fit is the caller's
    responsibility — this function scores a given assignment vector).

All operate on ``(N, D)`` embedding matrices (or an assignment vector).
"""

from __future__ import annotations

from typing import Any

import numpy as np


def _shannon_entropy_mm(counts: Any, n_total: float) -> float:
    """Miller-Madow-corrected Shannon entropy (nats) from raw counts.

    Matches Phase 0.1's ``_shannon_entropy_with_mm``: ``-Σ p ln p`` plus
    the bias term ``(k-1)/(2n)`` for ``k`` non-empty categories. Returns
    0.0 on non-positive ``n_total``.
    """
    counts_arr = np.asarray(counts, dtype=np.float64)
    total = float(n_total)
    if total <= 0.0:
        return 0.0
    p = counts_arr / total
    p = p[p > 0]
    h = -float((p * np.log(p)).sum())
    k_nonzero = int((counts_arr > 0).sum())
    h += (k_nonzero - 1) / (2.0 * total)
    return h


def effective_dimensionality(vectors: Any) -> float:
    """PCA participation ratio ``(Σλᵢ)² / Σλᵢ²`` of the sample covariance.

    ``λᵢ`` are eigenvalues of the covariance of the (mean-centered)
    ``(N, D)`` matrix, computed via SVD. Measures the effective number of
    dimensions the embeddings occupy — higher = semantically more diverse.

    Returns 0.0 for ``N < 2`` or zero-variance input. Caveat (Phase 0.1):
    when ``N < D`` the covariance rank ≤ ``N-1``, so effective dim ≤
    ``N-1`` by construction — the caller must flag that degenerate regime.
    """
    v = np.asarray(vectors, dtype=np.float64)
    n = v.shape[0]
    if n < 2:
        return 0.0
    centered = v - v.mean(axis=0, keepdims=True)
    s = np.linalg.svd(centered, compute_uv=False)
    eig = (s**2) / (n - 1)
    eig = eig[eig > 0]
    if eig.size == 0:
        return 0.0
    return float(eig.sum() ** 2 / (eig**2).sum())


def mean_pairwise_cosine_distance(
    vectors: Any,
    *,
    normalize: bool = True,
    max_sample: int | None = None,
    seed: int | None = None,
) -> float:
    """Mean cosine distance ``1 - cos`` over all unordered vector pairs.

    ``normalize`` L2-normalizes rows first (default; pass False if the
    input is already unit-norm). The full computation is O(N²); for large
    cells pass ``max_sample`` to score a seeded random subsample of that
    many rows (bootstrap-subsampled, per the plan-at-a-glance §5 stack).

    Returns 0.0 for ``N < 2``. Range ``[0, 2]`` (0 = all identical, 2 =
    antipodal).
    """
    v = np.asarray(vectors, dtype=np.float64)
    n = v.shape[0]
    if n < 2:
        return 0.0
    if max_sample is not None and n > max_sample:
        rng = np.random.default_rng(seed)
        idx = rng.choice(n, size=max_sample, replace=False)
        v = v[idx]
        n = max_sample
    if normalize:
        norms = np.linalg.norm(v, axis=1, keepdims=True)
        norms = np.where(norms > 0, norms, 1.0)
        v = v / norms
    sim = v @ v.T
    iu = np.triu_indices(n, k=1)
    return float((1.0 - sim[iu]).mean())


def cluster_entropy(assignments: Any, n_clusters: int) -> float:
    """Miller-Madow Shannon entropy of a K-means assignment distribution.

    ``assignments`` is an integer vector of cluster ids in ``[0,
    n_clusters)``; higher entropy = papers spread more evenly across
    clusters = semantically more diverse. The temporally-stratified
    cluster fit (§11) is the caller's responsibility — this scores a
    given assignment vector.
    """
    a = np.asarray(assignments)
    counts = np.bincount(a, minlength=n_clusters)
    return _shannon_entropy_mm(counts, int(a.size))
