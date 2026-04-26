# 01 — Slowed canonical progress in large fields of science

**Authors:** Johan S. G. Chu, James A. Evans
**Venue:** *PNAS* 118(41), e2021636118 (2021)
**PDF:** `literature-review/01-chu-evans-2021-canonical-progress.pdf` (gitignored)
**SI:** `literature-review/01-chu-evans-2021-canonical-progress_SI.pdf` (gitignored)
**DOI:** 10.1073/pnas.2021636118

---

## Background

Chu and Evans 2021 sits at the intersection of three established
scientometrics threads: (i) preferential attachment in citation
networks (Jeong-Néda-Barabási 2003; Wang-Song-Barabási 2013), (ii)
team-size-and-disruption dynamics (Wu-Wang-Evans 2019; Funk-Owen-Smith
2017 CD-index family), and (iii) the broader "are ideas getting
harder to find" research-productivity literature (Bloom-Jones-Van
Reenen-Webb 2020). The novel contribution is to treat **field size
itself** — measured as the number of papers published in a subject
in a given year — as the organizing variable that explains structural
shifts in citation dynamics.

The paper's central claim: when field size grows large, several
distinct citation-dynamics patterns shift in concert — citation
inequality rises, the most-cited list ossifies, new papers are
unlikely to enter canon, when they do they enter rapidly rather than
through gradual diffusion, and disruption (in the Wu-Wang-Evans /
Funk-Owen-Smith sense) declines. Six co-confirming predictions across
three substantive dimensions (durable dominance, entrepreneurial
futility, reduced disruption) are tested on Web of Science 1960–2014
(90.6M papers, 1.8B citations, 241 subjects) and all six are
empirically supported.

Two theoretical mechanisms are advanced. First, cognitive overload:
when many papers arrive in a short window, reviewers and readers
process new work via heuristics, anchoring on existing canon as
"intellectual badges" (Stinchcombe 1982; Zuckerman 1999); novel work
that resists categorization is filtered out. Second, the sandpile
critical-state mechanism (Bak-Tang-Wiesenfeld 1987; Adami-Chu 2002):
when the arrival rate of "grains" (new papers) is too fast,
neighboring miniavalanches interfere, and no individual grain can
trigger a pile-wide shift. Both mechanisms predict that fast arrival
rates suppress the localized diffusion processes by which new ideas
historically rose into canon.

The Chu-Evans framework is the direct methodological precedent for
ws2's canonical-concentration time-series metric. We adopt their
Spearman rank correlation of top-N most-cited papers as our primary
canonical-concentration operationalization. The paper does not engage
demographic plurality; its question is field-size-and-citation-
dynamics. ws2's question — does demographic plurality decouple from
semantic plurality, with canonical concentration as a candidate
mechanism — extends Chu-Evans by asking whether the canonical-
ossification phenomenon they document also tracks (or fails to track)
demographic plurality at the field level.

---

## Key Ideas

### 1. Field size as the organizing variable

Field size is operationalized as **N = the number of papers published
in a focal subject in a focal year**. The 241 Web of Science subjects
serve as field boundaries. The paper's analytical move is to bin
field-years by log₁₀N (cutpoints at 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5,
5.5) and document how citation dynamics change across bins. This
treats field size as a continuous covariate rather than a category;
the same subject can sit in different bins in different years.

### 2. Six predictions across three substantive dimensions

The theory yields six predictions, two per dimension. Compared to a
field-year with few publications, in a field-year with many
publications:

**Durable dominance:**
1. New citations are more likely to flow to the most-cited papers
   rather than less-cited papers.
2. The list of most-cited papers changes little year to year — the
   canon ossifies.

**Entrepreneurial futility:**
3. The probability a new paper eventually becomes canon (top 0.1%
   most cited) drops.
4. New papers that do rise into the most-cited do so rapidly, not
   through gradual cumulative attention-gathering.

**Reduced disruption:**
5. Newly published papers more often develop existing scientific
   ideas (D < 0) and less often disrupt existing ideas (D > 0).
6. The probability of a new paper being highly disruptive (top 5%
   of disruption measure) declines.

All six are confirmed in the data (Figs. 1–4).

### 3. Spearman rank correlation of top-50 as the canon-ossification metric

The paper's central operationalization of "canon ossification" is the
**Spearman rank correlation of the top-50 most-cited papers between
the focal year and the next year** (Δ=1 lag). Higher correlation =
more canonical stability = canon is ossified. The headline finding:
predicted Spearman correlation rises from 0.25 at N=1,000 papers/year
to 0.74 at N=100,000 papers/year. This is the metric ws2 directly
inherits as our primary canonical-concentration operationalization,
with the modification that we use Δ=5 rather than Δ=1 to smooth
single-year measurement noise.

### 4. Citation decay rate λ by percentile

For each (log₁₀N) × (citation percentile) bin, the paper regresses
the number of citations to a paper in year Y+1 on the number of
citations to that paper in year Y. The regression coefficient yields
the **decay rate (1−λ)**: the fraction of year-Y citations that
"survive" to year Y+1. In small fields (N<1,000), 1−λ ≈ constant
across percentiles. In large fields (N>10,000), 1−λ trends toward 1
for the top-percentile most-cited papers (their citations don't
decay) but toward values <1 for all other percentiles (their citations
decay year-over-year). The implication: **the most-cited papers in
large fields maintain their citation level indefinitely; everyone
else loses citations.**

### 5. Probability and time to reach canon

Two derived metrics on the entrepreneurial-futility side:
- **p (reach top 0.1%)**: probability a paper ever reaches the top
  0.1% most cited in its field. Drops with field size.
- **τ (reach top 0.1%)**: median number of years for a paper to
  reach the top 0.1%, conditional on reaching it. In small fields
  (N=1,000), τ ≈ 9 years — gradual cumulative process. In large
  fields (N=100,000), τ < 1 year — papers either rise to canon
  immediately or never.

The interpretation: in large fields, gradual diffusion-based ascent
to canon disappears. New papers either explode into canon or fade.

### 6. Disruption measure D and its decline

The disruption measure D from Wu-Wang-Evans 2019 (which inherits the
Funk-Owen-Smith CD-index family) ranges roughly from −1 (purely
develops prior work) to +1 (purely disrupts prior work). The paper
shows:
- The proportion of papers with D > 0 drops from 49% at N=1,000 to
  27% at N=10,000 to 13% at N=100,000.
- The proportion of papers with top-5% disruption drops from 8.8%
  at N=1,000 to 0.6% at N=100,000.

**Caveat for ws2 engagement.** The disruption measure D is the
contested CD-index family that ws2 has explicitly excluded from
primary canonical metrics per Petersen-Arroyave-Pammolli 2024 (citation
inflation critique) and Holst et al. 2024 (dataset artifact critique).
Engagement with predictions 5–6 must be filtered through this
methodological-critique lens.

### 7. Two theoretical mechanisms

**Cognitive overload + categorization.** When the rate of new-paper
arrival exceeds reviewer/reader cognitive bandwidth, work is processed
heuristically — categorized in relation to existing canon. Papers that
fit existing schemas pass; papers that don't fit are filtered out.
Authors learn to cite canon defensively as "intellectual badges"
(Stinchcombe 1982). The mechanism predicts both reduced disruption
(filtered at production) and reinforced canon (citations consolidate
on the schema-anchors).

**Sandpile critical state.** Drawn from self-organized-criticality
physics (Bak-Tang-Wiesenfeld 1987). When sand grains drop slowly, the
pile reaches scale-free critical state where a single grain can
trigger pile-wide avalanches. When grains drop too fast, neighboring
miniavalanches interfere; no grain can trigger pile-wide shifts. The
mechanism predicts that fast arrival of new papers prevents the
localized-diffusion-and-preferential-attachment process by which new
ideas historically reach canonical status.

Both mechanisms are *suggested* by the empirical patterns but **not
directly tested** at the cognitive or network-dynamics level.

### 8. Period dominates cohort (SI Tables S2, S3)

A natural alternative explanation: shifts in citation dynamics could
reflect cohort effects (different generations of scholars trained
under different field-size conditions cite differently) rather than
period effects (the same scholars cite differently as their field
grows). The SI uses author fixed effects on the largest field
(Electrical & Electronic Engineering) and finds:
- **Period effect (current field size):** 10× increase in current
  field size → +2 percentage points probability of citing a top-0.1%
  paper.
- **Cohort effect (field size at author's first publication):**
  16–30× smaller than the period effect.

**Interpretation:** even veteran scholars adapt their citation
patterns to current field size. The shift in citation dynamics is
not driven by generational replacement of citing scholars; it's
driven by all scholars responding to current-state field size.

### 9. Field-size effect persists after controlling for time (SI Table S1)

The most obvious confound — "fields grow over time, and time also
shifts citation dynamics" — is addressed via regression with
year-as-continuous, year-dummies, and subject-fixed-effects:
log₁₀N remains a significant predictor of top-50 rank correlation
(coefficient 0.090, p<0.001) under all three specifications. A
10× increase in field size produces about the same effect as 15
years of field maturation. The paper concedes this doesn't fully
rule out field-age confounding (some fields' size-and-age are highly
collinear, e.g., Pharmacology r=0.95, Mathematics r=0.95, Computer
Science r=0.97–0.98), and points to fields with weaker year-size
correlation (Biochemistry r=0.32, Applied Physics r=0.58) where the
size effect is still observed (Fig. S1).

---

## Results — Three Levels

### Level 1: For a smart high-schooler

When a scientific field gets really big — like, when 100,000 papers
get published every year in just one field — the same handful of
"famous" papers stay on top, year after year. New papers can't catch
up. Even when a new paper does become famous, it has to become famous
right away; there's no slow climb. And new papers tend to build on
what's already there, rather than challenging old ideas. The authors
argue this happens because there's just too much new stuff for
scientists to read carefully — they take shortcuts and lean on the
papers everyone already knows. The result: bigger fields might
actually slow down progress, even though they have more researchers
and more papers. More isn't always better.

### Level 2: For a junior/senior undergraduate

The paper analyzes 90 million papers and 1.8 billion citations from
Web of Science (1960–2014) across 241 subject classifications. The
key independent variable is field size — operationalized as the
number of papers published in a subject in a given year. The authors
make six predictions about how citation dynamics shift as field size
grows, all confirmed:

1. **Citation inequality rises** — Gini coefficient of citation share
   reaches 0.5 in the largest fields (comparable to income inequality
   in the most unequal countries).
2. **Canon ossifies** — Spearman rank correlation of top-50
   most-cited papers between adjacent years rises from 0.25 (at 1K
   papers/year) to 0.74 (at 100K papers/year).
3. **Top papers don't decay** — citation decay rate trends to zero
   for top-percentile papers in large fields (they keep their
   citations year over year), while all other papers lose citations.
4. **New papers can't reach canon** — probability of ever entering
   the top 0.1% drops with field size.
5. **When they do, it's instantaneous** — median time to top 0.1%
   drops from 9 years (small fields) to under 1 year (large fields).
6. **Disruption declines** — the proportion of papers with positive
   disruption measure (Wu-Wang-Evans 2019) drops from 49% to 13% as
   field size grows from 1K to 100K.

Two theoretical mechanisms are advanced: cognitive overload (readers
heuristically anchor on existing canon when overwhelmed) and a
sandpile critical-state argument from physics (fast arrival of grains
prevents pile-wide avalanches). The findings are robust to controls
for time (SI Table S1) and to author fixed effects, with period
effects 16–30× larger than cohort effects (SI Tables S2, S3).

### Level 3: For an early graduate student

Methodologically, the paper is built on a binning + within-bin
regression strategy. Field-years are binned by log₁₀N (cutpoints at
1, 1.5, 2, ..., 5, 5.5); within each bin, citation-share-by-rank,
year-over-year decay rate, top-50 rank correlation, p(reach top
0.1%), τ(reach top 0.1%), and disruption-measure proportion are
computed. Lowess trendlines on bin-level estimates yield the headline
patterns.

The empirical claim is largely descriptive — "as field size grows,
citation dynamics shift in concert across these six dimensions" —
backed by stratified estimates with field-fixed-effects and
year-controls. Causal language ("a deluge of new papers entrenches
top-cited papers") is invoked but the paper acknowledges
("Our current analyses cannot, however, rule out other causal
explanations") that the design is not causally identified. The
SI's most important contribution to causal credibility is the
period-vs-cohort decomposition: with author FEs, current-year
field size dominates entry-year field size by 16–30× in predicting
citation-to-canon probability — meaning scholars adapt to current
field size rather than imprinting on entry-state field size. This
weakens the strongest competitor explanation (cohort selection)
substantially.

Three substantial limitations matter for ws2:

**(a) Field operationalization.** WoS 241-subject classification is
exogenously imposed by Clarivate, not derived from research-community
boundaries. The paper acknowledges that subdisciplinary structure
might be where progress occurs, and that better classification
("temporal citation network community detection") is needed but
unavailable at scale. ws2 uses OpenAlex concept tags — a different
but parallel exogenous classification with broader coverage and
noisier per-paper concept assignment.

**(b) Disruption measure inheritance.** Predictions 5 and 6 rely on
the Wu-Wang-Evans 2019 disruption measure, which is in the
Funk-Owen-Smith CD-index family. Petersen-Arroyave-Pammolli 2024
(citation inflation) and Holst et al. 2024 (dataset artifacts) have
shown the CD-index is biased by precisely the citation-volume growth
that Chu-Evans uses as the IV. Whether predictions 5–6 survive
reanalysis under inflation-corrected and artifact-corrected disruption
measures is an open question. ws2 has explicitly excluded CD-index
from primary canonical metrics.

**(c) Theoretical mechanism inference.** Both mechanisms (cognitive
overload, sandpile criticality) are *suggested* by the empirical
patterns but not directly tested. The paper does not measure attention
allocation, does not test heuristic processing in reviewers, does not
operationalize the sandpile model on actual citation data. The
mechanisms are framing devices that organize the empirical findings
into a coherent narrative; their independent empirical validity is
not established here.

The cumulative-vs-annual operationalization of "field size" is also
worth flagging: the cognitive-overload mechanism arguably ties more
naturally to **cumulative literature size** (how much there is to
catch up on) than to **annual paper count** (how much new arrives
per year). The paper operates exclusively on annual count. Whether
findings would survive cumulative-literature operationalization is
an open question.

---

## Connection to Our Project

### What Chu-Evans do well that we should learn from

1. **Spearman rank correlation top-N is the right canonical-stability
   metric.** It is rank-invariant to citation magnitudes (so robust
   to citation inflation), tractable, and interpretable. ws2 inherits
   this directly as primary canonical-concentration operationalization
   with N=50, Δ=5 (Phase 0.1 plan, Open decisions deferred,
   "Canonical (primary)").
2. **Bin-by-log₁₀N as a within-subject heterogeneity strategy.** The
   bin-and-regress design avoids assuming linear or polynomial
   relationships and lets the data reveal regime shifts. Useful
   pattern for ws2's subfield mechanism test.
3. **Period-vs-cohort decomposition.** SI Tables S2/S3 establish
   that current-state field size dominates entry-state field size by
   16–30×. This supports time-FE specifications throughout ws2 (we
   control for paper publication year, not author entry year, in
   Test IV regression).
4. **Six co-confirming predictions across three substantive dimensions.**
   The pattern of co-confirming predictions raises the bar substantially
   above any single empirical finding. Useful framing for ws2's own
   four-co-primary-tests (Tests I-III + Test IV) approach: each test
   asks a distinct substantive question; agreement across tests is
   the strength of the package.
5. **Honest acknowledgment of causal limits.** "Our current analyses
   cannot, however, rule out other causal explanations." Worth
   replicating in ws2 — observational divergence claims are not
   causal effects of demographic-on-semantic plurality.

### What Chu-Evans do NOT do — and where ws2 fills the gap

1. **They use field size as IV; we treat canonical concentration
   itself as a time-series metric.** ws2's third panel is a time
   series of CanonConc per year per field, derived using their
   methodology but used as an outcome rather than a covariate.
2. **They don't link canonical concentration to demographic plurality.**
   ws2's central question — does demographic plurality decouple from
   semantic plurality, with canonical concentration as a candidate
   mechanism — is not in their scope. Our subfield mechanism test
   (CanonConc_s on DivMag_s) treats their finding as the upstream
   driver.
3. **They use WoS subject (n=241).** ws2 uses OpenAlex concept tags
   at finer granularity (~10–50 subfields per field). The OpenAlex
   classifier is noisier per-paper but covers more papers and supports
   finer subdisciplinary structure.
4. **They use Δ=1 adjacent-year Spearman.** ws2 uses Δ=5 to smooth
   single-year noise. We will report Δ=1 alongside Δ=5 as a
   comparability column with their published numbers.
5. **They use disruption measure D from CD-index family.** ws2
   excludes CD-index from primary canonical metrics. Predictions 5–6
   are engaged via the Park-Leahey-Funk → Petersen-Holst critique
   chain rather than replicated.
6. **They don't separate field size from cumulative literature size.**
   ws2's primary metric also operates on annual counts (per their
   precedent), but we should consider cumulative-literature
   operationalization as a sensitivity check (deferred to Stage 2
   if pilot results suggest material divergence).
7. **Their "subject" is exogenous (WoS classification).** Our
   subfield assignment is also exogenous (OpenAlex hybrid: arXiv
   category primary, OpenAlex concept fallback). Both inherit
   classification-imposed-by-database limitations. Mitigation in
   ws2: subfield classifier drift audit (Phase 0.1 sanity Check 2).

### Specific design implications for ws2

- **Confirms canonical-concentration primary as Chu-Evans Spearman
  N=50, Δ=5.** Already in plan; no change needed.
- **Add Δ=1 as a comparability column** in our canonical-concentration
  table for direct comparison to their published Spearman values.
  Phase 0.2 batch addition.
- **Field-size confound on subfield mechanism test (CanonConc_s on
  DivMag_s regression).** Chu-Evans documents that field size drives
  canonical concentration. Our regression must control for log
  subfield size in year Y, otherwise CanonConc_s is partially
  confounded with subfield-size growth. Already in plan as
  "log papers" subfield-level control; reaffirmed here.
- **Period-vs-cohort dominance supports time-FE specification in
  Test IV.** Already in plan as year-FE in Test IV regression;
  reaffirmed here. Ws2 should NOT control for author-entry-year
  (cohort) as the primary time control — current publication year is
  the load-bearing fixed effect per their finding.
- **Engagement with disruption finding (predictions 5–6) goes through
  Park-Leahey-Funk + Petersen-Holst, not direct replication.** Phase
  0.2 batch: Discussion section paragraph engaging Chu-Evans
  predictions 5–6 with explicit acknowledgment that the disruption
  measure they use is the contested CD-index family.
- **Cumulative-literature-size sensitivity flag.** Possible Stage 2
  sensitivity check: recompute canonical concentration with cumulative
  literature size as the IV instead of annual paper count. Deferred;
  decide based on Stage 2 pilot if material divergence between the
  two operationalizations.

### Mechanism-pluralism: how we use Chu-Evans

Chu-Evans offer two theoretical mechanisms (cognitive overload + canon
anchoring; sandpile critical-state interference). Simpler accounts —
Matthew-effect / preferential attachment, journal-prestige
entrenchment — predict the same empirical pattern (τ collapse, canon
ossification, citation inequality rising) through different mechanisms.
Chu-Evans do not adjudicate among these; their evidence is consistent
with all four. **ws2's use of Chu-Evans is methodological + empirical,
not mechanistic.** We inherit Spearman top-N as our canonical-
concentration metric; we cite their empirical pattern (canonical
concentration rises with field size) as a benchmark for positioning
our findings; we do *not* lean on any specific mechanism account as
upstream support for compass 13-A (actuator homogenization). In the
ws2 Discussion section, we will note that several mechanisms plausibly
contribute to canonical concentration at scale and that adjudicating
among them is out of ws2 scope.

---

## Key Quotes

For Methods / Related Work in the ws2 paper:

> "When the number of papers published per year in a scientific field
> grows large, citations flow disproportionately to already well-cited
> papers; the list of most-cited papers ossifies; new papers are
> unlikely to ever become highly cited, and when they do, it is not
> through a gradual, cumulative process of attention gathering; and
> newly published papers become unlikely to disrupt existing work."
> (Abstract.)

> "The largest fields have a Gini coefficient of citation shares of
> around 0.5, which is as large as income inequality in the most
> unequal countries — only China and South Africa have Gini
> coefficients higher than 0.5." (p. 2.)

> "The predicted Spearman rank correlation of the top-50 most-cited
> list in a field between subsequent years increases from 0.25 when
> 1,000 papers are published in the focal year to 0.74 when 100,000
> papers are published yearly." (p. 2.)

> "When a field is small, papers rise slowly over time into the top
> 0.1% most cited, consistent with a process of cumulative attention
> gathering. ... [In the largest fields] the same regression predicts
> a median of less than a year for papers to reach the top 0.1%."
> (p. 3.)

> "While the most-cited article in molecular biology was published
> in 1976 and has been the most-cited article every year since 1982,
> one would be hard pressed to say that the field has been stagnant.
> ... Could we be missing fertile new paradigms because we are locked
> into overworked areas of study?" (p. 4 — closing paragraph.)

> "When the number of papers published in a field is 10 times larger,
> a citation by the same author is about 2% more likely to refer to a
> top 0.1% or 1% most-cited paper. ... The estimated effect of field
> size at entry is 16–30 times smaller. These regressions suggest
> even established, veteran scholars are forced to change their
> reading and citation patterns when fields grow large." (SI p. 3.)

---

## Study Questions

**Warm-up (Level 1):**

1. **SQ1** — What does "ossification of canon" mean operationally
   in this paper? What metric captures it, and what value of that
   metric corresponds to high vs. low ossification?

2. **SQ2** — Why does field size matter for the *individual*
   experience of doing science (as a reader, reviewer, or author)?
   State the cognitive argument in your own words.

3. **SQ3** — The Gini coefficient of citation share reaches 0.5 in
   the largest fields. Why is comparing this to country-level
   income inequality a useful framing, and where does the analogy
   break down?

**Intermediate (Level 2):**

4. **SQ4** — There are six predictions across three substantive
   dimensions. Name the three dimensions and explain why each has
   *two* predictions rather than one. What does the
   two-predictions-per-dimension structure buy them?

5. **SQ5** — Why bin field-years by log₁₀N rather than treating N
   linearly? What does the within-bin regression of next-year
   citations on this-year citations actually measure?

6. **SQ6** — How do they argue field size matters above and beyond
   field age (SI Table S1)? What's the residual concern after their
   controls, and how would you sharpen the test?

**Advanced (Level 3):**

7. **SQ7** — Spearman rank correlation Δ=1 vs. Δ=5 vs. cumulative.
   What does the choice of lag affect substantively, and why might
   ws2 prefer Δ=5 over their Δ=1?

8. **SQ8** — Period vs. cohort decomposition (SI Tables S2/S3): walk
   through the identification strategy. What does "current field
   size effect dominates entry-year field size effect by 16–30×"
   actually claim about scholar adaptation, and what doesn't it
   claim?

9. **SQ9** — Disruption predictions 5–6 rest on the Wu-Wang-Evans
   2019 disruption measure D, which inherits Funk-Owen-Smith
   CD-index machinery. Given the Petersen-Arroyave-Pammolli 2024
   citation-inflation critique and Holst et al. 2024 dataset-artifact
   critique, how load-bearing are these predictions for the paper's
   substantive thesis?

10. **SQ10** — They use 241 WoS subjects as field definitions.
    OpenAlex's concept-tag classification is a different beast —
    finer-grained, hierarchical, machine-assigned with confidence
    scores. What kind of result would re-classification preserve
    vs. break?

---

## Challenge Corner

**C1:** The paper's central causal claim is "field size →
canonical-concentration shift." Field size and field age are
correlated (in CS, r ≈ 0.97; in math, r ≈ 0.95). Their controls
(year, year-dummies, subject-FE) help, but they concede the design
isn't causally identified. Beyond field-age confounding, what other
plausible confounds threaten the claim? (Candidates: methodological
maturation, dominance of mega-collaborations in HEP-style fields,
shift in citation-norm conventions, journal-hierarchy emergence,
introduction of preprint platforms.) Which of these are testable
with WoS data, and which would require external data?

**C2:** Δ=1 vs. Δ=5 vs. cumulative Spearman rank correlation. Each
captures a slightly different notion of "canon stability":
- **Δ=1:** "is this year's top-50 the same as next year's?" —
  short-window stability, sensitive to single-year measurement noise.
- **Δ=5:** "is this year's top-50 the same as the top-50 five years
  later?" — medium-window stability, less noisy but might miss fast
  ossification dynamics.
- **Cumulative:** "of the top-50 in year Y, how many are still in
  top-50 in year Y+10?" — slow-decay framing, captures durable
  dominance directly.
Why might ws2's Δ=5 choice be load-bearing for our findings? What
would we lose by going to Δ=1 (matching Chu-Evans exactly)? What
would we gain?

**C3:** WoS 241-subject classification vs. OpenAlex concept-tag
classification. The two are structurally different — WoS is curated
and discrete; OpenAlex is hierarchical, machine-assigned, with
confidence scores. If we re-ran Chu-Evans's analysis on OpenAlex
concept-tag-defined fields rather than WoS subjects, which findings
would most likely persist (operationalization-robust)? Which would
most likely change (operationalization-dependent)? What does this
say about whether their findings are about "canon ossification" as
a fundamental phenomenon or about "WoS classification + citation
dynamics" specifically?

**C4 (closed via calibration; see Discussion Notes):** Two theoretical
mechanisms are advanced (cognitive overload + sandpile criticality)
but not directly tested. The paper's empirical pattern is consistent
with both, and also with simpler explanations (Matthew /
preferential attachment, journal-prestige entrenchment).
**Out of ws2 scope** — our use of Chu-Evans is methodological +
empirical, not mechanistic. Resolution captured in Discussion Notes.

**C5:** Predictions 5–6 (disruption) rely on the Wu-Wang-Evans 2019
D measure, which is in the Funk-Owen-Smith CD-index family.
Petersen-Arroyave-Pammolli 2024 demonstrates that CD-index is
biased by citation inflation; Holst et al. 2024 demonstrates that
CD-index is biased by dataset artifacts (specifically, missing
references in older WoS records make older papers look more
"disruptive" than they are). Both critiques apply to D as well.
Two sub-questions:

(a) Are Chu-Evans's predictions 5–6 (disruption decline with field
size) compromised by these critiques? Note that their IV is field
size, not time-as-such; the critiques attack the disruption *measure*
across time, but Chu-Evans is comparing across fields. How does
this affect the bias-direction analysis?

(b) ws2 has excluded CD-index from primary canonical metrics. How
should we engage Chu-Evans predictions 5–6 in our Discussion? Three
options: (i) cite them as supportive context with a caveat; (ii) cite
them as contested findings and don't lean on them; (iii) attempt
inflation-corrected disruption replication on our OpenAlex data as
a secondary analysis.

**C6:** Field size = annual paper count vs. cumulative literature
size. The cognitive-overload mechanism arguably ties more to
cumulative size (how much past work there is to know about) than to
annual count (how much new arrives per year). Both are correlated
across the 1960–2014 window but they are distinct operationalizations.
Two sub-questions:

(a) If we re-ran Chu-Evans with cumulative literature size as the IV
instead of annual paper count, which findings would most plausibly
persist or strengthen, and which would weaken? (Hypothesis: the
durable-dominance findings would strengthen — old top-cited papers
benefit cumulatively from a larger literature anchoring on them; the
entrepreneurial-futility findings would weaken — fast-rising new
papers in fast-growing fields can still grab attention if cumulative
literature is moderate.)

(b) For ws2: should we report canonical concentration vs. annual
paper count (matching Chu-Evans) or vs. cumulative literature size
(arguably more mechanistic)? Or both?

**C7:** Period dominates cohort by 16–30× (SI Tables S2/S3). For
ws2's demographic-vs-semantic divergence, this implies *all* scholars
in a 2010s field — including those who entered when the field was
small — are responding to current field size by citing canon more.
For our subfield mechanism test (CanonConc_s on DivMag_s) and
specifically for the actuator-homogenization story (13-A in compass),
this suggests:

- Within-subfield divergence cannot be explained as "old guard
  cohorts kept producing canon-eccentric work while new cohorts
  conformed." All cohorts converge on current canon.
- Therefore, if demographic plurality rose while semantic plurality
  fell, it can't be attributed to "diverse new cohorts producing
  canon-eccentric work that pushes back against ossification" —
  because Chu-Evans says new cohorts conform to current canon just
  as much as old ones.

Does this strengthen or weaken the actuator-homogenization
interpretation of a positive divergence finding? Does it shift our
expected sign on Test IV's γ₁?

**C8:** Their Gini coefficient is computed on within-field-year
citation share. Our Gini-on-citation-distribution-across-papers is
similar. Both implicitly treat "field-year" as a well-defined
analytical frame for that year's citation flow. But citations don't
respect annual boundaries — a paper published in 2010 still receives
citations from 2014 papers. The "year" in "field-year" is the year of
the *citing* paper or the *cited* paper, depending on how you slice
it. Chu-Evans uses citing-year throughout (citations *to* a focal
paper *from* same-subject papers in the same year as the citing
paper). What's the implicit assumption, and how would findings
change under cited-year framing?

**C9:** Chu-Evans's classification is exogenously imposed (WoS
subjects). Our cluster-fit-on-temporally-stratified-subsample
(desiderata §11) is a different methodological move — fitting
classification on a balanced subsample to avoid modern-era cluster-
definition bias. Both are responses to the "imposed-vs-data-driven
classification" question, but they answer different sub-questions:

- Chu-Evans accepts an exogenous classification and asks "what do
  citation dynamics look like across these classes?"
- Our cluster fit derives a classification from data and asks "how
  does that classification's apparent diversity evolve over time?"

The methodological lesson: where do we place the burden of
classification stability? Chu-Evans places it on the database
provider (Clarivate); we place it on a stratification choice we
control. Both are defensible. But it raises a sharper question for
ws2: would Chu-Evans's findings replicate on cluster-derived field
boundaries? Probably yes for durable dominance (top-cited papers
would still ossify within cluster), probably ambiguous for
entrepreneurial futility (clusters might split or merge as they grow,
breaking the field-size IV).

**C10:** The substantive bridge to ws2's actuator-homogenization
story (compass 13-A): Chu-Evans documents *entrepreneurial futility* —
new papers can't reach canon through gradual diffusion in large
fields. If entrepreneurial futility is real, the *kinds* of new
papers that get produced should shift toward low-risk canon-centric
work (since high-risk canon-eccentric work is filtered out at the
production-and-publication stage). This is a production-stage
mechanism for reduced semantic diversity. Chu-Evans don't measure
semantic diversity, but their finding is structurally consistent with
ws2's expectation that semantic plurality declines or stagnates in
the era when annual paper counts grew.

The challenge: is this connection load-bearing for ws2's
interpretation, or is it incidental? If we find demographic-vs-
semantic divergence (Tests I-III positive), how much should we lean
on Chu-Evans as upstream-mechanism support, and how much should we
position our finding as orthogonal to theirs? (Risk of leaning too
hard: their disruption findings — which are structurally adjacent to
"semantic diversity declined" — are CD-index-contaminated, so we'd
be importing an underlying methodological dependency we explicitly
rejected.)

**C11:** Chu-Evans aggregate at the subject level (n=241 WoS
subjects). Our analysis is at the field-and-subfield level (CS,
Physics; ~10–50 subfields per field). Their unit-of-aggregation
choice is *coarser* than ours. What's gained vs. lost at each
aggregation level? Specifically:

(a) Their field-size effects might wash out within finer subfields
if subfields don't experience the cognitive-overload regime
individually (e.g., a researcher in cs.LG might only attend to cs.LG
papers, not all CS papers). Their effects might be artifacts of
within-CS subdisciplinary aggregation.

(b) Conversely, our subfield-level analysis might miss the
field-wide attention-economy effects that operate through field-wide
journals, conferences, and prestige hierarchies. A researcher in
cs.LG still attends to NeurIPS plenaries and field-wide
celebrity-paper coverage.

What's the right scale for the cognitive-overload mechanism, and how
should we report at multiple scales to cover both possibilities?

---

## Synthesis Pointers (for `synthesis.md`)

1. **Chu-Evans Spearman top-50 is the empirical backbone of ws2's
   canonical-concentration time series.** Direct methodological
   inheritance for our primary canonical metric. The Δ=5 vs. Δ=1
   choice and the N=50 vs. N=100/500 choices are operationalization
   parameters under their established framework.

2. **Period dominates cohort (SI S2/S3) supports time-FE specification
   throughout ws2.** Test IV's year-FE; Tests I-III's annual time
   series treating each year as an independent observation; the
   subfield mechanism test's per-year subfield aggregates — all are
   defensible in the Chu-Evans Period-dominant world.

3. **Field-size confound for subfield mechanism test.** Chu-Evans
   documents that field size drives canonical concentration. The
   subfield mechanism regression (CanonConc_s on DivMag_s) must
   control for log subfield size to avoid CanonConc_s being a
   noisy measurement of "this subfield got bigger."

4. **Disruption predictions (5–6) require Petersen-Holst-mediated
   engagement.** Their findings on declining disruption with field
   size cannot be cited as direct support for ws2's
   actuator-homogenization story without engaging the CD-index
   critique chain. Synthesis pointer for Discussion.

5. **Connection to compass 13-A (actuator homogenization):** Chu-Evans
   provides a production-stage mechanism (entrepreneurial futility →
   low-risk canon-centric work) consistent with ws2's expectation of
   reduced semantic diversity in modern eras. But we should not lean
   hard on this — their disruption-side evidence is CD-index-
   contaminated; their durable-dominance-side evidence is upstream
   of canonical concentration but not of semantic diversity per se.

6. **Operationalization-divergence flag:** Chu-Evans uses annual
   paper count for "field size"; cumulative-literature operationalization
   would arguably better capture the cognitive-overload mechanism.
   Sensitivity check candidate for ws2 Stage 2.

7. **Hofstra ↔ Chu-Evans interaction.** Hofstra studies dissertations
   (production stage); Chu-Evans studies citations (reception stage).
   Both find that the demographic-or-novelty-eccentric input is
   under-rewarded in field-wide attention. Different mechanisms
   (Hofstra: discrimination/distal-novelty mediation; Chu-Evans:
   cognitive overload + canon entrenchment), but compatible. ws2's
   3-panel decomposition + Test IV cross-section is the empirical
   bridge across the two.

8. **Cohort-mix interpretation handling (Chu-Evans SQ8 walkthrough,
   2026-04-26).** Chu-Evans's period-dominance finding (period
   effects 16–30× larger than cohort effects within-author) bounds
   the cohort-mix interpretation of any aggregate ws2 divergence
   finding toward unlikely *a priori*, but the inheritance isn't
   airtight (their evidence is for citation behavior, not semantic
   output of papers). ws2 commits to a Discussion-section paragraph
   leveraging Chu-Evans as upstream evidence, plus a Stage 3
   simplified cohort decomposition (per (publication year ×
   lead-author cohort) bins, semantic diversity trajectories). Full
   author-FE within-author longitudinal analysis on semantic output
   is deferred as back-pocket (Option C).

9. **Decoupled-subfield robustness check (Chu-Evans SQ6 walkthrough,
   2026-04-26).** Chu-Evans's identification-defense move (Fig. S1)
   examines subjects where year and field size are weakly
   correlated, showing that size-effects on citation dynamics
   persist in those decoupled subjects. ws2 inherits an analogous
   threat — observed demographic-vs-semantic divergence could
   reflect two unrelated time trends rather than a real decoupling.
   Commitment: per-subfield year–log-size correlation; pre-registered
   thresholds (r < 0.5, r < 0.7, r < 0.9) define decoupled subsets;
   headline tests replicated on each subset; pre-registered
   interpretive grid. Captured in pending Phase 0.2 batch.

10. **Classification-substrate acknowledgment (Chu-Evans C3
    walkthrough, 2026-04-26).** WoS subjects (n=241, stable, sparse)
    vs. OpenAlex concept tags (~65K, drifting, dense) are structurally
    different classification substrates. ws2 uses Chu-Evans's
    Spearman top-N methodology but cannot claim direct replication
    of their coefficient values; classification-substrate confound
    on any qualitative-pattern difference is unresolvable without
    parallel analysis. Commitment: Methods-paragraph acknowledgment
    + status-quo methodology-inheritance framing; cross-substrate
    Stage 3 robustness deferred as back-pocket. Captured in pending
    Phase 0.2 batch.

11. **Subfield mechanism test nonlinearity check (Chu-Evans
    bin-and-regress critique, 2026-04-26).** Chu-Evans's
    bin-and-regress strategy has a known weakness: bin-cutpoint
    choice is arbitrary and a regime shift falling within a bin
    gets averaged out. Their headline patterns are partially
    mitigated by LOWESS smoothing in the figures, but the underlying
    linear-relationship assumption when applied to ws2's subfield
    mechanism test (DivMag_s = γ_0 + γ_1·CanonConc_s + ...) carries
    the same vulnerability — if the CanonConc → DivMag relationship
    has regime structure, a linear fit smears it. Commitment:
    quadratic term (γ_2·CanonConc_s²) added to the regression spec;
    LOWESS visualization reported as a diagnostic alongside the
    linear fit. ~Half-day Stage 2 effort. Captured in pending
    Phase 0.2 batch.

---

## Discussion Notes

(Filled during collaborative review session. Blank until that session
happens.)

### On C1 — alternative confounds beyond field-age

(Pending.)

### On C2 — Spearman lag choice (Δ=1 / Δ=5 / cumulative)

(Pending.)

### On C3 — WoS subjects vs. OpenAlex concept tags

Working session with user, 2026-04-26.

**Structural differences in classification substrate.**

- *Granularity.* Chu-Evans uses WoS subjects (n=241). OpenAlex concept
  tags are ~65K concepts in a hierarchical tree. ws2 uses a hybrid
  subfield assignment at ~10–50 per field — finer than WoS subjects,
  coarser than raw OpenAlex concepts.
- *Stability.* WoS classification is curated and slow-changing;
  OpenAlex concepts evolve over time (hierarchy updates + classifier
  improvements). ws2's plan §3 classifier drift mitigation is the
  response.
- *Per-paper noise.* WoS subject tags are sparse/discrete (1–few per
  paper). OpenAlex concept tags are dense/probabilistic (5–15 per
  paper with confidence scores). ws2 commits to "highest-confidence
  concept tag or primary arXiv category" for primary subfield
  assignment.
- *Coverage.* OpenAlex covers more papers — non-English, open-access,
  non-Western institutions. **Advantageous for ws2 demographic-plurality
  measurement** (WoS would systematically under-sample non-Western
  authorship in ways that would confound demographic metrics; this
  was a load-bearing reason for using OpenAlex over WoS in the first
  place — see Hofstra C8 walkthrough).

**Three concrete implications for ws2.**

*(A) We cannot directly cite Chu-Evans's coefficient values.* Their
Spearman correlation rises from 0.25 (N=1K) to 0.74 (N=100K). Those
specific numbers are tied to their classification substrate. Our
Spearman values will differ — possibly substantially — even if the
qualitative pattern matches. We can say "we apply their methodology"
but not "we replicate their coefficients."

*(B) Classification-substrate confound on our findings.* If our
canonical-concentration time series differs in shape from Chu-Evans's,
three explanations are possible and not separable without parallel
analysis on both substrates: (i) real difference in dynamics across
1970–2024 vs. 1960–2014; (ii) real difference in subfield-level vs.
subject-level dynamics; (iii) classification-substrate artifact —
OpenAlex tags vs. WoS subjects producing different patterns on the
same data. We won't decompose these without WoS data access (not in
ws2 plan).

*(C) ws2 carries an identification burden Chu-Evans doesn't.* Their
WoS classification is stable; ours drifts. We must argue that our
canonical-concentration findings aren't artifacts of classifier
drift, *on top of* the size-vs-time threat (which they also face).
Our identification problem is structurally harder.

**Three options considered.**

*(1) Status quo — methodology inheritance, no replication claim.*
Use Chu-Evans's Spearman top-N methodology; cite as methodological
precedent; explicitly disclaim direct replication. Position findings
as "Chu-Evans-style canonical concentration applied to OpenAlex
data." Free effort.

*(2) Methods-paragraph acknowledgment.* Add a Methods paragraph
(approximately five sentences) explicitly stating substrate
difference, that quantitative coefficient comparisons are not
meaningful, and that we treat Chu-Evans as methodological precedent
rather than direct comparison.

*(3) Cross-substrate Stage 3 robustness (back-pocket).* Run the
analysis on the WoS-OpenAlex overlap subset where both classifications
agree. Requires WoS data access (not in ws2 plan, would require
Clarivate negotiation or partner institution). High cost.

**Decision (committed): (1) + (2); keep (3) as back-pocket.** The
Methods-paragraph acknowledgment (2) is cheap, defensible, and
pre-empts the natural reviewer question without forcing the
expensive cross-substrate analysis. Structurally parallel to the
cohort-mix handling pattern (SQ8) and the windows-as-estimand
handling (Hofstra C10): address the concern proportionately in
Methods, do lightweight ws2-specific checks where applicable, defer
expensive versions.

Phase 0.2 batch addition captured separately in
`docs/phases/phase-0.1-plan.md`.

### On C4 — direct tests of cognitive overload and sandpile mechanisms

Closed via calibration discussion, 2026-04-25 (not a full walkthrough).

The mechanism-which-is-it question is **out of ws2 scope**. Chu-Evans
offer two mechanisms (cognitive overload + canon anchoring; sandpile
critical-state interference); simpler accounts (Matthew /
preferential attachment; journal-prestige entrenchment) predict the
same τ-collapse pattern through different mechanisms; Chu-Evans do
not adjudicate. Our use of Chu-Evans is methodological + empirical,
not mechanistic — we inherit Spearman top-N and cite the empirical
pattern, but do not commit to any specific mechanism. A direct test
of either Chu-Evans mechanism would require infrastructure ws2
doesn't have (longitudinal attention/cascade measurement on citation
networks at fine temporal resolution; cognitive-process measurement
on actual reviewers). The C4 question stands as legitimate scientific
inquiry but is out of scope for ws2 design or interpretation. See
the "Mechanism-pluralism" subsection of Connection to Our Project
for the resolution.

### On C5 — disruption predictions under CD-index critique

(Pending.)

### On C6 — annual count vs. cumulative literature size

(Pending.)

### On C7 — period-dominance implications for actuator-homogenization

(Pending.)

### On C8 — citing-year vs. cited-year framing of citation flow

(Pending.)

### On C9 — exogenous classification vs. data-derived clustering

(Pending.)

### On C10 — leaning on Chu-Evans as upstream mechanism for ws2

(Pending.)

### On C11 — aggregation scale (field vs. subfield) for cognitive overload

(Pending.)

---

## Study Question Walkthroughs

(Answers worked through collaboratively in review sessions. Each
entry preserves the arc of initial intuition → sharpening → final
version. Questions not yet worked through are marked `(Pending)`.)

### SQ1 — What does "ossification of canon" mean operationally?

(Pending.)

### SQ2 — Cognitive argument for why field size matters

(Pending.)

### SQ3 — Gini coefficient and the country-inequality analogy

(Pending.)

### SQ4 — Six predictions across three dimensions

Working session with user, 2026-04-26.

**The three dimensions and their two predictions each.**

| Dimension | Prediction 1 | Prediction 2 |
|---|---|---|
| **Durable dominance** | Citations flow disproportionately to top-cited papers (Gini ↑) | Top-cited list ossifies (top-50 Spearman ↑) |
| **Entrepreneurial futility** | P(new paper reaches canon) drops (p ↓) | When new papers do reach canon, not gradually (τ ↓) |
| **Reduced disruption** | Proportion of D > 0 papers declines | Proportion of top-5%-disruption papers declines |

**What the two-predictions-per-dimension structure buys.**

*(1) Concept-coverage check.* Each dimension is a substantive concept
that has multiple measurable manifestations. The two predictions
together pin down the concept; either alone is ambiguous.
- "Durable dominance" requires both *concentration* (citations flow
  to a few) AND *identity persistence* (the same papers stay top).
  High Gini + low Spearman = "concentrated but churning" — not
  durable dominance. Low Gini + high Spearman = "stable list but no
  dominance." Both together = the concept applies.
- "Entrepreneurial futility" requires both *rare entry* AND *broken
  gradual path*. Just rare entry is consistent with "selective but
  gradual still works"; just broken gradual path is consistent with
  "everyone who enters does so fast." Both together = the gradual-
  attention path is gone, period.
- "Reduced disruption" requires both *distribution-level shift* AND
  *extreme-tail shrinkage*. Either alone is consistent with simpler
  stories.

*(2) Robustness against operationalization-dependence.* Each prediction
uses a specific metric. If only one prediction per dimension confirmed,
the finding could be an artifact of that metric. With both confirmed
via different metrics, the finding is robust to operationalization
choice.

*(3) Reduces false-positive probability under chance.* Six predictions
all going the same direction is unlikely under a null where each is
independent and chance-driven.

**For ws2.** This pattern matches our compass + desiderata §8
commitment: ≥2 metrics per substantive dimension (Shannon + Gini +
Rao for demographic; cluster entropy + effective dim + pairwise
distance for semantic; Spearman top-N + citation Gini for canonical).
Chu-Evans's six-prediction structure is methodologically what we
already aim for with our four-co-primary-tests + multi-metric
reporting. No new commitments — confirms existing design pattern.

### SQ5 — Why bin by log₁₀N? What does within-bin regression measure?

Working session with user, 2026-04-26.

**Part A: Why log₁₀N rather than linear N?**

Field sizes span ~3–4 orders of magnitude (~100 papers/year in small
subjects to ~100,000+ in mega-fields). Three reasons for log scale:

*(1) Distribution shape.* Linear N is heavily right-skewed with most
data clustering at low values. Log binning makes the distribution
more uniform across the range; each bin gets reasonable data density.
Linear binning would either give huge high-N bins with sparse data
or tiny low-N bins with most observations.

*(2) Coefficient interpretability.* Log₁₀N units correspond to 10×
multiplicative changes. "A 10× increase in N produces X effect" is
more useful than "an additional 1000 papers produces X effect"
(which depends sensitively on baseline N).

*(3) Theoretical match.* Preferential-attachment dynamics scale
multiplicatively, not additively. A paper at the 99th percentile of
a 10K-paper field is structurally analogous to a paper at the 99th
percentile of a 100K-paper field. Log scale captures this proportional
structure.

**Part B: What does the within-bin regression measure?**

Within each (log₁₀N range × citation percentile) cell, regress
year-(Y+1) citations on year-Y citations for papers in that cell.
The regression coefficient is **the citation decay rate** (technically
1−λ where λ is the loss rate per year).

Interpretation by coefficient value:
- **Coefficient = 1:** papers retain all their citations year over
  year (no decay).
- **Coefficient < 1:** papers lose citations year over year.
- **Coefficient > 1:** papers gain citations year over year (rich-
  get-richer dynamics).

Headline finding: in large fields, the coefficient → 1 for top-
percentile papers (their citations don't decay) but stays substantially
< 1 for all other percentiles (everyone else's citations decay). In
small fields, coefficient is similar across percentiles (all papers'
citations decay at roughly the same rate).

**Why within-bin?** The relationship between percentile and decay
rate isn't linear. Stratifying by both field size AND percentile
lets the data reveal the joint structure: at what combination of
(field size, percentile) does the rich-get-richer-and-everyone-else-
loses dynamic kick in?

**Substantive payoff.** The within-bin regression localizes the regime
change. It's not just "fields above 100K papers/year ossify" — it's
"fields above 100K papers/year ossify *specifically because top-
percentile papers stop decaying while everyone else continues
decaying.*" The decay-rate decomposition is the mechanism-localization
piece.

**For ws2.** We don't directly use within-bin citation-decay regression
for canonical concentration — Spearman top-N is a different
operationalization. The broader methodological pattern (log-binning
skewed continuous variables; stratifying by another covariate to
localize regime structure) we partially adopt (log subfield size as
control in subfield mechanism test). Could potentially extend to
year × subfield-size stratified plots of canonical concentration as
a Stage 2 visualization choice; not a Phase 0.2 commitment.

**Connection to user's bin-and-regress critique** (separate
walkthrough): the within-bin regression is exactly where the bin-
choice arbitrariness has bite. A regime shift falling within a
specific (log₁₀N range × percentile) cell gets averaged out. Their
LOWESS smoothing in the figures partially mitigates for the headline
patterns; the within-bin decay-rate analysis is the most bin-
sensitive part of their methodology. ws2's nonlinearity check
(quadratic + LOWESS on subfield mechanism test) addresses the
analog concern in our design.

### SQ6 — Field size vs. field age (SI Table S1)

Working session with user, 2026-04-26.

**The threat.** Chu-Evans's central claim is "bigger fields → canon
ossifies." Their evidence is correlational: at a given moment, fields
with larger N have higher top-50 Spearman correlation; longitudinally
within a field, as N grows, Spearman rises. The immediate counter:
maybe it's not size — it's just time. Fields mature, accumulate
canon, and naturally ossify. Size and time are correlated within
most fields, so distinguishing their effects requires structure.

**Their identification strategy (Table S1).** Regress top-50 Spearman
correlation on log₁₀N + time controls + subject FE.

- Model 1: log₁₀N + year (continuous) + subject FE
- Model 2: log₁₀N + year-dummies + subject FE

The year terms absorb common-across-subjects time effects. What
remains for log₁₀N to explain is *the deviation of a subject's
Spearman from what year-effects-alone would predict, attributable to
that subject's specific N.*

Result: log₁₀N coefficient = 0.091 (Model 1), 0.090 (Model 2), both
p<0.001. **A 10× field-size increase is equivalent in effect to ~15
years of field maturation** (0.090 ÷ 0.006 ≈ 15). Size matters after
time is absorbed.

**The residual concern they acknowledge.** Year and field size are
heavily collinear within most subjects — Pharmacology r=0.95, Math
r=0.95, CS r=0.97–0.98. With near-perfect collinearity, separating
year and log₁₀N coefficients is statistically thin; the regression
machinery is leaning on a sliver of variance.

**Their robustness move (Fig. S1).** Examine subjects where year
and size are *less* correlated:
- Biochemistry & Molecular Biology: r = 0.32
- Applied Physics: r = 0.58

In these decoupled subjects, citation-dynamics-by-field-size patterns
are similar to the highly collinear subjects. So when size and time
*can* be cleanly separated (because they don't move together), size
still predicts citation dynamics. This is the move that distinguishes
"size matters" from "size is just time in disguise."

**Residual concern after the robustness move.** Year controls absorb
common-across-fields time effects but not *field-specific* time
effects. A subfield could have its own time-trajectory dynamics
(e.g., maturation pattern specific to ML post-2012, or specific to
HEP post-Higgs) that aren't captured by year-dummies (which absorb
the common trend across all fields, not idiosyncratic per-field
trends). The decoupled-subjects evidence partially mitigates this
but doesn't fully address it.

**Implications and commitment for ws2.** The same identification
threat applies to ws2's headline divergence findings. If we observe
demographic plurality rising while semantic plurality falls, one
plausible alternative: the divergence is two unrelated time trends
(demographic-pluralization-over-time + canon-ossification-with-
field-size) rather than a real demographic-vs-semantic decoupling.

**ws2 commits to a Chu-Evans-style decoupled-subfield robustness
check** (added to pending Phase 0.2 batch in `docs/phases/
phase-0.1-plan.md`):

- For each subfield s in our analysis, compute within-subfield
  correlation between calendar year and log subfield size over
  1970–2024.
- Sort subfields by correlation; identify "decoupled" subset using
  pre-registered thresholds (r < 0.5, r < 0.7, r < 0.9 — multi-
  threshold reporting).
- Replicate Tests I–III, subfield mechanism test, and Test IV on
  the decoupled subset.
- Pre-registered interpretive grid:
  - Divergence holds in decoupled subfields → robust to time
    confound.
  - Divergence weakens → time confound contributes; magnitude
    estimable.
  - Divergence reverses → strong evidence full-sample finding is
    time-confounded; substantively interesting null.
  - Decoupled subfield count too low (<5 per field) → document
    inheritance of Chu-Evans's residual field-specific-time-effect
    concern; can't perform check.

### SQ7 — Spearman lag choice (Δ=1 / Δ=5 / cumulative)

(Pending.)

### SQ8 — Period vs. cohort decomposition (SI Tables S2/S3)

Working session with user, 2026-04-26.

**Cohort vs. period vs. age** (the standard age-period-cohort
identification triangle). For any individual scientist, three time
variables are linearly related: age = period − cohort. Without
restrictions, you can't separately identify all three.

For Chu-Evans:
- **Cohort** = year of first publication (entry-year).
- **Period** = year of citing paper publication.
- **Age** = career stage at time of citing paper.

**Two competing hypotheses Chu-Evans test.**

*Cohort hypothesis:* scholars are imprinted by training-era field-size
conditions; imprinting persists across careers. Aggregate citation-
pattern shifts are driven by **generational replacement** — old-cohort
scholars retire, new-cohort scholars replace them, mix-shift drives
aggregate change.

*Period hypothesis:* scholars adapt to current field-size conditions
regardless of entry-cohort. Aggregate shifts are driven by
**current-state adaptation**, not generational replacement.

These differ in within-author predictions: under cohort-dominance,
within-author citation patterns are stable across career; under
period-dominance, within-author patterns track current field size.

**Their identification strategy.**

*Table S2 — within-author variation (author FE).* Regress p(citation
to top 0.1% / 1% / bottom 50%) on log₁₀N (current field size) and
year, with author fixed effects. Author FE absorbs all time-invariant
author characteristics including cohort. The remaining log₁₀N
coefficient identifies within-author variation: same author, different
publication years, different field sizes. Result: log₁₀N coefficient
= 0.018 to 0.021 for top-percentile DVs, p<0.001. The same author
cites top-cited papers more when the field is large than when it's
small. Rules out cohort-replacement as the driver — generational
turnover can't explain within-author shifts.

*Table S3 — direct period-vs-cohort comparison.* Regress same DVs on
log₁₀N (period) AND log₁₀Ne (entry-year field size, the cohort
variable) WITHOUT author FE. Both coefficients identifiable. Result
for top 0.1%: period 0.028–0.030 vs. cohort 0.001 (period 28–30×
larger). For top 1%: period 0.064–0.065 vs. cohort 0.004 (16× larger).
Period dwarfs cohort.

**The substantive claim.** Even veteran scholars trained in a small-
field era change their citation behavior when the field grows large.
Imprinting effects exist but are dwarfed by current-state adaptation
by 16–30×.

**Identification caveats (what the regressions don't airtight rule
out).**

- *Within-author variation conflates period and age.* Same author
  publishing over 30 years also gets older over those 30 years.
  Author FE absorbs cohort but not age. The `year` control partially
  absorbs age but the separation isn't perfect. Possible alternative:
  older scholars cite top-cited papers more for reasons unrelated to
  field size (defending established research program, teaching
  habits, consolidation).
- *Field-specific (Electrical & Electronic Engineering only).*
  Generalization to other fields is plausible but not directly
  demonstrated. Different citation cultures or career-length
  distributions could shift the period-vs-cohort balance.

**Implications for ws2 — three substantive consequences.**

*(1) Time-FE specification confirmed.* Test IV uses year-FE (current
publication year), not author-entry-year (cohort). Chu-Evans support
this — current-period adaptation is operative; we don't need cohort
controls in the primary specification.

*(2) Weakens "old-guard cohort" interpretation of any divergence
finding.* If we find demographic diversity rising while semantic
diversity falls, a tempting alternative interpretation is "old-guard
cohorts trained pre-1990 kept producing canon-eccentric work; new
cohorts conform; aggregate semantic diversity falls as cohort mix
shifts." Chu-Evans say no — even old-guard cohorts conform when the
field grows. So if we observe homogenization, we *cannot* attribute
it to cohort selection. Homogenization affects everyone.

*(3) Strengthens "structural mechanism" framing for compass 13-A.*
Whatever's compressing semantic diversity in large fields operates
on all scholars, not on a specific cohort or generation. Consistent
with sandpile / Matthew / journal-prestige / cognitive-overload
accounts (mechanism-agnostic to who-is-citing); inconsistent with
imprinting / generational stories.

**Does ws2 need to do its own period-vs-cohort regression?**

Three options considered (in ascending order of effort):

*Option A — Discussion-section acknowledgment + cite Chu-Evans
period-dominance.* Cite Chu-Evans as upstream evidence that within-
field cohort imprinting is weak. Their evidence is for citation
behavior, not semantic-output of papers, so the inheritance isn't
airtight, but it's the closest direct evidence available. Free
effort; Discussion-section paragraph + citation.

*Option B — Stage 3 simplified cohort decomposition.* For each paper,
identify lead author's first-publication year as cohort proxy. Bin
papers by (publication year × lead-author cohort), compute mean
semantic diversity per bin, plot trajectories. Read interpretation
off pattern: all cohorts slope similarly → period effect operative;
divergent cohort-trajectories → cohort effect operative. ~1 week
Stage 3 effort; uses existing OpenAlex data; no new API calls.

*Option C (back-pocket) — full Chu-Evans-style within-author
longitudinal analysis on semantic output.* Define per-author
semantic-diversity-output construct (e.g., variance of an author's
papers' embeddings); take authors who published in both early and
late eras; fit author-FE regressions with current canonical
concentration as period predictor. Methodologically heavy: author
disambiguation at scale (compounds the C8 issue), long-career-author
selection bias, novel construct definition. 2–3 weeks Stage 3
methodology work + own validation pipeline. Deferred unless Option
B leaves cohort-mix question unresolved.

**Decision (committed):** **Combine A + B; keep C as back-pocket.**
The Discussion paragraph (A) leverages existing evidence; the Stage 3
decomposition (B) provides ws2-specific data; (C) is fallback if B's
results are ambiguous. Phase 0.2 batch additions captured separately
in `docs/phases/phase-0.1-plan.md`.

### SQ9 — Disruption predictions under CD-index critique

(Pending.)

### SQ10 — WoS subjects vs. OpenAlex concept tags

(Pending.)
