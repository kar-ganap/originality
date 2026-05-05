"""Phase 0.2 Wave 3A — ORCID-linkage hand-audit aggregation.

Ingests the user-completed audit CSV (with `linkage_correct` filled
per row) and produces:
- Overall linkage-correctness rate against §4's ≥70% threshold
- Per-region rate against §4's ≥50% per-region threshold
- Pass/fail decision per the Phase 0.2 plan §4 + Phase 0.1 retro
- Per-region exclusion list (regions with rate <50%) for §9a P5
  bias-uncertainty band

`linkage_correct` is interpreted as:
- "yes" → 1.0 (correct linkage; in numerator AND denominator)
- "likely" → 1.0 (correct linkage; in numerator AND denominator)
- "no" → 0.0 (incorrect linkage; in denominator only)
- "unclear" → excluded from BOTH numerator and denominator
  (Reading B: "couldn't determine" is neither evidence of correct
  nor incorrect linkage; reporting it as failure conflates ignorance
  with error)
- (empty) → row not yet audited; excluded from BOTH with a warning

Run from ws2 root (after hand-audit complete):
    uv run python experiments/phase-0.2/orcid_linkage_aggregate.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

_OUT_DIR = Path(__file__).parent
_AUDIT_CSV = _OUT_DIR / "orcid-linkage-audit-input.csv"

_THRESHOLD_OVERALL = 0.70
_THRESHOLD_PER_REGION = 0.50

_CORRECT_VALUES = {"yes", "likely"}
_INCORRECT_VALUES = {"no"}
_UNCLEAR_VALUES = {"unclear"}


def _classify(linkage_value: str) -> str | None:
    """Map user input to one of: 'correct', 'incorrect', 'unclear', None."""
    if not isinstance(linkage_value, str):
        return None
    val = linkage_value.lower().strip()
    if not val:
        return None
    if val in _CORRECT_VALUES:
        return "correct"
    if val in _INCORRECT_VALUES:
        return "incorrect"
    if val in _UNCLEAR_VALUES:
        return "unclear"
    # Unknown value — flag
    return f"unknown:{val}"


def _aggregate_rate(
    df: pd.DataFrame, group_col: str | None = None,
) -> pd.DataFrame:
    """Compute correctness rate, optionally per-group.

    Reading B (locked): unclear is EXCLUDED from both numerator AND
    denominator, on the grounds that "couldn't determine" is neither
    evidence of correct nor incorrect linkage.

    Numerator: count of `correct` rows (yes + likely).
    Denominator: count of correct + incorrect rows (yes + likely + no).
    Excluded: unclear, unaudited (empty), unknown values.
    """
    rows: list[dict[str, Any]] = []
    if group_col is None:
        groups = [(None, df)]
    else:
        groups = list(df.groupby(group_col))

    for key, sub in groups:
        n_correct = (sub["_classification"] == "correct").sum()
        n_incorrect = (sub["_classification"] == "incorrect").sum()
        n_unclear = (sub["_classification"] == "unclear").sum()
        n_decisive = n_correct + n_incorrect  # yes/likely/no only
        n_audited = n_decisive + n_unclear  # all-flag denominator (Reading A reference)
        n_unaudited = sub["_classification"].isna().sum()
        n_unknown = (
            sub["_classification"]
            .astype(str).str.startswith("unknown:")
        ).sum()

        # Reading B (locked): rate over decisive only
        rate = float(n_correct / n_decisive) if n_decisive > 0 else 0.0
        rows.append({
            "group": str(key) if key is not None else "_overall",
            "n_total": int(len(sub)),
            "n_correct": int(n_correct),
            "n_incorrect": int(n_incorrect),
            "n_unclear": int(n_unclear),
            "n_decisive": int(n_decisive),
            "n_audited": int(n_audited),
            "n_unaudited": int(n_unaudited),
            "n_unknown": int(n_unknown),
            "rate": rate,
        })
    return pd.DataFrame(rows)


def main() -> None:
    print("Phase 0.2 Wave 3A — ORCID-linkage aggregation")
    print()

    if not _AUDIT_CSV.exists():
        print(f"ERROR: {_AUDIT_CSV} not found.")
        print("Run experiments/phase-0.2/orcid_linkage_prep.py first.")
        sys.exit(2)

    df = pd.read_csv(_AUDIT_CSV)
    print(f"Loaded {len(df)} rows from {_AUDIT_CSV.name}")

    # Classify each row
    df["_classification"] = df["linkage_correct"].apply(_classify)

    n_unaudited = df["_classification"].isna().sum()
    n_unknown = (
        df["_classification"].astype(str).str.startswith("unknown:")
    ).sum()
    print(f"  unaudited rows: {n_unaudited}")
    print(f"  unknown-value rows: {n_unknown}")

    if n_unaudited > 0:
        print()
        print(f"WARNING: {n_unaudited} rows have empty linkage_correct.")
        print("Audit incomplete; report below excludes these rows.")
        print("Re-run after completing the hand-audit for full results.")

    if n_unknown > 0:
        print()
        print(f"WARNING: {n_unknown} rows have unrecognized linkage_correct values.")
        print("Expected values: 'yes', 'likely', 'unclear', 'no' (or empty).")
        print("Sample unknown values:")
        unknown_mask = df["_classification"].astype(str).str.startswith("unknown:")
        for v in df.loc[unknown_mask, "linkage_correct"].head(5):
            print(f"  {v!r}")

    print()

    # Overall rate
    overall = _aggregate_rate(df)
    overall_row = overall.iloc[0]
    overall_rate = float(overall_row["rate"])
    overall_pass = overall_rate >= _THRESHOLD_OVERALL
    overall_status = "✅ PASS" if overall_pass else "❌ FAIL"
    print("=== Overall (Reading B: unclear excluded from denominator) ===")
    print(
        f"  decisive: {int(overall_row['n_decisive'])} "
        f"(yes+likely+no, of {int(overall_row['n_total'])} total); "
        f"rate: {overall_rate:.1%}; "
        f"threshold: {_THRESHOLD_OVERALL:.0%}; "
        f"{overall_status}"
    )
    print(
        f"  yes/likely: {int(overall_row['n_correct'])}, "
        f"no: {int(overall_row['n_incorrect'])}, "
        f"unclear: {int(overall_row['n_unclear'])} (excluded)"
    )
    print()

    # Per-region rate
    per_region = _aggregate_rate(df, group_col="region_heuristic")
    per_region["status"] = per_region["rate"].apply(
        lambda r: "PASS" if r >= _THRESHOLD_PER_REGION else "FAIL"
    )
    print("=== Per-region (Reading B; unclear excluded) ===")
    print(
        f"{'region':<13} {'n_total':>8} {'decisive':>10} "
        f"{'rate':>8} {'status':>8}"
    )
    print("-" * 50)
    for _, row in per_region.sort_values("rate").iterrows():
        rate_str = f"{row['rate']:.1%}"
        decisive_str = f"{int(row['n_decisive'])}"
        if int(row['n_decisive']) == 0:
            rate_str = "n/a"
            decisive_str = "0"
        print(
            f"{row['group']:<13} {int(row['n_total']):>8} "
            f"{decisive_str:>10} {rate_str:>8} {row['status']:>8}"
        )
    print()

    # Exclusion list for §9a P5
    excluded_regions = per_region[
        per_region["rate"] < _THRESHOLD_PER_REGION
    ]["group"].tolist()
    print(f"Regions excluded from §9a P5 ground-truth: {excluded_regions or 'none'}")
    print()

    # Methodology revision check
    if not overall_pass:
        print("⚠ §4 ORCID-linkage validation FAILED at overall threshold.")
        print("Per `phase-0.2-plan.md` §4 + Phase 0.1 retro:")
        print("  - §9a P5 methodology re-opens for revision.")
        print("  - User judgment moment: trigger plan-revision branch.")
    elif excluded_regions:
        print(
            f"⚠ Per-region threshold failed for: {excluded_regions}. "
            f"§9a P5 ground-truth restricted to validated regions; "
            f"bias-uncertainty band's ORCID-quantified lower bound becomes "
            f"per-region for excluded cells."
        )
    else:
        print("✅ All §4 ORCID-linkage thresholds met.")

    # Write artifact md
    snapshot = datetime.now(timezone.utc).isoformat(timespec="seconds")
    md_lines = [
        "# Phase 0.2 Wave 3A — ORCID-linkage aggregation",
        "",
        f"**Run date:** {datetime.now(timezone.utc).date().isoformat()}",
        f"**Snapshot:** {snapshot}",
        "**Audit input:** `experiments/phase-0.2/orcid-linkage-audit-input.csv`",
        f"**N rows:** {len(df)} (decisive: "
        f"{int(overall_row['n_decisive'])}; "
        f"unclear: {int(overall_row['n_unclear'])}; "
        f"unaudited: {n_unaudited}; unknown: {n_unknown})",
        "",
        "**Methodology (Reading B):** unclear EXCLUDED from numerator and "
        "denominator. Rate = (yes+likely) / (yes+likely+no).",
        "",
        "## Overall linkage-correctness rate",
        "",
        f"- **{overall_rate:.1%}** ({int(overall_row['n_correct'])} yes/likely / "
        f"{int(overall_row['n_decisive'])} decisive)",
        f"- §4 threshold: ≥{_THRESHOLD_OVERALL:.0%}",
        f"- **Result: {overall_status}**",
        "",
        "## Per-region rate",
        "",
        "| Region | N total | N decisive | Rate | Status |",
        "|---|---:|---:|---:|---|",
    ]
    for _, row in per_region.sort_values("rate", ascending=False).iterrows():
        rate_str = f"{row['rate']:.1%}" if int(row['n_decisive']) > 0 else "n/a"
        md_lines.append(
            f"| {row['group']} | {int(row['n_total'])} | "
            f"{int(row['n_decisive'])} | {rate_str} | {row['status']} |"
        )
    md_lines += [
        "",
        f"§4 per-region threshold: ≥{_THRESHOLD_PER_REGION:.0%}",
        "",
        "## §9a P5 implication",
        "",
    ]
    if not overall_pass:
        md_lines.append(
            "**§9a P5 methodology re-opens for revision** (overall threshold failed)."
        )
    elif excluded_regions:
        md_lines.append(
            f"**§9a P5 ground-truth restricted to validated regions.** "
            f"Excluded: {excluded_regions}. Bias-uncertainty band's "
            f"ORCID-quantified lower bound becomes per-region for excluded "
            f"cells."
        )
    else:
        md_lines.append(
            "**No restriction needed.** All §4 thresholds met; §9a P5 "
            "ground-truth subsample usable across all regions."
        )

    md_lines += [
        "",
        "## Decision",
        "",
        ("Wave 3A acceptance gate met. §9a P5 ground-truth subsample is "
         "usable per the per-region restrictions above.")
        if overall_pass
        else ("Wave 3A acceptance gate FAILED. Plan revision required: "
              "§9a P5 methodology re-opens; user-judgment between "
              "alternative ground-truth source vs. expanded uncertainty "
              "band."),
        "",
        "## Artifacts",
        "",
        "- `experiments/phase-0.2/orcid-linkage-aggregate.md` — this artifact",
        "- `experiments/phase-0.2/orcid-linkage-aggregate-summary.json` — machine summary",
        "- `experiments/phase-0.2/orcid-linkage-audit-input.csv` — audit input",
        "- `experiments/phase-0.2/orcid_linkage_aggregate.py` — this script",
    ]

    md_path = _OUT_DIR / "orcid-linkage-aggregate.md"
    md_path.write_text("\n".join(md_lines) + "\n")
    print(f"wrote {md_path}")

    summary = {
        "snapshot": snapshot,
        "methodology": "Reading B: unclear excluded from numerator and denominator",
        "n_total": int(len(df)),
        "n_decisive": int(overall_row["n_decisive"]),
        "n_audited_inclusive": int(overall_row["n_audited"]),
        "n_unaudited": int(n_unaudited),
        "n_unknown": int(n_unknown),
        "overall_rate": overall_rate,
        "overall_pass": overall_pass,
        "threshold_overall": _THRESHOLD_OVERALL,
        "threshold_per_region": _THRESHOLD_PER_REGION,
        "per_region": per_region.to_dict(orient="records"),
        "excluded_regions": excluded_regions,
    }
    json_path = _OUT_DIR / "orcid-linkage-aggregate-summary.json"
    json_path.write_text(json.dumps(summary, indent=2, default=str))
    print(f"wrote {json_path}")
    print()
    print("Aggregation complete.")


if __name__ == "__main__":
    main()
    sys.exit(0)
