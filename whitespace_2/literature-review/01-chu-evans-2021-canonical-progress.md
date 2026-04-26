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

---

## Discussion Notes

(Filled during collaborative review session. Blank until that session
happens.)

### On C1 — alternative confounds beyond field-age

(Pending.)

### On C2 — Spearman lag choice (Δ=1 / Δ=5 / cumulative)

(Pending.)

### On C3 — WoS subjects vs. OpenAlex concept tags

(Pending.)

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

(Pending.)

### SQ5 — Why bin by log₁₀N? What does within-bin regression measure?

(Pending.)

### SQ6 — Field size vs. field age (SI Table S1)

(Pending.)

### SQ7 — Spearman lag choice (Δ=1 / Δ=5 / cumulative)

(Pending.)

### SQ8 — Period vs. cohort decomposition (SI Tables S2/S3)

(Pending.)

### SQ9 — Disruption predictions under CD-index critique

(Pending.)

### SQ10 — WoS subjects vs. OpenAlex concept tags

(Pending.)
