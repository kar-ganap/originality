"""Phase 2.3 — the subfield mechanism regression grid + verdict.

Reads the per-subfield metric tables (`subfield-metrics-{concepts,clusters}.json`)
and runs the pre-registered estimator across the 4-spec robustness grid
({SciNCL, Qwen3} embedding × {sub-concepts, K=50 clusters} subfield):

  divergence_magnitude(s) ~ γ₁·canon_concentration(s) + β·log_size(s) [+ field FE]

reporting γ₁ (sign, magnitude, permutation p, VIF, standardized) per spec + the
per-field slopes for the concept definition. Verdict per the pre-registered
decision rule:

  - SUPPORTS_REFRAMING — γ₁ not significant AND |standardized γ₁| < 0.3 in ALL
    4 specs (canon-concentration ⟂ divergence; independence).
  - LOCALIZED_MECHANISM — γ₁ > 0, significant, consistent sign in ALL 4 specs.
  - MIXED — otherwise (reported honestly, not cherry-picked).

G1 negative control (substrate sanity): the aggregate reference-canonicity Gini
rises over the window (loaded from the committed Phase-2.2 series). Output:
`subfield-mechanism-results.{md,json}`.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

from whitespace2.divergence import permutation_slope_test
from whitespace2.subfield_divergence import subfield_regression

_STD_SMALL = 0.3          # |standardized γ₁| below this = "≈ 0" (independence)
_HERE = Path(__file__).parent


def _load(metrics_dir: Path, definition: str) -> dict[str, Any]:
    return json.loads(
        (metrics_dir / f"subfield-metrics-{definition}.json").read_text())


def _spec(
    rows: list[dict[str, Any]], embedding: str, use_field_fe: bool,
) -> dict[str, Any]:
    canon = np.array([r["canon_concentration"] for r in rows])
    log_size = np.array([r["log_size"] for r in rows])
    div = np.array([r[f"divergence_{embedding}"] for r in rows])
    field = np.array([r["field"] for r in rows]) if use_field_fe else None
    res = subfield_regression(canon, div, log_size, field=field, seed=46)
    # audit context: component means + simple correlations
    res["mean_semantic_trend"] = float(np.mean(
        [r[f"semantic_trend_{embedding}"] for r in rows]))
    res["mean_demographic_trend"] = float(np.mean(
        [r["demographic_trend"] for r in rows]))
    res["corr_canon_logsize"] = float(np.corrcoef(canon, log_size)[0, 1])
    res["corr_canon_divergence"] = float(np.corrcoef(canon, div)[0, 1])
    return res


def _negative_control() -> dict[str, Any]:
    """G1: aggregate reference-canonicity Gini rises (Phase-2.2 committed series)."""
    sc = json.loads(
        (_HERE.parent / "phase-2.2" / "series"
         / "semantic-canonical.json").read_text())["fields"]
    out: dict[str, Any] = {}
    for field in ("cs", "physics"):
        rc = sc[field]["canonical"]["reference_canonicity"]
        rc = [r for r in rc if r["year"] <= 2023]
        yrs = np.array([r["year"] for r in rc], dtype=float)
        gini = np.array([r["ref_gini"] for r in rc], dtype=float)
        t = permutation_slope_test(yrs, gini, n_perm=10_000, seed=46)
        out[field] = {"direction": "up" if (t["slope"] or 0) > 0 else "down",
                      "slope": t["slope"], "significant": t["significant"]}
    out["passes"] = all(
        out[f]["direction"] == "up" and out[f]["significant"]
        for f in ("cs", "physics"))
    return out


def _verdict(grid: dict[str, dict[str, Any]]) -> str:
    specs = list(grid.values())
    all_ns = all(not s["significant"] for s in specs)
    all_small = all(abs(s["gamma1_standardized"]) < _STD_SMALL for s in specs)
    all_pos_sig = all(s["gamma1"] > 0 and s["significant"] for s in specs)
    all_neg_sig = all(s["gamma1"] < 0 and s["significant"] for s in specs)
    if all_ns and all_small:
        return "SUPPORTS_REFRAMING (γ₁ ≈ 0 across all specs — independence)"
    if all_pos_sig:
        return "LOCALIZED_MECHANISM (γ₁ > 0, significant, all specs)"
    if all_neg_sig:
        return ("INVERSE (γ₁ < 0 all specs — canon-concentrated subfields "
                "diverge LESS; not the hypothesized mechanism)")
    return "MIXED / metric-or-definition-dependent (reported honestly)"


def _fmt(s: dict[str, Any]) -> str:
    ci = s["gamma1_ci95"]
    return (f"γ₁={s['gamma1']:+.4f} "
            f"[{ci[0]:+.4f}, {ci[1]:+.4f}]  "
            f"std={s['gamma1_standardized']:+.3f}σ  "
            f"perm_p={s['gamma1_perm_pvalue']:.4f}"
            f"{'*' if s['significant'] else ''}  "
            f"VIF={s['vif_canon']:.2f}  n={s['n_subfields']}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--metrics-dir", required=True, type=Path)
    args = ap.parse_args()

    cdata = _load(args.metrics_dir, "concepts")
    kdata = _load(args.metrics_dir, "clusters")
    concepts = [r for r in cdata["subfields"] if r["eligible"]]
    clusters = [r for r in kdata["subfields"] if r["eligible"]]
    embeddings = cdata.get("embeddings", ["scincl", "qwen3"])

    grid: dict[str, dict[str, Any]] = {}
    for emb in embeddings:
        grid[f"{emb}|concepts"] = _spec(concepts, emb, use_field_fe=True)
        grid[f"{emb}|clusters"] = _spec(clusters, emb, use_field_fe=False)

    # per-field slopes (concept definition)
    per_field: dict[str, dict[str, Any]] = {}
    for fld in ("cs", "physics"):
        sub = [r for r in concepts if r["field"] == fld]
        if len(sub) >= 6:
            per_field[fld] = {
                emb: _spec(sub, emb, use_field_fe=False)
                for emb in embeddings}

    neg = _negative_control()
    verdict = _verdict(grid)

    result = {
        "verdict": verdict,
        "embeddings": embeddings,
        "negative_control_G1": neg,
        "n_eligible": {"concepts": len(concepts), "clusters": len(clusters)},
        "grid": grid,
        "per_field_concepts": per_field,
        "std_small_threshold": _STD_SMALL,
    }
    (args.metrics_dir / "subfield-mechanism-results.json").write_text(
        json.dumps(result, indent=2))

    # ---- console + markdown ----
    lines: list[str] = []
    lines.append(f"VERDICT: {verdict}\n")
    lines.append(f"G1 negative control (canon Gini rises): "
                 f"passes={neg['passes']}  "
                 f"cs={neg['cs']['direction']}/{neg['cs']['significant']}  "
                 f"physics={neg['physics']['direction']}/"
                 f"{neg['physics']['significant']}\n")
    lines.append(f"eligible subfields: concepts={len(concepts)}, "
                 f"clusters={len(clusters)}\n")
    lines.append("4-spec grid (γ₁ = slope of divergence on canon-concentration, "
                 "controlling for log size):")
    for name, s in grid.items():
        lines.append(f"  {name:16s}  {_fmt(s)}")
        lines.append(f"                    mean_sem_trend="
                     f"{s['mean_semantic_trend']:+.2f}σ  "
                     f"mean_dem_trend={s['mean_demographic_trend']:+.2f}σ  "
                     f"corr(canon,logsize)={s['corr_canon_logsize']:+.2f}  "
                     f"corr(canon,div)={s['corr_canon_divergence']:+.2f}")
    if per_field:
        lines.append("\nper-field (concepts):")
        for fld, d in per_field.items():
            for emb, s in d.items():
                lines.append(f"  {fld}/{emb:8s}  {_fmt(s)}")
    text = "\n".join(lines)
    print(text)
    (args.metrics_dir / "subfield-mechanism-summary.txt").write_text(text + "\n")


if __name__ == "__main__":
    main()
