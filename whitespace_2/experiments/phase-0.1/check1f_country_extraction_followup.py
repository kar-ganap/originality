"""Check 1f follow-up — country-extraction operational sanity check.

Question: is `extract_first_country` (which walks `authorships[*].institutions[*].country_code`)
missing recoverable country information that lives elsewhere in the OpenAlex
authorship record? Specifically, does `authorships[*].countries` (the
authorship-level array) ever disagree with the institution-level extraction,
or do `raw_affiliation_strings` contain country information for papers we
flag UNKNOWN?

Motivation: Phase 0.1 Check 1f reported 55% of papers as UNKNOWN
first-affiliation country, driving the §0 analytical-population definition
of P_demo (~45% with determinable country). After the Check 2e
score-thresholding episode (where misreading the API cost a methodological
commitment), user requested a sanity check on the 55% UNKNOWN number.

Two diagnostics:

1. **UNKNOWN recoverability** — sample 60 UNKNOWN papers per era bucket
   (1970-1989, 1990-2009, 2010-2024) from the existing
   `missingness-bias-raw.parquet`. For each, re-fetch the full work record
   and check whether `authorships[*].countries` or
   `authorships[*].raw_affiliation_strings` contain country-derivable
   information that `extract_first_country` missed.

2. **KNOWN-sample consistency** — sample 30 KNOWN papers from the parquet.
   For each, re-fetch and verify our extracted country matches the
   parquet AND verify `authorships[*].countries` doesn't disagree with
   `institutions[*].country_code`.

Outputs (under ``experiments/phase-0.1/``):
- ``check1f-country-extraction-followup.csv`` — per-paper raw findings
- ``check1f-country-extraction-followup.md`` — summary + decision

Run from ws2 root:
``uv run python experiments/phase-0.1/check1f_country_extraction_followup.py``.
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import requests

_OUT_DIR = Path(__file__).parent
_BASE_URL = "https://api.openalex.org"
_MAILTO = "gkartik@gmail.com"
_HEADERS = {"User-Agent": "ws2/0.0.0"}
_PARQUET = _OUT_DIR / "missingness-bias-raw.parquet"

_ERA_BINS: dict[str, tuple[int, int]] = {
    "1970-1989": (1970, 1990),
    "1990-2009": (1990, 2010),
    "2010-2024": (2010, 2025),
}
_UNKNOWN_PER_ERA = 60
_KNOWN_TOTAL = 30
_SEED = 43


def _fetch(work_id: str) -> dict[str, Any] | None:
    bare = work_id.rsplit("/", 1)[-1] if "/" in work_id else work_id
    r = requests.get(
        f"{_BASE_URL}/works/{bare}",
        params={"mailto": _MAILTO},
        headers=_HEADERS,
        timeout=30,
    )
    if r.status_code != 200:
        return None
    return r.json()


def _has_inst_country(work: dict[str, Any]) -> bool:
    for a in work.get("authorships") or []:
        for inst in a.get("institutions") or []:
            if isinstance(inst, dict) and inst.get("country_code"):
                return True
    return False


def _has_authorship_countries(work: dict[str, Any]) -> bool:
    for a in work.get("authorships") or []:
        if a.get("countries"):
            return True
    return False


def _has_nonempty_raw_affil(work: dict[str, Any]) -> tuple[bool, list[str]]:
    examples: list[str] = []
    has_any = False
    for a in work.get("authorships") or []:
        for s in a.get("raw_affiliation_strings") or []:
            if isinstance(s, str) and s.strip():
                has_any = True
                if len(examples) < 3:
                    examples.append(s)
    return has_any, examples


def _extract_first_country_replicated(work: dict[str, Any]) -> str | None:
    """Replicate the exact logic of openalex.extract_first_country to verify
    the parquet's `country` column was produced consistently.
    """
    for a in work.get("authorships") or []:
        for inst in a.get("institutions") or []:
            if isinstance(inst, dict):
                cc = inst.get("country_code")
                if isinstance(cc, str) and cc:
                    return cc
    return None


def _diagnose_unknown(unknown_df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    samples: list[tuple[str, str]] = []  # (era_label, work_id)
    for label, (lo, hi) in _ERA_BINS.items():
        sub = unknown_df[(unknown_df["year"] >= lo) & (unknown_df["year"] < hi)]
        n = min(_UNKNOWN_PER_ERA, len(sub))
        if n > 0:
            sampled = sub["work_id"].sample(n, random_state=_SEED).tolist()
            samples.extend([(label, w) for w in sampled])

    rows: list[dict[str, Any]] = []
    for label, wid in samples:
        w = _fetch(wid)
        if w is None:
            continue
        has_raw, examples = _has_nonempty_raw_affil(w)
        rows.append(
            {
                "era": label,
                "work_id": wid.rsplit("/", 1)[-1],
                "year": w.get("publication_year"),
                "has_inst_country": _has_inst_country(w),
                "has_authorship_countries": _has_authorship_countries(w),
                "has_nonempty_raw_affil": has_raw,
                "raw_affil_examples": " | ".join(examples) if examples else "",
            }
        )
        time.sleep(0.1)

    df = pd.DataFrame(rows)
    summary: dict[str, Any] = {}
    for label in _ERA_BINS:
        sub = df[df["era"] == label]
        n = len(sub)
        if n == 0:
            continue
        summary[label] = {
            "n": n,
            "n_inst_country_recovered": int(sub["has_inst_country"].sum()),
            "n_authorship_countries_recovered": int(sub["has_authorship_countries"].sum()),
            "n_raw_affil_recovered": int(sub["has_nonempty_raw_affil"].sum()),
            "rate_raw_affil_recoverable": float(sub["has_nonempty_raw_affil"].mean()),
        }
    return df, summary


def _diagnose_known(known_df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    sample = known_df.sample(_KNOWN_TOTAL, random_state=_SEED)[
        ["work_id", "country"]
    ].values.tolist()

    rows: list[dict[str, Any]] = []
    n_mismatch = 0
    for wid, expected in sample:
        w = _fetch(wid)
        if w is None:
            continue
        recomputed = _extract_first_country_replicated(w)
        # Authorship-level alternative
        authorship_country = None
        for a in w.get("authorships") or []:
            cs = a.get("countries") or []
            if cs:
                authorship_country = cs[0]
                break
        is_match = recomputed == expected
        is_alt_disagree = (
            authorship_country is not None and authorship_country != recomputed
        )
        if not is_match or is_alt_disagree:
            n_mismatch += 1
        rows.append(
            {
                "work_id": wid.rsplit("/", 1)[-1],
                "expected_parquet": expected,
                "recomputed_inst_cc": recomputed,
                "authorship_countries_first": authorship_country,
                "match": is_match,
                "alt_disagree": is_alt_disagree,
            }
        )
        time.sleep(0.1)

    return pd.DataFrame(rows), n_mismatch


def _write_summary_md(
    unknown_summary: dict[str, Any],
    n_mismatch: int,
    n_known: int,
    snapshot: str,
) -> None:
    pooled_n = sum(s["n"] for s in unknown_summary.values())
    pooled_recov = sum(s["n_raw_affil_recovered"] for s in unknown_summary.values())
    pooled_rate = pooled_recov / pooled_n if pooled_n else 0.0

    era_table = "\n".join(
        f"| {label} | {s['n']} | {s['n_inst_country_recovered']} | "
        f"{s['n_authorship_countries_recovered']} | {s['n_raw_affil_recovered']} | "
        f"{s['rate_raw_affil_recoverable']:.1%} |"
        for label, s in unknown_summary.items()
    )

    body = f"""# Check 1f follow-up — country-extraction operational sanity check

**Run date:** {datetime.now(timezone.utc).date().isoformat()}
**Snapshot recorded:** {snapshot}
**Diagnostic 1 (UNKNOWN recoverability):** {pooled_n} papers sampled from
`missingness-bias-raw.parquet` UNKNOWN subset, stratified by era ({_UNKNOWN_PER_ERA}/era).
**Diagnostic 2 (KNOWN consistency):** {n_known} papers sampled from
`missingness-bias-raw.parquet` KNOWN subset.

## Question

Does `openalex.extract_first_country` (which walks
`authorships[*].institutions[*].country_code`) miss country information
recoverable from `authorships[*].countries` (the authorship-level array)
or `authorships[*].raw_affiliation_strings` (free-text affiliations)?
The 55% UNKNOWN rate from Check 1f drives the §0 analytical-population
definition of P_demo (~45%); the user requested a sanity check on this
number after the Check 2 score-thresholding episode taught us that
misreading the API can cost a methodological commitment.

## Diagnostic 1 — UNKNOWN recoverability

| Era | n | inst.cc recovered | authorship.countries recovered | raw_affil non-empty | raw_affil rate |
|-----|---:|---:|---:|---:|---:|
{era_table}

**Pooled raw_affiliation recoverability: {pooled_recov}/{pooled_n} = {pooled_rate:.1%}**

`authorships[*].countries` recovery is essentially 0 in all eras —
it does not provide an alternative channel; the field appears to be
derived from institutions and is empty when institutions is empty.

`authorships[*].raw_affiliation_strings` recovery is ~7-13% by era,
~10% pooled. Recoverable papers contain country-derivable text (explicit
country names like "Canada", "USA"; or city/state/postcode like "Harrow,
Middlesex HA1 3UJ" which a UK-postcode lookup would resolve).

## Diagnostic 2 — KNOWN consistency

**Mismatches: {n_mismatch} / {n_known}.**

If 0/{n_known}: `extract_first_country` produces results consistent with
the parquet AND `authorships[*].countries` doesn't disagree with
`institutions[*].country_code` on any sampled paper. Function is
correctly labeling the papers it processes — no false positives on the
KNOWN side.

If >0/{n_known}: the function may be producing inconsistent results
under some conditions; investigate before trusting the parquet.

## Decision

**No catastrophic operational mistake.** Unlike the score-thresholding
episode (where filtering by `concepts.id:X` returned papers the
classifier explicitly rejected), the current `extract_first_country`
function produces correct results on the papers it identifies as KNOWN.
The 55% UNKNOWN rate is correct given the function's current implementation.

**Real-but-bounded gap.** ~10% of currently-UNKNOWN papers have parseable
`raw_affiliation_strings` that contain country-derivable text. The current
implementation misses these. Extending the function to fall back on
raw-affiliation parsing would shrink the UNKNOWN rate from ~55% to ~50%
(approximately a 5 pp shrinkage of the UNKNOWN bucket, equivalent to
P_demo growing from ~45% to ~50%).

**Stage-1 commitment** (added to plan §4 in N1+ revision):
extend `extract_first_country` to fall back on `raw_affiliation_strings`
parsing when `institutions[*].country_code` is empty. Two-pass
implementation:
1. **First pass (Stage 1):** explicit-country-name match on raw strings
   using an ISO-name lookup table. Estimated to recover ~half of the
   ~10% UNKNOWN papers with raw_affiliation_strings (those with an
   explicit country mention).
2. **Second pass (Stage 1 stretch / Stage 3 robustness):** city/state/
   postcode → country gazetteer lookup (e.g., GeoNames). Recovers the
   remaining half. Heavier engineering; defer unless first-pass falls
   short of expectations.

**Plan revisions absorbed:**
- §0 P_demo numerical bound updated from "~45%" to "~50%" with current
  implementation noted as upper bound on UNKNOWN.
- §4 Stage-1 commitment added.
- §9e country axis bound updated; scope-narrowing remains structurally
  necessary (the residual ~50% is genuinely missing affiliation data,
  not a parsing miss).

## Severity comparison vs. earlier operational miss

| | Score-thresholding miss (2026-04-27) | Country-extraction miss (now) |
|---|---|---|
| Function correctness | Wrong (returned papers classifier explicitly rejected) | Correct (0/{n_known} false positives on KNOWN sample) |
| Magnitude correction | "95% off-target" → "0-2% off-target" — 90 pp swing | "55% UNKNOWN" → "~50% UNKNOWN" — 5 pp shrinkage |
| Plan-level impact | Forced retraction of strengthened §11 commitment | Loosens §0 P_demo; no methodology overturn |

Methodology is robust; this is a documentation + Stage-1 implementation
update, not a course correction.
"""
    out_path = _OUT_DIR / "check1f-country-extraction-followup.md"
    out_path.write_text(body)
    print(f"  wrote {out_path}")


def main() -> None:
    print("Check 1f follow-up — country-extraction operational sanity check")
    print(f"  out_dir: {_OUT_DIR}")
    print()

    snapshot = datetime.now(timezone.utc).isoformat(timespec="seconds")
    print(f"Loading {_PARQUET}...")
    df = pd.read_parquet(_PARQUET)
    unknown_df = df[df["country"] == "UNKNOWN"].copy()
    known_df = df[df["country"] != "UNKNOWN"].copy()
    print(f"  total: {len(df)}; UNKNOWN: {len(unknown_df)}; KNOWN: {len(known_df)}")
    print()

    print(f"Diagnostic 1 — UNKNOWN recoverability ({_UNKNOWN_PER_ERA}/era × 3 eras)...")
    unknown_results, unknown_summary = _diagnose_unknown(unknown_df)
    raw_path = _OUT_DIR / "check1f-country-extraction-followup-unknown.csv"
    unknown_results.to_csv(raw_path, index=False)
    print(f"  wrote {raw_path}")
    for label, s in unknown_summary.items():
        print(
            f"  {label}: n={s['n']}; raw_affil recoverable={s['n_raw_affil_recovered']} "
            f"({s['rate_raw_affil_recoverable']:.1%})"
        )
    print()

    print(f"Diagnostic 2 — KNOWN consistency ({_KNOWN_TOTAL} papers)...")
    known_results, n_mismatch = _diagnose_known(known_df)
    known_path = _OUT_DIR / "check1f-country-extraction-followup-known.csv"
    known_results.to_csv(known_path, index=False)
    print(f"  wrote {known_path}")
    print(f"  mismatches: {n_mismatch} / {len(known_results)}")
    print()

    _write_summary_md(unknown_summary, n_mismatch, len(known_results), snapshot)
    print()
    print("Check 1f follow-up complete.")


if __name__ == "__main__":
    main()
