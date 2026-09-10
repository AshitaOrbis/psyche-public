"""Cap-burn handler for Claude CLI rate-limit incidents.

The Claude Max plan enforces a rolling 5-hour usage cap. When ``claude -p``
hits that cap (or a 429 rate-limit equivalent), it returns rc=1 immediately
with a cap-style stderr marker. The earlier judge driver did NOT distinguish
this case from an ordinary rc=1 — it just logged "ERROR: claude -p failed"
and moved on. With a worker pool of N and a 5h cap, that meant entire cap
windows could be burned through in fast succession on rc=1 spins, requiring a
``--missing-only`` re-run and doubling the cap-window cost. Observed three
times during v0.1 J3 (116 burned in the targeted block; 265 burned in the
full block; later fills cleaner).

This module defines the recovery state machine. The CapBurnHandler is
threadsafe and shared across all workers in a phase; it:

1. Wraps each call (`call_with_backoff`) with exponential-backoff retry
   on ``ClaudeCapError`` (60s → 300s → 900s → 1800s → 3600s, max 5 attempts).
2. Logs every cap event to ``runs/<tag>/cap_events.jsonl`` (separate from
   ``validation_warnings.jsonl`` — caps are not validation failures).
3. When inline retries are exhausted, sets a pool-wide ``cap_aborted`` flag
   and writes a resume checkpoint to ``runs/<tag>/checkpoint_<phase>.json``.
4. Other workers check ``is_cap_aborted()`` before each call; once tripped,
   they exit immediately so the pool drains without burning more cap-window
   calls on rc=1 spins.

Resume-safety is provided upstream by the score/pairwise dedup logic that
keys on ``(run_id, judge_model)`` for scoring and on ``canonical_key`` for
pairwise. A re-run reads the existing JSONL outputs and skips records
already present.
"""

from __future__ import annotations

import json
import threading
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable

from psycheeval import config


# Backoff schedule in seconds. After the 5th failure (covering ~3.5 minutes
# to ~1 hour of waiting), declare the cap exhausted and stop the run cleanly
# rather than spinning further. Tunable via constructor.
DEFAULT_BACKOFF_SCHEDULE: tuple[int, ...] = (60, 300, 900, 1800, 3600)


@dataclass
class CapEvent:
    """One cap-burn incident logged by the handler."""

    timestamp: str
    judge_model: str
    record_key: str
    stderr_preview: str
    returncode: int
    backoff_attempt: int  # 0 = first attempt; 1 = first retry; etc.


class CapBurnHandler:
    """Per-phase state machine for cap-burn handling.

    One handler instance per phase per run. Shared across worker threads.
    Methods are threadsafe; the handler's state machine is small enough that
    a single mutex suffices.
    """

    def __init__(
        self,
        run_tag: str,
        phase: str,
        *,
        backoff_schedule: tuple[int, ...] = DEFAULT_BACKOFF_SCHEDULE,
        sleep_fn: Callable[[float], None] = time.sleep,
        clock_fn: Callable[[], str] | None = None,
    ) -> None:
        self.run_tag = run_tag
        self.phase = phase
        self.backoff_schedule = backoff_schedule
        self._sleep = sleep_fn
        self._clock = clock_fn or (lambda: datetime.now(UTC).isoformat())
        self._lock = threading.Lock()
        self._cap_aborted = threading.Event()
        self._events: list[CapEvent] = []
        # Counters for the checkpoint
        self.completed_count = 0
        self.last_successful_record_id: str | None = None
        self.last_cap_hit_record_id: str | None = None

    @property
    def cap_events_path(self) -> Path:
        return config.run_dir(self.run_tag) / "cap_events.jsonl"

    @property
    def checkpoint_path(self) -> Path:
        return config.run_dir(self.run_tag) / f"checkpoint_{self.phase}.json"

    def is_cap_aborted(self) -> bool:
        """True iff cap-burn was hit and inline retries are exhausted.
        Workers should check this BEFORE each call; if true, return immediately
        so the pool drains without further cap-window draws."""
        return self._cap_aborted.is_set()

    def record_success(self, record_id: str) -> None:
        with self._lock:
            self.completed_count += 1
            self.last_successful_record_id = record_id

    def record_cap_event(
        self,
        *,
        judge_model: str,
        record_key: str,
        stderr: str,
        returncode: int,
        backoff_attempt: int,
    ) -> None:
        ev = CapEvent(
            timestamp=self._clock(),
            judge_model=judge_model,
            record_key=record_key,
            stderr_preview=(stderr or "")[:500],
            returncode=returncode,
            backoff_attempt=backoff_attempt,
        )
        with self._lock:
            self._events.append(ev)
            self.last_cap_hit_record_id = record_key
        # Persist to JSONL outside the lock to keep the critical section short.
        self.cap_events_path.parent.mkdir(parents=True, exist_ok=True)
        with self.cap_events_path.open("a") as fh:
            fh.write(
                json.dumps(
                    {
                        "timestamp": ev.timestamp,
                        "judge_model": ev.judge_model,
                        "record_key": ev.record_key,
                        "stderr_preview": ev.stderr_preview,
                        "returncode": ev.returncode,
                        "backoff_attempt": ev.backoff_attempt,
                    }
                )
                + "\n"
            )

    def declare_exhausted(self) -> None:
        """Mark the phase as cap-aborted. Idempotent."""
        self._cap_aborted.set()

    @property
    def cap_event_count(self) -> int:
        with self._lock:
            return len(self._events)

    def call_with_backoff(
        self,
        fn: Callable[[], object],
        *,
        record_key: str,
        judge_model: str,
    ) -> object:
        """Call ``fn()``; on ClaudeCapError, sleep with backoff and retry.

        Up to ``len(backoff_schedule)`` retries (default 5). Each retry logs
        a cap event. If retries are exhausted, declares the phase exhausted
        (so peer workers stop) and re-raises the last ClaudeCapError.

        Non-cap exceptions propagate immediately on the first occurrence.
        """
        # Imported lazily so the test fixture can mock the module without
        # pulling in a real subprocess client.
        from psycheeval.llm import ClaudeCapError

        max_attempts = len(self.backoff_schedule)
        last_err: ClaudeCapError | None = None

        for attempt in range(max_attempts + 1):
            if self._cap_aborted.is_set():
                # A peer worker already declared exhaustion. Bail before any
                # further call. If we have a last error, surface it; otherwise
                # synthesize one to keep the type contract consistent.
                if last_err is not None:
                    raise last_err
                raise ClaudeCapError(
                    f"cap aborted by peer worker before {record_key}",
                    stderr="",
                    returncode=1,
                )
            try:
                return fn()
            except ClaudeCapError as e:
                last_err = e
                self.record_cap_event(
                    judge_model=judge_model,
                    record_key=record_key,
                    stderr=e.stderr,
                    returncode=e.returncode,
                    backoff_attempt=attempt,
                )
                if attempt >= max_attempts:
                    break
                sleep_s = self.backoff_schedule[attempt]
                self._sleep(sleep_s)
                # Re-check after wake — peer might have declared exhaustion
                # while we slept.
                continue

        # Exhausted: declare and raise the last error.
        self.declare_exhausted()
        if last_err is not None:
            raise last_err
        raise ClaudeCapError(
            f"cap exhausted on {record_key} (no last error stored)",
            stderr="",
            returncode=1,
        )

    def write_checkpoint(
        self,
        *,
        pending_count: int,
        suggested_resume_command: str,
    ) -> Path:
        """Write a JSON checkpoint for the current phase. Always overwrites
        (not append) — the latest state is what matters for resume.

        Suggested call sites: end of phase (always, even on success), and
        after the cap-aborted exit so the user has a clear resume command.
        """
        with self._lock:
            payload = {
                "tag": self.run_tag,
                "phase": self.phase,
                "completed_count": self.completed_count,
                "pending_count": pending_count,
                "last_successful_record_id": self.last_successful_record_id,
                "last_cap_hit_record_id": self.last_cap_hit_record_id,
                "cap_aborted": self._cap_aborted.is_set(),
                "cap_event_count": len(self._events),
                "timestamp": self._clock(),
                "suggested_resume_command": suggested_resume_command,
            }
        self.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        self.checkpoint_path.write_text(json.dumps(payload, indent=2))
        return self.checkpoint_path
