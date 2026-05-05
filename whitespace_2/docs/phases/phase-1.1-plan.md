# Phase 1.1 Plan — Compute substrate + 50K dry-run

**Stage:** 1 — Crawl (begins 2026-05-05)
**Phase:** 1.1 — first phase of Stage 1
**Window opens:** TBD (next session)
**Branch:** `phase-1.1-execution` (cut from `main` post-Phase-0.2 PR #5 merge)
**Status:** Plan locked. TEST → IMPLEMENT → VERIFY → RETRO discipline.

---

## Stage 1 (Crawl) — overview

Stage 1 covers production-scale data work: pulling the §0
analytical population P from OpenAlex, running author
disambiguation + demographic inference, validating data quality
against field intuitions, and verifying compute economics before
Stage 2 begins the embedding-and-metric pipeline.

**Stage 1 phases (Phase 1.1 in detail; rest as stubs):**

| Phase | One-line scope | Status |
|---|---|---|
| **1.1** | **Compute substrate + 50K dry-run** | **CURRENT — this plan** |
| 1.2 | Production OpenAlex pull (target 1M post-§0-filter) | Stub |
| 1.3 | Author disambiguation + demographic inference | Stub |
| 1.4 | Pre-Stage-2 quality gates + transition signoff | Stub |

Stage 1 → Stage 2 transition criteria summarized at the bottom of
this plan; details fleshed out in Phase 1.4 when current.

---

## Phase 1.1 — One-line scope

**Set up Modal A100 preemptible compute infrastructure + a
resumable runner; verify the locked Stage 2 budget on a
50K-sample dry-run before committing the full 1M production
embedding.**

This is the highest-risk-front-loaded phase. Everything downstream
(Phase 1.2 pull, 1.3 disambig+demo, Stage 2 embed) assumes the
A100 preemptible cost + runner correctness numbers are in the
ballpark of Wave 4A's locked estimates. Phase 1.1 verifies those
assumptions before they get committed.

---

## Why this phase exists

Wave 4A locked the Stage 2 compute target as Modal A100 preemptible
at N=1M for headline + N=500K for robustness. The locked numbers:

| Item | Estimate |
|---|---:|
| Per-abstract A100 cost | ~$0.05/abs |
| Preemptible discount | ~40% off list |
| Headline 3-run budget | $150-300 |
| Robustness 2-run budget | $50-100 |
| Reserve | $50-150 |
| **Total Stage 2** | **$250-550** within §9 cap |

These are extrapolated from Wave 1A (Qwen3 timing on M-series
MPS) + Wave 2A (SPECTER2 production-scale timing). They have NOT
been verified on actual Modal A100 preemptible compute.

Phase 1.1's goal is to either CONFIRM these numbers within ±50%
(allowing Stage 2 to proceed with the locked budget) or SURFACE
a replan trigger before the production embed lands.

---

## Pre-registered hypotheses

### Layer A — pipeline correctness (abort-on-fail)

**H1 (resumable runner correctness):** The chunked runner, when
killed via SIGTERM mid-batch, resumes cleanly on restart with NO
data loss. After N≥10 simulated SIGTERM events at random points
during a 1000-paper test run, the resumed output is
**byte-identical** to a clean (no-preemption) reference run.

**H2 (Modal deploy):** The runner deploys + runs end-to-end on
Modal A100 preemptible. No undefined-behavior modes (e.g.,
incompatible torch version, missing model files, OOM at A100
40GB).

### Layer B — cost + preemption observations

**H3 (cost):** Combined SciNCL+Qwen3 per-abstract cost on Modal
A100 preemptible is ≤ $0.075/abs (50% margin over $0.05 estimate).
Above $0.075 → replan trigger.

**H4 (preemption rate):** Total wall-clock from preemption-driven
restarts is ≤ 30% of total wall-clock. Above 30% → suggests A100
preemptible capacity is too tight in our region/time-of-day;
consider switching to A10G preemptible OR non-preemptible A100.

### Layer C — output validity

**H5 (output finite + correct shape):** All output vectors are
finite and have correct shape:
- SciNCL: (50000, 768)
- Qwen3: (50000, 768) Matryoshka-truncated

**H6 (norm bands match Phase 0.2):**
- SciNCL: mean L2 norm ∈ [22.5, 24.5] (Wave 4A revalidation
  measured [22.66, 24.43])
- Qwen3: mean L2 norm ≈ 1.0 (already L2-normalized via
  last-token EOS pooling)

Out-of-band norms → flag investigate (Modal env-version drift,
fp16 precision issue, etc.).

---

## TEST plan — written before IMPLEMENT

### Resumable runner unit tests (6 cases, local; ~3-5 min total)

```
test_runner_clean_run:
  Input: 100 abstracts × 1 chunk (size 100)
  Expected: 100 vectors written to chunk_0.npy; done.txt has chunk_0.

test_runner_chunked_clean:
  Input: 1000 abstracts × 10 chunks (size 100)
  Expected: 10 chunk_*.npy files; done.txt has 10 entries;
            concatenated output shape (1000, 768).

test_runner_kill_mid_chunk:
  Input: 1000 abstracts × 10 chunks
  Action: SIGTERM after chunk 5 completes write but BEFORE
          done.txt update (race window).
  Expected on restart: chunk 5 gets re-embedded (since done.txt
                       didn't reflect it); final output identical
                       to clean run.

test_runner_kill_during_chunk:
  Input: 1000 abstracts × 10 chunks
  Action: SIGTERM mid-chunk-7-embedding.
  Expected on restart: chunks 0-6 skipped; chunk 7 re-embedded;
                       chunks 8-9 embedded; output identical to
                       clean run.

test_runner_idempotent_done_marking:
  Input: 1000 abstracts × 10 chunks
  Action: SIGTERM RIGHT AFTER chunk 5's done.txt write.
  Expected on restart: chunks 0-5 skipped; chunks 6-9 embedded.

test_runner_partial_chunk_file_recovery:
  Input: 1000 abstracts × 10 chunks
  Action: Corrupt chunk_5.npy (truncate) BEFORE restart.
  Expected on restart: detect corruption (file shorter than
                       expected), re-embed chunk 5.
```

These tests run LOCALLY (no Modal) using a tiny SciNCL model
load + synthetic abstracts. Total wall-clock for the test suite:
~3-5 min on M-series MPS.

### Modal-deploy smoke test (~5)

After local tests pass:
```
modal_smoke_100:
  Input: 100 real abstracts (seed=42 from cs 1990, post-§0-filter)
  Modal config: A100 preemptible, 1 GPU, 30-min timeout
  Expected: clean run completes; output downloads to local;
            shape (100, 768) per model; finite; norms in band.
```

Cost: ~100 × $0.05 = $5. Within §9 cost-gate.

---

## IMPLEMENT plan

### Step 1 — Modal account verification (~15 min)

- Confirm the existing Modal account is accessible (env has
  `MODAL_TOKEN_ID` and `MODAL_TOKEN_SECRET`, or sign in via CLI).
- Verify A100 preemptible availability in our region.
- Verify .env is loaded (NamSor + Genderize keys; Modal doesn't
  need them yet but Phase 1.3 will).

### Step 2 — Resumable runner implementation (~3-4 hours)

`src/whitespace2/resumable_runner.py`:

- `class ChunkedEmbedRunner`:
  - `__init__(self, model_fn, chunk_size, output_dir)`
  - `run(self, abstracts: list[str]) -> np.ndarray`
  - Writes `<output_dir>/chunk_<i>.npy` per chunk
  - Atomic done.txt append (write to .tmp, fsync, rename — race-free)
  - Skip-on-restart: read done.txt at start; skip chunks already there
  - Final concat: read all chunk_*.npy in order; return (N, dim)
  - Corruption detection: if chunk_<i>.npy is shorter than expected
    chunk_size, re-embed
- Type-checked + ruff-clean.
- 6 unit tests (per TEST plan above).

### Step 3 — Modal function definition (~1-2 hours)

`experiments/phase-1.1/embed_modal.py`:

- `@app.function(gpu="A100", concurrency_limit=10, ..., preemptible=True)`
- Loads SciNCL + Qwen3 (cached via Modal volume)
- Accepts `abstracts: list[str]` + `model_name: str`
- Returns vectors as numpy bytes
- Calls into `ChunkedEmbedRunner` for the actual embedding work
- Modal-side checkpointing: writes chunks to a Modal volume so
  preemption-driven restarts can resume without re-uploading
  abstracts

Considerations:
- Modal volume for cached model weights: ~600MB SciNCL + ~1.2GB
  Qwen3-Embedding-0.6B = ~1.8GB
- Modal volume for in-progress chunks: temporary; cleaned up
  after run
- Timeout per function call: 1 hour (chunk-level)
- If preempted during a chunk, Modal automatically retries —
  the runner deduplicates via done.txt
- **Verify Modal's current preemptible flag name** (it's been
  renamed across Modal versions; check current docs)

### Step 4 — Modal smoke test (~30 min, $5)

Run `modal_smoke_100` per TEST plan. Verify end-to-end works.

### Step 5 — 50K dry-run (~3-5 hours wall-clock, ~$8-12)

`experiments/phase-1.1/dry_run_50k.py`:

- Pull 50K post-§0-filter papers from OpenAlex (cs+physics,
  1970-2024) using locked §0 filter (regex word-boundary)
- Embed all 50K with SciNCL on Modal A100 preemptible
- Embed all 50K with Qwen3 on Modal A100 preemptible
- Track wall-clock; measure preemption events; count restarts
- Verify outputs: shape, finite, norm bands

Expected timing:
- SciNCL on A100: ~50K × 0.06 s/abs (1/7 of M-series 0.42) = ~50 min
- Qwen3 on A100 bs=1: ~50K × 0.28 s/abs (1/7 of M-series 1.95) = ~3.9 hours
- Total: ~4.5 hours wall-clock if no preemptions; ~6-8 hours
  if preemption rate is 30%

Expected cost:
- SciNCL: ~50 min × $1.70/hr = ~$1.40
- Qwen3: ~4 hours × $1.70/hr = ~$6.80
- Total: ~$8 (well under §9 $50 single-run cost-gate)

If H3 fires (cost > $0.075/abs at 1M extrapolation), surfaces a
replan trigger. Possible replans:
- Drop preemptible to non-preemptible A100 (40% more expensive,
  near-zero preemption)
- Drop to A10G preemptible (slower but cheaper per-hour; check
  per-abstract cost)
- Drop headline N from 1M to 500K (reduces total spend)

---

## VERIFY plan

After Step 5 (dry-run) completes:

1. **Cost extrapolation:** measure actual per-abstract A100 cost.
   Extrapolate to 1M for both models. Compare to Wave 4A locked
   budget. **Replan trigger: actual > $0.075/abs combined.**

2. **Preemption rate:** count restart events and time spent on
   re-embedding lost chunks. Compute total wall-clock penalty.
   **Replan trigger: penalty > 30% of total wall-clock.**

3. **Output validity:** load both models' 50K vectors. Verify:
   - Shape (50000, 768) per model
   - All finite (`np.isfinite(v).all()`)
   - SciNCL mean norm ∈ [22.5, 24.5]
   - Qwen3 mean norm ≈ 1.0
   - **Replan trigger: any of the above fails**

4. **Resume-correctness sanity:** after the run, simulate one
   final SIGTERM mid-restart in a controlled subset; verify
   output bit-identical to the prior result.

5. **Norm-band assertion update:** Phase 0.1.E pipeline tests
   assert SPECTER2 norm band [21.0, 23.0]. If SciNCL becomes
   Stage 2 production primary (per Wave 4A lock), update or
   add SciNCL band [22.5, 24.5] to the norm-band test.

---

## RETRO plan

After VERIFY:

- Document actual per-abstract cost + preemption rate in
  `experiments/phase-1.1/dry-run-results.md`.
- Lock the production-run budget: numbers feed into Phase 1.2's
  pull script + Stage 2 embedding planning.
- If any H1-H6 fired, document the replan + decision.
- Lessons logged in `tasks/lessons.md`.

---

## Validation gates (Phase 1.1 → 1.2 go/no-go)

| # | Gate | Acceptance | Status |
|---|---|---|---|
| 1 | All 6 resumable runner unit tests pass | TEST plan items green | Pending |
| 2 | Modal smoke test (100 abstracts) passes | shape + finite + in-band norm | Pending |
| 3 | 50K dry-run completes end-to-end | both models, no abort | Pending |
| 4 | H1 (resumable correctness) | byte-identical resume vs clean | Pending |
| 5 | H3 (cost) — actual ≤ $0.075/abs | combined SciNCL+Qwen3 | Pending |
| 6 | H4 (preemption rate) — penalty ≤ 30% | wall-clock measurement | Pending |
| 7 | H5+H6 (output validity + norm bands) | as specified | Pending |
| 8 | Retro written + lessons logged | doc commit | Pending |

**ANY gate failure → STOP, surface to user, replan before Phase 1.2.**

---

## Risks + mitigations

| # | Risk | Mitigation |
|---|---|---|
| R1 | Modal A100 preemptible region has high preemption rate | Switch to A10G preemptible (slower but more available) OR non-preemptible A100 (40% more cost; no preemption) |
| R2 | Resumable runner has subtle race conditions in done.txt | 6-test TEST plan covers race windows; atomic rename pattern; corruption detection |
| R3 | Qwen3 cost extrapolation off (bs=1 on A100 is slower than expected) | 50K dry-run measures it; replan trigger fires if > $0.075/abs combined |
| R4 | Modal egress cost not factored into estimate | Egress is small (1M × 768 × 4 bytes = ~3 GB; ~$0.30 at typical rates); negligible vs compute |
| R5 | Out-of-band norms reveal env-drift between local Phase 0.2 + Modal | Pin Modal's torch + transformers + sentence-transformers versions to match Phase 0.1.E |

---

## Cost estimate (Phase 1.1)

| Item | Cost |
|---|---:|
| Modal A100 smoke test (100 abstracts) | ~$5 |
| Modal A100 dry-run (50K both models) | ~$8-12 |
| Modal A100 contingency (if Step 5 needs re-run) | +$8-12 |
| **Phase 1.1 total** | **~$20-30** |

Within §9 cap; no pre-commit gate fires (single runs <$50). Logged
in `tasks/spend.md` as it incurs.

---

## Critical files

**Phase 0.2 lock points referenced:**
- `whitespace_2/docs/phases/phase-0.2-plan.md` §1, §11 — model
  stack + threshold locks
- `whitespace_2/experiments/phase-0.2/stage2-compute-decision.md`
  — Wave 4A compute lock + budget
- `whitespace_2/docs/phases/phase-0.2-scincl-primary-contingency.md`
  — SciNCL→SPECTER2 fallback (active)
- `whitespace_2/tasks/spend.md` — pre-commit estimates

**Existing implementations to reuse:**
- `src/whitespace2/embeddings.py::embed_scincl,embed_qwen3`
  — Phase 0.1.E embedding functions (stable)
- `src/whitespace2/openalex.py::fetch_works,...` — pull spec
  utilities (stable)
- `experiments/phase-0.2/section11_followup_bigger_heldouts.py`
  — pattern for "load existing data + embed + project" (rough
  template)

**New files to be created in Phase 1.1 (NOT this planning task):**
- `src/whitespace2/resumable_runner.py` — chunked
  write-then-mark-done runner
- `experiments/phase-1.1/embed_modal.py` — Modal function
- `experiments/phase-1.1/dry_run_50k.py` — driver
- `tests/test_resumable_runner.py` — 6 unit tests
- `experiments/phase-1.1/dry-run-results.md` — VERIFY artifact

---

## Stage 1 phases — stubs

### Phase 1.2 (stub) — Production OpenAlex pull

**Headline scope:** Pull the §0 analytical population P at
production scale (target 1M post-filter for CS+Physics,
1970-2024) using the locked filter (regex word-boundary
junk-year tokens + 15-token empty-abstract minimum + score≥0.3).
Per-decade supplemental seed pulls per Phase 0.1 Check 5d
lesson. Snapshot date pinned per ws2 desideratum §1.

**Open at start time:** Per-decade pull-budget allocation;
decade-balanced vs Nᵧ-proportional sampling for the production
set; held-out set construction.

**Acceptance gate (Phase 1.2 → 1.3):** ≥1M post-filter unique
papers; per-decade representation matches Nᵧ within 10%; pull
manifest committed.

### Phase 1.3 (stub) — Author disambiguation + demographic inference

**Headline scope:** Run author disambiguation (career-length
screen + within-era cross-reference per plan §10) and demographic
inference (gender_guesser primary, NamSor secondary, Genderize
cross-validation per plan §4). ORCID-linkage at production scale
(applying the Wave 3A 98.6% per-region rate to scale).

**Open at start time:** Per-region NamSor escalation budget;
disambig-error rate at production scale; demographic-coverage
floor for the §9e propensity model.

**Acceptance gate (Phase 1.3 → 1.4):** Disambiguation cross-era-
merger rate ≤ 5% (per plan §10's working assumption); demographic
coverage ≥ 45% on P_demo (Phase 0.1 Check 1f baseline).

### Phase 1.4 (stub) — Pre-Stage-2 quality gates + transition signoff

**Headline scope:** Spot-check the production data against field
intuitions (sanity passes equivalent to Phase 0.1 Checks 1+2 on
the production-scale corpus). Sign off on Stage 1 → Stage 2
transition.

**Open at start time:** Sanity-check sample size + cells;
go/no-go thresholds at production scale (vs pilot scale).

**Acceptance gate (Phase 1.4 → Stage 2):** All field-intuition
sanity checks pass; production data committed; Stage 2 plan
authored.

---

## Stage 1 → Stage 2 transition (headline-level)

What Stage 1 must deliver to Stage 2:

1. **§0 analytical population P** at production scale (parquet
   + JSON manifest + snapshot date)
2. **Author + demographic annotations** with confidence scores
   (parquet + per-region inference accuracy table)
3. **Validated cost + preemption profile** for Modal A100
   preemptible (from Phase 1.1)
4. **Resumable runner** ready for Stage 2's headline embedding
   pass

Stage 2 first task: kick off the 1M headline embedding using
Phase 1.1's locked compute config + Phase 1.2's pulled corpus.

---

## Companion documents

- `docs/phases/phase-0.2-plan.md` — Phase 0.2 pre-registration
- `docs/phases/phase-0.2-retro.md` — Phase 0.2 retro
- `experiments/phase-0.2/stage2-compute-decision.md` — Wave 4A lock
- `docs/phases/phase-0.2-scincl-primary-contingency.md` —
  SciNCL→SPECTER2 fallback (active for Phase 1.1)
- `tasks/spend.md` — pre-commit estimates + actuals

---

## Pre-flight choices already locked

Carryover from Phase 0.2; do not re-litigate in Phase 1.1:

- Modal A100 preemptible (Wave 4A)
- SciNCL primary + Qwen3 cross-family (Wave 4A + revalidated)
- Word-boundary regex junk-year filter (Wave 1C)
- Per-metric N_target = 1M headline / 500K robustness (Wave 4A)
- Cross-field Physics deferred to Stage 3 conditional (Wave 4A)
- Genderize keyed-free tier (Wave 4B)
- §11 H7' threshold 1.10 (Wave 2A + Wave 4A revalidation)
- ORCID-linkage rate 98.6%; no per-region restriction (Wave 3A)
