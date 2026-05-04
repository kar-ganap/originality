# Phase 0.2 Wave 2A — §11 production-scale re-validation

**Run date:** 2026-05-04
**Snapshot:** 2026-05-04T21:40:38+00:00
**Mode:** FULL
**Device:** mps; **dtype:** fp16

## Headline

**Wave 2A gate: FAIL**

H7' FAILED at all K∈[50, 30, 100]. BLOCK Stage 1 transition; trigger plan revision.

## Pull summary

| Set | Target | Actual | Notes |
|---|---:|---:|---|
| Stratified pool S | 1500 | 1500 | per-decade × 6 |
| Unstratified pool U | 1500 | 1482 | Nᵧ-proportional 1970-2024 |
| Held-out H_1975 | 50 | 49 | cs 1975 only |
| Held-out H_2020 | 50 | 45 | cs 2020 only |

Pairwise disjoint; all |X|≥H1 thresholds: PASS.

Pull wall-clock: 96s.

## Embedding summary

| Set | N | Mean L2 norm |
|---|---:|---:|
| S | 1500 | 21.95 |
| U | 1482 | 21.97 |
| H_1975 | 49 | 21.91 |
| H_2020 | 45 | 21.95 |

H2 (correctness): PASS.
Norm band per Phase 0.1.E: [21.0, 23.0].

Embedding wall-clock: 1296s
(0.421 s/abs).

## H7' results across K

H7' = effN_S(H_1975) > 1.43 × effN_U(H_1975) (artifact)
AND |effN_S(H_2020) − effN_U(H_2020)| / max < 0.2 (NC).

| K | S/H75 | U/H75 | ratio | art? | S/H20 | U/H20 | NC rd | NC? | overall |
|---|---:|---:|---:|---|---:|---:|---:|---|---|
| K=50 | 3.43 | 4.09 | 0.84 | NO | 7.93 | 6.83 | 0.138 | YES | **FAIL** |
| K=30 | 3.13 | 3.91 | 0.80 | NO | 4.87 | 9.17 | 0.469 | NO | **FAIL** |
| K=100 | 5.47 | 5.22 | 1.05 | NO | 8.18 | 13.22 | 0.382 | NO | **FAIL** |

Cluster-fit wall-clock: 41s.

## Acceptance gate

Per `phase-0.2-execution.md` Wave 2A acceptance:
- H7' PASS at K=50 primary → §11 validated; proceed to Stage 1.
- H7' PASS at K∈[30, 100] only → robustness sweep flag.
- H7' FAIL at all K → BLOCK Stage 1 transition.

**Result: FAIL**

H7' FAILED at all K∈[50, 30, 100]. BLOCK Stage 1 transition; trigger plan revision.

## Wall-clock summary

| Stage | Time |
|---|---:|
| Pulls | 96s |
| Embedding | 1296s |
| Cluster fit + H7' | 41s |
| **Total** | **1433s** |

## Cluster-fit manifest

Per §11 commitment: centroids committed for reproducibility.

- K=50: `section11-cluster-fit-S-K50.npy`, `section11-cluster-fit-U-K50.npy`
- K=30: `section11-cluster-fit-S-K30.npy`, `section11-cluster-fit-U-K30.npy`
- K=100: `section11-cluster-fit-S-K100.npy`, `section11-cluster-fit-U-K100.npy`

## Analysis & interpretation (post-result amendment)

The bare "FAIL at all K" headline understates a methodologically
interesting partial-null. The pre-registered hypothesis predicted
**effN_S(H_1975) > effN_U(H_1975)** — that the stratified fit
spreads pre-1990 papers across MORE clusters because S has
dedicated old-decade clusters that "carry" 1975 topical content.

The empirical direction is the OPPOSITE: at all three K values,
**effN_S < effN_U for H_1975**:

- K=50: 3.43 vs 4.09 (S concentrates 1975 by 16%)
- K=30: 3.13 vs 3.91 (S concentrates 1975 by 20%)
- K=100: 5.47 vs 5.22 (~unity)

But the K=50 result also shows the **opposite direction for
H_2020**:

- K=50: effN_S/H20 = 7.93, effN_U/H20 = 6.83 (S DISPERSES 2020 by 16%)

So at K=50 (the only K where the negative-control passes),
there's a **coherent asymmetric stratification artifact**:
- S concentrates 1975 papers (because S has dedicated old-era
  clusters that 1975 papers fall tightly into)
- U concentrates 2020 papers (because U is Nᵧ-proportional and
  thus dominated by recent topics, giving 2020 papers natural
  cluster homes)

The §11 mechanism IS detectable — the test just had the wrong
directional pre-registration. The artifact is "S favors old-era
cluster identity; U favors recent-era cluster identity," visible
as the SIGN-FLIP of effN_S/effN_U between H_1975 and H_2020.

### Three readings of this result

**Reading A — §11 pre-reg direction was wrong; underlying
mechanism real.** The K=50 sign-flip pattern (S concentrates
old, U concentrates recent) is consistent and methodologically
reasonable. Update §11 to predict the sign-flip rather than
strict effN_S > effN_U.
- Pro: salvages §11; documents an empirically-honest finding.
- Con: post-hoc methodology revision after pre-registration is
  reviewer-suspect.

**Reading B — Test framework is small-N noise-dominated even at
production scale.** With |H_1975|=49 papers projected onto K=50
clusters, expected effN under uniform projection is ~25-40 not
~3-4. The observed 3-4 means projections are highly concentrated
in both fits; distinguishing the 0.84 ratio from sampling noise
requires a much larger held-out (e.g., 200-500 papers per cell).
- Pro: explains the K=30 / K=100 negative-control failures.
- Con: requires another production-scale run with bigger
  held-outs (~1500 raw papers per held-out cell, ~20-40 min more
  embedding compute).

**Reading C — §11's load-bearing claim is empirically weak.**
If neither the strict direction nor the asymmetric direction
reproduces robustly across K, the §11 stratification commitment
may not be necessary. Stage 1 can proceed with unstratified
SPECTER2 sweep + report the result; if reviewers ask "why no
decade stratification?", the answer becomes "we tested at
production scale; the artifact wasn't reliably detectable, so
stratification doesn't add value here."
- Pro: simplest path forward; removes a methodology commitment
  whose empirical basis is now uncertain.
- Con: gives up a defensive layer against a plausible reviewer
  objection ("did you check whether decade-imbalance affects
  cluster fit?").

### What's NOT in question

These results do NOT undermine:
- §0 analytical population (independent of §11)
- Test I/II/III/IV pre-registrations (don't depend on §11)
- §9 demographic-uncertainty stack (orthogonal)
- The Stage 1 → Stage 2 → Stage 3 stage gates (all use Test I
  divergence directly, not §11 cluster-fit projections)

The §11 commitment was specifically a defense against a SUBSET
of methodology critiques about decade representation in cluster
fits. Its weakening doesn't propagate to the headline tests.

### Recommended next step

User judgment moment. Options:

1. **Bigger held-outs, re-run.** ~30 min more compute; if
   Reading B holds, the test stabilizes and gives clean direction.
2. **Lock Reading A; rewrite §11 with empirical direction.**
   Phase 0.2 plan amendment; document this as a methodology note.
3. **Drop §11 stratification commitment.** Phase 0.2 plan
   amendment; simpler narrative. Document this dry-run result
   as "we tested at production scale; artifact not robust;
   don't lock §11."

This is exactly the R1 risk flagged in
`docs/phases/phase-0.2-execution.md` Wave 2A. Per
phase-0.2-plan.md "Gate failures" provision, plan revision
is in scope.


## Artifacts

- `experiments/phase-0.2/section11-production-validation.md` — this artifact
- `data/metadata/section11-prod-{S,U,H_1975,H_2020}.parquet` — pulled metadata
- `data/metadata/section11-prod-{S,U,H_1975,H_2020}-vec.npy` — SPECTER2 vectors
- `data/metadata/section11-cluster-fit-{S,U}-K{30,50,100}.npy` — cluster centroids
- `experiments/phase-0.2/section11_production_validation.py` — this script
