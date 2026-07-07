"""Rung 4c — bounded role models: sub-criticality and the Strimling Level-3 anchor.

TDD anchors (plan: docs/phases/phase-1-rung4c-bounded-roles-plan.md). Level 3:
  * Strimling 2009 `λ_f = U/(1−β)` (via the open Lehmann–Aoki–Feldman 2011) — the
    specific number 0.2 at ε=0.1, f=0.5, n=1, N-independent.
  * Enquist et al. 2010 threshold `p·n>1` (my `f·n=1`) — sub-critical finite /
    super-critical runaway.
"""

from __future__ import annotations

import numpy as np
import pytest

from whitespace3.roles import run, steady_state, strimling_lambda_f


def _lf(pop: int, n_models: int, f: float, eps: float, seeds: range = range(6),
        g: int = 60, bi: int = 30) -> float:
    return float(np.mean(steady_state(pop, n_models, f, eps, g, seeds, bi, "per_agent")))


def test_determinism() -> None:
    a = run(50, 3, 0.2, 0.2, 40, seed=1)
    b = run(50, 3, 0.2, 0.2, 40, seed=1)
    assert a["per_agent"] == b["per_agent"] and a["repertoire"] == b["repertoire"]


def test_strimling_level3_number() -> None:
    """Strimling/LAF λ_f = U/(1−β) = 0.2 at U=0.1, β=0.5, n=1 — matched, N-independent."""
    for pop in (50, 150, 400):
        val = _lf(pop, 1, 0.5, 0.1)
        assert abs(val - 0.2) < 0.035, f"N={pop}: λ_f={val} != 0.2"


def test_closed_form() -> None:
    """λ_f = ε/(1−f·n) across n and f, well sub-critical (f·n ≤ 0.6)."""
    for n_models, f in [(1, 0.5), (2, 0.3), (3, 0.2), (1, 0.4)]:
        val = _lf(150, n_models, f, 0.1)
        pred = strimling_lambda_f(0.1, f, n_models)
        assert abs(val - pred) / pred < 0.12, f"n={n_models}, f={f}: {val} vs {pred}"


def test_N_independence() -> None:
    small, large = _lf(50, 2, 0.3, 0.1), _lf(400, 2, 0.3, 0.1)
    assert large / small < 1.4, f"λ_f not N-independent: {small} -> {large}"


def test_enquist_threshold() -> None:
    """Sub-critical f·n<1 ⇒ bounded/N-independent; super-critical f·n>1 ⇒ runaway."""
    sub = [_lf(pop, 2, 0.3, 0.1) for pop in (50, 200)]        # f·n = 0.6
    sup = [_lf(pop, 2, 0.7, 0.1) for pop in (50, 200)]        # f·n = 1.4
    assert sub[1] / sub[0] < 1.5, f"sub-critical should be bounded: {sub}"
    assert sup[1] / sup[0] > 2.5, f"super-critical should run away: {sup}"


def test_population_grows_with_N() -> None:
    """Individual saturates but the population repertoire grows ~linearly in N."""
    lp = [float(np.mean(steady_state(pop, 2, 0.3, 0.1, 60, range(4), 30, "repertoire")))
          for pop in (50, 150, 400)]
    assert lp[-1] > 2.0 * lp[0], f"population repertoire should grow with N: {lp}"


def test_strimling_lambda_f_formula() -> None:
    assert strimling_lambda_f(0.1, 0.5, 1) == pytest.approx(0.2)
    assert strimling_lambda_f(0.1, 0.5, 2) == float("inf")   # f·n = 1 (critical)
    assert strimling_lambda_f(0.1, 0.6, 3) == float("inf")   # super-critical


def test_input_validation() -> None:
    with pytest.raises(ValueError):
        run(1, 1, 0.5, 0.1, 10, 0)              # n < 2
    with pytest.raises(ValueError):
        run(10, 0, 0.5, 0.1, 10, 0)             # n_models < 1
    with pytest.raises(ValueError):
        run(10, 10, 0.5, 0.1, 10, 0)            # n_models > n-1
    with pytest.raises(ValueError):
        run(10, 2, 1.5, 0.1, 10, 0)             # f out of range
    with pytest.raises(ValueError):
        run(10, 2, 0.5, -0.1, 10, 0)            # epsilon out of range
    with pytest.raises(ValueError):
        run(10, 2, 0.5, 0.1, 0, 0)              # generations < 1


@pytest.mark.slow
def test_sensitivity_closed_form() -> None:
    """Closed form + N-independence hold across ε, f, n in the sub-critical regime."""
    for n_models, f, eps in [(1, 0.4, 0.15), (2, 0.35, 0.1), (3, 0.15, 0.2), (2, 0.25, 0.3)]:
        pred = strimling_lambda_f(eps, f, n_models)
        small = _lf(60, n_models, f, eps)
        large = _lf(300, n_models, f, eps)
        assert abs(large - pred) / pred < 0.15, f"n={n_models},f={f},eps={eps}: {large} vs {pred}"
        assert large / small < 1.4, f"not N-independent: {small} -> {large}"
