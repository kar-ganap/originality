"""Conviction audit (step 0) — is `cv_predictor.predict()`'s mean-field crossover λ* LOAD-BEARING,
or is a trivial constant λ* just as good?

`predict()` computes λ* = the conformity where ∂ln V*/∂ln N = 0 for the mean-field
`V*=ε·N^{−λ}·P(N)` (`analytics.v_star_meanfield`). This audit compares that mean-field λ*(f) against
the SIMULATION's λ*(f) — `innovation.run`, `kappa_mode="scaling"` (the reduced-form the mean-field
approximates) — across fidelity f, on the SAME N-grid (apples-to-apples): does the mean-field track
the sim's λ*, and does it beat a constant-λ* baseline? Free (CPU).
Run from whitespace_3/: uv run python experiments/cv_predictor_audit.py
"""

from __future__ import annotations

import numpy as np

from whitespace3.analytics import v_star_meanfield
from whitespace3.conformity import locate_lambda_star
from whitespace3.innovation import run as innov_run

NS = [10, 30, 100]
FS = [0.15, 0.25, 0.40, 0.55, 0.70]
LAMS = [0.0, 0.05, 0.10, 0.20, 0.40]
MODEL = dict(c0=5, epsilon=0.4, b=0.4, generations=40, persistence=2)
SEEDS = range(6)
BURN = 22


def meanfield_lambda_star(f: float, eps: float, ns: list[int] = NS) -> float:
    """What predict() computes: the λ where the OLS slope of log V* on log N crosses 0."""
    ln_n = np.log(np.asarray(ns, dtype=float))

    def slope(lam: float) -> float:
        v = np.array([v_star_meanfield(n, lam, eps, f) for n in ns])
        return float(np.polyfit(ln_n, np.log(v), 1)[0]) if np.all(v > 0) else float("nan")

    grid = np.linspace(0.0, 0.5, 201)
    s = np.array([slope(x) for x in grid])
    for i in range(1, grid.size):
        if np.isfinite(s[i]) and s[i] <= 0.0 < s[i - 1]:
            return float(grid[i - 1] + (0 - s[i - 1]) * (grid[i] - grid[i - 1]) / (s[i] - s[i - 1]))
    return float("nan")


def main() -> None:
    print("f      mean-field λ*    sim λ* (innovation.run, scaling)")
    rows: list[tuple[float, float, float | None]] = []
    for f in FS:
        mf = meanfield_lambda_star(f, MODEL["epsilon"])
        sim = locate_lambda_star(NS, LAMS, seeds=SEEDS, burn_in=BURN, metric="V",
                                 run_fn=innov_run, kappa_mode="scaling", f=f, **MODEL)
        ls = sim["lambda_star"]
        rows.append((f, mf, ls))
        print(f"{f:<6} {mf:+.4f}          {'none (no crossover)' if ls is None else f'{ls:+.4f}'}")

    valid = [(f, mf, s) for f, mf, s in rows if s is not None and np.isfinite(mf)]
    if len(valid) < 2:
        print("\nToo few defined sim λ* to compare — the crossover itself is fragile across f.")
        return
    sim_a = np.array([s for _, _, s in valid])
    mf_a = np.array([mf for _, mf, _ in valid])
    const = float(np.mean(sim_a))
    mae_mf = float(np.mean(np.abs(mf_a - sim_a)))
    mae_const = float(np.mean(np.abs(const - sim_a)))
    mae_zero = float(np.mean(np.abs(sim_a)))
    print(f"\nsim λ* over the defined range: {sim_a.min():.3f}–{sim_a.max():.3f} "
          f"(spread {sim_a.max() - sim_a.min():.3f}; constant baseline = {const:.3f})")
    print(f"  MAE(mean-field vs sim) = {mae_mf:.4f}")
    print(f"  MAE(constant {const:.3f} vs sim) = {mae_const:.4f}")
    print(f"  MAE(λ*=0 vs sim)        = {mae_zero:.4f}")
    beats = mae_mf < mae_const
    tag = "LOAD-BEARING" if beats else "NOT load-bearing (a constant is as good)"
    print(f"\nVERDICT: predict() {'BEATS' if beats else 'does NOT beat'} a constant λ* ⇒ {tag}.")
    print("Read: tracks the sim's fidelity-dependence (beats a constant) ⇒ directional predictor;")
    print("undershoots + N-grid-dependent ⇒ use the sim for exact λ*. AI = the next test.")


if __name__ == "__main__":
    main()
