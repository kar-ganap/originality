"""WS3 Phase 2 · Experiment C-2b (the adjudication test) — is the CD-decline a reference-LENGTH
artifact? Within-sample (SAME eligible focals as C-2a) so the citation-accumulation selection
confound cancels. Two views:
  (1) MEDIATION regression — CD ~ year (β_year) vs CD ~ year + mean-citer-reference-length
      (β_year'). If |β_year'| << |β_year|, the decline is length-mediated (the artifact). The
      mechanism (C-1b): later citers cite MORE ⇒ more overlap with a focal's refs ⇒ n_j↑ ⇒ CD↓.
  (2) LENGTH-CAP counterfactual — recompute CD after capping every paper's reference list to the
      early-era level (removes length-inflation, the mirror of C-1b which ADDED it); does the raw
      slope attenuate?
Pre-registered gate: ≥ ~50% attenuation of β_year.
Run from whitespace_2/: uv run python experiments/phase-2-bridge/cd_data_C2b.py"""

from __future__ import annotations

import numpy as np
import pandas as pd

from whitespace2.v_extension import cd_index

PANEL = "data/base-1m/panel-2.4.parquet"
MIN_CITERS = 3
SEED = 0


def _refs_idx(refs_col: pd.Series, idx: dict[str, int],
              cap: int | None, rng: np.random.Generator | None) -> list[list[int]]:
    out: list[list[int]] = []
    for r in refs_col:
        rr = list(r) if r is not None else []
        if cap is not None and len(rr) > cap and rng is not None:
            rr = list(rng.choice(np.asarray(rr, dtype=object), size=cap, replace=False))
        out.append([idx[str(x)] for x in rr if str(x) in idx])
    return out


def _ols_year_coef(y: np.ndarray, cols: list[np.ndarray]) -> float:
    x = np.column_stack([np.ones_like(y)] + cols)
    beta, *_ = np.linalg.lstsq(x, y, rcond=None)
    return float(beta[1])   # coefficient on `year` (first predictor after intercept)


def main() -> None:
    d = pd.read_parquet(PANEL, columns=["paper_id", "year", "refs", "field", "n_refs"])
    cs = d[d["field"] == "cs"].reset_index(drop=True)
    idx = {pid: i for i, pid in enumerate(cs["paper_id"].astype(str))}
    year = cs["year"].to_numpy().astype(float)
    nref_full = cs["n_refs"].to_numpy().astype(float)

    refs_idx = _refs_idx(cs["refs"], idx, None, None)
    citers: list[list[int]] = [[] for _ in range(len(cs))]
    for c, rr in enumerate(refs_idx):
        for pr in rr:
            citers[pr].append(c)
    cd = cd_index(refs_idx, min_citers=MIN_CITERS)
    ei = np.flatnonzero(~np.isnan(cd))
    print(f"eligible focals: {ei.size:,}")

    # mean full-reference-length of each focal's in-panel citers (the artifact driver)
    mean_citer_rl = np.array([float(np.mean(nref_full[citers[e]])) if citers[e] else np.nan
                              for e in ei])
    ok = ~np.isnan(mean_citer_rl)
    y, yr, mcr = cd[ei][ok], year[ei][ok], mean_citer_rl[ok]

    frl = nref_full[ei][ok]   # focal's own full reference length (the other length driver)
    b_year = _ols_year_coef(y, [yr])
    b_year_c = _ols_year_coef(y, [yr, frl, mcr])   # control BOTH length drivers
    xb = np.column_stack([np.ones_like(y), yr, frl, mcr])
    coef = np.linalg.lstsq(xb, y, rcond=None)[0]
    b_frl, b_mcr = float(coef[2]), float(coef[3])
    atten = 1.0 - abs(b_year_c) / abs(b_year) if b_year != 0 else float("nan")
    print("\n(1) MEDIATION (control focal + citer reference-length):")
    print(f"  β_year (raw)                    = {b_year:+.5f}")
    print(f"  β_year | focal+citer reflen     = {b_year_c:+.5f}   ({atten * 100:.0f}% attenuated)")
    print(f"  β_focal-reflen                  = {b_frl:+.6f}   (expect <0: more focal refs ⇒ CD↓)")
    print(f"  β_mean-citer-reflen             = {b_mcr:+.6f}   (expect <0: more citer refs ⇒ CD↓)")

    # (2) length-cap counterfactual — cap all refs to the early-era typical (with-refs) length
    early = nref_full[(year < 1980) & (nref_full > 0)]
    cap = int(np.median(early)) if early.size else 6
    rng = np.random.default_rng(SEED)
    refs_cap = _refs_idx(cs["refs"], idx, cap, rng)
    cd_cap = cd_index(refs_cap, min_citers=MIN_CITERS, focals=list(ei))
    m2 = ~np.isnan(cd_cap[ei])
    b_year_cap = float(np.polyfit(year[ei][m2], cd_cap[ei][m2], 1)[0]) if int(m2.sum()) >= 30 \
        else float("nan")
    atten_cap = 1.0 - abs(b_year_cap) / abs(b_year) if b_year != 0 else float("nan")
    print(f"\n(2) LENGTH-CAP (refs→{cap}, early-era level; {int(m2.sum()):,} focals survive):")
    print(f"  β_year (capped) = {b_year_cap:+.5f}  ({atten_cap * 100:.0f}% att.; sparse cap)")

    gate = atten >= 0.5 and (b_frl < 0 or b_mcr < 0)
    print(f"\nPre-registered gate (≥50% mediation attenuation AND a length coef<0): "
          f"{'MET ✓' if gate else 'NOT met'}")


if __name__ == "__main__":
    main()
