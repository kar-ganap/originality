"""Phase 2.2 — correctness / trust battery for the analysis pipeline.

Three kinds of check, each INDEPENDENT of the code under test:
  (A) cross-implementation — every metric recomputed a second way (scipy/sklearn
      / a different formula) and compared on real-ish data;
  (B) placebo / null — feed the pipeline data with NO signal (shuffled years,
      random-noise embeddings) and confirm it returns null (no spurious trend);
  (C) calibration + reproducibility — permutation false-positive rate ≈ alpha;
      the semantic trend is stable across subsample seeds.

Prints PASS/FAIL per check with both independently-computed values.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.stats import entropy as sp_entropy
from sklearn.decomposition import PCA

from whitespace2.canonical_metrics import gini, reference_canonicity
from whitespace2.divergence import (
    divergence_test,
    ols_trend,
    permutation_slope_test,
    residual_trend,
    standardized_effect,
)
from whitespace2.semantic_metrics import (
    cluster_entropy,
    effective_dimensionality,
    mean_pairwise_cosine_distance,
)

_SER = Path(__file__).parent / "series"
_rng = np.random.default_rng(0)


def _chk(name: str, a: float, b: float, tol: float = 1e-9) -> None:
    ok = abs(a - b) <= tol
    print(f"  [{'PASS' if ok else 'FAIL'}] {name:34s} ours={a:.6g} ref={b:.6g}")


def cross_implementation() -> None:
    print("=== (A) cross-implementation (ours vs an independent computation) ===")
    # gini vs the mean-absolute-difference definition G = MAD / (2·mean)
    x = _rng.exponential(size=800)
    mad = np.abs(x[:, None] - x[None, :]).mean()
    _chk("gini vs mean-abs-difference", gini(x), mad / (2 * x.mean()))

    # effective_dimensionality vs sklearn PCA participation ratio
    v = _rng.normal(size=(1500, 30)) @ _rng.normal(size=(30, 30))
    ev = PCA().fit(v).explained_variance_
    _chk("effective_dim vs sklearn PCA",
         effective_dimensionality(v), ev.sum() ** 2 / (ev ** 2).sum(), tol=1e-6)

    # cluster_entropy vs scipy entropy + the Miller-Madow term
    a = _rng.integers(0, 12, size=400)
    counts = np.bincount(a, minlength=12)
    mm = sp_entropy(counts / counts.sum()) + ((counts > 0).sum() - 1) / (2 * a.size)
    _chk("cluster_entropy vs scipy+MM", cluster_entropy(a, 12), mm)

    # mean_pairwise_cosine vs an explicit double loop (small n)
    w = _rng.normal(size=(40, 8))
    wn = w / np.linalg.norm(w, axis=1, keepdims=True)
    sims = [1 - wn[i] @ wn[j] for i in range(40) for j in range(i + 1, 40)]
    _chk("mean_pairwise vs explicit loop",
         mean_pairwise_cosine_distance(w), float(np.mean(sims)), tol=1e-9)

    # ols slope vs numpy polyfit
    xx = np.arange(60.0)
    yy = 2.5 * xx + _rng.normal(size=60)
    _chk("ols slope vs np.polyfit", ols_trend(xx, yy)["slope"],
         float(np.polyfit(xx, yy, 1)[0]), tol=1e-8)

    # standardized_effect vs manual slope·range/sd
    se = standardized_effect(xx, yy)
    man = float(np.polyfit(xx, yy, 1)[0]) * (xx.max() - xx.min()) / float(np.std(yy, ddof=1))
    _chk("standardized_effect vs manual", se["total_change_sd"], man, tol=1e-8)

    # residual_trend year_coef vs numpy normal-equations OLS
    ctrl = _rng.normal(size=60)
    dm = np.column_stack([np.ones(60), xx, ctrl])
    beta = np.linalg.solve(dm.T @ dm, dm.T @ yy)
    _chk("residual year_coef vs normal-eqns",
         residual_trend(xx, yy, [ctrl], n_perm=200)["year_coef"],
         float(beta[1]), tol=1e-6)

    # reference-canonicity Spearman vs scipy spearmanr on a hand-built pair
    yrs = np.array([2000] * 4 + [2005] * 4)
    refs = [["A", "B"], ["A"], ["A", "B", "C"], ["B"]] * 2  # identical 2000/2005
    row = reference_canonicity(yrs, refs, top_n=50, deltas=(5,))[0]
    # by construction 2000==2005 → perfect rank agreement
    _chk("reference stability (identical yrs)=1", row["canon_spearman_d5"], 1.0)


def placebo_null() -> None:
    print("\n=== (B) placebo / null (no signal in → no trend out) ===")
    # B1: shuffle the year labels of the REAL CS ratios → trend must vanish
    sc = json.loads((_SER / "semantic-canonical.json").read_text())["fields"]
    dem = {int(y): v for y, v in
           json.loads((_SER / "demographic-joint.json").read_text())["cs"].items()}
    sem = sc["cs"]["semantic"]
    yrs = sorted(int(y) for y in sem if 1970 <= int(y) <= 2024 and int(y) in dem)
    ce = np.array([sem[str(y)]["cluster_entropy"] for y in yrs])
    d = np.array([dem[y] for y in yrs])
    ratio = ce / d
    perm = permutation_slope_test(np.array(yrs, float), ratio, n_perm=5000, seed=1)
    print(f"  real CS cluster_entropy ratio: sig(perm)={perm['significant']} "
          f"(this is the finding — should be True)")
    # now shuffle YEAR labels: destroys any real year-trend
    sh_rng = np.random.default_rng(7)
    false_pos = 0
    for i in range(200):
        yr_sh = sh_rng.permutation(np.array(yrs, float))
        if permutation_slope_test(yr_sh, ratio, n_perm=500, seed=i)["significant"]:
            false_pos += 1
    print(f"  [{'PASS' if false_pos/200 < 0.03 else 'FAIL'}] year-shuffled CS ratio "
          f"significant in {false_pos}/200 shuffles (expect ~1% — no leak)")

    # B2: random-noise 'embeddings', MATCHED N per year → NO *significant* trend.
    # (The right null criterion is permutation significance, not raw σ: these
    # series are constant to ~4 decimals, so σ = slope·range/sd is ill-
    # conditioned — see the 8-seed investigation. The pipeline must not find a
    # SIGNIFICANT trend in noise.)
    yrs2 = np.arange(1970.0, 2025.0)
    eff, mpc = [], []
    for _ in yrs2:
        z = _rng.normal(size=(4000, 768)).astype(np.float32)  # iid noise, N matched
        eff.append(effective_dimensionality(z))
        mpc.append(mean_pairwise_cosine_distance(
            z, max_sample=1500, seed=int(_rng.integers(1_000_000))))
    for label, series in [("effective_dim", eff), ("pairwise", mpc)]:
        arr = np.array(series)
        sig = permutation_slope_test(yrs2, arr, n_perm=2000, seed=1)["significant"]
        print(f"  [{'PASS' if not sig else 'FAIL'}] random-embed {label}: "
              f"perm-significant={sig} (raw range {np.ptp(arr):.2e} — near-"
              f"constant; correct null criterion is significance)")


def calibration_repro() -> None:
    print("\n=== (C) permutation calibration + reproducibility ===")
    # C1: permutation false-positive rate on pure-noise series ≈ alpha=0.01
    sig = 0
    for i in range(1000):
        y = _rng.normal(size=55)
        if permutation_slope_test(np.arange(55.0), y, n_perm=500, seed=i)["significant"]:
            sig += 1
    rate = sig / 1000
    print(f"  [{'PASS' if rate < 0.03 else 'FAIL'}] permutation false-positive rate "
          f"= {rate:.3f} on noise (alpha=0.01)")

    # C2: a divergence_test on a KNOWN-null (both series ∝ same trend) → not confirmed
    yr = np.arange(1970.0, 2025.0)
    base = 1.0 + 0.02 * (yr - 1970) + _rng.normal(scale=0.01, size=55)
    semdict = {"cluster_entropy": 5 * base, "effective_dimensionality": 200 * base,
               "mean_pairwise_cosine": 0.5 * base}
    res = divergence_test(yr, base, semdict, 0.3 + 0.003 * (yr - 1970), n_perm=2000)
    print(f"  [{'PASS' if not res['divergence_confirmed'] else 'FAIL'}] "
          f"proportional (null) series → divergence_confirmed="
          f"{res['divergence_confirmed']} (expect False)")


def main() -> None:
    cross_implementation()
    placebo_null()
    calibration_repro()
    print("\ndone.")


if __name__ == "__main__":
    main()
