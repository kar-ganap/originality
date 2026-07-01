"""Phase 2.2 WS-E — assemble the 3 series + run the pre-registered divergence test.

Combines:
  - demographic: joint (gender × country × career-stage) plurality per
    (year, field) via `build_joint_plurality_series` on the regenerated
    Phase-1.3 substrate (the pre-registered denominator).
  - semantic + canonical: from `series/semantic-canonical.json` (WS-D).

Runs `divergence_test` per field (CS then Physics) with the PA-2 permutation
null + 0.1σ effect-size floor. PA-3: effective_dimensionality is set NaN (→
dropped from its ratio) for years with < 768 papers (degenerate). Detects the
pre-registered MIXED verdict (cluster-entropy vs effective-dim disagree).

Output: `series/divergence-verdict.json` + a printed summary.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from whitespace2.demographics import build_joint_plurality_series
from whitespace2.divergence import divergence_test, standardized_effect

_SER = Path(__file__).parent / "series"
_YEAR_MIN, _YEAR_MAX = 1970, 2024
_DEGEN_N = 768
_N_PERM = 10_000


def _demographic_series(demog_dir: Path) -> dict[str, dict[int, float]]:
    """{field: {year: career_joint_shannon}} from the regenerated substrate."""
    cache = _SER / "demographic-joint.json"
    if cache.exists():
        raw = json.loads(cache.read_text())
        return {f: {int(y): v for y, v in d.items()} for f, d in raw.items()}
    rows = build_joint_plurality_series(
        demog_dir / "authorships.parquet",
        demog_dir / "corrected.parquet",
        demog_dir / "paper-field.parquet",
    )
    out: dict[str, dict[int, float]] = {}
    for r in rows:
        if _YEAR_MIN <= r["year"] <= _YEAR_MAX:
            out.setdefault(r["field"], {})[r["year"]] = r[
                "career_joint_shannon"]
    _SER.mkdir(parents=True, exist_ok=True)
    (cache).write_text(json.dumps(
        {f: {str(y): v for y, v in d.items()} for f, d in out.items()},
        indent=2))
    return out


def _run_field(
    field: str, dem: dict[int, float], sc: dict[str, Any],
) -> dict[str, Any]:
    sem_by_year = {int(y): v for y, v in sc["semantic"].items()}
    # canonical negative control: reference-concentration Gini (should RISE)
    ref_rows = sc["canonical"]["reference_canonicity"]
    canon_by_year = {r["year"]: r["ref_gini"] for r in ref_rows}

    years = sorted(
        y for y in sem_by_year
        if _YEAR_MIN <= y <= _YEAR_MAX and y in dem and y in canon_by_year
    )
    yr = np.array(years, dtype=float)
    demv = np.array([dem[y] for y in years], dtype=float)
    canon = np.array([canon_by_year[y] for y in years], dtype=float)

    def _series(metric: str, degen_nan: bool) -> np.ndarray[Any, Any]:
        vals = []
        for y in years:
            cell = sem_by_year[y]
            v = cell[metric]
            if degen_nan and cell["n_used"] < _DEGEN_N:
                v = float("nan")     # PA-3: drop degenerate years from this ratio
            vals.append(v)
        return np.array(vals, dtype=float)

    semantic = {
        "cluster_entropy": _series("cluster_entropy", degen_nan=False),
        "effective_dimensionality": _series(
            "effective_dimensionality", degen_nan=True),
        "mean_pairwise_cosine": _series("mean_pairwise_cosine", degen_nan=False),
    }
    res = divergence_test(yr, demv, semantic, canon, n_perm=_N_PERM)

    # ---- RAW absolute trends (the confound diagnostic) ----
    # The ratio (semantic/demographic) falls whenever demographic OUTPACES
    # semantic — even if semantic RISES. Claim #13 requires semantic to
    # stagnate/DECLINE in absolute terms, so the raw trends are load-bearing.
    def _raw(series: np.ndarray[Any, Any]) -> float | None:
        m = ~np.isnan(series)
        return standardized_effect(yr[m], series[m])["total_change_sd"]

    raw = {"demographic": _raw(demv),
           **{m: _raw(s) for m, s in semantic.items()}}
    prim = [raw["cluster_entropy"], raw["effective_dimensionality"]]

    # PA-registered MIXED verdict: primaries disagree in the RATIO direction.
    d_ce = res["ratio_trends"]["cluster_entropy"]["direction"]
    d_ed = res["ratio_trends"]["effective_dimensionality"]["direction"]
    ratio_verdict = res["verdict"]
    if ratio_verdict != "substrate_broken" and {"up", "down"} <= {d_ce, d_ed}:
        ratio_verdict = "mixed"

    # HONEST verdict on Claim #13 (semantic stagnates/declines?), from the RAW
    # absolute primary trends — NOT the denominator-confounded ratio.
    up = [r for r in prim if r is not None and r > 0.1]
    down = [r for r in prim if r is not None and r < -0.1]
    if not res["substrate_ok"]:
        honest = "substrate_broken"
    elif up and down:
        honest = "mixed_absolute (primary semantic metrics disagree in sign)"
    elif len(up) == 2:
        honest = ("null_semantic_rises (both primary semantic metrics RISE in "
                  "absolute terms; the falling ratio is demographic-denominator-"
                  "driven, NOT semantic decline — Claim #13 not supported)")
    elif len(down) == 2:
        honest = "divergence (both primary semantic metrics decline absolutely)"
    else:
        honest = "inconclusive"

    return {
        "field": field, "n_years": len(years),
        "year_range": [years[0], years[-1]] if years else None,
        "n_degenerate_years": int(sum(
            1 for y in years if sem_by_year[y]["n_used"] < _DEGEN_N)),
        "ratio_verdict_CONFOUNDED": ratio_verdict,
        "honest_verdict": honest,
        "raw_absolute_trends_sd": raw,
        "substrate_ok": res["substrate_ok"],
        "primary_directions": {"cluster_entropy": d_ce,
                               "effective_dimensionality": d_ed},
        "ratio_trends": {
            m: {"slope": t["slope"], "direction": t["direction"],
                "perm_pvalue": t["permutation"]["perm_pvalue"],
                "perm_significant": t["permutation"]["significant"],
                "total_change_sd": t["effect"]["total_change_sd"]}
            for m, t in res["ratio_trends"].items()},
        "negative_control": {
            "slope": res["negative_control"]["slope"],
            "direction": res["negative_control"]["direction"],
            "perm_significant":
                res["negative_control"]["permutation"]["significant"]},
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--demog-dir", required=True, type=Path)
    args = ap.parse_args()

    sc = json.loads((_SER / "semantic-canonical.json").read_text())["fields"]
    dem = _demographic_series(args.demog_dir)
    print(f"demographic years: "
          f"cs={len(dem.get('cs', {}))}, physics={len(dem.get('physics', {}))}",
          flush=True)

    verdicts = {}
    for field in ("cs", "physics"):
        v = _run_field(field, dem.get(field, {}), sc[field])
        verdicts[field] = v
        print(f"\n===== {field.upper()} =====", flush=True)
        print(f"  ratio verdict (CONFOUNDED): {v['ratio_verdict_CONFOUNDED']}",
              flush=True)
        print(f"  HONEST verdict:             {v['honest_verdict']}", flush=True)
        print(f"  years {v['year_range']} (n={v['n_years']}, "
              f"{v['n_degenerate_years']} degenerate)", flush=True)
        print("  RAW absolute trends (σ over window):", flush=True)
        for m, r in v["raw_absolute_trends_sd"].items():
            print(f"    {m:26s} {r:+.2f}σ" if r is not None
                  else f"    {m}: n/a", flush=True)
        nc = v["negative_control"]
        print(f"  neg-control (ref Gini): dir={nc['direction']} "
              f"sig={nc['perm_significant']}  substrate_ok={v['substrate_ok']}",
              flush=True)

    (_SER / "divergence-verdict.json").write_text(
        json.dumps(verdicts, indent=2))
    print(f"\nwrote {_SER}/divergence-verdict.json", flush=True)


if __name__ == "__main__":
    main()
