"""Rung-0 stimulus preflight — the six criteria from ``docs/ws1-oss-rung0-stimuli.md`` §4.

**Thresholds are registered here BEFORE the run** (2026-07-21). They are constants, not tuned
parameters: changing one after seeing a result requires a dated change-log entry, per the design
note's no-post-hoc-constants rule. Embedding- and generation-dependent checks take injected
callables so every criterion is unit-testable without a network call.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from itertools import combinations

import numpy as np
from numpy.typing import NDArray

from .stimuli import FAMILIES, ROLES, Family, render_cell

# ---------------------------------------------------------------------------
# Registered thresholds (pre-run, 2026-07-21)
# ---------------------------------------------------------------------------
CARD_WORDS_MIN = 14
CARD_WORDS_MAX = 24
BRIEF_BALANCE_TOL = 0.15  # briefs within +/-15% of the mean word count
PROMPT_BALANCE_TOL = 0.10  # cell A vs cell B prompt length within +/-10%
CARD_SPREAD_MIN = 0.15  # within-family mean pairwise cosine distance across the 4 cards
CEILING_MIN = 0.35  # ablation pilot V_output floor (calibrated diverse ceiling is ~0.42)

# Words that would leak the manipulation into a brief or card.
BANNED = ("conformity", "diversity", "collapse", "adopted by", "adoption count")

Embedder = Callable[[Sequence[str]], NDArray[np.float64]]
Generator = Callable[[str], str]


@dataclass
class Check:
    name: str
    passed: bool
    detail: str


def _mpcd(vectors: NDArray[np.float64]) -> float:
    """Mean pairwise cosine distance over rows."""
    v = np.asarray(vectors, dtype=float)
    v = v / np.linalg.norm(v, axis=1, keepdims=True)
    pairs = list(combinations(range(len(v)), 2))
    if not pairs:
        return 0.0
    return float(np.mean([1.0 - float(np.dot(v[i], v[j])) for i, j in pairs]))


def check_role_coverage(families: Sequence[Family] = FAMILIES) -> Check:
    """C1 (structural): each brief must name >=3 distinct constraint clauses, so no single role
    monopolizes it. A blinded human read remains the authoritative version of this check."""
    bad = []
    for f in families:
        tail = f.brief.split("Active constraints:", 1)
        clauses = tail[1].count(",") + tail[1].count(";") if len(tail) == 2 else 0
        if len(tail) != 2 or clauses < 2:
            bad.append(f"{f.task_id}(clauses={clauses})")
    return Check(
        "C1 role coverage (structural)",
        not bad,
        "all briefs carry >=3 constraint clauses" if not bad else f"thin: {bad}",
    )


def check_card_spread(embed: Embedder, families: Sequence[Family] = FAMILIES) -> Check:
    """C2: within-family card spread >= CARD_SPREAD_MIN (cards must not be near-duplicates)."""
    rows, fails = [], []
    for f in families:
        d = _mpcd(embed([c.text for c in f.cards]))
        rows.append(f"{f.task_id}={d:.3f}")
        if d < CARD_SPREAD_MIN:
            fails.append(f.task_id)
    return Check(
        f"C2 card spread (>= {CARD_SPREAD_MIN})",
        not fails,
        " ".join(rows) + ("" if not fails else f"  FAIL: {fails}"),
    )


def check_family_separation(embed: Embedder, families: Sequence[Family] = FAMILIES) -> Check:
    """C3: between-family brief distance must exceed mean within-family card distance."""
    between = _mpcd(embed([f.brief for f in families]))
    within = float(np.mean([_mpcd(embed([c.text for c in f.cards])) for f in families]))
    ok = between > within
    return Check(
        "C3 family separation (between-brief > within-card)",
        ok,
        f"between={between:.3f} within={within:.3f}",
    )


def check_length_balance(families: Sequence[Family] = FAMILIES) -> Check:
    """C4: card word counts in range; briefs balanced; cell A vs B prompt lengths balanced."""
    problems = []
    card_words = [len(c.text.split()) for f in families for c in f.cards]
    out_of_range = [w for w in card_words if not CARD_WORDS_MIN <= w <= CARD_WORDS_MAX]
    if out_of_range:
        problems.append(f"cards out of [{CARD_WORDS_MIN},{CARD_WORDS_MAX}]: {out_of_range}")

    bw = [len(f.brief.split()) for f in families]
    mean_bw = float(np.mean(bw))
    if any(abs(w - mean_bw) / mean_bw > BRIEF_BALANCE_TOL for w in bw):
        problems.append(f"briefs unbalanced: {bw} (mean {mean_bw:.1f})")

    for f in families:
        a = len(render_cell(f, "A", ROLES[0]).split())
        b = len(render_cell(f, "B", ROLES[0]).split())
        if abs(a - b) / max(a, b) > PROMPT_BALANCE_TOL:
            problems.append(f"{f.task_id} A/B prompt skew: {a} vs {b}")

    return Check(
        "C4 length balance",
        not problems,
        f"cards {min(card_words)}-{max(card_words)}w, briefs {min(bw)}-{max(bw)}w"
        if not problems
        else "; ".join(problems),
    )


def check_no_leakage(families: Sequence[Family] = FAMILIES) -> Check:
    """C5: manipulation vocabulary must not appear in any brief or card."""
    hits = []
    for f in families:
        blob = (f.brief + " " + " ".join(c.text for c in f.cards)).lower()
        hits += [f"{f.task_id}:{w}" for w in BANNED if w in blob]
    return Check("C5 no leakage", not hits, "clean" if not hits else f"leaked: {hits}")


def check_ceiling_sanity(
    generate: Generator, embed: Embedder, families: Sequence[Family] = FAMILIES
) -> Check:
    """C6: one ablation pilot block per family must land V_output >= CEILING_MIN.

    A family whose ablation V is already low has a floor problem: the rung-0 >=20% margin would be
    measured against the wrong baseline.
    """
    rows, fails = [], []
    for f in families:
        outs = [generate(render_cell(f, "C", r)) for r in ROLES]
        v = _mpcd(embed(outs))
        rows.append(f"{f.task_id}={v:.3f}")
        if v < CEILING_MIN:
            fails.append(f.task_id)
    return Check(
        f"C6 ceiling sanity (ablation V >= {CEILING_MIN})",
        not fails,
        " ".join(rows) + ("" if not fails else f"  FAIL: {fails}"),
    )
