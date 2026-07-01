# Phase 2.1 WS4 — base 1M v3 embed (SciNCL + Qwen3)

**Date:** 2026-07-01 · **Status:** SciNCL ✅ · Qwen3 ✅ — both models clean.

The base 1M v3 embedding every downstream Stage-2 metric needs, produced by
`experiments/phase-2.1/embed_1m.py` on the deployed `ws2-embed` Modal app via
the parallel `ChunkedEmbedRunner.run_mapped` path (Modal `.map()` fan-out).

## Input

- Source: `section0-sample-1M-v3.parquet` (1,000,000 rows; the v3 production
  sample, local scratchpad).
- After the **1970–2024 study-window filter** (Phase 1.4 A1): **902,531**
  in-window papers (cs 645,721 / physics 256,810). 0 empty abstracts after
  reconstruction.
- Chunking: 1,000 abstracts/chunk → 903 chunks; resumable per-chunk to disk.

## Results

| model | n | dim | mean L2 norm | band | finite | wall-clock | est cost |
|---|---|---|---|---|---|---|---|
| SciNCL (primary) | 902,531 | 768 | **23.70** | [22.5, 24.5] ✅ | all | ~8 min | ~$2.00 |
| Qwen3 (cross-family) | 902,531 | 768 | **1.000** (min 1.0 / max 1.0) | [0.99, 1.01] ✅ | all | ~40 min | ~$15.34 |

SciNCL mean norm 23.70 matches the Phase-1.1 dry-run (23.56) and the Phase-1.4
100K pilot (23.70). Qwen3 uses last-token EOS pooling + L2 normalize → exact
unit norm (1.0), Matryoshka-truncated 1024→768. **Total embed ~$17.3** (under
the ~$19 §9 pre-commit).

### Resilience note (WS4 hardening)

The first full run died at chunk 250: one Qwen3 Modal call exhausted its 3
retries on a transient error and the ordered `.map()` raised there, discarding
the concurrently-completed later chunks. Chunk-250 data was verified clean
(max abstract 9,992 chars / 4,694 tokens ≪ Qwen3's 32K context), i.e.
transient not data. Fixed (`run_mapped` + `fn.map(return_exceptions=True)`):
per-chunk failures are skipped, every good chunk persists, and a resume
re-dispatches only the missing ones. The resumed run then swept 250 → 903 in a
**single clean pass** — the resumable contract earned its place. (Dashboard
also showed a lagging backlog of input *cancellations* from the crashed run's
orphaned in-flight inputs — cleanup, not new failures.)

## Parallelization (the WS4 engineering task)

`run_mapped` fans not-yet-done chunks across Modal A100 containers via an
order-preserving `fn.map`, preserving the sequential path's resumable
chunk-to-disk contract. The Qwen3 bs=1 embed (~10 hr sequential at 1M — the
long pole) collapses to wall-clock-parallel; SciNCL 1M went 50 min → ~8 min as
a side benefit. Cost is parallelism-invariant (same GPU-seconds; only
wall-clock shrinks). A 3K-abstract `.map()` smoke validated the path
end-to-end before the full run.

## Artifacts (durable — Modal volume `ws2-embeddings`, for Phase 2.2)

- `scincl-vectors.npy` — (902,531 × 768) float32 SciNCL embeddings.
- `qwen3-vectors.npy` — (902,531 × 768) float32 Qwen3 embeddings.
- `metadata.parquet` — row-aligned (paper_id, year, field, cited_by_count).
- `scincl-cluster-assignments.npy` — WS1 §11 K=50 assignments (int32).
- `section11-prod-fit-K50-scincl-1m.npy` — WS1 production centroids
  (also committed under `data/metadata/`).

Local run dir: session scratchpad `<scratchpad>/embed-1m/`. The vectors are
NOT committed to git (~2.7 GB each); they live on the `ws2-embeddings` volume.
Phase 2.2 retrieves them via `modal volume get ws2-embeddings <file> <dest>`.
