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

For ws2: **this paper validates ws2's drift-mitigation approach to
pre-1990 data** (Phase 0.1 §13 non-negotiable retention policy
backed by drift-mitigation ladder + per-1990 robustness row in
pooled appendix), rather than mandating clipping. Tests I-III
span 1970–2024 with pre-1990 retained per the §13 substantive
rationale (13-B baseline, 13-D variation, 13-F null-rebuttal
strengthening). Only the *subfield mechanism test* is restricted
to post-1990 per desiderata §10. The Holst paper also gives us a
**general framework for thinking about metric-discontinuities at
data-quality boundaries** — applicable to our C2(b) OpenAlex
coverage diagnostic *and* to our pre-1990 dummy-variable test
(see C1 walkthrough below).

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

**(1) Validation of ws2's pre-1990 handling approach.** Phase 0.1
§13 commits to *retaining* pre-1990 data in Tests I-III primary
analysis (1970–2024 span) for substantive reasons (13-B baseline,
13-D variation, 13-F null-rebuttal). Measurement weaknesses are
addressed via the drift-mitigation ladder (desiderata §3) plus
pre-1990 exclusion as one row in the pooled measurement-robustness
appendix (Hofstra C8 commitment). The subfield mechanism test
alone is post-1990-restricted (desiderata §10). Holst's findings
validate this asymmetric approach: dataset-quality issues are
concentrated in pre-1990, but clipping isn't the right response —
*drift mitigation + sensitivity-check-via-robustness-row* is.
Holst confirms our drift-mitigation work is doing real lifting.

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
- *Pre-1990 vs. post-1990 dummy* in our Tests I-III specifications.
  Year-FE absorbs year-specific shifts equally for all years; a
  specific pre-1990 dummy tests whether the pre-1990 era contributes
  a systematic shift *beyond* what year-FE absorbs. Given Tests I-III
  span 1970–2024 (pre-1990 retained per §13), the discontinuity at
  the 1990 boundary is in our analysis space. **This is now committed
  as a Phase 0.2 batch addition.**
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

- **Reaffirms ws2's asymmetric pre-1990 handling.** Phase 0.1 §13
  retention policy + drift mitigation + pooled-appendix robustness
  row + post-1990 restriction for subfield mechanism test only.
  Holst validates this asymmetric approach (drift mitigation +
  sensitivity check rather than clipping primary analysis). No
  design refinement needed.
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

2. **Holst validates ws2's asymmetric pre-1990 handling**: drift-
   mitigation + sensitivity-check-via-robustness-row, not clipping
   primary analysis. Phase 0.1 §13 retention policy is the right
   design choice; the pre-1990 era is exactly where drift mitigation
   does its work. The subfield mechanism test alone is post-1990-
   restricted (per desiderata §10).

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

Working session with user, 2026-04-27.

**Already explicitly handled (existing commitments):**
- Test IV N_p: < 5 references → exclude
- Test IV T_p: single-author → baseline (definitional T_p = 0)
- Demographic plurality: weight-by-confidence + per-region accuracy
- Spearman top-N / Gini / embedding metrics: small-sample exclusion
  via two-stage calibration protocol

**Possibly missed degenerate cases identified in this audit:**

*(1) Test IV upper-bound on team size — large-team saturation.*
HEP-style collaborations (k_p > 500) may have T_p saturated near
maximum (every demographic group represented mechanically). Three
options considered:
- (a) Exclude k_p > 50 from primary (initial recommendation —
  rejected; loses too much data)
- (b) Large-team binary dummy at arbitrary threshold (rejected;
  fuzzy discontinuity, not well-modeled by binary)
- (c) Sensitivity check at high threshold k_p > 500 (HEP-specific
  saturation regime)

**Refined recommendation: option (c) with k_p > 500.** Adds one
row to existing measurement-robustness appendix; primary spec
unchanged. The existing (log k_p)² quadratic from PAP 2025
refinement handles 50-500 range non-linearity; only the extreme
saturation tail (k_p > 500, < 1% of papers, concentrated in HEP)
needs separate handling.

*(2) Test IV papers with c_p = 0 (uncited at 5 years).* Direct
Holst parallel: PLF set CD-index of uncited papers to "non-defined"
or 0 by convention. We now have c_p as a control (per PAP 2025
SQ8). Papers with c_p = 0 have ill-defined relationships with N_p
(no community uptake → can't really test "team diversity →
community-recognized novelty"). Pre-register: exclude c_p = 0 from
Test IV primary; include as sensitivity-only subset.

*(3) Subfield mechanism test temporal-window degeneracy.* Subfields
with < N years of data → can't compute meaningful CanonConc_s or
DivMag_s time series slope. Pre-register: subfields with fewer
than 10 years of post-1990 coverage excluded from subfield
mechanism test.

*(4) Demographic plurality coverage threshold per year.* Years
with extremely sparse demographic inference might give unstable
estimates. Pre-register: years where < 50% of authors have
confident demographic inference flagged with disclaimer (not
excluded; reported with explicit caveat).

*(5) Anchor-concept distribution for drift mitigation.* Mitigation
4 (anchor-projection) requires anchor concepts well-distributed
across subfields. Subfields with fewer than ~5 anchor concepts
might give unstable anchor-projection. Pre-register: anchor-concept
distribution diagnostic (sanity check) as part of Phase 0.1
classifier-drift audit.

**Phase 0.2 batch additions captured separately in plan.**

### On C2 — robustness-check threat-level analysis for ws2

Working session with user, 2026-04-27.

**Four failure modes from Holst's analysis.**

PLF's robustness checks failed in specific ways. Generalized to
ws2:

1. *Threat operates at a different level than the check.* PLF's
   regression operated on continuous covariates; couldn't capture
   node-level (zero-references) discontinuity. PLF's rewiring
   preserved node-level structure; couldn't detect node-level
   threats.
2. *Threat preserved across all check variations.* PLF's three
   CD-variants all preserved the (1 + R_k) denominator structure.
   Variations didn't perturb the relevant level.
3. *Check lacks power for the threat.* Small effects buried in
   variance, or threat manifests at low frequency.
4. *Multiple checks share the same blind spot.* If multiple checks
   all operate at the same wrong level, "robust across multiple
   checks" is illusory.

**Per-check audit for ws2's existing robustness machinery.**

| Check | Threat targeted | Level | Failure mode |
|---|---|---|---|
| Detrended correlation w/ r(t) | Citation inflation via reference list growth | Metric-covariate correlation, time-detrended | Misses non-r(t) growth-related threats |
| Stationarity diagnostic | Metric distribution drift over time | Distribution-level test | Misses small but real drift |
| Multi-Δ Spearman | Δ-window choice as artefact | Window choice | Misses if all Δ miss true regime |
| Multi-N robustness (Spearman) | Top-N threshold sensitivity | N choice | Misses if all N miss true regime |
| Citation-difference-near-threshold | Rank-instability near top-N | Input-side stability | Heavy-tail near top is field-specific |
| Decoupled-subfield robustness | Field-size-vs-time confound | Subfield × time correlation | Subfield count low at strict thresholds |
| Pooled measurement-robustness appendix | Measurement-uncertainty restrictions | Per-restriction row | Threats preserved across restrictions |
| Cohort decomposition Option B | Cohort-mix-driven divergence | Year × cohort bins | Lead-author cohort proxy limited |
| OpenAlex coverage diagnostic | Coverage variability | Per-era × region rate | Coverage-metric joint distribution |
| Citation-completeness sensitivity | Undercoverage of citations | Completeness threshold | Completeness measure itself biased |
| Subfield mechanism nonlinearity check | Linear masks regime shift | Quadratic + LOWESS | Non-monotonic shapes quadratic can't capture |
| Test II quadratic fallback | Non-monotonic team-size effects | Linear-vs-quadratic | Same as nonlinearity check |
| Test IV with/without c_p | Bad-control problem | Confounder vs. mediator | c_p as complicated mixture |

**Threats potentially not well-covered.**

*Threat A: System-wide OpenAlex artefacts.* None of our committed
checks operate on alternative data. Holst found dataset artefacts
in WoS *and* PatentsView *and* SciSciNet *and* PubMed *and* JSTOR
*and* MAG — same artefact across "independent" databases.
Analogous risk for ws2: any OpenAlex-systematic issue passes all
our within-OpenAlex checks. **Mitigation: cross-substrate
WoS-OpenAlex overlap robustness in back-pocket (C3/SQ10 PLF
commitment); trigger if reviewers force.**

*Threat B: Embedding-model bias.* Our drift-mitigation ladder
addresses cross-era stability but not training-data bias. If
SPECTER2 has systematic biases (e.g., trained on disproportionately
Anglo content), all embedding-based metrics inherit the bias.
**Mitigation: alternative-model robustness (BGE-M3 / text-embedding-
3-large vs. SPECTER2) is committed for Stage 2; verify it swaps
embedding model entirely, not just adapter.**

*Threat C: Compound-threat interactions.* Our checks are
single-threat-at-a-time. If multiple threats interact, collective
effect could look substantive while no individual check flags
concern. **Mitigation: not directly addressable; acknowledge in
Limitations.**

*Threat D: Demographic inference systematic bias.* Even with
weight-by-confidence, if NamSor has systematic biases by region
we don't capture, demographic plurality is mis-measured.
**Mitigation: ORCID validation subsample (Phase 0.1 §4); validation
necessarily on non-random subsample (people with ORCID).
Acknowledge in Limitations.**

*Threat E: Subfield-classifier drift cascading effects.* If
subfield assignment changes over time, all subfield-level analyses
inherit the drift. **Mitigation: classifier drift audit (Phase 0.1
sanity Check 2); audit metric-level; if drift identified, downstream
handling decided.**

**Additional threats identified in audit (2026-04-27):**

*Threat F: Preprocessing decision biases.* Upstream of metric
computation: abstract text cleaning rules; citation count
aggregation method; subfield assignment tie-breaking; author
identity merging when ORCID conflicts with OpenAlex disambiguation.
**No metric-level robustness check catches these.** Mitigation:
pre-register preprocessing rules in detail; document choices;
acknowledge in Limitations as inherent uncertainty.

*Threat G: Citation-window choice (5-year aggregation).* Spearman
top-N and Gini use citations within Δ=5 of publication. The
choice of 5 vs. 3 vs. 10 years is methodological; could affect
findings. Multi-Δ Spearman commitment addresses *adjacent-year
stability* but not *underlying citation-window aggregation*.
Mitigation: extend to Δ_aggregate ∈ {3, 5, 10} sensitivity.

*Threat H: Multiple-comparisons across full analysis landscape.*
Hundreds of statistical tests across our pre-registration
(Tests I-IV × multi-N × multi-Δ × subfield × etc.). Bonferroni
correction within test-types; no global adjustment. Mitigation:
pre-register hierarchy — headline claim requires *agreement
across* Tests I-IV, not significance in any single test (parallel
to Chu-Evans's six-prediction structure).

*Threat I: Bootstrap CI failure modes.* We use 200-replicate
bootstrap CIs. Bootstrap can fail under heavy tails, dependent
observations, or small samples. Test I/II uses Newey-West HAC SEs
(handles autocorrelation); other bootstrap CIs may not. Mitigation:
sensitivity check — compare bootstrap CIs to alternative-method
CIs (jackknife, BCa) for headline metrics.

*Threat J: Temporal binning choice (year-level aggregation).*
Year-level aggregation could obscure finer dynamics or coarser
trends. Mitigation: one-sentence acknowledgment in Methods of
year-level choice; not load-bearing for ws2 design.

**Eight Phase 0.2 batch additions from C1 + C2 audit captured
separately in plan.**

**Four actions to prevent robustness-check failure.**

1. **Build a threat-to-check mapping** as Methods-section deliverable.
   The audit table above, formalized for the eventual ws2 paper.
2. **Identify uncovered threats explicitly** and decide handling
   (back-pocket Stage 3, Limitations acknowledgment, or new check).
3. **Acknowledge uncovered threats in Limitations.** Don't pretend
   robustness machinery is comprehensive. Match Holst's lesson:
   don't overclaim.
4. **Re-examine each existing robustness commitment** during Phase
   0.1 closure consolidation pass (gate #10) for threat-specificity,
   redundancy, missing threats.

**Phase 0.2 batch additions captured separately in plan.**

The substantive payoff: ws2's robustness machinery becomes
*honestly demarcated* rather than over-claimed. We document what
each check rules out and what remains as residual uncertainty.
This is methodological humility matching Holst's lesson.

### On C3 — analogous hand-validation for ws2

Working session with user, 2026-04-27.

**What Holst's hand-validation accomplished.** 100 random samples
from a *binary-outcome* category (zero references / has references);
verified against ground truth (original PDFs); 98% / 93% turned
out to be misleadingly labeled. Strong evidence; tight CI at
n=100; methodology works for binary outcomes with verifiable
ground truth.

**Six candidate ws2 hand-validations identified.**

| Category | What it affects | Outcome type | Ground truth source |
|---|---|---|---|
| Abstract availability | Semantic plurality metrics | Binary | Publisher pages, DOI links |
| Author-affiliation extraction | Demographic plurality (country, institution, prestige) | Mostly binary | Original publication |
| Subfield assignment | Subfield-level analyses | Continuous (degree of fit) | Domain expert judgment |
| Demographic inference (gender) | Demographic plurality directly | Binary | ORCID self-reports |
| Citation count | Canonical concentration | Continuous (% match) | Semantic Scholar, Google Scholar |
| Reference list completeness | Test IV N_p (especially N_p^author) | Continuous-but-binarizable | Crossref, original PDF |

**Best fits for Holst-style binary hand-validation:**

*(a) Gender inference accuracy.* Sample 100 names with ORCID
match. Compare NamSor's predicted gender to ORCID self-report.
Binary outcome. ORCID accessible programmatically. ~3 hours.

*(b) Reference list completeness.* Sample 100 papers (post-1990;
non-zero OpenAlex reference count). Compare OpenAlex reference
list to Crossref. Binarize: complete match / partial mismatch /
OpenAlex-fewer. ~3 hours.

**Less tractable categories:**

- *Subfield assignment:* continuous outcome; requires domain
  expert per paper; better covered by classifier drift audit.
- *Citation count:* continuous outcome; Google Scholar over-counts
  vs. WoS; comparison ambiguous.
- *Author-affiliation:* subsumed by demographic inference
  validation downstream.
- *Abstract availability:* high coverage assumed; marginal value
  of explicit hand-validation low.

**Existing ws2 validations (diagnostic-style, not hand-validation):**

- ORCID validation subsample for demographic inference (Phase 0.1
  §4)
- Concept classifier drift audit (sanity Check 2)
- Demographic inference coverage check (sanity Check 3)
- Author disambiguation spot-check (sanity Check 4)

These are statistical patterns over many samples, not Holst-style
hand-verification of specific samples against ground truth.
Different evidence type — complementary.

**Plus Culbert et al. 2024/2025 (Tier 2 paper 16) provides
broader OpenAlex coverage validation.** Their published validation
is population-level evidence; our hand-validations would be
individual-level evidence. Complementary.

**Three handling options:**

*Option A:* Comprehensive hand-validation across multiple
categories (~15 hours). Strong but expensive.

*Option B:* Targeted hand-validation of two high-payoff binary-
outcome categories (gender inference + reference list completeness;
~6 hours).

*Option C:* Rely on existing diagnostics + Culbert et al. validation
(0 additional hours; indirect).

**Decision: Option B.** Reasons:
1. Both validations directly affect load-bearing ws2 metrics
   (demographic plurality + Test IV N_p).
2. Both have binary outcomes (Holst-style methodology applies
   cleanly).
3. Both have accessible ground truth (ORCID + Crossref).
4. ~6 hours is reasonable in early Stage 1.
5. Strong evidence for two metric channels > weak evidence across
   many.

**What we skip:** abstract availability (high coverage); subfield
assignment (continuous; needs domain expert); citation count
(continuous; ambiguous comparison); author-affiliation (subsumed).

**Phase 0.2 batch additions: two targeted hand-validations**
captured separately in plan with pre-registered interpretive
thresholds.

**Why this matters substantively.** Without these validations,
we're trusting OpenAlex on faith for two metric channels affecting
headline findings. With them, we have specific evidence about
pipeline accuracy citable in Methods and Limitations.

### On C4 — OpenAlex-specific metadata-quality concerns

Closed via close-via-pointer + brief residual-concerns
acknowledgment, 2026-04-27.

**Substantive content covered by existing commitments + planned
EDA.** Audit checked OpenAlex-specific concerns against our
committed machinery:
- Concept tag drift → classifier drift audit (sanity Check 2)
- Reference list completeness → hand-validation (C3 commitment)
- Demographic inference accuracy → hand-validation (C3 commitment)
  + existing ORCID validation
- Per-era coverage variability → coverage diagnostic (PLF C2(b))
- Identifier disambiguation reliability → disambiguation spot-
  check (sanity Check 4)
- Distribution-shape oddities → pilot metric convergence (sanity
  Check 5)

**Residual concerns possibly not fully covered:**
- OpenAlex-specific MAG-legacy quirks (PDF parsing artifacts,
  name normalization). Mitigation: Culbert et al. 2024/2025
  (Tier 2 paper 16) provides MAG-vs-OpenAlex comparison; engage
  during Tier 2 reading.
- OpenAlex ID instability within a snapshot. Mitigation: snapshot-
  pinning (already in desiderata).
- ROR-based institution taxonomy issues (multiple ROR IDs per
  institution; missing ROR IDs). Not directly covered; small
  magnitude expected.
- Country boundary changes (USSR dissolution, etc.). Out of ws2
  scope.

**Decision: no new Phase 0.2 batch additions.** Existing
machinery + planned EDA + Tier 2 Culbert reading is sufficient.
Residual structural quirks acknowledged in Methods/Limitations
paragraph (per Threat F preprocessing-decisions commitment).

### On C5 — cross-substrate robustness interpretation

Closed via brief note, 2026-04-27.

**The Holst lesson:** cross-database "robustness" doesn't actually
demonstrate robustness against artefacts shared between databases
(PLF's six-database replication doesn't help when same artefact is
present in all six). Generalizes to ws2's back-pocket WoS-OpenAlex
cross-substrate robustness commitment (from PLF C3/SQ10).

**For ws2: bounded interpretive value of cross-substrate
replication.** If the back-pocket is triggered (reviewer pushback)
and findings converge across WoS-OpenAlex overlap subset, this
demonstrates robustness *against artefacts differing between WoS
and OpenAlex* but does *not* demonstrate robustness *against
artefacts shared between them* (e.g., pre-1990 metadata-quality
issues affecting both substrates similarly).

**Refinement to existing back-pocket commitment.** Add one
sentence to the C3/SQ10 cross-substrate Stage 3 robustness
back-pocket: "Per Holst C5 lesson: cross-substrate replication
establishes robustness against substrate-differential artefacts
but not against artefacts shared across substrates. Pre-1990
metadata-quality issues operating in both WoS and OpenAlex
similarly are not directly testable by this approach."

This is a small interpretive caveat, not a new commitment. No
Phase 0.2 batch addition; refinement folds into existing
back-pocket commitment.

### On C5 — cross-substrate robustness interpretation

(Pending.)

---

## Study Question Walkthroughs

### SQ1 — Why CD_5 = 1 for zero-reference papers

Skipped — covered via Key Idea #2 (CD_5 = 1 + zero references
mechanism). Substantive content captured there.

### SQ2 — Why seaborn bug didn't affect PLF's regression

Skipped — comprehension-level. Bug affected histograms only;
regression operated on raw data. Trivially answered from Key
Idea #1.

### SQ3 — Mechanical decline from CD_5 = 1 frequency change

Skipped — covered via Key Idea #3 (metadata-quality time trend
creating mechanical decline). Substantive content captured there.

### SQ4 — Confidence intervals on hand-validation percentages

Skipped — comprehension-level statistical question. 95% binomial
CI on 98% at n=100 is approximately [93%, 100%]; on 93% at n=100
is approximately [86%, 97%]. Tight enough for binary claims.

### SQ5 — R² jump as evidence of misspecification

Skipped — covered via Key Idea #5 (why PLF's robustness checks
failed). The R² jump (0.10 → 0.52, 0.15 → 0.95) when adding
zero-references dummy is exactly the diagnostic-of-discontinuity-
via-residual-pattern lesson captured there.

### SQ6 — Empirical vs. structural critique complementarity

Working session with user, 2026-04-27.

**The three critique types in the post-PLF chain.**

*PAP 2024 — deductive structural critique.* Attacks CD-index *as
a metric*, regardless of dataset. Mathematical: CD = CD^nok /
(1+R_k); R_k grows with citation density; CD → 0 mechanically.
Generalizable to any dataset where citation networks densify.
Methodology: algebraic + synthetic-network simulation.

*Holst 2024 — empirical data-quality critique.* Attacks PLF's
*specific empirical results*. Empirical: zero-reference papers in
early eras → CD_5 = 1 mechanically; metadata quality improvement
over time → declining average CD. Less generalizable; depends on
which datasets have which quality issues. Methodology: dataset
diagnosis + hand-validation + cross-database replication.

*PAP 2025 — empirical re-analysis with proper controls.* Attacks
PLF's *interpretation*. Even controlling for r_p, c_p, year-FE,
k_p with quadratic terms, residual effects 0.06σ (time) /
0.09σ (team size) — at noise level. Methodology: multivariate
regression + PNAS quasi-experiment.

**Are they complementary, redundant, or conflicting?**

**Complementary.** Each individually has limitations the others
address:

| Critique | What's strong | What's weak |
|---|---|---|
| PAP 2024 | Theoretical certainty; metric-level vulnerability provable | "Maybe in real data the bias is small" — no empirical magnitude |
| Holst | Strong empirical evidence on specific dataset | "Fix the data and the decline reappears" — doesn't address metric vulnerability |
| PAP 2025 | Controlled-analysis noise-level result | "Maybe controls over-correct" — doesn't address structural metric problem |

Each is defensible-against individually. The conjunction is much
harder to defend.

**What the conjunction proves: triple-jeopardy defense burden.**

To preserve PLF's claim, a defender must simultaneously:

1. Refute the structural vulnerability (PAP 2024) — *very hard*;
   algebra is direct.
2. AND show artefacts aren't dominant in their data (Holst) —
   *very hard*; hand-validation is direct.
3. AND show controlled analyses find substantive non-noise
   magnitude (PAP 2025) — *very hard*; multiple independent
   re-analyses converge.

Failing any one collapses the defense. Three independent successes
required. Individual critiques might be parried; the chain is hard
to break.

**Potential conflicts considered.**

- *PAP 2024's structural critique vs. Holst's artefact-driven
  decline?* Compatible. Artefact-driven decline operates *through*
  the structural vulnerability.
- *PAP 2025's noise-level vs. Holst's artefact-driven decline?*
  Different methodologies on related datasets. Both report same
  direction (decline disappears post-correction). Convergent
  evidence; could have diverged but didn't. Slightly over-
  determined but that's a strength, not weakness.

**The general methodological lesson — three-layer defense pattern.**

The post-PLF critique chain illustrates a generalizable pattern:

| Layer | Type | Purpose |
|---|---|---|
| Theoretical/analytical | Show structural property of metric | Establishes when metric is/isn't valid |
| Empirical diagnostic | Show specific data behaves as theory predicts | Validates theory in actual conditions |
| Controlled analysis | Show effect persists/disappears under proper controls | Removes alternative explanations |

For ws2's own methodological defense, we should aim for the same
three-layer pattern. **We already have all three layers committed:**

| Layer | ws2's existing commitment |
|---|---|
| Theoretical/analytical | Rank-invariance argument; algebraic decomposition statement; PAP 2025 three-conditions framework — all in (c-prime) sub-commitment 1 |
| Empirical diagnostic | PAP-style inflation diagnostics (stationarity, detrended correlation); decoupled-subfield robustness; pre-1990 dummy operational diagnostic |
| Controlled analysis | Test II/IV regression specifications with proper controls (c_p, quadratics, year-FE, subfield-FE); PAP 2025-style refinements |

The SQ6 walkthrough validates that ws2's methodological defense
follows the same successful structure as the post-PLF critique
chain.

**Refinement: explicit three-layer framing in Methods.**

Currently our defenses are scattered across commitments. Organizing
them as an explicit three-layer structure makes the conjunction
visible:

- *Layer 1 (theoretical):* "Our metrics are structurally
  inflation-immune [three-conditions framework]."
- *Layer 2 (empirical diagnostic):* "Our metrics empirically pass
  inflation-vulnerability diagnostics [stationarity + detrended
  correlation results]."
- *Layer 3 (controlled analysis):* "Our findings persist under
  proper-control regression specifications [PAP 2025-style
  controls]."

This is an organizational refinement to (c-prime) sub-commitment 1
(Methods paragraph defending inflation-immunity). Same content;
better structure. ~7-9 sentences becomes 3 short paragraphs.

**Methodologically stronger because:**

- Explicitly mirrors the structure of the most successful critique
  chain in the post-PLF literature.
- Makes triple-convergence visible to reviewers.
- Pre-empts pushback on any individual layer with the
  conjunction-strength argument.

**Phase 0.2 batch refinement: three-layer Methods structure
captured separately in plan.**

### SQ7 — Robustness-check-failure level analysis

Skipped — covered via C2 walkthrough (full robustness-check
threat-level analysis for ws2's 13 existing commitments + four
failure modes from Holst's PLF analysis). The substantive content
of SQ7 ("walk through why each failed at the level it operates at")
is captured in C2's per-check audit table.
