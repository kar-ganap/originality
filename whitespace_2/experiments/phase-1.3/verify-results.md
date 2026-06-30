# Phase 1.3 — VERIFY results (v3 production run)

**Run date:** 2026-06-30
**Population:** v3 §0 1M production sample (`section0-sample-1M-v3.parquet`,
exactly 1,000,000 papers — the set Stage 2 embeds; per the user-locked
"1M now, full corpus later if needed" decision).
**Driver:** `experiments/phase-1.3/run_pipeline.py` (commit `6e43902`),
chaining Steps 1→6 end to end.
**Compute:** local (single process), 1034 s (~17 min) wall-clock.
**Snapshot:** OpenAlex 2026-03-30 bulk dump (per Phase 1.2 manifest).

---

## Headline result — the demographic-plurality time series

This is the deliverable Phase 1.3 exists to produce. Bias-corrected
female share among **distinct CS authors (latin script)**:

| Year | CS female share (±95% CI half-width, n) | Physics female share |
|---|---|---|
| 1975 | 0.224 ±0.0148 (n=1,058) | 0.275 ±0.0083 (n=1,688) |
| 1985 | 0.236 ±0.0115 | 0.283 ±0.0066 |
| 1995 | 0.231 ±0.0071 | 0.280 ±0.0048 |
| 2005 | 0.258 ±0.0031 | 0.298 ±0.0036 |
| 2015 | 0.279 ±0.0024 | 0.325 ±0.0024 |
| 2020 | 0.299 ±0.0019 | 0.328 ±0.0023 |
| 2025 | 0.319 ±0.0014 (n=157,385) | 0.320 ±0.0020 |

**CS female share rose ~10pp (22.4% → 31.9%) over 1975–2025**, monotonic
since ~1995, tightly estimated (CI half-width 1.5pp → 0.14pp as n grows).
Physics started higher (~27.5%) and rose more slowly, so CS converged up
to physics by 2025. Geographic diversity (`country_shannon`, latin,
distinct) roughly doubled then plateaued: CS 1.64 (1975) → 3.23 (2015) →
2.97 (2025); physics 1.91 → 3.11 → 3.04.

This is the **demographic** plurality series. The Stage-2 divergence test
asks whether **semantic** plurality tracked this rise or decoupled from it.

**Robustness — unit choice barely matters.** 2024 CS latin female share:
0.3187 (distinct authors) vs 0.3164 (authorship appearances) — a 0.23pp
gap, so prolific authors are not materially gender-skewed.

---

## Pre-registered hypothesis verdicts

| # | Hypothesis | Threshold | Measured | Verdict |
|---|---|---|---|---|
| H1 | Cross-era-merger rate | ≤ 5% | **0.014%** (253 / 1.82M authors) | ✅ PASS |
| H2 | ORCID agreement | ≥ 95% | **99.62%** | ✅ PASS |
| H3 | Gender coverage (confident) | ≥ 45% | **41.5%** overall | 🟡 NEAR-MISS |
| H4 | Country coverage | ≥ 50% | **71.9%** | ✅ PASS |
| H5 | Per-region NamSor CI half-width | ≤ 10pp | **4/5 regions pass**; south_asian 32.7pp | 🟡 E1 (1 stratum) |
| H6 | NamSor spend | ≤ $10 | **$0** (23 calls, free tier) | ✅ PASS |
| H7 | NamSor sample per stratum | ≥ 10 | 4 regions 476–607; south_asian = 4 | 🟡 E3 (1 stratum) |
| H8 | Female-share CI half-width (headline cells) | ≤ 2.5pp | **max 1.48pp** (cells n≥1000) | ✅ PASS |

### H3 — gender coverage (near-miss, reframed)

The 41.5% is the **confident direct-assignment** rate (gg + Genderize at
p≥0.8), the plan's H3 metric; the plan itself expected "~45%". It is
dragged down by physics (more East-Asian / transliterated names) and the
pre-1990 initials-only tail. The §9e bias correction then extends a
**probabilistic** gender to the low-confidence remainder: of 1,822,535
authors, 756,023 (41.5%) are confident-identity and 1,066,509 (58.5%) are
bias-corrected (only 3 uncorrectable). So post-correction
`gender_coverage_rate` ≈ 1.00 on the headline cells (NamSor assigns
male/female to nearly all low-conf names; unknown mass ≈ 0). The headline
test uses the corrected distribution, so the marginal H3 miss does not
gate the result — but it is logged honestly as below the pre-registered
45%.

### H8 — passes where it gates

`female_share_ci_halfwidth` by cell size (distinct, all fields):

| min cell n | #cells | max half-width | median |
|---|---|---|---|
| ≥ 0 | 630 | 0.3750 | 0.0014 |
| ≥ 200 | 191 | 0.0301 | 0.0036 |
| ≥ 1000 | 114 | 0.0148 | 0.0044 |
| ≥ 5000 | 69 | 0.0074 | 0.0029 |

The max-over-all 0.375 is tiny old-year / rare-region cells, not headline
cells. Every cell with n≥1000 clears the 2.5pp gate. The headline CS-latin
cells (n up to 157k) sit at 0.14–1.5pp. **H8 holds on the headline cells.**

---

## Escape-trigger evaluation

| Trigger | Condition | Verdict |
|---|---|---|
| **E1** | per-region CI half-width > 10pp | **FIRED — south_asian only** |
| **E2** | headline statistic moves > 30% under kernel-CI perturbation | **NOT FIRED** (rel. spread ~13%) |
| **E3** | < 10 NamSor names in a headline cell | south_asian strata only (benign) |
| **E4** | NamSor quality issue | **NOT FIRED** (0 errors, 23/23 batches clean) |

### E1 — fired for `south_asian`, and it is benign

Per-region confusion-matrix `max_ci_halfwidth` (post the Step-5a fix that
excludes structurally-empty gg rows):

| region | n_sample | max_ci_halfwidth | E1 |
|---|---|---|---|
| latin | 606 | 0.038 | ok |
| cjk | 607 | 0.028 | ok |
| cyrillic | 607 | 0.036 | ok |
| arabic | 476 | 0.043 | ok |
| **south_asian** | **4** | **0.327** | **FIRES** |

The four populous script regions are well-estimated (≤4.3pp). E1 fires for
`south_asian` because only **4 Devanagari-script names exist in the entire
1M sample** — South Asian authors' names are romanized in OpenAlex and
therefore tagged `latin` (which is well-corrected). The stratum is
**population-limited, not under-sampled**: the plan's E1 escalation
("expand the stratified sample") cannot help — there are no more
Devanagari names to draw. This is exactly the risk flagged in the Phase
1.3 handoff ("97.4% of low-conf names are Latin-script"). **No methodology
change is warranted**; the affected population is empirically negligible
and its members are captured (and corrected) in the latin stratum. Logged
as a documented limitation.

### E2 — bias correction is robust (does not fire)

K=200 kernels drawn within the 5a Wilson CIs (`perturb_row_normalized`),
re-applied in memory, headline female_share re-aggregated
(`sensitivity_e2.py`):

| Cell | base | sweep [min, max] | rel. spread | E2 |
|---|---|---|---|---|
| 2020 cs latin | 0.299 | [0.281, 0.319] | 0.126 | ok |
| 2024 cs latin | 0.319 | [0.298, 0.339] | 0.128 | ok |
| 2025 cs latin | 0.319 | [0.299, 0.343] | 0.136 | ok |

Even at the extremes of the kernel uncertainty the female share stays in
~[0.28, 0.34] and the rising trend is preserved — ~13% relative movement,
well under the 30% E2 threshold.

---

## Robustness — axis sensitivity + v2/v3 pair

### Script vs country correction axis (`sensitivity_axis.py`)

Re-running the bias correction keyed on **country** instead of **script**
and comparing the field-level CS female-share trend:

| Year | script-corrected | country-corrected |
|---|---|---|
| 1975 | 0.224 | 0.184 |
| 1995 | 0.229 | 0.196 |
| 2015 | 0.278 | 0.261 |
| 2024 | 0.318 | 0.308 |

Both axes show the **same ~10pp rising trend** (study-window 1970–2024:
max |diff| 4.93pp, mean 3.01pp over 55 years, narrowing over time). The
~3pp level gap is **a confound, not a real axis effect**: the v3 NamSor
sample was *script*-stratified, so the per-country matrix is thin (68
countries, only 16 with n≥10) and only **41.6% of authors are
country-correctable** vs 99.97% under script — the uncorrected 58% stay
"unknown" and depress the country female-share. This **confirms
script-region is the correct primary axis**; a clean country-axis
estimate would need a country-stratified NamSor sample (fresh quota).

### v2 / v3 robustness pair

The full pipeline re-run on the **v2** §0 1M sample (`run_pipeline.py
--reuse-matrix v3-confusion-matrix.json --no-genderize` — the per-region
bias is §0-version-independent, so **zero new API quota**; 14 min).

| | v3 (24.5M-pop filter) | v2 (38.7M-pop filter) |
|---|---|---|
| author-paper rows | 3,124,143 | 2,750,876 |
| unique authors | 1,822,535 | 1,826,052 |
| H1 / H2 | 0.014% / 99.6% | 0.024% / 99.7% |
| H3 confident gender | 41.5% | 43.3% |
| H4 country coverage | 71.9% | 67.3% |
| H8 (cells n≥1000) | max 1.48pp | max 1.46pp |

**The CS female-share trend matches within 1.4pp at every decade**
(v3 vs v2: 1975 0.224/0.218, 1995 0.231/0.237, 2015 0.279/0.291, 2024
0.319/0.327; max |diff| over the listed years = 1.39pp). Both rise ~10pp.
**The headline demographic signal is robust to the §0 filter choice** —
it does not depend on the v2→v3 cleanup (publisher-chrome, concept-score
0.40, abstract-token-50). Deliverable: `data/metadata/
v2-coverage-table.parquet`.

---

## API usage (this run)

- **Genderize:** 2,200 names queried / 220 calls / 0 errors; extended
  3,283 authors beyond gg. Quota cap hit at 2,200 (smoke had used ~200).
- **NamSor:** 189,675 low-confidence names → 2,300 stratified sample →
  2,300 classified / 23 calls / 0 errors. $0 (free tier).
- Month-to-date free-tier usage (incl. smoke): ~2,400 Genderize, ~2,400
  NamSor — both just under the 2,500/mo cap. **A v2 run this month should
  reuse this run's confusion matrix** (per-region bias is §0-version-
  independent) rather than spend fresh NamSor quota.

---

## Surprises / findings

1. **Physics ≥ CS on early female share** (27.5% vs 22.4% in 1975).
   Counter to the usual "CS more diverse than physics" prior. Could be
   real (subfield composition) or a name-inference artifact on physics'
   heavier East-Asian name mix. Flag for scrutiny in the Stage-2 writeup;
   not obviously a bug (the bias correction is applied identically).
2. **The script-region stratification is geography, not nationality.**
   `south_asian` near-empty + `latin` dominant confirms that script ≠
   country: romanized non-Western names live in `latin`. This is why the
   country-region robustness axis (Step 6) exists, and why country
   coverage (71.9%) is the better geographic signal than script.
3. **The Step-5a H5 bug** (empty gg-rows pegging `max_ci_halfwidth` at
   0.5) was caught by the keyed smoke and fixed (commit `a213f42`) before
   this run — without it every region would have spuriously fired E1.
4. **The §0 corpus has a pre-1970 mis-dated tail.** The 1M sample
   contains papers dated back to **1803** with CS/physics concept tags —
   CS didn't exist in 1803, so these are OpenAlex metadata errors. They
   are tiny (1–2-author cells) and negligible in count, but Phase 1.4 /
   Stage 2 should bound the year to the **1970–2024** study window
   (the §0 filter screened junk-year *tokens* in text, not the
   `publication_year` field itself). Surfaced by degenerate country
   female-share (0.0) on those cells in the axis sweep.

---

## What carries to Phase 1.4 / Stage 2

- `data/metadata/v3-coverage-table.parquet` — 630 cells × 2 units, the
  demographic substrate (coverage + female_share + gender_shannon +
  country diversity + CIs).
- `experiments/phase-1.3/v3-confusion-matrix.json` — the per-region
  bias-correction kernel (reusable for the v2 run; §0-version-independent).
- `experiments/phase-1.3/v3-run-summary.json`,
  `v3-sensitivity-e2.json` — measurements.
- Open items for Phase 1.4 / Stage 2: (a) the physics≥CS early-female
  finding to scrutinize; (b) per-cell H7 (the driver reports per-region);
  (c) the script-vs-country **axis sensitivity** (rerun
  `build_coverage_table(region_axis="country")` and compare) — queued;
  (d) the v2 robustness pair (Step 7), with matrix reuse to avoid quota.

---

## Reproducibility

```bash
modal volume get ws2-section0 section0-sample-1M-v3.parquet <local>
uv run python experiments/phase-1.3/run_pipeline.py \
    --source <local>/section0-sample-1M-v3.parquet \
    --outdir experiments/phase-1.3/run-1M-v3 \
    --genderize-max 2200 --namsor-max 2300 --n-bootstrap 10000
uv run python experiments/phase-1.3/sensitivity_e2.py \
    --rundir experiments/phase-1.3/run-1M-v3 --k 200
```

Seeds: NamSor stratified sample `ws2-phase-1.3-namsor-seed-v1`; per-cell
bootstrap `ws2-phase-1.3-cell-bootstrap-seed-v1`; E2 sweep seed 20260630.
Note: Genderize/NamSor are live APIs — re-running draws the same stratified
NAMES (seeded) but the third-party gender verdicts could change if the
services update their models. The committed confusion matrix pins the
verdicts used here.
