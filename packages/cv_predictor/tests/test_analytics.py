"""Tests for the analytics lifted verbatim from WS3."""

from __future__ import annotations

import math

from cv_predictor.analytics import (
    branching_survival,
    maintenance_threshold,
    v_star_meanfield,
)


def test_branching_survival_gw_anchor() -> None:
    # Galton–Watson non-extinction probability for Poisson(μ=2) offspring.
    assert math.isclose(branching_survival(2.0), 0.7968, abs_tol=1e-3)


def test_branching_survival_subcritical_is_zero() -> None:
    assert branching_survival(1.0) == 0.0
    assert branching_survival(0.5) == 0.0


def test_v_star_meanfield_finite_and_positive() -> None:
    for n in (10, 100, 1000):
        v = v_star_meanfield(n, 0.1, 0.3, 0.6)
        assert math.isfinite(v)
        assert v > 0.0


def test_maintenance_threshold_decreasing_in_f() -> None:
    fs = [0.1, 0.3, 0.5, 0.7, 0.9]
    ns = [maintenance_threshold(f) for f in fs]
    assert all(hi > lo for hi, lo in zip(ns, ns[1:]))
