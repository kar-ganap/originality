"""Phase 2.3 — build the two paper→subfield maps (the subfield-definition pair).

  DEF-1 (PRIMARY) — OpenAlex level-1 sub-concepts. `build_paper_subfield_map`
    on the §0 source corpus → paper_id → "{field}:{concept_id}" (argmax
    highest-scoring level-1 concept within each field's papers).
  DEF-2 (ROBUSTNESS) — §11 K=50 SciNCL clusters. paper_id → "cluster:{k}"
    from the in-window metadata + committed cluster assignments.

Both maps use the `primary_field` column name so they are drop-in for the
Phase-1.3 demographic pipeline (`build_joint_plurality_series`). Also prints
the subfield-size distribution + how many clear the pre-registered N_MIN=2000
inclusion floor (a sanity checkpoint before the heavy metric compute).

Output: `<outdir>/subfield-concepts.parquet`, `<outdir>/subfield-clusters.parquet`.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from whitespace2.subfield_divergence import build_paper_subfield_map

_N_MIN = 2000     # pre-registered subfield inclusion floor (papers)


def _cluster_map(embed_dir: Path, out: Path) -> pd.DataFrame:
    """paper_id → 'cluster:{k}' from metadata + §11 K=50 assignments."""
    meta = pd.read_parquet(embed_dir / "metadata.parquet")
    assign = np.load(embed_dir / "scincl-cluster-assignments.npy")
    if len(meta) != len(assign):
        raise ValueError(
            f"metadata rows {len(meta)} != assignments {len(assign)}")
    df = pd.DataFrame({
        "paper_id": meta["paper_id"].to_numpy(),
        "primary_field": [f"cluster:{int(k)}" for k in assign],
    })
    pq.write_table(pa.Table.from_pandas(df, preserve_index=False), str(out))
    return df


def _report(df: pd.DataFrame, label: str) -> None:
    counts = df["primary_field"].value_counts()
    kept = counts[counts >= _N_MIN]
    print(f"\n[{label}] {len(counts)} subfields; "
          f"{len(kept)} clear N_MIN={_N_MIN} "
          f"(covering {int(kept.sum()):,}/{int(counts.sum()):,} papers)")
    print(f"  size: min {int(counts.min())}, median {int(counts.median())}, "
          f"max {int(counts.max())}")
    print(f"  top 8 kept: "
          f"{[(k.split(':')[-1][:16], int(v)) for k, v in kept.head(8).items()]}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, type=Path)
    ap.add_argument("--embed-dir", required=True, type=Path)
    ap.add_argument("--outdir", required=True, type=Path)
    args = ap.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    # DEF-1 — level-1 sub-concepts (both fields; keyed by "{field}:{concept}")
    concepts_out = args.outdir / "subfield-concepts.parquet"
    stats = build_paper_subfield_map(
        args.source, concepts_out, field_filter=None, level=1)
    print(f"concepts map: {stats}")
    _report(pq.read_table(concepts_out).to_pandas(), "concepts (level-1)")

    # DEF-2 — K=50 SciNCL clusters
    clusters_out = args.outdir / "subfield-clusters.parquet"
    cdf = _cluster_map(args.embed_dir, clusters_out)
    _report(cdf, "clusters (K=50)")

    print(f"\nwrote {concepts_out}\nwrote {clusters_out}")


if __name__ == "__main__":
    main()
