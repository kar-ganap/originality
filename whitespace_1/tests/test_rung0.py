"""Token-free tests for the rung-0 gate. The gate must be able to both pass and fail."""

from __future__ import annotations

import numpy as np
import pytest

from whitespace1 import rung0
from whitespace1.client import MockClient
from whitespace1.rung0 import (
    CellMeasure,
    anchor_alignment,
    collect_block,
    echo_concentration,
    evaluate,
    evaluate_family,
    mean_pairwise_cosine,
    measure_cell,
    role_margin,
)
from whitespace1.schedule import build_schedule
from whitespace1.stimuli import FAMILIES


def _measures(
    *,
    decline: float,
    n_blocks: int = 10,
    alignment: float = 0.40,
    margin_ratio: float = 1.0,
    families: int = 5,
    cell: str = "A",
) -> list[CellMeasure]:
    """Synthetic measures with a controllable decline, for gate-logic tests."""
    out: list[CellMeasure] = []
    for f in FAMILIES[:families]:
        for b in range(n_blocks):
            base = 0.42 + 0.001 * b  # slight per-block variation so deltas aren't degenerate
            out.append(CellMeasure(f.task_id, b, "C", base, 0.30))
            out.append(
                CellMeasure(
                    f.task_id,
                    b,
                    cell,
                    base * (1 - decline),
                    0.30 * margin_ratio,
                    anchor_alignment=alignment,
                    echo_concentration=0.35,
                )
            )
    return out


# --- metrics ---------------------------------------------------------------


def test_mpcd_zero_for_identical_and_positive_for_spread() -> None:
    assert mean_pairwise_cosine(np.tile(np.ones(4), (3, 1))) == pytest.approx(0.0, abs=1e-9)
    assert mean_pairwise_cosine(np.eye(3)) > 0.9


def test_anchor_alignment_is_one_when_outputs_are_the_cards() -> None:
    cards = np.eye(4)
    assert anchor_alignment(cards, cards) == pytest.approx(1.0, abs=1e-9)


def test_echo_concentration_max_when_all_outputs_hit_one_card() -> None:
    cards = np.eye(4)
    outputs = np.tile(cards[0], (5, 1))
    assert echo_concentration(outputs, cards) > 0.7
    spread = cards[[0, 1, 2, 3]]
    assert echo_concentration(spread, cards) == pytest.approx(0.0, abs=1e-9)


def test_role_margin_positive_when_outputs_track_own_roles() -> None:
    roles = np.eye(5)
    assert role_margin(roles, roles) > 0.9
    generic = np.tile(np.ones(5), (5, 1))
    assert role_margin(generic, roles) == pytest.approx(0.0, abs=1e-9)


# --- gate: it must be able to PASS ----------------------------------------


def test_gate_passes_on_a_real_collapse() -> None:
    verdict = evaluate(_measures(decline=0.35))
    assert verdict.passed
    assert len(verdict.passing_families("A")) == 5
    assert verdict.h_star() == pytest.approx(0.35)


# --- gate: it must be able to FAIL ----------------------------------------


def test_gate_fails_when_nothing_moves() -> None:
    assert not evaluate(_measures(decline=0.0)).passed


def test_gate_fails_below_the_20pct_margin() -> None:
    """19% is a near-miss and must not pass — the margin is the registered constant."""
    verdict = evaluate(_measures(decline=0.19))
    assert not verdict.passed
    assert all(not v.margin_ok for v in verdict.per_cell["A"])


def test_gate_fails_when_v_rises() -> None:
    assert not evaluate(_measures(decline=-0.10)).passed


def test_generality_rule_requires_three_of_five() -> None:
    """Two collapsing families is not enough, three is."""
    two = _measures(decline=0.35, families=2) + _measures(decline=0.0, families=5)[20:]
    assert len(evaluate(two).passing_families("A")) < 3
    assert not evaluate(two).passed
    assert evaluate(_measures(decline=0.35, families=5)).passed


def test_parroting_guard_blocks_a_restatement_collapse() -> None:
    """A big drop with alignment above the ceiling is an artifact, not a pass."""
    verdict = evaluate(_measures(decline=0.40, alignment=0.84))
    assert not verdict.passed
    assert len(verdict.parroting_flags) == 5
    assert all(v.margin_ok and not v.guards_ok for v in verdict.per_cell["A"])


def test_role_collapse_guard_blocks_the_homogeneous_corner() -> None:
    """If role differentiation collapses, V fell for the wrong reason."""
    verdict = evaluate(_measures(decline=0.40, margin_ratio=0.10))
    assert not verdict.passed
    assert all(not v.guards_ok for v in verdict.per_cell["A"])


def test_h_star_is_none_without_a_collapse() -> None:
    """No collapse point means no denominator — the earlier null stays uninterpretable."""
    assert evaluate(_measures(decline=0.0)).h_star() is None


def test_actuator_form_dependence_is_visible() -> None:
    """Cell A collapses, cell B does not — reachability is form-dependent, and reported so."""
    measures = _measures(decline=0.35, cell="A") + [
        m for m in _measures(decline=0.0, cell="B") if m.cell == "B"
    ]
    verdict = evaluate(measures)
    assert verdict.cell_passed("A")
    assert not verdict.cell_passed("B")
    assert verdict.passed  # reachable in one form


def test_wilcoxon_floor_is_reachable_at_n10() -> None:
    """The registered p<.05 branch must be attainable — it was not at n<=4 in a sibling project."""
    v = evaluate_family(_measures(decline=0.35, n_blocks=10), FAMILIES[0].task_id, "A")
    assert v.n_blocks == 10
    assert v.p_value < 0.05


def test_unpaired_blocks_are_dropped_not_imputed() -> None:
    measures = [m for m in _measures(decline=0.35) if not (m.block_index == 0 and m.cell == "C")]
    v = evaluate_family(measures, FAMILIES[0].task_id, "A")
    assert v.n_blocks == 9


# --- wiring ----------------------------------------------------------------


def test_collect_and_measure_run_end_to_end_on_the_mock() -> None:
    client = MockClient()
    block = build_schedule(n_blocks=1, seed=0)[0]
    texts, usage = collect_block(client, block, "A")
    assert len(texts) == 5
    assert usage.output > 0
    m = measure_cell(client, block, "A", texts)
    assert m.anchor_alignment is not None and m.echo_concentration is not None
    assert measure_cell(client, block, "C", texts).anchor_alignment is None


def test_registered_constants_match_the_design_note() -> None:
    assert rung0.DECLINE_MIN == 0.20
    assert rung0.FAMILIES_MIN == 3
    assert rung0.ALIGNMENT_CEILING == 0.65
    assert rung0.MAX_OUTPUT_TOKENS == 120
