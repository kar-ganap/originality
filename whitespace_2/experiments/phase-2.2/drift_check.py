"""Phase 2.2 WS-B — cross-era embedding-drift gate on the base 1M vectors.

Desideratum §3 + the E4 gotcha: no pre-1990 semantic-diversity claim ships
without cross-era nearest-neighbor sanity checks on the production embedding
stack. This runs the check on the actual 1M SciNCL (primary) + Qwen3
(cross-family) vectors (Check 5c was a 100-query pilot on SPECTER2).

Two signals, mirroring Check 5c + its H7 topical audit:
  (1) QUANTITATIVE era-match: for pre-1990 CS query papers retrieved against an
      era-balanced pool (equal papers/decade), how often is a query's nearest
      neighbor also pre-1990? Baseline (era-blind) = 2/6 decades = 0.333.
  (2) TOPICAL audit (the load-bearing one): dump each query + its top-3 SciNCL
      neighbors (title + abstract snippet + year) so a reviewer can judge
      whether neighbors are TOPICALLY related (embedding captures the old
      paper's topic → low drift) or era/style coincidences (→ drift). Check
      5c's H7 found the latter dominated on SPECTER2.

Gate: if the topical-coherence rate on pre-1990 queries is low (Check-5c H7
used ~66.7% as the fail line) → drift dominates → invoke the pre-registered E3
fallback (bound semantic claims to post-2000).

Usage:
  uv run python experiments/phase-2.2/drift_check.py \
      --embed-dir <scratchpad>/embed-1m \
      --source <scratchpad>/section0-sample-1M-v3.parquet
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from whitespace2.cluster_fit import build_decade_stratified_sample

_OUT = Path(__file__).parent / "drift-check"
_POOL_PER_DECADE = 500
_N_QUERIES = 150
_TOPK = 5
_AUDIT_N = 20          # queries dumped for the topical hand-audit
_SEED = 46
_PRE1990 = (1970, 1990)


def _l2(v: Any) -> np.ndarray[Any, Any]:
    v = np.asarray(v, dtype=np.float32)
    n = np.linalg.norm(v, axis=1, keepdims=True)
    return v / np.where(n > 0, n, 1.0)


def _reconstruct(inv: dict[str, list[int]]) -> str:
    if not inv:
        return ""
    m = max(max(p) for p in inv.values())
    toks = [""] * (m + 1)
    for w, ps in inv.items():
        for p in ps:
            toks[p] = w
    return " ".join(t for t in toks if t)


def _era_match(
    model: str, qvec: Any, pvec: Any, q_years: Any, p_years: Any,
) -> dict[str, Any]:
    """Top-1 / top-k era-match rate for pre-1990 queries vs the pool."""
    sims = _l2(qvec) @ _l2(pvec).T                     # (nq, npool)
    order = np.argsort(-sims, axis=1)[:, :_TOPK]        # top-k pool idx per query
    nbr_years = p_years[order]                          # (nq, k)
    nbr_pre90 = (nbr_years >= _PRE1990[0]) & (nbr_years < _PRE1990[1])
    return {
        "model": model,
        "n_queries": int(len(q_years)),
        "top1_era_match": round(float(nbr_pre90[:, 0].mean()), 4),
        "topk_era_match_mean": round(float(nbr_pre90.mean()), 4),
        "era_blind_baseline": round(2.0 / 6.0, 4),
        "_order": order,  # kept for the audit dump (SciNCL only)
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--embed-dir", required=True, type=Path)
    ap.add_argument("--source", required=True, type=Path)
    args = ap.parse_args()
    _OUT.mkdir(parents=True, exist_ok=True)

    meta = pd.read_parquet(args.embed_dir / "metadata.parquet")
    years = meta["year"].to_numpy()
    fields = meta["field"].to_numpy()
    ids = meta["paper_id"].to_numpy()

    # Era-balanced retrieval pool (equal papers/decade) — reuse the §11 sampler.
    pool_idx = build_decade_stratified_sample(
        years, n_per_decade=_POOL_PER_DECADE, seed=_SEED,
    )
    # Pre-1990 CS queries, disjoint from the pool.
    pre90_cs = np.nonzero(
        (years >= _PRE1990[0]) & (years < _PRE1990[1]) & (fields == "cs"),
    )[0]
    pool_set = set(pool_idx.tolist())
    q_candidates = np.array([i for i in pre90_cs if i not in pool_set])
    rng = np.random.default_rng(_SEED)
    query_idx = rng.choice(
        q_candidates, size=min(_N_QUERIES, len(q_candidates)), replace=False,
    )
    query_idx.sort()
    print(f"pool={len(pool_idx)} (500/decade), queries={len(query_idx)} "
          f"pre-1990 CS", flush=True)

    results: dict[str, Any] = {"pool_n": int(len(pool_idx)),
                               "query_n": int(len(query_idx)), "models": {}}
    scincl_order = None
    for model in ("scincl", "qwen3"):
        vecs = np.load(args.embed_dir / f"{model}-vectors.npy", mmap_mode="r")
        qvec = np.asarray(vecs[query_idx])
        pvec = np.asarray(vecs[pool_idx])
        em = _era_match(model, qvec, pvec, years[query_idx], years[pool_idx])
        if model == "scincl":
            scincl_order = em.pop("_order")
        else:
            em.pop("_order", None)
        results["models"][model] = em
        print(f"[{model}] top1 era-match {em['top1_era_match']} / "
              f"top{_TOPK} {em['topk_era_match_mean']} "
              f"(era-blind baseline {em['era_blind_baseline']})", flush=True)

    # ---- topical audit dump (SciNCL top-3 neighbors for AUDIT_N queries) ----
    assert scincl_order is not None
    audit_q = query_idx[:_AUDIT_N]
    audit_order = scincl_order[:_AUDIT_N, :3]
    need_ids = set(ids[audit_q].tolist())
    for row in audit_order:
        need_ids.update(ids[pool_idx[row]].tolist())

    # pull title + abstract for just the audited papers from the source parquet
    src = pq.read_table(
        str(args.source),
        columns=["id", "title", "abstract_inverted_index_json"],
    ).to_pandas()
    src = src[src["id"].isin(need_ids)]
    text = {
        r["id"]: (str(r["title"] or ""),
                  _reconstruct(json.loads(str(r["abstract_inverted_index_json"]))))
        for _, r in src.iterrows()
    }

    lines = ["# WS-B drift-check — SciNCL topical audit sample\n",
             "Pre-1990 CS queries (top-3 neighbors from an era-balanced pool). "
             "Judge: is each neighbor TOPICALLY related to the query?\n"]
    for qi, nbrs in zip(audit_q, audit_order):
        qid = ids[qi]
        qt, qa = text.get(qid, ("", ""))
        lines.append(f"\n## Q ({int(years[qi])}) — {qt[:140]}\n"
                     f"> {qa[:280]}\n")
        for rank, pj in enumerate(nbrs, 1):
            gi = pool_idx[pj]
            nt, na = text.get(ids[gi], ("", ""))
            lines.append(f"  {rank}. [{int(years[gi])}] {nt[:130]}\n"
                         f"     {na[:220]}\n")
    (_OUT / "scincl-topical-audit.md").write_text("".join(lines))
    (_OUT / "drift-check-results.json").write_text(
        json.dumps(results, indent=2))
    print(f"\nwrote {_OUT}/drift-check-results.json + scincl-topical-audit.md",
          flush=True)


if __name__ == "__main__":
    main()
