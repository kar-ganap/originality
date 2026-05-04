# Check 5d — Cluster-fit stratification artifact (SMOKE)

**Run date:** 2026-04-28
**Snapshot:** 2026-04-28T07:08:13+00:00
**Mode:** smoke
**Methodology (per Phase 0.1 plan §11):** Fit K-means clusters twice on the
same embedding space at the same K — once on a temporally-stratified pool S
(equal papers per decade) and once on an unstratified Nᵧ-proportional pool U
(same total N as S). Assign held-out 1975 and 2020 papers to clusters from
each fit. Compare assignment-distribution concentration via effective number
of clusters `effN(p) = exp(H(p))` and `KL(p || uniform)`.

## Pool composition

| Pool | N | Year distribution |
|---|---:|---|
| Stratified S | 60 | per-decade: {1970: 10, 1980: 10, 1990: 10, 2000: 10, 2010: 10, 2020: 10} |
| Unstratified U | 60 | per-decade: {1970: 1, 1980: 1, 1990: 3, 2000: 10, 2010: 20, 2020: 25} |
| Held-out 1975 | 10 | year=1975 only |
| Held-out 2020 | 10 | year=2020 only |

## Pre-registered H7 thresholds

- **Artifact present (H_1975):** effN_S / effN_U > 1.43.
- **Artifact absent (H_2020 negative control):**
  |effN_S - effN_U| / max(effN_S, effN_U) < 20%.
- **§11 validated:** both conditions hold at K=25.

## Headline at K=25

**§11 VALIDATED.** 

H_1975 effN ratio (S/U) = 1.59 >1.43 (artifact present); H_2020 relative diff = 14.3% <20% (artifact absent on negative control). The decade-stratified fit prevents the modern-cluster-dominance artifact for pre-1990 papers.

## Robustness sweep across K

| K | effN_S(1975) | effN_U(1975) | S/U | effN_S(2020) | effN_U(2020) | rel.diff | §11? |
|---:|----------:|----------:|----:|----------:|----------:|------:|---|
| 10 | 5.80 | 3.83 | 1.51 | 7.00 | 5.32 | 24.0% | NO |
| 25 | 6.64 | 4.18 | 1.59 | 6.42 | 5.50 | 14.3% | YES |
| 50 | 3.45 | 4.18 | 0.83 | 7.75 | 6.42 | 17.2% | NO |

## Methods-section magnitude statement

At K=25, the unstratified-fit effective cluster count for held-out
1975 papers is 4.2 (37% fewer
than the stratified-fit effective count of 6.6).
This quantifies the "modern-cluster dominance" artifact §11's stratification
prevents for pre-1990 papers.

## Artifacts

- `experiments/phase-0.1/cluster-stratification-check-smoke.csv` — per-K H7 metrics.
- `data/metadata/cluster-fit-manifest-{S,U}-K{30,50,100}-smoke.npy` — centroid arrays.
- `data/metadata/cluster-fit-manifest-smoke.md` — per-§11 manifest.
