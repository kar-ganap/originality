"""Phase 2.2 WS-F + robustness stack — does the semantic trend survive controls?

Runs the pre-registered robustness sweep on the base 1M vectors, all variants
reported (no cherry-picking). For each config, per (field, metric):
  - RAW absolute standardized trend (total σ over 1970-2024)
  - RESIDUAL year-coefficient of  metric ~ year + log(volume) + demographic
    (the "critical second figure"; Freedman-Lane permutation + year VIF)

Configs:
  base_volctrl  — SciNCL K=50, cluster-entropy on the MATCHED-N (5000) subsample
                  (volume-controlled) + effective-dim + pairwise-cosine
  scincl_k30 / scincl_k100 — cluster-entropy under a §11 refit at K∈{30,100}
  qwen3_k50     — model swap: effective-dim + pairwise-cosine on Qwen3, plus
                  cluster-entropy under a Qwen3 §11 fit
  clean05       — score≥0.50 subset (stricter concept filter; tests field
                  contamination, esp. the Physics effective-dim decline)

All cluster-entropy here is on the matched-N subsample, so volume is controlled
by construction (isolating the model / K / cleaning effect).

Usage: uv run python experiments/phase-2.2/robustness_sweep.py \
    --embed-dir <scratch>/embed-1m --source <scratch>/section0-sample-1M-v3.parquet
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from whitespace2.cluster_fit import (
    build_decade_stratified_sample,
    fit_clusters,
    project_to_clusters,
)
from whitespace2.divergence import residual_trend, standardized_effect
from whitespace2.semantic_metrics import (
    cluster_entropy,
    effective_dimensionality,
    mean_pairwise_cosine_distance,
)

_SER = Path(__file__).parent / "series"
_FIELDS = ("cs", "physics")
_YEARS = range(1970, 2025)
_N_CAP = 5000
_MPC = 2000
_SEED = 46
_CS_ID = "https://openalex.org/C41008148"
_PHYS_ID = "https://openalex.org/C121332964"
_N_PERM = 5000


def _field_score(cj: str, field: str) -> float:
    cid = _CS_ID if field == "cs" else _PHYS_ID
    for c in json.loads(cj):
        rid = c.get("id", "")
        if rid == cid or rid.rsplit("/", 1)[-1] == cid.rsplit("/", 1)[-1]:
            return float(c.get("score") or 0.0)
    return 0.0


def _subsample(idx_pool: np.ndarray[Any, Any], rng: Any) -> np.ndarray[Any, Any]:
    if idx_pool.size > _N_CAP:
        return np.sort(rng.choice(idx_pool, size=_N_CAP, replace=False))
    return idx_pool


def _trends(
    per_year: dict[int, float], vol: dict[int, float], dem: dict[int, float],
) -> dict[str, Any]:
    years = sorted(y for y in per_year
                   if not np.isnan(per_year[y]) and y in vol and y in dem)
    if len(years) < 6:
        return {"raw_sd": None, "resid_coef": None, "resid_dir": None,
                "resid_sig": None, "vif": None, "n": len(years)}
    yr = np.array(years, float)
    v = np.array([per_year[y] for y in years])
    logvol = np.log(np.array([vol[y] for y in years]))
    demv = np.array([dem[y] for y in years])
    raw = standardized_effect(yr, v)["total_change_sd"]
    rt = residual_trend(yr, v, [logvol, demv], n_perm=_N_PERM, seed=_SEED)
    coef = rt["year_coef"]
    return {"raw_sd": round(raw, 3) if raw is not None else None,
            "resid_coef": round(coef, 6) if coef is not None else None,
            "resid_dir": ("up" if coef and coef > 0 else "down"
                          if coef and coef < 0 else "flat"),
            "resid_sig": rt["significant"],
            "vif": round(rt["year_vif"], 1) if rt["year_vif"] else None,
            "n": len(years)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--embed-dir", required=True, type=Path)
    ap.add_argument("--source", required=True, type=Path)
    args = ap.parse_args()

    meta = pd.read_parquet(args.embed_dir / "metadata.parquet")
    years_all = meta["year"].to_numpy()
    fields_all = meta["field"].to_numpy()
    scincl = np.load(args.embed_dir / "scincl-vectors.npy", mmap_mode="r")
    qwen3 = np.load(args.embed_dir / "qwen3-vectors.npy", mmap_mode="r")
    assign50 = np.load(args.embed_dir / "scincl-cluster-assignments.npy")
    dem = json.loads((_SER / "demographic-joint.json").read_text())
    dem = {f: {int(y): v for y, v in d.items()} for f, d in dem.items()}

    # concept scores for the clean subset — precomputed once (per paper's field)
    print("loading + scoring concepts (once) …", flush=True)
    src = pq.read_table(str(args.source),
                        columns=["id", "concepts_json"]).to_pandas()
    cj_map = dict(zip(src["id"], src["concepts_json"], strict=True))
    paper_ids = meta["paper_id"].to_numpy()
    scores_all = np.array([
        _field_score(str(cj_map.get(pid, "[]")), fld)
        for pid, fld in zip(paper_ids, fields_all, strict=True)
    ])
    print("  scored", flush=True)

    rng = np.random.default_rng(_SEED)
    # per-(field,year) matched-N subsamples (base) + clean (score>=0.5) subsamples
    sub: dict[str, dict[int, np.ndarray[Any, Any]]] = {f: {} for f in _FIELDS}
    sub_clean: dict[str, dict[int, np.ndarray[Any, Any]]] = {f: {} for f in _FIELDS}
    vol: dict[str, dict[int, float]] = {f: {} for f in _FIELDS}
    for field in _FIELDS:
        fmask = fields_all == field
        for y in _YEARS:
            pool = np.nonzero(fmask & (years_all == y))[0]
            if pool.size == 0:
                continue
            vol[field][int(y)] = float(pool.size)
            sub[field][int(y)] = _subsample(pool, rng)
            cpool = pool[scores_all[pool] >= 0.5]
            if cpool.size:
                sub_clean[field][int(y)] = _subsample(cpool, rng)
    print("built subsamples", flush=True)

    # §11 fits for K-sweep + qwen3 (decade-balanced 60K, from full vectors)
    fits: dict[str, np.ndarray[Any, Any]] = {}
    for name, vecs, k in [("scincl_k30", scincl, 30),
                          ("scincl_k100", scincl, 100),
                          ("qwen3_k50", qwen3, 50)]:
        fi = build_decade_stratified_sample(years_all, n_per_decade=10000,
                                            seed=_SEED)
        print(f"fitting {name} …", flush=True)
        fits[name] = fit_clusters(np.asarray(vecs[fi]), k=k)

    def _ce_series(vecs: Any, centroids: Any, k: int,
                   subs: dict[int, np.ndarray[Any, Any]]) -> dict[int, float]:
        out = {}
        for y, gidx in subs.items():
            a = project_to_clusters(np.asarray(vecs[gidx]), centroids)
            out[y] = float(cluster_entropy(a, k))
        return out

    def _sem_series(vecs: Any, subs: dict[int, np.ndarray[Any, Any]],
                    metric: str) -> dict[int, float]:
        out = {}
        for y, gidx in subs.items():
            sv = np.asarray(vecs[gidx], dtype=np.float32)
            if metric == "effective_dimensionality":
                out[y] = float(effective_dimensionality(sv))
            else:
                out[y] = float(mean_pairwise_cosine_distance(
                    sv, max_sample=_MPC, seed=_SEED))
        return out

    results: dict[str, Any] = {}
    for field in _FIELDS:
        subs, subs_c, v, d = (sub[field], sub_clean[field],
                              vol[field], dem[field])
        cfg: dict[str, dict[str, Any]] = {}

        # base_volctrl: cluster-entropy matched-N (K=50) + eff-dim + pairwise
        ce50 = {y: float(cluster_entropy(assign50[gidx], 50))
                for y, gidx in subs.items()}
        cfg["base_volctrl/cluster_entropy_K50"] = _trends(ce50, v, d)
        cfg["base_volctrl/effective_dim"] = _trends(
            _sem_series(scincl, subs, "effective_dimensionality"), v, d)
        cfg["base_volctrl/mean_pairwise"] = _trends(
            _sem_series(scincl, subs, "mean_pairwise_cosine"), v, d)
        # K-sweep
        cfg["scincl_k30/cluster_entropy"] = _trends(
            _ce_series(scincl, fits["scincl_k30"], 30, subs), v, d)
        cfg["scincl_k100/cluster_entropy"] = _trends(
            _ce_series(scincl, fits["scincl_k100"], 100, subs), v, d)
        # qwen3 model swap
        cfg["qwen3_k50/cluster_entropy"] = _trends(
            _ce_series(qwen3, fits["qwen3_k50"], 50, subs), v, d)
        cfg["qwen3_k50/effective_dim"] = _trends(
            _sem_series(qwen3, subs, "effective_dimensionality"), v, d)
        cfg["qwen3_k50/mean_pairwise"] = _trends(
            _sem_series(qwen3, subs, "mean_pairwise_cosine"), v, d)
        # clean05 (score>=0.5) — cluster-entropy K=50 + eff-dim + pairwise
        ce50c = {y: float(cluster_entropy(assign50[gidx], 50))
                 for y, gidx in subs_c.items()}
        cfg["clean05/cluster_entropy_K50"] = _trends(ce50c, v, d)
        cfg["clean05/effective_dim"] = _trends(
            _sem_series(scincl, subs_c, "effective_dimensionality"), v, d)
        cfg["clean05/mean_pairwise"] = _trends(
            _sem_series(scincl, subs_c, "mean_pairwise_cosine"), v, d)

        results[field] = cfg
        print(f"\n===== {field.upper()} (raw σ / residual year-coef "
              f"[dir,sig,VIF]) =====", flush=True)
        for name, t in cfg.items():
            print(f"  {name:38s} raw={t['raw_sd']!s:>7} "
                  f"resid={t['resid_dir']!s:>4} sig={t['resid_sig']!s:>5} "
                  f"vif={t['vif']}", flush=True)

    (_SER / "robustness-sweep.json").write_text(json.dumps(results, indent=2))
    print(f"\nwrote {_SER}/robustness-sweep.json", flush=True)


if __name__ == "__main__":
    main()
