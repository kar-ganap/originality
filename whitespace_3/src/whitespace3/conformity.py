"""Rung 3 — the crossover measurement toolkit.

The conformity dynamics live in ``innovation.run`` (κ is part of the innovation
operator, primer Def 4.2). This module is the *measurement* layer that turns runs
into the load-bearing estimand: the slope of steady-state per-capita ``V*`` on
``log N`` and the conformity-scaling threshold ``λ*`` where it crosses zero.

Estimation discipline (ported from WS2): the crossover is a **regression slope with
a seed-bootstrap CI**, never a two-point ``V(N_big)−V(N_small)`` difference; ``C*``
and ``V*`` are reported **absolute and separate**, never a ``C/V`` ratio.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

import numpy as np
import numpy.typing as npt

from .innovation import run

RunFn = Callable[..., dict[str, Any]]


def logN_slope_ci(
    ns: Sequence[int],
    per_seed: dict[int, npt.NDArray[np.float64]],
    n_boot: int = 400,
    seed: int = 0,
) -> dict[str, float]:
    """Slope of the mean metric on ``log N`` with a seed-resampling bootstrap CI.

    ``per_seed`` maps each ``N`` to its per-seed steady-state values. Returns
    ``{"point", "lo", "hi"}`` (2.5 / 97.5 percentiles of the bootstrap slope)."""
    rng = np.random.default_rng(seed)
    log_n = np.log(np.asarray(ns, dtype=float))
    slopes = np.empty(n_boot, dtype=float)
    for j in range(n_boot):
        means = np.array(
            [float(np.mean(rng.choice(per_seed[nn], size=per_seed[nn].size, replace=True)))
             for nn in ns]
        )
        slopes[j] = float(np.polyfit(log_n, means, 1)[0])
    point = float(np.polyfit(log_n, [float(np.mean(per_seed[nn])) for nn in ns], 1)[0])
    return {
        "point": point,
        "lo": float(np.percentile(slopes, 2.5)),
        "hi": float(np.percentile(slopes, 97.5)),
    }


def steady_grid(
    ns: Sequence[int],
    lam: float,
    *,
    seeds: Sequence[int],
    burn_in: int,
    metric: str = "V",
    run_fn: RunFn = run,
    **run_kw: Any,
) -> dict[int, npt.NDArray[np.float64]]:
    """Per-seed steady-state ``metric`` (``"C"``/``"V"``/``"H"``…) for each ``N``: the
    post-burn-in window mean (``NaN`` lookahead tail ignored). ``run_fn`` is the model
    (``innovation.run`` by default; pass ``canon.run`` for the rung-4a substrate) and
    ``run_kw`` forwards its parameters."""
    if metric not in ("C", "V", "H", "R_size", "Vstruct", "Vlat", "W"):
        raise ValueError(f"metric must be one of C/V/H/R_size/Vstruct/Vlat/W, got {metric!r}")
    out: dict[int, npt.NDArray[np.float64]] = {}
    for nn in ns:
        vals = [
            float(np.nanmean(np.asarray(run_fn(nn, seed=s, lam=lam, **run_kw)[metric][burn_in:],
                                        dtype=float)))
            for s in seeds
        ]
        out[nn] = np.asarray(vals, dtype=float)
    return out


def crossover_slope(
    ns: Sequence[int],
    lam: float,
    *,
    seeds: Sequence[int],
    burn_in: int,
    metric: str = "V",
    n_boot: int = 400,
    boot_seed: int = 0,
    run_fn: RunFn = run,
    **run_kw: Any,
) -> dict[str, float]:
    """``∂metric*/∂logN`` at conformity-scaling ``lam``, with seed-bootstrap CI."""
    grid = steady_grid(ns, lam, seeds=seeds, burn_in=burn_in, metric=metric,
                       run_fn=run_fn, **run_kw)
    return logN_slope_ci(ns, grid, n_boot=n_boot, seed=boot_seed)


def locate_lambda_star(
    ns: Sequence[int],
    lams: Sequence[float],
    *,
    seeds: Sequence[int],
    burn_in: int,
    metric: str = "V",
    n_boot: int = 400,
    boot_seed: int = 0,
    run_fn: RunFn = run,
    **run_kw: Any,
) -> dict[str, Any]:
    """Sweep ``lams``; return each slope CI and ``λ*`` = where the point slope first
    crosses zero (linearly interpolated between the bracketing ``λ`` values). ``λ*``
    is ``None`` if the slope never reaches ``≤ 0`` over ``lams``."""
    slopes: dict[float, dict[str, float]] = {}
    for lam in lams:
        slopes[lam] = crossover_slope(
            ns, lam, seeds=seeds, burn_in=burn_in, metric=metric,
            n_boot=n_boot, boot_seed=boot_seed, run_fn=run_fn, **run_kw,
        )
    lam_star: float | None = None
    prev: tuple[float, float] | None = None
    for lam in lams:
        pt = slopes[lam]["point"]
        if pt <= 0.0:
            if prev is None:
                lam_star = float(lam)
            else:
                lp, pp = prev
                lam_star = float(lp) if pt == pp else float(
                    lp + (0.0 - pp) * (lam - lp) / (pt - pp))
            break
        prev = (float(lam), pt)
    return {"slopes": slopes, "lambda_star": lam_star}
