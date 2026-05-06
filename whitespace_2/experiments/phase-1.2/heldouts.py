"""Phase 1.2 Step 9 — generate held-out sets for Stage 2 §11 + drift.

Produces 4 held-out Parquet files (default 500 papers each), each
disjoint from the production §0 sample:

- heldout-1975-cs.parquet
- heldout-1975-physics.parquet
- heldout-2020-cs.parquet
- heldout-2020-physics.parquet

Why disjoint: Stage 2 §11 cluster-fit + drift validation require
held-out papers that were NOT in the training set (the sample is
what feeds Stage 2's embedding pipeline; held-out papers must be
unseen to give honest drift estimates).

Why these 4 cells: 1975 + 2020 spans the era boundary near which
embedding-drift effects are believed strongest; cs + physics
covers both fields in the population.

Server-side execution: the population parquet stays on the Modal
Volume (~3 GB compressed; expensive to download just to filter).
Modal does the per-cell year + field filter + anti-join + hash-
rank + parquet write; local downloads only the 4 small held-outs
(<10 MB each) plus a manifest.

Usage:

  uv run --with modal python experiments/phase-1.2/heldouts.py
  uv run --with modal python experiments/phase-1.2/heldouts.py --n-per 500
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import modal

generate_heldouts = modal.Function.from_name(
    "ws2-parse", "generate_heldouts",
)
section0_volume = modal.Volume.from_name(
    "ws2-section0", create_if_missing=False,
)

_OUT_DIR = Path(__file__).parent
_DATA_METADATA_DIR = _OUT_DIR.parent.parent / "data" / "metadata"

# Pinned seed: must match parse_modal.py::generate_heldouts.
# Different from the sample's nesting seed so held-outs aren't
# correlated with sample-membership beyond the disjointness
# constraint enforced by the anti-join.
_HELDOUT_SEED = "ws2-phase-1.2-heldout-seed-v1"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sample-filename", default="section0-sample-1M.parquet",
        help="Sample parquet filename on the Volume (default: 1M sample)",
    )
    parser.add_argument(
        "--n-per", type=int, default=500,
        help="Number of papers per held-out cell (default: 500)",
    )
    parser.add_argument(
        "--out-dir", type=Path,
        default=_DATA_METADATA_DIR,
        help=f"Local output directory (default: {_DATA_METADATA_DIR})",
    )
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Phase 1.2 Step 9 — held-out generation (n_per={args.n_per})")
    print(f"  sample: {args.sample_filename}")
    print(f"  heldout seed: {_HELDOUT_SEED}")
    print()

    # Server-side: filter + anti-join + hash-rank + write 4 cells
    print("Calling generate_heldouts.remote() on Modal...")
    t_start = time.time()
    result: dict[str, Any] = generate_heldouts.remote(
        args.sample_filename, args.n_per,
    )
    elapsed_remote = time.time() - t_start
    print(f"  done in {elapsed_remote:.0f}s")
    for cell in result["cells"]:
        print(f"  {cell['filename']}: "
              f"{cell['n_actual']}/{cell['n_target']} "
              f"({cell['elapsed_sec']:.0f}s)")

    # Download each cell
    print()
    print(f"Downloading {len(result['cells'])} held-out parquets to local...")
    download_log: list[dict[str, Any]] = []
    for cell in result["cells"]:
        filename = cell["filename"]
        local_path = args.out_dir / filename
        t_dl = time.time()
        with local_path.open("wb") as f:
            for chunk in section0_volume.read_file(filename):
                f.write(chunk)
        size_kb = local_path.stat().st_size / 1024
        elapsed_dl = time.time() - t_dl
        download_log.append({
            **cell,
            "local_path": str(local_path),
            "size_kb": size_kb,
            "elapsed_download_sec": elapsed_dl,
        })
        print(f"  {filename}: {size_kb:.0f} KB ({elapsed_dl:.1f}s)")

    # Manifest
    snapshot = datetime.now(timezone.utc).isoformat(timespec="seconds")
    manifest_path = args.out_dir / "heldouts-manifest.json"
    manifest = {
        "snapshot": snapshot,
        "n_per": args.n_per,
        "heldout_seed": _HELDOUT_SEED,
        "sample_filename": args.sample_filename,
        "n_sample_excluded": result["n_sample_excluded"],
        "population_path_volume": (
            "modal://ws2-section0/section0-population.parquet"
        ),
        "elapsed_remote_sec": elapsed_remote,
        "cells": download_log,
        "field_detection": (
            "strict: concepts_json contains a concept with matching id "
            "AND score >= 0.30 (mirrors §0 threshold)"
        ),
        "ordering_hash": (
            "duckdb_hash(HELDOUT_SEED || id) uint64; per-cell ordering"
        ),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print()
    print(f"Wrote {manifest_path}")
    print()
    print("Step 9 complete.")


if __name__ == "__main__":
    main()
