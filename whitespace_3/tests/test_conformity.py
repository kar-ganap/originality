"""Rung 3 — conformity ``κ`` → the crossover ``λ*`` (THE lemma).

TDD anchors (plan: docs/phases/phase-1-rung3-conformity-crossover-plan.md). The
pre-registered *signs* are fixed; grid sizes/thresholds are calibrated to be
non-flaky (fast sign-checks gate the pre-push hook; thorough tight-CI variants are
``slow``, run under ``make test-all``).

  * **T1 determinism / T2 κ=0 regression / T3 throttle primitives / T3b throttle
    reduces innovation.**
  * **T4 THE crossover (H3, headline):** scaling-κ ⇒ ``∂V*/∂logN`` CI ``<0``; the
    κ=0 placebo does not decline.
  * **T5 the hump (H3b):** interior peak ``N*``; small-team advantage on the
    descending branch.
  * **T6 reconciliation (H4′):** under scaling-κ, ``C*↑`` while ``V*↓`` — same lever,
    opposite signs.
  * **T7 NC1 (const, level-not-scaling) / T8 NC2 (fraction, VC-style):** no crossover
    — it is *absolute scale-tracking* consensus that bites.
  * **T9 dose-response / T10 spec-invariance / T_λ* location** (``slow``).
"""

from __future__ import annotations

import numpy as np
import pytest

from whitespace3.conformity import crossover_slope, locate_lambda_star, steady_grid
from whitespace3.innovation import consensus_signal, run, suppression

MODEL = dict(c0=5, f=0.5, epsilon=0.4, b=0.4, generations=40, persistence=2)
NS = [4, 12, 40]
SEEDS = range(6)
BURN = 22


# ── T1/T2/T3 — engine correctness under κ ─────────────────────────────────────

def test_determinism_with_kappa() -> None:
    kw = dict(**MODEL, lam=0.15, kappa_mode="scaling")
    a = run(30, seed=3, **kw)
    b = run(30, seed=3, **kw)
    assert a["C"] == b["C"] and a["R_size"] == b["R_size"]
    assert np.array_equal(np.array(a["V"]), np.array(b["V"]), equal_nan=True)


def test_kappa_off_equals_rung2b() -> None:
    """κ off ⇒ byte-identical to the rung-2b baseline (same code path); λ ignored."""
    base = run(25, **MODEL, seed=7)                                   # defaults: off
    off = run(25, **MODEL, seed=7, kappa_mode="off", lam=0.0)
    off2 = run(25, **MODEL, seed=7, kappa_mode="off", lam=9.0)        # λ ignored when off
    assert base["C"] == off["C"] == off2["C"]
    assert base["R_size"] == off["R_size"] == off2["R_size"]


def test_suppression_map() -> None:
    assert suppression(0.0, "exp") == 1.0
    assert suppression(0.0, "hyper") == 1.0
    assert suppression(1.0, "exp") == pytest.approx(float(np.exp(-1.0)))
    assert suppression(1.0, "hyper") == pytest.approx(0.5)
    assert suppression(2.0, "exp") < suppression(1.0, "exp") < suppression(0.5, "exp")


def test_consensus_signal() -> None:
    car = np.array([10, 2, 0], dtype=np.int64)
    assert consensus_signal(car, "maxredundancy") == pytest.approx(float(np.log(11)))
    assert consensus_signal(car, "repsize") == pytest.approx(float(np.log(3)))  # 2 live +1
    assert consensus_signal(np.array([], dtype=np.int64), "maxredundancy") == 0.0


def test_kappa_reduces_innovation() -> None:
    """Stronger scale-tracking conformity ⇒ fewer novelties ⇒ smaller repertoire."""
    off = run(40, **MODEL, seed=1, kappa_mode="scaling", lam=0.0)
    strong = run(40, **MODEL, seed=1, kappa_mode="scaling", lam=0.6)
    assert strong["R_size"][-1] < off["R_size"][-1]


# ── T4 — THE crossover (H3, headline gate) ────────────────────────────────────

def test_crossover_exists() -> None:
    placebo = crossover_slope(NS, 0.0, seeds=SEEDS, burn_in=BURN, kappa_mode="scaling", **MODEL)
    cross = crossover_slope(NS, 0.5, seeds=SEEDS, burn_in=BURN, kappa_mode="scaling", **MODEL)
    assert placebo["hi"] >= 0.0, f"κ=0 placebo should not decline: {placebo}"
    assert cross["hi"] < 0.0, f"scaling-κ should make V* decline in N: {cross}"


# ── T5 — the hump (H3b) ───────────────────────────────────────────────────────

def test_hump_shape() -> None:
    ns = [3, 8, 24, 72]
    grid = steady_grid(ns, 0.15, seeds=range(8), burn_in=BURN, kappa_mode="scaling", **MODEL)
    means = np.array([grid[nn].mean() for nn in ns])
    peak = int(np.argmax(means))
    assert 0 < peak < len(ns) - 1, f"V*(N) should peak at an interior N*: {means}"
    assert means[peak] > means[-1]              # small-team advantage on the descending branch


# ── T6 — reconciliation preview (H4′): C*↑ while V*↓ ──────────────────────────

def test_reconciliation_preview() -> None:
    c = crossover_slope(NS, 0.25, seeds=SEEDS, burn_in=BURN, metric="C",
                        kappa_mode="scaling", **MODEL)
    v = crossover_slope(NS, 0.25, seeds=SEEDS, burn_in=BURN, metric="V",
                        kappa_mode="scaling", **MODEL)
    assert c["lo"] > 0.0, f"C* should rise with N (Henrich): {c}"
    assert v["hi"] < 0.0, f"V* should fall with N (WWE): {v}"


# ── T7/T8 — negative controls: it is *absolute scale-tracking* consensus ───────

def test_control_const_no_crossover() -> None:
    """NC1: constant κ (same level, no N-scaling) ⇒ no crossover."""
    s = crossover_slope(NS, 0.5, seeds=SEEDS, burn_in=BURN, kappa_mode="const", n_ref=20, **MODEL)
    assert s["hi"] >= 0.0, f"const-κ should not produce a crossover: {s}"


def test_control_fraction_no_crossover() -> None:
    """NC2: fractional (VC-style) κ ∝ max_e M / N ≈ 1 (scale-free) ⇒ no crossover."""
    s = crossover_slope(NS, 0.5, seeds=SEEDS, burn_in=BURN, kappa_mode="fraction", **MODEL)
    assert s["hi"] >= 0.0, f"fraction-κ should not produce a crossover: {s}"


# ── T11 — input validation ────────────────────────────────────────────────────

def test_input_validation_kappa() -> None:
    with pytest.raises(ValueError):
        run(5, 5, 0.5, 0.3, 0.5, 10, 0, lam=-0.1)
    with pytest.raises(ValueError):
        run(5, 5, 0.5, 0.3, 0.5, 10, 0, kappa_mode="bogus")
    with pytest.raises(ValueError):
        run(5, 5, 0.5, 0.3, 0.5, 10, 0, g_map="bogus")
    with pytest.raises(ValueError):
        run(5, 5, 0.5, 0.3, 0.5, 10, 0, signal="bogus")
    with pytest.raises(ValueError):
        run(5, 5, 0.5, 0.3, 0.5, 10, 0, kappa_mode="const", n_ref=None)


# ── slow / thorough variants (make test-all) ──────────────────────────────────

@pytest.mark.slow
def test_crossover_thorough() -> None:
    cross = crossover_slope([4, 12, 40, 120], 0.5, seeds=range(12), burn_in=BURN,
                            n_boot=800, kappa_mode="scaling", **MODEL)
    assert cross["hi"] < 0.0


@pytest.mark.slow
def test_dose_response_monotone() -> None:
    slopes = [crossover_slope(NS, lam, seeds=range(8), burn_in=BURN, kappa_mode="scaling",
                              **MODEL)["point"] for lam in (0.0, 0.15, 0.3)]
    assert all(slopes[i] >= slopes[i + 1] - 0.01 for i in range(len(slopes) - 1))
    assert slopes[0] > slopes[-1]


@pytest.mark.slow
def test_spec_robustness_crossover_sign() -> None:
    for g_map in ("exp", "hyper"):
        for signal in ("maxredundancy", "repsize"):
            s = crossover_slope(NS, 0.5, seeds=range(8), burn_in=BURN, kappa_mode="scaling",
                                g_map=g_map, signal=signal, **MODEL)
            assert s["point"] < 0.0, f"crossover sign not invariant: g={g_map} s={signal}: {s}"


@pytest.mark.slow
def test_lambda_star_located() -> None:
    r = locate_lambda_star([4, 12, 40, 120], [0.0, 0.1, 0.2, 0.3], seeds=range(8), burn_in=BURN,
                           kappa_mode="scaling", n_boot=500, **MODEL)
    assert r["lambda_star"] is not None
    assert 0.0 < r["lambda_star"] < 0.3
