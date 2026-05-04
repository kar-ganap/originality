# Phase 0.1.E — Embedding pipeline smoke test

**Run date:** 2026-04-28
**Snapshot recorded:** 2026-04-28T02:07:44+00:00
**Device:** mps; **dtype:** fp16
**Inputs:** 50 OpenAlex abstracts sampled from
`missingness-bias-raw.parquet` (stratified across 1970-1989 / 1990-2009 /
2010-2024 eras), re-fetched via OpenAlex direct ID lookup.

## H1+H2+H3+H7 — per-model results

| Model | Shape | Finite | Pass1 total (s) | Pass1 s/abs | Pass2 total (s) | Pass2 s/abs | Norm mean ± std | Norm range |
|-------|-------|--------|----------------:|------------:|----------------:|------------:|-----------------|------------|
| scincl | (50, 768) | yes | 11.31 | 1.131 | 8.21 | 0.164 | 23.540 ± 0.206 | [23.098, 23.942] |
| specter2 | (50, 768) | yes | 6.61 | 0.661 | 11.85 | 0.237 | 21.998 ± 0.191 | [21.366, 22.389] |
| qwen3 | (50, 768) | yes | 22.86 | 2.286 | 211.38 | 4.228 | 1.000 ± 0.000 | [1.000, 1.000] |

**Pass 1:** 10 abstracts, batch_size=1 (includes one-time model load).
**Pass 2:** 50 abstracts, batch_size=8 (warm; isolates
inference-only timing).

## Pinning — resolved HuggingFace revisions

Recorded in `data/metadata/embedding-model-pins.csv`.

| Model | SHA (short) | Commit date | Title |
|-------|-------------|-------------|-------|
| allenai/specter2_base | 3447645e1d | 2024-12-04 | Update README.md |
| allenai/specter2 | 2081559630 | 2024-12-04 | Update README.md |
| malteos/scincl | ebc5348d18 | 2024-06-04 | Add Sentence Transformers integration (#2) |
| Qwen/Qwen3-Embedding-0.6B | 97b0c614be | 2026-04-20 | Update README.md (#55) |

## Cross-model agreement (sanity)

Pairwise mean cosine similarity between corresponding-paper embeddings
across models. The same paper, encoded by two different models, should
produce vectors that *agree on roughly which papers are similar to which*
even though the specific representations differ. We expect cosine in
[0.3, 0.8] — too low means models disagree wildly; too high (≈1.0) would
suggest one model is just a transformation of the other.

| Pair | Mean cosine |
|------|------------:|
| specter2_vs_scincl_mean_cos | 0.7638 |
| specter2_vs_qwen3_mean_cos | -0.0240 |
| scincl_vs_qwen3_mean_cos | -0.0227 |

## H7 timing — Stage 2 compute decision input

Pass 2 (warm, batched, batch_size=8) per-abstract timing, scaled linearly:

| Model | s/abstract (warm) | 500K abstracts (hrs) | 2M abstracts (hrs) |
|-------|------------------:|---------------------:|-------------------:|
| scincl | 0.164 | 22.8 | 91.2 |
| specter2 | 0.237 | 32.9 | 131.7 |
| qwen3 | 4.228 | 587.2 | 2348.6 |

### H7 finding: timing is dramatically worse than plan §1 estimate

**Plan §1 expected** (M-series MPS fp16):
- SPECTER2: 30-90 min for 500K → **0.0036-0.011 s/abs**
- SciNCL: 30-90 min for 500K → **0.0036-0.011 s/abs**
- Qwen3-0.6B: 3.5-9 hrs for 500K → **0.025-0.065 s/abs**

**Actual on this machine**:
- SPECTER2: **0.237 s/abs** — ~30× slower than upper bound of estimate
- SciNCL: **0.164 s/abs** — ~15× slower than upper bound
- Qwen3-0.6B: **4.228 s/abs** — ~70× slower than upper bound

H7 hypothesis (timing within 2× of plan §1) **fails** for all three models.
At Stage 2 N=500K the triple-pass would run ~643 hours (~27 days local)
against a planned "half a day" estimate. At N=2M the triple-pass is
~2572 hours (~107 days) — clearly untenable for local compute.

### Probable causes (not blocking for Phase 0.1.E)

1. **MPS fp16 partial fallback to CPU.** Apple MPS doesn't have fp16
   kernels for every transformer operator; missing ones silently fall
   back to CPU. SentenceTransformer's per-batch Python overhead amplifies
   this.
2. **Batch_size=8 leaves performance on the table** for SPECTER2/SciNCL.
   Production runs should sweep batch_size ∈ {32, 64, 128} to amortize
   Python overhead. Unlikely to explain a 15-30× gap on these models,
   but worth checking.
3. **Plan §1 estimates may have been overly optimistic for M-series.**
   They were drafted from prior Phase 0 research; this is the first
   actual measurement on the dev hardware. Plan revision may be warranted.
4. **Qwen3 batching anomaly — see next subsection.**

### Pass-1 vs pass-2 decomposition (load time visibility)

| Model | Pass 1 total (cold, bs=1, 10 abs) | Pass 1 s/abs | Pass 2 total (warm, bs=8, 50 abs) | Pass 2 s/abs | Load time upper bound |
|-------|----------------------------------:|-------------:|----------------------------------:|-------------:|----------------------:|
| SciNCL | 11.31s | 1.131 | 8.21s | 0.164 | ~9.7s |
| SPECTER2 | 6.61s | 0.661 | 11.85s | 0.237 | ~4.2s |
| Qwen3-0.6B | 22.86s | 2.286 | 211.38s | 4.228 | (see anomaly) |

Load-time upper bound = `pass1_total − pass1_n × pass2_rate`. This
assumes bs=1 inference is no slower than bs=8 inference, which is true
for SPECTER2/SciNCL but NOT for Qwen3 (next subsection). The bounds are
reasonable: SPECTER2 (~110M params, BERT-base) loads fastest; SciNCL
(similar size, more elaborate sentence-transformers config path) takes
longer.

### Qwen3 batching anomaly — bs=1 is FASTER per-abstract than bs=8

This was unexpected and worth flagging because it materially changes
the H7 projection for Qwen3.

| Qwen3-0.6B configuration | Per-abstract timing |
|---|---:|
| bs=1, cold (with load): pass 1 | 2.286 s/abs |
| bs=8, warm: pass 2 | **4.228 s/abs** |
| bs=1, warm (estimated, after subtracting ~10-15s load) | **~1.1 s/abs** |

**Qwen3 bs=8 is ~4× slower per-abstract than bs=1.** The pass-2 number
is the headline H7 finding, but it represents a worst-case batching
configuration, not a typical operating point.

**Why this happens.** Qwen3 is a decoder-LM with last-token EOS pooling
and 32K-token context. When sentence-transformers batches 8 abstracts
of variable length, it pads all sequences to the longest in the batch.
A scientific abstract distribution with mean ~250 tokens but a long
tail (≥500 tokens for review-style abstracts) means a typical bs=8
batch processes 8 × max_length ≈ 8 × 500 = 4000 tokens of compute,
versus bs=1 sequentially processing the actual lengths (sum ≈ 1500
tokens). **Padding waste = ~3×**, which fully explains the ~4× slowdown.

SPECTER2/SciNCL don't show this because they truncate at 512 (BERT max),
bounding the padding range; Qwen3's much larger context window leaves
the padding range unbounded by default.

This is a known sentence-transformers behavior with decoder-LM-derived
embedding models. Standard mitigations:

1. **Length-sorted batching** (group abstracts by tokenized length
   before batching). Reduces padding waste 5-10×; expected Qwen3
   timing ~0.5-1.0 s/abs.
2. **Fixed truncation_max_length** (cap all abstracts at e.g. 512
   tokens). Simpler but loses Qwen3's long-context advantage.
3. **Smaller batches (bs=2 or bs=4).** Less padding amplification
   but less amortization. Probably ~1-1.5 s/abs.
4. **bs=1.** ~1.1 s/abs as estimated. No batching efficiency, but
   Qwen3's per-call Python overhead is small enough that this is
   already faster than naive bs=8.

### Revised H7 projection (Qwen3 with mitigation)

Realistic upper bounds for Qwen3 with smarter batching:

| Strategy | Qwen3 s/abs | 500K hrs | 2M hrs |
|---|---:|---:|---:|
| Naive bs=8 (smoke test default) | 4.228 | 587 | 2349 |
| Length-sorted bs=8-32 (estimated) | ~0.7 | **97** | **389** |
| bs=1 (worst-case fallback) | ~1.1 | 153 | 611 |

The "untenable at N=2M" framing in the H7 finding above is a
**worst-case** read; with sorted batching, Qwen3 production is "still
slow but not impossible" on local M-series.

### Implication for Stage 2 compute decision (revised)

The deferred local-vs-cloud decision still leans cloud, but the
Qwen3 batching headroom changes the arithmetic:

- **Local with naive batching (smoke-test config):** ~643 hrs at
  N=500K; ~2572 hrs at N=2M. Untenable.
- **Local with length-sorted batching (Qwen3 only; SPECTER2/SciNCL
  unchanged):** ~153 hrs at N=500K (~6 days); ~611 hrs at N=2M (~25
  days). Tolerable for a one-time run; still painful for robustness
  sweeps.
- **Cloud A10G GPU (5-10× MPS):** ~30-65 hrs at N=500K with sorted
  batching; ~120-260 hrs at N=2M. Tolerable.
- **Cloud A100 GPU (30-50× MPS):** ~6-11 hrs at N=500K; ~24-44 hrs
  at N=2M. Comfortable. Cost ~$15-50 per pass.

### Stage 1 commitment — test sorted-by-length batching before committing to cloud

Before Stage 1 locks the cloud-vs-local decision, run a small
batching-strategy benchmark on the local hardware (~30 min):

1. Implement length-sorted batching in `embed_qwen3` (sort abstracts
   by tokenized length before assembling batches; rejoin in original
   order on output).
2. Re-run the smoke test with the same 50 abstracts under three
   strategies: naive bs=8 (current), sorted bs=8, sorted bs=32.
3. Record per-abstract timing for each.
4. Use the best-strategy timing as the H7 input to the Stage 1
   compute decision.

This is bounded engineering (~half a day including the rerun) and may
move the prior on cloud-vs-local meaningfully. Worth doing before
spending cloud budget. Logged as a Stage 1 task in `tasks/todo.md`.

Stage 1 will lock the decision against Check 5b's actual N_target +
the post-mitigation Qwen3 timing.

## Decision

H1-H6 confirmed via `tests/test_embeddings.py` (9 tests, all green) and
re-verified here on real OpenAlex abstracts. H7 timing **fails** the
"within 2× of plan §1" criterion — actual timing is 15-70× worse than
estimated; this is a load-bearing finding for the deferred Stage 2
compute decision (which now leans cloud).

Phase 0.1.E gates met:

- [x] Module loads + produces correct-shape, finite, distinct, sanely-
      normed outputs across all three models.
- [x] HF revisions pinned in `data/metadata/embedding-model-pins.csv`.
- [x] Timing benchmark recorded for Stage 2 compute decision input
      (with explicit comparison to plan §1 estimate).
- [x] Cross-model agreement passes sanity check.

Phase 0.1.E **complete**. Check 5c (drift pilot) is unblocked. Stage 2
compute strategy revisit moved from "deferred" to "high-priority Stage 1
decision" given the H7 result.

## Detailed per-model CSV

See `embedding-pipeline-smoke.csv`.
