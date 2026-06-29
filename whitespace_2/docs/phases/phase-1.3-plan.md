# Phase 1.3 Plan — Author disambiguation + demographic inference

**Stage:** 1 — Crawl
**Phase:** 1.3 — third phase of Stage 1
**Window opens:** 2026-06-29
**Branch:** `phase-1.3-execution` (cut from `main` post-Phase-1.2 merge)
**Status:** Plan in progress. TEST → IMPLEMENT → VERIFY → RETRO discipline.

---

## Stage 1 (Crawl) — overview

| Phase | One-line scope | Status |
|---|---|---|
| 1.1 | Compute substrate + 50K dry-run | ✅ COMPLETE |
| 1.2 | Production pull via bulk dump + v3 §0 corpus (24.5M) | ✅ COMPLETE |
| **1.3** | **Author disambiguation + demographic inference** | **CURRENT — this plan** |
| 1.4 | Pre-Stage-2 quality gates + transition signoff | Stub |

---

## Phase 1.3 — One-line scope

**Take the v3 §0 corpus (24.5M papers; `authorships` field
projected), produce per-author and per-paper demographic
annotations using gender_guesser (primary), Genderize (cross-
validation), and NamSor (bias estimation, NOT direct labeling),
and apply a §9e-style propensity correction for selection
bias.** Final output: enriched parquet ready for Stage 2 with
per-cell demographic coverage tables + sensitivity bounds.

This is the **last data-substrate phase** before Stage 2
embedding. Phase 1.4 then runs sanity gates on the production
data before Stage 2 starts.

---

## Why this phase exists

The headline ws2 test (Claim #13: intellectual plurality
decoupling from demographic plurality) needs **time-series of
per-cell demographic diversity** computed on the analytical
population. To do that we need: (a) per-paper author lists with
stable IDs, (b) demographic attributes attached to each author
(gender + country at minimum), and (c) per-cell coverage
estimates with uncertainty bands so the headline test can
distinguish signal from inference noise.

Phase 0.2 Wave 3A locked the ORCID-linkage validation methodology
(98.6% per-region agreement on the §9a P5 ground-truth subsample).
Phase 0.2 Check 3 locked the gender-inference stack
(gender_guesser primary + Genderize cross-validation) plus a
NamSor escalation commitment with $0-$500 budget. This phase
applies all three at production scale.

**Methodology amendment vs Phase 0.2 commitment:** NamSor's role
is locked here as **bias estimation for a §9e-style correction**,
NOT direct labeling of every low-confidence name. Rationale: at
production scale (~60K-200K low-confidence names), direct
labeling would cost $50-200+ and produce point estimates with no
quantified uncertainty. Sample-based bias estimation costs ≤$10
and produces principled per-region CIs that integrate cleanly
into the §9e four-layer defense pattern. See §3 below for the
escape hatch if quality concerns surface.

---

## Pre-registered hypotheses

### Layer A — pipeline correctness (abort-on-fail)

- **H1: Disambiguation cross-era-merger rate ≤ 5%.** Per Phase
  0.1 §10. Measured via career-length screen on the v3 corpus
  (papers spanning >60 years for a single author.id flagged
  for inspection).
- **H2: ORCID cross-validation agreement ≥ 95%.** Wave 3A
  measured 98.6% on the §9a P5 subsample (~3.6K author pairs).
  At production scale (~5-10× larger ORCID-validated subset),
  agreement should hold. Failure mode: OpenAlex disambiguation
  systematically diverges from ORCID for some sub-population.

### Layer B — demographic coverage + bias estimation

- **H3: Gender coverage ≥ 45% on P_demo.** Per Phase 0.1 Check
  1f baseline (50% pre-fix; post-fix expected ~45%). Measured
  per-cell (year × field × region).
- **H4: Country coverage ≥ 50%.** Affiliation-derived; depends
  on OpenAlex's `institutions.country_code` field completeness.
- **H5: NamSor stratified sample (N=2,500) yields per-region
  bias estimates with CI half-width ≤ 10pp.** This is the
  central methodology test for Option B. Failure → escape hatch
  (§3).
- **H6: NamSor spend ≤ $10.** Hard budget gate. Failure → stop
  + replan.

### Layer C — output validity

- **H7: Per-cell sample sizes meet minimum thresholds for the
  bias correction.** Specifically: each (year × field × region)
  cell that contributes to the headline divergence test has
  ≥10 NamSor-validated names. Cells below threshold flagged for
  targeted oversampling within the H6 budget.
- **H8: Bias-corrected estimates' uncertainty is tight enough
  to support the headline divergence test.** Specifically: the
  per-cell demographic-diversity CI half-width is small enough
  that a 5pp year-over-year change is distinguishable from
  inference noise. Concrete threshold: per-cell CI half-width
  ≤ 2.5pp on the headline cells.

---

## Pre-flight choices already locked

Carryover from Phase 0.2 + Phase 1.2:

- **Corpus**: v3 (24,492,279 papers) primary; v2 (38,697,769)
  retained as robustness pair. Per `experiments/phase-1.2/
  h2-audit-results.md` §3, Stage 2 will run on both — so Phase
  1.3 produces demographic annotations on **both** corpora.
- **Disambiguation primary key**: OpenAlex `authorships[*].
  author.id`. We adopt OpenAlex's disambiguation rather than
  rolling our own.
- **Gender stack**: gender_guesser primary (offline,
  deterministic), Genderize keyed-free cross-validation (2,500/mo
  tier; user-provided key), NamSor bias estimation (Option B per
  §3 — sample-based, not direct labeling).
- **Country extraction**: `authorships[*].institutions[*].
  country_code` (already in v3 parquet via Phase 1.2's
  `_KEEP_FIELDS`).
- **ORCID-linkage validation**: Wave 3A 98.6% per-region
  agreement on §9a P5 ground-truth subsample.
- **§9e propensity-model framework**: per ws2 desideratum §9e
  (Phase 0.1 N1 plan revision; established the four-layer
  defense pattern that Phase 1.3 plugs the NamSor bias
  correction into).

---

## NamSor scope — Option B locked + escape hatch

### Option B (locked)

NamSor is used to **estimate per-region bias of gender_guesser**,
not to directly label every low-confidence name.

**Procedure:**
1. After running gender_guesser + Genderize on the full corpus,
   identify low-confidence names (neither method assigns at
   p≥0.8).
2. Stratify low-confidence names by **script/region**: East
   Asian (CJK), Slavic (Cyrillic + Latin transliteration),
   Arabic, South Asian, Latin-script-other.
3. Draw a stratified random sample of **~2,500 names total**
   (within NamSor's free tier).
4. Submit to NamSor; record per-name gender attribution.
5. For each stratum: compute gender_guesser's per-region bias
   (false-positive rate by gender × refusal rate) with CI.
6. Apply per-region bias correction to gender_guesser outputs
   across the full corpus → corrected per-cell gender
   distribution + uncertainty bands.

**Budget**: ≤$10 reserve for targeted oversampling if a
particular cell underperforms (e.g., physics × pre-1990 ×
Asian-name cell has <10 NamSor samples and the headline test
relies on it).

### Escape hatch — when to revisit

Pre-registered trigger conditions. If ANY fires during VERIFY,
stop and re-evaluate before locking Phase 1.3 → Phase 1.4:

| # | Trigger | Threshold | Escalation |
|---|---|---|---|
| **E1** | Per-region bias CI half-width too wide | >10pp at N=2,500 | Expand stratified sample (more NamSor; still within free tier OR within $10 budget) |
| **E2** | Headline divergence sensitivity to bias-correction parameters too high | >30% change in the divergence statistic when bias-correction params perturbed within their CIs | Escalate to direct labeling of all low-confidence names (Option A); pre-commit estimate $50-200 in `tasks/spend.md` first |
| **E3** | Specific year × field × region cell has insufficient NamSor sample | <10 NamSor-validated names in any headline cell | Targeted oversampling for the under-sampled cell (~100-500 extra calls; should fit within $10) |
| **E4** | NamSor API quality issues surface (rate limit, accuracy concerns from cross-checks) | Any | Pause Phase 1.3; revisit methodology; possibly fall back to gender_guesser-only with "unknown" propagation (zero-cost, methodologically conservative — accepts lower coverage in exchange for no inference risk) |

**Escape-hatch ground rules:**
- Triggers are objective and measurable. Don't soft-pedal a
  trigger by re-interpreting the threshold.
- E2 is the most expensive escalation; pre-commit the cost
  estimate in `tasks/spend.md` before any Option A spend
  exceeds $50 (per ws2 desideratum §9).
- E4 is the methodological-conservatism escape — costs nothing
  but produces a corpus with more "unknown gender" rows. Per
  desideratum §4's "characterize coverage/confidence per
  variable; sensitivity bounds on headline numbers", this is a
  defensible fallback even if it limits per-cell granularity.

---

## TEST plan — written before IMPLEMENT

### Local unit tests for the annotation pipeline (~6 tests)

In `tests/test_demographics.py` (new file):

1. `test_explode_authorships_produces_one_row_per_author_paper` — given a 3-paper mock corpus with varying author counts, exploded table has correct row count + per-row author.id + paper-id binding.
2. `test_gender_guesser_assignment_threshold` — confidence threshold p≥0.8 correctly classifies known male/female test cases + correctly returns "unknown" on ambiguous test cases.
3. `test_country_extraction_handles_missing_institutions` — papers with null institutions, single institutions, multi-institutions all produce correct country sets.
4. `test_low_confidence_subset_identification` — given gender_guesser + Genderize outputs on a mock batch, correctly identifies the subset where neither method assigns at p≥0.8.
5. `test_stratified_sampler_respects_strata_counts` — given 1000 names tagged by script/region, the stratified sampler returns N=200 with correct per-stratum proportions.
6. `test_bias_correction_arithmetic` — given a mock bias-correction table (per-region false-positive/refusal rates) and a mock gender_guesser output, produces correctly-corrected aggregate gender distribution with CI.

### Local end-to-end smoke (~1 test, ~30 sec)

`test_demographics_pipeline_end_to_end` — process a 500-paper
synthetic corpus through the full pipeline (explode →
gender_guesser → Genderize-mock → low-confidence sub-set →
NamSor-mock with fixed bias → §9e-style correction → coverage
table). Assert: shape of output table, presence of expected
columns, sum of per-cell counts equals input row count.

### Production smoke (~$0.50 NamSor + $0 gender_guesser + free Genderize)

Run the full pipeline on a 100K-paper sample of v3. Sanity
checks: gender coverage % matches Phase 0.1 Check 3
extrapolation (±5pp); per-region bias estimates have CI half-
widths in expected range (<15pp at N=100K-scaled sample);
NamSor call count and cost within free tier.

---

## IMPLEMENT plan

Steps in dependency order. Time estimates are wall-clock with
some hands-on engagement.

### Step 1 — Author records extraction (~2 hours)

`src/whitespace2/demographics.py::extract_authorships`:
- Stream v3 parquet (24.5M rows; use PyArrow batched iter)
- For each paper, explode `authorships` array
- Emit per-author-paper rows with: `paper_id`, `author_id`,
  `author_position`, `author_display_name`, `author_first_name`
  (extracted), `affiliation_country_code` (set), `is_corresponding`
- Output: `data/metadata/v3-authorships.parquet` (~75M rows
  expected, ~5-10 GB)

### Step 2 — Disambiguation validation (~1.5 hours)

`src/whitespace2/demographics.py::validate_disambiguation`:
- For each unique author.id: compute career length (max year -
  min year). Flag any >60 years as cross-era-merger candidates.
- For author.ids with ORCID: spot-check by ORCID agreement on
  a stratified sample (~3K author pairs across regions).
- Output: `data/metadata/v3-disambig-validation.json` with
  H1 + H2 measurements.

### Step 3 — Gender + country annotation (~3 hours)

`src/whitespace2/demographics.py::annotate_gender_country`:
- For each unique first name in v3-authorships: run
  gender_guesser, return label + confidence.
- For names with confidence <0.8: queue for Genderize (batched
  10/req, keyed-free 2500/mo). Record Genderize result.
- Compute per-name combined inference: confident if EITHER
  method assigns at p≥0.8; agree if both agree.
- Per-paper country: union of `affiliation_country_code` across
  authors (multi-country papers count in each).
- Output: `data/metadata/v3-author-demographics.parquet`
  (~5-10M unique author rows with gender, country, confidence
  scores)

### Step 4 — Low-confidence stratification + NamSor sampling (~2 hours)

`src/whitespace2/demographics.py::sample_for_namsor`:
- Identify low-confidence subset (neither gender_guesser nor
  Genderize confident at p≥0.8).
- Tag each name with script/region via heuristic (Unicode
  ranges for CJK / Cyrillic / Arabic / Devanagari; transliteration
  detection via fastText langid as a secondary signal).
- Stratified random sample of ~2,500 names across regions
  (seed: `ws2-phase-1.3-namsor-seed-v1`).
- Submit to NamSor API (keyed-free 2,500/mo); record per-name
  gender + confidence.
- Output: `data/metadata/v3-namsor-bias-sample.parquet`

### Step 5 — §9e-style bias correction (~3 hours)

`src/whitespace2/demographics.py::compute_bias_correction`:
- Per region: fit a bias model on gender_guesser outputs vs
  NamSor ground truth (logistic regression with region as
  feature; HOOK for §9e four-layer defense pattern).
- Compute per-region per-gender false-positive + refusal rates
  with CI.
- Apply correction to gender_guesser outputs across the full
  corpus → corrected per-cell gender distribution.
- Output: `data/metadata/v3-gender-bias-correction.parquet`
  (per-region correction table) + `v3-cell-gender-corrected.
  parquet` (per-cell year × field × region × corrected gender
  distribution with CIs)

### Step 6 — Coverage table + sensitivity analysis (~2 hours)

`src/whitespace2/demographics.py::build_coverage_table`:
- For each (year × field × region) cell: compute
  coverage rate, corrected gender distribution, country
  diversity, sample size, CI half-width.
- Sensitivity analysis: perturb bias-correction parameters
  within their CIs; report headline-divergence-statistic
  variance.
- Output: `data/metadata/v3-coverage-table.parquet` +
  `experiments/phase-1.3/coverage-report.md`

### Step 7 — Repeat for v2 corpus (~1 hour)

The v2/v3 robustness pair commitment requires demographic
annotations on both. Steps 1-6 re-run with v2 source. Same
bias-correction table applies (per-region biases don't depend
on §0 corpus version).

---

## VERIFY plan

For each hypothesis: explicit pass/fail measurement against the
pre-registered threshold. Produce `experiments/phase-1.3/
verify-results.md` mirroring Phase 1.2's verify-results.md
structure.

- **H1**: career-length screen output (count of cross-era-merger
  candidates / total unique author.ids).
- **H2**: ORCID agreement rate on the production-scale subset.
- **H3, H4**: per-cell coverage % with histograms across cells.
- **H5**: per-region NamSor bias CI half-widths.
- **H6**: actual NamSor spend (from API usage page).
- **H7**: per-cell NamSor sample size histogram + minimum.
- **H8**: per-cell corrected-gender-distribution CI half-widths
  with sensitivity bounds.

**Escape-hatch evaluation**: explicit check of E1-E4 triggers
with verdict (FIRED / NOT FIRED). If any FIRED, document the
escalation path taken before locking Phase 1.3 → 1.4.

---

## RETRO plan

`docs/phases/phase-1.3-retro.md` mirroring `phase-1.2-retro.md`
structure: summary, what happened, surprises, lessons (logged in
`tasks/lessons.md`), validation gates check, methodology
amendments, what carries to Phase 1.4, transition signoff.

---

## Validation gates (Phase 1.3 → 1.4 go/no-go)

| # | Gate | Acceptance | Status |
|---|---|---|---|
| 1 | All unit tests pass | 6 new tests + existing 32 §0 tests = 38 green | Pending |
| 2 | Lint + typecheck clean | ruff + mypy strict | Pending |
| 3 | Local end-to-end smoke passes | shape + count + bias-correction arithmetic | Pending |
| 4 | Production 100K smoke passes | coverage % matches Phase 0.1 ±5pp; NamSor cost ≤ $0.50 | Pending |
| 5 | H1: cross-era-merger rate ≤ 5% | per career-length screen | Pending |
| 6 | H2: ORCID agreement ≥ 95% | at production scale | Pending |
| 7 | H3: gender coverage ≥ 45% | on P_demo | Pending |
| 8 | H4: country coverage ≥ 50% | from affiliations | Pending |
| 9 | H5: NamSor bias CI half-width ≤ 10pp | per-region; otherwise E1 escape | Pending |
| 10 | H6: NamSor spend ≤ $10 | hard budget gate | Pending |
| 11 | H7: per-headline-cell NamSor sample ≥ 10 | otherwise E3 escape | Pending |
| 12 | H8: corrected-distribution CI half-width ≤ 2.5pp | on headline cells | Pending |
| 13 | Both v3 + v2 corpora annotated | parquets present + manifests | Pending |
| 14 | Reproducibility: manifests + seeds committed | all annotation outputs + bias-correction table | Pending |
| 15 | Retro committed | `phase-1.3-retro.md` | Pending |

ANY gate failure → STOP, surface to user, replan or invoke
escape hatch.

---

## Risks + mitigations

| # | Risk | Mitigation |
|---|---|---|
| R1 | NamSor pricing changed since plan; $10 buys fewer calls than expected | Verify NamSor current pricing page before Step 4. Budget gate H6 catches overspend regardless. |
| R2 | Per-region script detection misclassifies (e.g., transliterated CJK marked as Latin) | Use multiple signals (Unicode ranges + fastText langid + author affiliation country) with majority vote. Document misclassification rate in coverage report. |
| R3 | gender_guesser per-region bias is highly heteroscedastic (some regions need many more samples for tight CIs than others) | E1 escape: expand stratified sample for under-sampled regions; spend up to $10 budget on this if needed. |
| R4 | OpenAlex disambiguation has systematic errors for specific sub-populations (e.g., Chinese names → over-merging) | H1 + H2 catch this; ORCID validation is the primary diagnostic. If failing, flag in verify-results.md but Stage 2 plan handles the implication. |
| R5 | Genderize keyed-free 2500/mo exhausted | gender_guesser primary handles all names regardless; Genderize is cross-validation only. Loss = no cross-validation on names beyond 2500. Document in retro. |
| R6 | Long-tail rare names propagate as "unknown" gender in significant numbers | Sensitivity analysis: report headline divergence WITH and WITHOUT "unknown" inclusion. If both agree on direction, the result is robust to inference incompleteness. |
| R7 | Author records extraction OOMs on the 24.5M corpus | PyArrow batched iteration (50K rows/batch); same pattern as Phase 1.2's v3 filter. Should handle 24.5M rows in <10 GB peak. |

---

## Cost estimate (Phase 1.3)

| Item | Expected cost | Notes |
|---|---|---|
| gender_guesser (offline) | $0 | Deterministic, no API |
| Genderize keyed-free | $0 | Within 2,500/mo allocation |
| NamSor stratified bias sample | $0 | Within 2,500/mo free tier |
| NamSor escape-hatch reserve | ≤$10 | Hard gate (H6) |
| Modal CPU (extract authorships + annotate; ~30 min on 24.5M rows) | ~$2 | One pass per corpus (v3 + v2) → ~$4 total |
| Local compute (laptop) for bias correction + coverage table | $0 | small enough to run locally |
| **Total** | **~$4-14** | Well under §9 cap |

Running total after Phase 1.3: ~$37-47. Stage 2 spend ($150-300
headline + reserve) is the next big commitment, still within
§9 $500 cap.

**Pre-commit threshold (per ws2 desideratum §9):** If E2 escape
fires and direct-labeling Option A is invoked, estimated cost
$50-200 — pre-commit estimate must be added to `tasks/spend.md`
BEFORE the run.

---

## Phase 1.4 stub — Pre-Stage-2 quality gates + transition signoff

**Headline scope:** Sanity-check the production-scale corpus +
demographic annotations against field intuitions (analog of
Phase 0.1 Checks 1+2 at full scale). Sign off on Stage 1 →
Stage 2 transition.

**Open at start time:** Sanity-check sample size + cells;
go/no-go thresholds at production scale; whether the headline
divergence test can be smoke-tested on a 100K subset before
committing the full Stage 2 spend.

**Acceptance gate (1.4 → Stage 2):** All field-intuition sanity
checks pass; production data committed; Stage 2 plan authored
(and pre-registered hypotheses for the divergence test locked).

---

## Stage 1 → Stage 2 transition (update)

What Stage 1 must deliver to Stage 2:

1. **§0 analytical population P** — v3 primary, v2 robustness
   pair. Per `experiments/phase-1.2/h2-audit-results.md`.
   ✅ Complete.
2. **Sampled production sets** — 1M v3 + 1M v2 samples on Modal
   Volume + manifests. ✅ Complete (locally deleted post-retro
   to free disk; regeneratable via `modal volume get` or
   `build_v[23].py`).
3. **Held-out sets** — 4 cells × 2 corpora = 8 parquets;
   committed. ✅ Complete.
4. **Author + demographic annotations** — Phase 1.3 deliverable.
   v3 + v2 enriched parquets with author IDs, gender, country,
   confidence scores + bias-correction table + coverage report.
   🟡 In progress (this phase).
5. **Validated cost + preemption profile for Modal A100 preempt** —
   Phase 1.1 deliverable. ✅ Complete.
6. **Resumable runner + Modal embed functions** — Phase 1.1
   deliverable. ✅ Complete.
7. **Sanity-check sign-off on production data** — Phase 1.4
   deliverable. Pending.

---

## Companion documents

- Phase 1.2 retro: `docs/phases/phase-1.2-retro.md`
- §0 v3 audit results: `experiments/phase-1.2/h2-audit-results.md`
- §0 filter source: `src/whitespace2/section0_filter.py`
- ORCID-linkage validation (Phase 0.2 Wave 3A):
  `experiments/phase-0.2/orcid-linkage-validation.md`
- Demographic-inference lock (Phase 0.2 Check 3):
  `experiments/phase-0.1/demographic-coverage.md`
- ws2 desiderata §4 (demographic inference) + §9 (cost) + §9e
  (selection-bias correction framework):
  `docs/desiderata.md`

---

## Methodology amendment (vs Phase 0.2 commitment)

**NamSor scope locked as Option B (sample-based bias estimation,
not direct labeling).** Per the user-locked decision 2026-06-29.

Phase 0.2 Check 3's NamSor commitment was framed as "escalation
on the low-confidence subset" with $0-$500 budget. At Phase 1.3
plan time it became clear that direct labeling of every low-
confidence name (~60K-200K) would cost $50-200+ AND produce
point estimates with no quantified uncertainty. Option B uses
NamSor instead as a measurement tool for per-region bias of
gender_guesser, producing principled CIs that plug directly into
the §9e four-layer defense framework. Cost: ≤$10 (within free
tier + small paid reserve). Quality trade-off: explicit
uncertainty bounds replace direct labels; per ws2 desideratum
§4 + §9e, this is a strict methodology improvement.

**Escape hatch retained (§3).** If E1-E4 triggers fire,
escalation paths include expanded NamSor sampling (within $10),
Option A direct labeling (pre-commit estimate $50-200 required),
or fall-back to gender_guesser-only with "unknown" propagation
(zero-cost methodological conservatism).
