"""Rung 4d — the subfield (content / ``τ``) channel: fragmentation as the mechanism.

The primer's deferred *content channel*, built because WS2 Phase 2.4 disconfirmed Core
Claim 6 (`cc:open`): per-capita structural novelty does not *decline* with scale — it
*rises*, and the rise is **cross-subfield** (within a subfield, combination-novelty is
flat; only against the whole field does novelty rise). This module reproduces that
fingerprint from one added structure — **niches that recombine a shared, high-degree
canon** — and shows it coexists with rising canonical concentration (concentrates at the
top, fragments in the middle).

This is a *different substrate* from the attachment DAG of rungs 3–4b (there, ``κ`` acts
on citation geometry; here ``τ`` places content and is ungoverned by ``κ``). ``C`` is the
attachment channel's business; rung 4d owns ``V^struct`` + ``H_global`` + ``K``.

The object (confirmed by prototyping — see ``docs/phases/phase-1-rung4d-subfield-channel-plan.md``
§9; the pre-registered *disjoint-block* mechanism was disconfirmed and replaced):

  * a **shared vocabulary** of elements in a latent content space; popularity
    **accumulates across niches**, so elements gain high global degree (the shared canon);
  * **persistent niches**, each a lens = two poles it characteristically recombines; a
    niche pairs *popular* elements in *its* way — a pairing few niches use, so it is
    globally rare relative to the pieces' popularity (atypical globally, standard locally);
  * **``K = N / m`` niches** (``m`` = agents per niche, the bounded-attention primitive),
    so the field **fragments as it grows** (``N`` up ⇒ ``K`` up).

Measured the faithful way (one corpus, one fixed degree-preserving null, atypicality
regressed on element **birth-time** — the analog of WS2's ``panel_year_test`` on year):
global novelty **rises**, within-niche **flat**, and ``H_global`` (canon concentration)
**rises** alongside. The sign flip is a **crossover** in niche distinctiveness ``bw``
(``bw* ≈ 0.05``): robust for distinct-enough niches, absent for diffuse ones. The claim is
the **sign-structure and the crossover**, not the empirical magnitude (the Uzzi-z is
scale-confounded).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np
import numpy.typing as npt

from .canon import gini


def _validate(
    m: int, generations: int, n0: int, n_growth: int, papers_per_niche: int,
    bw: float, vocab: int, core: int, dim: int,
) -> None:
    if m < 1:
        raise ValueError(f"m must be >= 1, got {m}")
    if generations < 1:
        raise ValueError(f"generations must be >= 1, got {generations}")
    if n0 < m:
        raise ValueError(f"n0 must be >= m (need >=1 niche), got n0={n0}, m={m}")
    if n_growth < 0:
        raise ValueError(f"n_growth must be >= 0, got {n_growth}")
    if papers_per_niche < 1:
        raise ValueError(f"papers_per_niche must be >= 1, got {papers_per_niche}")
    if not 0.0 < bw <= 1.0:
        raise ValueError(f"bw must be in (0, 1], got {bw}")
    if vocab < 10:
        raise ValueError(f"vocab must be >= 10, got {vocab}")
    if not 5 <= core <= vocab:
        raise ValueError(f"core must be in [5, vocab], got core={core}, vocab={vocab}")
    if dim < 1:
        raise ValueError(f"dim must be >= 1, got {dim}")


def run(
    m: int,
    generations: int,
    seed: int,
    *,
    n0: int = 10,
    n_growth: int = 4,
    papers_per_niche: int = 3,
    bw: float = 0.03,
    vocab: int = 300,
    core: int = 30,
    dim: int = 1,
    fragmentation: bool = True,
) -> dict[str, Any]:
    """Simulate a growing field whose niches recombine a shared canon.

    ``N(t) = n0 + n_growth·t`` agents ⇒ ``K(t) = N(t) // m`` niches (``fragmentation=False``
    freezes ``K`` at ``n0 // m`` — the placebo: the field grows but does not fragment). The
    **vocabulary grows**: ``core`` elements exist from the start (the stable, high-degree
    canon), the rest are born uniformly over the run (fringe; slower than ``K`` so the core
    stays high-degree). Each niche draws ``papers_per_niche`` papers per generation from the
    *live* vocabulary; a paper pairs an element near its left pole with one near its right
    pole, weighted by ``popularity × proximity`` (Gaussian, scale ``bw``); popularity
    accumulates. Deterministic given ``seed``.

    Returns arrays ``niche/u/v/birth`` (one row per paper), the accumulated ``pop`` (degree +
    a 0.1 base), and ``k_traj`` = list of ``(N(t), K(t))``.
    """
    _validate(m, generations, n0, n_growth, papers_per_niche, bw, vocab, core, dim)
    rng = np.random.default_rng(seed)
    epos = rng.random((vocab, dim))                       # element positions in content space
    ebirth = (rng.random(vocab) * generations).astype(np.int64)   # fringe born over the run
    ebirth[:core] = 0                                     # a stable canon core from t=0
    pop = np.full(vocab, 0.1)                             # accumulating global degree
    n_max = n0 + n_growth * generations
    k_max = max(1, n_max // m)
    poles_l = rng.random((k_max, dim))
    poles_r = rng.random((k_max, dim))
    inv2bw2 = 0.5 / (bw * bw)

    niche_l: list[int] = []
    u_l: list[int] = []
    v_l: list[int] = []
    birth_l: list[int] = []
    k_traj: list[tuple[int, int]] = []

    for t in range(generations + 1):
        n_t = n0 + n_growth * t
        k_t = min(k_max, max(1, (n_t if fragmentation else n0) // m))
        k_traj.append((n_t, k_t))
        live = np.nonzero(ebirth <= t)[0]
        if live.size < 5:
            continue
        pos_live = epos[live]
        pop_live = pop[live]
        for c in range(k_t):
            wl = pop_live * np.exp(-inv2bw2 * ((pos_live - poles_l[c]) ** 2).sum(axis=1))
            wr = pop_live * np.exp(-inv2bw2 * ((pos_live - poles_r[c]) ** 2).sum(axis=1))
            sl, sr = wl.sum(), wr.sum()
            if sl <= 0.0 or sr <= 0.0:
                continue
            us = live[rng.choice(live.size, size=papers_per_niche, p=wl / sl)]
            vs = live[rng.choice(live.size, size=papers_per_niche, p=wr / sr)]
            for a, b in zip(us, vs):
                ai, bi = int(a), int(b)
                if ai == bi:
                    continue
                lo, hi = (ai, bi) if ai < bi else (bi, ai)
                niche_l.append(c)
                u_l.append(lo)
                v_l.append(hi)
                birth_l.append(t)
                pop[ai] += 1.0
                pop[bi] += 1.0

    return {
        "niche": np.asarray(niche_l, dtype=np.int64),
        "u": np.asarray(u_l, dtype=np.int64),
        "v": np.asarray(v_l, dtype=np.int64),
        "birth": np.asarray(birth_l, dtype=np.int64),
        "pop": pop,
        "k_traj": k_traj,
        "m": m, "generations": generations, "n0": n0, "n_growth": n_growth,
        "papers_per_niche": papers_per_niche, "bw": bw, "vocab": vocab, "core": core,
        "dim": dim, "fragmentation": fragmentation,
    }


def _frame_slope(
    u: npt.NDArray[np.int64], v: npt.NDArray[np.int64], birth: npt.NDArray[np.int64],
    d_min: int,
) -> tuple[float, int]:
    """Slope of per-paper co-occurrence ``z`` on birth-time, in the frame defined by *these*
    papers (a degree-preserving null built from this subset). ``z < 0`` = atypical/novel;
    a *negative slope* = novelty rises over the run. Vocab restricted to degree ``>= d_min``."""
    n = u.shape[0]
    if n < 30:
        return float("nan"), 0
    deg: dict[int, int] = {}
    pc: dict[tuple[int, int], int] = {}
    for i in range(n):
        ui, vi = int(u[i]), int(v[i])
        deg[ui] = deg.get(ui, 0) + 1
        deg[vi] = deg.get(vi, 0) + 1
        key = (ui, vi)
        pc[key] = pc.get(key, 0) + 1
    bt: list[int] = []
    zz: list[float] = []
    for i in range(n):
        ui, vi = int(u[i]), int(v[i])
        du, dv = deg[ui], deg[vi]
        if du < d_min or dv < d_min:
            continue
        obs = pc[(ui, vi)]
        ex = du * dv / n
        var = du * dv * (n - du) * (n - dv) / (n * n * (n - 1)) if n > 1 else ex
        bt.append(int(birth[i]))
        zz.append((obs - ex) / np.sqrt(var) if var > 1e-12 else 0.0)
    if len(zz) < 30:
        return float("nan"), len(zz)
    return float(np.polyfit(np.asarray(bt, dtype=float), np.asarray(zz), 1)[0]), len(zz)


def global_slope(res: dict[str, Any], d_min: int = 5) -> float:
    """Global-frame atypicality-vs-birth slope (the crux estimand): ``< 0`` ⇒ per-capita
    structural novelty *rises* with scale (the WS2 Phase-2.4 fingerprint)."""
    s, _ = _frame_slope(res["u"], res["v"], res["birth"], d_min)
    return s


def within_slope(res: dict[str, Any], d_min: int = 5, min_papers: int = 50) -> float:
    """Within-niche atypicality-vs-birth slope, averaged over niches (each niche its own
    frame — the within-subfield discriminator): expected ``≈ 0`` (flat)."""
    niche = res["niche"]
    u, v, birth = res["u"], res["v"], res["birth"]
    slopes: list[float] = []
    for c in np.unique(niche):
        mask = niche == c
        if int(mask.sum()) < min_papers:
            continue
        s, _ = _frame_slope(u[mask], v[mask], birth[mask], d_min)
        if not np.isnan(s):
            slopes.append(s)
    return float(np.mean(slopes)) if slopes else float("nan")


def h_global(res: dict[str, Any]) -> float:
    """Canon concentration ``H_global`` = Gini of citation degree over the vocabulary."""
    return gini(np.clip(res["pop"] - 0.1, 0.0, None))


def k_final(res: dict[str, Any]) -> int:
    """Final niche count ``K`` (``= N/m`` under fragmentation)."""
    return int(res["k_traj"][-1][1])


def _boot_ci(vals: Sequence[float], seed: int = 0, n_boot: int = 400) -> tuple[float, float, float]:
    arr = np.asarray([v for v in vals if not np.isnan(v)], dtype=float)
    if arr.size == 0:
        return float("nan"), float("nan"), float("nan")
    if arr.size == 1:
        return float(arr[0]), float(arr[0]), float(arr[0])
    rng = np.random.default_rng(seed)
    means = np.array([float(np.mean(rng.choice(arr, size=arr.size, replace=True)))
                      for _ in range(n_boot)])
    return float(np.mean(arr)), float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def fingerprint(
    m: int, generations: int, seeds: Sequence[int], *, d_min: int = 5, **run_kw: Any,
) -> dict[str, Any]:
    """The rung's top-level estimand: per-seed global/within birth-slopes with a
    seed-bootstrap CI (never a two-point difference), plus mean ``H_global`` and ``K``.
    ``global_slope`` CI excluding 0 below is the confirmed sign-flip."""
    g: list[float] = []
    w: list[float] = []
    h: list[float] = []
    kf: list[int] = []
    for s in seeds:
        res = run(m, generations, s, **run_kw)
        g.append(global_slope(res, d_min))
        w.append(within_slope(res, d_min))
        h.append(h_global(res))
        kf.append(k_final(res))
    gp, glo, ghi = _boot_ci(g)
    wp, wlo, whi = _boot_ci(w)
    return {
        "global_slope": gp, "global_lo": glo, "global_hi": ghi,
        "within_slope": wp, "within_lo": wlo, "within_hi": whi,
        "H_global": float(np.mean(h)), "K": float(np.mean(kf)),
    }
