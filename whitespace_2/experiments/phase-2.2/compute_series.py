"""Phase 2.2 WS-D (semantic + canonical) — per-(field, year) annual series.

Computes, for CS and Physics over 1970-2024, from the base 1M SciNCL vectors +
metadata + the source corpus:

  SEMANTIC (SciNCL):
    - cluster_entropy   — over the §11 K=50 assignments (full year)
    - effective_dimensionality, mean_pairwise_cosine_distance — on a common
      per-(field,year) subsample of N_CAP (removes the N-confound; PA-3 flags
      years with < 768 papers as degenerate)
  CANONICAL:
    - reference_canonicity (PRIMARY, PA-1) — on the same N_CAP subsample
      (references from the source corpus; no counts_by_year, no accrual bias)
    - age_restricted_concentration (SECONDARY) — citation Gini/top-k, full
      year, N∈{3,5,10} sweep, snapshot 2026

The demographic series (joint career plurality) is computed separately once the
Phase-1.3 substrate is regenerated, and the divergence test is assembled in
`run_test.py`. Output: `experiments/phase-2.2/series/semantic-canonical.json`.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from whitespace2.canonical_metrics import (
    age_restricted_concentration,
    reference_canonicity,
)
from whitespace2.semantic_metrics import (
    cluster_entropy,
    effective_dimensionality,
    mean_pairwise_cosine_distance,
)

_OUT = Path(__file__).parent / "series"
_FIELDS = ("cs", "physics")
_YEARS = range(1970, 2025)
_K = 50
_N_CAP = 5000          # per-(field,year) subsample for N-sensitive metrics
_DEGEN_N = 768         # PA-3: effective_dim degenerate below this
_MPC_SAMPLE = 2000     # mean-pairwise-cosine subsample cap
_SNAPSHOT = 2026
_AGE_SWEEP = (3, 5, 10)
_SEED = 46


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--embed-dir", required=True, type=Path)
    ap.add_argument("--source", required=True, type=Path)
    args = ap.parse_args()
    _OUT.mkdir(parents=True, exist_ok=True)

    meta = pd.read_parquet(args.embed_dir / "metadata.parquet")
    assignments = np.load(args.embed_dir / "scincl-cluster-assignments.npy")
    vecs = np.load(args.embed_dir / "scincl-vectors.npy", mmap_mode="r")
    print(f"loaded {len(meta):,} papers; assignments {assignments.shape}",
          flush=True)

    # referenced_works from the source corpus, joined by paper_id → in-window rows
    print("loading referenced_works from source …", flush=True)
    src = pq.read_table(
        str(args.source), columns=["id", "referenced_works_json"],
    ).to_pandas()
    ref_map = dict(zip(src["id"], src["referenced_works_json"], strict=True))
    meta["refs"] = meta["paper_id"].map(
        lambda pid: json.loads(str(ref_map.get(pid, "[]"))),
    )
    print("  joined refs", flush=True)

    rng = np.random.default_rng(_SEED)
    out: dict[str, Any] = {"n_cap": _N_CAP, "snapshot": _SNAPSHOT,
                           "fields": {}}

    for field in _FIELDS:
        fmask = (meta["field"] == field).to_numpy()
        fyears = meta["year"].to_numpy()[fmask]
        f_assign = assignments[fmask]
        f_pos = np.nonzero(fmask)[0]          # global row indices for this field
        f_refs = meta["refs"].to_numpy()[fmask]
        f_cites = meta["cited_by_count"].to_numpy()[fmask]

        sem: dict[int, dict[str, Any]] = {}
        # subsample bookkeeping for reference_canonicity (capped per year)
        sub_years: list[int] = []
        sub_refs: list[Any] = []
        for y in _YEARS:
            ymask = fyears == y
            n = int(ymask.sum())
            if n == 0:
                continue
            ce = cluster_entropy(f_assign[ymask], _K)
            # common subsample for the N-sensitive metrics
            yidx = np.nonzero(ymask)[0]
            if n > _N_CAP:
                yidx = rng.choice(yidx, size=_N_CAP, replace=False)
            sub_vec = np.asarray(vecs[f_pos[yidx]], dtype=np.float32)
            ed = effective_dimensionality(sub_vec)
            mpc = mean_pairwise_cosine_distance(
                sub_vec, max_sample=_MPC_SAMPLE, seed=_SEED,
            )
            sem[int(y)] = {
                "cluster_entropy": round(float(ce), 5),
                "effective_dimensionality": round(float(ed), 4),
                "mean_pairwise_cosine": round(float(mpc), 6),
                "n": n, "n_used": int(len(yidx)),
                "degenerate": bool(len(yidx) < _DEGEN_N),
            }
            for gi in yidx:
                sub_years.append(int(y))
                sub_refs.append(f_refs[gi])

        ref_canon = reference_canonicity(
            np.array(sub_years), sub_refs, top_n=50, deltas=(5, 1),
        )
        age_restr = {
            str(N): age_restricted_concentration(
                fyears, f_cites, snapshot_year=_SNAPSHOT, min_age=N,
                min_papers=30,
            )
            for N in _AGE_SWEEP
        }
        out["fields"][field] = {
            "semantic": sem,
            "canonical": {"reference_canonicity": ref_canon,
                          "age_restricted": age_restr},
        }
        print(f"[{field}] {len(sem)} years semantic; "
              f"{len(ref_canon)} years ref-canon", flush=True)

    (_OUT / "semantic-canonical.json").write_text(json.dumps(out, indent=2))
    print(f"wrote {_OUT}/semantic-canonical.json", flush=True)


if __name__ == "__main__":
    main()
