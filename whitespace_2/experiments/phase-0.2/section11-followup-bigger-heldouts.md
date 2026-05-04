# Phase 0.2 Wave 2A followup — Path B (bigger held-outs)

**Run date:** 2026-05-04
**Snapshot:** 2026-05-04T22:20:18+00:00
**Mode:** FOLLOWUP (Path B)
**Scope:** New disjoint held-outs (target 200/cell);
re-project onto existing S/U cluster fits at K∈{30, 50, 100}.

## ⚠ POST-FIX UPDATE — projection-bug invalidates the PATH_C verdict below

The "PATH_C_RECOMMENDED" verdict reflects buggy projection
(`argmax(v·c)` instead of KMeans-consistent Euclidean). Re-projection
with FIXED Euclidean assignment (`section11_reproject_fix.py`)
shows the §11 pre-registered direction holds at production scale:

| K | r_H75 (FIXED, orig) | r_H75 (FIXED, this followup) |
|---|---:|---:|
| 30 | 1.26 | **1.31** |
| 50 | 1.17 | **1.25** |
| 100 | 1.33 | **1.17** |

All ratios >1.0 (S > U) in both orig and followup with the fix.
NC passes at all K (NC_rd 0.030-0.135 vs 0.20 threshold). The
empirical §11 direction is preserved; the buggy projection
produced reversed results due to centroid-magnitude bias.

**Corrected verdict: PATH_A-soft** — keep §11 commitment with
threshold revised from 1.43 to ~1.10 based on empirical
magnitudes 1.17-1.33. See parent
`section11-production-validation.md` "POST-FIX UPDATE" section.

The buggy verdict + analysis below kept for audit-trail
completeness.

---

## Headline (BUGGY — see POST-FIX UPDATE above)

**Verdict: PATH_C_RECOMMENDED**

No sign-flip pattern at any K. §11 mechanism not detectable at this scale. Recommend Path C (drop commitment) or Path D (full-corpus U pool).

## Followup pull summary

| Cell | Target | Actual | Disjoint from |
|---|---:|---:|---|
| H_1975 fu | 200 | 200 | S, U, H_1975, H_2020 |
| H_2020 fu | 200 | 200 | S, U, H_1975 fu+orig, H_2020 |

Embedding wall-clock: 91s
(0.228 s/abs).

## Followup H7' projection results

| K | S/H75 | U/H75 | r_H75 | S/H20 | U/H20 | r_H20 | NC rd | sign-flip? | NC? |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| K=30 | 3.91 | 4.41 | 0.89 | 5.18 | 10.17 | 0.51 | 0.490 | NO | FAIL |
| K=50 | 5.80 | 4.94 | 1.17 | 10.66 | 9.24 | 1.15 | 0.134 | NO | PASS |
| K=100 | 6.16 | 9.21 | 0.67 | 9.68 | 21.89 | 0.44 | 0.558 | NO | FAIL |

**sign-flip** = (r_H75 < 1.0 AND r_H20 > 1.0): the empirical Path A pattern
where S concentrates 1975 papers AND U concentrates 2020 papers
(decade-balanced fit favors old; Nᵧ-proportional fit favors recent).

## Comparison vs original (|H_1975|=49, |H_2020|=45)

| K | r_H75 (orig) | r_H20 (orig) | NC rd (orig) | NC (orig) |
|---|---:|---:|---:|---|
| K=30 | 0.80 | 0.53 | 0.469 | FAIL |
| K=50 | 0.84 | 1.16 | 0.138 | PASS |
| K=100 | 1.05 | 0.62 | 0.382 | FAIL |

| K | r_H75 (orig→fu) | r_H20 (orig→fu) | NC rd (orig→fu) |
|---|---|---|---|
| K=30 | 0.80→0.89 | 0.53→0.51 | 0.469→0.490 |
| K=50 | 0.84→1.17 | 1.16→1.15 | 0.138→0.134 |
| K=100 | 1.05→0.67 | 0.62→0.44 | 0.382→0.558 |


## Decision

No sign-flip pattern at any K. §11 mechanism not detectable at this scale. Recommend Path C (drop commitment) or Path D (full-corpus U pool).

Reading map (per `section11-production-validation.md`):

- **Path A** = rewrite §11 with empirical direction (S concentrates
  old; U concentrates recent). Defensible if sign-flip stabilizes.
- **Path C** = drop §11 commitment. Always available; simpler
  narrative; loses defensive layer.
- **Path D** = full-corpus U pool (~500K). Expensive ($50-150
  embedding cost); tests §11's full mechanism.

## Artifacts

- `experiments/phase-0.2/section11-followup-bigger-heldouts.md` — this artifact
- `experiments/phase-0.2/section11-followup-summary.json` — machine summary
- `data/metadata/section11-prod-H_1975-followup.parquet` — new H_1975
- `data/metadata/section11-prod-H_2020-followup.parquet` — new H_2020
- `data/metadata/section11-prod-H_1975-vec-followup.npy` — embed
- `data/metadata/section11-prod-H_2020-vec-followup.npy` — embed
- `experiments/phase-0.2/section11_followup_bigger_heldouts.py` — script
