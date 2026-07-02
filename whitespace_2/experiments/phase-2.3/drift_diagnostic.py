"""Phase 2.3 — is SPECTER2's semantic-trend reversal an early-era drift artifact?

SPECTER2 shows semantic diversity DECLINING (mean −1.35σ) where SciNCL/Qwen3 show
it rising (+2.3σ). SPECTER2 is the documented most-drift-susceptible family
(Phase-0.1 Check 5c: era-match 62.8%, worst of three; H7 audit "drift severe").
If its decline is a pre-1990-drift artifact, restricting the trend window to later
years (dropping the unreliable early era) should attenuate / reverse it.

Recomputes the mean per-subfield semantic trend (SciNCL control + SPECTER2) over
the eligible concept subfields for windows {1970–2023, 1990–2023, 2000–2023}.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from whitespace2.divergence import standardized_effect
from whitespace2.semantic_metrics import mean_pairwise_cosine_distance

_N_YEAR_MIN = 30
_MPC_SAMPLE = 2000
_SEED = 46
_WINDOWS = ((1970, 2023), (1990, 2023), (2000, 2023))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--embed-dir", required=True, type=Path)
    ap.add_argument("--specter2-dir", required=True, type=Path)
    ap.add_argument("--subfield-map", required=True, type=Path)
    ap.add_argument("--metrics", required=True, type=Path,
                    help="3-fam concepts metrics json (for the eligible set)")
    args = ap.parse_args()

    meta = pd.read_parquet(args.embed_dir / "metadata.parquet")
    scincl = np.load(args.embed_dir / "scincl-vectors.npy", mmap_mode="r")
    specter2 = np.load(args.specter2_dir / "specter2-vectors.npy", mmap_mode="r")
    smap = pq.read_table(str(args.subfield_map)).to_pandas()
    key_by_pid = dict(zip(smap["paper_id"], smap["primary_field"], strict=True))
    keys = meta["paper_id"].map(key_by_pid).fillna("").to_numpy().astype(str)
    yrs = meta["year"].to_numpy().astype(int)

    eligible = {r["subfield"] for r in json.loads(
        args.metrics.read_text())["subfields"] if r["eligible"]}

    order = np.argsort(keys, kind="stable")
    keys_s = keys[order]
    uniq, starts = np.unique(keys_s, return_index=True)
    bounds = list(starts) + [len(keys_s)]

    print(f"{'window':>12} | {'SciNCL mean':>12} | {'SPECTER2 mean':>13} | "
          f"{'SPECTER2 frac>0':>15}")
    for (y_min, y_max) in _WINDOWS:
        sc_tr, s2_tr = [], []
        for i, key in enumerate(uniq):
            if key == "" or key not in eligible:
                continue
            rows = order[bounds[i]:bounds[i + 1]]
            yr = yrs[rows]
            rng = np.random.default_rng(_SEED)
            sc_vals, s2_vals, yv = [], [], []
            for y in range(y_min, y_max + 1):
                cell = rows[yr == y]
                if cell.size < _N_YEAR_MIN:
                    continue
                idx = cell if cell.size <= _MPC_SAMPLE else rng.choice(
                    cell, size=_MPC_SAMPLE, replace=False)
                idx = np.sort(idx)
                sc_vals.append(mean_pairwise_cosine_distance(
                    np.asarray(scincl[idx], dtype=np.float32)))
                s2_vals.append(mean_pairwise_cosine_distance(
                    np.asarray(specter2[idx], dtype=np.float32)))
                yv.append(y)
            if len(yv) >= 3:
                ya = np.array(yv, dtype=float)
                sc_tr.append(standardized_effect(
                    ya, np.array(sc_vals))["total_change_sd"])
                s2_tr.append(standardized_effect(
                    ya, np.array(s2_vals))["total_change_sd"])
        sc_tr = np.array([t for t in sc_tr if t is not None])
        s2_tr = np.array([t for t in s2_tr if t is not None])
        print(f"{y_min}-{y_max} | {sc_tr.mean():>+11.2f}σ | "
              f"{s2_tr.mean():>+12.2f}σ | {np.mean(s2_tr > 0):>15.2f}")


if __name__ == "__main__":
    main()
