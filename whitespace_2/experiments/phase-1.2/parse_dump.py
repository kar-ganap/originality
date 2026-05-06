"""Phase 1.2 Step 4 — Local orchestrator for the bulk-dump parse.

Loads the works manifest (Step 1), filters out shards already
processed (Volume idempotency), dispatches the remaining shards
via ``parse_one_shard.map()``, then triggers the dedup pass.

Resumability: re-running the orchestrator after a crash or
network drop picks up where it left off — the
``parse_one_shard`` Modal function writes per-shard Parquet
to a Modal Volume; a re-run lists the Volume and skips
already-done shards.

Usage:

  # 5-shard parallel smoke (Step 6):
  modal run experiments/phase-1.2/parse_dump.py::smoke_5_shards

  # Full 2,127-shard pull (Step 7):
  modal run experiments/phase-1.2/parse_dump.py::main

The local entrypoint completes when:
1. All shards are processed (or marked failed), AND
2. The dedup pass has produced section0-population.parquet on
   the Modal Volume.

The §0 population parquet stays on the Modal Volume — at
~70-100 GB it's too large to download locally for marginal
gain. Sampling (Step 8) runs server-side; only the ~1 GB
sample is downloaded to local. See ``docs/phases/phase-1.2-plan.md``
for context.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import modal

# Local app for this script's entrypoint. Calls into the deployed
# ws2-parse app's functions.
app = modal.App("phase-1.2-orchestrator")

# Lookup the deployed Modal Functions by name.
parse_one_shard = modal.Function.from_name("ws2-parse", "parse_one_shard")
dedup_to_population = modal.Function.from_name(
    "ws2-parse", "dedup_to_population",
)

# Volume for downloading the final population parquet
section0_volume = modal.Volume.from_name(
    "ws2-section0", create_if_missing=True,
)

# ---------- paths ----------

_OUT_DIR = Path(__file__).parent
_MANIFEST_PATH = _OUT_DIR / "openalex-works-manifest.json"
_DATA_METADATA_DIR = _OUT_DIR.parent.parent / "data" / "metadata"
_RESULTS_LOG = _OUT_DIR / "parse-results.json"


# ---------- helpers ----------


def _load_manifest() -> list[str]:
    """Returns shard URLs from the manifest, in manifest order."""
    with _MANIFEST_PATH.open() as f:
        m = json.load(f)
    return [e["url"] for e in m["entries"]]


def _shard_output_filename(shard_url: str) -> str:
    """Mirror of parse_modal._shard_output_filename for local-side checks."""
    from pathlib import PurePosixPath

    parts = PurePosixPath(shard_url).parts
    date_part = next(
        (p for p in parts if p.startswith("updated_date=")), "unknown_date",
    )
    date_str = date_part.split("=", 1)[-1]
    fname_part = parts[-1]
    fname_stem = fname_part.removesuffix(".gz")
    return f"{date_str}_{fname_stem}.parquet"


def _list_done_shards() -> set[str]:
    """List Volume; return the set of shard output filenames present."""
    # Modal Volume listing API; iterates lazily over the volume
    done = set()
    for entry in section0_volume.iterdir("/"):
        # entry is a FileEntry; entry.path is like "/2026-01-13_part_0042.parquet"
        # entry.path is bytes/str depending on Modal version
        path_str = (
            entry.path if isinstance(entry.path, str)
            else entry.path.decode("utf-8")
        )
        # strip leading slash
        name = path_str.lstrip("/")
        if name.endswith(".parquet") and "_part_" in name:
            done.add(name)
    return done


def _filter_remaining(
    all_shards: list[str], done_filenames: set[str],
) -> list[str]:
    return [
        url for url in all_shards
        if _shard_output_filename(url) not in done_filenames
    ]


# ---------- 5-shard smoke (Step 6) ----------


@app.local_entrypoint()
def smoke_5_shards() -> None:
    """Phase 1.2 Step 6 — 5-shard parallel .map() smoke.

    Picks 5 representative shards (mix of small + large from the
    manifest) and runs them in parallel. Verifies that .map()
    parallelism works + per-shard yield is in expected band.

    Cost: ~$0.50.
    """
    print("Phase 1.2 Step 6 — 5-shard parallel smoke")
    print()

    all_shards = _load_manifest()
    # Pick a mix: 3 from 2026-01-13 (large bulk-update; ~915 MB each),
    # 1 small recent (~MB scale), 1 small pre-2020.
    chosen = [
        s for s in all_shards
        if "2026-01-13" in s and "part_0001.gz" in s
    ][:1] + [
        s for s in all_shards
        if "2026-01-13" in s and "part_0002.gz" in s
    ][:1] + [
        s for s in all_shards
        if "2026-01-13" in s and "part_0003.gz" in s
    ][:1] + [
        s for s in all_shards
        if "2024-08-15" in s
    ][:1] + [
        s for s in all_shards
        if "2018-06" in s
    ][:1]
    chosen = chosen[:5]
    print(f"Dispatching {len(chosen)} shards via .map()...")
    for s in chosen:
        print(f"  {s}")
    print()

    t_start = time.time()
    results: list[dict[str, Any]] = []
    errors: list[Any] = []
    for r in parse_one_shard.map(chosen, return_exceptions=True):
        if isinstance(r, Exception):
            errors.append(r)
            print(f"  ✗ exception: {r}")
        else:
            results.append(r)
            print(f"  ✓ {r['shard_url']}: "
                  f"{r['n_in']:,} in → {r['n_out']:,} out "
                  f"({r['yield_pct']:.1f}% yield, {r['elapsed_sec']:.1f}s)")

    elapsed = time.time() - t_start
    print()
    print(f"5-shard smoke complete: {elapsed:.0f}s wall-clock")
    print(f"  successes: {len(results)}/{len(chosen)}")
    print(f"  errors:    {len(errors)}")
    if results:
        total_in = sum(r["n_in"] for r in results)
        total_out = sum(r["n_out"] for r in results)
        avg_yield = total_out / total_in * 100.0 if total_in else 0.0
        print(f"  total in:  {total_in:,}")
        print(f"  total out: {total_out:,}")
        print(f"  avg yield: {avg_yield:.2f}%")


# ---------- Full pull (Step 7) ----------


@app.local_entrypoint()
def main() -> None:
    """Phase 1.2 Step 7 — full 2,127-shard parse + dedup + download.

    Wall-clock: ~30-60 min (100-way map() parallelism).
    Cost: ~$50-80.
    """
    print("Phase 1.2 Step 7 — full bulk-dump parse")
    print()

    snapshot = datetime.now(timezone.utc).isoformat(timespec="seconds")
    all_shards = _load_manifest()
    print(f"Loaded {len(all_shards)} shards from manifest")

    # Resumability check: list Volume for already-done shards
    print("Checking Volume for already-done shards...")
    try:
        done_filenames = _list_done_shards()
    except Exception as err:
        print(f"  WARN: Volume listing failed ({err}); treating all as fresh")
        done_filenames = set()
    print(f"  {len(done_filenames)} shards already done on Volume")

    remaining = _filter_remaining(all_shards, done_filenames)
    print(f"  {len(remaining)} shards remaining to process")
    print()

    if not remaining:
        print("All shards already processed; skipping to dedup.")
    else:
        # Dispatch via .map()
        print(f"Dispatching {len(remaining)} shards via .map() "
              f"(default ~100-way parallelism)...")
        t_start = time.time()
        results: list[dict[str, Any]] = []
        errors: list[tuple[str, str]] = []  # (shard_url, error message)

        # Wrap map() iteration with progress reporting every N shards
        progress_every = max(50, len(remaining) // 50)
        for i, r in enumerate(
            parse_one_shard.map(remaining, return_exceptions=True), start=1,
        ):
            if isinstance(r, Exception):
                errors.append((remaining[i - 1] if i - 1 < len(remaining) else "?",
                               str(r)))
            else:
                results.append(r)
            if i % progress_every == 0 or i == len(remaining):
                elapsed = time.time() - t_start
                rate = i / elapsed if elapsed > 0 else 0.0
                eta_sec = (len(remaining) - i) / rate if rate > 0 else 0.0
                print(f"  [{i:>5}/{len(remaining)}] "
                      f"results={len(results)}, errors={len(errors)}, "
                      f"elapsed={elapsed:.0f}s, "
                      f"rate={rate:.1f}/s, "
                      f"eta={eta_sec:.0f}s")

        parse_elapsed = time.time() - t_start
        print()
        print(f"Parse complete: {parse_elapsed:.0f}s "
              f"({parse_elapsed/60:.1f} min)")
        print(f"  successes: {len(results)}")
        print(f"  errors:    {len(errors)}")

        if errors:
            print("First 10 errors:")
            for url, err in errors[:10]:
                print(f"  {url}: {err}")

        # Yield stats
        if results:
            total_in = sum(r["n_in"] for r in results)
            total_out = sum(r["n_out"] for r in results)
            avg_yield = total_out / total_in * 100.0 if total_in else 0.0
            print(f"  total raw records:      {total_in:,}")
            print(f"  total post-§0:          {total_out:,}")
            print(f"  avg yield:              {avg_yield:.2f}%")

    # ---------- Step 7 follow-on: dedup ----------

    print()
    print("Step 7 follow-on: cross-shard dedup (paper-id; max updated_date)")
    t_start = time.time()
    dedup_result = dedup_to_population.remote()
    dedup_elapsed = time.time() - t_start
    print(f"  dedup complete: {dedup_elapsed:.0f}s")
    print(f"  shards concatenated: {dedup_result.get('n_shards_concat', 'N/A')}")
    print(f"  unique paper-ids: {dedup_result.get('n_records', 'N/A'):,}")
    print(f"  output (Volume):  {dedup_result.get('output', 'N/A')}")

    # ---------- Persist metadata ----------
    #
    # The §0 population parquet stays on the Modal Volume. At
    # ~70-100 GB it's too large to download locally for marginal
    # gain — sampling (Step 8) runs server-side via
    # ``sample_population.remote()``, and only the ~1 GB sample
    # gets downloaded to local.

    _DATA_METADATA_DIR.mkdir(parents=True, exist_ok=True)
    metadata = {
        "snapshot": snapshot,
        "manifest_path": str(_MANIFEST_PATH.relative_to(
            _MANIFEST_PATH.parent.parent.parent,
        )),
        "n_shards_total": len(all_shards),
        "n_shards_done_at_start": len(done_filenames),
        "n_shards_dispatched": len(remaining) if remaining else 0,
        "dedup_result": dedup_result,
        "population_parquet_volume": (
            "modal://ws2-section0/section0-population.parquet"
        ),
        "next_step": (
            "Run experiments/phase-1.2/sample.py to sample server-side "
            "and download the sample (~1 GB)."
        ),
    }
    _RESULTS_LOG.write_text(json.dumps(metadata, indent=2, default=str))
    print(f"  wrote {_RESULTS_LOG}")
    print()
    print("Phase 1.2 Step 7 complete.")
    print("Population stays on Modal Volume; run sample.py for the sample.")
