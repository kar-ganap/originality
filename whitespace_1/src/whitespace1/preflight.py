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
BRIEF_WORDS_MAX = 30  # open briefs are short; an enumerated checklist is long
CARD_SPREAD_MIN = 0.15  # within-family mean pairwise cosine distance across the 4 cards
CEILING_MIN = 0.35  # ablation V_output floor (calibrated diverse ceiling is ~0.42)
CEILING_BLOCKS = 3  # blocks/family: precision of the estimate, NOT the criterion

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


def check_open_brief(families: Sequence[Family] = FAMILIES) -> Check:
    """C1 (revised 2026-07-21): briefs must state the problem domain WITHOUT enumerating solution
    requirements.

    The first version required >=3 constraint clauses, on the theory that more clauses give the five
    roles more to divide. The pilot showed the opposite: an enumerated checklist hands every agent
    the same answer, and all five roles converged on one proposal (ablation V 0.14-0.24 against a
    ~0.42 calibrated ceiling). Open briefs let each role bring its own lens.
    """
    bad = []
    for f in families:
        n = len(f.brief.split())
        markers = ("active constraints", "must ", "required")
        prescriptive = any(m in f.brief.lower() for m in markers)
        if prescriptive or n > BRIEF_WORDS_MAX:
            bad.append(f"{f.task_id}(words={n}, prescriptive={prescriptive})")
    return Check(
        f"C1 open brief (no enumerated requirements, <= {BRIEF_WORDS_MAX}w)",
        not bad,
        "all briefs open-ended" if not bad else f"over-specified: {bad}",
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
    """C3 (re-specified 2026-07-21): between-family CARD distance must exceed within-family CARD
    distance -- i.e. cards cluster by family.

    The first version compared brief-to-brief against card-to-card. Those are incommensurable: the
    briefs share a deliberately identical stem, so their distance is dominated by boilerplate while
    card distance is dominated by content. That test had no power to discriminate family
    distinctness and could not pass however distinct the families were. Both sides are now
    card-to-card.
    """
    per_family = [
        embed([c.text for c in f.cards]) / np.linalg.norm(
            embed([c.text for c in f.cards]), axis=1, keepdims=True
        )
        for f in families
    ]
    within = float(np.mean([_mpcd(m) for m in per_family]))
    cross = [
        float(np.mean(1.0 - per_family[i] @ per_family[j].T))
        for i in range(len(per_family))
        for j in range(i + 1, len(per_family))
    ]
    between = float(np.mean(cross))
    return Check(
        "C3 family separation (between-card > within-card)",
        between > within,
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
    generate: Generator,
    embed: Embedder,
    families: Sequence[Family] = FAMILIES,
    *,
    n_blocks: int = CEILING_BLOCKS,
) -> Check:
    """C6: the mean ablation V_output over ``n_blocks`` pilot blocks must be >= CEILING_MIN.

    A family whose ablation V is already low has a floor problem: rung 0's >=20% margin would be
    measured against the wrong baseline.

    ``n_blocks`` raises the precision of the estimate; it does **not** move the criterion. A single
    block is too noisy to classify a family, and this check decides whether a family is replaced.
    """
    rows, fails = [], []
    for f in families:
        vs = [
            _mpcd(embed([generate(render_cell(f, "C", r)) for r in ROLES]))
            for _ in range(n_blocks)
        ]
        v = float(np.mean(vs))
        spread = f"[{min(vs):.2f}-{max(vs):.2f}]" if n_blocks > 1 else ""
        rows.append(f"{f.task_id}={v:.3f}{spread}")
        if v < CEILING_MIN:
            fails.append(f.task_id)
    return Check(
        f"C6 ceiling sanity (ablation V >= {CEILING_MIN})",
        not fails,
        " ".join(rows) + ("" if not fails else f"  FAIL: {fails}"),
    )
