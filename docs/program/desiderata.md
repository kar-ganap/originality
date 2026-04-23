# Originality Program — Desiderata

Immutable principles for the Originality research program.
Frozen after Phase 0. Changes require a Change Log entry with date and rationale.

## 1. Python + uv
Python 3.10+ only. uv as package manager. No pip.

## 2. Hypothesis-first research
Hypotheses with testable predictions are pre-registered before running
experiments. Evaluation criteria are written before results. The pre-registration
is a committed file, not a note.

## 3. Conceptual Doc is Law (per whitespace)
Each whitespace's `docs/conceptual.md` is the north star for that study. All
methodological, modeling, and data choices trace back to it. Cross-whitespace
decisions trace to `docs/program/research_program_overview.md`.

## 4. Reproducibility
Pin dataset snapshot dates, model versions (embedding, LLM, demographic
inference), library versions, random seeds. Raw data never modified. Every
reported number regenerable from committed code and parameters.

## 5. Raw Data Preservation
Raw OpenAlex dumps, raw S2AG embeddings, raw agent traces: immutable once
captured. Derived artifacts (aggregations, figures, tables) are regenerable.
If in doubt, keep the original.

## 6. Nulls Count
Negative results are results. A whitespace that disconfirms its driving claim
is a successful whitespace. Honest reporting of distributions — not cherry-picked
means — is non-negotiable.

## 7. Objective Before Subjective
Quantitative checks (tests, metrics, numeric sanity checks) precede qualitative
review. Numbers before narratives.

## 8. Separation of Concerns
Docs and config drive experimental choices. Pipelines and agent frameworks are
tools, not decision-makers. Protocol lives in docs/config, not hardcoded.

## 9. Git Workflow
Phase branches off main. User merges manually. No force pushes. No
Co-Authored-By lines in commits. Small, focused commits.

## 10. Documentation as Code
CLAUDE.md updated at the end of each phase. Phase plans before implementation.
Phase retros after. Everything in the repo. No out-of-repo "scratch" state that
matters.

## 11. Spend Discipline
All compute, API, and dataset costs logged in `tasks/spend.md` at the time of
incurring them, not retrospectively.

## 12. Whitespace Independence
Whitespaces do not share a lockfile. Cross-whitespace sharing happens via
explicit, versioned utilities (not ambient coupling). If a utility is reused
across two whitespaces, it graduates to a shared package with its own tests.

## Change Log
(Empty — amend only by proposing a Phase X.Y desiderata amendment with rationale.)
