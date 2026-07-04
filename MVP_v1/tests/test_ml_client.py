"""Unit tests for MLClient (app/ml_client.py).

Covers: health check, get_latest parsing, malformed response handling.
All HTTP calls are intercepted with httpx transport mocks — no real
ML service is needed.
"""

from __future__ import annotations

import json

import httpx
import numpy as np
import pytest

from app.ml_client import DetectedFace, LatestFrame, MLClient

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_transport(status: int, body: str | dict | None = None) -> httpx.MockTransport:
    """Return an httpx MockTransport that always responds with the given status/body."""

    if isinstance(body, dict):
        content = json.dumps(body).encode()
        media_type = "application/json"
    elif isinstance(body, str):
        content = body.encode()
        media_type = "text/plain"
    else:
        content = b""
        media_type = "text/plain"

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, content=content, headers={"content-type": media_type})

    return httpx.MockTransport(handler)


async def _client_with(status: int, body=None) -> MLClient:
    """Return an MLClient wired to a mock transport."""
    c = MLClient(base_url="http://fake-ml", timeout=2.0)
    c._client = httpx.AsyncClient(
        base_url="http://fake-ml",
        transport=_make_transport(status, body),
    )
    return c


# ---------------------------------------------------------------------------
# health()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_health_returns_true_on_200():
    c = await _client_with(200, "ok")
    assert await c.health() is True


@pytest.mark.asyncio
async def test_health_returns_false_on_503():
    c = await _client_with(503)
    assert await c.health() is False


@pytest.mark.asyncio
async def test_health_returns_false_on_connection_error():
    """Network failure must not raise — must return False."""

    def failing_handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused")

    c = MLClient(base_url="http://fake-ml", timeout=2.0)
    c._client = httpx.AsyncClient(
        base_url="http://fake-ml",
        transport=httpx.MockTransport(failing_handler),
    )
    assert await c.health() is False


# ---------------------------------------------------------------------------
# get_latest()
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_latest_parses_valid_payload():
    payload = {
        "timestamp": "2026-01-01T12:00:00Z",
        "faces": [
            {
                "bbox": [10, 20, 110, 120],
                "embedding": [0.1] * 512,
                "confidence": 0.97,
            }
        ],
    }
    c = await _client_with(200, payload)
    frame = await c.get_latest()

    assert isinstance(frame, LatestFrame)
    assert frame.timestamp == "2026-01-01T12:00:00Z"
    assert len(frame.faces) == 1

    face = frame.faces[0]
    assert isinstance(face, DetectedFace)
    assert face.bbox == (10, 20, 110, 120)
    assert face.embedding.shape == (512,)
    assert face.embedding.dtype == np.float32
    assert abs(face.confidence - 0.97) < 1e-6


@pytest.mark.asyncio
async def test_get_latest_returns_empty_faces_list():
    payload = {"timestamp": "2026-01-01T12:00:00Z", "faces": []}
    c = await _client_with(200, payload)
    frame = await c.get_latest()

    assert frame is not None
    assert frame.faces == []


@pytest.mark.asyncio
async def test_get_latest_returns_none_on_404():
    c = await _client_with(404)
    assert await c.get_latest() is None


@pytest.mark.asyncio
async def test_get_latest_returns_none_on_non_json():
    c = await _client_with(200, "not-json-at-all")
    assert await c.get_latest() is None


@pytest.mark.asyncio
async def test_get_latest_skips_malformed_face_entry():
    """One bad face entry must not prevent the others from being parsed."""
    payload = {
        "timestamp": "2026-01-01T12:00:00Z",
        "faces": [
            {"bbox": [0, 0, 50, 50], "embedding": [0.5] * 512, "confidence": 0.9},
            {"bbox": "broken", "embedding": None},  # malformed — skip
        ],
    }
    c = await _client_with(200, payload)
    frame = await c.get_latest()

    assert frame is not None
    assert len(frame.faces) == 1


@pytest.mark.asyncio
async def test_get_latest_returns_none_on_network_error():
    def failing(request):
        raise httpx.ConnectError("refused")

    c = MLClient(base_url="http://fake-ml")
    c._client = httpx.AsyncClient(
        base_url="http://fake-ml",
        transport=httpx.MockTransport(failing),
    )
    assert await c.get_latest() is None


# ---------------------------------------------------------------------------
# Lifecycle
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_client_start_creates_httpx_client():
    c = MLClient(base_url="http://fake-ml")
    assert c._client is None
    await c.start()
    assert c._client is not None
    await c.close()


@pytest.mark.asyncio
async def test_client_close_sets_none():
    c = MLClient(base_url="http://fake-ml")
    await c.start()
    await c.close()
    assert c._client is None


@pytest.mark.asyncio
async def test_client_context_manager():
    async with MLClient(base_url="http://fake-ml") as c:
        assert c._client is not None
    assert c._client is None
