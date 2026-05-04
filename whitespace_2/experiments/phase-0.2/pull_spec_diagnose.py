"""Wave 1C diagnostic — identify which production tokens fired on dropped papers.

The dry run flagged 4 papers from cs 1975 as production-excluded that
pilot Check 5a kept. To decide whether the production filter is too
aggressive (false positives) or correctly excluding non-CS noise
(true positives), we need to see which tokens fired on each.

Re-pulls cs 1975 (seed=42, sample=200) and prints, for each
production-dropped paper:
- which junk-year tokens fired (if any)
- abstract token count (for empty-abstract diagnostic)
- score on CS concept (sanity)
- full title + abstract reconstruction
"""

from __future__ import annotations

import sys
from typing import Any

from whitespace2 import openalex

_FIELD_CONCEPT_ID = "C41008148"
_SCORE_THRESHOLD = 0.3
_EMPTY_ABSTRACT_MIN_TOKENS = 15
_JUNK_YEAR_THRESHOLD = 1990

_PRODUCTION_JUNK_YEAR_TOKENS: tuple[str, ...] = (
    "r-cnn", "iot", "blockchain", "transformer", "smartphone",
    "lstm", "gan", "bert", "gpt", "chatgpt", "attention is all you need",
    "word2vec", "glove", "risc-v",
    "tls 1", "webrtc", "mqtt", "openid connect",
    "wearable", "vr headset", "cloud computing", "big data",
    "internet of things", "digital twin", "arm cortex",
)

_PILOT_JUNK_YEAR_TOKENS: tuple[str, ...] = (
    "r-cnn", "iot", "blockchain", "transformer", "smartphone",
)

_SELECT = [
    "id", "title", "publication_year", "type",
    "abstract_inverted_index", "concepts", "primary_location", "ids",
]


def _field_concept_score(work: dict[str, Any]) -> float | None:
    for c in work.get("concepts") or []:
        if not isinstance(c, dict):
            continue
        raw_id = c.get("id") or ""
        bare = raw_id.rsplit("/", 1)[-1] if "/" in raw_id else raw_id
        if bare == _FIELD_CONCEPT_ID:
            score = c.get("score")
            return float(score) if score is not None else 0.0
    return None


def _abstract_text(work: dict[str, Any]) -> str:
    inv = work.get("abstract_inverted_index") or {}
    if not isinstance(inv, dict) or not inv:
        return ""
    max_pos = max(max(positions) for positions in inv.values())
    tokens = [""] * (max_pos + 1)
    for word, positions in inv.items():
        for pos in positions:
            tokens[pos] = word
    return " ".join(t for t in tokens if t)


def _abstract_token_count(work: dict[str, Any]) -> int:
    inv = work.get("abstract_inverted_index") or {}
    if not isinstance(inv, dict):
        return 0
    return sum(len(positions) for positions in inv.values())


def _which_tokens_fire(
    work: dict[str, Any], tokens: tuple[str, ...],
) -> list[str]:
    title = (work.get("title") or "").lower()
    inv = work.get("abstract_inverted_index") or {}
    abs_tokens = " ".join(inv.keys()).lower() if isinstance(inv, dict) else ""
    text = f"{title} {abs_tokens}"
    return [tok for tok in tokens if tok in text]


def main() -> None:
    print("Wave 1C diagnostic — investigating cs 1975 over-filter rate")
    print()

    print("Re-pulling cs 1975 (seed=42, sample=200)...")
    raw = openalex.fetch_works(
        filters={"concepts.id": _FIELD_CONCEPT_ID, "publication_year": "1975"},
        sample_size=200,
        seed=42,
        select=_SELECT,
    )
    print(f"  pulled {len(raw)} raw papers")
    print()

    # Apply pilot pipeline (no empty-abstract filter)
    pilot_kept: list[dict[str, Any]] = []
    for w in raw:
        score = _field_concept_score(w)
        if score is None or score < _SCORE_THRESHOLD:
            continue
        if not openalex.has_abstract(w):
            continue
        year = w.get("publication_year")
        if year is not None and year < _JUNK_YEAR_THRESHOLD:
            tokens_fired = _which_tokens_fire(w, _PILOT_JUNK_YEAR_TOKENS)
            if tokens_fired:
                continue
        pilot_kept.append(w)

    print(f"Pilot pipeline kept: {len(pilot_kept)}")
    print()

    # For each pilot-kept paper, compute production-pipeline status
    print("=" * 80)
    print("Per-paper production pipeline analysis")
    print("=" * 80)
    print()

    n_dropped = 0
    for w in pilot_kept:
        wid = w.get("id", "?")
        title = (w.get("title") or "(no title)")[:90]
        n_tokens = _abstract_token_count(w)
        score = _field_concept_score(w)
        prod_tokens_fired = _which_tokens_fire(w, _PRODUCTION_JUNK_YEAR_TOKENS)
        pilot_tokens_fired = _which_tokens_fire(w, _PILOT_JUNK_YEAR_TOKENS)
        prod_extra = [t for t in prod_tokens_fired if t not in pilot_tokens_fired]
        empty_filter_excludes = n_tokens < _EMPTY_ABSTRACT_MIN_TOKENS

        if prod_extra or empty_filter_excludes:
            n_dropped += 1
            print(f"DROPPED #{n_dropped}: {wid}")
            print(f"  title: {title}")
            print(f"  cs score: {score}")
            print(f"  abstract tokens: {n_tokens} "
                  f"({'<15 → empty-abstract excluded' if empty_filter_excludes else 'OK'})")
            if prod_extra:
                print(f"  junk-year tokens fired (production-only): {prod_extra}")
            if not prod_extra and not empty_filter_excludes:
                print("  WAIT — neither filter should fire; bug in script?")
            abs_text = _abstract_text(w)[:300]
            print(f"  abstract preview: {abs_text!r}")
            print()
        else:
            pass  # production keeps it; uninteresting

    print()
    print(f"Total pilot-kept dropped by production: {n_dropped}/{len(pilot_kept)}")


if __name__ == "__main__":
    main()
    sys.exit(0)
