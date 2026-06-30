"""Phase 1.3 production driver — chains the demographic-annotation pipeline.

Runs the full Step 1→6 chain on a §0 corpus parquet:

  extract_authorships            (Step 1)
  validate_disambiguation        (Step 2 — H1 career screen + H2 ORCID)
  annotate_gender_country        (Step 3 — gg primary + Genderize x-val)
  sample_for_namsor              (Step 4 — stratified NamSor bias sample)
  compute_confusion_matrix       (Step 5a — per-region gg-vs-NamSor matrix)
  apply_bias_correction          (Step 5b — per-author calibrated gender)
  build_paper_field_map          (Step 5c — paper → cs/physics)
  build_cell_coverage_table      (Step 5c — per-cell expected gender counts)
  build_coverage_table           (Step 6 — per-cell coverage + diversity)

Modes:
  --no-api   gg-only: skip Genderize + NamSor, drive apply_bias_correction
             with an EMPTY confusion matrix (everything → identity). Zero
             API quota; validates the non-API mechanics end to end.
  (default)  keyed run: Genderize on gg-unknown names (cap --genderize-max)
             + NamSor on the stratified sample (cap --namsor-max).

Keys are read from .env (GENDERIZE_API_KEY / NAMSOR_API_KEY) or the shell
env. All intermediate parquets + run-summary.json land in --outdir, and
the H1-H8 / E1-E4 measurements are printed and saved.

Usage:
  uv run python experiments/phase-1.3/run_pipeline.py \
      --source data/metadata/heldouts-smoke-v3.parquet \
      --outdir experiments/phase-1.3/smoke-noapi --no-api
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

from whitespace2.demographics import (
    annotate_gender_country,
    apply_bias_correction,
    build_cell_coverage_table,
    build_coverage_table,
    build_paper_field_map,
    compute_confusion_matrix,
    extract_authorships,
    sample_for_namsor,
    validate_disambiguation,
)

# Pre-registered acceptance thresholds (Phase 1.3 plan §"Pre-registered
# hypotheses"). The driver reports each measurement + a pass flag; the
# authoritative evaluation lives in verify-results.md.
_H3_GENDER_COVERAGE_MIN = 0.45
_H4_COUNTRY_COVERAGE_MIN = 0.50
_H5_CI_HALFWIDTH_MAX = 0.10   # per-region, E1 trigger if exceeded
_H6_NAMSOR_SPEND_MAX = 10.0   # USD; free tier → $0
_H8_FEMALE_SHARE_CI_HALFWIDTH_MAX = 0.025  # headline cells


def _load_dotenv(env_path: Path) -> None:
    """Minimal .env loader (KEY=VALUE lines) — avoids a python-dotenv dep.

    Does not overwrite a variable already set in the shell environment.
    """
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def _headline_cells(coverage_parquet: Path) -> list[dict[str, Any]]:
    """Return the distinct-author coverage rows (the headline unit)."""
    df = pq.read_table(str(coverage_parquet)).to_pandas()
    df = df[df["unit"] == "distinct_authors"]
    return [dict(r) for r in df.to_dict("records")]


def run(
    *,
    source: Path,
    outdir: Path,
    no_api: bool,
    genderize_max: int,
    namsor_max: int,
    n_bootstrap: int,
    label: str,
    reuse_matrix: Path | None = None,
    no_genderize: bool = False,
) -> dict[str, Any]:
    outdir.mkdir(parents=True, exist_ok=True)
    summary: dict[str, Any] = {"label": label, "source": str(source),
                               "outdir": str(outdir), "no_api": no_api,
                               "steps": {}}
    t0 = time.time()

    # Genderize runs unless suppressed; NamSor sampling runs only when we're
    # not reusing a precomputed matrix (the v2 robustness pair reuses v3's —
    # per-region bias is §0-version-independent — to spend zero quota).
    do_genderize = not (no_api or no_genderize)
    do_namsor = not no_api and reuse_matrix is None
    genderize_key = (
        os.environ.get("GENDERIZE_API_KEY") if do_genderize else None
    )
    namsor_key = os.environ.get("NAMSOR_API_KEY") if do_namsor else None
    if do_namsor and not namsor_key:
        raise SystemExit(
            "NAMSOR_API_KEY not found in env/.env — set it, or pass "
            "--reuse-matrix <json> / --no-api",
        )
    summary["do_genderize"] = do_genderize
    summary["do_namsor"] = do_namsor
    summary["reuse_matrix"] = str(reuse_matrix) if reuse_matrix else None

    # ---- Step 1: extract authorships ----
    print(f"[{label}] Step 1 — extract_authorships …", flush=True)
    auth_pq = outdir / "authorships.parquet"
    summary["steps"]["1_extract"] = extract_authorships(source, auth_pq)
    print(f"    {summary['steps']['1_extract']['n_author_paper_rows']:,} "
          f"author-paper rows", flush=True)

    # ---- Step 2: disambiguation validation ----
    print(f"[{label}] Step 2 — validate_disambiguation …", flush=True)
    disambig = validate_disambiguation(auth_pq, outdir / "disambig.json")
    summary["steps"]["2_disambig"] = disambig

    # ---- Step 3: gender + country annotation ----
    print(f"[{label}] Step 3 — annotate_gender_country "
          f"(genderize={'on' if genderize_key else 'off'}) …", flush=True)
    per_author_pq = outdir / "per-author.parquet"
    summary["steps"]["3_annotate"] = annotate_gender_country(
        auth_pq, per_author_pq,
        genderize_api_key=genderize_key, genderize_max_names=genderize_max,
    )

    # ---- Step 4 + 5a: NamSor bias sample + confusion matrix ----
    confusion_matrix: dict[str, Any] = {}
    if reuse_matrix is not None:
        print(f"[{label}] Steps 4/5a — REUSING confusion matrix "
              f"{reuse_matrix} (zero NamSor quota)", flush=True)
        confusion_matrix = json.loads(Path(reuse_matrix).read_text())
        (outdir / "confusion-matrix.json").write_text(
            json.dumps(confusion_matrix, indent=2, default=list),
        )
        summary["steps"]["5a_confusion"] = {
            region: {"n_sample": m.get("n_sample"),
                     "max_ci_halfwidth": m.get("max_ci_halfwidth")}
            for region, m in confusion_matrix.items()
        }
        summary["steps"]["5a_confusion"]["_reused_from"] = str(reuse_matrix)
    elif do_namsor:
        print(f"[{label}] Step 4 — sample_for_namsor (max={namsor_max}) …",
              flush=True)
        ns_pq = outdir / "namsor-sample.parquet"
        assert namsor_key is not None  # guaranteed by the guard above
        summary["steps"]["4_namsor"] = sample_for_namsor(
            per_author_pq, ns_pq,
            namsor_api_key=namsor_key, max_names=namsor_max,
        )
        print(f"[{label}] Step 5a — compute_confusion_matrix …", flush=True)
        confusion_matrix = compute_confusion_matrix(ns_pq, per_author_pq)
        # Persist the matrix (tuples → lists) for the record + the E2 sweep.
        (outdir / "confusion-matrix.json").write_text(
            json.dumps(confusion_matrix, indent=2, default=list),
        )
        summary["steps"]["5a_confusion"] = {
            region: {
                "n_sample": m["n_sample"],
                "max_ci_halfwidth": m["max_ci_halfwidth"],
            }
            for region, m in confusion_matrix.items()
        }
    else:
        print(f"[{label}] Steps 4/5a SKIPPED (--no-api): empty matrix → "
              f"apply_bias_correction is identity everywhere", flush=True)

    # ---- Step 5b: apply bias correction ----
    print(f"[{label}] Step 5b — apply_bias_correction …", flush=True)
    corrected_pq = outdir / "corrected.parquet"
    summary["steps"]["5b_correct"] = apply_bias_correction(
        per_author_pq, corrected_pq,
        confusion_matrix=confusion_matrix, region_axis="script",
    )

    # ---- Step 5c: paper → field map ----
    print(f"[{label}] Step 5c — build_paper_field_map …", flush=True)
    field_pq = outdir / "paper-field.parquet"
    summary["steps"]["5c_field_map"] = build_paper_field_map(source, field_pq)

    # ---- Step 5c: per-cell expected gender counts ----
    print(f"[{label}] Step 5c — build_cell_coverage_table …", flush=True)
    cells_pq = outdir / "cells.parquet"
    summary["steps"]["5c_cells"] = build_cell_coverage_table(
        auth_pq, corrected_pq, field_pq, cells_pq, n_bootstrap=n_bootstrap,
    )

    # ---- Step 6: coverage + diversity table ----
    print(f"[{label}] Step 6 — build_coverage_table …", flush=True)
    coverage_pq = outdir / "coverage.parquet"
    summary["steps"]["6_coverage"] = build_coverage_table(
        auth_pq, corrected_pq, field_pq, coverage_pq, n_bootstrap=n_bootstrap,
    )

    summary["elapsed_sec"] = round(time.time() - t0, 1)

    # ---- Hypothesis measurements (driver-level; verify-results.md is canon) --
    hyp: dict[str, Any] = {}
    s = summary["steps"]
    hyp["H1_cross_era_merger_rate"] = {
        "value": s["2_disambig"]["h1_career_length_screen"]["flagged_fraction"],
        "passes": s["2_disambig"]["h1_passes"],
    }
    hyp["H2_orcid_agreement"] = {
        "value": s["2_disambig"]["h2_orcid_consistency"][
            "paper_level_agreement_rate"],
        "passes": s["2_disambig"]["h2_passes"],
    }
    hyp["H3_gender_coverage"] = {
        "value": s["3_annotate"]["gender_confident_rate"],
        "threshold": _H3_GENDER_COVERAGE_MIN,
        "passes": s["3_annotate"]["gender_confident_rate"]
        >= _H3_GENDER_COVERAGE_MIN,
    }
    hyp["H4_country_coverage"] = {
        "value": s["3_annotate"]["country_coverage_rate"],
        "threshold": _H4_COUNTRY_COVERAGE_MIN,
        "passes": s["3_annotate"]["country_coverage_rate"]
        >= _H4_COUNTRY_COVERAGE_MIN,
    }
    # H5 from the matrix (computed OR reused); skip only when there's no
    # matrix at all (--no-api). Drop the bookkeeping key when present.
    matrix_regions = {k: v for k, v in confusion_matrix.items()
                      if isinstance(v, dict) and "max_ci_halfwidth" in v}
    if matrix_regions:
        max_hw = max(m["max_ci_halfwidth"] for m in matrix_regions.values())
        hyp["H5_namsor_ci_halfwidth"] = {
            "max_over_regions": max_hw,
            "threshold": _H5_CI_HALFWIDTH_MAX,
            "passes": max_hw <= _H5_CI_HALFWIDTH_MAX,
            "E1_fired": max_hw > _H5_CI_HALFWIDTH_MAX,
            "reused": reuse_matrix is not None,
        }
    if do_namsor:
        hyp["H6_namsor_spend_usd"] = {
            "value": 0.0,  # free tier
            "n_calls": s["4_namsor"]["namsor_summary"]["n_calls"],
            "threshold": _H6_NAMSOR_SPEND_MAX, "passes": True,
        }
        hyp["H7_namsor_per_region"] = {
            "n_sampled_by_region": s["4_namsor"]["n_sampled_by_region"],
            "note": "per-headline-CELL counts computed in verify-results.md",
        }
    # H8: female_share CI half-width on headline (distinct-author) cells
    headline = _headline_cells(coverage_pq)
    hw = [c["female_share_ci_halfwidth"] for c in headline]
    max_hw8 = max(hw) if hw else 0.0
    hyp["H8_female_share_ci_halfwidth"] = {
        "max_over_headline_cells": max_hw8,
        "threshold": _H8_FEMALE_SHARE_CI_HALFWIDTH_MAX,
        "passes": max_hw8 <= _H8_FEMALE_SHARE_CI_HALFWIDTH_MAX,
        "n_cells": len(headline),
        "note": "smoke cells are tiny → wide CIs expected; gate is for "
                "production-scale headline cells",
    }
    summary["hypotheses"] = hyp

    (outdir / "run-summary.json").write_text(json.dumps(summary, indent=2))
    return summary


def _print_report(summary: dict[str, Any]) -> None:
    print("\n" + "=" * 64)
    print(f"RUN COMPLETE — {summary['label']}  ({summary['elapsed_sec']}s)")
    print("=" * 64)
    s = summary["steps"]
    print(f"papers={s['1_extract']['n_papers']:,}  "
          f"author-paper-rows={s['1_extract']['n_author_paper_rows']:,}  "
          f"unique-authors={s['3_annotate']['n_unique_authors']:,}")
    print(f"field map: cs={s['5c_field_map']['n_cs']:,} "
          f"physics={s['5c_field_map']['n_physics']:,} "
          f"unassigned={s['5c_field_map']['n_unassigned']:,}")
    print(f"cells (distinct): {s['6_coverage']['n_cells_by_unit']}")
    print("-" * 64)
    for name, h in summary["hypotheses"].items():
        flag = ""
        if "passes" in h:
            flag = "PASS" if h["passes"] else "FAIL"
        print(f"  {name:34s} {flag:4s} {json.dumps({k: v for k, v in h.items() if k != 'note'})}")
    print("=" * 64 + "\n")


def main() -> None:
    p = argparse.ArgumentParser(description="Phase 1.3 pipeline driver")
    p.add_argument("--source", required=True, type=Path)
    p.add_argument("--outdir", required=True, type=Path)
    p.add_argument("--no-api", action="store_true",
                   help="gg-only; skip Genderize + NamSor (zero quota)")
    p.add_argument("--reuse-matrix", type=Path, default=None,
                   help="reuse a precomputed confusion-matrix JSON (skip "
                        "NamSor; the v2 robustness pair reuses v3's)")
    p.add_argument("--no-genderize", action="store_true",
                   help="skip Genderize (gg-only) but keep NamSor/matrix")
    p.add_argument("--genderize-max", type=int, default=2500)
    p.add_argument("--namsor-max", type=int, default=2500)
    p.add_argument("--n-bootstrap", type=int, default=10_000)
    p.add_argument("--label", default="run")
    p.add_argument("--env", type=Path, default=Path(".env"))
    args = p.parse_args()

    _load_dotenv(args.env)
    summary = run(
        source=args.source, outdir=args.outdir, no_api=args.no_api,
        genderize_max=args.genderize_max, namsor_max=args.namsor_max,
        n_bootstrap=args.n_bootstrap, label=args.label,
        reuse_matrix=args.reuse_matrix, no_genderize=args.no_genderize,
    )
    _print_report(summary)


if __name__ == "__main__":
    main()
