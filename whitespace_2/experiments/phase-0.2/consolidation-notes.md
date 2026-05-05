# Phase 0.2 Consolidation Pass

**Phase:** 0.2 (Stage 0 — Foundation, closing-out phase)
**Consolidation date:** 2026-05-05
**Gate:** phase-0.1-retro lesson #6 — schedule consolidation pass
AHEAD of retro, not after.

This document is the gate-10 evidence for Phase 0.2.

---

## Why this pass exists

Phase 0.1's retro lesson #6 surfaced that consolidation is its
own work-item, not implicit in retro-writing. Phase 0.2 honors
that lesson: this consolidation runs BEFORE the retro, with the
goal of identifying what got accumulated through the 7 waves
that needs pruning, compressing, or amending.

Unlike Phase 0.1, Phase 0.2's accumulation was relatively
disciplined — most session amendments were committed in real
time (e.g., the §11 threshold amendment landed as part of the
projection-bug-fix commit, not as a deferred edit). The
consolidation surface is therefore smaller than Phase 0.1's.

---

## What was reviewed

| Artifact | Lines | Status |
|---|---:|---|
| `docs/phases/phase-0.2-plan.md` | 951 | reviewed; amendments identified |
| `docs/phases/phase-0.2-execution.md` | 370 | reviewed; status updates |
| `docs/phases/phase-0.2-scincl-primary-contingency.md` | 298 | reviewed; status note |
| 14 `experiments/phase-0.2/*.md` artifacts | various | reviewed; current |
| `tasks/lessons.md` | accumulated | reviewed; locked |
| `tasks/spend.md` | populated | reviewed; current |

---

## Pruning / compression decisions

### A. Plan §"Stage 1 prereqs" — RENAMING [APPLIED]

**Issue.** Lines 824-853 list "Stage 1 prereqs" as 7 items.
These were intended as work-to-do BEFORE Stage 1 begins. Through
the session, all 7 became Phase 0.2 work waves (1A, 1B, 1C, 2A,
3A, 4A, 4B). Calling them "Stage 1 prereqs" is now historical
naming. **All 7 are complete inside Phase 0.2.**

**Decision.** Leave the section title for backward-compat with
external references (`phase-0.1-retro.md` pointed users to "Stage
1 prereqs"). Add a status pass marking each ✅ with the wave that
resolved it. Phase 0.2 retro explicitly notes the wave→prereq map.

### B. Plan §11 — methodology revision is consolidated [VERIFIED CLEAN]

**Issue.** §11 went through two empirical revisions during the
session:
1. Original H7' threshold: 1.43 (set as planning prior in Phase
   0.1 plan).
2. Wave 2A first run: appeared to fail at all K (BUGGY projection).
3. Mid-session: drafted a §11 deprecation amendment in plan
   (would have switched to Path C "drop §11 commitment"). NEVER
   COMMITTED.
4. User audit prompt → projection-bug fix → §11 threshold revised
   to 1.10 (committed `6c99ae5`).
5. SciNCL re-validation confirmed 1.10 holds (committed `c074446`).

**Verification.** Plan §11 currently reflects the THRESHOLD-1.10
amendment with empirical evidence + projection-bug methodology
lesson. The deprecation draft was reverted before commit.
`git checkout` of plan §11 confirms current state is correct.

**Decision.** No change needed. Verified clean.

### C. SciNCL contingency doc — STATUS UPDATE NEEDED [APPLIED IN RETRO]

**Issue.** `docs/phases/phase-0.2-scincl-primary-contingency.md`
was authored as a what-if before Wave 4A locked Reading B. After
Reading B locked + SciNCL revalidation passed, the contingency's
"what would we do" section became reality. The doc was already
amended with a "Status update: Wave 4A LOCKED" section after
Reading B was chosen, but not after the SciNCL revalidation passed.

**Decision.** Add a follow-up status note to the contingency doc:
"SciNCL revalidation 2026-05-04 passed at 3/3 K with relaxed
threshold; the SciNCL→SPECTER2 fallback contingency stays 'never
triggered' as of Phase 0.2 close." Light-touch amendment;
contingency triggers remain in place for Stage 1 dry-run.

### D. Execution plan §"Open after Wave 4A commit" — RESOLVE [APPLIED]

**Issue.** `docs/phases/phase-0.2-execution.md` line section
listing "Open after Wave 4A commit" includes items that were
resolved during this session: real per-abstract A100 cost
(deferred to Stage 1 dry-run, not open), preemption rate
(deferred similarly), Stage 1 plan as a whole (still open;
correctly noted).

**Decision.** Keep the section as Stage 1 setup blockers.
"Real per-abstract A100 cost" and "preemption rate" remain
unresolved until Stage 1 dry-run runs; that's correct framing.

### E. Plan §"Validation gates" table — UPDATE STATUSES [APPLIED IN RETRO]

**Issue.** Table at lines 877-887 has all gates marked Pending.
After Phase 0.2 work, all 9 gates are met (gates 1-9 all
✅ at Wave 5C signoff).

**Decision.** Update the table in the retro doc, NOT in the plan
doc, since the plan is the pre-registration (frozen at
methodology lock) and the retro is the backward-looking phase
artifact.

### F. Lit-review Synthesis Pointers — DEFER TO STAGE 3 [NO ACTION NOW]

**Issue.** Same as Phase 0.1 consolidation §I. Per-paper
Pointers in literature-review/*.md remain the source of truth.
Stage 3 paper-drafting harvests them in a single per-Methods-
section pass.

**Decision.** No action now. Mirrors Phase 0.1 lesson.

### G. Workflow doc retention — KEEP [APPLIED]

**Issue.** `experiments/phase-0.2/orcid-linkage-audit-workflow.md`
was written as a printable user-facing companion. Now that the
audit is done, is it still needed?

**Decision.** Keep. Documents the methodology choice (Reading B)
and decision rule that produced the final §4 result. Reviewers
asking "how did you decide which records counted as correct?"
can read the workflow doc + the per-row `notes` column in
`orcid-linkage-audit-input.csv`.

---

## What survived without prune

The substantial majority of Phase 0.2 accumulated material
survives the consolidation pass clean. Specifically:

- **§0 analytical population definition** — model-independent;
  unchanged from post-Phase-0.1-consolidation lock.
- **Word-boundary regex matching** (Wave 1C amendment) — locked
  in plan §0.
- **§1 model stack** — Reading B locked + SciNCL primary
  empirically validated.
- **§4 ORCID-linkage threshold + validation** — passed at 98.6%.
- **§9e propensity-corrected aggregates** — locked.
- **§11 cluster-fit stratification** + threshold 1.10 + SciNCL
  primary lock + projection-bug methodology lesson — locked.
- **Per-metric N_target from Check 5b** — unchanged.
- **Test I/II/III/IV pre-registrations** — unchanged.
- **All 7 wave artifacts + methodology amendments** — current
  and consistent.
- **Pre-commit estimates in `tasks/spend.md`** — populated
  per §9 desideratum.
- **SciNCL→SPECTER2 fallback contingency** — preserved with
  trigger conditions for Stage 1 dry-run.

Phase 0.2 was a methodology-rich phase: 20+ commits across 7
waves, 3 methodology bugs caught and fixed mid-session, 2
significant methodology revisions (Reading B model stack, §11
threshold). Despite the volume, the accumulated material is
internally consistent because amendments landed in real time.

---

## Methodological lesson logged

**Real-time amendments beat deferred consolidation.** Phase 0.1
accumulated material across the phase and consolidated at the
end (with one substantial round of edits). Phase 0.2 amended in
real time as bugs surfaced + decisions locked. The Phase 0.2
consolidation surface is much smaller as a result.

This is a planning lesson: **gate-10 consolidation is lighter
when methodology amendments land per-commit during the phase**,
not at the end. For future phases, prefer the in-commit
amendment pattern over the accumulate-then-consolidate pattern.
The retro discipline is independent: retros are backward-looking
no matter how clean the consolidation.

Logged as Phase 0.2 lesson in `tasks/lessons.md`.

---

## Verification

```bash
cd whitespace_2

# A: Stage 1 prereqs all complete
grep -c "Wave 1A\|Wave 1B\|Wave 1C\|Wave 2A\|Wave 3A\|Wave 4A\|Wave 4B" \
  docs/phases/phase-0.2-retro.md

# B: §11 threshold currently locked at 1.10
grep "1\.10" docs/phases/phase-0.2-plan.md | head -3

# C: SciNCL contingency doc has status note
grep "Status update.*Wave 4A LOCKED" \
  docs/phases/phase-0.2-scincl-primary-contingency.md

# E: Validation gates table currently shows pending in plan
# (intentional — plan is the pre-reg; retro updates the gates)
grep -A 9 "## Validation gates" docs/phases/phase-0.2-plan.md

# G: Workflow doc retained
ls experiments/phase-0.2/orcid-linkage-audit-workflow.md

# Lessons file updated
tail -1 tasks/lessons.md
```

All checks should pass after the retro + signoff commit.
