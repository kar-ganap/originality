"""Phase 0.2 Wave 1C — production pull-spec dry run.

Exercises the locked §0 analytical-population filter pipeline (post-
consolidation) end-to-end on fresh OpenAlex pulls AND validates the
over-filter rate against the Check 5a baseline on cs 1975.

Per `docs/phases/phase-0.2-plan.md` §0 (locked post-consolidation):
1. score ≥ 0.3 on field concept (loose threshold)
2. has_abstract (non-empty inverted index)
3. Junk-year-token filter: pre-1990 papers excluded if title/abstract
   contains any of 25 post-2000-coined tokens (consolidation §A
   removed pre-1990 chip names, generic cnn/rnn, https)
4. Empty-abstract filter: ≥15 tokens after inverted-index
   reconstruction (consolidation §B relaxed from 30)

Per `docs/phases/phase-0.2-execution.md` Wave 1C acceptance:
- <2% over-filter rate vs Check 5a baseline on cs 1975 (production
  filter shouldn't exclude legitimate papers the pilot kept).
- Zero false negatives in 50-row hand-audit (post-2000 content with
  1970s year not slipping through).

Three pulls:
- cs 1975 seed=42 sample=200 (matches Check 5a single cell;
  reproducible since OpenAlex seeds are server-side stable).
- cs 2024 seeds 100-124 (25 × 200 = 5K raw → exercise modern era).
- cs 1980 seeds 100-124 (25 × 200 = 5K raw → exercise pre-1990 era
  where junk-year filter actually fires).

Run from ws2 root:
    uv run python experiments/phase-0.2/pull_spec_dry_run.py
"""

from __future__ import annotations

import json
import random
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from tqdm import tqdm

from whitespace2 import openalex

# ---------- paths ----------

_OUT_DIR = Path(__file__).parent

# ---------- §0 locked production spec ----------

_FIELD_CONCEPT_ID = "C41008148"  # cs
_SCORE_THRESHOLD = 0.3
_JUNK_YEAR_THRESHOLD = 1990
_EMPTY_ABSTRACT_MIN_TOKENS = 15

# Production junk-year tokens (post-2000-coined; per consolidation §A)
_PRODUCTION_JUNK_YEAR_TOKENS: tuple[str, ...] = (
    # Original pilot 5
    "r-cnn", "iot", "blockchain", "transformer", "smartphone",
    # Post-2000 ML / deep learning (model-specific)
    "lstm", "gan", "bert", "gpt", "chatgpt", "attention is all you need",
    "word2vec", "glove", "risc-v",
    # Post-2000 protocols / formats
    "tls 1", "webrtc", "mqtt", "openid connect",
    # Post-2000 devices / contexts
    "wearable", "vr headset", "cloud computing", "big data",
    "internet of things", "digital twin", "arm cortex",
)

# Pilot junk-year tokens (Check 5a baseline; for over-filter delta)
_PILOT_JUNK_YEAR_TOKENS: tuple[str, ...] = (
    "r-cnn", "iot", "blockchain", "transformer", "smartphone",
)


def _compile_token_patterns(tokens: tuple[str, ...]) -> tuple[re.Pattern[str], ...]:
    """Word-boundary patterns. Critical: avoids `gan` matching `organism`,
    `iot` matching `patriot`, `bert` matching `Albert`, etc. The original
    substring-matching pattern caused 3/4 of Wave 1C's first-run drops
    (organisms, organic-data papers wrongly excluded by `gan`).
    """
    return tuple(
        re.compile(r"\b" + re.escape(tok) + r"\b", re.IGNORECASE)
        for tok in tokens
    )


_PRODUCTION_PATTERNS = _compile_token_patterns(_PRODUCTION_JUNK_YEAR_TOKENS)
_PILOT_PATTERNS = _compile_token_patterns(_PILOT_JUNK_YEAR_TOKENS)

_SELECT = [
    "id",
    "title",
    "publication_year",
    "type",
    "abstract_inverted_index",
    "authorships",
    "concepts",
    "cited_by_count",
    "primary_location",
    "ids",
]

# ---------- pull params ----------

_CS_1975_SEED = 42  # Check 5a parity

_DRY_RUN_SEEDS = list(range(100, 125))  # 25 seeds
_SAMPLE_PER_CELL = 200  # OpenAlex cap

_HAND_AUDIT_N = 50
_HAND_AUDIT_SEED = 7

# ---------- filter primitives ----------


def _field_concept_score(
    work: dict[str, Any], field_concept_id: str,
) -> float | None:
    concepts = work.get("concepts") or []
    if not isinstance(concepts, list):
        return None
    for concept in concepts:
        if not isinstance(concept, dict):
            continue
        raw_id = concept.get("id") or ""
        bare = raw_id.rsplit("/", 1)[-1] if "/" in raw_id else raw_id
        if bare == field_concept_id:
            score = concept.get("score")
            return float(score) if score is not None else 0.0
    return None


def _passes_score_threshold(
    work: dict[str, Any], field_concept_id: str,
) -> bool:
    score = _field_concept_score(work, field_concept_id)
    return score is not None and score >= _SCORE_THRESHOLD


def _passes_junk_year_filter(
    work: dict[str, Any], patterns: tuple[re.Pattern[str], ...],
) -> bool:
    """Pre-1990 papers with post-2000 token in title/abstract → excluded.

    Uses word-boundary regex to avoid substring false positives (e.g.,
    `gan` matching `organism`). Patterns are case-insensitive.
    """
    year = work.get("publication_year")
    if year is None or year >= _JUNK_YEAR_THRESHOLD:
        return True
    title = work.get("title") or ""
    inv = work.get("abstract_inverted_index") or {}
    abstract_tokens = " ".join(inv.keys()) if isinstance(inv, dict) else ""
    text = f"{title} {abstract_tokens}"
    for pattern in patterns:
        if pattern.search(text):
            return False
    return True


def _abstract_token_count(work: dict[str, Any]) -> int:
    inv = work.get("abstract_inverted_index") or {}
    if not isinstance(inv, dict):
        return 0
    return sum(len(positions) for positions in inv.values())


def _passes_empty_abstract_filter(work: dict[str, Any]) -> bool:
    return _abstract_token_count(work) >= _EMPTY_ABSTRACT_MIN_TOKENS


# ---------- filter pipelines ----------


def _apply_pipeline(
    raw: list[dict[str, Any]],
    *,
    junk_year_patterns: tuple[re.Pattern[str], ...],
    with_empty_abstract_filter: bool,
) -> dict[str, Any]:
    """Returns dict with cumulative-survival counts + final kept list."""
    after_score = [
        w for w in raw if _passes_score_threshold(w, _FIELD_CONCEPT_ID)
    ]
    after_abstract = [w for w in after_score if openalex.has_abstract(w)]
    after_junk_year = [
        w for w in after_abstract
        if _passes_junk_year_filter(w, junk_year_patterns)
    ]
    if with_empty_abstract_filter:
        kept = [w for w in after_junk_year if _passes_empty_abstract_filter(w)]
    else:
        kept = after_junk_year
    return {
        "n_raw": len(raw),
        "n_after_score": len(after_score),
        "n_after_abstract": len(after_abstract),
        "n_after_junk_year": len(after_junk_year),
        "n_kept": len(kept),
        "kept": kept,
    }


def _ids_set(works: list[dict[str, Any]]) -> set[str]:
    return {str(w.get("id", "")) for w in works}


# ---------- pulls ----------


def _pull_one(filters: dict[str, str], seed: int, label: str) -> list[dict[str, Any]]:
    try:
        return openalex.fetch_works(
            filters=filters,
            sample_size=_SAMPLE_PER_CELL,
            seed=seed,
            select=_SELECT,
        )
    except RuntimeError as err:
        print(f"  WARN: {label} seed={seed}: {err}")
        return []


def _pull_cs_1975_baseline() -> list[dict[str, Any]]:
    """200 papers, seed=42 — matches Check 5a single-cell pull."""
    print(f"Pulling cs 1975 (seed={_CS_1975_SEED}, sample=200) for Check 5a parity...")
    raw = _pull_one(
        {"concepts.id": _FIELD_CONCEPT_ID, "publication_year": "1975"},
        seed=_CS_1975_SEED,
        label="cs/1975",
    )
    print(f"  pulled {len(raw)} raw papers")
    return raw


def _pull_year_dry_run(year: int) -> list[dict[str, Any]]:
    """5K raw papers via 25 seeds × 200; deduped by id."""
    print(f"Pulling cs {year} (25 seeds × 200) for dry-run end-to-end exercise...")
    seen_ids: set[str] = set()
    accumulated: list[dict[str, Any]] = []
    for seed in tqdm(_DRY_RUN_SEEDS, desc=f"cs/{year}"):
        raw = _pull_one(
            {"concepts.id": _FIELD_CONCEPT_ID, "publication_year": str(year)},
            seed=seed,
            label=f"cs/{year}",
        )
        for w in raw:
            wid = str(w.get("id", ""))
            if wid and wid not in seen_ids:
                seen_ids.add(wid)
                accumulated.append(w)
        time.sleep(0.3)
    print(f"  total raw (deduped): {len(accumulated)}")
    return accumulated


# ---------- analyses ----------


def _over_filter_rate_cs1975(raw_1975: list[dict[str, Any]]) -> dict[str, Any]:
    """Apply pilot vs production filter to cs 1975; compute over-filter delta.

    The "Check 5a baseline" is the post-pilot-filter set: score≥0.3 +
    has_abstract + 5-token junk-year filter (no empty-abstract filter).
    The "production" set adds: 25-token junk-year + 15-token min abstract.

    Over-filter rate = (baseline_kept - production_kept) / baseline_kept.
    """
    baseline = _apply_pipeline(
        raw_1975,
        junk_year_patterns=_PILOT_PATTERNS,
        with_empty_abstract_filter=False,
    )
    production = _apply_pipeline(
        raw_1975,
        junk_year_patterns=_PRODUCTION_PATTERNS,
        with_empty_abstract_filter=True,
    )
    # Decompose production-only exclusions
    production_no_empty = _apply_pipeline(
        raw_1975,
        junk_year_patterns=_PRODUCTION_PATTERNS,
        with_empty_abstract_filter=False,
    )

    baseline_kept_n = baseline["n_kept"]
    prod_kept_n = production["n_kept"]
    over_filter_count = baseline_kept_n - prod_kept_n
    over_filter_rate = (
        over_filter_count / baseline_kept_n if baseline_kept_n > 0 else 0.0
    )

    # Decompose: junk-year delta vs empty-abstract delta
    junk_year_delta = baseline_kept_n - production_no_empty["n_kept"]
    empty_abstract_delta = production_no_empty["n_kept"] - prod_kept_n

    # Identify which papers production drops that pilot kept
    base_ids = _ids_set(baseline["kept"])
    prod_ids = _ids_set(production["kept"])
    dropped_ids = base_ids - prod_ids
    dropped_papers = [w for w in baseline["kept"] if str(w.get("id", "")) in dropped_ids]

    return {
        "n_raw": baseline["n_raw"],
        "baseline_kept": baseline_kept_n,
        "production_kept": prod_kept_n,
        "over_filter_count": over_filter_count,
        "over_filter_rate": over_filter_rate,
        "junk_year_delta": junk_year_delta,
        "empty_abstract_delta": empty_abstract_delta,
        "dropped_papers": dropped_papers,
        "baseline_breakdown": {
            k: v for k, v in baseline.items() if k != "kept"
        },
        "production_breakdown": {
            k: v for k, v in production.items() if k != "kept"
        },
    }


def _retention_summary(raw: list[dict[str, Any]], label: str) -> dict[str, Any]:
    result = _apply_pipeline(
        raw,
        junk_year_patterns=_PRODUCTION_PATTERNS,
        with_empty_abstract_filter=True,
    )
    n_raw = result["n_raw"]
    return {
        "label": label,
        "n_raw": n_raw,
        "n_after_score": result["n_after_score"],
        "n_after_abstract": result["n_after_abstract"],
        "n_after_junk_year": result["n_after_junk_year"],
        "n_kept": result["n_kept"],
        "retention_score": result["n_after_score"] / n_raw if n_raw else 0.0,
        "retention_abstract": result["n_after_abstract"] / n_raw if n_raw else 0.0,
        "retention_junk_year": result["n_after_junk_year"] / n_raw if n_raw else 0.0,
        "retention_full": result["n_kept"] / n_raw if n_raw else 0.0,
        "kept": result["kept"],
    }


def _hand_audit_sample(
    raw: list[dict[str, Any]], n: int, seed: int,
) -> list[dict[str, Any]]:
    """Sample n papers from raw (post-filter kept) for hand audit."""
    rng = random.Random(seed)
    if len(raw) <= n:
        return list(raw)
    return rng.sample(raw, n)


def _audit_signals(work: dict[str, Any]) -> dict[str, Any]:
    """Return per-row diagnostic info for hand audit."""
    inv = work.get("abstract_inverted_index") or {}
    abstract_tokens_str = (
        " ".join(inv.keys()).lower() if isinstance(inv, dict) else ""
    )
    title = (work.get("title") or "").lower()
    text = f"{title} {abstract_tokens_str}"
    # Suspicious post-2000 markers NOT in the production token list
    suspicious_extras = [
        "deep learning", "convolutional neural network",
        "github", "kaggle", "stack overflow", "tensorflow", "pytorch",
        "machine learning model", "neural network architecture",
        "5g", "covid", "pandemic", "iphone", "android",
    ]
    found = [tok for tok in suspicious_extras if tok in text]
    return {
        "id": work.get("id"),
        "title": work.get("title"),
        "publication_year": work.get("publication_year"),
        "abstract_n_tokens": _abstract_token_count(work),
        "suspicious_extras_found": found,
    }


# ---------- artifact writing ----------


def _write_md_artifact(
    snapshot: str,
    over_filter: dict[str, Any],
    retention_2024: dict[str, Any],
    retention_1980: dict[str, Any],
    hand_audit_rows: list[dict[str, Any]],
    out_path: Path,
) -> None:
    snapshot_str = snapshot
    of = over_filter
    r24 = retention_2024
    r80 = retention_1980

    of_pct = of["over_filter_rate"] * 100
    of_status = "✅ PASS" if of_pct < 2.0 else "❌ FAIL"
    bb = of["baseline_breakdown"]
    pb = of["production_breakdown"]

    # Hand audit summary
    flagged = [r for r in hand_audit_rows if r["suspicious_extras_found"]]
    audit_status = "✅ PASS" if not flagged else "⚠ INVESTIGATE"

    dropped_lines = []
    for w in of["dropped_papers"][:10]:
        title = (w.get("title") or "")[:80]
        dropped_lines.append(
            f"- {w.get('id', '?')} ({w.get('publication_year')}) — {title}"
        )
    dropped_block = "\n".join(dropped_lines) if dropped_lines else "(none dropped)"

    audit_lines = []
    for r in hand_audit_rows[:50]:
        flag_str = ",".join(r["suspicious_extras_found"]) or "—"
        title = (r["title"] or "")[:70]
        audit_lines.append(
            f"| {r['id']} | {r['publication_year']} | "
            f"{r['abstract_n_tokens']} | {flag_str} | {title} |"
        )
    audit_table = "\n".join(audit_lines)

    body = f"""# Phase 0.2 Wave 1C — production pull-spec dry run

**Run date:** {datetime.now(timezone.utc).date().isoformat()}
**Snapshot recorded:** {snapshot_str}

## Headline

**Over-filter rate (cs 1975, vs Check 5a baseline):
{of['over_filter_count']}/{of['baseline_kept']} = {of_pct:.2f}% — {of_status}**

The locked §0 production filter (25-token junk-year list +
15-token empty-abstract minimum, post-consolidation) was applied
to the cs 1975 cell that Check 5a's pilot filter (5-token list,
no empty-abstract filter) processed. The acceptance gate is
<2% additional exclusion of papers Check 5a kept.

**Hand-audit ({_HAND_AUDIT_N} papers from cs 1980 kept set):
{len(flagged)}/{len(hand_audit_rows)} flagged for suspicious
post-2000 markers — {audit_status}**

## Pipeline definition (locked §0, post-consolidation)

1. score ≥ 0.3 on field concept (loose threshold per §3 N1)
2. has_abstract (non-empty inverted index)
3. Junk-year-token filter: pre-1990 papers excluded if title/abstract
   contains any of {len(_PRODUCTION_JUNK_YEAR_TOKENS)} tokens
   (post-2000-coined only; per consolidation §A)
4. Empty-abstract filter: ≥{_EMPTY_ABSTRACT_MIN_TOKENS} tokens after
   inverted-index reconstruction (per consolidation §B; relaxed
   from initial 30)

## Over-filter rate analysis (cs 1975, n_raw={of['n_raw']})

| Step | Pilot (Check 5a) | Production (post-consolidation) |
|---|---:|---:|
| Raw | {bb['n_raw']} | {pb['n_raw']} |
| After score≥0.3 | {bb['n_after_score']} | {pb['n_after_score']} |
| After has_abstract | {bb['n_after_abstract']} | {pb['n_after_abstract']} |
| After junk-year | {bb['n_after_junk_year']} | {pb['n_after_junk_year']} |
| After empty-abstract | (n/a) | {pb['n_kept']} |
| **Final kept** | **{of['baseline_kept']}** | **{of['production_kept']}** |

**Over-filter components:**
- Junk-year list expansion (5 → {len(_PRODUCTION_JUNK_YEAR_TOKENS)} tokens):
  excludes {of['junk_year_delta']} additional papers.
- Empty-abstract filter (new, ≥15 tokens): excludes
  {of['empty_abstract_delta']} additional papers.
- Total over-filter: {of['over_filter_count']} papers
  ({of_pct:.2f}% of pilot kept set).

**Acceptance gate:** {of_pct:.2f}% < 2.0% → {of_status}

### Sample of papers production filter excludes that pilot kept
{dropped_block}

## End-to-end exercise (cs 2024 + cs 1980, n_seeds=25 each)

### cs 2024 retention (modern era)

| Step | n | retention vs raw |
|---|---:|---:|
| Raw (deduped) | {r24['n_raw']} | 1.000 |
| After score≥0.3 | {r24['n_after_score']} | {r24['retention_score']:.1%} |
| After has_abstract | {r24['n_after_abstract']} | {r24['retention_abstract']:.1%} |
| After junk-year | {r24['n_after_junk_year']} | {r24['retention_junk_year']:.1%} |
| **After empty-abstract** | **{r24['n_kept']}** | **{r24['retention_full']:.1%}** |

cs 2024 junk-year filter is a no-op (year ≥ 1990; filter doesn't
fire). Empty-abstract filter is the only post-pilot stage active.

### cs 1980 retention (pre-1990 era; junk-year filter active)

| Step | n | retention vs raw |
|---|---:|---:|
| Raw (deduped) | {r80['n_raw']} | 1.000 |
| After score≥0.3 | {r80['n_after_score']} | {r80['retention_score']:.1%} |
| After has_abstract | {r80['n_after_abstract']} | {r80['retention_abstract']:.1%} |
| After junk-year | {r80['n_after_junk_year']} | {r80['retention_junk_year']:.1%} |
| **After empty-abstract** | **{r80['n_kept']}** | **{r80['retention_full']:.1%}** |

cs 1980 retention rate exercises the full pipeline. Plan §0
expectation: ~30-40% retention in pre-1990 cells (low coverage
of has_abstract on pre-1990 OpenAlex records is the dominant
loss; junk-year filter contributes <5%).

## Hand audit ({len(hand_audit_rows)} rows from cs 1980 kept set)

Each row sampled from the post-filter cs 1980 kept set. Suspicious
markers searched for: deep learning, convolutional neural network,
github, kaggle, stack overflow, tensorflow, pytorch, machine
learning model, neural network architecture, 5g, covid, pandemic,
iphone, android (not in production token list; would indicate
post-2000 content slipping past).

| OpenAlex ID | Year | Tokens | Suspicious markers | Title (truncated) |
|---|---:|---:|---|---|
{audit_table}

**Flagged rows:** {len(flagged)}/{len(hand_audit_rows)}.
Acceptance: 0 flagged → ✅ PASS; ≥1 flagged → ⚠ INVESTIGATE
(token list expansion may be needed).

## Acceptance check (Wave 1C)

Per `phase-0.2-execution.md` Wave 1C acceptance:

- Over-filter rate <2% vs Check 5a baseline on cs 1975:
  **{of_pct:.2f}% — {of_status}**
- Zero post-2000-content false negatives in 50-row hand-audit:
  **{len(flagged)}/{len(hand_audit_rows)} flagged — {audit_status}**

## Decision input

If both gates pass: locked §0 production filter is ready for Stage 1
bulk pull. No further token-list iteration needed.

If over-filter gate fails (>2%): investigate which production tokens
are causing false-positive exclusions on legitimate cs 1975 papers;
possibly remove those tokens.

If hand-audit gate fails (≥1 flagged): expand the production token
list with the markers that surfaced; re-run.

## Artifacts

- `experiments/phase-0.2/pull-spec-dry-run.md` — this artifact.
- `experiments/phase-0.2/pull-spec-dry-run-summary.json` — machine-
  readable summary.
- `experiments/phase-0.2/pull-spec-dry-run-cs1980-handaudit.csv` —
  full hand-audit table.
- `experiments/phase-0.2/pull_spec_dry_run.py` — this script.
"""
    out_path.write_text(body)


def main() -> None:
    print("Phase 0.2 Wave 1C — production pull-spec dry run")
    print()

    snapshot = datetime.now(timezone.utc).isoformat(timespec="seconds")

    # 1. cs 1975 baseline pull (Check 5a parity)
    raw_1975 = _pull_cs_1975_baseline()
    if not raw_1975:
        print("ERROR: cs 1975 pull empty; aborting.")
        sys.exit(1)
    print()

    # 2. cs 2024 dry-run pull
    raw_2024 = _pull_year_dry_run(2024)
    print()

    # 3. cs 1980 dry-run pull
    raw_1980 = _pull_year_dry_run(1980)
    print()

    # 4. Over-filter rate analysis on cs 1975
    print("Computing over-filter rate (cs 1975)...")
    of = _over_filter_rate_cs1975(raw_1975)
    of_pct = of["over_filter_rate"] * 100
    print(
        f"  pilot kept {of['baseline_kept']}; production kept "
        f"{of['production_kept']}; over-filter {of['over_filter_count']} "
        f"({of_pct:.2f}%)"
    )
    print()

    # 5. Retention summaries
    print("Computing retention summaries...")
    r24 = _retention_summary(raw_2024, "cs/2024")
    print(
        f"  cs 2024: {r24['n_raw']} raw → {r24['n_kept']} kept "
        f"({r24['retention_full']:.1%})"
    )
    r80 = _retention_summary(raw_1980, "cs/1980")
    print(
        f"  cs 1980: {r80['n_raw']} raw → {r80['n_kept']} kept "
        f"({r80['retention_full']:.1%})"
    )
    print()

    # 6. Hand audit (50 rows from cs 1980 kept set)
    print(f"Hand audit: sampling {_HAND_AUDIT_N} rows from cs 1980 kept...")
    audit_sample = _hand_audit_sample(r80["kept"], _HAND_AUDIT_N, _HAND_AUDIT_SEED)
    audit_rows = [_audit_signals(w) for w in audit_sample]
    flagged = [r for r in audit_rows if r["suspicious_extras_found"]]
    print(f"  flagged: {len(flagged)}/{len(audit_rows)}")
    print()

    # 7. Write artifacts
    print("Writing artifacts...")
    md_path = _OUT_DIR / "pull-spec-dry-run.md"
    _write_md_artifact(snapshot, of, r24, r80, audit_rows, md_path)
    print(f"  wrote {md_path}")

    summary_json = {
        "snapshot": snapshot,
        "over_filter": {
            "n_raw": of["n_raw"],
            "baseline_kept": of["baseline_kept"],
            "production_kept": of["production_kept"],
            "over_filter_count": of["over_filter_count"],
            "over_filter_rate": of["over_filter_rate"],
            "junk_year_delta": of["junk_year_delta"],
            "empty_abstract_delta": of["empty_abstract_delta"],
            "baseline_breakdown": of["baseline_breakdown"],
            "production_breakdown": of["production_breakdown"],
        },
        "retention_2024": {k: v for k, v in r24.items() if k != "kept"},
        "retention_1980": {k: v for k, v in r80.items() if k != "kept"},
        "hand_audit": {
            "n_sampled": len(audit_rows),
            "n_flagged": len(flagged),
            "flagged_rows": flagged,
        },
        "production_junk_year_tokens": list(_PRODUCTION_JUNK_YEAR_TOKENS),
        "empty_abstract_min_tokens": _EMPTY_ABSTRACT_MIN_TOKENS,
        "score_threshold": _SCORE_THRESHOLD,
    }
    summary_path = _OUT_DIR / "pull-spec-dry-run-summary.json"
    summary_path.write_text(json.dumps(summary_json, indent=2, default=str))
    print(f"  wrote {summary_path}")

    audit_df = pd.DataFrame(audit_rows)
    audit_csv = _OUT_DIR / "pull-spec-dry-run-cs1980-handaudit.csv"
    audit_df.to_csv(audit_csv, index=False)
    print(f"  wrote {audit_csv}")
    print()

    # Final status
    of_status = "PASS" if of_pct < 2.0 else "FAIL"
    audit_status = "PASS" if not flagged else "INVESTIGATE"
    print(f"Wave 1C gates: over-filter={of_status} ({of_pct:.2f}%); "
          f"hand-audit={audit_status} ({len(flagged)}/{len(audit_rows)} flagged)")
    print()
    print("Wave 1C complete.")


if __name__ == "__main__":
    main()
    sys.exit(0)
