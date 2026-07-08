"""Rung 5b — light mean-field analytics (simulation-*guided*, not airtight theorems; the
compass says keep analytics light). Two intuitions the simulation makes precise:

**C — Henrich carrier-survival.** An element's steady-state carrier count `c*` is the fixed
point of `c ↦ n·(1−(1−f)^c)`: it saturates near `n` when maintained, and collapses to 0
below the **maintenance threshold** `n* = 1/ln(1/(1−f))` — the small-population loss of
cumulative complexity (Tasmania).

**V — the crossover law.** Per-capita persisting novelty is, mean-field,
`V*(N) ≈ ε · g(λ·s(N)) · P(N)` with `g=e^{-κ}`, `s(N)=ln N` (κ scales with scale), and
`P(N)` the persistence (non-extinction) probability of a fresh innovation. Then

    ∂ ln V*/∂ ln N = 0   ⟺   λ* = d ln P / d ln N ,

i.e. **the crossover conformity `λ*` equals the returns-to-scale of persistence.** Because
persistence saturates fast (`N·f ≫ 1` ⇒ `P→1`), that elasticity is small — so `λ*` is
small, which is why the simulated crossover sits near zero (`≈0.09`, rung 3/5a).
"""

from __future__ import annotations

import numpy as np


def maintenance_threshold(f: float) -> float:
    """Henrich critical population size for element maintenance, `n* = 1/ln(1/(1−f))`."""
    if not 0.0 < f < 1.0:
        raise ValueError(f"f must be in (0, 1), got {f}")
    return float(1.0 / -np.log1p(-f))


def carrier_fixed_point(n: int, f: float, iters: int = 500) -> float:
    """Steady-state carrier count `c*` of an element under generational replacement — the
    fixed point of `c ↦ n·(1−(1−f)^c)`. `≈ n` when maintained (large `n·f`), `→ 0` below the
    maintenance threshold."""
    if n < 1 or not 0.0 <= f <= 1.0:
        raise ValueError(f"need n>=1 and f in [0,1], got n={n}, f={f}")
    c = float(n)
    for _ in range(iters):
        c = n * (1.0 - (1.0 - f) ** c)
    return c


def branching_survival(mu: float, iters: int = 500) -> float:
    """Persistence `P`: non-extinction probability of a Galton–Watson process with
    `Poisson(μ)` offspring (`μ` = expected carriers spawned by one carrier, `≈ n·f`).
    `q = e^{-μ(1−q)}`, `P = 1−q`. Zero for `μ ≤ 1`, rising to 1 as `μ → ∞`."""
    if mu <= 1.0:
        return 0.0
    q = float(np.exp(-mu))
    for _ in range(iters):
        q = float(np.exp(-mu * (1.0 - q)))
    return 1.0 - q


def v_star_meanfield(n: int, lam: float, epsilon: float, f: float) -> float:
    """Mean-field per-capita `V*(N) ≈ ε · N^{−λ} · P(N)` (with `s(N)=ln N`, `g=e^{−κ}`).
    Hump-shaped in `N` at intermediate `λ`: persistence rises (more minds) then the
    `N^{−λ}` consensus suppression dominates."""
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    return float(epsilon * (n ** (-lam)) * branching_survival(n * f))


def crossover_lambda(ns: list[int], persistence: list[float]) -> float:
    """The crossover law `λ* = d ln P/d ln N` — the persistence elasticity over `ns`. `P(N)`
    is measured from the simulation (or a mean-field); this returns the `λ` at which the
    conformity exponent exactly cancels the returns-to-scale of persistence."""
    ln_n = np.log(np.asarray(ns, dtype=float))
    ln_p = np.log(np.asarray(persistence, dtype=float))
    return float(np.polyfit(ln_n, ln_p, 1)[0])
