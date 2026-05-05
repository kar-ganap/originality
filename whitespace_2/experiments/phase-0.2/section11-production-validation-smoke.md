# Phase 0.2 Wave 2A — §11 production-scale re-validation

**Run date:** 2026-05-04
**Snapshot:** 2026-05-04T21:37:44+00:00
**Mode:** SMOKE
**Device:** mps; **dtype:** fp16

## Headline

**Wave 2A gate: FAIL**

H7' FAILED at all K∈[25, 15, 35]. BLOCK Stage 1 transition; trigger plan revision.

## Pull summary

| Set | Target | Actual | Notes |
|---|---:|---:|---|
| Stratified pool S | 150 | 150 | per-decade × 6 |
| Unstratified pool U | 150 | 150 | Nᵧ-proportional 1970-2024 |
| Held-out H_1975 | 15 | 15 | cs 1975 only |
| Held-out H_2020 | 15 | 15 | cs 2020 only |

Pairwise disjoint; all |X|≥H1 thresholds: PASS.

Pull wall-clock: 16s.

## Embedding summary

| Set | N | Mean L2 norm |
|---|---:|---:|
| S | 150 | 21.92 |
| U | 150 | 21.97 |
| H_1975 | 15 | 21.93 |
| H_2020 | 15 | 21.99 |

H2 (correctness): PASS.
Norm band per Phase 0.1.E: [21.0, 23.0].

Embedding wall-clock: 99s
(0.301 s/abs).

## H7' results across K

H7' = effN_S(H_1975) > 1.43 × effN_U(H_1975) (artifact)
AND |effN_S(H_2020) − effN_U(H_2020)| / max < 0.2 (NC).

| K | S/H75 | U/H75 | ratio | art? | S/H20 | U/H20 | NC rd | NC? | overall |
|---|---:|---:|---:|---|---:|---:|---:|---|---|
| K=25 | 5.53 | 8.00 | 0.69 | NO | 8.00 | 9.67 | 0.173 | YES | **FAIL** |
| K=15 | 5.53 | 6.09 | 0.91 | NO | 6.09 | 5.95 | 0.022 | YES | **FAIL** |
| K=35 | 8.62 | 6.42 | 1.34 | NO | 8.62 | 10.98 | 0.215 | NO | **FAIL** |

Cluster-fit wall-clock: 2s.

## Acceptance gate

Per `phase-0.2-execution.md` Wave 2A acceptance:
- H7' PASS at K=25 primary → §11 validated; proceed to Stage 1.
- H7' PASS at K∈[15, 35] only → robustness sweep flag.
- H7' FAIL at all K → BLOCK Stage 1 transition.

**Result: FAIL**

H7' FAILED at all K∈[25, 15, 35]. BLOCK Stage 1 transition; trigger plan revision.

## Wall-clock summary

| Stage | Time |
|---|---:|
| Pulls | 16s |
| Embedding | 99s |
| Cluster fit + H7' | 2s |
| **Total** | **117s** |

## Cluster-fit manifest

Per §11 commitment: centroids committed for reproducibility.

- K=25: `section11-cluster-fit-S-K25-smoke.npy`, `section11-cluster-fit-U-K25-smoke.npy`
- K=15: `section11-cluster-fit-S-K15-smoke.npy`, `section11-cluster-fit-U-K15-smoke.npy`
- K=35: `section11-cluster-fit-S-K35-smoke.npy`, `section11-cluster-fit-U-K35-smoke.npy`


## Artifacts

- `experiments/phase-0.2/section11-production-validation-smoke.md` — this artifact
- `data/metadata/section11-prod-{S,U,H_1975,H_2020}-smoke.parquet` — pulled metadata
- `data/metadata/section11-prod-{S,U,H_1975,H_2020}-vec-smoke.npy` — SPECTER2 vectors
- `data/metadata/section11-cluster-fit-{S,U}-K{30,50,100}-smoke.npy` — cluster centroids
- `experiments/phase-0.2/section11_production_validation.py` — this script
