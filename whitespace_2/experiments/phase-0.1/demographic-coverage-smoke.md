# Check 3 — Demographic inference coverage (SMOKE)

**Run date:** 2026-04-28
**Snapshot:** 2026-04-28T16:44:40+00:00
**Mode:** smoke
**Source:** `pilot-query-results.parquet`
**Authors extracted:** 50 (49 papers;
37 unique first names).
**Inference methods:**
- **gender_guesser** (PRIMARY for H5): 20 of 37
  unique names assigned to {male, female} (offline lookup, no API).
- **Genderize.io** (CROSS-VALIDATION): cache at `genderize-cache.json`
  with 94 valid responses (out of 97 cached entries).
**Spend:** $0 (gender_guesser is offline; Genderize used keyed-free 2500/mo
tier on a partial subset).

**Cross-validation: gender_guesser vs Genderize agreement** (unique names in both sources, n=36):

- Both assigned + same gender: 20 (55.6%)
- Both assigned + opposite gender: 0 (0.0%)
- Only gender_guesser assigned: 0 (0.0%)
- Only Genderize assigned (p≥0.8): 9 (25.0%)

Agreement on jointly-assigned subset: 20/20 = 100.0%.


## Per-cell coverage (3a / 3b / 3c)

Coverage threshold per plan §4 / §1691: **≥80%**. Gender confidence
threshold: probability ≥ 0.8.

| Field | Year | N auth | N pap | 3a Gender p≥0.8 | 3b Ctry | 3c ORCID |
|---|---:|---:|---:|---|---|---:|
| cs | 1975 | 5 | 23 | 60.0% (FAIL) | 8.7% (FAIL) | 40.0% |
| cs | 1990 | 5 | 19 | 60.0% (FAIL) | 0.0% (FAIL) | 0.0% |
| cs | 2005 | 5 | 63 | 40.0% (FAIL) | 4.8% (FAIL) | 20.0% |
| cs | 2015 | 5 | 62 | 0.0% (FAIL) | 3.2% (FAIL) | 60.0% |
| cs | 2024 | 5 | 92 | 40.0% (FAIL) | 1.1% (FAIL) | 40.0% |
| physics | 1975 | 5 | 30 | 60.0% (FAIL) | 6.7% (FAIL) | 20.0% |
| physics | 1990 | 5 | 32 | 20.0% (FAIL) | 15.6% (FAIL) | 20.0% |
| physics | 2005 | 5 | 43 | 80.0% (PASS) | 4.7% (FAIL) | 20.0% |
| physics | 2015 | 5 | 63 | 20.0% (FAIL) | 6.3% (FAIL) | 80.0% |
| physics | 2024 | 5 | 40 | 20.0% (FAIL) | 5.0% (FAIL) | 80.0% |

H5 (gender ≥80%): **1 / 10 cells pass**.
H6 (country ≥80%): **0 / 10 cells pass**.

## Decisions

### 3a — Gender coverage (H5)

**H5 FAIL in 9 of 10 cells under gender_guesser**, including modern cells. Phase 0.2: commit NamSor on the low-confidence subset per plan §1693. NamSor budget ($0–$500 per §9 cost compass) locked in Phase 0.2.

### 3b — Country coverage (H6)

**H6 FAIL** — paper country coverage averages 5.6% across cells (vs ≥80% threshold). Confirms Check 1f's "country undeterminable for ~55%" finding. **§9e selection-bias correction commitment confirmed** for Phase 0.2; P_demo restriction remains the load-bearing analytical population for demographic-plurality claims.

### 3c — ORCID coverage (H7)

Pre-registered band per cell:
- 1975/1990 cells: <5% (ORCID launched 2012).
- 2005 cells: 5-15%.
- 2015 cells: 15-30%.
- 2024 cells: 25-45%.

| Field | Year | Actual | Pre-reg band | Outcome |
|---|---:|---:|---|---|
| cs | 1975 | 40.0% | [0%, 5%] | ABOVE band |
| cs | 1990 | 0.0% | [0%, 5%] | in band |
| cs | 2005 | 20.0% | [5%, 15%] | ABOVE band |
| cs | 2015 | 60.0% | [15%, 30%] | ABOVE band |
| cs | 2024 | 40.0% | [25%, 45%] | in band |
| physics | 1975 | 20.0% | [0%, 5%] | ABOVE band |
| physics | 1990 | 20.0% | [0%, 5%] | ABOVE band |
| physics | 2005 | 20.0% | [5%, 15%] | ABOVE band |
| physics | 2015 | 80.0% | [15%, 30%] | ABOVE band |
| physics | 2024 | 80.0% | [25%, 45%] | ABOVE band |

## Per-(year, field, name-region) gender coverage (3a diagnostic)

Coarse heuristic name-region tagger; per-region rates are diagnostic, not
load-bearing for the H5 decision rule.

| Field | Year | Name region | N unique authors | Gender ≥0.8 |
|---|---:|---|---:|---:|
| cs | 1975 | anglo_other | 5 | 60.0% |
| cs | 1990 | anglo_other | 5 | 60.0% |
| cs | 2005 | anglo_other | 5 | 40.0% |
| cs | 2015 | anglo_other | 3 | 0.0% |
| cs | 2015 | east_asian | 2 | 0.0% |
| cs | 2024 | anglo_other | 4 | 50.0% |
| cs | 2024 | slavic | 1 | 0.0% |
| physics | 1975 | anglo_other | 5 | 60.0% |
| physics | 1990 | anglo_other | 3 | 33.3% |
| physics | 1990 | east_asian | 1 | 0.0% |
| physics | 1990 | slavic | 1 | 0.0% |
| physics | 2005 | anglo_other | 5 | 80.0% |
| physics | 2015 | anglo_other | 5 | 20.0% |
| physics | 2024 | anglo_other | 4 | 25.0% |
| physics | 2024 | east_asian | 1 | 0.0% |

## Cross-links

- Plan §4 (Demographic features) — H5/H6/H7 outcomes appended inline.
- Plan §9 (Cost gate) — Genderize free-tier usage at $0; logged in `tasks/spend.md`.
- Plan §9a P5 (ORCID validation) — H7 outcomes characterize feasibility of
  the §9a P5 ORCID-validation subsample for gender-inference accuracy
  quantification.
- Plan §9e (Selection-bias correction) — H6 confirms the country-coverage
  gap that §9e's IPW correction addresses.

## Artifacts

- `experiments/phase-0.1/demographic-coverage-smoke.csv` — per-cell rates.
- `experiments/phase-0.1/demographic-coverage-by-region-smoke.csv` — 3a by region.
- `experiments/phase-0.1/check3-author-records-smoke.parquet` — long-form authors.
- `data/metadata/genderize-cache.json` — Genderize response cache (reproducibility).
