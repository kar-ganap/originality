# Phase 0.2 Wave 4A — Stage 2 compute target decision matrix

**Compiled:** 2026-05-04 (post-Wave 2A)
**Inputs:** Wave 1A Qwen3 timing + Wave 2A SPECTER2 production timing
+ Phase 0.1.E SciNCL smoke timing (extrapolated to production).

## Locked per-model timings (M-series MPS, fp16, warm)

| Model | s/abs (warm) | Source | Confidence |
|---|---:|---|---|
| SPECTER2 | 0.421 | Wave 2A 3K-paper run (this commit) | High — direct measurement at 3K |
| SciNCL | ~0.40 | Phase 0.1.E smoke 0.164 s/abs × 2.5× thermal-throttle factor | Medium — extrapolated |
| Qwen3 (bs=1) | 1.953 | Wave 1A 48-paper warm benchmark | High — direct |
| **Triple-pass total** | **~2.77 s/abs** | sum | — |

Note: SciNCL number is extrapolated from a 50-paper smoke. Check 5b's
SPECTER2 result (0.423 s/abs at 11K) suggests sustained-load timing
is ~1.8-2.5× the smoke timing for BERT-class models. Apply same
factor to SciNCL: 0.164 × 2.5 ≈ 0.41 s/abs. Verify in Stage 2 first
benchmark batch.

## Production-scale N projections — local M-series

| N | SPECTER2 hrs | SciNCL hrs | Qwen3 hrs | **Total hrs** | Days @ 12hr/day |
|---:|---:|---:|---:|---:|---:|
| 500K | 58 | 56 | 271 | **385** | 32 |
| 1M | 117 | 111 | 543 | **771** | 64 |
| 2M | 234 | 222 | 1085 | **1541** | 128 |

Local feasibility at 500K = ~32 days continuous (12 hr/day). Practically
unworkable for any iteration sweep.

## Production-scale N projections — cloud (rough estimates)

A10G on Modal: ~7× faster than M-series MPS for SPECTER2/SciNCL,
~7× for Qwen3 (decoder-LM scaling on A10G is empirically similar
to encoder-only for inference).

A100 on Modal: ~30× faster than M-series for SPECTER2/SciNCL,
~30-40× for Qwen3.

| N | A10G total hrs | A100 total hrs | A10G $ | A100 $ |
|---:|---:|---:|---:|---:|
| 500K | ~55 | ~13 | $50-100 | $40-80 |
| 1M | ~110 | ~26 | $100-200 | $80-160 |
| 2M | ~220 | ~52 | $200-400 | $160-320 |

A10G Modal: ~$1.30/hr per GPU × ~55 hrs = ~$70 at 500K.
A100 Modal: ~$3.40/hr × ~13 hrs = ~$45 at 500K.

Both well within the §9 budget cap ($50-500). A100 is faster AND
cheaper at 500K because lower hours × higher rate beats A10G's
longer-but-cheaper. At 2M scale, A10G crosses A100's per-pass
cost (~$200 each).

## Robustness sweep multiplier

Phase 0.2 plan §1 commits to ≥2 embedding families (cross-family
robustness) + Flavor A drift correction (Check 5c commit). That's
**3 production runs minimum** for the headline:
1. Default stack (SPECTER2 + SciNCL + Qwen3)
2. Drift-corrected stack (Flavor A)
3. Robustness with 1+ embedding swap

Optional:
4. Subfield mechanism analysis (§11 #5 — kept upfront per consolidation H1)
5. Cross-field replication (Physics)

Cost stack at 500K:
- Headline (3 runs): A100 = ~$135; A10G = ~$210
- Headline + 2 robustness (5 runs): A100 = ~$225; A10G = ~$350

At 2M scale (5 runs): A100 = ~$800; A10G = ~$1000 — bumps up
against §9 cap.

## Production-scale N target derivation

Per Check 5b, N_target per metric:
- cluster_entropy: 200
- effective_dim: 1000 (degenerate <768; use ≥1000 floor)
- mean_pairwise_cosine: 200
- demographic_shannon: 500

Per-year bootstrap n = min(Nᵧ, N_target). For Test I (headline
divergence) on annual time series 1970-2024:

| Metric | N_target/year | × 55 years |
|---|---:|---:|
| effective_dim | 1000 | 55K |
| demographic_shannon | 500 | 27.5K |
| cluster_entropy | 200 | 11K |
| mean_pairwise_cosine | 200 | 11K |

So per-year-bootstrap minimum = ~55K papers spanning 1970-2024.
Plus held-out for §11 cluster fits (currently being re-considered;
500-1500 papers).

**Headline Test I N**: ~55K with year-balanced sampling (per-year
n=1000 with surplus for early-decade sparsity). Full §0 corpus at
~5-10M from OpenAlex CS+Physics → sample 55K.

But ws2 desideratum §6 commits to "≥1M papers across the full
1970-2024 range" for the headline, so we want N ≥ 1M for visibility
on the headline + sufficient resolution for subfield-mechanism
analyses (Test II/III/IV's per-subfield slices).

**Recommended target: N = 1M.**

## Recommendation

**Cloud A100 at N=1M for the headline triple-pass.**

| Aspect | Number |
|---|---|
| Wall-clock | ~26 hrs per run (Modal A100) |
| Cost per run | ~$80-160 |
| 3-run headline budget | ~$300-500 |
| Within §9 cap ($500)? | ✅ at upper edge |

A10G is workable (~$200-400 for headline) but A100 gives both
cheaper-per-pass AND faster turnaround at this scale.

**Reject local M-series**: 64-day wall-clock per run is simply
incompatible with the iterative-sweep nature of Stage 3 robustness
work.

## Open decisions for user

1. **Production N target**: 500K (cheapest) / 1M (recommended) / 2M
   (most thorough but tight against §9 cap)?
2. **Cloud target**: A10G (cheaper at 2M; cheaper per-hour) / A100
   (faster + cheaper per-pass at 500K-1M) / both as A/B?
3. **Provider**: Modal (recommended for ws2 — Python-native, no
   container ops) / RunPod / direct cloud?

## Proceed conditions

If user picks **A100 at N=1M**:
- Phase 0.2 Wave 4A locks the choice + records pre-commit estimate
  in `tasks/spend.md`: ~$300-500 for headline triple-pass.
- Stage 1 plan inherits this lock; first Stage 2 dry-run is a 50K
  sample on A100 to verify per-abstract timing + cost extrapolation.

If user picks **A10G at N=500K** (more conservative):
- Cost ~$50-100 per run; ~$150-300 for headline.
- Wall-clock ~55 hrs per run.
- Pre-commit lower than A100-at-1M but with less methodology
  coverage.

## Artifacts

- `experiments/phase-0.2/stage2-compute-decision.md` — this matrix
- Wave 1A timings: `experiments/phase-0.2/qwen3-batching-benchmark.md`
- Wave 2A timings: `experiments/phase-0.2/section11-production-validation.md`
- Phase 0.1.E SciNCL smoke: `experiments/phase-0.1/embedding-pipeline-smoke.md`
- §9 budget: `docs/desiderata.md`
