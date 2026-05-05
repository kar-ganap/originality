# Phase 0.2 — SciNCL-as-primary contingency plan (NOT YET TRIGGERED)

**Status:** What-if. NOT a commitment to switch. Documents what we
would do if we needed to pull the trigger.

**Created:** 2026-05-04
**Trigger gate:** see "When to pull the trigger" below.

---

## Why this document exists

Phase 0.1 Check 5c surfaced an empirical signal that SciNCL is
**materially more drift-robust** than SPECTER2 on our 1970-2024
corpus (era-match rate 75.4% vs 62.8% on 1970-1980 query papers).
SPECTER2 is the standard / well-maintained / benchmark-favored
model; SciNCL is the drift-optimal one for our specific use case.

The locked stack is SPECTER2 (primary) + SciNCL (cross-check) +
Qwen3 (cross-family). But "primary" is a methodology choice
that affects:

- §11 cluster fit (centroids are SPECTER2-derived)
- Headline metric reporting (which model's metric is the headline?)
- Reviewer-facing defense (which model's drift profile do we own?)

If at Stage 1/2/3 we discover SPECTER2's drift cost is too high to
defend, switching primary to SciNCL is the contingency. This
document plans that switch upfront so the cost is bounded and the
trigger conditions are pre-specified.

---

## When to pull the trigger

Switch SciNCL → primary if ANY of the following:

1. **Stage 2 production-scale Flavor A diagnostic shows SPECTER2's
   drift is worse than the Phase 0.1 Check 5c pilot suggested.**
   Specifically, if Flavor A correction reveals >5pp of the headline
   divergence is drift-attributable on SPECTER2 vs <2pp on SciNCL.

2. **Reviewer pushback in early manuscript circulation explicitly
   raises drift on SPECTER2.** If the methodology defense becomes
   "we used the more drift-prone model because it's more
   benchmark-standard," switch.

3. **Cross-family agreement is high between SciNCL and Qwen3 but
   low between SPECTER2 and either.** This would suggest SPECTER2
   is the outlier in the three-model stack.

4. **Cost-driven — drop SPECTER2 from headline stack.** If budget
   forces dropping one of the encoder models AND we drop SPECTER2,
   SciNCL becomes the de-facto headline encoder. This is the
   "Wave 4A budget reality + SciNCL is drift-optimal" composite
   trigger.

Trigger 4 is the most realistic given current §9 budget pressure.

---

## Concrete work items

### Code changes

- [ ] `src/whitespace2/embeddings.py`: no code changes needed —
      both models are already in the embedding pipeline. Just a
      configuration switch in the Stage 2 driver.

- [ ] `experiments/phase-0.2/section11_production_validation.py`:
      change `embed_specter2` calls to `embed_scincl`. Update H2
      norm band assertion (SPECTER2: [21.0, 23.0]; need to
      empirically establish SciNCL's band — likely similar but
      validate from Phase 0.1.E smoke).

- [ ] `experiments/phase-0.2/section11_followup_bigger_heldouts.py`:
      same swap.

- [ ] `tests/test_embeddings.py`: ensure SciNCL's slow tests are
      green; add equivalent norm-band assertion test for SciNCL
      if not already present.

### Data re-embedding

Existing artifacts that need SciNCL versions:

- [ ] `data/metadata/section11-prod-{S,U,H_1975,H_2020}-vec.npy`
      — 4 files; ~3100 papers total. Re-embed with SciNCL.
- [ ] `data/metadata/section11-prod-{H_1975,H_2020}-vec-followup.npy`
      — 2 files; 400 papers total.
- [ ] `data/metadata/section11-cluster-fit-{S,U}-K{30,50,100}.npy`
      — 6 centroid files; re-fit on SciNCL embeddings.

Compute estimate: ~3500 papers × ~0.4 s/abs (SciNCL on M-series MPS)
= ~25 min wall-clock locally. Cluster re-fit on K∈{30, 50, 100}:
~5-10 min. **Total: ~30-40 min.**

Re-running the §11 followup with bigger held-outs on SciNCL
embeddings (to verify the H7' empirical magnitude with the new
primary): ~5 min.

### Plan/doc updates

- [ ] `docs/phases/phase-0.2-plan.md` §1: rewrite "primary" model
      from SPECTER2 to SciNCL. Document the trigger that fired
      (link to evidence). Keep SPECTER2 in the stack as the
      cross-check / robustness model.

- [ ] `docs/phases/phase-0.2-plan.md` §11: re-record empirical
      H7' magnitudes with SciNCL primary. Update threshold if
      magnitudes differ materially (current SPECTER2-derived
      threshold is 1.10; SciNCL may give different magnitudes).

- [ ] `experiments/phase-0.2/section11-production-validation.md`:
      add post-switch update section documenting the SciNCL
      re-fit + new H7' results. Keep SPECTER2 results below as
      audit trail (same pattern as the projection-bug fix).

- [ ] `experiments/phase-0.2/stage2-compute-decision.md`: update
      per-model timing (SciNCL ≈ SPECTER2 for compute purposes;
      no major change).

- [ ] `tasks/lessons.md`: log "SPECTER2 → SciNCL primary switch
      driven by [trigger]" with rationale.

### Cluster-fit manifest

- [ ] Re-write `data/metadata/cluster-fit-manifest.md` with
      SciNCL-derived centroids. Reference the SPECTER2 manifest
      as the prior baseline.

### What stays the same

- §0 analytical population (model-independent)
- Pull-spec word-boundary regex (model-independent)
- §9 demographic-uncertainty stack (model-independent)
- Test I/II/III/IV pre-registrations (model-agnostic; just swap
  the embedding source)
- Per-metric N_target from Check 5b (model-independent)
- Stage 2 compute target (~$300-500 for 3 headline runs at 1M)
- Wave 1B NamSor smoke results (orthogonal)
- Wave 1C pull-spec dry run (orthogonal)
- Wave 3A ORCID linkage prep (orthogonal)

### What stays the same on a SPECTER2 → SciNCL switch

| Layer | Affected? |
|---|---|
| Pull spec | No (model-independent) |
| Pre-registered tests | No (model-agnostic) |
| Demographic pipeline | No (orthogonal) |
| §11 cluster fit | YES — re-fit |
| §11 H7' threshold | Maybe — re-validate |
| Phase 0.1.E pipeline norm-band test | YES — generalize |
| Plan doc references to "SPECTER2 primary" | YES — rewrite |
| Cluster-fit manifest | YES — regenerate |
| Stage 2 compute target | No (timing similar) |
| Wave 4A cost matrix | No (cost similar) |

---

## Effort estimate

| Item | Wall-clock |
|---|---:|
| Code swaps (script edits) | ~30 min |
| Test updates | ~15 min |
| Re-embed + re-fit (§11 production) | ~40 min |
| Plan doc rewrites (§1, §11) | ~30 min |
| Artifact md updates | ~30 min |
| Cluster-fit manifest regen | ~15 min |
| Lessons log + audit-trail commits | ~15 min |
| **Total** | **~3 hours** |

Compute cost: ~negligible if done locally (SciNCL ~0.4 s/abs on
MPS for ~3500 papers + cluster re-fit). If we want production-
scale re-validation at 1M (cloud A100), that's ~$80-160 — same
as one normal Stage 2 pass.

---

## Status update: Wave 4A LOCKED + EMPIRICALLY VALIDATED (2026-05-05)

This contingency was authored as a what-if. **Wave 4A locked
Reading B (SciNCL primary + Qwen3 cross-family, drop SPECTER2 from
headline) on 2026-05-04 — purely on the Phase 0.1 Check 5c drift
data, not budget pressure.** SPECTER2 retained in pipeline as
fallback + Stage 3 robustness swap. The work-items section above
becomes the actual Stage 1 first-day plan rather than contingency.

**SciNCL revalidation 2026-05-04 (commit `c074446`) PASSED at all
3 K** with relaxed threshold (r_H75 ∈ [1.17, 1.33]) AND at K=30
with strict threshold (r_H75 = 1.44 ≥ 1.43). NC passes cleanly at
all K. SciNCL is empirically at least as strong as SPECTER2 on §11.

**As of Phase 0.2 close, SciNCL→SPECTER2 fallback contingency
status: NEVER TRIGGERED.** Trigger conditions remain in place for
Stage 1 dry-run (and are bounded-cost reversible if any fire).

The fallback direction (SciNCL → SPECTER2) is now the contingency.
Trigger conditions for the FALLBACK direction below.

---

## Fallback contingency: SciNCL has its own issues → add SPECTER2 back

Symmetric to the SPECTER2 → SciNCL primary swap. Triggers if any
of the following surface during Stage 1 / Stage 2:

1. **SciNCL shows its OWN drift artifact at production scale.**
   E.g., systematic cluster-geometry differences across decades that
   weren't visible in the Phase 0.1 Check 5c pilot (1000-paper era
   pool). At Stage 1 production scale (1M papers), some pattern
   emerges that Check 5c missed.

2. **Cross-family agreement (SciNCL vs Qwen3) is unexpectedly low.**
   If SciNCL and Qwen3 disagree on >30% of paper similarity rankings
   at production scale, the cross-family check fails. Adding SPECTER2
   back gives a third vote.

3. **§11 H7' fails on SciNCL embeddings.** When we re-fit cluster
   centroids with SciNCL primary (per the work-items section above),
   if H7' still fails at all K with the projection-bug-fixed
   Euclidean assignment — DIFFERENT from the SPECTER2 result — then
   the issue is SciNCL-specific not bug-specific. Re-evaluate.

4. **Stage 1 dry-run shows SciNCL has anomalous production-scale
   behavior.** E.g., norm bands different from Phase 0.1.E smoke,
   slower than estimated, or unstable across batches. Dry-run is the
   first chance to catch SciNCL-specific quirks.

Fallback action if ANY of the above fires:

- **Re-add SPECTER2 to the headline stack** (back to Reading A's
  three-model triple-pass).
- **Re-fit §11 cluster centroids with SPECTER2** (already have
  these committed; just relabel as primary in plan §1).
- **Update plan §1 + §11 + cluster-fit manifest** to reflect
  three-model SciNCL+SPECTER2+Qwen3 stack with SciNCL still
  reported as headline if it still passes its own validation.
- **Pre-commit additional ~$75-150 spend** in `tasks/spend.md`
  for the SPECTER2 production runs.
- **Document the trigger that fired + the fallback action** in
  `tasks/lessons.md`.

Total fallback effort: ~3 hours code/doc work + ~$75-150 cloud
spend (less if local re-embedding is feasible at scale).

The Stage 1 dry-run is the FIRST gate where these triggers can
fire. Verifying SciNCL's production-scale behavior on the 50K
sample is therefore load-bearing — don't skip it.

---

## Reversal plan (if SciNCL primary turns out to be worse)

If after switching to SciNCL primary the Stage 1 production
analysis reveals SciNCL has its own quirks (e.g., systematically
different cluster geometry than expected, or lower agreement with
Qwen3 than SPECTER2 had), switching back is symmetric:

- Re-embed §11 pools with SPECTER2 (already have the centroids
  committed; just regenerate vectors)
- Re-fit cluster centroids
- Roll back plan-doc changes via git
- Document the SciNCL→SPECTER2 reversal in lessons

Reversal effort: ~3 hours, same as forward switch. Nothing is
lost permanently because all SPECTER2 artifacts remain in git
history.

---

## Things this contingency does NOT cover

- **Switching to a non-locked model** (e.g., text-embedding-3-large,
  bge-large-en-v1.5). That's a separate plan revision.
- **Dropping SciNCL from the stack entirely.** The Wave 4A
  conversation noted this as a budget option. If we drop SciNCL
  AND keep SPECTER2 as primary, no contingency triggers. If we
  drop SPECTER2 AND keep SciNCL as primary, this contingency IS
  the triggered plan.
- **Multi-encoder ensembling** (e.g., averaged embeddings). Not in
  scope; would require its own pre-registration.

---

## Decision authority

User-judgment moment. The trigger conditions above pre-specify
when ws2's methodology should switch primary; the actual switch
requires explicit user signoff because it's a methodology
revision after pre-registration.

If pulled, the switch should be commit-tagged
`phase-0.2-primary-scincl-switch` for clean audit trail.

---

## Cross-references

- Check 5c drift pilot: `experiments/phase-0.1/drift-pilot-results.md`
- §11 production validation (with projection-bug fix):
  `experiments/phase-0.2/section11-production-validation.md`
- Wave 4A compute decision: `experiments/phase-0.2/stage2-compute-decision.md`
- Phase 0.1.E embedding pipeline scaffold: `src/whitespace2/embeddings.py`
- Phase 0.1.E smoke artifact: `experiments/phase-0.1/embedding-pipeline-smoke.md`
