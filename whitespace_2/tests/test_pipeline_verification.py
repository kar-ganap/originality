"""Correctness / trust checks for the Stage-2 analysis pipeline.

These pin the metric implementations against INDEPENDENT computations
(scipy / sklearn / a different formula) and check the permutation machinery's
null calibration — the trust battery from `experiments/phase-2.2/
verify_correctness.py`, promoted to permanent tests. Cross-implementation checks
are fast; the permutation-calibration check is `slow` (deselected by default).
"""

from __future__ import annotations

import numpy as np
import pytest
from scipy.stats import entropy as sp_entropy
from sklearn.decomposition import PCA

from whitespace2.canonical_metrics import gini
from whitespace2.divergence import (
    divergence_test,
    ols_trend,
    permutation_slope_test,
    residual_trend,
    standardized_effect,
)
from whitespace2.semantic_metrics import (
    cluster_entropy,
    effective_dimensionality,
    mean_pairwise_cosine_distance,
)


def test_gini_vs_mean_absolute_difference() -> None:
    """gini == MAD / (2·mean) (a formula-independent definition)."""
    x = np.random.default_rng(0).exponential(size=800)
    mad = np.abs(x[:, None] - x[None, :]).mean()
    assert abs(gini(x) - mad / (2 * x.mean())) < 1e-9


def test_effective_dim_vs_sklearn_pca() -> None:
    """effective_dimensionality == participation ratio of sklearn PCA eigenvalues."""
    rng = np.random.default_rng(1)
    v = rng.normal(size=(1500, 30)) @ rng.normal(size=(30, 30))
    ev = PCA().fit(v).explained_variance_
    assert abs(effective_dimensionality(v) - ev.sum() ** 2 / (ev ** 2).sum()) < 1e-6


def test_cluster_entropy_vs_scipy_plus_mm() -> None:
    """cluster_entropy == scipy natural-log entropy + Miller-Madow (k−1)/(2n)."""
    a = np.random.default_rng(2).integers(0, 12, size=400)
    counts = np.bincount(a, minlength=12)
    mm = sp_entropy(counts / counts.sum()) + ((counts > 0).sum() - 1) / (2 * a.size)
    assert abs(cluster_entropy(a, 12) - mm) < 1e-9


def test_mean_pairwise_vs_explicit_loop() -> None:
    w = np.random.default_rng(3).normal(size=(40, 8))
    wn = w / np.linalg.norm(w, axis=1, keepdims=True)
    ref = float(np.mean(
        [1 - wn[i] @ wn[j] for i in range(40) for j in range(i + 1, 40)]))
    assert abs(mean_pairwise_cosine_distance(w) - ref) < 1e-9


def test_ols_and_effect_vs_numpy() -> None:
    rng = np.random.default_rng(4)
    x = np.arange(60.0)
    y = 2.5 * x + rng.normal(size=60)
    assert abs(ols_trend(x, y)["slope"] - float(np.polyfit(x, y, 1)[0])) < 1e-8
    man = float(np.polyfit(x, y, 1)[0]) * (x.max() - x.min()) / float(np.std(y, ddof=1))
    assert abs(standardized_effect(x, y)["total_change_sd"] - man) < 1e-8


def test_residual_year_coef_vs_normal_equations() -> None:
    """residual_trend's partial year coefficient == a direct normal-equations OLS."""
    rng = np.random.default_rng(5)
    x = np.arange(60.0)
    y = 2.5 * x + rng.normal(size=60)
    ctrl = rng.normal(size=60)
    dm = np.column_stack([np.ones(60), x, ctrl])
    beta = np.linalg.solve(dm.T @ dm, dm.T @ y)
    got = residual_trend(x, y, [ctrl], n_perm=200)["year_coef"]
    assert abs(got - float(beta[1])) < 1e-6


def test_divergence_null_on_proportional_series() -> None:
    """A proportional (semantic ∝ demographic) series is a known null → not confirmed."""
    rng = np.random.default_rng(6)
    yr = np.arange(1970.0, 2025.0)
    base = 1.0 + 0.02 * (yr - 1970) + rng.normal(scale=0.01, size=55)
    sem = {"cluster_entropy": 5 * base, "effective_dimensionality": 200 * base,
           "mean_pairwise_cosine": 0.5 * base}
    res = divergence_test(yr, base, sem, 0.3 + 0.003 * (yr - 1970), n_perm=1000)
    assert res["divergence_confirmed"] is False


@pytest.mark.slow
def test_permutation_null_calibration() -> None:
    """On pure-noise series the permutation test rejects at ≈ alpha (not inflated)."""
    rng = np.random.default_rng(7)
    x = np.arange(55.0)
    sig = sum(
        permutation_slope_test(x, rng.normal(size=55), n_perm=500,
                               seed=i)["significant"]
        for i in range(1000)
    )
    assert sig / 1000 < 0.03      # alpha=0.01, allow Monte-Carlo slack
