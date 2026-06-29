"""§0 analytical-population filter (LOCKED per Phase 0.2 + Phase 1.1;
type allow-list amended per Phase 1.2 H2 audit).

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
5. **Type allow-list.** Only ``article``, ``preprint``, ``review``,
   ``book-chapter``, ``dissertation``, ``book``, ``letter``,
   ``editorial``, ``report`` types pass. Phase 1.2 H2 audit
   amendment: the un-type-filtered population was 39.9%
   ``type='dataset'`` (largely GBIF "Occurrence Download" auto-
   generated DOIs) plus several smaller non-research types
   (paratext, libguides, peer-review, erratum, retraction,
   reference-entry, supplementary-materials, grant). Excluding
   these via an allow-list rather than a deny-list is the
   defensible methodology choice — additions to OpenAlex's type
   vocabulary default to "out" until inspected.

The 25-token production junk-year list (post-2000-coined only)
is locked per Phase 0.2 consolidation §A. Pre-1990 chip names
(tms320, z80, etc.) and pre-2000 lineage terms (cnn, rnn, https)
were REMOVED to avoid systematic false-positive exclusion of
legitimate early-era papers.

See ``docs/phases/phase-0.2-plan.md`` §0 for the original
locked spec; ``docs/phases/phase-1.2-retro.md`` (TBD) for the
type allow-list amendment.
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

#: Allowed OpenAlex work types (Phase 1.2 amendment). Anything not in
#: this set is excluded — including ``dataset`` (GBIF / Zenodo data
#: DOIs), ``paratext`` (frontmatter, indices), ``libguides`` (library
#: research guides), ``peer-review`` (review reports), ``erratum``,
#: ``retraction``, ``reference-entry``, ``supplementary-materials``,
#: ``grant``, ``software``, ``standard``, and OpenAlex's catch-all
#: ``other``. The allow-list bias is deliberate: new types added to
#: OpenAlex's vocabulary default to "out" until human-inspected.
ALLOWED_WORK_TYPES: frozenset[str] = frozenset({
    "article",
    "preprint",
    "review",
    "book-chapter",
    "dissertation",
    "book",
    "letter",
    "editorial",
    "report",
})

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


def passes_type_filter(
    work: dict[str, Any],
    allowed: frozenset[str] = ALLOWED_WORK_TYPES,
) -> bool:
    """True iff work's ``type`` is in the research-paper allow-list."""
    work_type = work.get("type")
    return isinstance(work_type, str) and work_type in allowed


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


# ---------- §0 v3 amendments (Phase 1.2 H2 audit retro) ----------

#: Stronger concept-score threshold for v3 (was 0.30 in v2). The
#: H2 audit found ~10-15% of v2 sample had a CS/physics concept at
#: 0.30-0.39 but was actually in a different field — concept-tagger
#: noise firing on incidental keywords. Raising to 0.40 eliminates
#: most of this with a mild temporal bias toward better-indexed
#: (modern) papers.
SCORE_THRESHOLD_V3: float = 0.40

#: Stronger abstract-token min for v3 (was 15). Catches publication-
#: status placeholders ("This is the author's version of..."),
#: bibliography stubs, and "Abstract not available" boilerplate that
#: cleared the 15-token threshold. Mild pre-1990 bias (older
#: abstracts are shorter on average); pre-1990 is already its own
#: stratum so the effect is tractable.
EMPTY_ABSTRACT_MIN_TOKENS_V3: int = 50

#: Abstract-prefix blacklist (v3). Captures publisher chrome that
#: OpenAlex put in the abstract field instead of the paper's actual
#: abstract. Audit found 12-13 of 100 sampled papers (~28% of FLAGs)
#: matched these patterns. Sub-patterns:
#:  - ``ADVERTISEMENT RETURN TO ISSUE`` / ``RETURN TO ISSUE`` →
#:    ACS Publications template (J. Am. Chem. Soc., Anal. Chem.,
#:    Chem. Eng. News).
#:  - ``Views Icon Views`` → Wiley / OUP / Portland Press / AIP
#:    template (Biochem J, Current History, J. Chem. Phys.).
#:  - ``Article Metrics`` → metric-stub-only abstracts.
#:  - ``This is the author's version`` → publication-status
#:    placeholders where the abstract field was never populated
#:    (the underlying paper may be real research).
ABSTRACT_PREFIX_BLACKLIST_PATTERN: re.Pattern[str] = re.compile(
    r"^("
    r"(?:ADVERTISEMENT\s+)?RETURN TO ISSUE"
    r"|Views Icon Views"
    r"|Article Metrics"
    r"|This is the author'?s version"
    r")",
    re.IGNORECASE,
)

#: Title-prefix blacklist (v3). Captures non-paper artifacts where the
#: OpenAlex ``type`` field is ``article`` but the work is front-matter,
#: a news brief, or a procedural document.
#:  - ``NEW PRODUCTS`` → C&EN-style product announcements.
#:  - ``Contributors`` (alone, with terminal punctuation, or with year/
#:    issue suffix) → magazine contributor bio sections. NOT a real
#:    paper title like "Contributors to Variance..." (those have a
#:    preposition next; we require Contributors to terminate, be
#:    followed by `:` `,` `;` `.`, or be followed by a digit/year).
#:  - ``Annex \d+`` → CoARA-style working-group annex documents.
#:  - ``Key Messages`` → OECD-style policy briefs.
#:  - ``Editorial Board`` → editorial-board listings.
TITLE_PREFIX_BLACKLIST_PATTERN: re.Pattern[str] = re.compile(
    r"^("
    r"NEW PRODUCTS\b"
    r"|Contributors(?:\s*$|\s*[:,;.]|\s+\d)"
    r"|Annex\s+\d+"
    r"|Key Messages\b"
    r"|Editorial Board\b"
    r")",
    re.IGNORECASE,
)

#: Number of leading word-positions reconstructed when checking the
#: abstract prefix. 20 is comfortably more than the longest blacklist
#: pattern (~5 words).
ABSTRACT_PREFIX_LOOKAHEAD: int = 20


def _reconstruct_abstract_prefix(
    inv: Any, n_positions: int = ABSTRACT_PREFIX_LOOKAHEAD,
) -> str:
    """Reconstruct the first ``n_positions`` words of the abstract.

    Walks the inverted index, finds which word lies at each position
    0..n_positions-1, joins them with single spaces. Gaps (positions
    with no word) are skipped silently — OpenAlex sometimes has them.
    """
    if not isinstance(inv, dict) or not inv:
        return ""
    pos_to_word: dict[int, str] = {}
    for word, positions in inv.items():
        if not isinstance(positions, list):
            continue
        for p in positions:
            if isinstance(p, int) and 0 <= p < n_positions:
                pos_to_word[p] = word
    if not pos_to_word:
        return ""
    max_pos = max(pos_to_word.keys())
    return " ".join(pos_to_word.get(i, "") for i in range(max_pos + 1)).strip()


def passes_abstract_prefix_filter(
    work: dict[str, Any],
    pattern: re.Pattern[str] = ABSTRACT_PREFIX_BLACKLIST_PATTERN,
) -> bool:
    """True iff the abstract prefix does NOT match the blacklist."""
    inv = work.get("abstract_inverted_index")
    prefix = _reconstruct_abstract_prefix(inv)
    if not prefix:
        return True  # no prefix to test — let other filters handle
    return pattern.match(prefix) is None


def passes_title_prefix_filter(
    work: dict[str, Any],
    pattern: re.Pattern[str] = TITLE_PREFIX_BLACKLIST_PATTERN,
) -> bool:
    """True iff the title does NOT start with a blacklisted prefix."""
    title = work.get("title")
    if not isinstance(title, str):
        return True  # missing / non-string title → let other filters handle
    return pattern.match(title) is None


# ---------- pipeline ----------


def apply_section0_filter(
    works: Iterable[dict[str, Any]],
) -> Iterator[dict[str, Any]]:
    """Yield works that pass all five v2 §0 filter stages.

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
        if not passes_type_filter(w):
            continue
        yield w


def apply_section0_filter_v3(
    works: Iterable[dict[str, Any]],
) -> Iterator[dict[str, Any]]:
    """Yield works that pass all §0 v3 filter stages.

    v3 = v2 with two thresholds raised + two prefix filters added:
      - Concept-score threshold 0.30 → 0.40
      - Abstract token min 15 → 50
      - Abstract-prefix blacklist (publisher chrome)
      - Title-prefix blacklist (non-paper artifacts)
      - Junk-year regex and type allow-list unchanged

    v3 is a strict superset of v2 filters; anything v3 yields, v2
    would also yield. The reverse is not true.
    """
    for w in works:
        if not passes_score_any_field(w, threshold=SCORE_THRESHOLD_V3):
            continue
        if not has_abstract(w):
            continue
        if not passes_junk_year_filter(w):
            continue
        if not passes_empty_abstract_filter(
            w, min_tokens=EMPTY_ABSTRACT_MIN_TOKENS_V3,
        ):
            continue
        if not passes_type_filter(w):
            continue
        if not passes_abstract_prefix_filter(w):
            continue
        if not passes_title_prefix_filter(w):
            continue
        yield w
