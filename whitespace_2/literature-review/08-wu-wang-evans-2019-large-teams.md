# 08 — Large Teams Have Developed Science and Technology; Small Teams Have Disrupted It

**Authors:** Lingfei Wu, Dashun Wang, James A. Evans
**Venue:** *Nature* 566, 378–382 (Feb 2019)
**PDF:** `literature-review/08-wu-wang-evans-2019-large-teams.pdf` (gitignored)
**SI:** same path, suffixed `_SI.pdf`
**DOI:** 10.1038/s41586-019-0941-9

---

## Background

Wu-Wang-Evans is the **canonical empirical paper on team-size and
disruption**: across 50M+ articles, patents, and software products
(1954–2014), large teams develop while small teams disrupt. The CD-
index (Funk-Owen-Smith 2017) is the disruption metric, and team
size from 1 to 50 spans the empirical x-axis.

This paper sits in the load-bearing position for ws2's Test II
(within-individual semantic scope vs team size) and Test IV (team
demographic-diversity × paper novelty). We're not testing W-W-E's
team-size-disruption claim directly; we're testing claim #13
(intellectual-vs-demographic plurality decoupling), but team-size
is a confound in our regression specifications. W-W-E + Petersen
2025 (Tier 1) form the team-size-methodology pair we engage with.

For ws2, the paper has four functional uses:
1. **Test II + Test IV pre-registration team-size specification.**
   W-W-E + Petersen 2025 establish three-way specification (team-
   size as control / predictor / stratified) is the right approach.
2. **Quadratic team-size finding for Test IV.** W-W-E document
   that cross-disciplinary breadth saturates at team size 8-10 and
   *reverses* at larger sizes — a quadratic effect, not monotone.
   Test IV's specification should include the quadratic team-size
   term to capture this.
3. **Search-depth + search-popularity as Test II measures.** W-W-E's
   "search depth" (average reference age) and "search popularity"
   (median citations to references) are operationalizations of
   intellectual scope that are directly portable to ws2.
4. **CD-index inheritance + Substrate divergence.** W-W-E uses
   CD-index (the metric ws2 explicitly excludes per
   Petersen-Holst-Macher critique) and uses WoS (which under-covers
   CS conference proceedings). Both are points where ws2's design
   intentionally departs.

This is **not a fatal-surface paper** — Phase 0.2 commitments
survive W-W-E's specifications. The paper *enriches* Test II + Test
IV pre-registration via specification refinements rather than
overturning anything.

---

## Key Ideas

### 1. The CD-index disruption metric

W-W-E adopts the CD-index from Funk & Owen-Smith 2017:

```
D_i = (N(A) - N(B)) / (N(A) + N(B) + N(C))
```

where:
- `A` = subsequent works that cite focal paper *i* but NOT its references
- `B` = subsequent works that cite focal paper *i* AND its references
- `C` = subsequent works that cite focal paper's references but NOT *i*

Range: D ∈ [-1, +1]
- **D = +1 (purely disruptive):** all citing works cite *i* alone,
  ignoring *i*'s references; *i* eclipses prior art.
- **D = 0 (neutral):** balanced.
- **D = -1 (purely developing):** all citing works cite *i* alongside
  its references; *i* amplifies prior art.

W-W-E example papers (Fig. 1):
- Bak et al. 1987 (BTW model of self-organized criticality):
  D = +0.86, disruptive — replaced its prior art.
- Davis et al. 1995 (Bose-Einstein condensation experimental):
  D = -0.58, developmental — co-cited with antecedents.
- Randall & Sundrum 1999 (large mass hierarchy):
  D = -0.004, neutral.

**ws2's commitment regarding CD-index:** Per ws2 desideratum
exclusions and the Petersen-Holst-Macher trio, ws2 does NOT use
CD-index as primary disruption metric. The Holst 2024 paper (Tier 1)
documented that ~5% of WoS records have CD_5 = 1 by mechanical
construction (zero-reference dataset artifacts), and that the time
trend in this artifact rate explains substantial fraction of the
disruption-decline pattern. Petersen 2024 (Tier 1) documented that
citation-inflation bias additively decreases CD over time, again
explaining substantial fraction. Petersen 2025 (Tier 1) re-analyzed
the team-size-disruption relationship with proper team-size adjustment
and found the effect substantially attenuated.

For ws2 Methods: cite W-W-E as the canonical disruption-decline
empirical paper, cite Petersen-Holst-Macher trio as the methodology-
level critique trio, and justify ws2's non-use of CD-index as
primary metric on this basis.

### 2. The team-size-disruption headline finding

The paper's central claim:

> "as teams enlarge from one to fifty team members, their papers,
> patents and products drop in disruption by 70%, 30% and 50%,
> respectively. In every case, this highlights a dramatic transition
> from disruption to development as disruption curves drop below the
> dashed line marking the zero point."

Specifically (Fig. 2D for articles, Fig. 2E patents, Fig. 2F software):
- **Top-5% disruption:** solo authors are **72% more likely** than
  5-person teams.
- **Top-5% citations:** 10-person teams are **50% more likely** than
  solo.

The pattern holds across:
- All disciplines (Fig. 3B + Figs S9-S17)
- All eras 1954-2014 (Fig. S4)
- 90% of detailed scientific fields

Exceptions: "Engineering and Computer and Information Technology"
where conference proceedings are the publishing norm (W-W-E's WoS
data only indexes journal articles).

**ws2 implication:** Our analytical population (CS+Physics 1970-2024,
OpenAlex) covers conference proceedings as well as journal articles
— a substantively different substrate from W-W-E's WoS-only journal
sample. **Our team-size results MAY DIVERGE from W-W-E's specifically
in CS** because conference papers tend to have smaller teams AND
different citation dynamics from journal articles. Methods should
note this substrate divergence; Discussion can interpret any divergence
as substrate-driven, not phenomenon-driven.

### 3. The within-author finding (~2/3 of team-size effect)

W-W-E's most methodologically careful claim:

> "We controlled for author differences by comparing the same
> author's articles against themselves, varying only team size
> (Fig. 3C), and we modeled this relationship accounting for a
> hundred variables that detail the coordinates of each article's
> title and abstract in the high-dimensional space of published
> science (see SOM; 21). These comparisons and models reveal that
> approximately one third of the team size effect we find can only
> be observed across different scientists presumably doing different
> kinds of science. Moreover, different kinds of science strongly
> influence the degree to which articles disrupt or develop science,
> increasing our model fit by an order of magnitude. Nevertheless,
> we continue to observe nearly two thirds of the effect shown in
> Fig. 2 when we compare scientists with themselves, varying team
> size and content."

Two interpretive claims:
- Roughly **1/3** of the team-size-disruption effect is between-
  scientist (different scientists tackle different kinds of work).
- Roughly **2/3** is within-scientist (the same scientist on
  larger teams produces more developmental work).

This is the empirical anchor for ws2's Test II ("within-individual
semantic-scope and team-size"). The within-author specification is
the more demanding because it eliminates between-scientist
heterogeneity.

**Important methodological caveat:** W-W-E's "100 variables coordinates
of title and abstract in high-dimensional space" is an early-stage
embedding-style topic control. ws2 has access to better embeddings
(SPECTER2 768-d) and better cluster assignments (§11 stratified
fit). Test II should reproduce W-W-E's within-author specification
*and* extend it with our more sophisticated topic controls.

**Petersen 2025 critique:** Petersen, Arroyave & Pammolli 2025 (J. of
Informetrics, our Tier 1 paper) argue that the within-author finding
is sensitive to the team-size adjustment specification. With proper
team-size adjustment in regression, the effect attenuates. ws2 Test
II should pre-register both W-W-E's specification and Petersen 2025's
specification and report the difference.

### 4. Search-behavior mechanism (search depth + search popularity)

W-W-E's mechanism explanation: large vs small teams have different
*search behaviors*. Small teams reach further into the past:

- **Search depth** = average relative age of references cited
- **Search popularity** = median citations to focal work's references

> "we find that solos and small teams are much more likely to build
> on older, less popular ideas (Fig. 2G-L). Larger teams, with more
> people spanning more dispersed areas, cannot be less aware of
> older, less popular work than small teams, but they have been
> systematically less likely to build on it. Indeed, larger teams
> have been much more likely to target recent, high-impact work as
> the primary source of their ideas, and this tendency increases
> monotonically with team size."

Mechanism implication: large teams' tendency to develop comes from a
*choice* to engage with high-visibility recent work, not from
ignorance of older / less-popular work.

**ws2 implication:** "Search depth" and "search popularity" are
*operationalizations of intellectual scope* — exactly the construct
ws2's Test II is trying to measure. We should pre-register search-
depth + search-popularity as DEPENDENT variables in Test II, alongside
our embedding-distance-based novelty metrics:

- Test II model: `intellectual_scope_paper_p ~ team_size_p +
  team_size_p^2 + author_fixed_effects + year + subfield`
- Where `intellectual_scope_paper_p` is jointly assessed via:
  1. Mean pairwise cosine distance of paper p's embedding to its
     references' embeddings (semantic search depth).
  2. Average reference age (W-W-E's "search depth").
  3. Median citations to references (W-W-E's "search popularity").

This is a Phase 0.2 specification refinement, not a new commitment.

### 5. The cross-disciplinary breadth saturation+reversal

W-W-E's finding on team breadth:

> "An often claimed advantage of large teams is their ability to link
> divergent fields. We find that this effect grows as a convex
> function of team size. The effect of broader teams on fusing
> surprising combinations from diverse journals saturates between
> eight and ten team members and then reverses with greater team
> size, dropping below solo authors and smaller teams (Fig. S4).
> These results suggest that combinations of distant ideas are
> benefited by broad teams, but they are more likely to enter
> published research when they occur within a few team members'
> individual experiences than across the experiences of many team
> members."

This is a **load-bearing finding for Test IV**. The functional shape:

- Solo / small teams (1-4 members): low cross-discipline breadth in
  references but high disruption.
- Medium teams (5-8 members): increasing cross-discipline breadth
  AND high citations.
- Large teams (8-10): peak cross-discipline breadth but declining
  disruption.
- Very large teams (>10): cross-discipline breadth REVERSES below
  solo authors; disruption continues to decline.

The mechanism: in large teams, divergent ideas have to be transmitted
across more team-member boundaries, and the transmission cost
decreases the likelihood that genuinely cross-disciplinary
combinations end up in the paper.

**ws2 Test IV pre-registration implication:** Our Test IV regresses
team-diversity (gender × country × prestige Rao Q) on paper novelty
(embedding-based distance to citation-context centroid). Team SIZE
is a covariate we need to specify carefully. W-W-E shows team-size
acts non-monotonically on cross-discipline breadth (which is closely
related to our novelty construct). **Test IV pre-registration should
commit to:**

- `novelty_p ~ team_diversity_p + team_size_p + team_size_p^2 +
  team_diversity_p × team_size_p + author/year/subfield FE + ε`
- Pre-register the QUADRATIC team-size term to capture W-W-E's
  saturation+reversal.
- Pre-register the INTERACTION team-diversity × team-size to capture
  the possibility that team-diversity effects on novelty are
  team-size-dependent.

This is a specific Phase 0.2 specification refinement — minor surface
worth flagging.

### 6. Sleeping Beauty Index — delayed-recognition pattern

W-W-E (Fig. 3D):

> "smaller teams experience a much longer citation delay, with an
> average Sleeping Beauty Index for solo and two-person research
> teams four times that of ten-person teams."

Sleeping Beauty Index measures convexity of citation distribution
over time:
- High SB index: paper ignored for years, then suddenly heavily cited
- Low SB index: paper cited linearly from publication
- Negative SB index: paper cited heavily early, then declines

Solo / small teams have 4x higher SB index than 10-person teams —
their work is more often delayed-recognition.

**ws2 implication:** This is a refinement, not a primary commitment.
For Stage 3 robustness analyses, ws2 could include SB-index analysis
as a citation-dynamics complement to our canonical-concentration
metrics (Spearman top-50, citation Gini). Phase 0.2 doesn't need
this; flag for Stage 3.

### 7. Funded-small-teams behave like large teams (Fig. S30) [ACKNOWLEDGE]

A striking finding in the closing paragraph:

> "Analyzing articles published from 2008 to 2012 that acknowledged
> financial support from several top government agencies around the
> world, we find that the small teams receiving funds are
> indistinguishable from large teams in their tendency to develop
> rather than disrupt their fields. This could result from a
> conservative review process, proposals designed to anticipate such
> a process, or a planning effect whereby small teams lock themselves
> into big team inertia by remaining accountable to a funded
> proposal."

If this finding generalizes, **funded research is systematically
biased toward developmental work**. ws2 implication:

- Our analytical population (post §0 filter) is biased toward
  abstract-having OpenAlex papers.
- Abstract-having papers are correlated with journal publication.
- Journal publication is correlated with funding-acknowledgment
  patterns.
- → Our analytical population may inherit a development-bias from
  funding-correlated indexing.
- Per Culbert 2025, OpenAlex doesn't reliably capture funding info
  (4,100 journals only have it in WoS/Scopus), so we can't directly
  control for funding status.

**Phase 0.2 Limitations should acknowledge** this potential bias
without claiming we can correct for it. The §9e propensity weighting
addresses abstract-availability selection bias (our primary concern),
but funding-status selection is a secondary concern we acknowledge
but don't model.

### 8. Substrate caveat for CS

W-W-E note (page 4):

> "The only consistent exceptions were observed for disciplines
> (e.g., Engineering and Computer and Information Technology) where
> conference proceedings rather than journal articles are the
> publishing norm (our WOS data only indexes journal articles)."

For ws2 (CS+Physics 1970-2024 OpenAlex), this is directly relevant:
- OpenAlex includes conference proceedings substantially better than
  WoS (per Culbert 2025).
- ws2's CS results may diverge from W-W-E's pattern specifically
  because of substrate.
- Methods should note this divergence; Discussion can attribute any
  CS-specific divergence to substrate, not phenomenon.

This is a Methods clarification, not a commitment change.

---

## Three-Level Results

### Smart-high-schooler reading (~5 min)

This paper analyzed 50 million scientific papers, patents, and
software projects spanning 1954-2014 to ask: do small research
teams produce different kinds of work than big teams?

The answer is: yes, dramatically. They found:

1. **Small teams do more disruptive work.** A "disruptive" paper is
   one that introduces a new idea important enough that future
   research stops citing the older work it built on, and instead
   only cites the new paper. Solo researchers are 72% more likely
   to produce highly disruptive papers than 5-person teams.

2. **Big teams do more developmental work.** "Developmental" papers
   refine and extend existing ideas. They get more citations
   immediately because there are more researchers ready to build on
   them. 10-person teams are 50% more likely to produce highly cited
   papers than solo researchers.

3. **The effect is mostly within-person.** Even when comparing the
   same scientist's papers to themselves, controlling for the topic,
   they produce more developmental work when on bigger teams. So
   it's not just that different kinds of researchers join different
   sized teams — being on a big team itself makes you more
   developmental.

4. **Small teams reach further back.** They build on older,
   less-popular ideas. Big teams build on recent, high-impact work
   only. Both have access to the same literature, but they make
   different choices about what to engage with.

For our project: this paper is about *how* team composition affects
the kind of science that gets done. We're testing a related but
different question: does the demographic composition of the
scientific workforce affect what kind of intellectual diversity
emerges? Wu-Wang-Evans's findings tell us team SIZE is a confound
we have to control for carefully — and they suggest team size has
a non-linear effect on intellectual breadth (saturates at ~10 then
reverses).

### Junior/senior-undergraduate reading (~15 min)

Wu-Wang-Evans is a methodologically meticulous team-size analysis
of three datasets:
- WoS articles 1954-2014 (43M articles, 615M citations among them)
- USPTO patents 2002-2014 with patent-citations
- GitHub software projects with code-forking patterns

The disruption metric is the Funk-Owen-Smith CD-index, a citation-
graph-based measure that distinguishes "this paper eclipsed its
prior art" (D=+1) from "this paper was co-cited with its prior art"
(D=-1).

The headline empirical claim: as teams enlarge from 1 to 50 members,
disruption drops 70% (articles), 30% (patents), 50% (software).
This is a monotone decrease in disruption across team size.

The methodological move that matters: W-W-E control for author
differences by comparing the same author's articles to each other,
varying only team size, and *also* control for topic via embedding-
style coordinates of title+abstract. They find ~2/3 of the team-size
effect persists *within-author*, meaning team size has a substantive
effect on the kind of work the same scientist produces, not just an
artifact of different scientists self-selecting into different team
sizes.

The mechanism analysis is search-behavior-based:
- "Search depth" = average reference age (small teams cite older
  references)
- "Search popularity" = median citations to references (small teams
  cite less-popular references)
- Solo / small teams reach further back into less-cited literature
- Large teams systematically engage with recent / high-impact work

The cross-disciplinary breadth analysis (Fig. S4) is the most
intricate and most relevant to ws2:
- Linking divergent fields requires team breadth (intuition).
- W-W-E find this effect grows as a *convex* function of team size.
- Saturates at ~8-10 members.
- *Reverses* beyond that — very large teams produce LESS
  cross-disciplinary work than smaller teams.
- Mechanism: in large teams, divergent ideas have to be transmitted
  across more team-member boundaries; transmission costs decrease
  the rate at which genuinely cross-disciplinary combinations land
  in published research.

The substrate caveat is important: WoS only indexes journal articles.
For Engineering and CS where conference proceedings dominate, the
effect doesn't replicate cleanly — W-W-E acknowledge this.

The funded-research-effect finding is striking but tangential: small
teams that received government funding behave like large teams in
their tendency to develop rather than disrupt. The hypothesis is
that conservative review processes and funded-proposal accountability
push small teams toward big-team behavior.

For ws2, the load-bearing inheritance is twofold:
1. **Test II + Test IV team-size specification** — Phase 0.2
   pre-registration commits to multi-spec team-size
   (control / predictor / stratified) per W-W-E + Petersen 2025.
2. **Quadratic team-size in Test IV** — W-W-E's saturation+reversal
   finding implies our team-diversity × team-size regression should
   include a quadratic team-size term.

### Early-grad reading (~30 min)

W-W-E's contribution is methodological *and* substantive. Three
methodological moves:

1. **Same-author within-team-size comparisons.** This is the cleanest
   identification strategy in the paper. By comparing the same
   author's articles to each other, varying only team size, W-W-E
   eliminate between-scientist heterogeneity (different fields,
   different career stages, different topics) as confounders. They
   then layer topic controls (100 variables of title+abstract
   embedding-style coordinates) on top. The finding that ~2/3 of the
   team-size effect persists with these controls is a strong
   identification claim.

2. **Functional-form analysis of cross-disciplinary breadth.** Most
   team-size papers report linear effects. W-W-E specifically
   document the non-monotone shape: convex-saturating-reversing.
   This is methodologically important because team-diversity
   regressions implicitly assume monotone team-size relations; if
   the relation is quadratic and reverses, linear specifications
   give biased estimates.

3. **Search-behavior-as-mechanism analysis.** Rather than treating
   team-size as a black-box variable, W-W-E decompose the effect
   into search-depth + search-popularity components. This is
   directly portable to ws2's Test II — search-depth and
   search-popularity are operationalizations of "intellectual scope"
   that complement embedding-distance-based novelty measures.

Substantively, the paper's normative claim:

> "Both small and large teams are essential to a flourishing ecology
> of science and technology. The increasing dominance of large
> teams, a flurry of scholarship on their perceived benefits,
> combined with our findings call for new investigation into the
> vital role played by individuals and small groups in advancing
> science and technology."

This is the policy frame. W-W-E argue that the increasing dominance
of large teams in scientific output may be *eroding* the ecology
that depends on both small-team disruption and large-team
development. The funded-research finding (small teams that get
funding behave like large teams) is the kicker — direct funding
support for small teams may not be enough, because funding processes
themselves push toward conservative-developmental work.

For ws2, the substantive frame matters less than the methodological
inheritance. We're not testing the team-size-disruption claim
directly; we're testing claim #13 (decoupling of intellectual from
demographic plurality). But team-size is a significant confound in
our regression specifications, and W-W-E + Petersen 2025 is the
methodological pair we engage with on team-size adjustment.

Petersen 2025 (our Tier 1 paper #04) re-analyzed W-W-E's team-size-
disruption relationship with proper team-size adjustment in the
regression and found the effect substantially attenuated. ws2 Test
II + Test IV should pre-register both W-W-E's specification and
Petersen 2025's specification and report the difference. Where they
agree, the substantive claim is robust; where they diverge, that's
the methodology-level tension we acknowledge.

---

## Connection to Our Project

### What ws2 takes from W-W-E

**1. Test II + Test IV multi-spec team-size pre-registration.**
Phase 0.2 commits to:

> "Team-size enters our regressions in three pre-registered
> specifications: (1) team-size as control variable (W-W-E 2019
> within-author specification), (2) team-size as primary predictor
> with author + year + subfield fixed effects (Petersen et al. 2025
> specification), (3) team-size-stratified analysis (no aggregation
> across team sizes; report effects within each team-size band).
> All three specifications are reported. Where they diverge, the
> divergence is itself the finding and is interpreted with reference
> to the W-W-E vs Petersen 2025 methodological tension."

**2. Quadratic team-size in Test IV.** W-W-E's saturation+reversal
finding requires:

> "Test IV regression: novelty_p ~ team_diversity_p + team_size_p +
> team_size_p^2 + team_diversity_p × team_size_p + author/year/
> subfield FE + ε. The quadratic team-size term captures the
> saturation+reversal pattern documented by Wu-Wang-Evans 2019. The
> interaction term tests whether team-diversity effects on novelty
> are team-size-dependent. Pre-registered hypothesis: team-diversity
> effect is positive at team-size 4-10, attenuates beyond 10."

This is a Phase 0.2 specification refinement — minor surface,
already part of the existing commitment, just made explicit.

**3. Search-depth + search-popularity as Test II measures.** Phase
0.2 commits Test II to multiple operationalizations of "intellectual
scope":

> "Test II's dependent variable 'intellectual scope' is operationalized
> via three measures, each computed per paper:
> (a) Mean pairwise cosine distance of paper's embedding to its
> references' embeddings (semantic distance).
> (b) Average relative age of references cited (W-W-E search depth).
> (c) Median citation count of references (W-W-E search popularity,
> reverse-coded so high values indicate scope).
> All three are reported as separate dependent variables. The
> primary inference is on (a) (semantic distance), but (b) and (c)
> serve as W-W-E-comparable cross-checks."

This is also a Phase 0.2 specification refinement.

**4. Substrate divergence acknowledgment.** Methods note:

> "We use OpenAlex CS+Physics 1970-2024. Wu-Wang-Evans 2019 used
> WoS journal articles only, which under-covers Engineering and
> Computer and Information Technology disciplines where conference
> proceedings are the publishing norm. OpenAlex covers conference
> proceedings, so our CS-specific results may diverge from
> Wu-Wang-Evans's pattern by substrate, not by phenomenon. Where
> our team-size results in CS differ from Wu-Wang-Evans, we
> interpret the difference as substrate-driven; where they agree
> for Physics (where journal-article publishing is the norm and
> WoS coverage is more comprehensive), the substrate effect is
> minimal."

This is a Methods clarification.

**5. Funded-research-bias acknowledgment.** Limitations:

> "Wu-Wang-Evans 2019 (Fig. S30) found that small teams receiving
> government funding behave indistinguishably from large teams in
> their tendency to develop rather than disrupt. This implies our
> analytical population may inherit a development-bias from
> funding-correlated indexing patterns (funded research is more
> likely to be journal-published with abstracts, which drives
> selection into our §0 analytical population). We acknowledge this
> bias but do not model it directly because OpenAlex's funding-info
> coverage is incomplete (Culbert et al. 2025); the §9e propensity
> correction addresses abstract-availability selection but not
> funding-status selection."

### What ws2 explicitly does NOT take from W-W-E

1. **CD-index as primary disruption metric.** Per ws2's
   Petersen-Holst-Macher trio rationale (Tier 1 papers 03, 04, 05).
   ws2's primary metric is semantic-embedding distance from citation
   context centroid; CD-index is excluded.

2. **WoS substrate.** Per substrate divergence acknowledgment above.

3. **The 1-to-50 team-size range as headline finding.** W-W-E's
   range is exploratory; team sizes >20 are increasingly rare and
   represent specific research norms (mega-projects, high-energy
   physics consortia). For ws2's CS+Physics population, team sizes
   are typically 1-10; we'll report results in this range as primary
   and acknowledge larger teams as Stage-3 robustness.

### Specific design implications for ws2

| Phase 0.2 commitment | W-W-E-driven content |
|---|---|
| Test II three-spec team-size pre-registration | W-W-E + Petersen 2025 |
| Test II multi-measure intellectual-scope (semantic + search-depth + search-popularity) | W-W-E search-behavior mechanism |
| Test IV quadratic team-size + interaction | W-W-E saturation+reversal finding |
| Methods CS-substrate divergence note | W-W-E WoS-only caveat |
| Limitations funded-bias acknowledgment | W-W-E Fig. S30 finding |
| Methods CD-index non-use justification | Add W-W-E citation to Petersen-Holst-Macher trio |
| Discussion ecology argument | Adopt W-W-E's "both kinds of teams essential" framing |

### How ws2 cites W-W-E in framing

In Methods §3 (subfield-classifier drift section, where we engage
with team-size-disruption literature):

> "Wu, Wang & Evans (2019) document a monotonic decrease in the
> Funk-Owen-Smith CD-index as team size increases from 1 to 50 in
> Web-of-Science articles, USPTO patents, and GitHub software
> projects 1954-2014. Their within-author specification (~2/3 of
> the effect) and search-behavior mechanism analysis (small teams
> cite older, less popular references) inform Test II's pre-
> registration. Petersen, Arroyave & Pammolli (2025) re-analyze
> the team-size-CD relationship with proper team-size adjustment in
> the regression and find the effect attenuates substantially. We
> pre-register both the Wu-Wang-Evans within-author specification
> and the Petersen et al. 2025 specification; where they diverge,
> the divergence is the finding."

In Discussion (closing paragraph):

> "Following Wu-Wang-Evans (2019), we recognize that 'both small and
> large teams are essential to a flourishing ecology of science and
> technology.' Our finding [...] complements their team-size analysis
> by adding the demographic-composition lens: workforce
> diversification may be necessary but not sufficient for
> intellectual diversification, particularly when team-size
> distributions concentrate in the saturating regime that Wu-Wang-
> Evans identified."

---

## Key Quotes

| # | Quote | Page | Use |
|---|---|---|---|
| Q1 | "as teams enlarge from one to fifty team members, their papers, patents and products drop in disruption by 70%, 30% and 50%, respectively." | p. 3 | Headline finding citation |
| Q2 | "approximately one third of the team size effect we find can only be observed across different scientists … Nevertheless, we continue to observe nearly two thirds of the effect shown in Fig. 2 when we compare scientists with themselves, varying team size and content." | p. 4 | Within-author specification basis |
| Q3 | "solos and small teams are much more likely to build on older, less popular ideas (Fig. 2G-L). Larger teams … have been much more likely to target recent, high-impact work as the primary source of their ideas, and this tendency increases monotonically with team size." | p. 4 | Search-behavior mechanism, Test II measures |
| Q4 | "The effect of broader teams on fusing surprising combinations from diverse journals saturates between eight and ten team members and then reverses with greater team size, dropping below solo authors and smaller teams" | p. 5 | LOAD-BEARING — Test IV quadratic specification |
| Q5 | "the small teams receiving funds are indistinguishable from large teams in their tendency to develop rather than disrupt their fields." | p. 6 | Funded-bias acknowledgment |
| Q6 | "The only consistent exceptions were observed for disciplines (e.g., Engineering and Computer and Information Technology) where conference proceedings rather than journal articles are the publishing norm (our WOS data only indexes journal articles)." | p. 4 | Substrate divergence note |
| Q7 | "Both small and large teams are essential to a flourishing ecology of science and technology." | p. 5 | Discussion ecology framing |
| Q8 | "smaller teams experience a much longer citation delay, with an average Sleeping Beauty Index for solo and two-person research teams four times that of ten-person teams" | p. 5 | Stage 3 SB-index robustness option |
| Q9 | "as teams grow, the likelihood that they eclipse the work on which they build vanishes" | p. 3 | Disruption-decline framing |

---

## Study Questions

### Basic (factual recall)

- **B1.** What is the mathematical formula for the CD-index used by
  W-W-E?
- **B2.** Across what year range does W-W-E's article dataset span?
- **B3.** What percentage drop in disruption do W-W-E document
  going from 1- to 50-person teams in articles?
- **B4.** In the within-author specification, what fraction of the
  team-size effect persists?
- **B5.** At what team size does W-W-E's cross-disciplinary breadth
  effect saturate?
- **B6.** What discipline does W-W-E specifically note as an
  exception (where the team-size pattern doesn't hold cleanly)?

### Intermediate (synthesis)

- **I1.** Why does W-W-E's within-author specification not
  *eliminate* topic confounds, and how do they address this
  remaining concern?
- **I2.** Explain in your own words what "search depth" and "search
  popularity" mean and why they're useful as intellectual-scope
  measures.
- **I3.** Why does the cross-disciplinary breadth effect *reverse*
  for very large teams (>10 members)? What's W-W-E's mechanism
  story?
- **I4.** What does W-W-E's funded-research finding (small teams
  with grants behave like large teams) imply about the
  representativeness of grant-supported research samples for
  bibliometric analysis?
- **I5.** ws2 uses OpenAlex which covers conference proceedings;
  W-W-E uses WoS which doesn't. What is the expected direction of
  divergence for ws2's CS-specific results?

### Advanced (engagement)

- **A1.** ws2's Test IV pre-registration adds a quadratic team-size
  term following W-W-E's saturation+reversal finding. Could the
  quadratic specification be confounded with team-diversity? Sketch
  the regression specification that disentangles the two.
- **A2.** W-W-E's within-author specification eliminates
  between-scientist heterogeneity. Can a within-author analysis on
  ws2's CS+Physics OpenAlex data even produce reliable estimates
  given the disambiguation-error rate Culbert 2025 documents?
- **A3.** W-W-E's funded-research finding suggests that selection
  into a "funded sample" introduces a development-bias. ws2's
  analytical population is "abstract-having OpenAlex CS+Physics
  papers," not "funded papers." Are these populations correlated
  enough that the funded-bias propagates to ws2?
- **A4.** Petersen 2025 critiques W-W-E's team-size-disruption
  effect as sensitive to team-size adjustment specification. ws2
  pre-registers both specifications. What additional specifications
  could ws2 add to make the comparison even more transparent? E.g.,
  a piece-wise linear team-size with breakpoints at 5 and 10.
- **A5.** W-W-E's "ecology of science" framing argues both small
  and large teams are essential. ws2's claim #13 about
  intellectual-vs-demographic plurality decoupling has its own
  ecology framing potential. Sketch a Discussion paragraph that
  weaves the two ecology frames together without overclaiming.

---

## Challenge Corner

These are questions where ws2 has to push back on or extend
W-W-E's framing. To be addressed during collaborative review.

### CW1 — Is the within-author specification reliable on OpenAlex?

W-W-E's within-author analysis depends on author disambiguation
working reliably. Culbert 2025 documents OpenAlex's "generous
disambiguation" producing 10,000+-record-per-ORCID over-merges,
especially on Chinese names. **Can ws2 reliably reproduce W-W-E's
within-author specification on our OpenAlex CS+Physics data?**

Possible answers:
- (a) Yes, but only on the ORCID-confirmed-linkage subset (small
  N).
- (b) Yes, but with explicit disambiguation-uncertainty propagated
  via bootstrap over alternative author assignments.
- (c) No, the within-author specification is fundamentally
  unreliable on OpenAlex; we use the between-author specification
  with author fixed effects only, and report the within-author
  spec as Stage 3 robustness on the high-quality subset.

This is a Phase 0.2 implementation choice we should discuss.

### CW2 — The quadratic team-size in Test IV — what's the breakpoint?

W-W-E find saturation at team-size 8-10. CS+Physics 2010-2024 has
high-energy physics teams with 1000+ authors. **Should we top-code
team size somewhere?**

Options:
- Top-code at 50 (W-W-E's range).
- Top-code at 10 (the saturation point).
- Use log(team-size) instead of team-size + team-size^2.

This is a Phase 0.2 specification detail.

### CW3 — Search-depth on OpenAlex when references are incomplete

Per Culbert 2025, OpenAlex undercounts references on the long-tail
content. W-W-E's "search depth" depends on the full reference list.
**Is W-W-E's search-depth measure reliable on OpenAlex for our
1970-2024 CS+Physics population?**

Recommendation: limit the search-depth analysis to the post-1996
window where OpenAlex's reference coverage is comparable to WoS/
Scopus per Culbert. Pre-1996 search-depth is unreliable due to
reference-coverage gaps.

### CW4 — Funded-research bias — direct test feasibility

W-W-E's funded-research finding (Fig. S30) is intriguing but not
testable on ws2's data because OpenAlex's funding-info coverage is
incomplete. **Is there an indirect proxy for funding status we can
use as a robustness check?**

Possibilities:
- Institution prestige tier (top-50 universities are more grant-
  funded).
- ORCID coverage (proxy for institutional affiliation).
- Publication venue (high-impact journals correlate with funding).

These are weak proxies; this is a Stage 3 robustness option.

### CW5 — How prominently does W-W-E feature in ws2's narrative?

W-W-E is prominent enough in scientometrics that ws2's reviewers
will expect engagement. **At what level of detail does ws2 cite
W-W-E?**

Options:
- (a) Brief: 1 paragraph in Methods justifying team-size
  pre-registration.
- (b) Substantive: 1 paragraph in Methods + 1 in Discussion engaging
  with W-W-E's ecology framing.
- (c) Deep: Methods + Discussion + a comparison of our team-size
  results to W-W-E's pattern as a side-quest analysis.

Default is (b); (c) is overclaiming for a paper testing claim #13
(a different question).

---

## Synthesis Pointers (for `synthesis.md`)

When harvesting into ws2's Methods + Results + Discussion:

- **Methods §3 (subfield drift) or §4 (demographic features)**:
  cite W-W-E in the team-size-pre-registration paragraph.
- **Methods Test II pre-registration**: include search-depth +
  search-popularity as cross-check measures alongside semantic
  distance.
- **Methods Test IV pre-registration**: quadratic team-size term;
  team-diversity × team-size interaction.
- **Methods substrate-caveat note**: OpenAlex vs WoS substrate
  divergence for CS specifically.
- **Methods CD-index non-use justification**: cite W-W-E as the
  canonical empirical CD-index paper, then cite Petersen 2024,
  Petersen 2025, Holst 2024 as the trio that justifies non-use.
- **Limitations**: funded-research-bias acknowledgment;
  disambiguation-uncertainty propagation if within-author
  specification is included.
- **Discussion**: ecology framing per W-W-E's closing paragraph.

---

## Discussion Notes

(To be filled during collaborative review session.)

### On CW1 — within-author specification feasibility

[Discussion]

### On CW2 — team-size top-coding

[Discussion]

### On CW3 — search-depth reliability pre-1996

[Discussion]

### On CW4 — funded-research bias proxies

[Discussion]

### On CW5 — depth of engagement

[Discussion]

---

## Surfaces flagged for retro adjustment

**Three minor surfaces** (specification refinements, not commitment
changes):

1. **Test IV quadratic team-size** — W-W-E's saturation+reversal at
   team-size 8-10 implies our team-diversity × team-size regression
   needs the quadratic term explicitly pre-registered.

2. **Test II search-depth + search-popularity measures** — W-W-E's
   "search depth" and "search popularity" are operationalizations
   of intellectual scope. Pre-register them as cross-check measures
   alongside our semantic-distance primary.

3. **Substrate divergence acknowledgment** — Methods note that ws2's
   CS results may diverge from W-W-E's pattern by substrate (OpenAlex
   conference-proceedings coverage > WoS journal-only).

None retire commitments; all are Phase 0.2 pre-registration
specification refinements. Phase 0.1 retro should integrate them
into the Test II + Test IV pre-registration drafts.
