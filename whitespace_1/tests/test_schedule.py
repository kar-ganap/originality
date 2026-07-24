"""The shuffle is part of the manipulation — these guard its correctness properties."""

from __future__ import annotations

import pytest

from whitespace1.schedule import (
    Block,
    build_schedule,
    call_count,
    position_adoption_correlation,
    render_block,
    schedule_hash,
)
from whitespace1.stimuli import FAMILIES, ROLES, render_cell


def test_schedule_covers_every_family() -> None:
    blocks = build_schedule(n_blocks=10, seed=0)
    assert len(blocks) == len(FAMILIES) * 10
    assert {b.family_id for b in blocks} == {f.task_id for f in FAMILIES}


def test_every_order_is_a_permutation() -> None:
    for b in build_schedule(n_blocks=10, seed=0):
        assert sorted(b.item_order) == [0, 1, 2, 3]


def test_schedule_is_deterministic_and_seed_sensitive() -> None:
    a = build_schedule(n_blocks=10, seed=0)
    assert a == build_schedule(n_blocks=10, seed=0)
    assert a != build_schedule(n_blocks=10, seed=1)
    assert schedule_hash(a) == schedule_hash(build_schedule(n_blocks=10, seed=0))
    assert len(schedule_hash(a)) == 64


def test_shuffle_decorrelates_position_from_adoption() -> None:
    """The core guard: display position must carry no adoption-rank information."""
    blocks = build_schedule(n_blocks=10, seed=0)
    assert abs(position_adoption_correlation(blocks)) < 0.15


def test_unshuffled_schedule_would_fail_the_guard() -> None:
    """Proves the guard can fail — an identity order makes position a perfect rank proxy."""
    fixed = tuple(
        Block(f.task_id, b, (0, 1, 2, 3)) for f in FAMILIES for b in range(10)
    )
    assert position_adoption_correlation(fixed) < -0.9


def test_cells_a_and_b_share_the_block_order() -> None:
    """Otherwise the contrast confounds annotation meaning with item ordering."""
    block = build_schedule(n_blocks=1, seed=7)[0]
    a = render_block(block, "A", 0)
    b = render_block(block, "B", 0)
    family = next(f for f in FAMILIES if f.task_id == block.family_id)
    names_a = [line for line in a.splitlines() if line.startswith("- ")]
    names_b = [line for line in b.splitlines() if line.startswith("- ")]
    expected = [family.cards[i].name for i in block.item_order]
    assert [n.split(":")[0][2:] for n in names_a] == expected
    assert [n.split(":")[0][2:] for n in names_b] == expected


def test_ablation_ignores_order() -> None:
    block = build_schedule(n_blocks=1, seed=3)[0]
    family = next(f for f in FAMILIES if f.task_id == block.family_id)
    assert render_block(block, "C", 0) == render_cell(family, "C", ROLES[0])


def test_render_cell_rejects_bad_order() -> None:
    with pytest.raises(ValueError):
        render_cell(FAMILIES[0], "A", ROLES[0], order=(0, 1, 2))
    with pytest.raises(ValueError):
        render_cell(FAMILIES[0], "A", ROLES[0], order=(0, 0, 1, 2))


def test_call_count_matches_the_registered_rung0_design() -> None:
    """5 families x 10 blocks x 3 cells x 5 roles = 750 calls (design note §9.2)."""
    assert call_count(build_schedule(n_blocks=10, seed=0)) == 750


def test_position_annotation_is_display_order_not_card_index() -> None:
    block = Block(FAMILIES[0].task_id, 0, (3, 2, 1, 0))
    rendered = render_block(block, "A", 0)
    first_item = next(ln for ln in rendered.splitlines() if ln.startswith("- "))
    assert FAMILIES[0].cards[3].name in first_item
    assert "(position 1)" in first_item
