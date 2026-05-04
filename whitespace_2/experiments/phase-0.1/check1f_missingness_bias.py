"""Check 1f — bias-of-missingness diagnostic.

Question: does ``has_abstract`` correlate systematically with the substantive
measurement axes ws2 cares about? Specifically:

- **Citation count** — would bias the canonical-concentration metric.
- **Country of first authorship** — would bias the demographic-plurality metric.
- **Top-level concept (subfield)** — would bias the semantic-plurality metric.
- **Paper type** — already known from Check 1c, included for completeness.

If missingness is approximately random with respect to these axes, path (B)
(acknowledge ~50% bottleneck and proceed with narrower analytical population)
is clean — the missing ~50% is essentially noise. If missingness is structured
along these axes, path (B) requires explicit selection-on-observables
corrections, and possibly constrains the substantive claims that can be made.

Re-samples the same 110 cells (seed=42) with an expanded OpenAlex select to
pull authorships, concepts, cited_by_count, primary_location. Cost: $0.
Wall-clock: ~3-4 min.

Outputs to ``experiments/phase-0.1/``:

- ``missingness-bias-raw.parquet``
- ``missingness-bias.csv`` (coverage by stratum, several strata)
- ``missingness-bias.png`` (4-panel: by country, by concept, by type, by
  citation-count tertile)
- ``missingness-bias.md`` (summary + decision support)
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
_SELECT = [
    "id",
    "publication_year",
    "abstract_inverted_index",
    "type",
    "ids",
    "authorships",
    "concepts",
    "cited_by_count",
]


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


def _collect_with_strata() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    cells = [(f, c, y) for f, c in _FIELDS.items() for y in _YEARS]
    for field, concept_id, year in tqdm(cells, desc="OpenAlex re-sample (with strata)"):
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
                    "has_doi": openalex.extract_doi(work) is not None,
                    "country": openalex.extract_first_country(work) or "UNKNOWN",
                    "top_concept": openalex.extract_top_concept_id(work, level=1)
                    or "UNKNOWN",
                    "cited_by_count": work.get("cited_by_count") or 0,
                }
            )
        time.sleep(0.5)
    return rows


def _coverage_by_stratum(
    df: pd.DataFrame, stratum_col: str, min_n: int = 50
) -> pd.DataFrame:
    grouped: dict[Any, dict[str, Any]] = defaultdict(lambda: {"n": 0, "n_with_abstract": 0})
    for _, row in df.iterrows():
        key = row[stratum_col]
        grouped[key]["n"] += 1
        if row["has_abstract"]:
            grouped[key]["n_with_abstract"] += 1
    records = []
    for key, vals in grouped.items():
        if vals["n"] < min_n:
            continue
        rate = vals["n_with_abstract"] / vals["n"]
        records.append(
            {
                "stratum": key,
                "n": vals["n"],
                "n_with_abstract": vals["n_with_abstract"],
                "coverage": rate,
            }
        )
    return pd.DataFrame(records).sort_values("coverage", ascending=False)


def _citation_strata(df: pd.DataFrame) -> pd.DataFrame:
    """Coverage by citation-count tertile (within each field)."""
    records = []
    for field in ("cs", "physics"):
        sub = df[df["field"] == field].copy()
        if len(sub) == 0:
            continue
        # Tertiles on cited_by_count
        cuts = sub["cited_by_count"].quantile([0.0, 1 / 3, 2 / 3, 1.0]).values
        # Ensure unique edges (lots of zeros at low end can collapse)
        cuts = np.unique(cuts)
        if len(cuts) < 3:
            # too many ties; fall back to two strata or skip
            continue
        labels = [f"T{i+1}" for i in range(len(cuts) - 1)]
        sub["tertile"] = pd.cut(
            sub["cited_by_count"], bins=cuts, labels=labels, include_lowest=True
        )
        for tertile in labels:
            sub_t = sub[sub["tertile"] == tertile]
            if len(sub_t) == 0:
                continue
            n = len(sub_t)
            n_abs = int(sub_t["has_abstract"].sum())
            records.append(
                {
                    "field": field,
                    "tertile": tertile,
                    "min_citations": int(sub_t["cited_by_count"].min()),
                    "max_citations": int(sub_t["cited_by_count"].max()),
                    "n": n,
                    "n_with_abstract": n_abs,
                    "coverage": n_abs / n if n else 0.0,
                    "mean_citations": float(sub_t["cited_by_count"].mean()),
                }
            )
    return pd.DataFrame(records)


def _gini(values: np.ndarray) -> float:
    """Standard Gini coefficient on a non-negative array. Returns 0 if empty
    or all zeros.
    """
    arr = np.array(values, dtype=float)
    if len(arr) == 0 or arr.sum() == 0:
        return 0.0
    arr = np.sort(arr)
    n = len(arr)
    cum = np.cumsum(arr)
    return float((n + 1 - 2 * np.sum(cum) / cum[-1]) / n)


def _summarize_bias(
    df: pd.DataFrame,
    by_country: pd.DataFrame,
    by_concept: pd.DataFrame,
    by_type: pd.DataFrame,
    by_citation: pd.DataFrame,
) -> dict[str, Any]:
    summary: dict[str, Any] = {}

    # Citation count: t-statistic / Mann-Whitney equivalent. Use medians.
    abstract_yes = df[df["has_abstract"]]["cited_by_count"].values
    abstract_no = df[~df["has_abstract"]]["cited_by_count"].values
    summary["citation"] = {
        "median_with_abstract": float(np.median(abstract_yes)) if len(abstract_yes) else None,
        "median_no_abstract": float(np.median(abstract_no)) if len(abstract_no) else None,
        "mean_with_abstract": float(np.mean(abstract_yes)) if len(abstract_yes) else None,
        "mean_no_abstract": float(np.mean(abstract_no)) if len(abstract_no) else None,
    }
    try:
        from scipy.stats import mannwhitneyu  # type: ignore[import-untyped]

        if len(abstract_yes) and len(abstract_no):
            stat, pval = mannwhitneyu(abstract_yes, abstract_no, alternative="two-sided")
            summary["citation"]["mannwhitney_u"] = float(stat)
            summary["citation"]["mannwhitney_p"] = float(pval)
    except ImportError:
        pass

    # Country: spread of coverage across major countries
    if len(by_country) > 0:
        summary["country"] = {
            "n_strata": len(by_country),
            "max_coverage": float(by_country["coverage"].max()),
            "min_coverage": float(by_country["coverage"].min()),
            "iqr_coverage": float(
                by_country["coverage"].quantile(0.75) - by_country["coverage"].quantile(0.25)
            ),
            "top_5_countries": by_country.head(5).to_dict("records"),
            "bottom_5_countries": by_country.tail(5).to_dict("records"),
        }

    # Concept: spread
    if len(by_concept) > 0:
        summary["concept"] = {
            "n_strata": len(by_concept),
            "max_coverage": float(by_concept["coverage"].max()),
            "min_coverage": float(by_concept["coverage"].min()),
            "iqr_coverage": float(
                by_concept["coverage"].quantile(0.75) - by_concept["coverage"].quantile(0.25)
            ),
        }

    # Type: spread
    if len(by_type) > 0:
        summary["type"] = {
            "n_strata": len(by_type),
            "max_coverage": float(by_type["coverage"].max()),
            "min_coverage": float(by_type["coverage"].min()),
        }

    # Citation tertile coverage delta
    if len(by_citation) > 0:
        summary["citation_tertile"] = by_citation.to_dict("records")

    return summary


def _make_plot(
    by_country: pd.DataFrame,
    by_concept: pd.DataFrame,
    by_type: pd.DataFrame,
    by_citation: pd.DataFrame,
    out_path: Path,
) -> None:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Country (top-15 by n)
    ax = axes[0, 0]
    top = by_country.sort_values("n", ascending=False).head(15).sort_values("coverage")
    ax.barh(range(len(top)), top["coverage"], color="#4c72b0", alpha=0.8)
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels(top["stratum"])
    ax.set_xlim(0, 1.05)
    ax.axvline(0.5, color="gray", linestyle="--", linewidth=0.8)
    ax.set_xlabel("Abstract coverage")
    ax.set_title("By country of first authorship (top-15 by n)")
    ax.grid(True, axis="x", alpha=0.3)

    # Concept (top-15 by n)
    ax = axes[0, 1]
    top = by_concept.sort_values("n", ascending=False).head(15).sort_values("coverage")
    ax.barh(range(len(top)), top["coverage"], color="#55a868", alpha=0.8)
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels(top["stratum"])
    ax.set_xlim(0, 1.05)
    ax.axvline(0.5, color="gray", linestyle="--", linewidth=0.8)
    ax.set_xlabel("Abstract coverage")
    ax.set_title("By top-level (level=1) concept (top-15 by n)")
    ax.grid(True, axis="x", alpha=0.3)

    # Type
    ax = axes[1, 0]
    top = by_type.sort_values("coverage")
    ax.barh(range(len(top)), top["coverage"], color="#c44e52", alpha=0.8)
    ax.set_yticks(range(len(top)))
    ax.set_yticklabels(top["stratum"])
    ax.set_xlim(0, 1.05)
    ax.axvline(0.5, color="gray", linestyle="--", linewidth=0.8)
    ax.set_xlabel("Abstract coverage")
    ax.set_title("By paper type")
    ax.grid(True, axis="x", alpha=0.3)

    # Citation tertile
    ax = axes[1, 1]
    if len(by_citation) > 0:
        cs = by_citation[by_citation["field"] == "cs"]
        ph = by_citation[by_citation["field"] == "physics"]
        x = np.arange(len(cs))
        width = 0.35
        ax.bar(x - width / 2, cs["coverage"], width, label="CS", color="#1f77b4", alpha=0.8)
        ax.bar(x + width / 2, ph["coverage"], width, label="Physics", color="#d62728", alpha=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(cs["tertile"])
        ax.set_ylim(0, 1.05)
        ax.axhline(0.5, color="gray", linestyle="--", linewidth=0.8)
        ax.set_ylabel("Abstract coverage")
        ax.set_xlabel("Citation count tertile (within field)")
        ax.set_title("By citation-count tertile")
        ax.legend()
        ax.grid(True, axis="y", alpha=0.3)

    fig.suptitle(
        "Check 1f — bias of has_abstract missingness across substantive measurement axes",
        fontsize=13,
    )
    fig.tight_layout()
    fig.savefig(out_path, dpi=110)
    plt.close(fig)


def _write_summary_md(
    df: pd.DataFrame,
    by_country: pd.DataFrame,
    by_concept: pd.DataFrame,
    by_type: pd.DataFrame,
    by_citation: pd.DataFrame,
    summary: dict[str, Any],
    snapshot_date: str,
) -> None:
    n_total = len(df)
    n_abstract = int(df["has_abstract"].sum())
    cit = summary.get("citation", {})
    country = summary.get("country", {})
    concept = summary.get("concept", {})

    lines = [
        "# Check 1f — bias of missingness across substantive measurement axes",
        "",
        f"**Run date:** {datetime.now(timezone.utc).date().isoformat()}",
        f"**Snapshot recorded:** {snapshot_date}",
        f"**Sample design:** same as Check 1 (200 papers per year × field cell, seed=42), "
        "with authorships, concepts, cited_by_count added to OpenAlex select.",
        f"**Total papers:** {n_total}; with abstract: {n_abstract} ({n_abstract/n_total:.1%})",
        "",
        "## Question",
        "",
        "Does `has_abstract` correlate systematically with substantive measurement axes — "
        "in ways that would bias ws2's central decoupling claim?",
        "",
        "## Headline findings",
        "",
        "### 1. Citation count",
        "",
    ]
    if cit:
        m_yes = cit.get("median_with_abstract")
        m_no = cit.get("median_no_abstract")
        u_yes = cit.get("mean_with_abstract")
        u_no = cit.get("mean_no_abstract")
        p = cit.get("mannwhitney_p")
        lines.append(
            f"- Median citations: with abstract = **{m_yes:.0f}**; without = **{m_no:.0f}**"
        )
        lines.append(
            f"- Mean citations: with abstract = **{u_yes:.1f}**; without = **{u_no:.1f}**"
        )
        if p is not None:
            lines.append(f"- Mann-Whitney p = {p:.2e}")
        if m_yes is not None and m_no is not None and m_yes > 0:
            ratio = m_yes / max(m_no, 1)
            lines.append(
                f"- **Bias direction:** abstract-having papers have {ratio:.1f}× the median "
                "citation count of no-abstract papers." if ratio > 1.5
                else f"- Median citation ratio = {ratio:.1f} — modest difference."
            )

    lines.extend(["", "### 2. Country of first authorship", ""])
    if country:
        lines.append(
            f"- Coverage range across major countries (n≥50): "
            f"**{country['min_coverage']:.1%} – {country['max_coverage']:.1%}** "
            f"(IQR {country['iqr_coverage']:.1%})"
        )
        lines.append(f"- Strata reported: {country['n_strata']} countries with n≥50")
        lines.append("")
        lines.append("**Top-5 highest coverage:**")
        for row in country["top_5_countries"]:
            lines.append(
                f"  - {row['stratum']}: {row['coverage']:.1%} (n={int(row['n'])})"
            )
        lines.append("")
        lines.append("**Bottom-5 lowest coverage:**")
        for row in country["bottom_5_countries"]:
            lines.append(
                f"  - {row['stratum']}: {row['coverage']:.1%} (n={int(row['n'])})"
            )

    lines.extend(["", "### 3. Top-level concept (subfield)", ""])
    if concept:
        lines.append(
            f"- Coverage range across major concepts (n≥50): "
            f"**{concept['min_coverage']:.1%} – {concept['max_coverage']:.1%}** "
            f"(IQR {concept['iqr_coverage']:.1%})"
        )
        lines.append(f"- Strata reported: {concept['n_strata']} concepts with n≥50")

    lines.extend(["", "### 4. Citation count tertile (within field)", ""])
    for row in summary.get("citation_tertile", []):
        lines.append(
            f"- **{row['field']} {row['tertile']}** (citations {row['min_citations']}-"
            f"{row['max_citations']}, n={row['n']}): coverage {row['coverage']:.1%}"
        )

    lines.extend(
        [
            "",
            "## Plot",
            "",
            "![bias diagnostics](missingness-bias.png)",
            "",
            "## Decision support",
            "",
            "**Path (B) is clean if:**",
            "- Citation count is approximately balanced across has_abstract groups (median ratio ≤ 1.5).",
            "- Country coverage range is tight (IQR < 15 pp).",
            "- Concept coverage range is tight (IQR < 15 pp).",
            "- Citation-tertile coverage is approximately uniform.",
            "",
            "**Path (B) requires selection-on-observables corrections if:**",
            "- Citation count median ratio is > 1.5 (high-citation papers more likely to have abstracts).",
            "- Country coverage IQR is > 15 pp (Western/non-Western differences).",
            "- Concept coverage IQR is > 15 pp (subfields differ in availability).",
            "- Citation-tertile coverage is monotone (low-citation papers systematically missing).",
            "",
            "**Path (M3 — scope narrowing) is required if:**",
            "- Multiple bias axes are large enough that selection corrections cannot rescue interpretability.",
            "- The biases align with ws2's central measurement axes (demographic plurality ↔ country; "
            "semantic plurality ↔ concept; canonical concentration ↔ citation count).",
            "",
            "*(Final decision filled after inspection of the headline numbers above.)*",
        ]
    )
    out_path = _OUT_DIR / "missingness-bias.md"
    out_path.write_text("\n".join(lines))
    print(f"  wrote {out_path}")


def main() -> None:
    print("Check 1f — bias of has_abstract missingness")
    snapshot_date = openalex.latest_snapshot_date()

    print("\nStep 1: OpenAlex re-sample with strata fields")
    rows = _collect_with_strata()
    print(f"  collected {len(rows)} paper records")
    df = pd.DataFrame(rows)
    raw_path = _OUT_DIR / "missingness-bias-raw.parquet"
    df.to_parquet(raw_path, index=False)
    print(f"  wrote {raw_path}")

    print("\nStep 2: stratify and tabulate")
    by_country = _coverage_by_stratum(df, "country", min_n=50)
    by_concept = _coverage_by_stratum(df, "top_concept", min_n=50)
    by_type = _coverage_by_stratum(df, "type", min_n=50)
    by_citation = _citation_strata(df)

    csv_path = _OUT_DIR / "missingness-bias.csv"
    # Long-format CSV with stratum-type column
    parts = [
        by_country.assign(stratum_type="country"),
        by_concept.assign(stratum_type="concept"),
        by_type.assign(stratum_type="type"),
    ]
    pd.concat(parts).to_csv(csv_path, index=False)
    print(f"  wrote {csv_path}")
    by_citation.to_csv(_OUT_DIR / "missingness-bias-citation-tertiles.csv", index=False)

    plot_path = _OUT_DIR / "missingness-bias.png"
    _make_plot(by_country, by_concept, by_type, by_citation, plot_path)
    print(f"  wrote {plot_path}")

    print("\nStep 3: summarize bias direction and magnitude")
    summary = _summarize_bias(df, by_country, by_concept, by_type, by_citation)
    _write_summary_md(df, by_country, by_concept, by_type, by_citation, summary, snapshot_date)

    # Print headline numbers to stdout
    print()
    print("Headline:")
    cit = summary.get("citation", {})
    if cit:
        print(
            f"  citation median (with/no abs): {cit.get('median_with_abstract'):.0f} / "
            f"{cit.get('median_no_abstract'):.0f}"
        )
    if summary.get("country"):
        c = summary["country"]
        print(f"  country coverage range: {c['min_coverage']:.1%} – {c['max_coverage']:.1%} "
              f"(IQR {c['iqr_coverage']:.1%})")
    if summary.get("concept"):
        c = summary["concept"]
        print(f"  concept coverage range: {c['min_coverage']:.1%} – {c['max_coverage']:.1%} "
              f"(IQR {c['iqr_coverage']:.1%})")
    print()
    print("Check 1f complete.")


if __name__ == "__main__":
    main()
