"""Insulation experiment — the AI causal test of Claim #17 (``docs/ws1-insulation-prereg.md``).

Two 5-persona R4 popularity runs build the candidate pool — a FIELD (connected, mainstream) and an
ISOLATED group (its own local catalog). The connected field is then shown balanced mixes of both
origins' round-T ideas, and we measure per-capita **adoption** (echo). Claim #17 predicts isolated >
connected. The estimand is the field's *uptake*, not diversity — not the insulation-is-distance
tautology. Token-free except the injected provider; orchestration in ``experiments/run_insulation``.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import cast

import numpy as np
from numpy.typing import NDArray

from .rung1_r4 import R4Provider
from .stimuli import Role

FloatMatrix = NDArray[np.float64]
ISOLATED = "isolated"
CONNECTED = "connected"


@dataclass(frozen=True)
class Candidate:
    text: str
    embedding: tuple[float, ...]
    origin: str  # ISOLATED | CONNECTED


@dataclass(frozen=True)
class Showing:
    """One candidate presented to the field in one adoption round, with the echo it drew."""

    origin: str
    echo: float
    shown: bool  # True = in the shown sample; False = an unseen decoy (for the live-check)


def _unit_rows(matrix: FloatMatrix) -> FloatMatrix:
    m = np.asarray(matrix, dtype=np.float64)
    norms = np.linalg.norm(m, axis=1, keepdims=True)
    return cast(FloatMatrix, m / np.where(norms == 0.0, 1.0, norms))


def _echo(field_outputs: FloatMatrix, candidate: NDArray[np.float64]) -> float:
    """``Σ_agents max(cos(output, candidate), 0)`` — the ``record_echoes`` uptake formula."""
    outs = _unit_rows(field_outputs)
    c = np.asarray(candidate, dtype=np.float64)
    norm = float(np.linalg.norm(c))
    unit = c / norm if norm > 0 else c
    return float(np.sum(np.maximum(outs @ unit, 0.0)))


def run_adoption(
    *,
    provider: R4Provider,
    personas: Sequence[Role],
    topic: str,
    candidates: Sequence[Candidate],
    rounds: int,
    shown_per_origin: int,
    rng: np.random.Generator,
) -> list[Showing]:
    """Show the field balanced candidate mixes; measure echo per shown candidate, plus the unseen
    candidates each round as decoys (for the live-check). One Showing per (candidate, round) it took
    part in. The field builds each round's prompt from the shown candidates (the exposure)."""
    iso = [c for c in candidates if c.origin == ISOLATED]
    conn = [c for c in candidates if c.origin == CONNECTED]
    if len(iso) < shown_per_origin or len(conn) < shown_per_origin:
        raise ValueError("not enough candidates of each origin for the requested sample")
    showings: list[Showing] = []
    for _ in range(rounds):
        pick_iso = {int(i) for i in rng.choice(len(iso), shown_per_origin, replace=False)}
        pick_conn = {int(i) for i in rng.choice(len(conn), shown_per_origin, replace=False)}
        shown = [iso[i] for i in pick_iso] + [conn[i] for i in pick_conn]
        catalog_samples = tuple(tuple(c.text for c in shown) for _ in personas)
        proposals = provider.propose_many(
            personas=list(personas), topic=topic, catalog_samples=catalog_samples
        )
        outputs = provider.embed([p.text for p in proposals])
        for candidate in shown:
            echo = _echo(outputs, np.asarray(candidate.embedding, dtype=np.float64))
            showings.append(Showing(origin=candidate.origin, echo=echo, shown=True))
        unseen = ([c for i, c in enumerate(iso) if i not in pick_iso]
                  + [c for i, c in enumerate(conn) if i not in pick_conn])
        for candidate in unseen:
            echo = _echo(outputs, np.asarray(candidate.embedding, dtype=np.float64))
            showings.append(Showing(origin=candidate.origin, echo=echo, shown=False))
    return showings


def per_capita_adoption(showings: Sequence[Showing]) -> dict[str, float]:
    """Mean echo per *shown* candidate, by origin — each group's per-capita adoption."""
    result: dict[str, float] = {}
    for origin in (ISOLATED, CONNECTED):
        echoes = [s.echo for s in showings if s.shown and s.origin == origin]
        result[origin] = float(np.mean(echoes)) if echoes else 0.0
    return result


def adoption_gap(showings: Sequence[Showing]) -> float:
    """isolated − connected per-capita adoption. Claim #17 predicts > 0."""
    per_capita = per_capita_adoption(showings)
    return per_capita[ISOLATED] - per_capita[CONNECTED]


def label_shuffle_null(
    showings: Sequence[Showing], rng: np.random.Generator, n: int = 10_000
) -> FloatMatrix:
    """Null gap distribution under permuted origin labels across the shown candidates — guards
    against the gap being a property of pool composition rather than of origin."""
    shown = [s for s in showings if s.shown]
    echoes = np.array([s.echo for s in shown], dtype=np.float64)
    n_iso = sum(1 for s in shown if s.origin == ISOLATED)
    if not len(echoes) or n_iso == 0 or n_iso == len(echoes):
        return np.zeros(n, dtype=np.float64)
    gaps = np.empty(n, dtype=np.float64)
    for i in range(n):
        perm = rng.permutation(len(echoes))
        gaps[i] = echoes[perm[:n_iso]].mean() - echoes[perm[n_iso:]].mean()
    return gaps


def live_check(showings: Sequence[Showing]) -> float:
    """Mean shown-echo − mean decoy-echo: does the field respond to what it is shown? A positive
    value is the precondition for reading adoption (as in rung 2b's uptake gate)."""
    shown = [s.echo for s in showings if s.shown]
    decoy = [s.echo for s in showings if not s.shown]
    shown_mean = float(np.mean(shown)) if shown else 0.0
    decoy_mean = float(np.mean(decoy)) if decoy else 0.0
    return shown_mean - decoy_mean
