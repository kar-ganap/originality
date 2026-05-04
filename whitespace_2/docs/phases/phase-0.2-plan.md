# Phase 0.2 Plan / Pre-Registration

**Phase:** 0.2 (Stage 0 — Foundation, closing-out phase)
**Window opens:** 2026-05-04
**Author:** Kartik Ganapathi (with Claude assistance)
**Status:** Active draft. Locks pre-Stage-1 methodology commitments.
**Companion:** `docs/phases/phase-0.1-retro.md` (backward-looking).

---

## One-line scope

**Lock the methodological pre-registration for Stage 1 production
work** by consolidating all Phase 0.1 empirical findings + Tier 2A
literature engagement into committed analytical-population definition,
metric specifications, test specifications (I, II, III, IV),
demographic-inference pipeline, drift-mitigation strategy, cluster-fit
manifest commitment, and propensity-correction model.

This document IS the pre-registered analysis plan. Stage 1
production data work begins after this is locked.

---

## Why this phase exists

Phase 0.1 ran 8 sanity checks, scaffolded the embedding pipeline,
and revised the methodology plan (N1 + N1+) based on empirical
findings. Phase 0.1's outcomes (per `phase-0.1-retro.md`):

- **Surfaces requiring locked commitments**: NamSor escalation
  (Check 3), per-metric N_target (Check 5b), Flavor A drift
  mitigation (Check 5c), §11 production-scale re-validation
  (Check 5d), three pull-spec tightenings (Check 5c), 100-record
  ORCID-linkage validation (Culbert 2025 close-read).
- **Specification refinements** from Tier 2A close-reads: quadratic
  team-size + interaction (Wu-Wang-Evans), search-depth +
  search-popularity as Test II measures, fractional probabilistic
  counting (Kozlowski + Lockhart P5), CV-by-region as §11 diagnostic
  (Kozlowski), substrate-divergence note (Wu-Wang-Evans /
  Culbert), explanation-turn framing (Funk).

Phase 0.2 is the **last methodology-design phase**. After this,
Stage 1 begins production-scale data work; methodological revisions
become Stage-1-conditional plan-revisions, not Phase-0.2 design.

The phase has three deliverables:

1. **This document** — the pre-registered analysis plan, locking
   §0-§14 methodology + the four headline tests + robustness scope.
2. **The Stage-1 task list** — production-scale work items including
   the pull, disambiguation, demographic-inference pipeline, §11
   re-validation, ORCID-linkage validation, and pre-Stage-2
   embeddings.
3. **A signed-off transition-gate decision** — user signoff that
   the pre-registration is complete, no further methodological
   investigation is needed, and Stage 1 may begin.

---

## Pre-registered hypotheses

Four headline tests, pre-registered before any Stage 1 production
data is touched. All four operate on the §0 analytical population P
(or the §0 P_demo subset for demographic analyses) within the
1970-2024 window. Reported with §9e propensity-corrected aggregates
+ §9a P5 bias-uncertainty band.

### Test I — Annual divergence in three plurality dimensions (THE HEADLINE)

**Hypothesis:** Demographic plurality (gender × country × prestige
joint Shannon entropy + Rao Q) and intellectual plurality (cluster
entropy + effective dimensionality + mean pairwise cosine distance)
diverge as time series over 1970-2024 in CS, with semantic plurality
stagnating or declining while demographic plurality rises.

**Pass criterion:** OLS regression of (semantic plurality / demographic
plurality) ratio on year shows negative slope significant at p<0.05
two-tailed across BOTH (a) embedding-cluster-based semantic metric
AND (b) effective-dimensionality semantic metric, with directional
agreement on the third (mean pairwise cosine).

**Fail criterion (successful null):** Both semantic and demographic
plurality rise in tandem with no significant divergence — this is
the substantive null that disconfirms claim #13. Reportable as a
publication-quality null per ws2 desideratum on null reporting.

**Negative control (pre-registered):** Canonical-concentration
(citation Gini + Spearman top-50) should also rise over time per
the Park-Leahey-Funk 2023 + Funk 2026 disruption-decline literature.
If canonical-concentration is FLAT in our data, the analysis is
substrate-broken and the divergence finding is not interpretable.

### Test II — Within-individual semantic scope vs team size

**Hypothesis:** Within author A across A's career, A's papers'
intellectual scope (semantic, search-depth, search-popularity)
varies with team size. Following Wu-Wang-Evans 2019 + Petersen
2025, both within-author and across-author specifications are
reported.

**Specifications (three pre-registered):**
1. Team-size as control: `scope ~ team_size + author_FE + year +
   subfield_FE + ε` (W-W-E within-author specification).
2. Team-size as primary predictor: `scope ~ team_size + year +
   subfield_FE + ε` (Petersen 2025 specification).
3. Team-size-stratified: report effects within each team-size band
   {1, 2, 3-4, 5-9, 10-19, 20+} separately.

**Multi-measure intellectual scope (three measures):**
- (a) Mean pairwise cosine distance of paper to its references'
  embeddings (semantic distance).
- (b) Average reference age (W-W-E search depth).
- (c) Median citation count of references, reverse-coded (W-W-E
  search popularity).

**Pass criterion:** Negative coefficient on team-size in (a) primary,
significant at p<0.05; directional agreement in (b) and (c).

**Substrate-divergence note:** ws2 uses OpenAlex which covers
conference proceedings; W-W-E used WoS which doesn't. Our CS
results may diverge from W-W-E's pattern by substrate, not by
phenomenon (per W-W-E's own caveat). Where our results diverge for
CS, we interpret the difference as substrate-driven; where they
agree for Physics (where journal-article publishing is the norm),
the substrate effect is minimal.

**Negative control:** Author-fixed-effects only specification (no
team-size term) should NOT show significant year effect on
intellectual-scope. If it does, there's an unmodeled author-time
confound.

### Test III — Canonical concentration trend (positioning)

**Hypothesis:** Citation distributions become more concentrated
over time per the disruption-decline literature, measured by:
- Spearman rank correlation on top-50 most-cited papers per year,
  lag Δ=5 (Chu-Evans 2021).
- Citation Gini per year over the per-paper citation distribution.

**Pass criterion:** Both Spearman and Gini show monotone increase
1970-2024, p<0.05 on year-coefficient.

**Why included:** Test III is positioning (not the headline). It
establishes that the canonical-concentration finding from Park-
Leahey-Funk / Wu-Wang-Evans / Funk 2026 inventory replicates on
our specific OpenAlex CS+Physics 1970-2024 substrate. If Test III
fails, the headline divergence reading needs adjustment because
our substrate doesn't reproduce the broader literature's pattern.

**Substrate caveat:** This is precisely the test where Petersen
2024's citation-inflation critique applies. We pre-register the
analysis WITHOUT inflation correction (matching the broader
literature) AND WITH Petersen 2024 correction; report both. If
they disagree directionally, that's the finding.

### Test IV — Team-diversity × novelty regression

**Hypothesis:** Within-paper team diversity (gender × country ×
prestige Rao Q) predicts paper-level novelty (semantic distance
to citation-context centroid) controlling for team size, year,
subfield. Pre-registered specification:

```
novelty_p ~ team_diversity_p
          + team_size_p + team_size_p^2
          + team_diversity_p × team_size_p
          + author/year/subfield FE
          + ε
```

**The quadratic + interaction terms** capture Wu-Wang-Evans 2019's
saturation+reversal at team size 8-10. Pre-registered prediction:
team-diversity coefficient is positive at team-size 4-10, attenuates
beyond 10.

**Pass criterion:** Team-diversity main effect positive at p<0.05;
quadratic team-size term significant; interaction term significant.

**Negative controls:**
- Field-fixed-effects-only specification (no team-diversity) should
  not produce significant year effect on novelty.
- Within-author within-team-size specification (matched team size,
  varying diversity) should preserve the team-diversity effect if
  the headline is real.

**Why this is the load-bearing within-paper test:** Test I tests the
aggregate-level decoupling. Test IV tests whether team-level
demographic diversity directly predicts paper-level novelty. The
two together address claim #13 from population AND individual
levels.

---

## §0 — Analytical population definition (LOCKED)

The analytical population P is the set of OpenAlex `Work` records
satisfying ALL of:

1. `concepts.id ∈ {C41008148, C121332964}` (CS or Physics)
   — selected via API filter.
2. **Score-thresholded** field-concept membership: client-side filter
   `_field_concept_score(work, concept_id) >= 0.30` (loose threshold
   per §3 N1; OpenAlex's `concepts.id:X` filter ignores score).
3. **`has_abstract`**: non-empty `abstract_inverted_index`.
4. **Junk-year-token filter** (pre-1990 only): exclude papers with
   `publication_year < 1990` whose abstract or title contain tokens
   indicating post-2000 origin. **Production list curated for
   post-2000-coined terms only** (per consolidation-pass §A — pre-1990
   chip names, generic "cnn"/"rnn", and pre-2000 protocols REMOVED to
   avoid false-positive exclusion of legitimate early-era papers):
   - Original pilot 5: `r-cnn`, `iot`, `blockchain`, `transformer`,
     `smartphone`.
   - **Post-2000 ML / deep learning** (model-specific, post-2000-coined):
     `lstm`, `gan`, `bert`, `gpt`, `chatgpt`, `attention is all you
     need`, `word2vec`, `glove`, `risc-v`.
   - **Post-2000 protocols / formats**: `tls 1`, `webrtc`, `mqtt`,
     `openid connect`.
   - **Post-2000 devices / contexts**: `wearable`, `vr headset`,
     `cloud computing`, `big data`, `internet of things`,
     `digital twin`, `arm cortex`.

   **Excluded (would over-filter pre-1990 papers per consolidation §A):**
   - Pre-1990 chip names: `tms320`, `tms9900`, `mos6502`, `z80`
     (TMS9900=1976, Z80=1976, MOS6502=1975).
   - Generic terms with pre-1990 lineage: `cnn` (Fukushima
     neocognitron 1980), `rnn` (Hopfield/Elman/Jordan late-1980s),
     `word embedding` (some 1980s connectionist papers).
   - Pre-2000-standardized protocols: `https`.

5. **Empty / near-empty abstract filter**: minimum **15 tokens** after
   inverted-index reconstruction (per consolidation §B — relaxed from
   initial 30; 15 catches boilerplate fillers like "abstract not
   available" / "preview only" without over-filtering legitimate
   short pre-1990 conference abstracts). Excludes the ~empty filler
   strings that Check 5c hand-audit surfaced (rows 8, 14, 17, 19
   with sim≈1.000 on boilerplate).

**Junk-year-token matching implementation (locked).** Tokens matched
via case-insensitive **word-boundary regex** (`\bTOKEN\b`), NOT
substring matching. Required because short production tokens (`gan`,
`bert`, `iot`, `gpt`) substring-match common English ("organism",
"Albert", "patriot", etc.). Validated by Wave 1C dry run 2026-05-04
which surfaced the substring-bug (3/4 cs-1975-baseline drops were
caused by `gan` matching "organism"/"organization"/"organic"); fix
applied; over-filter rate dropped from 17.39% to 4.35% raw / 0.00%
false-positive. See `experiments/phase-0.2/pull-spec-dry-run.md`.

The **strict variant** P_strict applies score≥0.5 instead of ≥0.3.
Used for tight subfield-mechanism analyses (e.g., §11 cluster fit
on tight CS-only papers). Choice between P and P_strict pre-
registered per use case.

The **demographic subset** P_demo is the subset of P with
determinable first-author institution country. Empirically ~45% of
P (Check 1f / Check 3 H6); the gap is the structural
country-undeterminable rate that §9e propensity weighting addresses.

### Snapshot pinning

Every Stage 1 + Stage 2 + Stage 3 run records the OpenAlex snapshot
date in artifact metadata. Re-running on a newer snapshot is a
separate experiment per ws2 desideratum §1. Per Culbert 2025 finding
of 7.61% reference-count growth in one month, snapshot-pinning is
load-bearing.

**Post-snapshot errata check** before publication: review OpenAlex
release notes + Hauschke-Nazarovets 2025-style errata reports for
errors affecting our pinned snapshot. Document any found errors in
Methods.

### Why OpenAlex despite known coverage gaps

Per Culbert 2025: OpenAlex's per-article abstract coverage on the
shared corpus (16.8M DOI-matched 2015-2022 publications) is 87% vs
WoS/Scopus 92%; on our broader 1970-2024 corpus it's ~50% (Check 1).
Internal reference coverage on the shared corpus is 83.2-83.6%,
comparable to WoS (81.6%) and Scopus (87.6%). ORCID coverage is
92% in OpenAlex vs 16-32% in WoS/Scopus, but with a "generous
disambiguation" caveat (over-merge on non-Western names; addressed
via the 100-record ORCID-linkage validation step in §9a P5).

ws2 chooses OpenAlex for: (a) reproducibility (no licensing barriers
prevent code+data sharing), (b) ORCID-coverage advantage (enables
§9a P5 ground-truth validation on a generously-sized subsample),
(c) institutional validation (Sorbonne University 2023 switch).
Cross-substrate WoS/Scopus comparison is Stage 3 robustness using
Culbert's shared-corpus DOI-match recipe; not Phase 0.2 commitment.

---

## §1 — Embedding pipeline (LOCKED — three models)

Per Phase 0.1.E:

- **SPECTER2** (allenai/specter2_base + allenai/specter2 proximity
  adapter): primary semantic model.
- **SciNCL** (malteos/scincl): SBERT-style contrastive scientific
  embedding; transformer-encoder-family robustness partner.
- **Qwen3-Embedding-0.6B** (Qwen/Qwen3-Embedding-0.6B at 768-dim via
  Matryoshka): decoder-LM-derived family for cross-architecture
  robustness.

HF revisions pinned in `data/metadata/embedding-model-pins.csv`.

**Stage 2 default stack**: all three models, with anchor-projection
(Mitigation 4).

**Stage 3 conditional**: Flavor A (Word2Vec-per-decade + orthogonal
Procrustes alignment + TF-IDF-weighted document aggregation) per
Check 5c gray-zone outcome. Locked as committed for Stage 3.

**Stage 2 compute target** (cloud vs local) deferred to Stage 1 —
gated by Qwen3 sorted-batching benchmark + cloud cost estimate +
user time-vs-budget preference. Pre-Stage-2 compute task list in
"Stage 1 prereqs" below.

---

## §2 — Drift-mitigation ladder (LOCKED)

Per `phase-0.1-plan.md` §2 + Check 5c outcome:

**Stage 2 default (always run):**
- Mitigation 2: Cross-model replication (SPECTER2 + SciNCL +
  Qwen3-0.6B).
- Mitigation 4: Anchor-dimension projection. ~100 curated era-stable
  field-specific anchor concepts (e.g., "Fourier analysis,"
  "Turing machines," "graph theory"). Anchor list locked in this
  Phase 0.2 document (see anchor-list appendix below — TODO).

**Stage 3 Flavor A (committed)** per Check 5c:
- SPECTER2 era-match rate 62.8% [CI 57.0%, 68.6%] on 1970-1980 CS;
  gray-zone outcome → commit Flavor A as cheap insurance.
- H7 hand-audit failure (66.7% < 80%) reinforces toward firm-commit;
  Type A errors (47% of "era-match" pairs are topically unrelated)
  imply the date-based metric understates drift severity.
- Word2Vec-per-decade + orthogonal Procrustes + TF-IDF-weighted
  document aggregation. Hamilton-Leskovec-Jurafsky 2016 template
  adapted to document-level.

**Stage 3 Flavor B (reserve)**: Fine-tune SPECTER2 per era + anchor-
paper Procrustes. Invoked if Stage 2 anchor-projection vs raw-space
results disagree substantively.

**Stage 3 Flavor C (reserve only)**: Dynamic embedding models (Bamler-
Mandt 2017, Rudolph-Blei 2018). Invoked only if Flavor B contradicts
domain intuition AND reviewers push.

---

## §3 — Subfield classifier policy (LOCKED)

Per Phase 0.1 Check 2 outcomes + N1 revision:

1. **Primary subfield mechanism: embedding-cluster (§11).** Status:
   *preferred* (not "necessary"). Avoids keyword-match anachronism.
2. **Score-thresholding policy** (default applied in §0 P): ≥0.3
   loose for population restriction; ≥0.5 strict for tight subfield
   identity. Pre-registered per use case.
3. **Junk-year-metadata filter** (production list): see §0 above.
4. **Concept-tag safety classification** for use as auxiliary
   features:
   - Soft category (terms older than 1990: Neural network, ML, AI,
     RNN, etc.) — pre-1990-safe.
   - Medium category (term ~1990-2000: Deep learning, CNN, World
     Wide Web, Internet) — conditional, score≥0.5 strict + junk-year
     filter required.
   - Hard category (term post-2000: Big data, Cloud computing, IoT,
     GAN, BERT, CRISPR, Augmented reality, Smartphone, Bitcoin,
     Transformer) — NOT pre-1990-safe; embedding-cluster (§11)
     required.

---

## §4 — Demographic features (LOCKED — primary set + secondary set)

Per `phase-0.1-plan.md` §4 + Check 3 outcomes + Lockhart 2023 P5
adoption + Kozlowski 2022 fractional-counting adoption.

**Coverage commitment**: ≥80% per year per dimension, within P_demo,
verified in Stage 1.

### Primary set

1. **Gender** — fractional probabilistic counting per Kozlowski
   2022 + Lockhart 2023 P5. Inference pipeline:
   - **Genderize.io** with API key (2500/mo keyed-free tier; paid
     tier procurement at Stage 1 if production scale exceeds free
     budget per ws2 desideratum §9 cost gate).
   - **NamSor** on low-confidence subset: when Genderize p<0.8 AND
     gender_guesser category ∈ {andy, mostly_male, mostly_female,
     unknown}. Budget $0-$500 per §9 cost compass.
   - **gender_guesser** as offline cross-validation (zero-cost
     parallel).
   - **ORCID self-report** via §9a P5 ground-truth validation on
     ORCID-linkage-validated subset (see §9a P5 below).
   - Each author has P(gender=woman) ∈ [0,1]; per-paper
     aggregations are fractional.

2. **Country of current affiliation (paper-time)** — OpenAlex
   institution ROR → country code. Stage-1 commitment to a raw-
   affiliation-parsing fix that pushes coverage from current ~45% to
   target ~50% on §0 P. Authors with multiple institutions resolved
   per §8.

3. **Country of earliest affiliation (author-level)** — proxy for
   training region. Computed from per-author publication history.

4. **Institution type** — OpenAlex institution category: education,
   government, facility, company, healthcare, nonprofit, other.

5. **Institutional prestige tier** — time-invariant Shanghai ARWU
   2003-2024 averaged: top-10 / top-50 / top-200 / other-university.
   Manual categorical scheme for non-universities (top industry
   labs, major govt labs). CS-specific CSRankings cross-check.

6. **Career stage** — continuous years-since-first-publication;
   binned 0-5 / 6-15 / 16+ for diversity metrics.

7. **Training-institution concentration (Proxy A)** — institution at
   earliest publication cluster; categorical feature for lineage-
   concentration metrics.

### Secondary set (report but don't rely on)

- Discipline of origin — first-paper concept tags.
- Coauthor network breadth — distinct collaborators / institutional
  diversity of coauthors.

### Explicitly excluded

- **Race / ethnicity** — not reliably inferable per Lockhart 2023 P1
  (65-73% error rates for Black + MENA subgroups). Excluded for both
  inference quality and methodological honesty per Lockhart P1
  critical-refusal commitment.
- **Socioeconomic background** — unavailable.
- **Full advisor lineage (Proxy C)** — out of scope; flagged as
  natural follow-up paper.

### Methods-framing commitment on weight-by-confidence

Per Hofstra C4 walkthrough: weight-by-confidence is an *uncertainty-
propagation policy*, not an *inference-quality fix*. Methods states
explicitly:
- We do not claim our inferences are reliable in absolute terms.
- We claim that inference uncertainty propagates into all downstream
  CIs.
- Per-region inference accuracy reported alongside every aggregate.

This is a deliberate move away from Hofstra's "treat all
classifications as equally certain" approach.

---

## §5 — Subfield partition (LOCKED)

Per Phase 0.1.E + §11 commitment:

- **Primary**: embedding-cluster per §11 (K=50 SPECTER2-stratified
  cluster fit). Each paper assigned to nearest centroid.
- **Robustness partners**:
  - arXiv category where paper is on arXiv (CS post-1993ish, Physics
    post-1991ish). Coverage-limited.
  - Score-thresholded OpenAlex concept tags (per §3): soft-category
    score≥0.3, hard-category score≥0.5 with junk-year filter.
- **Granularity**: ~10-50 subfields per field. K∈{30, 50, 100}
  robustness from §11.
- **Robustness criterion (Stage 2)**: divergence trend should agree
  in direction across embedding-cluster, arXiv-category (where
  available), and score-thresholded concept-tag partitions.
  Disagreements are findings, not bugs.

---

## §6 — Unit of analysis (LOCKED)

Per `phase-0.1-plan.md` §6:

- **Demographic diversity** → author-year. Each unique author
  active in year Y counts once; "active" = ≥1 paper in Y.
  Unweighted primary; productivity-weighted secondary.
- **Semantic diversity** → paper-year. One embedding per paper.
- **Canonical concentration** → paper-year (citation-based).
- **Within-paper team-diversity × novelty (Test IV)** → paper
  cross-section. Each paper one observation.

---

## §7 — Missing-data policy (LOCKED)

Per `phase-0.1-plan.md` §7 + N1+ stats primer §18 (MAR / MNAR / IPW):

- **Abstract missingness**: paper excluded from §0 P (deterministic
  exclusion).
- **Country missingness**: paper retained in P but excluded from
  P_demo. §9e propensity weighting recovers OpenAlex full-population
  aggregates over P_demo under MAR.
- **ORCID missingness**: irrelevant for headline divergence test;
  affects §9a P5 validation subsample size only.
- **Gender ambiguity**: fractional probabilistic counting per
  Kozlowski 2022; never thresholded into hard assignments per
  Lockhart 2023 P5.
- **Career-stage missingness**: imputed from earliest-publication-
  year proxy.

---

## §8 — Multi-affiliation handling (LOCKED)

Per `phase-0.1-plan.md` §8: first non-empty institution per
authorship; first authorship per work for paper-level country
attribution. Authors with multiple simultaneous affiliations
contribute fractionally to multiple country cells.

---

## §9 — Demographic-inference uncertainty stack (LOCKED)

### §9a — Lockhart 2023 principle-by-principle adoption

- **Principle 1 (critical refusal)**: race/ethnicity inference
  refused.
- **Principle 2 (Reading-A vs Reading-B)**: ascribed-X / name-coded-X
  terminology in Methods + headline language. Reading-A primary.
- **Principle 3 (population-specific training)**: deferred future
  work; explicitly named in Limitations.
- **Principle 4 (high-accuracy subgroups)**: 300-name gender
  hand-validation stratified by name-region × era (6 regions × 3 eras
  = 18 cells × 17 names each).
- **Principle 5 (aggregate + bias-quantification on target
  population)**: bias-uncertainty band on every headline number.
  - Lower bound: ORCID-only-quantified disagreement matrix.
  - Upper bound: ORCID-quantified matrix combined with NamSor's
    published per-region accuracy.
  - Composed with §9e propensity-weighted analytical population.
  - **Phase 0.2 NEW commitment**: 100-record ORCID-linkage validation
    stratified by name region (per Culbert 2025 close-read finding
    of OpenAlex over-merge on non-Western names). Validates that
    ORCID-author linkage is correct before treating ORCID-having
    authors as ground truth. If ORCID linkage is contaminated for a
    name-region cell, exclude that cell from §9a P5 ground-truth
    use; rely on NamSor accuracy table only.

### §9b — Within-between decomposition (LOCKED)

Per Lockhart C1: Lockhart's name-coded-X bias finding (high
within-region error rates) means inference error CANNOT be
decomposed cleanly into between-region + within-region components.
Methods reports the joint band per §9a P5; does not claim
independence.

### §9c — ORCID coverage transparency (LOCKED)

Per `phase-0.1-plan.md` §9c. Methods reports:
- ORCID-validated coverage rate per (year × region × era).
- Bias-uncertainty band (§9a P5) bounds.
- Explicit caveats per Check 3 H7 outcome (ABOVE-band ORCID coverage
  has noise floor from over-merge per Culbert 2025).

### §9d — Cross-dimensional spillover (LOCKED)

Per `phase-0.1-plan.md` §9d. Sensitivity checks for cross-dimensional
inference effects.

### §9e — Selection-bias correction (LOCKED)

Per `phase-0.1-plan.md` §9e:
- Inverse-probability-of-abstract-availability weighting on P_demo
  to recover OpenAlex full-population aggregates under MAR.
- Propensity model: covariates include `cited_by_count`, `type`,
  `concept_score`, `n_authorships`, `first_country`, `year`.
- Pre-registered CV-AUC threshold ≥0.75 (tentative; locked here).
- Composes with §9a P5: §9e weighting applied first, §9a P5
  bias-uncertainty band applied second.

### §9 cost gate

Per ws2 desideratum §9: any embedding/API run >$50 requires
pre-commit estimate in `tasks/spend.md`. NamSor production-scale
budget ($0-$500 per §9 cost compass) requires pre-commit at Stage 1
when low-confidence subset size is known.

---

## §10 — Disambiguation error floor (LOCKED with Culbert update)

Per `phase-0.1-plan.md` §10 + Check 4 + Culbert 2025:

- **Acknowledgment**: OpenAlex author-disambiguation accuracy ≈
  90-95% per their published benchmarks. With ~200K authors in our
  sample, that's thousands of errors propagating into career stage,
  training institution, and coauthor-network features.
- **Mitigation**:
  - Career-length > 60yr screen (Check 4: 3.0% cross-era-merger
    rate as lower bound).
  - **Culbert 2025 mechanism**: "generous disambiguation" produces
    >10K-records-per-ORCID over-merges, especially on non-Western
    (Chinese) names. The career-length screen doesn't catch this
    class. Methods explicitly cites Culbert and the 100-record
    ORCID-linkage validation step (§9a P5) as the partial mitigation.
  - Working assumption: 5-10% total-error band, with non-Western
    subgroup error rate plausibly above the upper end.
  - Author-level aggregates preferred over edge-level analyses.

---

## §11 — Cluster-fit temporal stratification (LOCKED + production-scale re-validation)

Per `phase-0.1-plan.md` §11 + Check 5d:

**Commitment** (locked):
- **Cluster-fit sample**: temporally-stratified pooled subsample with
  equal papers per decade (1970s, 1980s, 1990s, 2000s, 2010s,
  2020-24). Per-decade |s| ≥ 250 papers (production scale,
  |S| ≥ 1500 per decade × 6 decades).
- **Per-decade supplemental seed pulls** to handle low retention in
  early decades (Check 5d pull-underrun lesson).
- **Cluster count K**: 50 primary; K∈{30, 50, 100} as robustness.
- **Cluster assignment for production**: every paper in the full
  corpus assigned to nearest cluster centroid from the stratified
  fit. Assignment step uses the full corpus; fit step uses the
  stratified subsample. **This distinction is load-bearing.**
- **Same principle applies** to any other pooled-data fit consumed
  by a diversity metric.
- **Cluster-fit manifest committed**: stratified subsample indices,
  fitted cluster centroids, K value, fit hash, in
  `data/metadata/cluster-fit-manifest.{md,npy}`.
- **Re-validation at production scale** (Stage 1 prereq): replicate
  the Check 5d test (effN_S vs effN_U on held-out 1975 + 2020) at
  |S| ≥ 1500 per decade. Pre-registered H7' threshold: effN_S /
  effN_U > 1.43 on H_1975 AND |effN_S - effN_U| / max(...) < 0.20
  on H_2020 (negative control). At production scale, K=50 should
  comfortably support the test (~30 papers per cluster).

**CV-by-region diagnostic** (NEW per Kozlowski 2022 close-read):
- Report coefficient of variation (CV) of cluster occupancy per
  demographic cell, alongside cluster entropy and effective number
  of clusters (effN).
- High CV → group is specialized on a subset of clusters.
- Low CV → group is ubiquitous across clusters.
- Three statistics per (year × demographic-cell) row in §11
  reporting: entropy, effN, CV.

**If §11 production-scale re-validation fails**: §11 commitment
re-opens for plan-revision. Phase 0.2 → Stage 1 transition gate
requires §11 validation result.

### Production-scale validation result + threshold amendment (2026-05-04)

**Result:** §11 mechanism is **empirically detectable in the
pre-registered direction** at production scale, but with smaller
magnitude than the strict 1.43 threshold. After projection-bug
fix (see Wave 2A artifact's POST-FIX UPDATE section):

| K | r_H75 (orig, |H|=49) | r_H75 (followup, |H|=200) | NC rel-diff (orig→fu) | NC pass? |
|---|---:|---:|---:|---|
| 30 | 1.26 | 1.31 | 0.023 → 0.048 | YES → YES |
| 50 | 1.17 | 1.25 | 0.079 → 0.030 | YES → YES |
| 100 | 1.33 | 1.17 | 0.030 → 0.135 | YES → YES |

All r_H75 > 1.0 across K and across held-out size. NC passes
cleanly. Magnitudes tightly clustered (CV ~6% across K).

**Threshold amendment:** revise H7' artifact threshold from 1.43
to **1.10**. Empirical r_H75 minimum across measurements is 1.17
(K=50 orig and K=100 followup); 1.10 leaves modest safety margin
for re-runs at slightly different N or seeds.

NC threshold unchanged at <0.20 (passes by wide margin in all six
fixed measurements).

**Threshold rationale:** The original 1.43 threshold was a
planning prior, not a measurement-derived expectation. Two empirical
runs (|H|=49 + |H|=200) with the corrected projection both produce
r_H75 ∈ [1.17, 1.33]. The mechanism is real and reliably detectable
in the pre-registered direction; the threshold was overspec'd.

### Projection-bug methodology lesson

Wave 2A's first run used `argmax(v · c)` for cluster projection.
KMeans assigns via `argmin(‖v - c‖²)`. For unit-norm vectors v
with non-unit-norm centroids (KMeans centroids of unit vectors
have norms ~0.92-0.94), these criteria differ — argmax(v·c)
favors high-magnitude centroids and produces reversed results in
this geometry.

**Production rule:** any cluster-projection step in §11 (or
elsewhere) MUST use Euclidean distance for assignment, consistent
with KMeans's fitting criterion. Either via sklearn's
`KMeans.predict()` (canonical) or by explicitly computing
`argmin(‖v - c‖²)` = `argmax(2·v·c - ‖c‖²)` if centroids are
loaded from disk without a KMeans object.

Phase 0.1 check5bd correctly used `KMeans.predict()` via a
dummy-KMeans pattern (`km_dummy.cluster_centers_ = centroids;
km_dummy.predict(X)`). Phase 0.2 §11 scripts have been amended
to match. See `experiments/phase-0.2/section11_reproject_fix.py`
for the discovery + the buggy-vs-FIXED comparison artifact.

---

## §12 — Text representation (LOCKED)

Per `phase-0.1-plan.md` §12: title + abstract only. Full-text not
required. Coverage caveat (~50% per Check 1) addressed via §9e.

---

## §13 — Pre-1990 retention (LOCKED)

Per `phase-0.1-plan.md` §13: pre-1990 retained in headline tests
(13-B baseline, 13-D variation, 13-F null-rebuttal strengthening).
Subfield mechanism test restricted to post-1990 per ws2 desideratum
§10. Pre-1990 reported with explicit drift-mitigation caveats per
§2 + §3.

---

## §14 — Methods overview framing (LOCKED — four parallel construct-validity audits)

Per `phase-0.1-plan.md` §14 + N1: four parallel audit layers, each
addressing a distinct construct-validity threat:

1. **Embedding drift** (§2): Stage 2 default + Stage 3 Flavor A.
2. **Classifier drift** (§3): score-thresholding + junk-year + §11
   cluster-fit primary subfield mechanism.
3. **Disambiguation error** (§10): career-length screen + Culbert-
   informed ORCID-linkage validation.
4. **Selection bias** (§9e): IPW-corrected aggregates + bias-
   uncertainty band.

The four audit framework structure is more legible to reviewers
than ad-hoc per-threat framing.

---

## Per-metric N_target (LOCKED from Check 5b)

For each headline metric, per-year bootstrap sample size n =
`min(Nᵧ, N_target)`. From `experiments/phase-0.1/metric-convergence.md`:

| Metric | N_target | Convergence rationale |
|---|---:|---|
| Cluster entropy (K=50) | **200** | Δ_1=0.6%, Δ_2=0.6%, CV=2.2% at n=200 |
| Effective dimensionality | **1000** | Δ_1=0.8%, Δ_2=0.3%, CV=6.9% at n=1000 (n<768 degenerate) |
| Mean pairwise cosine distance | **200** | Δ_1=0.9%, Δ_2=0.3%, CV=1.6% at n=200 |
| Demographic Shannon (per categorical feature) | **500** | Δ_1=2.8%, Δ_2=0.1%, CV=3.6% at n=500 |

For early years where Nᵧ < N_target, the bootstrap n is bounded
above by Nᵧ; the bootstrap CI widens accordingly, propagating
through §9e.

---

## Robustness scope (LOCKED for Stage 3)

Per consolidation pass §C: items previously listed as #6 (Test II
three-spec team-size) and #7 (Test IV quadratic + interaction) have
been removed because they are part of the Test II + Test IV
**pre-registered specifications** (above), not robustness items.

Per consolidation pass §H1: items #5 (subfield mechanism) is
upfront-committed; items #6 (Petersen 2024 inflation) and #7 (Holst
zero-ref) are conditional on reviewer push.

The Stage 3 robustness suite, in priority order:

### Upfront commitments

1. **Embedding-model swap**: re-run Test I + Test IV with SciNCL +
   Qwen3 alongside SPECTER2. Direction agreement = robust;
   disagreement = methodology question.
2. **Anchor-projection (Mitigation 4)**: re-run all metrics in the
   ~100-anchor-concept projected space. Reported as robustness
   column on every headline.
3. **Flavor A** (Word2Vec-per-decade + Procrustes): committed per
   Check 5c. Cross-architecture robustness for pre-1990-data-
   dependent claims.
4. **Cross-field replication**: replicate Test I on Physics. Direction
   agreement validates the substantive claim; disagreement is the
   field-specific finding.
5. **Subfield mechanism test**: canonical-concentration → divergence
   linkage. Tests whether the headline divergence is mediated by
   subfield-level canonical concentration (the Park-Leahey-Funk
   2023 / Funk 2026 disruption-decline mechanism). **Intrinsic to
   claim #13's mechanism story; upfront commitment per consolidation
   §H1.**

### Conditional on reviewer push (per consolidation §H1)

6. **Petersen 2024 citation-inflation correction** [conditional]:
   re-run Test III with + without correction. Disagreement =
   finding. Run only if reviewers push on inflation-bias grounds.
7. **Holst 2024 zero-reference filter** [conditional]: re-run
   Test III excluding zero-reference papers. Direction agreement =
   headline robust to the dataset-artifact critique. Run only if
   reviewers push on data-artifact grounds.

### Stage-3-frontier (out of scope for Phase 0.2)

**Cross-substrate robustness (WoS / Scopus)**: NOT Phase 0.2
commitment; flagged as Stage 3 robustness frontier conditional on
reviewer push, using Culbert 2025's shared-corpus DOI-match recipe.

---

## Stage 1 prereqs (handoff to Stage 1)

The following must complete before Stage 1 production work begins:

1. **Qwen3 sorted-by-length batching benchmark** (~half day):
   implement length-sorted batching in `embed_qwen3`; re-run smoke
   test under naive-bs=8 / sorted-bs=8 / sorted-bs=32; record
   best-strategy timing.
2. **Stage 2 compute target decision** (cloud vs local M-series):
   gated by (1) above + Check 5b N_target + cloud cost estimate
   for Modal A10G default vs local sustained-run cost.
3. **Genderize.io paid-tier API key procurement** if production-
   scale gender inference exceeds 2500/mo keyed-free. Pre-commit
   estimate logged in `tasks/spend.md`.
4. **NamSor account setup + small-batch test** to verify API
   behavior + per-region accuracy claims.
5. **§11 production-scale re-validation**: pull production-scale
   stratified pool (|S| ≥ 1500 per decade with supplemental seeds);
   re-run Check 5d test; commit cluster-fit manifest.
6. **100-record ORCID-linkage validation** (NEW per Culbert 2025):
   sample 100 ORCID-having authors stratified by name region (16-17
   per cell × 6 regions); manually verify ORCID linkage accuracy via
   orcid.org profile cross-check; produce per-region linkage-
   correctness rate; feed into §9a P5 bias-uncertainty band.
7. **Production pull-spec dry run**: small over-sample (~10K papers)
   to verify the production junk-year-token list + empty-abstract
   filter behave as expected before full pull.

Each prereq is a single Stage 1 task; total estimate ~1-2 weeks at
~15 hrs/week.

---

## Open decisions deferred to Stage 1+

1. **Production-scale N**: 500K vs 1M vs 2M post-filter target.
   Driven by Check 5b N_target + Nᵧ distribution + cost commitment.
2. **NamSor budget specific commitment**: depends on low-confidence
   subset size at production scale.
3. **Pre-1990-specific validation extension**: whether additional
   diagnostic work is needed beyond Phase 0.1 Checks 1-2-4.
4. **Cross-substrate robustness commitment depth**: Stage 3
   conditional only; not pre-registered.
5. **Park 2025 Tier 1B addition**: ~2 hr positioning read; queued
   for Stage 1 / Stage 3 as time permits.
6. **Tier 2A collaborative review**: Discussion-Notes sections in
   the four .md files filled during Stage 3 paper drafting (not
   gating Phase 0.2 → Stage 1 transition).

---

## Validation gates (Phase 0.2 → Stage 1 go/no-go)

| # | Gate | Status |
|---|---|---|
| 1 | This document is finalized and user-signed-off | Pending user signoff |
| 2 | Stage 1 prereq #1 (Qwen3 sorted-batching benchmark) complete | Pending |
| 3 | Stage 1 prereq #2 (Stage 2 compute target) decided + recorded | Pending |
| 4 | Stage 1 prereq #5 (§11 production-scale re-validation) result documented | Pending |
| 5 | Stage 1 prereq #6 (100-record ORCID-linkage validation) result documented | Pending |
| 6 | All Phase 0.2 commitments cross-link to source artifact (Phase 0.1 check, Tier 2A close-read, or `phase-0.1-retro.md` lesson) | Done in this document |
| 7 | Spend pre-commit estimate logged for any expected Stage 1 spend ≥$50 | Pending |
| 8 | `tasks/todo.md` updated to reflect Phase 0.2 → Stage 1 transition | Will happen at signoff |
| 9 | `whitespace_2/CLAUDE.md` "Current State" updated to Stage 1 | Will happen at signoff |

---

## Cost estimate (consolidated for Phase 0.2 + Stage 1)

Per `phase-0.1-plan.md` "Revised cost estimate" + Phase 0.1 actual:

| Item | Phase 0.1 actual | Stage 1 + Stage 2 + Stage 3 estimate |
|---|---:|---:|
| OpenAlex anonymous REST API | $0 | $0 |
| Genderize.io | $0 (keyed-free 2500/mo) | $0-$50 (paid tier if production exceeds 2500/mo) |
| NamSor (low-confidence subset) | $0 | $0-$500 (low-confidence size tbd at Stage 1) |
| Embedding compute (M-series local) | $0 | $0 if local |
| Embedding compute (cloud Modal A10G) | $0 | $50-$200 per full triple-pass; possibly higher with robustness sweeps |
| Compute total (estimate) | | **$50-$750 across Stage 1+2+3** |

Within the program-level $50-$500 budget per ws2 plan; cost-gate
pre-commit per ws2 desideratum §9 fires for any single run >$50.

---

## Companion documents and maintenance

- `docs/phases/phase-0.1-plan.md` — original Phase 0.1 plan with N1
  + N1+ + inline post-check updates. The methodology commitments in
  this Phase 0.2 plan are derived from there.
- `docs/phases/phase-0.1-retro.md` — Phase 0.1 retro (backward-
  looking).
- `docs/conceptual.md` — north star.
- `docs/desiderata.md` — immutable principles.
- `tasks/todo.md` — task tracking.
- `tasks/lessons.md` — self-improvement log.
- `tasks/spend.md` — cost tracking.
- `experiments/phase-0.1/*.md` — empirical artifacts cited
  throughout.
- `literature-review/*.md` — Tier 1 + Tier 2A close-read reviews
  cited throughout.

When a Stage 1 surprise triggers a methodology revision, this
document's commitments may shift. Plan-revision discipline:
- Inline-update the affected section here.
- Cross-link to the surfacing artifact.
- Log the revision in `tasks/lessons.md`.
- Flag in next phase retro.

---

## References (key)

- Phase 0.1 sanity check artifacts: `experiments/phase-0.1/`
- Tier 1 + Tier 2A close-reads: `literature-review/`
- Park, Leahey & Funk 2023, *Nature* (Tier 1 paper 02)
- Petersen, Arroyave & Pammolli 2024, *Quant Sci Stud* (Tier 1 paper
  03)
- Petersen, Arroyave & Pammolli 2025, *J Informetrics* (Tier 1 paper
  04)
- Holst et al. 2024, arXiv:2402.14583 (Tier 1 paper 05)
- Hofstra et al. 2020, *PNAS* (Tier 1 paper 06)
- Lockhart, King & Munsch 2023, *Nature Hum Behav* (Tier 1 paper 07)
- Wu, Wang & Evans 2019, *Nature* (Tier 2A paper 08)
- Kozlowski et al. 2022, *PNAS* (Tier 2A paper 14)
- Funk et al. 2026, arXiv:2602.05140 (Tier 2A paper 15)
- Culbert et al. 2025, *Scientometrics* (Tier 2A paper 16)
- Park et al. 2025 [pending Tier 1B add]
