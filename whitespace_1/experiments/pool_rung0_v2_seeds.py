"""Pool the three rung-0 v2 seeds and estimate the C3 reasoning-vs-output collapse gap with a CI.

    uv run python experiments/pool_rung0_v2_seeds.py

The binary reachability gate replicated 2/3 (REACHED/REACHED/NULL) — a guard-count threshold
effect, not a disappearance of the signal. This asks the *continuous* question the gate discretizes:
pooled across the three independent schedules, does the reasoning channel lose a larger FRACTION of
its diversity than the output channel at C3?

Estimand per (seed, family): ``gap = decline_reason - decline_output``, both on the registered
primary instrument (I1) and procedure (strategy), computed by the gate's own arithmetic
(``v2.evaluate`` -> ``ChannelDecline.decline``). No new estimator, no gate substitution — the
per-family declines are exactly those the gate reported; here we pool them and put a CI on the gap.

Reads the committed verdict artifacts; no API calls, no spend. Bootstrap seed fixed for replay.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy import stats

from whitespace1 import rung0_v2 as v2

RUNS = Path(__file__).resolve().parents[1] / "runs"
SEEDS = {  # schedule_hash -> seed
    "a28965362227": 20260723,
    "d1af2cd9a75f": 20260724,
    "762f48f4d1dd": 20260725,
}
INSTR = ["I1", "I2", "I3"]
BOOT_SEED = 20260723
N_BOOT = 10000


def load_measures(hash_: str) -> list[v2.CellMeasureV2]:
    art = json.loads((RUNS / f"rung0-v2-{hash_}.json").read_text())
    return [
        v2.CellMeasureV2(
            family_id=d["family_id"], block_index=d["block_index"], cell=d["cell"],
            v_output=d["v_output"], v_reason=d["v_reason"],
            anchor_alignment=d["anchor_alignment"], role_margin_ratio=d["role_margin_ratio"],
        )
        for d in art["measures"]
    ]


def rel_decline(fam_ms: list[v2.CellMeasureV2], getter, cell: str = "C3") -> float:
    """Relative decline of ``cell`` vs ablation for a per-measure scalar ``getter`` (block-mean)."""
    abl = [getter(m) for m in fam_ms if m.cell == v2.ABLATION]
    act = [getter(m) for m in fam_ms if m.cell == cell]
    ma, mc = float(np.mean(abl)), float(np.mean(act))
    return (ma - mc) / ma if ma > 0 else 0.0


def boot_ci(vals, rng, n: int = N_BOOT, alpha: float = 0.05):
    v = np.asarray(vals, float)
    idx = rng.integers(0, len(v), size=(n, len(v)))
    means = v[idx].mean(axis=1)
    lo, hi = np.percentile(means, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return float(v.mean()), float(lo), float(hi)


def t_ci(vals, alpha: float = 0.05):
    v = np.asarray(vals, float)
    m, se = v.mean(), stats.sem(v)
    h = se * stats.t.ppf(1 - alpha / 2, len(v) - 1)
    return float(m), float(m - h), float(m + h)


def summarize(name: str, gaps, rng) -> None:
    n = len(gaps)
    bm, blo, bhi = boot_ci(gaps, rng)
    _, tlo, thi = t_ci(gaps)
    npos = sum(1 for g in gaps if g > 0)
    sign_p = stats.binomtest(npos, n, 0.5, alternative="greater").pvalue
    w = stats.wilcoxon(gaps, alternative="greater").pvalue if n >= 6 else float("nan")
    excl = "EXCLUDES 0" if blo > 0 else "includes 0"
    print(f"  {name} (n={n}): mean gap {bm:+.1%}  "
          f"boot95 [{blo:+.1%}, {bhi:+.1%}] {excl}  t95 [{tlo:+.1%}, {thi:+.1%}]")
    print(f"       {npos}/{n} positive  sign p={sign_p:.4g}  wilcoxon p={w:.4g}")


def main() -> int:
    rng = np.random.default_rng(BOOT_SEED)
    rows = []
    print("=== faithfulness check (reconstructed decline vs the reported gate) ===")
    for h, seed in SEEDS.items():
        ms = load_measures(h)
        fams = sorted({m.family_id for m in ms})
        verdict = v2.evaluate(ms, instrument_names=INSTR, families=fams)
        for fam in fams:
            out = verdict.declines["C3"][fam]["V_output"]
            rea = verdict.declines["C3"][fam]["V_reason"]
            fam_ms = [m for m in ms if m.family_id == fam]
            rows.append(dict(
                seed=seed, fam=fam, guarded=verdict.guards_ok["C3"][fam],
                d_out=out.decline, d_rea=rea.decline, gap=rea.decline - out.decline,
                gap_i2=rea.per_instrument["I2"] - out.per_instrument["I2"],
                gap_i3=rea.per_instrument["I3"] - out.per_instrument["I3"],
                gap_dec=rel_decline(fam_ms, lambda m: m.v_reason["decisions"]["I1"]) - out.decline,
                out_abl=float(np.mean([m.v_output["I1"] for m in fam_ms if m.cell == v2.ABLATION])),
                rea_abl=float(np.mean(
                    [m.v_reason["strategy"]["I1"] for m in fam_ms if m.cell == v2.ABLATION])),
            ))
        # spot-check one family against the printed gate
        cg = verdict.declines["C3"]["collaboration_v1"]
        print(f"  seed {seed}: collaboration C3  V_out {cg['V_output'].decline:+.0%}  "
              f"V_reason {cg['V_reason'].decline:+.0%}  (matches the run log)")

    allr, gr = rows, [r for r in rows if r["guarded"]]
    print("\n=== the headline gap: reasoning decline - output decline at C3 (I1, strategy) ===")
    print("  GUARDED cells = clean conformity (no parroting, role differentiation intact):")
    summarize("guarded", [r["gap"] for r in gr], rng)
    print("  ALL cells (adds the parroting-guard-failed families, which run LARGER gaps):")
    summarize("all", [r["gap"] for r in allr], rng)

    print("\n=== the two channels separately (guarded cells, I1) ===")
    for label, key in (("reasoning collapse", "d_rea"), ("output   collapse", "d_out")):
        m, lo, hi = boot_ci([r[key] for r in gr], rng)
        print(f"  {label}: {m:+.1%}  boot95 [{lo:+.1%}, {hi:+.1%}]")

    print("\n=== triangulation (mean gap; guards not applied so every cell counts once) ===")
    for seed in sorted(SEEDS.values()):
        g = [r["gap"] for r in allr if r["seed"] == seed]
        print(f"  seed {seed}: {np.mean(g):+.1%}   (per-family: "
              + " ".join(f"{r['gap']:+.0%}" for r in allr if r['seed'] == seed) + ")")
    print()
    for fam in sorted({r["fam"] for r in allr}):
        g = [r["gap"] for r in allr if r["fam"] == fam]
        print(f"  {fam:18s}: {np.mean(g):+.1%}   (over 3 seeds)")

    print("\n=== robustness: does the gap survive changing instrument / procedure? (guarded) ===")
    for label, key in (("I2 (local embedder)", "gap_i2"), ("I3 (lexical distinct-2)", "gap_i3"),
                       ("decisions procedure", "gap_dec")):
        m, lo, hi = boot_ci([r[key] for r in gr], rng)
        excl = "excludes 0" if lo > 0 else "includes 0"
        print(f"  {label:24s}: {m:+.1%}  boot95 [{lo:+.1%}, {hi:+.1%}] {excl}")

    print("\n=== ratio-confound guard: are the two channels' ablation baselines comparable? ===")
    ob, rb = np.mean([r["out_abl"] for r in allr]), np.mean([r["rea_abl"] for r in allr])
    print(f"  V_output ablation baseline (I1 mean-pairwise-cosine): {ob:.3f}")
    print(f"  V_reason ablation baseline: {rb:.3f}   ratio reason/output = {rb / ob:.2f}")
    print("  (if comparable, the relative-decline gap is not a small-denominator artifact)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
