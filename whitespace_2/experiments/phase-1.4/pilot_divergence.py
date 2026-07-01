"""Phase 1.4 C4 — run the pre-registered divergence test on the 100K pilot.

EXPLORATORY (per desideratum §5): the pre-registered headline is the full
1M Stage-2 run; this pilot de-risks the pipeline — does embed → per-year
semantic metrics → the divergence estimator compose and produce a sane,
computable statistic + a rising canonical negative control?

Assembles three per-year series for CS (primary field per §6), 1970-2024:
  - SEMANTIC (on the 100K SciNCL vectors): effective_dimensionality,
    mean_pairwise_cosine_distance (subsampled), cluster_entropy (K-means
    K=50; §11 temporal-stratification of the fit is a Stage-2 refinement —
    here the fit is on a year-stratified sample, noted as exploratory).
  - CANONICAL (negative control): citation Gini per year.
  - DEMOGRAPHIC: gender Shannon per year from the Phase-1.3 v3 cells table
    (full 1M — the pilot's semantic side is 100K; both estimate the
    population trend, flagged).

Usage:
  uv run python experiments/phase-1.4/pilot_divergence.py \
      --smokedir experiments/phase-1.4/smoke-100k \
      --cells experiments/phase-1.3/run-1M-v3/cells.parquet
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pyarrow.parquet as pq
from sklearn.cluster import KMeans

from whitespace2.canonical_metrics import gini
from whitespace2.divergence import divergence_test
from whitespace2.semantic_metrics import (
    _shannon_entropy_mm,
    cluster_entropy,
    effective_dimensionality,
    mean_pairwise_cosine_distance,
)

_YEAR_MIN, _YEAR_MAX = 1970, 2024
_MIN_PAPERS_PER_YEAR = 50   # stable per-year semantic metrics
_K_CLUSTERS = 50
_KMEANS_FIT_PER_YEAR = 400  # year-stratified fit sample (exploratory §11)
_MPCD_SUBSAMPLE = 500
_SEED = 20260630


def _demographic_gender_shannon(cells_parquet: Path) -> dict[int, float]:
    """Year-level CS gender Shannon (distinct authors) from the cells table:
    sum the corrected male/female mass over regions per year → MM Shannon."""
    df = pq.read_table(str(cells_parquet)).to_pandas()
    d = df[(df["unit"] == "distinct_authors") & (df["field"] == "cs")]
    g = d.groupby("year")[["sum_p_male", "sum_p_female"]].sum()
    out: dict[int, float] = {}
    for y, row in g.iterrows():
        m, f = float(row["sum_p_male"]), float(row["sum_p_female"])
        out[int(y)] = _shannon_entropy_mm(np.array([m, f]), m + f)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smokedir", required=True, type=Path)
    ap.add_argument("--cells", required=True, type=Path)
    args = ap.parse_args()

    vecs = np.load(args.smokedir / "scincl-vectors.npy")
    meta = pq.read_table(str(args.smokedir / "metadata.parquet")).to_pandas()
    assert len(meta) == vecs.shape[0], "metadata/vector row mismatch"

    # CS, in-window
    cs = meta[(meta["field"] == "cs") & (meta["year"] >= _YEAR_MIN)
              & (meta["year"] <= _YEAR_MAX)].copy()
    cs_idx = cs.index.to_numpy()
    cs_vecs = vecs[cs_idx]
    years_all = cs["year"].to_numpy()
    print(f"CS in-window pilot papers: {len(cs):,}", flush=True)

    # Global K-means fit on a year-stratified sample (exploratory §11 proxy).
    rng = np.random.default_rng(_SEED)
    fit_rows: list[int] = []
    for y in np.unique(years_all):
        pos = np.where(years_all == y)[0]
        take = min(len(pos), _KMEANS_FIT_PER_YEAR)
        fit_rows.extend(rng.choice(pos, size=take, replace=False).tolist())
    km = KMeans(n_clusters=_K_CLUSTERS, random_state=_SEED, n_init=4)
    km.fit(cs_vecs[np.array(fit_rows)])
    assign_all = km.predict(cs_vecs)

    # Per-year series
    years: list[int] = []
    sem_effdim: list[float] = []
    sem_mpcd: list[float] = []
    sem_clent: list[float] = []
    can_gini: list[float] = []
    for y in range(_YEAR_MIN, _YEAR_MAX + 1):
        pos = np.where(years_all == y)[0]
        if len(pos) < _MIN_PAPERS_PER_YEAR:
            continue
        yv = cs_vecs[pos]
        years.append(y)
        sem_effdim.append(effective_dimensionality(yv))
        sem_mpcd.append(mean_pairwise_cosine_distance(
            yv, max_sample=_MPCD_SUBSAMPLE, seed=_SEED))
        sem_clent.append(cluster_entropy(assign_all[pos], _K_CLUSTERS))
        can_gini.append(gini(cs.iloc[pos]["cited_by_count"].to_numpy()))

    # Demographic (full-1M CS gender Shannon), aligned to the semantic years
    dem_map = _demographic_gender_shannon(args.cells)
    demographic = [dem_map.get(y, float("nan")) for y in years]

    semantic = {
        "cluster_entropy": sem_clent,
        "effective_dimensionality": sem_effdim,
        "mean_pairwise_cosine": sem_mpcd,
    }
    result = divergence_test(years, demographic, semantic, can_gini)

    # Trim the verbose ratio_trends for the printed summary
    summary: dict[str, Any] = {
        "EXPLORATORY": "pilot on 100K SciNCL; headline is the full 1M "
                       "Stage-2 run (§5)",
        "n_years": len(years),
        "year_range": [years[0], years[-1]] if years else None,
        "verdict": result["verdict"],
        "divergence_confirmed": result["divergence_confirmed"],
        "substrate_ok": result["substrate_ok"],
        "ratio_trend_slopes": {
            m: {"slope": t["slope"], "pvalue": t["pvalue"],
                "direction": t["direction"], "significant": t["significant"]}
            for m, t in result["ratio_trends"].items()
        },
        "negative_control": {
            "slope": result["negative_control"]["slope"],
            "pvalue": result["negative_control"]["pvalue"],
            "direction": result["negative_control"]["direction"],
        },
    }
    print(json.dumps(summary, indent=2), flush=True)

    full = {**summary, "series": {
        "years": years, "demographic_gender_shannon": demographic,
        "semantic": semantic, "canonical_gini": can_gini}}
    (args.smokedir.parent / "pilot-divergence-results.json").write_text(
        json.dumps(full, indent=2))


if __name__ == "__main__":
    main()
