"""Check 2a (redesigned) — field-tag drift on a venue-anchored sample.

Original Check 2a (per phase-0.1-plan.md) was specified to measure the fraction
of OpenAlex papers carrying ≥1 concept tag, by year, as a diagnostic for
era-drift in the classifier. The Phase 0.1 implementation (Check 2 — see
`check2_concept_classifier_drift.py`) sampled within the field concept filter,
forcing 100% coverage by sampling design — see `classifier-drift.md` §"2a —
Coverage is undefined as sampled". This redesign restores the substantive
question by sampling papers via venue (`primary_location.source.id`) instead of
concept, with venues hand-curated for clear-CS / clear-Physics identity. We
then ask whether OpenAlex's level-0 field tagging (CS C41008148 / Physics
C121332964) drifts across eras on these venue-restricted samples.

If the field-tag rate is roughly flat across years, ws2's analytical population
(papers carrying the field concept) is not era-biased at the field-tagging
step, so the §0 analytical-population definition is era-clean at the field
level. If it drifts, ws2 has an additional bias channel beyond the abstract-
having selection bias surfaced in Check 1f.

Outputs (under ``experiments/phase-0.1/``):

- ``check2a-venues.csv`` — resolved venue manifest (name, ISSN, OpenAlex source ID,
  works count, era coverage)
- ``check2a-field-tag-drift-raw.parquet`` — per-paper sampled rows
- ``check2a-field-tag-drift.csv`` — per-(year × field) field-tag rate at score
  thresholds 0.3 and 0.5, plus any-tag rate
- ``check2a-field-tag-drift.png`` — trend plot
- ``check2a-field-tag-drift.md`` — summary + interpretation

Run from ws2 root:
``uv run python experiments/phase-0.1/check2a_field_tag_drift.py``.
"""

from __future__ import annotations

import math
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from tqdm import tqdm

from whitespace2 import openalex


# ---------- venue manifest (audit-visible at top of file) ----------

# (display_name, primary_issn) — chosen for clear single-field identity and
# wide temporal coverage of 1970–2024 where possible. Some venues post-date
# 1970 (e.g., PRA/B/C/D split from Physical Review in 1970; Nature Physics
# 2005+) and will simply have empty pre-launch year cells.
_CS_VENUES: list[tuple[str, str]] = [
    ("Communications of the ACM", "0001-0782"),
    ("Journal of the ACM", "0004-5411"),
    ("ACM Transactions on Programming Languages and Systems", "0164-0925"),
    ("IEEE Transactions on Computers", "0018-9340"),
    ("IEEE Transactions on Information Theory", "0018-9448"),
    ("IEEE Transactions on Pattern Analysis and Machine Intelligence", "0162-8828"),
    ("Information and Computation", "0890-5401"),
    ("Theoretical Computer Science", "0304-3975"),
    ("Artificial Intelligence", "0004-3702"),
    ("SIAM Journal on Computing", "0097-5397"),
    ("Journal of Computer and System Sciences", "0022-0000"),
    ("IEEE Transactions on Software Engineering", "0098-5589"),
]

_PHYSICS_VENUES: list[tuple[str, str]] = [
    ("Physical Review Letters", "0031-9007"),
    ("Physical Review A", "1050-2947"),
    ("Physical Review B", "0163-1829"),
    ("Physical Review C", "0556-2813"),
    ("Physical Review D", "0556-2821"),
    ("Physical Review E", "1063-651X"),
    ("Reviews of Modern Physics", "0034-6861"),
    ("Physics Letters A", "0375-9601"),
    ("Physics Letters B", "0370-2693"),
    ("Annals of Physics", "0003-4916"),
    ("Nuclear Physics B", "0550-3213"),
    ("Astrophysical Journal", "0004-637X"),
]

_FIELD_CONCEPT: dict[str, str] = {
    "cs": "C41008148",
    "physics": "C121332964",
}
_YEARS = list(range(1970, 2025))
_SAMPLE_SIZE = 50  # per (venue × year) cell
_SEED = 42
_SCORE_LOOSE = 0.3
_SCORE_STRICT = 0.5
_SELECT = ["id", "publication_year", "concepts", "primary_location"]

_OUT_DIR = Path(__file__).parent
_BASE_URL = "https://api.openalex.org"


# ---------- venue resolution ----------


def _resolve_venue(issn: str, mailto: str = "gkartik@gmail.com") -> dict[str, Any] | None:
    """Resolve an ISSN to an OpenAlex source record. Returns None if not found."""
    params = {"filter": f"issn:{issn}", "mailto": mailto}
    resp = requests.get(
        f"{_BASE_URL}/sources",
        params=params,
        headers={"User-Agent": "ws2/0.0.0"},
        timeout=30,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if not isinstance(results, list) or not results:
        return None
    # Prefer exact issn_l match if present.
    for source in results:
        if isinstance(source, dict) and source.get("issn_l") == issn:
            return source
    return results[0] if isinstance(results[0], dict) else None


def _build_venue_manifest() -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for field, venues in (("cs", _CS_VENUES), ("physics", _PHYSICS_VENUES)):
        for name, issn in venues:
            source = _resolve_venue(issn)
            if source is None:
                print(f"  WARN: could not resolve {field} venue {name} (ISSN {issn})")
                rows.append(
                    {
                        "field": field,
                        "name": name,
                        "issn_input": issn,
                        "source_id": None,
                        "openalex_display_name": None,
                        "works_count": None,
                    }
                )
                continue
            source_id = source.get("id", "").rsplit("/", 1)[-1]
            display_name = source.get("display_name")
            works_count = source.get("works_count")
            print(f"  {field}: {name} (ISSN {issn}) → {source_id} '{display_name}' ({works_count} works)")
            rows.append(
                {
                    "field": field,
                    "name": name,
                    "issn_input": issn,
                    "source_id": source_id,
                    "openalex_display_name": display_name,
                    "works_count": works_count,
                }
            )
            time.sleep(0.2)
    return pd.DataFrame(rows)


# ---------- sampling ----------


def _sample_venue_year(source_id: str, year: int) -> list[dict[str, Any]]:
    return openalex.fetch_works(
        filters={
            "primary_location.source.id": source_id,
            "publication_year": str(year),
        },
        sample_size=_SAMPLE_SIZE,
        seed=_SEED,
        select=_SELECT,
    )


def _field_tag_score(work: dict[str, Any], field_concept_id: str) -> float | None:
    """Return the OpenAlex classifier score for the field concept on this work,
    or None if the field concept is not in the concepts array.
    """
    concepts = work.get("concepts") or []
    if not isinstance(concepts, list):
        return None
    for concept in concepts:
        if not isinstance(concept, dict):
            continue
        raw_id = concept.get("id") or ""
        bare_id = raw_id.rsplit("/", 1)[-1] if "/" in raw_id else raw_id
        if bare_id == field_concept_id:
            score = concept.get("score")
            return float(score) if score is not None else 0.0
    return None


def _max_concept_score(work: dict[str, Any]) -> float:
    concepts = work.get("concepts") or []
    scores = [
        float(c.get("score") or 0.0)
        for c in concepts
        if isinstance(c, dict)
    ]
    return max(scores) if scores else 0.0


def _collect_samples(venues_df: pd.DataFrame) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    cells: list[tuple[str, str, str, int]] = []
    for _, vrow in venues_df.iterrows():
        if vrow["source_id"] is None or pd.isna(vrow["source_id"]):
            continue
        field = vrow["field"]
        for year in _YEARS:
            cells.append((field, vrow["source_id"], vrow["name"], year))

    for field, source_id, venue_name, year in tqdm(cells, desc="Sampling venue × year"):
        try:
            works = _sample_venue_year(source_id, year)
        except RuntimeError as err:
            print(f"  WARN: skipping {field}/{venue_name}/{year}: {err}")
            continue
        for work in works:
            field_concept = _FIELD_CONCEPT[field]
            field_score = _field_tag_score(work, field_concept)
            rows.append(
                {
                    "work_id": work.get("id"),
                    "year": year,
                    "field": field,
                    "venue_name": venue_name,
                    "source_id": source_id,
                    "field_tag_score": field_score,
                    "has_field_tag_loose": (field_score is not None) and field_score >= _SCORE_LOOSE,
                    "has_field_tag_strict": (field_score is not None) and field_score >= _SCORE_STRICT,
                    "max_concept_score": _max_concept_score(work),
                }
            )
        time.sleep(0.2)
    return rows


# ---------- aggregation ----------


def wilson_ci(successes: int, n: int) -> tuple[float, float]:
    """Wilson score 95% CI for a binomial proportion."""
    if n == 0:
        return 0.0, 1.0
    z = 1.959963984540054  # 95%
    p = successes / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = (z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def _aggregate(rows: list[dict[str, Any]]) -> pd.DataFrame:
    grouped: dict[tuple[int, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["year"], row["field"])].append(row)

    records: list[dict[str, Any]] = []
    for (year, field), cell_rows in sorted(grouped.items()):
        n = len(cell_rows)
        n_loose = sum(1 for r in cell_rows if r["has_field_tag_loose"])
        n_strict = sum(1 for r in cell_rows if r["has_field_tag_strict"])
        n_any_tag = sum(1 for r in cell_rows if r["max_concept_score"] >= _SCORE_LOOSE)
        loose_low, loose_high = wilson_ci(n_loose, n)
        records.append(
            {
                "year": year,
                "field": field,
                "n": n,
                "n_field_tag_loose": n_loose,
                "rate_field_tag_loose": n_loose / n if n else 0.0,
                "ci_low_loose": loose_low,
                "ci_high_loose": loose_high,
                "n_field_tag_strict": n_strict,
                "rate_field_tag_strict": n_strict / n if n else 0.0,
                "n_any_tag_loose": n_any_tag,
                "rate_any_tag_loose": n_any_tag / n if n else 0.0,
            }
        )
    return pd.DataFrame(records)


# ---------- plotting ----------


def _make_plot(df: pd.DataFrame, out_path: Path) -> None:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
    for ax, field, color in [
        (axes[0], "cs", "#1f77b4"),
        (axes[1], "physics", "#d62728"),
    ]:
        sub = df[df["field"] == field].sort_values("year")
        ax.plot(
            sub["year"],
            sub["rate_field_tag_loose"],
            label="field tag, score≥0.3",
            color=color,
            linewidth=1.5,
        )
        ax.fill_between(
            sub["year"],
            sub["ci_low_loose"],
            sub["ci_high_loose"],
            alpha=0.2,
            color=color,
        )
        ax.plot(
            sub["year"],
            sub["rate_field_tag_strict"],
            label="field tag, score≥0.5",
            color=color,
            linewidth=1.0,
            linestyle="--",
        )
        ax.plot(
            sub["year"],
            sub["rate_any_tag_loose"],
            label="any tag, score≥0.3",
            color="gray",
            linewidth=0.8,
            alpha=0.6,
        )
        ax.set_title(f"{field.upper()} — venue-anchored field-tag rate")
        ax.set_xlabel("Publication year")
        ax.set_ylim(-0.02, 1.02)
        ax.grid(True, alpha=0.3)
        ax.legend(loc="lower right", fontsize=9)
    axes[0].set_ylabel("Fraction of papers carrying field tag")
    fig.suptitle("Check 2a (redesigned) — field-tag drift on hand-curated CS + Physics venues")
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


# ---------- summary ----------


def _summarize(df: pd.DataFrame) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for field in ("cs", "physics"):
        sub = df[df["field"] == field].sort_values("year")
        if sub.empty:
            continue
        pre = sub[sub["year"] < 1990]["rate_field_tag_loose"].mean()
        post = sub[sub["year"] >= 1990]["rate_field_tag_loose"].mean()
        recent = sub[sub["year"] >= 2010]["rate_field_tag_loose"].mean()
        # Linear trend slope on rate_field_tag_loose vs. year.
        if len(sub) >= 2:
            xs = sub["year"].to_numpy(dtype=float)
            ys = sub["rate_field_tag_loose"].to_numpy(dtype=float)
            slope = float(((xs - xs.mean()) * (ys - ys.mean())).sum() / ((xs - xs.mean()) ** 2).sum())
        else:
            slope = 0.0
        summary[field] = {
            "mean_pre1990_loose": float(pre) if not pd.isna(pre) else None,
            "mean_post1990_loose": float(post) if not pd.isna(post) else None,
            "mean_2010plus_loose": float(recent) if not pd.isna(recent) else None,
            "linear_slope_per_year": slope,
        }
    return summary


def _fmt_pct(value: float | None) -> str:
    return f"{value:.1%}" if value is not None else "n/a"


def _write_summary_md(
    df: pd.DataFrame,
    summary: dict[str, Any],
    venues_df: pd.DataFrame,
    snapshot: str,
    n_calls: int,
) -> None:
    n_total = int(df["n"].sum())
    cs_pre = _fmt_pct(summary.get("cs", {}).get("mean_pre1990_loose"))
    cs_post = _fmt_pct(summary.get("cs", {}).get("mean_post1990_loose"))
    cs_recent = _fmt_pct(summary.get("cs", {}).get("mean_2010plus_loose"))
    cs_slope = summary.get("cs", {}).get("linear_slope_per_year", 0.0)
    ph_pre = _fmt_pct(summary.get("physics", {}).get("mean_pre1990_loose"))
    ph_post = _fmt_pct(summary.get("physics", {}).get("mean_post1990_loose"))
    ph_recent = _fmt_pct(summary.get("physics", {}).get("mean_2010plus_loose"))
    ph_slope = summary.get("physics", {}).get("linear_slope_per_year", 0.0)

    venues_resolved = venues_df[venues_df["source_id"].notna()]
    cs_venue_count = int((venues_resolved["field"] == "cs").sum())
    ph_venue_count = int((venues_resolved["field"] == "physics").sum())

    body = f"""# Check 2a (redesigned) — field-tag drift, venue-anchored

**Run date:** {datetime.now(timezone.utc).date().isoformat()}
**Snapshot recorded:** {snapshot}
**Sample design:** {_SAMPLE_SIZE} papers per (venue × year) cell, OpenAlex `?sample` with seed={_SEED}; sampled via `primary_location.source.id` filter (NOT via concept filter — that's the redesign).
**Years:** {min(_YEARS)}–{max(_YEARS)}
**Venues resolved:** CS = {cs_venue_count} / {len(_CS_VENUES)}; Physics = {ph_venue_count} / {len(_PHYSICS_VENUES)}. See `check2a-venues.csv` for the full manifest.
**Total papers sampled:** {n_total}
**Total OpenAlex API calls:** ~{n_calls}

## Question

Does OpenAlex's level-0 field tagging (CS `C41008148` / Physics `C121332964`)
drift across eras? Original Check 2a was undefined-as-sampled because the
sampling pipeline filtered by the field concept itself; this redesign samples
via venue and asks whether the field tag attaches at era-stable rates.

## Headline numbers (field tag at score ≥ 0.3)

| Field | Pre-1990 | Post-1990 | 2010+ | Linear slope |
|-------|---------:|----------:|------:|-------------:|
| CS | {cs_pre} | {cs_post} | {cs_recent} | {cs_slope:+.4f} /yr |
| Physics | {ph_pre} | {ph_post} | {ph_recent} | {ph_slope:+.4f} /yr |

## Interpretation rubric (pre-registered)

- **Field-tag rate flat across years (drift |slope| < 0.002 /yr, ≈ < 11 pp over 55 yr):**
  no era-drift in field-level tagging on canonical-venue papers. ws2's
  analytical population is era-clean at the field-tagging step, beyond the
  abstract-having selection bias surfaced in Check 1f. **Plan revision absorbs
  this as a clean Limitations sentence; no new bias channel.**
- **Field-tag rate rising over time (slope > +0.002 /yr):** era-drift IS
  present. ws2's analytical population is era-biased at the field-tagging step
  in addition to the abstract-having bias. The §0 analytical-population
  definition gains an era-conditional caveat; §9e propensity model gains a
  field-tag-rate-by-year covariate (or scope-narrows pre-1990).
- **Field-tag rate falling over time:** unlikely; would suggest classifier
  retroactively improving on older papers. Document and investigate.

## Plot

![field-tag drift](check2a-field-tag-drift.png)

## Detailed table

See `check2a-field-tag-drift.csv` for per-(year × field) field-tag rates at
both score thresholds plus any-tag rate.

## Venue manifest

See `check2a-venues.csv` for the resolved venue list (name, ISSN, OpenAlex
source ID, works count). Venues hand-curated for clear single-field identity
and broad temporal coverage 1970–2024.
"""
    out_path = _OUT_DIR / "check2a-field-tag-drift.md"
    out_path.write_text(body)
    print(f"  wrote {out_path}")


# ---------- main ----------


def main() -> None:
    print("Check 2a (redesigned) — field-tag drift on venue-anchored sample")
    print(f"  out_dir: {_OUT_DIR}")
    print()
    snapshot = openalex.latest_snapshot_date()
    print("Resolving venue ISSNs to OpenAlex source IDs...")
    venues_df = _build_venue_manifest()
    venues_path = _OUT_DIR / "check2a-venues.csv"
    venues_df.to_csv(venues_path, index=False)
    print(f"  wrote {venues_path}")
    print()
    print("Sampling venue × year cells...")
    rows = _collect_samples(venues_df)
    print(f"  collected {len(rows)} paper records")
    raw_path = _OUT_DIR / "check2a-field-tag-drift-raw.parquet"
    pd.DataFrame(rows).to_parquet(raw_path, index=False)
    print(f"  wrote {raw_path}")
    print()
    print("Aggregating per-year field-tag rates...")
    df = _aggregate(rows)
    csv_path = _OUT_DIR / "check2a-field-tag-drift.csv"
    df.to_csv(csv_path, index=False)
    print(f"  wrote {csv_path}")
    plot_path = _OUT_DIR / "check2a-field-tag-drift.png"
    _make_plot(df, plot_path)
    print(f"  wrote {plot_path}")
    summary = _summarize(df)
    n_resolved_venues = int(venues_df["source_id"].notna().sum())
    n_calls = len(_CS_VENUES) + len(_PHYSICS_VENUES) + n_resolved_venues * len(_YEARS)
    _write_summary_md(df, summary, venues_df, snapshot, n_calls)
    print()
    print("Check 2a (redesigned) complete.")


if __name__ == "__main__":
    main()
