# Phase 1.2 Plan — Production OpenAlex pull via bulk dump

**Stage:** 1 — Crawl
**Phase:** 1.2 — second phase of Stage 1
**Window opens:** TBD
**Branch:** `phase-1.2-execution` (cut from `main` post-Phase-1.1 merge)
**Status:** Plan locked. TEST → IMPLEMENT → VERIFY → RETRO discipline.

---

## Stage 1 (Crawl) — overview

| Phase | One-line scope | Status |
|---|---|---|
| 1.1 | Compute substrate + 50K dry-run | ✅ COMPLETE (`phase-1.1-plan.md`, retro at `experiments/phase-1.1/dry-run-results.md`) |
| **1.2** | **Production pull via bulk dump + N=2M sample** | **CURRENT — this plan** |
| 1.3 | Author disambiguation + demographic inference | Stub |
| 1.4 | Pre-Stage-2 quality gates + transition signoff | Stub |

---

## Phase 1.2 — One-line scope

**Stream the OpenAlex works bulk dump through Modal in parallel,
apply the locked §0 filter inline, persist the full filtered
corpus (~5-10M papers expected), and sample N=2M for Stage 2.**

This phase produces the canonical §0 analytical population P that
Stage 2 + Stage 3 will sample from. It is THE data-substrate
deliverable of Stage 1.

---

## Why this phase exists (and why bulk dump, not API)

Phase 1.1 measured pull throughput from the OpenAlex REST API at
~14K post-filter papers/hour sequential. Implication for sequential
API pulls:

| Target N | API hours | API days |
|---:|---:|---:|
| 1M | ~71 | ~3 |
| 2M | ~143 | ~6 |
| 5M | ~357 | ~15 |

This is impractical for production. Three real alternatives:

| Strategy | Time | Cost | Methodology |
|---|---:|---:|---|
| Sequential API pull | 3-15 days | $0 | Standard but slow |
| Parallel API pull | 18-36 hr | $0 | Risk: OpenAlex politeness |
| **Bulk dump + Modal `.map()`** | **~10 min** | **~$3** | **Recommended** |

**Bulk dump rationale (also satisfies ws2 desideratum §1):**

1. ws2 desideratum §1 mandates snapshot pinning. Bulk dump IS the
   snapshot — pinning is implicit.
2. The dump (~30 GB compressed JSONL split across ~100 shard
   files) parallelizes naturally via Modal `.map()`.
3. Reusable infrastructure for Stage 3 robustness sweeps and
   future snapshot refreshes.
4. Filtering happens locally on the full corpus, not via API
   calls — no rate-limit considerations.

Phase 1.1 retro lesson: pull retention at production scale is
~11.5%, not the ~30% extrapolated from Phase 0.1's single-cell
measurement. Bulk dump avoids this concern entirely (we filter
the full corpus, not sample-and-filter).

---

## Pre-registered hypotheses

### Layer A — pipeline correctness (abort-on-fail)

**H1 (parallel parse).** All ~100 OpenAlex shard files process
end-to-end on Modal `.map()` without any shard failing. Per-shard
output is a Parquet file with the §0-filtered records.

**H2 (§0 filter correctness).** Per-shard filter behavior matches
Phase 0.2 Wave 1C single-cell measurements. Specifically:
- score≥0.3 client-side filter
- has_abstract (non-empty inverted index)
- Word-boundary regex junk-year token filter (production list)
- ≥15-token empty-abstract filter

Cross-check: random sample of 100 records from the filtered
corpus has 0 false negatives (papers that should pass but don't)
in a hand audit.

**H3 (snapshot pinning).** Snapshot date recorded in artifact
metadata. Re-running against the same snapshot produces
byte-identical output (within Parquet binary equivalence).

### Layer B — yield + sampling

**H4 (corpus yield).** Full §0 filter on the OpenAlex works dump
(cs+physics 1970-2024) yields **5-15M post-filter papers**.
Below 3M → strategy revision (more permissive filter; expand
to other fields). Above 20M → §0 filter is too permissive;
investigate.

**H5 (sample integrity).** N=2M random sample drawn from the
filtered corpus is unique (no duplicates), respects per-decade
distribution within ±5% of Nᵧ-proportional (or per-decade
balanced if we choose stratification), and is reproducible with
a fixed seed.

### Layer C — operational

**H6 (cost).** Total Modal spend for Phase 1.2 ≤ $20.
Bulk-dump parse + filter ≤ $10; sampling ≤ $1; held-out
generation ≤ $5; reserve ≤ $4.

**H7 (wall-clock).** End-to-end Phase 1.2 wall-clock ≤ 1 hour
on Modal with 100-way `.map()` parallelism.

---

## TEST plan — written before IMPLEMENT

### Local unit tests for §0 filter

The §0 filter primitives (`_passes_score`, `_has_abstract`,
`_passes_junk_year`, `_passes_empty_abs`) already have implicit
test coverage via the Phase 0.2 + Phase 1.1 dry-run scripts.
Phase 1.2 lifts them into a proper module + adds dedicated unit
tests:

```
src/whitespace2/section0_filter.py:  # NEW
- _passes_score(work, concept_id) -> bool
- _has_abstract(work) -> bool
- _passes_junk_year(work, patterns) -> bool
- _passes_empty_abs(work) -> bool
- apply_section0_filter(works) -> list[works]

tests/test_section0_filter.py:  # NEW
- test_score_threshold_at_boundary (0.30 vs 0.29)
- test_has_abstract_empty_dict_returns_false
- test_junk_year_word_boundary_excludes_organism (Wave 1C regression)
- test_junk_year_post_1990_passes_through
- test_empty_abs_threshold_at_15_tokens
- test_full_pipeline_keeps_pre_1990_legitimate_paper
- test_full_pipeline_drops_post_2000_content_with_1970_year
```

### Single-shard smoke (Modal)

```
modal_parse_one_shard:
  Input: 1 shard URL (e.g., works_part_001.jsonl.gz)
  Modal: cpu=4, memory=8GB, timeout=1800s
  Output: shard_001.parquet on Volume; per-shard yield count
  Expected: shard yield ~50-150K records (~5-15% of ~1M raw per shard)
```

### 5-shard parallel smoke

```
modal_parse_5_shards_parallel:
  Input: 5 shard URLs
  Modal: .map() across 5 containers
  Output: shard_001.parquet through shard_005.parquet on Volume
  Expected: ~5 min wall-clock; all shards pass; total yield consistent
```

---

## IMPLEMENT plan

### Step 1 — Bulk-dump file enumeration (~30 min)

Identify the canonical OpenAlex bulk dump URL pattern and list
of shard files for the chosen snapshot. Likely entry point:
`https://openalex.org/data` or `s3://openalex/data/works/`.

Output: `experiments/phase-1.2/openalex-works-shards.json` with
{snapshot_date, shard_urls[], shard_sizes[]}.

### Step 2 — Section 0 filter module (~1.5 hours)

Lift Phase 0.2 + Phase 1.1 inline filter code into a clean
module. TDD: tests first.

Files:
- `src/whitespace2/section0_filter.py` (~150 lines)
- `tests/test_section0_filter.py` (~7 tests)

### Step 3 — Modal parse function (~2 hours)

`experiments/phase-1.2/parse_modal.py`:

```python
@app.function(
    image=parse_image,  # debian-slim + orjson + pyarrow + numpy
    cpu=4,
    memory=8192,
    volumes={"/output": filter_output_volume},
    timeout=1800,
    retries=modal.Retries(max_retries=3, initial_delay=10, max_delay=60),
)
def parse_one_shard(shard_url: str) -> dict[str, Any]:
    # 1. Stream from S3 via httpx + gzip.GzipFile
    # 2. Parse JSONL line-by-line via orjson (5-10× faster than stdlib)
    # 3. Apply section0_filter
    # 4. Drop unused fields (keep id, title, year, type, abstract_inv,
    #    authorships, concepts, cited_by_count, doi)
    # 5. Write filtered records to /output/shard_<i>.parquet
    # 6. Return metadata: {n_in, n_out, shard_id, snapshot_date}
```

Image must include: orjson, pyarrow, numpy. Lightweight (~500 MB).

### Step 4 — Local orchestrator (~1.5 hours)

`experiments/phase-1.2/parse_dump.py`:

```python
@app.local_entrypoint()
def main():
    shards = load_shard_list()
    print(f"Dispatching {len(shards)} shards via .map()")
    results = list(parse_one_shard.map(shards))
    # Verify all shards succeeded
    # Concat shard parquets into single corpus parquet
    # Write data/metadata/section0-population.parquet
    # Write data/metadata/section0-population-manifest.json
```

### Step 5 — Single-shard smoke (~10 min, ~$0.10)

Run `parse_one_shard.remote(first_shard_url)`. Verify:
- shape ~ (50K-150K, expected_columns)
- snapshot_date populated
- §0 filter behavior matches expectations on a hand-checked sample of 10 records

### Step 6 — 5-shard parallel smoke (~15 min, ~$0.50)

Run `.map()` across 5 shards. Verify:
- All 5 succeed
- Wall-clock ~3-5 min (parallelism works)
- Per-shard yield counts in expected range

### Step 7 — Full 100-shard parse (~10-15 min, ~$3)

Run `.map()` across all shards. Verify H1, H4 in real time.

### Step 8 — Sample N=2M (~5 min, $0)

`experiments/phase-1.2/sample_2m.py`:
- Load `section0-population.parquet`
- Random sample N=2M (seed-pinned)
- Write `data/metadata/section0-sample-2m.parquet`
- Optionally: also persist a 1M sample (for sensitivity analysis at Stage 2)

### Step 9 — Generate held-out sets (~5 min, $0)

For Stage 2 §11 + drift validation:
- 500 held-out from 1975 (cs)
- 500 held-out from 2020 (cs)
- 500 held-out from 1975 (physics)
- 500 held-out from 2020 (physics)

Disjoint from the 2M production sample; persisted as separate
Parquet files.

---

## VERIFY plan

After Step 7 (full parse) + Step 8 (sample):

1. **H1 verification:** all 100 shards in the manifest have a
   corresponding `shard_<i>.parquet` on the Volume; no Modal
   function failure logs.

2. **H4 verification (corpus yield):** total filtered count from
   concatenating all shards. Expected 5-15M; flag if outside
   that band.

3. **H4 detail (per-decade distribution):** decade histogram of
   the filtered corpus. Pre-1990 fraction expected ~5-15%
   (per Phase 1.1 finding ~11.5% retention; pre-1990 is the
   low-retention tail).

4. **H2 hand audit:** random sample of 100 papers from the
   filtered corpus. Visual check for §0-filter correctness
   (all should be cs+physics; all should have substantive
   abstract; pre-1990 ones shouldn't have post-2000 tokens).

5. **H5 sample integrity:** N=2M sample loaded; verify unique
   paper-ids; verify per-decade distribution within ±5% of
   target; reproducible from seed.

6. **H3 snapshot pinning:** manifest JSON has snapshot_date,
   shard_url_list, shard_md5s. Re-running with the same manifest
   should produce byte-equivalent Parquet outputs.

---

## RETRO plan

After VERIFY:

- `experiments/phase-1.2/parse-results.md` with measured numbers
- Lessons in `tasks/lessons.md`
- Phase 1.3 plan stub gets fleshed out for the next session

Specific lessons-watch list:
- Modal `.map()` concurrency limits hit?
- Per-shard yield variance (which shards underran/overran)?
- §0 filter false positives at scale (any reviewer-pushable issues)?
- Snapshot-date discoverability (where in OpenAlex's metadata?)

---

## Validation gates (Phase 1.2 → 1.3 go/no-go)

| # | Gate | Acceptance | Status |
|---|---|---|---|
| 1 | section0_filter unit tests pass | 7 tests green | Pending |
| 2 | Single-shard Modal smoke passes | shape + count + sanity | Pending |
| 3 | 5-shard parallel smoke passes | all 5 succeed; ~3-5 min wall-clock | Pending |
| 4 | Full 100-shard parse completes | H1 (no shard failures) | Pending |
| 5 | H4 corpus yield in [3M, 20M] | ≥3M flag minor revision; ≥20M flag filter audit | Pending |
| 6 | H2 hand audit (100-record sample) | 0 §0-filter false negatives | Pending |
| 7 | H5 sample integrity | N=2M unique; per-decade ±5%; reproducible from seed | Pending |
| 8 | H3 snapshot manifest committed | manifest.json with snapshot_date + shard md5s | Pending |
| 9 | H6 cost ≤ $20 | tasks/spend.md updated | Pending |
| 10 | H7 wall-clock ≤ 1 hour | retro records actual | Pending |
| 11 | Held-out sets generated | 4 × 500-paper Parquets, disjoint from main sample | Pending |
| 12 | Phase 1.2 retro committed | doc + lessons | Pending |

ANY gate failure → STOP, surface to user, replan before Phase 1.3.

---

## Risks + mitigations

| # | Risk | Mitigation |
|---|---|---|
| R1 | OpenAlex S3 schema or path changes mid-run | Pre-commit shard list to manifest; if pull fails halfway, re-run picks up via `.map()` retry |
| R2 | Modal concurrency limit (~100 default) | If account has lower limit, batch shards in groups; may slow wall-clock but doesn't change correctness |
| R3 | Out-of-memory on a large shard | Stream JSONL line-by-line (don't slurp); 8 GB memory should suffice for 300 MB compressed shard |
| R4 | §0 filter false positives at full-corpus scale | Hand audit catches macro-issues; per-shard yield outliers flagged for inspection |
| R5 | Snapshot-date not in shard records | Use OpenAlex's `meta.snapshot_date` field at the dump-archive level (not per-record); fall back to download-date if unavailable |
| R6 | orjson dependency conflict | Fallback to stdlib json; ~2-3× slower but works |
| R7 | Held-out sets not truly disjoint from sample | Apply set-difference on paper-id; verify in unit test |

---

## Cost estimate (Phase 1.2)

| Item | Cost |
|---|---:|
| Single-shard smoke | ~$0.10 |
| 5-shard parallel smoke | ~$0.50 |
| Full 100-shard parse + filter | ~$3-5 |
| Sample + held-out generation (CPU only) | <$1 |
| Reserve | ~$3 |
| **Phase 1.2 total** | **~$10** |

Within §9 cap; logged in `tasks/spend.md` per actual.

---

## Stage 1 phases — stubs (carryover from Phase 1.1 plan)

### Phase 1.3 (stub) — Author disambiguation + demographic inference

**Headline scope:** Run author disambiguation (career-length
screen + within-era cross-reference per plan §10) and demographic
inference (gender_guesser primary, NamSor secondary, Genderize
cross-validation per plan §4). ORCID-linkage at production scale
(applying the Wave 3A 98.6% per-region rate to scale).

**Open at start time:** Per-region NamSor escalation budget;
disambig-error rate at production scale; demographic-coverage
floor for the §9e propensity model.

**Acceptance gate (1.3 → 1.4):** Disambiguation cross-era-merger
rate ≤ 5% (per plan §10); demographic coverage ≥ 45% on P_demo
(Phase 0.1 Check 1f baseline).

### Phase 1.4 (stub) — Pre-Stage-2 quality gates + transition signoff

**Headline scope:** Spot-check production data against field
intuitions (sanity passes equivalent to Phase 0.1 Checks 1+2 on
the production-scale corpus). Sign off on Stage 1 → Stage 2
transition.

**Open at start time:** Sanity-check sample size + cells;
go/no-go thresholds at production scale.

**Acceptance gate (1.4 → Stage 2):** All field-intuition sanity
checks pass; production data committed; Stage 2 plan authored.

---

## Stage 1 → Stage 2 transition (headline-level)

What Stage 1 must deliver to Stage 2:

1. **§0 analytical population P** at production scale (this
   phase's deliverable: `data/metadata/section0-population.parquet`,
   ~5-15M papers; manifest with snapshot_date)
2. **Sampled production set** (`data/metadata/section0-sample-2m.parquet`,
   2M papers ready for Stage 2 embed)
3. **Held-out sets** (4 × 500-paper Parquets; disjoint from sample)
4. **Author + demographic annotations** (Phase 1.3 deliverable)
5. **Validated cost + preemption profile** for Modal A100 preempt
   (Phase 1.1 deliverable; complete)
6. **Resumable runner + Modal embed functions** (Phase 1.1
   deliverables; complete)

---

## Pre-flight choices already locked

Carryover from Phase 0.2 + Phase 1.1; do not re-litigate:

- §0 filter spec including word-boundary regex (Wave 1C; Phase 0.2)
- SciNCL primary + Qwen3 cross-family (Wave 4A; revalidated)
- Modal A100 preemptible (Wave 4A; cost-validated Phase 1.1)
- Per-metric N_target = 1M+ (Wave 4A)
- §11 H7' threshold 1.10 (Phase 0.2)
- ORCID-linkage rate 98.6% (Wave 3A)
- Resumable runner pattern (Phase 1.1)
- Bulk dump approach + Modal `.map()` parallelism (this phase's lock)
- Production target N=2M (this phase's lock; cost no longer binding;
  see Phase 1.1 retro)

---

## Methodology amendment (vs Phase 1.1 plan)

Phase 1.1 plan's Phase 1.2 stub said "target 1M post-§0-filter."
This plan revises to **N=2M** based on Phase 1.1's cost finding
($0.00002/abs makes 2M trivially affordable) and the methodology
gain on subfield + interaction analyses.

Locked at 2M unless Phase 1.4 quality gates surface a reason to
adjust.

---

## Companion documents

- `docs/phases/phase-1.1-plan.md` — Phase 1.1 plan
- `experiments/phase-1.1/dry-run-results.md` — Phase 1.1 retro
- `docs/phases/phase-0.2-plan.md` — Phase 0.2 pre-registration
- `experiments/phase-0.2/stage2-compute-decision.md` — Wave 4A
- `tasks/spend.md` — pre-commit estimates + actuals
- `tasks/lessons.md` — accumulated lessons
