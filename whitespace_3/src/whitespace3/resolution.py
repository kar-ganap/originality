"""Noise-floor diagnostics for the counterfactual resolution map.

Spec-independent primitives for design §3 (`docs/counterfactual-resolution-map.md`), under the
locked pre-registration `docs/resolution-map-phase3-prereg.md`. These classify a model output as
deterministic-flat / deterministic-clock / stochastic-with-signal / stochastic-noise-dominated, and
decompose its variance — knowing nothing about the model, the grid, or the SESOI values, which the
caller supplies. The point of keeping them here, generic and tested, is that the classification rule
cannot be quietly bent once model results are in view.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import numpy.typing as npt

FloatArray = npt.NDArray[np.float64]

DETERMINISM_TOL = 1e-6
"""Seed-CV below this is float-noise, i.e. deterministic. A tolerance, not a science threshold."""


def seed_cv(values: Sequence[float] | FloatArray) -> float:
    """Coefficient of variation across seeds. ``inf`` when the mean is ~0 (CV undefined)."""
    arr = np.asarray(values, dtype=np.float64)
    mean = float(np.mean(arr))
    if abs(mean) < 1e-300:
        return float("inf")
    return float(np.std(arr)) / abs(mean)


def mean_ci(
    values: Sequence[float] | FloatArray, *, n_boot: int = 2000, seed: int = 0, alpha: float = 0.05
) -> tuple[float, float]:
    """Percentile bootstrap CI for the mean of per-seed values."""
    arr = np.asarray(values, dtype=np.float64)
    if arr.size < 2:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    means = arr[rng.integers(0, arr.size, size=(n_boot, arr.size))].mean(axis=1)
    return (
        float(np.percentile(means, 100 * alpha / 2)),
        float(np.percentile(means, 100 * (1 - alpha / 2))),
    )


def classify(
    *,
    effect: float,
    ci_lo: float,
    ci_hi: float,
    sesoi: float,
    seed_cv_level: float,
    det_tol: float = DETERMINISM_TOL,
) -> str:
    """The pre-registered 4-way rule (pre-reg §"4-way classification rule").

    ``effect`` is the response to the lever (a level-difference or a slope); ``ci_lo/ci_hi`` its
    seed-bootstrap CI; ``sesoi`` the smallest meaningful effect in the estimand's units;
    ``seed_cv_level`` the coefficient of variation of the *output level* across seeds — determinism
    is a property of the output, so it is judged there, and it takes priority over the CI test (a
    deterministic output has a degenerate CI that would otherwise read as "excludes zero").
    """
    if seed_cv_level < det_tol:
        return "deterministic-clock" if abs(effect) >= sesoi else "deterministic-flat"
    excludes_zero = ci_lo > 0.0 or ci_hi < 0.0
    if excludes_zero and abs(effect) >= sesoi:
        return "stochastic-with-signal"
    return "stochastic-noise-dominated"


def crossover_exists(slopes: Sequence[tuple[float, float, float]]) -> bool:
    """E4's internal-relevance test: is there a CI-separated V→C sign flip across λ?

    ``slopes`` is ``(point, ci_lo, ci_hi)`` per λ, in **ascending-λ order**. Returns True iff some λ
    has its slope CI entirely above 0 (reliably V-favouring) followed by a later λ with its CI
    entirely below 0 (reliably C-favouring). A point whose CI straddles 0 contributes no determined
    sign; the flip must be carried by CI-separated points. The order matters — a wrong-direction
    (−then+) sequence is not WS3's crossover. Magnitude is not judged here (design
    §"E4 internal standard"); that is deferred to stage 2.
    """
    v_favouring_seen = False
    for _point, ci_lo, ci_hi in slopes:
        if ci_lo > 0.0:
            v_favouring_seen = True
        elif ci_hi < 0.0 and v_favouring_seen:
            return True
    return False


def variance_decompose(nested: FloatArray) -> dict[str, float]:
    """Split total variance into between-seed and within-seed(graph-draw) fractions.

    ``nested`` is ``(n_seeds, n_graph_draws)`` — one row per seed, its columns the repeated
    graph draws. Uses the standard one-way decomposition: between-group variance of the row means
    against the pooled within-row variance. Returns fractions of their sum, so a noise-dominated
    verdict can be attributed to a fixable (more seeds) vs intrinsic source.
    """
    data = np.asarray(nested, dtype=np.float64)
    if data.ndim != 2 or data.shape[1] < 2:
        raise ValueError("nested must be (n_seeds, n_graph_draws) with >=2 draws per seed")
    row_means = data.mean(axis=1)
    between = float(np.var(row_means, ddof=1))
    within = float(np.mean(np.var(data, axis=1, ddof=1)))
    total = between + within
    if total <= 0.0:
        return {"seed_fraction": 0.0, "graph_fraction": 0.0}
    return {"seed_fraction": between / total, "graph_fraction": within / total}
