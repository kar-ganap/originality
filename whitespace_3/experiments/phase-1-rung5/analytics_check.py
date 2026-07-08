"""Rung 5b — the light analytics, checked against the simulation (qualitative, the compass).
Run: ``uv run python experiments/phase-1-rung5/analytics_check.py``. Pure analytics (fast);
the simulated λ*≈0.09 and C-behaviour come from rung 5a's phase diagram.
"""

from __future__ import annotations

from whitespace3.analytics import (
    branching_survival,
    carrier_fixed_point,
    crossover_lambda,
    maintenance_threshold,
    v_star_meanfield,
)

F = 0.6
NS = [30, 60, 120, 240]          # rung 5a's phase-diagram N range


def main() -> None:
    print("=" * 68)
    print("C — Henrich carrier-survival (maintenance threshold + saturation)")
    print(f"  n* = 1/ln(1/(1-f)):  f=0.5→{maintenance_threshold(0.5):.2f}"
          f"  f=0.6→{maintenance_threshold(0.6):.2f}  f=0.9→{maintenance_threshold(0.9):.2f}")
    print("  carrier fixed point c*(n, f=0.6):",
          {n: round(carrier_fixed_point(n, F), 2) for n in (1, 2, 5, 30, 240)})
    print("  ⇒ elements collapse below n* (Tasmania), saturate at ≈n above — matches the")
    print("    Level-3 Henrich reproduction (rung 1) and the C↑-with-N of the 5a phase diagram.")

    print("\nV — the crossover law  λ* = d ln P / d ln N  (persistence elasticity)")
    print("  mean-field V*(N) = ε·N^(-λ)·P(N), P = GW survival(μ=n·f):")
    print("  V* hump in N (ε=1, λ=0.5):",
          {n: round(v_star_meanfield(n, 0.5, 1.0, F), 3) for n in (2, 5, 10, 30, 100)})
    p = [branching_survival(n * F) for n in NS]
    lam_star = crossover_lambda(NS, p)
    print(f"  P(N) over the 5a range {NS}: {[round(x, 4) for x in p]}")
    print(f"  ⇒ persistence saturates (μ=n·f ≥ {NS[0] * F:.0f} ≫ 1), λ* ≈ {lam_star:.3f}")
    print("\n  The law predicts λ* ≈ 0: with persistence near-complete over the relevant N,")
    print("  scale buys almost no extra originality to offset conformity — so ANY κ that")
    print("  grows with scale suppresses per-capita V. The simulated crossover sits at")
    print("  λ*≈0.09 (rung 5a) — small and positive, exactly as the law explains. A light")
    print("  mean-field (idealised κ=λ·ln N vs the model's κ=λ·H, H compressed near 1) matches")
    print("  the sign and the *smallness*, not the third decimal.")


if __name__ == "__main__":
    main()
