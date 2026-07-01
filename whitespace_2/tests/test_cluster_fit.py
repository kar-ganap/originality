"""Unit tests for the §11 temporally-stratified cluster fit (Phase 2.1 WS1).

Covers the three lifted primitives (`build_decade_stratified_sample`,
`fit_clusters`, `project_to_clusters`). The load-bearing test is that
`project_to_clusters` reproduces `KMeans.predict` EXACTLY — the Phase-0.2
Wave-2A bug was a hand-rolled `argmax(v·c)` projection that is NOT
consistent with KMeans's `argmin‖v−c‖²` for non-unit-norm centroids; the
fixed `argmax(2·v·c − ‖c‖²)` must match the library predict path.
"""

from __future__ import annotations

import numpy as np
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs

from whitespace2.cluster_fit import (
    build_decade_stratified_sample,
    fit_clusters,
    project_to_clusters,
)

_DECADES = (
    (1970, 1980), (1980, 1990), (1990, 2000),
    (2000, 2010), (2010, 2020), (2020, 2025),
)


# ---------- build_decade_stratified_sample ----------


def test_decade_sample_balanced() -> None:
    """Equal papers/decade when every decade has enough supply."""
    rng = np.random.default_rng(0)
    # 500 papers uniformly across 1970-2024 → every decade well-supplied.
    years = rng.integers(1970, 2025, size=5000)
    idx = build_decade_stratified_sample(years, n_per_decade=100, seed=7)

    assert len(idx) == 600  # 6 decades × 100
    assert idx.dtype.kind in ("i", "u")
    picked = years[idx]
    for lo, hi in _DECADES:
        n_in = int(((picked >= lo) & (picked < hi)).sum())
        assert n_in == 100, f"decade {lo}s got {n_in}, expected 100"


def test_decade_sample_underrun_takes_all() -> None:
    """A decade with fewer than n_per_decade contributes all it has."""
    # 1970s has only 3 papers; other decades plentiful.
    years = np.array(
        [1971, 1975, 1978]  # 1970s: 3
        + [1985] * 50 + [1995] * 50 + [2005] * 50
        + [2015] * 50 + [2022] * 50,
    )
    idx = build_decade_stratified_sample(years, n_per_decade=20, seed=1)
    picked = years[idx]
    n_1970s = int(((picked >= 1970) & (picked < 1980)).sum())
    assert n_1970s == 3  # took all available
    # Every other decade capped at 20.
    for lo, hi in _DECADES[1:]:
        assert int(((picked >= lo) & (picked < hi)).sum()) == 20
    assert len(idx) == 3 + 5 * 20


def test_decade_sample_excludes_out_of_window() -> None:
    """Years outside [1970, 2025) belong to no decade bin and are dropped."""
    years = np.array([1969, 1965, 2025, 2030, 1975, 1975, 2021])
    idx = build_decade_stratified_sample(years, n_per_decade=10, seed=3)
    picked = years[idx]
    assert set(picked.tolist()) == {1975, 2021}  # only in-window years survive


def test_decade_sample_deterministic() -> None:
    rng = np.random.default_rng(0)
    years = rng.integers(1970, 2025, size=3000)
    a = build_decade_stratified_sample(years, n_per_decade=50, seed=42)
    b = build_decade_stratified_sample(years, n_per_decade=50, seed=42)
    c = build_decade_stratified_sample(years, n_per_decade=50, seed=99)
    assert np.array_equal(a, b)
    assert not np.array_equal(a, c)  # different seed → different draw


def test_decade_sample_indices_in_range() -> None:
    rng = np.random.default_rng(0)
    years = rng.integers(1970, 2025, size=1000)
    idx = build_decade_stratified_sample(years, n_per_decade=30, seed=5)
    assert idx.min() >= 0
    assert idx.max() < len(years)
    assert len(set(idx.tolist())) == len(idx)  # no duplicate indices


# ---------- project_to_clusters == KMeans.predict (the R2 test) ----------


def test_project_matches_kmeans_predict() -> None:
    """The fixed Euclidean projection reproduces KMeans.predict exactly."""
    raw, _ = make_blobs(
        n_samples=800, n_features=16, centers=12, random_state=0,
    )
    raw = raw * 15.0  # non-unit norms (like real embeddings)
    norm = raw / np.linalg.norm(raw, axis=1, keepdims=True)

    km = KMeans(n_clusters=12, n_init=10, random_state=46).fit(norm)
    # Project raw held-out vectors (project normalizes internally by default).
    held_raw, _ = make_blobs(
        n_samples=300, n_features=16, centers=12, random_state=1,
    )
    held_raw = held_raw * 15.0
    held_norm = held_raw / np.linalg.norm(held_raw, axis=1, keepdims=True)

    got = project_to_clusters(held_raw, km.cluster_centers_)
    ref = km.predict(held_norm)
    assert np.array_equal(got, ref)


def test_project_normalize_false_on_prenormalized() -> None:
    """normalize=False projects already-unit vectors without re-normalizing."""
    raw, _ = make_blobs(n_samples=400, n_features=8, centers=6, random_state=2)
    norm = raw / np.linalg.norm(raw, axis=1, keepdims=True)
    km = KMeans(n_clusters=6, n_init=10, random_state=46).fit(norm)
    got = project_to_clusters(norm, km.cluster_centers_, normalize=False)
    assert np.array_equal(got, km.predict(norm))


def test_cosine_argmax_differs_from_euclidean() -> None:
    """Guard: naive argmax(v·c) disagrees with the fix on differing-norm centroids.

    Reproduces the Phase-0.2 bug conditions with a hand-built case where the
    two criteria provably diverge, so the ``== KMeans.predict`` equivalence
    tests above are load-bearing. c0 is unit-norm, c1 is short (norm 0.5); a
    unit vector v = (0.6, 0.8) is genuinely closer to c1 (Euclidean) but has a
    higher dot-product with c0 (cosine) — so the buggy cosine criterion
    mis-assigns it.
    """
    centroids = np.array([[1.0, 0.0], [0.0, 0.5]])  # norms 1.0 and 0.5
    v = np.array([[0.6, 0.8]])  # unit norm; ‖v−c1‖²=0.45 < ‖v−c0‖²=0.80

    euclid = project_to_clusters(v, centroids, normalize=False)
    cosine = np.argmax(v @ centroids.T, axis=1)  # the BUGGY criterion
    assert euclid[0] == 1  # true nearest by Euclidean distance
    assert cosine[0] == 0  # cosine wrongly picks the long centroid
    assert not np.array_equal(euclid, cosine)

    # Confirm the fixed criterion equals the true argmin‖v−c‖² on a batch.
    rng = np.random.default_rng(11)
    batch = rng.normal(size=(200, 2))
    batch = batch / np.linalg.norm(batch, axis=1, keepdims=True)
    true_argmin = np.array([
        int(np.argmin(((row - centroids) ** 2).sum(axis=1))) for row in batch
    ])
    assert np.array_equal(
        project_to_clusters(batch, centroids, normalize=False), true_argmin,
    )


# ---------- fit_clusters ----------


def test_fit_clusters_reproduces_kmeans_centroids() -> None:
    """fit_clusters == KMeans on L2-normalized input with the locked params."""
    raw, _ = make_blobs(n_samples=700, n_features=16, centers=8, random_state=3)
    raw = raw * 20.0
    norm = raw / np.linalg.norm(raw, axis=1, keepdims=True)

    cent = fit_clusters(raw, k=8, n_init=20, random_state=46, max_iter=300)
    ref = KMeans(
        n_clusters=8, n_init=20, random_state=46, max_iter=300,
    ).fit(norm)
    assert cent.shape == (8, 16)
    assert np.allclose(cent, ref.cluster_centers_)


def test_fit_clusters_deterministic() -> None:
    raw, _ = make_blobs(n_samples=500, n_features=12, centers=6, random_state=4)
    a = fit_clusters(raw, k=6, random_state=46)
    b = fit_clusters(raw, k=6, random_state=46)
    assert np.allclose(a, b)


def test_fit_and_project_roundtrip() -> None:
    """fit_clusters centroids + project_to_clusters == a fresh KMeans predict."""
    raw, _ = make_blobs(n_samples=900, n_features=16, centers=10, random_state=5)
    raw = raw * 12.0
    norm = raw / np.linalg.norm(raw, axis=1, keepdims=True)
    cent = fit_clusters(raw, k=10, n_init=10, random_state=46)
    ref = KMeans(n_clusters=10, n_init=10, random_state=46).fit(norm)
    assert np.array_equal(
        project_to_clusters(raw, cent), ref.predict(norm),
    )
