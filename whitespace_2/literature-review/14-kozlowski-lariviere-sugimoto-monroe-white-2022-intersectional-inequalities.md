# 14 — Intersectional Inequalities in Science

**Authors:** Diego Kozlowski, Vincent Larivière, Cassidy R. Sugimoto, Thema Monroe-White
**Venue:** *PNAS* 119(2): e2113067119 (Jan 2022)
**PDF:** `literature-review/14-kozlowski-lariviere-sugimoto-monroe-white-2022-intersectional-inequalities.pdf` (gitignored — main + SI bundled)
**SI:** same path, suffixed `_SI.pdf`
**DOI:** 10.1073/pnas.2113067119

---

## Background

Kozlowski et al. is the canonical large-scale **intersectional**
analysis of US scientific authorship — combining race AND gender at
the author-level, AND linking these to topic AND citation outcomes,
on a 5.4M-article WoS corpus (2008–2019). The intersectional framing
is from Crenshaw 1989 / Collins 1990 / Mustafaa 2014; the empirical
machinery is Larivière 2013-style name-based gender inference plus
US Census-derived family-name racial-group probabilities.

This is the **second-highest post-N1-priority Tier-2 paper** for ws2
because it is the methodological template for **how to report
intersectional cells under demographic-inference uncertainty**.
Phase 0.2 pre-registration's §9a Principle 5 commitment to a
bias-uncertainty band over name-inferred demographics inherits
Kozlowski's fractional-counting approach. The CV-of-topic-distribution
diagnostic Kozlowski introduces is also methodologically portable to
our §11 cluster-entropy reporting.

For ws2, the paper splits into:
1. **Methodology import:** fractional probabilistic counting (the
   "soft assignment" pattern), CV as a specialization diagnostic.
2. **Mechanism hypothesis:** Kozlowski's documented finding that
   minoritized authors specialize on lower-cited topics is a
   *specific mediator* candidate for ws2's claim #13. Our headline
   pattern (demographic plurality rises, intellectual plurality
   stagnates) could be partially mediated by within-field topic
   specialization. Worth integrating in Discussion.
3. **Methodological boundary:** Kozlowski uses binary gender + US
   Census racial categories + US-only first-author restriction.
   ws2 uses gender-only (no race), country-stratified (multi-national),
   non-US-restricted. Methods must explicitly note these divergences
   to prevent reviewer-confusion about why we don't replicate
   Kozlowski's full intersectional 4×2 grid.

This is not a fatal-surface paper — all our existing Phase 0.2
commitments survive Kozlowski's Methods. The paper *enriches* our
methodology and Discussion framing rather than overturning anything.

---

## Key Ideas

### 1. The fractional probabilistic counting pattern

This is **the** load-bearing methodology for ws2's §9a P5 Phase 0.2
commitment. Kozlowski operationalize it precisely:

> "we use the top five words from each topic to infer its semantic
> content. … Each article is defined as a distribution over topics
> from each topic to infer its topicality. Given an article's topic,
> there are some words that are more likely to repeat than others
> … we do not assign authors to a unique racial category. In
> previous work, we have shown that, given the overlap of Black and
> White family names, the use of a threshold—filtering those names
> with a probability in a single group above a threshold and
> assigning all authors with that name to a single category—
> underestimates the proportion of Black authors. This distinction
> is critical."

Operationally:
- Each author has `P(race ∈ {Asian, Black, Latinx, White})` from the
  US Census family-name distribution.
- Each author has `P(gender ∈ {man, woman})` from Larivière 2013-style
  inference.
- Each article has `P(topic = t)` for `t ∈ {1, …, K}` from LDA.
- Aggregate counts use **fractional weights** — an article contributes
  `P(race=R) × P(gender=G) × P(topic=t)` to the cell `(R, G, t)`.
- Citations are aggregated the same way: an article's citation count
  is fractionally distributed over the joint cells.

The mechanical contrast with thresholding: if you threshold at
`P(race=Black) > 0.7` and assign authors only when above the
threshold, you systematically lose authors near the boundary.
**Kozlowski demonstrates** (citing their own Coupling 2017 work)
that this systematic loss disproportionately affects Black authors
because of family-name overlap with White authors. **This is the
direct methodological lineage Lockhart 2023 P5 builds on**, and it's
why ws2 has already committed to fractional counting (Phase 0.2).

The paper doesn't explicitly call this "soft assignment" or
"probabilistic counting" — they just *do* it. For our Methods
section, we should:
1. Cite Kozlowski 2022 + Lockhart 2023 P5 as the methodology
   ancestor.
2. Describe our specific implementation: per-author probabilities
   from gender_guesser+Genderize+NamSor (combined), per-paper
   fractional contributions to (gender × country × subfield) cells.
3. Note that ws2 does NOT use race inference — see §3 below for the
   reasoning.

### 2. LDA topic modeling at scale (200-300 topics)

Kozlowski's topic-level resolution is fine: **200 topics for Health
(n=142,032 articles), 300 topics for Social Sciences/Humanities/
Professional Fields (n=283,589 articles).** This is at the higher end
of what makes interpretable topics — they call out the "trade-off
between granularity and repetition of topics" and acknowledge "manual
inspection" was needed to optimize K per discipline.

Examples of Kozlowski's discovered topics:
- Black-author overrepresented: African-American culture (Topic 122
  "black women violation"), African studies, racial discrimination,
  US communities, religion, language literacy
- Asian-author overrepresented: stocks/consumers/firms/markets, China
- Latinx-author overrepresented: Latin-American countries, language
  literacy
- White-author overrepresented: spread across many topics (low CV)
- Asian-women specialized: nursing, pregnancy, education, China
- Health gender split: Men more cited along the topic-citation
  distribution; women more cited at high-citation topics; topic-by-
  topic gap is small but compounded by topic distribution gap

**Why ws2 doesn't use LDA:** plan §3 + §11 commit to embedding-cluster
subfield identification (K=50 SPECTER2-stratified cluster fit).
LDA-based and embedding-cluster-based topic identification serve the
same FUNCTIONAL role (group articles into semantically coherent
buckets at appropriate granularity for diversity metrics) but rest on
different assumptions. Embedding clusters capture latent geometric
structure in fp16 vectors; LDA captures word-co-occurrence structure
on title+abstract+keywords. Plan §11's choice of embedding clusters
is justified by:
- Avoidance of keyword-match anachronism (per Check 2d findings)
- Better cross-era stability (LDA topics drift more aggressively as
  vocabulary changes)
- Direct compatibility with our §11 stratified-fit commitment

For Methods: **note that we adopt Kozlowski-style fractional counting
WITHOUT adopting Kozlowski-style LDA topic modeling.** The two are
methodologically separable.

### 3. Why Kozlowski uses race AND ws2 does not

Kozlowski uses race because their research question is about US
*intersectional* inequality. ws2 doesn't infer race, per ws2
desiderata exclusion (race/ethnicity inference is unreliable per
Lockhart 2023's reported 65–73% error rates for Black and MENA
subgroups).

**The methodological asymmetry matters:** Kozlowski uses US Census
family-name probabilities, which they validate works on US-context
data. The Lockhart critique applies *globally* but most strongly to
non-Western names. ws2's multi-national scope means we'd be
applying US-centric racial categorization to (e.g.) Chinese or
Indian authors where the US Census categories don't even map. The
right move is to NOT infer race; this is what we've committed to.

**For Methods:** explicitly cite Kozlowski as a reference point and
state why we depart. Suggested language: *"Kozlowski et al. 2022
combine name-based race inference with name-based gender inference
to study intersectional inequalities in US science. Our work follows
their fractional-counting methodology for demographic categories
where inference is defensible (gender, country, prestige tier) but
explicitly excludes race inference, following Lockhart et al. 2023
Principle 1 (critical refusal)."*

### 4. The CV-of-topic-distribution diagnostic [METHODOLOGY ADDITION]

Kozlowski page 3: "Fig. 2 also shows the coefficient of variation
(CV) for each racial group's proportion on topics. A high CV means
that the group has a high participation on some topics and a small
participation on others, relative to its average proportion. Asian
authors present the highest CV, while White authors exhibit lowest.
This suggests that Asian authors are highly specialized, focusing
on certain topics, while White authors are present in a wider range
of topics."

This is a **portable diagnostic** for ws2's §11 cluster-entropy
reporting. The metric:

```
CV(group g) = sd(p_g across clusters) / mean(p_g across clusters)
```

where `p_g(k) = fraction of group g's articles in cluster k`.

Interpretation:
- **High CV** → group is specialized on a subset of clusters (low
  diversity-of-engagement)
- **Low CV** → group is ubiquitous across clusters (high
  diversity-of-engagement)

**For ws2, adding CV-by-region (or CV-by-gender) alongside our
cluster-entropy headline gives a Kozlowski-style "specialization vs
ubiquity" decomposition.** This is a *small* methodological addition
on top of the existing §11 commitment — we're already computing
per-cluster occupancy by demographic cell; CV is a cheap derived
statistic.

For our Methods: include CV-by-(name-region, gender) as a row in
the §11 cluster-fit reporting table, alongside cluster entropy and
effective number of clusters (effN). Three statistics report:
spread (effN), inequality (Gini), specialization (CV).

This is a **minor surface** — not a commitment change but a
"consider adding."

### 5. The compound-mechanism finding

Kozlowski's substantive finding (Discussion):

> "We found that differences in research impact can be at least
> partially explained by topics' citation density but that within-
> topic differences remain. The compound effect of different citation
> rates of topics and unequal distribution on topics by race and
> gender leads to negative effects for marginalized groups and for
> science itself, as some topics become systematically less studied."

The mechanism has two parts:
1. **Between-topic component:** minoritized groups are over-represented
   in lower-cited topics.
2. **Within-topic component:** even within the same topic, citation
   gaps persist (Fig. 3).

The compound effect is multiplicative — a minoritized group's expected
citation differs from White-male's by both the *topic-citation gap*
and the *within-topic citation gap*.

**For ws2's claim #13**, this is a mechanism hypothesis worth
integrating into Discussion. Our headline pattern (demographic
plurality rises but intellectual plurality stagnates) could be
*mechanistically* mediated by:
- Demographic plurality rising → more minoritized scientists in
  the workforce.
- BUT topic-specialization patterns mean minoritized scientists
  cluster into specific (often lower-cited) sub-areas.
- → The semantic-cluster diversity at the workforce level rises
  more slowly than the headcount diversity.
- → Intellectual plurality (cluster entropy) stagnates relative to
  demographic plurality (gender × country × prestige Shannon).

This is a *plausible* mediator; ws2 doesn't need to *prove* it, but
Discussion should flag it as one of the candidate explanations for
the observed decoupling.

### 6. The counterfactual exercise

Kozlowski end of Discussion (page 6):

> "Assuming constant productivity and considering the career age of
> authors, we can estimate the cumulative loss in citations over the
> past 40 y. If the author distribution over the last 40 y would have
> matched the 2010 US Census, there would have been 29% more articles
> in public health, 26% more on gender-based violence, 25% more in
> gynecology and gerontology, 20% more on immigrants and minorities,
> and 18% more on mental health."

This is a **bold counterfactual claim** — "what topics would have
been more researched if demographics had matched US population." It
takes a particular interpretive license (constant productivity per
author of any race/gender) but the rhetorical move is striking.

**For ws2:** the counterfactual exercise pattern is portable. Our
claim #13 enables a similar exercise: *"if intellectual plurality
had matched the rise in demographic plurality, what would the
cluster-occupancy distribution look like, and what subfields would
have grown faster?"* This is Discussion material, not Phase 0.2
pre-registration content, but worth flagging as a high-impact
narrative move for the ws2 paper.

### 7. Limitations Kozlowski explicitly flag

Three from their Discussion that map to ws2:

1. **Causal modeling deferred.** "Causal modeling that considers
   topic choice, along with markers of prestige, would be germane
   in understanding the different mechanisms through which systemic
   inequalities are mediated." → ws2's Test IV (team-diversity ×
   novelty) is more causal than Kozlowski's descriptive analysis;
   we should position this as a step beyond Kozlowski.

2. **US-context limitation.** "Racial categories used in this
   research are only meaningful in the context of the US academic
   workforce; further research should be performed to understand
   general patterns across the globe." → ws2's multi-national
   country-stratified design directly addresses this.

3. **Other axes deferred.** "However, race and gender are not the
   only spaces of inequality in science; several other variables
   should be included to create a fully intersectional understanding
   of inequalities in science. Socioeconomic status, … disability,
   sexual orientation — variables that are often excluded or
   underreported in studies of the scientific workforce." → ws2
   includes prestige tier, training-institution, career stage, but
   not the deeper axes (disability, sexual orientation, SES) per
   our desiderata exclusions.

---

## Three-Level Results

### Smart-high-schooler reading (~5 min)

This paper looked at 5 million scientific papers from 2008-2019 to
ask: who writes about what topics, and who gets cited?

The authors used clever statistical inference to figure out, just from
authors' names, the gender (man/woman) and racial group (Asian, Black,
Latinx, White) of each paper's first author. They found:

1. **White and Asian authors write more papers; Black and Latinx
   authors write fewer.**
2. **Different racial-gender groups specialize in different topics.**
   Asian male authors are highly concentrated on stocks/markets/firms;
   Black authors on African American culture and racism research;
   Latinx authors on Latin American topics. White authors are spread
   across more topics.
3. **The topics that Asian and White men work on tend to get more
   citations** than the topics that Black and Latinx authors work on.
4. **Minoritized authors get fewer citations EVEN ON THE SAME TOPIC**
   as White/Asian male authors.
5. The combination of (3) and (4) makes the inequality multiplicative.

For our project: this paper is a methodology textbook on how to do
fair statistical analysis when each author has uncertain demographics.
We'll borrow their "fractional counting" technique (each author
contributes a *probability* to each demographic group, not a hard
assignment). We won't borrow their racial-categorization scheme,
because it's US-specific and our project is multi-national.

### Junior/senior-undergraduate reading (~15 min)

Kozlowski et al. tackle intersectional inequality in science by
linking three things at scale:
- **Author demographics** (race × gender, inferred from first names
  and family names with US Census-derived probabilities).
- **Article topics** (Latent Dirichlet Allocation on
  title+abstract+keywords; 200 topics for Health, 300 for
  Social Sciences).
- **Citation outcomes** (field-normalized citation counts).

The methodological key is **fractional probabilistic counting**: each
author has a probability distribution over racial groups (e.g., name
"Smith" might have P(White)=0.7, P(Black)=0.2, P(Asian)=0.05, …)
and over genders. Each article is fractionally counted in each
intersectional cell weighted by these probabilities. Citation
analysis is similarly fractional. This avoids the threshold-
sensitivity problem Kozlowski's earlier work documented (citing
Coupling et al. 2017): hard-assignment by probability cutoff
systematically under-counts minoritized authors.

The empirical findings are striking:
- **Asian and White first authors** are over-represented; Black and
  Latinx first authors under-represented.
- **Topic specialization differs sharply** by intersectional cell.
  Coefficient of variation across topics is highest for Asian
  authors (~0.19 in Social Sciences) and lowest for White authors
  (~0.03). Asian authors are highly specialized; White authors are
  ubiquitous.
- **Compound inequality:** topics with higher Asian-male
  participation get more citations; minoritized authors get fewer
  citations even within the same topic. The two effects multiply.

The paper's substantive intervention is the **counterfactual exercise**
(Discussion p.6): if author distribution had matched 2010 US Census,
public health research would have been 29% more abundant, gender-based
violence 26%, etc. This claims a real (not just perceived) loss in
the scientific endeavor from skewed demographic composition.

The Discussion ends with policy recommendations:
1. Recognize knowledge gaps related to author race and gender
   segregation.
2. Funding agencies should increase support for under-represented
   research areas.
3. Promote diverse participation within high-impact topics.

For ws2, the load-bearing inheritance is the **fractional counting
methodology** for our §9a P5 Phase 0.2 commitment, and the
**CV-of-topic-distribution** as a useful addition to our §11 cluster-
entropy reporting. The substantive findings are mechanism candidates
for our Discussion's interpretation of claim #13.

### Early-grad reading (~30 min)

Kozlowski et al. is a methodologically careful, ambitious empirical
paper combining four research-traditions:

1. **Bibliometric author-disambiguation + name-based demographic
   inference** (Larivière 2013 on gender; the authors' own prior work
   on race using Census family-name distributions).
2. **Topic modeling at scale** (200-300 topics, manually curated K).
3. **Field-normalized citation analysis** (per-citation-window
   normalization to avoid field-level baseline differences).
4. **Intersectional theory** (Crenshaw 1989; Collins 1990) applied
   quantitatively at the macroscale.

The probabilistic-counting innovation is methodologically subtle.
Their prior work (Kozlowski et al. 2018, *Proceedings of the 18th
ISSI Conference*) demonstrates that thresholding by name-region
probability (e.g., assigning to "Black" only if `P(Black) > 0.5`)
**systematically biases the resulting counts** because the
probability-distribution overlap between Black and White family
names is meaningful and not symmetric. The fractional-counting
solution is to keep each author's full probability distribution
intact and aggregate at the cell level using probability-weighted
contributions — analogous to expected-value computation rather than
maximum-a-posteriori assignment.

The LDA topic modeling is fairly conventional, but Kozlowski's
choice to fit *separate* LDA models per discipline-cluster (Health
vs Social Sciences/Humanities/Professional Fields) is unusual.
Their motivation: 200 topics on a 142K-article Health corpus produces
interpretable topics with manageable repetition; the same model on
the broader corpus produces less coherent topics. Phase 0.2 may
benefit from a similar choice — we cluster *separately* on CS and
Physics rather than jointly, to maximize within-discipline
interpretability of clusters.

The CV-of-topic-distribution is the methodological innovation most
directly portable to ws2. Conventional intersectional analysis
reports cell-level citation gaps; Kozlowski adds the
specialization-vs-ubiquity diagnostic that decomposes "are we
talking about a few specific cells or a population-wide phenomenon?"
This is the kind of diagnostic that survives review-cycle scrutiny
because it's mechanistically interpretable and a single-number summary.

The compound-mechanism finding — citation gaps from BOTH topic
selection AND within-topic differences — is methodologically
important for two reasons:
1. **It rules out** purely between-topic explanations. If only
   topic selection drove the gap, equalizing topic distributions
   would close it. Kozlowski show within-topic gaps remain.
2. **It rules out** purely within-topic explanations. If only
   within-topic citation differences drove the gap, the topic
   distribution would be irrelevant. Kozlowski show topic
   distribution matters substantially.

The mechanism is *multiplicative*, which is the formal pattern of
intersectional inequality (Crenshaw's original framework) — neither
race nor gender nor topic alone explains the gap; their joint
distribution does.

For ws2 — particularly relevant for our Test IV (team-diversity ×
novelty) — Kozlowski's compound-mechanism finding suggests that
team-level demographic diversity should mediate paper-level novelty
through both *topic-selection* effects (diverse teams pick different
topics) and *within-topic* effects (diverse teams tackle topics
differently). Our Test IV regression should pre-register both
mediators if we can identify them. (This is a Phase 0.2 detail to
work through during the retro consolidation.)

The paper's limitations (US-only, binary gender, racial-category-
imposition-from-Census, deferred-causal-modeling) are honest and
shape what ws2 can claim differently. Our multi-national,
gender-only, country-stratified design is partially motivated by
exactly these gaps.

---

## Connection to Our Project

### What ws2 takes from Kozlowski

**1. Fractional probabilistic counting for §9a P5.** Phase 0.2
pre-registration commits to:

> "Following Kozlowski et al. 2022 and Lockhart et al. 2023 Principle
> 5, we use fractional probabilistic counting for demographic-
> inference uncertainty. Each author's contribution to a demographic
> cell is weighted by the inferred probability of that demographic
> assignment; each article's contribution to a (subfield × demographic)
> cell is the product of the per-author probabilities and the per-
> article subfield-membership probability. Aggregate diversity metrics
> are fractional sums; bootstrap CIs are computed over the joint
> probability distribution."

This goes in Methods §4 (Demographic features) AND §9a P5 (ORCID
validation), AND becomes a constraint on how we compute
cluster-entropy and gender-Shannon at the cell level.

**2. CV-by-region as a §11 diagnostic [methodology addition].** Add
to plan §11's cluster-fit reporting:

> "In addition to cluster entropy and effective number of clusters
> (effN), we report the coefficient of variation (CV) of cluster
> occupancy per demographic cell, following Kozlowski et al. 2022.
> CV captures specialization (high CV) vs ubiquity (low CV) of a
> demographic group's engagement with the cluster space."

This is a small addition to existing §11 commitment — we already
compute per-cell cluster occupancy.

**3. Per-discipline LDA observation, applied to clustering.** Kozlowski
fits LDA *per discipline* (Health vs Social Sciences). This pattern
is portable: ws2 should fit cluster models *separately* on CS and
Physics, not jointly, to preserve within-discipline interpretability.
Plan §11 already specifies CS-only or Physics-only fitting; this is
consistent with Kozlowski's pattern. For Methods: cite Kozlowski as
methodological precedent for per-discipline-fit clustering.

**4. Discussion mediator hypothesis.** Kozlowski's compound-
mechanism finding (between-topic + within-topic citation gaps)
provides a candidate mediator for ws2's claim #13:
- Demographic plurality rises (more minoritized scientists enter)
- BUT topic-specialization patterns concentrate them in specific
  sub-areas
- → Cluster-level diversity rises slower than demographic diversity
- → Decoupling

This goes in ws2 Discussion as a candidate-explanation paragraph.

**5. Counterfactual narrative pattern.** Kozlowski's "what if
demographics had matched Census" exercise is a high-impact
rhetorical move. ws2's claim #13 enables an analogous "what if
intellectual plurality had matched demographic plurality" exercise.
Discussion-section-level commitment, not Phase 0.2 pre-registration.

**6. Limitations to acknowledge.** Kozlowski's three flagged
limitations (causal-modeling deferred, US-only, deeper axes deferred)
shape ws2's positioning:
- ws2's Test IV (within-paper team-diversity × novelty regression)
  is a step toward causal modeling that Kozlowski explicitly defer.
- ws2's multi-national design directly addresses Kozlowski's US-only
  limitation.
- ws2 inherits Kozlowski's deeper-axes exclusion (no SES, disability,
  sexual orientation) per our own desiderata.

### What ws2 explicitly does NOT take from Kozlowski

1. **Race inference.** Per ws2 desideratum exclusions, supported by
   Lockhart 2023 P1. We use gender + country + prestige as our
   demographic axes; race not inferred.

2. **LDA topic modeling.** We use SPECTER2 embedding-cluster subfield
   identification per plan §11. Different mechanism, similar
   functional role. Methods explicitly note the divergence.

3. **Binary gender (M/F only).** We use Lockhart 2023 P2 ascribed-X
   terminology and acknowledge the trans / nonbinary gap explicitly.
   Kozlowski doesn't.

4. **US-only restriction.** We are multi-national with country
   stratification.

5. **The specific "20% more articles on X" counterfactual numbers.**
   Their estimates are US-specific and depend on the constant-
   productivity assumption. ws2's analogous counterfactual would have
   different inputs and outputs.

### Specific design implications for ws2

| Phase 0.2 commitment | Kozlowski-driven content |
|---|---|
| §4 demographic-features Methods paragraph | Cite Kozlowski for fractional-counting precedent |
| §9a P5 ORCID-validation methodology | Lockhart P5 + Kozlowski 2022 as the methodology lineage |
| §11 cluster-fit reporting | Add CV-by-region as a third statistic alongside entropy and effN |
| §11 fit-per-discipline | Cite Kozlowski as precedent for per-discipline modeling |
| Discussion mediator paragraph | Cite Kozlowski's compound-mechanism finding as candidate mediator for claim #13 |
| Limitations | Kozlowski's deferred-axes echo our own |
| Counterfactual narrative (Discussion) | Pattern import |

### How ws2 cites Kozlowski in framing

In Methods §4:

> "We adopt the fractional probabilistic counting methodology
> developed by Kozlowski et al. (2022) for handling demographic-
> inference uncertainty. Each author's contribution to a demographic
> cell is weighted by the inferred probability for that cell rather
> than thresholded; this avoids the systematic biases that
> assignment-by-threshold introduces against minoritized groups
> with high family-name overlap (Kozlowski et al. 2018). Our
> implementation differs from Kozlowski et al. 2022 in three ways:
> (1) we infer gender and country but not race, following Lockhart
> et al. 2023 Principle 1; (2) we are multi-national rather than
> US-restricted; (3) we use embedding-cluster subfield
> identification per §11 rather than LDA topic modeling. The
> fractional-counting methodology applies identically across these
> differences."

In §11 reporting:

> "Cluster occupancy by demographic cell is reported with three
> statistics: cluster entropy (Shannon), effective number of
> clusters (effN = exp(entropy)), and coefficient of variation
> (CV) of cluster occupancy across the K=50 cluster bins.
> Following Kozlowski et al. 2022, CV captures specialization
> (high CV) vs ubiquity (low CV)."

In Discussion candidate-mediator paragraph:

> "One candidate mechanism for the observed decoupling between
> demographic and intellectual plurality is the compound-effect
> finding of Kozlowski et al. (2022): minoritized authors are
> over-represented in lower-cited topics AND face within-topic
> citation gaps, with the two effects compounding. If demographic
> diversification draws minoritized scientists into specific
> subfield clusters disproportionately, the cluster-occupancy
> distribution may diversify slower than the headcount-level
> demographic distribution. This is a hypothesis ws2 generates
> but does not test directly; Test IV (within-paper team-diversity
> × novelty) is the closest test in our pre-registration."

---

## Key Quotes

| # | Quote | Page | Use |
|---|---|---|---|
| Q1 | "we do not assign authors to a unique racial category. … the use of a threshold—filtering those names with a probability in a single group above a threshold and assigning all authors with that name to a single category—underestimates the proportion of Black authors. This distinction is critical." | p. 2 | LOAD-BEARING — fractional-counting methodology |
| Q2 | "Aggregate proportions are obtained using fractional counting over these three dimensions." | p. 2 | Methodology citation for §9a P5 |
| Q3 | "Asian authors present the highest CV, while White authors exhibit lowest. This suggests that Asian authors are highly specialized, focusing on certain topics, while White authors are present in a wider range of topics." | p. 3 | CV-as-diagnostic methodology import |
| Q4 | "We found that differences in research impact can be at least partially explained by topics' citation density but that within-topic differences remain. The compound effect of different citation rates of topics and unequal distribution on topics by race and gender leads to negative effects for marginalized groups and for science itself." | p. 6 | Discussion mediator hypothesis |
| Q5 | "If the author distribution over the last 40 y would have matched the 2010 US Census, there would have been 29% more articles in public health, 26% more on gender-based violence, 25% more in gynecology and gerontology, 20% more on immigrants and minorities, and 18% more on mental health." | p. 6 | Counterfactual narrative pattern |
| Q6 | "Racial categories used in this research are only meaningful in the context of the US academic workforce; further research should be performed to understand general patterns across the globe." | p. 6 | Limitations divergence — ws2 is multi-national |
| Q7 | "Causal modeling that considers topic choice, along with markers of prestige, would be germane in understanding the different mechanisms through which systemic inequalities are mediated." | p. 6 | ws2's Test IV is a step toward this |
| Q8 | "However, race and gender are not the only spaces of inequality in science; several other variables should be included to create a fully intersectional understanding." | p. 6 | Limitations — ws2 inherits deeper-axes exclusion |
| Q9 | "(58)…we have shown that, given the overlap of Black and White family names, the use of a threshold … underestimates the proportion of Black authors." | p. 2 | Methodological citation lineage (Kozlowski 2018) |

---

## Study Questions

### Basic (factual recall)

- **B1.** What is Kozlowski's corpus size (publications, year window,
  database)?
- **B2.** What inference methods do they use for race and gender?
- **B3.** How many topics are in their LDA model (Health vs Social
  Sciences)?
- **B4.** Which racial-gender groups are over-represented in US
  science publications? Which are under-represented?
- **B5.** What is the coefficient of variation of topic distribution
  for Asian authors? For White authors?
- **B6.** What is the counterfactual claim about public-health
  research?

### Intermediate (synthesis)

- **I1.** Why does threshold-based assignment of authors to racial
  groups systematically under-count Black authors?
- **I2.** What does "fractional counting" mean in practice — give a
  numerical example with a hypothetical author having P(Black)=0.4,
  P(White)=0.6, gender=woman, contributing one paper.
- **I3.** Why does Kozlowski use 200 topics for Health and 300 for
  Social Sciences? What's the trade-off?
- **I4.** The compound-mechanism finding has two parts. State each
  and explain why ruling out either part alone wouldn't fully
  account for the citation gap.
- **I5.** Why is the CV-of-topic-distribution diagnostic
  *interpretable* in a way that simple per-cell citation gaps
  aren't?

### Advanced (engagement)

- **A1.** ws2 commits to fractional probabilistic counting per
  Kozlowski. But our gender inference produces *one* probability
  per author (P(woman)) rather than a multi-class distribution.
  How does the fractional-counting machinery adapt? Specifically,
  if our embedding cluster-fit returns hard assignments (each paper
  belongs to one cluster), how do we fractionally aggregate
  (gender × country × cluster) cells?
- **A2.** Kozlowski uses LDA topic modeling. ws2 uses SPECTER2
  embedding cluster fitting. Both serve the same functional role
  (group articles into semantically coherent buckets). Should ws2's
  Methods justify this choice substantively, or merely note it as
  a different choice? Draft a one-paragraph justification.
- **A3.** Kozlowski's compound-mechanism finding suggests a
  mediator for ws2's claim #13. Could Test IV (within-paper
  team-diversity × novelty regression) test this mediator
  explicitly, or only indirectly? What additional measurements
  would make the mediation test direct?
- **A4.** Kozlowski's counterfactual exercise assumes constant
  productivity per author. What's the analogous assumption for
  ws2's claim #13 counterfactual ("what if intellectual plurality
  had matched demographic plurality")?
- **A5.** Kozlowski's data is 2008-2019; ws2's window is 1970-2024.
  Are Kozlowski's findings expected to hold longitudinally over
  ws2's longer window? What empirical pattern in ws2 would
  *replicate* Kozlowski's finding, vs *extend* it?

---

## Challenge Corner

These are questions where ws2 has to push back on or extend
Kozlowski's framing. To be addressed during the collaborative review.

### CK1 — The CV diagnostic — is it always interpretable?

CV is interpretable when the underlying distribution is roughly
log-normal or skewed. For our cluster-occupancy distribution at K=50
with ~10% per-decade strata, the per-cell counts are SMALL (e.g.,
30-50 papers per (year × cluster) cell pre-aggregation). CV at
small N is noisy. **Should ws2 commit to a minimum N per (group ×
cluster) cell before reporting CV?** Kozlowski had ~5M articles;
their per-(racial group × topic) cells average several thousand
articles. Our per-(year × cluster × demographic-cell) is much
smaller.

### CK2 — Counterfactual narrative — risks of overclaiming

Kozlowski's "29% more articles on X" claim is striking but assumes
constant productivity per author. Critics could note that
demographics that affect topic *choice* might also affect productivity
or quality — confounding the counterfactual. **Does ws2 want to
adopt this rhetorical pattern, or is it too strong a claim?** Risk:
reviewers may find the counterfactual provocative; benefit: it
generates discussion and citations. This is a Discussion-section
choice we should make deliberately.

### CK3 — Per-discipline modeling — joint vs separate

Kozlowski fits LDA separately for Health and Social Sciences;
ws2 plans to fit clusters separately for CS and Physics per §11.
**Do we lose anything by not fitting jointly?** A joint fit might
reveal cross-discipline patterns that separate fits hide (e.g., the
"AI/ML methodology" cluster appearing in both fields). Kozlowski's
choice was made for interpretability; if ws2 has a research question
about cross-field methodology spillover, we may want a joint fit
robustness check. This is a Stage-3 robustness question, not Phase
0.2.

### CK4 — Mechanism mediation — direct test feasibility

Our claim #13's decoupling pattern could be partially mediated by
Kozlowski's compound-mechanism (topic specialization + within-topic
citation gap). **Can we directly test the mediation in ws2?**

Direct test requires:
1. Per-paper subfield-cluster assignment (we have this).
2. Per-author demographic profile (we have this).
3. A way to model "paper p's subfield cluster = c is mediated by
   author a's gender, country, prestige" — this is a hierarchical
   model.

Test IV is the closest: it regresses paper novelty on team diversity.
But it doesn't decompose into between-cluster and within-cluster
components. A Stage-3 extension could add this decomposition.

### CK5 — Race exclusion — is it a methodology gap or a methodology improvement?

ws2 excludes race inference per Lockhart P1. Kozlowski uses race
inference. **Is ws2 missing important variation Kozlowski captures?**

The defensible answer: yes, we miss within-country racial dynamics
(e.g., Black US authors), but we capture across-country variation
that Kozlowski misses. The two designs complement; neither dominates.
For Methods: explicitly position ws2 as the across-country complement
to Kozlowski's within-country (US) intersectional analysis.

---

## Synthesis Pointers (for `synthesis.md`)

When harvesting into ws2's Methods + Results + Discussion:

- **Methods §4** (demographic features): cite Kozlowski for
  fractional-counting precedent.
- **Methods §9a P5** (bias-uncertainty band): Lockhart P5 +
  Kozlowski 2022 as methodology lineage.
- **Methods §11** (cluster-fit reporting): add CV-by-region as
  third statistic; cite Kozlowski.
- **Methods §11** (per-discipline fitting): cite Kozlowski as
  precedent for per-discipline modeling.
- **Results 3-panel figure caption**: report cluster entropy,
  effN, AND CV per (year × demographic-cell) row.
- **Discussion mediator paragraph**: cite Kozlowski's compound-
  mechanism finding as candidate explanation.
- **Discussion counterfactual** (optional, depending on CK2 outcome):
  pattern import from Kozlowski's "29% more on X" exercise.
- **Limitations**: explicitly position ws2's gender-only +
  multi-national + non-US-restricted design as deliberate
  divergence from Kozlowski.
- **Related Work**: position ws2 as across-country complement to
  Kozlowski's within-country intersectional analysis.

---

## Discussion Notes

(To be filled during collaborative review session.)

### On CK1 — minimum N per cell for CV reporting

[Discussion]

### On CK2 — counterfactual narrative adoption

[Discussion]

### On CK3 — joint vs separate cluster fitting

[Discussion]

### On CK4 — direct mediation test feasibility

[Discussion]

### On CK5 — race exclusion framing

[Discussion]

---

## Surfaces flagged for retro adjustment

**One minor surface** (additive, not adjustment-requiring):

1. **CV-by-region as a §11 diagnostic** — small methodology
   addition. Already-committed §11 cluster-fit reporting computes
   per-cell occupancy; adding CV is a derived statistic on the same
   data. Cost: trivial. Benefit: Kozlowski-style "specialization vs
   ubiquity" decomposition alongside cluster entropy.

No other surfaces. Phase 0.2 commitments survive Kozlowski's
methodology unchanged.
