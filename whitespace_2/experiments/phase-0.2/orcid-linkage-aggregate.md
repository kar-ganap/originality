# Phase 0.2 Wave 3A — ORCID-linkage aggregation

**Run date:** 2026-05-05
**Snapshot:** 2026-05-05T08:10:59+00:00
**Audit input:** `experiments/phase-0.2/orcid-linkage-audit-input.csv`
**N rows:** 100 (decisive: 72; unclear: 28; unaudited: 0; unknown: 0)

**Methodology (Reading B):** unclear EXCLUDED from numerator and denominator. Rate = (yes+likely) / (yes+likely+no).

## Overall linkage-correctness rate

- **98.6%** (71 yes/likely / 72 decisive)
- §4 threshold: ≥70%
- **Result: ✅ PASS**

## Per-region rate

| Region | N total | N decisive | Rate | Status |
|---|---:|---:|---:|---|
| anglo | 2 | 2 | 100.0% | PASS |
| other | 77 | 56 | 100.0% | PASS |
| slavic | 5 | 4 | 100.0% | PASS |
| south_asian | 2 | 1 | 100.0% | PASS |
| east_asian | 14 | 9 | 88.9% | PASS |

§4 per-region threshold: ≥50%

## §9a P5 implication

**No restriction needed.** All §4 thresholds met; §9a P5 ground-truth subsample usable across all regions.

## Decision

Wave 3A acceptance gate met. §9a P5 ground-truth subsample is usable per the per-region restrictions above.

## Artifacts

- `experiments/phase-0.2/orcid-linkage-aggregate.md` — this artifact
- `experiments/phase-0.2/orcid-linkage-aggregate-summary.json` — machine summary
- `experiments/phase-0.2/orcid-linkage-audit-input.csv` — audit input
- `experiments/phase-0.2/orcid_linkage_aggregate.py` — this script
