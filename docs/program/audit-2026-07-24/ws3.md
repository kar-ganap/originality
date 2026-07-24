# WS3 Adversarial Audit — the C/V ABM (Henrich ↔ Wu-Wang-Evans reconciliation)

**Auditor:** independent adversarial reviewer. **Scope:** `whitespace_3/` only.
**Date:** 2026-07-24. **Branch:** `ws3-phase-2-empirical-bridge` (38 commits ahead of `main`,
UNMERGED; working tree clean). All artifacts below are committed; the 2026-07-22 correction
commit `6506055` is present.

---

## EXECUTIVE SUMMARY

- **Two-channel "same lever, opposite signs"** → **WEAKENED/SPLIT.** The *W↑ ⊥ V^struct↓ in N*
  sign-structure SURVIVES (CIs exclude 0, 16/16 cells). The headline *C↑ while V↓* crossover FAILS
  at scale: C is a frozen constant, total-V straddles zero. (The record already says this.)
- **Bridge A 15.6× vs ~13×** → **SURVIVES (loosely).** `bridge_A.py` reproduces 15.6× exactly, but
  it is a qualitative fingerprint at ratio≥5×, not a magnitude match; the ratio is `bw`-tunable and
  numerically fragile (within-slope ≈ 0). "13×" is a WS2 target I could not re-verify (out of scope).
- **λ*≈0.09 self-critique** → **CONFIRMED, not overstated.** Independently verified from committed
  data: total-V slope straddles 0 at λ=0/0.1/0.25; ∂C/∂logN = 0.0000 *exactly* (C≡76.0, zero seed
  variance); the phase diagram's λ*≈0.09 interpolates between two straddle-zero slopes.
- **Most important finding:** the self-critique is accurate — but it has **not propagated to the
  paper-bound artifacts.** The formal-spine primer still calls the withdrawn crossover "the paper's
  central result" and states a Pareto "raise both (∂C*>0)" claim that the committed model refutes
  (∂C/∂ι = 0 exactly). `phase_diagram.py` still prints "V-favouring / λ*≈0.09" with no CI caveat.
- **Reproducibility:** 154/154 tests pass; lint+mypy clean; ABM deterministic; phase-3 verdict and
  headline numbers reproduce from committed code/data. One minor non-reproducibility (V^struct ~1e-4).

Bottom line: no NEW undocumented critical defect — the CI-straddle failure the audit hunts for was
already found and honestly recorded by the project. The residual risk is **doc/artifact drift**: the
correction lives in the master docs but not in the primer or the figure-generating script that feed
the paper.

---

## FINDINGS (most severe first)

### [HIGH] Formal-spine primer is stale — presents the withdrawn crossover as "the paper's central result" and states a Pareto claim the model refutes
- **Claim affected:** cc:wwe (per-capita V falls with scale via κ); cc:reconcile ("same lever,
  opposite signs" + Pareto "raise both").
- **File:** `docs/primers/cv-reconciliation-primer.tex:620-647` (cc:wwe, cc:reconcile), amendment
  block at `:694`.
- **What's wrong:** The primer carries a **2026-07-07** amendment (cc:open/CC6 disconfirmed) but
  **no 2026-07-22 amendment.** So (a) cc:reconcile is still labelled *"Status: the paper's central
  result"* with no note that the crossover is not statistically present; and (b) cc:reconcile states
  the Pareto direction as *"∃ intervention with ∂C\*>0, ∂V\*>0"* (raise **both**). The committed
  model delivers **∂C/∂ι = 0 exactly** — my `phase_diagram.py` run shows C = 46.0 flat across
  ι∈{0,0.1,0.25,0.5} while V^struct_iso rises 0→0.173→0.180→0.179. So the "raise both" claim is not
  merely uncaveated, it is **affirmatively contradicted** by the model, and `conceptual.md`'s own
  correction box says so ("really ∂V>0, ∂C=0 … not a both-boost"). The primer is named the "formal
  spine" / a Key Reference for the paper, and the author demonstrably *does* amend it — the missing
  2026-07-22 amendment is a real drift that can propagate into the paper.
- **Evidence:** grep of the primer shows amendments only at 2026-07-07; `phase_diagram.py` Panel C
  (rerun) C=46.0 constant across ι. **CONFIRMED.**

### [MEDIUM] `phase_diagram.py` — the committed "reconciliation deliverable" — reports λ*≈0.09 and labels λ=0 "V-favouring" with no CI caveat, while its own output shows the bracketing slopes straddle zero
- **Claim affected:** the λ*≈0.09 crossover / "V-favouring → C-favouring" regions (the paper's main
  figure).
- **File:** `experiments/phase-1-rung5/phase_diagram.py:43-62` (`_cross_zero` uses point-estimate
  sign only; prints "λ* ≈ {:.2f}" and "V-favouring").
- **What's wrong:** This is exactly the audit-history defect #2 (a λ* between slopes individually
  indistinguishable from 0). My rerun: λ=0 V-slope **+0.0021 CI[−0.0017,+0.0052]** (straddles 0,
  labelled "V-favouring"); λ=0.15 **−0.0016 CI[−0.0117,+0.0070]** (straddles 0); → "λ* ≈ 0.09."
  The script never checks whether the bracketing CIs exclude zero. The master docs now caveat this,
  but the *reproducible figure generator* does not, so a figure lifted from it inherits the overclaim.
- **Evidence:** background rerun of `phase_diagram.py` (full Panel A/B/C output captured). **CONFIRMED.**

### [MEDIUM] Bridge A "15.6× ≈ 13×" is a loose, fragile fingerprint sold in one line as "the right magnitude"
- **Claim affected:** Phase-2 A "reproduces at the right magnitude (15.6×≈13×)" (CLAUDE.md WS3,
  Phase-2 line).
- **File:** `experiments/phase-2/bridge_A.py:13-14,54-56`; CLAUDE.md WS3 §"Phase 2 … A".
- **What's wrong:** `bridge_A.py` reproduces the ratio at **15.6× exactly** (global −0.0231, within
  **+0.0015**), but (i) the pass criterion is only ratio ≥ ~5× (order-of-magnitude), (ii) the ratio
  is numerically unstable because the within-slope is ≈0 (a within of +0.003 would halve it to ~8×),
  and (iii) the record's own bridge_B line admits the magnitude is *"bw-tunable ⇒ consistency, not a
  tight prediction."* So the A-line phrase "the right magnitude" mildly overstates what B concedes.
  The *qualitative* fingerprint (global novelty↑, within ~flat) is sound; the *magnitude match* is not
  a prediction. The empirical "≈13×" (WS2: global −0.64 / within −0.05) is out of scope — not
  re-verified here.
- **Evidence:** `bridge_A.py` rerun prints ratio 15.6×. **CONFIRMED** (model side); WS2 target
  UNVERIFIED (out of scope).

### [LOW] Committed at-scale JSONL is not fully bit-reproducible — V^struct wobbles ~1e-4
- **Claim affected:** the at-scale sweep artifact `results-at-scale.jsonl` (rung 5b).
- **File:** `experiments/phase-1-rung5/results-at-scale.jsonl` vs `channel.run`.
- **What's wrong:** On spot-checked cells, **V, C, H bit-match** the committed values, but **V^struct
  differs by ~1×10⁻⁴** on some seeds (e.g. λ=0,N=200,seed=7: committed 0.1793, rerun 0.1794; total-V
  identical). The RNG stream is identical (V/C/H match) — only the structural/lateral *split* moves,
  consistent with a `np.argsort(closure)` canon-membership tie-break that is sensitive to numpy/scipy
  patch version (local numpy 1.26.4 / scipy 1.15.3 vs the Modal image's `numpy<2, scipy>=1.11`).
  **Does not change any audited conclusion** (V^struct-slope stays reliably <0; the headline is
  total-V, which matches). Full 300-cell reverification was not completed (channel.run is O(N²);
  infeasible in-window). Note: the docstrings say "Deterministic given seed" and "byte-identical" —
  true for V/C/H, not literally for the V^struct split across library versions.
- **Evidence:** 4-cell spot check (2 exact, 2 differ on V^struct only, all by ≤1e-4). **CONFIRMED.**

### [LOW] Spend-tracking discipline has drifted
- **File:** `tasks/spend.md` (running total **$0**, only a 2026-07-02 Phase-0 row).
- **What's wrong:** Ground rule #9 ("log all compute costs at the time of incurring"). Multiple Modal
  runs since — the rung-5b at-scale sweep to N=1500, and the Phase-2 Experiment C 24M-population dense
  graph (lessons.md itself mentions a "~$5 server-side density check") — are not logged. Small dollars,
  but the discipline the program repeatedly stresses is not being followed. **CONFIRMED.**

### [CONTEXT, not a defect] Entire WS3 record (incl. the corrections) is on an unmerged branch
- `ws3-phase-2-empirical-bridge` is 38 commits ahead of `main`. Anyone reading `main` sees neither the
  results nor the 2026-07-22 corrections. Noted for provenance; the branch itself is internally clean.

---

## STRESS-TEST OF THE SELF-CRITIQUE (the audit's core question)

**Is the crossover really statistically absent, or is the self-critique over/under-stated?**
Verdict: the self-critique is **accurate and, if anything, slightly generous to the model.** Three
independent recomputations from committed code/data:

1. **At-scale total-V slope on logN (recomputed from `results-at-scale.jsonl`, project's own
   `logN_slope_ci`, 2000 boots):**
   | λ | slope | 95% CI | verdict |
   |---|---|---|---|
   | 0.0 | +0.00021 | [−0.00127, +0.00158] | **straddles 0** |
   | 0.1 | −0.00007 | [−0.00133, +0.00131] | **straddles 0** |
   | 0.25 | −0.00073 | [−0.00172, +0.00031] | **straddles 0** |
   | 0.5 | −0.00116 | [−0.00217, −0.00015] | all<0 (barely) |
   | 1.0 | −0.00086 | [−0.00164, −0.00001] | all<0 (barely) |
   → Exactly the CLAUDE.md claim ("straddles zero at λ=0/0.1/0.25"). **No λ has a CI entirely >0**, so
   there is **no reliably V-favouring region** → the crossover's V-half is genuinely absent at scale.

2. **∂C/∂logN and C determinism (same data):** C = **76.0 for all 300 cells** (every N∈{200…1500},
   every λ∈{0…1}, every seed). Slope = **0.0000**, seed-CV = **0** → not just "a clock," a *frozen
   constant*: ∂C/∂logN = 0 and ∂C/∂λ = 0 exactly. The "Henrich C↑ with N" half of the reconciliation
   **does not exist at scale**; it is a small-N (30–240) phenomenon, which the rung-5 retro concedes.
   So **∂C/∂logN = 0.0000 exactly** is literally true and is a degenerate result, not a finding.

3. **Phase diagram (`phase_diagram.py`, channel.run, N=30–240) reruns to λ*≈0.09** — but the two
   slopes it interpolates between (λ=0: [−0.0017,+0.0052]; λ=0.15: [−0.0117,+0.0070]) **both straddle
   zero.** This is the uncertainty-free-point-estimate defect, reproduced live.

**Provenance of the self-critique is clean:** `run_diagnostics.py --from-raw` on the committed
`raw-grid.json` reproduces `phase3-verdict.json` **exactly** — E4 `internal_usable=False` (all
mode×f, no CI-separated flip), E5 `deterministic=True` (all cells).

**Where the self-critique is *nuanced but fair*:** a crossover IS statistically present in the
**reduced-form `innovation.run` at small N** — I reproduced it: λ=0 V-slope **+0.0549 [+0.0415,
+0.0689]** (all>0), λ=0.25 **−0.0338 [−0.0467,−0.0216]** (all<0): a genuine CI-separated flip. The
record correctly attributes the small λ* to "an artifact of the reduced-form driver" (κ≈λ·lnN has
wide dynamic range and a real persistence-rise at tiny N), which vanishes on the endogenous H driver
(λ*≈2, f-gated) and at scale. The "three inconsistent λ* (0.086 / 0.09 / ~2)" and "C is a
deterministic clock" residuals are all confirmed. **The self-critique is not overstated.**

**`cv_predictor_audit.py` conclusion:** "predict() BEATS a constant λ* ⇒ **LOAD-BEARING**" (MAE
mean-field 0.035 vs constant 0.096). This is *scoped* to the reduced-form `innovation.run` regime
(NS=[10,30,100]) and to *directionality* (tracking λ*'s f-dependence), and the script itself defers
exact λ* to "the next test." It does **not** contradict the crossover-absence finding — but the word
"LOAD-BEARING," if cited without its "directional / reduced-form" scope, could mislead. Note the audit
also shows λ* ranges **0.000–0.309** across f (and =0 at f≥0.55), reinforcing that a single "λ*≈0.09"
is a mean over a highly fidelity-dependent, often-zero quantity.

---

## REPRODUCTION LOG

| Ran | Result |
|---|---|
| `uv sync --extra dev` | OK |
| `pytest -m "not slow"` | **135 passed** (43.9s) |
| `pytest -m slow` | **19 passed** (185.6s) → 154/154 total |
| `ruff check src/ tests/` | clean |
| `mypy src/ --strict` | clean |
| at-scale V/C/V^struct slope CIs from committed JSONL | V straddles 0 at λ=0/0.1/0.25; C≡76 (∂=0); V^struct reliably <0 |
| `phase_diagram.py` (channel.run) | λ*≈0.09 reproduced; bracketing slopes straddle 0; Pareto C=46.0 flat across ι |
| `analytics_check.py` | mean-field λ*≈0.000 (persistence saturated, P(N)=[1,1,1,1]) |
| `bridge_A.py` | within/global = **15.6×** (global −0.0231, within +0.0015) reproduced |
| rung-3 crossover (`innovation.run`, N=[4,12,40]) | CI-separated flip reproduced (λ=0 all>0; λ=0.25 all<0) |
| `run_diagnostics.py --from-raw` | committed phase3-verdict reproduced exactly |
| at-scale determinism spot check | V/C/H bit-match; V^struct ~1e-4 wobble |
| `cv_predictor_audit.py` | "LOAD-BEARING" (directional, reduced-form scope) |
| **Not reproduced** | full 300-cell at-scale sweep from scratch (O(N²), infeasible in-window — committed per-seed data re-analyzed + spot cells re-run instead); WS2 "13× / −0.64" target (out of scope); any Modal/paid job (guardrail) |

---

## WHAT SURVIVES CLEANLY

- **The self-critique itself** — every quantitative claim in the 2026-07-22 correction boxes
  (crossover-absence, C-frozen-clock, three-λ* divergence ~20×, Pareto reframe to ∂V>0/∂C=0) is
  reproduced from committed code/data. This is a model of honest null-reporting.
- **Reproducibility infrastructure:** 154 tests pass; lint/mypy clean; seeds/params pinned; ABM
  deterministic for the headline outputs; the expensive verdict re-derives from a persisted raw grid.
- **The usable estimands** (resolution map, verified in the committed verdict): E1 conformity crushes
  V^struct level (−37% at λ=0.5, −86% at λ=2, CIs exclude 0 above λ≈0.5); E2 the W↑/V^struct↓ N-decoupling
  (16/16 cells, CIs on the right side of 0); E3 isolation +59% [+0.53,+0.64]. These are the model's
  real content and they hold.
- **Bridge A qualitative fingerprint** (global novelty↑, within ~flat) reproduces.
- **The reduced-form small-N crossover** is real (CI-separated) and honestly labelled reduced-form-only.
