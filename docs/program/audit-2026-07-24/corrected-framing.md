# Corrected paper-ready framing (from the 2026-07-24 independent audit)

Two claims are stated more strongly in the program's summaries than the evidence supports. Below is the
corrected, defensible framing for each — **what to claim**, **what to avoid**, and the **numbers that back it**
(all independently re-verified against committed artifacts during the audit). Use these as the basis for the
relevant paper sections.

---

## 1 — The AI multi-agent arm (polyphony ch.1 + WS1 ch.2 OSS)

### What the record over-claims
> "Role-diverse ensembles resist homogenization across **six experiments**; the CI excludes zero in the
> anti-homogenization direction across **three designs**; R4 **reproduces WS2's concentration+fragmentation
> decoupling** on an AI substrate."

### Why it is too strong (grep-verified: these strings appear nowhere in polyphony)
- Polyphony's **confirmatory** R4 result is a **one-sided refutation of collapse** — the pre-registered
  progressive-collapse hypothesis failed (`collapse_passed = false`).
- The anti-homogenization CIs that exclude zero are **three *exploratory* diagnostics inside the single R4
  experiment**, not three independent confirmatory designs: popularity-V slope **+0.0090 [+0.0057, +0.0118]**,
  residual-V **+0.0105 [+0.0068, +0.0138]**, persona-persistence gap **+0.0332 [+0.0231, +0.0437]**.
- Other experiments showed **task-conditional convergence or harm**: R6 topic-B immediate-anchor collapse;
  R7A governance off-task **−0.207 V**; R7C-A (below).
- The R4 *concentration* statistic (P_top4, **+0.0102**) is a **sampling artifact**: a matched null with agent
  preference removed reproduces it at **+0.0153 (151%)**, and the popularity arm is indistinguishable from that
  null (**p = 0.882** raw / **0.289** normalized).

### Corrected claim (defensible)
> Persona-diverse GPT-5.6 ensembles did **not** collapse into unison under the shared-context actuators we
> tested: the pre-registered progressive-collapse hypothesis was refuted, with exploratory evidence that
> diversity if anything rose. This resilience is **conditional** — specific task structures (topic anchoring,
> off-task governance context, superseded-version context) produced localized convergence or constraint-adoption
> failures. The apparent rise in top-item concentration under the popularity actuator is an artifact of weighted
> sampling, not an ensemble behavior (matched-null reproduced at 151%).
>
> The WS1 ch.2 OSS arm (DeepSeek, two-channel) **replicates this null cross-substrate and extends it to the
> reasoning layer**: under a live endogenous actuator neither outputs nor reasoning strategies collapse; a
> reasoning-strategy collapse appears **only under imposed maximal conformity**, never under endogenous conditioning.

### Do NOT say
"reproduces WS2's decoupling," "resists across six experiments," "three designs," "version-conflict is the one
real effect."

### On version-conflict specifically
The one surviving positive signal (R7C-A, 40/40 deprecated-constraint adoption) is **~100% confounded with
literal card-name copying**: the payload string "Approval Snapshot" appears in **40/40** superseded-context
outputs and **0/40** empty-context outputs, so the adoption label is collinear with *whether the named payload
was shown*. A pre-registered literal-copy-rate diagnostic was never reported. Frame version-conflict as **a
motivation for provenance inspection**, not a demonstrated robust effect.

---

## 2 — The WS2 semantic-fragmentation leg

### What the record over-claims
> "Semantic **fragmentation** in CS across **three embedding families** (**atypicality**↑)."

### Why it is too strong / mis-named
- The metric is **mean-pairwise-cosine distance (embedding spread)**, **not atypicality** — WS2 never computed
  atypicality.
- The three-family agreement is **directional** (raw permutation test: SciNCL **+22.6% / +3.35σ**, Qwen3
  **+6.6% / +3.07σ**, SPECTER2 **+3.4% / +2.2σ**, all p = 0.0001), but under a **year-collinearity control**
  (VIF **44.3**) the effect stays significant on **only SciNCL mean-pairwise-cosine**. Cluster-entropy and
  effective-dimensionality do not survive the control, and cluster-entropy **reverses** (declines) under Qwen3.

### Fairness caveat (report it — it cuts the other way)
VIF 44.3 is extreme collinearity: calendar-year and the rising metric are nearly the same variable, so
residualizing the metric against year is arguably **over-conservative** for a claim that is *intrinsically* about
a temporal trend. Report both the raw and the controlled result; don't treat the controlled test as decisive.

### Corrected claim (defensible)
> Over 1970–2024 the semantic spread of CS abstracts increased: mean-pairwise-cosine distance rose and was
> permutation-significant across all three embedding families, and the rise survives a stringent year-collinearity
> control for the SciNCL family. Cluster-entropy and effective-dimensionality are noisier and do not survive the
> control. We therefore report the spread as **robust for pairwise-cosine and directionally consistent across
> families**, and we do **not** claim uniform "fragmentation across three families."

### Do NOT say
"atypicality," "fragmentation robustly established across three embedding families."

---

## Where these came from
Full audit: `CONSOLIDATED.md` (this dir) + per-body reports `polyphony.md`, `ws2.md`. Findings T1.1, T1.2, T1.4.
Both framings were re-verified by the consolidator (grep-negative for the polyphony strings; direct read of
`aggregate-3family.json` + `robustness-sweep.json` for the semantic leg).
