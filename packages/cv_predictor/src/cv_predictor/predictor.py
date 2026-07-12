"""Fast mean-field C/V diversity-collapse regime predictor (no simulation).

The mean-field per-capita persisting novelty ``V*(N) = ε · N^{−λ} · P(N)`` (see
``analytics.v_star_meanfield``; ``P(N)`` is the Galton–Watson persistence
``branching_survival(N·f)``) is **hump-shaped** in ``N``: persistence ``P(N)`` rises with
more minds while the ``N^{−λ}`` consensus-suppression term falls. The **crossover
conformity** ``λ*`` is the ``λ`` at which ``d ln V*/d ln N = 0`` — the log–log slope flips
sign there. Below ``λ*`` the system is **V-favouring** (per-capita novelty *rises* with
scale — small teams and large fields can both win); above ``λ*`` it is **C-favouring**
(novelty *falls* with scale — diversity collapse, while cumulative depth ``C`` still accrues).

Because ``log V* = log ε − λ·log N + log P(N)``, the log–log slope is exactly
``d ln P/d ln N − λ``, so the crossover ``λ*`` equals the **persistence elasticity**
``d ln P/d ln N``. ``predict`` locates ``λ*`` by scanning the log–log slope over a ``λ`` grid
and interpolating its zero crossing; that value should agree with
``analytics.crossover_lambda(n_grid, [branching_survival(n·f) …])`` (a cross-check). Because
persistence saturates fast (``N·f ≫ 1 ⇒ P→1``), the elasticity — hence ``λ*`` — is small
whenever ``f`` is high; the crossover is most visible at low fidelity, where ``P(N)`` is
still climbing across the grid.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

from .analytics import v_star_meanfield


@dataclass
class SystemParams:
    """Inputs to the mean-field forecast.

    ``lam`` — conformity exponent (maps to ``v_star_meanfield``'s ``lam``); ``epsilon`` —
    innovation rate; ``f`` — fidelity; ``n_grid`` — population sizes over which the ``V*(N)``
    trajectory and its log–log slope are evaluated.
    """

    lam: float
    epsilon: float
    f: float
    n_grid: list[int] = field(default_factory=lambda: [10, 20, 50, 100, 200, 500, 1000])


@dataclass
class RegimeForecast:
    """Output of :func:`predict`.

    ``lambda_star`` — the ``λ`` where ``d ln V*/d ln N`` crosses 0 (``nan`` if there is no
    crossing in ``[0, 1]``); ``regime`` — ``"V-favouring"`` if the slope at ``params.lam`` is
    positive else ``"C-favouring"``; ``slope_at_lam`` — ``d ln V*/d ln N`` at ``params.lam``;
    ``v_trajectory`` — ``V*(n)`` over ``n_grid`` at ``params.lam``.
    """

    lambda_star: float
    regime: str
    slope_at_lam: float
    v_trajectory: list[float]


def _loglog_slope(lam: float, epsilon: float, f: float, n_grid: list[int]) -> float:
    """OLS slope of ``log V*`` on ``log N`` over ``n_grid``, using only entries with
    ``V* > 0`` (``= d ln V*/d ln N`` at ``lam``). Returns ``nan`` for < 2 positive entries.

    The ``V* > 0`` mask is ``λ``-independent (it is ``N·f > 1``), so across a fixed ``f``/grid
    the slope is exactly linear in ``λ`` — which makes the ``λ*`` scan in :func:`predict` an
    exact interpolation and the regime/``λ*`` consistency hold by construction.
    """
    v = np.array([v_star_meanfield(n, lam, epsilon, f) for n in n_grid], dtype=float)
    mask = v > 0.0
    if int(mask.sum()) < 2:
        return float("nan")
    ln_n = np.log(np.asarray(n_grid, dtype=float)[mask])
    ln_v = np.log(v[mask])
    return float(np.polyfit(ln_n, ln_v, 1)[0])


def predict(params: SystemParams) -> RegimeForecast:
    """Forecast the C/V regime for ``params`` from the mean-field ``V*(N)`` (no simulation)."""
    n_grid = params.n_grid
    v_trajectory = [
        v_star_meanfield(n, params.lam, params.epsilon, params.f) for n in n_grid
    ]

    slope_at_lam = _loglog_slope(params.lam, params.epsilon, params.f, n_grid)
    regime = "V-favouring" if slope_at_lam > 0.0 else "C-favouring"

    # Locate λ* = the λ where the log–log slope crosses zero, on a fixed candidate grid.
    lams = np.linspace(0.0, 1.0, 101)
    slopes = [_loglog_slope(float(lm), params.epsilon, params.f, n_grid) for lm in lams]
    lambda_star = float("nan")
    for i in range(len(slopes) - 1):
        s0, s1 = slopes[i], slopes[i + 1]
        if math.isnan(s0) or math.isnan(s1):
            continue
        if s0 >= 0.0 > s1:  # first downward zero-crossing
            frac = s0 / (s0 - s1)
            lambda_star = float(lams[i] + frac * (lams[i + 1] - lams[i]))
            break

    return RegimeForecast(
        lambda_star=lambda_star,
        regime=regime,
        slope_at_lam=slope_at_lam,
        v_trajectory=v_trajectory,
    )
