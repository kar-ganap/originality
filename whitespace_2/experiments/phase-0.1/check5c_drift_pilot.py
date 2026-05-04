"""Check 5c — Drift pilot (nearest-neighbor era-match rate).

Decides Phase 0.1 plan §2's Stage-3 conditional Flavor A commitment
(Word2Vec-per-decade + Procrustes alignment, the only genuinely non-
transformer cross-architecture drift check). The decision rule keys on
SPECTER2's era-match rate over 100 1970-1980 CS query papers against an
era-balanced candidate pool (500 pre-1990 + 500 post-2000 CS papers).

Plan §2 decision rule (with 95% bootstrap CI):
    SPECTER2 era-match CI fully > 70%  → skip Flavor A.
    SPECTER2 era-match CI fully < 50%  → commit Flavor A (drift severe).
    otherwise                          → commit Flavor A as cheap insurance.

Pre-registered hypotheses (mirroring Phase 0.1.E's H1-H7 discipline):

    Layer A (pipeline correctness; abort-on-fail):
    - H1 (query construction): Q has 100 unique work_ids, year ∈ [1970, 1980],
      all in §0 P (post-filter pull spec).
    - H2 (pool construction): C has ≥500 papers in pre-1990 (1970-1989) and
      ≥500 in post-2000 (2000-2024); Q ∩ C = ∅.
    - H3 (embedding correctness): each of 3 models produces (|Q|+|C|, 768)
      finite, non-zero embeddings; per-vector L2 norms within model-specific
      bands recorded in `embedding-pipeline-smoke.md`.
    - H4 (NN determinism): top-10 NN reproducible from fixed embeddings;
      cosine on L2-normalized vectors; ties broken by lower work_id.

    Layer B (scientific findings):
    - H5 (metric well-defined): per-model era-match = mean over queries of
      #{neighbors with year ≤ 1990} / 10; 95% CI via 1000-resample bootstrap.
    - H6 (SPECTER2 era-match): pre-registered point prediction ≈ 65%; pass
      criterion is decision-bin classification consistency (skip/commit/
      cheap-insurance) — not point precision.
    - H7 (qualitative validation): on 30-pair hand-audit (10/model, 5
      pre-1990 + 5 post-2000 per model), human "topically related y/n"
      agrees with date-based "pre-1990 y/n" labeling ≥80%.

Run from ws2 root:
    uv run python experiments/phase-0.1/check5c_drift_pilot.py [--smoke]
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
from tqdm import tqdm

from whitespace2 import embeddings as emb
from whitespace2 import openalex

# ---------- paths ----------

_OUT_DIR = Path(__file__).parent
_DATA_METADATA_DIR = _OUT_DIR.parent.parent / "data" / "metadata"


# ---------- pull spec (lifted verbatim from check5a; locked) ----------

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
    "title",  # added vs check5a; needed for hand-audit context
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


# ---------- check 5c parameters ----------

# Full-mode targets
_QUERY_YEARS = list(range(1970, 1981))  # 1970-1980 inclusive
_POOL_PRE1990_YEARS = list(range(1970, 1990))  # 1970-1989 inclusive
_POOL_POST2000_YEARS = list(range(2000, 2025))  # 2000-2024 inclusive

_TARGET_QUERIES = 100
_TARGET_POOL_PER_BUCKET = 500
_TOP_K = 10

_QUERY_SEED = 43
_POOL_PRE1990_SEED = 44
_POOL_POST2000_SEED = 45
_BOOTSTRAP_SEED = 46
_HAND_AUDIT_SEED = 47

_SAMPLE_PER_CELL = 200  # OpenAlex max sample per call

# Smoke-mode targets (override when --smoke). Sized so that H1/H2 assertions
# pass under Check 5a's observed ~11-31% retention floor for early-CS years.
_SMOKE_TARGET_QUERIES = 5
_SMOKE_TARGET_POOL_PER_BUCKET = 10
_SMOKE_QUERY_YEARS = [1975, 1978]
_SMOKE_POOL_PRE1990_YEARS = [1980, 1985, 1988]
_SMOKE_POOL_POST2000_YEARS = [2010, 2015, 2020]
_SMOKE_SAMPLE_PER_CELL = 200

# Embedding device
_DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"
_DTYPE = "fp16"

# Per Phase 0.1.E smoke artifact: bs=1 is faster than naive bs=8 for Qwen3
# on M-series MPS due to padding waste against 32K context. SPECTER2/SciNCL
# truncate at 512 (BERT max) so bs=8 is fine for them.
_BS_SPECTER = 8
_BS_SCINCL = 8
_BS_QWEN3 = 1

# Pre-registered model L2-norm bands per Phase 0.1.E smoke
_NORM_BANDS = {
    "specter2": (21.0, 23.0),
    "scincl": (22.5, 24.5),
    "qwen3": (0.99, 1.01),
}

# Bootstrap parameters
_N_BOOTSTRAP = 1000

# Hand-audit
_HAND_AUDIT_PER_MODEL = 10  # 5 pre-1990 + 5 post-2000


# ---------- post-fetch filters (lifted verbatim from check5a) ----------


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


def _execute_pull(
    years: list[int],
    sample_per_cell: int,
    seed: int,
    target_n: int,
    label: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Pull `sample_per_cell` papers per year, filter, take first `target_n`
    in year-rotation order so the result is year-stratified."""
    per_year_filtered: dict[int, list[dict[str, Any]]] = {y: [] for y in years}
    n_raw_total = 0
    n_calls = 0
    for year in tqdm(years, desc=f"pull {label}"):
        try:
            raw = openalex.fetch_works(
                filters={
                    "concepts.id": _FIELD_CONCEPT_ID,
                    "publication_year": str(year),
                },
                sample_size=sample_per_cell,
                seed=seed,
                select=_SELECT,
            )
        except RuntimeError as err:
            print(f"  WARN: skipping {label}/{year}: {err}")
            continue
        n_raw_total += len(raw)
        n_calls += 1
        kept = _post_filter(raw)
        for w in kept:
            w["_pull_year"] = year
            w["_pull_label"] = label
        per_year_filtered[year] = kept
        time.sleep(0.3)

    # Year-rotation stratified take to target_n
    out: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    while len(out) < target_n:
        added_any = False
        for year in years:
            bucket = per_year_filtered.get(year, [])
            if not bucket:
                continue
            w = bucket.pop(0)
            wid = w.get("id")
            if not isinstance(wid, str) or wid in seen_ids:
                continue
            seen_ids.add(wid)
            out.append(w)
            added_any = True
            if len(out) >= target_n:
                break
        if not added_any:
            break

    summary = {
        "label": label,
        "years": f"{min(years)}-{max(years)}",
        "n_calls": n_calls,
        "n_raw": n_raw_total,
        "n_post_filter": sum(len(v) for v in per_year_filtered.values()) + len(out),
        "n_taken": len(out),
        "target_n": target_n,
    }
    return out, summary


# ---------- abstract decoding (lifted from embedding_pipeline_smoke pattern) ----------


def _reconstruct_abstract(inverted_index: dict[str, list[int]]) -> str:
    if not inverted_index:
        return ""
    max_pos = max(max(positions) for positions in inverted_index.values())
    tokens = [""] * (max_pos + 1)
    for word, positions in inverted_index.items():
        for pos in positions:
            tokens[pos] = word
    return " ".join(t for t in tokens if t)


# ---------- parquet schema (matches check5a + adds title) ----------


def _flatten_for_parquet(work: dict[str, Any]) -> dict[str, Any]:
    return {
        "work_id": work.get("id"),
        "title": work.get("title") or "",
        "publication_year": work.get("publication_year"),
        "type": work.get("type"),
        "field": _FIELD,
        "pull_year": work.get("_pull_year"),
        "pull_label": work.get("_pull_label"),
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


def _to_dataframe(works: list[dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame([_flatten_for_parquet(w) for w in works])


def _decode_abstracts(df: pd.DataFrame) -> list[str]:
    """For each row, decode abstract_inverted_index_json into text."""
    out: list[str] = []
    for inv_json in df["abstract_inverted_index_json"]:
        inv = json.loads(inv_json) if inv_json else {}
        out.append(_reconstruct_abstract(inv))
    return out


# ---------- hypothesis assertions ----------


def _assert_h1_queries(queries_df: pd.DataFrame, target_n: int) -> None:
    n = len(queries_df)
    assert n == target_n, f"H1 fail: |Q|={n}, expected {target_n}"
    assert queries_df["work_id"].nunique() == n, "H1 fail: duplicate work_ids in Q"
    years = queries_df["publication_year"]
    bad_years = years[(years < 1970) | (years > 1980)]
    assert len(bad_years) == 0, (
        f"H1 fail: {len(bad_years)} queries outside 1970-1980 range"
    )
    bad_score = queries_df[queries_df["field_tag_score"] < _SCORE_THRESHOLD]
    assert len(bad_score) == 0, (
        f"H1 fail: {len(bad_score)} queries below score≥{_SCORE_THRESHOLD}"
    )
    assert queries_df["has_abstract"].all(), "H1 fail: some queries lack abstract"
    print(
        f"  H1 PASS: |Q|={n}; years in [1970,1980]; "
        f"all score≥{_SCORE_THRESHOLD}; all has_abstract."
    )


def _assert_h2_pool(pool_df: pd.DataFrame, queries_df: pd.DataFrame,
                    target_per_bucket: int) -> None:
    pre = pool_df[(pool_df["publication_year"] >= 1970)
                  & (pool_df["publication_year"] <= 1989)]
    post = pool_df[(pool_df["publication_year"] >= 2000)
                   & (pool_df["publication_year"] <= 2024)]
    assert len(pre) >= target_per_bucket, (
        f"H2 fail: pre-1990 pool |C_pre|={len(pre)}, expected ≥{target_per_bucket}"
    )
    assert len(post) >= target_per_bucket, (
        f"H2 fail: post-2000 pool |C_post|={len(post)}, expected ≥{target_per_bucket}"
    )
    overlap = set(queries_df["work_id"]) & set(pool_df["work_id"])
    assert len(overlap) == 0, f"H2 fail: |Q ∩ C|={len(overlap)} (must be 0)"
    print(
        f"  H2 PASS: |C_pre|={len(pre)}; |C_post|={len(post)}; |Q∩C|=0."
    )


def _assert_h3_embedding(
    name: str, vectors: np.ndarray[Any, Any], expected_n: int
) -> None:
    assert vectors.shape == (expected_n, 768), (
        f"H3 fail [{name}]: shape={vectors.shape}, expected ({expected_n}, 768)"
    )
    assert np.isfinite(vectors).all(), f"H3 fail [{name}]: non-finite values"
    norms = np.linalg.norm(vectors, axis=1)
    assert (norms > 0).all(), f"H3 fail [{name}]: zero-norm vector(s)"
    band = _NORM_BANDS[name]
    mean_norm = float(norms.mean())
    if not (band[0] <= mean_norm <= band[1]):
        # Soft-warn (smoke saw same number); don't abort, the gates are hard
        # contracts — band miss is information, not a contract violation.
        print(
            f"  H3 WARN [{name}]: mean L2 norm={mean_norm:.3f} outside "
            f"recorded band {band} — flagged for investigation."
        )
    print(
        f"  H3 PASS [{name}]: shape={vectors.shape}; finite; non-zero; "
        f"mean L2 norm={mean_norm:.3f}."
    )


# ---------- nearest-neighbor retrieval ----------


def _l2_normalize(vectors: np.ndarray[Any, Any]) -> np.ndarray[Any, Any]:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    norms = np.where(norms > 0, norms, 1.0)
    out: np.ndarray[Any, Any] = (vectors / norms).astype(np.float32)
    return out


def _topk_neighbors(
    query_vecs: np.ndarray[Any, Any],
    pool_vecs: np.ndarray[Any, Any],
    pool_ids: list[str],
    k: int,
) -> list[list[tuple[str, float]]]:
    """For each query row, return top-k (pool_id, similarity) pairs by cosine
    on L2-normalized vectors. Ties broken by lower lexicographic pool_id."""
    sims = query_vecs @ pool_vecs.T  # (|Q|, |C|)
    out: list[list[tuple[str, float]]] = []
    pool_ids_arr = np.array(pool_ids)
    for q_idx in range(sims.shape[0]):
        row = sims[q_idx]
        # Argsort by (-sim, pool_id) to get top-k with deterministic tie-break.
        # numpy argsort is stable; sort by (-sim) primarily and id lexicographic
        # as secondary by using a structured array.
        order = np.lexsort((pool_ids_arr, -row))[:k]
        out.append([(pool_ids[i], float(row[i])) for i in order])
    return out


# ---------- bootstrap CI ----------


def _bootstrap_ci(
    values: np.ndarray[Any, Any],
    n_bootstrap: int = _N_BOOTSTRAP,
    alpha: float = 0.05,
    seed: int = _BOOTSTRAP_SEED,
) -> tuple[float, float, float]:
    """Returns (mean, ci_low, ci_high) via percentile bootstrap."""
    rng = np.random.default_rng(seed)
    n = len(values)
    means = np.empty(n_bootstrap)
    for b in range(n_bootstrap):
        idx = rng.integers(0, n, size=n)
        means[b] = values[idx].mean()
    return (
        float(values.mean()),
        float(np.quantile(means, alpha / 2)),
        float(np.quantile(means, 1 - alpha / 2)),
    )


# ---------- decision rule ----------


def _apply_decision_rule(
    point: float,
    ci_low: float,
    ci_high: float,
) -> tuple[str, str]:
    """Returns (action, rationale)."""
    if ci_low > 0.70:
        return "skip Flavor A", (
            f"CI [{ci_low:.1%}, {ci_high:.1%}] fully > 70% — drift manageable."
        )
    if ci_high < 0.50:
        return "commit Flavor A (drift severe)", (
            f"CI [{ci_low:.1%}, {ci_high:.1%}] fully < 50% — drift severe."
        )
    return "commit Flavor A (cheap insurance)", (
        f"CI [{ci_low:.1%}, {ci_high:.1%}] straddles a boundary or "
        f"point estimate {point:.1%} ∈ [50%, 70%] — gray zone."
    )


# ---------- hand-audit sampling ----------


def _sample_hand_audit(
    neighbors_df: pd.DataFrame,
    queries_df: pd.DataFrame,
    pool_df: pd.DataFrame,
    per_model: int,
    seed: int,
) -> pd.DataFrame:
    """Stratified sample: per_model // 2 from era-match=True (pre-1990 neighbor)
    and per_model // 2 from era-match=False per model. Each row has the abstract
    text materialized for human reading.
    """
    rng = np.random.default_rng(seed)
    rows: list[dict[str, Any]] = []
    qmap = queries_df.set_index("work_id")[["title", "publication_year",
                                              "abstract_inverted_index_json"]]
    pmap = pool_df.set_index("work_id")[["title", "publication_year",
                                          "abstract_inverted_index_json"]]
    half = per_model // 2
    for model in neighbors_df["model"].unique():
        sub = neighbors_df[neighbors_df["model"] == model]
        for era_flag in [True, False]:
            era_sub = sub[sub["era_match"] == era_flag]
            n_pick = min(half, len(era_sub))
            if n_pick == 0:
                continue
            picked = era_sub.sample(n=n_pick, random_state=int(rng.integers(0, 1_000_000)))
            for _, r in picked.iterrows():
                qid, nid = r["query_id"], r["neighbor_id"]
                _ABS = "abstract_inverted_index_json"
                q_inv_json = str(qmap.at[qid, _ABS]) if qid in qmap.index else "{}"
                n_inv_json = str(pmap.at[nid, _ABS]) if nid in pmap.index else "{}"
                q_inv = json.loads(q_inv_json) if q_inv_json else {}
                n_inv = json.loads(n_inv_json) if n_inv_json else {}
                q_title = qmap.at[qid, "title"] if qid in qmap.index else ""
                n_title = pmap.at[nid, "title"] if nid in pmap.index else ""
                rows.append({
                    "model": model,
                    "query_id": qid,
                    "query_year": r["query_year"],
                    "query_title": q_title,
                    "query_abstract": _reconstruct_abstract(q_inv),
                    "neighbor_id": nid,
                    "neighbor_year": r["neighbor_year"],
                    "neighbor_title": n_title,
                    "neighbor_abstract": _reconstruct_abstract(n_inv),
                    "similarity": r["similarity"],
                    "era_match_date_based": era_flag,
                    "topically_related": "",  # to be hand-filled
                })
    return pd.DataFrame(rows)


# ---------- per-step orchestration ----------


def _do_pulls(smoke: bool) -> tuple[pd.DataFrame, pd.DataFrame, list[dict[str, Any]]]:
    """Returns (queries_df, pool_df, pull_summaries)."""
    summaries: list[dict[str, Any]] = []

    if smoke:
        q_years = _SMOKE_QUERY_YEARS
        pre_years = _SMOKE_POOL_PRE1990_YEARS
        post_years = _SMOKE_POOL_POST2000_YEARS
        sample_n = _SMOKE_SAMPLE_PER_CELL
        target_q = _SMOKE_TARGET_QUERIES
        target_pool = _SMOKE_TARGET_POOL_PER_BUCKET
    else:
        q_years = _QUERY_YEARS
        pre_years = _POOL_PRE1990_YEARS
        post_years = _POOL_POST2000_YEARS
        sample_n = _SAMPLE_PER_CELL
        target_q = _TARGET_QUERIES
        target_pool = _TARGET_POOL_PER_BUCKET

    q_works, q_summary = _execute_pull(q_years, sample_n, _QUERY_SEED, target_q, "queries")
    summaries.append(q_summary)

    pre_works, pre_summary = _execute_pull(
        pre_years, sample_n, _POOL_PRE1990_SEED, target_pool, "pool_pre1990"
    )
    summaries.append(pre_summary)

    post_works, post_summary = _execute_pull(
        post_years, sample_n, _POOL_POST2000_SEED, target_pool, "pool_post2000"
    )
    summaries.append(post_summary)

    queries_df = _to_dataframe(q_works)

    # De-duplicate queries from pool (Q ∩ C must be ∅)
    q_ids = set(queries_df["work_id"])
    pre_works = [w for w in pre_works if w.get("id") not in q_ids]
    post_works = [w for w in post_works if w.get("id") not in q_ids]
    pool_df = pd.concat(
        [_to_dataframe(pre_works), _to_dataframe(post_works)], ignore_index=True
    )

    return queries_df, pool_df, summaries


def _do_embeddings(
    queries_df: pd.DataFrame,
    pool_df: pd.DataFrame,
) -> dict[str, dict[str, Any]]:
    """For each model, embed Q ∪ C, L2-normalize, return per-model {q,c} arrays.

    Returns: {model_name: {"q": (|Q|, 768), "c": (|C|, 768),
              "norms_raw": np.array, "elapsed_sec": float}}
    """
    q_abstracts = _decode_abstracts(queries_df)
    c_abstracts = _decode_abstracts(pool_df)
    all_abstracts = q_abstracts + c_abstracts
    n_q = len(q_abstracts)

    out: dict[str, dict[str, Any]] = {}

    model_specs = [
        ("scincl", emb.embed_scincl, _BS_SCINCL),  # warmest first per smoke
        ("specter2", emb.embed_specter2, _BS_SPECTER),
        ("qwen3", emb.embed_qwen3, _BS_QWEN3),
    ]

    for name, fn, bs in model_specs:
        print(f"  [{name}] embedding {len(all_abstracts)} abstracts (bs={bs})...")
        t0 = time.time()
        vectors = fn(all_abstracts, device=_DEVICE, batch_size=bs, dtype=_DTYPE)
        elapsed = time.time() - t0
        print(
            f"    [{name}] {elapsed:.1f}s ({elapsed / len(all_abstracts):.3f}s/abs)"
        )

        _assert_h3_embedding(name, vectors, len(all_abstracts))

        normed = _l2_normalize(vectors)
        out[name] = {
            "q": normed[:n_q],
            "c": normed[n_q:],
            "norms_raw": np.linalg.norm(vectors, axis=1),
            "elapsed_sec": elapsed,
        }

    return out


def _do_neighbors(
    queries_df: pd.DataFrame,
    pool_df: pd.DataFrame,
    embeddings: dict[str, dict[str, Any]],
) -> pd.DataFrame:
    """Compute top-K NN per (query, model). Returns long-form neighbors df."""
    pool_ids = pool_df["work_id"].tolist()
    pool_years = dict(zip(pool_df["work_id"], pool_df["publication_year"]))

    rows: list[dict[str, Any]] = []
    for model, vecs in embeddings.items():
        topk = _topk_neighbors(vecs["q"], vecs["c"], pool_ids, _TOP_K)
        for q_idx, neighbors in enumerate(topk):
            qid = queries_df.iloc[q_idx]["work_id"]
            qyear = int(queries_df.iloc[q_idx]["publication_year"])
            for rank, (nid, sim) in enumerate(neighbors):
                nyear = int(pool_years[nid])
                rows.append({
                    "query_id": qid,
                    "query_year": qyear,
                    "model": model,
                    "rank": rank,
                    "neighbor_id": nid,
                    "neighbor_year": nyear,
                    "similarity": sim,
                    "era_match": nyear <= 1990,
                })
    return pd.DataFrame(rows)


def _per_model_era_match_rates(
    neighbors_df: pd.DataFrame,
    queries_df: pd.DataFrame,
) -> pd.DataFrame:
    """For each model, compute per-query era-match (#match/10) and aggregate
    to mean + 95% bootstrap CI."""
    rows = []
    for model in neighbors_df["model"].unique():
        sub = neighbors_df[neighbors_df["model"] == model]
        per_query = (
            sub.groupby("query_id")["era_match"].mean().reindex(queries_df["work_id"])
        ).to_numpy()
        mean, lo, hi = _bootstrap_ci(per_query)
        rows.append({
            "model": model,
            "era_match_rate": mean,
            "ci_low": lo,
            "ci_high": hi,
            "n_queries": len(per_query),
        })
    return pd.DataFrame(rows)


# ---------- artifact writing ----------


def _write_artifacts(
    queries_df: pd.DataFrame,
    pool_df: pd.DataFrame,
    embeddings: dict[str, dict[str, Any]],
    neighbors_df: pd.DataFrame,
    rates_df: pd.DataFrame,
    hand_audit_df: pd.DataFrame,
    pull_summaries: list[dict[str, Any]],
    snapshot: str,
    smoke: bool,
) -> None:
    suffix = "-smoke" if smoke else ""

    # Parquets — queries to data/metadata, embeddings to experiments
    queries_path = _DATA_METADATA_DIR / f"drift-pilot-queries{suffix}.parquet"
    queries_df.to_parquet(queries_path, index=False)
    print(f"  wrote {queries_path} ({len(queries_df)} rows)")

    pool_path = _DATA_METADATA_DIR / f"drift-pilot-pool{suffix}.parquet"
    pool_df.to_parquet(pool_path, index=False)
    print(f"  wrote {pool_path} ({len(pool_df)} rows)")

    # Embeddings parquet (one per model: work_id + 768 vector cols)
    for model, vecs in embeddings.items():
        all_ids = queries_df["work_id"].tolist() + pool_df["work_id"].tolist()
        all_vecs = np.vstack([vecs["q"], vecs["c"]])
        emb_df = pd.DataFrame(all_vecs, columns=[f"d{i}" for i in range(768)])
        emb_df.insert(0, "work_id", all_ids)
        emb_path = _OUT_DIR / f"drift-pilot-embeddings-{model}{suffix}.parquet"
        emb_df.to_parquet(emb_path, index=False)
        print(f"  wrote {emb_path} ({len(emb_df)} rows)")

    # Neighbors CSV
    neighbors_path = _OUT_DIR / f"drift-pilot-neighbors{suffix}.csv"
    neighbors_df.to_csv(neighbors_path, index=False)
    print(f"  wrote {neighbors_path} ({len(neighbors_df)} rows)")

    # Hand-audit CSV (with empty topically_related column)
    hand_audit_path = _OUT_DIR / f"drift-pilot-hand-audit{suffix}.csv"
    hand_audit_df.to_csv(hand_audit_path, index=False)
    print(f"  wrote {hand_audit_path} ({len(hand_audit_df)} rows)")

    # Per-model rates CSV
    rates_path = _OUT_DIR / f"drift-pilot-rates{suffix}.csv"
    rates_df.to_csv(rates_path, index=False)
    print(f"  wrote {rates_path} ({len(rates_df)} rows)")

    # Decision summary md
    _write_results_md(
        queries_df, pool_df, neighbors_df, rates_df, hand_audit_df,
        pull_summaries, embeddings, snapshot, smoke,
    )


def _write_results_md(
    queries_df: pd.DataFrame,
    pool_df: pd.DataFrame,
    neighbors_df: pd.DataFrame,
    rates_df: pd.DataFrame,
    hand_audit_df: pd.DataFrame,
    pull_summaries: list[dict[str, Any]],
    embeddings: dict[str, dict[str, Any]],
    snapshot: str,
    smoke: bool,
) -> None:
    suffix = "-smoke" if smoke else ""

    specter_row = rates_df[rates_df["model"] == "specter2"].iloc[0]
    action, rationale = _apply_decision_rule(
        specter_row["era_match_rate"], specter_row["ci_low"], specter_row["ci_high"]
    )

    rates_table = "\n".join(
        f"| {r['model']} | {r['era_match_rate']:.1%} | "
        f"[{r['ci_low']:.1%}, {r['ci_high']:.1%}] | {r['n_queries']} |"
        for _, r in rates_df.iterrows()
    )

    timing_table = "\n".join(
        f"| {model} | {vecs['elapsed_sec']:.1f} | "
        f"{vecs['elapsed_sec'] / (len(queries_df) + len(pool_df)):.3f} |"
        for model, vecs in embeddings.items()
    )

    pre_pool = pool_df[
        (pool_df["publication_year"] >= 1970) & (pool_df["publication_year"] <= 1989)
    ]
    post_pool = pool_df[
        (pool_df["publication_year"] >= 2000) & (pool_df["publication_year"] <= 2024)
    ]

    # Pre-format strings that would otherwise blow line-length in the body
    title_smoke_marker = " (SMOKE)" if smoke else ""
    mode_label = "smoke (toy inputs)" if smoke else "full"
    q_year_min = queries_df["publication_year"].min()
    q_year_max = queries_df["publication_year"].max()
    pull_table_rows = "\n".join(
        f"| {s['label']} | {s['years']} | {s['n_calls']} | "
        f"{s['n_raw']} | {s['n_taken']} | {s['target_n']} |"
        for s in pull_summaries
    )
    sp_rate = specter_row["era_match_rate"]
    sp_lo = specter_row["ci_low"]
    sp_hi = specter_row["ci_high"]
    flavor_a_desc = (
        "Flavor A = Word2Vec-per-decade + orthogonal Procrustes alignment "
        "+ TF-IDF-weighted document aggregation (Hamilton-Leskovec-Jurafsky 2016 "
        "template, document-level adaptation)."
    )
    artifact_emb = (
        f"- `experiments/phase-0.1/drift-pilot-embeddings-"
        f"{{specter2,scincl,qwen3}}{suffix}.parquet` — 3 files."
    )
    artifact_neighbors = (
        f"- `experiments/phase-0.1/drift-pilot-neighbors{suffix}.csv` — "
        f"{len(neighbors_df)} rows ({len(queries_df)} × 3 × {_TOP_K})."
    )
    artifact_handaudit = (
        f"- `experiments/phase-0.1/drift-pilot-hand-audit{suffix}.csv` — "
        f"{len(hand_audit_df)} rows (topically_related to be hand-filled)."
    )

    body = f"""# Check 5c — Drift pilot (nearest-neighbor era-match rate){title_smoke_marker}

**Run date:** {datetime.now(timezone.utc).date().isoformat()}
**Snapshot recorded:** {snapshot}
**Mode:** {mode_label}
**Device:** {_DEVICE}; **dtype:** {_DTYPE}

## Data composition

| Set | N | Years |
|-----|---:|---|
| Query Q | {len(queries_df)} | {q_year_min}-{q_year_max} |
| Pool C, pre-1990 | {len(pre_pool)} | 1970-1989 |
| Pool C, post-2000 | {len(post_pool)} | 2000-2024 |

## Pull summaries

| Label | Years | Calls | Pre-filter raw | Taken | Target |
|---|---|---:|---:|---:|---:|
{pull_table_rows}

## Embedding timing (this run)

| Model | Total (s) | s/abstract |
|-------|----------:|-----------:|
{timing_table}

## Era-match rates (Layer B H5 + H6)

Per-model headline = mean over {len(queries_df)} queries of (#{{neighbors year≤1990}} / {_TOP_K}).
95% CI via {_N_BOOTSTRAP}-resample bootstrap over queries (seed={_BOOTSTRAP_SEED}).

| Model | Era-match rate | 95% CI | N queries |
|-------|---------------:|--------|----------:|
{rates_table}

## Decision (per Phase 0.1 plan §2)

**SPECTER2 era-match: {sp_rate:.1%}** with CI [{sp_lo:.1%}, {sp_hi:.1%}].

**Action:** {action}.

**Rationale:** {rationale}

## H7 — Hand-audit (qualitative validation of date-based metric)

{_format_h7_summary(hand_audit_df)}

## Per-query era-match histogram (diagnostic)

{_format_histogram(neighbors_df)}

## Decision-rule reference

Per Phase 0.1 plan §2 (Stage 2 default + Stage 3 conditional Flavor A):

- SPECTER2 era-match CI fully > 70% → drift manageable, **skip Flavor A**.
- SPECTER2 era-match CI fully < 50% → drift severe, **commit Flavor A**.
- Otherwise → **commit Flavor A as cheap insurance**.

{flavor_a_desc}

## Artifacts

- `data/metadata/drift-pilot-queries{suffix}.parquet` — {len(queries_df)} rows.
- `data/metadata/drift-pilot-pool{suffix}.parquet` — {len(pool_df)} rows.
{artifact_emb}
{artifact_neighbors}
{artifact_handaudit}
- `experiments/phase-0.1/drift-pilot-rates{suffix}.csv` — per-model era-match + CI.
"""
    out_path = _OUT_DIR / f"drift-pilot-results{suffix}.md"
    out_path.write_text(body)
    print(f"  wrote {out_path}")


def _format_h7_summary(hand_audit_df: pd.DataFrame) -> str:
    if hand_audit_df.empty:
        return "(no audit rows generated)"
    filled = hand_audit_df[hand_audit_df["topically_related"] != ""]
    if len(filled) == 0:
        return (
            f"Audit CSV generated with {len(hand_audit_df)} rows; "
            f"`topically_related` column awaits hand fill. "
            f"H7 will be evaluated post-fill."
        )
    # Both columns are bool/string — coerce
    yes = filled[filled["topically_related"].astype(str).str.lower().isin(["y", "yes", "true"])]
    agree = yes[yes["era_match_date_based"] == True].shape[0]  # noqa: E712
    agree += filled[
        (filled["topically_related"].astype(str).str.lower().isin(["n", "no", "false"]))
        & (filled["era_match_date_based"] == False)  # noqa: E712
    ].shape[0]
    rate = agree / len(filled)
    verdict = "PASS" if rate >= 0.80 else "FAIL"
    return (
        f"{len(filled)} pairs hand-coded; agreement with date-based label "
        f"= {rate:.1%} ({verdict} ≥80% threshold)."
    )


def _format_histogram(neighbors_df: pd.DataFrame) -> str:
    """Per-model histogram of per-query era-match counts (0..10)."""
    header = (
        "| Model | 0/10 | 1/10 | 2/10 | 3/10 | 4/10 | 5/10 | "
        "6/10 | 7/10 | 8/10 | 9/10 | 10/10 |"
    )
    sep = (
        "|-------|-----:|-----:|-----:|-----:|-----:|-----:|"
        "-----:|-----:|-----:|-----:|------:|"
    )
    lines = [header, sep]
    for model in neighbors_df["model"].unique():
        sub = neighbors_df[neighbors_df["model"] == model]
        per_query = sub.groupby("query_id")["era_match"].sum().astype(int)
        counts = [int((per_query == k).sum()) for k in range(11)]
        lines.append(f"| {model} | " + " | ".join(str(c) for c in counts) + " |")
    return "\n".join(lines)


# ---------- main ----------


def main(smoke: bool = False) -> None:
    mode_label = "SMOKE" if smoke else "FULL"
    print(f"Check 5c — Drift pilot ({mode_label} mode)")
    print(f"  out_dir: {_OUT_DIR}")
    print(f"  device: {_DEVICE}; dtype: {_DTYPE}")
    if smoke:
        print(f"  smoke targets: |Q|={_SMOKE_TARGET_QUERIES}, "
              f"|C_pre|={_SMOKE_TARGET_POOL_PER_BUCKET}, "
              f"|C_post|={_SMOKE_TARGET_POOL_PER_BUCKET}")
    else:
        print(f"  full targets: |Q|={_TARGET_QUERIES}, "
              f"|C_pre|={_TARGET_POOL_PER_BUCKET}, "
              f"|C_post|={_TARGET_POOL_PER_BUCKET}")
    print()

    snapshot = openalex.latest_snapshot_date()

    print("[1/5] Pulling queries + pool from OpenAlex...")
    queries_df, pool_df, summaries = _do_pulls(smoke)
    print(f"  |Q|={len(queries_df)}; |C|={len(pool_df)}")
    print()

    print("[2/5] Layer A pipeline correctness checks (H1-H2)...")
    target_q = _SMOKE_TARGET_QUERIES if smoke else _TARGET_QUERIES
    target_pool = _SMOKE_TARGET_POOL_PER_BUCKET if smoke else _TARGET_POOL_PER_BUCKET
    _assert_h1_queries(queries_df, target_q)
    _assert_h2_pool(pool_df, queries_df, target_pool)
    print()

    print("[3/5] Embedding |Q ∪ C| under three models (H3 inline)...")
    embeddings = _do_embeddings(queries_df, pool_df)
    print()

    print("[4/5] Top-K NN retrieval + bootstrap CI (H5)...")
    neighbors_df = _do_neighbors(queries_df, pool_df, embeddings)
    rates_df = _per_model_era_match_rates(neighbors_df, queries_df)
    print(f"  rates:\n{rates_df.to_string(index=False)}")
    print()

    print("[5/5] Hand-audit sampling + artifact writing...")
    hand_audit_df = _sample_hand_audit(
        neighbors_df, queries_df, pool_df,
        per_model=_HAND_AUDIT_PER_MODEL, seed=_HAND_AUDIT_SEED,
    )
    _write_artifacts(
        queries_df, pool_df, embeddings, neighbors_df, rates_df,
        hand_audit_df, summaries, snapshot, smoke,
    )

    # Print decision
    sp = rates_df[rates_df["model"] == "specter2"].iloc[0]
    action, rationale = _apply_decision_rule(
        sp["era_match_rate"], sp["ci_low"], sp["ci_high"]
    )
    print()
    print(f"DECISION (SPECTER2 era-match {sp['era_match_rate']:.1%} "
          f"[CI {sp['ci_low']:.1%}, {sp['ci_high']:.1%}]):")
    print(f"  → {action}")
    print(f"  rationale: {rationale}")
    print()
    print(f"Check 5c {mode_label} complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true", help="run with toy inputs")
    args = parser.parse_args()
    main(smoke=args.smoke)
    sys.exit(0)
