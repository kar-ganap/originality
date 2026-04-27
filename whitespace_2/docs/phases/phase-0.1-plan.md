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

Three-model stack, with deliberate within-family and cross-family
robustness partners (per Phase 0 embedding-landscape research;
SPECTER3 does not exist, SciRepEval leaderboard is essentially static,
and the scientific-domain embedding space has stalled — so "robustness"
is load-bearing here).

- **Primary:** SPECTER2 (`allenai/specter2_base` + proximity adapter
  `allenai/specter2`). Pin to the Dec 4 2024 commit for reproducibility
  (avoid `aug2023refresh` — AI2 says use non-refresh for benchmarking).
- **Within-family robustness partner:** SciNCL (`malteos/scincl`).
  Same SciBERT backbone, different training objective (neighborhood
  contrastive on citation graph vs. triplet loss). Tests whether the
  result is driven by SPECTER2's specific training objective.
- **Cross-family robustness partner:** Qwen3-Embedding-0.6B at 768-dim
  via Matryoshka representation learning. Frontier-family model
  (decoder-LM, SentencePiece tokenizer, 32K context — no abstract
  truncation), Apache 2.0. Tests whether the SciBERT-era tokenization
  is driving the result. Critically important for diachronic robustness
  since SPECTER2 and SciNCL share the same 2019-era tokenizer.
- **Explicitly skipped:** NV-Embed-v2 (CC-BY-NC license), Qwen3-8B
  (10× compute, not worth it unless 0.6B proves limiting), `text-
  embedding-3-large` (API-only, no transparent training data, no
  obvious advantage over Qwen3-0.6B for this task).
- **Compute budget (500K abstracts, Apple M-series with MPS, fp16):**
  SPECTER2 ~30–90 min; SciNCL ~30–90 min; Qwen3-0.6B ~3.5–9 hrs.
  Total ~half a day for a full triple-pass. Storage ~5 GB for arrays.
- **For cross-field expansion (if philosophy or economics is pursued):**
  Qwen3-0.6B graduates from robustness partner to co-primary alongside
  SPECTER2. SciNCL remains a within-family check on SPECTER2 but would
  need an analogous within-family partner for Qwen3, deferred to that
  phase plan.

### 2. Embedding drift mitigation ladder

Per ws2 desiderata §2, §3. Restructured from a linear ladder to a
two-axis framework: **method-sophistication axis** (default → Flavor B)
and **cross-architecture axis** (transformer-only → includes non-
transformer). Flavor A (if adopted) lives on the cross-architecture
axis; Flavor B lives on the sophistication axis. They are complementary,
not sequential.

**Stage 2 default (always run):**
- Mitigation 2 — cross-model replication using the three-model stack
  above (SPECTER2 + SciNCL + Qwen3-0.6B). Qwen3-0.6B's different
  tokenizer is the most load-bearing diachronic check we run cheaply.
- Mitigation 4 — anchor-dimension projection. ~100 curated field-
  specific anchor concepts (stable across eras: "Fourier analysis,"
  "Turing machines," "graph theory," etc., for CS). Report anchor-
  space diversity alongside raw-space diversity as a column in every
  robustness table.

**Phase 0.1 drift-pilot (Check 5c) decides whether Flavor A is
added to Stage 3.** A 100-abstract nearest-neighbor spot-check on
1970–1980 CS under each of the three default-stack models. Quantitative
era-match rate (fraction of top-10 nearest neighbors that are era-
appropriate rather than modern-vocabulary-coincidence). Decision rule:
SPECTER2 era-match >70% → drift manageable, skip Flavor A; <50% →
drift severe, commit to Flavor A; between → commit to Flavor A as
cheap insurance.

**Stage 3 Flavor A (conditional, cross-architecture axis):** Word2Vec
per decade + orthogonal Procrustes alignment on stable anchor words
+ TF-IDF-weighted document aggregation. Hamilton-Leskovec-Jurafsky
2016 template, adapted to document-level via aggregation. Value-add:
genuinely non-transformer embedding family (distributional, non-
contextual) → if Word2Vec-diachronic converges with
SPECTER2+SciNCL+Qwen3 on the divergence trend, cross-architecture
robustness is established.

**Stage 3 Flavor B (conditional, method-sophistication axis):** Fine-
tune SPECTER2 per era on that era's abstracts, align via anchor-paper
Procrustes, compute diversity in aligned space. Invoked if Stage 2
or Flavor A results suggest measurement-level drift remains material,
or if reviewers push on pre-1990 data specifically.

**Stage 3 Flavor C (reserve only):** Dynamic embedding models
(Bamler-Mandt 2017, Rudolph-Blei 2018). Do not invoke unless Flavor B
produces results contradicting domain intuition AND reviewers are
still pushing.

**Document-level diachronic is an underdeveloped literature.** Post-
2018 contextual-embedding diachronic methods (Giulianelli et al. 2020,
Tahmasebi et al. 2021 textbook) operate at word-level; they don't
directly translate to document embeddings. The plan acknowledges
this in Limitations: Flavor B is reasonable engineering, not a
validated template.

**Escalation triggers:**
- Check 5c drift-pilot era-match rate <70% → add Flavor A.
- Stage 2 results differ substantively between raw-space and anchor-
  space (Mitigation 4) → add Flavor B.
- Any pre-1990-data-dependent headline claim requires at least Flavor A.

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

**Methods-framing commitment on weight-by-confidence (per Hofstra C4
walkthrough, lit-review session 2026-04-23).** Weight-by-confidence is
an *uncertainty-propagation policy*, not an *inference-quality fix*.
The Methods section states this explicitly in three sentences: (a) we
do not claim our demographic inferences are reliable in absolute
terms; (b) we claim that our inference uncertainty is propagated into
all downstream confidence intervals, so headline numbers carry visibly
wider bounds where inference is weak; (c) per-region inference
accuracy is reported alongside every aggregate result, so readers can
adjudicate which group-level contrasts survive realistic
misclassification rates. This is a deliberate move away from Hofstra's
"treat all classifications as equally certain" approach, but it does
not generate more accurate inferences — it makes the existing accuracy
visible in the error bars.

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
- **Primary analytic strategy: weight-by-confidence, not exclusion.** All
  authors retained; each demographic attribute's contribution to diversity
  metrics is weighted by its inference confidence (per-variable, per-author).
  Bootstrap CIs are computed over plausible alternative assignments on the
  low-confidence subset, propagating inference uncertainty into reported
  trends. This is the approach Lockhart, King & Munsch 2023 (*Nature Human
  Behaviour*) make the case for — their finding that name-based inference
  error concentrates in marginalized communities means exclusion-by-
  confidence would itself bias the sample; weighting by confidence keeps
  the population intact while making the uncertainty visible.
- **Secondary (ablation):** re-run headline metrics on the Anglo-first-author
  subset only. If the trend direction holds on the ablation, the finding
  is robust to inference-bias concerns. Smaller sample, cleaner inference,
  reduced external validity — report as a robustness check, not a headline.
- **Per-region accuracy reporting in Methods:** document the per-region
  gender-inference accuracy from the ORCID validation subsample. No
  results reported without this accuracy table.

#### 9a. Lockhart 2023 principle-by-principle audit refinements

Surfaced from the Lockhart Key Idea #7 walkthrough. The five principles
form a decision hierarchy (1 → 2 → 3 → {4, 5}); ws2's compliance posture
and the resulting operational refinements:

- **Principle 1 (Critical refusal) — partial.** Race/ethnicity inference
  refused per ws2 desiderata exclusion (post-hoc validated by Lockhart's
  reported 65–73% error rates for Black and MENA subgroups). Gender +
  country-of-affiliation retained with substantive justification (the
  decoupling-claim requires at least one demographic variable and these
  have the most defensible inference posture). **Commitment:** Methods
  paragraph names the refusal explicitly and articulates the substantive
  justification for retained inference — not a default-to-use posture.

- **Principle 2 (Align mechanism with method) — tension acknowledged.**
  ws2 has a genuine Reading-A (ascription) vs. Reading-B (identity)
  tension. **Commitment:** headline-claim language consistently uses
  "ascribed-X" or "name-coded-X" terminology rather than "actually-X."
  Reading-A is the primary substantive frame; Reading-B is reported as
  an extension with explicit caveats around proxy-quality (the gap is
  small for Anglo subgroups, large for Chinese-women / trans / nonbinary).
  Discussion paragraph (~1 paragraph) walks through this distinction
  explicitly.

- **Principle 3 (Population-specific training) — deferred (out of scope).**
  Custom-trained name-inference model on academic CS+Physics 1970–2024 is
  a multi-month engineering project incompatible with ws2's timeline, and
  doubly-circular given the ORCID-having vs. ORCID-lacking compositional
  difference. **Commitment:** Limitations paragraph (~3 sentences)
  explicitly invokes Principle 3 as deferred future work, not as a
  fixable-in-current-study limitation.

- **Principle 4 (High-accuracy subgroups) — refines Holst C3 commitment.**
  The existing Holst C3 commitment to a 100-name gender hand-validation
  is upgraded to **300 names, stratified by name-region × era** —
  six name regions (Anglo, East Asian, South Asian, Arabic-speaking,
  Slavic, other) crossed with three era buckets (pre-1990, 1990–2010,
  2010–2024) yielding 18 cells at ~17 names each. Per-cell accuracy is
  reported in Methods. Cells with per-cell accuracy below a pre-
  registered threshold (locked in Phase 0.2; tentative 70%) are flagged
  in Limitations and bound headline claims that disproportionately
  depend on that cell. The 100→300 upgrade is the cost of supporting
  per-cell accuracy CIs of usable width across both axes; the
  region × era stratification (rather than region-only) is forced by
  C5 spillover-pattern (ii) (gender × era inference-drift, see §9d).

- **Principle 5 (Aggregate + bias-quantification on target population) —
  refines the ORCID validation methodology with a bias-uncertainty band.**
  ORCID-having authors are not a random sample of ws2's target population
  (younger, OS-norms-stronger fields, multi-publication-incentivized,
  US/EU/CN-skewed). The bias-quantification on ORCID-having subset is
  therefore a *partial* bias quantification. **Commitment:** aggregate
  bias correction is reported as a band rather than a point estimate:
  - Lower bound: aggregate corrected by ORCID-only-quantified
    disagreement matrix (assumes ORCID-bias generalizes to non-ORCID).
  - Upper bound: aggregate corrected by combining ORCID-quantified
    matrix with NamSor's published per-region accuracy tables (treats
    ORCID and NamSor sources as bracketing).
  Headline demographic-plurality claims are reported with this
  bias-uncertainty band (e.g., "women share in CS-2020: 28–32% under
  bias-uncertainty bracket"), not as point estimates. Methods explicitly
  cites Lockhart 2023 Principle 5 as the operational basis.

These refinements are framing + budget-light operational changes; the
core pipeline (NamSor + Genderize + ORCID validation) is unchanged.

#### 9b. Within-between decomposition — composition-shift artifact diagnostic

Surfaced from the Lockhart C1 walkthrough. The Lockhart finding (name-
based inference accuracy heterogeneous across regions: 43% misgendering
for Chinese women, ~7% for Anglo women) combined with the empirical
fact that ws2's regional composition shifts substantially over
1970–2024 creates a measurement-artifact alternative explanation for
any temporal demographic-plurality trend: apparent change in plurality
could be (a) substantive within-region behavioral change OR
(b) cross-region composition shift interacting with subgroup-specific
misclassification rates.

This is structurally identical to the Holst 2024 critique of PLF
(composition shift in zero-reference papers driving the apparent
CD-index decline). The defense is structurally analogous: a Holst-style
three-layer pattern with an empirical-diagnostic layer specifically
designed to discriminate (a) from (b).

**Commitment.** For every reported temporal demographic-plurality
trend, compute and report a within-between decomposition of the change:

  ΔP(t → t+Δt) = Δ_within + Δ_between + interaction

where Δ_within holds regional composition fixed at t (isolates within-
region behavioral change); Δ_between holds within-region rates fixed
at t (isolates composition shift); interaction is the residual cross-
term.

Two operationalizations reported in parallel:
- **Primary (Theil-style additive decomposition):** uses the Theil
  index's natural additivity across partitions (T_total = T_within +
  T_between). Report ΔT_within and ΔT_between separately. Theil is
  already in ws2's committed plurality-metric basket per desiderata §8.
- **Secondary (DFL-style counterfactual reweighting):** for non-
  additively-decomposable plurality metrics (Shannon entropy, Gini),
  construct counterfactual distributions at t+Δt with t's composition
  vs. with t's within-region rates; compute the resulting plurality
  changes. Reported as confirmation of the Theil-based diagnostic.

**Trigger threshold.** If |Δ_between| / |Δ_total| > 0.33 for any
reported temporal trend, the composition-shift artifact concern is
load-bearing for that trend, and three-way (gender × region × era)
accuracy validation becomes mandatory for that trend. Threshold chosen
asymmetric-cost: failure to validate when validation was needed
(methodological-artifact attack on headline) is higher-cost than
extra-validation when not strictly needed; lower-third threshold biases
toward methodological caution.

**Three-way validation source when triggered.** ORCID subsample
stratified by region × era (primary), supplemented by extended hand-
validation if any era × region cell has insufficient ORCID coverage.
Per-cell accuracy estimates feed a bias-corrected version of the
headline trend, reported alongside the uncorrected version with the
bias-uncertainty band of §9a P5.

**Residual concern (Limitations).** The decomposition assumes within-
region inference rates are correctly measured, but Lockhart's findings
imply within-region heterogeneity (Chinese-women specifically are
heavily misclassified relative to other East-Asian-coded women). The
decomposition therefore diagnoses *measured* within-vs-between
contributions, not *true* contributions. Limitations paragraph
(~3 sentences) flags this residual concern explicitly; full resolution
would require either custom region-population-specific training models
(Lockhart Principle 3, deferred per §9a) or substantially expanded
hand-validation budget at sub-regional resolution.

**Three-layer defense — demographic side (parallel to canonical
side's PAP+Holst+PAP-2025 chain):**
- **Theoretical layer:** Lockhart 2023 principle-by-principle audit
  (§9a).
- **Empirical-diagnostic layer:** within-between decomposition (§9b,
  this section).
- **Controlled-analysis layer:** conditional three-way validation when
  diagnostic triggers (§9b trigger).

#### 9c. ORCID coverage transparency + multi-source bias-quantification

Surfaced from the Lockhart C2 walkthrough. §9a P5 commits to a bias-
uncertainty band leaning primarily on ORCID-quantified disagreement
matrices. Lockhart Principle 5 explicitly requires bias-quantification
on the *target* population. ORCID-having authors are not a random
sample of ws2's target — coverage is structurally weakest in the
exact subgroups where Lockhart predicts the largest misclassification:

- Pre-1990 cohort (ORCID launched 2012; pre-1990 retroactive adoption
  near zero) — interacts adversarially with the §13 pre-1990
  retention non-negotiable.
- Non-Western subgroups (Chinese, Indian, much of Global South — local
  ID systems substitute; ORCID adoption uneven).
- Possibly women (some empirical evidence of gender-asymmetric ORCID
  adoption).
- Career-stage skew (multi-publication mid/senior researchers
  overrepresented; one-paper authors undercount).
- Self-reported gender field is optional within ORCID, narrowing the
  validated subsample further.

§9a P5's bias-uncertainty band as currently specified is structurally
too tight in the regions of the target population where Lockhart
predicts the largest misclassification. C2's resolution is fundamentally
partial — there is no diagnostic that fully escapes the ORCID coverage
gap. The commitment is to acknowledge the partial nature, supplement
with multi-source bracketing, widen the band where coverage is weakest,
and acknowledge the residual.

**Commitments:**

1. **Coverage transparency.** Report ORCID-validated coverage rate
   per (era × region × gender) cell in Methods. Cells with coverage
   below a pre-registered threshold (locked in Phase 0.2; tentative
   20%) are flagged as bias-quantification-weak.

2. **Multi-source bias-quantification.** For each cell of interest,
   combine three sources of bias estimate:
   - (a) ORCID-derived disagreement matrix (where coverage permits).
   - (b) NamSor's published per-region accuracy tables (vendor-
     published bracketing).
   - (c) Targeted hand-validation specifically filling cells with weak
     ORCID coverage (drawn from the §9a P4 300-name budget where
     possible; supplemented if necessary).
   The bias estimate per cell is the multi-source combination, weighted
   by source-credibility per cell.

3. **Subgroup-conditional bias-correction (conditional).** Fit
   *conditional* disagreement matrices per (era × region) cell where
   data permits, rather than a single population-wide matrix. Used
   when §9b within-between decomposition triggers a load-bearing
   concern for a specific cell.

4. **Bias-uncertainty band widens proportional to coverage strength.**
   For cells with weak ORCID coverage, the §9a P5 band is widened by
   an additional Δ (locked in Phase 0.2) reflecting the lower-
   confidence bias estimate. Reported widening is per-cell, transparent
   in Methods.

5. **Limitations paragraph (~4 sentences).** Acknowledges the residual
   coverage-gap concern as a hard limit on principle-5-compliance for
   ws2 — full resolution requires either custom region-population-
   specific training (Lockhart Principle 3, deferred per §9a) or
   substantially expanded hand-validation. The residual is named, not
   dissolved.

#### 9d. Cross-dimensional spillover — enumeration + sensitivity checks

Surfaced from the Lockhart C5 walkthrough. ws2 has 7+ inferred or
derived demographic dimensions (gender, country of current affiliation,
country of earliest affiliation, institution type, prestige tier,
career stage, training-institution concentration). Errors in any one
dimension propagate to inferences about correlated dimensions through
analyses that condition on or stratify by them.

Lockhart's specific examples (disability × nonbinary spillover) don't
apply directly to ws2 (different demographic dimensions), but the
structural phenomenon does. Methods explicitly enumerates the six
anticipated spillover patterns rather than the aggregate "spillover is
a known concern" framing — honoring Holst-style methodological
discipline (name alternative explanations, then rule them out or
absorb them into uncertainty bounds):

**(i) gender × name-region — circularity, not classical spillover.**
NamSor uses name-region as a feature in gender inference. Per-region
NamSor accuracy is partly diagnostic of NamSor's internal feature
dependency, not an independent validation. Independent validation
comes from ORCID + hand-labeled ground truth (per §9a P4, §9c).
Methods explicitly distinguishes these. No additional sensitivity
check needed (already addressed by §9a P4 + §9c).

**(ii) gender × era inference-drift — load-bearing for headline
trend.** Romanization conventions and naming patterns shift across
eras (Pinyin standardization 1958 with uneven academic-publishing
uptake through 1980s; women's citation conventions evolved through
20th century). Inference accuracy plausibly differs across eras
independent of region. **Sensitivity check:** Holst C3 / §9a P4 hand-
validation is stratified region × era (forced here by C5 spillover
(ii); 300 names across 18 cells); per-cell accuracy reported.

**(iii) name-region × country-of-affiliation — diaspora confounding.**
Most East-Asian-named authors work at East-Asian institutions;
diaspora is the unusual case. Errors confusing diaspora with domestic
propagate to country-of-affiliation comparisons. **Sensitivity check
(Stage 3 robustness sweep):** repeat country-of-affiliation analyses
on the domestic-only subset (excluding likely diaspora — name-region ≠
affiliation-region); trend stability is the test.

**(iv) gender × prestige — entangling regional composition.** Top-50
institutions have historically had different regional composition than
non-prestige. Prestige-stratified gender-plurality claims entangle
substantive gender-prestige correlation, regional composition by
prestige, and region-specific misclassification. **Sensitivity check
(Stage 3):** disaggregate gender plurality by prestige tier *and* by
region; report decomposition.

**(v) country-of-affiliation × institution type — industry concen-
tration confound.** Industry-heavy countries (US, UK, Israel) bias
institution-type analyses through country correlation. **Sensitivity
check (Stage 3):** institution-type analyses run with country fixed
effects.

**(vi) career stage × gender × era — publication-gap interaction.**
Career-stage inference uses year of first publication. Women
historically had publication-gap interruptions; the career-stage
estimator may be biased for these cohorts. **Acknowledged in
Limitations** — no sensitivity check committed (lower-priority
secondary concern).

Patterns (i) and (ii) are addressed within Phase 0.2 / §9a / §9c
framework; (iii), (iv), (v) are committed as Stage 3 robustness sweep
deliverables; (vi) is Limitations-only.

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

### 12. Text representation and full-text policy

**Primary representation: title + abstract.** All embedding-based
analyses (semantic diversity, Test IV novelty metrics, anchor-dimension
projection) use title + abstract only. Matches SPECTER2's training
distribution, matches convention in scientometric embedding work
(Chu-Evans 2021, Hofstra et al. 2020, etc.), and provides high coverage
across the 1970–2024 window.

**Full-text is not required** for any primary analysis. Pre-1990
full-text coverage is prohibitively uneven; requiring full-text would
collapse the pre-1990 sample and defeat the paper's 50-year arc.

**Reference-list metadata for novelty computation.** Test IV primary
novelty (N_p = cosine distance from paper to cited-papers centroid)
uses OpenAlex's structured reference metadata, not full-text. Test IV
tertiary (Uzzi-Mukherjee-Stringer recombinant novelty, Stage 3) also
uses references. So reference-based analyses are cleanly doable
without full-text.

**Stage 3 arXiv full-text robustness (optional).** For the subset of
papers with arXiv full-text (CS post-1993ish, Physics post-1991ish),
re-run primary semantic-diversity metrics using long-context Qwen3
embeddings of the full text. Compare trend direction to the abstract-
based result. Purpose: test whether abstract summaries miss
substantive content that would change the divergence finding. Cost:
2–3 extra days of compute on the arXiv subset; arXiv is free and
legal. Limitation: covers only post-1991/93 window, so doesn't help
with 1970s drift concern — complements rather than replaces the
drift-mitigation ladder.

**Limitations acknowledgment (pre-baked for Methods section):**
abstracts are high-level summaries; they can mask methodological
similarity between papers with different approaches. Abstract-only
representation may over-state semantic similarity for methodologically-
distinct-but-topically-similar papers.

### 13. Pathway coverage and pre-1990 data retention

**Pathway coverage — what ws2 commits to saying about each of
Claim #13's 8 pathways.** Prevents over-claiming in the paper and
clarifies positioning vs. whitespace 1 (agent-based simulation).

| Pathway | ws2 engagement | Mechanism |
|---|---|---|
| 13-A Channel/recommender convergence | Circumstantial | Break-point timing near platform-era transitions (arXiv '91–93, web '93, foundation models '18–'20) is suggestive but not dispositive. Cannot separate from other mechanisms firing in same era. |
| 13-B Demographic-diversification-as-cosmetic | **Direct test** | Tests I–III operationalize this. Divergence confirms, tracking disconfirms, delayed tracking qualifies. Paper's central claim maps 1:1 onto 13-B. |
| 13-C Institutional selection pressure | Indirect | Prestige and career-stage shifts captured in demographic decomposition; Test II controls for these. Doesn't affirmatively identify 13-C as mechanism. |
| 13-D Network-topology canonical convergence | **Direct test** | Chu-Evans Spearman operationalizes 13-D. Subfield mechanism test (canon-concentration → divergence) provides direct mechanism evidence if γ₁ > 0. |
| 13-E Translation/linguistic asymmetry | Silent | English-language corpus; translation dynamics out of scope. |
| 13-F Measurement artifact (null) | **Directly constrained** | Drift-mitigation ladder + metric plurality + cross-model replication + field-level replication together constrain 13-F. Not a positive test; a rigorous rebuttal. |
| 13-G Individual-level conformity psychology | Silent | No individual-level conformity measures in observational-aggregate design. |
| 13-H Endogenous actuator emergence | Weakly suggestive | Break-point analysis can reveal non-linear dynamics consistent with tipping-point emergence. Emergence mechanisms (causal dynamics) are out of scope. |

**Influence-structure characterization (load-bearing in Discussion):**
ws2 does not observe individual author-to-author influence edges. It
provides aggregate correlates only — canonical concentration, training-
institution concentration (Proxy A), subfield mechanism test, Stage 3
advisor Proxy B. Which *specific* influence channels drive any
observed homogenization (shared textbooks vs. shared advisors vs.
shared platforms vs. shared training institutions) is not identifiable
from our data. That is the domain of interventional/simulation work —
explicitly whitespace 1.

**Pre-1990 data retention policy (non-negotiable).** Pre-1990 data is
retained in all primary analyses despite known measurement weaknesses
(classifier drift §10, embedding drift §3, sparser abstracts, weaker
demographic inference). Rationale:

1. **13-B requires a pre-diversification baseline.** The substantive
   claim ("demographic diversity rose while intellectual diversity
   didn't") needs the pre-acceleration era to be measured, not just
   assumed. Demographic diversification in CS and Physics accelerated
   substantially post-1990; clipping to post-1990 would start *at the
   inflection* rather than before it, losing the statistical leverage
   to identify the baseline-to-acceleration transition.
2. **13-D requires cross-subfield variation in canon-concentration.**
   Pre-1990 subfields had less-established canons (young CS fields
   pre-Knuth-textbooks, emerging physics subfields pre-high-Tc). This
   is exactly the variation the within-field subfield mechanism test
   needs on the right-hand side. Clipping compresses the variation.
3. **Ruling out 13-F (null) requires surviving worse measurement.**
   A trend that appears only post-1990 is consistent with "measurement
   became clean, not that anything actually changed." A trend that
   persists in the noisier pre-1990 data (after drift mitigation) is
   substantively harder to explain as a pure measurement artifact.
   Paradoxically, keeping the noisy era *strengthens* the rebuttal to
   the null.

**Asymmetric measurement-reliability handling.** Rather than clipping,
the plan applies different restrictions to different analyses:

- **Primary divergence tests (I–III):** span 1970–2024. Drift mitigation
  handles measurement concerns.
- **Subfield mechanism test:** restricted to post-1990 (desiderata §10 —
  classifier drift on pre-1990 subfield tags is untenable). This is a
  measurement-reliability restriction on *one* analysis, not a project-
  wide clip.
- **Full-text robustness:** post-1991/93 subset (arXiv coverage).
- **Demographic inference:** weight-by-confidence with per-era accuracy
  reporting; no clipping.

**Concrete pre-1990 break-point candidates** (added to the break-point
analysis pre-registration):

- **CS 1986:** first neural-network revival (Rumelhart-Hinton-Williams
  PDP volumes). Subfield rebirth event visible in aggregate citation
  and embedding structure.
- **Physics 1986:** high-Tc superconductivity discovery (Bednorz-Müller).
  Field-transforming event; new cohort of researchers, global interest.
- **Physics 1991:** Soviet Union dissolution → mass outflow of Soviet-
  trained physicists and mathematicians to the West. Demographic shock.

These join the existing candidate set (CS: 1991–93, 1998–2000, 2008–09,
2012, 2018–20; Physics: 1991, 1995–2000, 2012) with Bonferroni
correction within each field's expanded candidate list.

### 14. Methods overview framing — three parallel construct-validity audits

The Methods overview paragraph frames ws2's three metric channels
(demographic, semantic, canonical) as parallel construct-validity audits,
each with a structured proxy-vs-thing-of-interest gap and a corresponding
external audit framework: Lockhart 2023 principles 1–5 for demographic;
embedding-drift checks (desiderata §3) + within-family robustness for
semantic; PAP 2024 three-conditions framework for canonical. Headline
claims on each channel are bounded by the respective audit's documented
residual uncertainty. Framing-only commitment (no new operational change);
locked here so the Methods drafting phase does not re-open it.

## Sanity checks (this phase's empirical work)

Deliverables in rough order:

### Check 1 — Abstract availability by year

- **What:** fraction of papers in the pilot pull with a non-empty abstract,
  by year.
- **Why:** abstract availability is the upstream bottleneck for both concept
  classification and semantic embedding. Worst-case years get a bounded
  mitigation strategy.
- **Output:** plot + summary table in `experiments/phase-0.1/abstract-coverage.{png,md}`.
- **Expected (pre-run):** high (>95%) from ~1990 onward; drops sharply before ~1985.
- **Status (run 2026-04-27):** **complete; expectation falsified.** The
  pre-run hypothesis was qualitatively wrong. Actual coverage is a smooth
  gentle rise from ~30% (1970) to ~70% (2024) in CS, with **no sharp
  pre-1985 drop** and **neither field ever crossing 80%**. Physics
  consistently ~15 pp above CS. Spot-check confirms `has_abstract` logic
  is correct; the finding reflects OpenAlex's actual abstract coverage
  (publishers do not all permit redistribution). Strict §13 escalation
  rule is not triggered (CS pre-1990 mean = 33% > 30% threshold), but
  the **bigger finding** — post-1990 coverage at ~50% rather than ~95%
  — is a structural surprise that warrants discussion before Check 2.
  See `experiments/phase-0.1/abstract-coverage.md` for the full result
  and recommended next steps (re-evaluate §12 full-text policy as
  primary rather than robustness; pause Check 2 design until selection-
  bias implications are addressed).
- **Status (Check 1c, run 2026-04-27):** **type-disaggregation does not
  rescue coverage.** Articles (~80% of sample) are at 45-60% coverage —
  almost exactly the overall rate. Scoping to articles-only or excluding
  the worst types (book-chapter, book, paratext) yields only a 3-pp
  improvement (CS: 44%→47%). The constraint is genuinely uniform across
  analytically-relevant paper types. **One bright signal:** preprints
  have 81-87% coverage, consistent with the arXiv-supplementation
  hypothesis (arXiv records have abstracts; missing coverage is
  concentrated in non-arXiv-sourced records). This sharpens the case
  for promoting arXiv full-text from §12 robustness check to primary
  alternative data path. Proposed follow-up Check 1d: measure
  arXiv-has-an-ID rate and joint OpenAlex-OR-arXiv coverage by year ×
  field. See `experiments/phase-0.1/abstract-coverage-by-type.md`.
- **Status (Check 1d, run 2026-04-27):** **two findings, one clean null
  and one inconvenient surprise.**
  - **Access-method verification (clean null):** 100-paper spot-check
    re-fetched no-abstract papers via direct ID lookup (different code
    path than `?filter`+`?sample`). 100/100 confirmed no abstract via
    direct path. The ~50% bottleneck is **not** an artifact of anonymous
    access or `?sample` interaction — it is the real OpenAlex data
    state.
  - **arXiv linkage in OpenAlex is essentially absent (surprise):**
    only 1.4% (CS post-1991) / 4.8% (Physics post-1991) of papers have
    an arXiv linkage flagged in OpenAlex's `locations`. Joint
    (abstract OR arxiv) coverage is essentially identical to abstract-
    only coverage. This **rules out path (A) as originally conceived**
    (use OpenAlex `locations` to find arXiv-supplemented papers).
    OpenAlex's source-linkage to arXiv is conservative — most CS/Physics
    papers with arXiv preprints don't have arXiv flagged as a location.
  - **Refined options:**
    - **(A')** Direct arXiv API integration via DOI/title matching —
      slow (1 req/3s rate limit), feasible but multi-day batch.
    - **(C)** S2AG (Semantic Scholar) as primary abstract source —
      already in `data/README.md` as primary SPECTER2 embedding source;
      likely has better abstract coverage and arXiv linkage. Worth a
      Check 1e (measure S2AG abstract coverage on the same 22K
      sample, ~5 min, $0).
    - **(B)** Acknowledge in Limitations and proceed with narrower
      analytical population (~50% of OpenAlex CS+Physics papers).
  - See `experiments/phase-0.1/arxiv-coverage.md`.
- **Status (Check 1e, run 2026-04-27):** **path (C) decisively ruled out.**
  S2AG fill rate on OpenAlex no-abstract subset post-1990 is 2.2% (CS) /
  5.2% (Physics) — far below the 50% threshold. S2AG actually has *less*
  abstract coverage than OpenAlex on this sample (9.7% / 15.5% post-1990),
  not more. The two sources overlap heavily on abstract-having papers;
  joint (OA OR S2AG) is only 1-2 pp higher than OpenAlex alone. The mental
  model "SPECTER2 trained on S2AG → S2AG has best CS/Physics coverage" is
  backwards: SPECTER2 was trained on *the S2AG corpus that exists*, which
  is dramatically smaller than OpenAlex's CS+Physics population. DOI-join
  feasibility is also weaker than expected (55.8% / 72.1% DOI rate; 69.6%
  / 85.8% S2AG-found rate among DOI-having). **Remaining options:** path
  (A') direct arXiv API integration (multi-day batch job, fragile DOI/title
  matching), or path (B) acknowledge the structural ~50% bottleneck in
  Limitations and proceed with the narrower analytical population. See
  `experiments/phase-0.1/s2ag-coverage.md` for full interpretation and
  proposed next steps.
- **Status (Check 1f, run 2026-04-27):** **bias-of-missingness diagnostic
  surfaces three structurally important biases, each aligned with one of
  ws2's substantive measurement axes.** Path (B) without corrections is
  unsafe; we are partially in (M3) territory.
  - **Citation count → canonical-concentration (significant):** CS low-
    citation tertile (0-1 cites) has 36.7% abstract coverage; mid-citation
    tertile (2+) has 62.5% — a **26 pp gap**. Abstract-having CS papers
    are systematically the higher-impact papers. Physics shows same
    direction, smaller magnitude.
  - **Concept → semantic-plurality (moderate):** 93 level-1 concepts span
    20.3% – 89.0% coverage (IQR 13.3%). Subfields differ wildly.
  - **Country → demographic-plurality (compounded):** 25 known countries
    span 41-99% (IQR 11.0%) — moderate, but **55% of papers (n=12,174)
    have UNKNOWN first-affiliation country** in OpenAlex's authorship
    data. Demographic-plurality measurement is doubly precarious.
  - **Recommended path: (M2 + bounded M3).** Path (B) with selection-on-
    observables corrections via inverse-probability-of-abstract-
    availability weighting (propensity fit on year × field × type ×
    citation-tertile × concept-cluster × known-country). Bound
    corrections by propensity-model reliability. Restrict demographic-
    plurality claims to the ~45% with determinable country. Report
    corrected and uncorrected aggregates with explicit selection-bias
    bounds.
  - **New Phase 0.2 commitment:** formally define ws2 analytical
    population as "OpenAlex CS+Physics 1970-2024 with non-empty
    abstract_inverted_index"; demographic-plurality analyses additionally
    require a determinable first-authorship country.
  - **New diagnostic layer added to the Holst three-layer defense
    pattern:** selection-bias-correction-as-empirical-diagnostic, parallel
    to the within-between decomposition (§9b). Methods overview (§14)
    gains a fourth construct-validity layer for the selection-bias
    correction itself.
  - See `experiments/phase-0.1/missingness-bias.md` for full
    interpretation including impact on §13 pre-1990 retention, §9a/b/c/d
    Lockhart audit chain, and the three-layer defense.

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

- **Status (Check 2 a/b/c, run 2026-04-27):** 2a undefined as sampled (every
  paper has the field concept by sampling design — needs a different sampling
  strategy; deferred to plan revision). 2b: modest temporal trend in concepts-
  per-paper (CS 8.05→9.29 +15%, Physics 13.18→14.42 +10%) — not a red flag.
  2c: confidence scores era-stable (CS max-score 0.58→0.60; Physics 0.75→0.76)
  — no drift. Within papers the classifier tags, tag confidence is reliable
  across eras. The **deeper question is tagging *correctness***, addressed by
  2d + 2e. See `experiments/phase-0.1/classifier-drift.md`.
- **Status (Check 2d, run 2026-04-27):** **decisive red flag — 14 of 20
  modern concepts (70%) show multi-decade anachronistic tagging.** Examples:
  Deep learning earliest=1907 (gap 99 yr); CRISPR earliest=1905 (gap 107 yr);
  Internet earliest=1901 (gap 89 yr); Cloud computing earliest=1901 (gap 105
  yr). Many "earliest" years cluster suspiciously at 1901-1907, suggesting
  either retroactive label assignment or sentinel/junk publication_year
  metadata propagating into modern-tagged papers — either way, the
  `publication_year × concept_id` join is unreliable for identifying topic
  origins. See `experiments/phase-0.1/anachronism-audit.md`.
- **Status (Check 2e setup + directional read, run 2026-04-27):** **OpenAlex
  concept tagger is promiscuous in both eras.** Top-cited papers tagged with
  "Operating system" 1975: ~90% off-target (Kahneman-Tversky, Salton, Tinto,
  Mayhew, etc.); 2020: ~95% off-target (bioinformatics, COVID dashboards,
  vision ML, structural biology). Compilers 1975: ~50% off-target. Tag
  promiscuity is era-stable (consistent with 2c) but tag *correctness* is
  poor regardless. Full 200-row hand-audit pending; directional read is
  decisive. See `experiments/phase-0.1/hand-audit-papers.md`.
- **Combined Check 2 verdict:** **OpenAlex concept tags cannot be used as
  reliable subfield labels at any era.** The classifier produces
  multi-decade anachronistic tags (2d) AND promiscuously attaches modern
  topic tags to peripheral papers (2e). What survives:
  - Level-0 field tags (CS C41008148, Physics C121332964) for population
    restriction — but with documented field-restriction noise that adds to
    Check 1f's selection-bias-correction burden.
  - Concept-count and confidence-score *features* per paper (2b/2c stable).
  - **What does NOT survive:** OpenAlex concepts as the granular subfield
    ontology for semantic-plurality measurement.
  - **New Phase 0.2 commitment (strengthened from desiderata §11):**
    semantic-plurality measurement uses embedding-cluster-based subfield
    assignment exclusively; OpenAlex concept tags are NOT used as the
    subfield ontology. Concept tags retained only for population
    restriction (level-0) and as features.
  - This **strengthens** the §11 cluster-fit-on-temporally-stratified-
    pooled-subsample commitment from "preferred approach" to "necessary
    approach." Methods-section framing of the subfield mechanism shifts
    from "concept-tag-based with embedding-cluster robustness" to
    "embedding-cluster-based with concept-tag features as auxiliaries."

- **CORRECTION (Check 2 re-analysis, 2026-04-27, user-prompted):** the Check
  2e "~95% off-target" framing was a query artifact, NOT a classifier failure.
  OpenAlex's `concepts` array on each paper includes ALL concepts the
  classifier considered, including those scored 0.0 (explicitly rejected).
  The `concepts.id:X` filter returns ANY paper where X appears in the array
  regardless of score. Score-thresholded results (see
  `check2-correction-score-thresholds.md`):
  - OS × 1975 top-50: 45/50 are zero-score; **0/50 score≥0.3**.
  - OS × 2020 top-50: 41/50 are zero-score; **1/50 score≥0.3**.
  - Compilers × 1975 top-50: 2/50 zero-score; **46/50 score≥0.3** (and ≥0.5).
  - Compilers × 2020 top-50: 4/50 zero-score; **45/50 score≥0.3**.
  When score-thresholded, the classifier is reliable. The "promiscuous in
  both eras" finding below is **retracted**.
  - **Retract the strengthened §11 commitment.** OpenAlex concept tags are
    NOT broken; the issue was using `concepts.id:X` without score
    thresholding. The §11 cluster-fit commitment remains the *preferred*
    subfield mechanism per the original desiderata, but is no longer
    "necessary." Both mechanisms (score-thresholded concept tags AND
    embedding-cluster-based) are viable; the choice is based on substantive
    criteria (cluster coherence, era-stability, etc.), not on a perceived
    failure of one.
  - **New Phase 0.2 commitment:** ws2's pipeline must respect score
    thresholds when filtering by OpenAlex concept ID. Default thresholds
    for subfield-membership claims: score ≥ 0.3 (loose, inclusive) or ≥ 0.5
    (strict). Pre-register specific thresholds per use case in Phase 0.2.
  - **Note on Check 2d anachronism:** the multi-decade anachronism finding
    is REAL — earliest "deep learning" papers from 1907 actually have
    score=0.527; "Cloud computing" 1901 has score=0.416. Not zero-score
    noise. The classifier really does produce meaningful scores for modern
    concepts on very old papers, likely via keyword matching ("deep",
    "cloud") in unrelated contexts. **However:** these are pre-1920 papers,
    outside ws2's 1970-2024 analytical window. Within-window anachronism
    needs a separate score-thresholded check before drawing conclusions.
  - **lesson learned:** OpenAlex's `concepts` array semantics differ from
    typical concept-tagging APIs — it's a "considered" set, not an "about
    it" set. Always score-threshold client-side. Logged in
    `tasks/lessons.md`.

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

**5c — Drift pilot (nearest-neighbor era-match rate):**
- **What:** sample 100 abstracts from 1970–1980 CS. For each, compute
  top-10 nearest neighbors in each of the three default-stack models
  (SPECTER2, SciNCL, Qwen3-0.6B). Classify each neighbor as era-
  appropriate (other 1970–1990 paper on related topic by domain-read
  inspection) vs. era-mismatched (post-2000 paper sharing a surface
  word but not the topic). Compute per-model era-match rate.
- **Why:** decides whether the Stage 3 conditional Flavor A (Word2Vec
  diachronic) is added to the drift-mitigation ladder (subsection 2).
  Cheaper than committing to Flavor A a priori; empirically grounded.
- **Output:** `experiments/phase-0.1/drift-pilot-results.md` —
  per-model era-match rates, inspected-neighbor examples,
  qualitative commentary on where each model's failures concentrate.
- **Decision rule:** SPECTER2 era-match rate >70% → drift manageable,
  skip Flavor A; <50% → drift severe, commit to Flavor A; 50–70% →
  commit to Flavor A as cheap insurance. Applied at Phase 0.1 closure.

### Check 6 — Methodological literature deep dive (parallel track)

Parallel to sanity checks 1–5; runs concurrently with the empirical
data work. Deliverable gates Phase 0.2 (pre-registration).

- **What:** close methodological read of the ~10 Tier-1 and Tier-2
  papers confirmed in `literature-review/README.md`. Per paper:
  structured review document with three-level discourse (smart
  high-schooler / junior-senior undergrad / early grad), study questions
  (basic / intermediate / advanced), challenge questions (to be
  answered in discussion), plus convention sections (background, key
  ideas, connection to ws2, key quotes, synthesis pointers,
  discussion notes filled during review sessions). Template matches
  sibling house style (`inverse-device-design/literature-review/`
  format) with the three MUST-have elements (discourse levels, study
  questions, challenge questions) pinned as non-negotiable.
- **Why:** every ws2 methodology choice inherits from or diverges from
  specific prior work. Close reading (a) validates our Phase 0.2
  pre-registration commitments against current methodology, (b)
  prevents re-litigation of choices in later phases, (c) produces
  the structured notes that get harvested into ws2's Methods and
  Related Work sections.
- **Scope:** Tier 1 papers (read closely, deep review): Chu-Evans 2021,
  Park-Leahey-Funk 2023, Petersen 2024 QSS (positioning read),
  Petersen 2025 JOI (close methodological read — directly relevant to
  Test IV), Holst et al. 2024, Hofstra et al. 2020, Lockhart et al.
  2023. Tier 2 (read for methodology, not every claim):
  Wu-Wang-Evans 2019, Singh et al. 2023 SciRepEval, Cohan et al.
  2020 SPECTER, Ostendorff et al. 2022 SciNCL, Hamilton-Leskovec-
  Jurafsky 2016, Uzzi-Mukherjee-Stringer 2013 (correction: fourth
  author is Stringer not Stone), Kozlowski et al. 2022, Funk et al.
  2026 (disruption-decline inventory), Culbert et al. 2024/2025
  (OpenAlex coverage).
- **Output:** `literature-review/README.md` (master reading list,
  tiers, per-paper status tracking, template). `literature-review/XX-
  <slug>.md` per Tier 1 and Tier 2 paper. `literature-review/
  synthesis.md` (cross-paper synthesis harvested into ws2's Related
  Work / Methods sections).
- **Petersen distinction:** 2024 QSS is the broader citation-inflation
  critique — positioning read (~2 hrs) justifying our CD-index
  exclusion. 2025 JOI is the team-size / CD re-analysis — close read
  (~4 hrs) because it directly challenges the Wu-Wang-Evans team-size
  interpretation that underpins our Test II team-size control and
  Test IV's team-diversity × novelty setup. Read both; close-read 2025
  JOI, positioning-read 2024 QSS.
- **Effort estimate:** ~30 hours total (Tier 1: ~15 hrs deep reads;
  Tier 2: ~15 hrs methodological reads). Parallelizable with
  empirical Check 1–5 work.
- **Decision rule:** if a close read surfaces a methodology choice that
  contradicts Phase 0.1 commitments, Phase 0.1 re-opens. Better to
  re-plan once than ship the wrong Phase 0.2 pre-registration.

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
   - `drift-pilot-results.md`
5. **`data/metadata/pilot-query-results.parquet`** — 1000-paper pilot pull.
6. **Literature review artifacts** under `literature-review/`:
   - `README.md` — master reading list, tiers, status tracking, template
   - `XX-<slug>.md` per Tier 1 and Tier 2 paper (~16 files)
   - `synthesis.md` — cross-paper synthesis
7. **Statistics primer** at `docs/primers/stats.{tex,pdf}` (already
   committed earlier this phase; compiled 20-page PDF).
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
8. **Literature review closed.** Tier 1 + Tier 2 papers each have a
   committed review file following the template; `synthesis.md`
   harvested; no surfaced contradictions with Phase 0.1 methodology
   commitments remain unaddressed.
9. **Drift-pilot decision committed.** Check 5c era-match rate
   reported; Flavor A either committed (with rationale) or deferred
   (with rationale); decision logged in the retro.
10. **Consolidation pass.** Once literature review (Check 6) closes,
    perform a holistic review of accumulated framing artifacts,
    Synthesis Pointers across review files, Epistemic Scope
    subsections in `conceptual.md`, and pending Phase 0.2
    pre-registration batch items. Compress or prune where the
    accumulated material is overlapping, noise, or doing less work
    than its maintenance cost implies. Deliberate deferral to end of
    lit review (rather than pruning continuously): pruning decisions
    are higher-quality once the full cross-paper landscape is visible,
    at the cost of temporarily carrying some redundancy. The
    consolidation itself produces a short `experiments/phase-0.1/
    consolidation-notes.md` documenting what was pruned, what was
    kept, and why — useful for the retro and for future phases
    considering similar accumulation patterns.

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
    with subfield-level controls, cluster-robust standard errors.
    H₁: γ₁ > 0 (canonical-concentrated subfields show more divergence).
    Separate correction regime from the field-level tests — single
    test, α=0.05. Subfield-level controls:
    - log(papers in subfield) — field-size confound (per Chu-Evans
      SQ6 walkthrough).
    - mean team size in subfield — Wu-Wang-Evans 2019 confound.
    - subfield age (years since first paper).
    - **Mean age-dispersion of cited work** (per Park-Leahey-Funk
      Extended Data Table 1, lit-review session 2026-04-26): for
      each paper p in subfield s, compute the standard deviation of
      publication years of papers in p's reference list; aggregate
      to subfield-year level by mean. Captures temporal-concentration
      dimension (does the field engage with its history or only with
      recent work?) — distinct from CanonConc's paper-identity-
      concentration dimension. Without this control, γ_1 is a blended
      effect of paper-identity concentration + temporal narrowing;
      with it, the two mechanisms are separable. Computationally
      trivial (uses existing OpenAlex reference data).
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
    - **Paper-level team demographic diversity (T_p) — multi-operationalized
      (per Hofstra C9 framing, lit-review session 2026-04-23).** Authorship-
      norm regimes differ across our subfields: hierarchical (CS, much
      experimental physics — first/last authors carry disproportionate
      intellectual weight); alphabetical (high-energy physics — author order
      conveys little); egalitarian (some theory subfields). A single T_p
      operationalization collapses across these regimes and bakes in an
      assumption the lit-review pushback identified as wrong. Therefore,
      compute and co-report multiple operationalizations:
      - **T_p_full (co-primary):** Rao's Q over the full author team with
        uniform weights. Maps cleanly to alphabetical-norm regime;
        approximates field-level composite at small team sizes. The
        "team-as-collective" estimand.
      - **T_p_first (co-primary):** demographic feature vector of the first
        author only. Maps cleanly to hierarchical-norm regime; gives the
        most direct dissertation-to-paper transfer of Hofstra's
        single-individual finding. The "lead-intellectual-contributor"
        estimand.
      - **T_p_last (sensitivity):** demographic feature vector of the last
        author only. Last-author position is more about
        supervision/funding than novelty-generating vantage; reported to
        distinguish supervisor-effect from lead-author-effect.
      - **T_p_weighted (sensitivity):** Rao's Q with pre-registered weights
        0.4 first, 0.4 last, 0.2 distributed uniformly over middle authors.
        Captures hierarchical-norm intuition without the binary
        first-vs-rest cut.
      - Single-author papers: T_p_full = T_p_first = T_p_last = 0;
        T_p_weighted = 0. Included as baseline.
    - **Subfield authorship-norm stratification.** Test IV regressions
      are fit (a) pooled within field with all four T_p operationalizations
      reported separately; (b) stratified by subfield authorship-norm
      regime (high-energy physics / condensed-matter / experimental CS /
      theoretical CS / other). Subfield assignment to regime is
      pre-registered before Test IV runs (deferred to early Stage 2 once
      author-list distributions per subfield are visible — candidate
      operationalizations: mean Spearman between author-list position and
      contribution-statement keywords on the post-2010 subset; manual
      subfield-by-subfield assignment from flagship-journal conventions;
      hybrid).
    - **Pre-registered interpretive grid for γ₁ (across the four
      operationalizations × stratification cells).** Prevents
      "harvest-the-most-interesting-story" post-hoc:
      - γ₁ > 0 across all four ops + all strata → strongest pro-diversity
        finding; Hofstra at team level, replicated.
      - γ₁ > 0 for T_p_first but ≈ 0 for T_p_full → outsider-vantage
        transfer works at the lead-author level but is diluted by team
        integration; weakened/scoped version of an
        actuator-homogenization story restricted to integration effects.
      - γ₁ > 0 in egalitarian/hierarchical strata but ≈ 0 in alphabetical
        (HEP) → team-product novelty mechanism operates only when team
        composition is intellectually load-bearing; mega-collaborations
        are structurally different.
      - γ₁ ≈ 0 across the board → diversity-novelty link is weak at
        team-product level regardless of operationalization; the
        dissertation-finding does not transfer. Substantively interesting
        null; publishable as such.
      - γ₁ < 0 for T_p_full but γ₁ > 0 for T_p_first → integration
        mechanisms operating on middle-author input dilute the
        lead-author's distinctive vantage; the version of an
        actuator-homogenization story that survives the C9 framing
        correction.
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
      year-FE + subfield-FE + ε_p, fit four times — once per T_p
      operationalization (T_p_full, T_p_first, T_p_last, T_p_weighted).
      Reported as a single Test IV table with four γ₁ columns. T_p_full
      and T_p_first are flagged co-primary; T_p_last and T_p_weighted are
      flagged sensitivity. Stratified-by-subfield-norm-regime fits
      reported alongside.
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
    - **Methods framing — "team diversity" is multi-headed.** In fields
      with heterogeneous authorship-norm regimes (CS and physics both
      qualify), "team diversity" is not a single construct. The four
      T_p operationalizations are not redundant measures of the same
      thing — they answer subtly different substantive questions
      (collective composition vs. lead-author vantage vs. supervisor
      composition vs. weight-by-canonical-position). The Methods section
      makes this explicit; the Discussion section interprets the
      γ₁-pattern across operationalizations using the pre-registered
      interpretive grid. This is a deliberate move away from a single
      canonical T_p toward surfacing the construct-validity ambiguity
      in the design rather than laundering it into a single number.
    - **Causal interpretation caveat (pre-baked):** cross-sectional
      correlations ≠ causal effects of team composition on novelty.
      Direction could reverse (novel work attracts diverse teams; self-
      selection on risk preference, etc.). Reported as descriptive
      association, not causal effect. No instrumental variable strategy
      attempted in this paper.
- **Test IV Persistence Extension (Stage 3 pre-registration, per
  Hofstra C11 + C10 walkthroughs).** Per-paper multi-window persistence
  analysis to disambiguate "discrimination" from "surface-novelty"
  readings of γ₁ patterns:
  - **Variables per paper p:** C_k(p) for k ∈ {3, 5, 10, 15};
    Persistence(p) = C_10(p) / C_3(p).
  - **Regression 1 (direct interaction):** log(1 + C_15(p)) = α + β_1·N_p
    + β_2·T_p + β_3·(N_p × T_p) + controls + year-FE + subfield-FE + ε.
    Test β_3 sign.
  - **Regression 2 (persistence ratio):** Persistence(p) = γ_0 + γ_1·N_p
    + γ_2·T_p + γ_3·(N_p × T_p) + controls + FE + ε. Test γ_3 sign.
  - **Multi-window co-reporting (per C10):** C_5, C_10, C_15 reported
    as co-equal columns in a single Test IV Persistence table — not
    primary-vs-sensitivity. C_10 flagged as the headline-comparability
    column (Hofstra-era literature comparison), but column placement
    does not signal weight.
  - **Heavy-tail trimming robustness (per SQ7):** full sample / top-1%-
    trimmed / top-5%-trimmed reported alongside.
  - **Mediation-style control sensitivity (per SQ14):** β_3 reported
    without novelty-structure controls, with distance-from-canonical-
    centroid control, with subfield FE, with full control set.
  - **Pre-registered interpretive grid for γ₁ pattern across windows:**
    - γ₁ stable across C_5/C_10/C_15 → finding robust to "uptake"
      operationalization.
    - γ₁ > 0 at C_5 but ≈ 0 at C_15 → diverse-team novelty has a "fast
      spike" pattern; doesn't durably persist. The surface-novelty
      reading.
    - γ₁ ≈ 0 at C_5 but > 0 at C_15 → diverse-team novelty is slow to
      be picked up but durable. The discrimination →
      eventual-rediscovery reading.
    - γ₁ stable in fast-uptake strata (HEP, ML-post-2012) but unstable
      in slow-uptake strata → finding generalizes only where uptake
      is fast.
    - γ₁ unstable across windows in all strata → multi-headed construct;
      persistence-class question itself ill-posed at this resolution.
      Substantively interesting null on measurement.
  - **Empirical uptake-half-life diagnostic per stratum (Phase 0.2 +
    early Stage 1).** Per (field × subfield × decade) cell, fit a
    citation-accumulation curve and report the year by which 50% of
    eventual C_15 has accumulated. Reported alongside the Test IV
    Persistence table as a transparency artifact: tells the reader
    which window is most apt for which cell. Does not change the
    pre-registered primary or column ordering — informs interpretation,
    not specification.
  - **Truncation by window:** C_5 truncates papers at 2019; C_10 at
    2014; C_15 at 2009. Pre-registered. Cells that fall outside a
    window's truncation reported as "out of window."
  - **Standard errors:** double-clustered by lead author and subfield.
  - **Left-censoring:** OpenAlex citation-indexing completeness improves
    over time. Add `coverage_rate(year)` as a control in Regression 1.
  - **Effort:** ~1–2 weeks Stage 3, uses existing OpenAlex data.
- **Item 11 — Production-capture aggregate decomposition (Stage 3
  pre-registration).** Per-demographic-group annual production and
  uptake decomposition to test whether observed aggregate divergence
  reflects differential capture by demographic groups:
  - **Variables per (group G, year Y):** N(G, Y) = mean new links per
    active group-G author in year Y (active = ≥1 paper in Y); C_k(G, Y)
    for k ∈ {5, 10, 15}.
  - **Multi-window co-reporting (per C10):** C_5, C_10, C_15 reported
    side-by-side, parallel to Test IV Persistence. Same interpretive
    grid for window-disagreement patterns applies.
  - **Per-active-year normalization as primary (per SQ12):** controls
    for differential pipeline attrition. Total production reported as
    secondary.
  - **Pipeline-survival sub-analysis (per SQ12):** demographic-specific
    survival rate to ≥10-year publishing window.
  - **Region-of-origin granularity (per SQ13):** ≥7 region groups, not
    pooled URM/non-URM.
- **Stage 3 U-M-S tertiary novelty: 5-year accumulation buffer (per
  Hofstra C10 walkthrough).** Reference-pair atypicality (Uzzi-Mukherjee-
  Stringer style) requires a "what's been seen before" baseline. Pre-
  register: U-M-S computation uses 1975+ papers only; 1970–1974 papers
  excluded from this specific operationalization (would otherwise look
  maximally novel by construction since their reference-pair pre-corpus
  is empty). 1970–1974 papers remain in Test IV primary (centroid
  distance, no accumulation buffer needed) and in Tests I–III aggregate
  divergence (data-quality tiers govern).
- **Methods-framing commitment: windows-as-estimand (per Hofstra C10
  walkthrough).** Add a Methods paragraph stating that uptake/
  accumulation windows are part of the estimand, not nuisance
  parameters. Different windows define different substantive questions
  ("early hot finding" vs. "durable contribution"). The multi-window
  grid is a deliberate move away from collapsing these into one
  number, parallel to the T_p multi-operationalization for team
  diversity. The empirical uptake-half-life diagnostic transparently
  anchors which window is apt for which stratum without giving the
  analyst post-hoc freedom to tune the primary. Approximately one
  paragraph.
- **Identity-uncertainty diagnostics and measurement-robustness
  appendix (per Hofstra C8 walkthrough, lit-review session
  2026-04-25).** Hofstra's matching-error compounding (Pathway C —
  joint demographic × identity error correlation) has a clean ws2
  analog: OpenAlex disambiguation accuracy is signal-correlated,
  varies by name-region, and improved over time. The most important
  derived threat is **spurious-trend contamination**: observed
  demographic-diversity rises in Tests I–III could partly reflect
  measurement-coverage improvements rather than true demographic-
  pluralization. Five commitments (one diagnostic, three
  robustness/decomposition, one Methods framing):
  - **(a) Per-era identity-confidence diagnostic.** Per-decade
    identity-confidence-pass rate broken out by region-of-origin,
    plotted over the full 1970–2024 window. Reported alongside Tests
    I–III as a sample-composition transparency artifact. Identity-
    confidence threshold operationalized as a derived proxy
    (candidates: name-frequency × institutional-ROR-completeness ×
    publication-density; finalized in early Stage 1 once OpenAlex
    sample is visible). May additionally break out by name-script
    (Latin vs. non-Latin); decided in Stage 1.
  - **(b) Pooled measurement-robustness appendix.** Single appendix
    section reporting each headline number under each measurement-
    uncertainty restriction. One row per restriction:
    - demographic-confidence-only restriction (drop low-NamSor);
    - identity-confidence-only restriction (drop low-disambiguation);
    - joint-confidence restriction (drop either);
    - pre-1990 exclusion;
    - heavy-tail trim (Test IV / Item 11 only);
    - mediation-control sensitivity (Test IV / Item 11 only).
    Six rows per headline number for Tests I–III; eight rows for
    Test IV / Item 11 (additional heavy-tail and mediation rows).
    Earns C8's place in the design without analytical-grid bloat —
    no full-grid stratification on the headline tables.
  - **(c) Staged decomposition trigger on Test IV.** Joint-confidence-
    restricted Test IV γ₁ reported in (b). If movement >0.02 SD vs.
    headline, decompose into demographic-confidence-only and
    identity-confidence-only restrictions and report which dominates.
    Pre-registered threshold prevents post-hoc decomposition fishing.
  - **(d) Methods-framing extension on identity uncertainty.** Extend
    the C4 weight-by-confidence Methods paragraph (in plan §4): "weight-
    by-confidence applied to demographic inference alone is necessary
    but not sufficient; identity uncertainty introduces a parallel
    signal-correlated error structure characterized via the per-era
    diagnostic (item a) and the restriction-row in the robustness
    appendix (item b). Headline numbers carry both uncertainty
    dimensions visibly." Approximately three sentences added to the
    existing C4 paragraph.
  - **(e) Pathway-C spurious-trend acknowledgment.** Methods/Discussion
    framing: observed demographic-diversity rises in Tests I–III could
    partly reflect measurement-coverage improvements rather than true
    demographic-pluralization. If the per-era diagnostic (item a)
    shows pass-rate rising faster for non-Western regions than
    Western, document the magnitude of measurement-trend contamination
    in the headline divergence claim. **The most important of the
    five — addresses a threat specific to ws2's 50-year design that
    is invisible at the per-paper or per-author level.** Approximately
    one paragraph.
  - **What we considered and rejected:**
    - Full-grid joint-confidence stratification on every headline.
      Would push results tables from ~50 cells to ~250 cells. Pooled-
      appendix approach (item b) does the work at much lower cost.
    - Pathway-B-specific commitment. Variance issue, not bias.
      Standard errors already absorb it.
    - Hofstra-style "research faculty" restriction analog. ws2
      doesn't have a matching-pipeline architecture that motivates
      this filter; the per-era diagnostic + appendix do equivalent
      work.
    - Inverse-pass-rate reweighting of headline divergence. Introduces
      its own assumptions; default to documenting contamination
      magnitude rather than correcting it. Revisit only if Stage 2
      results show measurement-coverage improvement could plausibly
      account for the headline divergence.
- **Cohort-mix interpretation handling (per Chu-Evans SQ8 walkthrough,
  lit-review session 2026-04-26).** If aggregate semantic diversity
  declines while demographic diversity rises (Tests I-III positive),
  one alternative interpretation is cohort-mix: old cohorts trained
  pre-1990 produced canon-eccentric work; new cohorts produce canon-
  anchored work; aggregate decline reflects the cohort mix shifting
  rather than all cohorts adapting. Chu-Evans 2021 (SI Tables S2/S3)
  directly addresses the analogous question for citation behavior
  and finds period effects dominate cohort effects by 16–30× within-
  author, suggesting within-field cohort imprinting is weak. Their
  evidence is for citation behavior, not semantic-output of papers,
  so the inheritance bounds the cohort-mix interpretation toward
  unlikely a priori but doesn't airtight rule it out. ws2 commits
  to a two-part response (with a back-pocket option):
  - **(A) Discussion-section paragraph (item under §9 framing
    commitments).** Acknowledge cohort-mix as an alternative
    interpretation; cite Chu-Evans's period-dominance finding as
    upstream evidence weakening it; note that the inheritance is
    indirect (their DV is citation behavior, ours is semantic-output);
    point to (B) as ws2-specific evidence. Approximately one
    paragraph.
  - **(B) Stage 3 simplified cohort decomposition.** For each paper,
    identify lead author's first-publication year as cohort proxy.
    Bin papers by (publication year × lead-author cohort) cells;
    compute mean semantic diversity per cell; plot per-cohort
    trajectories. Interpretation grid:
    - All cohorts' trajectories slope similarly → period effect
      operative; cohort-mix not driving aggregate finding.
    - Divergent cohort-trajectories with old-cohort high and
      new-cohort low at same calendar year → cohort effect operative;
      cohort-mix could be driving aggregate finding.
    - Mixed pattern → ambiguous; trigger Option C.
    Methodologically thin (lead-author-only cohort proxy; rough
    cohort bins; no author FE; no within-author longitudinal claim),
    but answers the Discussion question with ws2 data rather than
    inheriting solely from Chu-Evans. Cost: ~1 week Stage 3 effort,
    existing OpenAlex data, no new API calls.
  - **(C) Back-pocket: full author-FE within-author longitudinal
    analysis on semantic output.** Define per-author semantic-
    diversity-output construct (candidates: variance of an author's
    papers' embeddings; distance from author-specific centroid; mean
    pairwise cosine distance among author's papers). Take authors
    who published in both early-era (1970–1990) and late-era
    (2000–2024); fit author-FE regressions with current canonical
    concentration as the period predictor. Methodologically heavy
    — author disambiguation at scale (compounds C8 issue), long-
    career-author selection bias, novel construct requiring its own
    validation pipeline. Cost: 2–3 weeks Stage 3 methodology work.
    **Deferred unless Option B's results are ambiguous (mixed
    pattern in the interpretation grid).**
- **Decoupled-subfield robustness check (per Chu-Evans SQ6
  walkthrough, lit-review session 2026-04-26).** Chu-Evans 2021
  Fig. S1 demonstrates an identification-defense move: when year
  and field size are weakly correlated within a subject (e.g.,
  Biochemistry r=0.32, Applied Physics r=0.58), citation-dynamics-
  by-field-size patterns persist — ruling out "size is just time in
  disguise." A residual concern remains: year controls absorb
  common-across-fields time effects but not field-specific time
  effects. ws2 inherits an analogous threat. Observed demographic-
  vs-semantic divergence (Tests I–III positive) could reflect two
  unrelated time trends — demographic-pluralization-over-time +
  canon-ossification-with-field-size — rather than a real
  decoupling. The decoupled-subfield robustness check directly
  addresses this:
  - **Per-subfield year–log-size correlation diagnostic.** For each
    subfield s in the post-1990 analytical window, compute within-
    subfield Pearson correlation between calendar year and log
    subfield size over 1970–2024. Report distribution of correlations
    across subfields.
  - **Pre-registered decoupled-subset thresholds:** r < 0.5,
    r < 0.7, r < 0.9. Multi-threshold reporting prevents post-hoc
    threshold tuning. Headline replication on each threshold's
    decoupled subset.
  - **Replicated tests:** Tests I–III aggregate divergence; subfield
    mechanism test (CanonConc_s on DivMag_s); Test IV (γ₁ at headline
    operationalization). All three rerun on each decoupled subset.
  - **Pre-registered interpretive grid:**
    - Divergence pattern stable across full sample, r<0.9, r<0.7,
      r<0.5 subsets → robust to size-time confound. Strongest version
      of headline.
    - Divergence weakens monotonically as decoupling threshold
      tightens → time confound contributes to full-sample finding;
      contamination magnitude estimable from threshold-by-threshold
      attenuation.
    - Divergence absent or reverses in r<0.5 subset → strong evidence
      full-sample finding is time-confounded; substantively
      interesting null on the divergence claim.
    - Decoupled subset count too small (n<5 per field at r<0.5) →
      check cannot run; document inheritance of Chu-Evans's residual
      field-specific-time-effect concern in Methods.
  - **Cost.** Computationally cheap — rerun existing analyses on
    subsets. ~1–2 days Stage 2 effort. No new data or API calls.
- **Classification-substrate acknowledgment (per Chu-Evans C3 +
  SQ10 walkthroughs, lit-review sessions 2026-04-26).** ws2 uses
  Chu-Evans 2021's Spearman top-N methodology for canonical
  concentration but operates on a structurally different classification
  substrate (OpenAlex concept tags + arXiv hybrid; ~10–50 subfields
  per field) than Chu-Evans (WoS subjects; n=241). Three implications:
  (i) we cannot directly cite their coefficient values as targets to
  replicate — Spearman magnitudes are tied to substrate; (ii) any
  qualitative-pattern difference between our findings and theirs
  could reflect real dynamics, real subfield-vs-subject scale
  differences, or substrate artifacts — not separable without
  parallel analysis on both substrates (which ws2 will not run);
  (iii) ws2 carries a classifier-drift identification burden
  (handled via plan §3) that Chu-Evans's stable WoS classification
  doesn't face. Commitment: **Methods-paragraph acknowledgment,
  approximately seven sentences** stating substrate difference,
  disclaiming direct coefficient comparison, treating Chu-Evans as
  methodological precedent rather than replication target.
  Specifically, the paragraph also covers two structural-classification
  caveats surfaced in SQ10:
  - **Journal-level vs. content-level classification.** WoS subjects
    are journal-inherited (a paper's subject depends on where it
    publishes); OpenAlex concepts are paper-level (classification
    depends on the paper's content regardless of venue). When we
    apply Chu-Evans methodology to OpenAlex data, we're potentially
    measuring content-canon ossification rather than journal-canon
    ossification — these could behave differently if journal-
    hierarchy entrenchment is part of the underlying mechanism.
  - **Temporal projection of modern concepts onto older papers.**
    OpenAlex's concept hierarchy is itself a 2020s artifact;
    applying it to 1975 papers projects modern conceptual structure
    retrospectively. Some 1975 papers may be classified into
    concepts that didn't exist at publication time. Plan §3
    classifier drift mitigation handles classifier-output stability;
    this is the orthogonal concern about whether the conceptual
    frame itself is era-appropriate. Stage 2 decision: whether to
    bound the analysis to concepts stable across 1970–2024
    (subset-of-stable-concepts approach) or accept temporal
    projection with explicit acknowledgment.
  Add to §9 Methods framing batch. Cross-substrate Stage 3 robustness
  (replicate on WoS-OpenAlex overlap subset) **deferred as
  back-pocket** — requires WoS data access not currently in ws2
  plan; trigger only if reviewers specifically request cross-
  substrate replication.
- **Subfield-canon overlap diagnostic (per Chu-Evans SQ10
  walkthrough, 2026-04-26).** OpenAlex assigns multiple concepts per
  paper (5–15 with confidence scores); ws2 uses highest-confidence
  primary subfield assignment but a paper can appear in multiple
  subfields' top-50 most-cited lists if it's in multiple subfields'
  scope. This induces structural correlation across subfields that
  Chu-Evans don't face (WoS subjects rarely overlap papers).
  Stage 3 diagnostic: measure subfield-canon overlap rate (fraction
  of subfield-pair top-50 lists that share papers). If overlap < 10%,
  issue is minor; report and move on. If 10–30%, acknowledge in
  Methods. If > 30%, adjust standard errors on Spearman correlations
  across subfields to account for non-independence. ~half-day Stage
  3 effort.
- **Selective Chu-Evans citation framing (per SQ9 walkthrough,
  2026-04-26).** Chu-Evans 2021 has six predictions across three
  dimensions; predictions 1–4 (durable dominance + entrepreneurial
  futility) rest on Spearman + Gini + p + τ, none CD-index-dependent.
  Predictions 5–6 (reduced disruption) rest on Wu-Wang-Evans 2019's
  D measure, which is in the Funk-Owen-Smith CD-index family.
  Petersen-Holst critiques apply directly. Critically, the **bias
  direction is in the same direction as Chu-Evans's finding** —
  citation-inflation and dataset-artifact biases mechanically
  produce the appearance of declining disruption with field size
  even if no real decline existed. Commitment: **selective citation**
  in ws2 Methods/Discussion. Cite Chu-Evans's predictions 1–4
  generally as "Chu-Evans 2021 documented durable dominance and
  entrepreneurial futility in large fields"; explicitly bracket
  predictions 5–6 as "their disruption findings (predictions 5–6)
  inherit CD-index measurement issues critiqued by
  Petersen-Arroyave-Pammolli 2024 and Holst et al. 2024 with
  bias-direction aligned to the finding; we do not lean on these
  for ws2's argument." Approximately three sentences in Methods,
  one sentence in Discussion. Add to §9 Methods framing batch.
- **Subfield mechanism test nonlinearity check (per Chu-Evans
  bin-and-regress critique, lit-review session 2026-04-26).** The
  subfield mechanism regression (DivMag_s = γ_0 + γ_1·CanonConc_s +
  Σ γ_k·Control_k + ε_s) assumes the CanonConc → DivMag relationship
  is linear. If the real relationship has regime structure (e.g.,
  divergence flat for low CanonConc subfields, sharply rising above
  a threshold), a linear fit smears the regime — underestimates the
  effect at high CanonConc, overestimates at low CanonConc, reports
  a "moderate γ_1" that misses the structure. Commitment:
  - **Quadratic term:** add γ_2·CanonConc_s² to the regression
    spec. If γ_2 is significant at α=0.05, report curvature
    coefficient and revised marginal-effect curve; otherwise default
    to linear-only headline.
  - **LOWESS visualization:** plot DivMag_s vs. CanonConc_s as
    scatterplot with LOWESS trendline; visually overlay the linear
    and quadratic fits. Flag any visible non-monotonic behavior.
  - **Cost:** ~half-day Stage 2 effort, no new data or API calls.
  - **Considered and rejected:** spline regression with
    cross-validation knot placement. More principled but introduces
    complexity not used elsewhere in ws2; quadratic + LOWESS captures
    the regime-structure concern proportionately.
- **Multi-Δ Spearman canonical-concentration co-reporting (per
  Chu-Evans C2 / SQ7 walkthrough, lit-review session 2026-04-26).**
  Supersedes the original "Δ=5 single primary" specification in
  the canonical-metric pre-registration block. Rationale: intrinsic
  ossification timescale varies across (field × era) regimes (ML
  post-2012 ~1–2 years; pure math 10+ years; 1970s biochem slow;
  HEP post-Higgs fast). A single committed Δ systematically
  mismeasures ossification in regimes whose intrinsic timescale
  doesn't match Δ. Blind multi-Δ trial = lag-selection p-hacking.
  Resolution combines pre-registration of multiple Δ values with a
  pre-registered interpretive grid (parallel to Test IV persistence
  multi-window pattern from Hofstra C10).
  - **Pre-registered Δ ∈ {1, 5, 10} as co-primary.** Reported as
    co-equal columns in the canonical-concentration table, not
    primary-vs-sensitivity. Δ=1 flagged as **Chu-Evans-comparability
    anchor** (their published Spearman uses Δ=1).
  - **Reuse per-stratum empirical uptake-half-life diagnostic**
    (already committed per Hofstra C10): per (field × subfield ×
    decade) cell, year by which 50% of eventual C_15 has accumulated.
    Tells reader which Δ is most apt for which cell; informs
    interpretation; does not change the pre-registered primary.
  - **Pre-registered interpretive grid for Δ-disagreement patterns:**
    - All three Δ stable → ossification detection robust to
      timescale; strongest version of headline.
    - Δ=1 stable, Δ=5 not → high-frequency stability that doesn't
      persist to medium-window; likely measurement-noise-driven;
      weaker claim.
    - Δ=1 unstable, Δ=5 stable → fast individual-ranking churn
      within stable medium-window canon set. Canon-as-set stable;
      specific rankings churn. Substantively interesting.
    - Δ=5 stable, Δ=10 unstable → era-bounded ossification;
      possibly real regime change between eras.
    - Pattern varies across (field × era) cells consistent with
      empirical uptake-half-life diagnostic → different timescales
      operative in different regimes.
  - **Considered and rejected.**
    - *Cumulative Spearman as primary.* Structurally different
      estimand (durable-membership vs. ranking-stability). Defer
      to Stage 3 if a third operationalization is needed.
    - *Adaptive Δ per (field × era) cell tuned by uptake-half-life.*
      Even with pre-registered tuning procedure, introduces
      researcher-degree-of-freedom complexity. Multi-Δ co-reporting
      is simpler and more defensible.
  - **Cost.** Computationally trivial (three correlations per cell
    instead of one). Methodologically minor (interpretive grid
    parallels existing Test IV persistence grid).
  - **Note on existing pre-registration block.** The "Canonical
    (primary)" line elsewhere in this section originally specified
    "Δ=5 years"; this commitment supersedes it. The "Canonical
    (robustness)" line's "Δ ∈ {3, 10}" specification is folded into
    the new co-primary set (Δ=1 added; Δ=3 dropped in favor of
    Δ=10 as the longer-window robustness; Δ=5 retained as medium-
    window default; Δ=1 added as Chu-Evans-comparability anchor).
- **OpenAlex coverage diagnostic + citation-completeness sensitivity
  (per Park-Leahey-Funk C2(b) walkthrough, lit-review session
  2026-04-26).** Holst et al. 2024's WoS reference-truncation
  threat doesn't transfer directly to ws2 (we use OpenAlex), but a
  parallel threat exists at a different layer: OpenAlex has variable
  indexing completeness for older papers (especially pre-1990),
  affecting citation counts → potentially distorting our canonical-
  concentration metrics. The bias direction is more favorable than
  PLF's case: for Spearman top-50 (rank-invariant to citation
  magnitudes), undercounting is either attenuating or non-directional;
  for citation Gini, undercounting in older eras could amplify our
  hypothesized trend. Multi-metric reporting (Spearman + Gini) gives
  early warning if Gini-only shows the effect. Three small
  extensions of existing commitments:
  - **(a) Per-era OpenAlex coverage diagnostic.** Parallel to Hofstra
    C8 per-era identity-confidence diagnostic. Per (field × decade),
    report OpenAlex coverage rate — fraction of papers with complete
    reference lists (Crossref-sourced); fraction of papers indexed
    relative to expected cross-database baseline. Sample-composition
    transparency artifact alongside Tests I-III.
  - **(b) Citation-completeness sensitivity row** in the existing
    pooled measurement-robustness appendix (from Hofstra C8
    commitment item (b)). Recompute canonical-concentration metrics
    (Spearman top-50, citation Gini) under high-completeness
    restriction (papers with reference completeness ≥ pre-registered
    threshold; possibly Crossref-sourced subset). One additional
    row in that appendix.
  - **(c) Methods-section sentence** extending the C3/SQ10 substrate-
    acknowledgment paragraph. Acknowledges OpenAlex-coverage analog
    of the Holst threat; distinguishes the mechanism (indexing-
    completeness for ws2 vs. reference-truncation for WoS); points
    to (a) diagnostic and (b) robustness row.
  - **Cost.** All three are computationally trivial (uses existing
    OpenAlex coverage metadata; reruns existing analyses on subset;
    one paragraph addition). No new data or pipeline.
  - **Why diagnostic-and-document rather than correct-and-restrict.**
    Bias direction analysis shows the threat is less severe for ws2
    than for PLF. We document the threat with a diagnostic and a
    sensitivity row; we don't restrict the primary analysis based
    on coverage thresholds.
- **PLF positioning (c-prime): inflation-immune evidence framing
  (per Park-Leahey-Funk C5 walkthrough, lit-review session
  2026-04-26).** Three options considered for citing PLF in ws2's
  Methods/Discussion: (a) don't cite as upstream support — orthogonal
  positioning; (b) cite with critique-chain caveat — methodologically-
  independent positioning; (c) engage aggressively as cleaner
  evidence. **Decision: (c-prime), a refined version of (c) that
  preserves ambition while calibrating claims.** Frame ws2 as
  contributing inflation-immune evidence to the debate rather than
  "resolving" it; explicitly acknowledge the construct gap (semantic
  plurality ≠ disruption); pre-commit to symmetric framings. Four
  concrete commitments:
  - **(1) Methods-section three-layer defense of inflation-immunity
    (per PAP 2025 C4 + Holst SQ6 walkthroughs, lit-review sessions
    2026-04-26 / 2026-04-27).** Structure as three short paragraphs
    explicitly mirroring the post-PLF critique chain pattern. The
    conjunction provides triple-convergence evidence; each layer
    addresses limitations of the others.

    *Layer 1 (theoretical/analytical):* organized via PAP 2025's
    three-conditions framework. PAP 2025's Discussion lays out
    three conditions any cross-temporal citation metric should
    satisfy: (i) stationary distribution over time; (ii) most
    weakly sensitive to secular growth; (iii) captures consensus
    of broader scientific community, not entirely dependent on
    author choices. CD-index fails all three structurally; ws2's
    metrics pass all three:
    - Spearman top-N satisfies (i) bounded + rank-stable;
      (ii) rank-invariant; (iii) determined by community citation
      patterns.
    - Citation Gini satisfies (i) bounded in [0, 1]; (ii) tested
      by detrended diagnostic; (iii) based on community-wide
      citation distribution.
    - Cluster entropy / effective dim / mean pairwise distance
      satisfy all three via embedding-space orthogonality to
      citation network structure (with cluster-fit temporal
      stratification per desiderata §11 and drift-mitigation
      ladder ensuring (i)).
    Two ws2-specific extensions: (iv) robustness to author-
    disambiguation errors (Hofstra C8 identity-confidence
    diagnostic); (v) robustness to missing references in early-era
    data (drift-mitigation ladder + pre-1990 dummy diagnostic).
    Cite PAP 2025 as framework source; note ws2 satisfies the
    conjunction.

    *Layer 2 (empirical diagnostic):* document that our metrics
    empirically pass inflation-vulnerability diagnostics. Reference
    PAP-style observational diagnostics (stationarity test,
    detrended correlation-with-r(t)). Pre-registered interpretive
    thresholds. If diagnostics surface concerning patterns, fall
    back to back-pocket synthetic-network stress-test.

    *Layer 3 (controlled analysis):* document that ws2's findings
    persist under proper-control regression specifications. Test
    II + Test IV regression refinements (c_p control, quadratic
    terms, year-FE, subfield-FE) per PAP 2025 lessons. Effect-size
    threshold calibrated to PAP 2025's 0.10σ noise floor. Both
    with-c_p and without-c_p specifications pre-registered for
    bad-control transparency.

    **Why three layers matters methodologically.** The post-PLF
    critique chain illustrates that single-layer evidence is
    defensible-against; conjunction across theoretical + empirical-
    diagnostic + controlled-analysis is much harder to defend
    against. Each layer addresses the limitations of the others:
    Layer 1 establishes when metric is valid (theoretical);
    Layer 2 validates theory in actual conditions (empirical);
    Layer 3 removes alternative explanations (controlled). Same
    pattern as PAP 2024 + Holst + PAP 2025 critique-chain
    structure. This is methodologically stronger than purely
    defensive structural arguments because it explicitly mirrors
    the most successful critique-chain pattern in the post-PLF
    literature.

    **Length:** ~3 short paragraphs (~5-7 sentences each) instead
    of single ~7-9 sentence paragraph. Same content, better
    structure that makes the conjunction visible to reviewers.
  - **(2) Discussion-section paragraph engaging PLF.** ~5 sentences.
    Cite PLF's substantive claim, cite Petersen-Arroyave-Pammolli
    2024 + Holst et al. 2024 critique chain, position ws2's
    semantic-plurality measurement as inflation-immune evidence on
    the substantively-related question.
  - **(3) Pre-registered interpretive grid for ws2 vs. PLF debate.**
    Three cells. Language tightened to be about *empirical alignment
    only*, not endorsement of any causal mechanism (per C8
    walkthrough):
    - Semantic plurality *declines* → empirically aligned with PLF's
      observed direction. Pattern is consistent with PLF's documented
      decline using a methodology immune to citation-inflation;
      reduces (without eliminating) the Petersen-Holst measurement-
      artifact reading.
    - Semantic plurality *stable* → empirical contradiction of PLF's
      observed direction. Pattern is consistent with the Petersen-
      Holst reading that PLF's observed decline is substantially a
      measurement artifact.
    - Semantic plurality *rises* → strong empirical contradiction of
      PLF's observed direction. Pattern is consistent with PLF's
      observed decline being mostly a measurement artifact.
    Note language: "empirically aligned/contradicts," "consistent
    with PLF's observed direction" — not "supports/contradicts PLF's
    narrowing-mechanism causal story." The grid documents
    observational alignment; it does not endorse or refute causal
    claims.
  - **(4) Calibration paragraph (load-bearing for c-prime framing).**
    ~3 sentences explicitly stating that semantic plurality is
    *adjacent to* but *not identical to* disruption. PLF measures
    citation-pattern structure; we measure content-space structure.
    Related but distinct constructs. We do *not* claim to resolve
    PLF — we contribute methodologically-cleaner evidence on the
    substantively-related question.
  - **Total Discussion + Methods real estate:** ~1.5 paragraphs
    Methods + ~1.5 paragraphs Discussion. Manageable; not free.
  - **What we explicitly do not do under (c-prime).** Don't claim
    to resolve PLF/Petersen-Holst debate; don't position our metric
    as replacement for CD-index in general scientometrics; don't
    engage PLF beyond inflation-immune-evidence claim (no stand on
    Shapley-Owen findings, conservation-of-disruption, verb-
    classification).
  - **Risks accepted.** Cleanness claim is contestable (we have our
    own issues: embedding stability, cluster-fit, subfield drift,
    coverage); scope creep risk (mitigated by calibration paragraph);
    Discussion real estate cost; positioning as participant in the
    debate.
  - **(5) Causal-pathway non-endorsement (per PLF C8 walkthrough,
    lit-review session 2026-04-26).** All PLF citations under
    (c-prime) are descriptive/measurement-only. ws2 does *not*
    endorse PLF's narrowing-mechanism causal story (Fig. 6 as
    collective evidence for "scientists narrowing prior-knowledge
    use → declining disruption"). Operational rules:
    - *Cite Fig. 6a/6d* as alternative operationalization of within-
      year citation concentration aligned with our **Gini secondary
      metric** (specifically, not Spearman-top-N primary).
    - *Do not cite* Fig. 6b/6e (self-citation) or Fig. 6c/6f (age
      of cited work). These only land as relevant evidence if we're
      endorsing the narrowing-mechanism causal story; we're not.
    - *Use neutral language:* "alternative operationalization,"
      "consistent with," "complements." Avoid "narrowing,"
      "scientists are increasingly relying on...," "supports
      narrowing-mechanism," etc.
    - *Acknowledge in C2(b) Methods-paragraph extension* that
      Fig. 6a/6d still inherits the Holst dataset-artifact concern
      (less severe than CD-index inflation; not zero).
    - *Connection to broader principle:* matches our Chu-Evans
      mechanism-trim. Meta-commitment running across all upstream-
      paper engagements: cite empirical observations, not causal-
      mechanism narratives. This preserves ws2's observational
      scope per program desiderata and per the Test IV "Causal
      interpretation caveat (pre-baked)" stance.
- **Program-aware observational-scope framing (meta-commitment, per
  PLF C8 + program-structure walkthrough, lit-review session
  2026-04-26).** Generalizes the Chu-Evans mechanism-trim and PLF
  C8 causal-pathway non-endorsement into a paper-wide framing
  commitment. ws2 is the empirical/observational layer of a
  3-whitespace research program (ws2 = empirical decomposition;
  ws3 = theoretical reconciliation, future; ws1 = agent simulation,
  future). Causal claims live in ws3 (formal model) and ws1
  (counterfactual simulation), not in ws2. ws2 documents covariation
  in time series; we do not claim causal direction or mechanism.
  Three operational moves to make this visible in the eventual ws2
  paper:
  - **(1) Methods-section observational-scope statement.** ~3
    sentences. ws2 documents covariation in three time series at
    the field-aggregate level (demographic plurality, semantic
    plurality, canonical concentration); we do not claim causal
    direction or mechanism; mechanistic explanation is reserved
    for the follow-up theoretical (ws3) and simulation (ws1)
    studies in our research program. Pin down once; refer back as
    needed.
  - **(2) Discussion-section: route mechanism speculation to
    follow-up work.** When discussing implications, frame mechanism
    speculation as questions for ws3/ws1, not answers from ws2.
    Concrete language pattern: "if our finding reflects actuator-
    homogenization, the next step is to test this counterfactually
    (ws1) or formalize it (ws3)" — not "our finding establishes
    that actuator-homogenization is operative." Apply consistently
    across Discussion paragraphs that gesture toward mechanism.
  - **(3) Limitations section: scope as deliberate design choice.**
    Explicitly state the observational-scope limitation, framed as
    deliberate epistemic-layer separation rather than methodological
    weakness. Pre-empts reviewers who might frame it as a flaw.
    Specifically: "ws2's observational scope is a design choice,
    not a limitation of available data. Causal claims about the
    mechanisms underlying any observed divergence require the
    formal modeling and counterfactual simulation that constitute
    the follow-up whitespaces of this research program."
  - **Connection to existing commitments.** This generalizes the
    Test IV "causal interpretation caveat (pre-baked)" stance to
    apply paper-wide; matches the Chu-Evans mechanism-trim (we use
    Chu-Evans methodologically + empirically, not mechanistically);
    matches the PLF C8 causal-pathway non-endorsement (we cite PLF
    descriptively, not as endorsement of narrowing-mechanism story).
    The meta-principle: *ws2 cites empirical observations from
    upstream papers and presents its own findings as covariation
    documentation; mechanism specification is reserved for ws3
    and ws1.*
  - **Why this scope trimming is appropriate.** Two-fold: (a)
    program-structure coherence — keeping ws2 observational
    preserves clean epistemic-layer separation across the
    3-whitespace program; if ws2 made causal claims, it would step
    on ws3 / ws1 territory and weaken the program's overall
    coherence; (b) cleaner peer-review path — at the Nature/PNAS
    level (the natural peer set), reviewers are alert to
    overclaiming and prefer descriptive findings with clear
    interpretation boundaries; strict observational scope preempts
    "what's your identification strategy?" pushback and signals
    methodological maturity.
  - **Cost: minimal Discussion-section real estate** (~3-5
    sentences total across Methods + Discussion + Limitations).
    The framing doesn't reduce ambition — the decoupling finding
    is bold enough on its own without causal-mechanism additions.
- **PAP-style inflation diagnostics on canonical-concentration
  metrics (per Petersen-Arroyave-Pammolli 2024 / lit-review session
  2026-04-26).** PAP 2024 offers three observational-data diagnostics
  for citation-inflation vulnerability that don't require synthetic-
  network stress-testing. Complementary to the C2(b) OpenAlex
  coverage commitment (which probes dataset-artifact threats); these
  diagnostics directly probe the citation-inflation threat as a
  separate vulnerability mechanism.
  - **(a) Algebraic decomposition statement (Methods, ~one
    paragraph).** Explicitly state that ws2's canonical-concentration
    metrics pass the PAP algebraic test:
    - Spearman top-N is rank-invariant — has no extensive R_k-like
      denominator term that grows with citation network density.
    - Citation Gini is bounded in [0, 1] — no extensive growth term.
    - Cluster entropy / effective dimensionality / mean pairwise
      distance operate on embedding space, orthogonal to citation
      network density.
    PAP's deductive test (CD = CD^nok / (1 + R_k) form) does not
    apply to any ws2 metric. Pass by construction; no empirical
    test needed for (a).
  - **(b) Stationarity diagnostic.** Compute per-year distribution
    of Spearman top-50 and citation Gini over the 1970–2024
    primary analysis window (Tests I-III span per Phase 0.1 §13).
    Test for time-stationarity of distribution mean and variance.
    Per PAP Fisher-Tippett observation: under inflation-immune
    regimes, metric distributions become time-stationary;
    non-stationarity tracking r(t) growth is the smoking gun for
    inflation. Report alongside headline metrics. Note: pre-1990
    era is included by design per §13 non-negotiable retention
    policy; if stationarity test reveals pre-1990 era shows
    systematic distribution-shape deviation, that's diagnostic
    information for the pre-1990 dummy-variable robustness check.
  - **(c) Detrended correlation-with-r(t) diagnostic (per PAP SQ3
    walkthrough, lit-review session 2026-04-26).** Compute
    *detrended* Pearson correlation between (i) CanonConc time
    series (Spearman top-50 and citation Gini, separately) and
    (ii) per-year mean r(t) (reference list length) time series.
    Should be ~0 if our metrics are inflation-immune as we argue
    analytically.
    - **Detrending operationalization:** first-difference both
      series — Δr(t) = r(t) − r(t−1) and ΔCanonConc(t) =
      CanonConc(t) − CanonConc(t−1) — and correlate differences.
      Robustness check: trend-residual correlation (fit LOWESS to
      each, take residuals, correlate). Both should give similar
      results.
    - **Why detrending is necessary:** raw Pearson correlation
      between two smoothly monotonic time series is ≈ 0.9+ even
      for causally unrelated variables (shared-trend artifact).
      Both r(t) and CanonConc(t) are smoothly monotonic over the
      1970–2024 primary analysis window (r(t) exponential at
      g_r ≈ 0.018; CanonConc plausibly monotonic if hypothesized
      trend is real). Raw correlation would trigger stress-test
      for everything, providing no information. Detrending isolates
      the year-to-year variation not explained by smooth trends —
      the substantive signal of interest.
    - **Note on PAP's R² = 0.96:** PAP report this as raw R²
      between r(t) and R_k(t), not detrended. The number is
      partly artifactual due to shared-trend correlation; the
      detrended R² would be lower. PAP's argument doesn't rest on
      R² alone (they triangulate with deduction and synthetic
      networks), but their headline number is overstated.
  - **Pre-registered interpretive thresholds for (c) — applied to
    detrended correlation:**
    - |corr| < 0.3 → metric is inflation-robust as argued; no
      action.
    - 0.3 ≤ |corr| < 0.7 → modest correlation in detrended
      residuals; document and investigate whether mediated by
      other variables.
    - |corr| ≥ 0.7 → strong correlation in detrended residuals;
      metric may have hidden inflation vulnerability we haven't
      identified analytically; trigger Stage 3 synthetic-network
      stress-test (back-pocket from PAP review).
  - **Cost.** Computationally trivial. Same data, simple
    aggregations and correlations. ~half-day Stage 2 effort.
  - **Why direct observational diagnostics complement the synthetic-
    network stress-test.** The diagnostics test our metrics on our
    actual data (direct evidence); the synthetic networks would
    test our metrics under known-synthetic CI conditions (indirect
    inference). Both have value, but observational diagnostics are
    higher-priority and lower-cost. Synthetic-network stress-test
    remains as Stage 3 back-pocket; trigger if (b) or (c)
    diagnostics surface concerning patterns.
- **Test II gap regression specification refinement (per PAP 2025
  walkthrough, lit-review session 2026-04-26).** PAP 2025's lesson
  generalizes: when team size is a regressor in any scientometric
  analysis, also include reference list length and citation impact
  as controls because all three correlate strongly over time.
  Without these, β_t (the gap-trend coefficient — our headline
  finding) is potentially contaminated by omitted-variable bias.
  Specific refinements to existing Test II controls list:
  - **Add aggregate c(t) control** — median citations per paper at
    5 years post-publication, aggregated to year-level. Currently
    NOT in our spec; PAP 2025 lesson implies it should be.
  - **Add quadratic on log(avg team size) with fallback rule (per
    PAP 2025 C5 walkthrough, 2026-04-26)** — captures non-monotonic
    team-size effects PAP 2025 documented (negative for small
    teams, positive for k_p ≥ 8). Currently linear-only. **Fallback
    rule:** if quadratic coefficient is not significant at p<0.05,
    default to linear specification for headline; if significant,
    report non-linear version. Pre-registered to prevent post-hoc
    specification decision. Why fallback matters: Test II has
    ~110 field-year observations (1970–2024 × 2 fields) with ~10
    covariates; adding quadratic coefficients reduces DOF from
    ~100 to ~98-99 (negligible power impact). The fallback rule
    is *methodological discipline* (no post-hoc choice between
    linear and quadratic specifications), not a power-driven
    necessity. For Test IV (paper-level, millions of observations)
    quadratic runs by default; no fallback needed.
  - **Add team-size × year interaction** — controls for team size
    growing over time, parallel to PAP 2025's b_{kxt} term.
  - **Switch year-trend (β_t·Y) to year fixed effects** — more
    flexible specification, and we already have year-FE elsewhere
    in the plan.
  - **Already have:** median references per paper (aggregate r(t)
    proxy); avg team size (linear); other secular-growth covariates.
  - **Cost:** computationally trivial. Same data, refined regression
    specification.
  - **Bias direction without these:** unclear (could push β_t up
    or down depending on c(t) and quadratic-team-size dynamics).
    The risk is real even if direction is uncertain.
- **Test IV regression specification refinement (per PAP 2025
  walkthrough, lit-review session 2026-04-26).** Test IV is a
  paper-level regression like PAP 2025's, so PAP 2025's lessons
  transfer directly. Specific refinements:
  - **Add c_p (citation impact of paper p) as paper-level control,
    with bad-control handling per SQ8 walkthrough.** Paper's own
    citation count at 5 years post-publication. Currently NOT in
    our spec. Critical because c_p correlates with both T_p (team
    diversity may correlate with citation impact via international
    collaborations) and N_p (highly-cited papers may have
    systematically more diverse or more concentrated reference
    lists). Without c_p control, γ₁ absorbs whatever c_p is doing —
    classic omitted-variable bias.
    - **Bad-control problem:** adding c_p as a control assumes
      citation impact is a *confounder*, not a *mediator*. If
      diverse teams *produce* more impactful papers, c_p is partly
      a *mediator* of T_p → outcome. Controlling for c_p would
      absorb part of the team-diversity effect.
    - **Resolution: pre-register both specifications.** Spec A
      (without c_p) captures total team-diversity → novelty effect
      including via citation-impact mediation if any. Spec B (with
      c_p) captures direct effect excluding mediation via c_p.
    - **Pre-registered interpretive grid:**
      - γ_1 similar in A and B → c_p isn't a mediator; either
        spec is fine; B is more conservative.
      - γ_1 substantially smaller in B than A → c_p is a mediator
        of T_p → novelty; A captures total effect, B captures
        direct effect; report both with substantive interpretation.
      - γ_1 changes sign between A and B → c_p has complex
        relationship with T_p and outcome; substantive
        investigation needed before headline claim.
  - **Add log(number of authors)² — quadratic on team size** —
    captures non-monotonic team-size effects per PAP 2025.
  - **Add log(number of references)² — quadratic on reference list
    length** — captures non-linear citation-inflation effects.
  - **Already have:** number of authors (linear), number of
    references (linear), mean career stage, mean prestige, log
    paper age, field dummy, year-FE, subfield-FE, double-clustered
    SEs.
  - **Cost:** computationally trivial. Three additional regression
    coefficients (c_p, log(authors)², log(refs)²).
  - **Why this isn't load-bearing for our central γ₁ estimate** but
    is load-bearing for *defensible* γ₁ estimate: the omitted-
    variable bias from missing c_p could be small in magnitude (we
    have year-FE and subfield-FE absorbing many confounds), but
    PAP 2025's WWE 2019 critique demonstrates this kind of bias can
    flip signs of small effects.
- **Effect-size threshold calibration review (per PAP 2025
  walkthrough, lit-review session 2026-04-26).** PAP 2025 reports
  residual effect sizes of **0.06σ (time)** and **0.09σ (team
  size)** as "noise level" in their post-controls regressions. The
  general lesson: in scientometric regressions involving network-
  density-correlated covariates, anything below ~0.1σ is at the
  noise floor.
  - **Specific concern: Test IV |γ₁| ≥ 0.05σ threshold is below
    PAP 2025's noise level.** Our pre-registered Test IV threshold
    of 0.05σ for substantive significance falls *below* what PAP
    2025 calls noise. If our analysis returns γ₁ = 0.06σ, we'd
    report it as a substantively significant headline finding —
    but it would be at the same magnitude PAP 2025 dismisses as
    noise. **Decision: raise Test IV threshold from 0.05σ to
    0.10σ** to safely clear the published noise calibration.
  - **Test I threshold review.** Currently Test I slope ≥ 0.02
    SD/year (a 1-SD gap change over 50 years). Different units
    than PAP 2025's σ-units; not directly comparable. Need to
    compute what 0.02 SD/year corresponds to in σ-units terms over
    our 1990-2024 window — probably moderate effect, but worth
    checking. If conversion shows Test I threshold is also below
    0.10σ-equivalent, raise.
  - **Cost:** zero — just re-pre-registering thresholds before
    Stage 2 runs.
  - **Why this matters substantively.** If our pre-registered
    threshold is below the noise floor, our headline claim becomes
    methodologically indefensible against PAP 2025-style critique.
    Raising the threshold is a defensive move that doesn't change
    our analysis, just our claim of what counts as substantively
    significant. Better conservative than vulnerable.
- **Test IV N_p primary/secondary label flip (per disruption-novelty
  discussion in PAP 2025 walkthrough, 2026-04-26).** Currently the
  Test IV N_p specification (Phase 0.1 plan, "Open decisions
  deferred" Test IV block) has:
  - N_p primary: cosine distance to centroid of papers in p's
    reference list
  - N_p secondary: cosine distance to year-Y canonical centroid
    (top-100 most-cited)
  - N_p tertiary (Stage 3): Uzzi-Mukherjee-Stringer reference-pair
    atypicality

  **The issue.** N_p primary as currently labeled depends on focal
  paper's *reference list choice* — exactly the condition-3
  vulnerability PAP 2025 raises about CD-index ("depends on author
  choice, not community consensus"). Conversely, N_p secondary uses
  the year-Y canonical centroid which is *community-determined*
  (top-100 most-cited papers in year Y).

  **Why this matters.** Disruption (CD-index) and novelty (our N_p)
  are conceptually associated metrics. Our N_p variants span a
  spectrum on author-vs-community dependence. The variant we
  labeled "primary" is the *most author-choice-dependent*, which is
  the *most vulnerable* under PAP 2025's framework. Reporting this
  as the headline metric inverts the desirable property: we should
  put our cleanest metric forward as primary, not the most
  vulnerable one.

  **Refinement: relabel and reorder.**
  - **N_p^community (new primary):** cosine distance to year-Y
    canonical centroid. Community-driven, condition 3 cleanly
    satisfied. Methodologically defensible as headline.
  - **N_p^author (new secondary):** cosine distance to reference
    centroid. Author-choice-dependent, partial condition 3.
    Reported alongside as alternative operationalization, with
    explicit framing that it has the same author-choice
    vulnerability PAP 2025 raises about CD.
  - **N_p^combinatorial (Stage 3, unchanged):** U-M-S atypicality.

  **Why this is parallel to (c-prime) framing.** Just as we report
  inflation-immune metrics as primary against PLF, we should report
  community-driven novelty metrics as primary against disruption-
  index critique. Same defensive logic.

  **What this preserves vs. changes.**
  - Preserves: the multi-operationalization commitment (we report
    all three).
  - Preserves: the substantive Test IV question (does team
    diversity correlate with paper-level novelty?).
  - Changes: which N_p is the headline metric. Discussion section
    can engage both — "headline N_p^community shows X; alternative
    N_p^author shows Y; consistent vs. divergent results discussed."
  - Changes: which N_p the pre-registered γ_1 effect-size threshold
    applies to (now applies to N_p^community by default).

  **Cost.** Computationally trivial. Same underlying computation;
  just different label and reporting order. The substantive
  refinement is methodological, not analytical.

  **Methods-paragraph framing.** This refinement also strengthens
  the Methods-section three-conditions defense (commitment 1 of
  c-prime): we explicitly identify which Test IV operationalization
  passes condition 3 cleanly (N_p^community), which has partial
  vulnerability (N_p^author), and report multi-operationalization
  as a hedge.
- **Post-2006 disruption-uptick context in (c-prime) Discussion (per
  PAP 2025 C2 walkthrough, lit-review session 2026-04-26).** Add
  one sentence to the (c-prime) Discussion-section paragraph
  acknowledging the four-paper convergence (PAP 2025, Bentley 2023,
  Holst 2024, Macher 2024) on a small post-2006 incremental
  disruption increase (~0.06σ). Frame as concurrent observation of
  a related-but-distinct phenomenon, not as competing/supporting
  ws2's findings. Specifically: "Post-2006, multiple independent
  re-analyses find a small incremental increase in disruption after
  CI controls. Our findings on canonical concentration and semantic
  plurality should be interpreted in this context — concurrent
  observations of related but distinct phenomena." Cost: one
  sentence; folds into existing (c-prime) Discussion paragraph.
  Why this matters: pre-empts reviewer pushback ("how does your
  finding relate to the recent disruption-uptick literature?")
  with a calibrated answer that doesn't expand scope.

- **Test I break-point candidate refinement: add 2006 (per PAP 2025
  C2 walkthrough, lit-review session 2026-04-26).** Currently
  pre-registered Test I break-point candidates for CS: 1991-93
  (arXiv launch); 1998-2000 (dot-com peak; demographic
  broadening); 2008-09 (financial crisis; academic-market
  consolidation); 2012 (AlexNet / deep learning); 2018-20
  (foundation models). **Add 2006** as additional candidate
  aligned with the four-paper convergence on post-2006 disruption-
  uptick (PAP 2025, Bentley 2023, Holst 2024, Macher 2024).
  Substantive justification: independent disruption-literature
  convergence on 2006 as a candidate inflection year for
  scientific dynamics. Cost: one additional candidate in
  pre-registered list; doesn't expand analytical scope. The
  Bonferroni correction across 6 candidates (rather than 5) for
  CS slightly tightens significance threshold; manageable.
- **Citation-difference-near-threshold sensitivity check (per PAP
  2025 C3 walkthrough, lit-review session 2026-04-26).** PAP 2025's
  WWE 2019 critique highlights percentile-amplification as a
  methodological pitfall. ws2's metrics are not vulnerable to the
  classic WWE pattern (no per-paper percentile transformation
  combined with concentrated distribution). However, a subtler
  related concern is rank-instability in our Spearman top-N list
  driven by small absolute citation differences for papers near
  rank N. To bound this empirically rather than relying solely on
  the heavy-tail assumption:
  - **Diagnostic:** for each (field × year), compute citation count
    at rank 50 minus citation count at rank 51 (Δ_50). Compute
    relative version Δ_50_relative = Δ_50 / (citation count at
    rank 50). Plot distribution across (field × year) cells.
  - **Pre-registered interpretive thresholds:**
    - Median Δ_50_relative > 5% → heavy-tail assumption holds;
      rank-instability concern minimal; existing multi-N
      robustness (N ∈ {30, 50, 100}) sufficient.
    - Median Δ_50_relative 1-5% → moderate; multi-N robustness
      check becomes more load-bearing in interpretation.
    - Median Δ_50_relative < 1% → heavy-tail assumption fails;
      rank-instability is real concern; trigger expanded multi-N
      reporting (N ∈ {200, 500} for additional robustness).
  - **Cost:** ~half-day Stage 2 effort. Computational only; uses
    existing OpenAlex citation data.
  - **Why this complements existing multi-N robustness.** Multi-N
    robustness tests how Spearman varies across N choice; this
    diagnostic empirically tests the *heavy-tail assumption* that
    underlies our claim that small-magnitude citation differences
    don't cause rank-flip artifacts. The two are complementary:
    multi-N tests outcome stability; near-threshold diagnostic
    tests input-side stability assumption.
- **Methods-section sentence on percentile-amplification compliance
  (per PAP 2025 C3 walkthrough, 2026-04-26).** Add to (c-prime)
  sub-commitment 1 (three-conditions Methods paragraph): one
  sentence acknowledging PAP 2025's percentile-amplification
  critique and ws2's compliant reporting practice. Specifically:
  "Following PAP 2025's recommended practice, ws2 reports effect
  sizes in σ-units of raw metrics rather than percentile-rank
  transformations. Our metrics are not vulnerable to WWE-style
  percentile-amplification because they either operate at the
  aggregate level (Tests I-III metrics, computed once per
  field-year) or use direct value-based measurements (Test IV T_p
  and N_p)." Cost: one sentence in existing Methods paragraph.
- **Broader post-PLF critique landscape acknowledgment in (c-prime)
  Discussion (per PAP 2025 C6 walkthrough).** Add one sentence to
  the (c-prime) Discussion-section paragraph acknowledging that
  PAP 2025's critique pattern extends beyond PLF 2023 itself to
  other CD-based scientometric findings (e.g., Lin et al. 2023a on
  collaboration distance; Wang et al. 2023b on geographic
  dispersion). Explicitly mark ws2's scope: "ws2 engages the
  citation-inflation question specifically rather than auditing
  related findings." Cost: one sentence; folds into existing
  (c-prime) Discussion paragraph. Why this matters: pre-empts
  reviewer pushback on related papers we don't address while
  maintaining bounded scope. We don't take positions on individual
  papers; we acknowledge the landscape exists and focus on what's
  load-bearing for ws2.
- **Threat-to-check mapping as Methods deliverable (per Holst C2
  walkthrough, lit-review session 2026-04-27).** For each
  pre-registered ws2 robustness check, build an explicit mapping:
  what threats does this check target? At what level does it
  operate? What's the failure mode (false positive of robustness)?
  Format: small Methods-section table or appendix. Approximate
  initial mapping (per Holst C2 walkthrough captured in PAP review
  file):
  - Detrended correlation w/ r(t) → citation inflation via reference
    list growth; metric-covariate correlation level; misses
    non-r(t) threats.
  - Multi-Δ Spearman / Multi-N robustness → window/threshold choice
    as artefact; window/N choice level; misses if all values miss
    true regime.
  - Decoupled-subfield robustness → field-size-vs-time confound;
    subfield × time correlation level; misses if subfield count
    low at strict thresholds.
  - Pooled measurement-robustness appendix → measurement-uncertainty
    restrictions; per-restriction row level; misses threats
    preserved across restrictions.
  - Cohort decomposition Option B → cohort-mix-driven divergence;
    year × cohort bins; lead-author cohort proxy limited.
  - Citation-difference-near-threshold → rank-instability near
    top-N; input-side stability; heavy-tail near top is
    field-specific.
  - OpenAlex coverage diagnostic → coverage variability; per-era ×
    region rate; coverage-metric joint distribution.
  - Citation-completeness sensitivity → undercoverage of citations;
    completeness threshold; completeness measure itself biased.
  - Subfield mechanism nonlinearity check → linear masks regime
    shift; quadratic + LOWESS; non-monotonic shapes quadratic
    can't capture.
  - Test II quadratic fallback / Test IV with/without c_p →
    captured separately.
  Cost: ~half-day to construct; informs Methods exposition;
  documents what we do and don't claim to robustly defend against.

- **Limitations-section paragraph on uncovered threats (per Holst
  C2 walkthrough, 2026-04-27).** Explicit acknowledgment that
  ws2's robustness checks address specific threats at specific
  levels; threats operating at levels not covered by our machinery
  may persist as potential confounds. Specifically acknowledge
  five threats not well-covered:
  - **(A) System-wide OpenAlex artefacts:** none of our committed
    checks operate on alternative data; cross-substrate
    WoS-OpenAlex overlap is back-pocket only.
  - **(B) Embedding-model bias:** drift-mitigation addresses
    cross-era stability but not training-data bias; alternative-
    model robustness (Stage 2) verifies embedding-model swap is
    complete, not just adapter swap.
  - **(C) Compound-threat interactions:** single-threat-at-a-time
    checks may not capture interactions; not directly addressable.
  - **(D) Demographic inference systematic bias:** ORCID validation
    on non-random subsample (people with ORCID); inherent
    limitation.
  - **(E) Subfield-classifier drift cascading effects:** classifier
    drift audit (sanity Check 2) is metric-level; downstream
    handling decided contingent on audit results.
  Approximately one paragraph (~150 words). Methodologically
  humble; matches Holst's lesson against overclaiming.

- **Robustness consolidation pass framework (refines existing
  Phase 0.1 closure gate #10, per Holst C2 walkthrough,
  2026-04-27).** During the existing committed Phase 0.1 closure
  consolidation pass (gate #10), apply Holst-derived framework:
  for each existing robustness commitment, evaluate whether it is:
  - **Threat-specific** (targets one well-defined threat at the
    right level) → keep as-is; document threat targeting in the
    threat-to-check mapping.
  - **Generic stability check** (just "let's see if results are
    stable") → replace with threat-specific framing or drop.
  - **Redundant** (multiple checks at the same level for the same
    threat) → consolidate into single check with clearer threat
    targeting.
  - **Missing** (threat identified but not covered by any check) →
    add new check OR acknowledge gap in Limitations OR defer to
    back-pocket if expensive.
  This refines gate #10's existing consolidation scope by adding
  threat-specificity as the explicit evaluation criterion.

- **Pre-registered exclusion of degenerate cases for ws2 metrics
  with two-stage calibration protocol (per Holst recommendation +
  EDA-needs walkthrough, 2026-04-27).** Holst's "exclude degenerate
  cases prior to analysis" methodological principle applied to
  ws2. The threshold values themselves split into two categories:
  *theoretically grounded* (can lock now in Phase 0.2) and
  *empirically dependent* (need EDA on pilot data before locking).

  **Stage A — Phase 0.2 pre-registration (lock now):**

  *Principle:* small-sample field-year cells excluded from
  metric computation prior to analysis. Each exclusion has a
  stated rationale tied to metric-stability or small-sample
  concerns.

  *Theoretically-grounded exclusions (lock now):*
  - **Test IV N_p:** papers with fewer than 5 references excluded
    from primary analysis. Rationale: insufficient reference
    points for stable centroid in cosine-distance computation.
    Already committed; defensible from principle.
  - **Test IV T_p:** single-author papers (T_p = 0 by construction)
    handled as baseline comparison group, not excluded. Already
    committed; definitional.
  - **Demographic plurality metrics:** authors with no
    demographic-confidence-passing inference excluded; weight-by-
    confidence + per-region accuracy reporting. Already committed
    via Hofstra C4 framework.

  *Empirically-dependent exclusions (initial heuristics; refine in
  Stage B):*
  - **Spearman top-N:** initial heuristic n ≥ 2N for stable
    correlation. Reason for empirical refinement: variance of
    Spearman under different (n, N) combinations is data-dependent;
    citation distribution shape near rank-N matters.
  - **Citation Gini:** initial heuristic n ≥ 50 (rule-of-thumb for
    stable Gini under Miller-Madow correction). Reason for
    empirical refinement: heavy-tailed distributions may need more;
    actual variance scaling with n is data-dependent.
  - **Cluster entropy / effective dim / pairwise distance:** initial
    heuristic n ≥ 100. Reason for empirical refinement: K=50
    clusters needs a few papers per cluster, but skewed within-
    cluster distribution affects this; embedding-space spread
    affects pairwise distance stability.

  **Stage B — Phase 0.1 sanity Check 5 / early Stage 1 EDA-driven
  calibration:**

  Specific calibration tasks for each empirically-dependent
  metric:

  - **Spearman top-N stability:** for each (field, year) cell in
    pilot sample, compute Spearman top-50 between adjacent years
    at varying n thresholds (n ≥ 100, 200, 500, 1000). Plot
    variance of Spearman as function of n. Identify inflection
    point where variance stops decreasing materially. Update
    threshold to that empirical point. Connects to existing
    citation-difference-near-threshold diagnostic (PAP 2025 C3 +
    SQ3 commitment) — same data, complementary angle.
  - **Citation Gini stability:** for each cell, compute Gini at
    varying n via bootstrap. Plot bootstrap CI width as function
    of n. Identify where CI width stabilizes. Update threshold.
  - **Cluster entropy / eff dim / pairwise distance stability:**
    bootstrap subsamples at varying sample sizes; plot variance
    and bias as function of n; identify minimum stable threshold.

  **Update protocol pre-registered:**
  - If empirically-calibrated threshold is *higher* than initial
    heuristic → adopt empirical threshold; document rationale.
  - If empirically-calibrated threshold is *lower* than initial
    heuristic → adopt empirical threshold only if doing so
    preserves stability claims; document the looser threshold.
  - If empirical and heuristic are similar → adopt heuristic;
    document validation.
  - All deviations documented in Methods with rationale.

  **Why this two-stage structure matters.** Pre-registering
  arbitrary thresholds risks either over-exclusion (losing valid
  data) or under-exclusion (analyzing degenerate cases). EDA-driven
  calibration matches thresholds to actual data characteristics.
  But pre-registering the *protocol* prevents post-hoc threshold
  manipulation to favor desired findings — the calibration follows
  pre-registered stability criteria, not desired-result criteria.
  Methodologically clean approach to a real EDA-vs-pre-registration
  tension.
- **Single-author dummy in Test IV regression (per Holst dummy-
  variable-controls walkthrough, 2026-04-27).** T_p (Rao's Q) has
  a definitional discontinuity at k_p = 1: single-author papers
  have T_p = 0 *by construction* (Rao's Q undefined for n=1, set
  to 0 by convention); team papers have T_p > 0 *measured value*.
  The current linear regression treats T_p = 0 (single-author
  definitional) and T_p ≈ 0 (homogeneous team measured) as
  interchangeable cases, but they're conceptually different.
  - **Spec refinement:** N_p = γ_0 + γ_1·T_p + γ_2·1[k_p = 1] +
    γ_3·c_p + ... + ε_p. γ_2 captures the discontinuous shift for
    single-author papers; γ_1 captures the continuous slope for
    team papers.
  - **Pre-registered fallback rule:** if γ_2 not significant at
    p<0.05, default to spec without dummy; if significant, report
    with dummy. Parallel to PAP 2025 quadratic fallback; prevents
    post-hoc specification choice.
  - **Why this matters substantively:** if single-author papers
    behave qualitatively differently from team papers (e.g.,
    systematically lower or higher N_p), γ_2 will be significant
    and we report a substantively interesting finding. If similar
    to homogeneous teams, γ_2 ≈ 0 and our linear specification
    was treating them interchangeably without harm.
  - **Cost:** computationally trivial. One additional regression
    coefficient. Methodological cleanness gain regardless of γ_2
    significance.

- **Pre-1990 dummy in Tests I-III specifications (per Holst dummy-
  variable-controls walkthrough + Phase 0.1 §13 alignment,
  2026-04-27).** Tests I-III span 1970–2024 with pre-1990 retained
  per §13 non-negotiable. Pre-1990 metadata quality differs from
  post-1990 in known ways (sparser abstracts, weaker demographic
  inference, classifier drift, OpenAlex coverage variability).
  Year fixed effects absorb year-specific shifts equally for all
  years; a specific pre-1990 dummy tests whether the pre-1990 era
  contributes a systematic shift *beyond* what year-FE absorbs —
  parallel to Holst's zero-references dummy in PLF's regression.
  - **Spec refinement:** add θ·1[Y < 1990] dummy to existing Tests
    I-III specifications (Test I trend regression; Test II gap
    regression; Test III cross-correlation models with appropriate
    adaptation).
  - **Pre-registered interpretive grid:**
    - θ small and not significant → drift mitigation absorbed
      pre-1990 measurement effects; existing year-FE specification
      sufficient. Headline finding robust.
    - θ significant and large → drift mitigation didn't fully
      absorb pre-1990 effects; report with explicit pre-1990
      segmentation; consider partition-by-era reporting.
    - θ significant but small → pre-1990 era contributes a
      systematic shift but not load-bearing for headline; report
      with dummy; document magnitude.
  - **Why this is the *operational diagnostic* for §13 retention
    policy.** §13 commits to retaining pre-1990 substantively;
    drift mitigation is the technical handler; the pre-1990
    dummy *tests whether the technical handler did its job*.
    Without this dummy, we have no specific-test for the
    drift-mitigation-success claim.
  - **Cost:** computationally trivial. One additional coefficient
    per Tests I-III regression.

- **Test IV k_p > 500 sensitivity row (per Holst C1 walkthrough,
  2026-04-27).** Add one row to existing pooled measurement-
  robustness appendix (Hofstra C8 commitment): Test IV regression
  restricted to papers with k_p ≤ 500. Captures HEP-saturation
  regime specifically (large collaborations where T_p saturates
  near maximum because every demographic group represented
  mechanically). Primary spec unchanged — existing (log k_p)²
  quadratic from PAP 2025 refinement handles 50-500 range; this
  addresses extreme tail only (< 1% of papers, concentrated in
  HEP). Cost: one additional row in robustness appendix.

- **Test IV exclude c_p = 0 papers from primary (per Holst C1
  walkthrough, 2026-04-27).** Direct Holst-parallel: PLF set
  CD-index of uncited papers to "non-defined" or 0 by convention.
  Papers with c_p = 0 (uncited at 5 years post-publication) have
  ill-defined relationships with N_p — no community uptake means
  we can't test "team diversity → community-recognized novelty"
  for these papers. Pre-register: exclude c_p = 0 from Test IV
  primary analysis; include as sensitivity-only subset (one row
  in robustness appendix). Substantive rationale matches PLF's
  treatment of CD = 0 cases.

- **Subfield mechanism test temporal-coverage threshold (per Holst
  C1 walkthrough, 2026-04-27).** Subfields with < 10 years of
  post-1990 coverage excluded from subfield mechanism test.
  Insufficient time series for stable slope estimation in either
  CanonConc_s (mean Spearman over time series) or DivMag_s (slope
  of standardized gap). Refinement to existing subfield mechanism
  test specification.

- **Demographic plurality per-year coverage disclaimer (per Holst
  C1 walkthrough, 2026-04-27).** Years where < 50% of authors
  have confident demographic inference flagged with explicit
  disclaimer (not excluded). Years below threshold reported with
  caveat in headline figures and tables: "demographic plurality
  estimate for year Y based on partial coverage; interpret with
  caution." Refinement to existing weight-by-confidence handling.

- **Anchor-concept distribution diagnostic (per Holst C1
  walkthrough, 2026-04-27).** Add to Phase 0.1 sanity Check 2
  (concept classifier drift audit) a check: per-subfield count
  of anchor concepts. Subfields with < 5 anchor concepts flagged
  as having unstable anchor-projection (Mitigation 4); downstream
  handling: subfield-level anchor-projection results for these
  subfields reported with caveat or excluded from anchor-projected
  semantic-diversity metrics. Refinement to existing classifier-
  drift audit.

- **Multiple-comparisons hierarchy pre-registration (per Holst C2
  Threat H walkthrough, 2026-04-27).** Pre-register that ws2's
  *headline claim* requires agreement across Tests I, II, III,
  and IV — not significance in any single test. Parallel to
  Chu-Evans's six-prediction structure (where the substantive
  claim required agreement across all six predictions, not just
  any one). Existing Bonferroni correction within test-types is
  retained for *within-test-type* multiple comparisons; the
  *across-test-type* multiple-comparisons concern is addressed by
  the agreement requirement, not by additional Bonferroni.
  Specifically:
  - **Headline divergence claim** (gap-trend > 0): requires
    Test I significant + Test II significant + Test III shows
    no aggressive lagged-tracking pattern + Test IV consistent
    direction.
  - **Disagreement across tests** → substantively interesting;
    report all four with explicit interpretive grid; don't claim
    headline.
  - **All four agree** → headline claim defensible; conjunction
    is the multiple-comparisons-correction strategy.
  Documented in Methods alongside the per-test Bonferroni rules.

- **Citation-window aggregation sensitivity (per Holst C2 Threat G
  walkthrough, 2026-04-27).** Extend existing multi-Δ Spearman
  commitment (Δ ∈ {1, 5, 10} adjacent-year-stability lag) to
  also include Δ_aggregate ∈ {3, 5, 10} sensitivity for the
  underlying citation-window aggregation. The two are different
  parameters (Δ = stability lag between top-N lists; Δ_aggregate
  = years of citations counted to identify "top-N"). Report both
  as sensitivity rows in robustness appendix. Extends existing
  multi-Δ commitment from one parameter to two.

- **Bootstrap CI alternative-method sensitivity (per Holst C2
  Threat I walkthrough, 2026-04-27).** For headline metrics in
  Tests I-III, compare 200-replicate Pearson bootstrap CIs to
  alternative-method CIs (jackknife, BCa bootstrap, or analytical
  SEs where available). Sensitivity check at headline level only
  — not exhaustive coverage. If alternative-method CIs differ
  materially (>20% width difference), flag and investigate.
  Single sensitivity row in robustness appendix.

- **Preprocessing acknowledgment in Limitations (per Holst C2
  Threat F walkthrough, 2026-04-27).** Methods/Limitations
  paragraph documenting that preprocessing decisions (abstract
  cleaning, citation aggregation, tie-breaking, identity-merging)
  are pre-registered but represent inherent uncertainty not
  captured by metric-level robustness checks. ~100 words.
  Methodologically humble; matches Holst's lesson on robustness-
  check-failure-modes (level-mismatch).

- **Year-level aggregation acknowledgment in Methods (per Holst
  C2 Threat J walkthrough, 2026-04-27).** One-sentence
  acknowledgment: "ws2 aggregates to year-level for the temporal
  axis. Finer (monthly, quarterly) or coarser (5-year period)
  aggregations are not pursued; year-level is methodologically
  defensible given citation-window-aggregated metrics but
  represents a methodological choice." Folds into Methods.

- **Gender inference accuracy hand-validation (per Holst C3
  walkthrough, 2026-04-27).** Stage 1 hand-validation of NamSor
  gender-prediction accuracy. Methodology:
  - Sample 100 author names from ws2 corpora (50 pre-1990 + 50
    post-1990; stratified to ensure region diversity).
  - Match each against ORCID where available.
  - Compare NamSor's predicted gender to ORCID self-reported
    gender.
  - Binary outcome per name: match / mismatch.
  - Report per-region accuracy (Anglo / East-Asian / South-Asian /
    other) and per-era accuracy (pre-1990 / post-1990).
  - **Pre-registered interpretive thresholds:**
    - ≥ 90% per-region accuracy → confirm pipeline; weight-by-
      confidence sufficient.
    - 80-90% per-region accuracy → caveat in Methods specific to
      that region; expand NamSor coverage if budget permits.
    - < 80% per-region accuracy → trigger expanded NamSor +
      manual-review pipeline for that region; possibly drop
      regions falling below threshold from headline analysis.
  - Cost: ~3 hours of hand-validation work in early Stage 1.
  - Why binary: ORCID provides binary self-report; NamSor outputs
    binary prediction; comparison is binary match/mismatch.
    Holst-style methodology applies cleanly.

- **Reference list completeness hand-validation (per Holst C3
  walkthrough, 2026-04-27).** Stage 1 hand-validation of OpenAlex
  reference list completeness. Methodology:
  - Sample 100 papers from ws2 corpus (post-1990; non-zero
    OpenAlex reference count; DOI accessible via Crossref).
  - For each: get reference count from Crossref + OpenAlex.
  - Compute completeness ratio = OpenAlex_count / Crossref_count.
  - Binarize: complete match (ratio ≥ 0.95) / partial mismatch
    (0.7 ≤ ratio < 0.95) / OpenAlex-fewer (ratio < 0.7).
  - **Pre-registered interpretive thresholds (median completeness
    ratio):**
    - ≥ 0.90 → confirm pipeline; Test IV N_p^author estimates
      reliable.
    - 0.70 - 0.90 → caveat in Methods; Test IV N_p^author
      estimates have known systematic undercounting.
    - < 0.70 → trigger expanded reference-completeness sensitivity
      in robustness appendix; consider supplementing OpenAlex
      reference data with Crossref where available.
  - Cost: ~3 hours of hand-validation work in early Stage 1.
  - Why direct ground truth: Crossref reference data is well-
    validated and accessible; provides clean binary-or-continuous
    comparison to OpenAlex.

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

Phase 0.1 target: **3 weeks, ~55–60 hours of effort** (bumped from the
original 2-week estimate to reflect the parallel lit-review track and
drift-pilot addition).

- **Week 1:** methodology commitment (this document); OpenAlex API
  setup + pilot query; `field_definitions.csv` draft. Literature
  review Tier 1 begins in parallel (~5 hrs).
- **Week 2:** sanity checks 1–5 (abstract coverage, classifier drift
  audit, demographic coverage, disambiguation spot-check, metric
  convergence, cluster-stratification A/B, drift-pilot);
  pilot-query review; cost budget revision. Literature review Tier 1
  continues (~10 hrs).
- **Week 3:** literature review Tier 2 (~15 hrs); `synthesis.md`
  harvest; drift-pilot decision locked; retro. If lit review
  surfaces methodology conflicts, Phase 0.1 re-opens before Phase 0.2.

Advancement to Phase 0.2 (pre-registration) assumes Phase 0.1 closes
cleanly and all validation gates pass, including lit-review closure
and drift-pilot decision. Advancement to Phase 1.1 (full data pull)
assumes Phase 0.2 and Phase 0.1 both close.

## Companion documents and maintenance

Derivative documents that depend on this plan and must be kept in sync
when the plan materially changes. If you edit this plan in a way that
alters scope, methodology, or decision logic, check the corresponding
companion(s) in the same session.

- **`../plan-at-a-glance.md`** — visual summary via Mermaid diagrams.
  Covers three-whitespace epistemic layering (diagram 1); phase/stage
  backbone with gates (diagram 2); drift-mitigation branching
  (diagram 3); test structure including aggregate, per-paper, and
  scale-bridging tests (diagram 4); semantic-diversity metric stack
  (diagram 5); novelty metric stack (diagram 6); pathway coverage
  table (section 7); Phase 0.1 sanity-check structure (diagram 8).
  **Update triggers:**
  - Phase/stage structure change → diagram 2
  - Drift-mitigation conditions or thresholds change → diagram 3
  - New tests or extensions added → diagram 4
  - Metric stack changes → diagrams 5 and 6
  - Pathway coverage changes → section 7 table
  - New sanity checks or Phase 0.1 deliverables → diagram 8
  - Three-whitespace program structure changes → diagram 1

- **`../primers/stats.tex`** — statistical methods primer. Update when
  new statistical methods are committed (new regression types, new
  correction schemes, new bootstrap protocols, etc.).

- **`../primers/topic-modeling.md`** — topic-modeling and
  cluster-quality diagnostics primer. Update when STM/FREX/clustering
  methodology changes in the plan (e.g., if Hofstra-style concept-
  linkage secondary novelty is pursued and introduces new pipeline
  commitments).

- **`../../literature-review/`** — per-paper review files.
  Synthesis Pointers that live in review files (currently 12 in
  `06-hofstra-2020-...md`) should be harvested into
  `literature-review/synthesis.md` as they accumulate across papers.
  Cross-paper methodological tensions surfaced in review sessions
  may imply plan updates — check when a review session closes.

**Cross-reference discipline (recommended workflow):**

1. Edit the plan file.
2. Before committing, check the companion-doc update-trigger list
   above; if a trigger is hit, edit the relevant companion in the
   same commit or the immediately-following one.
3. If a companion edit is deferred (e.g., "plan changed but diagram
   sync is tomorrow's task"), add a TODO entry to
   `../../tasks/todo.md` or a note to `docs/phases/phase-0.1-retro.md`.
4. Phase 0.1 closure gate: all companion docs synced before
   advancing to Phase 0.2. Include a companion-doc-freshness check
   in the retro.

## References

- North star: `../conceptual.md`
- Principles: `../desiderata.md` (amended §10 and §11 in this phase)
- Visual summary: `../plan-at-a-glance.md` (Mermaid diagrams;
  maintenance triggers listed above)
- Statistics primer: `../primers/stats.{tex,pdf}` (covers all methods
  committed in this plan)
- Topic-modeling primer: `../primers/topic-modeling.md`
- Program context: `../../../docs/program/`
- Literature review: `../../literature-review/README.md`
- Todo: `../../tasks/todo.md`
- Spend: `../../tasks/spend.md`
- Lessons: `../../tasks/lessons.md`
