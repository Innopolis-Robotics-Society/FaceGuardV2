FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 libgomp1 wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# InsightFace
RUN python -c "import insightface; insightface.app.FaceAnalysis(name='buffalo_sc', root='./models').prepare(ctx_id=-1)"

RUN mkdir -p models && wget -q -O models/pfld.onnx \
    "https://raw.githubusercontent.com/cunjian/pytorch_face_landmark/master/onnx/pfld.onnx" || \
    (echo "WARNING: download failed, place pfld.onnx manually" && exit 0)

COPY main.py .

ENV TF_CPP_MIN_LOG_LEVEL=3
ENV GLOG_minloglevel=2

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--log-level", "warning"]
