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
from collections import Counter
from collections.abc import Sequence
from typing import Any

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


def off_canon_share(
    years: Sequence[int],
    refs: Sequence[Sequence[str]],
    alpha: float = 0.05,
) -> npt.NDArray[np.float64]:
    """Empirical structural deviance ``1 − γ̂`` per paper (primer Eq 6): the share of a
    paper's references that lie **off** the canon ``K(t_p)``.

    ``K(t)`` = the top-``alpha`` fraction of referenced works by **cumulative**
    reference count as of year ``t`` (no look-ahead). Processing years in order keeps
    each paper scored against the canon it faced. Returns ``NaN`` for papers with no
    references. Higher = more structurally deviant (builds off the shared canon)."""
    years_arr = np.asarray(years, dtype=np.int64)
    order_by_year: dict[int, list[int]] = {}
    per_year_edges: dict[int, Counter[str]] = {}
    for i, (y, rlist) in enumerate(zip(years_arr, refs, strict=True)):
        yi = int(y)
        order_by_year.setdefault(yi, []).append(i)
        c = per_year_edges.setdefault(yi, Counter())
        c.update(rlist)

    out = np.full(len(years_arr), np.nan, dtype=np.float64)
    cum: Counter[str] = Counter()
    for yi in sorted(per_year_edges):
        cum.update(per_year_edges[yi])                       # cumulative up to yi
        counts = np.fromiter(cum.values(), dtype=np.float64, count=len(cum))
        if counts.size:
            # canon = the top-alpha fraction of works by RANK (not a count percentile,
            # which degenerates on the heavy citation tail); thr = the (alpha*D)-th
            # largest cumulative count; ties at thr are all admitted.
            rank = max(1, int(np.ceil(alpha * counts.size)))
            thr = float(np.partition(counts, -rank)[-rank])
        else:
            thr = np.inf
        for i in order_by_year.get(yi, ()):
            rlist = refs[i]
            if len(rlist):  # tolerate list or ndarray (parquet reload gives arrays)
                on = sum(1 for r in rlist if cum.get(r, 0) >= thr)
                out[i] = 1.0 - on / len(rlist)
    return out


def persistence_weight(
    uptake: Sequence[int],
    field: Sequence[str],
    year: Sequence[int],
) -> npt.NDArray[np.float64]:
    """Smooth persistence weight ``s(p) = u / (u + ū_{field,year})`` (the spec's
    within-cell form): a paper counts more the more its forward uptake exceeds the
    (field, year) base rate. Robust to the in-sample graph's sparsity — no hard
    threshold. ``s ∈ [0,1)``; ``0`` when the whole cell is un-cited."""
    df = pd.DataFrame(
        {"u": np.asarray(uptake, dtype=np.float64), "f": list(field), "y": list(year)}
    )
    ubar = df.groupby(["f", "y"])["u"].transform("mean").to_numpy()
    denom = df["u"].to_numpy() + ubar
    with np.errstate(divide="ignore", invalid="ignore"):
        s = np.where(denom > 0, df["u"].to_numpy() / denom, 0.0)
    return s.astype(np.float64)


def reference_atypicality(
    refs: Sequence[Sequence[str]],
    d_min: int = 20,
    min_pairs: int = 3,
) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    """Uzzi-style reference atypicality (embedding-free, canon-free) — captures novel
    *recombination* the off-canon share misses.

    For each pair of a paper's references ``{u,v}``, the co-reference z-score against a
    **degree-preserving null**: with ``deg_w`` = #papers citing ``w`` and ``N`` papers,
    the number ``O_uv`` of papers citing both is hypergeometric with
    ``E = deg_u·deg_v/N`` and ``Var = deg_u·deg_v·(N−deg_u)(N−deg_v)/(N²(N−1))``, so
    ``z = (O−E)/√Var`` (the analytic equivalent of Uzzi's Monte-Carlo reshuffle).
    High ``z`` = conventional (co-cited more than expected); low/negative ``z`` =
    atypical (novel combination). Pairs are restricted to works with ``deg ≥ d_min``
    (rare works give a degenerate ``E≈0``). Returns per-paper ``(median_z, p10_z)``
    (``NaN`` when fewer than ``min_pairs`` common-work pairs). *Structural novelty is
    DECREASING in median_z.*"""
    n = len(refs)
    deg: Counter[str] = Counter()
    for r in refs:
        deg.update({str(x) for x in r})
    vocab: dict[str, int] = {}
    deg_list: list[float] = []
    for w, dw in deg.items():
        if dw >= d_min:
            vocab[w] = len(vocab)
            deg_list.append(float(dw))
    degv = np.asarray(deg_list, dtype=np.float64)
    v_count = len(vocab)

    cooc: Counter[int] = Counter()
    common: list[list[int]] = []
    for r in refs:
        cw = sorted({vocab[str(x)] for x in r if str(x) in vocab})
        common.append(cw)
        for a in range(len(cw)):
            ia = cw[a] * v_count
            for b in range(a + 1, len(cw)):
                cooc[ia + cw[b]] += 1

    nf = float(n)
    med = np.full(n, np.nan, dtype=np.float64)
    p10 = np.full(n, np.nan, dtype=np.float64)
    for k, cw in enumerate(common):
        m = len(cw)
        if m * (m - 1) // 2 < min_pairs:
            continue
        zs: list[float] = []
        for a in range(m):
            ia, du = cw[a], degv[cw[a]]
            for b in range(a + 1, m):
                iv, dv = cw[b], degv[cw[b]]
                obs = cooc[ia * v_count + iv]
                var = du * dv * (nf - du) * (nf - dv) / (nf * nf * (nf - 1.0))
                zs.append((obs - du * dv / nf) / np.sqrt(var) if var > 0 else 0.0)
        med[k] = float(np.median(zs))
        p10[k] = float(np.percentile(zs, 10))
    return med, p10


def panel_year_test(
    outcome: Sequence[float],
    year: Sequence[float],
    field: Sequence[str],
    controls: Sequence[Sequence[float]] = (),
    *,
    n_perm: int = 2000,
    seed: int = 0,
    alpha: float = 0.01,
) -> dict[str, Any]:
    """Paper-level panel: the partial year coefficient of
    ``outcome ~ 1 + year + controls + field-FE`` (the spec's primary estimand — e.g.
    per-paper ``ν^struct`` on year with ``log(team), log(volume)`` controls and field
    fixed effects). Freedman-Lane permutation **within field** (shuffle reduced-model
    residuals) gives the null of the partial year coefficient — the correct test when
    year and controls are collinear (WS2's residual_trend logic, at paper scale via a
    dot-product permutation). Returns the year coefficient, its permutation p-value, the
    **absolute change** over the observed span (magnitude, not a standardized effect —
    the ill-conditioned-σ lesson), the year-vs-controls **VIF**, and ``n``."""
    y = np.asarray(outcome, dtype=np.float64)
    yr = np.asarray(year, dtype=np.float64)
    fld = np.asarray(field)
    ctrls = [np.asarray(c, dtype=np.float64) for c in controls]
    mask = ~(np.isnan(y) | np.isnan(yr))
    for c in ctrls:
        mask &= ~np.isnan(c)
    y, yr, fld = y[mask], yr[mask], fld[mask]
    ctrls = [c[mask] for c in ctrls]
    n = int(y.size)
    if n < len(ctrls) + 3 or float(np.ptp(yr)) == 0.0:
        return {"year_coef": None, "perm_pvalue": None, "abs_change": None,
                "year_vif": None, "n": n, "significant": False}

    codes, fcode = np.unique(fld, return_inverse=True)
    dummies = np.eye(len(codes))[fcode][:, 1:] if len(codes) > 1 else np.empty((n, 0))
    ones = np.ones(n)
    x_full = np.column_stack([ones, yr, *ctrls, dummies])
    x_red = np.column_stack([ones, *ctrls, dummies])
    pinv1 = np.linalg.pinv(x_full)[1]                       # year row of the pseudo-inverse
    year_coef = float(pinv1 @ y)
    beta_red, *_ = np.linalg.lstsq(x_red, y, rcond=None)
    fitted_red = x_red @ beta_red
    resid = y - fitted_red
    base = float(pinv1 @ fitted_red)

    b_yr, *_ = np.linalg.lstsq(x_red, yr, rcond=None)       # VIF of year vs the rest
    ss_res = float(((yr - x_red @ b_yr) ** 2).sum())
    ss_tot = float(((yr - yr.mean()) ** 2).sum())
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    vif = 1.0 / (1.0 - r2) if r2 < 1.0 else float("inf")

    rng = np.random.default_rng(seed)
    groups = [np.where(fcode == g)[0] for g in range(len(codes))]
    rp = resid.copy()
    perm_coefs = np.empty(n_perm, dtype=np.float64)
    for k in range(n_perm):
        for gi in groups:
            rp[gi] = resid[gi][rng.permutation(gi.size)]   # shuffle residuals within field
        perm_coefs[k] = base + float(pinv1 @ rp)
    exceed = int(np.sum(np.abs(perm_coefs - base) >= abs(year_coef - base)))
    perm_p = (1 + exceed) / (n_perm + 1)
    return {
        "year_coef": year_coef,
        "perm_pvalue": float(perm_p),
        "abs_change": float(year_coef * np.ptp(yr)),
        "year_vif": float(vif),
        "n": n,
        "significant": bool(perm_p < alpha),
    }
