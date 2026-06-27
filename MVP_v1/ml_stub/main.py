"""ML service stub for offline development.

This stub implements the same contract as the real ML service:

  GET /health            -> {"status": "ok"}
  GET /ml/stream         -> MJPEG stream (multipart/x-mixed-replace)
  GET /ml/latest         -> JSON of the latest annotated frame

In the real service, each frame is processed by InsightFace (face
detection + 512-dim embedding extraction + bbox drawing). Here we
return synthetic data:
  - The MJPEG stream is a series of grey frames with a moving square
    to simulate a detected face.
  - The embedding for each "face" is a deterministic 512-dim vector
    derived from the current time (so consecutive frames look similar
    enough that averaging during registration produces a stable
    identity).

Run:
    uvicorn ml_stub.main:app --port 8001 --reload
"""

from __future__ import annotations

import asyncio
import io
import math
import time
from datetime import UTC, datetime

import numpy as np
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from PIL import Image, ImageDraw

app = FastAPI(title="FaceGuard ML Stub", version="0.1.0")

FRAME_W = 640
FRAME_H = 480
EMB_DIM = 512


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _synthetic_embedding(seed: int) -> np.ndarray:
    """Deterministic normalized embedding derived from `seed`.

    Consecutive calls within ~1s of each other produce nearby vectors
    so the recognition loop has a chance to converge on a stable identity.
    """
    rng = np.random.default_rng(seed)
    v = rng.standard_normal(EMB_DIM).astype(np.float32)
    v = v / np.linalg.norm(v)
    return v


def _current_bbox(t: float) -> tuple[int, int, int, int]:
    """A square that orbits around the frame center — simulates a face."""
    cx = FRAME_W // 2 + int(120 * math.cos(t * 0.7))
    cy = FRAME_H // 2 + int(60 * math.sin(t * 0.5))
    size = 140
    return (cx - size // 2, cy - size // 2, cx + size // 2, cy + size // 2)


def _render_frame(t: float) -> bytes:
    """Render a single JPEG with a simulated face rectangle."""
    img = Image.new("RGB", (FRAME_W, FRAME_H), color=(40, 40, 40))
    draw = ImageDraw.Draw(img)
    bbox = _current_bbox(t)
    draw.rectangle(bbox, outline=(220, 220, 80), width=3)
    draw.text((bbox[0], bbox[1] - 20), "face (stub)", fill=(220, 220, 80))
    draw.text(
        (10, 10),
        f"FaceGuard ML Stub  t={t:.1f}",
        fill=(180, 180, 180),
    )

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=80)
    return buf.getvalue()


def _frame_payload(t: float) -> dict:
    bbox = _current_bbox(t)
    # Quantize the time to 1s so the embedding stays stable within a
    # registration burst (5 frames @ 400ms < 2.5s).
    seed = int(t)
    emb = _synthetic_embedding(seed)
    return {
        "timestamp": _now_iso(),
        "faces": [
            {
                "bbox": list(bbox),
                "embedding": emb.tolist(),
                "confidence": 0.95,
            }
        ],
    }


@app.get("/health")
async def health():
    return {"status": "ok", "service": "ml-stub"}


@app.get("/ml/latest")
async def ml_latest():
    return _frame_payload(time.time())


@app.get("/ml/stream")
async def ml_stream():
    """MJPEG stream — multipart/x-mixed-replace, boundary=frame."""

    boundary = b"--frame\r\n"

    async def generate():
        while True:
            t = time.time()
            jpg = _render_frame(t)
            headers = (
                b"Content-Type: image/jpeg\r\n"
                b"Content-Length: " + str(len(jpg)).encode() + b"\r\n\r\n"
            )
            yield boundary + headers + jpg + b"\r\n"
            # 10 fps
            await asyncio.sleep(0.1)

    return StreamingResponse(
        generate(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("ml_stub.main:app", host="0.0.0.0", port=8001, reload=True)
