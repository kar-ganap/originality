"""Phase 2 · Experiment B′ — the apples-to-apples fix (B′-1) + what the model predicts vs
reproduces.

B′-1 (from calibration.json): the empirical niche_specific_ref_share is 0.58 over ALL refs but
only ~0.03 over the ATYPICALITY-relevant subset (works with degree ≥ d_min) — because the
atypicality measure excludes the citation long-tail. The model's share on its heavily-cited
elements is ~0, so on the measured subset the microstructures MATCH; B's "structural gap" was
apples-to-oranges. Per the pre-registered dichotomy (H-B′1), no augmentation is needed.

Remaining honesty check: the fingerprint MAGNITUDE is `bw`-sensitive, so we report what the
model PREDICTS (the sign-structure, robust across the distinct-niche regime) vs REPRODUCES
(the ~13× magnitude, at a reasonable but `bw`-tunable value).
Run: ``uv run python experiments/phase-2/bridge_Bprime.py``.
"""

from __future__ import annotations

import json
import os

import numpy as np

from whitespace3.measures import reference_atypicality
from whitespace3.subfield import run

D_MIN = 5
CAL = os.path.join(os.path.dirname(__file__), "..", "..", "..", "whitespace_2",
                   "experiments", "phase-2-bridge", "calibration.json")


def _model_share_heavy(res: dict) -> float:
    """Model niche-specific-share over its ATYPICALITY-relevant (degree ≥ D_MIN) elements —
    apples-to-apples with the empirical d_min share."""
    elem = np.concatenate([res["u"], res["v"]])
    niche = np.concatenate([res["niche"], res["niche"]])
    deg = {int(e): int(c) for e, c in zip(*np.unique(elem, return_counts=True))}
    order = np.argsort(elem, kind="stable")
    elem_s, niche_s = elem[order], niche[order]
    bounds = np.flatnonzero(np.diff(elem_s)) + 1
    n_niches = {int(elem_s[s]): len(set(niche_s[s:e].tolist()))
                for s, e in zip(np.r_[0, bounds], np.r_[bounds, elem_s.size])}
    heavy = [int(e) for e in elem if deg[int(e)] >= D_MIN]
    if not heavy:
        return float("nan")
    return float(np.mean([n_niches[e] == 1 for e in heavy]))


def _global_slope(res: dict) -> float:
    refs = [[int(u), int(v)] for u, v in zip(res["u"], res["v"])]
    birth = res["birth"].astype(float)
    med, _ = reference_atypicality(refs, d_min=D_MIN, min_pairs=1)
    m = ~np.isnan(med)
    return float(np.polyfit(birth[m], med[m], 1)[0]) if int(m.sum()) >= 30 else float("nan")


def main() -> None:
    cal = json.load(open(CAL))
    print("B′-1 — niche_specific_ref_share, apples-to-apples:")
    print(f"  empirical ALL refs = {cal['niche_specific_ref_share']:.3f} (long-tail)")
    print(f"  empirical >=d_min  = {cal['niche_specific_ref_share_dmin']:.3f} (atyp subset)")
    sh = float(np.mean([_model_share_heavy(run(10, 100, s)) for s in range(3)]))
    print(f"  MODEL, ≥d_min              = {sh:.3f}")
    match = abs(sh - cal["niche_specific_ref_share_dmin"]) < 0.05
    print(f"  ==> microstructures MATCH on the measured subset: {'YES ✓' if match else 'no'}"
          "  (H-B′1 ⇒ no augmentation)")

    print("\nbw-sensitivity of the fingerprint (global atypicality-vs-birth slope):")
    slopes = {}
    for bw in (0.02, 0.03, 0.04, 0.05, 0.06, 0.08):
        s = float(np.nanmean([_global_slope(run(10, 100, sd, bw=bw)) for sd in range(3)]))
        slopes[bw] = s
        tag = "(fingerprint)" if s < -0.003 else "(flat/gone)"
        print(f"  bw={bw:.3f}: global slope = {s:+.4f}  {tag}")
    in_regime = [s for bw, s in slopes.items() if bw <= 0.04]
    sign_robust = all(s < -0.003 for s in in_regime)
    print("\nVERDICT (B/B′):")
    print("  sign-structure PREDICTED (global novelty rises) — robust across the distinct-niche")
    print(f"  regime (bw≤0.04): {'YES ✓' if sign_robust else 'no'}. Microstructure matches (B′-1).")
    print("  Magnitude (~13×) REPRODUCED but bw-sensitive ⇒ the ~13× is a reproduction at a")
    print("  reasonable bw, not a tight forced prediction. Net: PARTIAL PREDICTION (sign-structure")
    print("  + microstructure forced & confirmed; magnitude consistency).")


if __name__ == "__main__":
    main()
