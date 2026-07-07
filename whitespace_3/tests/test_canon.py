"""Rung 4a — the endogenous canon: `κ = λ·H(t)` driven by real canonical
concentration `H` on a multi-prerequisite attachment graph.

TDD anchors (plan: docs/phases/phase-1-rung4a-endogenous-canon-plan.md). Pre-registered
signs; thresholds calibrated (canon smoke + CI) to be non-flaky. The endogenous-`H`
crossover is real but **weak** (H compressed near 1), so the crossover / control tests
run at `λ=3` where the effect is CI-robust — and those runs are *cheap* (heavy
suppression → few elements). The `λ=0` placebo/`H`-rise runs are the costly ones, so
they stay at modest `N`.

  * T1 determinism / T2 κ=0 placebo (no crossover) / T3 endogenous `H` rises +
    metric correctness / T4 reproducible-frontier + closure correctness.
  * T5 THE crossover on real `H` (headline) / T6 reconciliation `C↑ / V↓`.
  * T7 NC-const (fixed `H` ⇒ no crossover) + spec-robustness across the weight.
  * T8 input validation.
"""

from __future__ import annotations

import numpy as np
import pytest

from whitespace3.canon import (
    closure_weights,
    gini,
    reproducible_frontier_multi,
    run,
)
from whitespace3.conformity import crossover_slope

MODEL = dict(c0=3, f=0.5, epsilon=0.4, b=0.4, generations=32, persistence=2, p=2)
NS_CHEAP = [5, 20, 80]     # λ=3 is heavily suppressed → few elements → fast
NS_PLACEBO = [5, 15, 40]   # λ=0 accumulates elements → keep N modest
BURN = 18


# ── T1 / T2 — engine correctness ──────────────────────────────────────────────

def test_determinism() -> None:
    kw = dict(**MODEL, lam=3.0)
    a = run(20, seed=2, **kw)
    b = run(20, seed=2, **kw)
    assert a["C"] == b["C"] and a["H"] == b["H"] and a["R_size"] == b["R_size"]
    assert np.array_equal(np.array(a["V"]), np.array(b["V"]), equal_nan=True)


def test_kappa0_placebo() -> None:
    """NC0: κ=0 ⇒ per-capita V* flat-or-rising in N (no crossover) on the new substrate."""
    ci = crossover_slope(NS_PLACEBO, 0.0, seeds=range(6), burn_in=BURN, run_fn=run, **MODEL)
    assert ci["hi"] >= 0.0, f"κ=0 placebo should not decline: {ci}"


# ── T3 / T4 — endogenous H + metric correctness ───────────────────────────────

def test_H_rises_with_N() -> None:
    """H1: closure-weight H* rises with N (CI strictly positive)."""
    ci = crossover_slope(NS_PLACEBO, 0.0, seeds=range(6), burn_in=BURN, metric="H",
                         run_fn=run, **MODEL)
    assert ci["lo"] > 0.0, f"endogenous H should rise with N: {ci}"


def test_gini() -> None:
    assert gini(np.array([1.0, 1.0, 1.0, 1.0])) == pytest.approx(0.0)   # uniform
    assert gini(np.zeros(4)) == 0.0                                      # all-zero
    assert gini(np.array([])) == 0.0                                     # empty
    assert gini(np.array([0.0, 0.0, 0.0, 9.0])) > 0.7                    # one holds all


def test_closure_weights_scratch() -> None:
    # 0,1 roots; 2->0; 3->0,1; 4->2 (so 4 transitively depends on 0 too).
    prereqs = [[], [], [0], [0, 1], [2]]
    w = closure_weights(prereqs)
    # descendants: 0:{2,3,4}=3  1:{3}=1  2:{4}=1  3:{}=0  4:{}=0
    assert list(w) == [3.0, 1.0, 1.0, 0.0, 0.0]


def test_closure_incremental_matches_scratch() -> None:
    """The closure maintained incrementally in run() equals from-scratch on the DAG."""
    r = run(15, **MODEL, seed=1, lam=0.0)
    assert np.array_equal(r["closure"], closure_weights(r["prereqs"]))


def test_reproducible_frontier_multi() -> None:
    level = [1, 1, 2, 3]
    prereqs = [[], [], [0, 1], [2]]
    assert reproducible_frontier_multi(level, prereqs, np.array([True, True, True, True])) == 3
    # drop element 1 (a prereq of 2): 2's closure incomplete ⇒ level-3 unreachable;
    # deepest present element with a full chain is a level-1 root.
    assert reproducible_frontier_multi(level, prereqs, np.array([True, False, True, True])) == 1
    assert reproducible_frontier_multi(level, prereqs, np.array([False] * 4)) == 0


# ── T5 — THE crossover on real H (headline) ───────────────────────────────────

def test_crossover_on_real_H() -> None:
    placebo = crossover_slope(NS_PLACEBO, 0.0, seeds=range(6), burn_in=BURN, run_fn=run, **MODEL)
    cross = crossover_slope(NS_CHEAP, 3.0, seeds=range(10), burn_in=BURN, run_fn=run, **MODEL)
    assert placebo["hi"] >= 0.0, f"κ=0 should not decline: {placebo}"
    assert cross["hi"] < 0.0, f"κ=λ·H should make V* decline in N: {cross}"


# ── T6 — reconciliation: C*↑ while V*↓ ────────────────────────────────────────

def test_reconciliation() -> None:
    c = crossover_slope(NS_CHEAP, 3.0, seeds=range(8), burn_in=BURN, metric="C",
                        run_fn=run, **MODEL)
    v = crossover_slope(NS_CHEAP, 3.0, seeds=range(8), burn_in=BURN, metric="V",
                        run_fn=run, **MODEL)
    assert c["lo"] > 0.0, f"C* should rise with N (Henrich): {c}"
    assert v["hi"] < 0.0, f"V* should fall with N (WWE): {v}"


# ── T7 — NC-const (fixed H) + spec-robustness across the weight ────────────────

def test_control_const_h() -> None:
    """Fixed H (no N-scaling) ⇒ no crossover — it is H *rising with N* that bites."""
    ci = crossover_slope(NS_CHEAP, 3.0, seeds=range(8), burn_in=BURN, const_h=0.88,
                         run_fn=run, **MODEL)
    assert ci["hi"] >= 0.0, f"fixed-H control should not produce a crossover: {ci}"


def test_spec_robustness_weight() -> None:
    for weight in ("closure", "indegree"):
        ci = crossover_slope(NS_CHEAP, 3.0, seeds=range(8), burn_in=BURN, weight=weight,
                             run_fn=run, **MODEL)
        assert ci["point"] < 0.0, f"crossover sign not robust under weight={weight}: {ci}"


# ── T8 — input validation ─────────────────────────────────────────────────────

def test_input_validation() -> None:
    with pytest.raises(ValueError):
        run(0, 3, 0.5, 0.3, 0.5, 10, 0)
    with pytest.raises(ValueError):
        run(5, 0, 0.5, 0.3, 0.5, 10, 0)                 # c0 < 1
    with pytest.raises(ValueError):
        run(5, 3, 0.5, 0.3, 0.5, 10, 0, lam=-1.0)
    with pytest.raises(ValueError):
        run(5, 3, 0.5, 0.3, 0.5, 10, 0, p=0)
    with pytest.raises(ValueError):
        run(5, 3, 0.5, 0.3, 0.5, 10, 0, weight="bad")
    with pytest.raises(ValueError):
        run(5, 3, 0.5, 0.3, 0.5, 10, 0, const_h=1.5)
