"""Pytest configuration."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path, monkeypatch):
    """FastAPI TestClient with test settings and mocked external services."""
    from app.config import Settings

    test_settings = Settings(
        DATABASE_PATH=str(tmp_path / "test.db"),
        SECRET_KEY="test-secret-key-32-bytes-long!!",
        ADMIN_PASSWORD="testpass",
        SERVO_MODE="emulated",
        SERVO_PIN=18,
        SERVO_OPEN_DURATION_SEC=0.05,
        ML_SERVICE_URL="http://localhost:8001",
        LOG_LEVEL="DEBUG",
    )

    import app.config

    monkeypatch.setattr(app.config, "get_settings", lambda: test_settings)

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
