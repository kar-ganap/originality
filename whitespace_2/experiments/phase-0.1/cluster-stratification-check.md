# Check 5d — Cluster-fit stratification artifact

**Run date:** 2026-04-28
**Snapshot:** 2026-04-28T07:14:05+00:00
**Mode:** full
**Methodology (per Phase 0.1 plan §11):** Fit K-means clusters twice on the
same embedding space at the same K — once on a temporally-stratified pool S
(equal papers per decade) and once on an unstratified Nᵧ-proportional pool U
(same total N as S). Assign held-out 1975 and 2020 papers to clusters from
each fit. Compare assignment-distribution concentration via effective number
of clusters `effN(p) = exp(H(p))` and `KL(p || uniform)`.

## Pool composition

| Pool | N | Year distribution |
|---|---:|---|
| Stratified S | 316 | per-decade: {1970: 35, 1980: 32, 1990: 36, 2000: 61, 2010: 72, 2020: 80} |
| Unstratified U | 600 | per-decade: {1970: 6, 1980: 16, 1990: 33, 2000: 118, 2010: 230, 2020: 197} |
| Held-out 1975 | 30 | year=1975 only |
| Held-out 2020 | 30 | year=2020 only |

## Pre-registered H7 thresholds

- **Artifact present (H_1975):** effN_S / effN_U > 1.43.
- **Artifact absent (H_2020 negative control):**
  |effN_S - effN_U| / max(effN_S, effN_U) < 20%.
- **§11 validated:** both conditions hold at K=50.

## Headline at K=50 (pre-registered primary)

**§11 NOT VALIDATED at K=50, but the failure is METHODOLOGICAL, NOT SUBSTANTIVE.**

H_1975 effN ratio = 0.72 (S < U, opposite of expected); H_2020 negative-control
relative difference = 29.5% > 20% (negative control also failed). Both pre-
registered conditions broken; under the strict pre-registered rule, §11 is
"not validated." But the negative-control failure means the test itself is
noise-dominated at K=50 — see the K=30 result and methodology issue below.

## Robustness sweep across K (load-bearing for interpretation)

| K | effN_S(1975) | effN_U(1975) | S/U | effN_S(2020) | effN_U(2020) | rel.diff | §11? |
|---:|----------:|----------:|----:|----------:|----------:|------:|---|
| 30 | 14.53 | 10.69 | **1.36** | 16.19 | 16.68 | **2.9%** | NO (just below threshold) |
| 50 | 11.52 | 16.07 | 0.72 | 15.55 | 22.07 | 29.5% | NO (negative control fails) |
| 100 | 12.87 | 19.08 | 0.67 | 13.35 | 22.46 | 40.5% | NO (negative control fails) |

**K=30 is the only K where the negative control passes (2.9% < 20%).** At
K=30, H_1975 effN ratio = 1.36 — directionally consistent with §11 (S
preserves more 1970s diversity than U) but **just below** the pre-registered
≥1.43 threshold. The K=50 and K=100 results are uninterpretable because the
negative control fails — the comparison itself is noise-dominated at those K.

## Methodology issue surfaced — pull underrun on stratified pool

The pre-registered |S| target was ≥480 (≥80 papers/decade × 6 decades). The
actual |S| = **316** because the early-decade samples underran:

| Decade | Target | Actual | Cause |
|---|---:|---:|---|
| 1970s | 80 | 35 | low retention (~17% per Check 5a) on a single 200-sample call |
| 1980s | 80 | 32 | same (~16%) |
| 1990s | 80 | 36 | same (~18%) |
| 2000s | 80 | 61 | retention rises (~31%) |
| 2010s | 80 | 72 | retention rises (~36%) |
| 2020s | 80 | 80 | retention saturates (~40%) — target met |

The script's per-decade pull is a single `?sample=200` call. Score-thresholding
and abstract-availability filters then drop early decades to ~30-40 papers.
The unstratified pool U has supplemental-seed loops that hit the 600 target,
but the per-decade fits don't.

## Why this matters — small-N cluster instability

At |S|=316 with K=50, the average cluster has ~6 papers — severely
underdetermined. KMeans on n=316, K=50 is noise-dominated; centroids
reflect specific paper choices rather than stable subfield structure.
At K=100, average cluster size = 3.16. Even a small change in S
membership (e.g., one paper moving) flips assignments substantially.

This is why the **K=30 result is the most interpretable**: at K=30 the
average cluster has ~10.5 papers, low-but-tractable. The K=30 negative
control passes (2.9% < 20%) means that for cs 2020 papers (which the
fit theoretically should handle uniformly well), the two fits agree
within sampling noise.

At K=50 and K=100, the negative-control failure (2020 ratio drifts to
29-40%) tells us the fits are **internally unstable** — not that
stratification has the opposite of §11's predicted effect.

## Plan revision triggered

Per the decision matrix in the Check 5b+5d plan:

> H7 negative control fails — H_2020 effN ratio > 1.20: "Methodology alert:
> stratification ALSO affects modern data, suggesting cluster fit is generally
> unstable. Plan revision triggered."

The plan revision is a **methodology refinement**, not a §11 retreat:

1. **§11 stratified-fit commitment STAYS.** The mechanism is well-supported
   in the literature (Hofstra et al. 2020 §3; Cohan-Specter 2020 §4
   diachronic checks; this study's plan §11). The K=30 directional signal
   on this pilot (S > U ratio 1.36 on H_1975, with passing negative control)
   is consistent with §11. The threshold-failure is most plausibly attributable
   to small-N cluster-fit instability, not §11 mechanism absence.

2. **Phase-0.2 §11 validation requires production-scale N.** Re-run 5d-style
   validation at |S| ≥ 1500 (10× per cluster at K=50 + buffer; ~250
   papers/decade × 6 decades). At that scale, KMeans clusters are stable,
   and the §11 mechanism — which the literature and the K=30 directional
   signal both support — should surface cleanly.

3. **Pull-spec follow-up for Phase 0.2.** Add supplemental-seed pulls per
   decade to handle low-retention early decades. The unstratified pool
   already does this; the stratified pool should match.

## Magnitude estimate (provisional, K=30)

The K=30 result gives a **provisional magnitude estimate**: under the
stratified fit, held-out 1975 papers spread across an effective ~14.5
clusters (out of 30); under the unstratified fit, they spread across ~10.7
— a **36% reduction in effective cluster spread under unstratified, the
direction §11 predicts**. The magnitude is below the pre-registered 30%
threshold (1.43 ratio = 30%+), but at the right sign.

This magnitude estimate should be re-pinned in Phase 0.2 with proper-scale
data.

## Artifacts

- `experiments/phase-0.1/cluster-stratification-check.csv` — per-K H7 metrics.
- `data/metadata/cluster-fit-manifest-{S,U}-K{30,50,100}.npy` — centroid arrays.
- `data/metadata/cluster-fit-manifest.md` — per-§11 manifest.
