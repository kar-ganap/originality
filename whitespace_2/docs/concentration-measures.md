# Concentration measurement — requirements and spec

**Written 2026-07-22, before measuring.** Every requirement below is derived from a specific
failure in this program, not chosen for elegance. The point of fixing them in writing first is that
the metric cannot be swapped after the result is seen.

## Why the existing metrics failed

| metric | where | failure |
| --- | --- | --- |
| `ref_gini` | WS2 primary | Gini over *observed* reference-target multiplicities. A repeat-rate statistic: 93% of its trend is reproduced by uniform random attachment, it correlates `+0.999` with edges-per-distinct-target, and it never leaves the near-all-singletons regime (0.013–0.060) where a real citation distribution sits at 0.8–0.99. |
| `age_restricted` Gini | WS2 substrate gate | Uses **all-time** `cited_by_count` with only a minimum-age filter. Its own docstring concedes "a residual accrual gradient remains": a 1970 cohort has had 55 years to accrue, a 2015 cohort 10. Trend across cohorts confounds concentration with accrual time — the same defect that made the CD-index reverse under a fixed window. |
| `P_top4` | polyphony R4 | Fixed-`k` share of a *growing* catalog (13→48). Falls by construction; the registered effect is over-reproduced by a no-preference null at 151%. |
| participation-ratio effective dim | canary | Exactly scale-invariant, therefore structurally blind to uniform contraction — i.e. to the thing it was used to detect. |

Four different metrics, one recurring shape: **the statistic moved because the corpus grew.**

## Requirements

- **R1 — Canon-scale range.** The measure must be able to express both "no canon" and "strong
  canon," and the observed values must land somewhere a canon could actually be. A metric pinned in
  its bottom 5% of range is not measuring the construct.
- **R2 — No growing denominator.** Either the pool is fixed, or the statistic is explicitly
  normalized by its pool, and which one is primary is declared before running.
- **R3 — Sample-size invariance.** Subsampling papers within a year must not move the estimate
  beyond noise. Tested directly, not assumed.
- **R4 — Fixed observation window.** Every cohort gets the same accrual opportunity. Where the data
  cannot supply this, say so rather than substituting an age filter.
- **R5 — Matched null, reported.** Re-run the generating process with the preference removed and
  report the excess. A concentration number without its null is not reportable.
- **R6 — Replay-validated.** The implementation must reproduce the committed series it claims to
  correct, before it is trusted to correct it.
- **R7 — Field discrimination.** CS and Physics differ on real concentration. A measure that
  assigns them the same trend is not sensitive to the construct.
- **R8 — At least two measures** (`docs/desiderata.md` §8), of different functional form, reported
  together including when they disagree.

## What the local data can and cannot support

The 1M local sample retains only **1.93%** of reference edges inside the population, so
citation-*received* in-degree cannot be reconstructed locally. A properly windowed
citations-received measure (R4) therefore **requires the 24M population** on the `ws2-section0`
Modal volume, as WS3's bridge C used (46.7% in-population). That is scoped, not done.

Out-edges are complete — every reference every sampled paper makes is visible, including to targets
outside the sample: **13,024,302 edges over 6,504,930 distinct targets.** That supports the
measures below.

## The measures

### M1 — `canon_share_K` (primary)

At year `t`, define the canon `C_t` as the top-`K` targets by cumulative citations received **from
papers published strictly before `t`**. Then

    canon_share_K(t) = (year-t reference edges landing in C_t) / (all year-t reference edges)

- **R1** — ranges over [0, 1] and can express any concentration level.
- **R2** — `K` is fixed and the denominator is year `t`'s own edge count, so the statistic cannot
  drift because the corpus grew. This is the defect that killed `ref_gini`, removed by construction.
- **R4** — `C_t` is built only from the past, so no year's canon is defined using its own edges;
  there is no selection on the outcome.
- Reported at `K ∈ {100, 1000, 10000}` — a canon claim should not hinge on the cutoff.

### M2 — `canon_entropy_deficit` (secondary, different functional form)

`1 − H(p_t) / log(K)`, where `p_t` is the distribution of year-`t`'s canon-directed edges across the
`K` canon slots. M1 asks how much attention reaches the canon; M2 asks how unevenly it is spread
*within* it. A canon that concentrates should move both.

### The null

Year `t`'s edges are re-drawn with the canon preference removed: each edge attaches to a target
sampled from the pool of previously-seen targets **in proportion to nothing** — every prior target
equally likely. The null therefore keeps the year's edge count and the prior target universe, and
destroys only the tendency to revisit established works. Report observed, null, and excess.

## Validation battery — all four run before any claim

1. **Sample-size invariance (R3).** Recompute on a 500-paper subsample of each year; the estimate
   must not shift systematically with cohort size.
2. **Denominator-confound check.** Correlate the measure with edges-per-distinct-target — the
   quantity `ref_gini` correlated with at `+0.999`. A near-zero correlation is required.
3. **Field discrimination (R7).** CS versus Physics must be allowed to differ.
4. **Null comparison (R5).** Observed trend against the matched-null trend, with the share of the
   trend the null reproduces stated as a percentage.
