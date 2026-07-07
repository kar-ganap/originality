"""Rung 4a — the endogenous canon: `κ` driven by real canonical concentration `H`.

rung 3 established the crossover on a *reduced-form* signal `s ≈ ln N`. Here we
replace it with the primer's canon-deviation driver `κ = λ·H(t)`, where
`H(t) = Gini(w)` is canonical concentration on a **multi-prerequisite attachment
graph** and `w(e)` is the **dependency-closure weight** (how much later work
transitively rests on `e`). Verified precondition: closure-`H` rises with scale
(`0.83→0.96`) while raw in-degree concentration is scale-invariant — so the
*closure* structure is what lets the endogenous mechanism reproduce the crossover.

Substrate (generalizes rung 2b/3's single-parent tree to a multi-parent DAG):
elements carry a *prereq list*; an agent holds `e` only if it holds **all** of
`prereqs[e]` (coherence). Innovation (throttled at rate `ε·g(κ)`) is **vertical**
(prob `b`: extend the agent's deepest chain → grows `C`) or **lateral** (prob `1−b`:
attach to `p` prereqs drawn `∝` in-degree — preferential attachment, which builds the
concentrated canon). `κ = λ·H` is **uniform** here; the per-agent `γ` heterogeneity
and the `V^struct/V^lat` split are rung 4b.

Well-mixed agents (topology is rung 4c). Reuses `suppression` and `variance_series`
from `innovation.py`.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import numpy.typing as npt

from .innovation import suppression, variance_series


def _validate(
    n: int, c0: int, f: float, epsilon: float, b: float, generations: int,
    persistence: int, lam: float, p: int, weight: str, const_h: float | None,
) -> None:
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n}")
    if c0 < 1:
        raise ValueError(f"c0 must be >= 1, got {c0}")
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
    if lam < 0.0:
        raise ValueError(f"lam must be >= 0, got {lam}")
    if p < 1:
        raise ValueError(f"p must be >= 1, got {p}")
    if weight not in ("closure", "indegree"):
        raise ValueError(f"weight must be 'closure' or 'indegree', got {weight!r}")
    if const_h is not None and not 0.0 <= const_h <= 1.0:
        raise ValueError(f"const_h must be in [0, 1] or None, got {const_h}")


def gini(w: npt.NDArray[np.float64]) -> float:
    """Gini coefficient of a non-negative weight vector (0 = uniform, →1 = one holds
    all). Returns 0 for an all-zero or empty vector."""
    if w.shape[0] == 0:
        return 0.0
    x = np.sort(w.astype(float))
    total = x.sum()
    if total <= 0.0:
        return 0.0
    n = x.shape[0]
    cum = np.cumsum(x)
    return float((n + 1 - 2 * cum.sum() / total) / n)


def closure_weights(prereqs: list[list[int]]) -> npt.NDArray[np.float64]:
    """`w_clo(e)` = number of transitive descendants of `e` (elements whose prereq
    closure contains `e`), computed from scratch. Used to verify the incremental
    maintenance in ``run``."""
    e_count = len(prereqs)
    children: list[list[int]] = [[] for _ in range(e_count)]
    for e in range(e_count):
        for pr in prereqs[e]:
            children[pr].append(e)
    reach: list[set[int]] = [set() for _ in range(e_count)]
    w = np.zeros(e_count, dtype=float)
    for e in range(e_count - 1, -1, -1):
        s: set[int] = set()
        for c in children[e]:
            s.add(c)
            s |= reach[c]
        reach[e] = s
        w[e] = float(len(s))
    return w


def reproducible_frontier_multi(
    level: list[int], prereqs: list[list[int]], present: npt.NDArray[np.bool_]
) -> int:
    """`C` on a multi-prereq DAG: the deepest level of any present element whose
    *entire* prerequisite closure is present."""
    e_count = len(level)
    if e_count == 0:
        return 0
    order = np.argsort(np.asarray(level), kind="stable")
    ok = np.zeros(e_count, dtype=bool)
    best = 0
    for e in order:
        good = bool(present[e]) and all(bool(ok[pr]) for pr in prereqs[e])
        ok[e] = good
        if good and level[e] > best:
            best = level[e]
    return best


def run(
    n: int,
    c0: int,
    f: float,
    epsilon: float,
    b: float,
    generations: int,
    seed: int,
    persistence: int = 1,
    lam: float = 0.0,
    p: int = 2,
    weight: str = "closure",
    const_h: float | None = None,
) -> dict[str, Any]:
    """Simulate the multi-prereq attachment-graph model with `κ = λ·H(t)` conformity.

    `H` = Gini of the dependency-closure weight (``weight="closure"``) or of the raw
    in-degree (``weight="indegree"``, the NC-weight control). Returns
    ``{"C", "V", "H", "R_size", ...params}``; `C`, `H`, `R_size` length
    ``generations+1``; `V` (persistence-filtered) carries ``NaN`` in its last
    ``persistence`` entries. Deterministic given ``seed``."""
    _validate(n, c0, f, epsilon, b, generations, persistence, lam, p, weight, const_h)
    rng = np.random.default_rng(seed)

    level: list[int] = [1] * c0
    prereqs: list[list[int]] = [[] for _ in range(c0)]
    ancestors: list[set[int]] = [set() for _ in range(c0)]
    birth: list[int] = [0] * c0
    indeg = np.zeros(c0, dtype=float)      # in-degree (times chosen as a prereq)
    closure = np.zeros(c0, dtype=float)    # transitive-descendant count
    base = np.ones((n, c0), dtype=bool)    # all agents hold the c0 roots

    def h_of() -> float:
        return gini(closure if weight == "closure" else indeg)

    c_traj: list[int] = [reproducible_frontier_multi(level, prereqs, base.any(axis=0))]
    h_traj: list[float] = [h_of()]
    r_hist: list[npt.NDArray[np.bool_]] = [base.any(axis=0).copy()]

    for t in range(1, generations + 1):
        e_count = len(level)
        level_arr = np.asarray(level)

        # ── transmission (generational replacement, coherent over ALL prereqs) ──
        carriers = base.sum(axis=0)
        acquire_p = 1.0 - (1.0 - f) ** carriers
        draws = rng.random((n, e_count)) < acquire_p[None, :]
        new_base = np.zeros((n, e_count), dtype=bool)
        for e in np.argsort(level_arr, kind="stable"):
            prq = prereqs[e]
            if prq:
                new_base[:, e] = draws[:, e] & new_base[:, prq].all(axis=1)
            else:
                new_base[:, e] = draws[:, e]
        base = new_base

        # ── conformity: κ = λ·H (uniform); realized rate ε·g(κ). const_h fixes H
        # at a reference value (the no-N-scaling control) instead of the live H(t). ──
        if lam > 0.0:
            h_val = const_h if const_h is not None else h_of()
            eps_eff = epsilon * suppression(lam * h_val)
        else:
            eps_eff = epsilon

        # ── innovation (simultaneous: prereqs drawn from start-of-generation state) ──
        innovators = np.where(rng.random(n) < eps_eff)[0]
        snap_indeg = indeg
        new_levels: list[int] = []
        new_prereqs: list[list[int]] = []
        new_ancestors: list[set[int]] = []
        new_owners: list[int] = []
        for i in innovators:
            held = np.where(base[i])[0]
            if held.size == 0:
                prq_new: list[int] = []
                lv = 1
            elif rng.random() < b:  # vertical: extend the agent's deepest chain
                deepest = int(held[int(np.argmax(level_arr[held]))])
                prq_new = [deepest]
                lv = level[deepest] + 1
            else:  # lateral: attach to p prereqs ∝ (in-degree+1) — preferential
                k = min(p, held.size)
                wsel = snap_indeg[held] + 1.0
                chosen = rng.choice(held, size=k, replace=False, p=wsel / wsel.sum())
                prq_new = [int(c) for c in chosen]
                lv = 1 + max(level[c] for c in prq_new)
            anc: set[int] = set(prq_new)
            for pr in prq_new:
                anc |= ancestors[pr]
            new_levels.append(lv)
            new_prereqs.append(prq_new)
            new_ancestors.append(anc)
            new_owners.append(int(i))

        add = len(new_levels)
        if add:
            indeg = np.append(indeg, np.zeros(add))
            closure = np.append(closure, np.zeros(add))
            for j in range(add):
                for pr in new_prereqs[j]:
                    indeg[pr] += 1.0
                for a_ in new_ancestors[j]:
                    closure[a_] += 1.0
            level.extend(new_levels)
            birth.extend([t] * add)
            prereqs.extend(new_prereqs)
            ancestors.extend(new_ancestors)
            block = np.zeros((n, add), dtype=bool)
            block[new_owners, np.arange(add)] = True
            base = np.hstack([base, block])

        present = base.any(axis=0)
        c_traj.append(reproducible_frontier_multi(level, prereqs, present))
        h_traj.append(h_of())
        r_hist.append(present.copy())

    e_final = len(level)
    r_grid = np.zeros((generations + 1, e_final), dtype=bool)
    for tt, row in enumerate(r_hist):
        r_grid[tt, : row.shape[0]] = row
    v_traj = variance_series(np.asarray(birth, dtype=np.int64), r_grid, n, persistence)
    r_size = [int(row.sum()) for row in r_hist]

    return {
        "C": c_traj,
        "V": v_traj,
        "H": h_traj,
        "R_size": r_size,
        "prereqs": prereqs,           # final DAG (for verification + rung 4b γ)
        "closure": closure,           # incrementally-maintained closure weights
        "level": level,
        "n": n, "c0": c0, "f": f, "epsilon": epsilon, "b": b,
        "persistence": persistence, "generations": generations,
        "lam": lam, "p": p, "weight": weight,
    }
