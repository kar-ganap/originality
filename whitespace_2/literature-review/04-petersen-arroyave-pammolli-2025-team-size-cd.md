# 04 — The disruption index suffers from citation inflation: Re-analysis of temporal CD trend and relationship with team size reveal discrepancies

**Authors:** Alexander Michael Petersen, Felber J. Arroyave, Fabio Pammolli
**Venue:** *Journal of Informetrics* 19 (2025), 101605
**PDF:** `literature-review/04-petersen-arroyave-pammolli-2025-team-size-cd.pdf` (gitignored)
**SI:** `literature-review/04-petersen-arroyave-pammolli-2025-team-size-cd_SI.pdf` (gitignored)
**DOI:** 10.1016/j.joi.2024.101605

---

## Background

PAP 2025 is the deeper methodological close-read on team-size and
temporal CD-index trends. Where PAP 2024 (paper 03 in our reading
list) formalized the citation-inflation critique through deductive +
empirical + computational analysis, PAP 2025 develops the empirical
side at scale: 7.8M articles from 1995–2015 in the SciSciNet dataset,
with proper multivariate regression controls.

Three substantive findings:

1. **Temporal trend in CD is at the level of noise** after controlling
   for r_p (reference list length), c_p (citation impact), and k_p
   (team size). The residual 0.06σ effect size means the apparent
   PLF "decline of disruption" is mostly artifact of omitting
   inflation-related controls. Disruptiveness has *incrementally
   increased since 2006* — consistent with three independent
   re-analyses (Bentley 2023, Holst 2024, Macher 2024).

2. **Team-size relationship to CD is also at the level of noise**
   (0.09σ) after CI controls, and *shifts from negative to positive
   for k_p ≥ 8*. This contradicts Wu-Wang-Evans 2019's headline
   "small teams disrupt; large teams develop" finding. PAP 2025
   argues WWE's negative correlation is a methodological artifact
   from (a) using percentile-based dependent variable, and (b)
   omitting r_p and c_p controls.

3. **PNAS vs. PNAS Plus quasi-experiment.** PAP 2025 exploits a
   natural experiment: PNAS Plus articles (online-only publishing
   format) differ from regular PNAS articles primarily in *reference
   list length* (~39% more references on average), with otherwise
   nearly indistinguishable characteristics. **100% of the difference
   in average |CD_{p,5}| between the two subsets is explained by
   the difference in average r_p.** This is the cleanest possible
   demonstration that r_p alone causes CD measurement bias.

For ws2, this paper directly affects:

- **Test II team-size control specification.** Our gap regression
  currently has `avg team size per paper (trimmed)` as one of
  several controls. PAP 2025 implies we should also include r_p
  (reference list length), c_p (citation impact), and possibly
  quadratic terms when team size is a covariate. Otherwise we risk
  inheriting WWE 2019's omitted-variable bias.
- **Test IV team-diversity × novelty setup.** Our four T_p
  operationalizations don't use CD-index, so PAP 2025's specific
  CD-team-size finding doesn't directly apply. But the *general
  lesson* — that scientometric regressions involving team size +
  network metrics need explicit r_p / c_p / year-FE controls —
  applies to our Test IV regression specification.
- **Phase 0.2 batch refinement to Test II + Test IV regression
  specifications.** This is the load-bearing addition from PAP 2025.

---

## Key Ideas

### 1. Two streams of critique (background framing)

PAP 2025 organizes the post-PLF critique landscape into two streams:

**Stream A — data quality issues** (Macher 2024, Holst 2024):
- Macher 2024: missing patent citations at the beginning of PLF's
  patent dataset artificially reduce r_p for early-era patents.
  Correcting these makes the negative trend in CD(t) "largely
  disappear."
- Holst 2024: papers with r_p = 0 generate CD = 1 by construction
  (a degenerate maximum-disruption value). These zero-reference
  outliers are concentrated in early years; correcting for them
  makes negative trend in CD(t) "largely disappear."

**Stream B — methodological choices** (Bornmann 2020, Leydesdorff
2021, PAP 2024, Ruan 2021, Wu & Wu 2019):
- Critiques of how CD is defined and applied to bibliometric
  contexts.
- PAP 2024 (the deductive critique we just reviewed) is the
  methodological-choice line.

PAP 2025 contributes to both streams by:
- Demonstrating CI is the inextricable structural problem (Stream B).
- Showing that data-quality issues (Stream A) and CI (Stream B)
  *both* contribute to PLF-reported negative trends, and *both* are
  resolved by appropriate controls.

### 2. The PNAS vs. PNAS Plus quasi-experiment

This is the paper's methodologically strongest move. The setup:

- *PNAS* articles are published in print + online with traditional
  format conventions (length, reference list size).
- *PNAS Plus* articles are published online-only with relaxed length
  conventions, allowing longer articles + longer reference lists.
- Both formats are *peer-reviewed and accepted by the same editorial
  process*. Submissions are not pre-sorted by intent or quality;
  the format is author-designated.

**The "natural experiment" claim:** PNAS and PNAS Plus articles are
*satisfactory counterfactuals* for testing whether publications with
larger r_p are biased toward smaller CD_p, on average, *aside from*
the reference-list-length difference. They differ on r_p but match
on most other characteristics (citation impact, team size, content
domain).

The empirical result (Fig. 4):

- PNAS Plus articles have ~39% more references on average than PNAS
  articles.
- |CD_{p,5}| values are slightly smaller for PNAS Plus.
- **100% of the difference in average |CD_{p,5}| between the two
  subsamples is explained by the difference in r_p.**

This is the cleanest possible empirical demonstration that r_p
alone causes CD measurement bias. No alternative explanation
(quality, content, audience) explains any of the observed
difference.

### 3. The 7.8M-article re-analysis (Section 4.3)

The headline scaled-up empirical analysis. Setup:

- **Sample:** 7.8M articles from 1995–2015 in the SciSciNet dataset
  (Lin et al. 2023b), restricted to ranked top-1000 journals by
  publication volume.
- **Filters:** 10 ≤ r_p ≤ 200; 1 ≤ k_p ≤ 25; 1 ≤ c_p ≤ 1000; uncited
  publications excluded (where CD = 0 by definition); |CD| extreme
  outliers excluded.
- **Regression:** `CD_{p,5,j,t} = b_j + b_k ln(k_p) + b_{k2}(ln k_p)² +
  b_{kxt}(ln k_p × t) + b_r ln(r_p) + b_{r2}(ln r_p)² + b_c
  ln(c_{p,5}) + b_{c2}(ln c_{p,5})² + γ_t + ε_j`

Key features:
- *Quadratic terms* on r_p, c_p, k_p — captures non-linearities.
- *Team-size × time interaction* (b_{kxt}) — controls for team-size
  growing over time.
- *Year fixed effects (γ_t)* — controls for secular trends.
- *Journal fixed effects (b_j)* — controls for journal-specific
  characteristics.
- *Standardized via journal-year normalization* — uses NormCD =
  (CD − mean_jt)/σ_jt, so coefficients are in σ units.

**Headline results:**

*(a) Temporal trend (γ_t):* After all controls, the residual γ_t
trend is at the noise level. The biggest residual effect (year 2015
vs. baseline 1995) is +0.06σ — a tiny effect that emerges only
post-2006. Bentley/Holst/Macher's three independent re-analyses
also find this incremental *increase* post-2006.

*(b) Team-size trend (b_k + b_{k2}):* After controls, the
relationship between CD and team size *shifts from negative to
positive at k_p ≈ 8*. The magnitude (0.09σ at k_p = 25 vs.
k_p = 2) is at noise level. Critically, this contradicts WWE 2019's
sign and magnitude.

### 4. Specific critique of Wu-Wang-Evans 2019

PAP 2025's diagnosis of why WWE got negative team-size effects:

**(i) Percentile-based dependent variable.** WWE used percentile
values of CD_p rather than raw values. Because most publications
have CD ≈ 0 (the distribution is extremely concentrated at 0; see
Fig. 2), small absolute shifts in CD value translate to large
shifts in percentile rank. This *amplifies* small effect sizes
into apparent large ones.

**(ii) Likely omission of c_p and r_p controls.** WWE's
Supplementary Table 4 has "no clear model specification provided"
and it's "unclear how they controlled for publication year."
Likely omitted r_p and c_p, leading to omitted-variable bias on
team size (since k_p, r_p, c_p all grow over time).

PAP 2025's reanalysis with proper controls reverses the sign and
shrinks the magnitude to noise level.

### 5. Specific critique of Park-Leahey-Funk 2023

PAP 2025's diagnosis:

**(i) Year-only control.** PLF's Extended Data Table 8 only shows
year-indicator coefficients, not estimates for r_p, c_p, k_p
controls. Possible they omitted these or didn't report them.

**(ii) Robustness checks insufficient.** PLF's random-rewiring
robustness check holds r_p and c_p constant by construction. So
this only detects bias attributable to *correlated citation
behavior*, not bias from *data quality issues + CI* — which is
exactly what PAP 2025 (and Macher 2024, Holst 2024) target.

**(iii) Sign vs. nominal-value distinction.** PLF's main analysis
relies on nominal CD values, but their robustness checks operate
on derived statistics (e.g., percentile rank). The robustness
checks don't transfer to the headline finding.

### 6. Critique of Lin et al. 2023a (collaboration distance and disruption)

A third paper PAP 2025 critiques (this is in the same critique-
chain spirit):

- Omits c_p and r_p from regression.
- Uses *sign* of CD_p instead of CD_p — which only depends on the
  numerator difference N_i − N_j, hiding all the denominator-
  driven inflation.
- Vulnerable to data quality issues (Holst, Macher) that affect
  early-era papers more.

The general lesson: many post-PLF papers using CD-index in
regressions inherit the omitted-variable bias problem.

### 7. Three conditions for cross-temporal CD analysis (Discussion)

PAP 2025 lays out three conditions any *future* CD-variant should
satisfy for cross-temporal use:

1. **Stationary distribution over time** — e.g., normalized
   citation metrics that leverage log-normal citation distribution.
2. **Most weakly sensitive to secular growth** (especially CI from
   r(t) and n(t) growth).
3. **Captures consensus of broader scientific community** — not
   entirely dependent on author choices (e.g., reference list
   composition).

PAP 2025 doesn't propose a specific CD-variant satisfying all
three; they advocate for "the development of unbiased citation-
network metrics" without specifying a replacement. Same posture
as PAP 2024.

### 8. Effect-size magnitude lesson

Throughout the paper, PAP 2025 emphasizes that the residual
effects (after CI controls) are *0.06σ for time*, *0.09σ for
team size*. These are at the level of noise. The substantive
claim: **scientometric regressions involving CD-index produce
small effect sizes once properly controlled, regardless of the
specific X variable being studied (time, team size, geographic
distance, etc.).**

This matters for ws2: when we report effect sizes in our own
regressions (Test II gap regression, subfield mechanism test,
Test IV team-diversity × novelty), we should be calibrated about
what counts as substantive. PAP 2025's 0.06–0.09σ residuals are
*not* substantively significant. ws2's effect-size threshold for
headline claim should be calibrated above this noise floor.

---

## Results — Three Levels

### Level 1: For a smart high-schooler

Wu-Wang-Evans 2019 (a famous *Nature* paper) said small scientific
teams produce more "disruptive" work than large teams. This idea
influenced science policy and funding decisions for years.

This paper says: that finding is mostly an artifact of how the
study was done. When you redo the analysis properly — controlling
for the things that grow over time (especially how many references
papers cite, which has grown a lot since 1995) — the team-size
effect almost disappears. The remaining tiny effect even reverses
direction for teams of 8+ people.

The paper proves this in two ways. First, a clean natural
experiment: PNAS journal articles (regular) vs. PNAS Plus articles
(longer, more references) — they're identical in every way except
reference list length. The CD-index difference between them is
*entirely* explained by the reference-list-length difference, not
anything substantive.

Second, they redo the analysis on 7.8 million articles with proper
controls. The team-size effect collapses to 0.09σ — basically
noise. Same for the time-trend effect (0.06σ). The PLF "decline of
disruption" finding doesn't survive proper controls.

The implication: many post-PLF studies that use CD-index in
regressions are likely producing artifacts, not real findings. The
problem is structural to how the metric is built.

### Level 2: For a junior/senior undergraduate

The paper's main empirical contribution is a multivariate regression
on 7.8M articles 1995–2015 (SciSciNet dataset) with proper controls.
The regression specification:

`CD_{p,5,j,t} = b_j + b_k ln(k_p) + b_{k2}(ln k_p)² + b_{kxt}(ln k_p × t) + b_r ln(r_p) + b_{r2}(ln r_p)² + b_c ln(c_{p,5}) + b_{c2}(ln c_{p,5})² + γ_t + ε_j`

After controls, both the temporal trend (γ_t residual) and the
team-size relationship (b_k + b_{k2}) collapse to noise-level effect
sizes (0.06σ and 0.09σ respectively).

Two separate critiques:

**(1) Wu-Wang-Evans 2019 likely got negative team-size effect from
two sources:** (a) using percentile-based dependent variable, which
amplifies tiny absolute effects into apparent large ones (because
CD distribution is extremely concentrated at 0); (b) likely omitting
r_p and c_p controls, allowing omitted-variable bias to make k_p's
coefficient negative.

**(2) Park-Leahey-Funk 2023's robustness checks miss the data
quality + CI issues** — random rewiring holds r_p constant by
construction, so it can't detect bias from r_p inflation.

The cleanest result is the PNAS vs. PNAS Plus quasi-experiment:
two publication formats nearly indistinguishable except PNAS Plus
articles have ~39% more references. The |CD| difference is *100%
explained* by the r_p difference. No quality or content explanation
survives.

The paper argues for three conditions any cross-temporal CD-variant
should satisfy: stationary distribution, weakly sensitive to CI,
captures community consensus. They don't propose a specific
replacement metric.

### Level 3: For an early graduate student

The methodological move worth understanding deeply: **the PNAS vs.
PNAS Plus quasi-experimental design**. This is what PLF lacks — a
clean identification strategy that isolates r_p as the causal
driver of CD measurement bias.

The natural-experiment logic: if PNAS and PNAS Plus articles are
identical on all observed and unobserved characteristics *except*
r_p, then any difference in average |CD| between the subsamples
must be attributable to r_p alone. PAP 2025 demonstrates this is
empirically the case (~100% explanatory power; Fig. 4c).

Three subtle methodological observations:

**(1) The PNAS vs. PNAS Plus design isn't a perfect natural
experiment.** Article-format choice is non-random — authors choose
which format to submit to. Possible the format-choice mechanism
correlates with substantive characteristics we haven't observed
(audience size, reading time expectations, type of contribution).
PAP 2025 doesn't fully address this, but their Fig. S3 shows
indistinguishability across many dimensions, which is the best
they can do.

**(2) The quadratic specification matters.** The team-size
relationship being non-monotonic (negative for small k_p, positive
for k_p ≥ 8) wouldn't be visible in a linear-only regression. This
is a methodological observation: **scientometric regressions
involving covariates that span orders of magnitude (team size 1–25,
references 10–200) often need polynomial specifications to capture
the actual functional form.** Linear-only regressions can produce
misleading sign-and-magnitude results.

**(3) The 0.06σ / 0.09σ effect-size lesson is important and
underappreciated in scientometrics.** The norm in the literature is
to report whether an effect is "statistically significant" without
calibrating against a noise threshold. PAP 2025's standardized
effect sizes (in σ units, with explicit comparison to "noise level")
suggest a discipline reform: report effect sizes in σ, not just
p-values, and treat anything below ~0.1σ as noise unless the sample
size justifies otherwise.

The paper's limitations:

**(a) PAP 2025 doesn't propose a CD-index replacement.** They
articulate three conditions any future variant should satisfy, but
don't develop one. This leaves the literature without a clean
metric for "disruption" — though PAP would argue (correctly) that
*no current variant satisfies the three conditions*, so the field
should pause rather than rush to a flawed replacement.

**(b) The 7.8M-article analysis covers 1995–2015 only.** PLF's
analysis covered 1945–2010. PAP 2025 doesn't extend back into the
pre-1995 era where data quality issues (per Macher and Holst) are
strongest. So the headline "PLF's negative trend disappears with
controls" claim is technically only verified for the post-1995
era, though the data-quality-correction studies extend the claim
backward.

**(c) The PNAS vs. PNAS Plus quasi-experiment has limited external
validity.** PNAS is a high-prestige multidisciplinary journal; the
generalizability to other publication contexts (specialty
journals, arXiv preprints, patents) is plausible but not directly
demonstrated.

---

## Connection to Our Project

### What ws2 takes from PAP 2025

**(1) Test II gap regression specification needs r_p, c_p controls
+ year FE.** Currently our gap regression has these controls:
- log(N papers in year Y) — field size
- avg team size per paper (trimmed)
- median references per paper
- arXiv fraction
- log(distinct active authors in year Y)
- field-entry rate
- subfield composition vector

We have *median references per paper* as a control. PAP 2025
implies we should also consider:
- *Quadratic term on log(team size)* — to capture the non-linear
  team-size relationship.
- *Citation impact (c_p)* aggregated to field-year level — to
  control for citation-density confound.
- *Team size × year interaction* — to control for team-size growing
  over time (PAP 2025's b_{kxt} term).

These are small specification refinements rather than major design
changes. Our gap regression isn't testing the same hypothesis as
PAP 2025's CD-index regression, but the controls are structurally
parallel.

**(2) Test IV regression specification needs analogous treatment.**
Test IV regresses paper-level novelty (N_p) on team-level
demographic diversity (T_p). Currently controls include:
- number of authors
- number of references
- mean author career stage
- mean author institutional prestige tier
- log paper age
- field dummy
- year-FE
- subfield-FE

PAP 2025 implies:
- *Quadratic term on log(team size)* — yes (number of authors
  enters log-linearly currently).
- *Quadratic term on log(references)* — yes (we currently include
  number of references log-linearly).
- *Citation impact c_p as a control* — currently NOT in our spec.
  Adding it would be parallel to PAP 2025's specification.
- *Team size × year interaction* — currently not in our spec; less
  load-bearing for Test IV than for Test II since Test IV has
  year-FE that absorbs aggregate temporal effects.

These are small refinements to Test IV's regression spec. Phase 0.2
batch addition.

**(3) Effect-size threshold calibration.** PAP 2025's 0.06σ /
0.09σ noise-level effect sizes give us a calibration point. ws2's
current effect-size threshold for headline claims:
- Test I slope ≥ 0.02 SD/year (1-SD gap change over 50 years)
- Test IV |γ₁| ≥ 0.05 after standardization

These are reasonable but should be reviewed against PAP 2025's
calibration. 0.05σ for Test IV is approaching PAP's noise level —
maybe we should raise to 0.1σ to be safely above noise. Worth a
brief revisit during Phase 0.2 pre-registration.

**(4) Lesson on omitted-variable bias in scientometric regressions.**
PAP 2025's core methodological lesson — that any scientometric
regression involving CD-index (or related citation-network metrics)
needs r_p, c_p, k_p, year-FE as standard controls — generalizes to
ws2 even though our metrics aren't CD-index-based. We should ensure
our regression specifications include analogous structural
controls.

### What ws2 explicitly does NOT take from PAP 2025

**(1) The PNAS vs. PNAS Plus quasi-experimental design.** ws2 is an
observational time-series study, not a quasi-experiment. We don't
have an analogous natural-experiment setting. The methodological
lesson (controls needed) transfers; the specific design doesn't.

**(2) The CD-index three-conditions framework as a replacement
metric proposal.** ws2's metrics already satisfy these conditions
(rank-invariant Spearman; bounded Gini; embedding-space metrics).
We don't need PAP 2025's framework as a guide — we already have
the right metrics.

**(3) The post-2006 incremental increase in disruption finding.**
Bentley/Holst/Macher/PAP 2025 all find a small post-2006 increase
in disruption after controls. This is interesting substantively
but doesn't directly affect ws2's design — we measure semantic
plurality, not disruption per se. We can cite the post-2006
upturn as context in Discussion if relevant to our findings.

### Specific design implications for ws2

- **Test II regression specification refinement.** Add quadratic
  terms on log(team size); add citation impact c_p as a control;
  consider team-size × year interaction. Phase 0.2 batch addition.
- **Test IV regression specification refinement.** Add citation
  impact c_p as a paper-level control; quadratic terms on log(team
  size) and log(references). Phase 0.2 batch addition.
- **Effect-size threshold calibration review.** Ensure our headline
  thresholds (Test I 0.02 SD/year; Test IV |γ₁| ≥ 0.05) are above
  PAP 2025's 0.06–0.09σ noise level. Possibly raise Test IV
  threshold. Phase 0.2 batch.
- **Methods-paragraph citation of PAP 2025.** When defending our
  inflation-immune-evidence framing under (c-prime), cite PAP 2025
  alongside PAP 2024 and Petersen-Holst as the cumulative critique
  chain. PAP 2025 is the strongest *empirical* demonstration; PAP
  2024 is the strongest *deductive* demonstration.

---

## Key Quotes

For Methods / Discussion of the ws2 paper:

> "After controlling for temporal variation and CI, we find that
> CD increases (albeit weakly) with team size (for k_p ∈ [3, 25]) —
> which is consistent with a statistically significant and positive
> coefficient associated with ln k_p identified in our companion
> study (Petersen et al., 2024). As with the temporal trend, the
> net effect is at the level of noise, with the difference between
> k_p = 2 and k_p = 25 corresponding to just a 0.09σ effect size.
> These results are in disagreement with the results reported Wu et
> al. (2019)." (p. 10 — the headline team-size finding.)

> "Wu et al. base their analysis upon differentials in the
> percentile values of CD_{p,5}, which obscures the relatively small
> magnitude of the effect size obtained for nominal CD values, which
> are extremely narrowly distributed around CD ≈ 0." (p. 10 — the
> percentile-amplification critique of WWE 2019.)

> "Our results show that 100% of the difference in average |CD_{p,5}|
> between the two publication subsets is explained by δ, the
> difference in the average r_p across the two subsets." (p. 9 —
> the PNAS vs. PNAS Plus quasi-experimental headline.)

> "Beyond data quality issues, another issue is the small effect
> size measuring correlations between CD and relevant covariates.
> Our re-analysis of temporal trends and team-size trends generate
> effect sizes at the 0.06σ and 0.09σ level, respectively; moreover,
> the directions of the trends are in disagreement with previous
> studies (Park et al., 2023; Wu et al., 2019)." (p. 10 — the
> magnitude-of-effect-size lesson.)

> "Citation metrics should follow a stationary distribution over
> time, such as with normalized citation metrics that leverage the
> log-normal distribution of citation counts. ... metrics should be
> most weakly sensitive to the secular growth of the academic
> enterprise, in particular CI deriving from increasing r(t) and
> n(t). And third, citation metrics should capture the consensus of
> the broader scientific community ... and not be entirely dependent
> on author choices (as with the selection of items included in a
> reference list)." (p. 11 — three conditions for cross-temporal
> citation metrics.)

---

## Study Questions

**Warm-up (Level 1):**

1. **SQ1** — What's the substantive finding of the PNAS vs. PNAS
   Plus quasi-experiment, and why is it methodologically stronger
   than purely observational regression analyses?

2. **SQ2** — PAP 2025 reports residual effect sizes of 0.06σ (time)
   and 0.09σ (team size) after controls. Why does the paper call
   these "noise level"? What would substantively significant effects
   look like instead?

**Intermediate (Level 2):**

3. **SQ3** — The team-size relationship to CD shifts from negative
   to positive at k_p ≈ 8. Why does the quadratic specification
   matter — would a linear-only regression have surfaced this
   pattern?

4. **SQ4** — PAP 2025 critiques WWE 2019 on two grounds: (a)
   percentile-based dependent variable; (b) likely omission of r_p
   and c_p controls. Why does the percentile transformation amplify
   small effect sizes into apparent large ones?

5. **SQ5** — The post-2006 incremental increase in disruption
   (after controls) is consistent across PAP 2025 + Bentley 2023 +
   Holst 2024 + Macher 2024. What does this consistency say about
   the underlying signal vs. data-quality artifact? Is it a real
   substantive shift in science?

**Advanced (Level 3):**

6. **SQ6** — The PNAS vs. PNAS Plus quasi-experiment has limited
   external validity. PNAS is high-prestige multidisciplinary; the
   format choice is author-designated and possibly correlated with
   substantive characteristics. How seriously should we take the
   "100% of |CD| difference explained by r_p" claim, and what
   alternative explanations should we worry about?

7. **SQ7** — PAP 2025 articulates three conditions for cross-
   temporal CD-variants but doesn't propose a replacement. What
   would a metric satisfying all three look like? Is it constructible
   in principle, or does the conjunction of conditions rule out any
   citation-network-based metric?

8. **SQ8** — For ws2 specifically: what's the strongest case for
   adding citation impact c_p as a control variable in our Test II
   gap regression and Test IV team-diversity × novelty regression?
   What would be missed without it?

---

## Challenge Corner

**C1:** PAP 2025's PNAS vs. PNAS Plus quasi-experiment is the
methodologically strongest move in the paper. But quasi-experiments
have known pitfalls. Two sub-questions:

(a) Article-format choice (PNAS vs. PNAS Plus) is author-designated.
Could the format-choice mechanism correlate with substantive
characteristics in ways that contaminate the "100% explained by
r_p" claim? E.g., authors who choose PNAS Plus might write more
review-style articles vs. discovery-style articles. Authors who
choose PNAS Plus might be more senior. PAP 2025's Fig. S3 shows
indistinguishability on observed covariates, but not on unobserved
ones. How worried should we be?

(b) For ws2: we don't have an analogous quasi-experimental setting.
Are there ws2-relevant settings we could exploit? Candidates:
arXiv preprint vs. journal version of the same paper (different
reference list lengths); pre-2010 vs. post-2010 papers in the same
subfield (different reference list growth rates within author's
career). Worth exploring or out of scope?

**C2:** The post-2006 incremental disruption increase is robust
across four independent studies (PAP 2025, Bentley 2023, Holst
2024, Macher 2024). This is a substantively interesting finding —
disruption is *increasing*, not decreasing, in recent eras. Two
sub-questions:

(a) Is this consistent with ws2's expected findings? If our
canonical-concentration metric shows continued rise post-2006, but
disruption is incrementally rising in the same period, does that
mean our metric is capturing something different from the
disruption-decline narrative — or is it capturing something that
actively contradicts it?

(b) The post-2006 increase is small (0.06σ over 9 years).
Substantively, does this matter, or is it just within the noise
floor of detection? What kinds of real-world phenomena correspond
to a 0.06σ effect over a decade?

**C3:** PAP 2025 critiques WWE 2019 on percentile transformation
amplifying tiny effects. This is a generalizable methodological
lesson. Two sub-questions:

(a) Are any of ws2's metrics or analyses vulnerable to similar
percentile-amplification? Specifically: when we report Spearman
top-50 (a percentile-defined metric), are we doing the same kind
of amplification? Or is rank-invariance structurally different from
percentile-amplification?

(b) For Test IV's team-diversity × novelty regression: if we report
N_p in raw cosine distance vs. percentile rank, would we get
different effect-size magnitudes? Should we pre-commit to one or
report both?

**C4:** PAP 2025's three conditions for cross-temporal CD-variants
(stationary distribution, weakly sensitive to CI, captures
community consensus) are useful for evaluating *any* time-varying
bibliometric metric, not just CD. Two sub-questions:

(a) Apply the three conditions to ws2's metrics (Spearman top-50,
citation Gini, cluster entropy, effective dim, mean pairwise
distance). Which pass each condition? Where do we have residual
concerns?

(b) Are there conditions PAP 2025 misses that should also matter
for ws2? E.g., robustness to author-disambiguation errors;
robustness to missing references in early-era data.

**C5:** PAP 2025's regression spec (Eq. 4) includes quadratic
terms and interactions. Our current Test II and Test IV
specifications are mostly linear with year-FE. Two sub-questions:

(a) What's the principled reason to add quadratic terms? Does the
underlying functional form of our hypothesized relationships
require non-linearity, or are we adding terms defensively?

(b) Adding quadratic terms doubles the number of regression
coefficients (linear + squared). With our pre-registered effect-
size thresholds, does this dilute statistical power, or is the
sample size large enough that this doesn't matter?

**C6:** PAP 2025's critique of WWE 2019 generalizes to many other
papers using CD-index in regressions. The pattern: omit r_p / c_p
/ year-FE → get spurious effect on whatever X variable is being
studied. Two sub-questions:

(a) Are there other widely-cited scientometric findings that ws2
should be aware of as potentially artifactual? Candidates: Lin et
al. 2023 (collaboration distance), Wang et al. 2023 (geographic
dispersion), Leahey et al. 2023 (novelty types). PAP 2025 critiques
several but not all.

(b) For ws2: should our Discussion include a brief paragraph on
"the broader landscape of post-PLF critique," or stay narrow on
just the citation-inflation question?

---

## Synthesis Pointers (for `synthesis.md`)

1. **Test II gap regression specification refinement.** Add r_p, c_p,
   year-FE controls; quadratic on log(team size); team-size × year
   interaction. Per PAP 2025 lessons. Phase 0.2 batch addition.

2. **Test IV regression specification refinement.** Add c_p
   (citation impact) as paper-level control; quadratic terms on
   log(team size) and log(references). Phase 0.2 batch addition.

3. **Effect-size threshold calibration check.** PAP 2025's 0.06σ
   (time) and 0.09σ (team size) noise-level effect sizes give us a
   calibration point. Review ws2's headline thresholds (Test I 0.02
   SD/year; Test IV |γ₁| ≥ 0.05). Possibly raise Test IV threshold
   to 0.10σ to safely clear noise. Phase 0.2 batch decision.

4. **PAP 2024 + PAP 2025 = full critique chain for our (c-prime)
   framing.** PAP 2024 is the deductive demonstration; PAP 2025 is
   the empirical demonstration. Cite both alongside Petersen-Holst
   in our Methods paragraph on CD-index decision. Strongest possible
   citation chain.

5. **Post-2006 incremental disruption increase is interesting
   substantive context.** Multiple independent re-analyses (PAP
   2025, Bentley 2023, Holst 2024, Macher 2024) find this. ws2 can
   cite this in Discussion if our findings show continued canonical
   concentration rise post-2006 — provides interesting tension
   ("concentration rises while disruption rises").

6. **Three-conditions framework for cross-temporal metrics** is
   useful for ws2's Methods-section defense of our metric choices.
   Apply explicitly: Spearman top-N satisfies (1) stationarity, (2)
   CI-robustness, (3) consensus capture; same for our other metrics.

7. **Percentile-amplification lesson.** WWE 2019's percentile
   transformation amplified tiny effects. ws2 doesn't use percentile
   transformations on our primary metrics, but worth noting for
   any percentile-related analysis we do (e.g., Spearman top-N is
   percentile-defined; is this vulnerable?). C3 walkthrough may
   address this.

8. **Generalizable critique pattern.** Many post-PLF papers using
   CD-index inherit omitted-variable bias. ws2's Discussion can
   briefly acknowledge "the broader landscape of post-PLF critique"
   without endorsing any specific critique paper as definitive.

---

## Discussion Notes

(Filled during collaborative review session. Blank until that
session happens.)

### On C1 — PNAS vs. PNAS Plus quasi-experimental validity

(Pending.)

### On C2 — post-2006 disruption increase in ws2 context

(Pending.)

### On C3 — percentile-amplification in ws2 metrics

(Pending.)

### On C4 — three-conditions framework applied to ws2

Working session with user, 2026-04-26.

**The three conditions (PAP 2025 Discussion).**

1. *Stationary distribution over time.* Metric's distribution
   should have stable mean/variance/higher moments across eras.
   Cross-era comparisons require apples-to-apples distributions.
2. *Most weakly sensitive to secular growth.* Even if approximately
   stationary, a metric should not have its values mechanically
   driven by citation network density growth.
3. *Captures consensus of broader scientific community.* Metric
   should reflect community attention, not author choices (e.g.,
   focal paper's own reference list composition).

**Why CD-index fails all three.**

- Condition 1: CD distribution mechanically pushed toward 0 over
  time as R_k grows; not stationary.
- Condition 2: CD = CD^nok / (1 + R_k); R_k grows with citation
  network density; mechanically driven by network growth.
- Condition 3: CD's signal (N_i − N_j) depends on which
  predecessors the focal author chose to cite; heavily author-
  choice-dependent.

**Why the conjunction is hard.** If a metric satisfies all three,
it must be invariant to network growth AND to author choices.
This rules out:
- Network-structural metrics like CD (fail 2 and 3).
- Raw citation count metrics (fail 1 and 2).
- Reference-list-composition metrics (fail 3).

What survives:
- Field-year-normalized citation metrics (z-scores within field ×
  year) — satisfy 1 by construction.
- Rank-based metrics — satisfy 2 trivially; satisfy 3 because
  ranks reflect community-wide citation patterns.

**Application to ws2 metrics — explicit pass/fail per condition.**

| Metric | Cond 1 (stationarity) | Cond 2 (CI-robustness) | Cond 3 (community consensus) |
|---|---|---|---|
| Spearman top-N | ✓ bounded in [−1, 1]; rank-stable across years | ✓ rank-invariant by construction | ✓ top-N determined by community citation patterns |
| Citation Gini | ✓ bounded in [0, 1] | Partial — undercoverage in older eras could compress distribution; tested by detrended diagnostic | ✓ based on community-wide citation distribution |
| Cluster entropy | ✓ bounded entropy; stationary if cluster fits temporally stratified (desiderata §11) | ✓ embedding-based, not citation-based | ✓ clusters reflect content distribution across field |
| Effective dim | ✓ ratio of singular values; bounded above | ✓ embedding-based | ✓ year-Y embedding distribution |
| Mean pairwise distance | ✓ bounded distance metric; stable if embedding model stable | ✓ embedding-based | ✓ pairwise structure reflects community distribution |

**Refinement (added 2026-04-26 after disruption-novelty discussion).**
The above table covers our *aggregate* metrics for canonical
concentration and semantic plurality (Tests I-III). Test IV's N_p
metrics need separate treatment because they're at the paper level
and depend on focal-paper-specific data:

| Test IV N_p variant | Cond 1 | Cond 2 | Cond 3 |
|---|---|---|---|
| N_p^author (cosine distance to reference centroid) | ✓ bounded | ✓ embedding-based | **Partial fail** — depends on focal paper's reference choices |
| N_p^community (cosine distance to year-Y canonical centroid) | ✓ bounded | ✓ embedding-based | ✓ canonical centroid is community-determined |
| N_p^combinatorial (U-M-S reference-pair atypicality, Stage 3) | depends on null-model stability | ✓ rank-based comparison | **Mixed** — depends on focal-paper reference pairs (author choice) but evaluated against community co-citation null |

**The substantive observation: Test IV N_p^author inherits the same
condition-3 vulnerability that PAP 2025 raises about CD-index.**
N_p^author depends on what the focal paper chose to cite, which is
exactly the "depends on author choice" failure mode. This was an
oversight in the original C4 assessment.

**Mitigation already partly in place:** our multi-operationalization
commitment for Test IV's N_p (primary + secondary + tertiary) hedges
across the spectrum of condition-3 dependence. N_p^community is the
cleanest community-driven measure.

**Refinement to commit (separate Phase 0.2 batch item):** flip Test
IV N_p primary/secondary labels — make N_p^community the headline
primary metric (cleanest condition-3 satisfaction) and N_p^author the
secondary/alternative operationalization. This is parallel to the
(c-prime) inflation-immune-evidence framing: report the *cleanest*
metric as primary, not the most-historically-used.

**Net: all aggregate ws2 metrics pass all three conditions; Test
IV N_p^community passes; Test IV N_p^author and N_p^combinatorial
have partial condition-3 vulnerabilities documented openly.** Two
caveats remain on the broader set:
- Citation Gini's condition 2 holds conditional on the detrended
  correlation-with-r(t) diagnostic showing |corr| < 0.7 (already
  pre-registered).
- Cluster entropy's condition 1 holds conditional on the temporal-
  stratification cluster-fit (already committed via desiderata §11).
- Effective dim and pairwise distance condition 1 holds conditional
  on embedding-model stability (already committed via drift-
  mitigation ladder).

So the three-conditions check doesn't generate new commitments —
it provides a *unified framework* for the structural defenses we've
already committed to elsewhere.

**Are there conditions PAP 2025 misses that should also matter for
ws2?**

Two potential additions worth flagging:
- *Robustness to author-disambiguation errors.* For our demographic-
  plurality metrics, this is load-bearing (we use OpenAlex
  disambiguation). PAP 2025 doesn't engage demographic-style metrics.
- *Robustness to missing references in early-era data.* PAP 2025
  acknowledges this via reference to Macher 2024 and Holst 2024 but
  doesn't add it as a fourth condition. ws2 has explicit pre-1990
  data-quality tier handling (per desiderata §10 and Phase 0.1 §13).

These extensions are already addressed by our existing commitments
(C2(b) OpenAlex coverage diagnostic; pre-1990 tier specifications;
identity-confidence diagnostic from Hofstra C8). The three
conditions plus these two extensions = a complete framework for
ws2's metric defense.

**For the eventual ws2 paper Methods section.**

The three-conditions framework provides clean exposition of why
our metric choices are appropriate for cross-temporal analysis.
Adding to Phase 0.2 batch (extension of (c-prime) sub-commitment
1): use PAP 2025's three conditions as the *organizing structure*
for the Methods-section paragraph defending inflation-immunity,
with our specific structural arguments (rank-invariance, bounded
distribution, embedding-orthogonality) as the answers under each
condition.

### On C5 — quadratic terms in ws2 regression specifications

(Pending.)

### On C6 — broader landscape of post-PLF critiques

(Pending.)

---

## Study Question Walkthroughs

### SQ1 — PNAS vs. PNAS Plus quasi-experiment

(Pending.)

### SQ2 — Why 0.06σ / 0.09σ are "noise level"

(Pending.)

### SQ3 — Quadratic specification and team-size sign reversal

(Pending.)

### SQ4 — Percentile-amplification of small effects

(Pending.)

### SQ5 — Post-2006 incremental disruption increase

(Pending.)

### SQ6 — PNAS vs. PNAS Plus external validity

(Pending.)

### SQ7 — Three-conditions framework constructibility

(Pending.)

### SQ8 — c_p as control variable in ws2 regressions

(Pending.)
