# Phase 2.3 — the subfield mechanism test: results (3 embedding families)

**The pre-registered "single most important analysis"** (`docs/conceptual.md`
line 35): *do canon-concentrated subfields show more demographic–semantic
divergence than diffuse ones?* Estimator (locked in `phase-2.3-plan.md`):

```
divergence_magnitude(s) = β0 + γ₁·canon_concentration(s) + β2·log_size(s)  [+ field FE]
```

`divergence_magnitude = demographic_trend_sd − semantic_trend_sd` (absolute
standardized trends differenced — **not** the Phase-2.2 confounded ratio),
`canon_concentration` = mean reference-canonicity Gini (LEVEL). Grid:
**{SciNCL, Qwen3, SPECTER2} × {level-1 sub-concepts, K=50 clusters}** = 6 specs.
SPECTER2 was added (a fresh 1M Modal embed, ~$3) as the pre-committed Stage-3
robustness family to adjudicate an embedding-sensitive Physics signal.

Window 1970–2023 (incomplete 2024 trimmed). Runs on local vectors (+ the $3
SPECTER2 embed).

---

## Verdict — NO ROBUST LOCALIZED MECHANISM; the reframing's independence holds

Across the 6 specs, γ₁'s **sign is embedding-determined** — the significant specs
point in **opposite directions** — so there is no robust concentration→divergence
link. The Physics signal that looked significant under SciNCL (+0.70σ) is **not
corroborated**: Qwen3 marginal, SPECTER2 negative. Canon-concentration does not
robustly predict demographic–semantic divergence → the aggregate Phase-2.2 null
is **not masking a localized narrowing**; concentration and frontier/authorship
diversity are independent.

## The 6-spec grid (γ₁ = slope of divergence on canon-concentration | log size)

| Spec | γ₁ | standardized | perm p | VIF |
|---|---|---|---|---|
| SciNCL × sub-concepts | +13.08 | +0.236σ | 0.021* | 2.04 |
| Qwen3 × sub-concepts | −0.92 | −0.017σ | 0.886 | 2.04 |
| **SPECTER2 × sub-concepts** | −35.79 | −0.432σ | 0.0001* | 2.04 |
| SciNCL × K=50 clusters | +2.03 | +0.158σ | 0.277 | 1.21 |
| Qwen3 × K=50 clusters | −4.89 | −0.166σ | 0.250 | 1.21 |
| **SPECTER2 × K=50 clusters** | −37.71 | −0.466σ | 0.0013* | 1.21 |

Signs span the range `{SciNCL +,+ ; Qwen3 −,− ; SPECTER2 −,−}`; the three
significant specs (SciNCL sub-concepts **+**, both SPECTER2 **−**) **contradict
each other** — the signature of no real effect, not a mechanism. VIF 1.2–2.0
(identifiable; the log-size control does its pre-registered job — canon⟂size
r≈+0.70).

## Per-field decomposition (sub-concepts) — the Physics wrinkle, adjudicated

| Field / embedding | γ₁ | standardized | perm p | n |
|---|---|---|---|---|
| CS / SciNCL | −7.43 | −0.129σ | 0.243 | 60 |
| CS / Qwen3 | −16.32 | −0.234σ | 0.073 | 60 |
| CS / SPECTER2 | −50.67 | −0.527σ | 0.0001* | 60 |
| Physics / SciNCL | +31.61 | +0.702σ | 0.0026* | 20 |
| Physics / Qwen3 | +11.77 | +0.417σ | 0.080 | 20 |
| Physics / SPECTER2 | −21.26 | −0.348σ | 0.144 | 20 |

The SciNCL-only Physics positive slope (the "wrinkle" the 2-family read flagged)
is **refuted by the tie-breaker**: Qwen3 marginal (p=0.08), SPECTER2 **negative**
and non-significant. 1 of 3 families supports it → not a real localized mechanism.
An internal leave-one-out on Physics/SciNCL is stable (γ₁∈[+25,+51], 100% of LOO
fits significant) — so it is a genuine SciNCL-specific feature, not an outlier;
its non-robustness is the cross-family disagreement, not a leverage point.

## The escalation: is "frontier widens" robust to a 3rd family?

SPECTER2's per-subfield semantic trends skew negative, which — if real — would
threaten the Phase-2.2 "the frontier diversifies" reframing. Verified with the
CORRECT tools (permutation significance + ABSOLUTE magnitude, not the
ill-conditioned σ), at the **aggregate whole-field** level (`aggregate-3family.json`):

| Field | SciNCL | Qwen3 | SPECTER2 |
|---|---|---|---|
| **CS** | +22.6% (up*) | +6.6% (up*) | **+3.4% (up*)** |
| **Physics** | +23.7% (up*) | +10.5% (up*) | **−10.2% (down*)** |

- **CS: all three families agree the frontier widens** (SPECTER2 +3.4%, small but
  permutation-significant). The reframing is **not overturned**.
- **Physics is the sole locus of embedding disagreement**: topical embeddings
  (SciNCL, Qwen3) widen strongly; the citation-tuned SPECTER2 narrows (−10.2%).
  Physics carries the most concentrated canon (astrophysics/particle ref-Gini
  ≈0.086), so a citation-geometry-tuned embedding "sees" the papers converging
  onto that canon while topical embeddings see subject-matter spreading — the two
  "semantic" axes (citation-structure vs topical) genuinely diverge in Physics.

## Verification (why the per-subfield σ misled — "verify extreme claims")

The per-subfield MEAN semantic trend read −1.35σ for SPECTER2 (vs +2.3σ SciNCL),
suggesting a global narrowing. It is an **ill-conditioned-σ artifact** (the exact
`tasks/lessons.md` Phase-2.2 caution): SPECTER2's per-year mpc is **near-flat** for
CS subfields (AI: 0.185→0.180, range 0.008), so `standardized_effect`
(slope×range / tiny-sd) amplifies dust into large sign-unstable σ. Checks
(`specter2-verification.txt`):

1. **Adapter active** — Modal `check_adapter`: on-vs-off embeddings differ
   materially (`adapter_materially_active=true`; on-norm 22.2 ≈ production 22.05).
   SPECTER2 is the citation-tuned proximity model, not the base.
2. **Not drift** — the SPECTER2 trend does not attenuate on later windows
   (−1.35σ 1970–2023 → −1.56σ 2000–2023), so it is not a pre-1990 embedding-drift
   artifact (SPECTER2 is the most drift-susceptible family per Check 5c, but the
   reversal survives dropping the early era).
3. **Curves smooth** — per-year mpc curves are stable, not degenerate; the
   reversal is real but small (Physics) / near-flat (CS), NOT a global −1.35σ.
4. **G1 negative control PASSES** — aggregate reference-canonicity Gini rises over
   1970–2023, permutation-significant in both fields (substrate intact).

## Cautions carried (`tasks/lessons.md`)

1. **Ratio ≠ control** — divergence is `demographic_sd − semantic_sd` (absolute
   trends differenced).
2. **VIF reported** — 1.2–2.0; identifiable (canon/size collinearity controlled).
3. **≥2 (here 3) embedding families** — decisive: the significant signals
   reverse across families; SPECTER2 adjudicated the Physics wrinkle.
4. **Verify extreme claims** — the SPECTER2 −1.35σ was chased to an
   ill-conditioned-σ artifact; the aggregate + permutation view is the honest one.
5. **Ill-conditioned σ** — a near-flat series' standardized effect is
   sign-unstable dust; judge with permutation significance + absolute magnitude.
6. **Trim the incomplete final year** (2024); **permutation inference** (small N).

## Honest limitations

- **Physics N=20 subfields** — low-powered per-field.
- **Level-1-argmax off-field concepts** add noise to the sub-concept partition
  (stray low-canon concepts); they do not drive the results (LOO-checked).
- **"Semantic diversity" is not one construct** — citation-geometry (SPECTER2)
  and topical (Qwen3) embeddings can disagree on the trend's sign (Physics). This
  is a genuine measurement caveat, now a headline methodological finding.

## Interpretation for the program (WS3 bridge)

`conceptual.md` §"What ws2 contributes": γ₁ ≈ 0 / no-robust-positive-γ₁ challenges
the actuator-homogenization *structural* claim at the phenomenon level. We find
**no robust localized mechanism** — the reframing's independence holds. The
Physics-specific embedding disagreement (citation-geometry narrows / topical
widens where the canon is most concentrated) is a **sharp target for WS1
simulation** — the mechanism-space is narrowed to "canon-concentration couples to
citation-geometry convergence, not to topical narrowing, and only where the canon
is strong (Physics)."

## Reproduce

```
python experiments/phase-2.3/build_subfields.py --source <corpus> --embed-dir <e> --outdir <sf>
# SPECTER2 3rd family (server-side volume-write; robust to flaky client):
uv run modal run experiments/phase-2.3/embed_specter2_vol.py --source <corpus> --outdir <s2>
uv run modal run experiments/phase-2.3/embed_specter2_vol.py::concat   # → volume specter2-vectors.npy
modal volume get ws2-embeddings /specter2-vectors.npy <s2>/specter2-vectors.npy
python experiments/phase-2.3/compute_subfield_metrics.py --embed-dir <e> --source <corpus> \
    --demog-dir <demog> --subfield-dir <sf> --specter2-dir <s2> --outdir <metrics>
python experiments/phase-2.3/run_subfield_test.py --metrics-dir <metrics>
python experiments/phase-2.3/aggregate_3family.py --embed-dir <e> --specter2-dir <s2>
python experiments/phase-2.3/drift_diagnostic.py ...   # verification
```
