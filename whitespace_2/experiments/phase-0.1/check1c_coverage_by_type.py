"""Check 1c — Abstract coverage disaggregated by paper type.

Extension of Check 1, surfaced by the finding that overall coverage is far
below the plan's pre-run expectation (~50-70% rather than ~95%). Question:
is the bottleneck uniform across paper types, or concentrated in specific
types (e.g., proceedings, book-chapters) that ws2 could scope out to recover
near-full coverage on the remainder?

Re-runs the same 110-cell sample (same seed) with ``type`` added to the field
projection. Aggregates coverage by (type, field).

Outputs:

- ``abstract-coverage-by-type-raw.parquet`` — per-paper rows with type
- ``abstract-coverage-by-type.csv`` — per-(type, field) coverage rates
- ``abstract-coverage-by-type.png`` — bar chart, types ranked by coverage
- ``abstract-coverage-by-type.md`` — summary + interpretation

Run from ws2 root: ``uv run python experiments/phase-0.1/check1c_coverage_by_type.py``.
"""

from __future__ import annotations

import importlib.util
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from tqdm import tqdm

from whitespace2 import openalex

_OUT_DIR = Path(__file__).parent
_FIELDS: dict[str, str] = {
    "cs": "C41008148",
    "physics": "C121332964",
}
_YEARS = list(range(1970, 2025))
_SAMPLE_SIZE = 200
_SEED = 42
_SELECT = ["id", "publication_year", "abstract_inverted_index", "type"]


def _import_check1_helpers() -> Any:
    spec = importlib.util.spec_from_file_location(
        "check1", _OUT_DIR / "check1_abstract_coverage.py"
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load check1 module")
    module = importlib.util.module_from_spec(spec)
    sys.modules["check1"] = module
    spec.loader.exec_module(module)
    return module


def _collect_samples_with_type() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    cells = [(f, c, y) for f, c in _FIELDS.items() for y in _YEARS]
    for field, concept_id, year in tqdm(cells, desc="Sampling cells (with type)"):
        try:
            works = openalex.fetch_works(
                filters={"concepts.id": concept_id, "publication_year": str(year)},
                sample_size=_SAMPLE_SIZE,
                seed=_SEED,
                select=_SELECT,
            )
        except RuntimeError as err:
            print(f"  WARN: skipping {field}/{year}: {err}")
            continue
        for work in works:
            rows.append(
                {
                    "work_id": work.get("id"),
                    "year": year,
                    "field": field,
                    "type": work.get("type") or "unknown",
                    "has_abstract": openalex.has_abstract(work),
                }
            )
        time.sleep(0.5)
    return rows


def _coverage_by_type(
    rows: list[dict[str, Any]],
    helpers: Any,
    min_n: int = 50,
) -> pd.DataFrame:
    """Coverage per (type, field) cell. Drops cells with fewer than min_n papers."""
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["type"], row["field"])].append(row)
    records: list[dict[str, Any]] = []
    for (paper_type, field), cell_rows in grouped.items():
        n_total, n_with, rate = helpers.coverage_rate(cell_rows)
        if n_total < min_n:
            continue
        ci_low, ci_high = helpers.wilson_ci(n_with, n_total)
        records.append(
            {
                "type": paper_type,
                "field": field,
                "n_sampled": n_total,
                "n_with_abstract": n_with,
                "coverage": rate,
                "ci_low": ci_low,
                "ci_high": ci_high,
            }
        )
    return pd.DataFrame(records).sort_values(["field", "coverage"], ascending=[True, False])


def _make_plot(coverage_df: pd.DataFrame, out_path: Path) -> None:
    import matplotlib.pyplot as plt

    types_order = (
        coverage_df.groupby("type")["coverage"].mean().sort_values(ascending=True).index.tolist()
    )
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    for ax, field in zip(axes, ["cs", "physics"], strict=False):
        sub = coverage_df[coverage_df["field"] == field].set_index("type").reindex(types_order).dropna()
        positions = range(len(sub))
        ax.barh(positions, sub["coverage"], color="#4c72b0", alpha=0.8)
        for pos, (_idx, row) in zip(positions, sub.iterrows(), strict=False):
            ax.errorbar(
                row["coverage"],
                pos,
                xerr=[[row["coverage"] - row["ci_low"]], [row["ci_high"] - row["coverage"]]],
                fmt="none",
                ecolor="black",
                capsize=3,
            )
            ax.text(
                row["coverage"] + 0.01,
                pos,
                f" n={int(row['n_sampled'])}",
                va="center",
                fontsize=8,
                color="dimgray",
            )
        ax.set_yticks(list(positions))
        ax.set_yticklabels(sub.index)
        ax.set_xlim(0, 1.05)
        ax.axvline(0.95, color="gray", linestyle="--", linewidth=0.8)
        ax.set_xlabel("Coverage (95% Wilson CI)")
        ax.set_title(f"{field.upper()}")
        ax.grid(True, axis="x", alpha=0.3)
    fig.suptitle("Abstract coverage by paper type — OpenAlex CS+Physics, 1970-2024 sample")
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _write_summary_md(coverage_df: pd.DataFrame, snapshot_date: str, total_papers: int) -> None:
    high_coverage = coverage_df[coverage_df["coverage"] >= 0.85].copy()
    low_coverage = coverage_df[coverage_df["coverage"] < 0.50].copy()
    pivot = coverage_df.pivot(index="type", columns="field", values="coverage").round(3)
    n_pivot = coverage_df.pivot(index="type", columns="field", values="n_sampled").fillna(0).astype(int)

    body_lines = [
        "# Check 1c — Abstract coverage by paper type",
        "",
        f"**Run date:** {datetime.now(timezone.utc).date().isoformat()}",
        f"**Snapshot recorded:** {snapshot_date}",
        f"**Sample design:** same as Check 1 (200 papers per year × field cell, seed=42), "
        "with `type` added to OpenAlex select projection.",
        f"**Total papers:** {total_papers}",
        "",
        "## Question",
        "",
        "Check 1 found overall abstract coverage at ~50-70% rather than the planned ~95%.",
        "Is the bottleneck uniform across paper types, or concentrated in specific types",
        "(proceedings, book-chapters, etc.) that ws2 could scope out to recover near-full",
        "coverage on the remainder?",
        "",
        "## Coverage by type",
        "",
        "Cells with fewer than 50 papers across the 1970-2024 sample are dropped (sample-size",
        "stability). Coverage = mean(has_abstract) within each (type, field) cell.",
        "",
        "| Type | CS coverage | CS n | Physics coverage | Physics n |",
        "|------|------------:|-----:|-----------------:|----------:|",
    ]
    for paper_type in pivot.index:
        cs_cov = pivot.loc[paper_type, "cs"] if "cs" in pivot.columns else None
        phys_cov = pivot.loc[paper_type, "physics"] if "physics" in pivot.columns else None
        cs_n = n_pivot.loc[paper_type, "cs"] if "cs" in n_pivot.columns else 0
        phys_n = n_pivot.loc[paper_type, "physics"] if "physics" in n_pivot.columns else 0
        cs_str = f"{cs_cov:.1%}" if pd.notna(cs_cov) else "—"
        phys_str = f"{phys_cov:.1%}" if pd.notna(phys_cov) else "—"
        body_lines.append(f"| {paper_type} | {cs_str} | {cs_n} | {phys_str} | {phys_n} |")

    body_lines.extend(
        [
            "",
            "## High-coverage types (≥85%)",
            "",
        ]
    )
    if len(high_coverage) > 0:
        for _, row in high_coverage.iterrows():
            body_lines.append(
                f"- **{row['type']} / {row['field']}**: "
                f"{row['coverage']:.1%} (n={int(row['n_sampled'])})"
            )
    else:
        body_lines.append("*(none)*")

    body_lines.extend(
        [
            "",
            "## Low-coverage types (<50%)",
            "",
        ]
    )
    if len(low_coverage) > 0:
        for _, row in low_coverage.iterrows():
            body_lines.append(
                f"- **{row['type']} / {row['field']}**: "
                f"{row['coverage']:.1%} (n={int(row['n_sampled'])})"
            )
    else:
        body_lines.append("*(none)*")

    body_lines.extend(
        [
            "",
            "## Plot",
            "",
            "![coverage by type](abstract-coverage-by-type.png)",
            "",
            "## Interpretation (to be filled after inspection)",
            "",
            "*(See commit message and follow-up plan.md status note.)*",
            "",
        ]
    )
    out_path = _OUT_DIR / "abstract-coverage-by-type.md"
    out_path.write_text("\n".join(body_lines))
    print(f"  wrote {out_path}")


def main() -> None:
    print("Check 1c — Abstract coverage by paper type")
    helpers = _import_check1_helpers()
    snapshot_date = openalex.latest_snapshot_date()
    print(f"Sampling {len(_FIELDS) * len(_YEARS)} cells with type included...")
    rows = _collect_samples_with_type()
    print(f"  collected {len(rows)} paper records")
    raw_path = _OUT_DIR / "abstract-coverage-by-type-raw.parquet"
    pd.DataFrame(rows).to_parquet(raw_path, index=False)
    print(f"  wrote {raw_path}")
    coverage_df = _coverage_by_type(rows, helpers)
    csv_path = _OUT_DIR / "abstract-coverage-by-type.csv"
    coverage_df.to_csv(csv_path, index=False)
    print(f"  wrote {csv_path}")
    plot_path = _OUT_DIR / "abstract-coverage-by-type.png"
    _make_plot(coverage_df, plot_path)
    print(f"  wrote {plot_path}")
    _write_summary_md(coverage_df, snapshot_date, len(rows))
    print()
    print("Check 1c complete.")


if __name__ == "__main__":
    main()
