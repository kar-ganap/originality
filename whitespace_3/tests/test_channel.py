"""Rung 4b — the channel refinement: targeted `κ` and WS2's `W↑` with `V^struct↓`.

TDD anchors (plan: docs/phases/phase-1-rung4b-channel-refinement-plan.md). The honest
decomposition (calibration): `V^struct`'s *decline* with `N` is partly endogenous
(present at κ=0); κ crushes its *level*; and *targeting* uniquely spares breadth. So
the full WS2 fingerprint (structural low & falling **while** breadth thrives) is unique
to the targeted mode. Adequate fidelity (`f≥0.5`) is the default regime (rung 4a/H5).
"""

from __future__ import annotations

import numpy as np
import pytest

from whitespace3.channel import run, variance_split
from whitespace3.conformity import crossover_slope, steady_grid

MODEL = dict(c0=3, f=0.6, epsilon=0.4, b=0.4, generations=32, persistence=2, p=2)
NS = [5, 20, 80]
SEEDS = range(6)
BURN = 18


def test_determinism() -> None:
    kw = dict(**MODEL, lam=3.0, mode="targeted")
    a = run(20, seed=2, **kw)
    b = run(20, seed=2, **kw)
    for key in ("C", "Vstruct", "Vlat", "H", "W"):
        assert np.array_equal(np.array(a[key]), np.array(b[key]), equal_nan=True)


def test_variance_split_and_invariant() -> None:
    birth = np.array([1, 1])
    struct = np.array([True, False])                  # one structural, one lateral
    r = np.array([[False, False], [True, True], [True, True], [True, True], [True, True]])
    vs, vl, vt = variance_split(birth, struct, r, n=10, k=2)
    assert vs[1] == pytest.approx(0.1) and vl[1] == pytest.approx(0.1)
    assert vt[1] == pytest.approx(0.2)
    assert np.isnan(vs[3]) and np.isnan(vs[4])
    # invariant on a real run: V^struct + V^lat == total V
    out = run(15, **MODEL, seed=1, lam=3.0, mode="targeted")
    vs2, vl2, vt2 = np.array(out["Vstruct"]), np.array(out["Vlat"]), np.array(out["V"])
    ok = ~np.isnan(vt2)
    assert np.allclose(vs2[ok] + vl2[ok], vt2[ok])


def test_signature_targeted() -> None:
    """T4 (H1, headline): under targeting, W↑ AND V^struct↓, together."""
    w = crossover_slope(NS, 3.0, seeds=SEEDS, burn_in=BURN, metric="W",
                        run_fn=run, mode="targeted", **MODEL)
    vs = crossover_slope(NS, 3.0, seeds=SEEDS, burn_in=BURN, metric="Vstruct",
                         run_fn=run, mode="targeted", **MODEL)
    assert w["lo"] > 0.0, f"breadth W should rise with N: {w}"
    assert vs["hi"] < 0.0, f"structural novelty V^struct should fall with N: {vs}"


def test_targeting_spares_breadth() -> None:
    """T5 (H2a, NC-uniform): targeting spares breadth; uniform κ crushes it."""
    wt = crossover_slope(NS, 3.0, seeds=SEEDS, burn_in=BURN, metric="W",
                         run_fn=run, mode="targeted", **MODEL)
    wu = crossover_slope(NS, 3.0, seeds=SEEDS, burn_in=BURN, metric="W",
                         run_fn=run, mode="uniform", **MODEL)
    vlt = crossover_slope(NS, 3.0, seeds=SEEDS, burn_in=BURN, metric="Vlat",
                          run_fn=run, mode="targeted", **MODEL)
    assert wt["point"] > 2.0 * wu["point"], f"targeting should spare breadth: {wt} vs {wu}"
    assert vlt["lo"] > 0.0, f"V^lat should rise under targeting: {vlt}"


def test_kappa_crushes_structural_level() -> None:
    """T5b (H2b, NC0): κ drops the structural *level* vs κ=0 (the decline-with-N is
    partly endogenous, present at κ=0)."""
    off = steady_grid(NS, 0.0, seeds=SEEDS, burn_in=BURN, metric="Vstruct",
                      run_fn=run, mode="off", **MODEL)
    tgt = steady_grid(NS, 3.0, seeds=SEEDS, burn_in=BURN, metric="Vstruct",
                      run_fn=run, mode="targeted", **MODEL)
    off_level = float(np.mean([off[nn].mean() for nn in NS]))
    tgt_level = float(np.mean([tgt[nn].mean() for nn in NS]))
    assert tgt_level < 0.5 * off_level, f"κ should crush V^struct level: {tgt_level} vs {off_level}"


def test_reconciliation() -> None:
    """T6 (H3): C*↑ while V^struct↓ under targeted κ."""
    c = crossover_slope(NS, 3.0, seeds=SEEDS, burn_in=BURN, metric="C",
                        run_fn=run, mode="targeted", **MODEL)
    vs = crossover_slope(NS, 3.0, seeds=SEEDS, burn_in=BURN, metric="Vstruct",
                         run_fn=run, mode="targeted", **MODEL)
    assert c["lo"] > 0.0, f"C* should rise (Henrich): {c}"
    assert vs["hi"] < 0.0, f"V^struct should fall (WWE): {vs}"


def test_input_validation() -> None:
    with pytest.raises(ValueError):
        run(0, 3, 0.6, 0.4, 0.4, 10, 0)
    with pytest.raises(ValueError):
        run(5, 3, 0.6, 0.4, 0.4, 10, 0, alpha=0.0)
    with pytest.raises(ValueError):
        run(5, 3, 0.6, 0.4, 0.4, 10, 0, alpha=1.5)
    with pytest.raises(ValueError):
        run(5, 3, 0.6, 0.4, 0.4, 10, 0, gamma_thresh=1.5)
    with pytest.raises(ValueError):
        run(5, 3, 0.6, 0.4, 0.4, 10, 0, mode="bad")
    with pytest.raises(ValueError):
        run(5, 3, 0.6, 0.4, 0.4, 10, 0, g_map="bad")
    with pytest.raises(ValueError):
        run(5, 3, 0.6, 0.4, 0.4, 10, 0, p=0)


# ── slow / thorough ───────────────────────────────────────────────────────────

@pytest.mark.slow
def test_fidelity_gate() -> None:
    """T7 (H5): V^struct↓ needs adequate fidelity; flat at f=0.3 (deep, not artifact)."""
    hi = crossover_slope(NS, 3.0, seeds=range(8), burn_in=BURN, metric="Vstruct",
                         run_fn=run, mode="targeted", **{**MODEL, "f": 0.6})
    lo = crossover_slope(NS, 3.0, seeds=range(8), burn_in=BURN, metric="Vstruct",
                         run_fn=run, mode="targeted", **{**MODEL, "f": 0.3})
    assert hi["hi"] < 0.0, f"f=0.6 should give V^struct↓: {hi}"
    assert lo["hi"] >= 0.0, f"f=0.3 should NOT (fidelity gate): {lo}"


@pytest.mark.slow
def test_sensitivity_signature() -> None:
    """T8: the signature (V^struct↓ with W↑) survives perturbing ε, b, p, g, γ_thresh,
    and a tight canon (α=0.10). (The α boundary is pinned separately.)"""
    for over in ({"epsilon": 0.55}, {"b": 0.6}, {"p": 3}, {"g_map": "hyper"},
                 {"gamma_thresh": 0.4}, {"alpha": 0.10}):
        kw = {**MODEL, **over}
        vs = crossover_slope(NS, 3.0, seeds=range(6), burn_in=BURN, metric="Vstruct",
                             run_fn=run, mode="targeted", **kw)
        w = crossover_slope(NS, 3.0, seeds=range(6), burn_in=BURN, metric="W",
                            run_fn=run, mode="targeted", **kw)
        assert vs["point"] < 0.0 and w["point"] > 0.0, f"signature failed under {over}: {vs}, {w}"


@pytest.mark.slow
def test_canon_fraction_boundary() -> None:
    """T8b: the V^struct signature needs a *tight* canon — it holds for α≤0.15 (a select
    few are 'canonical', so structural deviance is well-defined) and washes out for a
    broad canon (α≥0.20). An honest boundary, like the fidelity gate."""
    tight = crossover_slope(NS, 3.0, seeds=range(8), burn_in=BURN, metric="Vstruct",
                            run_fn=run, mode="targeted", **{**MODEL, "alpha": 0.10})
    broad = crossover_slope(NS, 3.0, seeds=range(8), burn_in=BURN, metric="Vstruct",
                            run_fn=run, mode="targeted", **{**MODEL, "alpha": 0.25})
    assert tight["hi"] < 0.0, f"tight canon (α=0.10) should give V^struct↓: {tight}"
    assert broad["hi"] >= 0.0, f"broad canon (α=0.25) should wash out: {broad}"
