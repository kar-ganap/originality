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

Working session with user, 2026-04-26.

**The user's meta-question.** "Does a quasi-experiment buy us
anything in ws2 irrespective of what specifically it'd look like?"
This reframes C1 from "what specific QE setting could we use?" to
"do we *want* QE-style identification at all given our scope?"

**What QE buys you in general.** Quasi-experiments support claim
types that pure observation can't:
1. Causal claims ("X causes Y" not just "X correlates with Y").
2. Counterfactual claims ("If X were different, Y would be
   different").
3. Mechanism claims ("X is the active causal channel" not just "X
   is associated with Y").

PAP 2025's PNAS quasi-experiment buys exactly this — converts
correlational "CD declines with r_p" into quasi-causal "r_p alone
causes the CD effect."

**Applied to ws2's claim structure.**

*Tests I-III (aggregate divergence):*
- Claim: time series covary or decouple in specific ways.
- Identification needed: none. Descriptive structural questions.
- QE benefit: zero. Not making causal claims at this level.

*Test IV (cross-sectional team-diversity × novelty):*
- Claim: T_p and N_p correlate cross-sectionally.
- Identification needed: descriptive. Pre-baked "Causal
  interpretation caveat" already disclaims causal direction.
- QE benefit: could give causal direction claim. But we've
  explicitly decided not to claim this.

*Subfield mechanism test (CanonConc_s → DivMag_s):*
- Claim: subfields with higher canonical concentration show more
  divergence.
- Identification needed: descriptive subfield-level association.
- QE benefit: theoretically could establish causation, but hard to
  imagine a QE setting on canonical concentration (slow-moving
  aggregate; no natural variation source).

*Metric-validity claims (inflation-immunity):*
- Claim: our metrics are inflation-immune by construction.
- Identification needed: analytical + observational (already
  committed: rank-invariance + detrended correlation diagnostic).
- QE benefit: arXiv-vs-journal-version style design could
  empirically demonstrate metric stability under r_p variation.
  But analytical defense + observational diagnostic already
  address this. Marginal gain.

**Substantive answer.**

*For central claims: no QE benefit.* Observational by design;
program-aware observational-scope meta-commitment makes this
explicit. Adding QE identification would either pull us into causal
territory we've disclaimed, or address concerns already addressed
via cheaper means.

*For methodological credibility against reviewer pushback:
marginally yes.* QE pre-empts "how do you know this isn't
confounded?" pushback. But the benefit is bounded — reviewers
reading carefully see our scope is observational by design.

*For very specific sub-claims: theoretically yes, practically not.*
The metric-inflation-immunity claim is the only place QE might add
beyond existing defense. Setting it up requires additional Stage 3
work; marginal info gain is small; expanding scope without
commensurate payoff.

**Recommendation: out of scope, mental-banked.**

QE is out of scope for ws2 given:
1. Observational-scope meta-commitment.
2. Claims being descriptive/correlational by design.
3. Existing analytical + observational defenses sufficient.

Worth mental banking:
- If reviewers push hard on causal questions in the eventual ws2
  paper, ready answer about why we declined QE pursuit.
- Follow-up ws2-extended studies (post-program) might benefit from
  QE designs.

**Substantive observation: program-level distributed QE.**

The 3-whitespace program structure is itself partly a
quasi-experimental architecture, distributed across whitespaces:

| Whitespace | Methodology | What it provides |
|---|---|---|
| **ws2 (observational)** | Real-data covariation documentation | Empirical patterns |
| **ws3 (formal model, future)** | Theoretical mechanism specification | Causal hypotheses |
| **ws1 (LLM-agent simulation, future)** | Counterfactual simulation | Mechanism testing |

ws3 + ws1 together provide the causal claims that ws2 deliberately
avoids. Causal identification is *distributed across the program*,
not concentrated in ws2. This is a strength of the program design —
each whitespace contributes the evidence its methodology is best
at; the conjunction of evidence supports causal claims.

ws2 doesn't need within-ws2 QE identification because ws1 + ws3 are
doing that work *at the right epistemic layer* for that kind of
claim.

**No new Phase 0.2 batch additions from C1.** This is a
methodological observation rather than a design refinement. The
substance is captured in this Discussion Notes entry for future
reference if reviewers push on causal-identification questions.

### On C2 — post-2006 disruption increase in ws2 context

Working session with user, 2026-04-26.

**Sub-question (a): consistent or contradictory with ws2's expected
findings?**

Canonical concentration and disruption measure different facets:

| Concept | What it measures |
|---|---|
| Canonical concentration | *Which papers* dominate citation distribution at year Y (Spearman top-N stability + citation Gini) |
| Disruption (CD-index post-corrections) | *How citation networks form* around individual papers (Type-1 vs. Type-2 citer ratios) |

**Two scenarios where rising disruption + rising canonical
concentration coexist consistently:**

*(1) New canonical papers emerging via disruption.* New disruptive
papers post-2006 (e.g., AlphaGo, ML methods, COVID-era bio
breakthroughs) become canonical themselves — replacing predecessors
in the citation network. Canon "rises" in the sense of consolidated
attention; disruption "rises" because new entrants displace
predecessors. Substantively interesting: scientific renewal at the
canon level.

*(2) Distribution-shape vs. list-stability decoupling.* Our two
canonical-concentration metrics measure different things:
- *Spearman top-N* (primary): adjacent-year stability. Should
  *decline* if new disruptive papers enter canon.
- *Gini* (secondary): citation distribution concentration. Could
  rise if new disruptive papers concentrate attention on
  themselves.

Spearman top-N rising while disruption rises would be *contradictory*.
Gini rising while disruption rises is *consistent* (new disruptive
papers aggregating citations to themselves).

**Predictive interpretive grid:**

| ws2 finding pattern | Interpretation |
|---|---|
| Spearman top-N rises post-2006 | Tension with disruption-rising narrative; our metric capturing list-stability dynamics distinct from disruption |
| Gini rises post-2006 | Consistent with disruption-rising; new canonical papers concentrating attention |
| Both rise | Different facets; report transparently |
| Both fall | Contradicts disruption-rising; suggests metrics measure neither aligned-with nor opposite-to disruption |

**Sub-question (b): does 0.06σ over a decade matter?**

Mechanical interpretation: σ for CD_5 in PAP 2025 is small
(distribution concentrated around 0). 0.06σ ≈ 0.0006–0.003 in
absolute CD units; ~0.06–0.3% of [−1, 1] range over a decade. Tiny.

Three readings:

*(1) Truly noise.* Argument against: four independent re-analyses
finding same direction is unlikely under pure noise.

*(2) Real but small.* Genuine post-2006 increase but too small to
reverse longer-term decline. Most likely reading.

*(3) Leading edge of regime change.* 9 years is a short window; if
increase continues, cumulative effect could be substantial.
Plausible substantive drivers: ML/AI emergence post-2012,
computational biology, COVID-era acceleration. But small magnitude
suggests slow regime change if any.

**For ws2's analytical window (1990–2024):** roughly the second
half is post-2006. The disruption-uptick literature operates within
our window. Our findings should be interpreted in this context —
not as competing theory but as concurrent observations of
related-but-distinct phenomena.

**Real-world phenomena corresponding to 0.06σ over a decade:**
- ML/AI domain emergence post-2012 (AlexNet, transformers, LLMs);
  plausibly 0.01–0.02σ alone via field restructuring.
- Computational biology / bioinformatics post-2010 (CRISPR, GWAS
  at scale).
- COVID-era biomedical acceleration (2020+); high-velocity
  publication + uptake.
- Aggregated, 0.06σ over a decade is plausible. Not nothing, not
  large.

**Phase 0.2 batch refinements (small).**

*(1) Add post-2006 disruption-uptick context to (c-prime) Discussion
paragraph.* One sentence acknowledging the four-paper convergence
(PAP 2025, Bentley 2023, Holst 2024, Macher 2024). Frame as
concurrent observation, not competing/supporting our findings.

*(2) Add 2006 as Test I pre-registered break-point candidate.*
Currently 1991-93, 1998-2000, 2008-09, 2012, 2018-20 for CS;
adding 2006 aligns with disruption-literature convergence.

Both are small, defensible, fold cleanly into existing commitments.

**Substantive takeaway: the post-2006 finding gives us interpretive
context, not a competing theory.** Our metrics measure different
facets than disruption; the relationship between our findings and
the post-2006 uptick depends on which canonical-concentration metric
we examine and what direction it moves.

### On C3 — percentile-amplification in ws2 metrics

Working session with user, 2026-04-26.

**The WWE 2019 amplification pattern (what we're checking against).**

WWE 2019 used percentile-rank values of CD as their dependent
variable rather than raw CD values. Combined with CD's extremely
concentrated distribution (95.5% within ±2σ of CD ≈ 0; σ small),
this amplifies tiny absolute effects into apparent large effect
sizes in percentile-rank units. PAP 2025's reanalysis finds the
underlying raw effect is 0.09σ (noise level); WWE's percentile-
based reporting made it appear substantively significant.

**The vulnerability requires two conditions co-occurring.**

1. *Percentile transformation:* take individual paper's metric
   value, transform to percentile rank within field-year, regress
   on covariates.
2. *Highly concentrated underlying distribution:* σ small relative
   to range, so small absolute shifts → large percentile shifts.

If either condition is absent, WWE-style amplification doesn't
operate.

**Per-metric audit for ws2.**

| Metric | Percentile transform? | Concentrated dist? | Vulnerable? |
|---|---|---|---|
| Spearman top-N (canonical primary) | No — list-stability between years, not per-paper percentile | N/A | No |
| Citation Gini (canonical secondary) | Lorenz-curve in construction, but single per-year aggregate | Bounded [0,1], reasonable variance | No |
| Cluster entropy (semantic primary A) | No — entropy on probability dist | N/A | No |
| Effective dimensionality (semantic primary B) | No — eigenvalue-based | N/A | No |
| Mean pairwise distance (semantic secondary) | No — direct distance | N/A | No |
| Demographic plurality (Shannon, Gini-Simpson, Rao's Q) | No | N/A | No |
| Test IV T_p | No — Rao's Q over team | N/A | No |
| Test IV N_p (community + author + combinatorial) | No — direct cosine distance; z-scoring is not percentile transform | N/A | No |

**Key distinction surfaced: rank-invariance ≠ percentile-amplification
vulnerability.**

These are *different* properties:
- *Rank-invariance:* metric stable under monotonic transformations
  of input values. Spearman top-N has this.
- *Percentile-amplification vulnerability:* small absolute
  differences → large percentile-rank differences. Requires
  percentile transformation + concentrated distribution.

A metric can be rank-invariant AND not vulnerable. A metric can
also be neither rank-invariant nor vulnerable. The two properties
address different aspects of metric behavior.

**ws2 reporting style matches PAP 2025's recommended practice.**

- Test I slope: SD/year (raw metric units).
- Test IV γ_1: σ-standardized units of T_p and N_p (z-scored for
  coefficient comparability — *not* percentile-transformed).
- Tests I-III: distributions of metrics with bootstrap CIs in raw
  units.

**Subtler vulnerability: rank-instability near the top-N threshold.**

The closest analog to percentile-amplification that could operate
in ws2 is rank-instability in our Spearman top-N list driven by
small absolute citation differences for papers near rank N.

Scenario:
- Paper A has 100 citations, ranked #50.
- Paper B has 99 citations, ranked #51.
- A small shift (10 citations) flips their ranks.
- Affects Spearman correlation by changing list membership.

**Mitigation already in place:**
- Citation distribution is heavy-tailed near top — papers at rank
  45-55 typically differ in citation counts by 10-20%, not single
  digits. List is more stable than WWE-concentrated case.
- Multi-N robustness already pre-registered (N ∈ {30, 50, 100}).
- Multi-Δ Spearman co-reporting (1, 5, 10) provides additional
  stability check.

**New explicit sensitivity check (added 2026-04-26).** To verify
the heavy-tail assumption empirically and bound the rank-instability
concern, add a citation-difference-near-threshold diagnostic:

For each (field × year), compute:
- Δ_50 = citation count at rank 50 minus citation count at rank 51
- Δ_50_relative = Δ_50 / citation count at rank 50
- Plot distribution of Δ_50_relative across (field × year) cells.

Pre-registered interpretive thresholds:
- Median Δ_50_relative > 5% → heavy-tail assumption holds; rank-
  instability concern minimal.
- Median Δ_50_relative 1-5% → moderate; multi-N robustness check
  becomes more load-bearing.
- Median Δ_50_relative < 1% → heavy-tail assumption fails; rank-
  instability is a real concern; trigger expanded multi-N
  reporting (additional N ∈ {200, 500} for robustness).

Cost: ~half-day Stage 2 effort. Computational only; uses existing
data.

**Methods-section addition.** Sentence acknowledging PAP 2025's
percentile-amplification critique and ws2's compliant reporting:
"Following PAP 2025's recommended practice, ws2 reports effect
sizes in σ-units of raw metrics rather than percentile-rank
transformations. Our metrics are not vulnerable to WWE-style
percentile-amplification because they either operate at the
aggregate level (Tests I-III metrics, computed once per
field-year) or use direct value-based measurements (Test IV T_p
and N_p)." Folds into (c-prime) sub-commitment 1 (the three-
conditions framework Methods paragraph).

**No major new Phase 0.2 batch additions** — primarily confirms
our existing methodological choices are correct. Three small
additions:
1. Methods-sentence in (c-prime) sub-commitment 1.
2. Citation-difference-near-threshold sensitivity check.
3. Pre-registered interpretive grid for the diagnostic.

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

Working session with user, 2026-04-26.

**Sub-question (a): What's the principled reason for quadratic
terms?**

PAP 2025's empirical finding: team-size relationship to CD shifts
from negative to positive at k_p ≥ 8 — non-monotonic. Linear-only
specification would miss this entirely.

Substantive logic for *why* the relationship might be non-monotonic:
- *Very small teams (1-2):* too small to take on ambitious
  disruptive projects; constrained by individual capacity.
- *Small-to-medium teams (3-7):* sweet spot — cohesive enough to
  coordinate, large enough to attempt ambitious problems.
- *Large teams (8+):* shift toward big-question collaborative
  projects (HEP collaborations, bioinformatics consortia) that
  themselves can be disruptive at field level.

Whether this exact pattern applies to *team-diversity → novelty*
in ws2 is unclear. We don't have strong priors on functional form.

**Decision: defensive specification.** Add quadratic terms with
the rule: if coefficient is near zero, behavior reduces to linear;
if non-zero, we capture non-monotonicity. Cost: minor coefficient-
count increase.

**Sub-question (b): Statistical power concern?**

*Test II (year-level):* 35 years post-1990 × 2 fields = 70
field-year observations; existing ~10 covariates. Adding 1-2
quadratic coefficients reduces effective DOF from ~60 to ~58-59.
Modest power impact but real.

*Test IV (paper-level):* millions of observations. Adding 1-2
coefficients has negligible power impact. Not a concern.

**Resolution.**

*For Test II:* report results both with and without quadratic
terms. If quadratic coefficients are not significant at p<0.05,
default to linear specification for headline. If significant,
report non-linear version. **Pre-registered fallback rule** —
prevents post-hoc decision about which specification to feature.

*For Test IV:* run quadratic by default; power isn't a concern.

**Phase 0.2 batch refinement to existing Test II commitment.** Add
linear-vs-quadratic fallback rule to existing "add quadratic on
log(avg team size)" addition.

### On C6 — broader landscape of post-PLF critiques in Discussion

Working session with user, 2026-04-26.

**Sub-question (a): Other potentially-artifactual scientometric
findings.**

PAP 2025 explicitly critiques several papers:
- WWE 2019: team-size → disruption
- PLF 2023: time → disruption
- Lin et al. 2023a: collaboration distance → disruption (omits
  r_p, c_p; uses sign of CD)

Implicitly critiques (mentioned but not deeply):
- Wang et al. 2023b: geographic dispersion → disruption
- Leahey et al. 2023: novelty types

The general pattern: any scientometric paper using CD-index in
regression with an X variable that grows over time is at risk if
it omits r_p, c_p, year-FE.

**Should ws2 audit these specifically?** No — out of scope. We
engage the critique chain collectively, not paper-by-paper
critiques. We're not in the business of post-mortem on the
post-PLF literature.

**Sub-question (b): Discussion paragraph on the broader landscape?**

Two competing considerations:

*Pros:* demonstrates methodological awareness; pre-empts reviewer
pushback on related papers; connects ws2 to richer scholarly
conversation.

*Cons:* scope creep; Discussion length expansion (we're already
adding paragraphs via (c-prime), three-conditions framework,
post-2006 disruption-uptick context); risk of seeming to take
sides on debates not central to ws2.

**Decision: brief mention is right.**

Add one sentence within the (c-prime) Discussion paragraph
acknowledging the broader landscape: "The broader post-PLF
critique landscape extends to other CD-based scientometric findings
(e.g., Lin et al. 2023a on collaboration distance; Wang et al.
2023b on geographic dispersion). ws2 engages the citation-inflation
question specifically rather than auditing related findings."

Don't expand to a separate paragraph. Don't take positions on
individual papers. Just acknowledge landscape exists and mark our
scope.

This is enough to demonstrate awareness without expanding scope.
Reviewers who push for detailed engagement get the honest answer:
"those debates are out of ws2's scope; we focus on citation-
inflation specifically because it directly affects our methodology
defense."

**Phase 0.2 batch refinement to (c-prime) Discussion paragraph.**
One-sentence addition acknowledging broader post-PLF critique
landscape with explicit scope-bounding.

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

Working session with user, 2026-04-26.

**Why the "100% explained by r_p" claim is strong evidence.** PNAS
and PNAS Plus articles are peer-reviewed by the same editorial
process, accepted to the same journal, with format determined by
author choice. PAP 2025's Fig. S3 shows the two subsamples are
indistinguishable on multiple observed covariates. The 39%
difference in average r_p translates into the entire observed
|CD| gap — within this clean comparison, the evidence is
compelling.

**Three alternative explanations to worry about.**

*(1) Author-format-choice mechanism.* Format choice is non-random.
Possible the choice mechanism correlates with substantive
characteristics that aren't observed:
- *Article type:* PNAS Plus may attract more *review-style* or
  *comprehensive* articles (which naturally have longer reference
  lists *and* are likely more synthesizing → less disruptive).
- *Author seniority:* senior authors write longer papers and choose
  PNAS Plus more often. The r_p-CD correlation could partly reflect
  senior-author-CD correlation.
- *Topic complexity:* topics requiring more background
  contextualization tend to have longer reference lists *and* tend
  to be more synthesizing.

PAP 2025's Fig. S3 controls for *observed* covariates, but
unobserved ones could still operate.

*(2) Length itself rather than r_p specifically.* PNAS Plus
articles are *longer overall* (more pages, more methods detail).
The "100% explained by r_p" claim assumes r_p is the active causal
channel, but article length is the upstream variable. If length
itself causes CD effects (longer papers more comprehensive →
synthesizing → less disruptive), then r_p is a proxy for length.

This matters because: capping reference list lengths (PAP 2025's
policy proposal) wouldn't help if length itself is the issue.

*(3) High-prestige sample selection.* PNAS is a high-prestige
multidisciplinary journal. Generalizability to specialty journals,
arXiv preprints, or patent literature is plausible but not
directly demonstrated.

**How seriously to take the claim.**

The 100% point estimate is *suggestive* of r_p being the dominant
driver in this comparison. Alternative explanations could partly
explain the same correlation. **The conjunction with PAP 2024's
deductive critique + Macher 2024 + Holst 2024 makes the overall
case strong even if the PNAS quasi-experiment alone has
limitations.**

For ws2: cite PAP 2025's PNAS evidence as *one piece* of supporting
evidence, not as the load-bearing demonstration. The (c-prime)
framing already does this — we engage the *aggregate* critique
chain rather than relying on any single piece.

### SQ7 — Three-conditions framework constructibility

Working session with user, 2026-04-26.

**Candidate metrics that satisfy all three conditions.**

*(a) Field-year normalized citation z-scores: z_p = (c_p − μ_jt) / σ_jt.*
- Cond 1: ✓ z-scores have unit variance by construction.
- Cond 2: ✓ normalization removes secular growth.
- Cond 3: ✓ citation count comes from community.
- *But:* measures citation impact, not disruption. Not a
  CD-replacement.

*(b) Rank-based metrics like Spearman top-N.*
- All three pass. *But:* measures canonical-list stability, not
  disruption.

*(c) Citation-distribution-shape metrics (Gini, entropy).*
- Pass all three with caveats. *But:* measures concentration, not
  disruption.

*(d) Direct community-reception metrics (e.g., "fraction of papers
in field-year that cite p without citing p's predecessors").*
- Almost CD's numerator (N_i / total citers).
- Cond 1: depends on whether the measure stabilizes across eras.
- Cond 2: vulnerable to citation density growth.
- Cond 3: ✓ community-driven.
- *Mixed pass.*

**The honest conclusion: no-go theorem implication.**

The three conditions essentially rule out any citation-network
metric that depends heavily on the focal paper's own reference list
composition. What survives are "what does the community do with
this paper" metrics — citation count metrics, citation-rank
metrics, citation-distribution metrics.

**Disruption specifically (in the CD-index sense) is fundamentally
about the relationship between citers and the focal paper's
predecessors, which involves the focal paper's reference list.** So
disruption is structurally tied to author choice in a way that may
rule out a clean cross-temporal disruption metric satisfying all
three conditions.

**This may be a no-go theorem for citation-network-based disruption
metrics.** The community may need a *different conceptual framework*
for measuring scientific disruption — perhaps text-based novelty,
reception-based attention, or hybrid approaches — rather than a
better CD-variant within the citation-network paradigm.

**For ws2.** We don't need a disruption metric. Our metrics measure
canonical concentration and semantic plurality, both of which
satisfy the three conditions. The no-go theorem doesn't constrain
us. *But* the lesson is methodologically interesting: when reading
scientometric papers proposing "improved" CD-variants, expect them
to fail one or more of the conditions, since the conjunction may
be unsatisfiable.

### SQ8 — c_p as control variable in ws2 regressions

Working session with user, 2026-04-26.

**For Test II (year-level gap regression).**

Aggregate c(t) [mean citation impact at year-level] correlates
with r(t) (citation inflation), n(t) (publication growth), and
demographic plurality (since later eras have both more citations
available and more demographically diverse authorship).

Without c(t) control, our β_t (gap-trend coefficient — the
headline finding) absorbs whatever c(t) is doing. Possible
directions:
- *Upward bias on β_t:* if c(t) growth correlates with rising
  demographic plurality and falling semantic plurality.
- *Downward bias on β_t:* if c(t) growth is causally related to a
  third factor that suppresses the gap.

Without explicit c(t) control, can't distinguish these scenarios.
Bias direction unclear, but risk is real — and a reviewer
noticing the omission could push hard on this.

**Without c_p in Test II:** confounded β_t that doesn't isolate
the demographic-vs-semantic gap shift from secular changes in
citation impact. Headline finding becomes vulnerable to reviewer
pushback ("did you control for citation impact?").

**For Test IV (paper-level regression).**

The omitted-variable bias issue is more direct. c_p correlates
with both T_p and N_p in non-trivial ways:

- *c_p ↔ T_p:* highly-cited papers may attract more international
  collaborations (high T_p) — *or* may be from established (often
  less demographically diverse) labs (low T_p). Direction unclear.
- *c_p ↔ N_p:* highly-cited papers may have more diverse reference
  lists (high N_p) — *or* may follow canonical templates (low N_p).
  Direction unclear.

Without c_p control, γ_1 absorbs whatever c_p contributes — exactly
the WWE 2019 omitted-variable bias pattern PAP 2025 critiques.

**Without c_p in Test IV:** confounded γ_1 that doesn't isolate the
team-diversity → novelty effect from citation-impact effects.

**The bad-control problem (subtle methodological concern).**

Adding c_p as a control assumes citation impact is a *confounder*,
not a *mediator*. But:
- If diverse teams *produce* more impactful papers, c_p is partly a
  *mediator* of T_p → outcome.
- Controlling for c_p absorbs part of the team-diversity effect we
  want to estimate.

This is the classic "bad control" problem in causal inference.
Whether c_p is a confounder or a mediator depends on causal-
direction assumptions we haven't made.

**The right move: pre-register both specifications.**
- *Specification A:* without c_p control. Captures total
  team-diversity → novelty effect (including via citation-impact
  mediation if any).
- *Specification B:* with c_p control. Captures direct effect
  (excluding mediation via c_p).

If γ_1 differs materially between A and B, that itself is
informative — tells us whether team diversity affects novelty
primarily through citation-impact mediation or directly. If γ_1 is
similar in both, c_p isn't a mediator and B is the right
specification.

Pre-registered transparency rather than picking sides.

**Phase 0.2 batch refinement to Test IV spec:** add both
with-c_p and without-c_p specifications to the pre-registered
analysis plan, with interpretive grid for whether to read γ_1 as
direct or total effect. (Captured in the Test IV refinement
commitment alongside the c_p control addition.)
