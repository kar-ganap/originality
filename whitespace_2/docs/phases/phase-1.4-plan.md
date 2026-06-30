# Phase 1.4 Plan — Pre-Stage-2 quality gates + 100K divergence smoke + transition signoff

**Stage:** 1 — Crawl
**Phase:** 1.4 — fourth (final) phase of Stage 1
**Window opens:** 2026-06-30
**Branch:** `phase-1.4-execution` (cut from `main` post-Phase-1.3 merge, PR #9)
**Status:** Plan locked. TEST → IMPLEMENT → VERIFY → RETRO discipline.

---

## Stage 1 (Crawl) — overview

| Phase | One-line scope | Status |
|---|---|---|
| 1.1 | Compute substrate + 50K dry-run | ✅ COMPLETE |
| 1.2 | Production §0 pull → v3 corpus (24.5M) | ✅ COMPLETE |
| 1.3 | Author disambiguation + demographic inference | ✅ COMPLETE |
| **1.4** | **Pre-Stage-2 quality gates + 100K divergence smoke + signoff** | **CURRENT — this plan** |

---

## One-line scope

Validate the Stage-1 demographic substrate at production scale, lift the
semantic + canonical diversity metrics into `src/`, run a 100K end-to-end
mini-Stage-2 pilot (embed → semantic metrics → divergence test), pre-register
the divergence test in the Stage 2 plan (desideratum §5), and sign off the
Stage 1 → Stage 2 transition.

This is the **go/no-go gate before Stage 2's embedding spend** (~$77 measured).

---

## Why this phase exists

Stage 2 is an expensive, hard-to-reverse commitment (full-corpus embedding +
the headline divergence test). Phase 1.4 is the checkpoint that (a) proves the
Stage-1 output is sound at production scale (analog of Phase 0.1 Checks 1+2),
(b) locks the headline divergence test *before* any full-data run per
desideratum §5, and (c) — per the user-chosen thorough scope — runs a 100K
end-to-end pilot to de-risk the full spend and confirm the whole pipeline
composes. Phase 1.3 left three concrete carry-forwards this phase resolves:
the pre-1970 mis-dated corpus tail (year-bound), the physics ≥ CS early-female
finding (scrutiny), and per-cell H7 (the Phase-1.3 driver reported per-region).

---

## Pre-flight choices already locked (carryover)

- **Embedding stack:** SciNCL (primary) + Qwen3 (cross-family), 768-dim, on
  Modal A100 preemptible. `src/whitespace2/embeddings.py` +
  `experiments/phase-1.1/embed_modal.py` (`ws2-embed`) +
  `src/whitespace2/resumable_runner.py`. Cost $0.0000191/abs (Phase 1.1).
- **Semantic metric stack (§8 + plan-at-a-glance §5):** effective
  dimensionality (primary B), mean pairwise cosine distance (secondary),
  cluster entropy (primary A, §11 temporally-stratified). Currently only in
  `experiments/phase-0.1/check5bd_convergence_stratification.py`.
- **Divergence test (phase-0.2-plan.md "Test I"):** OLS of (semantic /
  demographic plurality) ratio on year, negative slope p<0.05 two-tailed across
  both semantic metrics + directional 3rd; canonical concentration as the
  negative control. To be consolidated into `phase-2.0-plan.md` per §5.
- **Stage 2 N:** 1M headline + 500K robustness (Wave 4A lock).
- **Demographic substrate:** `data/metadata/v3-coverage-table.parquet` (630
  cells × 2 units; gender Shannon + female_share + country Shannon + coverage),
  the reusable bias kernel, v2 robustness pair.

---

## Workstreams

### A. Production-scale sanity gates

- **A1 — Year-bound 1970–2024.** Add a year-window filter downstream of the 1M
  sample + report the pre-1970/post-2024 dropped count. (`section0_filter.py`
  has no `publication_year` bound — confirmed; it screened junk-year *tokens*.)
  Apply uniformly; note for a future §0/sampling amendment.
- **A2 — Field-intuition checks** (Phase 0.1 Checks 1+2 analog at scale): CS /
  physics paper + author volume curves over time; demographic distributions vs
  known facts (female-share trajectory plausible; China's CS country-share rise
  post-2010); **diagnose the physics ≥ CS early-female finding** (real subfield
  effect vs name-inference artifact).
- **A3 — gender × country coverage cross-tab** per cell + **per-cell H7**
  (NamSor sample ≥ 10 in each headline year×field×region cell).
- **A4 — Disambiguation production spot-check** (career-length distribution at
  1.82M-author scale + small manual sample; Phase 0.1 Check 4 analog).
- Output: `experiments/phase-1.4/sanity-checks.md`.

### B. Divergence-test pre-registration (desideratum §5)

- Author `docs/phases/phase-2.0-plan.md` (Stage 2 plan) with the **locked
  divergence test** — consolidating Test I and reconciling with the *realized*
  Phase-1.3 demographic metrics. Lock: metric, estimator, field (CS primary +
  Physics robustness per §6), window (1970–2024), null (both rise = successful
  null), threshold (p<0.05 two-tailed), negative control (canonical rises).
- **Resolve the prestige gap:** Test I's demographic plurality was "gender ×
  country × prestige joint Shannon + Rao Q"; Phase 1.3 built gender + country,
  **not prestige**. Decide: drop prestige from the headline, or add it as a
  Stage 2 demographic variable.
- **§8 second demographic metric:** Phase 1.3 has Shannon + the directional
  female_share; consider adding a Blau/Simpson index for a clean ≥2.

### C. 100K end-to-end mini-Stage-2 smoke

- **C1 — Lift semantic + canonical metrics into `src/`** (TDD): port
  `effective_dimensionality`, `mean_pairwise_cosine_distance`, `cluster_entropy`
  (+ shared MM-Shannon) from `check5bd_…` → `src/whitespace2/semantic_metrics.py`;
  citation Gini + top-k share → `src/whitespace2/canonical_metrics.py`. Verify
  against Phase 0.1 values on a shared input.
- **C2 — Divergence estimator** (`src/whitespace2/divergence.py`, TDD): the
  Test-I OLS-of-ratio-on-year, on synthetic series.
- **C3 — Embed 100K** v3 abstracts on Modal: reuse `ws2-embed` +
  `ChunkedEmbedRunner` via `experiments/phase-1.4/smoke_100k.py`. Subset = the
  hash-ordered first 100K of `section0-sample-1M-v3.parquet` (the 1M file is
  already local in the scratchpad). ~$4 (log in `spend.md`).
- **C4 — Run the 3 axes + the divergence test on the pilot** (labeled
  **exploratory** per §5): demographic (Phase-1.3 coverage on the 100K),
  semantic (lifted metrics, §11-stratified), canonical (Gini) → `divergence.py`
  → sanity-check the slope + the negative control. De-risks: pipeline composes,
  per-cell semantic metrics stable at 100K, slope computable. Output:
  `experiments/phase-1.4/smoke-100k-results.md`.

### D. Stage 1 → Stage 2 transition signoff

Confirm all 7 transition deliverables; author `docs/phases/phase-1.4-retro.md`;
close Stage 1.

---

## Pre-registered acceptance gates

| # | Gate | Acceptance |
|---|---|---|
| 1 | Year-bound applied | pre-1970/post-2024 dropped + counted; headline unchanged within CI |
| 2 | Field-intuition checks pass | volume curves + demographic distributions match known facts; physics≥CS diagnosed |
| 3 | Per-cell H7 | headline cells have ≥10 NamSor names (or flagged) |
| 4 | Semantic + canonical metrics lifted to `src/` | with tests; match Phase 0.1 on a shared input |
| 5 | Divergence estimator implemented | Test-I OLS, tested on synthetic series |
| 6 | 100K embed clean | norms in band (SciNCL [22.5,24.5], Qwen3 ≈1.0), finite, ~$4, resumable |
| 7 | Pilot divergence computable | slope + p-value produced; negative control (canonical) rises |
| 8 | Divergence test pre-registered | `phase-2.0-plan.md` with metric/estimator/field/window/null/threshold locked |
| 9 | All tests pass + lint/typecheck clean | |
| 10 | Retro + transition signoff committed | |

ANY field-intuition failure or broken pilot pipeline → STOP, surface, replan.

---

## IMPLEMENT order

1. **A** sanity gates (local; year-bound + field intuitions + per-cell H7 +
   disambiguation).
2. **C1** lift semantic + canonical metrics into `src/` (TDD) — reusable Stage-2
   code.
3. **C2** divergence estimator in `src/` (TDD).
4. **C3** embed 100K on Modal.
5. **C4** run the pilot divergence end-to-end (exploratory writeup).
6. **B** pre-registration → `phase-2.0-plan.md`.
7. **D** retro + signoff.

A + C1/C2 are the high-leverage early wins (sanity + reusable metric code).
Commit per workstream.

---

## VERIFY plan

- `make lint typecheck && uv run pytest tests/` green (new metric + divergence
  tests; expect ~185+ total).
- Semantic-metric port verified against Phase 0.1 values on a shared vector set.
- 100K embed: norm-band + finiteness checks (per `embed_modal.py`);
  resumability validated by interrupt + restart on a chunk.
- Pilot divergence: OLS slope + p-value printed; canonical negative control
  rises; labeled **exploratory** (headline is the full 1M Stage-2 run).

---

## Risks + mitigations

| # | Risk | Mitigation |
|---|---|---|
| R1 | Semantic-metric port drifts from Phase 0.1 | verify against committed Phase 0.1 values on a shared input |
| R2 | 100K embed OOM / preemption | A100 + `ChunkedEmbedRunner` resume (Phase 1.1 contract); chunk_size 1000 |
| R3 | Per-cell semantic metrics noisy at 100K | §11 temporal stratification; report cell-size sensitivity (analog of H8) |
| R4 | Pilot divergence misread as the headline | label exploratory; the pre-registered headline is the full 1M run |
| R5 | Prestige gap blocks pre-registration | decide drop-vs-add in B; pre-register the realized definition |

---

## Cost estimate

| Item | Cost | Notes |
|---|---|---|
| Sanity gates + metric lifts | $0 | local |
| 100K embed (SciNCL + Qwen3) | ~$4 | $0.0000191/abs × 100K × 2; under §9 $50 gate; logged in spend.md |
| **Total** | **~$4** | Running total ~$37 |

---

## Companion documents

- Approved plan (this phase): `docs/phases/phase-1.4-plan.md`
- Phase 1.3 retro + carry-forwards: `docs/phases/phase-1.3-retro.md`
- Divergence-test source spec: `docs/phases/phase-0.2-plan.md` "Test I"
- Desiderata §5 (pre-registration), §6 (field robustness), §8 (metric
  plurality), §9 (cost gate), §11 (cluster-fit stratification): `docs/desiderata.md`
- Stage 2 compute lock: `experiments/phase-0.2/stage2-compute-decision.md`
- Conceptual / 3-panel figure: `docs/conceptual.md`
