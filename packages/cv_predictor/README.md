# cv-predictor

A fast **mean-field C/V diversity-collapse regime predictor**. It graduates the light
analytics of the Originality **Whitespace 3** ABM (the C/V reconciliation of the
population-complexity and small-team-disruption traditions) into a standalone, reusable
predictor — plus a Modal app for the heavy simulation path.

Given a system's conformity exponent `λ`, innovation rate `ε`, and fidelity `f`, it tells you
whether the system is **V-favouring** (per-capita persisting novelty *rises* with scale `N`)
or **C-favouring** (novelty *falls* with scale — a diversity collapse, while cumulative depth
`C` keeps accruing), and where the crossover conformity `λ*` sits.

## The law

Mean-field per-capita persisting novelty is hump-shaped in `N`:

```
V*(N) = ε · N^(−λ) · P(N),     P(N) = Galton–Watson non-extinction prob. of Poisson(N·f)
```

Persistence `P(N)` rises with more minds; the `N^(−λ)` consensus-suppression term falls.
Since `log V* = log ε − λ·log N + log P(N)`, the log–log slope is `d ln P/d ln N − λ`, so the
crossover is

```
λ* = d ln P/d ln N      (the persistence elasticity)
```

**V-favouring** below `λ*`, **C-favouring** above. Because persistence saturates fast
(`N·f ≫ 1 ⇒ P→1`), `λ*` is small at high fidelity — the crossover is most visible at low `f`,
where `P(N)` is still climbing across the population grid.

## Install

```bash
pip install 'git+https://github.com/…/originality#subdirectory=packages/cv_predictor'
# with the Modal serving extra:
pip install 'cv-predictor[modal] @ git+https://github.com/…/originality#subdirectory=packages/cv_predictor'
```

## Usage

```python
from cv_predictor import SystemParams, predict

fc = predict(SystemParams(lam=0.05, epsilon=0.3, f=0.15))
print(fc.regime)        # "V-favouring"
print(fc.lambda_star)   # ≈ 0.080  (crossover conformity)
print(fc.slope_at_lam)  # d ln V*/d ln N at λ=0.05  (> 0 ⇒ V-favouring)
print(fc.v_trajectory)  # V*(n) over n_grid
```

`predict` is pure mean-field (no simulation) — microseconds per call. The re-exported
analytics (`v_star_meanfield`, `branching_survival`, `crossover_lambda`,
`maintenance_threshold`, `carrier_fixed_point`) are the WS3 primitives it is built on.

### A note on fidelity

At **high fidelity** (e.g. `f=0.6`) persistence is already saturated across a typical grid, so
the mean-field `λ*` collapses toward 0 and essentially any scale-tracking conformity is
C-favouring. This is a real property, not a bug: the vivid `λ*≈0.09` crossover reported for
WS3 is the *simulation's* crossover; the mean-field predictor reproduces its **sign and
smallness**, and shows a clean V→C crossover in the low-fidelity regime (e.g. `f≈0.15`).

## Modal app (`ws3-cv-predictor`)

`modal_app.py` exposes `predict_endpoint` as a POST web endpoint and a documented
`calibrate` stub (the heavy ground-truth path that would run the full WS3 simulation for the
*simulated* `λ*`; it requires `whitespace3` installed in the Modal image and is intentionally
left unimplemented, since `whitespace3` is not a dependency of this package). The `modal`
import is guarded, so the module — and the rest of the package — works without modal
installed.

```bash
pip install 'cv-predictor[modal] @ …'
modal deploy modal_app.py
```

## Provenance

`src/cv_predictor/analytics.py` is lifted **byte-faithfully** from
`whitespace_3/src/whitespace3/analytics.py` (Originality WS3). `predictor.py` and
`modal_app.py` are new.

## Develop

```bash
uv run --extra dev ruff check .
uv run --extra dev mypy src
uv run --extra dev pytest -q
```
