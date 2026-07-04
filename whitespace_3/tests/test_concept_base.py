"""Rung 2a — concept-base transmission (no innovation yet).

Un-bundles transmission from innovation. Two anchors:

  * **Powell preservation:** with the primer's per-level f/redundancy acquisition
    (Def 4.1) on a prerequisite ladder, cumulative complexity C is *maintained*
    when the population is large (high redundancy) and *lost* (Tasmania) when it
    is small.
  * **The un-bundling anchor:** transmission ALONE can only maintain or lose C —
    it can never *grow* it (you cannot copy a level nobody has). C is therefore
    non-increasing and never exceeds the starting frontier c0. Growth waits for
    innovation (rung 2b), which is exactly what makes V separately definable.
"""

from __future__ import annotations

import pytest

from whitespace3.concept_base import retained_complexity, run_transmission

C0, F = 10, 0.3


def test_maintenance_large_N() -> None:
    """Large N → the full ladder is preserved (redundancy protects every level)."""
    r = run_transmission(n=200, c0=C0, f=F, generations=100, seed=0)
    assert r["C"][0] == C0
    assert r["C"][-1] == C0


def test_loss_small_N_is_tasmania() -> None:
    """Small N → cumulative complexity decays (the Tasmania effect)."""
    r = run_transmission(n=3, c0=C0, f=F, generations=100, seed=0)
    assert r["C"][-1] < C0
    assert retained_complexity(3, C0, F, 100, range(20)) < C0 / 2


def test_transmission_cannot_grow_C() -> None:
    """THE un-bundling anchor: without innovation, C never exceeds c0 and is
    monotone non-increasing over generations (transmission cannot create novelty)."""
    for n in (3, 20, 200):
        c = run_transmission(n=n, c0=C0, f=F, generations=100, seed=1)["C"]
        assert max(c) == C0
        assert all(c[t + 1] <= c[t] for t in range(len(c) - 1))


def test_retained_complexity_monotone_in_N() -> None:
    rc = [retained_complexity(n, C0, F, 100, range(20)) for n in (2, 5, 20, 100)]
    assert all(rc[i] <= rc[i + 1] + 1e-9 for i in range(len(rc) - 1))
    assert rc[0] < rc[-1]


def test_retained_complexity_monotone_in_f() -> None:
    rc = [retained_complexity(8, C0, f, 100, range(20)) for f in (0.1, 0.3, 0.6, 0.9)]
    assert all(rc[i] <= rc[i + 1] + 1e-9 for i in range(len(rc) - 1))
    assert rc[0] < rc[-1]


def test_determinism() -> None:
    a = run_transmission(20, C0, F, 50, seed=7)
    b = run_transmission(20, C0, F, 50, seed=7)
    assert a["C"] == b["C"]


def test_input_validation() -> None:
    with pytest.raises(ValueError):
        run_transmission(0, C0, F, 10, 0)
    with pytest.raises(ValueError):
        run_transmission(5, C0, 1.5, 10, 0)
    with pytest.raises(ValueError):
        run_transmission(5, C0, -0.1, 10, 0)
    with pytest.raises(ValueError):
        run_transmission(5, C0, F, 0, 0)
    with pytest.raises(ValueError):
        run_transmission(5, -1, F, 10, 0)
