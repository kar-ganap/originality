# Check 5b — Metric convergence analysis

**Run date:** 2026-04-28
**Snapshot:** 2026-04-28T07:14:05+00:00
**Mode:** full
**Q_5b:** cs 2024, |Q_5b|=10073, multi-seed sample of OpenAlex.
**Subsamples per n:** 20 independent draws, RNG seed_base=1000.

## Convergence criterion (pre-registered, H5)

Smallest n at which both:
1. Point estimate change <5% across the next two n-step comparisons.
2. Inter-subsample CV <10% at n.

If no n meets the criterion within the sweep range, N_target = "did not converge"
and the metric's bootstrap n locks at min(Nᵧ, max-n-in-sweep) for Phase 0.2 with
a noted caveat.

## Per-metric N_target (Phase 0.2 input)

| Metric | N_target | Max n in sweep | Rationale |
|---|---:|---:|---|
| cluster_entropy | 200 | 10000 | Δ_1=0.6%, Δ_2=0.6%, CV=2.2% all under thresholds at n=200 |
| effective_dim | 1000 | 10000 | Δ_1=0.8%, Δ_2=0.3%, CV=6.9% all under thresholds at n=1000 |
| mean_pairwise_cosine | 200 | 10000 | Δ_1=0.9%, Δ_2=0.3%, CV=1.6% all under thresholds at n=200 |
| demographic_shannon | 500 | 10000 | Δ_1=2.8%, Δ_2=0.1%, CV=3.6% all under thresholds at n=500 |

## Full sweep

| Metric | n | Mean | SD | CV | Notes |
|---|---:|---:|---:|---:|---|
| cluster_entropy | 200 | 2.9581 | 0.0655 | 2.2% |  |
| cluster_entropy | 500 | 2.9396 | 0.0467 | 1.6% |  |
| cluster_entropy | 1000 | 2.9560 | 0.0385 | 1.3% |  |
| cluster_entropy | 2000 | 2.9580 | 0.0225 | 0.8% |  |
| cluster_entropy | 5000 | 2.9516 | 0.0135 | 0.5% |  |
| cluster_entropy | 10000 | 2.9548 | 0.0009 | 0.0% |  |
| effective_dim | 200 | 21.2264 | 2.3299 | 11.0% | (degenerate) |
| effective_dim | 500 | 21.5099 | 1.6589 | 7.7% | (degenerate) |
| effective_dim | 1000 | 22.1576 | 1.5284 | 6.9% |  |
| effective_dim | 2000 | 22.3281 | 0.8639 | 3.9% |  |
| effective_dim | 5000 | 22.3931 | 0.4360 | 1.9% |  |
| effective_dim | 10000 | 22.5191 | 0.0398 | 0.2% |  |
| mean_pairwise_cosine | 200 | 0.1806 | 0.0029 | 1.6% |  |
| mean_pairwise_cosine | 500 | 0.1789 | 0.0017 | 1.0% |  |
| mean_pairwise_cosine | 1000 | 0.1794 | 0.0014 | 0.8% |  |
| mean_pairwise_cosine | 2000 | 0.1791 | 0.0008 | 0.5% |  |
| mean_pairwise_cosine | 5000 | 0.1791 | 0.0004 | 0.2% |  |
| mean_pairwise_cosine | 10000 | 0.1792 | 0.0000 | 0.0% |  |
| demographic_shannon | 500 | 3.0960 | 0.1125 | 3.6% |  |
| demographic_shannon | 2000 | 3.1820 | 0.0508 | 1.6% |  |
| demographic_shannon | 10000 | 3.1797 | 0.0017 | 0.1% |  |

## Caveats

- **Effective dimensionality (PCA participation ratio)** is degenerate for n < d=768
  (covariance matrix rank ≤ n-1). The n=200 and n=500 points are reported but
  excluded from the convergence test.
- **Mean pairwise cosine** at n=10000 uses the full pairwise matrix (~800MB).
  If memory becomes tight on rerun, fall back to a 50K random pair sample.
- **Demographic Shannon** is the lightweight check on `first_country`. Full
  demographic-feature suite (gender, career-stage, prestige, joint Rao Q) is
  Stage-1 work, not Phase-0.1.

## Pre-registered prediction outcomes (H6)

Pre-registered N_target bands (wide; goal was to extract empirically):

| Metric | Pre-registered band | Actual | Outcome |
|---|---|---:|---|
| effective_dim | [1000, 10000] | **1000** | within band ✓ (low end) |
| cluster_entropy | [200, 5000] | **200** | within band ✓ (low end) |
| mean_pairwise_cosine | [500, 5000] | **200** | **below band** (faster convergence than expected) |
| demographic_shannon | ≤2000 | **500** | within band ✓ |

Three of four metrics converged within the pre-registered band. Mean pairwise
cosine converged faster than predicted (200 < band lower 500), reflecting that
on highly-normalized SPECTER2 vectors the pairwise distance is dominated by
common-direction structure that stabilizes very quickly — a benign surprise.

## Decision (per Phase 0.1 plan §1723-1727)

The N_target values above are committed for Phase 0.2 pre-registration as
the per-metric bootstrap-sample-size constants. Per-year bootstrap n =
min(Nᵧ, N_target). All four metrics converged; no fallback or "did not
converge" caveat required.

**Phase 0.2 commitments (locked here):**

| Metric | Phase 0.2 bootstrap N |
|---|---:|
| Cluster entropy (K=50) | min(Nᵧ, **200**) |
| Effective dimensionality | min(Nᵧ, **1000**) |
| Mean pairwise cosine distance | min(Nᵧ, **200**) |
| Demographic Shannon (per feature) | min(Nᵧ, **500**) |

For early years where Nᵧ < N_target, the bootstrap n is bounded above by
Nᵧ; the bootstrap CI widens accordingly, which §9e's IPW-corrected aggregate
metrics handle by carrying through the sampling uncertainty.

## Artifacts

- `experiments/phase-0.1/metric-convergence.csv` — per-metric per-n means + SD.
- `experiments/phase-0.1/metric-convergence.png` — 4-panel plot (created in
  next step if matplotlib available).
- `data/metadata/check5bd-pull-2024-cs.parquet` — 5b pull source.
- `experiments/phase-0.1/check5bd-embeddings-specter2.parquet` — embeddings.
