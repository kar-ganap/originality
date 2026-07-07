"""WS2 Phase 2.4 — the per-capita V-extension (empirical anchor for WS3 Core Claim 6).

The pre-registered instrument is ``whitespace_3/docs/primers/v-extension-empirical-spec.tex``.
This module builds the **data spine** (2.4a): parse the section-0 corpus into a
paper-level panel (team size, subfield, references, authors, ORCID/country), and
invert ``referenced_works`` into the **in-sample forward-citation graph** for the
persistence filter. Measures (off-canon share, atypicality, embeddings) and the panel
regressions come in 2.4b/c.

Data note: reference coverage is ~50% and roughly *stable* over 1970–2024 (0.44–0.62),
so structural measures are computed on the ~450k papers that carry references; the
coverage is time-stable enough not to fabricate a trend, but is logged and controlled.
"""

from __future__ import annotations

import json
from collections.abc import Sequence

import numpy as np
import numpy.typing as npt
import pandas as pd


def parse_authorships(js: str) -> tuple[int, list[str], int, str | None]:
    """From an ``authorships_json`` string return
    ``(team_size, author_ids, n_orcid, first_country)``."""
    auth = json.loads(js) if js else []
    if not isinstance(auth, list):
        return 0, [], 0, None
    author_ids: list[str] = []
    n_orcid = 0
    first_country: str | None = None
    for a in auth:
        aobj = a.get("author") or {}
        aid = aobj.get("id")
        if aid:
            author_ids.append(str(aid))
        if aobj.get("orcid"):
            n_orcid += 1
        if first_country is None:
            countries = a.get("countries") or []
            if countries:
                first_country = str(countries[0])
    return len(auth), author_ids, n_orcid, first_country


def top_subfield(js: str, level: int = 1) -> str | None:
    """Highest-scoring concept at ``level`` (default 1) from ``concepts_json``."""
    con = json.loads(js) if js else []
    if not isinstance(con, list):
        return None
    best: str | None = None
    best_score = -1.0
    for c in con:
        if c.get("level") == level:
            s = float(c.get("score", 0.0))
            if s > best_score:
                best_score, best = s, str(c.get("display_name"))
    return best


def parse_references(js: str) -> list[str]:
    """Referenced work-ids from a ``referenced_works_json`` string."""
    refs = json.loads(js) if js else []
    return [str(r) for r in refs] if isinstance(refs, list) else []


def build_panel(corpus_path: str, base1m_path: str) -> pd.DataFrame:
    """Parse the section-0 corpus into the paper-level panel, joined to the base-1M
    field label (cs/physics) and restricted to the in-window (1970–2024) set.

    Columns: ``paper_id, year, field, team_size, n_refs, subfield, author_ids,
    n_orcid, primary_country, refs``."""
    cols = ["id", "publication_year", "referenced_works_json", "authorships_json", "concepts_json"]
    corpus = pd.read_parquet(corpus_path, columns=cols)
    corpus = corpus[(corpus.publication_year >= 1970) & (corpus.publication_year <= 2024)].copy()

    team, aids, norc, ctry = zip(*corpus["authorships_json"].map(parse_authorships), strict=True)
    refs = corpus["referenced_works_json"].map(parse_references)
    panel = pd.DataFrame({
        "paper_id": corpus["id"].to_numpy(),
        "year": corpus["publication_year"].to_numpy().astype(int),
        "team_size": np.asarray(team, dtype=int),
        "n_refs": refs.map(len).to_numpy(),
        "subfield": corpus["concepts_json"].map(top_subfield).to_numpy(),
        "author_ids": list(aids),
        "n_orcid": np.asarray(norc, dtype=int),
        "primary_country": list(ctry),
        "refs": refs.to_list(),
    })
    field = pd.read_parquet(base1m_path, columns=["paper_id", "field"])
    panel = panel.merge(field, on="paper_id", how="left")
    return panel


def forward_uptake(
    paper_ids: Sequence[str],
    years: Sequence[int],
    refs: Sequence[Sequence[str]],
    window: int = 5,
) -> npt.NDArray[np.int64]:
    """In-sample forward-citation uptake within a ``window``-year post-publication
    span. ``uptake[i]`` = number of in-sample papers that cite paper ``i`` within
    ``[year_i, year_i + window]``. Only citations from papers *inside* the corpus are
    counted (the spec's primary, self-contained persistence signal)."""
    index = {pid: k for k, pid in enumerate(paper_ids)}
    yr = np.asarray(years, dtype=np.int64)
    uptake = np.zeros(len(paper_ids), dtype=np.int64)
    for citer, rlist in enumerate(refs):
        cy = yr[citer]
        for r in rlist:
            j = index.get(r)
            if j is not None and 0 <= cy - yr[j] <= window:
                uptake[j] += 1
    return uptake
