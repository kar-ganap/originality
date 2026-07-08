"""Rung 5b — light mean-field analytics: the Henrich carrier-survival intuition (C) and the
crossover law λ* = d ln P/d ln N (V). Simulation-guided, not airtight; anchored where a
known analytic value exists (the Galton–Watson survival at μ=2)."""

from __future__ import annotations

import numpy as np
import pytest

from whitespace3.analytics import (
    branching_survival,
    carrier_fixed_point,
    crossover_lambda,
    maintenance_threshold,
    v_star_meanfield,
)


def test_maintenance_threshold() -> None:
    # Henrich critical population size n* = 1/ln(1/(1-f)); decreasing in f (higher fidelity
    # ⇒ easier to maintain ⇒ smaller critical N).
    assert abs(maintenance_threshold(0.6) - 1.0 / np.log(1 / 0.4)) < 1e-9
    assert maintenance_threshold(0.9) < maintenance_threshold(0.6) < maintenance_threshold(0.3)
    with pytest.raises(ValueError):
        maintenance_threshold(0.0)


def test_carrier_fixed_point() -> None:
    # saturates near n when maintained (large n·f); collapses to 0 below the threshold.
    assert abs(carrier_fixed_point(100, 0.6) - 100.0) < 1e-6      # maintained ⇒ c*≈n
    assert carrier_fixed_point(1, 0.1) < 1e-6                     # below threshold ⇒ lost
    assert carrier_fixed_point(200, 0.6) > carrier_fixed_point(100, 0.6)  # monotone in n
    assert carrier_fixed_point(50, 0.9) > carrier_fixed_point(50, 0.3)    # monotone in f


def test_branching_survival() -> None:
    # persistence = GW non-extinction; sub/critical ⇒ 0; the known Poisson(2) survival 0.7968.
    assert branching_survival(0.5) == 0.0
    assert branching_survival(1.0) == 0.0
    assert abs(branching_survival(2.0) - 0.7968) < 1e-3          # KNOWN analytic value
    assert branching_survival(5.0) > branching_survival(2.0)     # rising in μ
    assert branching_survival(18.0) > 0.999                       # saturates → 1


def test_v_star_hump() -> None:
    # mean-field per-capita V* is hump-shaped in N at intermediate λ (more minds, then
    # consensus suppression) — the CC:wwe shape; peak at small N.
    vs = [v_star_meanfield(n, 0.5, 1.0, 0.6) for n in (2, 5, 10, 30, 100)]
    assert vs[1] > vs[0]                                          # rises (2→5)
    assert vs[1] > vs[3] > vs[4]                                  # then falls (5→30→100)


def test_crossover_lambda() -> None:
    # λ* = persistence elasticity: rising P ⇒ positive λ*; saturated (flat) P ⇒ ~0 (why the
    # simulated crossover sits near zero — persistence saturates over the relevant N).
    ns = [30, 60, 120, 240]
    rising = crossover_lambda(ns, [0.5, 0.6, 0.7, 0.8])
    flat = crossover_lambda(ns, [1.0, 1.0, 1.0, 1.0])
    assert rising > 0.1                                           # meaningful returns-to-scale
    assert abs(flat) < 1e-6                                       # saturated ⇒ λ*≈0


def test_input_validation() -> None:
    with pytest.raises(ValueError):
        carrier_fixed_point(0, 0.5)
    with pytest.raises(ValueError):
        v_star_meanfield(0, 0.5, 0.1, 0.6)
