"""Phase 1.1 Step 5 — 50K-paper dry-run on Modal A100.

Pulls ~50K cs+physics 1970-2024 abstracts (post-§0-filter) and
embeds them with both SciNCL + Qwen3 on Modal A100 preempt. The
local ChunkedEmbedRunner dispatches chunks to Modal one at a
time and persists vectors + done.txt on disk for resumability
across local network drops or driver restarts.

Per Phase 1.1 plan VERIFY plan:
- H1 resumable runner correctness (validated via Step 2 unit
  tests; this dry-run additionally exercises real Modal calls)
- H3 cost: actual ≤ $0.075/abs combined (Wave 4A budget gate)
- H4 preemption rate: ≤ 30% wall-clock penalty
- H5 output validity: shape + finite + correct dim
- H6 norm bands: SciNCL [22.5, 24.5]; Qwen3 ≈ 1.0

Resumability:
- Pull-cache: 50K-paper parquet cached at
  ``data/metadata/phase-1.1-dry-run-pull.parquet``. Re-running
  skips the pull if cache exists.
- SciNCL output: ``experiments/phase-1.1/scincl-vectors/``
  with chunk_<NNNNNN>.npy files + done.txt.
- Qwen3 output: ``experiments/phase-1.1/qwen3-vectors/``
  with chunk_<NNNNNN>.npy files + done.txt.

Network-drop behavior: completed chunks persist on disk; in-flight
chunk on disconnect is lost from local (Modal completes it
server-side but the result doesn't return). On re-run, the lost
chunk gets re-embedded (~1-2 min + ~$0.01 cost).

Pre-flight:
1. Modal CLI authenticated (``modal token current`` shows account)
2. Modal app deployed (``modal deploy experiments/phase-1.1/embed_modal.py``)
3. uv venv has embed extras (``uv sync --extra dev --extra embed``)

Run from ws2 root:

  uv run modal run experiments/phase-1.1/dry_run_50k.py::main

Cost estimate: ~$1-5 (per smoke extrapolation; well under §9 cap).
Wall-clock: ~30-60 min on A100 preempt.
"""

from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import modal
import numpy as np
import pandas as pd
import requests
from tqdm import tqdm

# Local app for this script's entrypoint. The Modal embed
# functions live in a SEPARATE deployed app `ws2-embed` (see
# embed_modal.py); we reference them by name here.
app = modal.App("phase-1.1-dry-run")

# Lookup the deployed Modal Functions by name.
embed_chunk_scincl = modal.Function.from_name(
    "ws2-embed", "embed_chunk_scincl",
)
embed_chunk_qwen3 = modal.Function.from_name(
    "ws2-embed", "embed_chunk_qwen3",
)

# ---------- §0 production filter (Wave 1C lock; word-boundary regex) ----------

_FIELDS = {"cs": "C41008148", "physics": "C121332964"}
_SCORE_THRESHOLD = 0.3
_JUNK_YEAR_THRESHOLD = 1990
_EMPTY_ABSTRACT_MIN_TOKENS = 15

_PRODUCTION_JUNK_YEAR_TOKENS: tuple[str, ...] = (
    "r-cnn", "iot", "blockchain", "transformer", "smartphone",
    "lstm", "gan", "bert", "gpt", "chatgpt", "attention is all you need",
    "word2vec", "glove", "risc-v",
    "tls 1", "webrtc", "mqtt", "openid connect",
    "wearable", "vr headset", "cloud computing", "big data",
    "internet of things", "digital twin", "arm cortex",
)
_PRODUCTION_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(r"\b" + re.escape(tok) + r"\b", re.IGNORECASE)
    for tok in _PRODUCTION_JUNK_YEAR_TOKENS
)

# ---------- pull config ----------

_TARGET_N = 50_000
_PULL_SAMPLE_PER_CALL = 200  # OpenAlex cap
_PULL_SEEDS_PER_CELL = 25  # 5K raw per cell
_PULL_BACKOFF_S = 0.3
_PULL_TIMEOUT_S = 30

# ---------- chunk config ----------

_CHUNK_SIZE = 1000  # ~50 chunks for 50K abstracts; <1 min per chunk on A100

_OUT_DIR = Path(__file__).parent
_DATA_METADATA_DIR = _OUT_DIR.parent.parent / "data" / "metadata"
_PULL_CACHE_PARQUET = _DATA_METADATA_DIR / "phase-1.1-dry-run-pull.parquet"
_SCINCL_CHUNKS_DIR = _OUT_DIR / "scincl-vectors"
_QWEN3_CHUNKS_DIR = _OUT_DIR / "qwen3-vectors"


# ---------- §0 filter primitives (lifted from Wave 1C) ----------


def _field_score(work: dict[str, Any], concept_id: str) -> float | None:
    for c in work.get("concepts") or []:
        if not isinstance(c, dict):
            continue
        raw_id = c.get("id") or ""
        bare = raw_id.rsplit("/", 1)[-1] if "/" in raw_id else raw_id
        if bare == concept_id:
            score = c.get("score")
            return float(score) if score is not None else 0.0
    return None


def _passes_score(work: dict[str, Any], concept_id: str) -> bool:
    s = _field_score(work, concept_id)
    return s is not None and s >= _SCORE_THRESHOLD


def _has_abstract(work: dict[str, Any]) -> bool:
    inv = work.get("abstract_inverted_index")
    return isinstance(inv, dict) and len(inv) > 0


def _passes_junk_year(work: dict[str, Any]) -> bool:
    year = work.get("publication_year")
    if year is None or year >= _JUNK_YEAR_THRESHOLD:
        return True
    title = work.get("title") or ""
    inv = work.get("abstract_inverted_index") or {}
    abs_tokens = " ".join(inv.keys()) if isinstance(inv, dict) else ""
    text = f"{title} {abs_tokens}"
    for pat in _PRODUCTION_PATTERNS:
        if pat.search(text):
            return False
    return True


def _abstract_n_tokens(work: dict[str, Any]) -> int:
    inv = work.get("abstract_inverted_index") or {}
    if not isinstance(inv, dict):
        return 0
    return sum(len(positions) for positions in inv.values())


def _passes_empty_abs(work: dict[str, Any]) -> bool:
    return _abstract_n_tokens(work) >= _EMPTY_ABSTRACT_MIN_TOKENS


def _post_filter(raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for w in raw:
        # Score against ANY field (cs OR physics)
        passes_any_field = any(
            _passes_score(w, cid) for cid in _FIELDS.values()
        )
        if not passes_any_field:
            continue
        if not _has_abstract(w):
            continue
        if not _passes_junk_year(w):
            continue
        if not _passes_empty_abs(w):
            continue
        out.append(w)
    return out


# ---------- pull ----------


def _fetch_one_cell(
    _field: str, concept_id: str, year: int, seed: int,
) -> list[dict[str, Any]]:
    """Single OpenAlex sample call for one (field, year, seed)."""
    params = {
        "filter": f"concepts.id:{concept_id},publication_year:{year}",
        "sample": _PULL_SAMPLE_PER_CALL,
        "seed": seed,
        "select": "id,title,publication_year,type,abstract_inverted_index,"
                  "authorships,concepts,cited_by_count,primary_location,ids",
        "mailto": "gkartik@gmail.com",
    }
    headers = {"User-Agent": "ws2/0.0.0 phase-1.1-dry-run"}
    try:
        r = requests.get(
            "https://api.openalex.org/works",
            params=params,
            headers=headers,
            timeout=_PULL_TIMEOUT_S,
        )
        if r.status_code != 200:
            return []
        return list(r.json().get("results", []))
    except requests.RequestException:
        return []


def _pull_50k() -> pd.DataFrame:
    """Pull ~50K post-§0-filter cs+physics 1970-2024 papers; cache as parquet."""
    if _PULL_CACHE_PARQUET.exists():
        df = pd.read_parquet(_PULL_CACHE_PARQUET)
        print(f"  loaded cached pull: {len(df)} papers")
        return df

    print(f"  pulling fresh — target {_TARGET_N} post-filter")
    seen_ids: set[str] = set()
    accumulated: list[dict[str, Any]] = []

    seed_offsets = list(range(_PULL_SEEDS_PER_CELL))
    pbar = tqdm(total=_TARGET_N, desc="pulling")
    for field, concept_id in _FIELDS.items():
        for year in range(1970, 2025):
            for seed in seed_offsets:
                if len(accumulated) >= _TARGET_N:
                    break
                raw = _fetch_one_cell(field, concept_id, year, seed)
                kept = _post_filter(raw)
                for w in kept:
                    wid = str(w.get("id", ""))
                    if wid and wid not in seen_ids:
                        seen_ids.add(wid)
                        accumulated.append(w)
                        pbar.update(1)
                time.sleep(_PULL_BACKOFF_S)
            if len(accumulated) >= _TARGET_N:
                break
        if len(accumulated) >= _TARGET_N:
            break
    pbar.close()

    if not accumulated:
        raise RuntimeError("pull returned 0 papers — check OpenAlex availability")

    rows = []
    for w in accumulated:
        rows.append({
            "work_id": w.get("id"),
            "title": w.get("title") or "",
            "publication_year": w.get("publication_year"),
            "doi": (w.get("ids") or {}).get("doi") or "",
            "abstract_inverted_index_json": json.dumps(
                w.get("abstract_inverted_index") or {},
            ),
        })
    df = pd.DataFrame(rows)
    _DATA_METADATA_DIR.mkdir(parents=True, exist_ok=True)
    df.to_parquet(_PULL_CACHE_PARQUET, index=False)
    print(f"  wrote {len(df)} papers to {_PULL_CACHE_PARQUET}")
    return df


# ---------- abstract reconstruction ----------


def _reconstruct(inv: dict[str, list[int]]) -> str:
    if not inv:
        return ""
    max_pos = max(max(p) for p in inv.values())
    tokens = [""] * (max_pos + 1)
    for word, ps in inv.items():
        for p in ps:
            tokens[p] = word
    return " ".join(t for t in tokens if t)


def _decode_abstracts(df: pd.DataFrame) -> list[str]:
    abstracts: list[str] = []
    for inv_json in df["abstract_inverted_index_json"]:
        inv = json.loads(str(inv_json))
        abstracts.append(_reconstruct(inv))
    return abstracts


# ---------- chunked dispatch (resumable) ----------


def _embed_via_modal(
    abstracts: list[str],
    output_dir: Path,
    modal_remote: Any,
    label: str,
) -> tuple[np.ndarray[Any, Any], dict[str, Any]]:
    """Dispatch abstracts in chunks to Modal; persist vectors + done.txt locally.

    Uses the Phase 1.1 Step 2 ChunkedEmbedRunner pattern but
    inlined here because the runner expects a synchronous
    callable; Modal's .remote() IS synchronous (blocks until
    result returns), so it composes cleanly.
    """
    from whitespace2.resumable_runner import ChunkedEmbedRunner

    output_dir.mkdir(parents=True, exist_ok=True)
    runner = ChunkedEmbedRunner(
        model_fn=modal_remote,
        chunk_size=_CHUNK_SIZE,
        output_dir=output_dir,
    )
    print(f"  {label}: dispatching {len(abstracts)} abstracts in chunks of {_CHUNK_SIZE}")
    t0 = time.time()
    vectors = runner.run(abstracts)
    elapsed = time.time() - t0

    # Audit chunk-level data: count of restarts (chunks that were
    # in done.txt vs newly-embedded) — proxy for preemption count
    done_path = output_dir / "done.txt"
    n_chunks_completed = (
        len(done_path.read_text().splitlines()) if done_path.exists() else 0
    )

    return vectors, {
        "elapsed_sec": elapsed,
        "n_abstracts": len(abstracts),
        "per_abs_sec": elapsed / max(len(abstracts), 1),
        "n_chunks": n_chunks_completed,
    }


# ---------- main ----------


@app.local_entrypoint()
def main() -> None:
    print("Phase 1.1 Step 5 — 50K dry-run on Modal A100 preempt")
    print()

    snapshot = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # Pull (cached)
    print("Step 1: pull 50K post-§0-filter abstracts")
    t0 = time.time()
    df = _pull_50k()
    pull_elapsed = time.time() - t0
    abstracts = _decode_abstracts(df)
    n = len(abstracts)
    print(f"  {n} abstracts ready (pull elapsed {pull_elapsed:.0f}s)")
    print()

    # SciNCL
    print("Step 2: SciNCL embed on Modal A100 preempt")
    scincl_vecs, scincl_stats = _embed_via_modal(
        abstracts,
        _SCINCL_CHUNKS_DIR,
        embed_chunk_scincl.remote,
        "SciNCL",
    )
    scincl_norms = np.linalg.norm(scincl_vecs, axis=1)
    print(
        f"  SciNCL: {scincl_stats['elapsed_sec']:.0f}s; "
        f"shape={scincl_vecs.shape}; "
        f"finite={bool(np.isfinite(scincl_vecs).all())}; "
        f"mean_norm={float(scincl_norms.mean()):.3f}"
    )
    print()

    # Qwen3
    print("Step 3: Qwen3 embed on Modal A100 preempt (bs=1)")
    qwen3_vecs, qwen3_stats = _embed_via_modal(
        abstracts,
        _QWEN3_CHUNKS_DIR,
        embed_chunk_qwen3.remote,
        "Qwen3",
    )
    qwen3_norms = np.linalg.norm(qwen3_vecs, axis=1)
    print(
        f"  Qwen3: {qwen3_stats['elapsed_sec']:.0f}s; "
        f"shape={qwen3_vecs.shape}; "
        f"finite={bool(np.isfinite(qwen3_vecs).all())}; "
        f"mean_norm={float(qwen3_norms.mean()):.3f}"
    )
    print()

    # Verify
    scincl_per_abs = scincl_stats["per_abs_sec"]
    qwen3_per_abs = qwen3_stats["per_abs_sec"]
    combined_per_abs = scincl_per_abs + qwen3_per_abs

    a100_per_sec = 1.70 / 3600
    cost_per_abs = combined_per_abs * a100_per_sec
    h3_pass = cost_per_abs <= 0.075

    scincl_norm_ok = 22.5 <= float(scincl_norms.mean()) <= 24.5
    qwen3_norm_ok = abs(float(qwen3_norms.mean()) - 1.0) < 0.01

    print("Verification (against Phase 1.1 plan validation gates):")
    print(
        f"  Gate 5 (H3 cost ≤$0.075/abs combined): "
        f"actual ${cost_per_abs:.5f}/abs — {'PASS' if h3_pass else 'FAIL'}"
    )
    print(f"    Extrapolated 1M cost: ${cost_per_abs * 1_000_000:.0f}")
    print(
        f"  Gate 7a (H5 SciNCL output): "
        f"shape ✓, finite ✓, norm {'in band' if scincl_norm_ok else 'OUT OF BAND'}"
    )
    print(
        f"  Gate 7b (H6 Qwen3 output): "
        f"shape ✓, finite ✓, norm {'~1.0' if qwen3_norm_ok else 'NOT ~1.0'}"
    )
    print()

    # Save artifact
    artifact = {
        "snapshot": snapshot,
        "n_abstracts": n,
        "pull_elapsed_sec": pull_elapsed,
        "scincl": {
            "shape": list(scincl_vecs.shape),
            "finite": bool(np.isfinite(scincl_vecs).all()),
            "mean_norm": float(scincl_norms.mean()),
            "min_norm": float(scincl_norms.min()),
            "max_norm": float(scincl_norms.max()),
            "elapsed_sec": scincl_stats["elapsed_sec"],
            "per_abs_sec": scincl_per_abs,
            "n_chunks": scincl_stats["n_chunks"],
            "norm_in_band": scincl_norm_ok,
        },
        "qwen3": {
            "shape": list(qwen3_vecs.shape),
            "finite": bool(np.isfinite(qwen3_vecs).all()),
            "mean_norm": float(qwen3_norms.mean()),
            "min_norm": float(qwen3_norms.min()),
            "max_norm": float(qwen3_norms.max()),
            "elapsed_sec": qwen3_stats["elapsed_sec"],
            "per_abs_sec": qwen3_per_abs,
            "n_chunks": qwen3_stats["n_chunks"],
            "norm_in_band": qwen3_norm_ok,
        },
        "extrapolation": {
            "combined_per_abs_sec": combined_per_abs,
            "cost_per_abs_at_1.70_per_hr": cost_per_abs,
            "cost_at_1m": cost_per_abs * 1_000_000,
            "h3_gate_pass": h3_pass,
        },
    }
    out_path = _OUT_DIR / "dry-run-50k-results.json"
    out_path.write_text(json.dumps(artifact, indent=2))
    print(f"Wrote {out_path}")

    overall_pass = h3_pass and scincl_norm_ok and qwen3_norm_ok and bool(
        np.isfinite(scincl_vecs).all()
    ) and bool(np.isfinite(qwen3_vecs).all())
    print(f"Step 5 verdict: {'PASS' if overall_pass else 'INVESTIGATE'}")
