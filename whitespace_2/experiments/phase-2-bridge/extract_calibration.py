"""WS3 Phase 2 · Experiment B-1 — extract the ABM calibration parameters from the OpenAlex
panel, **off-trend** (structural statistics only, never the novelty trend). Writes a small
``calibration.json`` handoff for the WS3 side (B-2/B-3 calibrate + predict). Run from
``whitespace_2/``: ``uv run python experiments/phase-2-bridge/extract_calibration.py``.

Statistics (pinned snapshot = the panel-2.4 build):
  - **m** — reference-list length (→ the model's refs-per-paper). Coverage-caveated (~54%).
  - **within-subfield reference Gini** — the load-bearing calibration (→ the model's `bw`
    niche distinctiveness): how tightly a subfield cites a shared canon.
  - **q** — cross-cutting reference share (refs to works cited by many subfields).
  - **K(t)** — subfield count over time (the fragmentation growth).
Sampled to 200k with-refs papers for tractability (logged, not a silent cap).
"""

from __future__ import annotations

import json
import os

import numpy as np
import pandas as pd

PANEL = "data/base-1m/panel-2.4.parquet"
OUT = os.path.join(os.path.dirname(__file__), "calibration.json")
SAMPLE = 200_000
SEED = 0


def _gini(counts: np.ndarray) -> float:
    x = np.sort(counts.astype(float))
    if x.sum() <= 0 or x.size < 2:
        return 0.0
    n = x.size
    return float((n + 1 - 2 * np.cumsum(x).sum() / x.sum()) / n)


def main() -> None:
    d = pd.read_parquet(PANEL, columns=["year", "n_refs", "subfield", "refs", "field"])
    wr = d[(d["n_refs"] > 0) & d["subfield"].notna()].copy()
    print(f"with-refs+subfield papers: {len(wr):,} (of {len(d):,}; coverage "
          f"{(d['n_refs'] > 0).mean():.3f})")

    # m — reference-list length (coverage-caveated)
    m_median = float(wr["n_refs"].median())
    m_mean = float(wr["n_refs"].mean())
    m_substantial = float(wr.loc[wr["n_refs"] >= 5, "n_refs"].median())  # less coverage-biased

    # sample for the explode-heavy stats
    samp = wr.sample(n=min(SAMPLE, len(wr)), random_state=SEED)
    ex = samp[["subfield", "refs"]].explode("refs").dropna()
    ex["refs"] = ex["refs"].astype(str)
    print(f"exploded ref-instances (sample): {len(ex):,}")

    # within-subfield reference Gini — concentration of a subfield's citation targets
    ginis, sizes = [], []
    for sf, g in ex.groupby("subfield"):
        vc = g["refs"].value_counts().to_numpy()
        if vc.sum() >= 200:                      # enough refs to estimate concentration
            ginis.append(_gini(vc))
            sizes.append(vc.sum())
    ginis_a, sizes_a = np.asarray(ginis), np.asarray(sizes, dtype=float)
    gini_mean = float(np.mean(ginis_a))
    gini_wmean = float(np.average(ginis_a, weights=sizes_a))    # citation-weighted

    # q — cross-cutting share: refs to works cited by many subfields
    sf_per_work = ex.groupby("refs")["subfield"].nunique()
    broad = set(sf_per_work[sf_per_work >= 10].index)          # cited by >=10 subfields
    q = float(ex["refs"].isin(broad).mean())

    # between-subfield DISTINCTIVENESS (the real bw target): how niche-specific are refs?
    inst_breadth = ex["refs"].map(sf_per_work)                 # #subfields per cited work
    niche_specific_ref_share = float((inst_breadth == 1).mean())   # cited by exactly ONE subfield
    mean_ref_breadth = float(inst_breadth.mean())                  # avg #subfields per cited work
    median_ref_breadth = float(inst_breadth.median())

    # B'-1: niche-specific-share over the ATYPICALITY-relevant subset (heavily-cited works only).
    # reference_atypicality uses d_min=20 on the full panel; sample ~0.41x → sample d_min ≈ 8.
    work_deg = ex["refs"].value_counts()
    heavy = set(work_deg[work_deg >= 8].index)
    heavy_mask = ex["refs"].isin(heavy)
    ns_heavy = float((ex.loc[heavy_mask, "refs"].map(sf_per_work) == 1).mean())
    heavy_ref_frac = float(heavy_mask.mean())

    # K(t) — subfield count over time (fragmentation growth), on the full panel
    k_by_year = wr.groupby("year")["subfield"].nunique()
    early = float(k_by_year.loc[k_by_year.index <= 1985].mean())
    late = float(k_by_year.loc[k_by_year.index >= 2015].mean())

    cal = {
        "snapshot": "panel-2.4 (base-1m v3)",
        "n_papers_with_refs": int(len(wr)),
        "coverage": float((d["n_refs"] > 0).mean()),
        "m_ref_len_median": m_median,
        "m_ref_len_mean": m_mean,
        "m_ref_len_median_substantial": m_substantial,
        "within_subfield_ref_gini_mean": gini_mean,
        "within_subfield_ref_gini_wmean": gini_wmean,
        "n_subfields_scored": int(len(ginis)),
        "cross_cutting_q": q,
        "niche_specific_ref_share": niche_specific_ref_share,
        "mean_ref_breadth_subfields": mean_ref_breadth,
        "median_ref_breadth_subfields": median_ref_breadth,
        "niche_specific_ref_share_dmin": ns_heavy,     # B'-1: heavily-cited (atyp) works
        "heavy_ref_frac": heavy_ref_frac,
        "n_subfields_total": int(wr["subfield"].nunique()),
        "K_subfields_early_1985": early,
        "K_subfields_late_2015": late,
        "sample": int(len(samp)),
    }
    with open(OUT, "w") as fh:
        json.dump(cal, fh, indent=2)
    print(json.dumps(cal, indent=2))
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
