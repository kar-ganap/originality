"""Phase 1.2 retro — build v3 artifacts after the §0 H2-audit amendments.

Pipeline (server-side; only the small derived artifacts hit local):

1. ``filter_population_v3`` — apply v3 amendments (concept-score
   0.40, token-min 50, abstract-prefix blacklist, title-prefix
   blacklist) to v2, producing ``section0-population-v3.parquet``
   on the Volume.
2. ``sample_population`` (with v3 source) — produce
   ``section0-sample-1M-v3.parquet`` on the Volume + download.
3. ``generate_heldouts`` (with v3 source + sample) — produce four
   ``heldout-{year}-{field}-v3.parquet`` files on the Volume +
   download.

v1 + v2 artifacts stay on the Volume for the audit trail and the
robustness-pair analysis in the Phase 1.2 RETRO.

Deploy reminder: if you edited ``parse_modal.py`` (e.g., added or
changed ``filter_population_v3``) and re-deployed but Modal says
"Deployment skipped: no changes detected", force-stop the app
first:

  modal app stop -y ws2-parse
  modal deploy experiments/phase-1.2/parse_modal.py

Usage:

  uv run --with modal python experiments/phase-1.2/build_v3.py

Cost: ~$5 (filter + sample + heldouts on 32 GB / 512 GB-disk
containers).
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import modal

filter_population_v3 = modal.Function.from_name(
    "ws2-parse", "filter_population_v3",
)
sample_population = modal.Function.from_name(
    "ws2-parse", "sample_population",
)
generate_heldouts = modal.Function.from_name(
    "ws2-parse", "generate_heldouts",
)
section0_volume = modal.Volume.from_name(
    "ws2-section0", create_if_missing=False,
)

_OUT_DIR = Path(__file__).parent
_DATA_METADATA_DIR = _OUT_DIR.parent.parent / "data" / "metadata"


def _download(volume_filename: str, local_path: Path) -> dict[str, Any]:
    t = time.time()
    with local_path.open("wb") as f:
        for chunk in section0_volume.read_file(volume_filename):
            f.write(chunk)
    elapsed = time.time() - t
    size_mb = local_path.stat().st_size / 1e6
    return {
        "volume_filename": volume_filename,
        "local_path": str(local_path),
        "size_mb": size_mb,
        "elapsed_sec": elapsed,
    }


def main() -> None:
    n_sample = 1_000_000
    print("Phase 1.2 v3 build — H2 audit retro amendments")
    print()
    _DATA_METADATA_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Filter population
    print("[1/4] filter_population_v3.remote()...")
    t0 = time.time()
    filter_result: dict[str, Any] = filter_population_v3.remote()
    print(
        f"      v2: {filter_result['n_v2']:,} → v3: {filter_result['n_v3']:,} "
        f"({100*filter_result['kept_fraction']:.2f}% kept; "
        f"{time.time()-t0:.0f}s)"
    )
    print()

    # 2. Sample
    print("[2/4] sample_population.remote(n=1M, source=v3)...")
    t0 = time.time()
    sample_result: dict[str, Any] = sample_population.remote(
        n_sample,
        "section0-population-v3.parquet",
        "-v3",
    )
    print(
        f"      sample {sample_result['n_label']}: "
        f"{sample_result['n_actual']:,} ({time.time()-t0:.0f}s)"
    )
    sample_filename_v3 = (
        f"section0-sample-{sample_result['n_label']}-v3.parquet"
    )

    # Download sample
    print(f"      downloading {sample_filename_v3}...")
    sample_dl = _download(
        sample_filename_v3,
        _DATA_METADATA_DIR / sample_filename_v3,
    )
    print(
        f"      wrote {sample_dl['local_path']} "
        f"({sample_dl['size_mb']:.1f} MB, {sample_dl['elapsed_sec']:.0f}s)"
    )
    print()

    # 3. Heldouts
    print(
        f"[3/4] generate_heldouts.remote(sample={sample_filename_v3}, "
        "source=v3, suffix=-v3)..."
    )
    t0 = time.time()
    heldout_result: dict[str, Any] = generate_heldouts.remote(
        sample_filename_v3,
        500,
        "section0-population-v3.parquet",
        "-v3",
    )
    print(
        f"      {len(heldout_result['cells'])} cells in "
        f"{time.time()-t0:.0f}s"
    )
    for cell in heldout_result["cells"]:
        print(
            f"        {cell['filename']}: "
            f"{cell['n_actual']}/{cell['n_target']}"
        )
    print()

    # Download heldouts
    print("[4/4] downloading held-out cells...")
    heldout_dl = []
    for cell in heldout_result["cells"]:
        dl = _download(
            cell["filename"], _DATA_METADATA_DIR / cell["filename"],
        )
        dl_combined: dict[str, Any] = {**cell, **dl}
        heldout_dl.append(dl_combined)
        print(f"      {cell['filename']}: {dl['size_mb']*1024:.0f} KB")
    print()

    # Manifests
    snapshot = datetime.now(timezone.utc).isoformat(timespec="seconds")
    n_label = sample_result["n_label"]
    sample_manifest = (
        _DATA_METADATA_DIR
        / f"section0-sample-{n_label}-v3-manifest.json"
    )
    sample_manifest.write_text(json.dumps({
        "snapshot": snapshot,
        "version": "v3",
        "v3_amendments": [
            "concept-score 0.30 → 0.40",
            "abstract-token-min 15 → 50",
            "abstract-prefix blacklist (publisher chrome)",
            "title-prefix blacklist (non-paper artifacts)",
        ],
        "sample_n_target": n_sample,
        "sample_n_actual": sample_result["n_actual"],
        "n_label": sample_result["n_label"],
        "population_path_volume": (
            "modal://ws2-section0/section0-population-v3.parquet"
        ),
        "population_n_v2": filter_result["n_v2"],
        "population_n_v3": filter_result["n_v3"],
        "kept_fraction_v2_to_v3": filter_result["kept_fraction"],
        "score_threshold_v3": filter_result["score_threshold_v3"],
        "min_tokens_v3": filter_result["min_tokens_v3"],
        "stage_drops_independent": filter_result[
            "stage_drops_independent"
        ],
        "nesting_seed": "ws2-phase-1.2-nesting-seed-v1",
        "ordering_hash": "duckdb_hash(seed||paper_id) uint64",
        "sample_path_volume": sample_result["output"],
        "sample_path_local": sample_dl["local_path"],
        "sample_size_mb": sample_dl["size_mb"],
    }, indent=2))
    print(f"Wrote {sample_manifest}")

    heldouts_manifest = _DATA_METADATA_DIR / "heldouts-v3-manifest.json"
    heldouts_manifest.write_text(json.dumps({
        "snapshot": snapshot,
        "version": "v3",
        "v3_amendments": [
            "concept-score 0.30 → 0.40",
            "abstract-token-min 15 → 50",
            "abstract-prefix blacklist (publisher chrome)",
            "title-prefix blacklist (non-paper artifacts)",
        ],
        "n_per": 500,
        "heldout_seed": "ws2-phase-1.2-heldout-seed-v1",
        "sample_filename": sample_filename_v3,
        "n_sample_excluded": heldout_result["n_sample_excluded"],
        "population_path_volume": (
            "modal://ws2-section0/section0-population-v3.parquet"
        ),
        "cells": heldout_dl,
    }, indent=2))
    print(f"Wrote {heldouts_manifest}")
    print()
    print(
        "v3 build complete. Next: run h2_audit_generate.py against "
        "the v3 sample:"
    )
    print(
        "  uv run --with duckdb python experiments/phase-1.2/"
        "h2_audit_generate.py \\"
    )
    print(
        f"    --sample data/metadata/{sample_filename_v3} \\"
    )
    print(
        "    --out experiments/phase-1.2/h2-audit-sheet-v3.md"
    )


if __name__ == "__main__":
    main()
