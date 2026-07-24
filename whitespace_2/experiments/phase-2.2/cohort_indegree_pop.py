"""Compute complete windowed in-degree for the field-labeled panel, over the 24M population graph.

    uv run modal run experiments/phase-2.2/cohort_indegree_pop.py

The local panel's `uptake_W` counts citers only inside the 902K sample (1.93% of edges), and the
in-sample rate rises over time, so its trend is untrustworthy. This recovers **complete** in-degree:
for every paneled paper, citations received from anywhere in the 24M `ws2-section0` population,
within a fixed forward window — the accrual-fair measure `age_restricted_concentration` needed.

Server-side, mirroring the WS3 bridge C-2c graph build. Returns one small row per paneled paper
(`indeg_alltime`, `indeg_w5`, `indeg_w10`, plus field and year); all concentration + null + battery
work happens locally in `cohort_concentration_pop.py` against the tested pure functions, so the
science can be re-run without re-spending.
"""

from __future__ import annotations

from typing import Any

import modal

app = modal.App("ws2-cohort-indegree")
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("pyarrow>=15", "orjson>=3.10", "numpy>=1.24,<2", "pandas>=2")
    .add_local_python_source("whitespace2")
    .add_local_file(
        "data/base-1m/panel-field-map.parquet", "/panel/panel-field-map.parquet"
    )
)
section0_volume = modal.Volume.from_name("ws2-section0", create_if_missing=False)
POP = "/pop/section0-population-v3.parquet"
PANEL_MAP = "/panel/panel-field-map.parquet"
LAST_COMPLETE_YEAR = 2024
WINDOWS = (5, 10)


@app.function(image=image, volumes={"/pop": section0_volume}, memory=131072, timeout=5400)
def cohort_indegree() -> dict[str, Any]:
    import numpy as np
    import orjson
    import pyarrow.parquet as pq

    # Pass A — id -> row index and publication year for every population paper.
    pf = pq.ParquetFile(POP)
    id2idx: dict[str, int] = {}
    years: list[int] = []
    for i in range(pf.num_row_groups):
        table = pf.read_row_group(i, columns=["id", "publication_year"])
        for pid, yr in zip(
            table.column("id").to_pylist(), table.column("publication_year").to_pylist()
        ):
            id2idx[pid] = len(id2idx)
            years.append(int(yr) if yr else 0)
    n = len(id2idx)
    year = np.asarray(years, dtype=np.int32)
    print(f"Pass A done: {n:,} population papers", flush=True)

    # The panel supplies field labels; the population has none. A paneled paper is a target we
    # measure; every population paper is a potential citer.
    panel = pq.read_table(PANEL_MAP).to_pandas()
    panel_idx = np.array(
        [id2idx.get(pid, -1) for pid in panel["paper_id"]], dtype=np.int64
    )
    found = panel_idx >= 0
    print(f"panel papers mapped into population: {int(found.sum()):,} / {len(panel):,}", flush=True)
    is_panel = np.zeros(n, dtype=bool)
    is_panel[panel_idx[found]] = True

    # Pass B — walk every citer's references once, accumulating in-degree for paneled targets only.
    indeg_alltime = np.zeros(n, dtype=np.int64)
    indeg_windowed = {w: np.zeros(n, dtype=np.int64) for w in WINDOWS}
    p = 0
    for i in range(pf.num_row_groups):
        table = pf.read_row_group(i, columns=["referenced_works_json"])
        for payload in table.column("referenced_works_json").to_pylist():
            citer_year = year[p]
            for ref in (orjson.loads(payload) if payload else []):
                j = id2idx.get(ref, -1)
                if j < 0 or not is_panel[j]:
                    continue
                indeg_alltime[j] += 1
                delta = citer_year - year[j]
                if delta < 0:
                    continue
                for w in WINDOWS:
                    if delta <= w:
                        indeg_windowed[w][j] += 1
            p += 1
        if i % 150 == 0:
            print(f"Pass B row-group {i}/{pf.num_row_groups}", flush=True)
    onto_panel = int(indeg_alltime[is_panel].sum())
    print(f"Pass B done: {onto_panel:,} in-pop edges onto panel", flush=True)

    # One compact row per paneled paper — the only thing that leaves Modal.
    rows = []
    for local_i in np.flatnonzero(found):
        gi = int(panel_idx[local_i])
        rows.append(
            {
                "paper_id": panel["paper_id"].iloc[int(local_i)],
                "field": panel["field"].iloc[int(local_i)],
                "year": int(year[gi]),
                "indeg_alltime": int(indeg_alltime[gi]),
                "indeg_w5": int(indeg_windowed[5][gi]),
                "indeg_w10": int(indeg_windowed[10][gi]),
            }
        )
    return {
        "n_population": n,
        "last_complete_year": LAST_COMPLETE_YEAR,
        "n_panel_mapped": int(found.sum()),
        "rows": rows,
    }


@app.local_entrypoint()
def main() -> None:
    import json
    from pathlib import Path

    result = cohort_indegree.remote()
    out = Path("experiments/phase-2.2/cohort-indegree-pop.json")
    out.write_text(json.dumps(result))
    print(f"n_population={result['n_population']:,}  panel_mapped={result['n_panel_mapped']:,}")
    print(f"artifact -> {out}  ({len(result['rows']):,} paneled papers)")
