"""Script-vs-country axis sensitivity (Step 6 sensitivity analysis).

The bias correction (Step 5b) can key on the author's name SCRIPT-region
(the headline) or their COUNTRY (robustness). This compares the two:
build a per-country confusion matrix from the v3 NamSor sample
(``compute_confusion_matrix(region_column="primary_country")``), re-run
``apply_bias_correction(region_axis="country")``, re-aggregate, and diff
the FIELD-LEVEL female-share trend (cs, all regions) against the
script-corrected result.

Confound flagged honestly: the v3 NamSor sample was SCRIPT-stratified, so
the per-country matrix is uneven (some countries get few names). We report
the country-matrix sparsity + how many authors fall through to identity,
so the comparison is read with that caveat. A clean country-axis estimate
would need a country-stratified NamSor sample (fresh quota).

Usage:
  uv run python experiments/phase-1.3/sensitivity_axis.py \
      --rundir experiments/phase-1.3/run-1M-v3
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pyarrow.parquet as pq

from whitespace2.demographics import (
    apply_bias_correction,
    build_cell_coverage_table,
    compute_confusion_matrix,
)


def field_trend(cells_parquet: Path, field: str,
                unit: str = "distinct_authors") -> dict[int, float]:
    """Field-level female_share per year = Σ female / Σ assigned over
    all regions in (year, field)."""
    df = pq.read_table(str(cells_parquet)).to_pandas()
    d = df[(df["unit"] == unit) & (df["field"] == field)]
    g = d.groupby("year")[["sum_p_male", "sum_p_female"]].sum()
    share = g["sum_p_female"] / (g["sum_p_male"] + g["sum_p_female"])
    return {int(y): round(float(v), 4) for y, v in share.items()}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rundir", required=True, type=Path)
    ap.add_argument("--n-bootstrap", type=int, default=200)
    ap.add_argument("--year-min", type=int, default=1970,
                    help="study-window lower bound; the §0 corpus has a "
                         "pre-1970 mis-dated tail (papers back to 1803) of "
                         "tiny degenerate cells")
    ap.add_argument("--year-max", type=int, default=2024,
                    help="compare within the study window; boundary years "
                         "past the corpus window are near-empty / degenerate")
    args = ap.parse_args()
    rd: Path = args.rundir

    # 1. Per-country confusion matrix from the (script-stratified) sample.
    country_matrix = compute_confusion_matrix(
        rd / "namsor-sample.parquet", rd / "per-author.parquet",
        region_column="primary_country",
    )
    n_by_country = {k: v["n_sample"] for k, v in country_matrix.items()}
    n_countries = len(n_by_country)
    n_ge10 = sum(1 for n in n_by_country.values() if n >= 10)
    print(f"country matrix: {n_countries} countries, "
          f"{n_ge10} with n>=10 NamSor names")
    top = sorted(n_by_country.items(), key=lambda kv: -kv[1])[:8]
    print("  top countries by sample:",
          {k: v for k, v in top})

    # 2. Country-axis bias correction.
    cc_pq = rd / "corrected-country.parquet"
    cc = apply_bias_correction(
        rd / "per-author.parquet", cc_pq,
        confusion_matrix=country_matrix, region_axis="country",
    )
    print(f"country-corrected: {cc['n_bias_corrected']:,} of "
          f"{cc['n_authors']:,} authors corrected "
          f"({cc['n_low_conf_uncorrectable']:,} low-conf fell to identity)")

    # 3. Country-axis cells (point sums only; small bootstrap).
    cc_cells = rd / "cells-country.parquet"
    build_cell_coverage_table(
        rd / "authorships.parquet", cc_pq, rd / "paper-field.parquet",
        cc_cells, region_axis="country", n_bootstrap=args.n_bootstrap,
    )

    # 4. Field-level cs female_share trend: script vs country correction.
    script_trend = field_trend(rd / "cells.parquet", "cs")
    country_trend = field_trend(cc_cells, "cs")
    print("\nField-level CS female_share — script-corrected vs "
          "country-corrected:")
    print("year | script | country |  diff")
    diffs = []
    for y in sorted(script_trend):
        if y < args.year_min or y > args.year_max:
            continue
        s = script_trend[y]
        c = country_trend.get(y)
        # skip degenerate / missing country cells (c is None or NaN)
        if c is None or c != c:
            continue
        diffs.append(abs(s - c))
        print(f"{y} | {s:.4f} | {c:.4f} | {s - c:+.4f}")
    max_diff = max(diffs) if diffs else 0.0
    mean_diff = sum(diffs) / len(diffs) if diffs else 0.0
    print(f"\nstudy-window (≤{args.year_max}) |script - country|: "
          f"max {max_diff:.4f}, mean {mean_diff:.4f}")

    out = {
        "country_matrix_n_countries": n_countries,
        "country_matrix_n_ge10": n_ge10,
        "country_corrected_fraction": round(
            cc["n_bias_corrected"] / cc["n_authors"], 4),
        "cs_female_share_script": script_trend,
        "cs_female_share_country": country_trend,
        "study_window": [args.year_min, args.year_max],
        "max_abs_diff": round(max_diff, 4),
        "mean_abs_diff": round(mean_diff, 4),
    }
    (rd.parent / "v3-sensitivity-axis.json").write_text(
        json.dumps(out, indent=2),
    )


if __name__ == "__main__":
    main()
