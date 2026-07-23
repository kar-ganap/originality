"""Measure canon concentration with the denominator confound removed by construction.

    uv run --extra dev python experiments/phase-2.2/canon_share.py

Runs the full validation battery from `docs/concentration-measures.md` before reporting anything.
Reads committed data only; no network, no spend.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from whitespace2.canon_share import (
    CANON_SIZES,
    CanonStudy,
    iter_reference_ids,
    slope,
    subsample_invariance,
)


def _load(embed_dir: Path, source: Path) -> dict[str, list[tuple[int, list[list[int]]]]]:
    """Per-field, per-year reference lists as integer target ids, ascending by year."""
    metadata = pd.read_parquet(embed_dir / "metadata.parquet")
    field_of = dict(zip(metadata["paper_id"], metadata["field"], strict=True))

    table = pq.read_table(
        str(source), columns=["id", "publication_year", "referenced_works_json"]
    ).to_pandas()

    buckets: dict[str, dict[int, list[list[int]]]] = {}
    for paper_id, year, payload in zip(
        table["id"], table["publication_year"], table["referenced_works_json"], strict=True
    ):
        field_name = field_of.get(paper_id)
        if field_name is None or not np.isfinite(year):
            continue
        refs = list(iter_reference_ids(payload))
        if refs:
            buckets.setdefault(field_name, {}).setdefault(int(year), []).append(refs)

    return {
        name: [(year, per_year[year]) for year in sorted(per_year)]
        for name, per_year in buckets.items()
    }


def _report(study: CanonStudy, thinned: CanonStudy) -> dict[str, float]:
    years, share, null = study.year_array(), study.share_array(), study.null_array()
    observed_slope, null_slope = slope(years, share), slope(years, null)
    deficit_slope = slope(years, study.deficit_array())

    print(f"\n--- {study.field}  K={study.k} ---")
    print(f"  years {int(years[0])}-{int(years[-1])}  "
          f"canon_share {share[0]:.4f} -> {share[-1]:.4f}   (null {null[0]:.5f} -> {null[-1]:.5f})")
    print(f"  canon_share slope : {observed_slope:+.6f}/yr    "
          f"null slope {null_slope:+.6f}/yr")
    print(f"  entropy-deficit slope : {deficit_slope:+.6f}/yr")

    # Battery 1 (R3): the estimate must not move when the measured cohort is thinned.
    common = {y.year: y.canon_share for y in thinned.years}
    paired = [(y.canon_share, common[y.year]) for y in study.years if y.year in common]
    if paired:
        full_v = np.array([a for a, _ in paired])
        thin_v = np.array([b for _, b in paired])
        index = np.arange(len(full_v), dtype=np.float64)
        shift = slope(index, thin_v) - slope(index, full_v)
        print(f"  [R3] subsample invariance: mean |full-thinned| = "
              f"{np.abs(full_v - thin_v).mean():.5f}   slope shift {shift:+.6f}")

    # Battery 2: the quantity ref_gini correlated with at +0.999 must not drive this one.
    ratio = np.array([y.n_edges / max(y.n_prior_targets, 1) for y in study.years])
    print(f"  [confound] corr(canon_share, edges per prior target) = "
          f"{np.corrcoef(share, ratio)[0, 1]:+.4f}")
    return {"observed_slope": observed_slope, "null_slope": null_slope,
            "deficit_slope": deficit_slope}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--embed-dir", type=Path, default=Path("data/base-1m"))
    parser.add_argument(
        "--source", type=Path, default=Path("data/base-1m/section0-sample-1M-v3.parquet")
    )
    parser.add_argument(
        "--output", type=Path, default=Path("experiments/phase-2.2/canon-share.json")
    )
    arguments = parser.parse_args()

    per_field = _load(arguments.embed_dir, arguments.source)
    payload: dict[str, dict[str, object]] = {}

    for field_name, per_year in sorted(per_field.items()):
        total = sum(len(lists) for _, lists in per_year)
        print(f"\n===== {field_name.upper()} ({total:,} papers with references) =====")
        for k in CANON_SIZES:
            full, thinned = subsample_invariance(per_year, k=k, field_name=field_name)
            if not full.years:
                print(f"\n--- {field_name}  K={k} --- no year met the edge/canon minimum")
                continue
            summary = _report(full, thinned)
            payload[f"{field_name}-K{k}"] = {
                "summary": summary,
                "years": [asdict(y) for y in full.years],
            }

    arguments.output.write_text(json.dumps(payload, indent=2, sort_keys=True))
    print(f"\nartifact -> {arguments.output}")


if __name__ == "__main__":
    main()
