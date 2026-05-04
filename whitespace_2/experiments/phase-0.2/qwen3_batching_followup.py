"""Phase 0.2 Wave 1A follow-up — bs sweep ∈ {1, 2, 4} for Qwen3.

Wave 1A primary surfaced that sentence-transformers does length-sorted
batching internally (the original "sorted-batching mitigation" hypothesis
was wrong). This follow-up resolves the remaining open question:
*is bs=1 genuinely faster than bs=8 on warm Qwen3?*

Phase 0.1.E estimated warm bs=1 ≈ 1.1 s/abs by subtracting load time
from the cold pass-1 measurement. That estimate was never directly
measured. This script measures it.

Three configs added to the Wave 1A artifact:
1. bs=1 (warm)
2. bs=2 (warm)
3. bs=4 (warm)

bs=8 already measured in the primary Wave 1A run (5.748 s/abs).

If bs=1 is ≥30% faster than bs=8 on warm runs, the Qwen3 production
config switches to bs=1 and the Stage 2 compute prior tightens
proportionally. If not, bs=8 stays as the baseline and the Phase 0.1.E
"4× slowdown" claim was an artifact of the cold/warm comparison.

Run:
    uv run python experiments/phase-0.2/qwen3_batching_followup.py
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch

from whitespace2 import embeddings as emb

_OUT_DIR = Path(__file__).parent
_PILOT_PARQUET = _OUT_DIR.parent.parent / "data" / "metadata" / "pilot-query-results.parquet"

_DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
_DTYPE = "fp16"
_N_ABSTRACTS = 50
_SEED = 42


def _reconstruct_abstract(inverted_index: dict[str, list[int]]) -> str:
    if not inverted_index:
        return ""
    max_pos = max(max(positions) for positions in inverted_index.values())
    tokens = [""] * (max_pos + 1)
    for word, positions in inverted_index.items():
        for pos in positions:
            tokens[pos] = word
    return " ".join(t for t in tokens if t)


def _load_test_abstracts() -> list[str]:
    df = pd.read_parquet(_PILOT_PARQUET)
    rows: list[str] = []
    for (_field, _year), grp in df.groupby(["field", "cell_year"]):
        sub = grp[grp["has_abstract"]].copy()
        if len(sub) < 5:
            continue
        sample = sub.sample(min(5, len(sub)), random_state=_SEED)
        for _, r in sample.iterrows():
            inv = json.loads(str(r["abstract_inverted_index_json"]))
            text = _reconstruct_abstract(inv)
            if text and len(text) > 50:
                rows.append(text)
    return rows[:_N_ABSTRACTS]


def _benchmark_bs(abstracts: list[str], batch_size: int) -> dict[str, Any]:
    t0 = time.time()
    vectors = emb.embed_qwen3(
        abstracts,
        device=_DEVICE,
        batch_size=batch_size,
        dtype=_DTYPE,
        length_sort=False,  # sentence-transformers does it internally
    )
    elapsed = time.time() - t0
    norms = np.linalg.norm(vectors, axis=1)
    return {
        "config": f"bs={batch_size}",
        "batch_size": batch_size,
        "length_sort": False,
        "n_abstracts": len(abstracts),
        "elapsed_sec": elapsed,
        "sec_per_abstract": elapsed / max(1, len(abstracts)),
        "shape": str(vectors.shape),
        "finite": bool(np.isfinite(vectors).all()),
        "norm_mean": float(norms.mean()),
        "norm_std": float(norms.std()),
    }


def main() -> None:
    print("Phase 0.2 Wave 1A follow-up — bs ∈ {1, 2, 4} on warm Qwen3")
    print(f"  device: {_DEVICE}; dtype: {_DTYPE}")
    print()

    abstracts = _load_test_abstracts()
    print(f"Loaded {len(abstracts)} abstracts")
    print()

    # Warm-up
    print("Warming up Qwen3 (1-abstract call)...")
    _ = emb.embed_qwen3(
        abstracts[:1], device=_DEVICE, batch_size=1, dtype=_DTYPE, length_sort=False,
    )
    print("  warm-up done.")
    print()

    results: list[dict[str, Any]] = []
    for bs in [1, 2, 4]:
        print(f"Benchmarking bs={bs}...")
        r = _benchmark_bs(abstracts, batch_size=bs)
        print(f"  bs={bs}: {r['elapsed_sec']:.1f}s "
              f"({r['sec_per_abstract']:.3f} s/abs); norm={r['norm_mean']:.3f}")
        results.append(r)

    # Append to existing CSV
    csv_path = _OUT_DIR / "qwen3-batching-benchmark.csv"
    existing = pd.read_csv(csv_path) if csv_path.exists() else pd.DataFrame()
    new_rows = pd.DataFrame(results)
    combined = pd.concat([existing, new_rows], ignore_index=True)
    combined.to_csv(csv_path, index=False)
    print(f"\nappended to {csv_path}")

    # Print summary including bs=8 from primary run for comparison
    bs8_spa = 5.748  # Phase 0.2 Wave 1A primary
    print("\nSummary (incl. Wave 1A primary bs=8):")
    print(f"  bs=8 (primary): {bs8_spa:.3f} s/abs")
    for r in results:
        ratio = bs8_spa / r["sec_per_abstract"]
        if ratio > 1.05:
            verdict = "FASTER than bs=8"
        elif ratio > 0.95:
            verdict = "comparable"
        else:
            verdict = "SLOWER than bs=8"
        print(f"  bs={r['batch_size']}: {r['sec_per_abstract']:.3f} s/abs "
              f"({ratio:.2f}× of bs=8; {verdict})")

    # Find optimal
    all_configs = [{"batch_size": 8, "sec_per_abstract": bs8_spa}] + results
    best = min(all_configs, key=lambda r: r["sec_per_abstract"])
    print(f"\nOptimal: bs={best['batch_size']} at {best['sec_per_abstract']:.3f} s/abs")

    # Save snapshot for the artifact append step
    snapshot = datetime.now(timezone.utc).isoformat(timespec="seconds")
    summary_json = _OUT_DIR / "qwen3-batching-followup-summary.json"
    summary_json.write_text(json.dumps({
        "snapshot": snapshot,
        "bs8_primary": bs8_spa,
        "results": results,
        "optimal_bs": best["batch_size"],
        "optimal_spa": best["sec_per_abstract"],
    }, indent=2))
    print(f"\nwrote {summary_json} (for artifact append)")
    print("\nFollow-up complete.")


if __name__ == "__main__":
    main()
    sys.exit(0)
