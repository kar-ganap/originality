"""Rung 2b — innovation on the concept-base substrate (conformity OFF, ``κ=0``).

Completes the un-bundling that rung 2a set up. rung 2a (``concept_base``) showed
transmission *alone* can only preserve or lose cumulative complexity ``C``. Here we
add the primer's **innovation operator** (Def 4.2): with probability
``ε·g(κ) = ε`` (since ``κ=0 ⇒ g(0)=1``) each agent mints a *novel* element —

  * **vertical** (prob ``b``): an extension to level ``c_i+1``, requiring the agent
    to already hold a complete level-``c_i`` chain — this is the channel that lets
    ``C`` *grow*;
  * **lateral** (prob ``1-b``): a fresh sibling at an existing level ``k`` — breadth.

Every innovation mints a *fresh* element id (a novelty is "never previously
instantiated"), so distinct innovation events are distinct elements: no collisions,
gross per-capita novelty ``≈ ε`` by construction. That is deliberate — it forbids a
spurious crowding decline, so any per-capita fall in ``V`` must come from ``κ``
(rung 3), never from the substrate.

**Representation** (plan §2, decision A — explicit, primer-legible; sweep-scale
optimization is a separate rung-4 concern). Elements live on a single-parent
prerequisite *tree*: ``level[e]``, ``parent[e]`` (``-1`` for a level-1 root),
``birth[e]``. Agent bases are an explicit boolean ``agents × elements`` matrix.
The population is **well-mixed** (network topology is rung 4), so redundancy
``m(e) = M(e,t)`` is the global carrier count — rung 2a's ``(tops>=k).sum()``
generalized off the single chain. Transmission is generational replacement (the
canonical Henrich boundary): each element is re-acquired from scratch each
generation via Eq 4.1 ``a(e) = 1-(1-f)^{m(e)}``, coherently (a child is acquired
only if its parent is acquired the same generation).

**Outputs.** ``C(t)`` is the reproducible frontier (Def 5.1 ``C_R``: the deepest
level whose full chain is present in the repertoire). ``V(t)`` is per-capita
*persisting* novelty (Def 5.2): elements first appearing at ``t`` that survive the
``k``-generation persistence filter, divided by ``N``.

NB (reproduce-published-numbers, ``tasks/lessons.md``): the *quantitative* Henrich
number (``N* = exp(α/β - γ_E) ≈ 616``, Mesoudi eq 9.4) is anchored at **rung 1**
(``transmission.py``, the Gumbel model) — the concept-base substrate has no Gumbel
``α/β`` and does not re-derive it. rung 2b's V-side is anchored by the ``κ=0``
placebo (H2); a published Level-3 breadth number (Strimling 2009) requires bounded
role-models and is deferred to rung 4.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np
import numpy.typing as npt


def _validate(
    n: int, c0: int, f: float, epsilon: float, b: float, generations: int, persistence: int
) -> None:
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    if c0 < 0:
        raise ValueError(f"c0 must be >= 0, got {c0}")
    if not 0.0 <= f <= 1.0:
        raise ValueError(f"f must be in [0, 1], got {f}")
    if not 0.0 <= epsilon <= 1.0:
        raise ValueError(f"epsilon must be in [0, 1], got {epsilon}")
    if not 0.0 <= b <= 1.0:
        raise ValueError(f"b must be in [0, 1], got {b}")
    if generations < 1:
        raise ValueError(f"generations must be >= 1, got {generations}")
    if persistence < 1:
        raise ValueError(f"persistence must be >= 1, got {persistence}")


def reproducible_frontier(
    level: npt.NDArray[np.int64],
    parent: npt.NDArray[np.int64],
    present: npt.NDArray[np.bool_],
) -> int:
    """``C_R`` (primer Def 5.1): the deepest level of any element whose entire
    prerequisite chain is present. Elements are processed in increasing level order
    so each parent's chain-status is settled before its children."""
    e_count = int(present.shape[0])
    if e_count == 0:
        return 0
    order = np.argsort(level, kind="stable")
    chain_ok = np.zeros(e_count, dtype=bool)
    best = 0
    for e in order:
        p = int(parent[e])
        ok = bool(present[e]) and (p == -1 or bool(chain_ok[p]))
        chain_ok[e] = ok
        if ok and int(level[e]) > best:
            best = int(level[e])
    return best


def variance_series(
    birth: npt.NDArray[np.int64], r_hist: npt.NDArray[np.bool_], n: int, k: int
) -> list[float]:
    """Per-capita persisting-novelty series ``V(t)`` (primer Def 5.2).

    ``V(t) = |{e : birth[e]==t and e ∈ R(t'), ∀ t' ∈ [t, t+k]}| / n``. Returns
    ``NaN`` for ``t > generations - k`` (the ``k``-window is not yet observable)."""
    generations = int(r_hist.shape[0]) - 1
    out: list[float] = []
    for t in range(generations + 1):
        if t + k > generations:
            out.append(float("nan"))
            continue
        born = np.where(birth == t)[0]
        if born.size == 0:
            out.append(0.0)
            continue
        survive = r_hist[t : t + k + 1, born].all(axis=0)
        out.append(float(int(survive.sum())) / n)
    return out


def run(
    n: int,
    c0: int,
    f: float,
    epsilon: float,
    b: float,
    generations: int,
    seed: int,
    persistence: int = 1,
) -> dict[str, Any]:
    """Simulate ``generations`` of transmission + innovation (``κ=0``) for ``n``
    well-mixed agents who all start holding the level-``c0`` chain.

    Returns ``{"C", "V", "R_size", ...params}`` where ``C`` and ``R_size`` have
    length ``generations+1`` and ``V`` (length ``generations+1``) carries ``NaN``
    in its last ``persistence`` entries. Deterministic given ``seed``.
    """
    _validate(n, c0, f, epsilon, b, generations, persistence)
    rng = np.random.default_rng(seed)

    # Element registry: the initial level-c0 chain (element j has level j+1, parent j-1).
    level_arr = np.arange(1, c0 + 1, dtype=np.int64)
    parent_arr = np.arange(-1, c0 - 1, dtype=np.int64)  # [-1, 0, 1, ..., c0-2]
    birth: list[int] = [0] * c0
    base = np.ones((n, c0), dtype=bool)  # all agents hold the full initial chain

    def frontier_and_repertoire(
        matrix: npt.NDArray[np.bool_],
    ) -> tuple[int, npt.NDArray[np.bool_]]:
        present = matrix.any(axis=0) if matrix.shape[1] else np.zeros(0, dtype=bool)
        return reproducible_frontier(level_arr, parent_arr, present), present

    c_traj: list[int] = []
    r_hist: list[npt.NDArray[np.bool_]] = []
    c0_frontier, r0 = frontier_and_repertoire(base)
    c_traj.append(c0_frontier)
    r_hist.append(r0.copy())

    for t in range(1, generations + 1):
        e_count = base.shape[1]

        # ── transmission (generational replacement, coherent, well-mixed) ──
        if e_count:
            carriers = base.sum(axis=0)
            acquire_p = 1.0 - (1.0 - f) ** carriers
            new_base = np.zeros((n, e_count), dtype=bool)
            for lvl in range(1, int(level_arr.max()) + 1):
                idx = np.where(level_arr == lvl)[0]
                if idx.size == 0:
                    continue
                hit = rng.random((n, idx.size)) < acquire_p[idx]
                if lvl == 1:
                    new_base[:, idx] = hit
                else:
                    new_base[:, idx] = hit & new_base[:, parent_arr[idx]]
            base = new_base

        # ── innovation (κ=0 ⇒ rate ε; each event mints a fresh element) ──
        innovators = np.where(rng.random(n) < epsilon)[0]
        new_levels: list[int] = []
        new_parents: list[int] = []
        new_owners: list[int] = []
        for i in innovators:
            held = np.where(base[i])[0]
            if held.size == 0:
                new_level, new_parent = 1, -1  # nothing held → a fresh level-1 root
            else:
                depth = int(level_arr[held].max())
                if rng.random() < b:  # vertical: extend the agent's deepest chain
                    top = held[level_arr[held] == depth]
                    new_level, new_parent = depth + 1, int(top.min())
                else:  # lateral: a fresh sibling at an existing level k
                    kk = int(rng.integers(1, depth + 1))
                    if kk == 1:
                        new_level, new_parent = 1, -1
                    else:
                        cand = held[level_arr[held] == kk - 1]
                        new_level, new_parent = kk, int(cand.min())
            new_levels.append(new_level)
            new_parents.append(new_parent)
            new_owners.append(int(i))

        if new_levels:
            add = len(new_levels)
            level_arr = np.concatenate([level_arr, np.array(new_levels, dtype=np.int64)])
            parent_arr = np.concatenate([parent_arr, np.array(new_parents, dtype=np.int64)])
            birth.extend([t] * add)
            block = np.zeros((n, add), dtype=bool)
            block[new_owners, np.arange(add)] = True
            base = np.hstack([base, block]) if base.shape[1] else block

        frontier, present = frontier_and_repertoire(base)
        c_traj.append(frontier)
        r_hist.append(present.copy())

    # Pad the ragged per-generation repertoire snapshots into one array.
    e_final = base.shape[1]
    r_grid = np.zeros((generations + 1, e_final), dtype=bool)
    for t, row in enumerate(r_hist):
        r_grid[t, : row.shape[0]] = row

    v_traj = variance_series(np.array(birth, dtype=np.int64), r_grid, n, persistence)
    r_size = [int(row.sum()) for row in r_hist]

    return {
        "C": c_traj,
        "V": v_traj,
        "R_size": r_size,
        "n": n,
        "c0": c0,
        "f": f,
        "epsilon": epsilon,
        "b": b,
        "persistence": persistence,
        "generations": generations,
    }


def _window_mean(series: Sequence[float], burn_in: int) -> float:
    """Mean over the post-burn-in window, ignoring the ``NaN`` lookahead tail."""
    return float(np.nanmean(np.asarray(series[burn_in:], dtype=float)))


def steady_state_C(
    n: int,
    c0: int,
    f: float,
    epsilon: float,
    b: float,
    generations: int,
    seeds: Sequence[int],
    burn_in: int,
    persistence: int = 1,
) -> npt.NDArray[np.float64]:
    """Per-seed mean ``C`` over the post-burn-in window (replication discipline)."""
    return np.array([
        _window_mean(run(n, c0, f, epsilon, b, generations, s, persistence)["C"], burn_in)
        for s in seeds
    ])


def steady_state_V(
    n: int,
    c0: int,
    f: float,
    epsilon: float,
    b: float,
    generations: int,
    seeds: Sequence[int],
    burn_in: int,
    persistence: int = 1,
) -> npt.NDArray[np.float64]:
    """Per-seed mean per-capita ``V`` over the post-burn-in window."""
    return np.array([
        _window_mean(run(n, c0, f, epsilon, b, generations, s, persistence)["V"], burn_in)
        for s in seeds
    ])


def steady_state_R(
    n: int,
    c0: int,
    f: float,
    epsilon: float,
    b: float,
    generations: int,
    seeds: Sequence[int],
    burn_in: int,
    persistence: int = 1,
) -> npt.NDArray[np.float64]:
    """Per-seed mean repertoire size over the post-burn-in window."""
    return np.array([
        _window_mean(run(n, c0, f, epsilon, b, generations, s, persistence)["R_size"], burn_in)
        for s in seeds
    ])
