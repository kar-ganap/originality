# Check 5c — Drift pilot (nearest-neighbor era-match rate) (SMOKE)

**Run date:** 2026-04-28
**Snapshot recorded:** 2026-04-28T04:38:09+00:00
**Mode:** smoke (toy inputs)
**Device:** mps; **dtype:** fp16

## Data composition

| Set | N | Years |
|-----|---:|---|
| Query Q | 5 | 1975-1978 |
| Pool C, pre-1990 | 10 | 1970-1989 |
| Pool C, post-2000 | 10 | 2000-2024 |

## Pull summaries

| Label | Years | Calls | Pre-filter raw | Taken | Target |
|---|---|---:|---:|---:|---:|
| queries | 1975-1978 | 2 | 400 | 5 | 5 |
| pool_pre1990 | 1980-1988 | 3 | 600 | 10 | 10 |
| pool_post2000 | 2010-2020 | 3 | 600 | 10 | 10 |

## Embedding timing (this run)

| Model | Total (s) | s/abstract |
|-------|----------:|-----------:|
| scincl | 15.5 | 0.619 |
| specter2 | 8.7 | 0.349 |
| qwen3 | 53.9 | 2.155 |

## Era-match rates (Layer B H5 + H6)

Per-model headline = mean over 5 queries of (#{neighbors year≤1990} / 10).
95% CI via 1000-resample bootstrap over queries (seed=46).

| Model | Era-match rate | 95% CI | N queries |
|-------|---------------:|--------|----------:|
| scincl | 54.0% | [50.0%, 58.0%] | 5 |
| specter2 | 58.0% | [54.0%, 60.0%] | 5 |
| qwen3 | 62.0% | [56.0%, 68.0%] | 5 |

## Decision (per Phase 0.1 plan §2)

**SPECTER2 era-match: 58.0%** with CI [54.0%, 60.0%].

**Action:** commit Flavor A (cheap insurance).

**Rationale:** CI [54.0%, 60.0%] straddles a boundary or point estimate 58.0% ∈ [50%, 70%] — gray zone.

## H7 — Hand-audit (qualitative validation of date-based metric)

Audit CSV generated with 30 rows; `topically_related` column awaits hand fill. H7 will be evaluated post-fill.

## Per-query era-match histogram (diagnostic)

| Model | 0/10 | 1/10 | 2/10 | 3/10 | 4/10 | 5/10 | 6/10 | 7/10 | 8/10 | 9/10 | 10/10 |
|-------|-----:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|------:|
| scincl | 0 | 0 | 0 | 0 | 0 | 3 | 2 | 0 | 0 | 0 | 0 |
| specter2 | 0 | 0 | 0 | 0 | 0 | 1 | 4 | 0 | 0 | 0 | 0 |
| qwen3 | 0 | 0 | 0 | 0 | 0 | 1 | 2 | 2 | 0 | 0 | 0 |

## Decision-rule reference

Per Phase 0.1 plan §2 (Stage 2 default + Stage 3 conditional Flavor A):

- SPECTER2 era-match CI fully > 70% → drift manageable, **skip Flavor A**.
- SPECTER2 era-match CI fully < 50% → drift severe, **commit Flavor A**.
- Otherwise → **commit Flavor A as cheap insurance**.

Flavor A = Word2Vec-per-decade + orthogonal Procrustes alignment + TF-IDF-weighted document aggregation (Hamilton-Leskovec-Jurafsky 2016 template, document-level adaptation).

## Artifacts

- `data/metadata/drift-pilot-queries-smoke.parquet` — 5 rows.
- `data/metadata/drift-pilot-pool-smoke.parquet` — 20 rows.
- `experiments/phase-0.1/drift-pilot-embeddings-{specter2,scincl,qwen3}-smoke.parquet` — 3 files.
- `experiments/phase-0.1/drift-pilot-neighbors-smoke.csv` — 150 rows (5 × 3 × 10).
- `experiments/phase-0.1/drift-pilot-hand-audit-smoke.csv` — 30 rows (topically_related to be hand-filled).
- `experiments/phase-0.1/drift-pilot-rates-smoke.csv` — per-model era-match + CI.
