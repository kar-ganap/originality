"""Check 1 — Abstract availability by year for CS + Physics, 1970–2024.

Samples 200 papers per (year, field) cell from OpenAlex via the anonymous REST
API; measures the fraction with a non-empty ``abstract_inverted_index`` field.
Outputs:

- ``abstract-coverage-raw.parquet`` — per-paper sampled rows
- ``abstract-coverage.csv`` — per-(year, field) coverage rates with Wilson CIs
- ``abstract-coverage.png`` — coverage curve plot
- ``abstract-coverage.md`` — summary + interpretation

Run from the ws2 root: ``uv run python experiments/phase-0.1/check1_abstract_coverage.py``.
"""

from __future__ import annotations

import math
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from tqdm import tqdm

from whitespace2 import openalex

# ---------- analysis helpers (importable; tested in tests/test_check1_coverage.py) ----------


def coverage_rate(rows: list[dict[str, Any]]) -> tuple[int, int, float]:
    """Compute (n_total, n_with_abstract, rate) over a list of row dicts.

    Each row must contain ``has_abstract`` (bool).
    """
    n_total = len(rows)
    n_with = sum(1 for row in rows if row["has_abstract"])
    rate = (n_with / n_total) if n_total > 0 else 0.0
    return n_total, n_with, rate


def wilson_ci(successes: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion.

    Returns (lower, upper) bounds for the proportion ``successes / n`` at
    confidence level ``1 - alpha``. Robust at p=0 and p=1.
    """
    if n == 0:
        return 0.0, 1.0
    # 95% two-sided z = 1.959964; use the alpha to derive z.
    # We use the inverse-normal approximation via math.erfinv equivalent.
    # For alpha=0.05 → z = sqrt(2) * inv_erf(1 - alpha) approximated.
    # To avoid pulling scipy here, hardcode the common case and approximate otherwise.
    if abs(alpha - 0.05) < 1e-9:
        z = 1.959963984540054
    elif abs(alpha - 0.01) < 1e-9:
        z = 2.5758293035489004
    elif abs(alpha - 0.10) < 1e-9:
        z = 1.6448536269514722
    else:
        # Generic: use scipy if available; fallback z=2.0.
        try:
            from scipy.stats import norm  # type: ignore[import-untyped]

            z = float(norm.ppf(1 - alpha / 2))
        except ImportError:
            z = 2.0

    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = (z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n)) / denom
    low = max(0.0, centre - half)
    high = min(1.0, centre + half)
    return low, high


# ---------- main script ----------


_FIELDS: dict[str, str] = {
    "cs": "C41008148",
    "physics": "C121332964",
}
_YEARS = list(range(1970, 2025))  # inclusive of 2024
_SAMPLE_SIZE = 200
_SEED = 42
_SELECT = ["id", "publication_year", "abstract_inverted_index"]

_OUT_DIR = Path(__file__).parent
_DATA_METADATA_DIR = _OUT_DIR.parent.parent / "data" / "metadata"


def _validate_concepts() -> dict[str, dict[str, Any]]:
    """Validate concept IDs and pull human-readable names."""
    concepts: dict[str, dict[str, Any]] = {}
    for field, concept_id in _FIELDS.items():
        concept = openalex.get_concept(concept_id)
        concepts[field] = concept
        print(f"  {field}: {concept_id} → {concept['display_name']} (level={concept['level']})")
    return concepts


def _sample_cell(field: str, concept_id: str, year: int) -> list[dict[str, Any]]:
    works = openalex.fetch_works(
        filters={"concepts.id": concept_id, "publication_year": str(year)},
        sample_size=_SAMPLE_SIZE,
        seed=_SEED,
        select=_SELECT,
    )
    return works


def _collect_samples() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    cells = [(f, c, y) for f, c in _FIELDS.items() for y in _YEARS]
    for field, concept_id, year in tqdm(cells, desc="Sampling cells"):
        try:
            works = _sample_cell(field, concept_id, year)
        except RuntimeError as err:
            print(f"  WARN: skipping {field}/{year}: {err}")
            continue
        for work in works:
            rows.append(
                {
                    "work_id": work.get("id"),
                    "year": year,
                    "field": field,
                    "has_abstract": openalex.has_abstract(work),
                }
            )
        # Polite pacing: 1 req/sec average.
        time.sleep(0.5)
    return rows


def _compute_coverage(rows: list[dict[str, Any]]) -> pd.DataFrame:
    grouped: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["year"], row["field"])].append(row)

    records: list[dict[str, Any]] = []
    for (year, field), cell_rows in sorted(grouped.items()):
        n_total, n_with, rate = coverage_rate(cell_rows)
        ci_low, ci_high = wilson_ci(n_with, n_total)
        records.append(
            {
                "year": year,
                "field": field,
                "n_sampled": n_total,
                "n_with_abstract": n_with,
                "coverage": rate,
                "ci_low": ci_low,
                "ci_high": ci_high,
            }
        )
    return pd.DataFrame(records)


def _make_plot(coverage_df: pd.DataFrame, out_path: Path) -> None:
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 5))
    for field, color in [("cs", "#1f77b4"), ("physics", "#d62728")]:
        sub = coverage_df[coverage_df["field"] == field].sort_values("year")
        ax.plot(sub["year"], sub["coverage"], label=field.upper(), color=color, linewidth=1.5)
        ax.fill_between(
            sub["year"], sub["ci_low"], sub["ci_high"], alpha=0.2, color=color
        )
    ax.axhline(0.95, color="gray", linestyle="--", linewidth=0.8, label="95% reference")
    ax.set_xlabel("Publication year")
    ax.set_ylabel("Fraction of papers with non-empty abstract")
    ax.set_title("Abstract availability by year — OpenAlex CS + Physics, sample N=200/cell")
    ax.set_ylim(-0.02, 1.02)
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _summarize(coverage_df: pd.DataFrame) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for field in ("cs", "physics"):
        sub = coverage_df[coverage_df["field"] == field].sort_values("year")
        # First year >= 95%
        ge95 = sub[sub["coverage"] >= 0.95]
        first_ge95 = int(ge95["year"].min()) if len(ge95) > 0 else None
        # Last year < 50% (sharp drop indicator)
        lt50 = sub[sub["coverage"] < 0.50]
        last_lt50 = int(lt50["year"].max()) if len(lt50) > 0 else None
        # Pre-1990 mean coverage
        pre1990 = sub[sub["year"] < 1990]["coverage"].mean()
        post1990 = sub[sub["year"] >= 1990]["coverage"].mean()
        summary[field] = {
            "first_year_ge95": first_ge95,
            "last_year_lt50": last_lt50,
            "mean_pre1990": float(pre1990) if not pd.isna(pre1990) else None,
            "mean_post1990": float(post1990) if not pd.isna(post1990) else None,
        }
    return summary


def _write_field_definitions(concepts: dict[str, dict[str, Any]], snapshot_date: str) -> None:
    rows = []
    for field, concept_id in _FIELDS.items():
        concept = concepts[field]
        rows.append(
            {
                "field": field,
                "concept_id": concept_id,
                "concept_name": concept["display_name"],
                "parent_path": "(top-level)" if concept.get("level") == 0 else "(see openalex)",
                "snapshot_recorded": snapshot_date,
                "year_min": min(_YEARS),
                "year_max": max(_YEARS),
                "notes": "Phase 0.1 Check 1",
            }
        )
    df = pd.DataFrame(rows)
    out_path = _DATA_METADATA_DIR / "field_definitions.csv"
    df.to_csv(out_path, index=False)
    print(f"  wrote {out_path}")


def _fmt_pct(value: float | None) -> str:
    return f"{value:.1%}" if value is not None else "n/a"


def _write_summary_md(
    coverage_df: pd.DataFrame,
    summary: dict[str, Any],
    snapshot_date: str,
    n_calls: int,
) -> None:
    total_papers = int(coverage_df["n_sampled"].sum())
    pre_cs = _fmt_pct(summary["cs"]["mean_pre1990"])
    post_cs = _fmt_pct(summary["cs"]["mean_post1990"])
    pre_ph = _fmt_pct(summary["physics"]["mean_pre1990"])
    post_ph = _fmt_pct(summary["physics"]["mean_post1990"])
    body = f"""# Check 1 — Abstract availability by year

**Run date:** {datetime.now(timezone.utc).date().isoformat()}
**Snapshot recorded:** {snapshot_date} (request-time; OpenAlex REST does not expose snapshot pinning — see desiderata §1)
**Sample design:** {_SAMPLE_SIZE} papers per (year × field) cell, OpenAlex `?sample` with seed={_SEED}
**Years:** {min(_YEARS)}–{max(_YEARS)}
**Fields:** CS (`{_FIELDS['cs']}`), Physics (`{_FIELDS['physics']}`)
**Total papers sampled:** {total_papers}
**Total API calls (concepts + works):** {n_calls}

## Headline numbers

- **CS:** first year with coverage ≥95% = {summary['cs']['first_year_ge95']}; last year with coverage <50% = {summary['cs']['last_year_lt50']}
  - Mean pre-1990 coverage: {pre_cs}
  - Mean post-1990 coverage: {post_cs}
- **Physics:** first year with coverage ≥95% = {summary['physics']['first_year_ge95']}; last year with coverage <50% = {summary['physics']['last_year_lt50']}
  - Mean pre-1990 coverage: {pre_ph}
  - Mean post-1990 coverage: {post_ph}

## Implications for Phase 0.1

- **§13 pre-1990 retention:** assumption holds if pre-1990 coverage exceeds the operational
  workability threshold (>30% per the plan's escalation rule). Specific concern cells flagged
  in the CSV where coverage <30%.
- **Drift-mitigation ladder (§2):** ladder unchanged at this stage; Check 5c (drift-pilot)
  remains the load-bearing diagnostic for Flavor A commitment.

## Plot

![coverage by year](abstract-coverage.png)

## Detailed table

See `abstract-coverage.csv` for the full year × field × {{n_sampled, n_with_abstract,
coverage, ci_low, ci_high}} table.
"""
    out_path = _OUT_DIR / "abstract-coverage.md"
    out_path.write_text(body)
    print(f"  wrote {out_path}")


def main() -> None:
    print("Check 1 — Abstract availability by year")
    print(f"  out_dir: {_OUT_DIR}")
    print()
    print("Validating concept IDs...")
    snapshot_date = openalex.latest_snapshot_date()
    concepts = _validate_concepts()
    print()
    print(f"Sampling {len(_FIELDS)} fields × {len(_YEARS)} years = {len(_FIELDS) * len(_YEARS)} cells...")
    rows = _collect_samples()
    print(f"  collected {len(rows)} paper records")
    print()
    print("Computing coverage rates + Wilson CIs...")
    coverage_df = _compute_coverage(rows)
    raw_df = pd.DataFrame(rows)
    raw_path = _OUT_DIR / "abstract-coverage-raw.parquet"
    raw_df.to_parquet(raw_path, index=False)
    print(f"  wrote {raw_path}")
    csv_path = _OUT_DIR / "abstract-coverage.csv"
    coverage_df.to_csv(csv_path, index=False)
    print(f"  wrote {csv_path}")
    plot_path = _OUT_DIR / "abstract-coverage.png"
    _make_plot(coverage_df, plot_path)
    print(f"  wrote {plot_path}")
    summary = _summarize(coverage_df)
    n_calls = len(_FIELDS) + len(_FIELDS) * len(_YEARS)  # concept lookups + sample calls
    _write_summary_md(coverage_df, summary, snapshot_date, n_calls)
    _write_field_definitions(concepts, snapshot_date)
    print()
    print("Check 1 complete.")


if __name__ == "__main__":
    main()
