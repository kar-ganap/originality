"""WS2 Phase 2.4 — build the paper-level panel (the reproducible 2.4a step).

Regenerates ``data/base-1m/panel-2.4.parquet`` from the section-0 corpus + the base-1M
field labels, adds the in-sample forward-citation uptake (windows 3/5/10) and the
off-canon reference share (alpha=5%). Run once:
``uv run python experiments/phase-2.4/build_panel.py``.

Inputs (pull from Modal first, see docs/phases/phase-2.4-plan.md):
  data/base-1m/section0-sample-1M-v3.parquet   (ws2-section0)   — corpus w/ refs/authors/concepts
  data/base-1m/metadata.parquet                (ws2-embeddings) — paper_id/year/field, row-aligned

Output (git-ignored, regenerable): data/base-1m/panel-2.4.parquet.
"""

from __future__ import annotations

import time

from whitespace2.v_extension import build_panel, forward_uptake, off_canon_share

CORPUS = "data/base-1m/section0-sample-1M-v3.parquet"
META = "data/base-1m/metadata.parquet"
OUT = "data/base-1m/panel-2.4.parquet"


def main() -> None:
    t0 = time.time()
    panel = build_panel(CORPUS, META)
    print(f"panel: {len(panel):,} rows, {time.time() - t0:.0f}s to parse")

    t1 = time.time()
    for w in (3, 5, 10):
        panel[f"uptake_{w}"] = forward_uptake(
            panel["paper_id"].to_list(), panel["year"].to_list(), panel["refs"].to_list(), window=w
        )
    print(f"in-sample forward-citation graph (3 windows): {time.time() - t1:.0f}s")

    t2 = time.time()
    panel["off_canon"] = off_canon_share(
        panel["year"].to_numpy(), panel["refs"].to_numpy(), alpha=0.05
    )
    print(f"off-canon share (alpha=5%): {time.time() - t2:.0f}s")

    panel.to_parquet(OUT)
    print(f"wrote {OUT}  "
          f"(fields {panel['field'].value_counts().to_dict()}; "
          f"with-refs {(panel['n_refs'] > 0).mean():.3f})")


if __name__ == "__main__":
    main()
