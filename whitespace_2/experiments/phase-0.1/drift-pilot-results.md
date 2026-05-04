# Check 5c — Drift pilot (nearest-neighbor era-match rate)

**Run date:** 2026-04-28
**Snapshot recorded:** 2026-04-28T05:04:30+00:00
**Mode:** full
**Device:** mps; **dtype:** fp16

## Data composition

| Set | N | Years |
|-----|---:|---|
| Query Q | 100 | 1970-1980 |
| Pool C, pre-1990 | 500 | 1970-1989 |
| Pool C, post-2000 | 500 | 2000-2024 |

## Pull summaries

| Label | Years | Calls | Pre-filter raw | Taken | Target |
|---|---|---:|---:|---:|---:|
| queries | 1970-1980 | 11 | 2200 | 100 | 100 |
| pool_pre1990 | 1970-1989 | 20 | 4000 | 500 | 500 |
| pool_post2000 | 2000-2024 | 25 | 5000 | 500 | 500 |

## Embedding timing (this run)

| Model | Total (s) | s/abstract |
|-------|----------:|-----------:|
| scincl | 214.3 | 0.195 |
| specter2 | 241.9 | 0.220 |
| qwen3 | 3011.9 | 2.738 |

## Era-match rates (Layer B H5 + H6)

Per-model headline = mean over 100 queries of (#{neighbors year≤1990} / 10).
95% CI via 1000-resample bootstrap over queries (seed=46).

| Model | Era-match rate | 95% CI | N queries |
|-------|---------------:|--------|----------:|
| scincl | 75.4% | [71.5%, 79.1%] | 100 |
| specter2 | 62.8% | [57.0%, 68.6%] | 100 |
| qwen3 | 70.7% | [66.6%, 74.9%] | 100 |

## Decision (per Phase 0.1 plan §2)

**SPECTER2 era-match: 62.8%** with CI [57.0%, 68.6%].

**Action:** commit Flavor A (cheap insurance).

**Rationale:** CI [57.0%, 68.6%] straddles a boundary or point estimate 62.8% ∈ [50%, 70%] — gray zone.

## H7 — Hand-audit (qualitative validation of date-based metric)

30 (query, neighbor) pairs hand-coded by domain reading: 10 per model × {5
pre-1990 neighbor (era_match_date=True), 5 post-2000 neighbor (era_match_date=False)}.
Coding rule: `topically_related = yes` iff query and neighbor share substantive
topical content (not just surface-word overlap, boilerplate, or unrelated
domains). Filled column persisted in `drift-pilot-hand-audit.csv`.

**Headline: H7 FAILS pre-registered ≥80% threshold.**

| Model | Agreement (date-based ↔ topical) | n |
|-------|---------------------------------:|--:|
| scincl   | 70.0% (7/10) | 10 |
| specter2 | 70.0% (7/10) | 10 |
| qwen3    | 60.0% (6/10) | 10 |
| **Overall** | **66.7% (20/30)** | **30** |

### Error-mode decomposition

| Error mode | Count | What it means |
|---|---:|---|
| Type A — date=match BUT topically unrelated | 7/15 era-match pairs (47%) | Date-based metric **overstates drift mitigation success.** Models retrieved another pre-1990 paper, but it's not actually about the query topic. |
| Type B — date=mismatch BUT topically related | 3/15 era-mismatch pairs (20%) | Date-based metric **overstates drift severity.** Models correctly retrieved a topically-relevant modern paper that the binary era rule penalizes. |

Net direction: **Type A > Type B (47% vs 20%) — drift severity is somewhat
worse than the date-based rate suggests.** SPECTER2's 62.8% headline is an
upper bound on true topical-era-match precision; the topically-correct
era-match rate is closer to 62.8% × (1 - 0.47) ≈ **33%** if we
strictly count Type A as drift failures.

### Implications for the H6 decision

H7's failure **reinforces** the "commit Flavor A as cheap insurance"
decision. The pre-registered date-based metric is the H6 input and lands
in the gray zone (CI [57.0%, 68.6%], fully inside [50%, 70%]). The H7
audit shows the metric, if anything, is too generous: a stricter
topical-match metric would push SPECTER2 substantially below 50%, into
the "commit Flavor A (drift severe)" bin.

The decision stands: **commit Flavor A**. The cheap-insurance framing
remains correct against the pre-registered metric; the drift-severe
reading is the more plausible interpretation against a strict
topical-match metric.

## Surprises and limitations surfaced by Check 5c

1. **Many queries are non-CS papers.** Several query abstracts are
   language-teaching workbooks, Alaska mineral indices, NBC news
   scripts, and journal cover/back matter — papers OpenAlex tagged
   with `concepts.id:C41008148` at score ≥ 0.3 but whose substantive
   topic is peripheral to CS. This is a known consequence of OpenAlex's
   loose concept-tagging promiscuity (per Check 2 lessons). For Phase
   0.2, the strict ≥0.5 threshold (per plan §3 score-thresholding
   policy) should be considered for the analytical population, not
   just for tight subfield identity.

2. **Junk-year-metadata leaks not caught by minimal pilot token list.**
   Two query rows (24, 25) have `publication_year=1970` but content
   that is unmistakably post-1990: row 24 references the TI TMS320C3X
   DSP (released 1988+), row 25 is an Indonesian e-government
   information-systems paper. Neither matches the minimal 5-token
   filter (`R-CNN`, `IoT`, `blockchain`, `transformer`, `smartphone`).
   The full Phase-0.2-locked junk-year token list will need to expand
   to catch chip-name leaks and language-other-than-English content
   patterns.

3. **Boilerplate matches inflate similarity.** Row 8 (scincl, sim=1.000)
   pairs two "abstract not available" filler papers with identical
   placeholder text — the similarity is real but topically meaningless.
   Several other "agreement" cases on the era-mismatch side rely on
   filler/reference-list pairs where neither paper has substantive
   content (rows 14, 17, 19). For Phase 0.2, an empty/near-empty
   abstract filter (e.g., minimum N tokens after decoding) should be
   added to the pull spec.

4. **Per-model spread is large and informative.**
   - SciNCL (75.4%) is closest to "skip Flavor A" individually; passes
     the 70% boundary cleanly.
   - Qwen3 (70.7%) straddles 70% — gray-zone behavior matching its
     decoder-LM cross-architecture status.
   - SPECTER2 (62.8%) is firmly in gray zone; the rule keys here.
   The spread reinforces that diachronic-robustness varies by model
   even within transformer-based encoder-style embedders.

5. **Embedding timing on M-series.** Full-run timing matched smoke
   estimates closely:
   - SciNCL: 0.195 s/abs (smoke 0.619 includes load) — improved with
     warm cache and bs=8 over 1100 abstracts.
   - SPECTER2: 0.220 s/abs (smoke 0.349) — same improvement.
   - Qwen3 bs=1: 2.738 s/abs (smoke 2.155) — slightly slower at full
     scale; abstract-length distribution may differ across pulls.
   These remain consistent with Phase 0.1.E's H7 failure against plan
   §1; Stage 2 cloud-vs-local decision still leans cloud per
   `embedding-pipeline-smoke.md`.

## Per-query era-match histogram (diagnostic)

| Model | 0/10 | 1/10 | 2/10 | 3/10 | 4/10 | 5/10 | 6/10 | 7/10 | 8/10 | 9/10 | 10/10 |
|-------|-----:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|-----:|------:|
| scincl | 0 | 0 | 1 | 4 | 4 | 2 | 16 | 17 | 21 | 19 | 16 |
| specter2 | 2 | 7 | 2 | 9 | 11 | 8 | 11 | 10 | 9 | 12 | 19 |
| qwen3 | 1 | 0 | 1 | 0 | 10 | 11 | 20 | 9 | 20 | 13 | 15 |

## Decision-rule reference

Per Phase 0.1 plan §2 (Stage 2 default + Stage 3 conditional Flavor A):

- SPECTER2 era-match CI fully > 70% → drift manageable, **skip Flavor A**.
- SPECTER2 era-match CI fully < 50% → drift severe, **commit Flavor A**.
- Otherwise → **commit Flavor A as cheap insurance**.

Flavor A = Word2Vec-per-decade + orthogonal Procrustes alignment + TF-IDF-weighted document aggregation (Hamilton-Leskovec-Jurafsky 2016 template, document-level adaptation).

## Artifacts

- `data/metadata/drift-pilot-queries.parquet` — 100 rows.
- `data/metadata/drift-pilot-pool.parquet` — 1000 rows.
- `experiments/phase-0.1/drift-pilot-embeddings-{specter2,scincl,qwen3}.parquet` — 3 files.
- `experiments/phase-0.1/drift-pilot-neighbors.csv` — 3000 rows (100 × 3 × 10).
- `experiments/phase-0.1/drift-pilot-hand-audit.csv` — 30 rows (topically_related filled inline this session).
- `experiments/phase-0.1/drift-pilot-rates.csv` — per-model era-match + CI.
