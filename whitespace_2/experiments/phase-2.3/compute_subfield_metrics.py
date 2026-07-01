"""Phase 2.3 — per-subfield metrics for the mechanism test (both definitions).

For each subfield (level-1 sub-concept OR K=50 cluster) computes, over the trimmed
window 1970–2023:

  - `canon_concentration` (LEVEL) — mean over the subfield's years of
    `reference_canonicity.ref_gini` (how unequally references pile onto a few
    canonical works). Secondary: mean `ref_top_k_share`, mean `canon_spearman_d5`.
  - `semantic_trend_sd` — standardized slope (σ over window) of the subfield's
    per-year `mean_pairwise_cosine_distance`, on **SciNCL** and **Qwen3**
    (≥2 embedding families). Per-(subfield,year) cell subsampled to ≤ MPC_SAMPLE.
  - `demographic_trend_sd` — standardized slope of the subfield's per-year joint
    `career_joint_shannon` (via `build_joint_plurality_series` on the subfield
    map — the demographic pipeline reused verbatim).
  - `divergence_{scincl,qwen3}` = demographic_trend_sd − semantic_trend_sd (the
    HONEST absolute-based divergence, NOT the confounded ratio).
  - `log_size` = log10(subfield paper count) — the required control.

`metadata` is row-aligned to the vectors, so subfield membership is carried as a
full-length key array (sentinel "" = no subfield) and every cell index is a
GLOBAL vector/metadata row. Inclusion filter (pre-registered, reported): ≥ N_MIN
papers AND ≥ Y_MIN years with BOTH a semantic and a demographic value. Output:
`<outdir>/subfield-metrics-{concepts,clusters}.json`.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from whitespace2.canonical_metrics import reference_canonicity
from whitespace2.demographics import build_joint_plurality_series
from whitespace2.divergence import standardized_effect
from whitespace2.semantic_metrics import mean_pairwise_cosine_distance

_YEAR_MIN, _YEAR_MAX = 1970, 2023        # trim the incomplete final year (2024)
_N_MIN = 2000                            # subfield inclusion floor (papers)
_Y_MIN = 20                              # min years with a computable value
_N_YEAR_MIN = 30                         # min papers per (subfield,year) cell
_MPC_SAMPLE = 2000                       # per-cell semantic subsample cap
_SEED = 46


def _semantic_trends(
    keys: np.ndarray[Any, Any],
    years: np.ndarray[Any, Any],
    embeds: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    """{subfield_key: {'{name}_sd': …, 'sem_years': …}} — standardized slope of
    per-year mean-pairwise-cosine for each embedding family in ``embeds``.

    ``keys``/``years`` are full-length + row-aligned to the vectors; group row
    indices are therefore GLOBAL vector rows (sentinel "" skipped). Each cell's
    subsample is gathered ONCE and shared across embedding families (same idx)."""
    rng = np.random.default_rng(_SEED)
    out: dict[str, dict[str, Any]] = {}
    order = np.argsort(keys, kind="stable")
    keys_s = keys[order]
    uniq, starts = np.unique(keys_s, return_index=True)
    bounds = list(starts) + [len(keys_s)]

    for i, key in enumerate(uniq):
        if key == "":
            continue
        rows = order[bounds[i]:bounds[i + 1]]        # GLOBAL vector/metadata rows
        yr = years[rows]
        vals: dict[str, list[float]] = {name: [] for name in embeds}
        yv: list[int] = []
        for y in range(_YEAR_MIN, _YEAR_MAX + 1):
            cell = rows[yr == y]
            if cell.size < _N_YEAR_MIN:
                continue
            idx = cell
            if idx.size > _MPC_SAMPLE:
                idx = rng.choice(idx, size=_MPC_SAMPLE, replace=False)
            idx = np.sort(idx)                        # ordered mmap gather, shared
            for name, arr in embeds.items():
                v = np.asarray(arr[idx], dtype=np.float32)
                vals[name].append(mean_pairwise_cosine_distance(v))
            yv.append(y)
        ya = np.array(yv, dtype=float)
        ok = len(yv) >= 3
        rec: dict[str, Any] = {"sem_years": len(yv)}
        for name in embeds:
            rec[f"{name}_sd"] = standardized_effect(
                ya, np.array(vals[name]))["total_change_sd"] if ok else None
        out[str(key)] = rec
    return out


def _canon_levels(
    keys: np.ndarray[Any, Any],
    years: np.ndarray[Any, Any],
    refs: np.ndarray[Any, Any],
) -> dict[str, dict[str, Any]]:
    """{subfield_key: {canon_concentration, ref_top_k, canon_spearman_d5}} —
    mean over the subfield's in-window years (sentinel "" skipped)."""
    out: dict[str, dict[str, Any]] = {}
    df = pd.DataFrame({"key": keys, "year": years})
    for key, sub in df.groupby("key", sort=True):
        if key == "":
            continue
        idx = sub.index.to_numpy()                    # GLOBAL rows
        rows = reference_canonicity(
            years[idx], [refs[i] for i in idx], top_n=50, deltas=(5,))
        rows = [r for r in rows if _YEAR_MIN <= r["year"] <= _YEAR_MAX]
        if not rows:
            out[str(key)] = {"canon_concentration": None}
            continue
        sp = [r["canon_spearman_d5"] for r in rows
              if r.get("canon_spearman_d5") is not None]
        out[str(key)] = {
            "canon_concentration": float(np.mean([r["ref_gini"] for r in rows])),
            "ref_top_k": float(np.mean([r["ref_top_k_share"] for r in rows])),
            "canon_spearman_d5": float(np.mean(sp)) if sp else None,
            "canon_years": len(rows),
        }
    return out


def _demographic_trends(
    demog_dir: Path, subfield_map: Path,
) -> dict[str, dict[str, Any]]:
    """{subfield_key: {demographic_sd, dem_years}} via the reused demographic
    pipeline on the subfield map (its ``field`` key IS the subfield)."""
    rows = build_joint_plurality_series(
        demog_dir / "authorships.parquet",
        demog_dir / "corrected.parquet",
        subfield_map,
    )
    by_key: dict[str, dict[int, float]] = {}
    for r in rows:
        if _YEAR_MIN <= r["year"] <= _YEAR_MAX:
            by_key.setdefault(str(r["field"]), {})[r["year"]] = r[
                "career_joint_shannon"]
    out: dict[str, dict[str, Any]] = {}
    for key, ys in by_key.items():
        yrs = np.array(sorted(ys), dtype=float)
        vals = np.array([ys[int(y)] for y in yrs], dtype=float)
        out[key] = {
            "demographic_sd": standardized_effect(yrs, vals)["total_change_sd"]
            if len(yrs) >= 3 else None,
            "dem_years": int(len(yrs)),
        }
    return out


def _assemble(
    definition: str,
    subfield_map: Path,
    meta: pd.DataFrame,
    embeds: dict[str, Any],
    refs: np.ndarray[Any, Any],
    demog_dir: Path,
) -> dict[str, Any]:
    emb_names = list(embeds)
    smap = pq.read_table(str(subfield_map)).to_pandas()
    key_by_pid = dict(zip(smap["paper_id"], smap["primary_field"], strict=True))
    keys = meta["paper_id"].map(key_by_pid).fillna("").to_numpy().astype(str)
    yrs = meta["year"].to_numpy().astype(int)
    counts = pd.Series(keys[keys != ""]).value_counts()

    print(f"[{definition}] semantic trends ({', '.join(emb_names)}) over "
          f"{len(counts)} subfields …", flush=True)
    sem = _semantic_trends(keys, yrs, embeds)
    print(f"[{definition}] canon levels …", flush=True)
    canon = _canon_levels(keys, yrs, refs)
    print(f"[{definition}] demographic trends …", flush=True)
    dem = _demographic_trends(demog_dir, subfield_map)

    records: list[dict[str, Any]] = []
    n_kept = 0
    for key in sorted(counts.index):
        n_papers = int(counts[key])
        s, c, d = sem.get(key, {}), canon.get(key, {}), dem.get(key, {})
        sd = {name: s.get(f"{name}_sd") for name in emb_names}
        dem_sd = d.get("demographic_sd")
        sem_years, dem_years = int(s.get("sem_years", 0)), int(d.get("dem_years", 0))
        eligible = (
            n_papers >= _N_MIN and sem_years >= _Y_MIN and dem_years >= _Y_MIN
            and all(sd[n] is not None for n in emb_names) and dem_sd is not None
            and c.get("canon_concentration") is not None
        )
        rec: dict[str, Any] = {
            "subfield": key,
            "field": key.split(":")[0] if ":" in key else "cluster",
            "n_papers": n_papers, "log_size": float(np.log10(n_papers)),
            "canon_concentration": c.get("canon_concentration"),
            "ref_top_k": c.get("ref_top_k"),
            "canon_spearman_d5": c.get("canon_spearman_d5"),
            "demographic_trend": dem_sd,
            "sem_years": sem_years, "dem_years": dem_years,
            "eligible": bool(eligible),
        }
        for name in emb_names:
            rec[f"semantic_trend_{name}"] = sd[name]
        if eligible:
            for name in emb_names:
                rec[f"divergence_{name}"] = float(dem_sd) - float(sd[name])
            n_kept += 1
        records.append(rec)

    print(f"[{definition}] {n_kept}/{len(records)} subfields eligible "
          f"(N_MIN={_N_MIN}, Y_MIN={_Y_MIN})", flush=True)
    return {
        "definition": definition, "window": [_YEAR_MIN, _YEAR_MAX],
        "embeddings": emb_names,
        "n_min": _N_MIN, "y_min": _Y_MIN, "n_year_min": _N_YEAR_MIN,
        "mpc_sample": _MPC_SAMPLE, "seed": _SEED,
        "n_eligible": n_kept, "n_total": len(records), "subfields": records,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--embed-dir", required=True, type=Path)
    ap.add_argument("--source", required=True, type=Path)
    ap.add_argument("--demog-dir", required=True, type=Path)
    ap.add_argument("--subfield-dir", required=True, type=Path)
    ap.add_argument("--outdir", required=True, type=Path)
    ap.add_argument("--specter2-dir", type=Path, default=None,
                    help="dir with specter2-vectors.npy + metadata.parquet "
                         "(row-aligned to --embed-dir); adds the 3rd family")
    args = ap.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    meta = pd.read_parquet(args.embed_dir / "metadata.parquet")
    embeds: dict[str, Any] = {
        "scincl": np.load(args.embed_dir / "scincl-vectors.npy", mmap_mode="r"),
        "qwen3": np.load(args.embed_dir / "qwen3-vectors.npy", mmap_mode="r"),
    }
    print(f"loaded {len(meta):,} in-window papers + scincl/qwen3 vectors",
          flush=True)

    if args.specter2_dir is not None:
        s2_meta = pd.read_parquet(args.specter2_dir / "metadata.parquet")
        # Row-alignment is load-bearing: specter2 vectors must map to the SAME
        # metadata rows as scincl/qwen3. Assert paper_id order matches exactly.
        if not s2_meta["paper_id"].to_numpy().tolist() == meta[
                "paper_id"].to_numpy().tolist():
            raise ValueError(
                "specter2 metadata paper_id order != embed-dir metadata — "
                "vectors are NOT row-aligned; refusing to proceed")
        embeds["specter2"] = np.load(
            args.specter2_dir / "specter2-vectors.npy", mmap_mode="r")
        print(f"  + specter2 vectors (row-alignment verified)", flush=True)

    # refs from the source corpus, row-aligned to metadata (mirror compute_series)
    src = pq.read_table(
        str(args.source), columns=["id", "referenced_works_json"]).to_pandas()
    ref_map = dict(zip(src["id"], src["referenced_works_json"], strict=True))
    refs = meta["paper_id"].map(
        lambda pid: json.loads(str(ref_map.get(pid, "[]")))).to_numpy()
    print("joined referenced_works", flush=True)

    for definition, fname in (("concepts", "subfield-concepts.parquet"),
                              ("clusters", "subfield-clusters.parquet")):
        result = _assemble(
            definition, args.subfield_dir / fname, meta, embeds,
            refs, args.demog_dir)
        out = args.outdir / f"subfield-metrics-{definition}.json"
        out.write_text(json.dumps(result, indent=2))
        print(f"wrote {out}\n", flush=True)


if __name__ == "__main__":
    main()
