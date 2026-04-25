# Topic Modeling Primer

**Scope:** This primer covers Latent Dirichlet Allocation (LDA), Structural
Topic Models (STM), FREX concept extraction, and coherence/exclusivity
diagnostics. It supports close reading of Hofstra et al. 2020 (Tier 1,
literature-review file 06), Kozlowski et al. 2022 (Tier 2, file 14), and any
future paper in the reading list that uses topic modeling. A final section
maps the concepts onto ws2's own cluster-entropy methodology, where the
analogies apply in adapted form.

This primer is deliberately written as long-form prose rather than equations-
first. For the underlying math notation used across ws2's primary methods,
see `stats.tex` / `stats.pdf`.

---

## 1. Latent Dirichlet Allocation (LDA)

### The problem LDA solves

You have a corpus of documents. You don't have labels. You want to discover
the latent *topics* the documents are about, and for each document, the
mixture of topics it covers.

"Topic" in this framework is a probability distribution over vocabulary. A
"politics" topic puts high probability on words like `election`, `vote`,
`senator`, and low probability on words like `protein`, `enzyme`. LDA does
not know what to call the topics — humans label them by inspecting the top
words.

### The generative story

LDA assumes documents are generated this way:

1. For each topic k ∈ {1, …, K}, draw a word distribution
   β_k ∼ Dirichlet(η) over the full vocabulary. This is the "topic itself."
2. For each document d:
   - Draw a topic mixture θ_d ∼ Dirichlet(α). This is "what document d is
     about" — a distribution over the K topics.
   - For each word position n in document d:
     - Pick a topic z_{d,n} ∼ Multinomial(θ_d).
     - Pick the observed word w_{d,n} ∼ Multinomial(β_{z_{d,n}}).

The Dirichlet priors (α for document-topic mixtures, η for topic-word
distributions) encourage *sparsity*: most documents use only a few topics
heavily, most topics concentrate on a relatively small portion of vocabulary.
This matches how real documents work — a sports article isn't equally about
50 topics; it's mostly about 1–3.

### What inference gives you

LDA inference (via variational EM or Gibbs sampling) produces two matrices:

- **β matrix** (K topics × V vocabulary): each row is a topic's word
  distribution. Row k tells you what words topic k tends to emit.
- **θ matrix** (D documents × K topics): each row is a document's topic
  mixture. Row d tells you what topics document d is about.

### Choosing K

K is a hyperparameter — LDA doesn't find the "right" K. You fit at multiple
K values and use diagnostics (covered in Section 4) to pick one. Common
practice: fit at K ∈ {50, 100, …, 1000} and look for where diagnostics
plateau.

### Limitations

- **Bag-of-words model.** LDA ignores word order. "Dog bites man" and "man
  bites dog" are identical to LDA.
- **No syntax, no semantics beyond co-occurrence.** It only knows what
  words appear together.
- **Random initialization sensitivity.** Different random seeds can produce
  different topic solutions on the same corpus; topic indices are not
  comparable across runs without explicit alignment.
- **Stopword handling is load-bearing.** Pre-processing (removing common
  stopwords, stemming) dramatically affects what topics look like.
- **No covariate awareness.** Plain LDA doesn't use document metadata.

### Intuition with a concrete example

Run LDA on 10 years of newspaper articles with K=10. You might discover:

- Topic 1 (sports): `team`, `game`, `player`, `score`, `coach`
- Topic 2 (politics): `election`, `vote`, `candidate`, `poll`, `senate`
- Topic 3 (finance): `market`, `stock`, `trade`, `fed`, `earnings`
- Topic 4 (weather): `storm`, `rain`, `temperature`, `forecast`
- …

An article about "election coverage on TV" would have θ heavily weighted on
topic 2 (politics), with a small amount on topic 1 if sports metaphors
appear. The model discovered this structure from word co-occurrence alone;
nobody told it these are the categories.

---

## 2. Structural Topic Models (STM)

### The extension

STM (Roberts, Stewart, Tingley, Airoldi et al., 2013–2014) extends LDA by
letting **document metadata** influence topic *prevalence* (how much a
document uses each topic) and optionally topic *content* (which words show
up in a topic under different metadata conditions).

Metadata examples: publication year, author demographics, journal, country
of origin, discipline.

### Generative story — prevalence version

Same as LDA, but with one change: θ_d depends on a vector of covariates x_d:

θ_d = softmax(X_d · γ + noise)

where X_d is the covariate vector for document d and γ is a learned
regression coefficient matrix (K topics × number of covariates). The model
estimates how each covariate shifts the distribution over topics.

### What this buys you

- **Longitudinal analysis.** With `year` as a prevalence covariate, the model
  can discover that topic 7 (e.g., "deep learning") grew from near-zero
  prevalence in 1980 to substantial prevalence by 2020. This is implicit in
  the fit, not a post-hoc analysis.
- **Metadata testing.** You can test whether a covariate significantly
  affects topic prevalence, e.g., "do papers by women emphasize topic 12
  more than papers by men, holding year and discipline constant?"
- **Better fit on corpora with real temporal or group structure.** When the
  covariates actually matter, STM finds more interpretable topics than LDA.

### When STM does not meaningfully differ from LDA

In Hofstra et al. 2020, the authors tried STM with year as prevalence
covariate and reported (SI p. 5):

> "We found that including publication metadata in θ had little impact on
> the β distributions we use to extract documents. … STMs and simpler LDA
> topic models produced very similar β distributions."

This is worth remembering. STM's advantage over LDA is real only when the
downstream use is *inference about metadata effects on topics*. If you only
need β distributions for downstream concept extraction (as Hofstra does),
LDA would have given you similar results.

### Available covariates in STM

- **Prevalence covariates** (affect θ): e.g., year, discipline, author group.
- **Content covariates** (affect β per covariate level): e.g., let the
  topic's vocabulary itself vary by era. Hofstra did not use content
  covariates; modeling β(year) was computationally intractable.

### Practical workflow

1. Preprocess text (tokenize, remove stopwords, stem, extract n-grams).
2. Fit STM at multiple K values with your chosen covariates.
3. Pick K using diagnostics (next section).
4. Inspect topics by eyeballing β_k top words.
5. For downstream analysis, use either θ (document-topic mixtures),
   β (topic-word distributions), or derived objects like FREX scores.

---

## 3. FREX weighting

### The problem

After fitting LDA or STM, each topic's β_k is a probability distribution
over the entire vocabulary. To describe topic k to humans, you want to
display its "top words." But "top" is ambiguous:

- **Most frequent by β_k(v)**: you get words that are common *within this
  topic*. But common words tend to be common across many topics (data,
  study, results, analyze). The top-5 by frequency may look nearly
  identical across topics, which is useless for telling topics apart.
- **Most exclusive**: words whose total probability mass is concentrated in
  this one topic. But these tend toward rare, idiosyncratic terms
  (misspellings, one-off domain jargon, OCR errors) that don't inform
  reader about what the topic is.

### The FREX fix (Bischof & Airoldi 2012)

FREX combines frequency and exclusivity via a weighted harmonic mean of
their ranks. Formally, for a word v in topic k:

FREX(v, k) = 1 / [ w / ECDF_exclusivity(v, k) + (1 − w) / ECDF_frequency(v, k) ]

where:

- **frequency**(v, k) = β_k(v) — v's probability in topic k.
- **exclusivity**(v, k) = β_k(v) / Σ_j β_j(v) — what share of v's total
  probability mass (across all topics) is concentrated in topic k.
- **ECDF** (empirical cumulative distribution function) — normalizes raw
  values to percentile ranks (0 to 1) across the vocabulary.
- **w** ∈ [0, 1] — a weight balancing the two.

### Intuition

A word's FREX score is high only if it's *both* reasonably frequent in the
topic *and* reasonably exclusive to it. A word common in the topic but also
common everywhere (generic filler) has low exclusivity → low FREX. A word
exclusive to the topic but rarely used (idiosyncratic term) has low
frequency → low FREX. Words in the "common here, rare elsewhere" sweet
spot score high.

### The weight parameter

- **w = 0.5** (balanced, 50/50): Hofstra's main setting. Frequency and
  exclusivity contribute equally.
- **w = 0.75** (frequency-dominant, 75/25): tilts toward common-in-topic
  terms; tends to surface general vocabulary that happens to be this
  topic's most-used.
- **w = 0.25** (exclusivity-dominant, 25/75): tilts toward topic-specific
  terms; tends to surface specialized vocabulary.

Hofstra reports main results at 50/50 and runs robustness at all three
weights × three K values (400, 500, 600), giving nine sensitivity scenarios.

### Why FREX matters for downstream analysis

If you're using topic-extracted terms as *concepts* for further analysis
(as Hofstra does — FREX terms are the concept vocabulary for their novelty
measurement), the FREX weighting is load-bearing:

- Too frequency-heavy: concepts become generic; their co-occurrences are
  meaningless (half of science uses "data").
- Too exclusivity-heavy: concepts become idiosyncratic; their
  co-occurrences are rare and noisy.

The balanced setting is the defensible default when the use is
interpretable concept extraction.

---

## 4. Coherence, exclusivity, and K selection

K is a hyperparameter — LDA and STM do not discover it. You pick K based
on diagnostics. Two kinds of diagnostics: **internal** (computed from the
topic model alone) and **external** (checking alignment with independent
labels).

### Semantic coherence (Mimno et al. 2011)

Coherence asks: *do the top words of a topic actually co-occur in real
documents?*

For topic k with top N words v_1, …, v_N ranked by β_k:

C(k) = Σ_{i<j} log [ (D(v_i, v_j) + 1) / D(v_j) ]

where D(v_i, v_j) counts documents in which both v_i and v_j appear, and
D(v_j) counts documents in which v_j appears. The +1 is smoothing.

**Intuition.** The log-ratio asks, given that v_j appears, how often does
v_i co-appear? If the topic is coherent, these co-occurrence rates are
high and log-ratios are less negative. Summed over pairs of top words
gives the topic's coherence. Averaged across topics gives the model's
coherence.

**Range.** Typically negative. Higher (less negative) = more coherent.

**K dependence.** Coherence *decreases* as K grows. Reason: more topics →
each topic has fewer documents genuinely supporting it → top words are
less likely to co-occur in that thin support. A single broad "biomedicine"
topic has many supporting documents and very coherent top words; splitting
it into 30 biomedical sub-topics thins the support set and drops co-
occurrence rates.

### Exclusivity (aggregate)

Aggregate exclusivity for a topic is the mean exclusivity of its top N
words (same definition as FREX's exclusivity component).

**K dependence.** Exclusivity *increases* as K grows. Reason: more topics →
each topic specializes → top words become more unique to their topic. With
K=50, each topic is broad and its top words include general terms that
also dominate other topics. With K=500, each topic is narrow and its top
words concentrate heavily within it.

### The coherence-exclusivity trade-off

As K grows:

|        | Small K       | Large K       |
|--------|---------------|---------------|
| Coherence | high (broad topics, dense support) | low (narrow topics, thin support) |
| Exclusivity | low (generic top words) | high (topic-specific top words) |

These move in opposite directions. Neither alone picks K. The practical
rule is to **pick K where both metrics stabilize** — beyond that K,
adding topics pays coherence cost without exclusivity gain.

### External validation

Internal metrics can't tell you if the discovered topics match anything
real. For that you need external labels.

**Keyword/field agreement** (Matthew correlation, what Hofstra uses): form
two document-to-document networks, one from topic-mixture similarity and
one from author-declared keywords/fields. Measure overlap at the
document-pair level via MCC:

MCC = (TP · TN − FP · FN) / √[(TP+FP)(TP+FN)(TN+FP)(TN+FN)]

High MCC = topic model agrees with human-curated labels. Plateau in MCC as
K grows = topic model has converged on the human-distinguishable
structure.

**Cluster stability across K** (Fowlkes-Mallows index, Hofstra's panel D):
classify each document by its highest-probability topic at K = K₁ and at
K = K₂. Compare the resulting partitions. High FM = the models mostly
agree on which documents belong together, just with finer distinctions at
higher K. Low FM = models discover totally different structure at
different K values, which suggests instability.

### How Hofstra picks K

Four independent diagnostics — coherence, exclusivity, MCC with keywords,
Fowlkes-Mallows across K — all converge on K ∈ [400, 600]. They use
K=500 as the middle and show Table S2 that results hold at K=400 and K=600.

The general principle — *pick K where multiple independent diagnostics
agree* — generalizes well beyond topic modeling.

---

## 5. How these concepts map onto ws2's own methodology

ws2 does not use LDA or STM. Our primary text representation is SPECTER2
document embeddings, and our primary semantic-diversity metric is
**cluster entropy** over K-means clusters of those embeddings (see
`phase-0.1-plan.md` subsection 1 and the pre-registration of Test IV's
semantic primaries). The topic-modeling diagnostics transfer to our
cluster-entropy pipeline in adapted form.

### Coherence → cluster cohesion

Topic coherence asks whether top words of a topic co-occur in documents.
Our cluster analog: **are the embeddings in cluster k packed closely in
embedding space?** Metrics:

- **Silhouette score** (per-point mean intra-cluster distance vs. mean
  nearest-other-cluster distance, aggregated). Range −1 to +1. Higher =
  tighter, better-separated clusters. The closest moral analog to Mimno
  coherence.
- **Within-cluster sum of squares (WCSS / inertia)** — K-means minimizes
  this directly. Always decreases with K; elbow method looks for the
  bend, not the minimum.

### Exclusivity → cluster separation

Topic exclusivity asks whether top words concentrate in one topic or
spread across many. For hard clustering (K-means, where each point is in
exactly one cluster), exclusivity in the same form doesn't apply — there's
no probability mass to split. But the *spirit* (cluster distinctiveness)
maps onto **inter-cluster separation**:

- **Calinski-Harabasz index**: ratio of between-cluster to within-cluster
  dispersion. Higher = better-separated clusters relative to internal
  scatter.
- **Davies-Bouldin index**: penalizes clusters that sit close to each
  other. Lower = better.

If ws2 ever switches from K-means to GMM (Gaussian mixture model), the
probability-mass-based exclusivity from topic modeling transfers directly:
point x's exclusivity to cluster k = P(k | x) / Σ_j P(j | x) = P(k | x).
Probably not worth the methodological switch just for this, but worth
flagging as a possibility.

### External validation → partition alignment with arXiv categories

Hofstra checks STM-based document similarity against keyword-based
similarity. Our equivalent: **does our K-means cluster partition align
with arXiv primary categories?** Measures:

- **Normalized Mutual Information (NMI)**: information-theoretic overlap
  between two partitions.
- **Adjusted Rand Index (ARI)**: chance-corrected pair agreement between
  two partitions.
- **Fowlkes-Mallows index (FM)**: same as Hofstra's Panel D but comparing
  our K-means partition to arXiv categories.

High agreement means our clusters are tracking real field structure. Low
agreement means the clusters are finding something else — could be a
feature (embeddings capture semantic patterns orthogonal to administrative
field taxonomy) or a problem (clusters are arbitrary).

### Cluster-stability across K

Hofstra's FM between consecutive K values (K=50 vs. K=100, etc.) checks
that adding topics mostly refines existing structure rather than
rearranging everything. We should do the same: compute FM between
K=30 and K=50, K=50 and K=75, K=75 and K=100. If our cluster assignments
are stable up to refinement as K grows, cluster entropy is robust to
K choice within the range.

### The pragmatic difference

For Hofstra, topics are a substantive output. Each topic is supposed to
*mean* something to a human reader. So topic-quality diagnostics are
load-bearing for interpretation.

For ws2, clusters are *instrumental*. They partition the embedding space
so we can compute Shannon entropy over the partition. We don't need humans
to find individual clusters meaningful; we need the partition to be stable
and interpretable under robustness checks. Our diagnostics should focus on:

1. **Stability of the K=50 main choice across K ∈ {30, 50, 75, 100}.**
2. **External validation against arXiv categories** — does the partition
   track anything observable?
3. **Temporal stratification of the cluster fit** (desiderata §11) — the
   non-negotiable commitment that clusters be fit on equal-per-decade
   subsamples, not the full corpus.

Topic modeling's "what's the right K" problem has an analog for us but
lower stakes — the K ∈ {30, 50, 100} robustness already handles the
"does the result depend on specific K" concern; the diagnostics are about
*justifying* the main K choice rather than discovering it.

### Proposed addition to ws2's plan

Extend sanity Check 5b (or add Check 5d) with a **cluster-quality
diagnostics** sub-check:

- **Internal**: silhouette score, WCSS with elbow analysis,
  Calinski-Harabasz index, reported as curves across K ∈ {20, 30, 50, 75,
  100, 150}.
- **External**: NMI / ARI / FM between K-means cluster labels and arXiv
  primary categories for the CS pilot subset.
- **Stability**: FM between consecutive K values.
- **Output**: `experiments/phase-0.1/cluster-quality-diagnostics.md`.
- **Decision rule**: if internal diagnostics plateau within K ∈ {30, 50,
  100}, the pre-registered robustness range is justified; if they don't,
  revise the range before Phase 0.2 pre-registration.

Half a day of Phase 0.1 work, uses data already being computed.

---

## 6. Suggested reading order for the topic-modeling literature

If you want to go deeper, in order of increasing specialization:

1. **Blei, Ng & Jordan 2003** (*JMLR*), "Latent Dirichlet Allocation" —
   the foundation paper. Relatively readable.
2. **Blei 2012** (*Communications of the ACM*), "Probabilistic topic
   models" — Blei's accessible review article. Better starting point than
   the 2003 paper for first-time readers.
3. **Roberts et al. 2014** (*Am. J. Political Science*), "Structural Topic
   Models for Open-Ended Survey Responses" — the STM introduction.
4. **Bischof & Airoldi 2012** (*ICML*), "Summarizing Topical Content with
   Word Frequency and Exclusivity" — FREX weighting.
5. **Mimno et al. 2011** (*EMNLP*), "Optimizing Semantic Coherence in
   Topic Models" — the coherence diagnostic.
6. **Tahmasebi, Borin & Jatowt 2021** (Language Science Press, open
   access), *Computational Approaches to Semantic Change* — broader
   context on temporal/diachronic NLP, including diachronic extensions of
   topic modeling.

For ws2's immediate purposes, Blei 2012 + Roberts et al. 2014 +
Bischof & Airoldi 2012 is enough background to read Hofstra, Kozlowski,
and any related topic-modeling paper critically.

---

## References

- Blei, D. M., Ng, A. Y., & Jordan, M. I. (2003). Latent Dirichlet
  Allocation. *Journal of Machine Learning Research* 3, 993–1022.
- Blei, D. M. (2012). Probabilistic topic models. *Communications of the
  ACM* 55(4), 77–84.
- Bischof, J. M., & Airoldi, E. M. (2012). Summarizing Topical Content with
  Word Frequency and Exclusivity. *ICML*.
- Mimno, D., Wallach, H. M., Talley, E., Leenders, M., & McCallum, A.
  (2011). Optimizing Semantic Coherence in Topic Models. *EMNLP* 262–272.
- Roberts, M. E., Stewart, B. M., Tingley, D., Lucas, C., Leder-Luis, J.,
  Gadarian, S. K., Albertson, B., & Rand, D. G. (2014). Structural Topic
  Models for Open-Ended Survey Responses. *American Journal of Political
  Science* 58(4), 1064–1082.
- Roberts, M. E., Stewart, B. M., & Airoldi, E. M. (2016). A Model of
  Text for Experimentation in the Social Sciences. *JASA* 111(515),
  988–1003.
- Rousseeuw, P. J. (1987). Silhouettes: A graphical aid to the
  interpretation and validation of cluster analysis. *J. Computational and
  Applied Mathematics* 20, 53–65.
- Caliński, T., & Harabasz, J. (1974). A dendrite method for cluster
  analysis. *Communications in Statistics* 3(1), 1–27.
- Davies, D. L., & Bouldin, D. W. (1979). A cluster separation measure.
  *IEEE Transactions on Pattern Analysis and Machine Intelligence* PAMI-1
  (2), 224–227.
- Fowlkes, E. B., & Mallows, C. L. (1983). A method for comparing two
  hierarchical clusterings. *Journal of the American Statistical
  Association* 78(383), 553–569.
- Tahmasebi, N., Borin, L., & Jatowt, A. (Eds.) (2021). *Computational
  Approaches to Semantic Change*. Language Science Press.
