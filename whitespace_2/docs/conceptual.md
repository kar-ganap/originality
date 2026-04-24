# Whitespace 2: Decomposing Demographic vs. Semantic Plurality in Scientific Literature

**A compass document for when the work gets muddy.**

---

## What this paper is, in one sentence

An empirical time-series study that separates demographic diversity of authorship from semantic diversity of content on the same body of scientific work, to test whether intellectual plurality has declined even as demographic plurality has risen.

## Why this paper exists

The motivating claim (Claim #13 from the broader research program): despite massive expansions in demographic diversity of who produces intellectual work, the intellectual diversity of what gets produced has narrowed — because homogenizing "actuators" (shared platforms, canonical texts, institutional filters, formative pipelines) flatten outputs even when inputs are diverse.

This claim is widely believed but empirically thin. The two halves — demographic plurality rising, intellectual plurality falling — have been measured by different research communities using different methods on different datasets. Nobody has computed them on the same population over the same time horizon with consistent methodology. This paper fills that gap.

If the claim is correct, the two time series should diverge. If they don't, the claim is partially or fully disconfirmed. Either outcome is publishable. The divergence (if found) will matter for policy, institutional design, and the broader conversation about intellectual diversity. The non-divergence (if found) will deflate a widespread but unexamined assumption.

## What the paper shows

### Core claim of the paper

For one or more scientific fields over ~50 years, you report three time series:

1. **Demographic diversity of authorship** — Shannon entropy and related indices over author gender, nationality/country of affiliation, institutional prestige tier, and career stage.
2. **Semantic diversity of content** — effective dimensionality, entropy, and pairwise-distance measures over embedded paper content (abstracts or full text).
3. **Canonical concentration** — Chu-Evans-style Spearman correlation of top-N most-cited works across years; citation Gini; top-k share.

You then test: do (1) and (2) diverge over time, controlling for field growth and publication volume? And: does (2) decline while (3) rises, consistent with the actuator-homogenization mechanism?

### Secondary analyses (the paper's most valuable panels)

- **Cross-field comparison** — does the divergence pattern hold across fields, or is it field-specific?
- **Break-point analysis** — if divergence exists, when does it start? Does it coincide with identifiable events (internet, specific canonical papers, globalization of training pipelines)?
- **Subfield decomposition within-field** — subfields with clear canonical concentration (dominant textbook or foundational paper) vs. those without. The prediction: more canon-concentrated subfields show more demographic-semantic divergence. **This is the within-field test of the actuator-sharing mechanism and is probably the single most important analysis in the paper.**
- **Demographic decomposition** — which demographic expansions contribute most to rising demographic diversity, and does the divergence look different for different dimensions?

## Field selection — the key upfront decision

Field selection determines data availability, interpretability, and which research communities will review the paper.

**Primary field: Computer Science.**
- OpenAlex coverage is excellent.
- arXiv provides full-text for recent decades.
- Author disambiguation is tolerable.
- Massive demographic change — both in volume and geographic composition.
- Readers have strong intuitions, which helps calibration.
- Caveat: substantial topical expansion over time means you must handle semantic drift carefully.

**Robustness field: Physics.**
- Long history of good record-keeping (APS, arXiv-physics).
- Relatively stable topical structure.
- Pre-existing sociology-of-physics literature for cross-validation of demographic measurements.
- Caveat: you're on Wu-Wang-Evans / Evans-lab home turf; position the work as building on them rather than replacing them.

**Optional third field for contrast:** sociology or philosophy (via PhilPapers) if you want a non-STEM comparison. Skip if it would compromise depth.

**Do NOT choose:** economics (methodology-as-identity means abstract-based semantic measurement will miss the real concentration); anthropology/humanities as primary (data quality too uneven).

## Data sources — what to pull and how

**Primary: OpenAlex.**
- Free, CC0, excellent API.
- Query: all papers where concept IDs match field of interest, year between 1970 and 2024.
- For CS, this returns ~5-10M papers. Stratified sample by year; target 100-500K papers per field after sampling.
- Metadata includes title, abstract, authors with affiliations, year, citations, concept tags.

**Secondary: arXiv.**
- Bulk metadata and PDFs via S3, free for research.
- For full-text analysis if abstracts prove insufficient.
- Start with abstracts; only invoke full-text if robustness demands it.

**Tertiary: Semantic Scholar Academic Graph (S2AG).**
- Has precomputed SPECTER2 embeddings for ~200M papers.
- Check coverage of your field first — if good, this saves substantial embedding compute.

**Demographic inference sources:**
- Gender: `gender-guesser` library (free, weak) or Genderize.io (paid, better). Budget ~$30-100 for the full sample.
- Nationality: institutional affiliation → country mapping from OpenAlex institution records.
- Career stage: years since first publication, via OpenAlex author history.
- Institutional prestige: CWUR or Shanghai ranking for universities; heuristic categories for industry/government.

## Processing pipeline — week by week

### Weeks 1-2: Data acquisition
- OpenAlex bulk download (or paginated API scraping) for each field of interest.
- Filter to field, sample stratified by year.
- Store as parquet files. ~500K papers of metadata is ~10GB; fits on a laptop.
- Quick sanity checks: year distribution, citation distribution, author count distribution, field-match quality.

### Weeks 3-4: Author disambiguation and demographic inference
- Use OpenAlex author IDs as primary disambiguation. These are imperfect — document failure modes.
- Run gender inference. **Document failure rates explicitly** — gender inference underperforms on non-Western names, and this is a potential confound for any cross-national analysis.
- Map affiliations to countries. Handle multi-affiliation papers (use primary or all).
- Compute career stage from author publication history.
- Build institutional prestige categories.
- **Gut check:** produce a basic demographic dashboard and see if it matches your intuitions about the field. If it looks wrong, debug now.

### Weeks 5-6: Embeddings
- First check S2AG coverage. If >80%, use their embeddings.
- If not, run SPECTER2 locally via HuggingFace. ~5K abstracts/hour on a decent GPU. 500K papers ≈ 4 days of overnight runs.
- Alternative: OpenAI `text-embedding-3-large` via API. Faster but ~$50-100 for the full sample.
- Store embeddings as numpy arrays or in a vector DB alongside paper IDs.

### Weeks 7-8: Metric computation
For each year (or year-bucket):
- **Demographic**: Shannon entropy per dimension; Simpson's index; Rao's quadratic entropy using pairwise distance in a joint demographic feature space.
- **Semantic**: effective dimensionality (participation ratio of PCA eigenvalues); mean pairwise distance; entropy over k-means cluster assignments; semantic-volume measures.
- **Canonical concentration**: Spearman correlation of top-50 (or top-100) most-cited lists between year t and year t+Δ; citation Gini; fraction of citations to top-k works of prior years.
- **Controls**: publication volume, average paper length, average number of authors, average references per paper.

### Weeks 9-11: Robustness
**This is where papers live or die. Budget 2-3 weeks; do not skip.**

Re-run everything under:
- Different embedding models (SPECTER2, text-embedding-3-large, e5-large or Gecko if accessible).
- Different diversity metrics within each category.
- Different sampling strategies (uniform vs. citation-weighted vs. top-cited only).
- Different field definitions (main CS query vs. narrower subfield vs. broader).
- Different demographic-inference approaches (free vs. paid gender tools).
- Different time-bucket sizes (annual vs. 5-year windows).

Your main finding must survive most of these. If it doesn't, the finding is methodological not substantive, and you need to report that honestly.

### Weeks 12-14: Writing

## The hardest technical challenge: embedding drift

Modern embeddings trained on modern data may distort representations of older text. A 1975 paper embedded with a 2024 model sits in a space optimized for 2024 semantics; the model's pretraining data underrepresents 1970s scientific vocabulary and may overrepresent terms that have changed meaning ("neural network" in 1975 vs. 2024).

**Mitigation strategies, in increasing order of effort:**

1. **Use SPECTER2** as default — domain-trained on scientific text, more robust than general-purpose embeddings. Cheap, always worth doing.
2. **Check drift with a second embedding model** — if results replicate under text-embedding-3-large or Gecko, drift probably isn't driving them. Moderate effort.
3. **Period-specific embeddings** — train or fine-tune embeddings on each era separately, then align spaces using anchor papers appearing in both periods. Substantial effort.
4. **Anchor-dimension projection** — project embeddings onto dimensions defined by stable concepts (author names, universally agreed methods) and report metrics there in addition to raw space.

**Recommendation**: do (1) always, do (2) if a second model is easily available, acknowledge (3) and (4) in limitations. Do not let full methodological work on embedding drift consume this paper.

## What the paper's main figure looks like

Picture a 3-panel plot, same x-axis (year, 1970-2024):

- **Top panel**: demographic diversity over time (multiple colored lines for gender, country, institution).
- **Middle panel**: semantic diversity over time (multiple metrics, shaded error bands).
- **Bottom panel**: canonical concentration over time (Gini, top-k share).

Then a critical second figure: **residual semantic diversity after controlling for field growth, publication volume, and demographic composition, plotted against year.** This is where the divergence, if real, shows up cleanly.

Then a third figure for cross-field comparison: the same residual plot for each field side by side.

Then a fourth figure for subfield decomposition within CS: the divergence magnitude as a function of subfield canonical-concentration score.

## Common failure modes and responses

| Failure mode | Response |
|---|---|
| Demographic and semantic diversity track each other | Genuine finding; partial disconfirmation of Claim #13; write it up as such. Less publishable in top-tier venues but still valuable. |
| Results vary wildly across fields | Likely outcome. Reframe paper as "methodology for field-specific measurement; pattern varies by field in these ways." Still publishable. |
| Measurement bias you can't rule out | Fatal. Mitigation: the robustness weeks. Don't skip them. |
| Embedding drift dominates | Invoke mitigations 2-4 above. If nothing removes it, acknowledge as limitation and bound the claim to post-2000 data where drift is smaller. |
| Author disambiguation errors swamp signal | Report error rates explicitly. Use only author-level aggregates where error is bounded. |
| Demographic inference bias (especially non-Western gender) confounds country effects | Run sensitivity analyses stratified by naming conventions; acknowledge bound. |
| Can't access Semantic Scholar embeddings | Use SPECTER2 locally; plan for 4-day embedding runs. |

## Venue and audience

**Target venues, in order:**
1. *Quantitative Science Studies (QSS)* — natural home, friendly to this work.
2. *Journal of Informetrics* or *Scientometrics* — respectable specialized venues.
3. *Nature Human Behaviour* or *PNAS* — stretch, if findings are strong and clean.
4. arXiv + blog post — always deposit regardless of peer review target.

**Who will review this:**
- Evans lab (Chicago): Chu, Foster, Wu, Rzhetsky. Expert on canonical concentration and disruption.
- Hofstra-Sekara-Sharkey cluster: expert on diversity-innovation dynamics.
- Azoulay group: economics of science, selection, career dynamics.
- Petersen/Holst camp: methodological critics of disruption-index literature; will scrutinize your metrics ruthlessly.

Write for them. Engage their critiques pre-emptively.

## Cost estimate

| Item | Low | High |
|---|---|---|
| LLM/embedding API | $50 | $300 |
| Gender inference service | $0 | $100 |
| Compute (local GPU assumed) | $0 | $50 |
| **Total money** | **$50** | **$500** |
| Time at 15 hrs/week | 10 weeks | 14 weeks |
| Elapsed (realistic, with life events) | 3 months | 5 months |

## Epistemic scope and limits

Added 2026-04-24 during Phase 0.1 scoping conversations. Makes explicit
what ws2 can and cannot establish as a piece of observational
scientometric work.

### The measurement-construct gap

Ws2 measures surface markers — novelty (by embedding distance), adoption
(by citation patterns), team composition (by inferred demographics),
canonical concentration (by Spearman rank persistence). None of these
directly measures *innovation* in the substantive sense ("genuine
advancement of knowledge"). Following Hofstra et al. 2020's explicit
move, we hold that novelty and adoption are proxies for innovation, not
substitutes for it:

- Novelty ≠ innovation (new is necessary but not sufficient for
  substantively new knowledge).
- Adoption ≠ innovation (adoption patterns are contaminated by structural
  processes independent of substantive merit).

Any claim ws2 makes about "innovation" is inferential — a structural
argument about patterns across multiple surface markers — rather than a
direct measurement.

### The counterfactual-requires-simulation limit

The diversity-innovation literature implicitly invokes a counterfactual:
what would adoption, novelty, and career outcomes look like if
structural biases were absent? The difference between observed reality
and that counterfactual is the "bias" that observational studies
attempt to infer.

This counterfactual is **not producible from observational data alone**.
Producing it requires two moves that observational scientometrics cannot
make:

1. Making implicit structural assumptions explicit — specifying which
   channels operate (shared canon, shared training, shared platforms,
   shared advisors), with what strength, on what subpopulations.
2. Varying those assumptions — asking what changes when channel X is
   removed or modified. This is an interventional operation, not a
   measurement.

Both moves live in simulation, not in data analysis. Ws2 can characterize
the phenomenon with rigor. It cannot identify the structural
counterfactual that would let us adjudicate (e.g.) the "discrimination"
versus "quality-difference" readings of demographic adoption gaps.

### The three-whitespace epistemic layering

The originality program's three whitespaces are not redundant; they
operate on complementary epistemic layers. Each layer's weakness is
another's strength.

| Whitespace | Method | What it establishes | What it cannot |
|---|---|---|---|
| **ws2** (empirical) | Observational scientometrics | The phenomenon; quantitative constraints any structural model must reproduce; mechanism-space narrowing via the subfield test | Counterfactuals; causal identification; true adjudication of discrimination vs. quality |
| **ws3** (theoretical) | Formal model decomposing cumulative preservation (C) and per-capita variance generation (V) | Plausible structural stories; identifiable parameters; qualitative regimes separating mechanism classes | Whether any particular story actually operates; which parameter values real science supports |
| **ws1** (simulation) | Agent-based simulation of actuator-homogenization dynamics | Counterfactual trajectories under explicit structural assumptions; intervention effects on outputs; structural sensitivity analysis | External validity of simulation structure to real-world science |

Triangulating across layers is what makes the full research program
stronger than any single study. The layering is not a narrative
retrofit — it is the natural consequence of what each method can and
cannot establish.

### What ws2 specifically contributes under this limit

Given ws2 cannot produce the counterfactual, its contributions are:

1. **Phenomenon-level falsification.** If Tests I–III show no divergence,
   or if the subfield mechanism test produces γ₁ ≈ 0, the actuator-
   homogenization structural claim is directly challenged. This matters
   without requiring causal identification — the data refutes structural
   claims even if it doesn't identify the true alternative.
2. **Quantitative anchoring for ws1.** Any structural simulation in
   whitespace 1 must reproduce ws2's time-series patterns, subfield-
   mechanism results, and Test IV cross-sectional regression. Ws2's
   findings become empirical targets that simulations must match, not
   just hypotheses they might test.
3. **Mechanism-space narrowing.** The subfield mechanism test localizes
   where structural processes plausibly concentrate — evidence that
   narrows the class of plausible simulation architectures ws1 needs to
   build.
4. **Explicit identification of what simulation would adjudicate.** Ws2's
   Discussion names the specific unresolved counterfactuals that
   simulation work could answer (e.g., "what adoption pattern would obtain
   if canonical concentration were held flat across subfields?"). This
   gives ws1 a sharp research agenda rather than a vague charge.

### Implications for the ws2 paper's framing

Methods and Discussion should include (paraphrased):

> "Our analysis is observational. We document patterns in surface
> markers — novelty, team diversity, adoption, canonical concentration —
> but cannot directly estimate what these patterns would look like
> absent the structural processes we hypothesize produce them. That
> estimation requires interventional evidence, whether from large-scale
> field experiments on scientific evaluation (impractical) or from
> simulation of explicit structural models (our program's whitespace 1).
> Ws2 contributes quantitative characterization of the phenomenon that
> any structural model must reproduce, plus evidence about where
> structural mechanisms likely concentrate (subfield test), while
> leaving the counterfactual adjudication to simulation-based follow-up
> work."

This is the canonical honest framing for observational scientometric
work on bias-vs-quality. Readers of Hofstra, the Evans lab, and Azoulay
recognize the move; reviewers from the methodological-critique cluster
(Petersen-Holst) find it defensible even if not decisive; simulation-
oriented reviewers understand why observational constraints motivate the
program's simulation arm. Hiding the limit would invite critique;
stating it pre-empts it.

### Citation measures as behavioral traces, not influence

A related measurement-construct gap applies to the adoption side of
the design. Citations are load-bearing in four places in ws2:

1. **Canonical concentration** (Tests I–III, third panel) — Chu-Evans
   Spearman top-N rank correlation + citation Gini.
2. **Test IV primary novelty (N_p)** — cosine distance from paper to
   centroid of cited-references' embeddings; citations define the
   intellectual context.
3. **Test IV persistence extension (Stage 3)** — C_k(p) = incoming
   citations received in year t+k; measures long-term attention.
4. **Test IV tertiary novelty (optional, Stage 3)** — reference-pair
   recombination if Uzzi-style is pursued; uses the reference list.

Hofstra et al. 2020's "plethora of reasons to cite" argument motivates
reducing citation load where possible. Citation behavior is
heterogeneous: ritual citations, self-citations, politeness citations,
citations-to-rebut, field-specific citation norms, citation inflation
over time (Petersen-Arroyave-Pammolli 2024). The measurement chain from
citation to substantive influence is long:

> **citation** → **attention** → **reception** → **influence**

Each arrow is a non-trivial interpretive step. Observational scientometric
data gives us the first (citation behavior). Inferring influence requires
either (a) causal-identification strategies we don't deploy, or (b)
interventional simulation of explicit influence channels — which is
whitespace 1's domain, not ws2's.

**Ws2's explicit move.** Where feasible, we reduce citation load by
running citation-independent parallel measures:

- Test IV secondary novelty: Hofstra-style concept-linkage (first
  pairwise co-occurrence of FREX concepts with PMI filter in paper's
  abstract). Runs alongside embedding-distance primary as a citation-
  free second novelty measure. Co-movement across the two is real
  cross-methodology robustness.
- If Test IV tertiary is pursued: Hofstra-style concept-pair
  recombination preferred over Uzzi-style reference-pair recombination,
  for the same reason — further reduces citation dependency.

**Where citations remain load-bearing (no substitute).** Canonical
concentration and persistence are fundamentally adoption measures;
concept-linkage reuse has its own analog "plethora of reasons" problem
(ritual reuse, peripheral mention) and doesn't cleanly dodge the
underlying confound. Here the honest move is acknowledgment in Methods
rather than methodological escape.

**Methods section commitment.** A short paragraph near the opening of
Methods should state explicitly:

> "Our reception and adoption measures are citation-based. We use
> 'citation' rather than 'influence' throughout. Citations are
> behavioral traces, shaped by citation norms, field conventions, and
> structural processes. Inferring influence — a causal relationship —
> from citation patterns requires interpretive steps we do not take
> in this paper. Canonical-concentration metrics (Chu-Evans Spearman)
> should be read as measuring the concentration of year-over-year
> citation attention on a top-N cohort, not the concentration of
> intellectual influence. Where citation independence is feasible
> (novelty measures), we run citation-independent parallel metrics as
> robustness; where it isn't (adoption measures), we acknowledge the
> limit rather than engineer around it."

This mirrors the novelty-vs-innovation distinction (above) in
structural form: surface marker, intermediate construct, substantive
target, with honest framing about which gap our measurements do and
don't close.

### When to revisit this section

This section is a framing commitment. Revisit if:

- Phase 0.1 sanity checks reveal that the phenomenon level is itself
  contested (e.g., Test I produces no divergence under any specification),
  at which point the scope discussion shifts from "what does the
  divergence mean" to "is there a divergence to interpret."
- Ws1 starts producing simulation results whose counterfactual answers
  are reported in ws2 (they shouldn't be — simulation findings belong in
  ws1's own paper).
- A referee pushes on the counterfactual claim in a specific way that
  requires sharper language than this section provides.
- A referee pushes on the citation-as-influence concern in a way that
  requires more specific disclaimers than the Methods paragraph above.

## What "done" looks like

You have a paper draft with:
- Three main time-series figures plus residual decomposition.
- Cross-field replication (at least 2 fields).
- Within-field subfield decomposition linking canonical concentration to divergence magnitude.
- Robustness table showing the main finding holds (or doesn't) under varied embeddings, metrics, and sampling.
- Honest discussion of demographic-inference and embedding-drift limitations.
- Clear positioning as a contribution that empirically grounds (or disconfirms) a widely-held informal claim.

You have submitted to arXiv.

You have submitted to one peer-reviewed venue.

If the primary finding is divergence: you have the empirical targets that any simulation study (Whitespace 1) would need to reproduce.

If the primary finding is non-divergence: you have a substantive falsification that redirects the whole research program, saving you and others substantial wasted simulation effort.

Either way, you have a first paper on a research agenda that, combined with Whitespace 3, positions you for funding Whitespace 1.

## Key references to re-read when stuck

- Hofstra et al. 2020 (PNAS, "Diversity-Innovation Paradox") — closest prior work; cross-sectional but methodologically adjacent.
- Chu & Evans 2021 (PNAS, "Slowed canonical progress") — the template for canonical concentration measurement.
- Park, Leahey & Funk 2023 (Nature, "Papers are becoming less disruptive") — the contested headline you're contextualizing.
- Petersen, Arroyave & Pammolli 2024 (QSS) — the critique of Park-Leahey-Funk; your methodological check.
- Holst et al. 2024 (arXiv:2402.14583) — dataset-artifacts critique; essential for your robustness discussion.
- Foster, Rzhetsky & Evans 2015 (ASR, "Tradition and innovation") — strategy-frequency work that complements canonical concentration.
- Wu, Wang & Evans 2019 (Nature, "Large teams develop") — the team-size lens on disruption; relevant for interpretation.

## Note to self, for when morale dips

This paper is *cheap* relative to its potential impact. The core observation — nobody has jointly measured these two variables over time — is a real gap, and filling it requires no new data collection and no novel methods. You're stringing together existing tools to answer a question people keep gesturing at without answering. That's exactly the kind of contribution that gets cited durably.

If you get six weeks in and feel like it's not going anywhere, the most likely problem is that you're over-thinking the embeddings or the demographic inference. Pick defensible defaults, run the analysis end-to-end, then iterate. Don't let methodological perfectionism prevent you from seeing the first-pass result.

If the first-pass result is ugly, that's fine. You now know what to debug. If it's clean, you're almost done.
