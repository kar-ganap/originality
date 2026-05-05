"""Phase 0.2 Wave 2A — §11 production-scale re-validation.

Re-runs the §11 cluster-fit stratification artifact (Check 5d) at
~3-5× pilot scale, validating that the H7' production-scale gate
holds (i.e., decade-stratified cluster fit produces an effN
artifact pre-1990 that's absent on the 2020 negative control).

Scale changes vs Check 5d:
- Stratified pool S: 250/decade × 6 decades = 1500 (vs 80×6=480)
- Unstratified pool U: 1500 (vs 600)
- Held-out H_1975, H_2020: 50 each (vs 30)
- Per-decade supplemental seed pulls: more aggressive on early
  decades (Check 5d lesson — |S|=316 underrun in pilot).

Key implementation upgrades vs check5bd:
- Word-boundary regex matching for junk-year tokens (Wave 1C fix:
  `\bTOKEN\b` not `tok in text` — caught `gan`/`bert`/`iot`/`gpt`
  substring false positives).
- Per-decade adaptive seed allocation: more seeds for early decades
  (low retention) vs late decades (high retention).

Pre-registered hypotheses:

  Layer A (pipeline correctness):
  - H1 (pulls): |S|≥1400, |U|≥1400, |H_1975|≥45, |H_2020|≥45,
    pairwise disjoint.
  - H2 (embedding): SPECTER2 produces (N, 768) finite, L2-norm in
    [21.0, 23.0] mean band.
  - H3 (KMeans determinism): reproducible from random_state=46.

  Layer B (scientific findings):
  - H7' (production): effN_S(H_1975) > 1.43 × effN_U(H_1975)
    (artifact present pre-1990) AND |effN_S(H_2020) - effN_U(H_2020)|
    / max(...) < 0.20 (artifact absent on negative control).

Acceptance:
- H7' passes at K=50 primary → §11 production-scale validated;
  proceed to Stage 1.
- H7' passes at K=30 OR K=100 only → robustness sweep flag;
  proceed but document.
- H7' fails at all K → BLOCK Stage 1 transition; re-plan.

Run from ws2 root:
    uv run python experiments/phase-0.2/section11_production_validation.py [--smoke]
"""

from __future__ import annotations

import argparse
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
from sklearn.cluster import KMeans
from tqdm import tqdm

from whitespace2 import embeddings as emb
from whitespace2 import openalex

# ---------- paths ----------

_OUT_DIR = Path(__file__).parent
_DATA_METADATA_DIR = _OUT_DIR.parent.parent / "data" / "metadata"

# ---------- §0 locked production spec (with Wave 1C regex fix) ----------

_FIELD = "cs"
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
    "cited_by_count", "referenced_works", "primary_location", "ids",
]

# ---------- production-scale targets ----------

_DECADES: tuple[tuple[int, int], ...] = (
    (1970, 1980),
    (1980, 1990),
    (1990, 2000),
    (2000, 2010),
    (2010, 2020),
    (2020, 2025),
)

# Production targets (per Wave 2A execution plan)
_FULL_PER_DECADE_TARGET = 250
_FULL_UNSTRAT_TARGET = 1500
_FULL_HELDOUT_TARGET = 50

# Per-decade adaptive seed allocation (Check 5d lesson:
# early decades have lower retention → need more seeds).
_DECADE_BASE_SEEDS: dict[int, list[int]] = {
    1970: list(range(50, 75)),    # 25 seeds (target 250 at ~10% retention)
    1980: list(range(75, 95)),    # 20 seeds (target 250 at ~15% retention)
    1990: list(range(95, 110)),   # 15 seeds (target 250 at ~25% retention)
    2000: list(range(110, 122)),  # 12 seeds (target 250 at ~35% retention)
    2010: list(range(122, 132)),  # 10 seeds (target 250 at ~45% retention)
    2020: list(range(132, 142)),  # 10 seeds (target 250 at ~50% retention)
}
_UNSTRAT_SEEDS = list(range(60, 90))  # 30 seeds for 1500 unstrat target
_HELDOUT_1975_SEEDS = list(range(70, 80))  # 10 seeds for 50 cs 1975 held-out
_HELDOUT_2020_SEEDS = list(range(71, 75))  # 4 seeds for 50 cs 2020 held-out

_SAMPLE_PER_CELL = 200  # OpenAlex cap

# Smoke-mode (sanity check before full run)
_SMOKE_PER_DECADE_TARGET = 25
_SMOKE_UNSTRAT_TARGET = 150
_SMOKE_HELDOUT_TARGET = 15
_SMOKE_DECADE_SEEDS: dict[int, list[int]] = {
    1970: list(range(50, 56)),
    1980: list(range(75, 81)),
    1990: list(range(95, 99)),
    2000: list(range(110, 114)),
    2010: list(range(122, 126)),
    2020: list(range(132, 136)),
}
_SMOKE_UNSTRAT_SEEDS = list(range(60, 68))
_SMOKE_HELDOUT_1975_SEEDS = list(range(70, 73))
_SMOKE_HELDOUT_2020_SEEDS = list(range(71, 73))

# Cluster-fit parameters (per §11)
_K_PRIMARY = 50
_K_ROBUSTNESS: tuple[int, ...] = (30, 100)
_SMOKE_K_PRIMARY = 25
_SMOKE_K_ROBUSTNESS: tuple[int, ...] = (15, 35)
_KMEANS_RANDOM_STATE = 46
_KMEANS_N_INIT = 20
_KMEANS_MAX_ITER = 300

# H7' thresholds (§11 production-scale gate)
_H7_ARTIFACT_RATIO = 1.43
_H7_NEGATIVE_CONTROL_TOL = 0.20

# Embedding device
_DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
_DTYPE = "fp16"
_BS_SPECTER = 8
_NORM_BAND_SPECTER = (21.0, 23.0)


# ---------- post-fetch filters (regex word-boundary; Wave 1C fix) ----------


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
    after_empty = [w for w in after_junk if _passes_empty_abstract_filter(w)]
    return after_empty


# ---------- pulls ----------


def _pull_one(
    filters: dict[str, str], seed: int, label: str,
) -> list[dict[str, Any]]:
    try:
        raw = openalex.fetch_works(
            filters=filters,
            sample_size=_SAMPLE_PER_CELL,
            seed=seed,
            select=_SELECT,
        )
    except RuntimeError as err:
        print(f"  WARN: {label} seed={seed}: {err}")
        return []
    return _post_filter(raw)


def _pull_decade(
    decade_lo: int, decade_hi: int, seeds: list[int], target: int,
) -> list[dict[str, Any]]:
    """Multi-seed pull for one decade until target unique post-filter."""
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    pbar = tqdm(seeds, desc=f"strat {decade_lo}s")
    for seed in pbar:
        if len(out) >= target:
            break
        kept = _pull_one(
            filters={
                "concepts.id": _FIELD_CONCEPT_ID,
                "publication_year": f"{decade_lo}-{decade_hi - 1}",
            },
            seed=seed,
            label=f"strat_{decade_lo}s",
        )
        for w in kept:
            wid = str(w.get("id", ""))
            if wid and wid not in seen:
                seen.add(wid)
                w["_pull_decade"] = decade_lo
                out.append(w)
        pbar.set_postfix({"|S_d|": len(out)})
        time.sleep(0.3)
    if len(out) < target:
        print(
            f"  NOTE: decade {decade_lo}s underran target ({len(out)} < "
            f"{target}); will continue with what we have"
        )
    return out[:target]  # cap at target


def _pull_unstratified(seeds: list[int], target: int) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    pbar = tqdm(seeds, desc="unstrat")
    for seed in pbar:
        if len(out) >= target:
            break
        kept = _pull_one(
            filters={
                "concepts.id": _FIELD_CONCEPT_ID,
                "publication_year": "1970-2024",
            },
            seed=seed,
            label="unstrat",
        )
        for w in kept:
            wid = str(w.get("id", ""))
            if wid and wid not in seen:
                seen.add(wid)
                out.append(w)
        pbar.set_postfix({"|U|": len(out)})
        time.sleep(0.3)
    return out[:target]


def _pull_heldout(
    year: int, seeds: list[int], target: int,
) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    pbar = tqdm(seeds, desc=f"heldout cs/{year}")
    for seed in pbar:
        if len(out) >= target:
            break
        kept = _pull_one(
            filters={
                "concepts.id": _FIELD_CONCEPT_ID,
                "publication_year": str(year),
            },
            seed=seed,
            label=f"heldout_{year}",
        )
        for w in kept:
            wid = str(w.get("id", ""))
            if wid and wid not in seen:
                seen.add(wid)
                out.append(w)
        pbar.set_postfix({f"|H_{year}|": len(out)})
        time.sleep(0.3)
    return out[:target]


def _enforce_disjoint(
    s: list[dict[str, Any]],
    u: list[dict[str, Any]],
    h75: list[dict[str, Any]],
    h20: list[dict[str, Any]],
) -> tuple[
    list[dict[str, Any]], list[dict[str, Any]],
    list[dict[str, Any]], list[dict[str, Any]],
]:
    s_ids = {str(w.get("id", "")) for w in s}
    u_ids = {str(w.get("id", "")) for w in u}
    u = [w for w in u if str(w.get("id", "")) not in s_ids]
    u_ids = {str(w.get("id", "")) for w in u}
    h75 = [
        w for w in h75
        if str(w.get("id", "")) not in s_ids
        and str(w.get("id", "")) not in u_ids
    ]
    h75_ids = {str(w.get("id", "")) for w in h75}
    h20 = [
        w for w in h20
        if str(w.get("id", "")) not in s_ids
        and str(w.get("id", "")) not in u_ids
        and str(w.get("id", "")) not in h75_ids
    ]
    return s, u, h75, h20


# ---------- abstract reconstruction ----------


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
    return [_reconstruct(w.get("abstract_inverted_index") or {}) for w in works]


# ---------- L2 normalize ----------


def _l2_normalize(vectors: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.where(norms > 0, norms, 1.0)
    return (vectors / norms).astype(np.float32)


# ---------- effN computation ----------


def _kmeans_fit(
    vectors: np.ndarray[Any, Any], k: int,
) -> tuple[np.ndarray[Any, Any], np.ndarray[Any, Any]]:
    """Returns (centroids, labels)."""
    km = KMeans(
        n_clusters=k,
        random_state=_KMEANS_RANDOM_STATE,
        n_init=_KMEANS_N_INIT,
        max_iter=_KMEANS_MAX_ITER,
    )
    labels = km.fit_predict(vectors)
    return km.cluster_centers_, labels


def _project_to_clusters(
    vectors: np.ndarray[Any, Any], centroids: np.ndarray[Any, Any],
) -> np.ndarray[Any, Any]:
    """Hard-assign each vector to nearest centroid via Euclidean distance,
    consistent with KMeans's internal assignment criterion.

    For unit-norm vectors with non-unit-norm centroids (KMeans centroids
    are means of unit vectors and have norms ~0.92-0.94 in practice),
    `argmax(v · c)` is NOT consistent with KMeans's `argmin(‖v - c‖²)`.
    The naive cosine-style argmax favors high-magnitude centroids and
    materially mis-assigns; this implementation is corrected per
    `experiments/phase-0.2/section11_reproject_fix.py` discovery.

    Equivalent to `argmin(‖v - c‖²)` since for fixed v,
    `‖v - c‖² = ‖v‖² + ‖c‖² - 2·v·c`, and `‖v‖²` is constant per row →
    `argmin(‖c‖² - 2·v·c)` = `argmax(2·v·c - ‖c‖²)`.
    """
    centroid_norms_sq = np.sum(centroids ** 2, axis=1)
    scores = 2 * (vectors @ centroids.T) - centroid_norms_sq[None, :]
    return np.argmax(scores, axis=1)


def _eff_n(assignments: np.ndarray[Any, Any], k: int) -> float:
    """Effective number of clusters via exp(Shannon entropy)."""
    counts = np.bincount(assignments, minlength=k)
    n_total = int(counts.sum())
    if n_total == 0:
        return 0.0
    p = counts / n_total
    p_pos = p[p > 0]
    h = -float((p_pos * np.log(p_pos)).sum())
    return float(np.exp(h))


# ---------- H7' evaluation ----------


def _evaluate_h7_prime(
    eff_n_s_h75: float,
    eff_n_u_h75: float,
    eff_n_s_h20: float,
    eff_n_u_h20: float,
) -> dict[str, Any]:
    artifact_ratio = (
        eff_n_s_h75 / eff_n_u_h75 if eff_n_u_h75 > 0 else float("inf")
    )
    artifact_pass = artifact_ratio > _H7_ARTIFACT_RATIO

    nc_max = max(eff_n_s_h20, eff_n_u_h20)
    nc_rel_diff = (
        abs(eff_n_s_h20 - eff_n_u_h20) / nc_max if nc_max > 0 else float("inf")
    )
    nc_pass = nc_rel_diff < _H7_NEGATIVE_CONTROL_TOL

    overall_pass = artifact_pass and nc_pass
    return {
        "eff_n_s_h75": eff_n_s_h75,
        "eff_n_u_h75": eff_n_u_h75,
        "eff_n_s_h20": eff_n_s_h20,
        "eff_n_u_h20": eff_n_u_h20,
        "artifact_ratio": artifact_ratio,
        "artifact_threshold": _H7_ARTIFACT_RATIO,
        "artifact_pass": artifact_pass,
        "nc_rel_diff": nc_rel_diff,
        "nc_threshold": _H7_NEGATIVE_CONTROL_TOL,
        "nc_pass": nc_pass,
        "overall_pass": overall_pass,
    }


# ---------- artifact dataframe ----------


def _flatten(work: dict[str, Any], set_label: str) -> dict[str, Any]:
    return {
        "work_id": work.get("id"),
        "title": work.get("title") or "",
        "publication_year": work.get("publication_year"),
        "type": work.get("type"),
        "field": _FIELD,
        "set_label": set_label,
        "pull_decade": work.get("_pull_decade"),
        "has_abstract": openalex.has_abstract(work),
        "field_tag_score": _field_concept_score(work),
        "cited_by_count": work.get("cited_by_count", 0),
        "n_concepts": len(work.get("concepts") or []),
        "first_country": openalex.extract_first_country(work),
        "doi": openalex.extract_doi(work),
        "abstract_inverted_index_json": json.dumps(
            work.get("abstract_inverted_index") or {}
        ),
        "concepts_json": json.dumps(work.get("concepts") or []),
    }


def _to_df(works: list[dict[str, Any]], set_label: str) -> pd.DataFrame:
    return pd.DataFrame([_flatten(w, set_label) for w in works])


# ---------- main ----------


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--smoke", action="store_true",
        help="Run with smaller targets for quick sanity check.",
    )
    args = parser.parse_args()
    smoke = args.smoke

    print(
        f"Phase 0.2 Wave 2A — §11 production-scale validation "
        f"({'SMOKE' if smoke else 'FULL'})"
    )
    print(f"  device: {_DEVICE}; dtype: {_DTYPE}")
    print()

    snapshot = datetime.now(timezone.utc).isoformat(timespec="seconds")
    suffix = "-smoke" if smoke else ""

    # Targets
    if smoke:
        per_decade = _SMOKE_PER_DECADE_TARGET
        unstrat_target = _SMOKE_UNSTRAT_TARGET
        heldout_target = _SMOKE_HELDOUT_TARGET
        decade_seeds = _SMOKE_DECADE_SEEDS
        unstrat_seeds = _SMOKE_UNSTRAT_SEEDS
        h75_seeds = _SMOKE_HELDOUT_1975_SEEDS
        h20_seeds = _SMOKE_HELDOUT_2020_SEEDS
        k_primary = _SMOKE_K_PRIMARY
        k_robustness = _SMOKE_K_ROBUSTNESS
    else:
        per_decade = _FULL_PER_DECADE_TARGET
        unstrat_target = _FULL_UNSTRAT_TARGET
        heldout_target = _FULL_HELDOUT_TARGET
        decade_seeds = _DECADE_BASE_SEEDS
        unstrat_seeds = _UNSTRAT_SEEDS
        h75_seeds = _HELDOUT_1975_SEEDS
        h20_seeds = _HELDOUT_2020_SEEDS
        k_primary = _K_PRIMARY
        k_robustness = _K_ROBUSTNESS

    # ===== Pulls =====
    print(f"=== Pulls (target |S|={per_decade * 6}, |U|={unstrat_target}, "
          f"|H_*|={heldout_target}) ===")
    t_pull_start = time.time()

    s_works: list[dict[str, Any]] = []
    for (lo, hi) in _DECADES:
        seeds = decade_seeds.get(lo, [])
        decade_works = _pull_decade(lo, hi, seeds, per_decade)
        s_works.extend(decade_works)
    print(f"|S| (post-decade-pull): {len(s_works)}")

    u_works = _pull_unstratified(unstrat_seeds, unstrat_target)
    print(f"|U|: {len(u_works)}")

    h75_works = _pull_heldout(1975, h75_seeds, heldout_target)
    print(f"|H_1975|: {len(h75_works)}")

    h20_works = _pull_heldout(2020, h20_seeds, heldout_target)
    print(f"|H_2020|: {len(h20_works)}")

    s_works, u_works, h75_works, h20_works = _enforce_disjoint(
        s_works, u_works, h75_works, h20_works,
    )
    print(
        f"After disjoint: |S|={len(s_works)}, |U|={len(u_works)}, "
        f"|H_1975|={len(h75_works)}, |H_2020|={len(h20_works)}"
    )
    pull_elapsed = time.time() - t_pull_start
    print(f"  pull total: {pull_elapsed:.0f}s")
    print()

    # ===== H1 (pull correctness) =====
    if smoke:
        # Smaller thresholds for smoke
        h1_s_min = max(per_decade * 4, 100)
        h1_u_min = max(int(unstrat_target * 0.7), 100)
        h1_h_min = max(int(heldout_target * 0.7), 5)
    else:
        h1_s_min = 1400
        h1_u_min = 1400
        h1_h_min = 45

    h1_pass = (
        len(s_works) >= h1_s_min
        and len(u_works) >= h1_u_min
        and len(h75_works) >= h1_h_min
        and len(h20_works) >= h1_h_min
    )
    print(f"H1 pull correctness: {'PASS' if h1_pass else 'FAIL'} "
          f"(|S|={len(s_works)}≥{h1_s_min}, |U|={len(u_works)}≥{h1_u_min}, "
          f"|H_*|≥{h1_h_min})")
    print()

    # ===== Embed =====
    print("=== SPECTER2 embedding ===")
    t_emb_start = time.time()

    s_abs = _decode_abstracts(s_works)
    u_abs = _decode_abstracts(u_works)
    h75_abs = _decode_abstracts(h75_works)
    h20_abs = _decode_abstracts(h20_works)

    print(f"Embedding |S|={len(s_abs)}...")
    s_vec = emb.embed_specter2(
        s_abs, device=_DEVICE, batch_size=_BS_SPECTER, dtype=_DTYPE,
    )
    print(f"Embedding |U|={len(u_abs)}...")
    u_vec = emb.embed_specter2(
        u_abs, device=_DEVICE, batch_size=_BS_SPECTER, dtype=_DTYPE,
    )
    print(f"Embedding |H_1975|={len(h75_abs)}...")
    h75_vec = emb.embed_specter2(
        h75_abs, device=_DEVICE, batch_size=_BS_SPECTER, dtype=_DTYPE,
    )
    print(f"Embedding |H_2020|={len(h20_abs)}...")
    h20_vec = emb.embed_specter2(
        h20_abs, device=_DEVICE, batch_size=_BS_SPECTER, dtype=_DTYPE,
    )
    emb_elapsed = time.time() - t_emb_start
    print(f"  embedding total: {emb_elapsed:.0f}s "
          f"({emb_elapsed/(len(s_abs)+len(u_abs)+len(h75_abs)+len(h20_abs)):.3f} s/abs)")

    # H2 (embedding correctness)
    h2_pass = True
    for name, v, n in [
        ("S", s_vec, len(s_abs)),
        ("U", u_vec, len(u_abs)),
        ("H_1975", h75_vec, len(h75_abs)),
        ("H_2020", h20_vec, len(h20_abs)),
    ]:
        ok_shape = v.shape == (n, 768)
        ok_finite = bool(np.isfinite(v).all())
        norms = np.linalg.norm(v, axis=1)
        mean_norm = float(norms.mean())
        ok_norm = _NORM_BAND_SPECTER[0] <= mean_norm <= _NORM_BAND_SPECTER[1]
        if not (ok_shape and ok_finite):
            h2_pass = False
        print(
            f"  H2 [{name}]: shape={v.shape}, finite={ok_finite}, "
            f"norm={mean_norm:.2f} {'in-band' if ok_norm else 'OUT-OF-BAND'}"
        )
    print(f"H2 embedding correctness: {'PASS' if h2_pass else 'FAIL'}")
    print()

    # ===== L2 normalize for cluster fit =====
    s_norm = _l2_normalize(s_vec)
    u_norm = _l2_normalize(u_vec)
    h75_norm = _l2_normalize(h75_vec)
    h20_norm = _l2_normalize(h20_vec)

    # ===== Cluster fit + H7' across K =====
    print("=== Cluster fit + H7' evaluation ===")
    t_clust_start = time.time()

    h7_results: dict[int, dict[str, Any]] = {}
    manifest_paths: dict[int, dict[str, str]] = {}

    for k in [k_primary, *k_robustness]:
        print(f"  K={k}: fitting on |S|={len(s_norm)} and |U|={len(u_norm)}...")
        s_centroids, _ = _kmeans_fit(s_norm, k)
        u_centroids, _ = _kmeans_fit(u_norm, k)

        # Project held-outs to each fit
        h75_in_s = _project_to_clusters(h75_norm, s_centroids)
        h75_in_u = _project_to_clusters(h75_norm, u_centroids)
        h20_in_s = _project_to_clusters(h20_norm, s_centroids)
        h20_in_u = _project_to_clusters(h20_norm, u_centroids)

        eff_n_s_h75 = _eff_n(h75_in_s, k)
        eff_n_u_h75 = _eff_n(h75_in_u, k)
        eff_n_s_h20 = _eff_n(h20_in_s, k)
        eff_n_u_h20 = _eff_n(h20_in_u, k)

        h7 = _evaluate_h7_prime(
            eff_n_s_h75, eff_n_u_h75, eff_n_s_h20, eff_n_u_h20,
        )
        h7_results[k] = h7

        # Save manifest (centroids + assignments)
        s_manifest = _DATA_METADATA_DIR / f"section11-cluster-fit-S-K{k}{suffix}.npy"
        u_manifest = _DATA_METADATA_DIR / f"section11-cluster-fit-U-K{k}{suffix}.npy"
        np.save(s_manifest, s_centroids)
        np.save(u_manifest, u_centroids)
        manifest_paths[k] = {"s": str(s_manifest), "u": str(u_manifest)}

        print(
            f"    eff_n: S/H75={eff_n_s_h75:.2f}, U/H75={eff_n_u_h75:.2f}, "
            f"ratio={h7['artifact_ratio']:.2f} (>{_H7_ARTIFACT_RATIO}? "
            f"{'YES' if h7['artifact_pass'] else 'NO'})"
        )
        print(
            f"    NC: S/H20={eff_n_s_h20:.2f}, U/H20={eff_n_u_h20:.2f}, "
            f"rel_diff={h7['nc_rel_diff']:.3f} (<{_H7_NEGATIVE_CONTROL_TOL}? "
            f"{'YES' if h7['nc_pass'] else 'NO'})"
        )
        print(
            f"    overall: {'PASS' if h7['overall_pass'] else 'FAIL'}"
        )

    clust_elapsed = time.time() - t_clust_start
    print(f"  cluster fit total: {clust_elapsed:.0f}s")
    print()

    # ===== Summary + acceptance =====
    primary_pass = h7_results[k_primary]["overall_pass"]
    robustness_passes = [
        h7_results[k]["overall_pass"] for k in k_robustness
    ]
    any_robustness = any(robustness_passes)

    if primary_pass:
        gate = "PASS_PRIMARY"
        gate_msg = (
            f"H7' passed at K={k_primary} primary; §11 production-scale "
            "validated. Proceed to Stage 1."
        )
    elif any_robustness:
        gate = "PASS_ROBUSTNESS"
        passing_ks = [k for k, p in zip(k_robustness, robustness_passes) if p]
        gate_msg = (
            f"H7' passed at K∈{passing_ks} only (not primary K={k_primary}); "
            "robustness sweep flag. Proceed to Stage 1 with documented caveat."
        )
    else:
        gate = "FAIL"
        gate_msg = (
            f"H7' FAILED at all K∈{[k_primary, *k_robustness]}. BLOCK Stage 1 "
            "transition; trigger plan revision."
        )

    print(f"=== Wave 2A gate: {gate} ===")
    print(gate_msg)
    print()

    # ===== Persist parquet + manifest =====
    print("=== Persist artifacts ===")
    s_df = _to_df(s_works, "S")
    u_df = _to_df(u_works, "U")
    h75_df = _to_df(h75_works, "H_1975")
    h20_df = _to_df(h20_works, "H_2020")

    s_df.to_parquet(
        _DATA_METADATA_DIR / f"section11-prod-S{suffix}.parquet", index=False,
    )
    u_df.to_parquet(
        _DATA_METADATA_DIR / f"section11-prod-U{suffix}.parquet", index=False,
    )
    h75_df.to_parquet(
        _DATA_METADATA_DIR / f"section11-prod-H_1975{suffix}.parquet", index=False,
    )
    h20_df.to_parquet(
        _DATA_METADATA_DIR / f"section11-prod-H_2020{suffix}.parquet", index=False,
    )
    print(f"  wrote 4 parquets to {_DATA_METADATA_DIR}/section11-prod-*{suffix}.parquet")

    # Save vectors
    np.save(_DATA_METADATA_DIR / f"section11-prod-S-vec{suffix}.npy", s_vec)
    np.save(_DATA_METADATA_DIR / f"section11-prod-U-vec{suffix}.npy", u_vec)
    np.save(_DATA_METADATA_DIR / f"section11-prod-H_1975-vec{suffix}.npy", h75_vec)
    np.save(_DATA_METADATA_DIR / f"section11-prod-H_2020-vec{suffix}.npy", h20_vec)

    # ===== Write artifact md =====
    md_path = _OUT_DIR / f"section11-production-validation{suffix}.md"

    h7_table = "\n".join(
        f"| K={k} | {h7_results[k]['eff_n_s_h75']:.2f} | "
        f"{h7_results[k]['eff_n_u_h75']:.2f} | "
        f"{h7_results[k]['artifact_ratio']:.2f} | "
        f"{'YES' if h7_results[k]['artifact_pass'] else 'NO'} | "
        f"{h7_results[k]['eff_n_s_h20']:.2f} | "
        f"{h7_results[k]['eff_n_u_h20']:.2f} | "
        f"{h7_results[k]['nc_rel_diff']:.3f} | "
        f"{'YES' if h7_results[k]['nc_pass'] else 'NO'} | "
        f"**{'PASS' if h7_results[k]['overall_pass'] else 'FAIL'}** |"
        for k in [k_primary, *k_robustness]
    )

    body = f"""# Phase 0.2 Wave 2A — §11 production-scale re-validation

**Run date:** {datetime.now(timezone.utc).date().isoformat()}
**Snapshot:** {snapshot}
**Mode:** {'SMOKE' if smoke else 'FULL'}
**Device:** {_DEVICE}; **dtype:** {_DTYPE}

## Headline

**Wave 2A gate: {gate}**

{gate_msg}

## Pull summary

| Set | Target | Actual | Notes |
|---|---:|---:|---|
| Stratified pool S | {per_decade * 6} | {len(s_works)} | per-decade × 6 |
| Unstratified pool U | {unstrat_target} | {len(u_works)} | Nᵧ-proportional 1970-2024 |
| Held-out H_1975 | {heldout_target} | {len(h75_works)} | cs 1975 only |
| Held-out H_2020 | {heldout_target} | {len(h20_works)} | cs 2020 only |

Pairwise disjoint; all |X|≥H1 thresholds: {'PASS' if h1_pass else 'FAIL'}.

Pull wall-clock: {pull_elapsed:.0f}s.

## Embedding summary

| Set | N | Mean L2 norm |
|---|---:|---:|
| S | {len(s_abs)} | {float(np.linalg.norm(s_vec, axis=1).mean()):.2f} |
| U | {len(u_abs)} | {float(np.linalg.norm(u_vec, axis=1).mean()):.2f} |
| H_1975 | {len(h75_abs)} | {float(np.linalg.norm(h75_vec, axis=1).mean()):.2f} |
| H_2020 | {len(h20_abs)} | {float(np.linalg.norm(h20_vec, axis=1).mean()):.2f} |

H2 (correctness): {'PASS' if h2_pass else 'FAIL'}.
Norm band per Phase 0.1.E: [{_NORM_BAND_SPECTER[0]}, {_NORM_BAND_SPECTER[1]}].

Embedding wall-clock: {emb_elapsed:.0f}s
({emb_elapsed/(len(s_abs)+len(u_abs)+len(h75_abs)+len(h20_abs)):.3f} s/abs).

## H7' results across K

H7' = effN_S(H_1975) > {_H7_ARTIFACT_RATIO} × effN_U(H_1975) (artifact)
AND |effN_S(H_2020) − effN_U(H_2020)| / max < {_H7_NEGATIVE_CONTROL_TOL} (NC).

| K | S/H75 | U/H75 | ratio | art? | S/H20 | U/H20 | NC rd | NC? | overall |
|---|---:|---:|---:|---|---:|---:|---:|---|---|
{h7_table}

Cluster-fit wall-clock: {clust_elapsed:.0f}s.

## Acceptance gate

Per `phase-0.2-execution.md` Wave 2A acceptance:
- H7' PASS at K={k_primary} primary → §11 validated; proceed to Stage 1.
- H7' PASS at K∈{list(k_robustness)} only → robustness sweep flag.
- H7' FAIL at all K → BLOCK Stage 1 transition.

**Result: {gate}**

{gate_msg}

## Wall-clock summary

| Stage | Time |
|---|---:|
| Pulls | {pull_elapsed:.0f}s |
| Embedding | {emb_elapsed:.0f}s |
| Cluster fit + H7' | {clust_elapsed:.0f}s |
| **Total** | **{pull_elapsed + emb_elapsed + clust_elapsed:.0f}s** |

## Cluster-fit manifest

Per §11 commitment: centroids committed for reproducibility.

"""
    for k in [k_primary, *k_robustness]:
        body += (
            f"- K={k}: "
            f"`{Path(manifest_paths[k]['s']).name}`, "
            f"`{Path(manifest_paths[k]['u']).name}`\n"
        )

    body += f"""

## Artifacts

- `experiments/phase-0.2/section11-production-validation{suffix}.md` — this artifact
- `data/metadata/section11-prod-{{S,U,H_1975,H_2020}}{suffix}.parquet` — pulled metadata
- `data/metadata/section11-prod-{{S,U,H_1975,H_2020}}-vec{suffix}.npy` — SPECTER2 vectors
- `data/metadata/section11-cluster-fit-{{S,U}}-K{{30,50,100}}{suffix}.npy` — cluster centroids
- `experiments/phase-0.2/section11_production_validation.py` — this script
"""
    md_path.write_text(body)
    print(f"  wrote {md_path}")
    print()

    # Save full results JSON
    json_summary = {
        "snapshot": snapshot,
        "smoke": smoke,
        "n_S": len(s_works),
        "n_U": len(u_works),
        "n_H_1975": len(h75_works),
        "n_H_2020": len(h20_works),
        "h1_pass": h1_pass,
        "h2_pass": h2_pass,
        "h7_results": {
            str(k): {kk: vv for kk, vv in h7.items()} for k, h7 in h7_results.items()
        },
        "gate": gate,
        "gate_msg": gate_msg,
        "wall_clock": {
            "pulls_sec": pull_elapsed,
            "embedding_sec": emb_elapsed,
            "cluster_sec": clust_elapsed,
            "total_sec": pull_elapsed + emb_elapsed + clust_elapsed,
        },
    }
    json_path = _OUT_DIR / f"section11-production-validation{suffix}-summary.json"
    json_path.write_text(json.dumps(json_summary, indent=2, default=str))
    print(f"  wrote {json_path}")
    print()

    print(f"Wave 2A complete. Gate: {gate}")


if __name__ == "__main__":
    main()
    sys.exit(0)
