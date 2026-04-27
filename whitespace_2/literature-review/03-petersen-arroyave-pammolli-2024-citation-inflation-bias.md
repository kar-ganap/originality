# 03 — The disruption index is biased by citation inflation

**Authors:** Alexander Michael Petersen, Felber Arroyave, Fabio Pammolli
**Venue:** *Quantitative Science Studies* 5(4), 936–953 (2024)
**PDF:** `literature-review/03-petersen-arroyave-pammolli-2024-citation-inflation-bias.pdf` (gitignored)
**SI:** None (QSS paper has methodology in body; synthetic networks at Dryad)
**DOI:** 10.1162/qss_a_00333

---

## Background

This paper formalizes the citation-inflation critique of the CD index
that we've been treating as known background since our PLF SQ7
walkthrough. Petersen-Arroyave-Pammolli 2024 (henceforth PAP) is the
direct methodological response to Park-Leahey-Funk 2023's *Nature*
cover paper, arguing that the documented disruption decline is
substantially an artifact of citation inflation rather than a real
shift in scientific dynamics.

Per the lit-review-scope memory, this is a **Tier 1 positioning read
(~2 hrs)** rather than a deep collaborative-walkthrough paper. The
substantive content largely overlaps with what we already engaged via
PLF SQ7 (the accidental-Type-2 mechanism, the failure of PLF's
normalization variants to address numerator inflation). PAP's
contribution is to formalize the critique through three complementary
lines (deductive, empirical, computational) and to provide synthetic
citation networks publicly that can be used to test alternative
metrics for similar biases.

ws2's relationship to PAP: this paper *justifies* our CD-index
exclusion that's already in desiderata. We cite PAP in our Methods
paragraph on the CD-index decision and in our Discussion as the
formal basis for the critique chain we engage under PLF (c-prime).
We do not adopt any methodology from PAP — they're attacking CD-index,
not proposing replacement metrics relevant to our canonical-
concentration measurement.

The most ws2-relevant new content:
- The *deductive* derivation that CD_p = CD_p^nok / (1 + R_k) where
  R_k grows with citation network density — this is the cleanest
  mathematical statement of the bias mechanism.
- The *team-size finding* (b_k = +0.0039, positive correlation
  between team size and CD_5 controlling for r_p) which contradicts
  Wu-Wang-Evans 2019's negative-relationship finding. **This is the
  seed of Petersen-Arroyave-Pammolli 2025 (paper 04 in our reading
  list), which is the deeper close-read on team-size critique.**
- The *publicly available synthetic citation networks* at Dryad —
  could in principle be used to stress-test ws2's own canonical-
  concentration metrics for similar biases. Stage 3 candidate.

---

## Key Ideas

### 1. Three lines of critique

PAP structures its argument through three complementary methods:

1. **Deductive critique (Section 2):** mathematical derivation of
   why CD converges to 0 under citation inflation, independent of
   any empirical analysis.
2. **Empirical critique (Section 3):** MAG dataset analysis (~30M
   articles, 1945–2012) showing that CD_5(t) decline tracks R_k(t)
   growth tightly (R² = 0.96).
3. **Computational critique (Section 4):** synthetic citation
   network simulations where citation inflation is "turned on/off"
   parametrically, demonstrating that CI alone produces the observed
   decline pattern in the absence of any underlying disruption
   change.

Each line independently supports the conclusion; together they
constitute a strong methodological critique. PLF only had the
empirical strand and partial robustness; PAP adds the deductive
foundation and the controlled-simulation evidence.

### 2. The deductive reformulation: CD = CD^nok / (1 + R_k)

The clean mathematical statement of the bias. PAP show that:

CD_p = (N_i − N_j) / (N_i + N_j + N_k)

can be rewritten as:

CD_p = [(N_i − N_j) / (N_i + N_j)] / [1 + N_k/(N_i + N_j)] = CD_p^nok / (1 + R_k)

where:
- CD_p^nok ∈ [−1, 1] is *intensive* (bounded; the Bornmann variant
  PLF actually used).
- R_k = N_k / (N_i + N_j) is *extensive* (unbounded; grows with
  citation network density).

**As R_k → ∞, CD_p → 0 mechanically, independent of CD_p^nok.**

This is the cleanest formulation of the bias we've seen. The PLF
SQ7 walkthrough framed the issue as "the normalizations modify the
denominator but leave the numerator unchanged"; PAP's reformulation
shows that the decay of CD_p is *fundamentally* about R_k → ∞, and
no normalization that preserves CD_p^nok structure can avoid this.

### 3. The R_k inflation mechanism — empirical

R_k grows because:
1. Reference list length r_p has grown ~2.6-fold over 50 years
   (mean 9 → 23 references per article).
2. Highly cited papers accrue citations at rates that scale with
   network density.
3. Together, these mean that any random paper p has more references
   that are themselves highly cited → more N_k citations of those
   predecessors → higher R_k.

The empirical R²=0.96 between average r(t) and R_k(t) in MAG
(Figure 2e) is the load-bearing observation: **the decline in
CD_5(t) is essentially entirely explained by the growth in R_k(t),
which is essentially entirely explained by the growth in r(t).**
There is no residual signal attributable to actual changes in
disruption-vs-consolidation patterns once R_k is accounted for.

### 4. The synthetic-network simulations

PAP construct synthetic citation networks under six scenarios that
parametrically vary:
- Whether citation inflation is "on" (g_r = 0.018, empirical rate)
  or "off" (g_r = 0).
- Whether a "redirection mechanism" β(t) (capturing strategic
  citation behavior — citing references-of-references via web
  hyperlink trails, etc.) is constant or growing.

Key results:
- **Scenarios 1, 2 (no CI):** CD_5(t) systematically *increases*
  over time. The redirection mechanism (β > 0) doesn't produce
  decline by itself.
- **Scenario 3 (CI on, β growing):** CD_5(t) reproduces the PLF
  empirical decline pattern. *CI alone is sufficient to generate
  the decline.*
- **Scenarios 5, 6 (hypothetical reference-length cap):** CD_5(t)
  reverses to *increasing* immediately after the cap is imposed,
  even though no underlying disruption process changed.

This is the strongest result in the paper. It's a controlled
demonstration that the empirical PLF decline can be entirely
generated by citation inflation, with no disruption-process change
required.

### 5. The team-size finding (seed of Petersen 2025)

In a multivariate regression (Table 1, full model):
- b_k = +0.00394 (team size, ln k_p) — *positive* coefficient
- b_r = −0.0253 (reference list length, ln r_p) — negative, ~6×
  larger
- Year FE included

The +b_k coefficient is small but statistically significant
(p<0.001). It is *opposite in sign* to Wu-Wang-Evans 2019's
headline finding that "small teams disrupt and large teams develop."

PAP frame this as a smoking gun: WWE 2019's negative correlation is
likely an artifact of omitted variable bias (not controlling for
citation inflation), since CD and team size both inflate over time,
producing a spurious negative correlation if year is the only time
control.

This finding is the seed of **Petersen-Arroyave-Pammolli 2025**
(paper 04 in our reading list — the deeper close-read on team-size
re-analysis). PAP 2024 introduces the result; PAP 2025 develops it
into a full re-analysis of WWE 2019 with implications for our
Test II team-size control and Test IV team-diversity × novelty
setup.

### 6. The reference list length is the main driver

PAP's analysis explicitly identifies r_p (reference list length) as
the primary driver of citation inflation in CD_5. Two empirical
moves:
- The negative b_r coefficient (−0.0253) in the multivariate
  regression: a paper with twice as many references has CD_5 that
  is 0.0175 lower on average (b_r × ln(2) ≈ −0.017).
- The R²=0.96 between r(t) and R_k(t) confirms that r(t) growth is
  the dominant mechanism feeding R_k inflation.

This sharpens our PLF SQ7 conclusion. The accidental-Type-2
mechanism (longer reference lists → more accidental Type-2 citers)
is empirically the dominant inflation pathway, not just one of
several.

### 7. Policy implications: capped reference lists

PAP propose that journals could cap reference list lengths
("capping reference lists commensurate with the different types of
articles they publish") as a way to mitigate citation inflation in
disruption metrics. The synthetic-network simulations (Scenarios
5, 6) show this would reverse CD_5(t) decline.

This is offered as a hypothetical policy intervention. ws2 has no
direct stake in the policy implication, but it's worth noting that
PAP's framing positions disruption-metric reform as a science-policy
issue, not just a measurement issue.

---

## Results — Three Levels

### Level 1: For a smart high-schooler

The CD index measures whether a paper "disrupts" or "consolidates"
existing scientific knowledge by looking at citation patterns.
Park-Leahey-Funk 2023 used it to claim that science is becoming
less disruptive over time. This paper says: that decline isn't
real — it's a measurement artifact.

The argument: papers today cite many more references than papers
from the 1960s did (about 23 references vs. 9). When papers cite
more references, the math of the CD index forces it to drift toward
zero, regardless of whether the underlying science is more or less
disruptive. So when you see "CD index declining over time," you're
mostly seeing "papers have longer reference lists now," not "papers
are less disruptive."

To prove this, the authors build synthetic citation networks where
they control everything. They show that:
- When they "turn off" citation inflation, the CD index actually
  INCREASES over time.
- When they "turn it on," they reproduce Park-Leahey-Funk's pattern.
- When they hypothetically cap reference list lengths, the apparent
  disruption decline reverses.

The conclusion: the CD index is unreliable for cross-time analysis.
What looked like a fundamental shift in science was largely an
artifact of how the metric is computed.

### Level 2: For a junior/senior undergraduate

The paper formalizes the citation-inflation critique through three
complementary methods:

**Deductive:** PAP show CD_p = CD_p^nok / (1 + R_k) where R_k =
N_k/(N_i + N_j) is an extensive quantity that grows with citation
network density. As R_k → ∞ (which happens with citation inflation),
CD_p → 0 regardless of the bounded intensive quantity CD_p^nok.

**Empirical:** Using the MAG dataset (~30M articles, 1945–2012),
they find R²=0.96 between average reference list length r(t) and
average R_k(t). The decline in CD_5(t) is essentially entirely
explained by the growth in R_k(t), which is essentially entirely
explained by the growth in r(t).

**Computational:** They construct synthetic citation networks under
six scenarios. With citation inflation "on" (g_r = 0.018, the
empirical rate), CD_5(t) declines as in PLF. With CI "off" (g_r = 0),
CD_5(t) actually increases. With a hypothetical reference-length cap
imposed mid-simulation, the trend reverses immediately. This
parametric demonstration is the cleanest evidence that CI is the
dominant cause.

A secondary but striking finding: in their multivariate regression
with year FE, team size and CD_5 are *positively* correlated (b_k =
+0.0039). This contradicts Wu-Wang-Evans 2019's "small teams
disrupt" finding. PAP argue WWE's result is omitted-variable bias —
they didn't control for citation inflation, and CD and team size
both inflate over time. This is the seed of the deeper team-size
critique in PAP 2025.

The paper also references parallel critiques: Macher et al. 2024
(missing patent citations correction → CD decline disappears for
patents); Bentley et al. 2023 (weighted CD-index → reverses to
increasing trend); Holst et al. 2024 (dataset artifacts in
zero-reference and uncited papers).

### Level 3: For an early graduate student

The paper's three-line critique structure (deductive + empirical +
computational) is methodologically strong. The deductive line is
particularly load-bearing: by reformulating CD_p = CD_p^nok / (1 +
R_k), PAP show that the decline of CD_p is *fundamentally* about
R_k → ∞, and no normalization that preserves CD_p^nok structure can
avoid this. PLF's normalization variants (DI^nok, paper-normalized,
field × year normalized) all preserve CD_p^nok structure, so they
all fail to address the underlying issue.

Three subtle methodological observations:

**(1) The R²=0.96 is suspicious in a useful direction.** If R_k(t)
explained 96% of the variance in CD_5(t) but the underlying
disruption process was actually changing, we'd expect to see *less*
explanatory power for R_k(t) over time (real disruption changes
would introduce variance R_k can't capture). The fact that R_k(t)
explains nearly all the variance suggests there's no residual real
disruption change to explain.

**(2) The synthetic-network simulations are the cleanest causal
evidence.** Empirical analyses can always be challenged by
"unobserved confounders." Synthetic networks remove this concern
entirely — by construction, the only variables that change between
scenarios are the parameters PAP manipulate (g_r and β). The
Scenario 3 vs. 1, 2 comparison is essentially a controlled
experiment showing CI alone produces the decline.

**(3) The team-size finding (b_k > 0) is methodologically important
beyond its substantive implication.** The standard scientometrics
narrative is that small teams disrupt (WWE 2019), large teams
develop. PAP show this relationship reverses sign once you control
for citation inflation. This is a general lesson about
scientometrics: any finding that involves both citation-network
metrics AND time AND not controlling for citation inflation is
suspect.

The paper's limitations:

**(a) The proposed alternative is a policy intervention, not a
metric replacement.** PAP suggest journals cap reference list
lengths. They don't propose a CD-index variant that's inflation-
robust. This is appropriate to their argument (the issue is
structural to the CD index family) but leaves the literature
without a clean replacement.

**(b) The Fisher-Tippett distribution proposal in the conclusion
is suggestive but underdeveloped.** PAP note that CD_5 distributions
become time-invariant in scenarios where CI is removed, suggesting
this could be the basis for a time-invariant disruption measure
("rescaling values according to the location and scale parameters").
This idea is sketched, not developed. Future work.

**(c) The empirical analysis is on MAG, not WoS.** PLF used WoS;
PAP use MAG. Both have their own coverage issues (Chu-Evans C3
substrate-difference walkthrough applies). The cross-database
robustness PLF claimed (and Reviewer #3 questioned) is less well-
addressed in PAP, which uses a single database.

---

## Connection to Our Project

### What ws2 takes from PAP

**(1) Formal justification for our CD-index exclusion.** We can
cite PAP 2024 in our Methods paragraph on the CD-index decision as
the formal mathematical basis for the critique. Specifically: cite
the deductive derivation CD_p = CD_p^nok / (1 + R_k) as the
underlying reason CD-index is unsuitable for cross-temporal
analysis.

**(2) The R²=0.96 empirical observation as evidence strength.**
When we cite the Petersen-Holst critique chain in Discussion, the
R²=0.96 between r(t) and R_k(t) gives us a quantitative anchor for
how dominant the inflation effect is. Useful for the (c-prime)
inflation-immune-evidence framing.

**(3) Stage 3 candidate: stress-test our metrics on synthetic
networks.** PAP make synthetic citation networks publicly available
at Dryad. We could in principle compute Spearman top-50 and citation
Gini on these synthetic networks (where CI is parametrically
controlled) to verify our metrics are robust to CI. **Stage 3
candidate, low priority** — we already argue rank-invariance
analytically; empirical demonstration on PAP's networks would be
nice-to-have, not load-bearing.

**(4) Pointer to PAP 2025 (paper 04) for team-size.** The b_k > 0
finding here previews the deeper team-size re-analysis we'll engage
in PAP 2025. Expect implications for our Test II team-size control
and Test IV team-diversity × novelty setup.

### What ws2 explicitly does NOT take from PAP

**(1) Any specific replacement metric.** PAP doesn't propose one.
The Fisher-Tippett distribution suggestion is underdeveloped.

**(2) The policy-intervention framing.** Reference-list capping is
a science-policy proposal that's out of scope for ws2.

**(3) The MAG-vs-WoS substrate question.** We use OpenAlex; PAP and
PLF use different substrates. Our C3/SQ10 substrate-acknowledgment
already covers this.

### Specific design implications for ws2

- **Reaffirms CD-index exclusion in desiderata.** Already locked.
  PAP read confirms the wisdom.
- **Methods-section paragraph on CD-index decision (already in
  Phase 0.2 batch).** Now has stronger formal citation support.
  Specifically: "Per Petersen-Arroyave-Pammolli 2024's deductive
  derivation that CD_p = CD_p^nok / (1 + R_k) where R_k grows with
  citation network density, no CD-index variant preserving the
  CD_p^nok structure can be inflation-robust. ws2 therefore excludes
  CD-index from primary canonical metrics."
- **Anticipate PAP 2025 carefully** for team-size implications. The
  WWE 2019 → PAP 2025 critique chain may affect our Test II team-
  size control specification.

---

## Key Quotes

For Methods / Discussion of the ws2 paper:

> "CD_p systematically declines for the simple reason that CD
> features a numerator that is bounded and a denominator that is
> unbounded. ... The term R_k in the denominator is susceptible to
> CI, and continues to inflate according to two mechanisms: (a) It
> grows proportional to the reference list length; and (b) it is
> highly sensitive to highly cited papers, which in the present day
> can readily achieve hundreds of citations within 5 years, thereby
> causing R_k to explode and CD to converge to 0 over time." (p. 940
> — the deductive critique core.)

> "While our results are based upon a single representation of the
> scientific citation network ... the implications are generalizable
> to other citation networks featuring CI, such as patent citation
> networks." (p. 941 — the substrate-generalizability claim.)

> "Comparison of [Scenarios 1, 2] indicates that the redirection
> mechanism capturing shifting patterns of scholarly citation
> behavior is the weaker of the two mechanisms we analyzed. ...
> [Scenario 3 with CI on] reproduces both the magnitude and rate of
> the decreasing trend in CD(t) observed for real citation networks.
> ... These results demonstrate the acute effect of reference list
> CI on CD." (p. 947 — the controlled-simulation result.)

> "The estimated coefficient for publication year in Leahey et al.
> (2023) is not statistically significant ... which is inconsistent
> with the main result reported by the same authors in Park et al.
> (2023). Hence ... these inconsistencies merit investigation by way
> of a mechanistic citation network model where confounding sources
> of variation can be fully controlled." (p. 943 — the
> internal-inconsistency-in-PLF-team observation.)

> "This work, despite the reasonable logic behind the definition of
> CD, we show that its numerator (which captures the difference
> between disruptive and consolidating links, N_i − N_j) is
> systematically susceptible to becoming overwhelmed by the
> extensive quantity R_k ~ r(t) appearing in the denominator." (p.
> 949 — the discussion-section summary statement.)

---

## Study Questions

(Lighter set than other Tier 1 papers per the positioning-read scope.)

**Warm-up (Level 1):**

1. **SQ1** — What is R_k in the CD index, and why is it called
   "extensive" rather than "intensive"? What does this distinction
   mean for the metric's behavior over time?

2. **SQ2** — The paper structures its critique through three lines
   (deductive, empirical, computational). What does each line
   contribute that the others don't?

**Intermediate (Level 2):**

3. **SQ3** — The R²=0.96 between r(t) and R_k(t) (Figure 2e) is the
   load-bearing empirical observation. Why is this specific R²
   value methodologically significant — what would a lower R²
   imply, and what does this R² imply about residual disruption
   change?

4. **SQ4** — The synthetic-network Scenarios 1, 2 (no CI) show
   CD_5(t) *increasing* over time, not just stable. What does this
   surprising result imply about the underlying citation dynamics
   when CI is absent?

**Advanced (Level 3):**

5. **SQ5** — PAP's reformulation CD_p = CD_p^nok / (1 + R_k) shows
   that CD decay is fundamentally about R_k → ∞. PLF's
   normalization variants (DI^nok, paper-normalized, field × year
   normalized) all preserve CD_p^nok structure. Why does PAP's
   reformulation imply that no such variant can avoid the bias,
   and what would a structurally different metric have to look
   like to be inflation-robust?

6. **SQ6** — The team-size finding (b_k = +0.0039, positive)
   contradicts Wu-Wang-Evans 2019. PAP argue WWE's negative
   correlation is omitted-variable bias from not controlling for
   citation inflation. What's the general lesson for scientometrics
   from this — what other findings in the literature might be
   suspect for similar reasons?

7. **SQ7** — The Fisher-Tippett distribution proposal in the
   conclusion is sketched but underdeveloped. What would a fully
   developed version look like, and would it be a viable
   replacement metric for cross-temporal CD analysis? Why might
   PAP have chosen not to develop it further in this paper?

---

## Challenge Corner

(Tighter set than other Tier 1 papers.)

**C1:** PAP's deductive reformulation CD_p = CD_p^nok / (1 + R_k)
is the cleanest mathematical statement of the bias. Walk through
why this rewriting is non-trivial — specifically, why it surfaces
the R_k → ∞ mechanism in a way that the original formula CD_p =
(N_i − N_j) / (N_i + N_j + N_k) doesn't make obvious. What does
this teach us about *how* to spot inflation vulnerabilities in
network metrics?

**C2:** The synthetic-network simulations (Scenarios 1–6) are
PAP's strongest evidence. But synthetic networks are by construction
models — they assume specific link-formation rules (preferential
attachment, redirection mechanism, exponential growth in r(t) and
n(t)). Two sub-questions:

(a) How sensitive are PAP's conclusions to the specific link-
formation rules they choose? Could a different model (e.g., one
with topical clustering or with explicit innovation events) produce
different patterns?

(b) For ws2: PAP's networks are publicly available at Dryad. We've
listed stress-testing our metrics on them as a Stage 3 candidate.
What specifically would we test, and what would we learn?

**C3:** The team-size finding (b_k > 0) is methodologically
striking but presented briefly here (the deeper analysis is in PAP
2025). What's the structure of the WWE 2019 → PAP 2024 → PAP 2025
critique chain, and how does each step tighten the case? How
should we anticipate engaging PAP 2025 differently from PAP 2024
given that 2025 is a deeper close-read?

**C4:** PAP's policy proposal (capping reference list lengths)
treats citation inflation as a problem to be fixed structurally.
ws2 takes the opposite stance: we accept citation inflation as a
feature of the data and design metrics that are *immune* to it
(rank-invariance for Spearman; distribution-shape for Gini). Two
sub-questions:

(a) Are there situations where structural fixes (PAP) are preferable
to immunity-by-design (ws2)? What's the substantive trade-off?

(b) For ws2 Discussion: should we engage PAP's policy proposal at
all? It's adjacent to our scope but not load-bearing.

**C5:** PAP analyze MAG; PLF analyzed WoS + 5 others; ws2 uses
OpenAlex. The C3/SQ10 substrate-acknowledgment from PLF reading
applies here too. But there's a specific question: PAP's synthetic
networks are *substrate-agnostic* (they're synthetic). Does this
mean PAP's conclusions are stronger than PLF's despite using only
one empirical substrate? Or does the synthetic-network approach
have its own limitations that make substrate-diversity still
important?

---

## Synthesis Pointers (for `synthesis.md`)

1. **Formal mathematical basis for CD-index exclusion in ws2
   desiderata.** PAP's deductive reformulation CD_p = CD_p^nok /
   (1 + R_k) is the clean statement. Cite in Methods paragraph on
   CD-index decision.

2. **R²=0.96 between r(t) and R_k(t)** is the quantitative anchor
   for the inflation-magnitude argument. Useful in Discussion when
   defending (c-prime) inflation-immune-evidence framing.

3. **PAP-style observational-data diagnostics for inflation
   vulnerability (Phase 0.2 batch commitment, 2026-04-26).** PAP
   offers three diagnostics that don't require synthetic networks:
   (a) algebraic decomposition test (metric-level, structural — ws2's
   metrics pass by construction); (b) stationarity test on per-year
   metric distributions; (c) correlation-with-r(t) test. These are
   observational-data diagnostics computable on our actual data.
   Pre-registered interpretive thresholds: |corr| < 0.3 = robust;
   0.3-0.7 = investigate; ≥ 0.7 = trigger synthetic-network stress-
   test. Captured as new Phase 0.2 batch item alongside the existing
   C2(b) OpenAlex coverage commitment.

3a. **Synthetic citation networks at Dryad** remain as Stage 3
   back-pocket for stress-testing ws2's canonical-concentration
   metrics if the observational-data diagnostics (#3 above) surface
   concerning patterns. Lower priority than direct observational
   diagnostics.

4. **Team-size finding (b_k > 0) seeds PAP 2025.** Anticipate
   engaging PAP 2025 (paper 04) carefully for Test II team-size
   control implications.

5. **Substrate-difference acknowledgment applies to PAP too.** PAP
   uses MAG; ws2 uses OpenAlex. Same C3/SQ10 substrate caveat
   applies; no new commitment.

6. **PAP's policy proposal (reference-list capping) is out of ws2
   scope** but illustrates an alternative response strategy
   (structural fix vs. immunity-by-design). Worth a brief mention
   in Discussion if we're engaging PAP at length, otherwise skip.

---

## Discussion Notes

(Mostly Pending — light engagement per positioning-read scope.)

### On C1 — deductive reformulation and inflation-spotting lesson

(Pending.)

### On C2 — synthetic-network sensitivity and Stage 3 stress-test

(Pending.)

### On C3 — WWE → PAP 2024 → PAP 2025 critique chain structure

(Pending — will engage in PAP 2025 review.)

### On C4 — structural fix vs. immunity-by-design tradeoffs

(Pending.)

### On C5 — substrate-diversity vs. synthetic-network argument strength

(Pending.)

---

## Study Question Walkthroughs

(Mostly skipped per positioning-read scope. SQ4-SQ6 are the most
ws2-relevant if any are walked through collaboratively.)

### SQ1 — R_k as extensive vs. intensive

(Pending.)

### SQ2 — Three-line critique structure contributions

(Pending.)

### SQ3 — R²=0.96 methodological significance

(Pending.)

### SQ4 — Why CD_5 increases without CI

(Pending.)

### SQ5 — Why no CD-index variant can be inflation-robust

(Pending.)

### SQ6 — Omitted-variable bias lesson for scientometrics

(Pending.)

### SQ7 — Fisher-Tippett distribution proposal viability

(Pending.)
