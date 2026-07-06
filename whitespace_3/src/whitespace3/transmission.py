"""Rung 1 — transmission-only dynamics: cumulative complexity ``C`` and the
critical population size (Henrich 2004, "Demography and Cultural Evolution").

The WS3 model's ``C`` substrate (primer §5.1) in the classical scalar-skill
abstraction the cultural-evolution literature uses. Later rungs enrich the state
to the primer's concept-base-with-prerequisites representation and add innovation,
conformity ``kappa``, and network structure.

**Model (Henrich 2004; parameter names follow the paper).** A population of ``n``
learners. Each generation, every learner copies the current most-skilled
individual ``z_h`` with an inference error drawn from a Gumbel distribution of
**mode ``z_h - alpha``** and **dispersion ``beta``**: ``alpha`` is the
transmission-error / difficulty (mean loss), ``beta`` the inferential dispersion
(the Gumbel right tail lets rare learners exceed the model). Because the maximum
of ``n`` i.i.d. draws from ``Gumbel(mode, beta)`` has mean ``mode + beta*(ln n +
gamma_E)``, the expected change in mean skill per generation is Henrich's

    Eq (2):   dz_bar = -alpha + beta*(gamma_E + ln n),          (gamma_E = Euler)

so cumulative complexity accumulates iff ``n`` exceeds the critical size

    Eq (3):   N* = exp(alpha/beta - gamma_E)     (dz_bar(N*) = 0),

and is lost below it (the Tasmania effect). These are the paper's Eqs (2) and (3)
verbatim; the tests below reproduce Mesoudi's canonical ``DemographyModel``
(Simulation Models of Cultural Evolution in R, Model 9), including his specific
runs (N=100 vs N=1 at alpha=30, beta=15) and the Delta-z-bar-vs-N crossover at
``N* ~= 616`` for alpha=7, beta=1.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

import numpy as np

# Euler-Mascheroni constant (Henrich's ``epsilon`` in Eqs (2)-(3); the mean of a
# standard Gumbel-for-maxima).
EULER_GAMMA = 0.5772156649015329


def _validate(n: int, alpha: float, beta: float, generations: int) -> None:
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    if alpha < 0:
        raise ValueError(f"alpha (difficulty/loss) must be >= 0, got {alpha}")
    if beta <= 0:
        raise ValueError(f"beta (dispersion) must be > 0, got {beta}")
    if generations < 1:
        raise ValueError(f"generations must be >= 1, got {generations}")


def per_gen_drift(n: int, alpha: float, beta: float) -> float:
    """Henrich 2004 Eq (2): expected per-generation change in mean skill,
    ``-alpha + beta*(ln n + gamma_E)`` (the mean of the max of ``n`` Gumbel draws)."""
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    if beta <= 0:
        raise ValueError(f"beta must be > 0, got {beta}")
    return -alpha + beta * (math.log(n) + EULER_GAMMA)


def critical_population_size(alpha: float, beta: float) -> float:
    """Henrich 2004 Eq (3): the population size ``N* = exp(alpha/beta - gamma_E)``
    at which the drift is zero — above it complexity accumulates, below it is lost."""
    if beta <= 0:
        raise ValueError(f"beta must be > 0, got {beta}")
    return math.exp(alpha / beta - EULER_GAMMA)


def run_transmission(
    n: int,
    alpha: float,
    beta: float,
    generations: int,
    seed: int,
    z0: float = 0.0,
) -> dict[str, Any]:
    """Simulate ``generations`` of copy-the-best transmission for ``n`` learners
    (Henrich 2004 / Mesoudi ``DemographyModel``).

    Returns ``{"z_max": [...], "z_mean": [...], "n", "generations"}`` where
    ``z_max`` (length ``generations+1``, seeded by ``z0``) is the frontier
    complexity ``C(t)`` and ``z_mean`` (Mesoudi's ``z_bar``) is the mean acquired
    skill. Deterministic given ``seed``.
    """
    _validate(n, alpha, beta, generations)
    rng = np.random.default_rng(seed)
    z_h = float(z0)
    z_max: list[float] = [z_h]
    z_mean: list[float] = []
    for _ in range(generations):
        # each learner draws from Gumbel(mode = z_h - alpha, scale = beta)
        pop = z_h + rng.gumbel(loc=-alpha, scale=beta, size=n)
        z_h = float(pop.max())
        z_max.append(z_h)
        z_mean.append(float(pop.mean()))
    return {"z_max": z_max, "z_mean": z_mean, "n": n, "generations": generations}


def measure_drift(
    n: int,
    alpha: float,
    beta: float,
    generations: int,
    seeds: Sequence[int],
    z0: float = 0.0,
) -> float:
    """Empirical per-generation frontier drift (= Henrich's ``dz_bar``), averaged
    over ``seeds`` (the replication discipline: a slope over many runs, not a
    single-run difference). Converges to :func:`per_gen_drift` as ``generations``
    and ``|seeds|`` grow."""
    drifts = [
        (run_transmission(n, alpha, beta, generations, s, z0)["z_max"][-1] - z0)
        / generations
        for s in seeds
    ]
    return float(np.mean(drifts))
