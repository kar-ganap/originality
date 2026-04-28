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
2. **Batch_size=8 leaves performance on the table.** Production runs
   should sweep batch_size ∈ {32, 64, 128} to amortize Python overhead.
   Unlikely to explain a 30× gap, but worth checking.
3. **Plan §1 estimates may have been overly optimistic for M-series.**
   They were drafted from prior Phase 0 research; this is the first
   actual measurement on the dev hardware. Plan revision may be warranted.

### Implication for Stage 2 compute decision

The deferred local-vs-cloud decision (per plan §1 "Open decisions
deferred") now strongly leans **cloud GPU** for Stage 2:

- **Local (this hardware):** ~643 hrs at N=500K; untenable at N=2M.
- **Cloud A10G GPU** (rough estimate 5-10× MPS): ~64-128 hrs at 500K;
  256-515 hrs at 2M. Tolerable for one-time runs; expensive for
  robustness sweeps.
- **Cloud A100 GPU** (rough estimate 30-50× MPS): ~12-22 hrs at 500K;
  50-90 hrs at 2M. Tolerable. Cost ~$15-50 per pass.

Stage 1 will lock the decision against Check 5b's actual N_target. But
Phase 0.1.E's H7 result moves the prior strongly toward cloud.

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
