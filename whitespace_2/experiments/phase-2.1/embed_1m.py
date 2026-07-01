"""Phase 2.1 WS4 — base 1M v3 embed (SciNCL + Qwen3) on Modal via ``.map()``.

Loads the 1M v3 sample (local scratchpad), filters to the 1970-2024 study
window, reconstructs abstracts, and embeds with **SciNCL** (primary) +
**Qwen3** (cross-family) on Modal A100 preemptible.

The long-pole Qwen3 bs=1 embed (~10 hrs sequential at 1M) is parallelized by
fanning chunks across Modal containers via ``fn.map`` through the resumable
``ChunkedEmbedRunner.run_mapped``. Modal reuses warm containers across map
inputs, so each model loads once per container then streams many chunks; a
preemption re-dispatches only the missing chunks (bounded rework). Cost is
invariant to parallelism — the same abstract-seconds of A100 time either way;
``.map()`` only compresses wall-clock.

§9 pre-commit: ~$19 (SciNCL ~$2 + Qwen3 ~$17), written in ``tasks/spend.md``
(2026-06-30 row). Model driver pattern: ``experiments/phase-1.4/smoke_100k.py``.

Usage:
  uv run python experiments/phase-2.1/embed_1m.py \
      --source <scratchpad>/section0-sample-1M-v3.parquet \
      --outdir <scratchpad>/embed-1m \
      --model both              # or scincl / qwen3
      [--n 3000]                # subset for a smoke of the map path
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

import modal
import numpy as np
import pyarrow.parquet as pq

from whitespace2.demographics import extract_primary_field
from whitespace2.resumable_runner import ChunkedEmbedRunner

_CHUNK_SIZE = 1000
_YEAR_MIN, _YEAR_MAX = 1970, 2024

# Per-abstract A100 preempt rates (Phase 1.1 Step 5, 50K dry-run) + $1.70/hr.
_A100_USD_PER_SEC = 1.70 / 3600
_MODELS: dict[str, dict[str, Any]] = {
    "scincl": {
        "fn": "embed_chunk_scincl",
        "norm_band": (22.5, 24.5),   # Wave 4A revalidation
        "s_per_abs": 0.0047,
    },
    "qwen3": {
        "fn": "embed_chunk_qwen3",
        "norm_band": (0.99, 1.01),   # last-token EOS pooling + L2 normalize
        "s_per_abs": 0.036,
    },
}


def _reconstruct(inv: dict[str, list[int]]) -> str:
    """Invert an abstract_inverted_index → text (matches smoke_100k)."""
    if not inv:
        return ""
    max_pos = max(max(p) for p in inv.values())
    tokens = [""] * (max_pos + 1)
    for word, ps in inv.items():
        for p in ps:
            tokens[p] = word
    return " ".join(t for t in tokens if t)


def _load_abstracts(source: Path, n: int | None) -> Any:
    """Return the in-window frame (id, year, field, cited_by_count) + abstracts."""
    print(f"loading {source} …", flush=True)
    df = pq.read_table(
        str(source),
        columns=["id", "publication_year", "abstract_inverted_index_json",
                 "concepts_json", "cited_by_count"],
    ).to_pandas()
    df = df[(df["publication_year"] >= _YEAR_MIN)
            & (df["publication_year"] <= _YEAR_MAX)]
    if n is not None:
        df = df.head(n)
    df = df.reset_index(drop=True)
    df["field"] = df["concepts_json"].map(extract_primary_field)
    print(f"  {len(df):,} in-window papers "
          f"(cs={int((df.field == 'cs').sum()):,} "
          f"physics={int((df.field == 'physics').sum()):,})", flush=True)

    abstracts = [_reconstruct(json.loads(str(x)))
                 for x in df["abstract_inverted_index_json"]]
    n_empty = sum(1 for a in abstracts if not a.strip())
    print(f"  reconstructed {len(abstracts):,} abstracts ({n_empty} empty)",
          flush=True)
    return df, abstracts


def _embed_one(
    model: str, abstracts: list[str], outdir: Path,
) -> dict[str, Any]:
    """Embed all abstracts with one model via Modal .map(); validate + persist."""
    spec = _MODELS[model]
    fn = modal.Function.from_name("ws2-embed", str(spec["fn"]))
    runner = ChunkedEmbedRunner(
        model_fn=fn.remote,  # only used by the sequential run(); run_mapped uses map_fn
        chunk_size=_CHUNK_SIZE,
        output_dir=outdir / f"{model}-vectors",
    )

    def map_fn(chunks: list[list[str]]) -> Any:
        # Modal .map is order-preserving (default order_outputs=True): result i
        # ↔ input chunk i, exactly the contract run_mapped requires.
        return fn.map(chunks)

    print(f"[{model}] embedding {len(abstracts):,} abstracts "
          f"(A100, chunks of {_CHUNK_SIZE}, Modal .map fan-out) …", flush=True)
    t0 = time.time()
    vecs = runner.run_mapped(abstracts, map_fn=map_fn)
    elapsed = time.time() - t0

    norms = np.linalg.norm(vecs, axis=1)
    lo, hi = spec["norm_band"]
    mean_norm = float(norms.mean())
    summary: dict[str, Any] = {
        "model": model,
        "n": int(vecs.shape[0]),
        "dim": int(vecs.shape[1]),
        "wall_clock_sec": round(elapsed, 1),
        "all_finite": bool(np.isfinite(vecs).all()),
        "norm_mean": round(mean_norm, 4),
        "norm_min": round(float(norms.min()), 4),
        "norm_max": round(float(norms.max()), 4),
        "norm_in_band": bool(lo <= mean_norm <= hi),
        "norm_band": [lo, hi],
        # Cost from GPU-seconds (parallelism-invariant), not wall-clock.
        "est_cost_usd": round(
            len(abstracts) * float(spec["s_per_abs"]) * _A100_USD_PER_SEC, 4,
        ),
    }
    np.save(outdir / f"{model}-vectors.npy", vecs.astype(np.float32))
    (outdir / f"{model}-embed-summary.json").write_text(
        json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2), flush=True)
    if not summary["norm_in_band"]:
        print(f"  WARN [{model}]: mean norm {mean_norm:.4f} OUT of band "
              f"[{lo}, {hi}] — investigate before trusting downstream metrics.",
              flush=True)
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, type=Path)
    ap.add_argument("--outdir", required=True, type=Path)
    ap.add_argument("--model", choices=["scincl", "qwen3", "both"],
                    default="both")
    ap.add_argument("--n", type=int, default=None,
                    help="subset size (smoke the .map path); default all 1M")
    args = ap.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    df, abstracts = _load_abstracts(args.source, args.n)

    # Row-aligned metadata (written once; vectors keep input order).
    df[["id", "publication_year", "field", "cited_by_count"]].rename(
        columns={"id": "paper_id", "publication_year": "year"},
    ).to_parquet(args.outdir / "metadata.parquet")

    models = ["scincl", "qwen3"] if args.model == "both" else [args.model]
    summaries = [_embed_one(m, abstracts, args.outdir) for m in models]

    (args.outdir / "embed-1m-summary.json").write_text(
        json.dumps({"n_papers": len(df), "models": summaries}, indent=2))
    total_cost = sum(s["est_cost_usd"] for s in summaries)
    print(f"\nDONE — {len(df):,} papers, {len(models)} model(s); "
          f"est ${total_cost:.2f}. Vectors + metadata in {args.outdir}",
          flush=True)


if __name__ == "__main__":
    main()
