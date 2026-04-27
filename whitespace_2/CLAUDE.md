# Whitespace 2: Empirical Decomposition of Demographic vs. Semantic Plurality

## Project Thesis

Decompose demographic plurality, semantic plurality, and canonical concentration
in ~5–10M OpenAlex CS papers (1970–2024) as independent annual time series.
If demographic diversity rises while semantic diversity stagnates or falls,
that empirically grounds the program's central claim (#13) that intellectual
plurality has decoupled from demographic plurality. If the two track, the
claim is disconfirmed — a successful null.

## Current State

- **Current Stage:** Stage 0 — Foundation
- **Current Phase:** Phase 0.1 — sanity checks 1 + 2 complete; N1 plan
  revision pending
- **Completed:**
  - Repo scaffold
  - Tier 1 literature review (`literature-review/` 01-07)
  - Phase 0.1 plan with 14 numbered methodology commitments (§1-§14)
  - Phase 0.1 Check 1 (abstract availability) + extensions 1c (by paper
    type), 1d (arXiv linkage + access-method verification), 1e (S2AG
    coverage), 1f (bias-of-missingness across substantive measurement axes)
  - Phase 0.1 Check 2 a/b/c (concept-classifier drift) + 2d (anachronism
    audit) + 2e (hand-audit setup) + Check 2 score-thresholding correction
    + within-window anachronism verification
- **Next:** Phase 0.1 N1 — wholesale plan revision (see
  `tasks/todo.md` "Next session — N1 wholesale plan revision")

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
