"""Optimized ML service for FaceGuard — relaxed passive liveness."""

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
import onnxruntime as ort 
import numpy as np
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from insightface.app import FaceAnalysis

# --- Globals ---
face_app = None

pfld_session = None
pfld_input_name = None
pfld_output_name = None

_frame_lock = threading.Lock()
latest_frame: bytes | None = None
latest_result = {"timestamp": "", "faces": []}

# --- FPS Globals ---
_fps_lock = threading.Lock()
_fps_capture = 0
_fps_stream = 0
_fps_inference = 0

# --- Passive Liveness Config ---
EAR_THRESHOLD = 0.18          
CONSECUTIVE_CLOSED = 1        
MIN_OPEN_BEFORE = 2           
MIN_OPEN_AFTER = 2            
REQUIRED_BLINKS = 2           
BLINK_WINDOW = 5.0            
LIVENESS_TTL_SECONDS = 3.0    
MAX_EAR_HISTORY = 150
FACE_MESH_EVERY_N = 1
_face_mesh_counter = 0        

# Face stability relaxed
MAX_FACE_JITTER = 25         
STABLE_FRAMES_REQUIRED = 3    

ear_history: deque[tuple[float, float]] = deque(maxlen=MAX_EAR_HISTORY)
liveness_valid_until = 0.0
_last_bbox: tuple[float, float, float, float] | None = None
_stable_frame_count = 0

LEFT_EYE_IDX = [36, 37, 38, 39, 40, 41]
RIGHT_EYE_IDX = [42, 43, 44, 45, 46, 47]

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


def _bbox_center(bbox):
    return ((bbox[0] + bbox[2]) / 2.0, (bbox[1] + bbox[3]) / 2.0)


def _bbox_jitter(bbox1, bbox2):
    c1 = _bbox_center(bbox1)
    c2 = _bbox_center(bbox2)
    return abs(c1[0] - c2[0]) + abs(c1[1] - c2[1])


def init_model():
    global face_app, pfld_session, pfld_input_name, pfld_output_name

    face_app = FaceAnalysis(name="buffalo_sc", root="./models")
    face_app.prepare(ctx_id=-1, det_size=(160, 160))

    # --- PFLD ONNX ---
    model_path = "./models/pfld.onnx"
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"PFLD model not found: {model_path}. "
            f"Скачай вручную: https://github.com/cunjian/pytorch_face_landmark"
        )

    pfld_session = ort.InferenceSession(
        model_path, providers=["CPUExecutionProvider"]
    )
    pfld_input_name = pfld_session.get_inputs()[0].name
    pfld_output_name = pfld_session.get_outputs()[0].name


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


def _count_valid_blinks(history: deque[tuple[float, float]], now: float) -> int:
    recent = [(t, e) for t, e in history if now - t <= BLINK_WINDOW]
    if len(recent) < 6:
        return 0

    blinks = 0
    i = 0
    while i < len(recent):
        # Phase 1: eyes open
        open_start = i
        while i < len(recent) and recent[i][1] >= EAR_THRESHOLD:
            i += 1
        open_len = i - open_start
        if open_len < MIN_OPEN_BEFORE:
            i += 1
            continue

        # Phase 2: eyes closed (1+ frames)
        closed_start = i
        while i < len(recent) and recent[i][1] < EAR_THRESHOLD:
            i += 1
        closed_len = i - closed_start
        if closed_len < CONSECUTIVE_CLOSED or closed_len > 15:
            continue

        # Phase 3: eyes open again
        if i >= len(recent):
            break
        reopen_start = i
        while i < len(recent) and recent[i][1] >= EAR_THRESHOLD:
            i += 1
        reopen_len = i - reopen_start
        if reopen_len < MIN_OPEN_AFTER:
            continue

        blinks += 1

    return blinks

def _preprocess_pfld(crop: np.ndarray) -> np.ndarray:
    img = cv2.resize(crop, (112, 112))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32) / 255.0
    img = (img - 0.5) / 0.5              
    img = np.transpose(img, (2, 0, 1))
    return np.expand_dims(img, axis=0) 


def _get_pfld_landmarks(frame: np.ndarray, bbox: np.ndarray) -> np.ndarray | None:
    if pfld_session is None:
        return None

    x1, y1, x2, y2 = bbox.astype(int)
    h, w = frame.shape[:2]

    margin = int(max(x2 - x1, y2 - y1) * 0.2)
    x1, y1 = max(0, x1 - margin), max(0, y1 - margin)
    x2, y2 = min(w, x2 + margin), min(h, y2 + margin)

    crop = frame[y1:y2, x1:x2]
    if crop.size == 0:
        return None

    input_blob = _preprocess_pfld(crop)
    outputs = pfld_session.run([pfld_output_name], {pfld_input_name: input_blob})
    landmarks = outputs[0].reshape(-1, 2) 

    crop_h, crop_w = crop.shape[:2]
    landmarks[:, 0] = landmarks[:, 0] / 112.0 * crop_w + x1
    landmarks[:, 1] = landmarks[:, 1] / 112.0 * crop_h + y1

    return landmarks

def run_inference(frame: np.ndarray) -> dict:
    global liveness_valid_until, cached_faces, cached_landmarks, cached_status
    global _last_bbox, _stable_frame_count
    global _face_mesh_counter 

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
        _last_bbox = None
        _stable_frame_count = 0
        return {"timestamp": _now_iso(), "faces": [], "status": "NO_FACE"}

    primary = faces[0]
    bbox = primary.bbox.astype(int)
    bbox_tuple = tuple(primary.bbox.tolist())

    # Check face stability
    face_stable = False
    if _last_bbox is not None:
        jitter = _bbox_jitter(_last_bbox, bbox_tuple)
        if jitter < MAX_FACE_JITTER:
            _stable_frame_count += 1
            if _stable_frame_count >= STABLE_FRAMES_REQUIRED:
                face_stable = True
        else:
            _stable_frame_count = max(0, _stable_frame_count - 2)
    _last_bbox = bbox_tuple


    is_live = current_time < liveness_valid_until
    landmarks = None
    ear_avg = 0.0
    blink_count = 0
    status_extra = ""

    need_landmarks = face_stable and not is_live

    if need_landmarks:
        _face_mesh_counter += 1
        if _face_mesh_counter >= FACE_MESH_EVERY_N:
            _face_mesh_counter = 0
            landmarks = _get_pfld_landmarks(frame, primary.bbox)

            if landmarks is not None:
                ear_left = _calculate_ear(landmarks, LEFT_EYE_IDX)
                ear_right = _calculate_ear(landmarks, RIGHT_EYE_IDX)
                ear_avg = (ear_left + ear_right) / 2.0
                ear_history.append((current_time, ear_avg))

                while ear_history and current_time - ear_history[0][0] > 6.0:
                    ear_history.popleft()

                blink_count = _count_valid_blinks(ear_history, current_time)
                status_extra = f" B:{blink_count} S:{_stable_frame_count}"

                if blink_count >= REQUIRED_BLINKS:
                    liveness_valid_until = current_time + LIVENESS_TTL_SECONDS
                    is_live = True
    else:
        _face_mesh_counter = 0
        if not face_stable and not is_live:
            status_extra = f" S:{_stable_frame_count}"

    status_text = "ACCESS GRANTED" if is_live else "LOCKED"
    color = (0, 255, 0) if is_live else (0, 0, 255)

    if not face_stable and not is_live:
        status_text = "STABILIZE" + status_extra
        color = (0, 165, 255)
    elif not is_live:
        status_text = "LOCKED" + status_extra

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
    display = frame.copy()
    h, w, _ = display.shape

    with _inference_lock:
        faces = cached_faces
        landmarks = cached_landmarks
        status_text, color = cached_status

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

    if faces:
        primary = faces[0]
        bbox = primary.bbox.astype(int)
        cv2.rectangle(display, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
        cv2.putText(
            display, status_text,
            (bbox[0], max(bbox[1] - 10, y + 10)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1,
        )
        if landmarks is not None:
            ear_left = _calculate_ear(landmarks, LEFT_EYE_IDX)
            ear_right = _calculate_ear(landmarks, RIGHT_EYE_IDX)
            ear_avg = (ear_left + ear_right) / 2.0
            if ear_avg > 0:
                cv2.putText(
                    display, f"EAR:{ear_avg:.2f}",
                    (bbox[0], bbox[1] + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1,
                )
            for idx in LEFT_EYE_IDX + RIGHT_EYE_IDX:
                x, y = int(landmarks[idx][0]), int(landmarks[idx][1])
                cv2.circle(display, (x, y), 1, (0, 255, 255), -1)

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

        display = draw_frame(frame)
        small = cv2.resize(display, (STREAM_W, STREAM_H))
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


app = FastAPI(title="FaceGuard ML Service", version="2.8.0", lifespan=lifespan)


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