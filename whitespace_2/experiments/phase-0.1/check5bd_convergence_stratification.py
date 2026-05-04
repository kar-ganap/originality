"""Checks 5b + 5d — Metric convergence + cluster-fit stratification artifact.

Combined script that produces TWO Phase-0.2 inputs in a single embedding pass:

- **5b — metric convergence analysis.** On a single high-N year (cs 2024),
  sweep subsample sizes n ∈ {200, 500, 1000, 2000, 5000, 10000} for four
  semantic-diversity metrics (effective dimensionality, cluster entropy,
  mean pairwise cosine distance, demographic Shannon). Identify per-metric
  N_target where the estimator stabilizes. Output feeds Phase 0.2's
  per-year bootstrap n = min(Nᵧ, N_target) commitment.

- **5d — cluster-fit stratification artifact size.** Quantify what §11's
  decade-stratified cluster fit actually buys vs an unstratified fit on
  the same total N. Held-out 1975 + 2020 papers are assigned to clusters
  from each fit; the artifact is the assignment-distribution concentration
  difference. §11's commitment is non-negotiable but its magnitude needs
  a Methods-section citation.

Pre-registered hypotheses (mirroring Phase 0.1.E and Check 5c discipline):

  Layer A (pipeline correctness; abort-on-fail):
  - H1 (5b pull): ≥10K unique cs 2024 papers in §0 P.
  - H2 (5d pulls): ≥80 papers per decade in S; ~600 in U; ≥30 each in H_1975
    and H_2020; pairwise disjoint.
  - H3 (embedding correctness): SPECTER2 produces (N, 768) finite, non-zero
    embeddings; per-vector L2 norms in [21.0, 23.0].
  - H4 (KMeans determinism): cluster fits reproducible from random_state=46,
    n_init=20.

  Layer B (scientific findings):
  - H5 (5b convergence): per-metric curve stabilizes; N_target identifiable
    per the convergence criterion (point estimate <5% change across two
    n-step comparisons AND inter-subsample CV <10%).
  - H6 (5b N_target predictions, wide bands; goal is empirical extraction).
  - H7 (5d artifact): effN_S(H_1975) > 1.43 × effN_U(H_1975) (artifact
    present pre-1990) AND |effN_S(H_2020) - effN_U(H_2020)| / max(...) < 0.20
    (artifact absent on negative control).

Run from ws2 root:
    uv run python experiments/phase-0.1/check5bd_convergence_stratification.py [--smoke]
"""

from __future__ import annotations

import argparse
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
from tqdm import tqdm

from whitespace2 import embeddings as emb
from whitespace2 import openalex

# ---------- paths ----------

_OUT_DIR = Path(__file__).parent
_DATA_METADATA_DIR = _OUT_DIR.parent.parent / "data" / "metadata"


# ---------- pull spec (lifted from check5c; locked) ----------

_FIELD = "cs"
_FIELD_CONCEPT_ID = "C41008148"
_SCORE_THRESHOLD = 0.3
_JUNK_YEAR_TOKENS_PRE1990: tuple[str, ...] = (
    "r-cnn",
    "iot",
    "blockchain",
    "transformer",
    "smartphone",
)
_JUNK_YEAR_THRESHOLD = 1990

_SELECT = [
    "id",
    "title",
    "publication_year",
    "type",
    "abstract_inverted_index",
    "authorships",
    "concepts",
    "cited_by_count",
    "referenced_works",
    "primary_location",
    "ids",
]


# ---------- check 5bd parameters ----------

# 5b full-mode targets
_FULL_5B_TARGET_N = 10_000
_FULL_5B_YEAR = 2024
_FULL_5B_SEEDS = list(range(100, 210))  # 110 seeds; ~22K pre-filter at 200/seed
_FULL_5B_SUPPLEMENTAL_SEEDS = list(range(210, 260))  # if 110 seeds fall short

# 5d full-mode targets
_DECADES: tuple[tuple[int, int], ...] = (
    (1970, 1980),
    (1980, 1990),
    (1990, 2000),
    (2000, 2010),
    (2010, 2020),
    (2020, 2025),
)
_FULL_5D_PER_DECADE_TARGET = 80
_FULL_5D_UNSTRAT_TARGET = 600
_FULL_5D_HELDOUT_TARGET = 30
_FULL_5D_DECADE_SEEDS = (50, 51, 52, 53, 54, 55)
_FULL_5D_UNSTRAT_SEED = 60
_FULL_5D_HELDOUT_1975_SEED = 70
_FULL_5D_HELDOUT_2020_SEED = 71

_SAMPLE_PER_CELL = 200  # OpenAlex cap

# Smoke-mode targets
_SMOKE_5B_TARGET_N = 200
_SMOKE_5B_SEEDS = list(range(100, 105))  # 5 seeds × 200 = 1000 pre-filter
_SMOKE_5D_PER_DECADE_TARGET = 10
_SMOKE_5D_UNSTRAT_TARGET = 60
_SMOKE_5D_HELDOUT_TARGET = 10
_SMOKE_SAMPLE_PER_CELL = 100

# Cluster-fit parameters (per §11)
_K_PRIMARY = 50
_K_ROBUSTNESS = (30, 100)
_SMOKE_K_PRIMARY = 25
_SMOKE_K_ROBUSTNESS = (10, 50)  # 50 fits in smoke |S|=60
_KMEANS_RANDOM_STATE = 46
_KMEANS_N_INIT = 20
_KMEANS_MAX_ITER = 300

# Convergence sweep
_CONVERGENCE_N_VALUES = (200, 500, 1000, 2000, 5000, 10000)
_DEMOGRAPHIC_N_VALUES = (500, 2000, 10000)
_N_SUBSAMPLES = 20
_CONVERGENCE_PCT_THRESHOLD = 0.05  # <5% point-estimate change
_CONVERGENCE_CV_THRESHOLD = 0.10  # <10% inter-subsample CV
_PCA_DEGENERACY_FLOOR = 768  # below this, PCA participation ratio is degenerate
_SUBSAMPLE_SEED_BASE = 1000

# H7 (§11 validation) thresholds
_H7_ARTIFACT_RATIO = 1.43  # effN_S / effN_U on H_1975 must exceed this
_H7_NEGATIVE_CONTROL_TOL = 0.20  # |effN_S - effN_U| / max(...) on H_2020 < this

# Memory cap for n=10000 pairwise cosine
_PAIRWISE_MEMORY_LIMIT_N = 10_000

# Embedding device
_DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
_DTYPE = "fp16"
_BS_SPECTER = 8

_NORM_BAND_SPECTER = (21.0, 23.0)


# ---------- post-fetch filters (lifted verbatim from check5c) ----------


def _field_concept_score(work: dict[str, Any], field_concept_id: str) -> float | None:
    concepts = work.get("concepts") or []
    if not isinstance(concepts, list):
        return None
    for concept in concepts:
        if not isinstance(concept, dict):
            continue
        raw_id = concept.get("id") or ""
        bare = raw_id.rsplit("/", 1)[-1] if "/" in raw_id else raw_id
        if bare == field_concept_id:
            score = concept.get("score")
            return float(score) if score is not None else 0.0
    return None


def _passes_score_threshold(work: dict[str, Any], field_concept_id: str) -> bool:
    score = _field_concept_score(work, field_concept_id)
    return score is not None and score >= _SCORE_THRESHOLD


def _passes_junk_year_filter(work: dict[str, Any]) -> bool:
    year = work.get("publication_year")
    if year is None or year >= _JUNK_YEAR_THRESHOLD:
        return True
    title = (work.get("title") or "").lower()
    inv = work.get("abstract_inverted_index") or {}
    abstract_tokens = " ".join(inv.keys()).lower() if isinstance(inv, dict) else ""
    text = f"{title} {abstract_tokens}"
    for tok in _JUNK_YEAR_TOKENS_PRE1990:
        if tok in text:
            return False
    return True


def _post_filter(raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
    after_score = [w for w in raw if _passes_score_threshold(w, _FIELD_CONCEPT_ID)]
    after_abstract = [w for w in after_score if openalex.has_abstract(w)]
    after_junk_year = [w for w in after_abstract if _passes_junk_year_filter(w)]
    return after_junk_year


# ---------- pull execution ----------


def _pull_one_call(
    filters: dict[str, str],
    sample_size: int,
    seed: int,
    label: str,
) -> list[dict[str, Any]]:
    """Single OpenAlex sample call with post-filter; tags work_id with label."""
    try:
        raw = openalex.fetch_works(
            filters=filters,
            sample_size=sample_size,
            seed=seed,
            select=_SELECT,
        )
    except RuntimeError as err:
        print(f"  WARN: {label} seed={seed}: {err}")
        return []
    kept = _post_filter(raw)
    for w in kept:
        w["_pull_label"] = label
        w["_pull_seed"] = seed
    return kept


def _pull_5b(
    target_n: int,
    seeds: list[int],
    supplemental_seeds: list[int],
    sample_per_cell: int,
    year: int,
) -> list[dict[str, Any]]:
    """Multi-seed sampling for the 5b high-N year. Pulls until target_n unique
    post-filter or runs out of seeds."""
    seen_ids: set[str] = set()
    out: list[dict[str, Any]] = []
    n_calls = 0
    n_raw = 0

    all_seeds = seeds + supplemental_seeds
    pbar = tqdm(all_seeds, desc=f"5b cs {year}")
    for seed in pbar:
        if len(out) >= target_n:
            break
        kept = _pull_one_call(
            filters={
                "concepts.id": _FIELD_CONCEPT_ID,
                "publication_year": str(year),
            },
            sample_size=sample_per_cell,
            seed=seed,
            label="5b",
        )
        n_calls += 1
        n_raw += sample_per_cell  # request size, not necessarily returned
        for w in kept:
            wid = w.get("id")
            if not isinstance(wid, str) or wid in seen_ids:
                continue
            seen_ids.add(wid)
            out.append(w)
        pbar.set_postfix({"unique": len(out)})
        time.sleep(0.3)

    print(f"  5b: {n_calls} calls, ~{n_raw} pre-filter, {len(out)} unique post-filter")
    return out


def _pull_5d(
    smoke: bool,
) -> tuple[
    list[dict[str, Any]], list[dict[str, Any]],
    list[dict[str, Any]], list[dict[str, Any]],
]:
    """Pull stratified pool S, unstratified pool U, held-outs H_1975 and H_2020.

    Enforces pairwise disjointness by set-difference dedup.

    Returns (S, U, H_1975, H_2020).
    """
    per_decade_target = (
        _SMOKE_5D_PER_DECADE_TARGET if smoke else _FULL_5D_PER_DECADE_TARGET
    )
    unstrat_target = _SMOKE_5D_UNSTRAT_TARGET if smoke else _FULL_5D_UNSTRAT_TARGET
    heldout_target = _SMOKE_5D_HELDOUT_TARGET if smoke else _FULL_5D_HELDOUT_TARGET
    sample_per_cell = _SMOKE_SAMPLE_PER_CELL if smoke else _SAMPLE_PER_CELL

    # Stratified pool: per-decade samples
    strat: list[dict[str, Any]] = []
    pbar = tqdm(zip(_DECADES, _FULL_5D_DECADE_SEEDS), total=len(_DECADES),
                desc="5d S strat")
    for (lo, hi), seed in pbar:
        # Decade range filter: OpenAlex supports `publication_year:>=X,<Y` syntax
        # via two filter keys. Simpler: from-/to-publication-date filters.
        # Use publication_year:lo-(hi-1) range syntax.
        year_filter = f"{lo}-{hi - 1}"
        kept = _pull_one_call(
            filters={
                "concepts.id": _FIELD_CONCEPT_ID,
                "publication_year": year_filter,
            },
            sample_size=sample_per_cell,
            seed=seed,
            label=f"5d_strat_{lo}s",
        )
        # Take up to per_decade_target from this decade
        for w in kept[:per_decade_target]:
            w["_pull_decade"] = lo
            strat.append(w)
        pbar.set_postfix({"|S|": len(strat)})
        time.sleep(0.3)

    # Unstratified pool: single sample over the full window
    print("5d U unstrat...")
    unstrat_kept = _pull_one_call(
        filters={
            "concepts.id": _FIELD_CONCEPT_ID,
            "publication_year": "1970-2024",
        },
        sample_size=min(sample_per_cell, unstrat_target * 4),  # over-sample
        seed=_FULL_5D_UNSTRAT_SEED,
        label="5d_unstrat",
    )
    # OpenAlex max sample is 200 per call. Multi-call if we need more.
    extra_seeds = [_FULL_5D_UNSTRAT_SEED + 100 + i for i in range(20)]
    seen = {w.get("id") for w in unstrat_kept if isinstance(w.get("id"), str)}
    extra_pbar = tqdm(extra_seeds, desc="5d U supplemental")
    for seed in extra_pbar:
        if len(unstrat_kept) >= unstrat_target:
            break
        kept = _pull_one_call(
            filters={
                "concepts.id": _FIELD_CONCEPT_ID,
                "publication_year": "1970-2024",
            },
            sample_size=sample_per_cell,
            seed=seed,
            label="5d_unstrat",
        )
        for w in kept:
            wid = w.get("id")
            if isinstance(wid, str) and wid not in seen:
                seen.add(wid)
                unstrat_kept.append(w)
        extra_pbar.set_postfix({"|U|": len(unstrat_kept)})
        time.sleep(0.3)
    unstrat = unstrat_kept[:unstrat_target]

    # Held-outs
    h1975 = _pull_one_call(
        filters={
            "concepts.id": _FIELD_CONCEPT_ID,
            "publication_year": "1975",
        },
        sample_size=sample_per_cell,
        seed=_FULL_5D_HELDOUT_1975_SEED,
        label="5d_h1975",
    )[:heldout_target * 2]
    h2020 = _pull_one_call(
        filters={
            "concepts.id": _FIELD_CONCEPT_ID,
            "publication_year": "2020",
        },
        sample_size=sample_per_cell,
        seed=_FULL_5D_HELDOUT_2020_SEED,
        label="5d_h2020",
    )[:heldout_target * 2]

    # Enforce pairwise disjointness via id-set difference
    strat_ids = {w.get("id") for w in strat if isinstance(w.get("id"), str)}
    unstrat_ids = {w.get("id") for w in unstrat if isinstance(w.get("id"), str)}

    unstrat = [w for w in unstrat if w.get("id") not in strat_ids]
    h1975 = [
        w for w in h1975
        if w.get("id") not in strat_ids and w.get("id") not in unstrat_ids
    ][:heldout_target]
    h2020_ids_so_far = {w.get("id") for w in h1975 if isinstance(w.get("id"), str)}
    h2020 = [
        w for w in h2020
        if w.get("id") not in strat_ids
        and w.get("id") not in unstrat_ids
        and w.get("id") not in h2020_ids_so_far
    ][:heldout_target]

    print(
        f"  5d: |S|={len(strat)}, |U|={len(unstrat)}, "
        f"|H_1975|={len(h1975)}, |H_2020|={len(h2020)}"
    )
    return strat, unstrat, h1975, h2020


# ---------- abstract decoding ----------


def _reconstruct_abstract(inverted_index: dict[str, list[int]]) -> str:
    if not inverted_index:
        return ""
    max_pos = max(max(positions) for positions in inverted_index.values())
    tokens = [""] * (max_pos + 1)
    for word, positions in inverted_index.items():
        for pos in positions:
            tokens[pos] = word
    return " ".join(t for t in tokens if t)


# ---------- parquet schema ----------


def _flatten_for_parquet(work: dict[str, Any], set_label: str) -> dict[str, Any]:
    return {
        "work_id": work.get("id"),
        "title": work.get("title") or "",
        "publication_year": work.get("publication_year"),
        "type": work.get("type"),
        "field": _FIELD,
        "set_label": set_label,
        "pull_label": work.get("_pull_label"),
        "pull_seed": work.get("_pull_seed"),
        "pull_decade": work.get("_pull_decade"),
        "has_abstract": openalex.has_abstract(work),
        "field_tag_score": _field_concept_score(work, _FIELD_CONCEPT_ID),
        "cited_by_count": work.get("cited_by_count", 0),
        "n_authorships": len(work.get("authorships") or []),
        "n_referenced_works": len(work.get("referenced_works") or []),
        "n_concepts": len(work.get("concepts") or []),
        "first_country": openalex.extract_first_country(work),
        "doi": openalex.extract_doi(work),
        "abstract_inverted_index_json": json.dumps(
            work.get("abstract_inverted_index") or {}
        ),
        "authorships_json": json.dumps(work.get("authorships") or []),
        "concepts_json": json.dumps(work.get("concepts") or []),
        "referenced_works_json": json.dumps(work.get("referenced_works") or []),
        "primary_location_json": json.dumps(work.get("primary_location") or {}),
    }


def _to_dataframe(works: list[dict[str, Any]], set_label: str) -> pd.DataFrame:
    return pd.DataFrame([_flatten_for_parquet(w, set_label) for w in works])


def _decode_abstracts(df: pd.DataFrame) -> list[str]:
    out: list[str] = []
    for inv_json in df["abstract_inverted_index_json"]:
        inv = json.loads(inv_json) if inv_json else {}
        out.append(_reconstruct_abstract(inv))
    return out


# ---------- hypothesis assertions ----------


def _assert_h1_5b(q5b_df: pd.DataFrame, target_n: int) -> None:
    n = len(q5b_df)
    assert n >= target_n, f"H1 fail: |Q_5b|={n} < {target_n}"
    assert q5b_df["work_id"].nunique() == n, "H1 fail: duplicate work_ids in Q_5b"
    bad_year = q5b_df[q5b_df["publication_year"] != _FULL_5B_YEAR]
    assert len(bad_year) == 0, (
        f"H1 fail: {len(bad_year)} Q_5b papers not from year {_FULL_5B_YEAR}"
    )
    bad_score = q5b_df[q5b_df["field_tag_score"] < _SCORE_THRESHOLD]
    assert len(bad_score) == 0, (
        f"H1 fail: {len(bad_score)} Q_5b papers below score≥{_SCORE_THRESHOLD}"
    )
    assert q5b_df["has_abstract"].all(), "H1 fail: some Q_5b lack abstract"
    print(f"  H1 PASS: |Q_5b|={n}; year={_FULL_5B_YEAR}; all post-filter clean.")


def _assert_h2_5d(
    s_df: pd.DataFrame,
    u_df: pd.DataFrame,
    h1975_df: pd.DataFrame,
    h2020_df: pd.DataFrame,
    per_decade_target: int,
    heldout_target: int,
) -> None:
    # Stratified pool: ≥per_decade_target per decade
    counts = s_df.groupby("pull_decade").size()
    for (lo, hi) in _DECADES:
        n = int(counts.get(lo, 0))
        # Allow small under-counts in smoke (retention may be sparse for early decades)
        if n < per_decade_target:
            print(
                f"  H2 WARN: decade {lo}s has only {n} papers (target ≥{per_decade_target}); "
                "continuing with available count"
            )
    # Held-outs
    assert len(h1975_df) >= heldout_target, (
        f"H2 fail: |H_1975|={len(h1975_df)} < {heldout_target}"
    )
    assert len(h2020_df) >= heldout_target, (
        f"H2 fail: |H_2020|={len(h2020_df)} < {heldout_target}"
    )
    # Pairwise disjointness
    s_ids = set(s_df["work_id"])
    u_ids = set(u_df["work_id"])
    h1975_ids = set(h1975_df["work_id"])
    h2020_ids = set(h2020_df["work_id"])
    assert len(s_ids & u_ids) == 0, "H2 fail: S ∩ U ≠ ∅"
    assert len(s_ids & h1975_ids) == 0, "H2 fail: S ∩ H_1975 ≠ ∅"
    assert len(s_ids & h2020_ids) == 0, "H2 fail: S ∩ H_2020 ≠ ∅"
    assert len(u_ids & h1975_ids) == 0, "H2 fail: U ∩ H_1975 ≠ ∅"
    assert len(u_ids & h2020_ids) == 0, "H2 fail: U ∩ H_2020 ≠ ∅"
    assert len(h1975_ids & h2020_ids) == 0, "H2 fail: H_1975 ∩ H_2020 ≠ ∅"
    print(
        f"  H2 PASS: |S|={len(s_df)}; |U|={len(u_df)}; "
        f"|H_1975|={len(h1975_df)}; |H_2020|={len(h2020_df)}; pairwise disjoint."
    )


def _assert_h3_embedding(name: str, vectors: np.ndarray[Any, Any], expected_n: int) -> None:
    assert vectors.shape == (expected_n, 768), (
        f"H3 fail [{name}]: shape={vectors.shape}, expected ({expected_n}, 768)"
    )
    assert np.isfinite(vectors).all(), f"H3 fail [{name}]: non-finite values"
    norms = np.linalg.norm(vectors, axis=1)
    assert (norms > 0).all(), f"H3 fail [{name}]: zero-norm vector(s)"
    mean_norm = float(norms.mean())
    band = _NORM_BAND_SPECTER
    if not (band[0] <= mean_norm <= band[1]):
        print(
            f"  H3 WARN [{name}]: mean L2 norm={mean_norm:.3f} outside "
            f"recorded band {band}"
        )
    print(
        f"  H3 PASS [{name}]: shape={vectors.shape}; finite; non-zero; "
        f"mean L2 norm={mean_norm:.3f}."
    )


# ---------- L2 normalize ----------


def _l2_normalize(vectors: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.where(norms > 0, norms, 1.0)
    out: np.ndarray[Any, Any] = (vectors / norms).astype(np.float32)
    return out


# ---------- metric implementations ----------


def _shannon_entropy(p: np.ndarray[Any, Any], miller_madow: bool = True) -> float:
    """Shannon entropy in nats. Optional Miller-Madow bias correction (adds
    (k-1)/(2n) where k is #non-zero categories and n is total count, but we
    receive p as a probability distribution so n must be passed separately)."""
    p = np.asarray(p, dtype=np.float64)
    p = p[p > 0]
    h = -float((p * np.log(p)).sum())
    return h


def _shannon_entropy_with_mm(
    counts: np.ndarray[Any, Any], n_total: int
) -> float:
    """Miller-Madow corrected Shannon entropy from raw counts."""
    counts = np.asarray(counts, dtype=np.float64)
    p = counts / max(n_total, 1)
    h = _shannon_entropy(p)
    if n_total > 0:
        k_nonzero = int((counts > 0).sum())
        h += (k_nonzero - 1) / (2 * n_total)
    return h


def _cluster_entropy(
    assignments: np.ndarray[Any, Any], k: int
) -> float:
    """Shannon entropy of cluster-assignment distribution, MM-corrected."""
    counts = np.bincount(assignments, minlength=k)
    return _shannon_entropy_with_mm(counts, int(assignments.size))


def _effective_dimensionality(vectors: np.ndarray[Any, Any]) -> float:
    """PCA participation ratio (Σλᵢ)² / Σλᵢ² where λᵢ are eigenvalues of
    sample covariance. Computed via SVD on per-batch centered vectors.

    Caveat: when n < d, covariance rank ≤ n-1, so effective dim ≤ n-1 by
    construction. Caller responsibility to flag degenerate regime.
    """
    n = vectors.shape[0]
    if n < 2:
        return 0.0
    centered = vectors - vectors.mean(axis=0, keepdims=True)
    # SVD on centered; eigenvalues of cov are svd singular values squared / (n-1)
    s = np.linalg.svd(centered, compute_uv=False)
    eig = (s**2) / (n - 1)
    eig = eig[eig > 0]
    if eig.size == 0:
        return 0.0
    return float(eig.sum() ** 2 / (eig**2).sum())


def _mean_pairwise_cosine_distance(vectors_norm: np.ndarray[Any, Any]) -> float:
    """Mean of upper-triangle of pairwise cosine distance on L2-normalized
    vectors. 1 - X X^T."""
    n = vectors_norm.shape[0]
    if n < 2:
        return 0.0
    sim = vectors_norm @ vectors_norm.T
    # Upper triangle (excluding diagonal)
    iu = np.triu_indices(n, k=1)
    cosine_sim = sim[iu]
    cosine_dist = 1.0 - cosine_sim
    return float(cosine_dist.mean())


def _demographic_shannon(countries: pd.Series) -> float:
    """Miller-Madow corrected Shannon entropy on first_country categorical."""
    valid = countries.dropna()
    n = int(len(valid))
    if n == 0:
        return 0.0
    counts_series = valid.value_counts()
    counts = counts_series.to_numpy()
    return _shannon_entropy_with_mm(counts, n)


# ---------- convergence sweep ----------


def _convergence_sweep(
    metric_name: str,
    n_values: tuple[int, ...],
    full_data: Any,  # ndarray, Series, or otherwise indexable
    metric_fn: Any,  # function(subsample) -> float
    n_subsamples: int = _N_SUBSAMPLES,
    seed_base: int = _SUBSAMPLE_SEED_BASE,
    skip_below: int = 0,
) -> pd.DataFrame:
    """For each n, take n_subsamples random subsamples of full_data, apply
    metric_fn, record mean and SD. Returns a long-form DataFrame.

    `full_data` is anything indexable by an int array (np.ndarray, pd.Series,
    pd.DataFrame). For ndarray, subsample = full_data[idx]. For Series,
    same. For DataFrame, full_data.iloc[idx].
    """
    rows: list[dict[str, Any]] = []
    full_n: int
    if isinstance(full_data, np.ndarray):
        full_n = int(full_data.shape[0])
    else:
        full_n = int(len(full_data))

    pbar = tqdm(n_values, desc=f"sweep {metric_name}")
    for n in pbar:
        if n > full_n:
            print(
                f"  WARN [{metric_name}]: requested n={n} exceeds available {full_n}; "
                "skipping"
            )
            continue
        if n < skip_below:
            # Compute but mark degenerate
            degenerate = True
        else:
            degenerate = False

        values: list[float] = []
        for s in range(n_subsamples):
            rng = np.random.default_rng(seed_base + s * 100 + n)
            idx = rng.choice(full_n, size=n, replace=False)
            if isinstance(full_data, np.ndarray):
                sub = full_data[idx]
            elif isinstance(full_data, pd.Series):
                sub = full_data.iloc[idx]
            elif isinstance(full_data, pd.DataFrame):
                sub = full_data.iloc[idx]
            else:
                sub = [full_data[int(i)] for i in idx]
            values.append(float(metric_fn(sub)))

        arr = np.asarray(values)
        rows.append({
            "metric": metric_name,
            "n": n,
            "mean": float(arr.mean()),
            "sd": float(arr.std(ddof=1)) if arr.size > 1 else 0.0,
            "cv": (
                float(arr.std(ddof=1) / arr.mean())
                if (arr.size > 1 and arr.mean() != 0)
                else 0.0
            ),
            "n_subsamples": n_subsamples,
            "degenerate": degenerate,
        })
        pbar.set_postfix({"mean": f"{arr.mean():.4f}"})

    return pd.DataFrame(rows)


def _identify_n_target(
    sweep: pd.DataFrame,
    pct_threshold: float = _CONVERGENCE_PCT_THRESHOLD,
    cv_threshold: float = _CONVERGENCE_CV_THRESHOLD,
) -> tuple[int | None, str]:
    """Apply convergence criterion: smallest n such that
    (a) point estimate change <pct_threshold% across the next two n-step comparisons
    (b) inter-subsample CV <cv_threshold at n.

    Returns (N_target, rationale_string). N_target=None means did not converge.
    """
    valid = sweep[~sweep["degenerate"]].sort_values("n").reset_index(drop=True)
    if len(valid) < 3:
        return None, f"insufficient points (need ≥3 non-degenerate, have {len(valid)})"

    for i in range(len(valid) - 2):
        n = int(valid.iloc[i]["n"])
        m_n = valid.iloc[i]["mean"]
        m_2n = valid.iloc[i + 1]["mean"]
        m_5n = valid.iloc[i + 2]["mean"]
        if m_n == 0:
            continue
        pct_change_1 = abs(m_2n - m_n) / abs(m_n)
        pct_change_2 = abs(m_5n - m_2n) / abs(m_2n) if m_2n != 0 else float("inf")
        cv_n = float(valid.iloc[i]["cv"])
        if (
            pct_change_1 < pct_threshold
            and pct_change_2 < pct_threshold
            and cv_n < cv_threshold
        ):
            return n, (
                f"Δ_1={pct_change_1:.1%}, Δ_2={pct_change_2:.1%}, CV={cv_n:.1%} "
                f"all under thresholds at n={n}"
            )
    return None, "did not converge by largest n in sweep"


# ---------- §11 H7 cluster-stratification analysis ----------


def _effective_n_clusters(assignments: np.ndarray[Any, Any], k: int) -> float:
    """exp(Shannon entropy) of cluster-assignment distribution."""
    h = _cluster_entropy(assignments, k)
    return float(np.exp(h))


def _kl_to_uniform(assignments: np.ndarray[Any, Any], k: int) -> float:
    """KL(p || uniform) for cluster-assignment distribution."""
    counts = np.bincount(assignments, minlength=k).astype(np.float64)
    n = counts.sum()
    if n == 0:
        return 0.0
    p = counts / n
    p_nonzero = p[p > 0]
    log_k = float(np.log(k))
    h = -float((p_nonzero * np.log(p_nonzero)).sum())
    return log_k - h


def _fit_kmeans(vectors: np.ndarray[Any, Any], k: int) -> KMeans:
    return KMeans(
        n_clusters=k,
        random_state=_KMEANS_RANDOM_STATE,
        n_init=_KMEANS_N_INIT,
        max_iter=_KMEANS_MAX_ITER,
    ).fit(vectors)


def _h7_analysis(
    embeddings_S: np.ndarray[Any, Any],
    embeddings_U: np.ndarray[Any, Any],
    embeddings_H1975: np.ndarray[Any, Any],
    embeddings_H2020: np.ndarray[Any, Any],
    k: int,
) -> dict[str, Any]:
    """Fit KMeans on S and on U; assign held-outs; report effN + KL per
    fit × held-out. Returns a single-row dict ready for DataFrame ingest.
    """
    print(f"  fitting KMeans K={k} on S (|S|={embeddings_S.shape[0]})...")
    km_s = _fit_kmeans(embeddings_S, k)
    print(f"  fitting KMeans K={k} on U (|U|={embeddings_U.shape[0]})...")
    km_u = _fit_kmeans(embeddings_U, k)

    a_s_h1975 = km_s.predict(embeddings_H1975)
    a_u_h1975 = km_u.predict(embeddings_H1975)
    a_s_h2020 = km_s.predict(embeddings_H2020)
    a_u_h2020 = km_u.predict(embeddings_H2020)

    eff_s_h1975 = _effective_n_clusters(a_s_h1975, k)
    eff_u_h1975 = _effective_n_clusters(a_u_h1975, k)
    eff_s_h2020 = _effective_n_clusters(a_s_h2020, k)
    eff_u_h2020 = _effective_n_clusters(a_u_h2020, k)

    kl_s_h1975 = _kl_to_uniform(a_s_h1975, k)
    kl_u_h1975 = _kl_to_uniform(a_u_h1975, k)
    kl_s_h2020 = _kl_to_uniform(a_s_h2020, k)
    kl_u_h2020 = _kl_to_uniform(a_u_h2020, k)

    # Decision rule (only meaningful at K_PRIMARY; reported at all K)
    h1975_ratio = eff_s_h1975 / eff_u_h1975 if eff_u_h1975 > 0 else float("inf")
    artifact_present_1975 = h1975_ratio > _H7_ARTIFACT_RATIO

    if max(eff_s_h2020, eff_u_h2020) > 0:
        h2020_diff = abs(eff_s_h2020 - eff_u_h2020) / max(eff_s_h2020, eff_u_h2020)
    else:
        h2020_diff = 0.0
    artifact_absent_2020 = h2020_diff < _H7_NEGATIVE_CONTROL_TOL

    return {
        "k": k,
        "effN_S_H1975": eff_s_h1975,
        "effN_U_H1975": eff_u_h1975,
        "effN_S_H2020": eff_s_h2020,
        "effN_U_H2020": eff_u_h2020,
        "KL_S_H1975": kl_s_h1975,
        "KL_U_H1975": kl_u_h1975,
        "KL_S_H2020": kl_s_h2020,
        "KL_U_H2020": kl_u_h2020,
        "h1975_S_over_U_ratio": h1975_ratio,
        "h2020_relative_diff": h2020_diff,
        "artifact_present_1975": artifact_present_1975,
        "artifact_absent_2020": artifact_absent_2020,
        "validates_section_11": artifact_present_1975 and artifact_absent_2020,
        "inertia_S": float(km_s.inertia_),
        "inertia_U": float(km_u.inertia_),
        "centroids_S": km_s.cluster_centers_,
        "centroids_U": km_u.cluster_centers_,
    }


# ---------- per-step orchestration ----------


def _do_pulls(smoke: bool) -> tuple[
    pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame,
    dict[str, Any],
]:
    """Returns (q5b_df, s_df, u_df, h1975_df, h2020_df, summary)."""
    if smoke:
        target = _SMOKE_5B_TARGET_N
        seeds = _SMOKE_5B_SEEDS
        supplemental: list[int] = []
        sample_per = _SMOKE_SAMPLE_PER_CELL
    else:
        target = _FULL_5B_TARGET_N
        seeds = _FULL_5B_SEEDS
        supplemental = _FULL_5B_SUPPLEMENTAL_SEEDS
        sample_per = _SAMPLE_PER_CELL

    q5b_works = _pull_5b(target, seeds, supplemental, sample_per, _FULL_5B_YEAR)
    s_works, u_works, h1975_works, h2020_works = _pull_5d(smoke)

    q5b_df = _to_dataframe(q5b_works, "Q_5b")
    s_df = _to_dataframe(s_works, "S")
    u_df = _to_dataframe(u_works, "U")
    h1975_df = _to_dataframe(h1975_works, "H_1975")
    h2020_df = _to_dataframe(h2020_works, "H_2020")

    # Final disjointness enforcement at the dataframe level (defense in depth)
    s_ids = set(s_df["work_id"])
    u_df = u_df[~u_df["work_id"].isin(s_ids)].reset_index(drop=True)
    u_ids = set(u_df["work_id"])
    h1975_df = h1975_df[
        ~h1975_df["work_id"].isin(s_ids) & ~h1975_df["work_id"].isin(u_ids)
    ].reset_index(drop=True)
    h_ids = set(h1975_df["work_id"])
    h2020_df = h2020_df[
        ~h2020_df["work_id"].isin(s_ids)
        & ~h2020_df["work_id"].isin(u_ids)
        & ~h2020_df["work_id"].isin(h_ids)
    ].reset_index(drop=True)

    summary = {
        "Q_5b_n": len(q5b_df),
        "S_n": len(s_df),
        "U_n": len(u_df),
        "H_1975_n": len(h1975_df),
        "H_2020_n": len(h2020_df),
        "snapshot": openalex.latest_snapshot_date(),
    }
    return q5b_df, s_df, u_df, h1975_df, h2020_df, summary


def _do_embeddings(
    q5b_df: pd.DataFrame,
    s_df: pd.DataFrame,
    u_df: pd.DataFrame,
    h1975_df: pd.DataFrame,
    h2020_df: pd.DataFrame,
) -> dict[str, np.ndarray[Any, Any]]:
    """Embed all five sets in one SPECTER2 batch run; L2-normalize."""
    all_dfs = [q5b_df, s_df, u_df, h1975_df, h2020_df]
    labels = ["Q_5b", "S", "U", "H_1975", "H_2020"]
    counts = [len(df) for df in all_dfs]

    all_abstracts: list[str] = []
    for df in all_dfs:
        all_abstracts.extend(_decode_abstracts(df))

    print(f"  SPECTER2 embedding {len(all_abstracts)} abstracts (bs={_BS_SPECTER})...")
    t0 = time.time()
    vectors = emb.embed_specter2(
        all_abstracts, device=_DEVICE, batch_size=_BS_SPECTER, dtype=_DTYPE,
    )
    elapsed = time.time() - t0
    print(
        f"    SPECTER2 {elapsed:.1f}s ({elapsed / max(1, len(all_abstracts)):.3f}s/abs)"
    )

    _assert_h3_embedding("specter2", vectors, len(all_abstracts))
    normed = _l2_normalize(vectors)

    out: dict[str, np.ndarray[Any, Any]] = {}
    cur = 0
    for label, n in zip(labels, counts):
        out[label] = normed[cur : cur + n]
        cur += n
    out["_elapsed_sec"] = np.array([elapsed])
    return out


def _do_5b_convergence(
    q5b_df: pd.DataFrame,
    embeddings: dict[str, np.ndarray[Any, Any]],
    centroids_S: np.ndarray[Any, Any],
    n_values: tuple[int, ...],
    demographic_n_values: tuple[int, ...],
) -> pd.DataFrame:
    """Run convergence sweep on four metrics. Returns long-form DataFrame."""
    q5b_emb = embeddings["Q_5b"]
    n_q = q5b_emb.shape[0]
    valid_n = tuple(n for n in n_values if n <= n_q)
    valid_demo_n = tuple(n for n in demographic_n_values if n <= n_q)

    # Pre-compute cluster assignments for Q_5b (against S-fit centroids)
    print("  computing 5b cluster assignments (against S-fit canonical centroids)...")
    # Use sklearn to compute nearest centroid via predict
    km_dummy = KMeans(n_clusters=centroids_S.shape[0], random_state=0, n_init=1)
    km_dummy.cluster_centers_ = centroids_S.astype(q5b_emb.dtype)
    km_dummy.n_features_in_ = centroids_S.shape[1]
    km_dummy._n_threads = 1
    assignments_5b = km_dummy.predict(q5b_emb)

    # Pre-extract first_country
    countries_5b = q5b_df["first_country"]

    # Sweep 1: cluster entropy
    sweep_clust = _convergence_sweep(
        "cluster_entropy",
        valid_n,
        assignments_5b,
        lambda sub: _cluster_entropy(sub, centroids_S.shape[0]),
    )

    # Sweep 2: effective dimensionality
    sweep_effdim = _convergence_sweep(
        "effective_dim",
        valid_n,
        q5b_emb,
        _effective_dimensionality,
        skip_below=_PCA_DEGENERACY_FLOOR,
    )

    # Sweep 3: mean pairwise cosine distance (skip n above memory cap)
    cosine_n = tuple(n for n in valid_n if n <= _PAIRWISE_MEMORY_LIMIT_N)
    sweep_cosine = _convergence_sweep(
        "mean_pairwise_cosine",
        cosine_n,
        q5b_emb,
        _mean_pairwise_cosine_distance,
    )

    # Sweep 4: demographic Shannon (light)
    sweep_demo = _convergence_sweep(
        "demographic_shannon",
        valid_demo_n,
        countries_5b,
        _demographic_shannon,
    )

    return pd.concat([sweep_clust, sweep_effdim, sweep_cosine, sweep_demo],
                     ignore_index=True)


def _do_5d_h7(
    embeddings: dict[str, np.ndarray[Any, Any]],
    k_values: tuple[int, ...],
) -> tuple[pd.DataFrame, dict[int, dict[str, Any]]]:
    """Run H7 cluster-stratification analysis at each K. Returns:
    (long-form per-K DataFrame for the artifact, dict[k -> raw result with centroids]).
    """
    rows: list[dict[str, Any]] = []
    raw: dict[int, dict[str, Any]] = {}
    for k in k_values:
        result = _h7_analysis(
            embeddings["S"], embeddings["U"],
            embeddings["H_1975"], embeddings["H_2020"], k,
        )
        raw[k] = result
        # Strip centroids from row (they're large; persisted separately)
        row = {kk: vv for kk, vv in result.items() if kk not in ("centroids_S", "centroids_U")}
        rows.append(row)
    return pd.DataFrame(rows), raw


# ---------- artifact writing ----------


def _write_pulls(
    q5b_df: pd.DataFrame, s_df: pd.DataFrame, u_df: pd.DataFrame,
    h1975_df: pd.DataFrame, h2020_df: pd.DataFrame, smoke: bool,
) -> None:
    suffix = "-smoke" if smoke else ""
    paths = [
        (_DATA_METADATA_DIR / f"check5bd-pull-2024-cs{suffix}.parquet", q5b_df),
        (_DATA_METADATA_DIR / f"check5bd-stratified-pool{suffix}.parquet", s_df),
        (_DATA_METADATA_DIR / f"check5bd-unstratified-pool{suffix}.parquet", u_df),
        (_DATA_METADATA_DIR / f"check5bd-heldout-1975{suffix}.parquet", h1975_df),
        (_DATA_METADATA_DIR / f"check5bd-heldout-2020{suffix}.parquet", h2020_df),
    ]
    for path, df in paths:
        df.to_parquet(path, index=False)
        print(f"  wrote {path} ({len(df)} rows)")


def _write_embeddings(
    q5b_df: pd.DataFrame, s_df: pd.DataFrame, u_df: pd.DataFrame,
    h1975_df: pd.DataFrame, h2020_df: pd.DataFrame,
    embeddings: dict[str, np.ndarray[Any, Any]], smoke: bool,
) -> None:
    suffix = "-smoke" if smoke else ""
    all_ids = (
        q5b_df["work_id"].tolist() + s_df["work_id"].tolist()
        + u_df["work_id"].tolist() + h1975_df["work_id"].tolist()
        + h2020_df["work_id"].tolist()
    )
    all_labels = (
        ["Q_5b"] * len(q5b_df) + ["S"] * len(s_df) + ["U"] * len(u_df)
        + ["H_1975"] * len(h1975_df) + ["H_2020"] * len(h2020_df)
    )
    all_vecs = np.vstack([
        embeddings["Q_5b"], embeddings["S"], embeddings["U"],
        embeddings["H_1975"], embeddings["H_2020"],
    ])
    emb_df = pd.DataFrame(all_vecs, columns=[f"d{i}" for i in range(768)])
    emb_df.insert(0, "work_id", all_ids)
    emb_df.insert(1, "set_label", all_labels)
    path = _OUT_DIR / f"check5bd-embeddings-specter2{suffix}.parquet"
    emb_df.to_parquet(path, index=False)
    print(f"  wrote {path} ({len(emb_df)} rows)")


def _write_cluster_manifest(
    h7_raw: dict[int, dict[str, Any]],
    s_df: pd.DataFrame, u_df: pd.DataFrame, smoke: bool,
) -> None:
    """Per §11 mandate. Records subsample indices, K, fit hashes, centroid
    arrays."""
    suffix = "-smoke" if smoke else ""
    for k, result in h7_raw.items():
        np.save(
            _DATA_METADATA_DIR / f"cluster-fit-manifest-S-K{k}{suffix}.npy",
            result["centroids_S"],
        )
        np.save(
            _DATA_METADATA_DIR / f"cluster-fit-manifest-U-K{k}{suffix}.npy",
            result["centroids_U"],
        )
    manifest_md = (
        f"# Cluster-fit manifest (per Phase 0.1 plan §11)\n\n"
        f"**Run date:** {datetime.now(timezone.utc).date().isoformat()}\n"
        f"**Mode:** {'smoke' if smoke else 'full'}\n"
        f"**KMeans config:** random_state={_KMEANS_RANDOM_STATE}, "
        f"n_init={_KMEANS_N_INIT}, max_iter={_KMEANS_MAX_ITER}\n\n"
        f"## Stratified pool S\n"
        f"- |S| = {len(s_df)} rows; pulled per decade (1970s-2020s).\n"
        f"- Source parquet: `data/metadata/check5bd-stratified-pool{suffix}.parquet`.\n"
        f"- Per-decade counts: "
        + str(s_df.groupby("pull_decade").size().to_dict()) + "\n\n"
        f"## Unstratified pool U (comparison only)\n"
        f"- |U| = {len(u_df)} rows; OpenAlex `?sample=600` over 1970-2024.\n"
        f"- Source parquet: `data/metadata/check5bd-unstratified-pool{suffix}.parquet`.\n\n"
        f"## Centroid arrays (one .npy per K × per fit)\n"
        + "\n".join(
            f"- `data/metadata/cluster-fit-manifest-{{S,U}}-K{k}{suffix}.npy` — "
            f"shape {h7_raw[k]['centroids_S'].shape}; inertia_S={h7_raw[k]['inertia_S']:.2f}, "
            f"inertia_U={h7_raw[k]['inertia_U']:.2f}"
            for k in sorted(h7_raw.keys())
        )
        + "\n\n## §11 production rule\n"
        "The S-fit centroids at K=50 are the canonical cluster manifest. "
        "Every paper in the production corpus is assigned to its nearest "
        "centroid from this fit. The U fit is comparison-only — used to "
        "quantify the artifact §11 prevents (Check 5d).\n"
    )
    path = _DATA_METADATA_DIR / f"cluster-fit-manifest{suffix}.md"
    path.write_text(manifest_md)
    print(f"  wrote {path}")


def _write_metric_convergence(
    sweep: pd.DataFrame, q5b_n: int, snapshot: str, smoke: bool,
) -> None:
    suffix = "-smoke" if smoke else ""
    csv_path = _OUT_DIR / f"metric-convergence{suffix}.csv"
    sweep.to_csv(csv_path, index=False)
    print(f"  wrote {csv_path} ({len(sweep)} rows)")

    # Identify N_target per metric
    decisions: list[dict[str, Any]] = []
    for metric in sweep["metric"].unique():
        sub = sweep[sweep["metric"] == metric]
        n_target, rationale = _identify_n_target(sub)
        decisions.append({
            "metric": metric,
            "N_target": n_target,
            "rationale": rationale,
            "max_n_in_sweep": int(sub["n"].max()),
        })

    # Build markdown
    rows_md = "\n".join(
        f"| {r['metric']} | {r['N_target'] if r['N_target'] else 'did not converge'} "
        f"| {r['max_n_in_sweep']} | {r['rationale']} |"
        for r in decisions
    )

    sweep_md = "\n".join(
        f"| {r['metric']} | {r['n']} | {r['mean']:.4f} | {r['sd']:.4f} | "
        f"{r['cv']:.1%} | {'(degenerate)' if r['degenerate'] else ''} |"
        for _, r in sweep.iterrows()
    )

    body = f"""# Check 5b — Metric convergence analysis{' (SMOKE)' if smoke else ''}

**Run date:** {datetime.now(timezone.utc).date().isoformat()}
**Snapshot:** {snapshot}
**Mode:** {'smoke' if smoke else 'full'}
**Q_5b:** cs {_FULL_5B_YEAR}, |Q_5b|={q5b_n}, multi-seed sample of OpenAlex.
**Subsamples per n:** {_N_SUBSAMPLES} independent draws, RNG seed_base={_SUBSAMPLE_SEED_BASE}.

## Convergence criterion (pre-registered, H5)

Smallest n at which both:
1. Point estimate change <{_CONVERGENCE_PCT_THRESHOLD:.0%} across the next two n-step comparisons.
2. Inter-subsample CV <{_CONVERGENCE_CV_THRESHOLD:.0%} at n.

If no n meets the criterion within the sweep range, N_target = "did not converge"
and the metric's bootstrap n locks at min(Nᵧ, max-n-in-sweep) for Phase 0.2 with
a noted caveat.

## Per-metric N_target (Phase 0.2 input)

| Metric | N_target | Max n in sweep | Rationale |
|---|---:|---:|---|
{rows_md}

## Full sweep

| Metric | n | Mean | SD | CV | Notes |
|---|---:|---:|---:|---:|---|
{sweep_md}

## Caveats

- **Effective dimensionality (PCA participation ratio)** is degenerate for n < d=768
  (covariance matrix rank ≤ n-1). The n=200 and n=500 points are reported but
  excluded from the convergence test.
- **Mean pairwise cosine** at n=10000 uses the full pairwise matrix (~800MB).
  If memory becomes tight on rerun, fall back to a 50K random pair sample.
- **Demographic Shannon** is the lightweight check on `first_country`. Full
  demographic-feature suite (gender, career-stage, prestige, joint Rao Q) is
  Stage-1 work, not Phase-0.1.

## Decision (per Phase 0.1 plan §1723-1727)

The N_target values above are committed for Phase 0.2 pre-registration as
the per-metric bootstrap-sample-size constants. Per-year bootstrap n =
min(Nᵧ, N_target). For metrics that did not converge by the largest n
in this sweep, Phase 0.2 locks min(Nᵧ, max-n-in-sweep) with a documented
caveat.

## Artifacts

- `experiments/phase-0.1/metric-convergence{suffix}.csv` — per-metric per-n means + SD.
- `experiments/phase-0.1/metric-convergence{suffix}.png` — 4-panel plot (created in
  next step if matplotlib available).
- `data/metadata/check5bd-pull-2024-cs{suffix}.parquet` — 5b pull source.
- `experiments/phase-0.1/check5bd-embeddings-specter2{suffix}.parquet` — embeddings.
"""
    md_path = _OUT_DIR / f"metric-convergence{suffix}.md"
    md_path.write_text(body)
    print(f"  wrote {md_path}")


def _write_cluster_stratification(
    h7_df: pd.DataFrame, h7_raw: dict[int, dict[str, Any]],
    s_df: pd.DataFrame, u_df: pd.DataFrame,
    h1975_df: pd.DataFrame, h2020_df: pd.DataFrame,
    snapshot: str, smoke: bool, k_primary: int,
) -> None:
    suffix = "-smoke" if smoke else ""
    csv_path = _OUT_DIR / f"cluster-stratification-check{suffix}.csv"
    h7_df.to_csv(csv_path, index=False)
    print(f"  wrote {csv_path} ({len(h7_df)} rows)")

    primary = h7_df[h7_df["k"] == k_primary].iloc[0]
    artifact_present = bool(primary["artifact_present_1975"])
    validates = bool(primary["validates_section_11"])

    if validates:
        verdict = "**§11 VALIDATED.** "
        rationale = (
            f"H_1975 effN ratio (S/U) = {primary['h1975_S_over_U_ratio']:.2f} "
            f">{_H7_ARTIFACT_RATIO} (artifact present); H_2020 relative diff = "
            f"{primary['h2020_relative_diff']:.1%} <{_H7_NEGATIVE_CONTROL_TOL:.0%} "
            f"(artifact absent on negative control). The decade-stratified fit "
            f"prevents the modern-cluster-dominance artifact for pre-1990 papers."
        )
    elif not artifact_present:
        verdict = "**§11 NOT VALIDATED — artifact ratio below threshold.** "
        rationale = (
            f"H_1975 effN ratio = {primary['h1975_S_over_U_ratio']:.2f}, "
            f"below the pre-registered ≥{_H7_ARTIFACT_RATIO} threshold. "
            f"Either the artifact is smaller than feared, or K=50 is too coarse "
            f"to surface it. Plan revision warranted."
        )
    else:
        verdict = "**§11 NOT VALIDATED — negative control failed.** "
        rationale = (
            f"H_1975 effN ratio = {primary['h1975_S_over_U_ratio']:.2f} (artifact "
            f"present), but H_2020 relative diff = {primary['h2020_relative_diff']:.1%} "
            f">{_H7_NEGATIVE_CONTROL_TOL:.0%} (negative control failed). "
            f"Stratification ALSO affects modern data, suggesting general cluster-fit "
            f"instability. Plan revision warranted."
        )

    # Robustness sweep across K
    robustness_rows = "\n".join(
        f"| {int(r['k'])} | {r['effN_S_H1975']:.2f} | {r['effN_U_H1975']:.2f} | "
        f"{r['h1975_S_over_U_ratio']:.2f} | {r['effN_S_H2020']:.2f} | "
        f"{r['effN_U_H2020']:.2f} | {r['h2020_relative_diff']:.1%} | "
        f"{'YES' if r['validates_section_11'] else 'NO'} |"
        for _, r in h7_df.iterrows()
    )

    s_per_decade = s_df.groupby("pull_decade").size().to_dict()
    pct_concentration = 100 * (
        1 - primary["effN_U_H1975"] / primary["effN_S_H1975"]
    )
    u_decade_counts = (
        u_df["publication_year"].apply(lambda y: 10 * (int(y) // 10))
        .value_counts().sort_index().to_dict()
    )

    body = f"""# Check 5d — Cluster-fit stratification artifact{' (SMOKE)' if smoke else ''}

**Run date:** {datetime.now(timezone.utc).date().isoformat()}
**Snapshot:** {snapshot}
**Mode:** {'smoke' if smoke else 'full'}
**Methodology (per Phase 0.1 plan §11):** Fit K-means clusters twice on the
same embedding space at the same K — once on a temporally-stratified pool S
(equal papers per decade) and once on an unstratified Nᵧ-proportional pool U
(same total N as S). Assign held-out 1975 and 2020 papers to clusters from
each fit. Compare assignment-distribution concentration via effective number
of clusters `effN(p) = exp(H(p))` and `KL(p || uniform)`.

## Pool composition

| Pool | N | Year distribution |
|---|---:|---|
| Stratified S | {len(s_df)} | per-decade: {s_per_decade} |
| Unstratified U | {len(u_df)} | per-decade: {u_decade_counts} |
| Held-out 1975 | {len(h1975_df)} | year=1975 only |
| Held-out 2020 | {len(h2020_df)} | year=2020 only |

## Pre-registered H7 thresholds

- **Artifact present (H_1975):** effN_S / effN_U > {_H7_ARTIFACT_RATIO}.
- **Artifact absent (H_2020 negative control):**
  |effN_S - effN_U| / max(effN_S, effN_U) < {_H7_NEGATIVE_CONTROL_TOL:.0%}.
- **§11 validated:** both conditions hold at K={k_primary}.

## Headline at K={k_primary}

{verdict}

{rationale}

## Robustness sweep across K

| K | effN_S(1975) | effN_U(1975) | S/U | effN_S(2020) | effN_U(2020) | rel.diff | §11? |
|---:|----------:|----------:|----:|----------:|----------:|------:|---|
{robustness_rows}

## Methods-section magnitude statement

At K={k_primary}, the unstratified-fit effective cluster count for held-out
1975 papers is {primary['effN_U_H1975']:.1f} ({pct_concentration:.0f}% fewer
than the stratified-fit effective count of {primary['effN_S_H1975']:.1f}).
This quantifies the "modern-cluster dominance" artifact §11's stratification
prevents for pre-1990 papers.

## Artifacts

- `experiments/phase-0.1/cluster-stratification-check{suffix}.csv` — per-K H7 metrics.
- `data/metadata/cluster-fit-manifest-{{S,U}}-K{{30,50,100}}{suffix}.npy` — centroid arrays.
- `data/metadata/cluster-fit-manifest{suffix}.md` — per-§11 manifest.
"""
    md_path = _OUT_DIR / f"cluster-stratification-check{suffix}.md"
    md_path.write_text(body)
    print(f"  wrote {md_path}")


def _write_plot(sweep: pd.DataFrame, smoke: bool) -> None:
    """4-panel convergence plot."""
    try:
        import matplotlib  # noqa: F401
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("  matplotlib not available; skipping plot")
        return

    suffix = "-smoke" if smoke else ""
    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    metrics = sweep["metric"].unique()
    axes_flat = axes.flatten()
    for ax, metric in zip(axes_flat, metrics):
        sub = sweep[sweep["metric"] == metric]
        ax.errorbar(sub["n"], sub["mean"], yerr=sub["sd"],
                    fmt="o-", capsize=3, capthick=1.5)
        ax.set_xscale("log")
        ax.set_xlabel("n (subsample size)")
        ax.set_ylabel(f"{metric} (mean ± SD over {_N_SUBSAMPLES} subsamples)")
        ax.set_title(metric)
        ax.grid(True, alpha=0.3)
        # Mark degenerate region for effective_dim
        if metric == "effective_dim":
            ax.axvspan(0, _PCA_DEGENERACY_FLOOR, alpha=0.15, color="gray",
                       label=f"n<d={_PCA_DEGENERACY_FLOOR} degenerate")
            ax.legend(loc="best", fontsize=8)
    fig.suptitle(
        f"Check 5b — semantic-diversity metric convergence "
        f"(cs {_FULL_5B_YEAR}{', SMOKE' if smoke else ''})"
    )
    fig.tight_layout()
    out = _OUT_DIR / f"metric-convergence{suffix}.png"
    fig.savefig(out, dpi=120)
    plt.close(fig)
    print(f"  wrote {out}")


# ---------- main ----------


def main(smoke: bool = False) -> None:
    mode_label = "SMOKE" if smoke else "FULL"
    print(f"Checks 5b + 5d — Metric convergence + cluster-fit stratification ({mode_label} mode)")
    print(f"  out_dir: {_OUT_DIR}")
    print(f"  device: {_DEVICE}; dtype: {_DTYPE}")
    print()

    print("[1/6] OpenAlex pulls...")
    q5b_df, s_df, u_df, h1975_df, h2020_df, summary = _do_pulls(smoke)
    print(
        f"  collected: |Q_5b|={summary['Q_5b_n']}, "
        f"|S|={summary['S_n']}, |U|={summary['U_n']}, "
        f"|H_1975|={summary['H_1975_n']}, |H_2020|={summary['H_2020_n']}"
    )
    print()

    print("[2/6] Layer A pipeline-correctness checks (H1, H2)...")
    target_5b = _SMOKE_5B_TARGET_N if smoke else _FULL_5B_TARGET_N
    target_decade = _SMOKE_5D_PER_DECADE_TARGET if smoke else _FULL_5D_PER_DECADE_TARGET
    target_heldout = _SMOKE_5D_HELDOUT_TARGET if smoke else _FULL_5D_HELDOUT_TARGET
    _assert_h1_5b(q5b_df, target_5b)
    _assert_h2_5d(s_df, u_df, h1975_df, h2020_df, target_decade, target_heldout)
    _write_pulls(q5b_df, s_df, u_df, h1975_df, h2020_df, smoke)
    print()

    print("[3/6] SPECTER2 embedding (H3 inline)...")
    embeddings = _do_embeddings(q5b_df, s_df, u_df, h1975_df, h2020_df)
    _write_embeddings(q5b_df, s_df, u_df, h1975_df, h2020_df, embeddings, smoke)
    print()

    if smoke:
        k_primary = _SMOKE_K_PRIMARY
        k_robustness = _SMOKE_K_ROBUSTNESS
    else:
        k_primary = _K_PRIMARY
        k_robustness = _K_ROBUSTNESS
    k_values: tuple[int, ...] = tuple(sorted({*k_robustness, k_primary}))
    print(f"[4/6] §11 H7 cluster-stratification analysis (K ∈ {set(k_values)})...")
    h7_df, h7_raw = _do_5d_h7(embeddings, k_values)
    print(f"  K values: {k_values}")
    print(h7_df[["k", "effN_S_H1975", "effN_U_H1975", "h1975_S_over_U_ratio",
                 "effN_S_H2020", "effN_U_H2020", "h2020_relative_diff",
                 "validates_section_11"]].to_string(index=False))
    _write_cluster_manifest(h7_raw, s_df, u_df, smoke)
    print()

    print("[5/6] 5b convergence sweep (4 metrics × n values × subsamples)...")
    centroids_S_primary = h7_raw[k_primary]["centroids_S"]
    sweep = _do_5b_convergence(
        q5b_df, embeddings, centroids_S_primary,
        _CONVERGENCE_N_VALUES, _DEMOGRAPHIC_N_VALUES,
    )
    print()

    print("[6/6] Artifact writing + decision capture...")
    _write_metric_convergence(sweep, len(q5b_df), summary["snapshot"], smoke)
    _write_cluster_stratification(
        h7_df, h7_raw, s_df, u_df, h1975_df, h2020_df,
        summary["snapshot"], smoke, k_primary,
    )
    _write_plot(sweep, smoke)
    print()

    # Print headline decisions
    print("DECISIONS:")
    print()
    print("  5b N_targets per metric:")
    for metric in sweep["metric"].unique():
        sub = sweep[sweep["metric"] == metric]
        n_target, rationale = _identify_n_target(sub)
        print(f"    {metric}: N_target={n_target} ({rationale})")
    print()
    print(f"  5d §11 H7 (at K={k_primary}):")
    primary = h7_df[h7_df["k"] == k_primary].iloc[0]
    print(
        f"    effN_S(H_1975)={primary['effN_S_H1975']:.2f}, "
        f"effN_U(H_1975)={primary['effN_U_H1975']:.2f}, "
        f"ratio={primary['h1975_S_over_U_ratio']:.2f}"
    )
    print(
        f"    effN_S(H_2020)={primary['effN_S_H2020']:.2f}, "
        f"effN_U(H_2020)={primary['effN_U_H2020']:.2f}, "
        f"rel_diff={primary['h2020_relative_diff']:.1%}"
    )
    print(
        f"    artifact_present_1975={primary['artifact_present_1975']}, "
        f"artifact_absent_2020={primary['artifact_absent_2020']}"
    )
    print(
        f"    validates_section_11={primary['validates_section_11']}"
    )
    print()
    print(f"Checks 5b + 5d {mode_label} complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true", help="run with toy inputs")
    args = parser.parse_args()
    main(smoke=args.smoke)
    sys.exit(0)
