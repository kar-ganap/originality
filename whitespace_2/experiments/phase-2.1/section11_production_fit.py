"""Phase 2.1 WS1 — §11 production cluster fit on the base 1M SciNCL vectors.

Loads the WS4 base 1M v3 SciNCL embeddings + row-aligned metadata, builds a
decade-balanced fit sample (the §11 temporal stratification), fits K=50
clusters (locked params) via ``src/whitespace2/cluster_fit``, projects all
~900K in-window papers, and reports the assignment distribution +
``cluster_entropy``. Cross-checks the committed Phase-0.2 SciNCL centroids
(``data/metadata/section11-cluster-fit-S-K50-scincl.npy``) by re-projecting
the full sample through them and comparing entropy / effective-N.

The production centroids are committed (small, reproducible); the per-paper
assignments are written to the run dir (regenerable via
``project_to_clusters(vectors, centroids)``) as the Phase-2.2 semantic-series
input.

Usage:
  uv run python experiments/phase-2.1/section11_production_fit.py \
      --vectors  <scratchpad>/embed-1m/scincl-vectors.npy \
      --metadata <scratchpad>/embed-1m/metadata.parquet \
      --outdir   <scratchpad>/embed-1m
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from whitespace2.cluster_fit import (
    build_decade_stratified_sample,
    fit_clusters,
    project_to_clusters,
)
from whitespace2.semantic_metrics import cluster_entropy

_OUT_DIR = Path(__file__).parent
_DATA_METADATA = _OUT_DIR.parent.parent / "data" / "metadata"
_COMMITTED_CENTROIDS = _DATA_METADATA / "section11-cluster-fit-S-K50-scincl.npy"
_FIT_SEED = 46
_PROJECT_BATCH = 100_000


def _project_all(vectors: Any, centroids: Any) -> np.ndarray[Any, Any]:
    """Batched projection to bound the float64 normalize temp at ~600 MB."""
    parts: list[np.ndarray[Any, Any]] = []
    for start in range(0, len(vectors), _PROJECT_BATCH):
        parts.append(
            project_to_clusters(vectors[start:start + _PROJECT_BATCH], centroids),
        )
    return np.concatenate(parts)


def _cluster_stats(assignments: Any, k: int) -> dict[str, Any]:
    counts = np.bincount(np.asarray(assignments), minlength=k)
    n = int(counts.sum())
    ent = cluster_entropy(assignments, k)
    return {
        "n": n,
        "cluster_entropy": round(float(ent), 5),
        "effective_n_clusters": round(float(np.exp(ent)), 3),
        "n_empty_clusters": int((counts == 0).sum()),
        "min_cluster": int(counts.min()),
        "max_cluster": int(counts.max()),
        "max_cluster_share": round(float(counts.max() / n), 5) if n else 0.0,
        "median_cluster": float(np.median(counts)),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--vectors", required=True, type=Path)
    ap.add_argument("--metadata", required=True, type=Path)
    ap.add_argument("--outdir", required=True, type=Path)
    ap.add_argument("--k", type=int, default=50)
    ap.add_argument("--n-per-decade", type=int, default=10_000)
    ap.add_argument("--committed-centroids", type=Path,
                    default=_COMMITTED_CENTROIDS)
    args = ap.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    print(f"loading vectors {args.vectors} …", flush=True)
    vectors = np.load(args.vectors)
    meta = pd.read_parquet(args.metadata)
    years = meta["year"].to_numpy()
    assert len(vectors) == len(meta), (len(vectors), len(meta))
    print(f"  {len(vectors):,} × {vectors.shape[1]} vectors; "
          f"years {int(years.min())}-{int(years.max())}", flush=True)

    # ---- §11 decade-balanced fit sample ----
    sample_idx = build_decade_stratified_sample(
        years, n_per_decade=args.n_per_decade, seed=_FIT_SEED,
    )
    print(f"decade-balanced fit sample: {len(sample_idx):,} papers "
          f"(target {args.n_per_decade}/decade)", flush=True)

    # ---- fit K=50 on the balanced sample ----
    print(f"fitting K={args.k} (n_init=20, random_state=46) …", flush=True)
    centroids = fit_clusters(vectors[sample_idx], k=args.k)
    centroid_norms = np.linalg.norm(centroids, axis=1)
    print(f"  centroids {centroids.shape}; norm mean "
          f"{centroid_norms.mean():.4f} (expect ~0.92-0.94)", flush=True)

    # ---- project ALL papers ----
    print("projecting all papers …", flush=True)
    assignments = _project_all(vectors, centroids)
    prod = _cluster_stats(assignments, args.k)
    print(f"  production fit: {json.dumps(prod)}", flush=True)

    # ---- cross-check vs committed Phase-0.2 SciNCL centroids ----
    cross: dict[str, Any] = {"available": False}
    if args.committed_centroids.exists():
        committed = np.load(args.committed_centroids)
        committed_assign = _project_all(vectors, committed)
        cross = {
            "available": True,
            "path": str(args.committed_centroids),
            "committed_k": int(committed.shape[0]),
            "committed_norm_mean": round(
                float(np.linalg.norm(committed, axis=1).mean()), 4),
            **{f"committed_{kk}": vv
               for kk, vv in _cluster_stats(committed_assign, args.k).items()},
        }
        print(f"  cross-check (committed centroids): {json.dumps(cross)}",
              flush=True)

    # ---- persist ----
    centroids_out = _DATA_METADATA / f"section11-prod-fit-K{args.k}-scincl-1m.npy"
    np.save(centroids_out, centroids.astype(np.float32))
    np.save(args.outdir / "scincl-cluster-assignments.npy",
            assignments.astype(np.int32))

    summary = {
        "snapshot": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "n_papers": int(len(vectors)),
        "k": args.k,
        "n_per_decade": args.n_per_decade,
        "fit_sample_size": int(len(sample_idx)),
        "fit_seed": _FIT_SEED,
        "centroid_norm_mean": round(float(centroid_norms.mean()), 4),
        "production": prod,
        "cross_check": cross,
        "centroids_committed_to": str(centroids_out),
    }
    (args.outdir / "section11-prod-fit-summary.json").write_text(
        json.dumps(summary, indent=2))
    print(f"\nDONE. centroids → {centroids_out}", flush=True)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
