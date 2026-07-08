# WS3 Phase 1 · rung 5 retro — synthesis (the capstone). **Phase 1 COMPLETE.**

**Branch:** `ws3-phase-1-rung5b-closeout` (5b) + merged `ws3-phase-1-rung5-synthesis` (5a) ·
**Window:** 2026-07-07/08
**Status:** COMPLETE. All **five** audited Phase-1 items closed (rung-4e retro's honest
audit): analytics, phase diagram, the Pareto half of the reconciliation, robustness-grid
completion, and the at-scale verification.
**Plan:** `phase-1-rung5-synthesis-plan.md`.

---

## What rung 5 closed

The rung-4e retro's audit found "Phase-1 complete" was overstated — five stipulated items
were open. rung 5 closed all five:

| # | Open item | Closed by | Result |
|---|---|---|---|
| 1 | light analytics | 5b `analytics.py` | the **crossover law** `λ* = d ln P/d ln N`; Henrich carrier-survival; GW anchor `μ=2→0.7968` |
| 2 | the phase diagram | 5a `phase_diagram.py` | `λ*≈0.09` crossover (V- vs C-favouring regions); the figure |
| 3 | Pareto / non-strict trade-off | 5a `ι` + orthogonality | selective isolation: shielded subgroup `V^struct` high, global `C` preserved |
| 4 | robustness-grid completion | 5b memory-with-decay | **3rd Level-3 anchor** `λ_f = ε/(1−f·n−r) = 1.0` |
| 5 | at-scale verification | 5b Modal sweep | crossover **holds to N=1500** (`λ*` unchanged) |

## 5a — the reconciliation deliverable

- **Phase diagram** (well-mixed, uniform κ): `∂V*/∂logN` flips sign at **`λ*≈0.09`** —
  V-favouring (small λ) → C-favouring (large λ). Lands on rung 3's independent `λ*≈0.086`.
- **Same lever, opposite signs:** beyond `λ*`, `C↑` with N (Henrich, redundancy) while
  `V↓` (WWE) — the reconciliation, strengthening with λ (`C`-slope `+0.15→+9.6`).
- **Pareto (route chosen this session: orthogonality + a light `ι` demo):** selective
  isolation (`isolated_frac`, `κ_eff=0` for a subgroup) keeps the subgroup's `V^struct`
  high (`~0.18` vs conformist `~0.11`) with global `C` pinned (`46.0`) — H4's concrete
  "raise both" intervention, exhibited; the two-channel orthogonality (κ→C/H ⟂ τ→V^struct)
  is the primary framing.

## 5b — analytics + robustness + at-scale

- **Analytics (light, simulation-guided):** the crossover law `λ* = d ln P/d ln N`
  (persistence elasticity). The mean-field predicts `λ*≈0` — persistence saturates
  (`μ=n·f≫1`) — *explaining why the simulated crossover sits near zero* (0.09). Sign +
  smallness match, not the third decimal (idealised `κ=λ·ln N` vs the model's `κ=λ·H`).
- **Memory-with-decay retention (the last grid axis):** `roles.py` gains self-retention
  `r`; reproduces the **2nd Strimling number** `λ_f = ε/(1−f·n−r) = 1.0` (sim `0.965`,
  N-independent) — the program's **3rd Level-3 result**. `r=0` byte-identical.
- **At-scale Modal sweep (detached, survives laptop shutdown):** 300 cells `(λ×N×seed =
  5×4×15)`, N to 1500. **The crossover holds at ~6× laptop scale** — V-favouring at λ=0
  (`+0.0002`), C-favouring for λ≥0.1 (`−0.0001…−0.0012`), `λ*` still ≈0.09. So the phase
  diagram is **not a small-N artifact**.

## Surprises / notes

- The at-scale crossover **weakens** (`~10⁻³` vs the laptop's `~10⁻²`) — exactly the
  persistence-saturation analytics: at large N, scale buys even less originality to offset
  conformity, so the effect shrinks toward the near-zero `λ*`. Sign-structure invariant.
- `C`-slope ≈ 0 at N≥200: `C` saturates past the Henrich small-N threshold, so the `C↑`
  half of the reconciliation is a *small-N* phenomenon (visible on the laptop's 30–240).
- The program now has **three Level-3 anchors**: Henrich/Mesoudi, Strimling `U/(1−β)`,
  Strimling-memory `U/(1−β−r)`.

## Honest limits

- **At-scale = the focused `(λ,N)` slice to N=1500, NOT the full N=3000 6D grid.**
  `channel.run` is ~O(N²) (N=2000 ≈ 3 min/run), so the full grid is thousands of
  core-hours — infeasible under `<$50` (the §6 "few CPU-seconds/cell" estimate was wrong
  at scale). Logged, not silently capped; the slice is the meaningful verification.
- **Analytics are light** (mean-field, qualitative) — sign + magnitude-order, not exact
  numbers, per the compass.
- **Pareto** demonstrated concretely via `ι`; the broader orthogonality is synthesis
  across rungs 4b+4d, not a single in-model theorem.

## Program state — Phase 1 done, the reconciliation assembled

The C–V reconciliation is complete and robust: **the same growth that deepens a field's
cumulative knowledge (`C↑`, Henrich) thins each person's structural originality (`V↓`, WWE)
beyond a small conformity threshold `λ*` — unless a pocket is insulated (Pareto) — and a
separate content/`τ` channel makes cross-niche novelty *rise* (fragmentation), orthogonal
to canon concentration.** Sign-structure invariant across κ-specs × topologies × graph
draws × scale (to N=1500) × retention.

## What's next

- **Phase 2/3 (the paper):** the arc is whole — two driving claims (WS2 Claim #13, WS3
  CC6) honestly *disconfirmed* into a sharper positive thesis (concentration +
  fragmentation, orthogonal), three Level-3 anchors, the phase diagram, the crossover law.
  The writeup (`docs/conceptual.md` → paper) is the natural capstone.
- Optional deferred threads: the full N=3000 sweep *if* `channel.run` is vectorised;
  depth-`C` saturation under sub-criticality; the F2 escape-hatch demo.
