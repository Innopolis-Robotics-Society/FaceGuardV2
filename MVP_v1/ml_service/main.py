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
import onnxruntime as ort

# --- Globals ---
face_app = None
_frame_lock = threading.Lock()
latest_frame = None
latest_result = {"timestamp": "", "faces": []}
# --- Liveness State ---
EAR_THRESHOLD = 0.20
CONSECUTIVE_FRAMES = 2
LIVENESS_TTL_SECONDS = 3.0  # Время жизни статуса "живой" после моргания

blink_counter = 0
liveness_valid_until = 0.0  # Unix timestamp окончания действия liveness


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def init_model():
    """Load InsightFace model once at startup."""
    global face_app
    face_app = FaceAnalysis(name="buffalo_l", root="./models")
    face_app.prepare(ctx_id=-1, det_size=(640, 640))
    print("InsightFace model loaded")

RIGHT_EYE_IDX = [89, 95, 94, 93, 91, 87]
LEFT_EYE_IDX  = [35, 41, 40, 39, 37, 33]

def _calculate_ear(landmarks: np.ndarray, eye_idx: list[int]) -> float:
    """Eye Aspect Ratio for 6 eye landmarks.

    Expected landmark points (clockwise from the left corner):
        0 -- left corner (inner)
        1, 2 -- upper eyelid
        3 -- right corner (outer)
        4, 5 -- lower eyelid

    EAR = (|p1-p5| + |p2-p4|) / (2 * |p0-p3|)
    """
    if landmarks is None or len(landmarks) < max(eye_idx) + 1:
        return 0.0

    pts = landmarks[eye_idx]
    # vertical distance
    v1 = np.linalg.norm(pts[1] - pts[5])
    v2 = np.linalg.norm(pts[2] - pts[4])
    # horizontal distance
    h = np.linalg.norm(pts[0] - pts[3])
    if h < 1e-6:
        return 0.0
    return float((v1 + v2) / (2.0 * h))

def process_frame(frame: np.ndarray) -> tuple[bytes, dict]:
    global face_app, blink_counter, liveness_valid_until

    faces = face_app.get(frame)
    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)

    # 1. Жесткий сброс состояния, если в кадре нет лиц
    if not faces:
        blink_counter = 0
        liveness_valid_until = 0.0
        
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return buf.getvalue(), {"timestamp": _now_iso(), "faces": []}

    face_data = []
    
    # Сортировка по площади (самое крупное лицо — индекс 0)
    faces = sorted(faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]), reverse=True)

    for i, face in enumerate(faces):
        bbox = face.bbox.astype(int)
        
        ear_left, ear_right, ear_avg = 0.0, 0.0, 0.0
        
        if hasattr(face, 'landmark_2d_106') and face.landmark_2d_106 is not None:
            lm = face.landmark_2d_106
            ear_left = _calculate_ear(lm, LEFT_EYE_IDX)
            ear_right = _calculate_ear(lm, RIGHT_EYE_IDX)
            ear_avg = (ear_left + ear_right) / 2.0

        current_time = time.time()
        is_live = False

        # LIVENESS применяем только к главному лицу перед камерой
        if i == 0:
            if ear_avg < EAR_THRESHOLD:
                # Глаза закрыты
                blink_counter += 1
            else:
                # Глаза открыты. Фиксируем моргание, если до этого они были закрыты достаточно долго
                if blink_counter >= CONSECUTIVE_FRAMES:
                    liveness_valid_until = current_time + LIVENESS_TTL_SECONDS
                blink_counter = 0
            
            # Проверка актуальности статуса
            is_live = current_time < liveness_valid_until
                
            color = (0, 255, 0) if is_live else (255, 0, 0)
            draw.rectangle([bbox[0], bbox[1], bbox[2], bbox[3]], outline=color, width=2)
            
            status_text = f"LIVE" if is_live else f"BLINK TO UNLOCK"
            draw.text((bbox[0], bbox[1] - 25), status_text, fill=color)
        else:
            draw.rectangle([bbox[0], bbox[1], bbox[2], bbox[3]], outline=(128, 128, 128), width=1)

        draw.text((bbox[0], bbox[1] - 10), f"Conf: {face.det_score:.2f} | EAR: {ear_avg:.2f}", fill=(0, 255, 0))

        face_data.append({
            "bbox": [int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])],
            "embedding": face.embedding.tolist(),
            "confidence": float(face.det_score),
            "ear": round(ear_avg, 4),
            "is_primary": i == 0,
            "liveness_passed": is_live
        })

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    
    return buf.getvalue(), {"timestamp": _now_iso(), "faces": face_data}


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
