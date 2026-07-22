"""Rung-0 reachability probe — measurement and gate evaluation.

Everything here is token-free and testable behind a mock client; only :func:`collect_block` touches
the network. The gate is the locked four-condition rule from ``docs/ws1-oss-reasoning-arm.md`` §9.2:

1. ``V_output`` declines **≥20%** vs the matched ablation cell,
2. in **≥3 of 5** task families,
3. one-sided Wilcoxon **p<.05** at **n=10** blocks,
4. guards: ``anchor_alignment`` below the ceiling **and** role differentiation preserved.

Rung 0 is single-round, so the classifier's *level* path is the whole test — there is no trajectory
to fit a slope to. The level+slope co-primary in :mod:`whitespace1.preflight` applies from rung 1.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from itertools import combinations

import numpy as np
from numpy.typing import NDArray
from scipy.stats import wilcoxon

from .client import LLMClient, Usage
from .schedule import Block, render_block
from .stimuli import FAMILIES, ROLES, Family

# ---------------------------------------------------------------------------
# Registered gate constants (design note §9.2, locked 2026-07-21)
# ---------------------------------------------------------------------------
DECLINE_MIN = 0.20  # V_output must fall >=20% vs matched ablation
FAMILIES_MIN = 3  # in >=3 of 5 task families
ALPHA = 0.05  # one-sided Wilcoxon
ALIGNMENT_CEILING = 0.65  # parroting guard (diverse baseline 0.34-0.51; parroting 0.84)
ROLE_MARGIN_TOL = 0.50  # role differentiation may not fall below half its ablation value
MAX_OUTPUT_TOKENS = 120
ACTUATOR_CELLS = ("A", "B")
ABLATION_CELL = "C"


def _unit(matrix: NDArray[np.float64]) -> NDArray[np.float64]:
    m = np.asarray(matrix, dtype=np.float64)
    normed: NDArray[np.float64] = m / np.linalg.norm(m, axis=1, keepdims=True)
    return normed


def mean_pairwise_cosine(vectors: NDArray[np.float64]) -> float:
    """``V_output`` — mean pairwise cosine distance. The primary diversity metric.

    Never use participation-ratio effective dimensionality here: it is exactly scale-invariant and
    therefore blind to uniform contraction, which is what collapse is.
    """
    v = _unit(np.asarray(vectors, dtype=float))
    pairs = list(combinations(range(len(v)), 2))
    if not pairs:
        return 0.0
    return float(np.mean([1.0 - float(np.dot(v[i], v[j])) for i, j in pairs]))


def anchor_alignment(outputs: NDArray[np.float64], cards: NDArray[np.float64]) -> float:
    """Mean cosine of each output to its nearest shown card — the parroting guard.

    A V drop with alignment above :data:`ALIGNMENT_CEILING` is restatement, not conformity.
    """
    o, c = _unit(np.asarray(outputs, float)), _unit(np.asarray(cards, float))
    return float(np.mean(np.max(o @ c.T, axis=1)))


def echo_concentration(outputs: NDArray[np.float64], cards: NDArray[np.float64]) -> float:
    """Concentration of outputs over the shown cards, by nearest-card assignment (Gini).

    The single-round analogue of prior work's multi-round "top-four echo-concentration". **The two
    are not identical** — prior work measured a trend over rounds, this measures a level in one —
    so the H_endogenous / H* ratio it feeds carries that caveat and the definitions must be
    reconciled before the ratio is trusted. See the report's caveat line.
    """
    o, c = _unit(np.asarray(outputs, float)), _unit(np.asarray(cards, float))
    counts = np.bincount(np.argmax(o @ c.T, axis=1), minlength=len(c)).astype(float)
    if counts.sum() == 0:
        return 0.0
    shares = np.sort(counts / counts.sum())
    n = len(shares)
    index = np.arange(1, n + 1)
    return float((2.0 * np.sum(index * shares)) / (n * np.sum(shares)) - (n + 1.0) / n)


def role_margin(outputs: NDArray[np.float64], roles: NDArray[np.float64]) -> float:
    """How strongly each output still expresses **its own** role rather than the others.

    Operationalizes the design's "persona diversity D unchanged" guard. The risk it addresses: if
    the actuator makes agents abandon their roles, V falls because role differentiation collapsed —
    the homogeneous-persona corner — not because of conformity dynamics. Row *i* is scored as
    ``cos(output_i, role_i) - mean_j!=i cos(output_i, role_j)``; a positive, stable margin means
    roles are still being expressed.
    """
    o, r = _unit(np.asarray(outputs, float)), _unit(np.asarray(roles, float))
    sim = o @ r.T
    own = np.diag(sim)
    others = (sim.sum(axis=1) - own) / (sim.shape[1] - 1)
    return float(np.mean(own - others))


@dataclass(frozen=True)
class CellMeasure:
    """Metrics for one (block, cell)."""

    family_id: str
    block_index: int
    cell: str
    v_output: float
    role_margin: float
    anchor_alignment: float | None = None
    echo_concentration: float | None = None
    outputs: tuple[str, ...] = ()


def collect_block(
    client: LLMClient, block: Block, cell: str, *, max_output_tokens: int = MAX_OUTPUT_TOKENS
) -> tuple[list[str], Usage]:
    """The only network-touching function: one cell of one block, all five roles."""
    texts, usage = [], Usage()
    for role_index in range(len(ROLES)):
        completion = client.generate(
            render_block(block, cell, role_index), max_output_tokens=max_output_tokens
        )
        texts.append(completion.text)
        usage = usage + completion.usage
    return texts, usage


def measure_cell(
    client: LLMClient,
    block: Block,
    cell: str,
    outputs: Sequence[str],
    *,
    families: Sequence[Family] = FAMILIES,
) -> CellMeasure:
    """Embed one cell's outputs and compute every metric it supports."""
    family = next(f for f in families if f.task_id == block.family_id)
    out_emb = client.embed(list(outputs))
    role_emb = client.embed([r.descriptor for r in ROLES])

    align = conc = None
    if cell != ABLATION_CELL:
        card_emb = client.embed([family.cards[i].text for i in block.item_order])
        align = anchor_alignment(out_emb, card_emb)
        conc = echo_concentration(out_emb, card_emb)

    return CellMeasure(
        family_id=block.family_id,
        block_index=block.block_index,
        cell=cell,
        v_output=mean_pairwise_cosine(out_emb),
        role_margin=role_margin(out_emb, role_emb),
        anchor_alignment=align,
        echo_concentration=conc,
        outputs=tuple(outputs),
    )


@dataclass(frozen=True)
class FamilyVerdict:
    """Per-(family, actuator) outcome against the gate."""

    family_id: str
    cell: str
    n_blocks: int
    ablation_v: float
    actuator_v: float
    decline: float
    p_value: float
    mean_alignment: float
    role_margin_ratio: float
    mean_concentration: float
    deltas: tuple[float, ...] = ()

    @property
    def margin_ok(self) -> bool:
        return self.decline >= DECLINE_MIN

    @property
    def significant(self) -> bool:
        return self.p_value < ALPHA

    @property
    def guards_ok(self) -> bool:
        return self.mean_alignment < ALIGNMENT_CEILING and self.role_margin_ratio >= ROLE_MARGIN_TOL

    @property
    def parroting(self) -> bool:
        """A large decline achieved by restatement — reportable as an artifact, never a pass."""
        return self.margin_ok and self.mean_alignment >= ALIGNMENT_CEILING

    @property
    def passed(self) -> bool:
        return self.margin_ok and self.significant and self.guards_ok


def _paired_p(deltas: Sequence[float]) -> float:
    """One-sided Wilcoxon, H1: deltas < 0. Returns 1.0 when the test cannot run."""
    d = [x for x in deltas if x != 0.0]
    if len(d) < 1:
        return 1.0
    return float(wilcoxon(d, alternative="less").pvalue)


def evaluate_family(measures: Sequence[CellMeasure], family_id: str, cell: str) -> FamilyVerdict:
    """Pair each actuator block against its own ablation block within the family."""
    by_block = {
        (m.block_index, m.cell): m for m in measures if m.family_id == family_id
    }
    indices = sorted({m.block_index for m in measures if m.family_id == family_id})

    deltas, abl_v, act_v, aligns, margins, concs = [], [], [], [], [], []
    for i in indices:
        actuator, ablation = by_block.get((i, cell)), by_block.get((i, ABLATION_CELL))
        if actuator is None or ablation is None:
            continue
        deltas.append(actuator.v_output - ablation.v_output)
        abl_v.append(ablation.v_output)
        act_v.append(actuator.v_output)
        if actuator.anchor_alignment is not None:
            aligns.append(actuator.anchor_alignment)
        if actuator.echo_concentration is not None:
            concs.append(actuator.echo_concentration)
        if ablation.role_margin != 0.0:
            margins.append(actuator.role_margin / ablation.role_margin)

    mean_abl = float(np.mean(abl_v)) if abl_v else 0.0
    mean_act = float(np.mean(act_v)) if act_v else 0.0
    decline = (mean_abl - mean_act) / mean_abl if mean_abl > 0 else 0.0
    return FamilyVerdict(
        family_id=family_id,
        cell=cell,
        n_blocks=len(deltas),
        ablation_v=mean_abl,
        actuator_v=mean_act,
        decline=decline,
        p_value=_paired_p(deltas),
        mean_alignment=float(np.mean(aligns)) if aligns else 0.0,
        role_margin_ratio=float(np.mean(margins)) if margins else 1.0,
        mean_concentration=float(np.mean(concs)) if concs else 0.0,
        deltas=tuple(deltas),
    )


@dataclass
class Rung0Verdict:
    """The gate result, reported item by item."""

    per_cell: dict[str, list[FamilyVerdict]] = field(default_factory=dict)

    def passing_families(self, cell: str) -> list[str]:
        return [v.family_id for v in self.per_cell.get(cell, []) if v.passed]

    def cell_passed(self, cell: str) -> bool:
        return len(self.passing_families(cell)) >= FAMILIES_MIN

    @property
    def passed(self) -> bool:
        """Reachable if EITHER actuator form clears the bar — form dependence is reported."""
        return any(self.cell_passed(c) for c in self.per_cell)

    @property
    def parroting_flags(self) -> list[FamilyVerdict]:
        return [v for verdicts in self.per_cell.values() for v in verdicts if v.parroting]

    def h_star(self) -> float | None:
        """Concentration at the collapse point — the denominator the earlier null lacks.

        ``None`` when nothing collapsed, which is itself the answer: with no collapse point there is
        no H*, and prior work's endogenous +0.0102 stays uninterpretable.
        """
        passing = [v for verdicts in self.per_cell.values() for v in verdicts if v.passed]
        return float(np.mean([v.mean_concentration for v in passing])) if passing else None


def evaluate(
    measures: Sequence[CellMeasure], *, families: Sequence[Family] = FAMILIES
) -> Rung0Verdict:
    verdict = Rung0Verdict()
    for cell in ACTUATOR_CELLS:
        verdict.per_cell[cell] = [
            evaluate_family(measures, f.task_id, cell) for f in families
        ]
    return verdict


def bootstrap_ci(
    values: Sequence[float], *, n_boot: int = 10_000, seed: int = 0, alpha: float = 0.05
) -> tuple[float, float]:
    """Percentile bootstrap over blocks."""
    if len(values) < 2:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    arr = np.asarray(values, dtype=float)
    means = arr[rng.integers(0, len(arr), size=(n_boot, len(arr)))].mean(axis=1)
    return (
        float(np.percentile(means, 100 * alpha / 2)),
        float(np.percentile(means, 100 * (1 - alpha / 2))),
    )
