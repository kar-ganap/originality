# Check 5b — Metric convergence analysis (SMOKE)

**Run date:** 2026-04-28
**Snapshot:** 2026-04-28T07:08:13+00:00
**Mode:** smoke
**Q_5b:** cs 2024, |Q_5b|=248, multi-seed sample of OpenAlex.
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
| cluster_entropy | did not converge | 200 | insufficient points (need ≥3 non-degenerate, have 1) |
| effective_dim | did not converge | 200 | insufficient points (need ≥3 non-degenerate, have 0) |
| mean_pairwise_cosine | did not converge | 200 | insufficient points (need ≥3 non-degenerate, have 1) |

## Full sweep

| Metric | n | Mean | SD | CV | Notes |
|---|---:|---:|---:|---:|---|
| cluster_entropy | 200 | 1.6140 | 0.0243 | 1.5% |  |
| effective_dim | 200 | 21.3099 | 1.5679 | 7.4% | (degenerate) |
| mean_pairwise_cosine | 200 | 0.1796 | 0.0013 | 0.7% |  |

## Caveats

- **Effective dimensionality (PCA participation ratio)** is degenerate for n < d=768
  (covariance matrix rank ≤ n-1). The n=200 and n=500 points are reported but
  excluded from the convergence test.
- **Mean pairwise cosine** at n=10000 uses the full pairwise matrix (~800MB).
  If memory becomes tight on rerun, fall back to a 50K random pair sample.
- **Demographic Shannon** is the lightweight check on `first_country`. Full
  demographic-feature suite (gender, career-stage, prestige, joint Rao Q) is
  Stage-1 work, not Phase-0.1.

## Decision (per Phase 0.1 plan §1723-1727)

The N_target values above are committed for Phase 0.2 pre-registration as
the per-metric bootstrap-sample-size constants. Per-year bootstrap n =
min(Nᵧ, N_target). For metrics that did not converge by the largest n
in this sweep, Phase 0.2 locks min(Nᵧ, max-n-in-sweep) with a documented
caveat.

## Artifacts

- `experiments/phase-0.1/metric-convergence-smoke.csv` — per-metric per-n means + SD.
- `experiments/phase-0.1/metric-convergence-smoke.png` — 4-panel plot (created in
  next step if matplotlib available).
- `data/metadata/check5bd-pull-2024-cs-smoke.parquet` — 5b pull source.
- `experiments/phase-0.1/check5bd-embeddings-specter2-smoke.parquet` — embeddings.
