# 16 — Reference Coverage Analysis of OpenAlex Compared to Web of Science and Scopus

**Authors:** Jack H. Culbert, Anne Hobert, Najko Jahn, Nick Haupka, Marion Schmidt, Paul Donner, Philipp Mayr
**Venue:** *Scientometrics* 130:2475–2492 (2025); preprint arXiv:2401.16359 (2024)
**PDF:** `literature-review/16-culbert-2024-openalex-coverage.pdf` (gitignored)
**DOI:** 10.1007/s11192-025-05293-3

---

## Background

Culbert et al. is a head-to-head comparison of **OpenAlex vs Web of
Science (WoS) vs Scopus** on three quality dimensions: total/source
reference coverage, internal reference coverage, and per-journal
metadata coverage (abstracts, ORCID, OA status, funding info). The
study uses a **shared-corpus methodology** — 16.8M publications from
2015–2022 that are present in all three databases by exact-DOI
match — to enable bilateral coverage comparison without size
confounding.

This is the **highest post-N1-priority Tier-2 paper** for ws2 because
§0 (analytical-population definition) and §9e (selection-bias
correction layer) are OpenAlex-specific commitments. Phase 0.1's
empirical findings — ~50% abstract bottleneck (Check 1), ~55%
country-undeterminable rate (Check 1f / Check 3 H6), 3.0% cross-era-
merger rate (Check 4), ABOVE-pre-registered-band ORCID coverage
(Check 3 H7) — all need a "is this OpenAlex-specific or universal?"
reading to inform Methods-section justification of OpenAlex as
substrate. Culbert is the canonical answer to that question.

The paper also surfaces a **load-bearing data-quality finding** — that
OpenAlex's "generous disambiguation" of authors causes ORCIDs to be
assigned to >10,000 records in some cases, a fail mode concentrated
on non-Western (specifically Chinese) names. This finding directly
affects ws2's Check 4 disambiguation-error framing and Check 3 H7
methodology-bonus reading, both of which compound with Lockhart 2023
P5's bias-uncertainty band on non-Western subgroups.

For ws2, the paper splits into two functional uses:
1. **§0 / §9e justification:** a paragraph in Methods citing Culbert
   acknowledging OpenAlex's coverage trade-offs vs WoS/Scopus,
   defending the OpenAlex choice on reproducibility + Sorbonne-style
   institutional validation grounds.
2. **A surface for two specific Phase-0.1 finding re-readings:** Check
   4's lower-bound framing strengthens; Check 3 H7's "methodology
   bonus" needs a noise-floor caveat.

---

## Key Ideas

### 1. The shared-corpus methodology

The fundamental analytic move: **find publications present in all
three databases by exact DOI match, then compare metrics on that
subset.** Mechanically:

- Whole corpus sizes (mid-2023):
  - WoS: 71.3M records, 1.77B references
  - Scopus: 65.6M records, 2.03B references
  - OpenAlex: 243.1M records, 1.85B references
- Shared corpus (DOI-matched, 2015–2022): **16.8M publications**
  - WoS source references: 725M
  - Scopus source references: 727M
  - OpenAlex source references: 586M

The shared corpus is **23.6% / 25.6% / 6.9%** of WoS / Scopus /
OpenAlex's respective whole corpora. OpenAlex's much larger overall
size means most of its content is *outside* the shared corpus — books,
conference papers, gray literature, dissertations, non-DOI-having
records.

**Why this matters for ws2:** Our analytical population restricts to
papers with abstracts and CS/Physics concept tags. We don't fully
match the shared-corpus subset — much of pre-1990 OpenAlex CS/Physics
likely doesn't have DOIs (DOI registration didn't become standard
until ~2000). So Culbert's coverage figures on the shared corpus are
**upper bounds** on the OpenAlex quality we can expect for our 1970–
2024 window. The pre-1990 quality is plausibly worse than Culbert's
shared-corpus numbers suggest.

### 2. Headline reference-coverage finding

OpenAlex's **inferred internal reference coverage on the shared
corpus is 83.2–83.6%**, depending on whether we relate to WoS's or
Scopus's total reference count as the assumed denominator. This is
**comparable to** WoS (81.6%) and Scopus (87.6%) on the same
1996–2022 reference-publication-year restriction.

Caveats Culbert flags:
- OpenAlex's whole-corpus internal coverage *cannot be computed
  directly* because OpenAlex does not include non-source references
  in its data, only source references. The 83.2–83.6% is *inferred*
  from total-reference-count assumption.
- OpenAlex's pre-calculated source reference count "Average Source
  Reference Count" is 7.6 references/record on the whole corpus vs
  WoS's 16.9 and Scopus's 18.7. **OpenAlex undercounts references on
  its long-tail content** (the 93.1% of OpenAlex outside the shared
  corpus). Culbert attributes this to short-reference-list publications
  (preprints, conference abstracts, etc.) being included.
- On the **articles-only restriction** of the whole corpus, OpenAlex
  still trails: 8.1 references/record vs 22.4 (WoS) / 20.2 (Scopus).

**Why this matters for ws2:** Our ws2 metrics are primarily semantic-
diversity (embedding-based) and demographic-plurality, NOT reference-
graph-based. Our canonical-concentration metrics (Spearman top-50,
citation Gini) depend on citations *received*, not references *cited*,
so the reference-undercount affects us less directly. But Stage 3's
co-citation analyses and any reference-network robustness check
inherits this caveat — OpenAlex's reference coverage on the long tail
is materially worse than its shared-corpus performance.

### 3. The "generous disambiguation" finding [LOAD-BEARING FOR WS2]

Culbert's most operationally important finding — and the surface that
materially affects ws2 commitments:

> "the ORCID coverage is more comprehensive in OpenAlex (Fig. 4b). The
> proportion of articles in OpenAlex with at least one ORCID present
> is 92%, and the proportion of articles with at least one ORCID in
> WoS is 16% and in Scopus 32%. However, upon inspection we discovered
> that OpenAlex performs a generous disambiguation of authors,
> resulting in a high ORCID coverage. In particular, some authors with
> Chinese names were observed to be linked to more than 10,000
> publications."

And further (Discussion):

> "in some cases ORCIDs were assigned to more than 10,000 records in
> our corpus, suggesting issues with OpenAlex's author disambiguation
> method. … It is important to conduct further analysis to confirm
> whether the author names and ORCIDs are accurately matched, given
> the observed phenomenon of a single ORCID being erroneously
> attributed to tens of thousands of articles. If this is not the case
> then this may demonstrate the ongoing challenge of author name
> disambiguation in bibliographic databases."

The mechanism: OpenAlex's disambiguation algorithm aggressively merges
author records to maximize cross-reference coverage. It's optimized
for "find the same author across publications" rather than "be sure
two records are the same author." The recall/precision trade-off is
tuned toward recall, with documented over-merging on non-Western
names — specifically Chinese — where transliteration variation +
common-surname density (e.g., "Wang", "Li", "Zhang") creates
convergent name-fingerprint patterns that fool the algorithm.

**For ws2 this implies three things, in order of severity:**

1. **Check 4's 3.0% cross-era-merger rate is even more clearly a
   lower bound** than the artifact already states, AND the failure
   mode is concentrated on non-Western names. The career_length>60yr
   screen catches one class; Culbert's finding suggests another
   substantial class (10K-record-per-ORCID over-merges) the screen
   doesn't touch. Methods should explicitly cite Culbert as the
   reason the 5–10% total-error band remains the working assumption
   despite the 3.0% screen result.

2. **Check 3 H7 ABOVE-band ORCID coverage** has a noise floor. Our
   pre-1990 cells got 13–34% ORCID coverage vs <5% predicted. We
   attributed this to "OpenAlex back-propagates ORCID from author
   profile data" (legitimately: an author who registered in 2015 gets
   pre-2012 papers tagged). Culbert's finding tells us *some fraction*
   of that ABOVE-band signal is over-merge artifact, not back-
   propagation. The "methodology bonus" is therefore partially
   synthetic.

3. **§9a Principle 5 ORCID-validation methodology** is compromised
   for non-Western subgroups specifically. Using ORCID-having authors
   as ground truth for gender-inference accuracy assumes the ORCID-
   author linkage is itself correct. If ORCID linkages are over-
   merged on Chinese names, then "ground truth" gender-inference
   accuracy on Chinese-name authors is contaminated. The Lockhart
   2023 P5 bias-uncertainty band Methods commits to has to widen on
   non-Western subgroups.

### 4. Per-journal metadata coverage (Fig. 4)

Beyond references and ORCIDs, Culbert reports per-journal coverage of
abstracts, OA status, and funding info on the shared corpus:

- **Abstracts (Fig. 4a):** OpenAlex has 87% per-article abstract
  coverage on the shared corpus vs ~92% in WoS and Scopus. Most
  journals cluster near full coverage in WoS/Scopus; OpenAlex shows
  more spread, with concentration at top-right (matching WoS/Scopus)
  but a tail with partial coverage. Some journals have higher abstract
  coverage in OpenAlex than WoS/Scopus.
- **ORCID (Fig. 4b):** OpenAlex 92% vs WoS 16% / Scopus 32% per
  article — the over-merge caveat applies.
- **OA status (Fig. 4c):** all three databases use Unpaywall as the
  underlying source; coverage is similar (~49%); slight OpenAlex
  advantage from indexing-lag differences.
- **Funding info (Fig. 4d):** WoS/Scopus better than OpenAlex.
  Notably "funding information associated with articles in over 4,100
  journals can only be found in WoS and Scopus, which could indicate
  a lack of provision of funding information by some scholarly
  publishers for open databases such as OpenAlex and Crossref."

**Why this matters for ws2:** Abstracts are our primary input. The
87% vs 92% gap on the *shared corpus* is small. But this is a
DOI-matched 2015-2022 subset where everything is curated. **The 87%
shared-corpus number is NOT comparable to our pilot's ~50% abstract
coverage on the full 1970–2024 OpenAlex CS+Physics corpus.** The
shared corpus is best-case; our pilot population is worst-case (older,
broader, includes preprints and conference papers without DOI).
Methods should not conflate the two.

Funding info we don't use; OA we use opportunistically. ORCID we use
for the §9a P5 ground-truth subsample — see Key Idea #3 above.

### 5. Volatility of OpenAlex

> "Since the data collection effort of this study, at least 151
> million references have been added to OpenAlex, as of the May 30th
> 2024 snapshot of OpenAlex reportedly expanding the number of
> references by 7.61% compared to the April 25th 2024 snapshot."

A 7.61% reference-count growth in one month is **substantial**. It
corroborates ws2's snapshot-pinning commitment (desideratum §1):
every analysis must be pinned to a specific OpenAlex snapshot date,
and re-running on a newer snapshot is a separate experiment.

The paper also flags **Hauschke & Nazarovets 2025 (preprint at time
of writing)**: "data errors have been discovered in the 'is_retracted'
field of OpenAlex for publications between 22 December 2023 and 19
March 2024, further highlighting the volatility of the metadata
quality in OpenAlex." Implies metadata-quality issues are not just
author-disambiguation but also other fields.

For ws2: snapshot-pinning is well-justified; we should also commit to
documenting **which OpenAlex API version** we're using (if specified)
and to record any post-pull metadata-error notices that affect the
pinned snapshot.

### 6. What OpenAlex covers that WoS/Scopus does NOT

A subtle finding from Culbert's Discussion (re-read of Tables 1, 3):

> "The vastly greater corpus of document records in OpenAlex, compared
> to WoS and Scopus, raises the question of what this additional
> content is, which is covered by OpenAlex but by neither established
> commercial provider. Our findings demonstrate what this content is
> not: it is not that part of the scientific literature which is
> referenced by items within WoS and Scopus."

In other words: the 6× additional content in OpenAlex is genuinely
"different content" — preprints, gray literature, non-traditional
publication formats, conference papers, theses, books, datasets —
NOT just better coverage of the same scholarly mainstream. This has
two implications:

1. **For ws2's CS+Physics 1970–2024 scope**, the OpenAlex non-shared
   majority is largely *not* the kind of content we want anyway. WoS/
   Scopus's curated articles are the analytic core; the long tail is
   what makes the abstract/affiliation bottlenecks worse on the full
   OpenAlex corpus.
2. **For Stage 3 cross-substrate robustness**, the WoS/Scopus
   alternative would *narrow* our analytical population substantially.
   Cross-substrate replication is a useful robustness test but it's
   testing a slightly different hypothesis (the headline divergence on
   the curated subset, not on the inclusive corpus).

---

## Three-Level Results

### Smart-high-schooler reading (~5 min)

OpenAlex is a free, open database of scholarly papers — like Wikipedia
for scientific publications. The paper compares it to two paid
databases (WoS and Scopus) used by university librarians for decades
to evaluate research output. Three findings:

1. **OpenAlex is good enough for citation counting.** When comparing
   the same 16.8M papers across all three, OpenAlex's reference-
   coverage is in the same ballpark as WoS and Scopus.
2. **OpenAlex has more authors with ORCIDs (digital researcher IDs)
   listed**, but it cheats a bit: it sometimes assigns one ORCID to
   many different authors with similar names (especially Chinese
   names). So the high ORCID number is partly real, partly artifact.
3. **OpenAlex changes a lot.** A snapshot from one month is meaningfully
   different from the next month. So any analysis using OpenAlex has
   to record exactly which snapshot was used.

For our project, this paper says: OpenAlex is the right substrate to
use, but we need to (a) pin our snapshot date carefully, (b) treat
the ORCID coverage we find as having a noise floor on non-Western
names, and (c) acknowledge that some metadata quality is worse than
proprietary alternatives.

### Junior/senior-undergraduate reading (~15 min)

Culbert et al. do a head-to-head OpenAlex vs WoS vs Scopus comparison
with two main methodological moves:

**The shared-corpus method** (Section 2.1): exact-DOI match across
all three databases → 16.8M overlap publications (2015–2022). This
controls for the size confound — OpenAlex is 3-4× larger overall, but
on the subset where comparison is fair, OpenAlex performs comparably.

**The internal-coverage metric** (Moed 2005, Chapter 7; van Raan
2019): for a given database, what fraction of cited references are
themselves indexed source items in the same database? This measures
self-consistency — if a paper cites X papers and all X are also in the
database, internal coverage = 100%. Internal coverage is a proxy for
how much of the relevant scholarly conversation a database captures.

The headline result: OpenAlex's internal coverage on the shared corpus
is **83–84%, comparable to WoS (82%) and Scopus (88%)**. On the whole
corpus, OpenAlex undercounts references (because it includes
short-reference long-tail content like preprints) but the curated-
core comparison is fine.

The metadata story is mixed:
- Better in OpenAlex: ORCID coverage (with caveats on
  over-disambiguation), open-access status (Unpaywall-based, all three
  use the same source).
- Worse in OpenAlex: per-article funding info (4,100 journals
  exclusively in WoS/Scopus); abstracts on a per-journal basis (87%
  vs 92%, but with high variance).

The author-disambiguation issue is the headline data-quality concern.
OpenAlex prioritizes recall (find this author's other publications)
over precision (be confident two records are the same author). On
non-Western names — Chinese names with high-frequency surnames and
multiple Anglicization conventions — this produces over-merges, with
documented cases of one ORCID linked to 10,000+ records.

**Implication**: OpenAlex is suitable for bibliometrics but with
caveats specific to (a) which research question (per-paper analyses
are fine; per-author analyses inherit disambiguation noise), (b) which
sub-population (Western names cleaner than non-Western), (c) which
snapshot date (volatility is real).

### Early-grad reading (~30 min)

The paper's contribution is methodological — establishing the shared-
corpus + internal-coverage framework as a tool for cross-database
comparison without size-confound — combined with empirical findings
about each database's strengths and weaknesses on that framework.

Three substantive contributions to bibliometric methodology:

1. **Internal coverage as a partial bias quantifier.** The internal
   coverage metric was Moed's; Culbert applies it cross-database. Two
   databases with the same internal coverage rate may still differ in
   *what they cover*: if WoS and OpenAlex both have 80% internal
   coverage, that doesn't mean their 20% gaps are the same papers. So
   internal coverage is a necessary but not sufficient condition for
   bibliometric equivalence. Culbert is honest about this; the paper
   stops short of claiming OpenAlex is a 1:1 substitute.

2. **The volatility-as-data-quality argument.** Bibliometric databases
   are usually treated as static for analysis purposes. Culbert
   documents that OpenAlex's reference count grew 7.61% in one month
   and that the 'is_retracted' field had errors over a 3-month
   window. The implication: OpenAlex isn't just "less curated" than
   WoS/Scopus, it's "moving" in a way that requires explicit snapshot
   versioning. The paper recommends "treating OpenAlex as a moving
   target" — Culbert specifically suggests "Comparison should be
   limited to a core corpus of items if comparability of bibliometric
   analyses based on OpenAlex to WoS and Scopus is desired."

3. **Disambiguation as the load-bearing data-quality issue.** The
   non-Western-name over-merge finding is specific and operational.
   Some authors with Chinese names had >10,000 publications attributed
   to a single ORCID. The Discussion section explicitly recommends
   that researchers using OpenAlex for author-level analyses verify
   their specific subpopulation before relying on OpenAlex
   author IDs.

Methodological elegance: the shared-corpus restriction enables direct
comparison; the internal-coverage metric requires no external ground
truth; the per-journal metadata analysis enables fine-grained
comparison without aggregating away the dispersion.

The paper's ENGAGE-with-OpenAlex framing is significant for the open
scholarship movement: it positions OpenAlex as a *fit-for-most-purpose*
substitute for WoS/Scopus, with documented caveats. This is more
positive than earlier comparisons (Scheidsteger & Haunschild 2022 on
MAG) which emphasized gaps. Sorbonne University's switch from WoS to
OpenAlex (footnote 1) is the institutional-validation gold star.

---

## Connection to Our Project

### What ws2 takes from Culbert

**1. The §0 Methods justification paragraph.** Phase 0.2 pre-
registration's §0 (analytical-population definition) needs to commit
to OpenAlex as substrate and acknowledge the trade-offs. Specific
language to draft:

> "We use OpenAlex as the bibliometric substrate. Culbert et al. 2025
> establish that on the 16.8M-publication shared-corpus subset (2015–
> 2022), OpenAlex's internal reference coverage is 83.2–83.6%,
> comparable to WoS (81.6%) and Scopus (87.6%). On the whole corpus,
> OpenAlex undercounts references and has lower per-article abstract
> coverage than the proprietary alternatives, and these gaps are
> particularly relevant for our pre-1990 window where DOI registration
> was less common. We restrict our analytical population (§0) to
> abstract-having OpenAlex CS+Physics papers; the §9e selection-bias
> correction layer addresses the systematic under-representation
> introduced by this restriction. We choose OpenAlex despite these
> coverage gaps because (a) reproducibility — proprietary licensing
> would prevent code/data sharing, (b) ORCID coverage advantage —
> Culbert reports OpenAlex's per-article ORCID rate (92%) substantially
> exceeds WoS (16%) and Scopus (32%), enabling our §9a Principle 5
> ground-truth validation, and (c) institutional validation —
> Sorbonne University's December 2023 switch from WoS to OpenAlex
> demonstrates the open-source path is research-grade."

**2. Snapshot-pinning commitment strengthens.** Culbert's 7.61%-in-
one-month reference-count growth and the is_retracted-field errors
mean Phase 0.2 pre-registration commits to:
   - Recording the OpenAlex snapshot date for every pull.
   - Documenting any OpenAlex error notices affecting the pinned
     snapshot at the time of analysis.
   - Treating re-runs against newer snapshots as separate experiments
     per ws2 desideratum §1.

**3. Check 4 lower-bound framing strengthens [SURFACE].** Culbert's
"generous disambiguation" finding gives us a *named mechanism* for
disambiguation errors beyond the cross-era-merger class our screen
catches. The 3.0% rate from Check 4 is more clearly a lower bound,
with the additional class concentrated on non-Western names. Update
plan §10 (disambiguation error floor) inline:
   - Add a paragraph acknowledging Culbert's finding
   - Strengthen the language: "5–10% total-error working assumption"
     becomes "5–10% total-error working assumption, with non-Western
     names plausibly above the upper end given Culbert et al. 2025's
     finding of 10K+ records per ORCID for Chinese-name authors"

**4. Check 3 H7 needs a noise-floor caveat [SURFACE].** Our ABOVE-
band ORCID coverage on pre-1990 cells (13–34% vs <5% predicted) was
attributed to "OpenAlex back-propagates ORCID from author profile
data." This is partly true and partly artifact. Update the Check 3
artifact (`demographic-coverage.md`) inline:
   - Add a paragraph noting Culbert's "generous disambiguation"
     finding as an alternative explanation for the ABOVE-band signal
   - Note that the §9a P5 methodology bonus we claimed is partially
     synthetic; the actual ground-truth subsample size is
     (ORCID-coverage × disambiguation-correctness-rate)
   - Recommend a Phase 0.2 commitment: validate ORCID-author linkage
     on a sample of the §9a P5 subsample before relying on it for
     gender-inference accuracy quantification

**5. Stage 3 cross-substrate robustness path is feasible but
narrowing.** If a reviewer pushes "would your finding replicate on
WoS/Scopus?", Culbert's shared-corpus DOI-match recipe is the
methodology. But the WoS/Scopus version of our analysis would
restrict to DOI-having papers (~16.8M shared, vs OpenAlex's ~243M),
which is a substantial sample reduction. Test on shared corpus only,
report as "methodology robustness on the curated-core subset" rather
than "headline replicates."

### What ws2 explicitly does NOT take from Culbert

1. **The reference-count comparison is not load-bearing for our
   primary metrics.** Our semantic-diversity (embedding distance) and
   demographic-plurality metrics don't depend on reference-graph
   completeness. Test III (Chu-Evans Spearman on top-50 cited papers,
   citation Gini) DOES use citation data, but uses citations *received*
   not references *cited*. So Culbert's reference-undercount on the
   long tail is mostly orthogonal.

2. **The funding-info gap is not relevant.** We don't use funding info.

3. **The shared-corpus restriction does not apply to our analysis.**
   We work on the full OpenAlex CS+Physics 1970–2024 corpus, not the
   2015–2022 DOI-shared subset. Culbert's coverage figures are
   *upper bounds* on what we can expect for our broader population.

### Specific design implications for ws2

| Phase 0.2 commitment | Culbert-driven adjustment |
|---|---|
| §0 OpenAlex justification paragraph | New: cite Culbert specifically |
| Snapshot pinning per desideratum §1 | Existing, strengthens |
| Check 4 disambiguation framing | Existing artifact + plan §10: add Culbert's named mechanism for non-Western over-merge |
| Check 3 H7 ABOVE-band reading | Add noise-floor caveat citing Culbert |
| §9a P5 ORCID validation | Phase 0.2 commit: validate ORCID-author linkage before using as ground truth for non-Western subgroups |
| Stage 3 cross-substrate robustness | Frame as "shared-corpus methodology robustness" not "headline replicates" |

### How ws2 cites Culbert in framing

In the Limitations section: *"We use OpenAlex (Priem et al. 2022) as
our bibliometric substrate. Culbert et al. (2025) compare OpenAlex to
WoS and Scopus and find that on the 16.8M-publication shared-corpus
subset (2015-2022), OpenAlex's internal reference coverage and most
metadata fields are comparable to the proprietary alternatives, with
the notable exception that OpenAlex's author-disambiguation is more
permissive — leading to higher ORCID coverage (92% vs 16-32%) but with
documented over-merging of non-Western (specifically Chinese) author
records. We address this latter limitation through [our §9a P5
validation methodology + Check 4 disambiguation-error band + non-
Western-subgroup-specific bias-uncertainty band per Lockhart 2023
P5]."*

---

## Key Quotes

| # | Quote | Page | Use |
|---|---|---|---|
| Q1 | "OpenAlex provides its data freely and openly, it permits researchers to perform bibliometric studies that can be reproduced in the community without licensing barriers." | Abstract, p. 2475 | §0 reproducibility justification |
| Q2 | "OpenAlex's internal coverage in the Shared Corpus by assuming either Scopus or WoS contain a definitive reference count … would be 83.2% when related to WoS' total reference count, or 83.6% when related to Scopus' reference count, notably these values lie between those of WoS and Scopus." | p. 2484 | Headline reference-coverage equivalence |
| Q3 | "OpenAlex performs a generous disambiguation of authors, resulting in a high ORCID coverage. In particular, some authors with Chinese names were observed to be linked to more than 10,000 publications." | p. 2486 | LOAD-BEARING — disambiguation surface |
| Q4 | "We … recommend caution when utilising OpenAlex for scientometric studies due to the volatility and data quality issues discussed earlier in this section." | p. 2488 | Snapshot-pinning justification |
| Q5 | "Since the data collection effort of this study, at least 151 million references have been added to OpenAlex, as of the May 30th 2024 snapshot of OpenAlex reportedly expanding the number of references by 7.61% compared to the April 25th 2024 snapshot." | p. 2490 | Snapshot-pinning data point |
| Q6 | "Sorbonne University has switched from using the Web of Science (WoS) and Clarivate bibliometric tools to OpenAlex and open-source tools." (footnote 1) | p. 2476 | Institutional-validation citation |
| Q7 | "the proportion of articles in OpenAlex with at least one ORCID present is 92%, and the proportion of articles with at least one ORCID in WoS is 16% and in Scopus 32%." | p. 2486 | ORCID coverage advantage |
| Q8 | "this discrepancy likely merits a deeper analysis in OpenAlex as new versions are released." (re: reference-count discrepancies) | p. 2486 | OpenAlex-volatility caveat |
| Q9 | "the share of records with abstracts in OpenAlex is nevertheless higher than in Crossref" (Kramer 2024 cited) | p. 2489 | Abstract-coverage context |

---

## Study Questions

### Basic (factual recall)

- **B1.** What is the size (in publications) of Culbert's "Shared
  Corpus"? What is its publication-year window?
- **B2.** What is OpenAlex's inferred internal reference coverage on
  the Shared Corpus, and how does it compare to WoS and Scopus?
- **B3.** What is the per-article ORCID coverage rate in each of the
  three databases?
- **B4.** What specific data-quality issue does Culbert document
  about OpenAlex's author-disambiguation algorithm?
- **B5.** What was the percentage growth in OpenAlex's reference
  count between the April 25 and May 30, 2024 snapshots?

### Intermediate (synthesis)

- **I1.** Why does Culbert use the shared-corpus methodology rather
  than comparing whole-corpus statistics directly?
- **I2.** Why is OpenAlex's reference count per record (7.6) so much
  lower than WoS (16.9) on the whole corpus, but comparable on the
  shared corpus?
- **I3.** What's the difference between "source references" and
  "non-source references", and why does this matter for OpenAlex's
  reference-coverage analysis?
- **I4.** Culbert finds OpenAlex captures 92% of articles with at
  least one ORCID. Why is this number "somewhat excessive" per the
  Discussion?
- **I5.** Why does the volatility of OpenAlex (7.61% reference growth
  per month) matter more for our reproducibility than WoS/Scopus's
  monthly updates?

### Advanced (engagement)

- **A1.** Suppose ws2's headline-divergence test runs on the full
  OpenAlex CS+Physics corpus and shows demographic-plurality rising
  while semantic-plurality stagnates. A reviewer responds: "This is
  an OpenAlex-specific artifact — author over-merges on non-Western
  names mean your demographic counts include synthetic authors."
  How would you defend the finding?
- **A2.** Culbert's shared-corpus methodology requires DOI matching.
  ws2's pre-1990 OpenAlex CS+Physics population includes substantial
  non-DOI-having papers. How does this shift Culbert's reference-
  coverage figures (83-84%) as bounds on what we can expect for our
  pre-1990 subset?
- **A3.** Hauschke & Nazarovets 2025 found errors in OpenAlex's
  is_retracted field over a 3-month window. How would ws2's analysis
  pipeline detect/handle similar errors in a load-bearing metadata
  field for us (e.g., publication_year, country_code, ORCID)?
- **A4.** The ORCID over-merge finding is concentrated on non-Western
  names. Can ws2 use the affected-name-region fraction of authors as
  a covariate or stratification axis for the §9a P5 ground-truth
  validation? What would the methodology look like?
- **A5.** Culbert is published in *Scientometrics*, the same venue
  that initially published the Park-Leahey-Funk 2023 disruption
  paper that ws2 critiques. Does ws2 have a methodological-
  reproducibility responsibility analogous to Culbert's, given that
  ws2 is OpenAlex-substrate-dependent? What would such a
  responsibility commitment look like?

---

## Challenge Corner

These are the questions where ws2 has to push back on or extend
Culbert's framing. To be addressed during the collaborative review.

### C1 — Does the over-merge finding affect ws2's CS+Physics analysis specifically?

Culbert's 10K-per-ORCID example is "Chinese names." Our analytical
population is CS+Physics 1970-2024. CS authors include a high
proportion of Chinese-name authors (Check 3 H5 found Physics 2024
East-Asian sub-cell at 11.4% gender_guesser-resolvable rate, suggesting
substantial East-Asian representation in our pilot). **What's the
likely magnitude of over-merge contamination in our specific
population?** Need: a sub-analysis on the pilot's 1511 author records
to look for ORCID-records-count anomalies (e.g., authors with >100
publications attached to the same ORCID).

### C2 — Is the §9a P5 ground-truth validation salvageable?

If non-Western-name authors have unreliable ORCID linkages, then using
ORCID as ground truth for gender-inference accuracy on those subgroups
is contaminated. Two paths:
- (a) **Condition on linkage validation**: only use ORCID-validated
  authors whose linkage is itself confirmed (e.g., by hand-checking
  the author's profile page on orcid.org). Smaller subsample, cleaner
  ground truth. Phase 0.2 commits to a hand-validation budget.
- (b) **Triangulate**: use multiple disambiguation sources (OpenAlex
  ORCID + Author IDs from arXiv + Math Genealogy where available) and
  flag authors whose ORCIDs disagree across sources. Larger but
  noisier subsample.

The paper doesn't tell us which is better; this is for collaborative
discussion.

### C3 — Does Culbert's snapshot-volatility critique go far enough?

Culbert recommends snapshot-pinning. ws2 has already committed to it
(desideratum §1). But Culbert's specific finding — `is_retracted`
errors over a 3-month window — implies metadata fields can be
retroactively corrected. **Should ws2 commit to a "post-snapshot
errata check"** — i.e., before publishing, check OpenAlex's release
notes for errata affecting our pinned snapshot? Adds workflow but
catches latent errors.

### C4 — How do we engage with Culbert in the Methods section?

Two options:
- **Engage briefly** in §0/Limitations only; cite as substrate
  validation.
- **Engage substantively** by adopting Culbert-style cross-substrate
  comparison as a Stage-3 robustness commitment.

The first is ws2's current default. The second is what a reviewer
might ask for if they're skeptical of OpenAlex. Worth pre-empting in
the Methods narrative — but at what level of detail?

### C5 — Pre-1990 specifically

Culbert's data is 2015–2022. Our pre-1990 window (where the
pre-registered drift-mitigation has the most work to do) gets ZERO
direct evidence from Culbert. Does ws2 have any way to assess
OpenAlex's pre-1990 data quality independently? The pilot's
diagnostic checks (Check 1, 1c, 1d, 1e, 1f) cover this. Methods
should explicitly note that Culbert's findings don't extend to our
pre-1990 window and that Phase 0.1 Checks 1-2-4 are our pre-1990
diagnostic stack.

---

## Synthesis Pointers (for `synthesis.md`)

When harvesting into ws2's Methods + Related Work + Limitations:

- **Methods §0:** OpenAlex justification paragraph using Culbert
  Q1, Q2, Q6, Q7. Three-bullet substrate-choice rationale:
  reproducibility, ORCID-coverage advantage, institutional
  validation.
- **Methods §10 (disambiguation error floor):** add Culbert's
  named over-merge mechanism as an extension to the existing
  career_length>60yr screen.
- **Methods §9a P5 (ORCID validation):** new commitment to
  ORCID-author-linkage validation before using as ground truth.
  Specify Phase 0.2 hand-validation budget if (a) above (300
  names? 500?).
- **Limitations:** explicit acknowledgment that (i) abstract
  coverage on full corpus is worse than Culbert's shared-corpus
  numbers; (ii) ORCID over-merge is a non-Western-specific
  failure mode; (iii) reference-count discrepancies on long-tail
  content are out-of-scope but worth flagging; (iv) snapshot
  volatility per Culbert + Hauschke-Nazarovets motivates our
  pinning + post-pull errata-check commitments.
- **Stage 3 robustness frontier:** Culbert's shared-corpus DOI-
  match recipe as the "if a reviewer pushes" cross-substrate
  robustness path.

---

## Discussion Notes

(To be filled during the collaborative review session.)

### On the over-merge finding (C1) — spot-check on pilot

[Discussion]

### On §9a P5 (C2) — which validation path

[Discussion]

### On post-snapshot errata (C3)

[Discussion]

### On Methods engagement depth (C4)

[Discussion]

### On pre-1990 (C5) — what additional diagnostic, if any

[Discussion]

---

## Surfaces flagged for retro adjustment

**Two surfaces from this close-read affect Phase-0.1 finding
re-readings (will summarize separately for the user):**

1. **Check 4 disambiguation lower-bound strengthens** — Culbert's
   named non-Western over-merge mechanism is a class our
   career_length>60yr screen doesn't catch. Plan §10 inline note
   should be expanded.

2. **Check 3 H7 ABOVE-band ORCID has a noise floor** — the
   "methodology bonus" from OpenAlex back-propagating ORCID is
   partly synthetic (over-merge). The §9a P5 validation subsample
   needs an upstream linkage-validation step before being relied on
   as ground truth.

Neither surface is fatal to existing commitments. They strengthen
caveats rather than retire commitments. Worth the user's review
before Phase 0.2 pre-registration locks.
