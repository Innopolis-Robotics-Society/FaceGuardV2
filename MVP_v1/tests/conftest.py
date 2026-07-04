"""Pytest configuration."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient  # noqa: F401 (re-exported for tests)

ROOT = Path(__file__).parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("DATABASE_PATH", "/tmp/faceguard-test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-32-bytes-long!!")
os.environ.setdefault("ADMIN_PASSWORD", "testpass")
os.environ.setdefault("SERVO_MODE", "emulated")
os.environ.setdefault("SERVO_PIN", "18")
os.environ.setdefault("SERVO_OPEN_DURATION_SEC", "0.1")
os.environ.setdefault("ML_SERVICE_URL", "http://localhost:8001")
os.environ.setdefault("LOG_LEVEL", "DEBUG")


@pytest.fixture
def client(tmp_path, monkeypatch):
    """FastAPI TestClient with a fresh per-test DB."""
    db_path = str(tmp_path / "test.db")

    monkeypatch.setenv("DATABASE_PATH", db_path)

    from app.config import get_settings

    get_settings.cache_clear()

    import app.ml_client
    import app.recognition

    async def fake_ml_start(self):
        self._client = None

    async def fake_ml_close(self):
        pass

    async def fake_loop_start(self):
        pass

    async def fake_loop_stop(self):
        pass

    monkeypatch.setattr(app.ml_client.MLClient, "start", fake_ml_start)
    monkeypatch.setattr(app.ml_client.MLClient, "close", fake_ml_close)
    monkeypatch.setattr(app.recognition.RecognitionLoop, "start", fake_loop_start)
    monkeypatch.setattr(app.recognition.RecognitionLoop, "stop", fake_loop_stop)

    from app.main import app

    with TestClient(app) as c:
        yield c
    get_settings.cache_clear()
