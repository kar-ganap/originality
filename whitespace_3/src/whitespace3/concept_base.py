"""Rung 2a — concept-base transmission on a prerequisite ladder (maintenance /
loss), with NO innovation yet.

Un-bundles transmission from innovation (``transmission.py`` is the rung-1 scalar
model that fused them in a single Gumbel error). Here transmission is the
primer's per-level acquisition (Def 4.1): a learner acquires level ``k`` only if
it already holds level ``k-1`` (the prerequisite) and at least one of the ``m_k``
current holders transmits successfully, probability ``1 - (1-f)**m_k`` (``m_k`` =
redundancy). Because no one can transmit a level nobody holds, **transmission
alone can only maintain or lose cumulative complexity ``C`` — never grow it.**
Growth waits for innovation (rung 2b), which is exactly what lets ``V`` be
defined separately from ``C``.

State: by coherence a learner's concept base ``B_i = {1..c_i}`` is described by
its top level ``c_i``; ``C(t) = max_i c_i`` (primer Def 5.1). The qualitative
result — C preserved when the population is large (redundancy protects every
level), lost when small (the Tasmania direction) — is the Henrich/Powell
preservation insight.

NB (reproduce-published-numbers principle, ``tasks/lessons.md`` 2026-07-03): this
per-level mechanism is OUR construction (primer Def 4.1), not a verbatim published
model, so it reproduces the qualitative DIRECTION only, NOT a specific published
number (Level 3 unavailable — novel mechanism; documented reason). Powell's
metapopulation is the Level-3 target for the later network rung.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np


def _validate(n: int, c0: int, f: float, generations: int) -> None:
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    if c0 < 0:
        raise ValueError(f"c0 must be >= 0, got {c0}")
    if not 0.0 <= f <= 1.0:
        raise ValueError(f"f must be in [0, 1], got {f}")
    if generations < 1:
        raise ValueError(f"generations must be >= 1, got {generations}")


def run_transmission(
    n: int,
    c0: int,
    f: float,
    generations: int,
    seed: int,
) -> dict[str, Any]:
    """Simulate ``generations`` of per-level transmission for ``n`` learners who
    all start holding the ladder up to level ``c0``.

    Returns ``{"C": [...], "n", "c0", "generations"}`` where ``C`` (length
    ``generations+1``) is the frontier complexity ``C(t) = max_i c_i``.
    Deterministic given ``seed``; ``C`` is non-increasing (no innovation).
    """
    _validate(n, c0, f, generations)
    rng = np.random.default_rng(seed)
    tops = np.full(n, c0, dtype=np.int64)          # coherent base B_i = {1..tops[i]}
    trajectory: list[int] = [int(tops.max())]
    for _ in range(generations):
        c_cur = int(tops.max())
        if c_cur == 0:                              # nothing left to transmit
            trajectory.append(0)
            continue
        # redundancy m_k = #agents holding level k (k = 1..c_cur). The chain makes
        # m non-increasing in k, so levels are lost strictly top-down.
        m = np.array([int((tops >= k).sum()) for k in range(1, c_cur + 1)],
                     dtype=np.int64)
        a = 1.0 - (1.0 - f) ** m                    # per-level acquisition prob (Def 4.1)
        # Each learner acquires bottom-up; a prerequisite failure blocks every
        # higher level. cumprod turns a success row [1,1,0,1,..] -> [1,1,0,0,..],
        # whose sum = the number of leading successes = the acquired top level.
        success = rng.random((n, c_cur)) < a
        tops = np.cumprod(success, axis=1).sum(axis=1).astype(np.int64)
        trajectory.append(int(tops.max()))
    return {"C": trajectory, "n": n, "c0": c0, "generations": generations}


def retained_complexity(
    n: int,
    c0: int,
    f: float,
    generations: int,
    seeds: Sequence[int],
) -> float:
    """Mean final frontier complexity over ``seeds`` (replication discipline:
    average over runs, not a single trajectory)."""
    return float(np.mean(
        [run_transmission(n, c0, f, generations, s)["C"][-1] for s in seeds]))
