"""Phase 2.3 escalation — the aggregate (whole-field) semantic trend, 3 families.

Does the Phase-2.2 "semantic frontier widens" claim survive adding SPECTER2 as a
3rd family? Recomputes, for CS and Physics over 1970–2023, the per-year
mean-pairwise-cosine for SciNCL, Qwen3, SPECTER2 — and judges each with the
CORRECT tools (per `tasks/lessons.md`): permutation-slope significance + the
ABSOLUTE change over the window, NOT just the ill-conditioned standardized σ
(SPECTER2's near-flat series inflate σ). Reports all three per family so a
"reversal" can be read as real-and-significant vs near-flat noise.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from whitespace2.divergence import permutation_slope_test, standardized_effect
from whitespace2.semantic_metrics import mean_pairwise_cosine_distance

_YEAR_MIN, _YEAR_MAX = 1970, 2023
_N_YEAR_MIN = 30
_MPC_SAMPLE = 2000
_SEED = 46


def _per_year_mpc(rows, yrs, arr, y_min, y_max):
    rng = np.random.default_rng(_SEED)
    ys, vals = [], []
    for y in range(y_min, y_max + 1):
        cell = rows[yrs[rows] == y]
        if cell.size < _N_YEAR_MIN:
            continue
        idx = cell if cell.size <= _MPC_SAMPLE else rng.choice(
            cell, size=_MPC_SAMPLE, replace=False)
        idx = np.sort(idx)
        vals.append(mean_pairwise_cosine_distance(
            np.asarray(arr[idx], dtype=np.float32)))
        ys.append(y)
    return np.array(ys, dtype=float), np.array(vals, dtype=float)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--embed-dir", required=True, type=Path)
    ap.add_argument("--specter2-dir", required=True, type=Path)
    args = ap.parse_args()

    meta = pd.read_parquet(args.embed_dir / "metadata.parquet")
    fields = meta["field"].to_numpy()
    yrs = meta["year"].to_numpy().astype(int)
    embeds = {
        "scincl": np.load(args.embed_dir / "scincl-vectors.npy", mmap_mode="r"),
        "qwen3": np.load(args.embed_dir / "qwen3-vectors.npy", mmap_mode="r"),
        "specter2": np.load(
            args.specter2_dir / "specter2-vectors.npy", mmap_mode="r"),
    }

    out = {}
    for field in ("cs", "physics"):
        rows = np.nonzero(fields == field)[0]
        print(f"\n===== {field.upper()} (n={len(rows):,}) =====")
        print(f"{'family':>9} | {'abs Δ (first→last)':>20} | {'% change':>9} | "
              f"{'σ':>7} | {'perm_p':>8} | dir")
        out[field] = {}
        for name, arr in embeds.items():
            ys, vals = _per_year_mpc(rows, yrs, arr, _YEAR_MIN, _YEAR_MAX)
            if len(ys) < 3:
                continue
            abs_change = float(vals[-1] - vals[0])
            pct = 100.0 * abs_change / vals[0] if vals[0] else 0.0
            sd = standardized_effect(ys, vals)["total_change_sd"]
            perm = permutation_slope_test(ys, vals, n_perm=10_000, seed=_SEED)
            slope = perm["slope"] or 0.0
            direction = ("up" if slope > 0 else "down") if perm[
                "significant"] else "flat/ns"
            out[field][name] = {
                "abs_change": round(abs_change, 4), "pct_change": round(pct, 1),
                "total_change_sd": round(sd, 2) if sd is not None else None,
                "perm_pvalue": round(perm["perm_pvalue"], 4),
                "perm_significant": perm["significant"],
                "first": round(float(vals[0]), 4), "last": round(float(vals[-1]), 4),
                "min": round(float(vals.min()), 4), "max": round(float(vals.max()), 4),
            }
            print(f"{name:>9} | {abs_change:>+20.4f} | {pct:>+8.1f}% | "
                  f"{sd:>+6.2f}σ | {perm['perm_pvalue']:>8.4f} | {direction}"
                  f"{'*' if perm['significant'] else ''}")

    (args.specter2_dir / "aggregate-3family.json").write_text(
        json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
