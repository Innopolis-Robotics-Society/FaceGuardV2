FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download InsightFace models at build time so the container
# doesn't need network access at runtime.
RUN python -c "import insightface; insightface.app.FaceAnalysis(name='buffalo_sc', root='./models').prepare(ctx_id=-1)"

COPY main.py .

# MediaPipe: disable GPU (we run CPU-only on the Pi) and silence verbose logs.
ENV MEDIAPIPE_DISABLE_GPU=1
ENV TF_CPP_MIN_LOG_LEVEL=3
ENV GLOG_minloglevel=2

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--log-level", "warning"]
