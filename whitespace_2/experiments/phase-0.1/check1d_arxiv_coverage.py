"""Check 1d — arXiv ID rate + joint OpenAlex/arXiv coverage + access-method verification.

Two extensions of Check 1:

1. **Joint coverage:** re-runs the same 110-cell sample with ``ids`` and
   ``locations`` added to the OpenAlex select projection. For each paper:
   ``has_abstract`` (from Check 1), ``has_arxiv`` (via OpenAlex's location-
   source-ID for arXiv or arXiv DOI prefix), ``joint = has_abstract OR
   has_arxiv``. If joint coverage approaches 80-90% post-1991 (CS arXiv
   coverage start), the §12 arXiv-promotion path is operationally feasible.

2. **Access-method verification:** picks 100 random papers from the original
   Check 1 raw parquet that we marked ``has_abstract=False``, fetches each via
   direct ID lookup (``/works/W{id}``) — a *different* code path than ``?filter
   + ?sample`` used in Check 1. Reports whether any unexpectedly returned an
   abstract via the direct path. If so, the original Check 1 finding is
   confounded by a ``?sample`` interaction; if not, the finding is robust to
   anonymous-access concerns.

Outputs:

- ``arxiv-coverage-raw.parquet`` — per-paper rows with all flags
- ``arxiv-coverage.csv`` — per-(year, field) joint coverage rates
- ``arxiv-coverage.png`` — joint coverage plot (CS + Physics, two panels)
- ``arxiv-coverage.md`` — summary + interpretation
- ``verification-spot-check.csv`` — 100-paper verification result
"""

from __future__ import annotations

import importlib.util
import random
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
_SELECT = ["id", "publication_year", "abstract_inverted_index", "type", "ids", "locations"]
_VERIFICATION_N = 100
_VERIFICATION_SEED = 7


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


def _collect_with_arxiv() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    cells = [(f, c, y) for f, c in _FIELDS.items() for y in _YEARS]
    for field, concept_id, year in tqdm(cells, desc="Sampling cells (with arxiv signals)"):
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
            has_abs = openalex.has_abstract(work)
            has_arx = openalex.has_arxiv(work)
            rows.append(
                {
                    "work_id": work.get("id"),
                    "year": year,
                    "field": field,
                    "type": work.get("type") or "unknown",
                    "has_abstract": has_abs,
                    "has_arxiv": has_arx,
                    "joint": has_abs or has_arx,
                }
            )
        time.sleep(0.5)
    return rows


def _joint_coverage(rows: list[dict[str, Any]], helpers: Any) -> pd.DataFrame:
    grouped: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["year"], row["field"])].append(row)
    records: list[dict[str, Any]] = []
    for (year, field), cell_rows in sorted(grouped.items()):
        n_total = len(cell_rows)
        n_abs = sum(1 for r in cell_rows if r["has_abstract"])
        n_arx = sum(1 for r in cell_rows if r["has_arxiv"])
        n_joint = sum(1 for r in cell_rows if r["joint"])
        cov_abs = n_abs / n_total if n_total else 0.0
        cov_arx = n_arx / n_total if n_total else 0.0
        cov_joint = n_joint / n_total if n_total else 0.0
        ci_low, ci_high = helpers.wilson_ci(n_joint, n_total)
        records.append(
            {
                "year": year,
                "field": field,
                "n_sampled": n_total,
                "n_abstract": n_abs,
                "n_arxiv": n_arx,
                "n_joint": n_joint,
                "coverage_abstract": cov_abs,
                "coverage_arxiv": cov_arx,
                "coverage_joint": cov_joint,
                "joint_ci_low": ci_low,
                "joint_ci_high": ci_high,
            }
        )
    return pd.DataFrame(records)


def _make_plot(coverage_df: pd.DataFrame, out_path: Path) -> None:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    for ax, field in zip(axes, ["cs", "physics"], strict=False):
        sub = coverage_df[coverage_df["field"] == field].sort_values("year")
        ax.plot(sub["year"], sub["coverage_abstract"], label="OpenAlex abstract", color="#1f77b4")
        ax.plot(sub["year"], sub["coverage_arxiv"], label="arXiv linkage", color="#2ca02c")
        ax.plot(sub["year"], sub["coverage_joint"], label="Joint (abstract OR arxiv)", color="#d62728", linewidth=2)
        ax.fill_between(
            sub["year"],
            sub["joint_ci_low"],
            sub["joint_ci_high"],
            alpha=0.2,
            color="#d62728",
        )
        ax.axhline(0.95, color="gray", linestyle="--", linewidth=0.8)
        ax.axvline(1991, color="gray", linestyle=":", linewidth=0.8, alpha=0.5)
        ax.set_xlabel("Publication year")
        ax.set_title(f"{field.upper()}")
        ax.set_ylim(-0.02, 1.02)
        ax.legend(loc="upper left", fontsize=9)
        ax.grid(True, alpha=0.3)
    axes[0].set_ylabel("Coverage rate")
    fig.suptitle(
        "Check 1d — OpenAlex abstract / arXiv linkage / joint coverage by year"
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def _verify_no_abstract_via_direct_lookup(check1_raw_path: Path) -> pd.DataFrame:
    """Pick N papers marked has_abstract=False in Check 1's parquet, fetch each
    via direct ID lookup, report whether the direct path returns an abstract.
    """
    check1_df = pd.read_parquet(check1_raw_path)
    no_abs = check1_df[~check1_df["has_abstract"]]
    rng = random.Random(_VERIFICATION_SEED)
    sample_idxs = rng.sample(range(len(no_abs)), min(_VERIFICATION_N, len(no_abs)))
    sampled = no_abs.iloc[sample_idxs].copy()
    print(f"\nVerification spot-check: {len(sampled)} papers marked has_abstract=False via filter+sample")
    direct_results: list[dict[str, Any]] = []
    for _, row in tqdm(sampled.iterrows(), total=len(sampled), desc="Direct ID lookups"):
        work_id = row["work_id"]
        try:
            work = openalex.get_work(work_id)
            direct_has_abs = openalex.has_abstract(work)
        except RuntimeError as err:
            print(f"  WARN: lookup failed for {work_id}: {err}")
            direct_has_abs = None  # type: ignore[assignment]
        direct_results.append(
            {
                "work_id": work_id,
                "year": int(row["year"]),
                "field": row["field"],
                "filter_sample_has_abstract": False,
                "direct_lookup_has_abstract": direct_has_abs,
            }
        )
        time.sleep(0.3)
    return pd.DataFrame(direct_results)


def _write_summary_md(
    coverage_df: pd.DataFrame,
    verify_df: pd.DataFrame,
    snapshot_date: str,
    n_calls: int,
) -> None:
    total_papers = int(coverage_df["n_sampled"].sum())

    def _slice(field: str, year_min: int, year_max: int) -> pd.DataFrame:
        return coverage_df[
            (coverage_df["field"] == field)
            & (coverage_df["year"] >= year_min)
            & (coverage_df["year"] <= year_max)
        ]

    cs_post1991 = _slice("cs", 1991, 2024)
    phys_post1991 = _slice("physics", 1991, 2024)
    cs_pre1991 = _slice("cs", 1970, 1990)
    phys_pre1991 = _slice("physics", 1970, 1990)

    n_unexpected = int(verify_df["direct_lookup_has_abstract"].fillna(False).sum())
    n_lookup_failed = int(verify_df["direct_lookup_has_abstract"].isna().sum())
    n_confirmed_no_abstract = len(verify_df) - n_unexpected - n_lookup_failed

    body = f"""# Check 1d — arXiv linkage + joint coverage + access-method verification

**Run date:** {datetime.now(timezone.utc).date().isoformat()}
**Snapshot recorded:** {snapshot_date}
**Sample design:** same as Check 1 (200 papers per year × field cell, seed=42),
with `ids` + `locations` added to OpenAlex select projection.
**Total papers (joint analysis):** {total_papers}
**Total API calls:** {n_calls} (110 cell samples + 100 verification spot-checks)

## Joint coverage by era

| Field | Era | OpenAlex abstract | arXiv linkage | Joint (abstract OR arxiv) |
|-------|-----|------------------:|--------------:|--------------------------:|
| CS | 1970–1990 | {cs_pre1991['coverage_abstract'].mean():.1%} | {cs_pre1991['coverage_arxiv'].mean():.1%} | {cs_pre1991['coverage_joint'].mean():.1%} |
| CS | 1991–2024 | {cs_post1991['coverage_abstract'].mean():.1%} | {cs_post1991['coverage_arxiv'].mean():.1%} | {cs_post1991['coverage_joint'].mean():.1%} |
| Physics | 1970–1990 | {phys_pre1991['coverage_abstract'].mean():.1%} | {phys_pre1991['coverage_arxiv'].mean():.1%} | {phys_pre1991['coverage_joint'].mean():.1%} |
| Physics | 1991–2024 | {phys_post1991['coverage_abstract'].mean():.1%} | {phys_post1991['coverage_arxiv'].mean():.1%} | {phys_post1991['coverage_joint'].mean():.1%} |

## Access-method verification (100-paper spot-check)

Sampled 100 papers flagged `has_abstract=False` from Check 1's raw parquet
(via `?filter` + `?sample` code path). Re-fetched each via direct ID lookup
(`/works/W{{id}}` code path). Question: does the direct lookup return an
abstract that the filter-sample path missed?

- **Confirmed no abstract via direct lookup:** {n_confirmed_no_abstract} / {len(verify_df)}
- **Unexpected abstract via direct lookup:** {n_unexpected} / {len(verify_df)}
- **Lookup failed:** {n_lookup_failed} / {len(verify_df)}

If `n_unexpected` is small (≤2-3, plausibly 1-2% noise from concurrent
OpenAlex updates), the original Check 1 finding is robust to anonymous-
access / `?sample`-interaction concerns. If `n_unexpected` is meaningfully
large (≥10%), the original sample needs re-running through a different
path.

## Plot

![joint coverage by year](arxiv-coverage.png)

## Interpretation

*(See follow-up plan.md status note for the path-A/B/C decision based
on this Check 1d result.)*
"""
    out_path = _OUT_DIR / "arxiv-coverage.md"
    out_path.write_text(body)
    print(f"  wrote {out_path}")


def main() -> None:
    print("Check 1d — arXiv linkage + joint coverage + access-method verification")
    helpers = _import_check1_helpers()
    snapshot_date = openalex.latest_snapshot_date()
    print(f"\nSampling {len(_FIELDS) * len(_YEARS)} cells with ids+locations included...")
    rows = _collect_with_arxiv()
    print(f"  collected {len(rows)} paper records")
    raw_path = _OUT_DIR / "arxiv-coverage-raw.parquet"
    pd.DataFrame(rows).to_parquet(raw_path, index=False)
    print(f"  wrote {raw_path}")
    coverage_df = _joint_coverage(rows, helpers)
    csv_path = _OUT_DIR / "arxiv-coverage.csv"
    coverage_df.to_csv(csv_path, index=False)
    print(f"  wrote {csv_path}")
    plot_path = _OUT_DIR / "arxiv-coverage.png"
    _make_plot(coverage_df, plot_path)
    print(f"  wrote {plot_path}")

    print("\nVerification spot-check — direct ID lookups for {} no-abstract papers".format(_VERIFICATION_N))
    check1_raw_path = _OUT_DIR / "abstract-coverage-raw.parquet"
    verify_df = _verify_no_abstract_via_direct_lookup(check1_raw_path)
    verify_csv_path = _OUT_DIR / "verification-spot-check.csv"
    verify_df.to_csv(verify_csv_path, index=False)
    print(f"  wrote {verify_csv_path}")

    n_calls = len(_FIELDS) * len(_YEARS) + _VERIFICATION_N
    _write_summary_md(coverage_df, verify_df, snapshot_date, n_calls)
    print()
    print("Check 1d complete.")


if __name__ == "__main__":
    main()
