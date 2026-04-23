# Whitespace 2 — Desiderata

Immutable principles for the empirical decomposition of demographic vs.
semantic plurality. Extends `../../docs/program/desiderata.md`.
Frozen after Phase 0.

## 1. OpenAlex Snapshot Pinning
Every run records the OpenAlex snapshot date (or commit hash of the release
used). Analysis is reproducible against that snapshot only; re-running against
a newer snapshot is a separate, logged experiment.

## 2. Embedding Model Pinning + Robustness
Primary embedding model (SPECTER2) version is pinned. Every headline result
is replicated with at least one alternative embedding family (e.g.,
text-embedding-3-large) and the divergence reported. A result that holds under
only one embedding is not yet a result.

## 3. Embedding Drift Acknowledgment
Modern embeddings may distort 1970s-era text. Limitations section explicitly
reports drift-sensitivity checks (held-out old papers, cross-era nearest
neighbor sanity checks). No claim about pre-1990 semantic diversity is made
without this.

## 4. Demographic Inference Transparency
Gender, nationality, career stage, and institutional prestige are inferred,
not observed. Each inferred variable carries a documented confidence/coverage
metric. Sensitivity analyses bound the confound for non-Western names and
ambiguous cases. Aggregate claims report both the headline number and a
demographic-inference-uncertainty bound.

## 5. Pre-registered Divergence Test
The primary statistical test of demographic-vs-semantic divergence is
pre-registered (metric, estimator, field, time window, null, threshold) in
`docs/phases/phase-2.X-plan.md` before full-data analysis runs. Exploratory
checks on pilot data are clearly labeled as exploratory.

## 6. Field-Level Robustness Required
A headline finding in CS is not a finding until replicated in at least one
additional field (Physics primary, Sociology/PhilPapers optional). Failure to
replicate is reported, not hidden.

## 7. Stratified Sampling Documented
Any sub-sample of OpenAlex is stratified by year and field concept; the
stratification scheme is committed to `data/metadata/` and referenced by every
pipeline step that consumes the sample.

## 8. Metric Plurality
Demographic diversity uses ≥2 metrics (e.g., Shannon entropy + Gini).
Semantic diversity uses ≥2 (e.g., mean pairwise distance + effective rank).
Canonical concentration uses ≥2 (e.g., Spearman top-N + Gini on citations).
No headline claim rests on a single metric choice.

## 9. Cost Gate on Embedding Runs
Any embedding run above $50 requires a written pre-commit estimate in
`tasks/spend.md` with expected cost, sample size, and what result it enables.
Prevents silently running a $400 job on accident.

## 10. Subfield Assignment Drift Acknowledgment
OpenAlex concept tags and Topics are assigned by a classifier trained on
modern text. Applied uniformly across a 50-year corpus, the classifier
systematically under-tags or mis-tags older papers, threatening the within-field
subfield mechanism test. Treated as a first-class methodological concern
parallel to embedding drift (§2, §3), with its own sanity checks and
mitigation ladder documented in the phase plan. The subfield mechanism test
is restricted to post-1990 data by default; pre-1990 subfield-level claims
require explicit classifier-drift audit results and are bounded accordingly.
Where possible (arXiv-covered papers), author-assigned arXiv categories are
preferred over classifier-assigned OpenAlex concepts.

## 11. Cluster-Fit Temporal Stratification
Any clustering, PCA basis, or other pooled-data model fit whose output is used
in a diversity metric (notably cluster entropy for semantic diversity) must be
fit on a temporally-stratified subsample with equal papers per decade — not on
the full corpus where modern papers outnumber old ones by an order of magnitude
or more. Fitting on the unstratified pool lets modern semantic structure
define the clusters or basis; old papers then map poorly to those modern
definitions and concentrate artificially in a few clusters, producing spurious
low-diversity in early years and a spurious divergence trend. This would
manufacture the paper's headline finding as a corpus-composition artifact.
Treated as a first-class methodological concern parallel to §2, §3, §10. The
stratification scheme is committed to `data/metadata/` alongside the cluster
centroids or basis vectors and referenced by every pipeline step that consumes
them.

## Change Log

- **2026-04-23 (Phase 0.1 amendment):** Added §10 on subfield assignment
  drift. Rationale: during Phase 0.1 scoping, recognized that the OpenAlex
  concept classifier has the same "modern model applied to old text" structure
  as embedding drift (§2, §3), and similarly threatens the subfield mechanism
  test — arguably the paper's single most important analysis. Elevating to a
  first-class principle forces explicit treatment in every phase plan and the
  Methods section, parallel to embedding drift. No existing principles
  modified.
- **2026-04-23 (Phase 0.1 amendment):** Added §11 on cluster-fit temporal
  stratification. Rationale: during Phase 0.1 metric-definition discussion,
  cluster entropy was elevated to a primary semantic-diversity metric. Its
  correctness depends on clusters being fit on a temporally-balanced sample,
  not the full corpus. Without this stratification, modern papers dominate
  cluster definitions and the pipeline produces a spurious divergence trend
  as an artifact. Elevated to desiderata because a cluster-fit mistake would
  silently manufacture the paper's headline finding, which is exactly the
  failure mode desiderata exists to prevent. No existing principles modified.
