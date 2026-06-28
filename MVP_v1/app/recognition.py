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
from dataclasses import dataclass, field

import numpy as np

from .config import get_settings
from .database import FaceDatabase
from .ml_client import MLClient
from .servo import Servo
from .state import CurrentVerdict, SystemState

log = logging.getLogger(__name__)

@dataclass
class LivenessState:
    """Current liveness check state."""
    is_active: bool = False
    started_at: float = 0.0
    ear_history: list = field(default_factory=list)  # list of tuples (timestamp, ear)
    last_ear_high: float = 0.0
    blink_detected: bool = False

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
        
        # LIVENESS
        self._settings = get_settings() 
        self._liveness: LivenessState | None = None

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
                self._state.update(CurrentVerdict(verdict="error", name="Recognition loop crashed"))
            
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
                self._state.update(CurrentVerdict(verdict="error", name="ML service unreachable"))
                return

        latest = await self._ml.get_latest()
        if latest is None:
            self._state.update(CurrentVerdict(verdict="error", name="ML returned no frame"))
            return

        if not latest.faces:
            self._liveness = None
            self._state.update(CurrentVerdict(verdict="idle"))
            return

        face = max(latest.faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]))

        # Offload the (possibly blocking, GIL-released by numpy) DB call
        # to a thread so the asyncio loop stays responsive.
        result = await asyncio.to_thread(
            self._db.recognize,
            np.asarray(face.embedding, dtype=np.float32),
            self._threshold,
        )

        if result.access_type == "unknown":
            self._liveness = None
            self._state.update(CurrentVerdict(
                verdict="denied",
                name=result.name,
                score=result.score,
                access_type="unknown",
                liveness_status="disabled" if not self._settings.liveness_enabled else "failed",
            ))
            return
        
        if not self._settings.liveness_enabled:
            self._liveness = None
            await self._grant_access(result, face, liveness_passed=None)
            return

        if self._liveness is None or not self._liveness.is_active:
            self._liveness = LivenessState(
                is_active=True,
                started_at=time.time(),
                last_ear_high=getattr(face, 'ear', 0.0),
            )
            self._state.update(CurrentVerdict(
                verdict="liveness_check",
                name=result.name,
                score=result.score,
                access_type=result.access_type,
                matched_user_id=getattr(result, 'matched_user_id', None),
                liveness_status="checking",
                liveness_ear=getattr(face, 'ear', 0.0),
            ))
            log.info("Liveness check started for %s (ear=%.3f)", result.name, getattr(face, 'ear', 0.0))
            return

        
        liv = self._liveness
        current_ear = getattr(face, 'ear', 0.5) 
        liv.ear_history.append((time.time(), current_ear))

        cutoff = time.time() - self._settings.liveness_timeout_sec
        liv.ear_history = [(t, e) for t, e in liv.ear_history if t >= cutoff]

        threshold = self._settings.liveness_ear_threshold
        if not liv.blink_detected:
            for i in range(1, len(liv.ear_history)):
                t_prev, e_prev = liv.ear_history[i-1]
                t_cur, e_cur = liv.ear_history[i]
                if e_prev >= threshold and e_cur < threshold:
                    liv.last_ear_high = e_prev
                    log.info("Blink dip detected: %.3f → %.3f", e_prev, e_cur)
                elif e_prev < threshold and e_cur >= threshold:
                    liv.blink_detected = True
                    log.info("Blink confirmed: %.3f → %.3f", e_prev, e_cur)
                    break
        
        if liv.blink_detected:
            await self._grant_access(result, face, liveness_passed=True)
            self._liveness = None
            return

        elapsed = time.time() - liv.started_at
        if elapsed > self._settings.liveness_timeout_sec:
            log.warning(
                "Liveness FAILED for %s (ear stable for %.1fs, no blink detected)",
                result.name, elapsed,
            )
            self._state.update(CurrentVerdict(
                verdict="denied",
                name=result.name,
                score=result.score,
                access_type=result.access_type,
                matched_user_id=getattr(result, 'matched_user_id', None),
                liveness_status="failed",
                liveness_ear=current_ear,
            ))

            await asyncio.to_thread(
                self._db.add_log,
                f"Liveness failed: {result.name}",
                result.score,
                result.access_type,
                False,  # success=False
            )
            self._liveness = None
            return
        
        self._state.update(CurrentVerdict(
            verdict="liveness_check",
            name=result.name,
            score=result.score,
            access_type=result.access_type,
            matched_user_id=getattr(result, 'matched_user_id', None),
            liveness_status="checking",
            liveness_ear=current_ear,
        ))

    async def _grant_access(self, result, face, liveness_passed: bool | None):
        """Open the door and log the success"""
        self._state.update(CurrentVerdict(
            verdict="granted",
            name=result.name,
            score=result.score,
            access_type=result.access_type,
            matched_user_id=getattr(result, 'matched_user_id', None),
            liveness_status="passed" if liveness_passed else (
                "disabled" if liveness_passed is None else "failed"
            ),
            liveness_ear=getattr(face, 'ear', 0.0),
        ))
        log.info(
            "Granted: name=%s type=%s score=%.3f liveness=%s",
            result.name, result.access_type, result.score, liveness_passed,
        )
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
        if not guest_days or guest_days <= 0:
            raise ValueError("guest_days must be a positive integer")
        db.register_guest_for_days(name, avg, guest_days)
        msg = f"Guest '{name}' registered — expires in {guest_days} day(s)."
    else:
        db.register_user(name, avg)
        msg = f"User '{name}' registered."

    return msg, avg[:8].tolist()