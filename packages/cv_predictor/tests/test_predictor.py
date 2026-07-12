"""Tests for the mean-field regime predictor.

NOTE ON PARAMS. The spec sketched these assertions at ``f=0.6``, but the *mean-field*
crossover ``λ*`` collapses to ≈3.5e-4 there: persistence ``P(N)=GW-survival(n·f)`` is already
saturated (≈1) across the whole default grid (``n≥10 ⇒ n·f≥6 ≫ 1``) — WS3's own
``experiments/phase-1-rung5/analytics_check.py`` says "λ*≈0" at ``f=0.6``; the headline
``λ*≈0.09`` is the *simulation* crossover, not the mean-field one that ``predict`` computes.
So at ``f=0.6`` BOTH ``lam=0.05`` and ``lam=0.6`` are C-favouring and the intended
V-favouring→C-favouring demonstration is unrealisable.

We therefore exercise the sign-structure at ``f=0.15`` — the fidelity at which the mean-field
crossover on the default grid lands at ``λ*≈0.08`` (echoing the sim's ≈0.09), so ``lam=0.05``
is genuinely below it (V-favouring) and ``lam=0.6`` above (C-favouring), exactly the
sign-structure the spec intends, computed by the exact spec'd algorithm.
``test_high_fidelity_crossover_collapses`` documents the true ``f=0.6`` behaviour.
"""

from __future__ import annotations

import math

from cv_predictor import RegimeForecast, SystemParams, predict
from cv_predictor.analytics import branching_survival, crossover_lambda

# Fidelity at which the mean-field crossover lands inside (0.05, 0.6) on the default grid.
F_CROSS = 0.15


def test_v_favouring_below_crossover() -> None:
    fc = predict(SystemParams(lam=0.05, epsilon=0.3, f=F_CROSS))
    assert fc.regime == "V-favouring"
    assert fc.slope_at_lam > 0.0


def test_c_favouring_above_crossover() -> None:
    fc = predict(SystemParams(lam=0.6, epsilon=0.3, f=F_CROSS))
    assert fc.regime == "C-favouring"
    assert fc.slope_at_lam < 0.0


def test_lambda_star_finite_in_unit_interval() -> None:
    fc = predict(SystemParams(lam=0.05, epsilon=0.3, f=F_CROSS))
    assert math.isfinite(fc.lambda_star)
    assert 0.0 < fc.lambda_star < 1.0


def test_v_trajectory_length() -> None:
    params = SystemParams(lam=0.05, epsilon=0.3, f=F_CROSS)
    fc = predict(params)
    assert isinstance(fc, RegimeForecast)
    assert len(fc.v_trajectory) == len(params.n_grid)


def test_regime_consistency() -> None:
    # regime == "V-favouring" exactly when params.lam < lambda_star.
    for lam in (0.0, 0.02, 0.05, 0.2, 0.6, 0.9):
        fc = predict(SystemParams(lam=lam, epsilon=0.3, f=F_CROSS))
        assert (fc.regime == "V-favouring") == (lam < fc.lambda_star)


def test_lambda_star_matches_crossover_lambda() -> None:
    # Cross-check: predict's λ* == the persistence elasticity crossover_lambda computes.
    params = SystemParams(lam=0.3, epsilon=0.3, f=F_CROSS)
    fc = predict(params)
    persistence = [branching_survival(n * params.f) for n in params.n_grid]
    assert math.isclose(
        fc.lambda_star, crossover_lambda(params.n_grid, persistence), abs_tol=1e-3
    )


def test_high_fidelity_crossover_collapses() -> None:
    # Honest record of the spec's original f=0.6: persistence saturates, so λ* → ~0 and BOTH
    # lam=0.05 and lam=0.6 are C-favouring (the mean-field crossover is NOT the sim's 0.09).
    lo = predict(SystemParams(lam=0.05, epsilon=0.3, f=0.6))
    hi = predict(SystemParams(lam=0.6, epsilon=0.3, f=0.6))
    assert lo.regime == "C-favouring"
    assert hi.regime == "C-favouring"
    assert 0.0 < lo.lambda_star < 0.01
