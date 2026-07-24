"""Run WS2's `ref_gini` against a matched uniform-attachment null.

    uv run --extra dev python experiments/phase-2.2/null_ref_gini.py \
        --embed-dir data/base-1m --source data/base-1m/section0-sample-1M-v3.parquet

Reads committed data only; no network, no spend. See `whitespace2.null_ref_gini` for what the null
holds fixed and what it destroys.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from whitespace2.null_ref_gini import (
    RefGiniNullStudy,
    load_series,
    run_field_study,
    slope,
    subsampled_reference_lists,
)

_SERIES = Path(__file__).parent / "series" / "semantic-canonical.json"


def _render(study: RefGiniNullStudy) -> None:
    years, observed, null = study.year_array(), study.observed(), study.null()
    print(f"\n===== {study.field.upper()} =====")
    print("replay positive control: max |replay - committed ref_gini| = "
          f"{study.replay_max_error:.2e}")

    print(f"\n{'year':>6} {'edges':>9} {'targets':>9} {'pool':>12} "
          f"{'observed':>9} {'null':>9} {'excess':>9}   95% null band")
    for y in study.years:
        if y.year % 10 and y.year != study.years[-1].year:
            continue
        low, high = y.null_band
        pool = "inf" if not np.isfinite(y.pool_size) else f"{y.pool_size:,.0f}"
        print(f"{y.year:>6} {y.n_ref_edges:>9,} {y.n_distinct_targets:>9,} {pool:>12} "
              f"{y.observed_gini:>9.4f} {y.null_mean:>9.4f} {y.excess:>+9.4f}   "
              f"[{low:.4f}, {high:.4f}]")

    observed_slope, null_slope = slope(years, observed), slope(years, null)
    low, high = study.null_slope_band()
    print(f"\n  observed ref_gini slope : {observed_slope:+.6f} / yr")
    print(f"  matched-null slope      : {null_slope:+.6f} / yr   "
          f"95% [{low:+.6f}, {high:+.6f}]  p={study.slope_p_value():.3f}")
    if observed_slope:
        print(f"  the null reproduces {null_slope / observed_slope:.0%} of the observed trend")
    print(f"  EXCESS slope (observed - null) : {study.excess_slope():+.6f} / yr"
          f"   <- the concentration signal proper")

    inside = sum(y.null_band[0] <= y.observed_gini <= y.null_band[1] for y in study.years)
    print(f"  years whose observed Gini falls inside the null's 95% band: "
          f"{inside}/{len(study.years)}")

    ratio = np.array([y.n_ref_edges / y.n_distinct_targets for y in study.years])
    print(f"  corr(observed ref_gini, edges per distinct target) = "
          f"{np.corrcoef(observed, ratio)[0, 1]:+.4f}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--embed-dir", type=Path, default=Path("data/base-1m"))
    parser.add_argument(
        "--source", type=Path, default=Path("data/base-1m/section0-sample-1M-v3.parquet")
    )
    parser.add_argument("--replicates", type=int, default=200)
    parser.add_argument("--seed", type=int, default=20260722)
    parser.add_argument(
        "--output", type=Path, default=Path("experiments/phase-2.2/ref-gini-null.json")
    )
    arguments = parser.parse_args()

    metadata = pd.read_parquet(arguments.embed_dir / "metadata.parquet")
    source = pq.read_table(
        str(arguments.source), columns=["id", "referenced_works_json"]
    ).to_pandas()
    ref_map = dict(zip(source["id"], source["referenced_works_json"], strict=True))

    per_field = subsampled_reference_lists(metadata, ref_map)
    committed = load_series(_SERIES)

    studies = {}
    for field_name, per_year in per_field.items():
        study = run_field_study(
            per_year,
            committed[field_name],
            field_name=field_name,
            n_replicates=arguments.replicates,
            seed=arguments.seed,
        )
        _render(study)
        studies[field_name] = asdict(study)

    arguments.output.write_text(json.dumps(studies, indent=2, sort_keys=True))
    print(f"\nartifact -> {arguments.output}")


if __name__ == "__main__":
    main()
