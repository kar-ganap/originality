"""Unit tests for demographic-annotation pipeline (Phase 1.3).

§4 of `docs/desiderata.md` constrains the demographic-inference
stack:

- Gender: gender_guesser primary, Genderize cross-validation,
  NamSor sample-based bias estimation per Phase 1.3 plan §3.
- Country: extracted from ``authorships[*].countries`` (preferred)
  or ``authorships[*].institutions[*].country_code`` (fallback).
- Coverage + sensitivity bounds per cell.

Step 1 covers author-records extraction; subsequent steps cover
gender + country annotation, NamSor stratified sampling, bias
correction, and the per-cell coverage table.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from whitespace2.demographics import (
    _bootstrap_sum_ci,
    _extract_first_name,
    _extract_source_type,
    _gg_label_to_gender_probability,
    _ratio_ci,
    _shannon_entropy_mm,
    _wilson_ci,
    aggregate_per_author,
    annotate_gender_country,
    annotate_with_gender_guesser,
    apply_bias_correction,
    build_cell_coverage_table,
    build_coverage_table,
    build_paper_field_map,
    combine_gg_and_genderize,
    compute_career_length_screen,
    compute_confusion_matrix,
    compute_orcid_consistency,
    explode_authorships_for_paper,
    extract_authorships,
    extract_primary_field,
    perturb_row_normalized,
    query_genderize,
    query_genderize_batch,
    query_namsor,
    query_namsor_batch,
    sample_for_namsor,
    stratified_sample_names,
    tag_script_region,
    validate_disambiguation,
)

# ---------- helpers for building test author records ----------


def _make_author(
    *,
    author_id: str = "https://openalex.org/A5000000001",
    display_name: str = "John Q. Public",
    orcid: str | None = "https://orcid.org/0000-0000-0000-0001",
    position: str = "first",
    is_corresponding: bool = True,
    countries: list[str] | None = None,
    institutions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "author": {
            "display_name": display_name,
            "id": author_id,
            "orcid": orcid,
        },
        "author_position": position,
        "is_corresponding": is_corresponding,
        "countries": countries if countries is not None else ["US"],
        "institutions": institutions if institutions is not None else [
            {"country_code": "US", "display_name": "Test Univ",
             "id": "https://openalex.org/I0001"},
        ],
        "raw_author_name": display_name,
        "affiliations": [],
        "raw_affiliation_strings": [],
    }


def _make_paper(
    *,
    paper_id: str = "https://openalex.org/W1000000001",
    year: int | None = 2020,
    authorships: list[dict[str, Any]] | None = None,
    source_type: str | None = "journal",
) -> dict[str, Any]:
    if authorships is None:
        authorships = [_make_author()]
    primary_location: dict[str, Any] | None
    if source_type is not None:
        primary_location = {
            "source": {
                "type": source_type,
                "display_name": "Test Venue",
                "id": "https://openalex.org/S0001",
            },
        }
    else:
        primary_location = None
    return {
        "id": paper_id,
        "publication_year": year,
        "authorships_json": json.dumps(authorships),
        "primary_location_json": (
            json.dumps(primary_location)
            if primary_location is not None
            else None
        ),
    }


# ---------- _extract_first_name ----------


def test_extract_first_name_handles_full_name() -> None:
    """Full first name + middle initial + last → first token returned."""
    assert _extract_first_name("Thomas A. Brubaker") == ("Thomas", False)
    assert _extract_first_name("Jane Doe") == ("Jane", False)
    assert _extract_first_name("Hiroshi Tanaka") == ("Hiroshi", False)


def test_extract_first_name_flags_initials() -> None:
    """Single-letter or 2-letter first tokens are flagged as initials."""
    # "C.F. Gauss" → first token "C.F.", strip period → "C.F" (3 chars,
    # not flagged). Actually with two periods we get tokens ["C.F.", "Gauss"]
    # → strip trailing period → "C.F". Let's check both behaviours.
    # For the simple case:
    assert _extract_first_name("C. Gauss") == ("C", True)
    assert _extract_first_name("J Doe") == ("J", True)
    # Two-letter initial (e.g., "CF Gauss"):
    assert _extract_first_name("CF Gauss") == ("CF", True)


def test_extract_first_name_handles_missing_or_empty() -> None:
    """None, empty, whitespace, non-string → (empty, False)."""
    assert _extract_first_name(None) == ("", False)
    assert _extract_first_name("") == ("", False)
    assert _extract_first_name("   ") == ("", False)
    assert _extract_first_name(42) == ("", False)  # type: ignore[arg-type]


# ---------- _extract_source_type ----------


def test_extract_source_type_valid_journal() -> None:
    """Well-formed primary_location_json → source.type returned."""
    pl = json.dumps({"source": {"type": "journal", "display_name": "X"}})
    assert _extract_source_type(pl) == "journal"

    pl_repo = json.dumps({"source": {"type": "repository", "display_name": "arXiv"}})
    assert _extract_source_type(pl_repo) == "repository"


def test_extract_source_type_handles_missing_or_malformed() -> None:
    """None / empty / malformed / missing-source / missing-type → None."""
    assert _extract_source_type(None) is None
    assert _extract_source_type("") is None
    assert _extract_source_type("{not json") is None
    assert _extract_source_type("[]") is None  # wrong shape
    assert _extract_source_type(json.dumps({"source": None})) is None
    assert _extract_source_type(json.dumps({"source": {}})) is None
    assert _extract_source_type(
        json.dumps({"source": {"type": None}}),
    ) is None
    assert _extract_source_type(json.dumps({})) is None  # no source key


# ---------- explode_authorships_for_paper ----------


def test_explode_authorships_produces_one_row_per_author_paper() -> None:
    """A paper with N authors → exactly N rows, each with
    paper_id + author fields. Matches the pre-registered H1 test
    pattern from the plan.
    """
    paper = _make_paper(
        paper_id="https://openalex.org/W42",
        year=2022,
        authorships=[
            _make_author(author_id="https://openalex.org/A1",
                         display_name="Alice Smith"),
            _make_author(author_id="https://openalex.org/A2",
                         display_name="Bob Jones", position="middle",
                         is_corresponding=False),
            _make_author(author_id="https://openalex.org/A3",
                         display_name="Carol Tan", position="last",
                         is_corresponding=False),
        ],
    )
    rows = explode_authorships_for_paper(paper)
    assert len(rows) == 3
    assert all(r["paper_id"] == "https://openalex.org/W42" for r in rows)
    assert all(r["publication_year"] == 2022 for r in rows)
    assert all(r["source_type"] == "journal" for r in rows)
    assert [r["author_id"] for r in rows] == [
        "https://openalex.org/A1",
        "https://openalex.org/A2",
        "https://openalex.org/A3",
    ]
    assert [r["author_first_name"] for r in rows] == ["Alice", "Bob", "Carol"]
    assert [r["author_position"] for r in rows] == ["first", "middle", "last"]
    assert [r["is_corresponding"] for r in rows] == [True, False, False]


def test_explode_authorships_carries_repository_source_type() -> None:
    """Repository / preprint papers get source_type='repository' per row."""
    paper = _make_paper(
        source_type="repository",
        authorships=[
            _make_author(author_id="https://openalex.org/A1"),
            _make_author(author_id="https://openalex.org/A2"),
        ],
    )
    rows = explode_authorships_for_paper(paper)
    assert len(rows) == 2
    assert all(r["source_type"] == "repository" for r in rows)


def test_explode_authorships_carries_none_source_type_when_missing() -> None:
    """Missing primary_location_json → source_type=None on all rows."""
    paper = _make_paper(
        source_type=None,  # primary_location_json will be None
        authorships=[_make_author(author_id="https://openalex.org/A1")],
    )
    rows = explode_authorships_for_paper(paper)
    assert len(rows) == 1
    assert rows[0]["source_type"] is None


def test_explode_authorships_skips_author_without_id() -> None:
    """Authors lacking a stable id (the disambiguation key) are
    dropped — they can't be tracked across papers.
    """
    paper = _make_paper(
        authorships=[
            _make_author(author_id="https://openalex.org/A1"),
            {
                "author": {"display_name": "No ID Anon", "id": None,
                           "orcid": None},
                "author_position": "middle",
                "is_corresponding": False,
                "countries": [], "institutions": [],
            },
        ],
    )
    rows = explode_authorships_for_paper(paper)
    assert len(rows) == 1
    assert rows[0]["author_id"] == "https://openalex.org/A1"


def test_explode_authorships_handles_empty_or_malformed_json() -> None:
    """Missing / malformed authorships_json → empty list, no exception."""
    # None
    p = _make_paper()
    p["authorships_json"] = None  # type: ignore[assignment]
    assert explode_authorships_for_paper(p) == []
    # Empty string
    p["authorships_json"] = ""
    assert explode_authorships_for_paper(p) == []
    # Malformed JSON
    p["authorships_json"] = "{not json"
    assert explode_authorships_for_paper(p) == []
    # Valid JSON but wrong shape (e.g., dict instead of list)
    p["authorships_json"] = "{}"
    assert explode_authorships_for_paper(p) == []
    # Empty list
    p["authorships_json"] = "[]"
    assert explode_authorships_for_paper(p) == []


def test_explode_authorships_preserves_orcid_and_countries() -> None:
    """ORCID + countries pass through verbatim."""
    paper = _make_paper(
        authorships=[
            _make_author(
                author_id="https://openalex.org/A1",
                orcid="https://orcid.org/0000-0002-5444-8105",
                countries=["US", "JP"],
            ),
            _make_author(
                author_id="https://openalex.org/A2",
                orcid=None,
                countries=[],
            ),
        ],
    )
    rows = explode_authorships_for_paper(paper)
    assert rows[0]["author_orcid"] == "https://orcid.org/0000-0002-5444-8105"
    assert rows[0]["countries"] == ["US", "JP"]
    assert rows[1]["author_orcid"] is None
    assert rows[1]["countries"] == []


# ---------- extract_authorships (parquet streaming) ----------


def test_extract_authorships_writes_parquet_with_expected_shape(
    tmp_path: Path,
) -> None:
    """End-to-end: write a 3-paper synthetic input parquet, run
    extract_authorships, verify the output parquet has the right
    row count + columns.
    """
    # Build synthetic input matching v3 schema
    papers = [
        _make_paper(
            paper_id=f"https://openalex.org/W{i}",
            year=2000 + i,
            authorships=[
                _make_author(
                    author_id=f"https://openalex.org/A{i}_{j}",
                    display_name=f"Author{i}_{j} Surname",
                )
                for j in range(1 + i)  # paper 0 has 1 author, paper 1 has 2, paper 2 has 3
            ],
        )
        for i in range(3)
    ]
    src = tmp_path / "input.parquet"
    tbl = pa.Table.from_pylist(papers)
    pq.write_table(tbl, str(src), compression="zstd")

    dst = tmp_path / "output.parquet"
    result = extract_authorships(src, dst, batch_size=2)

    assert result["n_papers"] == 3
    assert result["n_author_paper_rows"] == 1 + 2 + 3  # = 6

    # Output parquet shape
    out_tbl = pq.read_table(str(dst))
    assert out_tbl.num_rows == 6
    cols = set(out_tbl.column_names)
    assert {"paper_id", "publication_year", "source_type", "author_id",
            "author_first_name", "author_position",
            "is_corresponding", "author_orcid", "countries"}.issubset(cols)


def test_extract_authorships_handles_no_authors_papers(
    tmp_path: Path,
) -> None:
    """Papers with empty authorships_json → 0 rows but pipeline
    doesn't error. Writer is only created if there's at least one
    row to write.
    """
    papers = [_make_paper(paper_id="https://openalex.org/W1", authorships=[])]
    src = tmp_path / "in.parquet"
    pq.write_table(pa.Table.from_pylist(papers), str(src))

    dst = tmp_path / "out.parquet"
    result = extract_authorships(src, dst, batch_size=10)
    assert result["n_papers"] == 1
    assert result["n_author_paper_rows"] == 0
    # No output parquet created (acceptable; documented behaviour)
    assert not dst.exists()


# ---------- disambiguation validation (Step 2) ----------


def _make_author_rows(
    rows: list[tuple[str, int | None, str | None]],
) -> pa.Table:
    """Build a per-author-paper Arrow table from
    (author_id, publication_year, author_orcid) tuples.

    Used by Step 2 tests to construct mock authorship inputs.
    """
    return pa.table({
        "author_id": [r[0] for r in rows],
        "publication_year": [r[1] for r in rows],
        "author_orcid": [r[2] for r in rows],
    })


def test_career_length_screen_flags_long_careers() -> None:
    """Authors whose papers span >threshold years get flagged."""
    rows = [
        # author A1: papers 1980, 2020 (40-year career) — NOT flagged
        ("https://openalex.org/A1", 1980, None),
        ("https://openalex.org/A1", 2020, None),
        # author A2: papers 1950, 2020 (70-year career) — flagged
        ("https://openalex.org/A2", 1950, None),
        ("https://openalex.org/A2", 2020, None),
        # author A3: 1 paper (career=0) — NOT flagged
        ("https://openalex.org/A3", 2010, None),
    ]
    table = _make_author_rows(rows)
    result = compute_career_length_screen(table, threshold=60)

    assert result["n_unique_authors"] == 3
    assert result["n_flagged_cross_era_merger"] == 1
    assert result["flagged_fraction"] == 1 / 3


def test_career_length_screen_handles_missing_years() -> None:
    """Authors with no publication_year are excluded from the screen."""
    rows = [
        ("https://openalex.org/A1", None, None),
        ("https://openalex.org/A1", 2020, None),
        ("https://openalex.org/A2", None, None),  # only None-year paper
    ]
    table = _make_author_rows(rows)
    result = compute_career_length_screen(table, threshold=60)
    # A1 contributes (only the non-null year); A2 has no valid year → excluded
    assert result["n_unique_authors"] == 1
    assert result["n_flagged_cross_era_merger"] == 0


def test_orcid_consistency_perfect_agreement() -> None:
    """Every ORCID maps to exactly 1 author.id → consistency rate = 1.0."""
    rows = [
        ("https://openalex.org/A1", 2020,
         "https://orcid.org/0000-0001-0000-0001"),
        ("https://openalex.org/A1", 2021,
         "https://orcid.org/0000-0001-0000-0001"),
        ("https://openalex.org/A2", 2020,
         "https://orcid.org/0000-0001-0000-0002"),
    ]
    table = _make_author_rows(rows)
    result = compute_orcid_consistency(table)

    assert result["n_paper_rows_with_orcid"] == 3
    assert result["n_unique_orcids"] == 2
    assert result["n_orcids_consistent"] == 2
    assert result["n_orcids_inconsistent"] == 0
    assert result["orcid_consistency_rate"] == 1.0
    assert result["paper_level_agreement_rate"] == 1.0


def test_orcid_consistency_with_split_author() -> None:
    """One ORCID mapping to two author.ids → consistency rate < 1.0.

    Models OpenAlex disambiguation splitting a real author into 2 IDs.
    Paper-level agreement = papers on the dominant author.id /
    total ORCID-tagged papers.
    """
    rows = [
        # ORCID #1 maps to A1 (3 papers) AND A2 (1 paper) — A1 dominant
        ("https://openalex.org/A1", 2020,
         "https://orcid.org/0000-0001-0000-0001"),
        ("https://openalex.org/A1", 2021,
         "https://orcid.org/0000-0001-0000-0001"),
        ("https://openalex.org/A1", 2022,
         "https://orcid.org/0000-0001-0000-0001"),
        ("https://openalex.org/A2", 2023,
         "https://orcid.org/0000-0001-0000-0001"),
        # ORCID #2 maps to A3 (consistent)
        ("https://openalex.org/A3", 2020,
         "https://orcid.org/0000-0001-0000-0002"),
    ]
    table = _make_author_rows(rows)
    result = compute_orcid_consistency(table)

    assert result["n_paper_rows_with_orcid"] == 5
    assert result["n_unique_orcids"] == 2
    assert result["n_orcids_consistent"] == 1  # ORCID #2 only
    assert result["n_orcids_inconsistent"] == 1
    assert result["orcid_consistency_rate"] == 0.5
    # paper-level: 4 of 5 papers are on the dominant pairing
    # (3 A1↔ORCID1, 1 A3↔ORCID2; A2↔ORCID1 disagrees)
    assert result["paper_level_agreement_rate"] == 4 / 5


def test_orcid_consistency_filters_nulls() -> None:
    """Rows with null author_orcid or null author_id are excluded."""
    rows = [
        ("https://openalex.org/A1", 2020,
         "https://orcid.org/0000-0001-0000-0001"),
        ("https://openalex.org/A2", 2020, None),  # no orcid
        (None, 2020,                              # type: ignore[list-item]
         "https://orcid.org/0000-0001-0000-0002"),  # no author_id
    ]
    table = _make_author_rows(rows)
    result = compute_orcid_consistency(table)
    # Only the first row is analyzable
    assert result["n_paper_rows_with_orcid"] == 1
    assert result["n_unique_orcids"] == 1


def test_validate_disambiguation_e2e(tmp_path: Path) -> None:
    """Write a mock authorships parquet, run validate_disambiguation,
    verify output JSON has the expected H1+H2 fields and verdicts.
    """
    rows = [
        # 4 authors with normal careers (none flagged); 1 with 70yr career (flagged)
        ("https://openalex.org/A1", 2010, "https://orcid.org/0000-1"),
        ("https://openalex.org/A1", 2020, "https://orcid.org/0000-1"),
        ("https://openalex.org/A2", 2015, None),
        ("https://openalex.org/A3", 2018,
         "https://orcid.org/0000-2"),
        ("https://openalex.org/A4", 2020, None),
        ("https://openalex.org/A5", 1950, None),  # 70-year career → flagged
        ("https://openalex.org/A5", 2020, None),
    ]
    table = _make_author_rows(rows)
    src = tmp_path / "authorships.parquet"
    pq.write_table(table, str(src))
    out = tmp_path / "validation.json"

    result = validate_disambiguation(src, out, career_length_threshold=60)

    assert out.exists()
    # H1
    assert result["h1_career_length_screen"]["n_unique_authors"] == 5
    assert result["h1_career_length_screen"]["n_flagged_cross_era_merger"] == 1
    assert result["h1_career_length_screen"]["flagged_fraction"] == 1 / 5
    # H1 acceptance: 20% flagged is > 5%; should NOT pass
    assert result["h1_passes"] is False

    # H2: 2 orcid-tagged authors, both consistent
    assert result["h2_orcid_consistency"]["orcid_consistency_rate"] == 1.0
    assert result["h2_passes"] is True

    # JSON loadable
    loaded = json.loads(out.read_text())
    assert loaded["h1_career_length_screen"]["n_unique_authors"] == 5


# ---------- gender_guesser annotation (Step 3a) ----------


def test_gg_label_to_gender_probability_mapping() -> None:
    """gender_guesser's 6-class labels → (gender, probability) tuples.

    Mapping (per Phase 1.3 plan §"Gender stack"):
      male / female    → confident (p=1.0)
      mostly_*         → mid (p=0.7)
      andy             → unknown (p=0.0; ambiguous unisex name)
      unknown          → unknown (p=0.0; not in gender_guesser's dictionary)
    """
    assert _gg_label_to_gender_probability("male") == ("male", 1.0)
    assert _gg_label_to_gender_probability("female") == ("female", 1.0)
    assert _gg_label_to_gender_probability("mostly_male") == ("male", 0.7)
    assert _gg_label_to_gender_probability("mostly_female") == ("female", 0.7)
    assert _gg_label_to_gender_probability("andy") == ("unknown", 0.0)
    assert _gg_label_to_gender_probability("unknown") == ("unknown", 0.0)
    # Defensive: any other string → unknown
    assert _gg_label_to_gender_probability("bogus") == ("unknown", 0.0)


def test_annotate_with_gender_guesser_known_names() -> None:
    """Known names from the smoke: John → male, Mary → mostly_female,
    Hiroshi → male, Wei → andy (Asian unisex), Asdfg → unknown.

    Returns dict[first_name → {gg_label, gender, probability}].
    """
    out = annotate_with_gender_guesser(
        ["John", "Mary", "Hiroshi", "Wei", "Asdfg"],
    )
    assert out["John"]["gg_label"] == "male"
    assert out["John"]["gender"] == "male"
    assert out["John"]["probability"] == 1.0
    # Mary → mostly_female in gender_guesser's dict (it's conservative)
    assert out["Mary"]["gg_label"] == "mostly_female"
    assert out["Mary"]["gender"] == "female"
    assert out["Mary"]["probability"] == 0.7
    assert out["Hiroshi"]["gender"] == "male"
    assert out["Wei"]["gender"] == "unknown"
    assert out["Wei"]["probability"] == 0.0
    assert out["Asdfg"]["gender"] == "unknown"


def test_annotate_with_gender_guesser_dedupes_and_handles_empty() -> None:
    """Duplicate names appear once in output; empty / whitespace
    names are skipped (no entry in result dict).
    """
    out = annotate_with_gender_guesser(
        ["John", "John", "", "  ", "Mary"],
    )
    assert set(out.keys()) == {"John", "Mary"}


def test_aggregate_per_author_single_paper() -> None:
    """Author with 1 paper → 1 output row with that paper's fields."""
    # Per-author-paper input: 1 author, 1 paper
    authorships = pa.table({
        "author_id": ["https://openalex.org/A1"],
        "publication_year": [2020],
        "author_first_name": ["John"],
        "first_name_is_initial": [False],
        "author_orcid": ["https://orcid.org/0000-1"],
        "countries": [["US"]],
        "source_type": ["journal"],
    })
    name_gender = {"John": {
        "gg_label": "male", "gender": "male", "probability": 1.0,
    }}
    result = aggregate_per_author(authorships, name_gender)

    assert result.num_rows == 1
    row = result.to_pylist()[0]
    assert row["author_id"] == "https://openalex.org/A1"
    assert row["author_first_name"] == "John"
    assert row["gender"] == "male"
    assert row["gender_probability"] == 1.0
    assert row["n_papers"] == 1
    assert row["primary_country"] == "US"
    assert row["n_papers_with_orcid"] == 1


def test_aggregate_per_author_multi_paper_picks_mode() -> None:
    """Author with N papers — primary_country = most-common; gender
    derived from author_first_name; n_papers counted.
    """
    authorships = pa.table({
        "author_id": ["https://openalex.org/A1"] * 4,
        "publication_year": [2018, 2019, 2020, 2021],
        "author_first_name": ["Mary", "Mary", "Mary", "Mary"],
        "first_name_is_initial": [False] * 4,
        "author_orcid": [None, None,
                          "https://orcid.org/0000-2",
                          "https://orcid.org/0000-2"],
        "countries": [["US"], ["US"], ["CA"], ["US"]],  # US wins
        "source_type": ["journal"] * 4,
    })
    name_gender = {"Mary": {
        "gg_label": "mostly_female", "gender": "female", "probability": 0.7,
    }}
    result = aggregate_per_author(authorships, name_gender)
    assert result.num_rows == 1
    row = result.to_pylist()[0]
    assert row["author_id"] == "https://openalex.org/A1"
    assert row["gender"] == "female"
    assert row["gender_probability"] == 0.7
    assert row["n_papers"] == 4
    assert row["primary_country"] == "US"
    assert row["n_papers_with_orcid"] == 2


def test_aggregate_per_author_unknown_name_yields_unknown_gender() -> None:
    """Author with first name not in name_gender dict → gender='unknown'."""
    authorships = pa.table({
        "author_id": ["https://openalex.org/A1"],
        "publication_year": [2020],
        "author_first_name": ["Xyzzy"],
        "first_name_is_initial": [False],
        "author_orcid": [None],
        "countries": [[]],
        "source_type": ["journal"],
    })
    result = aggregate_per_author(authorships, {})
    row = result.to_pylist()[0]
    assert row["gender"] == "unknown"
    assert row["gender_probability"] == 0.0
    assert row["primary_country"] is None  # empty countries → None


def test_annotate_gender_country_e2e(tmp_path: Path) -> None:
    """End-to-end: write a per-author-paper parquet, run
    annotate_gender_country, verify per-author output parquet has
    expected columns + sensible values.
    """
    rows = pa.table({
        "author_id": [
            "https://openalex.org/A1", "https://openalex.org/A1",
            "https://openalex.org/A2",
        ],
        "publication_year": [2019, 2020, 2020],
        "author_first_name": ["John", "John", "Mary"],
        "first_name_is_initial": [False, False, False],
        "author_orcid": [
            "https://orcid.org/0000-1", "https://orcid.org/0000-1", None,
        ],
        "countries": [["US"], ["US"], ["UK"]],
        "source_type": ["journal", "journal", "journal"],
    })
    src = tmp_path / "authorships.parquet"
    pq.write_table(rows, str(src))
    dst = tmp_path / "authors.parquet"

    summary = annotate_gender_country(src, dst)

    assert dst.exists()
    out = pq.read_table(str(dst))
    assert out.num_rows == 2  # 2 unique authors
    assert summary["n_unique_authors"] == 2
    assert summary["n_unique_first_names"] == 2
    # Coverage breakdown
    by_aid = {r["author_id"]: r for r in out.to_pylist()}
    assert by_aid["https://openalex.org/A1"]["gender"] == "male"
    assert by_aid["https://openalex.org/A1"]["primary_country"] == "US"
    assert by_aid["https://openalex.org/A2"]["gender"] == "female"
    assert by_aid["https://openalex.org/A2"]["primary_country"] == "UK"


# ---------- Genderize cross-validation (Step 3b) ----------
#
# All tests mock requests.get to avoid consuming the real 2,500/mo
# free-tier quota. The real Genderize call lives in
# query_genderize_batch; query_genderize orchestrates batching +
# quota tracking; combine_gg_and_genderize fuses gg + Genderize
# outputs per-name.


class _FakeResponse:
    """Minimal stand-in for requests.Response used by tests."""

    def __init__(
        self,
        json_data: Any,
        status_code: int = 200,
        headers: dict[str, str] | None = None,
    ) -> None:
        self._json = json_data
        self.status_code = status_code
        self.headers = headers or {}

    def json(self) -> Any:
        return self._json

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            from requests.exceptions import HTTPError
            raise HTTPError(f"HTTP {self.status_code}")


def test_query_genderize_batch_returns_per_name_dict(monkeypatch: Any) -> None:
    """A successful Genderize call returns {name: {gender, probability,
    count}} per name in the response.
    """
    captured: dict[str, Any] = {}

    def fake_get(url: str, params: dict[str, Any], timeout: float) -> _FakeResponse:
        captured["url"] = url
        captured["params"] = params
        return _FakeResponse([
            {"name": "John", "gender": "male", "probability": 0.99,
             "count": 12345},
            {"name": "Mary", "gender": "female", "probability": 0.98,
             "count": 11000},
        ])

    monkeypatch.setattr("requests.get", fake_get)

    out = query_genderize_batch(["John", "Mary"], api_key="test-key")
    assert out["John"]["gender"] == "male"
    assert out["John"]["probability"] == 0.99
    assert out["John"]["count"] == 12345
    assert out["Mary"]["gender"] == "female"
    assert captured["params"]["name[]"] == ["John", "Mary"]
    assert captured["params"]["apikey"] == "test-key"


def test_query_genderize_batch_handles_unknown_response(monkeypatch: Any) -> None:
    """Genderize returns gender=None for names it can't classify;
    these still get an entry in the output dict (with gender None).
    """
    monkeypatch.setattr(
        "requests.get",
        lambda *a, **kw: _FakeResponse([
            {"name": "Asdfg", "gender": None, "probability": 0.0,
             "count": 0},
        ]),
    )
    out = query_genderize_batch(["Asdfg"], api_key="test-key")
    assert "Asdfg" in out
    assert out["Asdfg"]["gender"] is None
    assert out["Asdfg"]["probability"] == 0.0


def test_query_genderize_orchestrator_batches_10(monkeypatch: Any) -> None:
    """query_genderize batches 10 names per request; n_calls counted.
    25 names → 3 calls (10 + 10 + 5).
    """
    calls: list[list[str]] = []

    def fake_get(url: str, params: dict[str, Any], timeout: float) -> _FakeResponse:
        names = params["name[]"]
        calls.append(names)
        return _FakeResponse([
            {"name": n, "gender": "male", "probability": 0.9, "count": 100}
            for n in names
        ])

    monkeypatch.setattr("requests.get", fake_get)
    names = [f"Name{i}" for i in range(25)]
    out = query_genderize(names, api_key="test-key", max_names=100)

    assert len(calls) == 3
    assert len(calls[0]) == 10
    assert len(calls[1]) == 10
    assert len(calls[2]) == 5
    assert len(out["results"]) == 25
    assert out["n_calls"] == 3
    assert out["n_names_queried"] == 25


def test_query_genderize_respects_max_names_quota(monkeypatch: Any) -> None:
    """Quota cap stops dispatching once max_names is reached.
    100 input names but max_names=25 → only the first 25 are queried."""
    def fake_get(url: str, params: dict[str, Any], timeout: float) -> _FakeResponse:
        return _FakeResponse([
            {"name": n, "gender": "male", "probability": 0.9, "count": 100}
            for n in params["name[]"]
        ])
    monkeypatch.setattr("requests.get", fake_get)

    out = query_genderize(
        [f"Name{i}" for i in range(100)],
        api_key="test-key",
        max_names=25,
    )
    assert out["n_names_queried"] == 25
    assert out["max_names"] == 25
    assert out["quota_exhausted"] is True
    assert len(out["results"]) == 25


def test_query_genderize_handles_api_error_partial(monkeypatch: Any) -> None:
    """If a batch fails mid-orchestration, prior results are kept
    and the failure is surfaced in the summary (no exception)."""
    call_counter = [0]

    def fake_get(url: str, params: dict[str, Any], timeout: float) -> _FakeResponse:
        call_counter[0] += 1
        if call_counter[0] == 2:
            return _FakeResponse({"error": "rate limit"}, status_code=429)
        return _FakeResponse([
            {"name": n, "gender": "male", "probability": 0.9, "count": 100}
            for n in params["name[]"]
        ])

    monkeypatch.setattr("requests.get", fake_get)
    out = query_genderize(
        [f"Name{i}" for i in range(25)],
        api_key="test-key",
        max_names=100,
    )
    # Batch 1 succeeded (10 names), batch 2 failed, batch 3 succeeded (5 names)
    assert len(out["results"]) == 15
    assert out["n_errors"] == 1


def test_combine_gg_and_genderize_both_confident_and_agree() -> None:
    """gg confident male + Genderize confident male → agree, combined male."""
    gg = {"John": {"gg_label": "male", "gender": "male", "probability": 1.0}}
    genderize = {"John": {"gender": "male", "probability": 0.99, "count": 1}}
    combined = combine_gg_and_genderize(gg, genderize)
    assert combined["John"]["combined_gender"] == "male"
    assert combined["John"]["both_methods_confident"] is True
    assert combined["John"]["both_methods_agree"] is True


def test_combine_gg_and_genderize_disagree() -> None:
    """gg male + Genderize female → disagree; combined is the GG result
    (gg is the locked primary per plan §"Gender stack"), but the
    disagreement flag is set so downstream can audit."""
    gg = {"Robin": {"gg_label": "mostly_male", "gender": "male", "probability": 0.7}}
    genderize = {"Robin": {"gender": "female", "probability": 0.8, "count": 100}}
    combined = combine_gg_and_genderize(gg, genderize)
    assert combined["Robin"]["both_methods_confident"] is False  # gg not confident
    assert combined["Robin"]["both_methods_agree"] is False
    # gg's lower-confidence pick still propagates as combined
    assert combined["Robin"]["combined_gender"] == "male"


def test_combine_gg_only() -> None:
    """Name with gg result but no Genderize → combined = gg, agree=None."""
    gg = {"John": {"gg_label": "male", "gender": "male", "probability": 1.0}}
    combined = combine_gg_and_genderize(gg, {})
    assert combined["John"]["combined_gender"] == "male"
    assert combined["John"]["both_methods_confident"] is False  # only gg
    assert combined["John"]["both_methods_agree"] is False
    assert combined["John"]["genderize_gender"] is None


def test_combine_gg_unknown_genderize_confident() -> None:
    """gg unknown + Genderize confident → use Genderize."""
    gg = {"Yiyu": {"gg_label": "unknown", "gender": "unknown",
                    "probability": 0.0}}
    genderize = {"Yiyu": {"gender": "female", "probability": 0.95, "count": 50}}
    combined = combine_gg_and_genderize(gg, genderize)
    assert combined["Yiyu"]["combined_gender"] == "female"
    # When gg is unknown but Genderize is confident, Genderize wins
    assert combined["Yiyu"]["genderize_gender"] == "female"


# ---------- annotate_gender_country with Genderize (Step 3c) ----------


def test_annotate_gender_country_with_genderize_extends_coverage(
    tmp_path: Path,
    monkeypatch: Any,
) -> None:
    """With genderize_api_key provided, gg-unknown names get Genderize
    extension. Verify: gg name "Yiyu" → gg unknown; Genderize returns
    female → per-author table shows gender=female, both_methods_*
    columns present, summary includes Genderize stats."""

    rows = pa.table({
        "author_id": [
            "https://openalex.org/A1", "https://openalex.org/A2",
            "https://openalex.org/A3",
        ],
        "publication_year": [2020, 2020, 2020],
        "author_first_name": ["John", "Yiyu", "Asdfg"],
        "first_name_is_initial": [False, False, False],
        "author_orcid": [None, None, None],
        "countries": [["US"], ["CN"], ["??"]],
        "source_type": ["journal", "journal", "journal"],
    })
    src = tmp_path / "authorships.parquet"
    pq.write_table(rows, str(src))
    dst = tmp_path / "authors.parquet"

    def fake_get(url: str, params: dict[str, Any], timeout: float) -> _FakeResponse:
        # Genderize sees ["Yiyu", "Asdfg"] (gg-unknown names)
        responses = {
            "Yiyu": {"name": "Yiyu", "gender": "female",
                      "probability": 0.95, "count": 50},
            "Asdfg": {"name": "Asdfg", "gender": None,
                       "probability": 0.0, "count": 0},
        }
        return _FakeResponse([
            responses[n] for n in params["name[]"] if n in responses
        ])

    monkeypatch.setattr("requests.get", fake_get)

    summary = annotate_gender_country(
        src, dst,
        genderize_api_key="test-key",
        genderize_max_names=100,
    )

    assert summary["genderize_invoked"] is True
    assert summary["genderize_summary"]["n_calls"] >= 1
    assert summary["genderize_summary"]["n_names_queried"] == 2
    # Yiyu (gg unknown, Genderize confident female) is one extension;
    # Asdfg (Genderize also fails) is not counted.
    assert summary["n_authors_extended_by_genderize"] == 1

    out = pq.read_table(str(dst))
    df = out.to_pandas()
    by_aid = {r["author_id"]: r for r in df.to_dict("records")}

    # John: gg confident male, no Genderize override
    assert by_aid["https://openalex.org/A1"]["gender"] == "male"
    # Yiyu: gg unknown, Genderize confident female → combined = female
    assert by_aid["https://openalex.org/A2"]["gender"] == "female"
    assert (
        by_aid["https://openalex.org/A2"]["genderize_gender"] == "female"
    )
    # Asdfg: gg unknown, Genderize also can't classify → still unknown
    assert by_aid["https://openalex.org/A3"]["gender"] == "unknown"


# ---------- Step 4a: script/region tagging + stratified sampler ----------


def test_tag_script_region_cjk() -> None:
    """CJK characters → cjk."""
    assert tag_script_region("张伟") == "cjk"       # Chinese
    assert tag_script_region("田中") == "cjk"       # Japanese kanji
    assert tag_script_region("김민수") == "cjk"     # Korean Hangul
    assert tag_script_region("ひろし") == "cjk"     # Japanese hiragana


def test_tag_script_region_cyrillic() -> None:
    """Cyrillic → cyrillic."""
    assert tag_script_region("Иван") == "cyrillic"
    assert tag_script_region("Людмила") == "cyrillic"


def test_tag_script_region_arabic() -> None:
    """Arabic → arabic."""
    assert tag_script_region("محمد") == "arabic"
    assert tag_script_region("فاطمة") == "arabic"


def test_tag_script_region_devanagari() -> None:
    """Devanagari → south_asian."""
    assert tag_script_region("राम") == "south_asian"
    assert tag_script_region("प्रिया") == "south_asian"


def test_tag_script_region_latin() -> None:
    """Latin script (incl. transliterations) → latin."""
    assert tag_script_region("John") == "latin"
    assert tag_script_region("Hiroshi") == "latin"      # Romaji
    assert tag_script_region("Yiyu") == "latin"         # Pinyin
    assert tag_script_region("Fenqiang") == "latin"
    assert tag_script_region("Müller") == "latin"       # Latin extended
    assert tag_script_region("Núñez") == "latin"


def test_tag_script_region_handles_empty() -> None:
    """Empty / None / whitespace-only → unknown."""
    assert tag_script_region("") == "unknown"
    assert tag_script_region("   ") == "unknown"
    assert tag_script_region(None) == "unknown"  # type: ignore[arg-type]


def test_stratified_sample_respects_strata_counts() -> None:
    """1000 names across 5 strata, sample 200 → 40 per stratum
    (deterministic by seed; uniform within stratum)."""
    names = []
    for region in ["latin", "cjk", "cyrillic", "arabic", "south_asian"]:
        for i in range(200):
            names.append((f"{region}_{i}", region))
    sample = stratified_sample_names(names, n_total=200, seed="test-seed-v1")

    assert len(sample) == 200
    from collections import Counter
    per_region = Counter(r for _, r in sample)
    # 200/5 = 40 per stratum
    for region in ["latin", "cjk", "cyrillic", "arabic", "south_asian"]:
        assert per_region[region] == 40


def test_stratified_sample_imbalanced_strata() -> None:
    """When some strata have fewer items than the per-stratum target,
    take all of them and over-sample the larger ones (sum-preserving).
    """
    # 1000 latin + 5 cjk + 10 cyrillic; sample 100 total
    names = (
        [(f"latin_{i}", "latin") for i in range(1000)]
        + [(f"cjk_{i}", "cjk") for i in range(5)]
        + [(f"cyr_{i}", "cyrillic") for i in range(10)]
    )
    sample = stratified_sample_names(names, n_total=100, seed="test-seed-v1")
    assert len(sample) == 100
    from collections import Counter
    per = Counter(r for _, r in sample)
    # cjk has only 5 → take all 5
    assert per["cjk"] == 5
    # cyrillic has 10 → take all 10
    assert per["cyrillic"] == 10
    # Remaining 85 go to latin
    assert per["latin"] == 85


def test_stratified_sample_deterministic_with_seed() -> None:
    """Same seed → same sample."""
    names = [(f"n_{i}", "latin") for i in range(100)]
    s1 = stratified_sample_names(names, n_total=20, seed="seed-A")
    s2 = stratified_sample_names(names, n_total=20, seed="seed-A")
    s3 = stratified_sample_names(names, n_total=20, seed="seed-B")
    assert s1 == s2
    assert s1 != s3


def test_stratified_sample_smaller_than_target() -> None:
    """When total population < n_total, return everything."""
    names = [(f"n_{i}", "latin") for i in range(10)]
    sample = stratified_sample_names(names, n_total=100, seed="x")
    assert len(sample) == 10


# ---------- annotate_gender_country without Genderize (Step 3a check) ----


def test_annotate_gender_country_without_genderize_unchanged(
    tmp_path: Path,
) -> None:
    """Without genderize_api_key, behavior matches Step 3a — no
    Genderize call, no genderize_* columns in output, no
    genderize_invoked flag.
    """
    rows = pa.table({
        "author_id": ["https://openalex.org/A1"],
        "publication_year": [2020],
        "author_first_name": ["John"],
        "first_name_is_initial": [False],
        "author_orcid": [None],
        "countries": [["US"]],
        "source_type": ["journal"],
    })
    src = tmp_path / "authorships.parquet"
    pq.write_table(rows, str(src))
    dst = tmp_path / "authors.parquet"

    summary = annotate_gender_country(src, dst)

    assert summary["genderize_invoked"] is False
    assert "genderize_summary" not in summary
    out = pq.read_table(str(dst))
    df = out.to_pandas()
    assert df.iloc[0]["gender"] == "male"
    # genderize_* columns NOT present when Genderize wasn't run
    assert "genderize_gender" not in df.columns


# ---------- Step 4b: NamSor API client ----------


def test_query_namsor_batch_returns_per_name_dict(monkeypatch: Any) -> None:
    """A successful NamSor batch returns {name: {gender, probability,
    score, script}} per requested name."""
    captured: dict[str, Any] = {}

    def fake_post(url: str, headers: dict[str, str],
                  json: dict[str, Any], timeout: float) -> _FakeResponse:
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        return _FakeResponse({
            "personalNames": [
                {"id": "Yiyu", "firstName": "Yiyu", "lastName": "",
                 "script": "LATIN", "likelyGender": "female",
                 "genderScale": 0.27, "score": 1.6,
                 "probabilityCalibrated": 0.64},
                {"id": "Junxu", "firstName": "Junxu", "lastName": "",
                 "script": "LATIN", "likelyGender": "male",
                 "genderScale": -0.87, "score": 7.18,
                 "probabilityCalibrated": 0.94},
            ],
        })

    monkeypatch.setattr("requests.post", fake_post)
    out = query_namsor_batch(["Yiyu", "Junxu"], api_key="test-key")
    assert out["Yiyu"]["gender"] == "female"
    assert out["Yiyu"]["probability"] == 0.64
    assert out["Yiyu"]["script"] == "LATIN"
    assert out["Junxu"]["gender"] == "male"
    assert out["Junxu"]["probability"] == 0.94

    # Request shape: headers carry X-API-KEY, body is genderBatch shape
    assert captured["headers"]["X-API-KEY"] == "test-key"
    assert captured["json"]["personalNames"] == [
        {"id": "Yiyu", "firstName": "Yiyu", "lastName": ""},
        {"id": "Junxu", "firstName": "Junxu", "lastName": ""},
    ]


def test_query_namsor_batch_handles_unknown_gender(monkeypatch: Any) -> None:
    """NamSor can return likelyGender='unknown' for unclassifiable
    names. Keep in dict with gender='unknown'."""
    monkeypatch.setattr(
        "requests.post",
        lambda url, headers, json, timeout: _FakeResponse({
            "personalNames": [{
                "id": "Asdfg", "firstName": "Asdfg",
                "script": "LATIN", "likelyGender": "unknown",
                "genderScale": 0.0, "score": 0.0,
                "probabilityCalibrated": 0.5,
            }],
        }),
    )
    out = query_namsor_batch(["Asdfg"], api_key="test-key")
    assert out["Asdfg"]["gender"] == "unknown"


def test_query_namsor_orchestrator_batches_100(monkeypatch: Any) -> None:
    """query_namsor batches 100 names per request (NamSor's batch limit).
    250 names → 3 calls (100 + 100 + 50)."""
    calls: list[list[str]] = []

    def fake_post(url: str, headers: dict[str, str],
                  json: dict[str, Any], timeout: float) -> _FakeResponse:
        names = [p["firstName"] for p in json["personalNames"]]
        calls.append(names)
        return _FakeResponse({
            "personalNames": [
                {"id": n, "firstName": n, "script": "LATIN",
                 "likelyGender": "male", "probabilityCalibrated": 0.9}
                for n in names
            ],
        })

    monkeypatch.setattr("requests.post", fake_post)
    names = [f"Name{i}" for i in range(250)]
    out = query_namsor(names, api_key="test-key", max_names=2500)

    assert len(calls) == 3
    assert [len(c) for c in calls] == [100, 100, 50]
    assert len(out["results"]) == 250
    assert out["n_calls"] == 3
    assert out["n_names_queried"] == 250


def test_query_namsor_respects_max_names_quota(monkeypatch: Any) -> None:
    """500 input names, max_names=150 → only first 150 queried."""
    monkeypatch.setattr(
        "requests.post",
        lambda url, headers, json, timeout: _FakeResponse({
            "personalNames": [
                {"id": p["firstName"], "firstName": p["firstName"],
                 "script": "LATIN", "likelyGender": "male",
                 "probabilityCalibrated": 0.9}
                for p in json["personalNames"]
            ],
        }),
    )
    out = query_namsor(
        [f"Name{i}" for i in range(500)],
        api_key="test-key", max_names=150,
    )
    assert out["n_names_queried"] == 150
    assert out["quota_exhausted"] is True
    assert len(out["results"]) == 150


# ---------- Step 4c: sample_for_namsor driver ----------


def test_sample_for_namsor_e2e(
    tmp_path: Path, monkeypatch: Any,
) -> None:
    """End-to-end driver: per-author parquet + low-conf identification
    + script-tagged stratified sample + NamSor query + bias-sample
    parquet write.
    """
    # Build a per-author parquet that mimics Step 3c's output. 4 unique
    # authors / 4 unique low-conf names; 2 distinct script regions.
    per_author = pa.table({
        "author_id": [f"https://openalex.org/A{i}" for i in range(4)],
        "author_first_name": ["Yiyu", "Junxu", "Иван", "Магдалена"],
        "gg_label": ["unknown", "unknown", "unknown", "unknown"],
        "gender": ["unknown"] * 4,
        "gender_probability": [0.0] * 4,
        "primary_country": ["CN", "CN", "RU", "BG"],
        "n_papers": [1, 1, 1, 1],
    })
    per_author_path = tmp_path / "per_author.parquet"
    pq.write_table(per_author, str(per_author_path))

    def fake_post(url: str, headers: dict[str, str],
                  json: dict[str, Any], timeout: float) -> _FakeResponse:
        return _FakeResponse({
            "personalNames": [
                {"id": p["firstName"], "firstName": p["firstName"],
                 "script": "LATIN" if not any(
                     ord(c) > 127 for c in p["firstName"]
                 ) else "CYRILLIC",
                 "likelyGender": "female",
                 "probabilityCalibrated": 0.85}
                for p in json["personalNames"]
            ],
        })

    monkeypatch.setattr("requests.post", fake_post)

    out_path = tmp_path / "namsor-sample.parquet"
    summary = sample_for_namsor(
        per_author_path, out_path,
        namsor_api_key="test-key",
        max_names=100,
        seed="test-seed",
    )

    assert out_path.exists()
    tbl = pq.read_table(str(out_path))
    df = tbl.to_pandas()
    # All 4 low-conf names should be sampled (well below n=100 cap)
    assert df.shape[0] == 4
    expected_cols = {
        "first_name", "script_region", "namsor_gender",
        "namsor_probability", "namsor_script",
    }
    assert expected_cols.issubset(set(df.columns))

    # Summary metrics
    assert summary["n_low_conf_names"] == 4
    assert summary["n_sampled"] == 4
    assert summary["n_namsor_classified"] == 4
    assert summary["namsor_summary"]["n_calls"] >= 1
    # Per-region breakdown
    assert "n_sampled_by_region" in summary
    assert summary["n_sampled_by_region"]["latin"] == 2  # Yiyu, Junxu
    assert summary["n_sampled_by_region"]["cyrillic"] == 2  # Иван, Магдалена


def test_sample_for_namsor_respects_quota(
    tmp_path: Path, monkeypatch: Any,
) -> None:
    """With 50 low-conf names and max_names=20, only 20 are sampled
    and sent to NamSor."""
    per_author = pa.table({
        "author_id": [f"https://openalex.org/A{i}" for i in range(50)],
        "author_first_name": [f"Name{i}" for i in range(50)],
        "gg_label": ["unknown"] * 50,
        "gender": ["unknown"] * 50,
        "gender_probability": [0.0] * 50,
        "primary_country": ["US"] * 50,
        "n_papers": [1] * 50,
    })
    pa_path = tmp_path / "pa.parquet"
    pq.write_table(per_author, str(pa_path))

    monkeypatch.setattr(
        "requests.post",
        lambda url, headers, json, timeout: _FakeResponse({
            "personalNames": [
                {"id": p["firstName"], "firstName": p["firstName"],
                 "script": "LATIN", "likelyGender": "male",
                 "probabilityCalibrated": 0.9}
                for p in json["personalNames"]
            ],
        }),
    )

    out = tmp_path / "out.parquet"
    summary = sample_for_namsor(
        pa_path, out, namsor_api_key="k", max_names=20, seed="s",
    )
    assert summary["n_low_conf_names"] == 50
    assert summary["n_sampled"] == 20
    assert summary["n_namsor_classified"] == 20


def test_query_namsor_handles_api_error_partial(monkeypatch: Any) -> None:
    """Transient batch failure → counted in n_errors; subsequent
    batches still succeed; prior results preserved."""
    call_counter = [0]

    def fake_post(url: str, headers: dict[str, str],
                  json: dict[str, Any], timeout: float) -> _FakeResponse:
        call_counter[0] += 1
        if call_counter[0] == 2:
            return _FakeResponse({"error": "rate limit"}, status_code=429)
        names = [p["firstName"] for p in json["personalNames"]]
        return _FakeResponse({
            "personalNames": [
                {"id": n, "firstName": n, "script": "LATIN",
                 "likelyGender": "male", "probabilityCalibrated": 0.9}
                for n in names
            ],
        })

    monkeypatch.setattr("requests.post", fake_post)
    out = query_namsor(
        [f"Name{i}" for i in range(250)],
        api_key="test-key", max_names=2500,
    )
    # Batch 1 (100) + batch 3 (50) succeed; batch 2 (100) fails
    assert len(out["results"]) == 150
    assert out["n_errors"] == 1


# ---------- Step 5a: Wilson CI + per-region confusion matrix ----------


def test_wilson_ci_known_proportions() -> None:
    """Wilson 95% CI matches known textbook values.

    For p=0.5, n=10 (5 successes), Wilson 95% CI is approx
    [0.237, 0.763] — comfortably wider than naive ±1.96*sqrt(p(1-p)/n)
    on small samples.
    """
    low, high = _wilson_ci(k=5, n=10, confidence=0.95)
    assert 0.20 < low < 0.27
    assert 0.73 < high < 0.80

    # 0 of 10 → CI is right-skewed, doesn't include 0 as center
    low, high = _wilson_ci(k=0, n=10, confidence=0.95)
    assert low == 0.0
    assert 0.20 < high < 0.32

    # All 10 of 10 → CI is left-skewed
    low, high = _wilson_ci(k=10, n=10, confidence=0.95)
    assert 0.68 < low < 0.80
    assert high == 1.0


def test_wilson_ci_zero_n() -> None:
    """n=0 → (0, 1) as a safe degenerate band."""
    assert _wilson_ci(k=0, n=0) == (0.0, 1.0)


def test_compute_confusion_matrix_basic_cjk(tmp_path: Path) -> None:
    """3×3 confusion matrix per region with row-normalization + Wilson CIs.

    Build a tiny bias-sample + per-author table covering one region
    (cjk) with 10 names:
      - 4 gg-male: NamSor agrees on 3, says female on 1
      - 2 gg-female: NamSor agrees on both
      - 4 gg-unknown: NamSor says male on 1, female on 3
    """
    # Per-author table (the gg side); first_name → gg_label mapping
    per_author = pa.table({
        "author_id": [f"A{i}" for i in range(10)],
        "author_first_name": [
            "M1", "M2", "M3", "M4",      # gg-male
            "F1", "F2",                  # gg-female
            "U1", "U2", "U3", "U4",      # gg-unknown
        ],
        "gg_label": [
            "male", "male", "male", "male",
            "female", "female",
            "unknown", "unknown", "unknown", "unknown",
        ],
        "gender": [
            "male", "male", "male", "male",
            "female", "female",
            "unknown", "unknown", "unknown", "unknown",
        ],
        "gender_probability": [
            1.0, 1.0, 1.0, 1.0,
            1.0, 1.0,
            0.0, 0.0, 0.0, 0.0,
        ],
    })
    per_author_path = tmp_path / "per_author.parquet"
    pq.write_table(per_author, str(per_author_path))

    # Bias-sample table (the NamSor side)
    bias_sample = pa.table({
        "first_name": ["M1", "M2", "M3", "M4", "F1", "F2",
                        "U1", "U2", "U3", "U4"],
        "script_region": ["cjk"] * 10,
        "namsor_gender": [
            "male", "male", "male", "female",   # 3/4 agree on gg-male
            "female", "female",                 # 2/2 agree on gg-female
            "male", "female", "female", "female",  # gg-unknown → 1M/3F
        ],
        "namsor_probability": [0.9] * 10,
    })
    bias_sample_path = tmp_path / "bias_sample.parquet"
    pq.write_table(bias_sample, str(bias_sample_path))

    result = compute_confusion_matrix(
        bias_sample_parquet=bias_sample_path,
        per_author_parquet=per_author_path,
    )

    assert "cjk" in result
    cjk = result["cjk"]
    assert cjk["n_sample"] == 10

    # Raw counts
    assert cjk["counts"]["male"] == {"male": 3, "female": 1, "unknown": 0}
    assert cjk["counts"]["female"] == {"male": 0, "female": 2, "unknown": 0}
    assert cjk["counts"]["unknown"] == {"male": 1, "female": 3, "unknown": 0}

    # Row-normalized P(NamSor | gg, region)
    assert cjk["row_normalized"]["male"]["male"] == 0.75
    assert cjk["row_normalized"]["male"]["female"] == 0.25
    assert cjk["row_normalized"]["female"]["female"] == 1.0
    assert cjk["row_normalized"]["unknown"]["male"] == 0.25
    assert cjk["row_normalized"]["unknown"]["female"] == 0.75

    # CIs present, structured as (low, high)
    ci = cjk["row_normalized_ci"]["male"]["male"]
    assert isinstance(ci, tuple) and len(ci) == 2
    assert 0.0 <= ci[0] <= ci[1] <= 1.0

    # max_ci_halfwidth = max over all cells of (high-low)/2;
    # small N → wide CIs
    assert cjk["max_ci_halfwidth"] > 0.3  # very wide on n=4 rows
    # And the H5 metric (true measurement at scale would be ≤0.10):
    assert "max_ci_halfwidth" in cjk


def test_compute_confusion_matrix_multi_region(tmp_path: Path) -> None:
    """Multi-region sample → one matrix per region present in bias sample."""
    per_author = pa.table({
        "author_id": ["A1", "A2", "A3"],
        "author_first_name": ["John", "Yiyu", "Иван"],
        "gg_label": ["male", "unknown", "unknown"],
        "gender": ["male", "unknown", "unknown"],
        "gender_probability": [1.0, 0.0, 0.0],
    })
    per_author_path = tmp_path / "pa.parquet"
    pq.write_table(per_author, str(per_author_path))

    bias_sample = pa.table({
        "first_name": ["John", "Yiyu", "Иван"],
        "script_region": ["latin", "latin", "cyrillic"],
        "namsor_gender": ["male", "female", "male"],
        "namsor_probability": [0.95, 0.85, 0.92],
    })
    bias_sample_path = tmp_path / "bs.parquet"
    pq.write_table(bias_sample, str(bias_sample_path))

    result = compute_confusion_matrix(
        bias_sample_parquet=bias_sample_path,
        per_author_parquet=per_author_path,
    )
    assert set(result.keys()) == {"latin", "cyrillic"}
    assert result["latin"]["n_sample"] == 2
    assert result["cyrillic"]["n_sample"] == 1


def test_compute_confusion_matrix_handles_namsor_unknown(
    tmp_path: Path,
) -> None:
    """NamSor's 'unknown' label is a valid column in the matrix."""
    per_author = pa.table({
        "author_id": ["A1", "A2"],
        "author_first_name": ["X", "Y"],
        "gg_label": ["unknown", "unknown"],
        "gender": ["unknown", "unknown"],
        "gender_probability": [0.0, 0.0],
    })
    per_author_path = tmp_path / "pa.parquet"
    pq.write_table(per_author, str(per_author_path))

    bias_sample = pa.table({
        "first_name": ["X", "Y"],
        "script_region": ["latin", "latin"],
        "namsor_gender": ["unknown", "male"],
        "namsor_probability": [0.5, 0.85],
    })
    bias_sample_path = tmp_path / "bs.parquet"
    pq.write_table(bias_sample, str(bias_sample_path))

    result = compute_confusion_matrix(
        bias_sample_parquet=bias_sample_path,
        per_author_parquet=per_author_path,
    )
    assert result["latin"]["counts"]["unknown"]["unknown"] == 1
    assert result["latin"]["counts"]["unknown"]["male"] == 1
    assert result["latin"]["row_normalized"]["unknown"]["unknown"] == 0.5
    assert result["latin"]["row_normalized"]["unknown"]["male"] == 0.5


def test_compute_confusion_matrix_excludes_empty_rows_from_ci(
    tmp_path: Path,
) -> None:
    """max_ci_halfwidth (the H5 metric) ignores structurally-empty gg
    rows. The low-conf bias sample never contains gg-confident names, so
    the gg-male / gg-female rows have zero samples and a degenerate
    (0, 1) Wilson band — those must NOT peg max_ci_halfwidth at 0.5.

    Here the gg-unknown row has 40 well-sampled names (CI half-width well
    under 0.5), while gg-male / gg-female are empty. max_ci_halfwidth
    must reflect only the populated gg-unknown row.
    """
    n = 40
    per_author = pa.table({
        "author_id": [f"A{i}" for i in range(n)],
        "author_first_name": [f"N{i}" for i in range(n)],
        "gg_label": ["unknown"] * n,
        "gender": ["unknown"] * n,
        "gender_probability": [0.0] * n,
    })
    per_author_path = tmp_path / "pa.parquet"
    pq.write_table(per_author, str(per_author_path))

    # 30 male / 10 female NamSor verdicts on the 40 gg-unknown names.
    bias_sample = pa.table({
        "first_name": [f"N{i}" for i in range(n)],
        "script_region": ["latin"] * n,
        "namsor_gender": ["male"] * 30 + ["female"] * 10,
        "namsor_probability": [0.9] * n,
    })
    bias_sample_path = tmp_path / "bs.parquet"
    pq.write_table(bias_sample, str(bias_sample_path))

    result = compute_confusion_matrix(
        bias_sample_parquet=bias_sample_path,
        per_author_parquet=per_author_path,
    )
    latin = result["latin"]
    # gg-male / gg-female rows are empty → their (0,1) bands are excluded.
    assert latin["counts"]["male"] == {"male": 0, "female": 0, "unknown": 0}
    # The H5 metric reflects only the populated gg-unknown row (n=40),
    # whose worst-cell half-width is far below the degenerate 0.5.
    assert latin["max_ci_halfwidth"] < 0.2


def test_compute_confusion_matrix_country_axis(tmp_path: Path) -> None:
    """region_column='primary_country' groups the matrix by each name's
    modal country (joined from per-author) instead of by script.

    This is the per-country robustness matrix locked for Step 5b. The
    bias sample is per-name and has no country column; the function
    attaches each name's modal ``primary_country`` from the per-author
    table before grouping.
    """
    per_author = pa.table({
        "author_id": ["A1", "A2", "A3", "A4"],
        "author_first_name": ["Yiyu", "Junxu", "Magda", "Magda"],
        "gg_label": ["unknown", "unknown", "unknown", "unknown"],
        "gender": ["unknown", "unknown", "unknown", "unknown"],
        "gender_probability": [0.0, 0.0, 0.0, 0.0],
        # Magda appears twice: PL twice → modal PL. Yiyu/Junxu → CN.
        "primary_country": ["CN", "CN", "PL", "PL"],
    })
    per_author_path = tmp_path / "pa.parquet"
    pq.write_table(per_author, str(per_author_path))

    bias_sample = pa.table({
        "first_name": ["Yiyu", "Junxu", "Magda"],
        "script_region": ["latin", "latin", "latin"],  # all latin script
        "namsor_gender": ["female", "male", "female"],
        "namsor_probability": [0.85, 0.9, 0.8],
    })
    bias_sample_path = tmp_path / "bs.parquet"
    pq.write_table(bias_sample, str(bias_sample_path))

    result = compute_confusion_matrix(
        bias_sample_parquet=bias_sample_path,
        per_author_parquet=per_author_path,
        region_column="primary_country",
    )
    # Grouped by country, not by script: CN (Yiyu+Junxu) and PL (Magda).
    assert set(result.keys()) == {"CN", "PL"}
    assert result["CN"]["n_sample"] == 2
    assert result["PL"]["n_sample"] == 1
    # CN gg-unknown → NamSor 1 female / 1 male
    assert result["CN"]["counts"]["unknown"]["female"] == 1
    assert result["CN"]["counts"]["unknown"]["male"] == 1


# ---------- Step 5b: per-author bias-correction application ----------


def _make_per_author(
    rows: list[dict[str, Any]],
) -> pa.Table:
    """Build a per-author Arrow table (Step 3c-shaped) for Step 5b tests.

    Each input dict supplies author_first_name / gg_label / gender /
    gender_probability / primary_country; author_id is auto-assigned.
    """
    return pa.table({
        "author_id": [f"https://openalex.org/A{i}" for i in range(len(rows))],
        "author_first_name": [r["author_first_name"] for r in rows],
        "gg_label": [r["gg_label"] for r in rows],
        "gender": [r["gender"] for r in rows],
        "gender_probability": [r["gender_probability"] for r in rows],
        "primary_country": [r.get("primary_country") for r in rows],
    })


def test_apply_bias_correction_confident_identity(tmp_path: Path) -> None:
    """Confident authors (gender_probability >= gate) get the identity
    transform — one-hot on their assigned gender — and are NOT marked
    bias_correction_applied. The confusion matrix is irrelevant for
    them (NamSor never sampled confident names)."""
    per_author = _make_per_author([
        {"author_first_name": "John", "gg_label": "male",
         "gender": "male", "gender_probability": 1.0, "primary_country": "US"},
        {"author_first_name": "Jane", "gg_label": "female",
         "gender": "female", "gender_probability": 1.0,
         "primary_country": "US"},
    ])
    src = tmp_path / "pa.parquet"
    pq.write_table(per_author, str(src))
    dst = tmp_path / "corrected.parquet"

    summary = apply_bias_correction(
        src, dst, confusion_matrix={}, region_axis="script",
    )

    df = pq.read_table(str(dst)).to_pandas()
    by_aid = {r["author_id"]: r for r in df.to_dict("records")}
    john = by_aid["https://openalex.org/A0"]
    jane = by_aid["https://openalex.org/A1"]
    assert john["corrected_p_male"] == 1.0
    assert john["corrected_p_female"] == 0.0
    assert john["corrected_p_unknown"] == 0.0
    assert bool(john["bias_correction_applied"]) is False
    assert jane["corrected_p_female"] == 1.0
    assert jane["corrected_p_male"] == 0.0
    assert bool(jane["bias_correction_applied"]) is False

    assert summary["n_authors"] == 2
    assert summary["n_confident_identity"] == 2
    assert summary["n_low_conf"] == 0
    assert summary["n_bias_corrected"] == 0


def test_apply_bias_correction_low_conf_uses_matrix(tmp_path: Path) -> None:
    """A low-confidence author whose script-region is present in the
    confusion matrix gets the row-normalized P(NamSor | gg, region)
    distribution and bias_correction_applied=True."""
    per_author = _make_per_author([
        {"author_first_name": "张伟", "gg_label": "unknown",
         "gender": "unknown", "gender_probability": 0.0,
         "primary_country": "CN"},
    ])
    src = tmp_path / "pa.parquet"
    pq.write_table(per_author, str(src))
    dst = tmp_path / "corrected.parquet"

    confusion_matrix = {
        "cjk": {
            "row_normalized": {
                "male": {"male": 0.0, "female": 0.0, "unknown": 0.0},
                "female": {"male": 0.0, "female": 0.0, "unknown": 0.0},
                "unknown": {"male": 0.25, "female": 0.75, "unknown": 0.0},
            },
        },
    }

    summary = apply_bias_correction(
        src, dst, confusion_matrix=confusion_matrix, region_axis="script",
    )

    row = pq.read_table(str(dst)).to_pandas().iloc[0]
    assert row["corrected_p_male"] == 0.25
    assert row["corrected_p_female"] == 0.75
    assert row["corrected_p_unknown"] == 0.0
    assert bool(row["bias_correction_applied"]) is True

    assert summary["n_low_conf"] == 1
    assert summary["n_bias_corrected"] == 1
    assert summary["n_corrected_by_region"]["cjk"] == 1


def test_apply_bias_correction_uncorrectable_fallback(tmp_path: Path) -> None:
    """A low-confidence author whose region is absent from the matrix
    falls back to the identity transform (one-hot on assigned gender)
    and is NOT marked bias_correction_applied. A gg-unknown author thus
    stays fully 'unknown' — conservative, no invented inference."""
    per_author = _make_per_author([
        {"author_first_name": "محمد", "gg_label": "unknown",
         "gender": "unknown", "gender_probability": 0.0,
         "primary_country": "SA"},
    ])
    src = tmp_path / "pa.parquet"
    pq.write_table(per_author, str(src))
    dst = tmp_path / "corrected.parquet"

    # Matrix only covers "latin"; the author's region ("arabic") is absent.
    confusion_matrix = {
        "latin": {
            "row_normalized": {
                "unknown": {"male": 0.5, "female": 0.5, "unknown": 0.0},
            },
        },
    }
    summary = apply_bias_correction(
        src, dst, confusion_matrix=confusion_matrix, region_axis="script",
    )
    row = pq.read_table(str(dst)).to_pandas().iloc[0]
    assert row["corrected_p_unknown"] == 1.0
    assert row["corrected_p_male"] == 0.0
    assert row["corrected_p_female"] == 0.0
    assert bool(row["bias_correction_applied"]) is False

    assert summary["n_low_conf"] == 1
    assert summary["n_bias_corrected"] == 0
    assert summary["n_low_conf_uncorrectable"] == 1


def test_apply_bias_correction_country_axis(tmp_path: Path) -> None:
    """region_axis='country' keys the correction on each author's
    primary_country (a per-author attribute) rather than the
    name-derived script-region. Proves the robustness axis works."""
    per_author = _make_per_author([
        # Latin-script name, but country CN — country axis should pick
        # the "CN" matrix row, not the "latin" script row.
        {"author_first_name": "Yiyu", "gg_label": "unknown",
         "gender": "unknown", "gender_probability": 0.0,
         "primary_country": "CN"},
    ])
    src = tmp_path / "pa.parquet"
    pq.write_table(per_author, str(src))
    dst = tmp_path / "corrected.parquet"

    confusion_matrix = {
        "CN": {
            "row_normalized": {
                "unknown": {"male": 0.4, "female": 0.6, "unknown": 0.0},
            },
        },
    }
    summary = apply_bias_correction(
        src, dst, confusion_matrix=confusion_matrix, region_axis="country",
    )
    row = pq.read_table(str(dst)).to_pandas().iloc[0]
    assert row["corrected_p_male"] == 0.4
    assert row["corrected_p_female"] == 0.6
    assert bool(row["bias_correction_applied"]) is True
    assert summary["region_axis"] == "country"
    assert summary["n_bias_corrected"] == 1


def test_apply_bias_correction_preserves_columns_and_sums(
    tmp_path: Path,
) -> None:
    """The corrected parquet keeps the original columns and adds the
    four Step-5b columns; corrected probabilities sum to 1.0 per author
    (so Step 5c expected-count sums are well-formed)."""
    per_author = _make_per_author([
        {"author_first_name": "John", "gg_label": "male",
         "gender": "male", "gender_probability": 1.0, "primary_country": "US"},
        {"author_first_name": "Yiyu", "gg_label": "unknown",
         "gender": "unknown", "gender_probability": 0.0,
         "primary_country": "CN"},
        {"author_first_name": "Zzzz", "gg_label": "unknown",
         "gender": "unknown", "gender_probability": 0.0,
         "primary_country": "XX"},
    ])
    src = tmp_path / "pa.parquet"
    pq.write_table(per_author, str(src))
    dst = tmp_path / "corrected.parquet"

    confusion_matrix = {
        "latin": {
            "row_normalized": {
                "unknown": {"male": 0.3, "female": 0.5, "unknown": 0.2},
            },
        },
    }
    apply_bias_correction(
        src, dst, confusion_matrix=confusion_matrix, region_axis="script",
    )
    df = pq.read_table(str(dst)).to_pandas()

    # Original columns preserved
    for col in ["author_id", "author_first_name", "gender",
                "gender_probability", "primary_country"]:
        assert col in df.columns
    # New Step-5b columns added
    for col in ["corrected_p_male", "corrected_p_female",
                "corrected_p_unknown", "bias_correction_applied"]:
        assert col in df.columns

    # Each author's corrected distribution sums to 1.0
    sums = (
        df["corrected_p_male"]
        + df["corrected_p_female"]
        + df["corrected_p_unknown"]
    )
    assert all(abs(s - 1.0) < 1e-9 for s in sums)
    # John (latin, confident) → identity; Yiyu (latin, low-conf) → corrected;
    # Zzzz (latin, low-conf) → corrected too (same latin row).
    by_name = {r["author_first_name"]: r for r in df.to_dict("records")}
    assert bool(by_name["John"]["bias_correction_applied"]) is False
    assert bool(by_name["Yiyu"]["bias_correction_applied"]) is True
    assert by_name["Yiyu"]["corrected_p_female"] == 0.5


def test_confusion_matrix_then_apply_correction_compose(tmp_path: Path) -> None:
    """End-to-end 5a→5b contract: a confusion matrix built by
    compute_confusion_matrix feeds apply_bias_correction unchanged.

    The script-region keys produced by Step 5a (via the bias sample's
    script_region column) must line up with the per-author regions
    Step 5b recomputes via tag_script_region, so a real pipeline
    composes without an intermediate adapter."""
    per_author = pa.table({
        "author_id": ["A0", "A1", "A2", "A3"],
        "author_first_name": ["John", "张三", "李四", "Wei"],
        "gg_label": ["male", "unknown", "unknown", "unknown"],
        "gender": ["male", "unknown", "unknown", "unknown"],
        "gender_probability": [1.0, 0.0, 0.0, 0.0],
        "primary_country": ["US", "CN", "CN", "CN"],
    })
    per_author_path = tmp_path / "pa.parquet"
    pq.write_table(per_author, str(per_author_path))

    # NamSor side for the 3 low-conf names. script_region must match
    # tag_script_region (Step 4c populates it that way in production).
    bias_sample = pa.table({
        "first_name": ["张三", "李四", "Wei"],
        "script_region": ["cjk", "cjk", "latin"],
        "namsor_gender": ["male", "female", "male"],
        "namsor_probability": [0.9, 0.88, 0.92],
    })
    bias_sample_path = tmp_path / "bs.parquet"
    pq.write_table(bias_sample, str(bias_sample_path))

    matrix = compute_confusion_matrix(
        bias_sample_parquet=bias_sample_path,
        per_author_parquet=per_author_path,
    )
    # cjk gg-unknown → 1 male / 1 female → 0.5 / 0.5
    assert matrix["cjk"]["row_normalized"]["unknown"]["male"] == 0.5
    assert matrix["latin"]["row_normalized"]["unknown"]["male"] == 1.0

    dst = tmp_path / "corrected.parquet"
    summary = apply_bias_correction(
        per_author_path, dst, confusion_matrix=matrix, region_axis="script",
    )
    by_name = {
        r["author_first_name"]: r
        for r in pq.read_table(str(dst)).to_pandas().to_dict("records")
    }
    # John: confident → identity male, not corrected.
    assert by_name["John"]["corrected_p_male"] == 1.0
    assert bool(by_name["John"]["bias_correction_applied"]) is False
    # 张三 / 李四: cjk low-conf → 0.5 / 0.5 from the matrix.
    assert by_name["张三"]["corrected_p_male"] == 0.5
    assert by_name["张三"]["corrected_p_female"] == 0.5
    assert bool(by_name["张三"]["bias_correction_applied"]) is True
    # Wei: latin low-conf → 1.0 male.
    assert by_name["Wei"]["corrected_p_male"] == 1.0
    assert bool(by_name["Wei"]["bias_correction_applied"]) is True

    assert summary["n_confident_identity"] == 1
    assert summary["n_bias_corrected"] == 3
    assert summary["n_corrected_by_region"] == {"cjk": 2, "latin": 1}


# ---------- Step 5c: field extraction + per-cell aggregation ----------

_CS_ID = "https://openalex.org/C41008148"
_PHYS_ID = "https://openalex.org/C121332964"


def _concepts_json(*pairs: tuple[str, float]) -> str:
    """Build a concepts_json string from (concept_id, score) pairs."""
    return json.dumps([{"id": cid, "score": score} for cid, score in pairs])


def test_extract_primary_field_cs_and_physics() -> None:
    """Single-field papers map to that field; cross-disciplinary papers
    take the higher-scoring of the two locked field concepts (argmax)."""
    assert extract_primary_field(_concepts_json((_CS_ID, 0.6))) == "cs"
    assert extract_primary_field(_concepts_json((_PHYS_ID, 0.5))) == "physics"
    # Cross-disciplinary: physics outscores cs → physics
    assert extract_primary_field(
        _concepts_json((_CS_ID, 0.40), (_PHYS_ID, 0.55)),
    ) == "physics"
    # Cross-disciplinary: cs outscores physics → cs
    assert extract_primary_field(
        _concepts_json((_CS_ID, 0.60), (_PHYS_ID, 0.50)),
    ) == "cs"
    # Non-field concepts present alongside cs → still cs
    assert extract_primary_field(
        _concepts_json(("https://openalex.org/C999", 0.9), (_CS_ID, 0.45)),
    ) == "cs"


def test_extract_primary_field_none_and_malformed() -> None:
    """Neither field concept present / malformed input → None."""
    assert extract_primary_field(
        _concepts_json(("https://openalex.org/C999", 0.9)),
    ) is None
    assert extract_primary_field("[]") is None
    assert extract_primary_field("{not json") is None
    assert extract_primary_field(None) is None  # type: ignore[arg-type]
    assert extract_primary_field("") is None


def test_build_paper_field_map(tmp_path: Path) -> None:
    """Stream a synthetic corpus parquet → paper_id→primary_field map."""
    corpus = pa.table({
        "id": [f"https://openalex.org/W{i}" for i in range(4)],
        "concepts_json": [
            _concepts_json((_CS_ID, 0.6)),                  # cs
            _concepts_json((_PHYS_ID, 0.5)),                # physics
            _concepts_json((_CS_ID, 0.4), (_PHYS_ID, 0.7)),  # physics (argmax)
            _concepts_json(("https://openalex.org/C999", 0.9)),  # none → drop
        ],
    })
    src = tmp_path / "corpus.parquet"
    pq.write_table(corpus, str(src))
    dst = tmp_path / "field_map.parquet"

    summary = build_paper_field_map(src, dst, batch_size=2)

    assert summary["n_papers"] == 4
    assert summary["n_cs"] == 1
    assert summary["n_physics"] == 2
    assert summary["n_unassigned"] == 1

    out = pq.read_table(str(dst)).to_pandas()
    field_by_paper = dict(zip(out["paper_id"], out["primary_field"], strict=True))
    assert field_by_paper["https://openalex.org/W0"] == "cs"
    assert field_by_paper["https://openalex.org/W1"] == "physics"
    assert field_by_paper["https://openalex.org/W2"] == "physics"
    # Unassigned paper W3 is absent from the map (inner-join semantics)
    assert "https://openalex.org/W3" not in field_by_paper


def _make_cell_inputs(
    tmp_path: Path,
    *,
    author_paper_rows: list[tuple[str, int | None, str]],
    authors: list[dict[str, Any]],
    paper_field_rows: list[tuple[str, str]],
) -> tuple[Path, Path, Path]:
    """Write the three Step-5c input parquets, return their paths.

    - author_paper_rows: (paper_id, publication_year, author_id)
    - authors: per-author dicts (author_id, author_first_name,
      corrected_p_male/_female/_unknown)
    - paper_field_rows: (paper_id, primary_field)
    """
    ap = pa.table({
        "paper_id": [r[0] for r in author_paper_rows],
        "publication_year": [r[1] for r in author_paper_rows],
        "author_id": [r[2] for r in author_paper_rows],
    })
    ap_path = tmp_path / "authorships.parquet"
    pq.write_table(ap, str(ap_path))

    corr_data: dict[str, Any] = {
        "author_id": [a["author_id"] for a in authors],
        "author_first_name": [a["author_first_name"] for a in authors],
        "corrected_p_male": [a["corrected_p_male"] for a in authors],
        "corrected_p_female": [a["corrected_p_female"] for a in authors],
        "corrected_p_unknown": [a["corrected_p_unknown"] for a in authors],
    }
    # Only add primary_country when a fixture supplies it, so 5c's
    # country-free fixtures keep their original schema.
    if any("primary_country" in a for a in authors):
        corr_data["primary_country"] = [
            a.get("primary_country") for a in authors
        ]
    # Same for min_year (WS2 career-stage): absent unless a fixture supplies it.
    if any("min_year" in a for a in authors):
        corr_data["min_year"] = [a.get("min_year") for a in authors]
    corr = pa.table(corr_data)
    corr_path = tmp_path / "corrected.parquet"
    pq.write_table(corr, str(corr_path))

    fmap = pa.table({
        "paper_id": [r[0] for r in paper_field_rows],
        "primary_field": [r[1] for r in paper_field_rows],
    })
    fmap_path = tmp_path / "field_map.parquet"
    pq.write_table(fmap, str(fmap_path))

    return ap_path, corr_path, fmap_path


def test_build_cell_coverage_table_distinct_vs_appearances(
    tmp_path: Path,
) -> None:
    """An author with two papers in one cell counts ONCE under the
    distinct-authors unit and TWICE under the appearances unit, so the
    two units' summed counts differ by exactly that author's row."""
    ap_path, corr_path, fmap_path = _make_cell_inputs(
        tmp_path,
        author_paper_rows=[
            ("W1", 2020, "A1"),  # John, twice in 2020-cs
            ("W2", 2020, "A1"),
            ("W1", 2020, "A2"),  # Yiyu, once
        ],
        authors=[
            {"author_id": "A1", "author_first_name": "John",
             "corrected_p_male": 1.0, "corrected_p_female": 0.0,
             "corrected_p_unknown": 0.0},
            {"author_id": "A2", "author_first_name": "Yiyu",
             "corrected_p_male": 0.3, "corrected_p_female": 0.5,
             "corrected_p_unknown": 0.2},
        ],
        paper_field_rows=[("W1", "cs"), ("W2", "cs")],
    )
    out_path = tmp_path / "cells.parquet"
    build_cell_coverage_table(
        ap_path, corr_path, fmap_path, out_path, n_bootstrap=200,
    )
    df = pq.read_table(str(out_path)).to_pandas()

    cells = {
        (r["unit"], r["year"], r["field"], r["region"]): r
        for r in df.to_dict("records")
    }
    distinct = cells[("distinct_authors", 2020, "cs", "latin")]
    appear = cells[("appearances", 2020, "cs", "latin")]

    # Distinct: A1 + A2 once each → n=2, male=1.0+0.3=1.3
    assert distinct["n"] == 2
    assert abs(distinct["sum_p_male"] - 1.3) < 1e-9
    assert abs(distinct["sum_p_female"] - 0.5) < 1e-9
    assert abs(distinct["sum_p_unknown"] - 0.2) < 1e-9
    # Appearances: A1 twice + A2 once → n=3, male=1.0+1.0+0.3=2.3
    assert appear["n"] == 3
    assert abs(appear["sum_p_male"] - 2.3) < 1e-9
    assert abs(appear["sum_p_female"] - 0.5) < 1e-9
    assert abs(appear["sum_p_unknown"] - 0.2) < 1e-9


def test_build_cell_coverage_table_routes_year_field_region(
    tmp_path: Path,
) -> None:
    """Papers land in the correct (year, field, region) cell; region is
    the author's script-region, field is the paper's field."""
    ap_path, corr_path, fmap_path = _make_cell_inputs(
        tmp_path,
        author_paper_rows=[
            ("W1", 2020, "A1"),   # John (latin), 2020 cs
            ("W2", 1995, "A2"),   # Иван (cyrillic), 1995 physics
        ],
        authors=[
            {"author_id": "A1", "author_first_name": "John",
             "corrected_p_male": 1.0, "corrected_p_female": 0.0,
             "corrected_p_unknown": 0.0},
            {"author_id": "A2", "author_first_name": "Иван",
             "corrected_p_male": 0.9, "corrected_p_female": 0.05,
             "corrected_p_unknown": 0.05},
        ],
        paper_field_rows=[("W1", "cs"), ("W2", "physics")],
    )
    out_path = tmp_path / "cells.parquet"
    build_cell_coverage_table(
        ap_path, corr_path, fmap_path, out_path, n_bootstrap=200,
    )
    df = pq.read_table(str(out_path)).to_pandas()
    distinct = df[df["unit"] == "distinct_authors"]
    keys = {
        (r["year"], r["field"], r["region"])
        for r in distinct.to_dict("records")
    }
    assert (2020, "cs", "latin") in keys
    assert (1995, "physics", "cyrillic") in keys


def test_build_cell_coverage_table_ci_properties(tmp_path: Path) -> None:
    """Every cell's bootstrap CI brackets its point estimate and stays
    within [0, n]; output carries the expected columns."""
    ap_path, corr_path, fmap_path = _make_cell_inputs(
        tmp_path,
        author_paper_rows=[(f"W{i}", 2020, f"A{i}") for i in range(8)],
        authors=[
            {"author_id": f"A{i}", "author_first_name": f"Name{i}",
             "corrected_p_male": 0.6, "corrected_p_female": 0.3,
             "corrected_p_unknown": 0.1}
            for i in range(8)
        ],
        paper_field_rows=[(f"W{i}", "cs") for i in range(8)],
    )
    out_path = tmp_path / "cells.parquet"
    build_cell_coverage_table(
        ap_path, corr_path, fmap_path, out_path, n_bootstrap=500,
    )
    df = pq.read_table(str(out_path)).to_pandas()

    expected_cols = {
        "unit", "year", "field", "region", "n",
        "sum_p_male", "sum_p_female", "sum_p_unknown",
        "ci_male_lo", "ci_male_hi", "ci_female_lo", "ci_female_hi",
        "ci_unknown_lo", "ci_unknown_hi",
    }
    assert expected_cols.issubset(set(df.columns))
    # Both units present
    assert set(df["unit"]) == {"distinct_authors", "appearances"}

    for r in df.to_dict("records"):
        n = r["n"]
        for g in ["male", "female", "unknown"]:
            lo, hi, point = r[f"ci_{g}_lo"], r[f"ci_{g}_hi"], r[f"sum_p_{g}"]
            assert lo <= point <= hi
            assert lo >= 0.0
            assert hi <= n + 1e-9


def test_build_cell_coverage_table_deterministic(tmp_path: Path) -> None:
    """Same pinned seed → identical CIs across runs (reproducibility)."""
    args = _make_cell_inputs(
        tmp_path,
        author_paper_rows=[(f"W{i}", 2020, f"A{i}") for i in range(6)],
        authors=[
            {"author_id": f"A{i}", "author_first_name": f"Name{i}",
             "corrected_p_male": 0.5, "corrected_p_female": 0.4,
             "corrected_p_unknown": 0.1}
            for i in range(6)
        ],
        paper_field_rows=[(f"W{i}", "cs") for i in range(6)],
    )
    out1 = tmp_path / "c1.parquet"
    out2 = tmp_path / "c2.parquet"
    build_cell_coverage_table(*args, out1, n_bootstrap=300)
    build_cell_coverage_table(*args, out2, n_bootstrap=300)
    df1 = pq.read_table(str(out1)).to_pandas()
    df2 = pq.read_table(str(out2)).to_pandas()
    assert df1["ci_male_lo"].tolist() == df2["ci_male_lo"].tolist()
    assert df1["ci_male_hi"].tolist() == df2["ci_male_hi"].tolist()


def test_build_cell_coverage_table_no_silent_drops(tmp_path: Path) -> None:
    """A nameless author lands in a region='unknown' cell (not dropped),
    and null-publication_year rows are counted in the summary rather than
    vanishing silently."""
    ap_path, corr_path, fmap_path = _make_cell_inputs(
        tmp_path,
        author_paper_rows=[
            ("W1", 2020, "A1"),     # named author, valid year
            ("W2", 2020, "A2"),     # nameless author → region 'unknown'
            ("W3", None, "A1"),     # null year → dropped (counted)
        ],
        authors=[
            {"author_id": "A1", "author_first_name": "John",
             "corrected_p_male": 1.0, "corrected_p_female": 0.0,
             "corrected_p_unknown": 0.0},
            {"author_id": "A2", "author_first_name": None,
             "corrected_p_male": 0.0, "corrected_p_female": 0.0,
             "corrected_p_unknown": 1.0},
        ],
        paper_field_rows=[("W1", "cs"), ("W2", "cs"), ("W3", "cs")],
    )
    out_path = tmp_path / "cells.parquet"
    summary = build_cell_coverage_table(
        ap_path, corr_path, fmap_path, out_path, n_bootstrap=100,
    )
    df = pq.read_table(str(out_path)).to_pandas()
    distinct = df[df["unit"] == "distinct_authors"]
    regions = set(distinct["region"])
    assert "latin" in regions       # John
    assert "unknown" in regions     # nameless A2 — NOT dropped
    # The null-year W3 appearance is reported, not silently lost.
    assert summary["n_dropped_null_year"] == 1


def test_bootstrap_sum_ci_exact_and_analytic_branches() -> None:
    """The hybrid CI helper: true percentile bootstrap for small cells
    (n <= exact_max_n), Gaussian bootstrap-SE for large ones. Both
    bracket the point estimate and respect [0, n] bounds."""
    import numpy as np

    rng = np.random.default_rng(0)
    # Exact branch (n=2 <= exact_max_n=2): values [1, 0] → sum can be 0..2
    point, lo, hi = _bootstrap_sum_ci(
        np.array([1.0, 0.0]), n_bootstrap=500, rng=rng, exact_max_n=2,
    )
    assert point == 1.0
    assert 0.0 <= lo <= 1.0 <= hi <= 2.0

    # Analytic branch (n=5 > exact_max_n=2): varied values, SD>0
    point, lo, hi = _bootstrap_sum_ci(
        np.array([0.0, 0.5, 1.0, 0.5, 0.0]),
        n_bootstrap=500, rng=rng, exact_max_n=2,
    )
    assert point == 2.0
    assert lo < 2.0 < hi
    assert lo >= 0.0
    assert hi <= 5.0

    # Degenerate: all-equal values → zero-width CI at the point
    point, lo, hi = _bootstrap_sum_ci(
        np.array([0.2, 0.2, 0.2, 0.2, 0.2]),
        n_bootstrap=500, rng=rng, exact_max_n=2,
    )
    assert point == lo == hi == 1.0


# ---------- Step 6: coverage table + diversity metrics + sensitivity ----------


def test_shannon_entropy_mm_known_values() -> None:
    """Miller-Madow Shannon entropy (nats) matches Phase 0.1's formula:
    single category → 0; two equal → ln2 + MM term; empty → 0."""
    import numpy as np

    # Single category: H = 0, MM term (k-1)/(2n) = 0
    assert _shannon_entropy_mm(np.array([5.0]), 5.0) == 0.0
    # Two equal categories of 5 each (n=10): H = ln2 ≈ 0.6931;
    # MM term = (2-1)/(2*10) = 0.05 → ≈ 0.7431
    h = _shannon_entropy_mm(np.array([5.0, 5.0]), 10.0)
    assert abs(h - (0.6931 + 0.05)) < 1e-3
    # Degenerate n=0 → 0.0
    assert _shannon_entropy_mm(np.array([0.0]), 0.0) == 0.0


def test_ratio_ci_exact_and_analytic_branches() -> None:
    """Hybrid ratio CI: true resample for small cells, linearization SE
    for large. Both bracket the point estimate and stay within [0, 1]."""
    import numpy as np

    rng = np.random.default_rng(1)
    # Exact branch: coverage-like ratio, num=[1,1,0,0], denom=ones → 0.5
    point, lo, hi = _ratio_ci(
        np.array([1.0, 1.0, 0.0, 0.0]), np.array([1.0, 1.0, 1.0, 1.0]),
        n_bootstrap=500, rng=rng, exact_max_n=4,
    )
    assert point == 0.5
    assert 0.0 <= lo <= 0.5 <= hi <= 1.0

    # Analytic branch (n=5 > exact_max_n=2): constant ratio 0.6 → SE 0
    point, lo, hi = _ratio_ci(
        np.array([0.6, 0.6, 0.6, 0.6, 0.6]), np.array([1.0] * 5),
        n_bootstrap=500, rng=rng, exact_max_n=2,
    )
    assert abs(point - 0.6) < 1e-9
    assert abs(lo - 0.6) < 1e-9 and abs(hi - 0.6) < 1e-9

    # Undefined ratio (zero denom mass) → degenerate (0, 0, 0)
    assert _ratio_ci(
        np.array([0.0, 0.0]), np.array([0.0, 0.0]),
        n_bootstrap=100, rng=rng, exact_max_n=10,
    ) == (0.0, 0.0, 0.0)


def test_build_coverage_table_metrics(tmp_path: Path) -> None:
    """Per-cell gender coverage, female share, and country diversity are
    computed correctly for a known cell."""
    ap_path, corr_path, fmap_path = _make_cell_inputs(
        tmp_path,
        author_paper_rows=[(f"W{i}", 2020, f"A{i}") for i in range(4)],
        authors=[
            # 2 confident male, 1 confident female, 1 unknown
            {"author_id": "A0", "author_first_name": "John",
             "corrected_p_male": 1.0, "corrected_p_female": 0.0,
             "corrected_p_unknown": 0.0, "primary_country": "US"},
            {"author_id": "A1", "author_first_name": "Paul",
             "corrected_p_male": 1.0, "corrected_p_female": 0.0,
             "corrected_p_unknown": 0.0, "primary_country": "GB"},
            {"author_id": "A2", "author_first_name": "Mary",
             "corrected_p_male": 0.0, "corrected_p_female": 1.0,
             "corrected_p_unknown": 0.0, "primary_country": "US"},
            {"author_id": "A3", "author_first_name": "Xyz",
             "corrected_p_male": 0.0, "corrected_p_female": 0.0,
             "corrected_p_unknown": 1.0, "primary_country": None},
        ],
        paper_field_rows=[(f"W{i}", "cs") for i in range(4)],
    )
    out_path = tmp_path / "coverage.parquet"
    build_coverage_table(
        ap_path, corr_path, fmap_path, out_path, n_bootstrap=300,
    )
    df = pq.read_table(str(out_path)).to_pandas()
    cell = df[
        (df["unit"] == "distinct_authors")
        & (df["year"] == 2020) & (df["field"] == "cs")
        & (df["region"] == "latin")
    ].iloc[0]

    assert cell["n"] == 4
    # Gender coverage: 3 of 4 assigned (male/female) → 0.75
    assert abs(cell["gender_coverage_rate"] - 0.75) < 1e-9
    # Female share among assigned: 1 female / 3 assigned → 1/3
    assert abs(cell["female_share"] - (1.0 / 3.0)) < 1e-9
    # gender_shannon over (sum_m=2, sum_f=1): MM-corrected, > 0
    assert cell["gender_shannon"] > 0.0
    # Country: 3 known (US, GB, US), 1 null → coverage 0.75, 2 distinct
    assert abs(cell["country_coverage_rate"] - 0.75) < 1e-9
    assert cell["n_countries"] == 2
    assert cell["country_shannon"] > 0.0
    # H8 quantity present
    assert "female_share_ci_halfwidth" in df.columns
    assert cell["female_share_ci_halfwidth"] >= 0.0


def test_build_coverage_table_both_units_and_ci_bounds(tmp_path: Path) -> None:
    """Output carries both units; every proportion CI brackets its point
    estimate and lies within [0, 1]."""
    ap_path, corr_path, fmap_path = _make_cell_inputs(
        tmp_path,
        author_paper_rows=[("W1", 2020, "A0"), ("W2", 2020, "A0"),
                           ("W1", 2020, "A1")],
        authors=[
            {"author_id": "A0", "author_first_name": "John",
             "corrected_p_male": 0.8, "corrected_p_female": 0.1,
             "corrected_p_unknown": 0.1, "primary_country": "US"},
            {"author_id": "A1", "author_first_name": "Mary",
             "corrected_p_male": 0.2, "corrected_p_female": 0.7,
             "corrected_p_unknown": 0.1, "primary_country": "CA"},
        ],
        paper_field_rows=[("W1", "cs"), ("W2", "cs")],
    )
    out_path = tmp_path / "coverage.parquet"
    build_coverage_table(
        ap_path, corr_path, fmap_path, out_path, n_bootstrap=300,
    )
    df = pq.read_table(str(out_path)).to_pandas()
    assert set(df["unit"]) == {"distinct_authors", "appearances"}
    # A0 twice (appearances) vs once (distinct)
    appear = df[df["unit"] == "appearances"].iloc[0]
    distinct = df[df["unit"] == "distinct_authors"].iloc[0]
    assert appear["n"] == 3
    assert distinct["n"] == 2

    for r in df.to_dict("records"):
        for lo_c, pt_c, hi_c in [
            ("gender_coverage_lo", "gender_coverage_rate", "gender_coverage_hi"),
            ("female_share_lo", "female_share", "female_share_hi"),
        ]:
            assert 0.0 <= r[lo_c] <= r[pt_c] <= r[hi_c] <= 1.0


def test_build_coverage_table_handles_missing_country(tmp_path: Path) -> None:
    """When the corrected parquet has no primary_country column, country
    metrics are null but gender metrics are still produced."""
    ap_path, corr_path, fmap_path = _make_cell_inputs(
        tmp_path,
        author_paper_rows=[("W1", 2020, "A0")],
        authors=[
            # No primary_country key → column absent from corrected parquet
            {"author_id": "A0", "author_first_name": "John",
             "corrected_p_male": 1.0, "corrected_p_female": 0.0,
             "corrected_p_unknown": 0.0},
        ],
        paper_field_rows=[("W1", "cs")],
    )
    out_path = tmp_path / "coverage.parquet"
    build_coverage_table(
        ap_path, corr_path, fmap_path, out_path, n_bootstrap=100,
    )
    df = pq.read_table(str(out_path)).to_pandas()
    cell = df[df["unit"] == "distinct_authors"].iloc[0]
    assert abs(cell["gender_coverage_rate"] - 1.0) < 1e-9
    # Country metrics null/None (or NaN) when the column is absent
    cc = cell["country_coverage_rate"]
    assert cc is None or cc != cc  # None or NaN


def test_career_stage_bin_boundaries() -> None:
    """0-5 / 6-15 / 16+ bins with null/negative → None (WS2)."""
    from whitespace2.demographics import _career_stage_bin

    assert _career_stage_bin(0) == "0-5"
    assert _career_stage_bin(5) == "0-5"
    assert _career_stage_bin(6) == "6-15"
    assert _career_stage_bin(15) == "6-15"
    assert _career_stage_bin(16) == "16+"
    assert _career_stage_bin(40) == "16+"
    assert _career_stage_bin(-1) is None  # paper predates first pub year (glitch)
    assert _career_stage_bin(None) is None
    assert _career_stage_bin(float("nan")) is None


def test_build_coverage_table_career_joint_plurality(tmp_path: Path) -> None:
    """Joint gender × country × career-stage Shannon + Gini-Simpson (WS2).

    Four authors in the 2020-cs-latin cell with known country + min_year.
    The joint (g, country, career-bin) mass distribution is hand-computable:
      (male, US, 0-5): 1.0 (John, cs=2) + 0.2 (Ann, cs=2) = 1.2
      (male, GB, 6-15): 1.0 (Paul, cs=10)
      (female, US, 16+): 1.0 (Mary, cs=20)
      (female, US, 0-5): 0.6 (Ann)
    total 3.8, 4 categories → Gini-Simpson = 1 − Σp² = 0.736842.
    """
    ap_path, corr_path, fmap_path = _make_cell_inputs(
        tmp_path,
        author_paper_rows=[(f"W{i}", 2020, f"A{i}") for i in range(4)],
        authors=[
            {"author_id": "A0", "author_first_name": "John",
             "corrected_p_male": 1.0, "corrected_p_female": 0.0,
             "corrected_p_unknown": 0.0, "primary_country": "US",
             "min_year": 2018},
            {"author_id": "A1", "author_first_name": "Paul",
             "corrected_p_male": 1.0, "corrected_p_female": 0.0,
             "corrected_p_unknown": 0.0, "primary_country": "GB",
             "min_year": 2010},
            {"author_id": "A2", "author_first_name": "Mary",
             "corrected_p_male": 0.0, "corrected_p_female": 1.0,
             "corrected_p_unknown": 0.0, "primary_country": "US",
             "min_year": 2000},
            {"author_id": "A3", "author_first_name": "Ann",
             "corrected_p_male": 0.2, "corrected_p_female": 0.6,
             "corrected_p_unknown": 0.2, "primary_country": "US",
             "min_year": 2018},
        ],
        paper_field_rows=[(f"W{i}", "cs") for i in range(4)],
    )
    out_path = tmp_path / "coverage.parquet"
    build_coverage_table(
        ap_path, corr_path, fmap_path, out_path, n_bootstrap=200,
    )
    df = pq.read_table(str(out_path)).to_pandas()
    cell = df[
        (df["unit"] == "distinct_authors")
        & (df["year"] == 2020) & (df["region"] == "latin")
    ].iloc[0]

    assert cell["n_career_joint_categories"] == 4
    assert abs(cell["career_joint_coverage_rate"] - 1.0) < 1e-9
    assert abs(cell["career_joint_gini_simpson"] - 0.736842105) < 1e-6
    assert cell["career_joint_shannon"] > 0.0
    # Joint (3 axes) is at least as diverse as gender alone.
    assert cell["career_joint_shannon"] > cell["gender_shannon"]


def test_build_coverage_table_career_partial_coverage(tmp_path: Path) -> None:
    """Authors missing country OR min_year drop out of the joint (coverage<1)."""
    ap_path, corr_path, fmap_path = _make_cell_inputs(
        tmp_path,
        author_paper_rows=[(f"W{i}", 2020, f"A{i}") for i in range(3)],
        authors=[
            {"author_id": "A0", "author_first_name": "John",
             "corrected_p_male": 1.0, "corrected_p_female": 0.0,
             "corrected_p_unknown": 0.0, "primary_country": "US",
             "min_year": 2015},
            {"author_id": "A1", "author_first_name": "Paul",
             "corrected_p_male": 1.0, "corrected_p_female": 0.0,
             "corrected_p_unknown": 0.0, "primary_country": None,
             "min_year": 2015},  # missing country → excluded
            {"author_id": "A2", "author_first_name": "Mary",
             "corrected_p_male": 0.0, "corrected_p_female": 1.0,
             "corrected_p_unknown": 0.0, "primary_country": "US",
             "min_year": None},  # missing min_year → excluded
        ],
        paper_field_rows=[(f"W{i}", "cs") for i in range(3)],
    )
    out_path = tmp_path / "coverage.parquet"
    build_coverage_table(
        ap_path, corr_path, fmap_path, out_path, n_bootstrap=100,
    )
    df = pq.read_table(str(out_path)).to_pandas()
    cell = df[(df["unit"] == "distinct_authors") & (df["region"] == "latin")].iloc[0]
    # Only A0 has both country + career → 1 of 3 authors in the joint.
    assert abs(cell["career_joint_coverage_rate"] - (1.0 / 3.0)) < 1e-9
    assert cell["n_career_joint_categories"] == 1


def test_build_coverage_table_career_null_when_no_min_year(tmp_path: Path) -> None:
    """No min_year column → career-joint metrics are null (like missing country)."""
    ap_path, corr_path, fmap_path = _make_cell_inputs(
        tmp_path,
        author_paper_rows=[("W1", 2020, "A0")],
        authors=[
            {"author_id": "A0", "author_first_name": "John",
             "corrected_p_male": 1.0, "corrected_p_female": 0.0,
             "corrected_p_unknown": 0.0, "primary_country": "US"},
        ],
        paper_field_rows=[("W1", "cs")],
    )
    out_path = tmp_path / "coverage.parquet"
    build_coverage_table(
        ap_path, corr_path, fmap_path, out_path, n_bootstrap=100,
    )
    df = pq.read_table(str(out_path)).to_pandas()
    cell = df[df["unit"] == "distinct_authors"].iloc[0]
    cs = cell["career_joint_shannon"]
    assert cs is None or cs != cs  # None or NaN
    # Gender metrics still produced.
    assert abs(cell["gender_coverage_rate"] - 1.0) < 1e-9


def test_perturb_row_normalized_within_ci_and_renormalized() -> None:
    """A perturbed kernel samples each cell within its Wilson CI then
    renormalizes each gg-row to sum to 1; deterministic given a seed."""
    import numpy as np

    matrix = {
        "cjk": {
            "row_normalized": {
                "unknown": {"male": 0.25, "female": 0.75, "unknown": 0.0},
            },
            "row_normalized_ci": {
                "unknown": {
                    "male": (0.10, 0.45), "female": (0.55, 0.90),
                    "unknown": (0.0, 0.20),
                },
            },
        },
    }
    rng = np.random.default_rng(7)
    perturbed = perturb_row_normalized(matrix, rng)
    row = perturbed["cjk"]["row_normalized"]["unknown"]
    # Renormalized → sums to 1
    assert abs(sum(row.values()) - 1.0) < 1e-9
    # Determinism: same seed → same draw
    perturbed2 = perturb_row_normalized(matrix, np.random.default_rng(7))
    assert perturbed2["cjk"]["row_normalized"]["unknown"] == row
    # A different seed generally differs
    perturbed3 = perturb_row_normalized(matrix, np.random.default_rng(8))
    assert perturbed3["cjk"]["row_normalized"]["unknown"] != row


def test_perturb_then_apply_correction_composes(tmp_path: Path) -> None:
    """A perturbed kernel still drives apply_bias_correction (the E2
    sensitivity loop's inner step composes end to end)."""
    import numpy as np

    matrix = {
        "latin": {
            "row_normalized": {
                "unknown": {"male": 0.4, "female": 0.6, "unknown": 0.0},
            },
            "row_normalized_ci": {
                "unknown": {
                    "male": (0.3, 0.5), "female": (0.5, 0.7),
                    "unknown": (0.0, 0.1),
                },
            },
        },
    }
    perturbed = perturb_row_normalized(matrix, np.random.default_rng(3))

    per_author = pa.table({
        "author_id": ["A0"],
        "author_first_name": ["Yiyu"],
        "gg_label": ["unknown"],
        "gender": ["unknown"],
        "gender_probability": [0.0],
        "primary_country": ["CN"],
    })
    src = tmp_path / "pa.parquet"
    pq.write_table(per_author, str(src))
    dst = tmp_path / "corrected.parquet"
    summary = apply_bias_correction(
        src, dst, confusion_matrix=perturbed, region_axis="script",
    )
    assert summary["n_bias_corrected"] == 1
    row = pq.read_table(str(dst)).to_pandas().iloc[0]
    # corrected triple still sums to 1 under the perturbed kernel
    total = (row["corrected_p_male"] + row["corrected_p_female"]
             + row["corrected_p_unknown"])
    assert abs(total - 1.0) < 1e-9
