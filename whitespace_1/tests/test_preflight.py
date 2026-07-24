"""Token-free tests for the stimulus set and the preflight criteria."""

from __future__ import annotations

import numpy as np
import pytest

from whitespace1 import preflight as pf
from whitespace1.stimuli import FAMILIES, ROLES, render_cell, stimulus_hash


def _fake_embed(seed: int = 0):
    """Deterministic pseudo-embedder: distinct texts get distinct directions."""

    def embed(texts):
        rows = []
        for t in texts:
            rng = np.random.default_rng(abs(hash(t)) % (2**32) + seed)
            rows.append(rng.normal(size=32))
        return np.asarray(rows)

    return embed


def _collinear_embed(texts):
    """Every text maps to the same direction -> zero spread (the near-duplicate failure)."""
    return np.tile(np.ones(8), (len(texts), 1))


# --- stimulus set ----------------------------------------------------------


def test_five_families_four_cards_each() -> None:
    assert len(FAMILIES) == 5
    assert all(len(f.cards) == 4 for f in FAMILIES)


def test_adoption_counts_are_skewed_and_identical_across_families() -> None:
    for f in FAMILIES:
        assert [c.adoption for c in f.cards] == [7, 4, 2, 1]


def test_task_ids_unique() -> None:
    assert len({f.task_id for f in FAMILIES}) == 5


def test_cells_a_and_b_show_identical_items() -> None:
    """The actuator contrast must isolate framing, not content."""
    for f in FAMILIES:
        a = render_cell(f, "A", ROLES[0])
        b = render_cell(f, "B", ROLES[0])
        for c in f.cards:
            assert c.text in a and c.text in b


def test_ablation_shows_no_items() -> None:
    for f in FAMILIES:
        c_cell = render_cell(f, "C", ROLES[0])
        assert all(card.text not in c_cell for card in f.cards)


def test_adoption_counts_only_visible_in_cell_b() -> None:
    for f in FAMILIES:
        assert "adopted by" not in render_cell(f, "A", ROLES[0])
        assert "adopted by" in render_cell(f, "B", ROLES[0])


def test_render_cell_rejects_unknown_cell() -> None:
    with pytest.raises(ValueError):
        render_cell(FAMILIES[0], "D", ROLES[0])


def test_stimulus_hash_is_stable() -> None:
    assert stimulus_hash() == stimulus_hash()
    assert len(stimulus_hash()) == 64


# --- criteria --------------------------------------------------------------


def test_c1_open_brief_passes() -> None:
    assert pf.check_open_brief().passed


def test_c4_length_balance_passes() -> None:
    assert pf.check_length_balance().passed


def test_c5_no_leakage_passes() -> None:
    assert pf.check_no_leakage().passed


def test_c2_fails_on_near_duplicate_cards() -> None:
    """The check must actually be able to fail."""
    assert not pf.check_card_spread(_collinear_embed).passed


def test_c2_passes_on_spread_cards() -> None:
    assert pf.check_card_spread(_fake_embed()).passed


def test_c6_fails_when_outputs_are_identical() -> None:
    assert not pf.check_ceiling_sanity(lambda p: "same", _collinear_embed).passed


def test_mpcd_of_identical_vectors_is_zero() -> None:
    assert pf._mpcd(np.tile(np.ones(4), (3, 1))) == pytest.approx(0.0, abs=1e-9)
