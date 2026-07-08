"""Rung 5a — the reconciliation deliverable. The Pareto / non-strict-trade-off claim's
concrete same-sign intervention: **selective isolation** (`ι`) — shield a subgroup from κ,
and its structural novelty stays high while global `C` is preserved. The (λ,N) phase-diagram
crossover and the (ρ) trade-off live in the reproducible experiment
(``experiments/phase-1-rung5/phase_diagram.py``). Thresholds are smoke-confirmed."""

from __future__ import annotations

import numpy as np
import pytest

from whitespace3.channel import run


def _iso(key: str, iso: float, seeds: tuple[int, ...] = (0, 1, 2)) -> float:
    """steady-state ``key`` at isolation fraction ``iso``, averaged over dynamics seeds."""
    return float(np.mean([
        np.nanmean(run(80, 5, 0.6, 0.3, 0.5, 50, s, lam=0.25, mode="targeted",
                       alpha=0.15, isolated_frac=iso)[key][25:])
        for s in seeds
    ]))


def test_determinism_isolation() -> None:
    a = run(60, 5, 0.6, 0.3, 0.5, 30, 0, lam=0.25, isolated_frac=0.25)
    b = run(60, 5, 0.6, 0.3, 0.5, 30, 0, lam=0.25, isolated_frac=0.25)
    assert a["C"] == b["C"]
    assert np.allclose(a["Vstruct_iso"][:-1], b["Vstruct_iso"][:-1])


def test_isolation_off_identity() -> None:
    # H0: isolated_frac=0 is byte-identical; Vstruct_iso≈0 and Vstruct_conf==Vstruct.
    a = run(80, 5, 0.6, 0.3, 0.5, 40, 0, lam=0.25)
    b = run(80, 5, 0.6, 0.3, 0.5, 40, 0, lam=0.25, isolated_frac=0.0)
    assert a["C"] == b["C"]
    assert np.allclose(a["Vstruct"][:-1], b["Vstruct"][:-1])
    assert float(np.nanmax(np.abs(np.asarray(b["Vstruct_iso"][:-1])))) < 1e-9
    assert np.allclose(b["Vstruct_conf"][:-1], b["Vstruct"][:-1])


def test_pareto_selective_isolation() -> None:
    # H-pareto-iso (the concrete same-sign / Pareto intervention): the shielded subgroup
    # keeps V^struct high vs the conformist majority, AND global C is preserved.
    vi, vc = _iso("Vstruct_iso", 0.25), _iso("Vstruct_conf", 0.25)
    assert vi > vc * 1.1                              # shielded subgroup materially more novel
    c_off, c_iso = _iso("C", 0.0), _iso("C", 0.25)
    assert c_iso >= c_off * 0.97                      # global C not lowered ⇒ Pareto, not trade-off


def test_input_validation_isolation() -> None:
    with pytest.raises(ValueError):
        run(80, 5, 0.6, 0.3, 0.5, 20, 0, isolated_frac=1.0)
    with pytest.raises(ValueError):
        run(80, 5, 0.6, 0.3, 0.5, 20, 0, isolated_frac=-0.1)


_PHASE_KW = dict(c0=5, f=0.6, epsilon=0.3, b=0.5, generations=60, alpha=0.15, mode="uniform")
_PHASE_NS = [30, 60, 120, 240]


def _logn_slope(metric: str, lam: float) -> dict[str, float]:
    from whitespace3.conformity import logN_slope_ci, steady_grid

    g = steady_grid(_PHASE_NS, lam, seeds=range(6), burn_in=30, metric=metric, run_fn=run,
                    **_PHASE_KW)
    return logN_slope_ci(_PHASE_NS, g)


@pytest.mark.slow
def test_phase_crossover() -> None:
    # H-cross: ∂V*/∂logN flips from V-favouring (λ=0, ≥0) to C-favouring (high λ, <0) — a
    # locatable λ* (the phase-diagram crossover; λ*≈0.09, consistent with rung 3's 0.086).
    s0 = _logn_slope("V", 0.0)
    s1 = _logn_slope("V", 1.0)
    assert s1["point"] < -0.002                       # high λ: V falls in N (C-favouring)
    assert s0["point"] > s1["point"] + 0.003          # low λ less negative ⇒ a crossover exists
    assert s0["point"] > -0.002                        # low λ: V-favouring (flat/rising)


@pytest.mark.slow
def test_reconciliation_opposite_signs() -> None:
    # H-trade: same N-lever, opposite signs — C↑ (Henrich, redundancy) while V↓ (WWE) at high λ.
    c = _logn_slope("C", 1.0)
    v = _logn_slope("V", 1.0)
    assert c["point"] > 0.5 and c["lo"] > 0.0         # C rises with N, CI excludes 0
    assert v["point"] < 0.0                            # V falls with N — the reconciliation
