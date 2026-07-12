# diversity-metrics

Small, dependency-light (`numpy` + `scipy`) library of **diversity, novelty, and
concentration metrics** operating on plain numpy arrays. Each function takes
arrays in and returns a scalar / array / dict out — no framework, no I/O, no
global state.

## What's inside

| Module | Functions |
| --- | --- |
| `diversity_metrics.semantic` | `effective_dimensionality`, `mean_pairwise_cosine_distance`, `cluster_entropy` |
| `diversity_metrics.concentration` | `gini`, `top_k_share` |
| `diversity_metrics.novelty` | `reference_atypicality`, `cd_index` (dense) |
| `diversity_metrics.novelty_sparse` | `cd_index_csr` (scipy.sparse CSR engine, same CD arithmetic as `cd_index`) |
| `diversity_metrics.divergence` | `ols_trend`, `permutation_slope_test`, `standardized_effect` |

Every public function is also re-exported from the top-level package:

```python
from diversity_metrics import gini, effective_dimensionality, cd_index
```

## Provenance

These functions were **graduated byte-faithfully** from the Originality
research program's Whitespace-2 empirical study
(`whitespace_2/src/whitespace2/`: `semantic_metrics.py`, `canonical_metrics.py`,
`v_extension.py`, `divergence.py`). They are behaviour-preserving copies — the
exact bodies, type hints, and docstrings that were validated there — lifted into
a standalone, reusable package. Each module carries a provenance header naming
its source file.

## Install

```
pip install 'git+https://github.com/kar-ganap/originality.git#subdirectory=packages/diversity_metrics'
```

## Develop

```
uv run --extra dev ruff check .
uv run --extra dev mypy src
uv run --extra dev pytest -q
```
