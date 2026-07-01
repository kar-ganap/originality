# Phase 2.1 WS1 — §11 production cluster fit (base 1M SciNCL)

**Date:** 2026-07-01 · **Status:** ✅ production fit landed; cross-check clean.

The §11 temporally-stratified K=50 cluster fit, run on the WS4 base 1M v3
SciNCL embeddings via `src/whitespace2/cluster_fit`
(`experiments/phase-2.1/section11_production_fit.py`). This is the fit the
Phase-2.2 semantic series scores with `cluster_entropy` — the metric is only
valid on a decade-balanced fit (pilot finding #3; Check 5d).

## Setup

| | |
|---|---|
| Vectors | 902,531 in-window (1970–2024) v3 papers × 768 (SciNCL, WS4) |
| Fit sample | **decade-balanced 60,000** (10,000/decade × 6; `build_decade_stratified_sample`, seed 46) |
| K-means | K=50, n_init=20, random_state=46, max_iter=300 (locked §11 params) |
| Projection | Euclidean `argmin‖v−c‖²` (`project_to_clusters` == `KMeans.predict`) |

Centroid norm mean **0.8872** (means of unit vectors; <1 as expected — the
reason `project_to_clusters` must use Euclidean, not cosine).

## Production fit — assignment distribution (all 902,531 papers)

| metric | value |
|---|---|
| cluster_entropy (MM, nats) | **3.859** |
| effective # clusters (exp H) | **47.4 / 50** |
| empty clusters | **0** |
| min / median / max cluster | 5,596 / 16,099 / 33,605 |
| max cluster share | **3.7%** |

Papers spread evenly across all 50 clusters — no collapse, no degenerate
(near-empty) cluster. A healthy fit for the semantic series.

## Cross-check vs committed Phase-0.2 SciNCL centroids

Projected the same 902,531 papers through the committed
`data/metadata/section11-cluster-fit-S-K50-scincl.npy` (the Phase-0.2 Wave-2A
fit on |S|=1,500 = 250/decade):

| metric | production (60K fit) | committed (1.5K fit) |
|---|---|---|
| centroid norm mean | 0.8872 | 0.8943 |
| cluster_entropy | 3.859 | 3.674 |
| effective # clusters | 47.4 | 39.4 |
| empty clusters | 0 | 0 |
| min / median / max cluster | 5,596 / 16,099 / 33,605 | 65 / 15,667 / 78,756 |
| max cluster share | 3.7% | 8.7% |

**Consistent + the new fit is cleaner.** Both are §11 K=50 SciNCL fits with no
empty clusters and near-identical median cluster size (~15.7–16.1K). The
committed 1,500-sample fit has a couple of dominant clusters (max share 8.7%)
and one near-empty cluster (min 65 papers) — small-sample fit artifacts. The
60K-balanced production fit removes both (min 5,596; max share 3.7%; effective
47.4 vs 39.4), i.e. it reproduces the validated structure while resolving the
Phase-0.2 fit's small-N instability. **The production fit is the one used for
the Phase-2.2 series.**

## Artifacts

- `data/metadata/section11-prod-fit-K50-scincl-1m.npy` — production centroids
  (50 × 768; committed, reproducible).
- `<scratchpad>/embed-1m/scincl-cluster-assignments.npy` — per-paper cluster
  ids (902,531 int32; regenerable via `project_to_clusters(vectors,
  centroids)`), the Phase-2.2 `cluster_entropy` input.
- `<scratchpad>/embed-1m/section11-prod-fit-summary.json` — full run summary.
