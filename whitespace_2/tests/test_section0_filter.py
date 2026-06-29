"""Unit tests for the §0 analytical-population filter.

§0 lock per `docs/phases/phase-0.2-plan.md`:

1. score ≥ 0.30 on cs (C41008148) OR physics (C121332964) concept
   (client-side filter; OpenAlex's `concepts.id` API filter
   ignores score per Phase 0.1 Check 2 correction)
2. has_abstract (non-empty abstract_inverted_index)
3. word-boundary regex junk-year token filter on pre-1990 papers
   (Wave 1C lock; production token list of 25 post-2000-coined terms)
4. ≥15 tokens after inverted-index reconstruction (Phase 0.2
   consolidation §B; relaxed from initial 30)

These tests cover regression cases from Phase 0.1 Check 2 (score
threshold), Phase 0.2 Wave 1C (substring vs word-boundary `gan` →
"organism" bug), and Phase 0.2 consolidation §B (15-token threshold
calibration).
"""

from __future__ import annotations

from typing import Any

from whitespace2.section0_filter import (
    ABSTRACT_PREFIX_BLACKLIST_PATTERN,
    ALLOWED_WORK_TYPES,
    EMPTY_ABSTRACT_MIN_TOKENS_V3,
    SCORE_THRESHOLD_V3,
    TITLE_PREFIX_BLACKLIST_PATTERN,
    abstract_token_count,
    apply_section0_filter,
    apply_section0_filter_v3,
    has_abstract,
    passes_abstract_prefix_filter,
    passes_empty_abstract_filter,
    passes_junk_year_filter,
    passes_score_any_field,
    passes_title_prefix_filter,
    passes_type_filter,
)

# ---------- helpers for building test work records ----------


def _make_work(
    *,
    title: str = "Test paper",
    year: int | None = 2020,
    concepts: list[dict[str, Any]] | None = None,
    inv: dict[str, list[int]] | None = None,
    work_type: str = "article",
) -> dict[str, Any]:
    if concepts is None:
        concepts = [
            {"id": "https://openalex.org/C41008148", "score": 0.50},
        ]
    if inv is None:
        # Default: 30-token abstract, no junk-year tokens
        inv = {f"word{i}": [i] for i in range(30)}
    return {
        "id": "https://openalex.org/W123",
        "title": title,
        "publication_year": year,
        "concepts": concepts,
        "abstract_inverted_index": inv,
        "type": work_type,
    }


# ---------- test 1: score boundary ----------


def test_score_threshold_at_boundary() -> None:
    """Score ≥0.30 passes; <0.30 fails. Cross-field OR semantics."""
    # exact boundary: 0.30 passes
    at_boundary = _make_work(
        concepts=[{"id": "https://openalex.org/C41008148", "score": 0.30}],
    )
    assert passes_score_any_field(at_boundary)

    # just below: 0.29 fails
    just_below = _make_work(
        concepts=[{"id": "https://openalex.org/C41008148", "score": 0.29}],
    )
    assert not passes_score_any_field(just_below)

    # cs above + physics below: passes (any-field semantics)
    mixed = _make_work(
        concepts=[
            {"id": "https://openalex.org/C41008148", "score": 0.50},
            {"id": "https://openalex.org/C121332964", "score": 0.10},
        ],
    )
    assert passes_score_any_field(mixed)

    # neither cs nor physics: fails
    biology = _make_work(
        concepts=[{"id": "https://openalex.org/C9999999", "score": 0.99}],
    )
    assert not passes_score_any_field(biology)

    # no concepts at all: fails
    empty = _make_work(concepts=[])
    assert not passes_score_any_field(empty)

    # missing concepts field entirely: fails
    no_concepts = _make_work()
    no_concepts.pop("concepts", None)
    assert not passes_score_any_field(no_concepts)


# ---------- test 2: has_abstract edge cases ----------


def test_has_abstract_empty_dict_returns_false() -> None:
    """Empty dict + None both fail; non-empty dict passes."""
    # non-empty dict
    populated = _make_work(inv={"hello": [0], "world": [1]})
    assert has_abstract(populated)

    # empty dict
    empty_dict = _make_work(inv={})
    assert not has_abstract(empty_dict)

    # None
    none_inv = _make_work()
    none_inv["abstract_inverted_index"] = None
    assert not has_abstract(none_inv)

    # missing key entirely
    missing = _make_work()
    missing.pop("abstract_inverted_index", None)
    assert not has_abstract(missing)


# ---------- test 3: word-boundary regression (Wave 1C) ----------


def test_junk_year_word_boundary_excludes_organism() -> None:
    """Wave 1C regression: 'gan' must NOT match within 'organism'.

    The Phase 0.2 Wave 1C dry-run caught this: the substring-matching
    implementation excluded papers titled 'The Mitochondria of
    Microorganisms' because `gan` matches inside 'organisms'. Fix
    was word-boundary regex; this test prevents regression.
    """
    # Pre-1990 paper with "organism" / "organic" / "organization" should pass
    organism_paper = _make_work(
        year=1975,
        title="The Mitochondria of Microorganisms",
        inv={
            "the": [0, 5], "mitochondria": [1], "of": [2],
            "microorganisms": [3], "organic": [4], "metabolism": [6],
            "is": [7], "a": [8], "key": [9], "process": [10],
            "in": [11], "biology": [12], "and": [13], "energy": [14],
            "production": [15],
        },
    )
    assert passes_junk_year_filter(organism_paper)

    # Pre-1990 paper with literal "GAN" word should be excluded
    gan_paper = _make_work(
        year=1975,
        title="GAN: Generative Adversarial Networks",
        inv={"the": [0], "gan": [1], "is": [2], "a": [3], "model": [4]},
    )
    assert not passes_junk_year_filter(gan_paper)

    # Similar test: `bert` must NOT match within `Albert`
    albert_paper = _make_work(
        year=1980,
        title="Albert Einstein papers archive",
        inv={
            "albert": [0], "einstein": [1], "papers": [2],
            "from": [3], "1905": [4], "to": [5], "1955": [6],
        },
    )
    assert passes_junk_year_filter(albert_paper)

    # `iot` must NOT match within `patriot`
    patriot_paper = _make_work(
        year=1980,
        title="Patriot games and political theory",
        inv={
            "patriot": [0], "games": [1], "political": [2],
            "theory": [3], "of": [4], "national": [5], "identity": [6],
        },
    )
    assert passes_junk_year_filter(patriot_paper)


# ---------- test 4: post-1990 papers pass junk-year regardless ----------


def test_junk_year_post_1990_passes_through() -> None:
    """Year ≥1990 → junk-year filter does not fire."""
    # 2020 paper with "GAN" in title: passes (year >= 1990)
    gan_2020 = _make_work(
        year=2020,
        title="A novel GAN architecture",
        inv={"a": [0], "novel": [1], "gan": [2], "model": [3]},
    )
    assert passes_junk_year_filter(gan_2020)

    # 1995 paper with "blockchain": passes
    blockchain_1995 = _make_work(
        year=1995,
        title="Early blockchain ideas",
        inv={"early": [0], "blockchain": [1], "concepts": [2]},
    )
    assert passes_junk_year_filter(blockchain_1995)

    # Year missing entirely: passes (treated as not-pre-1990)
    no_year = _make_work(year=None, title="Paper with blockchain in title")
    assert passes_junk_year_filter(no_year)

    # Exactly 1990: passes (threshold is < 1990 for filter to fire)
    paper_1990 = _make_work(
        year=1990,
        title="Use of LSTM in early NLP",
        inv={"use": [0], "of": [1], "lstm": [2], "in": [3], "nlp": [4]},
    )
    assert passes_junk_year_filter(paper_1990)


# ---------- test 5: empty-abstract threshold ----------


def test_empty_abs_threshold_at_15_tokens() -> None:
    """≥15 tokens passes; <15 fails. Token = sum of positions."""
    # exactly 15 tokens (15 unique words at positions 0-14)
    fifteen = _make_work(
        inv={f"word{i}": [i] for i in range(15)},
    )
    assert abstract_token_count(fifteen) == 15
    assert passes_empty_abstract_filter(fifteen)

    # 14 tokens: fails
    fourteen = _make_work(
        inv={f"word{i}": [i] for i in range(14)},
    )
    assert abstract_token_count(fourteen) == 14
    assert not passes_empty_abstract_filter(fourteen)

    # 100 tokens: passes easily
    hundred = _make_work(
        inv={f"word{i}": [i] for i in range(100)},
    )
    assert passes_empty_abstract_filter(hundred)

    # Repeated tokens count by occurrence (sum of positions across keys)
    # "the" appears 5 times + "a" appears 5 times + 5 unique = 15 tokens
    repeats = _make_work(
        inv={
            "the": [0, 2, 4, 6, 8],
            "a": [1, 3, 5, 7, 9],
            "word10": [10], "word11": [11], "word12": [12],
            "word13": [13], "word14": [14],
        },
    )
    assert abstract_token_count(repeats) == 15
    assert passes_empty_abstract_filter(repeats)


# ---------- test 6: full pipeline keeps legitimate pre-1990 paper ----------


def test_full_pipeline_keeps_pre_1990_legitimate_paper() -> None:
    """A 1980 cs paper with substantive abstract + no junk tokens → kept."""
    legit_1980 = _make_work(
        year=1980,
        title="Internal Sorting Using a Minimal Tree Merge Strategy",
        concepts=[{"id": "https://openalex.org/C41008148", "score": 0.85}],
        inv={
            "this": [0], "paper": [1], "describes": [2], "an": [3],
            "internal": [4], "sorting": [5], "algorithm": [6],
            "based": [7], "on": [8], "tree": [9], "merging": [10],
            "with": [11], "minimal": [12], "comparisons": [13],
            "for": [14], "performance": [15], "evaluation": [16],
        },
    )
    kept = list(apply_section0_filter([legit_1980]))
    assert len(kept) == 1
    assert kept[0]["id"] == legit_1980["id"]


# ---------- test 7: full pipeline drops post-2000 content with 1970 year ----------


def test_full_pipeline_drops_post_2000_content_with_1970_year() -> None:
    """A 1975 paper with 'blockchain' in abstract → dropped (junk-year)."""
    junk_1975 = _make_work(
        year=1975,
        title="Distributed systems",  # innocuous title
        concepts=[{"id": "https://openalex.org/C41008148", "score": 0.85}],
        inv={
            "this": [0], "paper": [1], "discusses": [2],
            "blockchain": [3], "consensus": [4], "in": [5],
            "distributed": [6], "systems": [7], "from": [8],
            "1975": [9], "perspective": [10], "and": [11],
            "scaling": [12], "issues": [13], "today": [14],
        },
    )
    kept = list(apply_section0_filter([junk_1975]))
    assert len(kept) == 0


# ---------- bonus: pipeline correctness on a mixed batch ----------


def test_apply_section0_filter_is_a_generator() -> None:
    """apply_section0_filter yields lazily — important for 492M-record streams."""
    works = [
        _make_work() for _ in range(5)  # all pass §0
    ]
    result = apply_section0_filter(works)
    # Should be an iterator/generator, not a materialized list
    assert hasattr(result, "__iter__")
    materialized = list(result)
    assert len(materialized) == 5


def test_apply_section0_filter_drops_each_failure_mode() -> None:
    """Mixed batch: one failure per filter rule + 2 legit → 2 kept."""
    legit1 = _make_work(year=2020)
    legit2 = _make_work(year=1985)
    bad_score = _make_work(
        concepts=[{"id": "https://openalex.org/C41008148", "score": 0.20}],
    )
    no_abstract = _make_work(inv={})
    junk_year = _make_work(
        year=1975,
        title="Use of LSTM in 1975",
        inv={"use": [0], "of": [1], "lstm": [2], "in": [3], "papers": [4],
             "from": [5], "1975": [6], "is": [7], "anachronistic": [8],
             "and": [9], "obviously": [10], "wrong": [11], "data": [12],
             "drift": [13], "issue": [14]},
    )
    short_abstract = _make_work(inv={"too": [0], "short": [1], "abstract": [2]})

    batch = [legit1, bad_score, no_abstract, junk_year, short_abstract, legit2]
    kept = list(apply_section0_filter(batch))
    # Both legit1 and legit2 share the default id; check count instead of ids
    assert len(kept) == 2


# ---------- type allow-list (Phase 1.2 amendment) ----------


def test_type_filter_allows_research_paper_types() -> None:
    """All types in ALLOWED_WORK_TYPES pass."""
    for work_type in ALLOWED_WORK_TYPES:
        w = _make_work(work_type=work_type)
        assert passes_type_filter(w), f"{work_type} should pass"


def test_type_filter_excludes_dataset_and_other_junk_types() -> None:
    """Dataset, paratext, libguides, peer-review, etc. all fail."""
    junk_types = [
        "dataset",       # GBIF Occurrence Downloads, Zenodo data DOIs
        "paratext",      # journal frontmatter / indices
        "libguides",     # library research guides
        "peer-review",   # peer-review reports
        "erratum",       # corrections
        "retraction",    # retraction notices
        "reference-entry",   # encyclopedia entries
        "supplementary-materials",
        "grant",
        "software",
        "standard",
        "other",         # OpenAlex's catch-all
    ]
    for work_type in junk_types:
        w = _make_work(work_type=work_type)
        assert not passes_type_filter(w), f"{work_type} should be excluded"


def test_type_filter_excludes_missing_or_none_type() -> None:
    """Missing or None type fails (allow-list bias: unknown types are out)."""
    w_no_type = _make_work()
    del w_no_type["type"]
    assert not passes_type_filter(w_no_type)

    w_none_type = _make_work()
    w_none_type["type"] = None
    assert not passes_type_filter(w_none_type)

    w_non_string_type = _make_work()
    w_non_string_type["type"] = 123
    assert not passes_type_filter(w_non_string_type)


def test_full_pipeline_drops_dataset_even_when_other_fields_valid() -> None:
    """A type='dataset' work that would otherwise pass §0 is dropped.

    Mirrors the real Phase 1.2 H2-audit finding: GBIF "Occurrence
    Download" records with cs concepts at score>=0.30 + substantive
    abstract + valid year all pass the original 4 §0 stages but are
    not research papers.
    """
    gbif_like = _make_work(
        work_type="dataset",
        title="Occurrence Download",
        concepts=[
            {"id": "https://openalex.org/C41008148", "score": 0.55},  # cs
            {"id": "https://openalex.org/C36289849", "score": 0.40},  # other
        ],
    )
    legit_article = _make_work(work_type="article")

    kept = list(apply_section0_filter([gbif_like, legit_article]))
    assert len(kept) == 1
    assert kept[0]["type"] == "article"


# ---------- §0 v3 amendments (Phase 1.2 H2 audit retro) ----------


def _make_inv_from_text(text: str) -> dict[str, list[int]]:
    """Build an inverted index from a space-separated text string.

    Used in v3 tests so the prefix-blacklist patterns are easy to
    write out as natural English rather than as raw position maps.
    """
    inv: dict[str, list[int]] = {}
    for i, word in enumerate(text.split()):
        inv.setdefault(word, []).append(i)
    return inv


def test_abstract_prefix_blocks_acs_advertisement_chrome() -> None:
    """ACS Publications "ADVERTISEMENT RETURN TO ISSUE..." abstracts blocked."""
    acs_chrome = _make_work(
        inv=_make_inv_from_text(
            "ADVERTISEMENT RETURN TO ISSUE PREV Article NEXT Some Chemistry Paper "
            "with normal-looking words after the publisher chrome prefix"
        ),
    )
    assert not passes_abstract_prefix_filter(acs_chrome)

    cen_news = _make_work(
        inv=_make_inv_from_text(
            "RETURN TO ISSUE PREV News NEXT GOVERNMENT Russia's Big Bomb "
            "Soviet explodes megaton nuclear weapon"
        ),
    )
    assert not passes_abstract_prefix_filter(cen_news)


def test_abstract_prefix_blocks_wiley_oup_aip_views_icon_chrome() -> None:
    """Wiley / OUP / AIP "Views Icon Views..." chrome blocked."""
    wiley_chrome = _make_work(
        inv=_make_inv_from_text(
            "Views Icon Views Article contents Figures and tables Video Audio "
            "Supplementary Data Peer Review Share Icon Share"
        ),
    )
    assert not passes_abstract_prefix_filter(wiley_chrome)


def test_abstract_prefix_blocks_article_metrics_stubs() -> None:
    """Article Metrics chrome blocked."""
    metrics_stub = _make_work(
        inv=_make_inv_from_text(
            "Article MetricsDownloadsCitationsNo data available "
            "AugSepOctNovDecJan Total months"
        ),
    )
    assert not passes_abstract_prefix_filter(metrics_stub)


def test_abstract_prefix_blocks_author_version_placeholders() -> None:
    """Publication-status placeholders ("This is the author's version...") blocked."""
    author_version = _make_work(
        inv=_make_inv_from_text(
            "This is the author's version of a work that was accepted for "
            "publication in Neurocomputing"
        ),
    )
    assert not passes_abstract_prefix_filter(author_version)


def test_abstract_prefix_passes_real_abstracts() -> None:
    """Real research abstracts pass the prefix filter."""
    real_paper = _make_work(
        inv=_make_inv_from_text(
            "We present a novel algorithm for computing the convex hull "
            "of n points in three dimensions with optimal time complexity"
        ),
    )
    assert passes_abstract_prefix_filter(real_paper)


def test_abstract_prefix_case_insensitive() -> None:
    """Prefix match is case-insensitive."""
    # mixed-case "ReTuRn To IsSuE" should still match
    weird_case = _make_work(
        inv=_make_inv_from_text(
            "ReTuRn To IsSuE PREV some other content here"
        ),
    )
    assert not passes_abstract_prefix_filter(weird_case)


def test_abstract_prefix_handles_missing_or_empty() -> None:
    """No abstract / empty abstract / non-dict inv → pass (other filters catch)."""
    no_inv = _make_work()
    no_inv["abstract_inverted_index"] = None
    assert passes_abstract_prefix_filter(no_inv)

    empty_inv = _make_work(inv={})
    assert passes_abstract_prefix_filter(empty_inv)


def test_title_prefix_blocks_known_artifact_titles() -> None:
    """Front-matter / news-brief / annex titles blocked."""
    assert not passes_title_prefix_filter(_make_work(title="NEW PRODUCTS"))
    assert not passes_title_prefix_filter(_make_work(title="Contributors"))
    assert not passes_title_prefix_filter(_make_work(title="Contributors:"))
    assert not passes_title_prefix_filter(
        _make_work(title="Contributors 2024"),
    )
    assert not passes_title_prefix_filter(
        _make_work(title="Annex 3 Communication and Data Management Guidelines"),
    )
    assert not passes_title_prefix_filter(_make_work(title="Key Messages"))
    assert not passes_title_prefix_filter(_make_work(title="Editorial Board 2024"))


def test_title_prefix_passes_real_titles_starting_with_blacklist_words() -> None:
    """Real paper titles starting with blacklist words but in real-paper
    contexts pass — i.e., the regex is precise enough.
    """
    # "Annex Effects in..." — "Annex" without a number → not the
    # blacklisted "Annex 3" pattern
    assert passes_title_prefix_filter(
        _make_work(title="Annex Effects in Quantum Hall Systems"),
    )
    # "Contributors to Variance..." — "Contributors" followed by " to "
    # (preposition + alphabetic continuation) → not the blacklisted
    # form (which requires terminal punct, end-of-string, or digit
    # suffix)
    assert passes_title_prefix_filter(
        _make_work(title="Contributors to Variance in fMRI BOLD Signal"),
    )


def test_title_prefix_handles_missing_title() -> None:
    """Missing / None / non-string title → pass."""
    w = _make_work()
    del w["title"]
    assert passes_title_prefix_filter(w)

    w_none = _make_work()
    w_none["title"] = None
    assert passes_title_prefix_filter(w_none)

    w_non_string = _make_work()
    w_non_string["title"] = 42
    assert passes_title_prefix_filter(w_non_string)


def test_score_threshold_v3_is_higher_than_v2() -> None:
    """v3 score threshold (0.40) excludes papers v2 (0.30) admits."""
    boundary_paper = _make_work(
        concepts=[{"id": "https://openalex.org/C41008148", "score": 0.35}],
    )
    # v2: passes (0.35 >= 0.30)
    assert passes_score_any_field(boundary_paper)
    # v3: fails (0.35 < 0.40)
    assert not passes_score_any_field(
        boundary_paper, threshold=SCORE_THRESHOLD_V3,
    )


def test_min_tokens_v3_is_higher_than_v2() -> None:
    """v3 token min (50) rejects abstracts v2 (15) admits."""
    short_paper = _make_work(
        inv={f"word{i}": [i] for i in range(30)},  # 30 tokens
    )
    # v2: passes (30 >= 15)
    assert passes_empty_abstract_filter(short_paper)
    # v3: fails (30 < 50)
    assert not passes_empty_abstract_filter(
        short_paper, min_tokens=EMPTY_ABSTRACT_MIN_TOKENS_V3,
    )


def test_v3_pipeline_drops_publisher_chrome_paper() -> None:
    """v3 drops an ACS chrome paper that v2 would have kept.

    The underlying paper might be real chemistry research, but the
    abstract field is unusable for downstream embeddings.
    """
    # An ACS-chrome paper with otherwise valid §0 fields
    acs_paper = _make_work(
        work_type="article",
        concepts=[{"id": "https://openalex.org/C41008148", "score": 0.55}],
        inv=_make_inv_from_text(
            "ADVERTISEMENT RETURN TO ISSUE PREV Article NEXT Aliphatic semidiones "
            "XXIV Bicyclo n.2.0 alkane semidiones Glen Russell Philip Whittle "
            "Cite this J. Am. Chem. Soc. publication date October citation "
            "downloads icon altmetric attention score view page"
        ),
    )
    # v2 keeps it (passes type + score + token min + has_abstract +
    # junk_year)
    v2_kept = list(apply_section0_filter([acs_paper]))
    assert len(v2_kept) == 1
    # v3 drops it (prefix blacklist)
    v3_kept = list(apply_section0_filter_v3([acs_paper]))
    assert len(v3_kept) == 0


def test_v3_pipeline_drops_low_confidence_concept_paper() -> None:
    """v3 drops a paper with CS concept only at 0.30-0.39 (concept-tagger noise)."""
    weak_cs_paper = _make_work(
        work_type="article",
        concepts=[{"id": "https://openalex.org/C41008148", "score": 0.34}],
        inv=_make_inv_from_text(" ".join(f"word{i}" for i in range(60))),
    )
    # v2 keeps it (passes 0.30 threshold)
    assert len(list(apply_section0_filter([weak_cs_paper]))) == 1
    # v3 drops it (fails 0.40 threshold)
    assert len(list(apply_section0_filter_v3([weak_cs_paper]))) == 0


def test_v3_pipeline_keeps_legitimate_paper() -> None:
    """A real CS paper with strong concept score + long real abstract → v3 keeps."""
    real_paper = _make_work(
        work_type="article",
        concepts=[{"id": "https://openalex.org/C41008148", "score": 0.85}],
        inv=_make_inv_from_text(
            "We present a novel algorithm for solving the maximum bipartite "
            "matching problem in O(V sqrt E) time with applications to "
            "scheduling network flow and pattern recognition tasks in modern "
            "distributed systems. The algorithm extends the Hopcroft-Karp "
            "approach with a novel pruning heuristic that reduces the constant "
            "factor by approximately 30 percent on dense instances. We prove "
            "correctness via reduction to alternating-path arguments and "
            "demonstrate empirical speedups on standard benchmarks."
        ),
    )
    kept = list(apply_section0_filter_v3([real_paper]))
    assert len(kept) == 1


def test_v3_pipeline_drops_short_abstract_paper() -> None:
    """v3 drops a paper with 15-49 token abstract (v2 would keep)."""
    short_paper = _make_work(
        work_type="article",
        concepts=[{"id": "https://openalex.org/C41008148", "score": 0.85}],
        inv={f"word{i}": [i] for i in range(20)},  # 20 tokens (v2 OK, v3 NO)
    )
    assert len(list(apply_section0_filter([short_paper]))) == 1
    assert len(list(apply_section0_filter_v3([short_paper]))) == 0


def test_v3_pipeline_drops_title_artifact_paper() -> None:
    """v3 drops a paper with blacklisted title prefix (v2 would keep)."""
    artifact = _make_work(
        work_type="article",
        title="Annex 3 Communication and Data Management Guidelines for CoARA WGs",
        concepts=[{"id": "https://openalex.org/C41008148", "score": 0.85}],
        inv=_make_inv_from_text(" ".join(f"word{i}" for i in range(60))),
    )
    assert len(list(apply_section0_filter([artifact]))) == 1
    assert len(list(apply_section0_filter_v3([artifact]))) == 0


def test_apply_section0_filter_v3_is_a_generator() -> None:
    """v3 pipeline is lazy (production-scale streaming compat)."""
    works = [
        _make_work(
            concepts=[{"id": "https://openalex.org/C41008148", "score": 0.85}],
            inv=_make_inv_from_text(" ".join(f"word{i}" for i in range(60))),
        )
        for _ in range(3)
    ]
    result = apply_section0_filter_v3(works)
    assert hasattr(result, "__iter__")
    assert len(list(result)) == 3


def test_v3_prefix_patterns_module_level() -> None:
    """Sanity check that the module-level pattern constants are exposed."""
    assert ABSTRACT_PREFIX_BLACKLIST_PATTERN.match("RETURN TO ISSUE PREV Article")
    assert ABSTRACT_PREFIX_BLACKLIST_PATTERN.match("Views Icon Views Article contents")
    assert TITLE_PREFIX_BLACKLIST_PATTERN.match("NEW PRODUCTS")
    assert TITLE_PREFIX_BLACKLIST_PATTERN.match("Editorial Board 2024")
