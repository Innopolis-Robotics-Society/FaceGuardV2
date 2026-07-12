"""Optimized ML service for FaceGuard — draw on original, then resize."""

from __future__ import annotations

import os
os.environ["OMP_NUM_THREADS"] = "2"
os.environ["OPENBLAS_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"
os.environ["VECLIB_MAXIMUM_THREADS"] = "2"
os.environ["NUMEXPR_NUM_THREADS"] = "2"
os.environ["ONNXRUNTIME_CPU_NUM_THREADS"] = "2"

import asyncio
import queue
import threading
import time
from collections import deque
from contextlib import asynccontextmanager
from datetime import UTC, datetime

import cv2
import mediapipe as mp
import numpy as np
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from insightface.app import FaceAnalysis

# --- Globals ---
face_app = None
mp_face_mesh = None

_frame_lock = threading.Lock()
latest_frame: bytes | None = None
latest_result = {"timestamp": "", "faces": []}

# --- FPS Globals ---
_fps_lock = threading.Lock()
_fps_capture = 0
_fps_stream = 0
_fps_inference = 0

# --- Passive Liveness ---
EAR_THRESHOLD = 0.22
CONSECUTIVE_FRAMES = 2
LIVENESS_TTL_SECONDS = 3.0
MAX_EAR_HISTORY = 45

ear_history: deque[tuple[float, float]] = deque(maxlen=MAX_EAR_HISTORY)
liveness_valid_until = 0.0

RIGHT_EYE_IDX = [362, 385, 387, 263, 373, 380]
LEFT_EYE_IDX = [33, 160, 158, 133, 153, 144]

# --- Cached inference ---
_inference_lock = threading.Lock()
cached_faces = []
cached_landmarks = None
cached_status = ("NO FACE", (128, 128, 128))

# --- Queues ---
capture_queue = queue.Queue(maxsize=1)
display_queue = queue.Queue(maxsize=2)

# --- Stream output size ---
STREAM_W, STREAM_H = 240, 180
STREAM_QUALITY = 40


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _update_fps(window: list[float], now: float) -> int:
    window.append(now)
    cutoff = now - 1.0
    while window and window[0] < cutoff:
        window.pop(0)
    return len(window)


def init_model():
    global face_app, mp_face_mesh

    face_app = FaceAnalysis(name="buffalo_sc", root="./models")
    face_app.prepare(ctx_id=-1, det_size=(320, 320))

    mp_face_mesh_module = mp.solutions.face_mesh
    mp_face_mesh = mp_face_mesh_module.FaceMesh(
        max_num_faces=1,
        refine_landmarks=False,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.7,
    )


def _calculate_ear(landmarks: np.ndarray, eye_idx: list[int]) -> float:
    if landmarks is None or len(landmarks) < max(eye_idx) + 1:
        return 0.0
    pts = landmarks[eye_idx]
    v1 = np.linalg.norm(pts[1] - pts[5])
    v2 = np.linalg.norm(pts[2] - pts[4])
    h = np.linalg.norm(pts[0] - pts[3])
    if h < 1e-6:
        return 0.0
    return float((v1 + v2) / (2.0 * h))


def _detect_blink(history: deque[tuple[float, float]]) -> bool:
    if len(history) < 6:
        return False
    state = "open"
    closed_count = 0
    for _, ear in history:
        if state == "open":
            if ear < EAR_THRESHOLD:
                state = "closing"
                closed_count = 1
        elif state == "closing":
            if ear < EAR_THRESHOLD:
                closed_count += 1
                if closed_count >= CONSECUTIVE_FRAMES:
                    state = "closed"
            else:
                state = "open"
                closed_count = 0
        elif state == "closed":
            if ear >= EAR_THRESHOLD:
                return True
    return False


def run_inference(frame: np.ndarray) -> dict:
    global liveness_valid_until, cached_faces, cached_landmarks, cached_status

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h_img, w_img, _ = frame.shape
    current_time = time.time()

    faces = face_app.get(frame, max_num=1)

    if not faces:
        with _inference_lock:
            cached_faces = []
            cached_landmarks = None
            cached_status = ("NO FACE", (128, 128, 128))
        liveness_valid_until = 0.0
        ear_history.clear()
        return {"timestamp": _now_iso(), "faces": [], "status": "NO_FACE"}

    primary = faces[0]
    bbox = primary.bbox.astype(int)

    mp_results = mp_face_mesh.process(rgb_frame)
    landmarks = None
    if mp_results.multi_face_landmarks:
        landmarks = np.array(
            [[lm.x * w_img, lm.y * h_img] for lm in mp_results.multi_face_landmarks[0].landmark]
        )

    ear_avg = 0.0
    is_live = current_time < liveness_valid_until

    if landmarks is not None:
        ear_left = _calculate_ear(landmarks, LEFT_EYE_IDX)
        ear_right = _calculate_ear(landmarks, RIGHT_EYE_IDX)
        ear_avg = (ear_left + ear_right) / 2.0
        ear_history.append((current_time, ear_avg))
        if _detect_blink(ear_history):
            liveness_valid_until = current_time + LIVENESS_TTL_SECONDS
            is_live = True
        is_live = current_time < liveness_valid_until

    status_text = "ACCESS GRANTED" if is_live else "LOCKED"
    color = (0, 255, 0) if is_live else (0, 0, 255)

    embedding = primary.embedding.tolist() if primary.embedding is not None else []
    face_data = [
        {
            "bbox": [int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])],
            "embedding": embedding,
            "confidence": float(primary.det_score),
            "ear": round(ear_avg, 4),
            "liveness_passed": is_live,
            "is_primary": True,
        }
    ]

    with _inference_lock:
        cached_faces = faces
        cached_landmarks = landmarks
        cached_status = (status_text, color)

    return {"timestamp": _now_iso(), "faces": face_data, "status": status_text}


def draw_frame(frame: np.ndarray) -> np.ndarray:
    """Рисует оверлей на ОРИГИНАЛЬНОМ кадре. Bbox совпадает идеально."""
    display = frame.copy()
    h, w, _ = display.shape

    with _inference_lock:
        faces = cached_faces
        landmarks = cached_landmarks
        status_text, color = cached_status

    # --- FPS overlay по центру ---
    with _fps_lock:
        cap_fps = _fps_capture
        str_fps = _fps_stream
        inf_fps = _fps_inference

    line = f"CAP:{cap_fps}  INF:{inf_fps}  STR:{str_fps}"
    font = cv2.FONT_HERSHEY_SIMPLEX
    fscale = 0.5
    thick = 1
    (tw, th), _ = cv2.getTextSize(line, font, fscale, thick)
    x = max((w - tw) // 2, 0)
    y = th + 6
    cv2.rectangle(display, (x - 4, 0), (x + tw + 4, y + 4), (0, 0, 0), -1)
    cv2.putText(display, line, (x, y), font, fscale, (0, 255, 0), thick)

    # --- Face box & status (оригинальные координаты — никакого scale!) ---
    if faces:
        primary = faces[0]
        bbox = primary.bbox.astype(int)
        cv2.rectangle(display, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
        cv2.putText(
            display, status_text,
            (bbox[0], max(bbox[1] - 10, y + 10)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2,
        )
        if landmarks is not None:
            ear_left = _calculate_ear(landmarks, LEFT_EYE_IDX)
            ear_right = _calculate_ear(landmarks, RIGHT_EYE_IDX)
            ear_avg = (ear_left + ear_right) / 2.0
            cv2.putText(
                display, f"EAR:{ear_avg:.2f}",
                (bbox[0], bbox[1] + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1,
            )

    return display


def capture_thread():
    global _fps_capture
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    cap.set(cv2.CAP_PROP_FPS, 30)

    if not cap.isOpened():
        raise RuntimeError("Cannot open camera")

    fps_window: list[float] = []
    first = True

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            time.sleep(0.001)
            continue
        if frame.shape[0] < 100 or frame.shape[1] < 100:
            continue

        if first:
            print(f"[CAP] Real camera resolution: {frame.shape[1]}x{frame.shape[0]}", flush=True)
            first = False

        now = time.time()
        with _fps_lock:
            _fps_capture = _update_fps(fps_window, now)

        try:
            capture_queue.put_nowait(frame)
        except queue.Full:
            try:
                capture_queue.get_nowait()
            except queue.Empty:
                pass
            try:
                capture_queue.put_nowait(frame)
            except queue.Full:
                pass

        try:
            display_queue.put_nowait(frame)
        except queue.Full:
            try:
                display_queue.get_nowait()
            except queue.Empty:
                pass
            try:
                display_queue.put_nowait(frame)
            except queue.Full:
                pass


def inference_thread():
    global latest_result, _fps_inference
    fps_window: list[float] = []

    while True:
        frame = capture_queue.get()
        now = time.time()

        try:
            result = run_inference(frame)
        except Exception as e:
            print(f"[INFERENCE ERROR] {e}", flush=True)
            result = {"timestamp": _now_iso(), "faces": [], "status": "ERROR"}

        with _fps_lock:
            _fps_inference = _update_fps(fps_window, now)
        with _frame_lock:
            latest_result = result


def stream_thread():
    global latest_frame, _fps_stream
    fps_window: list[float] = []

    while True:
        frame = display_queue.get()
        now = time.time()

        # Рисуем на оригинале — bbox точно по лицу
        display = draw_frame(frame)
        # Потом уменьшаем ВСЁ изображение пропорционально
        small = cv2.resize(display, (STREAM_W, STREAM_H))
        # Кодируем
        ret, buf = cv2.imencode(".jpg", small, [int(cv2.IMWRITE_JPEG_QUALITY), STREAM_QUALITY])
        jpeg = buf.tobytes() if ret else None

        with _fps_lock:
            _fps_stream = _update_fps(fps_window, now)

        if jpeg is not None:
            with _frame_lock:
                latest_frame = jpeg


# --- FastAPI ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_model()
    threading.Thread(target=capture_thread, daemon=True, name="capture").start()
    threading.Thread(target=inference_thread, daemon=True, name="inference").start()
    threading.Thread(target=stream_thread, daemon=True, name="stream").start()
    yield
    if mp_face_mesh:
        mp_face_mesh.close()


app = FastAPI(title="FaceGuard ML Service", version="2.5.3", lifespan=lifespan)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "ml-service"}


@app.get("/ml/latest")
async def ml_latest():
    with _frame_lock:
        return latest_result.copy() if latest_result else {"timestamp": _now_iso(), "faces": []}


@app.get("/ml/stream")
async def ml_stream():
    boundary = b"--frame\r\n"

    async def generate():
        while True:
            with _frame_lock:
                frame_data = latest_frame
            if frame_data:
                headers = (
                    b"Content-Type: image/jpeg\r\n"
                    b"Content-Length: " + str(len(frame_data)).encode() + b"\r\n\r\n"
                )
                yield boundary + headers + frame_data + b"\r\n"
            await asyncio.sleep(0.033)

    return StreamingResponse(
        generate(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001)