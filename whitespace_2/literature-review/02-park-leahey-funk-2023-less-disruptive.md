# 02 — Papers and patents are becoming less disruptive over time

**Authors:** Michael Park, Erin Leahey, Russell J. Funk
**Venue:** *Nature* 613, 138–144 (5 January 2023)
**PDF:** `literature-review/02-park-leahey-funk-2023-less-disruptive.pdf` (gitignored)
**SI:** `literature-review/02-park-leahey-funk-2023-less-disruptive_SI.pdf` (gitignored)
**Peer review:** `literature-review/02-park-leahey-funk-2023-less-disruptive_SI_peerreview.pdf`
(gitignored — Nature publishes peer review for many papers; load-bearing
for understanding the paper's known vulnerabilities)
**DOI:** 10.1038/s41586-022-05543-x

---

## Background

Park, Leahey & Funk 2023 (henceforth PLF) is the contested headline
ws2 is positioning against. The paper claims a universal, robust
decline in scientific and technological disruptiveness over six
decades, measured via the CD index (Funk-Owen-Smith 2017 family) on
~25M Web of Science papers (1945–2010) and ~3.9M USPTO patents
(1976–2010), corroborated across four additional databases (JSTOR,
American Physical Society, Microsoft Academic Graph, PubMed). The
paper's substantive thesis: science is increasingly *consolidating*
existing knowledge rather than *disrupting* it; this represents a
fundamental shift in the nature of discovery and invention attributable
to scientists' and inventors' reliance on a narrower set of existing
knowledge.

PLF is the canonical statement of the "decline of disruption"
narrative in science-of-science. It is the paper that put CD-index-
based decline-claims in front of policymakers (the OECD, NSF, etc.).
It is also the paper that triggered the sharpest published methodological
critiques to date — Petersen-Arroyave-Pammolli 2024 (citation inflation
critique) and Holst et al. 2024 (dataset artifact critique), both in
ws2's Tier 1 reading list.

ws2's relationship to PLF is fundamentally different from our
relationship to Hofstra or Chu-Evans. We do not borrow methodology
from PLF — we explicitly exclude CD-index from primary canonical
metrics per desiderata. Instead, we engage PLF as the contested
headline that any aggregate-divergence finding in ws2 must position
against. Our central question (decoupling of demographic from
intellectual plurality) is adjacent to PLF's central question (decline
of disruptiveness) but distinct: PLF documents a single trend
(disruption ↓); ws2 documents whether two trends (demographic ↑ vs.
semantic ?) covary or decouple. PLF's empirical claims, if true, would
provide one mechanism for the semantic-stagnation half of any
divergence we might observe — but we are not in a position to
validate or extend their substantive claim.

The peer review documents (Nature publishes them as `peerreview.pdf`)
are unusually informative for this paper. Reviewer #2 raised the
exact citation-inflation concern that Petersen-Holst later formalize;
the authors responded with normalization variants (DI^nok, paper-
normalized CD, field × year normalized CD) that partially address
but do not fully resolve the issue. Reviewer #1 raised cross-decade
comparability concerns; Reviewer #3 questioned the Monte Carlo
simulation rationale. The paper got published with these vulnerabilities
acknowledged-but-not-resolved. Petersen 2024 and Holst 2024 are
essentially formalizations of concerns flagged during review.

---

## Key Ideas

### 1. The CD index methodology (Funk-Owen-Smith 2017 family)

The CD index quantifies disruption vs. consolidation via the
network-structural relationship between a focal paper's citing papers
and the focal paper's predecessors:

- For a focal paper p, identify its *predecessors* (the papers p
  cites, "b" set) and its *successors* (papers that cite p, "f" set).
- For each successor s: classify as **Type 1** (cites p but does not
  cite any of p's predecessors — *disrupts* the reference network)
  or **Type 2** (cites both p and at least one predecessor —
  *consolidates*). A third category (cites a predecessor but not p
  itself) gets label *t*.
- CD_5(p) = (1/n_t) × Σ (-2 f_it × b_it + f_it) where the sum is over
  all citations within 5 years of p's publication. n_t is the total
  number of forward citations to p and its predecessors as of time t.
- **Range:** −1 (purely consolidating — every citer cites both p and
  predecessors) to +1 (purely disrupting — every citer cites p but
  ignores predecessors).
- **CD_5:** computed using citations within 5 years of publication.
  Authors also report CD_10 and CD_2017 (using all citations through
  2017) as robustness.

### 2. The headline finding: universal decline

The paper's core empirical claim, in Fig. 2:

- **Papers (WoS, 1945–2010):** average CD_5 declines 91.9% (physical
  sciences) to 100% (social sciences). For example, life sciences
  drops from 0.52 in 1945 to 0.04 in 2010.
- **Patents (USPTO, 1980–2010):** average CD_5 declines 78.7%
  (computers and communications) to 91.5% (drugs and medical).
- **Pattern:** declines are steepest in the early time series and
  begin stabilizing for patents around 2000–2005.

The paper claims the decline is *universal across all major fields*
and *robust across multiple databases* — which is the paper's main
defensive moat against database-specific artifacts.

### 3. The conservation finding (Fig. 4)

A subtle but important secondary claim: while average CD_5 declines,
the *absolute number* of highly disruptive papers/patents (those with
CD_5 > 0.25) remains roughly constant over time. This is the
"conservation of highly disruptive work" finding.

The substantive interpretation: declining aggregate disruptiveness
does not preclude individual highly disruptive works. The
"composition of the most disruptive papers" by field shifts over
time (different fields produce the disruptive outliers in different
eras), but the count of highly disruptive works is stable.

This finding is what allows PLF to reconcile their decline narrative
with continued obvious breakthroughs (mRNA vaccines, gravitational
waves, etc.). The defense: aggregate decline is real; outlier
breakthroughs persist.

### 4. The corroborating language analysis (Fig. 3, SI section 1)

PLF supplement the CD-index finding with text-based evidence:

- **Type-token ratio** (unique words / total words) declines over
  time in paper and patent titles. For paper titles 1945–2010, the
  ratio drops 76.5% (life sciences) to 88% (technology). For patent
  titles 1980–2010, drops 32.5% (chemical) to 81% (computers and
  communications).
- **New word pairs** (pairs of words appearing in a title that have
  never been used together in prior titles in the field) decline
  similarly.
- **Verb shift:** earlier-decade papers use verbs evoking creation
  ("produce," "form," "prepare," "make"), discovery ("determine,"
  "report"), and perception ("measure"). Later-decade papers use
  verbs evoking improvement ("improve," "enhance," "increase"),
  application ("use," "include"), or assessment ("associate,"
  "mediate," "relate"). The verb-frequency shift is dramatic and
  visually striking in Figure 3.

These are framed as independent corroborating evidence — text-based
patterns aligning with citation-based patterns. The peer review
record shows Reviewer #2 was less persuaded by the verb classification
methodology specifically (see SQ9 / C5).

### 5. The "narrowing" mechanism (Fig. 6)

PLF argue that the decline in disruption is mechanistically driven
by scientists/inventors *narrowing their use of prior knowledge*.
Three indicators show this narrowing:

- **Decline in diversity of work cited** (Fig. 6a, 6d): normalized
  entropy of the distribution of citations to prior work decreases
  over time. Drops from ~0.99 to ~0.97 in major paper fields; less
  dramatic for patents.
- **Increase in self-citations per paper/patent** (Fig. 6b, 6e):
  scientists/inventors cite their own prior work more frequently
  over time.
- **Increase in age of cited work** (Fig. 6c, 6f): mean age of cited
  references rises from ~5 years in 1945 to ~10 years in 2010 for
  papers; similar pattern for patents.

The Extended Data Table 1 / SI Table 1 regression: regress CD_5 on
these three indicators (diversity, self-citation ratio, mean age,
and dispersion in age). All three are significantly associated with
disruption in the predicted directions. Larger field-level diversity
of cited work → more disruption; higher self-citation → less
disruption; older mean age of cited work → less disruption.

### 6. The robustness battery

PLF's defensive posture is structured around five types of robustness:

(a) **Alternative bibliometric measures.** DI^nok (Bornmann-Tekles
   variant, less sensitive to N_k inflation) and DI* (Leydesdorff
   variant) both show similar declines (Extended Data Fig. 7). This
   is the most direct response to the citation-inflation concern.

(b) **Alternative samples.** CD_5 declines computed across WoS,
   Patents View, JSTOR, APS, MAG, and PubMed all show declines
   (Extended Data Fig. 6).

(c) **Normalization.** Paper-normalized (subtract focal paper's
   backward citations N_b from N_k) and field × year normalized
   (subtract field-year mean N_b) versions of CD_5 both decline.

(d) **Regression adjustment.** Predicted CD_5 from year fixed effects
   + field × year controls (number of new papers, mean papers cited,
   etc.) + paper/patent-level controls (papers cited, unlinked
   references) — predicted decline persists after adjustment.

(e) **Simulation.** Z-score of observed CD_5 vs. CD_5 from rewired
   citation networks (preserving degree distribution and age
   structure). Z-scores are negative and growing in magnitude over
   time → observed decline is *more* than what would be expected
   from random network growth.

The peer review reveals all five robustness checks were added or
revised in response to reviewer concerns; they were not in the
initial submission. This is informative about which threats the
reviewers identified as load-bearing.

### 7. Shapley-Owen decomposition (Extended Data Fig. 5)

PLF report a Shapley-Owen decomposition of the variance in CD_5
attributable to field, year, and author/inventor fixed effects.

For papers: author effects = 0.20; field effects = 0.02; year
effects = 0.01. Author dominates; field is essentially zero.

For patents: author = 0.17; field = 0.01; year = 0.16. Author and
year both substantial; field minimal.

PLF interpret this as evidence that **stable author characteristics
contribute significantly to disruptiveness, while field-specific
factors play very small roles** in explaining the decline.

This is a substantive claim that gets less attention than the
headline decline but is methodologically significant — it bears on
whether the decline reflects field-level structural change or
author-level behavioral change. We engage this in C7.

### 8. Six data sources

PLF use six bibliometric datasets:
- **Web of Science** (primary, papers 1945–2010, n=24.7M)
- **Patents View** (primary, USPTO patents 1976–2010, n=3.9M)
- **JSTOR** (papers 1930–2010, n=1.7M)
- **American Physical Society corpus** (papers 1930–2010, n=478K)
- **Microsoft Academic Graph** (random sample of 1M papers, 1930–2010)
- **PubMed** (papers 1930–2010, n=16.8M)

All six show declining CD_5 over time. Reviewer #3 questioned whether
the JSTOR/APS analyses were genuinely run on those databases or just
on WoS records that happened to overlap with JSTOR/APS coverage; the
authors did not directly resolve this.

### 9. Restriction to high-quality work

PLF show that restricting to *Nature*, *PNAS*, *Science*, or to
Nobel-winning papers, the CD_5 decline persists (Fig. 5). This is
the response to "maybe quality is declining" — even at the most
selective venues, disruption is declining. The peer review shows
Reviewer #2 was less than fully persuaded by this — high-prestige
venues' selection criteria themselves shift over time, so this
restriction doesn't cleanly rule out quality-related explanations.

---

## Results — Three Levels

### Level 1: For a smart high-schooler

Imagine looking at every academic paper published in the last 75
years and asking, for each one, whether the papers that came after
it built on it directly (consolidating) or moved past it in new
directions (disrupting). You can do this with citation patterns:
when a new paper cites an old paper, does it also cite the old
paper's own references? If yes, it's building on the same
intellectual foundation. If no, it's pivoting to new territory.

PLF compute this "disruption score" for ~25 million papers and ~4
million patents. They find that across every field — biology,
physics, chemistry, social sciences, engineering — papers and
patents have become much less disruptive over time. A typical paper
in 1945 had a disruption score around 0.5. By 2010, the typical
paper's score was near zero.

The decline is striking visually (the famous Figure 2 shows curves
plummeting toward the x-axis across every field). The authors argue
this represents a real shift in how science is done — scientists
are increasingly building on existing canonical work rather than
breaking from it.

Two important caveats: (1) the absolute number of *highly* disruptive
papers stays roughly constant, even as the average declines —
breakthroughs still happen, they're just rarer relative to the total
output. (2) The methodology has been heavily contested since
publication; later papers (Petersen 2024, Holst 2024) argue the
decline is partly an artifact of how the metric is computed rather
than a real change in science.

### Level 2: For a junior/senior undergraduate

The paper is the most prominent application of the **Funk-Owen-Smith
CD index** family. CD_5(p) for a focal paper p classifies papers
that cite p into two types: (1) those that cite p but not its
references, and (2) those that cite both p and its references. The
metric is bounded in [−1, 1], with +1 meaning maximally disruptive
(every citer ignores predecessors) and −1 meaning maximally
consolidating (every citer cites both).

PLF apply this to 25M Web of Science papers (1945–2010) and 3.9M
USPTO patents (1976–2010). Headline finding: average CD_5 declines
between 79% and 100% across all major fields, robust across six data
sources (WoS, Patents View, JSTOR, APS, MAG, PubMed).

Three secondary findings deepen the story:

(1) Language change: type-token ratio (unique words / total words)
in titles declines over time, and the most common verbs shift from
"creation/discovery" verbs (produce, form, determine) to
"application/improvement" verbs (improve, enhance, use).

(2) Mechanism: narrowing of prior-knowledge use. Diversity of cited
work declines, self-citation rates rise, mean age of cited work
rises. Regressions show all three are independently associated with
declining disruption.

(3) Conservation: the absolute number of highly disruptive works
(CD_5 > 0.25) stays roughly constant. So the decline is in the
*central tendency*, not in the existence of major breakthroughs.

The paper has substantial robustness machinery: alternative
disruption-measure variants (Bornmann's DI^nok, Leydesdorff's DI*),
alternative samples, paper-normalization, field × year normalization,
regression adjustment for changing publication/citation practices,
and Monte Carlo simulation against rewired networks. All show similar
declines.

The methodology has been critiqued in the post-publication literature.
Petersen-Arroyave-Pammolli 2024 argues the CD index is biased by
citation inflation (more papers being cited per paper over time
mechanically lowers CD_5); Holst et al. 2024 argues older-era WoS
records have systematically missing references that mechanically
inflate CD_5 for older papers. Both critiques predict a decline-by-
artifact even if no real decline existed. The peer review record
shows Reviewer #2 raised the inflation concern explicitly during
review; PLF added the DI^nok / paper-normalized / field × year
normalized variants in response, but these do not fully address the
underlying issue.

### Level 3: For an early graduate student

The paper is methodologically careful in some respects and
problematic in others. The careful parts:

- The robustness battery is genuinely thorough. Five distinct
  defensive moves (alternative measures, samples, normalization,
  regression adjustment, simulation). Most papers in this literature
  do one or two.
- The reporting of dispersion (Extended Data Fig. 1) shows the
  full distribution of CD_5 over time, not just means. This is
  better than most disruption-decline papers.
- The Shapley-Owen decomposition (Extended Data Fig. 5) is an
  unusual analytical move that bears directly on whether the decline
  is field-driven (it's not) vs. author-driven (mostly).
- The peer review process visibly improved the paper. Reviewer #2's
  citation-inflation concern triggered the addition of DI^nok and
  the normalized variants; Reviewer #1's time-comparability concern
  triggered the longer-window robustness.

The problematic parts:

- **The CD index is structurally biased by citation inflation.**
  Petersen-Holst 2024 formalize this: the N_k count (citations to
  predecessors but not to focal paper) mechanically grows as
  citation networks densify, and CD_5 ≈ (f − b·f) / n_t — anything
  that increases n_t without proportionally increasing the
  disruption-vs-consolidation balance pushes CD_5 toward zero.
  Modern papers cite more references than older papers (mean
  references per WoS paper rose from ~10 in 1945 to ~30+ in 2010);
  the same paper that would have been "disruptive" by CD_5 in 1945
  would be "less disruptive" purely from citation-count growth.
  PLF's DI^nok and normalized variants attenuate this but don't
  eliminate it; the underlying functional form is still N_k-driven.
- **The dataset artifact problem.** Older WoS records have
  systematically missing references (Holst 2024 documents this:
  pre-1980 WoS often only indexed first few references; many older
  papers' true reference lists are truncated in the database). A
  truncated reference list mechanically increases CD_5 (predecessors
  go missing → fewer Type-2 citers → CD_5 ↑). The decline-by-artifact
  prediction this generates is the same direction as PLF's empirical
  pattern.
- **The "conservation" finding (Fig. 4) is methodologically
  questionable** in light of citation inflation. If CD_5 is biased
  downward over time, then the threshold "CD_5 > 0.25" identifies
  systematically different populations in 1950 vs. 2010 — a fixed
  threshold on a metric whose distribution is shifting downward
  selects for ever-rarer outliers. The "stable absolute count" might
  reflect threshold mismatch rather than stable existence of
  disruptive works.
- **The verb-classification methodology** has methodological gaps
  the peer review surfaced. The word selection process used a wiki-
  survey on the All Our Ideas platform with three respondents whose
  identities and qualifications are not described in the paper.
  Reviewer #2 explicitly noted: "the words themselves did not appear
  semantically distinct or self-describing disruptive innovation
  vs. consolidation." Authors removed verb classification framing
  in revision but kept the verb-frequency observations.
- **The cross-database robustness (Extended Data Fig. 6) is less
  clean than presented.** Reviewer #3 questioned whether the
  JSTOR/APS analyses were truly run on those datasets or on WoS
  records that overlap with them; PLF's text claims separate
  database analysis but the methodology section's description leaves
  this ambiguous. Cross-database robustness is the paper's main
  defense against database-specific artifacts; if the actual analyses
  share substantial WoS infrastructure, the cross-database claim
  is weaker than presented.

The most diagnostic test for whether the PLF finding survives: would
the decline persist under a CD-index variant that is rigorously
inflation-corrected (per Petersen 2024) and dataset-artifact-corrected
(per Holst 2024)? PLF's DI^nok addresses the first concern partially;
neither addresses the second. The post-publication critique literature
predicts that under both corrections, the decline magnitude reduces
substantially, with some plausible scenarios where it disappears
entirely.

---

## Connection to Our Project

### What ws2 takes from PLF (very limited)

1. **Cross-database robustness pattern.** PLF report similar findings
   across six databases. ws2's analog: report findings on the WoS-
   OpenAlex overlap subset (back-pocket Stage 3 robustness from
   Chu-Evans C3 commitment) if reviewers push on substrate-specificity.
   Methodological pattern, not substantive inheritance.

2. **Distribution-not-mean reporting (Extended Data Fig. 1).** PLF's
   reporting of CD_5 distributions over time, not just means, is
   better than typical scientometrics practice. ws2 follows the
   same pattern (per desiderata + program-level emphasis on
   "characterize distributions, not just means").

3. **Dispersion-of-cited-work-age** as a mechanism indicator. PLF
   include this in Extended Data Table 1; it's a useful auxiliary
   variable for our subfield mechanism test as a control variable
   (we don't currently include it, but should consider). Possible
   Phase 0.2 batch addition for refinement.

### What ws2 explicitly does NOT take from PLF

1. **CD index as a primary canonical-concentration metric.** This
   is the central exclusion. Per desiderata and Phase 0.1 plan
   "Canonical (primary)", we use Chu-Evans Spearman top-N with
   citation Gini as secondary. CD-index is excluded due to the
   Petersen-Holst critique chain. PLF's Fig. 4 (declining disruption)
   is therefore *not* a finding we replicate or extend.

2. **The decline-of-disruption headline narrative.** ws2 does not
   take a position on whether disruption is declining in any
   substantive sense; we treat that as a contested empirical question
   beyond our scope. Our central question (decoupling of demographic
   from intellectual plurality) is structurally different and does
   not depend on the disruption-decline claim being true or false.

3. **The "conservation of highly disruptive work" framing.** Fig. 4
   is methodologically problematic in light of citation-inflation
   bias (a fixed threshold on a downward-biased metric selects for
   ever-rarer outliers). We don't engage this finding in ws2.

4. **The verb-classification analysis (Fig. 3c, 3f).** Methodologically
   shaky per peer review; we don't adopt verb-shift framing.

### How ws2 engages PLF in Discussion

The right framing for ws2's eventual paper Discussion section:

> "Park-Leahey-Funk 2023 (PLF) is the most prominent recent application
> of CD-index methodology to documenting declining disruption in
> science. Subsequent methodological critiques (Petersen-Arroyave-
> Pammolli 2024 on citation inflation; Holst et al. 2024 on dataset
> artifacts) have argued that the documented decline is at least
> partially attributable to measurement bias in the CD-index. ws2
> engages PLF as a contested empirical claim adjacent to our central
> question. Our canonical-concentration metric (Chu-Evans Spearman
> top-N) does not inherit the citation-inflation concerns that affect
> CD-index. Our finding [insert ws2 result] is therefore methodologically
> independent of the PLF debate; if PLF's substantive claim is
> ultimately validated, our [semantic-stagnation / divergence] finding
> would be consistent with one mechanism for it; if PLF's claim is
> attributed primarily to measurement artifact, our finding stands on
> its own."

This positions ws2 as orthogonal to PLF rather than dependent on it.

### Specific design implications for ws2

- **Reaffirms CD-index exclusion.** Already in desiderata; PLF read
  reinforces the wisdom of that exclusion.
- **Reaffirms multi-metric canonical concentration design.** PLF's
  problem is that they hang too much on one metric (CD-index) whose
  validity is contested. ws2's multi-metric pattern (Spearman top-N
  + citation Gini) is structurally more defensible.
- **Reaffirms distribution-not-mean reporting.** PLF do this for CD;
  we do this for all our metrics per desiderata.
- **Possibly add age-dispersion as auxiliary variable.** PLF's
  "dispersion in age of cited work" is a useful field-year-level
  feature; consider adding to subfield mechanism test as a control.
  Phase 0.2 batch candidate.
- **Methods-section paragraph on the CD-index decision.** ws2's
  exclusion of CD-index is a deliberate choice the reader will want
  justified. A short Methods paragraph (~3-4 sentences) citing
  PLF, Petersen 2024, Holst 2024, and noting our exclusion-decision.
  Phase 0.2 batch.

---

## Key Quotes

For Methods / Related Work / Discussion in the ws2 paper:

> "We find that papers and patents are increasingly less likely to
> break with the past in ways that push science and technology in
> new directions. This pattern holds universally across fields and
> is robust across multiple different citation- and text-based
> metrics." (Abstract.)

> "Despite large increases in scientific productivity, the number of
> papers and patents with CD₅ values in the far right tail of the
> distribution remains nearly constant over time." (p. 140 — the
> conservation claim.)

> "We attribute this trend in part to scientists' and inventors'
> reliance on a narrower set of existing knowledge. Even though
> philosophers of science may be correct that the growth of knowledge
> is an endogenous process — wherein accumulated understanding
> promotes future discovery and invention — engagement with a broad
> range of extant knowledge is necessary for that process to play
> out, a requirement that appears more difficult with time." (p. 143
> — the narrowing-mechanism claim.)

> "Our study is not without limitations. Notably, even though research
> to date supports the validity of the CD index, it is a relatively
> new indicator of innovative activity and will benefit from future
> work on its behaviour and properties, especially across data sources
> and contexts." (p. 143 — the methodological-uncertainty
> acknowledgment.)

> *Reviewer #2 (peer review):* "The Consolidating/Disrupting (CD)
> measure, which forms the core of the author's empirical argument,
> is based on a quantity that necessarily decreases with the amount
> of science available to be cited. ... Its comparison across time
> is suspect because the amount of science at risk of being cited,
> and relevant to current science, is increasing over time, which
> can only trivially be interpreted as a reduction in innovation."
> (Peer review file, page ~3.) **This is the citation-inflation
> concern, raised during review and incompletely addressed in
> revision; later formalized by Petersen-Arroyave-Pammolli 2024.**

> *Reviewer #1 (peer review):* "I am not sure whether CD index values
> can be compared across decades. The publication and citation
> cultures (and database coverages) are so different that these
> comparisons might be impossible." (Peer review file, page 1.)
> **The cross-decade-comparability concern, raised during review.**

---

## Study Questions

**Warm-up (Level 1):**

1. **SQ1** — What does the CD index measure operationally? Walk
   through how a citation that cites both a focal paper *and* its
   predecessors gets classified, vs. one that cites only the focal
   paper.

2. **SQ2** — The paper claims a 91.9–100% decline in average CD_5
   for papers between 1945 and 2010. What does "100% decline" mean
   for a metric that ranges from −1 to +1, and how should we interpret
   it?

3. **SQ3** — Why does PLF report results across six databases (WoS,
   Patents View, JSTOR, APS, MAG, PubMed) rather than just one?
   What's the defensive logic?

**Intermediate (Level 2):**

4. **SQ4** — The "conservation of highly disruptive work" finding
   (Fig. 4) shows the absolute count of papers with CD_5 > 0.25 is
   roughly constant over time. How does PLF reconcile this with their
   claim that disruption is declining? Is the reconciliation
   convincing?

5. **SQ5** — The narrowing-mechanism story (Fig. 6) identifies three
   indicators (diversity of cited work, self-citation rate, mean age
   of cited work) and shows they all correlate with CD_5 in the
   predicted directions. What's the difference between "these three
   covary with disruption" and "these three cause the disruption
   decline"?

6. **SQ6** — The Shapley-Owen decomposition (Extended Data Fig. 5)
   shows that author fixed effects explain 0.20 of variance in CD_5
   for papers, while field effects explain 0.02 and year effects
   0.01. How does this bear on whether the disruption decline is
   field-driven, time-driven, or author-driven?

**Advanced (Level 3):**

7. **SQ7** — Petersen-Arroyave-Pammolli 2024 argue CD-index is biased
   by citation inflation (the N_k count grows mechanically as
   citation networks densify). PLF respond with normalized variants
   (paper-normalized, field × year normalized) and DI^nok. Do these
   variants fully address the inflation concern? Walk through what
   each correction does mathematically and what residual bias
   remains.

8. **SQ8** — Holst et al. 2024 argue older WoS records have
   systematically missing references that inflate CD_5 for older
   papers (mechanical disruption-by-truncation). PLF do not address
   this in their robustness battery. What would a dataset-artifact-
   corrected analysis require, and how would the decline magnitude
   plausibly change?

9. **SQ9** — Reviewer #2 was unpersuaded by the verb-classification
   methodology (the word selection used a 3-respondent wiki-survey
   on All Our Ideas; the words "did not appear semantically distinct
   or self-describing disruptive vs. consolidation"). PLF removed
   the explicit "disruptive vs. consolidation" verb framing in
   revision but kept the verb-frequency observations. How load-bearing
   are the verb-shift findings (Fig. 3c, 3f) for the paper's
   substantive thesis?

10. **SQ10** — The paper's "alternative samples" robustness (Extended
    Data Fig. 6) shows declining CD_5 across JSTOR, APS, MAG, PubMed
    in addition to WoS and Patents View. Reviewer #3 questioned
    whether these analyses were genuinely run on those datasets or
    on WoS records overlapping them. How would you adjudicate this,
    and does it matter for the paper's substantive claim?

---

## Challenge Corner

**C1:** The CD index is structurally biased by citation inflation
(Petersen 2024). PLF respond with normalized variants. Walk through
the math: CD_5 = (Σ −2f·b + Σ f) / n_t where n_t includes N_k (cites
of predecessors-but-not-focal). What does paper-normalization
(subtracting N_b from N_k) do to this expression? What does field ×
year normalization (subtracting field-year mean N_b) do? Where does
residual inflation bias enter? Specifically: is the inflation bias
in the *numerator* (which the normalization addresses) or in the
*denominator* n_t (which the normalization doesn't address)?

**C2:** Holst et al. 2024 documents that older WoS records have
systematically missing references — pre-1980 entries often only
indexed the first few references. A truncated reference list
mechanically increases the focal paper's CD_5 (predecessors go
missing → fewer Type-2 citers → CD_5 ↑). This is a *separate* issue
from citation inflation: it's about pre-1980 metadata completeness,
not modern-era citation density. Two sub-questions:

(a) The bias direction: missing references in older papers should
inflate older papers' CD_5, making earlier-era CD_5 *higher* than
true. This is the same direction as PLF's empirical decline. How
much of PLF's decline could plausibly be attributable to dataset
artifact alone?

(b) ws2 uses OpenAlex, not WoS. OpenAlex has different reference
coverage characteristics (broader coverage, different temporal
coverage profile). Does ws2 face an analogous dataset-artifact threat
for our canonical-concentration time series? If so, how should we
characterize and mitigate it?

**C3:** The "conservation of highly disruptive work" (Fig. 4) is
defined as "papers with CD_5 > 0.25". A fixed threshold on a metric
whose distribution is shifting (downward over time, due to citation
inflation) selects for systematically different populations across
years. Two sub-questions:

(a) If we accept the citation-inflation critique, is the "stable
absolute count" finding methodologically meaningful, or is it a
threshold-mismatch artifact? What would a percentile-based threshold
(e.g., top 1% of disruption per year) show instead?

(b) ws2 doesn't compute CD-index, so we don't directly inherit this
issue. But we *do* compute Spearman top-50 (a fixed-N threshold) on
canonical-concentration. Is our top-50 threshold subject to an
analogous "shifting-distribution-vs-fixed-threshold" concern? Why
or why not?

**C4:** The verb-classification methodology (Fig. 3c, 3f) used a
three-respondent wiki-survey on All Our Ideas to classify verbs as
"disruptive" vs. "consolidating." Reviewer #2 was explicit:
"the words themselves did not appear semantically distinct or
self-describing disruptive vs. consolidation." Authors removed the
explicit framing in revision but kept the verb-frequency observations.
How seriously should we take the verb-shift evidence as independent
corroboration of the CD-index decline? Two readings:

(a) Strong reading: the verb shift is real and reflects substantive
language change in science, even if the "disruptive vs. consolidating"
labels are post-hoc rationalization. The evidence stands.

(b) Weak reading: without principled classification, the verb shift
shows that language changes over time (which is unsurprising), not
that science is becoming less disruptive. The evidence is decorative.

Which reading do we hold? Does this affect how we cite PLF in
Discussion?

**C5:** Disruption-decline as upstream mechanism for ws2's semantic-
stagnation findings. If we observe (Tests I-III) that aggregate
semantic plurality stagnates while demographic plurality rises, one
possible interpretation is "this aligns with PLF's disruption-decline
finding — papers are becoming more conventional, hence semantic
diversity stagnates." But citing PLF as upstream support would import
the methodological dependency we explicitly rejected. Three options:

(a) Don't cite PLF as upstream support for any ws2 finding. Position
ws2 as orthogonal to the disruption-decline debate.

(b) Cite PLF's substantive finding with explicit acknowledgment of
the Petersen-Holst critique chain; note that ws2's evidence is
methodologically independent.

(c) Engage PLF more aggressively — note that ws2's semantic-plurality
metric is *not* CD-index-based and therefore *cleaner evidence* for
or against semantic-stagnation than PLF's CD-index-based evidence.
Position ws2 as resolving (one direction or the other) the contested
PLF claim.

Which position do we want to take? (b) is the most defensible; (c)
is the most ambitious; (a) is the safest.

**C6:** The Shapley-Owen decomposition (Extended Data Fig. 5) shows
that author fixed effects dominate in explaining CD_5 variance
(0.20 for papers, 0.17 for patents). This bears on the substantive
mechanism: is the disruption decline driven by *who is doing the
science* (author-level differences in disruption-tendency) or by
*the structural conditions of the science* (field-level / year-level
factors)? PLF's data says "mostly author." Two implications:

(a) For PLF specifically: their narrowing-mechanism story (Fig. 6)
is about scientist behavior (use of prior knowledge). The author-FE
dominance is consistent with this — individual scientists drive most
of the variance in disruption.

(b) For ws2: this connects to our Chu-Evans SQ8 finding that period
effects dominate cohort effects. PLF's finding is about *between-
author variance*, not period-vs-cohort. They're complementary, not
contradictory: between-author variance could be large *and* period
effects could dominate within-author over time. But if author-level
disruption-tendency is largely fixed (PLF) and current-period field
size drives behavior (Chu-Evans), what does that imply about whether
field-wide canonical concentration is the right ws2 mechanism focus?

**C7:** Cross-database robustness (Extended Data Fig. 6) is the
paper's main defense against database-specific artifacts. Reviewer
#3 questioned whether the JSTOR/APS/MAG/PubMed analyses were truly
run on those databases or on WoS records overlapping them. The paper's
methodology section is ambiguous on this (Reviewer #3: "JSTOR and
APS do not index references and citations. Was the analysis performed
on records indexed in WoS that are also indexed in JSTOR and APS,
and PUBMED?"). The authors' rebuttal does not directly resolve this.
If the cross-database analyses share substantial WoS infrastructure,
the cross-database robustness claim is much weaker than presented.
How should we treat this in our Discussion engagement with PLF?

**C8:** PLF's "narrowing of cited-work diversity" indicator (Fig. 6a,
6d) is the strongest direct evidence for their causal story. It's
essentially a measurement of canonical concentration via field-year
normalized entropy of citation distribution. Two observations:

(a) This is conceptually the same kind of measurement ws2 makes
under "canonical concentration," just operationalized via entropy
rather than Spearman top-N. The fact that PLF observe declining
diversity of cited work *is* evidence for canonical concentration
in a sense compatible with ws2's framing — and this measurement is
*not* CD-index-based, so it's not subject to the Petersen-Holst
critique.

(b) Implication: ws2 could cite Fig. 6a / 6d as upstream evidence for
canonical concentration trends, even while disclaiming engagement
with the Fig. 2 CD-index decline. This is a more nuanced citation
strategy than the all-or-nothing "engage or disengage with PLF"
options in C5.

How should we position the citations? Specifically: cite Fig. 6a
diversity-of-cited-work as evidence consistent with canonical
concentration trends; disclaim engagement with Fig. 2 CD_5 decline
due to CD-index methodology issues. Does this work?

**C9:** PLF report a steeper decline for social sciences (100% from
1945 to 2010 for papers) than physical sciences (91.9%). They don't
unpack this differential heterogeneity; they treat it as part of the
"universal across fields" framing. But a 100% vs. 92% decline is
substantively different — social sciences essentially go to zero
average disruption, physical sciences still have some. Is this
field-level heterogeneity informative for ws2's positioning? Two
sub-questions:

(a) Differential decline rates by field could reflect different
mechanisms (different rates of canonical concentration; different
citation cultures; different field-size growth rates; different
database-coverage characteristics). PLF treat the universality as
strength; we could treat the heterogeneity as informative.

(b) For ws2's CS + Physics primary fields: PLF's CS analog is
"computers and communications" (patents) which shows the *least*
decline (78.7% — patents) or "technology" research area (papers) —
the relationship between disciplines is complicated by their data
sources (papers vs. patents). What's the takeaway for our cross-
field replication design?

**C10:** Restricting to high-prestige venues (Fig. 5: *Nature*, *PNAS*,
*Science*, Nobel papers) shows the decline persists. PLF treat this
as evidence that the decline isn't a quality artifact. But high-
prestige venue selection criteria themselves shift over time —
what counts as Nature-worthy in 2010 is different from 1945. The
restriction doesn't cleanly rule out quality-related explanations.
What would a more rigorous quality-control test look like? Why might
PLF's analysis be insufficient?

**C11:** Theoretical positioning vis-a-vis Chu-Evans 2021. Chu-Evans
documents declining entrepreneurial futility and increasing canonical
concentration with field size. PLF documents declining disruption
over time. The two findings are mechanistically adjacent but
methodologically different: Chu-Evans's IV is field size; PLF's IV
is calendar year. How do the two findings relate? Are they
complementary (same underlying phenomenon, different operationalizations)
or potentially conflicting (different explanatory variables, different
measurement substrates)? For ws2, which is the right upstream
reference?

---

## Synthesis Pointers (for `synthesis.md`)

1. **PLF is the contested headline ws2 positions against.** Methodology
   inheritance: zero (CD-index excluded per desiderata). Substantive
   engagement: Discussion-section paragraph noting Petersen-Holst
   critique chain and ws2's methodological independence.

2. **Citation-inflation critique applies to PLF and motivates ws2's
   CD-index exclusion.** Petersen-Arroyave-Pammolli 2024 (paper 03)
   formalizes the concern. PLF's normalization variants (DI^nok,
   paper-normalized, field × year normalized) attenuate but do not
   eliminate.

3. **Dataset-artifact critique applies to PLF.** Holst et al. 2024
   (paper 05) documents pre-1980 WoS reference truncation that
   mechanically inflates older-era CD_5. PLF do not address this.

4. **PLF's Fig. 6 (narrowing of cited-work diversity, self-citation,
   age) is more usable for ws2 than Fig. 2.** The Fig. 6 indicators
   are not CD-index-dependent and align conceptually with our
   canonical-concentration measurement. Citation strategy: engage
   Fig. 6 as upstream evidence; disclaim engagement with Fig. 2.

5. **Verb-classification methodology (Fig. 3c, 3f) is methodologically
   shaky** per peer review. ws2 should not cite verb-shift evidence;
   if we engage PLF's text-based findings, focus on type-token ratio
   (Fig. 3a, 3d) which has more defensible methodology.

6. **PLF's Shapley-Owen decomposition (author dominates field) is
   complementary to Chu-Evans's period-dominates-cohort.** Two
   different decompositions of variance; both are about within-vs-
   between sources. Synthesis: structural mechanisms operate on
   *all* authors at *current period* — neither generational
   replacement (Chu-Evans cohort effect ≈ 0) nor field-level
   factors (PLF field effect ≈ 0) explain the disruption decline
   or canonical-concentration rise. Author-level + period-level
   factors dominate. This shapes our Discussion framing for ws2.

7. **Peer review is load-bearing for understanding PLF's vulnerabilities.**
   Reviewer #2 raised exactly the citation-inflation concern that
   Petersen-Holst later formalize. The published paper carries
   acknowledged-but-incompletely-addressed vulnerabilities. ws2's
   exclusion of CD-index is reinforced by reading the peer review
   alongside the paper.

8. **PLF's robustness battery is methodologically careful but
   insufficient.** The five robustness types (alternative measures,
   samples, normalization, regression, simulation) collectively
   represent serious effort but do not address the structural
   citation-inflation and dataset-artifact issues. Lesson for ws2:
   robustness machinery is necessary but not sufficient — the
   underlying metric needs to be validated against the threats, not
   just shown to be stable across variants.

9. **Age-dispersion of cited work as auxiliary control variable**
   (PLF Extended Data Table 1 inheritance, 2026-04-26). PLF include
   "dispersion in age of cited work" as a regression control;
   conceptually it captures *temporal* concentration (does the field
   engage with its history or only with recent work?) — distinct
   from *paper-identity* concentration captured by CanonConc.
   Without this control, ws2's subfield mechanism test γ_1 is a
   blended effect of paper-identity concentration + temporal
   narrowing; with it, the two mechanisms are separable. Added as
   subfield-level control in the regression spec (see
   `docs/phases/phase-0.1-plan.md` subfield mechanism test
   subsection). Computationally trivial — uses existing OpenAlex
   reference data. This is the *one* methodology element ws2 directly
   inherits from PLF; we do not inherit CD-index or any of PLF's
   primary metrics.

---

## Discussion Notes

(Filled during collaborative review session. Blank until that session
happens.)

### On C1 — citation-inflation math + normalization variants

Closed via pointer to SQ7 walkthrough, 2026-04-26.

C1 is a more Socratic version of SQ7's math walkthrough. The
substantive content — clean notation setup of CD_5, the accidental-
Type-2 mechanism, walkthrough of all three normalization variants,
the critical insight that PLF's variants modify only the denominator
while inflation bias enters the numerator, why DI^nok amplifies
rather than mitigates, and the ws2 implication (Spearman top-N rank-
invariance) — is captured in the SQ7 walkthrough above. No new ws2
framing content here.

**Drafting note (minor):** C1's parentheticals as drafted have the
orientation reversed. The question reads "is the inflation bias in
the numerator (which the normalization addresses) or in the
denominator n_t (which the normalization doesn't address)?" — but
the actual relationship is the opposite. PLF's normalizations
*modify the denominator* (subtract from n_3) and *leave the
numerator unchanged*. The substantive answer in SQ7 is "bias is in
the numerator; normalizations address the denominator only" —
opposite of what C1's parentheticals suggest. Minor drafting issue;
not substantively important since the SQ7 walkthrough works through
the actual relationship.

### On C2 — dataset-artifact bias and ws2's analog

Working session with user, 2026-04-26.

**(a) Sub-question deferred to Holst 2024.** "How much of PLF's
decline could plausibly be attributable to dataset artifact alone?"
This is the substantive content of Holst et al. 2024 (paper 05 in
our reading list). We will engage this when we read Holst directly
rather than walking through PLF speculation. Marked deferred.

**(b) Walkthrough — does ws2 face an analogous threat?**

*The PLF/Holst threat structure recap.* WoS pre-1980 records often
indexed only first few references in a paper. Mechanism for inflated
older-era CD_5: truncated reference list → fewer indexed predecessors
→ smaller pool for citers to "accidentally" cite via Type 2 → fewer
Type-2 citers → numerator (n_1 − n_2) biased upward → CD_5 inflated
for older papers. This is a *layer-specific* dataset issue: papers
themselves are indexed in WoS, but their reference lists are
incomplete.

*The ws2 analog — same threat at a different layer.* OpenAlex has
its own version of the threat, structured differently:

- *Better than WoS* for non-English papers, open-access content,
  newer papers (2010+).
- *Variable for older papers* — especially pre-1990. Some older
  papers are missing entirely; some are indexed but with incomplete
  citation networks.
- *Reference completeness varies by source* — Crossref-sourced
  papers typically complete; MAG-sourced or PubMed-sourced papers
  may have partial reference data.

The threat layer differs from WoS-Holst:

| | WoS-Holst | OpenAlex-ws2 |
|---|---|---|
| What's incomplete | Reference lists *of* older papers | Indexing of older papers themselves + their citation networks |
| Mechanism | Truncated references → fewer Type-2 citers → CD_5 inflated | Missing citing papers → undercounted citations to older papers → distorted citation distribution |
| What it affects | CD-index numerator and denominator | Citation counts → Spearman top-N rankings + Gini |

We don't inherit the *exact* WoS-Holst issue (reference truncation
in older indexed papers) but we do inherit *a* dataset-artifact
threat at a different layer (incomplete indexing of older papers
and their citation networks).

*Bias direction analysis for our specific metrics.*

**Spearman top-50:** if undercounting is *uniform* across papers
in a year, ranks are preserved and Spearman is unaffected (rank-
invariance). If undercounting is *non-uniform* — systematically
undercounts certain journals, languages, etc. — top-50 list shifts.

Critical question: which direction does the bias go?
- *Scenario A:* undercounting decreases over time (OpenAlex is
  better at indexing recent papers). Top-50 lists in 1975 are
  noisier → Spearman correlation between adjacent years is
  *attenuated* in older eras → would *attenuate* the canonical-
  concentration-rises-over-time trend → bias *against* our
  hypothesized pattern.
- *Scenario B:* OpenAlex coverage is roughly stable per era but
  biased toward certain content types throughout the time series.
  Top-50 lists are systematically biased toward over-represented
  content types throughout. Spearman stability between adjacent
  years isn't strongly affected, but the *identity* of the canon
  is distorted.

In neither scenario does the bias clearly amplify our hypothesized
trend (in contrast to WoS-Holst, where bias direction aligns with
PLF's finding).

**Citation Gini:** if older-era citations are systematically
undercounted, the distribution looks more compressed → lower Gini
in older eras → bias direction *aligned* with our hypothesized
canonical-concentration-rises trend. Citation Gini is more
vulnerable to OpenAlex coverage bias than Spearman top-50 is. Worth
noting.

*What existing plan already mitigates.*

1. **Post-1990 primary, pre-1985 preliminary** (desiderata §10,
   plan §13). Era where OpenAlex coverage is most concerning is
   pre-1990; bounding primary analysis to post-1990 avoids the
   worst.
2. **Multi-metric reporting.** Spearman top-50 + citation Gini. If
   only Gini shows the trend, we'd flag it as potentially driven
   by coverage bias.
3. **Pre-1990 with disclaimer.** Acknowledge the limitation.

These collectively address the threat but don't *quantify* it.

*New commitments (Phase 0.2 batch addition).*

Three small extensions of existing commitments rather than
standalone new pending items:

- **Per-era OpenAlex coverage diagnostic.** Parallel to Hofstra C8
  per-era identity-confidence diagnostic. Per (field × decade),
  report OpenAlex coverage rate — fraction of papers with complete
  reference lists; fraction of papers indexed relative to expected
  cross-database baseline. Sample-composition transparency artifact.
- **Citation-completeness sensitivity row** in the existing pooled
  measurement-robustness appendix (from Hofstra C8 commitment).
  Recompute canonical-concentration metrics under high-completeness
  restriction. One additional row; doesn't expand the appendix
  significantly.
- **Methods-section sentence** extending the C3/SQ10 substrate-
  acknowledgment paragraph. Acknowledges the OpenAlex-coverage analog
  of the Holst threat, distinguishes the mechanism (indexing-
  completeness rather than reference-truncation), points to the
  diagnostic and robustness row.

Captured in pending Phase 0.2 batch.

**Why this is a small extension rather than a major commitment.**

The bias direction analysis above suggests the OpenAlex coverage
threat is *less* threatening to ws2 than the WoS-Holst threat is to
PLF. For Spearman top-50 specifically (our primary metric), the
bias is either attenuating (Scenario A) or non-directional
(Scenario B) — not amplifying. For Gini (secondary), the bias could
amplify our hypothesized trend, but the multi-metric pattern
(Spearman + Gini) gives us early warning if Gini-only shows the
effect. The new commitments are diagnostic-and-document rather than
correct-and-restrict.

### On C3 — fixed threshold on shifting distribution

(Pending.)

### On C4 — verb-classification methodology weight

(Pending.)

### On C5 — citing PLF as upstream support: three options

Working session with user, 2026-04-26.

**Three options considered.**

*(a) Don't cite PLF as upstream support.* Position ws2 as orthogonal
to the disruption-decline debate. Safest; lowest impact.

*(b) Cite PLF with critique-chain caveat.* Acknowledge PLF's
substantive finding; note the Petersen-Holst critique chain; note
that ws2's evidence is methodologically independent. Most defensible;
medium impact.

*(c) Engage PLF aggressively as cleaner evidence.* Position ws2's
semantic-plurality metric as methodologically cleaner than CD-index;
contribute inflation-immune evidence to the debate. Most ambitious;
highest impact; highest methodological burden.

**Decision: (c-prime) — refined version of (c).**

Raw option (c) used "resolving the contested PLF claim" framing
which overclaims. The refined (c-prime) version preserves the
ambition while calibrating the claims:

- Frame as "contributing inflation-immune evidence to the debate"
  rather than "resolving."
- Acknowledge the construct gap explicitly: semantic plurality is
  *adjacent to* but *not identical to* disruption.
- Pre-commit to symmetric framings (describe what we find without
  partisan language).

**What (c-prime) commits us to.** Four concrete pieces:

*(1) Methods-section paragraph defending the inflation-immune
claim.* ~5 sentences explaining why our semantic-plurality metrics
(cluster entropy + effective dimensionality + mean pairwise distance)
are methodologically sounder than CD-index for measuring change-in-
content-space-over-time:
- All three operate on paper embeddings, not citation network
  structure → not subject to citation-inflation bias.
- Effective dimensionality operates on embedding-space variance →
  also not subject to citation-inflation.
- Mean pairwise distance is a direct content-space measurement →
  orthogonal to citation patterns.
- All three are robust to the specific accidental-Type-2 mechanism
  walked through in SQ7 (longer reference lists → mechanically
  more Type-2 citations).

*(2) Discussion-section paragraph engaging PLF directly.* ~5
sentences. Cite PLF's substantive claim, cite Petersen-Holst critique
chain, position ws2's semantic-plurality measurement as inflation-
immune evidence on the substantively-related question.

*(3) Pre-registered interpretive grid for ws2 outcomes vs. PLF
debate.* Three cells (or one short paragraph):
- *Semantic plurality declines over time* → corroborates PLF's
  substantive direction with cleaner methodology. Strengthens PLF's
  underlying claim against Petersen-Holst's measurement-artifact
  reading.
- *Semantic plurality stable* → contradicts PLF's substantive
  direction. Strengthens the Petersen-Holst reading that PLF's
  decline is mostly artifact.
- *Semantic plurality rising* → strongly contradicts PLF. Supports
  the view that PLF's decline is mostly artifact (and possibly the
  underlying scientific dynamics are healthier than PLF claims).

*(4) Calibration paragraph (load-bearing for c-prime framing).*
~3 sentences. Important — semantic plurality is *adjacent to* but
*not identical to* "disruption" as PLF measures it. PLF measures
citation-pattern structure (whether successors cite predecessors);
we measure content-space structure (whether papers cluster or
spread). These are related but distinct constructs. We don't claim
to "resolve" PLF — we claim to contribute methodologically-cleaner
evidence on the substantively-related question.

**Risks of (c-prime) we accept.**

*(1) The "cleanness" claim itself is contestable.* Our metric isn't
trivially cleaner than CD-index. It has its own issues we've
engaged: embedding stability over time, cluster-fit sensitivity,
subfield assignment drift, OpenAlex coverage. A reviewer could
push: "you claim your metric is cleaner, but you have these issues
PLF doesn't have." Our defense is that we've explicitly addressed
these via drift-mitigation ladder, temporal-stratification commitment,
and coverage diagnostics. Defense, not automatic win.

*(2) Scope creep risk.* (c-prime) pulls narrative weight from the
decoupling story (our distinctive contribution) toward PLF positioning.
Mitigation: the calibration paragraph (commitment #4) explicitly
keeps PLF engagement bounded — "adjacent to but not identical to"
prevents the paper from becoming about PLF.

*(3) Discussion-section real estate.* (c-prime) requires ~1.5
paragraphs Methods + ~1.5 paragraphs Discussion. Manageable but
not free.

*(4) Participant rather than observer.* Position us as participants
in the disruption-decline debate. Future commenters will engage us
specifically on the cleanness claim. We accept this — high-impact
positioning is the upside.

**Why (c-prime) over (b).** (b) is safer but lower-impact. Given
that we're going to do most of the methodology work anyway (we have
to defend our metrics' soundness against citation-inflation
concerns regardless of whether we explicitly engage PLF), the
marginal cost of (c-prime) over (b) is small while the substantive
contribution to a high-profile debate is meaningful. The decoupling
story remains primary; PLF engagement is secondary but substantive.

**What we don't do under (c-prime).**

- Don't claim to "resolve" the PLF/Petersen-Holst debate.
- Don't position our metric as a *replacement* for CD-index in
  general scientometrics.
- Don't engage PLF beyond the inflation-immune-evidence claim;
  don't take a stand on the Shapley-Owen author-FE finding, the
  conservation-of-disruption finding, or the verb-classification
  evidence.

Captured in pending Phase 0.2 batch.

### On C6 — author-FE dominance interpretation

(Pending.)

### On C7 — cross-database robustness questioning

(Pending.)

### On C8 — Fig. 6 as more-usable evidence than Fig. 2

(Pending.)

### On C9 — field-level differential decline rates

(Pending.)

### On C10 — high-prestige venue robustness limits

(Pending.)

### On C11 — PLF vs. Chu-Evans theoretical relationship

(Pending.)

---

## Study Question Walkthroughs

(Answers worked through collaboratively in review sessions. Each
entry preserves the arc of initial intuition → sharpening → final
version. Questions not yet worked through are marked `(Pending)`.)

### SQ1 — CD index operationalization

(Pending.)

### SQ2 — Interpretation of "100% decline" in CD_5

Working session with user, 2026-04-26.

**The math.** "100% decline" = starting value reduced to 0, treating
starting value as the denominator. For social sciences: 0.36 (1945)
→ 0.00 (2010); (0.36 − 0.00) / 0.36 = 100%. For life sciences:
0.52 → 0.04; (0.52 − 0.04) / 0.52 = 92.3%.

Arithmetic is straightforward. The framing is the issue.

**Three problems with percentage-decline framing on a [−1, +1] metric.**

*(1) The denominator is the starting value, not the metric range.*
On a [−1, +1] metric, the *maximum possible decline* is Δ = −2
(going from +1 to −1). PLF's "100% decline" in social sciences
corresponds to Δ ≈ −0.36 — about 18% of the metric's full range.
"100% decline" is technically correct under the percentage-of-baseline
definition but rhetorically suggests "as much decline as possible,"
which it isn't.

*(2) The framing breaks down near zero.* A metric going from 0.05
to 0.005 is also a "90% decline" — but the absolute change is tiny
(Δ = −0.045). Percentage-decline framing collapses information
about magnitude relative to the metric's range. A 90% decline from
0.5 (Δ = −0.45) and a 90% decline from 0.05 (Δ = −0.045) look
identical in PLF's framing despite being 10× different in absolute
terms.

*(3) "100% decline" does NOT mean "maximally consolidating."* This
is the critical interpretive point. The 2010 social-sciences mean
of 0.00 means the average paper is *neutral* — equally split
between disruption and consolidation. Maximally consolidating
would be CD_5 = −1, where every citing paper cites both the focal
paper *and* its predecessors. PLF's data shows convergence toward
neutral, not movement toward the consolidating extreme. The "100%
decline" phrasing obscures this distinction.

**What the data actually shows in absolute terms.**

| Field | CD_5 1945 | CD_5 2010 | Δ | % of [−1,+1] range |
|---|---|---|---|---|
| Life sciences | 0.52 | 0.04 | −0.48 | 24% of range |
| Physical sciences | ~0.40 | ~0.03 | ~−0.37 | ~19% of range |
| Social sciences | 0.36 | 0.00 | −0.36 | 18% of range |
| Technology | 0.46 | 0.10 | −0.36 | 18% of range |

The shifts are 18–24% of the metric's full range. Real, but
materially different from the "100% decline" framing's connotation.
The fields are converging toward the neutral midpoint, not
approaching the consolidating extreme.

**Why this matters for ws2.**

*(1) Framing inflates the apparent magnitude of PLF's finding.* A
substantively meaningful but bounded shift toward neutrality is
presented through the percentage framing as "complete decline." If
we engage with PLF's quantitative results, we should be aware of
this and cite absolute Δ values rather than the 92.3%–100%
percentage-decline framing.

*(2) Compounds with the citation-inflation critique.* Petersen-Holst
argue that the *direction* of CD_5 movement is partly artifact. The
PLF framing magnifies the apparent magnitude of that
artifact-influenced movement. If we discount the magnitude-of-decline
by both (a) absolute-vs-percentage reframing AND (b) citation-
inflation correction, the substantive remaining finding might be
quite modest — possibly a Δ of −0.10 to −0.20 across the metric's
[−1, +1] range, or 5–10% of full range. Whether that constitutes
"decline of disruption in any meaningful substantive sense" becomes
a much closer call than PLF's framing suggests.

*(3) Lesson for ws2 reporting.* When we report headline numbers from
ws2's metrics, prefer absolute changes and percentage-of-range
framing over percentage-of-baseline framing — particularly for
bounded metrics like Spearman correlation (also bounded in [−1, +1])
and Gini (bounded in [0, 1]). This is good methodological hygiene
in any case; PLF illustrates what goes wrong without it.

No new Phase 0.2 batch commitment from this walkthrough — the
absolute-Δ-reporting practice is good methodological hygiene we
should follow regardless of PLF, and a Methods-section caveat
specifically addressing this would be over-engineered. Captured
here for our future reference if we cite PLF magnitudes in
Discussion.

### SQ3 — Cross-database robustness logic

(Pending.)

### SQ4 — Conservation finding reconciliation

(Pending.)

### SQ5 — Correlation vs. causation in narrowing mechanism

(Pending.)

### SQ6 — Shapley-Owen decomposition implications

(Pending.)

### SQ7 — Citation-inflation and normalization variants

Working session with user, 2026-04-26.

**Setting up the formula in clean notation.**

For a focal paper p, take all citations within 5 years of p's
publication. Each citer falls into one of three types:

- **Type 1 (n_1):** cites p but *not* p's predecessors. Disruptive.
- **Type 2 (n_2):** cites p *and* at least one predecessor.
  Consolidating.
- **Type 3 (n_3):** cites at least one predecessor but *not* p
  itself. Irrelevant to p directly but counted in PLF's denominator.

PLF's formula:

CD_5 = (n_1 − n_2) / (n_1 + n_2 + n_3)

The numerator (n_1 − n_2) is the "disruption signal" — disruptive
minus consolidating citations. The denominator includes n_3
(citations to p's predecessors that don't cite p itself).

**Where citation inflation enters.**

Citation networks have densified over time in two ways:

*(1) More citing papers per focal paper.* All three counts (n_1,
n_2, n_3) grow proportionally if disruption rates are constant.

*(2) Longer reference lists per citing paper.* Mean references per
WoS paper rose from ~10 in 1945 to ~30+ in 2010. This is the
substantively important inflation.

**The accidental-Type-2 mechanism (the Petersen critique core).**

Consider a citing paper i with reference list of length R_i. Suppose
i cites p (so it's Type 1 or Type 2). Whether i is Type 2 depends
on whether *any* of i's other R_i − 1 references happens to be one
of p's m predecessors.

If references were distributed uniformly at random across literature
of size T:

P(i cites at least one predecessor of p | i cites p) ≈ 1 − (1 − m/T)^(R_i − 1)

As R_i grows (longer reference lists), this probability rises. So
*conditional on citing p*, more recent citers are mechanically more
likely to also cite p's predecessors → pushing them into Type 2
rather than Type 1.

This biases the (n_1 − n_2) numerator downward over time even if
the underlying intellectual relationship between citing and cited
papers is identical. **A 1945 paper and a 2010 paper with the same
true disruption-vs-consolidation pattern would have different
observed (n_1, n_2) ratios purely from reference-list length
growth.**

This is in the *numerator*, not the denominator.

**What PLF's normalization variants do.**

*Paper-normalized:* subtract focal paper's backward citations N_b
from n_3.

CD^paper_norm = (n_1 − n_2) / (n_1 + n_2 + max(0, n_3 − N_b))

Intuition (PLF's): if p has many references, more "opportunities"
for n_3. Subtracting N_b corrects for trivial growth in n_3 due to
p having a longer reference list.

*Field × year normalized:* subtract field-year mean N_b instead.

CD^field_year_norm = (n_1 − n_2) / (n_1 + n_2 + max(0, n_3 − N_b^mean))

Intuition: in fields/eras where everyone cites more, n_3 grows for
everyone; subtracting field-year mean normalizes against this.

*Bornmann's DI^nok:* drop n_3 entirely.

DI^nok = (n_1 − n_2) / (n_1 + n_2)

Drops the irrelevant-denominator term completely.

**What's wrong with all three normalizations.**

**They all address denominator inflation. None address numerator
inflation.**

The numerator is always (n_1 − n_2) across all three variants. The
variants only modify the denominator. But the inflation bias from
the accidental-Type-2 mechanism is in the numerator — n_2 grows
mechanically as reference lists lengthen, biasing (n_1 − n_2)
downward.

DI^nok makes things worse in one specific sense: dropping n_3 from
the denominator means DI^nok = (n_1 − n_2) / (n_1 + n_2). When n_2
grows mechanically while n_1 stays constant, both the numerator
decreases AND the denominator increases. The metric falls faster,
not slower. PLF's Extended Data Fig. 7 shows DI^nok declining
steeply — they present this as robustness, but it's also consistent
with stronger numerator-bias amplification.

**Residual bias after PLF's strongest normalization.**

(n_1 − n_2) / [(n_1 + n_2) + adjusted denominator]

The numerator is biased downward at a rate proportional to how much
reference-list lengths have grown, scaled by predecessor density.
For typical fields where reference lengths roughly tripled between
1945 and 2010 (10 → 30+), the implied numerator bias is substantial.
Petersen-Arroyave-Pammolli 2024 computes specific magnitudes; their
core finding is that under inflation-corrected analyses, the apparent
disruption decline shrinks substantially or disappears for several
fields.

**Lesson on PLF's robustness battery.**

PLF claim the decline is robust because all three normalization
variants show declines. But all three address the same problem
(n_3 inflation) while leaving the more important problem (n_2
inflation) untouched. **Robustness across variants that share the
same vulnerability isn't robustness against the vulnerability
itself.** General lesson: robustness machinery needs to attack
different threats through different mechanisms, not the same threat
through different formulas.

**Why ws2 excludes CD-index — concrete reason now visible.**

The underlying functional form of CD-index makes it intrinsically
vulnerable to citation-inflation in the (n_1 − n_2) numerator. No
reformulation that keeps the (Type-1 minus Type-2) signal can avoid
this. To fix it, you'd need to redefine the disruption signal in a
way that's invariant to reference-list length — which would be a
different metric, not a CD-index variant.

ws2's primary canonical-concentration metric (Chu-Evans Spearman
rank correlation top-N) is *rank*-invariant to citation magnitudes.
Whether papers cite 10 or 30 references doesn't affect the top-N
most-cited list's identity-stability across years. We avoid the
CD-index family's specific vulnerability by choosing a fundamentally
different measurement — concentration of attention via ranks rather
than disruption via local citation-pattern signals.

ws2's secondary canonical metric (citation Gini) is also more
robust — it's about the citation distribution's concentration, not
about local disruption-vs-consolidation network structure. Reference-
list-length growth might shift the distribution somewhat but doesn't
systematically bias Gini the way it biases (n_1 − n_2).

**For ws2 Discussion engagement with PLF.**

The substantive position when we cite Petersen-Arroyave-Pammolli 2024
alongside our CD-index exclusion: not just "CD-index is contested"
but "CD-index has a specific structural vulnerability — numerator
inflation from reference-list growth — that PLF's normalization
variants do not address. Our canonical-concentration metric
(Spearman top-N) is methodologically immune to this specific
vulnerability by being rank-invariant."

This is a stronger Discussion-section position than just citing a
contested paper. It explains *why* CD-index is the wrong tool for
cross-decade comparison while *our* tool is the right one.

No new Phase 0.2 batch addition — the substantive engagement strategy
is captured in the existing "selective Chu-Evans citation framing"
batch item (which extends naturally to PLF) and the existing
"Methods-section paragraph on the CD-index decision" batch item
(under the eventual ws2 paper Methods/Discussion framing). This
walkthrough provides the technical substance for those existing
commitments rather than triggering new ones.

### SQ8 — Dataset-artifact correction implications

(Pending.)

### SQ9 — Verb-classification methodology weight

(Pending.)

### SQ10 — Cross-database analyses: WoS-shared infrastructure question

(Pending.)
