"""Phase 2 (empirical bridge) — measurement functions **vendored from WS2**, so the ABM can
be measured through the *identical* pipeline as the OpenAlex data (Experiment A). Whitespace
independence forbids ambient cross-imports, so we vendor these pure functions with a pin.

VENDORED from ``whitespace_2/src/whitespace2/v_extension.py`` @ commit ``683525e``
(``reference_atypicality``). **Keep in sync:** if the WS2 measure changes, re-copy and bump
the pin. The within-group wrapper mirrors ``experiments/phase-2.4/analyze.py``'s
``within_group_atypicality`` (the fragmentation discriminator).
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence

import numpy as np
import numpy.typing as npt


def reference_atypicality(
    refs: Sequence[Sequence[object]],
    d_min: int = 20,
    min_pairs: int = 3,
) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    """Uzzi-style reference atypicality (embedding-free, canon-free). For each pair of a
    paper's references ``{u,v}``, the co-reference z against a degree-preserving null:
    ``deg_w`` = #papers citing ``w``, ``N`` papers, ``O_uv`` = #papers citing both, hypergeometric
    ``E=deg_u·deg_v/N``, ``Var=deg_u·deg_v·(N−deg_u)(N−deg_v)/(N²(N−1))``, ``z=(O−E)/√Var``.
    High z = conventional; low/negative = atypical. Pairs restricted to works with ``deg≥d_min``.
    Returns per-paper ``(median_z, p10_z)`` (``NaN`` if fewer than ``min_pairs`` common-work
    pairs). *Structural novelty DECREASES in median_z.* (Vendored — do not edit the logic.)"""
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


def within_group_atypicality(
    refs: Sequence[Sequence[object]],
    groups: Sequence[int],
    d_min: int = 20,
    min_pairs: int = 3,
) -> npt.NDArray[np.float64]:
    """Median co-reference z recomputed **within each group's own frame** (the fragmentation
    discriminator): the null is built only from that group's papers. Returns per-paper
    ``median_z`` aligned to ``refs`` (``NaN`` where the paper's group is too small)."""
    out = np.full(len(refs), np.nan, dtype=np.float64)
    grp = np.asarray(groups)
    for g in np.unique(grp):
        idx = np.nonzero(grp == g)[0]
        if idx.size < max(min_pairs + 1, 10):
            continue
        med, _ = reference_atypicality([refs[i] for i in idx], d_min=d_min, min_pairs=min_pairs)
        out[idx] = med
    return out
