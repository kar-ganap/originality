# 06 — The Diversity–Innovation Paradox in Science

**Authors:** Bas Hofstra, Vivek V. Kulkarni, Sebastian Munoz-Najar Galvez, Bryan He, Dan Jurafsky, Daniel A. McFarland (Stanford University)
**Venue:** PNAS 117(17), 9284–9291, April 28, 2020
**DOI:** [10.1073/pnas.1915378117](https://doi.org/10.1073/pnas.1915378117)
**PDF (local):** `literature-review/06-hofstra-2020.pdf`
**SI (local):** `literature-review/06-hofstra-2020-SI.pdf` (32 pages; methodology lives here, read closely)

---

## Background

Prior diversity-innovation scholarship has two findings that don't fit together:
(a) demographic diversity predicts novel outputs at team and organizational
levels (Page 2007; Nielsen et al. 2017; Bell et al. 2011; de Vaan-Stark-Vedres
2015), and (b) underrepresented groups in organizations have worse career
outcomes than majorities holding nominal productivity constant (Moss-Racusin
et al. 2012; Ding-Murray-Stuart 2006; West et al. 2013; Rivera 2017; Bendels
et al. 2018; Clauset-Arbesman-Larremore 2015). The tension is called "the
diversity paradox." The Hofstra et al. contribution is to test whether this
paradox holds *in science* by linking a near-population of US PhDs to their
subsequent careers, and — crucially — to measure innovation *textually* via
concept recombination rather than via citation counts.

The paper sits at the intersection of three literatures: scientometric
measurement of innovation (Uzzi-Mukherjee-Stringer 2013; Foster-Rzhetsky-Evans
2015; Wang-Song-Barabási 2013; Iacopini et al. 2018), the sociology of
stratification in science (Clauset et al. 2015; Burris 2004), and name-based
demographic inference at scale (Sood-Laohaprapanon 2018; Sood 2017).

---

## Key Ideas

### 1. Innovation as novel conceptual recombination

Innovation is operationalized as the *introduction of new pairwise linkages
between scientific concepts* in dissertation abstracts. This is the paper's
core methodological move. It follows the Kuhnian framing that scientific
development is "the constellation of facts, theories, and methods collected
in current texts" (Kuhn 1962), and that new science consists of new
combinations of existing concepts (Weitzman 1998; Uzzi et al. 2013).

**Why not citations?** Two reasons the paper is explicit about: citation
metrics privilege some fields (journal-indexing asymmetries) and citation
behaviors are heterogeneous ("the plethora of reasons as to why scholars cite
other work"). Concept-recombination measurement avoids both issues.

**Why not keywords?** Keywords are curator-assigned and often classify a
paper's *topic* rather than its *contributions*. The paper argues keywords
conflate "what field the paper is in" with "what the paper actually
contributes" — a problem for innovation measurement.

### 2. Structural Topic Modeling for concept extraction

Concepts are extracted via Structural Topic Models (STM; Roberts et al. 2014)
fit on the ~1.2M abstracts with graduation year as a topic-prevalence
covariate. STM is a latent-Dirichlet-allocation variant that allows topic
proportions to depend on document metadata. They fit K∈[50,1000] in
increments of 50 (100 beyond K=600) and find that coherence and exclusivity
plateau at K∈[400,600]. They use K=500 as main results.

**FREX weighting.** Concepts are identified as the top-500 FRequency-
EXclusivity weighted terms per topic. FREX (Bischof & Airoldi 2012) compounds
how frequently a term appears in a topic with how exclusive it is to that
topic. Three weighting schemes tested: 75/25 (frequency-dominant), 50/50
(balanced, main), 25/75 (exclusivity-dominant). Main results use 50/50.

**Preprocessing** (SI, p. 6): strip standalone numbers, punctuation, English
stopwords, special characters; keep numbers in chemical formulae (e.g., H2S);
Snowball stemming; drop singleton tokens; extract n-grams via El-Kishky et
al. 2014's scalable phrase-mining.

### 3. Novelty = count of first-introduced concept pairs, filtered by PMI

For each thesis, the **novelty** metric (`# new links`) counts pairs of FREX
concepts that co-occur in the thesis for the first time in the 1977–2015
corpus. Co-introductions in the same year both get credit (1.6% of links;
99.7% of these are same-graduation-year).

**Spurious-link filtering via PMI.** Not all concept co-occurrences are
meaningful. They compute pointwise mutual information:

> PMI(L) = log₁₀ (Pr(a,b) / (Pr(a) × Pr(b)))

Links with low PMI (common-term co-occurrences that happen by chance) are
filtered. They keep the top 10M links after requiring each term to occur in
≥10 theses. This is an important methodological detail; without it, the
novelty signal would be flooded by noise links.

- `# new links`: mean=9.026, median=4, SD=13.744
- 20.9% of students introduce *zero* new links

### 4. Impactful novelty = future uptake per link

Impactful novelty (`uptake per new link`) counts how often subsequent theses
reuse a link first introduced by an earlier thesis, normalized by the
introducer's link count. Roughly 50% of new links are never taken up.

- `uptake per new link`: mean=0.790, median=0.333, SD=3.079

### 5. Distal novelty = semantic distance between linked concepts

To ask whether some novelty is more "distant" than other novelty, they train
a **Word2Vec skip-gram** embedding of the FREX concepts on the dissertation
abstracts (window=5, 100 dimensions; SI confirms robustness to 100/200/300
dims and stochasticity). Distance between newly linked concepts is cosine
distance; averaged over all new links in a thesis.

- `distal novelty`: mean=0.426, median=0.419, SD=0.118
- Validated with 3 human coders on 100 random links, Cohen's κ=0.46 (moderate
  agreement); coder judgments predict ~95% of distance>0.8 links
- 15–20% of distance>0.8 links are hard to interpret substantively (either
  metaphorical or cross-field)

**Notable diachronic choice:** they use **globally-trained time-independent
embeddings**, not per-era embeddings. Their justification (SI, p. 12): on
year 2000 specifically, global and time-dependent embeddings correlate at
r=0.931 for distal-novelty scores. They note modeling per-era is
"computationally intensive and suffers from data sparsity." **This is a
choice ws2 should think carefully about.**

### 6. Demographic inference from names

**Gender** (SI, pp. 13–14): first names matched to US SSA baby-name
frequencies (1900–2016); threshold of 71.45% female fraction for "female"
assignment; validated on 20,264 private-university scholars with self-reported
gender (r=0.91). Genderize.io fills remaining gaps (>95% agreement with their
combined method). **~8.5% of cases are unknown gender** after all methods.

**Race** (SI, pp. 13–15): last names matched to US Census 2000 and 2010
frequencies; per-name accuracy:

- White: 97.2% (12,929 of 13,197)
- Asian: 93.4% (5,079 of 5,436)
- Hispanic: 70.4% (698 of 992)
- **African and Native American: 9.9% (63 of 639)** — catastrophic

They patch this with Sood-Laohaprapanon 2018's character-sequence method
(trained on Florida voter registration), which raises Hispanic to ~0.83 and
African-American to ~0.74. Three racial categories are used for analysis:
white, Asian, and "underrepresented minority" (URM, combining Hispanic,
African-American, Native American). **~10.8% of cases are unknown race**.

### 7. Statistical models

- **Novelty & impactful novelty** → negative binomial regression (right-
  skewed counts; overdispersion handled via the NB dispersion parameter).
  Impactful novelty modeled with `log(# new links)` as an **offset** so
  coefficients are interpretable as rate changes (uptake per link).
- **Distal novelty** → linear regression (approximately normal).
- **Careers** (research faculty / continued research, both binary) →
  logistic regression.
- **Fixed effects throughout**: institution (N=215), academic discipline
  (N=84), graduation year (1977–2015). Missing disciplines inferred via
  random forest classifier with 96% precision using LDA topic distribution,
  keywords, Word2Vec averages, and university as features.
- **Sample weights**: relative number of PhD recipients per university-year
  (ProQuest vs. NSF population records) — accounts for selectivity in
  ProQuest filing patterns.

### 8. Career outcomes: a restrictive and a permissive measure

- **Research faculty** (mean=0.066): PhD becomes primary advisor of another
  PhD in the corpus. Narrow and conservative; captures only advisors at US
  PhD-granting universities with at least one trackable student.
- **Continued research** (mean=0.319): PhD publishes in WoS within 5 years
  of graduation OR becomes research faculty. Broader; includes non-academic
  research, liberal arts colleges, etc.

ProQuest-to-WoS matching is multi-step with heuristics (SI pp. 19–20):
co-authorship with advisor, institution match, keyword match, name-string
similarity, abstract-title textual similarity. Authors disambiguated via
Levin-Krawczyk-Bethard-Jurafsky 2012 (pre-2009) and Clarivate's proprietary
disambiguation (post-2009), reconciled via shared-article-cluster heuristics.

### 9. Core findings

**(a) Underrepresented introduce more novelty.** More same-gender peers in a
discipline-year reduces `# new links` (P<0.001); same for race (P<0.05).
Women introduce more novelty than men (P<0.001); nonwhite more than white
(P<0.001).

**(b) Their novelty is less taken up.** More same-gender peers *increase*
`uptake per new link` (P<0.01) — i.e., minorities' uptake is lower. Same
pattern for binary gender and race. No clear relationship for same-race
fraction (but binary nonwhite vs. white is significant).

**(c) Women introduce more distal novelty; distal novelty gets less uptake.**
% same-gender ↓ distal novelty (P<0.001); distal novelty ↓ uptake (P<0.001).
This is presented as a partial mechanism for the gender uptake gap.

**(d) Both novelty and impactful novelty predict careers.** Positive effects
on both faculty and continued-research outcomes (all P<0.001).

**(e) But minorities need higher innovation for same career returns.** At
low innovation levels, minority and majority career probabilities are
similar. At high levels they diverge. Specifically:

- 2SD increase in novelty → gender gap in faculty-probability grows from
  3.5% to 9.5%
- 2SD increase in impactful novelty → gender gap grows from 4.3% to 15%
- This discount holds controlling for distal novelty.

**(f) Robustness (Table S2).** Most results qualitatively stable across
K∈{400,500,600} × FREX∈{25/75, 50/50, 75/25}. The notable exceptions:
"racial minorities impact discount for continued research" is NOT significant
across all scenarios (no YES cells); some results vary at K=400 + extreme
FREX.

---

## Results — Three Levels

### Level 1: For a smart high-schooler

Hofstra and colleagues wanted to know whether diversity in who becomes a
scientist leads to new ideas — and whether those new ideas get recognized.
They looked at almost every PhD thesis in the US from 1977 to 2015
(1.2 million of them) and read what concepts appeared together in each
abstract. If you wrote a thesis using two ideas that had never been linked
before, the computer counted that as a "new connection" — their stand-in for
scientific novelty.

What they found was uncomfortable but consistent: women and people of color
in PhD programs made *more* new connections than white men did. But when
other people wrote later theses, they were *less* likely to use new
connections that came from women or people of color than new connections
that came from white men. And when it came to getting faculty jobs, you had
to produce much more novelty as a woman or a person of color to get the same
career outcome as a white man.

The "paradox" in the title: diverse scientists are more innovative, but the
system doesn't reward their innovation equally. Innovation is undercounted
when it comes from certain people.

### Level 2: For a junior/senior undergraduate

The authors link a near-population of 1.2M ProQuest US dissertations
(1977–2015) to Web of Science publication records and to name-based
demographic inference. They use Structural Topic Models at K=500 topics to
extract scientific concepts (via FRequency-EXclusivity weighting of topic
term distributions), then count when pairs of concepts first co-occur in a
thesis — this is their "novelty" measure. They filter spurious co-occurrences
with pointwise mutual information. They also compute "distal novelty"
(semantic distance between linked concepts in a Word2Vec embedding trained on
the corpus) and "impactful novelty" (uptake of a thesis's new links in later
theses, per link introduced).

Using negative binomial regression with institution, discipline, and year
fixed effects plus population weights, they show four things: (1)
underrepresented groups introduce more novelty; (2) minorities' novelty is
taken up less; (3) women introduce more distal novelty, which is generally
less taken up; (4) the career return on novelty is smaller for minorities —
minorities need higher innovation for similar faculty or continued-research
outcomes.

The design is associational, not causal. They use institution-discipline-year
fixed effects to absorb confounders at those levels, but they cannot rule
out all omitted variables (cohort-level quality differences, strategic topic
selection, advisor effects). The demographic inference is name-based and has
substantial error rates on non-white-non-Asian names, particularly African-
American and Native American (9.9% accuracy initially, raised to ~74% with
an auxiliary character-sequence method). Their 3-category race
operationalization (white/Asian/URM) folds African-American, Hispanic, and
Native American together due to low per-category accuracy.

### Level 3: For an early graduate student

The paper is methodologically ambitious and honest about its limits. Three
aspects repay close attention.

**(a) The novelty metric's construct validity.** "Number of first-introduced
concept pairs in a thesis abstract" is a defensible but narrow
operationalization of innovation. It captures combinatorial novelty
(Weitzman-style recombination) but not conceptual depth, methodological
innovation, or theoretical reframing. A thesis that introduces no new concept
pair but substantially changes how existing concepts relate would score zero.
A thesis that idiosyncratically juxtaposes two terms that happen not to
co-occur elsewhere — but carries no real intellectual weight — scores
positive. The PMI filter is their defense against the second failure mode;
there's no defense against the first.

Their external validity check (Table S3) shows that both `# new links` and
`uptake per new link` correlate with publication count and citation count
among publishing students. This is moderately reassuring but not dispositive
— citation counts have the same field-indexing issues they flagged initially.

**(b) The demographic inference's unequal error structure.** The most honest
part of the paper is SI pp. 13–15. White names achieve 97.2% accuracy; Asian
93.4%; Hispanic 70.4%; African-American and Native American 9.9%. The
auxiliary character-sequence method (Sood-Laohaprapanon 2018, trained on
Florida voter registration) raises AA to ~74% and Hispanic to ~83%. This is
*structurally* the problem Lockhart, King & Munsch 2023 (*Nature Human
Behaviour*) would later describe at scale — name-based inference error
concentrates in marginalized groups, confounding any cross-racial
comparison.

The paper's response is to fold Hispanic, AA, and NA into a single "URM"
category, exclude ~10.8% unknown cases, and run robustness checks on a
"highly certain cases only" subsample. They report that substantive
conclusions are unchanged. But the inference uncertainty propagates into the
URM-vs-majority contrasts in ways the point estimates don't reveal, and
intersectional analyses (gender × race) inherit the weakest inference cell.

**(c) The innovation-discount causal claim is not identified.** The finding
"minorities need higher novelty for equal career outcomes" is striking and
probably true directionally, but the design is associational. The fixed
effects (institution × discipline × year) absorb selection at those levels,
but not selection within them (which advisor, which research problem, which
venue for publication, pre-PhD preparation). The discount could reflect
discrimination (the authors' preferred reading), unmeasured quality
differences in the novel work (minorities' novelty is "different-novel" in a
way the measurement captures but reviewers penalize for legitimate
reasons), or post-PhD structural barriers (dual-career moves, caregiving,
geographic constraints) that confound innovation measurement with career
opportunity. The paper acknowledges this framing limit in the Discussion
without claiming causal identification.

The result is nonetheless important: the *conditional correlation* of
innovation with career outcomes differs by demographic group, which demands
an explanation. The authors offer the discrimination reading; other readings
are possible; the data does not adjudicate among them.

Methodologically this paper is in the top tier of scientometric studies
engaging with demographic-inference caveats seriously. The combination of
near-population coverage, PMI-filtered novelty, auxiliary demographic methods,
and fixed-effect controls is the model for how to do this rigorously.

---

## Connection to Our Project

### What Hofstra et al. do well that we should learn from

1. **PMI-based spurious-link filtering.** If ws2's Test IV tertiary novelty
   metric (Uzzi-style recombinant novelty over references) is pursued, PMI
   filtering is the right mechanism to separate meaningful from chance
   co-occurrences. Directly adoptable.
2. **Multi-scenario robustness across K and FREX.** Table S2 reports
   every headline result across 9 K×FREX scenarios. This is the model for
   our own cluster-count (K∈{30,50,100}) and anchor-weighting sensitivity
   tables. Default practice for ws2.
3. **Auxiliary demographic methods where primary methods fail per-group.**
   They use two independent inference methods (Census + Sood-Laohaprapanon
   character-sequence) and describe the per-group accuracy gain explicitly.
   Our Genderize.io + NamSor split follows the same principle.
4. **Conservative + permissive outcome measures.** Research faculty (mean
   0.066, narrow) + continued research (mean 0.319, broad). Reporting both
   lets results be robust against definitional disagreements. We should
   consider analog pairs for our own dimension-level reporting.
5. **External validity via publication/citation correlation.** Table S3's
   check — novelty correlates with WoS publications and citations — is a
   legitimate construct-validity defense even though it uses the same
   citation machinery they initially criticized. For our novelty metric
   (embedding distance to citation centroid), a similar check against
   external reception measures would be useful.
6. **Honest limitations in the main text.** They openly flag name-based
   inference failure modes, the associational nature of the career analysis,
   and acknowledge the African-American/Native-American accuracy gap.

### What Hofstra et al. do NOT do — and where ws2 fills the gap

1. **Individual-level, not team-level.** Their unit is the dissertation
   (single author). Our Test IV is team-level (paper author team). The
   substantive question shifts: Hofstra asks "do minority *individuals*
   produce more novel work?"; we ask "do demographically diverse *teams*
   produce more novel work?" These are different questions, and the two
   results can diverge even if both mechanisms are real.
2. **Cross-sectional snapshot (1982–2010), not long-horizon time series.**
   Their sample window is 28 years; ours is 54. Their analyses keep
   institution-discipline-year fixed, but do not model time-trend
   interactions (except implicitly through year fixed effects). Our Tests
   I–III are explicit time-series analyses of trend divergence.
3. **Dissertations, not papers.** A dissertation is one author's first big
   work. A paper is a team's published artifact. These differ in length,
   review process, authorship norms, and venue selectivity. Our conclusions
   should *not* be assumed consistent with theirs just because the
   methodology looks similar.
4. **Globally-trained time-independent Word2Vec embeddings.** Their
   justification (r=0.931 between global and year-2000 embeddings) is
   specifically for a year that is close to their training-corpus center.
   Early-era (1982) and late-era (2010) embeddings could drift more. Our
   drift-mitigation ladder addresses this head-on.
5. **STM-based concept extraction, not transformer embeddings.** STM is
   topic-model-based; we use SPECTER2 contextual document embeddings. Their
   novelty is combinatorial (new concept pairs); ours is geometric (cosine
   distance to citation context centroid). Co-movement under both approaches
   on a shared test set would be a meaningful robustness result.
6. **No engagement with embedding-drift concerns.** They use one Word2Vec
   model for all years; do not run a Procrustes-aligned diachronic check.
   Given their r=0.931 justification was for year 2000 only, this is a
   vulnerability their own data could have revealed but didn't.
7. **"URM" as a single category.** Combining Hispanic, African-American,
   and Native American into one URM bucket is an inference-necessity move,
   not a substantive one. It obscures heterogeneity that our region-of-origin
   stratified sensitivity analysis attempts to preserve.

### Specific design implications for ws2

1. **Test IV sign interpretation gets a reference point.** Hofstra's finding
   is γ > 0 at individual level (underrepresented produce more novelty).
   If our γ in Test IV is:
   - **γ > 0**: consistent with Hofstra; individual-vantage effect survives
     team aggregation.
   - **γ < 0**: opposite finding; team-level actuators (shared advisor,
     shared canon, consensus-building within team) overwhelm the individual-
     vantage effect. Strong novel result.
   - **γ ≈ 0**: the two cancel at team level; aggregate dynamics decouple
     from individual dynamics.
   All three are publishable; the first aligns with prior work, the other
   two challenge it.
2. **"Impactful novelty" is worth considering for Test IV.** Hofstra's
   two-step design — novelty, then uptake-per-novelty — is stronger than
   novelty alone. For ws2, "uptake" would require citation trajectories
   beyond our primary sample; feasible as a Stage 3 extension, not Stage 2
   primary. Worth noting in the phase plan's extension discussion.
3. **Name-inference accuracy reporting must match or exceed Hofstra's
   transparency.** Their per-group accuracy table is the bar. Our Phase 0.1
   Check 3 must produce an analog (per-region accuracy from ORCID ground
   truth).
4. **We should *not* fold demographic subcategories into single buckets
   unless inference accuracy forces us.** Hofstra's URM category is a
   necessity given their data; ours might be avoidable if Genderize+NamSor
   give adequate per-region accuracy. If it doesn't, disclosure should be
   equally explicit.
5. **Their "distal novelty → less uptake" result is important for us.**
   If our embedding-distance novelty metric (Test IV primary) captures
   something like "distal novelty," we may inherit the same mediator:
   distant recombinations get less uptake, so minorities' distant
   recombinations face a double discount. This is an explicit mechanism
   hypothesis to engage in Discussion.
6. **Diachronic embedding concern validated.** Their use of time-independent
   embeddings, with the r=0.931-on-year-2000 justification, is exactly the
   sort of single-year-justification our drift-mitigation ladder rejects.
   Their paper is a positive example of how *not* to treat diachronic
   robustness when the sample window is 28 years; our 54-year window needs
   more.
7. **Consider a sensitivity analysis on minority-author teams specifically.**
   Beyond team composition Rao's Q, consider reporting Test IV separately
   for teams with vs. without underrepresented-minority members. This is
   closer to Hofstra's research question and lets us engage directly with
   their framing.

---

## Key Quotes

On innovation vs. citation-based metrics:

> "The advantage of our focus on conceptual recombination compared to
> citation metrics for innovation is that it is insensitive to 1)
> prioritizing some academic disciplines over others with regard to
> journal indexing and 2) the plethora of reasons as to why scholars cite
> other work." (p. 9285)

On the novelty-adoption distinction:

> "Novelty in itself does not automatically imply innovation, nor is the
> future adoption of novelty a prerequisite to innovation—for example,
> which novelty gets adopted may be in itself a function of structural
> processes." (p. 9285)

On name-based demographic inference as perception proxy:

> "We recognize that in reality, individuals and names have varying
> degrees of gender and racial associations; as such our named-based
> metric is a simplified signal of gender and racial identity that may
> better capture how an individual is perceived by others and can be only
> a coarse proxy for authors' self-identification with certain genders or
> races." (p. 9289–9290)

On the core finding, worth citing verbatim in ws2's Related Work:

> "Numerically underrepresented races in a discipline have lower odds of
> becoming research faculty (25% lower odds) and continuing research
> endeavors (10% lower odds) compared to majorities." (p. 9287)

On the implications:

> "These results suggest that the scientific careers of underrepresented
> groups end prematurely despite their crucial role in generating novel
> conceptual discoveries and innovation. Which trailblazers has science
> missed out on as a consequence?" (p. 9288)

---

## Study Questions

**Warm-up (Level 1):**

1. What does "novelty" mean operationally in this paper? Give an example
   from Figure 1.
2. What's the "paradox" in the title? State it in your own words.
3. What's the difference between "novelty" and "impactful novelty"? Which
   does the paper claim matters more for explaining the career gap, and why?

**Intermediate (Level 2):**

4. Why do Hofstra et al. use Structural Topic Models (STM) to extract
   concepts rather than simpler approaches like TF-IDF? What specific
   advantage does STM offer for their task? (SI pp. 4–5)
5. What is FREX scoring? Why isn't it enough to just pick the most frequent
   terms in each topic? (SI p. 11)
6. The authors use negative binomial regression for novelty and impactful
   novelty, and include `log(# new links)` as an *offset* when modeling
   impactful novelty. Why not use OLS? What does the offset accomplish? (SI
   pp. 17–18)
7. The paper reports that ~50% of new links never get taken up. Given this,
   and given that 20.9% of students introduce zero new links, what fraction
   of students produce *any* novelty that gets adopted? What does this
   imply about the shape of the innovation distribution?
8. How do Hofstra et al. measure "distal" vs. "proximal" novelty? What
   Word2Vec hyperparameters did they use, and how did they validate?
   (p. 9286, SI p. 12)

**Advanced (Level 3):**

9. The PMI filter keeps the top 10M links after requiring each term to
   occur in ≥10 theses. What would happen to the novelty signal if the
   threshold were 1 vs. 100? How might results change under a raw-frequency
   filter instead of PMI?
10. They justify using *global* (time-independent) Word2Vec embeddings by
    showing r=0.931 between global and year-2000 time-specific embeddings.
    Under what conditions would this justification fail? Specifically: what
    does it imply for 1982 vs. 2010 embeddings, neither of which was the
    validation year?
11. The "innovation discount" finding — minorities need higher novelty for
    similar career outcomes — is reported at a 2SD-above-median increase
    yielding a 3.5% → 9.5% faculty-probability gap for gender. What's the
    appropriate *null hypothesis* for this comparison? What identifying
    assumptions would make it a causal discount rather than a conditional
    association?
12. The career outcome "research faculty" requires the PhD to become primary
    advisor of another PhD in the same ProQuest corpus. What are the
    selection mechanisms this definition induces? How would the reported
    career gaps change under alternative definitions (e.g., "obtained
    tenure-track position")?
13. Per-group name-inference accuracy ranges from 97.2% (white) to 9.9%
    (African-American + Native American, pre-auxiliary). Their URM category
    folds Hispanic + AA + NA. What does this imply about the *internal
    heterogeneity* of the URM-vs-majority contrasts they report? How would
    you decompose it if you had better inference?
14. Figure 4 shows career discount for minorities at high novelty levels.
    But by Figure 3, minorities introduce more distal novelty, and distal
    novelty independently gets less uptake. Does the career discount persist
    *after* controlling for distal novelty, and if so by how much? (The paper
    claims yes; find the numbers.)

---

## Challenge Corner

**C1:** Hofstra et al. frame the diversity-innovation finding as "outsider
vantage": minorities come from distinct walkways and see conceptual
connections majorities miss. What alternative explanations fit the data
equally well? (Selection into distinctive research topics, advisor
differences, supervisor risk tolerance, cross-disciplinary training
pipelines, etc.) Is the outsider-vantage framing privileged over these by
the data or by the authors' priors?

**C2:** The "distal novelty → less uptake" mediator is presented as a partial
explanation for why minority-introduced novelty gets adopted less. But distal
novelty is itself less likely to be adopted *regardless of who introduces
it*. Is the mediator meaningfully about discrimination, or is it a simpler
claim that unconventional combinations take longer to diffuse for
information-theoretic reasons (receivers need more inferential work)? How
would you distinguish?

**C3:** Hofstra's individual-level finding is that underrepresented people
produce more novelty. If we re-aggregate to team-level (our Test IV), what
result is most likely? Consider:
- Pure additive aggregation: teams with more underrepresented members should
  produce more team-level novelty.
- Actuator-override aggregation: teams average toward canonical outputs via
  shared inputs (advisor, canon, platform), and individual vantage gets
  suppressed.
- Selection aggregation: the formation of teams is non-random with respect to
  both diversity and research topic; controls absorb most of the individual-
  vantage effect.
Which do we expect, and what would we update on given Hofstra's finding?

**C4:** Their per-group demographic inference accuracy is 97.2% white, 93.4%
Asian, 70.4% Hispanic, 9.9% AA/NA (pre-auxiliary). The AA/NA rate is
*catastrophically low*. They patch this with a character-sequence method to
raise it, but the published headline findings depend on classifications made
with variable accuracy across the groups being compared. Does this invalidate
the URM-vs-white contrasts, and if not, what sensitivity analyses would
clear it? Does our Lockhart-2023-grounded weight-by-confidence approach
actually solve this in ws2, or does it just make the uncertainty visible?

**C5:** Hofstra uses time-independent concept embeddings and justifies the
choice by one year (2000) of validation. Our drift-mitigation ladder rejects
this. If we re-ran Hofstra's analysis with per-era embeddings aligned via
Procrustes (their Flavor A, adapted), which of their findings would most
plausibly change, and which would be stable?

**C6:** Their novelty metric is combinatorial (count of first-introduced
concept pairs over a fixed corpus-level FREX vocabulary). Our Test IV
novelty metric is geometric (embedding distance to citation context
centroid). Two sub-questions:

(a) Construct an example where these diverge — i.e., a paper that is
high-novelty on one measure and low on the other. Which metric would
better capture what a field's reviewers mean by "novel"?

(b) **The combinatorial metric has a hidden asymmetry on vocabulary-first
terms.** Because the FREX vocabulary is defined once over the entire
1977–2015 corpus, a thesis that is the *first* to use a vocabulary-valid
term T gets credit for every pair `(T, existing_concept)` *simultaneously*
— every co-occurrence of T with a term already in circulation is a
"first pairwise co-occurrence." A thesis introducing a rare-but-valid
term with 20 pre-existing co-concepts racks up 20 new links at once,
while a thesis creatively re-linking two already-common terms gets
credit for one. This weighting isn't called out in the paper. Does it
match the substantive notion of "introducing a new concept"? What does
it imply about which kinds of theses score high on `# new links`? If
ws2 adds a Uzzi-Mukherjee-Stringer reference-pair novelty as Test IV
tertiary (Stage 3), do we inherit the same asymmetry — and how would we
want to handle it? (Candidate: count first-co-occurrences with
down-weighting proportional to the pre-existing concept's frequency, so
introducing-a-new-term gets credit but not k× the credit of
relinking-two-established-terms.)

**C7:** The "innovation discount" result says minorities need higher
innovation to get similar career returns. The authors interpret this as
discrimination. A sympathetic critic might argue it reflects unmeasured
quality differences in the novel work (e.g., minorities' distant recombinations
are more speculative, less well-defended). How would you adjudicate between
these interpretations with additional data we don't currently have?

**C8:** The ProQuest-to-WoS matching pipeline has a ~97% precision
(SI pp. 19–20), meaning ~3% of linked author-records are wrong. For a
corpus of 1.2M students, that's 36K mismatches. These are concentrated in
names with weak signal (common surnames, non-US-standard names). Does this
compound their demographic-inference bias, and how? What would the career
analysis look like if we restricted to the high-confidence-linkage subset?

**C9:** Their paper studies dissertations — the thing a single person writes
at the *start* of their research career. Our ws2 studies papers — the thing
a team writes across a *career-spanning* corpus. What substantive difference
does this make for the diversity-innovation question? Does the "outsider
vantage" argument apply equally to first-year dissertations and mid-career
collaborative papers?

**C10:** The paper's core findings rest on ~1.2M dissertations, but the
inferential analyses restrict to 1982–2010 (~28 years). The restriction is
justified by allowing 5 years before/after for concept accumulation and
uptake. Given ws2 spans 1970–2024, how should we think about the analogous
boundary conditions for our cross-year analyses?

**C11 — Test-of-time / persistence:** Hofstra's uptake measure has three
scope limitations:

1. **Within-corpus only.** It counts reuse of a thesis's new links in
   *other theses*, not in published papers, textbooks, or broader citation
   patterns. A link that becomes textbook canon but isn't in another
   thesis gets zero credit.
2. **Unweighted by reception quality.** Reuse in an obscure thesis scores
   the same as reuse in a highly-cited one.
3. **Pattern-blind.** The uptake count aggregates across all years post-
   introduction. A link that gets reused 10 times in year 2 and then never
   again scores the same as one reused 10 times slowly over 20 years.

This leaves the central diversity-innovation claim underdetermined:

- **Discrimination reading** (Hofstra's): minorities produce durable
  innovation that is under-rewarded short-term but should eventually
  surface via slow diffusion and rediscovery.
- **Surface-novelty reading** (sympathetic critic): minorities produce
  idiosyncratic combinations that *look* novel by the combinatorial
  measure but aren't substantively deep; short-term low uptake reflects
  genuine quality, not bias; long-term persistence would also be low.

These are observationally equivalent in Hofstra's data but predict
*different* persistence patterns over 15+ year horizons — which OpenAlex
citation trajectories give us. Should Test IV incorporate a persistence
analysis as a Stage 3 extension? What are the data-availability
constraints (10-year lookahead truncates the analysis window at ~2014
papers)?

---

## Synthesis Pointers (for `synthesis.md`)

1. **Hofstra's findings anchor Test IV's sign discussion.** We now have a
   concrete prior-literature finding to contrast or replicate. Our γ > 0
   outcome aligns with Hofstra; γ < 0 contradicts them at team level and
   becomes the paper's news.

2. **The distal-novelty → less-uptake pathway is a within-field mechanism
   worth engaging.** For the Test IV time-interaction analysis (γ₁(Y) =
   γ₁₀ + γ₁₁Y), a strengthening negative γ₁₁ could reflect growing
   canonical concentration making distal work less adoptable over time.
   This connects Test IV directly to Test I/II's aggregate divergence.

3. **PMI-based spurious-link filtering is transferable.** If Test IV's
   tertiary novelty metric (Uzzi recombinant novelty over references) is
   pursued at Stage 3, PMI is the right filter. Default to Hofstra's
   threshold (terms appearing in ≥10 units) unless data volume differs.

4. **Per-group accuracy reporting is the transparency standard.** The
   Phase 0.1 drift-pilot and demographic-coverage checks should produce
   analog tables to Hofstra's SI pp. 13–15. This is now a minimum bar.

5. **Time-independent embedding-plus-single-year-validation is insufficient
   rigor.** Hofstra's r=0.931-on-year-2000 justification does not clear the
   bar ws2 sets for itself. Use as a cautionary citation when defending
   our drift-mitigation ladder.

6. **Hofstra connects to 13-B (demographic-diversification-as-cosmetic)
   directly.** Their finding is the individual-level version of 13-B at
   the reward stage: diverse inputs do not generate proportionally diverse
   adopted outputs because of differential reward. Our aggregate
   divergence (Tests I–III) is the population-level analog.

7. **URM-as-single-category is a negative example.** Even well-executed
   demographic measurement forces category aggregation under inference
   constraints. Our region-of-origin stratification is an attempt to do
   better, but it inherits the same per-group accuracy limits.

8. **Reviewer-pool implications:** Hofstra, McFarland, and Jurafsky are the
   Stanford cluster most likely to review ws2 if submitted to sociology/
   science-of-science venues. Engaging their 2020 finding directly (not
   just citing it) is reviewer-prep.

9. **Test-of-time / persistence sharpens 13-B adjudication (Stage 3
   extension).** Hofstra's uptake measure is narrow (within-dissertation
   only, unweighted, pattern-blind). Our OpenAlex-based design can measure
   long-term citation trajectories — Stage 3 extension to Test IV testing
   `log(1 + C_15(p))` and `C_10/C_3 persistence ratio` against team
   diversity × novelty. This directly adjudicates between the
   "discrimination" and "surface-novelty" readings of the diversity-
   innovation finding — one of the few live interpretive ambiguities in
   this literature. Data-availability: persistence needs 10+ year
   lookahead, truncating analysis window at ~2014 papers. Effort cost:
   ~1 week Stage 3, uses existing OpenAlex data, no new API calls. Goes
   into Phase 0.2 pre-registration as a Test IV persistence extension.

10. **Combinatorial-metric asymmetry informs Test IV tertiary design.**
    If we add Uzzi-Mukherjee-Stringer reference-pair novelty as a Stage
    3 tertiary for Test IV, Hofstra's hidden new-term weighting (a term's
    first appearance credits every co-occurring existing concept as a
    new link) is a known artifact we should either inherit or correct for.
    Candidate correction: down-weight first-co-occurrences by the
    pre-existing concept's frequency, so introducing-a-new-term gets
    credit but not k× the credit of relinking-two-established-terms.
    Pre-register in Phase 0.2.

11. **Scale-difference framing: aggregate vs. per-paper novelty.**
    Hofstra's novelty is a per-paper, combinatorial, composable quantity
    (each paper counts new concept-pairs; totals aggregate). Ws2's
    semantic diversity is aggregate, distributional, non-composable
    (each year has a spread-of-output number that isn't a sum over
    papers). These dissociate in at least four cases: (high per-paper
    novelty concentrated in one region of embedding space) vs. (normal
    science across diverse topics). Ws2's Methods and Discussion should
    engage this distinction explicitly: Tests I–III measure distributional
    spread at the population level; Test IV measures per-paper novelty
    (parallel to Hofstra's scale); together they triangulate, but they
    are not the same measurement at different units. Different
    combinations of results across scales tell different mechanism stories.

12. **Citation-as-behavioral-trace framing.** Citations are load-bearing
    in ws2 in four places (canonical concentration in Tests I–III;
    intellectual-context definition for Test IV primary N_p; long-term
    citation accumulation for Test IV persistence extension; reference-
    pair recombination for Test IV tertiary if pursued). Hofstra's
    "plethora of reasons to cite" argument motivates reducing citation
    load where possible. Concept-linkage novelty (Hofstra's methodology,
    adopted as Test IV secondary alongside embedding-distance primary)
    provides a citation-independent parallel novelty measure for Test IV,
    partially alleviating citation load on the novelty side. Canonical
    concentration and persistence remain citation-based — no substitute
    cleanly dodges the analogous "plethora of reasons to reuse a
    concept-linkage" problem. Methods section acknowledges that
    citations are behavioral traces, not direct influence measures, and
    that the measurement-to-influence chain (citation → attention →
    reception → influence) requires interpretive leaps reserved for
    ws1's interventional simulation rather than claimed from ws2's
    observational data.

---

## Discussion Notes

(To be filled in during the review session. Blank until we discuss the
Challenge Corner together.)

### On C1 — outsider vantage vs. alternatives

Working session with user, 2026-04-24.

**User's first-pass observation.** *"I don't know if data would've
had sufficient power to test these alternate hypotheses given the
size (likely they would) but the framing seems a bit agenda-driven.
In any case, what are the lessons for us? Should we consider
different ways to define demographic diversity?"*

The intuition is correct on both counts: the data does have power to
test most of the alternatives, and the outsider-vantage framing is
agenda-driven by the authors' theoretical priors rather than
data-privileged.

**Which alternatives are actually testable in Hofstra's data.**

Sample size (~800K observations in inferential analyses) is not the
constraint. The constraint is willingness to run the tests.

- **Topic selection within discipline:** testable. Hofstra has
  concept tags per thesis. Within-topic novelty comparisons would
  isolate topic-selection from demographic-novelty. Not done in
  main text.
- **Advisor differences:** testable. Advisor IDs are in ProQuest;
  advisor fixed effects would absorb time-invariant advisor-specific
  effects. If the minority-novelty finding disappears when adding
  advisor FE, advisor is the driver. Not done in main text.
- **Supervisor risk tolerance:** proxy-able via advisor-prior-
  novelty. Risk-tolerant advisors may attract novelty-inclined
  students and themselves produce novel work. Not done.
- **Cross-disciplinary training pipelines:** harder — needs
  undergraduate-major data not in ProQuest. Testable only with
  external data merge.
- **Self-selection into academia:** not testable from post-hoc
  academic data; requires counterfactual.

Three of five alternatives are directly testable; Hofstra runs none
of them.

**Outsider-vantage privileged by priors, not data.** The data shows:
*conditional on institution × discipline × year, minorities produce
more novelty.* This conditional pattern is compatible with outsider
vantage AND advisor mediation AND within-discipline topic selection
AND risk-tolerance differentials AND career-risk calculations
AND self-selection effects. Any of these alone or in combination
could produce the observed pattern.

Choosing outsider vantage as THE interpretation reflects:

- Hofstra's theoretical framing (citing Page's diversity-innovation
  literature heavily)
- The paper's rhetorical structure (lead with paradox; treat
  discounting as primary contribution)
- The pre-existing diversity-science literature the paper contributes
  to

Sympathetic reading: outsider vantage is the most parsimonious
theoretical frame. Hostile reading: it's the frame they wanted to
find. Either way, the alternatives aren't substantively engaged.

**The structural issue C1 surfaces.** The agenda-driven framing
points at a deeper problem: **the mapping from measurable
demographic categories to substantive claims about "different
perspectives" requires an interpretive leap the data cannot support.**

Hofstra's chain is:

> categorical inference (name-based) → demographic category
> assignment → assumed correspondence with lived experience →
> assumed correspondence with cognitive diversity → assumed effect
> on novelty production

Each arrow is an interpretive commitment, not a measurement. The
paper treats the chain as self-evident; close reading surfaces each
step as an assumption.

This is the third parallel measurement-construct gap we've
identified, alongside novelty-vs-innovation (SQ7, SQ11) and
citation-vs-influence (Synthesis Pointer 12). All three operate on
the same structural pattern: surface marker, intermediate construct,
substantive target, with each arrow requiring an interpretive
commitment the data alone cannot adjudicate.

**Lessons for ws2 — three structural commitments derived from C1.**

User asks: "Should we consider different ways to define demographic
diversity?" Yes. Three specific moves:

**(a) Multi-operationalization of demographic diversity.** Our
current Rao's Q metric operates on observed categorical demographics
(gender, country, institution, prestige, career stage, training
institution). To reduce reliance on any single proxy chain, run ws2's
divergence test under multiple operationalizations:

- **Categorical** (current primary): Rao's Q over 7 features.
- **Lineage-based** (Proxy A, already committed): Gini over training-
  institution concentration.
- **Advisor-lineage-based** (Proxy B, Stage 3): inferred-advisor
  diversity from Math Genealogy + ORCID validated subset.
- **Network-position-based** (potential Stage 3 addition): variance
  in coauthor-network centrality measures.

If all show similar divergence trends, multi-operational robustness.
If they differ, the substantive divergence claim is operationalization-
specific. **Add to pending batch as a new sub-item under item 11
(or new item) — Stage 3 Test I/II/III robustness with alternative
demographic-diversity operationalizations.**

**(b) Explicit Methods-section acknowledgment of the categorical-to-
substantive proxy chain.** Add to item 9 (Methods framing paragraph)
a third measurement-construct gap acknowledgment:

> *"Our demographic-diversity metric operates on observed demographic
> categories (gender, country, institution, etc.) inferred from name
> and affiliation data. We treat these as proxies for the substantive
> concept of 'different perspectives' that diversity-innovation
> theory invokes (lived experience, cognitive priors, intellectual
> pipelines). The categorical-to-substantive mapping requires
> interpretive assumptions that our measurements cannot directly
> validate. Where feasible (Proxy A training-institution
> concentration, Stage 3 Proxy B advisor lineage), we supplement
> categorical demographics with lineage-based operationalizations to
> reduce reliance on any single proxy chain."*

Three-sentence framing commitment; no new analysis.

**(c) Subfield-concentration-of-divergence as robustness against
alternatives.** Already in our subfield mechanism test, but worth
framing in Discussion: if divergence is concentrated in canonical-
concentrated subfields, consistent with actuator-mediated mechanisms;
if uniform across subfields, more consistent with outsider-vantage-
like dynamics. The subfield mechanism test already bears on this
distinction.

**Not adopting.**

- Advisor fixed effects at our scale — too computationally expensive,
  and our subfield FE absorbs much of the relevant variance.
- Explicit topic-selection test beyond what subfield mechanism test
  provides.
- Undergraduate-major integration — out of scope.

**One-sentence summary.** Three of five alternative explanations
(topic selection, advisor differences, supervisor risk tolerance)
are directly testable in Hofstra's data but not tested; the outsider-
vantage interpretation is privileged by authors' priors rather than
data. The deeper lesson — categorical demographic measurements proxy
for substantive diversity in ways that require interpretive leaps —
is the third parallel measurement-construct gap we've identified
(alongside novelty-vs-innovation and citation-vs-influence). For
ws2: multi-operationalization of demographic diversity (item 11
sub-item / new item), explicit Methods-section acknowledgment (item 9
extension), and subfield-concentration framing in Discussion.

### On C2 — distal-novelty mediator: discrimination or information-theoretic?

Working session with user, 2026-04-24.

**User's first-pass observation.** *"I don't have anything to add
beyond our SQ14 discussion. Can you think of anything else?"* The
intuition that C2 largely overlaps SQ14 is correct, but a useful
sharpening surfaced through the back-and-forth that's worth capturing
because it directly clarifies what Test IV's β_3 measures.

**The discrimination/information-theoretic distinction sharpened.**

C2's framing presents a binary: is the distal-novelty mediator
"discrimination" or "information-theoretic"? Hofstra's analysis
structure resolves this in a specific way that requires precision —
and an initial overstatement on my part required correction by the
user.

**What Hofstra actually does.** Controls for distal novelty as a
**main-effect covariate** in regressions of career outcomes on
demographic status. The 3.5% → 9.5% gender discount (and 4.3% → 15%
impactful-novelty version) include distal novelty as a control. Main
text claims: *"These results hold over and above of the distance
between newly linked concepts"* (p. 9287).

**What Hofstra does NOT do (or at least doesn't headline).** Test
the **(demographic × distal-novelty) interaction** at the link
level. They don't formally verify that the distal-novelty → uptake
relationship has the same slope for majority-introduced and
minority-introduced links.

**Why this distinction matters.** A main-effect control adjusts for
the *average* distal-novelty effect on outcomes. It treats distal
novelty as if its effect were uniform across creators. After
main-effect adjustment, the residual demographic effect could be:

- **Pure "around-distal" residual** if interaction = 0: distal
  novelty operates equally for everyone, demographic discrimination
  works through OTHER channels.
- **Underestimated "through-distal" effect plus around-distal
  residual** if interaction < 0: demographic discrimination operates
  PARTLY through differential treatment of distal contributions,
  which the main-effect control absorbs imperfectly.

These two readings are observationally indistinguishable from
Hofstra's main-text analysis. The main-effect control is a partial
information-theoretic correction; the differential-discrimination
question requires the interaction test, which isn't formally
reported.

**The earlier overstatement and its correction.**

I initially said: *"The mediator is information-theoretic, NOT a
discrimination claim... it operates the same for majority-introduced
and minority-introduced links."* User pushed back: *"so are you
saying that Hofstra had already controlled for the information-
theoretic confound?"*

The corrected framing: Hofstra controls for the distal-novelty *main
effect* (partial information-theoretic control); they don't formally
verify uniformity-of-effect-across-groups (the interaction). My
earlier framing collapsed this distinction. The correction matters
because it directly determines what Test IV's β_3 measures
methodologically.

**ws2 lesson — Test IV's β_3 IS the missing interaction test.**

Test IV's persistence regression specification:

> log(1 + C_15) = α + β_1·N_p + β_2·T_p + β_3·(N_p × T_p) + controls + ε

- **β_1 (N_p main effect)** corresponds to Hofstra's information-
  theoretic mediator — the average effect of paper-level novelty on
  long-term-citation accumulation, regardless of team composition.
- **β_2 (T_p main effect)** corresponds to Hofstra's residual
  demographic effect after main-effect distal control — the
  "around-novelty-channel" team-diversity effect.
- **β_3 (T_p × N_p interaction)** is the test Hofstra doesn't run —
  whether team-diversity differentially modulates the novelty →
  long-term-citation relationship.

Substantive readings of β_3:

- **β_3 = 0**: novelty's long-term-uptake effect is uniform across
  team-diversity levels. Information-theoretic mediation operates the
  same for everyone; team-diversity effects (if any) operate through
  other channels. Hofstra's "main-effect control" assumption holds.
- **β_3 < 0**: diverse teams' novel papers get less long-term uptake
  than non-diverse teams' equally-novel papers. Differential
  discrimination operates *through* the novelty channel. The
  main-effect-control approach (Hofstra's) would underestimate the
  full demographic effect.
- **β_3 > 0**: diverse teams' novel papers get more long-term uptake
  than non-diverse teams'. Inverse-discrimination through the novelty
  channel; less commonly hypothesized.

**Test IV's design directly addresses C2's discrimination-vs-
information-theoretic question** — not because we anticipated C2
specifically, but because the interaction-term specification is
methodologically more rigorous than main-effect-only adjustment for
mediator effects. We're built to distinguish what Hofstra leaves
implicit.

**Pending batch addition (item 9 extension — Methods framing
paragraph):**

> *"Hofstra et al. 2020 control for distal novelty as a main-effect
> covariate when estimating demographic discounts in career outcomes;
> their main-text analysis treats the distal-novelty → uptake
> relationship as uniform across demographic groups (without
> explicitly verifying the assumption). Our Test IV persistence
> regression includes the (T_p × N_p) interaction term β_3
> explicitly, which directly tests the uniformity assumption
> Hofstra leaves implicit. β_3 ≠ 0 indicates that the novelty →
> long-term-citation relationship varies by team diversity — the
> discrimination-through-novelty-channel hypothesis the main-effect
> specification cannot distinguish from pure information-theoretic
> mediation."*

Three-sentence framing addition. No new analysis (the regression
specification is already committed). Sharpens what β_3 measures
substantively and ties it to the broader literature.

**One-sentence summary.** Hofstra's "control for distal novelty" is a
main-effect adjustment that doesn't test the (demographic × distal-
novelty) interaction; the discrimination-through-distal-channel
question is observationally indistinguishable from pure information-
theoretic mediation in their main analysis. Test IV's β_3 is the
interaction Hofstra doesn't run — methodologically more rigorous on
this dimension. Methods framing should make this explicit.

### On C3 — individual findings aggregated to team level

Working session with user, 2026-04-24.

**User's first-pass.** *"Not sure how to answer."* The three
aggregation patterns make different predictions and the data hasn't
spoken yet. Walkthrough lays out predictions, evidence, honest
expectation, and what each observed outcome would update us on.

**Three aggregation patterns, three predictions for Test IV's γ_1:**

| Pattern | Mechanism | Test IV γ_1 prediction |
|---|---|---|
| Pure additive | Individual contributions sum mechanically | γ_1 > 0, scaling with minority fraction in team |
| Actuator-override | Shared inputs (advisor, canon, training) average individuals to consensus | γ_1 ≈ 0 even though Hofstra's individual effect is real |
| Selection | Team formation correlates with topic, advisor, institution | γ_1 attenuates substantially under FE |

**Evidence for each:**

- **Pure additive**: Hofstra's individual finding survives multiple
  robustness checks; Page-Hong literature predicts compositional
  effects at team level; some scientometric work finds positive
  team-composition effects.
- **Actuator-override**: ws2's whole thesis is built around shared
  actuators producing homogenization; CS especially has dense
  actuators (deep learning canon, GitHub, conferences, advisor
  lineage chains); field-level homogenization is observable, teams
  are smaller-scale instances of same dynamic.
- **Selection**: team formation in academic science is highly non-
  random; demographic patterns correlate with subfield, advisor,
  institution; Hofstra's individual-level analysis controls for
  these but team-level analysis exposes within-team selection
  patterns.

**Honest answer: probably some mixture, with field-specific
variation.**

For CS specifically, actuator-override is plausible at moderate-to-
strong magnitude. The actuators are dense (transformer-architecture
canon post-2017, conference monoculture, lineage chains). γ_1 could
be substantially attenuated relative to Hofstra's individual
coefficient, possibly approaching zero in some specifications.

For Physics, actuators are weaker on average (more diverse subfields,
less hot-trend dominance). γ_1 could be larger than in CS, closer
to pure additive.

For both, selection effects will absorb some signal under FE — both
fields have non-random team formation correlated with subfield,
advisor, institution.

Most likely empirical outcome: **γ_1 ≠ 0 but substantially smaller
than pure-additive aggregation of Hofstra's individual coefficient
would predict, with magnitude varying by field (CS smaller than
Physics) and by control specification (smaller with FE than
without).**

**What each observed outcome would update us on:**

| Observation | Update |
|---|---|
| γ_1 > 0, stable across specifications, both fields | Pure additive holds; outsider vantage extends from individual to team level; ws2's actuator-override hypothesis weakened |
| γ_1 ≈ 0, both fields, all specifications | Actuator-override dominant; team dynamics flatten individual vantage; strongest support for ws2's central claim |
| γ_1 > 0 in Physics, ≈ 0 in CS | Field-specific actuator-override; CS's tight actuator network suppresses team-level signal; Physics's looser structure preserves it. Most informative for ws1 — actuator density is parametrically variable |
| γ_1 substantially attenuated by FE | Selection-driven; individual-level effect was confounded with team-formation patterns; outsider-vantage requires nuancing |
| γ_1 < 0 (diverse teams less novel) | Surprising, doesn't fit any pattern cleanly; suggests differential editorial filtering or systematic publishing disadvantage; would prompt re-examination of measurement chain |

**Connection to ws2 commitments.**

We're already set up to test all three patterns through Test IV's
regression structure. What would help discriminate:

**(1) Report γ_1 across multiple control specifications.** Same
sensitivity-analysis pattern as the SQ14-derived mediation-control
sensitivity (β_3 across specs). For γ_1:

- No controls (pure correlation)
- Year FE only
- Year + subfield FE
- Full control set (year + subfield + team size + reference count + team-level covariates)

**Diagnostic readings:**
- Stable γ_1 across specs → not selection-driven
- Collapsing γ_1 with FE → selection effects matter
- Persistent γ_1 ≈ 0 across all specs → actuator-override regardless of selection

**(2) Field-stratified reporting.** Already committed via cross-
field replication (CS + Physics). γ_1 difference between fields is
the actuator-density-comparison test. Already in plan.

**(3) Pre-registered interpretive readings.** Phase 0.2 pre-
registration should explicitly state what each γ_1 pattern is
interpreted as. Prevents post-hoc framing of unexpected results.

**Pending batch addition (item 7 / Test IV extension):** report γ_1
across the four control specifications listed above, alongside the
existing β_3 mediation-sensitivity reporting. Sensitivity-analysis
table column, not new analysis. Discriminates the three aggregation
patterns empirically.

**One-sentence summary.** Three aggregation patterns make different
predictions for Test IV's γ_1: pure additive (γ_1 > 0 scaling with
minority fraction), actuator-override (γ_1 ≈ 0 despite real
individual effect), selection (γ_1 attenuates under FE). Most likely
outcome is a mixture with field-specific variation (CS smaller γ_1
than Physics, attenuation under controls). Already-committed cross-
field replication tests actuator-density variation; new pending-
batch addition reports γ_1 across multiple control specifications
to discriminate the patterns. The four-quadrant interpretive grid
(γ_1 sign × persistence pattern from SQ7) extends naturally to
this discrimination.

### On C4 — demographic inference accuracy and URM validity

Working session with user, 2026-04-23.

**Distinctive from SQ13.** SQ13 was about the structural problem of URM
as a compositional aggregate. C4 is more pointedly methodological: does
the URM-vs-white discount finding actually survive given the
catastrophic AA/NA accuracy, and (importantly for ws2) does our
weight-by-confidence approach solve the problem or just make uncertainty
visible?

**Sensitivity analyses that would clear Hofstra's URM-vs-white contrast.**

Hofstra mentions one of these in passing (SI p. 14–15): "our main
substantive conclusions and inferences are robust if we only consider
those students whose names overwhelmingly occur within one rather than
multiple races." This is a high-confidence-cases-only restriction. The
fact that they report it as a footnote rather than headlining suggests
the substantive conclusions hold, but the analysis isn't given the same
prominence as the main findings.

Three sensitivity analyses that would clear the contrast more
rigorously:

1. **Stratified by per-group accuracy.** Run the URM-vs-white discount
   separately for high-confidence URM cases (probability > 0.9) vs. low-
   confidence URM cases. If the discount holds in both, robust. If it
   holds only in low-confidence, measurement error is plausibly driving
   the result.
2. **Bounded under assumed misclassification patterns.** Compute the
   discount under different assumed misclassification rates for each
   subgroup. If the discount remains for all reasonable misclassification
   scenarios, it's robust.
3. **Decompose URM into Hispanic-only and AA-only contrasts where
   inference allows.** With ~83% Hispanic accuracy, a Hispanic-only-vs-
   white contrast is more defensible than the pooled URM contrast.

Hofstra's "overwhelmingly one race" restriction is approximately #1 in
compressed form. They claim the substantive conclusion is robust to
this restriction. Without seeing the actual numbers, this is a vague
reassurance.

**Does ws2's weight-by-confidence solve the problem, or just make
uncertainty visible?**

Honest answer: mostly the latter. Weight-by-confidence is a structural
improvement over Hofstra's "treat all classifications as equally
certain" approach because it propagates inference uncertainty into our
downstream estimates (wider CIs for low-confidence inferences). But it
doesn't fix the underlying problem in two specific ways:

- A 74% AA inference is still 74% accurate, regardless of how we weight
  it. Weight-by-confidence makes the lower confidence visible but
  doesn't generate a more accurate inference.
- Aggregate findings still mix high- and low-confidence cases under our
  reporting. Even with weighted CIs, the aggregate point estimate is
  contaminated by misclassification at rates we can't fully bound.

**What would actually solve the problem:**

1. **Better inference at the source.** NamSor's per-region accuracy is
   mostly higher than Census-based methods, but still imperfect. ORCID
   self-reported demographic data has higher accuracy but limited
   adoption (~30–40% of recent researchers). We're committed to NamSor
   + Genderize, which is better than Hofstra's stack but not a complete
   solution.
2. **Restrict analyses to high-confidence cases only** (lose statistical
   power; introduce sample selection if confidence varies by
   demographic).
3. **Bayesian models propagating inference uncertainty into all
   downstream estimates** — methodologically elegant but computationally
   heavy at our scale.

**Sharpening for the C4 walkthrough:** weight-by-confidence is better
than treating inferences as certain (Hofstra's approach), but it's not
a solution. It's an honest accounting of uncertainty that doesn't
pretend to fix the underlying inference quality. The Methods section
should acknowledge this distinction — we're not claiming our
demographic inference is reliable; we're claiming we report uncertainty
more transparently than Hofstra does.

**Pending batch addition:** small Methods-paragraph extension —
explicitly state that weight-by-confidence is an uncertainty-
propagation policy, not an inference-quality fix. Three sentences. Low-
cost.

### On C5 — diachronic embedding robustness

Working session with user, 2026-04-23.

**Distinctive from SQ10.** SQ10 unpacked Hofstra's r=0.931 single-year
validation as best-case-by-construction. C5 is the hypothetical: which
of Hofstra's specific findings would change under proper diachronic
embeddings, and which would be stable? This is genuinely useful to
think through because it tells us where the embedding choice is
actually load-bearing for Hofstra's substantive claims.

**What would change under proper diachronic embedding.**

- **The distal-novelty operationalization itself.** Distal novelty is
  an embedding-distance metric. Per-era embeddings would change which
  concept-pairs are classified as "distal" — particularly in earlier
  decades where vocabulary differs from the global average.
- **The gender-distal-novelty pattern (Figure 3C).** If women's distal
  novelty is concentrated in specific eras (e.g., post-2000 cross-
  disciplinary work), per-era embeddings might recalibrate which
  decades show the gender distal-novelty gap most strongly. The
  aggregate finding might survive but the temporal distribution would
  shift.
- **The partial-mediation argument (Figure 4 / SQ14).** Partly affected
  via redefinition of distal novelty. If "distal" gets re-classified,
  the mediator coefficient changes, and the residual demographic
  discount changes correspondingly.
- **Boundary-year findings specifically.** Pre-1990 distal-novelty
  estimates are most affected. The pre-1990 portion of the gender-
  distal-novelty finding is on shakier ground than the post-1990
  portion.

**What would stay stable.**

- **Per-individual novelty count (# new links).** Doesn't depend on
  embedding distance at all. Just first-pairwise-co-occurrences in the
  abstract. Stable.
- **Per-individual uptake count (impactful novelty).** Doesn't depend
  on embedding distance. Stable.
- **The headline diversity-innovation finding** ("minorities introduce
  more novel concept-pairs"). Stable, because it's based on novelty
  count not distance.
- **The career discount, controlling for distal novelty.** Mostly
  stable — the residual demographic effect after distal-novelty
  mediation isn't directly embedding-dependent (only the mediator is).

**What this tells us.**

The diachronic embedding choice is most load-bearing for the distal-
novelty mediator and least load-bearing for the headline finding. If
Hofstra's embedding methodology is flawed, the mediator argument is
suspect; the rest is more robust than the embedding criticism would
suggest.

This is actually generous to Hofstra — their core finding survives
even under aggressive criticism of their embedding methodology. The
criticism applies to a specific component (Figure 3 distal-novelty
argument) more than the headline.

**For ws2 specifically.**

Our drift-mitigation ladder is built precisely to handle the analog
problem. Test IV primary N_p uses one global SPECTER2 (similar to
Hofstra), but Mitigation 4 (anchor-projection) creates a drift-robust
subspace, and Stage 3 Flavor A creates per-era alternatives if the
drift-pilot result indicates need.

**Methodological vindication, not new commitment.** SQ10 already
covered this. C5's marginal contribution: clarifies that the embedding-
drift concern primarily affects mediator analyses, not core production-
and-uptake findings. Useful for thinking about which of our own
analyses are more vs. less drift-vulnerable.

### On C6 — combinatorial vs. geometric novelty

Working session with user, 2026-04-24.

**The hidden asymmetry on new-term introductions.** Close reading of the
FREX + PMI pipeline reveals that Hofstra's novelty metric operates over a
concept vocabulary that is *fixed at corpus level* — defined once from the
full 1977–2015 corpus via K=500 STM + top-500 FREX terms per topic. A term
doesn't enter the vocabulary unless it clears the FREX weighting threshold
across the whole corpus; a genuinely new term (below the threshold) is
invisible to the measure. But a term that is FREX-valid yet rare enough
to first appear in a thesis in a particular year gets credit combinatorially:
every pair (new_term, existing_concept) becomes a "first pairwise
co-occurrence" simultaneously. A thesis introducing a rare-but-valid term
with 20 pre-existing co-concepts scores 20 new links at once; a thesis
creatively re-linking two already-common terms scores one. This asymmetry
isn't called out in the paper.

**Implications for ws2's Test IV.**

- **Primary N_p (cosine distance to citation-context centroid) doesn't
  inherit this asymmetry.** A paper's distance from its citation context
  is geometric — one very-distant contribution and many moderate-distance
  contributions can produce the same N_p. No combinatorial inflation.
- **Tertiary N_p (Uzzi-style reference-pair novelty, Stage 3) WOULD
  inherit the asymmetry** by default. A paper citing two pre-existing
  references for the first time scores 1 atypical combination; a paper
  citing a brand-new reference with 20 others scores 20.
- **Proposed correction for Stage 3 tertiary:** down-weight
  first-co-occurrences by the rarer concept's frequency in the reference
  pool. Concretely: for each first-co-occurrence pair (a, b), contribute
  min(1, freq(a)/threshold + freq(b)/threshold) rather than 1. This
  gives credit for introducing new references but doesn't let k pair-ups
  with a single new reference dominate. Pre-register in Phase 0.2.

**Example where combinatorial and geometric diverge.** A physics thesis
in 1985 that uses the term "inflaton" (newly FREX-valid in the vocabulary
because inflation theory papers appear post-Guth 1981) alongside 20 pre-
existing standard-cosmology terms. Combinatorial novelty: 20 new links.
Geometric novelty (cosine to citation context): modest if the thesis's
citations are well-represented in early cosmology and inflaton sits near
them in embedding space. Conversely, a 1995 thesis using two long-
established concepts ("entropy" and "information") in a novel argument
about black-hole information paradox scores 1 new link combinatorially
but potentially very high geometrically (the combined embedding is far
from either concept's established contexts).

Which matches reviewer intuition? Depends on the reviewer — combinatorial
catches "introduces a new building block," geometric catches "bridges
conceptual regions." Both are real kinds of novelty. Test IV primary
uses geometric; Stage 3 tertiary (if pursued) should use a down-weighted
combinatorial to capture what geometric misses.

### On C7 — innovation discount interpretation

Working session with user, 2026-04-24.

**The adjudication the challenge asks for isn't fully possible from
observational data.** The discrimination reading and the quality reading
of Hofstra's innovation discount are observationally equivalent under
residualization-based bias inference. To adjudicate between them, you
need *counterfactual* evidence: what would adoption look like for the
same work, under the same network conditions, absent the structural
processes Hofstra hypothesizes?

That counterfactual is not producible from observational scientometric
data, because:

1. **The counterfactual requires making implicit structural assumptions
   explicit.** To ask "what would adoption be without bias?" you need a
   model of what bias is — which structural channels operate, with what
   strength, on what subpopulations. Hofstra's residualization treats
   *demographic residuals after controlling for measured quality proxies*
   as an operational definition of bias, but this is circular: the
   definition presupposes that demographic effects on adoption, after
   controls, *are* bias rather than unmeasured quality. Under alternative
   structural assumptions, the same residual could be genuine quality
   differences.

2. **The counterfactual requires varying structural assumptions.** Once
   you have a formal model of which structural channels operate and with
   what strength, you can ask "what changes if we remove or modify channel
   X?" But this is an interventional move, not a measurement. You can't
   perform it on observed data; you can only simulate it on a model whose
   structure you've specified explicitly.

This is what justifies the three-whitespace program structure:

| Whitespace | Method | What it can establish | What it can't |
|---|---|---|---|
| **ws2** (empirical) | Observational scientometrics | The phenomenon; quantitative constraints on any structural model; mechanism-space narrowing via subfield test | Counterfactuals; causal identification; true adjudication of discrimination vs. quality |
| **ws3** (theoretical) | Formal model of cumulative preservation (C) vs. per-capita variance generation (V) | Plausible structural stories; identifiable parameters; qualitative regimes separating mechanism classes | Whether any particular story actually operates; which parameter values empirical data supports |
| **ws1** (simulation) | Agent-based simulation of actuator-homogenization dynamics | Counterfactual trajectories under explicit structural assumptions; intervention effects; structural sensitivity | External validity of the simulation's structure to real-world science |

Each whitespace's weakness is another's strength. Together, they
triangulate on the causal question in ways no single layer can alone.

**What ws2 specifically contributes given this limit:** three things
more precise than "documents the phenomenon."

(i) **Phenomenon-level falsification.** If Tests I–III show no divergence,
or if Test IV's γ₁ is substantially positive (diverse teams → more novel
papers, in line with Hofstra at team level), then the actuator-
homogenization structural story is directly challenged. This matters
without requiring causal identification: the data refutes the structural
claim even if it doesn't identify the true alternative.

(ii) **Quantitative anchoring for ws1.** Whatever structural story ws1
eventually simulates must reproduce ws2's surface markers — the 3-panel
time series, the subfield mechanism results, the Test IV cross-sectional
regression. Ws2's findings become the empirical targets any
counterfactual simulation has to match. This turns ws2 from a standalone
empirical paper into foundational infrastructure for ws1.

(iii) **Mechanism-space narrowing.** The subfield mechanism test (canon-
concentration → divergence magnitude) isn't a causal claim, but it's
evidence about *where* structural processes plausibly concentrate. If
γ₁ > 0 in the subfield regression, actuators operate more strongly in
canon-concentrated subfields; ws1's simulation space narrows to models
with heterogeneous actuator density by subfield. If γ₁ ≈ 0, a different
model class is needed.

**Implication for ws2's framing.** The Methods and Discussion sections
should make this epistemic scope explicit, not hide it:

- Acknowledge that novelty and adoption are surface markers, not direct
  measurements of innovation.
- Acknowledge that the counterfactual adjudication Hofstra implicitly
  invokes requires structural simulation (ws1 in our program).
- Position ws2 as documenting the phenomenon and narrowing the space of
  plausible structural stories, not as identifying the correct one.
- Flag this as the canonical honest framing for observational
  scientometric work on bias-vs-quality — a move readers of Hofstra, the
  Evans lab, and Azoulay's work will recognize and appreciate.

**Where this insight goes durably:** this Discussion Note, plus a new
"Epistemic scope and limits" section in `whitespace_2/docs/conceptual.md`,
plus a layered-epistemics argument added to
`docs/program/research_program_overview.md` (the program-level rationale
for three whitespaces rather than one).

### On C8 — ProQuest-WoS matching error compounding

(Pending.)

### On C9 — dissertations vs. papers

Working session with user, 2026-04-23.

**Framing question.** Hofstra studies dissertations — the thing a single
person writes at the start of a research career. ws2 studies papers — the
thing a team writes across a career-spanning corpus. C9 asks whether the
"outsider vantage" mechanism — the substantive engine of Hofstra's
diversity-innovation finding — transfers cleanly to teams.

**My initial framing was wrong, and the user pushed back.** I had
characterized within-team dynamics as "averaging individual vantages
toward consensus" — i.e., advisor effects, communication norms, decision-
making protocols, and peer-review preferences would dilute an outsider
contributor's distinctive vantage when integrated into a team product.
The user's pushback: *that picture is not accurate for CS or physics.*
In hierarchical-authorship technical fields, first authors and last/PI
authors carry disproportionate weight in shaping the paper's intellectual
content; the rest of the author list contributes more narrowly (specific
analyses, code, data, infrastructure). A "team-averaged" characterization
is closer to the egalitarian-norm fields (some areas of theory, some
math) than to the modal CS/physics paper.

**Reframed mechanism.** This means the outsider-vantage transfer from
dissertation to paper is *more direct than I'd suggested*, with two
caveats:

1. **Position of the demographically-distinct author matters.** An
   outsider in the first-author or last/PI seat carries their vantage
   into the paper's conceptual framing with high fidelity. An outsider
   in a middle-author seat contributes to a team product whose framing
   is set elsewhere — the vantage is more attenuated.
2. **Authorship-norm regime varies by subfield.** High-energy physics
   (alphabetical authorship, mega-collaborations) is structurally
   different from condensed-matter physics or experimental CS subfields
   where first/last author positions are intellectually load-bearing.
   Pooling all team papers under a single T_p operationalization
   collapses across these regimes and likely loses signal.

**Three authorship patterns in CS/physics.** The literature treats this
as a known taxonomy:

- **Hierarchical (first-author-prominent):** modal in CS, much of
  experimental physics, condensed-matter, biology-adjacent areas.
  First author = lead intellectual contributor; last author = senior
  supervisor / PI. Middle authors contribute specific analyses or
  infrastructure. **Implication for T_p:** weight first and last authors
  more heavily; middle authors less.
- **Alphabetical:** dominant in high-energy physics (especially
  experimental, ATLAS / CMS-style), some areas of math, theoretical CS
  partially. Author order conveys little about contribution. **Implication
  for T_p:** uniform weighting is appropriate but information per author
  is diluted in the limit of mega-author papers (1000+ authors); T_p
  approaches the field-level T as team size grows, which is a different
  estimand.
- **Egalitarian:** some theory subfields, some math, occasional CS
  collaborative work. Small teams, equal intellectual contribution.
  **Implication for T_p:** uniform weighting maps directly to the
  team-product diversity claim.

**Decision: multi-operationalization of T_p as co-primary, not
sensitivity-only.** Because the authorship-norm regime is itself an
empirical question per subfield, the right move is to compute T_p
multiple ways and report co-equally rather than declaring one canonical
operationalization and treating others as robustness:

- **T_p_full:** Rao's Q over the full author team with uniform weights.
  This is the "team-as-collective" operationalization; matches the
  alphabetical-norm regime cleanly and serves as the pooled-corpus
  primary. Approximates the field-level composite at small team sizes.
- **T_p_first:** demographic feature vector of the first author only.
  This is the "lead-intellectual-contributor" operationalization; matches
  the hierarchical-norm regime cleanly and gives the most direct
  dissertation-to-paper transfer of Hofstra's finding (single individual
  → team product is intellectually attributed to a single individual).
- **T_p_last:** demographic feature vector of the last author only.
  Reported as sensitivity, not co-primary. Last-author position is more
  about supervision/funding than about novelty-generating intellectual
  vantage; expected to behave differently from T_p_first.
- **T_p_weighted:** Rao's Q with first/last weighted higher than middle
  authors (e.g., 0.4 first, 0.4 last, 0.2 split among middles, with
  weight scheme pre-registered). Reported as sensitivity. Captures the
  hierarchical-norm intuition without a binary first-vs-rest cut.

**Subfield-stratified analysis.** Test IV regressions are fit:
(a) pooled within field (CS, Physics) with T_p_full, T_p_first, T_p_last,
T_p_weighted as four separate co-reported estimates;
(b) stratified by subfield where authorship-norm regime is identifiable
(high-energy physics vs. condensed-matter vs. experimental CS vs.
theoretical CS), so that within-stratum T_p is interpretable. Report
the four operationalizations × stratification grid; let the agreement
or disagreement across cells be informative.

**Pre-registered interpretive readings of γ₁ patterns.** Because
multi-operationalization risks "harvest the most interesting story"
post-hoc, pre-register specific interpretations:

- **γ₁ > 0 across all four operationalizations + all subfield strata:**
  strongest pro-diversity finding; team diversity translates to novelty
  regardless of authorship-norm regime. Hofstra at team level, replicated.
- **γ₁ > 0 for T_p_first but ≈ 0 for T_p_full:** outsider-vantage transfer
  works specifically at the lead-author level; diluted by team integration.
  Consistent with a weakened version of the consensus-averaging story
  that I'd initially overgeneralized — restricted to integration effects,
  not assumed pervasive.
- **γ₁ > 0 in egalitarian/hierarchical strata but ≈ 0 in alphabetical
  (HEP):** team-product novelty mechanism operates only when team
  composition is intellectually load-bearing; mega-collaborations are
  structurally different.
- **γ₁ ≈ 0 across the board:** diversity-novelty link is weak at the
  team-product level regardless of operationalization; the
  dissertation-finding does not transfer. Substantively interesting null;
  publishable as such.
- **γ₁ < 0 for T_p_full but γ₁ > 0 for T_p_first:** diverse teams
  *integrate* away novelty even when an individual outsider in the lead
  seat would produce it. This is the version of the actuator-homogenization
  story that survives the framing correction — not "consensus averaging"
  in general, but specifically: integration mechanisms operating on
  middle-author input dilute the lead-author's distinctive vantage.
  Worth distinguishing from the simpler "no transfer" null.

**What this commits us to.** Test IV ships with multi-operationalization
co-reporting and subfield stratification as primary, not as Stage 3
robustness extensions. This raises Test IV's specification complexity
but is the right call: the alternative (single operationalization,
collapsed across authorship-norm regimes) bakes in an assumption that
the user identified as wrong for our fields. Better to surface the
ambiguity in the design than to launder it into a single number.

**Connection to ws2 commitments.**

- **Test IV regression** now reports four co-equal estimates of γ₁ per
  field × per subfield stratum.
- **Phase 0.2 pre-registration batch:** add T_p multi-operationalization
  spec, subfield stratification scheme, and the interpretive grid above.
- **Methods framing (Discussion):** explicitly acknowledge that "team
  diversity" is a multi-headed construct in fields with heterogeneous
  authorship norms; the four operationalizations are not redundant
  measures of the same thing — they answer subtly different substantive
  questions.

**Action items from this session:**

1. Add T_p multi-operationalization (T_p_full + T_p_first co-primary;
   T_p_last + T_p_weighted as sensitivity) to Phase 0.2 pre-registration
   batch.
2. Add subfield-norm stratification scheme to Phase 0.2 batch.
3. Add the five-cell pre-registered interpretive grid to Phase 0.2
   batch.
4. Update Methods framing: "team diversity" is multi-operationalized;
   no single canonical T_p.

**Left open for future discussion:**

- How to operationalize subfield authorship-norm regime empirically
  (mean Spearman correlation between author-list position and
  contribution-statement keywords? Self-reported convention from the
  field's flagship journals? Manual subfield-by-subfield assignment?).
  Decide in early Stage 2 once the OpenAlex sample is in hand and we
  can inspect author-list distributions per subfield.
- Whether T_p_weighted's specific weight scheme should be 0.4/0.4/0.2
  or empirically tuned (e.g., calibrated against contribution statements
  on the subset where they exist). Empirical tuning is appealing but
  introduces a researcher-degree-of-freedom; default to pre-registered
  fixed weights unless calibration meaningfully outperforms.
- Whether to add a fifth operationalization based on contribution
  statements where available (post-2010 papers in journals that require
  them). Likely too narrow a coverage to support a primary Test IV
  estimate; possibly useful as a diagnostic on the smaller subset.

### On C10 — boundary conditions for time-series restrictions

Working session with user, 2026-04-25.

**Reframing the question.** Hofstra's "1982–2010 with 5/5 buffer" choice
bundles two distinct boundary issues that should be disentangled before
asking whether ws2 should adopt an analogous restriction:

1. **Data-quality lower bounds** (pre-X year cutoffs): when does the
   corpus become reliable enough to compute the metric at all? Driven
   by abstract coverage, classifier drift, reference-list completeness.
2. **Process buffers** (uptake / accumulation windows): how long does
   a paper need on either side of its publication date for the metric
   to stabilize? Driven by the diffusion process of ideas.

These have different right answers and are independent. Most ws2 tests
need (1) but not (2); only the persistence-class tests and the Stage 3
U-M-S tertiary need (2).

**The substantive case for "let the data tell the story" on buffers.**
Uptake rates vary across regimes by orders of magnitude:

- **Field-level:** physics has rapid theory propagation; sociology has
  slower uptake; some areas of math have decade-scale rediscovery.
- **Subfield-level within physics:** high-energy physics is fast (large
  collaborations, rapid preprint diffusion); condensed-matter is
  moderate; pure-math subfields are slow.
- **Era-level:** pre-internet, uptake was slow; post-arXiv (~1991 in
  physics, late 1990s in CS), uptake accelerated; in ML post-2012,
  uptake is now subannual for breakthroughs.

A single 5-year (or 10-year) buffer is wrong-by-construction across
these regimes. It either truncates fast-uptake data unnecessarily or
undermeasures persistence in slow-uptake regimes. This is the same
multi-headed-construct issue we faced for Test IV T_p (C9): when the
underlying construct varies by regime, surface the multi-headedness in
the design rather than collapse it into one number.

**Countervailing pressures for committing to a primary.**

- *Cross-paper comparability.* Reviewers want a headline number to
  compare against Hofstra and the existing literature. A
  pre-registered C_10 primary lets us say "Hofstra-style replication:
  γ₁ = X" while showing the multi-window grid alongside.
- *Researcher-degree-of-freedom risk.* "Let the data tell the story
  via empirical uptake-half-life per stratum" can devolve into
  post-hoc tuning. Pre-registering a primary forces commitment.

**Per-test resolution.**

| Test | Boundary type | Action |
|---|---|---|
| Tests I–III (aggregate divergence) | Data quality only — no buffer needed | Already locked: post-1990 primary, pre-1985 preliminary, pre-1990 with disclaimer (desiderata §11, Phase 0.1 §13). No change. |
| Test IV primary (centroid distance) | Data quality only | <5-references flag for robustness-only subset already locked. No change. |
| Test IV Persistence Extension | Buffer applies (uptake) | C_10 pre-registered primary; C_5 and C_15 co-equal in the same table; empirical uptake-half-life diagnostic per field × subfield × era. |
| Item 11 (Production-capture) | Buffer applies (uptake) | C_10 primary (truncates 2014); C_5 (truncates 2019) and C_15 (truncates 2009) reported alongside. |
| Stage 3 U-M-S tertiary novelty | Buffer applies (accumulation) | Pre-register 5-year accumulation buffer: 1975+ for U-M-S computation; 1970–1974 papers excluded from this operationalization. |

**Pre-registered interpretive grid for window-disagreement patterns
(parallel to Test IV T_p γ₁ grid from C9).**

- γ₁ stable across C_5/C_10/C_15 → finding is robust to operationalization
  of "uptake."
- γ₁ > 0 at C_5 but ≈ 0 at C_15 → diverse-team novelty has a "fast
  spike" pattern; doesn't durably persist. The "surface novelty"
  reading from C11.
- γ₁ ≈ 0 at C_5 but > 0 at C_15 → diverse-team novelty is slow to be
  picked up but durable. The "discrimination → eventual rediscovery"
  reading from C11.
- γ₁ stable in fast-uptake strata (HEP, ML-post-2012) but unstable in
  slow-uptake strata → finding generalizes only where uptake is fast.
- γ₁ unstable across windows in *all* strata → multi-headed construct;
  the persistence-class question is itself ill-posed at this resolution.
  Substantively interesting; publishable as an honest null on
  measurement.

**Methods-framing commitment.** Add a Methods paragraph stating that
**windows are part of the estimand, not nuisance parameters**.
Different windows define different substantive questions ("early hot
finding" vs. "durable contribution"). The multi-window grid is a
deliberate move away from collapsing these into one number, parallel
to the T_p multi-operationalization for team diversity. The empirical
uptake-half-life diagnostic transparently anchors which window is apt
for which stratum without giving the analyst post-hoc freedom to tune
the primary.

**What this commits us to (action items for Phase 0.2 batch).**

1. Test IV Persistence: keep C_10 primary; report C_5/C_10/C_15 as
   co-equal columns, not sensitivity-only. Add empirical uptake-
   half-life diagnostic per stratum.
2. Item 11 (Production-capture): same multi-window co-reporting as
   Test IV Persistence.
3. Pre-registered interpretive grid for window-disagreement patterns,
   per the table above.
4. Stage 3 U-M-S tertiary: pre-register 1975+ accumulation buffer.
5. Methods-framing paragraph: windows-as-estimand.

**Left open for future discussion.**

- How to operationalize the empirical uptake-half-life diagnostic.
  Candidate: per (field × subfield × decade) cell, fit a citation-
  curve and report the year by which 50% of eventual C_15 has
  accumulated. Pre-register the operationalization in Phase 0.2.
- Whether to add an even longer window (C_20, C_25) for slow-uptake
  strata. Possibly useful but truncates the analysis window further
  (C_25 → papers ≤1999 only, losing 25 years of recent data). Decide
  after pilot uptake-half-life results land in Stage 1.

### On C11 — test-of-time / persistence

Working session with user, 2026-04-24.

**Centrality ranking agreed:**

- **Diversity-innovation question broadly: high centrality.** Persistence
  is how you adjudicate between the "discrimination" and "surface-novelty"
  readings of Hofstra's innovation discount. Without it, the two are
  observationally equivalent at 5–15 year windows.
- **Test IV interpretability: moderate centrality.** Without persistence,
  γ₁ conflates "diverse teams produce novel work that shapes the field"
  with "diverse teams produce weird papers that flame out." With
  persistence, we resolve four distinct cases (see below).
- **Aggregate Tests I–III: low centrality.** Persistence doesn't naturally
  fit. The aggregate divergence tests operate on full-corpus annual
  diversity metrics; weighting by per-paper persistence would be a
  different paper.

**Four-case interpretive table (γ₁ sign × persistence pattern):**

| | high-N_p papers persist | high-N_p papers fade |
|---|---|---|
| γ₁ > 0 | Diverse teams produce durable novelty. Strong pro-diversity reading, aligns with Hofstra at team level. | Diverse teams produce surface novelty. Finding weaker than appears; reception-side actuator-homogenization gains footing. |
| γ₁ < 0 | Diverse teams produce less novelty; what they do produce is durable. Surprising; doesn't fit actuator-homogenization cleanly. | Diverse teams produce less novelty AND it fades. Strongest actuator-homogenization reading. |

Without persistence, we collapse 1+2 and 3+4. With it, all four cases are
distinguishable — substantively different stories.

**Operational design agreed for Test IV Persistence Extension (Stage 3
pre-registration):**

- **Variables:** per paper p, compute C_k(p) for k ∈ {3, 5, 10, 15};
  Persistence(p) = C_10(p) / C_3(p).
- **Regression 1 (direct interaction):**
  log(1 + C_15(p)) = α + β_1·N_p + β_2·T_p + β_3·(N_p × T_p) + controls
  + year-FE + subfield-FE + ε. Test β_3 sign.
- **Regression 2 (persistence ratio):**
  Persistence(p) = γ_0 + γ_1·N_p + γ_2·T_p + γ_3·(N_p × T_p) + controls +
  FE + ε. Test γ_3 sign.
- **Controls:** team size, references, mean career stage, mean prestige,
  paper age, field, subfield FE, year FE.
- **Standard errors:** double-clustered by lead author and subfield
  (consistent with Test IV primary).
- **Scope constraint:** persistence needs ≥10-year lookahead → analysis
  window truncates at ~2014 papers. Pre-register this restriction. 2015–
  2024 papers excluded from persistence extension (still in primary Test
  IV). Roughly 40 years of papers remain for persistence (1975–2014).
- **Left-censoring:** OpenAlex citation-indexing completeness improves
  over time. Control for per-era citation-coverage rate in Regression 1
  (add `coverage_rate(year)` as a control).
- **Effort:** ~1 week Stage 3, uses existing OpenAlex data, no new API
  calls.

**Action items from this session:**

1. Add Test IV Persistence Extension to Phase 0.2 pre-registration next
   batch of plan amendments.
2. Update phase-0.1-plan.md's "Open decisions deferred" → Test IV
   specification with the persistence extension.
3. Note that this extension directly engages 13-B (demographic-
   diversification-as-cosmetic) — the persistence dimension is what
   separates "cosmetic" (surface novelty that fades) from "substantive
   but under-rewarded" (durable novelty under-adopted).

**Left open for future discussion:**

- Whether to use log(1 + C_15) or a different transformation for highly
  right-skewed citation counts (e.g., zero-inflated negative binomial).
- Whether `C_10/C_3` is the best persistence ratio or something like
  area-under-citation-curve would be cleaner.
- Whether to pre-register *any* expected direction for β_3 and γ_3, or
  leave as two-sided exploratory. User prior is left-leaning (top-left
  quadrant) but explicitly acknowledged as too-early to anchor
  pre-registration on.

---

## Study Question Walkthroughs

Answers to the Study Questions worked through collaboratively in review
sessions. Each entry preserves the arc of initial intuition → sharpening
→ final version, because the sharpening is often as instructive as the
answer. Questions not yet worked through are marked `(Pending)`.

### SQ1 — What does "novelty" mean operationally in this paper? Give an example from Figure 1

Working session with user, 2026-04-23.

**User's first pass.** Novelty = creation of a new edge (as determined
by STM/FREX) between already-existing concept nodes, introduced through
the thesis work.

**Sharpened version.** Three precisions to the initial framing:

1. The operation is **first-time pairwise co-occurrence**, not
   "edge creation" in a graph-building sense. For each thesis, count
   pairs of FREX-valid concepts that co-appear in the abstract for the
   first time in the 1977–2015 corpus. The graph metaphor is useful
   intuitively but the operation is a set-of-pairs comparison, not a
   graph-construction procedure.
2. **PMI filter.** Not every pairwise co-occurrence counts. They apply
   a pointwise-mutual-information significance filter (PMI = log[Pr(a,b)
   / (Pr(a) × Pr(b))]) to drop co-occurrences that happen by chance
   given base rates. Also require each term to appear in ≥10 theses
   corpus-wide.
3. **Abstract-level, not full-text.** The measurement is on dissertation
   abstracts only (~10 sentences). Co-occurrences in the body that
   don't appear in the abstract don't count.

**One subtlety about "already-existing."** The FREX vocabulary is
defined once over the entire 1977–2015 corpus, not accumulated over
time. So a 1985 thesis that uses a vocabulary-valid term T for the
first time in any thesis gets credit for every pair (T, existing_concept)
simultaneously. This hidden combinatorial asymmetry (caught in C6 of
the Challenge Corner) inflates credit for papers introducing a
vocabulary-first term. The initial "already existing nodes" framing is
technically correct given how the vocabulary is defined, but worth
remembering that "existing in the vocabulary" ≠ "previously seen in
any thesis."

**Figure 1 example — Donna Strickland (Panel E).**

- **Thesis:** "Development of an Ultrabright Laser and an Application
  to Multiphoton Ionization" (1989).
- **New link introduced:** `grate` ↔ `stretch` (grating and stretching,
  in the specific physical-optics sense).
- **Why it's novel under the measure:** both concepts were FREX-valid
  (they appear across the corpus), but no prior thesis from 1977–1988
  had both appearing together. Strickland's thesis is the first
  pairwise co-occurrence.
- **The substantive content:** this link corresponds to chirped pulse
  amplification — stretching a laser pulse via a diffraction grating
  before amplifying, then recompressing. The technique won Strickland
  and Mourou the 2018 Nobel Prize in Physics.
- **Uptake:** 22 subsequent theses used the link.

**What the example illustrates well.** A single new link can be
vastly more consequential than the count (1) suggests — because the
count collapses the *meaning* of what was linked. Hofstra's measure
doesn't privilege "important" links at the metric level; weight comes
from the uptake layer (22 uses vs. median 0.333 for new links).

**What the example doesn't illustrate.** The combinatorial asymmetry
issue (Strickland linked two concepts both already in circulation);
cases where PMI filtering is load-bearing (this link is technical
and semantically coherent, passing the filter easily).

---

### SQ2 — What's the "paradox" in the title? State it in your own words

Working session with user, 2026-04-24.

**User's first pass.** The paradox is the fact that the diversity-
enhancing minority itself doesn't reap the (supposed) benefits of
overall greater diversity, thereby serving as a positive externality
to the until-then-less-diverse group (likely the majority in many
cases).

**Sharpened version — Hofstra's premise-conflict structure.** The
paradox is best understood as a conflict between three statements
that can't simultaneously hold:

1. **Diversity breeds innovation.** Demographically underrepresented
   groups produce more novel scientific work (demonstrated in the paper).
2. **Innovation predicts career success.** Novelty and impactful
   novelty are what gets you a faculty job (demonstrated in the paper
   at aggregate level).
3. **Minorities have worse careers.** Underrepresented groups face
   persistent career disadvantage (prior literature + confirmed here).

These three can't all hold *if we assume innovation→career is the
same mechanism for everyone.* (1) + (2) together imply minorities
should have *better* careers — they produce more of what predicts
success. (3) says they don't.

Something has to give. Hofstra's resolution: **(2) is not universal.**
The innovation→success conversion rate differs by demographic group:

- Minorities' novelty is adopted by others at lower rates (the
  "impactful novelty" discount).
- Even holding novelty AND uptake constant, their career returns are
  lower (the pure career discount — Figure 4).

**What the user's externality framing adds.** Directionally right and
substantively interesting. It reframes the question from "why don't
minorities succeed?" to "who IS capturing the value minorities
generate?" Possible answers:

- **The collective scientific enterprise** — the field as a whole
  advances faster when demographic inputs diversify; benefit is
  public/diffuse.
- **Majority individuals** — who work in the same institutions,
  benefit from the broader talent pool, get more research
  opportunities from having diverse colleagues.
- **Institutional actors** — universities, funders, awards-committees
  capture reputational gains from diversity-associated innovation
  without distributing the rewards back to producers.

The externality framing isn't quite what Hofstra argues explicitly, but
it's a natural extension and arguably a deeper reading of the
mechanism. They document the discount; the externality reading asks
where the value goes when it's not captured by the producers.

**Note on externality-framing limits (surfaced later in the session).**
The externality framing requires being able to separate "value
produced" from "value captured" — which Hofstra's per-paper design
does (novelty count vs. uptake vs. career outcome). Ws2's Tests I–III
*aggregate* design cannot do this cleanly, because aggregate semantic
diversity doesn't decompose into per-paper production-and-capture
stories. The externality framing applies at Test IV (per-paper) scale
and at item 11's production-capture aggregate decomposition, but not
at Tests I–III as originally specified. See Synthesis Pointer 11 for
the scale-difference framing.

**Tight one-sentence versions.**

- Hofstra's structural reading: *"Diversity produces the innovation
  that supposedly fuels career success, but those who provide the
  diversity systematically don't capture the career returns — implying
  that the innovation→success conversion is not neutral across
  demographic groups."*
- User's distributional extension: *"Diverse individuals produce a
  collective good whose benefits are not distributed back to them in
  proportion to what they produce."*

Both are right. The first emphasizes premise-logical structure; the
second emphasizes distributional consequence. A good Discussion section
might use both.

---

### SQ3 — Novelty vs. impactful novelty: which matters more for explaining the career gap?

*(Pending — not yet worked through.)*

### SQ4 — Why STM rather than simpler approaches like TF-IDF? What advantage for their task?

Working session with user, 2026-04-24.

**User's first pass.** STM will "understand" topic in a deeper
semantic sense than TF-IDF, which is purely linguistic.

**Sharpened version.** The intuition is in the right direction but the
"semantic vs. linguistic" framing slightly overstates what's
happening. Neither method "understands" semantics in a meaningful
sense — both are statistical. The real distinction is about *what kind
of statistical structure* each captures.

**TF-IDF is a per-document weighting scheme.** For a word w in document d:

> TF-IDF(w, d) = (frequency of w in d) × log(|D| / |{d' : w ∈ d'}|)

It scores each word per document saying "how distinctive is this word
*to this document* versus the rest of the corpus?" High score = common
here, rare elsewhere. That's it. It operates on one document at a time
against corpus-wide word frequencies.

**STM is a corpus-level generative model.** It assumes the entire
corpus was produced by a mixture-model process and fits latent topics
by modeling the joint co-occurrence structure across *all* documents
simultaneously. Each topic β_k is a probability distribution over the
vocabulary; inference finds topics whose distributions best explain
observed word-document patterns.

**The real distinction.** Not "semantic vs. linguistic" — both are
purely statistical — but **per-document scoring vs. corpus-wide joint
structure**. STM discovers distributional regularity across the corpus
that happens to correspond to human-interpretable topics, because
human scientific writing *is* structured by underlying topics and
that structure propagates into co-occurrence patterns. The
correspondence between statistical structure and semantic topic is
real; the mechanism is distributional.

**What Hofstra specifically gets from STM over TF-IDF.**

1. **A topic-structured vocabulary.** ~500 topics, each with its
   characteristic terms. With TF-IDF, you'd get per-document term
   lists with no cross-paper thematic structure. STM's structure is
   what makes the vocabulary usable for novelty counting — concepts
   need to be grouped and comparable across papers, not just
   distinctive within one.
2. **FREX weighting over topic-word distributions.** FREX combines
   frequency and exclusivity *within a topic* (common in this topic,
   concentrated in this topic relative to others). TF-IDF's analogous
   selection (common in doc, rare elsewhere) doesn't give you
   thematic grouping — its "exclusivity" is against the corpus, not
   against other topics.
3. **Covariate awareness.** STM with year-as-prevalence-covariate
   lets topic prevalence evolve over time. "Deep learning" can grow
   as a topic from near-zero in 1980 to substantial in 2020. TF-IDF
   has no mechanism for temporal structure.
4. **Internal coherence validation.** STM's coherence metric (Mimno)
   plus exclusivity plus external validation (MCC against keyword
   partitions) lets Hofstra empirically justify K=500. TF-IDF
   produces no latent structure to validate.
5. **Scalable concept selection.** Top-500 FREX terms per topic × 500
   topics gives a principled way to pick a large, structured
   vocabulary. With TF-IDF you'd get top-N across the corpus, mixing
   function words, idiosyncratic terms, and topical terms without
   quality control.

**Hofstra's own framing (SI p. 5):**

> "The affordance of STMs in comparison to simpler concept extraction
> strategies — i.e., choose the top n TF-IDF weighted terms — is that
> it allows us to extract terms that play a significant role in an
> underlying thematic structure."

Their language echoes the sharpened distinction. STM gives thematic
structure; TF-IDF doesn't.

**Why the user's initial framing captured something real.** STM groups
words by how they co-occur in documents, which *feels* semantic
because the groups often correspond to topics humans would recognize.
The flavor is semantic even though the mechanism is distributional.
The user's "STM will understand topic in a deeper semantic sense"
intuition picks up on this flavor correctly; the sharpening just
clarifies the mechanism underneath.

**Takeaway for the sharpened version.** "STM discovers corpus-wide
latent topics by modeling joint co-occurrence structure across all
documents; TF-IDF only scores individual words' distinctiveness per
document. For Hofstra's task, STM's topic structure is what tilts the
balance — the vocabulary needs thematic grouping to be usable for
novelty counting, and TF-IDF can't provide that."

---

### SQ5 — What is FREX scoring? Why isn't frequency alone enough?

*(Pending — covered in topic-modeling primer §3; summary note could be
added here if the user wants the compressed version.)*

### SQ6 — Why negative binomial rather than OLS? What does the log offset accomplish?

Working session with user, 2026-04-24.

**User's first pass.** The offset is used to block/control on
# new links. Negative binomial (not OLS) because the graph obeys
power law.

Two sharpenings, each replacing a close-but-imprecise framing with
the actual technical mechanism.

**(1) The offset is normalization, not control.** A control variable
enters the regression equation on the right-hand side with an
*estimated* coefficient — the model learns how much to weight it. An
offset enters with a *fixed* coefficient of 1 (log-linked). For a
negative binomial model of count Y:

> log(E[Y]) = β₀ + β₁X₁ + ... + βₖXₖ + log(t)

This is algebraically equivalent to:

> log(E[Y]/t) = β₀ + β₁X₁ + ... + βₖXₖ

So the offset converts the model from predicting **expected count**
to predicting **expected rate** (count per unit of exposure).

Hofstra uses this to model `uptake per new link` (a rate,
non-integer) as a count model with normalization: total `uptake` is
the dependent count; `log(# new links)` is the offset. Coefficients
on other predictors become interpretable as rate changes. SI p. 18:

> "Uptake per new link (impactful novelty) is a non-integer rate
> instead of an integer event count. An occasional method of
> modelling non-integers is to offset the negative binomial
> regression with logged independent variables."

**Why the distinction matters.** The offset imposes an assumption —
fixed coefficient of 1 means uptake is assumed to scale exactly
linearly with # new links (in log-units). If uptake actually scales
sublinearly or superlinearly, the offset mis-specifies the
relationship. A freely-estimated coefficient would relax the
assumption but lose the clean rate interpretation. The control vs.
offset choice is a methodological commitment, not just a presentation
choice.

Your "control on # new links" framing captures the *effect* (the
result reads as uptake-per-link) but misses the *mechanism*
(normalization via fixed-coefficient rescaling). Informally these
look similar; technically they're distinct commitments.

**(2) Negative binomial is motivated by overdispersion, not
specifically power law.** OLS fails on count data for three distinct
reasons:

1. **Non-negative integer constraint.** OLS predicts real-valued
   outcomes; counts are non-negative integers.
2. **Skewed distributions with non-normal residuals.** Counts with
   many zeros and a long right tail break OLS's normality assumption.
   (20.9% of Hofstra's theses introduce 0 new links; `# new links`
   has mean=9, SD=14, max in hundreds.)
3. **Variance-mean relationship.** Count variance grows with mean;
   OLS's homoscedasticity assumption is violated.

**Why negative binomial specifically, not Poisson.** Poisson is the
simpler count model but assumes variance = mean. Real count data
typically has variance > mean (overdispersion). Negative binomial
generalizes Poisson with a dispersion parameter α, letting
variance = mean × (1 + α × mean). This accommodates the "counts
with variance much greater than mean" pattern typical of scientific
productivity, citation counts, and conceptual recombinations.

Hofstra's data: `# new links` variance ~189 (mean 9, SD 14) —
variance is ~20× the mean. Heavily overdispersed. `uptake per new
link` variance ~9.5 (mean 0.79, SD 3.08) — also overdispersed.

**The power-law angle — intuition captures something real.** Power-law
distributions are a specific kind of heavy-tailed distribution.
They're scale-free and exhibit overdispersion because the tail
carries so much mass. Power-law-distributed data are automatically
overdispersed, and Hofstra's right-skewed `# new links` distribution
is consistent with power-law-like tail behavior. But negative
binomial's motivation is **overdispersion generally**, not power-law
specifically. Many overdispersed distributions (clustered events,
zero-inflated processes, negative binomial itself) aren't power-law.
NB accommodates the variance-mean mismatch without committing to a
specific tail shape.

SI p. 17:

> "Scientific novelty (# new links) and impactful novelty (uptake per
> link), are right-skewed counts of events or rates. For these
> outcomes, we employ negative binomial regression analyses, where
> the overdispersion in the outcomes is modeled as a linear
> combination of the covariates."

Hofstra cites **right-skewness** and **overdispersion** as the
motivation — not power law specifically. The user's intuition picked
up the heavy-tailed shape correctly; the sharpening identifies
overdispersion as the technical condition that requires NB.

**Sharpened one-sentence version.** "Negative binomial handles
overdispersed count data (non-negative integers with right-skewed
distributions and variance growing with mean), which OLS can't fit.
The `log(# new links)` offset is a fixed-coefficient rescaling
device — it converts the count model into a rate model by imposing
a linear relationship between uptake and # new links rather than
estimating that relationship. The power-law framing captures the
heavy-tailed shape but isn't the technical condition that forces NB;
overdispersion is."

### SQ7 — What fraction of students produce any novelty that gets adopted? What does this imply about the shape of the innovation distribution?

Working session with user, 2026-04-24.

**Setup.** The question combines two figures from the paper: 20.9% of
students introduce zero new links (so 79.1% produce ≥1), and ~50% of
new links never receive any uptake. It asks what fraction of students
have at least one *adopted* new link, and what the answer implies about
the shape of the innovation distribution.

**User's decomposition.** Reduces to: for a student with k new links,
are k/2 typically adopted (independence-style, uptake spread across
the student's links), or is uptake correlated within-student (some
students have most links adopted, others have none)? The
50%-non-uptake aggregate doesn't reveal which.

**Two critiques user surfaced — both substantive.**

**(1) Within-student correlation isn't answerable from cumulative
statistics.** The paper reports per-link uptake distribution (mean=0.79,
median=0.33, SD=3.08) and per-student new-link distribution (mean=9,
median=4, SD=14), but not the joint distribution within students. We
don't know whether a student with high novelty also has high uptake-
per-link or whether the two are uncorrelated within-student. SD/mean
of uptake-per-link is ~4× — substantial heterogeneity that's more
consistent with within-student correlation than independence, but
this is suggestive rather than dispositive.

**(2) The 50% non-uptake figure is a cumulative aggregate that hides
temporal asymmetry.** A 1985-introduced link has ~30 years of
subsequent corpus to be adopted in; a 2010-introduced link has only 5
years. The "50% never adopted" aggregate includes substantial
right-censoring on recent-vintage links. The marginal probability
"this link would ever be adopted given infinite time" is higher than
50%; the empirical fraction "was this link adopted by 2015" is the
actual 50% figure. Hofstra's year fixed effects in inferential
analyses partially absorb this, but they don't fix the marginal
aggregate that the question is built on.

**Bounding analysis (given the data underdetermines the exact answer).**
Two extreme scenarios:

- **Independence scenario:** each of a student's new links has
  independent 50% probability of adoption. P(any adopted | k links) =
  1 − 0.5^k.
  - k=1: 50%
  - k=4 (median): 93.75%
  - k=9 (mean): 99.8%
  Under independence, almost every link-producing student has at least
  one adopted link, and the fraction "any adopted" approaches 79.1%.
- **Perfect correlation scenario:** each student is either "all
  adopted" or "all not." Half of link-producers fall in each. Fraction
  with any adopted = 0.5 × 79.1% = **39.6%**.

Realistic answer falls in 50–70%, with the uptake-per-link
heterogeneity suggesting the truth is closer to the lower end (more
correlation, not less). The literal number isn't sharp; the data
underdetermines it.

**Reframing — what the question actually probes.** Given the bounds
are wide and the literal number isn't derivable, the substantive
answer is about distributional *shape*, not a number. Three pieces of
evidence about innovation concentration:

1. Per-student new-link distribution is right-skewed (mean=9, median=4,
   SD=14, 20.9% at zero). The minority who produce more than the
   median produce most of the new links.
2. Per-link uptake distribution is also right-skewed (mean=0.79,
   median=0.33, SD=3.08).
3. The two heavy tails likely co-occur within students (large SD/mean
   of uptake-per-link argues for within-student correlation rather
   than independence).

When two right-skewed distributions are positively correlated within
unit, the compound distribution (per-student total adopted innovation)
is **extremely heavy-tailed**. A small minority of students likely
accounts for most of the adopted innovation. The fraction with *any*
adopted innovation is moderate (50–70% bound), but the fraction with
*substantial* adopted innovation is much smaller. **Innovation isn't
democratic, even within the link-producing subpopulation.**

**Connection to ws2's Test IV persistence extension.** This heavy-tail
concentration in citation distributions is well-documented (power-
law-like behavior in scientific impact). For our Test IV persistence
regressions on C_15 (10-year citation accumulation), a small fraction
of extremely-cited papers can dominate regression leverage —
particularly for the interaction term β_3 in the direct-interaction
regression and the persistence ratio in the C_10/C_3 regression.

**Pre-registration commitment added to pending Phase 0.2 batch
(item 7 sub-item):** report Test IV persistence regression
coefficients in three versions:

1. Full sample (1975–2014 papers)
2. Top 1% of C_15 trimmed
3. Top 5% of C_15 trimmed

Coefficient stability across all three = robustness claim. Coefficient
flip or substantial magnitude shift between full and trimmed = report
as evidence that a small set of extreme papers drives the result;
either outcome is publishable, framing differs.

**Net answer to SQ7.** Honest: the literal number isn't computable
from the given data because (a) within-student uptake correlation
isn't reported by the paper, and (b) the 50% non-uptake figure is a
cumulative aggregate that mixes uptake horizons across vintages. The
substantive answer is the shape claim — innovation is heavily
concentrated in a productive minority, with a heavy-tailed compound
distribution combining heavy-tailed novelty production and heavy-
tailed uptake. The fraction "with any adopted" is somewhere in
50–70%; the fraction "with substantial adopted innovation" is
considerably smaller; the very-top-cited papers exert disproportionate
influence on aggregate findings (motivating the pre-registered
trimming robustness for Test IV).

### SQ8 — How are distal vs. proximal novelty measured? What Word2Vec hyperparameters and validation?

Working session with user, 2026-04-24.

User noted they hadn't paid much attention to this on first reading and
asked for a full walkthrough. No first-pass answer to sharpen — this is
a reference walkthrough.

**What the metric measures.** Distal novelty asks: for a pair of
concepts that this thesis newly co-occurs, are those concepts
semantically close to each other or far apart in vector space? A new
link between concepts already in the same intellectual neighborhood
(e.g., `ceramic_composition` and `fracture_behavior`, both materials
science) is *proximal*; a new link between concepts in distinct
neighborhoods (e.g., `genetic_algorithm` and `hiv-1`) is *distal*.
Distal links are creative juxtapositions, cross-field bridges, or
metaphorical leaps; proximal links are within-field refinements.

The metric is computed per-pair, then averaged over a thesis's new
links to get a thesis-level distal-novelty score. So distal novelty
is a property of *pairs*, summarized as an *average over thesis*.

**Word2Vec hyperparameters (SI p. 12):**

- **Architecture:** skip-gram model (Mikolov et al. 2013, *Efficient
  Estimation of Word Representations in Vector Space*, arXiv:1301.3782).
- **Training data:** dissertation abstracts only (1977–2015). Not pre-
  trained on a larger corpus.
- **Vocabulary:** FREX concepts only (the ~250K-token concept
  vocabulary derived from STM topic-FREX terms). Not the full word
  vocabulary.
- **Window size:** 5 — captures co-occurrences within roughly two
  sentences.
- **Dimensions:** 100 main; robustness checked at 200 and 300.
- **Time scope:** **Globally trained on the entire 1977–2015 corpus.**
  Single embedding space, not per-year or per-decade. This is a
  load-bearing methodological choice with consequences for ws2.

**Distance metric.** For two FREX concepts a and b with learned
embeddings v(a) and v(b):

> distance(a, b) = 1 − cos(v(a), v(b)) = 1 − v(a)·v(b) / (||v(a)|| ||v(b)||)

Cosine distance, not Euclidean. Range 0 (identical direction) to 2
(opposite direction). For a thesis with multiple new links,
distal-novelty(thesis) = average cosine distance over all newly-linked
pairs in that thesis.

**Distribution in their data:**

- Mean = 0.426
- Median = 0.419
- SD = 0.118

Roughly normally distributed (hence linear regression to model it,
unlike novelty and impactful novelty which are right-skewed counts
requiring negative binomial).

**Validation — internal robustness:**

- **Robust to dimensionality:** results similar at 100, 200, 300 dims.
- **Robust to stochasticity:** Word2Vec has random initialization;
  multiple runs give similar scores.
- **Sensitivity check on time-independence:** trained alternative
  time-dependent embeddings on year-2000 data alone, computed distal-
  novelty scores, correlated with global-embedding scores.
  **Correlation r = 0.931** (very high).

**Validation — external against human coders:**

- Random sample of 100 newly-linked concept pairs.
- 3 expert human coders independently labeled each pair as "distal"
  or "proximal."
- Inter-coder agreement: **Cohen's κ = 0.46** (moderate; not high).
  Convention: 0.21–0.40 fair, 0.41–0.60 moderate, 0.61–0.80
  substantial, 0.81+ near-perfect.
- Coder consensus predicts ~95% of "true distal" links (defined as
  those with distance score > 0.8).
- **15–20% of high-distance links are "hard to interpret
  substantively"** — embedding flagged them as distal but humans
  couldn't articulate why.

**Substantive findings using this metric (Figure 3, p. 9287):**

1. **Underrepresented genders introduce more distal novelty** (Panel
   C; P<0.001). Women's new concept-pairs have higher cosine distance
   on average than men's. Same effect for nonwhite vs. white but
   smaller. Hofstra's interpretation: the "outsider vantage" of
   underrepresented groups produces less-conventional combinations —
   they bridge across fields more often.
2. **Distal novelty negatively predicts uptake** (Panel D; P<0.001).
   The further apart linked concepts are, the less likely the link
   is to be reused in subsequent theses. Distal links are creative
   but get less adopted.

Hofstra uses these together as a **partial mediation argument:** women
→ more distal novelty → less uptake. Some of the gender gap in uptake
is explained by distal novelty as a mediator. This doesn't fully
explain the gap (the discount holds even controlling for distal
novelty in Figure 4), but it's part of the mechanism.

**Methodological strengths.**

- **Concept-level, not document-level.** Word2Vec on FREX terms gives
  type-level vectors; distance is between concept types, not between
  specific contextual usages. Reproducible across runs, interpretable.
- **Independent of citation behavior.** Like the novelty count itself,
  distal novelty is text-only — doesn't depend on citation patterns.
- **Validated with human coders.** Most scientometric measures don't
  get external validation against domain experts. κ=0.46 is moderate
  but real; more than most papers do.
- **Robustness across dimensionality and seeds is checked.** Bare
  minimum, but explicit.

**Methodological weaknesses (relevant to ws2's drift discussion).**

**(1) Globally-trained, not diachronic.** The most consequential
choice. Hofstra trains one embedding on the whole 1977–2015 corpus,
then uses it to score links from any year. Modern semantic structure
is therefore baked in; 1985 links are scored against a 2015-
influenced embedding space. Their justification is the year-2000
robustness check (r=0.931 with time-dependent embeddings). But this
is a single-year sensitivity at a year close to the corpus center,
where global and time-dependent should look most similar. They don't
validate at 1985 or 2010 where drift would be larger. This is exactly
the methodological gap our drift-mitigation ladder addresses (see
`phase-0.1-plan.md` subsection 2 and `desiderata.md` §3).

**(2) Cohen's κ = 0.46 is moderate, not high.** Their human coders
agree with each other at moderate level, not strong consensus. The
distal-vs-proximal distinction is somewhat subjective even for
domain experts.

**(3) 15–20% of high-distance links are hard to interpret.** A
substantive error rate is baked in — not all high-distance pairs
are genuinely distal in a meaningful intellectual sense; some are
just tokens that happen not to co-occur in the corpus.

**Connection to ws2.**

**(a) Hofstra's distal-novelty pipeline IS our Flavor A pipeline
(Stage 3 conditional).** Word2Vec on FREX-style concept vocabulary,
trained globally on the corpus. This is what we'd run if our Phase
0.1 drift-pilot indicates Flavor A is needed. We'd implement
essentially Hofstra's methodology with the addition of explicit
Procrustes alignment across eras (which they don't do because their
global embeddings are nominally aligned by construction — at the
cost of suppressing diachronic signal).

**(b) Their `distal novelty` is conceptually parallel to our anchor-
dimension projection (Mitigation 4).** Both use a curated subset of
vocabulary as the basis for distance measurement, rather than
computing in raw transformer-embedding space. Hofstra's vocabulary
is automatic (FREX from STM); our anchor concepts are curated (~100
stable scientific terms). Different procedure, similar spirit.

**(c) The diachronic concern they elide is what our drift-mitigation
ladder addresses.** If we run Flavor A, we explicitly do not assume
year-2000 robustness extrapolates; we Procrustes-align across decades
using anchor papers. This is one of the few places where ws2's
methodology is genuinely better-rigored than Hofstra's.

**Distinction worth noting.** For Test IV's primary novelty (N_p =
embedding distance to citation-context centroid), we use SPECTER2
contextual document embeddings, not Word2Vec type-level concept
embeddings. Different embedding family, different unit (document vs.
concept), different operation (distance to centroid vs. distance to
single concept). So Hofstra's distal-novelty and our N_p aren't the
same metric — they're parallel constructions for different units. If
we add Hofstra-style concept-linkage as Test IV secondary, *that*
metric would adopt their distal-novelty methodology more directly.

**One-sentence summary.** Distal novelty = average cosine distance
(in a 100-dim Word2Vec space trained on dissertation abstracts, FREX
concepts only) between concept pairs newly-linked by a thesis;
validated with moderate human-coder agreement (κ=0.46), robust to
dim choice and stochasticity, with a single-year time-dependence
robustness check (r=0.931 at year 2000) that doesn't probe boundary
years; used by Hofstra to argue that women's higher distal-novelty
production partially mediates their lower uptake.

### SQ9 — PMI filter threshold sensitivity (≥10 vs. ≥1 vs. ≥100; PMI vs. raw frequency)

Working session with user, 2026-04-24.

User asked first for the PMI computation mechanics (corpus-wide
empirical probabilities, log-ratio of joint to product-of-marginals,
specific examples) before answering. Once mechanics were clear, user
gave a tight three-part answer that turned out to surface a deeper
methodological observation about demographic-by-filter interaction.

**User's first pass.**

- ≥10 → ≥1: many noise high-PMI pairs (false positives to what we
  truly want)
- ≥10 → ≥100: false negatives — some useful pairs get screened out;
  what remains is "not too distinguishable wrt median"
- Raw frequency filter: penalizes concepts with low baseline
  occurrence rates → many false negatives

**Sharpening (1) — ≥10 → ≥1.** The false positives concentrate in
*one-shot or two-shot terms*. Their PMI estimates are pathologically
unstable: the denominator $\Pr(a)\Pr(b)$ becomes vanishingly small,
and a single co-occurrence of two one-shot terms produces extreme
PMI by accident.

Substantive consequence: novelty count would *inflate massively*
because the candidate vocabulary explodes, but the new "links" would
be measuring vocabulary peculiarities of obscure terms rather than
substantive concept-bridging. Hofstra's headline finding might still
hold but would be measuring something different — statistical noise
over rare vocabulary rather than meaningful recombination.

The ≥10 threshold is essentially: "PMI on rare terms is noise;
require enough observations for the ratio to mean something."

**Sharpening (2) — ≥10 → ≥100.** User's "not too distinguishable wrt
median" intuition is sharp. The mechanism: PMI is most discriminating
when the candidate vocabulary spans a wide range of base rates —
common terms get penalized for high $\Pr(a)\Pr(b)$ products, rare-
but-associated terms get rewarded. When all surviving terms have
similar (relatively high) base rates, the products sit in a similar
range, and PMI's discriminative power across the surviving pool
narrows.

Specific consequence for Hofstra's findings: distal novelty depends
on cross-field bridges, which typically involve at least one
specialized term that wouldn't survive ≥100. So:

- Distal novelty signal weakens or disappears.
- The partial-mediation argument (women → more distal novelty → less
  uptake) loses its data foundation.
- Hofstra's mechanistic chain in Figure 3 would be broken.
- The novelty signal that survives is entirely "within-field common-
  concept recombinations," not the cross-field-bridges-by-outsiders
  narrative the paper builds.

**Sharpening (3) — Raw frequency vs. PMI.** This is the most
interesting result. User's framing (penalty for low-baseline concepts
→ false negatives) is correct but doesn't surface the deeper finding:
**the demographic-by-filter interaction.**

Hofstra's argument depends on a chain:

1. Women introduce more distal novelty (Figure 3C, P<0.001)
2. Distal novelty has lower uptake (Figure 3D, P<0.001)
3. Therefore part of the gender uptake gap is mediated by distal-
   novelty differential

Distal novelty = cross-field bridges = concept pairs from semantically
distant regions, typically involving at least one specialty/less-
common term. Under raw-frequency filtering:

- Cross-field-bridge pairs get excluded (low absolute joint count)
- Women's novelty contribution gets *disproportionately* filtered out
  (because their novelty is more distal-loaded)
- Surviving novelty pool skews toward within-field common-concept
  pairs (more conventional, less distal)

**The raw-frequency filter doesn't just produce false negatives
uniformly — it produces false negatives disproportionately for one
demographic group.** The filter choice isn't demographically neutral.

If Hofstra had used raw frequency instead of PMI:

- The headline "underrepresented groups introduce more novelty"
  might *weaken substantially*
- Distal novelty wouldn't exist as a measurable mediator
- The cross-field-outsider-vantage mechanism story wouldn't have
  data behind it
- Findings might *flip* — minorities could appear less novel under
  raw-frequency filtering

**The methodological lesson generalizes.** Filter choice in
scientometric measurement often has demographic-by-method
interactions. A filter that disproportionately excludes one kind of
content (here: rare-term-involving cross-field bridges) will
disproportionately exclude the demographic groups whose work is
characterized by that kind of content. This is not unique to PMI vs.
raw frequency; it applies to many filtering choices (citation-count
thresholds, author-disambiguation cutoffs, abstract-length
restrictions, etc.).

**Connection to ws2's filter policy.** This SQ directly motivated our
filter-policy commitments in pending Phase 0.2 batch item 5:

- Test IV primary N_p (embedding distance): no filter on cited
  references. Filtering would shift the metric toward "distance from
  mainstream references," biasing against distal-novelty detection
  — exactly the failure mode this SQ surfaces in Hofstra's context
  if they'd used raw frequency.
- Test IV secondary N_p (Hofstra-style concept-linkage): adopts
  Hofstra's ≥K filter on FREX concepts (K=20 default). Inherits
  PMI-style stability without distorting toward common-only.
- Citation-list richness sensitivity (sub-item): explicitly tests
  whether Test IV's findings differ when we restrict to citation-rich
  papers vs. include sparse-citation papers. Probes the demographic-
  by-filter interaction at our scale.

The demographic-by-filter interaction is a real methodological hazard
ws2 has to handle deliberately; this SQ exercise is exactly why our
filter policy is constructed the way it is.

**One-sentence summary.** Lowering the threshold to ≥1 floods the
candidate pool with one-shot-vocabulary noise (PMI estimates
unstable for rare terms); raising to ≥100 narrows the surviving
vocabulary to a common-base-rate range where PMI's discriminative
power flattens (and crucially, distal-novelty signal vanishes
because cross-field bridges depend on specialty terms); replacing
PMI with raw frequency systematically excludes cross-field bridges
and creates a demographic-by-filter interaction (women's distal-
loaded novelty is disproportionately filtered out, potentially
flipping or substantially weakening the headline finding). The
methodological lesson — filter choices have demographic-by-method
interactions — directly motivates ws2's deliberate no-filter primary
+ Hofstra-style ≥K filter on secondary policy.

### SQ10 — Global-embedding justification (r=0.931 at year 2000) — under what conditions does it fail?

Working session with user, 2026-04-24.

User engaged with the walkthrough but had no first-pass answer to
sharpen. Reference walkthrough.

**Setup.** Hofstra trains one global Word2Vec embedding on the full
1977–2015 corpus and uses it to compute distal novelty for theses
from any year. Validation: at year 2000 only, they trained an
alternative time-specific embedding and correlated distal-novelty
scores from global vs. time-specific. Correlation r = 0.931. They
take this as evidence that the metric is robust to time-dependence,
extrapolating to all years in the corpus.

**Why year 2000 is best-case by construction.** Year 2000 sits near
the temporal centroid of the 1977–2015 corpus. A global embedding's
representations are an average over all years' co-occurrence
patterns, weighted by data volume — so the global embedding is
**closest by construction** to a time-specific embedding from a
year near the data-weighted center. Validating at the center year
means choosing the year where global and time-specific should agree
the most. r = 0.931 there is essentially "in the year these two
methods should agree most by design, they do." Weak claim.

**Four reasons boundary years (1982, 2010) would diverge more:**

**(1) Vocabulary evolution.** Concepts emerge, fade, and shift
meaning. `neural_network` meant different things in 1982
(physiological/early-connectionist) and 2010 (post-PDP/post-LeNet
computational). Global embedding learns a weighted average between
the senses; doesn't represent either accurately.

**(2) Co-occurrence pattern shift.** Even for stable-meaning
concepts, what they co-occur with changes. `genomics` co-occurred
with `restriction_enzyme` in 1982 and `single_nucleotide_polymorphism`
in 2010. Distance calculations between concept pairs differ
substantially across eras.

**(3) Asymmetric data volume.** 1977–1985 has many fewer
dissertations than later decades (CS as a field was small;
indexing was incomplete). A hypothetical 1982-only embedding would
have noisier estimates from limited data; the global embedding has
post-2000 data dominating its representation. The boundary-year
sample-size effect compounds the temporal-distance effect.

**(4) Rapidly evolving fields hit hardest.** CS, which is heavily
represented in Hofstra's corpus and in our own focus, exhibits
substantial vocabulary turnover between 1982 and 2010. Stable fields
(classical mechanics) show little drift; fast-changing fields
(CS, genomics, ML) show a lot. Hofstra's distal-novelty findings
inherit the most error in exactly the fields whose vocabulary
shifts most.

**The structural critique of the validation logic.** From a single-
year, single-correlation result Hofstra extrapolates "the metric is
robust to time-dependence everywhere." Three reasons this
extrapolation is invalid:

1. **It's a best-case measurement.** Year 2000 is where the two
   methods should agree most by construction. Center-year agreement
   tells you nothing about boundary-year agreement.
2. **No bound on far-year disagreement.** A correlation of 0.931 at
   one year provides no theoretical basis for predicting the
   correlation at a different year. Could be 0.95 at 1995, 0.65 at
   1982, 0.75 at 2010 — we don't know.
3. **Aggregate scores can hide concept-level disagreement.** Even if
   distal-novelty *averages* correlate, individual concept-pair
   distances might differ wildly. Hofstra's substantive findings
   (women → more distal novelty; distal → less uptake) depend on
   per-pair distance estimates, not aggregate scores.

**What a proper validation would look like.** Train time-specific
embeddings at multiple years (1985, 1995, 2005, 2015), report the
full correlation curve. If the curve is uniformly high, the global-
embedding choice is justified. If it drops at boundary years, the
choice systematically distorts boundary-year measurements and the
pre-1990 / post-2010 distal-novelty claims are unreliable. Hofstra
didn't do this — they did the cheapest possible validation and
accepted the center-year result as license for the full corpus.

**Implication for the substantive claims.** The boundary-year
distortion isn't uniform; it concentrates in:

- Fields with rapid vocabulary change (CS specifically — Hofstra's
  primary corpus and our primary field)
- Eras with sparser data (pre-1990)
- The distal-novelty mediator specifically (which depends on
  per-pair concept distances, not aggregate scores)

So the partial-mediation argument (women → more distal → less uptake)
that Hofstra builds is on shakier ground than the validation
acknowledges, *especially* for the boundary-year portion of their
analysis window.

**Connection to ws2 — this is exactly what our drift-mitigation
ladder addresses.**

- **Mitigation 4 (anchor-dimension projection)** — runs in default
  Stage 2. Doesn't rely on the embedding model itself being time-
  invariant; projects onto stable-concept anchors that are
  drift-robust by construction.
- **Phase 0.1 Check 5c (drift-pilot)** — empirically tests era-match
  rates on 1970s abstracts specifically. Probes the boundary-year
  question Hofstra didn't probe.
- **Stage 3 Flavor A (conditional)** — explicitly trains per-era
  Word2Vec + Procrustes-aligns. This IS the multi-year validation
  curve Hofstra didn't do.
- **Stage 3 Flavor B (conditional)** — fine-tunes SPECTER2 per era.
  Document-embedding-level escalation if Flavor A surfaces drift.

This is one of the few places where ws2's methodology is genuinely
better-rigored than Hofstra's, not just different. The default
methodology assumes boundary-year drift is a real concern and
provides explicit escalation paths to test for it; Hofstra's
methodology assumes drift is not a concern, validated by a single
best-case correlation that doesn't actually probe the failure mode.

**One-sentence summary.** Hofstra's r=0.931 validation is a center-
year correlation that's best-case by construction; vocabulary
evolution, co-occurrence pattern shift, asymmetric data volume, and
field-specific rapid change all push global vs. time-specific
embeddings further apart at boundary years (1982, 2010); their
extrapolation from one center-year correlation to corpus-wide
robustness is structurally invalid, and ws2's drift-mitigation
ladder (Mitigation 4 default + drift-pilot + conditional Flavor
A/B) is built precisely to test the failure mode they didn't probe.

### SQ11 — Innovation-discount null hypothesis + causal identification

Working session with user, 2026-04-24.

User caught an imprecision in my original question wording — I had
conflated "minorities" (general) with the specific 3.5% → 9.5%
number (gender-specific). Cleaned-up version: "the 2SD-above-median
novelty increases the gender-minority-vs-majority faculty-
probability gap from 3.5% to 9.5%; what's the null and what would
make this causal?"

**Gender vs. race clarification.** Hofstra reports findings on both
demographic axes. The 3.5% → 9.5% (and 4.3% → 15% for impactful
novelty) numbers are gender-specific. The racial-discount finding
exists (25%-lower-baseline-odds for racial minorities; paper claims
the discount also extends to slope-with-novelty for racial axis) but
isn't put in the same headline-numerical form in the main text.

**Null hypothesis tested.** The relationship between novelty and
faculty-becoming-probability has the *same slope* across gender
groups (parallel-slopes / constant-gap null). Under this null, the
gap at low novelty equals the gap at high novelty.

**Alternative tested (and supported).** Slope differs — minorities
have shallower novelty-on-faculty slope. The 3.5% → 9.5% widening is
the operational signature. Formal test: (novelty × gender)
interaction term in logistic regression of faculty status. Hofstra
cites P<0.01 for this interaction.

**User's observation on causal identification.** "Their underlying
causal pathway is innovation → career outcomes AND gender → career
outcomes (among others), so all the issues with causal inference
will haunt them."

This captures the multi-arrow problem precisely: there are multiple
potentially-causal pathways, none individually identified from
observational data, and the slope-difference finding combines them.
The causal pathways at play:

1. **Demographic → innovation.** Minorities produce more novelty
   (Figure 2 main effect).
2. **Innovation → career.** Novelty predicts faculty outcome
   (Figure 4 main effect).
3. **Demographic → career, independent of innovation.** Baseline
   demographic gap at low novelty levels.
4. **Demographic × innovation → career.** The slope-difference /
   interaction term — the headline discount finding.

Pathway 3 alone (demographic → career through non-innovation
channels: hiring biases, dual-career constraints, network-access
asymmetries, advisor-support differentials) could partially produce
the observed pattern. Unmeasured confounders correlated with both
demographics and innovation quality could also produce it. The
conditional association is well-identified; the causal interpretation
requires assumptions Hofstra's design can't sustain.

**Identifying strategies that would establish causality, none
available to Hofstra:**

1. **Randomization.** Random demographic-identity assignment is
   impossible. Audit-study designs (same paper labeled with
   different inferred-gender names) exist at small scale but not
   population-level scientometric.
2. **Natural experiments.** Exogenous shock that changes novelty for
   one group but not the other. Hard to find at scientometric scale.
3. **Instrumental variables.** Instrument affecting novelty but not
   faculty-outcome through any non-novelty channel. Very hard for
   innovation in science.
4. **Panel data with individual fixed effects.** Repeated within-
   individual observations to absorb individual-level fixed effects.
   Hofstra has only first-thesis-per-individual, not panel data.

None of these strategies is operationally available given their
design. The result remains a **conditional association**, not a
causal discount. The paper's careful language (talking about
"discounting" patterns rather than "discrimination causing")
implicitly acknowledges this; a sympathetic reader infers
causality, a hostile reader argues the unmeasured-variable concern
is decisive.

**Connection to ws2.**

For our **Test IV** (within-paper team-diversity × novelty
regression), we face the same multi-arrow structure:

- Team diversity → novelty (the immediate question)
- Team diversity → citations / career outcomes (separate)
- Novelty → citations / career outcomes (separate)
- Team diversity × novelty → outcomes (interaction in persistence
  extension)

Same confounding structure, same identification limits. Our Methods
section already commits to reporting this as descriptive association,
not causal effect (the framing-commitment paragraphs in pending
Phase 0.2 batch). The user's observation reinforces a structural
point: the multi-arrow causal-inference problem isn't unique to
Hofstra; it's structural to *all* observational scientometrics.

For **aggregate Tests I–III**, the situation is even more
aggregated — within-paper causal arrows aren't identifiable from
aggregate data at all. The population-level pattern (divergence
between aggregate dimensions) can be documented without claiming
causal arrows. The Epistemic Scope section in `conceptual.md`
addresses this explicitly.

This is also why the three-whitespace program structure exists:
ws2 documents observable patterns; ws3 specifies plausible
structural stories formally; ws1 attempts counterfactual
identification through interventional simulation. The multi-arrow
causal-inference problem can't be resolved by ws2 alone, and
acknowledging that is a methodological commitment, not a
weakness.

**One-sentence summary.** Null = parallel-slope; alternative tested
= shallower-slope-for-minorities (slope-difference test, P<0.01 for
the interaction). For the discount to be *causal* rather than
*conditional*, Hofstra would need randomization, natural
experiments, instrumental variables, or panel data — none
available. With multiple causal pathways simultaneously in play
(demographic → innovation, innovation → career, demographic →
career, demographic × innovation → career), observational data can
document the conditional pattern but cannot isolate which arrows
produce it. Same identification limits apply to ws2's Test IV and
to all observational scientometric work; this is precisely what
motivates the three-whitespace program structure where ws1
simulation does the counterfactual that ws2 cannot.

### SQ12 — "Research faculty" definition and selection mechanisms

Working session with user, 2026-04-24.

**User's first pass.** The narrow "research faculty" definition
depends on "what career trajectory looks like in each field," citing
three filtered paths: (1) research lab after PhD, (2) non-research
position after PhD, (3) non-tenure research-track position in
academia. Plus a temporal skew observation: "some others like worked
for some time in 1)-3) above before obtaining tenure track will also
add some temporal skew." Plus the sharp framing: *"It's like saying
I will care for certain edges only if the creator of the edge
remains in the pool. This might only have like career progression as
the primary outcome of interest at the study design time."*

**Sharpening (1) — person-level vs edge-level filter.** The user's
"edges only if the creator remains in the pool" intuition captures
a specific methodological commitment: the "research faculty" outcome
operates on a survivors sub-sample of edge-creators, not on the full
population of edge-creators. Two-step filter:

- **Edge-creation (novelty) is measured at thesis stage, population-
  wide.** Every 1982–2010 PhD thesis in ProQuest contributes edges
  regardless of author's subsequent career.
- **Career outcome is measured years later, on a filtered sub-sample.**
  Whether the edge-creator becomes "research faculty" depends on US
  PhD-granting-institution employment + taking on a PhD student +
  that student appearing in the corpus.

So the discount comparison is technically: *"Among edge-creators who
ended up in PhD-granting-institution advisor roles, minorities need
higher novelty than majorities for similar advisor-pool membership."*
This is narrower than "minorities need higher novelty for similar
career outcomes." The narrowness matters for interpretation.

**Sharpening (2) — what Hofstra is actually studying.** The user's
intent-inference observation is correct. By using "research faculty"
as the narrow outcome, Hofstra is effectively asking a specific
question about the **reproduction of the academic class**: "do you
become someone who trains the next generation of PhDs?" This is
pipeline-continuity, not career-success-in-general.

A minority researcher who becomes a highly-cited industry researcher,
or a teaching-focused professor at a liberal arts college, or a
research scientist at a national lab — none count as "research
faculty." These are substantial career successes; they're just not
*academic-reproduction* successes.

The broader "does innovation pay off for minorities?" question
requires the broader "continued researcher" definition (Hofstra's
secondary outcome). That the discount holds on both is Hofstra's
evidence that the result isn't an artifact of the narrow definition —
but the magnitudes differ, and the broader-definition numbers aren't
in the same headline form in the main text.

**Selection mechanisms, demographically non-neutral.** Each of the
three filtered career paths the user identified has demographic
correlations:

- **Industry research.** Asian researchers (especially in CS/ML) may
  be over-represented at Google Research, Microsoft Research, Meta AI,
  etc. Excluding industry systematically excludes this subpopulation
  from the "research faculty" measurement even if they're doing
  high-impact research.
- **Non-research positions & teaching-focused academia.** Women are
  historically over-represented at teaching-focused and non-research-
  primary positions. The institution-type filter is thus not gender-
  neutral.
- **Non-tenure research-track.** Research scientists, staff
  scientists, soft-money researchers. Filtered out despite doing
  research. Demographic patterns here depend on field.
- **Temporal skew from non-linear careers** (user's observation). A
  person who goes industry → academia → eventually TT advisor is
  systematically later than linear-path peers. Women often have
  non-linear paths due to caregiving; some groups for economic or
  visa/geographic reasons.

**Alternative definitions and gap-change implications:**

| Definition | Expected gap change | Why |
|---|---|---|
| TT position at any institution (incl. liberal arts, foreign) | Smaller gap | Broader denominator; includes teaching-focused positions |
| h-index ≥ 10 by year 10 post-PhD | Smallest of common alternatives | Institution-neutral; productivity-based |
| Industry R&D employment | Possible inversion for some groups | Different selection dynamics by industry sector |
| Total 10-year citation count | Gap present but smaller | Impact-based, excludes no publishers |
| "Continued researcher" (Hofstra's broad) | Gap present, smaller than research-faculty | Includes WoS publishing; captures non-academic trajectories |

General principle: narrower definitions (higher institutional filter,
stricter career-path linearity) show larger gaps; broader definitions
show smaller gaps. Discount has both an *institutional-exclusion
component* and a *residual among-survivors component*.

**The edge–edge vs creator–creator asymmetry.** Hofstra's data
structure allows measuring every new edge regardless of the creator's
later career. But the discount finding conditions on the creator
surviving in the academic-reproduction pool. Hidden imbalance:

- Novelty time series: complete measurement (all edges).
- Career-discount time series: survivor-biased measurement (only
  academic-reproduction survivors).

If demographic groups have different academic-pipeline survival
rates *independent of novelty*, the career-discount gap is
contaminated by differential pipeline survival. Some of the
"discount" could be "some demographic groups leave academia for
non-academic-but-successful careers at higher rates, so we don't see
their late-career outcomes." This is not the same as Hofstra's
interpretation ("minorities get less credit for their novelty") but
it's consistent with the observed data.

**Connection to ws2 — three structural commitments derived from this
SQ.**

User asked: "anything we could do differently beyond explicit ack
given our core hypothesis?" The SQ surfaces three design
commitments that address survivor-bias structurally, not just via
acknowledgment.

**(a) Multi-window lookahead reporting** for Test IV persistence
extension (modifies pending batch item 7). Instead of anchoring on
C_15 alone, report regression at C_5, C_10, C_15 in a single table.
Stability across windows = robustness claim; divergence = substantive
finding about observation-window dependence. Each paper enters each
measurement at the appropriate post-publication stage. Cost: 2×
additional regression runs (trivial), 3 columns in main table.
Benefit: sharpens interpretability; aligns with metric-plurality
desideratum §8.

**(b) Per-active-year normalization** for item 11 production-capture
aggregate decomposition (modifies pending batch item 11). Instead of
$N(G, Y)$ = total new links by group G in year Y, use $N(G, Y)$ =
*mean new links per active group-G author in year Y* (active =
published ≥1 paper in Y). This isolates per-capita production from
pipeline-survival effects. A minority author who leaves the corpus
in 1995 contributes to the mean through 1994, then drops from the
denominator — they don't count as "zero production" in later years;
they just aren't counted. Cost: moderate; requires author-level
active-years tracking (low incremental given we're already doing
author-level demographic attribution). Benefit: substantially cleaner
substantive interpretation of item 11 results.

**(c) Explicit pipeline-survival sub-analysis** (new sub-item under
item 11). Define "pipeline survival" = publishing ≥1 paper in any
5-year window spanning ≥10 years post-first-publication. Report
pipeline-survival rates per demographic group. If minorities show
lower pipeline-survival independent of novelty, item 11's analysis
is contaminated by pipeline attrition. Worth documenting separately
so readers can see whether it drives the main result.

All three commitments documented in SQ12 → pending Phase 0.2 batch
updates (see running batch summary).

**What ws2 doesn't adopt from this SQ.** Two things considered and
rejected:

- **IPCW / survival-aware estimators.** Methodologically rigorous
  but substantially more complex. Cost-benefit doesn't favor for
  ws2's scope. Available if reviewers push on censoring bias.
- **Multiple imputation for missing post-corpus data.** Requires an
  imputation model (what would a minority author who left in 1995
  have produced in 2005?). The imputation model is itself a
  substantive commitment that could shift results. Without strong
  theoretical grounding, adds complexity without interpretive gain.

**One-sentence summary.** "Research faculty" is a narrow academic-
reproduction outcome that filters out industry research, teaching-
focused academia, non-tenure research-track, and non-linear career
paths — each demographically non-neutral. The discount holds on both
narrow and broad definitions (Hofstra reports both), but the
survivor-bias concern is real and structurally matches the kind of
concern that applies to ws2's Test IV persistence and item 11
production-capture decomposition. Three structural commitments
derived from this SQ: (a) multi-window lookahead reporting for
persistence; (b) per-active-year normalization for item 11; (c)
explicit pipeline-survival sub-analysis for item 11. These move
beyond explicit acknowledgment to design-level survivor-bias
handling.

### SQ13 — URM per-group inference accuracy heterogeneity

Working session with user, 2026-04-24.

**User's first-pass intuition.** *"Other than team-level tests I don't
see this question helping us much."* The intuition is largely correct
— we've already absorbed most of the methodological lesson into ws2's
commitments (Lockhart-2023-grounded weight-by-confidence policy,
region-of-origin stratification in plan subsection 9). Walkthrough
confirms this intuition and surfaces three marginal extras.

**Per-group accuracy heterogeneity (SI p. 14).** After all methods
including auxiliary:

- White: 97.2%
- Asian: 93.4%
- Hispanic: 70.4% raw → ~83% after Sood-Laohaprapanon auxiliary
- AA: 9.9% raw → ~74% after auxiliary
- NA: worst of all; auxiliary doesn't fully fix

**Three specific consequences of URM pooling.**

**(1) URM is a compositional average over subpopulations with
heterogeneous inference accuracy.** URM classifications have roughly
20–25 percentage points more misclassification than white
classifications. The URM-vs-white contrast is structurally
"(83%-accurate Hispanic + 74%-accurate AA + small NA) vs. 97%-
accurate white."

**(2) Subgroup-specific dynamics are invisible.** "URM introduces
more novelty" could be driven primarily by Hispanic, primarily by
AA, equally by both, or by opposite effects that partially cancel.
Hofstra's pooled analysis can't tell us which. The same ambiguity
propagates to the distal-novelty mediator.

**(3) Intersectional analyses limited to 2×2 cells.** Gender × race
in Hofstra is 2 × 2 (white women, white men, nonwhite women, nonwhite
men). With better inference, intersectional analysis at 2 × 3 level
(separate Hispanic, AA cells) becomes possible — revealing whether
gender gaps operate uniformly across racial subgroups or differently.

**How you'd decompose with better inference.** Given perfect
demographic inference:

- **Separate per-subgroup regressions:** Hispanic-vs-white, AA-vs-
  white, NA-vs-white analyses in parallel. Compare effect sizes. If
  URM aggregate finding holds for each subgroup, aggregate is
  meaningful. If subgroups differ substantially, URM is a statistical
  artifact hiding real heterogeneity.
- **Formal test of aggregation validity:** test whether per-subgroup
  coefficients are statistically indistinguishable. If yes, URM
  makes sense; if no, URM aggregates distinct populations.
- **Finer intersectional analyses:** 2 × 3 or finer cells with
  meaningful sample sizes.
- **Pipeline decomposition by subgroup:** differential career
  outcomes within URM.

Hofstra is explicit in SI that the URM pooling is *forced* by
inference accuracy, not preferred. With their 10% AA accuracy (pre-
auxiliary) and 74% (post-auxiliary), per-subgroup analysis would have
too much misclassification noise to be reliable. The aggregate is
defensive, not substantive.

**ws2 relevance — user's intuition validated with three marginal
extras.**

The main lesson is already absorbed into ws2 via the Lockhart-
grounded weight-by-confidence policy and the region-of-origin
stratification commitment (plan subsection 9). Our stratification is
finer (Anglo / East Asian / South Asian / Arabic-speaking / Slavic /
Latin / other) than Hofstra's white / Asian / URM, and our NamSor +
Genderize approach provides better per-region accuracy than
Hofstra's Census-and-Sood approach.

**SQ13 validates these existing commitments rather than motivating
new ones.** Three marginal extras surface from the SQ but are
low-priority:

**(a) Rao's Q distance-metric granularity.** Our Rao's Q uses uniform
Hamming distance between demographic states. SQ13's logic suggests
non-uniform weights (e.g., some demographic boundaries are more
culturally meaningful than others). For ws2 primary analysis, uniform
Hamming is defensible (transparent, convention-matching). Non-uniform
could be a Stage 3 robustness check — low priority.

**(b) Item 11 stratification level — worth noting in pre-
registration.** We're committed to per-demographic-group decomposition.
Question of granularity: at 7-region level (finer) vs. pooled bins
(coarser). Trade-off: finer = cleaner interpretation, smaller per-
group samples; coarser = bigger samples, URM-style pooling concern.
**Small modification to item 11 pre-registration**: report primary at
finer granularity (7+ regions), collapse to coarser groups only for
robustness or secondary analysis.

**(c) Intersectional analyses in Stage 3.** Gender × region-of-origin
× career-stage is a 2 × 7 × 3 = 42-cell structure. Most cells will
have thin samples. Document as a structural possibility we explored;
report selectively where cell sizes permit. Stage 3 secondary, not
primary.

None of (a)–(c) are load-bearing commitments. The main "what we can
do differently" answer is that we've already done it: finer-granularity
demographic stratification is built into ws2 by design from the start.

**Net framing.** Hofstra's URM pooling is a forced choice from
inference limits, not a methodological preference. It creates real
measurement and interpretability costs (subgroup heterogeneity
invisible; compositional-average findings; intersectional analyses
limited). Ws2's region-of-origin stratification and weight-by-
confidence policy are already better-rigored than Hofstra's approach
on this dimension. SQ13 validates these choices rather than motivating
new ones; the three marginal extras are nice-to-haves for Stage 3
robustness rather than load-bearing commitments.

**One-sentence summary.** URM = Hispanic + AA + NA pooled with
heterogeneous per-subgroup inference accuracy (83% / 74% / worse);
aggregate findings are compositional averages that mask subgroup
differences, forced by inference limits not preferred methodology.
With better inference, per-subgroup decomposition + finer
intersectional analyses become possible. Ws2's region-of-origin
stratification + weight-by-confidence policy are already better-
rigored than Hofstra's on this dimension; SQ13 validates existing
commitments rather than motivating new ones.

**Small modification to pending batch.** Item 11 primary
operationalization: report demographic decomposition at region-of-
origin granularity (≥7 groups) rather than pooled coarser bins. This
is consistent with our existing commitments but makes the granularity
choice explicit in pre-registration.

### SQ14 — Career discount after controlling for distal novelty

Covered implicitly via SQ8 (distal-novelty methodology) and SQ11
(multi-arrow causal-identification limits). Factual answer: Hofstra
reports *partial mediation* — the career discount persists when
controlling for distal novelty (the reported 3.5% → 9.5% / 4.3% →
15% numbers include distal as a control), but shrinks relative to
the no-control version. The paper states explicitly (p. 9287):
*"These results hold over and above of the distance between newly
linked concepts."* Residual discount beyond distal suggests other
mechanisms (direct discrimination, network access, pipeline
constraints) contribute. Consistent with the multi-arrow causal
structure in SQ11 — distal novelty is one mediator among several
unidentified pathways.

**Small modification to Test IV persistence extension (pending batch
item 7):** report β_3 (the T_p × N_p interaction coefficient) under
multiple control specifications — without novelty-structure controls,
controlling for distance-from-canonical-centroid (our secondary
novelty metric), controlling for subfield fixed effects, full control
set. Coefficient stability across specs is robustness; substantial
shrinkage under specific controls suggests those controls mediate
part of the relationship. Nice-to-have sensitivity reporting, not a
new pre-registration item; aligns with the partial-mediation framing
SQ14 introduces.

---

**When to fill in the pending entries.** These are extra-credit relative
to the Challenge Corner (C1–C11); the Challenge Corner is load-bearing
for ws2's methodology decisions, the Study Questions are primarily
educational. Fill in incrementally when the user wants to work through
a specific one, or leave as-is.
