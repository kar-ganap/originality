# Originality: A Research Program on Intellectual Plurality

## Program Thesis

Test whether and how intellectual plurality has decoupled from demographic
plurality in modern knowledge production (Claim #13), and whether small,
insulated groups produce disproportionate per-capita originality (Claim #17).
Three whitespace studies tackle the program in ascending order of cost/risk,
with each prior study de-risking the next.

## Whitespaces

- **Whitespace 2 — Empirical decomposition (ACTIVE).** Empirical time-series
  study on ~5–10M OpenAlex CS papers (1970–2024): do demographic, semantic,
  and canonical-concentration metrics diverge? See `whitespace_2/CLAUDE.md`.
- **Whitespace 3 — Theoretical reconciliation (future).** Formal model
  reconciling Henrich (larger populations preserve complexity) with
  Wu-Wang-Evans (small teams disrupt more per capita). See
  `whitespace_3/docs/conceptual.md`.
- **Whitespace 1 — Agent simulation (future).** LLM multi-agent model of
  opinion dynamics and actuator-driven homogenization. Activates after
  whitespace 2 lands.

## Current State

- **Active whitespace:** `whitespace_2/`
- **Program-level phase:** Scaffold complete; all downstream work happens
  inside the active whitespace.
- **Next:** `whitespace_2/` Phase 0.1 Check 5c (drift pilot) — see
  `whitespace_2/tasks/todo.md` "Next session — entry point" for the
  full handoff package, including required reading, recommended
  execution order (5c → 5b+5d → 3 → retro), open deferred decisions
  (Stage 2 compute target, Genderize API setup, junk-year token list
  expansion), and suggested entry prompt. Phase 0.1 is ~70% complete:
  N1 plan revision, N1+ adjustments, Phase 0.1.E embedding pipeline
  scaffold, and Checks 1+2 (with extensions), 4, 5a are all done.

## Navigating This Repo

- Program context → `docs/program/` (overview, deep research, pathway lineage)
- Immutable program principles → `docs/program/desiderata.md`
- Active study → `whitespace_2/` (each whitespace is a self-contained
  subproject with its own `CLAUDE.md`, `pyproject.toml`, `Makefile`, `docs/`,
  `tasks/`, `src/`, `tests/`)

## Build & Test

The program itself has no code. All `make` targets live inside each
whitespace. For the active study:

```bash
cd whitespace_2
uv sync --extra dev
make test          # run all tests
make lint          # ruff check
make typecheck     # mypy strict
```

## Ground Rules

### Workflow

1. **Plan mode** for ANY non-trivial task (3+ steps). If things go sideways, STOP and re-plan.
2. **Phase lifecycle**: PLAN → TEST → IMPLEMENT → VERIFY → RETRO.
3. **TDD**: For code, tests first. For research, hypothesis + evaluation criteria first. Tests define "done."
4. **Only plan current phase in detail.** Future phases stay headline-level.
5. **Verification before done.** Never mark complete without proving it works.
6. **Objective before subjective.** Run automated/quantitative checks before qualitative review.
7. **Separation of concerns.** Docs/config drive design decisions. Code is a tool, not a decision-maker.
8. **Self-improvement loop.** After ANY correction, update `whitespace_N/tasks/lessons.md`. Review at session start.
9. **Subagents** for research/exploration. One task per subagent. Keep main context clean.
10. **Autonomous bug fixing.** Just fix it. Zero context switching from the user.

### Code

- **Simplicity first.** Minimal code, minimal impact. Don't over-engineer.
- **No laziness.** Root causes. No temporary fixes. Senior developer standards.
- **Minimal impact.** Touch only what's necessary.
- **Reproducibility.** Pin all parameters, seeds, model versions, snapshot dates. Raw data never modified.

### Experimental Discipline

1. **Pre-register hypotheses.** Write what you expect and why before running experiments.
2. **Report nulls honestly.** Negative results are results. A whitespace that disconfirms its driving claim is a successful whitespace.
3. **Characterize distributions, not just means.** Point estimates without uncertainty are insufficient.
4. **Multiple metrics per experiment.**
5. **Track spend.** Log all compute/API/dataset costs in `whitespace_N/tasks/spend.md` at time of incurring, not retrospectively.

### Git

- Phase branches off `main` (e.g., `phase-0.1-openalex-scoping`).
- User merges manually. No force pushes.
- Small, focused commits. No Co-Authored-By lines in commits.

### Whitespace Independence

Whitespaces do not share a lockfile or virtual environment. Cross-whitespace
sharing happens via explicit, versioned utilities (not ambient coupling). If
a utility is reused across two whitespaces, it graduates to a shared package
with its own tests.

## Validation Gates (defaults, adapted per phase)

1. All tests pass (code phases) or all evaluation criteria met (research phases).
2. Linting / typechecking clean (code phases).
3. Reproducibility check: can results be regenerated from committed code + documented parameters?
4. Retro written covering: hypothesis, what happened, surprises, what to change.

## Key References

- Program overview: `docs/program/research_program_overview.md`
- Deep research (lit review + pathway DAGs): `docs/program/originality_deepresearch_markdown.md`
- Pathway lineage tables: `docs/program/pathway_lineage_tables.md`
- **Program desiderata (immutable):** `docs/program/desiderata.md`
- Active study: `whitespace_2/CLAUDE.md`

## Known Gotchas

- Embedding models trained on modern text may distort 1970s-era abstracts — see `whitespace_2/docs/desiderata.md` §3.
- Demographic inference (gender, nationality) is imperfect, especially for non-Western names — see `whitespace_2/docs/desiderata.md` §4.
- OpenAlex snapshots change; every result must be pinned to a snapshot date — see `whitespace_2/docs/desiderata.md` §1.
