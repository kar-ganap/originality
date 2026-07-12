"""C-2 recon — can we build a within-panel citation graph? Check id-space match, field/year
coverage, within-panel citation density (does any paper have enough within-panel citers for CD?).
Run from whitespace_2/: uv run python experiments/phase-2-bridge/recon_cd.py"""

from __future__ import annotations

import pandas as pd

PANEL = "data/base-1m/panel-2.4.parquet"


def main() -> None:
    d = pd.read_parquet(PANEL, columns=["paper_id", "year", "n_refs", "refs", "field"])
    print(f"panel rows: {len(d):,}")
    print(f"fields:\n{d['field'].value_counts()}")
    print(f"year range: {int(d['year'].min())}–{int(d['year'].max())}")
    print(f"paper_id[0] = {d['paper_id'].iloc[0]!r}")
    r0 = d['refs'].iloc[0]
    r0s = list(r0[:3]) if r0 is not None else None
    print(f"refs[0][:3] = {r0s!r}  (n_refs={d['n_refs'].iloc[0]})")

    # id-space match: fraction of ref-instances pointing INTO the panel
    ids = set(d['paper_id'].astype(str))
    samp = d.sample(n=min(20_000, len(d)), random_state=0)
    hit, tot = 0, 0
    for r in samp['refs']:
        if r is None:
            continue
        for x in r:
            tot += 1
            if str(x) in ids:
                hit += 1
    print(f"\nid-space match: {hit:,}/{tot:,} ref-instances point INTO panel "
          f"({hit / max(tot, 1):.3f}) — the within-panel edge density")

    # ref-length growth (the artifact driver)
    g = d.groupby(d['year'] // 5 * 5)['n_refs'].mean()
    print(f"\nmean n_refs by 5-yr bin:\n{g.round(1)}")


if __name__ == "__main__":
    main()
