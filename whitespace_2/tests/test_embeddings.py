"""Tests for the three-model embedding pipeline (Phase 0.1.E).

Tests the seven pre-registered hypotheses (H1-H7 in the Phase 0.1.E plan):

- H1: each model loads on the available device + dtype combo
- H2: output shape is (N, 768)
- H3: outputs are finite (no NaN/inf) on real inputs
- H4: outputs are batch-invariant within fp16 tolerance
- H5: outputs are distinct across distinct inputs
- H6: L2 norms are sane (either ≈1 if normalized, else bounded)
- H7: timing benchmark — verified in the smoke-test script, not here

All tests are slow-marked because they download and load 100MB-1GB models. Run
with ``pytest tests/test_embeddings.py -v -m slow`` (or ``make test-all``).
The default ``make test`` target excludes them.

The module skips entirely if torch is not importable (the embed extra not
installed). Device auto-detects MPS where available, falls back to CPU. fp16
is the default dtype per Phase 0.1 plan §1; tests are tolerant of the
fallback path documented in the plan.
"""

from __future__ import annotations

import pytest

torch = pytest.importorskip("torch", reason="embed extra not installed")
np = pytest.importorskip("numpy", reason="numpy required")


# ---------- shared fixtures / helpers ----------

# Three short, semantically-distinct abstracts in clearly different domains.
# Distinctness chosen so cosine similarity between any pair should be well
# below the H5 threshold (cos < 0.999) on any reasonable embedding.
_TEST_ABSTRACTS: list[str] = [
    "Recent advances in deep learning have transformed image classification "
    "by enabling end-to-end training of convolutional architectures on "
    "large-scale datasets, achieving superhuman accuracy on benchmark tasks.",
    "Quantum entanglement enables secure cryptographic key distribution "
    "between distant parties via the no-cloning theorem; eavesdropping "
    "introduces detectable disturbances in the quantum state.",
    "Phylogenetic analysis of mitochondrial DNA reveals evolutionary "
    "relationships between extant species and provides molecular-clock "
    "estimates for divergence times in primate lineages.",
]

_EXPECTED_DIM: int = 768


def _available_device() -> str:
    """Pick MPS where available, else CPU."""
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


# Lazy imports — fail at first test, not at module import, so a partial
# module install (e.g., transformers but not adapters) doesn't blow up
# collection of unrelated tests.


def _import_specter2():
    from whitespace2.embeddings import embed_specter2

    return embed_specter2


def _import_scincl():
    from whitespace2.embeddings import embed_scincl

    return embed_scincl


def _import_qwen3():
    from whitespace2.embeddings import embed_qwen3

    return embed_qwen3


_MODELS: list[tuple[str, callable]] = [
    ("specter2", _import_specter2),
    ("scincl", _import_scincl),
    ("qwen3", _import_qwen3),
]


# ---------- H1+H2+H3 — smoke (load, shape, finiteness) ----------


@pytest.mark.slow
@pytest.mark.parametrize("model_name,import_fn", _MODELS, ids=[m[0] for m in _MODELS])
def test_smoke_load_shape_finite(model_name: str, import_fn) -> None:
    """H1+H2+H3: model loads; output shape (N, 768); outputs finite."""
    embed_fn = import_fn()
    device = _available_device()
    embeddings = embed_fn(_TEST_ABSTRACTS, device=device, batch_size=4)

    # H2: shape contract
    assert isinstance(embeddings, np.ndarray), (
        f"{model_name}: expected np.ndarray, got {type(embeddings)}"
    )
    assert embeddings.shape == (len(_TEST_ABSTRACTS), _EXPECTED_DIM), (
        f"{model_name}: expected shape {(len(_TEST_ABSTRACTS), _EXPECTED_DIM)}, "
        f"got {embeddings.shape}"
    )

    # H3: finiteness
    assert np.isfinite(embeddings).all(), (
        f"{model_name}: embeddings contain NaN or inf — likely an MPS "
        f"operator gap; per plan §1, fall back to bfloat16 or fp32"
    )


# ---------- H4 — batch invariance ----------


@pytest.mark.slow
@pytest.mark.parametrize("model_name,import_fn", _MODELS, ids=[m[0] for m in _MODELS])
def test_batch_invariance(model_name: str, import_fn) -> None:
    """H4: embedding of the same input is invariant to batch size, within fp16 tolerance.

    Compares the embedding of ``[abstract_0]`` (single-item batch) against
    the first row of ``embed([abstract_0, abstract_1, abstract_2])`` (3-item
    batch). Tolerance is 5e-3 — fp16 numerical noise on MPS can be looser
    than on CUDA; conservative initial threshold per plan §1 risk
    acknowledgment.
    """
    embed_fn = import_fn()
    device = _available_device()

    single = embed_fn([_TEST_ABSTRACTS[0]], device=device, batch_size=1)
    batched = embed_fn(_TEST_ABSTRACTS, device=device, batch_size=4)

    assert single.shape == (1, _EXPECTED_DIM)
    assert batched.shape == (len(_TEST_ABSTRACTS), _EXPECTED_DIM)

    diff = np.abs(single[0] - batched[0]).max()
    assert diff < 5e-3, (
        f"{model_name}: batch-invariance failed (max abs diff = {diff:.4e}). "
        f"Likely cause: padding/masking inconsistency between batch sizes."
    )


# ---------- H5 + H6 — distinctness + norm sanity ----------


@pytest.mark.slow
@pytest.mark.parametrize("model_name,import_fn", _MODELS, ids=[m[0] for m in _MODELS])
def test_distinctness_and_norm_sanity(model_name: str, import_fn) -> None:
    """H5: unrelated inputs produce distinct vectors (pairwise cosine < 0.999).
    H6: L2 norms are bounded (≈1 if normalized; else within [0.5, 100]).
    """
    embed_fn = import_fn()
    device = _available_device()
    embeddings = embed_fn(_TEST_ABSTRACTS, device=device, batch_size=4)

    # H6: L2 norm sanity. We don't enforce normalization here — some models
    # post-hoc normalize, others don't. We assert the norms are in a sane
    # finite range. If norms vary by orders of magnitude across inputs,
    # pooling is broken.
    norms = np.linalg.norm(embeddings, axis=1)
    assert np.isfinite(norms).all(), f"{model_name}: non-finite L2 norms"
    assert (norms > 0.5).all() and (norms < 100.0).all(), (
        f"{model_name}: L2 norms outside [0.5, 100] — likely pooling bug. "
        f"Got norms = {norms}"
    )
    # Norm consistency: ratio of max to min norm should be < 10 (sane
    # variation across distinct inputs from a working pooler).
    norm_ratio = norms.max() / norms.min()
    assert norm_ratio < 10.0, (
        f"{model_name}: L2-norm ratio (max/min) = {norm_ratio:.2f} — "
        f"pooling likely producing inconsistent magnitudes across inputs"
    )

    # H5: pairwise cosine similarity < 0.999 across the three abstracts.
    # Normalize first so cosine is a simple dot product.
    normalized = embeddings / norms[:, np.newaxis]
    cos_01 = float(normalized[0] @ normalized[1])
    cos_02 = float(normalized[0] @ normalized[2])
    cos_12 = float(normalized[1] @ normalized[2])
    pairs = [("0,1", cos_01), ("0,2", cos_02), ("1,2", cos_12)]
    for label, cos in pairs:
        assert cos < 0.999, (
            f"{model_name}: cosine similarity for pair {label} = {cos:.4f}, "
            f"exceeds 0.999. Indicates pooling collapse or model-loading bug."
        )
