# Phase 0.2 Wave 3A — ORCID-linkage hand-audit prep

**Run date:** 2026-05-04
**Snapshot:** 2026-05-04T21:49:39+00:00
**Pool:** Check 5a pilot parquet — 632 unique ORCID-having authors
**Sample:** 100 records (random, seed=17; heuristic region annotation only — too sparse to stratify on, see prep script docstring)

## Pre-audit signals (auto-computed)

| Signal | Count | % |
|---|---:|---:|
| Name similarity ≥0.85 | 83 | 83.0% |
| Institution match (≥0.6 sim) | 38 | 38.0% |
| Publication DOI match | 20 | 20.0% |
| ORCID fetch error | 0 | 0.0% |

## Sampling distribution by name-region heuristic

| Region | N |
|---|---:|
| other | 77 |
| east_asian | 14 |
| slavic | 5 |
| south_asian | 2 |
| anglo | 2 |

## How to hand-audit

Open `orcid-linkage-audit-input.csv`. Each row has:
- `orcid_url` — click to open the ORCID profile
- `openalex_display_name` vs `orcid_full_name` + `name_similarity`
  (auto-computed)
- `openalex_institutions` vs `orcid_employments` + `orcid_educations`
  + `institution_match` (auto-computed)
- `openalex_paper_doi` vs `publication_doi_match` (auto-computed)
- `linkage_correct` (USER FILLS): `yes` / `likely` / `unclear` / `no`
- `notes` (USER FILLS): any context

**Decision rule** (suggested):
- All three signals match (high name sim + inst match + DOI match):
  → `yes`, no need to open ORCID profile
- Two of three match: → `likely`, brief profile glance
- One of three matches: → `unclear`, full profile read
- Zero match (or fetch error): → `unclear`/`no`, investigate

Aggregate per-region linkage-correctness rate; this becomes the
input to Phase 0.2 plan §4 ORCID-linkage validation. If overall
rate <70% or any region <50%, §9a P5 ground-truth methodology
opens for revision.

## Artifacts

- `experiments/phase-0.2/orcid-linkage-audit-input.csv` — hand-audit
  input (one row per sampled author, all comparison signals
  pre-computed; user fills `linkage_correct` + `notes`)
- `experiments/phase-0.2/orcid-linkage-prep.md` — this artifact
- `experiments/phase-0.2/orcid_linkage_prep.py` — this script
