# Phase 0.2 Wave 4A — Stage 2 compute target decision (LOCKED 2026-05-04)

**Compiled:** 2026-05-04 (post-Wave 2A + post-bug-fix + budget review)
**Locked decisions:** Reading B model stack + N=1M headline + N=500K
robustness + Modal A100 preemptible + cross-field deferred to
Stage 3 conditional + reserve budget for partial re-runs.

## Locked decisions

| # | Decision | Lock |
|---|---|---|
| 1 | Production N (headline) | **1M** |
| 2 | Production N (robustness sweeps) | **500K** |
| 3 | Model stack | **SciNCL (primary) + Qwen3 (cross-family)** — Reading B |
| 4 | GPU class | **A100** |
| 5 | Provider | **Modal** |
| 6 | Pricing tier | **Preemptible** (verify current Modal naming at Stage 1) |
| 7 | Cross-field Physics | **Deferred to Stage 3 conditional on CS headline** |
| 8 | Reserve budget | **$50-150 for partial high-N re-runs** |

## Rationale (per the conversation chain)

### N target — 1M

- **Meets ws2 desideratum §6** (≥1M papers across 1970-2024)
- **Power analysis: meaningful for ws3 inputs** at all five
  load-bearing patterns (Test I slope, Test IV curve, Test IV
  interaction, subfield decomposition, era contrast)
- **2M ruled out by §9 budget cap.** 2M-everywhere triple-pass
  ($600-1000+) violates the cap; 1M fits with reserve
- **500K considered**: violates desideratum §6; saves only
  $80-160; not enough margin to justify the methodology
  weakening

### Model stack — SciNCL primary + Qwen3 cross-family (Reading B)

- **SciNCL is drift-optimal on our specific 1970-2024 corpus.**
  Phase 0.1 Check 5c era-match rate: SciNCL 75.4% > Qwen3 70.7%
  > SPECTER2 62.8%. For a temporal-trend study with significant
  pre-1990 content, drift-robustness is the load-bearing
  embedding property.
- **Drop SPECTER2 from headline.** SPECTER2 + SciNCL are within-
  family (both BERT-base, both citation-contrastive on S2ORC);
  agreement carries little robustness information. Saves
  ~$75-150 across 3 headline runs.
- **Qwen3 retained** for cross-family (decoder-LM vs encoder)
  cross-check.
- **SPECTER2 retained in pipeline** for Stage 3 robustness item
  #1 ("embedding-model swap") and as fallback if SciNCL has
  unexpected production-scale issues — see
  `docs/phases/phase-0.2-scincl-primary-contingency.md`.

### GPU class — A100

- Cheaper-per-pass than A10G at our N (lower hours × higher rate
  beats A10G's longer-but-cheaper).
- Faster turnaround for iteration.

### Provider — Modal

- Python-native; no container ops overhead.
- Preemptible tier available for ~40% discount.

### Pricing — preemptible

- Embedding pass is embarrassingly parallel + tolerant to
  preemption with chunked-resumable runner pattern.
- Saves ~$100-200 across the headline 3-run pass.
- Trade-off: ~50-100 lines of resumable-runner code; ~20-30%
  wall-clock variance.
- Stage 1 dry-run uses preemptible to verify the runner works
  before committing the full 1M.

### Cross-field Physics — Stage 3 conditional

- If CS headline yields clear divergence: Physics replication is
  the strong test, fund it then.
- If CS headline is null: Physics doesn't save the program.
- Saves a full pass (~$100-200) from Stage 2 budget.

### Reserve — $50-150

- For partial re-runs of specific failing cells (e.g., re-embed
  only the 1970s slice at higher N if pre-1990 dispersion is
  suspect). Bounded escalation rather than full-N redo.

## Locked budget

| Component | Cost |
|---|---:|
| Headline: 3 runs × 1M (SciNCL + Qwen3 on A100 preemptible) | $150-300 |
| Robustness: 2 runs × 500K | $50-100 |
| Reserve | $50-150 |
| **Total Stage 2** | **$250-550** |
| Cross-field Physics (Stage 3 conditional) | +$80-160 if triggered |

Within §9 cap ($500) at the lower end; tight at the upper end.
Cross-field is Stage 3 spend, not Stage 2.

## Stage 1 first-task binding

**The Stage 1 plan's first task is a 50K-sample dry-run on Modal
A100 preemptible** to verify:

- Per-abstract A100 timing (estimated ~$0.05/abs at 1M scale;
  real number from dry-run may differ)
- Preemption rate in our region/time-of-day (variable; check
  during dry-run)
- Resumable-runner correctness end-to-end on real preemptions

**Replan trigger:** if dry-run shows >50% delta on per-abstract
cost vs estimate, escalate to user before committing the full
1M run. Possible replans: drop to 500K headline (within budget
if cost x2), drop preemptible (if rate too high), drop one
robustness run (if cost forces).

## Open after Wave 4A commit

- Real per-abstract A100 cost (resolved at dry-run)
- Preemption rate in our Modal region (resolved at dry-run)
- Stage 1 plan as a whole (separate document; this Wave 4A only
  locks the compute target, not the Stage 1 work order)
- SciNCL contingency status: stays "what-if" unless trigger fires
  during Stage 1 dry-run or Stage 2 production

## Cross-references

- Wave 1A timings (Qwen3 bs=1):
  `experiments/phase-0.2/qwen3-batching-benchmark.md`
- Wave 2A timings (SPECTER2 production at 3K):
  `experiments/phase-0.2/section11-production-validation.md`
- Phase 0.1.E SciNCL smoke (extrapolated to ~0.40 s/abs):
  `experiments/phase-0.1/embedding-pipeline-smoke.md`
- §9 budget desideratum: `docs/desiderata.md`
- Pre-commit estimate: `tasks/spend.md`
- SciNCL primary contingency:
  `docs/phases/phase-0.2-scincl-primary-contingency.md`
