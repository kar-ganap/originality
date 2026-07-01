# Phase 2.2 WS-B — cross-era drift-check gate (base 1M SciNCL + Qwen3)

**Date:** 2026-07-01 · **Verdict: GATE CLEARS — drift does NOT dominate.**
Pre-1990 semantic claims are permissible; the pre-registered **E3 fallback
(bound to post-2000) is NOT invoked.**

Desideratum §3 + the E4 gotcha: no pre-1990 semantic-diversity claim without a
cross-era nearest-neighbor sanity check on the production stack. Check 5c was a
100-query pilot on SPECTER2 (which FAILED its H7 topical audit at 66.7%,
Type-A-dominant). This is the production check on the actual 1M **SciNCL**
(primary) + **Qwen3** (cross-family) vectors.
`experiments/phase-2.2/drift_check.py`.

## Setup

- **Retrieval pool:** 3,000 papers, era-balanced (500/decade × 6, via the §11
  sampler, seed 46).
- **Queries:** 150 pre-1990 (1970–1989) CS papers, disjoint from the pool.
- **Two signals:** (1) quantitative era-match rate; (2) a topical audit of 20
  queries × top-3 SciNCL neighbors (the load-bearing signal).

## (1) Quantitative era-match

| model | top-1 era-match | top-5 mean | era-blind baseline |
|---|---|---|---|
| SciNCL (primary) | **0.60** | 0.563 | 0.333 |
| Qwen3 (cross-family) | 0.593 | 0.531 | 0.333 |

Both ≈1.8× the era-blind baseline (0.333 = 2 of 6 decades are pre-1990), and
the **two families agree** (0.60 vs 0.59) — satisfying the ≥2-families
requirement. But era-match alone is ambiguous (topic-driven vs style-driven),
so it is NOT the gate — the topical audit is.

## (2) Topical audit (SciNCL, 20 queries) — the load-bearing signal

Manual judgment of whether each query's top neighbors are **topically** related
(embedding captured the old paper's topic → low drift) vs era/style
coincidences (→ drift). Per-query verdict (`drift-check/scincl-topical-audit.md`):

- **Topically coherent (17/20):** power systems (Q1), radar/scattering (Q2),
  fault-testing (Q3), formal methods (Q5), signal-processing devices (Q6),
  manipulators (Q7), optics/holography (Q8), spacecraft/aerospace (Q9),
  biochem (Q10, coherent though field-mis-tagged), load forecasting (Q12),
  EEG/BCI (Q13), DSP filter banks (Q14), bus transit (Q15), acoustics (Q17),
  computer graphics/geometry (Q18), robotics (Q19), transit optimization (Q20).
- **Partial (1/20):** Q16 (traffic noise) — 1–2 of 3 neighbors on-topic.
- **Corpus-quality artifacts, NOT drift (2/20):** Q4 (a non-research "how to
  negotiate a publishing contract" → retrieved journal-index junk); Q11 (a
  paper whose stored abstract is mismatched to its title → nutrition text under
  a word-frequency title).

**Topical-coherence rate ≈ 85% (17/20), or ≈90% excluding the 2 corpus
artifacts** — well above Check 5c's 66.7% H7 fail line.

### Why this is a pass (and why era-match is topic-driven, not style-driven)

The audit's decisive feature: **the coherent retrievals span decades** — 1980→
2022 (power), 1973→1970/1987 (acoustics), 1989→2002 (DSP), 1985→1976/1989
(robotics), 1974→1990 (formal methods). Cross-era *topical* retrieval is the
signature of LOW drift: SciNCL places a 1975 paper near topically-similar
papers of *any* era, rather than dumping all old-style text into a stylistic
corner (which is the SPECTER2 failure mode Check 5c found). The 0.60 era-match
is therefore explained by **era-correlated topics** (SAW/CCD devices,
asynchronous machines, etc.), not a style artifact.

## Gate decision

**CLEARS.** SciNCL (and, agreeing, Qwen3) retrieve topic-coherent neighbors
across eras on pre-1990 CS papers. The E3 post-2000 bound is **not** invoked;
Phase 2.2 may make pre-1990 semantic-diversity claims, with the caveats below.

## Caveats surfaced (document in Methods/Limitations)

1. **Era-match ≠ drift-free by itself** — the topical audit, not the 0.60 rate,
   is what clears the gate. Reported as such.
2. **Pre-1990 corpus-quality tail (NEW finding, separate from drift):** the
   audit incidentally exposed a non-trivial junk/contamination tail in pre-1990
   CS — a non-research administrative paper (Q4), a mis-tagged biochem paper
   (Q10), and a mismatched-abstract paper (Q11), plus publisher-chrome
   abstracts (Q8's "Get PDF Email Share…"). This is field-contamination +
   corpus cleanliness (tied to the score≥0.40 threshold), not embedding drift.
   It adds noise to early-year metrics — worth a per-year sanity pass in WS-C /
   a Limitations note, and possibly a stricter early-year concept-score filter
   as a robustness variant.
3. Judgment is a single-reviewer topical audit (as in Check 5c); the dump
   (`scincl-topical-audit.md`) is committed so the calls are auditable.

## Artifacts

- `experiments/phase-2.2/drift_check.py` — the check.
- `experiments/phase-2.2/drift-check/drift-check-results.json` — era-match stats.
- `experiments/phase-2.2/drift-check/scincl-topical-audit.md` — the audited
  query→neighbor sample (the auditable record).
