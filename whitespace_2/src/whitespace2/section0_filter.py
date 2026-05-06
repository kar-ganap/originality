"""§0 analytical-population filter (LOCKED per Phase 0.2 + Phase 1.1).

The filter pipeline produces the §0 population P from raw OpenAlex
Work records. Lifted into a clean module for Phase 1.2's bulk-dump
processing; previously inlined across Phase 0.2 + Phase 1.1 scripts.

Filter sequence (each must pass):

1. **Score threshold.** Client-side filter: ≥0.30 on cs
   (``C41008148``) OR physics (``C121332964``) concept. Required
   because OpenAlex's API ``concepts.id`` filter ignores score per
   Phase 0.1 Check 2 correction.
2. **Has abstract.** Non-empty ``abstract_inverted_index`` dict.
3. **Junk-year-token filter.** Pre-1990 papers with post-2000-coined
   tokens in title or abstract get excluded. Word-boundary regex
   per Phase 0.2 Wave 1C lock (substring matching caused
   ``gan`` to match ``organism``; fix is ``\\bTOKEN\\b``).
4. **Empty-abstract filter.** ≥15 tokens after inverted-index
   reconstruction. Catches "Abstract not available" boilerplate
   (~3-7 tokens) without over-filtering legitimate short pre-1990
   conference abstracts. Threshold per Phase 0.2 consolidation §B.

The 25-token production junk-year list (post-2000-coined only)
is locked per Phase 0.2 consolidation §A. Pre-1990 chip names
(tms320, z80, etc.) and pre-2000 lineage terms (cnn, rnn, https)
were REMOVED to avoid systematic false-positive exclusion of
legitimate early-era papers.

See ``docs/phases/phase-0.2-plan.md`` §0 for the locked spec.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator
from typing import Any

# ---------- §0 locked parameters ----------

#: cs (Computer Science), physics (Physics) concept IDs
FIELD_CONCEPT_IDS: tuple[str, ...] = ("C41008148", "C121332964")

#: ≥0.30 score threshold on field concept (loose; per N1 §3)
SCORE_THRESHOLD: float = 0.30

#: Pre-1990 papers are subject to the junk-year-token filter
JUNK_YEAR_THRESHOLD: int = 1990

#: ≥15 tokens minimum (Phase 0.2 consolidation §B)
EMPTY_ABSTRACT_MIN_TOKENS: int = 15

#: Production junk-year tokens. Post-2000-coined only (Phase 0.2
#: consolidation §A). Word-boundary matched (Wave 1C fix).
PRODUCTION_JUNK_YEAR_TOKENS: tuple[str, ...] = (
    # Original pilot 5
    "r-cnn", "iot", "blockchain", "transformer", "smartphone",
    # Post-2000 ML / deep learning (model-specific)
    "lstm", "gan", "bert", "gpt", "chatgpt",
    "attention is all you need", "word2vec", "glove", "risc-v",
    # Post-2000 protocols / formats
    "tls 1", "webrtc", "mqtt", "openid connect",
    # Post-2000 devices / contexts
    "wearable", "vr headset", "cloud computing", "big data",
    "internet of things", "digital twin", "arm cortex",
)

#: Compiled word-boundary regex patterns. Re-using a single tuple
#: avoids re-compilation per record (~$10-30 saved on the 492M-record
#: bulk-dump pass).
PRODUCTION_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(r"\b" + re.escape(tok) + r"\b", re.IGNORECASE)
    for tok in PRODUCTION_JUNK_YEAR_TOKENS
)


# ---------- per-rule predicates ----------


def _field_concept_score(
    work: dict[str, Any], concept_id: str,
) -> float | None:
    """Return the score for a specific concept ID, or None if absent."""
    concepts = work.get("concepts") or []
    if not isinstance(concepts, list):
        return None
    for c in concepts:
        if not isinstance(c, dict):
            continue
        raw_id = c.get("id") or ""
        bare = raw_id.rsplit("/", 1)[-1] if "/" in raw_id else raw_id
        if bare == concept_id:
            score = c.get("score")
            return float(score) if score is not None else 0.0
    return None


def passes_score_any_field(
    work: dict[str, Any],
    concept_ids: tuple[str, ...] = FIELD_CONCEPT_IDS,
    threshold: float = SCORE_THRESHOLD,
) -> bool:
    """True iff work has score ≥threshold on any of the field concepts."""
    for cid in concept_ids:
        score = _field_concept_score(work, cid)
        if score is not None and score >= threshold:
            return True
    return False


def has_abstract(work: dict[str, Any]) -> bool:
    """True iff work has a non-empty abstract_inverted_index dict."""
    inv = work.get("abstract_inverted_index")
    return isinstance(inv, dict) and len(inv) > 0


def abstract_token_count(work: dict[str, Any]) -> int:
    """Total token count from inverted index (sum of positions per word)."""
    inv = work.get("abstract_inverted_index") or {}
    if not isinstance(inv, dict):
        return 0
    return sum(len(positions) for positions in inv.values())


def passes_empty_abstract_filter(
    work: dict[str, Any], min_tokens: int = EMPTY_ABSTRACT_MIN_TOKENS,
) -> bool:
    """True iff work has ≥min_tokens in its abstract."""
    return abstract_token_count(work) >= min_tokens


def passes_junk_year_filter(
    work: dict[str, Any],
    patterns: tuple[re.Pattern[str], ...] = PRODUCTION_PATTERNS,
    threshold: int = JUNK_YEAR_THRESHOLD,
) -> bool:
    """True iff (year ≥ threshold) OR (no junk-year tokens in title/abstract).

    Pre-threshold (i.e., pre-1990) papers with post-2000-coined
    tokens in title or abstract keys are excluded. Word-boundary
    regex (Wave 1C lock) prevents substring false positives
    (e.g., ``gan`` matching ``organism``).
    """
    year = work.get("publication_year")
    if year is None or year >= threshold:
        return True
    title = work.get("title") or ""
    inv = work.get("abstract_inverted_index") or {}
    if isinstance(inv, dict):
        abs_tokens = " ".join(inv.keys())
    else:
        abs_tokens = ""
    text = f"{title} {abs_tokens}"
    for pat in patterns:
        if pat.search(text):
            return False
    return True


# ---------- pipeline ----------


def apply_section0_filter(
    works: Iterable[dict[str, Any]],
) -> Iterator[dict[str, Any]]:
    """Yield works that pass all four §0 filter stages.

    Lazy iterator: critical at production scale (492M-record bulk
    dump streams through; materializing the full corpus would OOM).

    Yields work dicts in input order (filter is per-record; no
    cross-record dependencies).
    """
    for w in works:
        if not passes_score_any_field(w):
            continue
        if not has_abstract(w):
            continue
        if not passes_junk_year_filter(w):
            continue
        if not passes_empty_abstract_filter(w):
            continue
        yield w
