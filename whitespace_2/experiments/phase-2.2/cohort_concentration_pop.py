"""Cohort citation-concentration on the 24M-population in-degree — the trustworthy measurement.

    uv run --extra dev python experiments/phase-2.2/cohort_concentration_pop.py

Consumes `cohort-indegree-pop.json` (from `cohort_indegree_pop.py`) and runs the tested
`cohort_concentration` measure plus the full battery. The decisive panel is all-time vs
fixed-window: if the concentration trend flips between them, the concentration signal was an accrual
artifact — the same test that reversed the CD-index (WS3 bridge C-2c), applied to the metric that
was supposed to carry WS2's canon claim.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from whitespace2.cohort_concentration import (
    FieldConcentration,
    cohort_concentration,
    volume_controlled_gini,
)

MEASURES = ("indeg_alltime", "indeg_w5", "indeg_w10")


def _series(rows: list[dict], measure: str, field_name: str, *, last_complete: int,
            window: int) -> FieldConcentration:
    concentration = cohort_concentration(
        [r["year"] for r in rows],
        [r[measure] for r in rows],
        [r["field"] for r in rows],
        field_name=field_name,
        last_complete_year=last_complete,
        # window 0 (all-time) keeps every cohort; W>0 censors cohorts younger than the window
        window=window,
    )
    return FieldConcentration(field=field_name, window=window, rows=concentration)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", type=Path, default=Path("experiments/phase-2.2/cohort-indegree-pop.json")
    )
    arguments = parser.parse_args()

    payload = json.loads(arguments.input.read_text())
    rows, last_complete = payload["rows"], payload["last_complete_year"]
    print(f"loaded {len(rows):,} paneled papers over the {payload['n_population']:,}-paper graph")
    print(f"last complete citer year: {last_complete}\n")

    windows = {"indeg_alltime": 0, "indeg_w5": 5, "indeg_w10": 10}
    summary: dict[str, dict[str, float]] = {}

    for field_name in ("cs", "physics"):
        print(f"===== {field_name.upper()} =====")
        for measure in MEASURES:
            study = _series(rows, measure, field_name,
                            last_complete=last_complete, window=windows[measure])
            years = study.years()
            gini_slope = study.slope("gini")
            excess = study.series("gini") - study.series("null_gini")
            enough = len(study.rows) > 1
            excess_slope = float(np.polyfit(years, excess, 1)[0]) if enough else float("nan")
            ratio = np.array([r.n_citations / max(r.n_papers, 1) for r in study.rows])
            confound = (
                float(np.corrcoef(study.series("gini"), ratio)[0, 1]) if enough else float("nan")
            )
            label = f"{measure:14s}"
            print(f"  {label} ({int(years[0])}-{int(years[-1])}, {len(study.rows)} cohorts)")
            print(f"     gini {study.series('gini')[0]:.4f} -> {study.series('gini')[-1]:.4f}"
                  f"   slope {gini_slope:+.6f}/yr")
            print(f"     top_decile slope {study.slope('top_decile_share'):+.6f}   "
                  f"entropy_deficit slope {study.slope('entropy_deficit'):+.6f}")
            print(f"     EXCESS over null slope {excess_slope:+.6f}/yr    "
                  f"[confound] corr(gini, cites/paper) {confound:+.4f}")
            summary[f"{field_name}-{measure}"] = {
                "gini_slope": gini_slope,
                "excess_slope": excess_slope,
                "confound_corr": confound,
            }
        print()

    print("=== DECISIVE CONTRAST: does the trend survive a fixed window? ===")
    for field_name in ("cs", "physics"):
        at = summary[f"{field_name}-indeg_alltime"]["excess_slope"]
        w5 = summary[f"{field_name}-indeg_w5"]["excess_slope"]
        w10 = summary[f"{field_name}-indeg_w10"]["excess_slope"]
        print(f"  {field_name:8s} excess-Gini slope   all-time {at:+.6f}   "
              f"W=5 {w5:+.6f}   W=10 {w10:+.6f}")

    # The excess-Gini above is density-confounded (the null's Gini falls as citations/paper rise).
    # The clean test holds density fixed: thin every cohort to the field's MINIMUM cites/paper, then
    # any surviving Gini trend is concentration shape, not citation volume.
    print("\n=== VOLUME-CONTROLLED (each cohort thinned to the field's min cites/paper) ===")
    rng = np.random.default_rng(20260722)
    for field_name in ("cs", "physics"):
        for measure, window in (("indeg_w5", 5), ("indeg_w10", 10)):
            study = _series(rows, measure, field_name,
                            last_complete=last_complete, window=window)
            kept_years = {r.year for r in study.rows}
            by_year: dict[int, list[int]] = {}
            for r in rows:
                if r["field"] == field_name and r["year"] in kept_years:
                    by_year.setdefault(r["year"], []).append(r[measure])
            floor = float(min(r.n_citations / r.n_papers for r in study.rows))
            years = study.years()
            controlled = np.array(
                [volume_controlled_gini(rng, by_year[int(y)], floor) for y in years]
            )
            vc_slope = float(np.polyfit(years, controlled, 1)[0])
            summary[f"{field_name}-{measure}"]["volctrl_gini_slope"] = vc_slope
            summary[f"{field_name}-{measure}"]["min_rate"] = floor
            print(f"  {field_name:8s} {measure}  rate floor {floor:.2f} cites/paper   "
                  f"controlled Gini {controlled[0]:.4f} -> {controlled[-1]:.4f}   "
                  f"slope {vc_slope:+.6f}/yr")

    out = arguments.input.with_name("cohort-concentration-pop.json")
    out.write_text(json.dumps(summary, indent=2, sort_keys=True))
    print(f"\nartifact -> {out}")


if __name__ == "__main__":
    main()
