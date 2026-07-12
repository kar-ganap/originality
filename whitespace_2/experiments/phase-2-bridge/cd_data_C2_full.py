"""WS3 Phase 2 · C-2 (full-graph) — reproduce + decompose Park's CD-decline on the DENSE 24M
citation graph (step-0 density GO: 46.7% in-population). All server-side on the ws2-section0
Volume (54.8 GB population never downloaded).

Builds the within-population reference graph as CSR, then computes CD (vendored `cd_index_csr`,
scipy-sparse) for a per-year focal sample on:
  (uncapped)  the real graph — C-2a-full: does the decline replicate cleanly (now 41% eligible
              across all eras, so NOT the sample's selection-biased 0.85%)?
  (capped)    each paper's reference list truncated to the early-era length `cap` (removes the
              length-inflation the Petersen-Holst-Macher critique blames) — C-2b-full: does the
              decline ATTENUATE? Mirror of the model's C-1b (which ADDED length to flip CD down).

Population is all-field (CS+physics per the §0 pull); focal CD uses the full graph (Park-style).
Run from whitespace_2/: uv run modal run experiments/phase-2-bridge/cd_data_C2_full.py"""

from __future__ import annotations

import array
from typing import Any

import modal

app = modal.App("ws3-cd-full")
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install("pyarrow>=15", "orjson>=3.10", "numpy>=1.24,<2", "scipy>=1.11", "pandas>=2")
    .add_local_python_source("whitespace2")
)
section0_volume = modal.Volume.from_name("ws2-section0", create_if_missing=False)
POP = "/pop/section0-population-v3.parquet"


@app.function(image=image, volumes={"/pop": section0_volume}, memory=131072, timeout=5400)
def cd_full(
    cap: int = 8, per_year: int = 2500, min_citers: int = 3, seed: int = 0,
) -> dict[str, Any]:
    import numpy as np
    import orjson
    import pyarrow.parquet as pq

    from whitespace2.v_extension import cd_index_csr

    pf = pq.ParquetFile(POP)
    n_rg = pf.num_row_groups

    # Pass A — id → idx (read order) + publication_year
    id2idx: dict[str, int] = {}
    years: list[int] = []
    for i in range(n_rg):
        t = pf.read_row_group(i, columns=["id", "publication_year"])
        for pid, yr in zip(t.column("id").to_pylist(), t.column("publication_year").to_pylist()):
            id2idx[pid] = len(id2idx)
            years.append(int(yr) if yr else 0)
    n = len(id2idx)
    year = np.asarray(years, dtype=np.int32)
    print(f"Pass A done: {n:,} papers", flush=True)

    # Pass B — build uncapped + length-capped in-population reference CSR.
    # cap = RANDOM subset of the full ref list (seeded) — removes length-inflation without the
    # order-bias of a first-`cap` truncation (papers often cite foundational work first).
    rng = np.random.default_rng(seed)
    unc_idx, cap_idx = array.array("i"), array.array("i")
    unc_deg = np.zeros(n, dtype=np.int32)
    cap_deg = np.zeros(n, dtype=np.int32)
    full_reflen = np.zeros(n, dtype=np.int32)
    get = id2idx.get
    p = 0
    for i in range(n_rg):
        t = pf.read_row_group(i, columns=["referenced_works_json"])
        for rj in t.column("referenced_works_json").to_pylist():
            refs = orjson.loads(rj) if rj else []
            full_reflen[p] = len(refs)
            inpop = [j for r in refs if (j := get(r)) is not None]
            unc_idx.extend(inpop)
            unc_deg[p] = len(inpop)
            if len(refs) > cap:
                keep = rng.choice(len(refs), cap, replace=False)
                capped = [refs[k] for k in keep]
            else:
                capped = refs
            inpop_c = [j for r in capped if (j := get(r)) is not None]
            cap_idx.extend(inpop_c)
            cap_deg[p] = len(inpop_c)
            p += 1
        if i % 100 == 0:
            print(f"Pass B rg {i}/{n_rg}", flush=True)

    def _csr(deg: np.ndarray, idxarr: array.array) -> tuple[np.ndarray, np.ndarray]:
        indptr = np.zeros(n + 1, dtype=np.int64)
        np.cumsum(deg, out=indptr[1:])
        return indptr, np.frombuffer(idxarr, dtype=np.int32)

    u_ip, u_ix = _csr(unc_deg, unc_idx)
    c_ip, c_ix = _csr(cap_deg, cap_idx)
    print(f"CSR built: {u_ix.size:,} uncapped edges, {c_ix.size:,} capped", flush=True)

    # mean full-reference-length of each paper's citers (the mediation length driver), vectorized:
    # (R.T @ full_reflen)[e] = sum over citers i of e of full_reflen[i].
    from scipy.sparse import csr_matrix
    rmat = csr_matrix((np.ones(u_ix.size, dtype=np.int8), u_ix, u_ip), shape=(n, n))
    indeg = np.asarray(rmat.sum(axis=0)).ravel().astype(np.int64)
    mean_citer_reflen = rmat.T.dot(full_reflen.astype(np.float64)) / np.maximum(indeg, 1)

    # focal sampling — per-year, CD-eligible (>= min_citers in-pop citers, has in-pop refs)
    elig = (indeg >= min_citers) & (unc_deg > 0) & (year >= 1970) & (year <= 2024)
    focals: list[int] = []
    for y in range(1970, 2025):
        cand = np.flatnonzero(elig & (year == y))
        if cand.size:
            focals.extend(rng.choice(cand, min(per_year, cand.size), replace=False).tolist())
    fa = np.asarray(focals, dtype=np.int64)
    print(f"focals: {fa.size:,} ({int(elig.sum()):,} eligible total)", flush=True)

    cd_u = cd_index_csr(u_ip, u_ix, min_citers=min_citers, focals=focals)
    cd_c = cd_index_csr(c_ip, c_ix, min_citers=min_citers, focals=focals)
    fy = year[fa].astype(float)

    def _slope(cd: np.ndarray) -> dict[str, Any]:
        m = ~np.isnan(cd[fa])
        ff, cc = fy[m], cd[fa][m]
        boot = []
        idxs = np.arange(ff.size)
        for _ in range(400):
            s = rng.choice(idxs, idxs.size, replace=True)
            boot.append(float(np.polyfit(ff[s], cc[s], 1)[0]))
        lo, hi = np.percentile(boot, [2.5, 97.5])
        series = {int(y): round(float(cc[ff == y].mean()), 4) for y in np.unique(ff)}
        return {"slope": float(np.polyfit(ff, cc, 1)[0]), "ci": [float(lo), float(hi)],
                "mean_cd": float(cc.mean()), "n": int(m.sum()), "by_year": series}

    ru, rc = _slope(cd_u), _slope(cd_c)
    atten = 1.0 - abs(rc["slope"]) / abs(ru["slope"]) if ru["slope"] != 0 else float("nan")

    # mediation (independent of the cap): does the year-slope attenuate when we control for the
    # focal's own reference length AND its citers' mean reference length (the length drivers)?
    def _ols_year(y: np.ndarray, cols: list[np.ndarray]) -> float:
        xb = np.column_stack([np.ones_like(y), *cols])
        beta, *_ = np.linalg.lstsq(xb, y, rcond=None)
        return float(beta[1])

    mm = ~np.isnan(cd_u[fa])
    yv, yrv = cd_u[fa][mm], fy[mm]
    frl, mcr = full_reflen[fa][mm].astype(float), mean_citer_reflen[fa][mm]
    b1 = _ols_year(yv, [yrv])
    b1c = _ols_year(yv, [yrv, frl, mcr])
    atten_med = 1.0 - abs(b1c) / abs(b1) if b1 != 0 else float("nan")

    growth = {int(y): round(float(full_reflen[year == y].mean()), 1) for y in range(1970, 2025, 10)}
    return {
        "n_papers": n, "uncapped_edges": int(u_ix.size), "cap": cap, "per_year": per_year,
        "n_eligible": int(elig.sum()), "n_focals": int(fa.size),
        "ref_growth_by_decade": growth,
        "uncapped": ru, "capped": rc, "attenuation_under_cap": float(atten),
        "mediation": {"b_year": b1, "b_year_ctrl_reflen": b1c, "attenuation": float(atten_med)},
    }


@app.local_entrypoint()
def main() -> None:
    import json
    print(json.dumps(cd_full.remote(), indent=2))


if __name__ == "__main__":
    main()
