"""The Phase 2.3 subfield mechanism test (conceptual.md's "single most important
analysis").

Tests whether canon-concentrated subfields show more demographic–semantic
divergence than diffuse ones — the within-field probe of the actuator-sharing
mechanism and the direct test of the Phase 2.2 reframing (canon concentrates
*independently* of a diversifying frontier + authorship). Under independence the
slope γ₁ of divergence-magnitude on canon-concentration (controlling for log
subfield size) is ≈ 0; a robust positive γ₁ would localize a narrowing mechanism.

This module provides:
  - :func:`extract_primary_subconcept` / :func:`build_paper_subfield_map` — assign
    each paper to its highest-scoring OpenAlex **level-1 sub-concept** (the
    interpretable subfield), mirroring
    :func:`whitespace2.demographics.extract_primary_field`. The map's
    ``primary_field`` column carries the subfield key ``"{field}:{concept_id}"``
    so the Phase-1.3 demographic pipeline (:func:`build_joint_plurality_series`,
    which treats ``field`` as an opaque grouping key) produces a per-subfield
    demographic series with **no re-plumbing**.
  - :func:`subfield_regression` — the pre-registered estimator: OLS of
    divergence-magnitude on canon-concentration + log-size (+ optional field FE),
    with a **permutation null on γ₁** (the subfield count is small → no
    asymptotic-t reliance), a **collinearity VIF** (canon vs log-size — the WS-F
    caution), and a **standardized γ₁** so "≈ 0" carries a magnitude.

Divergence-magnitude is the caller's ``demographic_trend_sd − semantic_trend_sd``
(absolute standardized trends differenced) — NOT the Phase-2.2 ratio, which is
denominator-confounded (ratio ≠ control; see ``tasks/lessons.md``).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from whitespace2.demographics import extract_primary_field

# OpenAlex concept levels: 0 = domain roots (Computer science / Physics),
# 1 = the natural "subfield" grain (Machine learning, Cryptography, Quantum
# mechanics, …), 2+ = increasingly specific topics.
_SUBCONCEPT_LEVEL = 1


def extract_primary_subconcept(
    concepts_json: Any,
    *,
    level: int = _SUBCONCEPT_LEVEL,
    exclude_ids: frozenset[str] = frozenset(),
    min_score: float = 0.0,
) -> str | None:
    """The highest-scoring ``level``-N OpenAlex concept id (the paper's subfield).

    ``concepts_json`` is the JSON-string array of ``{id, level, score, …}``
    concept objects on the §0 corpus. Among concepts whose ``level`` equals
    ``level`` (default 1 — the subfield grain; excludes the level-0 field roots)
    and whose id is not in ``exclude_ids``, returns the id with the highest
    ``score`` (ties broken by the lexicographically smallest id for
    determinism). Returns ``None`` when no qualifying concept clears
    ``min_score``, and on missing / malformed input.
    """
    if not isinstance(concepts_json, str) or not concepts_json:
        return None
    try:
        concepts = json.loads(concepts_json)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(concepts, list):
        return None

    best_id: str | None = None
    best_score = float("-inf")
    for c in concepts:
        if not isinstance(c, dict):
            continue
        if c.get("level") != level:
            continue
        cid = c.get("id")
        score = c.get("score")
        if not isinstance(cid, str) or cid in exclude_ids:
            continue
        if not isinstance(score, (int, float)) or isinstance(score, bool):
            continue
        s = float(score)
        # strictly-greater keeps the first; equal-score ties → smaller id
        if s > best_score or (s == best_score and (
            best_id is None or cid < best_id)):
            best_score = s
            best_id = cid

    if best_id is None or best_score < min_score:
        return None
    return best_id


def build_paper_subfield_map(
    corpus_parquet: str | Path,
    output_parquet: str | Path,
    *,
    field_filter: str | None = None,
    level: int = _SUBCONCEPT_LEVEL,
    exclude_ids: frozenset[str] = frozenset(),
    min_score: float = 0.0,
    batch_size: int = 50_000,
) -> dict[str, Any]:
    """Stream a §0 corpus parquet → a ``paper_id → "{field}:{subfield}"`` map.

    Reads only ``id`` + ``concepts_json`` (PyArrow column projection). For each
    paper: assigns the field via :func:`extract_primary_field`; if
    ``field_filter`` is set and the field differs, the paper is dropped; else
    assigns the subfield via :func:`extract_primary_subconcept`. Papers with no
    qualifying level-N sub-concept are dropped (inner-join semantics, mirroring
    :func:`whitespace2.demographics.build_paper_field_map`).

    The output column is named ``primary_field`` (value ``"{field}:{concept}"``)
    so it is a drop-in for the demographic pipeline's paper→field map — the
    grouping key is opaque there. Returns per-run counts.
    """
    corpus_parquet = Path(corpus_parquet)
    output_parquet = Path(output_parquet)

    pf = pq.ParquetFile(str(corpus_parquet))
    writer: pq.ParquetWriter | None = None
    n_papers = 0
    n_assigned = 0
    n_no_field = 0
    n_no_subconcept = 0

    try:
        for batch in pf.iter_batches(
            batch_size=batch_size, columns=["id", "concepts_json"],
        ):
            rows: list[dict[str, Any]] = []
            for rec in batch.to_pylist():
                n_papers += 1
                cj = rec.get("concepts_json")
                field = extract_primary_field(cj)
                if field is None or (
                    field_filter is not None and field != field_filter):
                    n_no_field += 1
                    continue
                sub = extract_primary_subconcept(
                    cj, level=level, exclude_ids=exclude_ids,
                    min_score=min_score,
                )
                if sub is None:
                    n_no_subconcept += 1
                    continue
                rows.append({
                    "paper_id": rec.get("id"),
                    "primary_field": f"{field}:{sub}",
                })
                n_assigned += 1
            if rows:
                tbl = pa.Table.from_pylist(rows)
                if writer is None:
                    writer = pq.ParquetWriter(str(output_parquet), tbl.schema)
                writer.write_table(tbl)
    finally:
        if writer is not None:
            writer.close()

    if writer is None:  # nothing assigned — write an empty typed table
        empty = pa.table({
            "paper_id": pa.array([], pa.string()),
            "primary_field": pa.array([], pa.string()),
        })
        pq.write_table(empty, str(output_parquet))

    return {
        "n_papers": n_papers,
        "n_assigned": n_assigned,
        "n_no_field": n_no_field,
        "n_no_subconcept": n_no_subconcept,
    }


def _design_matrix(
    canon: np.ndarray[Any, Any],
    log_size: np.ndarray[Any, Any],
    field: np.ndarray[Any, Any] | None,
) -> np.ndarray[Any, Any]:
    """``[1, canon, log_size, field_dummies…]`` (drop-first field reference)."""
    n = canon.size
    cols = [np.ones(n), canon, log_size]
    if field is not None:
        levels = sorted(set(field.tolist()))
        for lv in levels[1:]:            # drop-first → reference category
            cols.append((field == lv).astype(np.float64))
    return np.column_stack(cols)


def subfield_regression(
    canon: Any,
    divergence: Any,
    log_size: Any,
    *,
    field: Any = None,
    n_perm: int = 10_000,
    seed: int = 0,
    alpha: float = 0.05,
) -> dict[str, Any]:
    """OLS of divergence-magnitude on canon-concentration + log-size (+ field FE).

    Parallel arrays over subfields. Fits
    ``divergence ~ 1 + canon + log_size [+ field_dummies]`` and returns the
    coefficient on ``canon`` (γ₁ — the conceptual doc's coefficient of interest)
    with:

      - ``gamma1_perm_pvalue`` — two-tailed **permutation p** (shuffle ``canon``
        across subfields ``n_perm`` times; add-one smoothed). Via Frisch-Waugh-
        Lovell: γ₁ = ⟨canon⊥Z, div⊥Z⟩ / ‖canon⊥Z‖², where ``Z`` is the design
        without ``canon``; only ``canon`` is residualized per permutation
        (``div⊥Z`` is fixed), so the null is exact and vectorized.
      - ``vif_canon`` — 1/(1−R²) of ``canon`` on ``Z`` (the collinearity
        diagnostic; γ₁ with VIF ≳ 10 is unreliable — the WS-F caution).
      - ``gamma1_standardized`` — γ₁·sd(canon)/sd(divergence) (magnitude for a
        "≈ 0" verdict).
      - ``gamma1_ci95`` / ``gamma1_stderr`` — OLS normal-theory interval.

    Degenerate input (fewer subfields than parameters + 1, or zero canon
    variance) → ``gamma1=None``, ``significant=False``.
    """
    canon_a = np.asarray(canon, dtype=np.float64)
    div_a = np.asarray(divergence, dtype=np.float64)
    ls_a = np.asarray(log_size, dtype=np.float64)
    field_a = None if field is None else np.asarray(field)

    mask = ~(np.isnan(canon_a) | np.isnan(div_a) | np.isnan(ls_a))
    canon_a, div_a, ls_a = canon_a[mask], div_a[mask], ls_a[mask]
    if field_a is not None:
        field_a = field_a[mask]
    n = int(canon_a.size)

    x_full = _design_matrix(canon_a, ls_a, field_a)
    p = x_full.shape[1]
    degenerate = {
        "n_subfields": n, "gamma1": None, "beta_logsize": None,
        "gamma1_stderr": None, "gamma1_ci95": None, "gamma1_perm_pvalue": None,
        "gamma1_standardized": None, "vif_canon": None, "r_squared": None,
        "n_perm": n_perm, "alpha": alpha, "significant": False,
    }
    if n < p + 1 or float(np.ptp(canon_a)) == 0.0:
        return degenerate

    # Full-model fit (for β_logsize, stderr/CI, R²)
    beta, *_ = np.linalg.lstsq(x_full, div_a, rcond=None)
    gamma1 = float(beta[1])
    beta_logsize = float(beta[2])
    resid = div_a - x_full @ beta
    rss = float(resid @ resid)
    tss = float(((div_a - div_a.mean()) ** 2).sum())
    r_squared = 1.0 - rss / tss if tss > 0 else 0.0

    dof = n - p
    xtx_inv = np.linalg.pinv(x_full.T @ x_full)
    sigma2 = rss / dof if dof > 0 else float("nan")
    gamma1_stderr = float(np.sqrt(sigma2 * xtx_inv[1, 1])) if dof > 0 else None
    gamma1_ci95: list[float] | None = None
    if gamma1_stderr is not None and np.isfinite(gamma1_stderr):
        from scipy.stats import t as _t
        tcrit = float(_t.ppf(1.0 - alpha / 2.0, dof))
        gamma1_ci95 = [gamma1 - tcrit * gamma1_stderr,
                       gamma1 + tcrit * gamma1_stderr]

    # FWL residualization on Z = design without the canon column
    z = np.delete(x_full, 1, axis=1)
    m = np.eye(n) - z @ np.linalg.pinv(z)      # residual-maker for Z
    canon_r = m @ canon_a
    div_r = m @ div_a
    denom = float(canon_r @ canon_r)
    # If the controls already explain divergence completely (no residual
    # variance left), γ₁ is exactly 0 and no permutation of canon can make it
    # nonzero — the observed and permuted coefficients are floating-point dust,
    # whose comparison would otherwise report a spurious p. Guard it: a
    # numerically-negligible div_r (relative to the divergence scale) → p = 1.0.
    div_r_ss = float(div_r @ div_r)
    negligible = div_r_ss <= 1e-18 * max(tss, 1.0)

    # VIF(canon | Z) = TSS(canon) / RSS(canon on Z) = 1/(1 − R²_canon)
    canon_tss = float(((canon_a - canon_a.mean()) ** 2).sum())
    vif_canon = (canon_tss / denom) if denom > 0 else float("inf")

    # standardized γ₁
    sd_c = float(np.std(canon_a, ddof=1))
    sd_d = float(np.std(div_a, ddof=1))
    gamma1_std = gamma1 * sd_c / sd_d if sd_d > 0 else 0.0

    # permutation null on γ₁: shuffle canon, residualize on Z, recompute the FWL
    # coefficient against the fixed div_r
    if denom > 0 and not negligible:
        rng = np.random.default_rng(seed)
        idx = np.argsort(rng.random((n_perm, n)), axis=1)
        canon_perm = canon_a[idx]                       # (n_perm, n)
        cr_perm = canon_perm @ m.T                       # residualize each row
        num = cr_perm @ div_r                            # (n_perm,)
        den = (cr_perm ** 2).sum(axis=1)                 # (n_perm,)
        with np.errstate(invalid="ignore", divide="ignore"):
            perm_g = np.where(den > 0, num / den, 0.0)
        exceed = int(np.sum(np.abs(perm_g) >= abs(gamma1)))
        perm_p = (1 + exceed) / (n_perm + 1)
    else:
        perm_p = 1.0

    return {
        "n_subfields": n,
        "gamma1": gamma1,
        "beta_logsize": beta_logsize,
        "gamma1_stderr": gamma1_stderr,
        "gamma1_ci95": gamma1_ci95,
        "gamma1_perm_pvalue": float(perm_p),
        "gamma1_standardized": float(gamma1_std),
        "vif_canon": float(vif_canon),
        "r_squared": float(r_squared),
        "n_perm": n_perm,
        "alpha": alpha,
        "significant": bool(perm_p < alpha),
    }
