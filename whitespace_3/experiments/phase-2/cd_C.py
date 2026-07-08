"""Phase 2 · Experiment C, the κ-half — the CD (consolidation–disruption) index on the
attachment model (``channel.py``). Tests whether conformity (κ) drives **consolidation**
(CD ↓) — the model analog of Park–Leahey–Funk's "disruption is declining." The τ-half
(atypicality ↑, fragmentation) is A/B′; the reconciliation is these two orthogonal channels.

Run: ``uv run python experiments/phase-2/cd_C.py`` (seeded, deterministic).
"""

from __future__ import annotations

import numpy as np

from whitespace3.channel import run
from whitespace3.measures import cd_index

KW = dict(c0=5, f=0.6, epsilon=0.3, b=0.5, generations=80, mode="targeted", alpha=0.15)


def _mean_cd(res: dict) -> float:
    return float(np.nanmean(cd_index(res["prereqs"], min_citers=3)))


def _cd_birth_slope(res: dict) -> float:
    cd = cd_index(res["prereqs"], min_citers=3)
    birth = np.asarray(res["birth"], dtype=float)
    m = ~np.isnan(cd)
    return float(np.polyfit(birth[m], cd[m], 1)[0]) if int(m.sum()) >= 30 else float("nan")


def main() -> None:
    print("=" * 64)
    print("C · κ-half — CD index on channel.py (the attachment channel)")
    print("κ (conformity) ⇒ consolidation ⇒ CD should FALL with λ and over birth-time")
    print("=" * 64)
    cds = {}
    for lam in (0.0, 0.25, 0.5, 1.0):
        vals = [_mean_cd(run(120, seed=s, lam=lam, **KW)) for s in range(4)]
        cds[lam] = float(np.mean(vals))
        tag = "(disruptive)" if cds[lam] > 0 else "(consolidating)"
        print(f"  λ={lam:>4}: mean CD = {cds[lam]:+.4f}   {tag}")
    drop = cds[0.0] - cds[1.0]
    tag = "CD falls with κ ✓" if drop > 0 else "no κ-consolidation"
    print(f"  ΔCD (λ:0→1) = {-drop:+.4f}   {tag}")

    slopes = [_cd_birth_slope(run(120, seed=s, lam=0.5, **KW)) for s in range(4)]
    sl = float(np.nanmean(slopes))
    print(f"  CD-vs-birth slope (λ=0.5) = {sl:+.5f}   "
          f"{'CD falls over time ✓ (Park analog)' if sl < 0 else 'no time-decline'}")


if __name__ == "__main__":
    main()
