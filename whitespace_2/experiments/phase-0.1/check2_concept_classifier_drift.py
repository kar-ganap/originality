"""Check 2 (a/b/c) — concept classifier drift audit.

Three sub-checks on the same 22K-paper sample:

- **2a — Concept coverage by year:** fraction of papers with ≥1 concept tag.
  Red flag: monotonically increasing from low base (systematic under-tagging
  of older papers).
- **2b — Concepts per paper by year:** mean and median, controlling for
  abstract presence. Red flag: systematic temporal trend.
- **2c — Confidence score distribution by year:** mean tag confidence. Red
  flag: systematically lower on older papers.

Outputs to ``experiments/phase-0.1/``:

- ``classifier-drift-raw.parquet``
- ``classifier-drift.csv``
- ``classifier-drift.png`` (3-panel)
- ``classifier-drift.md``
"""

from __future__ import annotations

import importlib.util
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
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
_SELECT = ["id", "publication_year", "abstract_inverted_index", "concepts"]


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


def _summarize_concepts(work: dict[str, Any]) -> dict[str, Any]:
    """Per-paper concept stats."""
    concepts = work.get("concepts") or []
    if not isinstance(concepts, list):
        concepts = []
    n_total = len(concepts)
    scores = [c.get("score") or 0.0 for c in concepts if isinstance(c, dict)]
    return {
        "n_concepts": n_total,
        "n_concepts_l0": sum(1 for c in concepts if isinstance(c, dict) and c.get("level") == 0),
        "n_concepts_l1": sum(1 for c in concepts if isinstance(c, dict) and c.get("level") == 1),
        "max_score": max(scores) if scores else 0.0,
        "mean_score": (sum(scores) / len(scores)) if scores else 0.0,
        "has_concept": n_total > 0,
    }


def _collect_with_concepts() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    cells = [(f, c, y) for f, c in _FIELDS.items() for y in _YEARS]
    for field, concept_id, year in tqdm(cells, desc="OpenAlex re-sample (with concepts)"):
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
            stats = _summarize_concepts(work)
            rows.append(
                {
                    "work_id": work.get("id"),
                    "year": year,
                    "field": field,
                    "has_abstract": openalex.has_abstract(work),
                    **stats,
                }
            )
        time.sleep(0.5)
    return rows


def _per_year_aggregate(df: pd.DataFrame) -> pd.DataFrame:
    grouped: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    for _, row in df.iterrows():
        grouped[(row["year"], row["field"])].append(dict(row))
    records = []
    for (year, field), cell_rows in sorted(grouped.items()):
        n_total = len(cell_rows)
        n_with_concept = sum(1 for r in cell_rows if r["has_concept"])
        ns_concepts = [r["n_concepts"] for r in cell_rows]
        ns_l1 = [r["n_concepts_l1"] for r in cell_rows]
        max_scores = [r["max_score"] for r in cell_rows if r["has_concept"]]
        mean_scores = [r["mean_score"] for r in cell_rows if r["has_concept"]]
        records.append(
            {
                "year": year,
                "field": field,
                "n_sampled": n_total,
                "concept_coverage": n_with_concept / n_total if n_total else 0.0,
                "mean_concepts_per_paper": float(np.mean(ns_concepts)) if ns_concepts else 0.0,
                "median_concepts_per_paper": float(np.median(ns_concepts)) if ns_concepts else 0.0,
                "mean_concepts_l1_per_paper": float(np.mean(ns_l1)) if ns_l1 else 0.0,
                "mean_max_score": float(np.mean(max_scores)) if max_scores else 0.0,
                "mean_mean_score": float(np.mean(mean_scores)) if mean_scores else 0.0,
            }
        )
    return pd.DataFrame(records)


def _make_plot(coverage_df: pd.DataFrame, out_path: Path) -> None:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(3, 2, figsize=(13, 11), sharex=True)
    field_colors = {"cs": "#1f77b4", "physics": "#d62728"}
    for col_idx, field in enumerate(["cs", "physics"]):
        sub = coverage_df[coverage_df["field"] == field].sort_values("year")
        color = field_colors[field]

        # Row 0 — coverage
        ax = axes[0, col_idx]
        ax.plot(sub["year"], sub["concept_coverage"], color=color, linewidth=1.6)
        ax.set_ylim(0, 1.05)
        ax.axhline(0.95, color="gray", linestyle="--", linewidth=0.8)
        ax.set_title(f"{field.upper()} — concept coverage")
        ax.grid(True, alpha=0.3)
        if col_idx == 0:
            ax.set_ylabel("Fraction with ≥1 concept")

        # Row 1 — mean concepts per paper
        ax = axes[1, col_idx]
        ax.plot(sub["year"], sub["mean_concepts_per_paper"], color=color, label="all levels",
                linewidth=1.5)
        ax.plot(sub["year"], sub["mean_concepts_l1_per_paper"], color=color, linewidth=1.0,
                linestyle="--", alpha=0.7, label="level=1 only")
        ax.set_title(f"{field.upper()} — concepts per paper")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        if col_idx == 0:
            ax.set_ylabel("Mean concept count")

        # Row 2 — mean confidence
        ax = axes[2, col_idx]
        ax.plot(sub["year"], sub["mean_max_score"], color=color, label="max score",
                linewidth=1.5)
        ax.plot(sub["year"], sub["mean_mean_score"], color=color, linewidth=1.0,
                linestyle="--", alpha=0.7, label="mean score")
        ax.set_title(f"{field.upper()} — confidence score")
        ax.set_ylim(0, 1.05)
        ax.set_xlabel("Publication year")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        if col_idx == 0:
            ax.set_ylabel("Tag confidence")

    fig.suptitle("Check 2 — Concept classifier drift (2a, 2b, 2c)", fontsize=13)
    fig.tight_layout()
    fig.savefig(out_path, dpi=110)
    plt.close(fig)


def _summarize(coverage_df: pd.DataFrame) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for field in ("cs", "physics"):
        sub = coverage_df[coverage_df["field"] == field].sort_values("year")
        pre1990 = sub[sub["year"] < 1990]
        post1990 = sub[sub["year"] >= 1990]
        summary[field] = {
            "coverage_pre1990_mean": float(pre1990["concept_coverage"].mean())
            if len(pre1990)
            else None,
            "coverage_post1990_mean": float(post1990["concept_coverage"].mean())
            if len(post1990)
            else None,
            "concepts_per_paper_pre1990": float(pre1990["mean_concepts_per_paper"].mean())
            if len(pre1990)
            else None,
            "concepts_per_paper_post1990": float(post1990["mean_concepts_per_paper"].mean())
            if len(post1990)
            else None,
            "max_score_pre1990": float(pre1990["mean_max_score"].mean())
            if len(pre1990)
            else None,
            "max_score_post1990": float(post1990["mean_max_score"].mean())
            if len(post1990)
            else None,
            "mean_score_pre1990": float(pre1990["mean_mean_score"].mean())
            if len(pre1990)
            else None,
            "mean_score_post1990": float(post1990["mean_mean_score"].mean())
            if len(post1990)
            else None,
        }
    return summary


def _fmt_pct(v: float | None) -> str:
    return f"{v:.1%}" if v is not None else "n/a"


def _fmt_num(v: float | None, n_decimals: int = 2) -> str:
    return f"{v:.{n_decimals}f}" if v is not None else "n/a"


def _write_summary_md(
    summary: dict[str, Any], snapshot_date: str, total_papers: int
) -> None:
    body = f"""# Check 2 — Concept classifier drift (2a, 2b, 2c)

**Run date:** {datetime.now(timezone.utc).date().isoformat()}
**Snapshot recorded:** {snapshot_date}
**Sample design:** same as Check 1 (200 papers per year × field cell, seed=42),
with `concepts` added to OpenAlex select.
**Total papers:** {total_papers}

## 2a — Concept coverage by year (fraction with ≥1 concept tag)

| Field | Pre-1990 | Post-1990 | Delta |
|-------|---------:|----------:|------:|
| CS | {_fmt_pct(summary['cs']['coverage_pre1990_mean'])} | {_fmt_pct(summary['cs']['coverage_post1990_mean'])} | {_fmt_pct((summary['cs']['coverage_post1990_mean'] or 0) - (summary['cs']['coverage_pre1990_mean'] or 0))} |
| Physics | {_fmt_pct(summary['physics']['coverage_pre1990_mean'])} | {_fmt_pct(summary['physics']['coverage_post1990_mean'])} | {_fmt_pct((summary['physics']['coverage_post1990_mean'] or 0) - (summary['physics']['coverage_pre1990_mean'] or 0))} |

**Red flag if:** monotonically increasing from low base (systematic under-tagging of older papers).

## 2b — Concepts per paper by year

| Field | Pre-1990 (mean) | Post-1990 (mean) | Ratio |
|-------|----------------:|-----------------:|------:|
| CS | {_fmt_num(summary['cs']['concepts_per_paper_pre1990'])} | {_fmt_num(summary['cs']['concepts_per_paper_post1990'])} | {_fmt_num((summary['cs']['concepts_per_paper_post1990'] or 1) / max(summary['cs']['concepts_per_paper_pre1990'] or 1, 0.01))} |
| Physics | {_fmt_num(summary['physics']['concepts_per_paper_pre1990'])} | {_fmt_num(summary['physics']['concepts_per_paper_post1990'])} | {_fmt_num((summary['physics']['concepts_per_paper_post1990'] or 1) / max(summary['physics']['concepts_per_paper_pre1990'] or 1, 0.01))} |

**Red flag if:** systematic temporal trend in concepts-per-paper (especially declining toward older years).

## 2c — Confidence score distribution by year

| Field | Pre-1990 max-score | Post-1990 max-score | Pre-1990 mean-score | Post-1990 mean-score |
|-------|--------------------:|--------------------:|--------------------:|---------------------:|
| CS | {_fmt_num(summary['cs']['max_score_pre1990'])} | {_fmt_num(summary['cs']['max_score_post1990'])} | {_fmt_num(summary['cs']['mean_score_pre1990'])} | {_fmt_num(summary['cs']['mean_score_post1990'])} |
| Physics | {_fmt_num(summary['physics']['max_score_pre1990'])} | {_fmt_num(summary['physics']['max_score_post1990'])} | {_fmt_num(summary['physics']['mean_score_pre1990'])} | {_fmt_num(summary['physics']['mean_score_post1990'])} |

**Red flag if:** systematically lower on older papers.

## Plot

![3-panel concept-classifier-drift diagnostic](classifier-drift.png)

## Interpretation

*(Filled after inspection.)*
"""
    out_path = _OUT_DIR / "classifier-drift.md"
    out_path.write_text(body)
    print(f"  wrote {out_path}")


def main() -> None:
    print("Check 2 — Concept classifier drift (2a, 2b, 2c)")
    snapshot_date = openalex.latest_snapshot_date()

    print("\nStep 1: OpenAlex re-sample with concepts")
    rows = _collect_with_concepts()
    print(f"  collected {len(rows)} paper records")
    df = pd.DataFrame(rows)
    raw_path = _OUT_DIR / "classifier-drift-raw.parquet"
    df.to_parquet(raw_path, index=False)
    print(f"  wrote {raw_path}")

    print("\nStep 2: per-year aggregation")
    coverage_df = _per_year_aggregate(df)
    csv_path = _OUT_DIR / "classifier-drift.csv"
    coverage_df.to_csv(csv_path, index=False)
    print(f"  wrote {csv_path}")

    plot_path = _OUT_DIR / "classifier-drift.png"
    _make_plot(coverage_df, plot_path)
    print(f"  wrote {plot_path}")

    summary = _summarize(coverage_df)
    _write_summary_md(summary, snapshot_date, len(rows))

    print("\nHeadline (2a coverage / 2b concepts-per-paper / 2c mean-max-score):")
    for field in ("cs", "physics"):
        s = summary[field]
        print(
            f"  {field}: cov pre1990={_fmt_pct(s['coverage_pre1990_mean'])}, "
            f"post1990={_fmt_pct(s['coverage_post1990_mean'])}; "
            f"concepts/paper {_fmt_num(s['concepts_per_paper_pre1990'])} → "
            f"{_fmt_num(s['concepts_per_paper_post1990'])}; "
            f"max-score {_fmt_num(s['max_score_pre1990'])} → "
            f"{_fmt_num(s['max_score_post1990'])}"
        )
    print("\nCheck 2 (2a/2b/2c) complete.")


if __name__ == "__main__":
    main()
