"""Token-free tests for the rung-1 Day-0 bite gate: it must detect diversity and conditioning shift,
and require both to pass."""

from __future__ import annotations

import numpy as np

from whitespace1.rung1_day0 import (
    DAY0_CATALOG_SAMPLE,
    conditioned_prompts,
    evaluate_day0,
    no_catalog_prompts,
)
from whitespace1.stimuli import ROLES


def _unit(v) -> np.ndarray:
    a = np.asarray(v, dtype=np.float64)
    return a / np.linalg.norm(a)


def test_prompts_cover_five_personas_and_show_catalog_only_when_conditioned() -> None:
    nc, cond = no_catalog_prompts(), conditioned_prompts()
    assert len(nc) == len(cond) == len(ROLES) == 5
    assert all("none available this round." in p for p in nc)
    assert all(DAY0_CATALOG_SAMPLE[0] in p for p in cond)  # shown only when conditioned
    assert all(DAY0_CATALOG_SAMPLE[0] not in p for p in nc)
    assert all(r.name in p for r, p in zip(ROLES, cond, strict=True))


def test_orthogonal_no_catalog_outputs_pass_the_diversity_gate() -> None:
    nc = np.eye(5, 8)  # 5 mutually orthogonal rows -> mean pairwise cosine distance = 1.0
    v = evaluate_day0(no_catalog_emb=nc, conditioned_emb=nc, catalog_emb=np.eye(3, 8))
    assert v.diversity_ok and v.diversity > 0.9


def test_identical_no_catalog_outputs_fail_the_diversity_gate() -> None:
    nc = np.tile(_unit(np.arange(1, 9)), (5, 1))  # all identical -> distance 0
    v = evaluate_day0(no_catalog_emb=nc, conditioned_emb=nc, catalog_emb=np.eye(3, 8))
    assert not v.diversity_ok and v.diversity < 0.01


def test_conditioning_shift_detected_when_outputs_move_toward_catalog() -> None:
    u = _unit([1.0, 1, 1, 0, 0, 0, 0, 0])
    ortho = _unit([0.0, 0, 0, 1, 1, 1, 0, 0])
    catalog = np.tile(u, (3, 1))  # centroid ~ u
    no_cat = np.tile(ortho, (5, 1))  # orthogonal to u -> low alignment
    cond = np.tile(_unit(0.9 * u + 0.1 * ortho), (5, 1))  # near u -> high alignment
    v = evaluate_day0(no_catalog_emb=no_cat, conditioned_emb=cond, catalog_emb=catalog)
    assert v.shift_ok and v.alignment_shift > 0.03
    assert v.conditioned_alignment > v.no_catalog_alignment


def test_no_shift_fails_the_bite_gate() -> None:
    u = _unit([1.0, 1, 1, 0, 0, 0, 0, 0])
    same = np.tile(_unit([0.0, 0, 0, 1, 1, 1, 0, 0]), (5, 1))  # conditioned == no-catalog
    v = evaluate_day0(no_catalog_emb=same, conditioned_emb=same, catalog_emb=np.tile(u, (3, 1)))
    assert not v.shift_ok and abs(v.alignment_shift) < 1e-9


def test_passed_requires_both_gates() -> None:
    # diverse no-catalog (orthogonal, all off the catalog axis) AND conditioned pulled onto it
    catalog = np.tile(_unit([1.0, 0, 0, 0, 0, 0, 0, 0]), (3, 1))  # centroid = e0
    no_cat = np.eye(5, 8, k=3)  # rows e3..e7: diverse and orthogonal to e0
    cond = np.tile(_unit([1.0, 0, 0, 0, 0, 0, 0, 0]), (5, 1))  # all on e0
    v = evaluate_day0(no_catalog_emb=no_cat, conditioned_emb=cond, catalog_emb=catalog)
    assert v.diversity_ok and v.shift_ok and v.passed
    # dropping either condition drops the pass
    v_no_div = evaluate_day0(no_catalog_emb=cond, conditioned_emb=cond, catalog_emb=catalog)
    assert not v_no_div.diversity_ok and not v_no_div.passed
