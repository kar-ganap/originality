"""WS3 Phase 2 · Experiment C-2a (go/no-go) — does Park's CD-decline replicate on the OpenAlex
panel? CD (vendored `cd_index`) on the WITHIN-PANEL citation graph (invert `refs`), CS field,
CD-vs-year slope + seed-bootstrap CI. Pre-registered gate: slope < 0, CI excluding 0.

Boundary caveat (measured in recon_cd.py): base-1m is a 1M sample of the 24M population, so only
~1.9% of references point INTO the panel — the within-panel graph is sparse + eligibility is
citation-accumulation-biased (older papers have more in-panel citers). This experiment QUANTIFIES
that truncation (eligibility-by-year) so the go/no-go is evidence-based, not asserted.
Run from whitespace_2/: uv run python experiments/phase-2-bridge/cd_data_C2a.py"""

from __future__ import annotations

import numpy as np
import pandas as pd

from whitespace2.v_extension import cd_index

PANEL = "data/base-1m/panel-2.4.parquet"
MIN_CITERS = 3
SEED = 0


def _slope(year: np.ndarray, cd: np.ndarray) -> float:
    m = ~np.isnan(cd)
    return float(np.polyfit(year[m], cd[m], 1)[0]) if int(m.sum()) >= 30 else float("nan")


def main() -> None:
    d = pd.read_parquet(PANEL, columns=["paper_id", "year", "refs", "field"])
    cs = d[d["field"] == "cs"].reset_index(drop=True)
    print(f"CS papers: {len(cs):,}")

    idx = {pid: i for i, pid in enumerate(cs["paper_id"].astype(str))}
    refs_idx: list[list[int]] = []
    for r in cs["refs"]:
        rr = r if r is not None else []
        refs_idx.append([idx[str(x)] for x in rr if str(x) in idx])
    edges = sum(len(r) for r in refs_idx)
    print(f"within-panel edges: {edges:,} (mean in-panel refs/paper {edges / len(cs):.2f})")

    cd = cd_index(refs_idx, min_citers=MIN_CITERS)   # sparse ⇒ most papers skip cheaply
    year = cs["year"].to_numpy().astype(float)
    elig = ~np.isnan(cd)
    print(f"CD-eligible papers (≥{MIN_CITERS} in-panel citers): {int(elig.sum()):,} "
          f"({elig.mean():.4f} of CS)")

    # eligibility-by-year — the citation-accumulation selection bias
    ey = pd.Series(elig).groupby(cs["year"] // 10 * 10).mean()
    print(f"eligibility rate by decade:\n{(ey * 100).round(2)}")

    slope = _slope(year, cd)
    # seed-bootstrap CI over eligible focals
    rng = np.random.default_rng(SEED)
    ei = np.flatnonzero(elig)
    boot = []
    for _ in range(500):
        s = rng.choice(ei, size=ei.size, replace=True)
        boot.append(float(np.polyfit(year[s], cd[s], 1)[0]))
    lo, hi = np.percentile(boot, [2.5, 97.5])
    print(f"\nCD-vs-year slope (CS, within-panel) = {slope:+.5f}  95% CI [{lo:+.5f}, {hi:+.5f}]")
    print(f"mean CD (eligible) = {np.nanmean(cd):+.4f}")

    gate = slope < 0 and hi < 0
    print(f"\nPre-registered gate (slope<0, CI excludes 0): {'MET' if gate else 'NOT met'}")
    print("Read against the boundary caveat: if eligibility is <~2% and decade-skewed, a clean")
    print("Park replication is infeasible on this sample → pivot to the mechanism+driver")
    print("adjudication (ref-growth measured + C-1b bridge + H↑/atyp↑ robustness).")


if __name__ == "__main__":
    main()
