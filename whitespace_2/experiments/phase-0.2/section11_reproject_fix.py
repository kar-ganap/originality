"""Phase 0.2 §11 — projection-bug fix + re-projection.

Wave 2A and its followup used `argmax(v · c)` for cluster
projection. KMeans assigns via `argmin(‖v - c‖²)`. For
unit-norm vectors with non-unit-norm centroids (KMeans
centroids are means of unit vectors, generally NOT unit norm),
these criteria differ:

- argmax(v · c) favors high-magnitude centroids
- argmin(‖v - c‖²) = argmax(2·v·c - ‖c‖²) is what KMeans used
  during fit

Phase 0.1 check5bd correctly used KMeans.predict() (Euclidean).
Both Phase 0.2 §11 scripts rolled their own argmax-cosine and
got it wrong. This script:

1. Loads existing S/U centroids at K∈{30, 50, 100}.
2. Loads existing H_1975 + H_2020 vectors (orig + followup).
3. Re-projects with the FIXED Euclidean assignment.
4. Recomputes effN + H7' for both buggy and fixed projections.
5. Reports the delta — does the bug change the conclusion?

Run from ws2 root:
    uv run python experiments/phase-0.2/section11_reproject_fix.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

_OUT_DIR = Path(__file__).parent
_DATA_METADATA_DIR = _OUT_DIR.parent.parent / "data" / "metadata"

_K_VALUES = (30, 50, 100)
_H7_ARTIFACT_RATIO = 1.43
_H7_NEGATIVE_CONTROL_TOL = 0.20


def _l2_normalize(vectors: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.where(norms > 0, norms, 1.0)
    return (vectors / norms).astype(np.float32)


def _project_argmax_cosine(
    vectors: np.ndarray[Any, Any], centroids: np.ndarray[Any, Any],
) -> np.ndarray[Any, Any]:
    """BUGGY: argmax(v · c). What both Phase 0.2 scripts used."""
    sims = vectors @ centroids.T
    return np.argmax(sims, axis=1)


def _project_euclidean(
    vectors: np.ndarray[Any, Any], centroids: np.ndarray[Any, Any],
) -> np.ndarray[Any, Any]:
    """FIXED: argmin(‖v - c‖²) = argmax(2·v·c - ‖c‖²). KMeans-consistent."""
    centroid_norms_sq = np.sum(centroids ** 2, axis=1)  # (k,)
    # Score = -dist² = 2·v·c - ‖c‖² (drops constant ‖v‖²)
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


def _evaluate(
    h75_norm: np.ndarray[Any, Any],
    h20_norm: np.ndarray[Any, Any],
    k: int,
    s_centroids: np.ndarray[Any, Any],
    u_centroids: np.ndarray[Any, Any],
    project_fn: Any,
) -> dict[str, Any]:
    h75_in_s = project_fn(h75_norm, s_centroids)
    h75_in_u = project_fn(h75_norm, u_centroids)
    h20_in_s = project_fn(h20_norm, s_centroids)
    h20_in_u = project_fn(h20_norm, u_centroids)
    eff_n_s_h75 = _eff_n(h75_in_s, k)
    eff_n_u_h75 = _eff_n(h75_in_u, k)
    eff_n_s_h20 = _eff_n(h20_in_s, k)
    eff_n_u_h20 = _eff_n(h20_in_u, k)
    artifact_ratio = (
        eff_n_s_h75 / eff_n_u_h75 if eff_n_u_h75 > 0 else float("inf")
    )
    ratio_h20 = (
        eff_n_s_h20 / eff_n_u_h20 if eff_n_u_h20 > 0 else float("inf")
    )
    nc_max = max(eff_n_s_h20, eff_n_u_h20)
    nc_rel_diff = (
        abs(eff_n_s_h20 - eff_n_u_h20) / nc_max if nc_max > 0 else 0.0
    )
    return {
        "eff_n_s_h75": eff_n_s_h75,
        "eff_n_u_h75": eff_n_u_h75,
        "eff_n_s_h20": eff_n_s_h20,
        "eff_n_u_h20": eff_n_u_h20,
        "artifact_ratio": artifact_ratio,
        "ratio_h20": ratio_h20,
        "nc_rel_diff": nc_rel_diff,
        "artifact_pass_orig": artifact_ratio > _H7_ARTIFACT_RATIO,
        "artifact_pass_inverted": artifact_ratio < (1.0 / _H7_ARTIFACT_RATIO),
        "nc_pass": nc_rel_diff < _H7_NEGATIVE_CONTROL_TOL,
        "sign_flip_present": artifact_ratio < 1.0 and ratio_h20 > 1.0,
    }


def _print_compare(label: str, buggy: dict[str, Any], fixed: dict[str, Any]) -> None:
    print(f"  {label}:")
    print(
        f"    buggy: r_H75={buggy['artifact_ratio']:.2f}, "
        f"r_H20={buggy['ratio_h20']:.2f}, "
        f"NC_rd={buggy['nc_rel_diff']:.3f}, "
        f"NC={'PASS' if buggy['nc_pass'] else 'FAIL'}, "
        f"sign_flip={'YES' if buggy['sign_flip_present'] else 'NO'}"
    )
    print(
        f"    FIXED: r_H75={fixed['artifact_ratio']:.2f}, "
        f"r_H20={fixed['ratio_h20']:.2f}, "
        f"NC_rd={fixed['nc_rel_diff']:.3f}, "
        f"NC={'PASS' if fixed['nc_pass'] else 'FAIL'}, "
        f"sign_flip={'YES' if fixed['sign_flip_present'] else 'NO'}"
    )


def main() -> None:
    print("§11 projection-bug fix + re-projection")
    print()

    snapshot = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # Load existing vectors + centroids
    print("Loading existing vectors + centroids...")
    h75_orig_vec = np.load(_DATA_METADATA_DIR / "section11-prod-H_1975-vec.npy")
    h20_orig_vec = np.load(_DATA_METADATA_DIR / "section11-prod-H_2020-vec.npy")
    h75_fu_vec = np.load(
        _DATA_METADATA_DIR / "section11-prod-H_1975-vec-followup.npy"
    )
    h20_fu_vec = np.load(
        _DATA_METADATA_DIR / "section11-prod-H_2020-vec-followup.npy"
    )

    h75_orig_norm = _l2_normalize(h75_orig_vec)
    h20_orig_norm = _l2_normalize(h20_orig_vec)
    h75_fu_norm = _l2_normalize(h75_fu_vec)
    h20_fu_norm = _l2_normalize(h20_fu_vec)
    print(
        f"  H_1975 orig: {h75_orig_vec.shape}; followup: {h75_fu_vec.shape}"
    )
    print(
        f"  H_2020 orig: {h20_orig_vec.shape}; followup: {h20_fu_vec.shape}"
    )
    print()

    # Centroid norm stats (sanity-check the bug)
    print("Centroid L2 norm stats (centroids are means of unit vectors;")
    print("if all close to 1.0 the bug barely matters; if spread, it matters):")
    for k in _K_VALUES:
        s_c = np.load(_DATA_METADATA_DIR / f"section11-cluster-fit-S-K{k}.npy")
        u_c = np.load(_DATA_METADATA_DIR / f"section11-cluster-fit-U-K{k}.npy")
        s_norms = np.linalg.norm(s_c, axis=1)
        u_norms = np.linalg.norm(u_c, axis=1)
        print(
            f"  K={k}: S-centroid norms p50={float(np.median(s_norms)):.3f} "
            f"[min={float(s_norms.min()):.3f}, max={float(s_norms.max()):.3f}]; "
            f"U p50={float(np.median(u_norms)):.3f} "
            f"[{float(u_norms.min()):.3f}, {float(u_norms.max()):.3f}]"
        )
    print()

    # Re-evaluate at each K
    all_results: dict[str, dict[int, dict[str, Any]]] = {
        "orig_buggy": {},
        "orig_fixed": {},
        "fu_buggy": {},
        "fu_fixed": {},
    }
    print("Comparing buggy vs FIXED projections...")
    for k in _K_VALUES:
        s_c = np.load(_DATA_METADATA_DIR / f"section11-cluster-fit-S-K{k}.npy")
        u_c = np.load(_DATA_METADATA_DIR / f"section11-cluster-fit-U-K{k}.npy")

        orig_buggy = _evaluate(
            h75_orig_norm, h20_orig_norm, k, s_c, u_c, _project_argmax_cosine,
        )
        orig_fixed = _evaluate(
            h75_orig_norm, h20_orig_norm, k, s_c, u_c, _project_euclidean,
        )
        fu_buggy = _evaluate(
            h75_fu_norm, h20_fu_norm, k, s_c, u_c, _project_argmax_cosine,
        )
        fu_fixed = _evaluate(
            h75_fu_norm, h20_fu_norm, k, s_c, u_c, _project_euclidean,
        )
        all_results["orig_buggy"][k] = orig_buggy
        all_results["orig_fixed"][k] = orig_fixed
        all_results["fu_buggy"][k] = fu_buggy
        all_results["fu_fixed"][k] = fu_fixed

        print(f"K={k}:")
        _print_compare(f"orig (|H_1975|={len(h75_orig_norm)})",
                       orig_buggy, orig_fixed)
        _print_compare(f"followup (|H_1975|={len(h75_fu_norm)})",
                       fu_buggy, fu_fixed)
        print()

    # Final verdict (using FIXED projections)
    fixed_orig = all_results["orig_fixed"]
    fixed_fu = all_results["fu_fixed"]

    # Path A criteria: sign-flip stable + NC pass
    sign_flip_orig = sum(1 for k in _K_VALUES if fixed_orig[k]["sign_flip_present"])
    sign_flip_fu = sum(1 for k in _K_VALUES if fixed_fu[k]["sign_flip_present"])
    nc_pass_orig = sum(1 for k in _K_VALUES if fixed_orig[k]["nc_pass"])
    nc_pass_fu = sum(1 for k in _K_VALUES if fixed_fu[k]["nc_pass"])

    # Path original (S>U) criteria
    h7_orig_pass_orig = sum(
        1 for k in _K_VALUES
        if fixed_orig[k]["artifact_pass_orig"] and fixed_orig[k]["nc_pass"]
    )
    h7_orig_pass_fu = sum(
        1 for k in _K_VALUES
        if fixed_fu[k]["artifact_pass_orig"] and fixed_fu[k]["nc_pass"]
    )

    print("=== Verdict (using FIXED Euclidean projection) ===")
    print()
    print(f"Original ({len(h75_orig_norm)}/{len(h20_orig_norm)} held-outs):")
    print(f"  Path-A sign-flip across K: {sign_flip_orig}/3 (need ≥2)")
    print(f"  NC passes: {nc_pass_orig}/3")
    print(f"  Original H7' (S>U direction) passes: {h7_orig_pass_orig}/3")
    print()
    print(f"Followup ({len(h75_fu_norm)}/{len(h20_fu_norm)} held-outs):")
    print(f"  Path-A sign-flip across K: {sign_flip_fu}/3 (need ≥2)")
    print(f"  NC passes: {nc_pass_fu}/3")
    print(f"  Original H7' (S>U direction) passes: {h7_orig_pass_fu}/3")
    print()

    # Save fixed results JSON
    summary = {
        "snapshot": snapshot,
        "fix_description": (
            "argmax(v·c) → argmax(2·v·c − ‖c‖²) [KMeans-Euclidean-consistent]"
        ),
        "results": {
            label: {
                str(k): {kk: vv for kk, vv in r.items()}
                for k, r in d.items()
            }
            for label, d in all_results.items()
        },
        "n_h75_orig": int(h75_orig_norm.shape[0]),
        "n_h20_orig": int(h20_orig_norm.shape[0]),
        "n_h75_fu": int(h75_fu_norm.shape[0]),
        "n_h20_fu": int(h20_fu_norm.shape[0]),
    }
    out_json = _OUT_DIR / "section11-reprojection-fix-summary.json"
    out_json.write_text(json.dumps(summary, indent=2, default=str))
    print(f"wrote {out_json}")


if __name__ == "__main__":
    main()
    sys.exit(0)
