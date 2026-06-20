"""In-memory shared state for the recognition loop and the UI.

The recognition loop (see `recognition.py`) continuously polls the ML
service and runs `FaceDatabase.recognize(...)`. The verdict is written
into a single `SystemState` object. The web UI reads from the same
object (for the dashboard snapshot) and from the SSE channel (for live
updates without polling).

This is intentionally not a database — it's the volatile "what is the
system doing right now" cache. The audit trail lives in SQLite via
`FaceDatabase.add_log(...)`.
"""

from __future__ import annotations

import asyncio
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

from .database import AccessType


Verdict = Literal["granted", "denied", "scanning", "idle", "error"]


@dataclass
class CurrentVerdict:
    """The latest recognition decision, plus UI hints.

    `verdict` is one of:
      * `granted`   — face matched, access granted, servo fired.
      * `denied`    — face seen but no match above threshold.
      * `scanning`  — ML service returned a face, comparison in flight.
      * `idle`      — no face detected in the latest frame.
      * `error`     — ML service unreachable or comparison crashed.
    """

    verdict: Verdict = "idle"
    name: str = ""
    score: float = 0.0
    access_type: AccessType = "unknown"
    matched_user_id: int | None = None
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "verdict": self.verdict,
            "name": self.name,
            "score": round(self.score, 4),
            "access_type": self.access_type,
            "matched_user_id": self.matched_user_id,
            "timestamp": datetime.fromtimestamp(
                self.timestamp, tz=timezone.utc
            ).isoformat(),
            "is_door_open": self.verdict == "granted",
        }


class SystemState:
    """Thread-safe single-writer / multi-reader state.

    The recognition loop calls `update()` from a background asyncio task
    or thread. The web layer reads via `snapshot()` (one-shot) or
    subscribes via `subscribe()` (asyncio Queue, drained by the SSE
    endpoint).
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._verdict = CurrentVerdict()
        self._subscribers: list[asyncio.Queue] = []
        self._ml_healthy: bool = False
        self._last_ml_check: float = 0.0

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------

    def snapshot(self) -> dict:
        with self._lock:
            return {
                **self._verdict.to_dict(),
                "ml_healthy": self._ml_healthy,
                "last_ml_check": self._last_ml_check,
            }

    async def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=64)
        loop = asyncio.get_running_loop()

        def _add():
            with self._lock:
                self._subscribers.append(q)

        await loop.run_in_executor(None, _add)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        with self._lock:
            if q in self._subscribers:
                self._subscribers.remove(q)

    # ------------------------------------------------------------------
    # Writes
    # ------------------------------------------------------------------

    def update(self, verdict: CurrentVerdict) -> None:
        with self._lock:
            self._verdict = verdict
            subs = list(self._subscribers)

        # Push to every subscriber queue. Drop oldest if full so a slow
        # SSE client can't block the recognition loop.
        for q in subs:
            try:
                q.put_nowait(verdict.to_dict())
            except asyncio.QueueFull:
                try:
                    q.get_nowait()
                except asyncio.QueueEmpty:
                    pass
                try:
                    q.put_nowait(verdict.to_dict())
                except asyncio.QueueFull:
                    pass  # give up on this client for this update

    def set_ml_health(self, healthy: bool) -> None:
        with self._lock:
            self._ml_healthy = healthy
            self._last_ml_check = time.time()


# Module-level singleton. The FastAPI app owns exactly one of these and
# injects it into handlers via Depends.
state = SystemState()
