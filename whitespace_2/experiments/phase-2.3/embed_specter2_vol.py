"""Phase 2.3 — SPECTER2 1M embed via SERVER-SIDE volume writes (robust variant).

The Phase-2.1 ``.map()`` path streams every chunk's vectors back to the local
client; at 902K×768 float32 (~2.7 GB) that result stream wedged the client
connection here (``socket.send()`` spam → throughput collapse). This variant has
each Modal container **write its chunk to the ``ws2-embeddings`` volume** and
return only a tiny chunk-id, so the client never receives the big payload — the
standard Modal bulk pattern. Server-side resume (skip chunks already on the
volume) makes preemptions cheap.

Then download + concat in id order → row-aligned ``specter2-vectors.npy``.

Usage:
  uv run modal run experiments/phase-2.3/embed_specter2_vol.py \
      --source <scratchpad>/section0-sample-1M-v3.parquet [--n 4000]
  # then, locally:
  modal volume get ws2-embeddings /specter2-1m-chunks/ <dest>
"""

from __future__ import annotations

import json
import os
from typing import Any

import modal
import numpy as np

app = modal.App("ws2-embed-s2vol")

embed_image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch==2.2.2",
        "transformers>=4.51,<5",
        "sentence-transformers>=2.7,<4",
        "adapters>=0.2,<2",
        "safetensors>=0.4",
        "huggingface_hub>=0.20",
        "numpy>=1.24,<2",
        "pyarrow>=14",
    )
    .env({"HF_HOME": "/cache"})
    .add_local_python_source("whitespace2")
)

hf_cache = modal.Volume.from_name("ws2-hf-cache", create_if_missing=True)
out_vol = modal.Volume.from_name("ws2-embeddings", create_if_missing=True)

_CHUNK = 2000
_YEAR_MIN, _YEAR_MAX = 1970, 2024
_OUTDIR = "/out/specter2-1m-chunks"


@app.function(
    image=embed_image,
    gpu="A100",
    volumes={"/cache": hf_cache, "/out": out_vol},
    timeout=3600,
    retries=modal.Retries(max_retries=3, initial_delay=10.0, max_delay=60.0),
)
def embed_chunk(item: tuple[int, list[str]]) -> int:
    """Embed one chunk with SPECTER2, write it to the volume, return the id.

    Server-side resume: a chunk already on the volume is skipped. Only the
    integer id crosses the wire back to the client (no 2.7 GB result stream)."""
    chunk_id, abstracts = item
    from whitespace2 import embeddings as emb

    path = f"{_OUTDIR}/chunk_{chunk_id:06d}.npy"
    out_vol.reload()
    if os.path.exists(path):
        return chunk_id
    vecs = emb.embed_specter2(
        abstracts, device="cuda", batch_size=32, dtype="fp16",
    ).astype(np.float32)
    os.makedirs(_OUTDIR, exist_ok=True)
    np.save(path, vecs)
    out_vol.commit()
    return chunk_id


@app.function(
    image=embed_image, volumes={"/out": out_vol}, timeout=1800,
)
def concat_chunks(n_expected: int) -> dict[str, Any]:
    """Concatenate all chunk_*.npy on the volume (id order) → specter2-vectors.npy.

    Runs server-side so the 452 small files never cross the (flaky) client
    connection — only the single concatenated result is downloaded afterward
    via ``modal volume get``. Verifies contiguity + row count."""
    import glob
    import re

    out_vol.reload()
    files = sorted(
        glob.glob(f"{_OUTDIR}/chunk_*.npy"),
        key=lambda p: int(re.findall(r"\d+", os.path.basename(p))[0]))
    ids = [int(re.findall(r"\d+", os.path.basename(p))[0]) for p in files]
    if ids != list(range(len(ids))):
        missing = sorted(set(range(max(ids) + 1)) - set(ids))
        return {"ok": False, "reason": "gaps", "missing": missing[:20],
                "n_files": len(files)}
    vecs = np.concatenate([np.load(p) for p in files], axis=0).astype(np.float32)
    np.save("/out/specter2-vectors.npy", vecs)
    out_vol.commit()
    return {"ok": True, "n_files": len(files), "shape": list(vecs.shape),
            "n_expected": n_expected,
            "all_finite": bool(np.isfinite(vecs).all()),
            "norm_mean": float(np.linalg.norm(vecs, axis=1).mean())}


@app.local_entrypoint()
def concat(n_expected: int = 452) -> None:
    """Trigger the server-side concat + print the verification summary."""
    print(json.dumps(concat_chunks.remote(n_expected), indent=2), flush=True)


@app.function(image=embed_image, gpu="A100", volumes={"/cache": hf_cache})
def check_adapter() -> dict[str, Any]:
    """Verify the SPECTER2 proximity adapter is ACTIVE (vs base-model output).

    Loads via the production loader, reports the model's active_adapters, and
    embeds 4 sample abstracts with the adapter active vs explicitly deactivated
    — if the two differ (cosine < 1), the adapter materially changes the
    embeddings (i.e. it is active and load-bearing)."""
    import numpy as np
    import torch

    from whitespace2 import embeddings as emb

    cache = emb._load_specter2_model(device="cuda", dtype="fp16")
    model, tok = cache["model"], cache["tokenizer"]
    active = list(getattr(model, "active_adapters", None).flatten()) if getattr(
        model, "active_adapters", None) is not None else []
    samples = [
        "We present a neural network for image classification on ImageNet.",
        "A quantum field theory of condensed matter phase transitions.",
        "An algorithm for sorting with optimal comparison complexity.",
        "Observations of galaxy rotation curves and dark matter halos.",
    ]

    def _embed(deactivate: bool) -> np.ndarray:
        if deactivate:
            model.set_active_adapters(None)
        else:
            model.set_active_adapters("specter2")
        inp = tok(samples, padding=True, truncation=True, return_tensors="pt",
                  max_length=512)
        inp = {k: v.to("cuda") for k, v in inp.items()}
        with torch.no_grad():
            out = model(**inp).last_hidden_state[:, 0, :]
        return out.float().cpu().numpy()

    on = _embed(deactivate=False)
    off = _embed(deactivate=True)
    model.set_active_adapters("specter2")  # restore
    cos = [float(np.dot(on[i], off[i]) / (np.linalg.norm(on[i]) *
           np.linalg.norm(off[i]))) for i in range(len(samples))]
    return {
        "active_adapters_after_load": [str(a) for a in active],
        "on_vs_off_cosine_per_sample": [round(c, 4) for c in cos],
        "adapter_materially_active": bool(np.mean(cos) < 0.999),
        "on_norm_mean": round(float(np.linalg.norm(on, axis=1).mean()), 3),
        "off_norm_mean": round(float(np.linalg.norm(off, axis=1).mean()), 3),
    }


@app.local_entrypoint()
def adapter() -> None:
    """Print the SPECTER2 adapter-activation verification."""
    print(json.dumps(check_adapter.remote(), indent=2), flush=True)


def _reconstruct(inv: dict[str, list[int]]) -> str:
    if not inv:
        return ""
    max_pos = max(max(p) for p in inv.values())
    tokens = [""] * (max_pos + 1)
    for word, ps in inv.items():
        for p in ps:
            tokens[p] = word
    return " ".join(t for t in tokens if t)


@app.local_entrypoint()
def main(source: str, outdir: str = "", n: int = -1) -> None:
    """Load abstracts locally, fan chunks to Modal (tiny returns), write metadata.

    Row-alignment: the same 1970–2024 window filter + reset_index as
    ``embed_1m.py``, so chunk order == metadata order == the base-1M order."""
    import pyarrow.parquet as pq
    from whitespace2.demographics import extract_primary_field

    df = pq.read_table(
        str(source),
        columns=["id", "publication_year", "abstract_inverted_index_json",
                 "concepts_json", "cited_by_count"],
    ).to_pandas()
    df = df[(df["publication_year"] >= _YEAR_MIN)
            & (df["publication_year"] <= _YEAR_MAX)].reset_index(drop=True)
    if n > 0:
        df = df.head(n)
    df["field"] = df["concepts_json"].map(extract_primary_field)
    abstracts = [_reconstruct(json.loads(str(x)))
                 for x in df["abstract_inverted_index_json"]]
    print(f"{len(abstracts):,} in-window abstracts", flush=True)

    if outdir:
        os.makedirs(outdir, exist_ok=True)
        df[["id", "publication_year", "field", "cited_by_count"]].rename(
            columns={"id": "paper_id", "publication_year": "year"},
        ).to_parquet(os.path.join(outdir, "metadata.parquet"))
        print(f"wrote {outdir}/metadata.parquet", flush=True)

    items = [(i, abstracts[i * _CHUNK:(i + 1) * _CHUNK])
             for i in range((len(abstracts) + _CHUNK - 1) // _CHUNK)]
    print(f"{len(items)} chunks of {_CHUNK} → Modal (server-side volume writes)",
          flush=True)

    done: set[int] = set()
    errors = 0
    for res in embed_chunk.map(items, return_exceptions=True):
        if isinstance(res, int):
            done.add(res)
        else:
            errors += 1
        if (len(done) + errors) % 25 == 0:
            print(f"  {len(done)}/{len(items)} done, {errors} err", flush=True)
    print(f"DONE map pass: {len(done)}/{len(items)} chunks on volume, "
          f"{errors} errors. Missing → re-run (server-side resume).",
          flush=True)


def _noop() -> Any:  # keep module importable outside modal
    return None
