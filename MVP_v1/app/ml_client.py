"""HTTP client for the ML service.

The ML service is owned by another team member. It owns the camera and
exposes two endpoints:

  GET /ml/stream
      MJPEG stream of annotated frames (bounding boxes drawn on top).
      The backend proxies this to the browser at `/stream`.

  GET /ml/latest
      JSON describing the latest processed frame:
        {
          "timestamp": "2026-06-12T14:32:11Z",
          "faces": [
            {
              "bbox": [x1, y1, x2, y2],
              "embedding": [512 floats],
              "confidence": 0.98
            }
          ]
        }

A `ml_stub/` service ships with this repo so the backend can be
developed and tested end-to-end without the real ML stack. See
`ml_stub/main.py` for the contract reference implementation.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx
import numpy as np

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class DetectedFace:
    bbox: tuple[int, int, int, int]
    embedding: np.ndarray  # float32, (512,)
    confidence: float


@dataclass(frozen=True)
class LatestFrame:
    timestamp: str
    faces: list[DetectedFace]


class MLClient:
    """Thin async client around the ML service.

    Uses a single reusable `httpx.AsyncClient` with a generous timeout —
    the ML service can be slow on the Raspberry Pi 4 (single-frame
    detection latency is typically 200–500ms on `buffalo_s`).
    """

    def __init__(self, base_url: str, timeout: float = 5.0):
        self._base_url = base_url.rstrip("/")
        self._client: httpx.AsyncClient | None = None
        self._timeout = timeout

    async def __aenter__(self) -> MLClient:
        await self.start()
        return self

    async def __aexit__(self, *exc) -> None:
        await self.close()

    async def start(self) -> None:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout,
            )

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def health(self) -> bool:
        """Lightweight liveness probe."""
        await self.start()
        assert self._client is not None
        try:
            r = await self._client.get("/health")
            return r.status_code == 200
        except httpx.HTTPError as e:
            log.warning("ML health check failed: %s", e)
            return False

    async def get_latest(self) -> LatestFrame | None:
        """Fetch the latest annotated frame metadata.

        Returns None if the ML service is unreachable or returned no
        recent frame (e.g. camera still warming up).
        """
        await self.start()
        assert self._client is not None
        try:
            r = await self._client.get("/ml/latest")
        except httpx.HTTPError as e:
            log.warning("ML /ml/latest failed: %s", e)
            return None
        if r.status_code != 200:
            log.warning("ML /ml/latest returned %s", r.status_code)
            return None

        try:
            payload = r.json()
        except ValueError:
            log.warning("ML /ml/latest returned non-JSON body")
            return None

        faces: list[DetectedFace] = []
        for f in payload.get("faces", []):
            try:
                bbox = tuple(int(v) for v in f["bbox"])
                embedding = np.asarray(f["embedding"], dtype=np.float32)
                confidence = float(f.get("confidence", 0.0))
                faces.append(DetectedFace(bbox, embedding, confidence))
            except (KeyError, TypeError, ValueError) as e:
                log.warning("Skipping malformed face entry: %s", e)
                continue

        return LatestFrame(timestamp=payload.get("timestamp", ""), faces=faces)

    async def stream_mjpeg(self):
        """Async generator yielding MJPEG chunks from the ML service.

        Used by the backend to proxy the camera stream to browsers.
        Yields raw bytes — the caller is expected to write them to an
        HTTP response with the appropriate multipart/x-mixed-replace
        content-type.
        """
        await self.start()
        assert self._client is not None
        async with self._client.stream("GET", "/ml/stream") as r:
            r.raise_for_status()
            async for chunk in r.aiter_bytes():
                yield chunk
