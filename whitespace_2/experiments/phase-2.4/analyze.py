"""WS2 Phase 2.4 — the committed, reproducible analysis of the per-capita V-extension.

Regenerates every headline finding from the cached panel + the tested measures in
``whitespace2.v_extension``. Run: ``uv run python experiments/phase-2.4/analyze.py``.

Data provenance (pinned): corpus ``ws2-section0/section0-sample-1M-v3.parquet`` +
vectors/clusters ``ws2-embeddings/base-1m/`` (Modal). The paper-level panel is built by
``v_extension.build_panel`` (see ``build_panel.py``); this script assumes
``data/base-1m/panel-2.4.parquet`` exists (regenerable, git-ignored). All randomness is
seeded, so the numbers are deterministic.

Pre-registration: ``../../whitespace_3/docs/primers/v-extension-empirical-spec.tex``.
Verdict: Core Claim 6 (per-capita structural novelty DECLINES) is DISCONFIRMED — it
RISES — and the rise is FRAGMENTATION (cross-subfield), not individual novelty.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from whitespace2.v_extension import (
    off_canon_share,
    panel_year_test,
    persistence_weight,
    reference_atypicality,
)

PANEL = "data/base-1m/panel-2.4.parquet"
CLUSTERS = "data/base-1m/scincl-cluster-assignments.npy"
META = "data/base-1m/metadata.parquet"
N_PERM = 2000
SEED = 0


def _prep(d: pd.DataFrame) -> pd.DataFrame:
    """Add the per-paper controls used by every panel test (log team size, log
    field-year volume)."""
    d = d.copy()
    d["log_team"] = np.log(d["team_size"].clip(lower=1))
    vol = d.groupby(["field", "year"]).size().rename("vol").reset_index()
    d = d.merge(vol, on=["field", "year"])
    d["log_vol"] = np.log(d["vol"])
    return d


def _yc(d: pd.DataFrame, outcome: str) -> dict[str, float]:
    """Partial year coefficient of ``outcome`` (team + volume + field-FE, permutation)."""
    return panel_year_test(
        d[outcome].to_numpy(), d["year"].to_numpy(), d["field"].to_numpy(),
        controls=[d["log_team"].to_numpy(), d["log_vol"].to_numpy()],
        n_perm=N_PERM, seed=SEED,
    )


def _line(label: str, r: dict[str, float]) -> str:
    return (f"  {label:32} coef={r['year_coef']:+.6f}  p={r['perm_pvalue']:.4f}  "
            f"absΔ={r['abs_change']:+.4f}  VIF={r['year_vif']:.1f}  n={r['n']:,}")


def within_group_atypicality(dr: pd.DataFrame, group: str, d_min: int = 10) -> np.ndarray:
    """Median co-reference z (Uzzi) recomputed WITHIN each ``group`` level — the
    fragmentation discriminator (no canon-accretion artifact)."""
    out = np.full(len(dr), np.nan)
    for _, idx in dr.groupby(group).indices.items():
        med, _ = reference_atypicality(dr.iloc[idx]["refs"].to_numpy(), d_min=d_min, min_pairs=3)
        out[idx] = med
    return out


def main() -> None:
    d = pd.read_parquet(PANEL)
    # ── measures ──
    if "off_canon" not in d.columns:
        d["off_canon"] = off_canon_share(d["year"].to_numpy(), d["refs"].to_numpy(), alpha=0.05)
    med, _ = reference_atypicality(d["refs"].to_numpy(), d_min=20, min_pairs=3)
    d["atyp_med"] = med
    d["persist"] = persistence_weight(d["uptake_5"].to_numpy(), d["field"].to_numpy(),
                                      d["year"].to_numpy())
    d["nu_struct"] = d["off_canon"] * d["persist"]

    print("=" * 78)
    print("HEADLINE — does per-capita structural novelty decline? (Core Claim 6)")
    print("  off_canon RISE = novelty↑ ;  atyp_med FALL (z↓) = novelty↑")
    print("=" * 78)
    s = _prep(d[d["off_canon"].notna() & (d["year"] <= 2019)])
    print(_line("nu_struct (off_canon×persist)", _yc(s, "nu_struct")))
    print(_line("off_canon (raw, a=5%)", _yc(s, "off_canon")))
    a = _prep(d[d["atyp_med"].notna() & (d["year"] <= 2023)])
    print(_line("atypicality median_z", _yc(a, "atyp_med")))
    print("  gradient + within-team-size (nu_struct):")
    for f in ("cs", "physics"):
        print(_line(f"  {f}", _yc(s[s["field"] == f], "nu_struct")))
    s2 = s.assign(tb=pd.cut(s["team_size"], [0, 1, 3, 9999], labels=["solo", "2-3", "4+"]))
    for b in ("solo", "2-3", "4+"):
        print(_line(f"  team {b}", _yc(s2[s2["tb"] == b], "nu_struct")))

    print("\n" + "=" * 78)
    print("NEGATIVE CONTROLS + robustness")
    print("=" * 78)
    rng = np.random.default_rng(42)
    allw: set[str] = set()
    for r in s["refs"]:
        allw.update(r.tolist())
    rand_canon = {w for w in allw if rng.random() < 0.05}
    s = s.assign(off_rand=[
        (1 - sum(1 for r in refs if r in rand_canon) / len(refs)) if len(refs) else np.nan
        for refs in s["refs"]])
    print(_line("random-canon placebo (must be flat)", _yc(s, "off_rand")))
    for al in (0.01, 0.10):
        s = s.assign(oc=off_canon_share(s["year"].to_numpy(), s["refs"].to_numpy(), alpha=al))
        print(_line(f"off_canon alpha={al}", _yc(s, "oc")))

    print("\n" + "=" * 78)
    print("FRAGMENTATION DISCRIMINATOR — within-subfield vs global atypicality")
    print("  global falls ≫ within-subfield flat  ⇒  novelty is CROSS-subfield (fragmentation)")
    print("=" * 78)
    clusters = np.load(CLUSTERS)
    meta = pd.read_parquet(META, columns=["paper_id"])
    d["cluster"] = d["paper_id"].map(dict(zip(meta["paper_id"].to_numpy(), clusters)))
    for group, gmin in (("subfield", 1000), ("cluster", 1000)):
        dr = d[(d["n_refs"] > 0) & (d[group].notna())].copy()
        big = dr[group].value_counts()
        dr = dr[dr[group].isin(big[big >= gmin].index)].reset_index(drop=True)
        dr["loc_atyp"] = within_group_atypicality(dr, group)
        gm, _ = reference_atypicality(dr["refs"].to_numpy(), d_min=20, min_pairs=3)
        dr["glob_atyp"] = gm
        ax = _prep(dr[dr["loc_atyp"].notna() & dr["glob_atyp"].notna() & (dr["year"] <= 2023)])
        print(f"  [{group}: {dr[group].nunique()} groups]")
        print(_line("    global atypicality", _yc(ax, "glob_atyp")))
        print(_line("    within-group atypicality", _yc(ax, "loc_atyp")))


if __name__ == "__main__":
    main()
