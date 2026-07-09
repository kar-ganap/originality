# Lifted verbatim from whitespace_2/src/whitespace2/v_extension.py (Originality WS2) — behaviour-preserving copy.
"""Novelty / recombination metrics on a citation-reference graph.

  - ``reference_atypicality`` — Uzzi-style co-reference z-score against a
    degree-preserving null (embedding-free, canon-free).
  - ``cd_index`` — Funk–Owen-Smith consolidation–disruption index per paper
    (dense list-of-lists form). See ``novelty_sparse.cd_index_csr`` for the
    scipy.sparse engine that scales to large graphs.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence

import numpy as np
import numpy.typing as npt


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


def cd_index(
    refs: Sequence[Sequence[int]],
    min_citers: int = 3,
    focals: Sequence[int] | None = None,
) -> npt.NDArray[np.float64]:
    """Funk–Owen-Smith **consolidation–disruption** index per paper (Phase-2 bridge — the WS3
    Park-reconciliation data-half). For a focal paper ``e`` with within-panel references
    ``refs[e]`` and citers (papers whose refs include ``e``): ``CD = (n_i − n_j)/(n_i+n_j+n_k)``,
    where ``n_i`` = citers of ``e`` that do NOT cite ``e``'s references (disruptive), ``n_j`` =
    citers that DO (consolidating), ``n_k`` = papers citing ``e``'s references but not ``e``.
    ``CD > 0`` disruptive, ``< 0`` consolidating; ``NaN`` if ``< min_citers`` citers or no refs.
    ``focals`` restricts the O(N²) computation to given indices (others ``NaN``); the citer graph
    is always built from the FULL ``refs`` so a sampled focal's citers/``n_k`` stay exact.

    VENDORED from ``whitespace_3/src/whitespace3/measures.py`` @ commit ``282e09f`` (byte-faithful;
    keep in sync). Applied here to the *within-panel* citation graph (refs crossing the panel
    boundary are truncated — a documented limitation vs Park's full-graph CD)."""
    e_count = len(refs)
    citers: list[list[int]] = [[] for _ in range(e_count)]
    for c in range(e_count):
        for pr in refs[c]:
            citers[pr].append(c)
    cd = np.full(e_count, np.nan, dtype=np.float64)
    for e in (range(e_count) if focals is None else focals):
        refs_e = set(refs[e])
        ce = citers[e]
        if not refs_e or len(ce) < min_citers:
            continue
        n_j = sum(1 for c in ce if refs_e & set(refs[c]))
        n_i = len(ce) - n_j
        citing_refs: set[int] = set()
        for r in refs_e:
            citing_refs.update(citers[r])
        n_k = len(citing_refs - set(ce) - {e})
        denom = n_i + n_j + n_k
        if denom > 0:
            cd[e] = (n_i - n_j) / denom
    return cd
