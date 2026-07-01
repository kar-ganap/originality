"""Phase 2.2 WS-F — the 3-panel figure (the reframing).

Demographic / semantic / canonical plurality per year (CS + Physics), 1970-2024.
The headline reading it makes visible: the citation CANON concentrates while the
semantic FRONTIER and AUTHORSHIP both diversify — the three do not co-narrow.
Semantic metrics (different native scales) are min-max normalized within the
panel; demographic (joint Shannon) and canonical (reference-canonicity Gini) are
raw. Light 3-yr rolling mean for readability; degenerate early years (N<768) are
lightened.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

_SER = Path(__file__).parent / "series"
_OUT = Path(__file__).parent / "figures"
_YEARS = range(1970, 2025)


def _roll(y: np.ndarray, w: int = 3) -> np.ndarray:
    if len(y) < w:
        return y
    k = np.ones(w) / w
    return np.convolve(y, k, mode="same")


def _norm(y: np.ndarray) -> np.ndarray:
    lo, hi = np.nanmin(y), np.nanmax(y)
    return (y - lo) / (hi - lo) if hi > lo else y * 0.0


def main() -> None:
    _OUT.mkdir(parents=True, exist_ok=True)
    sc = json.loads((_SER / "semantic-canonical.json").read_text())["fields"]
    dem = json.loads((_SER / "demographic-joint.json").read_text())

    fig, axes = plt.subplots(3, 1, figsize=(8.5, 9.5), sharex=True)
    styles = {"cs": ("-", "#1f77b4"), "physics": ("--", "#d62728")}

    for field, (ls, col) in styles.items():
        semd = sc[field]["semantic"]
        years = sorted(int(y) for y in semd if 1970 <= int(y) <= 2024)
        yr = np.array(years, float)

        # Panel A — demographic joint plurality
        dfield = dem[field]
        dv = np.array([dfield.get(str(y), np.nan) for y in years])
        axes[0].plot(yr, _roll(dv), ls, color=col, label=field.upper())

        # Panel B — semantic (3 metrics, min-max normalized)
        for metric, mstyle in [("cluster_entropy", 1.0),
                               ("effective_dimensionality", 0.6),
                               ("mean_pairwise_cosine", 0.3)]:
            mv = np.array([semd[str(y)][metric] for y in years])
            axes[1].plot(yr, _roll(_norm(mv)), ls, color=col, alpha=mstyle,
                         lw=1.6 if mstyle == 1.0 else 1.1)

        # Panel C — canonical (reference-canonicity Gini, raw)
        canon = {r["year"]: r["ref_gini"]
                 for r in sc[field]["canonical"]["reference_canonicity"]}
        cv = np.array([canon.get(y, np.nan) for y in years])
        axes[2].plot(yr, _roll(cv), ls, color=col, label=field.upper())

    axes[0].set_ylabel("Demographic plurality\n(joint Shannon, nats)")
    axes[0].set_title("Canon concentrates while frontier + authorship diversify "
                      "(CS solid, Physics dashed)", fontsize=11)
    axes[1].set_ylabel("Semantic plurality\n(3 metrics, min-max normalized)")
    axes[1].text(0.02, 0.92, "cluster-entropy (bold) / effective-dim / "
                 "pairwise-cosine", transform=axes[1].transAxes, fontsize=8,
                 va="top")
    axes[2].set_ylabel("Canonical concentration\n(reference-canonicity Gini)")
    axes[2].set_xlabel("Publication year")
    for ax in axes:
        ax.grid(alpha=0.25)
        ax.legend(loc="lower right", fontsize=8)
    axes[0].axvspan(1970, 1990, color="grey", alpha=0.06)  # thin/degenerate era
    fig.tight_layout()
    fig.savefig(_OUT / "phase2.2-3panel.png", dpi=150)
    print(f"wrote {_OUT}/phase2.2-3panel.png")


if __name__ == "__main__":
    main()
