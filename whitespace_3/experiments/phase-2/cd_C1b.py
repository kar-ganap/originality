"""Phase 2 · Experiment C-1b — is the empirical CD-decline a reference-length artifact?

C-1 found the model's CD *rises* with κ and over birth-time (real PA concentration ⇒ more
apparent disruption), the OPPOSITE of Park's decline. The model holds reference-list length
FIXED. The Petersen-Holst-Macher critique attributes the empirical CD-decline to *rising*
reference-list lengths (more refs ⇒ citers more likely to share a ref with the focal ⇒ n_j↑ ⇒
CD↓). So: inject length-inflation into the model's DAG (later elements cite more, sampled
UNIFORMLY from earlier elements so the attachment *kernel* is unchanged — only length grows)
and test whether the CD-vs-birth slope flips from + to −. If it does, the model isolates the
artifact: with the real dynamics held fixed, only length-inflation produces a CD-decline.

Run: ``uv run python experiments/phase-2/cd_C1b.py``.
"""

from __future__ import annotations

import numpy as np

from whitespace3.channel import run
from whitespace3.measures import cd_index

KW = dict(c0=5, f=0.6, epsilon=0.3, b=0.5, generations=80, mode="targeted", alpha=0.15, lam=0.5)


def _inflate(prereqs: list[list[int]], birth: np.ndarray, infl: float,
             rng: np.random.Generator) -> list[list[int]]:
    """Add birth-proportional extra references (uniform over earlier elements) — pure
    length-inflation, attachment kernel untouched."""
    bmax = float(birth.max()) or 1.0
    base = float(np.mean([len(p) for p in prereqs])) or 1.0
    out: list[list[int]] = []
    for e, refs in enumerate(prereqs):
        k = int(round(infl * (float(birth[e]) / bmax) * base))
        if k > 0 and e > 0:
            k = min(k, e)
            extra = rng.choice(e, size=k, replace=False).tolist()
            out.append(list(refs) + extra)
        else:
            out.append(list(refs))
    return out


def _cd_birth_slope(prereqs: list[list[int]], birth: np.ndarray) -> float:
    cd = cd_index(prereqs, min_citers=3)
    m = ~np.isnan(cd)
    return float(np.polyfit(birth[m], cd[m], 1)[0]) if int(m.sum()) >= 30 else float("nan")


def main() -> None:
    print("=" * 64)
    print("C-1b · is the CD-decline a reference-LENGTH artifact?")
    print("inject length-inflation (kernel fixed); does CD-vs-birth flip −?")
    print("=" * 64)
    for infl in (0.0, 1.0, 2.0, 4.0):
        slopes = []
        for s in range(4):
            res = run(120, seed=s, **KW)
            pr = [list(map(int, p)) for p in res["prereqs"]]
            birth = np.asarray(res["birth"], dtype=float)
            rng = np.random.default_rng(1000 + s)
            infl_pr = _inflate(pr, birth, infl, rng)
            slopes.append(_cd_birth_slope(infl_pr, birth))
        sl = float(np.nanmean(slopes))
        tag = "CD FALLS ✓ (artifact reproduced)" if sl < -1e-4 else \
              ("flat" if abs(sl) <= 1e-4 else "CD still rises")
        print(f"  inflation×{infl:>3}: CD-vs-birth slope = {sl:+.5f}   {tag}")
    print("\nRead: if the slope crosses 0 → − as length-inflation grows, the empirical")
    print("CD-decline is reproducible from length-inflation ALONE, with the real")
    print("attachment dynamics (which push CD UP) held fixed ⇒ supports the")
    print("Petersen-Holst-Macher 'CD-decline is a citation-practice artifact' critique.")


if __name__ == "__main__":
    main()
