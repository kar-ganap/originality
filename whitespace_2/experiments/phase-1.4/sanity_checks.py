"""Phase 1.4 Workstream A — production-scale sanity gates.

Validates the Stage-1 demographic substrate (the v3 1M run) against field
intuitions, analogous to Phase 0.1 Checks 1+2 at production scale.

  A1 — year distribution + the 1970-2024 bound (dropped counts; headline
       unchanged under the bound).
  A2 — field-intuition checks: CS/physics author-volume curves; the
       female-share trajectory; top-country share over time (China's
       CS rise); the physics >= CS early-female diagnosis.
  A3 — gender x country coverage cross-tab + per-cell H7 (NamSor names
       per headline year x field x region cell).
  A4 — disambiguation production spot-check (career-length distribution).

Runs on the committed v3 coverage table + the (gitignored, on-disk) Phase
1.3 run intermediates in experiments/phase-1.3/run-1M-v3/.

Usage:
  uv run python experiments/phase-1.4/sanity_checks.py \
      --rundir experiments/phase-1.3/run-1M-v3 \
      --coverage data/metadata/v3-coverage-table.parquet
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pyarrow.parquet as pq

from whitespace2.demographics import _join_cells

_YEAR_MIN = 1970
_YEAR_MAX = 2024
_H7_MIN = 10


def field_trend(df, field, unit="distinct_authors"):  # noqa: ANN001
    """Field-level female_share per year = Σ female / Σ assigned."""
    d = df[(df["unit"] == unit) & (df["field"] == field)]
    g = d.groupby("year")[["sum_p_male", "sum_p_female"]].sum()
    share = g["sum_p_female"] / (g["sum_p_male"] + g["sum_p_female"])
    return {int(y): round(float(v), 4) for y, v in share.items()}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rundir", required=True, type=Path)
    ap.add_argument("--coverage", required=True, type=Path)
    args = ap.parse_args()
    rd: Path = args.rundir

    cov = pq.read_table(str(args.coverage)).to_pandas()
    out: dict[str, object] = {}

    # ---- A1: year distribution + 1970-2024 bound ----
    d = cov[cov["unit"] == "distinct_authors"]
    pre = d[d["year"] < _YEAR_MIN]
    win = d[(d["year"] >= _YEAR_MIN) & (d["year"] <= _YEAR_MAX)]
    post = d[d["year"] > _YEAR_MAX]
    by_year_post = (
        post.groupby("year")["n"].sum().sort_index().to_dict()
    )
    out["A1_year_bound"] = {
        "corpus_year_range": [int(d["year"].min()), int(d["year"].max())],
        "n_authorcells_pre1970": int(pre["n"].sum()),
        "n_authorcells_1970_2024": int(win["n"].sum()),
        "n_authorcells_post2024": int(post["n"].sum()),
        "pre1970_pct": round(100 * pre["n"].sum() / d["n"].sum(), 3),
        "post2024_by_year": {int(y): int(v) for y, v in by_year_post.items()},
    }
    # headline (cs latin distinct) female_share unchanged 2024 vs 2025?
    csl = d[(d["field"] == "cs") & (d["region"] == "latin")].set_index("year")
    out["A1_headline_2024_vs_2025"] = {
        "fs_2024": round(float(csl.loc[2024, "female_share"]), 4)
        if 2024 in csl.index else None,
        "fs_2025": round(float(csl.loc[2025, "female_share"]), 4)
        if 2025 in csl.index else None,
    }

    # ---- A2: field-intuition checks ----
    # author-volume curve (distinct authors per year, in-window)
    vol = {}
    for fld in ("cs", "physics"):
        s = (win[win["field"] == fld].groupby("year")["n"].sum())
        vol[fld] = {int(y): int(v) for y, v in s.items()}
    out["A2_volume_cs"] = {y: vol["cs"].get(y) for y in
                           [1975, 1985, 1995, 2005, 2015, 2024]}
    out["A2_volume_physics"] = {y: vol["physics"].get(y) for y in
                                [1975, 1985, 1995, 2005, 2015, 2024]}
    out["A2_female_share_cs_latin"] = {y: round(float(
        csl.loc[y, "female_share"]), 4) for y in
        [1975, 1985, 1995, 2005, 2015, 2024] if y in csl.index}
    # physics>=CS early-female diagnosis: compare 1975 cs vs physics latin
    pl = d[(d["field"] == "physics") & (d["region"] == "latin")].set_index(
        "year")
    out["A2_physics_ge_cs_1975"] = {
        "cs_female_share_1975": round(float(csl.loc[1975, "female_share"]), 4)
        if 1975 in csl.index else None,
        "physics_female_share_1975": round(float(
            pl.loc[1975, "female_share"]), 4) if 1975 in pl.index else None,
        "cs_n_1975": int(csl.loc[1975, "n"]) if 1975 in csl.index else None,
        "physics_n_1975": int(pl.loc[1975, "n"]) if 1975 in pl.index else None,
    }

    # country-share-over-time (China in CS) — needs the join
    joined = _join_cells(
        rd / "authorships.parquet", rd / "corrected.parquet",
        rd / "paper-field.parquet", region_axis="script",
    )
    jw = joined[(joined["year"] >= _YEAR_MIN) & (joined["year"] <= _YEAR_MAX)
                & (joined["field"] == "cs")]
    jd = jw.drop_duplicates(subset=["year", "author_id"])
    china = {}
    for y in [1995, 2005, 2015, 2024]:
        sub = jd[jd["year"] == y]
        n_known = sub["primary_country"].notna().sum()
        n_cn = (sub["primary_country"] == "CN").sum()
        china[y] = round(float(n_cn / n_known), 4) if n_known else None
    out["A2_china_cs_authorshare"] = china

    # ---- A3: per-cell H7 (NamSor names per headline cell) ----
    ns = pq.read_table(str(rd / "namsor-sample.parquet")).to_pandas()
    ns_names = set(ns["first_name"].dropna())
    pa = pq.read_table(
        str(rd / "per-author.parquet"),
        columns=["author_id", "author_first_name"],
    ).to_pandas()
    ns_author_ids = set(
        pa[pa["author_first_name"].isin(ns_names)]["author_id"])
    jd_all = joined.drop_duplicates(subset=["year", "field", "region",
                                            "author_id"])
    jd_all = jd_all[(jd_all["year"] >= _YEAR_MIN)
                    & (jd_all["year"] <= _YEAR_MAX)]
    jd_all["has_ns"] = jd_all["author_id"].isin(ns_author_ids)
    per_cell_ns = jd_all.groupby(["year", "field", "region"])["has_ns"].sum()
    cell_n = jd_all.groupby(["year", "field", "region"]).size()
    # headline cells = the large ones (n >= 1000)
    big = cell_n[cell_n >= 1000].index
    ns_in_big = per_cell_ns.loc[big]
    out["A3_per_cell_h7"] = {
        "n_headline_cells_n>=1000": int(len(big)),
        "headline_cells_with_ns>=10": int((ns_in_big >= _H7_MIN).sum()),
        "headline_cells_with_ns<10": int((ns_in_big < _H7_MIN).sum()),
        "min_ns_in_headline_cell": int(ns_in_big.min()) if len(big) else None,
        "median_ns_in_headline_cell": int(ns_in_big.median())
        if len(big) else None,
    }
    # gender x country coverage cross-tab (overall, in-window)
    cw = cov[(cov["unit"] == "distinct_authors") & (cov["year"] >= _YEAR_MIN)
             & (cov["year"] <= _YEAR_MAX)]
    out["A3_coverage_overall"] = {
        "gender_coverage_mean": round(float(
            (cw["gender_coverage_rate"] * cw["n"]).sum() / cw["n"].sum()), 4),
        "country_coverage_mean": round(float(
            (cw["country_coverage_rate"] * cw["n"]).sum() / cw["n"].sum()), 4),
    }

    # ---- A4: disambiguation spot-check (career-length distribution) ----
    auth = pq.read_table(
        str(rd / "authorships.parquet"),
        columns=["author_id", "publication_year"],
    ).to_pandas()
    auth = auth[auth["publication_year"].notna()]
    car = auth.groupby("author_id")["publication_year"].agg(["min", "max"])
    career = car["max"] - car["min"]
    out["A4_career_length"] = {
        "n_authors": int(len(career)),
        "p50": int(career.quantile(0.50)),
        "p90": int(career.quantile(0.90)),
        "p99": int(career.quantile(0.99)),
        "n_over_60yr": int((career > 60).sum()),
        "pct_over_60yr": round(100 * (career > 60).mean(), 4),
    }

    print(json.dumps(out, indent=2))
    (Path(__file__).parent / "sanity-results.json").write_text(
        json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
