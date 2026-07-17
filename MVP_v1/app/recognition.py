"""Background recognition loop.

Polls the ML service at a fixed cadence, runs the face-embedding match
against the database, and updates the system state with the verdict.
Access grants trigger the servo (real GPIO on Pi, emulated on x86).

Liveness detection is delegated to the ML service: each frame's face
entry carries an ``liveness_passed`` flag set by the ML side (passive
blink detection). The backend only enforces that the flag is true
before granting access (when ``liveness_enabled`` is set in config).
"""

from __future__ import annotations

from .leds import LEDController
import asyncio
import logging
import time
from datetime import UTC, datetime

import numpy as np

from .config import get_settings
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
        leds: LEDController,
        *,
        threshold: float,
        interval_ms: int,
        log_retention_days: int = 30,
    ):
        self._db = db
        self._ml = ml
        self._servo = servo
        self._state = state
        self._leds = leds
        self._threshold = threshold
        self._interval = interval_ms / 1000.0
        self._task: asyncio.Task | None = None
        self._stop = asyncio.Event()
        self._last_health_check: float = 0.0
        self._last_log_purge: float = time.time()
        self._log_retention_days = log_retention_days
        self._last_logged_verdict: str | None = None
        self._settings = get_settings()

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

        try:
            n = await asyncio.to_thread(self._db.purge_old_logs, self._log_retention_days)
            if n:
                log.info("Purged %d old log entries (>%d days)", n, self._log_retention_days)
        except Exception:
            log.exception("Initial log purge failed")
        self._last_log_purge = time.time()

        while not self._stop.is_set():
            try:
                await self._tick()
            except Exception:
                log.exception("Recognition tick crashed")
                self._state.update(CurrentVerdict(verdict="error", name="Recognition loop crashed"))

            try:
                await asyncio.wait_for(self._stop.wait(), timeout=self._interval)
            except TimeoutError:
                pass
        log.info("Recognition loop stopped")

    async def _tick(self) -> None:
        now = time.time()

        # Periodic ML health probe.
        if now - self._last_health_check > 30.0:
            healthy = await self._ml.health()
            self._state.set_ml_health(healthy)
            self._last_health_check = now
            if not healthy:
                self._log_verdict_change("error", "ML service unreachable")
                self._state.update(CurrentVerdict(verdict="error", name="ML service unreachable"))
                return

        # Daily log rotation.
        if now - self._last_log_purge > 86400.0:
            try:
                n = await asyncio.to_thread(self._db.purge_old_logs, self._log_retention_days)
                if n:
                    log.info("Purged %d old log entries (>%d days)", n, self._log_retention_days)
            except Exception:
                log.exception("Log purge failed")
            self._last_log_purge = now

        latest = await self._ml.get_latest()
        if latest is None:
            self._log_verdict_change("error", "ML returned no frame")
            self._state.update(CurrentVerdict(verdict="error", name="ML returned no frame"))
            return

        if not latest.faces:
            self._log_verdict_change("idle", "")
            self._state.update(CurrentVerdict(verdict="idle"))
            self._leds.all_off()
            return

        # Prefer the face flagged as primary by the ML service; fall back
        # to the largest bounding box if no primary is set.
        primary = next((f for f in latest.faces if f.is_primary), None)
        if primary is None:
            primary = max(
                latest.faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1])
            )

        result = await asyncio.to_thread(
            self._db.recognize,
            np.asarray(primary.embedding, dtype=np.float32),
            self._threshold,
        )

        if result.access_type == "unknown":
            self._log_verdict_change(
                "denied",
                f"best_score={result.score:.3f} threshold={self._threshold:.3f}",
            )
            self._state.update(
                CurrentVerdict(
                    verdict="denied",
                    name=result.name,
                    score=result.score,
                    access_type="unknown",
                    timestamp=time.time(),
                    liveness_status="disabled",
                    liveness_ear=primary.ear,
                )
            )
            self._leds.red_on()
            return

        # Liveness gate. When disabled, grant immediately.
        if not self._settings.liveness_enabled:
            await self._grant_access(result, primary, liveness_passed=None)
            return

        if primary.liveness_passed:
            await self._grant_access(result, primary, liveness_passed=True)
        else:
            # Hold in the liveness_check state until the ML side reports
            # a successful blink.
            self._state.update(
                CurrentVerdict(
                    verdict="liveness_check",
                    name=result.name,
                    score=result.score,
                    access_type=result.access_type,
                    matched_user_id=result.matched_user_id,
                    liveness_status="checking",
                    liveness_ear=primary.ear,
                )
            )
            self._log_verdict_change("liveness_check", f"waiting for blink — {result.name}")
            self._leds.yellow_on()

    async def _grant_access(self, result, face, liveness_passed: bool | None):
        status_msg = (
            "passed" if liveness_passed else ("disabled" if liveness_passed is None else "failed")
        )

        self._log_verdict_change(
            "granted",
            f"name={result.name} type={result.access_type} score={result.score:.3f} liveness={status_msg}",
        )

        self._state.update(
            CurrentVerdict(
                verdict="granted",
                name=result.name,
                score=result.score,
                access_type=result.access_type,
                matched_user_id=result.matched_user_id,
                liveness_status=status_msg,
                liveness_ear=face.ear,
                timestamp=time.time(),
            )
        )

        log.info("Granted: name=%s score=%.3f liveness=%s", result.name, result.score, status_msg)
        await asyncio.to_thread(self._servo.open)
        self._leds.green_on()
        asyncio.get_event_loop().call_later(
            self._settings.led_grant_duration_sec,
            self._leds.all_off,
        )
        await asyncio.to_thread(
            self._db.add_log,
            result.name,
            result.score,
            result.access_type,
            True,
            liveness_passed,
        )

    def _log_verdict_change(self, verdict: str, detail: str) -> None:
        """Emit a Python log line only when the verdict changes."""
        if self._last_logged_verdict == verdict:
            return
        self._last_logged_verdict = verdict
        if verdict == "granted":
            log.info("Granted: %s", detail)
        elif verdict == "denied":
            log.info("Denied: %s", detail)
        elif verdict == "error":
            log.warning("Error: %s", detail)
        elif verdict == "idle":
            log.debug("Idle: %s", detail)
        elif verdict == "liveness_check":
            log.debug("Liveness check: %s", detail)


def register_one(
    db: FaceDatabase,
    ml: MLClient,
    *,
    name: str,
    is_guest: bool,
    expires_at: datetime | None = None,
    frame_count: int = 5,
    frame_interval_ms: int = 400,
) -> tuple[str, list[float]]:
    """Capture N frames from the ML service, average their embeddings,
    and persist the result.

    For ``is_guest=True`` the caller must provide ``expires_at`` (a
    UTC-aware datetime). Returns ``(status_message, embedding_preview)``
    where the preview is the first 8 components of the averaged
    embedding — useful for confirming in the UI that capture worked.

    Blocks for ``frame_count * frame_interval_ms``. The caller should
    run it inside ``asyncio.to_thread(...)`` from an async context.
    """
    embeddings: list[np.ndarray] = []
    interval = frame_interval_ms / 1000.0

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
                key=lambda f: (f["bbox"][2] - f["bbox"][0]) * (f["bbox"][3] - f["bbox"][1]),
            )
            embeddings.append(np.asarray(face["embedding"], dtype=np.float32))
            if i < frame_count - 1:
                time.sleep(interval)

    avg = np.mean(embeddings, axis=0)
    norm = float(np.linalg.norm(avg))
    if norm > 0:
        avg = avg / norm

    if is_guest:
        if expires_at is None:
            raise ValueError("temporary registration requires expires_at")
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        db.register_user(name, avg, type="temporary", expires_at=expires_at)
        local_str = expires_at.astimezone(UTC).isoformat()
        msg = f"Guest '{name}' registered — valid until {local_str}."
    else:
        db.register_user(name, avg)
        msg = f"User '{name}' registered."

    return msg, avg[:8].tolist()
