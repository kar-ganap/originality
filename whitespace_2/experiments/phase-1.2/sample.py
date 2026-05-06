"""Phase 1.2 Step 8 — nested sampling from §0 population (server-side).

Calls the deployed ``sample_population`` Modal function to draw a
deterministic sample of size N from the §0 population on the Modal
Volume, then downloads only the sample (~1 GB for N=1M) to local.

Why server-side: the §0 population parquet is ~70-100 GB; downloading
it just to sample 1M rows wastes bandwidth + local disk. Modal does
the hash-ordered sample on the volume and returns just the sample.

Nested sampling: rows ordered by ``hash(seed|paper_id)``; the first N
form the sample. This guarantees:

- sample(1M) ⊂ sample(2M) ⊂ sample(3M) ⊂ ... ⊂ population

Implication: if you embed sample(1M) now and later want sample(2M),
the embeddings for sample(1M) are reused; only the additional 1M
needs new embedding. Saves Stage 2 / Stage 3 compute when escalating N.

Default N = 1M (Wave 4A locked Stage 2 target). Re-run with
``--n 2000000`` for a 2M sample at any time; it's a strict superset.

Usage:

  uv run python experiments/phase-1.2/sample.py --n 1000000
  uv run python experiments/phase-1.2/sample.py --n 2000000

Output:

- Volume: ``/output/section0-sample-<N_LABEL>.parquet`` (server-side)
- Local:  ``data/metadata/section0-sample-<N_LABEL>.parquet`` (download)
- Local:  ``data/metadata/section0-sample-<N_LABEL>-manifest.json``

Where ``<N_LABEL>`` is "1M" for 1_000_000, "500K" for 500_000, etc.
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import modal

# Lookup the deployed sample_population Modal function.
sample_population = modal.Function.from_name(
    "ws2-parse", "sample_population",
)
section0_volume = modal.Volume.from_name(
    "ws2-section0", create_if_missing=False,
)

_OUT_DIR = Path(__file__).parent
_DATA_METADATA_DIR = _OUT_DIR.parent.parent / "data" / "metadata"

# Pinned seed: must match parse_modal.py::sample_population.
# Changing this breaks the nesting property across previously-drawn
# samples. NEVER change once Stage 2 has begun.
_NESTING_SEED = "ws2-phase-1.2-nesting-seed-v1"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--n", type=int, default=1_000_000,
        help="Sample size (default: 1M)",
    )
    parser.add_argument(
        "--out-dir", type=Path,
        default=_DATA_METADATA_DIR,
        help=f"Local output directory (default: {_DATA_METADATA_DIR})",
    )
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Phase 1.2 Step 8 — nested sampling N={args.n:,}")
    print(f"  nesting seed: {_NESTING_SEED}")
    print()

    # 1. Server-side sample on Modal
    print("Calling sample_population.remote() on Modal...")
    t_start = time.time()
    result: dict[str, Any] = sample_population.remote(args.n)
    elapsed_remote = time.time() - t_start
    n_label = result["n_label"]
    print(f"  done in {elapsed_remote:.0f}s")
    print(f"  population size: {result['n_population']:,}")
    print(f"  sample size:     {result['n_actual']:,} ({n_label})")
    print(f"  volume path:     {result['output']}")

    # 2. Download just the sample to local
    sample_filename = f"section0-sample-{n_label}.parquet"
    local_path = args.out_dir / sample_filename
    print()
    print(f"Downloading {sample_filename} from Volume to local...")
    t_start = time.time()
    with local_path.open("wb") as f:
        for chunk in section0_volume.read_file(sample_filename):
            f.write(chunk)
    elapsed_dl = time.time() - t_start
    size_mb = local_path.stat().st_size / 1e6
    print(f"  wrote {local_path} ({size_mb:.1f} MB, {elapsed_dl:.0f}s)")

    # 3. Persist sample manifest
    snapshot = datetime.now(timezone.utc).isoformat(timespec="seconds")
    manifest_path = args.out_dir / f"section0-sample-{n_label}-manifest.json"
    manifest: dict[str, Any] = {
        "snapshot": snapshot,
        "sample_n_target": args.n,
        "sample_n_actual": result["n_actual"],
        "n_label": n_label,
        "population_n": result["n_population"],
        "population_path_volume": (
            "modal://ws2-section0/section0-population.parquet"
        ),
        "nesting_seed": _NESTING_SEED,
        "ordering_hash": "duckdb_hash(seed||paper_id) uint64",
        "sample_path_volume": result["output"],
        "sample_path_local": str(local_path),
        "sample_size_mb": size_mb,
        "elapsed_remote_sec": elapsed_remote,
        "elapsed_download_sec": elapsed_dl,
        "nesting_property": (
            "sample(M) ⊂ sample(N) for any M ≤ N drawn with the same "
            "nesting_seed; embeddings of sample(M) reusable when "
            "escalating to sample(N)"
        ),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2))
    print(f"  wrote {manifest_path}")
    print()
    print(f"Sample {n_label} complete.")


if __name__ == "__main__":
    main()
