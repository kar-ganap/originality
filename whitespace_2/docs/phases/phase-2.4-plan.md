# WS2 Phase 2.4 — the per-capita V-extension (empirical anchor for WS3 Core Claim 6)

**Stage:** 3 (Run) · **Branch:** `phase-2.4-v-extension`
**Status:** IN PROGRESS (2.4a data spine).
**Pre-registration:** the instrument is fully specified in
`whitespace_3/docs/primers/v-extension-empirical-spec.tex` — 5 hypotheses, 3 structural
measures (2 embedding-free), 3 negative controls, the confound list, the robustness
grid, gates, escape hatches, and an interpretation matrix. **This doc does not
re-plan; it records the data-access reality + the decomposition + logs.** Unlocked by
WS3 rung 4b, which sharpened Core Claim 6 into a concrete `W↑`-with-`V^struct↓`
prediction (the empirical loop is now closed).

## The one-sentence test
Measure, per author/team and per year, how far scientific output strays from the
canonical way of building on prior work; **Core Claim 6** predicts per-capita
*structural* novelty `V^struct` declines (steepest where the canon concentrates —
Physics) while per-capita *topical* novelty `V^lat` does not.

## Data access reality (verified 2026-07-07 — the spec's "~$0, all existing")
- **Corpus + vectors live on Modal**, not local (local `data/` = 80M smoke). Pulled:
  `ws2-section0/section0-sample-1M-v3.parquet` (1M rows, 1.2GB) — has
  `referenced_works_json`, `authorships_json`, `concepts_json`; and
  `ws2-embeddings/base-1m/{scincl,qwen3}-vectors.npy` (→ `V^lat`),
  `specter2-vectors.npy` (→ `V^struct` embedding arm), K=50 cluster assignments.
  The base-1M `metadata.parquet` (paper_id/year/field, 902,531 in-window) is the
  alignment key + field label.
- **Reference coverage ≈ 50%, and roughly STABLE over 1970–2024** (0.44–0.62 by
  half-decade; authorships 99%). So structural measures run on the ~450k papers that
  carry references; the coverage is time-stable enough not to fabricate a trend, but
  is **logged and controlled** (report the with-refs subset trend + coverage-by-year).
  This is the spec's anticipated risk; its escape hatches (widen `w`, restrict window)
  are available if the in-sample forward graph proves too sparse early.

## Decomposition
- **2.4a — Data spine (this step).** `src/whitespace2/v_extension.py`: parse the
  corpus → paper-level panel (team size, subfield, refs, author ids, ORCID/country,
  field); invert `referenced_works` → the **in-sample forward-citation graph**
  (`forward_uptake`, windows {3,5,10}, age-restricted). TDD on toy data (parse +
  citation inversion). Artifact: `data/base-1m/panel-2.4.parquet` (regenerable; not
  committed — reproducibility rule).
- **2.4b — Measures.** Off-canon reference share (`1−γ̂` vs the canon `K(t)`, no
  look-ahead), Uzzi reference-atypicality (degree-preserving null), the persistence
  filter (within-(field,year) thresholds) — the embedding-free headline; then topical
  `V^lat` (SciNCL, Qwen3 robustness) + SPECTER2 structural (the embedding arm).
- **2.4c — Estimation.** The panel regression (author-FE + field-FE, `log T` + `log
  volume` controls), permutation inference + absolute magnitude + VIF; the 5
  hypotheses; the 3 negative controls (year-shuffle, random-canon, pure-noise); the
  robustness grid.
- **2.4d — Retro + interpretation** — read the outcome onto WS3 via the spec's
  interpretation matrix (confirm / falsify / relocate the κ mechanism).

## The one data decision (pre-registered)
Persistence forward-citations = the **in-sample graph** (primary, $0). The OpenAlex
forward-citation pull is held as *optional robustness* only if in-sample coverage
looks like an artifact — a bounded API job, logged, never silently applied.

## Gates (from the spec)
Instrument validity (3 structural measures pairwise-correlated; topical tracks the
Phase-2.2 `W`) → negative controls pass (random-canon specifically kills the
structural trend) → **headline** (`V^struct↓` on ≥2 measures, permutation-sig +
material magnitude, *and* `V^lat` spared) → mechanism + gradient. Every outcome is
informative; either headline direction is reported honestly.
