"""Rung 4b — the channel refinement: `κ` targets the *structural* channel.

rung 4a suppressed innovation *uniformly* (`κ=λ·H`), giving a weak total-`V` crossover.
The primer (§4.3) says conformity acts on the **attachment channel**: it throttles
**structurally deviant** (low canon-alignment `γ`) novelty while sparing canon-aligned
and lateral/content work. Here each innovation's success carries the factor
`g(κ_eff)`, `κ_eff = λ·H·(1−γ)` — aligned (`γ=1`) is free, deviant (`γ=0`) feels the
full `g(λ·H)`.

This separates the **declining** structural channel from the **thriving** breadth
channel, reproducing WS2's fingerprint: collective breadth `W↑` while per-capita
*structural* novelty `V^struct↓` (Core Claim 6). It also reframes the WWE decline —
the proper measure is `V^struct`, not total `V` (which can rise as breadth thrives).

Substrate = rung 4a's multi-prereq attachment graph (reuses `canon`'s
`closure_weights`, `gini`, `reproducible_frontier_multi`). ``mode`` selects the
conformity form: ``off`` (`κ=0`), ``uniform`` (`κ=λ·H`, the NC-uniform control), or
``targeted`` (`κ=λ·H·(1−γ)`). Well-mixed by default; a fixed finite-degree ER/WS/BA
interaction graph is the ``topology`` option (rung 4e, the `cc:robust` topology pass).
"""

from __future__ import annotations

from typing import Any

import networkx as nx
import numpy as np
import numpy.typing as npt
import scipy.sparse as sp

from .canon import gini, reproducible_frontier_multi
from .innovation import suppression

_TOPOLOGIES = ("well_mixed", "er", "ws", "ba")


def _build_adjacency(topology: str, n: int, mean_degree: int, graph_seed: int) -> Any:
    """Fixed interaction graph as a CSR adjacency with self-loops; ``None`` for well-mixed
    (rung 4e). Self-loops make an agent count its own prior holding, matching well-mixed
    semantics (``base.sum`` includes self). ``er``/``ws``/``ba`` = Erdős–Rényi /
    Watts–Strogatz / Barabási–Albert at the target mean degree."""
    if topology == "well_mixed":
        return None
    if topology == "er":
        g = nx.erdos_renyi_graph(n, min(1.0, mean_degree / (n - 1)), seed=graph_seed)
    elif topology == "ws":
        k = mean_degree + (mean_degree % 2)                 # watts_strogatz needs even k
        g = nx.watts_strogatz_graph(n, max(2, k), 0.1, seed=graph_seed)
    else:                                                   # ba: each node adds m edges
        g = nx.barabasi_albert_graph(n, max(1, mean_degree // 2), seed=graph_seed)
    a = nx.to_scipy_sparse_array(g, nodelist=range(n), dtype=float, format="csr")
    return (a + sp.eye(n, format="csr")).tocsr()


def _validate(
    n: int, c0: int, f: float, epsilon: float, b: float, generations: int,
    persistence: int, lam: float, p: int, alpha: float, gamma_thresh: float,
    mode: str, g_map: str, topology: str, mean_degree: int, isolated_frac: float,
) -> None:
    if not 0.0 <= isolated_frac < 1.0:
        raise ValueError(f"isolated_frac must be in [0, 1), got {isolated_frac}")
    if topology not in _TOPOLOGIES:
        raise ValueError(f"topology must be one of {_TOPOLOGIES}, got {topology!r}")
    if topology != "well_mixed" and not 2 <= mean_degree <= n - 1:
        raise ValueError(f"mean_degree must be in [2, n-1] for a graph, got {mean_degree}")
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
    if not 0.0 < alpha <= 1.0:
        raise ValueError(f"alpha must be in (0, 1], got {alpha}")
    if not 0.0 <= gamma_thresh <= 1.0:
        raise ValueError(f"gamma_thresh must be in [0, 1], got {gamma_thresh}")
    if mode not in ("off", "uniform", "targeted"):
        raise ValueError(f"mode must be off/uniform/targeted, got {mode!r}")
    if g_map not in ("exp", "hyper"):
        raise ValueError(f"g_map must be 'exp' or 'hyper', got {g_map!r}")


def variance_split(
    birth: npt.NDArray[np.int64],
    struct: npt.NDArray[np.bool_],
    r_grid: npt.NDArray[np.bool_],
    n: int,
    k: int,
) -> tuple[list[float], list[float], list[float]]:
    """Per-capita persisting novelty split by birth `γ`-class: returns
    ``(V^struct, V^lat, V^total)`` series. ``NaN`` in the last ``k`` entries."""
    generations = int(r_grid.shape[0]) - 1
    vs: list[float] = []
    vl: list[float] = []
    vt: list[float] = []
    for t in range(generations + 1):
        if t + k > generations:
            vs.append(float("nan"))
            vl.append(float("nan"))
            vt.append(float("nan"))
            continue
        born = np.where(birth == t)[0]
        if born.size == 0:
            vs.append(0.0)
            vl.append(0.0)
            vt.append(0.0)
            continue
        surv = born[r_grid[t : t + k + 1, born].all(axis=0)]
        s = struct[surv]
        vs.append(float(int(s.sum())) / n)
        vl.append(float(int((~s).sum())) / n)
        vt.append(float(int(surv.size)) / n)
    return vs, vl, vt


def variance_split_group(
    birth: npt.NDArray[np.int64],
    struct: npt.NDArray[np.bool_],
    owner_iso: npt.NDArray[np.bool_],
    r_grid: npt.NDArray[np.bool_],
    n_iso: int,
    n_conf: int,
    k: int,
) -> tuple[list[float], list[float]]:
    """Per-capita persisting *structural* novelty split by owner subgroup (selective
    isolation, rung 5a): ``(V^struct_isolated, V^struct_conformist)`` — surviving structural
    innovations owned by each subgroup, divided by that subgroup's size. ``NaN`` last ``k``."""
    generations = int(r_grid.shape[0]) - 1
    vi: list[float] = []
    vc: list[float] = []
    for t in range(generations + 1):
        if t + k > generations:
            vi.append(float("nan"))
            vc.append(float("nan"))
            continue
        born = np.where(birth == t)[0]
        if born.size == 0:
            vi.append(0.0)
            vc.append(0.0)
            continue
        surv = born[r_grid[t : t + k + 1, born].all(axis=0)]
        s = struct[surv]
        iso = owner_iso[surv]
        vi.append(float(int((s & iso).sum())) / max(n_iso, 1))
        vc.append(float(int((s & ~iso).sum())) / max(n_conf, 1))
    return vi, vc


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
    alpha: float = 0.15,
    gamma_thresh: float = 0.5,
    mode: str = "targeted",
    g_map: str = "exp",
    topology: str = "well_mixed",
    mean_degree: int = 8,
    graph_seed: int = 0,
    isolated_frac: float = 0.0,
) -> dict[str, Any]:
    """Multi-prereq graph with **targeted** conformity. Innovation fires at base rate
    `ε`; each event succeeds with prob `g(κ_eff)`, `κ_eff = λ·H·(1−γ)` (``targeted``),
    `λ·H` (``uniform``), or `0` (``off``). An element is *structural* iff its
    canon-alignment `γ < gamma_thresh`.

    ``topology`` (rung 4e) sets the interaction graph over which transmission spreads:
    ``well_mixed`` (default, global carriers — byte-identical to the pre-4e model) or a
    fixed finite-degree ``er``/``ws``/``ba`` graph (neighbour carriers, mean degree
    ``mean_degree``, built from ``graph_seed``). The κ-signature (`V^struct↓`, `W↑`) is
    tested for invariance across topologies (Core Claim `cc:robust`).

    ``isolated_frac`` (rung 5a) shields the first ``⌈isolated_frac·n⌉`` agents from κ
    (`κ_eff=0`) — the primer's *selective isolation*: the shielded subgroup keeps innovating
    freely (high `V^struct`) while the whole population's redundancy preserves `C`, a concrete
    Pareto intervention. ``Vstruct_iso``/``Vstruct_conf`` split per-capita structural novelty
    by subgroup.

    Returns ``{"C","V","Vstruct","Vlat","Vstruct_iso","Vstruct_conf","H","W","R_size", ...}``
    — `W` is collective breadth (repertoire size). Deterministic given ``seed`` (and
    ``graph_seed``)."""
    _validate(n, c0, f, epsilon, b, generations, persistence, lam, p, alpha,
              gamma_thresh, mode, g_map, topology, mean_degree, isolated_frac)
    rng = np.random.default_rng(seed)
    adjacency = _build_adjacency(topology, n, mean_degree, graph_seed)
    n_iso = int(np.ceil(isolated_frac * n))
    isolated_mask = np.arange(n) < n_iso              # first n_iso agents shielded from κ (5a)

    level: list[int] = [1] * c0
    prereqs: list[list[int]] = [[] for _ in range(c0)]
    ancestors: list[set[int]] = [set() for _ in range(c0)]
    birth: list[int] = [0] * c0
    struct: list[bool] = [False] * c0
    owner_iso: list[bool] = [False] * c0              # was the innovating agent isolated?
    indeg = np.zeros(c0, dtype=float)
    closure = np.zeros(c0, dtype=float)
    base = np.ones((n, c0), dtype=bool)

    c_traj: list[int] = [reproducible_frontier_multi(level, prereqs, base.any(axis=0))]
    h_traj: list[float] = [gini(closure)]
    r_hist: list[npt.NDArray[np.bool_]] = [base.any(axis=0).copy()]

    for t in range(1, generations + 1):
        e_count = len(level)
        level_arr = np.asarray(level)

        # ── transmission (coherent over all prereqs; neighbour carriers under a topology) ──
        if adjacency is None:
            carriers = base.sum(axis=0)                              # well-mixed (global)
            acquire_p = 1.0 - (1.0 - f) ** carriers
            draws = rng.random((n, e_count)) < acquire_p[None, :]
        else:
            nb: npt.NDArray[np.float64] = np.asarray(
                adjacency @ base.astype(np.float64), dtype=np.float64)   # (n, e) neighbours
            draws = rng.random((n, e_count)) < (1.0 - (1.0 - f) ** nb)
        new_base = np.zeros((n, e_count), dtype=bool)
        for e in np.argsort(level_arr, kind="stable"):
            prq = prereqs[e]
            if prq:
                new_base[:, e] = draws[:, e] & new_base[:, prq].all(axis=1)
            else:
                new_base[:, e] = draws[:, e]
        base = new_base

        h_now = gini(closure)
        # canon K_alpha = top-⌈α·E⌉ elements by closure weight
        n_canon = max(1, int(alpha * e_count))
        canon_mask = np.zeros(e_count, dtype=bool)
        canon_mask[np.argsort(closure)[::-1][:n_canon]] = True

        # ── innovation with per-event, γ-targeted suppression ──
        innovators = np.where(rng.random(n) < epsilon)[0]
        new_levels: list[int] = []
        new_prereqs: list[list[int]] = []
        new_ancestors: list[set[int]] = []
        new_owners: list[int] = []
        new_struct: list[bool] = []
        new_iso: list[bool] = []
        for i in innovators:
            held = np.where(base[i])[0]
            if held.size == 0:
                prq_new: list[int] = []
                lv = 1
            elif rng.random() < b:  # vertical: extend the agent's deepest chain
                deepest = int(held[int(np.argmax(level_arr[held]))])
                prq_new = [deepest]
                lv = level[deepest] + 1
            else:  # lateral: attach to p prereqs ∝ (in-degree+1)
                k_sel = min(p, held.size)
                wsel = indeg[held] + 1.0
                chosen = rng.choice(held, size=k_sel, replace=False, p=wsel / wsel.sum())
                prq_new = [int(c) for c in chosen]
                lv = 1 + max(level[c] for c in prq_new)
            gamma = (float(np.mean([canon_mask[c] for c in prq_new])) if prq_new else 0.0)
            if isolated_mask[i] or mode == "off" or lam == 0.0:   # isolated ⇒ shielded from κ
                kappa_eff = 0.0
            elif mode == "uniform":
                kappa_eff = lam * h_now
            else:  # targeted
                kappa_eff = lam * h_now * (1.0 - gamma)
            if rng.random() >= suppression(kappa_eff, g_map):  # innovation suppressed
                continue
            anc: set[int] = set(prq_new)
            for pr in prq_new:
                anc |= ancestors[pr]
            new_levels.append(lv)
            new_prereqs.append(prq_new)
            new_ancestors.append(anc)
            new_owners.append(int(i))
            new_struct.append(gamma < gamma_thresh)
            new_iso.append(bool(isolated_mask[i]))

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
            struct.extend(new_struct)
            owner_iso.extend(new_iso)
            block = np.zeros((n, add), dtype=bool)
            block[new_owners, np.arange(add)] = True
            base = np.hstack([base, block])

        present = base.any(axis=0)
        c_traj.append(reproducible_frontier_multi(level, prereqs, present))
        h_traj.append(gini(closure))
        r_hist.append(present.copy())

    e_final = len(level)
    r_grid = np.zeros((generations + 1, e_final), dtype=bool)
    for tt, row in enumerate(r_hist):
        r_grid[tt, : row.shape[0]] = row
    birth_arr = np.asarray(birth, dtype=np.int64)
    struct_arr = np.asarray(struct, dtype=bool)
    v_struct, v_lat, v_total = variance_split(birth_arr, struct_arr, r_grid, n, persistence)
    v_iso, v_conf = variance_split_group(
        birth_arr, struct_arr, np.asarray(owner_iso, dtype=bool),
        r_grid, n_iso, n - n_iso, persistence,
    )
    r_size = [int(row.sum()) for row in r_hist]

    return {
        "C": c_traj,
        "V": v_total,
        "Vstruct": v_struct,
        "Vlat": v_lat,
        "Vstruct_iso": v_iso,       # per-capita structural V of the isolated subgroup (5a)
        "Vstruct_conf": v_conf,     # per-capita structural V of the conformist majority
        "H": h_traj,
        "W": r_size,          # collective breadth (repertoire size)
        "R_size": r_size,
        "n": n, "c0": c0, "f": f, "epsilon": epsilon, "b": b,
        "persistence": persistence, "generations": generations,
        "lam": lam, "p": p, "alpha": alpha, "gamma_thresh": gamma_thresh,
        "mode": mode, "g_map": g_map,
        "topology": topology, "mean_degree": mean_degree, "graph_seed": graph_seed,
        "isolated_frac": isolated_frac,
    }
