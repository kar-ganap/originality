"""DERISK ONLY — cohort citation-concentration on the LOCAL panel's in-sample uptake.

    uv run --extra dev python experiments/phase-2.2/cohort_concentration_local.py

This validates the pipeline and the battery on `panel-2.4.parquet`'s `uptake_W` columns, which count
citations **only from within the 902K in-window sample**. The in-sample rate rises over time as the
corpus grows, so the in-sample uptake thins earlier cohorts more than later ones — which can
manufacture a trend. **The trend printed here is therefore NOT trustworthy.** Its job is to prove
the measure runs and its battery behaves; the trustworthy number comes from the 24M-population run
(`cohort_concentration_pop.py`), where in-degree is complete.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from whitespace2.cohort_concentration import FieldConcentration, cohort_concentration

LAST_COMPLETE_YEAR = 2024


def _run(panel: pd.DataFrame, field_name: str, window: int) -> FieldConcentration:
    rows = cohort_concentration(
        panel["year"].to_numpy(),
        panel[f"uptake_{window}"].to_numpy(),
        panel["field"].to_numpy(),
        field_name=field_name,
        last_complete_year=LAST_COMPLETE_YEAR,
        window=window,
    )
    return FieldConcentration(field=field_name, window=window, rows=rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel", type=Path, default=Path("data/base-1m/panel-2.4.parquet"))
    parser.add_argument("--window", type=int, default=5)
    arguments = parser.parse_args()

    panel = pd.read_parquet(
        arguments.panel, columns=["year", "field", f"uptake_{arguments.window}"]
    )
    print("*** DERISK RUN — in-sample uptake, trend not trustworthy (see module docstring) ***")
    print(f"panel: {len(panel):,} papers   window W={arguments.window}\n")

    for field_name in ("cs", "physics"):
        study = _run(panel, field_name, arguments.window)
        years = study.years()
        print(f"--- {field_name.upper()}  W={arguments.window}  "
              f"({int(years[0])}-{int(years[-1])}, {len(study.rows)} cohorts) ---")
        for attr in ("gini", "top_decile_share", "entropy_deficit"):
            first, last = study.series(attr)[0], study.series(attr)[-1]
            print(f"  {attr:18s} {first:.4f} -> {last:.4f}   slope {study.slope(attr):+.6f}/yr")
        null_slope = study.slope("null_gini")
        print(f"  {'null_gini':18s} slope {null_slope:+.6f}/yr")
        excess = study.series("gini") - study.series("null_gini")
        print(f"  excess Gini (observed-null): {excess[0]:+.4f} -> {excess[-1]:+.4f}   "
              f"slope {float(np.polyfit(years, excess, 1)[0]):+.6f}/yr")

        # battery item 3 (R7): fields must be free to differ; printed side by side below.
        ratio = np.array([r.n_citations / max(r.n_papers, 1) for r in study.rows])
        print(f"  [confound] corr(gini, citations per paper) = "
              f"{np.corrcoef(study.series('gini'), ratio)[0, 1]:+.4f}\n")


if __name__ == "__main__":
    main()
