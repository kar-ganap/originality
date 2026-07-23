"""Phase 3 noise-floor diagnostics — run the locked grid and classify each estimand.

    uv run --extra dev python experiments/phase-3-resolution/run_diagnostics.py     # grid + analyze
    uv run --extra dev python experiments/phase-3-resolution/run_diagnostics.py --from-raw <path>

Implements `docs/resolution-map-phase3-prereg.md` exactly. The expensive grid is persisted to
`raw-grid.json` (per-seed steady states) BEFORE any estimand logic runs, so re-analysis never
re-runs the model. Nothing here chooses a threshold — the SESOIs, the grid, and the classification
rule are all pinned in the pre-registration; this only executes them.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

from whitespace3.channel import run
from whitespace3.conformity import logN_slope_ci
from whitespace3.resolution import classify, crossover_exists, mean_ci, seed_cv

# --- the locked grid (pre-reg §"fixed diagnostic grid") --------------------------------------
LAMBDAS = [0.0, 0.1, 0.5, 2.0]
NS = [30, 120, 480]
FS = [0.3, 0.6]
MODES = ["targeted", "uniform"]
SEEDS = list(range(30))
BURN_IN = 30
BASE = dict(c0=5, epsilon=0.3, b=0.5, generations=60, alpha=0.15)  # f varies; mode varies
SESOI_LEVEL = 0.20  # WS1-tied floor for E1/E2/E3 (pre-reg)
E3_ISOLATED_FRAC = 0.2
E3_POINT = dict(mode="targeted", f=0.6, lam=0.5, n=120)  # C-favouring, where isolation shields
RUNS_DIR = Path(__file__).parent / "runs"


def _steady(result: dict, metric: str) -> float:
    arr = np.asarray(result[metric], dtype=float)
    return float(np.nanmean(arr[BURN_IN:]))


def run_grid() -> dict:
    """One `channel.run` per (mode, f, λ, N, seed); extract Vstruct/W/C steady states."""
    store: dict = {}
    t0 = time.time()
    total = len(MODES) * len(FS) * len(LAMBDAS) * len(NS) * len(SEEDS)
    done = 0
    for mode in MODES:
        store[mode] = {}
        for f in FS:
            store[mode][str(f)] = {}
            for lam in LAMBDAS:
                cell = {"Vstruct": {}, "W": {}, "C": {}, "V": {}}
                for n in NS:
                    vs, ws, cs, vt = [], [], [], []
                    for s in SEEDS:
                        r = run(n, seed=s, lam=lam, mode=mode, f=f, **BASE)
                        vs.append(_steady(r, "Vstruct"))
                        ws.append(_steady(r, "W"))
                        cs.append(_steady(r, "C"))
                        vt.append(_steady(r, "V"))  # total-V, for the E4 crossover
                        done += 1
                    cell["Vstruct"][str(n)] = vs
                    cell["W"][str(n)] = ws
                    cell["C"][str(n)] = cs
                    cell["V"][str(n)] = vt
                    print(f"  [{done}/{total}] {mode} f={f} λ={lam} N={n}  "
                          f"({time.time() - t0:.0f}s)", file=sys.stderr)
                store[mode][str(f)][str(lam)] = cell
    return store


def run_e3() -> dict:
    """Dedicated isolation point (E3 is undefined at isolated_frac=0; grid omitted it)."""
    p = E3_POINT
    iso, conf = [], []
    for s in SEEDS:
        r = run(p["n"], seed=s, lam=p["lam"], mode=p["mode"], f=p["f"],
                isolated_frac=E3_ISOLATED_FRAC, **BASE)
        iso.append(_steady(r, "Vstruct_iso"))
        conf.append(_steady(r, "Vstruct_conf"))
    return {"point": p, "isolated_frac": E3_ISOLATED_FRAC, "iso": iso, "conf": conf}


# --- estimand analysis (reads the raw store; reruns nothing) ---------------------------------


def _paired_rel_change(baseline: list[float], treated: list[float]) -> tuple[float, float, float]:
    """Mean per-seed relative change (treated vs baseline) with a seed-bootstrap CI."""
    b, t = np.asarray(baseline), np.asarray(treated)
    ok = b > 0
    rc = (t[ok] - b[ok]) / b[ok]
    lo, hi = mean_ci(rc, seed=0)
    return float(np.mean(rc)), lo, hi


def analyze_e1(store: dict) -> list[dict]:
    """E1 — Vstruct level response to λ, vs the λ=0 baseline, per (mode, f, N)."""
    rows = []
    for mode in MODES:
        for f in FS:
            cell0 = store[mode][str(f)]["0.0"]["Vstruct"]
            for lam in LAMBDAS[1:]:
                cell = store[mode][str(f)][str(lam)]["Vstruct"]
                for n in NS:
                    base, treated = cell0[str(n)], cell[str(n)]
                    effect, lo, hi = _paired_rel_change(base, treated)
                    cls = classify(effect=effect, ci_lo=lo, ci_hi=hi,
                                   sesoi=SESOI_LEVEL, seed_cv_level=seed_cv(treated))
                    rows.append({"estimand": "E1", "mode": mode, "f": f, "lam": lam, "n": n,
                                 "effect": effect, "ci": [lo, hi], "class": cls})
    return rows


def analyze_e2(store: dict) -> list[dict]:
    """E2 (reading a) — two-channel decoupling as an N-response, per (mode, f, λ).

    Internal standard: ∂W/∂logN reliably > 0 AND ∂Vstruct/∂logN reliably < 0 (CIs on the right side
    of 0). Targeted is primary; uniform reported as contrast. This is the WS2-matching *scale*
    decoupling — not a λ-response (the original spec pointed at the wrong lever; see the pre-reg
    correction).
    """
    rows = []
    for mode in MODES:
        for f in FS:
            for lam in LAMBDAS:
                w_grid = {n: np.asarray(store[mode][str(f)][str(lam)]["W"][str(n)]) for n in NS}
                v_grid = {n: np.asarray(store[mode][str(f)][str(lam)]["Vstruct"][str(n)])
                          for n in NS}
                w_sl = logN_slope_ci(NS, w_grid)
                v_sl = logN_slope_ci(NS, v_grid)
                w_up = w_sl["lo"] > 0.0
                v_down = v_sl["hi"] < 0.0
                rows.append({"estimand": "E2", "mode": mode, "f": f, "lam": lam,
                             "w_slope": w_sl["point"], "w_ci": [w_sl["lo"], w_sl["hi"]],
                             "vstruct_slope": v_sl["point"], "vstruct_ci": [v_sl["lo"], v_sl["hi"]],
                             "usable": bool(w_up and v_down)})
    return rows


def analyze_slope(store: dict, metric: str, estimand: str) -> list[dict]:
    """E4 (metric=Vstruct) / E5 (metric=C) — per (mode, f, λ): slope of the metric on logN."""
    rows = []
    for mode in MODES:
        for f in FS:
            per_lambda = []
            for lam in LAMBDAS:
                cell = store[mode][str(f)][str(lam)][metric]
                per_seed = {n: np.asarray(cell[str(n)]) for n in NS}
                sl = logN_slope_ci(NS, per_seed)
                # determinism on the largest-N level (a clock has ~0 seed spread)
                cv = seed_cv(cell[str(NS[-1])])
                per_lambda.append({"lam": lam, "slope": sl["point"],
                                   "ci": [sl["lo"], sl["hi"]], "seed_cv": cv})
            slopes = [(x["slope"], x["ci"][0], x["ci"][1]) for x in per_lambda]
            row = {"estimand": estimand, "mode": mode, "f": f, "per_lambda": per_lambda}
            if estimand == "E4":
                row["internal_usable"] = crossover_exists(slopes)  # CI-separated sign flip
            else:  # E5 — does C depend on N (a slope CI excludes 0) and is it non-deterministic
                responds = any(x["ci"][0] > 0 or x["ci"][1] < 0 for x in per_lambda)
                deterministic = all(x["seed_cv"] < 1e-6 for x in per_lambda)
                row["internal_usable"] = bool(responds and not deterministic)
                row["deterministic"] = deterministic
            rows.append(row)
    return rows


def analyze_e3(e3: dict) -> dict:
    iso, conf = np.asarray(e3["iso"]), np.asarray(e3["conf"])
    ok = conf > 0
    rc = (iso[ok] - conf[ok]) / conf[ok]
    lo, hi = mean_ci(rc, seed=0)
    effect = float(np.mean(rc))
    cls = classify(effect=effect, ci_lo=lo, ci_hi=hi, sesoi=SESOI_LEVEL,
                   seed_cv_level=seed_cv(iso))
    return {"estimand": "E3", **e3["point"], "isolated_frac": e3["isolated_frac"],
            "effect": effect, "ci": [lo, hi], "class": cls}


def _print_report(analysis: dict) -> None:
    print("\n================  PHASE 3 VERDICT  ================\n")

    print("E1 — Vstruct level response to λ (targeted primary; USABLE = stochastic-with-signal):")
    for r in analysis["E1"]:
        if r["mode"] == "targeted":
            print(f"  f={r['f']} λ={r['lam']:<4} N={r['n']:<4} "
                  f"eff={r['effect']:+.3f} CI[{r['ci'][0]:+.3f},{r['ci'][1]:+.3f}] {r['class']}")

    print("\nE2 — N-decoupling: ∂W/∂logN>0 AND ∂Vstruct/∂logN<0 (targeted primary):")
    for r in analysis["E2"]:
        if r["mode"] == "targeted":
            print(f"  f={r['f']} λ={r['lam']:<4} "
                  f"W-slope {r['w_slope']:+.1f} CI[{r['w_ci'][0]:+.1f},{r['w_ci'][1]:+.1f}]  "
                  f"Vstr-slope {r['vstruct_slope']:+.4f} "
                  f"CI[{r['vstruct_ci'][0]:+.4f},{r['vstruct_ci'][1]:+.4f}] USABLE={r['usable']}")

    print("\nE3 — isolation Pareto (isolated_frac=0.2):")
    r = analysis["E3"]
    print(f"  {r['mode']} f={r['f']} λ={r['lam']} N={r['n']}  "
          f"(iso-conf)/conf={r['effect']:+.3f} "
          f"CI[{r['ci'][0]:+.3f},{r['ci'][1]:+.3f}]  {r['class']}")

    for est in ("E4", "E5"):
        label = "crossover (CI-separated sign flip)" if est == "E4" else "C responds to N"
        print(f"\n{est} — {label} (internal standard):")
        for r in analysis[est]:
            marks = "  ".join(f"λ{x['lam']}:{x['slope']:+.4f}[{x['ci'][0]:+.4f},{x['ci'][1]:+.4f}]"
                              for x in r["per_lambda"])
            print(f"  {r['mode']} f={r['f']}: {marks}")
            print(f"      -> internal_usable={r['internal_usable']}"
                  + (f"  deterministic={r.get('deterministic')}" if est == "E5" else ""))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-raw", type=Path, help="skip the grid; analyze a saved raw-grid.json")
    args = ap.parse_args()
    RUNS_DIR.mkdir(exist_ok=True)

    if args.from_raw:
        payload = json.loads(args.from_raw.read_text())
        store, e3 = payload["store"], payload["e3"]
    else:
        print("running grid (this is the ~40-min step)…", file=sys.stderr)
        store = run_grid()
        e3 = run_e3()
        raw_path = RUNS_DIR / "raw-grid.json"
        raw_path.write_text(json.dumps({"store": store, "e3": e3}))
        print(f"raw grid -> {raw_path}", file=sys.stderr)

    analysis = {
        "E1": analyze_e1(store),
        "E2": analyze_e2(store),
        "E3": analyze_e3(e3),
        "E4": analyze_slope(store, "V", "E4"),  # crossover on TOTAL-V (corrected)
        "E5": analyze_slope(store, "C", "E5"),
    }
    _print_report(analysis)
    out = RUNS_DIR / "phase3-verdict.json"
    out.write_text(json.dumps(analysis, indent=2))
    print(f"\nverdict -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
