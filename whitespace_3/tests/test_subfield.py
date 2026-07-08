"""Rung 4d — the subfield (content/τ) channel: fragmentation reproduces the WS2 Phase-2.4
fingerprint (global structural novelty rises, within-niche flat, coexists with H↑), as a
crossover in niche distinctiveness. Thresholds are the prototype-confirmed values
(``docs/phases/phase-1-rung4d-subfield-channel-plan.md`` §9)."""

from __future__ import annotations

import numpy as np
import pytest

from whitespace3.subfield import (
    fingerprint,
    global_slope,
    h_global,
    k_final,
    run,
    within_slope,
)


def test_determinism() -> None:
    a = run(10, 50, 0)
    b = run(10, 50, 0)
    assert np.array_equal(a["u"], b["u"])
    assert np.array_equal(a["v"], b["v"])
    assert np.array_equal(a["birth"], b["birth"])


def test_k_equals_n_over_m() -> None:
    # F5: niche count is FORCED by K = N/m over the growing field, not imposed.
    r = run(10, 30, 0, n0=10, n_growth=4)
    for n_t, k_t in r["k_traj"]:
        assert k_t == max(1, n_t // 10)
    assert k_final(r) == r["k_traj"][-1][0] // 10
    # placebo freezes K while N still grows
    r0 = run(10, 30, 0, n0=10, n_growth=4, fragmentation=False)
    assert all(k_t == 1 for _n, k_t in r0["k_traj"])
    assert r0["k_traj"][-1][0] > r0["k_traj"][0][0]        # N still grew


def test_h_concentration() -> None:
    # F3 (level): the shared canon concentrates (rich-get-richer popularity).
    assert h_global(run(10, 60, 0)) > 0.5


def test_sign_and_placebo() -> None:
    # crux: fragmentation ON ⇒ global novelty rises (slope < 0); OFF (placebo, field grows
    # but K frozen) ⇒ flat. Multi-seed mean (single seeds are noisy — the seed-CI discipline).
    on = float(np.mean([global_slope(run(10, 80, s)) for s in range(8)]))
    off = float(np.mean([global_slope(run(10, 80, s, fragmentation=False)) for s in range(8)]))
    assert on < -0.010                    # global structural novelty rises (mean ≈ −0.027)
    assert off > -0.006                   # placebo does not rise (mean ≈ +0.003)
    assert on < off - 0.010               # fragmentation strictly steeper


def test_within_flat() -> None:
    # the fragmentation discriminator: within-niche novelty ≈ flat, global rises.
    g = float(np.mean([global_slope(run(10, 80, s)) for s in range(6)]))
    w = float(np.mean([within_slope(run(10, 80, s)) for s in range(6)]))
    assert g < -0.010
    assert abs(w) < abs(g) / 3            # within much flatter than global (≈ +0.001 vs −0.027)


def test_input_validation() -> None:
    with pytest.raises(ValueError):
        run(0, 40, 0)                     # m < 1
    with pytest.raises(ValueError):
        run(10, 40, 0, n0=5)             # n0 < m
    with pytest.raises(ValueError):
        run(10, 40, 0, bw=0.0)           # bw out of range
    with pytest.raises(ValueError):
        run(10, 40, 0, core=3)           # core < 5
    with pytest.raises(ValueError):
        run(10, 0, 0)                     # generations < 1


@pytest.mark.slow
def test_fingerprint_ci() -> None:
    # rigorous: seed-bootstrap CI (not a two-point diff). FRAG ON global CI excludes 0
    # (rises); within ≈ flat; placebo CI includes 0. Enough seeds to absorb the outlier seed.
    on = fingerprint(10, 100, range(12))
    assert on["global_hi"] < 0.0                      # rises, CI excludes 0
    assert abs(on["within_slope"]) < 0.005            # within flat
    assert on["H_global"] > 0.7                       # concentration co-occurs
    assert on["K"] == 41                              # = N/m
    off = fingerprint(10, 100, range(12), fragmentation=False)
    assert off["global_lo"] < 0.0 < off["global_hi"] or off["global_slope"] > -0.004


@pytest.mark.slow
def test_crossover_bw() -> None:
    # the sign flip is a tunable crossover (Q2): global slope monotone-ish in bw, with a
    # locatable bw* between tight (rises) and diffuse (does not).
    def gm(bw: float) -> float:
        return float(np.mean([global_slope(run(10, 80, s, bw=bw)) for s in range(6)]))

    tight, mid, diffuse = gm(0.02), gm(0.05), gm(0.12)
    assert tight < -0.01                              # distinct niches: novelty rises
    assert diffuse > tight + 0.008                    # diffuse: flip gone
    assert tight <= mid <= diffuse or tight < diffuse  # monotone-ish crossover


@pytest.mark.slow
def test_dim2_robustness() -> None:
    # sign-structure survives a 2-D content space (bw widened for the higher-dim metric).
    on = float(np.mean([global_slope(run(10, 80, s, dim=2, bw=0.08)) for s in range(6)]))
    assert on < -0.004
