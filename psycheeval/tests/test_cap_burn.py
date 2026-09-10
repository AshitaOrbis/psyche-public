"""Tests for CapBurnHandler and the rate-limit-detection helper.

The cap-burn handler exists because Claude Max's rolling 5-hour cap returns
rc=1 immediately when hit; without explicit detection + backoff, a worker
pool keeps submitting calls and burns the entire next cap window in seconds.
These tests prove the protective behavior:

1. ``_is_claude_cap_burn`` recognizes cap-style stderr substrings.
2. ``ClaudeCapError`` is raised distinctly from ``ClaudeCLIError``.
3. ``CapBurnHandler.call_with_backoff`` sleeps with the configured schedule
   on cap, succeeds when the underlying call eventually succeeds, and
   declares exhaustion after the schedule is consumed.
4. Cap events are written to ``cap_events.jsonl`` (NOT validation_warnings).
5. Once ``is_cap_aborted()`` is true, peer workers see it and bail without
   making further calls.
6. The checkpoint JSON has the documented shape (tag, phase, completed
   count, pending count, last successful record id, last cap-hit record id,
   cap_aborted, timestamp, suggested resume command).
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from psycheeval.cap_burn import (
    DEFAULT_BACKOFF_SCHEDULE,
    CapBurnHandler,
)
from psycheeval.llm import ClaudeCapError, ClaudeCLIError, _is_claude_cap_burn


# --------------------------------------------------------------------------
#  Cap-marker recognition
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "stderr",
    [
        "You've hit your usage limit. Try again at 9:00 AM.",
        "Error: rate-limited",
        "anthropic api error: 429 too many requests",
        "Quota exhausted on this account",
        "rolling 5-hour cap reached",
    ],
)
def test_cap_markers_recognized(stderr):
    assert _is_claude_cap_burn(stderr, returncode=1)


@pytest.mark.parametrize(
    "stderr",
    [
        "JSON decode error",
        "model not found",
        "connection refused",
    ],
)
def test_non_cap_errors_not_recognized(stderr):
    """Non-cap rc=1 with non-empty stderr should NOT be treated as cap.
    These are real errors that should propagate, not back off."""
    assert not _is_claude_cap_burn(stderr, returncode=1)


def test_empty_stderr_rc_nonzero_treated_as_cap():
    """Empirical v0.2 Phase 3 observation: claude -p in cap state returns
    rc=1 with EMPTY stderr (and empty stdout). Without this fallback, the
    worker pool burns through hundreds of rc=1 calls in seconds. Accepting
    the false-positive cost (slow backoff on real empty-output errors)
    because the false-negative cost is catastrophic for Opus quota."""
    assert _is_claude_cap_burn("", returncode=1, stdout="")
    assert _is_claude_cap_burn("   \n  ", returncode=1, stdout="\t")  # whitespace only


def test_cap_marker_in_stdout_recognized():
    """Some claude CLI versions print cap notices to stdout instead of stderr."""
    assert _is_claude_cap_burn(stderr="", returncode=1, stdout="You've hit your usage limit. Try again at 9:00 AM.")
    assert _is_claude_cap_burn(stderr="other text", returncode=1, stdout="rate limit reached")


# --------------------------------------------------------------------------
#  Burst-rate detector
# --------------------------------------------------------------------------


def test_burst_detector_threshold():
    """Burst detector should report True only on the Nth failure within
    the window (N = _BURST_THRESHOLD = 3). The 2026-05-13 v0.2 Phase 3
    incident burned ~800 records because content-based heuristics missed
    the cap; burst-rate is the safety net regardless of content."""
    from psycheeval.llm import _record_claude_failure, _reset_claude_burst_state, _BURST_THRESHOLD

    _reset_claude_burst_state()
    # Below threshold = not a burst
    for _ in range(_BURST_THRESHOLD - 1):
        assert _record_claude_failure() is False
    # The Nth call crosses the threshold
    assert _record_claude_failure() is True
    # Subsequent failures stay in burst state (until the window expires)
    assert _record_claude_failure() is True


def test_burst_detector_window_expiry(monkeypatch):
    """Failures older than _BURST_WINDOW_SEC should be ignored so the
    detector doesn't get stuck in burst state forever."""
    from psycheeval import llm as llm_mod
    from psycheeval.llm import _record_claude_failure, _reset_claude_burst_state, _BURST_WINDOW_SEC

    _reset_claude_burst_state()

    # Build up burst state at t=0
    t = [0.0]

    def fake_time():
        return t[0]

    monkeypatch.setattr(llm_mod.time, "time", fake_time)

    assert _record_claude_failure() is False  # 1 failure
    assert _record_claude_failure() is False  # 2 failures
    assert _record_claude_failure() is True  # 3 failures -> burst

    # Jump past the window
    t[0] = _BURST_WINDOW_SEC + 1
    # One more failure — old ones are now outside the window so this is the only one in scope
    assert _record_claude_failure() is False  # window reset


def test_burst_detector_thread_safe():
    """Concurrent record_failure calls from multiple workers must produce
    consistent results — the cap detector is shared across threads in the
    worker pool."""
    import threading
    from psycheeval.llm import _record_claude_failure, _reset_claude_burst_state

    _reset_claude_burst_state()

    results: list[bool] = []
    lock = threading.Lock()

    def worker():
        r = _record_claude_failure()
        with lock:
            results.append(r)

    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # At least 8 of the 10 calls should report burst=True (first 2 are below threshold)
    assert sum(results) >= 8, f"expected at least 8 burst-detections, got {sum(results)}: {results}"


def test_rc_zero_never_a_cap():
    # Even with cap-marker text in stderr (unusual but possible), rc=0 means
    # the call succeeded; we shouldn't flag it as a cap.
    assert not _is_claude_cap_burn("You've hit your usage limit", returncode=0)


# --------------------------------------------------------------------------
#  CapBurnHandler.call_with_backoff
# --------------------------------------------------------------------------


def _make_handler(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *, schedule=(1, 2)) -> CapBurnHandler:
    """Build a handler that writes under tmp_path and uses a fast no-op sleep
    so tests run instantly. ``schedule`` is short by default (1s, 2s) so
    'exhaustion' fires after 2 retries (3 total attempts)."""
    # Redirect run_dir() to point inside tmp_path.
    from psycheeval import config

    monkeypatch.setattr(config, "RUNS_DIR", tmp_path / "runs")
    sleep_calls: list[float] = []

    def fake_sleep(s: float) -> None:
        sleep_calls.append(s)

    h = CapBurnHandler(
        run_tag="capburn-test",
        phase="score_legacy",
        backoff_schedule=schedule,
        sleep_fn=fake_sleep,
        clock_fn=lambda: "2026-05-05T00:00:00+00:00",
    )
    h._sleep_calls = sleep_calls  # type: ignore[attr-defined]
    return h


def test_success_first_try_no_sleep(tmp_path, monkeypatch):
    h = _make_handler(tmp_path, monkeypatch)
    fn = MagicMock(return_value="ok")
    result = h.call_with_backoff(fn, record_key="r1", judge_model="opus")
    assert result == "ok"
    assert fn.call_count == 1
    assert h._sleep_calls == []  # type: ignore[attr-defined]
    assert not h.is_cap_aborted()
    assert h.cap_event_count == 0


def test_one_cap_then_success_sleeps_once(tmp_path, monkeypatch):
    h = _make_handler(tmp_path, monkeypatch, schedule=(1, 2, 3))
    err = ClaudeCapError("hit cap", stderr="usage limit reached", returncode=1)
    fn = MagicMock(side_effect=[err, "ok"])
    result = h.call_with_backoff(fn, record_key="r2", judge_model="opus")
    assert result == "ok"
    assert fn.call_count == 2
    assert h._sleep_calls == [1]  # only the first backoff entry was used  # type: ignore[attr-defined]
    assert not h.is_cap_aborted()
    assert h.cap_event_count == 1


def test_repeated_caps_exhausts_and_aborts(tmp_path, monkeypatch):
    schedule = (1, 2, 3)
    h = _make_handler(tmp_path, monkeypatch, schedule=schedule)
    err = ClaudeCapError("hit cap", stderr="rate limit", returncode=1)
    fn = MagicMock(side_effect=[err, err, err, err])  # 4 caps; schedule has 3 sleeps
    with pytest.raises(ClaudeCapError):
        h.call_with_backoff(fn, record_key="r3", judge_model="opus")
    # 4 attempts (initial + 3 retries); 3 sleeps consumed.
    assert fn.call_count == 4
    assert h._sleep_calls == list(schedule)  # type: ignore[attr-defined]
    assert h.is_cap_aborted()
    assert h.cap_event_count == 4


def test_non_cap_error_propagates_immediately(tmp_path, monkeypatch):
    h = _make_handler(tmp_path, monkeypatch)
    fn = MagicMock(side_effect=ClaudeCLIError("model not found"))
    with pytest.raises(ClaudeCLIError):
        h.call_with_backoff(fn, record_key="r4", judge_model="opus")
    assert fn.call_count == 1
    assert h._sleep_calls == []  # type: ignore[attr-defined]
    assert not h.is_cap_aborted()
    assert h.cap_event_count == 0


# --------------------------------------------------------------------------
#  Peer-worker abort propagation
# --------------------------------------------------------------------------


def test_peer_abort_short_circuits_other_workers(tmp_path, monkeypatch):
    """Once one worker exhausts retries and declares the phase aborted, peer
    workers should bail BEFORE making any further `claude -p` invocation —
    this is the key protective behavior against burning entire cap windows."""
    h = _make_handler(tmp_path, monkeypatch, schedule=(1,))
    err = ClaudeCapError("hit cap", stderr="usage limit", returncode=1)

    worker_a_calls = []
    worker_b_calls = []

    def worker_a():
        # Will fail twice (initial + 1 retry), exhaust schedule, declare cap.
        fn = MagicMock(side_effect=[err, err])
        try:
            h.call_with_backoff(fn, record_key="A", judge_model="opus")
        except ClaudeCapError:
            pass
        worker_a_calls.append(fn.call_count)

    def worker_b():
        # Will only run after worker_a has aborted. Since cap is set,
        # call_with_backoff should raise without invoking fn at all.
        fn = MagicMock(return_value="should-never-run")
        try:
            h.call_with_backoff(fn, record_key="B", judge_model="opus")
        except ClaudeCapError:
            pass
        worker_b_calls.append(fn.call_count)

    # Run sequentially to make ordering deterministic in the test.
    worker_a()
    assert h.is_cap_aborted()
    worker_b()

    assert worker_a_calls == [2]  # initial + 1 retry
    assert worker_b_calls == [0]  # bailed before making a call


# --------------------------------------------------------------------------
#  Persistence: cap events + checkpoint
# --------------------------------------------------------------------------


def test_cap_events_written_to_separate_jsonl(tmp_path, monkeypatch):
    h = _make_handler(tmp_path, monkeypatch, schedule=(1, 2))
    err = ClaudeCapError("hit cap", stderr="usage limit reached", returncode=1)
    fn = MagicMock(side_effect=[err, err, err])
    with pytest.raises(ClaudeCapError):
        h.call_with_backoff(fn, record_key="r5", judge_model="opus")

    assert h.cap_events_path.exists()
    lines = h.cap_events_path.read_text().strip().splitlines()
    assert len(lines) == 3  # one per attempt
    rec = json.loads(lines[0])
    assert rec["judge_model"] == "opus"
    assert rec["record_key"] == "r5"
    assert rec["returncode"] == 1
    assert rec["backoff_attempt"] == 0  # first attempt = 0
    # Validation warnings must be SEPARATE — cap events must not pollute it.
    val_path = h.cap_events_path.parent / "validation_warnings.jsonl"
    assert not val_path.exists()


def test_checkpoint_has_documented_shape(tmp_path, monkeypatch):
    h = _make_handler(tmp_path, monkeypatch, schedule=(1,))
    h.record_success("ok-1")
    h.record_success("ok-2")
    err = ClaudeCapError("hit cap", stderr="usage limit", returncode=1)
    fn = MagicMock(side_effect=[err, err])
    with pytest.raises(ClaudeCapError):
        h.call_with_backoff(fn, record_key="cap-victim", judge_model="opus")

    cp_path = h.write_checkpoint(
        pending_count=42,
        suggested_resume_command="uv run python -m psycheeval.judge score --tag t --resume",
    )
    assert cp_path.exists()
    payload = json.loads(cp_path.read_text())
    # Required fields per the cap-burn hardening contract:
    for key in [
        "tag",
        "phase",
        "completed_count",
        "pending_count",
        "last_successful_record_id",
        "last_cap_hit_record_id",
        "cap_aborted",
        "cap_event_count",
        "timestamp",
        "suggested_resume_command",
    ]:
        assert key in payload, f"checkpoint missing required field: {key}"
    assert payload["tag"] == "capburn-test"
    assert payload["phase"] == "score_legacy"
    assert payload["completed_count"] == 2
    assert payload["pending_count"] == 42
    assert payload["last_successful_record_id"] == "ok-2"
    assert payload["last_cap_hit_record_id"] == "cap-victim"
    assert payload["cap_aborted"] is True
    assert payload["cap_event_count"] == 2
    assert "uv run python -m psycheeval.judge" in payload["suggested_resume_command"]


def test_clean_run_writes_checkpoint_with_cap_aborted_false(tmp_path, monkeypatch):
    """Even on a clean run with no cap events, the checkpoint records the
    final state. cap_aborted=False signals that the phase completed cleanly."""
    h = _make_handler(tmp_path, monkeypatch)
    h.record_success("a")
    h.record_success("b")
    h.record_success("c")
    cp_path = h.write_checkpoint(pending_count=0, suggested_resume_command="(clean)")
    payload = json.loads(cp_path.read_text())
    assert payload["cap_aborted"] is False
    assert payload["completed_count"] == 3
    assert payload["pending_count"] == 0
    assert payload["last_cap_hit_record_id"] is None
    assert payload["cap_event_count"] == 0


def test_default_backoff_schedule_is_what_we_documented():
    """If this changes, update docs/v0_2_plan_extended_2026-05-05.md and the
    BACKLOG cap-burn entry. Five attempts, ranging 60s to 3600s — designed
    to span the typical cap-window wait without futilely spinning."""
    assert DEFAULT_BACKOFF_SCHEDULE == (60, 300, 900, 1800, 3600)
