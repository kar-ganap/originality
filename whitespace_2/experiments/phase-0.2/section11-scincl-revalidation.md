# Phase 0.2 Wave 4A — SciNCL §11 re-validation results

**Run date:** 2026-05-05
**Snapshot:** 2026-05-05T02:57:46+00:00
**Mode:** SciNCL re-embed of existing Wave 2A pools + re-fit + Euclidean
re-projection (orig held-outs only; followup parquet schema doesn't include
abstracts)

## Headline

**Verdict: SCINCL_PRIMARY_HOLDS**

r_H75 ≥1.10 AND NC pass at 3/3 K. SciNCL primary lock empirically validated. Strict passes at 1/3 K — relaxed threshold appropriate.

## SciNCL norm bands at production scale

| Pool | N | Mean L2 norm | [min, max] |
|---|---:|---:|---|
| S | 1500 | 23.591 | [22.664, 24.394] |
| U | 1482 | 23.696 | [22.677, 24.438] |
| H_1975 | 49 | 23.379 | [22.698, 23.930] |
| H_2020 | 45 | 23.669 | [22.878, 24.518] |

Note: SciNCL norm band [22.66, 24.43] differs from SPECTER2's
locked band [21.0, 23.0]. Phase 0.1.E pipeline tests asserting
SPECTER2 norm range need to be either generalized or replaced
with a SciNCL-specific assertion (norm ≈ 23.0-24.0) when SciNCL
becomes primary.

## H7' results (SciNCL vs SPECTER2 reference in parens)

Held-out: |H_1975|=49, |H_2020|=45 (orig pool only).

| K | r_H75 (S2) | NC_rd (S2) | ≥1.10? | ≥1.43? | NC? |
|---|---|---|---|---|---|
| K=30 | 1.44 (1.26) | 0.074 (0.023) | YES | YES | PASS |
| K=50 | 1.24 (1.17) | 0.065 (0.079) | YES | NO | PASS |
| K=100 | 1.27 (1.33) | 0.030 (0.030) | YES | NO | PASS |

Thresholds:
- r_H75 ≥ 1.10 (relaxed, current Phase 0.2 lock; passes at 3/3 K)
- r_H75 ≥ 1.43 (strict, original pre-reg; passes at 1/3 K)
- NC tolerance < 0.20 (passes at all K)

## Comparison to SPECTER2

| K | SciNCL r_H75 | SPECTER2 r_H75 | SciNCL stronger? |
|---|---:|---:|---|
| 30 | 1.44 | 1.26 | YES |
| 50 | 1.24 | 1.17 | YES |
| 100 | 1.27 | 1.33 | NO |

Average across K: SciNCL r_H75 = 1.32;
SPECTER2 r_H75 = 1.25.

## Decision

r_H75 ≥1.10 AND NC pass at 3/3 K. SciNCL primary lock empirically validated. Strict passes at 1/3 K — relaxed threshold appropriate.

The Wave 4A lock (SciNCL primary + Qwen3, drop SPECTER2 from
headline) is **empirically validated** by this re-validation.
The Phase 0.1 Check 5c drift signal (75.4% era-match for SciNCL)
that drove the choice is consistent with SciNCL producing at
least as strong an §11 artifact as SPECTER2.

Stage 1 first task should:
- Replace existing SPECTER2-derived cluster centroids with these
  SciNCL ones for production use
- Update Phase 0.1.E pipeline tests to assert SciNCL norm band
  (22.5, 24.5) rather than SPECTER2's (21.0, 23.0), or
  generalize the assertion

## Artifacts

- `experiments/phase-0.2/section11-scincl-revalidation.md` — this artifact
- `experiments/phase-0.2/section11-scincl-revalidation-summary.json` — machine summary
- `data/metadata/section11-prod-{S,U,H_1975,H_2020}-vec-scincl.npy` — SciNCL vectors
- `data/metadata/section11-cluster-fit-{S,U}-K{30,50,100}-scincl.npy` — SciNCL centroids
- `experiments/phase-0.2/section11_scincl_revalidation.py` — embedding script
  (kept for reproducibility)
- `experiments/phase-0.2/section11_scincl_verdict_only.py` — this verdict-only script
