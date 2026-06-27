"""Real ML service for FaceGuardV2.

Replaces ml_stub. Runs on Raspberry Pi or laptop.
Uses InsightFace (buffalo_l) for detection + 512-dim embeddings.
"""

from __future__ import annotations

import asyncio
import io
import threading
import time
from contextlib import asynccontextmanager
from datetime import UTC, datetime

import cv2

# --- InsightFace ---
import numpy as np
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from insightface.app import FaceAnalysis
from PIL import Image, ImageDraw

# --- Globals ---
face_app = None
_frame_lock = threading.Lock()
latest_frame = None
latest_result = {"timestamp": "", "faces": []}


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def init_model():
    """Load InsightFace model once at startup."""
    global face_app
    face_app = FaceAnalysis(name="buffalo_l", root="./models")
    face_app.prepare(ctx_id=0, det_size=(640, 480))
    print("InsightFace model loaded")


def process_frame(frame: np.ndarray) -> tuple[bytes, dict]:
    """Detect faces, draw boxes, return JPEG + metadata."""
    global face_app

    # InsightFace detection
    faces = face_app.get(frame)

    # Draw on frame
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)

    face_data = []
    for face in faces:
        bbox = face.bbox.astype(int)
        # Draw rectangle
        draw.rectangle([bbox[0], bbox[1], bbox[2], bbox[3]], outline=(0, 255, 0), width=2)
        draw.text((bbox[0], bbox[1] - 10), f"{face.det_score:.2f}", fill=(0, 255, 0))

        # Collect metadata
        face_data.append(
            {
                "bbox": [int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])],
                "embedding": face.embedding.tolist(),  # 512-dim, already L2-normalized
                "confidence": float(face.det_score),
            }
        )

    # Encode to JPEG
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    jpeg_bytes = buf.getvalue()

    result = {"timestamp": _now_iso(), "faces": face_data}

    return jpeg_bytes, result


def capture_loop():
    """Background thread: captures from camera, processes frames."""
    global latest_frame, latest_result

    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)

    cap.set(cv2.CAP_PROP_FPS, 15)

    if not cap.isOpened():
        raise RuntimeError("Cannot open camera")

    print("Camera opened")

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            print("Frame read failed")
            continue

        if frame.shape[0] < 100 or frame.shape[1] < 100:
            print("Corrupted frame detected:", frame.shape)
            continue

        jpeg, result = process_frame(frame)

        with _frame_lock:
            latest_frame = jpeg
            latest_result = result

        time.sleep(0.066)


# --- FastAPI endpoints ---


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_model()
    thread = threading.Thread(target=capture_loop, daemon=True)
    thread.start()
    yield


app = FastAPI(title="FaceGuard ML Service", version="1.0.0", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "ml-service"}


@app.get("/ml/latest")
async def ml_latest():
    with _frame_lock:
        return latest_result


@app.get("/ml/stream")
async def ml_stream():
    """MJPEG stream."""
    boundary = b"--frame\r\n"

    async def generate():
        while True:
            if latest_frame is not None:
                headers = (
                    b"Content-Type: image/jpeg\r\n"
                    b"Content-Length: " + str(len(latest_frame)).encode() + b"\r\n\r\n"
                )
                yield boundary + headers + latest_frame + b"\r\n"
            await asyncio.sleep(0.066)  # ~15 fps

    return StreamingResponse(
        generate(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8001)
