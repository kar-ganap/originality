# Whitespace 2: Empirical Decomposition of Demographic vs. Semantic Plurality

## Project Thesis

Decompose demographic plurality, semantic plurality, and canonical concentration
in ~5–10M OpenAlex CS papers (1970–2024) as independent annual time series.
If demographic diversity rises while semantic diversity stagnates or falls,
that empirically grounds the program's central claim (#13) that intellectual
plurality has decoupled from demographic plurality. If the two track, the
claim is disconfirmed — a successful null.

## Current State

- **Current Stage:** Stage 2 — Walk **(Phase 2.2 COMPLETE — the pre-registered
  test is run).** Stage 1 CLOSED. **Headline: Claim #13 robustly DISCONFIRMED
  (successful null), reframed as "the citation canon concentrates while the
  semantic frontier + authorship diversify."** The pre-registered ratio
  estimator returned a "divergence" that was a demographic-denominator confound;
  raw absolute trends + a full robustness stack (Qwen3 swap, K-sweep, clean
  subset) show no robust semantic decline, and an independent correctness
  battery verifies the pipeline. See `docs/phases/phase-2.2-retro.md`. **To
  fully wrap up WS2:** subfield mechanism test (the pre-registered "single most
  important analysis"), publication-grade figures, paper draft.
- **Phase 0.1 (Foundation scoping):** COMPLETE. See
  `docs/phases/phase-0.1-retro.md`.
- **Phase 0.2 (Pre-registration + Stage-1 prereqs):** COMPLETE
  2026-05-05. See `docs/phases/phase-0.2-retro.md`. All 7 prereq
  waves closed (1A Qwen3 batching, 1B NamSor smoke, 1C pull-spec
  dry run, 2A §11 production validation, 3A ORCID-linkage
  audit, 4A Stage 2 compute decision, 4B Genderize procurement
  resolved no-op). All 10 Phase 0.2 → Stage 1 validation gates met.
- **Phase 1.1 (Compute substrate):** COMPLETE. Modal A100 preempt
  + resumable runner + 50K dry-run. See `docs/phases/phase-1.1-retro.md`.
- **Phase 1.2 (Production §0 pull):** COMPLETE. Bulk-dump parse →
  v3 analytical population **24,492,279 papers** (v2 retained as
  robustness pair). §0 amended to v3 (score≥0.40, abstract-token-50,
  publisher-chrome + title-prefix blacklists). See
  `docs/phases/phase-1.2-retro.md`.
- **Phase 1.3 (Disambiguation + demographic inference):** COMPLETE
  2026-06-30. Per-(year×field×region) demographic coverage tables
  on v3 + v2 with §9e bias-corrected gender + geographic diversity.
  **Headline: CS female share 22.4% (1975) → 31.9% (2025)**, robust
  to §0 filter (v2↔v3 within 1.4pp) + correction axis. See
  `docs/phases/phase-1.3-retro.md`.
- **Phase 1.4 (Pre-Stage-2 gates + 100K pilot + pre-registration):**
  COMPLETE 2026-06-30. Sanity gates pass (year-bound 1970–2024;
  China's CS rise 2%→30% validates the country inference); Stage-2
  metric code lifted to `src/` (`semantic_metrics`, `canonical_metrics`,
  `divergence`); 100K mini-Stage-2 pilot de-risked the embed→semantic→
  divergence chain ($0.22) + surfaced 3 findings; **divergence test
  PRE-REGISTERED** (`docs/phases/phase-2.0-plan.md`, §5). **Stage 1
  CLOSED.** See `docs/phases/phase-1.4-retro.md`.
- **Phase 2.1 (Stage-2 metric machinery + base 1M embed):** COMPLETE
  2026-07-01. All 6 acceptance gates pass. §11 cluster-fit
  (`src/whitespace2/cluster_fit.py`, `project_to_clusters ==
  KMeans.predict`) + production fit on the 1M SciNCL vectors (effective
  47.4/50 clusters); career-stage joint gender×country×career plurality
  (MM Shannon + Gini-Simpson) in `build_coverage_table`; age-restricted
  canonical control (`age_restricted_concentration`, fixed-window dropped);
  **base 1M v3 embed** SciNCL (norm 23.70) + Qwen3 (norm 1.000), 902,531
  in-window papers, ~$17.4, via a parallel resumable Modal `.map()` path
  (`run_mapped`, `return_exceptions=True`). Vectors on Modal volume
  `ws2-embeddings` `/base-1m/`. See `docs/phases/phase-2.1-retro.md`.
- **Phase 2.2 (compute the 3 series + run the pre-registered test):**
  COMPLETE 2026-07-01. **Claim #13 robustly DISCONFIRMED — a successful null,
  reframed: the citation canon concentrates (reference-canonicity Gini ↑) while
  the semantic frontier (pairwise cosine ↑ robustly; cluster-entropy /
  effective-dim noisier) AND authorship (+3.3σ) diversify.** The pre-registered
  *ratio* estimator returned "divergence" for both fields, but it is
  **denominator-confounded** (ratio falls whenever demographic outpaces
  semantic, even as semantic rises); the residual "critical second figure" is
  collinearity-limited (year VIF 44–60); the one narrowing signal (Physics
  effective-dim) reverses under Qwen3. A full robustness stack + an independent
  correctness battery (metrics cross-checked vs scipy/sklearn; year-shuffle +
  noise placebos find 0 spurious trends) confirm a robust null. New src:
  `reference_canonicity`, `build_joint_plurality_series`, `permutation_slope_test`,
  `standardized_effect`, `residual_trend`. Amendments PA-1/2/3 in
  `phase-2.0-plan.md` §5. See `docs/phases/phase-2.2-retro.md`.
- **Methodology locks** (per `docs/phases/phase-0.2-plan.md` +
  Phase 0.2 retro):
  - **§0 analytical population**: score≥0.3 + has_abstract +
    25-token post-2000 junk-year filter (word-boundary regex) +
    15-token empty-abstract minimum
  - **§1 model stack**: SciNCL primary + Qwen3 cross-family;
    SPECTER2 retained for Stage 3 robustness swap + SciNCL
    fallback (per
    `docs/phases/phase-0.2-scincl-primary-contingency.md`)
  - **§4 ORCID-linkage validation**: PASS at 98.6% overall (per
    Wave 3A); §9a P5 ground-truth subsample fully usable across
    all regions
  - **§11 cluster-fit stratification**: H7' threshold revised
    1.43 → 1.10 (post-projection-bug-fix); SciNCL primary lock
    empirically validated (r_H75 ∈ [1.17, 1.44] across K)
  - **Stage 2 compute target**: Modal A100 preemptible at N=1M
    headline + N=500K robustness; budget $250-550 within §9 cap
- **Demographic substrate (Phase 1.3):** gender via gender_guesser
  primary + Genderize keyed cross-validation; NamSor **Option B**
  (sample-based per-region bias estimation, not direct labeling) →
  §9e-style correction; country from affiliations; reusable
  per-region bias kernel `experiments/phase-1.3/v3-confusion-matrix.json`.
- **Next — wrap up WS2 (Stage 2→3 close-out):** the pre-registered test is
  run; to complete the study: **(1) the subfield mechanism test** — do
  canon-concentrated subfields show more demographic-semantic divergence? (the
  conceptual doc's "single most important analysis"; the last place a localized
  signal could live + the direct test of the reframing); **(2) publication-grade
  figures** (trim the incomplete final year; polish the 3-panel + residual +
  cross-field + subfield-decomposition); **(3) the paper draft** — thesis:
  "canon concentrates while the frontier diversifies, and the naive decoupling
  test manufactures the opposite." Optional robustness: Genderize-augmented
  demographic substrate; SPECTER2 third embedding family. **WS3 (theory) is
  queued AFTER WS2 wraps** (user-locked 2026-07-01); the WS2→WS3 bridge (a
  per-capita-V extension) is noted in `docs/phases/phase-2.2-retro.md`.

## Constraints

- Hardware: Apple M-series (local), limited to CPU / MPS for embeddings
- Primary data: OpenAlex bulk dump + API (free, but snapshot-dependent)
- Embedding model: SPECTER2 (domain-trained on scientific text); robustness
  with text-embedding-3-large
- Demographic inference: gender-guesser (local, free); country from
  affiliation; prestige from public rankings
- Budget: $50–500 total (embedding API + optional paid demographic services)
- Timeline: 3–5 months at ~15 hrs/week

## Structure

### Stages (headline only — detailed planning when a stage's turn arrives)

- **Stage 0 — Foundation:** literature review, OpenAlex scoping, field/concept
  IDs, pilot query.
- **Stage 1 (Crawl):** OpenAlex bulk fetch + stratified sample, author
  disambiguation, demographic inference, sanity checks against field intuitions.
- **Stage 2 (Walk):** embedding pipeline (SPECTER2), metric computation
  (entropy, Gini, pairwise distance, canonical concentration), 3-panel annual
  time-series figure.
- **Stage 3 (Run):** robustness sweep (embedding model swaps, metric
  variants, sampling strategies), cross-field replication (Physics), subfield
  mechanism test (canonical-concentration → divergence linkage), paper draft.

### Phases

Phases are small, atomic units within each stage. Each phase has:
- A single task, feature, or hypothesis class
- Explicit go/no-go validation gates defined before work begins
- A strict cycle: PLAN → TEST → IMPLEMENT → VERIFY → RETRO

Phase plans live in `docs/phases/phase-X.Y-plan.md`.
Phase retros live in `docs/phases/phase-X.Y-retro.md`.

## Build & Test

```bash
uv sync --extra dev
make test          # run all tests
make lint          # ruff check
make typecheck     # mypy strict
make clean         # remove build artifacts
```

For embedding work: `uv sync --extra dev --extra embed`.
For plotting: `uv sync --extra dev --extra plot`.

## Ground Rules

### Workflow

1. **Plan mode** for ANY non-trivial task (3+ steps). If things go sideways, STOP and re-plan.
2. **Phase lifecycle**: PLAN → TEST → IMPLEMENT → VERIFY → RETRO.
3. **TDD**: For code, tests first. For research, hypothesis + evaluation criteria first. Tests define "done."
4. **Only plan current phase in detail.** Future phases stay headline-level.
5. **Verification before done.** Never mark complete without proving it works.
6. **Objective before subjective.** Run automated/quantitative checks before qualitative review.
7. **Separation of concerns.** Docs/config drive design decisions. Code is a tool, not a decision-maker.
8. **Self-improvement loop.** After ANY correction, update `tasks/lessons.md`. Review at session start.
9. **Subagents** for research/exploration. One task per subagent. Keep main context clean.
10. **Autonomous bug fixing.** Just fix it. Zero context switching from the user.

### Code

- **Simplicity first.** Minimal code, minimal impact. Don't over-engineer.
- **No laziness.** Root causes. No temporary fixes. Senior developer standards.
- **Minimal impact.** Touch only what's necessary.
- **Reproducibility.** Pin OpenAlex snapshot dates, embedding model versions, library versions, random seeds. Raw data never modified.

### Experimental Discipline

1. **Pre-register hypotheses.** Write what you expect and why before running experiments. The primary divergence test is pre-registered per `docs/desiderata.md` §5.
2. **Report nulls honestly.** A disconfirmation of Claim #13 is a publishable result.
3. **Characterize distributions, not just means.** Confidence bands, sensitivity intervals, bootstrap distributions on every headline number.
4. **Multiple metrics per experiment.** Demographic: ≥2 metrics. Semantic: ≥2. Canonical: ≥2 (per `docs/desiderata.md` §8).
5. **Track spend.** Log all compute/API costs in `tasks/spend.md` at time of incurring, not retrospectively.

### Git

- Phase branches off `main` (e.g., `phase-0.1-openalex-scoping`).
- User merges manually. No force pushes.
- Small, focused commits. No Co-Authored-By lines in commits.

## Validation Gates (defaults, adapted per phase)

1. All tests pass (code phases) or all pre-registered evaluation criteria met (research phases).
2. Linting / typechecking clean (code phases).
3. Reproducibility: results regenerable from committed code + OpenAlex snapshot date + pinned model versions.
4. Retro written covering: hypothesis, what happened, surprises, what to change.

## Key References

- North star: `docs/conceptual.md`
- **Immutable principles (ws2): `docs/desiderata.md`**
- Program-level desiderata: `../docs/program/desiderata.md`
- Phase plans/retros: `docs/phases/`
- **Visual plan summary: `docs/plan-at-a-glance.md`** (Mermaid
  diagrams; keep in sync when phase plans change — see the
  "Companion documents and maintenance" section of each phase plan
  for specific update triggers)
- Statistics primer: `docs/primers/stats.{tex,pdf}`
- Topic-modeling primer: `docs/primers/topic-modeling.md`
- Literature review: `literature-review/README.md`
- Task tracking: `tasks/todo.md`
- Lessons: `tasks/lessons.md`
- Spend tracking: `tasks/spend.md`
- Program overview: `../docs/program/research_program_overview.md`
- Deep research (lit review + pathway DAGs): `../docs/program/originality_deepresearch_markdown.md`

## Known Gotchas

- **Embedding drift on old text.** Modern embeddings may distort 1970s abstracts. Required: cross-era nearest-neighbor sanity checks and replication across ≥2 embedding families before claiming any semantic-diversity trend pre-1990. See `docs/desiderata.md` §2, §3.
- **Demographic inference bias.** Gender/nationality inference underperforms on non-Western names. Required: documented coverage/confidence metric per variable; sensitivity bounds on headline numbers. See `docs/desiderata.md` §4.
- **OpenAlex snapshot drift.** OpenAlex updates continuously. Every run records snapshot date; re-running against a newer snapshot is a separate experiment. See `docs/desiderata.md` §1.
- **LLM recall risk is not relevant here** (no LLMs in the analysis loop), but the primary statistical test must be pre-registered before the full-data run to avoid implicit multiple comparisons.
- **Park-Leahey-Funk CD-index contested.** If using CD-index as a canonical-concentration proxy, cite the Petersen-Holst-Macher critique and use at least one alternative metric.
