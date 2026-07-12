FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download InsightFace models at build time
RUN python -c "import insightface; insightface.app.FaceAnalysis(name='buffalo_sc', root='./models').prepare(ctx_id=-1)"

COPY main.py .

# Отключаем GPU для MediaPipe ДО старта процесса
ENV MEDIAPIPE_DISABLE_GPU=1
ENV TF_CPP_MIN_LOG_LEVEL=3
ENV GLOG_minloglevel=2

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--log-level", "warning"]