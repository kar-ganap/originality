"""Phase 1.2 Step 8 — nested sampling from §0 population.

Draws a deterministic sample of size N from the §0 population.
Uses NESTED SAMPLING: the population is sorted by a stable
seeded hash of paper-id; sample(N) is the first N rows. This
guarantees:

- sample(1M) ⊂ sample(2M) ⊂ sample(3M) ⊂ ... ⊂ population

Implication: if you embed sample(1M) now and later want sample(2M),
the embeddings for sample(1M) are reused; only the additional
1M needs new embedding. Saves Stage 2 / Stage 3 compute when
escalating N.

Default N = 1M (Wave 4A locked Stage 2 target). Re-run with
``--n 2000000`` for a 2M sample at any time; it's a strict
superset.

Usage:

  uv run python experiments/phase-1.2/sample.py --n 1000000
  uv run python experiments/phase-1.2/sample.py --n 2000000

Output: ``data/metadata/section0-sample-NM.parquet`` where N
is the sample size in millions (formatted ``{N//1_000_000}M``;
fractional Ns are written as full integers).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import polars as pl

_OUT_DIR = Path(__file__).parent
_DATA_METADATA_DIR = _OUT_DIR.parent.parent / "data" / "metadata"
_POPULATION_PARQUET = _DATA_METADATA_DIR / "section0-population.parquet"

# Pinned seed: changing this breaks the nesting property across
# previously-drawn samples. NEVER change once Stage 2 has begun.
_NESTING_SEED = "ws2-phase-1.2-nesting-seed-v1"


def _ordering_hash(paper_id: str) -> str:
    """Stable hash of paper_id + nesting seed; used as sort key.

    Using SHA-256 (truncated) ensures uniform random ordering
    given the seed; deterministic across machines + Python versions.
    """
    h = hashlib.sha256(
        f"{_NESTING_SEED}|{paper_id}".encode("utf-8"),
    ).hexdigest()
    return h


def _format_n_label(n: int) -> str:
    """1_000_000 → '1M'; 500_000 → '500K'; 1_500_000 → '1.5M'."""
    if n >= 1_000_000 and n % 1_000_000 == 0:
        return f"{n // 1_000_000}M"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000 and n % 1_000 == 0:
        return f"{n // 1_000}K"
    return str(n)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--n", type=int, default=1_000_000,
        help="Sample size (default: 1M)",
    )
    parser.add_argument(
        "--population", type=Path,
        default=_POPULATION_PARQUET,
        help=f"Population parquet path (default: {_POPULATION_PARQUET})",
    )
    parser.add_argument(
        "--out-dir", type=Path,
        default=_DATA_METADATA_DIR,
        help=f"Output directory (default: {_DATA_METADATA_DIR})",
    )
    args = parser.parse_args()

    if not args.population.exists():
        print(f"ERROR: population parquet not found at {args.population}")
        print("Run Phase 1.2 Step 7 first to produce it.")
        sys.exit(1)

    n_label = _format_n_label(args.n)
    out_path = args.out_dir / f"section0-sample-{n_label}.parquet"
    print(f"Phase 1.2 Step 8 — nested sampling N={args.n:,} ({n_label})")
    print(f"  population: {args.population}")
    print(f"  output:     {out_path}")
    print(f"  nesting seed: {_NESTING_SEED}")
    print()

    # 1. Load population (lazy)
    lf = pl.scan_parquet(args.population)
    n_population = int(lf.select(pl.len()).collect().item())
    print(f"  population size: {n_population:,}")

    if args.n > n_population:
        print(f"WARN: requested N={args.n:,} > population {n_population:,}")
        print(f"  → sample size capped at {n_population:,}")
        n_effective = n_population
    else:
        n_effective = args.n

    # 2. Compute ordering hash + sort + take first N
    # We need to load IDs to compute hashes (polars doesn't have a
    # streaming hash function directly). Load just the id column,
    # compute the sort key, then re-join with the full population
    # via id-based filter.
    print("  computing nesting hash...")
    ids_df = lf.select("id").collect()
    ids_list = ids_df["id"].to_list()
    print(f"  hashed {len(ids_list):,} ids")

    # Pair each id with its hash, sort, take first N ids
    print("  sorting + taking first N ids...")
    id_hashes = [
        (paper_id, _ordering_hash(paper_id)) for paper_id in ids_list
    ]
    id_hashes.sort(key=lambda x: x[1])
    selected_ids = {paper_id for paper_id, _ in id_hashes[:n_effective]}
    print(f"  selected {len(selected_ids):,} ids")

    # 3. Filter population to selected ids; write
    print("  filtering + writing parquet...")
    sample = lf.filter(pl.col("id").is_in(list(selected_ids))).collect()
    sample.write_parquet(out_path, compression="zstd")

    # Sanity: did we actually get N rows?
    n_actual = sample.height
    print(f"  wrote {n_actual:,} rows")

    if n_actual != n_effective:
        print(f"WARN: expected {n_effective:,} rows; got {n_actual:,}")
        print("  (could be due to dedup-prior-to-this-step or empty IDs)")

    # 4. Persist sample manifest
    snapshot = datetime.now(timezone.utc).isoformat(timespec="seconds")
    manifest_path = args.out_dir / f"section0-sample-{n_label}-manifest.json"
    manifest: dict[str, Any] = {
        "snapshot": snapshot,
        "sample_n_target": args.n,
        "sample_n_actual": n_actual,
        "n_label": n_label,
        "population_path": str(args.population),
        "population_n": n_population,
        "nesting_seed": _NESTING_SEED,
        "ordering_hash": "sha256(seed|paper_id)[:64]",
        "output_parquet": str(out_path),
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
