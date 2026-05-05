"""Phase 0.2 Wave 2A followup — Path B: bigger held-outs, re-project.

Tests whether the K=50 sign-flip pattern (S concentrates 1975, U
concentrates 2020) observed at |H_1975|=49 / |H_2020|=45
stabilizes when held-outs are 4×-10× larger. Uses the existing
S/U cluster fits from Wave 2A full mode — no re-fit, no re-embed
of S/U.

Pulls:
- New H_1975 (target 200) using fresh seeds disjoint from existing
  S/U/H_1975 pools.
- New H_2020 (target 200) using fresh seeds disjoint from existing
  S/U/H_2020 pools.

Embeds: SPECTER2 on the new held-outs (~170 sec for 400 papers).

Projection: hard-assign to nearest centroid in each (K, fit) ∈
{30, 50, 100} × {S, U}. Compute effN per (K, fit, held-out cell).

Decision input:
- If sign-flip pattern (S < U for H_1975, S > U for H_2020)
  stabilizes at bigger N with NC pass: Path A (rewrite §11
  with empirical direction).
- If both sign-flip and NC fail at bigger N: Path C (drop §11
  commitment).
- If sign-flip works but NC still fails: noise-still-dominant;
  Path D (full-corpus U pool) or Path C.

Run from ws2 root:
    uv run python experiments/phase-0.2/section11_followup_bigger_heldouts.py
"""

from __future__ import annotations

import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
from tqdm import tqdm

from whitespace2 import embeddings as emb
from whitespace2 import openalex

_OUT_DIR = Path(__file__).parent
_DATA_METADATA_DIR = _OUT_DIR.parent.parent / "data" / "metadata"

# §0 production filter (regex word-boundary; Wave 1C fix)
_FIELD_CONCEPT_ID = "C41008148"
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

_SELECT = [
    "id", "title", "publication_year", "type",
    "abstract_inverted_index", "authorships", "concepts",
    "cited_by_count", "primary_location", "ids",
]

# Followup targets
_HELDOUT_TARGET = 200
_SAMPLE_PER_CELL = 200
_HELDOUT_1975_SEEDS = list(range(200, 230))  # 30 seeds, fresh
_HELDOUT_2020_SEEDS = list(range(230, 240))  # 10 seeds, fresh

# Cluster fit Ks (already fit; just project)
_K_VALUES = (30, 50, 100)
_H7_ARTIFACT_RATIO = 1.43
_H7_NEGATIVE_CONTROL_TOL = 0.20

_DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
_DTYPE = "fp16"
_BS_SPECTER = 8


# ---------- filter primitives ----------


def _field_concept_score(work: dict[str, Any]) -> float | None:
    for c in work.get("concepts") or []:
        if not isinstance(c, dict):
            continue
        raw_id = c.get("id") or ""
        bare = raw_id.rsplit("/", 1)[-1] if "/" in raw_id else raw_id
        if bare == _FIELD_CONCEPT_ID:
            score = c.get("score")
            return float(score) if score is not None else 0.0
    return None


def _passes_score_threshold(work: dict[str, Any]) -> bool:
    score = _field_concept_score(work)
    return score is not None and score >= _SCORE_THRESHOLD


def _passes_junk_year_filter(work: dict[str, Any]) -> bool:
    year = work.get("publication_year")
    if year is None or year >= _JUNK_YEAR_THRESHOLD:
        return True
    title = work.get("title") or ""
    inv = work.get("abstract_inverted_index") or {}
    abs_str = " ".join(inv.keys()) if isinstance(inv, dict) else ""
    text = f"{title} {abs_str}"
    for pattern in _PRODUCTION_PATTERNS:
        if pattern.search(text):
            return False
    return True


def _abstract_token_count(work: dict[str, Any]) -> int:
    inv = work.get("abstract_inverted_index") or {}
    if not isinstance(inv, dict):
        return 0
    return sum(len(positions) for positions in inv.values())


def _passes_empty_abstract_filter(work: dict[str, Any]) -> bool:
    return _abstract_token_count(work) >= _EMPTY_ABSTRACT_MIN_TOKENS


def _post_filter(raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
    after_score = [w for w in raw if _passes_score_threshold(w)]
    after_abstract = [w for w in after_score if openalex.has_abstract(w)]
    after_junk = [w for w in after_abstract if _passes_junk_year_filter(w)]
    return [w for w in after_junk if _passes_empty_abstract_filter(w)]


def _pull_one(filters: dict[str, str], seed: int) -> list[dict[str, Any]]:
    try:
        raw = openalex.fetch_works(
            filters=filters, sample_size=_SAMPLE_PER_CELL,
            seed=seed, select=_SELECT,
        )
    except RuntimeError as err:
        print(f"  WARN: seed={seed}: {err}")
        return []
    return _post_filter(raw)


def _pull_heldout_disjoint(
    year: int, seeds: list[int], target: int, exclude_ids: set[str],
) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    pbar = tqdm(seeds, desc=f"heldout cs/{year}")
    for seed in pbar:
        if len(out) >= target:
            break
        kept = _pull_one(
            {"concepts.id": _FIELD_CONCEPT_ID, "publication_year": str(year)},
            seed=seed,
        )
        for w in kept:
            wid = str(w.get("id", ""))
            if wid and wid not in seen and wid not in exclude_ids:
                seen.add(wid)
                out.append(w)
        pbar.set_postfix({f"|H_{year}|": len(out)})
        time.sleep(0.3)
    return out[:target]


def _reconstruct(inv: dict[str, list[int]]) -> str:
    if not inv:
        return ""
    max_pos = max(max(positions) for positions in inv.values())
    tokens = [""] * (max_pos + 1)
    for word, positions in inv.items():
        for pos in positions:
            tokens[pos] = word
    return " ".join(t for t in tokens if t)


def _decode_abstracts(works: list[dict[str, Any]]) -> list[str]:
    return [
        _reconstruct(w.get("abstract_inverted_index") or {}) for w in works
    ]


def _l2_normalize(vectors: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.where(norms > 0, norms, 1.0)
    return (vectors / norms).astype(np.float32)


def _project(
    vectors: np.ndarray[Any, Any], centroids: np.ndarray[Any, Any],
) -> np.ndarray[Any, Any]:
    """Hard-assign via Euclidean distance (KMeans-consistent).

    For unit-norm v and non-unit-norm c (KMeans centroids of unit
    vectors typically have norms 0.92-0.94), argmax(v·c) is NOT
    KMeans-consistent. Use argmin(‖v-c‖²) = argmax(2·v·c - ‖c‖²).
    Bug history: pre-fix used argmax(v·c) and produced reversed
    results. See `section11_reproject_fix.py`.
    """
    centroid_norms_sq = np.sum(centroids ** 2, axis=1)
    scores = 2 * (vectors @ centroids.T) - centroid_norms_sq[None, :]
    return np.argmax(scores, axis=1)


def _eff_n(assignments: np.ndarray[Any, Any], k: int) -> float:
    counts = np.bincount(assignments, minlength=k)
    n_total = int(counts.sum())
    if n_total == 0:
        return 0.0
    p = counts / n_total
    p_pos = p[p > 0]
    h = -float((p_pos * np.log(p_pos)).sum())
    return float(np.exp(h))


def main() -> None:
    print("Phase 0.2 Wave 2A followup — Path B (bigger held-outs)")
    print()

    snapshot = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # 1. Load existing S/U/H_1975/H_2020 ids to enforce disjointness
    print("Loading existing S/U/H pools (for disjoint enforcement)...")
    s_df = pd.read_parquet(_DATA_METADATA_DIR / "section11-prod-S.parquet")
    u_df = pd.read_parquet(_DATA_METADATA_DIR / "section11-prod-U.parquet")
    h75_old_df = pd.read_parquet(
        _DATA_METADATA_DIR / "section11-prod-H_1975.parquet"
    )
    h20_old_df = pd.read_parquet(
        _DATA_METADATA_DIR / "section11-prod-H_2020.parquet"
    )
    exclude_ids = (
        set(s_df["work_id"]) | set(u_df["work_id"])
        | set(h75_old_df["work_id"]) | set(h20_old_df["work_id"])
    )
    print(f"  excluding {len(exclude_ids)} ids from existing pools")
    print()

    # 2. Pull bigger held-outs (disjoint)
    print(f"Pulling H_1975 followup (target {_HELDOUT_TARGET})...")
    h75_works = _pull_heldout_disjoint(
        1975, _HELDOUT_1975_SEEDS, _HELDOUT_TARGET, exclude_ids,
    )
    print(f"  |H_1975_followup| = {len(h75_works)}")

    # Update exclude_ids before next pull
    exclude_ids |= {str(w.get("id", "")) for w in h75_works}

    print(f"Pulling H_2020 followup (target {_HELDOUT_TARGET})...")
    h20_works = _pull_heldout_disjoint(
        2020, _HELDOUT_2020_SEEDS, _HELDOUT_TARGET, exclude_ids,
    )
    print(f"  |H_2020_followup| = {len(h20_works)}")
    print()

    # 3. Embed new held-outs
    print("Embedding new held-outs (SPECTER2)...")
    h75_abs = _decode_abstracts(h75_works)
    h20_abs = _decode_abstracts(h20_works)

    t0 = time.time()
    h75_vec = emb.embed_specter2(
        h75_abs, device=_DEVICE, batch_size=_BS_SPECTER, dtype=_DTYPE,
    )
    h20_vec = emb.embed_specter2(
        h20_abs, device=_DEVICE, batch_size=_BS_SPECTER, dtype=_DTYPE,
    )
    embed_time = time.time() - t0
    print(f"  embedding total: {embed_time:.0f}s "
          f"({embed_time/(len(h75_abs)+len(h20_abs)):.3f} s/abs)")
    print()

    # L2 normalize
    h75_norm = _l2_normalize(h75_vec)
    h20_norm = _l2_normalize(h20_vec)

    # 4. Re-project onto existing cluster fits + compute H7'
    print("Loading cluster fits + projecting...")
    results: dict[int, dict[str, Any]] = {}
    for k in _K_VALUES:
        s_centroids = np.load(
            _DATA_METADATA_DIR / f"section11-cluster-fit-S-K{k}.npy"
        )
        u_centroids = np.load(
            _DATA_METADATA_DIR / f"section11-cluster-fit-U-K{k}.npy"
        )

        h75_in_s = _project(h75_norm, s_centroids)
        h75_in_u = _project(h75_norm, u_centroids)
        h20_in_s = _project(h20_norm, s_centroids)
        h20_in_u = _project(h20_norm, u_centroids)

        eff_n_s_h75 = _eff_n(h75_in_s, k)
        eff_n_u_h75 = _eff_n(h75_in_u, k)
        eff_n_s_h20 = _eff_n(h20_in_s, k)
        eff_n_u_h20 = _eff_n(h20_in_u, k)

        artifact_ratio = (
            eff_n_s_h75 / eff_n_u_h75 if eff_n_u_h75 > 0 else float("inf")
        )
        artifact_pass_orig = artifact_ratio > _H7_ARTIFACT_RATIO
        artifact_pass_inverted = artifact_ratio < (1.0 / _H7_ARTIFACT_RATIO)
        # Inverted Path A direction: S concentrates → ratio < 1/1.43 = 0.70
        nc_max = max(eff_n_s_h20, eff_n_u_h20)
        nc_rel_diff = (
            abs(eff_n_s_h20 - eff_n_u_h20) / nc_max if nc_max > 0 else 0.0
        )
        nc_pass = nc_rel_diff < _H7_NEGATIVE_CONTROL_TOL

        # Path A signal: opposite direction sign-flip
        # H_1975: ratio < 1 (S concentrates)
        # H_2020: ratio > 1 (U concentrates) → ratio_h20 = effN_S/effN_U > 1
        ratio_h20 = (
            eff_n_s_h20 / eff_n_u_h20 if eff_n_u_h20 > 0 else float("inf")
        )
        sign_flip_present = artifact_ratio < 1.0 and ratio_h20 > 1.0

        results[k] = {
            "eff_n_s_h75": eff_n_s_h75,
            "eff_n_u_h75": eff_n_u_h75,
            "eff_n_s_h20": eff_n_s_h20,
            "eff_n_u_h20": eff_n_u_h20,
            "artifact_ratio": artifact_ratio,
            "ratio_h20": ratio_h20,
            "artifact_pass_orig": artifact_pass_orig,
            "artifact_pass_inverted": artifact_pass_inverted,
            "nc_rel_diff": nc_rel_diff,
            "nc_pass": nc_pass,
            "sign_flip_present": sign_flip_present,
            "n_h75": len(h75_works),
            "n_h20": len(h20_works),
        }

        print(
            f"  K={k}: ratio_H75={artifact_ratio:.2f}, "
            f"ratio_H20={ratio_h20:.2f}, NC_rd={nc_rel_diff:.3f}, "
            f"sign_flip={'YES' if sign_flip_present else 'NO'}, "
            f"NC={'PASS' if nc_pass else 'FAIL'}"
        )
    print()

    # 5. Compare with original (|H_1975|=49, |H_2020|=45) results
    orig = {
        30: {"ratio_h75": 0.80, "ratio_h20": 0.531, "nc_rd": 0.469, "nc_pass": False},
        50: {"ratio_h75": 0.84, "ratio_h20": 1.16, "nc_rd": 0.138, "nc_pass": True},
        100: {"ratio_h75": 1.05, "ratio_h20": 0.618, "nc_rd": 0.382, "nc_pass": False},
    }
    # Note orig ratio_h20 computed from md numbers: K=50 (7.93/6.83=1.16),
    # K=30 (4.87/9.17=0.531), K=100 (8.18/13.22=0.618).

    # 6. Decision logic
    sign_flip_at_k50 = results[50]["sign_flip_present"]
    nc_pass_at_k50 = results[50]["nc_pass"]
    sign_flip_count = sum(1 for k in _K_VALUES if results[k]["sign_flip_present"])
    nc_pass_count = sum(1 for k in _K_VALUES if results[k]["nc_pass"])

    if sign_flip_count >= 2 and nc_pass_count >= 1:
        verdict = "PATH_A_SUPPORTED"
        verdict_msg = (
            f"Sign-flip stable at {sign_flip_count}/3 K values; "
            f"NC passes at {nc_pass_count}/3. §11 mechanism real, "
            "opposite direction. Recommend Path A (rewrite §11 with "
            "empirical direction)."
        )
    elif sign_flip_at_k50 and nc_pass_at_k50:
        verdict = "PATH_A_K50_ONLY"
        verdict_msg = (
            "K=50 sign-flip + NC pass clean, but pattern not stable "
            "across K. Path A defensible at K=50 only; Path C also "
            "reasonable."
        )
    elif sign_flip_count == 0:
        verdict = "PATH_C_RECOMMENDED"
        verdict_msg = (
            "No sign-flip pattern at any K. §11 mechanism not "
            "detectable at this scale. Recommend Path C (drop "
            "commitment) or Path D (full-corpus U pool)."
        )
    else:
        verdict = "MIXED"
        verdict_msg = (
            "Mixed signal across K. User judgment between A/C/D."
        )

    print(f"=== Verdict: {verdict} ===")
    print(verdict_msg)
    print()

    # 7. Write artifact md
    table_rows = "\n".join(
        f"| K={k} | {results[k]['eff_n_s_h75']:.2f} | "
        f"{results[k]['eff_n_u_h75']:.2f} | "
        f"{results[k]['artifact_ratio']:.2f} | "
        f"{results[k]['eff_n_s_h20']:.2f} | "
        f"{results[k]['eff_n_u_h20']:.2f} | "
        f"{results[k]['ratio_h20']:.2f} | "
        f"{results[k]['nc_rel_diff']:.3f} | "
        f"{'YES' if results[k]['sign_flip_present'] else 'NO'} | "
        f"{'PASS' if results[k]['nc_pass'] else 'FAIL'} |"
        for k in _K_VALUES
    )
    orig_table = "\n".join(
        f"| K={k} | {orig[k]['ratio_h75']:.2f} | {orig[k]['ratio_h20']:.2f} | "
        f"{orig[k]['nc_rd']:.3f} | "
        f"{'PASS' if orig[k]['nc_pass'] else 'FAIL'} |"
        for k in _K_VALUES
    )

    body = f"""# Phase 0.2 Wave 2A followup — Path B (bigger held-outs)

**Run date:** {datetime.now(timezone.utc).date().isoformat()}
**Snapshot:** {snapshot}
**Mode:** FOLLOWUP (Path B)
**Scope:** New disjoint held-outs (target {_HELDOUT_TARGET}/cell);
re-project onto existing S/U cluster fits at K∈{{30, 50, 100}}.

## Headline

**Verdict: {verdict}**

{verdict_msg}

## Followup pull summary

| Cell | Target | Actual | Disjoint from |
|---|---:|---:|---|
| H_1975 fu | {_HELDOUT_TARGET} | {len(h75_works)} | S, U, H_1975, H_2020 |
| H_2020 fu | {_HELDOUT_TARGET} | {len(h20_works)} | S, U, H_1975 fu+orig, H_2020 |

Embedding wall-clock: {embed_time:.0f}s
({embed_time/(len(h75_abs)+len(h20_abs)):.3f} s/abs).

## Followup H7' projection results

| K | S/H75 | U/H75 | r_H75 | S/H20 | U/H20 | r_H20 | NC rd | sign-flip? | NC? |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
{table_rows}

**sign-flip** = (r_H75 < 1.0 AND r_H20 > 1.0): the empirical Path A pattern
where S concentrates 1975 papers AND U concentrates 2020 papers
(decade-balanced fit favors old; Nᵧ-proportional fit favors recent).

## Comparison vs original (|H_1975|=49, |H_2020|=45)

| K | r_H75 (orig) | r_H20 (orig) | NC rd (orig) | NC (orig) |
|---|---:|---:|---:|---|
{orig_table}

| K | r_H75 (orig→fu) | r_H20 (orig→fu) | NC rd (orig→fu) |
|---|---|---|---|
"""
    for k in _K_VALUES:
        body += (
            f"| K={k} | {orig[k]['ratio_h75']:.2f}→"
            f"{results[k]['artifact_ratio']:.2f} | "
            f"{orig[k]['ratio_h20']:.2f}→"
            f"{results[k]['ratio_h20']:.2f} | "
            f"{orig[k]['nc_rd']:.3f}→"
            f"{results[k]['nc_rel_diff']:.3f} |\n"
        )

    body += f"""

## Decision

{verdict_msg}

Reading map (per `section11-production-validation.md`):

- **Path A** = rewrite §11 with empirical direction (S concentrates
  old; U concentrates recent). Defensible if sign-flip stabilizes.
- **Path C** = drop §11 commitment. Always available; simpler
  narrative; loses defensive layer.
- **Path D** = full-corpus U pool (~500K). Expensive ($50-150
  embedding cost); tests §11's full mechanism.

## Artifacts

- `experiments/phase-0.2/section11-followup-bigger-heldouts.md` — this artifact
- `experiments/phase-0.2/section11-followup-summary.json` — machine summary
- `data/metadata/section11-prod-H_1975-followup.parquet` — new H_1975
- `data/metadata/section11-prod-H_2020-followup.parquet` — new H_2020
- `data/metadata/section11-prod-H_1975-vec-followup.npy` — embed
- `data/metadata/section11-prod-H_2020-vec-followup.npy` — embed
- `experiments/phase-0.2/section11_followup_bigger_heldouts.py` — script
"""
    md_path = _OUT_DIR / "section11-followup-bigger-heldouts.md"
    md_path.write_text(body)
    print(f"wrote {md_path}")

    # Save followup pulls + vectors
    h75_followup_df = pd.DataFrame([
        {
            "work_id": w.get("id"),
            "publication_year": w.get("publication_year"),
            "title": w.get("title") or "",
            "doi": openalex.extract_doi(w),
        }
        for w in h75_works
    ])
    h20_followup_df = pd.DataFrame([
        {
            "work_id": w.get("id"),
            "publication_year": w.get("publication_year"),
            "title": w.get("title") or "",
            "doi": openalex.extract_doi(w),
        }
        for w in h20_works
    ])
    h75_followup_df.to_parquet(
        _DATA_METADATA_DIR / "section11-prod-H_1975-followup.parquet",
        index=False,
    )
    h20_followup_df.to_parquet(
        _DATA_METADATA_DIR / "section11-prod-H_2020-followup.parquet",
        index=False,
    )
    np.save(
        _DATA_METADATA_DIR / "section11-prod-H_1975-vec-followup.npy", h75_vec
    )
    np.save(
        _DATA_METADATA_DIR / "section11-prod-H_2020-vec-followup.npy", h20_vec
    )

    summary = {
        "snapshot": snapshot,
        "n_h75_followup": len(h75_works),
        "n_h20_followup": len(h20_works),
        "embed_sec": embed_time,
        "results": {
            str(k): {kk: vv for kk, vv in r.items()}
            for k, r in results.items()
        },
        "orig": orig,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
    }
    summary_path = _OUT_DIR / "section11-followup-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, default=str))
    print(f"wrote {summary_path}")
    print()
    print(f"Wave 2A followup complete. Verdict: {verdict}")


if __name__ == "__main__":
    main()
    sys.exit(0)
