"""Real ML service for FaceGuard with Active Liveness."""

from __future__ import annotations

import asyncio
import io
import threading
import time
import random
from contextlib import asynccontextmanager
from datetime import UTC, datetime

import cv2
import numpy as np
import mediapipe as mp
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from insightface.app import FaceAnalysis
from PIL import Image, ImageDraw

# --- Globals ---
face_app = None
mp_face_mesh = None

_frame_lock = threading.Lock()
latest_frame = None
latest_result = {"timestamp": "", "faces": []}

# --- Liveness State ---
EAR_THRESHOLD = 0.22 # Немного повысили порог, чтобы исключить шум
CONSECUTIVE_FRAMES = 3 # Требуем 3 кадра подряд закрытых глаз для надежности
LIVENESS_TTL_SECONDS = 2.0 # Время действия "проверки" сократили

blink_counter = 0
liveness_valid_until = 0.0

# Active Challenge State
challenge_active = False
challenge_start_time = 0.0
challenge_duration = 0.0
next_challenge_in = random.uniform(2.0, 5.0)

# --- MediaPipe Landmarks ---
RIGHT_EYE_IDX = [362, 385, 387, 263, 373, 380]
LEFT_EYE_IDX  = [33, 160, 158, 133, 153, 144]

def _now_iso() -> str:
    return datetime.now(UTC).isoformat()

def init_model():
    """Load InsightFace (SC) and MediaPipe models once at startup."""
    global face_app, mp_face_mesh
    
    face_app = FaceAnalysis(name="buffalo_sc", root="./models")
    face_app.prepare(ctx_id=-1, det_size=(640, 640))
    
    mp_face_mesh_module = mp.solutions.face_mesh
    mp_face_mesh = mp_face_mesh_module.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True, # Включаем уточнение для лучшей детекции глаз
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
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

def _check_image_quality(frame: np.ndarray, bbox: list) -> bool:
    """Простая эвристика против экранов: проверяет вариативность яркости внутри лица."""
    x1, y1, x2, y2 = bbox
    face_roi = frame[y1:y2, x1:x2]
    if face_roi.size == 0:
        return True
    
    # Вычисляем стандартное отклонение яркости (контраст)
    gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
    std_dev = np.std(gray)
    
    # Экраны часто дают либо слишком высокий контраст (пиксели), либо слишком низкий (размытие)
    # Эмпирические пороги для камеры 320x240
    if std_dev < 10 or std_dev > 80:
        return False 
    return True

def process_frame(frame: np.ndarray) -> tuple[bytes, dict]:
    global face_app, mp_face_mesh, blink_counter, liveness_valid_until
    global challenge_active, challenge_start_time, challenge_duration, next_challenge_in

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    faces = face_app.get(frame)
    
    img = Image.fromarray(rgb_frame)
    draw = ImageDraw.Draw(img)

    current_time = time.time()
    
    # Логика активного челленджа
    if not challenge_active:
        if current_time > next_challenge_in:
            challenge_active = True
            challenge_start_time = current_time
            challenge_duration = random.uniform(1.5, 3.0) # Окно для выполнения
            blink_counter = 0 # Сбрасываем счетчик, чтобы не засчитывать старые моргания
    else:
        # Если время челленджа вышло, а моргания не было
        if current_time > (challenge_start_time + challenge_duration):
            challenge_active = False
            next_challenge_in = current_time + random.uniform(2.0, 5.0)
            blink_counter = 0

    if not faces:
        blink_counter = 0
        liveness_valid_until = 0.0
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return buf.getvalue(), {"timestamp": _now_iso(), "faces": [], "status": "NO_FACE"}

    faces = sorted(faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]), reverse=True)
    
    h_img, w_img, _ = frame.shape
    mp_results = mp_face_mesh.process(rgb_frame)
    
    main_face_landmarks = None
    if mp_results.multi_face_landmarks:
        main_face_landmarks = np.array([
            [lm.x * w_img, lm.y * h_img] for lm in mp_results.multi_face_landmarks[0].landmark
        ])

    face_data = []
    primary_face = faces[0]
    bbox = primary_face.bbox.astype(int)

    ear_avg = 0.0
    is_live = False
    status_text = "WAITING..."

    # Проверка качества изображения (Anti-Screen)
    quality_ok = _check_image_quality(frame, bbox)

    if main_face_landmarks is not None and quality_ok:
        ear_left = _calculate_ear(main_face_landmarks, LEFT_EYE_IDX)
        ear_right = _calculate_ear(main_face_landmarks, RIGHT_EYE_IDX)
        ear_avg = (ear_left + ear_right) / 2.0

        # Детекция моргания
        if ear_avg < EAR_THRESHOLD:
            blink_counter += 1
        else:
            if blink_counter >= CONSECUTIVE_FRAMES:
                # Моргание засчитано!
                if challenge_active:
                    # Если мы в режиме челленджа, то это успешное прохождение
                    liveness_valid_until = current_time + LIVENESS_TTL_SECONDS
                    challenge_active = False
                    next_challenge_in = current_time + random.uniform(3.0, 6.0)
                    status_text = "VERIFIED!"
                else:
                    # Если челлендж не активен, просто обновляем таймер (для удобства UX)
                    liveness_valid_until = current_time + LIVENESS_TTL_SECONDS
            
            blink_counter = 0

        is_live = current_time < liveness_valid_until
        
        if challenge_active:
            status_text = f"BLINK NOW! ({int(challenge_duration - (current_time - challenge_start_time))}s)"
            color = (0, 165, 255) # Orange
        elif is_live:
            status_text = "ACCESS GRANTED"
            color = (0, 255, 0)
        else:
            status_text = "LOCKED"
            color = (0, 0, 255) # Red
            
    else:
        status_text = "BAD QUALITY / NO LANDMARKS"
        color = (128, 128, 128)

    draw.rectangle([bbox[0], bbox[1], bbox[2], bbox[3]], outline=color, width=3)
    draw.text((bbox[0], bbox[1] - 25), status_text, fill=color)
    draw.text((bbox[0], bbox[1] - 10), f"EAR: {ear_avg:.2f} | Q: {quality_ok}", fill=(255, 255, 255))

    face_data.append({
        "bbox": [int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])],
        "embedding": primary_face.embedding.tolist() if primary_face.embedding is not None else [],
        "confidence": float(primary_face.det_score),
        "ear": round(ear_avg, 4),
        "liveness_passed": is_live,
        "challenge_active": challenge_active
    })

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue(), {"timestamp": _now_iso(), "faces": face_data}

def capture_loop():
    global latest_frame, latest_result
    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    cap.set(cv2.CAP_PROP_FPS, 15)

    if not cap.isOpened():
        raise RuntimeError("Cannot open camera")

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            time.sleep(0.01)
            continue
        if frame.shape[0] < 100 or frame.shape[1] < 100:
            continue

        jpeg, result = process_frame(frame)

        with _frame_lock:
            latest_frame = jpeg
            latest_result = result
        time.sleep(0.066)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_model()
    thread = threading.Thread(target=capture_loop, daemon=True)
    thread.start()
    yield
    if mp_face_mesh:
        mp_face_mesh.close()

app = FastAPI(title="FaceGuard ML Service", version="1.2.0", lifespan=lifespan)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "ml-service"}

@app.get("/ml/latest")
async def ml_latest():
    with _frame_lock:
        return latest_result

@app.get("/ml/stream")
async def ml_stream():
    boundary = b"--frame\r\n"
    async def generate():
        while True:
            if latest_frame is not None:
                headers = (
                    b"Content-Type: image/jpeg\r\n"
                    b"Content-Length: " + str(len(latest_frame)).encode() + b"\r\n\r\n"
                )
                yield boundary + headers + latest_frame + b"\r\n"
            await asyncio.sleep(0.066)
    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001)