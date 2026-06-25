"""Pytest configuration."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ["DATABASE_PATH"] = "/tmp/faceguard-test.db"
os.environ["SECRET_KEY"] = "test-secret-key-32-bytes-long!!"
os.environ["ADMIN_PASSWORD"] = "testpass"
os.environ["SERVO_MODE"] = "emulated"
os.environ["SERVO_PIN"] = "18"
os.environ["SERVO_OPEN_DURATION_SEC"] = "0.05"
os.environ["ML_SERVICE_URL"] = "http://localhost:8001"
os.environ["LOG_LEVEL"] = "DEBUG"

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    """FastAPI TestClient with mocked external services (no real ML/HTTP/GPIO)."""
    db_path = str(tmp_path / "test.db")
    monkeypatch.setenv("DATABASE_PATH", db_path)

    import app.ml_client

    async def fake_ml_start(self):
        self._client = None

    async def fake_ml_close(self):
        pass

    monkeypatch.setattr(app.ml_client.MLClient, "start", fake_ml_start)
    monkeypatch.setattr(app.ml_client.MLClient, "close", fake_ml_close)
    import app.recognition

    async def fake_loop_start(self):
        pass

    async def fake_loop_stop(self):
        pass

    monkeypatch.setattr(app.recognition.RecognitionLoop, "start", fake_loop_start)
    monkeypatch.setattr(app.recognition.RecognitionLoop, "stop", fake_loop_stop)

    from app.main import app

    with TestClient(app) as c:
        yield c
