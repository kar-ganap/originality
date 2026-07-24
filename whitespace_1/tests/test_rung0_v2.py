"""Token-free tests for the rung-0 v2 gate: detect a collapse, a null, and instrument splits."""

from __future__ import annotations

from whitespace1.rung0_v2 import (
    ABLATION,
    ACTUATOR_CELLS,
    POSITIVE,
    CellMeasureV2,
    distinct_2,
    evaluate,
)

INSTRUMENTS = ["I1", "I2", "I3"]
FAMILIES = [f"fam{i}" for i in range(5)]


def _measure(fam: str, block: int, cell: str, *, v: float, align: float, margin: float,
             instr_v: dict[str, float] | None = None) -> CellMeasureV2:
    """One synthetic cell-block. ``v`` sets both channels on every instrument unless ``instr_v``
    overrides per-instrument values (to force a sign split)."""
    per = instr_v or {i: v for i in INSTRUMENTS}
    return CellMeasureV2(
        family_id=fam, block_index=block, cell=cell,
        v_output=dict(per),
        v_reason={"strategy": dict(per), "decisions": dict(per)},
        anchor_alignment=align, role_margin_ratio=margin,
    )


def _dataset(actuator_v: float, *, cp_v: float = 0.15, abl_v: float = 0.42,
             actuator_align: float = 0.40, actuator_margin: float = 0.30,
             families=FAMILIES, n_blocks: int = 10) -> list[CellMeasureV2]:
    """Ablation at abl_v, positive control at cp_v, all actuator cells at actuator_v."""
    ms: list[CellMeasureV2] = []
    for fam in families:
        for b in range(n_blocks):
            jitter = 0.001 * b
            ms.append(_measure(fam, b, ABLATION, v=abl_v + jitter, align=float("nan"), margin=0.30))
            ms.append(_measure(fam, b, POSITIVE, v=cp_v + jitter, align=0.84, margin=0.30))
            for cell in ACTUATOR_CELLS:
                ms.append(_measure(fam, b, cell, v=actuator_v + jitter,
                                   align=actuator_align, margin=actuator_margin))
    return ms


# --- I3 lexical instrument -------------------------------------------------------------------


def test_distinct_2_zero_for_identical_and_high_for_varied() -> None:
    assert distinct_2(["a b c", "a b c", "a b c"]) < 0.5  # all identical → repeated bigrams
    assert distinct_2(["a b c", "d e f", "g h i"]) == 1.0  # all distinct bigrams


# --- H0: the apparatus must be validated by the positive control -----------------------------


def test_h0_holds_when_positive_control_collapses() -> None:
    v = evaluate(_dataset(actuator_v=0.42), instrument_names=INSTRUMENTS, families=FAMILIES)
    assert v.h0_apparatus_valid()  # CP at 0.15 vs ablation 0.42 is a ~64% drop, both channels


def test_h0_fails_when_positive_control_does_not_collapse() -> None:
    # CP barely below ablation → apparatus not validated.
    v = evaluate(_dataset(actuator_v=0.42, cp_v=0.40), instrument_names=INSTRUMENTS,
                 families=FAMILIES)
    assert not v.h0_apparatus_valid()


# --- H1: reachability ------------------------------------------------------------------------


def test_reachable_when_actuator_collapses_with_guards() -> None:
    v = evaluate(_dataset(actuator_v=0.20), instrument_names=INSTRUMENTS, families=FAMILIES)
    reached, cell, channel = v.reachable()
    assert reached and cell in ACTUATOR_CELLS and channel in ("V_output", "V_reason")


def test_not_reachable_when_actuator_holds() -> None:
    # actuator == ablation → no decline (v1's actual result). H0 still holds; H1 does not.
    v = evaluate(_dataset(actuator_v=0.42), instrument_names=INSTRUMENTS, families=FAMILIES)
    assert v.h0_apparatus_valid()
    assert not v.reachable()[0]


def test_parroting_actuator_collapse_is_blocked_by_the_guard() -> None:
    # big drop but alignment above the ceiling → guard fails → not counted as reachability.
    v = evaluate(_dataset(actuator_v=0.20, actuator_align=0.84),
                 instrument_names=INSTRUMENTS, families=FAMILIES)
    assert not v.reachable()[0]


def test_role_collapse_actuator_is_blocked_by_the_guard() -> None:
    # role margin collapses to 10% of ablation → guard fails.
    v = evaluate(_dataset(actuator_v=0.20, actuator_margin=0.03),
                 instrument_names=INSTRUMENTS, families=FAMILIES)
    assert not v.reachable()[0]


# --- the three-instrument sign rule ----------------------------------------------------------


def test_instrument_sign_split_voids_the_collapse() -> None:
    """I1/I2 show a drop but I3 shows a rise → signs disagree → not a clean collapse."""
    ms: list[CellMeasureV2] = []
    for fam in FAMILIES:
        for b in range(10):
            j = 0.001 * b
            ms.append(_measure(fam, b, ABLATION, v=0.42 + j, align=float("nan"), margin=0.30))
            ms.append(_measure(fam, b, POSITIVE, v=0.15 + j, align=0.84, margin=0.30))
            for cell in ACTUATOR_CELLS:
                # I1, I2 drop to 0.20; I3 RISES to 0.60 — a sign split.
                ms.append(_measure(fam, b, cell, v=0.20,
                                   instr_v={"I1": 0.20 + j, "I2": 0.20 + j, "I3": 0.60 + j},
                                   align=0.40, margin=0.30))
    v = evaluate(ms, instrument_names=INSTRUMENTS, families=FAMILIES)
    # I1 shows a drop and the Wilcoxon is significant, but signs disagree → collapses() is False.
    d = v.declines["C1"]["fam0"]["V_output"]
    assert d.decline > 0 and d.significant and not d.signs_agree
    assert not d.collapses(0.20)
    assert not v.reachable()[0]


def test_evaluate_populates_all_cells_and_families() -> None:
    v = evaluate(_dataset(actuator_v=0.30), instrument_names=INSTRUMENTS, families=FAMILIES)
    assert set(v.declines) == {POSITIVE, *ACTUATOR_CELLS}
    for cell in v.declines:
        assert set(v.declines[cell]) == set(FAMILIES)
        for fam in FAMILIES:
            assert set(v.declines[cell][fam]) == {"V_output", "V_reason"}
