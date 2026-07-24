"""Rung-0 v2 — two channels, three instruments, positive-controlled. Measurement + gate.

Implements ``docs/ws1-oss-rung0-v2-prereg.md``. Everything here is token-free and mockable except
skeleton extraction, which takes an injected generator. Diversity metrics, the parroting guard, the
role-margin guard, and the Wilcoxon are reused verbatim from :mod:`whitespace1.rung0` — the v1
measurement was audited and is correct; v2 changes the *design* (cells, channels, instruments), not
the arithmetic.

Cells: ``C0`` ablation · ``CP`` positive control · ``C1/C2/C3`` the instruction-λ sweep.
Channels: ``V_output`` (answers) and ``V_reason`` (reasoning skeletons — the meat, boilerplate
stripped). Instruments per channel: I1 = a fixed embedder, I2 = a second-family embedder, I3 = a
lexical measure; a decline claim requires the sign to agree across all three.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

from .rung0 import ALPHA, _paired_p, anchor_alignment, mean_pairwise_cosine, role_margin

# --- registered constants (design note §9 / v2 pre-reg, locked 2026-07-23) --------------------
DECLINE_MIN = 0.20  # H1: an actuator cell must fall >=20% vs ablation
POS_CONTROL_MIN = 0.30  # H0: the positive control must fall >=30% vs ablation, both channels
FAMILIES_MIN = 3  # H1: in >=3 of 5 families
ALIGNMENT_CEILING = 0.65  # parroting guard on the actuator cells (CP exempt — parrots by design)
ROLE_MARGIN_TOL = 0.50  # role differentiation may not fall below half its ablation value

ABLATION = "C0"
POSITIVE = "CP"
ACTUATOR_CELLS: tuple[str, ...] = ("C1", "C2", "C3")
SKELETON_PROCEDURES: tuple[str, ...] = ("strategy", "decisions")
PRIMARY_PROCEDURE = "strategy"

# Frozen skeleton-extraction prompts (temperature 0). Both discard the task restatement — the smoke
# showed traces open with identical boilerplate that would fake similarity if left in.
SKELETON_PROMPTS: dict[str, str] = {
    "strategy": (
        "Below is a model's private reasoning trace for a feature-proposal task. In 2-3 sentences, "
        "state ONLY the reasoning STRATEGY: the approach taken, the main options weighed, and the "
        "choice made. Do NOT restate the task, the domain, or the options shown to the model. "
        "Reasoning trace:\n\n{trace}"
    ),
    "decisions": (
        "Below is a model's private reasoning trace. List its key decision points as terse bullet "
        "phrases — what was considered and what was chosen — one per line, no preamble. Do NOT "
        "restate the task or the options shown. Reasoning trace:\n\n{trace}"
    ),
}

#: An instrument scores the diversity of a group of texts. I1/I2 embed then take mean pairwise
#: cosine; I3 is lexical. Higher = more diverse, for all three (so signs are comparable).
Instrument = Callable[[Sequence[str]], float]


def distinct_2(texts: Sequence[str]) -> float:
    """I3 — distinct-2: unique bigrams / total bigrams across the group. Lexical, non-semantic.

    Collapses toward 0 as the group repeats itself and toward 1 as it varies, so it moves the same
    direction as the cosine instruments — a shared sign is what the gate checks, not a shared scale.
    """
    bigrams: list[tuple[str, str]] = []
    for t in texts:
        tokens = t.lower().split()
        bigrams.extend(zip(tokens, tokens[1:], strict=False))
    if not bigrams:
        return 0.0
    return len(set(bigrams)) / len(bigrams)


def embed_instrument(embed: Callable[[Sequence[str]], NDArray[np.float64]]) -> Instrument:
    """Wrap an embedder into an instrument: embed the group, take mean pairwise cosine distance."""
    return lambda texts: mean_pairwise_cosine(embed(list(texts)))


def extract_skeletons(
    generate: Callable[[str], str], traces: Sequence[str], procedure: str
) -> list[str]:
    """Extract one skeleton per trace under ``procedure`` (a frozen, temperature-0 prompt)."""
    prompt = SKELETON_PROMPTS[procedure]
    return [generate(prompt.format(trace=t)) for t in traces]


@dataclass(frozen=True)
class CellMeasureV2:
    """All measurements for one (family, block, cell): both channels, every instrument."""

    family_id: str
    block_index: int
    cell: str
    v_output: dict[str, float]  # instrument -> diversity of the answers
    v_reason: dict[str, dict[str, float]]  # procedure -> instrument -> diversity of the skeletons
    anchor_alignment: float  # parroting guard (answers vs shown cards); NaN when no cards shown
    role_margin_ratio: float  # role differentiation vs this family's ablation (filled at eval time)
    answers: tuple[str, ...] = ()
    skeletons: dict[str, tuple[str, ...]] = field(default_factory=dict)


def measure_cell(
    *,
    family_id: str,
    block_index: int,
    cell: str,
    answers: Sequence[str],
    traces: Sequence[str],
    instruments: Sequence[tuple[str, Instrument]],
    extract: Callable[[Sequence[str], str], list[str]],
    embed_fixed: Callable[[Sequence[str]], NDArray[np.float64]],
    card_texts: Sequence[str] | None,
    roles_emb: NDArray[np.float64],
) -> CellMeasureV2:
    """Measure one cell-block. ``extract(traces, procedure)`` returns the skeletons; ``embed_fixed``
    (the I1 embedder) backs the parroting/role guards so those stay on one instrument."""
    skeletons = {p: extract(traces, p) for p in SKELETON_PROCEDURES}
    v_output = {name: fn(answers) for name, fn in instruments}
    v_reason = {
        p: {name: fn(skeletons[p]) for name, fn in instruments}
        for p in SKELETON_PROCEDURES
    }

    out_emb = embed_fixed(list(answers))
    align = float("nan")
    if card_texts:
        align = anchor_alignment(out_emb, embed_fixed(list(card_texts)))
    margin = role_margin(out_emb, roles_emb)  # normalized against ablation in evaluate()

    return CellMeasureV2(
        family_id=family_id,
        block_index=block_index,
        cell=cell,
        v_output=v_output,
        v_reason=v_reason,
        anchor_alignment=align,
        role_margin_ratio=margin,
        answers=tuple(answers),
        skeletons={p: tuple(s) for p, s in skeletons.items()},
    )


def _series(
    measures: Sequence[CellMeasureV2], cell: str, getter: Callable[[CellMeasureV2], float]
) -> dict[int, float]:
    """Per-block values for one cell, keyed by block index."""
    return {m.block_index: getter(m) for m in measures if m.cell == cell}


@dataclass(frozen=True)
class ChannelDecline:
    """One (family, cell, channel) decline vs ablation, with the three-instrument sign check."""

    channel: str
    decline: float  # relative decline on the primary instrument (I1), block-mean
    p_value: float  # one-sided Wilcoxon on the paired per-block I1 deltas
    signs_agree: bool  # do all three instruments show the same sign of decline?
    per_instrument: dict[str, float]  # instrument -> relative decline

    @property
    def significant(self) -> bool:
        return self.p_value < ALPHA

    def collapses(self, threshold: float) -> bool:
        return self.decline >= threshold and self.significant and self.signs_agree


def _channel_decline(
    measures: Sequence[CellMeasureV2],
    cell: str,
    channel: str,
    instrument_names: Sequence[str],
) -> ChannelDecline:
    """Relative decline of ``cell`` vs ablation for ``channel``: per instrument, Wilcoxon on I1."""
    def value(m: CellMeasureV2, instrument: str) -> float:
        if channel == "V_output":
            return m.v_output[instrument]
        return m.v_reason[PRIMARY_PROCEDURE][instrument]

    per_instrument: dict[str, float] = {}
    primary_deltas: list[float] = []
    for instrument in instrument_names:
        abl = _series(measures, ABLATION, lambda m: value(m, instrument))
        act = _series(measures, cell, lambda m: value(m, instrument))
        shared = sorted(set(abl) & set(act))
        mean_abl = float(np.mean([abl[b] for b in shared])) if shared else 0.0
        mean_act = float(np.mean([act[b] for b in shared])) if shared else 0.0
        per_instrument[instrument] = (mean_abl - mean_act) / mean_abl if mean_abl > 0 else 0.0
        if instrument == instrument_names[0]:
            primary_deltas = [act[b] - abl[b] for b in shared]  # <0 == a decline

    declines = list(per_instrument.values())
    signs_agree = all(d > 0 for d in declines) or all(d < 0 for d in declines) or all(
        d == 0 for d in declines
    )
    return ChannelDecline(
        channel=channel,
        decline=per_instrument[instrument_names[0]],
        p_value=_paired_p(primary_deltas),
        signs_agree=signs_agree,
        per_instrument=per_instrument,
    )


@dataclass
class Rung0V2Verdict:
    """The gate, item by item (H0-H3)."""

    instrument_names: list[str] = field(default_factory=list)
    families: list[str] = field(default_factory=list)
    # cell -> family -> channel -> ChannelDecline
    declines: dict[str, dict[str, dict[str, ChannelDecline]]] = field(default_factory=dict)
    guards_ok: dict[str, dict[str, bool]] = field(default_factory=dict)  # cell -> family -> ok

    def h0_apparatus_valid(self) -> bool:
        """The positive control collapses >= POS_CONTROL_MIN in BOTH channels, most families."""
        hits = 0
        for fam in self.families:
            cp = self.declines.get(POSITIVE, {}).get(fam, {})
            if all(
                cp.get(ch, ChannelDecline(ch, 0, 1, False, {})).collapses(POS_CONTROL_MIN)
                for ch in ("V_output", "V_reason")
            ):
                hits += 1
        return hits >= FAMILIES_MIN

    def reachable(self) -> tuple[bool, str | None, str | None]:
        """H1: some actuator cell collapses >= DECLINE_MIN, >= FAMILIES_MIN families, >=1 channel,
        guards passing. Returns (reached, winning_cell, winning_channel)."""
        for cell in ACTUATOR_CELLS:
            for channel in ("V_output", "V_reason"):
                n = sum(
                    1
                    for fam in self.families
                    if self.declines.get(cell, {}).get(fam, {}).get(
                        channel, ChannelDecline(channel, 0, 1, False, {})
                    ).collapses(DECLINE_MIN)
                    and self.guards_ok.get(cell, {}).get(fam, False)
                )
                if n >= FAMILIES_MIN:
                    return True, cell, channel
        return False, None, None


def evaluate(
    measures: Sequence[CellMeasureV2],
    *,
    instrument_names: Sequence[str],
    families: Sequence[str],
) -> Rung0V2Verdict:
    """Assemble the full verdict: per (cell, family, channel) declines + the parroting/role guards.

    Role margin is normalized per family against that family's own ablation, so ``guards_ok`` means
    "role differentiation held above ``ROLE_MARGIN_TOL`` of the ablation level, and the answers did
    not parrot the shown cards." CP is exempt from the parroting guard (it parrots by design).
    """
    verdict = Rung0V2Verdict(
        instrument_names=list(instrument_names), families=list(families)
    )
    cells = (POSITIVE, *ACTUATOR_CELLS)
    for cell in cells:
        verdict.declines[cell] = {}
        verdict.guards_ok[cell] = {}
        for fam in families:
            fam_measures = [m for m in measures if m.family_id == fam]
            verdict.declines[cell][fam] = {
                ch: _channel_decline(fam_measures, cell, ch, instrument_names)
                for ch in ("V_output", "V_reason")
            }
            verdict.guards_ok[cell][fam] = _guards_ok(fam_measures, cell)
    return verdict


def _guards_ok(fam_measures: Sequence[CellMeasureV2], cell: str) -> bool:
    """Parroting + role-differentiation guards for one (family, cell), vs that family's ablation."""
    cell_ms = [m for m in fam_measures if m.cell == cell]
    abl_ms = [m for m in fam_measures if m.cell == ABLATION]
    if not cell_ms or not abl_ms:
        return False
    mean_align = float(np.nanmean([m.anchor_alignment for m in cell_ms]))
    abl_margin = float(np.mean([m.role_margin_ratio for m in abl_ms]))
    cell_margin = float(np.mean([m.role_margin_ratio for m in cell_ms]))
    margin_ratio = cell_margin / abl_margin if abl_margin > 0 else 1.0
    parroting_ok = cell == POSITIVE or np.isnan(mean_align) or mean_align < ALIGNMENT_CEILING
    return bool(parroting_ok and margin_ratio >= ROLE_MARGIN_TOL)
