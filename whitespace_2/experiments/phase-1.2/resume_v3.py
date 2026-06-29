"""Phase 1.2 retro — resume v3 build after the sample download hang.

The full build (build_v3.py) got through filter + sample, and the
sample parquet wrote fully to disk (310 MB) — but the Modal Volume
read iterator never returned, leaving the local process hung in
sleep state. After ~50 min idle, the process was killed.

State at resume:
- ``section0-population-v3.parquet`` is on the Modal Volume.
- ``section0-sample-1M-v3.parquet`` is on the Modal Volume and on
  local disk.
- Heldouts have NOT been generated. No v3 manifests exist locally.

This script picks up at step 3 (heldouts) and step 4 (manifests).
Values for the sample/filter manifests are taken from the build
log (committed in ``build-v3-log.txt``).

Usage:

  uv run --with modal python experiments/phase-1.2/resume_v3.py
"""

from __future__ import annotations

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


# Values from build-v3-log.txt (committed).
_FILTER_RESULT = {
    "n_v2": 38_697_769,
    "n_v3": 24_492_279,
    "kept_fraction": 24_492_279 / 38_697_769,
    "score_threshold_v3": 0.40,
    "min_tokens_v3": 50,
    "stage_drops_independent": {
        "score_ge_0.40": {
            "n_passes": 27_319_136, "n_drops": 11_378_633,
        },
        "tokens_ge_50": {
            "n_passes": 34_310_592, "n_drops": 4_387_177,
        },
        "abstract_prefix_ok": {
            "n_passes": 38_202_515, "n_drops": 495_254,
        },
        "title_prefix_ok": {
            "n_passes": 38_692_362, "n_drops": 5_407,
        },
    },
}
_SAMPLE_FILENAME_V3 = "section0-sample-1M-v3.parquet"
_SAMPLE_RESULT = {
    "n_label": "1M",
    "n_actual": 1_000_000,
    "output": f"/output/{_SAMPLE_FILENAME_V3}",
}


def _download(
    volume_filename: str, local_path: Path, timeout_sec: float = 180,
) -> dict[str, Any]:
    """Stream a file from Volume → local with a per-chunk timeout
    guard. The build_v3 hang was the volume-read iterator never
    returning after the file fully wrote; if we don't see a new
    chunk for ``timeout_sec`` seconds we abort.
    """
    t = time.time()
    with local_path.open("wb") as f:
        last_chunk_t = time.time()
        for chunk in section0_volume.read_file(volume_filename):
            f.write(chunk)
            now = time.time()
            if now - last_chunk_t > timeout_sec:
                raise TimeoutError(
                    f"Download stalled (no chunks for "
                    f"{timeout_sec}s): {volume_filename}"
                )
            last_chunk_t = now
    elapsed = time.time() - t
    size_mb = local_path.stat().st_size / 1e6
    return {
        "volume_filename": volume_filename,
        "local_path": str(local_path),
        "size_mb": size_mb,
        "elapsed_sec": elapsed,
    }


def main() -> None:
    print("Phase 1.2 v3 build — resume after sample-download hang")
    print()

    # 3. Heldouts
    print(
        f"[3/4] generate_heldouts.remote(sample={_SAMPLE_FILENAME_V3}, "
        "source=v3, suffix=-v3)..."
    )
    t0 = time.time()
    heldout_result: dict[str, Any] = generate_heldouts.remote(
        _SAMPLE_FILENAME_V3,
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

    # Download heldouts (small files; the hang earlier was on the
    # 310 MB sample; ~500 KB heldouts should be quick).
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
    n_label = _SAMPLE_RESULT["n_label"]
    sample_local = _DATA_METADATA_DIR / _SAMPLE_FILENAME_V3
    sample_size_mb = sample_local.stat().st_size / 1e6

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
        "sample_n_target": 1_000_000,
        "sample_n_actual": _SAMPLE_RESULT["n_actual"],
        "n_label": _SAMPLE_RESULT["n_label"],
        "population_path_volume": (
            "modal://ws2-section0/section0-population-v3.parquet"
        ),
        "population_n_v2": _FILTER_RESULT["n_v2"],
        "population_n_v3": _FILTER_RESULT["n_v3"],
        "kept_fraction_v2_to_v3": _FILTER_RESULT["kept_fraction"],
        "score_threshold_v3": _FILTER_RESULT["score_threshold_v3"],
        "min_tokens_v3": _FILTER_RESULT["min_tokens_v3"],
        "stage_drops_independent": _FILTER_RESULT[
            "stage_drops_independent"
        ],
        "nesting_seed": "ws2-phase-1.2-nesting-seed-v1",
        "ordering_hash": "duckdb_hash(seed||paper_id) uint64",
        "sample_path_volume": _SAMPLE_RESULT["output"],
        "sample_path_local": str(sample_local),
        "sample_size_mb": sample_size_mb,
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
        "sample_filename": _SAMPLE_FILENAME_V3,
        "n_sample_excluded": heldout_result["n_sample_excluded"],
        "population_path_volume": (
            "modal://ws2-section0/section0-population-v3.parquet"
        ),
        "cells": heldout_dl,
    }, indent=2))
    print(f"Wrote {heldouts_manifest}")
    print()
    print(
        "v3 build complete. Next: run h2_audit_generate.py "
        "against the v3 sample."
    )


if __name__ == "__main__":
    main()
