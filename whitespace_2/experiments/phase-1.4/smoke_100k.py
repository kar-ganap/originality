"""Phase 1.4 C3 — embed a 100K v3 pilot on Modal (de-risk the Stage 2 spend).

Takes the hash-ordered first 100K in-window (1970-2024) papers of the v3
1M production sample, reconstructs abstracts, and embeds them with SciNCL
(the Stage-2 primary) on Modal A100 preemptible via the deployed `ws2-embed`
app + the resumable `ChunkedEmbedRunner`. Writes row-aligned metadata
(paper_id, year, field, cited_by_count) + the vectors for the C4 pilot
divergence test.

(Qwen3 cross-family was already validated at 16K in Phase 1.1; the full
cross-family embed runs in Stage 2. SciNCL alone drives the primary pilot.)

Usage:
  uv run python experiments/phase-1.4/smoke_100k.py \
      --source <scratchpad>/section0-sample-1M-v3.parquet --n 100000
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
_SCINCL_NORM_BAND = (22.5, 24.5)  # per embed_modal.py
_YEAR_MIN, _YEAR_MAX = 1970, 2024
_OUTDIR = Path(__file__).parent / "smoke-100k"


def _reconstruct(inv: dict[str, list[int]]) -> str:
    """Invert an abstract_inverted_index → text (matches dry_run_50k)."""
    if not inv:
        return ""
    max_pos = max(max(p) for p in inv.values())
    tokens = [""] * (max_pos + 1)
    for word, ps in inv.items():
        for p in ps:
            tokens[p] = word
    return " ".join(t for t in tokens if t)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, type=Path)
    ap.add_argument("--n", type=int, default=100_000)
    args = ap.parse_args()
    _OUTDIR.mkdir(parents=True, exist_ok=True)

    # ---- subset: first N in-window, hash-ordered (deterministic) ----
    print(f"loading {args.source} …", flush=True)
    df = pq.read_table(
        str(args.source),
        columns=["id", "publication_year", "abstract_inverted_index_json",
                 "concepts_json", "cited_by_count"],
    ).to_pandas()
    df = df[(df["publication_year"] >= _YEAR_MIN)
            & (df["publication_year"] <= _YEAR_MAX)].head(args.n).reset_index(
        drop=True)
    df["field"] = df["concepts_json"].map(extract_primary_field)
    print(f"  {len(df):,} in-window papers (cs={int((df.field=='cs').sum()):,} "
          f"physics={int((df.field=='physics').sum()):,})", flush=True)

    abstracts = [_reconstruct(json.loads(str(x)))
                 for x in df["abstract_inverted_index_json"]]
    n_empty = sum(1 for a in abstracts if not a.strip())
    print(f"  reconstructed {len(abstracts):,} abstracts "
          f"({n_empty} empty)", flush=True)

    # ---- embed SciNCL on Modal (resumable) ----
    fn = modal.Function.from_name("ws2-embed", "embed_chunk_scincl")
    runner = ChunkedEmbedRunner(
        model_fn=fn.remote, chunk_size=_CHUNK_SIZE,
        output_dir=_OUTDIR / "scincl-vectors",
    )
    print(f"embedding {len(abstracts):,} abstracts (SciNCL, A100, chunks of "
          f"{_CHUNK_SIZE}) …", flush=True)
    t0 = time.time()
    vecs = runner.run(abstracts)
    elapsed = time.time() - t0

    # ---- validate ----
    norms = np.linalg.norm(vecs, axis=1)
    summary: dict[str, Any] = {
        "n": int(vecs.shape[0]),
        "dim": int(vecs.shape[1]),
        "elapsed_sec": round(elapsed, 1),
        "per_abs_sec": round(elapsed / max(len(abstracts), 1), 6),
        "all_finite": bool(np.isfinite(vecs).all()),
        "norm_mean": round(float(norms.mean()), 4),
        "norm_in_band": bool(_SCINCL_NORM_BAND[0] <= norms.mean()
                             <= _SCINCL_NORM_BAND[1]),
        "est_cost_usd": round(len(abstracts) * 0.00475 / 3600 * 1.70, 4),
    }
    print(json.dumps(summary, indent=2), flush=True)

    # ---- persist row-aligned metadata + vectors for C4 ----
    np.save(_OUTDIR / "scincl-vectors.npy", vecs.astype(np.float32))
    df[["id", "publication_year", "field", "cited_by_count"]].rename(
        columns={"id": "paper_id", "publication_year": "year"},
    ).to_parquet(_OUTDIR / "metadata.parquet")
    (_OUTDIR / "embed-summary.json").write_text(json.dumps(summary, indent=2))
    print(f"saved vectors + metadata + summary to {_OUTDIR}", flush=True)


if __name__ == "__main__":
    main()
