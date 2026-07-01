"""Phase 1.1 Step 3 — Modal A100 embedding functions.

Defines two Modal functions for the Stage 2 production embed
pipeline: SciNCL (primary) + Qwen3 (cross-family). Both run on
A100 GPU; both are preemptible-by-default per Modal's GPU pricing
(no explicit flag needed). Each function is retried up to 3 times
on preemption with exponential backoff.

Per Wave 4A lock (`experiments/phase-0.2/stage2-compute-decision.md`):
- Modal A100 preemptible (default)
- SciNCL primary; Qwen3 cross-family (drop SPECTER2 from headline)
- Production embed at N=1M for headline; N=500K for robustness

Per Wave 1A measurement:
- Qwen3 must use batch_size=1 (decoder-LM KV-cache pressure;
  bs=1 is 2.94× faster than bs=8 on M-series MPS; expected to
  hold on A100 too — verify in Phase 1.1 dry-run)

Per Wave 4A SciNCL revalidation:
- Norm band [22.5, 24.5] (mean ~23.59 measured)

Modal volumes:
- ``ws2-hf-cache`` — HuggingFace model cache (persists across
  invocations; ~1.8 GB SciNCL + Qwen3 weights, downloaded once)
- ``ws2-chunks`` — chunk-level outputs for any Modal-side
  resumability (Phase 1.1 driver writes chunks via the local
  ChunkedEmbedRunner; this volume reserved for if/when we move
  the runner inside Modal)

Usage:

  # Deploy (one-time per code change):
  modal deploy experiments/phase-1.1/embed_modal.py

  # Smoke test (Phase 1.1 Step 4):
  modal run experiments/phase-1.1/embed_modal.py::smoke

See ``docs/phases/phase-1.1-plan.md`` for context.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import modal
import numpy as np

# ---------- App + image ----------

app = modal.App("ws2-embed")

# Image: debian-slim + embed deps + the local whitespace2 package.
# torch==2.2.2 to match Phase 0.1.E lock; pip will pick the CUDA wheel
# on linux automatically.
embed_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch==2.2.2",
        "transformers>=4.51,<5",
        "sentence-transformers>=2.7,<4",
        "adapters>=0.2,<2",
        "safetensors>=0.4",
        "huggingface_hub>=0.20",
        "numpy>=1.24,<2",
    )
    .env({"HF_HOME": "/cache"})
    # add_local_* must come LAST so local-file changes don't
    # trigger image rebuilds (Modal copies them at container
    # startup instead).
    .add_local_python_source("whitespace2")
)

# ---------- Volumes ----------

hf_cache = modal.Volume.from_name("ws2-hf-cache", create_if_missing=True)
chunk_volume = modal.Volume.from_name("ws2-chunks", create_if_missing=True)


# ---------- Embedding functions ----------


@app.function(
    image=embed_image,
    gpu="A100",
    volumes={"/cache": hf_cache, "/chunks": chunk_volume},
    timeout=3600,  # 1 hour per chunk — generous; typical chunk <1 min on A100
    retries=modal.Retries(
        max_retries=3, initial_delay=10.0, max_delay=60.0,
    ),
)
def embed_chunk_scincl(abstracts: list[str]) -> np.ndarray[Any, Any]:
    """Embed a chunk of abstracts via SciNCL on A100.

    Returns ``(N, 768)`` float32 array. Mean L2 norm expected
    [22.5, 24.5] per Wave 4A revalidation.

    Modal preemptible-by-default; up to 3 retries on preemption.
    """
    from whitespace2 import embeddings as emb

    return emb.embed_scincl(
        abstracts, device="cuda", batch_size=32, dtype="fp16",
    )


@app.function(
    image=embed_image,
    gpu="A100",
    volumes={"/cache": hf_cache, "/chunks": chunk_volume},
    timeout=3600,
    retries=modal.Retries(
        max_retries=3, initial_delay=10.0, max_delay=60.0,
    ),
)
def embed_chunk_qwen3(abstracts: list[str]) -> np.ndarray[Any, Any]:
    """Embed a chunk of abstracts via Qwen3-Embedding-0.6B on A100.

    Uses ``batch_size=1`` per Wave 1A measurement (bs=1 is 2.94×
    faster than bs=8 on M-series MPS due to decoder-LM KV-cache
    pressure; expected to hold on A100 — verify in Phase 1.1 dry-run).

    Returns ``(N, 768)`` float32 array (Matryoshka-truncated from
    1024). Mean L2 norm expected ≈ 1.0 (last-token EOS pooling
    + normalize).

    Modal preemptible-by-default; up to 3 retries on preemption.
    """
    from whitespace2 import embeddings as emb

    return emb.embed_qwen3(
        abstracts, device="cuda", batch_size=1, dtype="fp16", dim=768,
    )


@app.function(
    image=embed_image,
    gpu="A100",
    volumes={"/cache": hf_cache, "/chunks": chunk_volume},
    timeout=3600,
    retries=modal.Retries(
        max_retries=3, initial_delay=10.0, max_delay=60.0,
    ),
)
def embed_chunk_specter2(abstracts: list[str]) -> np.ndarray[Any, Any]:
    """Embed a chunk of abstracts via SPECTER2 (base + proximity adapter) on A100.

    Added Phase 2.3 as the retained **third embedding family** (the pre-committed
    Stage-3 robustness swap; `docs/phases/phase-0.2-scincl-primary-contingency.md`)
    to adjudicate the subfield test's embedding-sensitive Physics wrinkle. SPECTER2
    is domain-trained on scientific text. Returns ``(N, 768)`` float32 (CLS
    pooling); norms are not unit-normalized (the pairwise-cosine metric
    normalizes internally, so the raw norm is informational only).

    Modal preemptible-by-default; up to 3 retries on preemption.
    """
    from whitespace2 import embeddings as emb

    return emb.embed_specter2(
        abstracts, device="cuda", batch_size=32, dtype="fp16",
    )


# ---------- Phase 1.1 Step 4: smoke test (local entrypoint) ----------

# Wave 4A SciNCL norm band (revalidation measurement); Qwen3 last-token
# EOS pooling + L2 normalize → unit norm.
_SCINCL_NORM_MIN = 22.5
_SCINCL_NORM_MAX = 24.5
_QWEN3_NORM_TOL = 0.01

_PILOT_PARQUET_REL = "data/metadata/pilot-query-results.parquet"
_SMOKE_OUT_REL = "experiments/phase-1.1/modal-smoke-results.json"
_SMOKE_N = 100
_SMOKE_SEED = 42


def _reconstruct(inv: dict[str, list[int]]) -> str:
    if not inv:
        return ""
    max_pos = max(max(p) for p in inv.values())
    tokens = [""] * (max_pos + 1)
    for word, ps in inv.items():
        for p in ps:
            tokens[p] = word
    return " ".join(t for t in tokens if t)


def _load_smoke_abstracts(ws2_root: Path) -> list[str]:
    """100 real abstracts from cs/1990 cell of the Check 5a pilot parquet."""
    import pandas as pd

    parquet_path = ws2_root / _PILOT_PARQUET_REL
    df = pd.read_parquet(parquet_path)
    sub = df[
        (df["field"] == "cs")
        & (df["cell_year"] == 1990)
        & (df["has_abstract"])
    ].copy()
    if len(sub) < _SMOKE_N:
        sub = df[(df["field"] == "cs") & (df["has_abstract"])].copy()
    sample = sub.sample(min(_SMOKE_N, len(sub)), random_state=_SMOKE_SEED)
    abstracts: list[str] = []
    for _, r in sample.iterrows():
        inv_json = r["abstract_inverted_index_json"]
        inv = json.loads(str(inv_json))
        text = _reconstruct(inv)
        if text and len(text) > 50:
            abstracts.append(text)
    return abstracts[:_SMOKE_N]


@app.local_entrypoint()
def smoke() -> None:
    """Phase 1.1 Step 4 — Modal smoke test on 100 real abstracts.

    Runs both SciNCL + Qwen3 on Modal A100; verifies output shape,
    finite, norm bands; produces per-abstract timing for cost
    extrapolation.

    Cost: ~$5 (within §9 cap; no pre-commit gate).
    """
    print("Phase 1.1 Step 4 — Modal smoke test")
    print()

    # Resolve ws2 root from this file's location:
    # experiments/phase-1.1/embed_modal.py → ../../
    ws2_root = Path(__file__).parent.parent.parent
    abstracts = _load_smoke_abstracts(ws2_root)
    print(f"Loaded {len(abstracts)} smoke abstracts from cs/1990 pilot")
    print()

    # SciNCL on Modal
    print("Calling embed_chunk_scincl.remote() — first call may include image build")
    t0 = time.time()
    scincl_vecs: np.ndarray[Any, Any] = embed_chunk_scincl.remote(abstracts)
    scincl_elapsed = time.time() - t0
    scincl_norms = np.linalg.norm(scincl_vecs, axis=1)
    scincl_finite = bool(np.isfinite(scincl_vecs).all())
    scincl_mean_norm = float(scincl_norms.mean())
    print(f"  SciNCL: shape={scincl_vecs.shape}, finite={scincl_finite}, "
          f"mean_norm={scincl_mean_norm:.3f}, elapsed={scincl_elapsed:.1f}s")
    scincl_norm_ok = _SCINCL_NORM_MIN <= scincl_mean_norm <= _SCINCL_NORM_MAX
    band_str = f"[{_SCINCL_NORM_MIN}, {_SCINCL_NORM_MAX}]"
    if scincl_norm_ok:
        print(f"  PASS: SciNCL norm in band {band_str}")
    else:
        print(f"  FAIL: SciNCL norm out of band {band_str} — investigate")
    print()

    # Qwen3 on Modal
    print("Calling embed_chunk_qwen3.remote() — slower (bs=1)")
    t0 = time.time()
    qwen3_vecs: np.ndarray[Any, Any] = embed_chunk_qwen3.remote(abstracts)
    qwen3_elapsed = time.time() - t0
    qwen3_norms = np.linalg.norm(qwen3_vecs, axis=1)
    qwen3_finite = bool(np.isfinite(qwen3_vecs).all())
    qwen3_mean_norm = float(qwen3_norms.mean())
    print(f"  Qwen3: shape={qwen3_vecs.shape}, finite={qwen3_finite}, "
          f"mean_norm={qwen3_mean_norm:.3f}, elapsed={qwen3_elapsed:.1f}s")
    qwen3_norm_ok = abs(qwen3_mean_norm - 1.0) < _QWEN3_NORM_TOL
    if qwen3_norm_ok:
        print("  PASS: Qwen3 norm ~ 1.0")
    else:
        print(f"  FAIL: Qwen3 norm not ~1.0 (got {qwen3_mean_norm:.3f})")
    print()

    # Per-abstract timing extrapolation
    scincl_per_abs = scincl_elapsed / len(abstracts)
    qwen3_per_abs = qwen3_elapsed / len(abstracts)
    print("Per-abstract A100 timing (note: includes cold-start on first call):")
    print(f"  SciNCL: {scincl_per_abs:.3f} s/abs")
    print(f"  Qwen3:  {qwen3_per_abs:.3f} s/abs")
    print(f"  Combined: {scincl_per_abs + qwen3_per_abs:.3f} s/abs")
    print()

    # Cost extrapolation at $1.70/hr A100 preempt
    a100_per_sec = 1.70 / 3600
    cost_per_abs = (scincl_per_abs + qwen3_per_abs) * a100_per_sec
    cost_at_1m = cost_per_abs * 1_000_000
    h3_gate_pass = cost_per_abs <= 0.075
    print("Extrapolation (at $1.70/hr A100 preempt):")
    print(f"  Per-abstract cost: ${cost_per_abs:.4f}")
    print(f"  At 1M abstracts:   ${cost_at_1m:.0f}")
    h3_status = "PASS" if h3_gate_pass else "FAIL"
    print(f"  Wave 4A H3 gate (≤$0.075/abs): {h3_status}")
    print()

    # Save smoke artifact
    artifact_path = ws2_root / _SMOKE_OUT_REL
    artifact_path.write_text(json.dumps({
        "n_abstracts": len(abstracts),
        "scincl": {
            "shape": list(scincl_vecs.shape),
            "finite": scincl_finite,
            "mean_norm": scincl_mean_norm,
            "min_norm": float(scincl_norms.min()),
            "max_norm": float(scincl_norms.max()),
            "elapsed_sec": scincl_elapsed,
            "per_abs_sec": scincl_per_abs,
            "norm_in_band": scincl_norm_ok,
        },
        "qwen3": {
            "shape": list(qwen3_vecs.shape),
            "finite": qwen3_finite,
            "mean_norm": qwen3_mean_norm,
            "min_norm": float(qwen3_norms.min()),
            "max_norm": float(qwen3_norms.max()),
            "elapsed_sec": qwen3_elapsed,
            "per_abs_sec": qwen3_per_abs,
            "norm_in_band": qwen3_norm_ok,
        },
        "extrapolation": {
            "combined_per_abs_sec": scincl_per_abs + qwen3_per_abs,
            "cost_per_abs_at_1.70_per_hr": cost_per_abs,
            "cost_at_1m": cost_at_1m,
            "h3_gate_pass": h3_gate_pass,
        },
    }, indent=2))
    print(f"Wrote {artifact_path}")
    print()

    overall_ok = scincl_norm_ok and qwen3_norm_ok and scincl_finite and qwen3_finite
    print(f"Smoke verdict: {'PASS' if overall_ok else 'INVESTIGATE'}")
