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

## Change Log
(Empty — amend only by proposing a Phase X.Y desiderata amendment with rationale.)
