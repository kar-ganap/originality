"""§11 temporally-stratified cluster fit for the Stage-2 semantic series.

The ``cluster_entropy`` semantic metric (``semantic_metrics.py``) scores a
K-means assignment vector; it is only valid on the §11 **temporally-
stratified** fit — a K-means fit on a decade-balanced sample so early-year
papers aren't projected into modern-dominated clusters (Phase-1.4 pilot
finding #3; Phase-0.1 Check 5d). This module productionizes that fit,
lifted (behaviour-preserving) from
``experiments/phase-0.2/section11_production_validation.py``:

  - ``build_decade_stratified_sample`` — equal papers per decade bin.
  - ``fit_clusters`` — K-means (locked K=50 / n_init=20 / random_state=46)
    on L2-normalized vectors → centroids.
  - ``project_to_clusters`` — hard-assign vectors to nearest centroid by
    **Euclidean** distance, ``argmin‖v−c‖² = argmax(2·v·c − ‖c‖²)``.
    This is the Phase-0.2 Wave-2A bug fix: a hand-rolled ``argmax(v·c)``
    (cosine) projection is NOT consistent with K-means's fitting criterion
    for non-unit-norm centroids (means of unit vectors have norms ~0.92-0.94),
    and reversed the §11 results across all cells. ``project_to_clusters``
    reproduces ``KMeans.predict`` exactly.

Locked cluster-fit parameters (§11 / phase-0.2 retro): K=50 primary,
n_init=20, random_state=46, max_iter=300.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from sklearn.cluster import KMeans

# §11 decade bins (half-open [lo, hi)); matches the Phase-0.2 validation
# script's ``publication_year: f"{lo}-{hi-1}"`` server-side filter.
_DECADE_BINS: tuple[tuple[int, int], ...] = (
    (1970, 1980), (1980, 1990), (1990, 2000),
    (2000, 2010), (2010, 2020), (2020, 2025),
)

# Locked §11 K-means parameters (phase-0.2 retro).
_K_PRIMARY = 50
_N_INIT = 20
_RANDOM_STATE = 46
_MAX_ITER = 300


def _l2_normalize(vectors: Any) -> np.ndarray[Any, Any]:
    """Row-wise L2 normalize (float64; zero rows pass through unchanged)."""
    v = np.asarray(vectors, dtype=np.float64)
    norms = np.linalg.norm(v, axis=1, keepdims=True)
    norms = np.where(norms > 0, norms, 1.0)
    normalized: np.ndarray[Any, Any] = v / norms
    return normalized


def build_decade_stratified_sample(
    years: Any,
    n_per_decade: int,
    *,
    seed: int,
) -> np.ndarray[Any, Any]:
    """Indices of a decade-balanced subsample of ``years`` (the §11 balance).

    ``years`` is an array of publication years (one per paper). Returns the
    integer indices of up to ``n_per_decade`` papers drawn without
    replacement from each of the six decade bins ``[1970,1980) …
    [2020,2025)`` — equal papers per decade so the K-means fit isn't
    dominated by the paper-rich recent decades. A decade with fewer than
    ``n_per_decade`` papers contributes all it has (documented underrun,
    per Check 5d). Years outside ``[1970, 2025)`` fall in no bin and are
    excluded. Deterministic given ``seed``.
    """
    years_arr = np.asarray(years)
    rng = np.random.default_rng(seed)
    picked: list[np.ndarray[Any, Any]] = []
    for lo, hi in _DECADE_BINS:
        in_decade = np.nonzero((years_arr >= lo) & (years_arr < hi))[0]
        if in_decade.size > n_per_decade:
            chosen = rng.choice(in_decade, size=n_per_decade, replace=False)
        else:
            chosen = in_decade
        picked.append(np.sort(chosen))
    if not picked:
        return np.array([], dtype=np.int64)
    result: np.ndarray[Any, Any] = np.concatenate(picked).astype(np.int64)
    return result


def fit_clusters(
    vectors: Any,
    *,
    k: int = _K_PRIMARY,
    n_init: int = _N_INIT,
    random_state: int = _RANDOM_STATE,
    max_iter: int = _MAX_ITER,
    normalize: bool = True,
) -> np.ndarray[Any, Any]:
    """Fit K-means on ``vectors`` (L2-normalized by default); return centroids.

    Returns the ``(k, D)`` centroid matrix. Parameters default to the locked
    §11 values (K=50 / n_init=20 / random_state=46 / max_iter=300). Pass
    ``normalize=False`` if ``vectors`` are already unit-norm. The centroids
    are means of unit vectors — their norms are typically ~0.92-0.94, which
    is exactly why :func:`project_to_clusters` must use the Euclidean (not
    cosine) criterion.
    """
    v = _l2_normalize(vectors) if normalize else np.asarray(
        vectors, dtype=np.float64,
    )
    km = KMeans(
        n_clusters=k, n_init=n_init, random_state=random_state,
        max_iter=max_iter,
    )
    km.fit(v)
    centroids: np.ndarray[Any, Any] = np.asarray(
        km.cluster_centers_, dtype=np.float64,
    )
    return centroids


def project_to_clusters(
    vectors: Any,
    centroids: Any,
    *,
    normalize: bool = True,
) -> np.ndarray[Any, Any]:
    """Hard-assign each vector to its nearest centroid (Euclidean).

    Equivalent to ``KMeans.predict`` on a model with these centroids:
    ``argmin‖v−c‖² = argmax(2·v·c − ‖c‖²)`` since ``‖v‖²`` is constant per
    row. This is the Phase-0.2 Wave-2A fix — ``argmax(v·c)`` (cosine) favours
    high-magnitude centroids and mis-assigns when centroids are non-unit-norm.
    ``vectors`` are L2-normalized first by default (the fit convention);
    pass ``normalize=False`` if already unit-norm. Returns an int64 vector of
    cluster ids in ``[0, len(centroids))``.
    """
    v = _l2_normalize(vectors) if normalize else np.asarray(
        vectors, dtype=np.float64,
    )
    c = np.asarray(centroids, dtype=np.float64)
    centroid_norms_sq = np.sum(c**2, axis=1)
    scores = 2.0 * (v @ c.T) - centroid_norms_sq[None, :]
    assignments: np.ndarray[Any, Any] = np.argmax(scores, axis=1).astype(
        np.int64,
    )
    return assignments
