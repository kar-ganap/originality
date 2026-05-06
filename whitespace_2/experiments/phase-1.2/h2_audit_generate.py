"""Phase 1.2 H2 hand audit — generate the audit sheet.

Picks 100 papers from a §0 sample (50 uniform random + 50 pre-1990
stratified) and renders them as a Markdown audit sheet for human
review. The reviewer eyeballs each entry checking for:

1. Field plausibility — is this actually a cs / physics paper?
   (concept score≥0.30 already enforced mechanically; the audit
   catches cases where a concept is technically tagged but the
   paper is, e.g., primarily an econ paper that mentioned "ML")
2. Substantive abstract — real prose, not garbled inverted-
   index reconstruction or OCR slop
3. Pre-1990 junk-year tokens — pre-1990 papers shouldn't contain
   post-2000 tokens like "ChatGPT" or "2024"; §0 filters via word-
   boundary regex on a 25-token list, this audit catches misses

Pass criterion: 0 §0-filter false positives in the 100 sampled.

Stratification rationale: uniform 100 would give ~5 pre-1990
papers (4.81% of population). The junk-year filter is the audit's
main concern and benefits from more pre-1990 samples; 50 is
enough for a quick eyeball. Caveat: stratification slightly
deviates from the plan's "random 100"; documented in retro.

Audit-sheet seed is separate from sample / nesting / heldout
seeds (so the audit isn't correlated with sample membership).

Usage:

  # v1 sample (un-type-filtered):
  uv run --with duckdb python experiments/phase-1.2/h2_audit_generate.py

  # v2 sample (type allow-list amendment):
  uv run --with duckdb python experiments/phase-1.2/h2_audit_generate.py \\
      --sample data/metadata/section0-sample-1M-v2.parquet \\
      --out experiments/phase-1.2/h2-audit-sheet-v2.md
"""

from __future__ import annotations

import argparse
from pathlib import Path

import duckdb

import json

_OUT_DIR = Path(__file__).parent
_DATA_METADATA_DIR = _OUT_DIR.parent.parent / "data" / "metadata"
_SAMPLE_PARQUET_DEFAULT = _DATA_METADATA_DIR / "section0-sample-1M.parquet"
_AUDIT_SHEET_DEFAULT = _OUT_DIR / "h2-audit-sheet.md"

_AUDIT_SEED = "ws2-phase-1.2-h2-audit-seed-v1"
_N_UNIFORM = 50
_N_PRE1990 = 50


def _reconstruct_abstract(inverted_json: str | None) -> str:
    """Reconstruct abstract text from OpenAlex's inverted-index format.

    Input shape: ``{"word": [pos, ...], "another": [pos, ...], ...}``.
    Build a position → word map; walk positions in order; join with
    spaces. Gaps (positions with no word) are skipped silently —
    OpenAlex sometimes has them.
    """
    if not inverted_json:
        return "[no abstract]"
    try:
        idx = json.loads(inverted_json)
    except (json.JSONDecodeError, TypeError):
        return "[unparseable abstract_inverted_index_json]"

    pos_to_word: dict[int, str] = {}
    for word, positions in idx.items():
        if not isinstance(positions, list):
            continue
        for p in positions:
            if isinstance(p, int):
                pos_to_word[p] = word

    if not pos_to_word:
        return "[empty inverted index]"

    max_pos = max(pos_to_word.keys())
    words = [pos_to_word.get(i, "") for i in range(max_pos + 1)]
    return " ".join(w for w in words if w)


def _format_concepts(concepts_json: str | None, top_n: int = 5) -> str:
    """Render the top-N concepts as a one-line summary.

    Format: ``computer science (0.85), algorithms (0.65), ...``.
    """
    if not concepts_json:
        return "[no concepts]"
    try:
        concepts = json.loads(concepts_json)
    except (json.JSONDecodeError, TypeError):
        return "[unparseable concepts_json]"
    if not isinstance(concepts, list):
        return "[concepts not a list]"
    # Sort by score desc, take top_n
    sorted_concepts = sorted(
        concepts,
        key=lambda c: -(c.get("score") or 0) if isinstance(c, dict) else 0,
    )
    parts = []
    for c in sorted_concepts[:top_n]:
        if not isinstance(c, dict):
            continue
        name = c.get("display_name") or "?"
        score = c.get("score")
        score_str = f"{score:.2f}" if isinstance(score, (int, float)) else "?"
        parts.append(f"{name} ({score_str})")
    return ", ".join(parts) if parts else "[no parseable concepts]"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sample", type=Path, default=_SAMPLE_PARQUET_DEFAULT,
        help=f"Sample parquet (default: {_SAMPLE_PARQUET_DEFAULT})",
    )
    parser.add_argument(
        "--out", type=Path, default=_AUDIT_SHEET_DEFAULT,
        help=f"Output Markdown sheet (default: {_AUDIT_SHEET_DEFAULT})",
    )
    args = parser.parse_args()

    print("Phase 1.2 H2 hand audit — generating audit sheet")
    print(f"  sample:     {args.sample}")
    print(f"  output:     {args.out}")
    print(f"  uniform N={_N_UNIFORM}; pre-1990 N={_N_PRE1990}")
    print(f"  audit seed: {_AUDIT_SEED}")
    print()

    con = duckdb.connect()

    # 50 uniform random across all years
    print("Drawing 50 uniform-random papers...")
    uniform_rows = con.execute(f"""
        SELECT id, title, publication_year, type,
               abstract_inverted_index_json, concepts_json
        FROM read_parquet('{args.sample}')
        ORDER BY hash('{_AUDIT_SEED}|uniform' || id)
        LIMIT {_N_UNIFORM}
    """).fetchall()
    print(f"  drew {len(uniform_rows)}")

    # 50 random pre-1990
    print("Drawing 50 pre-1990 papers...")
    pre1990_rows = con.execute(f"""
        SELECT id, title, publication_year, type,
               abstract_inverted_index_json, concepts_json
        FROM read_parquet('{args.sample}')
        WHERE publication_year < 1990
        ORDER BY hash('{_AUDIT_SEED}|pre1990' || id)
        LIMIT {_N_PRE1990}
    """).fetchall()
    print(f"  drew {len(pre1990_rows)}")

    con.close()

    all_rows = [(r, "uniform") for r in uniform_rows] + \
               [(r, "pre1990") for r in pre1990_rows]

    # Render Markdown
    lines: list[str] = []
    lines.append("# Phase 1.2 H2 hand audit — sheet")
    lines.append("")
    lines.append(
        f"Generated: 100 papers from `{args.sample.name}`, "
        f"stratified {_N_UNIFORM} uniform + {_N_PRE1990} pre-1990. "
        f"Audit seed: `{_AUDIT_SEED}`."
    )
    lines.append("")
    lines.append("## Reviewer task")
    lines.append("")
    lines.append(
        "For each of the 100 papers below, decide whether §0 was right "
        "to include it. Write one verdict on the `**Verdict:** _____` "
        "line:"
    )
    lines.append("")
    lines.append(
        "- **`OK`** — clearly a research paper in cs or physics with a "
        "real abstract. No further note needed."
    )
    lines.append(
        "- **`FLAG: WRONG_FIELD`** — paper is primarily about something "
        "else (e.g., chemistry, marketing, biology) and only got tagged "
        "as cs/physics because of one or two boilerplate keywords. "
        "Add a short reason."
    )
    lines.append(
        "- **`FLAG: BAD_ABSTRACT`** — the abstract is publisher "
        "boilerplate (citation menu, icon labels, download buttons), "
        "OCR fragments, a stub like \"Abstract not available,\" or "
        "otherwise unusable as a representation of the paper's content."
    )
    lines.append(
        "- **`FLAG: JUNK_YEAR`** — pre-1990 paper that contains a "
        "post-2000 token the regex missed (e.g., \"ChatGPT\", "
        "\"blockchain\", \"transformer architecture\"). Note the "
        "specific token."
    )
    lines.append(
        "- **`FLAG: BORDERLINE`** — you're not sure; note why."
    )
    lines.append("")
    lines.append("**Three things to know going in:**")
    lines.append("")
    lines.append(
        "1. The pass criterion of \"0 FLAGs\" is aspirational. We "
        "expect some FLAGs — the goal is to characterize which "
        "patterns of §0 false positives are common, not to certify "
        "perfection."
    )
    lines.append(
        "2. Multi-field papers (e.g., a real cs paper that also has "
        "bio concepts) are **OK**. The test is whether the paper "
        "genuinely belongs in a cs/physics analytical population, not "
        "whether cs/physics is its only or primary field."
    )
    lines.append(
        "3. If you start seeing the same FLAG pattern repeat (3+ "
        "instances of the same root cause), you can stop reviewing "
        "the rest of that pattern's likely cases and just note "
        "\"pattern X seen ≥3 times; recommend filter Y.\" We're after "
        "kinds of error, not a complete enumeration."
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    for i, (row, stratum) in enumerate(all_rows, start=1):
        paper_id, title, year, ptype, abs_json, concepts_json = row
        # Strip the OpenAlex prefix for terser display
        short_id = paper_id.replace("https://openalex.org/", "")
        title = title or "[no title]"
        title = str(title).strip()
        ptype_str = ptype or "?"

        abstract = _reconstruct_abstract(abs_json)
        concepts_summary = _format_concepts(concepts_json)

        lines.append(f"## {i:>3}. [{short_id}]({paper_id}) — {year} — {ptype_str} — `{stratum}`")
        lines.append("")
        lines.append(f"**Concepts:** {concepts_summary}")
        lines.append("")
        lines.append(f"**Title:** {title}")
        lines.append("")
        lines.append(f"> {abstract}")
        lines.append("")
        lines.append("**Verdict:** _____")
        lines.append("")
        lines.append("---")
        lines.append("")

    args.out.write_text("\n".join(lines))
    print()
    print(f"Wrote {args.out}")
    print(f"Total: {len(all_rows)} papers")


if __name__ == "__main__":
    main()
