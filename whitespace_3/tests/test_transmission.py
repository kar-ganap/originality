"""Phase 0 rung 1 — the transmission harness reproduces the Henrich 2004 /
Powell-Shennan-Thomas 2009 critical-population-size result for cumulative culture.

The known-answer anchor (trust = independent agreement with a published result):
with each of ``n`` learners imitating the current frontier skill with a Gumbel
inference error of location ``mu`` (a mean loss when ``mu<0``) and scale
``alpha``, the frontier ``z_max`` drifts per generation by exactly
``mu + alpha*(ln n + gamma_E)``.  Hence there is a critical population size
``N* = exp(-mu/alpha - gamma_E)`` above which cumulative complexity accumulates
and below which it is lost (the Tasmania effect).
"""

from __future__ import annotations

import math

import pytest

from whitespace3.transmission import (
    EULER_GAMMA,
    critical_population_size,
    measure_drift,
    per_gen_drift,
    run_transmission,
)

MU, ALPHA = -3.0, 1.0          # N* = exp(3 - gamma_E) ~= 11.28


def test_per_gen_drift_formula() -> None:
    assert per_gen_drift(1, MU, ALPHA) == pytest.approx(MU + ALPHA * EULER_GAMMA)
    assert per_gen_drift(10, MU, ALPHA) == pytest.approx(
        MU + ALPHA * (math.log(10) + EULER_GAMMA))


def test_critical_population_size_roundtrip() -> None:
    nstar = critical_population_size(MU, ALPHA)
    assert nstar == pytest.approx(math.exp(-MU / ALPHA - EULER_GAMMA))
    assert nstar == pytest.approx(11.28, abs=0.1)
    # drift evaluated at N* is zero by construction
    assert per_gen_drift(nstar, MU, ALPHA) == pytest.approx(0.0, abs=1e-9)


def test_accumulation_large_N() -> None:
    """N=50 >> N*: the frontier accumulates over generations."""
    r = run_transmission(50, MU, ALPHA, generations=200, seed=0)
    assert r["z_max"][-1] > r["z_max"][0]


def test_loss_small_N_is_tasmania() -> None:
    """N=4 < N*: the frontier is LOST over generations (net negative drift)."""
    r = run_transmission(4, MU, ALPHA, generations=200, seed=0)
    assert r["z_max"][-1] < r["z_max"][0]
    assert measure_drift(4, MU, ALPHA, 200, range(20)) < 0


def test_drift_monotone_in_N() -> None:
    """More minds accumulate complexity faster (drift increasing in N)."""
    drifts = [measure_drift(n, MU, ALPHA, 200, range(15))
              for n in (2, 4, 11, 50, 200)]
    assert all(drifts[i] < drifts[i + 1] for i in range(len(drifts) - 1))


def test_drift_matches_analytic_across_N() -> None:
    """The known-answer anchor: empirical per-gen drift matches
    mu + alpha*(ln N + gamma_E) across N (seed-averaged)."""
    for n in (2, 8, 30, 100):
        emp = measure_drift(n, MU, ALPHA, 300, range(40))
        assert emp == pytest.approx(per_gen_drift(n, MU, ALPHA), abs=0.05)


def test_determinism() -> None:
    a = run_transmission(20, MU, ALPHA, 50, seed=7)
    b = run_transmission(20, MU, ALPHA, 50, seed=7)
    assert a["z_max"] == b["z_max"]


def test_input_validation() -> None:
    with pytest.raises(ValueError):
        run_transmission(0, MU, ALPHA, 10, 0)
    with pytest.raises(ValueError):
        run_transmission(5, MU, 0.0, 10, 0)
    with pytest.raises(ValueError):
        run_transmission(5, MU, ALPHA, 0, 0)
    with pytest.raises(ValueError):
        per_gen_drift(0, MU, ALPHA)
    with pytest.raises(ValueError):
        critical_population_size(MU, 0.0)
