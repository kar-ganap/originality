"""Phase 2 · Experiment B (B-2/B-3) — off-trend calibration → forced prediction.

The empirical niche-distinctiveness (``niche_specific_ref_share`` from B-1) is a *structural*
statistic, not the novelty trend. Calibrate the model's ``bw`` so its niche-specific-ref-share
matches the empirical (~0.58), then ask whether the calibrated model **predicts** the observed
within/global novelty ratio (~13×). If it lands near 13× with ``bw`` fixed *only* by structure,
that is forced prediction; if it's only in the ballpark, we report **consistency, not
prediction** (the pre-registered honest-null).

Run: ``uv run python experiments/phase-2/bridge_B.py`` (reads WS2's calibration.json; seeded).
"""

from __future__ import annotations

import json
import os

import numpy as np

from whitespace3.measures import reference_atypicality, within_group_atypicality
from whitespace3.subfield import run

D_MIN = 5
CAL = os.path.join(os.path.dirname(__file__), "..", "..", "..", "whitespace_2",
                   "experiments", "phase-2-bridge", "calibration.json")


def _niche_specific_share(res: dict) -> float:
    """Fraction of ref-instances whose cited element is used by exactly ONE niche (the model
    analog of the empirical niche_specific_ref_share)."""
    niche = np.concatenate([res["niche"], res["niche"]])
    elem = np.concatenate([res["u"], res["v"]])
    order = np.argsort(elem, kind="stable")
    elem_s, niche_s = elem[order], niche[order]
    bounds = np.flatnonzero(np.diff(elem_s)) + 1
    n_niches = {int(elem_s[s]): len(set(niche_s[s:e].tolist()))
                for s, e in zip(np.r_[0, bounds], np.r_[bounds, elem_s.size])}
    return float(np.mean([n_niches[int(e)] == 1 for e in elem]))


def _slope(birth: np.ndarray, z: np.ndarray) -> float:
    m = ~np.isnan(z)
    if int(m.sum()) < 30:
        return float("nan")
    return float(np.polyfit(birth[m], z[m], 1)[0])


def _novelty_ratio(res: dict) -> float:
    refs = [[int(u), int(v)] for u, v in zip(res["u"], res["v"])]
    birth = res["birth"].astype(float)
    med_g, _ = reference_atypicality(refs, d_min=D_MIN, min_pairs=1)
    med_w = within_group_atypicality(refs, res["niche"], d_min=D_MIN, min_pairs=1)
    sg, sw = _slope(birth, med_g), _slope(birth, med_w)
    return abs(sg) / abs(sw) if abs(sw) > 1e-6 else float("inf")


def main() -> None:
    cal = json.load(open(CAL))
    target = cal["niche_specific_ref_share"]
    emp_ratio = 13.0
    print(f"empirical: niche_specific_ref_share = {target:.3f}  (novelty ratio ≈ {emp_ratio:.0f}×)")
    print(f"{'bw':>6} | {'niche-specific share':>20} | {'novelty ratio':>13}")
    print("-" * 48)
    rows = []
    for bw in (0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.12):
        shares, ratios = [], []
        for s in range(3):
            r = run(10, 100, s, bw=bw)
            shares.append(_niche_specific_share(r))
            ratios.append(_novelty_ratio(r))
        sh, ra = float(np.mean(shares)), float(np.nanmean(ratios))
        rows.append((bw, sh, ra))
        print(f"{bw:>6.3f} | {sh:>20.3f} | {ra:>12.1f}×")

    max_share = float(max(r[1] for r in rows))
    print("-" * 48)
    if max_share < 0.5 * target:
        # H-B honest-null: the calibration statistic does not map to bw.
        print(f"STRUCTURAL GAP: model niche-specific-share (max {max_share:.3f}) ≪ empirical "
              f"{target:.3f}.")
        print("  The model fragments via niche-specific RECOMBINATION of a SHARED canon")
        print("  (elements cited by many niches); the data has distinct subfield vocabularies")
        print("  + a citation long-tail, so niche_specific_ref_share is long-tail-confounded")
        print("  and does NOT pin bw. (A already showed the model reproduces the ratio,")
        print("  ~15.6× ≈ 13×, at bw≈0.03 — the right MAGNITUDE, in the distinct-niche regime.)")
        print("  H-B ⇒ CONSISTENCY, not forced prediction (pre-registered honest-null):")
        print("  the fingerprint magnitude matches, but bw is not cleanly pinned off-trend by")
        print("  this minimal model's structural statistics.")
    else:
        shs = np.array([r[1] for r in rows])
        ras = np.array([r[2] for r in rows])
        order = np.argsort(shs)
        bw_star = float(np.interp(target, shs[order], np.array([r[0] for r in rows])[order]))
        ratio_star = float(np.interp(target, shs[order], ras[order]))
        print(f"calibrated bw*≈{bw_star:.3f} → ratio ≈ {ratio_star:.1f}× (emp {emp_ratio:.0f}×)")
        v = ("FORCED PREDICTION ✓" if 0.5 * emp_ratio <= ratio_star <= 2 * emp_ratio
             else "CONSISTENCY (right regime)")
        print(f"  H-B ⇒ {v}")


if __name__ == "__main__":
    main()
