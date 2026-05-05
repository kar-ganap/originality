"""Chunked, resumable embedding runner for Stage 2 production embeds.

Pattern:

1. Split abstracts into chunks of ``chunk_size``.
2. For each chunk: embed via ``model_fn``, save to
   ``chunk_<NNNNNN>.npy``, then atomic-append the chunk_id to
   ``done.txt``.
3. On restart, skip chunks already in ``done.txt``; detect +
   re-embed corrupted chunks (npy load failure or wrong shape).

Designed for Modal A100 preemptible compute where SIGTERM-style
preemption can happen at any point. Resume cost is bounded to one
chunk's worth of work (typically <1 minute at chunk_size=1000 on
A100).

See ``docs/phases/phase-1.1-plan.md`` for context.

Race-window guarantees
----------------------

Two race windows during normal operation:

(a) Crash AFTER ``np.save`` returns but BEFORE the ``done.txt``
    atomic-append: chunk file exists with valid contents, but the
    runner doesn't trust it (chunk_id not in done.txt) and
    re-embeds. Idempotent because ``model_fn`` is deterministic
    given the same input.

(b) Crash DURING the ``done.txt`` atomic-append: the rename is
    atomic on POSIX, so done.txt is either the OLD content or
    the NEW content — never partial. Either way, the runner's
    state on restart is consistent.

The ``done.txt`` write uses write-to-tmp + ``fsync`` + ``rename``,
which is atomic on POSIX filesystems used in Modal containers.

Output validation
-----------------

On restart, each chunk file in done.txt is validated by
attempting ``np.load`` and checking the shape against expected
``(chunk_actual_size, output_dim)``. Validation failures (load
exception, wrong shape) trigger re-embedding.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

import numpy as np

_DONE_FILENAME = "done.txt"
_DONE_TMP_SUFFIX = ".tmp"
_CHUNK_FILENAME_TEMPLATE = "chunk_{:06d}.npy"


class ChunkedEmbedRunner:
    """Resumable, chunk-by-chunk embedding driver.

    ``model_fn`` should be a deterministic function:
    ``list[str] → np.ndarray[N, D]``. Determinism is required for
    the resume-correctness guarantee — preempted chunks get
    re-embedded and must produce byte-identical output.
    """

    def __init__(
        self,
        model_fn: Callable[[list[str]], np.ndarray[Any, Any]],
        chunk_size: int,
        output_dir: Path | str,
    ) -> None:
        if chunk_size < 1:
            raise ValueError(
                f"chunk_size must be >= 1; got {chunk_size}"
            )
        self._model_fn = model_fn
        self._chunk_size = chunk_size
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

    @property
    def done_path(self) -> Path:
        return self._output_dir / _DONE_FILENAME

    def chunk_path(self, chunk_id: int) -> Path:
        return self._output_dir / _CHUNK_FILENAME_TEMPLATE.format(chunk_id)

    def _read_done(self) -> set[int]:
        if not self.done_path.exists():
            return set()
        with self.done_path.open() as f:
            return {
                int(line.strip()) for line in f if line.strip()
            }

    def _atomic_append_done(self, chunk_id: int) -> None:
        """Atomic-append by reading current contents, writing tmp, renaming.

        On POSIX, ``rename`` is atomic, so ``done.txt`` is always
        either the old content or the new content — never partial.
        """
        current = self._read_done()
        current.add(chunk_id)
        tmp_path = self.done_path.with_suffix(_DONE_TMP_SUFFIX)
        with tmp_path.open("w") as f:
            for cid in sorted(current):
                f.write(f"{cid}\n")
            f.flush()
            os.fsync(f.fileno())
        tmp_path.rename(self.done_path)

    def _chunk_valid(
        self, chunk_id: int, expected_shape: tuple[int, ...],
    ) -> bool:
        """True iff chunk file exists, loads cleanly, and has expected shape."""
        path = self.chunk_path(chunk_id)
        if not path.exists():
            return False
        try:
            v = np.load(path)
        except (ValueError, OSError, EOFError):
            return False
        return tuple(v.shape) == expected_shape

    def _detect_output_dim(self, abstracts: list[str], done: set[int]) -> int:
        """Determine output dim from any existing chunk; else probe model_fn."""
        for cid in sorted(done):
            path = self.chunk_path(cid)
            if path.exists():
                try:
                    sample = np.load(path)
                    return int(sample.shape[1])
                except (ValueError, OSError, EOFError):
                    continue
        # No valid existing chunk; probe with the first abstract
        sample = self._model_fn([abstracts[0]])
        return int(sample.shape[1])

    def run(
        self, abstracts: list[str],
    ) -> np.ndarray[Any, Any]:
        """Embed all abstracts, resuming from any prior state on disk.

        Returns: ``np.ndarray[len(abstracts), output_dim]``. Output
        order matches input order (chunks concatenated in chunk_id
        order).
        """
        n_total = len(abstracts)
        if n_total == 0:
            raise ValueError("no abstracts to embed")

        n_chunks = (n_total + self._chunk_size - 1) // self._chunk_size
        done = self._read_done()
        output_dim = self._detect_output_dim(abstracts, done)

        for chunk_id in range(n_chunks):
            start = chunk_id * self._chunk_size
            end = min(start + self._chunk_size, n_total)
            expected_shape = (end - start, output_dim)

            if chunk_id in done and self._chunk_valid(
                chunk_id, expected_shape,
            ):
                # Skip — already complete + valid on disk
                continue

            # Either not in done, OR done.txt says complete but
            # file is missing/corrupted. Re-embed in both cases
            # (idempotent because model_fn is deterministic).
            chunk_abstracts = abstracts[start:end]
            vectors = self._model_fn(chunk_abstracts)
            if tuple(vectors.shape) != expected_shape:
                raise ValueError(
                    f"model_fn returned shape {vectors.shape} for chunk "
                    f"{chunk_id}; expected {expected_shape}"
                )

            np.save(self.chunk_path(chunk_id), vectors)
            self._atomic_append_done(chunk_id)

        # Final concat in chunk_id order
        all_vectors: list[np.ndarray[Any, Any]] = []
        for chunk_id in range(n_chunks):
            v = np.load(self.chunk_path(chunk_id))
            all_vectors.append(v)
        return np.concatenate(all_vectors, axis=0)
