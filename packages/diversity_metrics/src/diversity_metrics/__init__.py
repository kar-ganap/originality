"""diversity_metrics — vetted diversity, novelty, and concentration metrics.

Graduated from the Originality Whitespace-2 empirical study. Every function is a
behaviour-preserving lift of the corresponding WS2 metric (numpy in, numpy/scalar
out); see each module's provenance header for its source file.
"""

from diversity_metrics.concentration import gini, top_k_share
from diversity_metrics.divergence import (
    ols_trend,
    permutation_slope_test,
    standardized_effect,
)
from diversity_metrics.novelty import cd_index, reference_atypicality
from diversity_metrics.novelty_sparse import cd_index_csr
from diversity_metrics.semantic import (
    cluster_entropy,
    effective_dimensionality,
    mean_pairwise_cosine_distance,
)

__version__ = "0.1.0"

__all__ = [
    "cd_index",
    "cd_index_csr",
    "cluster_entropy",
    "effective_dimensionality",
    "gini",
    "mean_pairwise_cosine_distance",
    "ols_trend",
    "permutation_slope_test",
    "reference_atypicality",
    "standardized_effect",
    "top_k_share",
]
