# Phase 0.2 Execution Plan

**Phase:** 0.2 (Stage 0 — Foundation, closing-out phase)
**Branch:** `phase-0.2-execution` (cut from `main` 2026-05-04 after
`phase-0.1-scoping` merged)
**Status:** Active.
**Companion:** `docs/phases/phase-0.2-plan.md` (the methodology
pre-registration, locked post-consolidation).

---

## Branch + persistence

- **Branch.** New branch `phase-0.2-execution` cut from `main` (now
  that `phase-0.1-scoping` is merged). All Phase 0.2 work happens on
  this branch; user merges manually per project ground rules. No
  force pushes.
- **Plan persistence.** This document is the project-tracked,
  versioned plan (vs scratch-located). Distinct from
  `phase-0.2-plan.md` (the methodology pre-registration) — this is
  the execution / work-ordering / gate-tracking companion.

## Context

Phase 0.2 pre-registration is locked (`docs/phases/phase-0.2-plan.md`,
post-consolidation). Phase 0.2 is now the **execution phase** that
runs the 7 Stage-1 prereqs from the pre-registration, validates them
against the Phase-0.2 → Stage-1 gates, holds a consolidation pass +
retro, and signs off on transition to Stage 1.

This is the *closing-out phase* of Stage 0. After it, Stage 1 begins
production-scale data work.

The pre-registration committed to 7 prereqs:
1. Qwen3 sorted-by-length batching benchmark
2. Stage 2 compute target decision (cloud vs local)
3. Genderize.io paid-tier API key procurement
4. NamSor account setup + small-batch test
5. §11 production-scale re-validation
6. 100-record ORCID-linkage validation
7. Production pull-spec dry run

This document orders them, defines work content per prereq, identifies
user-judgment moments, surfaces risks, and sets the gate for
transition.

---

## Order of operations

Three waves + one parallel track + close-out:

### Wave 1 — Quick code-and-setup (parallel-runnable)

**1A. Qwen3 sorted-by-length batching benchmark** [~3 hours]
- Implement length-sorted batching in `embed_qwen3` (sort abstracts
  by tokenized length, batch within length bands, rejoin in input
  order on output).
- Re-run the 50-abstract Phase 0.1.E smoke under three configs:
  (a) naive bs=8 (current baseline, 4.228 s/abs in smoke), (b)
  sorted bs=8, (c) sorted bs=32.
- Record per-abstract timing per config.
- Acceptance: best-strategy wall-clock recorded; sorted-batching PR
  (or in-place commit) merged.

**1B. NamSor account setup + small-batch test** [~1 hour]
- Sign up for NamSor; obtain API key; store in env (never committed).
- Test with 50-name batch covering 6 name regions × ~8 names each.
- Record per-region accuracy claims from NamSor's response metadata.
- Acceptance: API key in env; 50-name response cached for
  reproducibility; per-region accuracy table logged.

**1C. Production pull-spec dry run** [~1.5 hours]
- 10K-paper smoke pull from cs 2024 + cs 1980 (representative recent
  + representative pre-1990) using the **post-consolidation** §0
  filter pipeline:
  - score≥0.3 loose threshold
  - has_abstract
  - **post-2000-coined-only** junk-year token list (per consolidation §A)
  - **15-token** empty-abstract minimum (per consolidation §B)
- Acceptance: <2% over-filter rate vs the original Check 5a baseline
  on cs 1975 (verifying we didn't break the legitimate-paper set);
  zero post-2000-content-with-1970-year false negatives in a 50-row
  hand-audit.

These three can run in parallel on different days/sessions; they
share no compute and no data dependencies.

### Wave 2 — §11 production-scale re-validation [the big methodology gate]

**2A. §11 production-scale re-validation** [~4-6 hours]

This is the most substantial prereq. It re-runs Check 5d at 3-5× the
pilot scale to validate §11's stratification commitment.

Steps:
1. **Stratified pull** — 250 papers × 6 decades = 1500 post-filter
   papers, with **per-decade supplemental seed pulls** per the
   Check 5d lesson (early decades have lower retention; need 5-8
   sample calls per decade vs 1).
2. **Unstratified pull** — 1500 papers Nᵧ-proportional over the
   1970-2024 range.
3. **Held-out pulls** — 50 papers each from cs 1975, cs 2020 (not
   in either pool).
4. **SPECTER2 embedding** of all ~3100 papers (SPECTER2 only; no
   SciNCL/Qwen3 needed for §11).
5. **Cluster fit at K∈{30, 50, 100}** on stratified pool S vs
   unstratified pool U.
6. **H7 evaluation** — effN_S vs effN_U on H_1975 + H_2020 negative
   control.
7. **Cluster-fit manifest** — commit centroids + indices + fit
   hashes per §11's "artifacts to commit" mandate.

Pre-registered hypotheses (per `phase-0.2-plan.md` §11):
- H7' (production scale): effN_S(H_1975) > 1.43 × effN_U(H_1975)
  AND |effN_S(H_2020) - effN_U(H_2020)| / max(...) < 0.20
  (negative control passes).

Acceptance criteria:
- H7' passes at K=50 primary → §11 production-scale validated;
  proceed to Stage 1.
- H7' passes at K=30 or K=100 only → robustness sweep flag;
  document in artifact and proceed.
- H7' fails at all K → **block Stage 1 transition**; trigger plan
  revision per Phase 0.1 plan §"Gate failures" provision.

This is the load-bearing prereq. Can't run Wave 3 / Wave 4 cleanly
until this lands.

### Wave 3 — Parallel hand-work

**3A. 100-record ORCID-linkage validation** [~5 hours hand-work]

Runs in parallel with Wave 1 + Wave 2. Pure manual-validation work.

Steps:
1. Sample 100 ORCID-having authors from the existing pilot parquet,
   stratified by name region (16-17 per cell × 6 regions: Anglo,
   East-Asian, South-Asian, Arabic-speaking, Slavic, Other).
2. For each author: load `orcid.org/<id>`; check display-name match;
   check at least one institution match between OpenAlex
   `authorships.institutions[].display_name` and ORCID's employment
   history; check at least one publication in OpenAlex matches a
   publication on the ORCID profile.
3. Record per-record: linkage_correct (yes/likely/unclear/no), notes.
4. Aggregate: per-region linkage-correctness rate.

Acceptance criteria:
- 100 records validated; per-region rate computed.
- If overall correctness rate <70%, OpenAlex's ORCID linkage is
  unreliable for ws2 use; §9a P5 methodology re-opens for plan
  revision.
- If <50% on any name-region cell, that cell excluded from §9a P5
  ground-truth use; bias-uncertainty band's ORCID-only-quantified
  lower bound becomes per-region.

Can be done in 2-3 sittings of ~2 hours each. Compatible with other
work since it's pure manual.

### Wave 4 — Decisions + procurement (gated by Waves 1-3)

**4A. Stage 2 compute target decision (cloud vs local)** [user-judgment]

Inputs:
- Qwen3 sorted-batching result (Wave 1A): best-strategy s/abs.
- §11 production-scale embedding timing (Wave 2A): SPECTER2 actual
  s/abs at 3K-paper scale.
- Cloud cost estimate (Modal A10G default): $$ per full triple-pass
  at production N.
- Production-scale N target (open decision, gated by Check 5b
  N_target + Nᵧ): plausible range 500K-2M.

Decision: local M-series MPS vs cloud (Modal A10G default vs A100
upgrade).

Output: decision recorded in `tasks/spend.md` with pre-commit cost
estimate per ws2 desideratum §9 if cloud; recorded in retro either
way.

User-judgment moment: I'll surface the tradeoff numbers; user
decides.

**4B. Genderize.io paid-tier procurement** [conditional]

Only needed if production-scale Stage 1 exceeds 2500/mo (the
keyed-free tier).

- Production-scale unique-name count estimate: ~500K papers × ~3
  authors/paper × ~30% unique = ~450K unique names. Far exceeds
  2500/mo.
- Therefore: paid-tier procurement IS needed. Genderize plans:
  100K names → $9/mo; 1M names → $50/mo.
- Procurement: sign up; store key in env; pre-commit estimate in
  spend.md.

User decision needed: which Genderize plan tier (anything >$50
triggers ws2 desideratum §9 cost-gate pre-commit).

### Wave 5 — Phase 0.2 close-out

**5A. Phase 0.2 consolidation pass** [~2 hours]
- Per Phase 0.1 retro lesson #6: schedule the consolidation pass
  AHEAD of retro, not after.
- Review accumulated material: any new framing additions to
  phase-0.2-plan.md; any new lessons in lessons.md; any pending
  docs/conceptual.md updates.
- Compress where overlapping.
- Output: `experiments/phase-0.2/consolidation-notes.md` (new
  experiments dir for Phase 0.2).

**5B. Phase 0.2 retro** [~1.5 hours]
- `docs/phases/phase-0.2-retro.md` (backward-looking).
- Sections: what happened (the 7 prereqs + waves), surprises,
  lessons, validation gates check (signed off), what carries to
  Stage 1.

**5C. Phase 0.2 → Stage 1 transition signoff**
- User-signed-off on the pre-registration.
- All Phase 0.2 → Stage 1 gates (per `phase-0.2-plan.md` lines 770+)
  marked ✅ with evidence.
- `tasks/todo.md` updated to mark Stage 1 as active.
- `whitespace_2/CLAUDE.md` Current State updated to Stage 1.
- Stage 1 plan written (separate document, not part of Phase 0.2).

---

## Estimated runtime

| Wave | Items | Wall-clock | Cum. |
|---|---|---:|---:|
| 1 | Qwen3 benchmark + NamSor setup + pull-spec dry run | ~5 hrs | 5 |
| 2 | §11 production-scale re-validation | ~6 hrs | 11 |
| 3 | ORCID hand-validation (parallel) | ~5 hrs | (parallel; doesn't add) |
| 4 | Stage 2 compute decision + Genderize procurement | ~2 hrs | 13 |
| 5 | Consolidation + retro + signoff | ~4 hrs | 17 |
| **Total** | | **~17 hrs of focused work** | |

Roughly **1-2 calendar weeks at ~15 hrs/week**, matching the
phase-0.2-plan.md estimate. Could compress to ~1 week if Wave 3
runs fully in parallel with Waves 1-2.

---

## Risks and mitigations

| # | Risk | Mitigation |
|---|---|---|
| R1 | §11 H7' fails at all K — blocks Stage 1 transition | Pre-emptively prepare a plan-revision branch; document failure mode + alternative §11 spec (e.g., K=20 fit, decade-decoupled clustering); requires user judgment whether to re-attempt at higher \|S\| or revise §11 |
| R2 | ORCID linkage validation reveals widespread over-merge — §9a P5 contaminated for non-Western names | Document per-region rates; restrict §9a P5 to validated subsets; widen bias-uncertainty band on excluded cells |
| R3 | Stage 2 compute target ambiguous — neither cloud nor local clearly dominates | Surface decision matrix to user with explicit cost+time tradeoffs at multiple production N |
| R4 | Genderize paid-tier needs >$50 → triggers ws2 desideratum §9 cost-gate | Pre-commit estimate in `tasks/spend.md` BEFORE procurement; user signoff required |
| R5 | Pull-spec dry run reveals new false-positive class in junk-year token list | Iterate token list; consider per-token false-positive audit on hand sample of ~50 pre-1990 papers from each token's match set |
| R6 | Qwen3 sorted-batching doesn't help meaningfully (e.g., <30% speedup) | Stage 2 compute decision tilts further toward cloud; not a Phase 0.2 blocker |

---

## Phase 0.2 → Stage 1 validation gates

From `phase-0.2-plan.md` lines 770+:

| # | Gate | Acceptance evidence |
|---|---|---|
| 1 | Pre-registration finalized + user-signed-off | this plan + pre-reg approved by user |
| 2 | Qwen3 sorted-batching benchmark complete | Wave 1A artifact + best-strategy timing in lessons.md |
| 3 | Stage 2 compute target decided | Wave 4A user-decision recorded in retro + spend.md |
| 4 | §11 production-scale re-validation result documented | Wave 2A artifact in `experiments/phase-0.2/`; H7' outcome recorded; cluster-fit manifest committed |
| 5 | 100-record ORCID-linkage validation result documented | Wave 3A artifact + per-region rate table |
| 6 | All Phase 0.2 commitments cross-link to source | Done in pre-reg already |
| 7 | Spend pre-commit estimates logged for any Stage 1 spend ≥$50 | Wave 4 outputs |
| 8 | `tasks/todo.md` updated to Stage 1 active | Wave 5C |
| 9 | `whitespace_2/CLAUDE.md` Current State = Stage 1 | Wave 5C |

---

## Critical files to create

- `docs/phases/phase-0.2-execution.md` (this plan, persisted to project)
- `experiments/phase-0.2/qwen3-batching-benchmark.md` (Wave 1A)
- `experiments/phase-0.2/namsor-smoke.md` (Wave 1B)
- `experiments/phase-0.2/pull-spec-dry-run.md` (Wave 1C)
- `experiments/phase-0.2/section11-production-validation.md` (Wave 2A)
- `experiments/phase-0.2/section11-production-validation.py` (script)
- `experiments/phase-0.2/orcid-linkage-validation.md` (Wave 3A)
- `experiments/phase-0.2/orcid-linkage-validation.csv` (per-record audit)
- `data/metadata/cluster-fit-manifest-production.{md,npy}` (Wave 2A artifact)
- `experiments/phase-0.2/consolidation-notes.md` (Wave 5A)
- `docs/phases/phase-0.2-retro.md` (Wave 5B)

To edit:
- `tasks/todo.md` (Stage 1 transition)
- `whitespace_2/CLAUDE.md` (Current State → Stage 1)
- `tasks/spend.md` (pre-commit estimates for Wave 4)

---

## What this plan is NOT

- **Not the pre-registration.** That's `phase-0.2-plan.md` (locked
  post-consolidation).
- **Not Stage 1's plan.** Stage 1 plan is a separate document
  written after Wave 5C transition signoff.
- **Not new methodology.** All methodology is locked in the pre-reg.

---

## User-judgment decisions surfaced

1. **Stage 2 compute target** (Wave 4A): cloud vs local at expected
   production-scale N. I'll prepare the decision matrix with cost +
   wall-clock numbers.
2. **Genderize paid-tier plan** (Wave 4B): which plan ($9 / $50 /
   $200 / etc.) — depends on production-scale unique-name count
   estimate.
3. **§11 H7' failure response** (R1, conditional): if production-
   scale validation fails, do we re-attempt at higher \|S\| or
   revise §11 commitment?
4. **ORCID validation outcome interpretation** (R2, conditional):
   if rates are mixed across regions, where to draw the per-region
   exclusion threshold?

These are flagged for user review at the relevant Wave.

---

## Verification

End-of-phase checks:

```bash
cd whitespace_2
# All Phase 0.2 artifacts present
ls -la experiments/phase-0.2/
# §11 production-scale validation passed
grep -A 3 "validates_section_11" experiments/phase-0.2/section11-production-validation.md
# Cluster-fit manifest committed
ls -la data/metadata/cluster-fit-manifest-production*
# Spend pre-commits recorded
grep -E "Stage 2 compute|Genderize.*paid" tasks/spend.md
# Phase 0.2 retro present
cat docs/phases/phase-0.2-retro.md | head
```

Linting/typechecking applies if §11 validation has new code:
`uv run ruff check experiments/phase-0.2/`,
`uv run mypy experiments/phase-0.2/`.

---

## Pre-flight choices already locked

- Order of operations (Wave 1 quick parallel; Wave 2 §11 big gate;
  Wave 3 ORCID parallel; Wave 4 decisions; Wave 5 close-out).
- Consolidation pass scheduled BEFORE retro (per Phase 0.1 retro
  lesson #6).
- Phase 0.2 retro is its own document
  (`docs/phases/phase-0.2-retro.md`).
- Genderize paid tier IS needed (production-scale exceeds 2500/mo);
  question is which plan, not whether.
