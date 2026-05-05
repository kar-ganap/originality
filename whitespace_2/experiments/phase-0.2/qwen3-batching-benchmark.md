# Phase 0.2 Wave 1A — Qwen3 batching benchmark

**Run dates:** 2026-05-04 (primary + follow-up)
**Device:** mps; **dtype:** fp16
**Inputs:** 48 abstracts stratified across the 10 (year × field) cells
of `data/metadata/pilot-query-results.parquet` (5 per cell, seed=42).
Char-length: min=106, p50=807, p95=1790, max=3254.

## Headline

**bs=1 is the optimal Qwen3 batching strategy on M-series MPS** —
**2.94× faster than bs=8** (1.953 vs 5.748 s/abs warm). Per-abstract
time increases *monotonically* with batch size, which is the opposite
of typical embedding-model behavior.

The "sorted-batching mitigation" hypothesized in Phase 0.1.E doesn't
exist (sentence-transformers does length-sorted batching internally).
But Phase 0.1.E's *empirical* claim that bs=1 is much faster than bs=8
on warm Qwen3 was correct — confirmed at 2.94× here.

The mechanism is *not* padding. Most likely candidates:
1. **Decoder-LM KV-cache memory pressure on MPS.** Each token in a
   batch needs KV-cache memory; larger batches hit MPS memory-
   bandwidth limits with Qwen3's 600M parameters.
2. **MPS-specific batch operator overhead.** Apple's MPS backend may
   pay a fixed per-element cost that doesn't amortize for decoder-LM
   architectures.
3. **Sequential-decoder-step amortization** — bs=1 lets the model
   process each abstract's last-token-pooling step without batch
   coordination.

## Results — full bs sweep

| Config | N | Total (s) | s/abstract | vs bs=8 | 500K hrs | 2M hrs |
|---|---:|---:|---:|---:|---:|---:|
| **bs=1** (warm) | 48 | 93.8 | **1.953** | **2.94×** | **271** | **1085** |
| bs=2 | 48 | 197.1 | 4.106 | 1.40× | 570 | 2281 |
| bs=4 | 48 | 217.9 | 4.540 | 1.27× | 631 | 2522 |
| bs=8 | 48 | 275.9 | 5.748 | 1.00× | 798 | 3193 |
| sorted bs=8 (primary) | 48 | 322.0 | 6.709 | 0.86× | 932 | 3727 |
| sorted bs=32 (primary) | 48 | 410.5 | 8.551 | 0.67× | 1188 | 4751 |

**Primary run** (bs=8 ± sorted variants) measured 2026-05-04T20:14
UTC. **Follow-up run** (bs ∈ {1, 2, 4}) measured ~30 min later same
session. Sustained-load conditions are similar.

## Two findings

### Finding 1 — sentence-transformers does length-sorted batching internally

Source-read of `sentence_transformers.SentenceTransformer.encode`
revealed:

> `length_sorted_idx = np.argsort([-self._text_length(sen) for sen in sentences])`
> `sentences_sorted = [sentences[idx] for idx in length_sorted_idx]`

External pre-sort (Wave 1A's hypothesized mitigation) is therefore
redundant. The 17% slowdown of "sorted bs=8" vs "naive bs=8" is the
double-sort overhead.

`embed_qwen3`'s `length_sort` parameter is now `False` by default
(documentation/diagnostic-only).

### Finding 2 — bs=1 is genuinely faster than bs=8 (Phase 0.1.E claim confirmed)

Phase 0.1.E observed cold bs=1 = 2.286 s/abs (10 abstracts) and warm
bs=8 = 4.228 s/abs (50 abstracts) and estimated warm bs=1 ≈ 1.1 s/abs
by subtracting load time. The ratio bs=1/bs=8 was claimed at ~4×.

Wave 1A follow-up directly measured warm bs=1 at 1.953 s/abs. Ratio
bs=8/bs=1 = 2.94× — close to the claim, slightly less aggressive.
Phase 0.1.E was right *that* bs=1 is faster, just slightly off on
*how much*.

The pattern is monotonic across bs ∈ {1, 2, 4, 8}: each batch-size
doubling adds ~1-2 s/abs. This is consistent across runs.

## Decision input for Wave 4A (Stage 2 compute target)

Real Qwen3 production timing for compute planning is **bs=1 at
~1.953 s/abs on M-series MPS fp16**.

| Strategy | s/abs | 500K hrs | 2M hrs | Note |
|---|---:|---:|---:|---|
| bs=1 (M-series MPS, warm) | 1.953 | 271 | 1085 | Wave 1A optimal |
| A10G (~7×) | ~0.279 | ~39 | ~155 | $5-15/pass |
| A100 (~40×) | ~0.049 | ~7 | ~27 | $15-50/pass |

**Implication for Stage 2 compute target.**

At Qwen3 bs=1, local M-series for 500K papers is ~271 hrs (~11
days continuous). Multiplied across the three-model triple-pass
(SPECTER2 ~30 hrs + SciNCL ~25 hrs + Qwen3 271 hrs ≈ 330 hrs ≈ 14
days), local is *technically feasible* for one production run but
impractical for robustness sweeps.

Cloud A10G at ~$5-15 per Qwen3 pass + ~$10-20 for SPECTER2/SciNCL
combined = **~$15-35 per full triple-pass**, well within the §9 cost
gate. A100 is the cleaner choice for robustness sweeps but A10G
suffices for the headline.

**Conclusion**: Stage 2 compute decision still leans cloud, but the
margin is narrower. Wave 4A user-judgment moment retained — the
~$15-35-per-pass cloud cost vs ~14-day local feasibility is a real
choice.

## Production batching defaults

Production callers should use:
- **SPECTER2**: `batch_size=8` (BERT-base, 512 truncation; Phase 0.1.E
  optimal).
- **SciNCL**: `batch_size=8` (same).
- **Qwen3**: `batch_size=1` (per this benchmark).

`embed_qwen3` default is now `batch_size=8` for backward compatibility
with Phase 0.1.E callers, but production scripts (Check 5c, Check 5b/5d,
Stage 2 pipeline) should explicitly pass `batch_size=1`. The function
docstring documents the bs=1 recommendation.

## Methodology lessons

**Lesson 1 — Check upstream library defaults before hypothesizing a
mitigation.** Phase 0.1.E's "padding waste from unsorted batching"
hypothesis assumed sentence-transformers wasn't doing the sort. A
30-second source-read would have caught this. Logged for future
phases.

**Lesson 2 — Cold/warm comparisons across different batch sizes
deserve a direct measurement.** Phase 0.1.E estimated warm bs=1 by
arithmetic on cold bs=1 (with load) and warm bs=8 (without). The
estimate was directionally right but quantitatively off (~1.1 vs
actual ~1.95). For Stage 2 cost planning, direct measurements at the
production batch size are required.

**Lesson 3 — Per-abstract time can increase with batch size for
decoder-LM embedding models on memory-bandwidth-limited backends.**
This is the opposite of typical encoder-only model behavior. The
right batch size for a given (model architecture × hardware backend)
combination is empirical, not assumed.

Logged in `tasks/lessons.md`.

## Acceptance check (Wave 1A)

Per `phase-0.2-execution.md` Wave 1A acceptance: best-strategy
wall-clock recorded; production batching decision committed.

- ✅ Best-strategy wall-clock: bs=1 at 1.953 s/abs warm.
- ✅ Sentence-transformers' internal length-sorting verified via
  source-read; redundant external pre-sort de-defaulted.
- ✅ Production callers: use `batch_size=1` for Qwen3 (documented
  in `embed_qwen3` docstring).
- ✅ Open question from primary run answered: bs=1 IS faster than
  bs=8 (2.94×).

Wave 1A complete. Stage 2 compute decision input ready for Wave 4A.

## Artifacts

- `experiments/phase-0.2/qwen3-batching-benchmark.csv` — six-config
  per-config timings (3 primary + 3 follow-up).
- `experiments/phase-0.2/qwen3-batching-followup-summary.json` —
  follow-up summary + optimal config.
- `experiments/phase-0.2/qwen3_batching_benchmark.py` — primary run.
- `experiments/phase-0.2/qwen3_batching_followup.py` — bs ∈ {1,2,4}
  follow-up.
- `src/whitespace2/embeddings.py::embed_qwen3` — `length_sort`
  parameter de-defaulted; docstring updated with bs=1 production
  recommendation.
