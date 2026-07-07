"""Rung 4c — bounded role models: sub-criticality and the Strimling anchor.

The minimal model of **accumulation of independent cultural traits** (Strimling et
al. 2009). Flat traits (no prerequisite structure). Each generation every agent is
replaced and learns from `n` **randomly-sampled role models** (fresh each generation,
excluding self ⇒ no memory, `r=0`): it acquires each trait held by its models with
per-model fidelity `f` (so acquisition prob `1−(1−f)^{m}`, `m` = #models holding it),
and innovates a fresh trait with probability `ε`.

Two regimes, separated by the critical line `f·n = 1` (Enquist et al. 2010's `p·n>1`):

  * **sub-critical (`f·n < 1`):** each trait is lost faster than it spreads, so
    per-individual culture reaches a **bounded, `N`-independent** equilibrium
    `λ_f = ε/(1−f·n)` — at `n=1` this is Strimling's `U/(1−β)` (via Lehmann–Aoki–
    Feldman 2011). The population repertoire `λ_p` still grows ~linearly in `N`.
  * **super-critical (`f·n ≥ 1`):** traits self-sustain and culture runs away,
    growing with `N` (rung 2b's immortal-traits / ballistic regime).

That single sub-/super-critical split is the honest resolution of rung 2b's
"well-mixing → no saturation": bounded culture is a *sub-criticality* phenomenon, not
a redundancy one.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

import numpy as np
import numpy.typing as npt


def _validate(n: int, n_models: int, f: float, epsilon: float, generations: int, c0: int) -> None:
    if n < 2:
        raise ValueError(f"n must be >= 2 (need a role model other than self), got {n}")
    if not 1 <= n_models <= n - 1:
        raise ValueError(f"n_models must be in [1, n-1], got {n_models}")
    if not 0.0 <= f <= 1.0:
        raise ValueError(f"f must be in [0, 1], got {f}")
    if not 0.0 <= epsilon <= 1.0:
        raise ValueError(f"epsilon must be in [0, 1], got {epsilon}")
    if generations < 1:
        raise ValueError(f"generations must be >= 1, got {generations}")
    if c0 < 0:
        raise ValueError(f"c0 must be >= 0, got {c0}")


def strimling_lambda_f(epsilon: float, f: float, n_models: int) -> float:
    """The predicted per-individual equilibrium `λ_f = ε/(1 − f·n)` (sub-critical
    `f·n < 1`). At `n_models=1` this is Strimling's `U/(1−β)` (Lehmann–Aoki–Feldman
    2011, eq 3.4). Returns `inf` at/above the critical line `f·n ≥ 1`."""
    fn = f * n_models
    if fn >= 1.0:
        return math.inf
    return epsilon / (1.0 - fn)


def run(
    n: int,
    n_models: int,
    f: float,
    epsilon: float,
    generations: int,
    seed: int,
    c0: int = 3,
) -> dict[str, Any]:
    """Simulate the bounded-role-model accumulation of independent traits.

    Returns ``{"per_agent", "repertoire", ...params}`` where ``per_agent[t]`` is the
    mean number of traits an agent holds (`λ_f`) and ``repertoire[t]`` is the number of
    distinct live traits (`λ_p`). Deterministic given ``seed``."""
    _validate(n, n_models, f, epsilon, generations, c0)
    rng = np.random.default_rng(seed)
    base = np.ones((n, c0), dtype=bool)
    agent_idx = np.arange(n)[:, None]

    per_agent: list[float] = [float(base.sum(axis=1).mean())]
    repertoire: list[int] = [int(base.any(axis=0).sum())]

    for _t in range(1, generations + 1):
        e_count = base.shape[1]
        # sample n_models role models per agent from the OTHER n-1 agents (exclude self)
        models = rng.integers(0, n - 1, size=(n, n_models))
        models += (models >= agent_idx)                       # skip self ⇒ no memory
        m = base[models].sum(axis=1)                          # (n, e): #models holding each trait
        acquire_p = 1.0 - (1.0 - f) ** m
        base = rng.random((n, e_count)) < acquire_p           # generational replacement
        # innovation: each agent w.p. ε mints a fresh trait
        innovators = np.where(rng.random(n) < epsilon)[0]
        if innovators.size:
            block = np.zeros((n, innovators.size), dtype=bool)
            block[innovators, np.arange(innovators.size)] = True
            base = np.hstack([base, block])
        base = base[:, base.any(axis=0)]  # prune dead traits (behavior-preserving speedup)
        per_agent.append(float(base.sum(axis=1).mean()))
        repertoire.append(int(base.shape[1]))

    return {
        "per_agent": per_agent,
        "repertoire": repertoire,
        "n": n, "n_models": n_models, "f": f, "epsilon": epsilon,
        "generations": generations, "c0": c0,
    }


def steady_state(
    n: int,
    n_models: int,
    f: float,
    epsilon: float,
    generations: int,
    seeds: Sequence[int],
    burn_in: int,
    metric: str = "per_agent",
    c0: int = 3,
) -> npt.NDArray[np.float64]:
    """Per-seed steady-state ``metric`` (``"per_agent"`` = `λ_f`, ``"repertoire"`` =
    `λ_p`): the post-burn-in window mean."""
    if metric not in ("per_agent", "repertoire"):
        raise ValueError(f"metric must be 'per_agent' or 'repertoire', got {metric!r}")
    return np.array([
        float(np.mean(run(n, n_models, f, epsilon, generations, s, c0)[metric][burn_in:]))
        for s in seeds
    ])
