"""``modal_app.py`` must import cleanly whether or not ``modal`` is installed.

It lives at the package root (not under ``src/``), so we load it by path.
"""

from __future__ import annotations

import importlib.util
import os
from types import ModuleType

import pytest

_MODAL_APP_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "modal_app.py"
)


def _load_modal_app() -> ModuleType:
    spec = importlib.util.spec_from_file_location("modal_app", _MODAL_APP_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_modal_app_imports_cleanly() -> None:
    mod = _load_modal_app()
    assert hasattr(mod, "predict_endpoint")
    assert hasattr(mod, "calibrate")
    assert isinstance(mod.MODAL_AVAILABLE, bool)


def test_predict_endpoint_logic() -> None:
    mod = _load_modal_app()
    if mod.MODAL_AVAILABLE:
        pytest.skip("modal installed; endpoint is wrapped as a modal Function")
    out = mod.predict_endpoint({"lam": 0.05, "epsilon": 0.3, "f": 0.15})
    assert out["regime"] == "V-favouring"
    assert set(out) == {"lambda_star", "regime", "slope_at_lam", "v_trajectory"}


def test_calibrate_is_documented_stub() -> None:
    mod = _load_modal_app()
    if mod.MODAL_AVAILABLE:
        pytest.skip("modal installed; calibrate is wrapped as a modal Function")
    with pytest.raises(NotImplementedError):
        mod.calibrate({"lam": 0.05, "epsilon": 0.3, "f": 0.15})
