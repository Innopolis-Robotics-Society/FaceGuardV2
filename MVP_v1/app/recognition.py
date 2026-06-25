"""Background recognition loop.

Every `RECOGNITION_INTERVAL_MS`:
  1. Poll ML service for the latest annotated frame.
  2. If no face -> set verdict to "idle".
  3. If face -> take the biggest, run `db.recognize(embedding, threshold)`.
     * match   -> verdict "granted", trigger servo, update last-seen.
     * no match -> verdict "denied".
  4. Periodically (every 30s) health-check the ML service so the UI can
     surface "ML offline" warnings.

Runs as an asyncio task launched from `main.py` lifespan.
"""

from __future__ import annotations

import asyncio
import logging
import time

import numpy as np

from .database import FaceDatabase
from .ml_client import MLClient
from .servo import Servo
from .state import CurrentVerdict, SystemState

log = logging.getLogger(__name__)


class RecognitionLoop:
    def __init__(
        self,
        db: FaceDatabase,
        ml: MLClient,
        servo: Servo,
        state: SystemState,
        *,
        threshold: float,
        interval_ms: int,
    ):
        self._db = db
        self._ml = ml
        self._servo = servo
        self._state = state
        self._threshold = threshold
        self._interval = interval_ms / 1000.0
        self._task: asyncio.Task | None = None
        self._stop = asyncio.Event()
        self._last_health_check: float = 0.0

    async def start(self) -> None:
        if self._task is None or self._task.done():
            self._stop.clear()
            self._task = asyncio.create_task(self._run(), name="recognition-loop")

    async def stop(self) -> None:
        self._stop.set()
        if self._task and not self._task.done():
            try:
                await asyncio.wait_for(self._task, timeout=5.0)
            except TimeoutError:
                self._task.cancel()

    async def _run(self) -> None:
        log.info("Recognition loop started (interval=%.3fs)", self._interval)
        while not self._stop.is_set():
            try:
                await self._tick()
            except Exception:  # pragma: no cover — defensive
                log.exception("Recognition tick crashed")
                self._state.update(
                    CurrentVerdict(verdict="error", name="Recognition loop crashed")
                )
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=self._interval)
            except TimeoutError:
                pass
        log.info("Recognition loop stopped")

    async def _tick(self) -> None:
        # Throttled ML health check.
        now = time.time()
        if now - self._last_health_check > 30.0:
            healthy = await self._ml.health()
            self._state.set_ml_health(healthy)
            self._last_health_check = now
            if not healthy:
                self._state.update(
                    CurrentVerdict(verdict="error", name="ML service unreachable")
                )
                return

        latest = await self._ml.get_latest()
        if latest is None:
            self._state.update(CurrentVerdict(verdict="error", name="ML returned no frame"))
            return

        if not latest.faces:
            self._state.update(CurrentVerdict(verdict="idle"))
            return

        # Pick the biggest face (same rule as MVP v0).
        face = max(
            latest.faces,
            key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]),
        )

        # Offload the (possibly blocking, GIL-released by numpy) DB call
        # to a thread so the asyncio loop stays responsive.
        result = await asyncio.to_thread(
            self._db.recognize,
            np.asarray(face.embedding, dtype=np.float32),
            self._threshold,
        )

        if result.access_type == "unknown":
            self._state.update(
                CurrentVerdict(
                    verdict="denied",
                    name=result.name,
                    score=result.score,
                    access_type="unknown",
                    timestamp=time.time(),
                )
            )
            log.info(
                "Denied: best_score=%.3f threshold=%.3f",
                result.score, self._threshold,
            )
            return

        # Granted.
        self._state.update(
            CurrentVerdict(
                verdict="granted",
                name=result.name,
                score=result.score,
                access_type=result.access_type,
                matched_user_id=result.matched_user_id,
                timestamp=time.time(),
            )
        )
        log.info(
            "Granted: name=%s type=%s score=%.3f",
            result.name, result.access_type, result.score,
        )
        # Trigger the servo in a thread — even GpioServo's open() returns
        # quickly, but we don't want any chance of blocking the loop.
        await asyncio.to_thread(self._servo.open)


def register_one(
    db: FaceDatabase,
    ml: MLClient,
    *,
    name: str,
    is_guest: bool,
    guest_days: int | None = None,
    frame_count: int = 5,
    frame_interval_ms: int = 400,
) -> tuple[str, list[float]]:
    """Capture N frames from the ML service, average their embeddings,
    save the result as a user or guest.

    Returns `(status_message, embedding_preview)` where embedding_preview
    is the first 8 components of the averaged embedding — useful for
    confirming in the UI that we actually captured something.

    Blocks for frame_count * frame_interval_ms. Caller should run it
    inside `asyncio.to_thread(...)` from an async context.
    """
    embeddings: list[np.ndarray] = []
    interval = frame_interval_ms / 1000.0

    # Synchronous loop — runs in a worker thread, see MLClient.start().
    import httpx
    with httpx.Client(base_url=ml._base_url, timeout=ml._timeout) as client:
        for i in range(frame_count):
            try:
                r = client.get("/ml/latest")
                r.raise_for_status()
                payload = r.json()
            except (httpx.HTTPError, ValueError) as e:
                raise RuntimeError(f"ML service error on frame {i + 1}: {e}") from e

            faces = payload.get("faces", [])
            if not faces:
                raise RuntimeError(f"No face detected on frame {i + 1}/{frame_count}")

            face = max(
                faces,
                key=lambda f: (
                    (f["bbox"][2] - f["bbox"][0])
                    * (f["bbox"][3] - f["bbox"][1])
                ),
            )
            embeddings.append(np.asarray(face["embedding"], dtype=np.float32))
            if i < frame_count - 1:
                time.sleep(interval)

    # Average + L2-normalize, exactly like MVP v0's create_average_embedding.
    avg = np.mean(embeddings, axis=0)
    norm = float(np.linalg.norm(avg))
    if norm > 0:
        avg = avg / norm

    if is_guest:
        if not guest_days or guest_days <= 0:
            raise ValueError("guest_days must be a positive integer")
        db.register_guest_for_days(name, avg, guest_days)
        msg = f"Guest '{name}' registered — expires in {guest_days} day(s)."
    else:
        db.register_user(name, avg)
        msg = f"User '{name}' registered."

    return msg, avg[:8].tolist()
