"""Phase 2 · Experiment A — the measurement bridge.

Run the ABM's content channel (``subfield.run``, the τ/fragmentation model) through WS2's
**identical** atypicality pipeline (vendored in ``whitespace3.measures``) and check it yields
the fragmentation fingerprint *apples-to-apples* with the empirical: global co-reference
atypicality **falls** with birth-time (median-z↓ = novelty↑) while the **within-subfield**
recomputation stays flat. This is the first model-vs-data comparison under one measurement.

Run: ``uv run python experiments/phase-2/bridge_A.py`` (seeded, deterministic). ``d_min=5``
is model-scale (vs WS2's 20 on real data); the *procedure* is identical, only the
degree floor adapts to the model's smaller vocabulary — logged, not hidden.

Empirical target (WS2 Phase 2.4): global atypicality slope `−0.64`, within `−0.05` (≈13×).
H-A pass: model within/global slope-ratio ≥ ~5× (order-of-magnitude).
"""

from __future__ import annotations

import numpy as np

from whitespace3.measures import reference_atypicality, within_group_atypicality
from whitespace3.subfield import run

D_MIN = 5


def _slope(birth: np.ndarray, z: np.ndarray) -> tuple[float, int]:
    m = ~np.isnan(z)
    if int(m.sum()) < 30:
        return float("nan"), 0
    return float(np.polyfit(birth[m], z[m], 1)[0]), int(m.sum())


def main() -> None:
    gs: list[float] = []
    ws: list[float] = []
    for seed in range(4):
        r = run(10, 100, seed)                       # the confirmed fragmenting config
        refs = [[int(u), int(v)] for u, v in zip(r["u"], r["v"])]
        birth = r["birth"].astype(float)
        med_g, _ = reference_atypicality(refs, d_min=D_MIN, min_pairs=1)
        med_w = within_group_atypicality(refs, r["niche"], d_min=D_MIN, min_pairs=1)
        sg, ng = _slope(birth, med_g)
        sw, nw = _slope(birth, med_w)
        gs.append(sg)
        ws.append(sw)

    g, w = float(np.nanmean(gs)), float(np.nanmean(ws))
    print("=" * 68)
    print("EXPERIMENT A — the ABM through WS2's identical atypicality pipeline")
    print("=" * 68)
    print(f"  global  atypicality-vs-birth slope = {g:+.4f}   (want < 0 = novelty↑)")
    print(f"  within  atypicality-vs-birth slope = {w:+.4f}   (want ~ 0 = flat)")
    ratio = abs(g) / abs(w) if abs(w) > 1e-6 else float("inf")
    print(f"  within/global ratio ≈ {ratio:.1f}×   (empirical ≈ 13×; H-A pass ≥ ~5×)")
    fp = g < 0 and abs(w) < abs(g) / 5
    print(f"  ==> fingerprint under the WS2 measure: {'YES ✓' if fp else 'no'}")


if __name__ == "__main__":
    main()
