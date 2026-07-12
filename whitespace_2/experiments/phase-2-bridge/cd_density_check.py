"""WS3 Phase 2 · C-2 step-0 go/no-go — is the FULL 24M population dense enough for a real CD graph?

The base-1m sample gave only 1.9% in-panel citation density (C-2a). The full v3 population
(24M papers, on Modal Volume `ws2-section0`) should be far denser. This measures, server-side
(never downloading 54.8 GB): the fraction of references pointing INTO the population (edge
density), the CD-eligibility distribution (papers with ≥3 in-population references), and both by
era. Decision rule: if in-population density clears ~30%, a dense-graph CD decomposition is
viable → proceed to steps 1–3; else stop and close C on the measure-contrast.

Run from whitespace_2/: uv run modal run experiments/phase-2-bridge/cd_density_check.py"""

from __future__ import annotations

from typing import Any

import modal

app = modal.App("ws3-cd-density")
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "pyarrow>=15", "orjson>=3.10", "numpy>=1.24,<2",
)
section0_volume = modal.Volume.from_name("ws2-section0", create_if_missing=False)
POP = "/pop/section0-population-v3.parquet"


@app.function(image=image, volumes={"/pop": section0_volume}, memory=98304, timeout=2400)
def density() -> dict[str, Any]:
    import orjson
    import pyarrow.parquet as pq

    pf = pq.ParquetFile(POP)
    n_rg = pf.num_row_groups
    print(f"population row-groups: {n_rg}; rows: {pf.metadata.num_rows:,}")

    # 1. id set over ALL row groups (id column only)
    ids: set[str] = set()
    for i in range(n_rg):
        ids.update(pf.read_row_group(i, columns=["id"]).column("id").to_pylist())
    print(f"id set built: {len(ids):,}")

    # 2. sample evenly-spaced row groups for refs; measure density + eligibility + era
    step = max(1, n_rg // 40)
    sample_rgs = list(range(0, n_rg, step))
    tot_refs = in_pop = npapers = elig1 = elig3 = elig5 = 0
    era: dict[str, list[int]] = {}   # era -> [in_pop_refs, papers, elig3]
    for i in sample_rgs:
        t = pf.read_row_group(i, columns=["referenced_works_json", "publication_year"])
        rjs = t.column("referenced_works_json").to_pylist()
        yrs = t.column("publication_year").to_pylist()
        for rj, yr in zip(rjs, yrs):
            refs = orjson.loads(rj) if rj else []
            k = sum(1 for r in refs if r in ids)
            tot_refs += len(refs)
            in_pop += k
            npapers += 1
            elig1 += k >= 1
            elig3 += k >= 3
            elig5 += k >= 5
            e = ("pre-1990" if (yr or 0) < 1990 else
                 "1990-2009" if (yr or 0) < 2010 else "2010+")
            era.setdefault(e, [0, 0, 0])
            era[e][0] += k
            era[e][1] += 1
            era[e][2] += k >= 3

    return {
        "n_population": len(ids),
        "sampled_papers": npapers,
        "mean_refs_per_paper": tot_refs / max(npapers, 1),
        "mean_in_pop_refs_per_paper": in_pop / max(npapers, 1),
        "density_in_population": in_pop / max(tot_refs, 1),
        "cd_eligible_frac_ge1": elig1 / max(npapers, 1),
        "cd_eligible_frac_ge3": elig3 / max(npapers, 1),
        "cd_eligible_frac_ge5": elig5 / max(npapers, 1),
        "by_era": {e: {"density_in_pop_refs": v[0] / max(v[1], 1),
                       "papers": v[1], "elig3_frac": v[2] / max(v[1], 1)}
                   for e, v in sorted(era.items())},
    }


@app.local_entrypoint()
def main() -> None:
    import json
    print(json.dumps(density.remote(), indent=2))


if __name__ == "__main__":
    main()
