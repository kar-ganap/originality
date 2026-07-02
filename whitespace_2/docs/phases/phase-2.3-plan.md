# Phase 2.3 Plan — the subfield mechanism test (WS2's "single most important analysis")

**Phase:** 2.3 — subfield mechanism test
**Stage:** 2 → 3 (Walk → Run close-out)
**Branch:** `phase-2.3-subfield` (off `main` @ `273ceb3`)
**Status:** PLAN (pre-registration). Cost: **$0** — all inputs are local
(base-1M vectors, K=50 assignments, 1M source corpus, regenerated demographic
substrate); no Modal downloads, no API, no embed.

---

## Amendment (execution, 2026-07-01) — SPECTER2 3rd family

The 4-spec grid ran first and flagged a Physics-only positive γ₁ under SciNCL
that reversed under Qwen3. Per user request ("run a third embedding model"), the
pre-committed Stage-3 robustness family **SPECTER2** was embedded on the 1M
sample (~$3, Modal) and added → a **6-spec grid** + an **aggregate 3-family**
escalation. SPECTER2 adjudicated the Physics wrinkle (refuted) and — after a
"verify first" pass (adapter active; not drift; ill-conditioned-σ caught) —
refined (did not overturn) the Phase-2.2 reframing. See
`docs/phases/phase-2.3-retro.md`.

## One-line scope

Test the pre-registered **subfield mechanism** (`docs/conceptual.md` line 35:
*"probably the single most important analysis in the paper"*): **do
canon-concentrated subfields show more demographic–semantic divergence than
diffuse ones?** Regress a subfield's divergence magnitude on its canonical
concentration, **controlling for log subfield size**. Under the Phase 2.2
reframing (canon concentrates *independently* of a diversifying frontier +
authorship) the slope γ₁ should be ≈ 0 (**flat → supports the reframing**); a
robust **positive** slope would localize a narrowing mechanism (the last place a
narrowing signal could still hide after the aggregate null).

## Why this phase exists (post-Phase-2.2)

Phase 2.2 robustly **disconfirmed Claim #13 in aggregate** and reframed it: the
citation canon concentrates while the semantic frontier and authorship both
diversify. Two things remain before WS2 can wrap:

1. The aggregate null does not rule out a **localized** mechanism — that
   narrowing is concentrated in the subfields with the most ossified canon,
   and averages out across the field. This is exactly the actuator-sharing /
   homogenization mechanism the program hypothesizes, and the subfield test is
   its direct within-field probe.
2. The reframing predicts **independence** (concentration ⟂ divergence). A flat
   γ₁ across specifications is the affirmative evidence for that independence,
   not merely the absence of an aggregate signal.

`γ₁ ≈ 0` challenges the actuator-homogenization *structural* claim at the
phenomenon level (conceptual.md §"What ws2 specifically contributes", point 1)
and narrows the ws1 simulation's mechanism space (point 3).

## Design (pre-registered)

### Unit of analysis — a subfield `s`

Two subfield definitions (both named in `conceptual.md` + `tasks/todo.md`;
reported as a **robustness pair**, neither cherry-picked):

- **PRIMARY — OpenAlex level-1 sub-concepts.** Within each field's papers
  (CS / Physics via `extract_primary_field`), assign each paper to its
  **highest-scoring `level==1` concept** (excluding the level-0 field roots),
  read from `concepts_json`. Subfield key = `(field, level1_concept_id)`.
  Interpretable ("Machine learning", "Cryptography", "Condensed matter
  physics"); **independent of the SciNCL embedding**, so the semantic-diversity
  metric is not measured on the same construct that defines the partition (no
  circularity).
- **ROBUSTNESS — §11 K=50 SciNCL clusters** (`scincl-cluster-assignments.npy`,
  already fit). Data-driven, non-overlapping, purely semantic. Circular-adjacent
  (a cluster is semantically tight by construction), hence robustness not
  primary. 50 units.

Subfield **inclusion filter** (pre-registered, no silent drops — the count
kept/dropped is reported): ≥ `N_MIN = 2000` papers **and** ≥ `Y_MIN = 20`
publication-years with a computable semantic + demographic value, over the
analysis window. A per-(subfield,year) semantic value needs ≥ `N_YEAR_MIN = 30`
papers; below that the year is NaN'd out of that subfield's trend.

### Window

**1970–2023.** The incomplete final year **2024 is trimmed** (it drops across
all Phase-2.2 panels; `tasks/todo.md` publication-figure note).

### Per-subfield quantities

1. **`canon_concentration(s)` — the LEVEL of canonical concentration** (the
   predictor). Mean over the subfield's years of `reference_canonicity`
   `ref_gini` (how unequally references pile onto a few canonical works within
   the subfield) — the operationalization of *"clear canonical concentration
   (dominant textbook or foundational paper)"*. Secondary predictors reported:
   mean `ref_top_k_share`; mean top-N=50 canon-stability `canon_spearman_d5`.
   Uses the existing `canonical_metrics.reference_canonicity` on the subfield's
   `referenced_works`.
2. **`semantic_trend_sd(s)`** — standardized slope (`standardized_effect`
   `total_change_sd`, σ over the window) of the subfield's per-year
   **`mean_pairwise_cosine_distance`**. Chosen because it is the retro's
   **most robust** semantic metric (rose in both fields across all 5 Phase-2.2
   configs) and the only one **comparable across embedding families** and
   **computable under both subfield definitions** (`cluster_entropy` is
   degenerate within a single K=50 cluster). Per-year N-capped subsample
   (`N_CAP = 3000`, seeded) to remove the N-confound, mirroring
   `compute_series.py`. Computed on **SciNCL (primary)** and **Qwen3
   (robustness)** — the ≥2-embedding-families caution.
3. **`demographic_trend_sd(s)`** — standardized slope (σ) of the subfield's
   per-year joint `career_joint_shannon` from `build_joint_plurality_series`,
   driven by a **paper→subfield map** (same schema as `build_paper_field_map`,
   so the existing demographic pipeline is reused verbatim — `field` is an
   opaque grouping key).
4. **`divergence_magnitude(s)` — the HONEST, absolute-based divergence** =
   `demographic_trend_sd − semantic_trend_sd`. Larger ⇒ demographic outpaces
   semantic more (the "narrowing" direction). **NOT the Phase-2.2
   ratio-slope** — the ratio≠control lesson: a ratio conflates "semantic
   declined" with "semantic rose slower". We separate the two absolute trends
   and difference them.
5. **`log_size(s)`** = log10(subfield paper count) — the **required control**
   (close-read 01; controls for field-growth / publication-volume confounds).

### The estimator (the test)

OLS, subfields as observations:

```
divergence_magnitude(s) = β0 + γ₁·canon_concentration(s) + β2·log_size(s)  [+ field FE]
```

- **γ₁** is the coefficient of interest (the conceptual doc's γ₁).
- Pooled CS+Physics with a **field fixed effect** for the sub-concept
  definition (subfields keyed by `(field, concept)`); per-field slopes also
  reported. Clusters span fields → run field-agnostic (50 units), with a
  majority-field FE as a sensitivity.
- **Inference — permutation null** (the subfield count is small, so no
  asymptotic-t): permute `canon_concentration` across subfields `N_PERM = 10⁴`
  times, refit, γ₁'s two-tailed permutation p = fraction of |permuted γ₁| ≥
  |observed| (add-one smoothed). OLS 95% CI reported alongside.
- **VIF(`canon_concentration`, `log_size`)** reported — the collinearity
  caution (small subfields may carry more concentrated canons). γ₁ with VIF ≳ 10
  is flagged unreliable, exactly as WS-F's residual regression was.
- Also report the **standardized** γ₁ (per-SD-of-canon change in
  divergence-SD-units) so "≈ 0" has a magnitude, not just a p-value.

### Specifications (robustness grid)

`{SciNCL, Qwen3} embedding × {sub-concepts, K=50 clusters} subfield` = **4**
primary specs. γ₁ (sign, magnitude, permutation p, VIF) reported for all four.

### Decision rule (pre-registered)

- **SUPPORTS THE REFRAMING (independence):** γ₁ **not** permutation-significant
  **and** |standardized γ₁| small (< ~0.3σ per canon-SD) in **both embedding
  families and both subfield definitions**. → canon-concentration does not
  predict demographic–semantic divergence; concentration and frontier/authorship
  diversity are independent. Consistent with a flat γ₁ ⇒ the aggregate null is
  not masking a localized narrowing.
- **LOCALIZED MECHANISM:** γ₁ **positive**, permutation-significant, and
  **consistent in sign across all four specs**. → canon-concentrated subfields
  narrow more; the actuator mechanism is real but localized.
- **MIXED / INCONCLUSIVE:** signs disagree across specs, or significant in one
  family and reversed in the other (the Phase-2.2 effective-dim-under-Qwen3
  failure mode). → reported honestly as metric/definition-dependent, NOT
  cherry-picked to a favorable spec.

### Cautions carried (hard-won, `tasks/lessons.md`)

1. **Ratio ≠ control** → divergence is `demographic_sd − semantic_sd` (absolute
   trends differenced), never the confounded ratio.
2. **Report VIF** on the regression (`canon` vs `log_size` collinearity).
3. **≥2 embedding families** (SciNCL + Qwen3); a single-family signal that
   reverses on swap is not a finding.
4. **Verify extreme claims** — if γ₁ comes out large/striking, cross-check the
   component trends before believing it.
5. **Trim the incomplete final year** (2024).
6. **Small-N-of-subfields** → permutation inference, not asymptotic t.
7. **Negative control intact at subfield grain** — pooled canonical
   concentration must still rise over time (substrate sanity).

## Evaluation criteria / gates (pre-registered "done")

- **G1 — substrate sanity:** pooled canonical concentration (reference-canonicity
  Gini) rises over 1970–2023 at the subfield grain (permutation-significant).
- **G2 — estimator correctness (TDD):** the new `subfield_divergence` src module
  (paper→subfield map builder + `subfield_regression` with permutation γ₁ + VIF +
  standardized γ₁) is unit-tested against independent computation, incl. a
  **synthetic case with a known planted γ₁** (recovered within tolerance) and a
  **null case** (γ₁ ≈ 0, permutation p ≳ α). Tests first.
- **G3 — full grid reported:** γ₁ (sign, magnitude, permutation p, VIF, standardized)
  for all 4 specs + per-field slopes + secondary canon predictors, written to
  `experiments/phase-2.3/subfield-mechanism-results.md` + a `.json`.
- **G4 — verdict** stated per the decision rule, with the component trends shown
  (so an extreme γ₁ is auditable).
- **G5 — tests + lint + typecheck clean** (≥ 249 + new, ruff + mypy strict).

## IMPLEMENT order

1. **PLAN** — this doc (pre-registration). Commit before any regression is run.
2. **TEST** — `tests/test_subfield_divergence.py`: paper→subfield map (level-1
   argmax, tie/empty handling), `subfield_regression` (planted-γ₁ recovery, null
   γ₁, VIF, permutation p, standardized γ₁). Red.
3. **IMPLEMENT src** — `src/whitespace2/subfield_divergence.py`:
   `extract_primary_subconcept` + `build_paper_subfield_map` (mirrors
   `build_paper_field_map`) + `subfield_regression`. Green.
4. **COMPUTE** — `experiments/phase-2.3/`:
   - `build_subfields.py` → the two paper→subfield maps on the source corpus.
   - `compute_subfield_metrics.py` → per-subfield canon + semantic trend
     (SciNCL & Qwen3) + demographic trend + log_size, for both definitions.
   - `run_subfield_test.py` → the 4-spec regression grid + verdict → results md/json.
5. **VERIFY** — component-trend audit; negative-control (G1); cross-check any
   striking γ₁; confirm gates.
6. **RETRO** — `docs/phases/phase-2.3-retro.md`.

## Data (all local — $0)

| Input | Path (session scratchpad symlinks) | Provenance |
|---|---|---|
| SciNCL + Qwen3 vectors, metadata, K=50 assignments | `embed-1m/` | Modal `ws2-embeddings /base-1m/` (cached) |
| Source corpus (`concepts_json`, `referenced_works_json`) | `section0-sample-1M-v3.parquet` | Modal `ws2-section0` (cached) |
| Demographic substrate (`authorships`, `corrected` w/ `min_year`+`primary_country`, `paper-field`) | `demog-v3-ws2/` | `run_pipeline.py --reuse-matrix … --no-genderize` (cached) |

Regenerate substrate if the cache is lost: `run_pipeline.py --source
section0-sample-1M-v3.parquet --reuse-matrix experiments/phase-1.3/
v3-confusion-matrix.json --no-genderize --n-bootstrap 100 --outdir <dir>`.

## Companion documents

- North star: `docs/conceptual.md` (line 35 subfield test; §"What ws2
  contributes" γ₁≈0 interpretation).
- Pre-registered aggregate test + framework: `docs/phases/phase-2.0-plan.md` §5.
- The reframing + cautions: `docs/phases/phase-2.2-retro.md`, `tasks/lessons.md`.
- Results (to be written): `experiments/phase-2.3/subfield-mechanism-results.md`.
