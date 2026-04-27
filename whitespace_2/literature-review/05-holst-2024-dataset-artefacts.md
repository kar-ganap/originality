# 05 — Dataset Artefacts are the Hidden Drivers of the Declining Disruptiveness in Science

**Authors:** Vincent Holst, Andres Algaba, Floriano Tori, Sylvia Wenmackers, Vincent Ginis
**Venue:** arXiv:2402.14583 (preprint, Feb 2024)
**PDF:** `literature-review/05-holst-2024-dataset-artefacts.pdf` (gitignored — main + SI bundled)
**arXiv:** https://arxiv.org/abs/2402.14583

---

## Background

Holst et al. 2024 is the third major critique of PLF 2023, complementing
PAP 2024 (the citation-inflation deductive critique) and PAP 2025
(the team-size empirical re-analysis). Where PAP critiques the
*structural mathematics* of CD-index, Holst critiques the *data
quality* underlying PLF's specific empirical results.

The headline claim: **PLF's reported decline in disruptiveness is
substantially driven by papers/patents with CD_5 = 1 (a degenerate
maximum-disruption value), most of which are dataset artefacts
rather than substantive disruption**. The relative frequency of
these outliers decreases over time, mirroring (and largely
explaining) the apparent disruption decline.

The critique is also a methodological detective story. Holst et al.
discovered:
1. **A seaborn 0.11.2 plotting bug** that silently dropped the
   largest data points from PLF's histograms — hiding 972,161
   papers and 142,362 patents with CD_5 = 1 from PLF's visual
   inspection.
2. The hidden outliers were *included* in PLF's main analysis
   (which uses raw data, not the histograms) — they just couldn't
   *see* them.
3. The CD_5 = 1 outliers are mostly papers/patents with zero
   recorded references — a degenerate case where CD_5 mechanically
   equals 1 by construction (no references means no Type-2
   consolidating citers possible).
4. Hand-checking 100 random samples: 98% of patents and 93% of
   papers in this category *actually do* make references in their
   original PDFs. These are dataset artefacts, not real
   zero-reference works.

For ws2: **this paper validates and extends our existing pre-1990
data-quality tier specification** (desiderata §10, post-1990 default
analysis). Pre-1990 data has more metadata-quality issues; our
restriction protects against a Holst-style artefact. The paper
also gives us a **general framework for thinking about
metric-discontinuities at data-quality boundaries** — applicable
to our C2(b) OpenAlex coverage diagnostic.

This paper is the one we deferred PLF SQ8 to (dataset-artefact
correction implications). The deferred content lives here.

---

## Key Ideas

### 1. The seaborn 0.11.2 plotting bug

A specific, mundane bug discovery: `seaborn 0.11.2` has a bug where
specifying the `binwidth` parameter (rather than `bins`) causes the
library to silently drop the largest data points from histograms.
PLF used `binwidth = 1`, and as a consequence:

- The histograms in PLF's Extended Data Fig. 1 visually appear to
  show CD_5 distributions concentrated near 0 with no significant
  outliers.
- **Hidden:** 972,161 papers and 142,362 patents with CD_5 = 1.
- The hidden outliers represent ~4% of the WoS sample and ~5% of
  the PatentsView sample — substantial.
- The bug was silent — no warning from seaborn, no error, just
  dropped points.

This is a methodologically embarrassing detail but a real
observation. PLF's robustness checks didn't surface this because
the underlying data analyses operated on raw values, not the
histograms.

### 2. The CD_5 = 1 + zero references mechanism

The substantive heart of the critique. CD_5 has a degenerate case
when a paper/patent has zero indexed references:

- B (citers of focal AND its predecessors) = ∅ by definition (no
  predecessors).
- R (citers of predecessors only) = ∅ by definition.
- F (citers of focal only) = however many forward citations.
- CD_5 = (N_F − N_B) / (N_F + N_B + N_R) = N_F / N_F = 1 (whenever
  F is non-empty).

**Whenever a paper has zero references and at least one forward
citation, its CD_5 = 1 exactly.** This is mechanical, not
substantive disruption.

In SciSciNet, 97% of papers with CD_5 = 1 have zero references.
In PatentsView, 78% of patents with CD_5 = 1 have zero references.
The CD_5 = 1 category is dominated by zero-reference cases.

### 3. Why the time trend in CD_5 = 1 frequency is the dataset artefact

The relative frequency of CD_5 = 1 outliers (which are mostly
zero-reference cases) **decreases over time**:

- Pre-1980 papers in WoS frequently have zero recorded references.
- Post-2000 papers almost all have non-zero recorded references.

Why? **Metadata quality improved over time.** Older papers'
reference lists were less consistently digitized; newer papers
have full reference lists indexed.

The implication: as metadata quality improves, the proportion of
papers stuck at the degenerate CD_5 = 1 value decreases. The
average CD_5 mechanically falls. **PLF's reported decline in
disruptiveness is substantially measuring metadata-quality
improvement over time, not declining disruption.**

When CD_5 = 1 outliers are excluded, the decline:
- For papers (WoS): **almost completely disappears.**
- For patents (PatentsView): **substantially reduces** (but
  doesn't fully disappear — patents have other artefacts too).

### 4. Validation: zero references are mostly artefacts, not substantive

Hand-check methodology: Holst et al. randomly sample 100 papers and
100 patents from the CD_5 = 1, zero-references category. Inspect
the original PDFs.

Results:
- **98% of patents** *actually do* make references in their
  original documents — but those references aren't recorded in the
  PatentsView database.
- **93% of papers** *actually do* make references in their original
  documents — but those references aren't recorded in the WoS
  database.

So the "zero references" label is overwhelmingly false. These are
real papers/patents with real reference lists; the references just
aren't in the database. **They should be excluded from analysis as
data-quality artefacts**, not analyzed as if they were genuinely
zero-reference works.

### 5. Why PLF's robustness checks failed

PLF had three types of robustness checks. Holst documents why each
failed to detect the artefact:

**(a) Regression adjustment** (PLF Supplementary Table 1, models 4
and 8). Holst's Fig. 2c, 2d shows that PLF's regression model has a
*discontinuity* at zero references — the regression residuals
(RMSE) peak at zero references, indicating the model fits poorly
there. PLF's linear specification can't capture the discontinuous
effect at exactly zero references.

When Holst extends PLF's regression to include a *zero-references
dummy variable*, the adjusted R² jumps from 0.10 → 0.52 (patents)
and 0.15 → 0.95 (papers). After explicitly controlling for the
zero-references discontinuity, the temporal decline in adjusted
CD_5 is **largely negated** for SciSciNet (papers) and **substantially
reduced** for PatentsView (patents).

**(b) Monte Carlo simulations / random rewiring.** PLF used a
degree-preserving rewiring algorithm to test whether observed CD_5
values are different from random networks with the same degree
structure. Holst's Fig. 2e, 2f shows this rewiring preserves
zero-reference structure by construction (rewiring affects edges,
not nodes' reference counts). So the *same artefact appears in
rewired networks*. The temporal decline in average CD_5 is mirrored
in the rewired networks. **Random rewiring with degree-preservation
can't detect the artefact** because the artefact lives at the node
level (zero references), not the edge level.

**(c) Alternative bibliometric measures** (CD^nok, DI*). These
preserve the same fundamental structure where zero-reference papers
yield maximum-disruption values. Same artefact persists.

The general lesson: **robustness checks must specifically attack
the threat being raised, not just be generic stability checks.**
PLF's checks were generic; they couldn't detect a node-level
data-quality issue because they all operated at the edge level
(rewiring) or used the same metric formulation (alternative CD
variants).

### 6. Cross-dataset validation

Holst's Extended Data Fig. A3 shows the artefact across six data
sources:
- Web of Science (PLF used)
- PatentsView (PLF used)
- JSTOR
- American Physical Society
- Microsoft Academic Graph
- PubMed

Plus DBLP-Citation-network V14 (CS-only, used in SI Section S4).

In every dataset, the same pattern holds:
- The CD_5 = 1 + zero-references category is concentrated in early
  years.
- Removing this category eliminates or substantially reduces the
  apparent disruption decline.

So PLF's "cross-database robustness" finding (replication across 6
databases) doesn't actually demonstrate robustness against the
artefact — it demonstrates that *the same artefact is present in
all 6 databases*, in different magnitudes.

### 7. The discontinuity in CD as a function of references

A subtle technical point that Holst surfaces: CD_5 has a *structural
discontinuity* at zero references. As you move from 1 reference to
0 references, CD_5 jumps to exactly 1 (or becomes undefined if no
forward citations).

This discontinuity is invisible in Holst's Fig. 2a, 2b unless you
examine the regression residuals carefully (Fig. 2c, 2d). **Standard
linear regression specifications can't capture this discontinuity.**
You'd need either:
- A zero-references dummy variable (Holst's fix).
- Explicit exclusion of zero-references cases prior to regression
  (best practice per Holst, p. 3).
- A non-linear specification with discontinuity at zero
  (theoretically possible, not practical).

Many recent science-of-science publications correctly set CD_5 of
zero-reference papers to "non-defined" prior to analysis (Holst
cites SciSciNet, etc.). PLF didn't.

### 8. Best practice: exclude degenerate cases prior to analysis

Holst's specific methodological recommendation:

> "Therefore, it is best practice to exclude zero reference papers
> and patents prior to further analysis. Indeed, many recent
> Science of Science publications set the CD indices of papers
> that make zero references to non-defined." (p. 3)

This generalizes to a broader principle: **identify the degenerate
cases of any metric you're using; exclude them prior to analysis;
acknowledge in Methods that you've done so**. Don't rely on
post-hoc robustness checks to catch what should be a pre-analysis
data-cleaning step.

For ws2: this gives us a specific framework for our own pre-analysis
data filtering. We need to identify degenerate cases of our
metrics and exclude them explicitly.

---

## Results — Three Levels

### Level 1: For a smart high-schooler

Park, Leahey & Funk's 2023 Nature paper claimed scientific
disruptiveness is declining over time. This paper (Holst et al.
2024) says that decline is mostly an artefact — a quirk of how
the data is recorded, not a real change in science.

The story:
- PLF used a metric called CD-index. For papers with zero recorded
  references in the database, CD-index mathematically equals 1
  (the maximum "disruption" value), regardless of whether the
  paper is actually disruptive.
- A bug in their plotting library hid these papers from PLF's
  histograms — they didn't notice them.
- These zero-reference papers are mostly in *old* databases. As
  data quality has improved over time, fewer papers appear with
  zero references.
- So the average CD-index naturally falls over time as fewer
  papers are stuck at the degenerate CD = 1 value.
- When you exclude these papers from the analysis, the apparent
  decline almost completely disappears for scientific papers and
  substantially reduces for patents.
- Hand-checking 100 random samples: 98% of patents and 93% of
  papers labeled "zero references" actually do make references in
  their original PDFs. The references just aren't in the database.

The implication: PLF's "decline of disruption" is largely measuring
how database metadata quality has improved over the decades, not
how science itself has changed.

### Level 2: For a junior/senior undergraduate

The paper makes three independent demonstrations that data-quality
artefacts drive PLF's reported decline:

**(1) Direct exclusion.** Remove papers/patents with CD_5 = 1 from
the analysis. The decline in average CD_5 over time disappears for
WoS papers and substantially reduces for PatentsView patents.

**(2) Regression with zero-references dummy.** Extend PLF's
regression model with an explicit dummy variable for papers/patents
with zero recorded references. The model fit jumps dramatically
(adjusted R² 0.10 → 0.52 for patents, 0.15 → 0.95 for papers),
indicating the dummy captures most of the variation PLF attributed
to year. After this control, the temporal decline in adjusted CD_5
is largely negated.

**(3) Random-rewiring null model.** PLF's Monte Carlo simulations
use degree-preserving random rewiring. But this preserves
zero-reference papers by construction. Holst shows the temporal
decline in CD_5 is mirrored in rewired networks — meaning the
"unexpectedly low CD_5" pattern PLF interpreted as evidence for
disruption decline can be reproduced by random citation behavior
applied to networks containing the same zero-reference outliers.

The substantive mechanism is clear: CD_5 has a structural
discontinuity at zero references (mechanically equals 1). Older
databases have more zero-reference entries due to incomplete
metadata. As metadata quality improves over time, the proportion
of CD_5 = 1 outliers decreases, mechanically lowering the average
CD_5. PLF's robustness checks couldn't detect this because they
all preserve the zero-reference structure.

The recommendation: exclude papers/patents with zero references
prior to CD-index analysis. Acknowledge this in Methods.

This critique combines with PAP 2024's structural critique of
CD-index (citation-inflation in the denominator) to give a complete
picture: CD-index has *both* a structural problem (PAP 2024) *and*
a data-quality problem (Holst 2024). PLF's reported decline reflects
contributions from both, plus possibly some real signal that's hard
to extract.

### Level 3: For an early graduate student

Three methodologically interesting features of this paper worth
deep engagement:

**(1) The dataset-artefact framework as distinct from the
citation-inflation framework.** PAP 2024 attacks CD-index from
the algebraic-structural side (the (1 + R_k) denominator
inflation). Holst attacks from the data-quality side (zero-reference
discontinuity at metric boundary). These are *different* kinds of
critique:
- PAP 2024's critique applies to CD-index *as a metric*, regardless
  of dataset.
- Holst's critique applies to *PLF's specific empirical results*,
  given the WoS / PatentsView dataset's metadata characteristics.
- Both critiques attack the same target (PLF's decline finding) but
  from different angles. Both are necessary to fully diagnose
  what's wrong with PLF.

**(2) The robustness-check-failure analysis is methodologically
important beyond CD-index specifics.** Holst's Fig. 2 shows that
PLF's three robustness checks failed *because each check operates
at a different level than the actual threat*:
- Regression adjustment operates on linear continuous variables;
  can't capture discontinuity at zero references.
- Random rewiring preserves node-level structure (including
  zero-reference status); can't detect node-level data-quality
  issues.
- Alternative metric variants preserve the same denominator
  structure; same discontinuity.

The general lesson: robustness machinery must be tailored to the
specific threat. A generic "let's test if the result is stable"
approach can miss threats that operate at a level the checks don't
target. This applies to ws2: when we propose robustness checks, we
should explicitly list what threats each check targets, not just
verify "the result is stable across this variation."

**(3) The hand-validation methodology (98% / 93% have references
in original PDFs).** This is a small-scale (n=100) but methodologically
clean validation. It establishes that the "zero references" label
is overwhelmingly false in this category. Three observations:
- *Sample size:* 100 is small. The 95% binomial confidence interval
  on "98%" is approximately [93%, 100%]. Solid but not airtight.
- *Generalization:* the validation applies to the specific category
  (CD_5 = 1, zero references). Generalizing to all PLF outliers
  requires an inference step.
- *Causal direction:* the validation establishes that zero references
  are mostly metadata artefacts. It does *not* establish what the
  "real" CD_5 would be if the missing references were filled in.
  Macher et al. 2024 (cited in the paper) does this for patents and
  finds that with corrected references, patent CD_5 actually
  *increases* over time — overturning PLF's direction.

The paper's limitations:

**(a) The 100-paper hand validation is small.** A larger sample or
more sophisticated automated validation could strengthen the claim.

**(b) The critique is empirical (about PLF's specific data) rather
than structural (about CD-index as a metric). The complementary
PAP 2024 critique fills this gap, but Holst alone doesn't address
whether CD-index can ever be used cross-temporally with proper
exclusions.

**(c) The cross-database validation (Extended Data Fig. A3) is good
but has its own limitations.** SciSciNet is derived from MAG;
PubMed shares lineage with other indices; "independent" datasets
share underlying source material in ways that aren't fully
disentangled.

---

## Connection to Our Project

### What ws2 takes from Holst 2024

**(1) Validation of our pre-1990 data-quality tier specification.**
We've already committed (desiderata §10) to post-1990 default
analysis with pre-1985 preliminary and pre-1990 with disclaimer.
Holst's findings strongly validate this design choice. The
pre-1990 era is exactly where dataset-quality issues like
zero-reference artefacts are most concentrated. **Our existing
pre-1990 caution is methodologically vindicated.**

**(2) "Identify degenerate cases prior to analysis" lesson.** Holst
recommends (p. 3): "it is best practice to exclude zero reference
papers and patents prior to further analysis." For ws2, this
translates to identifying degenerate cases of our metrics:

- *Spearman top-N:* what's a degenerate case? A paper with zero
  citations cannot be in the top-N. But papers near the rank-N
  threshold with very few citations could be unstable. We've
  already addressed this via the citation-difference-near-threshold
  diagnostic (PAP 2025 C3 commitment).
- *Citation Gini:* what's degenerate? A field-year with extremely
  few papers (e.g., n < 10) could have degenerate Gini values
  (small samples → high variance). Worth pre-registering an
  exclusion threshold for cells with insufficient sample size.
- *Cluster entropy / effective dim / pairwise distance:* what's
  degenerate? A field-year with insufficient paper-coverage to
  fit clusters reliably (e.g., n < some threshold). Worth
  pre-registering.
- *Test IV N_p:* what's degenerate? Papers with insufficient
  references for centroid stability. We've already addressed this
  (papers with <5 citations flagged for robustness-only subset).
- *Test IV T_p:* what's degenerate? Single-author papers (T_p = 0
  by construction) — already explicitly handled as "baseline,
  included as comparison."

**(3) Robustness-check tailoring lesson.** Holst's analysis of why
PLF's robustness checks failed gives us a concrete framework: when
we propose any robustness check for ws2, **explicitly enumerate
what threat the check targets, and verify the check operates at the
level where the threat lives**. Generic "stability across variations"
is insufficient. This applies to all our existing robustness
commitments.

**(4) Specific methodological tactic: dummy-variable controls for
discontinuous effects.** Holst extends PLF's regression with a
zero-references dummy and gets dramatic R² improvement. The general
move: when a covariate has discontinuous effects (regime change at
specific values), include explicit dummies for those discontinuity
points.

For ws2, this could apply to:
- *Pre-1990 vs. post-1990 dummy* in our gap regression — we already
  have year-FE which absorbs this, but a specific pre-1990 dummy
  could test whether pre-1990 era contributes systematically
  different signal.
- *Single-author vs. team paper dummy* in Test IV — captures the
  T_p = 0 boundary case.

These are small refinements rather than major design changes.

### What ws2 explicitly does NOT take from Holst 2024

**(1) Direct application of zero-references exclusion.** Our metrics
are not CD-index-based. The specific zero-references discontinuity
doesn't apply to Spearman top-N, Gini, cluster entropy, etc.
(though analogous degenerate cases might exist for our metrics).

**(2) The seaborn plotting bug story.** Cute methodological-detective
narrative; not directly relevant to ws2.

**(3) The hand-validation methodology.** ws2's metrics are aggregate
(field-year level) rather than per-paper. A "hand-validation of
100 random samples" doesn't translate cleanly. We use other
diagnostic strategies.

### Specific design implications for ws2

These are mostly extensions or validations of existing commitments:

- **Reaffirms post-1990 data-quality tier specification** (already
  in desiderata §10). Holst validates this design choice; no
  refinement needed.
- **Add pre-registered exclusion of degenerate cases for ws2
  metrics.** Phase 0.2 batch addition: per-metric list of
  degenerate cases excluded prior to analysis, with justification.
  Parallel to Holst's "exclude zero references" recommendation.
- **Refines C2(b) OpenAlex coverage diagnostic.** Holst's framework
  explicitly looks for discontinuities at metadata-quality
  boundaries. Our existing diagnostic (per-decade coverage rate
  by region) should also examine whether metric values show
  discontinuities at coverage-quality thresholds. Phase 0.2
  refinement.
- **Refines robustness-check rationales.** When pre-registering
  any ws2 robustness check, explicitly state what threat it
  targets and at what level it operates. Parallel to Holst's
  "PLF's checks failed because they were at the wrong level"
  diagnosis.

### How ws2 cites Holst in (c-prime) framing

Holst is the third paper in our critique chain (PAP 2024 + PAP 2025
+ Holst). The citation strategy under (c-prime) inflation-immune
evidence framing:

> "Our (c-prime) framing rests on three complementary critiques of
> PLF's CD-index methodology: PAP 2024 (deductive structural critique
> on citation inflation), PAP 2025 (empirical re-analysis on
> team-size dynamics), and Holst 2024 (data-quality artefact
> critique). Together, these establish that PLF's reported decline
> reflects a combination of metric-structural inflation, omitted-
> variable bias, and dataset-quality artefacts — leaving the
> underlying empirical claim about disruption substantially
> contested. ws2's metrics are immune to all three critique
> pathways by construction."

This is the cleanest framing now that all three pieces of the
critique chain have been engaged.

---

## Key Quotes

For Methods / Discussion of the ws2 paper:

> "Our reanalysis shows that the reported decline in disruptiveness
> can be attributed to a relative decline of these database entries
> with zero references." (Abstract.)

> "Most of these papers and patents correspond to erroneous database
> entries. The curves showing how average CD indices have evolved,
> plotted in Park et al. [1], therefore, do not track declining
> disruption of scientific and technological work, but rather trace
> how metadata quality has increased over time." (p. 3 — the
> headline diagnosis.)

> "Therefore, it is best practice to exclude zero reference papers
> and patents prior to further analysis. Indeed, many recent Science
> of Science publications set the CD indices of papers that make
> zero references to non-defined." (p. 3 — the methodological
> recommendation.)

> "Adding a dummy variable for zero references substantially
> improves the model fit as depicted by the adjusted R², while a
> similar effect is not found for any other number of references."
> (p. 5 — diagnostic-of-discontinuity-via-residual-pattern lesson.)

> "We find that 98% of the patent sample and 93% of the paper sample
> do make references in their original PDF, indicating that most of
> the CD_5 = 1 patents and papers with zero references should be
> treated as artefacts of the respective data sources rather than
> meaningful indicators of disruptive science and technology." (p. 3
> — the hand-validation result.)

---

## Study Questions

(Focused set per the dataset-artefact-specific scope.)

**Warm-up (Level 1):**

1. **SQ1** — Why does CD_5 mechanically equal 1 for papers/patents
   with zero recorded references? Walk through the formula.

2. **SQ2** — The seaborn 0.11.2 bug silently dropped the largest
   data points from PLF's histograms. Why didn't this affect PLF's
   regression results, only their visual inspection?

**Intermediate (Level 2):**

3. **SQ3** — The relative frequency of CD_5 = 1 outliers decreases
   over time. Why does this mechanically produce a declining
   average CD_5 over time, even if no real disruption decline
   exists?

4. **SQ4** — Holst's hand-validation: 98% of patents and 93% of
   papers in the CD_5 = 1, zero-references category actually do
   make references in their original PDFs. What confidence
   intervals can we place on these percentages, and what does it
   imply for the population-level claim?

5. **SQ5** — Holst's regression-with-dummy approach: adjusted R²
   jumps from 0.10 → 0.52 for patents, 0.15 → 0.95 for papers
   when zero-references dummy is added. What does this dramatic
   jump tell us about PLF's original specification?

**Advanced (Level 3):**

6. **SQ6** — Holst's critique is empirical (specific to PLF's
   dataset) while PAP 2024's is structural (about CD as a metric).
   Are these critiques complementary, redundant, or potentially
   conflicting? What does the conjunction prove that neither alone
   does?

7. **SQ7** — PLF's three robustness checks (regression adjustment,
   alternative measures, random rewiring) all failed to detect the
   artefact. Walk through why each failed at the level it operates
   at. What's the general lesson about how to design robustness
   checks?

---

## Challenge Corner

(Focused set, ws2-load-bearing.)

**C1:** Holst's "exclude zero references prior to analysis"
recommendation generalizes to a methodological principle: identify
degenerate cases of any metric and exclude them pre-analysis. For
ws2, what are the degenerate cases of our metrics, and have we
excluded them appropriately?

(a) Walk through each ws2 metric (Spearman top-N, citation Gini,
cluster entropy, effective dim, pairwise distance, T_p, N_p) and
identify its degenerate cases.

(b) Are there degenerate cases we *haven't* explicitly excluded
that we should add to the pre-registered analysis specification?

**C2:** The robustness-check-failure analysis (Holst Fig. 2)
demonstrates that PLF's checks operated at a different level than
the threat. For each ws2 robustness check we've committed to
(detrended correlation diagnostic, multi-Δ Spearman, multi-N
robustness, citation-completeness sensitivity, decoupled-subfield
robustness, etc.), explicitly state what threat it targets and at
what level it operates. Are there threats we've identified but our
existing checks don't operate at the right level for?

**C3:** Holst's hand-validation found 98% / 93% of "zero-reference"
papers/patents actually have references in original PDFs. ws2 uses
OpenAlex, which has different metadata-quality characteristics from
WoS. Is there an analogous validation we could do for ws2's
metric-relevant metadata?

(a) Candidates: hand-validate that papers with abstracts in
OpenAlex actually have abstracts in original sources; hand-validate
that author-affiliations are correctly extracted; hand-validate
that subfield assignments are correct.

(b) Should ws2 commit to any such validation, or rely on existing
OpenAlex validation studies?

**C4:** Holst's critique is data-source-specific (WoS / PatentsView
have these issues) but the lesson generalizes (any database has
metadata-quality issues; identify the discontinuities). For ws2's
OpenAlex-based analysis, what specific metadata-quality concerns
should we anticipate, and how should our Methods/Discussion section
acknowledge them?

**C5:** The cross-database validation (Holst Fig. A3) shows the
artefact is present in all six databases tested, just at different
magnitudes. PLF's "robustness across databases" claim therefore
doesn't actually demonstrate robustness against the artefact. For
ws2's potential cross-substrate Stage 3 robustness check
(WoS-OpenAlex overlap; back-pocket from C3/SQ10 PLF), does this
lesson change how we'd interpret a positive replication result?

---

## Synthesis Pointers (for `synthesis.md`)

1. **Holst is the third critique-chain paper (with PAP 2024 + PAP
   2025).** Cite all three together in (c-prime) framing for the
   strongest possible CD-index critique chain. PAP 2024 is the
   deductive structural critique; PAP 2025 is the empirical
   re-analysis with proper controls; Holst is the data-quality
   artefact critique.

2. **Holst validates ws2's pre-1990 data-quality tier specification.**
   The pre-1990 era is exactly where dataset-quality issues are
   concentrated. Our existing post-1990 default is methodologically
   vindicated.

3. **"Exclude degenerate cases prior to analysis" methodological
   principle.** Generalizes to ws2: identify and exclude degenerate
   cases of each metric. Phase 0.2 batch addition.

4. **Robustness-check-tailoring lesson.** Each robustness check
   should explicitly target a specific threat at the level the
   threat operates. For ws2, when pre-registering robustness
   checks, enumerate threats explicitly. Refinement to existing
   commitments.

5. **Discontinuity-at-boundaries diagnostic.** When a covariate has
   discontinuous effects at specific values (e.g., zero references
   for CD-index), include explicit dummies for those boundaries
   rather than relying on linear specifications.

6. **PLF SQ8 is closed via this paper.** The deferred PLF SQ8
   (dataset-artefact correction implications) is fully addressed
   through Holst's analysis. ws2's commitment from PLF SQ8
   (citation-completeness sensitivity row in measurement-robustness
   appendix) remains as the operational handling.

7. **The cross-database "robustness" lesson is methodologically
   subtle.** Replication across six databases doesn't establish
   robustness if the same artefact is present in all six. ws2's
   own back-pocket cross-substrate robustness check (WoS-OpenAlex
   overlap) needs careful interpretation per Holst's critique
   pattern.

8. **Macher et al. 2024 is mentioned but not included in our
   reading list.** They corrected for missing patent citations and
   found that patent CD_5 actually *increases* over time. If we
   want a fourth piece of the critique chain (focused on patents),
   we could add Macher; otherwise the critique chain is complete
   with Holst. **Decision: don't add; Holst + PAP 2024 + PAP 2025
   is sufficient for ws2 positioning.**

---

## Discussion Notes

(Filled during collaborative review session. Blank until that
session happens.)

### On C1 — degenerate cases of ws2 metrics

(Pending.)

### On C2 — robustness-check threat-level analysis for ws2

(Pending.)

### On C3 — analogous hand-validation for ws2

(Pending.)

### On C4 — OpenAlex-specific metadata-quality concerns

(Pending.)

### On C5 — cross-substrate robustness interpretation

(Pending.)

---

## Study Question Walkthroughs

### SQ1 — Why CD_5 = 1 for zero-reference papers

(Pending.)

### SQ2 — Why seaborn bug didn't affect PLF's regression

(Pending.)

### SQ3 — Mechanical decline from CD_5 = 1 frequency change

(Pending.)

### SQ4 — Confidence intervals on hand-validation percentages

(Pending.)

### SQ5 — R² jump as evidence of misspecification

(Pending.)

### SQ6 — Empirical vs. structural critique complementarity

(Pending.)

### SQ7 — Robustness-check-failure level analysis

(Pending.)
