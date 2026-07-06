"""Rung 1 — the transmission harness reproduces Henrich 2004, verified against the
paper's equations AND against Mesoudi's canonical ``DemographyModel`` reproduction
(Simulation Models of Cultural Evolution in R, Model 9), with its specific runs.

Level-2 anchor: our formulas ARE Henrich's Eq (2) ``dz_bar = -alpha + beta(gamma_E
+ ln N)`` and Eq (3) ``N* = exp(alpha/beta - gamma_E)``.

Level-3 anchor (reproduce specific published numbers of the *same* model):
  * Mesoudi's two stated runs at ``alpha=30, beta=15``: ``N=100`` -> cultural GAIN,
    ``N=1`` -> cultural LOSS.
  * Mesoudi's ``DemographyModel2`` at ``alpha=7, beta=1``: the Delta-z-bar-vs-N
    curve crosses zero at ``N* = exp(7 - gamma_E) ~= 616`` (loss below, gain above).
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


def test_henrich_eq2_drift_formula() -> None:
    """Henrich 2004 Eq (2): dz_bar = -alpha + beta*(gamma_E + ln N)."""
    assert per_gen_drift(1, 30, 15) == pytest.approx(-30 + 15 * EULER_GAMMA)
    assert per_gen_drift(100, 30, 15) == pytest.approx(
        -30 + 15 * (math.log(100) + EULER_GAMMA))


def test_henrich_eq3_critical_population_size() -> None:
    """Henrich 2004 Eq (3): N* = exp(alpha/beta - gamma_E). Mesoudi's alpha=7,
    beta=1 gives N* ~= 616; the "complex skill" alpha=9, beta=1 gives ~4553."""
    assert critical_population_size(7, 1) == pytest.approx(math.exp(7 - EULER_GAMMA))
    assert critical_population_size(7, 1) == pytest.approx(615.7, abs=1.0)
    assert critical_population_size(9, 1) == pytest.approx(4549.0, abs=5.0)
    # drift evaluated at N* is zero by construction
    assert per_gen_drift(round(critical_population_size(7, 1)), 7, 1) == pytest.approx(
        0.0, abs=1e-3)


def test_mesoudi_model9_regime_reproduction() -> None:
    """Mesoudi Model 9's two stated runs (alpha=30, beta=15): N=100 -> gain,
    N=1 -> loss, and the drift magnitudes match Eq (2)."""
    d100 = measure_drift(100, 30, 15, 100, range(20))
    assert d100 > 0                                              # "cultural gain"
    assert d100 == pytest.approx(per_gen_drift(100, 30, 15), abs=3.0)   # ~ +47.7

    d1 = measure_drift(1, 30, 15, 100, range(20))
    assert d1 < 0                                               # "cultural loss"
    assert d1 == pytest.approx(per_gen_drift(1, 30, 15), abs=3.0)       # ~ -21.3


def test_mesoudi_model9_crossover_at_N_star() -> None:
    """The hard Level-3 number: DemographyModel2(alpha=7, beta=1) crosses
    Delta-z-bar = 0 at N* ~= 616. Our simulation reproduces the crossover:
    loss below, gain above, and ~0 at N*."""
    nstar = critical_population_size(7, 1)
    assert 610.0 < nstar < 620.0
    assert measure_drift(300, 7, 1, 200, range(20)) < 0         # below N* -> loss
    assert measure_drift(1000, 7, 1, 200, range(20)) > 0        # above N* -> gain
    assert measure_drift(round(nstar), 7, 1, 400, range(40)) == pytest.approx(
        0.0, abs=0.1)                                           # at N* -> ~0


def test_drift_monotone_in_N() -> None:
    drifts = [measure_drift(n, 7, 1, 200, range(15)) for n in (2, 100, 616, 2000)]
    assert all(drifts[i] < drifts[i + 1] for i in range(len(drifts) - 1))


def test_determinism() -> None:
    a = run_transmission(20, 7, 1, 50, seed=7)
    b = run_transmission(20, 7, 1, 50, seed=7)
    assert a["z_max"] == b["z_max"]


def test_input_validation() -> None:
    with pytest.raises(ValueError):
        run_transmission(0, 7, 1, 10, 0)
    with pytest.raises(ValueError):
        run_transmission(5, -1, 1, 10, 0)          # alpha must be >= 0
    with pytest.raises(ValueError):
        run_transmission(5, 7, 0.0, 10, 0)         # beta must be > 0
    with pytest.raises(ValueError):
        run_transmission(5, 7, 1, 0, 0)
    with pytest.raises(ValueError):
        per_gen_drift(0, 7, 1)
    with pytest.raises(ValueError):
        critical_population_size(7, 0.0)
