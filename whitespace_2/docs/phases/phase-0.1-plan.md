# Phase 0.1 — Scoping and Methodology Commitments

## Metadata

- **Branch:** `phase-0.1-scoping`
- **Stage:** 0 (Foundation)
- **Phase:** 0.1
- **Status:** planning → implementation
- **Prerequisite phases:** none (first phase)
- **Blocks:** everything downstream

## One-line scope

Lock in the data pull parameters, methodology commitments, and first-pass
sanity-check results that all downstream phases depend on.

## Why this phase exists

The compass (`../conceptual.md`) is a 10,000-ft view. Between it and any
actual analysis there are roughly thirty methodology decisions whose details
propagate through the entire 14-week study. Making them implicit or
ad-hoc means every downstream phase re-litigates them; making them explicit
and committed here means every downstream phase can treat them as settled.

Specifically, this phase exists to:

1. **Commit methodology.** Lock in the choices made during the Phase 0 exploration
   conversations: embedding model and drift ladder; demographic feature set
   and inference pipeline; subfield partition and classifier-drift mitigation;
   unit of analysis; missing-data policy.
2. **Characterize the data empirically.** Run small, cheap audits — concept-
   classifier drift, abstract availability, demographic inference coverage —
   on a pilot pull before committing to the full pull. The 14-week plan assumes
   certain data properties hold; we verify them first.
3. **Revise cost.** The compass's cost table predates several methodology
   decisions (notably NamSor for non-Western gender inference). Produce a
   revised budget with explicit per-item pre-commit estimates.
4. **Produce `field_definitions.csv`.** The single small, committed data
   artifact that every other phase references: the concept IDs, year range,
   and sampling scheme that define the corpus.

This phase is NOT:
- The pre-registration of the primary divergence test. That's Phase 0.2.
- Any full-scale data pull. That's Phase 1.1.
- Any actual analysis. That's Stage 2 onward.

## Design questions this phase answers

1. **Data pull parameters.** Which OpenAlex concept IDs define "Computer Science"
   and "Physics" for this study? What year range, sample size, and stratification
   scheme? Which OpenAlex snapshot date?
2. **Primary embedding + robustness partners.** SPECTER2 primary confirmed; which
   specific robustness partner(s) and in what order?
3. **Drift mitigation ladders.** The embedding-drift ladder (mitigations 2 + 4
   default, Flavors A → B progressive, C reserve) and the parallel subfield-
   classifier-drift ladder ((A) + (B) default, (C) robustness, (D/E) reserve)
   are committed.
4. **Demographic feature set.** Primary vs. secondary dimensions, inference
   vendors, missingness policy, non-Western name handling protocol.
5. **Subfield partition.** Hybrid arXiv-category-first / OpenAlex-concept-fallback,
   with post-1990 default restriction on subfield mechanism test.
6. **Unit of analysis.** Author-year for demographic diversity; paper-year for
   semantic diversity and canonical concentration.
7. **Revised budget.** What does the methodology-committed budget look like,
   and what pre-commit cost gates are required?

## Methodology commitments (locked in this phase)

### 1. Embeddings

- **Primary:** SPECTER2 (pinned version to be recorded in `tasks/spend.md` and
  `data/metadata/` when the pipeline runs; check latest version at that time).
- **Robustness partner 1 (commercial, required):** `text-embedding-3-large`
  via OpenAI API. Different architecture, different training data, different
  scale — genuine cross-family replication.
- **Robustness partner 2 (open-source, optional):** BGE-M3 or SciNCL. Free,
  local; included if Stage 2 has capacity.
- **For cross-field expansion (if pursued):** for philosophy or economics,
  `text-embedding-3-large` or BGE-M3 becomes co-primary alongside SPECTER2
  (not a robustness partner). See compass on field-specific embedding strength.

### 2. Embedding drift mitigation ladder

Per ws2 desiderata §2, §3.

**Stage 2 default (always run):**
- Mitigation 2 — cross-model replication using the robustness partner(s) above.
- Mitigation 4 — anchor-dimension projection. ~100 curated field-specific
  anchor concepts (stable across eras: "Fourier analysis," "Turing machines,"
  "graph theory," etc., for CS). Report anchor-space diversity alongside raw-
  space diversity as a column in every robustness table.

**Stage 3 progressive escalation (invoke if triggered):**
- Flavor A — diachronic Word2Vec + orthogonal Procrustes alignment
  (Hamilton-Leskovec-Jurafsky 2016 template).
- Flavor B — fine-tune SPECTER2 per era, align via anchor-paper Procrustes.
- Flavor C (dynamic embedding models) — **reserve only**; do not invoke unless
  (B) produces results contradicting domain intuition AND reviewers are still
  pushing.

**Escalation triggers:**
- Mitigation 4 shows direction-changing divergence from raw-space results → Flavor A.
- Flavor A is ambiguous or shows era-dependent inconsistencies → Flavor B.
- Any pre-1990-data-dependent headline claim requires at least Flavor A regardless.

### 3. Subfield classifier drift mitigation ladder

Per ws2 desiderata §10 (new in this phase).

**Stage 2 default (always run):**
- Mitigation A — subfield mechanism test restricted to post-1990 window.
  Field-level analyses (demographic, semantic, canonical) still span 1970–2024;
  only the within-field subfield mechanism test is year-bounded.
- Mitigation B — arXiv categories are the primary subfield partition where
  available (CS post-1993ish, Physics post-1991ish). OpenAlex concepts are the
  fallback for non-arXiv papers and older papers.

**Stage 3 progressive escalation (invoke if triggered):**
- Mitigation C — citation-network community detection as an alternative
  subfield partition (SciSciNet has precomputed communities, or compute
  fresh). Classifier-free, vocabulary-drift-proof, but community labels are
  data-defined not sociologically-named.

**Reserve (do not invoke unless necessary):**
- Mitigation D — per-era reclassification.
- Mitigation E — manual audit of a subsample.

**Escalation triggers:**
- Phase 0.1 sanity checks reveal pre-1990 concept tags are so sparse that
  Mitigation A alone is insufficient → invoke B aggressively + consider C.
- Stage 2 results differ substantively between arXiv-category and OpenAlex-
  concept partitions → invoke C as robustness check.

### 4. Demographic features

**Primary set (≥80% coverage required per year):**
1. **Gender** — inferred via Genderize.io primary + NamSor on low-confidence /
   non-Western subset. Country-conditional where affiliation is known. Reported
   with per-region accuracy (Anglo/East-Asian/South-Asian/Arabic-speaking/
   Slavic/other) from ORCID ground-truth validation.
2. **Country of current affiliation** (paper-time) — OpenAlex institution ROR → country.
3. **Country of earliest affiliation** (author-level) — proxy for training region.
4. **Institution type** — OpenAlex institution category: education, government,
   facility, company, healthcare, nonprofit, other.
5. **Institutional prestige tier** — time-invariant Shanghai ARWU (2003–2024
   averaged) binned top-10 / top-50 / top-200 / other-university; manual
   categorical scheme for non-universities (top industry labs, major
   govt labs, etc.); CS-specific CSRankings cross-check.
6. **Career stage** — continuous years-since-first-publication, binned 0-5 /
   6-15 / 16+ for diversity metrics.
7. **Training-institution concentration (Proxy A)** — institution at earliest
   publication cluster; used as categorical feature for lineage-concentration
   metrics (Gini, effective number of distinct institutions per subfield-year).

**Secondary set (report but don't rely on; may fall below 80% coverage):**
- Discipline of origin — first-paper concept tags as categorical.
- Coauthor network breadth — distinct collaborators / institutional diversity
  of coauthors.

**Explicitly excluded:**
- Race / ethnicity — not reliably inferable; would introduce bias specifically
  confounding cross-national analysis.
- Socioeconomic background — unavailable.
- Full advisor lineage (Proxy C) — out of scope; flagged in Discussion as
  natural follow-up paper.

**Stage 3 addition:**
- **Proxy B — coauthor-based advisor inference at scale, validated on
  Math Genealogy + ORCID ground-truth subsample** (2–5K authors). Reported
  with accuracy metrics and systematic-bias characterization. Enables advisor-
  lineage concentration metrics as a deeper mechanism check.

### 5. Subfield partition

- **Primary:** hybrid — arXiv category where paper is on arXiv; OpenAlex
  concept (dominant / highest-confidence tag) as fallback.
- **Granularity:** target ~10–50 subfields per field. Specific OpenAlex concept
  level chosen to hit this range; specific arXiv category granularity
  (`cs.AI` vs. `cs.AI.ML`) chosen for consistency.
- **Multi-label handling:** each paper gets one primary subfield assignment
  (highest-confidence concept tag, or primary arXiv category). Multi-subfield
  robustness check in Stage 3.

### 6. Unit of analysis

- **Demographic diversity** → author-year. Each unique author active in year
  Y counts once; "active" = ≥1 paper in Y. Unweighted primary; productivity-
  weighted secondary.
- **Semantic diversity** → paper-year. One embedding per paper.
- **Canonical concentration** → paper-year. Citation-based (Gini, Spearman top-N, top-k share).
- **Within-paper team-diversity × novelty analysis** → paper cross-section.
  Each paper is one observation. Team demographic diversity (Rao's Q over
  the author team) regressed on paper-level semantic novelty (distance to
  citation-context centroid) with year + subfield fixed effects. This is a
  distinct analytic level from the three aggregate time-series analyses
  above, addressing the within-paper version of the central claim: do
  demographically diverse teams produce semantically novel papers, or do
  shared actuators average diverse inputs toward canonical outputs? See
  pre-registration detail in "Open decisions deferred."

  **Why this level matters:** the aggregate time-series tests (Tests I–III
  above) detect divergence at the field level; they cannot distinguish
  field-wide shared-canon effects from within-team averaging-toward-canon
  dynamics. This cross-sectional analysis addresses the intra-paper
  influence question directly, at the measurable level, complementing the
  field-level tests without duplicating them.

### 7. Missing-data policy

- **Pairwise deletion.** Each author is included in diversity calculations for
  each dimension they have, excluded for dimensions they don't.
- **Coverage threshold:** ≥80% coverage per dimension per year required for a
  dimension to count as "primary." Dimensions dropping below 80% in any year
  are demoted to "secondary" (reported but not headline).
- **"Unknown" as a category** only where the missingness itself is meaningful
  (e.g., "unaffiliated" authors are a real category; "prestige-unknown" is not).
- **Per-sub-analysis sample universe reported explicitly** — every diversity
  time-series plot includes n per year.

### 8. Multi-affiliation handling

- **Primary rule:** first-listed affiliation per author per paper. Simple,
  matches convention.
- **Robustness:** all affiliations with fractional weighting. Reported only if
  primary result is sensitive to the rule.
- **Descriptive panel:** fraction of papers with ≥2 affiliations per author,
  per year. Itself may be a meaningful trend (internationalization of research).

### 9. Non-Western name handling protocol

- **Region-of-origin classification:** NamSor's name-region classifier. Each
  author tagged with probable name region: Anglo, East Asian, South Asian,
  Arabic-speaking, Slavic, Latin, other/unknown.
- **ORCID ground-truth validation:** 5–10K-author subsample where ORCID
  gender is self-reported; compute per-region gender-inference accuracy.
- **Stratified sensitivity analyses:** all demographic diversity time series
  reported both (a) on full population and (b) on Anglo-name subset. If
  headline trend holds on (b), finding is robust to inference bias.

### 10. Disambiguation error floor

- **Acknowledgment:** OpenAlex author-disambiguation accuracy ≈ 90–95% per
  their published benchmarks. With ~200K authors in our sample, that's
  thousands of errors propagating into career stage, training institution,
  and coauthor-network features.
- **Mitigation:** flag implausible career lengths (>60 years since first
  publication); spot-check. Report OpenAlex's reported accuracy in Methods.
  Use author-level aggregates (diversity metrics over aggregated authors
  are more robust than edge-level analyses).

### 11. Cluster-fit temporal stratification (non-negotiable)

Per ws2 desiderata §11.

**The risk being mitigated.** Cluster entropy (primary semantic-diversity
metric A, per Phase 0.2 pre-registration) depends on a fitted clustering of
embeddings. If clusters are fit on the full 1970–2024 corpus without
stratification, modern papers — 10×–50× more numerous than early-decade
papers — dominate the cluster definitions. The resulting clusters reflect
modern semantic structure. 1970s papers then map poorly to those
modern-defined clusters, concentrate artificially in a few least-wrong
clusters, and produce spurious low-diversity in early years. The divergence
finding becomes a corpus-composition artifact.

This is the single largest "quiet failure" risk among the primary metrics
and is treated as a first-class methodological commitment, not a
pre-registration footnote.

**Commitment:**
- **Cluster-fit sample:** temporally-stratified pooled subsample with
  **equal papers per decade** (1970s, 1980s, 1990s, 2000s, 2010s, 2020–24).
  Subsample size per decade set at min across decades of Nₐ; actual count
  committed once pilot data lands.
- **Cluster count K:** 50 primary; K ∈ {30, 50, 100} as robustness.
- **Cluster assignment for production:** every paper in the full corpus
  (all years) is assigned to its nearest cluster centroid from the
  stratified fit. Assignment step uses the full corpus; fit step uses the
  stratified subsample. This distinction is load-bearing.
- **Same principle applies** to any other pooled-data fit consumed by a
  diversity metric (e.g., PCA basis if we ever compute PCA on pooled data
  rather than per year). Default for effective dimensionality is per-year
  fit on per-year-centered embeddings, so the principle applies to cluster
  entropy specifically today but extends to any future pooled-fit step.
- **Artifacts to commit:** the stratified subsample indices, the fitted
  cluster centroids, the K value, and a `cluster-fit-manifest.md` in
  `data/metadata/` that records all of the above and is referenced by
  every downstream metric computation.
- **Validation:** a sanity check on pilot data comparing cluster-assignment
  distributions at both ends (1975 vs. 2020) under (a) stratified cluster
  fit and (b) unstratified cluster fit, quantifying the artifact the
  stratification prevents. Included as an extension of sanity Check 5b.

**If this is violated, the finding is invalid.** Acknowledged in Methods
explicitly; verified in any independent reproduction.

## Sanity checks (this phase's empirical work)

Deliverables in rough order:

### Check 1 — Abstract availability by year

- **What:** fraction of papers in the pilot pull with a non-empty abstract,
  by year.
- **Why:** abstract availability is the upstream bottleneck for both concept
  classification and semantic embedding. Worst-case years get a bounded
  mitigation strategy.
- **Output:** plot + summary table in `experiments/phase-0.1/abstract-coverage.{png,md}`.
- **Expected:** high (>95%) from ~1990 onward; drops sharply before ~1985.

### Check 2 — Concept classifier drift audit

Per ws2 desiderata §10. Five sub-checks:

- **2a — Concept coverage by year:** fraction of papers with ≥1 concept tag.
  Red flag: monotonically increasing from low base (indicates systematic
  under-tagging of old papers).
- **2b — Concepts per paper by year:** mean and median, controlling for
  abstract length. Red flag: systematic trend.
- **2c — Confidence score distribution by year:** mean tag confidence. Red
  flag: systematically lower on older papers.
- **2d — Anachronism audit:** 20 concepts with names denoting recent concepts
  ("deep learning," "transformer," "CRISPR," "GPT", etc.). Earliest paper
  tagged with each. Red flag: pre-dates the concept by >5 years.
- **2e — Hand-auditable subfield at both ends:** pick 2 subfields that
  clearly existed in 1975 (e.g., "operating systems," "compiler design").
  Manually inspect top 50 papers tagged with those concepts in 1975 and
  2020. Qualitative assessment of classifier reliability across eras.
- **Output:** `experiments/phase-0.1/classifier-drift-audit.md` with plots,
  anachronism table, and hand-audit notes.
- **Decision:** depending on severity, confirms or tightens the post-1990
  default in Mitigation A.

### Check 3 — Demographic inference coverage

- **3a — Gender coverage via Genderize.io on pilot:** fraction of authors
  receiving a gender assignment above a confidence threshold (e.g., p>0.8),
  stratified by year and by NamSor-inferred name region.
- **3b — Country-of-affiliation coverage:** fraction of papers with ROR-
  resolvable country, by year.
- **3c — ORCID self-report coverage:** fraction of authors with an ORCID
  record, by year. Used as ground-truth sample size estimator.
- **Output:** `experiments/phase-0.1/demographic-coverage.md`.
- **Decision:** confirms (or flags a revision to) the 80% coverage threshold
  per dimension. If gender drops below 80% in any year under Genderize-only,
  commit to NamSor on the low-confidence subset. Revise budget accordingly.

### Check 4 — OpenAlex disambiguation spot-check

- **What:** identify authors in the pilot with implausible publication
  histories (e.g., first-publication year >1970 AND latest-publication year
  >2020, implying 50+ year career). Manually inspect a sample.
- **Why:** characterize the upper-bound disambiguation error rate on our
  corpus specifically.
- **Output:** one-paragraph summary in `experiments/phase-0.1/disambiguation-check.md`.

### Check 5 — Pilot query + metric convergence analysis

Two coupled goals, run together on the pilot data:

**5a — Pilot pull:**
- **What:** execute the committed OpenAlex pull specification on a stratified
  pilot sample (~1000 CS papers: 200 each from 1975, 1990, 2005, 2015, 2024).
  Record Nᵧ (papers per year) across the full 1970–2024 range from a lighter
  metadata-only pull as an additional deliverable.
- **Why:** validate that the pull parameters produce an expected-shape
  dataset before the full 500K-paper pull. Catches pull-specification errors
  cheaply. Nᵧ distribution determines the binding constraint on per-year
  bootstrap sample size.
- **Output:** `data/metadata/pilot-query-results.parquet` + descriptive
  summary in `experiments/phase-0.1/pilot-summary.md` including Nᵧ
  distribution and the projected smallest-year sample size.

**5b — Metric convergence analysis:**
- **What:** on a single high-N recent year from the pilot (e.g., 2015 CS or
  2024 CS, whichever gives ≥10K papers after sampling), run convergence
  analysis for the sample-size-sensitive semantic-diversity metrics
  (effective dimensionality; cluster entropy once clusters are fit) at
  subsample sizes n ∈ {200, 500, 1000, 2000, 5000, 10000}. For each n, take
  20 independent subsamples, compute each metric, record mean and spread.
  Plot metric-vs-n; identify the smallest n at which the estimator is stable
  (metric point estimate changes by <5% across three consecutive n values
  AND inter-subsample spread is acceptable).
- **Why:** determine empirically the minimum bootstrap sample size per
  metric rather than relying on rules of thumb. The compass and earlier
  methodology drafts used heuristic values (n=2000 for semantic, n=10K
  ceiling for demographic); these should be empirically grounded before
  Phase 0.2 pre-registration. Effective dimensionality specifically depends
  on sample-to-embedding-dimension ratio (d=768 for SPECTER2) and needs
  pilot-data calibration.
- **Note on demographic metrics:** convergence analysis less critical here
  because Shannon entropy on categorical features is well-understood and
  Miller-Madow bias correction is standard. A light check on a high-N year
  (entropy at n ∈ {500, 2000, 10000}) is sufficient.
- **Cluster-fit stratification artifact check** (per §11 commitment):
  fit clusters twice on the pilot pool — once on a temporally-stratified
  subsample (equal papers per decade) and once on the unstratified full
  pool. Assign a held-out 1975 sample and a held-out 2020 sample to
  clusters from each fit. Compare cluster-assignment distributions. The
  unstratified fit is expected to concentrate 1975 papers in fewer clusters
  (artificial low diversity); the stratified fit should show more even
  spread. Quantifying this artifact size on pilot data validates that §11
  is doing real work and provides a Methods-section citation for the
  magnitude of the effect being prevented.
- **Output:** `experiments/phase-0.1/metric-convergence.{png,md}` — plots,
  per-metric N_target recommendations with rationale, any surprises.
  `experiments/phase-0.1/cluster-stratification-check.{png,md}` — the
  artifact-size quantification.

**Decisions from Check 5:**
- Go/no-go on committing to the full pull in Phase 1.1.
- Per-metric N_target values fed into Phase 0.2 pre-registration.
- Per-year bootstrap n = min(Nᵧ, N_target) committed as a pre-registered
  constant per metric.

## Deliverables (committed at end of phase)

1. **`data/metadata/field_definitions.csv`** — concept IDs (CS, Physics) with
   parent-concept paths, year range, OpenAlex snapshot date, sample size
   target, stratification scheme.
2. **`docs/phases/phase-0.1-plan.md`** (this document) — methodology
   commitments locked.
3. **`docs/phases/phase-0.1-retro.md`** — post-phase retrospective (what
   held up, what didn't, what to adjust before Phase 0.2).
4. **Sanity check outputs** under `experiments/phase-0.1/`:
   - `abstract-coverage.{png,md}`
   - `classifier-drift-audit.md`
   - `demographic-coverage.md`
   - `disambiguation-check.md`
   - `pilot-summary.md`
   - `metric-convergence.{png,md}`
   - `cluster-stratification-check.{png,md}`
5. **`data/metadata/pilot-query-results.parquet`** — 1000-paper pilot pull.
6. **Updated `docs/desiderata.md`** — §10 amendment committed (already done
   in this phase, 2026-04-23).
7. **Revised cost estimate in `tasks/spend.md`** with pre-commit entries for
   Genderize + NamSor gender inference and commercial embedding robustness.

## Validation gates (go/no-go for Stage 1)

Each gate must be met before advancing to Phase 1.1 (full data pull):

1. **Pilot query returns a non-empty, expected-shape dataset.** Year
   distribution matches target; concept filter works as expected; no
   silent API-pagination errors.
2. **Abstract coverage is workable.** ≥90% of papers post-1985 have abstracts.
   Pre-1985 coverage is characterized and a bounded mitigation committed (e.g.,
   "treat pre-1985 semantic-diversity measurements as preliminary pending
   title-only vs. title+abstract sensitivity").
3. **Classifier drift is characterized.** Coverage by year, concepts per paper,
   confidence distribution, and anachronism audit all reported. Default post-
   1990 Mitigation A is confirmed or explicitly loosened.
4. **Demographic inference coverage is characterized.** Gender coverage by
   name region reported. Decision made on Genderize-only vs. Genderize +
   NamSor, with cost implications committed to `tasks/spend.md`.
5. **Disambiguation error rate is spot-checked.** Upper-bound estimate
   documented.
6. **`field_definitions.csv` is committed.** Review-worthy and pinned.
7. **Retro written** — what surprised us, what to adjust before Phase 0.2.

Gate failures are not blockers in themselves — they are triggers for phase
re-planning. "Abstract coverage pre-1985 is 40%" ≠ "stop the project"; it =
"revise the pre-1985 analysis scope and re-commit."

## Revised cost estimate

The compass's cost table (conceptual.md lines 183–192) predates several
methodology decisions. Updated estimate based on Phase 0 conversations:

| Item | Compass | Revised low | Revised high | Notes |
|---|---|---|---|---|
| Embedding API (primary) | $50–$300 | $0 | $0 | SPECTER2 local — free |
| Embedding API (robustness, text-embedding-3-large) | (bundled above) | $50 | $150 | ~$0.13 per 1M tokens; 500K abstracts ≈ $50–150 |
| Gender inference — Genderize.io | $0–$100 | $30 | $100 | 500K authors ≈ 1 call each; bulk pricing |
| Gender inference — NamSor (low-confidence subset) | not in compass | $0 | $500 | Only if Genderize coverage drops below 80% on non-Western subset; 100–200K names |
| Compute (local GPU) | $0–$50 | $0 | $50 | Assumed free Apple M-series |
| Math Genealogy / ORCID API (Stage 3 Proxy B) | not in compass | $0 | $0 | Free |
| **Total** | **$50–$500** | **$80** | **$800** |

**Upper-bound pressure points:**
- NamSor is the largest new cost. Contingent on Genderize coverage results
  from sanity Check 3. If Genderize alone clears 80% threshold per year,
  NamSor spend is minimal.
- Commercial embedding replication is the second largest. Contingent on
  whether open-source alternatives (BGE-M3, SciNCL) satisfy desiderata §2.

**Per ws2 desiderata §9** (cost gate applies to embedding runs ≥$50): the
commercial embedding robustness run requires a pre-commit entry in
`tasks/spend.md` before Stage 2 executes. The same pre-commit discipline is
extended to NamSor gender inference by convention (not strictly covered by
desiderata §9, but same principle).

## Open decisions deferred to later phases

- **Pre-registration of the primary divergence test.** Metric choice,
  estimator, field, time window, null hypothesis, threshold. Phase 0.2.
  Metric choices are pre-drafted in Phase 0 conversation and will be
  formally locked in Phase 0.2 pre-registration:
  - **Demographic (per-feature):** Shannon entropy primary; Gini-Simpson
    secondary. Miller-Madow bias correction on both.
  - **Demographic (composite):** Rao's quadratic entropy with uniform
    Hamming distance between joint states as primary composite; joint
    Shannon entropy as secondary; weight-sensitivity on Q (one dimension
    doubled at a time) as robustness.
  - **Demographic (decomposition, Figure 4):** additive Shannon entropy
    decomposition across dimensions, with mutual-information terms
    reported.
  - **Semantic (primary A):** cluster entropy — Shannon over K=50
    cluster-assignment probabilities, where clusters are fit on a
    temporally-stratified pooled subsample (equal papers per decade) to
    avoid modern-era cluster-definition bias. Reported alongside K ∈
    {30, 50, 100} robustness. Directly parallel to demographic Shannon
    entropy; enables direct visual comparison in the main 3-panel figure.
  - **Semantic (primary B):** effective dimensionality — PCA participation
    ratio (Σλᵢ)²/Σλᵢ² on year-centered embeddings.
  - **Semantic (secondary):** mean pairwise cosine distance, bootstrap-
    subsampled.
  - **Semantic (robustness column):** all three of the above recomputed in
    the anchor-projected space (embedding-drift Mitigation 4).
  - **Canonical (primary):** Chu-Evans Spearman rank correlation on top-50
    most-cited papers, lag Δ=5 years. Citation framing (A): citations
    received *in* year Y, regardless of cited paper's publication year.
  - **Canonical (secondary):** citation Gini over the per-year citation
    distribution.
  - **Canonical (robustness):** top-1% share; Spearman at N ∈ {100, 500}
    and Δ ∈ {3, 10}.
  - **Canonical (explicitly NOT included):** Park-Leahey-Funk CD-index as
    primary or secondary. Contested per Petersen-Holst-Macher; reserved
    for engagement-with-literature framing in the Discussion only.
  - **Bootstrap sample size per metric:** empirically determined from
    sanity Check 5b (metric convergence analysis); per-year n =
    min(Nᵧ, N_target). Not fixed in this phase.
  - **Uncertainty reporting:** every metric on every figure reported with
    95% bootstrap confidence interval (200 replicates). Not optional.
  - **Primary divergence test set (three co-primary tests, each answering a
    distinct substantive question — not redundant):**
    - **Test I — Standardized-gap trend (contemporaneous divergence).**
      Z-score DemDiv and SemDiv independently over 1970–2024; compute
      Gap_Y = z_Dem_Y − z_Sem_Y; regress Gap_Y on Y with Newey-West
      standard errors for autocorrelation. One-sided test (H₁: slope > 0).
      Mann-Kendall nonparametric trend test as robustness.
    - **Test II — Confound-controlled gap regression (reformulated from
      an earlier SemDiv-on-DemDiv specification).** To avoid the
      "who-controls-whom" ambiguity of regressing semantic on demographic
      while also including time, test the gap directly:
      Gap_Y = β₀ + Σ βₖ·Controlₖ + β_t·Y + ε_Y,
      where Gap_Y = z(DemDiv_Y) − z(SemDiv_Y). One-sided test (H₁: β_t > 0
      — gap grows over time after controls absorb confounds). Newey-West
      HAC standard errors for autocorrelation. Controls operationalized in
      the dedicated subsection below.
    - **Test III — De-trended cross-correlation + Granger causality
      (propagation structure).** First-difference both series; compute
      cross-correlation at pre-registered lags k ∈ {0, 3, 5, 10, 15};
      plot cross-correlogram with bootstrap CI. Formal test: Granger
      causality — regress SemDiv_Y on its own lags AND on lagged DemDiv;
      F-test whether DemDiv lags are jointly significant. Lag order for
      Granger chosen by AIC on a pre-pilot subsample, capped at 5.
      HP-filter residuals as de-trending robustness check.
  - **Four-quadrant interpretation** (Test I × Test III):
    - Test I significant, Test III no lagged correlation → true divergence.
    - Test I significant, Test III peak at lag k > 0 → delayed tracking.
    - Test I not significant, Test III peak at lag 0 → contemporaneous tracking.
    - Test I not significant, Test III peak at lag k > 0 → lagged tracking.
    All four are publishable; each tells a different story about mechanism.
  - **Multiple-comparisons correction (hierarchical + directional agreement):**
    - 3 test types × 6 metric pairings (3 semantic × 2 demographic composites)
      × 2 fields (CS, Physics) = 36 primary tests total.
    - **Correction scheme:** Bonferroni within each test-type across 6
      metric pairings (α = 0.05/6 ≈ 0.0083 per pairing); no correction
      across test-types since they ask distinct questions.
    - **"Replicated divergence" requires:** all 3 test types agree on
      direction (sign) in ≥4 of 6 metric pairings within each field,
      independently. Pre-registered before Stage 2 runs.
    - Secondary tests (per-dimension decomposition, 7 dims × 3 semantic
      × 2 fields = 42 tests) reported with FDR control at q=0.1, labeled
      exploratory.
  - **Effect-size threshold for headline claim:** Test I slope ≥ 0.02 SD/year
    (a 1-SD gap change over 50 years). Smaller magnitudes reported honestly
    as "suggestive, below pre-registered threshold."
  - **Power acknowledgment:** 55 annual observations; minimum detectable
    Test I slope at 80% power is ~0.02 SD/year. Effects substantially
    smaller will not be detectable — pre-register the expectation.
  - **Subfield mechanism test (the single most important analysis, per
    compass).** Unit of analysis = subfield. For each subfield s in the
    post-1990 window (per desiderata §10): CanonConc_s = mean
    Chu-Evans Spearman over subfield time series; DivMag_s = slope of
    standardized gap within subfield. Regress DivMag_s on CanonConc_s
    with subfield-level controls (log papers, avg team size, subfield
    age), cluster-robust standard errors. H₁: γ₁ > 0 (canonical-
    concentrated subfields show more divergence). Separate correction
    regime from the field-level tests — single test, α=0.05.
  - **Control variables (operationalization for Test II and Test IV):**
    - **log(N papers in year Y) — field size.** Count from OpenAlex
      as-indexed in our snapshot, log-transformed. Captures field expansion
      and absorbs sample-size-dependent measurement bias. **Caveat:**
      conflates true field growth with OpenAlex back-indexing improvements;
      document the snapshot date and note in Methods.
    - **Avg team size per paper (trimmed).** Trimmed mean of authors per
      paper, excluding top 1% to remove mega-author outliers (HEP ATLAS
      papers, large genomics consortia). Median as robustness. Wu-Wang-
      Evans 2019 documented team-size growth; team size is a confound
      for both demographic (more authors → more dimensions represented)
      and semantic (larger teams may produce more integrative work).
    - **Median references per paper.** Median (not mean) reference count,
      robust to review-paper outliers. **Caveat:** OpenAlex reference
      coverage is incomplete pre-1990; report per-year reference-extraction
      completeness as a diagnostic. Control is weak for pre-1990 data.
    - **arXiv fraction.** Fraction of year-Y papers with an arXiv ID.
      Near-zero pre-1991 and for CS through mid-90s; most regression
      contribution is from the late period. Different dynamics in CS vs.
      Physics. Robustness: Test II with and without this control.
    - **log(distinct active authors in year Y).** Separates researcher-
      population growth from publication growth. If papers-per-author
      rises while author pool stays flat, that's a different phenomenon
      from both rising proportionally.
    - **Field-entry rate.** Fraction of year-Y authors publishing for the
      first time. Large entry cohorts are both a demographic event (new
      demographics enter) and a semantic one (newcomers produce different
      work on average).
    - **Subfield composition vector.** Fraction of year-Y papers in each
      major subfield (~10–50 subfields per field). **Important confound:**
      shifts in subfield mix mechanically shift aggregate semantic
      diversity even without within-subfield changes. Controlling for
      composition separates "CS diversified" from "CS's subfield mix
      reshuffled."
    - **Standardization:** all controls z-scored (mean 0, SD 1 over
      1970–2024) before entering the regression, for coefficient
      comparability.
    - **Multicollinearity:** expected to be substantial; all controls are
      upward-trending over 50 years. Report VIF per variable. Mandatory
      sensitivity analysis: Test II fit under (i) all controls, (ii) each
      control dropped in turn, (iii) subfield composition included vs.
      not. Report β_t across specifications; qualitative stability is the
      robustness claim.
    - **Not included as controls** (deliberately): demographic diversity
      itself (it's the independent variable of interest in Test II's
      predecessor formulation; in the Gap_Y reformulation, it enters the
      gap definition itself); semantic diversity (same reason); canonical
      concentration (it's a potential mechanism, not a confound).
  - **Break-point analysis (secondary, conditional on Test I or Test II
    being significant).** When does divergence start? Substantive story
    changes materially depending on whether the gap widens continuously
    from 1970 or breaks at a specific inflection.
    - **Primary method — Bai-Perron multiple-breakpoint test on Gap_Y.**
      Data-driven search for 0 to m breakpoints; number of breaks selected
      by BIC. HAC (Newey-West) standard errors. **Trimming:** 15% from
      each series end — breaks cannot be detected before ~1978 or after
      ~2017 (artifact of the statistical method, not a substantive choice).
    - **Secondary method — Chow test at pre-registered candidate years.**
      For each candidate, fit pre- and post-break regressions; F-test
      whether allowing the break improves fit materially. Higher power
      than data-driven search when the hypothesis is specific.
    - **Pre-registered candidate break years per field:**
      - **CS:** 1991–93 (arXiv launch + public web); 1998–2000 (dot-com
        peak; demographic broadening from industry demand); 2008–09
        (financial crisis, academic-market consolidation); 2012 (AlexNet
        / deep learning takeoff); 2018–20 (foundation models; likely too
        recent to show in smoothed series).
      - **Physics:** 1991 (arXiv launched in hep-th); 1995–2000
        (post-SSC-cancellation; string theory dominance); 2012 (Higgs
        boson discovery).
    - **Concordance requirement for "significant break":** both
      Bai-Perron detects the break AND Chow at a nearby pre-specified
      candidate (within ±2 years) rejects the no-break null. Prevents
      reporting one-method-only breaks as substantive.
    - **Minimum detectable effect (pre-registered expectation):** slope
      change ≥ 0.1 SD/year at 80% power with 55 annual observations.
      Smaller break magnitudes reported but flagged as
      "below-detection-threshold."
    - **Multiple-comparisons:** Bonferroni within candidate set (5 for CS,
      3 for Physics), consistent with the hierarchical-correction scheme
      used for Tests I–III.
    - **Output:** figure of Gap_Y with detected breakpoints (95% CIs),
      pre-specified candidates annotated, piecewise-linear fit showing
      pre/post slopes per break; table reporting break location, pre-slope,
      post-slope, Δslope, p-value, and concordant-candidate-event
      interpretation.
  - **Test IV — Within-paper team-diversity × novelty (cross-sectional
    companion to the aggregate divergence tests).** Addresses the
    within-paper version of the central claim: "do demographically diverse
    teams produce semantically novel papers?" Complements Tests I–III by
    operating at a different level of aggregation (paper cross-section vs.
    aggregate time series) and using fundamentally different statistical
    methodology.
    - **Paper-level team demographic diversity (T_p):** Rao's Q over the
      author team of paper p, with the same uniform Hamming distance
      metric as the field-level composite. Single-author papers: T_p = 0
      by construction, included as baseline (the single-author-vs.-team
      gradient is itself informative).
    - **Paper-level semantic novelty (N_p) — primary:** cosine distance
      from paper p's embedding to the centroid of embeddings of papers in
      its reference list. High N_p = paper synthesizes distant concepts;
      low N_p = paper is close to its cited context. Papers with fewer
      than 5 citations (insufficient for a stable centroid) flagged and
      analyzed in a robustness-only subset.
    - **Paper-level semantic novelty (N_p) — secondary:** cosine distance
      from paper p to the year-Y canonical centroid (centroid of the
      top-100 most-cited papers in year Y). Different notion of novelty —
      distance-from-canon rather than distance-from-own-inputs. Reported
      alongside primary as robustness.
    - **Paper-level semantic novelty (N_p) — tertiary (Stage 3 if capacity):**
      Uzzi-Mukherjee-Stringer recombinant novelty on reference-pair
      atypicality. Well-established method (Science 2013); requires
      separate pipeline (co-citation null model). Only if Stage 3 has
      bandwidth.
    - **Regression specification:** N_p = γ₀ + γ₁·T_p + Σ γₖ·Controlₖ +
      year-FE + subfield-FE + ε_p.
      - **Controls:** number of authors, number of references, mean author
        career stage, mean author institutional prestige tier, log paper
        age (for robustness on older papers), field dummy (CS vs. Physics
        in pooled model).
      - **Standard errors:** double-clustered by lead author and by
        subfield (papers with same lead author or same subfield are not
        independent).
    - **Hypotheses (pre-registered, two-sided):**
      - H₀: γ₁ = 0 (team diversity uncorrelated with novelty).
      - H₁ (actuator-dominant): γ₁ < 0 — diverse teams produce LESS novel
        work; shared actuators average diverse inputs toward canonical
        outputs. This is the strongest within-paper form of the paper's
        central claim.
      - H₁' (diversity-productive): γ₁ > 0 — diverse teams produce MORE
        novel work; demographic diversity translates to output diversity
        at the team level. Consistent with Hofstra et al. 2020 (though
        they found more nuanced differential-reward patterns).
      - H₁" (null effect): γ₁ ≈ 0 — team composition is orthogonal to
        output novelty. Partially undermines both stories; mechanism is
        elsewhere.
    - **Effect-size threshold (substantive significance):** |γ₁| ≥ 0.05
      after standardization of T_p and N_p. Smaller magnitudes reported
      but flagged as "detectable but below substantive-significance
      threshold" — with hundreds of thousands of papers, statistical
      significance is nearly automatic; substantive significance is the
      binding criterion.
    - **Time interaction (secondary within Test IV):** fit γ₁(Y) =
      γ₁₀ + γ₁₁·Y — does the team-diversity × novelty relationship evolve
      over time? Strengthening negative γ₁ over time would be consistent
      with growing actuator dominance.
    - **Positioning vs. prior work:** Hofstra et al. 2020 (PNAS) did a
      related analysis; their finding was that underrepresented groups
      produce more novel work but receive differential reward. Our Test IV
      is structurally similar (team composition → novelty) but focuses on
      the aggregate team-diversity→novelty relationship over 50 years,
      and pairs it with the field-level tests to ask whether any
      within-paper effect shows up at aggregate scale.
    - **Causal interpretation caveat (pre-baked):** cross-sectional
      correlations ≠ causal effects of team composition on novelty.
      Direction could reverse (novel work attracts diverse teams; self-
      selection on risk preference, etc.). Reported as descriptive
      association, not causal effect. No instrumental variable strategy
      attempted in this paper.
- **Specific anchor concepts for Mitigation 4.** List of ~100 concepts with
  representative reference texts, per-field. Phase 0.2 or early Stage 1.
- **Specific alternative embedding model for Mitigation 2.** Choice between
  `text-embedding-3-large` (commercial) and BGE-M3 (open). Decision deferred
  to Stage 2 based on Stage 1 results and budget at that point.
- **Decision on third field** (sociology / philosophy / economics vs. none).
  Deferred; compass lists pros/cons. Decide in Stage 2 based on CS + Physics
  results.
- **Advisor lineage Proxy B detailed protocol.** Coauthor-heuristic specifics,
  Math Genealogy + ORCID matching pipeline, accuracy validation scheme.
  Stage 3 phase plan.

## Timeline

Phase 0.1 target: **2 weeks, ~30 hours of effort.**

- **Week 1:** methodology commitment (this document — in progress);
  OpenAlex API setup + pilot query; field_definitions.csv draft.
- **Week 2:** sanity checks (abstract coverage, classifier drift audit,
  demographic coverage, disambiguation spot-check); pilot-query review;
  budget revision; retro.

Advancement to Phase 0.2 (pre-registration) assumes Phase 0.1 closes cleanly.
Advancement to Phase 1.1 (full data pull) assumes Phase 0.2 and Phase 0.1
both close.

## References

- North star: `../conceptual.md`
- Principles: `../desiderata.md` (amended §10 and §11 in this phase)
- Program context: `../../../docs/program/`
- Todo: `../../tasks/todo.md`
- Spend: `../../tasks/spend.md`
- Lessons: `../../tasks/lessons.md`
