"""Rung 1 — transmission-only dynamics: cumulative complexity ``C`` and the
critical population size (Henrich 2004; Powell-Shennan-Thomas 2009).

This is the WS3 model's ``C`` substrate (primer §5.1) in the classical
scalar-skill abstraction the cultural-evolution literature uses. Later rungs
enrich the state to the primer's concept-base-with-prerequisites representation
and add innovation, conformity ``kappa``, and network structure.

**Model (Henrich 2004, "copy-the-best" oblique transmission).** A single
population of ``n`` learners. Each generation, every learner imitates the current
frontier skill ``z_best`` with an inference error drawn from a Gumbel
distribution of location ``mu`` and scale ``alpha``; ``mu<0`` is the mean loss
("you cannot perfectly infer the expert's skill"), while the Gumbel's right tail
lets rare imitators exceed the model. The new frontier is the best of the ``n``
imitators. Because the maximum of ``n`` i.i.d. ``Gumbel(mu, alpha)`` draws is
``Gumbel(mu + alpha*ln n, alpha)`` with mean ``mu + alpha*(ln n + gamma_E)``, the
frontier drifts per generation by exactly

    drift(n) = mu + alpha * (ln n + gamma_E),                       (Euler gamma)

so cumulative complexity accumulates iff ``n`` exceeds the critical size

    N* = exp(-mu/alpha - gamma_E)     (drift(N*) = 0),

and is lost below it (the Tasmania effect). These closed forms are the
known-answer anchor the tests check the simulation against.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

import numpy as np

# Euler-Mascheroni constant (the mean of a standard Gumbel-for-maxima).
EULER_GAMMA = 0.5772156649015329


def per_gen_drift(n: int, mu: float, alpha: float) -> float:
    """Analytical expected per-generation drift of the frontier skill,
    ``mu + alpha*(ln n + gamma_E)`` (the mean of the max of ``n`` Gumbel draws)."""
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    if alpha <= 0:
        raise ValueError(f"alpha must be > 0, got {alpha}")
    return mu + alpha * (math.log(n) + EULER_GAMMA)


def critical_population_size(mu: float, alpha: float) -> float:
    """The population size ``N* = exp(-mu/alpha - gamma_E)`` at which the frontier
    drift is zero: above it complexity accumulates, below it is lost."""
    if alpha <= 0:
        raise ValueError(f"alpha must be > 0, got {alpha}")
    return math.exp(-mu / alpha - EULER_GAMMA)


def run_transmission(
    n: int,
    mu: float,
    alpha: float,
    generations: int,
    seed: int,
    z0: float = 0.0,
) -> dict[str, Any]:
    """Simulate ``generations`` of copy-the-best transmission for ``n`` learners.

    Returns ``{"z_max": [...], "z_mean": [...], "n", "generations"}`` where
    ``z_max`` (length ``generations+1``, seeded by ``z0``) is the frontier
    cumulative complexity ``C(t)`` and ``z_mean`` (length ``generations``) is the
    mean acquired skill. Deterministic given ``seed``.
    """
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    if alpha <= 0:
        raise ValueError(f"alpha must be > 0, got {alpha}")
    if generations < 1:
        raise ValueError(f"generations must be >= 1, got {generations}")

    rng = np.random.default_rng(seed)
    z_best = float(z0)
    z_max: list[float] = [z_best]
    z_mean: list[float] = []
    for _ in range(generations):
        errors = rng.gumbel(loc=mu, scale=alpha, size=n)
        pop = z_best + errors                 # each learner imitates the frontier
        z_best = float(pop.max())             # the new frontier = best imitator
        z_max.append(z_best)
        z_mean.append(float(pop.mean()))
    return {"z_max": z_max, "z_mean": z_mean, "n": n, "generations": generations}


def measure_drift(
    n: int,
    mu: float,
    alpha: float,
    generations: int,
    seeds: Sequence[int],
    z0: float = 0.0,
) -> float:
    """Empirical per-generation frontier drift, averaged over ``seeds`` (the
    replication discipline: a slope over many runs, not a single-run difference).
    Converges to :func:`per_gen_drift` as ``generations`` and ``|seeds|`` grow."""
    drifts = [
        (run_transmission(n, mu, alpha, generations, s, z0)["z_max"][-1] - z0)
        / generations
        for s in seeds
    ]
    return float(np.mean(drifts))
