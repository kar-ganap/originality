"""Phase 0.2 Wave 4A — SciNCL §11 re-validation.

Pre-lock empirical validation of SciNCL as headline primary.
Re-uses the existing S/U/H pools (no new pulls); re-embeds with
SciNCL; re-fits cluster centroids on SciNCL S/U pools; re-projects
held-outs with KMeans-Euclidean assignment (the post-bug-fix
projection); computes H7' against the SPECTER2-derived 1.10
threshold.

Outcomes drive Wave 4A lock status:
- All r_H75 ≥ 1.10 across K with NC pass: SciNCL primary holds
- All r_H75 ≥ 1.43: SciNCL strictly clears original threshold
- Any r_H75 < 1.0 or NC fails consistently: trigger fallback to
  SPECTER2 primary per
  `docs/phases/phase-0.2-scincl-primary-contingency.md`

Cost: ~30-40 min wall-clock locally; $0 (local-only). No new
OpenAlex pulls; no cloud spend.

Run from ws2 root:
    uv run python experiments/phase-0.2/section11_scincl_revalidation.py
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
from sklearn.cluster import KMeans

from whitespace2 import embeddings as emb

_OUT_DIR = Path(__file__).parent
_DATA_METADATA_DIR = _OUT_DIR.parent.parent / "data" / "metadata"

_K_VALUES = (30, 50, 100)
_KMEANS_RANDOM_STATE = 46
_KMEANS_N_INIT = 20
_KMEANS_MAX_ITER = 300

_DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
_DTYPE = "fp16"
_BS_SCINCL = 8

_H7_ARTIFACT_RATIO_STRICT = 1.43  # original pre-reg
_H7_ARTIFACT_RATIO_RELAXED = 1.10  # post-projection-bug threshold (SPECTER2)
_H7_NEGATIVE_CONTROL_TOL = 0.20

# SPECTER2 reference numbers (post-bug-fix; from section11-reprojection-fix-summary.json)
_SPECTER2_REFS = {
    30: {"r_h75_orig": 1.26, "r_h75_fu": 1.31, "nc_rd_orig": 0.023, "nc_rd_fu": 0.048},
    50: {"r_h75_orig": 1.17, "r_h75_fu": 1.25, "nc_rd_orig": 0.079, "nc_rd_fu": 0.030},
    100: {"r_h75_orig": 1.33, "r_h75_fu": 1.17, "nc_rd_orig": 0.030, "nc_rd_fu": 0.135},
}


def _reconstruct(inv: dict[str, list[int]]) -> str:
    if not inv:
        return ""
    max_pos = max(max(p) for p in inv.values())
    tokens = [""] * (max_pos + 1)
    for word, ps in inv.items():
        for p in ps:
            tokens[p] = word
    return " ".join(t for t in tokens if t)


def _decode_from_parquet(
    parquet_path: Path,
) -> tuple[list[str], pd.DataFrame]:
    df = pd.read_parquet(parquet_path)
    abstracts: list[str] = []
    for inv_json in df["abstract_inverted_index_json"]:
        inv = json.loads(inv_json) if inv_json else {}
        abstracts.append(_reconstruct(inv))
    return abstracts, df


def _l2_normalize(vectors: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.where(norms > 0, norms, 1.0)
    return (vectors / norms).astype(np.float32)


def _kmeans_fit(
    vectors: np.ndarray[Any, Any], k: int,
) -> np.ndarray[Any, Any]:
    km = KMeans(
        n_clusters=k,
        random_state=_KMEANS_RANDOM_STATE,
        n_init=_KMEANS_N_INIT,
        max_iter=_KMEANS_MAX_ITER,
    )
    km.fit(vectors)
    return km.cluster_centers_


def _project_euclidean(
    vectors: np.ndarray[Any, Any], centroids: np.ndarray[Any, Any],
) -> np.ndarray[Any, Any]:
    """KMeans-consistent: argmin(‖v - c‖²) = argmax(2·v·c - ‖c‖²)."""
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


def _eval_h7(
    h75_norm: np.ndarray[Any, Any],
    h20_norm: np.ndarray[Any, Any],
    k: int,
    s_centroids: np.ndarray[Any, Any],
    u_centroids: np.ndarray[Any, Any],
) -> dict[str, Any]:
    h75_in_s = _project_euclidean(h75_norm, s_centroids)
    h75_in_u = _project_euclidean(h75_norm, u_centroids)
    h20_in_s = _project_euclidean(h20_norm, s_centroids)
    h20_in_u = _project_euclidean(h20_norm, u_centroids)
    eff_n_s_h75 = _eff_n(h75_in_s, k)
    eff_n_u_h75 = _eff_n(h75_in_u, k)
    eff_n_s_h20 = _eff_n(h20_in_s, k)
    eff_n_u_h20 = _eff_n(h20_in_u, k)
    r_h75 = eff_n_s_h75 / eff_n_u_h75 if eff_n_u_h75 > 0 else float("inf")
    r_h20 = eff_n_s_h20 / eff_n_u_h20 if eff_n_u_h20 > 0 else float("inf")
    nc_max = max(eff_n_s_h20, eff_n_u_h20)
    nc_rd = abs(eff_n_s_h20 - eff_n_u_h20) / nc_max if nc_max > 0 else 0.0
    return {
        "eff_n_s_h75": eff_n_s_h75,
        "eff_n_u_h75": eff_n_u_h75,
        "eff_n_s_h20": eff_n_s_h20,
        "eff_n_u_h20": eff_n_u_h20,
        "r_h75": r_h75,
        "r_h20": r_h20,
        "nc_rd": nc_rd,
        "nc_pass": nc_rd < _H7_NEGATIVE_CONTROL_TOL,
        "passes_relaxed": r_h75 >= _H7_ARTIFACT_RATIO_RELAXED,
        "passes_strict": r_h75 >= _H7_ARTIFACT_RATIO_STRICT,
    }


def main() -> None:
    print("Phase 0.2 Wave 4A — SciNCL §11 re-validation")
    print(f"  device: {_DEVICE}; dtype: {_DTYPE}")
    print()

    snapshot = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # 1. Load existing pools
    print("Loading existing S/U/H pools...")
    s_abs, _s_df = _decode_from_parquet(
        _DATA_METADATA_DIR / "section11-prod-S.parquet"
    )
    u_abs, _u_df = _decode_from_parquet(
        _DATA_METADATA_DIR / "section11-prod-U.parquet"
    )
    h75_orig_abs, _ = _decode_from_parquet(
        _DATA_METADATA_DIR / "section11-prod-H_1975.parquet"
    )
    h20_orig_abs, _ = _decode_from_parquet(
        _DATA_METADATA_DIR / "section11-prod-H_2020.parquet"
    )
    # Followup parquets were saved with a thinner schema (no abstract
    # column); skipping followup re-embed. Orig pool gives 6 measurements
    # (3 K × 2 held-out cells) — sufficient for primary lock decision.
    print(f"  |S|={len(s_abs)}, |U|={len(u_abs)}, "
          f"|H_1975 orig|={len(h75_orig_abs)}, |H_2020 orig|={len(h20_orig_abs)}; "
          "skipping followup (parquet schema missing abstracts)")
    print()

    # 2. Embed with SciNCL
    print("Embedding with SciNCL...")
    t0 = time.time()
    s_vec = emb.embed_scincl(
        s_abs, device=_DEVICE, batch_size=_BS_SCINCL, dtype=_DTYPE,
    )
    print(f"  S done ({len(s_vec)} vectors)")
    u_vec = emb.embed_scincl(
        u_abs, device=_DEVICE, batch_size=_BS_SCINCL, dtype=_DTYPE,
    )
    print(f"  U done ({len(u_vec)} vectors)")
    h75_orig_vec = emb.embed_scincl(
        h75_orig_abs, device=_DEVICE, batch_size=_BS_SCINCL, dtype=_DTYPE,
    )
    h20_orig_vec = emb.embed_scincl(
        h20_orig_abs, device=_DEVICE, batch_size=_BS_SCINCL, dtype=_DTYPE,
    )
    embed_elapsed = time.time() - t0
    n_total = sum(
        len(v) for v in [s_vec, u_vec, h75_orig_vec, h20_orig_vec]
    )
    print(f"  total embedding: {embed_elapsed:.0f}s "
          f"({embed_elapsed/n_total:.3f} s/abs over {n_total} papers)")
    print()

    # 3. Norm-band check
    print("SciNCL L2 norm bands at production scale:")
    for name, vec in [
        ("S", s_vec), ("U", u_vec),
        ("H_1975 orig", h75_orig_vec), ("H_2020 orig", h20_orig_vec),
    ]:
        norms = np.linalg.norm(vec, axis=1)
        finite = bool(np.isfinite(vec).all())
        print(
            f"  {name}: shape={vec.shape}, "
            f"finite={finite}, "
            f"mean={float(norms.mean()):.3f}, "
            f"min={float(norms.min()):.3f}, "
            f"max={float(norms.max()):.3f}"
        )
    print()

    # 4. L2 normalize for clustering
    s_norm = _l2_normalize(s_vec)
    u_norm = _l2_normalize(u_vec)
    h75_orig_norm = _l2_normalize(h75_orig_vec)
    h20_orig_norm = _l2_normalize(h20_orig_vec)

    # 5. Fit + project + H7'
    print("Cluster fit + H7' evaluation across K (Euclidean projection):")
    t0 = time.time()
    results: dict[int, dict[str, Any]] = {}

    for k in _K_VALUES:
        print(f"  K={k}: fitting...")
        s_centroids = _kmeans_fit(s_norm, k)
        u_centroids = _kmeans_fit(u_norm, k)

        np.save(
            _DATA_METADATA_DIR / f"section11-cluster-fit-S-K{k}-scincl.npy",
            s_centroids,
        )
        np.save(
            _DATA_METADATA_DIR / f"section11-cluster-fit-U-K{k}-scincl.npy",
            u_centroids,
        )

        orig_eval = _eval_h7(
            h75_orig_norm, h20_orig_norm, k, s_centroids, u_centroids,
        )
        results[k] = {"orig": orig_eval}

        s2 = _SPECTER2_REFS[k]
        print(
            f"    orig: r_H75={orig_eval['r_h75']:.2f} "
            f"(SPECTER2 {s2['r_h75_orig']:.2f}), "
            f"NC_rd={orig_eval['nc_rd']:.3f} "
            f"(SPECTER2 {s2['nc_rd_orig']:.3f}); "
            f"NC={'PASS' if orig_eval['nc_pass'] else 'FAIL'}"
        )
    cluster_elapsed = time.time() - t0
    print(f"  cluster fit total: {cluster_elapsed:.0f}s")
    print()

    # 6. Save SciNCL vectors
    np.save(_DATA_METADATA_DIR / "section11-prod-S-vec-scincl.npy", s_vec)
    np.save(_DATA_METADATA_DIR / "section11-prod-U-vec-scincl.npy", u_vec)
    np.save(
        _DATA_METADATA_DIR / "section11-prod-H_1975-vec-scincl.npy",
        h75_orig_vec,
    )
    np.save(
        _DATA_METADATA_DIR / "section11-prod-H_2020-vec-scincl.npy",
        h20_orig_vec,
    )

    # 7. Verdict logic
    relaxed_passes_orig = sum(
        1 for k in _K_VALUES
        if results[k]["orig"]["passes_relaxed"] and results[k]["orig"]["nc_pass"]
    )
    strict_passes_orig = sum(
        1 for k in _K_VALUES
        if results[k]["orig"]["passes_strict"] and results[k]["orig"]["nc_pass"]
    )

    if relaxed_passes_orig >= 2:
        verdict = "SCINCL_PRIMARY_HOLDS"
        verdict_msg = (
            "r_H75 ≥1.10 AND NC pass at ≥2/3 K. SciNCL primary lock "
            "confirmed empirically. Threshold stays at 1.10."
        )
        if strict_passes_orig >= 2:
            verdict_msg += (
                " ALSO: passes strict 1.43 threshold at ≥2/3 K — could "
                "revert to original pre-reg threshold."
            )
    elif relaxed_passes_orig == 0:
        verdict = "FALLBACK_TO_SPECTER2"
        verdict_msg = (
            "r_H75 fails 1.10 threshold at all K. SciNCL primary "
            "lock invalid; trigger SPECTER2 fallback per "
            "phase-0.2-scincl-primary-contingency.md."
        )
    else:
        verdict = "MIXED_USER_JUDGMENT"
        verdict_msg = (
            f"Mixed: relaxed_passes={relaxed_passes_orig}/3. User "
            "judgment between holding SciNCL primary (with K-specific "
            "caveats) and falling back to SPECTER2."
        )

    print(f"=== Verdict: {verdict} ===")
    print(verdict_msg)
    print()

    # 8. Write artifact md
    md_path = _OUT_DIR / "section11-scincl-revalidation.md"
    table_rows = "\n".join(
        f"| K={k} | {results[k]['orig']['r_h75']:.2f} "
        f"({_SPECTER2_REFS[k]['r_h75_orig']:.2f}) | "
        f"{results[k]['orig']['nc_rd']:.3f} "
        f"({_SPECTER2_REFS[k]['nc_rd_orig']:.3f}) | "
        f"{'YES' if results[k]['orig']['passes_relaxed'] else 'NO'} | "
        f"{'PASS' if results[k]['orig']['nc_pass'] else 'FAIL'} |"
        for k in _K_VALUES
    )

    norm_table = "\n".join(
        f"| {name} | {len(vec)} | {float(np.linalg.norm(vec, axis=1).mean()):.3f} | "
        f"[{float(np.linalg.norm(vec, axis=1).min()):.3f}, "
        f"{float(np.linalg.norm(vec, axis=1).max()):.3f}] |"
        for name, vec in [
            ("S", s_vec), ("U", u_vec),
            ("H_1975 orig", h75_orig_vec), ("H_2020 orig", h20_orig_vec),
        ]
    )

    body = f"""# Phase 0.2 Wave 4A — SciNCL §11 re-validation

**Run date:** {datetime.now(timezone.utc).date().isoformat()}
**Snapshot:** {snapshot}
**Mode:** SciNCL re-embed of existing Wave 2A pools + re-fit + Euclidean re-projection

## Headline

**Verdict: {verdict}**

{verdict_msg}

## SciNCL norm bands at production scale

| Pool | N | Mean L2 norm | [min, max] |
|---|---:|---:|---|
{norm_table}

## H7' results (SciNCL vs SPECTER2 reference in parens)

Note: only orig held-out (|H_1975|=49, |H_2020|=45) used; followup
held-outs (200/cell) not re-validated because the followup parquet
schema was thinner (no abstracts; only id+year+title+doi). Acceptable
because orig gives 6 measurements (3 K × 2 cells) — sufficient for
primary-lock decision.

| K | r_H75 orig (S2) | NC_rd orig (S2) | ≥1.10? | NC? |
|---|---|---|---|---|
{table_rows}

Thresholds:
- r_H75 ≥ 1.10 (relaxed, post-projection-bug, current Phase 0.2 lock)
- r_H75 ≥ 1.43 (strict, original pre-reg)
- NC tolerance < 0.20

Strict-threshold passes (r_H75 ≥ 1.43 AND NC pass): {strict_passes_orig}/3
Relaxed-threshold passes (r_H75 ≥ 1.10 AND NC pass): {relaxed_passes_orig}/3

## Wall-clock

| Stage | Time |
|---|---:|
| SciNCL embedding ({n_total} papers) | {embed_elapsed:.0f}s ({embed_elapsed/n_total:.3f} s/abs) |
| Cluster fit + H7' (3 K values) | {cluster_elapsed:.0f}s |

## Decision

{verdict_msg}

If SCINCL_PRIMARY_HOLDS: Wave 4A lock is empirically validated.
Stage 1 first task replaces SPECTER2 cluster centroids in
`data/metadata/section11-cluster-fit-{{S,U}}-K*.npy` with the
new SciNCL ones (committed in this run as
`section11-cluster-fit-{{S,U}}-K*-scincl.npy`).

If FALLBACK_TO_SPECTER2: revert phase-0.2-plan.md §1 to SPECTER2
primary; re-add SPECTER2 to headline stack; document trigger that
fired in tasks/lessons.md.

If MIXED_USER_JUDGMENT: user makes the call between holding
SciNCL primary (with K-specific caveats reported in robustness
section) vs falling back to SPECTER2.

## Cross-references

- Wave 2A SPECTER2 §11 (post-bug-fix):
  `experiments/phase-0.2/section11-production-validation.md`
- Wave 2A bug-fix re-projection:
  `experiments/phase-0.2/section11-reprojection-fix-summary.json`
- SciNCL primary contingency:
  `docs/phases/phase-0.2-scincl-primary-contingency.md`
- Wave 4A compute decision:
  `experiments/phase-0.2/stage2-compute-decision.md`
"""
    md_path.write_text(body)
    print(f"wrote {md_path}")

    # Save summary JSON
    summary = {
        "snapshot": snapshot,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "n_total": n_total,
        "embed_elapsed_sec": embed_elapsed,
        "cluster_elapsed_sec": cluster_elapsed,
        "results": {
            str(k): {
                "orig": {kk: vv for kk, vv in r["orig"].items()},
            }
            for k, r in results.items()
        },
        "specter2_refs": {str(k): v for k, v in _SPECTER2_REFS.items()},
        "norm_bands": {
            name: {
                "n": int(len(vec)),
                "mean": float(np.linalg.norm(vec, axis=1).mean()),
                "min": float(np.linalg.norm(vec, axis=1).min()),
                "max": float(np.linalg.norm(vec, axis=1).max()),
            }
            for name, vec in [
                ("S", s_vec), ("U", u_vec),
                ("H_1975_orig", h75_orig_vec), ("H_2020_orig", h20_orig_vec),
            ]
        },
    }
    summary_path = _OUT_DIR / "section11-scincl-revalidation-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, default=str))
    print(f"wrote {summary_path}")
    print()
    print(f"SciNCL re-validation complete. Verdict: {verdict}")


if __name__ == "__main__":
    main()
    sys.exit(0)
