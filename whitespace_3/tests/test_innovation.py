"""Rung 2b — innovation → per-capita ``V`` (conformity OFF, ``κ=0``).

TDD anchors (plan: docs/phases/phase-1-rung2b-innovation-v-plan.md):

  * **T1 — un-bundling invariant.** With innovation off (``ε=0``) the model reduces
    to rung 2a: ``C`` non-increasing, capped at ``c0``; behavioral equivalence to
    ``concept_base``; qualitative Henrich (maintenance large-N, Tasmania small-N).
    (The *quantitative* Henrich number ``N*≈616`` stays at rung 1 — the concept-base
    substrate has no Gumbel ``α/β``.)
  * **T2 — metric correctness** on hand-built states (``C`` reproducible frontier;
    the ``k``-generation persistence filter of ``V``).
  * **T3 — determinism.**
  * **T4 — the ``κ=0`` placebo (H2, headline gate):** per-capita ``V*`` is
    flat-or-rising in ``N`` (slope of ``V*`` on ``log N``, seed-bootstrap CI, not
    two-point). The WWE decline must be ``κ``'s doing (rung 3), never the substrate's.
  * **T5 — innovation restores ``C``-growth (H1′):** with ``ε>0``, ``C`` exceeds
    ``c0``; ``C*`` non-decreasing in ``f`` and ``N``.
  * **T6 — input validation.**
"""

from __future__ import annotations

import numpy as np
import pytest

from whitespace3.concept_base import retained_complexity
from whitespace3.innovation import (
    reproducible_frontier,
    run,
    steady_state_C,
    steady_state_V,
    variance_series,
)

C0, F = 10, 0.3


# ── T1 — un-bundling invariant (ε=0 → rung 2a) ────────────────────────────────

def test_eps0_no_growth_capped_at_c0() -> None:
    """ε=0: transmission alone → C non-increasing and never exceeds c0."""
    for n in (3, 20, 200):
        c = run(n=n, c0=C0, f=F, epsilon=0.0, b=0.5, generations=100, seed=1)["C"]
        assert max(c) == C0
        assert all(c[t + 1] <= c[t] for t in range(len(c) - 1))


def test_eps0_matches_rung2a() -> None:
    """ε=0: behaviorally equivalent to rung 2a — mean final C matches within noise
    (same per-generation transition; only the RNG layout differs)."""
    for n in (5, 50):
        ours = float(np.mean([
            run(n=n, c0=C0, f=F, epsilon=0.0, b=0.5, generations=100, seed=s)["C"][-1]
            for s in range(20)
        ]))
        theirs = retained_complexity(n, C0, F, 100, range(20))
        assert abs(ours - theirs) < 1.0


def test_eps0_qualitative_henrich() -> None:
    """ε=0: maintenance for large N, Tasmania loss for small N."""
    assert run(n=200, c0=C0, f=F, epsilon=0.0, b=0.5, generations=100, seed=0)["C"][-1] == C0
    assert run(n=3, c0=C0, f=F, epsilon=0.0, b=0.5, generations=100, seed=0)["C"][-1] < C0


# ── T2 — metric correctness on hand-built states ──────────────────────────────

def test_reproducible_frontier() -> None:
    # chain 1<-2<-3 (elems 0,1,2) plus a level-2 sibling (elem 3) whose parent is elem 0.
    level = np.array([1, 2, 3, 2])
    parent = np.array([-1, 0, 1, 0])
    assert reproducible_frontier(level, parent, np.array([True, True, True, True])) == 3
    # elem 2 (level 3) present but its chain is broken (elem 1 absent); the deepest
    # element with a fully-present chain is elem 3 (level 2, parent elem 0 present).
    assert reproducible_frontier(level, parent, np.array([True, False, True, True])) == 2
    # nothing present → frontier 0
    assert reproducible_frontier(level, parent, np.array([False, False, False, False])) == 0


def test_variance_series_persistence_filter() -> None:
    # two elements born at t=1: A survives the k=2 window, B dies immediately.
    birth = np.array([1, 1])
    R = np.array([
        [False, False],  # t0
        [True, True],    # t1  (both first appear)
        [True, False],   # t2
        [True, False],   # t3
        [True, False],   # t4
    ])
    v = variance_series(birth, R, n=10, k=2)          # gens = 4
    assert v[0] == 0.0                                  # nothing born at t0
    assert v[1] == pytest.approx(0.1)                   # only A survives [t1,t3] → 1/10
    assert np.isnan(v[3]) and np.isnan(v[4])            # t > gens-k = 2 → not yet observable


# ── T3 — determinism ──────────────────────────────────────────────────────────

def test_determinism() -> None:
    a = run(20, C0, F, 0.2, 0.5, 40, seed=7, persistence=2)
    b = run(20, C0, F, 0.2, 0.5, 40, seed=7, persistence=2)
    assert a["C"] == b["C"]
    assert a["R_size"] == b["R_size"]
    assert np.array_equal(np.array(a["V"]), np.array(b["V"]), equal_nan=True)


# ── T4 — the κ=0 placebo (H2, the headline gate) ──────────────────────────────

def _bootstrap_logN_slope(
    ns: list[int], per_seed: dict[int, np.ndarray], n_boot: int = 400, seed: int = 0
) -> dict[str, float]:
    """Slope of mean V* on log N with a seed-resampling bootstrap CI."""
    rng = np.random.default_rng(seed)
    log_n = np.log(ns)
    slopes = np.empty(n_boot)
    for j in range(n_boot):
        means = [float(np.mean(rng.choice(per_seed[nn], size=per_seed[nn].size, replace=True)))
                 for nn in ns]
        slopes[j] = np.polyfit(log_n, means, 1)[0]
    point = float(np.polyfit(log_n, [float(np.mean(per_seed[nn])) for nn in ns], 1)[0])
    return {"lo": float(np.percentile(slopes, 2.5)),
            "hi": float(np.percentile(slopes, 97.5)),
            "point": point}


def test_placebo_V_not_declining_in_N() -> None:
    """H2: at κ=0, per-capita V* is flat-or-rising in N — the slope CI must not lie
    entirely below zero (falsifier would be a significant decline from the substrate)."""
    ns = [8, 32, 128]
    seeds = range(8)
    kw = dict(c0=C0, f=0.3, epsilon=0.2, b=0.5, generations=45, persistence=2)
    per_seed = {nn: steady_state_V(nn, seeds=seeds, burn_in=25, **kw) for nn in ns}
    ci = _bootstrap_logN_slope(ns, per_seed)
    assert ci["hi"] >= 0.0, f"V* slope CI entirely below 0 (decline): {ci}"


# ── T5 — innovation restores C-growth (H1′) ───────────────────────────────────

def test_innovation_restores_C_growth() -> None:
    """With ε>0, vertical innovation extends depth beyond c0 (rung 2a could not)."""
    c = run(n=100, c0=C0, f=0.9, epsilon=0.3, b=0.8, generations=60, seed=0)["C"]
    assert max(c) > C0


def test_Cstar_nondecreasing_in_f() -> None:
    # Fidelity binds only when innovation is WEAK (preservation-limited). With strong
    # vertical innovation the frontier ratchets ballistically and C* is ~f-independent
    # (well-mixing → unbounded redundancy → no saturation; see rung-2b retro).
    cs = [float(np.mean(steady_state_C(
        30, c0=C0, f=f, epsilon=0.05, b=0.5, generations=80, seeds=range(8), burn_in=40)))
        for f in (0.2, 0.45, 0.9)]
    assert cs[0] < cs[-1]
    assert all(cs[i] <= cs[i + 1] + 1.5 for i in range(len(cs) - 1))


def test_Cstar_nondecreasing_in_N() -> None:
    cs = [float(np.mean(steady_state_C(
        nn, c0=C0, f=0.8, epsilon=0.3, b=0.8, generations=50, seeds=range(5), burn_in=25)))
        for nn in (10, 50, 200)]
    assert cs[-1] >= cs[0] - 0.5           # larger N at least as deep (within noise)


# ── T6 — input validation ─────────────────────────────────────────────────────

def test_input_validation() -> None:
    with pytest.raises(ValueError):
        run(0, C0, F, 0.1, 0.5, 10, 0)             # n < 1
    with pytest.raises(ValueError):
        run(5, -1, F, 0.1, 0.5, 10, 0)             # c0 < 0
    with pytest.raises(ValueError):
        run(5, C0, 1.5, 0.1, 0.5, 10, 0)           # f out of range
    with pytest.raises(ValueError):
        run(5, C0, F, -0.1, 0.5, 10, 0)            # epsilon < 0
    with pytest.raises(ValueError):
        run(5, C0, F, 1.1, 0.5, 10, 0)             # epsilon > 1
    with pytest.raises(ValueError):
        run(5, C0, F, 0.1, 1.5, 10, 0)             # b > 1
    with pytest.raises(ValueError):
        run(5, C0, F, 0.1, 0.5, 0, 0)              # generations < 1
    with pytest.raises(ValueError):
        run(5, C0, F, 0.1, 0.5, 10, 0, persistence=0)  # k < 1
