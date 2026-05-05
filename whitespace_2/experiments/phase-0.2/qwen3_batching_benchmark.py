"""Phase 0.2 Wave 1A — Qwen3 sorted-by-length batching benchmark.

Phase 0.1.E surfaced that naive bs=8 batching is ~4× slower per-abstract
than bs=1 for Qwen3-Embedding-0.6B due to padding waste against the
model's 32K-token context window. SPECTER2/SciNCL truncate at 512 (BERT
max), bounding the padding range; Qwen3's much larger context window
leaves padding range unbounded by default, so a long-tail abstract joining
a bs=8 batch with shorter ones inflates compute by 3-4×.

This benchmark validates the sorted-batching mitigation: pre-sort
abstracts by length so each batch contains similar-length items,
minimizing padding waste. The fix lives in `embed_qwen3(length_sort=True)`
(default in the production pipeline as of this commit).

Three configs benchmarked on 50 stratified-by-year abstracts from the
locked Check-5a pilot parquet:
1. Naive bs=8 (length_sort=False) — Phase 0.1.E baseline (4.228 s/abs).
2. Sorted bs=8 (length_sort=True, batch_size=8) — drop-in mitigation.
3. Sorted bs=32 (length_sort=True, batch_size=32) — larger batches further
   amortize per-call overhead given uniform within-batch lengths.

Output: `experiments/phase-0.2/qwen3-batching-benchmark.{md,csv}`.

Run:
    uv run python experiments/phase-0.2/qwen3_batching_benchmark.py
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
    """OpenAlex stores abstracts as {word: [positions]}; reconstruct."""
    if not inverted_index:
        return ""
    max_pos = max(max(positions) for positions in inverted_index.values())
    tokens = [""] * (max_pos + 1)
    for word, positions in inverted_index.items():
        for pos in positions:
            tokens[pos] = word
    return " ".join(t for t in tokens if t)


def _load_test_abstracts() -> list[str]:
    """50 abstracts stratified across the pilot's 10 cells (5 per cell)."""
    df = pd.read_parquet(_PILOT_PARQUET)
    rows: list[str] = []
    for (field, year), grp in df.groupby(["field", "cell_year"]):
        sub = grp[grp["has_abstract"]].copy()
        if len(sub) < 5:
            continue
        sample = sub.sample(min(5, len(sub)), random_state=_SEED)
        for _, r in sample.iterrows():
            inv = json.loads(r["abstract_inverted_index_json"])
            text = _reconstruct_abstract(inv)
            if text and len(text) > 50:
                rows.append(text)
    return rows[:_N_ABSTRACTS]


def _benchmark_config(
    abstracts: list[str],
    batch_size: int,
    length_sort: bool,
) -> dict[str, Any]:
    """Time one config; returns timing + shape + L2-norm stats."""
    t0 = time.time()
    vectors = emb.embed_qwen3(
        abstracts,
        device=_DEVICE,
        batch_size=batch_size,
        dtype=_DTYPE,
        length_sort=length_sort,
    )
    elapsed = time.time() - t0
    norms = np.linalg.norm(vectors, axis=1)
    return {
        "config": f"{'sorted' if length_sort else 'naive'} bs={batch_size}",
        "batch_size": batch_size,
        "length_sort": length_sort,
        "n_abstracts": len(abstracts),
        "elapsed_sec": elapsed,
        "sec_per_abstract": elapsed / max(1, len(abstracts)),
        "shape": str(vectors.shape),
        "finite": bool(np.isfinite(vectors).all()),
        "norm_mean": float(norms.mean()),
        "norm_std": float(norms.std()),
    }


def _project_at_n(s_per_abs: float, n: int) -> float:
    """Hours at production scale n."""
    return s_per_abs * n / 3600.0


def main() -> None:
    print("Phase 0.2 Wave 1A — Qwen3 sorted-batching benchmark")
    print(f"  device: {_DEVICE}; dtype: {_DTYPE}")
    print()

    print("Loading 50 abstracts from pilot parquet...")
    abstracts = _load_test_abstracts()
    char_lens = [len(a) for a in abstracts]
    print(f"  loaded {len(abstracts)} abstracts; char-length stats: "
          f"min={min(char_lens)}, p50={int(np.percentile(char_lens, 50))}, "
          f"p95={int(np.percentile(char_lens, 95))}, max={max(char_lens)}")
    print()

    # Warm-up call (1 abstract) to force model load before timing
    print("Warming up Qwen3 (1-abstract call to force model load)...")
    _ = emb.embed_qwen3(abstracts[:1], device=_DEVICE, batch_size=1, dtype=_DTYPE)
    print("  warm-up done.")
    print()

    snapshot = datetime.now(timezone.utc).isoformat(timespec="seconds")

    configs = [
        (8, False),   # naive baseline (Phase 0.1.E)
        (8, True),    # sorted bs=8 (drop-in mitigation)
        (32, True),   # sorted bs=32 (larger batches with uniform lengths)
    ]
    results: list[dict[str, Any]] = []
    for bs, sort in configs:
        label = f"{'sorted' if sort else 'naive'} bs={bs}"
        print(f"Benchmarking {label}...")
        result = _benchmark_config(abstracts, batch_size=bs, length_sort=sort)
        print(f"  {label}: {result['elapsed_sec']:.1f}s "
              f"({result['sec_per_abstract']:.3f} s/abs); "
              f"shape={result['shape']}, finite={result['finite']}, "
              f"norm={result['norm_mean']:.3f}±{result['norm_std']:.3f}")
        results.append(result)

    # Save CSV
    csv_path = _OUT_DIR / "qwen3-batching-benchmark.csv"
    pd.DataFrame(results).to_csv(csv_path, index=False)
    print(f"\nwrote {csv_path}")

    # Compute speedup vs baseline (naive bs=8)
    baseline_spa = next(
        r["sec_per_abstract"] for r in results
        if not r["length_sort"] and r["batch_size"] == 8
    )
    for r in results:
        r["speedup_vs_naive_bs8"] = baseline_spa / r["sec_per_abstract"]

    # Markdown artifact
    table_rows = "\n".join(
        f"| {r['config']} | {r['n_abstracts']} | {r['elapsed_sec']:.1f} | "
        f"{r['sec_per_abstract']:.3f} | {r['speedup_vs_naive_bs8']:.2f}× | "
        f"{_project_at_n(r['sec_per_abstract'], 500_000):.1f} | "
        f"{_project_at_n(r['sec_per_abstract'], 2_000_000):.1f} |"
        for r in results
    )

    best_config = min(results, key=lambda r: r["sec_per_abstract"])
    best_speedup = baseline_spa / best_config["sec_per_abstract"]
    best_spa = float(best_config["sec_per_abstract"])
    best_500k = _project_at_n(best_spa, 500_000)
    best_2m = _project_at_n(best_spa, 2_000_000)
    base_500k = _project_at_n(baseline_spa, 500_000)
    base_2m = _project_at_n(baseline_spa, 2_000_000)
    naive_spa = next(r["sec_per_abstract"] for r in results if not r["length_sort"])
    local_status = (
        "Tolerable on local M-series" if best_500k < 100 else "Still slow locally"
    )

    body = f"""# Phase 0.2 Wave 1A — Qwen3 sorted-batching benchmark

**Run date:** {datetime.now(timezone.utc).date().isoformat()}
**Snapshot recorded:** {snapshot}
**Device:** {_DEVICE}; **dtype:** {_DTYPE}
**Inputs:** {len(abstracts)} abstracts stratified across the 10 (year × field)
cells of `data/metadata/pilot-query-results.parquet` (5 per cell, seed={_SEED}).
Char-length: min={min(char_lens)}, p50={int(np.percentile(char_lens, 50))},
p95={int(np.percentile(char_lens, 95))}, max={max(char_lens)}.

## Background

Phase 0.1.E surfaced that naive bs=8 batching for Qwen3-Embedding-0.6B
runs at 4.228 s/abs vs bs=1 at ~1.1 s/abs warm — a 4× slowdown. The
mechanism: Qwen3 is a decoder-LM with 32K-token context; sentence-
transformers pads to the longest sequence in each batch; a typical
abstract distribution (mean ~250 tokens, long-tail ≥500) means a bs=8
batch processes ~8 × max ≈ 4000 tokens of compute, vs bs=1 sequentially
processing the actual lengths (sum ≈ 1500 tokens).

The sorted-batching mitigation pre-sorts abstracts by length so each
batch contains similar-length items, minimizing padding waste.
Implementation in `src/whitespace2/embeddings.py::embed_qwen3` with
`length_sort=True` (default).

## Results — three configs

| Config | N | Total (s) | s/abstract | Speedup vs naive bs=8 | 500K hrs | 2M hrs |
|---|---:|---:|---:|---:|---:|---:|
{table_rows}

## Headline

**Best config: `{best_config['config']}` at {best_spa:.3f} s/abs
({best_speedup:.2f}× faster than naive bs=8).**

At Stage 2 N=500K, this projects to ~{best_500k:.0f} hrs of Qwen3
compute (vs ~{base_500k:.0f} hrs naive bs=8).
At N=2M, ~{best_2m:.0f} hrs (vs ~{base_2m:.0f} hrs naive).

## Acceptance check (Wave 1A)

Per `phase-0.2-execution.md` Wave 1A acceptance: best-strategy wall-clock
recorded; sorted-batching merged into `embed_qwen3` default behavior.

Status: ✅ recorded; default switched to `length_sort=True` (set
`length_sort=False` to disable for benchmarking parity with Phase 0.1.E).

## Decision input for Wave 4A (Stage 2 compute target)

| Strategy | s/abs | 500K hrs | 2M hrs | Note |
|---|---:|---:|---:|---|
| Naive bs=8 | {naive_spa:.3f} | {base_500k:.0f} | {base_2m:.0f} | Phase 0.1.E baseline |
| Best sorted | {best_spa:.3f} | {best_500k:.0f} | {best_2m:.0f} | {local_status} |
| A10G (~7×) | ~{best_spa/7:.3f} | ~{best_500k/7:.0f} | ~{best_2m/7:.0f} | $15-50/pass |
| A100 (~40×) | ~{best_spa/40:.3f} | ~{best_500k/40:.0f} | ~{best_2m/40:.0f} | $50-200/pass |

The sorted-batching gain reduces but does not eliminate the cloud-vs-
local tradeoff. Locked Stage 2 compute decision happens in Wave 4A,
gated by this number plus the §11 production-scale embedding timing
(Wave 2A) plus the chosen production-N target.

## Artifacts

- `experiments/phase-0.2/qwen3-batching-benchmark.csv` — per-config timings.
- `experiments/phase-0.2/qwen3_batching_benchmark.py` — this script.
- `src/whitespace2/embeddings.py::embed_qwen3` — `length_sort` parameter
  (default True from this commit forward).
"""
    md_path = _OUT_DIR / "qwen3-batching-benchmark.md"
    md_path.write_text(body)
    print(f"wrote {md_path}")
    print()
    print(
        f"Wave 1A complete. Best: {best_config['config']} = "
        f"{best_spa:.3f} s/abs ({best_speedup:.2f}× speedup)."
    )


if __name__ == "__main__":
    main()
    sys.exit(0)
