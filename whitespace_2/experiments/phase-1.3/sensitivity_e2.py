"""E2 sensitivity sweep — headline female_share vs bias-correction kernel CIs.

The E2 escape trigger (Phase 1.3 plan §3) fires if the headline statistic
moves >30% when the bias-correction parameters are perturbed within their
5a Wilson CIs. Here the headline statistic is the per-cell female share on
the headline cells (recent CS, latin). We draw K kernels via
``perturb_row_normalized``, re-derive each author's corrected female /
assigned mass IN MEMORY (no parquet round-trips), re-aggregate the cell,
and report the relative spread of female_share against the 30% threshold.

Usage:
  uv run python experiments/phase-1.3/sensitivity_e2.py \
      --rundir experiments/phase-1.3/run-1M-v3 --k 200
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

from whitespace2.demographics import (
    _canonicalize_gender,
    perturb_row_normalized,
    tag_script_region,
)

_CONFIDENCE_GATE = 0.8
_E2_REL_CHANGE_MAX = 0.30
# Headline cells: the largest recent-CS latin cells.
_HEADLINE = [(2020, "cs", "latin"), (2024, "cs", "latin"),
             (2025, "cs", "latin")]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rundir", required=True, type=Path)
    ap.add_argument("--k", type=int, default=200)
    ap.add_argument("--seed", type=int, default=20260630)
    args = ap.parse_args()

    rundir: Path = args.rundir
    matrix = json.loads((rundir / "confusion-matrix.json").read_text())

    # Per-author pre-correction features (region, gg_canon, low_conf) plus
    # the identity female/assigned mass for confident authors.
    pa = pq.read_table(
        str(rundir / "per-author.parquet"),
        columns=["author_id", "author_first_name", "gender",
                 "gender_probability", "gg_label"],
    ).to_pandas()
    pa["region"] = pa["author_first_name"].map(
        lambda n: tag_script_region(n),
    ).fillna("unknown")
    pa["gg_canon"] = pa["gg_label"].map(_canonicalize_gender)
    pa["low_conf"] = pa["gender_probability"].fillna(0.0) < _CONFIDENCE_GATE
    g = pa["gender"].map(_canonicalize_gender)
    pa["id_female"] = (g == "female").astype(float)
    pa["id_assigned"] = ((g == "male") | (g == "female")).astype(float)

    # Cell membership (distinct authors) for the headline cells.
    auth = pq.read_table(
        str(rundir / "authorships.parquet"),
        columns=["paper_id", "publication_year", "author_id"],
    ).to_pandas()
    field = pq.read_table(
        str(rundir / "paper-field.parquet"),
        columns=["paper_id", "primary_field"],
    ).to_pandas()
    joined = auth.merge(
        pa[["author_id", "region", "gg_canon", "low_conf",
            "id_female", "id_assigned"]],
        on="author_id", how="inner",
    ).merge(field, on="paper_id", how="inner").rename(
        columns={"publication_year": "year", "primary_field": "field"},
    )

    def cell_members(year: int, fld: str, region: str):  # noqa: ANN202
        sub = joined[(joined["year"] == year) & (joined["field"] == fld)
                     & (joined["region"] == region)]
        return sub.drop_duplicates(subset=["author_id"])

    def female_share(members, kernel) -> float:  # noqa: ANN001
        lc = members["low_conf"].to_numpy()
        reg = members["region"].to_numpy()
        gg = members["gg_canon"].to_numpy()
        idf = members["id_female"].to_numpy()
        ida = members["id_assigned"].to_numpy()
        fem = idf.copy()
        asg = ida.copy()
        for i in np.where(lc)[0]:
            row = kernel.get(reg[i], {}).get("row_normalized", {}).get(gg[i])
            if row and (row.get("male", 0) + row.get("female", 0)
                        + row.get("unknown", 0)) > 0:
                fem[i] = row.get("female", 0.0)
                asg[i] = row.get("male", 0.0) + row.get("female", 0.0)
            # else: keep identity (uncorrectable)
        tot = float(asg.sum())
        return float(fem.sum() / tot) if tot > 0 else 0.0

    rng = np.random.default_rng(args.seed)
    results = {}
    for (year, fld, region) in _HEADLINE:
        members = cell_members(year, fld, region)
        base = female_share(members, matrix)
        draws = [female_share(members, perturb_row_normalized(matrix, rng))
                 for _ in range(args.k)]
        lo, hi = float(np.min(draws)), float(np.max(draws))
        rel = (hi - lo) / base if base > 0 else 0.0
        results[f"{year}-{fld}-{region}"] = {
            "n": int(len(members)), "base_female_share": round(base, 4),
            "sweep_min": round(lo, 4), "sweep_max": round(hi, 4),
            "abs_spread": round(hi - lo, 4),
            "rel_spread": round(rel, 4),
            "E2_fires": rel > _E2_REL_CHANGE_MAX,
        }
        print(f"{year} {fld} {region}: base={base:.4f} "
              f"sweep=[{lo:.4f}, {hi:.4f}] rel_spread={rel:.3f} "
              f"{'E2 FIRES' if rel > _E2_REL_CHANGE_MAX else 'ok'}")

    out = {"k": args.k, "threshold_rel_change": _E2_REL_CHANGE_MAX,
           "cells": results}
    (rundir.parent / "v3-sensitivity-e2.json").write_text(
        json.dumps(out, indent=2),
    )
    print("\nE2 fires anywhere:",
          any(c["E2_fires"] for c in results.values()))


if __name__ == "__main__":
    main()
