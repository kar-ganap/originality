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
  - **(1) Methods-section paragraph defending inflation-immunity,
    organized via PAP 2025's three-conditions framework (per PAP
    2025 C4 walkthrough, lit-review session 2026-04-26).** ~7-9
    sentences. PAP 2025's Discussion lays out three conditions any
    cross-temporal citation metric should satisfy: (i) stationary
    distribution over time; (ii) most weakly sensitive to secular
    growth (especially CI from r(t) and n(t) growth); (iii)
    captures consensus of broader scientific community, not entirely
    dependent on author choices. CD-index fails all three
    structurally; ws2's metrics pass all three by construction or
    via committed mitigations. Use this as organizing structure
    for the Methods paragraph:
    - Spearman top-N satisfies (i) bounded in [−1, 1] + rank-
      stable; (ii) rank-invariant; (iii) determined by community
      citation patterns.
    - Citation Gini satisfies (i) bounded in [0, 1]; (ii) tested
      by detrended diagnostic; (iii) based on community-wide
      citation distribution.
    - Cluster entropy / effective dim / mean pairwise distance
      satisfy all three via embedding-space orthogonality to
      citation network structure (with cluster-fit temporal
      stratification per desiderata §11 and drift-mitigation
      ladder ensuring (i)).
    Two ws2-specific extensions of the framework: (iv) robustness
    to author-disambiguation errors (handled by Hofstra C8
    identity-confidence diagnostic); (v) robustness to missing
    references in early-era data (handled by pre-1990 tier
    specifications). Methods paragraph cites PAP 2025 as the
    framework source and notes ws2 satisfies the conjunction.
    This is methodologically stronger than purely defensive
    structural arguments because it appeals to a published criterion
    set rather than ad-hoc claims of inflation-immunity.
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
    of Spearman top-50 and citation Gini over the post-1990
    analysis window. Test for time-stationarity of distribution
    mean and variance. Per PAP Fisher-Tippett observation: under
    inflation-immune regimes, metric distributions become time-
    stationary; non-stationarity tracking r(t) growth is the
    smoking gun for inflation. Report alongside headline metrics.
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
      post-1990 analysis window (r(t) exponential at g_r ≈ 0.018;
      CanonConc plausibly monotonic if hypothesized trend is
      real). Raw correlation would trigger stress-test for
      everything, providing no information. Detrending isolates
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
  - **Add quadratic on log(avg team size)** — captures non-monotonic
    team-size effects PAP 2025 documented (negative for small
    teams, positive for k_p ≥ 8). Currently linear-only.
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
  - **Add c_p (citation impact of paper p) as paper-level control**
    — paper's own citation count at 5 years post-publication.
    Currently NOT in our spec. Critical because c_p correlates with
    both T_p (team diversity may correlate with citation impact via
    international collaborations) and N_p (highly-cited papers may
    have systematically more diverse or more concentrated reference
    lists). Without c_p control, γ₁ absorbs whatever c_p is doing —
    classic omitted-variable bias.
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
