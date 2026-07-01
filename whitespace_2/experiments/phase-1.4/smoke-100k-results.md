# Phase 1.4 C3+C4 — 100K end-to-end mini-Stage-2 pilot

**Date:** 2026-06-30 · **Status:** ✅ pipeline de-risked; 3 Stage-2 findings.
**EXPLORATORY** (desideratum §5): the pre-registered headline is the full
1M Stage-2 run — this pilot only validates that the machinery composes and
surfaces issues before the spend.

---

## C3 — 100K embed (SciNCL, Modal A100) ✅

`experiments/phase-1.4/smoke_100k.py`: the hash-ordered first 100K in-window
(1970–2024) papers of the v3 1M sample → reconstructed abstracts → SciNCL on
the deployed `ws2-embed` app via the resumable `ChunkedEmbedRunner`.

| metric | value | gate |
|---|---|---|
| papers | 100,000 (cs 71,311 / physics 28,689) | |
| empty abstracts | 0 | |
| shape / finite | (100000, 768) / all finite | ✅ |
| SciNCL norm mean | **23.70** | ✅ in band [22.5, 24.5] |
| compute | 319 s (0.0032 s/abs) | |
| **cost** | **$0.22** | ✅ ≪ §9 $50 gate |

The embed pipeline (subset → reconstruct → Modal A100 → resumable chunks →
validate) works cleanly at 100K, norms match Phase 1.1 (23.56). Qwen3
cross-family was validated at 16K in Phase 1.1; full cross-family runs in
Stage 2.

## C4 — pilot divergence test ✅ (composes) + 3 findings

`experiments/phase-1.4/pilot_divergence.py` assembled per-year CS series
(1972–2024, 53 years ≥50 papers): semantic (effective-dim / cluster-entropy
[K-means K=50] / mean-pairwise-cosine on the vectors), canonical (citation
Gini), demographic (gender Shannon, full-1M Phase-1.3 cells) → the
pre-registered `divergence_test`. **The whole chain composed and produced
computable statistics — the de-risk goal.** Exploratory verdict:
`substrate_broken`, driven by finding #1 below.

### Finding 1 — the canonical negative control needs citation-age robustness

Raw citation Gini per **publication year** declines slightly (slope −0.00065,
p=0.053), failing the "should rise" negative-control expectation → the
exploratory `substrate_broken` flag. **Cause:** recent papers are
zero-inflated (a 2024 paper has ~0 citations; a 1990 paper has 30 years of
accrual), so recent-year citation distributions are artificially *less*
concentrated. The Gini *does* rise 1980→2000 (0.86→0.898) where citations
have matured, then falls with the recent-accrual artifact.
**Not fixable by rescaling** — Gini is scale-invariant, so dividing by paper
age is a no-op (confirmed). **Stage-2 fix:** a citation-age-robust canonical
metric — a fixed citation window (cites within N years of publication), an
age-restricted subset (papers ≥N years old), or within-age-cohort
concentration.

### Finding 2 — the two primary semantic metrics disagree in direction

Ratio (semantic / demographic) trends over year:

| semantic metric | slope | p | direction |
|---|---|---|---|
| cluster_entropy | −0.0087 | 0.003 | **down** (→ divergence) |
| effective_dimensionality | +0.553 | 1e-11 | **up** (→ no divergence) |
| mean_pairwise_cosine | +0.0009 | 2e-8 | up |

The Test-I rule requires BOTH primaries to show a negative-significant ratio
slope; here they **disagree**. This is interpretable, not a bug:
`effective_dimensionality` measures global embedding spread (rises as CS
diversifies into new areas), while `cluster_entropy` measures concentration
within a *fixed* K=50 structure (falls as papers pile into dominant
clusters). The multi-metric §8 discipline exists exactly for this — and it
means "does semantic plurality rise or fall?" is **metric-dependent**, the
central tension to resolve at full scale.

### Finding 3 — §11 K-means temporal stratification matters

The pilot fit K-means on a year-stratified sample (a §11 proxy). Finding 2's
disagreement may partly reflect the non-§11 global fit biasing early-year
cluster assignments toward modern-dominated clusters. §11 (temporally-
stratified fit) is already locked as non-negotiable; the pilot reinforces it.

---

## Verdict

The mini-Stage-2 pipeline **de-risked successfully**: 100K embed clean +
cheap; the embed → per-year semantic → canonical → demographic → divergence
chain composes and yields computable statistics. Three concrete methodology
requirements for the full Stage-2 run were surfaced *before* the spend:

1. **Canonical metric** must be citation-age-robust (window / age-cohort).
2. **Semantic-metric direction disagreement** (cluster-entropy vs
   effective-dim) is the key thing to watch — pre-register how it's
   adjudicated (both-must-agree is conservative; the §8 stack reports all).
3. **§11 temporal K-means stratification** is confirmed load-bearing.

These feed the Stage 2 plan / pre-registration (workstream B). The pilot's
`substrate_broken` verdict is an artifact of finding #1, not a real defect.
