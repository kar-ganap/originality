"""cv_predictor — a fast mean-field C/V diversity-collapse regime predictor.

Graduates WS3's C/V mean-field analytics (the crossover law ``λ* = d ln P/d ln N``, Henrich
carrier-survival, the Galton–Watson persistence anchor) into a reusable predictor:
:func:`predict` maps :class:`SystemParams` to a :class:`RegimeForecast` telling you whether a
system is **V-favouring** (per-capita novelty rises with scale) or **C-favouring** (diversity
collapse) and where the crossover conformity ``λ*`` sits.
"""

from __future__ import annotations

from .analytics import (
    branching_survival,
    carrier_fixed_point,
    crossover_lambda,
    maintenance_threshold,
    v_star_meanfield,
)
from .predictor import RegimeForecast, SystemParams, predict

__all__ = [
    "branching_survival",
    "carrier_fixed_point",
    "crossover_lambda",
    "maintenance_threshold",
    "v_star_meanfield",
    "SystemParams",
    "RegimeForecast",
    "predict",
]

__version__ = "0.1.0"
