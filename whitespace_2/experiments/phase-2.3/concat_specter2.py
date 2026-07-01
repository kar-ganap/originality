"""Phase 2.3 — concat the SPECTER2 volume chunks → row-aligned specter2-vectors.npy.

After `embed_specter2_vol.py` writes chunks to the ws2-embeddings volume, pull
them (`modal volume get ws2-embeddings /specter2-1m-chunks/ <dir>`) and run this
to concat in numeric id order into a single `(N, 768)` array, then verify the
row count matches the metadata (row-alignment is load-bearing downstream).
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import numpy as np
import pandas as pd


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chunk-dir", required=True, type=Path)
    ap.add_argument("--metadata", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    files = sorted(args.chunk_dir.glob("chunk_*.npy"),
                   key=lambda p: int(re.findall(r"\d+", p.name)[0]))
    if not files:
        raise SystemExit(f"no chunk_*.npy in {args.chunk_dir}")
    ids = [int(re.findall(r"\d+", p.name)[0]) for p in files]
    if ids != list(range(len(ids))):
        missing = sorted(set(range(max(ids) + 1)) - set(ids))
        raise SystemExit(f"chunk ids not contiguous 0..{max(ids)}; missing {missing[:20]}")

    parts = [np.load(p) for p in files]
    vecs = np.concatenate(parts, axis=0).astype(np.float32)
    meta = pd.read_parquet(args.metadata)
    print(f"concatenated {len(files)} chunks → {vecs.shape}; "
          f"metadata rows {len(meta)}")
    if vecs.shape[0] != len(meta):
        raise SystemExit(
            f"row mismatch: vectors {vecs.shape[0]} != metadata {len(meta)}")
    norms = np.linalg.norm(vecs, axis=1)
    print(f"all_finite={bool(np.isfinite(vecs).all())} "
          f"norm mean={norms.mean():.3f} [{norms.min():.3f}, {norms.max():.3f}]")
    np.save(args.out, vecs)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
