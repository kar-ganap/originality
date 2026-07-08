"""Rung 5a — the reconciliation deliverable (reproducible).

Regenerates the WS3 phase diagram + the two headline claims, from the committed model
(``whitespace3.channel.run``, well-mixed, uniform-κ). Run (the figure needs the ``plot``
extra): ``uv run --extra plot python experiments/phase-1-rung5/phase_diagram.py`` → writes
``phase-diagram.png`` and prints the numbers. All seeded, deterministic.

Panels:
  A. **The crossover.** ∂V*/∂logN vs λ (seed-bootstrap CI): a locatable ``λ*`` separating a
     **V-favouring** region (λ<λ*, per-capita V rises/flat in N) from a **C-favouring** one
     (λ>λ*, V falls in N) — Core Claim `cc:wwe` + the phase diagram of `cc:reconcile`.
  B. **Same lever, opposite signs.** C↑ with N (Henrich, redundancy protects depth) while
     V↓ with N (WWE) in the crossover regime — the reconciliation's opposite-sign column.
  C. **Pareto / selective isolation.** Shielding a subgroup from κ keeps its V^struct high
     while global C is preserved (the non-strict-trade-off, `cc:reconcile`).
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import os

import matplotlib.pyplot as plt
import numpy as np

from whitespace3.channel import run
from whitespace3.conformity import logN_slope_ci, steady_grid

NS = [30, 60, 120, 240]
SEEDS = range(6)
LAMBDAS = [0.0, 0.15, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0]
KW = dict(c0=5, f=0.6, epsilon=0.3, b=0.5, generations=60, alpha=0.15, mode="uniform")
OUT = os.path.join(os.path.dirname(__file__), "phase-diagram.png")


def _slope(metric: str, lam: float) -> dict[str, float]:
    g = steady_grid(NS, lam, seeds=SEEDS, burn_in=30, metric=metric, run_fn=run, **KW)
    return logN_slope_ci(NS, g)


def _cross_zero(lams: list[float], pts: list[float]) -> float:
    """linear-interpolate the λ where the V-slope crosses 0 (the crossover λ*)."""
    for i in range(len(lams) - 1):
        if pts[i] >= 0.0 > pts[i + 1]:
            f = pts[i] / (pts[i] - pts[i + 1])
            return lams[i] + f * (lams[i + 1] - lams[i])
    return float("nan")


def main() -> None:
    v = [_slope("V", lam) for lam in LAMBDAS]
    c = [_slope("C", lam) for lam in LAMBDAS]
    vpt = [x["point"] for x in v]
    lam_star = _cross_zero(LAMBDAS, vpt)
    print("=" * 70)
    print("A. THE CROSSOVER — ∂V*/∂logN vs λ (uniform κ); λ* = sign flip")
    for lam, x in zip(LAMBDAS, v):
        reg = "V-favouring" if x["point"] > 0 else "C-favouring"
        print(f"  λ={lam:>4}: V-slope={x['point']:+.4f} [{x['lo']:+.4f},{x['hi']:+.4f}]  {reg}")
    print(f"  ==> λ* ≈ {lam_star:.2f}")
    print("\nB. SAME LEVER, OPPOSITE SIGNS (in N) — C↑ while V↓ beyond λ*")
    for lam, xc, xv in zip(LAMBDAS, c, v):
        print(f"  λ={lam:>4}: C-slope={xc['point']:+.3f}  V-slope={xv['point']:+.4f}"
              f"   {'opposite ✓' if xc['point'] > 0 > xv['point'] else ''}")

    # Panel C — Pareto via selective isolation
    isos = [0.0, 0.1, 0.25, 0.5]
    vi, vc_, cc = [], [], []
    for iso in isos:
        ri = [run(120, 5, 0.6, 0.3, 0.5, 60, s, lam=0.5, mode="targeted", alpha=0.15,
                  isolated_frac=iso) for s in SEEDS]
        vi.append(float(np.mean([np.nanmean(r["Vstruct_iso"][30:]) for r in ri])))
        vc_.append(float(np.mean([np.nanmean(r["Vstruct_conf"][30:]) for r in ri])))
        cc.append(float(np.mean([np.nanmean(r["C"][30:]) for r in ri])))
    print("\nC. PARETO / SELECTIVE ISOLATION — subgroup V^struct high, global C preserved")
    for iso, a, b_, cval in zip(isos, vi, vc_, cc):
        print(f"  ι={iso:>4}: Vstruct_iso={a:.3f}  Vstruct_conf={b_:.3f}  C={cval:.1f}")

    # ── figure ──
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))
    lo = [x["lo"] for x in v]
    hi = [x["hi"] for x in v]
    ax[0].axhline(0, color="k", lw=0.8)
    ax[0].fill_between(LAMBDAS, lo, hi, alpha=0.2, color="C0")
    ax[0].plot(LAMBDAS, vpt, "o-", color="C0")
    if not np.isnan(lam_star):
        ax[0].axvline(lam_star, ls="--", color="C3", label=f"λ*≈{lam_star:.2f}")
    ax[0].set(xlabel="λ (conformity scaling)", ylabel="∂V*/∂logN",
              title="A. The crossover (V-favouring → C-favouring)")
    ax[0].legend()
    axb = ax[1]
    axb.plot(LAMBDAS, [x["point"] for x in c], "s-", color="C2", label="∂C*/∂logN")
    axb.set_ylabel("∂C*/∂logN", color="C2")
    axr = axb.twinx()
    axr.plot(LAMBDAS, vpt, "o-", color="C0", label="∂V*/∂logN")
    axr.axhline(0, color="C0", lw=0.6, ls=":")
    axr.set_ylabel("∂V*/∂logN", color="C0")
    axb.set(xlabel="λ", title="B. Same lever, opposite signs (C↑, V↓)")
    ax[2].plot(isos, vi, "o-", label="V^struct isolated")
    ax[2].plot(isos, vc_, "s-", label="V^struct conformist")
    ax[2].plot(isos, [x / max(cc) * max(vi) for x in cc], "^--", color="gray",
               label="C (rescaled, ~flat)")
    ax[2].set(xlabel="ι (isolated fraction)", ylabel="per-capita V^struct",
              title="C. Pareto: selective isolation")
    ax[2].legend()
    fig.tight_layout()
    fig.savefig(OUT, dpi=110)
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
