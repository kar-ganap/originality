# 07 — Name-Based Demographic Inference and the Unequal Distribution of Misrecognition

**Authors:** Jeffrey W. Lockhart, Molly M. King, Christin Munsch
**Venue:** *Nature Human Behaviour* 7(7), 1084–1095 (2023)
**PDF:** `literature-review/07-lockhart-king-munsch-2023-name-based-demographic-inference.pdf` (gitignored)
**SI:** `literature-review/07-lockhart-king-munsch-2023-name-based-demographic-inference_SI.pdf` (gitignored)
**DOI:** 10.1038/s41562-023-01587-9

---

## Background

Lockhart, King & Munsch 2023 (henceforth Lockhart) is the
methodologically most consequential paper for ws2's demographic
plurality measurement. It directly attacks the foundation of
name-based gender and race/ethnicity inference — the technologies
underlying our committed Genderize+NamSor pipeline.

The empirical core: a survey of 19,924 social science authors
(sociology, economics, communications) 2015–2020 from Web of Science,
matched against name-based inference outputs from four gender
algorithms (genderize.io, M3-Inference, R's `predictrace`, R's
`gender`) and four race/ethnicity algorithms (ethnicolor's Florida
voter model, ethnicolor's North Carolina voter model, R's
`predictrace`, R's `wru`). Self-reported demographics serve as the
ground-truth comparison.

The findings are dramatic:

- **Overall gender error rate: 4.6%** (genderize.io). Sounds modest.
- But **error rates are wildly heterogeneous by subgroup:**
  - Women misgendered 3.5× more than men.
  - **Chinese women misgendered 43%** of the time.
  - Trans people misgendered 57% of the time.
  - **Nonbinary people misgendered 100%** of the time (definitional —
    algorithms only output binary).
- **Race/ethnicity error rates 14% overall** but with even worse
  heterogeneity:
  - Black: 65% error rate.
  - MENA: 73% error rate.
  - Filipino: 55% error rate.
  - Native Hawaiian / Pacific Islander: high but small-sample.
  - White / Asian / Latino: under 10%.

The theoretical core: **name-based demographic inference does not
measure "ground truth" — it measures cultural consensus about how
names signal demographic categories.** Names don't have intrinsic
gender or race; people *signal* (consciously or unconsciously)
demographic categories through naming conventions, and algorithms
infer based on aggregate naming patterns in reference populations.
This means:

1. There is no "true" gender of a name — only a cultural ascription
   that varies by population, era, and context.
2. Errors cannot be eliminated by more training data or better
   algorithms — they reflect fundamental cultural ambiguity and
   heterogeneity.
3. The relationship between name and demographic category is
   irreducibly heterogeneous across subpopulations.

The paper closes with **five principles for responsible use of
name-based demographic inference:**

1. **Critical refusal** — sometimes don't infer at all.
2. **Align mechanism with method** — only for ascription-based
   research questions, not identity questions.
3. **Population-specific inference using domain expertise.**
4. **Use subgroups with high accuracy.**
5. **Use only aggregate estimates, with bias-quantification on
   target population.**

For ws2: this paper validates and reframes our existing weight-by-
confidence approach (Hofstra C4 commitment) and our gender inference
hand-validation (Holst C3 commitment). It also generates several
new commitments — particularly around per-intersectional-cell
accuracy reporting, the cultural-ascription-vs-identity framing,
and explicit alignment with Lockhart's principle 5 (aggregate
estimates + bias-quantification on target population).

---

## Key Ideas

### 1. Names measure cultural consensus, not identity

The theoretical centerpiece. Names don't *intrinsically* signal
gender or race — they signal *culturally*. People (consciously or
unconsciously) name children to signal categories; the aggregate
of these choices forms an "imperfect cultural consensus around the
gendered, racialized, and other associations of many names."

Implications:
- "Ground truth" is misnamed — there is no ground truth, only
  cultural ascription.
- Cultural consensus is *local* — "Andrea" is woman in US, man in
  Italy.
- Cultural consensus is *contextual* — academic publications differ
  from social media; first-generation immigrants differ from
  second-generation.

This reframes the entire methodological discussion. Our weight-by-
confidence approach (committed in Hofstra C4) treats inference
confidence as approximating ground truth. Lockhart says: there is
no ground truth; inference is *by definition* cultural ascription.
We're not measuring identity; we're measuring how names are
culturally read.

### 2. The 4.6% overall error rate masks dramatic subgroup heterogeneity

Headline number from Genderize.io (the most popular tool): 4.6%
overall gender error rate. Sounds small enough to not worry about.

But subgroup decomposition (Lockhart's Figure 1 + 2):

| Subgroup | Gender error rate |
|---|---|
| Men (overall) | ~2% |
| Women (overall) | ~7% (3.5× men) |
| Chinese women | 43% |
| Vietnamese | ~25% |
| Nonbinary | 100% (definitional) |
| Trans (any gender) | 57% |
| Asian | 16% |
| Black | 7% |
| White | 4% |

The 4.6% population-average is misleading because it averages over
groups with vastly different error rates. **For substantive analyses
involving subgroups, the relevant error rate is the subgroup-
specific one, not the average.**

### 3. Errors are fundamentally not eliminable

Algorithms are approaching the *information-theoretic limit* of
name-based gender inference accuracy. More training data, better
models, or larger reference populations *will not* fix the issue
because:

- Some names are inherently ambiguous (Leslie, Andrea — different
  gender associations in different populations).
- Some demographic groups have less name-gender correlation
  (East-Asian transliteration loses tonal information that signals
  gender in Mandarin).
- Naming patterns shift over time, generations, migration.

This is a **fundamental limit, not an engineering challenge.**
Wishful thinking that "next-generation tools will be better" doesn't
work — we're approaching the limit.

### 4. Errors are heterogeneous *and* compound across covariates

Lockhart's Figure 3 (two-way cross-tabulation): error rates by
intersectional categories. Examples:
- Chinese women: 43% misgendered.
- Trans Chinese person: ~80%+.
- Black trans: ~60%.
- Nonbinary disabled: ~80%+.
- First-generation Black: higher error rate than parent-with-PhD
  Black.

Errors cluster in non-linear, intersectional ways. **Single-axis
error reporting (per-region OR per-gender) misses intersectional
error patterns.** For honest accuracy reporting, two-way (or
multi-way) cross-tabulation is needed.

### 5. Demographic confounding and spillover

A subtle but important point. Errors don't just affect the
specifically-misclassified groups — they *spill over* to inferences
about other groups via demographic correlations.

Example: 60% of disabled people misgendered are nonbinary (because
nonbinary people are both more likely to be disabled and more
likely to be misgendered). So studying disability-by-gender
introduces nonbinary-related error into the disability analysis,
*even though disability per se isn't the misclassification target*.

**Spillover means errors propagate through the data structure in
non-obvious ways.** Single-variable error analysis misses these
cascading effects.

### 6. The reference-population mismatch problem

Almost all name-based inference tools are trained on US-specific
reference data:
- Genderize.io: proprietary blackbox aggregation.
- predictrace: US Census + Social Security data.
- ethnicolor: Florida or North Carolina voter rolls.

But these tools are applied to:
- Global academic populations.
- Authors of papers from any country.
- Names from any cultural origin.

**The reference population is almost never the target population.**
Cultural consensus in the reference population doesn't transfer
cleanly. Tools systematically mis-perform on populations
underrepresented in training data.

For ws2: our target population is global authors of CS and Physics
papers 1970–2024. The reference populations of NamSor + Genderize
are different. **Our gender inference accuracy on our target
population is unknown without explicit validation on a sample of
that population.** This is the core motivation for Holst C3
gender-inference hand-validation we already committed to.

### 7. The five principles for responsible use

Lockhart proposes five principles. Let me unpack each with ws2
relevance:

**(1) Critical refusal.** Sometimes the right answer is "don't
infer." When inference can't be theoretically or ethically
justified for the research question, refuse. ws2 doesn't infer
race/ethnicity (excluded from desiderata for this exact reason);
we do infer gender, country, prestige. Each inference must be
justified by ws2's substantive question.

**(2) Align mechanism with method.** Name-based inference measures
*ascription* (how names are read). Use only for ascription-based
research questions. Don't use for identity-based questions
(self-perception, biological category, legal status). For ws2:
demographic plurality measures *the diversity of who is
producing/cited*, which is closer to ascription than identity. Our
mechanism (aggregate diversity at field-year level) aligns with
the ascription-based-method capacity.

**(3) Population-specific inference using domain expertise.** When
possible, train models on the specific population being studied.
Out of scope for ws2 — we'd need to train custom NamSor for
academic populations. Acknowledge as limitation.

**(4) Use subgroups with high accuracy.** Restrict claims to
subgroups where inference is accurate enough to support them. For
ws2: gender claims about Chinese-women subgroup may be unreliable
(43% error rate). Headline aggregate claims partially insulated;
disaggregated claims need per-subgroup-accuracy reporting.

**(5) Use only aggregate estimates, with bias-quantification on
target population.** This is the principle most directly aligned
with ws2. Aggregate estimates (e.g., "X% of authors are women in
year Y") are usable *if* we can quantify bias on a sample of the
target population. Our ORCID validation subsample is exactly this.
The validation lets us *correct* aggregate estimates by known
biases.

### 8. Information-theoretic limit and English-language databases

A subtle point worth understanding. Gender inference from English-
romanized names of speakers of tonal languages (Chinese, Vietnamese)
is fundamentally limited:

- 张伟 (Zhang Wei, masculine) and 张薇 (Zhang Wei, feminine) romanize
  to the same English string.
- Tonal information that signals gender is lost in romanization.
- No amount of better training fixes this — the information was
  destroyed at romanization.

This means gender inference for East-Asian names will always have
high error rates in English-language databases. Not an engineering
problem; an information-content problem.

For ws2: gender inference for non-Western, especially East-Asian,
authors will have systematic error rates regardless of which tool
we use. Acknowledge in Limitations.

### 9. Aggregate-vs-individual claim distinction

Lockhart emphasizes a critical distinction:

- **Individual-level claims** ("This author is a woman") — heavily
  affected by error rates; problematic when accuracy is low.
- **Aggregate-level claims** ("X% of authors in this field are
  women") — partially robust to individual errors via cancellation
  *if* errors are random.

But errors are *not* random — they're systematically biased
(toward men; against trans/nonbinary; against East-Asians). So
aggregate estimates are still biased, but the bias can be quantified
and corrected via sample validation.

**ws2 is entirely an aggregate-claims study.** All our demographic-
plurality metrics are field-year aggregates. This is in our favor
methodologically. But we still need bias-quantification on our
target population.

---

## Results — Three Levels

### Level 1: For a smart high-schooler

When researchers want to study gender or race patterns in big
datasets, they often "guess" demographic information from people's
names. Tools like Genderize.io look at names and predict whether
someone is a man or woman based on patterns from millions of
existing names.

This paper says these tools are wrong much more often than the
overall accuracy numbers suggest. The headline number is 4.6%
error — sounds small. But that's an average. For specific groups:
- Women are misclassified 3.5× more often than men.
- Chinese women are misclassified 43% of the time.
- Trans people 57%.
- Nonbinary people 100%.

The same problems exist for race/ethnicity guessing — Black,
Middle Eastern, and Filipino people are misclassified 55–80% of
the time.

Worse, the errors aren't fixable with better algorithms. The
fundamental issue is that names don't actually have a gender or
race — names *signal* these categories culturally, and the cultural
signal is ambiguous, varies by population, and gets lost in
translation (Chinese characters that signal gender don't signal it
in English transliteration).

The paper recommends: don't use these tools when you don't have to;
when you do, only use aggregate statistics (not individual labels);
always check accuracy on the specific population you're studying.

### Level 2: For a junior/senior undergraduate

Lockhart et al. survey 19,924 social science authors with a
self-report demographic survey, then compare their self-reports to
name-based inference outputs from four gender algorithms and four
race/ethnicity algorithms. Self-reports serve as the comparison
standard.

Key empirical findings:

- Genderize.io overall gender error: 4.6%.
- But subgroup decomposition shows dramatic heterogeneity: women
  misgendered 3.5× more than men; Chinese women 43%; trans people
  57%; nonbinary 100% (definitional).
- Race/ethnicity error rates: 14% overall; Black 65%; MENA 73%;
  Filipino 55%.

Theoretical contribution: name-based inference doesn't measure
identity; it measures cultural consensus. Names signal demographic
categories culturally, with consensus that varies by population
and context. There is no "ground truth" — the inference is
intrinsically ascription-based.

Methodological contribution: errors are *fundamentally not
eliminable* with more data or better algorithms. They reflect
information-theoretic limits (e.g., tonal information lost in
English romanization) and intersectional cultural complexity (e.g.,
naming patterns vary by class within race; spillover effects mean
errors in one group propagate to inferences about other groups
through demographic correlations).

Five principles for responsible use:
1. Critical refusal when inference isn't justified.
2. Align mechanism (cultural ascription) with method (name-based
   inference).
3. Population-specific inference using domain expertise.
4. Restrict claims to high-accuracy subgroups.
5. Aggregate estimates with bias-quantification on target population.

For ws2-relevant takeaways:
- The 4.6% headline accuracy is misleading; subgroup-specific
  accuracy is what matters.
- Our aggregate-divergence design (all metrics at field-year level)
  partially insulates from individual misclassification, but
  systematic biases persist in aggregates.
- Our ORCID validation subsample (Phase 0.1 §4) operationalizes
  Lockhart's principle 5.
- Our gender inference hand-validation (Holst C3 commitment) needs
  to test per-subgroup accuracy, not just overall.

### Level 3: For an early graduate student

The methodologically subtle observations worth deep engagement:

**(1) The cultural-consensus framing is theoretically load-bearing.**
Lockhart is not just saying "tools are inaccurate" (that would be
a calibration claim). They're saying "the thing tools are
*measuring* is itself constructed and heterogeneous." This is a
deeper claim:
- Conventional framing: tools approximate ground truth; better
  tools get closer.
- Lockhart framing: there is no ground truth; tools measure
  cultural consensus, which is intrinsically heterogeneous and
  varies by population.

For ws2's weight-by-confidence approach (Hofstra C4): we treat
inference confidence as approximating ground truth. Under
Lockhart's framing, the "confidence" is actually how strongly
cultural consensus assigns the name to a category, not how likely
it is that the inference is "correct." Subtle but important
reframing.

**(2) The information-theoretic limit argument is methodologically
binding.** Algorithms are approaching the limit beyond which more
data won't help. This means:
- Future "better" tools won't fix the issue.
- We can't wait for technology to improve.
- Acknowledgment in Limitations is mandatory, not optional.

For ws2: our pipeline is approximately as good as it'll ever be;
no future-tools-will-improve hand-waving applies.

**(3) Spillover effects propagate errors through data structure.**
Errors in one demographic dimension affect inferences about other
dimensions via correlations. Example: 60% of misgendered disabled
people are nonbinary. So a disability-x-gender analysis is
contaminated by nonbinary-misgendering, even though disability per
se isn't the target.

For ws2: when we report multiple demographic dimensions
simultaneously (gender + country + institution + prestige), errors
in one dimension propagate via correlations among dimensions.
Single-dimension error reporting misses the cascading.

**(4) The aggregate-vs-individual distinction is the methodological
escape hatch.** Lockhart's principle 5 explicitly: aggregate
estimates with bias-quantification on target population. ws2 is
entirely aggregate. So Lockhart's critique partially excuses us —
we don't make individual claims, only aggregate ones.

But aggregates are still biased (errors not random); the
bias-quantification step is non-negotiable.

**(5) The reference-population-mismatch problem is unfixable for
ws2's scope.** NamSor + Genderize are trained on populations
different from ws2's target (global academic authors 1970–2024).
We can't retrain — out of scope. So we acknowledge in Methods,
quantify on ORCID validation subsample, and report uncertainty
bounds.

The paper's limitations:

**(a) The 14% response rate for the survey raises concerns.**
Response bias may make the survey-respondent sample non-
representative of the broader academic population. Lockhart
acknowledges this. Our equivalent: ORCID validation subsample is
non-random (people with ORCID are systematically different from
people without).

**(b) The five principles are general; population-specific
operationalization requires further work.** ws2's task is to
operationalize Lockhart's principles for our specific population
and metrics — not just cite the paper.

**(c) Race/ethnicity is excluded from ws2 by design** (per
desiderata) so the more dramatic race-error findings don't directly
affect us. But the spillover argument means race-correlated errors
in gender inference might still operate through related variables
(country of origin).

---

## Connection to Our Project

### What ws2 takes from Lockhart 2023 (substantial)

**(1) Reframe weight-by-confidence as cultural-ascription
uncertainty, not ground-truth approximation.** Currently the
Hofstra C4 commitment frames weight-by-confidence as "uncertainty
propagation, not inference-quality fix." Lockhart sharpens: there
is no ground-truth-quality to fix. The inference is intrinsically
ascription-based. Methods paragraph framing should reflect this.

**(2) Strengthen Holst C3 gender-inference hand-validation with
per-subgroup design.** Currently our hand-validation samples 100
names. Lockhart's findings imply we should:
- Sample stratified by region (Anglo, East-Asian, South-Asian,
  Arabic-speaking, Slavic, other) — not just random sample.
- Report accuracy per stratum, not just overall.
- Pre-register per-subgroup thresholds (e.g., Chinese-women
  accuracy threshold may need to be lower than Anglo).

**(3) Per-intersectional-cell accuracy reporting for headline
demographic findings.** Single-axis (per-region) reporting misses
intersectional patterns. Where sample sizes allow, two-way
cross-tabulation in Limitations:
- Gender × region (e.g., Chinese-women specific accuracy).
- Gender × era (pre-1990 vs. post-1990 may have different
  inference quality).

**(4) Explicitly invoke Lockhart's principle 5 in Methods.** Our
ORCID validation subsample is the bias-quantification step. Methods
paragraph should explicitly cite Lockhart and frame our approach
as principle-5-compliant.

**(5) Ascription-vs-identity framing in Discussion.** When discussing
demographic plurality findings, frame as "diversity of how authors
are *culturally read*" not "diversity of authors' *identities*."
This is technically more accurate and aligns with Lockhart's
mechanism.

**(6) Information-theoretic-limit acknowledgment in Limitations.**
Don't claim "tools will improve"; acknowledge approaching the limit.
~3 sentences in Limitations.

**(7) Spillover-effect acknowledgment in Limitations.** Errors in
gender inference propagate to inferences about other demographic
dimensions via correlations. ~2 sentences in Limitations.

### What ws2 explicitly does NOT take from Lockhart

**(1) Race/ethnicity inference critique applies only partially.**
ws2 doesn't infer race/ethnicity directly (per desiderata
exclusion). The race-inference findings inform our country-of-origin
inference indirectly via correlation, but we don't use the same
race-inference tools.

**(2) Trans/nonbinary specific recommendations.** ws2's gender
inference is binary (NamSor outputs male/female/unknown). We don't
attempt to infer trans status. Lockhart's nonbinary-misgendered-100%
finding is a definitional consequence of binary inference, which
we acknowledge but don't address structurally.

**(3) Custom domain-expertise model training.** Lockhart's principle
3 (population-specific inference) is out of scope for ws2 — we'd
need to train custom NamSor for academic populations. Acknowledge
as deferral.

### Specific design implications for ws2

These translate to Phase 0.2 batch additions:

- **Reframe weight-by-confidence Methods paragraph** as
  cultural-ascription-uncertainty, not ground-truth-approximation.
  Refines Hofstra C4 commitment.
- **Strengthen Holst C3 gender hand-validation** with stratified
  sampling and per-subgroup accuracy reporting.
- **Add intersectional accuracy reporting** for demographic plurality
  headline findings.
- **Methods-section principle-5 alignment** with explicit Lockhart
  citation.
- **Discussion ascription-vs-identity framing.**
- **Limitations: information-theoretic-limit + spillover-effects
  acknowledgments.**

### How ws2 cites Lockhart in our methodology defense

Lockhart strengthens our defense for the demographic-plurality
side of ws2 (parallel to PAP 2024 + Holst + PAP 2025 strengthening
our defense for the canonical-concentration side). The cumulative
critique-chain framing:

- **Canonical concentration:** PAP 2024 (deductive) + Holst
  (data-quality) + PAP 2025 (controlled re-analysis) → ws2 metrics
  are inflation-immune by construction.
- **Demographic plurality:** Lockhart 2023 (cultural-consensus
  framing) → ws2 measures *ascription-based* aggregate plurality,
  with bias-quantification via ORCID validation, per Lockhart's
  principle 5.

The two parallel defense chains together demarcate what ws2 claims
and doesn't claim, on both metric channels.

---

## Key Quotes

For Methods / Discussion of the ws2 paper:

> "What name-based demographic imputation tools measure, then, is
> not the 'ground truth' of a person's or name's gender or race
> (which does not exist), but rather the cultural 'consensus
> estimates of how each name is gendered' or racialized." (p. 4 —
> the cultural-consensus framing.)

> "Our analyses reveal considerable heterogeneity in error rates
> for both gender and race imputation across demographic groups."
> (p. 6 — the headline empirical finding.)

> "Disparities in error rates are fundamental problems with the
> information content of names and the cultural construction of
> gendered and racialized groups. Thus they cannot be eliminated
> with more data or better statistics. They can, however, suggest
> substantively interesting insights about the world." (p. 3 — the
> information-theoretic-limit observation.)

> "The reference data population is almost never the target
> population. ... These populations have different demographic
> distributions." (p. 4 — the reference-population-mismatch
> problem.)

> "Use only aggregate estimates of demographics from names, and
> check accuracy and bias on the target population. Aggregate
> estimates ... do not require individual ascriptions, and we can
> quantify their biases by surveying a subpopulation." (p. 15 —
> principle 5, the methodological escape hatch.)

> "Methodologies unable to stand up to our conservative test of
> the problem are inappropriate for most applied uses, where a
> stricter approach requiring exact matching ... is critical for
> mitigating racial misrecognition and for overall quality of
> inference." (p. 18 — the methodological discipline statement.)

---

## Study Questions

**Warm-up (Level 1):**

1. **SQ1** — What does Lockhart mean when they say names measure
   "cultural consensus" rather than "ground truth"? How does this
   reframe what name-based inference tools actually do?

2. **SQ2** — The 4.6% overall gender error rate sounds small, but
   the paper argues it's misleading. Why? What specific subgroup
   error rates undermine the headline number?

**Intermediate (Level 2):**

3. **SQ3** — Why does Lockhart claim errors are "fundamentally not
   eliminable"? Walk through the information-theoretic-limit
   argument and the English-romanization example.

4. **SQ4** — What is "spillover" in Lockhart's analysis? Walk
   through the disability-misgendered-as-nonbinary example.
   What's the implication for multi-dimensional demographic
   analyses?

5. **SQ5** — Lockhart's principle 5 (aggregate estimates with
   bias-quantification) is the methodological escape hatch. Why
   does aggregate use partially insulate from individual error?
   What's the limit of this insulation?

**Advanced (Level 3):**

6. **SQ6** — The reference-population-mismatch problem: ws2's
   target population (global academic authors 1970–2024) differs
   from NamSor + Genderize's training populations. What specific
   bias patterns do we anticipate, and how does our ORCID
   validation subsample help?

7. **SQ7** — Lockhart distinguishes ascription from identity. ws2
   measures demographic plurality as a field-year aggregate. Is
   our claim about *ascribed-diversity* or *identity-diversity*?
   Does this matter for our substantive interpretation?

8. **SQ8** — The 14% survey response rate raises selection-bias
   concerns. Lockhart acknowledges respondent population may not
   represent broader population. What's the analogous concern for
   ws2's ORCID validation subsample, and how should we address?

---

## Challenge Corner

**C1:** ws2 currently commits to weight-by-confidence handling
(Hofstra C4) and overall + per-region accuracy reporting.
Lockhart's heterogeneity findings imply this is insufficient. Per-
intersectional-cell reporting (e.g., Chinese-women specific
accuracy) is needed for honest accuracy-claim.

(a) For ws2's headline demographic plurality findings, what specific
intersectional cells should we report accuracy for? Candidates:
gender × region (Chinese-women, Vietnamese-women, etc.); gender ×
era (pre-1990 vs. post-1990 inference quality); gender × institution
type (industry vs. academic name conventions).

(b) Sample-size constraints: Lockhart's intersectional cells with
< 10 are grayed out. ws2 may have similar small-sample issues for
intersectional cells. How do we handle?

**C2:** Lockhart's principle 5 (aggregate estimates with
bias-quantification) is the methodological escape hatch ws2 leans
on. But the bias-quantification step requires a sample of the
target population. Our ORCID validation subsample is non-random
(people with ORCID are systematically different).

(a) What systematic differences should we anticipate between
ORCID-having and ORCID-lacking authors in our population (CS +
Physics 1970–2024)?

(b) Does the non-random ORCID subsample limit our ability to
quantify bias on the full target population? If so, how should
Methods/Limitations handle?

**C3:** The ascription-vs-identity distinction is theoretically
load-bearing for ws2's substantive interpretation. ws2 measures
demographic plurality as field-year aggregates of *inferred-from-
name* demographic features.

(a) Are our claims about ascribed-diversity (how authors are
culturally read) or identity-diversity (who authors are)? For
the central question (decoupling of demographic from semantic
plurality), does this distinction matter?

(b) How should Discussion frame demographic plurality findings —
as "diversity of who is culturally recognized" or "diversity of
who is producing"?

**C4:** Lockhart's information-theoretic-limit argument means
future-tools-won't-fix-this. ws2's pipeline (NamSor + Genderize)
is approximately as good as it'll get. This is a hard methodological
constraint.

(a) Do we acknowledge this in Limitations as a hard constraint, or
as a "current limitation pending future improvements"? The honest
answer per Lockhart is the former.

(b) Are there areas where the limit is *not* binding for ws2 —
e.g., where domain-expertise-trained models could help (Lockhart's
principle 3)? Worth flagging as deferred future work?

**C5:** The spillover-effects observation: errors in one
demographic dimension propagate to inferences about other
dimensions via correlations. ws2 uses 7+ demographic dimensions
(gender, country of current affiliation, country of earliest
affiliation, institution type, prestige tier, career stage,
training-institution concentration).

(a) Where do we anticipate spillover concerns? Candidates: gender ×
country (Chinese-women misgendering propagates to country-of-origin
inferences via name-language correlation); gender × institution
(Asian-institution employees may have higher misgendering rates,
contaminating institution-level analyses).

(b) Should our Methods explicitly enumerate anticipated spillover
patterns? Or acknowledge in aggregate ("spillover is a known
concern; specific patterns will be addressed in sensitivity
analyses")?

---

## Synthesis Pointers (for `synthesis.md`)

1. **Lockhart 2023 is the critique-chain anchor for the demographic
   plurality side of ws2.** Parallel to PAP 2024 + Holst + PAP 2025
   for the canonical concentration side. ws2's defense framing now
   has parallel chains for both metric channels.

2. **Cultural-consensus framing reframes weight-by-confidence**
   from "approximating ground truth" to "reporting ascription-
   based uncertainty." Methods paragraph refinement.

3. **Per-intersectional-cell accuracy reporting** is mandatory for
   honest accuracy-claim. Single-axis reporting misses heterogeneous
   patterns.

4. **Holst C3 gender hand-validation needs stratified-sampling
   refinement** to test per-subgroup accuracy patterns. Existing
   commitment to be refined.

5. **Lockhart's principle 5 is the methodological escape hatch
   ws2 leans on.** Aggregate estimates + bias-quantification on
   target population. Our ORCID validation subsample operationalizes
   this. Methods explicit citation.

6. **Information-theoretic-limit acknowledgment in Limitations is
   non-negotiable.** Don't hand-wave about future improvements;
   acknowledge the limit.

7. **Spillover-effects acknowledgment** for multi-dimensional
   demographic analyses. ~2 sentences in Limitations.

8. **Race/ethnicity exclusion from ws2 (per desiderata) is
   methodologically vindicated** by Lockhart's race-inference error
   findings. The exclusion was the right call.

---

## Discussion Notes

(Filled during collaborative review session. Blank until that
session happens.)

### On C1 — per-intersectional-cell accuracy reporting

(Pending.)

### On C2 — ORCID subsample bias-quantification limits

(Pending.)

### On C3 — ascription-vs-identity framing for ws2

(Pending.)

### On C4 — information-theoretic-limit acknowledgment

(Pending.)

### On C5 — spillover effects in ws2's multi-dimensional design

(Pending.)

---

## Study Question Walkthroughs

### SQ1 — Cultural consensus vs. ground truth

(Pending.)

### SQ2 — Why 4.6% headline accuracy is misleading

(Pending.)

### SQ3 — Information-theoretic-limit argument

(Pending.)

### SQ4 — Spillover effects example

(Pending.)

### SQ5 — Aggregate-estimate insulation limits

(Pending.)

### SQ6 — Reference-population mismatch for ws2

(Pending.)

### SQ7 — Ascription-vs-identity for ws2's claim

(Pending.)

### SQ8 — ORCID subsample selection bias

(Pending.)
