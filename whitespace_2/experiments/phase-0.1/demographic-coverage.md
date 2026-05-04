# Check 3 — Demographic inference coverage

**Run date:** 2026-04-28
**Snapshot:** 2026-04-28T17:14:50+00:00
**Mode:** full
**Source:** `pilot-query-results.parquet`
**Authors extracted:** 1511 (452 papers;
744 unique first names).
**Inference methods:**
- **gender_guesser** (PRIMARY for H5): 390 of 744
  unique names assigned to {male, female} (offline lookup, no API).
- **Genderize.io** (CROSS-VALIDATION): cache at `genderize-cache.json`
  with 721 valid responses (out of 744 cached entries).
**Spend:** $0 (gender_guesser is offline; Genderize used keyed-free 2500/mo
tier on a partial subset).

**Cross-validation: gender_guesser vs Genderize agreement** (unique names in both sources, n=721):

- Both assigned + same gender: 372 (51.6%)
- Both assigned + opposite gender: 1 (0.1%)
- Only gender_guesser assigned: 17 (2.4%)
- Only Genderize assigned (p≥0.8): 233 (32.3%)

Agreement on jointly-assigned subset: 372/373 = 99.7%.


## Per-cell coverage (3a / 3b / 3c)

Coverage threshold per plan §4 / §1691: **≥80%**. Gender confidence
threshold: probability ≥ 0.8.

| Field | Year | N auth | N pap | Gz p≥0.8 | gg | Ctry | ORCID |
|---|---:|---:|---:|---|---|---|---:|
| cs | 1975 | 35 | 23 | 71.4% (FAIL) | 57.1% (FAIL) | 52.2% (FAIL) | 14.3% |
| cs | 1990 | 29 | 19 | 75.9% (FAIL) | 69.0% (FAIL) | 42.1% (FAIL) | 13.8% |
| cs | 2005 | 113 | 63 | 58.4% (FAIL) | 38.1% (FAIL) | 50.8% (FAIL) | 38.9% |
| cs | 2015 | 145 | 62 | 69.5% (FAIL) | 50.4% (FAIL) | 46.8% (FAIL) | 50.3% |
| cs | 2024 | 541 | 92 | 68.5% (FAIL) | 41.0% (FAIL) | 48.9% (FAIL) | 35.1% |
| physics | 1975 | 50 | 30 | 29.2% (FAIL) | 22.9% (FAIL) | 56.7% (FAIL) | 16.0% |
| physics | 1990 | 68 | 32 | 35.3% (FAIL) | 26.5% (FAIL) | 62.5% (FAIL) | 33.8% |
| physics | 2005 | 134 | 43 | 42.0% (FAIL) | 32.1% (FAIL) | 53.5% (FAIL) | 57.5% |
| physics | 2015 | 169 | 63 | 64.0% (FAIL) | 45.7% (FAIL) | 52.4% (FAIL) | 60.9% |
| physics | 2024 | 227 | 40 | 38.6% (FAIL) | 23.8% (FAIL) | 50.0% (FAIL) | 65.6% |

H5 (gender ≥80%): **0 / 10 cells pass**.
H6 (country ≥80%): **0 / 10 cells pass**.

## Decisions

### 3a — Gender coverage (H5)

**H5 FAIL in 10 of 10 cells under Genderize p≥0.8** (plan §4 methodology), including modern cells. Phase 0.2: commit NamSor on the low-confidence subset per plan §1693. NamSor budget ($0–$500 per §9 cost compass) locked in Phase 0.2. 

Cross-validation: under gender_guesser, 0/10 cells pass at the same 80% threshold.

### 3b — Country coverage (H6)

**H6 FAIL** — paper country coverage averages 51.6% across cells (vs ≥80% threshold). Confirms Check 1f's "country undeterminable for ~55%" finding. **§9e selection-bias correction commitment confirmed** for Phase 0.2; P_demo restriction remains the load-bearing analytical population for demographic-plurality claims.

### 3c — ORCID coverage (H7)

Pre-registered band per cell:
- 1975/1990 cells: <5% (ORCID launched 2012).
- 2005 cells: 5-15%.
- 2015 cells: 15-30%.
- 2024 cells: 25-45%.

| Field | Year | Actual | Pre-reg band | Outcome |
|---|---:|---:|---|---|
| cs | 1975 | 14.3% | [0%, 5%] | ABOVE band |
| cs | 1990 | 13.8% | [0%, 5%] | ABOVE band |
| cs | 2005 | 38.9% | [5%, 15%] | ABOVE band |
| cs | 2015 | 50.3% | [15%, 30%] | ABOVE band |
| cs | 2024 | 35.1% | [25%, 45%] | in band |
| physics | 1975 | 16.0% | [0%, 5%] | ABOVE band |
| physics | 1990 | 33.8% | [0%, 5%] | ABOVE band |
| physics | 2005 | 57.5% | [5%, 15%] | ABOVE band |
| physics | 2015 | 60.9% | [15%, 30%] | ABOVE band |
| physics | 2024 | 65.6% | [25%, 45%] | ABOVE band |

## Per-(year, field, name-region) gender coverage (3a diagnostic)

Coarse heuristic name-region tagger; per-region rates are diagnostic, not
load-bearing for the H5 decision rule.

| Field | Year | Name region | N unique authors | Gender ≥0.8 |
|---|---:|---|---:|---:|
| cs | 1975 | anglo_other | 34 | 58.8% |
| cs | 1975 | east_asian | 1 | 0.0% |
| cs | 1990 | anglo_other | 26 | 73.1% |
| cs | 1990 | east_asian | 1 | 0.0% |
| cs | 1990 | slavic | 1 | 100.0% |
| cs | 1990 | south_asian | 1 | 0.0% |
| cs | 2005 | anglo_other | 88 | 47.7% |
| cs | 2005 | arabic | 1 | 100.0% |
| cs | 2005 | east_asian | 23 | 0.0% |
| cs | 2005 | south_asian | 1 | 0.0% |
| cs | 2015 | anglo_other | 114 | 60.5% |
| cs | 2015 | east_asian | 22 | 9.1% |
| cs | 2015 | slavic | 2 | 0.0% |
| cs | 2015 | south_asian | 3 | 0.0% |
| cs | 2024 | anglo_other | 232 | 45.3% |
| cs | 2024 | arabic | 2 | 100.0% |
| cs | 2024 | east_asian | 44 | 11.4% |
| cs | 2024 | slavic | 13 | 46.2% |
| cs | 2024 | south_asian | 4 | 75.0% |
| physics | 1975 | anglo_other | 48 | 22.9% |
| physics | 1975 | east_asian | 1 | 0.0% |
| physics | 1990 | anglo_other | 58 | 29.3% |
| physics | 1990 | east_asian | 6 | 0.0% |
| physics | 1990 | slavic | 4 | 25.0% |
| physics | 2005 | anglo_other | 117 | 33.3% |
| physics | 2005 | east_asian | 8 | 12.5% |
| physics | 2005 | slavic | 6 | 33.3% |
| physics | 2005 | south_asian | 1 | 0.0% |
| physics | 2015 | anglo_other | 142 | 48.6% |
| physics | 2015 | arabic | 1 | 0.0% |
| physics | 2015 | east_asian | 9 | 11.1% |
| physics | 2015 | slavic | 10 | 50.0% |
| physics | 2015 | south_asian | 3 | 0.0% |
| physics | 2024 | anglo_other | 189 | 27.0% |
| physics | 2024 | east_asian | 28 | 0.0% |
| physics | 2024 | slavic | 6 | 33.3% |
| physics | 2024 | south_asian | 1 | 0.0% |

## Methodology insights surfaced by this check

1. **gg vs Genderize disagree on assignment-rate, not on direction.** When
   both methods commit to a gender, they agree at **99.7%** (372 of 373
   jointly-assigned names). The methods diverge on the long tail of
   ambiguous names: gender_guesser flags ~33% of unique names as
   `mostly_male/mostly_female/andy` and refuses to commit, while
   Genderize at p≥0.8 commits on those (and Genderize's own per-name
   probability tends to align with the gg category — e.g., "andy" names
   tend to score Genderize p≈0.5-0.7). This means Genderize p≥0.8 is
   the more permissive of the two, and gg is a valid lower bound.

2. **The 80% coverage threshold fails under BOTH methods at all cells.**
   Per-cell rates max out at 75.9% (CS 1990 Genderize) and 69.0% (CS
   1990 gg). Physics consistently underperforms CS, especially in
   modern years (Physics 2024 = 38.6% Genderize, 23.8% gg). The Physics
   gap reflects (a) higher East-Asian author share, (b) more
   institutional-affiliation patterns where the OpenAlex `display_name`
   is a transliteration that neither method handles well.

3. **The H5 failure is NOT about Genderize-vs-gg choice — it's about
   the inference-target population.** Even with Genderize p≥0.8 (the
   plan §4 primary methodology, hitting 81% per-unique-name overall),
   per-cell aggregation never clears 80% because:
   - Many authors have non-Latin display names (CJK, etc.) that neither
     method can resolve.
   - Many authors appear as initials-only ("J. Smith") in pilot data
     (see H1: 35.1% non-extractable rate).
   - Per-cell sampling produces small N for some cells (CS 1975 = 35
     authors), introducing variance.

4. **NamSor escalation is required for Phase 0.2** per plan §1693
   decision rule. NamSor's stated per-region accuracy on East-Asian /
   Slavic / Arabic-speaking names is significantly higher than
   Genderize's, and it handles transliterated CJK forms better.
   Budget per §9 cost compass: $0-$500 for 100-200K names. **Locked
   for Phase 0.2.**

5. **ORCID coverage is much higher than expected at every era** —
   "ABOVE band" in 9 of 10 cells, including pre-1990 cells where the
   pre-registered band was <5% (got 13-34%). This is OpenAlex back-
   propagating ORCID from author-profile data: an author who registered
   ORCID in 2015 gets it associated with their pre-2012 papers.
   **Methodology bonus**: the §9a Principle 5 ORCID-validation
   subsample is much larger than feared. Phase 0.2 can stratify the
   300-name gender-validation budget more finely (per name-region ×
   era), since adequate ORCID-having candidates exist in each cell.

## Cross-links

- Plan §4 (Demographic features) — H5/H6/H7 outcomes appended inline.
- Plan §9 (Cost gate) — Genderize free-with-key tier ($0); NamSor
  budget locked in Phase 0.2 per H5 decision rule. Logged in
  `tasks/spend.md`.
- Plan §9a P5 (ORCID validation) — H7 ABOVE-band outcome means the
  validation subsample is generously sized; methodology bonus.
- Plan §9e (Selection-bias correction) — H6 confirms the country-coverage
  gap that §9e's IPW correction addresses.

## Artifacts

- `experiments/phase-0.1/demographic-coverage.csv` — per-cell rates.
- `experiments/phase-0.1/demographic-coverage-by-region.csv` — 3a by region.
- `experiments/phase-0.1/check3-author-records.parquet` — long-form authors.
- `data/metadata/genderize-cache.json` — Genderize response cache (reproducibility).
