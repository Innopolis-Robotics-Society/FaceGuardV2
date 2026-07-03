"""Integration tests for GET /api/logs (app/routes/logs.py).

Uses the shared `client` fixture from conftest.py which wires a
TestClient with an in-memory DB and mocked ML/servo.
"""

from __future__ import annotations

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _login(client) -> None:
    client.post("/login", data={"username": "admin", "password": "testpass"})


# ---------------------------------------------------------------------------
# Auth guard
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_logs_requires_auth(client):
    """Unauthenticated request must be rejected."""
    resp = client.get("/api/logs", follow_redirects=False)
    assert resp.status_code in (302, 307, 401, 403)


# ---------------------------------------------------------------------------
# Basic response shape
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_logs_returns_entries_list_when_empty(client):
    _login(client)
    resp = client.get("/api/logs")
    assert resp.status_code == 200
    data = resp.json()
    assert "entries" in data
    assert isinstance(data["entries"], list)


@pytest.mark.integration
def test_log_entry_schema(client):
    """Each log entry must have the documented fields."""
    import numpy as np

    from app.config import Settings
    from app.database import FaceDatabase

    _login(client)

    # Seed one log entry directly via DB
    settings = Settings(SERVO_OPEN_DURATION_SEC=0.1)
    import os

    db = FaceDatabase(db_path=os.environ["DATABASE_PATH"])
    db.add_log("Alice", 0.91, "user", True)
    db.close()

    resp = client.get("/api/logs")
    assert resp.status_code == 200
    entries = resp.json()["entries"]
    assert len(entries) >= 1

    entry = entries[0]
    for field in ("id", "name", "score", "access_type", "success", "timestamp"):
        assert field in entry, f"Missing field: {field}"


# ---------------------------------------------------------------------------
# Query parameters
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_logs_limit_parameter_respected(client):
    _login(client)

    import os

    from app.database import FaceDatabase

    db = FaceDatabase(db_path=os.environ["DATABASE_PATH"])
    for i in range(10):
        db.add_log(f"User{i}", 0.8, "user", True)
    db.close()

    resp = client.get("/api/logs?limit=3")
    assert resp.status_code == 200
    assert len(resp.json()["entries"]) <= 3


@pytest.mark.integration
def test_logs_filter_by_name(client):
    _login(client)

    import os

    from app.database import FaceDatabase

    db = FaceDatabase(db_path=os.environ["DATABASE_PATH"])
    db.add_log("Alice", 0.9, "user", True)
    db.add_log("Bob", 0.4, "unknown", False)
    db.close()

    resp = client.get("/api/logs?q=Alice")
    assert resp.status_code == 200
    entries = resp.json()["entries"]
    assert all(e["name"] == "Alice" for e in entries)


@pytest.mark.integration
def test_logs_invalid_limit_rejected(client):
    """limit=0 violates ge=1 — FastAPI should return 422."""
    _login(client)
    resp = client.get("/api/logs?limit=0")
    assert resp.status_code == 422


@pytest.mark.integration
def test_logs_limit_too_large_rejected(client):
    """limit=9999 violates le=1000."""
    _login(client)
    resp = client.get("/api/logs?limit=9999")
    assert resp.status_code == 422
