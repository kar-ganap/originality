"""Check 1e — S2AG abstract coverage on the same 22K-paper sample.

Path-(C) feasibility check. Re-samples OpenAlex (same seed=42, 110 cells)
with DOI extraction, then batch-looks-up each DOI in Semantic Scholar's
``/paper/batch`` endpoint. Compares OpenAlex vs. S2AG abstract coverage by
year × field, with the most decision-relevant number being **S2AG fill
rate on the OpenAlex no-abstract subset** post-1990.

Decision rule (pre-registered):

- S2AG fill rate ≥80% on OpenAlex no-abstract papers post-1990: **path
  (C) decisively wins**; proceed to wholesale Phase 0.1 plan revision.
- S2AG fill rate 50-80%: path (C) helps but doesn't fully solve.
- S2AG fill rate <50%: path (C) is not the answer.

Outputs to ``experiments/phase-0.1/``:

- ``s2ag-coverage-raw.parquet``
- ``s2ag-coverage.csv``
- ``s2ag-coverage.png``
- ``s2ag-coverage.md``
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

from whitespace2 import openalex, s2ag

_OUT_DIR = Path(__file__).parent
_FIELDS: dict[str, str] = {
    "cs": "C41008148",
    "physics": "C121332964",
}
_YEARS = list(range(1970, 2025))
_SAMPLE_SIZE = 200
_SEED = 42
_OPENALEX_SELECT = ["id", "publication_year", "abstract_inverted_index", "ids"]
_S2AG_FIELDS = ["paperId", "abstract", "externalIds", "year"]


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


def _extract_doi(work: dict[str, Any]) -> str | None:
    """Pull bare DOI string (no URL prefix) from an OpenAlex work record."""
    ids = work.get("ids") or {}
    if not isinstance(ids, dict):
        return None
    doi = ids.get("doi")
    if not isinstance(doi, str):
        return None
    # OpenAlex DOIs come as 'https://doi.org/10.x/y'; strip URL prefix.
    if doi.startswith("https://doi.org/"):
        return doi[len("https://doi.org/") :]
    if doi.startswith("http://doi.org/"):
        return doi[len("http://doi.org/") :]
    return doi


def _collect_openalex_with_doi() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    cells = [(f, c, y) for f, c in _FIELDS.items() for y in _YEARS]
    for field, concept_id, year in tqdm(cells, desc="OpenAlex re-sample (with DOI)"):
        try:
            works = openalex.fetch_works(
                filters={"concepts.id": concept_id, "publication_year": str(year)},
                sample_size=_SAMPLE_SIZE,
                seed=_SEED,
                select=_OPENALEX_SELECT,
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
                    "doi": _extract_doi(work),
                    "has_abstract_openalex": openalex.has_abstract(work),
                }
            )
        time.sleep(0.5)
    return rows


def _enrich_with_s2ag(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Add has_abstract_s2ag and s2ag_paper_id to each row.

    Only papers with a DOI get an S2AG lookup attempt. DOI-less rows get
    has_abstract_s2ag=False, s2ag_paper_id=None.
    """
    by_doi: dict[str, list[int]] = defaultdict(list)
    for idx, row in enumerate(rows):
        if row["doi"]:
            by_doi[row["doi"]].append(idx)
    unique_dois = list(by_doi.keys())
    print(f"\n  papers with DOI: {sum(len(v) for v in by_doi.values())} / {len(rows)}")
    print(f"  unique DOIs to look up: {len(unique_dois)}")

    paper_ids = [f"DOI:{doi}" for doi in unique_dois]
    print(f"  S2AG batch lookups: {(len(paper_ids) + 499) // 500} batches of up to 500")

    # Initialize all rows to false; fill in successes.
    for row in rows:
        row["has_abstract_s2ag"] = False
        row["s2ag_paper_id"] = None

    if not paper_ids:
        return rows

    chunk_size = 500
    for start in tqdm(range(0, len(paper_ids), chunk_size), desc="S2AG batch lookups"):
        chunk_ids = paper_ids[start : start + chunk_size]
        chunk_dois = unique_dois[start : start + chunk_size]
        try:
            results = s2ag.batch_lookup(chunk_ids, fields=_S2AG_FIELDS)
        except RuntimeError as err:
            print(f"  WARN: batch failed at start={start}: {err}")
            continue
        for doi, paper in zip(chunk_dois, results, strict=True):
            if paper is None:
                continue
            paper_id = paper.get("paperId")
            has_abs = s2ag.has_abstract(paper)
            for row_idx in by_doi[doi]:
                rows[row_idx]["has_abstract_s2ag"] = has_abs
                rows[row_idx]["s2ag_paper_id"] = paper_id
        time.sleep(0.5)  # polite pacing on anonymous tier

    return rows


def _coverage_table(rows: list[dict[str, Any]], helpers: Any) -> pd.DataFrame:
    grouped: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["year"], row["field"])].append(row)
    records: list[dict[str, Any]] = []
    for (year, field), cell_rows in sorted(grouped.items()):
        n_total = len(cell_rows)
        n_oa = sum(1 for r in cell_rows if r["has_abstract_openalex"])
        n_s2 = sum(1 for r in cell_rows if r["has_abstract_s2ag"])
        n_join = sum(
            1 for r in cell_rows if r["has_abstract_openalex"] or r["has_abstract_s2ag"]
        )
        n_doi = sum(1 for r in cell_rows if r["doi"])
        n_s2_found = sum(1 for r in cell_rows if r["s2ag_paper_id"])
        # S2AG fill on OA no-abstract subset
        oa_no_abs = [r for r in cell_rows if not r["has_abstract_openalex"]]
        n_fill = sum(1 for r in oa_no_abs if r["has_abstract_s2ag"])
        ci_low, ci_high = helpers.wilson_ci(n_join, n_total)
        records.append(
            {
                "year": year,
                "field": field,
                "n_sampled": n_total,
                "n_with_doi": n_doi,
                "n_s2ag_found": n_s2_found,
                "n_oa_abstract": n_oa,
                "n_s2ag_abstract": n_s2,
                "n_joint": n_join,
                "coverage_oa": n_oa / n_total if n_total else 0.0,
                "coverage_s2ag": n_s2 / n_total if n_total else 0.0,
                "coverage_joint": n_join / n_total if n_total else 0.0,
                "joint_ci_low": ci_low,
                "joint_ci_high": ci_high,
                "s2ag_fill_rate_on_no_abstract": (
                    n_fill / len(oa_no_abs) if oa_no_abs else float("nan")
                ),
                "n_oa_no_abstract": len(oa_no_abs),
            }
        )
    return pd.DataFrame(records)


def _make_plot(coverage_df: pd.DataFrame, out_path: Path) -> None:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    for ax, field in zip(axes, ["cs", "physics"], strict=False):
        sub = coverage_df[coverage_df["field"] == field].sort_values("year")
        ax.plot(sub["year"], sub["coverage_oa"], label="OpenAlex", color="#1f77b4", linewidth=1.4)
        ax.plot(sub["year"], sub["coverage_s2ag"], label="S2AG", color="#ff7f0e", linewidth=1.4)
        ax.plot(
            sub["year"],
            sub["coverage_joint"],
            label="Joint (OA OR S2AG)",
            color="#d62728",
            linewidth=2.2,
        )
        ax.fill_between(
            sub["year"], sub["joint_ci_low"], sub["joint_ci_high"], alpha=0.18, color="#d62728"
        )
        ax.axhline(0.95, color="gray", linestyle="--", linewidth=0.8)
        ax.set_xlabel("Publication year")
        ax.set_title(f"{field.upper()}")
        ax.set_ylim(-0.02, 1.02)
        ax.legend(loc="lower right", fontsize=9)
        ax.grid(True, alpha=0.3)
    axes[0].set_ylabel("Abstract coverage rate")
    fig.suptitle("Check 1e — OpenAlex vs. S2AG abstract coverage")
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _summarize(coverage_df: pd.DataFrame) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for field in ("cs", "physics"):
        sub = coverage_df[coverage_df["field"] == field].sort_values("year")
        post = sub[sub["year"] >= 1991]
        pre = sub[sub["year"] < 1991]

        # Pool over papers (weighted by n_sampled), not over cell-means.
        def _pool(df: pd.DataFrame, num: str, denom: str = "n_sampled") -> float:
            total_denom = df[denom].sum()
            return float(df[num].sum() / total_denom) if total_denom else float("nan")

        post_oa = _pool(post, "n_oa_abstract")
        post_s2 = _pool(post, "n_s2ag_abstract")
        post_joint = _pool(post, "n_joint")
        post_fill = _pool(post, "n_oa_no_abstract").__class__  # placeholder
        # S2AG fill on OA no-abstract: pool numerator and denominator independently.
        post_no_abs_total = post["n_oa_no_abstract"].sum()
        post_fill_count = (post["s2ag_fill_rate_on_no_abstract"].fillna(0) * post["n_oa_no_abstract"]).sum()
        post_fill = float(post_fill_count / post_no_abs_total) if post_no_abs_total else float("nan")

        pre_oa = _pool(pre, "n_oa_abstract")
        pre_s2 = _pool(pre, "n_s2ag_abstract")
        pre_joint = _pool(pre, "n_joint")
        pre_no_abs_total = pre["n_oa_no_abstract"].sum()
        pre_fill_count = (pre["s2ag_fill_rate_on_no_abstract"].fillna(0) * pre["n_oa_no_abstract"]).sum()
        pre_fill = float(pre_fill_count / pre_no_abs_total) if pre_no_abs_total else float("nan")

        n_with_doi = int(sub["n_with_doi"].sum())
        n_total = int(sub["n_sampled"].sum())
        n_s2ag_found = int(sub["n_s2ag_found"].sum())
        summary[field] = {
            "post1991_oa": post_oa,
            "post1991_s2": post_s2,
            "post1991_joint": post_joint,
            "post1991_fill_rate": post_fill,
            "pre1991_oa": pre_oa,
            "pre1991_s2": pre_s2,
            "pre1991_joint": pre_joint,
            "pre1991_fill_rate": pre_fill,
            "doi_rate": n_with_doi / n_total if n_total else float("nan"),
            "s2ag_found_rate_among_doi": (n_s2ag_found / n_with_doi) if n_with_doi else float("nan"),
        }
    return summary


def _write_summary_md(
    coverage_df: pd.DataFrame,
    summary: dict[str, Any],
    snapshot_date: str,
    n_calls: int,
) -> None:
    total_papers = int(coverage_df["n_sampled"].sum())

    def _pct(v: float | None) -> str:
        if v is None or (isinstance(v, float) and (v != v)):  # NaN check
            return "n/a"
        return f"{v:.1%}"

    body = f"""# Check 1e — S2AG abstract coverage on the same 22K-paper sample

**Run date:** {datetime.now(timezone.utc).date().isoformat()}
**Snapshot recorded:** {snapshot_date}
**Sample design:** same as Check 1 (200 papers per year × field cell, seed=42),
re-fetched from OpenAlex with `ids` extracted; DOIs cross-referenced against S2AG
via `/paper/batch`.
**Total papers:** {total_papers}
**Total API calls:** {n_calls}

## Headline numbers (era-aggregated, papers-pooled)

| Field | Era | OpenAlex | S2AG | Joint | S2AG fill on OA no-abstract |
|-------|-----|---------:|-----:|------:|----------------------------:|
| CS | 1970–1990 | {_pct(summary['cs']['pre1991_oa'])} | {_pct(summary['cs']['pre1991_s2'])} | {_pct(summary['cs']['pre1991_joint'])} | {_pct(summary['cs']['pre1991_fill_rate'])} |
| CS | 1991–2024 | {_pct(summary['cs']['post1991_oa'])} | {_pct(summary['cs']['post1991_s2'])} | {_pct(summary['cs']['post1991_joint'])} | **{_pct(summary['cs']['post1991_fill_rate'])}** |
| Physics | 1970–1990 | {_pct(summary['physics']['pre1991_oa'])} | {_pct(summary['physics']['pre1991_s2'])} | {_pct(summary['physics']['pre1991_joint'])} | {_pct(summary['physics']['pre1991_fill_rate'])} |
| Physics | 1991–2024 | {_pct(summary['physics']['post1991_oa'])} | {_pct(summary['physics']['post1991_s2'])} | {_pct(summary['physics']['post1991_joint'])} | **{_pct(summary['physics']['post1991_fill_rate'])}** |

## DOI-join feasibility

- CS: DOI rate {_pct(summary['cs']['doi_rate'])}; S2AG found rate among DOI-having papers {_pct(summary['cs']['s2ag_found_rate_among_doi'])}.
- Physics: DOI rate {_pct(summary['physics']['doi_rate'])}; S2AG found rate among DOI-having papers {_pct(summary['physics']['s2ag_found_rate_among_doi'])}.

## Decision (pre-registered rule)

The most decision-relevant number is **S2AG fill rate on the OpenAlex no-abstract
subset, post-1990** (bolded in the table above):

- **≥80%** → path (C) decisively wins. Proceed to wholesale Phase 0.1 plan revision.
- **50-80%** → path (C) helps but doesn't fully solve. Targeted plan revision.
- **<50%** → path (C) is not the answer. Confront paths (A') or (B).

## Plot

![OpenAlex vs S2AG vs joint coverage](s2ag-coverage.png)

## Implications for plan revision

*(Filled after running and inspecting the headline numbers above.)*
"""
    out_path = _OUT_DIR / "s2ag-coverage.md"
    out_path.write_text(body)
    print(f"  wrote {out_path}")


def main() -> None:
    print("Check 1e — S2AG abstract coverage on the Check 1 sample")
    helpers = _import_check1_helpers()
    snapshot_date = openalex.latest_snapshot_date()

    print("\nStep 1: OpenAlex re-sample with DOI extraction")
    rows = _collect_openalex_with_doi()
    print(f"  collected {len(rows)} paper records")

    print("\nStep 2: S2AG batch lookups by DOI")
    rows = _enrich_with_s2ag(rows)

    raw_path = _OUT_DIR / "s2ag-coverage-raw.parquet"
    pd.DataFrame(rows).to_parquet(raw_path, index=False)
    print(f"  wrote {raw_path}")

    print("\nStep 3: joint coverage analysis")
    coverage_df = _coverage_table(rows, helpers)
    csv_path = _OUT_DIR / "s2ag-coverage.csv"
    coverage_df.to_csv(csv_path, index=False)
    print(f"  wrote {csv_path}")

    plot_path = _OUT_DIR / "s2ag-coverage.png"
    _make_plot(coverage_df, plot_path)
    print(f"  wrote {plot_path}")

    summary = _summarize(coverage_df)
    n_calls_openalex = len(_FIELDS) * len(_YEARS)
    n_calls_s2ag = (sum(1 for r in rows if r["doi"]) + 499) // 500
    _write_summary_md(coverage_df, summary, snapshot_date, n_calls_openalex + n_calls_s2ag)

    print("\nCheck 1e complete.")
    print("\nDecision-relevant numbers (S2AG fill rate on OpenAlex no-abstract, post-1990):")
    print(f"  CS:      {summary['cs']['post1991_fill_rate']:.1%}" if summary['cs']['post1991_fill_rate'] == summary['cs']['post1991_fill_rate'] else "  CS: n/a")
    print(f"  Physics: {summary['physics']['post1991_fill_rate']:.1%}" if summary['physics']['post1991_fill_rate'] == summary['physics']['post1991_fill_rate'] else "  Physics: n/a")


if __name__ == "__main__":
    main()
