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
    abstract_token_count,
    apply_section0_filter,
    has_abstract,
    passes_empty_abstract_filter,
    passes_junk_year_filter,
    passes_score_any_field,
)

# ---------- helpers for building test work records ----------


def _make_work(
    *,
    title: str = "Test paper",
    year: int | None = 2020,
    concepts: list[dict[str, Any]] | None = None,
    inv: dict[str, list[int]] | None = None,
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
