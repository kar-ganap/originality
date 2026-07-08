"""WS3 Phase 2 · C-2c (the coverage battery) — is Park's decline a citation-COVERAGE artifact?
C-2b-full showed it is not a reference-LENGTH artifact; this tests the other prong. All
server-side on the 24M ws2-section0 population.

Three mechanisms (see phase-2-empirical-bridge-plan.md §10):
  (2) observation-window / accumulation asymmetry — we counted ALL-TIME citations, so old focals
      were watched 50 yrs, recent ones ~6. FIX: fixed forward-citation window W=5, W=10 (the
      Park-standard equal-window control); focals restricted to year ≤ max_year−W (uncensored).
  (3) field-growth / network size — corpus grows ⇒ the n_k pool grows ⇒ CD↓ mechanically. FIX:
      control the year-slope for log(papers published in the focal's year).
  (1) reference-recording completeness (old papers under-covered) — the free sub-period check
      already showed a UNIFORM slope across eras; here we confirm airtight with a born-digital
      clean cut (focals AND citers ≥ 2010).
Gate for each: the decline survives (slope < 0). Run from whitespace_2/:
uv run modal run experiments/phase-2-bridge/cd_data_C2c_coverage.py"""

from __future__ import annotations

import array
from typing import Any

import modal

app = modal.App("ws3-cd-coverage")
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("pyarrow>=15", "orjson>=3.10", "numpy>=1.24,<2", "scipy>=1.11", "pandas>=2")
    .add_local_python_source("whitespace2")
)
section0_volume = modal.Volume.from_name("ws2-section0", create_if_missing=False)
POP = "/pop/section0-population-v3.parquet"


@app.function(image=image, volumes={"/pop": section0_volume}, memory=131072, timeout=5400)
def cd_coverage(per_year: int = 2500, min_citers: int = 3, seed: int = 0) -> dict[str, Any]:
    import numpy as np
    import orjson
    import pyarrow.parquet as pq

    from whitespace2.v_extension import cd_index_csr

    pf = pq.ParquetFile(POP)
    n_rg = pf.num_row_groups
    id2idx: dict[str, int] = {}
    years: list[int] = []
    for i in range(n_rg):
        t = pf.read_row_group(i, columns=["id", "publication_year"])
        for pid, yr in zip(t.column("id").to_pylist(), t.column("publication_year").to_pylist()):
            id2idx[pid] = len(id2idx)
            years.append(int(yr) if yr else 0)
    n = len(id2idx)
    year = np.asarray(years, dtype=np.int32)
    print(f"Pass A done: {n:,}", flush=True)

    idx_arr = array.array("i")
    deg = np.zeros(n, dtype=np.int32)
    get = id2idx.get
    p = 0
    for i in range(n_rg):
        t = pf.read_row_group(i, columns=["referenced_works_json"])
        for rj in t.column("referenced_works_json").to_pylist():
            refs = orjson.loads(rj) if rj else []
            inpop = [j for r in refs if (j := get(r)) is not None]
            idx_arr.extend(inpop)
            deg[p] = len(inpop)
            p += 1
        if i % 150 == 0:
            print(f"Pass B rg {i}/{n_rg}", flush=True)
    indptr = np.zeros(n + 1, dtype=np.int64)
    np.cumsum(deg, out=indptr[1:])
    indices = np.frombuffer(idx_arr, dtype=np.int32)
    indeg = np.bincount(indices, minlength=n).astype(np.int32)
    max_year = int(year[(year >= 1970) & (year <= 2030)].max())
    # citers only exist among panel papers (≤2024); the 2025-2030 tail is future-dated noise. A
    # W-year forward window is COMPLETE only if focal_year + W ≤ LAST_COMPLETE. Snapshot 2026-03 ⇒
    # 2024 citing papers are indexed, so 2024 is the last complete citer year.
    last_complete = 2024
    tail = {int(y): int((year == y).sum()) for y in range(2023, 2031)}
    print(f"CSR built: {indices.size:,} edges; max_year {max_year}; year-tail {tail}", flush=True)

    rng = np.random.default_rng(seed)
    elig = (indeg >= min_citers) & (deg > 0) & (year >= 1970) & (year <= 2024)

    def _sample(lo: int, hi: int) -> np.ndarray:
        f: list[int] = []
        for y in range(lo, hi + 1):
            cand = np.flatnonzero(elig & (year == y))
            if cand.size:
                f.extend(rng.choice(cand, min(per_year, cand.size), replace=False).tolist())
        return np.asarray(f, dtype=np.int64)

    def _slope(cd: np.ndarray, fa: np.ndarray) -> dict[str, Any]:
        m = ~np.isnan(cd[fa])
        ff, cc = year[fa][m].astype(float), cd[fa][m]
        boot = [float(np.polyfit(ff[s], cc[s], 1)[0])
                for s in (rng.choice(ff.size, ff.size, replace=True) for _ in range(400))]
        lo, hi = np.percentile(boot, [2.5, 97.5])
        series = {int(y): round(float(cc[ff == y].mean()), 4) for y in np.unique(ff)}
        return {"slope": float(np.polyfit(ff, cc, 1)[0]), "ci": [float(lo), float(hi)],
                "mean_cd": float(cc.mean()), "n_focals": int(fa.size), "by_year": series}

    out: dict[str, Any] = {"n_papers": n, "edges": int(indices.size), "max_year": max_year}

    # baseline (un-windowed) + field-growth control
    fa = _sample(1970, 2024)
    cd_base = cd_index_csr(indptr, indices, min_citers=min_citers, focals=list(fa))
    out["baseline"] = _slope(cd_base, fa)
    papers_per_year = np.bincount(np.clip(year, 0, 2030))
    logc = np.log(np.maximum(papers_per_year[year[fa]], 1)).astype(float)
    mm = ~np.isnan(cd_base[fa])
    yv, yr, lc = cd_base[fa][mm], year[fa][mm].astype(float), logc[mm]
    b1 = float(np.linalg.lstsq(np.column_stack([np.ones_like(yv), yr]), yv, rcond=None)[0][1])
    b1c = float(np.linalg.lstsq(np.column_stack([np.ones_like(yv), yr, lc]), yv, rcond=None)[0][1])
    out["field_growth_control"] = {"b_year": b1, "b_year_ctrl_logcorpus": b1c,
                                   "attenuation": 1.0 - abs(b1c) / abs(b1) if b1 else float("nan")}

    # fixed forward-citation windows — uncensored focals only (focal_year + W ≤ last_complete)
    out["last_complete_year"] = last_complete
    for w in (5, 10):
        fw = fa[year[fa] <= last_complete - w]
        cdw = cd_index_csr(indptr, indices, min_citers=min_citers, focals=list(fw),
                           year=year, window=w)
        out[f"window_{w}"] = _slope(cdw, fw)

    # born-digital clean cut (focals + citers >= 2010)
    fbd = _sample(2010, 2024)
    cd_bd = cd_index_csr(indptr, indices, min_citers=min_citers, focals=list(fbd),
                         year=year, year_min=2010)
    out["born_digital_2010"] = _slope(cd_bd, fbd)
    return out


@app.local_entrypoint()
def main() -> None:
    import json
    print(json.dumps(cd_coverage.remote(), indent=2))


if __name__ == "__main__":
    main()
