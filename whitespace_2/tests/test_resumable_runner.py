"""Unit tests for ChunkedEmbedRunner — covers all SIGTERM race windows.

Per Phase 1.1 plan TEST plan (`docs/phases/phase-1.1-plan.md`):
6 cases covering clean run, chunked clean, kill mid-chunk, kill in
the post-save / pre-done race window, kill after done update, and
corrupted chunk file recovery.

All tests run locally with a deterministic synthetic embedding
function (no GPU). Total wall-clock <1 sec on M-series.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import numpy as np
import pytest

from whitespace2.resumable_runner import ChunkedEmbedRunner

# ---------- test fixtures ----------


_OUTPUT_DIM = 4


def _deterministic_embed(abstracts: list[str]) -> np.ndarray[Any, Any]:
    """Hash-based deterministic embedding; same input → same output."""
    vecs = np.zeros((len(abstracts), _OUTPUT_DIM), dtype=np.float32)
    for i, abs_str in enumerate(abstracts):
        h = int(hashlib.md5(abs_str.encode()).hexdigest()[:8], 16)
        vecs[i] = [
            (h % 100) / 100.0,
            ((h // 100) % 100) / 100.0,
            ((h // 10000) % 100) / 100.0,
            ((h // 1000000) % 100) / 100.0,
        ]
    return vecs


class _SimulatedPreemption(Exception):
    """Test-only exception simulating Modal preemption (SIGTERM)."""


class _KillAfterCalls:
    """Wraps a model_fn to raise after N successful invocations.

    Each call to model_fn counts as one "chunk's worth" of work. To
    simulate kill DURING chunk N's embedding: set kill_after=N
    (chunks 0..N-1 succeed, chunk N raises before returning).
    """

    def __init__(self, kill_after: int) -> None:
        self.kill_after = kill_after
        self.calls = 0

    def wrap(
        self,
        model_fn: Any,
    ) -> Any:
        def wrapped(abstracts: list[str]) -> np.ndarray[Any, Any]:
            if self.calls >= self.kill_after:
                raise _SimulatedPreemption(
                    f"simulated preemption at call {self.calls}"
                )
            self.calls += 1
            return model_fn(abstracts)

        return wrapped


# ---------- test 1: clean single-chunk run ----------


def test_runner_clean_run(tmp_path: Path) -> None:
    """100 abstracts × chunk_size=100 = 1 chunk; clean happy path."""
    abstracts = [f"abs {i}" for i in range(100)]
    runner = ChunkedEmbedRunner(
        model_fn=_deterministic_embed,
        chunk_size=100,
        output_dir=tmp_path / "out",
    )
    result = runner.run(abstracts)

    # Output shape correct
    assert result.shape == (100, _OUTPUT_DIM)
    # Matches direct embed
    expected = _deterministic_embed(abstracts)
    assert np.array_equal(result, expected)
    # Chunk file + done.txt populated
    assert (tmp_path / "out" / "chunk_000000.npy").exists()
    assert (tmp_path / "out" / "done.txt").exists()
    done_contents = (tmp_path / "out" / "done.txt").read_text().strip()
    assert done_contents == "0"


# ---------- test 2: chunked clean run ----------


def test_runner_chunked_clean(tmp_path: Path) -> None:
    """1000 abstracts × chunk_size=100 = 10 chunks; clean happy path."""
    abstracts = [f"abs {i}" for i in range(1000)]
    runner = ChunkedEmbedRunner(
        model_fn=_deterministic_embed,
        chunk_size=100,
        output_dir=tmp_path / "out",
    )
    result = runner.run(abstracts)

    assert result.shape == (1000, _OUTPUT_DIM)
    expected = _deterministic_embed(abstracts)
    assert np.array_equal(result, expected)
    # 10 chunk files + done.txt with 10 entries
    for cid in range(10):
        assert (tmp_path / "out" / f"chunk_{cid:06d}.npy").exists()
    done = sorted(
        int(line.strip())
        for line in (tmp_path / "out" / "done.txt").read_text().splitlines()
        if line.strip()
    )
    assert done == list(range(10))


# ---------- test 3: kill DURING chunk embedding ----------


def test_runner_kill_during_chunk(tmp_path: Path) -> None:
    """SIGTERM during chunk-7-embedding; restart resumes from chunk 7.

    Note: kill_after=8 because the runner does 1 dim-probe call before
    the chunk loop (no existing chunks to read dim from on first run).
    Probe (1) + chunks 0-6 (7) = 8 successful invocations; chunk 7
    embedding raises on the 9th invocation.
    """
    abstracts = [f"abs {i}" for i in range(1000)]
    out_dir = tmp_path / "out"

    kill = _KillAfterCalls(kill_after=8)
    runner1 = ChunkedEmbedRunner(
        model_fn=kill.wrap(_deterministic_embed),
        chunk_size=100,
        output_dir=out_dir,
    )
    with pytest.raises(_SimulatedPreemption):
        runner1.run(abstracts)
    # Verify chunks 0-6 saved; chunk 7+ NOT
    for cid in range(7):
        assert (out_dir / f"chunk_{cid:06d}.npy").exists()
    for cid in range(7, 10):
        assert not (out_dir / f"chunk_{cid:06d}.npy").exists()

    # Second run: clean model_fn, should resume + complete
    runner2 = ChunkedEmbedRunner(
        model_fn=_deterministic_embed,
        chunk_size=100,
        output_dir=out_dir,
    )
    result = runner2.run(abstracts)

    expected = _deterministic_embed(abstracts)
    assert np.array_equal(result, expected)


# ---------- test 4: kill in race window (chunk file written, done not updated) ----------


def test_runner_kill_after_chunk_before_done(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """SIGTERM AFTER chunk 5 saved but BEFORE done.txt update.

    On restart: chunk_5.npy exists with valid contents but is NOT in
    done.txt. Runner re-embeds chunk 5 (idempotent: same content).
    """
    abstracts = [f"abs {i}" for i in range(1000)]
    out_dir = tmp_path / "out"

    # Patch _atomic_append_done to raise on the 6th call (chunk 5)
    original_append = ChunkedEmbedRunner._atomic_append_done
    call_count = {"n": 0}

    def patched_append(self: Any, chunk_id: int) -> None:
        if call_count["n"] >= 5:
            raise _SimulatedPreemption("kill before done update for chunk 5")
        call_count["n"] += 1
        original_append(self, chunk_id)

    monkeypatch.setattr(
        ChunkedEmbedRunner, "_atomic_append_done", patched_append,
    )

    runner1 = ChunkedEmbedRunner(
        model_fn=_deterministic_embed,
        chunk_size=100,
        output_dir=out_dir,
    )
    with pytest.raises(_SimulatedPreemption):
        runner1.run(abstracts)

    # Chunk 5 file should exist (saved before the kill); done.txt has only 0-4
    assert (out_dir / "chunk_000005.npy").exists()
    done = sorted(
        int(line.strip())
        for line in (out_dir / "done.txt").read_text().splitlines()
        if line.strip()
    )
    assert done == [0, 1, 2, 3, 4]

    # Restart with un-patched _atomic_append_done
    monkeypatch.setattr(
        ChunkedEmbedRunner, "_atomic_append_done", original_append,
    )
    runner2 = ChunkedEmbedRunner(
        model_fn=_deterministic_embed,
        chunk_size=100,
        output_dir=out_dir,
    )
    result = runner2.run(abstracts)

    expected = _deterministic_embed(abstracts)
    assert np.array_equal(result, expected)


# ---------- test 5: kill RIGHT AFTER done.txt update ----------


def test_runner_kill_after_done_update(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """SIGTERM RIGHT AFTER chunk 5's done.txt update.

    On restart: chunks 0-5 in done.txt + valid files. Skip those;
    embed chunks 6-9.
    """
    abstracts = [f"abs {i}" for i in range(1000)]
    out_dir = tmp_path / "out"

    original_append = ChunkedEmbedRunner._atomic_append_done
    call_count = {"n": 0}

    def patched_append(self: Any, chunk_id: int) -> None:
        original_append(self, chunk_id)
        call_count["n"] += 1
        if call_count["n"] >= 6:  # raise AFTER chunk 5's append
            raise _SimulatedPreemption("kill after done update for chunk 5")

    monkeypatch.setattr(
        ChunkedEmbedRunner, "_atomic_append_done", patched_append,
    )

    runner1 = ChunkedEmbedRunner(
        model_fn=_deterministic_embed,
        chunk_size=100,
        output_dir=out_dir,
    )
    with pytest.raises(_SimulatedPreemption):
        runner1.run(abstracts)

    # done.txt has 0-5
    done = sorted(
        int(line.strip())
        for line in (out_dir / "done.txt").read_text().splitlines()
        if line.strip()
    )
    assert done == [0, 1, 2, 3, 4, 5]

    # Restart should skip 0-5 + embed 6-9
    monkeypatch.setattr(
        ChunkedEmbedRunner, "_atomic_append_done", original_append,
    )

    # Use a counter on model_fn to verify chunks 0-5 are NOT re-embedded
    skip_check = _KillAfterCalls(kill_after=999)  # never kills; just counts
    runner2 = ChunkedEmbedRunner(
        model_fn=skip_check.wrap(_deterministic_embed),
        chunk_size=100,
        output_dir=out_dir,
    )
    result = runner2.run(abstracts)

    # First run made 6 model_fn calls (chunks 0-5); second run should make 4
    # (chunks 6-9). Plus the initial output-dim probe (1 call against the
    # first abstract from chunk 0)... actually if first_existing chunk file
    # exists, the runner uses it for dim detection — no probe call.
    assert skip_check.calls == 4, (
        f"expected 4 model_fn calls (chunks 6-9); got {skip_check.calls}"
    )
    expected = _deterministic_embed(abstracts)
    assert np.array_equal(result, expected)


# ---------- test 6: partial / corrupt chunk file recovery ----------


def test_runner_partial_chunk_file_recovery(tmp_path: Path) -> None:
    """Corrupt chunk_5.npy after a clean run; restart re-embeds chunk 5."""
    abstracts = [f"abs {i}" for i in range(1000)]
    out_dir = tmp_path / "out"

    # Clean run
    runner1 = ChunkedEmbedRunner(
        model_fn=_deterministic_embed,
        chunk_size=100,
        output_dir=out_dir,
    )
    runner1.run(abstracts)

    # Corrupt chunk_5.npy by truncating it
    chunk5 = out_dir / "chunk_000005.npy"
    chunk5.write_bytes(b"")  # empty file — np.load will raise

    # Re-run: should detect chunk 5 is invalid + re-embed
    skip_check = _KillAfterCalls(kill_after=999)
    runner2 = ChunkedEmbedRunner(
        model_fn=skip_check.wrap(_deterministic_embed),
        chunk_size=100,
        output_dir=out_dir,
    )
    result = runner2.run(abstracts)

    # Only chunk 5 should be re-embedded (1 call)
    assert skip_check.calls == 1, (
        f"expected 1 model_fn call (chunk 5 re-embed); got {skip_check.calls}"
    )
    expected = _deterministic_embed(abstracts)
    assert np.array_equal(result, expected)


# ---------- bonus: empty input + bad chunk_size ----------


def test_runner_rejects_empty_abstracts(tmp_path: Path) -> None:
    runner = ChunkedEmbedRunner(
        model_fn=_deterministic_embed,
        chunk_size=10,
        output_dir=tmp_path / "out",
    )
    with pytest.raises(ValueError, match="no abstracts"):
        runner.run([])


def test_runner_rejects_bad_chunk_size(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="chunk_size"):
        ChunkedEmbedRunner(
            model_fn=_deterministic_embed,
            chunk_size=0,
            output_dir=tmp_path / "out",
        )


def test_runner_handles_uneven_last_chunk(tmp_path: Path) -> None:
    """1050 abstracts × chunk_size=100 = 10 full chunks + 1 partial (50)."""
    abstracts = [f"abs {i}" for i in range(1050)]
    runner = ChunkedEmbedRunner(
        model_fn=_deterministic_embed,
        chunk_size=100,
        output_dir=tmp_path / "out",
    )
    result = runner.run(abstracts)

    assert result.shape == (1050, _OUTPUT_DIM)
    expected = _deterministic_embed(abstracts)
    assert np.array_equal(result, expected)
    # Last chunk has 50 vectors
    last_chunk = np.load(tmp_path / "out" / "chunk_000010.npy")
    assert last_chunk.shape == (50, _OUTPUT_DIM)


# ---------- run_mapped: parallel Modal .map() dispatch (Phase 2.1 WS4) ----------
#
# Qwen3 bs=1 at 1M is ~10 hrs sequential; run_mapped fans chunks out across
# Modal containers via `fn.map` (an ordered map: result i ↔ input chunk i)
# while preserving the SAME resumable chunk-to-disk contract as run().


class _CountingMap:
    """Wraps a per-chunk embed into an ordered batch map_fn, counting chunks.

    Mirrors Modal's ``fn.map`` contract: takes an ordered list of chunks
    (each a ``list[str]``) and returns an ordered list of per-chunk arrays.
    ``self.n_chunks_embedded`` records how many chunks were dispatched —
    used to assert that a resume only re-dispatches the missing chunks.
    """

    def __init__(self, per_chunk: Any = _deterministic_embed) -> None:
        self.per_chunk = per_chunk
        self.n_chunks_embedded = 0
        self.batch_calls = 0

    def __call__(
        self, chunks: list[list[str]],
    ) -> list[np.ndarray[Any, Any]]:
        self.batch_calls += 1
        out: list[np.ndarray[Any, Any]] = []
        for chunk in chunks:
            self.n_chunks_embedded += 1
            out.append(self.per_chunk(chunk))
        return out


def test_run_mapped_clean(tmp_path: Path) -> None:
    """1000 abstracts × chunk_size=100 = 10 chunks dispatched via map_fn.

    Result must byte-match the sequential embed (ordering preserved) and
    write the same chunk files + done.txt the sequential path would.
    """
    abstracts = [f"abs {i}" for i in range(1000)]
    runner = ChunkedEmbedRunner(
        model_fn=_deterministic_embed,  # unused by run_mapped
        chunk_size=100,
        output_dir=tmp_path / "out",
    )
    mp = _CountingMap()
    result = runner.run_mapped(abstracts, map_fn=mp)

    assert result.shape == (1000, _OUTPUT_DIM)
    expected = _deterministic_embed(abstracts)
    assert np.array_equal(result, expected)
    assert mp.n_chunks_embedded == 10
    for cid in range(10):
        assert (tmp_path / "out" / f"chunk_{cid:06d}.npy").exists()
    done = sorted(
        int(line.strip())
        for line in (tmp_path / "out" / "done.txt").read_text().splitlines()
        if line.strip()
    )
    assert done == list(range(10))


def test_run_mapped_uneven_last_chunk(tmp_path: Path) -> None:
    """1050 abstracts × chunk_size=100 = 10 full + 1 partial (50) via map."""
    abstracts = [f"abs {i}" for i in range(1050)]
    runner = ChunkedEmbedRunner(
        model_fn=_deterministic_embed,
        chunk_size=100,
        output_dir=tmp_path / "out",
    )
    result = runner.run_mapped(abstracts, map_fn=_CountingMap())

    assert result.shape == (1050, _OUTPUT_DIM)
    assert np.array_equal(result, _deterministic_embed(abstracts))
    last_chunk = np.load(tmp_path / "out" / "chunk_000010.npy")
    assert last_chunk.shape == (50, _OUTPUT_DIM)


def test_run_mapped_resume_only_missing(tmp_path: Path) -> None:
    """A second run_mapped skips valid done chunks; re-dispatches none."""
    abstracts = [f"abs {i}" for i in range(1000)]
    out_dir = tmp_path / "out"
    runner = ChunkedEmbedRunner(
        model_fn=_deterministic_embed, chunk_size=100, output_dir=out_dir,
    )
    runner.run_mapped(abstracts, map_fn=_CountingMap())

    # Re-run: everything is done + valid → map_fn dispatched 0 chunks.
    mp2 = _CountingMap()
    result = runner.run_mapped(abstracts, map_fn=mp2)
    assert mp2.n_chunks_embedded == 0
    assert mp2.batch_calls == 0  # empty todo → map_fn not called at all
    assert np.array_equal(result, _deterministic_embed(abstracts))


def test_run_mapped_resumes_from_partial_run(tmp_path: Path) -> None:
    """Sequential run() dies mid-way; run_mapped resumes the remainder.

    Interop: run_mapped shares the done.txt / chunk-file contract with
    run(), so a preempted sequential run can be finished by a parallel one.
    """
    abstracts = [f"abs {i}" for i in range(1000)]
    out_dir = tmp_path / "out"

    kill = _KillAfterCalls(kill_after=8)  # probe(1) + chunks 0-6 → dies on 7
    runner1 = ChunkedEmbedRunner(
        model_fn=kill.wrap(_deterministic_embed),
        chunk_size=100, output_dir=out_dir,
    )
    with pytest.raises(_SimulatedPreemption):
        runner1.run(abstracts)
    for cid in range(7):
        assert (out_dir / f"chunk_{cid:06d}.npy").exists()

    # Parallel resume: only chunks 7-9 remain.
    mp = _CountingMap()
    runner2 = ChunkedEmbedRunner(
        model_fn=_deterministic_embed, chunk_size=100, output_dir=out_dir,
    )
    result = runner2.run_mapped(abstracts, map_fn=mp)
    assert mp.n_chunks_embedded == 3
    assert np.array_equal(result, _deterministic_embed(abstracts))


def test_run_mapped_corrupt_chunk_recovery(tmp_path: Path) -> None:
    """Corrupt one chunk after a clean map run; re-run re-dispatches only it."""
    abstracts = [f"abs {i}" for i in range(1000)]
    out_dir = tmp_path / "out"
    runner = ChunkedEmbedRunner(
        model_fn=_deterministic_embed, chunk_size=100, output_dir=out_dir,
    )
    runner.run_mapped(abstracts, map_fn=_CountingMap())

    (out_dir / "chunk_000005.npy").write_bytes(b"")  # truncate → np.load fails

    mp2 = _CountingMap()
    result = runner.run_mapped(abstracts, map_fn=mp2)
    assert mp2.n_chunks_embedded == 1  # only chunk 5 re-dispatched
    assert np.array_equal(result, _deterministic_embed(abstracts))


def test_run_mapped_rejects_empty(tmp_path: Path) -> None:
    runner = ChunkedEmbedRunner(
        model_fn=_deterministic_embed, chunk_size=10, output_dir=tmp_path / "out",
    )
    with pytest.raises(ValueError, match="no abstracts"):
        runner.run_mapped([], map_fn=_CountingMap())


def test_run_mapped_tolerates_failed_chunks_and_resumes(tmp_path: Path) -> None:
    """A map_fn that returns exceptions for some chunks (Modal
    return_exceptions=True) saves the good ones and raises a resume-needed
    error; a second pass whose map_fn succeeds completes the run.

    This is the production-hardening: on the base-1M Qwen3 embed a single
    transient chunk failure must NOT discard the concurrently-completed later
    chunks — the good ones are persisted and only the failed one is re-run.
    """
    abstracts = [f"abs {i}" for i in range(500)]  # 5 chunks
    out_dir = tmp_path / "out"
    runner = ChunkedEmbedRunner(
        model_fn=_deterministic_embed, chunk_size=100, output_dir=out_dir,
    )

    def flaky_map(chunks: list[list[str]]) -> list[Any]:
        # First dispatch: chunk index 2 "fails" (returns an exception object),
        # mirroring Modal .map(return_exceptions=True).
        out: list[Any] = [_deterministic_embed(c) for c in chunks]
        out[2] = RuntimeError("simulated transient preemption")
        return out

    with pytest.raises(RuntimeError, match="incomplete"):
        runner.run_mapped(abstracts, map_fn=flaky_map)

    # The 4 good chunks were persisted; the failed one was not.
    done = sorted(
        int(line.strip())
        for line in (out_dir / "done.txt").read_text().splitlines()
        if line.strip()
    )
    assert done == [0, 1, 3, 4]  # chunk 2 left undone

    # Resume with a clean map_fn → only the missing chunk is re-dispatched.
    mp2 = _CountingMap()
    result = runner.run_mapped(abstracts, map_fn=mp2)
    assert mp2.n_chunks_embedded == 1
    assert np.array_equal(result, _deterministic_embed(abstracts))


def test_run_mapped_shape_mismatch_raises(tmp_path: Path) -> None:
    """A map_fn returning the wrong row count for a chunk is a hard error."""
    abstracts = [f"abs {i}" for i in range(300)]
    runner = ChunkedEmbedRunner(
        model_fn=_deterministic_embed, chunk_size=100, output_dir=tmp_path / "out",
    )

    def bad_map(chunks: list[list[str]]) -> list[np.ndarray[Any, Any]]:
        # Drop a row from the first chunk's output → shape mismatch.
        out = [_deterministic_embed(c) for c in chunks]
        out[0] = out[0][:-1]
        return out

    with pytest.raises(ValueError, match="rows for chunk"):
        runner.run_mapped(abstracts, map_fn=bad_map)
