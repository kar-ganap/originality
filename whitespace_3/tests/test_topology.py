"""Rung 4e — topology robustness (Core Claim `cc:robust`, the ER/WS/BA half): the
κ-signature (`V^struct↓` with breadth `W` spared) survives on a fixed finite-degree
interaction graph, invariant to topology. Thresholds are the smoke-confirmed values
(``docs/phases/phase-1-rung4e-topology-robustness-plan.md``)."""

from __future__ import annotations

import numpy as np
import pytest

from whitespace3.channel import _TOPOLOGIES, _build_adjacency, run

GRAPHS = ("er", "ws", "ba")
ALL = ("well_mixed", *GRAPHS)


def _sig(topo: str, mode: str, lam: float, seeds: tuple[int, ...] = (0, 1),
         graph_seed: int = 0) -> tuple[float, float]:
    """(steady-state V^struct, steady-state W) for a topology on a given graph instance
    (``graph_seed``), averaged over dynamics ``seeds``."""
    vs, ws = [], []
    for s in seeds:
        r = run(80, 5, 0.6, 0.3, 0.5, 45, s, lam=lam, mode=mode, alpha=0.15,
                topology=topo, mean_degree=8, graph_seed=graph_seed)
        vs.append(float(np.nanmean(r["Vstruct"][22:])))
        ws.append(float(np.mean(r["W"][22:])))
    return float(np.mean(vs)), float(np.mean(ws))


def test_determinism() -> None:
    a = run(60, 5, 0.6, 0.3, 0.5, 30, 0, lam=0.25, topology="er", mean_degree=8, graph_seed=1)
    b = run(60, 5, 0.6, 0.3, 0.5, 30, 0, lam=0.25, topology="er", mean_degree=8, graph_seed=1)
    assert a["C"] == b["C"]
    assert np.allclose(a["Vstruct"][:-1], b["Vstruct"][:-1])
    assert a["W"] == b["W"]


def test_well_mixed_identity() -> None:
    # H0: the default is byte-identical to explicit well_mixed (no regression to rungs 4a/4b).
    a = run(80, 5, 0.6, 0.3, 0.5, 40, 0, lam=0.25)
    b = run(80, 5, 0.6, 0.3, 0.5, 40, 0, lam=0.25, topology="well_mixed")
    assert a["C"] == b["C"]
    assert a["W"] == b["W"]
    assert np.allclose(a["Vstruct"][:-1], b["Vstruct"][:-1])
    assert np.allclose(a["H"], b["H"])


def test_graph_mean_degree() -> None:
    # realized mean degree ≈ target (self-loops excluded); graphs actually finite-degree.
    for topo in GRAPHS:
        a = _build_adjacency(topo, 200, 8, 0)
        deg = np.asarray(a.sum(axis=1)).ravel() - 1          # drop the self-loop
        assert 4.0 <= float(deg.mean()) <= 12.0
        assert float(deg.max()) < 200                        # not the complete graph


def test_signature_sign_invariant() -> None:
    # H1 + H2 (the crux): on EVERY topology, targeted κ suppresses V^struct AND spares W.
    for topo in ALL:
        v_off, w_off = _sig(topo, "off", 0.0)
        v_on, w_on = _sig(topo, "targeted", 0.25)
        assert v_on < v_off, f"{topo}: V^struct not suppressed ({v_on:.4f} !< {v_off:.4f})"
        assert w_on > 0.5 * w_off, f"{topo}: breadth collapsed ({w_on:.0f} vs {w_off:.0f})"


def test_placebo_kappa_zero() -> None:
    # κ=0 (λ=0) ⇒ no suppression regardless of mode, on a graph — the signature is κ-driven.
    v_off, _ = _sig("er", "off", 0.0)
    v_zero, _ = _sig("er", "targeted", 0.0)
    assert abs(v_off - v_zero) < 0.02


def test_input_validation() -> None:
    assert "well_mixed" in _TOPOLOGIES
    with pytest.raises(ValueError):
        run(80, 5, 0.6, 0.3, 0.5, 20, 0, topology="ring")
    with pytest.raises(ValueError):
        run(80, 5, 0.6, 0.3, 0.5, 20, 0, topology="er", mean_degree=1)
    with pytest.raises(ValueError):
        run(80, 5, 0.6, 0.3, 0.5, 20, 0, topology="er", mean_degree=200)


@pytest.mark.slow
def test_signature_robust_to_graph_instance() -> None:
    # robustness to the random GRAPH DRAW (not just dynamics noise): targeted κ suppresses
    # V^struct on EVERY one of several independent graph instances per topology — incl. the
    # BA hub draws (the worry case). Complements test_signature_sign_invariant (one instance).
    for topo in GRAPHS:
        for gs in range(4):
            v_off, _ = _sig(topo, "off", 0.0, graph_seed=gs)
            v_on, _ = _sig(topo, "targeted", 0.25, graph_seed=gs)
            assert v_on < v_off, f"{topo} graph_seed={gs}: V^struct not suppressed"


@pytest.mark.slow
def test_crossover_slope_sign_invariant() -> None:
    # H3: κ makes V^struct fall at least as hard in N on every topology (the crossover sign,
    # not magnitude). Regression slopes with seed-bootstrap, never a two-point difference.
    from whitespace3.conformity import logN_slope_ci, steady_grid

    ns = [40, 80, 160]
    kw = dict(c0=5, f=0.6, epsilon=0.3, b=0.5, generations=50, alpha=0.15, mean_degree=8)
    for topo in GRAPHS:
        off = steady_grid(ns, 0.0, seeds=range(4), burn_in=25, metric="Vstruct",
                          run_fn=run, mode="off", topology=topo, **kw)
        on = steady_grid(ns, 0.25, seeds=range(4), burn_in=25, metric="Vstruct",
                         run_fn=run, mode="targeted", topology=topo, **kw)
        s_off = logN_slope_ci(ns, off)["point"]
        s_on = logN_slope_ci(ns, on)["point"]
        assert s_on <= s_off + 0.02, f"{topo}: κ did not steepen V^struct decline"
