# Originality: A Research Program on Intellectual Plurality

## Program Thesis

Test whether and how intellectual plurality has decoupled from demographic
plurality in modern knowledge production (Claim #13), and whether small,
insulated groups produce disproportionate per-capita originality (Claim #17).
Three whitespace studies tackle the program in ascending order of cost/risk,
with each prior study de-risking the next.

## Whitespaces

- **Whitespace 2 — Empirical decomposition (empirical work COMPLETE; concentration leg
  WITHDRAWN 2026-07-22).** Time-series study on OpenAlex CS papers: do demographic,
  semantic, and canonical-concentration metrics diverge? The demographic rise and the
  semantic fragmentation (atypicality↑, three embedding families) both hold. **The
  canon-concentration leg is withdrawn on a matched null** (`src/whitespace2/null_ref_gini.py`,
  replay bit-exact): uniform random attachment with no canon reproduces **93%** of the
  `ref_gini` trend in both fields; `ref_gini` correlates `+0.999` with edges-per-distinct-target,
  never leaves the near-all-singletons regime (0.013→0.060, versus 0.8–0.99 for a real citation
  distribution), and rises near-identically in CS and Physics while the age-restricted citation
  Gini moves in *opposite* directions. That age-restricted series is the pre-registered substrate
  gate; in CS it **declines** at all three windows, and was never reported. See
  `whitespace_2/CLAUDE.md`.
- **Whitespace 3 — Theoretical reconciliation (Phase 1 + Phase 2 bridge COMPLETE;
  crossover claim UNDER REVISION as of 2026-07-22).** Minimal ABM decomposing cumulative
  complexity `C` from per-capita variance `V`, reconciling Henrich with Wu-Wang-Evans.
  The two-channel sign structure and bridge A (fragmentation fingerprint, 15.6× vs ~13×)
  both reproduce. **`λ*≈0.09` carries no CI** and interpolates between slopes individually
  indistinguishable from zero; at N=200–1500 the V-slope CI straddles zero at λ = 0/0.1/0.25
  and `∂C/∂logN = 0.0000` exactly, so neither half of "same lever, opposite signs" is
  statistically present at scale. See `whitespace_3/docs/conceptual.md`.
- **Whitespace 1 — Agent simulation (ACTIVE since 2026-07-21).** The mechanistic /
  counterfactual leg: manipulates the actuator WS2 could only observe and WS3 only
  theorize. Two chapters — **ch.1 Polyphony COMPLETE + public** (`../polyphony`);
  **ch.2 the OSS adjudication arm** designed, not built. See `whitespace_1/CLAUDE.md`.

## Current State

- **Active whitespace:** `whitespace_1/` (ch.2). WS2 and WS3 are complete; their
  remaining work is the write-up.
- **The program's headline result is WITHDRAWN as of 2026-07-22.** It read: intellectual
  plurality **decouples** from concentration — observed in humans (WS2), explained by
  theory (WS3), reproduced on an AI substrate (WS1 ch.1 R4). An independent per-arm audit
  found all three legs compromised, and independently: WS2's concentration is largely a
  reference-density artifact; WS3's crossover is not statistically present at scale; and
  the R4 replication was never in polyphony's record — it originated in this repo. **A
  matched null has now settled the AI leg (2026-07-22):** re-running R4's exact process
  with item preference removed reproduces the registered `+0.0102` at **+0.0153 (151%)**,
  and the popularity arm's concentration is indistinguishable from the null (p = 0.882
  raw, 0.289 normalized). That leg is **refuted**, not merely untested. WS2's and WS3's
  legs remain open pending their own nulls.
- **What still stands:** demographic plurality rises sharply (robust); semantic
  fragmentation in CS across three embedding families; recursive self-training collapses
  diversity, with 12.5% synthetic still collapsing 31–37% in two architectures (canary H1);
  role-diverse ensembles do not homogenize under shared-context conditioning, CI excluding
  zero in the opposite direction across three designs (polyphony); WS3's two-channel sign
  structure and bridge A. Plus four methods results: eff-dim scale-invariance, the
  ratio-estimator confound, CD-index observation-window fragility, and identifiability.
- **Next:** (a) `whitespace_1/` ch.2 — stimulus preflight, then the locked rung-0
  reachability probe (~$2.80). See `whitespace_1/tasks/todo.md`. (b) The papers —
  ~2 planned, split by thesis rather than substrate; division deferred until the
  remaining AI results land.

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
