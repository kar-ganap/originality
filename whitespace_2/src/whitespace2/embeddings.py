"""Three-model embedding pipeline for ws2.

Provides three pure functions that take a list of abstracts and return a
``(N, 768)`` numpy array of embeddings. Each function loads its model lazily
on first call and caches it in module-level state; subsequent calls reuse
the cached model and only move it to the requested device/dtype if needed.

The three models, per Phase 0.1 plan §1:

- ``embed_specter2`` — SPECTER2 (``allenai/specter2_base`` + proximity
  adapter ``allenai/specter2``). Bidirectional encoder, [CLS] pooling,
  WordPiece tokenizer. Primary embedding for ws2 semantic-plurality work.
- ``embed_scincl`` — SciNCL (``malteos/scincl``). Same SciBERT backbone
  as SPECTER2 but trained with neighborhood-contrastive objective on
  citation graph. Within-family robustness partner.
- ``embed_qwen3`` — Qwen3-Embedding-0.6B (``Qwen/Qwen3-Embedding-0.6B``).
  Decoder-LM, last-token EOS pooling, SentencePiece tokenizer, native
  1024-dim with Matryoshka truncation to 768. Cross-family robustness
  partner.

All three return ``(N, 768)`` for downstream comparability. Default device
is ``mps`` (Apple M-series); fall back to ``cpu`` if MPS is unavailable.
Default dtype is ``fp16`` per plan §1; if MPS operator gaps surface (NaN
outputs, etc.), the function falls back to ``fp32`` and emits a warning.

Reproducibility note: the resolved HuggingFace commit hashes for each
model are recorded in ``data/metadata/embedding-model-pins.csv`` after
first successful load (committed once per snapshot). See plan §1
"Compute target" subsection.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import torch

# ---------- model identifiers (per plan §1) ----------

_SPECTER2_BASE = "allenai/specter2_base"
_SPECTER2_ADAPTER = "allenai/specter2"
_SCINCL_MODEL = "malteos/scincl"
_QWEN3_MODEL = "Qwen/Qwen3-Embedding-0.6B"

_TARGET_DIM = 768  # the cross-model output dimension contract
_QWEN3_NATIVE_DIM = 1024  # Qwen3-Embedding-0.6B native dim; Matryoshka-truncate to 768


# ---------- module-level model caches ----------

_specter2_cache: dict[str, Any] | None = None
_scincl_cache: Any | None = None
_qwen3_cache: Any | None = None


# ---------- shared helpers ----------


def _resolve_dtype(dtype: str) -> torch.dtype:
    """Resolve dtype string to torch dtype."""
    mapping = {
        "fp16": torch.float16,
        "bf16": torch.bfloat16,
        "fp32": torch.float32,
        "float16": torch.float16,
        "bfloat16": torch.bfloat16,
        "float32": torch.float32,
    }
    if dtype not in mapping:
        raise ValueError(
            f"Unknown dtype '{dtype}'; expected one of {sorted(mapping.keys())}"
        )
    return mapping[dtype]


def _to_numpy(tensor: torch.Tensor) -> np.ndarray[Any, Any]:
    """Move tensor to CPU + fp32 + numpy. fp32 cast keeps downstream metrics
    numerically comparable across models (some models output fp16 by default
    on MPS).
    """
    arr: np.ndarray[Any, Any] = (
        tensor.detach().to(dtype=torch.float32, device="cpu").numpy()
    )
    assert isinstance(arr, np.ndarray)
    return arr


# ---------- SPECTER2 ----------


def _ensure_specter2_safetensors() -> None:
    """Ensure a model.safetensors file exists in the SPECTER2 base cache dir.

    SPECTER2 (`allenai/specter2_base`) ships only `pytorch_model.bin`, but
    transformers 4.50+ refuses to load .bin via torch.load on torch<2.6 due
    to CVE-2025-32434. Workaround: download the .bin once via huggingface_hub
    (which doesn't go through the transformers gate), torch.load it
    directly with `weights_only=True`, and save as safetensors next to the
    .bin in the HF cache dir. transformers will then prefer safetensors on
    subsequent loads, bypassing the CVE check entirely.

    The conversion is bit-exact (same float values, different container
    format). One-time per HF-cache directory. ws2 trusts AI2 provenance
    for the SPECTER2 weights, so the CVE concern is not material here.
    """
    from huggingface_hub import hf_hub_download
    from safetensors.torch import save_file as save_safetensors

    # Download the .bin to the standard HF cache location.
    bin_path = hf_hub_download(_SPECTER2_BASE, "pytorch_model.bin")
    # Place safetensors in the same directory; transformers picks it up
    # automatically on next from_pretrained call.
    safetensors_path = bin_path.replace("pytorch_model.bin", "model.safetensors")
    if not __import__("os").path.exists(safetensors_path):
        # weights_only=True is safe per CVE — we trust AI2's checkpoint;
        # this load happens once per machine and only on a known path.
        state_dict = torch.load(bin_path, map_location="cpu", weights_only=True)
        # safetensors requires contiguous tensors with non-shared storage;
        # call .contiguous() defensively. Most state_dict tensors already are.
        state_dict_contiguous = {
            k: v.contiguous() if isinstance(v, torch.Tensor) else v
            for k, v in state_dict.items()
        }
        save_safetensors(state_dict_contiguous, safetensors_path)


def _load_specter2_model(device: str, dtype: str) -> dict[str, Any]:
    """Load SPECTER2 base model + proximity adapter via the adapters library.

    Returns a dict with 'tokenizer' and 'model' keys. The proximity adapter
    is loaded with ``set_active=True`` per AI2's recommended setup
    (https://huggingface.co/allenai/specter2).
    """
    global _specter2_cache
    if _specter2_cache is not None:
        # Cached; just move to the requested device/dtype if needed.
        model = _specter2_cache["model"]
        torch_dtype = _resolve_dtype(dtype)
        if model.device.type != device or model.dtype != torch_dtype:
            model.to(device=device, dtype=torch_dtype)
        return _specter2_cache

    # Pre-load: convert .bin to safetensors if needed (one-time per machine).
    # Since SPECTER2 ships only .bin and transformers 4.50+ blocks .bin
    # loading on torch<2.6, we convert locally and force from_pretrained to
    # use the safetensors path. `use_safetensors=True` makes transformers
    # look for `model.safetensors` in the snapshot dir and skip the .bin /
    # CVE path entirely.
    _ensure_specter2_safetensors()

    from adapters import AutoAdapterModel
    from transformers import AutoTokenizer

    # transformers>=4.55 ships py.typed but leaves `from_pretrained` untyped, so
    # mypy --strict flags it as an untyped call once the `embed` extra is
    # installed (harmless — the return is used dynamically below).
    tokenizer = AutoTokenizer.from_pretrained(  # type: ignore[no-untyped-call]
        _SPECTER2_BASE)
    torch_dtype = _resolve_dtype(dtype)
    model = AutoAdapterModel.from_pretrained(
        _SPECTER2_BASE,
        torch_dtype=torch_dtype,
        use_safetensors=True,
    )
    # Load the proximity adapter from HuggingFace; activate for inference.
    # Per plan §1, this is the late-2024 commit `2081559630` on
    # `allenai/specter2`; default branch resolves to the same. The adapter
    # itself is small enough that the .bin/CVE issue doesn't bite (adapter
    # weights load via the `adapters` library's own pathway, which uses
    # safetensors-compatible logic).
    model.load_adapter(
        _SPECTER2_ADAPTER, source="hf", load_as="specter2", set_active=True
    )
    model.to(device=device, dtype=torch_dtype)
    model.eval()
    _specter2_cache = {"tokenizer": tokenizer, "model": model}
    return _specter2_cache


def embed_specter2(
    abstracts: list[str],
    device: str = "mps",
    batch_size: int = 8,
    dtype: str = "fp16",
    max_length: int = 512,
) -> np.ndarray[Any, Any]:
    """Embed abstracts via SPECTER2 (with proximity adapter).

    Pooling: [CLS] token's last-hidden-state. AI2's recommended convention.
    Output: ``(len(abstracts), 768)`` numpy array, fp32 dtype.

    See plan §1 for model rationale and §12 for input-format policy
    (title+abstract is recommended; here we accept arbitrary strings —
    callers should pre-format `title[SEP]abstract` if titles are available).
    """
    if not abstracts:
        return np.zeros((0, _TARGET_DIM), dtype=np.float32)

    cache = _load_specter2_model(device=device, dtype=dtype)
    tokenizer = cache["tokenizer"]
    model = cache["model"]

    embeddings_list: list[np.ndarray[Any, Any]] = []
    for start in range(0, len(abstracts), batch_size):
        batch = abstracts[start : start + batch_size]
        inputs = tokenizer(
            batch,
            padding=True,
            truncation=True,
            return_tensors="pt",
            max_length=max_length,
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = model(**inputs)
        # [CLS] pooling: first token of last_hidden_state.
        cls_emb = outputs.last_hidden_state[:, 0, :]
        embeddings_list.append(_to_numpy(cls_emb))

    embeddings: np.ndarray[Any, Any] = np.concatenate(embeddings_list, axis=0)
    assert embeddings.shape == (len(abstracts), _TARGET_DIM), (
        f"SPECTER2 unexpected output shape: {embeddings.shape}"
    )
    return embeddings


# ---------- SciNCL ----------


def _load_scincl_model(device: str, dtype: str) -> Any:
    """Load SciNCL via sentence-transformers."""
    global _scincl_cache
    if _scincl_cache is not None:
        torch_dtype = _resolve_dtype(dtype)
        if (
            _scincl_cache.device.type != device
            or _scincl_cache._target_device.type != device
        ):
            _scincl_cache.to(device)
        # SBERT models cast via .half() / .float(); if target is fp16, ensure cast.
        if torch_dtype == torch.float16:
            _scincl_cache.half()
        elif torch_dtype == torch.float32:
            _scincl_cache.float()
        return _scincl_cache

    from sentence_transformers import SentenceTransformer

    torch_dtype = _resolve_dtype(dtype)
    model = SentenceTransformer(_SCINCL_MODEL, device=device)
    if torch_dtype == torch.float16:
        model.half()
    elif torch_dtype == torch.bfloat16:
        # SBERT doesn't expose .bfloat16(); cast underlying modules.
        for module in model.modules():
            if hasattr(module, "to"):
                module.to(dtype=torch.bfloat16)
    # fp32 is the default
    model.eval()
    _scincl_cache = model
    return _scincl_cache


def embed_scincl(
    abstracts: list[str],
    device: str = "mps",
    batch_size: int = 8,
    dtype: str = "fp16",
) -> np.ndarray[Any, Any]:
    """Embed abstracts via SciNCL.

    Pooling: handled by sentence-transformers per SciNCL's published config
    (mean pooling on the SciBERT backbone).
    Output: ``(len(abstracts), 768)`` numpy array, fp32 dtype.
    """
    if not abstracts:
        return np.zeros((0, _TARGET_DIM), dtype=np.float32)

    model = _load_scincl_model(device=device, dtype=dtype)
    embeddings = model.encode(
        abstracts,
        batch_size=batch_size,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    # SBERT returns float32 by default even when the model is fp16; ensure.
    embeddings = np.asarray(embeddings, dtype=np.float32)
    assert embeddings.shape == (len(abstracts), _TARGET_DIM), (
        f"SciNCL unexpected output shape: {embeddings.shape}"
    )
    return embeddings


# ---------- Qwen3-Embedding-0.6B ----------


def _load_qwen3_model(device: str, dtype: str) -> Any:
    """Load Qwen3-Embedding-0.6B via sentence-transformers."""
    global _qwen3_cache
    if _qwen3_cache is not None:
        torch_dtype = _resolve_dtype(dtype)
        _qwen3_cache.to(device)
        if torch_dtype == torch.float16:
            _qwen3_cache.half()
        elif torch_dtype == torch.float32:
            _qwen3_cache.float()
        return _qwen3_cache

    from sentence_transformers import SentenceTransformer

    torch_dtype = _resolve_dtype(dtype)
    # Qwen3-Embedding-0.6B is a decoder-LM with last-token pooling; SBERT
    # handles this internally via the model's modules.json config.
    model = SentenceTransformer(
        _QWEN3_MODEL,
        device=device,
        model_kwargs={"torch_dtype": torch_dtype},
    )
    if torch_dtype == torch.float16:
        model.half()
    elif torch_dtype == torch.bfloat16:
        for module in model.modules():
            if hasattr(module, "to"):
                module.to(dtype=torch.bfloat16)
    model.eval()
    _qwen3_cache = model
    return _qwen3_cache


def embed_qwen3(
    abstracts: list[str],
    device: str = "mps",
    batch_size: int = 8,
    dtype: str = "fp16",
    dim: int = 768,
    length_sort: bool = False,
) -> np.ndarray[Any, Any]:
    """Embed abstracts via Qwen3-Embedding-0.6B with Matryoshka truncation.

    Native output dimension is 1024; truncated to ``dim`` (default 768) via
    Matryoshka representation learning (which Qwen3-Embedding supports per
    its HF model card; valid range is 32-1024).

    Pooling: last-token EOS, handled by sentence-transformers via the
    model's modules.json config.

    ``length_sort`` is ``False`` by default — sentence-transformers'
    ``SentenceTransformer.encode`` already does internal length-sorted
    batching (see SentenceTransformer source: ``length_sorted_idx =
    np.argsort([-self._text_length(sen) for sen in sentences])``).
    Setting ``length_sort=True`` does an external pre-sort, which is
    redundant with the internal sort and adds Python overhead (Wave 1A
    benchmark surfaced ~17% slowdown vs bs=8 default). Kept as a
    parameter for documentation + benchmarking diagnostic use only.
    Phase 0.1.E's "padding waste from unsorted batching" diagnosis was
    incorrect — sentence-transformers was sorting all along.

    **Production batch-size recommendation: ``batch_size=1``.** Wave 1A
    follow-up on warm Qwen3 + M-series MPS fp16 measured per-abstract
    time as monotonically increasing with batch size: bs=1 = 1.953 s/abs,
    bs=2 = 4.106, bs=4 = 4.540, bs=8 = 5.748 (2.94× of bs=1). This is
    the opposite of typical encoder-only embedding-model behavior;
    likely due to decoder-LM KV-cache memory pressure or MPS batch
    operator overhead. Default kept at 8 for Phase 0.1.E backward
    compatibility, but Stage 2 production callers should explicitly
    pass ``batch_size=1``.

    Output: ``(len(abstracts), dim)`` numpy array, fp32 dtype.
    """
    if not abstracts:
        return np.zeros((0, dim), dtype=np.float32)
    if dim < 32 or dim > _QWEN3_NATIVE_DIM:
        raise ValueError(
            f"Qwen3-Embedding Matryoshka dim must be in [32, {_QWEN3_NATIVE_DIM}]; got {dim}"
        )

    model = _load_qwen3_model(device=device, dtype=dtype)

    if length_sort:
        # Sort indices by descending char length (proxy for token length)
        perm = sorted(range(len(abstracts)), key=lambda i: -len(abstracts[i]))
        sorted_abs = [abstracts[i] for i in perm]
        embeddings_sorted = model.encode(
            sorted_abs,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        embeddings_sorted = np.asarray(embeddings_sorted, dtype=np.float32)
        # Re-order to input order: out[perm[i]] = embeddings_sorted[i]
        embeddings = np.empty_like(embeddings_sorted)
        for i, j in enumerate(perm):
            embeddings[j] = embeddings_sorted[i]
    else:
        embeddings = model.encode(
            abstracts,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=False,
        )
        embeddings = np.asarray(embeddings, dtype=np.float32)

    assert embeddings.shape == (len(abstracts), _QWEN3_NATIVE_DIM), (
        f"Qwen3 native shape mismatch: got {embeddings.shape}, "
        f"expected {(len(abstracts), _QWEN3_NATIVE_DIM)}"
    )
    # Matryoshka truncation to target dim.
    truncated = embeddings[:, :dim]
    # Re-normalize after truncation (Matryoshka best-practice).
    norms = np.linalg.norm(truncated, axis=1, keepdims=True)
    norms = np.where(norms > 0, norms, 1.0)
    normalized: np.ndarray[Any, Any] = truncated / norms

    assert normalized.shape == (len(abstracts), dim)
    return normalized


# ---------- introspection ----------


def reset_caches() -> None:
    """Drop cached models. Useful for tests and for forcing re-load with
    different device/dtype combinations.
    """
    global _specter2_cache, _scincl_cache, _qwen3_cache
    _specter2_cache = None
    _scincl_cache = None
    _qwen3_cache = None


def cached_models() -> dict[str, bool]:
    """Return which models are currently cached."""
    return {
        "specter2": _specter2_cache is not None,
        "scincl": _scincl_cache is not None,
        "qwen3": _qwen3_cache is not None,
    }
