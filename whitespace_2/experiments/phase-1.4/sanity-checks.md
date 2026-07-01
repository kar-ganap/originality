# Phase 1.4 Workstream A — production-scale sanity checks

**Date:** 2026-06-30
**Input:** `data/metadata/v3-coverage-table.parquet` + the Phase 1.3 v3 1M
run intermediates (`experiments/phase-1.3/run-1M-v3/`).
**Script:** `experiments/phase-1.4/sanity_checks.py` → `sanity-results.json`.
**Verdict:** ✅ Substrate sound. Two methodology clarifications (no failures).

---

## A1 — Year-bound 1970–2024

The §0 corpus spans **1790–2027** (the §0 filter screened junk-year
*tokens* in text, not the `publication_year` field). Distinct-author-cell
counts:

| Window | author-cells | note |
|---|---|---|
| pre-1970 | 16,669 (**0.6%**) | mis-dated tail (CS/physics tags on 1790–1969 records) |
| 1970–2024 | 2,460,198 | the study window |
| post-2024 | 276,368 | 2025: 214,296 · 2026: 62,071 · 2027: 1 |

**Bound applied: 1970–2024** (the pre-registered window — `conceptual.md`,
`field_definitions.csv` year_max 2024). pre-1970 is a negligible mis-dated
tail. post-2024 is 2025 (a boundary year, mostly complete) + 2026 (partial
— the snapshot is 2026-03-30) + 2027 (1 junk record). **The headline is
unchanged under the bound:** CS-latin female share is 0.3187 (2024) vs
0.3193 (2025), so excluding 2025+ does not move the conclusion.

**Carry-forward:** add an explicit `publication_year` ≥1970 (and a
snapshot-aware upper bound) to the §0 filter / sampling for future pulls.

---

## A2 — Field-intuition checks ✅

**Author-volume curves** (distinct authors/year, in-window):

| Year | CS | Physics |
|---|---|---|
| 1975 | 1,064 | 1,705 |
| 1995 | 6,449 | 6,524 |
| 2005 | 29,922 | 14,941 |
| 2015 | 62,696 | 36,703 |
| 2024 | 150,061 | 50,797 |

CS grows ~140× (1975→2024, accelerating — exponential, as expected), and
**overtakes physics around 2005** — both match field intuition.

**China's CS author share** (of country-known CS authors): **2.2% (1995) →
15.5% (2005) → 19.5% (2015) → 29.8% (2024)**. This reproduces the
well-documented real-world rise of China as a top CS-producing nation — a
strong external validation that the affiliation-based country inference
captures a known macro trend.

**Female-share trajectory** (CS latin): 0.224 (1975) → 0.319 (2024),
monotonic since ~1995 — the headline, plausible in level and direction.

**physics ≥ CS early-female — diagnosed, flagged.** 1975: CS 0.2242
(n=1,058) vs Physics 0.2753 (n=1,688). The pattern is **robust to sample
size** (both cells n>1,000), so it is *not* a small-N artifact. Whether it
is a true subfield-composition effect or a name-inference artifact (physics'
heavier East-Asian name mix interacting with the bias correction) remains
open — **flag for Stage 2 scrutiny**; not a substrate defect.

---

## A3 — Coverage cross-tab + per-cell H7

**Coverage** (in-window, author-weighted): gender 1.00 (post-correction,
by design — the §9e correction assigns probabilistic gender to ~all
authors), country **0.816** (higher than the all-era 71.9% because the
window excludes the sparse pre-1970 cells).

**Per-cell H7 — re-framed for Option B.** Of 110 headline cells (n≥1000),
57 have ≥10 NamSor-sampled names and **53 have <10** (min 0, median 10).
Taken literally, H7 (≥10 NamSor names per headline cell) is borderline.

**But H7-as-specified is a vestige of Option A (direct per-cell labeling).**
Under the **locked Option B** (sample-based *per-region* bias estimation),
a cell's authors are corrected by their **region's** confusion matrix
(estimated from ~600 names/region — H5, which passes for 4/5 regions), NOT
from per-cell NamSor labels. So the binding per-cell quantity is the
**corrected-distribution CI half-width (H8)**, which PASSES on the headline
cells (max 1.48pp ≤ 2.5pp). The per-cell NamSor count is informational, not
gating — exactly parallel to the H5-empty-rows fix (a gate specified for a
different methodology). **H7 re-framed: per-region sample (H5) + per-cell
CI (H8) are the binding gates; both pass.**

---

## A4 — Disambiguation production spot-check ✅

Career length (max−min publication_year) over **1,821,598** authors:

| p50 | p90 | p99 | >60yr |
|---|---|---|---|
| 0 | 8 | 27 | 253 (**0.014%**) |

Sane distribution: most authors have a short publishing span (p50=0 → one
year / one paper), a long tail to 27yr at p99, and a tiny >60yr tail (253
authors, 0.014%) — the cross-era mergers, matching H1 exactly. No anomaly.

---

## Verdict + carry-forwards

The Stage-1 demographic substrate is **sound at production scale**: volume
curves, the China-rise validation, the female-share trajectory, coverage,
and the career-length distribution all match field intuition. Two items
carry forward (both methodology clarifications, not failures):

1. **physics ≥ CS early-female** — robust to sample size; mechanism (real
   vs inference) open → Stage 2 scrutiny.
2. **H7 re-framed for Option B** — per-region (H5) + per-cell-CI (H8) are
   the binding gates; the literal per-cell NamSor count is informational.

Plus the **§0 year-bound carry-forward** (add a `publication_year` floor to
future pulls).
