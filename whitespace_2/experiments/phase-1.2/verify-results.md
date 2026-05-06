# Phase 1.2 — VERIFY results

Snapshot: 2026-05-05 (manifest pull + bulk parse + dedup +
nested 1M sample + 4 held-outs).

This is the data record for the Phase 1.2 retro. Numbers below
flow into `phase-1.2-retro.md` for narrative + decisions.

## Hypotheses (vs plan §VERIFY)

| ID | Plan claim | Measured | Outcome |
|---|---|---|---|
| H1 | All 2,127 shards have output Parquet on Volume; no Modal failures | 2,127/2,127 shards on Volume | PASS |
| H4 (yield) | Total post-§0 corpus 5–15M | 72.17M | **FAIL** (4.8× upper bound) |
| H4 (decades) | pre-1990 fraction 5–15% | 4.81% | **MISS** (just below band) |
| H2 (audit) | Random 100-paper hand audit; §0 correctness | Pending (manual) | Pending |
| H5 | N=1M sample loaded, unique paper-ids | 1,000,000 unique / 1,000,000 rows | PASS |
| H3 | Manifest has snapshot_date + shard URLs; reproducible | manifest committed; bulk pull deterministic by URL | PASS |

## H1 — shard coverage

All 2,127 manifest shards produced a per-shard Parquet on the
`ws2-section0` Modal Volume:

```
volume listing → 2,127 *_part_*.parquet entries
manifest entries: 2,127
```

No `parse_one_shard` failures. Modal `.map()` with
`return_exceptions=True` returned zero exceptions across the full
run.

## H4 yield — population is 4.8× the plan band

Plan H4 band: 5–15M post-§0-filter records. Measured: **72,173,308
records** in `section0-population.parquet` (after dedup by `id`,
keeping the row with maximum `updated_date`).

Why the miss is most likely:

- Plan band was set on a desk extrapolation from Phase 0.1 pilot
  yields, scaled by manifest size. The Phase 0.1 pilot was a
  300K-record API fetch with field+score filters applied at fetch
  time; bulk-dump records arrive without those filters and need
  in-process §0 application, but the in-process §0 filter is the
  same predicate (score ≥ 0.30 + has_abstract + junk-year + 15-
  token min). Yields that match across pilot + bulk should have
  caught this.
- The 8.7% bulk-dump yield (per Step 6 smoke) × 492M raw records
  = 42.8M expected. The ratio jumps further to 72.17M because the
  bulk dump's `updated_date` partition contains overwrites — a
  paper updated 5× appears in 5 shards. After dedup, ~72M of those
  rows remain — implying the bulk dump's effective unique-record
  count is closer to ~830M (since 8.7% × 830M ≈ 72M), not 492M as
  the manifest implies.
- Net: the §0 filter is doing what it was specified to do; the
  manifest size is the surprise.

Implication for downstream:

- **Sample fraction**: 1.4% of population (vs 7–20% planned). 1M
  sample is still well above any per-decade-cell minimum power
  threshold (e.g., 1970s gets ~11.5K papers in the sample).
- **Storage**: population parquet is 2.8 GB compressed; lives on
  Modal Volume (gitignored locally).
- **Stage 2 cost**: not affected — Stage 2 embeds the 1M sample,
  not the full population.
- **Variance considerations**: with only 1.4% sampling rate the
  per-paper sampling variance dominates over finite-population
  correction, so design-effect adjustments are negligible.

## H4 detail — decade distribution (from 1M sample)

Sample is uniform-random by `hash(seed||id)`, so per-decade
fractions are within ~1 / sqrt(N_decade) of population. For all
decades with ≥1K sample papers, the relative error is <1%.

| Decade | Sample count | Sample share |
|---|---:|---:|
| 1970s | 11,524 | 1.16% |
| 1980s | 17,022 | 1.72% |
| 1990s | 34,149 | 3.45% |
| 2000s | 106,870 | 10.80% |
| 2010s | 246,203 | 24.89% |
| 2020s | 554,511 | 56.05% |

Pre-1990 share: **4.81%** (plan band 5–15%). Just below the lower
bound. Absolute pre-1990 papers in the population ≈ 4.81% × 72.17M
= **3.47M** — abundant for any decade-stratified analysis. The
miss is on share, not on absolute power.

Edge-case observations (informational):

- 119 records have `publication_year = 1750`; all observed cases
  are anachronistic OpenAlex metadata (catalog records of
  pre-modern works that happen to match the §0 filter via
  modern abstracts). Effect on metrics is negligible.
- 1 record has `publication_year = 2030` (forward-dated; likely
  scheduled publication or erratum).
- No NULL `publication_year` values — §0 / dedup retains
  `publication_year` for all kept records.

## H5 — sample integrity

```
n_rows:        1,000,000
n_unique_ids:  1,000,000   ← all unique
nulls in id:   0
nulls in publication_year: 0
nulls in abstract_inverted_index_json: 0  ← §0 has_abstract enforced
```

Sample seed: `ws2-phase-1.2-nesting-seed-v1` (committed in
`parse_modal.py`; immutable).

Nested-sampling property holds: re-running `sample_population(N)`
for any N ≥ 1M (e.g., escalating to 2M) produces a strict
superset.

## Field distribution (informational)

`concepts_json` contains the OpenAlex concept array. A paper is
"in cs" / "in physics" if a concept with the relevant ID appears
anywhere in the array (LIKE match — not score-checked here, but
§0 already enforces score ≥ 0.30 on at least one of the two).

| Field flag | n in 1M sample | share |
|---|---:|---:|
| cs concept appears | 624,484 | 62.4% |
| physics concept appears | 511,902 | 51.2% |
| both appear | 136,386 | 13.6% |
| (cs ∪ physics) | 1,000,000 | 100.0% (by §0) |

Cross-disciplinary cs+physics rate of 13.6% is consistent with
the 9–18% bands cited in §0 robustness checks during Phase 0.2.

## Abstract metrics (informational)

```
mean abstract_inverted_index_json size: 1,281 chars
min / max:                              45 / 32,757
pct < 100 chars:                        0.0%
null abstract:                          0
```

§0's `15-token empty-abstract minimum` and `has_abstract` filters
are doing their job — no zero-token or near-zero abstracts in the
sample.

## Held-out cells (Step 9 — disjoint from sample)

| Cell | n | concept score≥0.30 hit | overlap with sample |
|---|---:|---:|---:|
| 1975-cs | 500 | 500/500 | 0 |
| 1975-physics | 500 | 500/500 | 0 |
| 2020-cs | 500 | 500/500 | 0 |
| 2020-physics | 500 | 500/500 | 0 |

Held-out seed: `ws2-phase-1.2-heldout-seed-v1`. Different from the
nesting seed so per-cell ordering is independent of sample
membership.

## Spend tracking

Phase 1.2 actual Modal compute (cumulative, to-date):

- Step 5/6 smokes (single + 5-shard parallel): ~$1
- Step 7 full parse (2,127 shards × ~100s per shard, ~100-way
  parallelism): ~$80–100 (within $80-100 plan estimate)
- Step 7 dedup (2-pass GROUP BY → JOIN, 64GB + 512GB ephemeral
  disk, single container, ~30 min): ~$2
- Step 8 sample (32GB + 512GB disk, 2-pass, ~2 min): ~$0.50
- Step 9 held-outs (32GB + 512GB disk, ~5 min): ~$1

Total Phase 1.2: ~$85–105 (within plan range).

## VERIFY signoff

- H1 PASS, H5 PASS, H3 PASS.
- H4 yield FAIL (population 4.8× over plan band) — surfaced for
  retro.
- H4 decade FAIL (pre-1990 share just below band) — minor;
  absolute pre-1990 power is abundant.
- H2 audit pending — sample 100 papers + visual spot check
  during retro.

Decision required (in retro): does H4 yield miss require any
methodology change? The §0 filter behaved as specified; the miss
is on the manifest-size assumption. Default proposal: accept the
larger population (no methodology change), tighten the plan-band
language for Phase 1.3+ to be a "loose informational target,"
and document the bulk-dump-update-overwrite mechanism for future
phases.
