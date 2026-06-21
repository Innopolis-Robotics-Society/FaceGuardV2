# ============================================================
# FaceGuard backend image.
# Multi-arch: builds for linux/arm64 (Raspberry Pi 4 / 5) and
# linux/amd64 (laptops). Uses Python 3.11 slim base.
# ============================================================

FROM python:3.11-slim AS base

# System deps for OpenCV-less build (we don't need cv2 in the backend;
# camera capture happens in the ML service). Pillow needs libjpeg.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libjpeg62-turbo \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (better layer caching).
COPY requirements.txt .
RUN pip install --default-timeout=300 --no-cache-dir -r requirements.txt

# Application code.
COPY app/ ./app/
COPY ml_stub/ ./ml_stub/

# Persistent data lives outside the container (mounted volume).
RUN mkdir -p /data

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DATABASE_PATH=/data/faces.db

EXPOSE 8000

# Default command. Override via docker-compose if needed.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
