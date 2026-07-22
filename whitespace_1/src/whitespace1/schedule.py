"""Committed call schedule with per-block item shuffling.

Cell A annotates each shown item with its **display position**; cell B annotates it with its
**adoption count**. If item order were fixed, position would rank-correlate with adoption and cell
A would silently carry the popularity signal the contrast is meant to isolate. The shuffle is what
makes position neutral, so it is part of the manipulation, not presentation detail.

Within a block, cells A and B use the **same** order — the contrast isolates the annotation's
meaning, not the ordering. The schedule is seeded and hashed so a run can prove what it executed.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

import numpy as np

from .stimuli import FAMILIES, ROLES, Family, render_cell

CELLS: tuple[str, ...] = ("A", "B", "C")


@dataclass(frozen=True)
class Block:
    """One (family, block) unit: all three cells, sharing one item order."""

    family_id: str
    block_index: int
    item_order: tuple[int, ...]

    def ordered_cards(self, family: Family) -> tuple[object, ...]:
        return tuple(family.cards[i] for i in self.item_order)


def build_schedule(
    *, n_blocks: int, seed: int, families: tuple[Family, ...] = FAMILIES
) -> tuple[Block, ...]:
    """Deterministic schedule: ``n_blocks`` per family, each with its own shuffled item order."""
    rng = np.random.default_rng(seed)
    blocks: list[Block] = []
    for family in families:
        n_cards = len(family.cards)
        for b in range(n_blocks):
            order = tuple(int(i) for i in rng.permutation(n_cards))
            blocks.append(Block(family.task_id, b, order))
    return tuple(blocks)


def schedule_hash(blocks: tuple[Block, ...]) -> str:
    """Stable hash of the ordered schedule — pin this alongside the stimulus hash."""
    payload = [[b.family_id, b.block_index, list(b.item_order)] for b in blocks]
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()


def position_adoption_correlation(
    blocks: tuple[Block, ...], families: tuple[Family, ...] = FAMILIES
) -> float:
    """Mean Pearson r between display position and adoption count across the schedule.

    The guard the shuffle exists to satisfy: near zero means position carries no rank information.
    An unshuffled schedule returns ~-1 (position 1 always holds the highest-adoption card).
    """
    by_id = {f.task_id: f for f in families}
    positions: list[float] = []
    adoptions: list[float] = []
    for block in blocks:
        family = by_id[block.family_id]
        for display_pos, card_idx in enumerate(block.item_order, start=1):
            positions.append(float(display_pos))
            adoptions.append(float(family.cards[card_idx].adoption))
    if len(set(positions)) < 2 or len(set(adoptions)) < 2:
        return 0.0
    return float(np.corrcoef(positions, adoptions)[0, 1])


def render_block(block: Block, cell: str, role_index: int) -> str:
    """Render one prompt for this block, honouring the block's item order."""
    by_id = {f.task_id: f for f in FAMILIES}
    return render_cell(by_id[block.family_id], cell, ROLES[role_index], order=block.item_order)


def call_count(blocks: tuple[Block, ...], *, n_roles: int = len(ROLES)) -> int:
    """Total generation calls the schedule implies — sanity-check against the budget."""
    return len(blocks) * len(CELLS) * n_roles
