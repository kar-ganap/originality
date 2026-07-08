"""Rung 5b — at-scale verification of the phase-diagram crossover (Modal, detached).

A **focused (λ,N) sweep to N=1500** — NOT the stipulated full 6D N=3000 grid. `channel.run`
scales ~O(N²) (N=2000 ≈ 3 min/run), so the full grid is thousands of core-hours,
infeasible under `<$50` (the §6 "few CPU-seconds/cell" estimate was wrong at scale). This
slice verifies the crossover survives ~6× the laptop scale (N=240 → 1500). Scope logged
here + in the retro (no silent caps).

**Survives laptop shutdown.** The orchestration runs *on Modal* (a remote ``orchestrate``
function that does the ``.map`` server-side) and writes to a **Modal Volume**, so the local
client is not needed once launched. Run from ``whitespace_3/`` (needs ``modal token new``):
  smoke:  ``uv run --extra sweep modal run experiments/phase-1-rung5/modal_sweep.py --smoke``
  launch: ``uv run --extra sweep modal run --detach experiments/phase-1-rung5/modal_sweep.py``
          → prints a call id, returns immediately; close the laptop freely.
  fetch:  ``uv run --extra sweep modal run experiments/phase-1-rung5/modal_sweep.py --fetch``

Server-side scalar summaries only. Resumable: a re-launch skips cells already in the Volume;
``return_exceptions=True`` ⇒ a flaky cell costs one cell.
"""

import json
import os

import modal

LAMBDAS = [0.0, 0.1, 0.25, 0.5, 1.0]
NS = [200, 500, 1000, 1500]
SEEDS = list(range(15))
GENS, BURN = 100, 50
VOL = "/results"
RESULTS = "results-at-scale.jsonl"
SMOKE_RESULTS = "results-smoke.jsonl"

app = modal.App("ws3-at-scale-sweep")
image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install("numpy<2", "scipy>=1.11", "networkx>=3.2")
    .add_local_python_source("whitespace3")
)
vol = modal.Volume.from_name("ws3-at-scale-results", create_if_missing=True)


@app.function(image=image, timeout=1800)
def cell(args: tuple[float, int, int]) -> dict[str, float]:
    """One (λ, N, seed) cell: steady-state scalar summaries from the 5a phase-diagram model
    (well-mixed, uniform κ). Returns only scalars (server-side summary)."""
    import numpy as np

    from whitespace3.channel import run

    lam, n, seed = args
    r = run(n, 5, 0.6, 0.3, 0.5, GENS, seed, lam=lam, mode="uniform", alpha=0.15)
    return {
        "lam": lam, "n": n, "seed": seed,
        "V": float(np.nanmean(r["V"][BURN:])),
        "C": float(np.mean(r["C"][BURN:])),
        "Vstruct": float(np.nanmean(r["Vstruct"][BURN:])),
        "H": float(np.mean(r["H"][BURN:])),
    }


@app.function(image=image, volumes={VOL: vol}, timeout=10800)
def orchestrate(cells: list[tuple[float, int, int]], results_file: str) -> dict[str, int]:
    """Runs entirely on Modal: dispatches the cells via ``cell.map`` and streams scalar
    results into the Volume — so the sweep does not depend on the local client. Resumable."""
    vol.reload()
    path = os.path.join(VOL, results_file)
    done: set[tuple[float, int, int]] = set()
    if os.path.exists(path):
        for line in open(path):
            d = json.loads(line)
            done.add((d["lam"], d["n"], d["seed"]))
    todo = [tuple(c) for c in cells if tuple(c) not in done]
    n_ok = 0
    with open(path, "a") as fh:
        for res in cell.map(todo, return_exceptions=True):
            if isinstance(res, Exception):
                continue
            fh.write(json.dumps(res) + "\n")
            fh.flush()
            n_ok += 1
            if n_ok % 20 == 0:
                vol.commit()
    vol.commit()
    return {"cached": len(done), "dispatched": len(todo), "ok": n_ok}


@app.function(image=image, volumes={VOL: vol})
def read_results(results_file: str) -> list[dict[str, float]]:
    vol.reload()
    path = os.path.join(VOL, results_file)
    if not os.path.exists(path):
        return []
    return [json.loads(line) for line in open(path)]


def _aggregate(rows: list[dict[str, float]]) -> None:
    import numpy as np

    if not rows:
        print("(no results yet — the sweep may still be running; try --fetch again later)")
        return
    lams = sorted({r["lam"] for r in rows})
    n_cells = len({(r["lam"], r["n"], r["seed"]) for r in rows})
    print(f"\nAT-SCALE crossover — ∂V*/∂logN per λ  ({n_cells} cells, N up to "
          f"{max(r['n'] for r in rows)}):")
    for lam in lams:
        ns = sorted({r["n"] for r in rows if r["lam"] == lam})
        if len(ns) < 2:
            continue
        vmean = [float(np.mean([r["V"] for r in rows if r["lam"] == lam and r["n"] == n]))
                 for n in ns]
        cmean = [float(np.mean([r["C"] for r in rows if r["lam"] == lam and r["n"] == n]))
                 for n in ns]
        sV = float(np.polyfit(np.log(ns), vmean, 1)[0])
        sC = float(np.polyfit(np.log(ns), cmean, 1)[0])
        reg = "V-favouring" if sV > 0 else "C-favouring"
        print(f"  λ={lam:>4}: ∂V/∂logN={sV:+.4f} ({reg})  ∂C/∂logN={sC:+.3f}  "
              f"V(N={ns})={[round(v, 3) for v in vmean]}")


@app.local_entrypoint()
def main(smoke: bool = False, fetch: bool = False) -> None:
    rf = SMOKE_RESULTS if smoke else RESULTS
    if fetch:
        _aggregate(read_results.remote(rf))
        return
    if smoke:
        cells = [(le, n, s) for le in (0.0, 0.5) for n in (100, 200) for s in (0, 1)]
        print(f"SMOKE: {len(cells)} cells (blocking, server-side orchestrate)")
        print("orchestrate:", orchestrate.remote(cells, rf))
        _aggregate(read_results.remote(rf))
        return
    cells = [(le, n, s) for le in LAMBDAS for n in NS for s in SEEDS]
    handle = orchestrate.spawn(cells, rf)
    print(f"LAUNCHED detached orchestrator (call id: {handle.object_id}); {len(cells)} cells.")
    print("Safe to close the laptop — the sweep runs on Modal, results in Volume "
          "'ws3-at-scale-results'.")
    print("Fetch later:  uv run --extra sweep modal run "
          "experiments/phase-1-rung5/modal_sweep.py --fetch")
