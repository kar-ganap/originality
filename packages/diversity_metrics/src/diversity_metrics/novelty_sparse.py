# Lifted verbatim from whitespace_2/src/whitespace2/v_extension.py (Originality WS2) — behaviour-preserving copy.
"""Sparse (CSR) consolidation–disruption index.

``cd_index_csr`` is the ``scipy.sparse`` engine for the same CD arithmetic as
``novelty.cd_index``, scaled to large citation graphs, with optional
forward-citation-window / absolute-year-floor coverage filters.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import numpy.typing as npt


def cd_index_csr(
    indptr: npt.NDArray[np.int64],
    indices: npt.NDArray[np.int32],
    min_citers: int = 3,
    focals: Sequence[int] | None = None,
    cand_cap: int = 500_000,
    year: npt.NDArray[np.int32] | None = None,
    window: int | None = None,
    year_min: int | None = None,
) -> npt.NDArray[np.float64]:
    """Same CD arithmetic as ``cd_index`` but on a **CSR reference graph** (``indptr``/``indices``:
    paper ``e``'s references = ``indices[indptr[e]:indptr[e+1]]``), so it scales to the 24M-paper
    OpenAlex graph without materializing list-of-lists. Citers come from the transposed (CSC) view.
    For focal ``e``: ``support`` = papers citing any of ``e``'s refs (union of the citer-columns of
    ``refs_e``); ``n_j`` = ``|support ∩ citers(e)|``; ``n_i = |citers(e)| − n_j``; ``n_k = |support|
    − n_j − 1`` (``e`` itself cites its refs so it is in ``support`` — the ``−1`` drops it, matching
    ``cd_index``'s ``− {e}``). A ref cited by ``> cand_cap`` papers is a mega-hub ⇒ ``CD≈0`` ⇒
    short-circuit to ``0.0`` (bounds cost). Equivalence to ``cd_index`` is asserted in tests.

    **Coverage-battery filters** (both need ``year``): ``window`` = a **fixed forward-citation
    window** — count only citers/``n_k`` papers with ``year_e ≤ year_c ≤ year_e + window`` (the
    Park-standard equal-observation-window control for the accumulation asymmetry); ``year_min`` =
    an **absolute floor** — count only papers with ``year_c ≥ year_min`` (the born-digital
    well-covered-era cut). Both filter ``citers(e)`` and the ``support``/``n_k`` set; ``e`` stays in
    ``support`` (its own year is in-window/≥floor for a focal that passes), so the ``−1`` holds."""
    from scipy.sparse import csr_matrix

    n = int(indptr.shape[0] - 1)
    rcsr = csr_matrix((np.ones(indices.shape[0], dtype=np.int8), indices, indptr), shape=(n, n))
    rcsc = rcsr.tocsc()
    ci, cp = rcsc.indices, rcsc.indptr   # column e ⇒ citers of e (papers citing e)
    filt = year is not None and (window is not None or year_min is not None)

    def _keep(arr: npt.NDArray[np.int32], ye: int) -> npt.NDArray[np.int32]:
        if not filt or year is None:
            return arr
        ya = year[arr]
        m = np.ones(arr.size, dtype=bool)
        if window is not None:
            m &= (ya >= ye) & (ya <= ye + window)
        if year_min is not None:
            m &= ya >= year_min
        return arr[m]  # type: ignore[no-any-return]

    cd = np.full(n, np.nan, dtype=np.float64)
    for e in (range(n) if focals is None else focals):
        refs_e = indices[indptr[e]:indptr[e + 1]]
        if refs_e.size == 0:
            continue
        ye = int(year[e]) if year is not None else 0
        citers_e = _keep(ci[cp[e]:cp[e + 1]], ye)
        if citers_e.size < min_citers:
            continue
        cand = _keep(np.concatenate([ci[cp[r]:cp[r + 1]] for r in refs_e]), ye)
        if cand.size > cand_cap:
            cd[e] = 0.0
            continue
        support = np.unique(cand)
        n_j = int(np.intersect1d(support, citers_e, assume_unique=True).size)
        n_i = int(citers_e.size) - n_j
        n_k = int(support.size) - n_j - 1
        denom = n_i + n_j + n_k
        if denom > 0:
            cd[e] = (n_i - n_j) / denom
    return cd
