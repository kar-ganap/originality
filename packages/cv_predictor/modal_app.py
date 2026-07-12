"""Modal app ``ws3-cv-predictor`` — serves the fast mean-field predictor as a POST endpoint,
plus a documented ``calibrate`` stub for the heavy ground-truth simulation path.

The ``modal`` import is guarded so importing this module works WITHOUT modal installed
(``pip install 'cv-predictor[modal]'`` to enable). When modal is absent the endpoint/stub are
left as plain callables (so they stay importable and unit-testable); when present they are
registered on the app. Deploy with ``modal deploy modal_app.py``.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Callable
from typing import Any

from cv_predictor import SystemParams, predict

try:
    import modal
except ModuleNotFoundError:  # `modal` is an optional extra; keep the module usable without it.
    modal = None  # type: ignore[assignment]

MODAL_AVAILABLE: bool = modal is not None


def _identity(fn: Callable[..., Any]) -> Callable[..., Any]:
    """No-op decorator used when ``modal`` is not installed."""
    return fn


if MODAL_AVAILABLE:
    app = modal.App("ws3-cv-predictor")
    image = modal.Image.debian_slim().pip_install("numpy", "scipy")
    _function = app.function(image=image)
    _web = modal.web_endpoint(method="POST")
else:
    app = None
    image = None
    _function = _identity
    _web = _identity


@_function
@_web
def predict_endpoint(params: dict) -> dict:
    """POST a ``SystemParams`` dict (``lam``, ``epsilon``, ``f``, optional ``n_grid``) → the
    ``RegimeForecast`` as a dict."""
    forecast = predict(SystemParams(**params))
    return dataclasses.asdict(forecast)


@_function
def calibrate(params: dict) -> dict:
    """Ground-truth ``λ*`` via the FULL WS3 simulation — a documented stub, NOT implemented.

    The mean-field :func:`cv_predictor.predict` approximates the crossover only in sign and
    smallness; the *simulated* crossover (``λ*≈0.09``, WS3 rung 3/5a) is measured by running
    the real ABM: ``whitespace3.conformity.locate_lambda_star`` over
    ``whitespace3.channel.run``. That is deliberately NOT wired up here — ``whitespace3`` is
    not a dependency of this package (WS3 keeps its own lockfile/venv; whitespace
    independence). To enable it, add ``whitespace3`` to the Modal image (e.g.
    ``image.pip_install("whitespace3 @ ...")`` or ``image.add_local_python_source(...)``) and
    call the locator here, returning the simulated ``λ*`` and its seed-bootstrap CI.
    """
    raise NotImplementedError(
        "calibrate() runs the full WS3 simulation for the ground-truth λ*; it requires "
        "`whitespace3` installed in the Modal image (not a dependency of cv_predictor). "
        "See the docstring for how to wire it up."
    )
